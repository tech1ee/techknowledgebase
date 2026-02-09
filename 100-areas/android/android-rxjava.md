---
title: "RxJava и RxAndroid: полный гайд"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [reactive-streams, observer-pattern, backpressure, functional-programming]
tags:
  - topic/android
  - topic/reactive
  - type/deep-dive
  - level/advanced
related:
  - "[[android-async-evolution]]"
  - "[[android-threading]]"
  - "[[kotlin-flow]]"
---

# RxJava и RxAndroid: полный гайд

## Prerequisites

Для эффективного изучения RxJava необходимо:

- **Понимание callback-based async**: знание традиционных подходов к асинхронности (AsyncTask, Callbacks, Handlers)
- **Базовое понимание streams/collections**: опыт работы с Stream API, lambda expressions
- **Java/Kotlin basics**: знание generics, interfaces, lambda syntax
- **Android lifecycle**: понимание жизненного цикла Activity/Fragment

## Введение в реактивное программирование

RxJava — это implementation паттерна Observer с акцентом на композицию асинхронных операций и обработку потоков данных. Это библиотека для композиции асинхронных и event-based программ с использованием observable sequences.

**Ключевая идея**: Всё — это stream данных. UI events, network responses, database queries — всё можно представить как observable sequence, которую можно transform, combine, filter.

## Терминология

### Observable
Источник данных, который emit'ит 0 или более элементов (items), затем завершается успешно или с ошибкой. Основной строительный блок RxJava.

```kotlin
// Простейший Observable
val observable = Observable.just(1, 2, 3)
```

### Observer
Потребитель данных, который подписывается на Observable и реагирует на события:
- `onNext(T)` — новый элемент
- `onComplete()` — успешное завершение
- `onError(Throwable)` — ошибка

```kotlin
val observer = object : Observer<Int> {
    override fun onSubscribe(d: Disposable) { }
    override fun onNext(t: Int) { println(t) }
    override fun onComplete() { println("Done!") }
    override fun onError(e: Throwable) { println("Error: $e") }
}
```

### Subscription/Disposable
Связь между Observable и Observer. Disposable позволяет отменить подписку и освободить ресурсы.

```kotlin
val disposable: Disposable = observable.subscribe { item ->
    println(item)
}

// Позже отменить
disposable.dispose()
```

### Operator
Функция трансформации потока, которая принимает Observable и возвращает новый Observable.

```kotlin
observable
    .map { it * 2 }        // Operator: умножает каждый элемент на 2
    .filter { it > 5 }     // Operator: фильтрует элементы
    .subscribe { println(it) }
```

### Scheduler
Контекст выполнения (thread pool, executor), определяет где будет выполняться работа.

```kotlin
observable
    .subscribeOn(Schedulers.io())              // Подписка на IO thread
    .observeOn(AndroidSchedulers.mainThread()) // Результат на main thread
    .subscribe { updateUI(it) }
```

### Backpressure
Ситуация, когда producer генерирует данные быстрее, чем consumer их обрабатывает. Требует специальных механизмов контроля.

```kotlin
// Flowable поддерживает backpressure
Flowable.range(1, 1_000_000)
    .onBackpressureBuffer(100) // Буфер на 100 элементов
    .observeOn(Schedulers.computation())
    .subscribe({ /* обработка */ })
```

## История RxJava в Android (2014-2024)

### 2013-2014: RxJava 1.x и приход в Android

**Netflix создаёт RxJava**
- Netflix разрабатывает RxJava как port ReactiveX для JVM
- Цель: упростить работу с асинхронными операциями в микросервисной архитектуре
- RxJava 1.0 выходит в ноябре 2014

**Square и Jake Wharton приносят в Android**
- Jake Wharton и команда Square активно продвигают RxJava в Android community
- RxAndroid 1.0 (2015) — добавляет Android-специфичные schedulers
- Retrofit 2.0 (2016) добавляет нативную поддержку RxJava
- Становится de-facto стандартом для network layer

```kotlin
// Ранний пример (2015)
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") id: String): Observable<User>
}

api.getUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> showUser(user) },
        { error -> showError(error) }
    )
```

### 2016: RxJava 2.x — Reactive Streams specification

**Крупный breaking change** с важными улучшениями:

1. **Reactive Streams compliance**
   - Следование стандарту Reactive Streams
   - Улучшенная interoperability с другими реактивными библиотеками

2. **Новые типы**
   - Observable (без backpressure)
   - Flowable (с backpressure)
   - Single, Maybe, Completable

3. **Null safety**
   - Нельзя emit null values
   - Приводит к более предсказуемому коду

4. **Улучшенная производительность**
   - Меньше allocation'ов
   - Более эффективные operators

```kotlin
// RxJava 2 — разделение типов
val observable: Observable<String> = Observable.just("A", "B")  // Без backpressure
val flowable: Flowable<String> = Flowable.just("A", "B")        // С backpressure
val single: Single<User> = api.getUser("123")                    // Ровно 1 элемент
val completable: Completable = api.updateUser(user)              // Только completion
```

**Период расцвета (2016-2019)**
- RxJava становится обязательным навыком Android developer
- Множество библиотек добавляют RxJava support
- RxBinding для UI events
- Room database с RxJava return types
- Массовое adoption в enterprise проектах

### 2019: Появление Kotlin Coroutines и Flow

**Конкуренция от first-party решения**
- Google продвигает Kotlin Coroutines как recommended approach
- kotlinx.coroutines.flow как reactive alternative
- Официальная документация начинает рекомендовать Coroutines

**Преимущества Coroutines**
- Встроенная language support
- Проще для понимания (sequential код)
- Меньше boilerplate
- Лучшая интеграция с Android (lifecycle scope)

```kotlin
// Flow vs Observable — похожие концепции
// RxJava
api.getUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { user -> updateUI(user) }

// Coroutines + Flow
viewModelScope.launch {
    api.getUser("123")
        .flowOn(Dispatchers.IO)
        .collect { user -> updateUI(user) }
}
```

### 2020: RxJava 3.x — модернизация

**Эволюционное обновление**
- Java 8+ baseline (раньше был Java 6)
- Улучшенная интероперабельность с Java 8 Stream API
- Мелкие performance improvements
- Убраны deprecated API

**Основные изменения:**
1. Java 8 API support (CompletableFuture, Optional, Stream)
2. Улучшенные error messages
3. Новые operators
4. Улучшенная производительность

```kotlin
// RxJava 3 — интеграция с Java 8
val completableFuture: CompletableFuture<String> = CompletableFuture.supplyAsync { "Result" }

Single.fromFuture(completableFuture)
    .subscribe { result -> println(result) }
```

### 2024: Современное состояние

**Текущая позиция RxJava**
- Стабильная, mature библиотека
- Активно поддерживается, но не растёт
- Используется в legacy проектах
- Новые проекты предпочитают Coroutines

**Статистика:**
- ~50% Android проектов используют RxJava (2024)
- ~80% новых проектов стартуют с Coroutines
- Enterprise проекты медленно мигрируют
- Сложные event-driven системы остаются на RxJava

**Когда RxJava всё ещё актуален:**
- Существующие large codebase с RxJava
- Complex event streams с множеством источников
- Backpressure scenarios
- Team expertise в RxJava
- Specific operators отсутствующие в Flow

## RxAndroid — Android-специфичные расширения

**Основная задача**: предоставить Android schedulers

```kotlin
// Основной вклад RxAndroid
AndroidSchedulers.mainThread() // Scheduler для UI thread

// Использование
observable
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { result -> textView.text = result }
```

**RxBinding** (связанный проект от Jake Wharton):
```kotlin
// Clicks как Observable
RxView.clicks(button)
    .debounce(300, TimeUnit.MILLISECONDS)
    .subscribe { /* handle click */ }

// Text changes
RxTextView.textChanges(editText)
    .debounce(500, TimeUnit.MILLISECONDS)
    .subscribe { text -> search(text.toString()) }
```

## Core Types — детальный разбор

### Observable<T> — базовый тип (0..N items)

**Характеристики:**
- Может emit 0, 1 или бесконечное количество элементов
- Не поддерживает backpressure
- Hot или Cold

```kotlin
// Простейший Observable
val numbers = Observable.just(1, 2, 3, 4, 5)

numbers.subscribe { println(it) }
// Output: 1, 2, 3, 4, 5

// Observable из списка
val list = listOf("A", "B", "C")
Observable.fromIterable(list)
    .subscribe { println(it) }

// Observable с периодическим emit
Observable.interval(1, TimeUnit.SECONDS)
    .subscribe { println("Tick: $it") }
```

**Hot vs Cold Observable**

**Cold Observable** (по умолчанию):
- Начинает emit только при subscribe
- Каждый subscriber получает все элементы с начала
- Независимые execution для каждого subscriber

```kotlin
val cold = Observable.just(1, 2, 3)

cold.subscribe { println("Subscriber 1: $it") }
// Output: Subscriber 1: 1, 2, 3

cold.subscribe { println("Subscriber 2: $it") }
// Output: Subscriber 2: 1, 2, 3
```

**Hot Observable**:
- Emit'ит независимо от subscribers
- Subscribers получают только новые элементы после подписки
- Общий source для всех subscribers

```kotlin
val subject = PublishSubject.create<Int>()  // Hot Observable

subject.onNext(1)  // Никто не получит

subject.subscribe { println("Subscriber 1: $it") }
subject.onNext(2)  // Output: Subscriber 1: 2

subject.subscribe { println("Subscriber 2: $it") }
subject.onNext(3)  // Output: Subscriber 1: 3, Subscriber 2: 3
```

