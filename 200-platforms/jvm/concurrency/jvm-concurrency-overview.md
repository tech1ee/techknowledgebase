---
title: "JVM Concurrency: карта многопоточности"
created: 2025-11-25
modified: 2026-02-11
tags:
  - topic/jvm
  - concurrency
  - threads
  - type/moc
  - level/beginner
type: moc
status: published
area: programming
confidence: high
related:
  - "[[jvm-synchronization]]"
  - "[[jvm-concurrent-collections]]"
  - "[[jvm-executors-futures]]"
  - "[[java-modern-features]]"
reading_time: 12
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# JVM Concurrency: карта многопоточности

> **TL;DR:** Concurrency в JVM --- это не просто потоки. Это стек абстракций: от hardware memory barriers и CAS-инструкций через `synchronized`/`volatile`/`Atomic*` к `ExecutorService` и `CompletableFuture`, и наконец к Virtual Threads (Java 21), которые позволяют создавать миллионы легковесных потоков. Java Memory Model (JMM) --- формальный контракт, определяющий, когда изменения одного потока становятся видны другому. Без понимания JMM любая многопоточная программа --- набор случайных совпадений.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Как работает JVM | Понимать потоки в контексте JVM | [[jvm-basics-history]] |
| OS потоки | Thread vs Process, scheduling | [[os-processes-threads]] |
| OS синхронизация | Mutex, semaphore на уровне ОС | [[os-synchronization]] |

---

## Зачем это знать

Многопоточные баги --- самые дорогие в production. Race condition проявляется один раз на тысячу запусков, только под нагрузкой, только на определённом сервере. Deadlock замораживает сервис в 3 часа ночи. Visibility bug приводит к тому, что один поток читает стейл-данные, а вы неделю ищете «случайный» баг в бизнес-логике.

По данным исследования Shan Lu et al. (2008, "Learning from Mistakes"), 97% реальных concurrency-багов в open-source проектах относятся к четырём категориям: atomicity violation (порядок операций), order violation (последовательность), deadlock и пропущенная синхронизация. Все четыре категории разбираются в этом разделе и его дочерних материалах.

Понимание concurrency на уровне JVM даёт инженеру способность: (1) выбирать правильный примитив синхронизации для конкретной задачи, (2) читать и понимать concurrent-код фреймворков, (3) диагностировать проблемы через thread dump и profiler, (4) проектировать системы, которые масштабируются под нагрузкой.

---

## Аналогия: кухня ресторана

Прежде чем погружаться в детали, представьте кухню загруженного ресторана. Эта аналогия будет сопровождать нас на протяжении всего раздела.

**Повара --- это потоки.** Каждый повар работает независимо, выполняя свои задачи. У ресторана ограниченное количество поваров (как ограничено число CPU-ядер). Нанять 100 поваров на кухню с 4 плитами --- бессмысленно: они будут толкаться и мешать друг другу (thread contention).

**Заказы --- это задачи (tasks).** Заказы приходят от клиентов и складываются в очередь (task queue). Не каждый повар хватает заказ из зала напрямую --- есть менеджер зала, который распределяет работу (ExecutorService). Это эффективнее, чем нанимать нового повара на каждый заказ.

**Рецепты --- это shared state.** Книга рецептов одна на всю кухню. Если два повара одновременно пытаются исправить рецепт (один добавляет соль, другой убирает) --- получается хаос (race condition). Решение: либо повар берёт книгу в руки и никто другой не может её изменить (synchronized), либо каждый повар работает со своей копией (thread-local), либо изменения делаются атомарно на отдельных карточках (Atomic operations).

**Холодильник --- это общая память.** У каждого повара есть маленький столик с ингредиентами (CPU cache). Если повар A положил в холодильник свежее молоко, повар B может не знать об этом --- он смотрит на свой столик, где молоко старое (visibility problem). `volatile` --- это крик на кухне: «Я обновил молоко в холодильнике, проверяйте!» Все слышат и обновляют свои столики.

