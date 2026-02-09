---
title: "JVM Memory Model: где живут объекты"
created: 2025-11-25
modified: 2025-12-28
tags:
  - jvm
  - memory
  - heap
  - stack
  - concurrency
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-gc-tuning]]"
  - "[[jvm-production-debugging]]"
  - "[[jvm-performance-overview]]"
  - "[[kotlin-coroutines]]"
  - "[[caching-strategies]]"
  - "[[microservices-vs-monolith]]"
---

# JVM Memory Model: где живут объекты

> JVM делит память на области с разным назначением. Heap хранит объекты (GC). Stack хранит локальные переменные. Java Memory Model (JMM) определяет правила видимости между потоками. Generational ZGC (Java 21) обеспечивает паузы <1ms при heap до 16TB.

---

## Зачем это нужно

### Проблема: Неправильное понимание памяти = production incidents

| Ситуация | Причина | Последствия |
|----------|---------|-------------|
| OutOfMemoryError: heap | Утечки памяти, недостаточный heap | Приложение падает |
| Высокие GC паузы | Неправильный выбор GC, настройки | Latency spikes, timeouts |
| Race conditions | Неправильная работа с volatile/synchronized | Data corruption |
| Container OOM Kill | Неучёт native memory | Kubernetes restart pod |

### Актуальность в 2024-2025

**Java 21 LTS — ключевые изменения:**

| Фича | Описание | Влияние на память |
|------|----------|-------------------|
| **Virtual Threads** | Миллионы потоков | Микроскопические стеки, меньше памяти |
| **Generational ZGC** | GC <1ms pause | -75% memory, +4x throughput vs old ZGC |
| **Sequenced Collections** | Новые API | — |

**Сравнение GC (2024-2025):**

| GC | Pause Time | Throughput | Heap Size | Когда использовать |
|----|------------|------------|-----------|---------------------|
| **G1GC** | 10-200ms | Высокий | До 64GB | Default, general purpose |
| **ZGC Gen** | <1ms | Высокий | До 16TB | Low latency, большие heap |
| **Shenandoah** | <10ms | Средний | До 1TB | OpenJDK alternative |

**Рекомендация 2025:**
```bash
# Для большинства приложений (Java 21+)
-XX:+UseZGC -XX:+ZGenerational -Xmx4g

# Для legacy или ограниченных ресурсов
-XX:+UseG1GC -Xmx4g -XX:MaxGCPauseMillis=200
```

### Container-aware настройки (критично!)

С Java 8u191+ JVM автоматически определяет лимиты контейнера:

```bash
# Автоматически (по умолчанию включено)
-XX:+UseContainerSupport

# Heap = 25% от container memory limit
# Можно изменить:
-XX:MaxRAMPercentage=75.0

# Пример: container с 2GB limit
# Heap ≈ 1.5GB (75% от 2GB)
```

**Важно:** Native memory (Metaspace, threads, buffers) не входит в Xmx! Оставляйте запас.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Heap (Куча)** | Область памяти для всех объектов, управляется GC |
| **Stack (Стек)** | Память потока для локальных переменных и вызовов |
| **Young Gen** | Область для короткоживущих объектов |
| **Old Gen** | Область для долгоживущих объектов |
| **Metaspace** | Память для метаданных классов (вне heap) |
| **GC Root** | Точка входа для определения достижимости объектов |

---

## Структура памяти JVM

Память JVM делится на две большие категории: Heap (куча) — общая для всех потоков область, где живут объекты, и Non-Heap — остальная память, включающая Metaspace и стеки потоков.

