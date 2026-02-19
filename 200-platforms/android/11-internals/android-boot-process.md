---
title: "Загрузка Android: от кнопки питания до Launcher"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/boot
  - topic/internals
  - type/deep-dive
  - level/expert
related:
  - "[[android-system-services]]"
  - "[[android-activitythread-internals]]"
  - "[[android-binder-ipc]]"
  - "[[android-kernel-extensions]]"
  - "[[android-app-startup-performance]]"
  - "[[android-process-memory]]"
  - "[[android-architecture]]"
  - "[[android-art-runtime]]"
cs-foundations: [boot-sequence, process-model, init-system, class-loading, socket-ipc]
prerequisites:
  - "[[android-architecture]]"
  - "[[os-processes-threads]]"
  - "[[android-kernel-extensions]]"
reading_time: 95
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Загрузка Android: от кнопки питания до Launcher

> **Hook:** Каждый раз при включении Android загружает 8 000+ Java-классов, запускает ~100 системных сервисов и fork'ает шаблонный процесс — за 10-30 секунд. За эти секунды выстраивается цепочка доверия от аппаратного ROM до каждого APK, поднимается ядро Linux с Android-специфичными патчами, запускается уникальная система инициализации и рождается процесс, от которого произойдут все приложения. Понимание этой цепочки — фундамент для оптимизации запуска, отладки системных проблем и глубокого понимания платформы.

---

## Зачем это нужно

| Проблема | Как помогает знание загрузки |
|---|---|
| Медленный холодный старт приложения | Понимание Zygote fork + preloaded classes помогает оптимизировать первые миллисекунды |
| ContentProvider инициализируется до Application.onCreate() | Знание порядка: fork → preload → bindApplication → installProviders → onCreate |
| Приложение крашится только при cold start | Разница между Zygote fork (чистый процесс) и тёплым перезапуском |
| Непонятные ANR при загрузке | SystemServer ещё не готов, AMS не отвечает на Binder-вызовы |
| Системный сервис не найден | servicemanager ещё не зарегистрировал сервис → порядок запуска в init.rc |
| Verified Boot блокирует кастомную прошивку | Цепочка доверия AVB, boot states, vbmeta |
| BOOT_COMPLETED приходит поздно | Весь pipeline: Zygote → SystemServer → Home → broadcast |
| OTA-обновление ломает загрузку | A/B partitions, rollback, dm-verity |

---

## Полная цепочка загрузки

Ниже — мастер-диаграмма всего процесса загрузки Android от нажатия кнопки питания до появления домашнего экрана:

```
 НАЖАТИЕ КНОПКИ ПИТАНИЯ
          |
          v
 +------------------+
 |    Boot ROM       |  Аппаратный код в SoC (read-only)
 |  (PBL / BROM)     |  Загружает первичный загрузчик из flash
 +--------+---------+
          |
          v
 +------------------+
 |  Primary          |  SBL1 / SPL — минимальная инициализация
 |  Bootloader       |  DRAM init, security setup
 +--------+---------+
          |
          v
 +------------------+
 |  Secondary        |  ABL (Android Bootloader) / U-Boot / LK
 |  Bootloader       |  Verified Boot (AVB), A/B slot selection
 |                   |  Загрузка kernel + ramdisk
 +--------+---------+
          |
          |  Проверка подписей (chain of trust)
          |  vbmeta → boot → system → vendor
          v
 +------------------+
 |  Linux Kernel     |  Распаковка, device tree, driver probing
 |                   |  Android-патчи: binder, ashmem, wakelocks
 |                   |  Монтирование rootfs
 +--------+---------+
          |
          |  Запуск PID 1
          v
 +------------------+
 |  init (PID 1)     |  Парсинг init.rc
 |                   |  Монтирование /system, /vendor, /data
 |                   |  SELinux init, property service
 |                   |  Запуск демонов
 +--------+---------+
          |
          +----------> servicemanager (Binder context manager)
          |            logd, healthd, lmkd, vold ...
          |
          v
 +------------------+
 |  Zygote            |  app_process64 → AndroidRuntime
 |  (app_process)     |  ZygoteInit.main()
 |                    |  Preload: 8000+ классов, ресурсы, SO
 |                    |  Открытие Zygote socket
 +--------+---------+
          |
          |  fork() — первый дочерний процесс
          v
 +------------------+
 |  System Server     |  SystemServer.main() → run()
 |                    |  startBootstrapServices()
 |                    |  startCoreServices()
 |                    |  startOtherServices()
 |                    |  ~100 системных сервисов
 +--------+---------+
          |
          |  AMS.systemReady()
          v
 +------------------+
 |  Home / Launcher   |  Intent: ACTION_MAIN + CATEGORY_HOME
 |                    |  Fork из Zygote (как обычное приложение)
 |                    |  Boot animation останавливается
 +--------+---------+
          |
          v
  ACTION_BOOT_COMPLETED broadcast
  (все приложения с BroadcastReceiver получают)
```

**Временные рамки типичной загрузки (flagship 2024-2025):**

```
 Фаза                    | Время (мс) | Накопленное
 -------------------------+------------+-----------
 Boot ROM + PBL           |    50-200  |      200
 Primary Bootloader (SBL) |   200-500  |      700
 Secondary Bootloader     |   500-2000 |     2700
 Kernel boot              |  1000-3000 |     5700
 init (до Zygote start)   |  2000-5000 |    10700
 Zygote preload           |  3000-8000 |    18700
 SystemServer bootstrap   |  2000-5000 |    23700
 Home ready               |  1000-3000 |    26700
 BOOT_COMPLETED           |  3000-8000 |    34700
```

---

## Bootloader

### Boot ROM (Primary Boot Loader / PBL)

Boot ROM — это самый первый код, который выполняется при подаче питания на SoC. Он «зашит» в масочное ПЗУ кристалла на этапе производства и не может быть изменён.

**Задачи Boot ROM:**
1. Инициализация минимального набора hardware: CPU clock, internal SRAM
2. Определение источника загрузки (eMMC, UFS, SD-карта, USB)
3. Загрузка Primary Bootloader (SBL1 / SPL) во внутреннюю SRAM
4. Проверка цифровой подписи SBL1 (аппаратный root of trust)
5. Передача управления SBL1

```
 +------------------------------------------+
 |             SoC (System on Chip)          |
 |                                          |
 |  +------------+      +--------------+    |
 |  |  Boot ROM  |----->|  Internal    |    |
 |  |  (Mask ROM)|      |  SRAM        |    |
 |  |  ~64-256KB |      |  ~256KB-1MB  |    |
 |  +-----+------+      +------+-------+    |
 |        |                     |            |
 |        | read                | execute    |
 |        v                     v            |
 |  +------------+      +--------------+    |
 |  |  Flash     |      |  SBL1 / SPL  |    |
 |  |  (eMMC/UFS)|      |  (signed)    |    |
 |  +------------+      +--------------+    |
 +------------------------------------------+
```

**Аппаратный Root of Trust:**
- OEM-ключ прошивается в eFuse (one-time programmable)
- Boot ROM проверяет подпись SBL1 с помощью этого ключа
- Если проверка не прошла — загрузка останавливается (brick)
- Этот механизм — начало всей цепочки доверия (chain of trust)

### Primary Bootloader (SBL / SPL)

Primary Bootloader (SBL1 на Qualcomm, SPL на MediaTek/Samsung) выполняется во внутренней SRAM, пока внешняя память (DRAM) ещё не инициализирована.

**Задачи:**
1. Инициализация DRAM-контроллера и калибровка тактов
2. Инициализация базовых периферийных устройств
3. Настройка Trust Zone (TrustZone / TEE)
4. Загрузка вторичного загрузчика (ABL) в DRAM
5. Проверка подписи ABL
6. Передача управления ABL

### Secondary Bootloader (ABL / U-Boot / LK)

Вторичный загрузчик — это уже полноценная программа, работающая в DRAM. На большинстве современных Android-устройств используется ABL (Android Bootloader) на базе UEFI (Qualcomm) или LK (Little Kernel) на MediaTek.

**Задачи ABL:**
1. Отображение splash screen (логотип OEM)
2. Выбор A/B слота для загрузки
3. **Android Verified Boot (AVB)** — проверка всех образов
4. Загрузка kernel (boot.img / init_boot.img) и ramdisk
5. Подготовка kernel cmdline
6. Передача управления ядру

```
 Secondary Bootloader (ABL)
 +-------------------------------------------------+
 |                                                 |
 |  1. Splash screen                               |
 |  2. Проверка A/B слота                          |
 |     +-------------------+  +------------------+ |
 |     |  Slot A (active)  |  |  Slot B (backup) | |
 |     |  boot_a           |  |  boot_b          | |
 |     |  system_a         |  |  system_b        | |
 |     |  vendor_a         |  |  vendor_b        | |
 |     +-------------------+  +------------------+ |
 |                                                 |
 |  3. AVB: verify vbmeta → boot → system → vendor|
 |  4. Загрузка boot.img в RAM                     |
 |     +------+--------+---------+                 |
 |     |header| kernel | ramdisk |                 |
 |     +------+--------+---------+                 |
 |  5. Передача управления kernel                  |
 +-------------------------------------------------+
```

### Android Verified Boot (AVB) — Цепочка доверия

Android Verified Boot 2.0 (AVB) — механизм верификации целостности всех загружаемых образов. Он гарантирует, что на устройстве запущен именно тот код, который был подписан OEM.

**Принцип работы:**

```
 ЦЕПОЧКА ДОВЕРИЯ AVB (Chain of Trust)

 +------------------+
 |  Hardware Root   |  eFuse OEM key (неизменяемый)
 |  of Trust        |
 +--------+---------+
          |
          | проверяет подпись
          v
 +------------------+
 |  Boot ROM        |  Проверяет SBL1
 +--------+---------+
          |
          | проверяет подпись
          v
 +------------------+
 |  SBL1 / SPL      |  Проверяет ABL
 +--------+---------+
          |
          | проверяет подпись
          v
 +------------------+
 |  ABL              |  Проверяет vbmeta
 +--------+---------+
          |
          | AVB 2.0
          v
 +------------------+
 |  vbmeta           |  Подписанная метаинформация
 |                   |  Содержит хеши и hash trees
 +--------+---------+
          |
          +--------+----------+---------+
          |        |          |         |
          v        v          v         v
       boot.img  system   vendor    dtbo
       (HASH)    (HASHTREE)(HASHTREE)(HASH)
                 dm-verity  dm-verity
```