### Flowable<T> — с поддержкой backpressure

**Когда использовать:**
- Producer генерирует данные быстрее, чем consumer обрабатывает
- Работа с большими объёмами данных
- Чтение файлов, database queries
- Network streams с большим количеством данных

```kotlin
// Пример проблемы без backpressure
Observable.range(1, 1_000_000)
    .observeOn(Schedulers.computation())
    .subscribe { Thread.sleep(10); println(it) }
// Может привести к OutOfMemoryError

// Решение с Flowable
Flowable.range(1, 1_000_000)
    .onBackpressureBuffer(100)  // Буферизация 100 элементов
    .observeOn(Schedulers.computation())
    .subscribe { Thread.sleep(10); println(it) }
```

**Backpressure стратегии:**

```kotlin
// 1. BUFFER — буферизация всех элементов (может привести к OOM)
Flowable.range(1, 1000)
    .onBackpressureBuffer()
    .subscribe { /* обработка */ }

// 2. DROP — отбрасывает новые элементы если consumer не успевает
Flowable.range(1, 1000)
    .onBackpressureDrop()
    .subscribe { /* обработка */ }

// 3. LATEST — держит только последний элемент
Flowable.range(1, 1000)
    .onBackpressureLatest()
    .subscribe { /* обработка */ }

// 4. ERROR — выбрасывает MissingBackpressureException
Flowable.create<Int>({ emitter ->
    for (i in 1..1000) {
        emitter.onNext(i)
    }
    emitter.onComplete()
}, BackpressureStrategy.ERROR)
```

### Single<T> — ровно 1 элемент или ошибка

**Идеально для:**
- Network requests
- Database queries (one result)
- Любая операция, возвращающая ровно один результат

```kotlin
// Retrofit с Single
interface ApiService {
    @GET("user/{id}")
    fun getUser(@Path("id") id: String): Single<User>
}

api.getUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> showUser(user) },      // onSuccess
        { error -> showError(error) }     // onError
    )

// Single из callable
Single.fromCallable {
    // Heavy computation
    calculateResult()
}
.subscribeOn(Schedulers.computation())
.subscribe { result -> println(result) }
```

**Важное отличие от Observable:**
- Нет `onComplete()` — только `onSuccess(T)` или `onError(Throwable)`
- Гарантированно один элемент или ошибка

### Maybe<T> — 0 или 1 элемент

**Использование:**
- Database query, который может ничего не найти
- Optional результаты
- Cache lookup

```kotlin
// Room database с Maybe
@Query("SELECT * FROM users WHERE id = :id")
fun getUserById(id: String): Maybe<User>

// Использование
database.getUserById("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> showUser(user) },           // onSuccess (если найден)
        { error -> showError(error) },         // onError
        { showUserNotFound() }                 // onComplete (если не найден)
    )

// Maybe из nullable
Maybe.fromCallable<String> {
    cache.get("key")  // Может вернуть null
}
.subscribe { value -> println("Found: $value") }
```

### Completable — только completion, без данных

**Когда использовать:**
- UPDATE/DELETE операции в database
- POST/PUT requests без response body
- Любая операция, где важен только факт выполнения

```kotlin
// Retrofit с Completable
interface ApiService {
    @POST("users/{id}/like")
    fun likeUser(@Path("id") id: String): Completable
}

api.likeUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { showSuccess() },              // onComplete
        { error -> showError(error) }   // onError
    )

// Room database
@Query("DELETE FROM users WHERE id = :id")
fun deleteUser(id: String): Completable

database.deleteUser("123")
    .subscribeOn(Schedulers.io())
    .subscribe { println("User deleted") }
```

## Таблица выбора типа

| Сценарий | Тип | Пример |
|----------|-----|--------|
| 0..N элементов, без backpressure | `Observable<T>` | UI events, небольшие списки |
| 0..N элементов, с backpressure | `Flowable<T>` | Чтение файлов, database stream |
| Ровно 1 элемент | `Single<T>` | Network GET request |
| 0 или 1 элемент | `Maybe<T>` | Cache lookup, optional query |
| Только completion | `Completable` | Database UPDATE/DELETE |
| 0..N элементов из нескольких источников | `Observable<T>` + operators | Combine multiple APIs |

## Operators — полный справочник по категориям

### Creation Operators

**just** — создаёт Observable из переданных значений

```kotlin
Observable.just(1, 2, 3)
    .subscribe { println(it) }
// Output: 1, 2, 3

// Важно: just принимает до 10 параметров
Observable.just("A", "B", "C", "D", "E")
```

**fromArray** — из массива

```kotlin
val array = arrayOf(1, 2, 3, 4, 5)
Observable.fromArray(*array)
    .subscribe { println(it) }
```

**fromIterable** — из коллекции

```kotlin
val list = listOf("Apple", "Banana", "Orange")
Observable.fromIterable(list)
    .subscribe { println(it) }
```

**create** — полный контроль над emission

```kotlin
Observable.create<String> { emitter ->
    try {
        emitter.onNext("First")
        emitter.onNext("Second")
        emitter.onComplete()
    } catch (e: Exception) {
        emitter.onError(e)
    }
}.subscribe { println(it) }

// С backpressure
Flowable.create<Int>({ emitter ->
    for (i in 1..100) {
        if (emitter.isCancelled) break
        emitter.onNext(i)
    }
    emitter.onComplete()
}, BackpressureStrategy.BUFFER)
```

**defer** — отложенное создание (важно для hot/cold)

```kotlin
// БЕЗ defer — значение вычисляется сразу
val withoutDefer = Observable.just(System.currentTimeMillis())

Thread.sleep(1000)
withoutDefer.subscribe { println("First: $it") }

Thread.sleep(1000)
withoutDefer.subscribe { println("Second: $it") }
// Оба subscriber получат ОДИНАКОВОЕ время

// С defer — значение вычисляется при каждой подписке
val withDefer = Observable.defer {
    Observable.just(System.currentTimeMillis())
}

Thread.sleep(1000)
withDefer.subscribe { println("First: $it") }

Thread.sleep(1000)
withDefer.subscribe { println("Second: $it") }
// Каждый subscriber получит РАЗНОЕ время
```

**interval** — периодический emit

```kotlin
// Каждую секунду
Observable.interval(1, TimeUnit.SECONDS)
    .subscribe { println("Tick: $it") }

// С начальной задержкой
Observable.interval(2, 1, TimeUnit.SECONDS)
    .subscribe { println("Tick: $it") }
```

**range** — последовательность чисел

```kotlin
Observable.range(1, 5)
    .subscribe { println(it) }
// Output: 1, 2, 3, 4, 5
```

**empty/never/error** — специальные Observable

```kotlin
// Сразу onComplete
Observable.empty<String>()
    .subscribe(
        { println("onNext") },
        { println("onError") },
        { println("onComplete") }  // Вызовется
    )

// Никогда не завершается
Observable.never<String>()

// Сразу onError
Observable.error<String>(RuntimeException("Error"))
```

### Transformation Operators

**map** — трансформация каждого элемента 1:1

```kotlin
Observable.just("apple", "banana", "orange")
    .map { it.uppercase() }
    .subscribe { println(it) }
// Output: APPLE, BANANA, ORANGE

// Пример с объектами
data class User(val id: String, val name: String)

Observable.just(User("1", "Alice"), User("2", "Bob"))
    .map { it.name }
    .subscribe { println(it) }
// Output: Alice, Bob
```

**flatMap** — трансформация в Observable, merge результатов

```kotlin
// Каждый элемент → Observable
Observable.just("User1", "User2", "User3")
    .flatMap { userId ->
        api.getUser(userId)  // Возвращает Observable<User>
    }
    .subscribe { user -> println(user) }

// Важно: НЕ гарантирует порядок!
Observable.just(1, 2, 3)
    .flatMap { number ->
        Observable.just(number)
            .delay(3 - number.toLong(), TimeUnit.SECONDS)
    }
    .subscribe { println(it) }
// Output может быть: 3, 2, 1 (обратный порядок!)
```

**concatMap** — как flatMap, но сохраняет порядок

```kotlin
Observable.just(1, 2, 3)
    .concatMap { number ->
        Observable.just(number)
            .delay(3 - number.toLong(), TimeUnit.SECONDS)
    }
    .subscribe { println(it) }
// Output ВСЕГДА: 1, 2, 3 (ждёт завершения предыдущего)
```

**switchMap** — отменяет предыдущий Observable при новом emit

```kotlin
// Идеально для search
val searchQuery = PublishSubject.create<String>()

searchQuery
    .debounce(300, TimeUnit.MILLISECONDS)
    .switchMap { query ->
        api.search(query)  // Observable<List<Result>>
    }
    .subscribe { results -> showResults(results) }

searchQuery.onNext("an")      // Запрос 1
searchQuery.onNext("and")     // Запрос 1 отменяется, запрос 2
searchQuery.onNext("android") // Запрос 2 отменяется, запрос 3
// Результат только от последнего запроса
```

**Сравнение flatMap, concatMap, switchMap:**

```kotlin
val source = Observable.just(1, 2, 3)

// flatMap — параллельно, без гарантии порядка
source.flatMap { makeRequest(it) }  // Быстро, но может быть 3, 1, 2

// concatMap — последовательно, с сохранением порядка
source.concatMap { makeRequest(it) }  // Всегда 1, 2, 3, но медленнее

// switchMap — отменяет предыдущие
source.switchMap { makeRequest(it) }  // Только результат от 3
```