> **Ключевая идея:** Concurrency --- это координация поваров на общей кухне. Без правил будет хаос. С избыточными правилами --- очередь у каждого шкафа.

---

## Concurrency vs Parallelism: принципиальная разница

Одно из самых распространённых заблуждений --- отождествление concurrency и parallelism. Роб Пайк в каноническом докладе "Concurrency is not Parallelism" (2012) объяснил разницу так: concurrency --- это **структура**, parallelism --- это **выполнение**.

**Concurrency** --- способность программы управлять несколькими задачами, которые могут перекрываться во времени. Задачи не обязательно выполняются одновременно. На одноядерном процессоре concurrent-программа переключается между задачами (time-slicing), создавая иллюзию одновременности. Суть --- в **декомпозиции** проблемы на независимые части.

**Parallelism** --- физически одновременное выполнение нескольких операций. Требует нескольких ядер CPU или нескольких машин. Parallelism невозможен без hardware-поддержки, но concurrency --- свойство программы, а не железа.

```
Concurrency (структура):          Parallelism (выполнение):

  Task A ──▶──▶                     Task A ──▶──▶──▶──▶
  Task B       ──▶──▶               Task B ──▶──▶──▶──▶
  Task C            ──▶──▶          (одновременно на разных ядрах)
  (чередование на одном ядре)
```

Почему это важно для JVM? Java-программа может быть concurrent (используя потоки), но не параллельной (если запущена на одном ядре). И наоборот --- `parallelStream()` даёт parallelism, но без правильной concurrency-структуры (immutable data, правильная синхронизация) это приведёт к багам, а не к ускорению.

---

## Историческая справка: 60 лет параллельных вычислений

Concurrency --- не новая идея. Чтобы понять, почему Java concurrency устроена именно так, нужно знать ключевые вехи.

**1965 --- Dijkstra и семафоры.** Эдсгер Дейкстра формализовал проблему взаимного исключения и предложил семафоры (semaphores) как примитив синхронизации. Его работа "Cooperating Sequential Processes" заложила теоретический фундамент всей области. Проблема обедающих философов, которую он же сформулировал, до сих пор используется для объяснения deadlock.

**1974 --- Hoare и мониторы.** Тони Хоар предложил концепцию мониторов --- механизма, объединяющего mutex и condition variable в одну конструкцию. Именно мониторы Хоара стали прототипом для `synchronized` в Java: каждый объект Java имеет встроенный монитор, а `wait()`/`notify()` --- это condition variable часть монитора.

**1995 --- Java 1.0: Green Threads.** Первая версия Java использовала green threads --- потоки, которые управлялись JVM, а не операционной системой. На системах без native thread support (ранний Linux, некоторые UNIX) это было единственным вариантом. Green threads не использовали несколько ядер CPU, но давали concurrency.

**1998 --- Java 1.2: Native Threads.** JVM перешла на native threads --- реальные потоки операционной системы с отображением 1:1. Это дало настоящий parallelism на многоядерных машинах, но и все проблемы OS threads: высокая стоимость создания (~1MB стека, ~1ms на создание), ограниченное количество.

**2004 --- Java 5: java.util.concurrent (JSR-166).** Дуг Ли (Doug Lea), автор книги "Concurrent Programming in Java", разработал пакет `java.util.concurrent`. Это был перелом: `ExecutorService`, `ConcurrentHashMap`, `ReentrantLock`, `CountDownLatch`, `AtomicInteger`. Впервые Java-разработчики получили высокоуровневые, протестированные абстракции вместо голых `synchronized` и `wait()/notify()`.

**2014 --- Java 8: CompletableFuture и Streams.** `CompletableFuture` принесла асинхронную композицию в функциональном стиле. `parallelStream()` --- декларативный parallelism через Fork/Join pool. Java перешла от imperative concurrency к declarative.

