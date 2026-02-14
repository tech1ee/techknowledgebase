---
title: "Kotlin Channels: каналы, CSP и select"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
tags:
  - topic/kotlin
  - type/deep-dive
  - level/advanced
related:
  - "[[kotlin-coroutines]]"
  - "[[kotlin-flow]]"
  - "[[kotlin-coroutines-internals]]"
  - "[[android-flow-guide]]"
  - "[[jvm-concurrent-collections]]"
prerequisites:
  - "[[kotlin-coroutines]]"
reading_time: 40
difficulty: 6
study_status: not_started
mastery: 0
---

# Kotlin Channels: каналы, CSP и select

> Полное руководство по Kotlin Channels: теория CSP, типы каналов, produce builder, select expression, паттерн Actor, сравнение с Flow, практические паттерны для Android и backend.

---

## Зачем это нужно

### Проблема: безопасная коммуникация между корутинами

Корутины позволяют запускать тысячи конкурентных задач с минимальными затратами ресурсов. Но возникает фундаментальный вопрос: **как эти задачи обмениваются данными?**

| Подход | Проблема |
|--------|----------|
| **Shared mutable state** | Race conditions, data corruption, need for locks |
| **Mutex/locks** | Deadlocks, priority inversion, сложная отладка |
| **Atomic variables** | Годятся только для примитивных значений |
| **Callbacks** | Callback hell, сложное управление порядком |

Философия Go, которую Kotlin Channels реализуют:

> **Don't communicate by sharing memory; share memory by communicating.**
> -- Rob Pike, Go Proverbs

Channels предоставляют примитив коммуникации между корутинами, при котором данные передаются через канал, а не через общую память. Отправитель кладёт элемент в канал через `send()`, получатель забирает через `receive()` -- обе операции являются suspend-функциями, что обеспечивает естественную синхронизацию без явных блокировок.

### Когда Channel, а не Flow

Flow -- это абстракция для потоков данных от одного источника к одному или нескольким потребителям. Channel -- это примитив коммуникации между двумя или более корутинами. Ключевое различие:

- **Flow** -- для data streams: наблюдение за БД, сетевые обновления, UI-состояние
- **Channel** -- для communication: передача задач воркерам, one-time events, координация корутин

### Актуальность 2025-2026

