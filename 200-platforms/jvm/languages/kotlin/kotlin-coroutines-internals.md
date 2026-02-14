---
title: "Kotlin Coroutines Internals: как корутины работают внутри"
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
  - "[[kotlin-channels]]"
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-executors-futures]]"
  - "[[jvm-memory-model]]"
prerequisites:
  - "[[kotlin-coroutines]]"
  - "[[jvm-concurrency-overview]]"
reading_time: 55
difficulty: 8
study_status: not_started
mastery: 0
---

# Kotlin Coroutines Internals: как корутины работают внутри

> Глубокое погружение в механику корутин: CPS-трансформация, state machine, Continuation, CoroutineContext, Dispatchers, Job — от байткода до production debugging.

---

## Зачем это нужно

Большинство разработчиков используют корутины как black box: пишут `launch`, `withContext`, `Flow` — и всё работает. Но есть ситуации, когда знание внутренностей становится критическим:

**Debugging production issues.** Стектрейс корутины не похож на обычный стектрейс потока. Без понимания state machine невозможно читать decompiled байткод и разбирать, в каком state корутина зависла. Когда приложение "залипает" на `suspendCancellableCoroutine`, нужно понимать, что `CancellableContinuationImpl` находится в состоянии SUSPENDED, и resume так и не был вызван.

**Performance optimization.** Каждый `withContext(Dispatchers.IO)` — это dispatch, аллокация `DispatchedContinuation`, переключение потока. Когда разработчик понимает, что `withContext` на том же диспатчере оптимизируется (UndispatchedCoroutine), он принимает осознанные решения об архитектуре.

**Понимание framework-кода.** Retrofit, Room, Ktor — все используют `suspendCancellableCoroutine` внутри. Когда Retrofit-адаптер оборачивает OkHttp Call в корутину, он вызывает `continuation.resume(response)` из callback. Без знания Continuation API это чёрная магия.

**Собеседования senior+.** На интервью в Google, Meta, крупные продуктовые компании вопросы вроде "как компилятор трансформирует suspend функцию?" и "чем Dispatchers.Default отличается от IO на уровне thread pool?" — стандарт.

**Написание собственных coroutine primitives.** Если нужно написать свой `suspendCancellableCoroutine`-based adapter или custom CoroutineContext element — без знания internals это невозможно.

**Выбор архитектурных решений.** Знание internals позволяет принимать обоснованные решения: использовать `limitedParallelism()` вместо `newFixedThreadPoolContext()`, понимать стоимость вложенных `withContext`, оценивать impact аллокаций на GC, выбирать между корутинами и Virtual Threads для конкретного сценария.

### Что НЕ нужно знать для повседневной работы

Важно понимать границу. Для 90% задач достаточно знать API: launch, async, withContext, Flow, structured concurrency. Internals нужны когда:
- Стектрейс непонятен, и нужно разобраться, что происходит
- Performance-критичный код, и нужно минимизировать аллокации
- Пишете библиотеку или framework поверх корутин
- Готовитесь к senior+ интервью

---

## TL;DR

- Kotlin-компилятор трансформирует каждую `suspend` функцию в state machine: добавляет параметр `Continuation`, разбивает тело на states по точкам приостановки, генерирует switch по label
- `COROUTINE_SUSPENDED` — sentinel-значение; если suspend функция его вернула, корутина приостановлена; если вернула результат — выполнение продолжается без приостановки
- `CoroutineContext` — immutable indexed set с pattern Element/Key; `plus()` имеет семантику set (последний элемент с тем же Key побеждает); Job всегда новый при наследовании
- `Dispatchers.Default` и `Dispatchers.IO` разделяют один и тот же пул потоков (carrier threads); IO — elastic view поверх общего пула, `limitedParallelism()` создаёт view с семафором, а не отдельный пул
- Job проходит через state machine: New -> Active -> Completing -> Completed (или Cancelling -> Cancelled); ошибки летят вверх, отмена — вниз по иерархии
- Одна корутина стоит ~несколько сотен байт (объект state machine + поля для локальных переменных), в отличие от ~1 MB на поток
- Для debugging: `-Dkotlinx.coroutines.debug`, `DebugProbes.install()`, Coroutines panel в IntelliJ IDEA

---

## Пререквизиты

| Тема | Где изучить | Зачем нужна |
|------|-------------|-------------|
| Suspend функции, CoroutineScope, launch/async | [[kotlin-coroutines]] | Базовое API, которое мы будем разбирать изнутри |
| Потоки JVM, Executor, Future | [[jvm-concurrency-overview]] | Корутины работают поверх потоков; dispatcher = executor |
| JVM Memory Model | [[jvm-memory-model]] | happens-before гарантии при resume корутины |
| Kotlin лямбды и inline | [[kotlin-functional]] | State machine — это анонимный класс (лямбда); inline suspend лямбды не аллоцируют |
| Байткод JVM (базово) | [[jvm-jit-compiler]] | Чтение decompiled Java-кода из Kotlin Bytecode viewer |

---

## Терминология

| Термин | Определение |
|--------|------------|
| **CPS (Continuation Passing Style)** | Стиль трансформации, при котором функция не возвращает результат, а передаёт его в callback (Continuation) |
| **Continuation** | Интерфейс с методом `resumeWith(Result<T>)` — "что делать дальше с результатом" |
| **State Machine** | Конечный автомат, генерируемый компилятором из suspend-функции; каждое состояние — код между двумя точками приостановки |
| **Suspension Point** | Место вызова другой suspend-функции; точка, в которой корутина может приостановиться |
| **COROUTINE_SUSPENDED** | Специальное sentinel-значение (`CoroutineSingletons.COROUTINE_SUSPENDED`); означает "корутина приостановлена, результат будет позже" |
| **BaseContinuationImpl** | Базовый класс state machine; содержит `resumeWith()` и абстрактный `invokeSuspend()` |
| **DispatchedContinuation** | Обёртка над Continuation, которая при resume ставит задачу в очередь диспатчера |
| **ContinuationInterceptor** | Элемент контекста, который перехватывает (оборачивает) каждый Continuation — по сути, диспатчер |
| **Job** | Элемент контекста, представляющий жизненный цикл корутины; формирует parent-child иерархию |
| **Structured Concurrency** | Принцип: child-корутины привязаны к parent; отмена parent отменяет children; parent ждёт children |
| **CoroutineScheduler** | Внутренний планировщик kotlinx.coroutines; реализует work-stealing поверх shared thread pool |
| **Label** | Целочисленное поле в state machine; определяет, в какое состояние перейти при следующем `invokeSuspend()` |
| **SuspendLambda** | Подкласс ContinuationImpl, генерируемый компилятором для suspend-лямбд (блоков launch, async) |
| **CoroutineScheduler** | Кастомный планировщик kotlinx.coroutines; реализует work-stealing; обслуживает и Default, и IO задачи |
| **UndispatchedCoroutine** | Оптимизация withContext: когда dispatcher не меняется, корутина выполняется без dispatch в текущем потоке |

---

## State Machine: детальный разбор

### Исходная suspend-функция

Рассмотрим простую функцию с двумя точками приостановки:

```kotlin
suspend fun fetchUserData(userId: String): UserData {
    val token = getToken()          // suspension point 1
    val user = getUser(token)       // suspension point 2
    return UserData(user.name, user.email)
}
```

Здесь две точки приостановки (`getToken()` и `getUser()`), значит будет **три состояния** (N точек приостановки = N + 1 состояний).

### Шаг 1: CPS-трансформация сигнатуры

Компилятор трансформирует сигнатуру, добавляя параметр `Continuation`:

```kotlin
// Исходная:
suspend fun fetchUserData(userId: String): UserData

// После CPS-трансформации (как видит JVM):
fun fetchUserData(userId: String, cont: Continuation<UserData>): Any?
```

Ключевые изменения:
- Добавлен параметр `Continuation<T>`, где T — исходный return type
- Возвращаемый тип стал `Any?` — потому что функция может вернуть либо результат (`UserData`), либо `COROUTINE_SUSPENDED`

### Шаг 2: Генерация state machine класса

Компилятор генерирует анонимный внутренний класс, наследующий `ContinuationImpl`:

```
Иерархия наследования:
Continuation<T>                  (интерфейс, stdlib)
  |
BaseContinuationImpl             (абстрактный класс, stdlib)
  |                              resumeWith() + abstract invokeSuspend()
ContinuationImpl                 (абстрактный класс, stdlib)
  |                              intercepted() для диспатчинга
SuspendLambda                    (генерируется компилятором)
  |                              для suspend лямбд
Anonymous class                  (генерируется компилятором)
                                 конкретная state machine
```

### Шаг 3: Разбиение на состояния

Тело функции разбивается по точкам приостановки. Каждое состояние маркируется label:

```
State 0 (label=0): Код до первой точки приостановки
                    -> вызов getToken()

State 1 (label=1): Код после getToken(), до getUser()
                    -> вызов getUser(token)

State 2 (label=2): Код после getUser()
                    -> return UserData(...)
```

### Шаг 4: Decompiled байткод (упрощённый)

Вот что генерирует компилятор (упрощённо, но близко к реальному байткоду):

```java
// Decompiled Java (Tools -> Kotlin -> Show Kotlin Bytecode -> Decompile)
public final Object fetchUserData(String userId, Continuation<UserData> cont) {
    // Создаём или переиспользуем state machine
    FetchUserDataStateMachine sm;
    if (cont instanceof FetchUserDataStateMachine) {
        sm = (FetchUserDataStateMachine) cont;
        // Проверяем, что это resume нашей корутины
        sm.result = null;
    } else {
        sm = new FetchUserDataStateMachine(cont);
    }
    sm.userId = userId;  // сохраняем параметр

    Object result = sm.result;
    Object SUSPENDED = COROUTINE_SUSPENDED;

    switch (sm.label) {
        case 0:
            // State 0: начальное состояние
            sm.label = 1;  // следующее состояние после resume
            Object tokenResult = getToken(sm);  // передаём SM как continuation
            if (tokenResult == SUSPENDED) return SUSPENDED;
            // Если getToken() не приостановился — fall through
            result = tokenResult;
            // FALL THROUGH

        case 1:
            // State 1: получили token
            String token = (String) result;
            sm.token = token;  // сохраняем в поле SM
            sm.label = 2;
            Object userResult = getUser(token, sm);
            if (userResult == SUSPENDED) return SUSPENDED;
            result = userResult;
            // FALL THROUGH

        case 2:
            // State 2: получили user
            User user = (User) result;
            return new UserData(user.getName(), user.getEmail());

        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }
}

// Сгенерированный класс state machine
static final class FetchUserDataStateMachine extends ContinuationImpl {
    int label;          // текущее состояние
    Object result;      // результат последнего resume
    String userId;      // параметр функции
    String token;       // локальная переменная, пережившая suspension point

    FetchUserDataStateMachine(Continuation<UserData> completion) {
        super(completion);
    }

    @Override
    public Object invokeSuspend(Object result) {
        this.result = result;
        return fetchUserData(userId, this);  // перезапуск state machine
    }
}
```

### Более сложный пример: вложенные suspend-вызовы и try-catch

Рассмотрим реальный сценарий с обработкой ошибок:

```kotlin
suspend fun loadUserProfile(userId: String): Profile {
    val token = authenticate()           // SP #1
    return try {
        val user = fetchUser(token)      // SP #2
        val avatar = fetchAvatar(user)   // SP #3
        Profile(user, avatar)
    } catch (e: IOException) {
        val cached = loadFromCache(userId)  // SP #4
        Profile(cached, null)
    }
}
```

Здесь 4 точки приостановки -> 5 состояний. Но компилятор генерирует ещё более сложный код из-за try-catch:

```java
// Упрощённый decompiled код:
public Object loadUserProfile(String userId, Continuation cont) {
    LoadUserProfileSM sm;
    if (cont instanceof LoadUserProfileSM) {
        sm = (LoadUserProfileSM) cont;
    } else {
        sm = new LoadUserProfileSM(cont);
    }

    Object result = sm.result;
    Object SUSPENDED = COROUTINE_SUSPENDED;

    try {
        switch (sm.label) {
            case 0:
                sm.userId = userId;
                sm.label = 1;
                result = authenticate(sm);
                if (result == SUSPENDED) return SUSPENDED;
                // fall through

            case 1:
                String token = (String) result;
                sm.token = token;
                sm.label = 2;
                result = fetchUser(token, sm);
                if (result == SUSPENDED) return SUSPENDED;
                // fall through

            case 2:
                User user = (User) result;
                sm.user = user;
                sm.label = 3;
                result = fetchAvatar(user, sm);
                if (result == SUSPENDED) return SUSPENDED;
                // fall through

            case 3:
                Avatar avatar = (Avatar) result;
                return new Profile(sm.user, avatar);

            case 4:
                // Resume после loadFromCache
                UserCache cached = (UserCache) result;
                return new Profile(cached, null);
        }
    } catch (IOException e) {
        // При ошибке в state 2 или 3 — переходим к recovery
        sm.label = 4;
        result = loadFromCache(sm.userId, sm);
        if (result == SUSPENDED) return SUSPENDED;
        UserCache cached = (UserCache) result;
        return new Profile(cached, null);
    }
}
```

