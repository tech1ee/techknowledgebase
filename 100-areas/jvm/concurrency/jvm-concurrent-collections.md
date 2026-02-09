---
title: "JVM Concurrent Collections: потокобезопасные коллекции"
created: 2025-11-25
modified: 2025-12-02
tags:
  - jvm
  - concurrency
  - collections
  - concurrent
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-synchronization]]"
---

# JVM Concurrent Collections: потокобезопасные коллекции

`ConcurrentHashMap` использует lock striping — отдельная блокировка на каждый bucket, потоки не блокируют друг друга при работе с разными ключами. `CopyOnWriteArrayList` создаёт копию массива при каждой записи — идеально для read-heavy сценариев, итерация никогда не бросит ConcurrentModificationException. `BlockingQueue` реализует producer-consumer с блокирующими put/take.

`Collections.synchronizedMap()` — один замок на всю карту, все потоки ждут. ConcurrentHashMap в 10 раз быстрее при 1000 потоках. CopyOnWriteArrayList: каждый add копирует весь массив — не для частых записей. LinkedBlockingQueue — unbounded по умолчанию, может съесть память.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Lock Striping** | Разделение данных на сегменты с отдельными блокировками |
| **Bucket** | Ячейка хэш-таблицы |
| **False Sharing** | Кэш-линии разных CPU конфликтуют из-за близости данных |
| **Copy-on-Write** | Создание копии при изменении |

---

## Почему обычные коллекции не подходят для многопоточности

`HashMap` при параллельном доступе может не просто вернуть неправильные данные — он может уйти в бесконечный цикл. Внутри HashMap — массив связных списков. При resize (увеличении размера) ссылки перестраиваются. Если два потока делают это одновременно, список может замкнуться в кольцо. Поток, итерирующий по нему, никогда не остановится.

`Collections.synchronizedMap()` решает проблему корректности, но создаёт новую — один глобальный lock на всё. Тысяча потоков, работающих с разными ключами, всё равно ждут друг друга.

Concurrent collections решают обе проблемы: корректность + высокий параллелизм.

## Сравнение подходов

| Коллекция | Блокировка | Когда использовать |
|-----------|------------|-------------------|
| `HashMap` | Нет | Строго один поток |
| `synchronizedMap` | Одна на всё | Мало потоков, простота важнее производительности |
| `ConcurrentHashMap` | По bucket'ам | Много потоков, нужна производительность |
| `CopyOnWriteArrayList` | Копирование при записи | Много чтений, редкие записи |

---

## ConcurrentHashMap

ConcurrentHashMap — рабочая лошадка многопоточного Java-кода. Это не просто "HashMap с блокировками", а отдельная структура данных, спроектированная для параллелизма с нуля.

### Эволюция дизайна

В Java 7 ConcurrentHashMap использовал фиксированное количество сегментов (по умолчанию 16). Каждый сегмент — отдельная мини-HashMap со своим lock. Проблема: если данные распределяются неравномерно, один сегмент становится hot spot.

Java 8 переработала дизайн. Теперь блокировка — на уровне отдельного bucket (ячейки массива). При низкой конкуренции используется CAS без блокировок вообще. При высокой конкуренции bucket превращается в красно-чёрное дерево для быстрого поиска.

### Почему быстрее synchronized

```java
// synchronizedMap — одна блокировка
Map<String, User> users = Collections.synchronizedMap(new HashMap<>());
// Поток 1 пишет в ключ "alice" → ВСЕ ждут
// Поток 2 хочет писать в "bob" → ЖДЁТ

// ConcurrentHashMap — блокировка по сегментам
ConcurrentHashMap<String, User> users = new ConcurrentHashMap<>();
// Поток 1 пишет в ключ "alice" → блокировка сегмента 5
// Поток 2 пишет в ключ "bob" → блокировка сегмента 12 → ПАРАЛЛЕЛЬНО!
```

### Lock Striping (полосная блокировка)

```
synchronizedMap (одна блокировка):
┌──────────────────────────────────────────────┐
│  [ОДНА БЛОКИРОВКА]                           │
│  bucket[0] bucket[1] ... bucket[1000]        │
└──────────────────────────────────────────────┘
Все потоки конкурируют за ОДНУ блокировку

ConcurrentHashMap (Java 8+):
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ bucket[0]   │ │ bucket[1]   │ │ bucket[2]   │
│ блокировка  │ │ блокировка  │ │ блокировка  │
└─────────────┘ └─────────────┘ └─────────────┘
Каждый bucket — отдельная блокировка
```