```
┌─────────────────────────────────────────────────────────────┐
│                        JVM MEMORY                            │
├──────────────────────────┬──────────────────────────────────┤
│     HEAP (shared)        │        NON-HEAP                  │
│                          │                                   │
│  ┌─────────────────────┐ │  ┌─────────────────────────────┐ │
│  │    Young Gen        │ │  │   Metaspace                 │ │
│  │  ┌──────┬────────┐  │ │  │   (класс метаданные)        │ │
│  │  │Eden  │Survivor│  │ │  └─────────────────────────────┘ │
│  │  └──────┴────────┘  │ │                                   │
│  └─────────────────────┘ │  ┌─────────────────────────────┐ │
│  ┌─────────────────────┐ │  │   Thread Stacks             │ │
│  │    Old Gen          │ │  │   (по одному на поток)      │ │
│  │   (tenured)         │ │  └─────────────────────────────┘ │
│  └─────────────────────┘ │                                   │
└──────────────────────────┴──────────────────────────────────┘
```

**Heap** — единственная область, управляемая Garbage Collector. Когда вы пишете `new Object()`, память выделяется именно здесь. Размер контролируется флагами `-Xms` (начальный) и `-Xmx` (максимальный).

**Metaspace** — хранит информацию о загруженных классах: структуру полей, методы, байткод. В отличие от старого PermGen (Java 7 и ранее), Metaspace находится в нативной памяти и растёт автоматически. Проблемы здесь редки, но возможны при динамической генерации классов (например, много Groovy скриптов или hot-reload в development).

**Thread Stacks** — каждый поток получает свой стек фиксированного размера (по умолчанию ~1MB). При 1000 потоках это уже 1GB только на стеки, что часто упускают при расчёте памяти.

---

## Heap: где живут объекты

### Generational Hypothesis

Heap разделён на поколения на основе эмпирического наблюдения: подавляющее большинство объектов живут очень недолго. Исследования показывают, что 90-98% объектов становятся мусором в течение нескольких миллисекунд после создания.

Типичный пример — обработка HTTP-запроса. За один запрос создаются десятки временных объектов: DTO для передачи данных, StringBuilder для формирования ответа, итераторы для обхода коллекций, промежуточные результаты вычислений. Все они нужны только на время обработки запроса и сразу после становятся мусором.

Если бы GC проверял все объекты одинаково, он тратил бы много времени на проверку долгоживущих объектов (кэши, синглтоны, connection pools), которые годами остаются живыми. Разделение на поколения решает эту проблему: Young Gen собирается часто, но быстро (потому что большинство объектов уже мертвы), Old Gen — редко, но дольше.

```java
public List<UserDTO> getUsers() {
    List<User> users = userRepository.findAll();

    // Все эти объекты — короткоживущие, идеальные кандидаты для Young Gen
    List<UserDTO> dtos = new ArrayList<>();  // Временный список
    for (User user : users) {
        UserDTO dto = new UserDTO();         // Временный объект
        dto.setName(user.getName());         // Временная строка (возможно)
        dtos.add(dto);
    }
    return dtos;  // Только dtos выживет и уйдёт в Old Gen (если доживёт)
}
```

### Жизненный цикл объекта

Каждый объект проходит через определённые этапы жизни в памяти. Понимание этого цикла помогает диагностировать проблемы с памятью и оптимизировать приложение.

**Eden Space** — место рождения объектов. При вызове `new` объект создаётся здесь. Eden обычно составляет 80% Young Gen и заполняется быстро.

**Minor GC** — когда Eden заполняется, запускается Minor GC. Он проверяет только Young Gen, находит живые объекты и копирует их в Survivor Space. Мёртвые объекты просто забываются — их память становится свободной.

**Survivor Spaces (S0 и S1)** — два пространства, работающие по принципу ping-pong. Живые объекты копируются из одного в другое при каждом Minor GC. Каждое копирование увеличивает "возраст" объекта.

**Promotion (продвижение)** — когда объект пережил достаточно Minor GC (по умолчанию 15), он считается долгоживущим и перемещается в Old Gen.

```
new Object()
    │
    ▼
Eden Space (новые объекты)
    │
    │ Minor GC
    ▼
Survivor S0 (age=1)
    │
    │ Minor GC
    ▼
Survivor S1 (age=2)
    │
    │ ... повторяется до age=15
    ▼
Old Gen (age >= 15)
    │
    │ Major GC (когда Old Gen заполнен)
    ▼
Удалён (если нет ссылок)
```