**Типы дескрипторов в vbmeta:**

| Тип | Описание | Применение |
|---|---|---|
| HASH | Прямой хеш всего раздела | boot, dtbo (маленькие разделы) |
| HASHTREE | Дерево хешей (Merkle tree) | system, vendor (большие разделы) |
| CHAIN | Ссылка на дочерний vbmeta | Делегирование проверки (vendor vbmeta) |

**dm-verity** — модуль ядра Linux (Device Mapper), который проверяет целостность блоков при чтении:

```
 dm-verity: Merkle Hash Tree

 Уровень 0 (root hash — в vbmeta):
                    [Root Hash]
                   /           \
 Уровень 1:     [H01]         [H23]
               /     \       /     \
 Уровень 2: [H0]   [H1]  [H2]   [H3]
             |       |     |       |
 Данные:   [Блок0][Блок1][Блок2][Блок3]

 При чтении Блок1:
 1. Вычислить SHA-256(Блок1)
 2. Сравнить с H1
 3. Вычислить SHA-256(H0 + H1)
 4. Сравнить с H01
 5. Вычислить SHA-256(H01 + H23)
 6. Сравнить с Root Hash
 → Если не совпало — I/O ошибка (EIO)
```

### Состояния загрузки (Boot States)

AVB определяет четыре состояния загрузки:

| Состояние | Цвет | Bootloader | Верификация | Описание |
|---|---|---|---|---|
| Verified | Зелёный | Locked | OEM-ключ | Стандартное заводское состояние |
| Custom | Жёлтый | Locked | Кастомный ключ | OEM разрешил кастомные ключи |
| Unlocked | Оранжевый | Unlocked | Отключена | Разблокированный (разработка) |
| Failed | Красный | Locked | Ошибка | Не прошла проверка → не грузится |

**Что происходит при каждом состоянии:**

```
 Зелёный (LOCKED + OEM key):
   Boot ROM → SBL → ABL → vbmeta (OEM key) → boot → system
   Всё подписано OEM. Стандартная загрузка.

 Жёлтый (LOCKED + custom key):
   Boot ROM → SBL → ABL → vbmeta (custom key) → boot → system
   Предупреждение на экране 10 сек. Key fingerprint показан.

 Оранжевый (UNLOCKED):
   Boot ROM → SBL → ABL → [skip verification] → boot → system
   Предупреждение на экране 5 сек.
   Attestation key стёрт из TEE.
   Wiped userdata (factory reset при unlock).

 Красный (FAILED):
   Boot ROM → SBL → ABL → vbmeta (FAIL!)
   Загрузка остановлена. Устройство не грузится.
```

### A/B (Seamless) Updates

Начиная с Android 7.0, устройства могут использовать схему A/B обновлений:

```
 Разметка flash-памяти с A/B:

 +----------+----------+----------+
 |  boot_a  |  boot_b  | vbmeta_a |
 +----------+----------+----------+
 | system_a | system_b | vbmeta_b |
 +----------+----------+----------+
 | vendor_a | vendor_b | userdata |
 +----------+----------+----------+
 | dtbo_a   | dtbo_b   | misc     |
 +----------+----------+----------+

 Процесс OTA-обновления:

 Текущий слот: A (active)
 1. Скачивание OTA в фоне
 2. Запись в слот B (неактивный) — без прерывания работы
 3. AVB-верификация слота B
 4. Переключение active slot → B
 5. Перезагрузка → загрузка из слота B
 6. Если загрузка неудачна → rollback на слот A

 Преимущества:
 - Нет downtime при обновлении
 - Мгновенный rollback при неудаче
 - Нет recovery partition (A/B заменяет)
```

### Virtual A/B (Android 11+)

Для устройств с ограниченным flash-хранилищем Android 11 ввёл Virtual A/B — только boot имеет два слота, а system/vendor используют copy-on-write (snapshots):

```
 Virtual A/B:

 +----------+----------+
 |  boot_a  |  boot_b  |   ← реальные A/B слоты
 +----------+----------+
 | system   | (COW     |   ← один физический раздел
 | (base)   |  snapshot)|  + COW-снэпшот для обновления
 +----------+----------+
 | vendor   | (COW     |
 | (base)   |  snapshot)|
 +----------+----------+

 При OTA:
 1. Записать изменения в COW snapshot
 2. При загрузке — merge snapshot → base
 3. Если merge не удался — отменить snapshot
```

---

## Linux Kernel Boot

После того как bootloader загрузил образ ядра и ramdisk в оперативную память и передал управление, начинается загрузка Linux kernel.

### Последовательность загрузки ядра

```
 ЗАГРУЗКА LINUX KERNEL

 +--------------------------------------------------+
 |  1. Распаковка ядра (gzip/lz4)                   |
 |     Kernel image: ~15-30 MB (сжатый ~8-15 MB)    |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  2. Ранняя инициализация (head.S / head.o)       |
 |     - Настройка MMU (Memory Management Unit)      |
 |     - Настройка таблиц страниц (page tables)      |
 |     - Включение кэша                              |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  3. start_kernel() — основная функция init        |
 |     - setup_arch(): архитектурно-зависимая init    |
 |     - mm_init(): инициализация памяти              |
 |     - sched_init(): планировщик                    |
 |     - console_init(): ранний вывод                 |
 |     - rest_init(): создание kernel threads         |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  4. Device Tree Blob (DTB) разбор                 |
 |     - Описание hardware для ядра                   |
 |     - Какие устройства есть, их адреса, IRQ        |
 |     - Overlay DTB для vendor-специфичного hw       |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  5. Driver probing                                |
 |     - Platform drivers                             |
 |     - Android-специфичные:                         |
 |       * Binder driver  (/dev/binder, /dev/hwbinder)|
 |       * Ashmem (anonymous shared memory)            |
 |       * ION / DMA-BUF heap allocator                |
 |       * Wakelocks (power management)                |
 |       * Low Memory Killer driver (lmk)              |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  6. Монтирование initramfs (ramdisk)              |
 |     - Generic ramdisk (GKI) + vendor ramdisk       |
 |     - Содержит init binary и init.rc               |
 +--------------------------------------------------+
           |
           v
 +--------------------------------------------------+
 |  7. Запуск /init (PID 1)                          |
 |     kernel_init() → run_init_process("/init")      |
 +--------------------------------------------------+
```

### Android-специфичные компоненты ядра

Android использует модифицированное ядро Linux с набором расширений. Начиная с Android 12, Google продвигает GKI (Generic Kernel Image) — унифицированное ядро с отделёнными vendor-модулями.

| Компонент | Описание | Файл в ядре |
|---|---|---|
| Binder | IPC-механизм Android | drivers/android/binder.c |
| HW Binder | Binder для HAL (Treble) | drivers/android/binder.c (отдельный контекст) |
| VND Binder | Binder для vendor-процессов | drivers/android/binder.c |
| Ashmem | Anonymous Shared Memory | drivers/staging/android/ashmem.c (→ memfd в новых) |
| ION → DMA-BUF | Аллокатор для multimedia buffers | drivers/staging/android/ion/ (deprecated → dma-buf heaps) |
| Wakelocks | Управление suspend/wakeup | kernel/power/wakelock.c |
| Low Memory Killer | Убийство процессов при нехватке RAM | drivers/staging/android/lowmemorykiller.c (→ lmkd userspace) |

### Generic Kernel Image (GKI) — Android 12+

GKI — ключевая инициатива Google по борьбе с фрагментацией ядра. До GKI каждый OEM и SoC-вендор поддерживал свой fork ядра, что приводило к задержкам обновлений безопасности.

```
 АРХИТЕКТУРА GKI

 До GKI (Android < 12):
 +------------------------------------------+
 |  OEM Kernel (форк от SoC-вендора)        |
 |  = Linux kernel                          |
 |  + Android patches                       |
 |  + SoC vendor patches (Qualcomm/MTK/...) |
 |  + OEM device-specific patches           |
 |  Всё слито в один монолит                |
 +------------------------------------------+

 С GKI (Android 12+):
 +------------------------------------------+
 |  GKI Kernel (Google)                     |
 |  = ACK (Android Common Kernel)           |
 |  + Android patches                       |
 |  + Стабильный KMI (Kernel Module Iface)  |
 +----+-------------------------------------+
      |
      | KMI (стабильный интерфейс)
      v
 +------------------------------------------+
 |  Vendor Modules (loadable .ko)           |
 |  - SoC-специфичные драйверы              |
 |  - OEM-специфичные драйверы              |
 |  - Загружаются при boot из vendor_boot   |
 +------------------------------------------+

 Преимущества:
 - Google обновляет ядро независимо от OEM
 - Vendor модули стабильны между версиями ядра
 - Быстрее security patches
 - Меньше фрагментация
```

### Образы загрузки в GKI

```
 Android 12 (GKI):
 +-----------+     +----------------+
 | boot.img  |     | vendor_boot.img|
 |           |     |                |
 | GKI kernel|     | vendor ramdisk |
 | generic   |     | vendor dtb     |
 | ramdisk   |     | vendor modules |
 +-----------+     +----------------+

 Android 13+ (GKI):
 +------------+  +----------+  +----------------+
 | boot.img   |  |init_boot |  | vendor_boot.img|
 |            |  |          |  |                |
 | GKI kernel |  | generic  |  | vendor ramdisk |
 | (no ramdsk)|  | ramdisk  |  | vendor dtb     |
 +------------+  +----------+  +----------------+

 При загрузке bootloader конкатенирует:
 [vendor ramdisk] + [generic ramdisk] → initramfs
 Generic оверлеит vendor (приоритет generic)
```

---

## init Process (PID 1)

### Обзор

Android использует **собственную реализацию init** — это НЕ systemd, НЕ sysvinit, НЕ busybox init. Android init — уникальная программа, специально написанная для Android, с собственным языком конфигурации (`.rc`-файлы).

Исходный код: `system/core/init/` в AOSP.

