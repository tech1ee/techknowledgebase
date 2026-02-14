---
title: "JVM Profiling: как найти bottleneck"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - profiling
  - async-profiler
  - performance
  - type/deep-dive
  - level/intermediate
type: deep-dive
status: published
area: programming
confidence: high
prerequisites:
  - "[[jvm-performance-overview]]"
  - "[[jvm-memory-model]]"
related:
  - "[[jvm-performance-overview]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-jit-compiler]]"
  - "[[jvm-benchmarking-jmh]]"
  - "[[jvm-production-debugging]]"
reading_time: 23
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# JVM Profiling: как найти bottleneck

> **TL;DR:** async-profiler -- лучший выбор для JVM, <1% overhead, production-safe. Flame graph: ширина = % CPU, ищи самые широкие полосы. Типы: CPU (горячие методы), alloc (GC pressure), lock (contention). Интуиция ошибается в 90%: "JSON медленный" -> а профиль показывает SQL в цикле.

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
| **Flame Graph** | Визуализация стека вызовов | МРТ-снимок: послойная картина, каждый слой = уровень стека |
| **Hotspot** | Метод, потребляющий много ресурсов | Узкое место на дороге |
| **Overhead** | Замедление от самого профилирования | Камера, которая тормозит работу |
| **Allocation Rate** | Скорость создания объектов (MB/s) | Счётчик расхода воды: показывает, кто потребляет больше |
| **Lock Contention** | Потоки ждут освобождения блокировки | Очередь к одному туалету |
| **Call Stack** | Цепочка вызовов методов | Хлебные крошки: откуда пришёл |
| **Safepoint Bias** | Искажение данных из-за sampling только в safepoints | Опрос только тех, кто стоит на остановке -- не репрезентативно |
| **Wall-clock profiling** | Профилирование по реальному времени (включая ожидание) | Хронометраж всего рабочего дня, включая перерывы |

---

## Зачем это знать

Профилирование -- сбор данных о том, где приложение тратит ресурсы: CPU time, memory allocations, lock contention. async-profiler делает sampling (снимки состояния) с минимальным overhead (<1%) и генерирует flame graphs -- визуализацию, где ширина полосы показывает долю времени метода.

Интуиция программиста обманывает в 90% случаев. "JSON парсинг тормозит" -- а профилирование показывает SQL запрос в цикле, занимающий 80% времени. Это не риторическое преувеличение: исследования Brendan Gregg показывают, что разработчики систематически ошибаются в оценке "горячих" участков кода. Причина -- cognitive bias: мы запоминаем сложный код (парсинг, сериализация), а не тривиальный, но повторяющийся тысячи раз (логирование, конкатенация строк). async-profiler безопасен для production и находит реальные hotspots за минуту.

> **Аналогия:** Профилирование -- это как медицинское обследование. Пациент говорит: "У меня болит голова" (интуиция). Врач делает анализ крови и МРТ (профилирование) и находит, что проблема в давлении (реальный bottleneck). Лечить голову бесполезно -- нужно лечить причину. Точно так же оптимизировать "подозрительный" код без данных -- значит лечить симптом, а не болезнь.

---

## Историческая справка

Профилирование JVM прошло долгий путь от примитивных инструментов до production-safe решений.

**HPROF (1998-2010)** -- встроенный в JDK профайлер, появившийся с самых ранних версий Java. Работал через JVMTI (Java Virtual Machine Tool Interface), вставляя инструментацию в каждый метод. Overhead был катастрофическим: 30-50%. Использовать в production было невозможно, а результаты в dev-среде не отражали реальное поведение под нагрузкой. HPROF удалён из JDK 9 как устаревший.

**JProfiler (2001) и YourKit (2003)** -- коммерческие профайлеры, значительно улучшившие UX. Красивые GUI, удобная навигация по call tree, интеграция с IDE. Однако оба страдали от **safepoint bias** -- фундаментальной проблемы JVM profiling. JVM может безопасно остановить поток только в safepoint (вызов метода, возврат, обратный переход цикла). Если метод содержит длинный цикл без safepoints, профайлер его просто "не видит". Результат: горячий код, который не попадает в safepoints, невидим для профайлера.