### Настройка размеров

Размеры областей памяти критично влияют на производительность. Слишком маленький Young Gen приводит к частым Minor GC, слишком большой — к длинным паузам.

```bash
# Общий heap: -Xms (начальный) и -Xmx (максимальный)
# Рекомендация: ставить одинаковыми, чтобы избежать resize в runtime
-Xms2g -Xmx2g

# Соотношение Old:Young (по умолчанию 2:1)
# При -Xmx3g это означает Old=2g, Young=1g
-XX:NewRatio=2

# Соотношение Eden:Survivor (по умолчанию 8:1)
# При Young=1g это означает Eden=800MB, каждый Survivor=100MB
-XX:SurvivorRatio=8
```

**Практические следствия:**
- Увеличение Young Gen уменьшает частоту Minor GC, но увеличивает их длительность
- Для приложений с большим количеством короткоживущих объектов (веб-сервисы) стоит увеличить Young Gen
- Для приложений с большими долгоживущими кэшами — увеличить Old Gen

---

## Stack: вызовы методов

Каждый поток в JVM имеет собственный Stack, недоступный другим потокам. Это ключевое отличие от Heap: данные в Stack не требуют синхронизации, потому что принадлежат только одному потоку.

Stack хранит два типа данных:
- **Локальные переменные** — примитивы хранятся полностью (int, boolean, double), для объектов хранится только ссылка (сам объект в Heap)
- **Stack frames** — информация о вызовах методов (какой метод, откуда вызван, куда вернуться)

При вызове метода создаётся новый frame, при возврате — frame удаляется. Это автоматическое управление памятью без участия GC.

```java
public void main() {
    int x = 10;                    // Stack: примитив (4 байта)
    User user = new User("Alice"); // Stack: ссылка (8 байт) → Heap: объект
    calculate(x);
}

public void calculate(int a) {
    int result = a * 2;            // Stack: новый frame с локальными переменными
}  // ← frame удаляется, result исчезает
```

Визуализация памяти при выполнении `calculate(x)`:

```
STACK (Thread main)              HEAP
┌──────────────────┐            ┌────────────────┐
│ calculate()      │            │ User object    │
│   a = 10         │            │  name="Alice"  │
│   result = 20    │            └────────────────┘
├──────────────────┤                  ▲
│ main()           │                  │
│   x = 10         │                  │
│   user ──────────┼──────────────────┘
└──────────────────┘
```

### StackOverflowError

Stack имеет фиксированный размер (по умолчанию ~1MB на поток). Переполнение происходит при слишком глубокой вложенности вызовов — чаще всего из-за бесконечной рекурсии.

```java
public void recursive() {
    recursive();  // Каждый вызов добавляет frame в Stack
}
// → StackOverflowError после ~10000-20000 вызовов (зависит от размера frame)
```

Размер Stack настраивается флагом `-Xss`. Увеличивать стоит осторожно — это влияет на каждый поток:

```bash
-Xss512k   # Уменьшить для приложений с тысячами потоков
-Xss2m     # Увеличить для глубокой рекурсии

# Пример расчёта памяти:
# 1000 потоков × 1MB = 1GB только на стеки
# 1000 потоков × 512KB = 500MB — уже экономия
```

**Практические следствия:**
- При создании много потоков (серверные приложения) уменьшайте размер Stack
- При глубокой рекурсии увеличивайте Stack или переписывайте на итерацию
- Virtual Threads (Java 21) решают проблему, используя микроскопические стеки

---

## GC Roots: что держит объекты живыми

Garbage Collector работает по принципу достижимости (reachability). Объект считается живым, если до него можно добраться от одного из GC Roots — специальных "точек входа".

**GC Roots включают:**
- Локальные переменные активных методов (в Stack)
- Static поля классов
- Активные потоки
- JNI ссылки (ссылки из нативного кода)

Всё, что недостижимо от GC Roots, считается мусором и будет удалено.