| Изменение | Версия | Значение |
|-----------|--------|----------|
| **Новый алгоритм каналов** | kotlinx.coroutines 1.9+ | 10-25% быстрее в sequential-сценариях, на порядок быстрее для workloads с интенсивной коммуникацией (issue #3621) |
| **Меньше аллокаций** | 1.9+ | Каналы без onUndeliveredElement аллоцируют меньше памяти (#3646) |
| **BroadcastChannel deprecated** | 1.7+ → 1.10 | Уровень deprecation повышен. Замена: SharedFlow |
| **actor builder deprecated** | 1.5+ | @ObsoleteCoroutinesApi. Замена: sealed class + Channel или Mutex |
| **select всё ещё experimental** | 1.10 | @ExperimentalCoroutinesApi, но стабилен на практике, API может измениться |
| **Kotlin/Native atomic transformations** | 1.10 | Уменьшают footprint coroutine-heavy кода на всех платформах |
| **Channel в Android** | Стандарт 2025 | receiveAsFlow() для one-time events, trySend() из non-suspend контекста |

В kotlinx.coroutines 1.10 (выпуск под Kotlin 2.1.0) каналы получили внутреннюю оптимизацию без изменения внешнего API. Это означает, что знание API каналов, полученное сейчас, останется актуальным на годы вперёд.

---

## TL;DR

- **Channel** -- примитив коммуникации между корутинами. send() и receive() -- suspend-операции, обеспечивающие синхронизацию без блокировок
- **Четыре типа**: Rendezvous (capacity=0, синхронный обмен), Buffered (capacity=N), Unlimited (без ограничений, риск OOM), Conflated (хранит только последний элемент)
- **produce {}** -- builder для создания канала с автоматическим закрытием. Основа паттернов pipeline, fan-out, fan-in
- **select {}** -- мультиплексирование нескольких каналов: первый готовый выигрывает. Experimental, но стабильно работает
- **actor deprecated** -- используйте sealed class + Channel или Mutex + encapsulated state
- **Channel vs Flow**: Channel для communication (горячий, one-to-one), Flow для data streams (холодный, one-to-many)
- **В Android**: Channel<UiEvent> + receiveAsFlow() -- стандартный паттерн для one-time events в ViewModel

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin Coroutines | suspend functions, CoroutineScope, structured concurrency | [[kotlin-coroutines]] |
| Kotlin Flow (базово) | Понимать отличие холодных и горячих потоков | [[kotlin-flow]] |
| JVM Concurrency (базово) | Threads, locks, BlockingQueue -- для понимания аналогий | [[jvm-concurrency-overview]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Channel** | Канал для передачи данных между корутинами | Труба между двумя комнатами -- через неё можно передавать предметы |
| **send()** | Отправить элемент в канал (suspend) | Положить посылку на конвейер |
| **receive()** | Получить элемент из канала (suspend) | Забрать посылку с конвейера |
| **Rendezvous** | Канал без буфера: отправитель ждёт получателя | Передача из рук в руки -- оба должны встретиться |
| **Buffered channel** | Канал с буфером на N элементов | Полка на N посылок: отправитель кладёт и уходит |
| **close()** | Закрыть канал для отправки | Повесить табличку "закрыто" на окно приёма посылок |
| **produce {}** | Builder, создающий канал и корутину-производителя | Конвейер, который автоматически останавливается когда работа закончена |
| **select {}** | Ожидание первого готового канала | Кассы в супермаркете: идёшь к первой свободной |
| **fan-out** | Один производитель, несколько потребителей | Один повар, несколько официантов разносят блюда |
| **fan-in** | Несколько производителей, один потребитель | Несколько поваров, один раздаточный стол |
| **CSP** | Communicating Sequential Processes -- теория Хоара | Правила работы почтовой системы: процессы общаются только через каналы |

---

## Основы Channel

### Теория: Communicating Sequential Processes (CSP)

В 1978 году Тони Хоар (C.A.R. Hoare) опубликовал фундаментальную работу "Communicating Sequential Processes". Ключевая идея CSP:

```
Традиционный подход (shared memory):
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│ Process A │────>│  Shared Variable │<────│ Process B │
└──────────┘     │  (need locks!)   │     └──────────┘
                 └──────────────────┘

CSP подход (message passing):
┌──────────┐     ┌─────────┐     ┌──────────┐
│ Process A │────>│ Channel │────>│ Process B │
└──────────┘     └─────────┘     └──────────┘
                 No shared state!
```

В CSP процессы (в Kotlin -- корутины) являются последовательными и общаются исключительно через каналы. Отправка и получение -- это точки синхронизации: процесс приостанавливается, пока другой процесс не будет готов к обмену. Это устраняет необходимость в мьютексах и делает конкурентный код предсказуемым.

Go-каналы -- прямая реализация CSP. Kotlin Channels -- реализация тех же идей поверх suspend-функций корутин.

### CSP vs Actor Model: ключевые отличия

Две главные модели конкурентности через message passing:

```
CSP (Hoare, 1978):
┌──────────┐                   ┌──────────┐
│ Process A │── named channel ──│ Process B │
│ (anon.)   │                   │ (anon.)   │
└──────────┘                   └──────────┘
Процессы анонимны, каналы именованы.
Отправка синхронна (рандеву по умолчанию).

Actor Model (Hewitt, 1973):
┌──────────┐                   ┌──────────────┐
│ Actor X  │── message to Y ──>│ Actor Y       │
│ (named)  │                   │ (named, mailbox)│
└──────────┘                   └──────────────┘
Акторы именованы, каналы (mailbox) встроены.
Отправка асинхронна.
```

| Аспект | CSP | Actor Model |
|--------|-----|-------------|
| Идентичность | Процессы анонимны | Акторы именованы (адрес) |
| Каналы | Явные, именованные | Неявные (mailbox актора) |
| Отправка | Синхронная (рандеву) | Асинхронная (fire-and-forget) |
| Топология | Гибкая: M:N через каналы | Один mailbox на актор |
| Реализации | Go channels, Kotlin Channels, Clojure core.async | Erlang/OTP, Akka, Kotlin actor (deprecated) |

Kotlin выбрал CSP как основную модель. Buffered Channel добавляет элемент асинхронности (sender не ждёт receiver, если есть место в буфере), но фундаментально это CSP-модель.

### Создание канала и базовые операции

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

fun main() = runBlocking {
    // Создаём канал целых чисел (Rendezvous по умолчанию)
    val channel = Channel<Int>()

    // Корутина-отправитель
    launch {
        for (x in 1..5) {
            println("Sending $x")
            channel.send(x) // suspend, пока получатель не готов
        }
        channel.close() // Сигнал: больше элементов не будет
    }

    // Корутина-получатель (итерация по каналу)
    for (value in channel) { // suspend на каждом receive
        println("Received $value")
    }
    println("Done")
}
```

Вывод (порядок Sending/Received чередуется, т.к. Rendezvous):
```
Sending 1
Received 1
Sending 2
Received 2
Sending 3
Received 3
Sending 4
Received 4
Sending 5
Received 5
Done
```

### send() и receive() как suspend-операции

`send()` и `receive()` -- suspend-функции. Это значит, что они приостанавливают корутину, не блокируя поток:

```kotlin
// send() приостанавливает, если:
// - Rendezvous: нет получателя
// - Buffered: буфер полон
// - Канал закрыт: бросает ClosedSendChannelException

// receive() приостанавливает, если:
// - Канал пуст (нет элементов)
// - Канал закрыт и пуст: бросает ClosedReceiveChannelException
```

### Неприостанавливающие альтернативы: trySend() и tryReceive()

Для ситуаций, когда suspend невозможен (например, из обычной функции):

```kotlin
val channel = Channel<Int>(capacity = 10)

// trySend -- не suspend, не бросает исключений
val result = channel.trySend(42)
when {
    result.isSuccess -> println("Sent")
    result.isFailure -> println("Channel full or closed")
    result.isClosed -> println("Channel closed")
}

// tryReceive -- не suspend, не бросает исключений
val received = channel.tryReceive()
received.getOrNull()?.let { println("Got: $it") }
    ?: println("Channel empty or closed")
```

Важно: `trySend()` и `tryReceive()` работают только для каналов с буфером. Для Rendezvous-канала `trySend()` всегда вернёт failure (некуда положить элемент без ожидания).

### Закрытие канала

Закрытие канала -- односторонняя операция. После `close()`:

```kotlin
val channel = Channel<String>()

launch {
    channel.send("Hello")
    channel.send("World")
    channel.close() // После этого:
    // channel.send("!") // ClosedSendChannelException!
}

launch {
    // receive() работает, пока есть элементы
    // Когда канал закрыт И пуст: ClosedReceiveChannelException
    // Безопасная итерация через for:
    for (msg in channel) {
        println(msg) // "Hello", "World"
    }
    // for завершается нормально после close + все элементы получены
}
```

### Итерация: for vs consumeEach

```kotlin
// Вариант 1: for loop (рекомендуется для fan-out)
for (element in channel) {
    process(element)
}

// Вариант 2: consumeEach (НЕ для множественных потребителей!)
channel.consumeEach { element ->
    process(element)
}
// consumeEach отменяет канал при исключении
// Безопасен только для единственного потребителя

// Вариант 3: receiveCatching (для ручного контроля)
while (true) {
    val result = channel.receiveCatching()
    if (result.isClosed) break
    val value = result.getOrThrow()
    process(value)
}
```

### onUndeliveredElement: гарантия очистки ресурсов

Если через канал передаются ресурсы (файлы, соединения), важно гарантировать их закрытие даже при отмене:

```kotlin
// Паттерн: безопасная передача ресурсов через канал
val channel = Channel<Connection>(
    capacity = Channel.BUFFERED,
    onUndeliveredElement = { connection ->
        // Вызывается если элемент не был доставлен:
        // - Канал отменён с элементами в буфере
        // - send() отменён после помещения в буфер
        // - receive() отменён после извлечения
        connection.close()
    }
)

// Теперь ресурсы гарантированно закрываются
launch {
    val conn = openConnection()
    channel.send(conn) // Если отменено -- onUndeliveredElement закроет conn
}

launch {
    val conn = channel.receive() // Если отменено -- onUndeliveredElement закроет conn
    try {
        conn.use { /* работа с соединением */ }
    } finally {
        conn.close()
    }
}
```

Callback `onUndeliveredElement` вызывается синхронно в произвольном контексте. Он должен быть быстрым, неблокирующим и не бросать исключений.

---

## Типы Channel

Kotlin предоставляет четыре типа каналов, различающихся стратегией буферизации:

```
Rendezvous (capacity = 0):
Sender ──[wait]──> <──[wait]── Receiver
         Оба ждут друг друга

Buffered (capacity = N):
Sender ──> [1][2][3][ ][ ] ──> Receiver
           Буфер на N элементов

Unlimited (Channel.UNLIMITED):
Sender ──> [1][2][3][4][5][6][7]... ──> Receiver
           Неограниченный буфер (OOM risk!)

Conflated (Channel.CONFLATED):
Sender ──> [last] ──> Receiver
           Хранит только последний элемент
```

### BufferOverflow: стратегии переполнения

Помимо четырёх основных типов, каналы поддерживают стратегии переполнения буфера через параметр `onBufferOverflow`:

```kotlin
// DROP_OLDEST: при переполнении самый старый элемент удаляется
val channel = Channel<Int>(
    capacity = 3,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST: при переполнении новый элемент отбрасывается
val channel = Channel<Int>(
    capacity = 3,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)

// SUSPEND (по умолчанию): send() suspend'ится при полном буфере
val channel = Channel<Int>(
    capacity = 3,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

Channel.CONFLATED по сути эквивалентен `Channel(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`.

### Rendezvous Channel (capacity = 0)

Канал без буфера. Sender приостанавливается до тех пор, пока Receiver не вызовет receive(), и наоборот. Это прямая реализация CSP-рандеву.

```kotlin
val channel = Channel<Int>() // По умолчанию Rendezvous

launch {
    println("Before send") // 1
    channel.send(1)        // suspend пока receive() не вызван
    println("After send")  // 3
}

launch {
    delay(1000) // Имитируем задержку
    println("Before receive") // 2
    val value = channel.receive()
    println("Received: $value") // 4
}
```

**Когда использовать:**
- Строгая синхронизация между producer и consumer
- Когда обработка должна идти в lockstep
- Для guaranteed handoff (передача из рук в руки)

### Buffered Channel (capacity = N)

Канал с буфером фиксированного размера. Sender приостанавливается только когда буфер полон. Receiver приостанавливается только когда буфер пуст.

```kotlin
val channel = Channel<Int>(capacity = 3) // Буфер на 3 элемента

launch {
    for (i in 1..5) {
        println("Sending $i")
        channel.send(i) // suspend только если буфер полон
    }
    channel.close()
}

launch {
    delay(500) // Consumer медленнее
    for (value in channel) {
        println("Received $value")
        delay(300)
    }
}
// Вывод: Sending 1, 2, 3 (буфер заполнен),
// затем чередование send/receive
```

**Когда использовать:**
- Producer быстрее consumer (сглаживание burst'ов)
- Когда допустима небольшая задержка обработки
- Пулы задач с ограниченной очередью

```kotlin
// Стандартный размер буфера из системных свойств
val channel = Channel<Int>(Channel.BUFFERED)
// Размер = значение kotlinx.coroutines.channels.defaultBuffer
// По умолчанию: 64
```

### Unlimited Channel (Channel.UNLIMITED)

Канал с неограниченным буфером. Sender никогда не приостанавливается (кроме случая закрытого канала).

```kotlin
val channel = Channel<Event>(Channel.UNLIMITED)

launch {
    // Отправка никогда не suspend'ится
    repeat(1_000_000) {
        channel.send(Event(it)) // Мгновенно, всё в буфере
    }
    // ОПАСНО: 1M объектов в памяти!
}
```

**Когда использовать:**
- Очереди логирования/аналитики, где потеря данных недопустима
- Ситуации, когда producer гарантированно быстрее consumer на ограниченное время
- **С осторожностью!** Без ограничения буфера -- прямой путь к OOM

### Conflated Channel (Channel.CONFLATED)

Буфер на один элемент с политикой DROP_OLDEST. Новый send() перезаписывает предыдущее значение, если оно не было получено.

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

launch {
    channel.send(1)
    channel.send(2)
    channel.send(3) // Перезаписывает 2, которое перезаписало 1
}

launch {
    delay(100)
    println(channel.receive()) // 3 -- только последнее значение
}
```

**Когда использовать:**
- Обновления местоположения GPS (важно только текущее)
- Обновления прогресса (промежуточные значения не нужны)
- Любой сценарий "latest value wins"

### Сводная таблица типов каналов

| Тип | Capacity | send() suspend? | receive() suspend? | Потеря данных | Типичный кейс |
|-----|----------|-----------------|--------------------|----|-------|
| **Rendezvous** | 0 | Да, всегда | Да, если пусто | Нет | Строгая синхронизация |
| **Buffered** | N | Если буфер полон | Если пусто | Нет | Burst smoothing |
| **Unlimited** | MAX | Нет | Если пусто | Нет (но OOM) | Логирование, аналитика |
| **Conflated** | 1 | Нет | Если пусто | Да (старые) | GPS, прогресс |

---

## produce builder

### Основы produce

`produce {}` -- coroutine builder, который создаёт канал и корутину-производителя. Канал автоматически закрывается, когда блок produce завершается (нормально или с исключением):

```kotlin
// Без produce: нужно вручную закрывать канал
fun CoroutineScope.manualProducer(): ReceiveChannel<Int> {
    val channel = Channel<Int>()
    launch {
        try {
            for (i in 1..5) channel.send(i)
        } finally {
            channel.close() // Легко забыть!
        }
    }
    return channel
}

// С produce: канал закрывается автоматически
fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    for (i in 1..5) {
        send(i) // this = ProducerScope, у которого есть send()
    }
    // close() вызывается автоматически при выходе из блока
}
```

`produce` возвращает `ReceiveChannel<T>` -- из него можно только получать элементы. Это обеспечивает правильную инкапсуляцию: потребитель не может отправить ничего обратно производителю через тот же канал.

### Pipeline: цепочка преобразований

Pipeline -- паттерн, где выход одного produce становится входом другого:

```kotlin
// Этап 1: генерация чисел
fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    var x = 1
    while (true) {
        send(x++)
        delay(100) // Симулируем работу
    }
}

// Этап 2: возведение в квадрат
fun CoroutineScope.square(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) {
        send(x * x)
    }
}

// Этап 3: фильтрация
fun CoroutineScope.filterEven(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) {
        if (x % 2 == 0) send(x)
    }
}

// Использование pipeline
fun main() = runBlocking {
    val numbers = produceNumbers()      // 1, 2, 3, 4, 5, ...
    val squares = square(numbers)       // 1, 4, 9, 16, 25, ...
    val evenSquares = filterEven(squares) // 4, 16, 36, 64, ...

    // Отмена корутины каскадно отменяет весь pipeline
    repeat(5) {
        println(evenSquares.receive())
    }
    coroutineContext.cancelChildren() // Отменяем все этапы pipeline
}
```

Pipeline реализует ленивую обработку: каждый этап обрабатывает элемент только когда следующий этап готов его принять (в случае Rendezvous-канала).

### Fan-out: один производитель, несколько потребителей

Несколько корутин могут получать из одного канала. Каждый элемент обрабатывается ровно одним потребителем:

```kotlin
fun CoroutineScope.produceTasks(): ReceiveChannel<String> = produce {
    var taskId = 0
    while (true) {
        send("Task-${taskId++}")
        delay(50) // Генерируем задачи
    }
}

fun CoroutineScope.processTask(id: Int, tasks: ReceiveChannel<String>) = launch {
    for (task in tasks) { // Безопасный fan-out через for
        println("Worker $id processing $task")
        delay(200) // Обработка занимает время
    }
}

fun main() = runBlocking {
    val tasks = produceTasks()

    // Запускаем 5 воркеров, каждый забирает задачи из одного канала
    repeat(5) { workerId ->
        processTask(workerId, tasks)
    }

    delay(2000) // Работаем 2 секунды
    coroutineContext.cancelChildren()
}
```

Важно: при fan-out используйте `for` loop, а не `consumeEach`. `consumeEach` отменяет весь канал при исключении в одном из потребителей, что нарушит работу остальных.

### Fan-in: несколько производителей, один потребитель

Несколько корутин могут отправлять в один канал:

```kotlin
// Несколько источников данных отправляют в один канал
suspend fun sendMessages(
    channel: SendChannel<String>,
    source: String,
    count: Int
) {
    repeat(count) {
        channel.send("[$source] Message $it")
        delay(100)
    }
}

fun main() = runBlocking {
    val channel = Channel<String>()

    // Запускаем 3 производителя
    launch { sendMessages(channel, "API", 5) }
    launch { sendMessages(channel, "DB", 5) }
    launch { sendMessages(channel, "Cache", 5) }

    // Один потребитель получает из всех источников
    repeat(15) {
        println(channel.receive())
    }
}
```

Альтернативный подход через produce и merge:

```kotlin
fun CoroutineScope.mergeChannels(
    vararg channels: ReceiveChannel<String>
): ReceiveChannel<String> = produce {
    // Запускаем корутину для каждого входного канала
    channels.forEach { ch ->
        launch {
            for (msg in ch) {
                send(msg) // Все отправляют в один produce-канал
            }
        }
    }
}
```

---

## select expression

### Что такое select

`select {}` позволяет ожидать несколько suspend-операций одновременно и выполнить ту, которая станет доступна первой. Это аналог `select()` в POSIX для сокетов или `select` в Go.

```
select {} -- мультиплексор:

    Channel A ──┐
                ├──> select {} ──> result
    Channel B ──┘

Ожидает первый готовый канал и выполняет его clause.
```

Статус: `@ExperimentalCoroutinesApi`. API может измениться, но удаление маловероятно. На практике select стабильно работает с момента появления в библиотеке.

### Selecting from multiple channels: onReceive

```kotlin
import kotlinx.coroutines.selects.*

suspend fun selectFromTwo(
    channelA: ReceiveChannel<String>,
    channelB: ReceiveChannel<String>
): String = select {
    channelA.onReceive { value ->
        "A: $value" // Выполнится, если channelA готов первым
    }
    channelB.onReceive { value ->
        "B: $value" // Выполнится, если channelB готов первым
    }
}

fun main() = runBlocking {
    val fast = produce {
        delay(100)
        send("fast response")
    }
    val slow = produce {
        delay(500)
        send("slow response")
    }

    val result = selectFromTwo(fast, slow)
    println(result) // "A: fast response"
    coroutineContext.cancelChildren()
}
```

### onReceiveCatching: безопасный select

`onReceive` бросает исключение, если канал закрыт. `onReceiveCatching` возвращает `ChannelResult`:

```kotlin
suspend fun selectOrDefault(
    channelA: ReceiveChannel<Int>,
    channelB: ReceiveChannel<Int>
): Int = select {
    channelA.onReceiveCatching { result ->
        result.getOrNull() ?: -1 // -1 если канал закрыт
    }
    channelB.onReceiveCatching { result ->
        result.getOrNull() ?: -2
    }
}
```

### onSend: ожидание готовности к отправке

```kotlin
suspend fun produceToFastest(
    channelA: SendChannel<Int>,
    channelB: SendChannel<Int>,
    value: Int
) {
    select {
        channelA.onSend(value) {
            println("Sent to A")
        }
        channelB.onSend(value) {
            println("Sent to B")
        }
    }
}
```

### onAwait: select с Deferred

```kotlin
suspend fun fetchFirstResponse(
    apiA: Deferred<String>,
    apiB: Deferred<String>
): String = select {
    apiA.onAwait { "API A: $it" }
    apiB.onAwait { "API B: $it" }
}

// Использование: first-response pattern
fun main() = runBlocking {
    val apiA = async {
        delay(300)
        "Response from server A"
    }
    val apiB = async {
        delay(100)
        "Response from server B"
    }

    // Получаем первый готовый результат
    val fastest = fetchFirstResponse(apiA, apiB)
    println(fastest) // "API B: Response from server B"

    coroutineContext.cancelChildren()
}
```

### Bias в select

`select` является biased -- при одновременной доступности нескольких clause'ов приоритет отдаётся первому по порядку объявления:

```kotlin
// Если оба канала готовы одновременно:
select {
    channelA.onReceive { /* ПРИОРИТЕТ: этот clause первый */ }
    channelB.onReceive { /* Выполнится, только если channelA не готов */ }
}
```

Для справедливого выбора можно рандомизировать порядок clause'ов:

```kotlin
// Fair select: рандомизируем порядок clause'ов
suspend fun <T> fairSelect(
    channels: List<ReceiveChannel<T>>
): T {
    val shuffled = channels.shuffled()
    return select {
        shuffled.forEach { ch ->
            ch.onReceive { it }
        }
    }
}
```

Bias -- это осознанный design choice: он предсказуем и позволяет задавать приоритеты. Например, можно поместить высокоприоритетный канал первым, чтобы его сообщения обрабатывались в первую очередь.

### Практический пример: мультиплексирование с таймаутом

```kotlin
sealed class Result {
    data class Data(val value: String) : Result()
    data object Timeout : Result()
    data object ChannelClosed : Result()
}

suspend fun receiveWithTimeout(
    channel: ReceiveChannel<String>,
    timeoutMs: Long
): Result {
    return select {
        channel.onReceiveCatching { result ->
            if (result.isClosed) Result.ChannelClosed
            else Result.Data(result.getOrThrow())
        }
        onTimeout(timeoutMs) {
            Result.Timeout
        }
    }
}

fun main() = runBlocking {
    val channel = Channel<String>()

    launch {
        delay(2000)
        channel.send("Late response")
    }

    when (val result = receiveWithTimeout(channel, 500)) {
        is Result.Data -> println("Got: ${result.value}")
        is Result.Timeout -> println("Timeout!") // Этот вариант
        is Result.ChannelClosed -> println("Channel closed")
    }

    coroutineContext.cancelChildren()
}
```

### Цикл select для непрерывного мультиплексирования

```kotlin
// Непрерывно получаем из нескольких каналов
suspend fun multiplex(
    channels: List<ReceiveChannel<String>>,
    output: SendChannel<String>
) {
    while (true) {
        val message = select {
            channels.forEach { ch ->
                ch.onReceiveCatching { result ->
                    result.getOrNull()
                }
            }
        }
        if (message != null) {
            output.send(message)
        } else {
            break // Все каналы закрыты
        }
    }
}
```

---

## Actor pattern

### Что такое Actor

Actor -- это корутина, которая инкапсулирует изменяемое состояние и принимает сообщения через Channel (mailbox). Внешний мир взаимодействует с Actor'ом только через отправку сообщений, что гарантирует thread safety без блокировок.

```
Actor model (Carl Hewitt, 1973):

External World ──send()──> [Mailbox/Channel] ──receive()──> Actor Coroutine
                                                              │
                                                        Mutable State
                                                    (доступно только Actor'у)
```

### Почему actor deprecated в Kotlin

Функция `actor {}` в kotlinx.coroutines помечена `@ObsoleteCoroutinesApi`. Причины:

1. **Дизайн имеет известные дефекты** -- нет proper supervision, нет typed actor system
2. **Планируется полный редизайн** -- JetBrains планировала создать полноценную actor-систему (complex actors), но приоритеты сместились
3. **Существуют более простые альтернативы** -- sealed class + Channel или Mutex решают большинство задач
4. **SharedFlow/StateFlow перекрывают основные use cases** -- для reactive state management

```kotlin
// DEPRECATED: Не используйте actor {} builder
@ObsoleteCoroutinesApi
val counterActor = actor<CounterMsg> {
    var counter = 0
    for (msg in channel) { /* ... */ }
}
```

### Альтернатива 1: sealed class + Channel

Современный паттерн -- использовать sealed class/interface для определения сообщений и Channel для их передачи:

```kotlin
// Определяем типы сообщений
sealed interface CounterCommand {
    data object Increment : CounterCommand
    data object Decrement : CounterCommand
    data class GetValue(val response: CompletableDeferred<Int>) : CounterCommand
}

// Actor как класс с инкапсулированным каналом
class CounterActor(scope: CoroutineScope) {
    private var counter = 0
    private val commands = Channel<CounterCommand>(Channel.UNLIMITED)

    init {
        scope.launch {
            for (cmd in commands) {
                when (cmd) {
                    is CounterCommand.Increment -> counter++
                    is CounterCommand.Decrement -> counter--
                    is CounterCommand.GetValue -> cmd.response.complete(counter)
                }
            }
        }
    }

    suspend fun increment() = commands.send(CounterCommand.Increment)
    suspend fun decrement() = commands.send(CounterCommand.Decrement)

    suspend fun getValue(): Int {
        val response = CompletableDeferred<Int>()
        commands.send(CounterCommand.GetValue(response))
        return response.await()
    }
}

// Использование
fun main() = runBlocking {
    val counter = CounterActor(this)

    // 100 корутин инкрементируют конкурентно
    val jobs = List(100) {
        launch {
            repeat(1000) {
                counter.increment()
            }
        }
    }
    jobs.forEach { it.join() }

    println("Counter = ${counter.getValue()}") // Всегда 100000
}
```

### Альтернатива 2: Mutex + encapsulated state

Для простых сценариев Mutex часто проще:

```kotlin
class SafeCounter {
    private val mutex = Mutex()
    private var counter = 0

    suspend fun increment() = mutex.withLock { counter++ }
    suspend fun decrement() = mutex.withLock { counter-- }
    suspend fun getValue(): Int = mutex.withLock { counter }
}
```

**Когда Channel-based actor, когда Mutex:**

| Критерий | sealed class + Channel | Mutex |
|----------|------------------------|-------|
| Сложная логика обработки | Да -- switch/when по типам сообщений | Нет |
| Простой shared state | Overkill | Да -- проще и нагляднее |
| Гарантия порядка обработки | Да -- FIFO | Нет -- зависит от scheduler'а |
| Много операций с одним состоянием | Да | Mutex withLock на каждую операцию |
| Производительность (high contention) | Лучше (нет lock overhead) | Хуже (contention на lock) |

---

## Channel vs Flow

### Фундаментальные различия

```
Channel (горячий):
Producer ──> [Channel] ──> Consumer
Работает независимо от наличия потребителей.
Каждый элемент доставляется ровно одному потребителю.

Flow (холодный):
              ┌──> Collector A (своя копия)
Source ──> Flow
              └──> Collector B (своя копия)
Запускается заново для каждого подписчика.
```

### Сравнительная таблица

| Характеристика | Channel | Flow |
|----------------|---------|------|
| **Природа** | Горячий (hot) | Холодный (cold) по умолчанию |
| **Запуск** | Работает с момента создания | Запускается при collect() |
| **Потребители** | Один элемент -- один потребитель (fan-out) | Каждый collector получает все элементы |
| **Буферизация** | Встроенная (4 типа) | Через оператор buffer() |
| **Backpressure** | Через suspend send() | Через suspend emit()/collect() |
| **Операторы** | Минимум (нет map, filter и т.д.) | Богатый набор (map, filter, flatMap, debounce...) |
| **Lifecycle** | Ручное управление (close, cancel) | Привязан к coroutine scope через collect |
| **Тестирование** | Ручная отправка/получение | Turbine, тестовые коллекторы |
| **Android** | One-time events | UI state (StateFlow), data streams |
| **Многоразовость** | Нет -- канал нельзя "перезапустить" | Да -- flow builder вызывается заново при каждом collect |
| **Thread safety** | Да -- встроенная синхронизация | Да -- через structured concurrency |

### Decision guide: когда что

```
Нужна коммуникация между корутинами?
├── Да ──> Channel
│   ├── Worker pool ──> Channel + fan-out
│   ├── Event bus ──> Channel + receiveAsFlow()
│   └── Координация ──> Channel (Rendezvous)
│
└── Нет, нужен data stream
    ├── Один подписчик, cold ──> flow {}
    ├── Состояние UI ──> StateFlow
    ├── События (broadcast) ──> SharedFlow
    └── Трансформации данных ──> flow {} с операторами
```

### Внутренняя реализация: как Channel работает под капотом

На высоком уровне Channel -- это конкурентная структура данных, реализованная через lock-free алгоритмы. В kotlinx.coroutines 1.9+ используется новый алгоритм на основе сегментированных массивов (FAA-based queue), который обеспечивает:

```
Внутренняя структура Channel (упрощённо):

┌─────────────────────────────────────────────┐
│                   Channel                    │
│                                             │
│  Senders Queue    Buffer     Receivers Queue│
│  [S1][S2][S3]  [E1][E2][E3]  [R1][R2][R3]  │
│                                             │
│  sendersHead ──>            <── receiversHead│
│                                             │
│  State: EMPTY | HAS_BUFFER | CLOSED          │
└─────────────────────────────────────────────┘
```

Ключевые детали реализации:
- **Lock-free**: операции используют CAS (Compare-And-Swap) вместо блокировок, что позволяет избежать context switching на уровне ОС
- **Segment-based**: вместо linked list используются массивы сегментов фиксированного размера, что улучшает cache locality
- **Prompt cancellation**: если корутина отменена во время suspend на send/receive, элемент корректно обрабатывается через onUndeliveredElement

Эти детали объясняют, почему Channel на порядок быстрее java.util.concurrent.BlockingQueue для coroutine-based кода: нет блокировки потоков, нет overhead на park/unpark.

### channelFlow и callbackFlow: мост между Channel и Flow

Когда нужна мощь каналов внутри Flow API:

```kotlin
// channelFlow: Flow с возможностью отправки из разных корутин
fun mergedDataFlow(): Flow<Data> = channelFlow {
    // Можно запускать несколько корутин
    launch {
        apiService.fetchData().forEach { send(it) }
    }
    launch {
        database.observe().collect { send(it) }
    }
}

// callbackFlow: адаптация callback API в Flow
fun locationFlow(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            trySend(result.lastLocation) // Не suspend!
        }
    }
    locationClient.requestLocationUpdates(request, callback, looper)

    awaitClose {
        locationClient.removeLocationUpdates(callback)
    }
}
```

---

## Channel в Android

### One-time events в ViewModel

Самый частый use case для Channel в Android -- one-time events (навигация, показ Snackbar, Toast). В отличие от StateFlow, который хранит последнее значение и переигрывает его при resubscribe, Channel гарантирует однократную доставку:

```kotlin
class OrderViewModel(
    private val repository: OrderRepository
) : ViewModel() {

    // Состояние UI -- StateFlow (всегда актуальное значение)
    private val _state = MutableStateFlow(OrderUiState())
    val state: StateFlow<OrderUiState> = _state.asStateFlow()

    // One-time events -- Channel
    private val _events = Channel<OrderEvent>(Channel.BUFFERED)
    val events: Flow<OrderEvent> = _events.receiveAsFlow()

    fun submitOrder(order: Order) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                repository.submitOrder(order)
                _state.update { it.copy(isLoading = false) }
                _events.send(OrderEvent.NavigateToConfirmation(order.id))
            } catch (e: Exception) {
                _state.update { it.copy(isLoading = false) }
                _events.send(OrderEvent.ShowError(e.message ?: "Unknown error"))
            }
        }
    }
}

