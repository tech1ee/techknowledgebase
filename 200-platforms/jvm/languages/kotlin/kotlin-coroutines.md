---
title: "Kotlin Coroutines: Асинхронное программирование"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - coroutines
  - async
  - concurrency
  - structured-concurrency
  - flow
  - type/concept
  - level/intermediate
reading_time: 29
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[kotlin-basics]]"
  - "[[kotlin-functional]]"
  - "[[jvm-concurrency-overview]]"
related:
  - "[[kotlin-flow]]"
  - "[[kotlin-functional]]"
  - "[[jvm-concurrency-overview]]"
  - "[[kotlin-testing]]"
status: published
---

# Kotlin Coroutines: асинхронность без callback hell

> Полное руководство по корутинам: suspend функции, CoroutineScope, Dispatchers, structured concurrency, обработка ошибок.

---

## Зачем это нужно

### Проблема: Асинхронность = Ад коллбеков

| Проблема | Последствия |
|----------|-------------|
| **Callback Hell** | Вложенность 5+ уровней, нечитаемый код |
| **Thread на каждый запрос** | 1000 запросов = 1GB RAM, OOM |
| **ANR на Main Thread** | Network/IO на Main = приложение зависает |
| **Утечки памяти** | Callbacks держат ссылки на Activity |

### Что решают корутины

```
Callbacks:                         Coroutines:
┌──────────────────────┐           ┌──────────────────────┐
│ fetchUser { user ->  │           │ val user = fetchUser()│
│   fetchPosts { posts │           │ val posts = fetchPosts()
│     fetchComments {  │           │ val comments = fetchComments()
│       // 5+ levels   │           │ // Flat, readable     │
│     }                │           │                      │
│   }                  │           │                      │
│ }                    │           │                      │
└──────────────────────┘           └──────────────────────┘
```

### Ключевые преимущества

| Аспект | Threads | Coroutines |
|--------|---------|------------|
| **Память** | 1 MB/thread | ~несколько KB/coroutine |
| **Создание** | Миллисекунды | Микросекунды |
| **100K одновременно** | ~100 GB RAM | ~несколько MB |
| **Отмена** | Сложно, флаги | Встроенная, structured |
| **Код** | Callbacks/RxJava | Последовательный, как синхронный |

### Кому это нужно

- **Android разработчики** — сетевые запросы, база данных, UI
- **Backend (Ktor)** — высоконагруженные API
- **Multiplatform** — единый async код для iOS/Android/Web

### Актуальность 2024-2025

| Фича | Статус | Что нового |
|------|--------|------------|
| **kotlinx.coroutines 1.9+** | ✅ Stable | Virtual Threads interop (Dispatchers.IO на Loom) |
| **Dispatchers.IO.limitedParallelism** | ✅ Stable | Ограничение параллелизма без создания пула |
| **Flow.shareIn/stateIn** | ✅ Stable | Cold→Hot конвертация, интеграция с Compose |
| **runTest** | ✅ Stable | kotlinx-coroutines-test для детерминированных тестов |
| **Virtual Threads (Java 21)** | ⚠️ Experimental | `Dispatchers.IO` автоматически использует Loom если доступен |
| **TestScope.backgroundScope** | ✅ 1.7+ | Корутины, не блокирующие завершение теста |

**Тренды 2025:**
- Virtual Threads (Project Loom) + Coroutines интеграция
- Structured concurrency как стандарт в JEP 453
- Flow вытесняет RxJava в Android-проектах
- `runTest` + Turbine — стандарт для тестирования Flow

---

## TL;DR

Coroutines — механизм асинхронного программирования, где код выглядит синхронным, но не блокирует потоки. Thread стоит 1MB стека и миллисекунды на создание; корутина — объект в heap (килобайты, микросекунды). Миллион корутин на одном реальном потоке — норма.

Suspend функции приостанавливаются без блокировки потока. CoroutineScope управляет жизненным циклом: отмена scope отменяет все дочерние корутины (structured concurrency). Dispatchers.IO для сети и файлов, Dispatchers.Default для CPU-задач, Dispatchers.Main для UI. В Android viewModelScope автоматически отменяется при onCleared().

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin basics | Lambdas, higher-order functions | [[kotlin-basics]], [[kotlin-functional]] |
| Многопоточность JVM | Понимать threads, blocking, context switch | [[jvm-concurrency-overview]] |
| Основы async programming | Callbacks, Promises/Futures | Любой async tutorial |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Корутина** | Легковесный "поток" — объект в heap (~сотни байт), не OS thread | Задача в списке дел — переключаешься между ними без найма нового сотрудника |
| **suspend** | Функция, которая может приостановиться без блокировки потока | Официант, который ставит заказ и идёт к другому столику пока готовится |
| **Continuation** | Объект, хранящий состояние приостановленной корутины | Закладка в книге — помнит где остановился |
| **CoroutineScope** | Область жизни корутин — управляет отменой | Менеджер проекта — закрывает проект, все задачи отменяются |
| **Dispatcher** | Определяет на каком потоке выполняется корутина | Диспетчер такси — направляет машины на заказы |
| **Job** | Представление жизненного цикла корутины | Контракт на работу — активен, выполнен или расторгнут |
| **SupervisorJob** | Job, где failure дочерней корутины не отменяет siblings | Директор школы — если один ученик заболел, остальные продолжают учиться |
| **Deferred\<T\>** | Job с результатом, получается через await() | Квитанция на химчистку — позже заберёшь результат |
| **Structured Concurrency** | Корутины образуют иерархию: parent ждёт children | Семья в поездке — родители не уедут без детей |
| **Channel** | Передача данных между корутинами | Конвейерная лента — один кладёт, другой забирает |
| **Flow** | Cold асинхронный поток данных | Подписка на YouTube — видео приходят когда подписался |
| **viewModelScope** | Android CoroutineScope в ViewModel | Охранник офиса — уходит когда офис закрывается |

---

## Основы Coroutines

### Что такое корутина?

