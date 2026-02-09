---
title: "Жизненный цикл Activity: состояния и переходы"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
tags:
  - android
  - activity
  - lifecycle
  - savedinstancestate
  - viewmodel
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-process-memory]]"
  - "[[android-architecture-patterns]]"
  - "[[android-context-internals]]"
cs-foundations: [process-lifecycle, state-machine, resource-management, callback-pattern]
---

# Жизненный цикл Activity: состояния и переходы

Жизненный цикл Activity — это последовательность состояний, через которые проходит экран приложения. Система вызывает callback-методы при каждом переходе. Понимание этого цикла критически важно: неправильная работа с lifecycle — причина большинства багов в Android-приложениях (утечки памяти, потеря данных, crashes).

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Android Overview | Базовое понимание Android | [[android-overview]] |
| OOP | Классы, наследование, callbacks | Kotlin/Java basics |
| Kotlin/Java | Синтаксис языка | Kotlin docs |
| **CS: Process Lifecycle** | Почему система убивает процессы | [[cs-process-lifecycle]] |

---

## Зачем вообще нужен жизненный цикл?

### Проблема: почему нельзя просто сделать обычный класс?

На сервере или десктопе вы создаёте объект, он живёт пока нужен, потом уничтожается. В Android это не работает:

```kotlin
// Так работает на сервере:
class UserController {
    fun handleRequest(): Response {
        val data = loadData()
        return Response(data)
    }
}
// Объект создан → работает → уничтожен. Просто.

// Почему это НЕ работает в Android:
class MainActivity {
    private val data = loadData()  // Когда загружать?

    fun showUI() {
        display(data)  // Что если экран уже не виден?
    }
}
```

**Проблемы без lifecycle:**

1. **Ресурсы устройства ограничены.** Телефон имеет 4-8GB RAM на всё: систему, все приложения, фоновые процессы. Если каждое приложение будет держать все свои данные в памяти — память закончится за минуту.

2. **Пользователь постоянно переключается.** Открыл приложение → позвонили → перешёл в браузер → вернулся. Ваше приложение должно корректно приостанавливаться и возобновляться.

3. **Система может убить ваш процесс.** Если память заканчивается, Android убьёт фоновые приложения. Ваш код должен быть готов к внезапной смерти.

4. **Конфигурация меняется.** Поворот экрана, смена языка, подключение клавиатуры — всё это требует пересоздания UI.

### Что даёт lifecycle

Lifecycle — это **контракт между вашим кодом и системой**:

```
Система говорит:                         Вы отвечаете:
─────────────────                        ───────────────
"onCreate: я создала Activity"           → Инициализирую UI
"onStart: сейчас покажу пользователю"   → Запускаю анимации
"onResume: пользователь может тапать"   → Включаю камеру
"onPause: пользователь отвлёкся"        → Приостанавливаю видео
"onStop: экран больше не виден"         → Сохраняю черновик
"onDestroy: я уничтожаю Activity"       → Освобождаю ресурсы
```

Без этого контракта ваш код не знает, когда безопасно использовать UI, когда сохранять данные, когда освобождать ресурсы.

### Альтернативы и почему они хуже

**Альтернатива 1: Polling (проверять состояние вручную)**
```kotlin
// Плохо: тратит CPU, ненадёжно
while (true) {
    if (isScreenVisible()) {
        updateUI()
    }
    Thread.sleep(100)
}
```
Проблемы: тратит батарею, не точно, не знаете точный момент.

**Альтернатива 2: Event Bus (глобальные события)**
```kotlin
// Плохо: сложно отследить, легко пропустить событие
EventBus.subscribe("screen_visible") { updateUI() }
```
Проблемы: нет гарантии порядка, легко забыть отписаться, неявные зависимости.

**Альтернатива 3: Ручное управление (как в играх)**
```kotlin
// Сложно: нужно самому всё контролировать
class GameLoop {
    fun update() {
        if (isPaused) return
        // ...
    }
}
```
Проблемы: изобретаете велосипед, не интегрируется с системой Android.

**Lifecycle callbacks — это стандартное решение**, потому что:
- Система гарантирует порядок вызова
- Интеграция с остальным Android (permissions, navigation, system UI)
- Проверено миллионами приложений
- Инструменты (LifecycleObserver, ViewModel) упрощают работу

### Недостатки lifecycle подхода

Lifecycle не идеален:

1. **Сложность изучения.** 6 методов, много правил, легко ошибиться.
2. **Configuration change пересоздаёт Activity.** Нужен ViewModel для сохранения данных.
3. **Process death теряет ViewModel.** Нужен SavedStateHandle.
4. **Boilerplate код.** Много повторяющихся паттернов (решается Compose).

