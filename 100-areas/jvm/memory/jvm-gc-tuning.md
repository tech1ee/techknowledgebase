---
title: "GC Tuning: выбор и настройка сборщика мусора"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - gc
  - performance
  - g1
  - zgc
  - type/deep-dive
  - level/intermediate
type: deep-dive
status: published
area: programming
confidence: high
related:
  - "[[jvm-performance-overview]]"
  - "[[jvm-memory-model]]"
  - "[[jvm-profiling]]"
---

# GC Tuning: выбор и настройка сборщика мусора

> **TL;DR:** Выбор GC зависит от требований: **G1** (default) — баланс пауз/throughput для 90% приложений; **ZGC** — паузы <10ms даже на TB heap, но -10-15% throughput; **Parallel** — максимум throughput для batch, паузы 100ms-1s. Правило: heap = 3-4x live data. Netflix перешли на ZGC и снизили ошибки с 2000/сек до 100/сек.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Память JVM | Понимать Heap, Stack, Metaspace | [[jvm-memory-model]] |
| Как работает JVM | Общая архитектура | [[jvm-basics-history]] |
| OS память | Виртуальная память, paging | [[os-memory-management]] |

---

Garbage Collector освобождает память от объектов без ссылок. JVM предлагает несколько сборщиков: Parallel GC максимизирует throughput для batch-обработки, G1 балансирует паузы и пропускную способность, ZGC держит паузы под 10ms даже на терабайтных heap.

p99 latency скачет до секунд? CPU 100%, но throughput падает? Full GC на 5 секунд? "Просто увеличить heap" — не решение. G1 работает для 90% веб-приложений при правильных параметрах: MaxGCPauseMillis, InitiatingHeapOccupancyPercent, размеры регионов. ZGC для low-latency, Parallel для batch.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **STW (Stop-The-World)** | Пауза, когда все потоки остановлены для GC | Остановка конвейера для уборки |
| **Throughput** | Доля времени на полезную работу (не GC) | КПД = работа / (работа + уборка) |
| **Minor GC** | Сборка только Young Generation | Ежедневная уборка в комнате |
| **Major/Full GC** | Сборка всего heap, включая Old Gen | Генеральная уборка всей квартиры |
| **G1 Region** | Блок памяти в G1 (обычно 1-32MB) | Комната в квартире — можно убрать отдельно |
| **Humongous** | Объект >50% размера региона в G1 | Огромный шкаф, занимающий несколько комнат |
| **IHOP** | Порог запуска concurrent marking | Когда начинать уборку: при 45% заполнении или раньше |
| **Colored Pointers** | Метаданные в указателях ZGC | Цветные метки на коробках для быстрой сортировки |
| **Live Data** | Объекты, достижимые от GC roots | То, что реально используется и нельзя выбросить |
| **GC Roots** | Стартовые точки для поиска живых объектов | Отправные точки для инвентаризации |

---

## Фундаментальный компромисс GC

Любой сборщик мусора решает одну задачу: найти и освободить память от недостижимых объектов. Но способ решения определяет, что именно вы получите — и чем заплатите.

**Stop-the-world (STW) паузы** — время, когда все потоки приложения остановлены. Чем короче паузы, тем больше накладных расходов: сборщик тратит CPU на координацию с работающим приложением вместо того, чтобы просто остановить его и собрать мусор.

**Throughput** — доля времени, которую приложение тратит на полезную работу (а не на GC). Если приложение работает 95 секунд из 100, throughput = 95%.

Эти метрики противоположны. Parallel GC максимизирует throughput за счёт длинных пауз. ZGC минимизирует паузы, но отдаёт 10-15% throughput на накладные расходы concurrent-фазы. G1 — компромисс посередине.

| Сценарий | GC | Паузы | Throughput | Почему |
|----------|-----|-------|------------|--------|
| **Batch processing** | Parallel GC | 100-1000ms | 95%+ | Паузы не важны, важна скорость |
| **Web API** | G1 GC | 50-200ms | 85-90% | Баланс для p99 latency |
| **Low-latency** | ZGC | <10ms | 80-85% | SLA важнее throughput |
| **Контейнеры <512MB** | Serial GC | Варьируется | OK | Минимум памяти под GC |