**async-profiler (Andrei Pangin, 2016)** -- революция в JVM profiling. Andrei Pangin, инженер из Одноклассников (ныне VK), решил проблему safepoint bias принципиально: вместо JVMTI он использовал Linux perf_events и macOS dtrace для получения стеков. Операционная система "фотографирует" стек в любой момент, не дожидаясь safepoint. Результат: overhead <1%, отсутствие bias, безопасность для production. async-profiler быстро стал стандартом индустрии -- его используют Netflix, Uber, LinkedIn, Datadog.

**JFR (Java Flight Recorder, 2018 open-source)** -- встроенный в JDK continuous profiler. Изначально был коммерческим продуктом Oracle (часть JRockit), затем перенесён в HotSpot и открыт в JDK 11. JFR записывает события (GC, allocations, lock contention, I/O) с минимальным overhead (<1%) и сохраняет в бинарный формат .jfr. Идеален для continuous profiling -- "чёрный ящик" вашего приложения.

Эволюция показывает чёткий тренд: от invasive instrumentation к low-overhead sampling, от "только в dev" к "always-on в production".

---

## Почему профилирование необходимо

Человеческая интуиция о производительности почти всегда ошибочна. Разработчик думает: "Этот цикл выглядит медленным" -- а реальная проблема в неиндексированном SQL запросе, который занимает 90% времени.

Профилирование даёт объективные данные. Вместо предположений вы видите точные цифры: какой метод потребляет сколько CPU, где создаются объекты, какие блокировки вызывают contention.

**Sampling vs Instrumentation:** Sampling периодически делает снимки стека вызовов (например, 100 раз в секунду). Instrumentation вставляет измерительный код в каждый метод. Sampling даёт статистическую картину с минимальным overhead (<1%), instrumentation даёт точные числа, но замедляет приложение (10-50%). Для production всегда используйте sampling.

Разница между этими подходами аналогична разнице между опросом общественного мнения и тотальной переписью населения. Опрос (sampling) охватывает не всех, но стоит дёшево и даёт статистически верную картину. Перепись (instrumentation) точна до каждого человека, но стоит огромных ресурсов и парализует обычную жизнь на время проведения.

## Типы профилирования

| Тип | Что ищет | Overhead | Когда использовать |
|-----|----------|----------|-------------------|
| **CPU** | Горячие методы | 1-5% | "Приложение медленное" |
| **Memory** | Allocations, leaks | 5-10% | Частые GC, OOM |
| **Lock** | Thread contention | 10-20% | Низкий throughput при высоком CPU |
| **I/O** | Медленные операции | 5-10% | Database/network latency |
| **Wall-clock** | Все потоки, включая ожидание | 1-5% | Потоки "висят" без CPU нагрузки |

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

Flame graph -- визуализация, придуманная Brendan Gregg в 2011 году для диагностики CPU-проблем в production-системах Netflix. Идея оказалась настолько мощной, что flame graphs стали стандартом индустрии.

### Базовая структура

```
Ширина полосы = % CPU времени. Чем шире -- тем медленнее.

main() ──────────────────────────────────────────────
  │
  ├─ processRequest() ──────────────────────────────  (60%)
  │    │
  │    ├─ parseJSON() ───────────  (15%)
  │    │
  │    └─ calculateResult() ──────────────────  (40%) <- HOTSPOT
  │         │
  │         └─ fibonacci(n) ────────────  (35%) <- Оптимизировать!
  │
  └─ sendResponse() ──────  (10%)
```

**Интерпретация:**
- `fibonacci(n)` занимает 35% CPU -> главный кандидат на оптимизацию
- `parseJSON()` -- 15% -> второй приоритет
- `sendResponse()` -- 10% -> уже достаточно быстрый