Но альтернативы ещё хуже. Lifecycle — меньшее зло для мобильной среды с ограниченными ресурсами.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Lifecycle callback** | Метод, вызываемый системой при изменении состояния |
| **Configuration change** | Изменение конфигурации (поворот, язык, размер окна) |
| **SavedInstanceState** | Bundle для сохранения состояния при пересоздании |
| **ViewModel** | Компонент для хранения данных, переживающих config change |
| **Foreground** | Activity видна и имеет фокус |
| **Visible** | Activity видна, но не имеет фокуса |
| **Background** | Activity не видна |

---

## Диаграмма жизненного цикла

```
┌─────────────────────────────────────────────────────────────────┐
│                    ЖИЗНЕННЫЙ ЦИКЛ ACTIVITY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Запуск Activity                                                │
│        │                                                        │
│        ▼                                                        │
│  ┌──────────┐                                                   │
│  │ onCreate │ ← Создание Activity, setContentView               │
│  └────┬─────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────┐                                                   │
│  │ onStart  │ ← Activity становится видимой                     │
│  └────┬─────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────┐                                                   │
│  │ onResume │ ← Activity в foreground, пользователь может       │
│  └────┬─────┘   взаимодействовать                               │
│       │                                                         │
│       │ ◀═══════════════════════════════════════════════════╗  │
│       │         ACTIVITY RUNNING                             ║  │
│       │ ════════════════════════════════════════════════════▶║  │
│       │                                                      ║  │
│       ▼                                                      ║  │
│  ┌──────────┐   Другая Activity                              ║  │
│  │ onPause  │ ← частично закрывает                           ║  │
│  └────┬─────┘   (диалог, новая прозрачная Activity)          ║  │
│       │         ─────────────────────────────────────────────╢  │
│       │                     │                                ║  │
│       │                     │ Вернулись                      ║  │
│       │                     └────────────────────────────────╝  │
│       ▼                                                         │
│  ┌──────────┐   Activity полностью                              │
│  │ onStop   │ ← скрыта (Home, другое                            │
│  └────┬─────┘   приложение)                                     │
│       │         ─────────────────────────────────────────────┐  │
│       │                     │                                │  │
│       │                     │ onRestart → onStart            │  │
│       │                     └────────────────────────────────┘  │
│       │                                                         │
│       │         Система убила процесс                           │
│       │         или finish() вызван                             │
│       ▼                                                         │
│  ┌───────────┐                                                  │
│  │ onDestroy │ ← Activity уничтожается                          │
│  └───────────┘                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Callback-методы: что делать в каждом

### onCreate()

**Когда вызывается:** Один раз при создании Activity (или при пересоздании после config change).

**Что делать:**
- `setContentView()` — установить layout
- Инициализировать UI компоненты
- Восстановить состояние из `savedInstanceState`
- Создать ViewModel, настроить observers

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 1. Inflate layout
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // 2. Восстановить состояние (если есть)
        val scrollPosition = savedInstanceState?.getInt("scroll_position") ?: 0

        // 3. Настроить UI
        binding.recyclerView.scrollToPosition(scrollPosition)
        binding.button.setOnClickListener { viewModel.loadData() }

        // 4. Подписаться на ViewModel
        viewModel.data.observe(this) { data ->
            binding.textView.text = data
        }
    }
}
```

**Чего НЕ делать:**
- Долгие операции (блокирует UI)
- Запросы к сети (Activity ещё не видна)

### onStart()

**Когда вызывается:** Activity становится видимой (но ещё может не иметь фокуса).

**Что делать:**
- Начать анимации, видео
- Зарегистрировать BroadcastReceiver для UI-событий

```kotlin
override fun onStart() {
    super.onStart()
    // Регистрируем receiver для системных событий
    registerReceiver(batteryReceiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
}
```

### onResume()

**Когда вызывается:** Activity в foreground, пользователь может взаимодействовать.

**Что делать:**
- Возобновить то, что приостановили в onPause
- Начать камеру, сенсоры, GPS

```kotlin
override fun onResume() {
    super.onResume()
    // Начать получать обновления геолокации
    locationClient.requestLocationUpdates(locationRequest, locationCallback, null)
}
```

### onPause()

**Когда вызывается:** Activity теряет фокус (но может быть ещё видна).

**Критически важно:**
- Вызывается ПЕРЕД тем, как другая Activity получит фокус
- Должен быть БЫСТРЫМ (<500ms)
- Следующая Activity не запустится, пока onPause не завершится