```
 init (PID 1) — Android's custom init

 +----------------------------------------------------+
 |  НЕ systemd  |  НЕ sysvinit  |  НЕ OpenRC         |
 +----------------------------------------------------+
 |  Собственная реализация Google                      |
 |  Язык конфигурации: .rc-файлы                       |
 |  Property system вместо environment variables       |
 |  SELinux enforcement                                |
 |  Watchdog для критичных сервисов                    |
 +----------------------------------------------------+
```

### First-Stage Init vs Second-Stage Init (Android 10+)

Начиная с Android 10, init разделён на две стадии:

```
 ДВУХСТАДИЙНАЯ ЗАГРУЗКА INIT

 +---------------------------------------------+
 |  First-stage init (из ramdisk)              |
 |                                             |
 |  1. Монтирование /dev, /proc, /sys          |
 |  2. Загрузка SELinux policy                  |
 |  3. Монтирование /system, /vendor, /product |
 |     (используя fstab из DTB или ramdisk)    |
 |  4. switch_root → /system                    |
 |  5. exec /system/bin/init (second stage)     |
 +---------------------+-----------------------+
                        |
                        v
 +---------------------------------------------+
 |  Second-stage init (из /system)             |
 |                                             |
 |  1. Property service start                   |
 |  2. Парсинг init.rc и всех импортированных  |
 |     .rc-файлов                               |
 |  3. Выполнение trigger early-init            |
 |  4. Выполнение trigger init                  |
 |  5. Выполнение trigger late-init             |
 |  6. Запуск сервисов (servicemanager,         |
 |     surfaceflinger, zygote, etc.)            |
 |  7. Property-triggered actions               |
 |  8. Обработка сигналов (SIGCHLD)             |
 |  9. Перезапуск crashed сервисов              |
 +---------------------------------------------+
```

### Язык init.rc

init.rc — это декларативный файл конфигурации с тремя основными конструкциями:

**1. Actions (on-блоки):**
```
on early-init
    # Выполняется в начале загрузки
    mount tmpfs tmpfs /dev mode=0755

on init
    # Основная инициализация
    mkdir /dev/stune 0755 system system
    start servicemanager
    start hwservicemanager

on late-init
    # Запуск основных сервисов
    trigger zygote-start

on property:sys.boot_completed=1
    # Действие при установке property
    write /dev/kmsg "Boot completed"
```

**2. Services:**
```
service servicemanager /system/bin/servicemanager
    class core animation
    user system
    group system readproc
    critical
    onrestart restart healthd
    onrestart restart zygote
    onrestart restart audioserver

service zygote /system/bin/app_process64 \
    -Xzygote /system/bin \
    --zygote --start-system-server \
    --socket-name=zygote
    class main
    priority -20
    user root
    group root readproc reserved_disk
    socket zygote stream 660 root system
    socket usap_pool_primary stream 660 root system
    onrestart exec_background_no_selog -- /system/bin/vdc volume abort_fuse
    onrestart write /sys/power/state on
    onrestart restart audioserver
    onrestart restart cameraserver
    onrestart restart media
    onrestart restart netd
    onrestart restart wificond
```

**3. Imports:**
```
import /system/etc/init/hw/init.${ro.hardware}.rc
import /vendor/etc/init/hw/init.${ro.hardware}.rc
import /system/etc/init/*.rc
import /vendor/etc/init/*.rc
import /odm/etc/init/*.rc
```

### Полная последовательность парсинга init.rc

```
 ПАРСИНГ И ВЫПОЛНЕНИЕ INIT.RC

 init (PID 1)
   |
   +-- 1. Парсинг /system/etc/init/hw/init.rc (главный файл)
   |       |
   |       +-- import /system/etc/init/hw/init.${ro.hardware}.rc
   |       +-- import /vendor/etc/init/hw/init.${ro.hardware}.rc
   |       +-- import /system/etc/init/*.rc
   |       +-- import /vendor/etc/init/*.rc
   |       +-- import /odm/etc/init/*.rc
   |       +-- import /product/etc/init/*.rc
   |
   +-- 2. Построение списка actions и services
   |
   +-- 3. Выполнение triggers в порядке:
   |       |
   |       +-- early-init
   |       |   - Минимальные операции
   |       |   - Установка cgroups
   |       |   - start ueventd
   |       |
   |       +-- init
   |       |   - Монтирование файловых систем
   |       |   - Настройка cgroups
   |       |   - Создание директорий
   |       |   - start logd
   |       |   - start servicemanager
   |       |   - start hwservicemanager
   |       |
   |       +-- late-init
   |       |   - trigger post-fs
   |       |   - trigger post-fs-data
   |       |   - trigger zygote-start
   |       |   - trigger boot
   |       |
   |       +-- boot
   |           - Настройка сети
   |           - Установка permissions
   |           - start сервисов class main
   |
   +-- 4. Event loop: property triggers + SIGCHLD
```

### Property System

Property system — Android-специфичный механизм глобальных key-value настроек, доступных всем процессам через shared memory:

| Префикс | Описание | Пример |
|---|---|---|
| `ro.*` | Read-only, устанавливается при загрузке | `ro.build.version.sdk=34` |
| `persist.*` | Сохраняется между перезагрузками | `persist.sys.timezone=Europe/Moscow` |
| `sys.*` | Системные runtime-свойства | `sys.boot_completed=1` |
| `init.svc.*` | Состояние init-сервисов | `init.svc.zygote=running` |
| `ctl.*` | Управление сервисами | `ctl.start=zygote` |
| `gsm.*` | Телефония | `gsm.sim.state=READY` |
| `dalvik.*` | ART / Dalvik VM | `dalvik.vm.heapsize=512m` |
| `debug.*` | Отладочные | `debug.atrace.tags.enableflags=0` |

**Как работает property system:**

```
 PROPERTY SYSTEM

 +------------------+    +-------------------+
 |  init (PID 1)    |    |  Property файлы   |
 |  property_service|<---|  /default.prop     |
 |                  |    |  /system/build.prop|
 |                  |    |  /vendor/build.prop|
 +--------+---------+    +-------------------+
          |
          | mmap (shared memory)
          v
 +---------------------------+
 |  /dev/__properties__      |
 |  (shared memory region)   |
 |  Доступно всем процессам  |
 |  (read-only для большинст)|
 +---------------------------+
    |         |         |
    v         v         v
 [App1]   [App2]   [System Server]
 getprop   getprop   setprop/getprop
```

### SELinux в init

Init отвечает за первичную загрузку SELinux policy:

1. **First-stage init** загружает monolithic SELinux policy
2. Устанавливает enforcing mode (`ro.boot.selinux=enforcing`)
3. Каждый сервис в init.rc имеет SELinux контекст:
   ```
   service zygote ...
       seclabel u:r:zygote:s0
   ```
4. Переход контекста при exec: init (u:r:init:s0) → zygote (u:r:zygote:s0)

---

## servicemanager

### Роль servicemanager

servicemanager — это native-демон, который является **центральным реестром всех Binder-сервисов**. Он должен запуститься раньше всех остальных сервисов, использующих Binder IPC.

```
 servicemanager: РЕЕСТР BINDER-СЕРВИСОВ

 +---------------------------------------------------+
 |  servicemanager (PID ~2-5)                        |
 |                                                   |
 |  1. Открывает /dev/binder                         |
 |  2. Вызывает ioctl(BINDER_SET_CONTEXT_MANAGER)    |
 |     → становится handle 0 (context manager)       |
 |  3. Входит в binder loop (ожидание запросов)       |
 |                                                   |
 |  API:                                             |
 |  - addService(name, IBinder) — регистрация         |
 |  - getService(name) → IBinder — поиск              |
 |  - listServices() → список имён                    |
 |  - checkService(name) → IBinder (non-blocking)     |
 +---------------------------------------------------+

 Три варианта servicemanager:
 +------------------+-------------------+------------------+
 | servicemanager   | hwservicemanager  | vndservicemanager|
 | /dev/binder      | /dev/hwbinder     | /dev/vndbinder   |
 | Framework svcs   | HAL services      | Vendor services  |
 | Java + Native    | HIDL / AIDL HAL   | Vendor-to-vendor |
 +------------------+-------------------+------------------+
```

### Почему Zygote использует Socket, а не Binder

Это один из ключевых архитектурных вопросов Android, часто задаваемый на собеседованиях:

```
 ПОЧЕМУ ZYGOTE ИСПОЛЬЗУЕТ UNIX SOCKET, А НЕ BINDER?

 Проблема с Binder + fork():
 +-------------------------------------------------+
 |  Binder thread pool использует multi-threaded    |
 |  модель. При fork() дочерний процесс наследует   |
 |  file descriptors, но НЕ threads.                |
 |                                                   |
 |  Родитель (Zygote):                               |
 |  - Binder driver fd = открыт                      |
 |  - Binder thread 1 = работает                     |
 |  - Binder thread 2 = работает                     |
 |  - Lock held by thread 2                          |
 |                                                   |
 |  После fork() в дочернем:                         |
 |  - Binder driver fd = скопирован                  |
 |  - Thread 1 = НЕ СУЩЕСТВУЕТ                      |
 |  - Thread 2 = НЕ СУЩЕСТВУЕТ                      |
 |  - Lock held by thread 2 = НАВСЕГДА ЗАБЛОКИРОВАН |
 |                                                   |
 |  Результат: DEADLOCK в дочернем процессе          |
 +-------------------------------------------------+

 Решение: Zygote НЕ использует Binder до fork().
 Вместо этого:
 - UNIX domain socket для получения fork-запросов
 - После fork() дочерний процесс СНАЧАЛА открывает
   свой собственный /dev/binder (ZygoteInit.zygoteInit())
 - Только потом начинает использовать Binder IPC
```

Подробнее о Binder — см. [[android-binder-ipc]].

---

## Zygote (app_process)

### Что такое Zygote

Zygote (от греч. «зигота» — оплодотворённая клетка) — это процесс-шаблон, от которого fork'аются **все** Java/Kotlin-процессы в Android: System Server, все приложения, все background-сервисы.

Бинарный файл: `/system/bin/app_process64` (или `app_process32`).

### Запуск Zygote

