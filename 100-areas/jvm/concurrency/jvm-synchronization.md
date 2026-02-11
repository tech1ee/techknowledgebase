---
title: "JVM Synchronization: synchronized, volatile, atomic"
created: 2025-11-25
modified: 2026-02-11
tags:
  - topic/jvm
  - concurrency
  - synchronized
  - volatile
  - atomic
  - type/deep-dive
  - level/intermediate
type: deep-dive
status: published
area: programming
confidence: high
prerequisites:
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-memory-model]]"
related:
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-concurrent-collections]]"
  - "[[jvm-executors-futures]]"
---

# JVM Synchronization: синхронизация потоков

> **TL;DR:** `synchronized` = mutual exclusion + visibility (блокирует поток). `volatile` = visibility без блокировки (флаги, one-writer). `Atomic*` = lock-free через CAS (счётчики). `LongAdder` = 100x быстрее AtomicLong при high contention. `ReentrantLock` = tryLock с таймаутом для предотвращения deadlock. Каждый примитив решает свою задачу --- выбор неправильного ведёт либо к багам, либо к потерянной производительности.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| JVM многопоточность | Общая картина concurrency | [[jvm-concurrency-overview]] |
| CPU cache и память | Почему нужна синхронизация | [[os-memory-management]] |
| OS синхронизация | Mutex, semaphore базовые концепции | [[os-synchronization]] |

---

## Зачем это знать

Синхронизация --- это ответ на фундаментальный вопрос concurrent programming: как обеспечить корректность программы, когда несколько потоков одновременно работают с общими данными? Без синхронизации результат любой многопоточной программы непредсказуем.

Проблема не абстрактная. `counter++` --- три операции (read, increment, write). Без синхронизации два потока могут прочитать одно и то же значение, каждый увеличит его на единицу, и запишут одно и то же --- вместо двух инкрементов получится один. Это atomicity violation. Или: один поток установил `flag = true`, а другой не видит этого бесконечно долго, потому что значение застряло в CPU cache --- это visibility problem.

Ещё опаснее --- эти баги проявляются недетерминированно. Программа может работать корректно тысячи раз, а на тысячу первый --- при определённой нагрузке, на определённом CPU, при определённом scheduling --- сломаться. Именно поэтому понимание примитивов синхронизации --- не опциональное знание, а фундамент для любого Java-разработчика, пишущего код, который будет работать под нагрузкой.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Монитор (Monitor)** | Встроенная блокировка в каждом Java-объекте | Замок на двери кабинета |
| **Барьер памяти** | Инструкция CPU, гарантирующая порядок операций | Финишная черта: всё до неё завершено |
| **CAS** | Compare-And-Swap --- атомарная проверка и замена | "Если цена ещё 100, покупаю" |
| **Reentrant** | Поток может захватить свою же блокировку повторно | Ключ от дома --- можно зайти снова |
| **Contention** | Конкуренция потоков за один ресурс | Очередь за одним кассиром |
| **Striped** | Разделение на независимые сегменты | Много касс вместо одной |
| **ABA Problem** | Значение изменилось A->B->A, но CAS не заметил | Подмена одинаково выглядящих товаров |
| **Fair Lock** | FIFO порядок для ожидающих потоков | Честная очередь --- кто первый пришёл |

---

## Историческая справка: от Dijkstra до Virtual Threads

Примитивы синхронизации в Java --- не изобретение Sun Microsystems. Они опираются на 60 лет теоретических и инженерных работ. Знание этой истории объясняет, **почему** API спроектировано именно так.

**1965 --- Dijkstra и семафоры.** Эдсгер Дейкстра в работе "Cooperating Sequential Processes" формализовал проблему взаимного исключения (mutual exclusion) и предложил семафоры --- переменные со специальными операциями P (wait/acquire) и V (signal/release). Семафор --- это обобщённый mutex: counting semaphore позволяет N потокам одновременно иметь доступ к ресурсу. В Java семафор доступен как `java.util.concurrent.Semaphore` (с Java 5), но его концепция повлияла на дизайн всех последующих примитивов.

**1974 --- Hoare и мониторы.** Тони Хоар в статье "Monitors: An Operating System Structuring Concept" предложил мониторы --- конструкцию, объединяющую mutual exclusion и condition variable (механизм ожидания определённого условия). Ключевая идея Хоара: mutex и condition variable всегда нужны вместе --- нет смысла разделять их на уровне примитива. Именно эта идея стала основой `synchronized` в Java: каждый Java-объект имеет монитор (mutex-часть --- `synchronized`, condition-часть --- `wait()`/`notify()`). Когда вы пишете `synchronized (obj)`, вы используете дизайн, придуманный Хоаром 50 лет назад.

