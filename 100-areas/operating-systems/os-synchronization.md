---
title: "Синхронизация: координация параллельных процессов"
created: 2025-12-02
modified: 2025-12-02
type: deep-dive
status: published
area: operating-systems
confidence: high
tags:
  - topic/os
  - synchronization
  - concurrency
  - deadlock
  - type/deep-dive
  - level/intermediate
related:
  - "[[os-overview]]"
  - "[[os-processes-threads]]"
  - "[[os-scheduling]]"
  - "[[jvm-synchronization]]"
prerequisites:
  - "[[os-processes-threads]]"
  - "[[os-scheduling]]"
---

# Синхронизация: координация параллельных процессов

Когда несколько потоков или процессов обращаются к общим данным, возникает проблема координации. Без синхронизации результат зависит от непредсказуемого порядка выполнения (race condition). Примитивы синхронизации — mutex, semaphore, condition variable — позволяют потокам координировать доступ к общим ресурсам. Но неправильное использование ведёт к deadlock — взаимной блокировке, когда никто не может продолжить.

---

## TL;DR

> **Проблема:** Два потока одновременно делают `counter++` → результат непредсказуем (race condition).
>
> **Решение — примитивы синхронизации:**
> - **Mutex** — "замок" на ресурс. Только один поток может владеть.
> - **Semaphore** — "парковка на N мест". Ограничивает количество параллельных потоков.
> - **Condition Variable** — "звонок" для пробуждения ждущих потоков.
>
> **Deadlock:** A держит lock1, ждёт lock2. B держит lock2, ждёт lock1. → Оба ждут вечно.
>
> **4 условия Coffman:** Mutual Exclusion + Hold & Wait + No Preemption + Circular Wait = Deadlock.
>
> **Решение deadlock:** Lock ordering (всегда захватывать в одном порядке), trylock с таймаутом.

---

## Часть 1: Интуиция без кода

### 🚪 Аналогия 1: Ванная комната (Mutex)

**Mutex** — это как **замок на двери ванной комнаты**:

- **lock()** = войти в ванную и запереть дверь
- **unlock()** = выйти и освободить замок
- Если занято → ждёшь в очереди у двери

```
Без mutex (race condition):
┌─────────────────────────────────────────────────────────┐
│              Ванная комната                              │
│     ┌─────────────────────────────────────────┐         │
│     │  😨 Том     😱 Джерри                    │         │
│     │     одновременно!                        │         │
│     └─────────────────────────────────────────┘         │
│              (КАТАСТРОФА!)                               │
└─────────────────────────────────────────────────────────┘

С mutex:
┌─────────────────────────────────────────────────────────┐
│              Ванная комната                              │
│     ┌─────────────────────────────────────────┐         │
│     │  🚿 Том (внутри, замок закрыт)          │         │
│     └─────────────────────────────────────────┘         │
│              🔒 [ЗАНЯТО]                                 │
│     😴 Джерри (ждёт снаружи)                             │
└─────────────────────────────────────────────────────────┘
```

**Важное свойство:** Только тот, кто закрыл замок, может его открыть. Это **ownership** mutex.

### 🅿️ Аналогия 2: Парковка (Semaphore)

**Semaphore(N)** — это как **парковка на N мест**:

- **wait()/P()** = въехать, занять место (counter--)
- **signal()/V()** = выехать, освободить место (counter++)
- Если мест нет (counter == 0) → ждёшь на въезде

```
Semaphore(3) — парковка на 3 места:

Изначально:  [🅿️] [🅿️] [🅿️]  counter = 3

wait(): 🚗 въезжает
         [🚗] [🅿️] [🅿️]  counter = 2

wait(): 🚙 въезжает
         [🚗] [🚙] [🅿️]  counter = 1

wait(): 🚕 въезжает
         [🚗] [🚙] [🚕]  counter = 0

wait(): 🚐 хочет въехать → ЖДЁТ (counter = 0)

signal(): 🚗 уехал
         [🅿️] [🚙] [🚕]  counter = 1
         → 🚐 въезжает!
```

**Mutex vs Semaphore:**
- **Mutex = Semaphore(1)** с ownership
- **Semaphore** — без ownership (любой поток может signal)

### 🔔 Аналогия 3: Колокольчик (Condition Variable)

**Condition Variable** — это как **колокольчик в приёмной врача**:

- **wait()** = сесть и ждать звонка (отпустить mutex!)
- **signal()** = звякнуть колокольчиком (разбудить одного)
- **broadcast()** = громко позвать (разбудить всех)

```
Без condition variable (busy waiting):
while (queue.empty()) {
    // 🔁 Крутимся в цикле, тратим CPU
    // "Готово? Нет. Готово? Нет. Готово? Нет."
}

С condition variable:
mutex.lock()
while (queue.empty()) {
    cond.wait(mutex);  // 😴 Спим, ждём звонка
    // Просыпаемся только когда позвонят!
}
process(queue.pop())
mutex.unlock()
```

**Producer-Consumer с колокольчиком:**
```
Producer:                         Consumer:
mutex.lock()                      mutex.lock()
queue.push(item)                  while (queue.empty())
cond.signal()  ← ЗВОНОК 🔔           cond.wait(mutex) ← 😴
mutex.unlock()                    item = queue.pop()
                                  mutex.unlock()
```

### 🚗 Аналогия 4: Узкий мост (Deadlock)

**Deadlock** — это когда **два автомобиля застряли на узком мосту**:

```
Мост позволяет проехать только одному

         🚗 A → [========= МОСТ =========] ← 🚙 B
                       ↑
                   Застряли!
         A ждёт, пока B освободит мост
         B ждёт, пока A освободит мост
         → Никто не движется = DEADLOCK
```

