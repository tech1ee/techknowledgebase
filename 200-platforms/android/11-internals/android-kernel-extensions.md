---
title: "Linux Kernel: что Android добавил к ядру"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/kernel
  - topic/internals
  - type/deep-dive
  - level/expert
related:
  - "[[android-binder-ipc]]"
  - "[[android-boot-process]]"
  - "[[android-process-memory]]"
  - "[[android-system-services]]"
  - "[[android-architecture]]"
  - "[[os-processes-threads]]"
  - "[[os-memory-management]]"
cs-foundations: [kernel-modules, device-drivers, memory-management, process-management, security-model, ipc-mechanisms]
prerequisites:
  - "[[os-processes-threads]]"
  - "[[os-memory-management]]"
  - "[[android-architecture]]"
reading_time: 85
difficulty: 9
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Linux Kernel: что Android добавил к ядру

> Android-ядро — это **НЕ** «просто Linux». Google добавил 200+ патчей к ванильному ядру, многие из которых upstream-сообщество отвергало годами. В 2010 году Greg Kroah-Hartman даже удалил Android-драйверы из staging tree. Только к 2019–2020 большинство патчей были приняты в mainline. Сегодня GKI (Generic Kernel Image) стандартизирует ядро на всех устройствах, а Android — крупнейший потребитель Linux-ядра в мире: 3+ миллиарда устройств.

> **Prerequisites:**
> - [[os-processes-threads]] — процессы, потоки, планирование в ОС
> - [[os-memory-management]] — виртуальная память, страницы, mmap
> - [[android-architecture]] — общая архитектура Android (слои)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **GKI** | Generic Kernel Image — единый образ ядра от Google для всех устройств |
| **KMI** | Kernel Module Interface — стабильный ABI между GKI и вендорными модулями |
| **Binder** | Механизм IPC в ядре Android: /dev/binder |
| **ashmem** | Anonymous Shared Memory — разделяемая память с kernel-рекламацией |
| **memfd** | memfd_create — upstream-замена ashmem |
| **ION** | Аллокатор специализированной памяти (deprecated в Android 12) |
| **DMA-BUF heaps** | Upstream-замена ION для аллокации буферов GPU/камеры |
| **lmkd** | Low Memory Killer Daemon — убийца процессов при нехватке памяти |
| **PSI** | Pressure Stall Information — метрики давления на ресурсы |
| **wakeup_sources** | Upstream-механизм предотвращения засыпания устройства |
| **SELinux** | Security-Enhanced Linux — мандатный контроль доступа |
| **seccomp-BPF** | Фильтрация системных вызовов через BPF-программы |
| **FUSE** | Filesystem in Userspace — файловая система в userspace |
| **dm-verity** | Device-mapper target для проверки целостности разделов |
| **AVB** | Android Verified Boot — цепочка доверия при загрузке |
| **cgroups** | Control Groups — группировка процессов для управления ресурсами |
| **EAS** | Energy-Aware Scheduling — энерго-эффективное планирование |
| **Treble** | Архитектурное разделение framework/vendor (Android 8+) |
| **HIDL/AIDL** | HAL Interface Definition Languages для Treble |
| **oom_score_adj** | Приоритет процесса для OOM killer (-1000..1000) |

---

## Зачем это нужно

| Проблема | Без знания ядра | С пониманием ядра |
|----------|-----------------|-------------------|
| Приложение убивается в фоне | «Система глючит» | Понимаете lmkd, adj scores, PSI-триггеры |
| Camera/GPU буфер corrupted | «Баг драйвера» | Знаете ION/DMA-BUF, физически непрерывную память |
| Binder transaction failed | «Binder — магия» | Понимаете kernel driver, mmap, 1 МБ лимит буфера |
| Battery drain в фоне | «Нужен task killer» | Знаете wakeup_sources, suspend blockers |
| SELinux denial в logcat | «Отключить SELinux» | Понимаете TE-политики, домены, типы |
| Файлы недоступны на /sdcard | «Scoped Storage — зло» | Знаете FUSE mediation, MediaStore |
| OOM на устройстве с 2 ГБ RAM | «Мало памяти» | Понимаете ashmem pin/unpin, zRAM, lmkd стратегии |
| Процессор греется | «Нужна оптимизация» | Знаете cgroups, EAS, cpuset для big.LITTLE |

---

## Историческая шкала

```
2003        2005        2008     2010      2012       2014
──┬───────────┬───────────┬────────┬─────────┬──────────┬──────
  │           │           │        │         │          │
  │      Покупка     Android   GKH       Linux      Binder
  │      Android     1.0 на   удаляет   Plumbers:  в staging
  │      Inc.       Linux    Android   «Android    tree
  │                 2.6.25   из        и Linux     ядра 3.19
  │                          staging   community»
  │
  │
2015        2017        2019     2020      2021       2024
──┬───────────┬───────────┬────────┬─────────┬──────────┬──────
  │           │           │        │         │          │
  │        Project     Binder  ashmem    GKI 2.0    GKI на
  │        Treble:     принят  удалён    (Android   всех
  │        разделение  в       из        12):       форм-
  │        vendor/     mainline staging;  единое    факторах;
  │        framework   5.0     ION→      ядро      RISC-V
  │        (A8)                DMA-BUF            убран
```

### Ключевые даты подробно

**2005 — покупка Android Inc.**
Google приобретает стартап Andy Rubin и начинает строить мобильную ОС на базе Linux 2.6. Решение использовать Linux вместо собственного ядра — стратегическое: готовая поддержка оборудования, сетевой стек, файловые системы.

**2008 — Android 1.0 (Linux 2.6.25)**
Первый релиз содержит десятки патчей к ядру:
- Binder driver (из OpenBinder проекта Palm/Be)
- ashmem (анонимная разделяемая память)
- pmem (физическая память для мультимедиа)
- wakelocks (управление засыпанием)
- Low Memory Killer driver
- RAM console / persistent RAM для crash-логов
- logger (собственная система логирования)

**2010 — Greg Kroah-Hartman удаляет Android из staging**
Maintainer staging tree Linux удаляет все Android-драйверы из ядра. Причина: код находился в staging больше года без активной работы по его улучшению. Это не означало враждебность — скорее фиксацию факта, что Google не участвовал в upstream-процессе.

> «The Android kernel code is a mess. [...] But to be fair, everyone's kernel code in the staging tree is a mess, that's why it's in the staging tree.»
> — Greg Kroah-Hartman, 2010

**2012 — «Android and the Linux Kernel Community»**
Историческая презентация на Linux Plumbers Conference. Tim Bird (Sony) и другие обсуждают пути интеграции Android-патчей в mainline. Начинается систематическая работа по upstreaming.

**2017 — Project Treble (Android 8.0)**
Архитектурное разделение framework и vendor code. Появляются три домена Binder: binder (framework), hwbinder (HAL), vndbinder (vendor). Это ядерное изменение — три отдельных /dev/ устройства.

**2019 — Binder в mainline (ядро 5.0)**
После 10+ лет Binder принят в mainline Linux kernel. Это означает, что любой Linux-дистрибутив может использовать Binder IPC.

**2020 — ashmem удалён из staging**
ashmem начинает миграцию на memfd_create. Одновременно ION начинает замену на DMA-BUF heaps.

**2021 — GKI 2.0 (Android 12)**
Google требует использование единого ядра (GKI) для всех устройств с ядром 5.10+. Вендорный код вынесен в загружаемые модули. KMI стабилизирует интерфейс.

**2024 — GKI обязателен на всех форм-факторах**
GKI распространён на часы, автомобили, ТВ — все AArch64-устройства. Поддержка RISC-V убрана из GKI.

---

## GKI: единое ядро для всех

### Проблема до GKI

До GKI каждое Android-устройство имело собственную сборку ядра:

```
                      БЕЗ GKI (до Android 12)
┌─────────────────────────────────────────────────────┐
│                    AOSP Common Kernel                │
│               (android-mainline ветка)              │
└───────────────┬─────────────────────┬───────────────┘
                │                     │
        ┌───────▼───────┐     ┌───────▼───────┐
        │  SoC Vendor   │     │  SoC Vendor   │
        │  Kernel       │     │  Kernel       │
        │  (Qualcomm)   │     │  (MediaTek)   │
        └───────┬───────┘     └───────┬───────┘
                │                     │
        ┌───────▼───────┐     ┌───────▼───────┐
        │  OEM Device   │     │  OEM Device   │
        │  Kernel       │     │  Kernel       │
        │  (Samsung)    │     │  (Xiaomi)     │
        └───────────────┘     └───────────────┘

  Результат: каждое устройство = уникальное ядро
  Обновления безопасности: месяцы задержки
  Фрагментация: тысячи вариантов ядра
```

### Архитектура GKI

```
                      С GKI (Android 12+)
┌─────────────────────────────────────────────────────┐
│              GKI Kernel (от Google)                  │
│         Единый бинарник для архитектуры              │
│    ┌────────────────────────────────────────┐        │
│    │  Стабильный KMI (Kernel Module Interface)│      │
│    └────────────────────┬───────────────────┘        │
└─────────────────────────┼───────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
   │  Qualcomm   │ │  MediaTek   │ │  Tensor     │
   │  Vendor     │ │  Vendor     │ │  Vendor     │
   │  Modules    │ │  Modules    │ │  Modules    │
   │  (.ko)      │ │  (.ko)      │ │  (.ko)      │
   └─────────────┘ └─────────────┘ └─────────────┘

  Результат: одно ядро + загружаемые модули
  Обновления безопасности: недели, не месяцы
  Google контролирует ядро напрямую
```

### KMI — Kernel Module Interface

KMI — это список экспортируемых символов (функций и переменных), которые GKI гарантирует вендорным модулям. После «KMI freeze» Google не меняет эти символы до следующей версии ядра.

```c
// Пример: вендорный модуль камеры использует KMI-символы
#include <linux/dma-buf.h>
#include <linux/dma-heap.h>

// Эти функции — часть KMI, их сигнатуры стабильны
struct dma_buf *dma_buf_get(int fd);           // KMI-символ
void dma_buf_put(struct dma_buf *dmabuf);      // KMI-символ
int dma_buf_fd(struct dma_buf *dmabuf, int flags); // KMI-символ

// Вендорный модуль загружается динамически
static int __init camera_vendor_init(void)
{
    // Используем стабильные KMI-символы
    struct dma_buf *buf = dma_buf_get(shared_fd);
    if (IS_ERR(buf))
        return PTR_ERR(buf);

    // Работаем с буфером камеры...
    dma_buf_put(buf);
    return 0;
}
module_init(camera_vendor_init);
```

### Структура GKI на устройстве

```
boot.img
├── kernel (GKI — от Google)
└── ramdisk
    └── lib/modules/
        ├── google_modules/    ← GKI-модули (Wi-Fi, Bluetooth и др.)
        └── vendor_modules/    ← Вендорные модули (камера, GPU и др.)

vendor_boot.img
├── vendor ramdisk
│   └── lib/modules/
│       └── *.ko              ← Дополнительные вендорные модули
└── vendor dtb               ← Device Tree Blob
```

