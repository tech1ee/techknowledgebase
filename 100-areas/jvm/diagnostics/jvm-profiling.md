---
title: "JVM Profiling: как найти bottleneck"
created: 2025-11-25
modified: 2026-01-03
tags:
  - jvm
  - profiling
  - async-profiler
  - performance
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-performance-overview]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-jit-compiler]]"
---

# JVM Profiling: как найти bottleneck

> **TL;DR:** async-profiler — лучший выбор для JVM, <1% overhead, production-safe. Flame graph: ширина = % CPU, ищи самые широкие полосы. Типы: CPU (горячие методы), alloc (GC pressure), lock (contention). Интуиция ошибается в 90%: "JSON медленный" → а профиль показывает SQL в цикле.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Как работает JVM | Понимать стек вызовов, JIT | [[jvm-basics-history]] |
| GC основы | Понимать allocation pressure | [[jvm-gc-tuning]] |
| Многопоточность | Lock contention | [[jvm-concurrency-overview]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Profiling** | Сбор данных о потреблении ресурсов | Видеонаблюдение за работой офиса |
| **Sampling** | Периодические снимки состояния | Фото каждые 10мс вместо видео 24/7 |
| **Flame Graph** | Визуализация стека вызовов | Карта теплоотдачи — где горит |
| **Hotspot** | Метод, потребляющий много ресурсов | Узкое место на дороге |
| **Overhead** | Замедление от самого профилирования | Камера, которая тормозит работу |
| **Allocation Rate** | Скорость создания объектов (MB/s) | Скорость заполнения мусорки |
| **Lock Contention** | Потоки ждут освобождения блокировки | Очередь к одному туалету |
| **Call Stack** | Цепочка вызовов методов | Хлебные крошки: откуда пришёл |

---

Профилирование — сбор данных о том, где приложение тратит ресурсы: CPU time, memory allocations, lock contention. async-profiler делает sampling (снимки состояния) с минимальным overhead (<1%) и генерирует flame graphs — визуализацию, где ширина полосы показывает долю времени метода.

Интуиция программиста обманывает в 90% случаев. "JSON парсинг тормозит" — а профилирование показывает SQL запрос в цикле занимающий 80% времени. async-profiler безопасен для production и находит реальные hotspots за минуту.

---

## Почему профилирование необходимо

Человеческая интуиция о производительности почти всегда ошибочна. Разработчик думает: "Этот цикл выглядит медленным" — а реальная проблема в неиндексированном SQL запросе, который занимает 90% времени.

Профилирование даёт объективные данные. Вместо предположений вы видите точные цифры: какой метод потребляет сколько CPU, где создаются объекты, какие блокировки вызывают contention.

**Sampling vs Instrumentation:** Sampling периодически делает снимки стека вызовов (например, 100 раз в секунду). Instrumentation вставляет измерительный код в каждый метод. Sampling даёт статистическую картину с минимальным overhead (<1%), instrumentation даёт точные числа, но замедляет приложение (10-50%). Для production всегда используйте sampling.

## Типы профилирования

| Тип | Что ищет | Overhead | Когда использовать |
|-----|----------|----------|-------------------|
| **CPU** | Горячие методы | 1-5% | "Приложение медленное" |
| **Memory** | Allocations, leaks | 5-10% | Частые GC, OOM |
| **Lock** | Thread contention | 10-20% | Низкий throughput при высоком CPU |
| **I/O** | Медленные операции | 5-10% | Database/network latency |

---

## async-profiler (рекомендую)

Лучший профайлер для JVM. Open-source, production-safe, <1% overhead.

### Установка

```bash
# macOS
brew install async-profiler

# Linux
wget https://github.com/async-profiler/async-profiler/releases/download/v2.9/async-profiler-2.9-linux-x64.tar.gz
tar xzf async-profiler-2.9-linux-x64.tar.gz
```

### CPU profiling

```bash
# Профилировать 30 секунд, вывести flame graph
./profiler.sh -d 30 -f flamegraph.html <pid>

# Только ваш код (без фреймворков)
./profiler.sh -d 30 --include 'com/myapp/*' -f cpu.html <pid>
```

### Memory profiling

```bash
# Найти где создаются объекты (GC pressure)
./profiler.sh -d 60 -e alloc -f alloc.html <pid>
```

### Lock profiling

```bash
# Найти thread contention
./profiler.sh -d 60 -e lock -f lock.html <pid>
```

---

## Как читать Flame Graph

```
Ширина полосы = % CPU времени. Чем шире — тем медленнее.

main() ──────────────────────────────────────────────
  │
  ├─ processRequest() ──────────────────────────────  (60%)
  │    │
  │    ├─ parseJSON() ───────────  (15%)
  │    │
  │    └─ calculateResult() ──────────────────  (40%) ← HOTSPOT
  │         │
  │         └─ fibonacci(n) ────────────  (35%) ← Оптимизировать!
  │
  └─ sendResponse() ──────  (10%)
```

**Интерпретация:**
- `fibonacci(n)` занимает 35% CPU → главный кандидат на оптимизацию
- `parseJSON()` — 15% → второй приоритет
- `sendResponse()` — 10% → уже достаточно быстрый

**Интерактивность HTML:**
- Click → zoom на subtree
- Ctrl+F → поиск метода
- Hover → детали (% CPU, полное имя)

---

## Практический пример

**Проблема:** REST API, p99 latency 800ms (SLA: 100ms).

### Шаг 1: CPU profiling

```bash
./profiler.sh -d 60 -f cpu.html <pid>
```

**Flame graph показывает:**
```
OrderController.getOrders() ─────────────────────
  │
  └─ orderRepository.findAll() ─────────────  (65%) ← SQL!
```

### Шаг 2: Проверить SQL

```sql
-- N+1 проблема: 101 запрос вместо 1
SELECT * FROM orders WHERE user_id = ?  -- вызывается 100 раз
```

### Шаг 3: Fix

```java
// БЫЛО: N+1 queries
for (User u : users) {
    orderRepo.findByUserId(u.getId());  // 100 запросов
}

// СТАЛО: JOIN FETCH (1 запрос)
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

### Шаг 4: Проверить

```bash
./profiler.sh -d 60 -f cpu-after.html <pid>
```

**Результат:**
| Метрика | До | После |
|---------|-----|-------|
| p99 latency | 800ms | 80ms |
| Throughput | 500/s | 2000/s |
| SQL queries | 101 | 1 |

---

## Memory Profiling: найти allocation hotspots

### Зачем

High allocation rate → частые GC → паузы → плохой latency.

### Пример

```bash
./profiler.sh -d 60 -e alloc -f alloc.html <pid>
```

**Результат:**
```
processRequest() ────────────────────────────────  (100%)
  │
  ├─ logging() ──────────────  (25%)  ← Неожиданно!
  │    │
  │    └─ String.format() ──────  (25%)
```

**Fix:**
```java
// БЫЛО: создаёт объекты даже если DEBUG выключен
logger.debug("User: " + userId + ", action: " + action);

// СТАЛО: zero allocation если DEBUG выключен
logger.debug("User: {}, action: {}", userId, action);
```

**Результат:** allocation rate 500 MB/s → 50 MB/s.

---

## Heap Dump: найти memory leak

### Когда брать

- OutOfMemoryError
- Memory растёт со временем и не падает
- Подозрение на leak

### Как взять

```bash
# Рекомендуемый способ
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Автоматически при OOM
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/heap.hprof \
     -jar myapp.jar
```

### Анализ в Eclipse MAT

1. **Leak Suspects Report** → автоматически находит потенциальные leaks
2. **Dominator Tree** → объекты с наибольшей retained size
3. **Histogram** → группировка по классу

**Типичный leak:**
```
CacheEntry instances holding 600MB
→ Unbounded cache в UserService
→ Fix: добавить eviction policy (LRU, max size)
```

---

## Lock Profiling: найти contention

### Симптомы

- High CPU, но низкий throughput
- Threads в BLOCKED state
- Добавление threads не помогает

### Пример

```bash
./profiler.sh -d 60 -e lock -f lock.html <pid>
```

**Результат:**
```
workerThread() ────────────────────────────────  (100%)
  │
  └─ synchronized(lock) ───────────────  (70%) ← Bottleneck!
       │
       └─ updateCounter() ─────────  (70%)
```

**Fix:**
```java
// БЫЛО: synchronized bottleneck
public synchronized void updateCounter() {
    counter++;
}

// СТАЛО: lock-free
private final AtomicInteger counter = new AtomicInteger();
public void updateCounter() {
    counter.incrementAndGet();
}
```

**Результат:** 8 threads: 50K → 500K ops/sec (10x).

---

## Best Practices для Production

**1. Sampling, не instrumentation**

Sampling делает снимки стека с интервалом (например, каждые 10ms) — overhead <1%. Instrumentation вставляет код в каждый метод — overhead 10-50%. На production разница критична: 1% overhead незаметен, 50% — сервис под нагрузкой упадёт.

**2. Профилируй 30-60 секунд**

Меньше 30 секунд — статистически недостоверно, редкие события не попадут в выборку. Больше 60 секунд — файл станет огромным, а паттерн уже виден. Исключение: профилирование startup — тогда достаточно 10 секунд.

**3. Профилируй под реальной нагрузкой**

Профиль idle приложения бесполезен — там нет hotspots. Нужен трафик, желательно production-like. Используйте load testing (Gatling, k6) или профилируйте прямо на production (async-profiler безопасен).

**4. Фильтруй свой код**

`--include 'com/myapp/*'` исключает framework код из flame graph. Иначе 80% графа — это Spring/Hibernate internals, которые вы не можете оптимизировать. Ищите проблемы в своём коде.

**5. Сохраняй raw data**

`./profiler.sh -o collapsed > stacks.txt` сохраняет сырые стеки. Позже можно перегенерировать flame graph с другими фильтрами, сравнить с будущими профилями, провести детальный анализ. HTML визуализация — удобна, но raw data — полнее.

---

## Сравнение профайлеров

| | async-profiler | VisualVM | JProfiler | JFR |
|---|---|---|---|---|
| **Overhead (prod)** | <1% | 2-5% | 1-3% | <1% |
| **Flame graphs** | Да | Нет | Plugin | Converter |
| **Production safe** | Да | Sampling | Да | Да |
| **Цена** | Free | Free | $499 | Free |
| **Рекомендую для** | Production | Dev quick | Enterprise | Continuous |

---

## Кто использует и реальные примеры

| Компания | Как используют профилирование | Что нашли |
|----------|------------------------------|-----------|
| **Netflix** | Continuous profiling в production | Hotspots в serialization, JSON overhead |
| **Uber** | async-profiler + custom dashboards | N+1 queries, thread pool sizing |
| **LinkedIn** | JFR для постоянного мониторинга | GC tuning, lock contention |
| **DataDog** | Continuous Profiler (APM) | Allocation hotspots, latency issues |

### Реальные кейсы оптимизации

```
Case 1: JSON serialization
Симптом: High CPU usage
Профиль: ObjectMapper.writeValueAsString() = 40%
Причина: Создание нового ObjectMapper на каждый запрос
Fix: Reuse ObjectMapper (thread-safe)
Результат: CPU -30%

Case 2: String concatenation в логах
Симптом: High allocation rate, частые Young GC
Профиль: alloc flame graph → String.concat() = 25%
Причина: logger.debug("User: " + userId) создаёт String даже если DEBUG off
Fix: logger.debug("User: {}", userId)
Результат: Allocation rate 500 MB/s → 50 MB/s

Case 3: Lock contention
Симптом: 16 threads, но throughput как на 2
Профиль: lock flame graph → synchronized = 70%
Причина: Global lock на весь cache
Fix: ConcurrentHashMap + striped locking
Результат: Throughput 5x
```

---

## Рекомендуемые источники

### Инструменты
- [async-profiler](https://github.com/async-profiler/async-profiler) — лучший для JVM
- [JFR (Flight Recorder)](https://openjdk.org/jeps/328) — встроенный в JDK
- [Eclipse MAT](https://eclipse.dev/mat/) — анализ heap dumps
- [VisualVM](https://visualvm.github.io/) — визуальный мониторинг

### Статьи
- [Flame Graphs](https://www.brendangregg.com/flamegraphs.html) — Brendan Gregg, создатель концепции
- [Java Profiling Tutorial](https://www.baeldung.com/java-profilers) — Baeldung
- [async-profiler guide](https://krzysztofslusarski.github.io/2022/12/12/async-manual.html) — детальный гайд

### Книги
- **"Java Performance"** — Scott Oaks, глава про profiling
- **"Systems Performance"** — Brendan Gregg — теория и практика

### Видео
- [Profiling Java Applications with async-profiler](https://www.youtube.com/results?search_query=async-profiler+java) — практические демо
- [Flame Graphs talks](https://www.youtube.com/results?search_query=brendan+gregg+flame+graphs) — от Brendan Gregg

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Профилирование замедляет приложение" | **Sampling profilers** (async-profiler) имеют <1% overhead. Безопасно для production |
| "JProfiler/YourKit лучше async-profiler" | Для **CPU profiling** async-profiler точнее (no safepoint bias). Для memory analysis — они удобнее |
| "Flame graph показывает время" | Flame graph показывает **количество samples**. Это proportional to time, но не время напрямую |
| "Самый высокий стек = проблема" | Flame graphs читаются по **ширине**, не высоте. Широкие прямоугольники = много времени |
| "Профилировать нужно только при проблемах" | **Continuous profiling** (Pyroscope, Parca) даёт baseline. Видим regression сразу |

---

## CS-фундамент

| CS-концепция | Применение в Profiling |
|--------------|------------------------|
| **Sampling** | Периодический snapshot стека. Статистически верно, низкий overhead |
| **Instrumentation** | Вставка кода в методы. Точно, но высокий overhead (не для production) |
| **Flame Graphs** | Визуализация стеков. Ширина = время. Позволяет быстро найти hotspots |
| **Safepoint Bias** | JVM profilers видят только safepoints. async-profiler использует PERF_EVENTS, без bias |
| **Allocation Profiling** | Отслеживание объектов, вызывающих GC pressure. Flame graph с allocation samples |

---

## Связи

- [[jvm-performance-overview]] — общая карта оптимизации
- [[jvm-gc-tuning]] — если проблема в GC
- [[jvm-jit-compiler]] — если код не компилируется в native
- [[jvm-benchmarking-jmh]] — для проверки оптимизаций

---

*Проверено: 2026-01-09 | Источники: async-profiler docs, Brendan Gregg, Baeldung — Педагогический контент проверен*