```bash
# Batch (максимум throughput)
java -XX:+UseParallelGC -Xms8g -Xmx8g MyApp

# Web API (баланс)
java -XX:+UseG1GC -Xms4g -Xmx4g MyApp

# Low-latency
java -XX:+UseZGC -Xms16g -Xmx16g MyApp
```

---

## G1 GC (default, для большинства)

G1 (Garbage First) стал дефолтным сборщиком в Java 9 не случайно. Он решает главную проблему веб-приложений: непредсказуемые паузы при большом heap.

Традиционные сборщики (Parallel, CMS) работают с монолитными областями памяти. Когда Old Gen занимает 10GB и нужна очистка — собирается весь Old Gen целиком. Пауза может длиться секунды.

### Идея регионов

G1 разбивает heap на множество небольших регионов (обычно 2048 штук). Каждый регион — самостоятельная единица, которую можно собрать отдельно. Вместо "собрать весь Old Gen" G1 говорит: "У меня есть 50ms на паузу. Какие регионы содержат больше всего мусора? Соберу сначала их."

Отсюда название: Garbage First — сначала мусор. G1 ведёт статистику по каждому региону и всегда начинает с самых "мусорных".

```
Heap = регионы разного типа:
┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ E │ E │ E │ S │ O │ O │ O │ H │ F │
└───┴───┴───┴───┴───┴───┴───┴───┴───┘
  ↑       ↑   ↑       ↑   ↑   ↑
 Eden  Survivor Old  Humongous Free
```

**Типы регионов:**
- **Eden (E)** — новые объекты. G1 динамически выделяет регионы под Eden по мере необходимости
- **Survivor (S)** — объекты, пережившие Minor GC. Перемещаются между регионами несколько раз
- **Old (O)** — долгоживущие объекты после 15 циклов GC
- **Humongous (H)** — объекты больше 50% размера региона. Занимают несколько смежных регионов
- **Free (F)** — свободные регионы в пуле

**Почему Humongous — проблема:** Большой массив на 10MB при регионах по 4MB займёт 3 смежных региона. Эти регионы нельзя собрать частично — только все вместе. И они сразу считаются "старыми", даже если объект живёт миллисекунду. Много humongous-объектов ломают всю идею инкрементальной сборки.

### Основные параметры

G1 — adaptive collector. Он сам подстраивает внутренние параметры под ваш target. Ваша задача — правильно задать цели.

```bash
# Target max pause (default: 200ms)
-XX:MaxGCPauseMillis=100

# Когда запускать concurrent marking (default: 45%)
-XX:InitiatingHeapOccupancyPercent=35

# Размер региона (auto: heap/2048)
-XX:G1HeapRegionSize=8m
```

**MaxGCPauseMillis** — это не гарантия, а цель. G1 старается уложиться, но если heap переполнен или объектов слишком много — пауза будет дольше. Слишком агрессивное значение (10ms) приведёт к тому, что G1 будет собирать очень мало за раз и не успеет за allocation rate.

**InitiatingHeapOccupancyPercent (IHOP)** определяет, когда начинать concurrent marking — фоновую фазу, которая определяет живые объекты. Если IHOP слишком высокий (скажем, 70%), marking может не успеть завершиться до того, как heap переполнится → Full GC.

**G1HeapRegionSize** обычно не трогают. Но если много больших объектов (массивы, буферы), увеличение размера региона уменьшит количество humongous-объектов.

### Частые проблемы и решения

**Проблема: Паузы > 200ms**

```bash
# До: p99 pause = 400ms
java -Xms4g -Xmx4g -XX:+UseG1GC MyApp

# После: агрессивный target + раньше запускать marking
java -Xms4g -Xmx4g -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=100 \
     -XX:InitiatingHeapOccupancyPercent=35 \
     MyApp

# Результат: p99 pause = 120ms (throughput -5%)
```

**Проблема: Full GC (паузы 1-10 секунд)**

```
# В логах
[Full GC (Allocation Failure) 3950M->1234M(4096M), 3.456s]
                                                   ↑
                                            3.5 секунды!
```

