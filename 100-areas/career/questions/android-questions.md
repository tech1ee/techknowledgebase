---
title: "Android Interview Questions 2025: 50+ вопросов с ответами"
created: 2025-12-26
modified: 2025-12-26
type: reference
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/intermediate
  - interview
related:
  - "[[technical-interview]]"
  - "[[kotlin-questions]]"
  - "[[architecture-questions]]"
prerequisites:
  - "[[interview-process]]"
---

# Android Interview Questions: что спрашивают в 2025

Jetpack Compose — must-know для любого интервью в 2025. Lifecycle вопросы остаются фундаментом. Coroutines заменили RxJava в большинстве кодовых баз. Этот справочник — 50+ реальных вопросов с ответами, которые спрашивают в FAANG и top-tier компаниях.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Android разработка** | Минимум 1+ год опыта | Android Developer docs |
| **Kotlin** | Язык Android разработки | [[kotlin-questions]] |
| **Jetpack Compose** | UI framework в 2025 | Android Compose docs |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | ✅ Да | Изучай вопросы как roadmap |
| **Middle** | ✅ Да | Проработай все темы глубоко |
| **Senior** | ✅ Да | Освежи знания, фокус на "почему" |

### Терминология для новичков

> 💡 **Android Interview Questions** = типичные вопросы, которые спрашивают на собеседованиях. Не зубрить ответы, а понять концепции — интервьюер видит когда отвечаешь заученно.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Lifecycle** | Жизненный цикл Activity/Fragment | **Распорядок дня** — когда просыпается, работает, засыпает |
| **Configuration Change** | Изменение конфигурации (поворот экрана) | **Переезд** — всё пересоздаётся |
| **Process Death** | Система убила приложение в фоне | **Внезапное отключение** — всё из памяти пропало |
| **Recomposition** | Перерисовка UI в Compose | **Перерисовка картины** — только изменившиеся части |
| **State Hoisting** | Подъём состояния вверх по иерархии | **Передача ключей начальнику** — контроль на уровень выше |
| **Side Effect** | Действие за пределами composable функции | **Побочный эффект** — что-то кроме рисования UI |
| **Coroutine** | Лёгкий поток для асинхронного кода | **Помощник** — делает работу не блокируя главный поток |
| **Flow** | Асинхронный поток данных | **Конвейер** — данные текут как вода |
| **StateFlow** | Flow с текущим значением | **Табло** — всегда показывает актуальное значение |
| **SavedStateHandle** | Сохранение состояния при process death | **Резервная копия** — автоматически сохраняется |

---

## Lifecycle

### Что такое Activity Lifecycle?

```
onCreate()   → Activity создаётся
onStart()    → Становится видимой
onResume()   → Получает фокус, можно взаимодействовать
onPause()    → Теряет фокус (другая activity поверх)
onStop()     → Больше не видна
onDestroy()  → Уничтожается

Ключевой момент: onSaveInstanceState() вызывается ПЕРЕД onStop()
```

### Что происходит при повороте экрана?

```
1. onPause()
2. onStop()
3. onSaveInstanceState()
4. onDestroy()
5. onCreate() — новая Activity
6. onStart()
7. onRestoreInstanceState()
8. onResume()

Как сохранить данные:
• Простые данные → onSaveInstanceState(Bundle)
• Сложные объекты → ViewModel (переживает rotation)
• Очень большие → SavedStateHandle или persist to disk
```

### В чём разница между onSaveInstanceState и onPause?

```
onPause():
• Вызывается всегда когда activity теряет фокус
• Для сохранения данных в persistent storage

onSaveInstanceState():
• Вызывается только если system может убить activity
• Для сохранения UI state (scroll position, text input)
• НЕ гарантировано при user-initiated destruction (back button)
```

### Как ViewModel переживает configuration change?

```
ViewModel хранится в ViewModelStore, который привязан к:
• Activity → retained configuration instance
• Fragment → FragmentManager

При rotation:
1. Activity уничтожается
2. ViewModelStore сохраняется в NonConfigurationInstances
3. Новая Activity получает тот же ViewModelStore
4. ViewModel остаётся живым

Когда ViewModel очищается:
• Activity finish() (не rotation)
• Fragment detach с remove
• Навигация назад
```

### Что такое Process Death и как с ним работать?