**scan** — accumulator (как fold, но emit промежуточные значения)

```kotlin
Observable.just(1, 2, 3, 4, 5)
    .scan { accumulator, value -> accumulator + value }
    .subscribe { println(it) }
// Output: 1, 3, 6, 10, 15

// С начальным значением
Observable.just(1, 2, 3)
    .scan(10) { acc, value -> acc + value }
    .subscribe { println(it) }
// Output: 10, 11, 13, 16
```

**buffer** — группирует элементы в списки

```kotlin
// По количеству
Observable.range(1, 10)
    .buffer(3)
    .subscribe { println(it) }
// Output: [1, 2, 3], [4, 5, 6], [7, 8, 9], [10]

// По времени
Observable.interval(100, TimeUnit.MILLISECONDS)
    .buffer(1, TimeUnit.SECONDS)
    .subscribe { println("Batch: $it") }
```

**groupBy** — группирует по ключу

```kotlin
data class User(val id: String, val city: String)

Observable.just(
    User("1", "Moscow"),
    User("2", "London"),
    User("3", "Moscow"),
    User("4", "Paris")
)
.groupBy { it.city }
.flatMap { group ->
    group.toList()
        .map { users -> group.key to users }
}
.subscribe { (city, users) ->
    println("$city: $users")
}
```

### Filtering Operators

**filter** — фильтрация элементов

```kotlin
Observable.range(1, 10)
    .filter { it % 2 == 0 }
    .subscribe { println(it) }
// Output: 2, 4, 6, 8, 10
```

**take** — первые N элементов

```kotlin
Observable.range(1, 100)
    .take(5)
    .subscribe { println(it) }
// Output: 1, 2, 3, 4, 5
```

**takeLast** — последние N элементов

```kotlin
Observable.range(1, 10)
    .takeLast(3)
    .subscribe { println(it) }
// Output: 8, 9, 10
```

**skip** — пропустить первые N элементов

```kotlin
Observable.range(1, 10)
    .skip(7)
    .subscribe { println(it) }
// Output: 8, 9, 10
```

**debounce** — emit только если прошло N времени без новых элементов

```kotlin
// Идеально для search input
val searchInput = PublishSubject.create<String>()

searchInput
    .debounce(300, TimeUnit.MILLISECONDS)
    .subscribe { query -> performSearch(query) }

// Пользователь печатает "android"
searchInput.onNext("a")       // Не emit (пришёл следующий слишком быстро)
searchInput.onNext("an")      // Не emit
searchInput.onNext("and")     // Не emit
searchInput.onNext("andr")    // Не emit
searchInput.onNext("andro")   // Не emit
searchInput.onNext("android") // Emit через 300ms (если больше ничего не пришло)
```

**throttleFirst** — emit первый элемент, игнорирует остальные в течение N времени

```kotlin
// Идеально для кликов по кнопке
RxView.clicks(button)
    .throttleFirst(1, TimeUnit.SECONDS)
    .subscribe { handleClick() }

// Пользователь кликает 10 раз за секунду
// Обработается только первый клик
```

**throttleLast (sample)** — emit последний элемент за период

```kotlin
Observable.interval(100, TimeUnit.MILLISECONDS)
    .throttleLast(1, TimeUnit.SECONDS)
    .subscribe { println(it) }
// Emit каждую секунду последнее значение
```

**distinctUntilChanged** — пропускает последовательные дубликаты

```kotlin
Observable.just(1, 1, 2, 2, 2, 3, 1, 1)
    .distinctUntilChanged()
    .subscribe { println(it) }
// Output: 1, 2, 3, 1

// Идеально для EditText
RxTextView.textChanges(editText)
    .map { it.toString() }
    .distinctUntilChanged()  // Только если текст реально изменился
    .subscribe { text -> handleTextChange(text) }
```

**distinct** — все уникальные значения

```kotlin
Observable.just(1, 2, 1, 3, 2, 4)
    .distinct()
    .subscribe { println(it) }
// Output: 1, 2, 3, 4
```

**elementAt** — элемент по индексу

```kotlin
Observable.just("A", "B", "C", "D")
    .elementAt(2)
    .subscribe { println(it) }
// Output: C
```

### Combining Operators

**merge** — объединяет несколько Observable в один (параллельно)

```kotlin
val obs1 = Observable.just(1, 2, 3)
val obs2 = Observable.just(4, 5, 6)

Observable.merge(obs1, obs2)
    .subscribe { println(it) }
// Output: 1, 2, 3, 4, 5, 6 (или 1, 4, 2, 5, 3, 6 — не гарантирован порядок)

// Практический пример: загрузка из cache и network
val cache = cacheRepository.getUsers()  // Observable<List<User>>
val network = networkRepository.getUsers()  // Observable<List<User>>

Observable.merge(cache, network)
    .subscribe { users -> showUsers(users) }
// Сначала показываем cache, потом обновляем network данными
```

**concat** — объединяет последовательно (ждёт завершения предыдущего)

```kotlin
val obs1 = Observable.just(1, 2, 3)
val obs2 = Observable.just(4, 5, 6)

Observable.concat(obs1, obs2)
    .subscribe { println(it) }
// Output ВСЕГДА: 1, 2, 3, 4, 5, 6
```

**zip** — комбинирует элементы попарно

```kotlin
val numbers = Observable.just(1, 2, 3)
val letters = Observable.just("A", "B", "C")

Observable.zip(numbers, letters) { num, letter ->
    "$num$letter"
}
.subscribe { println(it) }
// Output: 1A, 2B, 3C

// Практический пример: параллельные запросы
Observable.zip(
    api.getUser("123"),
    api.getUserPosts("123"),
    api.getUserFriends("123")
) { user, posts, friends ->
    UserProfile(user, posts, friends)
}
.subscribe { profile -> showProfile(profile) }
```

**combineLatest** — комбинирует последние значения из каждого Observable

```kotlin
val firstName = PublishSubject.create<String>()
val lastName = PublishSubject.create<String>()

Observable.combineLatest(firstName, lastName) { first, last ->
    "$first $last"
}
.subscribe { println(it) }

firstName.onNext("John")   // Ничего (нет lastName)
lastName.onNext("Doe")     // Output: "John Doe"
firstName.onNext("Jane")   // Output: "Jane Doe"
lastName.onNext("Smith")   // Output: "Jane Smith"

// Популярно для form validation
val email = emailEditText.textChanges()
val password = passwordEditText.textChanges()

Observable.combineLatest(email, password) { e, p ->
    e.isNotEmpty() && p.length >= 6
}
.subscribe { isValid -> loginButton.isEnabled = isValid }
```

**withLatestFrom** — комбинирует с последним значением другого Observable

```kotlin
val clicks = button.clicks()
val text = editText.textChanges()

clicks.withLatestFrom(text) { _, currentText ->
    currentText
}
.subscribe { text -> submitForm(text.toString()) }
// При клике берёт текущий текст из EditText
```

**startWith** — начинает с указанного значения

```kotlin
Observable.just(2, 3, 4)
    .startWith(1)
    .subscribe { println(it) }
// Output: 1, 2, 3, 4

// Практический пример: начальное состояние loading
api.getUsers()
    .map { users -> State.Success(users) as State }
    .startWith(State.Loading)
    .onErrorReturn { State.Error(it) }
    .subscribe { state -> renderState(state) }
```

### Error Handling Operators

**onErrorReturn** — возвращает значение по умолчанию при ошибке

```kotlin
api.getUser("123")
    .onErrorReturn { error ->
        User.EMPTY  // Fallback значение
    }
    .subscribe { user -> showUser(user) }
```

**onErrorResumeNext** — переключается на другой Observable при ошибке

```kotlin
api.getUser("123")
    .onErrorResumeNext { error ->
        cacheRepository.getUser("123")  // Fallback к cache
    }
    .subscribe { user -> showUser(user) }

// Практический пример: network → cache → default
networkRepository.getUsers()
    .onErrorResumeNext { cacheRepository.getUsers() }
    .onErrorReturn { emptyList() }
    .subscribe { users -> showUsers(users) }
```

**retry** — повторяет при ошибке

```kotlin
// Повторить до 3 раз
api.getUser("123")
    .retry(3)
    .subscribe(
        { user -> showUser(user) },
        { error -> showError(error) }
    )

// Повторять пока условие true
api.getUser("123")
    .retry { retryCount, error ->
        retryCount < 3 && error is IOException
    }
    .subscribe { user -> showUser(user) }
```

**retryWhen** — сложная retry логика (exponential backoff)

```kotlin
api.getUser("123")
    .retryWhen { errors ->
        errors.zipWith(Observable.range(1, 3)) { error, retryCount ->
            retryCount
        }
        .flatMap { retryCount ->
            val delay = Math.pow(2.0, retryCount.toDouble()).toLong()
            Observable.timer(delay, TimeUnit.SECONDS)
        }
    }
    .subscribe { user -> showUser(user) }

// Exponential backoff: 2s, 4s, 8s
```

**doOnError** — side-effect при ошибке (не обрабатывает ошибку)

```kotlin
api.getUser("123")
    .doOnError { error ->
        logError(error)  // Logging
        analytics.trackError(error)
    }
    .onErrorReturn { User.EMPTY }
    .subscribe { user -> showUser(user) }
```

### Threading Operators

**subscribeOn** — указывает Scheduler для подписки и upstream работы