Причины и решения:
```bash
# 1. Heap переполнился → увеличить
-Xms8g -Xmx8g  # было 4g

# 2. GC не успевает → запускать marking раньше
-XX:InitiatingHeapOccupancyPercent=30  # было 45

# 3. Humongous объекты → увеличить размер региона
-XX:G1HeapRegionSize=16m  # было 2m
```

**Проблема: Premature promotion (объекты уходят в Old Gen слишком рано)**

```bash
# Симптом: Old Gen растёт быстро, частые Mixed GC

# Решение: увеличить Young Gen
-XX:G1NewSizePercent=30     # min Young Gen (default: 5%)
-XX:G1MaxNewSizePercent=60  # max Young Gen (default: 60%)
```

---

## ZGC (low-latency)

ZGC делает то, что раньше считалось невозможным: паузы меньше 10 миллисекунд на heap размером в терабайты. Это не маркетинг — это реальные цифры в production.

### Как это возможно

Традиционные сборщики останавливают приложение, чтобы безопасно перемещать объекты. Пока GC двигает объект, никто не должен читать старый адрес.

ZGC использует colored pointers и load barriers. Каждый указатель на объект содержит метаданные в неиспользуемых битах (на 64-bit системах адресное пространство избыточно). Когда приложение читает указатель, load barrier проверяет цвет и при необходимости обновляет его на лету.

Результат: ZGC перемещает объекты *параллельно* с работающим приложением. Stop-the-world паузы нужны только для начальной синхронизации — это микросекунды, не миллисекунды.

### Цена low-latency

- **CPU overhead 10-15%** — load barriers выполняются при каждом чтении объекта
- **Memory overhead** — ZGC требует больше памяти для своих структур
- **Throughput ниже** — concurrent GC тратит CPU, который мог бы делать полезную работу

Для batch processing, где пауза в 500ms раз в минуту никому не мешает, ZGC — плохой выбор. Вы платите 15% throughput за ненужную вам low-latency.

### Базовая настройка

```bash
java -XX:+UseZGC \
     -Xms16g -Xmx16g \
     -XX:SoftMaxHeapSize=14g \
     MyApp
```

**SoftMaxHeapSize** — мягкий лимит. ZGC старается не превышать его, но может при необходимости. Полезно для контейнеров с memory limits.

### Реальные результаты

```
До (G1):   p99 pause = 150ms, p99.9 = 300ms
После (ZGC): p99 pause = 2ms, p99.9 = 5ms

Tradeoff: throughput -10%, CPU +15%
```

### Когда ZGC не подходит

- **Heap < 4GB** — overhead не оправдан, G1 справится лучше
- **Batch processing** — платите за low-latency, которая не нужна
- **Java < 15** — ZGC был experimental до Java 15
- **32-bit JVM** — colored pointers требуют 64-bit

---

## Parallel GC (максимум throughput)

Parallel GC — самый "тупой" и самый быстрый сборщик. Он не пытается минимизировать паузы. Он просто останавливает приложение и собирает мусор максимально эффективно, используя все доступные ядра.

### Почему он быстрее

G1 и ZGC тратят ресурсы на:
- Отслеживание ссылок между регионами (remembered sets)
- Concurrent phases (фоновое сканирование параллельно с приложением)
- Write/load barriers (перехват записей и чтений)

Parallel GC ничего этого не делает. Он работает по простой схеме:
1. Остановить всё
2. Просканировать heap всеми ядрами параллельно
3. Скопировать живые объекты
4. Продолжить

Меньше overhead = больше времени на полезную работу.

### Когда использовать

- **Batch processing** — обработка данных без interactive latency требований
- **ETL pipelines** — важно обработать N записей за M времени, паузы внутри неважны
- **ML training** — пауза в секунду раз в минуту не влияет на итоговое время
- **Ночные задачи** — никто не ждёт response time

```bash
java -XX:+UseParallelGC \
     -Xms8g -Xmx8g \
     -XX:ParallelGCThreads=8 \
     MyApp
```

**ParallelGCThreads** — количество потоков для GC. По умолчанию равно количеству CPU. На серверах с 64+ ядрами имеет смысл ограничить до 8-16, иначе coordination overhead съедает выигрыш.

Паузы 100-1000ms, но throughput 95%+ (vs 85-90% у G1). Для batch job на час пауза в секунду раз в минуту — это 60 секунд overhead из 3600. Незаметно.