```
Process Death — система убивает приложение в background
для освобождения памяти.

Проблема:
• ViewModel теряется (это in-memory)
• Activity lifecycle пропускается
• При возврате — пустой state

Решение:
1. SavedStateHandle в ViewModel
   val state = savedStateHandle.getStateFlow("key", default)

2. onSaveInstanceState для UI state
   override fun onSaveInstanceState(outState: Bundle) {
       outState.putInt("scrollPosition", position)
   }

3. Persist critical data to disk (Room, DataStore)

Тестирование:
Developer Options → Don't keep activities
```

---

## Jetpack Compose

### Что такое Recomposition?

```
Recomposition — процесс пере-вызова composable функций
когда state меняется.

Когда происходит:
• State читаемый внутри composable меняется
• Compose runtime решает перерисовать

Важно:
• Composables должны быть idempotent (результат зависит только от input)
• Composables должны быть side-effect free
• Recomposition может происходить частично (skip unaffected)
```

### Как избежать лишних recomposition?

```
1. Используй remember для кэширования
   val filtered = remember(list) { list.filter { ... } }

2. Используй derivedStateOf для computed state
   val showButton by remember {
       derivedStateOf { scrollState.value > 100 }
   }

3. Используй key() для идентификации items
   items(list, key = { it.id }) { item -> ... }

4. Передавай lambda напрямую, не создавай в теле
   ❌ onClick = { viewModel.onClick() }
   ✓  onClick = viewModel::onClick

5. Используй Stable/Immutable аннотации
   @Stable class UserState(...)
```

### В чём разница между remember и rememberSaveable?

```
remember:
• Переживает recomposition
• НЕ переживает configuration change
• НЕ переживает process death

rememberSaveable:
• Переживает recomposition
• Переживает configuration change (rotation)
• Переживает process death
• Сохраняет в Bundle, должен быть Parcelable/Saveable

Когда использовать:
• remember: computed values, objects that can be recreated
• rememberSaveable: user input, scroll position, UI state
```

### Что такое Side Effects в Compose?

```
Side Effect — изменение состояния вне composable scope
(network call, analytics, navigation).

Проблема: Composables могут вызываться много раз.
Side effects должны быть controlled.

LaunchedEffect(key):
• Запускает coroutine когда key меняется
• Отменяется при leave composition или key change
LaunchedEffect(Unit) {
    viewModel.loadData()
}

DisposableEffect(key):
• Для cleanup (listeners, subscriptions)
DisposableEffect(lifecycle) {
    val observer = LifecycleEventObserver { ... }
    lifecycle.addObserver(observer)
    onDispose { lifecycle.removeObserver(observer) }
}

SideEffect:
• После каждой successful recomposition
• Для синхронизации с non-compose code
```

### Что такое Composition Local?

```
CompositionLocal — dependency injection в Compose tree.

Создание:
val LocalTheme = compositionLocalOf { Theme.Light }

Предоставление:
CompositionLocalProvider(LocalTheme provides Theme.Dark) {
    ChildComposable()
}

Использование:
val theme = LocalTheme.current

Встроенные:
• LocalContext
• LocalConfiguration
• LocalDensity
• LocalLifecycleOwner
```

---

## Coroutines

### В чём разница между launch и async?

```
launch:
• Fire-and-forget
• Возвращает Job
• Для side effects (save to DB, log, navigate)

async:
• Возвращает Deferred<T> с результатом
• Нужно вызвать await() для получения
• Для parallel computations

val job = launch { saveData() }  // no result

val deferred = async { fetchData() }
val result = deferred.await()  // suspend until ready

Parallel execution:
val a = async { fetchA() }
val b = async { fetchB() }
val combined = a.await() + b.await()  // runs in parallel
```

### Что такое Structured Concurrency?

```
Structured Concurrency — coroutines привязаны к scope
и автоматически отменяются вместе с ним.

Правила:
1. Child coroutine наследует context от parent
2. Parent ждёт завершения всех children
3. Если parent отменён — все children отменяются
4. Если child fails — parent отменяется

viewModelScope.launch {  // parent
    launch { fetchA() }   // child 1
    launch { fetchB() }   // child 2
}
// Если ViewModel cleared — обе coroutines отменяются

SupervisorScope:
• Failure одного child не отменяет других
• Используй для независимых задач (UI events)
```

### В чём разница между CoroutineScope и SupervisorScope?

```
CoroutineScope (обычный Job):
• Если child fails → parent и все siblings отменяются
• Используй когда tasks связаны

SupervisorScope (SupervisorJob):
• Если child fails → другие children продолжают
• Используй для независимых tasks

coroutineScope {
    launch { taskA() }  // if fails...
    launch { taskB() }  // ...this is cancelled too
}

supervisorScope {
    launch { taskA() }  // if fails...
    launch { taskB() }  // ...this continues
}
```