```
GC Roots:
├─ Локальные переменные (stack всех потоков)
├─ Static поля загруженных классов
├─ Активные потоки (Thread объекты)
└─ JNI Global References
```

Практический пример утечки памяти:

```java
// Static поле — это GC Root
static Map<String, User> cache = new HashMap<>();

void process() {
    User temp = new User("Bob");  // temp — локальная переменная = GC Root
    cache.put("bob", temp);       // Теперь User достижим через cache
}  // temp уходит из Stack, но User ЖИВ через static cache!

// Через месяц cache содержит миллион записей
// GC не может их удалить — они достижимы от GC Root (static поле)
```

**Практические следствия:**
- Static коллекции без ограничений — частая причина утечек
- Используйте WeakHashMap или bounded caches (Caffeine, Guava Cache)
- Подписки на события (listeners) — вторая частая причина: объект подписался, но не отписался

---

## Java Memory Model (JMM): видимость между потоками

JMM — это не про структуру памяти, а про **правила видимости** изменений между потоками. Без понимания JMM легко написать код с race conditions.

### Проблема видимости

Каждый поток может иметь локальную копию переменных (CPU cache). Без синхронизации изменения одного потока могут быть невидимы другому.

```java
// ПРОБЛЕМА: поток 2 может никогда не увидеть flag = true
class Visibility {
    boolean flag = false;  // Не volatile!

    void thread1() {
        flag = true;  // Записали в CPU cache потока 1
    }

    void thread2() {
        while (!flag) {  // Читаем из CPU cache потока 2
            // Бесконечный цикл!
        }
    }
}
```

### Happens-Before (гарантии порядка)

JMM определяет отношение **happens-before**: если A happens-before B, то все изменения в A видны в B.

| Правило | Пример |
|---------|--------|
| **Thread.start()** | Всё до start() видно в новом потоке |
| **Thread.join()** | Всё в потоке видно после join() |
| **volatile write → read** | Запись видна последующим чтениям |
| **synchronized exit → enter** | Выход из synchronized видно при входе |

### volatile

`volatile` гарантирует:
1. **Видимость** — запись видна всем потокам
2. **Запрет reordering** — memory barriers до и после

```java
class SafeVisibility {
    volatile boolean flag = false;  // volatile!

    void thread1() {
        flag = true;  // Запись с memory barrier
    }

    void thread2() {
        while (!flag) {  // Чтение с memory barrier
            // Корректно завершится
        }
    }
}
```

**Важно:** volatile НЕ делает операции атомарными!

```java
volatile int counter = 0;

void increment() {
    counter++;  // НЕ атомарно! Read-modify-write
}

// Решение: AtomicInteger или synchronized
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();  // Атомарно
```

### Double-Checked Locking

Классический пример, где volatile критичен:

```java
// БЕЗ volatile — сломано!
class Singleton {
    private static Singleton instance;

    static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();  // Может быть reordered!
                }
            }
        }
        return instance;
    }
}

// С volatile — корректно
class Singleton {
    private static volatile Singleton instance;  // volatile!

    static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

---

## Virtual Threads (Java 21)

Virtual Threads меняют правила работы с памятью:

### Преимущества

| Аспект | Platform Threads | Virtual Threads |
|--------|------------------|-----------------|
| **Stack size** | ~1MB | ~несколько KB |
| **1M потоков** | ~1TB RAM | ~несколько GB |
| **Переключение** | OS scheduler (дорого) | JVM (дёшево) |

### Особенности памяти

```java
// Создание миллиона virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 1_000_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}
// ~несколько GB вместо ~1TB для platform threads
```

### Pinning (блокировка carrier thread)

Virtual thread "приклеивается" к carrier thread в:
- `synchronized` блоках
- Native методах

```java
// ❌ ПЛОХО — pinning, блокирует carrier thread
synchronized (lock) {
    Thread.sleep(1000);  // Virtual thread не может отсоединиться
}

