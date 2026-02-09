---
title: "JVM Synchronization: synchronized, volatile, atomic"
created: 2025-11-25
modified: 2026-01-03
tags:
  - jvm
  - concurrency
  - synchronized
  - volatile
  - atomic
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-concurrent-collections]]"
---

# JVM Synchronization: синхронизация потоков

> **TL;DR:** `synchronized` = mutual exclusion + visibility (блокирует поток). `volatile` = visibility без блокировки (флаги, one-writer). `Atomic*` = lock-free через CAS (счётчики). `LongAdder` = 100x быстрее AtomicLong при high contention. `ReentrantLock` = tryLock с таймаутом для предотвращения deadlock.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| JVM многопоточность | Общая картина concurrency | [[jvm-concurrency-overview]] |
| CPU cache и память | Почему нужна синхронизация | [[os-memory-management]] |
| OS синхронизация | Mutex, semaphore базовые концепции | [[os-synchronization]] |

---

`synchronized` блокирует монитор объекта для mutual exclusion. `volatile` гарантирует видимость между потоками без блокировки. `Atomic*` — атомарные операции через lock-free CAS (Compare-And-Swap). Каждый решает свою задачу с разными tradeoffs.

`counter++` на volatile — race condition (три операции: read-modify-write). synchronized блокирует все потоки, даже если они работают с разными данными. ReentrantLock даёт tryLock с таймаутом — предотвращает deadlock. LongAdder в 100 раз быстрее AtomicLong при высокой конкуренции. Неправильный примитив — баги или потерянная производительность.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Монитор (Monitor)** | Встроенная блокировка в каждом Java-объекте | Замок на двери |
| **Барьер памяти** | Инструкция CPU, гарантирующая порядок операций | "Финишная черта" — всё до неё завершено |
| **CAS** | Compare-And-Swap — атомарная проверка и замена | "Если цена ещё 100₽, покупаю" |
| **Reentrant** | Поток может захватить свою же блокировку повторно | Ключ от дома — можно зайти снова |
| **Contention** | Конкуренция потоков за один ресурс | Очередь за одним кассиром |
| **Striped** | Разделение на независимые сегменты | Много кассиров вместо одного |
| **ABA Problem** | Значение изменилось A→B→A, но CAS не заметил | Подмена одинаково выглядящих товаров |
| **Fair Lock** | FIFO порядок для ожидающих потоков | Честная очередь — кто первый пришёл |

---

## synchronized: блокировка монитора

`synchronized` — самый старый и простой механизм синхронизации в Java. Он решает две задачи одновременно: mutual exclusion (только один поток выполняет код) и visibility (изменения видны другим потокам).

Почему это важно понимать вместе? Mutual exclusion без visibility бесполезен. Если поток A изменил переменную внутри synchronized блока, но поток B видит старое значение — программа сломана. Java Memory Model гарантирует, что при выходе из synchronized все изменения сбрасываются в main memory, а при входе — читаются из main memory.

### Базовое использование

```java
public class Counter {
    private int count = 0;

    // Весь метод под lock
    public synchronized void increment() {
        count++;
    }

    // Блок — более гранулярно
    public void add(int n) {
        synchronized (this) {
            count += n;
        }
    }
}
```

### Монитор объекта

Каждый объект в Java имеет скрытую структуру — **монитор**. Это не что-то абстрактное; это реальные байты в header объекта (mark word), которые хранят информацию о блокировке.

Когда поток входит в synchronized:
1. JVM пытается установить ownership монитора в header объекта
2. Если монитор свободен — поток его захватывает
3. Если занят другим потоком — текущий поток переходит в BLOCKED состояние

```
Thread 1: synchronized(obj) { count++ }
Thread 2: synchronized(obj) {         ← BLOCKED (ждёт освобождения монитора)
          ...
          } ← получил lock после Thread 1
```

**Важно:** блокировка привязана к конкретному объекту, не к коду. `synchronized(objA)` и `synchronized(objB)` — это разные блокировки. Потоки могут выполнять их параллельно.

### Static synchronized

```java
// Lock на Class объект
public static synchronized void staticMethod() {
    // SharedResource.class как monitor
}

// Эквивалент
public static void staticMethod() {
    synchronized (SharedResource.class) { }
}
```

### Reentrant (повторный вход)

Монитор в Java — reentrant. Это значит, что поток может захватить монитор, который он уже держит. JVM ведёт счётчик захватов для каждого монитора.

```java
public synchronized void outer() {
    inner();  // OK — счётчик становится 2
}

public synchronized void inner() {
    // Тот же поток уже держит lock — счётчик 2
}  // счётчик становится 1

// } из outer() — счётчик становится 0, монитор освобождён
```