---

## Диагностика GC

GC tuning без данных — гадание. Прежде чем крутить параметры, нужно понять текущее поведение.

### Включить GC логи

GC логи — единственный достоверный источник информации о поведении сборщика. Включайте их всегда, даже в production. Overhead минимален.

```bash
# Java 9+
java -Xlog:gc*:file=gc.log:time,level,tags MyApp

# Java 8
java -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:gc.log MyApp
```

Логи ротируются, можно настроить размер и количество файлов:

```bash
java -Xlog:gc*:file=gc.log:time,level,tags:filecount=5,filesize=10m MyApp
```

### Что смотреть в логах

```
[GC pause (G1 Evacuation Pause) (young) 512M->156M(4096M), 25.4 ms]
          ↑                      ↑       ↑      ↑    ↑       ↑
          |                      |    Before  After Total  Pause
          |                      |
          |                      └─ (young) = Young Gen только
          |                         (mixed) = Young + часть Old
          |
          └─ Evacuation Pause = копирование живых объектов
             в свободные регионы (основная работа G1)
```

**Ключевые метрики:**
- **Pause time** — время stop-the-world. Главная метрика для latency-sensitive приложений
- **Before/After** — сколько памяти было и стало. Если After растёт со временем — утечка
- **Frequency** — как часто происходят GC. Если Young GC каждые 100ms — слишком много аллокаций

**Красные флаги:**
- `[Full GC` — любой Full GC в production требует расследования
- Паузы растут со временем — вероятно memory leak
- `(Allocation Failure)` — heap не успевает освобождаться
- `(to-space exhausted)` — G1 не успел освободить место для копирования объектов

### Инструменты

- **GCViewer** — визуализация GC логов, графики пауз и heap usage
- **GCEasy.io** — онлайн анализ с рекомендациями (загружаешь gc.log, получаешь отчёт)
- **async-profiler** — allocation profiling:

```bash
# Показывает какой код создаёт больше всего объектов
# Flame graph: чем шире полоса — тем больше аллокаций
./profiler.sh -e alloc -d 30 -f alloc.html <pid>

# Результат: "метод parseJson() аллоцирует 80% объектов"
# → Оптимизируй parseJson() или используй object pool
```

---

## Sizing: сколько памяти выделять

Правильный размер heap — ключевой фактор производительности GC. Слишком мало — частые сборки. Слишком много — долгие паузы и waste ресурсов.

### Принцип: GC нужно место для работы

Сборщики мусора копируют живые объекты из одной области в другую. Если живых данных 4GB, а heap всего 5GB, то после копирования остаётся только 1GB свободного места. Следующая сборка начнётся очень скоро.

**Правило 3-4x:** Heap должен быть в 3-4 раза больше размера живых данных после Full GC. Это даёт достаточно пространства для аллокаций между сборками.

### Определение live data

**Live data** — объекты, которые реально используются приложением (достижимы от GC roots: static поля, стек потоков, JNI references). Всё остальное — мусор.

Запустите приложение под нагрузкой и посмотрите heap usage после Full GC:

```bash
# jcmd — CLI утилита для диагностики JVM (входит в JDK)
# <pid> — process ID вашего Java-процесса (узнать: jps или ps aux | grep java)

# Принудительно вызвать Full GC
jcmd <pid> GC.run

# Посмотреть heap usage
jcmd <pid> GC.heap_info
```

Или в GC логах найдите `Full GC` и посмотрите на "after":

```
[Full GC ... 3950M->1234M(4096M), 3.456s]
                  ↑
             Live data = 1234MB
```

### Практические правила

1. **-Xms = -Xmx** — фиксированный размер heap. Resize во время работы вызывает паузы и фрагментацию
2. **Heap = 3-4x live data** — достаточно места для работы GC
3. **Не больше 75% RAM** — остальное нужно для:
   - **OS cache** — файловый кэш ускоряет I/O
   - **Metaspace** — память под классы, методы, constant pool (вне heap!)
   - **Direct ByteBuffers** — off-heap память для NIO (сетевые буферы, mapped files)

### Пример расчёта