```
 ЗАПУСК ZYGOTE: ОТ INIT.RC ДО ZYGOTEINIT.MAIN()

 init.rc:
   service zygote /system/bin/app_process64 ...
     |
     v
 app_process64 (native binary)
   |
   +-- main() в app_main.cpp
   |   |
   |   +-- runtime.start("com.android.internal.os.ZygoteInit", ...)
   |       |
   |       v
   |   AndroidRuntime::start()
   |       |
   |       +-- 1. startVm()
   |       |       Создание ART VM (dalvik VM instance)
   |       |       - Настройка heap size (-Xmx)
   |       |       - Настройка GC параметров
   |       |       - JIT compilation настройки
   |       |       - Загрузка libart.so
   |       |
   |       +-- 2. startReg()
   |       |       Регистрация JNI-методов
   |       |       - ~100+ JNI-функций: android.os.Binder,
   |       |         android.util.Log, android.content.res, ...
   |       |
   |       +-- 3. CallStaticVoidMethod("ZygoteInit", "main")
   |               Вызов ZygoteInit.main() через JNI
   |
   v
 ZygoteInit.main() [Java-код]
   |
   +-- 1. Zygote.createBlastulaPool()  (Android 10+: USAP pool)
   |
   +-- 2. preloadClasses()
   |       Загрузка ~8000+ framework-классов
   |
   +-- 3. preloadResources()
   |       Загрузка framework-ресурсов (drawables, layouts, colors)
   |
   +-- 4. preloadSharedLibraries()
   |       Загрузка native-библиотек (libandroid_runtime.so, etc.)
   |
   +-- 5. gcAndFinalize()
   |       GC для минимизации dirty pages перед fork
   |
   +-- 6. Zygote.forkSystemServer()
   |       fork() первого дочернего процесса → SystemServer
   |
   +-- 7. zygoteServer.runSelectLoop()
           Бесконечный цикл ожидания fork-запросов
           на Zygote socket
```

### preloadClasses() — Детали

Файл со списком классов для предзагрузки: `/system/etc/preloaded-classes`

```
 PRELOAD CLASSES

 Файл: frameworks/base/boot/preloaded-classes
 Содержит ~8000+ полных имён классов:

 android.app.Activity
 android.app.ActivityManager
 android.app.ActivityThread
 android.app.Application
 android.app.Dialog
 android.app.Fragment
 android.app.Service
 android.content.ContentProvider
 android.content.ContentResolver
 android.content.Context
 android.content.Intent
 android.content.res.Resources
 android.database.sqlite.SQLiteDatabase
 android.graphics.Bitmap
 android.graphics.Canvas
 android.graphics.Paint
 android.graphics.drawable.Drawable
 android.net.Uri
 android.os.Bundle
 android.os.Handler
 android.os.Looper
 android.os.Message
 android.os.Parcel
 android.text.TextUtils
 android.util.ArrayMap
 android.util.Log
 android.view.View
 android.view.ViewGroup
 android.widget.TextView
 android.widget.LinearLayout
 ... (~8000+ классов)

 Зачем:
 - Классы загружаются ОДИН РАЗ в Zygote
 - При fork() → Copy-on-Write → shared memory
 - Каждое приложение экономит ~50-100 MB RAM
 - Каждое приложение экономит ~1-3 сек startup time
```

### preloadResources()

```
 PRELOAD RESOURCES

 ZygoteInit.preloadResources():
 +-------------------------------------------+
 |  Framework resources (предзагружаются):   |
 |                                           |
 |  Drawables:                               |
 |  - System icons                            |
 |  - Default backgrounds                     |
 |  - Widget drawables                        |
 |                                           |
 |  Colors:                                  |
 |  - Theme colors                            |
 |  - System palette                          |
 |                                           |
 |  Layouts:                                 |
 |  - System dialog layouts                   |
 |  - Toast layout                            |
 |  - Notification layouts                    |
 |                                           |
 |  Результат: Resources кэшированы в памяти |
 |  Fork → COW → shared между процессами     |
 +-------------------------------------------+
```

### preloadSharedLibraries()

```
 PRELOAD SHARED LIBRARIES

 ZygoteInit.preloadSharedLibraries():
 +-------------------------------------------+
 |  Библиотеки:                              |
 |  - libandroid_runtime.so                   |
 |  - libcompiler_rt.so                       |
 |  - libandroid.so                           |
 |  - libjnigraphics.so                       |
 |  - libmedia_jni.so                         |
 |  - libwebviewchromium_loader.so            |
 |                                           |
 |  dlopen() в Zygote → mmap() → shared pages|
 |  После fork() → COW → все SO shared       |
 +-------------------------------------------+
```

### Механизм fork() и Copy-on-Write

Ключевой принцип, который делает Zygote эффективным:

```
 FORK + COPY-ON-WRITE (COW)

 ДО FORK:
 +---------------------------------------------------+
 |  Zygote процесс (RAM: ~180 MB)                   |
 |                                                   |
 |  [ART VM] [8000+ классов] [Resources] [SO libs]   |
 |  Все страницы памяти: READ-WRITE                   |
 +---------------------------------------------------+

 СРАЗУ ПОСЛЕ FORK:
 +---------------------------------------------------+
 |  Zygote (родитель)        | App (дочерний)        |
 |                           |                       |
 |  [ART VM]                 | [ART VM]              |
 |  [8000+ классов]          | [8000+ классов]       |
 |  [Resources]              | [Resources]           |
 |  [SO libs]                | [SO libs]             |
 |                           |                       |
 |  Указывают на ОДНИ И ТЕ ЖЕ физические страницы    |
 |  Все страницы: READ-ONLY (COW protection)          |
 +---------------------------------------------------+
 Физическая RAM: всё ещё ~180 MB (не 360 MB!)

 ПОСЛЕ РАБОТЫ APP:
 +---------------------------------------------------+
 |  Zygote                   | App                   |
 |                           |                       |
 |  [ART VM]  ─shared──────>| [ART VM]              |
 |  [8000+ кл] ─shared─────>| [8000+ кл]            |
 |  [Resources] ─shared────>| [Resources]           |
 |  [SO libs]  ─shared─────>| [SO libs]             |
 |                           |                       |
 |                           | [App code]  ← PRIVATE |
 |                           | [App heap]  ← PRIVATE |
 |                           | [App stack] ← PRIVATE |
 +---------------------------------------------------+
 Физическая RAM: ~180 MB (shared) + ~30-100 MB (private)
 Вместо: ~180 + 180 = 360 MB без COW
```

**Экономия при 50 приложениях:**
- Без Zygote + COW: 50 x 180 MB = 9 000 MB
- С Zygote + COW: 180 MB (shared) + 50 x 50 MB (private) = 2 680 MB
- Экономия: ~6 320 MB (70%!)

### 32-bit и 64-bit Zygote

На 64-bit устройствах запускаются два процесса Zygote:

```
 ДВОЙНОЙ ZYGOTE

 init.rc:
 +------------------+     +------------------+
 | service zygote   |     | service zygote   |
 | app_process64    |     | _secondary       |
 | --zygote         |     | app_process32    |
 | --start-system-  |     | --zygote         |
 |   server         |     | --socket-name=   |
 | socket zygote    |     |   zygote_secondary|
 +--------+---------+     +--------+---------+
          |                        |
          v                        v
 +------------------+     +------------------+
 | Zygote64 (primary)|    | Zygote32 (second)|
 | PID ~200          |    | PID ~201          |
 |                   |    |                   |
 | Forks:            |    | Forks:            |
 | - SystemServer    |    | - 32-bit apps    |
 | - 64-bit apps     |    | - 32-bit libs    |
 | socket: zygote    |    | socket: zygote   |
 |                   |    |   _secondary      |
 +------------------+     +------------------+

 AMS решает какой Zygote использовать
 на основе abi primaryCpuAbi в AndroidManifest:
 - arm64-v8a → zygote64
 - armeabi-v7a → zygote32
```

### WebViewZygote (Android 8.0+)

Для безопасности WebView-рендеринг изолирован в отдельный процесс, forked из специального WebViewZygote:

```
 WEBVIEW ZYGOTE

 +------------------+
 |  Zygote (primary)|
 +--------+---------+
          |
          | fork()
          v
 +------------------+
 | WebViewZygote    |  Предзагружает:
 |                  |  - WebView native libs
 |                  |  - Chromium renderer
 |                  |  - GPU process setup
 +--------+---------+
          |
          | fork() (при первом WebView в app)
          v
 +------------------+
 | WebView render   |  Sandboxed процесс
 | process          |  Минимальные permissions
 |                  |  isolatedProcess=true
 +------------------+
```

### USAP Pool (Unspecialized App Process) — Android 10+

Для ускорения холодного старта Android 10 ввёл пул предсозданных процессов:

```
 USAP POOL (Android 10+)

 +------------------+
 |  Zygote          |
 +--------+---------+
          |
          | pre-fork() (заранее, до запроса)
          |
          +------+------+------+
          |      |      |      |
          v      v      v      v
        [USAP] [USAP] [USAP] [USAP]
        (idle)  (idle) (idle) (idle)
          |
          | Запрос от AMS: "запусти com.example.app"
          v
        [USAP] → specialize() → [com.example.app]
        (used)   - Установка UID/GID
                 - Загрузка APK
                 - Вызов Application.onCreate()

 Без USAP: fork() + specialize = ~100-200 ms
 С USAP:   specialize only     = ~20-50 ms
 Выигрыш: ~80-150 ms на каждый cold start
```

---

## System Server

### Обзор

System Server — **самый важный процесс в Android** после ядра. Это первый процесс, forked из Zygote, и он содержит все основные системные сервисы фреймворка.

Если System Server крашится — Zygote перезапускается (init.rc: `onrestart restart zygote`), что приводит к перезапуску ВСЕХ приложений (мягкая перезагрузка).

### Запуск System Server

