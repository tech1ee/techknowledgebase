---
title: "Concurrency & Parallelism: Threads, Async, Race Conditions"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/programming
  - concurrency
  - parallelism
  - threads
  - async
  - type/concept
  - level/intermediate
related:
  - "[[programming-overview]]"
  - "[[jvm-concurrency-overview]]"
  - "[[architecture-resilience-patterns]]"
---

# Concurrency & Parallelism: Threads, Async, Race Conditions

> Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once. — Rob Pike

---

## TL;DR

- **Concurrency** — структурирование программы для работы с несколькими задачами
- **Parallelism** — одновременное выполнение на нескольких CPU cores
- **Race condition** — баг из-за непредсказуемого порядка операций
- **Async/Await** — concurrency без явных потоков (cooperative)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Thread** | Поток выполнения внутри процесса |
| **Process** | Изолированная единица выполнения с своей памятью |
| **Race Condition** | Баг из-за timing зависимости |
| **Deadlock** | Взаимная блокировка потоков |
| **Mutex** | Mutual Exclusion — блокировка ресурса |
| **Semaphore** | Ограничение числа одновременных доступов |
| **Atomic** | Операция, выполняемая как единое целое |
| **Async** | Неблокирующее выполнение |

---

## Concurrency vs Parallelism

```
┌────────────────────────────────────────────────────────────────────────────┐
│                 CONCURRENCY vs PARALLELISM                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONCURRENCY (структура)                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  1 CPU, 3 Tasks (time-slicing)                                      │   │
│  │                                                                      │   │
│  │  Time: ─────────────────────────────────────────────────▶           │   │
│  │                                                                      │   │
│  │  CPU:  [T1][T2][T1][T3][T1][T2][T3][T1][T2][T3]                     │   │
│  │                                                                      │   │
│  │  Tasks switch rapidly → appears simultaneous                        │   │
│  │  Good for: I/O-bound work (waiting for network, disk)              │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PARALLELISM (исполнение)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  4 CPUs, 4 Tasks (truly simultaneous)                               │   │
│  │                                                                      │   │
│  │  Time: ─────────────────────────────────────────────────▶           │   │
│  │                                                                      │   │
│  │  CPU1: [───────────── Task 1 ─────────────]                         │   │
│  │  CPU2: [───────────── Task 2 ─────────────]                         │   │
│  │  CPU3: [───────────── Task 3 ─────────────]                         │   │
│  │  CPU4: [───────────── Task 4 ─────────────]                         │   │
│  │                                                                      │   │
│  │  Actually runs at the same time                                     │   │
│  │  Good for: CPU-bound work (calculations)                           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  KEY INSIGHT:                                                              │
│  • Concurrency = dealing with multiple things (design)                    │
│  • Parallelism = doing multiple things (execution)                        │
│  • Can have concurrency without parallelism (single core)                │
│  • Parallelism requires concurrency structure                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Threading Models

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      THREADING MODELS                                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. OS THREADS (1:1)                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  User Thread ──────────────────▶ Kernel Thread                      │   │
│  │                                                                      │   │
│  │  • Java, C++, Rust (std::thread)                                   │   │
│  │  • Heavy (~1MB stack per thread)                                   │   │
│  │  • Expensive context switch                                        │   │
│  │  • True parallelism                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. GREEN THREADS (M:N)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Many User Threads ────────────▶ Few Kernel Threads                 │   │
│  │                                                                      │   │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐                                          │   │
│  │  │ G │ │ G │ │ G │ │ G │   Green threads                          │   │
│  │  └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘   (lightweight)                          │   │
│  │    └─────┼─────┴─────┘                                              │   │
│  │          ▼                                                          │   │
│  │       ┌─────┐ ┌─────┐                                              │   │
│  │       │ OS  │ │ OS  │     OS threads                               │   │
│  │       └─────┘ └─────┘                                              │   │
│  │                                                                      │   │
│  │  • Go (goroutines), Erlang, Java 21+ (virtual threads)             │   │
│  │  • Lightweight (~KB per thread)                                    │   │
│  │  • Cheap context switch                                            │   │
│  │  • Runtime manages scheduling                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. EVENT LOOP (Async)                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │     ┌─────────────────────────────────────────────────┐            │   │
│  │     │             EVENT LOOP                          │            │   │
│  │     │                                                 │            │   │
│  │     │  while (events.hasNext()) {                    │            │   │
│  │     │      event = events.next();                    │            │   │
│  │     │      handler(event);  // non-blocking          │            │   │
│  │     │  }                                              │            │   │
│  │     │                                                 │            │   │
│  │     └─────────────────────────────────────────────────┘            │   │
│  │                                                                      │   │
│  │  • JavaScript (Node.js), Python (asyncio)                          │   │
│  │  • Single thread, non-blocking I/O                                 │   │
│  │  • Callbacks/Promises/async-await                                  │   │
│  │  • No parallelism for CPU-bound work                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Race Conditions

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      RACE CONDITION                                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROBLEM: Non-atomic read-modify-write                                     │
│                                                                             │
│  counter = 0                                                               │
│                                                                             │
│  Thread A                    Thread B                                      │
│  ─────────                   ─────────                                     │
│  read counter (0)            read counter (0)                              │
│  add 1 (= 1)                                                               │
│                              add 1 (= 1)                                   │
│  write counter (1)                                                         │
│                              write counter (1)                             │
│                                                                             │
│  Expected: counter = 2                                                     │
│  Actual:   counter = 1  ← BUG!                                            │
│                                                                             │
│  SOLUTION: Make operation atomic                                           │
│                                                                             │
│  Thread A                    Thread B                                      │
│  ─────────                   ─────────                                     │
│  LOCK                        waiting...                                    │
│  read counter (0)            waiting...                                    │
│  add 1 (= 1)                 waiting...                                    │
│  write counter (1)           waiting...                                    │
│  UNLOCK                      LOCK                                          │
│                              read counter (1)                              │
│                              add 1 (= 2)                                   │
│                              write counter (2)                             │
│                              UNLOCK                                        │
│                                                                             │
│  Result: counter = 2 ✓                                                     │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Code Examples

```python
# ❌ Race condition
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # Not atomic!

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # Often < 1000000 due to race condition

