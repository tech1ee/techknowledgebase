---
title: "JVM Production Debugging: диагностика без downtime"
created: 2025-11-25
modified: 2025-12-02
type: deep-dive
tags:
  - jvm
  - production
  - debugging
  - troubleshooting
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-profiling]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-performance-overview]]"
---

# JVM Production Debugging: диагностика без downtime

Диагностика проблем на работающем сервисе без его остановки: thread dump показывает что делает каждый поток прямо сейчас, heap dump — snapshot всех объектов в памяти, Java Flight Recorder (JFR) — continuous profiling с overhead <2%.

3 часа ночи, сервис тормозит, CPU 100%. Remote debugging в production — никогда (останавливает JVM). Heap dump на 8GB heap = 10-60 секунд Full GC пауза. Thread dump безопасен (~100ms). JFR можно держать включённым постоянно. Правильный выбор инструмента — разница между 5-минутной диагностикой и часами даунтайма.

---

## Что безопасно, что нет

| Инструмент | Безопасность | Когда использовать |
|------------|--------------|-------------------|
| **JFR** | Safe (<2% overhead) | Всегда, continuous recording |
| **Thread dump** | Safe (~100ms pause) | High CPU, deadlocks |
| **Heap dump** | Risky (Full GC!) | Memory leaks, OOM |
| **Remote debugging** | NEVER | Только dev/staging |

---

## Thread Dump: High CPU / Deadlocks

Thread dump — snapshot состояния всех потоков. Показывает что делает каждый thread прямо сейчас.

### Когда использовать

Thread dump — первый инструмент при проблемах с CPU или отзывчивостью.

**CPU 100%:** Когда все ядра загружены, но приложение не делает полезной работы. Thread dump покажет, какой код выполняется прямо сейчас — обычно это infinite loop, неэффективный алгоритм или busy wait. Найдите потоки в состоянии RUNNABLE и посмотрите их stack trace.

**Приложение "зависло":** Запросы не обрабатываются, но CPU низкий. Это признак deadlock — потоки ждут друг друга. JVM автоматически детектирует deadlock и выводит его в thread dump с полной цепочкой ожиданий.

**Slow response:** Latency выросла, но CPU не 100%. Thread dump покажет, где потоки застряли — обычно это BLOCKED state (ждут lock) или WAITING (ждут I/O, sleep, или condition). Если много потоков blocked на одном lock — это contention bottleneck.

### Как взять

```bash
# Способ 1: jstack (рекомендую)
jstack <pid> > thread-dump.txt

# Способ 2: kill -3 (выводит в stdout приложения)
kill -3 <pid>

# Способ 3: jcmd
jcmd <pid> Thread.print > thread-dump.txt
```

### Что искать

**High CPU — найти RUNNABLE threads:**

```
"http-worker-42" #42 prio=5 os_prio=0 tid=0x00007f... nid=0x1234 runnable
   java.lang.Thread.State: RUNNABLE
        at com.example.OrderService.calculateTotal(OrderService.java:156)
        at com.example.OrderController.getOrder(OrderController.java:42)
        ...
```

Метод `calculateTotal` в строке 156 — вероятный hotspot.

**Deadlock — JVM сама найдёт:**

```
Found one Java-level deadlock:
=============================
"Thread-1":
  waiting to lock monitor 0x00007f... (object 0x000000..., a java.lang.Object),
  which is held by "Thread-2"

"Thread-2":
  waiting to lock monitor 0x00007f... (object 0x000000..., a java.lang.Object),
  which is held by "Thread-1"
```

**Blocked threads — много BLOCKED:**

```
"http-worker-15" #15 prio=5 ... BLOCKED
   - waiting to lock <0x000000076b2a8c40> (a java.util.HashMap)
   - locked by "http-worker-7"
```

### Анализ

**fastthread.io** — бесплатный онлайн-анализатор. Загрузите dump, получите визуализацию: группировка потоков по состоянию, автоматическое обнаружение deadlock, heatmap загруженности. Удобно для быстрого анализа без установки инструментов.

**IntelliJ IDEA** → Analyze → Analyze Stacktrace: вставьте thread dump, IDE раскрасит его и сделает кликабельными ссылки на код. Можно сразу перейти к проблемному методу.

**Техника множественных dump'ов:** Один dump — snapshot момента, который может быть случайным. Возьмите 3 dump'а с интервалом 5-10 секунд. Если поток на том же месте во всех трёх — это не случайность, а реальная проблема. Если позиция меняется — поток работает, просто медленно.