### Атомарные операции — ключ к корректности

Главная ошибка при работе с concurrent коллекциями — составные операции. "Проверить и добавить" — это ДВЕ операции. Между ними другой поток может вклиниться.

```java
// ❌ Race condition!
if (!map.containsKey(key)) {  // Поток B может вставить здесь
    map.put(key, value);       // И мы перезапишем его значение
}

// ✅ Одна атомарная операция
map.putIfAbsent(key, value);
```

ConcurrentHashMap предоставляет набор атомарных операций:

```java
ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();

// Атомарно: если нет — добавить, вернуть существующее или null
counts.putIfAbsent("errors", 0);

// Атомарно: вычислить значение при первом обращении (lazy initialization)
counts.computeIfAbsent("key", k -> expensiveCalculation(k));

// Атомарно: merge со старым значением (идеально для счётчиков)
counts.merge("errors", 1, Integer::sum);  // errors += 1

// Подсчёт слов в параллельном стриме — безопасно благодаря merge
words.parallelStream().forEach(word -> {
    counts.merge(word, 1, Integer::sum);
});
```

**Важно:** лямбда внутри `computeIfAbsent` должна быть быстрой и не иметь побочных эффектов. Она может вызываться под lock на bucket.

### Производительность

```
Тест: 1000 потоков, операции put/get

synchronizedMap:    ~1M ops/sec
ConcurrentHashMap:  ~10M ops/sec  — 10× быстрее
```

---

## CopyOnWriteArrayList

CopyOnWriteArrayList решает проблему, которую не решают блокировки: безопасная итерация во время модификации.

### Проблема с обычными списками

```java
// ❌ ConcurrentModificationException или хуже
for (Listener l : listeners) {
    l.onEvent(event);
    // Другой поток делает listeners.add(newListener) — крах
}
```

Даже `synchronizedList` не поможет — итератор не защищён. Нужно вручную синхронизировать весь цикл, что блокирует всех на время итерации.

### Решение: Copy-on-Write

При каждой записи создаётся полная копия внутреннего массива. Читатели продолжают работать со старой версией, не замечая изменений.

```java
CopyOnWriteArrayList<EventListener> listeners = new CopyOnWriteArrayList<>();

// Запись: создаёт новый массив, копирует старый + новый элемент
listeners.add(new MyListener());  // O(n) — дорого!

// Чтение: получает ссылку на текущий массив и итерирует
for (EventListener listener : listeners) {
    listener.onEvent(event);  // Никаких блокировок, никаких исключений
    // Даже если другой поток сделает add — мы итерируем по "снимку"
}
```

### Стоимость и компромиссы

Каждый `add()` — это аллокация нового массива и копирование всех элементов. Для списка из 1000 элементов это 1000 копирований на каждую вставку.

```
✅ Слушатели событий (add редко, iterate часто)
✅ Конфигурация (меняется редко, читается постоянно)
✅ Кэш маленького размера с редкими обновлениями

❌ Частые записи (каждый add = O(n))
❌ Большие списки (копирование мегабайтов на каждую запись)
❌ Нужна консистентность записей (reader видит "старый снимок")
```

---

## BlockingQueue

BlockingQueue — основа паттерна Producer-Consumer. Это не просто потокобезопасная очередь, а механизм координации между потоками.

### Зачем блокирующие операции

Обычная очередь при `poll()` пустой очереди возвращает null. Потребитель должен крутиться в цикле, постоянно проверяя. Это называется busy-waiting и тратит CPU впустую.

BlockingQueue решает это элегантно: `take()` блокирует поток до появления элемента. Поток спит, не потребляя ресурсы. Когда producer добавляет элемент — consumer просыпается.

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100);

// Производитель
executor.submit(() -> {
    queue.put(task);  // Блокируется если очередь полная (backpressure)
});

