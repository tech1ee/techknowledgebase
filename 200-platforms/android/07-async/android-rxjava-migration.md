---
title: "Миграция RxJava → Kotlin Coroutines и Flow"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-rxjava]]"
  - "[[kotlin-coroutines]]"
  - "[[kotlin-flow]]"
  - "[[android-coroutines-guide]]"
  - "[[android-flow-guide]]"
prerequisites:
  - "[[android-rxjava]]"
  - "[[kotlin-coroutines]]"
  - "[[kotlin-flow]]"
reading_time: 40
difficulty: 5
study_status: not_started
mastery: 0
---

# Миграция RxJava → Kotlin Coroutines и Flow

## Зачем мигрировать

### Актуальность 2025-2026

Ландшафт Android-разработки кардинально изменился за последние годы. Google официально рекомендует Kotlin Coroutines и Flow как стандартный подход к асинхронности. Все Jetpack-библиотеки -- Room, WorkManager, DataStore, Paging 3, Compose -- построены на корутинах. Новые API появляются только с suspend-функциями, а RxJava-адаптеры становятся вторичными или вовсе не поддерживаются.

**Аргументы за миграцию:**

- **Официальная рекомендация Google**. Весь Jetpack и Compose спроектированы вокруг корутин. Использование RxJava с Compose требует дополнительных адаптеров и создаёт friction
- **Экосистема Kotlin-first**. Корутины -- часть языка и стандартной библиотеки. Flow -- это `kotlinx.coroutines`, не внешняя зависимость. Компилятор Kotlin оптимизирует suspend-функции
- **Structured concurrency**. Автоматическая отмена через CoroutineScope решает главную боль RxJava -- забытые Disposable и memory leaks. `viewModelScope`, `lifecycleScope` привязаны к lifecycle
- **Проще найти разработчиков**. Новые Android-разработчики учат корутины, а не RxJava. Порог входа ниже: suspend функции vs Observable/Single/Maybe/Completable/Flowable
- **Меньше boilerplate**. CompositeDisposable, subscribeOn/observeOn, dispose в onDestroy -- всё это заменяется на `viewModelScope.launch { }`
- **Библиотечная поддержка снижается**. RxJava 3 находится в maintenance mode. RxBinding, RxLifecycle, AutoDispose -- многие библиотеки экосистемы RxJava перестали активно развиваться
- **Размер APK**. RxJava добавляет ~2.5 MB к APK. kotlinx-coroutines-core ~1.5 MB и уже включены во многие Jetpack-зависимости

**Что НЕ стоит мигрировать:**

- **Стабильные модули, которые не меняются**. Если код работает и не трогается -- нет смысла тратить ресурсы
- **Сложные реактивные цепочки без аналогов**. Некоторые паттерны RxJava (window, buffer с комбинированными стратегиями) не имеют прямых аналогов в Flow
- **Проекты с командой, глубоко экспертной в RxJava**, без времени на обучение
- **Библиотеки, публикующие RxJava API**. Если ваш модуль -- публичная библиотека с RxJava-контрактами, миграция -- это breaking change для пользователей

**Ключевой принцип**: мигрируйте постепенно, новый код -- на корутинах, старый -- по мере рефакторинга. Интероп-библиотека `kotlinx-coroutines-rx3` делает сосуществование бесшовным.

---

## TL;DR

| Аспект | RxJava | Coroutines/Flow |
|--------|--------|-----------------|
| One-shot операция | `Single<T>` | `suspend fun: T` |
| Поток данных | `Observable<T>` / `Flowable<T>` | `Flow<T>` |
| Hot stream с состоянием | `BehaviorSubject<T>` | `MutableStateFlow<T>` |
| Hot stream без состояния | `PublishSubject<T>` | `MutableSharedFlow<T>` |
| Управление подписками | `CompositeDisposable` | `CoroutineScope` / `Job` |
| Переключение потоков | `subscribeOn` / `observeOn` | `flowOn` / `withContext` |
| Lifecycle-безопасность | Ручной dispose / AutoDispose | Structured concurrency |

Стратегия: добавить `kotlinx-coroutines-rx3` → писать новый код на корутинах → мигрировать снизу вверх (data → domain → presentation) → удалить RxJava.

---

## Пререквизиты

Для эффективного использования этого гайда необходимо:

- **[[android-rxjava]]** -- понимание типов RxJava (Observable, Single, Completable, Flowable), операторов, Schedulers, CompositeDisposable
- **[[kotlin-coroutines]]** -- базовое понимание suspend-функций, CoroutineScope, Dispatchers, structured concurrency
- **[[kotlin-flow]]** -- понимание Flow API: cold streams, операторы, StateFlow, SharedFlow

---

## Терминология

| RxJava концепция | Coroutines эквивалент | Пояснение |
|------------------|-----------------------|-----------|
| Observable | Flow | Cold stream, переиспускает данные для каждого подписчика |
| Observer | FlowCollector / collect {} | Потребитель данных |
| Subscription/Disposable | Job | Управление отменой операции |
| CompositeDisposable | CoroutineScope | Группировка и отмена связанных операций |
| Scheduler | CoroutineDispatcher | Контекст исполнения (IO, Default, Main) |
| subscribeOn | flowOn | Переключение контекста для upstream (ВНИМАНИЕ: семантика различается) |
| observeOn | collect на нужном Dispatcher | Контекст downstream |
| Subject | SharedFlow / StateFlow | Hot stream, множество подписчиков |
| Backpressure (Flowable) | Suspend (неявная) | Flow приостанавливает эмиттер автоматически через suspend |
| onErrorReturn | catch { emit() } | Перехват ошибки и замена значением |
| dispose() | cancel() | Отмена операции |

---

## Маппинг типов

### Базовые типы

| RxJava | Kotlin Coroutines/Flow | Комментарий |
|--------|------------------------|-------------|
| `Observable<T>` | `Flow<T>` | Cold stream. Flow пере-выполняется для каждого collector. Backpressure через suspend |
| `Single<T>` | `suspend fun: T` | Одна операция, один результат. Самая частая замена |
| `Maybe<T>` | `suspend fun: T?` | Результат может отсутствовать. Nullable return type |
| `Completable` | `suspend fun` (Unit) | Операция без результата. `suspend fun doWork()` |
| `Flowable<T>` | `Flow<T>` | Backpressure встроена в Flow через механизм suspend. Flowable `→` Flow без потери функциональности |

### Hot streams (Subject → SharedFlow/StateFlow)

| RxJava | Kotlin | Комментарий |
|--------|--------|-------------|
| `BehaviorSubject<T>` | `MutableStateFlow<T>(initial)` | Хранит последнее значение, требует начальное значение. `distinctUntilChanged` по умолчанию |
| `PublishSubject<T>` | `MutableSharedFlow<T>(replay = 0)` | Без буфера, новые подписчики не получают старые значения |
| `ReplaySubject<T>` | `MutableSharedFlow<T>(replay = N)` | Буферизует N последних значений для новых подписчиков |
| `ReplaySubject.createWithSize(1)` | `MutableSharedFlow<T>(replay = 1)` | Похоже на BehaviorSubject, но без начального значения и без distinctUntilChanged |
| `AsyncSubject<T>` | `CompletableDeferred<T>` | Один результат после завершения |
| `UnicastSubject<T>` | `Channel<T>` (один потребитель) | Один подписчик, горячий источник |

**Важные различия StateFlow vs BehaviorSubject:**