```
Live data после Full GC: 2GB
→ Оптимальный heap: 6-8GB
→ Если сервер 12GB RAM: -Xms8g -Xmx8g (OK, остаётся 4GB для OS)
→ Если контейнер 4GB RAM: -Xms3g -Xmx3g (tight! рассмотрите уменьшение cache sizes)
```

**Контейнеры:** JVM видит cgroup limits начиная с Java 10 (до этого JVM видела всю RAM хоста, а не лимит контейнера!).

```bash
# Вместо абсолютных -Xmx — процент от доступной памяти
# JVM сама вычислит heap на основе cgroup limit
java -XX:MaxRAMPercentage=75.0 -XX:InitialRAMPercentage=75.0 MyApp

# В контейнере с memory: 4Gi → heap ≈ 3GB
```

---

## Чеклист GC Tuning

```
□ Выбрал правильный GC для use case
□ Heap size = 3-4x live data
□ -Xms = -Xmx (фиксированный размер)
□ Включил GC логи
□ Нет Full GC в production
□ Паузы в рамках SLA
□ Throughput приемлемый
```

---

## Quick Reference: флаги

| Задача | Флаг |
|--------|------|
| Выбрать G1 | `-XX:+UseG1GC` |
| Выбрать ZGC | `-XX:+UseZGC` |
| Target pause | `-XX:MaxGCPauseMillis=100` |
| Начать marking раньше | `-XX:InitiatingHeapOccupancyPercent=35` |
| Больше Young Gen | `-XX:G1NewSizePercent=30` |
| Размер региона | `-XX:G1HeapRegionSize=8m` |
| GC логи | `-Xlog:gc*:file=gc.log:time,level,tags` |
| Heap dump при OOM | `-XX:+HeapDumpOnOutOfMemoryError` |

---

## Кто использует и реальные примеры

| Компания | GC выбор | Результаты |
|----------|----------|------------|
| **Netflix** | Перешли с G1 на ZGC (JDK 21) | Ошибки 2000/сек → 100/сек, batch на 6-8% быстрее |
| **LinkedIn** | G1 для большинства сервисов | Стабильные паузы ~100ms |
| **Alibaba** | Dragonwell с улучшенным G1 | Оптимизации под их workload |
| **Discord** | ZGC для real-time messaging | Паузы <10ms обязательны для UX |
| **Cassandra** | G1 или ZGC в зависимости от SLA | Latency-sensitive database |

### Netflix Case Study (2024)

```
До (G1):
- p99 pause: 150ms
- p99.9 pause: 300ms
- Peak errors: 2000/sec (из-за timeouts)

После (Generational ZGC, JDK 21):
- p99 pause: 2ms
- p99.9 pause: 5ms
- Peak errors: ~100/sec

Ключевые наблюдения:
- Операционная простота: ZGC работает без тюнинга
- Allocation stalls редки и короткие
- Некоторые workloads всё ещё лучше на G1
```

### Когда какой GC

```
Вопрос: Какой GC выбрать?

if heap < 4GB && latency не критична:
    return G1  # default, просто работает

elif latency SLA < 10ms:
    return ZGC  # готовы платить throughput

elif batch processing (Spark, ETL):
    return Parallel  # максимум throughput

elif контейнер < 512MB:
    return Serial  # минимум overhead

else:
    return G1  # safe default
```

---

## Рекомендуемые источники