**2000--2004 --- Doug Lea и java.util.concurrent.** Дуг Ли, профессор SUNY Oswego, написал книгу "Concurrent Programming in Java" (1996, 2nd ed. 2000) и реализовал библиотеку `dl.util.concurrent`. На основе его работы был создан JSR-166, ставший пакетом `java.util.concurrent` в Java 5 (2004). Ли предложил `ReentrantLock` --- явный lock с API для tryLock, fairness и interruptible waiting. Это решило главную проблему `synchronized`: невозможность отменить ожидание блокировки или задать timeout.

**2004+ --- Cliff Click и lock-free CAS.** Клифф Клик (Cliff Click), инженер Azul Systems и один из авторов HotSpot JVM, популяризировал lock-free алгоритмы на основе Compare-And-Swap (CAS) в Java-мире. CAS --- hardware-инструкция (CMPXCHG на x86), которая атомарно проверяет и меняет значение. `AtomicInteger`, `AtomicReference`, `ConcurrentHashMap` --- все используют CAS как фундамент. Lock-free подход гарантирует, что хотя бы один поток всегда делает прогресс, даже если другие потоки preempted.

**2010+ --- Оптимизации JVM.** Начиная с Java 6, HotSpot JVM получила серию оптимизаций для `synchronized`: biased locking (блокировка привязывается к потоку, повторный захват --- без CAS), lightweight locking (CAS вместо OS mutex для uncontended случая), lock coarsening (JIT объединяет соседние synchronized блоки), lock elision (JIT убирает synchronized, если escape analysis показывает, что объект не покидает поток). Эти оптимизации сделали `synchronized` конкурентоспособным с `ReentrantLock` для простых случаев.

> **Ключевая идея:** Каждый примитив синхронизации в Java --- ответ на конкретную историческую проблему. `synchronized` --- мониторы Хоара. `ReentrantLock` --- ответ на ограничения synchronized. `Atomic*` --- hardware CAS для lock-free прогресса.

---

## synchronized: блокировка монитора

`synchronized` --- самый старый и самый простой механизм синхронизации в Java, существующий с версии 1.0. Он решает две задачи одновременно: **mutual exclusion** (только один поток выполняет код) и **visibility** (изменения видны другим потокам).

Почему эти две задачи неразделимы? Mutual exclusion без visibility бесполезен. Представьте: поток A изменил переменную внутри synchronized блока, но поток B видит старое значение --- программа сломана. Java Memory Model гарантирует, что при выходе из synchronized все изменения сбрасываются в main memory (как monitor unlock в модели Хоара), а при входе --- читаются из main memory (monitor lock). Это и есть happens-before гарантия для `synchronized`.

Аналогия из жизни: `synchronized` --- это дверь с замком в переговорную комнату. Только один человек может быть внутри. Он заходит, закрывает дверь (acquire monitor), делает работу, открывает дверь (release monitor). Все ожидающие видят результат его работы (whiteboard в комнате обновлён). Если кто-то не закрыл дверь --- два человека могут одновременно стирать и писать на доске, и результат будет нечитаемым.

### Базовое использование

Ниже --- два способа применения `synchronized`. Первый --- на уровне метода (грубая гранулярность: весь метод под блокировкой). Второй --- на уровне блока (тонкая гранулярность: только критическая секция).

```java
public class Counter {
    private int count = 0;

    // Весь метод под lock (monitor = this)
    public synchronized void increment() {
        count++;  // read-modify-write теперь атомарен
    }

    // Блок — более гранулярный контроль
    public void add(int n) {
        synchronized (this) {  // Явно указываем объект-монитор
            count += n;
        }
    }
}
```

Оба варианта функционально эквивалентны для instance-методов: `synchronized` на методе использует `this` как монитор. Но блочная форма позволяет синхронизироваться на другом объекте и защитить только минимально необходимый участок кода --- это уменьшает время, когда блокировка удерживается (hold time), и повышает throughput.

### Монитор объекта: что происходит внутри

Каждый объект в Java имеет скрытую структуру --- **монитор**. Это не что-то абстрактное; это реальные байты в header объекта (mark word), которые хранят информацию о блокировке. Mark word занимает 8 байт (на 64-bit JVM) и содержит: hash code, GC age, lock state и pointer на owner thread.

Когда поток входит в synchronized, JVM выполняет следующую последовательность:
1. Проверяет mark word объекта --- свободен ли монитор
2. Если монитор свободен --- устанавливает ownership (CAS операция)
3. Если монитор занят текущим потоком --- увеличивает счётчик reentrant (потому что мониторы reentrant)
4. Если монитор занят другим потоком --- текущий поток переходит в состояние BLOCKED и ставится в очередь ожидания монитора

```
Поток 1: synchronized(obj) { count++ }  → захватил монитор
Поток 2: synchronized(obj) {            → BLOCKED (ждёт освобождения)
          count++
          }                              → получил lock после Потока 1
```