> **Аналогия:** Flame graph -- это МРТ-снимок вашего приложения. Как МРТ показывает послойную картину тела (каждый слой -- срез на определённой глубине), flame graph показывает послойную картину стека вызовов (каждый слой -- уровень вложенности). Широкие "пятна" на МРТ -- патология. Широкие полосы на flame graph -- performance hotspot. Врач не лечит по жалобам пациента -- он смотрит на снимок. Разработчик не оптимизирует по интуиции -- он смотрит на flame graph.

### Паттерны чтения flame graph

**Flat top (плоская вершина)** -- самый важный паттерн. Если метод занимает широкую полосу на самом верху графа, значит он тратит CPU time в своём собственном коде, а не в вызываемых методах. Это типичный признак CPU-bound операции: вычисление хеша, сериализация, математика. Flat top -- самый "благодарный" кандидат для оптимизации, потому что bottleneck локализован в одном конкретном методе.

**Tall thin tower (высокая узкая башня)** -- глубокая рекурсия или длинная цепочка вызовов. Каждый уровень вызывает следующий, но ни один не занимает много CPU сам по себе. Это может быть рекурсивный алгоритм (обход дерева), цепочка middleware, или слишком глубокий call chain фреймворка. Если башня высокая но узкая -- проблема не в CPU, а в stack depth. Если широкая и высокая -- комбинация глубокой рекурсии и высокого CPU потребления.

**Plateau (плато)** -- широкая полоса в середине графа, от которой отходят множество узких "зубцов" наверху. Это означает, что метод вызывает много разных дочерних методов, каждый из которых быстр сам по себе, но суммарно они занимают значительное время. Типичный пример -- метод-диспетчер, который обрабатывает разные типы запросов. Оптимизировать отдельные зубцы бессмысленно -- нужно пересмотреть архитектуру диспетчеризации.

**Missing frames** -- если flame graph выглядит "рваным" с пробелами, это может указывать на inlining: JIT-компилятор встроил метод в вызывающий код, и отдельного фрейма больше нет. async-profiler с флагом `-XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints` покажет более полную картину.

### Интерактивные возможности HTML-версии

HTML flame graph, генерируемый async-profiler -- не статическая картинка, а полноценное интерактивное приложение.

- **Click** -> zoom на поддерево: кликните на любой метод, и он растянется на всю ширину, показывая детали его дочерних вызовов. Это необходимо для исследования глубоких стеков, где интересующий метод занимает всего 5% общей ширины
- **Ctrl+F (Search)** -> подсвечивает все вхождения метода по имени или пакету. Например, поиск "jdbc" подсветит все database-вызовы, разбросанные по разным веткам стека. Суммарный процент показывается внизу экрана -- это ответ на вопрос "сколько CPU тратится на базу данных в сумме?"
- **Hover** -> показывает полное имя метода, количество samples и процент от общего числа. Полное имя критично, когда в графе видно только сокращённое имя из-за ширины полосы
- **Reset zoom** -> клик на `root` (нижний уровень) возвращает полный вид

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
  └─ orderRepository.findAll() ─────────────  (65%) <- SQL!
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

High allocation rate -> частые GC -> паузы -> плохой latency. Но есть важный нюанс: не всякий высокий allocation rate -- проблема. Ключевой вопрос -- куда уходят объекты.

> **Аналогия:** Allocation profiling -- это как счётчик расхода воды в доме. Общий счётчик показывает, что расход 1000 литров в день (allocation rate). Но чтобы понять проблему, нужно поставить счётчики на каждый кран: кухня -- 100 литров, ванная -- 200, а неисправный бачок -- 700 литров. Allocation profiling ставит "счётчик" на каждый вызов `new` и показывает, какой код "расходует" больше всего памяти.

### Allocation rate: пороговые значения

Allocation rate -- количество мегабайт, выделяемых в секунду. Для типичного web-приложения нормальный диапазон -- 100-500 MB/s. Если allocation rate превышает 1 GB/s, это почти всегда указывает на проблему: либо создаются ненужные объекты (строки, временные коллекции), либо архитектура неэффективна (создание объектов в цикле).