```
 ЗАПУСК SYSTEM SERVER

 ZygoteInit.main()
   |
   +-- forkSystemServer()
   |     |
   |     +-- Zygote.forkSystemServer(uid=1000, gid=1000,
   |     |       gids=[...], runtimeFlags, ...)
   |     |     |
   |     |     +-- nativeForkSystemServer() [JNI → fork()]
   |     |           |
   |     |           +-- [Дочерний] pid == 0 → handleSystemServerProcess()
   |     |           +-- [Родитель] pid > 0 → continue (Zygote loop)
   |     |
   |     +-- handleSystemServerProcess()
   |           |
   |           +-- createPathClassLoader() — для загрузки system JARs
   |           +-- ZygoteInit.zygoteInit()
   |                 |
   |                 +-- RuntimeInit.commonInit()
   |                 |     Установка Thread.UncaughtExceptionHandler
   |                 |
   |                 +-- ZygoteInit.nativeZygoteInit()
   |                 |     Запуск Binder thread pool
   |                 |     (Теперь SystemServer может использовать Binder)
   |                 |
   |                 +-- RuntimeInit.applicationInit()
   |                       |
   |                       +-- invokeStaticMain("SystemServer", ...)
   |                             |
   |                             +-- throw MethodAndArgsCaller
   |                                   (хак для очистки stack frame)
   |
   v
 SystemServer.main()
   |
   +-- new SystemServer().run()
```

### SystemServer.run() — Три фазы запуска

```
 SYSTEMSERVER.RUN() — ТРИ ФАЗЫ

 SystemServer.run()
   |
   +-- 1. Подготовка окружения
   |       - Looper.prepareMainLooper()
   |       - System.loadLibrary("android_servers")
   |       - createSystemContext() → ActivityThread для SystemServer
   |
   +-- 2. startBootstrapServices()      ← ФАЗА 1
   |       Критичные сервисы, от которых зависят все остальные
   |       (порядок ИМЕЕТ ЗНАЧЕНИЕ!)
   |
   +-- 3. startCoreServices()           ← ФАЗА 2
   |       Важные сервисы, но без жёстких зависимостей
   |
   +-- 4. startOtherServices()          ← ФАЗА 3
   |       Все остальные ~80+ сервисов
   |
   +-- 5. Looper.loop()
           Бесконечный message loop
```

### Фаза 1: startBootstrapServices()

```
 ФАЗА 1: BOOTSTRAP SERVICES
 (порядок запуска КРИТИЧЕН)

 +----------------------------------------------------------+
 |  # |  Сервис                  | Зависимости              |
 +----+--------------------------+--------------------------+
 |  1 |  Installer               | Нет (самый первый)       |
 |  2 |  DeviceIdentifiersPolicyService | Installer          |
 |  3 |  UriGrantsManagerService | Нет                      |
 |  4 |  ActivityTaskManagerService (ATMS) | UriGrants       |
 |  5 |  ActivityManagerService (AMS) | ATMS                 |
 |  6 |  PowerManagerService     | Нет                      |
 |  7 |  ThermalManagerService   | PowerManager             |
 |  8 |  RecoverySystemService   | Нет                      |
 |  9 |  LightsService           | Нет                      |
 | 10 |  DisplayManagerService   | Нет                      |
 | 11 |  PackageManagerService (PMS) | Installer, DisplayMgr|
 | 12 |  DomainVerificationService | PMS                    |
 | 13 |  UserManagerService      | PMS                      |
 | 14 |  OverlayManagerService   | PMS, Installer           |
 | 15 |  SensorPrivacyService    | Нет                      |
 | 16 |  SensorService           | SensorPrivacy            |
 +----------------------------------------------------------+

 Каждый сервис:
 1. new XxxService(context)
 2. ServiceManager.addService("xxx", service)
    → Регистрация в servicemanager через Binder
 3. service.onStart()
```

### Фаза 2: startCoreServices()

```
 ФАЗА 2: CORE SERVICES

 +----------------------------------------------------------+
 |  Сервис                        | Описание                |
 +--------------------------------+--------------------------+
 |  SystemConfigService           | Разбор системных конфигов|
 |  BatteryService                | Мониторинг аккумулятора |
 |  UsageStatsService             | Статистика использования|
 |  WebViewUpdateService          | Управление WebView      |
 |  CachedDeviceStateService      | Кэш состояния устройства|
 |  BinderCallsStatsService       | Статистика Binder-вызов.|
 |  LooperStatsService            | Статистика Looper       |
 |  RollbackManagerService        | Rollback обновлений     |
 |  BugreportManagerService       | Управление bugreport    |
 |  GpuService                    | GPU статистика          |
 +----------------------------------------------------------+
```

### Фаза 3: startOtherServices()

Самая большая фаза — запуск ~80+ сервисов. Ниже ключевые:

```
 ФАЗА 3: OTHER SERVICES (ВЫБОРКА)

 +----------------------------------------------------------+
 |  Сервис                        | Описание                |
 +--------------------------------+--------------------------+
 |  WindowManagerService (WMS)    | Управление окнами       |
 |  InputManagerService           | Ввод: touch, keyboard   |
 |  NetworkManagementService      | Сеть: iptables, routing |
 |  ConnectivityService           | Подключения             |
 |  WifiService                   | Wi-Fi                   |
 |  BluetoothManagerService       | Bluetooth               |
 |  AudioService                  | Звук                    |
 |  CameraService                 | Камера                  |
 |  AlarmManagerService           | Таймеры                 |
 |  NotificationManagerService    | Уведомления             |
 |  LocationManagerService        | Геолокация              |
 |  ClipboardService              | Буфер обмена            |
 |  TelephonyRegistry             | Телефония               |
 |  MediaRouterService            | Маршрутизация медиа     |
 |  VibratorManagerService        | Вибрация                |
 |  AccessibilityManagerService   | Доступность             |
 |  StorageManagerService         | Хранилище               |
 |  AccountManagerService         | Аккаунты                |
 |  ContentService                | Content observation     |
 |  JobSchedulerService           | Фоновые задачи          |
 |  DevicePolicyManagerService    | MDM/Enterprise          |
 |  StatusBarManagerService       | Статус-бар              |
 |  TrustManagerService           | Аутентификация          |
 |  FingerprintService            | Отпечатки               |
 |  LauncherAppsService           | Интеграция с Launcher   |
 |  MediaSessionService           | Медиа-сессии            |
 |  ... (~80+ сервисов)           |                         |
 +----------------------------------------------------------+
```

### systemReady() — Цепочка обратных вызовов

После запуска всех сервисов начинается цепочка systemReady():

```
 SYSTEMREADY() CALLBACK CHAIN

 startOtherServices() → конец метода:
   |
   +-- mActivityManagerService.systemReady(() -> {
   |       // Этот callback выполняется ВНУТРИ AMS.systemReady()
   |
   |       // Фаза 1: Подготовка системных сервисов
   |       mSystemServiceManager.startBootPhase(
   |           SystemService.PHASE_ACTIVITY_MANAGER_READY)  // 550
   |
   |       // Фаза 2: Каждый сервис получает systemReady()
   |       wm.systemReady()          // WindowManagerService
   |       power.systemReady()       // PowerManagerService
   |       pm.systemReady()          // PackageManagerService
   |       display.systemReady()     // DisplayManagerService
   |       ...
   |
   |       // Фаза 3: Третьи сервисы
   |       mSystemServiceManager.startBootPhase(
   |           SystemService.PHASE_THIRD_PARTY_APPS_CAN_START)  // 600
   |   })
   |
   +-- AMS.systemReady() внутри:
         |
         +-- startHomeActivityLocked()   ← ЗАПУСК LAUNCHER
         +-- sendBootCompletedBroadcast()
```

### Boot Phases (фазы загрузки)

SystemServiceManager определяет стандартные фазы:

| Фаза | Значение | Описание |
|---|---|---|
| PHASE_WAIT_FOR_DEFAULT_DISPLAY | 100 | Display доступен |
| PHASE_LOCK_SETTINGS_READY | 480 | Lock settings загружены |
| PHASE_SYSTEM_SERVICES_READY | 500 | Системные сервисы готовы |
| PHASE_ACTIVITY_MANAGER_READY | 550 | AMS готов к работе |
| PHASE_THIRD_PARTY_APPS_CAN_START | 600 | Можно запускать приложения |
| PHASE_BOOT_COMPLETED | 1000 | Boot завершён |

```
 BOOT PHASES TIMELINE

 Время →
 |--100--|--480--|--500----|--550----|--600---------|--1000--|
 Display  Lock   System    AMS      Third-party     Boot
 ready    settings services ready    apps can        completed
          ready   ready             start

 Каждый SystemService может переопределить:
 onBootPhase(int phase) {
     switch(phase) {
         case PHASE_SYSTEM_SERVICES_READY:
             // Можно начинать использовать другие сервисы
             break;
         case PHASE_BOOT_COMPLETED:
             // Загрузка полностью завершена
             break;
     }
 }
```

---

## Home Launcher Ready

### Запуск Launcher

После того как AMS получает systemReady(), он запускает домашний экран:

```
 ЗАПУСК HOME / LAUNCHER

 AMS.systemReady()
   |
   +-- startHomeActivityLocked()
   |     |
   |     +-- Формирование Intent:
   |     |     action = Intent.ACTION_MAIN
   |     |     category = Intent.CATEGORY_HOME
   |     |
   |     +-- resolveActivity() через PMS
   |     |     → Определение Launcher-приложения
   |     |       (com.google.android.apps.nexuslauncher или другой)
   |     |
   |     +-- startActivityLocked()
   |           |
   |           +-- AMS → Zygote: "fork new process"
   |           |     (через zygote socket)
   |           |
   |           +-- Zygote fork()
   |           |     |
   |           |     v
   |           |   [New process: Launcher]
   |           |     |
   |           |     +-- ActivityThread.main()
   |           |     +-- Application.onCreate()
   |           |     +-- LauncherActivity.onCreate()
   |           |     +-- Отрисовка первого кадра
   |           |
   |           +-- WMS.performSurfacePlacement()
   |                 → Launcher window visible
   |
   +-- Boot Animation остановка:
   |     property: service.bootanim.exit = 1
   |     (Когда первое окно Home нарисовано)
   |
   +-- ACTION_BOOT_COMPLETED broadcast
         |
         +-- Отправляется ВСЕМ зарегистрированным
         |   BroadcastReceiver (в manifest)
         +-- Порядок: priority в intent-filter
         +-- Фильтр: только foreground user apps
         +-- sys.boot_completed = 1 (property)
```

### Timeline загрузки (от Zygote до Launcher)

