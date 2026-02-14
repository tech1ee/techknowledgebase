---
title: "Kotlin Coroutines в Android: полный практический гайд"
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
  - "[[kotlin-coroutines]]"
  - "[[android-threading]]"
  - "[[android-coroutines-mistakes]]"
  - "[[android-flow-guide]]"
  - "[[android-viewmodel-internals]]"
prerequisites:
  - "[[kotlin-coroutines]]"
  - "[[android-threading]]"
reading_time: 50
difficulty: 6
study_status: not_started
mastery: 0
---

# Kotlin Coroutines в Android: полный практический гайд

Корутины на уровне языка Kotlin -- это один набор знаний. Корутины в контексте Android-приложения -- принципиально другой. Между `suspend fun` из учебника и продакшн-кодом с `repeatOnLifecycle`, Hilt-инъекцией диспатчеров и offline-first паттерном лежит пропасть. Этот гайд закрывает именно её: он не повторяет теорию CPS и structured concurrency (это в [[kotlin-coroutines]]), а сосредоточен на платформенных скоупах, lifecycle-aware подходах, интеграции с Jetpack и проверенных паттернах.

> **Scope этого файла:** Практическое применение корутин на платформе Android. Языковые основы -- [[kotlin-coroutines]]. Типичные ошибки -- [[android-coroutines-mistakes]]. StateFlow/SharedFlow для UI -- [[android-state-management]]. Внутреннее устройство viewModelScope -- [[android-viewmodel-internals]].

---

## Зачем это нужно

### Проблема: разрыв между теорией и Android-реальностью

Вы изучили корутины на уровне языка: `suspend`, `launch`, `async`, `CoroutineScope`, `Dispatchers`. Но при написании реального Android-приложения немедленно возникают вопросы:

- В каком скоупе запускать корутину -- `viewModelScope`, `lifecycleScope`, кастомном?
- Почему `lifecycleScope.launch { flow.collect {} }` -- это утечка ресурсов?
- Как правильно инжектить диспатчеры через Hilt для тестируемости?
- Как Room, Retrofit, WorkManager, DataStore работают с корутинами?
- Что происходит с корутинами при configuration change и process death?

Этот гайд отвечает на каждый из этих вопросов с кодом, диаграммами и ссылками на первоисточники.

### Зачем отдельный гайд, если есть kotlin-coroutines.md?

[[kotlin-coroutines]] описывает механику на уровне языка: как компилятор трансформирует `suspend` через CPS, что такое `CoroutineContext`, как работает structured concurrency. Это необходимая база, но она не отвечает на вопросы Android-разработчика:

| Вопрос | kotlin-coroutines.md | Этот гайд |
|--------|---------------------|-----------|
| Какой scope выбрать? | Описывает CoroutineScope абстрактно | viewModelScope vs lifecycleScope vs custom -- с обоснованием |
| Как безопасно собирать Flow в UI? | Flow как языковая конструкция | repeatOnLifecycle, collectAsStateWithLifecycle |
| Как тестировать корутины? | TestDispatcher упоминается | Инъекция Dispatchers через Hilt, TestScope |
| Как Room/Retrofit работают с suspend? | Не затрагивает | Подробные примеры для каждой Jetpack-библиотеки |
| Что происходит при rotation/process death? | Не Android-специфично | Полная матрица lifecycle-поведения |

### Актуальность 2025-2026

| Версия | Изменение | Влияние на корутины в Android |
|--------|-----------|-------------------------------|
| Kotlin 2.1 / kotlinx.coroutines 1.10+ | `limitedParallelism()` стабильный, улучшения cancellation | Более точный контроль параллелизма |
| Lifecycle 2.8+ | `collectAsStateWithLifecycle()` стабильный | Обязательный API для Compose + Flow |
| Room 2.7+ | Улучшенный suspend + Flow, исправлен deadlock при auto-close | Более надежная работа с базой |
| Compose 1.7+ | Stable `collectAsStateWithLifecycle` | Единый паттерн сбора Flow в Compose |
| Retrofit 2.11+ / 3.0 preview | Нативная поддержка suspend, улучшенный error handling | Упрощённая интеграция |
| WorkManager 2.10+ | `CoroutineWorker` как стандарт | Корутины для фоновых задач |

**Важный контекст:** Google официально рекомендует корутины как единственный подход к асинхронности в Android. RxJava переходит в режим maintenance. Все новые Jetpack-библиотеки проектируются с нативной поддержкой suspend/Flow. Знание корутин на платформенном уровне -- не опция, а необходимость для любого Android-разработчика уровня middle и выше.

---

## TL;DR

```
Scope выбора:
  viewModelScope     -- бизнес-логика, загрузка данных, переживает rotation
  lifecycleScope     -- только для launch { repeatOnLifecycle {} }
  @ApplicationScope  -- work outliving ViewModel (analytics, sync)
  Никогда GlobalScope.

Сбор Flow:
  Views:    lifecycleScope.launch { repeatOnLifecycle(STARTED) { flow.collect {} } }
  Compose:  val state = flow.collectAsStateWithLifecycle()

Dispatcher:
  Никогда не хардкодить -- инжектить через Hilt для тестируемости.
  Main.immediate для viewModelScope (дефолт), IO для сети/БД, Default для CPU.

Jetpack:
  Room      -- suspend для one-shot, Flow для observe, withTransaction для групп
  Retrofit  -- suspend API methods, try/catch HttpException + IOException
  DataStore -- Flow для чтения, suspend updateData для записи
  WorkManager -- CoroutineWorker.doWork() suspend
```

---

## Пререквизиты

| Тема | Файл | Что нужно знать |
|------|------|-----------------|
| Suspend, CPS, CoroutineContext | [[kotlin-coroutines]] | Как работают suspend-функции, что такое Continuation |
| Structured concurrency | [[kotlin-coroutines]] | Parent-child, SupervisorJob, cancellation propagation |
| Dispatchers | [[kotlin-coroutines]] | Main, IO, Default, Unconfined -- когда какой |
| Main Thread, ANR | [[android-threading]] | Почему UI однопоточный, Handler/Looper |
| Android Lifecycle | [[android-activity-lifecycle]] | onCreate..onDestroy, configuration change, process death |
| ViewModel internals | [[android-viewmodel-internals]] | ViewModelStore, NonConfigurationInstance, onCleared |

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **viewModelScope** | CoroutineScope внутри ViewModel; SupervisorJob + Dispatchers.Main.immediate; отменяется в onCleared() |
| **lifecycleScope** | CoroutineScope для LifecycleOwner (Activity/Fragment); отменяется при DESTROYED |
| **repeatOnLifecycle** | Suspend-функция, которая запускает блок при достижении state, отменяет при выходе ниже state, перезапускает при возврате |
| **collectAsStateWithLifecycle** | Compose-API для lifecycle-aware сбора Flow в State; внутри использует repeatOnLifecycle |
| **flowWithLifecycle** | Оператор на Flow, который emit'ит только когда lifecycle >= заданного state |
| **SupervisorJob** | Job, при котором failure одного child не отменяет siblings |
| **Main.immediate** | Dispatchers.Main без redispatch, если уже на Main Thread |
| **CoroutineWorker** | WorkManager Worker с suspend doWork() |
| **withContext** | Suspend-функция для смены Dispatcher без создания нового scope |
| **limitedParallelism** | Создаёт view поверх Dispatcher с ограничением параллелизма |
| **Process Death** | Система убивает процесс приложения; все корутины, память, in-memory state теряются |
| **Configuration Change** | Rotation, locale change; Activity пересоздаётся, но ViewModel (и viewModelScope) переживают |

---

## Android Scopes: полный каталог

### Обзор иерархии скоупов

```
Application Process
|
+-- @ApplicationScope (SupervisorJob + Dispatchers.Main.immediate)
|   |   живёт = весь процесс
|   |   use case: analytics, sync, кеш
|   |
|   +-- viewModelScope (SupervisorJob + Dispatchers.Main.immediate)
|   |   |   живёт = ViewModel (переживает rotation)
|   |   |   use case: бизнес-логика, загрузка данных
|   |   |
|   |   +-- coroutineScope { } / supervisorScope { }
|   |       |   живёт = пока все children не завершены
|   |       |   use case: параллельные запросы внутри ViewModel
|   |
|   +-- lifecycleScope (SupervisorJob + Dispatchers.Main.immediate)
|       |   живёт = Lifecycle (Activity/Fragment, уничтожается при DESTROYED)
|       |   use case: запуск repeatOnLifecycle, UI-only tasks
|       |
|       +-- repeatOnLifecycle(STARTED) { ... }
|           |   живёт = STARTED..STOPPED, перезапускается
|           |   use case: collect Flow для UI
```

### viewModelScope -- основной рабочий скоуп

**Конфигурация:** `SupervisorJob() + Dispatchers.Main.immediate`

**Почему это основной скоуп:**
- Переживает configuration change (rotation, locale change)
- Автоматически отменяется при `onCleared()` (когда Activity финально уничтожается или Fragment отсоединяется)
- SupervisorJob означает: failure одной корутины не убивает остальные
- Main.immediate означает: если уже на Main Thread, код выполняется сразу без redispatch

```kotlin
class UserViewModel(
    private val userRepository: UserRepository,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init {
        loadUser()
    }

    private fun loadUser() {
        // viewModelScope -- корутина переживёт rotation
        viewModelScope.launch {
            try {
                val user = userRepository.getUser() // suspend, IO внутри
                _uiState.value = UserUiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message)
            }
        }
    }

    fun trackScreenView() {
        // Другая корутина -- если упадёт, loadUser() не затронет (SupervisorJob)
        viewModelScope.launch {
            analyticsTracker.track("user_screen_viewed")
        }
    }
}
```

**Почему SupervisorJob, а не обычный Job?**

Обычный Job при failure дочерней корутины отменяет всех siblings и самого себя. Для ViewModel это катастрофично: если `trackScreenView()` упадёт, то `loadUser()` тоже отменится, и пользователь увидит пустой экран. SupervisorJob изолирует failures: каждая дочерняя корутина независима.

```
Обычный Job:                     SupervisorJob:
  Parent Job                       Parent Job (Supervisor)
  /        \                       /        \
child1    child2                 child1    child2
  X (fail)  -> cancelled!          X (fail)  -> still running
```

**Время жизни viewModelScope:**

```
Activity.onCreate() ---------> Activity.onDestroy() (rotation)
    |                               |
    |  ViewModel создан             |  ViewModel ЖИВ (NonConfigurationInstance)
    |  viewModelScope создан        |  viewModelScope АКТИВЕН
    |                               |
Activity.onCreate() (new) ---> Activity.onDestroy() (final, finish())
    |                               |
    |  ViewModel тот же             |  ViewModel.onCleared()
    |  viewModelScope тот же        |  viewModelScope.cancel()
                                    |  Все корутины отменены
```

