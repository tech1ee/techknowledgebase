---
title: "Async модели: от callbacks до coroutines"
created: 2026-01-04
modified: 2026-02-13
type: overview
reading_time: 23
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/cs-foundations
  - type/overview
  - level/intermediate
related:
  - "[[processes-threads-fundamentals]]"
  - "[[synchronization-primitives]]"
  - "[[kotlin-coroutines]]"
---

# Async модели: от callbacks до coroutines

> **TL;DR:** Async программирование решает проблему ожидания без блокировки. Эволюция: callbacks (callback hell) → promises (chaining) → async/await (sync-like syntax). Event loop — ядро JS/Python: один поток с очередями задач. Coroutines — кооперативная многозадачность без overhead threads. Kotlin coroutines используют CPS-трансформацию и state machines, structured concurrency управляет lifecycle. Для KMP критично: coroutines — основа всего async кода.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Threads** | Понять разницу с coroutines | [[processes-threads-fundamentals]] |
| **Context Switch** | Понять overhead blocking | [[processes-threads-fundamentals]] |
| **First-class functions** | Callbacks — функции как аргументы | Базовое программирование |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Callback** | Функция, вызываемая после завершения | Звонок обратно |
| **Promise** | Объект-обещание будущего результата | Квитанция в очереди |
| **Future** | То же что Promise (другое название) | Талон на выдачу |
| **Async/Await** | Синтаксис для работы с promises | Ожидание без блокировки |
| **Event Loop** | Цикл обработки событий | Диспетчер задач |
| **Coroutine** | Функция с точками приостановки | Pausable function |
| **Suspending** | Приостановка без блокировки | Отложить, не бросить |

---

## ПОЧЕМУ появилось async программирование

### Проблема: ожидание убивает производительность

Представь однопоточную программу. Ты делаешь HTTP-запрос. Что происходит?

```
Запрос отправлен ──────────────────────────────> Ответ получен
                  [       500ms ожидания      ]
                  CPU простаивает. Thread заблокирован.
                  Ничего не происходит.
```

В браузере это означает: пользователь нажал кнопку — интерфейс замёрз на полсекунды. Анимации остановились. Скролл не работает.

### Решение 1: много threads

Можно создать thread для каждой операции. Thread 1 ждёт HTTP, Thread 2 обрабатывает UI. Но threads дорогие:
- ~1MB памяти на stack
- Контекстные переключения в kernel
- Синхронизация через mutex/locks
- Тысячи threads = проблемы

JavaScript вообще не имеет threads в классическом смысле. Один main thread для всего.

### Решение 2: не блокировать, а уведомлять

Вместо ожидания: "вызови эту функцию, когда будет ответ". Это и есть async модель.

```
Отправь запрос → (callback) когда ответ → обработай
    ↓
 Thread свободен
    ↓
 Делай другую работу
```

---

## История async моделей

### 1976: рождение Promise

Daniel Friedman и David Wise ввели термин "promise" для обозначения значения, которое будет доступно в будущем. Годом позже Henry Baker и Carl Hewitt предложили "future".

Идея: вместо блокировки получить "талон" (promise/future), по которому позже можно забрать результат.

### 1988: Barbara Liskov и promise pipelining

Liskov и Shrira развили концепцию: можно передавать promise дальше, не дожидаясь результата. Цепочка операций выстраивается заранее.

### 2009: Node.js и callback revolution

Node.js принёс async I/O в мейнстрим. Весь I/O — callbacks. Файловая система, HTTP, базы данных — всё async.

```javascript
fs.readFile('data.txt', function(err, data) {
    if (err) throw err;
    console.log(data);
});
console.log('Это выполнится РАНЬШЕ!');
```

### 2015-2017: ES6 Promises и async/await

JavaScript стандартизировал Promises (ES6) и async/await (ES2017). Код стал читаемым.

---

## Эволюция: от Callbacks к Async/Await

### Callbacks: начало