**2023 --- Java 21: Virtual Threads (Project Loom).** Возвращение к идее green threads, но на новом уровне. Virtual threads --- легковесные потоки (килобайты вместо мегабайтов), которые JVM мультиплексирует на небольшое количество platform threads. Можно создать миллионы virtual threads для I/O-bound задач. Netflix перешла на virtual threads и снизила потребление потоков с 5000 до ~200 carrier threads при том же throughput.

> **Ключевая идея:** Каждые ~10 лет Java concurrency делает качественный скачок. Green threads -> Native threads -> java.util.concurrent -> CompletableFuture -> Virtual Threads.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Поток (Thread)** | Независимая последовательность выполнения кода | Повар на кухне |
| **Блокировка (Lock)** | Механизм ограничения доступа к ресурсу | Ключ от кладовки --- только у одного |
| **Deadlock** | Потоки ждут друг друга бесконечно | Два водителя не уступают на узком мосту |
| **Race Condition** | Результат зависит от порядка выполнения | Два кассира продают последний билет |
| **Видимость (Visibility)** | Гарантия что поток видит изменения другого | Записка на общей доске --- все видят |
| **CAS** | Compare-And-Swap --- атомарная операция CPU | "Если цена всё ещё 100, покупаю" |
| **JMM** | Java Memory Model --- модель памяти | Контракт: когда изменения видны другим |
| **Happens-Before** | Гарантия порядка операций между потоками | "Если A до B, то A точно виден из B" |
| **Virtual Thread** | Легковесный поток в Java 21+ | Курьер на велосипеде (вместо грузовика) |

---

## Обзор ключевых тем

### Threads: единица выполнения

Поток (thread) --- это самостоятельный путь выполнения внутри JVM-процесса. Все потоки одного процесса разделяют одно адресное пространство (heap), но имеют собственный стек вызовов. Это ключевое отличие от процессов, которые изолированы друг от друга.

В JVM каждый platform thread отображается на один OS thread (модель 1:1). Создание потока стоит ~1ms и ~1MB памяти под стек. Поэтому создавать тысячи platform threads --- плохая идея. Вместо этого используют пулы потоков (thread pools), где ограниченное число потоков обрабатывают очередь задач.

Жизненный цикл потока --- конечный автомат с шестью состояниями: NEW (создан), RUNNABLE (выполняется или готов), BLOCKED (ждёт монитор), WAITING (ждёт бесконечно), TIMED_WAITING (ждёт с таймаутом), TERMINATED (завершён). Переходы между состояниями --- ключ к пониманию thread dump и диагностике проблем.

```
NEW → start() → RUNNABLE ⇄ BLOCKED / WAITING / TIMED_WAITING → TERMINATED
```

### Synchronization: защита общих данных

Когда несколько поваров пользуются одной книгой рецептов, нужны правила. Synchronization --- это набор механизмов для координации доступа к shared state.

В JVM есть три уровня синхронизации. Первый --- `volatile`: гарантирует видимость (changes flush to main memory), но не атомарность составных операций. Второй --- `synchronized` и `ReentrantLock`: mutual exclusion + visibility, но блокируют потоки. Третий --- `Atomic*` и CAS: lock-free атомарные операции, без блокировок, но только для простых операций.

Выбор неправильного уровня --- либо баг (volatile для `counter++`), либо потерянная производительность (synchronized для простого флага). Подробности: [[jvm-synchronization]].

### Concurrent Collections: thread-safe структуры данных

Обычные коллекции (`HashMap`, `ArrayList`) не предназначены для concurrent access. Два потока, делающие `put()` в `HashMap` одновременно, могут повредить внутреннюю структуру --- цепочки превращаются в циклы, и `get()` зависает навсегда.

`java.util.concurrent` предоставляет коллекции, спроектированные для многопоточного доступа: `ConcurrentHashMap` (lock striping --- разные сегменты блокируются независимо), `CopyOnWriteArrayList` (копирование при записи --- идеально для read-heavy нагрузки), `BlockingQueue` (producer-consumer паттерн с блокировкой). Каждая коллекция оптимизирована под конкретный паттерн использования. Подробности: [[jvm-concurrent-collections]].