```kotlin
Observable.fromCallable {
    // Тяжёлая работа (IO, вычисления)
    loadDataFromDatabase()
}
.subscribeOn(Schedulers.io())  // Выполнится на IO thread
.observeOn(AndroidSchedulers.mainThread())
.subscribe { data -> updateUI(data) }

// ВАЖНО: subscribeOn влияет на весь upstream независимо от позиции
observable
    .map { /* выполнится на io() */ }
    .filter { /* выполнится на io() */ }
    .subscribeOn(Schedulers.io())
    .map { /* выполнится на io() */ }
```

**observeOn** — переключает Scheduler для downstream операций

```kotlin
observable
    .subscribeOn(Schedulers.io())  // Upstream на IO
    .map { /* IO thread */ }
    .observeOn(AndroidSchedulers.mainThread())  // Переключение на Main
    .map { /* Main thread */ }
    .observeOn(Schedulers.computation())  // Переключение на Computation
    .map { /* Computation thread */ }
    .subscribe { /* Computation thread */ }
```

**Правило**: subscribeOn один раз (upstream), observeOn сколько угодно (переключение)

```kotlin
// Типичный паттерн
repository.getData()  // Может быть DB или network
    .subscribeOn(Schedulers.io())  // Выполнение на IO
    .observeOn(AndroidSchedulers.mainThread())  // Результат на Main
    .subscribe { data -> textView.text = data }
```

### Utility Operators

**delay** — задерживает emission

```kotlin
Observable.just(1, 2, 3)
    .delay(2, TimeUnit.SECONDS)
    .subscribe { println(it) }
// Весь поток выйдет через 2 секунды
```

**timeout** — error если нет emission за указанное время

```kotlin
api.getUser("123")
    .timeout(10, TimeUnit.SECONDS)
    .subscribe(
        { user -> showUser(user) },
        { error ->
            if (error is TimeoutException) {
                showTimeout()
            }
        }
    )
```

**doOnNext** — side-effect для каждого элемента

```kotlin
observable
    .doOnNext { item ->
        log("Received: $item")
        analytics.track("item_received", item)
    }
    .subscribe { processItem(it) }
```

**doOnComplete** — side-effect при завершении

```kotlin
observable
    .doOnComplete {
        log("Stream completed")
        hideLoading()
    }
    .subscribe { processItem(it) }
```

**doOnSubscribe** — side-effect при подписке

```kotlin
observable
    .doOnSubscribe {
        log("Subscribed")
        showLoading()
    }
    .subscribe { processItem(it) }
```

**doOnDispose** — side-effect при dispose

```kotlin
observable
    .doOnDispose {
        log("Disposed")
        cleanup()
    }
    .subscribe { processItem(it) }
```

**doFinally** — выполнится в любом случае (onComplete, onError, dispose)

```kotlin
observable
    .doFinally {
        hideLoading()  // Всегда скрыть loading
    }
    .subscribe(
        { showData(it) },
        { showError(it) }
    )
```

## Schedulers — детальный разбор

### Schedulers.io() — для IO-bound операций

**Характеристики:**
- Unbounded thread pool (растёт по мере необходимости)
- Thread reuse через caching
- Idle threads умирают через 60 секунд

**Использование:**
- Network requests
- Database operations
- File IO
- Любые blocking IO операции

```kotlin
// Network request
api.getUsers()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { users -> showUsers(users) }

// Database query
Observable.fromCallable {
    database.userDao().getAllUsers()
}
.subscribeOn(Schedulers.io())
.subscribe { users -> processUsers(users) }
```

### Schedulers.computation() — для CPU-bound операций

**Характеристики:**
- Fixed thread pool (размер = количество CPU cores)
- Для вычислений без blocking
- Не использовать для IO!

**Использование:**
- Математические вычисления
- Обработка изображений
- Parsing больших данных
- Любые CPU-intensive операции без IO

```kotlin
// Image processing
Observable.fromCallable {
    processBitmap(bitmap)
}
.subscribeOn(Schedulers.computation())
.observeOn(AndroidSchedulers.mainThread())
.subscribe { processed -> imageView.setImageBitmap(processed) }

// Сложные вычисления
Observable.range(1, 1000)
    .observeOn(Schedulers.computation())
    .map { calculateComplexFunction(it) }
    .subscribe { result -> processResult(result) }
```

### Schedulers.newThread() — новый thread каждый раз

**Характеристики:**
- Создаёт новый thread для каждой работы
- НЕ reuse threads
- Expensive (overhead создания thread)

**Использование:**
- Почти никогда не используйте!
- Только для специфичных long-running задач
- Предпочитайте io() или computation()

```kotlin
// Плохо
observable.subscribeOn(Schedulers.newThread())  // Создаёт новый thread

// Хорошо
observable.subscribeOn(Schedulers.io())  // Reuse из pool
```

### AndroidSchedulers.mainThread() — UI thread

**Характеристики:**
- Android Main/UI thread
- Используется для обновления UI

**Использование:**
- Обновление View
- Показ Toast/Dialog
- Любая UI операция

```kotlin
api.getUsers()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())  // Переключение на UI thread
    .subscribe { users ->
        // Безопасно обновлять UI
        adapter.setUsers(users)
        progressBar.visibility = View.GONE
    }
```

### Schedulers.trampoline() — текущий thread, sequential

**Характеристики:**
- Выполняется на текущем thread
- Sequential execution (очередь)
- Блокирует текущий thread

**Использование:**
- Testing
- Recursive операции
- Редко в production коде

```kotlin
// Пример с trampoline
Observable.just(1, 2, 3)
    .subscribeOn(Schedulers.trampoline())
    .subscribe { println("$it on ${Thread.currentThread().name}") }
```

### Schedulers.single() — один shared thread

**Характеристики:**
- Один thread для всех операций
- Sequential execution
- Полезно для serialization

**Использование:**
- Операции требующие строгую последовательность
- Shared mutable state
- Event bus

```kotlin
// Все операции выполнятся последовательно на одном thread
val scheduler = Schedulers.single()

observable1.subscribeOn(scheduler).subscribe()
observable2.subscribeOn(scheduler).subscribe()
```

### Кастомный Scheduler из Executor

```kotlin
val executor = Executors.newFixedThreadPool(4)
val customScheduler = Schedulers.from(executor)

observable
    .subscribeOn(customScheduler)
    .subscribe { /* работа на custom thread pool */ }

// Важно: закрыть executor когда не нужен
executor.shutdown()
```

### subscribeOn vs observeOn — критические различия

**subscribeOn**:
- Влияет на весь upstream chain
- Обычно вызывается один раз
- Позиция не важна (влияет на весь upstream)
- Определяет где произойдёт подписка и upstream работа

```kotlin
observable
    .map { "A" }  // Выполнится на io()
    .subscribeOn(Schedulers.io())
    .map { "B" }  // Выполнится на io()

// То же самое
observable
    .subscribeOn(Schedulers.io())
    .map { "A" }  // Выполнится на io()
    .map { "B" }  // Выполнится на io()
```

**observeOn**:
- Влияет только на downstream операции
- Можно вызывать много раз (переключение thread)
- Позиция важна!

```kotlin
observable
    .map { "A" }  // io thread
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .map { "B" }  // main thread
    .observeOn(Schedulers.computation())
    .map { "C" }  // computation thread
```

**Типичный паттерн Android:**

```kotlin
// Правильно
repository.getData()
    .subscribeOn(Schedulers.io())  // Работа на IO thread
    .observeOn(AndroidSchedulers.mainThread())  // Результат на Main thread
    .subscribe { updateUI(it) }

// Неправильно
repository.getData()
    .observeOn(AndroidSchedulers.mainThread())  // Бесполезно
    .subscribeOn(Schedulers.io())  // getData выполнится на IO
    .subscribe { updateUI(it) }  // updateUI на IO thread! Crash!
```

## Lifecycle и Disposal — критически важно

### Disposable interface

**Основа управления ресурсами:**

```kotlin
val disposable: Disposable = observable.subscribe { item ->
    println(item)
}

// Позже отменить подписку
disposable.dispose()

// Проверка
if (!disposable.isDisposed) {
    disposable.dispose()
}
```

### CompositeDisposable — группировка подписок

**Стандартный подход в Android:**

```kotlin
class MainActivity : AppCompatActivity() {
    private val compositeDisposable = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val disposable1 = api.getUsers()
            .subscribe { users -> showUsers(users) }

        val disposable2 = api.getPosts()
            .subscribe { posts -> showPosts(posts) }

        // Добавить в группу
        compositeDisposable.add(disposable1)
        compositeDisposable.add(disposable2)

        // Или сразу
        api.getComments()
            .subscribe { comments -> showComments(comments) }
            .let { compositeDisposable.add(it) }
    }

    override fun onDestroy() {
        super.onDestroy()
        compositeDisposable.dispose()  // Отменит ВСЕ подписки
    }
}
```

### clear() vs dispose() — важное различие!

```kotlin
val composite = CompositeDisposable()

// dispose() — освобождает все ресурсы, больше нельзя использовать
composite.dispose()
composite.add(disposable)  // IllegalStateException! Composite disposed

// clear() — очищает, но можно использовать дальше
composite.clear()
composite.add(disposable)  // OK!
```

**Когда использовать:**
- **dispose()** — в onDestroy, когда объект уничтожается навсегда
- **clear()** — в onStop/onPause, когда возможно повторное использование