```
 TIMELINE: ZYGOTE → LAUNCHER

 Время (ms)   Событие
 0            Zygote forked from init
 |
 50           ZygoteInit.main() начало
 |
 100          preloadClasses() начало
 |            ... загрузка 8000+ классов ...
 4000         preloadClasses() конец
 |
 4100         preloadResources() начало
 5000         preloadResources() конец
 |
 5100         preloadSharedLibraries()
 5500         preload завершён
 |
 5600         forkSystemServer()
 |            [SystemServer process created]
 |
 5700         SystemServer.main()
 5800         startBootstrapServices()
 |            AMS, PMS, PowerManager, WMS...
 8000         startBootstrapServices() конец
 |
 8100         startCoreServices()
 8500         startCoreServices() конец
 |
 8600         startOtherServices()
 |            ~80+ сервисов...
 13000        startOtherServices() конец
 |
 13100        AMS.systemReady()
 13200        startHomeActivityLocked()
 |
 13300        Zygote fork() → Launcher process
 14000        Launcher: ActivityThread.main()
 14500        Launcher: Application.onCreate()
 15000        Launcher: Activity.onCreate()
 16000        Launcher: первый кадр нарисован
 |
 16100        Boot animation stop
 16200        sys.boot_completed = 1
 |
 18000        ACTION_BOOT_COMPLETED broadcast
 |            (доставка всем приложениям)
 |
 20000-30000  Все BOOT_COMPLETED receivers обработаны
```

---

## Эволюция загрузки по версиям Android

| Версия | Год | Ключевое изменение | Влияние на загрузку |
|---|---|---|---|
| Android 4.4 | 2013 | ART preview (рядом с Dalvik) | Начало перехода на AOT |
| Android 5.0 | 2014 | ART по умолчанию, dex2oat при установке | Первая загрузка быстрее (AOT), установка медленнее |
| Android 6.0 | 2015 | Runtime permissions | Не влияет на boot напрямую |
| Android 7.0 | 2016 | Hybrid compilation (JIT + AOT + profile) | Первая загрузка после OTA значительно быстрее |
| Android 7.0 | 2016 | A/B (seamless) updates | Нет downtime при OTA, быстрый rollback |
| Android 8.0 | 2017 | Project Treble | Отделение vendor от framework, vendor_boot |
| Android 8.0 | 2017 | HIDL (HAL interface) | hwservicemanager, /dev/hwbinder |
| Android 9.0 | 2018 | APEX modules (early) | Модульные обновления системных компонентов |
| Android 10 | 2019 | Two-stage init | First-stage mount, dynamic partitions |
| Android 10 | 2019 | USAP pool | Ускорение cold start на ~100 ms |
| Android 11 | 2020 | Virtual A/B | Экономия flash (COW вместо дублирования) |
| Android 12 | 2021 | GKI (Generic Kernel Image) | Унификация ядра, быстрее security patches |
| Android 12 | 2021 | Faster boot (оптимизации) | ~500ms быстрее boot на Pixel |
| Android 13 | 2022 | init_boot partition | Раздельный generic ramdisk |
| Android 13 | 2022 | Baseline Profiles (improved) | Быстрее холодный старт приложений |
| Android 14 | 2023 | Vendor DLKM | Vendor kernel modules в отдельном разделе |
| Android 15 | 2024 | 16KB page size support | Оптимизация для новых SoC |

### Сравнение компиляции dex-кода по версиям

```
 ЭВОЛЮЦИЯ DEX-КОМПИЛЯЦИИ

 Android 4.x (Dalvik):
 +----------+     +----------+     +----------+
 | .dex     | --> | JIT (при | --> | machine  |
 | bytecode |     | запуске) |     | code     |
 +----------+     +----------+     +----------+
 Проблема: JIT при каждом запуске → медленный start

 Android 5.0-6.0 (ART, full AOT):
 +----------+     +----------+     +----------+
 | .dex     | --> | dex2oat  | --> | .oat     |
 | bytecode |     | (install)|     | (native) |
 +----------+     +----------+     +----------+
 Проблема: install ~5 мин, занимает 2x storage, OTA-boot ~20 мин

 Android 7.0+ (ART, hybrid):
 +----------+     +----------+     +----------+
 | .dex     | --> | JIT      | --> | Profile  |
 | bytecode |     | (runtime)|     | data     |
 +----------+     +---+------+     +----+-----+
                      |                 |
                      v                 v
               +----------+     +----------+
               | interpret|     | dex2oat  |
               | (hot     |     | (idle,   |
               |  code)   |     |  profile)|
               +----------+     +----------+
 Install: секунды. Первый запуск: JIT. Позже: AOT по профилю.

 Android 13+ (Baseline Profiles):
 +----------+     +----------+     +----------+
 | .dex     | --> | Baseline | --> | dex2oat  |
 | bytecode |     | Profile  |     | (install)|
 | + .dm    |     | (из APK) |     |          |
 +----------+     +----------+     +----------+
 Разработчик включает профиль в APK → AOT сразу при установке
 для горячих методов. Остальное — JIT как обычно.
```

---

## Cold Start vs Warm Start vs Hot Start

### Определения

```
 ТРИ ТИПА ЗАПУСКА ПРИЛОЖЕНИЯ

 COLD START (холодный):
 +---+----+------+--------+-------+-------+--------+
 |Zygote  |bind  |install |App.   |Act.   |First   |
 |fork()  |App   |Providers|onCreate|onCreate|frame  |
 +---+----+------+--------+-------+-------+--------+
 0        50    100      200     300     400      600 ms
 Процесс НЕ существует в памяти.
 Полный цикл создания от fork до первого кадра.

 WARM START (тёплый):
         +--------+-------+-------+--------+
         |App.    |Act.   |Act.   |First   |
         |onCreate|onCreate|onStart|frame   |
         +--------+-------+-------+--------+
         0        100     150     200      350 ms
 Процесс СУЩЕСТВУЕТ, но Activity уничтожен.
 Пропускаем fork + bind + providers.

 HOT START (горячий):
                          +-------+--------+
                          |Act.   |First   |
                          |onResume|frame  |
                          +-------+--------+
                          0       50       100 ms
 Процесс и Activity СУЩЕСТВУЮТ в памяти.
 Только onResume + redraw.
```

### Что происходит при Cold Start — детали

```
 COLD START: ПОЛНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ

 1. AMS получает startActivity() запрос
    |
 2. AMS проверяет: процесс существует?
    Нет → cold start
    |
 3. AMS → Zygote socket: "fork process for com.example.app"
    |
 4. Zygote.fork()
    |
    +-- [Дочерний процесс]
    |   |
    |   +-- a. Специализация: setUID, setGID, capabilities
    |   +-- b. Открытие /dev/binder (свой Binder context)
    |   +-- c. Запуск Binder thread pool
    |   +-- d. ActivityThread.main()
    |   |       |
    |   |       +-- Looper.prepareMainLooper()
    |   |       +-- new ActivityThread()
    |   |       +-- thread.attach(false) → AMS.attachApplication()
    |   |       +-- Looper.loop() — бесконечный цикл
    |   |
    |   +-- e. AMS.attachApplication()
    |   |       |
    |   |       +-- bindApplication()
    |   |       |     |
    |   |       |     +-- handleBindApplication()
    |   |       |     |     |
    |   |       |     |     +-- LoadedApk: загрузка APK
    |   |       |     |     +-- AppComponentFactory.instantiateApplication()
    |   |       |     |     +-- installContentProviders()  ← ДО onCreate!
    |   |       |     |     +-- Application.onCreate()
    |   |       |     |
    |   |       +-- scheduleLaunchActivity()
    |   |             |
    |   |             +-- handleLaunchActivity()
    |   |                   |
    |   |                   +-- Activity.onCreate()
    |   |                   +-- Activity.onStart()
    |   |                   +-- Activity.onResume()
    |   |                   +-- ViewRootImpl.performTraversals()
    |   |                   +-- Первый кадр отрисован
    |   |
    |   +-- f. AMS записывает: displayed time
    |         (Это время, которое видно в logcat:
    |          "Displayed com.example.app/.MainActivity: +600ms")
```

Подробнее о запуске приложений — см. [[android-app-startup-performance]].

---

## Команды для отладки загрузки

### Kernel и ранняя загрузка

```bash
# Kernel messages (ring buffer)
adb shell dmesg

# Kernel boot время
adb shell dmesg | grep "Booting Linux"

# Время загрузки ядра
adb shell cat /proc/uptime

# Boot причина (normal, watchdog, kernel_panic, etc.)
adb shell getprop ro.boot.bootreason

# Kernel command line (параметры от bootloader)
adb shell cat /proc/cmdline
```

### init и property system

```bash
# Все boot-related properties
adb shell getprop | grep boot

# Boot timing properties
adb shell getprop ro.boottime.init
adb shell getprop ro.boottime.init.selinux
adb shell getprop ro.boottime.init.cold_boot_wait
adb shell getprop ro.boottime.zygote
adb shell getprop ro.boottime.SurfaceFlinger

# Состояние init-сервисов
adb shell getprop | grep init.svc

# Проверка: загрузка завершена?
adb shell getprop sys.boot_completed
# 1 = да, пусто = нет

# Все properties
adb shell getprop
```

### Zygote и SystemServer

```bash
# Процессы Zygote
adb shell ps -A | grep zygote

# SystemServer процесс
adb shell ps -A | grep system_server

# Время запуска SystemServer
adb shell logcat -b events | grep "boot_progress"

# Boot progress events (ключевые вехи):
adb shell logcat -b events -d | grep boot_progress
# boot_progress_start          — Zygote начал загрузку
# boot_progress_preload_start  — preloadClasses() начало
# boot_progress_preload_end    — preloadClasses() конец
# boot_progress_system_run     — SystemServer.run() начало
# boot_progress_pms_start      — PMS начал сканирование
# boot_progress_pms_ready      — PMS готов
# boot_progress_ams_ready      — AMS готов
# boot_progress_enable_screen  — Экран включён

# Время "displayed" для конкретного приложения
adb shell logcat | grep "Displayed"
```

### Verified Boot и разделы