### Официальные
- [HotSpot GC Tuning Guide](https://docs.oracle.com/en/java/javase/21/gctuning/) — Oracle официальная документация
- [JEP 439: Generational ZGC](https://openjdk.org/jeps/439) — спецификация нового ZGC

### Статьи
- [Netflix: Bending pause times with Generational ZGC](https://netflixtechblog.com/bending-pause-times-to-your-will-with-generational-zgc-256629c9386b) — реальный опыт миграции
- [Deep Dive into Java GC](https://www.datadoghq.com/blog/understanding-java-gc/) — Datadog детальный разбор
- [How to choose the best GC](https://developers.redhat.com/articles/2021/11/02/how-choose-best-java-garbage-collector) — Red Hat гайд

### Инструменты
- [GCEasy.io](https://gceasy.io/) — онлайн анализ GC логов
- [GCViewer](https://github.com/chewiebug/GCViewer) — визуализация GC логов
- [async-profiler](https://github.com/async-profiler/async-profiler) — allocation profiling

### Книги
- **"Java Performance"** — Scott Oaks, главы про GC
- **"Optimizing Java"** — Evans, Gough, Newland — GC internals

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Чем больше heap, тем лучше" | Большой heap = **длинные паузы GC**. 64GB heap с G1 может иметь паузы по секундам. ZGC/Shenandoah нужны для больших heap'ов |
| "System.gc() очищает память" | System.gc() — **hint**, не команда. JVM может проигнорировать. В production вызов System.gc() — обычно ошибка. `-XX:+DisableExplicitGC` отключает |
| "GC tuning — первый шаг оптимизации" | **Allocation rate** — главная метрика. Если создаёте много мусора, никакой GC не поможет. Сначала профилируйте allocations, потом GC |
| "G1 всегда лучше Parallel GC" | Для **batch processing** (Spark, ETL) Parallel GC может дать лучший throughput. G1 оптимизирован для latency, не throughput |
| "ZGC = серебряная пуля" | ZGC жертвует ~15% throughput ради low latency. Для batch jobs Parallel лучше. ZGC = trade-off, не universal solution |
| "Generational hypothesis не работает для моего приложения" | 95%+ приложений следуют паттерну: большинство объектов живут недолго. Если не так — проблема в архитектуре приложения, не в hypothesis |
| "Нужно тюнить все GC параметры" | Современные GC (G1, ZGC) **самотюнящиеся**. Обычно достаточно `-Xmx` и выбора GC. Over-tuning часто вредит |
| "Full GC = катастрофа" | Periodic full GC — нормально. **Проблема** — частые Full GC из-за нехватки памяти. Occasional full GC в off-peak часы — приемлемо |
| "Metaspace unlimited = хорошо" | Unlimited Metaspace может привести к **OOM при class leak** (hot deploy). Лимит Metaspace помогает детектировать утечки раньше |
| "Логи GC нужны только при проблемах" | GC логи нужны **всегда в production**. `-Xlog:gc*` почти бесплатны, но бесценны для post-mortem анализа |

---

## CS-фундамент

| CS-концепция | Применение в GC Tuning |
|--------------|----------------------|
| **Generational Hypothesis** | "Большинство объектов умирают молодыми". Young Gen собирается часто и дёшево, Old Gen — редко. Основа всех generational collectors |
| **Mark-and-Sweep Algorithm** | Базовый алгоритм GC: отмечаем reachable объекты, удаляем остальные. Варианты: mark-compact (дефрагментация), mark-copy (copying collector) |
| **Stop-The-World (STW)** | Пауза всех application threads во время GC. G1 минимизирует STW, ZGC делает concurrent marking и relocation |
| **Concurrent vs Parallel** | Parallel = несколько GC threads одновременно. Concurrent = GC работает параллельно с приложением. ZGC — mostly concurrent |
| **Write Barrier** | Инструментация записей в heap для отслеживания изменений. G1/ZGC используют write barriers для concurrent marking. Небольшой overhead |
| **Tri-color Marking** | Алгоритм concurrent marking: white (не посещён), gray (посещён, дети не все), black (посещён полностью). Позволяет concurrent traversal |
| **Reference Counting vs Tracing** | JVM использует tracing (reachability). Reference counting не справляется с циклами. Tracing находит все unreachable объекты |
| **Compaction** | Перемещение живых объектов для устранения фрагментации. G1 делает compaction per-region. Необходим для долгоживущих приложений |
| **Safepoints** | Точки в коде где JVM может безопасно приостановить thread для GC. Loop safepoint polling, call safepoints. Time-to-safepoint влияет на паузы |
| **Colored Pointers (ZGC)** | ZGC хранит metadata в указателях (unused bits). Позволяет concurrent relocation без STW. Load barrier декодирует pointer color |

---

## Связи

- [[jvm-performance-overview]] — общая карта оптимизации
- [[jvm-profiling]] — как найти причину GC pressure
- [[jvm-memory-model]] — как работает память JVM
- [[jvm-benchmarking-jmh]] — как измерять влияние GC

---

*Проверено: 2026-01-09 | Источники: Netflix Tech Blog, Oracle docs, Datadog — Педагогический контент проверен*