Callback — функция, передаваемая как аргумент и вызываемая позже.

```javascript
function fetchUser(id, callback) {
    setTimeout(() => {
        callback({ id: id, name: 'Arman' });
    }, 1000);
}

fetchUser(1, function(user) {
    console.log(user.name);  // Через 1 секунду: 'Arman'
});
```

Проблема в том, что callbacks вложенные:

```javascript
fetchUser(1, function(user) {
    fetchOrders(user.id, function(orders) {
        fetchProducts(orders[0].productId, function(product) {
            fetchReviews(product.id, function(reviews) {
                // ... и так далее
            });
        });
    });
});
```

### Callback Hell (Pyramid of Doom)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CALLBACK HELL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   fetchUser(id, (user) => {                                     │
│       fetchOrders(user, (orders) => {                           │
│           fetchProducts(orders, (products) => {                 │
│               fetchReviews(products, (reviews) => {             │
│                   // Добро пожаловать в ад!                     │
│               });                                               │
│           });                                                   │
│       });                                                       │
│   });                                                           │
│                                                                 │
│   Пирамида растёт вправо. Код нечитаем.                         │
│   Обработка ошибок в каждом callback.                           │
│   Отладка — кошмар.                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Promises: выход из ада

Promise — объект, представляющий результат async операции. Три состояния:
- **pending** — операция выполняется
- **fulfilled** — успешно завершена
- **rejected** — завершена с ошибкой

```javascript
function fetchUser(id) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve({ id: id, name: 'Arman' });
        }, 1000);
    });
}

fetchUser(1)
    .then(user => fetchOrders(user.id))
    .then(orders => fetchProducts(orders[0].productId))
    .then(product => fetchReviews(product.id))
    .then(reviews => console.log(reviews))
    .catch(error => console.error('Ошибка:', error));
```

Код стал плоским. Ошибки ловятся в одном месте.

### Async/Await: синхронный вид

Async/await — синтаксический сахар поверх Promises. Код выглядит синхронно, но работает асинхронно.

```javascript
async function getReviews(userId) {
    try {
        const user = await fetchUser(userId);
        const orders = await fetchOrders(user.id);
        const product = await fetchProducts(orders[0].productId);
        const reviews = await fetchReviews(product.id);
        return reviews;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
```

Читается как синхронный код. Отладка проще. try/catch работает как обычно.

---

## КАК работает Event Loop

### Зачем Event Loop

JavaScript однопоточный. Один Call Stack. Одна операция в момент времени.

Но async операции (HTTP, таймеры, DOM events) не блокируют. Как?

Event Loop координирует выполнение: что делать сейчас, что отложить, когда вернуться к отложенному.

### Компоненты Event Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT LOOP (JavaScript)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │  Call Stack  │  ← Выполняемый код                           │
│   └──────────────┘                                              │
│          ↑                                                      │
│   ┌──────┴───────────────────────────────────────────┐          │
│   │                   EVENT LOOP                      │          │
│   │                                                   │          │
│   │   1. Взять из Call Stack                         │          │
│   │   2. Проверить Microtask Queue                   │          │
│   │   3. Проверить Task Queue                        │          │
│   │   4. Повторить                                   │          │
│   └──────────────────────────────────────────────────┘          │
│          ↓                    ↓                                 │
│   ┌──────────────┐    ┌──────────────┐                          │
│   │ Microtask Q  │    │   Task Q     │                          │
│   │              │    │              │                          │
│   │ • Promise    │    │ • setTimeout │                          │
│   │ • async body │    │ • setInterval│                          │
│   │ • queueMicro │    │ • I/O events │                          │
│   └──────────────┘    └──────────────┘                          │
│                                                                 │
│   ВАЖНО: Microtasks выполняются ВСЕ                             │
│          перед следующей Task!                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Порядок выполнения

1. Call Stack выполняется до пустоты
2. Все microtasks выполняются (Promise.then, async continuations)
3. Одна task из Task Queue
4. Снова все microtasks
5. Повторить