Связь с GC прямая и количественная: allocation rate определяет частоту Young GC. Если Young Generation = 1 GB, а allocation rate = 500 MB/s, то Young GC будет происходить каждые 2 секунды. При 2 GB/s -- каждые 500ms. Каждый Young GC -- это STW пауза (обычно 5-50ms для G1), поэтому снижение allocation rate напрямую уменьшает количество пауз.

### Young vs Old allocations

Большинство объектов (по generational hypothesis -- 90%+) умирают молодыми и никогда не покидают Young Generation. Они создаются, используются в рамках одного запроса и собираются следующим Young GC. Это дёшево -- Young GC копирует только живые объекты, а мёртвые просто "забывает".

Проблема возникает, когда объекты "протекают" в Old Generation. Это происходит, если объект пережил несколько Young GC (обычно 15 циклов). Если allocation rate высокий и Young GC происходят слишком часто, даже short-lived объекты успевают "постареть" и переместиться в Old Gen. Это создаёт давление уже на Old Gen, провоцируя Mixed GC или даже Full GC -- значительно более дорогие операции.

Allocation flame graph в async-profiler показывает не только ЧТО создаётся, но и СКОЛЬКО в байтах. Ширина полосы -- пропорциональна суммарному объёму аллокаций данного call path. Если 80% ширины занимает `String.concat()` внутри `logger.debug()` -- вы нашли проблему.

### Пример

```bash
./profiler.sh -d 60 -e alloc -f alloc.html <pid>
```

**Результат:**
```
processRequest() ────────────────────────────────  (100%)
  │
  ├─ logging() ──────────────  (25%)  <- Неожиданно!
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

**Результат:** allocation rate 500 MB/s -> 50 MB/s.

Это не экзотический пример -- конкатенация строк в логировании одна из самых частых allocation-проблем. Даже если уровень DEBUG выключен, оператор `+` создаёт StringBuilder и промежуточные String-объекты ДО вызова метода `debug()`. Parameterized logging (`{}`) откладывает конкатенацию до момента, когда известно, что лог действительно нужен.

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

1. **Leak Suspects Report** -> автоматически находит потенциальные leaks
2. **Dominator Tree** -> объекты с наибольшей retained size
3. **Histogram** -> группировка по классу

**Типичный leak:**
```
CacheEntry instances holding 600MB
-> Unbounded cache в UserService
-> Fix: добавить eviction policy (LRU, max size)
```

---

## Lock Profiling: найти contention

### Симптомы

- High CPU, но низкий throughput
- Threads в BLOCKED state
- Добавление threads не помогает

### Как отличить lock contention от других проблем

Lock contention -- коварная проблема, потому что её симптомы похожи на другие bottleneck. Вот систематический подход к диагностике.

**Шаг 1: Thread dump.** Если большинство потоков в состоянии `BLOCKED` или `WAITING` с одним и тем же monitor -- это lock contention. Если потоки в `RUNNABLE` с высоким CPU -- это CPU-bound проблема. Если потоки в `TIMED_WAITING` на I/O -- это I/O bottleneck. Thread dump даёт мгновенный снимок; для надёжности сделайте 3-5 дампов с интервалом 5 секунд и сравните -- если одни и те же потоки "застряли" на одном мониторе, это подтверждает contention.

**Шаг 2: Соотношение CPU и throughput.** При lock contention CPU может быть высоким (потоки активно крутятся в spin-lock) или низким (потоки заблокированы и спят). В обоих случаях throughput непропорционально низкий. Если 8 потоков потребляют 800% CPU, а throughput как у 2 потоков -- классический признак contention: потоки тратят большую часть времени на ожидание и переключение контекста.

**Шаг 3: Lock profiling.** async-profiler с `-e lock` показывает, сколько времени потоки проводят в ожидании каждой конкретной блокировки. Flame graph покажет не CPU-time, а wait-time -- ширина полосы пропорциональна суммарному времени ожидания данного lock. Это позволяет отличить contention от медленного кода под lock: если lock держится долго потому что код внутри медленный, нужно оптимизировать код; если lock держится недолго, но много потоков ждут -- нужно уменьшить granularity блокировки.

**Шаг 4: Решение.** В зависимости от диагноза: переход от `synchronized` к `ReentrantLock` с fair=false; striped locking (разбить один lock на несколько по ключу); lock-free структуры (`ConcurrentHashMap`, `AtomicInteger`); полное устранение общего состояния (thread-local, immutable data).

### Пример

```bash
./profiler.sh -d 60 -e lock -f lock.html <pid>
```

**Результат:**
```
workerThread() ────────────────────────────────  (100%)
  │
  └─ synchronized(lock) ───────────────  (70%) <- Bottleneck!
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