Сравним обычную функцию, которая блокирует поток, с suspend-функцией, которая освобождает его:

```kotlin
// Обычная функция блокирует поток
fun fetchData(): String {
    Thread.sleep(1000)  // Блокирует поток!
    return "Data"
}

// suspend функция может приостановиться без блокировки
suspend fun fetchDataSuspend(): String {
    delay(1000)  // Приостанавливает корутину, НЕ блокирует поток!
    return "Data"
}
```

Вызов suspend-функции возможен только из корутины или другой suspend-функции. `runBlocking` создаёт корутину и блокирует текущий поток до её завершения:

```kotlin
fun main() = runBlocking {
    println("Start")
    val data = fetchDataSuspend()  // Вызов suspend функции
    println("Data: $data")
    println("End")
}
```

**Почему корутины легковесные?**

**Не создают OS потоки.** Каждый thread в JVM занимает ~1MB памяти под стек (минимум 64KB). Корутина — это объект в heap размером в несколько десятков байт. Бенчмарки показывают соотношение ~6:1 по памяти между thread и coroutine. При 100,000 потоках нужно ~100GB RAM только под стеки. При 100,000 корутинах — мегабайты.

**Переключение корутин дешевле.** Context switch между OS-потоками требует сохранения регистров, переключения стека, инвалидации кэшей CPU — это тысячи тактов процессора. Переключение корутины — просто вызов функции: сохранить состояние в объект, вызвать следующую корутину. Это в десятки раз быстрее.

**Корутины делят потоки.** 100,000 корутин на `Dispatchers.Default` реально выполняются на нескольких потоках (по количеству CPU ядер). Корутины кооперативно передают управление в точках suspension. Один поток может обслуживать тысячи корутин последовательно.

### suspend функции

Ключевое слово `suspend` маркирует функцию как способную приостановиться. Вызвать её можно только из другой suspend-функции или из корутины:

```kotlin
suspend fun doWork(): Int {
    delay(1000)  // Приостановка на 1 секунду
    return 42
}

suspend fun caller() {
    val result = doWork()  // OK из suspend функции
}

fun regularFunction() {
    // val result = doWork()  // Ошибка компиляции!
    GlobalScope.launch {
        val result = doWork()  // OK внутри корутины
    }
}
```

Suspend-модификатор применим и к extension-функциям. Внутри suspend-функции можно вызывать другие suspend-функции свободно:

```kotlin
suspend fun fetchUser(id: String): User {
    val data = apiCall(id)  // suspend вызов
    delay(100)
    return parseUser(data)
}

suspend fun String.fetchFromNetwork(): ByteArray {
    delay(500)
    return this.toByteArray()
}
```

**Почему suspend в сигнатуре?**

**Явная маркировка асинхронности.** В отличие от JavaScript (где любая функция может быть async), Kotlin требует явного `suspend`. Глядя на сигнатуру `suspend fun fetchUser()`, вы сразу понимаете: эта функция может приостановиться, её нельзя вызвать из обычного синхронного кода.

**Защита на уровне компиляции.** Попытка вызвать suspend-функцию из обычной функции — ошибка компиляции. Это предотвращает случайное блокирование потоков и заставляет явно думать о контексте выполнения.

**Генерация state machine.** Компилятор трансформирует suspend-функцию в state machine (конечный автомат). Каждая точка приостановки — это состояние. При suspension текущее состояние сохраняется, при resumption — восстанавливается. Это позволяет "запомнить" место приостановки без сохранения всего стека вызовов.

### Как корутины работают внутри: CPS и Continuation

Kotlin использует **CPS (Continuation Passing Style)** трансформацию. Компилятор превращает suspend-функцию в обычную функцию с дополнительным параметром `Continuation`.

```kotlin
// Что вы пишете:
suspend fun fetchUser(id: String): User {
    val data = apiCall(id)    // suspension point 1
    delay(100)                 // suspension point 2
    return parseUser(data)
}

// Что генерирует компилятор (упрощённо):
fun fetchUser(id: String, cont: Continuation<User>): Any? {
    val sm = cont as? FetchUserSM ?: FetchUserSM(cont)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = apiCall(id, sm)  // Передаём continuation
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // Если не suspended, продолжаем
        }
        1 -> {
            sm.data = sm.result as Data  // Сохраняем результат
            sm.label = 2
            val result = delay(100, sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
        }
        2 -> {
            return parseUser(sm.data)
        }
    }
}

// State Machine хранит состояние между вызовами
class FetchUserSM(val completion: Continuation<User>) : Continuation<Any?> {
    var label = 0       // Текущее состояние (где остановились)
    var data: Data? = null  // Локальные переменные
    var result: Any? = null // Результат последней операции

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        fetchUser(id, this)  // Продолжаем выполнение
    }
}
```

**Continuation** — это callback на стероидах. Когда корутина приостанавливается:
1. Текущее состояние (label, локальные переменные) сохраняется в объект Continuation
2. Функция возвращает `COROUTINE_SUSPENDED`
3. Поток освобождается для другой работы
4. Когда операция завершена, вызывается `continuation.resumeWith(result)`
5. State machine продолжает с сохранённого label

**Почему это эффективнее потоков?**

```
Thread (1MB stack):
┌────────────────────────────────────────┐
│ Stack frame fetchUser()                │
│   ├─ локальные переменные              │
│   └─ return address                    │
│ Stack frame apiCall()                  │
│   ├─ ...                               │
│ Stack frame networkRead()              │
│   ├─ BLOCKED waiting for I/O           │  ← Весь 1MB занят!
└────────────────────────────────────────┘

Coroutine (~100 bytes):
┌──────────────────────┐
│ Continuation object  │
│   label = 1          │
│   data = null        │  ← Только нужные данные
│   id = "123"         │
└──────────────────────┘
Поток свободен для других корутин!
```

### Корутина билдеры

`runBlocking` блокирует текущий поток до завершения корутины и всех её дочерних. Используется в `main()` и в тестах, но никогда в production-коде Android:

```kotlin
fun main() = runBlocking {
    launch {
        delay(1000)
        println("World")
    }
    println("Hello")
    // Ждёт завершения всех дочерних корутин
}
// Output: Hello, World (через 1 секунду)
```

`launch` запускает корутину "fire-and-forget" и возвращает `Job`. `async` запускает корутину с результатом и возвращает `Deferred<T>`:

```kotlin
fun example1() = runBlocking {
    val job: Job = launch {
        delay(1000)
        println("Task completed")
    }
    println("Task launched")
    job.join()  // Ждём завершения
}

fun example2() = runBlocking {
    val deferred: Deferred<Int> = async {
        delay(1000)
        42
    }
    println("Computing...")
    val result = deferred.await()  // Ждём и получаем результат
    println("Result: $result")
}
```

Множественные `async` внутри `coroutineScope` позволяют выполнять несколько операций параллельно. Функция не вернётся, пока все дочерние корутины не завершатся:

```kotlin
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    val user = async { fetchUser(userId) }
    val posts = async { fetchPosts(userId) }
    val friends = async { fetchFriends(userId) }

    UserData(
        user = user.await(),
        posts = posts.await(),
        friends = friends.await()
    )
}
```

**launch vs async:**
- `launch` возвращает `Job` — для управления жизненным циклом
- `async` возвращает `Deferred<T>` — для получения результата через `await()`
- `launch` для побочных эффектов, `async` для вычислений

## Structured Concurrency

### CoroutineScope - область видимости корутин

`GlobalScope` живёт вечно -- корутины в нём не привязаны к жизненному циклу компонента. Это антипаттерн:

```kotlin
GlobalScope.launch {
    // Корутина может продолжать работать после Activity.onDestroy()
}
```

Правильный подход -- создать собственный scope и отменить его при уничтожении компонента:

```kotlin
class MyViewModel {
    private val scope = CoroutineScope(Dispatchers.Main + Job())

    fun loadData() {
        scope.launch {
            val data = fetchData()
            updateUI(data)
        }
    }

    fun onCleared() {
        scope.cancel()  // Отменяет все корутины в scope
    }
}
```

В Android используйте готовый `viewModelScope`, который автоматически отменяется при `onCleared()`:

```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Автоматически отменится при onCleared()
        }
    }
}
```

**Почему Structured Concurrency?**

**Автоматическая отмена предотвращает "зомби"-задачи.** В традиционном подходе (threads, callbacks) запущенная задача живёт независимо. Если Activity уничтожена, а сетевой запрос продолжает выполняться — это утечка. При structured concurrency отмена scope автоматически отменяет все дочерние корутины. Вызов `scope.cancel()` рекурсивно отменит всё дерево.

**Корутины не переживают свой scope.** `GlobalScope` — антипаттерн именно потому, что живёт вечно. `viewModelScope` в Android автоматически отменяется при `onCleared()`. Когда пользователь закрыл экран — все его корутины отменяются, ресурсы освобождаются.

**Parent ждёт children.** Функция `coroutineScope { }` не вернётся, пока все дочерние корутины внутри не завершатся. Это гарантирует, что при выходе из функции вся асинхронная работа завершена. Нет "висячих" задач, результаты которых никто не ждёт.

### coroutineScope - структурированное выполнение

```kotlin
// coroutineScope создаёт scope и ждёт всех дочерних корутин
suspend fun fetchData(): Data = coroutineScope {
    val user = async { fetchUser() }
    val settings = async { fetchSettings() }

    Data(user.await(), settings.await())
    // Функция не вернётся пока обе корутины не завершатся
}

// Если любая дочерняя корутина кинет исключение:
// - все остальные отменятся
// - coroutineScope пробросит исключение дальше
suspend fun fetchDataWithError() = coroutineScope {
    launch {
        delay(1000)
        throw Exception("Error!")  // Все корутины отменятся
    }

    launch {
        delay(2000)
        println("Never printed")  // Отменится до выполнения
    }
}

// supervisorScope - дочерние корутины независимы
suspend fun fetchDataSupervised() = supervisorScope {
    val job1 = launch {
        delay(1000)
        throw Exception("Error in job1")  // Только этот job упадёт
    }

    val job2 = launch {
        delay(2000)
        println("Job2 completed")  // Выполнится независимо!
    }
}
```

**coroutineScope vs supervisorScope:**
- `coroutineScope`: ошибка в одной корутине отменяет все
- `supervisorScope`: корутины независимы, ошибка не влияет на другие

### Иерархия корутин

```kotlin
fun main() = runBlocking {  // Parent корутина
    launch {  // Child 1
        launch {  // Grandchild 1.1
            delay(1000)
            println("Grandchild 1.1")
        }

        launch {  // Grandchild 1.2
            delay(500)
            println("Grandchild 1.2")
        }

        println("Child 1")
    }

    launch {  // Child 2
        delay(750)
        println("Child 2")
    }

    println("Parent")
    // Parent ждёт всех children (включая grandchildren)
}
// Output:
// Parent
// Child 1
// Grandchild 1.2
// Child 2
// Grandchild 1.1

// Отмена parent отменяет всех children
val parentJob = launch {
    launch {
        repeat(1000) {
            delay(100)
            println("Child 1: $it")
        }
    }

    launch {
        repeat(1000) {
            delay(100)
            println("Child 2: $it")
        }
    }
}

delay(500)
parentJob.cancel()  // Отменяет обе дочерние корутины
```

## Dispatchers - выбор потока выполнения

### Типы диспетчеров

```kotlin
// Dispatchers.Default - для CPU-интенсивных задач
// Пул потоков = количество CPU ядер
launch(Dispatchers.Default) {
    val result = heavyComputation()  // Парсинг, сортировка, расчёты
}

// Dispatchers.IO - для I/O операций
// Пул потоков = 64 (или больше)
launch(Dispatchers.IO) {
    val data = readFile()  // Файлы, сеть, БД
    val response = apiCall()
}

// Dispatchers.Main - UI поток (Android, Swing, JavaFX)
launch(Dispatchers.Main) {
    updateUI()  // Обновление UI элементов
}

// Dispatchers.Unconfined - не привязан к потоку
// Выполняется в текущем потоке до первой suspend точки
launch(Dispatchers.Unconfined) {
    println(Thread.currentThread().name)  // Thread 1
    delay(100)
    println(Thread.currentThread().name)  // Может быть другой поток!
}
```

