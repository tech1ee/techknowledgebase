---
title: "JVM Concurrency: карта многопоточности"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - concurrency
  - threads
  - type/moc
  - level/beginner
type: moc
status: published
area: programming
confidence: high
related:
  - "[[jvm-synchronization]]"
  - "[[jvm-concurrent-collections]]"
  - "[[jvm-executors-futures]]"
  - "[[java-modern-features]]"
---

# JVM Concurrency: карта многопоточности

> **TL;DR:** Java Memory Model (JMM) = правила видимости между потоками. `volatile` = видимость, `synchronized` = mutual exclusion + видимость, `Atomic*` = lock-free через CAS. Virtual Threads (Java 21) = миллионы легковесных потоков для I/O. Netflix: Virtual Threads снизили потребление потоков с 5000 до 200 при том же throughput.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Как работает JVM | Понимать потоки в контексте JVM | [[jvm-basics-history]] |
| OS потоки | Thread vs Process, scheduling | [[os-processes-threads]] |
| OS синхронизация | Mutex, semaphore на уровне ОС | [[os-synchronization]] |

---

Многопоточность в Java — стек от низкоуровневых примитивов (volatile, synchronized, Atomic) до высокоуровневых абстракций (ExecutorService, CompletableFuture, Virtual Threads в Java 21). Java Memory Model определяет правила видимости изменений между потоками через happens-before гарантии.

Race conditions и deadlocks проявляются под нагрузкой, почти невоспроизводимы локально. `flag = true` без volatile — другой поток может не увидеть изменение из-за CPU cache. volatile для видимости, synchronized для mutual exclusion, Atomic для lock-free счётчиков. Неправильный выбор — баги или потерянная производительность.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Поток (Thread)** | Независимая последовательность выполнения кода | Работник в команде |
| **Блокировка (Lock)** | Механизм ограничения доступа к ресурсу | Ключ от комнаты — только у одного |
| **Deadlock** | Потоки ждут друг друга бесконечно | Два человека не уступают друг другу на узкой дороге |
| **Race Condition** | Результат зависит от порядка выполнения | Два кассира продают последний билет |
| **Видимость (Visibility)** | Гарантия что поток видит изменения другого | Записка на общей доске — все видят |
| **CAS** | Compare-And-Swap — атомарная операция CPU | "Если цена ещё X, покупаю за Y" |
| **JMM** | Java Memory Model — модель памяти | Контракт: когда изменения видны другим |
| **Happens-Before** | Гарантия порядка операций между потоками | "Если A до B, то A точно виден из B" |
| **Virtual Thread** | Легковесный поток в Java 21+ | Сотни курьеров на одной машине |

---

## Выбор инструмента

```
Задача                              Инструмент
─────────────────────────────────────────────────────────────
Простой флаг (stop/ready)        → volatile boolean
Счётчик                          → AtomicInteger / LongAdder
Защита критической секции        → synchronized / Lock
Thread-safe Map                  → ConcurrentHashMap
Producer-Consumer                → BlockingQueue
Параллельные задачи              → ExecutorService
Async composition                → CompletableFuture
Миллионы I/O операций            → Virtual Threads (Java 21+)
```

---

## Java Memory Model (JMM)

**Проблема:** изменения одного потока могут быть не видны другому.

```java
// Поток 1
counter = 42;
flag = true;

// Поток 2
while (!flag) { }     // Может зависнуть навсегда
print(counter);       // Может вывести 0
```

**Причины:**
- CPU cache — каждый поток читает из своего кэша
- Compiler reordering — инструкции переставляются для оптимизации
- Store buffer — записи откладываются

**Решение:** happens-before гарантии.

```
happens-before rules:
───────────────────────────────────────────────────
volatile write  →  volatile read
monitor unlock  →  monitor lock
thread.start()  →  первая инструкция потока
последняя инструкция  →  thread.join()
```

---

## Что когда использовать

### volatile — видимость без блокировки

```java
private volatile boolean shutdown = false;

// Writer
public void stop() { shutdown = true; }

// Reader
while (!shutdown) { work(); }
```

**Годится:** флаги, one-writer-many-readers.
**Не годится:** `counter++` (не атомарно).

### synchronized — mutual exclusion

```java
public synchronized void transfer(Account to, int amount) {
    this.balance -= amount;
    to.balance += amount;
}
```

**Годится:** составные операции, критические секции.
**Минус:** блокирует потоки.

### Atomic — lock-free счётчики

```java
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();  // Атомарно через CAS
```

**Годится:** счётчики, CAS-операции.
**Минус:** только простые операции.

### LongAdder — высоконагруженные счётчики

```java
LongAdder counter = new LongAdder();
counter.increment();  // Striped, минимум contention
long total = counter.sum();
```

**Когда:** много потоков, частые обновления.

---

## Thread States

```
NEW → start() → RUNNABLE
                    ↓
              BLOCKED (ждёт lock)
              WAITING (wait/join)
              TIMED_WAITING (sleep/timeout)
                    ↓
               TERMINATED
```

**Состояния потока:**
- **NEW** — поток создан (`new Thread()`), но `start()` ещё не вызван
- **RUNNABLE** — поток выполняется или готов к выполнению (ждёт CPU)
- **BLOCKED** — ждёт захвата монитора (другой поток держит `synchronized`)
- **WAITING** — ждёт бесконечно: `Object.wait()`, `Thread.join()`, `LockSupport.park()`
- **TIMED_WAITING** — ждёт с таймаутом: `sleep(ms)`, `wait(ms)`, `join(ms)`
- **TERMINATED** — поток завершился (нормально или с исключением)