> Внутреннее устройство viewModelScope, как он создаётся и хранится в ViewModelStore -- подробно в [[android-viewmodel-internals]].

### lifecycleScope -- скоуп UI-компонента

**Конфигурация:** `SupervisorJob() + Dispatchers.Main.immediate`

**Когда использовать:**
- Как "контейнер" для `repeatOnLifecycle`
- Для операций, которые не должны переживать уничтожение Activity/Fragment

**Когда НЕ использовать:**
- Для загрузки данных (не переживает rotation)
- Для `flow.collect {}` напрямую -- это утечка ресурсов

```kotlin
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // lifecycleScope -- запускаем repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state) // безопасно, корутина отменена при STOPPED
                }
            }
        }
    }
}
```

### repeatOnLifecycle -- механизм cancel+restart

**Проблема:** `lifecycleScope.launch { flow.collect {} }` продолжает собирать Flow даже когда Activity/Fragment в STOPPED state. Upstream Flow остаётся активным, тратит ресурсы (сеть, CPU, батарею).

**Решение:** `repeatOnLifecycle(Lifecycle.State.STARTED)`:

```
Timeline:
  CREATED --> STARTED --> RESUMED --> STOPPED --> STARTED --> STOPPED --> DESTROYED
                |                      |            |           |
                +-- launch block       |            +-- relaunch|
                                       +-- cancel               +-- cancel (final)
```

```kotlin
// ПРАВИЛЬНО: collect отменяется при STOPPED, перезапускается при STARTED
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        // Этот блок запускается каждый раз при STARTED
        // и отменяется при STOPPED
        viewModel.uiState.collect { state ->
            binding.textView.text = state.toString()
        }
    }
}

// НЕПРАВИЛЬНО: collect активен даже в background
lifecycleScope.launch {
    viewModel.uiState.collect { state -> // утечка!
        binding.textView.text = state.toString()
    }
}
```

**Почему repeatOnLifecycle, а не launchWhenStarted?**

`launchWhenStarted` (deprecated) лишь приостанавливает (suspend) корутину при уходе ниже STARTED, но не отменяет её. Upstream Flow остаётся активным и продолжает emit'ить значения, которые буферизуются. Это тратит ресурсы:

```
repeatOnLifecycle(STARTED):
  STARTED -> корутина запущена, collect активен
  STOPPED -> корутина ОТМЕНЕНА, upstream Flow останавливается
  STARTED -> корутина ПЕРЕЗАПУЩЕНА, новый collect

launchWhenStarted (deprecated):
  STARTED -> корутина запущена, collect активен
  STOPPED -> корутина ПРИОСТАНОВЛЕНА, но upstream Flow ЕЩЁ РАБОТАЕТ
  STARTED -> корутина возобновлена, получает буферизованные значения

Разница: repeatOnLifecycle ОТМЕНЯЕТ (cancel), launchWhenStarted ПРИОСТАНАВЛИВАЕТ (suspend).
Отмена = upstream останавливается. Приостановка = upstream продолжает работать в фоне.
```

**Множественный сбор в одном repeatOnLifecycle:**

```kotlin
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        // Каждый collect в отдельной корутине внутри блока
        launch {
            viewModel.uiState.collect { updateMainUI(it) }
        }
        launch {
            viewModel.notifications.collect { showNotification(it) }
        }
        launch {
            viewModel.navigation.collect { navigate(it) }
        }
    }
}
```

### flowWithLifecycle -- для одного Flow

Когда нужно lifecycle-aware поведение только для одного Flow, `flowWithLifecycle` удобнее:

```kotlin
lifecycleScope.launch {
    viewModel.uiState
        .flowWithLifecycle(viewLifecycleOwner.lifecycle, Lifecycle.State.STARTED)
        .collect { state ->
            updateUI(state)
        }
}
```

Внутри `flowWithLifecycle` использует `repeatOnLifecycle`. Для нескольких Flow предпочтительнее один блок `repeatOnLifecycle` с несколькими `launch`.

### collectAsStateWithLifecycle -- для Jetpack Compose

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    // Собирает Flow lifecycle-aware:
    // подписка при STARTED, отписка при STOPPED
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> LoadingIndicator()
        is UserUiState.Success -> UserContent(state.user)
        is UserUiState.Error -> ErrorMessage(state.message)
    }
}
```

`collectAsStateWithLifecycle()` -- обязательный API для Compose. Не используйте `collectAsState()` -- он не учитывает lifecycle и продолжает сбор в background.

### Custom Scopes

#### Application-level scope через ProcessLifecycleOwner

```kotlin
// Для операций, которые должны пережить все ViewModel
val applicationScope = ProcessLifecycleOwner.get().lifecycleScope
```

Но лучше -- через Hilt (см. раздел "Hilt + Coroutines").

#### Repository-level scope

```kotlin
class SyncRepository(
    private val externalScope: CoroutineScope, // инжектируется
    private val api: SyncApi,
    private val db: SyncDao
) {
    // Операция, которая должна завершиться даже если ViewModel отменён
    suspend fun syncData() {
        externalScope.launch {
            val data = api.fetchAll()
            db.insertAll(data)
        }.join() // ждём завершения
    }
}
```

### Принятие решения: какой скоуп выбрать

Алгоритм выбора скоупа в виде дерева решений:

```
Вопрос: Операция привязана к конкретному экрану?
  |
  +-- ДА: Должна ли пережить rotation?
  |    |
  |    +-- ДА: viewModelScope (90% случаев)
  |    |
  |    +-- НЕТ: lifecycleScope (редко, только для UI-only задач)
  |
  +-- НЕТ: Должна ли завершиться даже если пользователь ушёл?
       |
       +-- ДА: Нужна ли guaranteed execution (выживает process death)?
       |    |
       |    +-- ДА: WorkManager + CoroutineWorker
       |    |
       |    +-- НЕТ: @ApplicationScope
       |
       +-- НЕТ: viewModelScope (отменится при уходе -- это ok)
```

#### Когда нужен custom scope

| Ситуация | Скоуп | Почему |
|----------|-------|--------|
| Загрузка данных для экрана | `viewModelScope` | Переживает rotation, отменяется при уходе с экрана |
| Сбор Flow для UI | `lifecycleScope` + `repeatOnLifecycle` | Отменяется при STOPPED |
| Отправка аналитики | `@ApplicationScope` | Должна завершиться независимо от экрана |
| Синхронизация с сервером | `@ApplicationScope` | Не привязана к конкретному экрану |
| Compose UI events | `rememberCoroutineScope()` | Привязан к Composition lifecycle |

---

## Lifecycle-aware корутины

### Configuration Change (rotation)

```
Rotation:
  Activity.onDestroy() --> Activity.onCreate()
       |                        |
       |  ViewModel НЕ уничтожается (NonConfigurationInstance)
       |  viewModelScope НЕ отменяется
       |
       +-- lifecycleScope ОТМЕНЯЕТСЯ --> новый lifecycleScope создаётся
```

```kotlin
class SearchViewModel : ViewModel() {

    private val _results = MutableStateFlow<List<SearchResult>>(emptyList())
    val results: StateFlow<List<SearchResult>> = _results.asStateFlow()

    fun search(query: String) {
        viewModelScope.launch {
            // Эта корутина переживёт rotation.
            // Пользователь повернул экран во время загрузки --
            // результат всё равно попадёт в StateFlow,
            // новый Fragment соберёт его через repeatOnLifecycle.
            val data = repository.search(query)
            _results.value = data
        }
    }
}
```

### Process Death

```
Process Death:
  Система убивает процесс --> ВСЁ теряется:
    - Все корутины (все скоупы)
    - Все in-memory данные (StateFlow, переменные)
    - ViewModel (полностью)

  Восстановление:
    - Bundle/SavedStateHandle (до 500KB)
    - Room/DataStore (persistent storage)
    - WorkManager (для guaranteed execution)
```

**Матрица: что переживает что:**

```
+---------------------------+-----------+-----------+-----------+
|                           | Config    | Process   | App       |
|                           | Change    | Death     | Restart   |
+---------------------------+-----------+-----------+-----------+
| viewModelScope            | ДА        | НЕТ       | НЕТ       |
| lifecycleScope            | НЕТ       | НЕТ       | НЕТ       |
| @ApplicationScope         | ДА        | НЕТ       | НЕТ       |
| StateFlow (in-memory)     | ДА (VM)   | НЕТ       | НЕТ       |
| SavedStateHandle          | ДА        | ДА        | НЕТ       |
| Room/DataStore            | ДА        | ДА        | ДА        |
| WorkManager               | ДА        | ДА        | ДА        |
+---------------------------+-----------+-----------+-----------+
```

Стратегия: используйте `viewModelScope` + `StateFlow` для быстрых данных (переживают rotation), `SavedStateHandle` для критичного input (переживает process death), `Room/DataStore` для persistent данных, `WorkManager` для guaranteed execution.

**Паттерн восстановления с SavedStateHandle:**

```kotlin
class SearchViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {

    // Последний запрос сохраняется в SavedStateHandle (переживает process death)
    private val lastQuery = savedStateHandle.getStateFlow("query", "")

    val results: StateFlow<List<SearchResult>> = lastQuery
        .flatMapLatest { query ->
            if (query.isBlank()) flowOf(emptyList())
            else repository.searchFlow(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun search(query: String) {
        savedStateHandle["query"] = query // сохранится при process death
    }
}
```

> Подробности о SavedStateHandle и его интеграции с ViewModel -- в [[android-viewmodel-internals]].

### Fragment: viewLifecycleOwner vs this

```
Fragment Lifecycle:
  onAttach -> onCreate -> onCreateView -> onViewCreated -> onStart -> onResume
                                                                         |
  onPause <- onStop <- onDestroyView <- ... (backstack) ... -> onCreateView
                                |
                         View уничтожен,
                         но Fragment жив!
```

**Критическое различие:**

```kotlin
class UserFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ПРАВИЛЬНО: привязано к lifecycle View
        // Отменяется в onDestroyView -- безопасно обращаться к binding
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { updateUI(it) }
            }
        }

        // ОПАСНО: привязано к lifecycle самого Fragment
        // Fragment может пережить свой View (при navigation + backstack)
        // --> обращение к binding после onDestroyView --> crash
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { updateUI(it) } // может упасть!
            }
        }
    }
}
```

**Правило:** В `onViewCreated` и далее всегда используйте `viewLifecycleOwner.lifecycleScope`, не `this.lifecycleScope`.

### Service: LifecycleService

```kotlin
class SyncService : LifecycleService() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)

        // lifecycleScope привязан к lifecycle Service
        lifecycleScope.launch {
            try {
                startForeground(NOTIFICATION_ID, createNotification())
                performSync() // long-running suspend
            } finally {
                stopSelf()
            }
        }

        return START_NOT_STICKY
    }

    private suspend fun performSync() {
        withContext(Dispatchers.IO) {
            repository.syncAllData()
        }
    }
}
```

**Foreground Service + длительная корутина:**

```kotlin
class UploadService : LifecycleService() {