```kotlin
// BehaviorSubject -- нет distinctUntilChanged по умолчанию
val subject = BehaviorSubject.createDefault(0)
subject.subscribe { println(it) } // 0
subject.onNext(1) // 1
subject.onNext(1) // 1 (дублируется!)

// StateFlow -- distinctUntilChanged встроен
val stateFlow = MutableStateFlow(0)
scope.launch {
    stateFlow.collect { println(it) } // 0, 1
}
stateFlow.value = 1 // 1
stateFlow.value = 1 // НЕ эмитится (value == previous)
```

### Управление жизненным циклом

| RxJava | Kotlin | Комментарий |
|--------|--------|-------------|
| `CompositeDisposable` | `CoroutineScope` / `Job` | Scope автоматически отменяет все дочерние корутины |
| `Disposable` | `Job` | `job.cancel()` аналогичен `disposable.dispose()` |
| `Disposable.isDisposed` | `Job.isActive` / `Job.isCancelled` | Проверка статуса |
| AutoDispose (Uber) | `lifecycleScope` / `viewModelScope` | Structured concurrency заменяет AutoDispose |
| `takeUntil(lifecycle)` | Structured concurrency | Отмена через scope, а не через оператор |

### Schedulers → Dispatchers

| RxJava Scheduler | Kotlin Dispatcher | Комментарий |
|------------------|-------------------|-------------|
| `Schedulers.io()` | `Dispatchers.IO` | IO-операции. IO диспетчер ограничен 64 потоками (настраиваемо) |
| `Schedulers.computation()` | `Dispatchers.Default` | CPU-bound работа. Пул = количество CPU ядер |
| `AndroidSchedulers.mainThread()` | `Dispatchers.Main` | UI поток. `Dispatchers.Main.immediate` для немедленного выполнения |
| `Schedulers.newThread()` | `newSingleThreadContext()` | Выделенный поток (редко нужен) |
| `Schedulers.trampoline()` | `Dispatchers.Unconfined` | Выполнение на текущем потоке (для тестов) |
| `Schedulers.single()` | `newSingleThreadContext()` | Один поток для последовательного выполнения |
| `TestScheduler` | `TestDispatcher` (StandardTestDispatcher / UnconfinedTestDispatcher) | Контроль виртуального времени в тестах |

---

## Маппинг операторов

### Transformation operators

| RxJava | Kotlin Flow | Пример / Комментарий |
|--------|-------------|----------------------|
| `map { }` | `map { }` | Идентичны |
| `flatMap { }` | `flatMapMerge { }` | RxJava flatMap параллелен, Flow flatMapMerge -- аналог |
| `concatMap { }` | `flatMapConcat { }` | Последовательное выполнение, сохраняет порядок |
| `switchMap { }` | `flatMapLatest { }` | Отменяет предыдущий inner flow при новом значении |
| `scan { acc, v -> }` | `scan(initial) { acc, v -> }` / `runningFold` | `runningFold` -- с начальным значением, `runningReduce` -- без |
| `toList()` | `toList()` | Собирает все элементы в список (terminal) |
| `buffer(count)` | `chunked(count)` | Группировка по количеству |
| `groupBy { }` | Нет прямого аналога | Реализуется через `collect` + `groupBy` из stdlib |
| `cast()` | `map { it as T }` / `filterIsInstance<T>()` | Через стандартные функции Kotlin |

```kotlin
// RxJava: flatMap (параллельный)
observable
    .flatMap { id -> api.getUser(id).toObservable() }
    .subscribe { user -> process(user) }

// Flow: flatMapMerge (параллельный аналог)
flow
    .flatMapMerge { id -> flow { emit(api.getUser(id)) } }
    .collect { user -> process(user) }

// RxJava: switchMap (отмена предыдущего)
searchQuery
    .switchMap { query -> api.search(query).toObservable() }
    .subscribe { results -> show(results) }

// Flow: flatMapLatest (отмена предыдущего)
searchQuery
    .flatMapLatest { query -> flow { emit(api.search(query)) } }
    .collect { results -> show(results) }
```

### Filtering operators

| RxJava | Kotlin Flow | Пример / Комментарий |
|--------|-------------|----------------------|
| `filter { }` | `filter { }` | Идентичны |
| `distinctUntilChanged()` | `distinctUntilChanged()` | Идентичны |
| `debounce(ms, TimeUnit)` | `debounce(ms)` | В Flow принимает Long в миллисекундах |
| `throttleFirst(ms, TimeUnit)` | `throttleFirst(ms)` (с Kotlin 1.9.20+) | До 1.9.20: кастомная реализация через `conflate` + `transformLatest` |
| `throttleLast(ms, TimeUnit)` / `sample` | `sample(ms)` | Идентичны по семантике |
| `take(n)` | `take(n)` | Идентичны |
| `takeLast(n)` | Нет прямого аналога | Реализуется через `toList().takeLast(n)` |
| `skip(n)` | `drop(n)` | Разные имена, одинаковая семантика |
| `first()` | `first()` | Идентичны |
| `elementAt(n)` | `drop(n).first()` | Через комбинацию |
| `distinct()` | `distinctUntilChanged()` + дедупликация | Flow не имеет `distinct()` из коробки |
| `takeUntil(other)` | Отмена через scope | Structured concurrency вместо оператора |
| `skipUntil(other)` | Нет прямого аналога | Кастомная реализация |

```kotlin
// RxJava: debounce + filter + distinctUntilChanged
searchEditText.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .subscribe { query -> search(query) }

// Flow: аналогичная цепочка
searchEditText.textChanges() // предполагаем Flow<String>
    .debounce(300)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .collect { query -> search(query) }
```

### Combining operators

| RxJava | Kotlin Flow | Пример / Комментарий |
|--------|-------------|----------------------|
| `zip(a, b) { }` | `a.zip(b) { }` | Идентичны по семантике |
| `combineLatest(a, b) { }` | `combine(a, b) { }` | Другое имя, та же семантика |
| `merge(a, b)` | `merge(a, b)` / `listOf(a, b).merge()` | Идентичны |
| `concat(a, b)` | `flowOf(a, b).flattenConcat()` / `a.onCompletion { emitAll(b) }` | Последовательное объединение |
| `startWith(value)` | `onStart { emit(value) }` | Через оператор onStart |
| `startWithItem(value)` | `onStart { emit(value) }` | Аналогично |
| `withLatestFrom(other)` | Нет прямого аналога | Реализуется через `combine` + дополнительную логику |
| `amb(a, b)` / `ambArray` | Нет прямого аналога | Кастомная реализация через `select` |
| `switchOnNext` | `flatMapLatest` | Аналогичная семантика |

```kotlin
// RxJava: combineLatest для валидации формы
Observable.combineLatest(
    emailFlow, passwordFlow, termsFlow
) { email, password, terms ->
    email.isValid() && password.length >= 8 && terms
}.subscribe { isValid -> button.isEnabled = isValid }

// Flow: combine для валидации формы
combine(emailFlow, passwordFlow, termsFlow) { email, password, terms ->
    email.isValid() && password.length >= 8 && terms
}.collect { isValid -> button.isEnabled = isValid }

// RxJava: merge
Observable.merge(cacheSource, networkSource)
    .subscribe { data -> show(data) }

// Flow: merge
merge(cacheSource, networkSource)
    .collect { data -> show(data) }

// RxJava: startWith
observable
    .startWithItem(State.Loading)
    .subscribe { state -> render(state) }

// Flow: onStart
flow
    .onStart { emit(State.Loading) }
    .collect { state -> render(state) }
```

### Error handling operators