// ✅ ХОРОШО — ReentrantLock не вызывает pinning
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    Thread.sleep(1000);  // Virtual thread может отсоединиться
} finally {
    lock.unlock();
}
```

### ThreadLocal осторожно!

```java
// ❌ ПЛОХО — миллионы virtual threads = миллионы копий
ThreadLocal<ExpensiveObject> cache = new ThreadLocal<>();

// ✅ ХОРОШО — ScopedValue (Java 21)
// Или shared cache с синхронизацией
```

---

## Native Memory Tracking (NMT)

JVM использует память за пределами heap. NMT помогает её отследить.

### Включение NMT

```bash
# Включить NMT (5-10% overhead)
-XX:NativeMemoryTracking=summary   # или detail

# Получить отчёт
jcmd <pid> VM.native_memory summary

# Сравнение (найти утечки)
jcmd <pid> VM.native_memory baseline
# ... время проходит ...
jcmd <pid> VM.native_memory summary.diff
```

### Категории native memory

```
Native Memory Tracking:
Total: 2345MB
- Java Heap:     1024MB  ← -Xmx
- Class:         150MB   ← Metaspace
- Thread:        120MB   ← Stack × потоки
- Code:          80MB    ← JIT compiled code
- GC:            60MB    ← GC structures
- Internal:      50MB    ← JVM internal
- Symbol:        30MB    ← Symbol table
- Native Memory Tracking: 20MB ← NMT overhead
```

### Важно для контейнеров

```bash
# Container memory = Heap + Native
# Пример для 4GB container:
# - Heap: 2.5GB (-Xmx2500m)
# - Metaspace: 256MB
# - Thread stacks: 200MB (200 threads × 1MB)
# - Buffers, GC, etc: 500MB
# - Safety margin: 544MB
# Total: ~4GB
```

---

## OutOfMemoryError: виды и диагностика

### Java heap space

```
java.lang.OutOfMemoryError: Java heap space
```

**Что произошло:** Heap переполнен, GC не может освободить достаточно памяти для создания нового объекта.

**Причины:**
- Утечка памяти — объекты накапливаются, но не удаляются
- Недостаточный heap для объёма данных
- Большие объекты (например, загрузка огромного файла в память)

**Диагностика:**
```bash
# Увеличить heap (временное решение)
-Xmx4g

# Автоматический heap dump при OOM (для анализа)
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/

# Анализ heap dump
# 1. Открыть в Eclipse MAT
# 2. Leak Suspects Report покажет подозрительные объекты
# 3. Dominator Tree покажет что держит больше всего памяти
```

### Metaspace

```
java.lang.OutOfMemoryError: Metaspace
```

**Что произошло:** Область метаданных классов переполнена.

**Причины:**
- Динамическая генерация классов (Groovy, hot-reload frameworks)
- Утечка ClassLoader — загруженные классы не выгружаются
- Слишком много зависимостей с уникальными классами

**Диагностика:**
```bash
# Увеличить лимит Metaspace
-XX:MaxMetaspaceSize=512m

# Мониторинг количества загруженных классов
jcmd <pid> VM.class_hierarchy
```

### StackOverflowError

```
java.lang.StackOverflowError
```

**Что произошло:** Stack потока переполнен из-за слишком глубокой вложенности вызовов.

**Причины:**
- Бесконечная рекурсия (самая частая)
- Очень глубокая легитимная рекурсия (обход глубоких деревьев)

**Решение:**
```bash
# Увеличить размер Stack
-Xss2m

# Или переписать рекурсию на итерацию (лучше)
```

### Unable to create native thread

```
java.lang.OutOfMemoryError: unable to create new native thread
```

**Что произошло:** ОС не может создать новый поток.

**Причины:**
- Достигнут лимит потоков ОС (ulimit)
- Недостаточно памяти для Stack нового потока
- Слишком много потоков уже создано

**Решение:**
```bash
# Linux: увеличить лимит процессов
ulimit -u 65536

# Уменьшить размер Stack каждого потока
-Xss512k