Почему это важно? Без reentrant поток бы заблокировался сам на себе при вызове `inner()` из `outer()`. Это привело бы к deadlock в самых простых случаях рекурсии или композиции методов.

---

## volatile: видимость без блокировки

`volatile` решает проблему, о которой многие не знают: переменная, записанная одним потоком, может быть невидима для другого потока бесконечно долго.

### Проблема visibility

Каждое ядро CPU имеет свой кэш. Когда поток записывает значение в переменную, оно попадает в кэш ядра, но не обязательно в main memory. Другой поток на другом ядре читает из своего кэша — и видит старое значение.

Без каких-либо синхронизационных механизмов JVM вправе оптимизировать код так, что изменения вообще никогда не попадут в main memory. Это не баг — это оптимизация. JMM (Java Memory Model) явно разрешает такое поведение для non-volatile переменных.

### Гарантии volatile

1. **Видимость** — запись в volatile переменную сбрасывает кэши, чтение — обновляет из main memory
2. **Запрет reordering** — компилятор и CPU не могут переупорядочить операции через volatile
3. **НЕ атомарность** — `volatile int++` всё ещё три операции: read, increment, write

```java
private volatile boolean ready = false;
private int data = 0;

// Writer
data = 42;
ready = true;  // volatile write — барьер памяти

// Reader
if (ready) {           // volatile read — барьер памяти
    print(data);       // Гарантированно 42, не 0
}
```

Без volatile компилятор мог бы переставить `data = 42` и `ready = true` местами. Или reader мог бы увидеть `ready = true`, но `data` ещё не видеть как 42.

### Memory Barriers

Барьеры памяти — инструкции CPU, запрещающие переупорядочивание операций:

- **StoreStore** — все записи до барьера завершатся до записей после
- **StoreLoad** — все записи до барьера видны перед чтениями после (самый дорогой)
- **LoadLoad** — все чтения до барьера завершатся до чтений после
- **LoadStore** — все чтения до барьера завершатся до записей после

```
volatile write:
    data = 42         ← обычная запись
    [StoreStore]      ← барьер: data записан до ready
    ready = true      ← volatile
    [StoreLoad]       ← барьер: flush в main memory

volatile read:
    r = ready         ← volatile
    [LoadLoad]        ← барьер: data читается после ready
    [LoadStore]
    value = data      ← обычное чтение
```

### Когда использовать

```java
// ✅ Флаг остановки
private volatile boolean shutdown = false;

// ✅ One writer, many readers
private volatile Config currentConfig;

// ❌ Счётчик (не атомарно!)
private volatile int counter;
counter++;  // read → increment → write — race!

// ✅ Fix: AtomicInteger
private AtomicInteger counter = new AtomicInteger();
counter.incrementAndGet();
```

### Стоимость

```
Non-volatile write:  ~1 cycle
volatile write:      ~40-100 cycles (mfence на x86)

Причина: cache invalidation на всех CPU cores
```

---

## Atomic: Lock-Free операции

Atomic классы решают проблему, которую не решает volatile: атомарные read-modify-write операции. `volatile int++` — это три операции (read, increment, write), между которыми другой поток может вклиниться.

### Почему блокировка не всегда лучший выбор

`synchronized` и `ReentrantLock` работают, но имеют фундаментальный недостаток: заблокированные потоки ничего не делают. Если поток A захватил lock и был preempted операционной системой — все остальные потоки стоят и ждут.

Lock-free алгоритмы гарантируют, что хотя бы один поток всегда делает прогресс. Если поток A был preempted — поток B продолжает работать.

### Compare-And-Swap (CAS)

CAS — фундаментальная операция lock-free программирования. Она атомарно проверяет значение и меняет его, только если оно не изменилось.

```
CAS(memory, expected, new):
    if (*memory == expected)
        *memory = new
        return true
    else
        return false

// Одна атомарная CPU инструкция (CMPXCHG на x86)
```

Ключевое слово — *атомарная*. Между проверкой и записью никто не может вклиниться. Это гарантирует железо.

### AtomicInteger

```java
AtomicInteger counter = new AtomicInteger(0);

counter.incrementAndGet();     // ++counter
counter.getAndIncrement();     // counter++
counter.addAndGet(5);          // counter += 5
counter.compareAndSet(10, 20); // if (counter == 10) counter = 20
```

**Как работает внутри:**