**Результат:** 8 threads: 50K -> 500K ops/sec (10x).

---

## Best Practices для Production

**1. Sampling, не instrumentation**

Sampling делает снимки стека с интервалом (например, каждые 10ms) -- overhead <1%. Instrumentation вставляет код в каждый метод -- overhead 10-50%. На production разница критична: 1% overhead незаметен, 50% -- сервис под нагрузкой упадёт. Но есть и менее очевидная причина: instrumentation изменяет поведение программы. Добавление байткода в каждый метод меняет inlining decisions JIT-компилятора, сдвигает timing многопоточного кода и может маскировать или создавать race conditions. Sampling наблюдает за программой, не вмешиваясь -- как скрытая камера vs камера, на которую все смотрят.

**2. Профилируй 30-60 секунд**

Почему не 5 секунд? Sampling -- статистический метод. При частоте 100 samples/sec за 5 секунд вы получите 500 samples. Метод, занимающий 2% CPU, попадёт в 10 samples -- статистическая погрешность огромна. За 30 секунд -- 3000 samples, тот же метод попадёт в 60 samples -- достаточно для достоверной оценки. Brendan Gregg рекомендует 30-60 секунд как оптимальный баланс между достоверностью и размером данных.

Почему не 5 минут? Во-первых, объём данных растёт линейно, а дополнительная информация -- логарифмически. Паттерн уже виден после 30 секунд, дополнительные 4 минуты добавят точности, но не изменят выводы. Во-вторых, длинные сессии "размазывают" картину: если за 5 минут было 2 минуты нагрузки и 3 минуты idle, hotspots будут выглядеть менее выражено. Исключение: профилирование startup -- тогда достаточно 10 секунд, потому что startup -- детерминированный процесс с фиксированным набором операций.

**3. Профилируй под реальной нагрузкой**

Профиль idle приложения бесполезен -- там нет hotspots. Нужен трафик, желательно production-like. Используйте load testing (Gatling, k6) или профилируйте прямо на production (async-profiler безопасен). Важно: нагрузка должна быть представительной. Если в production 80% запросов -- чтение, а 20% -- запись, то load test с 50/50 покажет другие hotspots. Идеал -- replay production traffic (через shadow traffic или запись/воспроизведение).

**4. Фильтруй свой код**

`--include 'com/myapp/*'` исключает framework код из flame graph. Иначе 80% графа -- это Spring/Hibernate internals, которые вы не можете оптимизировать. Ищите проблемы в своём коде. Однако иногда стоит посмотреть и на framework код: если вы видите `ObjectMapper.writeValueAsString()` в 40% CPU -- это не "Spring internals", а следствие вашего архитектурного решения (создание ObjectMapper на каждый запрос).

**5. Сохраняй raw data**

`./profiler.sh -o collapsed > stacks.txt` сохраняет сырые стеки. Позже можно перегенерировать flame graph с другими фильтрами, сравнить с будущими профилями, провести детальный анализ. HTML визуализация -- удобна, но raw data -- полнее. Это как сохранять RAW-фото вместо JPEG: из RAW всегда можно получить JPEG, обратное невозможно. Месяц спустя, когда нужно будет сравнить "до" и "после" оптимизации, collapsed stacks позволят сделать diff-flame graph.

**6. Используй wall-clock mode для I/O-bound приложений**