**Критически важно:** блокировка привязана к **объекту**, не к коду. `synchronized(objA)` и `synchronized(objB)` --- разные блокировки. Потоки, синхронизирующиеся на разных объектах, выполняются параллельно. Это позволяет повышать granularity: вместо одного глобального lock можно использовать отдельные lock на каждый ресурс.

### Static synchronized

Для статических методов монитором служит объект `Class`:

```java
// Lock на объект Class (один на весь ClassLoader)
public static synchronized void staticMethod() {
    // SharedResource.class как monitor
}

// Эквивалент
public static void staticMethod() {
    synchronized (SharedResource.class) { }
}
```

Важный нюанс: static synchronized и instance synchronized --- **разные** мониторы. Поток в static synchronized методе не блокирует поток в instance synchronized методе того же класса. Это частый источник багов: разработчик думает, что оба метода защищены одной блокировкой.

### Reentrant (повторный вход)

Монитор в Java --- reentrant. Это значит, что поток может захватить монитор, который он уже держит. JVM ведёт счётчик захватов --- каждый `synchronized` увеличивает его, каждый выход уменьшает. Монитор освобождается только когда счётчик достигает нуля.

```java
public synchronized void outer() {
    inner();  // OK — счётчик входов 1 → 2
}

public synchronized void inner() {
    // Тот же поток уже держит lock, счётчик = 2
}  // счётчик 2 → 1

// } из outer() — счётчик 1 → 0, монитор освобождён
```

Почему reentrant критичен? Без reentrant поток заблокировался бы сам на себе при вызове `inner()` из `outer()` --- мгновенный deadlock. Reentrant делает возможной рекурсию и композицию synchronized-методов: вы можете вызывать один synchronized-метод из другого на том же объекте без страха.

Мы разобрали `synchronized` --- механизм, дающий и mutual exclusion, и visibility, но блокирующий потоки. А что если нужна только visibility, без блокировки?

---

## volatile: видимость без блокировки

`volatile` решает проблему, о которой многие не подозревают: переменная, записанная одним потоком, может быть **невидима** для другого потока бесконечно долго. Не «с задержкой», а именно бесконечно --- JMM это явно разрешает.

### Проблема visibility: почему потоки не видят изменения друг друга

Каждое ядро CPU имеет свой кэш (L1, L2). Когда поток записывает значение в переменную, оно попадает в кэш ядра, но не обязательно в основную память (main memory). Другой поток на другом ядре читает из **своего** кэша --- и видит старое значение.

Но кэш --- это только часть проблемы. Компилятор (javac и JIT) и процессор имеют право **переупорядочивать** инструкции для оптимизации. Если JIT определит, что переменная `flag` не меняется в текущем потоке, он может вынести её чтение за пределы цикла --- и поток **никогда** не увидит изменение.

Аналогия: представьте двух бухгалтеров в разных офисах. Каждый ведёт копию баланса на своём столе (CPU cache). Бухгалтер A записал новую сумму в свою копию, но не отправил обновление в центральную базу. Бухгалтер B продолжает работать со старой суммой --- расхождения растут. `volatile` --- это правило «каждое изменение немедленно отправляется в центральную базу и каждое чтение идёт из центральной базы».

### Гарантии volatile

1. **Видимость** --- запись в volatile переменную сбрасывает кэши, чтение --- обновляет из main memory
2. **Запрет reordering** --- компилятор и CPU не могут переупорядочить операции через volatile
3. **НЕ атомарность** --- `volatile int++` всё ещё три операции: read, increment, write

Следующий пример показывает, как volatile обеспечивает happens-before: запись в `ready` гарантирует, что `data = 42` будет видна потоку-читателю.

```java
private volatile boolean ready = false;
private int data = 0;

// Writer
data = 42;
ready = true;  // volatile write — барьер памяти

// Reader
if (ready) {           // volatile read — барьер памяти
    print(data);       // Гарантированно 42, не 0
}
```

Без volatile компилятор мог бы переставить `data = 42` и `ready = true` местами (reordering). Или reader мог бы увидеть `ready = true`, но `data` ещё не видеть как 42 --- потому что запись `data` застряла в store buffer. Volatile запрещает оба сценария.

### Memory Barriers: механизм под капотом

Барьеры памяти (memory barriers, fences) --- инструкции CPU, запрещающие переупорядочивание операций. Volatile read и volatile write вставляют барьеры в определённых точках:

```
volatile write:
    data = 42         ← обычная запись
    [StoreStore]      ← барьер: data записан до ready
    ready = true      ← volatile запись
    [StoreLoad]       ← барьер: flush в main memory

volatile read:
    r = ready         ← volatile чтение
    [LoadLoad]        ← барьер: data читается после ready
    [LoadStore]       ← барьер: записи не переместятся до чтения ready
    value = data      ← обычное чтение
```

StoreLoad --- самый дорогой барьер. На x86 он компилируется в инструкцию `mfence` или `lock add` (используемую как fence). Стоимость: 40--100 CPU-циклов вместо 1 цикла для обычной записи. Это цена cache invalidation protocol: все ядра CPU должны согласовать состояние кэша.