### Executors и Futures: абстракция над потоками

Создавать поток на каждую задачу --- как нанимать нового повара на каждый заказ. `ExecutorService` --- это менеджер кухни: принимает задачи, распределяет по имеющимся поварам (потокам из пула), возвращает `Future` (квитанцию о заказе).

`CompletableFuture` (Java 8+) добавила функциональную композицию: `thenApply()`, `thenCompose()`, `exceptionally()`. Вместо блокирующего `future.get()` вы строите цепочку преобразований, которая выполняется асинхронно. Это декларативный concurrency --- вы описываете **что** нужно, а не **как** управлять потоками. Подробности: [[jvm-executors-futures]].

### Virtual Threads: революция Java 21

Virtual threads --- пожалуй, самое значительное изменение в Java concurrency за 20 лет. Идея проста: если I/O-bound задача 99% времени ждёт ответ от базы данных или HTTP-сервиса, зачем держать целый OS-поток (1MB памяти) в состоянии ожидания?

Virtual thread занимает килобайты памяти. Когда он блокируется на I/O, JVM автоматически «снимает» его с carrier thread и ставит другой virtual thread. Это M:N модель: миллионы виртуальных потоков мультиплексируются на десятки platform threads. API полностью совместим --- `Thread.ofVirtual().start(() -> ...)` выглядит как обычный поток. Подробности: [[java-modern-features]].

---

## Выбор инструмента: дерево решений

```
Задача                              Инструмент
─────────────────────────────────────────────────────────────
Простой флаг (stop/ready)        → volatile boolean
Счётчик (low contention)         → AtomicInteger
Счётчик (high contention)        → LongAdder
Защита критической секции        → synchronized / ReentrantLock
Thread-safe Map                  → ConcurrentHashMap
Producer-Consumer                → BlockingQueue
Параллельные задачи              → ExecutorService
Async composition                → CompletableFuture
Миллионы I/O операций            → Virtual Threads (Java 21+)
```

> **Правило:** Используйте наименее мощный инструмент, который решает задачу. `volatile` проще `synchronized`, `synchronized` проще `ReentrantLock`. Сложность --- источник багов.

---

## Карта обучения: рекомендуемый порядок

Concurrency --- область, где порядок изучения критичен. Каждый следующий уровень опирается на предыдущий.

**Шаг 1: Java Memory Model.** Начните с понимания JMM и happens-before. Без этого невозможно понять, почему `volatile` работает и когда `synchronized` необходим. Это фундамент, на котором стоит всё остальное.

**Шаг 2: Примитивы синхронизации.** `synchronized`, `volatile`, `Atomic*`, `ReentrantLock`. Это инструменты ручного управления --- как ручная коробка передач. Чтобы понять автоматическую, нужно сначала научиться на ручной. Материал: [[jvm-synchronization]].

**Шаг 3: Concurrent collections.** `ConcurrentHashMap`, `BlockingQueue`, `CopyOnWriteArrayList`. Эти структуры --- «готовые блюда», построенные на примитивах из шага 2. Материал: [[jvm-concurrent-collections]].

**Шаг 4: Executors и CompletableFuture.** Высокоуровневые абстракции, которые вы будете использовать в 90% production-кода. Но без понимания шагов 1--3 вы не сможете диагностировать проблемы. Материал: [[jvm-executors-futures]].

