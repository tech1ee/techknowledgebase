---
title: "Android System Internals: карта глубокого погружения"
created: 2026-02-19
modified: 2026-02-19
type: overview
area: android
confidence: high
tags:
  - topic/android
  - topic/internals
  - type/overview
  - level/advanced
related:
  - "[[android-architecture]]"
  - "[[android-overview]]"
  - "[[android-handler-looper]]"
  - "[[android-process-memory]]"
cs-foundations: [operating-systems, ipc, process-model, virtual-memory, runtime-systems]
prerequisites:
  - "[[android-architecture]]"
  - "[[os-processes-threads]]"
reading_time: 10
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Android System Internals: карта глубокого погружения

> Этот раздел посвящён **внутреннему устройству Android** — механизмам, которые работают между Linux-ядром и вашим `onCreate()`. Здесь нет API-документации и рецептов. Здесь ответы на вопросы "почему" и "как на самом деле".

---

## Зачем изучать internals

| Что вы поймёте | Без этих знаний |
|----------------|-----------------|
| Почему `startActivity()` — это 15 Binder-транзакций | "Магия framework, просто работает" |
| Почему ANR через 5 секунд, а не 10 | Не знаете про Main Thread message queue |
| Почему `ContentProvider.onCreate()` вызывается ДО `Application.onCreate()` | Непонятные баги инициализации |
| Почему приложение запускается за 200ms, а не 3 секунды | Не можете объяснить роль Zygote |
| Почему Android убивает приложения без предупреждения | Неправильная работа с lifecycle |
| Как Baseline Profiles ускоряют запуск | Не понимаете JIT/AOT стратегию ART |

---

## Prerequisites

Перед погружением в internals рекомендуется пройти:

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| Архитектура Android (обзор) | Общее понимание слоёв: Linux → ART → Framework → App | [[android-architecture]] |
| Процессы и потоки ОС | fork(), mmap, IPC на уровне ОС | [[os-processes-threads]] |
| Управление памятью ОС | Виртуальная память, Copy-on-Write | [[os-memory-management]] |
| Handler/Looper/MessageQueue | Фундамент асинхронности Android | [[android-handler-looper]] |
| Activity Lifecycle | Базовое понимание жизненного цикла | [[android-activity-lifecycle]] |

---

## Карта раздела

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANDROID SYSTEM INTERNALS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  УРОВЕНЬ 1: Linux Kernel                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  android-kernel-extensions                                        │  │
│  │  Binder driver, ashmem/memfd, lmkd, wakelocks, SELinux,          │  │
│  │  cgroups, dm-verity, ION/DMA-BUF                                 │  │
│  └──────────────────────────┬────────────────────────────────────────┘  │
│                              │                                          │
│  УРОВЕНЬ 2: IPC Framework   │                                          │
│  ┌───────────────────────────▼──────────────────────────────────────┐  │
│  │  android-binder-ipc                                               │  │
│  │  Proxy/Stub, Parcel, ServiceManager, mmap (1-copy),              │  │
│  │  thread pool, death notification, security model                  │  │
│  └──────────────────────────┬────────────────────────────────────────┘  │
│                              │                                          │
│  УРОВЕНЬ 3: System          │                                          │
│  ┌──────────────────────────▼──────────┐  ┌─────────────────────────┐  │
│  │  android-boot-process               │  │  android-art-runtime    │  │
│  │  init → Zygote → SystemServer →     │  │  DEX, JIT/AOT, GC,     │  │
│  │  → Launcher → BOOT_COMPLETED       │  │  profiles, class load   │  │
│  └──────────────────────────┬──────────┘  └────────────┬────────────┘  │
│                              │                          │               │
│  УРОВЕНЬ 4: Framework       │                          │               │
│  ┌──────────────────────────▼──────────┐  ┌────────────▼────────────┐  │
│  │  android-system-services            │  │  android-activitythread  │  │
│  │  AMS, WMS, PMS, PowerManager,       │  │  -internals             │  │
│  │  SystemServer startup               │  │  ApplicationThread,     │  │
│  │                                     │  │  ClientTransaction,     │  │
│  │                                     │  │  Instrumentation        │  │
│  └─────────────────────────────────────┘  └─────────────────────────┘  │
│                                                                         │
│  СВЯЗАННЫЕ DEEP-DIVES (уже существуют):                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │
│  │ Handler/    │ │ Context     │ │ Window      │ │ App Startup     │  │
│  │ Looper      │ │ Internals   │ │ System      │ │ Performance     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │
│  │ Intent      │ │ Service     │ │ Broadcast   │ │ ContentProvider │  │
│  │ Internals   │ │ Internals   │ │ Internals   │ │ Internals       │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Рекомендуемый порядок чтения