**Что делать:**
- Приостановить анимации, видео
- Освободить камеру, сенсоры
- **НЕ сохранять данные** в БД/сеть (слишком долго)

```kotlin
override fun onPause() {
    super.onPause()
    // Остановить геолокацию
    locationClient.removeLocationUpdates(locationCallback)
    // Приостановить видео
    videoPlayer.pause()
}
```

### onStop()

**Когда вызывается:** Activity полностью не видна.

**Что делать:**
- Сохранить данные (в БД, файл)
- Освободить тяжёлые ресурсы
- Отменить регистрацию receivers

```kotlin
override fun onStop() {
    super.onStop()
    // Сохранить черновик в базу
    viewModel.saveDraft()
    // Отменить регистрацию
    unregisterReceiver(batteryReceiver)
}
```

**Важно:** После onStop система может убить процесс в любой момент! onDestroy может не вызваться.

### onDestroy()

**Когда вызывается:**
1. `finish()` вызван
2. Система убивает Activity (config change или нехватка памяти)

**Что делать:**
- Очистить ресурсы, которые не очистились в onStop
- Проверить `isFinishing` чтобы понять причину

```kotlin
override fun onDestroy() {
    super.onDestroy()
    if (isFinishing) {
        // Activity завершается навсегда
        // Очистить кэши, отменить работу
    } else {
        // Configuration change, Activity будет пересоздана
        // ViewModel сохранит данные
    }
}
```

---

## Configuration Change: пересоздание Activity

При изменении конфигурации (поворот экрана, смена языка, изменение размера окна) Activity по умолчанию **полностью пересоздаётся**.

```
Поворот экрана:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Old Activity│     │  Destroyed  │     │ New Activity│
│             │────▶│             │────▶│             │
│  Portrait   │     │onSaveInstance│    │  Landscape  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    savedInstanceState
                           │
                           ▼
                    onCreate(bundle)
```

### Сохранение состояния: savedInstanceState

```kotlin
class FormActivity : AppCompatActivity() {

    private var userInput: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // Восстановить при пересоздании
        userInput = savedInstanceState?.getString("user_input") ?: ""
        binding.editText.setText(userInput)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранить перед уничтожением
        outState.putString("user_input", binding.editText.text.toString())
    }
}
```

**Ограничения savedInstanceState:**
- Только примитивы и Parcelable
- Максимум ~1MB (TransactionTooLargeException)
- Для больших данных используйте ViewModel + Repository

### ViewModel: данные, переживающие config change

ViewModel хранится отдельно от Activity и не уничтожается при config change:

```kotlin
class MainViewModel : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private var isLoading = false

    fun loadUsers() {
        if (isLoading) return  // Не загружать повторно
        isLoading = true

        viewModelScope.launch {
            val result = repository.getUsers()
            _users.value = result
            isLoading = false
        }
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ViewModel переживёт поворот экрана
        // Данные не будут загружаться повторно
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }

        if (savedInstanceState == null) {
            // Первый запуск (не поворот)
            viewModel.loadUsers()
        }
    }
}
```

```
                    Activity 1          Activity 2
                    (portrait)          (landscape)
                         │                   │
                         ▼                   ▼
┌──────────────────────────────────────────────────┐
│                    ViewModel                      │
│              (живёт пока Activity scope)          │
│                                                  │
│     users: List<User>  ──────────────────────▶  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Отключение пересоздания (не рекомендуется)

Можно указать, что Activity сама обработает config change:

```xml
<activity
    android:name=".VideoActivity"
    android:configChanges="orientation|screenSize|keyboardHidden" />
```

```kotlin
override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    // Сами обрабатываем изменение ориентации
    when (newConfig.orientation) {
        Configuration.ORIENTATION_LANDSCAPE -> setupLandscapeLayout()
        Configuration.ORIENTATION_PORTRAIT -> setupPortraitLayout()
    }
}
```

**Почему не рекомендуется:**
- Нужно вручную обрабатывать ВСЕ изменения (язык, размер шрифта, темная тема)
- Легко упустить edge cases
- Compose/ViewModel решают проблему лучше

---

## Распространённые ошибки

### 1. Утечка памяти через Context

```kotlin
// ПЛОХО: Activity утечёт!
object DataManager {
    private var callback: DataCallback? = null

    fun setCallback(callback: DataCallback) {
        this.callback = callback  // Activity не соберётся GC
    }
}