Обратите внимание: try-catch в байткоде охватывает switch-блок целиком. Если исключение произойдёт во время одного из suspend-вызовов (fetchUser или fetchAvatar), и корутина была приостановлена, то исключение будет передано через `resumeWith(Result.failure(e))` — и `invokeSuspend()` получит его в параметре `result`. Затем исключение перебрасывается, ловится catch-блоком, и state machine переходит к recovery-коду.

### Полный жизненный цикл вызова suspend-функции

Проследим полный путь от вызова до результата:

```
Вызывающий код:
  launch {
      val data = fetchUserData("user123")  // <-- suspend call
      println(data)
  }

1. launch { } создаёт SuspendLambda (назовём SL-1)
   SL-1.label = 0
   -> dispatch через Dispatchers.Default
   -> Worker thread берёт задачу

2. Worker вызывает SL-1.invokeSuspend(Unit)
   SL-1.label == 0
   -> вызывает fetchUserData("user123", SL-1)

3. fetchUserData получает SL-1 как continuation
   -> Создаёт FetchUserDataSM (назовём SM-2), completion = SL-1
   -> SM-2.label = 0
   -> вызывает getToken(SM-2)

4. getToken — реальная сетевая операция
   -> внутри: suspendCancellableCoroutine { cont ->
        okhttp.enqueue(callback that calls cont.resume(token))
      }
   -> возвращает COROUTINE_SUSPENDED

5. SM-2 видит SUSPENDED -> возвращает SUSPENDED
   SL-1 видит SUSPENDED -> возвращает SUSPENDED
   Worker thread свободен! Идёт брать другие задачи.

   [--- Время проходит. Сетевой запрос выполняется на OkHttp thread ---]

6. OkHttp callback вызывает cont.resume("abc123")
   -> CancellableContinuationImpl.resumeWith(Result.success("abc123"))
   -> intercepted().resumeWith()
   -> DispatchedContinuation.resumeWith()
   -> dispatcher.dispatch(context, task)
   -> Задача попадает в очередь CoroutineScheduler

7. Worker thread (может быть другой!) берёт задачу
   -> SM-2.invokeSuspend(Result.success("abc123"))
   -> SM-2.label == 1 (был установлен перед вызовом getToken)
   -> result = "abc123"
   -> token = (String) result
   -> вызывает getUser(token, SM-2)
   -> ... (аналогично)

8. Когда fetchUserData завершается:
   -> SM-2.completion.resumeWith(Result.success(userData))
   -> SL-1.resumeWith() -> invokeSuspend()
   -> SL-1.label == 1
   -> data = userData
   -> println(data)
   -> return Unit
   -> StandaloneCoroutine.resumeWith(Result.success(Unit))
   -> Job переходит в Completed
```

### Как смотреть реальный байткод

В IntelliJ IDEA:
1. Открыть Kotlin-файл с suspend-функцией
2. **Tools -> Kotlin -> Show Kotlin Bytecode**
3. Нажать кнопку **Decompile** в окне байткода
4. Получить Java-код, который показывает state machine

Также можно использовать `javap -c -p ClassName` для просмотра raw bytecode. В реальном байткоде вместо switch/case используются `TABLESWITCH` или `LOOKUPSWITCH` инструкции JVM, а поля state machine имеют имена вроде `L$0`, `L$1` (для Object-полей) и `I$0`, `I$1` (для примитивов).

### BaseContinuationImpl.resumeWith()

Ключевой метод, который запускает state machine при resume:

```kotlin
// kotlin-stdlib: BaseContinuationImpl.kt (упрощённо)
internal abstract class BaseContinuationImpl(
    val completion: Continuation<Any?>?
) : Continuation<Any?> {

    final override fun resumeWith(result: Result<Any?>) {
        var current = this
        var param = result

        while (true) {
            with(current) {
                val outcome: Any? = try {
                    // Вызываем сгенерированный invokeSuspend
                    val result = invokeSuspend(param)
                    if (result === COROUTINE_SUSPENDED) return  // корутина приостановилась
                    Result.success(result)
                } catch (e: Throwable) {
                    Result.failure(e)
                }
                releaseIntercepted()  // освобождаем intercepted continuation
                val completion = completion!!

                if (completion is BaseContinuationImpl) {
                    // Оптимизация: не рекурсия, а цикл (tail-call)
                    current = completion
                    param = outcome
                } else {
                    // Конец цепочки — отдаём результат в completion
                    completion.resumeWith(outcome)
                    return
                }
            }
        }
    }

    protected abstract fun invokeSuspend(result: Result<Any?>): Any?
}
```

Обратите внимание на цикл `while(true)` — это оптимизация tail-call. Если `completion` тоже `BaseContinuationImpl` (то есть вызывающая функция тоже suspend), вместо рекурсивного вызова `resumeWith` просто обновляются `current` и `param`. Это предотвращает StackOverflowError при глубоких цепочках suspend вызовов.

### COROUTINE_SUSPENDED: sentinel-значение

```kotlin
// kotlin-stdlib: CoroutineSingletons.kt
internal enum class CoroutineSingletons {
    COROUTINE_SUSPENDED,
    UNDECIDED,
    RESUMED
}
```

`COROUTINE_SUSPENDED` — это маркер "функция приостановлена, результат будет позже". Когда suspend-функция вызывает другую suspend-функцию:

```
Сценарий 1: Дочерняя функция приостановилась
fetchUserData() -> getToken(sm) -> возвращает COROUTINE_SUSPENDED
fetchUserData() видит SUSPENDED -> возвращает SUSPENDED вверх по стеку
... позже getToken вызывает sm.resumeWith(Result.success(token))
-> invokeSuspend() -> switch(label=1) -> продолжение

Сценарий 2: Дочерняя функция не приостановилась
fetchUserData() -> getToken(sm) -> возвращает "abc123" сразу
fetchUserData() видит результат != SUSPENDED -> fall through в case 1
-> нет приостановки, нет дополнительного dispatch
```

### Хранение локальных переменных

Компилятор анализирует, какие локальные переменные нужны после каждой точки приостановки, и сохраняет их как поля state machine объекта:

```
Переменная    Нужна после SP#1?    Нужна после SP#2?    Сохраняется?
-----------   -----------------    -----------------    -----------
userId        Нет                  Нет                  Нет (только параметр)
token         Да (в getUser)       Нет                  Да (поле sm.token)
user          -                    Да (в return)        Нет (последний state)
```

Если переменная нужна только до первой точки приостановки — она остаётся в стековом фрейме и не копируется в state machine. Это оптимизация: меньше полей = меньше памяти.

### Оптимизации компилятора

**Tail-call оптимизация в resumeWith.** Цепочка suspend-вызовов не увеличивает стек — цикл `while(true)` в `BaseContinuationImpl.resumeWith()` заменяет рекурсию итерацией.

**Inline suspend лямбды.** Если suspend лямбда передана в `inline` функцию, компилятор не создаёт отдельный объект:

```kotlin
// inline функция — лямбда не аллоцируется
suspend inline fun <T> measureTime(block: suspend () -> T): T { ... }

// НЕ-inline — создаётся объект SuspendLambda
suspend fun <T> withRetry(block: suspend () -> T): T { ... }
```

**Fast path без приостановки.** Если вызванная suspend-функция возвращает результат сразу (не COROUTINE_SUSPENDED), state machine просто "проваливается" в следующий case без dispatch и без аллокации `DispatchedContinuation`.

### Стоимость state machine

| Аспект | State Machine (корутина) | Thread |
|--------|--------------------------|--------|
| Память | ~100-200 байт (объект SM + поля) | ~1 MB (стек потока) |
| Создание | Аллокация одного объекта | Системный вызов ОС |
| 100K штук | ~20-40 MB | ~100 GB |
| Переключение | Вызов метода + dispatch | Context switch ядра |
| Хранение состояния | Поля объекта в heap | Стековые фреймы |

Расчёт размера state machine объекта:

```
Базовый объект (JVM 64-bit, compressed oops):
  Object header:              12 байт
  completion (Continuation):   4 байт (ссылка)
  label (int):                 4 байт
  result (Object):             4 байт
  _context (CoroutineContext): 4 байт
  intercepted (Continuation):  4 байт
  padding:                     0 байт
  ================================
  Итого базовый:              ~32 байт

  + поля для локальных переменных: 4-8 байт каждое
  + поля для параметров функции:   4-8 байт каждое

Типичная suspend-функция с 2-3 полями: ~48-64 байт
Сложная функция с 8-10 полями: ~96-128 байт
```

Для сравнения, стековый фрейм потока для той же функции занимал бы аналогичное место, но стек потока — это непрерывный блок ~1 MB, выделенный заранее, даже если используется только малая часть.

---

## Continuation и его реализация

### Интерфейс Continuation<T>

```kotlin
// kotlin-stdlib: Continuation.kt
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Extension-функции для удобства:
public fun <T> Continuation<T>.resume(value: T)
public fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

Continuation — это "что делать дальше". Два поля — контекст (в каком окружении выполнять) и способ передать результат. Это функциональный аналог callback, но с контекстом.

### Иерархия реализаций

```
Continuation<T>                          (интерфейс, stdlib)
  |
  +-- BaseContinuationImpl               (stdlib, абстрактный)
  |     resumeWith() с while-loop
  |     abstract invokeSuspend()
  |     |
  |     +-- ContinuationImpl             (stdlib, абстрактный)
  |           intercepted() -> кэшированный DispatchedContinuation
  |           |
  |           +-- SuspendLambda           (генерируется компилятором)
  |           |     create() + invoke()
  |           |     для suspend лямбд: launch { ... }, async { ... }
  |           |
  |           +-- RestrictedSuspendLambda (для sequence { })
  |
  +-- SafeContinuation                   (stdlib)
  |     Обёртка для защиты от double resume
  |
  +-- CancellableContinuationImpl        (kotlinx.coroutines)
  |     suspendCancellableCoroutine { }
  |
  +-- DispatchedContinuation             (kotlinx.coroutines)
        Обёртка для dispatch через диспатчер
```

### BaseContinuationImpl -> ContinuationImpl

`ContinuationImpl` добавляет одну важную вещь — кэширование intercepted continuation:

```kotlin
// kotlin-stdlib: ContinuationImpl.kt (упрощённо)
internal abstract class ContinuationImpl(
    completion: Continuation<Any?>?,
    private val _context: CoroutineContext?
) : BaseContinuationImpl(completion) {

    @Transient
    private var intercepted: Continuation<Any?>? = null

    fun intercepted(): Continuation<Any?> =
        intercepted ?: (context[ContinuationInterceptor]
            ?.interceptContinuation(this) ?: this)
            .also { intercepted = it }
}
```

`intercepted()` — запрашивает `ContinuationInterceptor` (обычно это диспатчер) из контекста и оборачивает текущий Continuation. Результат кэшируется — не надо оборачивать каждый раз. При `releaseIntercepted()` кэш очищается.

### CancellableContinuationImpl

Это ключевой класс для интеграции с callback-based API:

```kotlin
// Использование:
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            cont.resume(response.body()!!)
        }
        override fun onFailure(call: Call<T>, t: Throwable) {
            cont.resumeWithException(t)
        }
    })
    cont.invokeOnCancellation { cancel() }  // отмена OkHttp Call при отмене корутины
}
```

Внутренние состояния `CancellableContinuationImpl`:

```
UNDECIDED (0)   -> Начальное состояние, ещё не решено: suspend или нет
SUSPENDED (1)   -> Корутина приостановлена, ждёт resume
RESUMED (2)     -> resume() вызван, корутина продолжит выполнение