# Использовать пулы потоков вместо создания новых
```

---

## Memory Leaks в Java

Технически в Java нет классических утечек памяти — GC удаляет недостижимые объекты. Но есть "логические утечки": объекты, которые приложению не нужны, но остаются достижимыми от GC Roots.

### Типичные паттерны утечек

**1. Static коллекции без ограничений:**
```java
// ПРОБЛЕМА: cache никогда не очищается
static List<User> cache = new ArrayList<>();

void process(User user) {
    cache.add(user);  // Добавляем, но никогда не удаляем
}

// РЕШЕНИЕ: использовать bounded cache
static Cache<String, User> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(10))
    .build();
```

**2. Незакрытые ресурсы:**
```java
// ПРОБЛЕМА: ресурс держит нативную память
FileInputStream fis = new FileInputStream(path);
// Забыли fis.close()

// РЕШЕНИЕ: try-with-resources
try (FileInputStream fis = new FileInputStream(path)) {
    // работа с файлом
}  // автоматически закроется
```

**3. Listeners без отписки:**
```java
// ПРОБЛЕМА: listener держит ссылку на объект
eventBus.register(this);  // Подписались
// Объект "удалён", но живёт через eventBus

// РЕШЕНИЕ: явная отписка
@Override
public void onDestroy() {
    eventBus.unregister(this);
}
```

**4. ThreadLocal без очистки:**
```java
// ПРОБЛЕМА: в пуле потоков ThreadLocal живёт вечно
ThreadLocal<User> currentUser = new ThreadLocal<>();
currentUser.set(user);
// Поток вернулся в пул, но ThreadLocal остался