**Почему разные диспетчеры?**

**Default — ограниченный пул для CPU-задач.** Размер пула = количество CPU ядер. Больше потоков для CPU-bound работы бессмысленно: они будут конкурировать за процессорное время. JSON-парсинг, сортировка, вычисления — сюда.

**IO — большой пул для блокирующих операций.** По умолчанию до 64 потоков. Блокирующие операции (сеть, файлы, JDBC) не нагружают CPU, но ждут I/O. Много потоков позволяет параллельно ждать много операций. Если поток заблокирован на `socket.read()` — это нормально, другие потоки работают.

**Main — единственный UI поток.** В Android/Swing/JavaFX обновлять UI можно только из main thread. Блокировка main = зависшее приложение. Используйте `withContext(Dispatchers.Main)` только для финального обновления UI, не для вычислений.

**Unconfined — для специальных случаев.** Запускается в текущем потоке, но после suspension может продолжиться в любом. Полезен для тестов и специфичных оптимизаций, но в обычном коде редко нужен.

### Переключение контекста

```kotlin
suspend fun loadData() {
    withContext(Dispatchers.IO) {
        // Выполняется на IO потоке
        val data = database.query()

        withContext(Dispatchers.Main) {
            // Переключились на Main поток
            updateUI(data)
        }
    }
}

// Типичный паттерн Android
suspend fun fetchAndDisplay() {
    // Начинаем на Main
    showLoading()

    val data = withContext(Dispatchers.IO) {
        // Переключаемся на IO для сети
        apiCall()
    }

    // Автоматически вернулись на Main
    hideLoading()
    displayData(data)
}

// Вложенные withContext
suspend fun complexOperation() = withContext(Dispatchers.Default) {
    val parsed = parseData()  // На Default

    val saved = withContext(Dispatchers.IO) {
        saveToDatabase(parsed)  // На IO
    }

    // Вернулись на Default
    processResult(saved)
}
```

**withContext vs launch:**
- `withContext` возвращает результат и ждёт завершения
- `launch` запускает корутину и возвращает Job
- `withContext` используется для переключения диспетчера внутри suspend функции

### Создание собственных диспетчеров

```kotlin
// Однопоточный диспетчер
val singleThreadDispatcher = newSingleThreadContext("MyThread")

launch(singleThreadDispatcher) {
    // Всегда выполняется на одном и том же потоке
}

// Фиксированный пул потоков
val fixedThreadPool = newFixedThreadPoolContext(4, "MyPool")

launch(fixedThreadPool) {
    // Выполняется на одном из 4 потоков
}

// Ограничение параллелизма IO диспетчера
val limitedIO = Dispatchers.IO.limitedParallelism(10)

launch(limitedIO) {
    // Максимум 10 параллельных корутин на IO задачах
}

// Закрытие диспетчеров
singleThreadDispatcher.close()
fixedThreadPool.close()
```

## Job и Deferred

### Job - управление жизненным циклом

```kotlin
// Job представляет корутину
val job: Job = launch {
    repeat(1000) {
        delay(100)
        println("Working $it")
    }
}

// Состояния Job
println(job.isActive)      // true во время выполнения
println(job.isCompleted)   // false пока не завершён
println(job.isCancelled)   // false пока не отменён

// Ожидание завершения
job.join()  // Suspend до завершения

// Отмена
job.cancel()  // Отменяет корутину
job.join()    // Ждёт завершения отмены

// Или в одну строку
job.cancelAndJoin()

// Обработка при завершении
job.invokeOnCompletion { exception ->
    if (exception != null) {
        println("Job failed: $exception")
    } else {
        println("Job completed successfully")
    }
}
```

### Отмена корутин

```kotlin
// Корутина должна кооперировать с отменой
val job = launch {
    repeat(1000) {
        // Проверка отмены
        if (!isActive) {
            println("Cancelled!")
            return@launch
        }

        // Или через ensureActive()
        ensureActive()  // Кидает CancellationException если отменена

        println("Working $it")
        Thread.sleep(100)  // НЕ проверяет отмену!
    }
}

delay(500)
job.cancel()

// delay() сама проверяет отмену
val job2 = launch {
    repeat(1000) {
        delay(100)  // Автоматически кидает CancellationException при отмене
        println("Working $it")
    }
}

// Неотменяемая корутина (антипаттерн!)
val job3 = launch {
    repeat(1000) {
        Thread.sleep(100)  // Блокирует поток, не проверяет отмену
        println("Working $it")  // Будет работать даже после cancel()!
    }
}
```

**Почему важна кооперация?**

**Корутины не прерываются силой.** В отличие от `Thread.interrupt()`, который устанавливает флаг и может прервать блокирующую операцию, корутины используют кооперативную отмену. Корутина сама решает, когда проверить флаг отмены. Если она занята вычислениями и не проверяет — отмена не произойдёт.

**Стандартные suspend-функции проверяют автоматически.** `delay()`, `yield()`, `withContext()` и все библиотечные suspend-функции проверяют отмену перед выполнением. Если корутина отменена — они бросят `CancellationException` и корутина завершится.

**Для блокирующего кода нужна ручная проверка.** `Thread.sleep()` или длинный цикл вычислений не знают про корутины. Они не проверят отмену сами. Используйте `isActive` в циклах или `ensureActive()` для периодической проверки.

```kotlin
// Плохо: не реагирует на отмену
while (true) {
    heavyComputation()  // Никогда не остановится по cancel()
}

// Хорошо: проверяет отмену
while (isActive) {
    heavyComputation()  // Выйдет из цикла при cancel()
}
```