```java
public int incrementAndGet() {
    for (;;) {  // retry loop — "optimistic locking"
        int current = get();
        int next = current + 1;
        if (compareAndSet(current, next))
            return next;
        // CAS failed — кто-то изменил значение, пробуем снова
    }
}
```

В низко-конкурентных сценариях CAS почти всегда успешен с первой попытки. В высоко-конкурентных — может быть много retries, что нивелирует преимущество.

### AtomicReference

```java
AtomicReference<User> currentUser = new AtomicReference<>();
currentUser.set(new User("Alice"));
currentUser.compareAndSet(oldUser, newUser);
```

### LongAdder — решение для высокого contention

AtomicLong с CAS отлично работает при низкой конкуренции. Но что происходит при 1000 потоках? Каждый поток делает CAS, но успевает только один за раз. 999 потоков получают failure и retry. И снова успевает только один. CPU тратит циклы на бесполезные попытки.

LongAdder решает эту проблему архитектурно: вместо одного счётчика — массив ячеек (cells). Каждый поток пишет в свою ячейку, конфликтов почти нет. Когда нужен результат — суммируем все ячейки.

```java
// AtomicLong: все потоки бьются за один адрес
AtomicLong counter = new AtomicLong();
// 1000 threads → lock cmpxchg [counter] ← все толпятся

// LongAdder: striped counters
LongAdder counter = new LongAdder();
// Thread 1 → cells[0].add(1)
// Thread 2 → cells[1].add(1)  ← параллельно!
// ...
long total = counter.sum();  // сумма всех cells
```

**Цена:** `sum()` не атомарен — пока вы суммируете, кто-то может добавить в ячейку. Для точных счётчиков с мгновенным чтением LongAdder не подходит. Но для метрик (requests/second, bytes transferred) — идеален.

**Benchmark:**
```
AtomicLong  (1000 threads):  ~5M ops/sec
LongAdder   (1000 threads):  ~500M ops/sec — 100× быстрее
```

### ABA Problem

CAS проверяет только значение, не историю. Это создаёт неочевидную проблему.

```
Thread 1: читает A, собирается сделать CAS(A, C)
Thread 2: меняет A → B
Thread 2: меняет B → A (вернул как было)
Thread 1: CAS(A, C) SUCCESS — но A уже "другой"!
```

На примитивах (int, long) это редко проблема. Но на указателях — катастрофа. Представьте lock-free stack:
- Thread 1 читает head = A, next = B, собирается сделать pop
- Thread 2 делает pop A, pop B, push A (переиспользует память A)
- Thread 1 делает CAS(head, A → B) — успех, но B уже не в стеке!

**Решение: AtomicStampedReference** — добавляет версию (stamp). CAS проверяет и значение, и версию.

```java
AtomicStampedReference<Node> ref = new AtomicStampedReference<>(node, 0);
// stamp увеличивается при каждом изменении
ref.compareAndSet(expected, newNode, expectedStamp, newStamp);
```

---

## ReentrantLock: явный контроль над блокировкой

`synchronized` прост, но негибок. Вы не можете отменить ожидание блокировки, не можете узнать, свободна ли она, не можете дать приоритет долго ждущим потокам.

`ReentrantLock` — это тот же монитор, но с API для тонкого контроля.

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    // critical section
} finally {
    lock.unlock();  // ОБЯЗАТЕЛЬНО в finally!
}
```

**Почему finally обязателен?** В отличие от synchronized, JVM не освободит ReentrantLock автоматически при выходе из блока. Забытый unlock — deadlock для всех, кто попытается захватить эту блокировку.

### Преимущества над synchronized

```java
// 1. tryLock — без блокировки
if (lock.tryLock()) {
    try { work(); }
    finally { lock.unlock(); }
} else {
    fallback();
}

// 2. Timeout
if (lock.tryLock(1, TimeUnit.SECONDS)) { ... }

// 3. Interruptible
lock.lockInterruptibly();  // можно прервать ожидание

// 4. Fair mode — FIFO
ReentrantLock fairLock = new ReentrantLock(true);
```

### ReadWriteLock — оптимизация для read-heavy нагрузки

Представьте кэш: 99% операций — чтение, 1% — обновление. С обычным lock все 99% readers ждут друг друга, хотя чтение не конфликтует с чтением.

`ReadWriteLock` разделяет блокировки:
- Read lock: много потоков могут держать одновременно
- Write lock: эксклюзивный, блокирует всех (и readers, и writers)

```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();

// Много readers одновременно — не блокируют друг друга
rwLock.readLock().lock();
try { return data; }
finally { rwLock.readLock().unlock(); }

