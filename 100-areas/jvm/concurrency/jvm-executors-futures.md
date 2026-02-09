---
title: "JVM Executors & Futures: управление потоками"
created: 2025-11-25
modified: 2025-12-02
tags:
  - jvm
  - concurrency
  - executors
  - completablefuture
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-synchronization]]"
  - "[[java-modern-features]]"
---

# JVM Executors & Futures: управление потоками

ExecutorService — пул потоков, переиспользующий потоки вместо создания новых (Thread стоит ~1MB стека и ~1мс). CompletableFuture — функциональная композиция асинхронных операций: цепочки (thenApply), комбинирование (thenCombine), обработка ошибок (exceptionally).

`Executors.newFixedThreadPool()` с неограниченной очередью съест память при перегрузке — нужен ThreadPoolExecutor с ограничениями. Забытый `shutdown()` — программа не завершится, потоки не-демоны. CompletableFuture: 3 HTTP-запроса параллельно вместо последовательных. В Java 21 Virtual Threads заменяют пулы для I/O-bound задач.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Пул потоков (Thread Pool)** | Набор переиспользуемых потоков |
| **Очередь задач (Work Queue)** | Очередь ожидающих выполнения задач |
| **Future** | Результат асинхронной операции |
| **Callback** | Функция, вызываемая по завершении |

---

## ExecutorService: пулы потоков

Создание потока — дорогая операция. Каждый Thread занимает ~1MB стека и требует системного вызова для создания. При обработке 10000 запросов в секунду создание нового потока на каждый запрос убьёт производительность.

Пул потоков решает эту проблему: потоки создаются один раз и переиспользуются. Задачи попадают в очередь, свободный поток берёт следующую задачу.

### Типы пулов и их внутренности

```java
// Фиксированный пул — N потоков, неограниченная LinkedBlockingQueue
// Потоки никогда не умирают, очередь растёт бесконечно (опасно!)
ExecutorService fixed = Executors.newFixedThreadPool(10);

// Кэширующий пул — от 0 до Integer.MAX_VALUE потоков
// Потоки живут 60 сек без работы, очередь SynchronousQueue (размер 0)
// Каждая задача либо берётся потоком, либо создаётся новый поток
ExecutorService cached = Executors.newCachedThreadPool();

// Один поток — гарантирует последовательное выполнение
// Задачи выполняются в порядке поступления
ExecutorService single = Executors.newSingleThreadExecutor();

// Запланированные задачи — для отложенного и периодического выполнения
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(5);
```

### Отправка задач

```java
ExecutorService executor = Executors.newFixedThreadPool(10);

// Без результата
executor.execute(() -> System.out.println("Задача"));

// С результатом
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

// Получить результат (блокирует)
Integer result = future.get();

// С таймаутом
Integer result = future.get(5, TimeUnit.SECONDS);
```

### Правильное завершение

```java
executor.shutdown();  // Не принимать новые, дождаться текущих

if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
    executor.shutdownNow();  // Прервать всё
}
```

### Конфигурация вручную (рекомендуется для production)

Фабричные методы `Executors.*` скрывают опасные дефолты. В production создавайте пулы вручную с явными параметрами.

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                              // corePoolSize — минимум потоков (всегда живы)
    10,                             // maximumPoolSize — максимум при пиках
    60L, TimeUnit.SECONDS,          // время жизни потоков сверх corePoolSize
    new LinkedBlockingQueue<>(100), // очередь задач С ОГРАНИЧЕНИЕМ
    new ThreadPoolExecutor.CallerRunsPolicy()  // политика отказа
);
```

**Как работает расширение:** Сначала создаются corePoolSize потоков. Новые задачи идут в очередь. Если очередь заполнилась — создаются дополнительные потоки до maximumPoolSize. Если и они заняты — применяется rejection policy.

### Политики отказа (Rejection Policy)

Что делать, когда пул и очередь переполнены?

| Политика | Что делает | Когда использовать |
|----------|-----------|-------------------|
| `AbortPolicy` | Бросает RejectedExecutionException | Нужно знать о перегрузке |
| `CallerRunsPolicy` | Выполняет в вызывающем потоке | Естественный backpressure |
| `DiscardPolicy` | Молча отбрасывает задачу | Задачи не критичны |
| `DiscardOldestPolicy` | Отбрасывает самую старую | Старые задачи менее важны |

**CallerRunsPolicy** — часто лучший выбор. Когда пул перегружен, вызывающий поток сам выполняет задачу. Это замедляет producer — естественный backpressure без потери задач.

---

## CompletableFuture: асинхронная композиция

`Future` из Java 5 позволяет получить результат асинхронной операции, но только через блокирующий `get()`. Нельзя сказать "когда завершится — сделай это". Нельзя скомпоновать несколько futures.

`CompletableFuture` (Java 8) — это и Future, и Promise. Можно строить цепочки преобразований, комбинировать результаты, обрабатывать ошибки — всё без блокирующих вызовов.

### Создание

```java
// Асинхронное выполнение в ForkJoinPool.commonPool()
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    return fetchData();  // Выполняется в background
});

// С указанием пула — рекомендуется для I/O операций
// commonPool размером Runtime.getRuntime().availableProcessors()
// Если все потоки заблокированы на I/O — всё приложение встанет
CompletableFuture<String> future = CompletableFuture.supplyAsync(
    () -> fetchData(),
    ioExecutor  // Отдельный пул для I/O
);
```

### Цепочки преобразований

```java
CompletableFuture.supplyAsync(() -> "hello")
    .thenApply(s -> s + " world")        // Преобразовать результат
    .thenApply(String::toUpperCase)      // Ещё одно преобразование
    .thenAccept(System.out::println);    // Использовать результат