### Deferred - результат асинхронных вычислений

```kotlin
// Deferred<T> наследует Job и содержит результат
val deferred: Deferred<Int> = async {
    delay(1000)
    42
}

// await() ждёт результата
val result = deferred.await()  // 42

// Множественные await на одном Deferred
val d = async { heavyComputation() }
val r1 = d.await()  // Вычисляется
val r2 = d.await()  // Возвращает кешированный результат

// Параллельное выполнение
suspend fun fetchAll(): List<String> = coroutineScope {
    val urls = listOf("url1", "url2", "url3")

    val deferreds = urls.map { url ->
        async { fetch(url) }
    }

    // Ждём всех
    deferreds.awaitAll()
}

// getCompleted() - результат без ожидания
val deferred = async { 42 }
delay(100)
if (deferred.isCompleted) {
    val result = deferred.getCompleted()  // Не suspend, кидает исключение если не завершён
}
```

## Обработка исключений

### Распространение исключений

```kotlin
// launch: исключение распространяется вверх по иерархии
val job = launch {
    throw Exception("Error!")
    // Исключение поднимется к родителю
}

// async: исключение сохраняется в Deferred
val deferred = async {
    throw Exception("Error!")
    42
}

try {
    deferred.await()  // Здесь кинется исключение
} catch (e: Exception) {
    println("Caught: $e")
}

// coroutineScope: исключение пробрасывается дальше
suspend fun fetchData() = coroutineScope {
    launch {
        throw Exception("Error!")
    }
    // coroutineScope кинет исключение наружу
}

// supervisorScope: исключения не пробрасываются автоматически
suspend fun fetchDataSafe() = supervisorScope {
    launch {
        throw Exception("Error in child")
        // Не повлияет на supervisorScope
    }
}
```

### CoroutineExceptionHandler

```kotlin
// Handler для необработанных исключений
val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught $exception in $context")
}

// Устанавливается на корень иерархии
val scope = CoroutineScope(Dispatchers.Main + handler)

scope.launch {
    throw Exception("Error!")  // Будет обработано handler'ом
}

// Handler НЕ работает для async
scope.async {
    throw Exception("Error!")  // НЕ будет обработано handler'ом!
}.await()  // Нужно обработать здесь

// SupervisorJob для независимых корутин
val scope = CoroutineScope(SupervisorJob() + handler)

scope.launch {
    throw Exception("Error in 1")  // Не отменит другие корутины
}

scope.launch {
    delay(1000)
    println("Still working")  // Выполнится
}
```

**Правила exception handling:**
- `launch`: исключение идёт к CoroutineExceptionHandler или default handler
- `async`: исключение сохраняется, кидается при `await()`
- `coroutineScope`: пробрасывает исключение дальше
- `supervisorScope`: не пробрасывает исключения дочерних корутин

### try-catch в корутинах

```kotlin
// Обычный try-catch работает
suspend fun safeFetch() {
    try {
        val data = fetchData()
        process(data)
    } catch (e: Exception) {
        handleError(e)
    }
}

// Но не поймает исключения из дочерних launch
suspend fun wontCatch() {
    try {
        coroutineScope {
            launch {
                throw Exception("Error!")  // Не будет поймано!
            }
        }
    } catch (e: Exception) {
        // Не выполнится
    }
}

// Правильно: try-catch внутри launch
suspend fun willCatch() {
    coroutineScope {
        launch {
            try {
                throw Exception("Error!")
            } catch (e: Exception) {
                handleError(e)  // Выполнится
            }
        }
    }
}

// Или используйте supervisorScope
suspend fun withSupervisor() {
    try {
        supervisorScope {
            launch {
                throw Exception("Error!")
            }
        }
    } catch (e: Exception) {
        // supervisorScope не пробрасывает исключения launch
        // Этот catch не сработает
    }
}
```

## Каналы и коммуникация

### Channel - передача данных между корутинами

```kotlin
import kotlinx.coroutines.channels.*

// Создание канала
val channel = Channel<Int>()

// Producer
launch {
    for (x in 1..5) {
        channel.send(x)  // Suspend пока не будет получателя
    }
    channel.close()  // Закрываем канал
}

// Consumer
launch {
    for (y in channel) {  // Итерация до закрытия
        println("Received $y")
    }
}

// Или явно
launch {
    while (!channel.isClosedForReceive) {
        val value = channel.receive()  // Suspend пока нет данных
        println("Received $value")
    }
}
```

### Buffered Channels

```kotlin
// Без буфера (Rendezvous) - send ждёт receive
val channel1 = Channel<Int>()

// С буфером - send не блокируется пока буфер не полон
val channel2 = Channel<Int>(capacity = 10)

// Unlimited buffer - send никогда не suspend
val channel3 = Channel<Int>(Channel.UNLIMITED)

// Conflated - хранит только последнее значение
val channel4 = Channel<Int>(Channel.CONFLATED)

launch {
    repeat(5) {
        channel4.send(it)  // Отправляем 0, 1, 2, 3, 4
    }
}

delay(100)
println(channel4.receive())  // Получим только 4 (последнее)
```

### Produce builder

```kotlin
// produce создаёт ReceiveChannel
fun CoroutineScope.produceNumbers() = produce {
    var x = 1
    while (true) {
        send(x++)
        delay(100)
    }
}

val numbers = produceNumbers()
repeat(5) {
    println(numbers.receive())
}
numbers.cancel()  // Отменяем producer

// Pipeline паттерн
fun CoroutineScope.produceSquares(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send(x * x)
    }
}

val numbers = produceNumbers()
val squares = produceSquares(numbers)

repeat(5) {
    println(squares.receive())
}

coroutineContext.cancelChildren()
```

## Практические паттерны

### Timeout