```javascript
console.log('1');                    // Sync

setTimeout(() => console.log('2'), 0);  // Task Queue

Promise.resolve().then(() => console.log('3')); // Microtask

console.log('4');                    // Sync

// Вывод: 1, 4, 3, 2
// Sync сначала, потом Microtask, потом Task
```

### Node.js: расширенный Event Loop

Node.js добавляет фазы:
1. **Timers** — setTimeout, setInterval
2. **Pending callbacks** — отложенные I/O callbacks
3. **Idle, prepare** — внутреннее использование
4. **Poll** — получение новых I/O событий
5. **Check** — setImmediate callbacks
6. **Close** — close callbacks (socket.on('close'))

`process.nextTick()` выполняется между фазами, с наивысшим приоритетом.

---

## Coroutines: лёгкая конкурентность

### Что такое Coroutine

Coroutine — функция, которая может приостановить выполнение и возобновить его позже. В отличие от обычной функции, coroutine не теряет своё состояние при паузе.

```
┌─────────────────────────────────────────────────────────────────┐
│                 FUNCTION vs COROUTINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   FUNCTION:                                                     │
│   start ─────────────────────────────> finish                   │
│   (run to completion)                                           │
│                                                                 │
│   COROUTINE:                                                    │
│   start ───> pause ───> resume ───> pause ───> finish           │
│              (state    (state      (state                       │
│               saved)    restored)   saved)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Cooperative vs Preemptive

| Аспект | Coroutines | Threads |
|--------|------------|---------|
| Scheduling | Кооперативный | Вытесняющий |
| Кто решает | Сама coroutine | ОС (scheduler) |
| Переключение | yield/suspend | Timer interrupt |
| Race conditions | Редко | Часто |
| Overhead | Микросекунды | Миллисекунды |

Threads вытесняются принудительно — ОС прерывает в любой момент. Coroutines отдают управление сами — в известных точках (yield, await).

### Stackful vs Stackless Coroutines

**Stackful:** каждая coroutine имеет собственный stack. Можно приостановить на любой глубине вложенных вызовов.

**Stackless:** coroutines делят stack. Приостановка только на верхнем уровне. Меньше памяти, но ограничения.

Kotlin coroutines — stackless с state machine transformation.

---

## Kotlin Coroutines под капотом

### Suspending Functions

`suspend` — ключевое слово, меняющее природу функции. Suspend function может приостановиться без блокировки thread.

```kotlin
suspend fun fetchUser(id: String): User {
    delay(1000)  // suspend, не block!
    return User(id, "Arman")
}
```

### CPS Transformation

Компилятор Kotlin преобразует suspend функции в Continuation-Passing Style:

```kotlin
// Как пишем
suspend fun getUser(): User?

// Как компилируется (упрощённо)
fun getUser(continuation: Continuation<User?>): Any?
```

Return type `Any?` потому что функция может вернуть:
- Результат типа `User?` — если выполнилась
- `COROUTINE_SUSPENDED` — если приостановлена

### State Machine

Каждая suspend функция становится state machine с labels:

```kotlin
// Исходный код
suspend fun fetchData(): Data {
    val user = fetchUser()      // suspend point 1
    val orders = fetchOrders(user.id)  // suspend point 2
    return process(user, orders)
}