    private val uploadJob = MutableStateFlow<Job?>(null)

    fun startUpload(files: List<Uri>) {
        val job = lifecycleScope.launch {
            files.forEachIndexed { index, uri ->
                ensureActive() // проверяем, не отменён ли
                uploadFile(uri)
                updateNotification(progress = (index + 1f) / files.size)
            }
        }
        uploadJob.value = job
    }

    override fun onDestroy() {
        // lifecycleScope отменится автоматически,
        // но можно явно обработать cleanup
        super.onDestroy()
    }
}
```

### Миграция с RxJava

Если ваш проект мигрирует с RxJava на корутины, вот маппинг концепций:

```
+---------------------------+---------------------------+
| RxJava                    | Coroutines                |
+---------------------------+---------------------------+
| Single<T>                 | suspend fun(): T          |
| Completable               | suspend fun()             |
| Observable<T>             | Flow<T>                   |
| Flowable<T> (backpressure)| Flow<T> (suspension-based)|
| BehaviorSubject           | MutableStateFlow          |
| PublishSubject             | MutableSharedFlow         |
| subscribeOn(IO)           | withContext(Dispatchers.IO)|
| observeOn(mainThread)     | Dispatchers.Main / collect|
| CompositeDisposable       | CoroutineScope (auto)     |
| dispose()                 | scope.cancel() (auto)     |
+---------------------------+---------------------------+
```

Библиотека `kotlinx-coroutines-rx3` предоставляет bridge-функции: `Observable.asFlow()`, `Flow.asObservable()`, `suspend fun await()` для Single. Это позволяет мигрировать постепенно, модуль за модулем.

**Стратегия постепенной миграции:**
1. Новый код пишется на корутинах
2. Существующие Repository постепенно переводятся на suspend/Flow
3. ViewModel используют корутины, bridge-функции для legacy Repository
4. Последний шаг -- удаление RxJava зависимости из build.gradle

```kotlin
// Bridge: RxJava Repository -> Coroutine ViewModel
class LegacyRepository {
    fun getUsers(): Observable<List<User>> = api.getUsers() // RxJava
}

class ModernViewModel(
    private val legacyRepo: LegacyRepository
) : ViewModel() {

    val users: StateFlow<List<User>> = legacyRepo.getUsers()
        .asFlow()  // Observable -> Flow (bridge)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
}
```

---

## Интеграция с Jetpack

### Room + Coroutines

Room нативно поддерживает корутины через `room-ktx`. Три паттерна:

#### Suspend для one-shot операций

```kotlin
@Dao
interface UserDao {
    // INSERT/UPDATE/DELETE -- suspend, выполняются на Room executor thread
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)

    @Update
    suspend fun update(user: User)

    @Delete
    suspend fun delete(user: User)

    // SELECT one-shot -- suspend, возвращает результат один раз
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: String): User?

    @Query("SELECT COUNT(*) FROM users")
    suspend fun getUserCount(): Int
}
```

#### Flow для reactive-наблюдения

```kotlin
@Dao
interface UserDao {
    // Flow -- автоматический re-emit при изменении таблицы
    @Query("SELECT * FROM users ORDER BY name ASC")
    fun observeAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    fun observeUser(userId: String): Flow<User?>
}

// В ViewModel:
class UserListViewModel(private val userDao: UserDao) : ViewModel() {

    val users: StateFlow<List<User>> = userDao.observeAllUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

**Как Room обрабатывает suspend и Flow внутри:**

Room при компиляции (KSP/KAPT) генерирует реализацию DAO. Для suspend-функций он:
1. Оборачивает SQL-операцию в `Callable`
2. Выполняет на специальном `ArchTaskExecutor.getIOThreadExecutor()` (или Room transaction executor)
3. Возобновляет корутину с результатом

Для `Flow<T>`:
1. Room создаёт `InvalidationTracker.Observer` для наблюдаемых таблиц
2. При любом INSERT/UPDATE/DELETE в эти таблицы -- observer получает уведомление
3. Room перевыполняет запрос и emit'ит новое значение в Flow
4. Flow -- cold: запрос выполняется только при наличии collector

```
Room Flow pipeline:
  Collector subscribes -> Room executes query -> emit result
       |
  Table changed (INSERT/UPDATE/DELETE)
       |
  InvalidationTracker notifies -> Room re-executes query -> emit new result
```

#### withTransaction для атомарных операций

```kotlin
@Dao
abstract class TransferDao {
    @Insert
    abstract suspend fun insert(transfer: Transfer)

    @Update
    abstract suspend fun updateAccount(account: Account)
}

class TransferRepository(
    private val db: AppDatabase,
    private val transferDao: TransferDao
) {
    suspend fun performTransfer(from: Account, to: Account, amount: Double) {
        // withTransaction -- все операции атомарно
        // Room сам управляет потоком (специальный transaction executor)
        db.withTransaction {
            val updatedFrom = from.copy(balance = from.balance - amount)
            val updatedTo = to.copy(balance = to.balance + amount)
            transferDao.updateAccount(updatedFrom)
            transferDao.updateAccount(updatedTo)
            transferDao.insert(Transfer(from.id, to.id, amount))
        }
    }
}
```

### Retrofit + Coroutines

Начиная с Retrofit 2.6 suspend-функции в API-интерфейсах поддерживаются нативно.

```kotlin
interface UserApi {
    // suspend -- Retrofit автоматически выполняет на IO
    // и возвращает результат на вызывающем Dispatcher
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): List<User>

    @POST("users")
    suspend fun createUser(@Body user: User): User

    // Если нужен доступ к Response (headers, status code)
    @GET("users/{id}")
    suspend fun getUserResponse(@Path("id") userId: String): Response<User>
}
```

**Как Retrofit обрабатывает suspend внутри:**

Когда вы объявляете `suspend fun getUser()`, Retrofit:
1. Обнаруживает `Continuation` как последний параметр (CPS-трансформация)
2. Создаёт `KotlinExtensions.await()` вокруг обычного `Call<T>`
3. Выполняет запрос через `OkHttp` (на IO-потоке OkHttp dispatcher)
4. Возобновляет корутину на вызывающем Dispatcher с результатом или исключением

```
suspend fun getUser(id)
     |
     v
Retrofit: Call<User>.await()
     |
     v
OkHttp: enqueue(callback) на OkHttp thread pool
     |
     v (response ready)
continuation.resume(user) на вызывающем Dispatcher
```

Это означает, что вам НЕ нужен `withContext(Dispatchers.IO)` при вызове Retrofit suspend-функций -- Retrofit сам выполняет запрос в фоне. `withContext(IO)` нужен только если вы делаете дополнительную работу (парсинг, сохранение в БД).

**Обработка ошибок:**

```kotlin
class UserRepository(
    private val api: UserApi,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val user = api.getUser(userId)
            Result.success(user)
        } catch (e: HttpException) {
            // 4xx, 5xx -- сервер вернул ошибку
            val errorBody = e.response()?.errorBody()?.string()
            Result.failure(ApiException(e.code(), errorBody))
        } catch (e: IOException) {
            // Нет сети, timeout, DNS failure
            Result.failure(NetworkException(e))
        }
    }
}

// Sealed class для типизированных ошибок (альтернатива kotlin.Result)
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class HttpError(val code: Int, val body: String?) : ApiResult<Nothing>()
    data class NetworkError(val exception: IOException) : ApiResult<Nothing>()
    data class UnknownError(val exception: Throwable) : ApiResult<Nothing>()
}

suspend fun <T> safeApiCall(block: suspend () -> T): ApiResult<T> {
    return try {
        ApiResult.Success(block())
    } catch (e: HttpException) {
        ApiResult.HttpError(e.code(), e.response()?.errorBody()?.string())
    } catch (e: IOException) {
        ApiResult.NetworkError(e)
    } catch (e: Exception) {
        ApiResult.UnknownError(e)
    }
}
```

### DataStore + Coroutines

DataStore -- замена SharedPreferences с нативной поддержкой корутин. Два типа: Preferences DataStore (key-value) и Proto DataStore (typed schema).

**Ключевые принципы:**
- Чтение всегда через `Flow` -- reactive, lifecycle-aware
- Запись всегда через `suspend` -- безопасна, атомарна
- DataStore гарантирует single writer -- конкурентные записи сериализуются
- При ошибке чтения (corrupted file) -- используйте `.catch {}` для graceful degradation

```kotlin
class SettingsRepository(
    private val dataStore: DataStore<Preferences>
) {
    // Чтение -- Flow (reactive)
    val darkModeEnabled: Flow<Boolean> = dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                // Файл повреждён -- возвращаем defaults
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences ->
            preferences[DARK_MODE_KEY] ?: false
        }

    // Запись -- suspend, атомарная
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[DARK_MODE_KEY] = enabled
        }
    }

    // Чтение одного значения (one-shot)
    suspend fun isDarkModeEnabled(): Boolean {
        return dataStore.data.first()[DARK_MODE_KEY] ?: false
    }

    // Атомарное обновление нескольких значений
    suspend fun updateTheme(isDark: Boolean, fontSize: Int) {
        dataStore.edit { preferences ->
            preferences[DARK_MODE_KEY] = isDark
            preferences[FONT_SIZE_KEY] = fontSize
        }
    }

    companion object {
        private val DARK_MODE_KEY = booleanPreferencesKey("dark_mode")
        private val FONT_SIZE_KEY = intPreferencesKey("font_size")
    }
}

// В ViewModel:
@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    val isDarkMode: StateFlow<Boolean> = settingsRepository.darkModeEnabled
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = false
        )

    fun toggleDarkMode() {
        viewModelScope.launch {
            val current = settingsRepository.isDarkModeEnabled()
            settingsRepository.setDarkMode(!current)
            // UI обновится автоматически через Flow -> StateFlow -> Compose
        }
    }
}
```

**DataStore vs SharedPreferences:**

```
+----------------------------+------------------+------------------+
|                            | SharedPreferences | DataStore        |
+----------------------------+------------------+------------------+
| Thread-safe                | Нет (apply async)| Да (Mutex внутри)|
| Корутины                   | Нет              | Нативно          |
| Reactive (Flow)            | Нет              | Да               |
| Error handling             | Exceptions       | Flow catch        |
| Typed (Proto)              | Нет              | Да               |
| Миграция                   | --               | Встроенная        |
+----------------------------+------------------+------------------+
```
```

### WorkManager + CoroutineWorker

```kotlin
class SyncWorker(
    appContext: Context,
    params: WorkerParameters,
    private val syncRepository: SyncRepository // через HiltWorker
) : CoroutineWorker(appContext, params) {

    // doWork() -- suspend, по умолчанию на Dispatchers.Default
    override suspend fun doWork(): Result {
        return try {
            // Прогресс
            setProgress(workDataOf("progress" to 0))

            val data = syncRepository.fetchRemoteData()
            setProgress(workDataOf("progress" to 50))

            syncRepository.saveToLocal(data)
            setProgress(workDataOf("progress" to 100))

            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry() // WorkManager переставит в очередь
            } else {
                Result.failure(workDataOf("error" to e.message))
            }
        }
    }
}

