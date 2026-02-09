---
title: "Synchronization Primitives: mutex, semaphore и другие"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[processes-threads-fundamentals]]"
  - "[[concurrency-vs-parallelism]]"
  - "[[async-models-overview]]"
---

# Synchronization Primitives: mutex, semaphore и другие

> **TL;DR:** Примитивы синхронизации координируют доступ к shared resources. Mutex — механизм блокировки (один владелец). Semaphore — механизм сигнализации (счётчик). Deadlock возникает при 4 условиях Coffman: mutual exclusion + hold and wait + no preemption + circular wait. Лучшая синхронизация — её отсутствие: immutable data, message passing, thread confinement.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Процессы и потоки** | Что синхронизируем | [[processes-threads-fundamentals]] |
| **Concurrency vs Parallelism** | Когда нужна синхронизация | [[concurrency-vs-parallelism]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Mutex** | Блокировка с владельцем | Ключ от туалета в кофейне |
| **Semaphore** | Счётчик доступных ресурсов | Светофор на перекрёстке |
| **Critical Section** | Код, работающий с shared data | Кабинка банкомата |
| **Deadlock** | Взаимная блокировка | Два человека в узком коридоре |
| **Race Condition** | Результат зависит от порядка | Два кассира обновляют баланс |

---

## ПОЧЕМУ нужна синхронизация

### Проблема: shared mutable state

Когда несколько потоков обращаются к одним данным, возникает хаос. Рассмотрим простой счётчик:

```kotlin
var counter = 0

// Thread 1                    // Thread 2
counter++                      counter++
```

Казалось бы, результат должен быть 2. Но `counter++` — это три операции:

```
1. Прочитать counter (= 0)
2. Добавить 1 (= 1)
3. Записать обратно (counter = 1)
```

Если потоки выполняются параллельно:

```
┌─────────────────────────────────────────────────────────────┐
│                    RACE CONDITION                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Thread 1              Thread 2                            │
│   ────────              ────────                            │
│   read counter = 0                                          │
│                         read counter = 0                    │
│   add 1 → 1                                                 │
│                         add 1 → 1                           │
│   write counter = 1                                         │
│                         write counter = 1                   │
│                                                             │
│   Результат: counter = 1 (потерян один increment!)         │
└─────────────────────────────────────────────────────────────┘
```

### История: Dijkstra и THE System

**1962-1963:** Эдсгер Дейкстра разрабатывал операционную систему для компьютера Electrologica X8 в Технологическом университете Эйндховена (THE — Technische Hogeschool Eindhoven).

Проблема: на одном процессоре выполняются несколько программ. Каждая хочет использовать принтер, терминал, диск. Без координации — хаос.

**Решение Дейкстры:** семафор — простой счётчик с двумя операциями:
- **P** (probeer te verlagen — попробовать уменьшить)
- **V** (vrijgave — освобождение)

Терминология взята из железнодорожных семафоров: поезд ждёт зелёного сигнала, чтобы занять участок пути.

**1968:** Публикация в Communications of the ACM. Эта статья стала фундаментом для всех современных примитивов синхронизации.

---

## ЧТО такое Mutex

### Определение

Mutex (Mutual Exclusion) — примитив синхронизации, гарантирующий, что только один поток может владеть ресурсом в любой момент времени.

**Ключевое свойство: владение.** Только тот, кто заблокировал mutex, может его разблокировать.

```
┌─────────────────────────────────────────────────────────────┐
│                         MUTEX                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Thread A                    Thread B                      │
│   ────────                    ────────                      │
│   lock()                      lock() → ждёт...              │
│   [critical section]                 ↓                      │
│   unlock()                    [теперь владеет]              │
│                               [critical section]            │
│                               unlock()                      │
│                                                             │
│   Только ОДИН поток внутри critical section                │
└─────────────────────────────────────────────────────────────┘
```

### Аналогия: ключ от туалета

В кофейне один туалет и один ключ. Хочешь зайти — берёшь ключ. Если ключа нет — ждёшь в очереди. Вышел — повесил ключ обратно.

Важно: только ты можешь вернуть ключ (владение). Нельзя попросить друга повесить твой ключ.

### Использование в Kotlin/Java

```kotlin
// Java-style synchronized block
val lock = Any()

fun increment() {
    synchronized(lock) {
        // Только один поток здесь одновременно
        counter++
    }
}

// Kotlin coroutines: Mutex
val mutex = Mutex()

suspend fun incrementSafe() {
    mutex.withLock {
        // Только одна корутина здесь одновременно
        counter++
    }
}
```

**Критическое отличие:** `synchronized` блокирует поток (blocking), `Mutex.withLock` приостанавливает корутину (suspending).

---

## ЧТО такое Semaphore

### Определение

Semaphore — счётчик, контролирующий доступ к ресурсу. Может разрешать доступ нескольким потокам одновременно.

**Две операции:**
- **acquire/wait/P** — уменьшить счётчик (если > 0), иначе ждать
- **release/signal/V** — увеличить счётчик

```
┌─────────────────────────────────────────────────────────────┐
│                    SEMAPHORE (count = 3)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Начальное состояние: count = 3                           │
│                                                             │
│   Thread A: acquire() → count = 2 ✓                        │
│   Thread B: acquire() → count = 1 ✓                        │
│   Thread C: acquire() → count = 0 ✓                        │
│   Thread D: acquire() → ЖДЁТ (count = 0)                   │
│                                                             │
│   Thread A: release() → count = 1                          │
│   Thread D: просыпается → count = 0 ✓                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Binary Semaphore vs Mutex

Binary semaphore (count = 1) похож на mutex, но есть важное отличие:

| Аспект | Mutex | Binary Semaphore |
|--------|-------|------------------|
| Владение | Только владелец может unlock | Любой может release |
| Priority inheritance | Да | Нет |
| Назначение | Защита ресурса | Сигнализация |

**Семафор — сигнальный механизм, не блокировочный.**

### Паттерн: Producer-Consumer

```kotlin
val itemsAvailable = Semaphore(0)  // Изначально нет items
val spaceAvailable = Semaphore(10) // Буфер на 10 элементов

// Producer
suspend fun produce(item: Item) {
    spaceAvailable.acquire()  // Ждём свободное место
    buffer.add(item)
    itemsAvailable.release()  // Сигнал: есть новый item
}

// Consumer
suspend fun consume(): Item {
    itemsAvailable.acquire()  // Ждём item
    val item = buffer.remove()
    spaceAvailable.release()  // Сигнал: освободилось место
    return item
}
```

---

## Mutex vs Semaphore: когда что

### Сравнительная таблица

| Критерий | Mutex | Semaphore |
|----------|-------|-----------|
| **Назначение** | Защита ресурса | Сигнализация/координация |
| **Счётчик** | Всегда 1 | Любое число |
| **Владение** | Строгое | Нет |
| **Паттерн использования** | lock-use-unlock | signal-wait |
| **Типичный сценарий** | Critical section | Producer-consumer |

### Правило выбора

> **Mutex:** Когда нужно защитить shared data от одновременного доступа.
>
> **Semaphore:** Когда нужно координировать события между потоками или ограничить количество одновременных операций.

---

## Spinlock: активное ожидание

### Как работает

Spinlock — это mutex, который не усыпляет поток при ожидании, а "крутится" в цикле:

```c
while (lock != 0) {
    // Busy waiting — ничего не делаем, просто проверяем
}
lock = 1;  // Захватили
```

### Когда использовать

| Сценарий | Spinlock | Mutex |
|----------|----------|-------|
| Очень короткий critical section | ✅ | Overhead context switch |
| Длинный critical section | ❌ CPU waste | ✅ |
| Single-core | ❌ Бесполезен | ✅ |
| Kernel code | ✅ (нельзя спать) | Зависит |

**Важный вывод из бенчмарков:** под высокой нагрузкой mutex обычно быстрее spinlock. Scheduler не знает, что поток "крутится впустую", и может отдать ему всё CPU время.

### Hybrid: Adaptive Mutex

Современные ОС (Linux, macOS) используют адаптивный подход:
- Если владелец lock'а сейчас выполняется на другом ядре — spin немного
- Если владелец заблокирован — сразу sleep

---

## Deadlock: взаимная блокировка

### Что это

Deadlock — ситуация, когда два или более потоков ждут друг друга бесконечно.

```
┌─────────────────────────────────────────────────────────────┐
│                        DEADLOCK                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Thread A                    Thread B                      │
│   ────────                    ────────                      │
│   lock(mutex1) ✓             lock(mutex2) ✓                │
│   lock(mutex2) → ждёт B      lock(mutex1) → ждёт A         │
│       ↓                           ↓                         │
│   ∞ ЖДЁТ                     ∞ ЖДЁТ                        │
│                                                             │
│   Кольцевое ожидание: A → B → A                            │
└─────────────────────────────────────────────────────────────┘
```

### 4 условия Coffman (1971)

Deadlock возникает **только если выполняются все 4 условия**:

| Условие | Описание | Пример |
|---------|----------|--------|
| **Mutual Exclusion** | Ресурс нельзя разделить | Принтер |
| **Hold and Wait** | Держит одно, ждёт другое | Thread A держит mutex1, хочет mutex2 |
| **No Preemption** | Нельзя отобрать силой | Нет timeout на lock |
| **Circular Wait** | Кольцевое ожидание | A → B → A |

**Нарушь любое одно — deadlock невозможен.**

### Стратегии предотвращения

**1. Lock Ordering (против Circular Wait):**

```kotlin
// ПЛОХО: разный порядок
// Thread A: lock(a), lock(b)
// Thread B: lock(b), lock(a)

// ХОРОШО: одинаковый порядок везде
// Thread A: lock(a), lock(b)
// Thread B: lock(a), lock(b)
```

**2. Try-Lock с Timeout (против No Preemption):**

```kotlin
if (mutex.tryLock(timeout = 1.seconds)) {
    try {
        // работа
    } finally {
        mutex.unlock()
    }
} else {
    // Не удалось захватить — откатываемся
}
```

**3. Захватывать все или ничего (против Hold and Wait):**

```kotlin
fun transferMoney(from: Account, to: Account, amount: Int) {
    // Захватываем оба lock'а в определённом порядке
    val (first, second) = if (from.id < to.id) from to to else to to from

    synchronized(first) {
        synchronized(second) {
            from.balance -= amount
            to.balance += amount
        }
    }
}
```

---

## Race Condition: гонка за данными

### Что это

Race condition — ситуация, когда результат зависит от непредсказуемого порядка выполнения потоков.

### Классический паттерн: Check-Then-Act

```kotlin
// ГОНКА!
if (map.containsKey(key)) {    // Check
    return map[key]             // Act — между check и act другой поток мог удалить key
}
```

```kotlin
// БЕЗОПАСНО
return map.getOrElse(key) { default }  // Атомарная операция
```

### Аналогия: банковский перевод

Два человека одновременно проверяют баланс (1000₽) и снимают по 800₽. Каждый видит "баланс достаточен", каждый снимает. Итого: -600₽ на счету.

### Решение: атомарные операции

```kotlin
// AtomicInteger гарантирует атомарность
val counter = AtomicInteger(0)
counter.incrementAndGet()  // Атомарно: read + add + write

// ConcurrentHashMap для thread-safe коллекций
val cache = ConcurrentHashMap<String, User>()
cache.computeIfAbsent(key) { loadUser(key) }  // Атомарно
```

---

## Kotlin: практические инструменты

### Иерархия выбора

```
┌─────────────────────────────────────────────────────────────┐
│              ВЫБОР ИНСТРУМЕНТА СИНХРОНИЗАЦИИ                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. Избегать shared state                                 │
│      └── Immutable data, message passing                   │
│                                                             │
│   2. Thread confinement                                    │
│      └── Dispatchers.Default.limitedParallelism(1)         │
│                                                             │
│   3. Atomic operations                                     │
│      └── AtomicInteger, AtomicReference                    │
│                                                             │
│   4. Lock-free structures                                  │
│      └── ConcurrentHashMap, ConcurrentLinkedQueue          │
│                                                             │
│   5. Fine-grained locking                                  │
│      └── Mutex (coroutines), synchronized (blocking)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### synchronized vs Mutex

```kotlin
// JVM blocking - используй для blocking кода
fun updateBlocking() {
    synchronized(lock) {
        // Блокирует поток
        Thread.sleep(100)
        counter++
    }
}

// Coroutines suspending - используй для suspend функций
suspend fun updateSuspending() {
    mutex.withLock {
        // НЕ блокирует поток, только приостанавливает корутину
        delay(100)
        counter++
    }
}
```

**Важно:** Никогда не используй `synchronized` внутри suspend функции с другими suspend-вызовами — это заблокирует поток на время всего блока.

### StateFlow для UI State

```kotlin
class ViewModel {
    // Thread-safe обновление состояния
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun updateName(name: String) {
        _state.update { currentState ->
            currentState.copy(name = name)
        }
    }
}
```

`MutableStateFlow.update` — атомарная операция, не требует внешней синхронизации.

---

## Подводные камни

### Когда НЕ синхронизировать

**Immutable data:**
```kotlin
data class User(val name: String, val age: Int)  // Immutable
// Несколько потоков могут читать безопасно
```

**Thread-local data:**
```kotlin
val threadLocal = ThreadLocal<Connection>()
// Каждый поток имеет свою копию
```

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Забыть unlock | Вечная блокировка | `withLock { }`, `try-finally` |
| Lock на разные объекты | Race condition | Один lock для одних данных |
| Nested locks разном порядке | Deadlock | Lock ordering |
| synchronized в suspend | Thread blocked | Использовать Mutex |
| Coarse-grained lock | Плохая производительность | Fine-grained или lock-free |

### Мифы и заблуждения

**Миф:** "volatile решает все проблемы синхронизации"
**Реальность:** volatile гарантирует visibility, но не atomicity. `counter++` всё равно не атомарен с volatile.

**Миф:** "Чем больше locks, тем безопаснее"
**Реальность:** Избыточная синхронизация создаёт deadlock и убивает performance.

**Миф:** "Deadlock легко отловить в тестах"
**Реальность:** Deadlock может проявиться только при специфическом timing, который редок в тестах.

---

## Куда дальше

**Если здесь впервые:**
→ [[processes-threads-fundamentals]] — как работают потоки

**Если понял и хочешь глубже:**
→ [[async-models-overview]] — async/await, корутины, альтернативы lock'ам

**Практическое применение:**
→ KMP: как синхронизация отличается на разных платформах

---

## Источники

- [Barr Group: Mutexes and Semaphores Demystified](https://barrgroup.com/blog/mutexes-and-semaphores-demystified) — locking vs signaling
- [Wikipedia: Semaphore](https://en.wikipedia.org/wiki/Semaphore_(programming)) — история Dijkstra
- [GeeksforGeeks: Deadlock Conditions](https://www.geeksforgeeks.org/conditions-for-deadlock-in-operating-system/) — 4 условия Coffman
- [kt.academy: Synchronization](https://kt.academy/article/ek-synchronization) — Kotlin best practices
- [matklad: Mutexes Are Faster Than Spinlocks](https://matklad.github.io/2020/01/04/mutexes-are-faster-than-spinlocks.html) — бенчмарки
- [Kotlin Docs: Shared Mutable State](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex в корутинах

---

*Проверено: 2026-01-09*
