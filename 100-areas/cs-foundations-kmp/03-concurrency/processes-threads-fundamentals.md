---
title: "Процессы и потоки: фундамент конкурентности"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/intermediate
related:
  - "[[concurrency-vs-parallelism]]"
  - "[[synchronization-primitives]]"
  - "[[async-models-overview]]"
---

# Процессы и потоки: фундамент конкурентности

> **TL;DR:** Процесс — экземпляр программы с изолированной памятью. Поток — единица исполнения внутри процесса, потоки делят память. Context switch — переключение CPU между задачами. Kernel threads управляются ОС, user/green threads — runtime'ом (дешевле, но ограничения). Для KMP критично: Kotlin coroutines — это "зелёные потоки" поверх thread pools, отсюда их эффективность.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Memory Model** | Понять shared memory | [[memory-model-fundamentals]] |
| **CPU basics** | Понять scheduling | Общие знания |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Process** | Экземпляр программы с изолированной памятью | Отдельная квартира |
| **Thread** | Единица исполнения внутри процесса | Жилец в квартире |
| **Context Switch** | Переключение CPU между задачами | Смена работника у станка |
| **Scheduler** | Компонент ОС, распределяющий CPU | Менеджер смен |
| **Preemption** | Принудительное прерывание программы | Звонок будильника |
| **Thread Pool** | Набор готовых потоков для работы | Команда дежурных |
| **IPC** | Inter-Process Communication | Письма между квартирами |

---

## ПОЧЕМУ нужны процессы и потоки

### Одна программа — один CPU?

В 1940-х компьютеры работали так: одна программа загружается, выполняется до конца, потом следующая. Программисты ждали в очередях часами.

Проблема: CPU простаивает когда программа ждёт ввода-вывода. Пользователь печатает — CPU ждёт. Данные читаются с диска — CPU ждёт.

### 1960-е: рождение многозадачности

Решение: пока одна программа ждёт I/O, запустить другую. Unix (1969) реализовал preemptive multitasking — ОС сама решает когда переключить программу.

Но процессы дорогие: отдельная память, контексты, ресурсы. Что если программа хочет делать несколько вещей одновременно?

### Потоки: лёгкие процессы

Потоки появились как "облегчённые процессы". Один процесс, несколько потоков исполнения. Потоки делят память — дешевле создавать и переключать.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ПРОЦЕСС vs ПОТОК                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ПРОЦЕСС A           ПРОЦЕСС B                                 │
│   ┌─────────────┐     ┌─────────────┐                           │
│   │ Code        │     │ Code        │                           │
│   │ Data        │     │ Data        │                           │
│   │ Heap        │     │ Heap        │  ← Изолированная память   │
│   │ Stack       │     │ Stack       │                           │
│   └─────────────┘     └─────────────┘                           │
│                                                                 │
│   ПРОЦЕСС C (с потоками)                                        │
│   ┌─────────────────────────────────┐                           │
│   │ Code  (shared)                  │                           │
│   │ Data  (shared)                  │                           │
│   │ Heap  (shared)                  │                           │
│   ├─────────┬─────────┬─────────────┤                           │
│   │ Stack 1 │ Stack 2 │ Stack 3     │  ← Отдельные стеки        │
│   │ Thread1 │ Thread2 │ Thread3     │                           │
│   └─────────┴─────────┴─────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ЧТО такое процесс

### Анатомия процесса

Процесс — это:
- **Код программы** (text segment)
- **Данные** (data segment — глобальные переменные)
- **Heap** (динамическая память)
- **Stack** (локальные переменные, call stack)
- **Ресурсы** (открытые файлы, сокеты, ...)
- **Контекст** (регистры, program counter)

Каждый процесс имеет уникальный Process ID (PID). ОС ведёт таблицу процессов — Process Control Block (PCB) для каждого.

### Изоляция процессов

Процесс A не может читать память процесса B. Это:
- **Безопасность** — малварь не достанет данные браузера
- **Надёжность** — crash одного не роняет другие
- **Независимость** — разные версии библиотек