**Шаг 5: Virtual Threads и современные подходы.** Java 21+ features. Знание предыдущих шагов помогает понять, что virtual threads решают и чего не решают. Материал: [[java-modern-features]].

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Threads = параллелизм" | Threads --- **concurrency** (interleaving). Parallelism требует несколько CPU cores |
| "Больше threads = быстрее" | После N_cores потоков --- **contention**, context switching overhead. Закон Амдала ограничивает выигрыш |
| "Virtual Threads заменят всё" | Virtual Threads для **I/O-bound** задач. CPU-bound по-прежнему требуют Platform Threads |
| "synchronized устарел" | synchronized **оптимизирован** в Java 6+ (biased locking, lock coarsening). Для простых случаев проще ReentrantLock |
| "Immutable = нет проблем" | Immutable объекты безопасны для sharing, но **публикация** должна быть безопасной (final fields, volatile reference) |

---

## Кто использует и реальные примеры

| Компания | Как используют concurrency | Результаты |
|----------|---------------------------|------------|
| **Netflix** | Virtual Threads (JDK 21) для I/O | Потоки: 5000 -> 200, тот же throughput |
| **Twitter/X** | Scala Futures, Finagle | Миллионы RPS |
| **Uber** | ExecutorService, CompletableFuture | Async микросервисы |
| **LinkedIn** | Kafka (concurrent consumers) | Миллиарды сообщений/день |

---

## Связь с другими темами

**[[jvm-synchronization]]** --- примитивы синхронизации (`synchronized`, `volatile`, `Atomic*`, `ReentrantLock`) --- это фундамент concurrency в JVM. Обзорный документ даёт карту; synchronization --- детальное описание конкретных механизмов. Начните с этого обзора, затем читайте synchronization для глубокого понимания каждого примитива.

**[[jvm-concurrent-collections]]** --- thread-safe коллекции (`ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`) построены на примитивах из synchronization. Понимание CAS и lock striping из synchronization объясняет, почему `ConcurrentHashMap` масштабируется лучше, чем `Collections.synchronizedMap()`. Читайте после synchronization.

**[[jvm-executors-futures]]** --- `ExecutorService` и `CompletableFuture` --- высокоуровневые абстракции, инкапсулирующие управление потоками и синхронизацию. Это инструменты, которые вы будете использовать в production-коде ежедневно. Но когда `CompletableFuture` зависает или thread pool исчерпан --- без понимания нижних уровней диагностика невозможна.

**[[java-modern-features]]** --- Virtual Threads (Java 21), Records, Pattern Matching --- современные возможности Java. Virtual Threads --- кульминация 25 лет эволюции concurrency в Java. Понимание предыдущих подходов помогает оценить, что именно virtual threads упрощают и какие ограничения остаются (например, `synchronized` внутри virtual thread по-прежнему блокирует carrier thread --- pinning).

---

## Источники и дальнейшее чтение

- Goetz B. et al. (2006). *Java Concurrency in Practice*. --- Каноническая книга по Java concurrency. Объясняет JMM, happens-before, все примитивы синхронизации с теоретическим обоснованием. Обязательное чтение для любого Java-разработчика.
- Herlihy M., Shavit N. (2012). *The Art of Multiprocessor Programming*, Revised Edition. --- Глубокая теория concurrent programming: от spin locks и CAS до lock-free структур данных и linearizability. Для тех, кто хочет понять фундамент, а не только API.
- Lea D. (2000). *Concurrent Programming in Java: Design Principles and Patterns*, 2nd Edition. --- Дуг Ли --- автор java.util.concurrent. Эта книга --- его design rationale. Объясняет, почему API спроектировано именно так.
- Pike R. (2012). *Concurrency is not Parallelism* (talk). --- Каноническое объяснение разницы между concurrency и parallelism на примерах из Go, но идеи универсальны.
- Lu S. et al. (2008). *Learning from Mistakes --- A Comprehensive Study on Real World Concurrency Bug Characteristics*. --- Анализ реальных concurrency-багов в open-source проектах. Показывает, что 97% багов относятся к четырём категориям.

---

*Проверено: 2026-02-11 | Источники: JCIP, Herlihy & Shavit, Lea, Pike --- Педагогический контент проверен*

---

## Проверь себя