### Когда использовать volatile

```java
// Флаг остановки потока — классическое применение
private volatile boolean shutdown = false;

// Публикация immutable-объекта: one writer, many readers
private volatile Config currentConfig;

// ОШИБКА: счётчик (не атомарно — race condition!)
private volatile int counter;
counter++;  // read → increment → write — три операции

// Решение: AtomicInteger
private AtomicInteger counter = new AtomicInteger();
counter.incrementAndGet();  // одна атомарная CAS-операция
```

**Правило:** volatile подходит, когда (1) только один поток пишет, (2) операция записи --- одно присваивание (не read-modify-write), (3) значение не зависит от предыдущего. Если хоть одно условие нарушено --- нужен `synchronized` или `Atomic*`.

Мы разобрали volatile --- механизм visibility без блокировки. Но что если нужна атомарная операция read-modify-write **без** блокировки потоков?

---

## Atomic: Lock-Free операции

Atomic-классы решают проблему, которую не решает volatile: атомарные read-modify-write операции **без блокировки**. `volatile int++` --- это три операции (read, increment, write), между которыми другой поток может вклиниться. `AtomicInteger.incrementAndGet()` --- одна атомарная операция.

### Почему lock-free лучше блокировки (не всегда)

`synchronized` и `ReentrantLock` работают, но имеют фундаментальный недостаток: заблокированные потоки ничего не делают. Если поток A захватил lock и был preempted операционной системой (например, его time-slice закончился) --- **все** остальные потоки стоят и ждут. Время ожидания непредсказуемо: от наносекунд до миллисекунд, если OS решила дать приоритет другому процессу.

Lock-free алгоритмы гарантируют **system-wide progress**: хотя бы один поток всегда делает полезную работу. Если поток A preempted --- поток B продолжает. Нет блокировки --- нет конвоя (lock convoy), нет priority inversion.

Аналогия: обмен товарами на рынке. Представьте, что вы хотите купить яблоки по 100 рублей за килограмм. Вы подходите к прилавку и говорите: «Если цена **всё ещё** 100 рублей, беру килограмм» (compare). Продавец проверяет ценник --- если 100, продаёт (swap). Если кто-то другой уже купил по 100 и цена стала 110 --- ваша сделка отменяется, и вы решаете заново (retry). Никто не стоит в очереди --- каждый пытается сам, и успешные сделки проходят параллельно. Это и есть CAS --- Compare-And-Swap.

### Compare-And-Swap (CAS): фундаментальная операция

CAS --- аппаратная инструкция CPU (`CMPXCHG` на x86, `LL/SC` на ARM). Она атомарно выполняет: «прочитай значение по адресу; если оно равно ожидаемому --- замени на новое; иначе --- ничего не делай и верни текущее значение». Между проверкой и записью никто не может вклиниться --- это гарантирует **железо**, а не операционная система.

```
CAS(memory_address, expected_value, new_value):
    atomically {
        if (*memory_address == expected_value)
            *memory_address = new_value
            return true
        else
            return false
    }
```

### AtomicInteger: CAS в действии

```java
AtomicInteger counter = new AtomicInteger(0);

counter.incrementAndGet();     // ++counter (атомарно)
counter.getAndIncrement();     // counter++ (атомарно)
counter.addAndGet(5);          // counter += 5 (атомарно)
counter.compareAndSet(10, 20); // if (counter == 10) counter = 20
```

Как это работает внутри? Метод `incrementAndGet()` --- это retry loop с CAS. Поток читает текущее значение, вычисляет новое, пытается записать через CAS. Если другой поток успел изменить значение между чтением и записью --- CAS возвращает false, и мы пробуем снова.

```java
public int incrementAndGet() {
    for (;;) {  // retry loop — "optimistic locking"
        int current = get();             // читаем текущее
        int next = current + 1;          // вычисляем новое
        if (compareAndSet(current, next)) // CAS: атомарно
            return next;
        // CAS failed: кто-то изменил, пробуем снова
    }
}
```

В низко-конкурентных сценариях CAS почти всегда успешен с первой попытки --- overhead минимален. В высоко-конкурентных --- может быть много retries, и CAS теряет преимущество. Именно для таких случаев создан `LongAdder`.

### AtomicReference: CAS для объектов

`AtomicReference<T>` позволяет атомарно обновлять ссылку на объект. Это основа для lock-free структур данных: lock-free stack, lock-free queue, immutable snapshot patterns.

```java
AtomicReference<User> currentUser = new AtomicReference<>();
currentUser.set(new User("Alice"));
currentUser.compareAndSet(oldUser, newUser);
```

### LongAdder: решение проблемы CAS contention