Chrome использует отдельный процесс для каждой вкладки. Вкладка зависла? Другие работают.

---

## ЧТО такое поток

### Что делят потоки

Потоки внутри процесса делят:
- Код (text segment)
- Данные (globals)
- Heap
- Открытые файлы
- Signal handlers

У каждого потока своё:
- Stack
- Program Counter
- Регистры
- Thread ID
- Thread Local Storage (TLS)

### Почему потоки легче процессов

Создание процесса: выделить память, скопировать данные, настроить таблицы страниц — миллисекунды.

Создание потока: выделить стек, инициализировать контекст — микросекунды. В 100-1000 раз быстрее.

Переключение между потоками одного процесса дешевле — не нужно менять адресное пространство.

### Цена удобства: shared memory

Общая память = общие проблемы. Два потока меняют одну переменную — race condition:

```kotlin
// Thread 1                    // Thread 2
val temp = counter             val temp = counter
counter = temp + 1             counter = temp + 1

// Ожидаемо: counter += 2
// Реально: counter += 1 (один инкремент потерян)
```

Потоки требуют синхронизации: mutex, semaphore, atomic operations.

---

## КАК работает Context Switch

### Зачем переключаться

CPU выполняет один поток в один момент времени. Чтобы создать иллюзию одновременности, ОС переключает потоки быстро — десятки-сотни раз в секунду.

### Что происходит при переключении

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT SWITCH                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Thread A работает                                             │
│       ↓                                                         │
│   Timer interrupt! (или I/O, или yield)                         │
│       ↓                                                         │
│   1. Сохранить регистры Thread A в его TCB                      │
│   2. Сохранить program counter Thread A                         │
│   3. Сохранить stack pointer Thread A                           │
│       ↓                                                         │
│   Scheduler выбирает следующий поток                            │
│       ↓                                                         │
│   4. Загрузить регистры Thread B из его TCB                     │
│   5. Загрузить program counter Thread B                         │
│   6. Загрузить stack pointer Thread B                           │
│       ↓                                                         │
│   Thread B продолжает работу                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Стоимость context switch

Context switch не бесплатен:
- **CPU cycles:** 1000-10000 циклов
- **Cache miss:** L1/L2 кэш заполнен данными предыдущего потока
- **TLB flush:** при переключении процессов
- **Pipeline flush:** современные CPU используют pipelining

Частые переключения = overhead. Слишком редкие = плохая отзывчивость.

### Когда происходит переключение

- **Time slice expired** — таймер прерывает поток
- **Blocking I/O** — поток ждёт диск/сеть
- **Higher priority ready** — важная задача проснулась
- **Voluntary yield** — поток сам отдаёт управление

---

## Kernel Threads vs Green Threads

### Kernel (Native) Threads

Kernel threads управляются ОС:
- Scheduler ОС видит их и распределяет по cores
- Настоящий параллелизм на multicore
- Если один блокируется на I/O — другие работают
- Тяжелее создавать и переключать

### User / Green Threads

Green threads (user-level threads) управляются runtime'ом в user space:
- ОС не знает о них
- Очень лёгкие — можно создать тысячи
- Быстрое переключение (нет kernel mode switch)
- Один kernel thread = много green threads

Проблема: если green thread делает blocking syscall — заблокирует весь kernel thread со всеми green threads.