# ✅ Fixed with Lock
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:  # Acquire before, release after
            counter += 1

# ✅ Better: Use atomic operations
from threading import Lock
from collections import Counter
import queue

# Thread-safe alternatives:
# - queue.Queue for producer-consumer
# - threading.Lock for critical sections
# - atomic types (e.g., AtomicInteger in Java)
```

```go
// ✅ Go: sync/atomic for simple counters
import "sync/atomic"

var counter int64

func increment() {
    atomic.AddInt64(&counter, 1)  // Atomic operation
}

// ✅ Go: sync.Mutex for complex operations
import "sync"

type SafeCounter struct {
    mu    sync.Mutex
    value map[string]int
}

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value[key]++
}
```

---

## Deadlock

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          DEADLOCK                                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Four conditions (ALL must be true):                                       │
│                                                                             │
│  1. MUTUAL EXCLUSION                                                       │
│     Resource can only be held by one thread                               │
│                                                                             │
│  2. HOLD AND WAIT                                                          │
│     Thread holding resource waits for another                             │
│                                                                             │
│  3. NO PREEMPTION                                                          │
│     Resource cannot be forcibly taken                                     │
│                                                                             │
│  4. CIRCULAR WAIT                                                          │
│     Thread A waits for B, B waits for A                                   │
│                                                                             │
│  EXAMPLE:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Thread A                      Thread B                             │   │
│  │  ─────────                     ─────────                            │   │
│  │  lock(resource1)               lock(resource2)                      │   │
│  │  ...                           ...                                  │   │
│  │  lock(resource2) ← WAITING     lock(resource1) ← WAITING           │   │
│  │         │                              │                            │   │
│  │         └──────── DEADLOCK! ───────────┘                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PREVENTION:                                                               │
│  • Lock ordering: Always acquire locks in same order                      │
│  • Timeout: Give up if can't acquire lock in time                        │
│  • Lock-free data structures                                              │
│  • Single lock for related resources                                      │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

```python
# ❌ Deadlock prone
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread_1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:  # Waits for lock_b
            pass

def thread_2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:  # Waits for lock_a → DEADLOCK
            pass

# ✅ Fixed: Consistent lock ordering
def thread_1():
    with lock_a:  # Always acquire a first
        with lock_b:
            pass

def thread_2():
    with lock_a:  # Same order: a first
        with lock_b:
            pass
```

---

## Async/Await Pattern

```python
# ✅ Python asyncio
import asyncio