---

## Deadlock

```java
// Thread 1: lock(A) → lock(B)
// Thread 2: lock(B) → lock(A)
// → Deadlock!
```

**Решение:** всегда брать locks в одинаковом порядке.

---

## Platform vs Virtual Threads

| | Platform | Virtual (Java 21+) |
|---|----------|-------------------|
| **Природа** | 1:1 с OS thread | M:N, lightweight |
| **Создание** | ~1ms, ~1MB stack | ~μs, ~KB stack |
| **Количество** | Тысячи | Миллионы |
| **Блокировка** | Блокирует OS thread | Автоматически unmount |
| **Когда** | CPU-bound | I/O-bound |

```java
// Platform thread
Thread.ofPlatform().start(() -> cpuWork());

// Virtual thread (Java 21+)
Thread.ofVirtual().start(() -> ioWork());
```

---

## Quick Reference

| Проблема | Решение |
|----------|---------|
| Visibility | volatile, synchronized |
| Atomicity | synchronized, Atomic* |
| Race condition | synchronized, CAS |
| Deadlock | Lock ordering, tryLock |
| Thread coordination | wait/notify, CountDownLatch |
| Producer-consumer | BlockingQueue |

---

## Детальные топики

- [[jvm-synchronization]] — synchronized, volatile, Atomic, locks детально
- [[jvm-concurrent-collections]] — ConcurrentHashMap, BlockingQueue, CopyOnWrite
- [[jvm-executors-futures]] — ExecutorService, CompletableFuture
- [[java-modern-features]] — Virtual Threads

---

## Чеклист

```
□ Понимаю JMM и happens-before
□ Знаю volatile vs synchronized vs Atomic
□ Понимаю deadlock и как избежать
□ Использую ExecutorService вместо raw threads
□ Использую ConcurrentHashMap вместо synchronized Map
□ Знаю когда Virtual Threads (I/O) vs Platform (CPU)
```

---

## Кто использует и реальные примеры

| Компания | Как используют concurrency | Результаты |
|----------|---------------------------|------------|
| **Netflix** | Virtual Threads (JDK 21) для I/O | Потоки: 5000 → 200, тот же throughput |
| **Twitter/X** | Scala Futures, Finagle | Миллионы RPS |
| **Uber** | ExecutorService, CompletableFuture | Async микросервисы |
| **LinkedIn** | Kafka (concurrent consumers) | Миллиарды сообщений/день |

### Netflix Virtual Threads Case Study (2024)

```
До (Platform Threads):
- 5000 потоков в пуле
- Высокое потребление памяти (~1MB/thread)
- Сложная настройка pool size

После (Virtual Threads, JDK 21):
- ~200 carrier threads
- Миллионы virtual threads
- Автоматическое масштабирование

Результат: тот же throughput, меньше памяти, проще код
```

---

## Рекомендуемые источники

### Книги
- **"Java Concurrency in Practice"** — Brian Goetz, классика
- **"Effective Java"** — Bloch, главы про concurrency

### Статьи
- [JMM FAQ](https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html) — официальный FAQ
- [Baeldung Concurrency](https://www.baeldung.com/java-concurrency) — практические гайды
- [Netflix Virtual Threads](https://www.infoq.com/news/2024/08/netflix-performance-case-study/) — real-world case study

### Инструменты
- [ThreadMXBean](https://docs.oracle.com/javase/8/docs/api/java/lang/management/ThreadMXBean.html) — мониторинг потоков
- [VisualVM](https://visualvm.github.io/) — thread dumps, deadlock detection
- [async-profiler](https://github.com/async-profiler/async-profiler) — профилирование lock contention

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Threads = параллелизм" | Threads — **concurrency** (interleaving). Parallelism требует несколько CPU cores |
| "Больше threads = быстрее" | После N_cores потоков — **contention**, context switching overhead. Закон Амдала |
| "Virtual Threads заменят всё" | Virtual Threads для **I/O-bound** задач. CPU-bound по-прежнему требуют Platform Threads |
| "synchronized устарел" | synchronized **оптимизирован** в Java 6+. Для простых случаев проще ReentrantLock |
| "Future.get() блокирует — это плохо" | Блокирование **нормально** если в правильном контексте. CompletableFuture для async chains |

---

## CS-фундамент

| CS-концепция | Применение в JVM Concurrency |
|--------------|------------------------------|
| **Concurrency vs Parallelism** | Concurrency = структура (interleaving), Parallelism = execution (simultaneous) |
| **Thread Safety** | Корректное поведение при concurrent access. Immutability, synchronization, atomic ops |
| **Memory Model** | JMM: happens-before, visibility, ordering. Основа корректной многопоточности |
| **Lock-free Programming** | CAS-based algorithms. ConcurrentHashMap, AtomicInteger. Прогресс без locks |
| **Fork-Join Model** | Divide and conquer. ForkJoinPool для recursive parallelism (parallel streams) |

---

*Проверено: 2026-01-09 | Источники: Netflix Tech Blog, Oracle docs, Baeldung — Педагогический контент проверен*