AtomicLong с CAS прекрасно работает при низкой конкуренции. Но что происходит, когда 1000 потоков одновременно инкрементируют один и тот же `AtomicLong`? Каждый поток делает CAS, но успевает только один за раз. 999 потоков получают failure и retry. И снова успевает один. CPU тратит циклы на бесполезные попытки --- это **CAS contention**.

`LongAdder` решает эту проблему архитектурно: вместо одного счётчика --- массив ячеек (cells), распределённых по cache lines. Каждый поток пишет в свою ячейку --- конфликтов почти нет. Когда нужен итоговый результат --- суммируем все ячейки.

Аналогия: представьте голосование на собрании. С `AtomicLong` --- одна урна, все толпятся. С `LongAdder` --- несколько урн в разных углах зала. Каждый бросает бюллетень в ближайшую, толкучки нет. В конце подсчитываем все урны.

```java
// AtomicLong: все потоки бьются за один адрес
AtomicLong counter = new AtomicLong();
// 1000 потоков → lock cmpxchg [counter] ← contention

// LongAdder: striped counters
LongAdder adder = new LongAdder();
// Поток 1 → cells[0].add(1)
// Поток 2 → cells[1].add(1)   ← параллельно!
long total = adder.sum();       // сумма всех cells
```

**Цена:** `sum()` не атомарен --- пока вы суммируете, кто-то может добавить в ячейку. Для точных мгновенных чтений LongAdder не подходит. Но для метрик (requests/second, bytes transferred) --- идеален.

```
Benchmark (1000 threads, 10M increments):
AtomicLong:   ~5M ops/sec   (CAS contention)
LongAdder:    ~500M ops/sec  (striped, 100x быстрее)
```

### ABA Problem: скрытая ловушка CAS

CAS проверяет только текущее значение, не историю его изменений. Это создаёт неочевидную проблему.

```
Поток 1: читает A, готовится сделать CAS(A → C)
Поток 2: меняет A → B
Поток 2: меняет B → A (вернул как было)
Поток 1: CAS(A → C) — SUCCESS, но A уже "другой"!
```

Для примитивных типов (int, long) это редко проблема: число 42 --- всегда число 42. Но для указателей (ссылок) --- катастрофа. В lock-free stack: поток 1 читает `head = A, next = B`, собирается сделать pop. Поток 2 делает pop A, pop B, push A (переиспользует память A). Поток 1 делает `CAS(head, A -> B)` --- успех, но B уже не в стеке! Структура данных повреждена.

**Решение:** `AtomicStampedReference` --- добавляет версионный stamp. CAS проверяет и значение, и версию:

```java
AtomicStampedReference<Node> ref =
    new AtomicStampedReference<>(node, 0);
// stamp увеличивается при каждом изменении
ref.compareAndSet(expected, newNode,
    expectedStamp, newStamp);
```

Мы разобрали lock-free подход через CAS. Но что если задача сложнее одной атомарной операции и нужен full mutual exclusion, но с большим контролем, чем даёт `synchronized`?

---

## ReentrantLock: явный контроль над блокировкой

`synchronized` прост, но негибок. Вы не можете: отменить ожидание блокировки, узнать свободна ли она, задать timeout, обеспечить fairness (FIFO-порядок). `ReentrantLock` --- это тот же монитор, но с полноценным API для тонкого контроля.

Аналогия: `ReentrantLock` --- это ключ от комнаты, который можно одолжить коллеге, но с правилами. Обычный `synchronized` --- вы входите, и дверь запирается автоматически. `ReentrantLock` --- вы берёте ключ (`lock()`), входите, и **обязаны** вернуть ключ (`unlock()`) сами. Если забудете --- комната заперта навсегда. Зато: можно попробовать открыть дверь без ожидания (`tryLock()`), можно подождать максимум 5 секунд (`tryLock(5, SECONDS)`), можно организовать честную очередь (`new ReentrantLock(true)` --- fair mode).

### Базовое использование

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();           // Захватить блокировку
try {
    // critical section
} finally {
    lock.unlock();     // ОБЯЗАТЕЛЬНО в finally!
}
```

**Почему `finally` обязателен?** В отличие от `synchronized`, JVM не освободит `ReentrantLock` автоматически при выходе из блока или при исключении. Забытый `unlock()` --- deadlock для всех, кто попытается захватить эту блокировку. Это главный trade-off: больше контроля = больше ответственности.

### Преимущества над synchronized

Следующий код демонстрирует четыре возможности `ReentrantLock`, недоступные для `synchronized`:

```java
// 1. tryLock — попытка без блокировки
if (lock.tryLock()) {
    try { work(); }
    finally { lock.unlock(); }
} else { fallback(); }

// 2. Timeout — ограниченное ожидание
if (lock.tryLock(1, TimeUnit.SECONDS)) { ... }

// 3. Interruptible — прерываемое ожидание
lock.lockInterruptibly();