// РЕШЕНИЕ: очистка в finally
try {
    currentUser.set(user);
    // работа
} finally {
    currentUser.remove();
}
```

### Диагностика утечек

```bash
# Получить heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Или через jmap
jmap -dump:live,format=b,file=heap.hprof <pid>
```

**Анализ в Eclipse MAT:**
1. **Leak Suspects Report** — автоматически находит подозрительные объекты
2. **Dominator Tree** — показывает что держит больше всего памяти
3. **Path to GC Roots** — показывает цепочку ссылок от GC Root до объекта

---

## Quick Reference

| Область | Что хранит | Управление | Ошибка переполнения |
|---------|-----------|------------|---------------------|
| Heap | Объекты | GC | OutOfMemoryError: heap |
| Stack | Локальные переменные, вызовы | Автоматически (при выходе) | StackOverflowError |
| Metaspace | Метаданные классов | GC (частично) | OutOfMemoryError: Metaspace |

| Флаг | Назначение | Пример |
|------|-----------|--------|
| `-Xms` / `-Xmx` | Min/max heap | `-Xms2g -Xmx2g` |
| `-Xss` | Stack на поток | `-Xss512k` |
| `-XX:NewRatio` | Old:Young соотношение | `-XX:NewRatio=2` |
| `-XX:MaxMetaspaceSize` | Лимит Metaspace | `-XX:MaxMetaspaceSize=512m` |
| `-XX:+HeapDumpOnOutOfMemoryError` | Dump при OOM | — |

---

## Куда дальше

**Следующий шаг — GC:**
→ [[jvm-gc-tuning]] — выбор и настройка сборщика мусора. Понимание Memory Model без знания GC неполно.

**Диагностика проблем:**
→ [[jvm-production-debugging]] — heap dump, thread dump, jcmd. Когда в production OutOfMemoryError.
→ [[jvm-profiling]] — async-profiler, Eclipse MAT. Как найти утечки до production.

**Общая картина:**
→ [[jvm-performance-overview]] — карта всех аспектов производительности JVM.

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Java Memory Model = структура памяти JVM" | JMM — это правила видимости между потоками (happens-before), не про Heap/Stack. Структура памяти — отдельная тема |
| "volatile делает операции атомарными" | volatile гарантирует видимость и запрет reordering. Но counter++ не атомарен! Используйте AtomicInteger |
| "-Xmx определяет всю память JVM" | Xmx — только heap. Native memory (Metaspace, threads, buffers) не включена. В контейнерах оставляйте 25% запас |
| "GC паузы = плохой код" | GC паузы — normal behavior. G1 10-200ms, ZGC <1ms. Проблема в неправильном выборе GC для use case |
| "Young Gen всегда 1/3 heap" | Соотношение настраивается. Для веб-сервисов (много short-lived objects) Young Gen можно увеличить |
| "ThreadLocal безопасен в пулах потоков" | ThreadLocal может протечь! В пулах потоки переиспользуются. Всегда remove() в finally |
| "OutOfMemoryError = heap переполнен" | OOM имеет разные виды: heap, Metaspace, native threads, unable to create thread. Причины разные |
| "Virtual Threads решают все проблемы памяти" | Virtual Threads экономят stack memory. Но ThreadLocal с ними опасен — миллион VT = миллион копий |
| "Static = живёт вечно" | Static fields — GC roots. Они держат объекты живыми. Static cache без ограничений = утечка |
| "Heap dump — это всё для диагностики" | Heap dump показывает объекты. Thread dump показывает что делают потоки. Часто нужны оба |

---

## CS-фундамент

| CS-концепция | Применение в JVM Memory |
|--------------|------------------------|
| **Stack vs Heap** | Stack — LIFO для вызовов методов, per-thread. Heap — общая память для объектов, managed by GC |
| **Generational Hypothesis** | 90%+ объектов умирают молодыми. Young Gen собирается часто, Old Gen — редко |
| **Reachability Analysis** | GC определяет live objects через достижимость от GC Roots. Недостижимые — мусор |
| **Memory Barriers** | volatile/synchronized создают memory barriers — точки синхронизации между CPU caches |
| **Happens-Before** | Частичный порядок операций для visibility. Thread.start() happens-before первая операция потока |
| **Cache Coherence** | Каждый CPU имеет cache. JMM определяет когда изменения видны другим потокам |
| **Reference Types** | Strong, Soft, Weak, Phantom references — разные уровни "живости" для GC |
| **Escape Analysis** | JIT определяет, "убегает" ли объект из scope. Не убегает — можно на stack (скалярная замена) |
| **TLAB (Thread-Local Allocation Buffer)** | Каждый поток имеет private buffer в Eden для быстрого allocation без синхронизации |
| **Card Table / Remembered Sets** | Отслеживание ссылок между поколениями для эффективного Minor GC |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Oracle: Java Virtual Machine Specification](https://docs.oracle.com/javase/specs/jvms/se21/html/) | Спецификация | Memory areas, threads |
| 2 | [Oracle: Virtual Threads](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) | Документация | Virtual threads, pinning |
| 3 | [Oracle: ZGC Tuning Guide](https://docs.oracle.com/en/java/javase/21/gctuning/z-garbage-collector.html) | Документация | Generational ZGC, tuning |
| 4 | [JSR-133 FAQ (Java Memory Model)](https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html) | Спецификация | Happens-before, volatile |
| 5 | [Jenkov: Java Memory Model](https://jenkov.com/tutorials/java-concurrency/java-memory-model.html) | Туториал | JMM объяснение |
| 6 | [Oracle: Native Memory Tracking](https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/tooldescr007.html) | Документация | NMT, jcmd |
| 7 | [DZone: Troubleshooting Native Memory](https://dzone.com/articles/troubleshooting-problems-with-native-off-heap-memo) | Статья | Native memory leaks |
| 8 | [Medium: ZGC Low Latency at Scale](https://medium.com/@codesprintpro/javas-z-garbage-collector-achieving-low-latency-at-scale-809fb43bf046) | Статья | ZGC benchmarks |
| 9 | [Red Hat: Choosing Java GC](https://developers.redhat.com/articles/2021/11/02/how-choose-best-java-garbage-collector) | Руководство | GC selection |
| 10 | [Sematext: OutOfMemoryError Guide](https://sematext.com/blog/java-lang-outofmemoryerror/) | Статья | OOM types, diagnosis |

---

*Проверено: 2026-01-09 | Педагогический контент проверен — Уровень достоверности: high*