// Упрощённо компилируется в:
fun fetchData(cont: Continuation<Data>): Any? {
    when (cont.label) {
        0 -> {
            cont.label = 1
            val result = fetchUser(cont)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // продолжить
        }
        1 -> {
            cont.label = 2
            val user = cont.result as User
            val result = fetchOrders(user.id, cont)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // продолжить
        }
        2 -> {
            val orders = cont.result as List<Order>
            return process(user, orders)
        }
    }
}
```

### Continuation Object

Continuation хранит:
- **label** — текущее состояние
- **Local variables** — сохранённые локальные переменные
- **Caller continuation** — для возврата вверх по стеку

Когда coroutine приостанавливается, continuation сохраняется. Когда возобновляется — восстанавливается из continuation.

### Structured Concurrency

Kotlin enforces structured concurrency — coroutines образуют иерархию:

```kotlin
coroutineScope {
    val user = async { fetchUser() }     // child 1
    val orders = async { fetchOrders() } // child 2

    processData(user.await(), orders.await())
}
// Scope завершается только когда ВСЕ children завершены
```

Правила:
- Parent ждёт всех children
- Отмена parent → отмена всех children
- Ошибка в child → отмена siblings, propagation к parent
- CoroutineScope управляет lifecycle

---

## Модели передачи сообщений

### CSP: Communicating Sequential Processes

CSP (Tony Hoare, 1978) — процессы общаются через каналы. Go использует этот подход.

```
┌──────────┐    channel    ┌──────────┐
│ Process1 │ ────────────> │ Process2 │
└──────────┘   (blocking)  └──────────┘
              send/receive
```

Особенности:
- Синхронный: sender блокируется пока receiver не получит
- Анонимные процессы
- Каналы как первоклассные объекты
- "Share memory by communicating"

```go
// Go channels
ch := make(chan int)
go func() { ch <- 42 }()  // send
value := <-ch              // receive (blocks until ready)
```

### Actor Model

Actor Model (Carl Hewitt, 1973) — акторы с mailboxes. Erlang, Akka используют этот подход.

```
┌──────────┐    message    ┌──────────┐
│  Actor1  │ ────────────> │ Mailbox  │ → Actor2
└──────────┘  (async)      └──────────┘
              non-blocking
```

Особенности:
- Асинхронный: sender не блокируется
- Именованные акторы с identity
- Mailbox буферизует сообщения
- Location transparency (можно распределять)

### CSP vs Actor

| Аспект | CSP | Actor Model |
|--------|-----|-------------|
| Передача | Синхронная | Асинхронная |
| Буфер | Нет (или явный) | Mailbox (неограниченный) |
| Identity | Анонимные | Именованные |
| Языки | Go, Clojure | Erlang, Akka |

---

## Reactive Streams vs Async/Await

### Когда что использовать

**Async/Await:**
- Одноразовые операции (HTTP запрос)
- Простая последовательность операций
- Когда нужен императивный стиль

**Reactive (RxJS, Kotlin Flow):**
- Потоки событий (UI events, WebSocket)
- Множественные значения во времени
- Сложные трансформации (debounce, throttle, combine)

### Kotlin Flow

Flow — это cold reactive stream, интегрированный с coroutines:

```kotlin
// Suspend function — одно значение
suspend fun fetchUser(): User

// Flow — поток значений
fun observePrices(): Flow<Price> = flow {
    while (true) {
        emit(getPrice())
        delay(1000)
    }
}

// Сбор Flow
observePrices()
    .filter { it.value > 100 }
    .map { it.currency }
    .collect { println(it) }
```

Flow vs RxJava:
- Flow — часть coroutines, нативный Kotlin
- Backpressure через suspension
- Structured concurrency
- Меньше операторов, но покрывает 90% случаев

---

## Подводные камни

### 1. Забытый await

```kotlin
// ПЛОХО: запускает, но не ждёт результат
suspend fun bad() {
    fetchUser()  // возвращает сразу!
}

// ХОРОШО
suspend fun good() {
    val user = fetchUser()  // ждёт результат
}
```

### 2. Блокирующий вызов в async контексте

```kotlin
// ПЛОХО: блокирует dispatcher thread
launch {
    Thread.sleep(1000)  // НИКОГДА так!
}

// ХОРОШО: suspend, не block
launch {
    delay(1000)  // отпускает thread
}
```

### 3. Последовательное ожидание независимых операций

```kotlin
// ПЛОХО: 2 секунды (последовательно)
suspend fun bad(): Pair<User, Orders> {
    val user = fetchUser()      // 1 сек
    val orders = fetchOrders()  // 1 сек
    return user to orders
}