**Важные особенности CoroutineWorker:**

1. `doWork()` по умолчанию выполняется на `Dispatchers.Default` (не Main, не IO)
2. Если Worker останавливается (отменяется), корутина автоматически отменяется через cooperative cancellation
3. `setProgress()` -- suspend-функция для отправки промежуточного прогресса
4. `setForeground()` -- для перевода Worker в Foreground Service (длительные операции)
5. `runAttemptCount` -- количество попыток, полезно для retry-логики

```kotlin
// Foreground Worker (для операций > 10 минут)
class LongSyncWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        // Переводим в Foreground -- показываем notification
        setForeground(createForegroundInfo())

        return try {
            performLongSync()
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private fun createForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Syncing...")
            .setSmallIcon(R.drawable.ic_sync)
            .setOngoing(true)
            .build()
        return ForegroundInfo(NOTIFICATION_ID, notification)
    }
}
```

// Запуск:
val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

WorkManager.getInstance(context).enqueueUniqueWork(
    "sync",
    ExistingWorkPolicy.KEEP,
    syncRequest
)
```

### Paging 3 + Coroutines

```kotlin
class UserPagingSource(
    private val api: UserApi
) : PagingSource<Int, User>() {

    // load() -- suspend
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        return try {
            val page = params.key ?: 1
            val response = api.getUsers(page = page, size = params.loadSize)

            LoadResult.Page(
                data = response.users,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.users.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, User>): Int? {
        return state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchor)?.nextKey?.minus(1)
        }
    }
}

// В ViewModel:
class UserListViewModel(private val api: UserApi) : ViewModel() {

    val users: Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20, enablePlaceholders = false),
        pagingSourceFactory = { UserPagingSource(api) }
    ).flow.cachedIn(viewModelScope) // cachedIn -- кеширует в viewModelScope
}

// В Compose:
@Composable
fun UserList(viewModel: UserListViewModel) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        items(count = users.itemCount) { index ->
            users[index]?.let { user -> UserItem(user) }
        }

        // Обработка состояния загрузки
        when (users.loadState.refresh) {
            is LoadState.Loading -> item { LoadingIndicator() }
            is LoadState.Error -> item {
                ErrorItem(
                    message = (users.loadState.refresh as LoadState.Error).error.message,
                    onRetry = { users.retry() }
                )
            }
            is LoadState.NotLoading -> {} // данные загружены
        }

        // Индикатор при подгрузке следующей страницы
        if (users.loadState.append is LoadState.Loading) {
            item { LoadingIndicator() }
        }
    }
}
```

**Как Paging 3 использует корутины:**
- `PagingSource.load()` -- suspend-функция, вызывается Paging library на IO dispatcher
- `Flow<PagingData<T>>` -- reactive stream страниц, собирается в UI
- `cachedIn(viewModelScope)` -- кеширует загруженные страницы в scope ViewModel; при rotation данные не перезагружаются
- `RemoteMediator` (для offline-first) -- `load()` тоже suspend, вызывается при необходимости обновления из сети
```

---

## Hilt + Coroutines

### @HiltViewModel и viewModelScope

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // viewModelScope доступен из ViewModel -- не нужно инжектить
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadProfile()
    }

    private fun loadProfile() {
        viewModelScope.launch {
            val userId = savedStateHandle.get<String>("userId") ?: return@launch
            val result = userRepository.getUser(userId)
            _uiState.value = when (result) {
                is ApiResult.Success -> ProfileUiState.Success(result.data)
                is ApiResult.HttpError -> ProfileUiState.Error("Server error: ${result.code}")
                is ApiResult.NetworkError -> ProfileUiState.Error("No connection")
                is ApiResult.UnknownError -> ProfileUiState.Error("Unknown error")
            }
        }
    }
}
```

### Инъекция CoroutineDispatcher

**Проблема:** Если вы хардкодите `Dispatchers.IO` в репозиториях, то в тестах не можете подставить `TestDispatcher`. Решение -- инъекция через квалификаторы.

```kotlin
// Квалификаторы
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainImmediateDispatcher

// Module
@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main

    @Provides
    @MainImmediateDispatcher
    fun provideMainImmediateDispatcher(): CoroutineDispatcher = Dispatchers.Main.immediate
}

// Использование в Repository
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getUser(userId: String): User = withContext(ioDispatcher) {
        val cached = dao.getUserById(userId)
        if (cached != null) return@withContext cached

        val remote = api.getUser(userId)
        dao.insert(remote)
        remote
    }
}
```

### Инъекция CoroutineScope (@ApplicationScope)

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class ApplicationScope

@Module
@InstallIn(SingletonComponent::class)
object CoroutineScopeModule {

    @Provides
    @Singleton
    @ApplicationScope
    fun provideApplicationScope(
        @DefaultDispatcher defaultDispatcher: CoroutineDispatcher
    ): CoroutineScope = CoroutineScope(
        SupervisorJob() + defaultDispatcher + CoroutineExceptionHandler { _, throwable ->
            // Логирование необработанных ошибок
            Log.e("ApplicationScope", "Unhandled coroutine exception", throwable)
        }
    )
}

// Использование -- операции, которые должны пережить ViewModel
class AnalyticsRepository @Inject constructor(
    @ApplicationScope private val appScope: CoroutineScope,
    private val analyticsApi: AnalyticsApi
) {
    // fire-and-forget: должно завершиться даже если пользователь ушёл с экрана
    fun trackEvent(event: AnalyticsEvent) {
        appScope.launch {
            try {
                analyticsApi.send(event)
            } catch (e: Exception) {
                // логируем, но не крэшим
                Log.w("Analytics", "Failed to send event", e)
            }
        }
    }
}
```

### @HiltWorker -- инъекция зависимостей в CoroutineWorker

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val syncRepository: SyncRepository,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        return withContext(ioDispatcher) {
            try {
                syncRepository.performFullSync()
                Result.success()
            } catch (e: Exception) {
                if (runAttemptCount < 3) Result.retry()
                else Result.failure()
            }
        }
    }
}
```

`@AssistedInject` нужен потому, что `Context` и `WorkerParameters` предоставляются WorkManager в runtime, а не Hilt. Все остальные зависимости инжектируются через Hilt как обычно.

### Иерархия скоупов в Hilt-приложении

```
SingletonComponent (Application)
|
+-- @ApplicationScope CoroutineScope (SupervisorJob + Default)
|   |   Предоставлен через Hilt Module
|   |   Живёт весь процесс
|   |
|   +-- AnalyticsRepository (fire-and-forget)
|   +-- SyncManager (background sync)
|   +-- CacheWarmupService
|
+-- @ViewModelScoped (per ViewModel)
|   |
|   +-- viewModelScope (встроен в ViewModel)
|       |   Живёт пока ViewModel жив
|       |
|       +-- LoadUserUseCase
|       +-- SearchUseCase
|
+-- @ActivityRetainedScoped (переживает rotation)
|
+-- @ActivityScoped
    |
    +-- lifecycleScope (встроен в Activity)
```

### Полный пример: ViewModel + Repository + Hilt

```kotlin
// --- DI Module ---
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideUserRepository(
        api: UserApi,
        dao: UserDao,
        @IoDispatcher ioDispatcher: CoroutineDispatcher,
        @ApplicationScope appScope: CoroutineScope
    ): UserRepository = UserRepository(api, dao, ioDispatcher, appScope)
}

// --- Repository ---
class UserRepository(
    private val api: UserApi,
    private val dao: UserDao,
    private val ioDispatcher: CoroutineDispatcher,
    private val appScope: CoroutineScope
) {
    fun observeUser(userId: String): Flow<User?> = dao.observeUser(userId)

    suspend fun refreshUser(userId: String) = withContext(ioDispatcher) {
        val user = api.getUser(userId)
        dao.insert(user)
    }

    // Work that must complete: uses appScope
    fun scheduleSync(userId: String) {
        appScope.launch {
            val user = api.getUser(userId)
            dao.insert(user)
        }
    }
}

// --- ViewModel ---
@HiltViewModel
class UserDetailViewModel @Inject constructor(
    private val repository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = checkNotNull(savedStateHandle["userId"])

    private val _uiState = MutableStateFlow<UserDetailState>(UserDetailState.Loading)
    val uiState: StateFlow<UserDetailState> = _uiState.asStateFlow()

    init {
        // Observe из Room (reactive)
        viewModelScope.launch {
            repository.observeUser(userId).collect { user ->
                if (user != null) {
                    _uiState.value = UserDetailState.Success(user)
                }
            }
        }

        // Одноразовый refresh с сервера
        viewModelScope.launch {
            try {
                repository.refreshUser(userId)
            } catch (e: Exception) {
                if (_uiState.value is UserDetailState.Loading) {
                    _uiState.value = UserDetailState.Error(e.message)
                }
                // Если данные уже в кеше, ошибка refresh не критична
            }
        }
    }
}

sealed interface UserDetailState {
    data object Loading : UserDetailState
    data class Success(val user: User) : UserDetailState
    data class Error(val message: String?) : UserDetailState
}
```

---

## Exception handling в Android корутинах

### Стратегия обработки исключений

Исключения в корутинах ведут себя по-разному в зависимости от builder:

```
launch { throw Exception() }
  -> исключение propagates к parent Job
  -> если нет handler, приложение падает

async { throw Exception() }
  -> исключение "хранится" в Deferred
  -> пробрасывается при вызове .await()
  -> НО если parent -- coroutineScope, propagates сразу

supervisorScope { launch { throw Exception() } }
  -> исключение НЕ propagates к parent
  -> но если нет try/catch или CoroutineExceptionHandler, app crashes
```

### CoroutineExceptionHandler

```kotlin
// Для viewModelScope -- установка глобального handler
class SafeViewModel : ViewModel() {