> [!question]- Почему Virtual Threads не заменяют platform threads для CPU-bound задач?
> Virtual threads оптимизированы для I/O-bound нагрузки: когда поток блокируется на I/O, JVM снимает его с carrier thread и ставит другой. Но если задача CPU-bound, virtual thread непрерывно занимает carrier thread и не «уступает» его. В итоге миллион CPU-bound virtual threads будет выполняться на тех же N carrier threads, что и N platform threads, --- без выигрыша. Для CPU-bound задач ограничивающий фактор --- число ядер (закон Амдала), а не модель потоков.

> [!question]- В приложении ConcurrentHashMap используется для кэша, но при высокой нагрузке наблюдаются дубликаты записей. Какой класс ошибок это и как его исправить?
> Это atomicity violation --- классический check-then-act race condition. Вероятно, код сначала проверяет `containsKey()`, а затем вызывает `put()` --- между этими двумя вызовами другой поток может вставить значение. Хотя каждая операция ConcurrentHashMap по отдельности thread-safe, составная операция «проверить + записать» --- нет. Решение: использовать атомарные составные методы, такие как `putIfAbsent()` или `computeIfAbsent()`, которые выполняют проверку и запись как одну атомарную операцию.

> [!question]- Как модель потоков JVM (1:1, M:N) связана с концепцией процессов и потоков на уровне ОС? Что произойдёт с JVM-потоками, если ОС решит вытеснить процесс JVM?
> Platform threads в JVM (модель 1:1) --- это обёртки над OS threads. Планировщик ОС управляет ими так же, как и любыми другими потоками: при вытеснении процесса JVM все его OS threads теряют CPU time. Virtual threads (модель M:N) добавляют ещё один уровень: JVM сама планирует virtual threads на carrier threads. Если ОС вытесняет carrier thread, все virtual threads, ожидающие этот carrier, тоже останавливаются. Это объясняет, почему даже с virtual threads важно понимать OS scheduling --- JVM не существует в вакууме, а работает поверх ОС.

> [!question]- Разработчик пометил поле `counter` как `volatile` и использует `counter++` из нескольких потоков. Почему значение счётчика в итоге будет неправильным, если volatile гарантирует видимость?
> `volatile` гарантирует только видимость --- каждый поток увидит последнее записанное значение. Но `counter++` --- это не одна операция, а три: чтение текущего значения, инкремент, запись обратно. Между чтением и записью другой поток может прочитать то же значение и записать тот же результат --- происходит потерянное обновление (lost update). Для атомарного инкремента нужен `AtomicInteger.incrementAndGet()` (CAS-операция) или `synchronized`-блок, которые гарантируют и видимость, и атомарность.

> [!question]- Kotlin-корутины и Java Virtual Threads решают похожую проблему. В чём принципиальная разница в подходе к прерыванию блокирующего кода?
> Kotlin-корутины --- это кооперативная многозадачность на уровне компилятора: корутина уступает управление в точках приостановки (`suspend`-функциях). Если корутина вызывает блокирующий код (например, `Thread.sleep()`), она блокирует весь поток диспетчера. Virtual Threads работают на уровне JVM: при вызове блокирующей I/O-операции JVM автоматически «отсоединяет» virtual thread от carrier thread без явных точек приостановки в коде. Однако virtual threads тоже не всесильны --- `synchronized`-блок внутри virtual thread вызывает pinning (привязку к carrier thread). Оба подхода дополняют друг друга: корутины дают структурированный concurrency, а virtual threads --- масштабируемость на уровне JVM.

---

## Ключевые карточки

Что такое happens-before в Java Memory Model?
?
Формальное отношение порядка между операциями в разных потоках. Если операция A happens-before операции B, то результаты A гарантированно видны в B. Примеры: запись volatile перед чтением того же поля, выход из synchronized перед входом в тот же монитор, `Thread.start()` перед первой операцией нового потока.

Чем отличается concurrency от parallelism?
?
Concurrency --- это структура программы: способность управлять несколькими задачами, которые могут перекрываться во времени (возможно на одном ядре через time-slicing). Parallelism --- физически одновременное выполнение на нескольких ядрах. Concurrency --- свойство кода, parallelism --- свойство исполнения.