| RxJava | Kotlin Flow | Пример / Комментарий |
|--------|-------------|----------------------|
| `onErrorReturn { value }` | `catch { emit(value) }` | catch -- terminal оператор для Flow |
| `onErrorResumeNext { otherObs }` | `catch { emitAll(otherFlow) }` | Переключение на fallback Flow |
| `retry(n)` | `retry(n)` | Идентичны |
| `retryWhen { errors -> }` | `retryWhen { cause, attempt -> }` | Разная сигнатура: Flow даёт cause + attempt number |
| `doOnError { }` | `onEach { }.catch { log(it); throw it }` | Side-effect при ошибке |
| `onErrorComplete()` | `catch { }` (пустой блок) | Поглотить ошибку |

```kotlin
// RxJava: onErrorReturn
api.getUsers()
    .onErrorReturn { emptyList() }
    .subscribe { users -> show(users) }

// Flow: catch
api.getUsersFlow()
    .catch { emit(emptyList()) }
    .collect { users -> show(users) }

// RxJava: retry с exponential backoff
api.getUser(id)
    .retryWhen { errors ->
        errors.zipWith(Observable.range(1, 3)) { e, i -> i }
            .flatMap { Observable.timer(it.toLong() * 2, TimeUnit.SECONDS) }
    }
    .subscribe { user -> show(user) }

// Flow: retry с exponential backoff
flow { emit(api.getUser(id)) }
    .retryWhen { cause, attempt ->
        if (attempt < 3 && cause is IOException) {
            delay(2000L * (attempt + 1))
            true
        } else {
            false
        }
    }
    .collect { user -> show(user) }
```

### Threading / Context operators

| RxJava | Kotlin Flow | Комментарий |
|--------|-------------|-------------|
| `subscribeOn(scheduler)` | `flowOn(dispatcher)` | **КРИТИЧЕСКОЕ РАЗЛИЧИЕ**: семантика перевёрнута (см. раздел "Ловушки миграции") |
| `observeOn(scheduler)` | Collect на нужном Dispatcher | Flow собирается в контексте вызывающего scope |
| `unsubscribeOn(scheduler)` | Нет аналога | Отмена происходит в контексте scope |

```kotlin
// RxJava: subscribeOn + observeOn
repository.getData()                        // создание на IO
    .subscribeOn(Schedulers.io())           // upstream на IO
    .map { transform(it) }                 // IO thread
    .observeOn(AndroidSchedulers.mainThread()) // переключение на Main
    .subscribe { data -> updateUI(data) }  // Main thread

// Flow: flowOn + collect в scope
repository.getDataFlow()                    // создание
    .map { transform(it) }                 // IO thread (из-за flowOn ниже)
    .flowOn(Dispatchers.IO)                // всё выше -- на IO
    .collect { data -> updateUI(data) }    // контекст scope (Main)
```

### Lifecycle operators

| RxJava | Kotlin Flow | Комментарий |
|--------|-------------|-------------|
| `takeUntil(lifecycle)` | Structured concurrency (scope cancellation) | Не нужен оператор -- scope отменяет всё |
| `autoDispose(provider)` | `lifecycleScope` / `viewModelScope` | Встроено в Android KTX |
| `compose(transformer)` | Extension functions на Flow | Kotlin extensions естественнее |
| `doOnSubscribe { }` | `onStart { }` | Идентичны по назначению |
| `doOnDispose { }` | `onCompletion { }` | Вызывается при завершении или отмене |
| `doFinally { }` | `onCompletion { }` | Аналогично |
| `doOnNext { }` | `onEach { }` | Side-effect для каждого элемента |

---

## Стратегия миграции

### Обзор фаз

```
Phase 1: Coexistence     → Добавить корутины, мост через interop
Phase 2: New Code Policy → Весь новый код на корутинах
Phase 3: Layer Migration  → Миграция слоями (data → domain → presentation)
Phase 4: Cleanup         → Удаление RxJava зависимостей
```

### Phase 1: Coexistence (сосуществование)

**Цель**: обеспечить бесшовную работу RxJava и Coroutines в одном проекте.

**Шаг 1. Добавить зависимости:**

```kotlin
// build.gradle.kts
dependencies {
    // Существующие RxJava зависимости (не трогаем)
    implementation("io.reactivex.rxjava3:rxjava:3.1.8")
    implementation("io.reactivex.rxjava3:rxandroid:3.0.2")

    // Добавляем корутины
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")

    // Ключевая библиотека: мост RxJava ↔ Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:1.8.1")

    // Для тестов
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

**Шаг 2. Использовать interop-адаптеры:**

Библиотека `kotlinx-coroutines-rx3` предоставляет двусторонние конвертеры:

```kotlin
import kotlinx.coroutines.rx3.*

// RxJava → Coroutines
val single: Single<User> = api.getUser("123")
val user: User = single.await()                  // Single → suspend

val observable: Observable<Event> = eventBus.events()
val flow: Flow<Event> = observable.asFlow()       // Observable → Flow

val flowable: Flowable<Data> = source.getData()
val flow2: Flow<Data> = flowable.asFlow()         // Flowable → Flow

val completable: Completable = db.insertUser(user)
completable.await()                               // Completable → suspend

val maybe: Maybe<User> = db.findUser(id)
val result: User? = maybe.awaitSingleOrNull()     // Maybe → suspend nullable

// Coroutines → RxJava (для обратной совместимости)
val flow: Flow<Data> = repository.getDataFlow()
val observable: Observable<Data> = flow.asObservable()  // Flow → Observable

val deferred: Deferred<User> = async { getUser() }
val single: Single<User> = deferred.asSingle()          // Deferred → Single

// Создание RxJava типов из корутин-блоков
val rxSingle: Single<User> = rxSingle {
    api.getUser("123")  // suspend вызов внутри RxJava Single
}

val rxObservable: Observable<Int> = rxObservable {
    for (i in 1..10) {
        send(i)          // emit значений в Observable
        delay(100)
    }
}

val rxCompletable: Completable = rxCompletable {
    db.insertUser(user)  // suspend вызов внутри Completable
}
```

**Шаг 3. Создать bridge на уровне Repository:**

```kotlin
// Интерфейс, который поддерживает оба стиля в переходный период
interface UserRepository {
    // Новый API (корутины)
    suspend fun getUser(id: String): User
    fun observeUsers(): Flow<List<User>>

    // Legacy API (RxJava) -- deprecated
    @Deprecated("Use suspend getUser()", ReplaceWith("getUser(id)"))
    fun getUserRx(id: String): Single<User>

    @Deprecated("Use observeUsers()", ReplaceWith("observeUsers()"))
    fun observeUsersRx(): Observable<List<User>>
}