**В терминах locks:**
```
Thread A:                Thread B:
lock(mutex1)            lock(mutex2)
// держит mutex1         // держит mutex2
lock(mutex2)  ← ЖДЁТ     lock(mutex1)  ← ЖДЁТ
// хочет mutex2          // хочет mutex1

A ждёт mutex2 (который у B)
B ждёт mutex1 (который у A)
→ DEADLOCK!
```

### 🍽️ Аналогия 5: Обедающие философы (классическая проблема)

5 философов сидят за круглым столом. Между каждыми двумя лежит одна вилка. Чтобы есть, нужны 2 вилки.

```
         🍽️
      🧠    🧠
    🍽️        🍽️
      🧠    🧠
         🍽️
    5 философов, 5 вилок

Проблема:
1. Все берут левую вилку одновременно
2. Все ждут правую вилку
3. Никто не может есть = DEADLOCK

Решения:
1. Не все берут левую первой (нарушить симметрию)
2. Брать обе вилки атомарно (mutex)
3. Отпустить, если не получилось (timeout)
```

### 🔢 Численная интуиция

| Операция | Время | Сравнение |
|----------|-------|-----------|
| Spinlock (нет contention) | ~10-20 ns | Проверить ручку двери |
| Mutex lock (нет contention) | ~25-50 ns | Повернуть ключ |
| Mutex lock (contention) | ~1-10 µs | Ждать в очереди |
| Condition wait | ~1-5 µs | Сесть и дремать |
| Syscall (futex) | ~200 ns - 1 µs | Позвать охранника |

**Когда что использовать:**
```
Критическая секция < 1µs → Spinlock (busy wait дешевле syscall)
Критическая секция > 10µs → Mutex (не тратить CPU на spin)
Ожидание события → Condition Variable (не делать busy wait)
Ограничение параллельности → Semaphore
```

**Правило:** Если под lock'ом работа > времени context switch (~5µs), используй mutex, не spinlock.

---

## Часть 2: Почему это сложно

### ❌ Ошибка 1: Забыть unlock (оставить дверь запертой)

**СИМПТОМ:** Deadlock — другие потоки вечно ждут.

**ПОЧЕМУ ВОЗНИКАЕТ:** Exception, ранний return, сложная логика ветвления.

**КАК ПРОЯВЛЯЕТСЯ:**
```c
void bad_function() {
    mutex.lock();

    if (error_condition) {
        return;  // ❌ mutex остаётся залоченным!
    }

    // ... код ...

    mutex.unlock();  // Никогда не достигнем при error
}
```

**РЕШЕНИЕ — RAII (Resource Acquisition Is Initialization):**
```cpp
// C++ — lock_guard автоматически unlock при выходе из scope
void good_function() {
    std::lock_guard<std::mutex> guard(mutex);

    if (error_condition) {
        return;  // ✅ guard.~lock_guard() вызовет unlock()
    }
}

// Java — try-with-resources / synchronized
synchronized (lock) {
    // unlock гарантирован даже при exception
}

// Kotlin — withLock extension
mutex.withLock {
    // unlock гарантирован
}
```

---

### ❌ Ошибка 2: Неправильный порядок lock'ов (deadlock)

**СИМПТОМ:** Программа "зависает" под нагрузкой.

**ПОЧЕМУ ВОЗНИКАЕТ:** Разные потоки захватывают locks в разном порядке.

**КЛАССИЧЕСКИЙ ПРИМЕР:**
```java
// Thread A:                    // Thread B:
transfer(alice, bob, 100) {     transfer(bob, alice, 50) {
    lock(alice.mutex);              lock(bob.mutex);    // ← разный
    lock(bob.mutex);                lock(alice.mutex);  // ← порядок!
    // ...                          // ...
}                               }

// Thread A держит alice, ждёт bob
// Thread B держит bob, ждёт alice
// → DEADLOCK!
```

**РЕШЕНИЕ — Lock Ordering:**
```java
void transfer(Account from, Account to, int amount) {
    // Всегда захватывать в порядке возрастания id
    Account first = from.id < to.id ? from : to;
    Account second = from.id < to.id ? to : from;

    synchronized (first) {
        synchronized (second) {
            // Теперь порядок всегда одинаковый!
            // transfer(alice, bob) и transfer(bob, alice)
            // оба захватят в порядке alice → bob (если alice.id < bob.id)
        }
    }
}
```

---

### ❌ Ошибка 3: Spurious wakeup (ложное пробуждение)

**СИМПТОМ:** Код после wait() выполняется, хотя условие не выполнено.

**ПОЧЕМУ ВОЗНИКАЕТ:** Спецификация condition variables разрешает "ложные пробуждения" (spurious wakeups).

**НЕПРАВИЛЬНО:**
```c
mutex.lock()
if (queue.empty()) {      // ❌ if вместо while
    cond.wait(mutex);     // Проснулись... но очередь может быть пуста!
}
item = queue.pop();       // 💥 CRASH! Очередь пуста
mutex.unlock()
```

**ПРАВИЛЬНО:**
```c
mutex.lock()
while (queue.empty()) {   // ✅ while проверяет после каждого пробуждения
    cond.wait(mutex);
}
item = queue.pop();       // Гарантировано не пустая
mutex.unlock()
```

**Почему while:**
1. Spurious wakeup (ОС может разбудить без signal)
2. Другой поток мог забрать элемент между signal и пробуждением
3. broadcast() разбудил всех, но элемент только один

---

### ❌ Ошибка 4: Lock contention (слишком широкий lock)

**СИМПТОМ:** Многопоточная программа работает как однопоточная.

**ПОЧЕМУ ВОЗНИКАЕТ:** Один большой lock на всю структуру данных.

**ПРИМЕР:**
```java
// ❌ Плохо: один lock на всю HashMap
class BadCache {
    private Map<String, Object> cache = new HashMap<>();
    private Object lock = new Object();

    public Object get(String key) {
        synchronized (lock) {  // ВСЕ потоки ждут
            return cache.get(key);
        }
    }

    public void put(String key, Object value) {
        synchronized (lock) {  // ВСЕ потоки ждут
            cache.put(key, value);
        }
    }
}
// 100 потоков → эффективно 1 поток работает
```