```kotlin
class MyFragment : Fragment() {
    private val disposables = CompositeDisposable()

    override fun onStart() {
        super.onStart()
        // Подписываемся
        api.getUsers()
            .subscribe { users -> showUsers(users) }
            .let { disposables.add(it) }
    }

    override fun onStop() {
        super.onStop()
        disposables.clear()  // Очищаем, но можем использовать в onStart снова
    }

    override fun onDestroyView() {
        super.onDestroyView()
        disposables.dispose()  // Окончательно уничтожаем
    }
}
```

### Где вызывать dispose — по типу компонента

**Activity:**

```kotlin
class UserActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.users
            .subscribe { users -> adapter.setUsers(users) }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        super.onDestroy()
        disposables.dispose()  // Отменить все подписки
    }
}
```

**Fragment:**

```kotlin
class UserFragment : Fragment() {
    private val disposables = CompositeDisposable()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.users
            .subscribe { users -> adapter.setUsers(users) }
            .let { disposables.add(it) }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        disposables.dispose()  // ВАЖНО: в onDestroyView, не onDestroy!
    }
}
```

**ViewModel:**

```kotlin
class UserViewModel : ViewModel() {
    private val disposables = CompositeDisposable()

    fun loadUsers() {
        repository.getUsers()
            .subscribe { users -> /* ... */ }
            .let { disposables.add(it) }
    }

    override fun onCleared() {
        super.onCleared()
        disposables.dispose()  // ViewModel уничтожается
    }
}
```

### AutoDispose library (Uber) — автоматический lifecycle management

**Проблема**: легко забыть dispose, особенно в сложных экранах

**Решение**: AutoDispose автоматически dispose при lifecycle events

```kotlin
// Gradle
implementation 'com.uber.autodispose:autodispose:1.4.0'
implementation 'com.uber.autodispose:autodispose-android:1.4.0'
implementation 'com.uber.autodispose:autodispose-androidx-lifecycle:1.4.0'

// Activity/Fragment
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        api.getUsers()
            .autoDispose(AndroidLifecycleScopeProvider.from(this))
            .subscribe { users -> showUsers(users) }

        // Автоматически dispose в onDestroy
        // Не нужен CompositeDisposable!
    }
}

// С ViewModel
class UserViewModel : ViewModel() {
    private val scopeProvider = ScopeProvider {
        CompletableSource.fromAction { /* onCleared */ }
    }

    fun loadUsers() {
        repository.getUsers()
            .autoDispose(scopeProvider)
            .subscribe { users -> /* ... */ }
    }
}
```

### RxLifecycle (deprecated, но встречается в legacy коде)

**Старый подход** от Trello, сейчас не рекомендуется:

```kotlin
class UserActivity : RxAppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        api.getUsers()
            .compose(bindToLifecycle())  // Автоматический dispose
            .subscribe { users -> showUsers(users) }
    }
}
```

**Почему deprecated:**
- Требует наследование от RxActivity/RxFragment
- Магическое поведение (неясно когда dispose)
- AutoDispose решает ту же задачу лучше

## Anti-patterns и Memory Leaks — что НЕ делать

### 1. Forgotten Disposable — Activity leak

**Проблема:**

```kotlin
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: подписка никогда не отменяется
        Observable.interval(1, TimeUnit.SECONDS)
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { count ->
                textView.text = "Count: $count"
            }

        // Activity не может быть уничтожена!
        // Observable продолжает работать и держит ссылку на Activity
    }
}
```

**Решение:**

```kotlin
class UserActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Observable.interval(1, TimeUnit.SECONDS)
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { count -> textView.text = "Count: $count" }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        super.onDestroy()
        disposables.dispose()  // Отменяем подписку
    }
}
```

### 2. Lambda capturing `this` — implicit reference leak

**Проблема:**

```kotlin
class UserActivity : AppCompatActivity() {
    private val compositeDisposable = CompositeDisposable()
    private var cachedData: List<User>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: lambda захватывает this
        api.getUsers()
            .subscribe { users ->
                cachedData = users  // Обращение к полю Activity
                showUsers(users)    // Вызов метода Activity
            }
            .let { compositeDisposable.add(it) }

        // Lambda держит ссылку на Activity через captured this
    }
}
```

**Детектирование:**

```kotlin
// Kotlin decompiled:
api.getUsers().subscribe(new Action1<List<User>>() {
    @Override
    public void call(List<User> users) {
        UserActivity.this.cachedData = users;  // Явная ссылка на Activity
        UserActivity.this.showUsers(users);
    }
});
```

**Решение:**

```kotlin
class UserActivity : AppCompatActivity() {
    private val compositeDisposable = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Хорошо: используем WeakReference
        val weakThis = WeakReference(this)

        api.getUsers()
            .subscribe { users ->
                weakThis.get()?.let { activity ->
                    activity.showUsers(users)
                }
            }
            .let { compositeDisposable.add(it) }

        // Или просто dispose правильно
        api.getUsers()
            .subscribe { users -> showUsers(users) }
            .let { compositeDisposable.add(it) }
    }

    override fun onDestroy() {
        super.onDestroy()
        compositeDisposable.dispose()  // Главное — dispose!
    }
}
```

### 3. Singleton с CompositeDisposable

**Проблема:**

```kotlin
object NetworkManager {
    private val compositeDisposable = CompositeDisposable()  // ПЛОХО!

    fun fetchData(callback: (Data) -> Unit) {
        api.getData()
            .subscribe { data -> callback(data) }
            .let { compositeDisposable.add(it) }
    }

    // CompositeDisposable никогда не очищается!
    // Накапливает подписки и держит ссылки
}

// Использование
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        NetworkManager.fetchData { data ->
            updateUI(data)  // Activity leak!
        }
    }
}
```

**Решение 1: возвращать Disposable**

```kotlin
object NetworkManager {
    fun fetchData(): Single<Data> {
        return api.getData()  // Caller управляет подпиской
    }
}

class MyActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        NetworkManager.fetchData()
            .subscribe { data -> updateUI(data) }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        disposables.dispose()
    }
}
```

**Решение 2: Scoped singleton**

```kotlin
class NetworkManager {
    private val disposables = CompositeDisposable()

    fun fetchData(callback: (Data) -> Unit) {
        api.getData()
            .subscribe { data -> callback(data) }
            .let { disposables.add(it) }
    }

    fun cleanup() {
        disposables.clear()
    }
}

// Dependency injection — каждой Activity свой instance
class MyActivity : AppCompatActivity() {
    @Inject lateinit var networkManager: NetworkManager

    override fun onDestroy() {
        networkManager.cleanup()
    }
}
```

### 4. Hot Observable leaks (Subject)

**Проблема:**

```kotlin
object EventBus {
    private val subject = PublishSubject.create<Event>()  // Hot Observable

    fun subscribe(observer: Observer<Event>) {
        subject.subscribe(observer)  // ПЛОХО: нет dispose!
    }

    fun publish(event: Event) {
        subject.onNext(event)
    }
}

class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        EventBus.subscribe { event ->
            handleEvent(event)  // Activity leak!
        }
    }
}
```

**Решение:**

```kotlin
object EventBus {
    private val subject = PublishSubject.create<Event>()

    fun subscribe(): Observable<Event> {
        return subject  // Возвращаем Observable, caller управляет
    }

    fun publish(event: Event) {
        subject.onNext(event)
    }
}

class MyActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        EventBus.subscribe()
            .subscribe { event -> handleEvent(event) }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        disposables.dispose()
    }
}
```

### 5. Неправильный выбор operator

**flatMap когда нужен switchMap:**

```kotlin
// ПЛОХО: search с flatMap
searchEditText.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .flatMap { query ->
        api.search(query.toString())  // Все запросы выполняются параллельно
    }
    .subscribe { results -> showResults(results) }

// Пользователь печатает "android"
// Запросы: "a", "an", "and", "andr", "andro", "android"
// ВСЕ 6 запросов выполняются, результаты приходят в random порядке
```

**Решение: switchMap**

```kotlin
// ХОРОШО: search с switchMap
searchEditText.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .switchMap { query ->
        api.search(query.toString())  // Отменяет предыдущие запросы
    }
    .subscribe { results -> showResults(results) }

// Выполнится только последний запрос "android"
```

**merge когда нужен concat:**

```kotlin
// ПЛОХО: последовательные операции с merge
val step1 = database.insertUser(user)
val step2 = database.updateUserProfile(user.id)
val step3 = database.notifyUserCreated(user.id)

Observable.merge(step1, step2, step3)  // Параллельно! Порядок не гарантирован
    .subscribe()

// step2 может выполниться раньше step1!
```

**Решение: concat**

```kotlin
// ХОРОШО: последовательные операции с concat
Observable.concat(step1, step2, step3)  // Строго последовательно
    .subscribe()
```

### 6. subscribeOn после observeOn

**Проблема:**

```kotlin
// ПЛОХО: subscribeOn после observeOn бесполезен
api.getUsers()
    .observeOn(AndroidSchedulers.mainThread())  // Переключение на main
    .subscribeOn(Schedulers.io())  // Бесполезно! Уже на main thread
    .subscribe { users -> updateUI(users) }

// api.getUsers() выполнится на main thread!
```

**Решение:**

```kotlin
// ХОРОШО: subscribeOn до observeOn
api.getUsers()
    .subscribeOn(Schedulers.io())  // Запрос на IO thread
    .observeOn(AndroidSchedulers.mainThread())  // Результат на main thread
    .subscribe { users -> updateUI(users) }
```

### 7. Blocking operators на main thread

**Проблема:**

```kotlin
// ПЛОХО: blockingGet на main thread
button.setOnClickListener {
    try {
        val user = api.getUser("123")
            .blockingGet()  // БЛОКИРУЕТ main thread!

        showUser(user)
    } catch (e: Exception) {
        showError(e)
    }
}
```