```
┌─────────────────────────────────────────────────────────────────┐
│                    KERNEL vs GREEN THREADS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   KERNEL THREADS:                                               │
│   ┌─────────┬─────────┬─────────┐                               │
│   │ Thread1 │ Thread2 │ Thread3 │    OS видит все               │
│   └────┬────┴────┬────┴────┬────┘                               │
│        │         │         │                                    │
│        ▼         ▼         ▼                                    │
│   ┌─────────────────────────────┐                               │
│   │      OS Scheduler           │                               │
│   └─────────────────────────────┘                               │
│                                                                 │
│   GREEN THREADS:                                                │
│   ┌─────────────────────────────────────┐                       │
│   │ Green1 Green2 Green3 Green4 Green5  │  Runtime scheduler    │
│   └─────────────────┬───────────────────┘                       │
│                     │                                           │
│                     ▼                                           │
│              ┌─────────────┐                                    │
│              │ 1 Kernel Th │     OS видит только это            │
│              └─────────────┘                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Mapping Models

**Many-to-One:** все user threads → один kernel thread. Просто, но нет параллелизма.

**One-to-One:** каждый user thread → kernel thread. Linux, Windows используют это. Настоящий параллелизм, но тяжело.

**Many-to-Many:** M user threads → N kernel threads. Go goroutines работают так. Лучшее из обоих миров.

---

## Thread Pools

### Проблема частого создания потоков

Создание потока занимает время и память. Создавать поток на каждую задачу — расточительно.

### Решение: пул готовых потоков

Thread pool — набор заранее созданных потоков. Задачи добавляются в очередь, свободный поток берёт задачу.

```kotlin
// Java ExecutorService
val pool = Executors.newFixedThreadPool(4)
pool.submit { doWork() }

// Kotlin coroutines используют пулы под капотом
launch(Dispatchers.Default) {
    doWork()
}
```

### Размер пула

- **CPU-bound работа:** ~количество cores
- **I/O-bound работа:** больше (потоки ждут I/O)
- **Слишком много:** overhead на переключения
- **Слишком мало:** недоиспользование CPU

---

## Kotlin Coroutines как Green Threads

### Что такое coroutine

Coroutine — это suspendable computation. Она может приостановиться и возобновиться без блокировки потока.

```kotlin
suspend fun fetchData(): Data {
    val response = httpClient.get(url)  // suspend, не block!
    return response.parse()
}
```

### Как это работает

Coroutines работают поверх thread pool (Dispatcher):

```
Coroutine → suspend → Dispatcher возвращает thread в pool
                     ...другие coroutines работают...
Coroutine → resume → Dispatcher даёт thread из pool
```

Один поток может исполнять тысячи coroutines (по очереди).

### Dispatchers

- **Dispatchers.Default:** CPU-bound, #cores потоков
- **Dispatchers.IO:** I/O-bound, расширяемый пул
- **Dispatchers.Main:** UI поток (Android)

### Преимущества над threads

| Threads | Coroutines |
|---------|------------|
| Тяжёлые (~1MB stack) | Лёгкие (~KB) |
| Блокируют при ожидании | Suspend без блокировки |
| Сотни max | Тысячи-миллионы |
| OS scheduling | Structured concurrency |

---

## Подводные камни

### Race Conditions

Общая память + несколько потоков = race conditions. Используй:
- Mutex / synchronized
- Atomic operations
- Channels (share by communicating)

### Deadlocks

Два потока ждут друг друга → оба заблокированы навсегда.

```kotlin
// Thread 1: lock A, then lock B
// Thread 2: lock B, then lock A
// → Deadlock!
```

### Context Switch Overhead

Много потоков ≠ много работы. Переключения съедают CPU.

### Green Threads и Blocking

```kotlin
// ПЛОХО: blocking call в coroutine
launch {
    Thread.sleep(1000)  // блокирует dispatcher thread!
}

// ХОРОШО: suspend function
launch {
    delay(1000)  // suspend, не block
}
```

---

## Куда дальше

**Для синхронизации:**
→ [[synchronization-primitives]] — mutex, semaphore, atomic

**Для async patterns:**
→ [[async-models-overview]] — callbacks, promises, coroutines

**Практика:**
→ Kotlin coroutines guide

---

## Источники

- [GeeksforGeeks: Process vs Thread](https://www.geeksforgeeks.org/operating-systems/difference-between-process-and-thread/) — базовое сравнение
- [Wikipedia: Context Switch](https://en.wikipedia.org/wiki/Context_switch) — детали переключения
- [Kotlin: Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html) — официальная документация
- [Baeldung: Threads vs Coroutines](https://www.baeldung.com/kotlin/threads-coroutines) — сравнение для Kotlin

---

*Проверено: 2026-01-09*