class MainActivity : AppCompatActivity(), DataCallback {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        DataManager.setCallback(this)  // Утечка!
    }
}

// ХОРОШО: очищать в onDestroy
override fun onDestroy() {
    super.onDestroy()
    DataManager.setCallback(null)
}

// ЕЩЁ ЛУЧШЕ: использовать lifecycle-aware компоненты
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(MyLifecycleObserver())
    }
}
```

### 2. Обращение к View после onDestroyView (Fragment)

```kotlin
// ПЛОХО: view может быть null
class MyFragment : Fragment() {
    private var binding: FragmentMyBinding? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding = FragmentMyBinding.bind(view)

        lifecycleScope.launch {
            delay(5000)
            binding?.textView?.text = "Done"  // Crash если Fragment уже destroyed
        }
    }
}

// ХОРОШО: использовать viewLifecycleOwner
lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        delay(5000)
        binding?.textView?.text = "Done"  // Отменится автоматически
    }
}
```

### 3. Сетевой запрос в onCreate без проверки

```kotlin
// ПЛОХО: загрузит дважды при повороте
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    loadDataFromNetwork()  // Каждый раз при пересоздании
}

// ХОРОШО: проверить savedInstanceState
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState == null) {
        loadDataFromNetwork()  // Только при первом создании
    }
}

// ЕЩЁ ЛУЧШЕ: ViewModel сам управляет загрузкой
class MyViewModel : ViewModel() {
    val data = liveData {
        emit(repository.loadData())  // Загрузится один раз
    }
}
```

### 4. Потеря данных при process death

```kotlin
// ПЛОХО: данные пропадут при убийстве процесса
class FormViewModel : ViewModel() {
    var draftText: String = ""  // Пропадёт!
}

// ХОРОШО: SavedStateHandle
class FormViewModel(private val savedState: SavedStateHandle) : ViewModel() {

    var draftText: String
        get() = savedState["draft"] ?: ""
        set(value) { savedState["draft"] = value }
}
```

---

## Lifecycle-aware компоненты

### LifecycleObserver

Компонент, который автоматически реагирует на lifecycle:

```kotlin
class LocationObserver(
    private val context: Context,
    private val onLocation: (Location) -> Unit
) : DefaultLifecycleObserver {

    private val locationClient = LocationServices.getFusedLocationProviderClient(context)

    override fun onStart(owner: LifecycleOwner) {
        // Автоматически при onStart Activity/Fragment
        startLocationUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        // Автоматически при onStop
        stopLocationUpdates()
    }

    private fun startLocationUpdates() { /* ... */ }
    private fun stopLocationUpdates() { /* ... */ }
}