sealed interface OrderEvent {
    data class NavigateToConfirmation(val orderId: String) : OrderEvent
    data class ShowError(val message: String) : OrderEvent
    data object ShowSuccessToast : OrderEvent
}
```

### receiveAsFlow() vs consumeAsFlow()

```kotlin
// receiveAsFlow() -- рекомендуется
// Создаёт Flow, который получает из канала
// Несколько collector'ов делят элементы (fan-out)
val events: Flow<Event> = channel.receiveAsFlow()

// consumeAsFlow() -- consume канал
// После завершения collection канал отменяется
// Только один collector!
val events: Flow<Event> = channel.consumeAsFlow()
```

### trySend() для не-suspend контекста

В обработчиках кликов, callbacks и других не-suspend функциях используйте `trySend()`:

```kotlin
class SearchViewModel : ViewModel() {

    private val _events = Channel<SearchEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    // Вызывается из onClick -- не suspend контекст
    fun onSearchClicked(query: String) {
        if (query.isBlank()) {
            // trySend не suspend, возвращает ChannelResult
            _events.trySend(SearchEvent.ShowValidationError)
            return
        }
        viewModelScope.launch {
            // Внутри корутины можно использовать send()
            performSearch(query)
        }
    }
}
```

### Сбор событий в Fragment/Activity

```kotlin
// В Fragment (с Lifecycle-aware collection)
class OrderFragment : Fragment() {