    private val exceptionHandler = CoroutineExceptionHandler { _, throwable ->
        // Логируем, но не крэшим
        Log.e("ViewModel", "Coroutine failed", throwable)
        _uiState.value = UiState.Error(throwable.message)
    }

    fun loadData() {
        // Handler ловит необработанные исключения из launch
        viewModelScope.launch(exceptionHandler) {
            val data = repository.getData() // может бросить
            _uiState.value = UiState.Success(data)
        }
    }
}
```

**Когда что использовать:**

```
+----------------------------+----------------------------------+
| Механизм                   | Когда использовать               |
+----------------------------+----------------------------------+
| try/catch в корутине       | Конкретная операция, нужен       |
|                            | recovery или fallback            |
+----------------------------+----------------------------------+
| CoroutineExceptionHandler  | Глобальный catch-all для launch, |
|                            | логирование, обновление UI state |
+----------------------------+----------------------------------+
| supervisorScope            | Параллельные операции, failure   |
|                            | одной не должен отменять другие  |
+----------------------------+----------------------------------+
| Result / sealed class      | Чистый API без исключений,       |
|                            | caller решает что делать         |
+----------------------------+----------------------------------+
```

### Паттерн: Result wrapper для Repository

```kotlin
// Единый Result тип для всего приложения
sealed interface AppResult<out T> {
    data class Success<T>(val data: T) : AppResult<T>
    data class Error(val exception: Throwable) : AppResult<Nothing>
}

// Extension для удобства
fun <T> AppResult<T>.getOrNull(): T? = when (this) {
    is AppResult.Success -> data
    is AppResult.Error -> null
}

fun <T> AppResult<T>.getOrThrow(): T = when (this) {
    is AppResult.Success -> data
    is AppResult.Error -> throw exception
}

// Repository всегда возвращает AppResult, никогда не бросает
class UserRepository @Inject constructor(
    private val api: UserApi,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getUser(userId: String): AppResult<User> = withContext(ioDispatcher) {
        try {
            AppResult.Success(api.getUser(userId))
        } catch (e: CancellationException) {
            throw e // ОБЯЗАТЕЛЬНО пробрасываем
        } catch (e: Exception) {
            AppResult.Error(e)
        }
    }
}

// ViewModel -- чистая обработка без try/catch
viewModelScope.launch {
    _uiState.value = UiState.Loading
    val result = repository.getUser(userId)
    _uiState.value = when (result) {
        is AppResult.Success -> UiState.Success(result.data)
        is AppResult.Error -> UiState.Error(result.exception.message)
    }
}
```

---

## Compose-специфичные скоупы

### rememberCoroutineScope

В Compose для запуска корутин из event handlers (onClick, onDrag, etc.) используется `rememberCoroutineScope()`:

```kotlin
@Composable
fun AnimatedButton(onClick: suspend () -> Unit) {
    // Скоуп привязан к Composition -- отменяется при выходе из composition
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            onClick()
        }
    }) {
        Text("Click me")
    }
}
```

**Когда использовать:**
- Анимации, инициированные пользователем
- Scroll-to-position по клику
- Snackbar `showSnackbar()` (suspend-функция)

**Когда НЕ использовать:**
- Загрузка данных (используйте ViewModel)
- Сбор Flow (используйте `collectAsStateWithLifecycle`)

### LaunchedEffect -- корутина привязанная к Composition

```kotlin
@Composable
fun UserScreen(userId: String, viewModel: UserViewModel = hiltViewModel()) {
    // LaunchedEffect запускает корутину при входе в composition
    // и отменяет при выходе. При изменении key -- перезапускает.
    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    // Для side-effects, зависящих от state
    val snackbarHostState = remember { SnackbarHostState() }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(uiState) {
        if (uiState is UserUiState.Error) {
            snackbarHostState.showSnackbar(
                message = (uiState as UserUiState.Error).message
            )
        }
    }
}
```

```
+-----------------------------+---------------------------+----------------------------+
| rememberCoroutineScope      | LaunchedEffect            | collectAsStateWithLifecycle|
+-----------------------------+---------------------------+----------------------------+
| Для event handlers          | Для side-effects при      | Для сбора Flow в State     |
| (onClick, onDrag)           | входе в composition       |                            |
| Ручной launch               | Автоматический launch     | Автоматический collect     |
| Отменяется при выходе       | Перезапускается при       | Lifecycle-aware            |
| из composition              | изменении key             | (STARTED/STOPPED)          |
+-----------------------------+---------------------------+----------------------------+
```

---

## Паттерны

### UDF с StateFlow (полный пример)

Unidirectional Data Flow -- основной архитектурный паттерн для Android UI:

```
User Action (UiEvent)
     |
     v
ViewModel (обрабатывает event, обновляет state)
     |
     v
UiState (sealed interface, единственный источник правды)
     |
     v
UI (Compose / View наблюдает и рендерит)
```

```kotlin
// --- State ---
sealed interface ArticleListState {
    data object Loading : ArticleListState
    data class Success(
        val articles: List<Article>,
        val isRefreshing: Boolean = false
    ) : ArticleListState
    data class Error(val message: String) : ArticleListState
}

// --- Events ---
sealed interface ArticleListEvent {
    data class Search(val query: String) : ArticleListEvent
    data object Refresh : ArticleListEvent
    data class ToggleBookmark(val articleId: String) : ArticleListEvent
    data object RetryLoad : ArticleListEvent
}

// --- ViewModel ---
@HiltViewModel
class ArticleListViewModel @Inject constructor(
    private val articleRepository: ArticleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ArticleListState>(ArticleListState.Loading)
    val uiState: StateFlow<ArticleListState> = _uiState.asStateFlow()

    private var searchJob: Job? = null

    init {
        loadArticles()
    }

    fun onEvent(event: ArticleListEvent) {
        when (event) {
            is ArticleListEvent.Search -> search(event.query)
            is ArticleListEvent.Refresh -> refresh()
            is ArticleListEvent.ToggleBookmark -> toggleBookmark(event.articleId)
            is ArticleListEvent.RetryLoad -> loadArticles()
        }
    }

    private fun loadArticles() {
        viewModelScope.launch {
            _uiState.value = ArticleListState.Loading
            try {
                val articles = articleRepository.getArticles()
                _uiState.value = ArticleListState.Success(articles)
            } catch (e: Exception) {
                _uiState.value = ArticleListState.Error(
                    e.message ?: "Unknown error"
                )
            }
        }
    }

    private fun search(query: String) {
        searchJob?.cancel() // отменяем предыдущий поиск
        searchJob = viewModelScope.launch {
            delay(300) // debounce
            _uiState.value = ArticleListState.Loading
            try {
                val articles = articleRepository.searchArticles(query)
                _uiState.value = ArticleListState.Success(articles)
            } catch (e: Exception) {
                _uiState.value = ArticleListState.Error(e.message ?: "Search failed")
            }
        }
    }

    private fun refresh() {
        val currentState = _uiState.value
        if (currentState is ArticleListState.Success) {
            _uiState.value = currentState.copy(isRefreshing = true)
        }
        viewModelScope.launch {
            try {
                val articles = articleRepository.getArticles(forceRefresh = true)
                _uiState.value = ArticleListState.Success(articles, isRefreshing = false)
            } catch (e: Exception) {
                if (currentState is ArticleListState.Success) {
                    // Данные есть, но refresh провалился -- показываем ошибку как snackbar
                    _uiState.value = currentState.copy(isRefreshing = false)
                    // Отправить one-time event через Channel
                }
            }
        }
    }

    private fun toggleBookmark(articleId: String) {
        viewModelScope.launch {
            articleRepository.toggleBookmark(articleId)
            // Room Flow автоматически обновит UI
        }
    }
}
```

**Альтернатива: MVI-подход с reduce:**

Для сложных экранов с множеством событий можно использовать `reduce`-подход, где каждый event явно трансформирует state:

```kotlin
@HiltViewModel
class CounterViewModel @Inject constructor() : ViewModel() {

    private val _state = MutableStateFlow(CounterState())
    val state: StateFlow<CounterState> = _state.asStateFlow()

    fun onEvent(event: CounterEvent) {
        _state.update { currentState ->
            when (event) {
                CounterEvent.Increment -> currentState.copy(count = currentState.count + 1)
                CounterEvent.Decrement -> currentState.copy(count = currentState.count - 1)
                CounterEvent.Reset -> CounterState()
            }
        }
    }
}

data class CounterState(val count: Int = 0)

sealed interface CounterEvent {
    data object Increment : CounterEvent
    data object Decrement : CounterEvent
    data object Reset : CounterEvent
}
```

`MutableStateFlow.update {}` -- атомарная операция (CAS -- compare-and-swap). Безопасна для вызова из нескольких корутин одновременно. Подробнее о State vs Events -- в [[android-state-management]].

### Параллельные запросы

```kotlin
// coroutineScope -- все должны завершиться успешно
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val userDeferred = async { userRepository.getUser() }
    val statsDeferred = async { statsRepository.getStats() }
    val notificationsDeferred = async { notificationRepository.getRecent() }

    // Если любой упадёт -- все отменяются (structured concurrency)
    Dashboard(
        user = userDeferred.await(),
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}