// ХОРОШО: 1 секунда (параллельно)
suspend fun good(): Pair<User, Orders> = coroutineScope {
    val user = async { fetchUser() }
    val orders = async { fetchOrders() }
    user.await() to orders.await()
}
```

### 4. Потеря контекста ошибок

```javascript
// ПЛОХО: глотает ошибку
async function bad() {
    fetchUser();  // без await — ошибка потеряна
}

// ХОРОШО
async function good() {
    try {
        await fetchUser();
    } catch (e) {
        console.error(e);
    }
}
```

### Мифы и заблуждения

**Миф:** Async делает код быстрее.
**Реальность:** Async делает код отзывчивее, не быстрее. CPU-bound работа не ускорится.

**Миф:** Coroutines = threads.
**Реальность:** Coroutines работают поверх threads, но не являются threads. Тысячи coroutines могут работать на одном thread.

**Миф:** Async/await решает все проблемы callbacks.
**Реальность:** Async/await не решает cancellation нативно. Это частая жалоба разработчиков.

---

## Куда дальше

**Для синхронизации:**
→ [[synchronization-primitives]] — mutex, channels, atomic

**Для понимания threads:**
→ [[processes-threads-fundamentals]] — context switch, thread pools

**Практика Kotlin:**
→ [[kotlin-coroutines]] — детальное руководство

---

## Связь с другими темами

### [[processes-threads-fundamentals]]
Async модели возникли как ответ на ограничения потоковой модели — дорогие context switches, высокое потребление памяти на stack, сложность синхронизации. Глубокое понимание того, как работают threads и процессы на уровне ОС, позволяет оценить, почему coroutines с их кооперативным scheduling настолько эффективнее. Знание thread pools и scheduling помогает понять, на чём в итоге выполняются coroutines.

### [[synchronization-primitives]]
Async модели не устраняют потребность в синхронизации — они меняют её форму. Вместо mutex и семафоров coroutines используют channels (CSP) и actors для безопасного обмена данными. Понимание классических примитивов синхронизации даёт фундамент для осознания того, почему structured concurrency в Kotlin и actor model в Swift предотвращают race conditions без явных lock'ов.

### [[kotlin-coroutines]]
Kotlin coroutines — это практическая реализация async моделей, описанных в этом файле. Знание CPS-трансформации, state machines и continuation на теоретическом уровне позволяет глубже понять, как Kotlin компилятор реализует suspend-функции. Это связывает абстрактные концепции (cooperative multitasking, structured concurrency) с конкретным инструментом, используемым ежедневно в KMP-разработке.

---

## Источники и дальнейшее чтение

- Hoare C.A.R. (1978). *Communicating Sequential Processes*. — оригинальная работа по CSP, заложившая основы channel-based конкурентности (Go, Kotlin channels)
- Hewitt C., Bishop P., Steiger R. (1973). *A Universal Modular Actor Formalism for Artificial Intelligence*. — оригинальная paper по Actor Model, реализованной в Erlang и Akka
- Marlin C. (1980). *Coroutines: A Programming Methodology, a Language Design and an Implementation*. — одна из первых систематизаций coroutines как парадигмы программирования
- [ui.dev: Async JavaScript Evolution](https://ui.dev/async-javascript-from-callbacks-to-promises-to-async-await) — история JS async
- [Kotlin Docs: Coroutines](https://kotlinlang.org/docs/coroutines-basics.html) — официальная документация
- [kt.academy: Coroutines Under the Hood](https://kt.academy/article/cc-under-the-hood) — внутреннее устройство

---

## Проверь себя

> [!question]- Почему callbacks приводят к "callback hell" и как Promises/async-await решают эту проблему?
> Callbacks создают вложенную структуру: каждая следующая операция — вложенный callback внутри предыдущего. При 5+ операциях код сдвигается вправо (пирамида), становится нечитаемым, обработка ошибок дублируется на каждом уровне. Promises решают через chaining (.then().then()) — плоская цепочка вместо вложенности. Async/await идёт дальше: код выглядит как синхронный (последовательный), но выполняется асинхронно. Kotlin suspend-функции — аналог async/await.

> [!question]- Как Kotlin coroutines реализованы "под капотом" — что делает компилятор с suspend-функциями?
> Компилятор применяет CPS-трансформацию (Continuation Passing Style): каждая suspend-функция получает дополнительный параметр Continuation. Тело функции превращается в state machine: каждая точка suspension — это состояние (label). При вызове suspend-функции state machine сохраняет текущее состояние и возвращает COROUTINE_SUSPENDED. При возобновлении — восстанавливает состояние и переходит к следующему label. Нет блокировки потока.

> [!question]- Почему structured concurrency лучше чем запуск "голых" coroutines, и как это связано с lifecycle Android-компонентов?
> Structured concurrency через CoroutineScope гарантирует: (1) Дочерние корутины не переживут родительский scope. (2) При отмене scope все дочерние корутины автоматически отменяются. (3) Исключение в дочерней корутине пробрасывается в родительскую. Для Android: viewModelScope привязан к lifecycle ViewModel — при clearing ViewModel все корутины отменяются. Без structured concurrency: утечки памяти, crashes при обращении к уничтоженному Activity.

---

## Ключевые карточки

Какова эволюция async-моделей программирования?
?
Callbacks (callback hell, error handling на каждом уровне) -> Promises/Futures (chaining через .then(), единая обработка ошибок) -> async/await (код выглядит синхронным, suspend/resume) -> Structured Concurrency (lifecycle management, отмена, иерархия). Kotlin coroutines реализуют async/await + structured concurrency.

---

Что такое event loop и как он работает?
?
Event loop — бесконечный цикл на одном потоке: 1) Проверить очередь задач (task queue), 2) Взять задачу и выполнить до конца (run-to-completion), 3) Проверить microtask queue, 4) Повторить. Используется в Node.js, браузерах, Python asyncio. Блокирующая операция в event loop замораживает весь UI/сервер — поэтому I/O делегируется OS через неблокирующие вызовы.

---

Что такое CPS-трансформация в Kotlin coroutines?
?
CPS (Continuation Passing Style) — компилятор добавляет к suspend-функции параметр Continuation (callback для результата). Тело функции превращается в state machine с label'ами для каждой точки suspension. При suspend — сохраняет состояние в Continuation, возвращает COROUTINE_SUSPENDED. При resume — восстанавливает состояние и продолжает с нужного label.

---

Чем Dispatchers.Main, Default и IO отличаются?
?
Dispatchers.Main — главный поток (UI), для обновления интерфейса. Dispatchers.Default — пул из N потоков (N = число ядер), для CPU-intensive задач. Dispatchers.IO — расширенный пул (до 64 потоков), для блокирующих I/O операций. Dispatchers.Unconfined — выполняется в текущем потоке до первого suspension, затем в потоке, который возобновил.

---

Что такое structured concurrency и какие гарантии даёт?
?
Structured concurrency — подход, где корутины организованы в иерархию через CoroutineScope. Гарантии: (1) Родитель не завершится, пока не завершатся все дети. (2) Отмена родителя отменяет всех детей. (3) Исключение ребёнка пробрасывается родителю. (4) Нет "orphan" корутин. В Kotlin: coroutineScope {}, viewModelScope, lifecycleScope.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kotlin-coroutines]] | Глубокое погружение в Kotlin coroutines на практике |
| Углубиться | [[synchronization-primitives]] | Понять низкоуровневые механизмы синхронизации |
| Смежная тема | [[processes-threads-fundamentals]] | Вернуться к основам потоков, на которых строятся async-модели |
| Обзор | [[cs-foundations-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-02-13*