// Вывод: HELLO WORLD
```

### Комбинирование

```java
CompletableFuture<User> userFuture = fetchUserAsync(userId);
CompletableFuture<List<Order>> ordersFuture = fetchOrdersAsync(userId);

// Объединить два результата
CompletableFuture<Dashboard> dashboard = userFuture
    .thenCombine(ordersFuture, (user, orders) -> new Dashboard(user, orders));

// Дождаться всех
CompletableFuture.allOf(future1, future2, future3)
    .thenRun(() -> System.out.println("Все завершены"));

// Дождаться любого
CompletableFuture.anyOf(future1, future2, future3)
    .thenAccept(result -> System.out.println("Первый: " + result));
```

### Обработка ошибок

```java
CompletableFuture.supplyAsync(() -> {
    if (Math.random() > 0.5) throw new RuntimeException("Ошибка");
    return 42;
})
.exceptionally(ex -> {
    System.err.println("Ошибка: " + ex.getMessage());
    return -1;  // Значение по умолчанию
})
.thenAccept(System.out::println);

// Или handle для обоих случаев
.handle((result, ex) -> {
    if (ex != null) return -1;
    return result;
});
```

### Реальный пример: параллельные запросы

```java
public CompletableFuture<UserProfile> getUserProfile(int userId) {
    // Три запроса параллельно
    CompletableFuture<User> user = fetchUserAsync(userId);
    CompletableFuture<List<Post>> posts = fetchPostsAsync(userId);
    CompletableFuture<Settings> settings = fetchSettingsAsync(userId);

    return user.thenCombine(posts, (u, p) -> new Pair<>(u, p))
               .thenCombine(settings, (pair, s) ->
                   new UserProfile(pair.getFirst(), pair.getSecond(), s));
}
```

---

## ScheduledExecutorService

### Запуск с задержкой

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Одноразово через 5 секунд
scheduler.schedule(() -> {
    System.out.println("Выполнено через 5 сек");
}, 5, TimeUnit.SECONDS);
```

### Периодическое выполнение

```java
// Каждые 10 секунд (от начала предыдущего)
scheduler.scheduleAtFixedRate(() -> {
    checkHealth();
}, 0, 10, TimeUnit.SECONDS);

// Каждые 10 секунд (от конца предыдущего)
scheduler.scheduleWithFixedDelay(() -> {
    processQueue();
}, 0, 10, TimeUnit.SECONDS);
```

### Разница Rate vs Delay

```
scheduleAtFixedRate (каждые 10 сек):
|──задача──|     |──задача──|     |──задача──|
0         5     10        15     20
           └─────10 сек───┘

scheduleWithFixedDelay (10 сек ПОСЛЕ завершения):
|──задача──|          |──задача──|
0         5──10 сек──15        20
```

---

## Выбор стратегии

```
Задача                              Решение
─────────────────────────────────────────────────
Фиксированная нагрузка           → newFixedThreadPool(N)
Короткие задачи, пики            → newCachedThreadPool()
Последовательное выполнение      → newSingleThreadExecutor()
Периодические задачи             → newScheduledThreadPool(N)
Много I/O (Java 21+)             → Virtual Threads
```

---

## Типичные ошибки

### Забытый shutdown

```java
// ❌ Программа не завершится — потоки не демоны
ExecutorService executor = Executors.newFixedThreadPool(10);
executor.submit(task);
// Программа висит!

// ✅ Всегда shutdown
try {
    executor.submit(task);
} finally {
    executor.shutdown();
}
```

### Бесконечная очередь

```java
// ❌ newFixedThreadPool имеет неограниченную очередь
// При перегрузке съест всю память
ExecutorService bad = Executors.newFixedThreadPool(2);

// ✅ Ограниченная очередь + политика отказа
ThreadPoolExecutor good = new ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    new ArrayBlockingQueue<>(100),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

### Игнорирование исключений

```java
// ❌ Исключение проглочено
executor.submit(() -> {
    throw new RuntimeException("Ошибка");
});

// ✅ Обработка через Future
Future<?> future = executor.submit(() -> {
    throw new RuntimeException("Ошибка");
});
try {
    future.get();
} catch (ExecutionException e) {
    log.error("Ошибка в задаче", e.getCause());
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Executors.newFixedThreadPool безопасен" | Unbounded очередь может вызвать **OOM**. Используйте ThreadPoolExecutor с bounded queue |
| "CompletableFuture асинхронный всегда" | Без `Async` суффикса (`thenApply`) выполняется в **том же thread**. `thenApplyAsync` — в ForkJoinPool |
| "Future.get() — плохо" | `get()` **нормален** для простых случаев. Проблема — блокировать много threads. CompletableFuture для chains |
| "Virtual Threads решают всё" | Virtual Threads для **I/O-bound**. CPU-bound задачи по-прежнему нуждаются в Platform Threads с ограниченным pool |
| "Больше threads = быстрее" | После N_cores — **overhead** от context switching. ThreadPool sizing важен |

---

## CS-фундамент

| CS-концепция | Применение в Executors |
|--------------|------------------------|
| **Thread Pool Pattern** | Reuse threads вместо создания новых. Amortize creation cost |
| **Producer-Consumer** | Submit task (producer) → BlockingQueue → Worker thread (consumer) |
| **Work Stealing** | ForkJoinPool: idle thread берёт задачи из очереди другого. Load balancing |
| **Future/Promise** | Future = placeholder для результата. Promise = возможность записать результат |
| **Backpressure** | Bounded queue + rejection policy предотвращают overload |

---

## Связи

- [[jvm-concurrency-overview]] — общая карта
- [[jvm-concurrent-collections]] — потокобезопасные коллекции
- [[java-modern-features]] — Virtual Threads

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