---

## Heap Dump: Memory Leaks / OOM

Heap dump — snapshot всех объектов в памяти. Тяжёлый инструмент.

### Опасность

```
⚠️ Heap dump вызывает Full GC!

Heap 8GB → dump занимает:
- 10-60 секунд паузы
- 8GB на диске
- Может убить приложение если диск заполнится
```

### Когда использовать

Heap dump — тяжёлая артиллерия, используйте только когда другие методы не помогли.

**OutOfMemoryError:** Приложение упало с OOM. Настройте `-XX:+HeapDumpOnOutOfMemoryError` заранее — при OOM JVM автоматически сохранит dump. Без этого флага после OOM уже поздно что-то делать.

**Memory растёт и не падает:** Метрики показывают, что heap usage после GC не возвращается к baseline, а растёт с каждым циклом. Это классический признак memory leak — объекты создаются, но не освобождаются.

**Подозрение на leak:** Частые Full GC, но память не освобождается. Или Old Gen постоянно заполнен. Heap dump покажет, какие объекты занимают память и кто их держит (GC roots path).

### Как взять

```bash
# Рекомендуемый способ (только live объекты)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Или jmap
jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>

# Автоматически при OOM (настроить заранее!)
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/java/ \
     -jar myapp.jar
```

### Анализ в Eclipse MAT

Eclipse Memory Analyzer Tool (MAT) — стандартный инструмент для анализа heap dump. Открывает файлы размером в десятки гигабайт.

**Leak Suspects Report** — первое, что смотреть. MAT автоматически анализирует dump и выдаёт список подозрительных объектов: "Problem Suspect 1: 150,000 instances of com.example.CacheEntry loaded by system class loader occupy 600MB". Часто этого достаточно для диагностики.

**Dominator Tree** — показывает, какие объекты "владеют" наибольшим количеством памяти. Retained size — сколько памяти освободится, если удалить объект. Dominator с большим retained size и маленьким shallow size — это объект, который держит много других объектов (например, collection).

**Histogram** — группировка объектов по классу. Если видите миллион объектов `byte[]` — это не обязательно проблема (строки хранятся в byte[]). Но миллион объектов вашего `CacheEntry` — повод разобраться.

**Типичный leak:**

```
Class                          | Objects | Retained Heap
-------------------------------|---------|---------------
byte[]                         | 450,000 | 1.2 GB
com.example.CacheEntry         | 150,000 | 600 MB ← Подозрительно!
```

Причина: unbounded cache в `UserService`. Fix: добавить eviction.

---

## Java Flight Recorder (JFR)

Continuous profiling с минимальным overhead. Можно держать включённым постоянно.

### Запуск

```bash
# При старте приложения
java -XX:StartFlightRecording=filename=recording.jfr,settings=profile \
     -jar myapp.jar

# На работающем приложении
jcmd <pid> JFR.start name=my-recording settings=profile duration=60s
jcmd <pid> JFR.dump name=my-recording filename=recording.jfr
jcmd <pid> JFR.stop name=my-recording
```

### Что записывает

JFR собирает данные из всех подсистем JVM с минимальным overhead (< 2%).

**CPU sampling:** Какие методы потребляют CPU. В отличие от async-profiler, JFR встроен в JVM и не требует установки. Результат — flame graph с процентным распределением времени по методам.

**Memory allocations:** Где создаются объекты. Показывает allocation rate по классам и stack traces создания. Позволяет найти код, создающий много временных объектов (GC pressure).

**GC events:** Каждая сборка мусора: тип (Young/Old/Full), длительность, причина (allocation failure, System.gc(), ergonomics). Помогает понять паттерн GC и настроить параметры.

**Lock contention:** Какие lock'и contested и сколько времени потоки на них ждут. Незаменимо для диагностики проблем с synchronized и ReentrantLock.

**I/O events:** Медленные файловые и сетевые операции. Показывает, какие методы делают I/O и сколько времени это занимает.

### Анализ

**JDK Mission Control (JMC):**

```bash
# Установка
sdk install jmc

# Запуск
jmc
# File → Open → recording.jfr
```

**Ключевые вкладки JMC:**

**Automated Analysis** — начните с этой вкладки. JMC анализирует recording и выдаёт рекомендации с приоритетами: "High: Thread contention on java.util.concurrent.locks.ReentrantLock consuming 45% of CPU time". Каждая рекомендация кликабельна — переходит к деталям.