Почему volatile недостаточно для операции counter++?
?
`counter++` --- составная операция (чтение + инкремент + запись). `volatile` гарантирует только видимость каждой отдельной операции, но не атомарность составной. Между чтением и записью другой поток может выполнить свою операцию, вызывая lost update. Нужен `AtomicInteger` или `synchronized`.

Какие четыре категории покрывают 97% concurrency-багов (по исследованию Shan Lu et al.)?
?
Atomicity violation (нарушение атомарности составных операций), order violation (нарушение ожидаемого порядка), deadlock (взаимная блокировка) и пропущенная синхронизация (отсутствие защиты shared state).

В чём разница между моделью потоков 1:1 и M:N в JVM?
?
1:1 --- каждый Java platform thread отображается на один OS thread (~1MB стека, ~1ms на создание). M:N --- множество virtual threads мультиплексируются JVM на несколько carrier (platform) threads. M:N позволяет создавать миллионы потоков для I/O-bound задач, поскольку при блокировке virtual thread «освобождает» carrier thread.

Что такое pinning в контексте Virtual Threads?
?
Pinning --- привязка virtual thread к carrier thread, при которой carrier thread блокируется и не может выполнять другие virtual threads. Происходит, когда virtual thread входит в `synchronized`-блок или вызывает native-метод. Для избежания pinning рекомендуется заменять `synchronized` на `ReentrantLock`.

Почему ConcurrentHashMap масштабируется лучше, чем Collections.synchronizedMap()?
?
`synchronizedMap()` блокирует всю map одним мьютексом --- при N потоках все они стоят в очереди. `ConcurrentHashMap` использует lock striping: разные сегменты (бакеты) блокируются независимо, позволяя нескольким потокам одновременно работать с разными частями map. В Java 8+ вместо сегментных блокировок используется CAS на уровне отдельных нод.

Почему порядок изучения concurrency критичен (JMM -> примитивы -> коллекции -> executors)?
?
Каждый уровень абстракции построен на предыдущем. Без понимания JMM невозможно объяснить, почему `volatile` работает. Без знания примитивов нельзя понять, как устроен `ConcurrentHashMap`. Без понимания коллекций и потоков невозможно диагностировать проблемы в `ExecutorService` или `CompletableFuture`.

Когда следует предпочесть LongAdder вместо AtomicLong?
?
При высоком contention (много потоков часто обновляют один счётчик). `AtomicLong` использует один CAS, и при конкуренции потоки постоянно повторяют операцию (spinning). `LongAdder` распределяет значение по нескольким ячейкам (striped), снижая contention. Итоговое значение получается суммированием всех ячеек через `sum()`.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[jvm-synchronization]] | Детальный разбор synchronized, volatile, Atomic*, ReentrantLock --- фундамент всей JVM concurrency |
| Углубление | [[jvm-concurrent-collections]] | Thread-safe коллекции: ConcurrentHashMap, BlockingQueue, CopyOnWriteArrayList --- практические инструменты |
| Продвинутый уровень | [[jvm-executors-futures]] | ExecutorService, CompletableFuture, Fork/Join --- абстракции, которые используются в production-коде ежедневно |
| Современные возможности | [[java-modern-features]] | Virtual Threads (Java 21), Records, Structured Concurrency --- будущее JVM concurrency |
| Kotlin-перспектива | [[kotlin-coroutines]] | Корутины и structured concurrency в Kotlin --- альтернативный подход к асинхронности поверх JVM |
| Кросс-доменная связь | [[concurrency-vs-parallelism]] | Теоретическая база concurrency/parallelism вне контекста JVM --- для переноса знаний на другие платформы |
| Диагностика | [[jvm-profiling]] | Профилирование потоков, thread dump анализ, обнаружение deadlock и contention --- навыки отладки в production |