// supervisorScope -- независимые операции, failure одного не отменяет другие
suspend fun loadDashboardResilient(): Dashboard = supervisorScope {
    val userDeferred = async { userRepository.getUser() }
    val statsDeferred = async {
        try {
            statsRepository.getStats()
        } catch (e: Exception) {
            Stats.empty() // fallback
        }
    }
    val notificationsDeferred = async {
        try {
            notificationRepository.getRecent()
        } catch (e: Exception) {
            emptyList() // fallback
        }
    }

    Dashboard(
        user = userDeferred.await(), // этот обязателен
        stats = statsDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

### Retry с exponential backoff

```kotlin
suspend fun <T> retryWithBackoff(
    times: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 16000,
    factor: Double = 2.0,
    shouldRetry: (Throwable) -> Boolean = { it is IOException },
    block: suspend () -> T
): T {
    var currentDelay = initialDelayMs
    repeat(times - 1) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            if (!shouldRetry(e)) throw e
            Log.w("Retry", "Attempt ${attempt + 1} failed, retrying in ${currentDelay}ms", e)
        }
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
    }
    return block() // последняя попытка -- исключение пробрасывается наверх
}

// Использование
viewModelScope.launch {
    val user = retryWithBackoff(times = 3) {
        api.getUser(userId)
    }
    _uiState.value = UserUiState.Success(user)
}
```

### Debounce-поиск на Flow

Поиск с debounce -- один из самых частых паттернов в мобильных приложениях. Пользователь печатает текст, и мы не хотим отправлять запрос на каждый символ -- ждём, пока он остановится.

```kotlin
class SearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val queryFlow = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = queryFlow
        .debounce(300) // ждём 300ms после последнего символа
        .distinctUntilChanged() // не повторяем одинаковые запросы
        .flatMapLatest { query ->
            // flatMapLatest: при новом значении отменяет предыдущий Flow
            if (query.length < 2) {
                flowOf(emptyList())
            } else {
                repository.search(query)
                    .catch { emit(emptyList()) } // fallback при ошибке
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onQueryChanged(query: String) {
        queryFlow.value = query
    }
}
```

```
Пользователь печатает: "k" -> "ko" -> "kot" -> "kotl" -> "kotlin"
                        |      |       |        |         |
debounce(300ms):      timer  reset   reset    reset     timer...
                                                           |
                                               300ms без изменений
                                                           |
flatMapLatest:                                    search("kotlin")
                                                           |
                                                     emit results
```

**Почему `flatMapLatest`, а не `flatMapConcat`?**
- `flatMapLatest` отменяет предыдущий Flow при получении нового значения. Если пользователь быстро печатает, старые запросы отменяются -- экономия ресурсов.
- `flatMapConcat` ждёт завершения предыдущего Flow перед запуском нового -- запросы выстраиваются в очередь, UI тормозит.
```

### Timeout для операций

```kotlin
// withTimeout -- бросает TimeoutCancellationException
suspend fun loadWithTimeout(): User {
    return withTimeout(5000) { // 5 секунд
        api.getUser(userId)
    }
}

// withTimeoutOrNull -- возвращает null при timeout
suspend fun loadWithTimeoutOrNull(): User? {
    return withTimeoutOrNull(5000) {
        api.getUser(userId)
    }
}

// В ViewModel:
viewModelScope.launch {
    val user = withTimeoutOrNull(10_000) {
        repository.getUser(userId)
    }
    _uiState.value = if (user != null) {
        UserUiState.Success(user)
    } else {
        UserUiState.Error("Request timed out")
    }
}
```

**Важно:** `TimeoutCancellationException` -- подкласс `CancellationException`. Если вы ловите `CancellationException` и пробрасываете его (как и должны), timeout будет обработан корректно. Но если вы используете `catch (e: Exception)` без пробрасывания `CancellationException`, timeout тоже будет "проглочен".

### One-shot vs Observer

```
+-------------------+--------------------+---------------------+
|                   | One-shot           | Observer             |
+-------------------+--------------------+---------------------+
| Тип               | suspend fun        | Flow<T>             |
| Use case          | Загрузить один раз | Наблюдать изменения |
| Room              | suspend @Query     | @Query: Flow<T>     |
| Retrofit          | suspend fun        | --                  |
| DataStore         | .first()           | .data (Flow)        |
| ViewModel scope   | launch { ... }     | stateIn / shareIn   |
+-------------------+--------------------+---------------------+
```

```kotlin
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    // One-shot: вызвал -- получил результат
    suspend fun getProductById(id: String): Product = withContext(ioDispatcher) {
        dao.getProduct(id) ?: api.getProduct(id).also { dao.insert(it) }
    }

    // Observer: Flow с автоматическим обновлением
    fun observeProducts(): Flow<List<Product>> = dao.observeAll()

    // Observer + periodic refresh
    fun observeProductsWithRefresh(): Flow<List<Product>> = dao.observeAll()
        .onStart {
            // При первой подписке -- обновляем из сети
            try {
                val remote = api.getProducts()
                dao.insertAll(remote)
            } catch (e: Exception) {
                // Если нет сети -- данные из кеша всё равно придут через Flow
            }
        }
}
```

### Offline-first

Offline-first -- паттерн, при котором UI всегда получает данные из локального хранилища (Room), а сеть используется только для обновления этого хранилища. Преимущества:

- **Мгновенный отклик:** данные из Room отображаются сразу, без ожидания сети
- **Работа без интернета:** приложение функционирует с последними кешированными данными
- **Единый источник правды:** Room -- single source of truth, нет рассинхронизации между UI и данными
- **Автоматическое обновление:** Room Flow автоматически уведомляет UI об изменениях

```
+--------+        +------------+         +--------+
|   UI   | -----> | Repository | ------> | Remote |
|        | <----- |            | <------ |  API   |
+--------+  Flow  |  (Room +   |  suspend+--------+
    ^              |   Network) |
    |              +-----+------+
    |                    |
    |              +-----v------+
    +------------- |   Room DB  |
         Flow      +------------+
         (observe)

Порядок:
1. UI подписывается на Room Flow (через ViewModel)
2. Room отдаёт кешированные данные (мгновенно)
3. Repository запускает network refresh в фоне
4. Данные из сети сохраняются в Room
5. Room Flow автоматически emit'ит обновлённые данные
6. UI обновляется без явного вызова
```

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val dao: ArticleDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
    @ApplicationScope private val appScope: CoroutineScope
) {
    // UI подписывается на этот Flow -- всегда получает данные из Room
    fun observeArticles(): Flow<List<Article>> = dao.observeAll()

    // Trigger refresh: загружаем из сети, сохраняем в Room
    // Room Flow автоматически отправит обновление в UI
    suspend fun refreshArticles() = withContext(ioDispatcher) {
        val remote = api.getArticles()
        dao.upsertAll(remote) // Room -> Flow emit -> UI update
    }

    // Начальная загрузка: Room + trigger network refresh
    fun observeArticlesWithAutoRefresh(): Flow<List<Article>> = dao.observeAll()
        .onStart {
            // В фоне запускаем refresh (не блокируем emit из кеша)
            appScope.launch(ioDispatcher) {
                try {
                    refreshArticles()
                } catch (_: Exception) {
                    // Offline -- ничего страшного, покажем кеш
                }
            }
        }
}

// ViewModel
@HiltViewModel
class ArticleListViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    val articles: StateFlow<ArticlesUiState> = repository
        .observeArticlesWithAutoRefresh()
        .map<List<Article>, ArticlesUiState> { ArticlesUiState.Success(it) }
        .catch { emit(ArticlesUiState.Error(it.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = ArticlesUiState.Loading
        )

    fun refresh() {
        viewModelScope.launch {
            try {
                repository.refreshArticles()
                // UI обновится автоматически через Room -> Flow
            } catch (e: Exception) {
                // Показать ошибку через Channel/SharedFlow
            }
        }
    }
}
```

---

## Dispatcher best practices

### Когда какой Dispatcher

```
+------------------------+--------------------------------------------------+
| Dispatcher             | Когда использовать                               |
+------------------------+--------------------------------------------------+
| Main                   | Обновление UI, если нужен async boundary         |
|                        | (редко нужен напрямую)                           |
+------------------------+--------------------------------------------------+
| Main.immediate         | Обновление UI без redispatch (дефолт в           |
|                        | viewModelScope и lifecycleScope)                 |
+------------------------+--------------------------------------------------+
| IO                     | Сеть, файлы, БД, SharedPreferences               |
|                        | Пул: 64 потока (или core count, если больше)     |
+------------------------+--------------------------------------------------+
| Default                | CPU-intensive: JSON parsing, sorting, encryption  |
|                        | Пул: кол-во CPU cores                            |
+------------------------+--------------------------------------------------+
| IO.limitedParallelism  | Ограничить параллелизм для конкретного ресурса    |
| (n)                    | Пример: max 4 одновременных записи в файл        |
+------------------------+--------------------------------------------------+
| Unconfined             | Тесты, очень специфичные случаи                  |
|                        | НЕ использовать в production-коде                |
+------------------------+--------------------------------------------------+
```

### IO vs Default: общий пул потоков

Dispatchers.IO и Dispatchers.Default разделяют один и тот же пул потоков. Разница -- в лимитах:

```
Thread Pool (общий):
+----------------------------------------------------------+
|  Thread-1  Thread-2  Thread-3  Thread-4  ... Thread-N    |
|                                                          |
|  Default: ограничен CPU cores (например, 8)              |
|  IO:      ограничен max(64, CPU cores)                   |
|                                                          |
|  withContext(IO) из Default-корутины НЕ создаёт          |
|  новый поток -- переиспользует существующий              |
+----------------------------------------------------------+
```

Это важно для понимания:
- `withContext(Dispatchers.IO)` из корутины на `Dispatchers.Default` -- почти бесплатная операция (нет thread switch, если есть свободный слот)
- Но `limitedParallelism(n)` создаёт "виртуальный" dispatcher поверх пула -- ограничивает сколько корутин одновременно выполняются, не создавая новые потоки
- Перегрузка IO dispatcher (>64 блокирующих операций) может повлиять на Default dispatcher, т.к. пул общий

### Main vs Main.immediate

```kotlin
// Dispatchers.Main -- всегда post через Handler
// Даже если уже на Main Thread, код выполнится на следующем цикле Looper
viewModelScope.launch(Dispatchers.Main) {
    // Handler.post(...) -> выполнится позже
    updateUI()
}

// Dispatchers.Main.immediate -- если уже на Main, выполняется сразу
// Если не на Main -- ведёт себя как Main (post через Handler)
viewModelScope.launch(Dispatchers.Main.immediate) {
    // Уже на Main? Выполняется сразу, без post
    updateUI()
}
```

**Когда Main (не immediate):**
- Нужна гарантия, что текущий callback завершится до выполнения нового кода
- Предотвращение reentrancy

**Когда Main.immediate:**
- Стандартный случай (viewModelScope уже использует его)
- Минимальная задержка, снижение jank

### withContext vs launch(Dispatcher)

```kotlin
// withContext -- переключает контекст ТЕКУЩЕЙ корутины, ждёт результата
viewModelScope.launch {
    val user = withContext(Dispatchers.IO) {
        // Выполняется на IO, результат возвращается на Main
        repository.loadUser()
    }
    // Снова на Main
    _uiState.value = UserUiState.Success(user)
}

// launch(Dispatcher) -- создаёт НОВУЮ корутину на другом Dispatcher
viewModelScope.launch {
    // Новая корутина на IO -- fire-and-forget внутри scope
    launch(Dispatchers.IO) {
        analyticsTracker.logEvent("screen_viewed")
    }
    // Продолжаем на Main, не ждём analytics
    _uiState.value = UserUiState.Ready
}
```

**Правило:** Используйте `withContext` когда нужен результат. Используйте `launch(Dispatcher)` для fire-and-forget операций.

### limitedParallelism

```kotlin
// Проблема: 100 параллельных запросов к БД перегружают connection pool
// Решение: ограничить параллелизм
val dbDispatcher = Dispatchers.IO.limitedParallelism(4)

class ImageRepository(
    private val dao: ImageDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    // Ограниченный dispatcher для файловых операций
    private val fileDispatcher = ioDispatcher.limitedParallelism(2)

    suspend fun saveImage(bitmap: Bitmap, path: String) = withContext(fileDispatcher) {
        // Максимум 2 параллельных записи в файловую систему
        val file = File(path)
        file.outputStream().use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
    }
}
```

### Никогда не хардкодить Dispatchers

```kotlin
// ПЛОХО: невозможно тестировать
class BadRepository {
    suspend fun loadData(): Data = withContext(Dispatchers.IO) { // хардкод!
        api.getData()
    }
}

// ХОРОШО: Dispatcher инжектируется
class GoodRepository @Inject constructor(
    private val api: Api,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun loadData(): Data = withContext(ioDispatcher) {
        api.getData()
    }
}

// В тесте:
@Test
fun `loadData returns data from api`() = runTest {
    val repository = GoodRepository(
        api = fakeApi,
        ioDispatcher = StandardTestDispatcher(testScheduler)
        // или UnconfinedTestDispatcher для простых случаев
    )
    val data = repository.loadData()
    assertEquals(expectedData, data)
}

// StandardTestDispatcher vs UnconfinedTestDispatcher:
// StandardTestDispatcher -- корутины не выполняются автоматически,
//   нужен явный advanceUntilIdle() / runCurrent(). Даёт полный контроль.
// UnconfinedTestDispatcher -- корутины выполняются eagerly.
//   Проще для тестов, но меньше контроля над порядком.
```

### SharingStarted.WhileSubscribed(5000) -- объяснение

При использовании `stateIn` и `shareIn` в ViewModel, параметр `started` определяет, когда upstream Flow активен:

```kotlin
val uiState: StateFlow<UiState> = repository.observeData()
    .map { UiState.Success(it) }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(
            stopTimeoutMillis = 5000,  // ждём 5 секунд после последнего subscriber
            replayExpirationMillis = Long.MAX_VALUE // кеш не истекает
        ),
        initialValue = UiState.Loading
    )
```

```
Timeline:
  Collector 1 subscribes -----> upstream STARTS
  Collector 1 unsubscribes ---> timer starts (5000ms)
  ... 3 секунды ...
  Collector 2 subscribes -----> timer cancelled, upstream still active
  Collector 2 unsubscribes ---> timer starts (5000ms)
  ... 5 секунд прошло ...
  Timer fires -----------------> upstream STOPS

Зачем 5000ms?
- Configuration change (rotation) занимает ~1-3 секунды
- WhileSubscribed(5000) позволяет upstream пережить rotation
  без перезапуска (новый collector подключится до истечения таймера)
- Экономит ресурсы: если пользователь ушёл навсегда, upstream остановится
```
```

---

## Тестирование корутин (краткий обзор)

Тестирование корутин в Android опирается на `kotlinx-coroutines-test`:

```kotlin
// build.gradle.kts
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.1")
```

### runTest -- основной builder

```kotlin
@Test
fun `loadUser returns cached user when available`() = runTest {
    // runTest создаёт TestScope с TestDispatcher
    // Виртуальное время: delay(1000) выполняется мгновенно
    val dao = FakeUserDao(cachedUser = testUser)
    val api = FakeUserApi()
    val repository = UserRepository(
        dao = dao,
        api = api,
        ioDispatcher = StandardTestDispatcher(testScheduler)
    )

    val result = repository.getUser("123")

    assertEquals(testUser, result)
    assertEquals(0, api.callCount) // API не вызывался
}
```

### Тестирование ViewModel с StateFlow

```kotlin
@Test
fun `initial state is Loading, then Success after load`() = runTest {
    val repository = FakeArticleRepository(articles = testArticles)
    val viewModel = ArticleListViewModel(repository)

    // Начальное состояние
    assertEquals(ArticleListState.Loading, viewModel.uiState.value)

    // Продвигаем виртуальное время
    advanceUntilIdle()

    // После загрузки
    val state = viewModel.uiState.value
    assertIs<ArticleListState.Success>(state)
    assertEquals(testArticles, state.articles)
}
```

### Turbine -- библиотека для тестирования Flow

```kotlin
@Test
fun `search emits loading then results`() = runTest {
    val viewModel = SearchViewModel(FakeRepository())

    viewModel.searchResults.test {
        assertEquals(emptyList(), awaitItem()) // initial
        viewModel.onQueryChanged("kotlin")
        advanceTimeBy(400) // debounce 300ms + margin
        val results = awaitItem()
        assertTrue(results.isNotEmpty())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Подробное руководство по тестированию -- в [[android-testing]].

---

## Распространённые ошибки

Здесь -- краткий обзор. Подробный разбор каждой ошибки с примерами проблемного и правильного кода -- в [[android-coroutines-mistakes]].

| # | Ошибка | Суть | Подробности |
|---|--------|------|-------------|
| 1 | GlobalScope | Утечка корутин, нет structured concurrency | [[android-coroutines-mistakes]] |
| 2 | Проглатывание CancellationException | `catch (e: Exception)` ловит и cancellation | [[android-coroutines-mistakes]] |
| 3 | Блокирующие вызовы на Main | `Thread.sleep()`, blocking IO на Dispatchers.Main | [[android-coroutines-mistakes]] |
| 4 | collect без repeatOnLifecycle | Flow продолжает работать в background | [[android-coroutines-mistakes]] |
| 5 | Хардкод Dispatchers | Невозможно тестировать | [[android-coroutines-mistakes]] |
| 6 | launch без обработки ошибок | Необработанные исключения crash app | [[android-coroutines-mistakes]] |
| 7 | async без await | Исключение теряется до вызова await | [[android-coroutines-mistakes]] |
| 8 | Не main-safe suspend | Suspend-функция делает IO без withContext | [[android-coroutines-mistakes]] |
| 9 | SharedFlow для state | SharedFlow(replay=0) теряет state для новых подписчиков | [[android-coroutines-mistakes]] |
| 10 | viewModelScope в конструкторе | init {} запускает корутину до полной инициализации | [[android-coroutines-mistakes]] |

**Cooperative cancellation -- ключевая концепция:**

Корутины не прерываются принудительно (как Thread.interrupt()). Отмена -- cooperative: корутина проверяет isActive в suspension points (delay, withContext, yield, emit). Если ваш код выполняет длительную CPU-операцию без suspension points, он не отменится:

```kotlin
// ПРОБЛЕМА: бесконечный цикл не отменяется
viewModelScope.launch {
    while (true) {
        // Нет suspension point -- корутина не проверяет isActive
        processNextItem()
    }
}

// РЕШЕНИЕ 1: ensureActive()
viewModelScope.launch {
    while (true) {
        ensureActive() // бросает CancellationException если отменена
        processNextItem()
    }
}

// РЕШЕНИЕ 2: yield()
viewModelScope.launch {
    while (true) {
        yield() // проверяет cancellation + даёт другим корутинам шанс выполниться
        processNextItem()
    }
}
```

**Быстрая памятка:**

```kotlin
// CancellationException -- ВСЕГДА пробрасывать
try {
    suspendOperation()
} catch (e: CancellationException) {
    throw e // ОБЯЗАТЕЛЬНО
} catch (e: Exception) {
    handleError(e)
}

// Или используйте runCatching с осторожностью:
// kotlin.runCatching{} ловит CancellationException!
// Альтернатива:
suspend fun <T> safeCatching(block: suspend () -> T): Result<T> {
    return try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

---

## CS-фундамент

Корутины в Android опираются на ряд фундаментальных концепций computer science. Понимание этих концепций объясняет, почему API спроектировано именно так.

| Концепция | Определение | Связь с корутинами в Android |
|-----------|-------------|------------------------------|
| **Continuation Passing Style (CPS)** | Трансформация кода: вместо возврата значения -- передача его в continuation | Компилятор Kotlin превращает suspend-функции в CPS; каждый suspend point -- точка возврата. Подробно: [[kotlin-coroutines]] |
| **Cooperative Scheduling** | Задачи сами уступают управление (yield), а не прерываются принудительно | Корутины кооперативны: cancellation работает только в suspension points. Поэтому `ensureActive()` и `yield()` нужны в CPU-bound циклах |
| **Structured Concurrency** | Иерархия задач: parent ждёт children, отмена propagates вниз | viewModelScope -> launch -> withContext: отмена viewModelScope каскадно отменяет все дочерние корутины |
| **Event Loop** | Цикл, который обрабатывает события по одному из очереди | Android Main Thread = Looper + MessageQueue = event loop. Dispatchers.Main отправляет работу в эту очередь |
| **Observer Pattern** | Подписчик уведомляется об изменениях, не polling | StateFlow, SharedFlow, Room Flow -- все основаны на observer pattern |
| **Finite State Machine** | Система с конечным набором состояний и переходами между ними | sealed interface UiState, repeatOnLifecycle (lifecycle states), CoroutineWorker Result (success/retry/failure) |
| **Thread Pool** | Набор потоков, переиспользуемых для выполнения задач | Dispatchers.IO и Default используют thread pool. limitedParallelism создаёт view над пулом |
| **Backpressure** | Механизм управления скоростью producer/consumer | Flow -- cold с suspension-based backpressure. Buffer, conflate, collectLatest -- стратегии обработки |

**Structured Concurrency в действии:**

```
viewModelScope.launch {              // Job A
    val users = withContext(IO) {    //   Job B (child of A)
        coroutineScope {             //     Job C (child of B)
            val a = async { api1() } //       Job D (child of C)
            val b = async { api2() } //       Job E (child of C)
            a.await() + b.await()
        }
    }
    _state.value = users
}

Отмена viewModelScope:
  cancel A -> cancel B -> cancel C -> cancel D + E
  Вся иерархия отменяется каскадно.

Exception в Job D (coroutineScope):
  D fails -> C fails (coroutineScope propagates) -> B fails -> A fails
  Все sibling и parent корутины отменяются.

Exception в Job D (supervisorScope):
  D fails -> E НЕ отменяется -> supervisorScope НЕ fails
  Только сама failed корутина останавливается.
```

---

## Связь с другими темами

```
                        +-----------------------+
                        | kotlin-coroutines     |
                        | (CPS, suspend,        |
                        |  structured conc.)    |
                        +----------+------------+
                                   |
                                   | языковая основа
                                   v
+-------------------+   +----------------------------+   +---------------------+
| android-threading |-->| android-coroutines-guide   |<--| android-viewmodel-  |
| (Main Thread,     |   | (ЭТА СТАТЬЯ:              |   | internals           |
|  Handler, Looper) |   |  scopes, lifecycle,        |   | (viewModelScope,    |
+-------------------+   |  Jetpack, Hilt, patterns)  |   |  onCleared)         |
                        +----------------------------+   +---------------------+
                           |              |
             +-------------+              +-------------+
             v                                          v
+----------------------------+            +----------------------------+
| android-coroutines-mistakes|            | android-state-management   |
| (10 anti-patterns,         |            | (StateFlow, SharedFlow,    |
|  подробный разбор)         |            |  Channel, Compose State)   |
+----------------------------+            +----------------------------+
```

| Тема | Связь | Файл |
|------|-------|------|
| Kotlin Coroutines (язык) | Языковая основа: suspend, CPS, Dispatchers | [[kotlin-coroutines]] |
| Threading в Android | Main Thread, Handler, Looper, ANR | [[android-threading]] |
| ViewModel internals | viewModelScope, onCleared, ViewModelStore | [[android-viewmodel-internals]] |
| State Management | StateFlow, SharedFlow, Channel для UI | [[android-state-management]] |
| Ошибки с корутинами | 10 типичных anti-patterns | [[android-coroutines-mistakes]] |
| Kotlin Flow | Операторы, cold vs hot, backpressure | [[kotlin-flow]] |
| Activity Lifecycle | Configuration change, process death | [[android-activity-lifecycle]] |
| DI в Android | Hilt, Dagger, инъекция зависимостей | [[android-dependency-injection]] |
| Background Work | WorkManager, Services, scheduling | [[android-background-work]] |
| Android Architecture | MVVM, MVI, Clean Architecture | [[android-architecture-patterns]] |

---

## Источники и дальнейшее чтение

### Книги

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive*. Kt. Academy. -- Наиболее глубокий источник по корутинам: CPS, Job hierarchy, Dispatchers internals, structured concurrency, Flow internals.
- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition*. Manning. -- Главы по корутинам и Flow с акцентом на практическое применение.

### Официальная документация

- [Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines) -- Android Developers. Основная точка входа.
- [Best practices for coroutines in Android](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) -- Android Developers. Inject Dispatchers, main-safe suspend, structured concurrency.
- [Use Kotlin coroutines with lifecycle-aware components](https://developer.android.com/topic/libraries/architecture/coroutines) -- Android Developers. viewModelScope, lifecycleScope, repeatOnLifecycle.
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) -- Android Developers. Сбор Flow для UI.
- [Threading in CoroutineWorker](https://developer.android.com/develop/background-work/background-tasks/persistent/threading/coroutineworker) -- Android Developers. CoroutineWorker API.
- [Coroutines guide](https://kotlinlang.org/docs/coroutines-guide.html) -- Kotlin Documentation. Языковой reference.

### Статьи и блоги

- Vivo M. [A safer way to collect flows from Android UIs](https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda) -- Android Developers Blog. Объясняет, почему `launchWhenX` -- плохо и зачем нужен `repeatOnLifecycle`.
- Vivo M. [repeatOnLifecycle API design story](https://medium.com/androiddevelopers/repeatonlifecycle-api-design-story-8670d1a7d333) -- Android Developers Blog. Дизайн-решения за API.
- Vivo M. [Consuming flows safely in Jetpack Compose](https://medium.com/androiddevelopers/consuming-flows-safely-in-jetpack-compose-cde014d0d5a3) -- collectAsStateWithLifecycle.
- Vivo M. [Create an application CoroutineScope using Hilt](https://medium.com/androiddevelopers/create-an-application-coroutinescope-using-hilt-dd444e721528) -- @ApplicationScope паттерн.
- Patil S. [Understanding Dispatchers: Main and Main.immediate](https://blog.shreyaspatil.dev/understanding-dispatchers-main-and-mainimmediate) -- Детальное сравнение.
- Moskala M. [Best practices](https://kt.academy/article/cc-best-practices) -- Kt. Academy. Практические рекомендации.
- [Exploring the Secrets of Dispatchers Default and IO](https://www.droidcon.com/2024/11/21/exploring-the-secrets-of-dispatchers-default-and-io-in-kotlin-coroutines/) -- droidcon. Thread pool internals.
- Muntenescu F. [Room + Coroutines](https://medium.com/androiddevelopers/room-coroutines-422b786dc4c5) -- Android Developers Blog.
- Muntenescu F. [Room + Flow](https://medium.com/androiddevelopers/room-flow-273acffe5b57) -- Android Developers Blog.
- Santiago D. [Threading models in Coroutines and Android SQLite API](https://medium.com/androiddevelopers/threading-models-in-coroutines-and-android-sqlite-api-6cab11f7eb90) -- Room transaction threading.

### Talks

- Lake I. "Single source of truth" -- Android Dev Summit talks. viewModelScope design, lifecycle integration.
- Bader F., Vivo M. -- KotlinConf / droidcon talks на тему coroutines + lifecycle.

---

## Проверь себя

**Вопрос 1:** Почему `lifecycleScope.launch { flow.collect {} }` считается утечкой ресурсов, а `lifecycleScope.launch { repeatOnLifecycle(STARTED) { flow.collect {} } }` -- нет?

<details>
<summary>Ответ</summary>

`lifecycleScope.launch { flow.collect {} }` отменяется только при DESTROYED. Это значит, что когда Activity/Fragment уходит в STOPPED (например, пользователь сворачивает приложение), корутина продолжает собирать Flow: upstream остаётся активным, тратит ресурсы (сеть, CPU, батарея). `repeatOnLifecycle(STARTED)` отменяет внутреннюю корутину при переходе ниже STARTED и перезапускает при возврате. Таким образом, в background нет активных подписок.
</details>

**Вопрос 2:** У вас есть `AnalyticsRepository`, который должен отправить событие на сервер. Пользователь может уйти с экрана до завершения отправки. В каком скоупе запускать корутину и почему?

<details>
<summary>Ответ</summary>

В `@ApplicationScope` (или аналогичном application-level скоупе). `viewModelScope` отменится при уходе с экрана -- событие может не отправиться. `GlobalScope` нарушает structured concurrency. Application-level scope с SupervisorJob и CoroutineExceptionHandler -- правильный выбор: корутина завершится независимо от lifecycle экрана, и ошибки будут обработаны.
</details>

**Вопрос 3:** В чём разница между `Dispatchers.Main` и `Dispatchers.Main.immediate`? Какой используется по умолчанию в `viewModelScope`?

<details>
<summary>Ответ</summary>

`Dispatchers.Main` всегда отправляет работу через `Handler.post()`, даже если код уже выполняется на Main Thread. Это создаёт async boundary -- код выполнится на следующей итерации Looper. `Dispatchers.Main.immediate` проверяет: если уже на Main Thread -- выполняет код сразу (inline), если не на Main -- ведёт себя как `Main`. `viewModelScope` использует `Main.immediate` для минимальной задержки.
</details>

**Вопрос 4:** В Fragment при navigation + back stack, View уничтожается (onDestroyView), но Fragment продолжает жить. Какой lifecycleScope нужно использовать в `onViewCreated` для сбора Flow и почему?

<details>
<summary>Ответ</summary>

`viewLifecycleOwner.lifecycleScope`. Если использовать `this.lifecycleScope` (lifecycle самого Fragment), корутина переживёт уничтожение View. При попытке обратиться к binding или View -- crash (NullPointerException или IllegalStateException). `viewLifecycleOwner` привязан к lifecycle View: его scope отменяется в `onDestroyView`, что гарантирует безопасность работы с UI.
</details>

---

## Ключевые карточки

**Карточка 1: viewModelScope**
- Front: Какую конфигурацию имеет viewModelScope и когда он отменяется?
- Back: `SupervisorJob() + Dispatchers.Main.immediate`. Отменяется в `ViewModel.onCleared()` -- когда Activity финально уничтожается (не rotation) или Fragment отсоединяется. Переживает configuration change.

**Карточка 2: repeatOnLifecycle**
- Front: Что делает `repeatOnLifecycle(Lifecycle.State.STARTED)`?
- Back: Suspend-функция, которая: (1) ждёт достижения state STARTED, (2) запускает переданный блок в новой корутине, (3) отменяет корутину при уходе ниже STARTED, (4) перезапускает блок при возврате в STARTED. Идеальна для collect Flow в UI.

**Карточка 3: collectAsStateWithLifecycle**
- Front: Зачем нужен `collectAsStateWithLifecycle()` вместо `collectAsState()` в Compose?
- Back: `collectAsState()` не учитывает lifecycle -- продолжает сбор в background (STOPPED). `collectAsStateWithLifecycle()` внутри использует `repeatOnLifecycle(STARTED)` -- отписывается при уходе в background, экономя ресурсы.

**Карточка 4: Main.immediate**
- Front: Чем `Dispatchers.Main.immediate` отличается от `Dispatchers.Main`?
- Back: `Main` всегда делает `Handler.post()` (async boundary). `Main.immediate` -- если уже на Main Thread, выполняет код сразу (inline), без post. Это default в viewModelScope для минимальной задержки.

**Карточка 5: Инъекция Dispatcher**
- Front: Почему нельзя хардкодить `Dispatchers.IO` в репозиториях?
- Back: Невозможно тестировать: в unit-тестах нужен `TestDispatcher` для контроля времени и порядка выполнения. Решение: инжектировать через Hilt с квалификаторами (`@IoDispatcher`, `@DefaultDispatcher`).

**Карточка 6: withContext vs launch**
- Front: Когда использовать `withContext(Dispatchers.IO)` vs `launch(Dispatchers.IO)`?
- Back: `withContext` -- переключает контекст текущей корутины и ждёт результата (sequential). `launch` -- создаёт новую корутину (concurrent, fire-and-forget). Правило: `withContext` когда нужен результат, `launch` для параллельных/независимых операций.

---

## Куда дальше

| Направление | Тема | Файл | Зачем |
|-------------|------|------|-------|
| Углубление | Типичные ошибки с корутинами | [[android-coroutines-mistakes]] | 10 anti-patterns с подробным разбором |
| Углубление | StateFlow, SharedFlow, Channel | [[android-state-management]] | Паттерны управления UI state |
| Углубление | ViewModel internals | [[android-viewmodel-internals]] | Как viewModelScope создаётся и хранится |
| Языковая база | Kotlin Coroutines (язык) | [[kotlin-coroutines]] | CPS, suspend internals, structured concurrency |
| Flow | Kotlin Flow (язык) | [[kotlin-flow]] | Операторы, cold/hot, backpressure, testing |
| Architecture | Architecture Patterns | [[android-architecture-patterns]] | MVVM, MVI, Clean Architecture с корутинами |
| Background | WorkManager + Background Work | [[android-background-work]] | Guaranteed execution, scheduling |
| Testing | Testing в Android | [[android-testing]] | Тестирование корутин: runTest, TestDispatcher |
| DI | Dependency Injection | [[android-dependency-injection]] | Hilt/Dagger для Android |