---

## Binder Driver

> Подробный разбор Binder: [[android-binder-ipc]]
> Здесь — только ядерная часть (kernel driver).

### Зачем Binder в ядре

Binder мог бы быть userspace-библиотекой (как D-Bus). Почему он — kernel driver?

1. **Безопасность**: ядро знает UID/PID вызывающего процесса. Подделать невозможно. D-Bus передаёт credentials через SO_PEERCRED — менее надёжно.
2. **Производительность**: данные копируются один раз (отправитель → ядро через copy_from_user), а получатель читает их через mmap. Итого: **одна копия** вместо двух.
3. **Reference counting**: ядро отслеживает жизненный цикл Binder-объектов. Если процесс умирает, ядро уведомляет всех держателей ссылок (death notification).
4. **Безопасность потоков**: ядро управляет пулом потоков Binder.

### Три домена Binder (с Android 8.0 Treble)

```
┌──────────────────────────────────────────────────────────┐
│                    USERSPACE                              │
│                                                          │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│  │  Apps &   │     │  HAL     │     │  Vendor  │         │
│  │  System   │     │  Processes│    │  Processes│         │
│  │  Services │     │  (audio, │     │  (sensor,│         │
│  │           │     │  camera) │     │  modem)  │         │
│  └─────┬─────┘     └────┬─────┘     └────┬─────┘         │
│        │                │                │               │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐        │
│  │libbinder  │    │libhidl-   │    │libvndk    │        │
│  │           │    │transport  │    │binder     │        │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘        │
│========│================│================│===============│
│        │     KERNEL      │                │               │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐        │
│  │/dev/binder│    │/dev/      │    │/dev/      │        │
│  │           │    │hwbinder   │    │vndbinder  │        │
│  │ Framework │    │ Hardware  │    │ Vendor-to-│        │
│  │ IPC       │    │ HAL IPC   │    │ vendor IPC│        │
│  └───────────┘    └───────────┘    └───────────┘        │
│                                                          │
│           Binder driver (drivers/android/binder.c)       │
└──────────────────────────────────────────────────────────┘
```

### Ключевые структуры в ядре

```c
// Упрощённые структуры из drivers/android/binder.c

// Транзакция Binder — основная единица обмена данными
struct binder_transaction {
    struct binder_work work;          // Элемент рабочей очереди
    struct binder_thread *from;       // Отправитель
    pid_t from_pid;                   // PID отправителя (ядро заполняет!)
    uid_t from_uid;                   // UID отправителя (ядро заполняет!)
    struct binder_proc *to_proc;      // Процесс-получатель
    struct binder_thread *to_thread;  // Поток-получатель
    struct binder_buffer *buffer;     // Буфер данных (mmap)
    unsigned int code;                // Код операции
    unsigned int flags;               // Флаги (ONE_WAY и др.)
};

// Процесс, зарегистрированный в Binder
struct binder_proc {
    struct hlist_node proc_node;      // Узел в глобальном списке
    struct rb_root threads;           // Красно-чёрное дерево потоков
    struct rb_root nodes;             // Binder-ноды этого процесса
    struct rb_root refs_by_desc;      // Ссылки по дескриптору
    struct rb_root refs_by_node;      // Ссылки по ноде
    struct list_head todo;            // Очередь задач
    struct binder_alloc alloc;        // Аллокатор mmap-буфера
    pid_t pid;                        // PID процесса
    // ...
};

// Буфер Binder — аллоцируется в mmap-области получателя
struct binder_buffer {
    struct list_head entry;           // Список буферов
    struct rb_node rb_node;           // Узел в дереве свободных
    unsigned free:1;                  // Свободен ли
    unsigned clear_on_free:1;         // Очистить при освобождении
    unsigned allow_user_free:1;       // Пользователь может освободить
    size_t data_size;                 // Размер данных
    size_t offsets_size;              // Размер таблицы смещений
    struct binder_transaction *transaction; // Связанная транзакция
};
```

### Механизм «одной копии»

```
┌──────────────────┐                    ┌──────────────────┐
│  Процесс A       │                    │  Процесс B       │
│  (отправитель)    │                    │  (получатель)     │
│                   │                    │                   │
│  user buffer ─────┼───copy_from_user──▶│                   │
│                   │        │           │                   │
│                   │   ┌────▼────┐      │  mmap region ◄───┤
│                   │   │ Kernel  │      │  (виртуальная    │
│                   │   │ buffer  │──────│   память, та же  │
│                   │   │(physical│      │   физ. страница) │
│                   │   │ page)   │      │                   │
│                   │   └─────────┘      │                   │
└──────────────────┘                    └──────────────────┘

   Итого: 1 копия (copy_from_user)
   Получатель читает данные через mmap — ноль копий на его стороне

   Сравнение: pipe/socket = copy_from_user + copy_to_user = 2 копии
```

---

## ashmem (Anonymous Shared Memory)

### Назначение

ashmem — механизм разделяемой памяти между процессами Android. Ключевое отличие от POSIX shared memory (`shm_open`):

**Ядро может забрать UNPINNED-страницы ashmem под давлением памяти.**

Это критично для мобильных устройств, где памяти мало, и система должна уметь адаптивно освобождать ресурсы.

### API ashmem

```c
// Создание региона ashmem
// Возвращает file descriptor
int fd = ashmem_create_region("my_shared_data", SIZE);

// Установка маски защиты (до первого mmap!)
// Ограничивает права маппинга
ioctl(fd, ASHMEM_SET_PROT_MASK, PROT_READ | PROT_WRITE);

// Маппинг в адресное пространство процесса
void *addr = mmap(NULL, SIZE, PROT_READ | PROT_WRITE,
                  MAP_SHARED, fd, 0);

// Передача fd другому процессу (через Binder или Unix socket)
// Другой процесс может сделать свой mmap на тот же fd

// Pin/Unpin — управление рекламацией
struct ashmem_pin pin = { .offset = 0, .len = SIZE };

// Unpin: разрешаем ядру забрать эти страницы
ioctl(fd, ASHMEM_UNPIN, &pin);

// Pin: страницы нужны, не забирай
int ret = ioctl(fd, ASHMEM_PIN, &pin);
// ret == ASHMEM_NOT_PURGED — данные целы
// ret == ASHMEM_WAS_PURGED — данные были очищены ядром!
```

### Жизненный цикл ashmem

```
┌──────────────────────────────────────────────────────────┐
│                  ЖИЗНЕННЫЙ ЦИКЛ ashmem                   │
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   CREATE     │───▶│    MMAP      │───▶│   PINNED     │  │
│  │  ashmem_     │    │  Маппинг    │    │  Данные     │  │
│  │  create_     │    │  в адресное │    │  защищены   │  │
│  │  region()    │    │  пространство│   │  от очистки │  │
│  └─────────────┘    └─────────────┘    └──────┬──────┘  │
│                                               │          │
│                                         UNPIN │          │
│                                               ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌──────┴──────┐  │
│  │   PURGED     │◀───│  RECLAIM    │◀───│  UNPINNED   │  │
│  │  Данные      │    │  Ядро       │    │  Ядро может │  │
│  │  потеряны!   │    │  забирает   │    │  забрать    │  │
│  │  PIN вернёт  │    │  страницы   │    │  страницы   │  │
│  │  WAS_PURGED  │    │  при давлении│   │  при нехватке│ │
│  └─────────────┘    └─────────────┘    └──────┬──────┘  │
│                                               │          │
│                                          PIN  │          │
│                                               ▼          │
│                                        ┌──────┴──────┐  │
│                                        │  RE-PINNED  │  │
│                                        │  Если данные │  │
│                                        │  NOT_PURGED: │  │
│                                        │  можно       │  │
│                                        │  использовать│  │
│                                        └─────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Применения ashmem в Android

| Компонент | Использование |
|-----------|--------------|
| **SharedMemory API** | Java-обёртка для ashmem (android.os.SharedMemory) |
| **Bitmap sharing** | Передача больших Bitmap между процессами |
| **SurfaceFlinger** | Буферы отрисовки (через GraphicBuffer/Gralloc) |
| **CursorWindow** | Данные ContentProvider (каждый Cursor = ashmem) |
| **MemoryFile** | Устаревший Java API для ashmem |
| **Parcel large data** | Когда данные не помещаются в Binder-буфер (1 МБ) |

### Миграция на memfd_create

Начиная с ядра 5.18, ashmem удалён из upstream Linux. Android мигрирует на `memfd_create`:

```c
// Старый путь: ashmem
int fd = ashmem_create_region("buffer", 4096);

// Новый путь: memfd_create (ядро 3.17+)
int fd = memfd_create("buffer", MFD_ALLOW_SEALING);

// memfd использует файловые «печати» (seals) вместо pin/unpin
fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW);