// 4. Fair mode — FIFO-очередь ожидающих
ReentrantLock fairLock = new ReentrantLock(true);
```

`tryLock()` с timeout --- мощный инструмент для предотвращения deadlock: если не удалось захватить второй lock за разумное время --- отпустить первый и попробовать позже. Это разрывает условие "hold and wait" из четырёх условий Коффмана.

### ReadWriteLock: оптимизация для read-heavy нагрузки

Представьте библиотеку. Любое количество читателей может одновременно находиться в зале и читать книги --- они не мешают друг другу. Но когда библиотекарь вносит новые книги или переставляет полки (write operation), зал должен быть пуст: иначе читатель возьмёт книгу, которая в процессе перестановки, и получит неполную информацию.

`ReadWriteLock` реализует именно эту семантику:
- **Read lock:** много потоков могут держать одновременно
- **Write lock:** эксклюзивный --- блокирует и readers, и writers

```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();

// Много readers одновременно — не блокируют друг друга
rwLock.readLock().lock();
try { return cache.get(key); }
finally { rwLock.readLock().unlock(); }

// Writer ждёт, пока все readers закончат
rwLock.writeLock().lock();
try { cache.put(key, value); }
finally { rwLock.writeLock().unlock(); }
```

Для кэша с 99% чтений и 1% записей `ReadWriteLock` даёт многократный выигрыш по сравнению с обычным lock: 99 readers работают параллельно вместо того, чтобы стоять в очереди.

**Осторожно с writer starvation:** если readers приходят постоянно, writer может ждать бесконечно --- ведь для write lock нужно дождаться, пока **все** readers отпустят read lock. `ReentrantReadWriteLock(true)` (fair mode) решает это: writer получит приоритет после разумного ожидания. Также существует `StampedLock` (Java 8) --- оптимистичная альтернатива с ещё меньшим overhead для чтений.

---

## Deadlock: взаимная блокировка

Deadlock --- ситуация, когда два или более потоков вечно ждут друг друга. Каждый держит ресурс, который нужен другому, и ждёт ресурс, который держит другой. Это не таймаут --- это **вечное** ожидание.

### Четыре условия Coffman (1971)

Эдвард Коффман формализовал: deadlock возможен **только** если выполняются все четыре условия одновременно:

1. **Mutual exclusion** --- ресурсы нельзя разделить (блокировка эксклюзивна)
2. **Hold and wait** --- поток держит ресурсы, ожидая другие
3. **No preemption** --- ресурсы нельзя отобрать силой у потока
4. **Circular wait** --- циклическая зависимость: A ждёт B, B ждёт A

Разорвите **любое** --- и deadlock невозможен. Каждая стратегия предотвращения deadlock разрывает одно из этих условий.

### Классический пример

```java
// Поток 1: захватывает A, потом B
synchronized (lockA) {
    synchronized (lockB) { transfer(); }
}