async def fetch_data(url: str) -> dict:
    """Non-blocking HTTP request."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    # Sequential (slow)
    data1 = await fetch_data("http://api1.com")
    data2 = await fetch_data("http://api2.com")

    # Concurrent (fast)
    data1, data2 = await asyncio.gather(
        fetch_data("http://api1.com"),
        fetch_data("http://api2.com")
    )

    # With timeout
    try:
        data = await asyncio.wait_for(
            fetch_data("http://slow-api.com"),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print("Request timed out")

asyncio.run(main())
```

```javascript
// ✅ JavaScript async/await
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}

async function main() {
    // Concurrent
    const [data1, data2] = await Promise.all([
        fetchData('http://api1.com'),
        fetchData('http://api2.com')
    ]);

    // With timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const data = await fetch(url, { signal: controller.signal });
    } catch (e) {
        if (e.name === 'AbortError') {
            console.log('Request timed out');
        }
    } finally {
        clearTimeout(timeout);
    }
}
```

---

## Synchronization Primitives

| Primitive | Use Case | Characteristics |
|-----------|----------|-----------------|
| **Mutex/Lock** | Exclusive access to resource | One thread at a time |
| **RWLock** | Multiple readers, one writer | Better for read-heavy |
| **Semaphore** | Limit concurrent access | N threads at a time |
| **Condition Variable** | Wait for condition | Producer-consumer |
| **Barrier** | Synchronize at point | All threads wait |
| **Atomic** | Simple counters, flags | Lock-free, fast |
| **Channel** | Message passing | Go, Rust, Kotlin |

```go
// ✅ Go channels: "Don't communicate by sharing memory;
//                 share memory by communicating."

func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i  // Send to channel
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for value := range ch {  // Receive from channel
        fmt.Println(value)
    }
}

func main() {
    ch := make(chan int, 10)  // Buffered channel

    go producer(ch)
    consumer(ch)
}
```

---

## Common Patterns

### Producer-Consumer

```python
import queue
import threading

def producer(q: queue.Queue):
    for i in range(10):
        q.put(i)
        print(f"Produced: {i}")
    q.put(None)  # Sentinel to stop consumer

def consumer(q: queue.Queue):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        q.task_done()

q = queue.Queue(maxsize=5)  # Bounded queue
threading.Thread(target=producer, args=(q,)).start()
threading.Thread(target=consumer, args=(q,)).start()
```

### Worker Pool

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_item(item):
    # Heavy processing
    return item * 2

items = range(100)

with ThreadPoolExecutor(max_workers=10) as executor:
    # Submit all tasks
    futures = {executor.submit(process_item, item): item for item in items}

    # Process as completed
    for future in as_completed(futures):
        item = futures[future]
        try:
            result = future.result()
            print(f"Item {item} -> {result}")
        except Exception as e:
            print(f"Item {item} failed: {e}")
```

---

## Проверь себя

<details>
<summary>1. Когда использовать threads vs async?</summary>

**Ответ:**

**Threads (parallelism):**
- CPU-bound работа (вычисления)
- Нужен настоящий параллелизм
- Blocking I/O (legacy libraries)

**Async (concurrency):**
- I/O-bound работа (network, disk)
- Много ожидания
- Высокое число concurrent connections

**Примеры:**
- Image processing → threads/multiprocessing
- Web scraping → async
- API server → async
- Data science calculations → multiprocessing

</details>

<details>
<summary>2. Как избежать deadlock?</summary>

**Ответ:**

**Стратегии:**

1. **Lock ordering:**
   - Всегда acquire locks в одном порядке
   - Например, по ID ресурса

2. **Timeout:**
   ```python
   if lock.acquire(timeout=5.0):
       try:
           # work
       finally:
           lock.release()
   else:
       # Handle timeout
   ```

3. **Try-lock:**
   ```python
   if lock_a.acquire(blocking=False):
       if lock_b.acquire(blocking=False):
           # work
       else:
           lock_a.release()
   ```

4. **Single lock:** Один lock для связанных ресурсов

5. **Lock-free:** Atomic operations, channels

</details>

<details>
<summary>3. Что такое happens-before?</summary>

**Ответ:**

**Happens-before** — гарантия порядка видимости изменений между потоками.

**В Java/Kotlin:**
- `synchronized` block exit happens-before entry в том же мониторе
- `volatile` write happens-before read той же переменной
- `Thread.start()` happens-before любого кода в потоке
- Thread termination happens-before `Thread.join()` return

**Зачем:**
Без happens-before компилятор и CPU могут переупорядочить операции → неожиданное поведение.

```java
// Без volatile — может не работать!
boolean flag = false;
int value = 0;

// Thread 1
value = 42;
flag = true;

// Thread 2
if (flag) {
    // value может быть 0 из-за reordering!
}
```

</details>

<details>
<summary>4. Чем отличаются Mutex и Semaphore?</summary>

**Ответ:**

**Mutex (Mutual Exclusion):**
- Только 1 поток может владеть
- Owner может release (ownership)
- Binary: locked/unlocked

**Semaphore:**
- N потоков могут владеть одновременно
- Любой может release (no ownership)
- Counting: 0 to N

**Примеры:**
```python
# Mutex: exclusive access to file
mutex = threading.Lock()
with mutex:
    write_to_file()

# Semaphore: limit concurrent connections
semaphore = threading.Semaphore(10)  # Max 10
with semaphore:
    connect_to_db()  # Up to 10 concurrent
```

</details>

---

## Связи

- [[programming-overview]] — основы программирования
- [[jvm-concurrency-overview]] — JVM concurrency specifics
- [[architecture-resilience-patterns]] — retry, circuit breaker
- [[kotlin-coroutines]] — Kotlin coroutines

---

## Источники

- "Java Concurrency in Practice" by Brian Goetz
- "The Go Programming Language" — Chapter 8
- [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [Rust async book](https://rust-lang.github.io/async-book/)

---

*Проверено: 2025-12-22*