CPU profiling показывает только время, когда поток активен на CPU. Если поток ждёт I/O (база данных, сеть, диск), он не потребляет CPU и невидим для CPU-профайлера. `./profiler.sh -e wall -d 30` записывает samples по реальному времени, включая ожидание. Это критично для web-приложений, где 90% времени -- ожидание ответа от базы данных.

---

## Continuous Profiling в CI/CD

### Зачем нужен continuous profiling

Традиционное профилирование -- реактивный подход: проблема возникает, разработчик запускает профайлер, ищет bottleneck. Continuous profiling -- проактивный: профайлер работает всегда, собирая данные каждую минуту каждого дня. Когда проблема обнаруживается через мониторинг, данные уже есть.

Netflix, Google и Uber используют continuous profiling как стандартную практику. Google Profiler (описанный в paper "Google-Wide Profiling: A Continuous Profiling Infrastructure for Data Centers", 2010) собирает профили всех production-сервисов с overhead менее 0.5%. Это позволяет не только реагировать на инциденты, но и отслеживать performance regression между деплоями.

### Инструменты и интеграция

Pyroscope, Grafana Phlare и Parca -- open-source решения для continuous profiling. Они интегрируются с async-profiler (JVM agent) и отправляют данные в централизованное хранилище. В CI/CD pipeline это работает так: при каждом деплое автоматически начинается сбор профилей. Через 10 минут после деплоя система сравнивает profile текущей версии с предыдущей. Если какой-то метод стал потреблять на 20%+ больше CPU -- alert.

Ключевое преимущество continuous profiling -- diff flame graphs. Это flame graph, показывающий не абсолютные значения, а разницу между двумя профилями. Красные участки -- регрессия (метод стал медленнее), зелёные -- улучшение. Это позволяет отследить влияние конкретного pull request на performance ещё до того, как пользователи заметят деградацию.

---

## Сравнение профайлеров

| | async-profiler | VisualVM | JProfiler | JFR |
|---|---|---|---|---|
| **Overhead (prod)** | <1% | 2-5% | 1-3% | <1% |
| **Flame graphs** | Да | Нет | Plugin | Converter |
| **Production safe** | Да | Sampling | Да | Да |
| **Цена** | Free | Free | $499 | Free |
| **Safepoint bias** | Нет | Да | Да | Частично |
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
Профиль: alloc flame graph -> String.concat() = 25%
Причина: logger.debug("User: " + userId) создаёт String даже если DEBUG off
Fix: logger.debug("User: {}", userId)
Результат: Allocation rate 500 MB/s -> 50 MB/s