```kotlin
// withTimeout - кидает TimeoutCancellationException
try {
    withTimeout(1000) {
        repeat(1000) {
            delay(100)
            println("Working $it")
        }
    }
} catch (e: TimeoutCancellationException) {
    println("Timed out!")
}

// withTimeoutOrNull - возвращает null
val result = withTimeoutOrNull(1000) {
    delay(1500)
    "Result"
}
println(result)  // null

// Практический пример
suspend fun fetchWithTimeout(url: String): String? {
    return withTimeoutOrNull(5000) {
        apiCall(url)
    }
}
```

### Retry логика

```kotlin
suspend fun <T> retry(
    times: Int = 3,
    delayMillis: Long = 1000,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            println("Attempt ${it + 1} failed, retrying...")
            delay(delayMillis)
        }
    }
    return block()  // Последняя попытка без catch
}

// Использование
val data = retry(times = 3, delayMillis = 2000) {
    fetchData()  // Попробует 3 раза с задержкой 2 сек
}
```

### Параллельная обработка с ограничением

```kotlin
// Семафор для ограничения параллелизма
val semaphore = Semaphore(permits = 3)  // Максимум 3 параллельных

suspend fun processWithLimit(items: List<Item>) = coroutineScope {
    items.map { item ->
        async {
            semaphore.withPermit {
                // Максимум 3 корутины одновременно здесь
                processItem(item)
            }
        }
    }.awaitAll()
}

// Или через limitedParallelism
val limitedDispatcher = Dispatchers.IO.limitedParallelism(3)

suspend fun processWithLimitedDispatcher(items: List<Item>) = coroutineScope {
    items.map { item ->
        async(limitedDispatcher) {
            processItem(item)
        }
    }.awaitAll()
}
```

### Кэширование результатов

```kotlin
class DataRepository {
    private var cachedData: Deferred<Data>? = null

    suspend fun getData(): Data {
        val cached = cachedData
        if (cached != null && cached.isCompleted) {
            return cached.getCompleted()
        }

        // Создаём новый Deferred если кэш пуст
        return coroutineScope {
            val newDeferred = async { fetchData() }
            cachedData = newDeferred
            newDeferred.await()
        }
    }

    fun invalidateCache() {
        cachedData = null
    }
}
```

## Распространённые ошибки

### 1. GlobalScope

```kotlin
// ❌ GlobalScope живёт вечно
class MyActivity : Activity() {
    fun loadData() {
        GlobalScope.launch {
            val data = fetchData()
            updateUI(data)  // Activity может быть уничтожена!
        }
    }
}

// ✅ Используйте lifecycleScope или собственный scope
class MyActivity : Activity() {
    private val scope = CoroutineScope(Dispatchers.Main + Job())

    fun loadData() {
        scope.launch {
            val data = fetchData()
            updateUI(data)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()  // Отменяет все корутины
    }
}
```

### 2. Блокирующие вызовы на Main

```kotlin
// ❌ Блокирует UI поток
fun loadData() {
    lifecycleScope.launch(Dispatchers.Main) {
        val data = blockingNetworkCall()  // UI зависнет!
        updateUI(data)
    }
}

// ✅ Используйте withContext для переключения
fun loadData() {
    lifecycleScope.launch(Dispatchers.Main) {
        val data = withContext(Dispatchers.IO) {
            blockingNetworkCall()  // Выполнится на IO потоке
        }
        updateUI(data)  // Вернулись на Main
    }
}
```

### 3. Игнорирование отмены

```kotlin
// ❌ Корутина не отменяется
val job = launch {
    while (true) {
        Thread.sleep(100)  // Не проверяет отмену!
        doWork()
    }
}

// ✅ Используйте delay() или проверяйте isActive
val job = launch {
    while (isActive) {
        delay(100)  // Проверяет отмену
        doWork()
    }
}
```

### 4. Утечка через async без await

```kotlin
// ❌ async без await - ошибки игнорируются
fun loadData() {
    lifecycleScope.async {
        throw Exception("Error!")  // Никто не увидит!
    }
    // Забыли await()
}

// ✅ Используйте launch если не нужен результат
fun loadData() {
    lifecycleScope.launch {
        try {
            val data = fetchData()
        } catch (e: Exception) {
            handleError(e)
        }
    }
}

// ✅ Или await() для async
fun loadData() {
    lifecycleScope.launch {
        try {
            val deferred = async { fetchData() }
            val data = deferred.await()
        } catch (e: Exception) {
            handleError(e)
        }
    }
}
```

### 5. suspend функция без suspend операций

```kotlin
// ❌ suspend модификатор без смысла
suspend fun calculateSum(a: Int, b: Int): Int {
    return a + b  // Никаких suspend вызовов!
}

// ✅ Уберите suspend если нет suspend операций
fun calculateSum(a: Int, b: Int): Int {
    return a + b
}

// suspend имеет смысл только если:
suspend fun realSuspendFunction() {
    delay(100)  // 1. Есть suspend вызовы
    // или
    withContext(Dispatchers.IO) { }  // 2. Переключение контекста
}
```

## Чеклист

- [ ] Избегаете GlobalScope, используете структурированную concurrency
- [ ] Применяете правильные Dispatchers (Main/IO/Default)
- [ ] Корутины кооперируют с отменой (delay, isActive, ensureActive)
- [ ] Обрабатываете исключения правильно (try-catch, CoroutineExceptionHandler)
- [ ] Используете launch для побочных эффектов, async для результатов
- [ ] Применяете withContext для переключения диспетчера
- [ ] Не блокируете Main поток
- [ ] Используете coroutineScope/supervisorScope для структурированности
- [ ] Не забываете await() для async
- [ ] Понимаете разницу между Job и Deferred

## Куда дальше

**Если понял корутины и хочешь реактивность:**
→ [[kotlin-flow]] — реактивные потоки на базе корутин. StateFlow заменяет LiveData, SharedFlow для событий.

**Для понимания контекста:**
→ [[kotlin-functional]] — лямбды и higher-order functions. Корутины интенсивно используют их синтаксис.
→ [[jvm-concurrency-overview]] — как корутины соотносятся с потоками JVM и примитивами синхронизации.