```bash
# Состояние Verified Boot
adb shell getprop ro.boot.verifiedbootstate
# green, yellow, orange, red

# Активный A/B слот
adb shell getprop ro.boot.slot_suffix
# _a или _b

# Информация о разделах
adb shell ls -la /dev/block/by-name/

# dm-verity состояние
adb shell getprop ro.boot.veritymode
# enforcing или logging

# Bootloader lock status
adb shell getprop ro.boot.flash.locked
# 1 = locked, 0 = unlocked

# Подробная информация о boot image
adb shell cat /proc/version
```

### Профилирование загрузки

```bash
# Системная трассировка загрузки (Android 9+)
# Включить перед перезагрузкой:
adb shell setprop persist.debug.atrace.boottrace 1
adb shell setprop persist.debug.atrace.tags.enableflags 0x1000
adb reboot
# После загрузки забрать trace:
adb shell cat /data/misc/perfetto-traces/boottrace.perfetto-trace > boot.trace

# Simpleperf для профилирования boot
adb shell simpleperf record -p $(pidof system_server) -o /data/local/tmp/perf.data

# Boot chart (если доступно)
adb shell cat /proc/bootprof

# Systrace boot (альтернативный способ):
adb shell atrace --boot -t 30 sched freq idle am wm
adb reboot
# После загрузки:
adb shell cat /data/misc/atrace/boot_trace > boot_trace.txt
```

### Полезные logcat фильтры

```bash
# Все boot-related логи
adb logcat -b all -d | grep -iE "boot|zygote|system_server"

# SELinux denials при загрузке
adb shell dmesg | grep "avc: denied"

# Service start/stop
adb logcat -b events | grep -E "service_|am_proc"

# Время до BOOT_COMPLETED
adb shell logcat -b events | grep "boot_completed"
```

---

## Подводные камни

### 1. ContentProvider инициализируется ДО Application.onCreate()

```
 Порядок при cold start:

 fork() → bindApplication():
   1. LoadedApk (загрузка APK)
   2. Application instantiation
   3. installContentProviders()    ← ContentProvider.onCreate() ЗДЕСЬ
   4. Application.onCreate()       ← Приложение думает, что это первое

 Проблема:
 - Если ContentProvider зависит от инициализации в Application.onCreate()
   → crash или некорректное поведение
 - Firebase, WorkManager, Startup Library — все используют ContentProvider
   для автоинициализации
 - Порядок ContentProvider'ов внутри одного приложения НЕ гарантирован

 Решение:
 - Не зависеть от Application.onCreate() в ContentProvider
 - Использовать lazy initialization
 - App Startup library для управления порядком
```

### 2. BOOT_COMPLETED — не гарантия готовности

```
 Миф: "BOOT_COMPLETED значит всё готово"
 Реальность:
 - BOOT_COMPLETED отправляется когда AMS считает boot завершённым
 - Но: storage может быть encrypted и не расшифрован
 - Direct Boot (Android 7+): приложение может запуститься
   ДО расшифровки credential-encrypted storage
 - Нужно слушать ACTION_LOCKED_BOOT_COMPLETED для device-encrypted data
   и ACTION_BOOT_COMPLETED для credential-encrypted data
```

### 3. Zygote restart = потеря всех приложений

```
 Если Zygote крашится:
 1. init обнаруживает SIGCHLD
 2. init.rc: onrestart → restart zygote
 3. Все дочерние процессы Zygote получают SIGKILL
    (SystemServer, ВСЕ приложения)
 4. Новый Zygote → новый SystemServer → перезапуск Launcher
 5. Эффект: "мягкая перезагрузка" без перезагрузки ядра

 То же самое при crash SystemServer:
 init.rc: service zygote → onrestart restart zygote
 Т.к. SystemServer — критический процесс
```

### 4. Порядок запуска сервисов нельзя нарушать

```
 Если запустить WMS до AMS:
 → WMS пытается вызвать AMS → сервис не зарегистрирован → crash

 Если запустить PMS до Installer:
 → PMS не может устанавливать/удалять пакеты → crash

 Порядок в startBootstrapServices() — не случайный,
 а результат тщательного анализа зависимостей.
 Изменение порядка = потенциальный bootloop.
```

### 5. dm-verity может заблокировать после OTA

```
 Сценарий:
 1. OTA обновление записано в slot B
 2. Перезагрузка → boot из slot B
 3. dm-verity проверяет system_b
 4. Если hash tree повреждён → EIO при чтении
 5. Критичный файл недоступен → crash loop
 6. Bootloader обнаруживает failed boot → rollback на slot A

 Для разработчиков:
 - adb disable-verity  (только на userdebug builds)
 - Перезагрузка требуется после disable-verity
 - На production builds dm-verity НЕЛЬЗЯ отключить
```

---

## Мифы и заблуждения

### Миф 1: "Android использует стандартный Linux init (systemd)"

**Реальность:** Android имеет полностью собственную реализацию init. Она не совместима с systemd, sysvinit, OpenRC или любой другой стандартной Linux-системой инициализации. Android init использует собственный язык `.rc`-файлов, собственный property system и собственную систему управления сервисами.

### Миф 2: "Каждое приложение загружает свою копию framework-классов"

**Реальность:** Zygote предзагружает ~8000+ классов один раз. При fork() используется Copy-on-Write — все приложения разделяют одни и те же физические страницы памяти с framework-классами. Приватные копии создаются только для тех страниц, которые приложение модифицирует (что для framework-классов случается крайне редко).

### Миф 3: "Zygote использует Binder для fork-запросов"

**Реальность:** Zygote намеренно НЕ использует Binder до fork(). Причина: Binder создаёт thread pool, а fork() в многопоточном процессе приводит к deadlock'ам (locks, held другими потоками, остаются заблокированными навсегда в дочернем процессе). Вместо этого используется UNIX domain socket. После fork() дочерний процесс открывает СВОЙ /dev/binder и начинает использовать Binder IPC.

### Миф 4: "Boot animation — просто видео"

**Реальность:** Boot animation — это native-процесс (bootanim), который рендерит последовательности PNG-кадров через OpenGL ES. Файл анимации (`bootanimation.zip`) содержит папки с PNG-кадрами и текстовый файл `desc.txt` с параметрами (разрешение, FPS, количество повторов). Boot animation останавливается НЕ по таймеру, а по сигналу от SystemServer (property `service.bootanim.exit=1`), когда первое окно Home нарисовано.

---

## CS-фундамент

| CS-концепция | Где в загрузке Android | Почему важно |
|---|---|---|
| **Chain of Trust** | Boot ROM → SBL → ABL → vbmeta → boot → system | Каждый уровень проверяет следующий. Компрометация одного уровня = компрометация всех выше |
| **Process Model (fork)** | Zygote fork() для каждого приложения и SystemServer | Одна из причин почему Android использует процессную модель (а не thread model) для изоляции |
| **Copy-on-Write** | Zygote preload + fork → shared pages между всеми приложениями | Экономия ~70% RAM на framework-классах |
| **Init System** | Android init (PID 1) с .rc-файлами, property system, SELinux | Нестандартная реализация, заточенная под мобильные устройства |
| **IPC (Binder vs Socket)** | servicemanager: Binder. Zygote: Unix socket. Причины: fork safety | Выбор IPC зависит от threading model процесса |
| **Merkle Hash Tree** | dm-verity проверяет system/vendor через дерево хешей | O(log n) проверка целостности при каждом чтении блока |
| **Class Loading** | preloadClasses() загружает 8000+ классов в Zygote | Class loading — дорогая операция (resolve, verify, init), делается один раз |
| **Service Registry** | servicemanager — централизованный реестр (handle 0) | Паттерн Service Locator: единая точка для поиска сервисов по имени |
| **Watchdog** | init перезапускает crashed critical сервисы | Supervisor pattern для обеспечения reliability |
| **DAG зависимостей** | startBootstrapServices() — порядок определяется зависимостями | Topological sort: AMS до WMS, PMS до AMS, etc. |

---

## Проверь себя

### Вопрос 1: Порядок загрузки
**Вопрос:** Расположите элементы в правильном порядке загрузки:
SystemServer, Zygote, init, Kernel, Bootloader, servicemanager, Boot ROM, Launcher

<details>
<summary>Ответ</summary>

1. Boot ROM
2. Bootloader (PBL → SBL → ABL)
3. Kernel (Linux)
4. init (PID 1)
5. servicemanager
6. Zygote (app_process)
7. SystemServer (fork из Zygote)
8. Launcher (fork из Zygote по запросу AMS)

Ключевое: servicemanager ДОЛЖЕН запуститься до Zygote, потому что SystemServer (forked из Zygote) регистрирует Binder-сервисы в servicemanager. Но Zygote сам НЕ использует servicemanager (использует socket).
</details>

### Вопрос 2: Почему Zygote использует socket, а не Binder?
**Вопрос:** Объясните архитектурное решение использовать Unix domain socket для коммуникации с Zygote вместо Binder IPC.

<details>
<summary>Ответ</summary>

Binder создаёт пул потоков (thread pool) для обработки запросов. При вызове fork() в многопоточном процессе:
1. Дочерний процесс наследует все file descriptors, но НЕ потоки
2. Если поток родителя держал lock (mutex) в момент fork — этот lock НАВСЕГДА останется заблокированным в дочернем процессе (поток, который должен его отпустить, не существует)
3. Результат: deadlock в дочернем процессе

Поэтому Zygote:
- НЕ инициализирует Binder thread pool
- Принимает fork-запросы через Unix domain socket (однопоточный)
- После fork() дочерний процесс открывает СВОЙ /dev/binder и создаёт свой thread pool

Это классическая проблема POSIX: fork() + threads = danger.
</details>

### Вопрос 3: Экономия памяти через Zygote
**Вопрос:** На устройстве запущено 30 приложений. Zygote предзагрузил 150 MB framework-классов и ресурсов. Сколько RAM экономится благодаря COW? Какие условия могут уменьшить экономию?

<details>
<summary>Ответ</summary>

Теоретическая экономия: 30 apps × 150 MB = 4500 MB − 150 MB (shared) = **4350 MB**

На практике экономия меньше, потому что:
1. **Dirty pages:** Если приложение модифицирует объект из preloaded-класса, COW создаёт приватную копию страницы (4KB). Даже изменение одного поля в одном объекте = копия всей страницы
2. **GC:** Garbage collector может перемещать объекты (compacting GC), создавая dirty pages
3. **JIT-компиляция:** JIT создаёт приватные compiled code pages
4. **Class initialization:** Статические инициализаторы модифицируют class metadata