Переходы:
UNDECIDED -> SUSPENDED   (нормальный suspend: блок suspendCancellableCoroutine вернул управление)
UNDECIDED -> RESUMED     (fast path: resume вызван ДО выхода из блока — нет настоящей приостановки)
SUSPENDED -> RESUMED     (нормальный resume: callback вызвал cont.resume())
```

При отмене Job вызывается `cancel()` на `CancellableContinuationImpl`, который:
1. Ставит состояние CANCELLED
2. Вызывает invokeOnCancellation handler
3. При попытке `resume()` после cancel — бросает `CancellationException`

### SafeContinuation

Обёртка для защиты от double resume:

```kotlin
// kotlin-stdlib: SafeContinuation.kt (упрощённо)
internal class SafeContinuation<in T>(
    private val delegate: Continuation<T>,
    initialResult: Any?
) : Continuation<T> {
    @Volatile
    private var result: Any? = initialResult  // UNDECIDED

    override fun resumeWith(result: Result<T>) {
        val cur = this.result
        when {
            cur === UNDECIDED -> {
                this.result = result.value  // CAS
            }
            cur === COROUTINE_SUSPENDED -> {
                this.result = RESUMED
                delegate.resumeWith(result)
            }
            else -> throw IllegalStateException("Already resumed")
        }
    }
}
```

`SafeContinuation` используется в `suspendCoroutine {}` (не cancellable-версия). В `suspendCancellableCoroutine` используется `CancellableContinuationImpl`, который сам обрабатывает double resume.

### DispatchedContinuation: мост между Continuation и Dispatcher

`DispatchedContinuation` — это ключевой класс, соединяющий state machine с потоковой моделью:

```kotlin
// kotlinx.coroutines: DispatchedContinuation.kt (упрощённо)
internal class DispatchedContinuation<T>(
    val dispatcher: CoroutineDispatcher,
    val continuation: Continuation<T>  // оригинальный state machine
) : DispatchedTask<T>(), Continuation<T> {

    override fun resumeWith(result: Result<T>) {
        val context = continuation.context
        if (dispatcher.isDispatchNeeded(context)) {
            // Нужен dispatch — ставим в очередь
            _state = result.toState()
            dispatcher.dispatch(context, this)  // this is Runnable!
        } else {
            // Dispatch не нужен (Unconfined или Main.immediate когда уже на Main)
            val eventLoop = ThreadLocalEventLoop.eventLoop
            if (eventLoop.isUnconfinedLoopActive) {
                _state = result.toState()
                eventLoop.dispatchUnconfined(this)
            } else {
                // Выполняем прямо здесь
                continuation.resumeWith(result)
            }
        }
    }

    // Как Runnable:
    override fun run() {
        val continuation = this.continuation
        val result = _state.toResult<T>()
        continuation.resumeWith(result)  // -> BaseContinuationImpl.resumeWith -> invokeSuspend
    }
}
```

Этот класс реализует `Runnable`, поэтому его можно поставить в очередь любого `Executor`/`Handler`/`CoroutineScheduler`. При выполнении `run()` он делегирует в `continuation.resumeWith()`, что запускает state machine.

### startCoroutineCancellable: запуск с поддержкой отмены

```kotlin
// Вызывается при CoroutineStart.DEFAULT:
internal fun <T> (suspend () -> T).startCoroutineCancellable(
    completion: Continuation<T>
) {
    val continuation = createCoroutineUnintercepted(completion)
    // createCoroutineUnintercepted -> компилятор создаёт SuspendLambda
    // completion -> это Job (StandaloneCoroutine/DeferredCoroutine)

    continuation.intercepted()
    // -> context[ContinuationInterceptor]?.interceptContinuation(continuation)
    // -> DispatchedContinuation(dispatcher, continuation)

    .resumeCancellableWith(Result.success(Unit))
    // -> Если Job уже отменён -> бросить CancellationException
    // -> Если не отменён -> dispatcher.dispatch(context, task)
}
```

Ключевая проверка: `resumeCancellableWith` проверяет, не отменён ли Job ещё до dispatch. Это предотвращает бесполезную работу: если scope уже отменён к моменту launch, корутина даже не начнёт выполняться.

---

## CoroutineContext: архитектура

### Element и Key pattern

`CoroutineContext` — это не просто Map. Это immutable indexed set, использующий паттерн Element/Key:

```kotlin
// kotlin-stdlib: CoroutineContext.kt
public interface CoroutineContext {
    public operator fun <E : Element> get(key: Key<E>): E?
    public fun <R> fold(initial: R, operation: (R, Element) -> R): R
    public operator fun plus(context: CoroutineContext): CoroutineContext
    public fun minusKey(key: Key<*>): CoroutineContext

    public interface Key<E : Element>

    public interface Element : CoroutineContext {
        public val key: Key<*>
        // Element ТОЖЕ является CoroutineContext!
    }
}
```

Ключевой паттерн: **каждый Element — это одновременно CoroutineContext**. Это Composite pattern. Одиночный элемент и коллекция элементов имеют один интерфейс.

### Как работает get()

```kotlin
// Типичное использование:
val job = coroutineContext[Job]                      // -> Job?
val dispatcher = coroutineContext[ContinuationInterceptor]  // -> ContinuationInterceptor?
val name = coroutineContext[CoroutineName]            // -> CoroutineName?
```

Каждый элемент использует companion object как Key:

```kotlin
public class CoroutineName(val name: String) : AbstractCoroutineContextElement(CoroutineName) {
    companion object Key : CoroutineContext.Key<CoroutineName>
    //        ^^ companion object является Key для ЭТОГО типа
}

// Поэтому context[CoroutineName] работает — CoroutineName (companion) : Key<CoroutineName>
```

### Операция plus: семантика set

```kotlin
val ctx1 = CoroutineName("worker") + Dispatchers.IO
val ctx2 = ctx1 + CoroutineName("updater")
// ctx2 содержит: CoroutineName("updater") + Dispatchers.IO
// Последний элемент с тем же Key побеждает!
```

Внутренняя структура:

```
CoroutineContext:
+-- CombinedContext
      +-- element: CoroutineName("updater")
      +-- left: CombinedContext
              +-- element: Dispatchers.IO
              +-- left: EmptyCoroutineContext

При get(Key):
  - Если element.key == key -> вернуть element
  - Иначе -> искать в left

При plus(element):
  - Удалить старый элемент с тем же Key (minusKey)
  - Добавить новый в конец цепочки
```

### Визуализация структуры контекста

```
EmptyCoroutineContext
        |
   plus(Job())
        |
   CombinedContext(Job, Empty)
        |
   plus(Dispatchers.Default)
        |
   CombinedContext(Dispatchers.Default, CombinedContext(Job, Empty))
        |
   plus(CoroutineName("worker"))
        |
   CombinedContext(CoroutineName, CombinedContext(Dispatchers.Default, CombinedContext(Job, Empty)))

Доступ: context[CoroutineName] -> O(1) по цепочке
         context[Job]           -> O(n), но n обычно 3-5
```

### fold: обход всех элементов

Метод `fold` — единственный способ обойти все элементы контекста:

```kotlin
// Собрать все элементы в список:
val elements = coroutineContext.fold(emptyList<CoroutineContext.Element>()) { acc, element ->
    acc + element
}
// elements = [Job, Dispatchers.IO, CoroutineName("worker")]

// Пример из kotlinx.coroutines: newCoroutineContext складывает debug info
public fun CoroutineScope.newCoroutineContext(context: CoroutineContext): CoroutineContext {
    val combined = coroutineContext.fold(context) { acc, element ->
        if (element != EmptyCoroutineContext) acc + element else acc
    }
    // ...
}
```

### CombinedContext: внутренняя реализация

Когда два контекста складываются через `plus`, создаётся `CombinedContext` — linked list:

```kotlin
// kotlin-stdlib (упрощённо):
internal class CombinedContext(
    private val left: CoroutineContext,  // "хвост" списка
    private val element: Element         // "голова" (последний добавленный)
) : CoroutineContext {

    override fun <E : Element> get(key: Key<E>): E? {
        // Сначала проверяем голову
        @Suppress("UNCHECKED_CAST")
        if (element[key] != null) return element[key] as E
        // Потом рекурсивно ищем в хвосте
        return left[key]
    }

    override fun minusKey(key: Key<*>): CoroutineContext {
        // Удаляет элемент с данным ключом
        if (element[key] != null) return left
        val newLeft = left.minusKey(key)
        return if (newLeft === left) this
               else if (newLeft === EmptyCoroutineContext) element
               else CombinedContext(newLeft, element)
    }
}
```

Сложность операций:
- `get(key)`: O(n) в худшем случае, но n обычно 3-5 элементов
- `plus(element)`: O(n) — нужно удалить старый элемент с тем же key через minusKey
- `fold`: O(n) — линейный обход всех элементов

### Создание custom CoroutineContext Element

```kotlin
// Пример: передача Request ID через контекст корутины
class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId($id)"
}

// Использование:
launch(RequestId("req-42") + Dispatchers.IO) {
    val requestId = coroutineContext[RequestId]?.id
    // requestId = "req-42"
    logger.info("Processing request $requestId")
}
```

### ThreadContextElement: перенос ThreadLocal

Для интеграции с ThreadLocal-based библиотеками (MDC, Security Context):

```kotlin
// kotlinx.coroutines предоставляет:
class MDCContext(
    private val contextMap: Map<String, String> = MDC.getCopyOfContextMap() ?: emptyMap()
) : ThreadContextElement<Map<String, String>?>(Key) {

    companion object Key : CoroutineContext.Key<MDCContext>

    // Вызывается ПЕРЕД dispatch на целевой поток
    override fun updateThreadContext(context: CoroutineContext): Map<String, String>? {
        val oldMap = MDC.getCopyOfContextMap()
        MDC.setContextMap(contextMap)
        return oldMap  // сохраняем старое значение
    }

    // Вызывается ПОСЛЕ выполнения на целевом потоке
    override fun restoreThreadContext(context: CoroutineContext, oldState: Map<String, String>?) {
        if (oldState != null) MDC.setContextMap(oldState)
        else MDC.clear()
    }
}

// Использование:
MDC.put("requestId", "req-42")
launch(MDCContext()) {
    // MDC.get("requestId") == "req-42"  — перенесён через dispatch!
    withContext(Dispatchers.IO) {
        // И здесь тоже MDC.get("requestId") == "req-42"
    }
}
```

### Стандартные элементы контекста

| Element | Key | Назначение |
|---------|-----|------------|
| `Job` | `Job` | Жизненный цикл, отмена, parent-child |
| `ContinuationInterceptor` | `ContinuationInterceptor` | Диспатчинг (куда отправлять на выполнение) |
| `CoroutineExceptionHandler` | `CoroutineExceptionHandler` | Обработка необработанных исключений |
| `CoroutineName` | `CoroutineName` | Имя для debugging |
| `ThreadContextElement` | custom | Перенос ThreadLocal при dispatch |

### Наследование контекста

```kotlin
val scope = CoroutineScope(
    SupervisorJob() + Dispatchers.Main + CoroutineName("parent")
)