// Использование
class MapActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationObserver = LocationObserver(this) { location ->
            updateMap(location)
        }
        lifecycle.addObserver(locationObserver)
    }
}
```

### LiveData и lifecycle

LiveData автоматически учитывает lifecycle:

```kotlin
viewModel.data.observe(this) { data ->
    // Вызывается только когда Activity в STARTED или RESUMED
    // Автоматически отписывается в onDestroy
    binding.textView.text = data
}
```

### Flow и repeatOnLifecycle

```kotlin
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        // Этот блок выполняется когда lifecycle >= STARTED
        // Автоматически отменяется когда lifecycle < STARTED
        viewModel.uiState.collect { state ->
            updateUI(state)
        }
    }
}
```

---

## Тестирование lifecycle

```kotlin
@Test
fun `ViewModel data survives configuration change`() {
    // Создать Activity
    val scenario = launchActivity<MainActivity>()

    scenario.onActivity { activity ->
        // Загрузить данные
        activity.viewModel.loadData()
    }

    // Симулировать поворот экрана
    scenario.recreate()

    scenario.onActivity { activity ->
        // Данные должны сохраниться
        assertNotNull(activity.viewModel.data.value)
    }
}
```

---

## Чеклист

```
□ onCreate: только инициализация UI, никаких долгих операций
□ onStart/onStop: регистрация/отмена BroadcastReceiver
□ onResume/onPause: камера, сенсоры, геолокация
□ onSaveInstanceState: только маленькие данные (scroll position, input)
□ ViewModel: данные, которые не должны теряться при повороте
□ SavedStateHandle: данные ViewModel, переживающие process death
□ Нет утечек: очищать callbacks в onDestroy
□ Lifecycle-aware: использовать LiveData, Flow + repeatOnLifecycle
```

---

## Проверь себя

<details>
<summary>1. Какие методы lifecycle вызываются при повороте экрана?</summary>

**Ответ:** Activity полностью уничтожается и создаётся заново:
1. `onPause()` → `onStop()` → `onSaveInstanceState()` → `onDestroy()`
2. `onCreate(savedInstanceState)` → `onStart()` → `onRestoreInstanceState()` → `onResume()`

Данные сохраняются в `savedInstanceState` Bundle. Поэтому ViewModel важен — он переживает configuration changes.

</details>

<details>
<summary>2. Когда вызывается onSaveInstanceState(), а когда onStop()?</summary>

**Ответ:**
- `onStop()` — всегда при уходе Activity в background (не видна)
- `onSaveInstanceState()` — когда система может убить Activity позже (configuration change, уход в background). НЕ вызывается если пользователь явно закрыл Activity (back button, finish()).

Важно: `onSaveInstanceState()` вызывается ПОСЛЕ `onStop()` (Android P+), раньше было перед.

</details>

<details>
<summary>3. Чем отличается finish() от onDestroy()?</summary>

**Ответ:**
- `finish()` — ты просишь систему закрыть Activity. Activity будет удалена из back stack.
- `onDestroy()` — callback, сообщающий что Activity уничтожается. Может быть вызван системой (configuration change, нехватка памяти) ИЛИ после finish().

После finish() — onDestroy() вызовется. Но onDestroy() может быть без finish() (configuration change).

</details>

<details>
<summary>4. Почему нельзя сохранять большие объекты в savedInstanceState?</summary>

**Ответ:** savedInstanceState передаётся через Binder (IPC механизм Android). Лимит транзакции Binder ~1MB на весь процесс. Большой Bundle = TransactionTooLargeException. Сохраняй только IDs и ключевые данные. Для больших данных — ViewModel, Room, файловый кэш.

</details>

---

## Связи

**Фундамент:**
- [[android-overview]] — контекст Android-приложений, процессы и компоненты
- [[os-processes-threads]] — почему Android убивает процессы, LMK (Low Memory Killer)

**Связанные концепции:**
- [[android-app-components]] — Activity как один из 4 компонентов приложения
- [[android-process-memory]] — как Android управляет памятью и решает что убить

**Решения проблем lifecycle:**
- [[android-architecture]] — ViewModel переживает configuration changes
- [[android-compose]] — Compose имеет свой lifecycle (Composition), интегрированный с Activity
- [[android-navigation]] — Navigation component управляет lifecycle destinations
- [[android-bundle-parcelable]] — Bundle и savedInstanceState: как данные сохраняются через Binder IPC при пересоздании Activity

**Практика:**
- [[android-data-persistence]] — как правильно сохранять данные между lifecycle transitions
- [[android-background-work]] — когда приложение в background, но работа продолжается

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Моё приложение контролирует lifecycle" | Система (Android) контролирует. Activity может быть убита в любой момент без предупреждения |
| "ViewModel сохраняет данные при process death" | Нет! ViewModel теряется. Используй SavedStateHandle или persistent storage |
| "onDestroy() всегда вызывается" | Не гарантируется при process death. Сохраняй важное в onStop() |
| "Пользователи не поворачивают экран" | 60% регулярно переключаются между portrait/landscape |
| "configChanges в манифесте — хорошее решение" | Плохо: нужно обрабатывать ВСЕ changes вручную, легко упустить edge cases |

## CS-фундамент

| Концепция | Применение в Activity Lifecycle |
|-----------|--------------------------------|
| Process Lifecycle | Android убивает процессы для освобождения памяти → Activity должна быть готова к пересозданию |
| State Machine | Activity — конечный автомат: CREATED→STARTED→RESUMED→PAUSED→STOPPED→DESTROYED |
| Resource Management | onPause/onStop — освобождение ресурсов (камера, GPS), иначе battery drain |
| Callback Pattern | Система вызывает методы Activity, инверсия контроля (IoC) |
| Serialization | savedInstanceState → Bundle → Parcel (IPC), ограничение ~1MB |

## Источники

- [The Activity Lifecycle - Android Developers](https://developer.android.com/guide/components/activities/activity-lifecycle) — официальная документация
- [Handling Lifecycles with Lifecycle-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle) — lifecycle-aware компоненты
- [Activity Lifecycle Codelab](https://developer.android.com/codelabs/basic-android-kotlin-compose-activity-lifecycle) — практический codelab
- [ViewModel Persistence - droidcon](https://www.droidcon.com/2025/01/13/understanding-viewmodel-persistence-across-configuration-changes-in-android/) — ViewModel и config changes

---

*Проверено: 2026-01-09 | Android 14+, Kotlin 2.x*