**РЕШЕНИЕ — Fine-grained locking или lock-free:**
```java
// ✅ Хорошо: ConcurrentHashMap с сегментами
class GoodCache {
    private ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();

    public Object get(String key) {
        return cache.get(key);  // Много потоков могут читать одновременно
    }

    public void put(String key, Object value) {
        cache.put(key, value);  // Lock только на сегмент
    }
}
```

---

### ❌ Ошибка 5: Использование notify() вместо notifyAll()

**СИМПТОМ:** Некоторые потоки никогда не просыпаются.

**ПОЧЕМУ ВОЗНИКАЕТ:** notify() будит только один поток, который может не соответствовать условию.

**ПРИМЕР:**
```java
// Producer-Consumer с разными условиями
// Producers ждут: while (queue.full()) wait()
// Consumers ждут: while (queue.empty()) wait()

// Producer кладёт элемент и делает notify()
// Но notify() будит случайный поток!
// Если разбудил producer (вместо consumer) →
// → Producer снова засыпает (queue всё ещё full)
// → Consumer не разбужен, хотя элемент есть
// → СИСТЕМА ОСТАНОВИЛАСЬ!
```

**РЕШЕНИЕ:**
```java
// Вариант 1: Всегда notifyAll()
notifyAll();  // Все проснутся и проверят своё условие

// Вариант 2: Разные condition variables
Condition notFull = lock.newCondition();   // Для producers
Condition notEmpty = lock.newCondition();  // Для consumers

// Producer:
notEmpty.signal();  // Будит только consumers

// Consumer:
notFull.signal();   // Будит только producers
```

---

### ❌ Ошибка 6: Double-checked locking (без volatile)

**СИМПТОМ:** Singleton иногда null, хотя уже создан.

**ПОЧЕМУ ВОЗНИКАЕТ:** Compiler/CPU может переупорядочить инструкции (reordering).

**КЛАССИЧЕСКИЙ BROKEN PATTERN:**
```java
class Singleton {
    private static Singleton instance;  // ❌ Нет volatile!

    public static Singleton getInstance() {
        if (instance == null) {           // Check 1 (без lock)
            synchronized (Singleton.class) {
                if (instance == null) {   // Check 2 (с lock)
                    instance = new Singleton();  // ← ПРОБЛЕМА!
                }
            }
        }
        return instance;
    }
}

// Проблема: instance = new Singleton() это:
// 1. Выделить память
// 2. Вызвать конструктор
// 3. Присвоить ссылку в instance
//
// Компилятор может переупорядочить: 1 → 3 → 2
// Другой поток видит instance != null
// Но объект ещё не инициализирован! 💥
```

**РЕШЕНИЕ:**
```java
// Вариант 1: volatile
private static volatile Singleton instance;  // ✅

// Вариант 2: Initialization-on-demand holder (лучше!)
class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // Ленивая, потокобезопасная
    }
}
```

---

## Часть 3: Ментальные модели

### 🧠 Модель 1: "4 условия Coffman для Deadlock"

```
Deadlock возникает ТОЛЬКО если ВСЕ 4 условия истинны:

┌─────────────────────────────────────────────────────────────┐
│ 1. MUTUAL EXCLUSION                                          │
│    Ресурс используется только одним потоком                  │
│    (нельзя поделиться)                                       │
├─────────────────────────────────────────────────────────────┤
│ 2. HOLD AND WAIT                                             │
│    Поток держит ресурс И ждёт другой                         │
│    (не отпускает имеющееся)                                  │
├─────────────────────────────────────────────────────────────┤
│ 3. NO PREEMPTION                                             │
│    Ресурс нельзя отобрать у потока                           │
│    (только добровольный release)                             │
├─────────────────────────────────────────────────────────────┤
│ 4. CIRCULAR WAIT                                             │
│    A ждёт B, B ждёт C, C ждёт A                               │
│    (цикл ожидания)                                           │
└─────────────────────────────────────────────────────────────┘

РАЗОРВИ ЛЮБОЕ условие → deadlock невозможен

Практические решения:
1. Lock ordering → нарушает Circular Wait
2. Timeout/trylock → нарушает Hold and Wait
3. Захватывать все locks атомарно → нарушает Hold and Wait
```

### 🧠 Модель 2: "Happens-Before и Memory Model"

```
Проблема: CPU и компилятор переупорядочивают инструкции

Код:                  Реальное выполнение:
x = 1;                y = 1;  // ← Переставлены!
y = 1;                x = 1;

Без синхронизации нет гарантий порядка!

Happens-Before гарантии:
┌─────────────────────────────────────────────────────────────┐
│ unlock(m) ───────────────────▶ lock(m)                      │
│   (всё до unlock видно после lock)                          │
├─────────────────────────────────────────────────────────────┤
│ volatile write ──────────────▶ volatile read                │
│   (запись видна после чтения)                               │
├─────────────────────────────────────────────────────────────┤
│ thread.start() ──────────────▶ первая инструкция потока     │
├─────────────────────────────────────────────────────────────┤
│ последняя инструкция ────────▶ thread.join() возвращается   │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Модель 3: "Таблица выбора примитива"

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ВЫБОР ПРИМИТИВА СИНХРОНИЗАЦИИ                      │
├───────────────────┬──────────────┬──────────────┬──────────────────────┤
│ Сценарий          │ Примитив     │ Альтернатива │ Пример               │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Защита данных     │ Mutex        │ RWLock       │ counter++            │
│ (1 поток)         │              │              │                      │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Много читателей   │ RWLock       │ Lock-free    │ config, cache        │
│ мало писателей    │              │              │                      │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Ограничить        │ Semaphore(N) │ ThreadPool   │ max 10 connections   │
│ параллельность    │              │              │                      │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Ждать событие     │ Condition    │ Future       │ producer-consumer    │
│                   │ Variable     │              │                      │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Короткая секция   │ Spinlock     │ Lock-free    │ критичный путь       │
│ (< 1µs)           │              │              │                      │
├───────────────────┼──────────────┼──────────────┼──────────────────────┤
│ Барьер (ждать     │ Barrier      │ CountDown    │ параллельные фазы    │
│ всех)             │              │ Latch        │                      │
└───────────────────┴──────────────┴──────────────┴──────────────────────┘
```

