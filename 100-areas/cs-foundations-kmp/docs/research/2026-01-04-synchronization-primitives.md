# Research Report: Synchronization Primitives

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Примитивы синхронизации — инструменты для координации доступа к shared resources. Mutex — locking mechanism (один владелец), Semaphore — signaling mechanism (счётчик). Изобретены Dijkstra в 1962-63 для THE multiprogramming system. Deadlock возникает при выполнении 4 условий Coffman: mutual exclusion, hold and wait, no preemption, circular wait. Spinlock эффективен только для очень коротких critical sections на multi-core. Kotlin coroutines используют Mutex вместо synchronized. Лучшая синхронизация — её отсутствие: immutable data, message passing.

## Key Findings

### 1. Mutex vs Semaphore: фундаментальная разница

**Mutex (Mutual Exclusion):**
- Механизм **блокировки** (locking)
- Строгое владение: только владелец может разблокировать
- Один ресурс, один замок
- Аналогия: ключ от туалета в кофейне

**Semaphore:**
- Механизм **сигнализации** (signaling)
- Нет владения: один поток может post, другой — wait
- Счётчик ресурсов
- Аналогия: светофор на перекрёстке

**Ключевая фраза:**
"Mutex protects resources, semaphore signals events"

### 2. История: Dijkstra и THE System

**1962-1963:** Dijkstra изобретает семафоры при разработке ОС для Electrologica X8
**1965:** Внутренние публикации о cooperating sequential processes
**1968:** Публикация в Communications of the ACM

**P и V операции:**
- P = probeer te verlagen (попробовать уменьшить)
- V = vrijgave (освобождение)
- Терминология взята из железнодорожных сигналов

### 3. Deadlock: 4 условия Coffman (1971)

| Условие | Описание | Как предотвратить |
|---------|----------|-------------------|
| **Mutual Exclusion** | Ресурс неделим | Использовать read-only, lock-free |
| **Hold and Wait** | Держит одно, ждёт другое | Захватывать все или ничего |
| **No Preemption** | Нельзя отобрать силой | Timeout, try-lock |
| **Circular Wait** | Кольцевое ожидание | Упорядочить захват (lock ordering) |

**Все 4 условия необходимы и достаточны.** Нарушь одно — deadlock невозможен.

### 4. Spinlock vs Mutex

| Аспект | Spinlock | Mutex |
|--------|----------|-------|
| Ожидание | Busy-waiting (крутится) | Блокировка (спит) |
| CPU при ожидании | 100% | 0% |
| Накладные расходы | Нет context switch | Syscall при contention |
| Когда использовать | Очень короткие critical sections | Длительные операции |
| Single-core | Бесполезен | OK |

**Важный вывод:** "Mutexes are faster than spinlocks" — под высокой нагрузкой spinlock проигрывает из-за scheduler interference.

### 5. Condition Variables и Monitors

**Monitor:**
- Концептуальная "коробка" с функциями
- Гарантия: только одна функция выполняется одновременно
- Java synchronized = monitor pattern

**Condition Variable:**
- Позволяет ждать условия внутри monitor
- wait() — отпустить lock и заснуть
- notify/signal — разбудить ожидающих

### 6. Race Condition: паттерны

**Check-Then-Act (самый частый):**
```
if (x == 0) {    // Thread 1 читает x=0
    x = x + 1;   // Thread 2 тоже читает x=0
}                // Оба записывают x=1, потерян increment
```

**Read-Modify-Write:**
```
counter++;  // Выглядит атомарно, но это 3 операции:
            // 1. Прочитать counter
            // 2. Добавить 1
            // 3. Записать обратно
```

### 7. Kotlin: synchronized vs Mutex

| Инструмент | Когда использовать |
|------------|-------------------|
| `synchronized` | JVM, blocking код |
| `@Synchronized` | Аннотация для методов |
| `Mutex` | Coroutines (suspending) |
| `AtomicInteger` | Простые счётчики |
| `StateFlow` | Reactive state |
| Single-thread dispatcher | Thread confinement |

**Главное:** Mutex.lock() — suspending function, не блокирует поток.

### 8. Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Забыть unlock() | Вечная блокировка | RAII: lock_guard, withLock |
| Разный порядок locks | Deadlock | Lock ordering |
| Lock внутри lock | Deadlock (non-reentrant) | ReentrantLock |
| Volatile вместо sync | Race condition | Atomic или sync |
| Coarse-grained lock | Низкая производительность | Fine-grained |
| Lock на suspending call | Blocking thread | Mutex, не synchronized |

### 9. Best Practices

**Иерархия предпочтений:**
1. **Избегать shared state** — immutable, message passing
2. **Thread confinement** — single-thread dispatcher
3. **Atomic operations** — AtomicInteger, AtomicReference
4. **Lock-free structures** — ConcurrentHashMap
5. **Fine-grained locking** — synchronized/Mutex

**Правило:** "All program memory should fall into one of three buckets: thread exclusive, read-only, or lock protected."

## Community Sentiment

### Positive
- Понимание примитивов улучшает debugging
- Kotlin Mutex интегрируется с coroutines
- Lock ordering решает большинство deadlock
- RAII (withLock) предотвращает забытые unlock

### Negative
- "Fighting with locks" — сложность отладки
- Deadlock трудно воспроизвести
- Priority inversion на production
- Over-synchronization убивает performance

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Barr Group: Mutexes and Semaphores](https://barrgroup.com/blog/mutexes-and-semaphores-demystified) | Blog | ★★★★★ | Locking vs signaling |
| [Wikipedia: Semaphore](https://en.wikipedia.org/wiki/Semaphore_(programming)) | Reference | ★★★★☆ | Dijkstra history |
| [GeeksforGeeks: Deadlock Conditions](https://www.geeksforgeeks.org/conditions-for-deadlock-in-operating-system/) | Tutorial | ★★★★☆ | 4 Coffman conditions |
| [Baeldung: Mutex vs Spinlock](https://www.baeldung.com/cs/mutex-vs-spinlock-concurrent-parallel-distributed-programming) | Tutorial | ★★★★☆ | When to use which |
| [kt.academy: Synchronization](https://kt.academy/article/ek-synchronization) | Tutorial | ★★★★★ | Kotlin best practices |
| [matklad: Mutexes Faster](https://matklad.github.io/2020/01/04/mutexes-are-faster-than-spinlocks.html) | Blog | ★★★★★ | Performance benchmarks |
| [Kotlin Docs: Shared Mutable State](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) | Official | ★★★★★ | Mutex in coroutines |
| [UCSD: Monitors and CVs](https://cseweb.ucsd.edu/classes/sp17/cse120-a/applications/ln/lecture8.html) | Academic | ★★★★☆ | Monitor theory |

## Research Methodology
- **Queries used:** 8 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** Mutex/Semaphore difference, Dijkstra history, Deadlock conditions, Kotlin specifics

---

*Проверено: 2026-01-09*