    private val viewModel: OrderViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Состояние UI
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state ->
                    updateUI(state)
                }
            }
        }

        // One-time events
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.events.collect { event ->
                    when (event) {
                        is OrderEvent.NavigateToConfirmation ->
                            findNavController().navigate(/* ... */)
                        is OrderEvent.ShowError ->
                            Snackbar.make(view, event.message, LENGTH_SHORT).show()
                        is OrderEvent.ShowSuccessToast ->
                            Toast.makeText(context, "Success!", LENGTH_SHORT).show()
                    }
                }
            }
        }
    }
}
```

### Сбор событий в Compose

```kotlin
@Composable
fun OrderScreen(
    viewModel: OrderViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }
    val context = LocalContext.current

    // One-time events через LaunchedEffect
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is OrderEvent.ShowError ->
                    snackbarHostState.showSnackbar(event.message)
                is OrderEvent.ShowSuccessToast ->
                    Toast.makeText(context, "Success!", Toast.LENGTH_SHORT).show()
                is OrderEvent.NavigateToConfirmation -> { /* навигация */ }
            }
        }
    }

    // UI на основе state
    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
        OrderContent(state = state, onSubmit = viewModel::submitOrder)
    }
}
```

### Тестирование Channel-based ViewModel

Тестирование каналов требует внимания к timing и lifecycle:

```kotlin
@Test
fun `submitOrder sends navigation event`() = runTest {
    val repository = FakeOrderRepository()
    val viewModel = OrderViewModel(repository)

    // Запускаем сбор событий в фоне
    val events = mutableListOf<OrderEvent>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.events.collect { events.add(it) }
    }

    viewModel.submitOrder(testOrder)
    advanceUntilIdle()

    // Проверяем
    assertThat(events).hasSize(1)
    assertThat(events[0]).isInstanceOf(OrderEvent.NavigateToConfirmation::class.java)

    job.cancel() // Обязательно отменяем collector
}