class UserRepositoryImpl(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository {

    // Первичная реализация -- корутины
    override suspend fun getUser(id: String): User =
        withContext(Dispatchers.IO) {
            api.getUser(id)
        }

    override fun observeUsers(): Flow<List<User>> =
        dao.observeAllUsers() // Room уже возвращает Flow
            .flowOn(Dispatchers.IO)

    // Legacy -- делегирует к корутинам через interop
    override fun getUserRx(id: String): Single<User> =
        rxSingle { getUser(id) }

    override fun observeUsersRx(): Observable<List<User>> =
        observeUsers().asObservable()
}
```

### Phase 2: New Code on Coroutines (новый код на корутинах)

**Цель**: все новые фичи пишутся на корутинах. RxJava в новом коде запрещён.

**Lint-правило для предотвращения нового RxJava-кода:**

```kotlin
// Кастомный lint check (или Detekt правило)
// detekt.yml
custom-rules:
  NoNewRxJava:
    active: true
    # Запретить import io.reactivex в новых файлах
    patterns:
      - "import io.reactivex"
```

Более простой подход -- Git hook или CI-проверка:

```bash
#!/bin/bash
# pre-commit hook: запретить новые файлы с RxJava imports
NEW_FILES=$(git diff --cached --name-only --diff-filter=A -- '*.kt')
for file in $NEW_FILES; do
    if grep -q "import io.reactivex" "$file"; then
        echo "ERROR: New file $file contains RxJava imports."
        echo "All new code must use Kotlin Coroutines/Flow."
        exit 1
    fi
done
```

### Phase 3: Migrate Layer-by-Layer (миграция по слоям)

**Стратегия: bottom-up** -- снизу вверх, от data layer к presentation.

```
┌─────────────────────────┐
│   Presentation (UI)     │  ← Мигрируем ПОСЛЕДНИМ
│   ViewModel / Presenter │
├─────────────────────────┤
│   Domain (UseCases)     │  ← Мигрируем ВТОРЫМ
├─────────────────────────┤
│   Data (Repository)     │  ← Мигрируем ПЕРВЫМ
│   Network / Database    │
└─────────────────────────┘
```

**Почему снизу вверх?**

1. Data layer -- наименее связан с UI, проще тестировать
2. Retrofit и Room уже поддерживают suspend-функции нативно
3. Каждый мигрированный слой уменьшает количество interop-мостов
4. Presentation layer меняется только когда нижние слои готовы

### Phase 4: Cleanup (очистка)

После полной миграции всех слоёв:

```kotlin
// build.gradle.kts -- удаляем RxJava зависимости
dependencies {
    // УДАЛИТЬ:
    // implementation("io.reactivex.rxjava3:rxjava:3.1.8")
    // implementation("io.reactivex.rxjava3:rxandroid:3.0.2")
    // implementation("io.reactivex.rxjava3:rxkotlin:3.0.1")
    // implementation("com.squareup.retrofit2:adapter-rxjava3:2.9.0")
    // implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:1.8.1")

    // ОСТАВИТЬ:
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}
```

Проверки перед удалением:
- `grep -r "import io.reactivex" --include="*.kt" .` -- ноль результатов
- `./gradlew dependencies | grep rxjava` -- ноль транзитивных зависимостей
- Все тесты проходят

---

## Миграция по слоям: практика

### Data Layer: Repository

**До (RxJava):**

```kotlin
class UserRepository(
    private val api: ApiService,
    private val dao: UserDao
) {
    fun getUser(id: String): Single<User> {
        return api.getUser(id)                          // Single<User>
            .doOnSuccess { user -> dao.insertUser(user) }
            .onErrorResumeNext { error ->
                if (error is IOException) {
                    dao.getUserById(id).toSingle()
                } else {
                    Single.error(error)
                }
            }
            .subscribeOn(Schedulers.io())
    }

    fun observeUsers(): Observable<List<User>> {
        return dao.observeAllUsers()                    // Observable<List<User>>
            .subscribeOn(Schedulers.io())
    }

    fun updateUser(user: User): Completable {
        return api.updateUser(user)                     // Completable
            .doOnComplete { dao.updateUser(user) }
            .subscribeOn(Schedulers.io())
    }
}

// Retrofit API
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") id: String): Single<User>

    @PUT("users/{id}")
    fun updateUser(@Body user: User): Completable
}
```

**После (Coroutines/Flow):**

```kotlin
class UserRepository(
    private val api: ApiService,
    private val dao: UserDao
) {
    suspend fun getUser(id: String): User =
        withContext(Dispatchers.IO) {
            try {
                val user = api.getUser(id)    // suspend fun
                dao.insertUser(user)
                user
            } catch (e: IOException) {
                dao.getUserById(id)           // suspend fun, fallback
                    ?: throw e
            }
        }

    fun observeUsers(): Flow<List<User>> =
        dao.observeAllUsers()                 // Room возвращает Flow
            .flowOn(Dispatchers.IO)

    suspend fun updateUser(user: User) =
        withContext(Dispatchers.IO) {
            api.updateUser(user)              // suspend fun
            dao.updateUser(user)
        }
}

// Retrofit API (suspend)
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @PUT("users/{id}")
    suspend fun updateUser(@Body user: User)
}
```

**Ключевые изменения:**
- `Single<T>` → `suspend fun: T`
- `Completable` → `suspend fun` (возвращает Unit)
- `Observable<T>` → `Flow<T>`
- `subscribeOn(Schedulers.io())` → `withContext(Dispatchers.IO)` или `flowOn(Dispatchers.IO)`
- `onErrorResumeNext` → try/catch
- `doOnSuccess` → прямой вызов после await

### Domain Layer: UseCase

**До (RxJava):**

```kotlin
class GetUserProfileUseCase(
    private val userRepo: UserRepository,
    private val postRepo: PostRepository
) {
    fun execute(userId: String): Single<UserProfile> {
        return Single.zip(
            userRepo.getUser(userId),
            postRepo.getUserPosts(userId)
        ) { user, posts ->
            UserProfile(user, posts)
        }
    }
}

class ObserveSearchResultsUseCase(
    private val searchRepo: SearchRepository
) {
    fun execute(query: Observable<String>): Observable<List<SearchResult>> {
        return query
            .debounce(300, TimeUnit.MILLISECONDS)
            .filter { it.length >= 3 }
            .distinctUntilChanged()
            .switchMap { searchRepo.search(it).toObservable() }
    }
}
```

**После (Coroutines/Flow):**

```kotlin
class GetUserProfileUseCase(
    private val userRepo: UserRepository,
    private val postRepo: PostRepository
) {
    suspend fun execute(userId: String): UserProfile =
        coroutineScope {
            val user = async { userRepo.getUser(userId) }
            val posts = async { postRepo.getUserPosts(userId) }
            UserProfile(user.await(), posts.await())
        }
}