```
1. [[android-kernel-extensions]]           — Что Android добавил к Linux ядру
       ↓
2. [[android-binder-ipc]]                  — Фундамент всего IPC в Android
       ↓
3. [[android-boot-process]]               — Загрузка: от кнопки питания до Launcher
       ↓
4. [[android-art-runtime]]                — ART: DEX, компиляция, GC
       ↓
5. [[android-system-services]]            — System Server: AMS, WMS, PMS
       ↓
6. [[android-activitythread-internals]]   — Внутри процесса приложения
```

---

## Все материалы раздела

| # | Файл | Что узнаете | Prerequisites | Время |
|---|------|------------|---------------|-------|
| 1 | [[android-kernel-extensions]] | Binder driver, ashmem, lmkd, wakelocks, SELinux — как Android модифицировал Linux | [[os-processes-threads]], [[android-architecture]] | ~85 мин |
| 2 | [[android-binder-ipc]] | Полный механизм Binder IPC: driver, mmap, Proxy/Stub, AIDL, ServiceManager, security | [[android-kernel-extensions]], [[android-architecture]] | ~110 мин |
| 3 | [[android-boot-process]] | Цепочка загрузки: Bootloader → init → Zygote → SystemServer → Launcher | [[android-kernel-extensions]], [[android-binder-ipc]] | ~95 мин |
| 4 | [[android-art-runtime]] | ART: DEX format, JIT/AOT/Interpret, GC (CC), Baseline Profiles, class loading | [[android-architecture]], [[android-compilation-pipeline]] | ~105 мин |
| 5 | [[android-system-services]] | System Server, AMS, WMS, PMS: как framework управляет всем | [[android-binder-ipc]], [[android-boot-process]] | ~100 мин |
| 6 | [[android-activitythread-internals]] | ActivityThread, ApplicationThread, ClientTransaction: как dispatching lifecycle | [[android-handler-looper]], [[android-binder-ipc]], [[android-system-services]] | ~95 мин |

---

## Связи с существующими deep-dives

Новые файлы дополняют (не дублируют) существующие material:

| Существующий файл | Что покрывает | Новый файл идёт глубже |
|-------------------|--------------|----------------------|
| [[android-architecture]] | Обзор: Linux → Binder → Zygote → ART | binder-ipc, boot-process, art-runtime, system-services |
| [[android-handler-looper]] | Handler/Looper/MessageQueue, Choreographer | activitythread-internals (как Handler используется framework) |
| [[android-process-memory]] | LMK, OOM adj, heap management | kernel-extensions (lmkd kernel mechanism) |
| [[android-app-startup-performance]] | Cold start оптимизация (Zygote → первый кадр) | boot-process (system boot), activitythread (app init) |
| [[android-service-internals]] | Service lifecycle, Local/Messenger/AIDL | binder-ipc (low-level Binder mechanism) |
| [[android-compilation-pipeline]] | kotlinc → D8 → R8 → APK (build) | art-runtime (runtime: DEX execution, JIT/AOT, GC) |

---

## Источники (общие для раздела)

### Книги
| Книга | Применение |
|-------|-----------|
| Vasavada N. *Android Internals: A Confectioner's Cookbook* (2019) | Все файлы — AOSP internals |
| Meier R. *Professional Android* (2018, 4th ed) | Framework internals |
| Levin J. *Android Internals: Power User's View* (2015) | Kernel, boot process |

### AOSP Source
- [frameworks/base/](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/) — Framework код
- [frameworks/native/libs/binder/](https://cs.android.com/android/platform/superproject/+/master:frameworks/native/libs/binder/) — Native Binder
- [art/](https://cs.android.com/android/platform/superproject/+/master:art/) — ART Runtime
- [system/core/init/](https://cs.android.com/android/platform/superproject/+/master:system/core/init/) — init process

### Полезные ресурсы
- [Android Source](https://source.android.com/) — официальная документация AOSP
- [cs.android.com](https://cs.android.com/) — поиск по AOSP исходникам
- [LWN.net](https://lwn.net/) — статьи о Linux ядре и Android