### 🧠 Модель 4: "Граф ожидания для обнаружения Deadlock"

```
Wait-For Graph: направленное ребро A→B означает "A ждёт ресурс, который держит B"

Нет deadlock:                 Есть deadlock:
    A → B → C                     A → B
        ↓                         ↑   ↓
        D                         D ← C

    (DAG — нет циклов)           (Цикл A→B→C→D→A)

Алгоритм обнаружения:
1. Построить граф ожидания
2. Найти цикл (DFS)
3. Если цикл есть → DEADLOCK

В реальных системах:
- Базы данных строят граф транзакций
- При обнаружении цикла → abort одной транзакции (victim)
```

### 🧠 Модель 5: "Иерархия примитивов синхронизации"

```
            Высокоуровневые (проще использовать)
                         ↑
┌─────────────────────────────────────────────────────────────┐
│  BlockingQueue, ConcurrentHashMap, Future, Actor            │
│  (готовые thread-safe структуры данных)                     │
├─────────────────────────────────────────────────────────────┤
│  Semaphore, Barrier, CountDownLatch, ReadWriteLock          │
│  (составные примитивы)                                      │
├─────────────────────────────────────────────────────────────┤
│  Mutex, Condition Variable                                  │
│  (базовые примитивы ОС)                                     │
├─────────────────────────────────────────────────────────────┤
│  Spinlock, Futex                                            │
│  (низкоуровневые примитивы)                                 │
├─────────────────────────────────────────────────────────────┤
│  Atomic operations (CAS, fetch-and-add)                     │
│  (CPU инструкции)                                           │
├─────────────────────────────────────────────────────────────┤
│  Memory barriers, cache coherence                           │
│  (hardware)                                                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
             Низкоуровневые (сложнее, эффективнее)

Правило: Используй самый высокоуровневый примитив,
         который решает твою задачу
```

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| [[os-processes-threads]] | Понимание потоков и разделяемой памяти — без этого синхронизация бессмысленна | Предыдущий материал раздела |
| [[os-overview]] | Базовые концепции ОС, syscalls, kernel mode | Предыдущий материал раздела |
| Race conditions интуитивно | Понимание почему `counter++` небезопасен | [Baeldung: Race Conditions](https://www.baeldung.com/cs/race-conditions) |
| Базовый C | Примеры на pthread | [Learn C](https://www.learn-c.org/) |

**Время на подготовку:** ~3-5 дней если уже понимаете потоки

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Race Condition** | Результат зависит от порядка выполнения потоков | Двое одновременно хватают последний кусок пиццы — кто успеет первым? |
| **Critical Section** | Код, работающий с общими данными | Ванная комната — только один может использовать |
| **Mutual Exclusion** | Гарантия "только один поток в критической секции" | Замок на двери ванной |
| **Mutex** | Механизм для mutual exclusion (lock/unlock) | Ключ от ванной: взял — никто не войдёт, положил — следующий может взять |
| **Semaphore** | Счётчик для ограничения параллельного доступа | Парковка на N мест: есть место — въезжаешь, нет — ждёшь |
| **Deadlock** | Взаимная блокировка — все ждут друг друга | Два автомобиля на узком мосту: никто не уступает, оба стоят |
| **Livelock** | Процессы активны, но не делают прогресс | Двое пытаются разойтись в коридоре: оба шагают в одну сторону бесконечно |
| **Starvation** | Процесс бесконечно ждёт ресурс (другие всегда успевают раньше) | Вежливый человек у двери: всё время пропускает других и никогда не входит |
| **Spinlock** | Активное ожидание (busy waiting) | Ждать у двери и постоянно дёргать ручку: "открыто? нет. открыто? нет." |
| **Condition Variable** | Механизм ожидания условия (signal/wait) | Колокольчик: жди, когда позвонят — не надо постоянно проверять |
| **Priority Inversion** | Низкоприоритетный блокирует высокоприоритетного | VIP ждёт, пока уборщик доделает работу в комнате |
| **Futex** | Fast userspace mutex — быстрый путь без syscall | Проверить дверь: если открыта — войти. Только если закрыта — звонить охраннику |

---

## Проблема: Race Condition

### Почему это происходит

Операция `counter++` выглядит атомарной, но на уровне CPU это три инструкции:

```assembly
mov eax, [counter]   ; 1. Прочитать counter в регистр
inc eax              ; 2. Увеличить регистр
mov [counter], eax   ; 3. Записать обратно
```

Если два потока выполняют это одновременно:

```
            Thread A              Thread B
            ────────              ────────
counter=0
            mov eax, [counter]
            eax_A = 0
                                  mov eax, [counter]
                                  eax_B = 0
            inc eax
            eax_A = 1
                                  inc eax
                                  eax_B = 1
            mov [counter], eax
counter=1
                                  mov [counter], eax
counter=1   ← Должно быть 2!
```

### Ещё пример: банковский перевод

```c
// Перевод с account1 на account2
void transfer(Account* from, Account* to, int amount) {
    if (from->balance >= amount) {
        from->balance -= amount;  // ← Между этими двумя строками
        to->balance += amount;    // ← может случиться прерывание
    }
}

// Два потока одновременно:
// Thread A: transfer(alice, bob, 100)
// Thread B: transfer(alice, charlie, 100)

// Alice.balance = 150
// Thread A: проверка 150 >= 100 ✓
// Thread B: проверка 150 >= 100 ✓
// Thread A: alice.balance = 50
// Thread B: alice.balance = 50 (не 150-100-100!)
// Результат: Alice потеряла только 100, хотя перевела 200
```

---

## Critical Section

### Требования к решению

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRITICAL SECTION PROBLEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  entry_section();     // Попытка войти                          │
│  // === CRITICAL SECTION ===                                    │
│  // Доступ к общим данным                                       │
│  exit_section();      // Выход                                  │
│  // remainder_section                                           │
│                                                                 │
│  Требования:                                                    │
│                                                                 │
│  1. Mutual Exclusion: В critical section максимум один поток    │
│                                                                 │
│  2. Progress: Если никто не в critical section и кто-то хочет   │
│     войти — решение должно быть принято за конечное время       │
│                                                                 │
│  3. Bounded Waiting: Ограниченное время ожидания (нет starvation)│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mutex (Mutual Exclusion)

### Концепция

Mutex — это "замок" на критическую секцию. Только один поток может владеть mutex в каждый момент.

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void* thread_function(void* arg) {
    pthread_mutex_lock(&lock);    // Захватить (блокирует если занят)

    // Critical section
    counter++;

    pthread_mutex_unlock(&lock);  // Освободить

    return NULL;
}
```

### Как работает внутри

```
pthread_mutex_lock(&lock):

1. Попытка атомарно установить lock = 1
   - Если lock был 0 (свободен) → успех, продолжить
   - Если lock был 1 (занят) → перейти в состояние blocked

2. Поток в состоянии blocked:
   - Убирается из ready queue
   - Добавляется в wait queue mutex'а
   - Context switch на другой поток

3. Когда владелец вызывает unlock:
   - Один поток из wait queue переносится в ready queue
   - Планировщик может его запустить
```

### Spinlock vs Mutex

**Spinlock:** Активное ожидание (busy waiting)

```c
while (lock == 1) {
    // Крутимся в цикле, тратим CPU
}
lock = 1;  // Захватили
```

**Когда spinlock лучше:** Если ожидание короткое (< context switch time). Переключение контекста дороже, чем покрутиться пару микросекунд. Используется в ядре для очень коротких критических секций.

**Когда mutex лучше:** Если ожидание долгое или неизвестное. Поток засыпает, не тратит CPU.

---

## Semaphore

### Концепция

Semaphore — это счётчик с двумя атомарными операциями:
- `wait()` (P, down): Уменьшить счётчик. Если <0, заблокироваться.
- `signal()` (V, up): Увеличить счётчик. Разбудить ждущий поток.

```c
// Binary semaphore (как mutex)
sem_t sem;
sem_init(&sem, 0, 1);  // Начальное значение = 1

sem_wait(&sem);    // Захватить (value: 1 → 0)
// Critical section
sem_post(&sem);    // Освободить (value: 0 → 1)

// Counting semaphore (ограничить N параллельных)
sem_t pool;
sem_init(&pool, 0, 5);  // Максимум 5 потоков одновременно

sem_wait(&pool);   // Взять из пула
// Использовать ресурс
sem_post(&pool);   // Вернуть в пул
```

### Применение: Producer-Consumer

```c
#define BUFFER_SIZE 10
int buffer[BUFFER_SIZE];
int in = 0, out = 0;

sem_t empty;  // Количество пустых слотов
sem_t full;   // Количество заполненных слотов
sem_t mutex;  // Защита buffer

void init() {
    sem_init(&empty, 0, BUFFER_SIZE);  // Все слоты пустые
    sem_init(&full, 0, 0);              // Ничего не заполнено
    sem_init(&mutex, 0, 1);
}

void* producer(void* arg) {
    while (1) {
        int item = produce();

        sem_wait(&empty);       // Ждать пустой слот
        sem_wait(&mutex);       // Захватить buffer

        buffer[in] = item;
        in = (in + 1) % BUFFER_SIZE;

        sem_post(&mutex);       // Освободить buffer
        sem_post(&full);        // Сигнал: есть данные
    }
}

void* consumer(void* arg) {
    while (1) {
        sem_wait(&full);        // Ждать данные
        sem_wait(&mutex);       // Захватить buffer

        int item = buffer[out];
        out = (out + 1) % BUFFER_SIZE;

        sem_post(&mutex);       // Освободить buffer
        sem_post(&empty);       // Сигнал: есть место

        consume(item);
    }
}
```

---

## Condition Variable

### Проблема

Mutex защищает данные, но не позволяет эффективно ждать условие:

```c
// Плохо: polling
while (1) {
    pthread_mutex_lock(&lock);
    if (condition_met) {
        // работаем
        pthread_mutex_unlock(&lock);
        break;
    }
    pthread_mutex_unlock(&lock);
    sleep(1);  // Тратим время или CPU
}
```

### Решение: Condition Variable

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int data_ready = 0;

// Ожидающий поток
void* waiter(void* arg) {
    pthread_mutex_lock(&lock);

    while (!data_ready) {  // Проверка условия в цикле!
        pthread_cond_wait(&cond, &lock);
        // wait() атомарно: unlock + sleep + lock при пробуждении
    }

    // Данные готовы, работаем
    process_data();

    pthread_mutex_unlock(&lock);
    return NULL;
}

// Сигнализирующий поток
void* signaler(void* arg) {
    pthread_mutex_lock(&lock);

    data_ready = 1;
    pthread_cond_signal(&cond);  // Разбудить одного ждущего
    // или pthread_cond_broadcast(&cond);  // Разбудить всех

    pthread_mutex_unlock(&lock);
    return NULL;
}
```

### Почему while, а не if?

**Spurious wakeup:** Поток может проснуться без signal (особенность реализации).

**Lost wakeup:** Signal мог прийти до wait.

**Изменившееся условие:** Пока поток просыпался, другой поток мог изменить условие.

```c
// НЕПРАВИЛЬНО
if (!data_ready) {
    pthread_cond_wait(&cond, &lock);
}
// После wakeup data_ready может быть снова false!

// ПРАВИЛЬНО
while (!data_ready) {
    pthread_cond_wait(&cond, &lock);
}
// Гарантированно data_ready == true
```

---

## Deadlock

### Четыре условия Coffman

Deadlock возможен только если выполняются **все четыре** условия:

1. **Mutual Exclusion:** Ресурс может держать только один процесс
2. **Hold and Wait:** Процесс держит ресурс и ждёт другой
3. **No Preemption:** Ресурс нельзя отобрать силой
4. **Circular Wait:** Цикл ожидания: A ждёт B, B ждёт C, C ждёт A

### Пример deadlock

```c
pthread_mutex_t lock_a, lock_b;

void* thread1(void* arg) {
    pthread_mutex_lock(&lock_a);
    sleep(1);  // Увеличиваем шанс deadlock
    pthread_mutex_lock(&lock_b);  // Ждёт lock_b

    // Critical section

    pthread_mutex_unlock(&lock_b);
    pthread_mutex_unlock(&lock_a);
}

void* thread2(void* arg) {
    pthread_mutex_lock(&lock_b);
    sleep(1);
    pthread_mutex_lock(&lock_a);  // Ждёт lock_a

    // Critical section

    pthread_mutex_unlock(&lock_a);
    pthread_mutex_unlock(&lock_b);
}

// Thread 1 держит A, ждёт B
// Thread 2 держит B, ждёт A
// → Deadlock!
```

### Стратегии предотвращения

**1. Lock Ordering (нарушить Circular Wait)**

Всегда захватывать locks в одном порядке:

```c
// Определить глобальный порядок: lock_a < lock_b

void* thread1(void* arg) {
    pthread_mutex_lock(&lock_a);  // Сначала A
    pthread_mutex_lock(&lock_b);  // Потом B
    // ...
}

void* thread2(void* arg) {
    pthread_mutex_lock(&lock_a);  // Тоже сначала A!
    pthread_mutex_lock(&lock_b);  // Потом B
    // ...
}

// Циклического ожидания быть не может
```

**2. trylock с таймаутом (нарушить Hold and Wait)**

```c
void safe_transfer() {
    while (1) {
        pthread_mutex_lock(&lock_a);

        if (pthread_mutex_trylock(&lock_b) == 0) {
            // Успех — оба захвачены
            break;
        }

        // Не удалось — освободить A и попробовать снова
        pthread_mutex_unlock(&lock_a);
        usleep(rand() % 1000);  // Random backoff
    }

    // Critical section

    pthread_mutex_unlock(&lock_b);
    pthread_mutex_unlock(&lock_a);
}
```

**3. Один lock (нарушить Hold and Wait)**

```c
// Самый простой способ — один глобальный lock
pthread_mutex_t global_lock;

void transfer(Account* from, Account* to, int amount) {
    pthread_mutex_lock(&global_lock);
    // Работаем с любыми accounts безопасно
    pthread_mutex_unlock(&global_lock);
}

// Минус: меньше параллелизма
```

### Обнаружение deadlock

Если предотвращение сложно, можно обнаруживать и recovery:

```
1. Построить граф ожидания (wait-for graph)
2. Искать циклы
3. При обнаружении — убить один из процессов

Граф ожидания:
  P1 → P2 (P1 ждёт ресурс от P2)
  P2 → P3
  P3 → P1 ← Цикл! Deadlock!
```

---

## Классические проблемы синхронизации

### Dining Philosophers (Обедающие философы)

5 философов сидят за круглым столом. Между каждыми двумя — одна вилка. Для еды нужны две вилки.

```
          P0
       🍴    🍴
     P4        P1
     🍴        🍴
       P3    P2
          🍴

Если каждый возьмёт левую вилку — deadlock!
```

**Решение — асимметрия:**
```c
void philosopher(int id) {
    if (id % 2 == 0) {
        // Чётные: сначала левую, потом правую
        pick_up(left_fork);
        pick_up(right_fork);
    } else {
        // Нечётные: сначала правую, потом левую
        pick_up(right_fork);
        pick_up(left_fork);
    }
    eat();
    put_down(left_fork);
    put_down(right_fork);
}
```

### Readers-Writers

Множество readers могут читать одновременно. Writer требует эксклюзивный доступ.

```c
pthread_rwlock_t rwlock;

void* reader(void* arg) {
    pthread_rwlock_rdlock(&rwlock);  // Shared lock
    // Чтение
    pthread_rwlock_unlock(&rwlock);
}

void* writer(void* arg) {
    pthread_rwlock_wrlock(&rwlock);  // Exclusive lock
    // Запись
    pthread_rwlock_unlock(&rwlock);
}
```

---

## Когда синхронизация НЕ нужна

Синхронизация добавляет сложность и overhead. Избегай её где возможно.

### Ситуации где синхронизация избыточна

**1. Immutable данные:**
- Если данные не меняются после создания — locks не нужны
- Пример: конфигурация, загруженная при старте

**2. Thread-local данные:**
- Данные принадлежат одному потоку → нет shared state
- Используй TLS или передавай данные в параметрах

**3. Single-threaded код:**
- Один поток = нет конкуренции
- Event loop архитектура (Node.js) избегает проблем синхронизации

**4. Lockless структуры данных:**
- Atomic операции вместо locks для простых случаев
- CAS (Compare-And-Swap) для счётчиков

### Признаки over-engineering синхронизации

| Симптом | Проблема |
|---------|----------|
| Lock на каждый метод | Слишком гранулярно, overhead |
| Вложенные locks | Риск deadlock растёт экспоненциально |
| Lock contention >20% | Дизайн требует пересмотра |
| synchronized(this) везде | Coarse-grained, блокирует всё |

---

## Реализация в ядре: Futex

**Futex (Fast Userspace muTEX)** — механизм Linux для эффективной синхронизации.

```
Идея: Быстрый путь в userspace, медленный путь через kernel

pthread_mutex_lock():

1. Атомарная проверка в userspace:
   atomic_compare_exchange(lock, 0, 1)

   Если успех → lock захвачен, НЕТ syscall!

2. Если lock занят → syscall futex(FUTEX_WAIT)
   Поток засыпает в kernel

pthread_mutex_unlock():

1. Атомарно: lock = 0

2. Если есть ждущие → syscall futex(FUTEX_WAKE)
   Разбудить ждущих
```

**Эффективность:** В случае отсутствия contention (lock свободен) — никакого syscall, только атомарная операция в userspace (~10-20 cycles).

---

## Связь с JVM

### synchronized

```java
synchronized (object) {
    // Critical section
}

// Компилируется в:
// monitorenter object
// ... critical section ...
// monitorexit object

// Под капотом: каждый объект имеет monitor (встроенный mutex)
```

### ReentrantLock

```java
Lock lock = new ReentrantLock();
lock.lock();
try {
    // Critical section
} finally {
    lock.unlock();
}
```

Подробнее — в [[jvm-synchronization]].

---

## Кто использует и реальные примеры

### Знаменитые баги из-за race conditions

| Инцидент | Что случилось | Причина |
|----------|---------------|---------|
| **Therac-25 (1985-1987)** | Смертельные дозы радиации пациентам | Race condition между UI и аппаратурой. Быстрый ввод оператора опережал систему |
| **Mars Pathfinder (1997)** | Rover перезагружался на Марсе | Priority inversion: низкоприоритетная задача держала mutex, высокоприоритетная ждала |
| **Northeast Blackout (2003)** | 55 млн человек без электричества | Race condition в alarm system — операторы не видели предупреждений |

### Инструменты для обнаружения race conditions

| Инструмент | Язык | Как использовать |
|------------|------|------------------|
| **ThreadSanitizer (TSan)** | C/C++, Go | `gcc -fsanitize=thread`, `go test -race` |
| **Helgrind** | C/C++ | Часть Valgrind: `valgrind --tool=helgrind ./program` |
| **Intel Inspector** | C/C++ | GUI для анализа threading bugs |
| **Java: jconsole/JMC** | Java | Мониторинг deadlocks в JVM |

### Практические паттерны синхронизации

| Паттерн | Когда использовать | Пример |
|---------|-------------------|--------|
| **Fine-grained locking** | Высокий параллелизм, разные части данных | HashMap с lock на каждый bucket (ConcurrentHashMap) |
| **Coarse-grained locking** | Простота важнее производительности | Один lock на всю структуру данных |
| **Read-Write Lock** | Много читателей, редкие писатели | Кэш, конфигурация |
| **Lock-free (CAS)** | Простые счётчики, очень высокая конкуренция | AtomicInteger, AtomicReference |
| **Immutable data** | Избегаем синхронизации вообще | Functional programming, event sourcing |

### Performance: lock vs lock-free

| Операция | Lock (mutex) | Lock-free (CAS) | Когда выбирать |
|----------|--------------|-----------------|----------------|
| Increment counter | ~50-100ns с contention | ~10-30ns | Lock-free для счётчиков |
| Complex update | Надёжно | Сложный retry loop | Lock для сложных операций |
| Low contention | ~20ns (futex fast path) | ~10ns | Разница минимальна |
| High contention | Деградация, очередь | Retry storms | Обе деградируют, пересмотреть дизайн |

### Рекомендации по дизайну

| Проблема | Плохой подход | Хороший подход |
|----------|---------------|----------------|
| Много данных | Один глобальный lock | Шардирование: lock на каждый шард |
| Read-heavy workload | Mutex на всё | ReadWriteLock или MVCC |
| Complex state machine | Много вложенных locks | Actor model, message passing |
| Distributed system | Distributed locks везде | Idempotency, optimistic locking |

---

## Проверь себя

<details>
<summary>1. Чем mutex отличается от semaphore?</summary>

**Ответ:** Mutex — бинарный (locked/unlocked), владелец должен освободить. Semaphore — счётчик, позволяет N потокам войти одновременно. Mutex для взаимоисключения, semaphore для ограничения параллелизма (например, пул соединений).

</details>

<details>
<summary>2. Назови 4 условия Coffman для deadlock</summary>

**Ответ:**
1. **Mutual Exclusion** — ресурс может использовать только один поток
2. **Hold and Wait** — поток держит ресурс и ждёт другой
3. **No Preemption** — ресурс нельзя отобрать силой
4. **Circular Wait** — цикл ожидания (A ждёт B, B ждёт A)

Убери любое — deadlock невозможен.

</details>

<details>
<summary>3. Почему spurious wakeup требует проверки условия в цикле?</summary>

**Ответ:** Condition variable может разбудить поток без signal (spurious wakeup). Если проверить условие только один раз (if), поток продолжит работу хотя условие не выполнено. Поэтому ВСЕГДА while(condition) вместо if(condition).

</details>

<details>
<summary>4. Что такое priority inversion и как его решить?</summary>

**Ответ:** Низкоприоритетный поток держит lock, высокоприоритетный ждёт. Средний поток вытесняет низкий → высокий ждёт дольше чем должен. Решения: priority inheritance (временно поднять приоритет держателя lock) или priority ceiling (lock имеет фиксированный высокий приоритет).

</details>

---

## Связь с другими темами

**[[os-overview]]** — Обзор ОС объясняет разделение kernel/user mode, которое критично для понимания синхронизации: когда поток блокируется на mutex, он совершает системный вызов (futex в Linux), переходит в kernel mode, и ядро помещает его в wait queue — это стоит ~1-2 µs. Атомарные операции (CAS, fetch-and-add), лежащие в основе lock-free алгоритмов, реализуются на уровне процессорных инструкций (CMPXCHG, LOCK prefix на x86) без перехода в kernel. Понимание interrupt handling также важно: критические секции ядра часто защищаются не mutex, а запретом прерываний (cli/sti), поскольку interrupt handler не может ждать на lock.

**[[os-processes-threads]]** — Потоки и синхронизация неразрывно связаны: именно потому, что потоки одного процесса разделяют адресное пространство, возникают race conditions при одновременном доступе к общим данным. Без понимания модели памяти потоков — stack приватный, heap и глобальные переменные общие — невозможно определить, какие данные требуют защиты. Каждый поток имеет собственный кэш процессора (L1/L2), и cache coherency protocol (MESI) обеспечивает видимость записей между ядрами, но с задержкой — именно это порождает необходимость memory barriers. Процессы, в отличие от потоков, имеют изолированные адресные пространства и синхронизируются через IPC-механизмы (named semaphores, shared memory + mutexes), что принципиально дороже.

**[[os-scheduling]]** — Планирование и синхронизация тесно взаимодействуют через несколько механизмов. Priority inversion — классическая проблема на стыке двух тем: высокоприоритетный поток T1 ждёт mutex, захваченный низкоприоритетным T3, а среднеприоритетный T2 вытесняет T3, косвенно блокируя T1 на неопределённое время. Решения (priority inheritance protocol, priority ceiling protocol) требуют, чтобы планировщик динамически изменял приоритеты на основе владения mutex. Выбор между spinlock и mutex зависит от scheduling: если ожидаемое время ожидания меньше стоимости context switch (~2 µs), spinlock эффективнее; если больше — mutex с перепланированием экономит CPU cycles.

**[[jvm-synchronization]]** — Синхронизация в JVM построена поверх примитивов ОС: synchronized блок использует monitor, который на уровне HotSpot реализован через biased locking → thin lock (CAS) → fat lock (OS mutex/futex) по мере возрастания contention. ReentrantLock из java.util.concurrent использует AbstractQueuedSynchronizer (AQS), который сочетает CAS-спин с park/unpark (futex на Linux). Volatile в Java генерирует memory barriers на уровне процессора (StoreLoad barrier на x86), гарантируя visibility без mutex — это прямая связь с аппаратными механизмами синхронизации. Понимание OS-уровня помогает диагностировать проблемы: lock contention в Java profiler (JFR) показывает время в состоянии BLOCKED, которое соответствует ожиданию на futex в ядре.

**Связанные концепции:**
- [[os-memory-management]] — memory barriers и cache coherency связаны с синхронизацией на низком уровне
- [[jvm-concurrency-overview]] — synchronized, ReentrantLock, volatile в JVM построены на этих примитивах
- [[kotlin-coroutines]] — Mutex в корутинах, structured concurrency как альтернатива locks

---

## Рекомендуемые источники

### Учебники

- Tanenbaum A., Bos H. (2014). *"Modern Operating Systems, 4th Edition."* — глава 2.3 (Interprocess Communication) и 6.1-6.4 (Deadlocks) — классическое изложение от race conditions через mutual exclusion до алгоритмов обнаружения и предотвращения deadlock; задача обедающих философов разобрана в деталях.
- Silberschatz A., Galvin P., Gagne G. (2018). *"Operating System Concepts, 10th Edition."* — главы 6 (Synchronization Tools) и 7 (Synchronization Examples) и 8 (Deadlocks) — формальные определения критических секций, Peterson's algorithm, семафоры Дейкстры и решения классических задач (bounded buffer, readers-writers, dining philosophers).
- Arpaci-Dusseau R., Arpaci-Dusseau A. (2018). *"Operating Systems: Three Easy Pieces."* — главы 26-33 (Concurrency) — от потоков и locks до condition variables и семафоров с практическими упражнениями и симуляторами; бесплатно, с отличными пошаговыми объяснениями.
- Bryant R., O'Hallaron D. (2015). *"Computer Systems: A Programmer's Perspective, 3rd Edition."* — глава 12 (Concurrent Programming) рассматривает синхронизацию с точки зрения программиста: thread safety, reentrant functions, races и deadlocks в контексте реального C-кода.
- Love R. (2010). *"Linux Kernel Development, 3rd Edition."* — главы 9 (An Introduction to Kernel Synchronization) и 10 (Kernel Synchronization Methods) — spinlocks, semaphores, completion variables, seq locks, RCU и preemption в контексте ядра Linux.

### Книги и курсы
- [OSTEP: Concurrency chapters](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf) — бесплатная книга, главы 26-33
- [MIT 6.S081: Locks lab](https://pdos.csail.mit.edu/6.1810/2025/) — практическая работа с locks в xv6

### Статьи и туториалы
- [Baeldung: Race Conditions](https://www.baeldung.com/cs/race-conditions) — отличное объяснение с примерами
- [GeeksforGeeks: Mutex vs Semaphore](https://www.geeksforgeeks.org/mutex-vs-semaphore/) — сравнение примитивов
- [Medium: Locks vs Semaphores vs Mutex](https://medium.com/@stoic.engineer/locks-vs-semaphores-vs-mutex-understanding-concurrency-control-in-real-systems-f726dabdf781) — практические примеры (2025)

### Инструменты
- [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html) — обнаружение race conditions
- [Go Race Detector](https://go.dev/doc/articles/race_detector) — `go test -race`

### Классические статьи
- Dijkstra: "Cooperating Sequential Processes" (1965) — изобретение semaphore
- Coffman et al: "System Deadlocks" (1971) — 4 условия deadlock

---

*Обновлено: 2026-01-09 — добавлены педагогические секции (5 аналогий: ванная/mutex, парковка/semaphore, колокольчик/condvar, узкий мост/deadlock, обедающие философы; 6 типичных ошибок: забыть unlock, порядок lock'ов, spurious wakeup, lock contention, notify vs notifyAll, double-checked locking; 5 ментальных моделей: 4 условия Coffman, happens-before, таблица выбора примитива, граф ожидания, иерархия примитивов)*