class ObserveSearchResultsUseCase(
    private val searchRepo: SearchRepository
) {
    fun execute(query: Flow<String>): Flow<List<SearchResult>> {
        return query
            .debounce(300)
            .filter { it.length >= 3 }
            .distinctUntilChanged()
            .flatMapLatest { searchRepo.search(it) }
    }
}
```

**Ключевые изменения:**
- `Single.zip()` → `coroutineScope { async/await }` -- параллельные запросы
- `switchMap` → `flatMapLatest`
- `debounce(300, TimeUnit.MILLISECONDS)` → `debounce(300)`
- Observable параметр → Flow параметр

### Presentation Layer: ViewModel

**До (RxJava):**

```kotlin
class UserViewModel(
    private val getUserProfile: GetUserProfileUseCase,
    private val observeUsers: ObserveUsersUseCase
) : ViewModel() {

    private val compositeDisposable = CompositeDisposable()

    private val _state = BehaviorSubject.createDefault<UiState>(UiState.Loading)
    val state: Observable<UiState> = _state.hide()

    private val _events = PublishSubject.create<UiEvent>()
    val events: Observable<UiEvent> = _events.hide()

    fun loadProfile(userId: String) {
        getUserProfile.execute(userId)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .doOnSubscribe { _state.onNext(UiState.Loading) }
            .subscribe(
                { profile -> _state.onNext(UiState.Success(profile)) },
                { error ->
                    _state.onNext(UiState.Error(error.message ?: "Unknown"))
                    _events.onNext(UiEvent.ShowSnackbar(error.message ?: "Error"))
                }
            )
            .let { compositeDisposable.add(it) }
    }

    fun observeUsers() {
        observeUsers.execute()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { users -> _state.onNext(UiState.UserList(users)) },
                { error -> _state.onNext(UiState.Error(error.message ?: "")) }
            )
            .let { compositeDisposable.add(it) }
    }

    override fun onCleared() {
        compositeDisposable.dispose()
        super.onCleared()
    }
}
```

**После (Coroutines/Flow):**

```kotlin
class UserViewModel(
    private val getUserProfile: GetUserProfileUseCase,
    private val observeUsers: ObserveUsersUseCase
) : ViewModel() {

    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val profile = getUserProfile.execute(userId)
                _state.value = UiState.Success(profile)
            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown")
                _events.emit(UiEvent.ShowSnackbar(e.message ?: "Error"))
            }
        }
    }

    fun observeUsers() {
        viewModelScope.launch {
            observeUsers.execute()
                .catch { error ->
                    _state.value = UiState.Error(error.message ?: "")
                }
                .collect { users ->
                    _state.value = UiState.UserList(users)
                }
        }
    }

    // onCleared не нужен -- viewModelScope автоматически отменяет все корутины
}
```

**Ключевые изменения:**
- `CompositeDisposable` → `viewModelScope` (автоматическая отмена)
- `BehaviorSubject` → `MutableStateFlow` (hot stream с состоянием)
- `PublishSubject` → `MutableSharedFlow` (hot stream для событий)
- `subscribe(onSuccess, onError)` → `try/catch` в `viewModelScope.launch`
- `subscribeOn/observeOn` → не нужны (repository сам определяет Dispatcher)
- `onCleared { dispose() }` → не нужен

### UI Layer: Activity/Fragment

**До (RxJava):**

```kotlin
class UserFragment : Fragment() {
    private val disposables = CompositeDisposable()
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.state
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showProfile(state.profile)
                    is UiState.Error -> showError(state.message)
                    is UiState.UserList -> showUsers(state.users)
                }
            }
            .let { disposables.add(it) }

        viewModel.events
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { event ->
                when (event) {
                    is UiEvent.ShowSnackbar -> showSnackbar(event.message)
                }
            }
            .let { disposables.add(it) }

        viewModel.loadProfile("123")
    }

    override fun onDestroyView() {
        disposables.dispose()
        super.onDestroyView()
    }
}
```

**После (Coroutines/Flow) -- XML Views:**

```kotlin
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.state.collect { state ->
                        when (state) {
                            is UiState.Loading -> showLoading()
                            is UiState.Success -> showProfile(state.profile)
                            is UiState.Error -> showError(state.message)
                            is UiState.UserList -> showUsers(state.users)
                        }
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        when (event) {
                            is UiEvent.ShowSnackbar -> showSnackbar(event.message)
                        }
                    }
                }
            }
        }

        viewModel.loadProfile("123")
    }

    // onDestroyView не нужен -- repeatOnLifecycle автоматически отменяет сбор
}
```

**После (Coroutines/Flow) -- Compose:**

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowSnackbar -> { /* показать Snackbar */ }
            }
        }
    }

    when (val currentState = state) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> ProfileContent(currentState.profile)
        is UiState.Error -> ErrorMessage(currentState.message)
        is UiState.UserList -> UserListContent(currentState.users)
    }

    LaunchedEffect(Unit) {
        viewModel.loadProfile("123")
    }
}
```

**Ключевые изменения:**
- `CompositeDisposable` + `dispose()` → `repeatOnLifecycle` / `collectAsStateWithLifecycle`
- `observeOn(mainThread())` → не нужен (StateFlow collect на Main по умолчанию в lifecycleScope)
- `subscribe { }` → `collect { }`
- Lifecycle-безопасность встроена в `repeatOnLifecycle`

---

## Ловушки миграции

### 1. subscribeOn vs flowOn -- ПЕРЕВЁРНУТАЯ семантика

Это самая опасная ловушка при миграции. RxJava и Flow используют противоположные направления для переключения контекста.

**RxJava: subscribeOn влияет на upstream (вверх по цепочке) от точки создания:**

```kotlin
// RxJava: subscribeOn -- позиция НЕ важна
observable
    .map { transform(it) }    // IO thread
    .filter { isValid(it) }   // IO thread
    .subscribeOn(Schedulers.io()) // весь upstream на IO
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { show(it) }   // Main thread
```

**Flow: flowOn влияет на upstream (вверх по цепочке) от точки вызова:**

```kotlin
// Flow: flowOn -- позиция ВАЖНА
flow
    .map { transform(it) }    // IO thread (выше flowOn)
    .filter { isValid(it) }   // IO thread (выше flowOn)
    .flowOn(Dispatchers.IO)   // всё ВЫШЕ -- на IO
    .map { format(it) }       // Main thread (ниже flowOn, в контексте scope)
    .collect { show(it) }     // Main thread (контекст scope)
```

**Ключевое различие:**
- В RxJava `subscribeOn` влияет на **весь** upstream **независимо от позиции** в цепочке
- В Flow `flowOn` влияет **только на операторы выше** себя в цепочке
- `observeOn` в RxJava переключает downstream -- в Flow это просто контекст scope, где вызван `collect`

**Распространённая ошибка при миграции:**

```kotlin
// НЕПРАВИЛЬНО: механическая замена subscribeOn на flowOn
flow
    .flowOn(Dispatchers.IO) // flowOn в начале -- бесполезен!
    .map { transform(it) }  // Main thread (контекст scope)
    .collect { show(it) }   // Main thread

// ПРАВИЛЬНО: flowOn после операторов, которые нужно выполнить на IO
flow
    .map { transform(it) }  // IO thread
    .flowOn(Dispatchers.IO) // всё выше -- IO
    .collect { show(it) }   // Main thread (контекст scope)
```

### 2. Concurrency по умолчанию: параллельный vs последовательный

**RxJava: flatMap -- параллелен по умолчанию:**

```kotlin
// RxJava: flatMap запускает все inner Observable параллельно
Observable.fromIterable(userIds)
    .flatMap { id -> api.getUser(id).toObservable() } // ПАРАЛЛЕЛЬНО
    .toList()
    .subscribe { users -> show(users) }
```

**Flow: flatMapConcat -- последователен по умолчанию:**

```kotlin
// Flow: flatMapConcat -- ПОСЛЕДОВАТЕЛЬНО!
userIds.asFlow()
    .flatMapConcat { id -> flow { emit(api.getUser(id)) } } // ПОСЛЕДОВАТЕЛЬНО
    .toList()

// Для параллельного выполнения нужен flatMapMerge
userIds.asFlow()
    .flatMapMerge { id -> flow { emit(api.getUser(id)) } } // ПАРАЛЛЕЛЬНО
    .toList()

// Или channelFlow для явного параллелизма
channelFlow {
    userIds.forEach { id ->
        launch { send(api.getUser(id)) }
    }
}.toList()
```

**Ошибка**: механическая замена `flatMap` на `flatMapConcat` превращает параллельные запросы в последовательные, что может драматически ухудшить производительность.

### 3. Обработка ошибок: глобальная vs структурированная

**RxJava: необработанная ошибка → глобальный RxJavaPlugins.onError:**

```kotlin
// RxJava: если subscribe() без onError -- ошибка уходит в глобальный handler
observable.subscribe { data -> process(data) }
// UndeliverableException → RxJavaPlugins.setErrorHandler

// Настройка глобального handler
RxJavaPlugins.setErrorHandler { e ->
    Log.e("RxJava", "Unhandled error", e)
}
```

**Flow: необработанная ошибка → exception в корутине:**

```kotlin
// Flow: необработанная ошибка крашит корутину (и, возможно, приложение)
scope.launch {
    flow.collect { data -> process(data) }
    // Если flow выбросит exception -- корутина крашится
}

// Правильно: обработать ошибку
scope.launch {
    flow
        .catch { e -> handleError(e) }
        .collect { data -> process(data) }
}

// Или в CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, e ->
    Log.e("Coroutines", "Unhandled error", e)
}
scope.launch(handler) {
    flow.collect { data -> process(data) }
}
```

