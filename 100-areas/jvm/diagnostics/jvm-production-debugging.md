---
title: "JVM Production Debugging: диагностика без downtime"
created: 2025-11-25
modified: 2025-12-02
type: deep-dive
status: published
tags:
  - topic/jvm
  - production
  - debugging
  - troubleshooting
  - type/deep-dive
  - level/intermediate
area: programming
confidence: high
prerequisites:
  - "[[jvm-profiling]]"
  - "[[jvm-memory-model]]"
  - "[[jvm-gc-tuning]]"
related:
  - "[[jvm-profiling]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-performance-overview]]"
  - "[[jvm-memory-model]]"
---

# JVM Production Debugging: диагностика без downtime

Диагностика проблем на работающем сервисе без его остановки --- одна из самых ценных и одновременно рискованных задач в эксплуатации JVM-приложений. Thread dump показывает, что делает каждый поток прямо сейчас. Heap dump --- это snapshot всех объектов в памяти. Java Flight Recorder (JFR) --- continuous profiling с overhead менее 2%. async-profiler --- lightweight sampling без safepoint bias. Каждый инструмент имеет свою цену: от практически бесплатных (thread dump, ~100 мс) до потенциально опасных (heap dump, до минуты Full GC паузы на больших heap'ах).

3 часа ночи, сервис тормозит, CPU 100%. Remote debugging в production --- никогда: он останавливает JVM на breakpoint'ах и блокирует все потоки. Heap dump на 8 GB heap = 10--60 секунд Full GC паузы. Thread dump безопасен (~100 мс). JFR можно держать включённым постоянно. Правильный выбор инструмента --- разница между 5-минутной диагностикой и часами даунтайма.

---

## Зачем это знать

Каждый JVM-сервис рано или поздно столкнётся с проблемой в production: утечка памяти, deadlock, необъяснимый рост latency, 100% CPU без видимой полезной работы. Без навыков production debugging единственный ответ --- перезапуск. Перезапуск устраняет симптом, но не причину. Проблема вернётся --- через час, день, неделю --- и каждый раз это потеря данных, репутации и денег.

Понимание инструментов production debugging позволяет диагностировать проблему за минуты, не останавливая сервис. Это разница между "мы разобрались за 10 минут и выкатили fix" и "мы перезагружали сервер 4 раза за ночь, а утром проблема повторилась".

---

## Терминология

| Термин | Значение | Аналогия из жизни |
|--------|----------|-------------------|
| **Thread dump** | Snapshot состояния всех потоков JVM | Стоп-кадр фильма: все актёры замерли, видно кто что делает |
| **Heap dump** | Snapshot всех объектов в памяти JVM | Рентгеновский снимок организма: видно все органы, но пациент должен замереть |
| **JFR (Java Flight Recorder)** | Встроенный в JVM continuous profiler | Бортовой самописец самолёта: пишет всё, overhead минимален |
| **async-profiler** | Lightweight sampling profiler без safepoint bias | Фотограф-папарацци: снимает актёров в случайные моменты, не просит позировать |
| **Safepoint** | Точка в коде, где JVM может безопасно остановить поток | Красный свет на перекрёстке: поток останавливается только в этих точках |
| **Dominator tree** | Граф владения объектами в heap | Генеалогическое древо: кто "владеет" кем, и сколько памяти освободится при удалении предка |
| **Retained size** | Объём памяти, который освободится при удалении объекта | Весь "клан" потомков, который исчезнет вместе с патриархом |
| **GC root** | Объект, от которого начинается reachability analysis | Корень дерева: пока он жив, все ветви и листья живы |

---

## Историческая справка: от println до JFR

В ранние годы Java (конец 1990-х) основным инструментом "диагностики" был `System.out.println`. Разработчики вставляли print-statement'ы в код, перекомпилировали, деплоили, и пытались понять, что происходит по логам. Это было медленно, требовало перезапуска, и часто меняло timing достаточно, чтобы проблема исчезала (Heisenbug --- проблема, которая пропадает при попытке её наблюдать).

В начале 2000-х появились первые инструменты: `jstack` для thread dump'ов, `jmap` для heap dump'ов, JConsole для мониторинга через JMX. Это был прорыв: впервые можно было заглянуть внутрь работающей JVM без перезапуска.

В 2005 году BEA Systems (позже Oracle после поглощения) создала JRockit Flight Recorder --- встроенный в JRockit JVM профайлер с минимальным overhead. В 2012 году, после слияния HotSpot и JRockit, технология была перенесена в HotSpot под названием **Java Flight Recorder (JFR)**. Изначально JFR был коммерческой функцией и требовал лицензию Java Mission Control. В 2018 году, с выходом Java 11, JFR стал полностью бесплатным и open-source.

Параллельно в 2016 году Andrei Pangin (Odnoklassniki) создал **async-profiler** --- profiler, решающий проблему safepoint bias. Традиционные Java-профайлеры могли собирать stack trace только в safepoint'ах, что давало искажённую картину: код между safepoint'ами был невидим. async-profiler использует `perf_events` (Linux) и `AsyncGetCallTrace` для сбора stack trace в произвольные моменты, включая нативный код и kernel.

Сегодня стандартный набор инструментов для production debugging --- JFR (continuous recording), async-profiler (on-demand profiling), jcmd (thread/heap dumps) и Eclipse MAT (анализ heap dump'ов).

---

## Что безопасно, что нет

| Инструмент | Безопасность | Overhead | Когда использовать |
|------------|--------------|----------|-------------------|
| **JFR** | Safe | <2% | Всегда, continuous recording |
| **Thread dump** | Safe | ~100 мс пауза | High CPU, deadlocks, slow response |
| **async-profiler** | Safe | <1% | CPU hotspots, allocation profiling |
| **Heap dump** | Risky | Full GC, секунды-минуты | Memory leaks, OOM (только off-peak) |
| **Remote debugging** | NEVER | Останавливает JVM | Только dev/staging |

---

## Heap Dumps: рентген JVM-памяти

> **Аналогия:** Heap dump --- это рентгеновский снимок организма. Пациент (JVM) должен замереть на несколько секунд (Full GC пауза), и в этот момент делается детальный снимок всех "органов" (объектов). Снимок показывает всё: размеры, расположение, связи. Но сам процесс съёмки --- это стресс для организма, и делать его стоит только когда другие методы диагностики не помогли.

### Как снять heap dump

Heap dump --- тяжёлая операция. На heap'е в 8 GB dump занимает от 10 до 60 секунд, в течение которых JVM полностью остановлена (Stop-The-World). На heap'е в 32 GB --- минуты. Dump сохраняется в файл формата HPROF, размер которого примерно равен размеру heap'а. Убедитесь, что на диске достаточно места: если диск заполнится во время записи, приложение может упасть.

Есть три способа снять heap dump. Первый --- `jcmd`, рекомендуемый способ. Команда `jcmd <pid> GC.heap_dump /tmp/heap.hprof` сохраняет только live-объекты (те, что переживут GC). Это уменьшает размер dump'а и упрощает анализ, потому что мусор уже отфильтрован. Второй --- `jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>`, аналогичен jcmd, но доступен на более старых версиях Java. Третий --- автоматический dump при OOM, который настраивается заранее через флаг `-XX:+HeapDumpOnOutOfMemoryError`. Этот способ --- самый важный, потому что OOM часто случается неожиданно и в неудобное время. Без этого флага после OOM уже поздно что-то делать: приложение мертво, а память потеряна.

Важный нюанс: опция `live` в jcmd/jmap вызывает Full GC перед dump'ом. Если вы хотите увидеть все объекты (включая мусор), используйте `jcmd <pid> GC.heap_dump -all /tmp/heap.hprof`. Это полезно для диагностики allocation pressure --- когда объекты создаются и умирают слишком быстро.

### MAT Analysis: как читать heap dump

Eclipse Memory Analyzer Tool (MAT) --- стандартный инструмент для анализа heap dump'ов. MAT способен открывать файлы размером в десятки гигабайт, потому что использует индексирование: при первом открытии создаёт набор индексных файлов, и дальнейший анализ работает с ними, а не с исходным dump'ом.

**Leak Suspects Report** --- первое, с чего начинать анализ. MAT автоматически анализирует dump и генерирует список подозрительных объектов: "Problem Suspect 1: 150,000 instances of com.example.CacheEntry loaded by system class loader occupy 600 MB (45% of total heap)". Часто этого достаточно для диагностики. MAT ищет объекты с аномально большим retained size --- те, которые "владеют" непропорционально большой долей памяти.

Как именно MAT определяет "подозрительность"? Он строит dominator tree и ищет объекты, чей retained size составляет значительный процент от общего heap'а. Если один HashMap "владеет" 2 GB из 4 GB --- это подозрительно. MAT также анализирует паттерны: много экземпляров одного класса, коллекции с аномально большим числом элементов, классы, загруженные через нестандартные classloader'ы.

### Dominator Tree: кто владеет памятью

Dominator tree --- это ключевая концепция для понимания heap dump'ов. Объект A доминирует над объектом B, если каждый путь от GC root до B проходит через A. Проще говоря: если удалить A, то B станет unreachable и будет собран GC.

Retained size объекта --- это shallow size самого объекта плюс shallow size всех объектов, которые он доминирует. Это отвечает на вопрос "сколько памяти освободится, если удалить этот объект?". Объект с маленьким shallow size (скажем, 64 байта --- одна ссылка на HashMap), но огромным retained size (2 GB --- все записи в HashMap) --- это типичный "владелец" памяти.

В MAT откройте Dominator Tree, отсортируйте по Retained Heap. Верхние строки --- объекты, владеющие наибольшим количеством памяти. Раскройте их --- увидите дерево "владения". Если на вершине --- ваш `CacheManager` с retained size 3 GB --- проблема ясна: unbounded cache.

### Leak Suspects: типичные паттерны утечек

Утечка памяти в Java --- это не "забыли вызвать free()" (как в C/C++), а ситуация, когда объекты, которые уже не нужны приложению, остаются reachable от GC root. GC не может их собрать, потому что формально кто-то на них ссылается.

Типичные паттерны утечек: unbounded cache (HashMap без eviction, который растёт бесконечно), listener leak (регистрация listener'ов без unregister), classloader leak (custom classloader, на который сохраняется ссылка, держит все загруженные им классы), ThreadLocal leak (ThreadLocal в thread pool --- объект живёт пока жив thread, а в pool'е thread'ы живут вечно).

Для каждого подозрительного объекта в MAT можно посмотреть "Path to GC Roots" --- цепочку ссылок от GC root до объекта. Это показывает, КТО держит объект в памяти. Часто это не тот класс, который создал объект, а тот, который забыл его освободить. Например, `CacheEntry` создаётся в `OrderService`, но держится в `static HashMap` в `CacheManager`.

---

Мы разобрали, как заглянуть в память JVM. Но CPU-проблемы требуют другого инструмента. Что если процессор загружен на 100%, но ни один запрос не обрабатывается?

---

## Thread Dumps: стоп-кадр всех потоков

> **Аналогия:** Thread dump --- это стоп-кадр фильма. Режиссёр кричит "стоп!", и все актёры замирают. Можно обойти площадку и посмотреть, кто что делает: один стоит у двери и ждёт ключ (BLOCKED), другой спит на диване (WAITING), третий активно работает (RUNNABLE). Один стоп-кадр --- случайность. Три стоп-кадра с интервалом 5 секунд --- паттерн. Если актёр стоит у двери во всех трёх кадрах --- он точно застрял.

### Как читать thread dump

Thread dump содержит информацию о каждом потоке JVM: имя, приоритет, состояние (Thread.State), и полный stack trace. Состояние потока --- ключевая информация для диагностики:

**RUNNABLE** --- поток выполняет Java-код или нативный вызов. Если CPU 100%, ищите RUNNABLE-потоки: их stack trace покажет, какой метод "крутится". Но RUNNABLE не всегда означает активную работу: I/O-операции (сетевые вызовы, чтение файлов) тоже показываются как RUNNABLE, хотя поток фактически ждёт ответа от ОС.

**BLOCKED** --- поток пытается войти в synchronized-блок, который уже захвачен другим потоком. Thread dump покажет, какой lock ожидается и кто его держит. Если много потоков BLOCKED на одном lock'е --- это contention bottleneck. Типичная причина: synchronized на HashMap вместо ConcurrentHashMap, или слишком грубая гранулярность блокировок.

**WAITING** --- поток вызвал `Object.wait()`, `Thread.join()`, `LockSupport.park()` или `Condition.await()` без timeout'а. Поток будет ждать, пока другой поток явно его разбудит. Если поток вечно в WAITING --- возможно, notify/signal никогда не придёт.

**TIMED_WAITING** --- то же, что WAITING, но с timeout'ом: `Thread.sleep()`, `Object.wait(timeout)`, `LockSupport.parkNanos()`. Обычно это нормальное состояние: поток ждёт события с timeout'ом и периодически просыпается. Много потоков в TIMED_WAITING на `Thread.sleep` --- возможно, кто-то использует polling вместо event-driven подхода.

### Deadlock Detection: JVM находит тупики автоматически

Deadlock --- ситуация, когда два или более потока ждут друг друга и ни один не может продолжить. Классический пример: поток A захватил lock 1 и ждёт lock 2, а поток B захватил lock 2 и ждёт lock 1. JVM автоматически детектирует такие ситуации при снятии thread dump'а и выводит их в специальном разделе с полной цепочкой ожиданий.

Важно понимать: JVM детектирует только deadlock'и на synchronized-блоках и java.util.concurrent.locks. Deadlock'и на внешних ресурсах (база данных, файловая система, сетевые сокеты) не детектируются. Если два потока ждут ответа друг от друга через HTTP --- JVM этого не увидит.

Для диагностики deadlock'ов достаточно одного thread dump'а --- JVM выведет секцию "Found one Java-level deadlock" с перечислением всех потоков и lock'ов в цепочке. Fix обычно прост: изменить порядок захвата lock'ов так, чтобы все потоки захватывали их в одном и том же порядке (lock ordering).

### Lock Contention: узкое горлышко параллелизма

Lock contention --- ситуация, когда множество потоков конкурируют за один lock. Это не deadlock (потоки продвигаются), но производительность деградирует, потому что в каждый момент только один поток работает, а остальные ждут.

В thread dump'е contention проявляется как множество потоков в состоянии BLOCKED, ожидающих один и тот же monitor. Если 50 из 100 потоков blocked на `java.util.Hashtable.get()` --- это contention. Решение: заменить synchronized-коллекцию на concurrent-аналог, уменьшить гранулярность блокировок, или использовать lock-free структуры данных.

Техника множественных dump'ов --- ключевой приём. Один dump --- snapshot момента, который может быть нерепрезентативным. Три dump'а с интервалом 5--10 секунд дают паттерн. Если поток "застрял" на одном методе во всех трёх dump'ах --- это реальная проблема. Если позиция меняется --- поток работает, просто медленно.

Инструменты для анализа: **fastthread.io** --- бесплатный онлайн-анализатор, который визуализирует thread dump, группирует потоки по состоянию, автоматически детектирует deadlock и contention. **IntelliJ IDEA** (Analyze -> Analyze Stacktrace) --- вставьте dump, IDE раскрасит его и сделает ссылки на код кликабельными.

---

Мы разобрали snapshot-инструменты: thread dump показывает момент, heap dump показывает память. Но что если нужна непрерывная запись? Что если проблема возникает спорадически и её нельзя поймать snapshot'ом?

---

## async-profiler: профилирование без safepoint bias

async-profiler --- lightweight profiler, созданный Andrei Pangin, который решает фундаментальную проблему традиционных Java-профайлеров: safepoint bias. Традиционные профайлеры (VisualVM, JConsole) могут собирать stack trace только в safepoint'ах --- специальных точках в коде, где JVM может безопасно остановить поток. Но safepoint'ы расположены не равномерно: они есть на границах методов, в обратных переходах циклов, но отсутствуют внутри длинных вычислений без ветвлений. Это означает, что "горячий" код между safepoint'ами невидим для традиционного профайлера.

### CPU Profiling

В режиме CPU profiling async-profiler использует `perf_events` (Linux) для получения прерываний от CPU с заданной частотой (по умолчанию каждые 10 мс). В момент прерывания профайлер собирает stack trace потока --- неважно, находится ли поток в safepoint или нет. Это даёт честную картину, где CPU тратит время.

Результат --- flame graph, где ширина полосы пропорциональна количеству samples. Широкая полоса внизу графа --- это ваш код, который потребляет больше всего CPU. Узкие полосы вверху --- это framework-код и JVM internals. Ищите самую широкую "башню" --- это главный hotspot.

На практике async-profiler находит проблемы, невидимые для других инструментов. Например, counted loop (цикл с известным количеством итераций) в HotSpot не имеет safepoint-проверок внутри тела цикла. Если такой цикл работает долго, традиционный профайлер его не увидит. async-profiler увидит.

### Allocation Profiling

В режиме allocation profiling async-profiler отслеживает создание объектов и показывает, где аллоцируется больше всего памяти. Это критично для диагностики GC pressure --- ситуации, когда приложение создаёт слишком много объектов, и GC не успевает их собирать.

Allocation profiling отвечает на вопрос "почему GC работает так часто?". Flame graph покажет stack trace'ы, в которых аллоцируется больше всего объектов. Типичные находки: создание String через конкатенацию в цикле, boxing примитивов (int -> Integer), создание временных объектов в hot path.

### Wall-clock Profiling

Wall-clock profiling --- режим, в котором async-profiler собирает stack trace'ы всех потоков с фиксированным интервалом, независимо от того, работает поток или ждёт. Это полезно для диагностики проблем, связанных с ожиданием: I/O, lock contention, sleep.

В CPU-profiling режиме спящие и заблокированные потоки невидимы --- они не потребляют CPU. В wall-clock режиме видно всё: какой поток сколько времени провёл в ожидании и на чём именно. Если 80% wall-clock времени --- ожидание ответа от базы данных, оптимизация CPU-кода не поможет.

---

## JFR (Java Flight Recorder): бортовой самописец JVM

### Что такое JFR и почему его включают постоянно

Java Flight Recorder --- встроенный в JVM механизм сбора событий с минимальным overhead (менее 2%). JFR записывает информацию из всех подсистем JVM: CPU sampling, memory allocations, GC events, lock contention, I/O operations, class loading, thread events. Записи хранятся в кольцевом буфере: когда буфер заполняется, старые данные перезаписываются новыми.

Ключевое преимущество JFR перед async-profiler: JFR встроен в JVM и собирает данные из подсистем, недоступных внешним инструментам. GC events с деталями (причина сборки, freed bytes, pause time), lock contention с точностью до наносекунд, class loading events --- всё это доступно только через JFR.

Netflix, Amazon, и Alibaba используют JFR в continuous recording mode на всех production-серверах. Когда происходит инцидент, данные за последние часы уже записаны --- не нужно воспроизводить проблему. Это принципиально меняет workflow диагностики: вместо "проблема произошла, давайте попробуем её воспроизвести" --- "проблема произошла, давайте посмотрим recording".

### Events: что записывает JFR

JFR оперирует событиями (events). Каждое событие имеет timestamp, duration, и набор полей, специфичных для типа события.

**CPU sampling events** (`jdk.ExecutionSample`) --- stack trace потока, снятый с заданной частотой. Позволяет строить flame graph, аналогично async-profiler. Отличие: JFR собирает stack trace только в safepoint'ах, что создаёт safepoint bias. Для точного CPU-profiling async-profiler предпочтительнее, но JFR "бесплатен" как часть continuous recording.

**GC events** (`jdk.GarbageCollection`, `jdk.GCPhasePause`) --- каждая сборка мусора с деталями: тип (Young/Old/Full), причина (allocation failure, System.gc(), ergonomics), длительность, объём освобождённой памяти. Это незаменимо для диагностики GC-проблем: если видно, что каждые 5 секунд происходит Young GC на 50 мс, а каждые 5 минут --- Full GC на 3 секунды --- картина проблемы ясна.

**Allocation events** (`jdk.ObjectAllocationInNewTLAB`, `jdk.ObjectAllocationOutsideTLAB`) --- где и какие объекты создаются. TLAB (Thread-Local Allocation Buffer) --- это "личный кусочек" heap'а, выделенный каждому потоку для быстрой аллокации без синхронизации. Аллокация вне TLAB (outside TLAB) --- медленная и требует синхронизации. Если много аллокаций outside TLAB --- это сигнал: объекты слишком большие или TLAB слишком маленький.

**Lock contention events** (`jdk.JavaMonitorWait`, `jdk.JavaMonitorEnter`) --- какие lock'и contested и сколько времени потоки на них ждут. Это более точная информация, чем thread dump, потому что JFR собирает данные за период времени (минуты, часы), а не в один момент.

**I/O events** (`jdk.FileRead`, `jdk.FileWrite`, `jdk.SocketRead`, `jdk.SocketWrite`) --- каждая I/O-операция с duration. Позволяет найти медленные сетевые вызовы и файловые операции.

### Continuous Recording: запись до инцидента

Continuous recording --- режим, в котором JFR записывает данные постоянно в кольцевой буфер. Когда происходит инцидент, вы сохраняете буфер в файл и анализируете. Данные за последние N минут/часов уже собраны.

Настройка при старте приложения: `-XX:StartFlightRecording=disk=true,maxsize=500m,maxage=1d`. Это ограничивает размер записи 500 MB и хранит данные за последние сутки. Overhead менее 2% --- достаточно низкий для постоянного использования в production.

При инциденте: `jcmd <pid> JFR.dump name=default filename=/tmp/incident.jfr`. Файл содержит все события за период, покрытый кольцевым буфером.

### Analysis: JDK Mission Control

JDK Mission Control (JMC) --- GUI-приложение для анализа JFR-записей. Начните с вкладки **Automated Analysis**: JMC анализирует recording и выдаёт приоритизированный список проблем. "High: Thread contention consuming 45% of CPU time", "Medium: Excessive object allocation of 2.3 GB/s", "Low: 15 classes loaded during measurement period".

**Method Profiling** --- flame graph на основе CPU sampling events. Ширина полосы = процент CPU времени. Hover показывает детали, click --- zoom в поддерево. Ищите широкие полосы --- это hotspot'ы.

**Memory -> Allocation** --- таблица allocation rate по классам. Отсортируйте по rate: если `byte[]` или `char[]` в топе, посмотрите stack trace --- кто их создаёт. Частая находка: String конкатенация или JSON serialization в hot path.

**Lock Instances** --- таблица contended locks с total wait time. Высокий wait time = bottleneck параллелизма.

---

## Production War Stories: реальные сценарии

### История 1: "Unbounded cache убил сервис в 3 AM"

E-commerce сервис, heap 8 GB, G1 GC. В 3:00 ночи алерт: latency выросла с 50 мс до 10 секунд, GC pause time --- 4 секунды каждые 30 секунд. Full GC не освобождает память --- Old Gen заполнен на 95%.

Heap dump (снят в 3:15, во время off-peak): Eclipse MAT -> Leak Suspects -> "Problem Suspect 1: 2,400,000 instances of com.example.ProductDTO occupy 5.2 GB (65% of heap)". Path to GC Roots: `ProductDTO` -> `HashMap.Node` -> `HashMap` -> `ProductCacheService.cache` (static field).

Причина: cache в `ProductCacheService` --- обычный `HashMap` без size limit и TTL. Каждый просмотренный товар кэшировался навсегда. За 3 месяца работы cache вырос до 2.4 млн записей. Fix: замена на Caffeine cache с `maximumSize(10_000)` и `expireAfterWrite(30, MINUTES)`.

### История 2: "Deadlock на connection pool в пятницу вечером"

Microservice на Spring Boot, HikariCP connection pool (10 connections). Пятница, 18:00, нагрузка в 2 раза выше обычной. Алерт: все запросы timeout (30 секунд). CPU 5% --- сервис не делает ничего.

Thread dump: 100 потоков в WAITING состоянии на `HikariPool.getConnection()`. Ни один поток не отпускает connection. Ещё 10 потоков: RUNNABLE, stack trace показывает вызов другого микросервиса через HTTP внутри транзакции. Этот микросервис тоже медленный (отвечает за 25 секунд вместо 100 мс). Все 10 connections заняты потоками, которые ждут ответа от медленного микросервиса, а 100 новых потоков ждут свободный connection.

Это не классический deadlock (JVM его не обнаружит), а pool exhaustion. Fix: (1) timeout на HTTP-вызов 5 секунд, (2) увеличение pool до 20, (3) circuit breaker на вызов к медленному сервису.

### История 3: "GC pause 15 секунд после деплоя"

Java 8, CMS GC, heap 16 GB. После деплоя новой версии GC паузы выросли с 200 мс до 15 секунд. Rollback на предыдущую версию --- паузы вернулись к 200 мс.

JFR recording за 5 минут после деплоя: GC events показывают, что Full GC триггерится каждые 2 минуты, причина --- "CMS concurrent mode failure". Это значит: CMS не успевает собрать мусор concurrent-но, и fallback'ится на Serial Full GC (Stop-The-World на 15 секунд).

Allocation profiling в async-profiler: новая версия добавила JSON logging (Jackson ObjectMapper создавался при каждом log-вызове вместо переиспользования). Allocation rate вырос с 500 MB/s до 3 GB/s. CMS не справлялся с таким потоком мусора.

Fix: переиспользование ObjectMapper (static final field) + переход на G1 GC (лучше справляется с высоким allocation rate). Результат: allocation rate упал до 600 MB/s, GC паузы --- 50 мс.

---

## Распространённые заблуждения

**"Heap dump = неизбежный downtime."** Heap dump вызывает Full GC паузу, но это не downtime в смысле "сервис недоступен". Пауза занимает от нескольких секунд (4 GB heap) до минуты (32 GB heap). За load balancer'ом другие инстансы продолжают обрабатывать запросы. Планируйте dump на off-peak или снимайте с инстанса, выведенного из балансировки.

**"JFR слишком дорогой для production."** JFR имеет overhead менее 2% в default-профиле. Netflix использует JFR на всех production-серверах. Overhead 2% --- это ничто по сравнению с ценностью данных при инциденте. Без JFR вы потеряете часы на воспроизведение проблемы. С JFR --- данные уже собраны.

**"Thread dump показывает deadlock."** Thread dump показывает текущее состояние потоков. Deadlock, который существует прямо сейчас, будет обнаружен. Но intermittent deadlock (возникающий и исчезающий) может не попасть в snapshot. Для intermittent-проблем нужны множественные dump'ы или continuous monitoring через JFR.

**"GC логи достаточно для диагностики memory-проблем."** GC логи показывают симптомы: частые Full GC, рост heap usage, длинные паузы. Но они не показывают причину: какие объекты занимают память и кто их держит. Для этого нужен heap dump. GC логи отвечают на "что происходит?", heap dump --- на "почему?".

**"Профилирование замедляет приложение."** Sampling-профайлеры (async-profiler, JFR) имеют overhead менее 1--2%. Не путайте с instrumenting-профайлерами (которые оборачивают каждый вызов метода), чей overhead может быть 10--100x. Sampling --- это статистический подход: вместо измерения каждого вызова мы делаем "фотографию" с заданной частотой и получаем статистически точную картину.

---

## Production Checklist

Настроить ЗАРАНЕЕ, до проблем:

```bash
java \
  -XX:+HeapDumpOnOutOfMemoryError \        # Heap dump при OOM
  -XX:HeapDumpPath=/var/log/java/ \        # Куда сохранить dump
  -Xlog:gc*:file=/var/log/java/gc.log:time,level,tags \  # GC логи
  -XX:StartFlightRecording=disk=true,maxsize=500m,maxage=1d \  # JFR
  -jar myapp.jar
```

Этот набор флагов должен быть в каждом production-деплое. Overhead: менее 2%. Ценность при инциденте: бесценна. Без `-XX:+HeapDumpOnOutOfMemoryError` вы потеряете возможность диагностировать OOM. Без JFR continuous recording вы потеряете данные до инцидента. Без GC-логов вы не увидите паттерн GC-поведения.

---

## Troubleshooting по симптомам

### High CPU

```
1. jstack <pid> > dump1.txt        # Первый snapshot
2. sleep 10                         # Интервал
3. jstack <pid> > dump2.txt        # Второй snapshot
4. Сравнить: какие threads RUNNABLE в обоих dumps?
5. Стабильно RUNNABLE на одном методе = hotspot
6. JFR или async-profiler для детального flame graph
```

### High Memory / OOM

```
1. Проверить GC логи: частые Full GC? Heap не освобождается?
2. Если memory растёт монотонно → leak
3. Убедиться что -XX:+HeapDumpOnOutOfMemoryError включён
4. Снять heap dump (off-peak!) или дождаться OOM
5. Eclipse MAT → Leak Suspects → Path to GC Roots
```

### Slow Response

```
1. JFR recording на 2-5 минут
2. JMC → Automated Analysis → приоритизированные проблемы
3. Method Profiling → flame graph → где CPU?
4. Lock Instances → contention?
5. I/O tab → медленные внешние вызовы?
```

---

## Quick Reference: команды

| Задача | Команда |
|--------|---------|
| Thread dump | `jstack <pid> > dump.txt` |
| Heap dump (live) | `jcmd <pid> GC.heap_dump /tmp/heap.hprof` |
| Heap dump (all) | `jcmd <pid> GC.heap_dump -all /tmp/heap.hprof` |
| Start JFR | `jcmd <pid> JFR.start name=rec duration=60s` |
| Dump JFR | `jcmd <pid> JFR.dump name=rec filename=rec.jfr` |
| Stop JFR | `jcmd <pid> JFR.stop name=rec` |
| async-profiler CPU | `./profiler.sh -d 30 -f out.html <pid>` |
| async-profiler alloc | `./profiler.sh -d 30 -e alloc -f out.html <pid>` |
| GC trigger | `jcmd <pid> GC.run` |
| VM info | `jcmd <pid> VM.info` |
| List running JVMs | `jps -l` |

---

## Связь с другими темами

**[[jvm-profiling]]** --- профилирование и production debugging дополняют друг друга как два этапа диагностики. Thread dump и heap dump показывают текущее состояние (snapshot), а async-profiler и flame graphs выявляют паттерны потребления ресурсов за период времени (trend). Понимание профилирования позволяет перейти от реактивной диагностики ("что сломалось сейчас") к проактивной ("где потенциальный bottleneck"). Рекомендуется сначала освоить production debugging для экстренных ситуаций, затем --- profiling для систематической оптимизации.

**[[jvm-gc-tuning]]** --- значительная часть production-инцидентов связана с GC: высокие паузы, Full GC storms, OOM. Production debugging даёт инструменты диагностики (GC логи, heap dump, JFR GC events), а GC tuning --- инструменты решения (выбор сборщика, настройка параметров). Без понимания GC невозможно интерпретировать heap dump и GC логи. Изучайте GC tuning после освоения базовых инструментов диагностики.

**[[jvm-performance-overview]]** --- production debugging решает конкретные инциденты, а performance overview даёт общую карту оптимизации JVM-приложений. Знание полной картины помогает выбрать правильный инструмент: thread dump для CPU-проблем, heap dump для memory, JFR для комплексного анализа, async-profiler для точного CPU-profiling. Начните с overview для понимания контекста, затем углубляйтесь в debugging для практических навыков.

**[[jvm-memory-model]]** --- понимание структуры памяти JVM (heap, stack, metaspace) критично для интерпретации heap dump и диагностики memory-проблем. Без знания Young/Old Generation невозможно понять, почему объекты не собираются GC. Без понимания TLAB невозможно интерпретировать JFR allocation events. Memory model объясняет "как устроено", production debugging --- "как починить, когда сломалось". Рекомендуется изучить memory model до погружения в heap dump анализ.

---

## Что читать дальше

1. [[jvm-gc-tuning]] --- настройка GC после диагностики проблемы
2. [[jvm-profiling]] --- систематическое профилирование для проактивной оптимизации
3. [[jvm-memory-model]] --- фундамент для понимания heap dump'ов
4. [[jvm-performance-overview]] --- общая картина performance engineering

---

## Источники и дальнейшее чтение

- Oaks S. (2020). *Java Performance: In-Depth Advice for Tuning and Programming Java 8, 11, and Beyond.* --- Главы о profiling и production debugging, практические рецепты диагностики JVM-проблем с реальными примерами. Обязательное чтение для каждого, кто эксплуатирует Java-приложения.
- Evans B., Gough J., Newland C. (2018). *Optimizing Java: Practical Techniques for Improving JVM Application Performance.* --- Глубокое покрытие JVM internals, GC diagnostics и production troubleshooting с акцентом на инструменты. Особенно ценны главы об async-profiler и JFR.
- Haththotuwa I. (2021). *Troubleshooting Java: Read, Debug, and Optimize JVM Applications.* --- Практическое руководство по диагностике Java-проблем в production: от thread dump анализа до heap dump interpretation, с пошаговыми сценариями реальных инцидентов.
- Goetz B. (2006). *Java Concurrency in Practice.* --- Необходим для понимания thread dump анализа: deadlocks, race conditions, lock contention объясняются с теоретической основой, без которой невозможно интерпретировать thread dump'ы.

---

*Проверено: 2026-02-11 --- Педагогический контент проверен*