// Поток 2: захватывает B, потом A
synchronized (lockB) {
    synchronized (lockA) { transfer(); }
}
// → Deadlock: Поток 1 держит A, ждёт B.
//             Поток 2 держит B, ждёт A.
```

### Стратегии предотвращения

**1. Lock ordering (разрывает circular wait).** Если все потоки захватывают блокировки в одном и том же порядке --- циклической зависимости не возникнет. Это самое надёжное и простое решение.

```java
// Всегда сначала lockA, потом lockB — во всей программе
synchronized (lockA) {
    synchronized (lockB) { transfer(); }
}
```

**2. tryLock с timeout (разрывает hold and wait).** Если не удалось захватить второй lock --- отпускаем первый и пробуем позже.

```java
if (lock1.tryLock(100, MILLISECONDS)) {
    try {
        if (lock2.tryLock(100, MILLISECONDS)) {
            try { work(); }
            finally { lock2.unlock(); }
        }
    } finally { lock1.unlock(); }
}
```

**3. Один lock (разрывает circular wait).** Простейшее решение --- один глобальный lock. Нет нескольких блокировок --- нет циклов. Цена --- сниженный параллелизм, но для многих приложений это приемлемо.

---

## Сравнение примитивов

| | synchronized | volatile | Atomic* | ReentrantLock |
|---|-------------|----------|---------|---------------|
| **Mutual exclusion** | да | нет | нет | да |
| **Visibility** | да | да | да | да |
| **Atomicity** | да | нет | да (простые) | да |
| **Blocking** | да | нет | нет | да |
| **tryLock** | нет | --- | --- | да |
| **Fair mode** | нет | --- | --- | да |
| **Автоматический unlock** | да | --- | --- | нет (finally!) |

---

## Когда что использовать

```
Простой флаг stop/ready        → volatile
Счётчик (low contention)       → AtomicInteger
Счётчик (high contention)      → LongAdder
Критическая секция (простая)   → synchronized
Нужен tryLock/timeout          → ReentrantLock
Много readers, мало writers    → ReadWriteLock
```

> **Правило:** используйте наименее мощный инструмент, который решает задачу. `volatile` проще `synchronized`, `synchronized` проще `ReentrantLock`. Каждый уровень сложности --- дополнительный источник багов.

---

## Распространённые заблуждения

| Миф | Реальность |
|-----|-----------|
| "volatile решает все проблемы синхронизации" | volatile обеспечивает только **visibility**, не atomicity. `count++` на volatile --- race condition |
| "synchronized медленный, избегаю его" | В Java 6+ biased locking и lock coarsening сделали synchronized быстрым. Для uncontended lock --- ~20ns |
| "Больше синхронизации = безопаснее" | Over-synchronization ведёт к **deadlock** и **performance degradation**. Lock только минимально необходимый scope |
| "ReentrantLock всегда лучше synchronized" | ReentrantLock нужен для **специфических** случаев: tryLock, timeout, fairness. Для простых --- synchronized проще и безопаснее (авто-unlock) |
| "AtomicLong быстрее всего для счётчиков" | При high contention **LongAdder в 100x быстрее**. CAS contention убивает AtomicLong |
| "Double-Checked Locking работает" | Работает **только с volatile** (Java 5+). Без volatile JMM позволяет видеть partially constructed object |
| "Синхронизация на String литерале безопасна" | String interning делает это **опасным**. Два модуля могут синхронизироваться на одном объекте. Используйте `private final Object lock` |
| "Thread-safe класс = любые операции безопасны" | Отдельные операции безопасны, но **compound actions** --- нет. `if (!map.containsKey(k)) map.put(k, v)` --- race даже с ConcurrentHashMap |
| "Deadlock можно избежать добавлением timeout" | Timeout маскирует проблему. **Правильное решение**: lock ordering или lock-free алгоритмы |

---

## Кто использует и реальные примеры

| Сценарий | Примитив | Реальные применения |
|----------|----------|---------------------|
| Флаг остановки | `volatile boolean` | Graceful shutdown в Spring, Netty |
| Метрики, счётчики | `LongAdder` | Prometheus Java client, Micrometer |
| Shared state | `synchronized` | Hibernate session, Spring transaction |
| Lock с timeout | `ReentrantLock` | Distributed lock fallback |
| Read-heavy cache | `ReadWriteLock` | Guava Cache, Caffeine |

### Известные баги синхронизации

| Баг | Причина | Решение |
|-----|---------|---------|
| **Double-Checked Locking** (до Java 5) | Visibility без volatile | `volatile` на поле |
| **HashMap corruption** | Concurrent put без sync | `ConcurrentHashMap` |
| **Iterator ConcurrentModification** | Изменение во время итерации | `CopyOnWriteArrayList` или snapshot |

---

## Подводные камни

**Синхронизация на изменяемом объекте.** `synchronized(list)` опасен, если ссылка `list` может быть переназначена. Один поток синхронизируется на старом объекте, другой --- на новом. Они не видят блокировок друг друга --- race condition. Решение: `private final Object lock = new Object()`. Ключевое слово `final` гарантирует, что ссылка не изменится после инициализации.

**False sharing.** Две переменные, расположенные на одной cache line (обычно 64 байта), вызывают cache invalidation даже если к ним обращаются разные потоки с разных ядер. Один поток пишет в переменную A, процессор инвалидирует cache line целиком --- поток на другом ядре, читающий соседнюю переменную B, вынужден перезагружать её из памяти. Аннотация `@Contended` (JDK 8+) добавляет padding между полями, разнося их по разным cache lines. `LongAdder` использует striping именно для избежания false sharing --- каждая ячейка (cell) находится на отдельной cache line.

**Pinning virtual threads.** `synchronized` внутри virtual thread «прикрепляет» его к carrier thread (platform thread) --- это называется pinning. Пока virtual thread находится внутри `synchronized`-блока, carrier thread не может обслуживать другие virtual threads. Если I/O-операция происходит внутри `synchronized`, carrier thread блокируется на уровне ОС --- это нивелирует преимущества virtual threads. Для virtual threads рекомендуется использовать `ReentrantLock` вместо `synchronized`, потому что `ReentrantLock` корректно поддерживает unmounting virtual thread при блокировке.

**Compound actions на thread-safe объектах.** Даже если отдельные операции thread-safe, их комбинация --- нет. Классический пример: `if (!map.containsKey(key)) map.put(key, value)` --- race condition даже с `ConcurrentHashMap`. Между `containsKey()` и `put()` другой поток может вставить значение. Решение: `map.putIfAbsent(key, value)` --- атомарная compound-операция, предоставляемая `ConcurrentHashMap`.

**Lock scope слишком широкий.** Синхронизация целых методов (`public synchronized void process()`) вместо минимально необходимого блока --- одна из самых частых ошибок. Если метод содержит I/O-операцию (HTTP-запрос, чтение файла) внутри synchronized --- все потоки стоят в очереди на время I/O. Правило: держите lock ровно столько, сколько необходимо для защиты shared state. I/O, длительные вычисления, вызовы внешних сервисов --- за пределами synchronized.

---

## Когда НЕ нужна синхронизация

Не каждый concurrent-код требует синхронизации. Понимание того, когда синхронизация **не** нужна, так же важно, как знание примитивов.

**Immutable objects.** Если объект не меняется после создания (все поля `final`, нет setter-ов, нет mutable state) --- он безопасен для sharing между потоками без синхронизации. `String`, `Integer`, `LocalDate` --- immutable. Но важно: ссылка на immutable объект должна быть опубликована безопасно (`final` поле, `volatile` ссылка, или через `synchronized`).

**Thread-local state.** Если данные принадлежат одному потоку и не расшариваются --- синхронизация не нужна. `ThreadLocal<T>` создаёт отдельную копию переменной для каждого потока. `SimpleDateFormat` не thread-safe, но `ThreadLocal<SimpleDateFormat>` --- безопасен.

**Stateless objects.** Объект без полей (или только с `final`-ссылками на immutable objects) --- thread-safe by design. Большинство Spring `@Service` и `@Controller` бинов stateless --- именно поэтому они безопасны как singletons.

---

## Связь с другими темами

**[[jvm-concurrency-overview]]** --- Примитивы синхронизации (synchronized, volatile, atomic) --- фундамент всей concurrency модели JVM. Обзор concurrency описывает общую картину: потоки, состояния, JMM, историю. Этот документ углубляется в конкретные механизмы обеспечения thread safety. Без понимания happens-before relationship из JMM невозможно объяснить, почему volatile обеспечивает visibility, а synchronized --- и visibility, и mutual exclusion. Рекомендуемый порядок: сначала обзор concurrency (карта), затем этот документ (детали).

**[[jvm-concurrent-collections]]** --- Concurrent collections (ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue) построены на примитивах, описанных в этом документе. ConcurrentHashMap использует CAS для `putIfAbsent()` и synchronized для bucket-level locks; CopyOnWriteArrayList --- ReentrantLock для защиты мутации; BlockingQueue --- Condition variables из ReentrantLock для producer-consumer координации. Понимание underlying примитивов помогает выбрать правильную коллекцию: если вы понимаете CAS contention, вы знаете, почему ConcurrentHashMap масштабируется лучше, чем `Collections.synchronizedMap()`.

**[[jvm-executors-futures]]** --- Executors и CompletableFuture --- высокоуровневые абстракции, позволяющие избежать прямой работы с примитивами синхронизации в application-коде. ThreadPoolExecutor инкапсулирует управление потоками и их синхронизацию; CompletableFuture заменяет ручные wait/notify цепочками функциональных преобразований. Рекомендуемый порядок: сначала примитивы (этот документ) для понимания фундамента, затем executors для production-кода --- так вы будете знать, что происходит «под капотом», когда CompletableFuture зависает или thread pool перегружен.

---

## Источники и дальнейшее чтение

- Goetz B. et al. (2006). *Java Concurrency in Practice*. --- Главы 2--5 (building blocks) и 14--16 (JMM, advanced synchronization) --- каноническое руководство по Java synchronization. Объясняет каждый примитив с теоретическим обоснованием и production-примерами. Обязательное чтение.
- Herlihy M., Shavit N. (2012). *The Art of Multiprocessor Programming*, Revised Edition. --- Глубокая теория: spin locks, CAS, lock-free structures, linearizability. Для тех, кто хочет понять, почему AtomicInteger работает корректно и что означает lock-free прогресс.
- Lea D. (2000). *Concurrent Programming in Java: Design Principles and Patterns*, 2nd Edition. --- Дуг Ли --- автор java.util.concurrent. Книга объясняет design rationale пакета: почему ReentrantLock спроектирован именно так, зачем нужна fairness, как работает AbstractQueuedSynchronizer (AQS).
- Oaks S. (2020). *Java Performance: In-Depth Advice for Tuning and Programming Java 8, 11, and Beyond*, 2nd Edition. --- Главы о synchronization overhead, biased locking, lock coarsening. Объясняет, как HotSpot JVM оптимизирует synchronized и почему его performance в Java 8+ значительно лучше, чем в Java 5.
- Dijkstra E. W. (1965). *Cooperating Sequential Processes*. --- Историческая работа, заложившая основы синхронизации: семафоры, mutual exclusion, проблема обедающих философов.
- Hoare C. A. R. (1974). *Monitors: An Operating System Structuring Concept*. --- Статья, описавшая мониторы --- конструкцию, ставшую основой synchronized в Java.

---

*Проверено: 2026-02-11 | Источники: JCIP, Herlihy & Shavit, Lea, Oaks, Dijkstra, Hoare --- Педагогический контент проверен*