Реальная экономия: ~60-70% от теоретической, т.е. ~2500-3000 MB для 30 приложений.
</details>

### Вопрос 4: Что произойдёт при crash SystemServer?
**Вопрос:** System Server крашнулся из-за uncaught exception. Опишите цепочку событий, которая последует.

<details>
<summary>Ответ</summary>

1. SystemServer процесс завершается (exit с ненулевым кодом)
2. init получает SIGCHLD (как родитель всех демонов)
3. Но SystemServer — дочерний процесс Zygote, не init
4. Zygote обнаруживает смерть SystemServer (waitpid)
5. Zygote вызывает exit() — завершает себя
6. init получает SIGCHLD для Zygote (Zygote — direct child of init)
7. init видит: `service zygote` → class `main` → `critical` flag
8. init перезапускает Zygote (и все сервисы с `onrestart restart ...`)
9. Все процессы-потомки Zygote получают SIGHUP/SIGKILL:
   - Все приложения убиты
   - Все ContentProvider закрыты
   - Все Binder-соединения разорваны
10. Новый Zygote → preload → fork SystemServer → boot sequence
11. Launcher перезапущен
12. Пользователь видит "мягкую перезагрузку" (без kernel reboot)
13. Время восстановления: ~10-20 секунд

Это аналог "горячей перезагрузки" — kernel и init остаются, перезапускается только Java-стек.
</details>

---

## Ключевые карточки

### Карточка 1: Zygote
| | |
|---|---|
| **Вопрос** | Что такое Zygote и зачем он нужен? |
| **Ответ** | Zygote — процесс-шаблон (app_process64), который предзагружает ~8000+ framework-классов, ресурсы и native-библиотеки. Все приложения создаются через fork() от Zygote, используя COW для разделения памяти. Экономит ~70% RAM и ~1-3 сек при каждом cold start. |

### Карточка 2: Почему socket, а не Binder
| | |
|---|---|
| **Вопрос** | Почему Zygote использует Unix socket вместо Binder? |
| **Ответ** | fork() в многопоточном процессе (каким был бы Zygote с Binder thread pool) приводит к deadlock: дочерний процесс наследует locks, но не потоки, которые их держат. Поэтому Zygote однопоточно слушает Unix socket, а Binder инициализируется только ПОСЛЕ fork в дочернем процессе. |

### Карточка 3: AVB Boot States
| | |
|---|---|
| **Вопрос** | Какие четыре состояния загрузки определяет AVB? |
| **Ответ** | Green (locked + OEM key = штатное), Yellow (locked + custom key = предупреждение), Orange (unlocked = верификация отключена, data wiped), Red (locked + failed verification = не грузится). |

### Карточка 4: SystemServer фазы
| | |
|---|---|
| **Вопрос** | Назовите три фазы запуска сервисов в SystemServer. |
| **Ответ** | 1) startBootstrapServices() — критичные сервисы с жёсткими зависимостями (AMS, PMS, PowerManager). 2) startCoreServices() — важные, но менее зависимые (BatteryService, UsageStats). 3) startOtherServices() — все остальные ~80+ сервисов (WMS, InputManager, ConnectivityService и др.). |

### Карточка 5: dm-verity
| | |
|---|---|
| **Вопрос** | Как dm-verity обеспечивает целостность system partition? |
| **Ответ** | dm-verity использует Merkle Hash Tree (дерево хешей). Root hash хранится в vbmeta (подписан OEM-ключом). При чтении каждого блока ядро вычисляет путь от блока до root hash. Если хеш не совпадает — возвращается EIO. Проверка O(log n) от количества блоков. |

### Карточка 6: init.rc
| | |
|---|---|
| **Вопрос** | Чем Android init отличается от стандартного Linux init? |
| **Ответ** | Android init — полностью собственная реализация (не systemd/sysvinit). Использует .rc-файлы с тремя конструкциями: actions (on-блоки с triggers), services (демоны), imports. Имеет property system (shared memory key-value), SELinux инициализацию и двухстадийную загрузку (first-stage из ramdisk, second-stage из /system). |

### Карточка 7: Cold Start последовательность
| | |
|---|---|
| **Вопрос** | Опишите порядок инициализации при cold start приложения (от fork до первого кадра). |
| **Ответ** | fork() от Zygote → специализация (UID/GID) → открытие /dev/binder → ActivityThread.main() → Looper.prepare → attach → AMS.attachApplication() → bindApplication() → LoadedApk → installContentProviders() (ДО onCreate!) → Application.onCreate() → Activity.onCreate() → onStart() → onResume() → первый кадр (ViewRootImpl.performTraversals). |

---

## Куда дальше

| Направление | Материал | Зачем |
|---|---|---|
| Binder IPC | [[android-binder-ipc]] | Детали механизма IPC, который связывает все сервисы |
| Системные сервисы | [[android-system-services]] | Подробный разбор AMS, WMS, PMS и других сервисов |
| ART Runtime | [[android-art-runtime]] | Как работает виртуальная машина, JIT/AOT, GC |
| Запуск приложения | [[android-app-startup-performance]] | Оптимизация cold/warm/hot start |
| ActivityThread | [[android-activitythread-internals]] | Главный поток приложения: Looper, Handler, message loop |
| Память процесса | [[android-process-memory]] | PSS, shared/private memory, COW в деталях |
| Kernel-расширения | [[android-kernel-extensions]] | Binder driver, ashmem, wakelocks на уровне ядра |
| Архитектура | [[android-architecture]] | Общий обзор слоёв Android |

---

## Связи

**Прямые зависимости:**
- [[android-architecture]] — общая архитектура, в контексте которой происходит загрузка
- [[os-processes-threads]] — процессная модель, fork(), COW — фундамент Zygote
- [[android-kernel-extensions]] — Android-патчи ядра (Binder driver, ashmem)

**Тесно связанные:**
- [[android-binder-ipc]] — IPC-механизм, servicemanager, handle 0
- [[android-system-services]] — сервисы, запускаемые в SystemServer
- [[android-art-runtime]] — ART VM, создаваемая в Zygote (startVm)
- [[android-activitythread-internals]] — ActivityThread.main() при cold start
- [[android-app-startup-performance]] — cold/warm/hot start оптимизация
- [[android-process-memory]] — COW, shared memory, PSS

**Косвенные:**
- [[android-build-system]] — как собираются boot.img, system.img
- [[android-security-model]] — SELinux, permissions, sandbox
- [[linux-kernel-boot]] — общие принципы загрузки Linux ядра

---

## Источники

### AOSP исходный код
1. **system/core/init/** — Android init daemon
   - `init.cpp` — main(), first/second stage init
   - `init.rc` — главный конфигурационный файл
   - `property_service.cpp` — property system
   - `service.cpp` — управление сервисами
   - https://android.googlesource.com/platform/system/core/+/refs/heads/main/init/

2. **frameworks/base/core/java/com/android/internal/os/ZygoteInit.java**
   - `main()`, `preloadClasses()`, `preloadResources()`, `forkSystemServer()`
   - https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/com/android/internal/os/ZygoteInit.java

3. **frameworks/base/services/java/com/android/server/SystemServer.java**
   - `main()`, `run()`, `startBootstrapServices()`, `startCoreServices()`, `startOtherServices()`
   - https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/java/com/android/server/SystemServer.java

4. **frameworks/base/cmds/app_process/app_main.cpp**
   - Точка входа app_process (бинарник Zygote)
   - https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/cmds/app_process/app_main.cpp

5. **frameworks/base/core/jni/AndroidRuntime.cpp**
   - `start()`, `startVm()`, `startReg()`
   - https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/jni/AndroidRuntime.cpp

6. **frameworks/native/cmds/servicemanager/**
   - servicemanager daemon, Binder context manager
   - https://android.googlesource.com/platform/frameworks/native/+/refs/heads/main/cmds/servicemanager/

### Официальная документация
7. **Android Verified Boot (AVB):**
   - https://source.android.com/docs/security/features/verifiedboot
   - https://source.android.com/docs/security/features/verifiedboot/avb
   - https://source.android.com/docs/security/features/verifiedboot/verified-boot

8. **Generic Kernel Image (GKI):**
   - https://source.android.com/docs/core/architecture/kernel/generic-kernel-image
   - https://source.android.com/docs/core/architecture/partitions/generic-boot
   - https://source.android.com/docs/core/architecture/partitions/vendor-boot-partitions

9. **Boot Time Management:**
   - https://source.android.com/docs/automotive/power/boot_time

10. **A/B (Seamless) Updates:**
    - https://source.android.com/docs/core/ota/ab

### Книги
11. **"Embedded Android" — Karim Yaghmour (O'Reilly, 2013)**
    - Главы о boot sequence, init, Zygote
    - Фундаментальный справочник (многие принципы актуальны)

12. **"Android Internals: A Confectioner's Cookbook" — Jonathan Levin**
    - Глубокий разбор init, boot, internals
    - http://newandroidbook.com/

13. **"Android System Programming" — Roger Ye (Packt, 2017)**
    - Boot process, HAL, system services

14. **"Learning Android Internals" — Oleg Vasavada**
    - Обзор SystemServer, Zygote, AMS

### Статьи и блоги
15. **"Android Boot Sequence" — libliboom (Medium)**
    - https://libliboom.medium.com/android-boot-sequence-71f1f5ca3c5c

16. **"How does system_server work?" — AOSP Insight**
    - https://aospinsight.com/the-very-first-android-system-process-system_server/

17. **"Android Booting Process" — NXP Community**
    - https://community.nxp.com/t5/i-MX-Processors-Knowledge-Base/The-Android-Booting-process/ta-p/1129182

18. **eLinux.org — Android Booting:**
    - https://elinux.org/Android_Booting
    - https://elinux.org/Android_Zygote_Startup

19. **"Android Verified Boot 2.0 and U-Boot" — Linaro/TI**
    - https://docs.u-boot.org/en/latest/android/avb2.html

20. **"Google's Generic Kernel Image" — XDA Developers**
    - https://www.xda-developers.com/google-generic-kernel-image/