Case 3: Lock contention
Симптом: 16 threads, но throughput как на 2
Профиль: lock flame graph -> synchronized = 70%
Причина: Global lock на весь cache
Fix: ConcurrentHashMap + striped locking
Результат: Throughput 5x
```

---

## Распространённые заблуждения

| Заблуждение | Почему это неверно |
|-------------|-------------------|
| "Профилирование замедляет приложение" | **Sampling profilers** (async-profiler) имеют <1% overhead. Безопасно для production. Путаница возникает из-за опыта с instrumentation-профайлерами (HPROF, старый JProfiler), которые действительно замедляли приложение на 30-50% |
| "JProfiler/YourKit лучше async-profiler" | Для **CPU profiling** async-profiler точнее (no safepoint bias). Для memory analysis и GUI-навигации -- JProfiler/YourKit удобнее. Это разные инструменты для разных задач |
| "Flame graph показывает время выполнения" | Flame graph показывает **количество samples**, которое пропорционально CPU-time, но не равно ему. Метод с 100 samples при частоте 100 Hz занимает ~1 секунду CPU, но это статистическая оценка, а не точное измерение |
| "Самый высокий стек = проблема" | Flame graphs читаются по **ширине**, не высоте. Высокий узкий стек -- глубокая рекурсия, но если она узкая, то занимает мало CPU. Широкие полосы -- вот где проблема |
| "Профилировать нужно только при проблемах" | **Continuous profiling** (Pyroscope, Parca) даёт baseline. Видим regression сразу, а не после жалоб пользователей. Google профилирует все production-сервисы всегда |
| "Одного CPU-профиля достаточно" | CPU profiling не видит I/O wait, lock contention, off-heap allocations. Полная картина требует нескольких видов профилирования: CPU + alloc + lock + wall-clock |
| "Профилирование в dev-среде эквивалентно production" | JIT-компилятор принимает разные решения при разной нагрузке. Код, горячий под 10 req/s в dev, может быть холодным под 10000 req/s в production (и наоборот). Production profiling незаменимо |

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

## Связь с другими темами

**[[jvm-performance-overview]]** -- profiling -- это ключевой инструмент в арсенале оптимизации, а performance overview задаёт контекст: какие метрики важны, какой порядок действий, когда профилирование уместно. Без общей картины есть риск оптимизировать не то -- профилирование покажет hotspot, но overview поможет понять, стоит ли его оптимизировать. Начните с overview для стратегии, затем используйте profiling для тактики.

**[[jvm-gc-tuning]]** -- allocation profiling через async-profiler напрямую связан с GC: высокий allocation rate создаёт GC pressure, что ведёт к паузам и снижению throughput. Profiling находит источник проблемы (какой код создаёт объекты), а GC tuning решает её на уровне JVM (выбор сборщика, параметры). Изучайте profiling для диагностики причин, GC tuning -- для настройки решения.

**[[jvm-jit-compiler]]** -- flame graph может показать неожиданные hotspots, связанные с отсутствием JIT-компиляции: interpreted code в 10-100 раз медленнее compiled. Понимание JIT помогает интерпретировать профиль: warmup артефакты, deoptimization, inlining boundaries видны в flame graph. Рекомендуется изучить основы JIT перед глубоким анализом CPU-профилей.

**[[jvm-benchmarking-jmh]]** -- профилирование находит bottleneck, а JMH позволяет измерить эффект оптимизации с научной точностью. Без бенчмарков невозможно доказать, что fix действительно помог -- микрооптимизации часто дают непредсказуемые результаты из-за JIT, GC и CPU cache effects. Используйте profiling для поиска проблемы, JMH для валидации решения.

**[[jvm-production-debugging]]** -- профилирование и debugging -- два complementary инструмента диагностики. Profiling отвечает на вопрос "что медленное?", debugging -- на вопрос "почему это происходит?". Thread dumps, heap dumps, GC logs -- инструменты debugging, которые часто используются совместно с profiling для полной картины. Начните с profiling для локализации проблемы, затем переключитесь на debugging для понимания root cause.

---

## Источники и дальнейшее чтение

- Gregg B. (2020). *Systems Performance: Enterprise and the Cloud, 2nd ed.* -- Фундаментальная книга о performance analysis от создателя flame graphs. Глава 6 (CPUs) и глава 13 (Perf Tools) подробно описывают теорию sampling, методологию USE/RED и flame graph визуализацию. Обязательна для понимания, ПОЧЕМУ profiling работает, а не только КАК.
- Oaks S. (2020). *Java Performance: In-Depth Advice for Tuning and Programming Java 8, 11, and Beyond, 2nd ed.* -- Главы 3 и 4 о CPU и memory profiling JVM-приложений. Практическое руководство с примерами async-profiler, JFR и оптимизации реальных приложений. Лучший источник для JVM-специфичного profiling.
- Pangin A. (2016-2024). *async-profiler documentation and talks.* -- Документация и доклады автора async-profiler. Объясняют архитектуру инструмента, safepoint bias problem и техники low-overhead sampling через perf_events. Доклады на JPoint и Joker -- лучший первоисточник.
- Goetz B. (2006). *Java Concurrency in Practice.* -- Необходим для понимания lock contention profiling: объясняет synchronized, ReentrantLock, atomic operations на глубоком уровне. Без этих знаний lock flame graph невозможно интерпретировать корректно.

---

---

## Проверь себя

> [!question]- Почему async-profiler точнее JProfiler/YourKit для CPU profiling и в чём суть safepoint bias?
> JVM может остановить поток для sampling только в safepoint (вызов метода, возврат, обратный переход цикла). Длинный цикл без safepoints невидим для JVM-based профайлеров. async-profiler использует OS-уровень (perf_events/dtrace) и делает snapshot в любой момент, без привязки к safepoints. Результат: hotspots, скрытые в циклах, становятся видимыми.

> [!question]- Сценарий: allocation flame graph показывает 25% в String.format() внутри logger.debug(). Уровень DEBUG отключён в production. Почему объекты всё равно создаются?
> Оператор конкатенации (+) вычисляется ДО вызова метода debug(). Строки "User: " + userId создают StringBuilder и промежуточные String-объекты до того, как debug() проверит уровень логирования. Parameterized logging (logger.debug("User: {}", userId)) откладывает конкатенацию до момента, когда известно, что лог нужен.

> [!question]- Как отличить lock contention от CPU-bound проблемы по thread dump и метрикам?
> Lock contention: потоки в BLOCKED/WAITING на одном мониторе, CPU может быть высоким, но throughput непропорционально низкий. CPU-bound: потоки в RUNNABLE, CPU высокий, throughput пропорционален количеству ядер. Подтверждение: 3-5 thread dumps с интервалом 5 секунд -- если одни и те же потоки застряли на одном мониторе, это contention.

> [!question]- Почему профилирование в dev-среде может показать другие hotspots, чем в production?
> JIT-компилятор принимает разные решения при разной нагрузке: inlining, escape analysis, branch prediction зависят от "горячести" кода. При 10 req/s в dev код может оставаться в interpreted mode, а при 10000 req/s в production -- быть полностью скомпилирован. Разные allocation patterns, разный GC behavior, разный thread contention.

---

## Ключевые карточки

Какие три типа профилирования покрывают большинство проблем?
?
CPU (горячие методы, overhead <1%), alloc (allocation hotspots, GC pressure, 5-10%), lock (thread contention, 10-20%). Для полной картины добавляют wall-clock mode, который видит I/O wait.

Как читать flame graph: что означает ширина и высота?
?
Ширина пропорциональна количеству samples (CPU time). Высота -- глубина стека вызовов. Широкая полоса вверху (flat top) -- CPU-bound hotspot. Высокий узкий стек -- глубокая рекурсия, не обязательно проблема. Искать самые широкие полосы.

Что такое continuous profiling и зачем он нужен?
?
Профайлер работает всегда в production с overhead <1%. Собирает данные каждую минуту. При инциденте данные уже есть. Diff flame graphs показывают регрессию между деплоями. Используют Netflix, Google, Uber. Инструменты: Pyroscope, Grafana Phlare, Parca.

Почему sampling лучше instrumentation для production?
?
Sampling: снимки стека каждые 10мс, overhead <1%, не меняет поведение программы. Instrumentation: код в каждый метод, overhead 10-50%, изменяет inlining и timing. Sampling -- наблюдение без вмешательства, instrumentation -- вмешательство, искажающее результат.

Какой нормальный allocation rate для web-приложения?
?
100-500 MB/s нормально. Свыше 1 GB/s -- почти всегда проблема. Allocation rate определяет частоту Young GC: при Young Gen = 1 GB и rate = 500 MB/s, Young GC каждые 2 секунды. Каждый Young GC -- STW пауза 5-50мс (G1).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[jvm-benchmarking-jmh]] | Валидировать эффект оптимизации после профилирования |
| Углубиться | [[jvm-production-debugging]] | Thread dumps, heap dumps как дополнение к profiling |
| Связанная тема | [[jvm-gc-tuning]] | Allocation profiling напрямую связан с GC tuning |
| Смежная область | [[observability]] | Профилирование как часть observability-стека в production |
| Обзор | [[jvm-overview]] | Вернуться к карте раздела |

---

*Проверено: 2026-02-11 | Источники: Gregg (2020), Oaks (2020), Pangin (2016-2024), Goetz (2006) -- Педагогический контент проверен*