**Решение:**

```kotlin
// ХОРОШО: асинхронная подписка
button.setOnClickListener {
    api.getUser("123")
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe(
            { user -> showUser(user) },
            { error -> showError(error) }
        )
        .let { disposables.add(it) }
}
```

### 8. Неправильный error handling в chain

**Проблема:**

```kotlin
// ПЛОХО: onErrorReturn слишком рано
api.getUser("123")
    .onErrorReturn { User.EMPTY }  // Скрывает ошибку
    .flatMap { user ->
        api.getUserPosts(user.id)  // Передаст EMPTY user, неправильный id
    }
    .subscribe { posts -> showPosts(posts) }
```

**Решение:**

```kotlin
// ХОРОШО: правильная последовательность error handling
api.getUser("123")
    .flatMap { user ->
        api.getUserPosts(user.id)
    }
    .onErrorReturn { emptyList() }  // Обработка ошибки в конце
    .subscribe { posts -> showPosts(posts) }

// Или отдельная обработка ошибок для каждого запроса
api.getUser("123")
    .onErrorResumeNext { error ->
        if (error is NetworkException) {
            cacheRepository.getUser("123")
        } else {
            Single.error(error)
        }
    }
    .flatMap { user ->
        api.getUserPosts(user.id)
            .onErrorReturn { emptyList() }
    }
    .subscribe { posts -> showPosts(posts) }
```

## Практические паттерны

### Repository pattern с RxJava

**Классическая архитектура:**

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao,
    private val preferences: SharedPreferences
) {
    // Single source of truth pattern
    fun getUsers(forceRefresh: Boolean = false): Observable<List<User>> {
        return if (forceRefresh) {
            fetchFromNetwork()
        } else {
            getCached()
                .switchIfEmpty(fetchFromNetwork())
        }
    }

    private fun getCached(): Observable<List<User>> {
        return userDao.getAllUsers()
            .filter { it.isNotEmpty() }
            .toObservable()
    }

    private fun fetchFromNetwork(): Observable<List<User>> {
        return apiService.getUsers()
            .doOnSuccess { users ->
                // Cache result
                userDao.insertAll(users)
            }
            .toObservable()
    }

    // Network + Cache merge pattern
    fun getUsersWithCache(): Observable<List<User>> {
        val cache = userDao.getAllUsers()
            .filter { it.isNotEmpty() }
            .toObservable()

        val network = apiService.getUsers()
            .doOnSuccess { users -> userDao.insertAll(users) }
            .toObservable()

        return Observable.concat(cache, network)
            .distinctUntilChanged()
    }

    // Single user with fallback
    fun getUser(id: String): Single<User> {
        return apiService.getUser(id)
            .onErrorResumeNext { error ->
                if (error is IOException) {
                    userDao.getUserById(id)
                        .toSingle()
                } else {
                    Single.error(error)
                }
            }
    }
}
```

### Error handling strategy с sealed class Result

**Result wrapper:**

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Extension для Observable
fun <T> Observable<T>.toResult(): Observable<Result<T>> {
    return this
        .map<Result<T>> { Result.Success(it) }
        .onErrorReturn { Result.Error(it) }
        .startWith(Result.Loading)
}

// Использование
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val compositeDisposable = CompositeDisposable()

    private val _usersState = PublishSubject.create<Result<List<User>>>()
    val usersState: Observable<Result<List<User>>> = _usersState

    fun loadUsers() {
        repository.getUsers()
            .toResult()
            .subscribe { result ->
                _usersState.onNext(result)
            }
            .let { compositeDisposable.add(it) }
    }

    override fun onCleared() {
        compositeDisposable.dispose()
    }
}

// Activity
class UserActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.usersState
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { result ->
                when (result) {
                    is Result.Loading -> showLoading()
                    is Result.Success -> showUsers(result.data)
                    is Result.Error -> showError(result.exception)
                }
            }
            .let { disposables.add(it) }

        viewModel.loadUsers()
    }

    override fun onDestroy() {
        disposables.dispose()
        super.onDestroy()
    }
}
```

### Caching с replay/share

**replay operator:**

```kotlin
// Без replay — каждый subscriber запускает новый network request
val users: Observable<List<User>> = apiService.getUsers().toObservable()

users.subscribe { println("Subscriber 1: $it") }  // Network request 1
users.subscribe { println("Subscriber 2: $it") }  // Network request 2

// С replay — один network request, результат кэшируется
val usersWithCache: Observable<List<User>> = apiService.getUsers()
    .toObservable()
    .replay(1)  // Cache последний результат
    .autoConnect()  // Автоматический connect при первой подписке

usersWithCache.subscribe { println("Subscriber 1: $it") }  // Network request
usersWithCache.subscribe { println("Subscriber 2: $it") }  // Из cache
```

**share operator:**

```kotlin
// share = publish + refCount
val shared = Observable.interval(1, TimeUnit.SECONDS)
    .share()

// Первая подписка — запускает Observable
val disposable1 = shared.subscribe { println("Sub 1: $it") }

Thread.sleep(3000)

// Вторая подписка — подключается к существующему Observable
val disposable2 = shared.subscribe { println("Sub 2: $it") }

// Обе подписки получают одинаковые значения
```

**Практический пример: кэширование с TTL**

```kotlin
class UserRepository(private val api: ApiService) {
    private var cachedUsers: Observable<List<User>>? = null
    private var cacheTime: Long = 0
    private val cacheTtl = 5 * 60 * 1000  // 5 минут

    fun getUsers(): Observable<List<User>> {
        val now = System.currentTimeMillis()

        if (cachedUsers == null || now - cacheTime > cacheTtl) {
            cachedUsers = api.getUsers()
                .toObservable()
                .replay(1)
                .autoConnect()

            cacheTime = now
        }

        return cachedUsers!!
    }
}
```

### Form validation с combineLatest

**Сложная форма с множеством полей:**

```kotlin
class RegistrationActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        // Observables для каждого поля
        val email = RxTextView.textChanges(emailEditText)
            .map { it.toString() }
            .distinctUntilChanged()

        val password = RxTextView.textChanges(passwordEditText)
            .map { it.toString() }
            .distinctUntilChanged()

        val passwordConfirm = RxTextView.textChanges(passwordConfirmEditText)
            .map { it.toString() }
            .distinctUntilChanged()

        val termsAccepted = RxCompoundButton.checkedChanges(termsCheckbox)

        // Validation rules
        val isEmailValid = email
            .map { android.util.Patterns.EMAIL_ADDRESS.matcher(it).matches() }

        val isPasswordValid = password
            .map { it.length >= 8 }

        val doPasswordsMatch = Observable.combineLatest(
            password,
            passwordConfirm
        ) { pass, confirm ->
            pass == confirm && pass.isNotEmpty()
        }

        // Combine все validations
        val isFormValid = Observable.combineLatest(
            isEmailValid,
            isPasswordValid,
            doPasswordsMatch,
            termsAccepted
        ) { emailOk, passOk, matchOk, termsOk ->
            emailOk && passOk && matchOk && termsOk
        }

        // Enable/disable button
        isFormValid
            .subscribe { isValid ->
                registerButton.isEnabled = isValid
            }
            .let { disposables.add(it) }

        // Show error messages
        isEmailValid
            .skip(1)  // Пропустить initial значение
            .subscribe { isValid ->
                emailEditText.error = if (isValid) null else "Invalid email"
            }
            .let { disposables.add(it) }

        isPasswordValid
            .skip(1)
            .subscribe { isValid ->
                passwordEditText.error = if (isValid) null else "Min 8 characters"
            }
            .let { disposables.add(it) }

        doPasswordsMatch
            .skip(1)
            .subscribe { match ->
                passwordConfirmEditText.error = if (match) null else "Passwords don't match"
            }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        disposables.dispose()
        super.onDestroy()
    }
}
```

### Search с debounce + switchMap + distinctUntilChanged

**Оптимальный search pattern:**

```kotlin
class SearchActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_search)

        RxTextView.textChanges(searchEditText)
            .map { it.toString().trim() }
            .filter { it.length >= 3 }  // Минимум 3 символа
            .debounce(300, TimeUnit.MILLISECONDS)  // Ждём паузу в наборе
            .distinctUntilChanged()  // Только если текст изменился
            .switchMap { query ->
                if (query.isEmpty()) {
                    Observable.just(emptyList<SearchResult>())
                } else {
                    searchRepository.search(query)
                        .toObservable()
                        .onErrorReturn { emptyList() }
                }
            }
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { results ->
                adapter.setResults(results)
            }
            .let { disposables.add(it) }
    }

    override fun onDestroy() {
        disposables.dispose()
        super.onDestroy()
    }
}

// Repository
class SearchRepository(private val api: ApiService) {
    fun search(query: String): Single<List<SearchResult>> {
        return api.search(query)
            .subscribeOn(Schedulers.io())
            .timeout(10, TimeUnit.SECONDS)
            .retry { retryCount, error ->
                retryCount < 2 && error is IOException
            }
    }
}
```

### Retry with exponential backoff

**Сложная retry стратегия:**