### Как обрабатывать exceptions в Coroutines?

```
launch:
• Exception propagates to parent
• Используй CoroutineExceptionHandler

async:
• Exception stored in Deferred
• Throws при await()

val handler = CoroutineExceptionHandler { _, e ->
    Log.e("Error", e.message)
}

scope.launch(handler) {
    throw RuntimeException("Oops")
}

Для async:
try {
    val result = async { riskyOperation() }.await()
} catch (e: Exception) {
    // handle
}

SupervisorScope + try-catch в каждом launch
— best practice для UI operations
```

### Что такое Flow и когда использовать?

```
Flow — cold asynchronous stream of values.

Когда использовать:
• Database changes (Room returns Flow)
• UI state updates
• Search с debounce
• Multiple values over time

val searchFlow = searchQuery
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { query ->
        repository.search(query)
    }

StateFlow vs SharedFlow:

StateFlow:
• Всегда имеет current value
• Replays last value новым collectors
• distinctUntilChanged by default
• Для UI state

SharedFlow:
• Может не иметь initial value
• Configurable replay и buffer
• Для events (navigation, snackbar)
```

---

## Memory & Performance

### Как обнаружить memory leak?

```
Инструменты:
1. LeakCanary — автоматически детектит в debug
2. Android Studio Profiler → Memory
3. MAT (Memory Analyzer Tool)

Частые источники leaks:
• Static reference к Context/View
• Inner class с reference на outer Activity
• Незакрытые listeners/callbacks
• Coroutines без proper scope
• Handler с reference на Activity

Как избежать:
• Используй applicationContext где возможно
• WeakReference для callbacks
• viewModelScope / lifecycleScope
• Unregister listeners в onDestroy/onDispose
```

### Что такое ANR и как избежать?

```
ANR (Application Not Responding):
• Main thread blocked > 5 секунд
• BroadcastReceiver > 10 секунд

Причины:
• Network на main thread
• Heavy computation на main thread
• Database operations на main thread
• Deadlock

Как избежать:
• Все I/O на Dispatchers.IO
• Heavy work на Dispatchers.Default
• Используй coroutines/WorkManager
• StrictMode в debug для detection
```

### Как оптимизировать startup time?

```
Измерение:
adb shell am start-activity -W -n package/.Activity

Оптимизации:

1. Lazy initialization
   val heavyObject by lazy { ... }

2. Убрать лишнее из Application.onCreate()

3. App Startup library для lazy ContentProviders

4. Baseline Profiles
   • Compile critical paths ahead of time
   • 30%+ improvement в некоторых случаях

5. Splash Screen API вместо custom splash

6. Avoid synchronous disk I/O в onCreate
```

---

## Storage

### Room vs SQLite — когда что использовать?

```
Room — ВСЕГДА для нового кода.

Room преимущества:
• Compile-time SQL verification
• Boilerplate reduction (no cursors)
• LiveData/Flow integration
• Migration support
• Testing support

SQLite напрямую:
• Legacy code
• Extreme performance requirements
• Custom SQL features не поддерживаемые Room
```

### Как мигрировать SharedPreferences → DataStore?

```
Почему мигрировать:
• SharedPreferences блокирует main thread при commit()
• Нет type safety
• Нет Flow support

DataStore Preferences:
val dataStore = context.createDataStore("settings")

// Read
val flow: Flow<String> = dataStore.data.map { prefs ->
    prefs[KEY] ?: default
}

// Write
dataStore.edit { prefs ->
    prefs[KEY] = value
}

Proto DataStore:
• Type-safe с Protocol Buffers
• Для complex data structures

Миграция:
val dataStore = context.createDataStore(
    name = "settings",
    migrations = listOf(SharedPreferencesMigration(context, "old_prefs"))
)
```

---

## Networking

### Как реализовать retry с exponential backoff?

```kotlin
suspend fun <T> retryWithBackoff(
    times: Int = 3,
    initialDelayMs: Long = 100,
    maxDelayMs: Long = 10000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelayMs
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            // Log error
        }
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
    }
    return block() // last attempt, let exception propagate
}
```

### Как реализовать offline-first?

```
Стратегия:
1. Показать cached data сразу
2. Fetch fresh в background
3. Update UI когда fresh приходит
4. Handle errors gracefully

fun getData(): Flow<Resource<Data>> = flow {
    // 1. Emit cached
    val cached = localDataSource.get()
    if (cached != null) emit(Resource.Success(cached))

    // 2. Fetch fresh
    try {
        val fresh = remoteDataSource.fetch()
        localDataSource.save(fresh)
        emit(Resource.Success(fresh))
    } catch (e: Exception) {
        if (cached == null) emit(Resource.Error(e))
        // else: keep showing cached
    }
}
```