// F_SEAL_FUTURE_WRITE — аналог ASHMEM_SET_PROT_MASK
// Добавлен специально для Android-миграции
fcntl(fd, F_ADD_SEALS, F_SEAL_FUTURE_WRITE);
```

**Ключевая проблема миграции**: ashmem поддерживает `ASHMEM_SET_PROT_MASK` для ограничения маппинга (нельзя сделать mmap с PROT_EXEC). В memfd такого не было — для решения добавили `F_SEAL_FUTURE_EXEC` в ядро. На Linux Plumbers Conference 2025 обсуждалась финальная стратегия миграции.

### Сравнение ashmem vs POSIX shm vs memfd

| Характеристика | ashmem | POSIX shm | memfd |
|---------------|--------|-----------|-------|
| Kernel reclaim | Да (pin/unpin) | Нет | Нет (через seals) |
| Именованный | Нет (анонимный) | Да (через /dev/shm) | Нет (анонимный) |
| FD-passing | Да | Нет (имя) | Да |
| Upstream Linux | Нет (удалён 5.18) | Да | Да (3.17+) |
| Android API | SharedMemory | Нет в Android | SharedMemory (10+) |
| Exec protection | SET_PROT_MASK | Нет | F_SEAL_FUTURE_EXEC |

---

## ION Memory Allocator / DMA-BUF Heaps

### Зачем нужна специализированная память

Стандартный `malloc()` / `kmalloc()` возвращает **виртуально непрерывную** память. Но аппаратные компоненты требуют специфических свойств:

| Устройство | Требование к памяти |
|-----------|---------------------|
| **GPU** | Физически непрерывная, доступная по DMA |
| **Камера** | Непрерывная, в определённой области DRAM |
| **Video decoder** | Непрерывная, с выравниванием по строке |
| **Display** | Непрерывная, доступная контроллеру дисплея |
| **ISP** | Из CMA-зоны, с определённым выравниванием |

`malloc()` не может гарантировать ни одно из этих свойств. Вот зачем нужен ION/DMA-BUF.

### ION (до Android 12)

```
┌──────────────────────────────────────────────────────────┐
│                    USERSPACE                              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Camera  │  │  GPU     │  │  Video   │               │
│  │  HAL     │  │  Driver  │  │  Codec   │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                     │
│       └──────────────┼──────────────┘                     │
│                      │                                    │
│                ┌─────▼─────┐                              │
│                │  libion   │  ← Userspace библиотека      │
│                └─────┬─────┘                              │
│══════════════════════│════════════════════════════════════│
│                KERNEL│                                    │
│                ┌─────▼─────┐                              │
│                │ /dev/ion  │  ← Единый character device   │
│                └─────┬─────┘                              │
│                      │                                    │
│       ┌──────────────┼──────────────┐                     │
│       │              │              │                     │
│  ┌────▼────┐   ┌─────▼────┐   ┌────▼─────┐              │
│  │ System  │   │  CMA     │   │ Carveout │              │
│  │ Heap    │   │  Heap    │   │ Heap     │              │
│  │(vmalloc)│   │(физ.     │   │(зарезер- │              │
│  │         │   │ непрер.) │   │ вированная│             │
│  └─────────┘   └──────────┘   └──────────┘              │
│                                                          │
│  + Vendor-специфичные heaps (Qualcomm, Samsung и др.)    │
└──────────────────────────────────────────────────────────┘
```

### Проблемы ION

1. **Единый /dev/ion** — один character device для всех типов памяти. Невозможно настроить SELinux-политики отдельно для каждого типа.
2. **Нестандартные ioctl** — ION использовал собственные ioctl, не совместимые с upstream DMA-BUF.
3. **Vendor-зависимость** — каждый SoC-вендор добавлял собственные heaps, что увеличивало фрагментацию.
4. **Отвергнут upstream** — ION находился в staging и не был принят в mainline из-за архитектурных проблем.

### DMA-BUF Heaps (Android 12+)

```
┌──────────────────────────────────────────────────────────┐
│                    USERSPACE                              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Camera  │  │  GPU     │  │  Video   │               │
│  │  HAL     │  │  Driver  │  │  Codec   │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                     │
│       └──────────────┼──────────────┘                     │
│                      │                                    │
│             ┌────────▼────────┐                           │
│             │ libdmabufheap   │  ← Совместимость ION→    │
│             │                 │    DMA-BUF                │
│             └────────┬────────┘                           │
│══════════════════════│════════════════════════════════════│
│                KERNEL│                                    │
│                      │                                    │
│       ┌──────────────┼──────────────┐                     │
│       │              │              │                     │
│  ┌────▼──────┐  ┌────▼──────┐  ┌────▼──────┐            │
│  │/dev/dma_  │  │/dev/dma_  │  │/dev/dma_  │            │
│  │heap/      │  │heap/      │  │heap/      │            │
│  │system     │  │cma        │  │vendor_    │            │
│  │           │  │           │  │carveout   │            │
│  └───────────┘  └───────────┘  └───────────┘            │
│                                                          │
│  Каждый heap = отдельный character device                │
│  → Отдельные SELinux-политики для каждого типа!         │
│  → Принят в mainline Linux 5.6                          │
└──────────────────────────────────────────────────────────┘
```

### Пример использования DMA-BUF heaps

```c
#include <linux/dma-heap.h>
#include <linux/dma-buf.h>

// Открытие heap (userspace)
int heap_fd = open("/dev/dma_heap/system", O_RDONLY);

// Аллокация буфера
struct dma_heap_allocation_data alloc = {
    .len = 4096 * 256,          // 1 МБ
    .fd_flags = O_RDWR | O_CLOEXEC,
    .heap_flags = 0,
};
ioctl(heap_fd, DMA_HEAP_IOCTL_ALLOC, &alloc);
int buf_fd = alloc.fd;          // DMA-BUF file descriptor

// buf_fd можно:
// 1. Передать другому процессу через Binder
// 2. mmap в userspace для CPU-доступа
// 3. Передать GPU/камере для DMA-доступа

void *ptr = mmap(NULL, alloc.len, PROT_READ | PROT_WRITE,
                 MAP_SHARED, buf_fd, 0);

// Синхронизация CPU/device доступа
struct dma_buf_sync sync = {
    .flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_RW,
};
ioctl(buf_fd, DMA_BUF_IOCTL_SYNC, &sync);

// ... работа с буфером ...

sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_RW;
ioctl(buf_fd, DMA_BUF_IOCTL_SYNC, &sync);
```

### Сравнение ION vs DMA-BUF Heaps

| Характеристика | ION | DMA-BUF Heaps |
|---------------|-----|---------------|
| Character devices | Один (/dev/ion) | По одному на heap |
| SELinux гранулярность | Грубая | Тонкая (per-heap) |
| Upstream Linux | staging (удалён 5.11) | mainline (5.6+) |
| Совместимость | Собственные ioctl | Стандартный DMA-BUF |
| Vendor heaps | В коде ION | Отдельные модули |
| Миграция | N/A | libdmabufheap |

---

## lmkd (Low Memory Killer Daemon)

### Эволюция убийцы процессов

```
┌───────────────────────────────────────────────────────────────┐
│                 ЭВОЛЮЦИЯ LOW MEMORY KILLER                    │
│                                                               │
│  Android 1.0–8.0              Android 9.0+                   │
│  ┌───────────────────┐        ┌───────────────────┐          │
│  │ KERNEL SPACE       │        │ USERSPACE          │          │
│  │                    │        │                    │          │
│  │ lowmemorykiller.c  │        │ lmkd (daemon)      │          │
│  │ - Ядерный драйвер │   ──▶  │ - Userspace процесс│          │
│  │ - /proc мониторинг │        │ - PSI мониторинг   │          │
│  │ - minfree уровни   │        │ - Тонкая настройка │          │
│  │ - Нет обновлений   │        │ - Mainline-модуль  │          │
│  │   без OTA          │        │ - OTA не нужен     │          │
│  └───────────────────┘        └───────────────────┘          │
│                                                               │
│  Удалён из upstream 4.12      Текущее решение                │
└───────────────────────────────────────────────────────────────┘
```

### Почему убрали из ядра

1. **Обновления**: драйвер в ядре обновляется только через OTA. lmkd в userspace можно обновить через Google Play (Mainline модуль).
2. **Гибкость**: в userspace проще реализовать сложные стратегии убийства.
3. **PSI**: Pressure Stall Information появилась в ядре 4.20 и даёт точные метрики давления. Старый драйвер использовал грубые пороги свободной памяти.
4. **Upstream**: ядерный LMK был Android-специфичным хаком. Linux имеет собственный OOM killer, но он слишком агрессивен для мобильных устройств.

### PSI (Pressure Stall Information)

PSI — механизм ядра (Linux 4.20+), который измеряет, сколько времени процессы проводят в ожидании ресурсов:

```
/proc/pressure/memory:
some avg10=0.00 avg60=0.00 avg300=0.00 total=0
full avg10=0.00 avg60=0.00 avg300=0.00 total=0

some = хотя бы один процесс ждёт память
full = ВСЕ процессы ждут память

avg10  = среднее за последние 10 секунд (%)
avg60  = среднее за последние 60 секунд (%)
avg300 = среднее за последние 300 секунд (%)
```

lmkd использует PSI-мониторы — ядро уведомляет lmkd, когда давление превышает пороги:

```c
// lmkd настраивает PSI-мониторы (упрощённо)

// Частичный stall: хотя бы один процесс ждёт
// Порог: 70мс stall за 1 секунду → LOW memory pressure
struct psi_trigger low_trigger = {
    .state = PSI_SOME,          // some — частичное давление
    .threshold_us = 70000,       // 70 мс
    .window_us = 1000000,        // за окно 1 секунда
};

// Полный stall: все процессы ждут
// Порог: 700мс stall за 1 секунду → CRITICAL memory pressure
struct psi_trigger critical_trigger = {
    .state = PSI_FULL,          // full — полное давление
    .threshold_us = 700000,      // 700 мс
    .window_us = 1000000,        // за окно 1 секунда
};
```

### Как lmkd принимает решение об убийстве

```
┌──────────────────────────────────────────────────────────────┐
│               АЛГОРИТМ РЕШЕНИЯ lmkd                          │
│                                                              │
│  ┌────────────────┐                                          │
│  │  PSI Monitor   │─── Срабатывание ───▶ Какой уровень?     │
│  │  (ядро)        │                      │                   │
│  └────────────────┘                      │                   │
│                                          ▼                   │
│                              ┌───────────────────────┐       │
│                              │  LOW (some > 70ms/1s) │       │
│                              │  MEDIUM               │       │
│                              │  CRITICAL (full>700ms)│       │
│                              └───────────┬───────────┘       │
│                                          │                   │
│                                          ▼                   │
│  ┌────────────────┐    ┌─────────────────────────────┐       │
│  │ ActivityManager│───▶│  oom_score_adj для каждого   │       │
│  │ Server (AMS)   │    │  процесса:                   │       │
│  │                │    │                               │       │
│  │ Назначает adj  │    │  -1000 = native (не убивать) │       │
│  │ каждому        │    │   -900 = system_server        │       │
│  │ процессу       │    │   -800 = persistent           │       │
│  └────────────────┘    │      0 = foreground            │       │
│                        │    100 = visible               │       │
│                        │    200 = perceptible           │       │
│                        │    300 = heavy_weight          │       │
│                        │    400 = home (launcher)       │       │
│                        │    500 = previous              │       │
│                        │    700 = cached (A)            │       │
│                        │    900 = cached (B)            │       │
│                        │    999 = cached (empty)        │       │
│                        └───────────────┬─────────────┘       │
│                                        │                     │
│                                        ▼                     │
│                           ┌────────────────────────┐         │
│                           │  Выбираем жертву:       │         │
│                           │  1. Фильтр по min_adj  │         │
│                           │     (зависит от уровня │         │
│                           │      давления)         │         │
│                           │  2. Наибольший RSS      │         │
│                           │     среди кандидатов    │         │
│                           │  3. kill(pid, SIGKILL)  │         │
│                           └────────────────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

### Стратегии убийства

**Legacy (minfree):**
```
# /sys/module/lowmemorykiller/parameters/minfree
# Пороги свободной памяти в страницах (4 КБ)
# Когда свободная память падает ниже порога,
# убиваем процессы с adj >= соответствующего уровня

minfree: 18432, 23040, 27648, 32256, 55296, 80640
adj:         0,   100,   200,   300,   900,   906

# Пример: если свободно < 80640 страниц (315 МБ),
# убиваем процессы с adj >= 906 (cached empty)
```

**Modern (PSI-based, Android 10+):**
```
# Свойства lmkd
ro.lmk.use_psi=true                    # Использовать PSI
ro.lmk.psi_partial_stall_ms=70        # Порог partial stall
ro.lmk.psi_complete_stall_ms=700      # Порог complete stall
ro.lmk.thrashing_limit=30             # Порог thrashing (%)
ro.lmk.swap_free_low_percentage=10    # Порог swap
ro.lmk.kill_timeout_ms=100            # Таймаут между убийствами
```

### lmkd vs стандартный Linux OOM Killer

| Аспект | Linux OOM Killer | Android lmkd |
|--------|-----------------|--------------|
| Где работает | Ядро | Userspace |
| Когда убивает | При OOM (критическая нехватка) | Превентивно (до OOM) |
| Что учитывает | oom_score (RSS + поправки) | adj от AMS + PSI + swap |
| Гранулярность | Грубая | Тонкая (знает foreground/background) |
| Пользовательский опыт | Может убить видимое приложение | Сначала убивает cached/empty |
| Настройка | /proc/pid/oom_score_adj | Множество системных свойств |
| Обновление | Только с ядром | Через Mainline (Google Play) |

> Подробнее о памяти процессов: [[android-process-memory]]

---

## Wakelocks / wakeup_sources

### Проблема: мобильное устройство должно спать

На десктопе Linux не нужно агрессивно засыпать — питание от сети. На мобильном устройстве каждая секунда бодрствования стоит батарею. Но:

- Приложение скачивает файл → нельзя засыпать
- Приходит push-уведомление → нужно проснуться, обработать, заснуть
- Воспроизводится музыка → экран можно выключить, но CPU работает

Linux не имел механизма «не засыпай, пока я не закончу». Процесс не мог сказать ядру: «подожди с suspend».

### История upstream-отвержения

**2008**: Google добавляет wakelocks в Android-ядро. Механизм: процесс берёт «wakelock» (блокировку пробуждения), ядро не засыпает, пока есть активные wakelocks.

**2009–2011**: Upstream-разработчики отвергают wakelocks. Претензии:
- Неидиоматичный API для Linux
- Проблема: userspace может забыть отпустить wakelock → батарея сядет
- Wakelock — «костыль», нужна архитектурная переработка

**2011–2012**: Rafael Wysocki разрабатывает `wakeup_sources` — upstream-совместимый механизм. Принят в ядро 3.5.

### Стек wakelocks в Android

```
┌──────────────────────────────────────────────────────────────┐
│                        JAVA API                              │
│                                                              │
│  PowerManager pm = getSystemService(POWER_SERVICE);          │
│  PowerManager.WakeLock wl = pm.newWakeLock(                  │
│      PowerManager.PARTIAL_WAKE_LOCK, "MyApp:download");      │
│  wl.acquire(10 * 60 * 1000);  // 10 минут максимум          │
│  // ... скачиваем файл ...                                   │
│  wl.release();                                               │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                   PowerManagerService                         │
│                                                              │
│  - Отслеживает все wakelocks всех приложений                │
│  - Применяет политики (Doze, App Standby)                   │
│  - Пишет в /sys/power/wake_lock                             │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                     KERNEL                                    │
│                                                              │
│  /sys/power/wake_lock      ← Запись имени = acquire         │
│  /sys/power/wake_unlock    ← Запись имени = release         │
│  /sys/kernel/debug/wakeup_sources  ← Статистика             │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              wakeup_source framework              │       │
│  │                                                    │       │
│  │  - Каждый wakeup_source = struct wakeup_source    │       │
│  │  - Ведёт счётчик активных sources                 │       │
│  │  - Если count > 0 → блокирует suspend             │       │
│  │  - Интегрирован с PM (Power Management) core      │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  autosleep: система автоматически пытается заснуть          │
│  Если нет активных wakeup_sources → suspend                 │
└──────────────────────────────────────────────────────────────┘
```

### Типы WakeLock в Android

| Тип | CPU | Экран | Клавиатура | Применение |
|-----|-----|-------|------------|------------|
| `PARTIAL_WAKE_LOCK` | Работает | Выкл | Выкл | Скачивание, музыка |
| `SCREEN_DIM_WAKE_LOCK` | Работает | Тусклый | Выкл | Deprecated |
| `SCREEN_BRIGHT_WAKE_LOCK` | Работает | Яркий | Выкл | Deprecated |
| `FULL_WAKE_LOCK` | Работает | Яркий | Яркая | Deprecated |
| `PROXIMITY_WAKE_LOCK` | Работает | Зависит | Выкл | Звонок у уха |

> Начиная с API 17, только `PARTIAL_WAKE_LOCK` не deprecated. Для управления экраном используйте `FLAG_KEEP_SCREEN_ON` на Window.

### Механизм autosleep

```c
// Упрощённая логика autosleep (kernel/power/autosleep.c)

// Ядро постоянно пытается заснуть
static void try_to_suspend(struct work_struct *work)
{
    unsigned int initial_count, final_count;

    // Проверяем количество активных wakeup events
    initial_count = pm_get_wakeup_count();

    // Если есть активные wakeup_sources — отмена
    if (!pm_save_wakeup_count(initial_count)) {
        // Кто-то держит wakeup_source — не засыпаем
        goto out;
    }

    // Пытаемся перейти в suspend
    pm_suspend(PM_SUSPEND_MEM);

out:
    // Планируем следующую попытку
    queue_up_suspend_work();
}
```

### Отладка проблем с батареей

```bash
# Посмотреть активные wakeup_sources
cat /sys/kernel/debug/wakeup_sources

# Формат вывода:
# name       active_count  event_count  wakeup_count  expire_count
#            active_since  total_time   max_time      last_change
#            prevent_suspend_time

# Через dumpsys (более удобно)
adb shell dumpsys power | grep -A 5 "Wake Locks"

# Battery historian
adb shell dumpsys batterystats --reset
# ... используем устройство ...
adb shell dumpsys batterystats > batterystats.txt
adb bugreport > bugreport.zip
# Загружаем в https://bathist.ef.lc/
```

---

## SELinux (Security-Enhanced Linux)

### Android + SELinux = обязательное сочетание

Большинство Linux-дистрибутивов (Ubuntu, Debian) **не используют** SELinux или используют в permissive mode. Android — противоположность:

- **Android 4.3**: SELinux в permissive mode (только логирование)
- **Android 4.4**: Enforcing для критичных доменов (installd, netd, vold, zygote)
- **Android 5.0+**: Full enforcing mode. **Обязательно для CTS** (Compatibility Test Suite)

### Три уровня безопасности Android

```
┌──────────────────────────────────────────────────────────────┐
│              ТРИ УРОВНЯ БЕЗОПАСНОСТИ ANDROID                 │
│                                                              │
│  ┌────────────────────────────────────────────────────┐      │
│  │  УРОВЕНЬ 3: SELinux (MAC — Mandatory Access Control)│     │
│  │                                                      │     │
│  │  Даже если процесс имеет права (DAC) и правильный   │     │
│  │  UID (Binder), SELinux может запретить операцию.     │     │
│  │  Правила заданы в .te файлах, не меняются runtime.   │     │
│  │                                                      │     │
│  │  Пример: untrusted_app НЕ МОЖЕТ читать              │     │
│  │  /data/system даже если каким-то образом получит     │     │
│  │  права root.                                         │     │
│  └──────────────────────────────────────────────────────┘     │
│                          ▲                                    │
│  ┌───────────────────────┴──────────────────────────────┐    │
│  │  УРОВЕНЬ 2: Binder (UID/PID проверка)                │    │
│  │                                                      │    │
│  │  Ядро вставляет UID/PID вызывающего в Binder-        │    │
│  │  транзакцию. Сервис проверяет через                   │    │
│  │  checkCallingPermission(). Подделать невозможно.      │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ▲                                    │
│  ┌───────────────────────┴──────────────────────────────┐    │
│  │  УРОВЕНЬ 1: DAC (Unix permissions + Android sandbox) │    │
│  │                                                      │    │
│  │  Каждое приложение = отдельный Linux user (UID).     │    │
│  │  Файловые права: rwx для owner, ничего для others.  │    │
│  │  Изоляция через стандартные Unix-механизмы.          │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Type Enforcement

В SELinux каждый объект имеет **контекст безопасности** (label):

```
# Формат: user:role:type:level
# Для Android важен type (он же domain для процессов)

# Посмотреть контекст процесса
ps -eZ | grep system_server
# u:r:system_server:s0  system  1234  ... system_server

# Посмотреть контекст файла
ls -Z /data/system/
# u:object_r:system_data_file:s0  packages.xml

# Контексты определены в файлах:
# /system/etc/selinux/plat_file_contexts
# /vendor/etc/selinux/vendor_file_contexts
```

### Ключевые домены Android

| Домен | Процесс | Описание |
|-------|---------|----------|
| `init` | /init | Первый процесс, запускает всё |
| `zygote` | zygote / zygote64 | Родитель всех Java-процессов |
| `system_server` | system_server | Системные сервисы (AMS, WMS, PMS) |
| `system_app` | Settings, SystemUI | Системные приложения |
| `platform_app` | Calendar, Contacts | Приложения платформы |
| `untrusted_app` | Все сторонние | Ваше приложение из Play Store |
| `isolated_app` | WebView renderer | Максимальная изоляция |
| `priv_app` | GMS (Google) | Привилегированные приложения |
| `mediaserver` | mediaserver | Воспроизведение/запись медиа |
| `surfaceflinger` | SurfaceFlinger | Композитинг экрана |
| `installd` | installd | Установка APK |
| `vold` | vold | Управление хранилищем |
| `netd` | netd | Сеть, firewall, DNS |

### Пример SELinux-политики

```
# Файл: untrusted_app.te
# Определяет, что может делать стороннее приложение

# Запрет: стороннее приложение не может
# обращаться к отладочным устройствам
neverallow untrusted_app debugfs:file { read write };

# Запрет: не может менять SELinux-политики
neverallow untrusted_app kernel:security { setenforce setbool };

# Запрет: не может загружать модули ядра
neverallow untrusted_app self:capability sys_module;

# Разрешение: может использовать Binder для связи с system_server
allow untrusted_app system_server:binder { call transfer };

# Разрешение: может читать/писать свои файлы
allow untrusted_app app_data_file:file { read write create unlink };
allow untrusted_app app_data_file:dir { search add_name remove_name };

# Разрешение: может использовать сеть
allow untrusted_app self:tcp_socket { create connect write read };
allow untrusted_app self:udp_socket { create connect write read };
```

### Binder и SELinux

Binder-транзакции также проверяются SELinux:

```
# Правило для Binder call между untrusted_app и system_server
allow untrusted_app system_server:binder call;

# Правило для передачи Binder-объектов
allow untrusted_app system_server:binder transfer;

# В Binder driver (ядро):
// binder_transaction() вызывает security_binder_transaction()
// которая проверяет SELinux-политику
static int security_binder_transaction(
    const struct cred *from,    // Отправитель
    const struct cred *to)      // Получатель
{
    // Проверяем: разрешено ли from->domain вызывать to->domain через binder
    return avc_has_perm(from->security, to->security,
                        SECCLASS_BINDER, BINDER__CALL, NULL);
}
```

### Цепочка принятия решения SELinux

```
┌──────────────────────────────────────────────────────────────┐
│            ЦЕПОЧКА РЕШЕНИЯ SELinux                            │
│                                                              │
│  Процесс (u:r:untrusted_app:s0)                            │
│  хочет прочитать файл /data/system/packages.xml             │
│  (u:object_r:system_data_file:s0)                           │
│                                                              │
│  ┌────────────┐                                              │
│  │ DAC Check  │──── rwx?  ──▶ Файл принадлежит system,      │
│  │ (Unix      │              untrusted_app = другой user     │
│  │  permissions)│             → DENIED на уровне DAC         │
│  └────────────┘                                              │
│       │ (если бы DAC разрешил)                               │
│       ▼                                                      │
│  ┌────────────┐                                              │
│  │ SELinux    │──── Ищем правило:                            │
│  │ AVC Check  │     allow untrusted_app                      │
│  │            │     system_data_file:file read;              │
│  └────────────┘                                              │
│       │                                                      │
│       ▼                                                      │
│  ┌────────────┐                                              │
│  │ Результат  │     Такого правила НЕТ                       │
│  │            │     + есть neverallow                         │
│  │            │     → DENIED                                 │
│  │            │     → avc: denied в logcat                   │
│  └────────────┘                                              │
│                                                              │
│  logcat:                                                     │
│  avc: denied { read } for pid=12345                          │
│  scontext=u:r:untrusted_app:s0:c512,c768                    │
│  tcontext=u:object_r:system_data_file:s0                     │
│  tclass=file permissive=0                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Seccomp-BPF

### Фильтрация системных вызовов

Seccomp-BPF — механизм ядра Linux, позволяющий фильтровать системные вызовы на уровне ядра. Android применяет его с Android 8.0 (Oreo).

### Как это работает в Android

```
┌──────────────────────────────────────────────────────────────┐
│              SECCOMP-BPF В ANDROID                           │
│                                                              │
│  ┌──────────┐                                                │
│  │  init    │                                                │
│  │          │                                                │
│  └────┬─────┘                                                │
│       │ fork + exec                                          │
│       ▼                                                      │
│  ┌──────────┐                                                │
│  │ Zygote   │  ← Устанавливает seccomp-BPF фильтр          │
│  │          │    ОДИН РАЗ при старте                        │
│  └────┬─────┘                                                │
│       │ fork (для каждого приложения)                        │
│       ▼                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  App A   │  │  App B   │  │  App C   │                   │
│  │          │  │          │  │          │                   │
│  │ Наследует│  │ Наследует│  │ Наследует│                   │
│  │ seccomp  │  │ seccomp  │  │ seccomp  │                   │
│  │ фильтр   │  │ фильтр   │  │ фильтр   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│                                                              │
│  Syscall от приложения:                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                 │
│  │ App      │──▶│ Seccomp  │──▶│ Ядро     │                 │
│  │ вызывает │   │ BPF      │   │ выполняет│                 │
│  │ syscall  │   │ фильтр   │   │ syscall  │                 │
│  └──────────┘   └─────┬────┘   └──────────┘                 │
│                       │                                      │
│                 Если syscall                                  │
│                 заблокирован:                                 │
│                       │                                      │
│                 ┌─────▼────┐                                  │
│                 │ SIGKILL  │  ← Процесс убит                │
│                 │ или ERRNO│  ← или ошибка                   │
│                 └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘
```

### Заблокированные системные вызовы

Android блокирует syscalls, которые:
- Не нужны обычным приложениям
- Имеют историю эксплуатации уязвимостей
- Могут нарушить изоляцию

```c
// Примеры заблокированных syscalls в Android (arm64)
// Из bionic/libc/seccomp/

// Управление ядром (опасно)
BPF_DENY(kexec_load);        // Загрузка нового ядра
BPF_DENY(kexec_file_load);   // Загрузка нового ядра (из файла)
BPF_DENY(reboot);            // Перезагрузка
BPF_DENY(init_module);       // Загрузка модулей ядра
BPF_DENY(finit_module);      // Загрузка модулей из fd

// Файловые системы (опасно)
BPF_DENY(mount);             // Монтирование ФС
BPF_DENY(umount2);           // Размонтирование
BPF_DENY(swapon);            // Включение swap
BPF_DENY(swapoff);           // Выключение swap

// Отладка (уязвимости)
BPF_DENY(ptrace);            // Отладка процессов
                              // (разрешено для debuggable apps
                              //  через SELinux, не seccomp)

// Ключи ядра (не нужны приложениям)
BPF_DENY(add_key);           // Добавление ключа в keyring
BPF_DENY(keyctl);            // Управление ключами

// Прочее
BPF_DENY(acct);              // Process accounting
BPF_DENY(syslog);            // Чтение kernel log

// Итого (arm64): 17 из 271 syscalls заблокированы
// Итого (arm):   70 из 364 syscalls заблокированы
// arm блокирует больше, т.к. многие legacy syscalls
```

### Установка фильтра в Zygote

```c
// Упрощённо: как Zygote устанавливает seccomp-фильтр
// bionic/libc/seccomp/seccomp_policy.cpp

bool set_app_seccomp_filter() {
    // Загрузка BPF-программы
    struct sock_filter filter[] = {
        // Загрузить номер syscall
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS,
                 offsetof(struct seccomp_data, nr)),

        // Проверить архитектуру (arm64 vs arm)
        // ...

        // Для каждого заблокированного syscall:
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRAP),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mount, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRAP),

        // ... остальные правила ...

        // По умолчанию: разрешить
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = ARRAY_SIZE(filter),
        .filter = filter,
    };

    // Установить фильтр (необратимо!)
    // PR_SET_NO_NEW_PRIVS — запрет повышения привилегий
    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
    prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);

    return true;
}
```

---

## FUSE и Scoped Storage

### Проблема доступа к файлам

До Android 10 любое приложение с `READ_EXTERNAL_STORAGE` могло читать **все файлы** на /sdcard. Это создавало проблемы приватности:
- Мессенджер мог читать фотографии из банковского приложения
- Игра могла сканировать все документы
- Вредоносное ПО получало полный доступ к файлам

### FUSE медиация

```
┌──────────────────────────────────────────────────────────────┐
│          ДОСТУП К ФАЙЛАМ: ДО И ПОСЛЕ SCOPED STORAGE         │
│                                                              │
│  ДО Android 10:                                             │
│  ┌──────────┐     ┌──────────────┐                          │
│  │   App    │────▶│  /sdcard/    │  Прямой доступ            │
│  │          │     │  (ext4/f2fs) │  ко всем файлам          │
│  └──────────┘     └──────────────┘                          │
│                                                              │
│  Android 11+ (с FUSE):                                      │
│  ┌──────────┐     ┌──────────────┐     ┌───────────────┐   │
│  │   App    │────▶│ /storage/    │────▶│  FUSE daemon  │   │
│  │          │     │ emulated/0/  │     │  (MediaProvider│   │
│  └──────────┘     │ (FUSE mount) │     │   process)    │   │
│                   └──────────────┘     └───────┬───────┘   │
│                                                │            │
│                                         Проверка:           │
│                                         1. Это свои файлы?  │
│                                         2. Есть permission? │
│                                         3. MediaStore grant? │
│                                                │            │
│                                         ┌──────▼──────┐    │
│                                         │  Нижняя ФС  │    │
│                                         │  (ext4/f2fs) │    │
│                                         └─────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Правила Scoped Storage

```
┌──────────────────────────────────────────────────────────────┐
│                 ПРАВИЛА ДОСТУПА К ФАЙЛАМ                     │
│                                                              │
│  Своя директория (/Android/data/<pkg>/):                    │
│  ✅ Полный доступ без permissions                            │
│  ✅ Файлы удаляются при деинсталляции                       │
│                                                              │
│  MediaStore (фото, видео, аудио):                           │
│  ✅ Чтение своих файлов — без permissions                    │
│  ⚠️  Чтение чужих — нужен READ_MEDIA_IMAGES и т.д.          │
│  ❌ Изменение/удаление чужих — через MediaStore.createWriteRequest│
│                                                              │
│  Downloads:                                                  │
│  ✅ Свои загруженные файлы — полный доступ                  │
│  ❌ Чужие файлы — недоступны                                │
│                                                              │
│  Произвольные файлы:                                         │
│  ❌ ACTION_OPEN_DOCUMENT / Storage Access Framework          │
│  ❌ MANAGE_EXTERNAL_STORAGE — только файл-менеджеры         │
└──────────────────────────────────────────────────────────────┘
```

### Производительность FUSE

FUSE добавляет накладные расходы — каждая файловая операция проходит через userspace:

```
БЕЗ FUSE:
App → syscall (open/read/write) → VFS → ext4 → блочное устройство

С FUSE:
App → syscall → VFS → FUSE kernel → FUSE daemon (userspace) →
→ VFS → ext4 → блочное устройство

Дополнительные расходы:
- 2 переключения контекста (kernel→user→kernel)
- Копирование данных между буферами
- Обработка в MediaProvider
```

**FUSE Passthrough (Android 12+):**
После первой проверки прав FUSE daemon может сообщить ядру: «для этого fd все операции разрешены — пересылай напрямую». Последующие read/write идут мимо userspace:

```
С FUSE Passthrough (после авторизации):
App → syscall → VFS → FUSE kernel → ext4 → блочное устройство
                        │
                        └── Минуя userspace daemon!

Производительность ≈ прямой доступ
```

### sdcardfs → FUSE

```
Timeline миграции файловой системы /sdcard:
┌────────┬──────────────┬─────────────────────────────────┐
│ Версия │ Механизм     │ Особенности                     │
├────────┼──────────────┼─────────────────────────────────┤
│ 1.0–4  │ FUSE (первая │ Простая проверка прав           │
│        │ версия)      │                                  │
├────────┼──────────────┼─────────────────────────────────┤
│ 5.0–10 │ sdcardfs     │ Ядерная ФС, быстрее FUSE.      │
│        │              │ Stackable FS поверх ext4/f2fs.  │
│        │              │ Не принят upstream.             │
├────────┼──────────────┼─────────────────────────────────┤
│ 11+    │ FUSE (новая  │ MediaStore медиация.            │
│        │ версия)      │ Passthrough в Android 12+.      │
│        │              │ Scoped Storage enforcement.     │
└────────┴──────────────┴─────────────────────────────────┘
```

---

## dm-verity и Verified Boot

### Цепочка доверия

Android Verified Boot (AVB) обеспечивает проверку целостности системы при каждой загрузке. Если системный раздел изменён — устройство предупреждает пользователя или отказывается загружаться.

```
┌──────────────────────────────────────────────────────────────┐
│                ЦЕПОЧКА ДОВЕРИЯ AVB                            │
│                                                              │
│  ┌────────────┐                                              │
│  │ Hardware   │  Корень доверия (Root of Trust)              │
│  │ Root of    │  Зашит в eFuse процессора                   │
│  │ Trust      │  Содержит публичный ключ OEM                │
│  └─────┬──────┘                                              │
│        │ Проверяет подпись                                    │
│        ▼                                                     │
│  ┌────────────┐                                              │
│  │ Bootloader │  Primary bootloader (BL1/BL2)               │
│  │            │  Проверен hardware root of trust             │
│  └─────┬──────┘                                              │
│        │ Проверяет подпись                                    │
│        ▼                                                     │
│  ┌────────────┐                                              │
│  │ boot.img   │  Содержит:                                  │
│  │            │  - Linux kernel (GKI)                        │
│  │            │  - ramdisk                                   │
│  │            │  - vbmeta подпись                            │
│  └─────┬──────┘                                              │
│        │ dm-verity для системных разделов                    │
│        ▼                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  system    │  │  vendor    │  │  product   │             │
│  │  partition │  │  partition │  │  partition │             │
│  │            │  │            │  │            │             │
│  │ dm-verity  │  │ dm-verity  │  │ dm-verity  │             │
│  │ hash tree  │  │ hash tree  │  │ hash tree  │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

### dm-verity: как работает

dm-verity — device-mapper target, который проверяет целостность блочного устройства при чтении. Каждый блок данных имеет хэш в дереве хэшей:

```
┌──────────────────────────────────────────────────────────────┐
│                  ДЕРЕВО ХЭШЕЙ dm-verity                      │
│                                                              │
│                    ┌────────────┐                             │
│                    │ Root Hash  │ ← Хранится в vbmeta        │
│                    │ (SHA-256)  │   (подписан OEM-ключом)    │
│                    └─────┬──────┘                             │
│                          │                                    │
│              ┌───────────┼───────────┐                        │
│              │                       │                        │
│        ┌─────▼─────┐          ┌─────▼─────┐                  │
│        │  Hash L1   │          │  Hash L1   │                  │
│        │  (block 0-3)│         │  (block 4-7)│                 │
│        └──┬───┬──┬──┘          └──┬───┬──┬──┘                 │
│           │   │  │                │   │  │                    │
│   ┌───┐ ┌─┘ ┌┘  └┐       ┌───┐ ┌─┘ ┌┘  └┐                  │
│   │   │ │   │    │       │   │ │   │    │                    │
│  ┌▼┐ ┌▼┐ ┌▼┐ ┌▼┐     ┌▼┐ ┌▼┐ ┌▼┐ ┌▼┐                     │
│  │0│ │1│ │2│ │3│     │4│ │5│ │6│ │7│   Data blocks          │
│  └─┘ └─┘ └─┘ └─┘     └─┘ └─┘ └─┘ └─┘                     │
│                                                              │
│  При чтении блока N:                                        │
│  1. Вычислить SHA-256(блок N)                               │
│  2. Сравнить с хэшем в leaf-ноде дерева                     │
│  3. Проверить цепочку хэшей до root                         │
│  4. Если не совпадает → I/O error                           │
└──────────────────────────────────────────────────────────────┘
```

### Состояния загрузки (Boot States)

| Состояние | Цвет | Значение |
|-----------|------|----------|
| Verified | Зелёный | Все подписи верны, bootloader заблокирован |
| Self-signed | Жёлтый | Используется пользовательский ключ |
| Unlocked | Оранжевый | Bootloader разблокирован (для разработчиков) |
| Failed | Красный | Верификация провалилась, возможна модификация |

```
┌─────────────────────────────────────────┐
│           СОСТОЯНИЯ ЗАГРУЗКИ            │
│                                          │
│  🟢 GREEN (Verified)                    │
│  │  Bootloader locked                   │
│  │  Подпись OEM — верна                 │
│  │  dm-verity — включён                 │
│  │  → Нормальная загрузка               │
│  │                                       │
│  🟡 YELLOW (Self-signed)                │
│  │  Bootloader locked                   │
│  │  Подпись пользовательская            │
│  │  dm-verity — включён                 │
│  │  → Предупреждение на 10 сек          │
│  │                                       │
│  🟠 ORANGE (Unlocked)                   │
│  │  Bootloader unlocked                 │
│  │  Подпись не проверяется              │
│  │  dm-verity — может быть отключён     │
│  │  → Предупреждение на 5 сек           │
│  │                                       │
│  🔴 RED (Failed)                        │
│  │  Bootloader locked                   │
│  │  Подпись — НЕВАЛИДНА                 │
│  │  → Предупреждение / отказ загрузки   │
└─────────────────────────────────────────┘
```

### Практические последствия

- **Модификация system.img** → dm-verity обнаружит → I/O error → устройство может не загрузиться
- **Magisk** обходит AVB, модифицируя boot.img (а не system) и патча init
- **OTA-обновления** работают вместе с dm-verity: новый system-раздел (A/B slots) имеет новое дерево хэшей
- **Rollback protection**: vbmeta содержит rollback index, предотвращающий откат на старую (уязвимую) версию

---

## cgroups и Energy-Aware Scheduling

### cgroups в Android

Android активно использует cgroups (Control Groups) для управления ресурсами процессов. Ключевые контроллеры:

### Иерархия cgroups

```
┌──────────────────────────────────────────────────────────────┐
│                ИЕРАРХИЯ CGROUPS В ANDROID                    │
│                                                              │
│  /dev/cpuctl/ (cpu controller)                               │
│  ├── top-app/            ← Приложение на экране             │
│  │   └── tasks: [PID текущего foreground app]               │
│  │   └── cpu.shares: 1024 (максимальный приоритет)          │
│  ├── foreground/         ← Видимые, но не top               │
│  │   └── tasks: [PIDs видимых activities/services]          │
│  │   └── cpu.shares: 512                                     │
│  ├── background/         ← Фоновые процессы                 │
│  │   └── tasks: [PIDs фоновых процессов]                    │
│  │   └── cpu.shares: 52  (минимальный приоритет)            │
│  └── system-background/  ← Системные фоновые               │
│      └── tasks: [PIDs системных daemon-ов]                  │
│      └── cpu.shares: 52                                      │
│                                                              │
│  /dev/cpuset/ (cpuset controller)                            │
│  ├── top-app/                                                │
│  │   └── cpus: 0-7       ← Все ядра (big + LITTLE)         │
│  ├── foreground/                                             │
│  │   └── cpus: 0-7       ← Все ядра                        │
│  ├── background/                                             │
│  │   └── cpus: 0-3       ← Только LITTLE ядра!             │
│  ├── system-background/                                      │
│  │   └── cpus: 0-3       ← Только LITTLE ядра              │
│  └── restricted/                                             │
│      └── cpus: 0-3       ← Только LITTLE ядра              │
│                                                              │
│  /dev/blkio/ (block I/O controller)                         │
│  ├── background/                                             │
│  │   └── blkio.weight: 200 (ниже приоритет I/O)            │
│  └── (default)                                               │
│      └── blkio.weight: 1000 (нормальный приоритет)          │
│                                                              │
│  /dev/memcg/ (memory controller)                            │
│  ├── apps/                                                   │
│  │   └── uid_<UID>/                                          │
│  │       └── pid_<PID>/                                      │
│  │           └── memory.limit_in_bytes                       │
│  └── system/                                                 │
│      └── memory.limit_in_bytes                               │
└──────────────────────────────────────────────────────────────┘
```

### ActivityManagerService и cgroups

```java
// Упрощённо: как AMS перемещает процессы между cgroups
// frameworks/base/services/core/java/com/android/server/am/ProcessList.java

void setOomAdj(int pid, int uid, int adj) {
    // 1. Записываем adj в /proc/pid/oom_score_adj (для lmkd)
    writeProcFile("/proc/" + pid + "/oom_score_adj", adj);

    // 2. Перемещаем процесс в нужную cgroup
    if (adj <= ProcessList.FOREGROUND_APP_ADJ) {
        // Foreground → все ядра, высокий приоритет CPU
        setCpusetGroup(pid, "top-app");
        setSchedGroup(pid, SCHED_GROUP_TOP_APP);
    } else if (adj <= ProcessList.VISIBLE_APP_ADJ) {
        setCpusetGroup(pid, "foreground");
        setSchedGroup(pid, SCHED_GROUP_DEFAULT);
    } else {
        // Background → только LITTLE ядра, низкий приоритет
        setCpusetGroup(pid, "background");
        setSchedGroup(pid, SCHED_GROUP_BACKGROUND);
    }
}
```

### big.LITTLE и cpuset

```
┌──────────────────────────────────────────────────────────────┐
│         РАСПРЕДЕЛЕНИЕ ЗАДАЧ НА big.LITTLE                    │
│                                                              │
│  Типичный SoC (например Snapdragon 8 Gen 3):               │
│                                                              │
│  ┌──────────────────────────────────────┐                    │
│  │           Cortex-X4 (prime)          │  Ядро 7            │
│  │  CPU 7: 3.3 GHz, высокое энергопотр.│                    │
│  └──────────────────────────────────────┘                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Cortex-A720  │  │ Cortex-A720  │  │ Cortex-A720  │       │
│  │ CPU 4: 3.2G  │  │ CPU 5: 3.2G  │  │ CPU 6: 3.2G  │       │
│  │ (big)        │  │ (big)        │  │ (big)        │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐               │
│  │A520    │ │A520    │ │A520    │ │A520    │               │
│  │CPU 0   │ │CPU 1   │ │CPU 2   │ │CPU 3   │               │
│  │2.0 GHz │ │2.0 GHz │ │2.0 GHz │ │2.0 GHz │               │
│  │(LITTLE)│ │(LITTLE)│ │(LITTLE)│ │(LITTLE)│               │
│  └────────┘ └────────┘ └────────┘ └────────┘               │
│                                                              │
│  cpuset распределение:                                       │
│  top-app:       CPU 0-7  (все ядра, включая prime)          │
│  foreground:    CPU 0-7  (все ядра)                         │
│  background:    CPU 0-3  (только LITTLE — экономия батареи) │
│  restricted:    CPU 0-3  (только LITTLE)                    │
│                                                              │
│  Результат:                                                  │
│  Фоновый процесс на LITTLE: ~2 ГГц, низкое энергопотр.     │
│  UI-поток на prime: ~3.3 ГГц, максимальная производительность│
└──────────────────────────────────────────────────────────────┘
```

### EAS (Energy-Aware Scheduling)

EAS — расширение планировщика Linux для ARM big.LITTLE (и подобных архитектур). Вместо того чтобы всегда выбирать самое быстрое ядро, EAS оценивает **энергетическую стоимость** размещения задачи:

```
┌──────────────────────────────────────────────────────────────┐
│              РЕШЕНИЕ EAS: КУДА ПОМЕСТИТЬ ЗАДАЧУ              │
│                                                              │
│  Задача: рендеринг UI-списка                                │
│  Нагрузка: 40% одного ядра                                  │
│                                                              │
│  Вариант A: LITTLE ядро (CPU 0, 2.0 GHz)                   │
│  ┌─────────────────────────────────────┐                     │
│  │ Производительность: достаточная     │                     │
│  │ Энергия: 100 mW                     │                     │
│  │ Задержка: приемлемая                │                     │
│  └─────────────────────────────────────┘                     │
│                                                              │
│  Вариант B: big ядро (CPU 4, 3.2 GHz)                      │
│  ┌─────────────────────────────────────┐                     │
│  │ Производительность: избыточная      │                     │
│  │ Энергия: 350 mW (+250%)             │                     │
│  │ Задержка: чуть ниже                 │                     │
│  └─────────────────────────────────────┘                     │
│                                                              │
│  EAS выберет: Вариант A (LITTLE)                            │
│  Потому что: задаче хватает производительности LITTLE,       │
│  а энергозатраты в 3.5× ниже.                               │
│                                                              │
│  Но для top-app с флагом SCHED_BOOST:                       │
│  EAS выберет big ядро → минимальная задержка UI              │
└──────────────────────────────────────────────────────────────┘
```

### SCHED_FIFO для критичных потоков

Android использует `SCHED_FIFO` (real-time scheduling policy) для потоков, где недопустимы задержки:

```c
// Потоки с SCHED_FIFO в Android:

// 1. RenderThread — отрисовка UI
//    Приоритет: SCHED_FIFO, prio=2
//    Почему: 16.6 мс на кадр (60 FPS), любая задержка = jank

// 2. Audio threads (AudioFlinger)
//    Приоритет: SCHED_FIFO, prio=3
//    Почему: буфер аудио ~5 мс, задержка = заикание

// 3. SurfaceFlinger main thread
//    Приоритет: SCHED_FIFO, prio=2
//    Почему: композитинг экрана каждый VSYNC

// 4. HwBinder threads (HAL)
//    Приоритет: может быть SCHED_FIFO для real-time HAL

// Установка в коде (нативный):
struct sched_param param;
param.sched_priority = 2;  // 1-99 для FIFO
sched_setscheduler(0, SCHED_FIFO, &param);
```

---

## Подводные камни

### 1. Binder buffer overflow (TransactionTooLargeException)

```
Симптом: TransactionTooLargeException при передаче данных через Intent/Bundle
Причина: Binder-буфер ограничен ~1 МБ НА ПРОЦЕСС (не на транзакцию!)
         Все активные транзакции процесса делят этот буфер.

Решение:
- Не передавать большие объекты через Bundle
- Использовать ContentProvider / SharedMemory для больших данных
- Помнить: Bundle сериализуется в Parcel → все данные копируются
```

### 2. WakeLock leak → battery drain

```
Симптом: приложение потребляет батарею в фоне
Причина: WakeLock.acquire() без release() или без таймаута
         Устройство не может заснуть

Решение:
- ВСЕГДА используйте acquire(timeout) вместо acquire()
- Используйте try/finally для release()
- WorkManager автоматически управляет wakelocks
- Проверяйте: adb shell dumpsys power | grep "Wake Locks"
```

### 3. SELinux denial при доступе к файлам вендора

```
Симптом: avc: denied в logcat, функционал не работает
Причина: SELinux-политика не разрешает доступ
         Часто после обновления targetSdkVersion

Решение:
- НЕ переводите SELinux в permissive (нарушает CTS)
- Используйте audit2allow для генерации правил (.te)
- Проверьте контексты: ls -Z, ps -eZ
- Для vendor-кода: обновите sepolicy в device tree
```

### 4. lmkd убивает приложение с foreground service

```
Симптом: foreground service убивается на устройствах с малой RAM
Причина: adj foreground service = 200 (PERCEPTIBLE)
         На устройствах с 2 ГБ RAM lmkd агрессивнее

Решение:
- Убедитесь, что notification активен (иначе adj повышается)
- Используйте foregroundServiceType правильно
- Для критичных задач: WorkManager с Constraints
- Профилируйте потребление памяти: Studio Profiler
```

### 5. DMA-BUF утечки при работе с камерой/GPU

```
Симптом: рост /proc/pid/fd, OOM через несколько минут
Причина: DMA-BUF fd не закрыт после использования
         Каждый буфер = физическая память, не подлежит swap

Решение:
- Закрывайте fd после munmap()
- Используйте HardwareBuffer (Java API) — GC очистит
- Мониторинг: cat /proc/pid/fdinfo/* | grep dma
- dumpsys meminfo <pid> → покажет "DMA-BUF" раздел
```

### 6. FUSE overhead при массовых файловых операциях

```
Симптом: медленное чтение/запись файлов на shared storage
Причина: каждая операция проходит через FUSE daemon
         Random reads могут быть в 2× медленнее

Решение:
- Используйте app-specific storage (/data/data/) для I/O-интенсивных задач
- Batch-операции через MediaStore
- Для больших файлов: requestLegacyExternalStorage (deprecated!)
  или переход на content:// URI
- FUSE passthrough (Android 12+) помогает автоматически
```

---

## Мифы и заблуждения

### Миф 1: «Android-ядро сильно отличается от Linux»

**Реальность**: Начиная с 2019–2020, почти все Android-специфичные патчи приняты в mainline Linux. Binder — в mainline 5.0. GKI — стандартное ядро с загружаемыми модулями. Разница между Android-ядром и vanilla Linux сейчас минимальна — в основном конфигурация (включённые модули) и вендорные драйверы.

### Миф 2: «SELinux замедляет Android»

**Реальность**: Накладные расходы SELinux — менее 1% CPU. Решения кэшируются в AVC (Access Vector Cache). Первая проверка: ~микросекунды, повторная (из кэша): ~наносекунды. Google измерял: разница в производительности с включённым и выключенным SELinux статистически незначима.

### Миф 3: «Linux OOM killer достаточен для мобильных устройств»

**Реальность**: Linux OOM killer срабатывает, когда память **уже** исчерпана — все процессы стоят, система подвисает. lmkd убивает **превентивно**, до наступления OOM. Без lmkd Android-устройство с 2–4 ГБ RAM было бы непригодно для использования — OOM killer мог бы убить foreground-приложение.

### Миф 4: «Root-доступ даёт полный контроль над Android»

**Реальность**: Даже с root (UID 0) SELinux в enforcing mode ограничивает действия. Процесс с UID 0, но в домене `untrusted_app`, не может обойти neverallow-правила. Magisk обходит это, запуская su daemon в собственном SELinux-домене (magisk), для которого политики написаны специально.

### Миф 5: «Wakelocks — основная причина разряда батареи»

**Реальность**: С Android 6.0+ (Doze mode) и 9.0+ (App Standby Buckets) wakelocks ограничены системой. Doze откладывает wakelocks до maintenance window. Основные причины разряда сейчас — фоновая сеть, GPS, push-уведомления и экран, а не wakelocks.

---

## CS-фундамент

| Концепция ядра | Где в CS | Связь с Android |
|---------------|---------|-----------------|
| **Процессы и потоки** | [[os-processes-threads]] | fork() в Zygote, cgroups для приоритетов |
| **Виртуальная память** | [[os-memory-management]] | mmap в Binder, ashmem, ION буферы |
| **IPC механизмы** | [[os-processes-threads]] | Binder vs pipes vs sockets vs shared memory |
| **Планирование** | [[os-processes-threads]] | EAS, SCHED_FIFO, cgroups cpu.shares |
| **Файловые системы** | CS fundamentals | FUSE, ext4/f2fs, dm-verity, VFS |
| **Модули ядра** | OS kernel | GKI + KMI, вендорные .ko модули |
| **Безопасность** | [[os-memory-management]] | SELinux MAC, seccomp-BPF, DAC |
| **Device drivers** | OS kernel | Binder driver, ashmem driver |
| **Memory allocators** | [[os-memory-management]] | ION heaps, DMA-BUF, slab/slub |
| **Power management** | OS kernel | wakeup_sources, autosleep, cpuidle |

---

## Проверь себя

> [!question]- Почему Binder реализован как kernel driver, а не userspace-библиотека?
> Три причины:
> 1. **Безопасность**: ядро вставляет UID/PID отправителя в транзакцию. Подделать невозможно — credentials заполняет ядро, а не процесс. В userspace IPC (D-Bus) credentials передаются через менее надёжный SO_PEERCRED.
> 2. **Производительность**: данные копируются один раз (copy_from_user), а получатель читает через mmap — без второго копирования. Pipe/socket делают две копии.
> 3. **Lifecycle management**: ядро отслеживает ссылки на Binder-объекты. При гибели процесса ядро уведомляет всех держателей ссылок (death notification). В userspace это потребовало бы отдельного мониторинга.

> [!question]- Чем ashmem отличается от POSIX shared memory и почему Android мигрирует на memfd?
> **Отличие ashmem от POSIX shm**:
> - ashmem поддерживает pin/unpin: UNPINNED-страницы могут быть рекламированы ядром под давлением памяти. POSIX shm не умеет этого.
> - ashmem — анонимный (передаётся через fd), POSIX shm — именованный (через /dev/shm).
>
> **Почему миграция на memfd**:
> - ashmem не принят в upstream Linux (удалён из staging в ядре 5.18)
> - memfd_create — upstream-функция (ядро 3.17+), поддерживается везде
> - memfd использует file seals (F_SEAL_SHRINK, F_SEAL_FUTURE_WRITE) для защиты вместо pin/unpin
> - Для полной совместимости с ashmem добавлен F_SEAL_FUTURE_EXEC

> [!question]- Как lmkd решает, какой процесс убить, и чем PSI лучше старых minfree-порогов?
> **Алгоритм lmkd**:
> 1. PSI-монитор ядра срабатывает при превышении порога (например, 70 мс stall за 1 секунду)
> 2. lmkd определяет уровень давления (LOW/MEDIUM/CRITICAL)
> 3. На основе уровня выбирает минимальный adj (например, при CRITICAL — adj ≥ 200)
> 4. Среди процессов с adj ≥ min_adj выбирает процесс с наибольшим RSS
> 5. Отправляет SIGKILL
>
> **PSI лучше minfree**:
> - minfree реагирует на количество свободных страниц — грубая метрика, не учитывает кэши и swap
> - PSI измеряет реальное время ожидания процессами памяти — это прямой индикатор деградации
> - PSI различает partial (один процесс ждёт) и full (все ждут) stall
> - Android 11+ учитывает thrashing (перетасовка страниц) для ещё более точного решения

> [!question]- Как работает трёхуровневая безопасность Android (DAC + Binder + SELinux)?
> **Уровень 1 — DAC (Discretionary Access Control)**:
> Каждое приложение получает уникальный Linux UID. Файлы приложения принадлежат этому UID с правами 0700. Другие приложения не могут читать/писать файлы — стандартная Unix-изоляция.
>
> **Уровень 2 — Binder UID проверка**:
> При вызове системного сервиса через Binder, ядро автоматически вставляет UID/PID вызывающего. Сервис вызывает `checkCallingPermission()` для проверки прав. Подделать UID невозможно.
>
> **Уровень 3 — SELinux MAC (Mandatory Access Control)**:
> Даже если DAC разрешает и Binder проверка пройдена, SELinux может запретить операцию. Правила заданы в .te файлах и не могут быть изменены runtime. neverallow-правила обеспечивают защиту даже от root.
>
> Все три уровня работают одновременно. Для успешного доступа нужно пройти ВСЕ три проверки.

---

## Ключевые карточки

> [!tip] Binder — одна копия
> Binder копирует данные **один раз**: copy_from_user (отправитель → ядро). Получатель читает через mmap — нулевое копирование. Pipe/socket требуют двух копий. Это ядерный механизм, не userspace-оптимизация.

> [!tip] ashmem → memfd
> ashmem удалён из upstream Linux (ядро 5.18). Android мигрирует на memfd_create (ядро 3.17+). Ключевое отличие ashmem — pin/unpin для kernel reclaim. В memfd используются file seals (F_SEAL_*) вместо pin/unpin.

> [!tip] ION → DMA-BUF Heaps
> ION (один /dev/ion, грубый SELinux) заменён на DMA-BUF heaps (по /dev/dma_heap/* на каждый тип, гранулярный SELinux). Принят в mainline Linux 5.6. Обязателен с Android 12 (GKI 2.0).

> [!tip] lmkd + PSI
> lmkd — userspace daemon (не kernel driver). Использует PSI (Pressure Stall Information) для определения давления памяти. PSI измеряет реальное время ожидания, а не просто количество свободных страниц. Убивает превентивно, до OOM.

> [!tip] SELinux = Enforcing
> Android ТРЕБУЕТ SELinux в enforcing mode (обязательно для CTS с Android 5.0). Три уровня: DAC → Binder UID → SELinux MAC. Даже root ограничен neverallow-правилами. Домены: untrusted_app (ваше приложение), system_server, zygote и др.

> [!tip] GKI = единое ядро
> С Android 12 Google контролирует единый образ ядра (GKI) для всех устройств. Вендорный код — загружаемые модули (.ko) через стабильный KMI. Обновления безопасности ядра — недели, не месяцы. Обязателен на всех AArch64 форм-факторах с 2024.

> [!tip] FUSE + Scoped Storage
> Android 11+ использует FUSE для /sdcard: каждая файловая операция проходит через MediaProvider (FUSE daemon). Проверяет права доступа. FUSE passthrough (Android 12+) минимизирует overhead: после авторизации read/write идут напрямую в нижнюю ФС.

---

## Сводная таблица Android-расширений ядра

```
┌──────────────────────────────────────────────────────────────────────────┐
│           СВОДНАЯ ТАБЛИЦА: РАСШИРЕНИЯ ЯДРА ANDROID                      │
│                                                                          │
│  Компонент        │ Статус upstream │ Замена          │ Версия Android   │
│═══════════════════│════════════════│═════════════════│═════════════════  │
│  Binder           │ mainline 5.0   │ —               │ 1.0+             │
│  ashmem           │ удалён 5.18    │ memfd_create    │ 1.0 → deprecated │
│  ION              │ удалён 5.11    │ DMA-BUF heaps   │ 4.0 → deprecated │
│  Low Memory Kill  │ удалён 4.12    │ lmkd (userspace)│ 9.0+             │
│  wakelocks        │ заменён 3.5    │ wakeup_sources  │ 1.0 → переход    │
│  logger           │ никогда        │ logd (userspace) │ 5.0+             │
│  paranoid network │ никогда        │ eBPF (userspace) │ 9.0+             │
│  sdcardfs         │ никогда        │ FUSE             │ 11+              │
│  RAM console      │ mainline       │ pstore           │ автоматически    │
│  pmem             │ никогда        │ ION → DMA-BUF    │ deprecated рано  │
│  alarm-dev        │ никогда        │ timerfd          │ переход           │
│  timed GPIO       │ никогда        │ LED class        │ переход           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Хронология upstream-принятия

```
Upstream     Год      Что принято
kernel       принятия
─────────────────────────────────────────────────────
3.5          2012     wakeup_sources (замена wakelocks)
3.17         2014     memfd_create (будущая замена ashmem)
3.19         2015     Binder в staging tree
4.12         2017     Удалён lowmemorykiller driver
4.20         2018     PSI (Pressure Stall Information)
5.0          2019     Binder в mainline (drivers/android/)
5.6          2020     DMA-BUF heaps framework
5.11         2021     ION удалён из staging
5.18         2022     ashmem удалён из staging
6.x          2023+    Binder improvements (binderfs и др.)
```

### Полезные команды для исследования ядра

```bash
# Версия ядра на устройстве
adb shell cat /proc/version
# Linux version 5.15.104-android13-8-... (GKI)

# Загруженные модули ядра
adb shell lsmod
# binder_linux     200704  53  — Binder driver
# ...

# Информация о Binder
adb shell cat /proc/binder/stats
adb shell cat /proc/binder/transactions
adb shell cat /proc/binder/state

# SELinux статус
adb shell getenforce
# Enforcing

# SELinux контекст текущего процесса
adb shell cat /proc/self/attr/current
# u:r:shell:s0

# PSI давление памяти
adb shell cat /proc/pressure/memory
# some avg10=0.00 avg60=0.00 avg300=0.00 total=12345
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0

# PSI давление CPU
adb shell cat /proc/pressure/cpu
# some avg10=2.50 avg60=1.20 avg300=0.80 total=67890

# PSI давление I/O
adb shell cat /proc/pressure/io

# cgroups текущего процесса
adb shell cat /proc/self/cgroup
# 0::/top-app

# Список DMA-BUF heaps
adb shell ls /dev/dma_heap/
# system  system-uncached  cma  ...

# Информация о DMA-BUF буферах
adb shell cat /proc/dma_buf/bufinfo

# Wakeup sources
adb shell cat /sys/kernel/debug/wakeup_sources

# dm-verity статус
adb shell getprop ro.boot.verifiedbootstate
# green

# GKI версия
adb shell uname -r
# 5.15.104-android13-8-xxxxx

# Seccomp статус процесса
adb shell cat /proc/<PID>/status | grep Seccomp
# Seccomp:	2    (2 = SECCOMP_MODE_FILTER)
```

### Как устроен /proc/binder/

```
/proc/binder/
├── stats                ← Общая статистика Binder
│   └── binder_proc: <PID>
│       ├── threads: N        ← Активные Binder-потоки
│       ├── requested_threads  ← Запрошенные потоки
│       ├── ready_threads      ← Готовые к обработке
│       ├── nodes: N           ← Binder-ноды процесса
│       ├── refs: N            ← Ссылки на удалённые ноды
│       ├── pending: N         ← Ожидающие транзакции
│       └── buffers: N/Total   ← Использование mmap-буфера
│
├── transactions         ← Активные транзакции
│   └── transaction <ID>
│       ├── from <PID>:<TID>  ← Кто отправил
│       ├── to <PID>:<TID>    ← Кому
│       ├── code: N            ← Код операции
│       └── flags: N           ← ONE_WAY и др.
│
├── state                ← Полное состояние (огромный вывод)
├── failed_transaction_log ← Лог упавших транзакций
└── transaction_log      ← Лог последних транзакций
```

---

## Куда дальше

| Направление | Файл | Что узнаете |
|-------------|------|-------------|
| Binder подробно | [[android-binder-ipc]] | Протокол, AIDL, threading, death notifications |
| Загрузка системы | [[android-boot-process]] | init → Zygote → SystemServer → Launcher |
| Память процессов | [[android-process-memory]] | RSS, PSS, USS, adj scores, zRAM |
| Системные сервисы | [[android-system-services]] | AMS, WMS, PMS — как используют ядро |
| Архитектура | [[android-architecture]] | Слои Android: ядро → HAL → framework → apps |
| Процессы ОС | [[os-processes-threads]] | Теория процессов, потоков, планирования |
| Память ОС | [[os-memory-management]] | Виртуальная память, paging, mmap |

---

## Связи

### Прямые зависимости (prerequisites)
- [[os-processes-threads]] — процессы, потоки, планирование
- [[os-memory-management]] — виртуальная память, mmap, paging
- [[android-architecture]] — общая архитектура Android

### Развитие темы
- [[android-binder-ipc]] — детальный разбор Binder IPC
- [[android-boot-process]] — загрузка Android (init, Zygote, SystemServer)
- [[android-process-memory]] — управление памятью процессов
- [[android-system-services]] — системные сервисы поверх ядра

### Связанные концепции
- [[android-art-runtime]] — ART runtime поверх ядра
- [[jvm-memory-model]] — модель памяти JVM (над ядерной)

---

## Источники

### Официальная документация
- [Android Kernel Overview](https://source.android.com/docs/core/architecture/kernel) — обзор ядра Android
- [Generic Kernel Image (GKI)](https://source.android.com/docs/core/architecture/kernel/generic-kernel-image) — спецификация GKI
- [SELinux in Android](https://source.android.com/docs/security/features/selinux) — документация SELinux
- [Low Memory Killer Daemon](https://source.android.com/docs/core/perf/lmkd) — спецификация lmkd
- [FUSE Passthrough](https://source.android.com/docs/core/storage/fuse-passthrough) — FUSE passthrough
- [DMA-BUF Heaps Transition](https://source.android.com/docs/core/architecture/kernel/dma-buf-heaps) — миграция ION → DMA-BUF
- [Scoped Storage](https://source.android.com/docs/core/storage/scoped) — Scoped Storage

### Презентации и статьи
- [Greg Kroah-Hartman: Android and the Linux Kernel Community (LWN, 2010)](https://lwn.net/Articles/372419/) — историческая статья
- [Destaging ION (LWN, 2019)](https://lwn.net/Articles/792733/) — удаление ION из staging
- [The Android ION Memory Allocator (LWN, 2012)](https://lwn.net/Articles/480055/) — обзор ION
- [Android Kernel Notes from LPC 2020 (LWN)](https://lwn.net/Articles/830979/) — заметки с Linux Plumbers
- [DMA-BUF Heap Transition in AOSP (Linaro)](https://old.linaro.org/blog/dma-buf-heap-transition-in-aosp/) — миграция на DMA-BUF
- [Seccomp Filter in Android O (Android Developers Blog, 2017)](https://android-developers.googleblog.com/2017/07/seccomp-filter-in-android-o.html) — seccomp в Android
- [Transitioning Android from ashmem to memfd (LPC 2025)](https://lpc.events/event/19/contributions/2117/) — миграция ashmem → memfd
- [Android Kernel Wakelock Solution (Linux Foundation)](https://www.linuxfoundation.org/blog/blog/android-kernel-wakelock-solution) — история wakelocks

### Книги
- Karim Yaghmour, «Embedded Android» — внутренности Android, включая ядро
- Jonathan Levin, «Android Internals: A Confectioner's Cookbook» — глубокое погружение
- Robert Love, «Linux Kernel Development, 3rd Edition» — основы ядра Linux

### Исходный код
- [AOSP Kernel Source](https://android.googlesource.com/kernel/common/) — android-mainline ветка
- [Binder Driver](https://android.googlesource.com/kernel/common/+/refs/heads/android-mainline/drivers/android/binder.c) — исходный код binder.c
- [lmkd Source](https://android.googlesource.com/platform/system/memory/lmkd/) — исходный код lmkd
- [SELinux Policy](https://android.googlesource.com/platform/system/sepolicy/) — SELinux-политики Android
- [eLinux.org Android Pages](https://elinux.org/Android_Portal) — wiki по Android internals