```kotlin
class NetworkRepository(private val api: ApiService) {

    fun getUserWithRetry(id: String): Single<User> {
        return api.getUser(id)
            .retryWhen { errors ->
                errors.zipWith(Observable.range(1, 4)) { error, retryCount ->
                    RetryInfo(error, retryCount)
                }
                .flatMap { info ->
                    when {
                        info.retryCount > 3 -> Observable.error(info.error)
                        info.error !is IOException -> Observable.error(info.error)
                        else -> {
                            val delay = Math.pow(2.0, info.retryCount.toDouble()).toLong()
                            println("Retry ${info.retryCount} after ${delay}s")
                            Observable.timer(delay, TimeUnit.SECONDS)
                        }
                    }
                }
            }
    }

    data class RetryInfo(val error: Throwable, val retryCount: Int)
}

// Более продвинутый вариант с jitter
fun <T> Single<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelay: Long = 1,
    maxDelay: Long = 10,
    timeUnit: TimeUnit = TimeUnit.SECONDS,
    retryPredicate: (Throwable) -> Boolean = { it is IOException }
): Single<T> {
    return this.retryWhen { errors ->
        errors.zipWith(Observable.range(1, maxRetries + 1)) { error, attempt ->
            if (attempt > maxRetries || !retryPredicate(error)) {
                throw error
            }

            // Exponential backoff с jitter
            val delay = minOf(
                initialDelay * (1 shl (attempt - 1)),  // 2^(n-1)
                maxDelay
            )
            val jitter = Random.nextLong(0, delay / 2)

            println("Retry $attempt after ${delay + jitter}${timeUnit.name}")

            Observable.timer(delay + jitter, timeUnit)
        }.flatMap { it }
    }
}

// Использование
api.getUser("123")
    .retryWithExponentialBackoff(
        maxRetries = 5,
        initialDelay = 1,
        maxDelay = 30,
        retryPredicate = { it is IOException || it is SocketTimeoutException }
    )
    .subscribe(
        { user -> showUser(user) },
        { error -> showError(error) }
    )
```

## Миграция RxJava → Coroutines

### Observable → Flow mapping

**Базовое преобразование:**

```kotlin
// RxJava
val observable: Observable<User> = repository.getUsers()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())

observable.subscribe { users ->
    updateUI(users)
}

// Coroutines + Flow
val flow: Flow<User> = repository.getUsers()
    .flowOn(Dispatchers.IO)

lifecycleScope.launch {
    flow.collect { users ->
        updateUI(users)
    }
}
```

### Single → suspend function

**Network requests:**

```kotlin
// RxJava
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") id: String): Single<User>
}

api.getUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> showUser(user) },
        { error -> showError(error) }
    )

// Coroutines
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User
}

lifecycleScope.launch {
    try {
        val user = withContext(Dispatchers.IO) {
            api.getUser("123")
        }
        showUser(user)
    } catch (e: Exception) {
        showError(e)
    }
}
```

### Operators equivalents

| RxJava | Kotlin Flow | Заметки |
|--------|-------------|---------|
| `map` | `map` | Идентичны |
| `flatMap` | `flatMapMerge` | Flow не гарантирует порядок |
| `concatMap` | `flatMapConcat` | Последовательное выполнение |
| `switchMap` | `flatMapLatest` | Отмена предыдущих |
| `filter` | `filter` | Идентичны |
| `take` | `take` | Идентичны |
| `skip` | `drop` | Разные названия |
| `debounce` | `debounce` | Идентичны |
| `throttleFirst` | `sample` | Sample в Flow ближе к throttleLast |
| `distinctUntilChanged` | `distinctUntilChanged` | Идентичны |
| `zip` | `zip` | Идентичны |
| `combineLatest` | `combine` | Разные названия |
| `merge` | `merge` | Идентичны |
| `concat` | `concatenate` | Разные названия |
| `scan` | `scan` | Идентичны |
| `subscribeOn` | `flowOn` | Flow меняет только upstream |
| `observeOn` | `flowOn` + `withContext` | Flow проще |

**Примеры миграции:**

```kotlin
// RxJava: flatMap
observable
    .flatMap { user -> api.getUserPosts(user.id) }
    .subscribe()

// Flow: flatMapMerge
flow
    .flatMapMerge { user -> api.getUserPosts(user.id) }
    .collect()

// RxJava: switchMap
searchQuery
    .switchMap { query -> api.search(query) }
    .subscribe()

// Flow: flatMapLatest
searchQuery
    .flatMapLatest { query -> api.search(query) }
    .collect()

// RxJava: combineLatest
Observable.combineLatest(email, password) { e, p ->
    e.isNotEmpty() && p.length >= 6
}.subscribe()

// Flow: combine
combine(email, password) { e, p ->
    e.isNotEmpty() && p.length >= 6
}.collect()

// RxJava: debounce + switchMap
searchEditText.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .switchMap { query -> api.search(query.toString()) }
    .subscribe()

// Flow: debounce + flatMapLatest
searchEditText.textChanges()
    .debounce(300)
    .flatMapLatest { query -> api.search(query.toString()) }
    .collect()
```

### Постепенная миграция strategy

**Phase 1: Добавить Coroutines dependency**

```kotlin
// build.gradle.kts
dependencies {
    // Existing RxJava
    implementation("io.reactivex.rxjava3:rxjava:3.1.8")
    implementation("io.reactivex.rxjava3:rxandroid:3.0.2")

    // Add Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Interop library
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:1.7.3")
}
```

**Phase 2: Использовать interop для постепенной миграции**

```kotlin
// kotlinx-coroutines-rx3 предоставляет converters

// RxJava → Coroutines
val single: Single<User> = api.getUser("123")
val deferred: Deferred<User> = single.await()  // Extension

lifecycleScope.launch {
    try {
        val user = single.await()  // Suspend call
        showUser(user)
    } catch (e: Exception) {
        showError(e)
    }
}

// Observable → Flow
val observable: Observable<String> = searchEditText.textChanges()
val flow: Flow<CharSequence> = observable.asFlow()

lifecycleScope.launch {
    flow.collect { text ->
        handleTextChange(text.toString())
    }
}

// Coroutines → RxJava (если нужно для legacy кода)
suspend fun getUser(): User = api.getUser("123")

val single: Single<User> = GlobalScope.async {
    getUser()
}.asSingle(Dispatchers.IO)
```

**Phase 3: Постепенно мигрировать слоями**

```kotlin
// 1. Начните с Data layer (Repository)
class UserRepository(private val api: ApiService, private val dao: UserDao) {
    // Новый метод с Coroutines
    suspend fun getUsersSuspend(): List<User> = withContext(Dispatchers.IO) {
        try {
            val users = api.getUsers()  // suspend fun
            dao.insertAll(users)
            users
        } catch (e: Exception) {
            dao.getAllUsers()
        }
    }

    // Старый метод с RxJava (deprecated, для совместимости)
    @Deprecated("Use getUsersSuspend")
    fun getUsers(): Single<List<User>> {
        return GlobalScope.async {
            getUsersSuspend()
        }.asSingle(Dispatchers.IO)
    }
}

// 2. Мигрировать ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    // Новый подход
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsersSuspend()
                _users.value = users
            } catch (e: Exception) {
                // Handle error
            }
        }
    }

    // onCleared автоматически отменит все viewModelScope jobs
}

// 3. Обновить UI layer
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)
            }
        }

        viewModel.loadUsers()
    }
}
```

**Phase 4: Убрать RxJava dependencies**

После полной миграции:

```kotlin
// build.gradle.kts
dependencies {
    // Remove
    // implementation("io.reactivex.rxjava3:rxjava:3.1.8")
    // implementation("io.reactivex.rxjava3:rxandroid:3.0.2")
    // implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:1.7.3")

    // Keep
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

## Когда RxJava всё ещё актуален (2024)

### 1. Complex event streams

**Сценарий**: множественные источники событий, сложная композиция

```kotlin
// Сложная комбинация UI events
class FormValidator {
    fun observeFormValidity(
        email: Observable<String>,
        password: Observable<String>,
        passwordConfirm: Observable<String>,
        terms: Observable<Boolean>,
        newsletter: Observable<Boolean>
    ): Observable<ValidationResult> {

        return Observable.combineLatest(
            email.map { validateEmail(it) },
            password.map { validatePassword(it) },
            Observable.combineLatest(password, passwordConfirm) { p, c ->
                p == c && p.isNotEmpty()
            },
            terms,
            newsletter
        ) { emailValid, passValid, match, termsAccepted, newsletterSubscribed ->
            ValidationResult(
                isValid = emailValid && passValid && match && termsAccepted,
                emailError = if (emailValid) null else "Invalid email",
                passwordError = if (passValid) null else "Weak password",
                matchError = if (match) null else "Passwords don't match",
                marketingConsent = newsletterSubscribed
            )
        }
    }
}

// В Flow это более verbose
```

### 2. Backpressure scenarios

**Сценарий**: чтение большого файла, streaming данных

```kotlin
// RxJava Flowable с backpressure
class LogFileReader {
    fun readLogs(file: File): Flowable<LogEntry> {
        return Flowable.create({ emitter ->
            file.bufferedReader().use { reader ->
                reader.lineSequence()
                    .forEach { line ->
                        if (emitter.isCancelled) return@forEach

                        val entry = parseLogEntry(line)
                        emitter.onNext(entry)
                    }
                emitter.onComplete()
            }
        }, BackpressureStrategy.BUFFER)
    }
}

// Flow пока не имеет такого explicit backpressure control
```

### 3. Existing large codebase

**Реальность**: миграция большого проекта требует времени и ресурсов

```kotlin
// Проект с 500+ RxJava chains
// Миграция может занять месяцы
// Выгоднее поддерживать RxJava и постепенно мигрировать