---

## Quick Reference

### Часто путают

| Вопрос | Ответ |
|--------|-------|
| Fragment vs Activity lifecycle | Fragment имеет onCreateView/onDestroyView |
| ViewBinding vs DataBinding | ViewBinding — только views, DataBinding — + expressions |
| LiveData vs StateFlow | StateFlow требует initial value, no lifecycle-aware |
| remember vs mutableStateOf | remember кэширует, mutableStateOf создаёт state |

### Red Flags в ответах

```
❌ "Я не использовал Compose, только XML"
   → Compose обязателен в 2025

❌ "Использую AsyncTask для network"
   → Deprecated, используй Coroutines

❌ "Сохраняю в SharedPreferences синхронно"
   → Блокирует main thread

❌ "Не знаю разницу между launch и async"
   → Базовые Coroutines обязательны
```

---

## Связь с другими темами

- **[[technical-interview]]** — Android-вопросы — это часть более широкого технического интервью, которое также включает алгоритмы и System Design. Понимание формата и ожиданий технического раунда помогает правильно дозировать глубину ответов. На Senior-уровне важно не просто знать ответ, а объяснить trade-offs и практический опыт.

- **[[kotlin-questions]]** — Kotlin и Android неразделимы: coroutines, Flow, sealed classes используются в каждом Android-проекте. Kotlin-вопросы дополняют Android-вопросы, и на интервью их часто смешивают в одном раунде. Глубокое знание Kotlin internals (inline, reified, delegation) отличает Senior от Mid.

- **[[architecture-questions]]** — Архитектурные вопросы (MVVM vs MVI, Clean Architecture, модуляризация) — следующий уровень после базовых Android-вопросов. На Senior-интервью архитектура занимает до 30% технического раунда. Понимание архитектурных паттернов показывает способность проектировать системы, а не просто писать код.

---

## Источники и дальнейшее чтение

- **McDowell G.L. (2015). Cracking the Coding Interview.** — Фундаментальный справочник по подготовке к техническим интервью. Хотя фокус на алгоритмах, методология подготовки и формат ответов применимы к Android-вопросам. Незаменима для понимания, как думает интервьюер.

- **Xu A. (2020). System Design Interview.** — System Design вопросы всё чаще появляются на Android-интервью: «Design offline-first app», «Design image loading library». Эта книга даёт структурированный подход к таким задачам, адаптируемый под mobile-специфику.

---

## Источники

- [GitHub: Android Interview Questions](https://github.com/amitshekhariitbhu/android-interview-questions)
- [Medium: Senior Android Lifecycle](https://medium.com/@sandeepkella23/senior-android-developer-interview-questions-and-answers-lifecycle-9dce4f47aace)
- [Curotec: 125 Android/Kotlin Questions](https://www.curotec.com/interview-questions/125-android-kotlin-interview-questions/)
- [GeeksforGeeks: Top 50 Android Questions](https://www.geeksforgeeks.org/android/top-50-android-interview-questions-answers-sde-i-to-sde-iii/)

---

## Куда дальше

### Углубить понимание

**Lifecycle и компоненты:**
→ [[android-activity-lifecycle]] — детальный разбор lifecycle callbacks и edge cases
→ [[android-viewmodel-internals]] — как ViewModel переживает configuration change под капотом
→ [[android-state-management]] — паттерны управления состоянием

**Compose:**
→ [[android-compose-internals]] — recomposition, stability, smart recomposition
→ [[android-compose]] — Compose overview и migration

**Coroutines:**
→ [[kotlin-coroutines]] — structured concurrency, dispatchers, Job hierarchy
→ [[kotlin-flow]] — Flow vs StateFlow vs SharedFlow детально
→ [[android-coroutines-mistakes]] — частые ошибки и как их избежать

**Архитектура:**
→ [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture на практике
→ [[android-repository-pattern]] — Repository pattern правильно

### Подготовка к интервью

**Связанные вопросники:**
→ [[kotlin-questions]] — Kotlin вопросы (тесно связаны с Android)
→ [[architecture-questions]] — архитектурные паттерны

**Как эффективно готовиться:**
→ [[learning-complex-things]] — Active Recall, Spaced Repetition
→ [[deliberate-practice]] — практика на грани способностей

---

*Обновлено: 2025-12-26*

---

*Проверено: 2026-01-09*