**Ошибка**: забыть добавить `catch` при миграции кода, который полагался на глобальный RxJava error handler.

### 4. Backpressure: явная vs неявная

**RxJava: явное управление backpressure через Flowable:**

```kotlin
// RxJava: выбор стратегии backpressure
Flowable.create({ emitter ->
    for (i in 1..1_000_000) {
        emitter.onNext(i)
    }
    emitter.onComplete()
}, BackpressureStrategy.BUFFER)   // BUFFER, DROP, LATEST, ERROR, MISSING
    .observeOn(Schedulers.computation())
    .subscribe { process(it) }
```

**Flow: backpressure неявна через suspend:**

```kotlin
// Flow: emit() -- suspend функция, естественная backpressure
flow {
    for (i in 1..1_000_000) {
        emit(i)  // приостановится, если collector не успевает
    }
}
.collect { process(it) }

// Явное управление через buffer/conflate
flow
    .buffer(capacity = 64)     // буферизация
    .collect { process(it) }

flow
    .conflate()                // пропускать промежуточные значения
    .collect { process(it) }

flow
    .collectLatest { process(it) } // отменять обработку при новом значении
```

**Ошибка**: при миграции Flowable с `BackpressureStrategy.DROP` на Flow забыть добавить `conflate()`, что приведёт к другому поведению при высокой нагрузке.

### 5. Hot streams: Subject vs SharedFlow -- тонкие различия

**BehaviorSubject vs StateFlow:**

```kotlin
// BehaviorSubject: эмитит ВСЕ значения, включая дубликаты
val subject = BehaviorSubject.createDefault(0)
subject.subscribe { println(it) }
subject.onNext(1) // печатает 1
subject.onNext(1) // печатает 1 (дубликат!)
subject.onNext(2) // печатает 2

// StateFlow: НЕ эмитит дубликаты (equality check)
val stateFlow = MutableStateFlow(0)
scope.launch { stateFlow.collect { println(it) } }
stateFlow.value = 1 // печатает 1
stateFlow.value = 1 // НЕ печатает (значение не изменилось)
stateFlow.value = 2 // печатает 2
```

**PublishSubject vs SharedFlow -- потеря событий:**

```kotlin
// PublishSubject: если нет подписчиков, события теряются
val subject = PublishSubject.create<Event>()
subject.onNext(Event.A) // потеряно! нет подписчиков
subject.subscribe { println(it) }
subject.onNext(Event.B) // печатает B

// SharedFlow(replay=0): аналогичное поведение, но...
val sharedFlow = MutableSharedFlow<Event>()
scope.launch { sharedFlow.emit(Event.A) } // suspend -- ждёт подписчика!

// Для поведения "fire and forget" нужен tryEmit или extraBufferCapacity
val sharedFlow2 = MutableSharedFlow<Event>(
    extraBufferCapacity = 64  // буфер для событий без подписчика
)
sharedFlow2.tryEmit(Event.A) // не suspend, вернёт false если буфер полон
```

**Ошибка**: при миграции BehaviorSubject на StateFlow может сломаться логика, зависящая от повторных эмиссий одинаковых значений. При миграции PublishSubject на SharedFlow(replay=0) может зависнуть `emit()` при отсутствии подписчиков.

### 6. Тестирование: TestScheduler vs TestDispatcher

**RxJava: TestScheduler для контроля времени:**

```kotlin
// RxJava
@Test
fun `debounce emits after delay`() {
    val scheduler = TestScheduler()
    val subject = PublishSubject.create<String>()
    val results = mutableListOf<String>()

    subject
        .debounce(300, TimeUnit.MILLISECONDS, scheduler)
        .subscribe { results.add(it) }

    subject.onNext("a")
    scheduler.advanceTimeBy(200, TimeUnit.MILLISECONDS)
    assertEquals(0, results.size) // ещё не прошло 300ms

    scheduler.advanceTimeBy(100, TimeUnit.MILLISECONDS)
    assertEquals(1, results.size) // прошло 300ms
    assertEquals("a", results[0])
}
```

**Flow: TestDispatcher + runTest:**

```kotlin
// Flow
@Test
fun `debounce emits after delay`() = runTest {
    val flow = MutableSharedFlow<String>()
    val results = mutableListOf<String>()

    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        flow
            .debounce(300)
            .collect { results.add(it) }
    }

    flow.emit("a")
    advanceTimeBy(200)
    assertEquals(0, results.size) // ещё не прошло 300ms

    advanceTimeBy(100)
    runCurrent()
    assertEquals(1, results.size) // прошло 300ms
    assertEquals("a", results[0])

    job.cancel()
}
```

**Ошибка**: использование `runBlocking` вместо `runTest` приводит к реальным задержкам в тестах. `StandardTestDispatcher` и `UnconfinedTestDispatcher` имеют разное поведение -- выбор зависит от того, нужен ли автоматический dispatch.

---

## Инструменты миграции

### Gradle: анализ зависимостей

Определить, какие модули всё ещё используют RxJava:

```bash
# Найти все модули с RxJava зависимостью
./gradlew dependencies --configuration releaseRuntimeClasspath | grep rxjava

# Для каждого модуля отдельно
./gradlew :feature-user:dependencies | grep rxjava

# Dependency Insight -- кто притягивает RxJava транзитивно
./gradlew :app:dependencyInsight --dependency rxjava
```

### IDE: структурный поиск и замена

**IntelliJ IDEA / Android Studio -- Structural Search:**

Шаблон для поиска всех `subscribe()` вызовов:

```
$observable$.subscribe($args$)
```

Шаблон для поиска CompositeDisposable:

```
private val $name$ = CompositeDisposable()
```

### Lint: кастомные правила

```kotlin
// Детект неиспользуемого RxJava import
// build.gradle.kts
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.4"
}

// detekt.yml -- правило для обнаружения RxJava usage
style:
  ForbiddenImport:
    active: true
    imports:
      - 'io.reactivex.rxjava3.*'
    message: 'RxJava imports are deprecated. Use Kotlin Coroutines/Flow.'
```

### Метрики миграции

Скрипт для отслеживания прогресса миграции:

```bash
#!/bin/bash
echo "=== RxJava Migration Progress ==="

TOTAL_KT=$(find . -name "*.kt" -not -path "*/build/*" | wc -l)
RXJAVA_FILES=$(grep -rl "import io.reactivex" --include="*.kt" \
    --exclude-dir=build . | wc -l)
COROUTINE_FILES=$(grep -rl "import kotlinx.coroutines" --include="*.kt" \
    --exclude-dir=build . | wc -l)

echo "Total Kotlin files: $TOTAL_KT"
echo "Files with RxJava imports: $RXJAVA_FILES"
echo "Files with Coroutine imports: $COROUTINE_FILES"
echo "Migration progress: $(( (TOTAL_KT - RXJAVA_FILES) * 100 / TOTAL_KT ))%"
```

---

## Real-world примеры

### Cash App: серия "Rx to Coroutines Concepts"

Команда Cash App (Block) провела масштабную миграцию с RxJava на корутины и опубликовала серию из 6 статей, документирующих процесс. Их кодовая база была "thoroughly invested in RxJava" -- практически весь presenter layer и значительная часть кода вне него строились на Observable.

**Основные выводы Cash App:**

- Корутины позволяют "discard reactive grammar and write what is essentially straight up Kotlin code"
- `Channel` проще и гибче, чем `PublishSubject` для тех же задач
- Suspend-код делает логику более прозрачной, чем цепочки RxJava операторов
- Structured concurrency кардинально отличается от подхода RxJava к управлению жизненным циклом

### Uber: проблемы backpressure