**Method Profiling** — интерактивный flame graph. Ширина полосы = % CPU времени. Hover показывает детали, click — zoom на поддерево. Ищите широкие полосы внизу графа — это ваш код, который тратит больше всего времени.

**Memory → Allocation** — таблица с allocation rate по классам и stack traces. Отсортируйте по allocation rate — если `byte[]` или `String` в топе, посмотрите кто их создаёт (expand stack trace).

**Lock Instances** — таблица contended locks. Показывает сколько времени потоки провели в ожидании каждого lock'а. Высокий contention time = bottleneck, который ограничивает параллелизм.

---

## Troubleshooting по симптомам

### High CPU

```
1. jstack <pid> > dump1.txt
2. sleep 10
3. jstack <pid> > dump2.txt
4. Сравнить: какие threads RUNNABLE в обоих dumps?
5. Найти метод → профилировать детальнее через JFR
```

### High Memory / OOM

```
1. Проверить GC логи: частые Full GC?
2. Если memory растёт постоянно → leak
3. Включить -XX:+HeapDumpOnOutOfMemoryError
4. Дождаться OOM или взять heap dump вручную
5. Анализ в Eclipse MAT → Leak Suspects
```

### Slow Response

```
1. JFR recording на 1-2 минуты
2. JMC → Method Profiling → где время?
3. Частые причины:
   - GC паузы → см. [[jvm-gc-tuning]]
   - Lock contention → JMC → Lock Instances
   - I/O → JMC → I/O tab
```

### Deadlock

```
1. jstack <pid> | grep -A 100 "deadlock"
2. JVM выведет цепочку locks
3. Fix: изменить порядок захвата locks
```

---

## Production Checklist

Настроить ЗАРАНЕЕ, до проблем:

```bash
java \
  # Heap dump при OOM
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/java/ \

  # GC логи
  -Xlog:gc*:file=/var/log/java/gc.log:time,level,tags \

  # JFR continuous recording
  -XX:StartFlightRecording=disk=true,maxsize=500m,maxage=1d \

  # JMX для мониторинга
  -Dcom.sun.management.jmxremote \

  -jar myapp.jar
```

---

## Quick Reference: команды

| Задача | Команда |
|--------|---------|
| Thread dump | `jstack <pid> > dump.txt` |
| Heap dump | `jcmd <pid> GC.heap_dump /tmp/heap.hprof` |
| Start JFR | `jcmd <pid> JFR.start name=rec duration=60s` |
| Dump JFR | `jcmd <pid> JFR.dump name=rec filename=rec.jfr` |
| Stop JFR | `jcmd <pid> JFR.stop name=rec` |
| GC trigger | `jcmd <pid> GC.run` |
| VM info | `jcmd <pid> VM.info` |
| List running JVMs | `jps -l` |

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Heap dump = downtime" | `jcmd` heap dump **останавливает** app, но обычно <1 минуты. Планируйте на off-peak |
| "JFR слишком дорогой для production" | JFR имеет **<2% overhead**. Netflix, Amazon используют постоянно. Включайте заранее |
| "Thread dump покажет deadlock" | Thread dump показывает **текущее состояние**. Deadlock может быть intermittent. Несколько дампов нужно |
| "GC logs достаточно для диагностики" | GC logs показывают симптомы. Причину ищем через **allocation profiling** (async-profiler) |
| "Профилирование = замедление" | Sampling profilers (async-profiler) имеют **<1% overhead**. Не путать с instrumenting profilers |

---

## CS-фундамент

| CS-концепция | Применение в Production Debugging |
|--------------|----------------------------------|
| **Observability** | Logs + Metrics + Traces. Понимание внутреннего состояния системы |
| **Sampling vs Instrumentation** | Sampling (async-profiler): низкий overhead, статистически точен. Instrumentation: точен, но дорогой |
| **Root Cause Analysis** | От симптома (slow, OOM) к причине. Систематический подход через инструменты |
| **Post-mortem Analysis** | Heap dump, JFR recording, GC logs — данные собранные до/во время инцидента |
| **Distributed Tracing** | Trace ID через микросервисы. OpenTelemetry, Jaeger для end-to-end visibility |

---

## Связи

- [[jvm-profiling]] — детальное профилирование (async-profiler, flame graphs)
- [[jvm-gc-tuning]] — если проблема в GC
- [[jvm-performance-overview]] — общая карта оптимизации
- [[jvm-memory-model]] — понимание heap структуры

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