class LegacyProject {
    // 1000+ методов возвращают Observable/Single/Completable
    // 500+ ViewModels с RxJava
    // Вся архитектура построена вокруг RxJava

    // Решение: продолжать использовать RxJava
    // Новые фичи на Coroutines через interop
}
```

### 4. Team expertise

**Фактор**: команда с 5+ годами опыта в RxJava

```kotlin
// Команда знает все нюансы RxJava
// Производительность высокая
// Меньше багов благодаря опыту

// Переход на Coroutines = временное снижение productivity
// Иногда выгоднее остаться на знакомом стеке
```

### 5. Specific operators отсутствующие в Flow

**Примеры:**

```kotlin
// replay с autoConnect — сложнее в Flow
val cached = observable
    .replay(1)
    .autoConnect()

// Hot/Cold conversion — проще в RxJava
val hot = coldObservable.share()

// Сложные retry стратегии
observable.retryWhen { errors ->
    errors.zipWith(Observable.range(1, 3)) { e, i -> i }
        .flatMap { Observable.timer(it.toLong(), TimeUnit.SECONDS) }
}

// window/buffer с time/count комбинациями
observable
    .buffer(100, TimeUnit.MILLISECONDS, 10)  // Буфер по времени ИЛИ количеству
```

### Рекомендации по выбору (2024)

**Используйте RxJava если:**
- Существующий проект уже на RxJava
- Команда экспертна в RxJava
- Сложные event-driven системы с множеством источников
- Нужен explicit backpressure control
- Специфичные operators критичны для бизнес-логики

**Используйте Coroutines + Flow если:**
- Новый проект
- Команда новичок в reactive programming
- Простые асинхронные операции
- Хотите first-party Google support
- Нужна простота и меньше boilerplate

**Hybrid подход:**
- Data layer: Coroutines (простота)
- Complex UI logic: RxJava (мощные operators)
- Используйте kotlinx-coroutines-rx3 для interop

## Проверь себя

### Вопрос 1: Чем flatMap отличается от switchMap?

<details>
<summary>Ответ</summary>

**flatMap**:
- Выполняет все inner Observable параллельно
- НЕ гарантирует порядок результатов
- НЕ отменяет предыдущие Observable при новом emit
- Подходит для независимых операций

**switchMap**:
- Отменяет предыдущий inner Observable при новом emit
- Гарантирует, что обрабатывается только последний
- Идеален для search, autocomplete
- Экономит ресурсы за счёт отмены устаревших операций

```kotlin
// flatMap — все 3 запроса выполнятся
searchQuery
    .flatMap { api.search(it) }  // Запросы для "a", "an", "and" все выполнятся

// switchMap — только последний запрос
searchQuery
    .switchMap { api.search(it) }  // Только "and" выполнится, "a" и "an" отменятся
```
</details>

### Вопрос 2: Когда использовать Flowable вместо Observable?

<details>
<summary>Ответ</summary>

**Используйте Flowable когда:**
- Producer генерирует данные быстрее, чем Consumer обрабатывает
- Работаете с большими объёмами данных (файлы, database streaming)
- Нужен explicit control над backpressure
- Читаете 10,000+ элементов

**Используйте Observable когда:**
- Небольшое количество элементов (< 1000)
- UI events (clicks, text changes)
- Producer и Consumer примерно одинаковой скорости
- Backpressure не критичен

```kotlin
// Observable — UI events
RxView.clicks(button)  // Пользователь не сделает 10000 кликов в секунду

// Flowable — чтение файла
Flowable.create({ emitter ->
    file.forEachLine { line ->
        emitter.onNext(line)  // Может быть миллионы строк
    }
}, BackpressureStrategy.BUFFER)
```
</details>

### Вопрос 3: Почему subscribeOn можно вызвать только один раз?

<details>
<summary>Ответ</summary>

**Технически** можно вызвать несколько раз, но эффект будет только от первого вызова.

**Причина**: subscribeOn влияет на весь upstream chain, определяя где произойдёт **подписка** и выполнение source Observable.

```kotlin
observable
    .subscribeOn(Schedulers.computation())  // Эффект: upstream на computation
    .map { /* выполнится на computation */ }
    .subscribeOn(Schedulers.io())  // ИГНОРИРУЕТСЯ!
    .map { /* выполнится на computation */ }

// Правило: один subscribeOn для upstream, много observeOn для downstream

observable
    .subscribeOn(Schedulers.io())  // Upstream на IO
    .observeOn(AndroidSchedulers.mainThread())  // Downstream на Main
    .observeOn(Schedulers.computation())  // Дальше на Computation
```

**Почему так работает**: subscribeOn propagates вверх по chain, первый который встретится при подписке — определяет Scheduler.
</details>

### Вопрос 4: Чем clear() отличается от dispose()?

<details>
<summary>Ответ</summary>

**dispose()**:
- Отменяет все подписки в CompositeDisposable
- Переводит CompositeDisposable в disposed state
- После dispose() нельзя добавлять новые Disposable (IllegalStateException)
- Используйте в onDestroy

**clear()**:
- Отменяет все подписки
- НЕ меняет state CompositeDisposable
- После clear() можно добавлять новые Disposable
- Используйте в onStop/onPause

```kotlin
val composite = CompositeDisposable()

// Сценарий 1: onStop/onStart
override fun onStop() {
    composite.clear()  // Очистить подписки
}

override fun onStart() {
    composite.add(observable.subscribe())  // OK! Можно добавить снова
}

// Сценарий 2: onDestroy
override fun onDestroy() {
    composite.dispose()  // Окончательно уничтожить
}

// composite.add(...)  // IllegalStateException!
```
</details>

### Вопрос 5: Как правильно обработать ошибку в chain?

<details>
<summary>Ответ</summary>

**Варианты обработки:**

1. **onErrorReturn** — вернуть fallback значение

```kotlin
api.getUser("123")
    .onErrorReturn { User.EMPTY }
    .subscribe { user -> showUser(user) }
```

2. **onErrorResumeNext** — переключиться на другой Observable

```kotlin
api.getUser("123")
    .onErrorResumeNext { error ->
        cacheRepository.getUser("123")
    }
    .subscribe { user -> showUser(user) }
```

3. **retry** — повторить при ошибке

```kotlin
api.getUser("123")
    .retry(3)
    .subscribe({ user -> showUser(user) }, { error -> showError(error) })
```

4. **onErrorXxx в subscribe**

```kotlin
api.getUser("123")
    .subscribe(
        { user -> showUser(user) },
        { error -> showError(error) }
    )
```

**Правильная позиция operator'а**:

```kotlin
// ПЛОХО: onErrorReturn слишком рано
api.getUser("123")
    .onErrorReturn { User.EMPTY }
    .flatMap { user -> api.getPosts(user.id) }  // Передаст EMPTY.id!

// ХОРОШО: обработка в конце или для каждого этапа
api.getUser("123")
    .flatMap { user -> api.getPosts(user.id) }
    .onErrorReturn { emptyList() }
```
</details>

### Вопрос 6: Почему combineLatest популярен для форм?

<details>
<summary>Ответ</summary>

**combineLatest** идеален для form validation потому что:

1. **Реагирует на изменение ЛЮБОГО поля**

```kotlin
combineLatest(email, password) { e, p ->
    e.isNotEmpty() && p.length >= 6
}
// Каждый раз когда меняется email ИЛИ password — пересчёт
```

2. **Использует последние значения всех полей**

```kotlin
// Пользователь ввёл email, затем password
combineLatest(email, password, terms) { e, p, t ->
    // Всегда имеем АКТУАЛЬНЫЕ значения всех трёх полей
    ValidationResult(e.isValid() && p.isValid() && t)
}
```

3. **Композируемость**

```kotlin
val isEmailValid = email.map { it.isValidEmail() }
val isPasswordValid = password.map { it.length >= 8 }
val doPasswordsMatch = combineLatest(password, passwordConfirm) { p, c -> p == c }

combineLatest(isEmailValid, isPasswordValid, doPasswordsMatch, terms)
    { emailOk, passOk, match, termsOk ->
        emailOk && passOk && match && termsOk
    }
    .subscribe { isValid -> submitButton.isEnabled = isValid }
```

4. **Альтернативы хуже**:
   - `zip` — требует равное количество emissions (неудобно для форм)
   - `merge` — не комбинирует значения
   - `withLatestFrom` — реагирует только на одно поле

**Итог**: combineLatest создан именно для сценариев "комбинировать несколько изменяющихся значений", что идеально для форм.
</details>

## Связи с другими темами

**[[android-async-evolution]]** — эволюция асинхронности в Android от AsyncTask через RxJava к Coroutines. RxJava был критическим шагом в этой эволюции, принёс реактивный подход.

**[[android-threading]]** — RxJava Schedulers абстрагируют Android threading. Понимание Handler, Looper, Thread критично для правильного использования observeOn/subscribeOn.

**[[kotlin-flow]]** — современная альтернатива RxJava от JetBrains. Flow проще для простых случаев, RxJava мощнее для complex event streams. Многие концепции общие (operators, cold/hot streams).

---

**Итог**: RxJava — мощная библиотека для реактивного программирования в Android. Хотя Kotlin Coroutines стали рекомендованным подходом, RxJava остаётся актуальной для сложных event-driven систем и legacy проектов. Критически важно правильно управлять lifecycle через Disposable, выбирать правильные operators и понимать threading model.

Знание RxJava полезно даже при работе с Coroutines — многие концепции переносимы, и понимание реактивного программирования делает вас более сильным разработчиком.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