// Writer ждёт, пока все readers закончат, потом блокирует всех
rwLock.writeLock().lock();
try { data = newValue; }
finally { rwLock.writeLock().unlock(); }
```

**Осторожно с writer starvation:** Если readers приходят постоянно, writer может ждать бесконечно. `ReentrantReadWriteLock(true)` использует fair ordering — writer получит приоритет после разумного ожидания.

---

## Deadlock

Deadlock — ситуация, когда два или более потоков вечно ждут друг друга. Каждый держит ресурс, который нужен другому, и ждёт ресурс, который держит другой.

### Четыре условия Coffman

Deadlock возможен только если выполняются ВСЕ четыре условия:
1. **Mutual exclusion** — ресурсы нельзя разделить
2. **Hold and wait** — поток держит ресурсы, ожидая другие
3. **No preemption** — ресурсы нельзя отобрать силой
4. **Circular wait** — циклическая зависимость

Разорвите любое — и deadlock невозможен.

### Классический пример

```java
// Thread 1
synchronized (lockA) {
    synchronized (lockB) { }  // ждёт lockB
}

// Thread 2
synchronized (lockB) {
    synchronized (lockA) { }  // ждёт lockA
}
// → Deadlock: Thread 1 держит A, ждёт B. Thread 2 держит B, ждёт A.
```

### Решения

**1. Lock ordering (разрывает circular wait):**

Если все потоки захватывают локи в одном порядке — циклической зависимости не возникнет.

```java
// Всегда сначала lockA, потом lockB — везде в программе
synchronized (lockA) {
    synchronized (lockB) { }
}
```

**2. tryLock с timeout (разрывает hold and wait):**

Если не удалось захватить второй lock — отпускаем первый и пробуем снова.

```java
if (lock1.tryLock(100, MILLISECONDS)) {
    try {
        if (lock2.tryLock(100, MILLISECONDS)) {
            try { work(); }
            finally { lock2.unlock(); }
        } else {
            // Не удалось — отпускаем lock1, пробуем позже
        }
    } finally { lock1.unlock(); }
}
```

**3. Один lock (разрывает circular wait):**

Простейшее решение — один глобальный lock. Нет нескольких локов — нет циклов.

```java
synchronized (singleLock) {
    // все операции с A и B
}
```

Цена — сниженный параллелизм. Но для многих приложений это приемлемо.

---

## Сравнение

| | synchronized | volatile | Atomic | ReentrantLock |
|---|-------------|----------|--------|---------------|
| **Mutual exclusion** | ✓ | ✗ | ✗ | ✓ |
| **Visibility** | ✓ | ✓ | ✓ | ✓ |
| **Atomicity** | ✓ | ✗ | ✓ (простые) | ✓ |
| **Blocking** | ✓ | ✗ | ✗ | ✓ |
| **tryLock** | ✗ | - | - | ✓ |
| **Fair mode** | ✗ | - | - | ✓ |

---

## Когда что

```
Простой флаг stop/ready     → volatile
Счётчик                     → AtomicInteger
Счётчик с high contention   → LongAdder
Критическая секция          → synchronized
Нужен tryLock/timeout       → ReentrantLock
Много readers, мало writers → ReadWriteLock
```

---

## Кто использует и реальные примеры

| Сценарий | Примитив | Реальные применения |
|----------|----------|---------------------|
| Флаг остановки | `volatile boolean` | Graceful shutdown в Spring, Netty |
| Метрики, счётчики | `LongAdder` | Prometheus Java client, Micrometer |
| Shared state | `synchronized` | Hibernate session, Spring transaction |
| Lock с timeout | `ReentrantLock` | Distributed lock fallback |
| Read-heavy cache | `ReadWriteLock` | Guava Cache, Caffeine |

### Benchmark: LongAdder vs AtomicLong

```
1000 threads, 10M increments:

AtomicLong:   ~5M ops/sec  (CAS contention)
LongAdder:    ~500M ops/sec (striped, 100x быстрее)