// С Turbine (рекомендуется):
@Test
fun `submitOrder sends navigation event with Turbine`() = runTest {
    val viewModel = OrderViewModel(FakeOrderRepository())

    viewModel.events.test {
        viewModel.submitOrder(testOrder)
        val event = awaitItem()
        assertThat(event).isInstanceOf(OrderEvent.NavigateToConfirmation::class.java)
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Channel vs SharedFlow для событий в Android

| Аспект | Channel + receiveAsFlow() | SharedFlow(replay=0) |
|--------|---------------------------|----------------------|
| Гарантия доставки | Да -- элемент ждёт потребителя | Нет -- если нет подписчика, событие теряется |
| Множество подписчиков | Элемент получит только один | Все подписчики получат |
| Configuration change | Элемент сохраняется в буфере | Теряется если нет подписчика |
| Рекомендация | One-time events (навигация, toast) | Broadcast events (logging, analytics) |

### Архитектурное правило для Android

Чёткая схема выбора между инструментами:

```
UI State (текущее состояние экрана):
└── StateFlow (MutableStateFlow + asStateFlow())
    └── Collect: collectAsStateWithLifecycle() / repeatOnLifecycle

One-time Events (навигация, Snackbar, Toast):
└── Channel(BUFFERED) + receiveAsFlow()
    └── Collect: repeatOnLifecycle / LaunchedEffect

Broadcast Events (аналитика, logging):
└── SharedFlow(replay=0, extraBufferCapacity=1, DROP_OLDEST)
    └── Collect: repeatOnLifecycle
```

---

## Практические паттерны

### Producer-Consumer

Базовый паттерн: один производитель, один потребитель с буферизацией:

```kotlin
fun CoroutineScope.imageProcessor() {
    val downloadChannel = Channel<ImageUrl>(capacity = 10)

    // Producer: загружает URL из API
    launch {
        apiService.getImageUrls().forEach { url ->
            downloadChannel.send(url)
        }
        downloadChannel.close()
    }

    // Consumer: обрабатывает изображения
    launch {
        for (url in downloadChannel) {
            val image = downloadImage(url)
            saveToGallery(image)
        }
    }
}
```

### Worker Pool (fan-out)

Распределение задач по пулу воркеров -- один из самых полезных паттернов:

```kotlin
suspend fun <T, R> workerPool(
    items: List<T>,
    workerCount: Int,
    process: suspend (T) -> R
): List<R> = coroutineScope {
    val inputChannel = Channel<T>(Channel.BUFFERED)
    val outputChannel = Channel<R>(Channel.BUFFERED)

    // Заполняем входной канал
    launch {
        items.forEach { inputChannel.send(it) }
        inputChannel.close()
    }

    // Запускаем N воркеров
    val workers = List(workerCount) {
        launch {
            for (item in inputChannel) {
                val result = process(item)
                outputChannel.send(result)
            }
        }
    }

    // Собираем результаты
    launch {
        workers.forEach { it.join() } // Ждём завершения всех воркеров
        outputChannel.close()
    }

    buildList {
        for (result in outputChannel) {
            add(result)
        }
    }
}

// Использование
val results = workerPool(
    items = urls,
    workerCount = 5,
    process = { url -> httpClient.get(url) }
)
```

### Aggregator (fan-in)

Сбор данных из нескольких источников:

```kotlin
data class SearchResult(val source: String, val items: List<String>)

fun CoroutineScope.aggregateSearch(
    query: String
): ReceiveChannel<SearchResult> = produce {
    // Каждый источник отправляет результаты в один канал
    launch {
        val items = googleSearch(query)
        send(SearchResult("Google", items))
    }
    launch {
        val items = bingSearch(query)
        send(SearchResult("Bing", items))
    }
    launch {
        val items = duckDuckGoSearch(query)
        send(SearchResult("DuckDuckGo", items))
    }
}

// Использование: получаем результаты по мере готовности
val results = aggregateSearch("Kotlin channels")
repeat(3) {
    val result = results.receive()
    println("${result.source}: ${result.items.size} results")
}
```

### Rate Limiter с Channel

Использование Channel для ограничения скорости выполнения операций:

```kotlin
class RateLimiter(
    private val permits: Int,
    private val periodMs: Long,
    scope: CoroutineScope
) {
    private val ticketChannel = Channel<Unit>(permits)

    init {
        // Периодически пополняем "пул разрешений"
        scope.launch {
            while (true) {
                repeat(permits) {
                    ticketChannel.trySend(Unit)
                }
                delay(periodMs)
            }
        }
    }

    // Ожидаем разрешение перед выполнением операции
    suspend fun <T> execute(block: suspend () -> T): T {
        ticketChannel.receive() // suspend пока нет свободных разрешений
        return block()
    }
}

// Использование: не более 10 запросов в секунду
val rateLimiter = RateLimiter(permits = 10, periodMs = 1000, scope = this)

repeat(100) { i ->
    launch {
        rateLimiter.execute {
            apiCall(i) // Выполнится с ограничением 10 RPS
        }
    }
}
```

### Ticker: периодическая генерация событий

```kotlin
// Простой ticker через produce
fun CoroutineScope.ticker(
    intervalMs: Long,
    initialDelayMs: Long = 0
): ReceiveChannel<Unit> = produce {
    delay(initialDelayMs)
    while (true) {
        send(Unit)
        delay(intervalMs)
    }
}

// Использование: polling
fun main() = runBlocking {
    val tick = ticker(intervalMs = 1000)

    repeat(5) {
        tick.receive() // Ожидаем следующий тик
        println("Tick at ${System.currentTimeMillis()}")
        // Выполняем периодическую операцию
        checkForUpdates()
    }

    coroutineContext.cancelChildren()
}
```

### Semaphore через Channel: ограничение конкурентности

Канал можно использовать как семафор для ограничения количества одновременно выполняемых операций:

```kotlin
class ChannelSemaphore(permits: Int) {
    // Заполняем канал "разрешениями"
    private val semaphore = Channel<Unit>(permits).apply {
        repeat(permits) { trySend(Unit) }
    }

    suspend fun <T> withPermit(block: suspend () -> T): T {
        semaphore.receive() // Забираем разрешение (suspend если нет свободных)
        return try {
            block()
        } finally {
            semaphore.send(Unit) // Возвращаем разрешение
        }
    }
}

// Использование: не более 5 параллельных запросов к API
val limiter = ChannelSemaphore(5)

urls.map { url ->
    async {
        limiter.withPermit {
            httpClient.get(url) // Максимум 5 одновременно
        }
    }
}.awaitAll()
```

Примечание: в kotlinx.coroutines есть встроенный `Semaphore`, но этот пример демонстрирует гибкость Channel как строительного блока.

### Batch Processing: сбор элементов пачками

```kotlin
fun <T> CoroutineScope.batchChannel(
    source: ReceiveChannel<T>,
    batchSize: Int,
    timeoutMs: Long
): ReceiveChannel<List<T>> = produce {
    val batch = mutableListOf<T>()

    while (true) {
        // Ждём первый элемент без таймаута
        val first = source.receiveCatching()
        if (first.isClosed) {
            if (batch.isNotEmpty()) send(batch.toList())
            break
        }
        batch.add(first.getOrThrow())

        // Собираем остальные с таймаутом
        val deadline = System.currentTimeMillis() + timeoutMs
        while (batch.size < batchSize) {
            val remaining = deadline - System.currentTimeMillis()
            if (remaining <= 0) break

            val result = select {
                source.onReceiveCatching { it }
                onTimeout(remaining) { null }
            }
            if (result == null || result.isClosed) break
            batch.add(result.getOrThrow())
        }

        send(batch.toList())
        batch.clear()
    }
}

// Использование: отправляем в API пачками по 100 или каждую секунду
val events = Channel<AnalyticsEvent>(Channel.UNLIMITED)
val batches = batchChannel(events, batchSize = 100, timeoutMs = 1000)

launch {
    for (batch in batches) {
        analyticsApi.sendBatch(batch) // Отправляем пачкой
    }
}
```

---

## Распространённые ошибки

### 1. Забыли close()

```kotlin
// BUG: Канал никогда не закрывается, for зависнет навечно
fun CoroutineScope.buggyProducer(): ReceiveChannel<Int> {
    val channel = Channel<Int>()
    launch {
        for (i in 1..5) channel.send(i)
        // Забыли channel.close()!
    }
    return channel
}

// FIX: Используйте produce {} -- close() автоматически
fun CoroutineScope.correctProducer(): ReceiveChannel<Int> = produce {
    for (i in 1..5) send(i)
    // close() вызовется автоматически
}
```

### 2. Fan-out с consumeEach

```kotlin
// BUG: consumeEach отменит канал при исключении в одном воркере
val channel = produce { /* ... */ }
repeat(5) {
    launch {
        channel.consumeEach { process(it) } // ОПАСНО для fan-out!
    }
}

// FIX: Используйте for loop
repeat(5) {
    launch {
        for (item in channel) { // Безопасно для fan-out
            process(item)
        }
    }
}
```

### 3. Утечка Channel (producing coroutine не отменена)

```kotlin
// BUG: Бесконечный produce без отмены
fun startProducing(scope: CoroutineScope): ReceiveChannel<Int> {
    return scope.produce {
        var i = 0
        while (true) {
            send(i++)
            delay(100)
        }
    }
}

// Если consumer прекратил чтение, но не отменил scope --
// producer продолжит работать вечно!

// FIX: Привяжите к правильному scope или отменяйте явно
val channel = startProducing(viewModelScope)
// viewModelScope отменится при onCleared()
```

### 4. Unlimited Channel без контроля

```kotlin
// BUG: OOM при быстром producer и медленном consumer
val channel = Channel<ByteArray>(Channel.UNLIMITED)

launch {
    while (true) {
        channel.send(ByteArray(1_000_000)) // 1MB каждый раз
        // Никогда не suspend -- UNLIMITED!
    }
}

launch {
    for (data in channel) {
        slowProcess(data) // Медленная обработка
        // Тем временем в буфере копятся гигабайты...
    }
}

// FIX: Используйте Buffered с разумным capacity
val channel = Channel<ByteArray>(capacity = 10) // Макс 10MB в буфере
```

### 5. Channel вместо Flow

```kotlin
// АНТИПАТТЕРН: Channel для data stream в UI
class UserViewModel : ViewModel() {
    // Плохо: Channel не реплеит состояние новому подписчику
    private val _users = Channel<List<User>>()
    val users = _users.receiveAsFlow()
    // При ротации экрана новый Fragment не получит текущий список!

    // Правильно: StateFlow для состояния UI
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
    // Новый подписчик сразу получает текущее значение
}
```

### 6. send() из non-suspend контекста

```kotlin
// BUG: send() -- suspend функция, нельзя вызвать из onClick
button.setOnClickListener {
    channel.send(ClickEvent) // Ошибка компиляции!
}

// FIX 1: trySend() для non-suspend контекста
button.setOnClickListener {
    channel.trySend(ClickEvent) // OK, не suspend
}

// FIX 2: launch в scope
button.setOnClickListener {
    viewLifecycleOwner.lifecycleScope.launch {
        channel.send(ClickEvent)
    }
}
```

### 7. Потеря событий при конфигурационных изменениях

```kotlin
// BUG: SharedFlow(replay=0) теряет события при ротации экрана
class MyViewModel : ViewModel() {
    private val _events = MutableSharedFlow<UiEvent>() // replay=0
    // Между onStop и onStart события теряются!

    // FIX: Channel с буфером сохраняет события
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()
    // Элемент остаётся в буфере, пока Fragment не соберёт его
}
```

### 8. Блокировка в onUndeliveredElement

```kotlin
// BUG: Тяжёлая операция в onUndeliveredElement
val channel = Channel<Resource>(
    onUndeliveredElement = { resource ->
        // ПЛОХО: блокирующий вызов в onUndeliveredElement
        resource.saveToDatabase() // Может заблокировать dispatcher!
        resource.close()
    }
)

// FIX: onUndeliveredElement должен быть быстрым и неблокирующим
val channel = Channel<Resource>(
    onUndeliveredElement = { resource ->
        resource.close() // Только быстрая очистка
        // Логирование через неблокирующий logger
        logger.warn("Resource undelivered: ${resource.id}")
    }
)
```

### 9. Использование Channel.RENDEZVOUS с trySend

```kotlin
// BUG: trySend на Rendezvous-канале всегда возвращает failure
val channel = Channel<Int>() // Rendezvous, capacity = 0

channel.trySend(42) // ВСЕГДА failure: нет буфера, некуда положить!

// FIX: Используйте буферизованный канал для trySend
val channel = Channel<Int>(Channel.BUFFERED) // capacity = 64
channel.trySend(42) // Успешно, если буфер не полон
```

### Сводная таблица ошибок

| Ошибка | Симптом | Решение |
|--------|---------|---------|
| Забыли close() | Consumer зависает на receive/for | Используйте produce{} |
| consumeEach в fan-out | Ошибка одного воркера убивает канал | Используйте for-loop |
| Утечка producer'а | Корутина работает вечно в background | Привяжите к lifecycle scope |
| Unlimited без контроля | OOM при быстром producer | Используйте Buffered с разумным capacity |
| Channel вместо StateFlow | Потеря состояния при ротации экрана | StateFlow для состояния, Channel для событий |
| send() из non-suspend | Ошибка компиляции | trySend() или launch { send() } |
| SharedFlow(replay=0) для events | Потеря событий между onStop/onStart | Channel(BUFFERED) + receiveAsFlow() |
| trySend на Rendezvous | Всегда failure | Используйте канал с буфером |

---

## CS-фундамент

| Концепция | Описание | Связь с Kotlin Channels |
|-----------|----------|-------------------------|
| **CSP (Hoare, 1978)** | Communicating Sequential Processes -- формальный язык для описания параллельных систем. Процессы синхронизируются через каналы | Kotlin Channels -- прямая реализация CSP. send/receive -- точки синхронизации |
| **Actor Model (Hewitt, 1973)** | Параллельные вычисления через акторов с mailbox'ами. Асинхронная отправка сообщений | Deprecated actor builder. Современная альтернатива: sealed class + Channel |
| **Go channels** | Goroutine'ы общаются через каналы. Те же идеи CSP, но с синтаксисом `ch <- value` | Kotlin Channels -- аналог. produce{} похож на go func с defer close |
| **Message Passing** | Взаимодействие процессов через передачу сообщений (вместо shared memory) | Вся философия Channel: share by communicating |
| **BlockingQueue (Java)** | java.util.concurrent очередь с блокирующими put/take | Channel -- suspend-аналог BlockingQueue. send = put, receive = take |
| **Producer-Consumer** | Классический паттерн: один поток производит, другой потребляет | produce{} + for-loop -- идиоматическая реализация |
| **FIFO ordering** | First In, First Out -- порядок обработки | Channel гарантирует FIFO: элементы получаются в порядке отправки |
| **Backpressure** | Механизм обратного давления при перегрузке потребителя | Buffered Channel: send() suspend'ится когда буфер полон -- естественный backpressure |

---

## Связь с другими темами

**[[kotlin-coroutines]]** -- Channel является частью библиотеки kotlinx.coroutines и строится непосредственно поверх корутин. send() и receive() -- suspend-функции, produce{} -- coroutine builder, select{} работает внутри корутин. Structured concurrency корутин определяет жизненный цикл каналов: когда scope отменяется, все каналы в нём закрываются. Изучение корутин -- обязательный пререквизит для понимания каналов. Без знания suspend-функций, CoroutineScope и structured concurrency невозможно корректно использовать Channel API.

**[[kotlin-flow]]** -- Flow и Channel дополняют друг друга. Flow -- абстракция для data streams (наблюдение за изменениями), Channel -- примитив коммуникации между корутинами. channelFlow{} и callbackFlow{} используют Channel внутри для создания горячих источников данных. receiveAsFlow() конвертирует Channel в Flow. В Android-архитектуре StateFlow используется для UI-состояния, а Channel -- для one-time events. Понимание обоих концепций необходимо для правильного архитектурного выбора.

**[[kotlin-coroutines-internals]]** -- Внутри Channel реализован через сложные lock-free алгоритмы. В kotlinx.coroutines 1.9+ используется новый алгоритм (issue #3621), обеспечивающий значительный прирост производительности. CAS-операции, segment-based arrays, continuation-based scheduling -- всё это внутренние детали реализации каналов. Понимание internals помогает при отладке сложных проблем конкурентности и выборе правильного типа канала.

**[[jvm-concurrent-collections]]** -- Channel в Kotlin можно рассматривать как suspend-аналог BlockingQueue из java.util.concurrent. BlockingQueue.put() блокирует поток, Channel.send() приостанавливает корутину. BlockingQueue.take() блокирует поток, Channel.receive() приостанавливает корутину. Это фундаментальное отличие: один поток JVM может обслуживать тысячи каналов через корутины, тогда как BlockingQueue требует по потоку на каждый блокирующий вызов. Для Kotlin-кода с корутинами всегда предпочитайте Channel вместо BlockingQueue.

**[[android-flow-guide]]** -- В Android-разработке Channel занимает конкретную нишу: one-time events в MVVM-архитектуре. Паттерн Channel<UiEvent> + receiveAsFlow() стал стандартом для навигации, показа Snackbar и других событий, которые должны быть обработаны ровно один раз. Это дополняет StateFlow (для UI-состояния) и SharedFlow (для broadcast-событий). Android-специфичные нюансы: trySend() из callback'ов, lifecycle-aware collection через repeatOnLifecycle, сохранение событий в буфере при конфигурационных изменениях.

---

## Источники и дальнейшее чтение

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive*. Ch.17-21 -- единственная книга с глубоким разбором Channel API, produce, select, actor и практических паттернов. Обязательна для серьёзного изучения.
- Hoare C.A.R. (1978). *Communicating Sequential Processes*. Communications of the ACM. -- Фундаментальная работа, заложившая теоретическую базу CSP. Описывает формальную модель, на которой построены Go channels и Kotlin Channels.
- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition*. -- Обновлённое издание от разработчиков JetBrains. Глава о корутинах покрывает channels и flow на уровне, необходимом для production-разработки.
- Kotlin Documentation: [Channels](https://kotlinlang.org/docs/channels.html) -- официальная документация с примерами produce, fan-out, fan-in и pipeline.
- Kotlin Documentation: [Select expression (experimental)](https://kotlinlang.org/docs/select-expression.html) -- документация по select: onReceive, onSend, onAwait с примерами.
- Elizarov R. (2019). *Structured Concurrency*. KotlinConf talk. -- Доклад автора Kotlin Coroutines о том, как structured concurrency влияет на дизайн Channel API и lifecycle каналов.
- Elizarov R. (2018). *Kotlin Coroutines in Practice*. KotlinConf talk. -- Практические паттерны использования корутин и каналов от создателя библиотеки.
- kotlinx.coroutines GitHub: [CHANGES.md](https://github.com/Kotlin/kotlinx.coroutines/blob/master/CHANGES.md) -- changelog библиотеки. Важно для отслеживания изменений в Channel API (новый алгоритм в 1.9, deprecation BroadcastChannel).
- kotlinx.coroutines GitHub: [Issue #3621 -- Fast and scalable channels algorithm](https://github.com/Kotlin/kotlinx.coroutines/issues/3621) -- описание нового алгоритма каналов, обеспечившего 10-25% ускорение.
- Patil S. (2023). [Exploring "select" expression of Kotlin coroutines](https://medium.com/@patilshreyas/exploring-select-expression-of-kotlin-coroutines-8b777e5a23da). -- Практическое руководство по select с примерами мультиплексирования.
- Anifantakis I. (2025). [Mastering Kotlin Coroutine Channels in Android](https://www.droidcon.com/2025/01/30/mastering-kotlin-coroutine-channels-in-android-from-basics-to-advanced-patterns/). -- Подробный разбор паттернов Channel в Android: от основ до advanced patterns.
- Kakkar K. (2025). [SharedFlow vs Channel in Kotlin Coroutines](https://kamaldeepkakkar.medium.com/sharedflow-vs-channel-in-kotlin-coroutines-when-to-use-which-in-android-c7c3bc8da90d). -- Сравнение SharedFlow и Channel для событий в Android MVVM.

---

## Проверь себя

> [!question]- В чём фундаментальное различие между Channel и Flow, и почему нельзя использовать Channel вместо StateFlow для UI-состояния?
> Channel -- горячий примитив коммуникации. Каждый элемент доставляется ровно одному потребителю (point-to-point). Элемент извлекается из канала при receive() и больше не доступен. StateFlow -- горячий поток с последним значением (replay=1). При подписке новый collector немедленно получает текущее значение. Если использовать Channel для UI-состояния, то: (1) при ротации экрана новый Fragment не получит текущее состояние; (2) при нескольких подписчиках только один получит каждый элемент; (3) нет оператора для получения текущего значения (в отличие от StateFlow.value). Channel подходит для one-time events (навигация, toast), а StateFlow -- для persistent state (данные на экране).

> [!question]- Почему при fan-out (несколько потребителей одного канала) нужно использовать for-loop, а не consumeEach?
> consumeEach отменяет (cancel) весь канал, если в lambda выбрасывается исключение. При fan-out это означает, что ошибка в одном воркере убьёт канал для всех остальных воркеров. for-loop такого эффекта не имеет -- при исключении в одном потребителе остальные продолжают работать. Дополнительно, consumeEach предназначен для единственного потребителя и вызывает channel.cancel() при завершении, что нежелательно при множественных потребителях. Правило: for-loop для fan-out, consumeEach только для single consumer.

> [!question]- Объясните, в чём разница между CSP (Hoare) и Actor Model (Hewitt) и какую модель реализуют Kotlin Channels?
> В CSP процессы анонимны и общаются через именованные каналы. Отправка и получение -- синхронные точки рандеву (оба участника ждут друг друга). В Actor Model акторы имеют идентичность (адрес) и получают сообщения через mailbox. Отправка асинхронна -- отправитель не ждёт, пока актор обработает сообщение. Kotlin Channels реализуют CSP: каналы именованы, процессы (корутины) анонимны, Rendezvous-канал обеспечивает синхронную передачу. Buffered Channel добавляет элемент асинхронности (как в Actor mailbox), но базовая модель -- CSP. Deprecated actor{} builder пытался реализовать Actor Model, но был признан неудачным.

> [!question]- Какой паттерн вы выберете для обработки 10000 URL с ограничением в 20 параллельных запросов: Channel-based worker pool или Flow с flatMapMerge? Обоснуйте.
> Оба подхода жизнеспособны. Channel-based worker pool: создаём Channel<String>(BUFFERED), заполняем URL'ами, запускаем 20 корутин, каждая читает из канала через for-loop. Преимущество: явный контроль конкурентности, каждый URL обрабатывается ровно одним воркером, легко добавить retry. Flow с flatMapMerge(concurrency=20): urls.asFlow().flatMapMerge(20) { url -> flow { emit(fetch(url)) } }. Преимущество: декларативный стиль, богатый набор операторов, backpressure из коробки. Worker pool лучше, когда нужна двусторонняя коммуникация (отправлять результаты обратно), сложная логика retry или динамическое изменение числа воркеров. Flow лучше для простой трансформации данных без complex state.

---

## Ключевые карточки

Q: Какие четыре типа Channel существуют в Kotlin и чем они отличаются?
A: Rendezvous (capacity=0): без буфера, send ждёт receive. Buffered (capacity=N): буфер на N элементов, send suspend при полном буфере. Unlimited (Channel.UNLIMITED): неограниченный буфер, send никогда не suspend (риск OOM). Conflated (Channel.CONFLATED): буфер на 1 элемент, новый send перезаписывает предыдущий.

Q: Чем produce{} лучше ручного создания Channel + launch?
A: produce{} автоматически закрывает канал при завершении блока (нормальном или с исключением). При ручном подходе легко забыть close(), что приведёт к зависанию потребителя на receive(). Также produce возвращает ReceiveChannel, что запрещает потребителю отправлять данные обратно -- правильная инкапсуляция.

Q: Что такое select{} в Kotlin и какие clause'ы он поддерживает?
A: select{} ожидает несколько suspend-операций и выполняет первую доступную. Clause'ы: onReceive/onReceiveCatching (получение из канала), onSend (отправка в канал), onAwait (ожидание Deferred), onTimeout (таймаут). select biased -- при одновременной доступности приоритет у первого clause по порядку объявления. API экспериментальный.

Q: Какой паттерн рекомендуется для one-time events в Android ViewModel?
A: Private Channel<UiEvent>(Channel.BUFFERED) + public Flow через receiveAsFlow(). Для отправки из suspend-контекста: send(). Из non-suspend (onClick): trySend(). Сбор: repeatOnLifecycle(STARTED) { events.collect {} } в Fragment или LaunchedEffect в Compose. Channel гарантирует: событие обработано ровно один раз, сохраняется в буфере при конфигурационных изменениях.

Q: Почему actor{} builder deprecated и какие альтернативы существуют?
A: actor{} помечен @ObsoleteCoroutinesApi из-за дефектов дизайна: нет proper supervision, нет типизированной actor system. Альтернатива 1: sealed class (для типов сообщений) + Channel + корутина с for-loop. Альтернатива 2: Mutex + encapsulated state (для простого shared state). Выбор: Channel-based actor для сложной логики с FIFO-гарантией, Mutex для простых операций.

Q: В чём разница между trySend() и send()?
A: send() -- suspend-функция: приостанавливает корутину если буфер полон, бросает ClosedSendChannelException если канал закрыт. trySend() -- обычная функция: возвращает ChannelResult немедленно, не приостанавливает, не бросает исключений. trySend() используется из non-suspend контекста (onClick, callbacks). Для Rendezvous-канала trySend() всегда вернёт failure (нет буфера).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[kotlin-flow]] | Flow -- основная абстракция для data streams, дополняет Channel |
| Углубление | [[kotlin-coroutines-internals]] | Внутренняя реализация Channel: lock-free алгоритмы, segment-based structure |
| Практика | [[android-flow-guide]] | Конкретные паттерны Channel + Flow в Android-приложениях |
| Связь | [[jvm-concurrent-collections]] | BlockingQueue -- предшественник Channel в Java-мире |
| Фундамент | [[kotlin-coroutines]] | Вернуться к основам: suspend, scope, structured concurrency |
| Навигация | [[kotlin-overview]] | Вернуться к обзору Kotlin-тем |

---

*Проверено: 2026-02-14 | Источники: Kotlin docs, kotlinx.coroutines changelog, Marcin Moskala "Kotlin Coroutines: Deep Dive", Roman Elizarov KotlinConf talks, droidcon 2025*