Uber -- один из крупнейших пользователей RxJava в Android -- столкнулся с массовыми `MissingBackpressureException` крашами. Начав миграцию ещё с RxJava 1.x на 2.x, они обнаружили, что даже после миграции большей части кода rider-приложения "long tail" крашей от legacy RxJava 1.x кода оставался. Опыт Uber показывает, что:

- Backpressure -- одна из самых сложных проблем RxJava
- Flow решает её автоматически через suspend-механизм
- В больших кодовых базах миграция занимает годы

### Общие метрики миграции

На основе опубликованных отчётов команд, мигрировавших с RxJava:

| Метрика | Типичный результат |
|---------|-------------------|
| Уменьшение boilerplate | 20-40% меньше строк кода |
| Уменьшение размера APK | 1-2 MB (удаление RxJava) |
| Время сборки | Незначительное изменение |
| Тесты | Проще писать с `runTest` |
| Memory leaks | Существенное уменьшение (structured concurrency) |
| Скорость разработки (после адаптации) | На 10-30% выше |
| Время миграции (крупный проект) | 6-18 месяцев (постепенно) |

---

## Распространённые ошибки

### Ошибка 1: Механическая замена без понимания семантики

```kotlin
// НЕПРАВИЛЬНО: слепая замена flatMap → flatMapConcat
// RxJava flatMap -- параллельный, flatMapConcat -- последовательный!
userIds.asFlow()
    .flatMapConcat { id -> flow { emit(api.getUser(id)) } }
    // Было 5 параллельных запросов, стало 5 ПОСЛЕДОВАТЕЛЬНЫХ
    // Время: 200ms → 1000ms

// ПРАВИЛЬНО: выбор аналога по семантике
userIds.asFlow()
    .flatMapMerge(concurrency = 5) { id -> flow { emit(api.getUser(id)) } }
```

### Ошибка 2: Использование GlobalScope вместо viewModelScope

```kotlin
// НЕПРАВИЛЬНО: GlobalScope -- аналог забытого Disposable
class UserViewModel : ViewModel() {
    fun loadUser() {
        GlobalScope.launch { // утечка! не отменится при onCleared
            val user = repo.getUser("123")
            _state.value = UiState.Success(user)
        }
    }
}

// ПРАВИЛЬНО: viewModelScope
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch { // отменится в onCleared
            val user = repo.getUser("123")
            _state.value = UiState.Success(user)
        }
    }
}
```

### Ошибка 3: Забыть repeatOnLifecycle при сборе Flow в UI

```kotlin
// НЕПРАВИЛЬНО: Flow продолжает собираться в фоне
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.state.collect { state -> // утечка: собирает даже в фоне
                updateUI(state)
            }
        }
    }
}

// ПРАВИЛЬНО: repeatOnLifecycle
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### Ошибка 4: Потеря контекста при onErrorResumeNext → catch

```kotlin
// RxJava: onErrorResumeNext может различать типы ошибок
observable
    .onErrorResumeNext { error ->
        when (error) {
            is NetworkException -> cacheObservable
            is AuthException -> Observable.error(error) // пробрасываем
            else -> Observable.empty()
        }
    }

// НЕПРАВИЛЬНО: catch глотает все ошибки
flow
    .catch { emit(cachedData) } // все ошибки обрабатываются одинаково

// ПРАВИЛЬНО: различаем типы ошибок в catch
flow
    .catch { error ->
        when (error) {
            is NetworkException -> emitAll(cacheFlow)
            is AuthException -> throw error // пробрасываем дальше
            else -> { /* ignore */ }
        }
    }
```

### Ошибка 5: Блокировка Main thread при миграции suspend-функций

```kotlin
// НЕПРАВИЛЬНО: suspend функция выполняет тяжёлую работу без переключения Dispatcher
suspend fun parseJsonFile(path: String): Data {
    val content = File(path).readText() // блокирующая IO на текущем потоке!
    return Json.decodeFromString(content)
}

// ПРАВИЛЬНО: явный withContext
suspend fun parseJsonFile(path: String): Data =
    withContext(Dispatchers.IO) {
        val content = File(path).readText()
        Json.decodeFromString(content)
    }