**Практическое применение:**
→ [[kotlin-testing]] — тестирование корутин с runTest, TestDispatcher, Turbine.
→ [[kotlin-best-practices]] — паттерны и антипаттерны асинхронного кода.

## Кто использует и реальные примеры

| Компания | Как используют Coroutines | Результаты |
|----------|--------------------------|------------|
| **JetBrains** | IntelliJ IDEA, все IDE продукты | Async UI operations, background indexing |
| **Google** | Android Jetpack, все современные Android API | Стандарт для async в Android с 2019 |
| **Netflix** | Ktor backend services | Высоконагруженные API с минимальным overhead |
| **Square** | Cash App, OkHttp, Retrofit | Полная интеграция с Coroutines |
| **Uber** | Rider/Driver apps | Замена RxJava, проще тестировать |
| **Pinterest** | Android app async operations | Меньше crashes от race conditions |

### Реальные кейсы оптимизации

```
Case 1: Uber — миграция с RxJava на Coroutines
До: RxJava chains с 5+ операторами, сложный debugging
После: Suspend functions с sequential code, легче читать

Результат:
- Новые разработчики продуктивны за 2 дня вместо 2 недель
- Меньше багов связанных с threading

Case 2: Pinterest — 100K+ concurrent operations
Проблема: Thread pool exhaustion при пиковых нагрузках
Решение: Coroutines + limitedParallelism()

Результат:
- 10x меньше памяти на async операции
- Graceful degradation вместо OOM

Case 3: Ktor высоконагруженный API
Настройка: Dispatchers.IO.limitedParallelism(100)
Нагрузка: 50K requests/second

Результат:
- Latency p99: 15ms
- Memory: 200MB vs 2GB с thread-per-request
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Coroutines — это lightweight threads" | Coroutines — state machines, не threads. Один thread может выполнять миллионы coroutines последовательно |
| "suspend функция автоматически асинхронна" | suspend только маркер возможности приостановки. Без withContext/async код выполняется синхронно на текущем потоке |
| "Dispatchers.IO создаёт неограниченные потоки" | IO dispatcher ограничен 64 потоками (или количеством ядер, если больше). Это shared pool, не unlimited |
| "GlobalScope безопасен для fire-and-forget" | GlobalScope нарушает structured concurrency. Утечки ресурсов, невозможность отмены. Используйте viewModelScope, lifecycleScope |
| "launch и async взаимозаменяемы" | launch возвращает Job (fire-and-forget). async возвращает Deferred с результатом. Разное exception handling |
| "Exception в одной coroutine не влияет на другие" | В coroutineScope/supervisorScope — влияет. Exception отменяет siblings. supervisorScope изолирует failures |
| "runBlocking можно использовать в production" | runBlocking блокирует текущий thread. На Main thread = ANR. Только для тестов и main() |
| "Dispatchers.Main.immediate всегда лучше" | immediate пропускает dispatch если уже на Main. Может нарушить порядок событий. Используйте осознанно |
| "CancellationException — это ошибка" | CancellationException — нормальный механизм отмены. Не логируется как error. Не пробрасывается через catch |
| "withContext(Dispatchers.IO) делает код thread-safe" | withContext меняет thread, не добавляет synchronization. Shared mutable state требует отдельной защиты |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Coroutines |
|--------------|--------------------------------|
| **Continuation-Passing Style (CPS)** | suspend функции компилируются в CPS — state machine с switch на label. Continuation хранит состояние |
| **Cooperative Multitasking** | Coroutines кооперативные — yield control явно (suspension points). В отличие от preemptive threads |
| **Structured Concurrency** | Иерархия parent→children. Cancellation propagates down, failure propagates up. Гарантия cleanup |
| **State Machine** | Каждая suspend функция — state machine. States = suspension points. Transitions = resume |
| **M:N Threading Model** | M coroutines → N threads. Dispatchers реализуют mapping. Экономия resources vs 1:1 model |
| **Context Propagation** | CoroutineContext наследуется по иерархии. Job, Dispatcher, Exception handler — элементы контекста |
| **Cancellation Tokens** | Job — cancellation token pattern. isActive проверка, cancel() запрос. Cooperative cancellation |
| **Thread Pool Patterns** | Dispatchers используют ForkJoinPool (Default), cached thread pool (IO). Work stealing для балансировки |
| **Exception Propagation** | Structured exception handling. SupervisorJob изолирует failures. CoroutineExceptionHandler для top-level |
| **Lazy Evaluation** | async(LAZY) откладывает выполнение до await()/start(). Избегает ненужной работы |

---

## Связь с другими темами

**[[kotlin-flow]]** — Flow строится поверх coroutines: каждый flow builder (`flow {}`) запускается в coroutine, операторы Flow используют suspend functions, а collection происходит в coroutine scope. Без понимания coroutines (structured concurrency, dispatchers, cancellation) невозможно правильно использовать Flow. Coroutines — механизм выполнения, Flow — абстракция для потоков данных. Изучите coroutines перед Flow.

**[[kotlin-functional]]** — suspend functions, по сути, являются продолжением функционального программирования: continuation — это callback, structured concurrency — композиция функций с управлением жизненным циклом. Лямбды и higher-order functions, изученные в functional programming, используются повсеместно в coroutines API: `launch {}`, `async {}`, `withContext {}`. FP даёт основу для понимания coroutines API.

**[[jvm-concurrency-overview]]** — Kotlin coroutines работают поверх JVM threading model: Dispatchers.Default использует ForkJoinPool, Dispatchers.IO — cached thread pool. Понимание JVM concurrency (threads, locks, volatile, happens-before) помогает при отладке coroutine-кода и выборе правильного dispatcher. Coroutines абстрагируют threading, но не устраняют необходимость понимать thread safety.

**[[kotlin-testing]]** — тестирование coroutine-кода требует специальных инструментов: `runTest`, `TestDispatcher`, `advanceUntilIdle`. Без понимания structured concurrency и dispatchers написание тестов для async-кода превращается в борьбу с race conditions и flaky tests. Turbine (от Square) стал стандартом для тестирования Flow. Изучайте testing после освоения coroutines basics.

---

## Источники и дальнейшее чтение

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive*. — Единственная книга, полностью посвящённая корутинам: CPS-трансформация, structured concurrency, dispatcher internals, тестирование. Обязательна для глубокого понимания.
- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition*. — Глава о coroutines даёт фундамент: suspend functions, builders, dispatchers. Хорошее введение от создателей языка.
- Elizarov R. (2018). *Structured Concurrency* (KotlinConf talk). — Доклад автора Kotlin Coroutines о философии structured concurrency и design decisions библиотеки. Объясняет ПОЧЕМУ корутины устроены именно так.
- Herlihy M., Shavit N. (2012). *The Art of Multiprocessor Programming*. — CS-фундамент конкурентного программирования: от теории к практике. Помогает понять, какие проблемы корутины решают на уровне абстракций над потоками.

---

## Проверь себя

> [!question]- Почему structured concurrency считается важнее, чем просто launch/async, и какую проблему GlobalScope создаёт в production?
> Structured concurrency гарантирует: (1) если parent scope отменяется — все child корутины тоже отменяются; (2) parent ждёт завершения всех children; (3) исключение в child пробрасывается в parent. GlobalScope нарушает все три гарантии: корутины живут до завершения приложения, не привязаны к lifecycle, утечки памяти в Android (Activity уничтожена, но корутина продолжает работать), исключения теряются. В production GlobalScope приводит к "zombie корутинам" — невидимым операциям, потребляющим ресурсы.

> [!question]- Сценарий: нужно загрузить данные из двух API параллельно и вернуть результат. Если одна из загрузок упала — отменить вторую. Какой подход использовать: async/await или что-то другое?
> coroutineScope + async: val result = coroutineScope { val user = async { fetchUser() }; val orders = async { fetchOrders() }; Pair(user.await(), orders.await()) }. coroutineScope создаёт scope, который ждёт завершения обоих async. Если один async бросает исключение — coroutineScope отменяет второй и пробрасывает исключение. Не использовать supervisorScope — он не отменяет sibling корутины при ошибке. Не использовать GlobalScope.async — потеряются гарантии structured concurrency.

> [!question]- Почему Dispatchers.IO и Dispatchers.Default используют разные thread pools и когда какой выбрать?
> Dispatchers.Default — для CPU-bound задач (вычисления, парсинг, сортировка). Thread pool размера CPU cores (обычно 4-8 потоков). Больше потоков не ускорят CPU-bound работу, а добавят overhead на context switching. Dispatchers.IO — для I/O-bound задач (HTTP, DB, файлы). Thread pool до 64+ потоков. I/O-задачи проводят большую часть времени в ожидании, поэтому много потоков повышает throughput. Использование Default для I/O: все 4-8 потоков будут заблокированы, UI зависнет. Использование IO для CPU: overhead на лишние потоки и context switching.

> [!question]- Как suspend функция реализована "под капотом" и что такое CPS-трансформация?
> Компилятор трансформирует suspend fun в обычную функцию с дополнительным параметром Continuation<T>. Это Continuation Passing Style (CPS). Тело функции разбивается на state machine: каждая точка suspend — новое состояние. При suspend корутина сохраняет состояние в Continuation и освобождает поток. При resume — восстанавливает состояние и продолжает с нужного шага. Это zero-overhead по сравнению с thread blocking: нет создания нового потока, нет OS context switch.

---

## Ключевые карточки

Чем launch отличается от async?
?
launch возвращает Job — для fire-and-forget операций без результата. async возвращает Deferred<T> — для операций с результатом, получаемым через await(). launch исключение пробрасывает в parent scope. async исключение хранится в Deferred и бросается при await(). Для параллельных операций: два async + два await().

Что такое Dispatchers и какие основные типы?
?
Dispatchers определяют на каком потоке выполняется корутина. Main — UI поток (Android). Default — CPU-bound (вычисления), thread pool = CPU cores. IO — I/O-bound (сеть, файлы), thread pool до 64+ потоков. Unconfined — запускается на текущем потоке, после suspend — на потоке resume. withContext(Dispatchers.IO) для смены dispatcher.

Что гарантирует structured concurrency?
?
1) Child корутины привязаны к parent scope. 2) Parent ждёт завершения всех children. 3) Отмена parent отменяет всех children. 4) Исключение в child пробрасывается в parent (кроме supervisorScope). Это предотвращает утечки корутин, потерю ошибок и zombie-операции. Никогда не используй GlobalScope в production.

Как работает cancellation в корутинах?
?
Корутина проверяет isActive в точках suspend (yield, delay, withContext). При cancel: CancellationException бросается в следующей точке suspend. Для CPU-bound кода нужен явный ensureActive() или yield(). finally блок выполняется при cancellation — для cleanup. withContext(NonCancellable) для critical cleanup (close connection, save state).

Чем coroutineScope отличается от supervisorScope?
?
coroutineScope: исключение в одном child отменяет все sibling корутины и пробрасывается вверх. Для параллельных операций "всё или ничего". supervisorScope: исключение в одном child НЕ отменяет siblings. Для независимых операций "продолжай несмотря на ошибки". В Android ViewModel: viewModelScope — supervisor по умолчанию.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[kotlin-flow]] | Flow — реактивные потоки данных на базе корутин |
| Углубление | [[kotlin-channels]] | Channels — межкорутинная коммуникация, fan-out/fan-in |
| Под капотом | [[kotlin-coroutines-internals]] | CPS, Continuation, state machine — как корутины работают внутри |
| Тестирование | [[kotlin-testing]] | runTest, Turbine — тестирование корутин и Flow |
| Связь | [[kotlin-functional]] | Suspend functions как расширение концепции лямбд |
| Кросс-область | [[java-modern-features]] | Virtual Threads (Java 21) — альтернативный подход к конкурентности на JVM |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, Roman Elizarov talks, Android DevSummit 2024 — Педагогический контент проверен*