scope.launch(Dispatchers.IO + CoroutineName("child")) {
    // Итоговый контекст:
    // Job         = новый child Job (ВСЕГДА новый!)
    // Dispatcher  = Dispatchers.IO (переопределили)
    // Name        = CoroutineName("child") (переопределили)
}
```

Формула наследования:

```
childContext = parentContext + childOverrides + Job()
```

**Job всегда новый** — это фундаментальное правило structured concurrency. Если бы child использовал parent Job, отмена child отменяла бы parent. Новый child Job становится child-ом parent Job:

```
parentJob
  +-- childJob1 (launch #1)
  +-- childJob2 (launch #2)
       +-- grandchildJob (вложенный launch)
```

---

## ContinuationInterceptor и Dispatchers

### Механизм перехвата

Когда корутина приостанавливается и потом resume-ится, нужно решить: в каком потоке продолжить? Это работа `ContinuationInterceptor`:

```
1. Компилятор генерирует suspend-лямбду (SuspendLambda extends ContinuationImpl)
2. При первом вызове intercepted():
   context[ContinuationInterceptor]?.interceptContinuation(this)
   -> CoroutineDispatcher.interceptContinuation(continuation)
   -> return DispatchedContinuation(this, continuation)
3. При resume:
   DispatchedContinuation.resumeWith(result)
   -> dispatcher.dispatch(context, DispatchedTask)
   -> задача попадает в очередь потоков

     +------------------------+
     | DispatchedContinuation |
     |   dispatcher: Dispatcher.IO  |
     |   continuation: <state machine>  |
     |   resumeWith(result):        |
     |     dispatcher.dispatch(     |
     |       context,               |
     |       this as Runnable       |
     |     )                        |
     +------------------------+
```

### Dispatchers.Default

```
Dispatchers.Default
  |
  +-- Backed by: CoroutineScheduler (kotlinx.coroutines internal)
  |
  +-- Thread pool size: max(2, Runtime.availableProcessors())
  |
  +-- Algorithm: Work-stealing
  |     - Каждый поток имеет локальную очередь задач
  |     - Если очередь пуста, поток "крадёт" задачи из очереди другого потока
  |     - Снижает contention, улучшает CPU utilization
  |
  +-- Оптимизирован для: CPU-bound задач (парсинг, сортировка, вычисления)
  |
  +-- Worker threads: "DefaultDispatcher-worker-1", "DefaultDispatcher-worker-2", ...
```

Исторически `Dispatchers.Default` использовал `java.util.concurrent.ForkJoinPool` через `CommonPool`. В текущих версиях kotlinx.coroutines реализован собственный `CoroutineScheduler` с work-stealing алгоритмом, который более эффективен для корутин.

```kotlin
// CoroutineScheduler.kt (упрощённо)
internal class CoroutineScheduler(
    val corePoolSize: Int,    // availableProcessors
    val maxPoolSize: Int,     // для IO задач
    val schedulerName: String
) {
    // Каждый worker имеет свою очередь
    val workers = Array(maxPoolSize) { Worker(it) }

    // Глобальная очередь для задач, не привязанных к worker
    val globalCpuQueue = GlobalQueue()
    val globalBlockingQueue = GlobalQueue()

    inner class Worker : Thread() {
        val localQueue = WorkStealingQueue()

        override fun run() {
            while (true) {
                val task = findTask() ?: park()
                task.run()
            }
        }

        fun findTask(): Task? =
            localQueue.poll()                    // 1. своя очередь
            ?: globalCpuQueue.poll()             // 2. глобальная CPU
            ?: stealFrom(otherWorkers)           // 3. украсть у соседа
    }
}
```

### Dispatchers.IO

```
Dispatchers.IO
  |
  +-- РАЗДЕЛЯЕТ тот же CoroutineScheduler что и Default!
  |     (те же carrier threads, тот же пул)
  |
  +-- Отличие: задачи маркируются как BLOCKING
  |     -> CoroutineScheduler может создать ДОПОЛНИТЕЛЬНЫЕ потоки
  |     -> до max(64, availableProcessors) одновременных blocking задач
  |
  +-- Системное свойство: kotlinx.coroutines.io.parallelism
  |
  +-- Оптимизирован для: IO-bound задач (сеть, диск, БД)
```

Ключевой инсайт: **Default и IO — не два разных пула, а один пул с двумя "видами" задач:**

```
                    CoroutineScheduler
                    ==================

Worker-1  [CPU] [CPU] [IO] [CPU]    <- один поток выполняет и CPU, и IO задачи
Worker-2  [IO] [IO] [CPU] [IO]
Worker-3  [CPU] [CPU] [CPU]
Worker-4  [IO] [IO] [IO] [IO]      <- при нагрузке IO может быть больше

Лимиты:
- CPU задачи (Default): max = availableProcessors (не больше ядер)
- IO задачи (IO):       max = 64 (или больше, настраивается)
- Общий пул:            адаптивно расширяется для blocking задач
```

### CoroutineScheduler: work-stealing в деталях

Work-stealing — алгоритм, при котором каждый worker имеет свою локальную deque (double-ended queue) задач. Когда worker заканчивает свою задачу:

```
Алгоритм поиска задачи (findTask):
====================================

1. Проверить свою локальную очередь (LIFO — берём последнюю добавленную)
   -> Если есть задача -> выполнить
   -> Cache locality: задача, добавленная этим потоком, скорее всего горячая

2. Проверить глобальную CPU-очередь (FIFO — берём самую старую)
   -> Глобальная очередь используется для задач, не привязанных к worker
   -> FIFO обеспечивает fairness

3. Попытаться "украсть" у другого worker (FIFO — берём самую старую у жертвы)
   -> Выбираем случайного worker
   -> Берём задачу из НАЧАЛА его deque (противоположный конец)
   -> Это минимизирует contention: владелец берёт с конца, вор — с начала

4. Проверить глобальную blocking-очередь
   -> Если текущий worker может выполнять blocking задачи

5. Park (уснуть)
   -> Через LockSupport.parkNanos()
   -> Периодический wakeup для проверки (не busy-wait)

Визуализация:
                    Global CPU Queue
                    [task5] [task4] [task3]
                         |
            +------------+------------+
            |            |            |
       Worker-1     Worker-2     Worker-3
       [task1]      [task7]      (пусто)
       [task2]      [task8]        |
            ^                      |
            |   steal from Worker-1|
            +<---------------------+
```

### Типы задач в CoroutineScheduler

```kotlin
// CoroutineScheduler различает два типа задач:
internal const val TASK_NON_BLOCKING = 0  // CPU-bound (Default)
internal const val TASK_PROBABLY_BLOCKING = 1  // IO-bound (IO)

// При dispatch:
fun dispatch(block: Runnable, taskContext: TaskContext = NonBlockingContext) {
    val task = Task(block, taskContext)
    // Если TASK_PROBABLY_BLOCKING -> может создать дополнительный worker
    // Если TASK_NON_BLOCKING -> использует существующие workers
    currentWorker?.localQueue?.add(task) ?: globalQueue.add(task)
    signalWork()  // разбудить спящий worker
}
```

Когда IO-задача занимает worker, CoroutineScheduler может создать дополнительный поток (до maxPoolSize), чтобы CPU-задачи не голодали. Это "elastic" поведение IO dispatcher.

### limitedParallelism() deep dive

```kotlin
// Создание ограниченного view:
val dbDispatcher = Dispatchers.IO.limitedParallelism(4)
// Не создаёт новый пул! Создаёт "семафорный view" поверх IO

val networkDispatcher = Dispatchers.IO.limitedParallelism(16)
// Ещё один view. dbDispatcher + networkDispatcher могут использовать > 64 потоков!
```

Как работает `limitedParallelism()`:

```
Dispatchers.IO.limitedParallelism(4)
  -> создаёт LimitedDispatcher(parentDispatcher=IO, parallelism=4)

LimitedDispatcher:
  - Внутренняя очередь задач
  - Атомарный счётчик runningWorkers
  - dispatch():
      queue.add(task)
      if (runningWorkers < parallelism) {
          runningWorkers++
          parentDispatcher.dispatch(wrappedTask)
      }
  - После выполнения задачи:
      next = queue.poll()
      if (next != null) {
          parentDispatcher.dispatch(next)  // переиспользуем слот
      } else {
          runningWorkers--
      }
```

Важные тонкости `limitedParallelism()`:
- **IO elastic**: views поверх `Dispatchers.IO` не ограничены лимитом 64; сумма всех views может превышать его
- **Default**: `Dispatchers.Default.limitedParallelism(1)` создаёт single-threaded dispatcher, полезный для мутабельного shared state
- **Не гарантирует конкретные потоки**: задачи могут выполняться на любых потоках пула; гарантируется только max concurrency

### Dispatchers.Main

```kotlin
// Android реализация:
// kotlinx-coroutines-android: HandlerDispatcher.kt
internal class HandlerContext(
    private val handler: Handler  // = Handler(Looper.getMainLooper())
) : HandlerDispatcher() {

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        handler.post(block)  // -> Message в MessageQueue main Looper
    }

    override fun isDispatchNeeded(context: CoroutineContext): Boolean = true

    // Main.immediate:
    val immediate = object : HandlerDispatcher() {
        override fun isDispatchNeeded(context: CoroutineContext): Boolean =
            Looper.myLooper() != handler.looper
            // Если мы УЖЕ на Main — не нужен dispatch!
    }
}
```

`Dispatchers.Main.immediate` — оптимизация: если код уже выполняется на Main Thread, `isDispatchNeeded()` возвращает `false`, и корутина продолжает выполнение без dispatch через Handler. Это экономит один проход через MessageQueue.

### Dispatchers.Unconfined

```kotlin
// Не выполняет dispatch вообще!
override fun isDispatchNeeded(context: CoroutineContext): Boolean = false

// Корутина начинает выполнение в том потоке, где resume() был вызван
// ПОСЛЕ первой suspension — продолжает в потоке, вызвавшем resume()
```

Unconfined полезен в тестах и специфичных сценариях, но опасен в production — нет гарантий, в каком потоке будет выполнение после suspend.

### Сводная таблица диспатчеров

| Dispatcher | Thread pool | Размер | isDispatchNeeded | Сценарий |
|-----------|-------------|--------|------------------|----------|
| **Default** | CoroutineScheduler (CPU) | availableProcessors | true | CPU-bound: парсинг, сортировка, crypto |
| **IO** | CoroutineScheduler (blocking) | max(64, cores) | true | IO-bound: сеть, диск, БД |
| **Main** | Android Handler | 1 (main thread) | true | UI updates |
| **Main.immediate** | Android Handler | 1 (main thread) | false (если на Main) | UI без лишнего dispatch |
| **Unconfined** | нет | нет | false | Тесты, event loops |
| **limitedParallelism(N)** | view поверх parent | max N | true | Rate limiting, connection pools |
| **newFixedThreadPoolContext(N)** | отдельный пул | ровно N | true | Изоляция (legacy, не рекомендуется) |
| **asCoroutineDispatcher()** | из Executor | зависит от Executor | true | Интеграция со старым кодом |

### newSingleThreadContext и asCoroutineDispatcher

Для интеграции с Java-кодом:

```kotlin
// Из существующего ExecutorService:
val executor = Executors.newFixedThreadPool(4)
val dispatcher = executor.asCoroutineDispatcher()

withContext(dispatcher) {
    // Выполняется на потоках executor
}

// ВАЖНО: нужно закрывать!
dispatcher.close()  // -> executor.shutdown()

// Или через use:
Executors.newFixedThreadPool(4).asCoroutineDispatcher().use { dispatcher ->
    withContext(dispatcher) { ... }
}
```

`asCoroutineDispatcher()` создаёт `ExecutorCoroutineDispatcher`, который делегирует `dispatch()` в `executor.execute()`. Это мост между миром `java.util.concurrent` и миром корутин.

---

## Создание корутины: от launch до выполнения

### launch internals

```kotlin
// kotlinx.coroutines: Builders.kt (упрощённо)
public fun CoroutineScope.launch(
    context: CoroutineContext = EmptyCoroutineContext,
    start: CoroutineStart = CoroutineStart.DEFAULT,
    block: suspend CoroutineScope.() -> Unit
): Job {
    // 1. Формируем контекст
    val newContext = newCoroutineContext(context)

    // 2. Создаём корутину (Job)
    val coroutine = if (start.isLazy)
        LazyStandaloneCoroutine(newContext, block)
    else
        StandaloneCoroutine(newContext, active = true)

    // 3. Запускаем
    coroutine.start(start, coroutine, block)
    return coroutine
}
```

Что происходит внутри `newCoroutineContext()`:

```kotlin
public actual fun CoroutineScope.newCoroutineContext(context: CoroutineContext): CoroutineContext {
    // parentContext + переданный context + debug info
    val combined = coroutineContext + context
    // В debug-режиме добавляет CoroutineId
    val debug = if (DEBUG) combined + CoroutineId(COROUTINE_ID.incrementAndGet()) else combined
    // Если нет dispatcher — добавляем Dispatchers.Default
    return if (combined !== Dispatchers.Default && combined[ContinuationInterceptor] == null)
        debug + Dispatchers.Default
    else debug
}
```

Что происходит при `coroutine.start()`:

```kotlin
// CoroutineStart.DEFAULT:
coroutine.start(start, coroutine, block)
  -> block.startCoroutineCancellable(coroutine, coroutine)
    -> createCoroutineUnintercepted(receiver, completion)
       // Создаёт SuspendLambda (state machine объект)
    -> intercepted()
       // Оборачивает в DispatchedContinuation
    -> resumeCancellableWith(Result.success(Unit))
       // Отправляет в dispatcher
```

Полная цепочка от `launch {}` до выполнения блока:

```
launch { block }
  |
  +-> newCoroutineContext()     // формируем контекст
  +-> StandaloneCoroutine()    // создаём Job
  +-> start()
        |
        +-> createCoroutineUnintercepted()   // компилятор создаёт SuspendLambda
        +-> intercepted()                     // -> DispatchedContinuation(dispatcher, SM)
        +-> resumeCancellableWith(Unit)       // -> dispatcher.dispatch(context, task)
              |
              +-> Worker thread picks up task
              +-> DispatchedContinuation.run()
              +-> continuation.resumeWith(result)
              +-> BaseContinuationImpl.resumeWith()
              +-> invokeSuspend()             // -> state machine starts (label=0)
```

### async internals

```kotlin
public fun <T> CoroutineScope.async(
    context: CoroutineContext = EmptyCoroutineContext,
    start: CoroutineStart = CoroutineStart.DEFAULT,
    block: suspend CoroutineScope.() -> T
): Deferred<T> {
    val newContext = newCoroutineContext(context)
    val coroutine = if (start.isLazy)
        LazyDeferredCoroutine(newContext, block)
    else
        DeferredCoroutine<T>(newContext, active = true)
    coroutine.start(start, coroutine, block)
    return coroutine
}
```

`DeferredCoroutine` наследуется от `AbstractCoroutine` и реализует `Deferred<T>`. Метод `await()`:

```kotlin
// DeferredCoroutine.await() -> awaitInternal()
suspend fun awaitInternal(): Any? {
    while (true) {
        val state = this.state
        if (state is CompletedExceptionally) throw state.cause
        if (state is ChildHandleNode) continue  // completing, ждём
        if (state !is Incomplete) return state   // completed — результат готов
        // Корутина ещё не завершена — suspend
        return awaitSuspend()  // -> suspendCancellableCoroutine
    }
}
```

### withContext internals

```kotlin
public suspend fun <T> withContext(
    context: CoroutineContext,
    block: suspend CoroutineScope.() -> T
): T {
    val newContext = newCoroutineContext(context)
    // ...проверки...

    // ОПТИМИЗАЦИЯ: если dispatcher не меняется
    if (newContext === oldContext || newContext[ContinuationInterceptor] === oldContext[ContinuationInterceptor]) {
        // UndispatchedCoroutine: НЕ делает dispatch, выполняет block сразу
        val coroutine = UndispatchedCoroutine(newContext, continuation)
        return coroutine.startUndispatchedOrReturn(block)
    }

    // Dispatcher меняется: нужен dispatch
    val coroutine = DispatchedCoroutine(newContext, continuation)
    coroutine.initParentJob()
    block.startCoroutineCancellable(coroutine, coroutine)
    return coroutine.getResult()  // suspend до завершения block
}
```

Эта оптимизация критична для performance:

```kotlin
// БЕЗ dispatch (тот же dispatcher):
withContext(coroutineContext) { ... }  // UndispatchedCoroutine
withContext(CoroutineName("x")) { ... }  // UndispatchedCoroutine (dispatcher не менялся)

// С dispatch (другой dispatcher):
withContext(Dispatchers.IO) { ... }  // DispatchedCoroutine -> два dispatch (туда и обратно)
```

### CoroutineStart: стратегии запуска

```kotlin
enum class CoroutineStart {
    DEFAULT,     // Сразу dispatch -> выполнение
    LAZY,        // Не запускать до start()/join()/await()
    ATOMIC,      // Как DEFAULT, но не проверять cancellation до первого suspension point
    UNDISPATCHED // Запустить СРАЗУ в текущем потоке до первого suspension point
}
```

Детальное сравнение:

```
DEFAULT:
  launch { block }
  -> dispatch -> worker thread -> block starts
  -> Если Job уже отменён к моменту dispatch -> block НЕ выполняется

LAZY:
  val job = launch(start = CoroutineStart.LAZY) { block }
  // Ничего не происходит
  job.start()  // или job.join() / deferred.await()
  -> dispatch -> worker thread -> block starts

ATOMIC:
  launch(start = CoroutineStart.ATOMIC) { block }
  -> dispatch -> worker thread -> block starts
  -> Даже если Job отменён -> block начинает выполнение до первого SP
  -> Полезно для cleanup-кода, который должен выполниться

UNDISPATCHED:
  launch(start = CoroutineStart.UNDISPATCHED) {
      println("1: ${Thread.currentThread().name}")  // текущий поток!
      delay(100)                                     // suspension point
      println("2: ${Thread.currentThread().name}")  // worker поток (dispatch!)
  }
  // "1" печатается СРАЗУ в вызывающем потоке (без dispatch)
  // После первого suspend -> нормальный dispatch через dispatcher
```

`UNDISPATCHED` полезен для оптимизации: если нужно выполнить синхронную часть немедленно, без постановки в очередь. Это как `Main.immediate`, но для любого контекста.

### runBlocking: мост между blocking и suspend мирами

```kotlin
// runBlocking создаёт EventLoop на текущем потоке:
fun main() = runBlocking {
    // Текущий поток блокируется до завершения всех корутин внутри
    launch { delay(1000); println("World") }
    println("Hello")
}

// Внутри:
// 1. Создаёт BlockingCoroutine (наследует Job)
// 2. Создаёт BlockingEventLoop для текущего потока
// 3. Запускает block
// 4. Текущий поток входит в event loop:
//    while (!coroutine.isCompleted) {
//        val task = eventLoop.processNextEvent()
//        if (task == null) LockSupport.park()
//    }
// 5. delay(1000) ставит задачу в event loop с таймером
// 6. По истечении таймера -> resume корутины -> продолжение в event loop
```

`runBlocking` — единственный builder, который блокирует текущий поток. Он используется в `main()` и в тестах. Не использовать внутри корутин — это приводит к deadlock при нехватке потоков в пуле.

---

## Job и Cancellation internals

### State machine Job-а

Job внутри — это state machine с 6 состояниями:

```
                    wait children
+----------+   start   +---------+   finish   +------------+  finish  +-----------+
|   New    | --------> | Active  | --------->  | Completing | ------> | Completed |
| (opt.)   |           |         |             |            |         | (final)   |
+----------+           +---------+             +------------+         +-----------+
                            |                       |
                        cancel/fail             cancel/fail
                            |                       |
                            v                       v
                       +------------+  finish  +-----------+
                       | Cancelling | ------> | Cancelled  |
                       |            |         | (final)    |
                       +------------+         +-----------+
```

| Состояние | isActive | isCompleted | isCancelled | Описание |
|-----------|----------|-------------|-------------|----------|
| New | false | false | false | Создан с `start=LAZY`, не запущен |
| Active | **true** | false | false | Выполняется нормально |
| Completing | **true** | false | false | Тело завершено, ждёт children |
| Cancelling | false | false | false | В процессе отмены, ждёт children |
| Completed | false | **true** | false | Успешно завершён |
| Cancelled | false | **true** | **true** | Отменён или failed |

Обратите внимание: **Completing выглядит как Active** для внешнего наблюдателя (`isActive=true`). Это внутреннее состояние.

### Внутреннее представление (JobSupport.kt)

```kotlin
// JobSupport.kt использует атомарное поле state:
// - Empty/InactiveNodeList   -> New
// - NodeList                 -> Active (список listener-ов)
// - Finishing                -> Completing или Cancelling
// - CompletedExceptionally   -> Cancelled (финальное)
// - Any?                     -> Completed (финальное, результат = state)

internal open class JobSupport constructor(active: Boolean) : Job {
    @Volatile
    private var _state: Any? = if (active) EMPTY_ACTIVE else EMPTY_NEW

    // Атомарные переходы через compareAndSet
    private fun tryMakeCompleting(state: Any?, proposedUpdate: Any?): Any? {
        // CAS на _state
    }
}
```

### Parent-child связи

```kotlin
// При создании child-корутины:
scope.launch {   // parent = scope.coroutineContext[Job]
    launch {     // parent = this coroutine's Job
        // ...
    }
}

// Регистрация child:
// child.initParentJob() ->
//   parent.attachChild(child) ->
//     parent добавляет ChildHandleNode в свой список
//     возвращает ChildHandle для отписки
```

### Распространение отмены и ошибок

```
Отмена (cancel): ВНИЗ по дереву
================================
Parent.cancel()
  -> child1.cancel()
       -> grandchild1.cancel()
       -> grandchild2.cancel()
  -> child2.cancel()

Ошибки (exception): ВВЕРХ по дереву
====================================
grandchild1 throws IOException
  -> child1.childCancelled(IOException)
       -> child1 отменяет child1 и все свои children
       -> parent.childCancelled(IOException)
            -> parent отменяет parent и все children
            -> ЕСЛИ есть CoroutineExceptionHandler -> обрабатывает
            -> ИНАЧЕ -> Thread.uncaughtExceptionHandler

SupervisorJob: ошибки НЕ летят вверх
=====================================
grandchild1 throws IOException
  -> child1.childCancelled(IOException)
       -> child1 отменяется
       -> parent (SupervisorJob).childCancelled(IOException)
            -> return false  // "не моя проблема"
            -> parent НЕ отменяется, child2 продолжает работать
```

### Completing: ожидание children

Состояние Completing — одно из самых тонких. Когда тело корутины завершилось, но у неё есть незавершённые children:

```kotlin
launch {                           // parent Job
    launch { delay(1000) }         // child #1
    launch { delay(2000) }         // child #2
    println("Body done")           // тело завершено
    // Parent переходит в Completing
    // isActive = true (для внешнего наблюдателя)
    // Внутри: ждёт child #1 и child #2
}
// Parent завершится только когда ОБА child завершатся
// -> через ~2000ms -> Completed
```

Внутри `JobSupport` переход в Completing:

```kotlin
// JobSupport.kt (упрощённо):
private fun tryMakeCompleting(state: Any?, proposedUpdate: Any?): Any? {
    // Если нет children — сразу Completed
    if (state !is Incomplete || state is Finishing) return COMPLETING_ALREADY
    // Если есть children — переход в Finishing (Completing)
    val finishing = Finishing(state.list, false, null)
    if (!_state.compareAndSet(state, finishing)) return COMPLETING_RETRY
    // Ждём children:
    finishing.addCompletionHandler { tryFinalizeFinishingState(finishing, proposedUpdate) }
    return COMPLETING_WAITING_CHILDREN
}
```

### Атомарные операции в JobSupport

Job использует lock-free подход с CAS (Compare-And-Swap):

```kotlin
// Все переходы состояний — через CAS:
while (true) {
    val state = _state  // volatile read
    when (state) {
        is Empty -> {
            // Попытка перейти из Empty в NodeList (Active с listeners)
            val list = NodeList()
            if (_state.compareAndSet(state, list)) break  // успех
            // иначе — другой поток уже изменил state, retry
        }
        is NodeList -> {
            // Добавить listener в список
            state.addLast(node)
            break
        }
    }
}
```

Это позволяет избежать synchronized-блоков и работает эффективно при высокой конкуренции.

### invokeOnCompletion internals

```kotlin
// job.invokeOnCompletion { cause -> ... }
// Внутри:
// 1. Если Job уже Completed/Cancelled -> вызвать handler сразу
// 2. Если Active -> добавить handler в NodeList (linked list)
// 3. При переходе в финальное состояние -> обойти NodeList, вызвать все handlers

// NodeList — intrusive linked list:
internal class JobNode : CompletionHandlerBase(), DisposableHandle {
    // prev, next — указатели в двусвязном списке
    // handler — callback
}
```

### CancellationException — особый статус

```kotlin
// CancellationException НЕ распространяется к parent:
child.cancel()  // бросает CancellationException
// -> parent.childCancelled(CancellationException) -> return true
// НО parent НЕ отменяется, потому что CancellationException — "нормальная отмена"

// CancellationException НЕ логируется как ошибка:
// CoroutineExceptionHandler НЕ вызывается для CancellationException
```

Это специальная обработка в `JobSupport`:

```kotlin
// JobSupport.kt (упрощённо)
private fun cancelParent(cause: Throwable): Boolean {
    if (cause is CancellationException) return true  // "обработано", не передаём parent
    // Для других исключений — передаём parent
    return parent?.childCancelled(cause) ?: false
}
```

---

## Debugging корутин

### Флаг -Dkotlinx.coroutines.debug

```bash
# Запуск JVM с debug-флагом:
java -Dkotlinx.coroutines.debug -jar myapp.jar

# Или в build.gradle.kts:
tasks.test {
    jvmArgs("-Dkotlinx.coroutines.debug")
}
```

Что это даёт: имя корутины добавляется к имени потока.

```
Без debug:   Thread name = "DefaultDispatcher-worker-1"
С debug:     Thread name = "DefaultDispatcher-worker-1 @coroutine#3"
```

### CoroutineName

```kotlin
launch(CoroutineName("UserLoader")) {
    // Thread name: "DefaultDispatcher-worker-1 @UserLoader#3"
    // #3 — автоматический ID корутины
}
```

### IntelliJ IDEA Coroutines Panel

В IntelliJ IDEA есть встроенная панель для debugging корутин:

1. Поставить breakpoint в suspend-функции
2. Запустить Debug
3. Открыть вкладку **Coroutines** в Debug tool window
4. Видны все корутины, их состояние (Running/Suspended/Created), стектрейс

Панель показывает:
- Иерархию parent-child корутин
- Состояние каждой корутины
- В каком suspend-вызове корутина приостановлена
- Контекст корутины (dispatcher, name, Job)

### Thread dump анализ

В thread dump suspended корутины не видны как заблокированные потоки (потому что приостановленная корутина не занимает поток). Но можно видеть стектрейсы worker-потоков:

```
"DefaultDispatcher-worker-1 @LoadUsers#3" #15 daemon prio=5
   java.lang.Thread.State: TIMED_WAITING
   at java.lang.Thread.sleep(Thread.java)
   at kotlinx.coroutines.delay(Delay.kt:120)
   at com.example.UserRepo.loadUsers(UserRepo.kt:42)
   ...
```

### DebugProbes API

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-debug:1.9.0")
}
```

```kotlin
import kotlinx.coroutines.debug.DebugProbes

fun main() {
    DebugProbes.install()  // Устанавливает debug-агент через ByteBuddy

    try {
        runBlocking {
            launch(CoroutineName("worker-1")) { delay(1000) }
            launch(CoroutineName("worker-2")) { delay(2000) }

            delay(500)

            // Вывести все корутины:
            DebugProbes.dumpCoroutines()
            // Output:
            // Coroutine "worker-1#2":DeferredCoroutine{Active}@1a2b3c, state: SUSPENDED
            //   at kotlinx.coroutines.delay(Delay.kt)
            //   at com.example.MainKt$main$1$1.invokeSuspend(Main.kt:8)
            // Coroutine "worker-2#3":DeferredCoroutine{Active}@4d5e6f, state: SUSPENDED
            //   at kotlinx.coroutines.delay(Delay.kt)
            //   at com.example.MainKt$main$1$2.invokeSuspend(Main.kt:9)
        }
    } finally {
        DebugProbes.uninstall()
    }
}
```

Программный доступ:

```kotlin
// Получить информацию обо всех корутинах:
val infos: List<CoroutineInfo> = DebugProbes.dumpCoroutinesInfo()
for (info in infos) {
    println("${info.job}: state=${info.state}, context=${info.context}")
    println("  Creation stacktrace: ${info.creationStackTrace}")
    println("  Last observed stacktrace: ${info.lastObservedStackTrace}")
}

// Напечатать иерархию корутин для scope:
DebugProbes.printScope(scope)

// Напечатать иерархию Job:
DebugProbes.printJob(job)
```

### Запуск как Java Agent

```bash
# Альтернативный способ — без вызова install() в коде:
java -javaagent:kotlinx-coroutines-debug-1.9.0.jar -jar myapp.jar

# На Linux/macOS можно запросить dump в рантайме:
kill -5 $PID   # SIGQUIT -> печатает дамп всех корутин
```

### Creation stack traces

```kotlin
// По умолчанию ОТКЛЮЧЕНО (дорого):
DebugProbes.enableCreationStackTraces = true
// Теперь каждая корутина запоминает стектрейс места создания (launch/async)
// Полезно для поиска "кто создал эту утёкшую корутину?"

// ВАЖНО: НЕ включать в production!
// Оверхед: захват стектрейса при каждом launch/async
```

### Stacktrace recovery

По умолчанию стектрейс корутины теряет информацию о вызывающей стороне из-за dispatch-ов. kotlinx.coroutines восстанавливает стектрейсы:

```kotlin
// Без recovery:
Exception in thread "main" java.io.IOException: Network error
    at NetworkClient.fetch(NetworkClient.kt:15)
    at UserRepo$loadUser$2.invokeSuspend(UserRepo.kt:8)
    at BaseContinuationImpl.resumeWith(ContinuationImpl.kt:33)
    at DispatchedTask.run(DispatchedTask.kt:106)
    at CoroutineScheduler.runSafely(CoroutineScheduler.kt:570)
    at CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:750)
    // Потерян стектрейс вызывающего кода!

// С recovery (по умолчанию в debug mode):
Exception in thread "main" java.io.IOException: Network error
    at NetworkClient.fetch(NetworkClient.kt:15)
    at UserRepo$loadUser$2.invokeSuspend(UserRepo.kt:8)
    ... восстановленный стектрейс ...
    at UserRepo.loadUser(UserRepo.kt:7)       // <-- вызывающая функция
    at MainKt$main$1.invokeSuspend(Main.kt:4) // <-- место вызова
```

Как это работает: при каждом dispatch kotlinx.coroutines сохраняет текущий стектрейс в специальном поле, и при возникновении исключения "склеивает" фактический стектрейс с сохранёнными фрагментами. Это можно отключить системным свойством: `-Dkotlinx.coroutines.stacktrace.recovery=false`.

### Интеграция с testing

```kotlin
// kotlinx-coroutines-test предоставляет:
@Test
fun testCoroutine() = runTest {
    // Виртуальное время: delay() не ждёт реально
    // TestCoroutineScheduler контролирует время

    launch {
        delay(1000)  // Не ждёт 1 секунду!
        println("After delay")
    }

    advanceTimeBy(500)   // Перемотать на 500ms
    // "After delay" ещё не напечатано

    advanceTimeBy(500)   // Ещё 500ms
    // Теперь напечатано

    // Или:
    advanceUntilIdle()   // Перемотать до завершения всех корутин
}
```

`TestCoroutineScheduler` заменяет реальный `CoroutineScheduler` и хранит задачи в priority queue, отсортированной по виртуальному времени. `advanceTimeBy()` продвигает виртуальные часы и выполняет задачи, чей `delay` истёк.

### Практические сценарии debugging

**Сценарий 1: Корутина "зависла" — не завершается.**

```kotlin
// 1. Включить DebugProbes
DebugProbes.install()

// 2. Через N секунд сделать дамп
delay(10_000)
val infos = DebugProbes.dumpCoroutinesInfo()
val suspended = infos.filter { it.state == State.SUSPENDED }

// 3. Посмотреть, где корутина suspended:
for (info in suspended) {
    println("Suspended at: ${info.lastObservedStackTrace.firstOrNull()}")
    // -> "at com.example.NetworkClient.fetch(NetworkClient.kt:42)"
    // -> Ага, callback OkHttp никогда не вызывает resume()
}
```

**Сценарий 2: Утечка корутин — создаются, но не отменяются.**

```kotlin
// Включить creation stack traces:
DebugProbes.enableCreationStackTraces = true

// Периодически проверять количество живых корутин:
val count = DebugProbes.dumpCoroutinesInfo().size
if (count > 1000) {
    log.warn("Possible coroutine leak: $count active coroutines")
    DebugProbes.dumpCoroutines()  // -> в лог
}
```

---

## Performance

### Аллокации

Понимание того, что аллоцируется при работе с корутинами, критично для hot paths:

| Операция | Что аллоцируется | Можно избежать? |
|----------|-------------------|-----------------|
| `launch { }` | StandaloneCoroutine + SuspendLambda (state machine) | Нет (но объекты маленькие) |
| `async { }` | DeferredCoroutine + SuspendLambda | Нет |
| `withContext(sameDispatcher)` | UndispatchedCoroutine | Частично (если тот же dispatcher — нет dispatch) |
| `withContext(otherDispatcher)` | DispatchedCoroutine + dispatch overhead | Нет |
| Вызов suspend fun | Ничего (если не приостановилась) | Fast path: нет аллокации DispatchedContinuation |
| `suspendCancellableCoroutine` | CancellableContinuationImpl | Нет |
| inline suspend lambda | Ничего (инлайнится) | Используйте inline |
| Dispatch через dispatcher | DispatchedContinuation (при первом dispatch) | Кэшируется в intercepted() |

### Что НЕ аллоцируется

```kotlin
// 1. Вызов suspend-функции, которая не приостановилась:
suspend fun getValue(): Int = 42  // компилируется в обычный return
// Вызов этой функции из state machine -> label переключается, но dispatch-а нет

// 2. Inline suspend lambda:
inline fun <T> run(block: suspend () -> T): T = ...
// block не создаёт SuspendLambda объект — код инлайнится в state machine вызывающего

// 3. Resume на том же dispatcher (fast path):
// Если поток уже принадлежит нужному dispatcher, dispatch может быть пропущен
```

### Стоимость context switch при withContext

```kotlin
// Два dispatch-а:
withContext(Dispatchers.IO) {   // dispatch #1: текущий -> IO thread
    readFile()
}                               // dispatch #2: IO thread -> предыдущий thread

// Каждый dispatch = постановка задачи в очередь + wakeup потока + context switch
// Типичная стоимость: ~1-5 микросекунд на dispatch
```

Оптимизация: если `withContext` вызывается с тем же dispatcher, dispatch-а нет:

```kotlin
// На Dispatchers.Default:
withContext(Dispatchers.Default) {
    // UndispatchedCoroutine — нет dispatch, выполняется сразу
    compute()
}

// Сравните:
withContext(Dispatchers.IO) {
    // DispatchedCoroutine — два dispatch (туда и обратно)
    readFile()
}
```

### Сравнительная таблица: Coroutines vs Platform Threads vs Virtual Threads

| Характеристика | Kotlin Coroutines | Platform Threads | Virtual Threads (JDK 21+) |
|----------------|-------------------|------------------|---------------------------|
| **Память на единицу** | ~200 байт-1 KB (state machine) | ~1 MB (стек потока) | ~1-10 KB (стек в heap) |
| **Создание** | ~0.1-1 мкс (аллокация объекта) | ~100-500 мкс (системный вызов) | ~1-10 мкс (аллокация в heap) |
| **100K одновременно** | ~20-100 MB | ~100 GB (невозможно) | ~500 MB-1 GB |
| **1M одновременно** | ~200 MB-1 GB | Невозможно | ~5-10 GB |
| **Context switch** | ~10-50 нс (вызов метода) | ~1-10 мкс (ядро ОС) | ~100-500 нс (JVM runtime) |
| **Structured concurrency** | Встроена (Job hierarchy) | Нет (Project Loom partial) | Частично (JEP 453) |
| **Cancellation** | Cooperative, встроена | Interrupt (ненадёжно) | Interrupt |
| **Backpressure** | Flow, Channel | Ручной (BlockingQueue) | Нет встроенного |
| **Dispatcher control** | Да (Default, IO, Main) | Executor | Нет (managed by JVM) |
| **Интеграция с Android** | Полная (lifecycle, viewModelScope) | Ручная | Нет (Android < JDK 21) |

### Benchmark: создание 100K корутин vs потоков

```kotlin
// Benchmark с JMH (kotlinx-benchmark):
@Benchmark
fun createCoroutines() = runBlocking {
    repeat(100_000) {
        launch(Dispatchers.Default) {
            delay(1)
        }
    }
}
// Результат: ~200ms, ~50 MB heap

@Benchmark
fun createThreads() {
    val threads = List(100_000) {
        Thread { Thread.sleep(1) }
    }
    threads.forEach { it.start() }
    threads.forEach { it.join() }
}
// Результат: OOM или ~30 секунд, ~100 GB теоретически
```

### Аллокации на hot path: детальный анализ

Рассмотрим типичный серверный handler:

```kotlin
suspend fun handleRequest(request: Request): Response {
    val user = userRepo.getUser(request.userId)     // suspend
    val permissions = authService.check(user)        // suspend
    return buildResponse(user, permissions)
}
```

Аллокации при каждом вызове:
1. **State machine объект** (~64 байт): поля label, result, user, request
2. **Если getUser приостановилась**: DispatchedContinuation (~48 байт) + постановка в очередь
3. **Если getUser НЕ приостановилась**: 0 дополнительных аллокаций (fast path)
4. **При dispatch**: Task объект (~32 байт) для очереди CoroutineScheduler

Итого worst case: ~150-200 байт на вызов. Для сравнения, RxJava Observable chain аналогичной длины аллоцирует ~500-1000 байт.

### GC impact

Объекты state machine — short-lived (живут время выполнения корутины). Они попадают в Young Generation и собираются Minor GC. Для серверных приложений с high throughput это означает:

```
10,000 RPS * 200 байт/корутина = 2 MB/sec мусора
-> Minor GC каждые ~50 секунд (при 100 MB young gen)
-> Pause: < 1ms (G1GC/ZGC)
```

Это значительно меньше, чем thread-per-request модель, где каждый поток аллоцирует стек ~1 MB.

### Когда корутины быстрее

- **Большое количество конкурентных IO-задач** (10K+): корутины используют меньше памяти и создаются быстрее
- **UI-приложения**: встроенный Dispatchers.Main, structured concurrency с lifecycle, автоматическая привязка к Activity/Fragment lifecycle
- **Backpressure-сценарии**: Flow/Channel обеспечивают встроенный backpressure; с потоками нужны BlockingQueue и ручной контроль
- **Massive fan-out/fan-in**: создание 100K корутин для параллельной обработки — тривиально и дёшево; с потоками это физически невозможно из-за memory overhead

### Когда Virtual Threads могут быть лучше

- **Чисто серверный JVM-код** без Android ограничений
- **Существующий blocking code**, который не хочется переписывать на suspend
- **Pinning** не проблема (нет synchronized-блоков во время IO)

### Coroutines + Virtual Threads: совместное использование

Начиная с kotlinx.coroutines 1.7.3+, можно использовать Virtual Threads как dispatcher:

```kotlin
// Создание dispatcher на Virtual Threads:
val vtDispatcher = Executors.newVirtualThreadPerTaskExecutor()
    .asCoroutineDispatcher()

withContext(vtDispatcher) {
    // Каждый dispatch -> новый virtual thread
    // Полезно для massive IO parallelism с blocking API
    blockingJdbcQuery()
}
```

Однако в большинстве случаев `Dispatchers.IO.limitedParallelism()` предпочтительнее, потому что:
1. Даёт контроль над параллелизмом (virtual threads — неограниченные)
2. Интегрируется с structured concurrency
3. Работает на Android (где нет Virtual Threads)
4. Не создаёт новый поток на каждый dispatch

### Профилирование корутин

Для анализа production performance:

```kotlin
// async-profiler: позволяет видеть wall-clock время suspend-функций
// Запуск: java -agentpath:libasyncProfiler.so=start,event=wall,file=profile.html

// JFR (Java Flight Recorder): работает с корутинами через thread events
// Запуск: java -XX:StartFlightRecording=filename=recording.jfr

// Micrometer integration:
val registry = SimpleMeterRegistry()
val timedDispatcher = Dispatchers.IO.withMicrometerTracing(registry)
// Метрики: dispatch время, queue время, execution время
```

Для профилирования аллокаций:

```kotlin
// JMH с -prof gc:
@Benchmark
fun benchmarkCoroutine(bh: Blackhole) = runBlocking {
    val result = withContext(Dispatchers.Default) { compute() }
    bh.consume(result)
}
// Результат покажет:
// gc.alloc.rate.norm: ~200 B/op (state machine + dispatch overhead)
```

---

## Распространённые ошибки

### Ошибка 1: withContext(Dispatchers.IO) для CPU-bound задач

```kotlin
// НЕПРАВИЛЬНО: IO dispatcher для сортировки
suspend fun sortData(data: List<Int>) = withContext(Dispatchers.IO) {
    data.sorted()  // CPU-bound!
}

// ПРАВИЛЬНО: Default dispatcher для CPU-bound
suspend fun sortData(data: List<Int>) = withContext(Dispatchers.Default) {
    data.sorted()
}
```

Почему важно: `Dispatchers.IO` допускает до 64 одновременных задач. Если все 64 слота заняты CPU-задачами, IO-задачи (сеть, диск) будут ждать в очереди. `Dispatchers.Default` ограничен числом ядер — это правильно для CPU-задач, оставляя IO-слоты свободными.

### Ошибка 2: Непонимание shared pool Default/IO

```kotlin
// Разработчик думает, что это изолированные пулы:
withContext(Dispatchers.Default) { heavyComputation() }  // "не мешает IO"
withContext(Dispatchers.IO) { networkCall() }             // "не мешает CPU"

// Реальность: ОБА используют одни и те же потоки CoroutineScheduler!
// IO может "подождать", пока Default-задачи выполняются на тех же потоках
// Настоящая изоляция — через newFixedThreadPoolContext() (но это дорого)
```

### Ошибка 3: Блокирующий вызов без переключения dispatcher

```kotlin
// НЕПРАВИЛЬНО: blocking IO на Dispatchers.Default
suspend fun getUser(): User {
    return database.querySync()  // blocking! Занимает поток из Default pool
    // Default имеет только N потоков (N = кол-во ядер)
    // 8-ядерная машина: 8 таких вызовов = все потоки заблокированы
}

// ПРАВИЛЬНО:
suspend fun getUser(): User = withContext(Dispatchers.IO) {
    database.querySync()
}

// ЕЩЁ ЛУЧШЕ: использовать suspend-версию:
suspend fun getUser(): User {
    return database.querySuspend()  // настоящий suspend, не блокирует поток
}
```

### Ошибка 4: Ловля CancellationException

```kotlin
// НЕПРАВИЛЬНО: подавляет отмену корутины
try {
    suspendCancellableCoroutine<Unit> { cont ->
        callback.onResult { cont.resume(Unit) }
    }
} catch (e: Exception) {  // Ловит ВСЕ, включая CancellationException
    log.error("Error", e)
    // CancellationException проглочена! Корутина НЕ отменится
}

// ПРАВИЛЬНО:
try {
    suspendCancellableCoroutine<Unit> { cont ->
        callback.onResult { cont.resume(Unit) }
    }
} catch (e: CancellationException) {
    throw e  // ОБЯЗАТЕЛЬНО перебрасываем
} catch (e: Exception) {
    log.error("Error", e)
}

// Или ещё лучше — ловить конкретные типы:
try { ... } catch (e: IOException) { ... }
```

### Ошибка 5: Забывать про invokeOnCancellation

```kotlin
// НЕПРАВИЛЬНО: утечка ресурса при отмене корутины
suspend fun fetchData(): Data = suspendCancellableCoroutine { cont ->
    val call = okHttpClient.newCall(request)
    call.enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            cont.resume(parseResponse(response))
        }
        override fun onFailure(call: Call, e: IOException) {
            cont.resumeWithException(e)
        }
    })
    // Если корутина отменена — call продолжает выполняться!
    // Сервер получит запрос, ответ придёт, но resume() бросит исключение
}

// ПРАВИЛЬНО:
suspend fun fetchData(): Data = suspendCancellableCoroutine { cont ->
    val call = okHttpClient.newCall(request)
    call.enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            cont.resume(parseResponse(response))
        }
        override fun onFailure(call: Call, e: IOException) {
            cont.resumeWithException(e)
        }
    })
    cont.invokeOnCancellation { call.cancel() }  // Отменяем HTTP-запрос
}
```

### Ошибка 6: Создание нового dispatcher вместо limitedParallelism

```kotlin
// НЕПРАВИЛЬНО: создаёт отдельный пул потоков
val dbDispatcher = newFixedThreadPoolContext(4, "DB")
// Проблема: 4 потока ВСЕГДА живы, даже без нагрузки
// Проблема: не переиспользует потоки с Default/IO

// ПРАВИЛЬНО: view поверх существующего пула
val dbDispatcher = Dispatchers.IO.limitedParallelism(4)
// Использует потоки из общего CoroutineScheduler
// Не создаёт отдельных потоков
// Гарантирует max 4 одновременных DB-операции
```

### Ошибка 7: Игнорирование structured concurrency

```kotlin
// НЕПРАВИЛЬНО: GlobalScope — нет parent Job, нет structured concurrency
fun loadData() {
    GlobalScope.launch {
        // Если Activity/Fragment уничтожен — корутина продолжает работать
        // Утечка памяти, бесполезная работа
        val data = fetchFromNetwork()
        updateUI(data)  // Crash! Activity уже мертва
    }
}

// ПРАВИЛЬНО: привязка к lifecycle
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // viewModelScope отменяется при onCleared()
            val data = fetchFromNetwork()
            updateUI(data)
        }
    }
}
```

Причина ошибки: разработчик не понимает, что Job в контексте формирует parent-child иерархию. `GlobalScope` не имеет parent Job, поэтому его корутины не привязаны к жизненному циклу.

### Ошибка 8: Неправильное использование runBlocking внутри корутины

```kotlin
// НЕПРАВИЛЬНО: deadlock при нехватке потоков
suspend fun fetchAllUsers(): List<User> {
    return runBlocking {  // БЛОКИРУЕТ текущий поток!
        users.map { id ->
            async { fetchUser(id) }
        }.awaitAll()
    }
}

// Сценарий deadlock:
// 1. Корутина выполняется на Dispatchers.Default (4 потока на 4-ядерной машине)
// 2. runBlocking блокирует один из 4 потоков
// 3. Внутренние async тоже хотят Default
// 4. Если все 4 потока заблокированы runBlocking -> deadlock

// ПРАВИЛЬНО: использовать coroutineScope (suspend, не blocking)
suspend fun fetchAllUsers(): List<User> = coroutineScope {
    users.map { id ->
        async { fetchUser(id) }
    }.awaitAll()
}
```

`runBlocking` блокирует поток, а `coroutineScope` приостанавливает корутину. Это фундаментальное отличие: блокировка занимает поток (ресурс ОС), приостановка освобождает поток для других корутин.

### Ошибка 9: Непонимание SupervisorJob vs supervisorScope

```kotlin
// НЕПРАВИЛЬНО: SupervisorJob в launch не защищает siblings
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
scope.launch {
    // Этот launch создаёт обычный (не supervisor) child Job
    launch { throw RuntimeException("fail") }  // отменяет parent!
    launch { delay(1000); println("never printed") }
}

// ПРАВИЛЬНО: supervisorScope для локальной supervisor-семантики
scope.launch {
    supervisorScope {
        launch { throw RuntimeException("fail") }   // НЕ отменяет siblings
        launch { delay(1000); println("printed!") }  // выполнится
    }
}
```

Причина: `SupervisorJob()` — это parent Job, который не отменяется при ошибке child. Но `launch {}` внутри создаёт обычный `StandaloneCoroutine` (не supervisor). Ошибка в nested launch поднимается к `StandaloneCoroutine`, который отменяет своих siblings. `supervisorScope` создаёт `SupervisorCoroutine`, который игнорирует ошибки children.

---

## CS-фундамент

| Концепция | Связь с корутинами | Где изучить |
|-----------|--------------------|-------------|
| **Continuation Passing Style (CPS)** | Компилятор трансформирует suspend в CPS; Continuation — callback с контекстом | [[kotlin-coroutines]], Lambda calculus |
| **Finite State Machine (FSM)** | Каждая suspend-функция компилируется в FSM с label-based switch | [[cs-fundamentals-overview]] |
| **Cooperative multitasking** | Корутины отдают управление в точках приостановки (cooperative, не preemptive) | [[concurrency-vs-parallelism]] |
| **Work-stealing** | CoroutineScheduler (Dispatchers.Default) использует work-stealing для балансировки | [[jvm-executors-futures]] |
| **Happens-before** | resume() устанавливает happens-before между suspend и resume; это гарантия JMM | [[jvm-memory-model]] |
| **Composite pattern** | CoroutineContext.Element является CoroutineContext; одиночный элемент = коллекция | [[design-patterns]] |
| **Indexed set (map with typed keys)** | CoroutineContext — immutable indexed set с паттерном Key/Element | [[hash-tables]] |
| **Thread pool и Executor** | Dispatchers — это обёртки над thread pool; CoroutineScheduler = custom Executor | [[jvm-executors-futures]] |
| **Parent-child tree** | Job hierarchy — дерево; отмена = DFS вниз, ошибки = propagation вверх | [[trees-binary]] |
| **Sentinel value** | COROUTINE_SUSPENDED — sentinel, отличающий "приостановлена" от "вернула результат" | Computer Science basics |
| **Lock-free algorithms** | JobSupport использует CAS для атомарных переходов состояний без synchronized | [[synchronization-primitives]] |
| **Event loop** | runBlocking создаёт BlockingEventLoop; Dispatchers.Unconfined использует EventLoop для nested dispatch | [[async-models-overview]] |

---

## Связь с другими темами

**[[kotlin-coroutines]]** — базовое руководство по API корутин (launch, async, withContext, Flow, structured concurrency). Данный материал раскрывает, что стоит за каждым из этих примитивов: launch создаёт StandaloneCoroutine и отправляет SuspendLambda через dispatcher, withContext оптимизирует UndispatchedCoroutine для того же dispatcher, Flow — это cold stream, где каждый collect запускает state machine заново.

**[[kotlin-channels]]** — каналы (Channel) используют `suspendCancellableCoroutine` внутри для приостановки send/receive. `BufferedChannel` реализует lock-free алгоритм с CAS-операциями. Понимание CancellableContinuationImpl из этого материала необходимо для понимания, как именно send() приостанавливает корутину, когда буфер полон.

**[[jvm-concurrency-overview]]** — корутины работают поверх JVM потоков. CoroutineScheduler — это кастомный ExecutorService с work-stealing. Dispatchers.Default аналогичен ForkJoinPool, Dispatchers.IO — elastic thread pool. Знание JVM threading модели (потоки ОС, context switch, happens-before) необходимо для понимания стоимости dispatch.

**[[jvm-executors-futures]]** — Executor и Future — предшественники корутин на JVM. CoroutineDispatcher расширяет Executor (`asCoroutineDispatcher()`). Deferred — корутинный аналог Future с suspend-based await вместо blocking get(). CompletableFuture интегрируется с корутинами через `future.await()`.

**[[jvm-memory-model]]** — JMM гарантирует happens-before между записью в resume() и чтением в invokeSuspend(). Это значит, что state machine поля (сохранённые локальные переменные) безопасно видны после resume без volatile. CoroutineDispatcher.dispatch() тоже устанавливает happens-before (через submit в thread pool). Без понимания JMM невозможно объяснить, почему корутины thread-safe без explicit synchronization.

**[[kotlin-functional]]** — лямбды, inline функции, higher-order функции — всё это используется в API корутин. Suspend лямбда (`suspend () -> T`) компилируется в `SuspendLambda` класс. `inline` suspend функции (например, `coroutineScope`, `withContext`) не создают дополнительных объектов для лямбды. Понимание reified, crossinline, noinline в контексте suspend лямбд важно для написания эффективного кода.

**[[android-coroutines-mistakes]]** — Android-специфичные проблемы: viewModelScope, lifecycleScope, liveData builder, repeatOnLifecycle. Все они построены поверх Job hierarchy и Dispatchers.Main.immediate. Зная internals, можно понять, почему `lifecycleScope.launchWhenStarted` deprecated в пользу `repeatOnLifecycle` — первый только приостанавливает корутину, но не отменяет, что приводит к утечкам upstream Flow collectors.

**[[design-patterns]]** — CoroutineContext использует Composite pattern (Element является CoroutineContext). Builder pattern — launch/async создают и настраивают корутину. Decorator pattern — DispatchedContinuation оборачивает Continuation для добавления dispatch. Strategy pattern — Dispatchers подставляют разные стратегии выполнения.

---

## Источники и дальнейшее чтение

### Книги

1. Moskala M. (2022). *Kotlin Coroutines: Deep Dive* — Ch.1-15. Наиболее полное руководство по internals: state machine, Continuation, Dispatchers, structured concurrency, testing.
2. Goetz B. et al. (2006). *Java Concurrency in Practice* — фундамент для понимания happens-before, thread pool, Executor, который лежит под корутинами.
3. Herlihy M., Shavit N. (2012). *The Art of Multiprocessor Programming* — lock-free алгоритмы, work-stealing, CAS — всё это используется в CoroutineScheduler и Channel.

### Доклады и презентации

4. Elizarov R. (2017). *Deep Dive into Coroutines on JVM* — KotlinConf 2017. Архитектурные решения: почему CPS, почему state machine, бенчмарки. Слайды: resources.jetbrains.com
5. Elizarov R. (2018). *Kotlin Coroutines in Practice* — KotlinConf 2018. Практические паттерны, structured concurrency, обработка ошибок.
6. Elizarov R. (2021). *Kotlin Coroutines: Design and Implementation* — Research paper. Формальное описание дизайна корутин.

### Исходный код и документация

7. kotlinx.coroutines source code — GitHub: github.com/Kotlin/kotlinx.coroutines. Ключевые файлы: JobSupport.kt, CoroutineScheduler.kt, CancellableContinuationImpl.kt, Dispatchers.kt
8. Kotlin stdlib source — GitHub: github.com/JetBrains/kotlin. Файлы: BaseContinuationImpl, ContinuationImpl.kt, CoroutineContext.kt
9. KEEP-0087: Coroutines — github.com/Kotlin/KEEP/blob/master/proposals/coroutines.md. Оригинальное предложение по дизайну корутин.
10. Kotlin Documentation: Debug coroutines — jetbrains.com/help/idea/debug-kotlin-coroutines.html
11. kotlinx-coroutines-debug API — kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-debug/

### Статьи

12. Anifantakis I. (2025). *Inside Kotlin Coroutines: State Machines, Continuations, and Structured Concurrency* — ProAndroidDev. Подробный разбор state machine с диаграммами.
13. Moskala M. *Coroutines under the hood* — kt.academy/article/cc-under-the-hood. Статья-выжимка из книги.
14. Moskala M. *Kotlin Coroutines dispatchers* — kt.academy/article/cc-dispatchers. Детальное описание каждого диспатчера.
15. Moskala M. *What is CoroutineContext and how does it work?* — kt.academy/article/cc-coroutine-context. Element/Key паттерн.
16. *Understanding Kotlin Suspend Functions Internally* — droidcon.com (2025). CPS-трансформация с примерами байткода.
17. *The Beginner's Guide to Kotlin Coroutine Internals* — DoorDash Engineering Blog. Практический разбор internals.

---

## Проверь себя

### Вопрос 1: State Machine и COROUTINE_SUSPENDED

Рассмотрим suspend-функцию с тремя вызовами suspend-функций внутри. Сколько состояний будет в сгенерированной state machine? Что произойдёт, если одна из вызванных suspend-функций вернёт результат немедленно, а не COROUTINE_SUSPENDED?

**Ответ:** State machine будет иметь 4 состояния (3 точки приостановки + 1 начальное). Если функция вернёт результат немедленно (не COROUTINE_SUSPENDED), state machine "провалится" (fall through) в следующий case без приостановки, без dispatch, без аллокации DispatchedContinuation. Это fast path — код продолжит выполняться синхронно в том же потоке.

### Вопрос 2: Dispatchers.Default vs IO

Объясните, почему `Dispatchers.Default.limitedParallelism(1)` и `Dispatchers.IO.limitedParallelism(4)` не создают отдельных пулов потоков. Какой механизм ограничивает параллелизм?

**Ответ:** Оба вызова создают `LimitedDispatcher` — view поверх родительского dispatcher. Внутри LimitedDispatcher используется атомарный счётчик `runningWorkers` и очередь задач. Когда задача завершается, LimitedDispatcher проверяет очередь и, если есть ожидающие задачи, отправляет следующую через parent dispatcher. Физически задачи выполняются на потоках общего CoroutineScheduler. Это семафорный паттерн: ограничение concurrency без выделенных потоков.

### Вопрос 3: CancellationException

Почему при отмене дочерней корутины через `job.cancel()` родительская корутина не отменяется? Какой механизм в JobSupport это обеспечивает?

**Ответ:** `job.cancel()` бросает `CancellationException`. В `JobSupport.cancelParent()` есть проверка: если причина — `CancellationException`, метод возвращает `true` (считается "обработанным") и НЕ вызывает `parent.childCancelled()`. Для любых других исключений (IOException, RuntimeException) ошибка передаётся parent-у, что вызывает каскадную отмену всей иерархии. SupervisorJob переопределяет `childCancelled()`, возвращая `false` — это означает "я не принимаю отмену от child" для любых исключений, не только CancellationException.

### Вопрос 4: Оптимизация withContext

Объясните разницу между `withContext(Dispatchers.IO)` и `withContext(CoroutineName("x"))` с точки зрения количества dispatch-ов и аллокаций.

**Ответ:** `withContext(Dispatchers.IO)` меняет dispatcher, поэтому создаётся `DispatchedCoroutine` и выполняется два dispatch-а: один для переключения на IO thread, второй для возврата на исходный thread после завершения блока. `withContext(CoroutineName("x"))` не меняет dispatcher (только добавляет имя в контекст), поэтому создаётся `UndispatchedCoroutine` — блок выполняется сразу в текущем потоке без dispatch. Экономия: 0 dispatch вместо 2, нет переключения потоков, нет ожидания в очереди.

---

## Ключевые карточки

**Q: Что делает компилятор с suspend-функцией?**
A: Добавляет параметр `Continuation<T>`, меняет return type на `Any?`, генерирует state machine класс с полем `label` и `invokeSuspend()`. Тело разбивается по точкам приостановки на states, переключение через switch(label). Локальные переменные, пережившие suspension point, сохраняются как поля state machine объекта.

---

**Q: Что означает COROUTINE_SUSPENDED?**
A: Это sentinel-значение (`CoroutineSingletons.COROUTINE_SUSPENDED`). Когда suspend-функция его возвращает, это значит "корутина приостановлена, результат будет передан через continuation.resumeWith() позже". Если функция вернула обычное значение (не COROUTINE_SUSPENDED), корутина продолжает выполнение без приостановки (fast path).

---

**Q: Как Dispatchers.Default и IO соотносятся?**
A: Оба используют один и тот же CoroutineScheduler (shared thread pool). Default ограничен числом CPU ядер (CPU-bound задачи). IO допускает до 64+ одновременных blocking-задач, расширяя пул дополнительными потоками. `limitedParallelism()` создаёт LimitedDispatcher — "view" с семафорным ограничением поверх parent, без выделенного пула потоков.

---

**Q: Как устроен CoroutineContext?**
A: Immutable indexed set с паттерном Element/Key. Каждый Element — это одновременно CoroutineContext (Composite pattern). Companion object класса служит Key (`context[Job]`). Операция `plus()` имеет семантику set: последний элемент с тем же Key побеждает. При наследовании контекста Job всегда создаётся новый (child Job), остальные элементы наследуются или переопределяются.

---

**Q: Что такое CancellableContinuationImpl и зачем нужен invokeOnCancellation?**
A: `CancellableContinuationImpl` — реализация Continuation для `suspendCancellableCoroutine`. Имеет состояния UNDECIDED/SUSPENDED/RESUMED. `invokeOnCancellation` регистрирует handler, который вызывается при отмене корутины (Job cancel). Без него внешний ресурс (HTTP-запрос, таймер, listener) продолжит работать после отмены корутины, что приведёт к утечке ресурсов.

---

**Q: Как дебажить зависшие корутины в production?**
A: (1) Флаг `-Dkotlinx.coroutines.debug` добавляет имя корутины в thread name. (2) `DebugProbes.install()` + `dumpCoroutines()` показывают все живые корутины с состоянием и стектрейсом. (3) `DebugProbes.enableCreationStackTraces = true` запоминает, где корутина была создана (дорого, только для debug). (4) IntelliJ IDEA Coroutines panel показывает иерархию и состояния при breakpoint. (5) `kill -5 PID` на Linux/macOS печатает дамп корутин в stdout.

---

## Куда дальше

| Направление | Файл | Что изучать |
|-------------|------|-------------|
| Flow internals | [[kotlin-flow]] | Как Flow использует state machine, cold vs hot streams, SharedFlow/StateFlow internals |
| Channels | [[kotlin-channels]] | Lock-free BufferedChannel, suspend send/receive через CancellableContinuationImpl |
| JVM concurrency | [[jvm-concurrency-overview]] | Потоки, happens-before, volatile — фундамент, поверх которого работают корутины |
| JVM Memory Model | [[jvm-memory-model]] | Формальная модель happens-before, которая гарантирует видимость state machine полей |
| Kotlin testing | [[kotlin-testing]] | TestCoroutineScheduler, runTest, UnconfinedTestDispatcher для тестирования корутин |
| Android lifecycle | [[android-coroutines-mistakes]] | viewModelScope, lifecycleScope, типичные ошибки с lifecycle-aware корутинами |
| Virtual Threads | [[jvm-concurrency-overview]] | Project Loom, сравнение с корутинами, когда что использовать |
| Performance profiling | [[jvm-profiling]] | JMH бенчмарки для корутин, профилирование аллокаций, async-profiler |
| Design patterns | [[design-patterns]] | Composite (CoroutineContext), Decorator (DispatchedContinuation), Strategy (Dispatchers) |
| Synchronization | [[jvm-synchronization]] | CAS, atomic operations — основа lock-free реализации JobSupport и Channel |