Когда использовать:
- AtomicLong: low contention, нужен точный get()
- LongAdder: high contention, метрики, sum() в конце
```

### Известные баги синхронизации

| Баг | Причина | Решение |
|-----|---------|---------|
| **Double-Checked Locking** (до Java 5) | Visibility без volatile | `volatile` на поле |
| **HashMap corruption** | Concurrent put без sync | `ConcurrentHashMap` |
| **Iterator ConcurrentModification** | Изменение во время итерации | `CopyOnWriteArrayList` или snapshot |

---

## Рекомендуемые источники

### Книги
- **"Java Concurrency in Practice"** — Brian Goetz, главы 3-5
- **"The Art of Multiprocessor Programming"** — Herlihy, Shavit — глубокая теория

### Статьи
- [JSR-133 FAQ](https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html) — JMM спецификация
- [Baeldung synchronized](https://www.baeldung.com/java-synchronized) — практический гайд
- [JMM in pictures](https://shipilev.net/blog/2014/jmm-pragmatics/) — Aleksey Shipilëv

### Инструменты
- [ThreadSanitizer](https://github.com/google/sanitizers) — поиск race conditions
- [JCStress](https://openjdk.org/projects/code-tools/jcstress/) — тестирование concurrency

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "volatile решает все проблемы синхронизации" | volatile обеспечивает только **visibility**, не atomicity. `count++` на volatile — race condition. Для compound operations нужен `synchronized` или `Atomic*` |
| "synchronized медленный, избегаю его" | В Java 6+ **biased locking** и lock coarsening сделали synchronized очень быстрым. Для uncontended lock — ~20ns. Premature optimization — корень зла |
| "Больше синхронизации = безопаснее" | Over-synchronization ведёт к **deadlock'ам** и **performance degradation**. Lock только минимально необходимый scope. Fine-grained locking лучше coarse-grained |
| "ReentrantLock всегда лучше synchronized" | ReentrantLock нужен для **специфических случаев**: tryLock, timeout, fairness. Для простых случаев synchronized проще и менее error-prone (авто-unlock в finally) |
| "AtomicLong быстрее всего для счётчиков" | При high contention **LongAdder в 100x быстрее** AtomicLong. CAS contention убивает AtomicLong. Для метрик/счётчиков — LongAdder |
| "Double-Checked Locking работает" | Работает **только с volatile** (Java 5+). Без volatile JMM позволяет видеть partially constructed object. Классический antipattern до Java 5 |
| "Синхронизация на String литерале безопасна" | String interning делает это **опасным**. Два модуля могут синхронизироваться на одном объекте. Синхронизируйся на private final Object lock |
| "Thread-safe класс = любые операции безопасны" | Отдельные операции безопасны, но **compound actions** — нет. `if (!map.containsKey(k)) map.put(k, v)` — race condition даже с ConcurrentHashMap |
| "volatile достаточно для флага остановки потока" | Для простого boolean флага — да. Но если есть **другие shared данные** связанные с флагом, нужна полная синхронизация всех данных |
| "Deadlock можно избежать добавлением timeout" | Timeout маскирует проблему, не решает. **Правильное решение**: lock ordering, lock hierarchy, или lock-free структуры данных |

---

## CS-фундамент

| CS-концепция | Применение в JVM Synchronization |
|--------------|----------------------------------|
| **Memory Visibility** | CPU кэши создают иллюзию несогласованности памяти. volatile и synchronized обеспечивают visibility через memory barriers (fences) |
| **Happens-Before Relationship** | JMM определяет happens-before для гарантий порядка операций. Release от lock happens-before acquire того же lock'а другим потоком |
| **Compare-And-Swap (CAS)** | Hardware primitive для atomic operations. `AtomicInteger.compareAndSet()` компилируется в CMPXCHG instruction. Основа lock-free алгоритмов |
| **Mutual Exclusion (Mutex)** | `synchronized` — реализация mutex. Только один поток владеет lock'ом. Критическая секция защищена от concurrent access |
| **Deadlock Detection** | Циклическая зависимость locks. JVM может детектировать через `ThreadMXBean.findDeadlockedThreads()`. Решение: lock ordering или tryLock |
| **Lock-Free Data Structures** | AtomicReference, ConcurrentHashMap используют CAS вместо locks. Прогресс гарантирован даже если поток preempted |
| **False Sharing** | Разные переменные на одной cache line вызывают cache invalidation. `@Contended` (JDK 8+) добавляет padding. LongAdder использует striping |
| **Monitor Pattern** | synchronized реализует monitor: mutex + condition variable. `wait()/notify()` — condition variable часть. Классический паттерн из concurrent programming |
| **Linearizability** | Операции атомарных классов linearizable: выглядят как мгновенные, в каком-то порядке. Сильнее чем sequential consistency |
| **Memory Model (JMM)** | Формальная спецификация what behaviors are allowed. Определяет когда записи одного потока видны другому. Основа корректной concurrent programming |

---

## Связи

- [[jvm-concurrency-overview]] — общая карта
- [[jvm-concurrent-collections]] — thread-safe коллекции
- [[jvm-executors-futures]] — высокоуровневые абстракции

---

*Проверено: 2026-01-09 | Источники: JCIP, Oracle docs, Baeldung — Педагогический контент проверен*