```

---

## CS-фундамент

### Reactive Extensions: история и теория

Reactive Extensions (Rx) были созданы Эриком Мейером (Erik Meijer) в Microsoft Research около 2009 года. Ключевая идея -- дуальность итераторов и наблюдателей. Если Iterable/Iterator -- pull-based (потребитель запрашивает данные), то Observable/Observer -- push-based (источник проталкивает данные).

```
Pull (Iterator):     consumer.next()  → data
Push (Observable):   producer.onNext(data) → consumer
```

Эта дуальность математически формализована через категорную теорию: Observable -- это "dual" (противоположный) к Iterable. Все операторы Iterable (map, filter, zip) имеют дуальные аналоги для Observable.

### Observer Pattern

RxJava -- это расширенная реализация классического паттерна Observer (GoF). Отличия от классического паттерна:
- Поддержка завершения (onComplete) и ошибок (onError) наряду с данными (onNext)
- Композиция через операторы (map, flatMap, filter)
- Управление потоками (Schedulers)
- Backpressure (Flowable)

### Корутины: продолжения (continuations)

Kotlin Coroutines основаны на концепции Continuation Passing Style (CPS). Компилятор трансформирует suspend-функцию в конечный автомат (state machine) с объектом Continuation, который хранит состояние выполнения. Это позволяет приостанавливать и возобновлять выполнение без создания новых потоков.

```
suspend fun → компилятор → state machine + Continuation
```

Flow строится поверх корутин: каждый `emit()` -- это suspend-вызов, который может приостановить эмиттер, если collector не готов принять данные. Это обеспечивает естественную backpressure без явного управления стратегиями, как в RxJava Flowable.

### От push к push-pull

RxJava Observable -- чистый push. Flow -- push-pull гибрид:
- **Push**: эмиттер проталкивает данные через `emit()`
- **Pull**: collector приостанавливает эмиттер через suspend, создавая backpressure

Этот гибридный подход -- одно из ключевых преимуществ Flow над RxJava Observable.

---

## Связь с другими темами

**[[android-rxjava]]** -- полный справочник по RxJava, который является отправной точкой для миграции. Все типы, операторы и паттерны, описанные в rxjava-гайде, имеют соответствия в этом документе.

**[[kotlin-coroutines]]** -- фундамент, на который строится миграция. Без понимания suspend-функций, CoroutineScope, structured concurrency и Dispatchers миграция невозможна.

**[[kotlin-flow]]** -- детальное описание Flow API, которое используется как целевой стандарт миграции. StateFlow, SharedFlow, операторы Flow -- всё это описано в flow-гайде.

**[[android-coroutines-guide]]** -- практическое применение корутин в Android: viewModelScope, lifecycleScope, best practices. Дополняет этот гайд практическими паттернами.

**[[android-flow-guide]]** -- практическое применение Flow в Android: collectAsStateWithLifecycle, repeatOnLifecycle, Room + Flow. Дополняет этот гайд UI-интеграцией.

**[[android-coroutines-mistakes]]** -- типичные ошибки при работе с корутинами в Android. После миграции с RxJava полезно изучить, чтобы не наступить на новые грабли.

**[[android-async-evolution]]** -- общая картина эволюции асинхронности в Android: от AsyncTask через RxJava к Coroutines. Помогает понять место миграции в историческом контексте.

---

## Источники и дальнейшее чтение

### Книги

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive*. -- детальное сравнение RxJava и Coroutines/Flow, миграционные паттерны, механика корутин и Flow. Главы о Flow operators и structured concurrency -- обязательное чтение при миграции

### Официальная документация

- Android Developers. *Kotlin flows on Android*. -- https://developer.android.com/kotlin/flow -- официальное руководство по Flow в Android
- Android Developers. *Best practices for coroutines in Android*. -- https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- JetBrains. *kotlinx-coroutines-rx3*. -- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-rx3/ -- документация interop-библиотеки
- JetBrains. *kotlinx.coroutines GitHub*. -- https://github.com/Kotlin/kotlinx.coroutines/tree/master/reactive/kotlinx-coroutines-rx3 -- исходный код и примеры interop

### Статьи и блоги

- Shoemaker M. *RxJava to Kotlin Coroutines: The Ultimate Migration Guide*. -- https://itnext.io/rxjava-to-kotlin-coroutines-the-ultimate-migration-guide-d41d782f9803 -- комплексный гайд с примерами
- Drobushkov V. *From RxJava 2 to Kotlin Flow: Threading*. -- https://proandroiddev.com/from-rxjava-2-to-kotlin-flow-threading-8618867e1955 -- детальный анализ различий subscribeOn/observeOn и flowOn
- Cash App. *Rx to Coroutines Concepts* (Parts 1-5). -- https://code.cash.app/rx-to-coroutines-concepts -- серия из 6 постов о миграции в масштабном проекте
- Capital One. *Coroutines and RxJava -- An Asynchronicity Comparison: Interop Library*. -- https://medium.com/capital-one-tech/coroutines-and-rxjava-an-asynchronicity-comparison-part-4-interop-library-4a2439a690f9
- Stefan M. *Our way of migrating from RxJava to Kotlin Coroutines*. -- https://stefma.medium.com/our-way-of-migrating-from-rxjava-to-kotlin-coroutines-edbb648e6277 -- практический опыт команды

### Выступления

- Wharton J. -- Twitter/X дискуссии о RxJava и корутинах: "RxJava is a high-level API around manual implementations of callbacks and state machines. Coroutines are a compiler transformation to create callbacks and state machines. There's no reason we can't have a high-level Rx API around coroutines."
- Vivo M. *Migrating from LiveData to Kotlin Flow*. -- Android Dev Summit, рекомендации по миграции UI-слоя

---

## Проверь себя

> [!question]- Почему при миграции нужно заменять flatMap на flatMapMerge, а не на flatMapConcat?
> RxJava `flatMap` выполняет inner Observable **параллельно**. Flow `flatMapConcat` -- **последовательно**. Прямая замена flatMap → flatMapConcat превратит параллельные запросы в последовательные, что может ухудшить производительность в разы. Правильный аналог для параллельного flatMap -- `flatMapMerge`. Для switchMap (отмена предыдущего) -- `flatMapLatest`.

> [!question]- Чем различается семантика subscribeOn (RxJava) и flowOn (Flow)?
> `subscribeOn` влияет на **весь upstream** цепочки **независимо от позиции** вызова -- он определяет, на каком Scheduler произойдёт подписка. `flowOn` влияет **только на операторы выше** себя в цепочке -- его позиция критична. В RxJava направление "от источника вниз", в Flow -- "от collector вверх". Это самая частая причина ошибок при миграции.

> [!question]- BehaviorSubject заменяется на StateFlow. Какие есть подводные камни?
> 1) StateFlow имеет **встроенный distinctUntilChanged** -- повторные эмиссии одинаковых значений (по `equals`) игнорируются, BehaviorSubject пропускает все. 2) StateFlow **требует начальное значение** в конструкторе, BehaviorSubject может быть создан без начального значения (`BehaviorSubject.create()`). 3) StateFlow использует `equals` для сравнения -- для data class это может быть неожиданно.

> [!question]- Какая стратегия миграции рекомендуется для крупного проекта?
> **Bottom-up** (снизу вверх): Data Layer → Domain Layer → Presentation Layer. 1) Data Layer мигрируется первым -- Retrofit и Room нативно поддерживают suspend. 2) Domain Layer (UseCases) -- переводим интерфейсы на suspend/Flow. 3) Presentation Layer -- последним, когда нижние слои готовы. Ключевой инструмент: `kotlinx-coroutines-rx3` для interop на границах слоёв во время миграции.

---

## Ключевые карточки

Какие основные типы RxJava маппятся на Coroutines/Flow?
?
Single<T> → suspend fun: T (one-shot). Maybe<T> → suspend fun: T? (nullable). Completable → suspend fun (Unit). Observable<T> → Flow<T> (cold stream). Flowable<T> → Flow<T> (backpressure встроена). BehaviorSubject → MutableStateFlow. PublishSubject → MutableSharedFlow(replay=0). CompositeDisposable → CoroutineScope/Job.

Чем отличается subscribeOn от flowOn?
?
subscribeOn (RxJava) влияет на весь upstream независимо от позиции в цепочке. flowOn (Flow) влияет только на операторы ВЫШЕ себя в цепочке -- позиция критична. Семантика "перевёрнута": RxJava думает от создания вниз, Flow -- от сбора вверх. observeOn переключает downstream, а в Flow downstream определяется контекстом scope.

Как мигрировать flatMap из RxJava в Flow?
?
RxJava flatMap параллелен по умолчанию → Flow flatMapMerge (параллельный аналог). RxJava concatMap → Flow flatMapConcat (последовательный). RxJava switchMap → Flow flatMapLatest (отмена предыдущего). Ошибка: слепо заменять flatMap на flatMapConcat, превращая параллельные операции в последовательные.

Как организовать стратегию миграции большого проекта?
?
4 фазы: 1) Coexistence -- добавить kotlinx-coroutines-rx3 и корутины рядом с RxJava. 2) New Code Policy -- весь новый код на корутинах, lint запрещает RxJava в новых файлах. 3) Layer Migration -- bottom-up: data → domain → presentation. 4) Cleanup -- удалить RxJava зависимости. Ключ: interop-библиотека для бесшовного моста на границах.

Какие ловушки при миграции BehaviorSubject → StateFlow?
?
1) StateFlow имеет встроенный distinctUntilChanged -- дубликаты не эмитятся (BehaviorSubject эмитит все). 2) StateFlow требует начальное значение, BehaviorSubject может быть без него. 3) SharedFlow(replay=0) для PublishSubject: emit() -- suspend, может зависнуть без подписчиков. Нужен extraBufferCapacity или tryEmit.

Как обрабатывать ошибки при миграции с RxJava на Flow?
?
onErrorReturn { value } → catch { emit(value) }. onErrorResumeNext { obs } → catch { emitAll(flow) }. retry(n) → retry(n). retryWhen { errors → } → retryWhen { cause, attempt → boolean }. Важно: RxJava имеет глобальный error handler (RxJavaPlugins), Flow -- нет. Необработанная ошибка в Flow крашит корутину.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубиться | [[android-rxjava]] | Полный справочник RxJava для понимания, что именно мигрируем |
| Основа | [[kotlin-coroutines]] | Фундамент корутин, без которого миграция невозможна |
| Основа | [[kotlin-flow]] | Flow API -- целевой стандарт миграции |
| Практика | [[android-coroutines-guide]] | Корутины в Android: scope, lifecycle, best practices |
| Практика | [[android-flow-guide]] | Flow в Android: collectAsStateWithLifecycle, Room + Flow |
| Ошибки | [[android-coroutines-mistakes]] | Типичные ошибки при работе с корутинами -- чтобы не наступить на новые грабли |
| Контекст | [[android-async-evolution]] | Эволюция асинхронности: AsyncTask → RxJava → Coroutines |
| Обзор | [[android-overview]] | Вернуться к карте раздела |

*Проверено: 2026-02-14*