// Потребитель
executor.submit(() -> {
    Task task = queue.take();  // Спит до появления задачи
    process(task);
});
```

### Backpressure через ограниченную очередь

`ArrayBlockingQueue(100)` — это механизм backpressure. Если consumer не успевает — очередь заполняется. Когда достигнут лимит — producer блокируется на `put()`. Система автоматически балансируется.

Unbounded очередь (`LinkedBlockingQueue()` без размера) — опасна. Producer может наполнять её быстрее, чем consumer обрабатывает → OutOfMemoryError.

### Варианты очередей

| Очередь | Особенность | Когда использовать |
|---------|-------------|-------------------|
| `ArrayBlockingQueue` | Фиксированный размер, на массиве | Нужен backpressure |
| `LinkedBlockingQueue` | Опционально ограниченная | Гибкость размера |
| `PriorityBlockingQueue` | Элементы сортируются | Задачи с приоритетами |
| `SynchronousQueue` | Размер 0, прямая передача | Handoff между потоками |

`SynchronousQueue` — особенный случай. В ней никогда ничего не хранится. `put()` блокируется пока другой поток не вызовет `take()`. Это прямая передача из рук в руки. Используется в `Executors.newCachedThreadPool()`.

### Паттерн Производитель-Потребитель

```java
public class WorkerPool {
    private final BlockingQueue<Runnable> queue;
    private final List<Thread> workers = new ArrayList<>();

    public WorkerPool(int workerCount, int queueSize) {
        queue = new ArrayBlockingQueue<>(queueSize);

        for (int i = 0; i < workerCount; i++) {
            Thread worker = new Thread(() -> {
                while (!Thread.interrupted()) {
                    try {
                        Runnable task = queue.take();
                        task.run();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            });
            workers.add(worker);
            worker.start();
        }
    }

    public void submit(Runnable task) throws InterruptedException {
        queue.put(task);
    }
}
```

---

## Сравнение для выбора

```
Нужна Map:
  └─ Один поток?           → HashMap
  └─ Много потоков?        → ConcurrentHashMap
  └─ Простота важнее?      → synchronizedMap

Нужен List:
  └─ Много записей?        → synchronizedList
  └─ Много чтений?         → CopyOnWriteArrayList

Нужна очередь между потоками?
  └─ Ограниченная?         → ArrayBlockingQueue
  └─ Неограниченная?       → LinkedBlockingQueue
  └─ С приоритетами?       → PriorityBlockingQueue
```

---

## Типичные ошибки

### Итерация + модификация

```java
// ❌ Не атомарно!
if (!map.containsKey(key)) {
    map.put(key, value);
}

// ✅ Атомарно
map.putIfAbsent(key, value);
```

### Составная проверка

```java
// ❌ Между contains и get другой поток может удалить
if (map.contains(key)) {
    return map.get(key);
}

// ✅ Один вызов
return map.get(key);  // вернёт null если нет
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "ConcurrentHashMap всегда лучше HashMap" | ConcurrentHashMap имеет **overhead**. Для single-thread HashMap быстрее |
| "CopyOnWriteArrayList быстрый" | Копирование на каждой записи **дорого**. Только для read-heavy сценариев |
| "Collections.synchronizedMap = ConcurrentHashMap" | synchronizedMap блокирует **весь map**. ConcurrentHashMap — fine-grained locks (segments) |
| "BlockingQueue.poll() блокирует" | `poll()` **не блокирует**, возвращает null. `take()` блокирует до появления элемента |
| "Итерация по ConcurrentHashMap thread-safe" | Итератор **weakly consistent** — может не видеть concurrent updates. Это OK для большинства случаев |

---

## CS-фундамент

| CS-концепция | Применение в Concurrent Collections |
|--------------|-------------------------------------|
| **Lock Striping** | ConcurrentHashMap делит на segments с отдельными locks. Fine-grained concurrency |
| **Copy-on-Write** | CopyOnWriteArrayList: новый array при каждой записи. Идеально для read-heavy |
| **Producer-Consumer** | BlockingQueue связывает producers и consumers. Backpressure через bounded queue |
| **Compare-and-Swap** | ConcurrentHashMap.putIfAbsent использует CAS. Lock-free где возможно |
| **Weak Consistency** | Итераторы видят snapshot. Не бросают ConcurrentModificationException |

---

## Связи

- [[jvm-concurrency-overview]] — общая карта
- [[jvm-synchronization]] — примитивы синхронизации
- [[jvm-executors-futures]] — пулы потоков

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
