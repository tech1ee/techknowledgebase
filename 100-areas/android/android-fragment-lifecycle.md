---
title: "Fragment Lifecycle: состояния, View lifecycle и FragmentManager под капотом"
created: 2026-01-27
modified: 2026-01-27
type: deep-dive
area: android
confidence: high
tags:
  - android
  - fragment
  - lifecycle
  - fragmentmanager
  - viewlifecycleowner
  - backstack
  - navigation
related:
  - "[[android-activity-lifecycle]]"
  - "[[android-navigation]]"
  - "[[android-navigation-evolution]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-state-management]]"
  - "[[android-context-internals]]"
cs-foundations: [state-machine, stack-data-structure, observer-pattern, command-pattern, decorator-pattern]
---

# Fragment Lifecycle: состояния, View lifecycle и FragmentManager под капотом

> Fragment проходит 5 состояний (INITIALIZED -> CREATED -> STARTED -> RESUMED -> DESTROYED). View lifecycle отделён от Fragment lifecycle: onDestroyView() != onDestroy() -- Fragment может пережить уничтожение своего View. FragmentManager управляет состоянием через FragmentStateManager (per-fragment) и SpecialEffectsController (per-container). commit() async через Handler, commitNow() sync но без back stack. viewLifecycleOwner -- для LiveData/Flow наблюдения в Fragment (не this!). Fragment Result API заменяет setTargetFragment(). ViewModel scoping: viewModels() -> Fragment, activityViewModels() -> Activity, navGraphViewModels() -> Navigation Graph.

---

## Зачем это нужно

### Проблема: скрытая сложность Fragment

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| IllegalStateException after state saved | commit() после onSaveInstanceState() | Крэш приложения |
| Memory leak от LiveData observers | Наблюдение через `this` вместо `viewLifecycleOwner` | Утечка памяти, дублирование обработки |
| View is null после onDestroyView | Обращение к View после возврата с back stack | NullPointerException |
| Fragment not attached crash | Обращение к `requireContext()` после detach | IllegalStateException |
| Back stack confusion | Непонимание разницы addToBackStack/replace/add | Наложение Fragment, потеря состояния |
| Дублирование Fragment при ротации | Ручное создание вместо восстановления из savedState | Два одинаковых Fragment в контейнере |
| onActivityResult не вызывается | Вложенные Fragment, неправильный requestCode | Потерянные результаты |
| ViewModel неправильный scope | viewModels() vs activityViewModels() путаница | Данные не расшариваются или живут слишком долго |
| Утечка binding после onDestroyView | ViewBinding не обнуляется в onDestroyView | Удержание всей View-иерархии в памяти |
| Анимации ломают lifecycle | SpecialEffectsController задерживает transition | Callbacks вызываются не в ожидаемом порядке |

### Актуальность в 2025-2026

**Fragment всё ещё актуален:**

```kotlin
// Fragment остаётся основой Android навигации
// NavHostFragment -- основа Jetpack Navigation
class NavHostFragment : Fragment() {
    // Навигация между экранами = замена Fragment'ов
}

// Даже в Compose-first проектах Fragment используется как хост
class ComposeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
            )
            setContent {
                MyComposableScreen()
            }
        }
    }
}
```

**Статистика (2025):**
- **60%+** Android проектов используют Fragment (рядом с Compose)
- Jetpack Navigation построена на Fragment (NavHostFragment)
- Fragment 1.8+ с Kotlin-first API и улучшенным lifecycle
- Google рекомендует постепенную миграцию на Compose, но Fragment будет поддерживаться

**Что вы узнаете:**
1. Как работают 5 состояний Fragment lifecycle и отличие от Activity
2. Критическое различие View lifecycle и Fragment lifecycle
3. Внутреннее устройство FragmentManager (FragmentStateManager, SpecialEffectsController)
4. Все варианты commit() и когда использовать каждый
5. Fragment Result API, ViewModel scoping, FragmentFactory
6. Fragment + Compose интеграция

---

## Prerequisites

Для полного понимания материала необходимо:

| Тема | Зачем нужна | Ссылка |
|------|-------------|--------|
| Activity Lifecycle | Fragment lifecycle вложен в Activity lifecycle; максимальное состояние Fragment = состояние Activity | [[android-activity-lifecycle]] |
| Jetpack Navigation | Navigation Component построен на Fragment; NavHostFragment управляет заменой Fragment | [[android-navigation]] |
| ViewModel Internals | ViewModel scoping зависит от Fragment/Activity/NavGraph lifecycle | [[android-viewmodel-internals]] |
| Context Internals | Fragment получает Context через onAttach(); requireContext() зависит от attach-состояния | [[android-context-internals]] |
| State Management | savedInstanceState, onSaveInstanceState, процесс восстановления | [[android-state-management]] |

---

## Терминология

### Fragment
**Fragment** -- модульный компонент UI, который имеет собственный lifecycle, получает input events и может быть добавлен/удалён из Activity. Fragment всегда хостится внутри Activity и его lifecycle напрямую зависит от lifecycle хост-Activity.

### FragmentManager
**FragmentManager** -- класс, ответственный за добавление, удаление, замену Fragment'ов и управление back stack. Каждая Activity имеет `supportFragmentManager`, каждый Fragment имеет `childFragmentManager` для вложенных Fragment.

### FragmentTransaction
**FragmentTransaction** -- набор операций (add, remove, replace, attach, detach, show, hide) над Fragment'ами, выполняемый атомарно. Создаётся через `fragmentManager.beginTransaction()`.

### BackStackRecord
**BackStackRecord** -- внутренняя реализация FragmentTransaction, которая записывает операции и может быть сохранена в back stack для последующего pop (отмены).

### FragmentStateManager
**FragmentStateManager** -- внутренний класс (с Fragment 1.4+), управляющий lifecycle каждого конкретного Fragment. Вычисляет ожидаемое состояние через `computeExpectedState()` и выполняет переходы.

### SpecialEffectsController
**SpecialEffectsController** -- внутренний контроллер (per-container), управляющий анимациями и переходами между Fragment'ами. Координирует enter/exit/shared element transitions.

### viewLifecycleOwner
**viewLifecycleOwner** -- LifecycleOwner, привязанный к View фрагмента. Валиден от onCreateView() до onDestroyView(). Используется для наблюдения LiveData/Flow из Fragment, чтобы избежать утечек памяти.

### FragmentFactory
**FragmentFactory** -- фабрика для создания экземпляров Fragment. По умолчанию использует рефлексию (no-arg constructor). Может быть переопределена для dependency injection.

### Fragment Result API
**Fragment Result API** -- механизм передачи данных между Fragment'ами через `setFragmentResult()`/`setFragmentResultListener()`. Заменяет deprecated `setTargetFragment()`. Безопасен при process death/recreation.

### NavHostFragment
**NavHostFragment** -- специальный Fragment из Jetpack Navigation, который выступает контейнером для навигации. Управляет заменой destination Fragment'ов через NavController.

---

## 1. Fragment Lifecycle: 5 состояний

### ЧТО: конечный автомат Fragment

Fragment проходит через 5 основных состояний, определённых в `Lifecycle.State`:

```
┌──────────────────────────────────────────────────────────────────┐
│                  Fragment Lifecycle State Machine                 │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │ INITIALIZED │ ← Fragment создан, но не добавлен в FM          │
│  └──────┬──────┘                                                 │
│         │ add/replace → FM                                       │
│         ▼                                                        │
│  ┌─────────────┐                                                 │
│  │   CREATED   │ ← onCreate() вызван, View ещё не создан        │
│  └──────┬──────┘                                                 │
│         │ Activity.onStart()                                     │
│         ▼                                                        │
│  ┌─────────────┐                                                 │
│  │   STARTED   │ ← onStart() вызван, Fragment видим              │
│  └──────┬──────┘                                                 │
│         │ Activity.onResume()                                    │
│         ▼                                                        │
│  ┌─────────────┐                                                 │
│  │   RESUMED   │ ← onResume() вызван, Fragment интерактивен      │
│  └─────────────┘                                                 │
│                                                                  │
│  Обратный путь:                                                  │
│  RESUMED → STARTED → CREATED → DESTROYED                        │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │  DESTROYED  │ ← Fragment полностью уничтожен                  │
│  └─────────────┘                                                 │
└──────────────────────────────────────────────────────────────────┘
```

### ПОЧЕМУ: зачем столько состояний

Fragment повторяет модель Activity lifecycle, но добавляет дополнительные callbacks для View-управления. Это необходимо потому что:

1. **Fragment может существовать без View** -- в back stack Fragment находится в CREATED состоянии (View уничтожен)
2. **Fragment вложен в Activity** -- его состояние не может превышать состояние хост-Activity
3. **Модульность** -- Fragment можно переиспользовать в разных Activity
4. **Управление ресурсами** -- разные уровни lifecycle позволяют освобождать ресурсы на правильном этапе

### КАК РАБОТАЕТ: callbacks в порядке вызова

**Восходящий путь (создание):**

```
onAttach(context)           ← Fragment присоединён к Activity
    │                         Context доступен
    ▼
onCreate(savedInstanceState) ← Инициализация non-UI компонентов
    │                         ViewModel, аргументы, восстановление
    ▼
onCreateView(inflater,       ← Создание View-иерархии
  container,                   Inflate layout или создание ComposeView
  savedInstanceState)
    │
    ▼
onViewCreated(view,          ← View создан, настройка UI
  savedInstanceState)          findViewById, RecyclerView setup, observers
    │
    ▼
onViewStateRestored(         ← Состояние View восстановлено
  savedInstanceState)          EditText text, ScrollView position
    │
    ▼
onStart()                    ← Fragment видим пользователю
    │                         Можно запускать анимации
    ▼
onResume()                   ← Fragment интерактивен
                               Можно слушать input events
```

**Нисходящий путь (уничтожение):**

```
onPause()                    ← Fragment теряет фокус
    │                         Приостановить интерактивные операции
    ▼
onStop()                     ← Fragment больше не видим
    │                         Остановить анимации, освободить тяжёлые ресурсы
    ▼
onSaveInstanceState(outState) ← Сохранение состояния
    │                          Сохранить данные для восстановления
    ▼
onDestroyView()              ← View уничтожается
    │                         Обнулить binding, удалить View-слушатели
    ▼
onDestroy()                  ← Fragment уничтожается
    │                         Финальная очистка
    ▼
onDetach()                   ← Fragment отсоединён от Activity
                               Context больше не доступен
```

### КАК ПРИМЕНЯТЬ: типичный Fragment

```kotlin
class UserProfileFragment : Fragment(R.layout.fragment_user_profile) {

    // ViewModel с scope к этому Fragment
    private val viewModel: UserProfileViewModel by viewModels()

    // ViewBinding -- обнуляется в onDestroyView
    private var _binding: FragmentUserProfileBinding? = null
    private val binding get() = _binding!!

    // Аргументы -- безопасный способ передачи данных
    private val args: UserProfileFragmentArgs by navArgs()

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Context доступен
        // Можно получить зависимости из Activity/Application
        Log.d("Lifecycle", "onAttach: context = $context")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Инициализация NON-UI компонентов
        // ViewModel уже создан через by viewModels()
        // Получаем аргументы
        val userId = args.userId
        Log.d("Lifecycle", "onCreate: userId = $userId")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Создание View-иерархии
        _binding = FragmentUserProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Настройка UI ПОСЛЕ создания View
        setupRecyclerView()
        setupClickListeners()

        // КРИТИЧЕСКИ ВАЖНО: viewLifecycleOwner, НЕ this!
        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            binding.userName.text = profile.name
            binding.userEmail.text = profile.email
        }

        // Flow наблюдение -- тоже viewLifecycleOwner
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }

    override fun onViewStateRestored(savedInstanceState: Bundle?) {
        super.onViewStateRestored(savedInstanceState)
        // View state восстановлен системой (EditText text, etc.)
        // Можно читать состояние View элементов
    }

    override fun onStart() {
        super.onStart()
        // Fragment видим -- запустить анимации, начать обновления
    }

    override fun onResume() {
        super.onResume()
        // Fragment интерактивен -- начать слушать сенсоры, камеру и т.д.
    }

    override fun onPause() {
        super.onPause()
        // Приостановить интерактивные операции
    }

    override fun onStop() {
        super.onStop()
        // Fragment не видим -- остановить анимации
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранить состояние, которое View не сохраняет автоматически
        outState.putInt("scroll_position", currentScrollPosition)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ОБЯЗАТЕЛЬНО: обнулить binding чтобы избежать утечки памяти
        _binding = null
    }

    override fun onDestroy() {
        super.onDestroy()
        // Финальная очистка (редко нужна, ViewModel сделает это в onCleared)
    }

    override fun onDetach() {
        super.onDetach()
        // Context больше не доступен
        // requireContext() вызовет IllegalStateException
    }

    private fun setupRecyclerView() { /* ... */ }
    private fun setupClickListeners() { /* ... */ }
    private fun updateUI(state: UiState) { /* ... */ }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. Обращение к View после onDestroyView:**

```kotlin
// ❌ НЕПРАВИЛЬНО: View может быть null
class BadFragment : Fragment() {
    private lateinit var textView: TextView

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        textView = view.findViewById(R.id.textView)
    }

    // Этот callback может быть вызван после onDestroyView!
    fun updateFromOutside(text: String) {
        textView.text = text // CRASH: View уже уничтожен
    }
}

// ✅ ПРАВИЛЬНО: проверка View или использование binding
class GoodFragment : Fragment() {
    private var _binding: FragmentBinding? = null
    private val binding get() = _binding!!

    fun updateFromOutside(text: String) {
        // Безопасная проверка
        _binding?.textView?.text = text
        // или
        view?.findViewById<TextView>(R.id.textView)?.text = text
    }
}
```

**2. Отличие от Activity: дополнительные callbacks**

```
Activity:                          Fragment:
                                   onAttach()        ← НЕТ в Activity
onCreate()                         onCreate()
                                   onCreateView()    ← НЕТ в Activity
                                   onViewCreated()   ← НЕТ в Activity
                                   onViewStateRestored()
onStart()                          onStart()
onResume()                         onResume()
onPause()                          onPause()
onStop()                           onStop()
onSaveInstanceState()              onSaveInstanceState()
                                   onDestroyView()   ← НЕТ в Activity
onDestroy()                        onDestroy()
                                   onDetach()        ← НЕТ в Activity
```

**3. Порядок onSaveInstanceState относительно onStop:**

```kotlin
// До Android P (API 28):
// onSaveInstanceState() вызывался ПЕРЕД onStop()
// onPause() → onSaveInstanceState() → onStop()

// С Android P (API 28+):
// onSaveInstanceState() вызывается ПОСЛЕ onStop()
// onPause() → onStop() → onSaveInstanceState()

// Fragment 1.3.0+ всегда следует новому порядку
// независимо от API уровня
```

---

## 2. View Lifecycle vs Fragment Lifecycle

### ЧТО: два отдельных lifecycle

Это **ключевая концепция**, которую чаще всего неправильно понимают. Fragment имеет ДВА lifecycle:

1. **Fragment lifecycle** -- от `onAttach()` до `onDetach()`
2. **View lifecycle** -- от `onCreateView()` до `onDestroyView()`

View lifecycle **короче** и может **повторяться** без пересоздания Fragment.

### ПОЧЕМУ: back stack и configuration changes

Когда Fragment помещается в back stack (например, при навигации вперёд), View уничтожается, но сам Fragment остаётся в памяти:

```
Сценарий: Fragment A → navigate → Fragment B (addToBackStack)

Fragment A lifecycle:                Fragment A View lifecycle:
onAttach()     ──────────┐          onCreateView()  ──────────┐
onCreate()               │          onViewCreated()            │
                         │                                     │
[навигация к B]          │          [навигация к B]            │
                         │          onDestroyView() ───────────┘ ← View УНИЧТОЖЕН
                         │
[нажатие Back]           │          [нажатие Back]
                         │          onCreateView()  ──────────┐ ← НОВЫЙ View
                         │          onViewCreated()            │
                         │                                     │
[закрытие Activity]      │                                     │
onDestroy()              │          onDestroyView() ───────────┘
onDetach()     ──────────┘
```

```
┌──────────────────────────────────────────────────────────────────────┐
│                Fragment Lifecycle vs View Lifecycle                    │
│                                                                      │
│  Fragment lifecycle (this):                                          │
│  ├────────────────────────────────────────────────────────────────┤  │
│  onAttach → onCreate → ... → onDestroy → onDetach                   │
│                                                                      │
│  View lifecycle #1 (viewLifecycleOwner):                            │
│  ├───────────────────────┤                                          │
│  onCreateView → onDestroyView   ← уход в back stack                │
│                                                                      │
│  View lifecycle #2 (viewLifecycleOwner):                            │
│          ├───────────────────────────────────────┤                   │
│          onCreateView → onDestroyView   ← возврат из back stack     │
│                                                                      │
│  Fragment lifecycle продолжается!                                    │
│  View lifecycle перезапускается!                                     │
└──────────────────────────────────────────────────────────────────────┘
```

### КАК РАБОТАЕТ: viewLifecycleOwner

`viewLifecycleOwner` -- это `LifecycleOwner`, который:
- Создаётся в `onCreateView()`
- Переходит в DESTROYED в `onDestroyView()`
- Все наблюдатели, привязанные к нему, автоматически отписываются

```kotlin
// Внутри Fragment (упрощённо из AOSP)
class Fragment {
    // Fragment's own lifecycle
    private val mLifecycleRegistry = LifecycleRegistry(this)

    // View lifecycle -- отдельный!
    private var mViewLifecycleOwner: FragmentViewLifecycleOwner? = null

    fun performCreateView(...) {
        // Создаём View lifecycle owner
        mViewLifecycleOwner = FragmentViewLifecycleOwner(
            this, // Fragment как LifecycleOwner-parent
            getViewModelStore()
        )

        val view = onCreateView(inflater, container, savedInstanceState)

        if (view != null) {
            // Инициализируем View lifecycle
            mViewLifecycleOwner!!.initialize()
        }
    }

    fun performDestroyView() {
        // View lifecycle переходит в DESTROYED
        mViewLifecycleOwner?.handleLifecycleEvent(Lifecycle.Event.ON_DESTROY)

        onDestroyView()

        // View lifecycle owner сбрасывается
        mViewLifecycleOwner = null
    }

    // Публичный API
    val viewLifecycleOwner: LifecycleOwner
        get() {
            val owner = mViewLifecycleOwner
                ?: throw IllegalStateException(
                    "Can't access the Fragment View's LifecycleOwner when " +
                    "getView() is null i.e., before onCreateView() or after " +
                    "onDestroyView()"
                )
            return owner
        }
}
```

### КАК ПРИМЕНЯТЬ: правильное наблюдение

```kotlin
class SearchFragment : Fragment(R.layout.fragment_search) {

    private val viewModel: SearchViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ────────────────────────────────────────────────
        // ❌ НЕПРАВИЛЬНО: LiveData.observe(this, ...)
        // ────────────────────────────────────────────────
        // Если Fragment в back stack:
        // 1. onDestroyView() вызван, onDestroy() НЕ вызван
        // 2. Fragment lifecycle ещё CREATED
        // 3. Observer НЕ отписан (lifecycle не DESTROYED)
        // 4. Возврат из back stack → новый onCreateView()
        // 5. Новый observe() добавляет ВТОРОЙ observer
        // 6. Теперь ДВА observer'а обрабатывают одни данные!
        viewModel.searchResults.observe(this) { results ->  // ❌
            // ДУБЛИРОВАНИЕ: при возврате из back stack
            adapter.submitList(results)
        }

        // ────────────────────────────────────────────────
        // ✅ ПРАВИЛЬНО: LiveData.observe(viewLifecycleOwner, ...)
        // ────────────────────────────────────────────────
        // viewLifecycleOwner переходит в DESTROYED при onDestroyView()
        // Observer автоматически отписывается
        // При возврате из back stack создаётся новый viewLifecycleOwner
        // Только один активный observer
        viewModel.searchResults.observe(viewLifecycleOwner) { results ->  // ✅
            adapter.submitList(results)
        }

        // ────────────────────────────────────────────────
        // ✅ ПРАВИЛЬНО: Flow с viewLifecycleOwner
        // ────────────────────────────────────────────────
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

**Визуализация проблемы с `this`:**

```
Время:  ──────────────────────────────────────────────────→

Fragment A показан:
  onViewCreated() → observe(this, observer1)
  observer1 активен ✓

Navigate to B (addToBackStack):
  onDestroyView() вызван
  Fragment lifecycle: CREATED (жив!)
  observer1: НЕ отписан (lifecycle не DESTROYED)

Back pressed, возврат к A:
  onCreateView() → новый View
  onViewCreated() → observe(this, observer2)
  observer1: всё ещё активен!  ← УТЕЧКА
  observer2: активен
  Теперь ДВА observer'а работают одновременно!

Каждый back → forward цикл добавляет ещё один observer:
  observer1, observer2, observer3, ... → MEMORY LEAK
```

**Визуализация с viewLifecycleOwner:**

```
Время:  ──────────────────────────────────────────────────→

Fragment A показан:
  viewLifecycleOwner #1 создан
  onViewCreated() → observe(viewLifecycleOwner, observer1)
  observer1 активен ✓

Navigate to B (addToBackStack):
  onDestroyView() → viewLifecycleOwner #1 → DESTROYED
  observer1: АВТОМАТИЧЕСКИ отписан ✓

Back pressed, возврат к A:
  viewLifecycleOwner #2 создан (НОВЫЙ!)
  onViewCreated() → observe(viewLifecycleOwner, observer2)
  observer2: единственный активный ✓

Всегда только ОДИН observer! ✓
```

### ПОДВОДНЫЕ КАМНИ

**1. Доступ к viewLifecycleOwner вне окна View lifecycle:**

```kotlin
// ❌ CRASH: доступ в onCreate() -- View ещё не создан
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val owner = viewLifecycleOwner // IllegalStateException!
}

// ❌ CRASH: доступ в onDestroyView() после super
override fun onDestroyView() {
    super.onDestroyView()
    val owner = viewLifecycleOwner // IllegalStateException!
}

// ✅ ПРАВИЛЬНО: использовать в onViewCreated() - onDestroyView()
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    val owner = viewLifecycleOwner // OK
}
```

**2. ComposeView требует правильную ViewCompositionStrategy:**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    return ComposeView(requireContext()).apply {
        // ❌ НЕПРАВИЛЬНО: по умолчанию DisposeOnDetachedFromWindow
        // Compose disposes при detach от window, но Fragment может
        // быть в transition анимации и View ещё attached

        // ✅ ПРАВИЛЬНО: dispose когда View lifecycle DESTROYED
        setViewCompositionStrategy(
            ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
        )
        setContent {
            MyTheme {
                MyScreen(viewModel = viewModel)
            }
        }
    }
}
```

**3. ViewBinding утечка памяти:**

```kotlin
class LeakyFragment : Fragment(R.layout.fragment_example) {

    // ❌ УТЕЧКА: binding держит ссылку на View после onDestroyView
    private lateinit var binding: FragmentExampleBinding

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding = FragmentExampleBinding.bind(view)
    }
    // binding.root всё ещё ссылается на старый View!
}

class SafeFragment : Fragment(R.layout.fragment_example) {

    // ✅ ПРАВИЛЬНО: nullable binding с обнулением
    private var _binding: FragmentExampleBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        _binding = FragmentExampleBinding.bind(view)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // ОБЯЗАТЕЛЬНО обнулить!
    }
}
```

---

## 3. FragmentManager Internals

### ЧТО: архитектура управления Fragment

FragmentManager -- центральный координатор, управляющий жизненным циклом всех Fragment'ов в данном контейнере.

```
┌─────────────────────────────────────────────────────────────┐
│                     FragmentManager                          │
│                                                             │
│  ┌──────────────────┐    ┌───────────────────────────────┐  │
│  │   FragmentStore   │    │       BackStack               │  │
│  │                   │    │  ┌─────────────────────────┐  │  │
│  │ Active Fragments: │    │  │ BackStackRecord #3      │  │  │
│  │  - Fragment A     │    │  │ BackStackRecord #2      │  │  │
│  │  - Fragment B     │    │  │ BackStackRecord #1      │  │  │
│  │                   │    │  └─────────────────────────┘  │  │
│  │ Added Fragments:  │    │                               │  │
│  │  - Fragment B     │    │  (Stack: LIFO)                │  │
│  └──────────────────┘    └───────────────────────────────┘  │
│                                                             │
│  Per-Fragment:                      Per-Container:          │
│  ┌─────────────────────┐   ┌──────────────────────────┐    │
│  │ FragmentStateManager│   │ SpecialEffectsController  │    │
│  │ (Fragment A)        │   │ (container R.id.container)│    │
│  ├─────────────────────┤   ├──────────────────────────┤    │
│  │ FragmentStateManager│   │ Manages transitions:      │    │
│  │ (Fragment B)        │   │  - enter/exit animations  │    │
│  └─────────────────────┘   │  - shared element trans.  │    │
│                            └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### ПОЧЕМУ: перестройка архитектуры (Ian Lake)

До Fragment 1.4.0 вся логика lifecycle переходов была внутри одного метода `moveToState()` в FragmentManager -- монолитного switch-case на ~500 строк. Перестройка разделила ответственности:

- **FragmentStateManager** -- отвечает за lifecycle одного Fragment
- **SpecialEffectsController** -- отвечает за анимации/transitions одного контейнера
- **FragmentStore** -- отвечает за хранение и поиск Fragment'ов

### КАК РАБОТАЕТ: внутренний flow

**FragmentStore: хранилище Fragment'ов**

```kotlin
// Внутри FragmentManager (упрощённо из AOSP)
class FragmentStore {

    // Все когда-либо добавленные Fragment'ы (включая в back stack)
    // Key = Fragment.mWho (уникальный UUID)
    private val mActive = HashMap<String, FragmentStateManager>()

    // Fragment'ы, которые "добавлены" (visible или managed)
    // Упорядочены по порядку добавления
    private val mAdded = ArrayList<Fragment>()

    // Получить Fragment по tag
    fun findFragmentByTag(tag: String): Fragment? {
        return mAdded.firstOrNull { it.tag == tag }
            ?: mActive.values.map { it.fragment }
                .firstOrNull { it.tag == tag }
    }

    // Получить Fragment по id контейнера
    fun findFragmentById(id: Int): Fragment? {
        return mAdded.lastOrNull { it.mFragmentId == id }
            ?: mActive.values.map { it.fragment }
                .lastOrNull { it.mFragmentId == id }
    }
}
```

**FragmentStateManager: управление lifecycle одного Fragment**

```kotlin
// Упрощённая версия из AOSP
class FragmentStateManager(
    private val dispatcher: FragmentLifecycleCallbacksDispatcher,
    private val fragmentStore: FragmentStore,
    val fragment: Fragment
) {

    // Вычисление ожидаемого состояния
    fun computeExpectedState(): Int {
        // Максимальное состояние = состояние хост-Activity
        var maxState = fragment.mHost.currentState

        // Если Fragment скрыт -- максимум STARTED
        if (fragment.mHidden) {
            maxState = min(maxState, Fragment.STARTED)
        }

        // Если Fragment в back stack -- максимум CREATED
        // (View уничтожен, но Fragment жив)
        if (fragment.isInBackStack) {
            maxState = min(maxState, Fragment.CREATED)
        }

        // Если Fragment удалён -- INITIALIZED
        if (fragment.mRemoving) {
            maxState = if (fragment.isInBackStack) {
                Fragment.CREATED
            } else {
                Fragment.INITIALIZED
            }
        }

        return maxState
    }

    // Переход к ожидаемому состоянию
    fun moveToExpectedState() {
        val expectedState = computeExpectedState()
        val currentState = fragment.mState

        if (currentState < expectedState) {
            // Восходящий путь: INITIALIZED → CREATED → STARTED → RESUMED
            when (expectedState) {
                Fragment.CREATED -> {
                    fragment.performAttach()
                    fragment.performCreate(fragment.mSavedFragmentState)
                    fragment.performCreateView(...)
                    fragment.performViewCreated()
                }
                Fragment.STARTED -> {
                    fragment.performStart()
                }
                Fragment.RESUMED -> {
                    fragment.performResume()
                }
            }
        } else if (currentState > expectedState) {
            // Нисходящий путь: RESUMED → STARTED → CREATED → DESTROYED
            when (expectedState) {
                Fragment.STARTED -> {
                    fragment.performPause()
                }
                Fragment.CREATED -> {
                    fragment.performStop()
                    fragment.performDestroyView()
                }
                Fragment.INITIALIZED -> {
                    fragment.performDestroy()
                    fragment.performDetach()
                }
            }
        }
    }
}
```

**BackStackRecord: запись транзакции**

```kotlin
// BackStackRecord реализует FragmentTransaction
class BackStackRecord(
    val fragmentManager: FragmentManager
) : FragmentTransaction() {

    // Список операций в транзакции
    val mOps = ArrayList<Op>()

    // Одна операция
    class Op(
        val cmd: Int,           // CMD_ADD, CMD_REMOVE, CMD_REPLACE, ...
        val fragment: Fragment,
        val enterAnim: Int,
        val exitAnim: Int
    )

    // Команды
    companion object {
        const val CMD_ADD = 1
        const val CMD_REMOVE = 3
        const val CMD_REPLACE = 8
        const val CMD_ATTACH = 7
        const val CMD_DETACH = 6
        const val CMD_HIDE = 4
        const val CMD_SHOW = 5
        const val CMD_SET_PRIMARY_NAV = 9
    }

    override fun add(containerViewId: Int, fragment: Fragment, tag: String?): FragmentTransaction {
        addOp(Op(CMD_ADD, fragment, ...))
        return this
    }

    override fun replace(containerViewId: Int, fragment: Fragment, tag: String?): FragmentTransaction {
        addOp(Op(CMD_REPLACE, fragment, ...))
        return this
    }

    // executeOps: выполнение всех операций
    fun executeOps() {
        for (op in mOps) {
            when (op.cmd) {
                CMD_ADD -> {
                    fragmentManager.addFragment(op.fragment)
                }
                CMD_REMOVE -> {
                    fragmentManager.removeFragment(op.fragment)
                }
                CMD_REPLACE -> {
                    // Удалить все Fragment'ы в контейнере
                    // Добавить новый Fragment
                    fragmentManager.replaceFragment(op.fragment)
                }
                CMD_HIDE -> {
                    fragmentManager.hideFragment(op.fragment)
                }
                CMD_SHOW -> {
                    fragmentManager.showFragment(op.fragment)
                }
            }
        }
    }
}
```

**Child FragmentManager: вложенные Fragment'ы**

```kotlin
// Каждый Fragment может хостить дочерние Fragment'ы
class ParentFragment : Fragment(R.layout.fragment_parent) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // childFragmentManager -- для дочерних Fragment'ов
        // НЕ parentFragmentManager!
        childFragmentManager.beginTransaction()
            .replace(R.id.child_container, ChildFragment())
            .commit()
    }
}

// Иерархия FragmentManager'ов:
//
// Activity.supportFragmentManager
//   └── ParentFragment
//       └── ParentFragment.childFragmentManager
//           └── ChildFragment
//               └── ChildFragment.childFragmentManager
//                   └── GrandChildFragment
```

### КАК ПРИМЕНЯТЬ: на практике

```kotlin
// Добавление Fragment программно
supportFragmentManager.beginTransaction()
    .replace(R.id.fragment_container, UserListFragment::class.java, null)
    .setReorderingAllowed(true)  // Оптимизация: позволяет FM переупорядочить операции
    .addToBackStack("user_list") // Добавить в back stack с именем
    .commit()

// FragmentContainerView -- рекомендуемый контейнер (вместо FrameLayout)
// XML:
// <androidx.fragment.app.FragmentContainerView
//     android:id="@+id/fragment_container"
//     android:name="com.example.UserListFragment"
//     android:layout_width="match_parent"
//     android:layout_height="match_parent" />
```

### ПОДВОДНЫЕ КАМНИ

**1. setReorderingAllowed(true) -- всегда включайте:**

```kotlin
// ❌ Без setReorderingAllowed:
// Каждая операция выполняется строго по порядку
// Промежуточные состояния видны пользователю

// ✅ С setReorderingAllowed(true):
// FM может оптимизировать: если add(A) → replace(A, B),
// то A никогда не будет создан (оптимизация)
supportFragmentManager.beginTransaction()
    .setReorderingAllowed(true)  // ✅ ВСЕГДА включайте
    .replace(R.id.container, fragment)
    .addToBackStack(null)
    .commit()
```

**2. FragmentContainerView vs FrameLayout:**

```kotlin
// ❌ FrameLayout: устаревший подход
// - Не обрабатывает WindowInsets правильно
// - Не поддерживает Fragment transitions при Z-ordering
// - Не обрабатывает Fragment результаты из XML

// ✅ FragmentContainerView: правильный контейнер
// - Правильная обработка WindowInsets
// - Правильный Z-ordering для transitions
// - Поддержка android:name для начального Fragment
// - Поддержка android:tag
```

---

## 4. commit() варианты

### ЧТО: четыре способа выполнения транзакции

| Метод | Async/Sync | Back Stack | Потеря состояния | Когда использовать |
|-------|------------|------------|------------------|--------------------|
| `commit()` | Async | Да | Throws ISE | Стандартный случай |
| `commitAllowingStateLoss()` | Async | Да | Разрешает | Когда потеря состояния допустима |
| `commitNow()` | Sync | **Нет** | Throws ISE | Немедленное выполнение без back stack |
| `commitNowAllowingStateLoss()` | Sync | **Нет** | Разрешает | Немедленное + допустима потеря |

### ПОЧЕМУ: разные требования

**commit() -- async:**
- Транзакция планируется через `Handler.post()` на Main Thread
- Выполняется на следующем frame
- Позволяет batching нескольких транзакций
- Поддерживает back stack (потому что операции на back stack должны быть упорядочены)

**commitNow() -- sync:**
- Транзакция выполняется немедленно
- **НЕ поддерживает back stack** -- потому что синхронное выполнение нарушило бы порядок back stack записей
- Полезно когда нужен результат немедленно (например, DialogFragment)

### КАК РАБОТАЕТ: внутренний flow

**commit() -- асинхронный путь:**

```
commit()
  │
  ├── Проверка: isStateSaved? → YES → throw IllegalStateException
  │                            → NO  → продолжить
  │
  ├── BackStackRecord.commitInternal()
  │     └── mManager.enqueueAction(this, allowStateLoss=false)
  │
  ├── FragmentManager.enqueueAction()
  │     └── mPendingActions.add(action)
  │     └── scheduleCommit()
  │
  ├── scheduleCommit()
  │     └── mHost.getHandler().post(mExecCommit)  ← через Handler!
  │
  └── [следующий frame Main Thread]
        └── execPendingActions()
              └── generateOpsForPendingActions()
              └── removeRedundantOperationsAndExecute()
              └── executeOpsTogether()
              └── executeOps()
                    └── BackStackRecord.executeOps()
                          └── FM.addFragment() / removeFragment()
                                └── FragmentStore.addFragment()
                                └── FragmentStateManager.moveToExpectedState()
```

**commitNow() -- синхронный путь:**

```
commitNow()
  │
  ├── Проверка: isStateSaved? → YES → throw IllegalStateException
  │
  ├── Проверка: addToBackStack? → YES → throw IllegalStateException
  │     "This transaction is already being added to the back stack"
  │
  ├── FragmentManager.execSingleAction(this)
  │     └── [та же цепочка выполнения, но синхронно]
  │     └── executeOps()
  │           └── moveToExpectedState()
  │
  └── [выполнено немедленно]
```

### КАК ПРИМЕНЯТЬ: дерево решений

```
                    Нужен back stack?
                   /               \
                 ДА                 НЕТ
                 │                   │
        Потеря состояния       Потеря состояния
         допустима?              допустима?
        /          \            /          \
      ДА            НЕТ       ДА            НЕТ
       │             │         │             │
commitAllow-     commit()  commitNow-    commitNow()
ingStateLoss()             Allowing
                           StateLoss()
```

**Примеры использования:**

```kotlin
// ✅ commit() -- стандартный случай
// Навигация между экранами
fun navigateToDetail(userId: String) {
    supportFragmentManager.beginTransaction()
        .setReorderingAllowed(true)
        .replace(R.id.container, DetailFragment.newInstance(userId))
        .addToBackStack("detail")
        .commit()
}

// ✅ commitNow() -- немедленное выполнение (без back stack!)
// Показ DialogFragment
fun showDialog() {
    val dialog = ConfirmDialog()
    dialog.show(supportFragmentManager, "confirm")
    // show() использует commitNow() внутри (без back stack)
}

// Или когда нужен Fragment немедленно
fun addFragmentImmediately() {
    supportFragmentManager.beginTransaction()
        .setReorderingAllowed(true)
        .add(R.id.container, StatusFragment())
        // .addToBackStack(...) ← НЕЛЬЗЯ с commitNow()!
        .commitNow()
}

// ✅ commitAllowingStateLoss() -- когда потеря допустима
// Например, обновление UI-only Fragment после onSaveInstanceState
fun updateStatusAfterSave() {
    supportFragmentManager.beginTransaction()
        .setReorderingAllowed(true)
        .replace(R.id.status_container, StatusFragment())
        .commitAllowingStateLoss()
}
```

### ПОДВОДНЫЕ КАМНИ

**1. IllegalStateException: Can not perform this action after onSaveInstanceState:**

```kotlin
// ❌ ПРОБЛЕМА: commit() после onSaveInstanceState
class MyActivity : AppCompatActivity() {

    override fun onResume() {
        super.onResume()
        fetchDataFromServer { data ->
            // Этот callback может прийти ПОСЛЕ onSaveInstanceState!
            // Например: Activity уходит в background во время запроса
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, ResultFragment.newInstance(data))
                .commit() // CRASH: IllegalStateException!
        }
    }
}

// ✅ РЕШЕНИЕ 1: проверять lifecycle state
class MyActivity : AppCompatActivity() {

    override fun onResume() {
        super.onResume()
        fetchDataFromServer { data ->
            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                supportFragmentManager.beginTransaction()
                    .replace(R.id.container, ResultFragment.newInstance(data))
                    .commit()
            }
        }
    }
}

// ✅ РЕШЕНИЕ 2: использовать ViewModel + observe
class MyActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Observer автоматически lifecycle-aware
        viewModel.navigationEvent.observe(this) { event ->
            // Вызовется только когда Activity в правильном состоянии
            navigateToResult(event.data)
        }
    }
}
```

**2. commitNow() + addToBackStack() = crash:**

```kotlin
// ❌ CRASH: IllegalStateException
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    .addToBackStack("tag")
    .commitNow() // CRASH!

// Причина: синхронное выполнение нарушает порядок back stack
// Если другая async транзакция в очереди, back stack будет неконсистентен

// ✅ Используйте commit() с back stack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    .addToBackStack("tag")
    .commit() // OK
```

**3. Множественные commit() в одном frame:**

```kotlin
// ❌ НЕОПТИМАЛЬНО: два отдельных commit()
supportFragmentManager.beginTransaction()
    .add(R.id.container1, Fragment1())
    .commit()
supportFragmentManager.beginTransaction()
    .add(R.id.container2, Fragment2())
    .commit()

// ✅ ЛУЧШЕ: одна транзакция
supportFragmentManager.beginTransaction()
    .add(R.id.container1, Fragment1())
    .add(R.id.container2, Fragment2())
    .commit()

// Или используйте commitNow() для гарантированного порядка
```

---

## 5. Fragment Result API

### ЧТО: передача данных между Fragment'ами

Fragment Result API -- механизм для передачи данных между Fragment'ами через FragmentManager, заменяющий deprecated `setTargetFragment()`.

### ПОЧЕМУ: проблемы старого подхода

```kotlin
// ❌ DEPRECATED: setTargetFragment()
// Проблемы:
// 1. Не переживает process death -- ссылка на target теряется
// 2. Прямая связь между Fragment'ами -- нарушает modularity
// 3. requestCode конфликты
// 4. Target Fragment может быть уничтожен

class OldDialogFragment : DialogFragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        confirmButton.setOnClickListener {
            // Прямая ссылка на target Fragment
            (targetFragment as? ResultListener)?.onResult(data) // ❌
            dismiss()
        }
    }
}

// Использование:
val dialog = OldDialogFragment()
dialog.setTargetFragment(this, REQUEST_CODE) // ❌ DEPRECATED
dialog.show(parentFragmentManager, "dialog")
```

### КАК РАБОТАЕТ: через FragmentManager

```
┌─────────────────────────────────────────────────────────┐
│                    FragmentManager                        │
│                                                         │
│  Result Store:                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ "request_key" → Bundle(result data)              │   │
│  │ "dialog_key" → Bundle(confirmed = true)          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Listener Store:                                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ "request_key" → { requestKey, result -> ... }    │   │
│  │ "dialog_key" → { requestKey, result -> ... }     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Когда setFragmentResult("key", bundle):                │
│  1. Сохраняет bundle в Result Store                     │
│  2. Если есть listener для "key" И Fragment >= STARTED  │
│     → вызывает listener                                 │
│  3. Если нет listener -- результат ждёт                │
│                                                         │
│  Когда setFragmentResultListener("key", owner, cb):     │
│  1. Регистрирует listener в Listener Store              │
│  2. Привязывает к LifecycleOwner (авто-отписка)        │
│  3. Если результат уже есть → вызывает callback        │
└─────────────────────────────────────────────────────────┘
```

### КАК ПРИМЕНЯТЬ

**Между sibling Fragment'ами (один FragmentManager):**

```kotlin
// Fragment A -- ПОЛУЧАТЕЛЬ результата
class FragmentA : Fragment(R.layout.fragment_a) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Регистрация listener В onCreate() -- переживёт пересоздание
        setFragmentResultListener("request_key") { requestKey, bundle ->
            val result = bundle.getString("result_value")
            // Обработка результата
            Log.d("FragmentA", "Получен результат: $result")
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.openDialogButton.setOnClickListener {
            // Открываем Fragment B
            parentFragmentManager.beginTransaction()
                .replace(R.id.container, FragmentB())
                .addToBackStack(null)
                .commit()
        }
    }
}

// Fragment B -- ОТПРАВИТЕЛЬ результата
class FragmentB : Fragment(R.layout.fragment_b) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.confirmButton.setOnClickListener {
            // Отправляем результат
            setFragmentResult("request_key", bundleOf(
                "result_value" to "selected_item_42"
            ))
            // Возвращаемся назад
            parentFragmentManager.popBackStack()
        }
    }
}
```

**Между parent и child Fragment:**

```kotlin
// Parent Fragment -- ПОЛУЧАТЕЛЬ
class ParentFragment : Fragment(R.layout.fragment_parent) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Для child Fragment используем childFragmentManager!
        childFragmentManager.setFragmentResultListener(
            "child_result_key",
            this  // LifecycleOwner
        ) { requestKey, bundle ->
            val confirmed = bundle.getBoolean("confirmed")
            handleChildResult(confirmed)
        }
    }

    fun showChildDialog() {
        ConfirmDialogFragment().show(childFragmentManager, "dialog")
    }
}

// Child Dialog Fragment -- ОТПРАВИТЕЛЬ
class ConfirmDialogFragment : DialogFragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.confirmButton.setOnClickListener {
            // Отправляем через parentFragmentManager (который = parent's childFragmentManager)
            setFragmentResult("child_result_key", bundleOf(
                "confirmed" to true
            ))
            dismiss()
        }
    }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. Правильный FragmentManager:**

```kotlin
// ❌ НЕПРАВИЛЬНО: listener на parentFragmentManager для child result
parentFragmentManager.setFragmentResultListener(...) // НЕ получит от child

// ✅ ПРАВИЛЬНО: listener на childFragmentManager для child result
childFragmentManager.setFragmentResultListener(...)

// Правило:
// sibling → sibling: parentFragmentManager
// child → parent: parent.childFragmentManager
```

**2. Время регистрации listener:**

```kotlin
// ❌ ПРОБЛЕМА: регистрация в onViewCreated -- может потеряться при recreation
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    setFragmentResultListener("key") { _, bundle -> ... }
}

// ✅ ПРАВИЛЬНО: регистрация в onCreate -- переживёт recreation
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setFragmentResultListener("key") { _, bundle -> ... }
}
```

---

## 6. ViewModel Scoping с Fragment

### ЧТО: три уровня scope

ViewModel может быть привязан к разным scope, определяя время жизни и область видимости данных:

```
┌──────────────────────────────────────────────────────────────┐
│                        Activity Scope                        │
│  activityViewModels() → SharedViewModel                      │
│  Живёт пока жива Activity                                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               Navigation Graph Scope                     │ │
│  │  navGraphViewModels(R.id.nav_graph) → FlowViewModel     │ │
│  │  Живёт пока NavGraph в back stack                       │ │
│  │                                                         │ │
│  │  ┌──────────────┐    ┌──────────────┐                   │ │
│  │  │  Fragment A   │    │  Fragment B   │                   │ │
│  │  │              │    │              │                   │ │
│  │  │ viewModels() │    │ viewModels() │                   │ │
│  │  │ → ViewModelA │    │ → ViewModelB │                   │ │
│  │  │              │    │              │                   │ │
│  │  │ Fragment      │    │ Fragment      │                   │ │
│  │  │ Scope        │    │ Scope        │                   │ │
│  │  └──────────────┘    └──────────────┘                   │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### ПОЧЕМУ: разные потребности в sharing

| Scope | Область видимости | Время жизни | Когда использовать |
|-------|-------------------|-------------|-------------------|
| `viewModels()` | Один Fragment | Fragment lifecycle | Данные одного экрана |
| `activityViewModels()` | Все Fragment'ы в Activity | Activity lifecycle | Общие данные (user session, theme) |
| `navGraphViewModels(graphId)` | Fragment'ы в Navigation Graph | Пока graph в back stack | Данные flow (checkout, registration) |

### КАК РАБОТАЕТ

```kotlin
// Внутри Fragment (by viewModels()) -- упрощённо
inline fun <reified VM : ViewModel> Fragment.viewModels(
    noinline ownerProducer: () -> ViewModelStoreOwner = { this },
    noinline factoryProducer: (() -> ViewModelProvider.Factory)? = null
): Lazy<VM> {
    return ViewModelLazy(
        VM::class,
        storeProducer = { ownerProducer().viewModelStore },
        factoryProducer = factoryProducer ?: { defaultViewModelProviderFactory }
    )
}

// Fragment реализует ViewModelStoreOwner
class Fragment : ViewModelStoreOwner {
    // ViewModelStore создаётся при первом обращении
    // Переживает configuration changes!
    override val viewModelStore: ViewModelStore
        get() = /* сохраняется через FragmentManager */
}
```

### КАК ПРИМЕНЯТЬ

```kotlin
// ============================================
// Scope 1: viewModels() -- Fragment scope
// ============================================
class ProductDetailFragment : Fragment(R.layout.fragment_product_detail) {

    // ViewModel привязан к ЭТОМУ Fragment
    // Уничтожается когда Fragment уничтожен (не в back stack)
    private val viewModel: ProductDetailViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.product.observe(viewLifecycleOwner) { product ->
            binding.productName.text = product.name
        }
    }
}

// ============================================
// Scope 2: activityViewModels() -- Activity scope
// ============================================
class CartFragment : Fragment(R.layout.fragment_cart) {

    // ViewModel общий для всех Fragment'ов в Activity
    private val sharedViewModel: CartViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.cartItems.observe(viewLifecycleOwner) { items ->
            adapter.submitList(items)
        }
    }
}

class CartBadgeFragment : Fragment(R.layout.fragment_cart_badge) {

    // ТОТ ЖЕ ViewModel что и в CartFragment!
    private val sharedViewModel: CartViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.cartItemCount.observe(viewLifecycleOwner) { count ->
            binding.badge.text = count.toString()
        }
    }
}

// ============================================
// Scope 3: navGraphViewModels() -- Navigation Graph scope
// ============================================
// Навигационный граф checkout_graph содержит:
// CheckoutStep1Fragment → CheckoutStep2Fragment → CheckoutStep3Fragment

class CheckoutStep1Fragment : Fragment(R.layout.fragment_checkout_step1) {

    // ViewModel привязан к навигационному графу checkout_graph
    // Живёт пока любой Fragment из графа в back stack
    private val checkoutViewModel: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.nextButton.setOnClickListener {
            checkoutViewModel.setShippingAddress(binding.addressInput.text.toString())
            findNavController().navigate(R.id.action_step1_to_step2)
        }
    }
}

class CheckoutStep2Fragment : Fragment(R.layout.fragment_checkout_step2) {

    // ТОТ ЖЕ ViewModel -- данные из Step1 доступны
    private val checkoutViewModel: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Адрес из Step1 доступен!
        checkoutViewModel.shippingAddress.observe(viewLifecycleOwner) { address ->
            binding.addressPreview.text = address
        }
    }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. activityViewModels() живёт слишком долго:**

```kotlin
// ❌ ПРОБЛЕМА: ViewModel на уровне Activity для данных одного flow
// Данные checkout остаются в памяти даже после завершения checkout
class CheckoutFragment : Fragment() {
    private val vm: CheckoutViewModel by activityViewModels() // ❌
    // VM живёт пока жива Activity!
}

// ✅ РЕШЕНИЕ: navGraphViewModels для flow
class CheckoutFragment : Fragment() {
    private val vm: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph) // ✅
    // VM уничтожается когда выходим из checkout_graph
}
```

**2. navGraphViewModels требует Navigation dependency:**

```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.navigation:navigation-fragment-ktx:2.8.5")
}

// Без этой зависимости navGraphViewModels() не доступен
```

---

## 7. FragmentFactory

### ЧТО: фабрика для создания Fragment

FragmentFactory -- механизм создания экземпляров Fragment, позволяющий передавать зависимости через конструктор вместо пустого конструктора + Bundle.

### ПОЧЕМУ: проблема с default constructor

```kotlin
// ❌ ПРОБЛЕМА: Android пересоздаёт Fragment через рефлексию
// Требуется пустой конструктор
class UserFragment : Fragment() {

    // Как передать repository?
    // Через конструктор НЕЛЬЗЯ -- Android вызовет пустой конструктор при recreation!
    // constructor(val repository: UserRepository) ← CRASH при recreation

    companion object {
        fun newInstance(userId: String): UserFragment {
            return UserFragment().apply {
                arguments = bundleOf("userId" to userId)
            }
        }
    }
}

// При process death Android вызывает:
// Class.forName("com.example.UserFragment").newInstance()
// Если нет пустого конструктора → InstantiationException
```

### КАК РАБОТАЕТ

```kotlin
// FragmentFactory -- базовый класс
abstract class FragmentFactory {
    // Создание Fragment по имени класса
    open fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        // По умолчанию: рефлексия
        val clazz = loadFragmentClass(classLoader, className)
        return clazz.getConstructor().newInstance() // Вызов пустого конструктора
    }
}

// FragmentManager использует factory при:
// 1. Восстановлении из savedInstanceState
// 2. Навигации через Navigation Component
// 3. Программном создании через FragmentTransaction
```

### КАК ПРИМЕНЯТЬ: с Hilt

```kotlin
// Hilt автоматически настраивает FragmentFactory

// 1. Аннотируем Fragment
@AndroidEntryPoint
class UserFragment @Inject constructor(
    private val userRepository: UserRepository,
    private val analytics: Analytics
) : Fragment(R.layout.fragment_user) {

    // Зависимости инжектированы через конструктор!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // userRepository и analytics доступны
    }
}

// 2. Activity тоже должна быть @AndroidEntryPoint
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    // Hilt автоматически устанавливает HiltFragmentFactory
}
```

**Без Hilt -- ручная FragmentFactory:**

```kotlin
// Кастомная фабрика
class MyFragmentFactory(
    private val userRepository: UserRepository,
    private val analytics: Analytics
) : FragmentFactory() {

    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            UserFragment::class.java.name -> {
                UserFragment(userRepository, analytics)
            }
            SettingsFragment::class.java.name -> {
                SettingsFragment(analytics)
            }
            else -> {
                // Fallback на default (рефлексия)
                super.instantiate(classLoader, className)
            }
        }
    }
}

// Установка в Activity (ПЕРЕД super.onCreate!)
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // ВАЖНО: установить factory ПЕРЕД super.onCreate()
        // Потому что super.onCreate() может восстанавливать Fragment'ы!
        supportFragmentManager.fragmentFactory = MyFragmentFactory(
            userRepository = (application as MyApp).userRepository,
            analytics = (application as MyApp).analytics
        )

        super.onCreate(savedInstanceState) // Теперь Fragment recreation использует нашу factory
        setContentView(R.layout.activity_main)
    }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. Порядок установки factory:**

```kotlin
// ❌ CRASH: factory установлена после super.onCreate()
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState) // Fragment'ы восстановлены с DEFAULT factory!
    supportFragmentManager.fragmentFactory = myFactory // Слишком поздно!
}

// ✅ ПРАВИЛЬНО: factory перед super.onCreate()
override fun onCreate(savedInstanceState: Bundle?) {
    supportFragmentManager.fragmentFactory = myFactory // ДО super!
    super.onCreate(savedInstanceState) // Теперь использует нашу factory
}
```

**2. Testing с FragmentFactory:**

```kotlin
// В тестах используем FragmentScenario с factory
@Test
fun testUserFragment() {
    val factory = object : FragmentFactory() {
        override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
            return UserFragment(FakeUserRepository(), FakeAnalytics())
        }
    }

    launchFragmentInContainer<UserFragment>(factory = factory).onFragment { fragment ->
        // Проверки
        assertThat(fragment.view).isNotNull()
    }
}
```

---

## 8. Fragment + Compose

### ЧТО: интеграция Fragment с Jetpack Compose

Fragment можно использовать как хост для Compose UI через ComposeView. Это основной подход при постепенной миграции с View на Compose.

### ПОЧЕМУ: миграция и совместимость

```kotlin
// Типичная ситуация: часть экранов на View, часть на Compose
// Navigation Component использует Fragment'ы
// Новые экраны пишем на Compose внутри Fragment

// Будущее: Navigation Compose не требует Fragment,
// но миграция занимает время
```

### КАК РАБОТАЕТ

```kotlin
class ComposeFragment : Fragment() {

    private val viewModel: ComposeViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            // КРИТИЧЕСКИ ВАЖНО: правильная strategy
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
            )
            setContent {
                // Compose UI
                MyAppTheme {
                    val state by viewModel.uiState.collectAsStateWithLifecycle()
                    MyScreen(
                        state = state,
                        onAction = viewModel::onAction
                    )
                }
            }
        }
    }
}
```

### КАК ПРИМЕНЯТЬ: ViewCompositionStrategy

```kotlin
// Доступные стратегии:

// 1. DisposeOnDetachedFromWindow (по умолчанию)
//    Dispose когда View detached от window
//    ❌ ПРОБЛЕМА для Fragment: View может быть detached
//    во время transition анимации, но Fragment ещё жив

// 2. DisposeOnViewTreeLifecycleDestroyed ✅ РЕКОМЕНДУЕТСЯ для Fragment
//    Dispose когда ViewTreeLifecycleOwner (= viewLifecycleOwner) DESTROYED
//    Правильно работает с Fragment back stack и transitions

// 3. DisposeOnLifecycleDestroyed(lifecycle)
//    Dispose когда конкретный Lifecycle DESTROYED
//    Используется для кастомных случаев

// Пример: Fragment с ComposeView в XML layout
class MixedFragment : Fragment(R.layout.fragment_mixed) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val composeView = view.findViewById<ComposeView>(R.id.compose_view)
        composeView.apply {
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
            )
            setContent {
                // Compose часть экрана
                ComposeSection()
            }
        }
    }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. Неправильная strategy → утечка памяти или преждевременный dispose:**

```kotlin
// ❌ Без явной strategy: DisposeOnDetachedFromWindow
// Проблема: при Fragment transition View detached → Compose disposed
// Но анимация ещё идёт → глитчи

// ❌ DisposeOnLifecycleDestroyed(this.lifecycle)
// this = Fragment, НЕ viewLifecycleOwner
// Проблема: Compose живёт даже когда View уничтожен (back stack)

// ✅ DisposeOnViewTreeLifecycleDestroyed
// Автоматически привязан к viewLifecycleOwner
```

**2. collectAsStateWithLifecycle для корректного lifecycle:**

```kotlin
// ❌ НЕПРАВИЛЬНО: collectAsState не lifecycle-aware
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val state by viewModel.uiState.collectAsState() // ❌ Продолжит collect в background
}

// ✅ ПРАВИЛЬНО: collectAsStateWithLifecycle
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle() // ✅
    // Автоматически приостанавливает collect когда lifecycle < STARTED
}

// Зависимость:
// implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "Fragment deprecated, надо использовать только Compose" | Fragment активно поддерживается (1.8+). Jetpack Navigation построена на Fragment. Google рекомендует постепенную миграцию, а не "big rewrite" |
| 2 | "onDestroy() всегда вызывается после onDestroyView()" | При добавлении в back stack: onDestroyView() вызывается, onDestroy() НЕТ. Fragment жив, View уничтожен |
| 3 | "LiveData.observe(this, ...) в Fragment безопасно" | НЕТ! При возврате из back stack создаётся дублирующий observer. Используйте viewLifecycleOwner |
| 4 | "commit() выполняется немедленно" | commit() -- async через Handler. Выполнится на следующем frame. Для немедленного выполнения -- commitNow() |
| 5 | "commitNow() лучше commit() потому что быстрее" | commitNow() НЕ поддерживает back stack. Используйте его только когда back stack не нужен |
| 6 | "Fragment должен иметь пустой конструктор" | С FragmentFactory можно использовать конструктор с параметрами. Hilt делает это автоматически |
| 7 | "setTargetFragment() -- способ передачи данных" | Deprecated! Используйте Fragment Result API -- безопасен при process death |
| 8 | "viewModels() и activityViewModels() -- одно и то же" | viewModels() scoped к Fragment, activityViewModels() scoped к Activity. Разное время жизни и область видимости |
| 9 | "Fragment нельзя вкладывать друг в друга" | Можно! childFragmentManager позволяет вложенные Fragment'ы. Это основа ViewPager2, TabLayout и т.д. |
| 10 | "replace() удаляет Fragment" | replace() удаляет Fragment из контейнера. Но если addToBackStack(), Fragment остаётся в CREATED состоянии (View уничтожен) |

---

## CS-фундамент

| Концепция CS | Где проявляется в Fragment Lifecycle | Почему важно |
|-------------|-------------------------------------|-------------|
| **State Machine** (конечный автомат) | 5 состояний Fragment (INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED) с определёнными переходами | Fragment lifecycle -- классический конечный автомат. Состояние определяет, какие операции допустимы. moveToState() реализует переходы |
| **Stack (LIFO)** | BackStack FragmentManager'а -- стек транзакций. popBackStack() снимает верхнюю запись | Кнопка "Назад" = pop из стека. Понимание LIFO объясняет порядок восстановления Fragment'ов |
| **Observer Pattern** | LiveData/Flow наблюдение через viewLifecycleOwner. FragmentLifecycleCallbacks | Fragment'ы реагируют на изменения данных через Observer. LifecycleOwner автоматически управляет подпиской/отпиской |
| **Command Pattern** | BackStackRecord записывает операции (add, remove, replace) как команды. executeOps() выполняет, popOps() откатывает | FragmentTransaction -- набор команд, которые могут быть выполнены и отменены (back stack pop). Undo/Redo через записанные операции |
| **Decorator Pattern** | FragmentStateManager оборачивает Fragment, добавляя управление состоянием. SpecialEffectsController добавляет анимации | Разделение ответственности: Fragment -- бизнес-логика, FragmentStateManager -- lifecycle управление, SpecialEffectsController -- visual effects |
| **Composite Pattern** | FragmentManager содержит Fragment'ы, каждый из которых может содержать childFragmentManager с вложенными Fragment'ами | Дерево Fragment'ов: Activity → ParentFragment → ChildFragment. Lifecycle каскадно распространяется вниз |
| **Factory Pattern** | FragmentFactory создаёт экземпляры Fragment. Можно подменить для DI или тестирования | Абстрагирование создания объектов. Позволяет менять способ создания без изменения клиентского кода |
| **Mediator Pattern** | FragmentManager -- медиатор между Fragment'ами. Fragment Result API передаёт данные через FM, а не напрямую | Fragment'ы не знают друг о друге. FM координирует взаимодействие. Снижает связность (coupling) |
| **Template Method** | Fragment.onCreateView(), onViewCreated() и т.д. -- шаблонные методы, вызываемые framework в определённом порядке | Разработчик переопределяет конкретные шаги, framework определяет порядок вызовов. Инверсия контроля |
| **Memento Pattern** | savedInstanceState Bundle сохраняет состояние Fragment. onSaveInstanceState() → Bundle → onCreate(savedState) | Сохранение и восстановление состояния без нарушения инкапсуляции. Fragment не знает, кто и как хранит его состояние |

---

## Проверь себя

### Вопрос 1: Почему нельзя использовать `this` вместо `viewLifecycleOwner` при наблюдении LiveData в Fragment?

<details>
<summary>Ответ</summary>

Когда Fragment помещается в back stack:
1. `onDestroyView()` вызывается -- View уничтожен
2. `onDestroy()` НЕ вызывается -- Fragment жив в состоянии CREATED
3. Observer, привязанный к `this` (Fragment lifecycle), НЕ отписывается, потому что Fragment lifecycle ещё не DESTROYED
4. При возврате из back stack вызывается новый `onCreateView()` → `onViewCreated()`
5. В `onViewCreated()` регистрируется НОВЫЙ observer
6. Теперь ДВА observer'а активны одновременно -- дублирование обработки

С `viewLifecycleOwner`:
- viewLifecycleOwner переходит в DESTROYED при `onDestroyView()`
- Observer автоматически отписывается
- При возврате создаётся НОВЫЙ viewLifecycleOwner
- Только один активный observer

```kotlin
// ❌ this → дублирование при back stack
viewModel.data.observe(this) { ... }

// ✅ viewLifecycleOwner → один observer
viewModel.data.observe(viewLifecycleOwner) { ... }
```

</details>

### Вопрос 2: Почему commitNow() не поддерживает addToBackStack()?

<details>
<summary>Ответ</summary>

`commitNow()` выполняет транзакцию **синхронно**, а `commit()` -- **асинхронно** через Handler.

Проблема: если несколько транзакций запланированы через `commit()` (ожидают в очереди Handler'а), и между ними вызывается `commitNow()` с `addToBackStack()`, порядок записей в back stack будет нарушен.

Пример:

```
commit() с addToBackStack("A")    → запланирован на следующий frame
commitNow() с addToBackStack("B") → выполняется СЕЙЧАС
commit() с addToBackStack("C")    → запланирован на следующий frame

Ожидаемый порядок back stack: A → B → C
Реальный порядок: B → A → C (B выполнен раньше!)
```

Чтобы гарантировать консистентность back stack, `commitNow()` с `addToBackStack()` запрещён. Если вам нужен back stack -- используйте `commit()`.

</details>

### Вопрос 3: Что произойдёт если вызвать requireContext() в onDetach()?

<details>
<summary>Ответ</summary>

`requireContext()` бросит `IllegalStateException`:

```kotlin
override fun onDetach() {
    super.onDetach()
    // После super.onDetach() Fragment отсоединён от Activity
    // mHost = null
    val ctx = requireContext() // IllegalStateException:
    // "Fragment UserFragment not attached to a context."
}
```

Внутри `requireContext()`:

```kotlin
fun requireContext(): Context {
    return context ?: throw IllegalStateException(
        "Fragment $this not attached to a context."
    )
}

// context вычисляется как:
val context: Context?
    get() = mHost?.context // mHost = null после detach!
```

**Решение:** если нужен Context в onDetach(), сохраните его раньше или используйте `context` (nullable) вместо `requireContext()`.

```kotlin
override fun onAttach(context: Context) {
    super.onAttach(context)
    // Сохраняем applicationContext (он живёт вечно)
    appContext = context.applicationContext
}
```

</details>

### Вопрос 4: Как Fragment переживает configuration change (поворот экрана)?

<details>
<summary>Ответ</summary>

При configuration change:

1. **Activity уничтожается** -- `onDestroy()` вызывается
2. **FragmentManager сохраняет состояние** -- `onSaveInstanceState()` для каждого Fragment
3. **Новая Activity создаётся** -- `onCreate(savedInstanceState)` с non-null Bundle
4. **FragmentManager восстанавливает Fragment'ы** -- через FragmentFactory (рефлексия)
5. **Fragment'ы пересоздаются** -- с сохранённым `savedInstanceState`

```
Поворот экрана:

Activity#1 → onSaveInstanceState() → Activity#1.onDestroy()
  Fragment#1 → onSaveInstanceState() → полный lifecycle down

Activity#2 → onCreate(savedInstanceState)
  FragmentManager восстанавливает:
    Fragment#2 = FragmentFactory.instantiate("com.example.MyFragment")
    Fragment#2.onCreate(savedInstanceState) ← данные из Fragment#1
```

**ViewModel переживает configuration change** -- он привязан к ViewModelStore, который сохраняется в `NonConfigurationInstances`. Поэтому данные из ViewModel доступны после поворота без пересоздания.

**Важно:** `arguments` Bundle автоматически сохраняется и восстанавливается. Но конструкторные параметры -- нет! Поэтому нужен пустой конструктор (или FragmentFactory).

</details>

### Вопрос 5: В чём разница между replace() и add() в FragmentTransaction?

<details>
<summary>Ответ</summary>

```kotlin
// add() -- ДОБАВЛЯЕТ Fragment в контейнер
// Существующие Fragment'ы остаются!
fragmentManager.beginTransaction()
    .add(R.id.container, FragmentB())
    .addToBackStack(null)
    .commit()

// Контейнер: [FragmentA, FragmentB] -- ОБА видны!
// FragmentA НЕ уничтожен, НЕ в onDestroyView()

// replace() -- ЗАМЕНЯЕТ все Fragment'ы в контейнере
// Существующие Fragment'ы удаляются!
fragmentManager.beginTransaction()
    .replace(R.id.container, FragmentB())
    .addToBackStack(null)
    .commit()

// Контейнер: [FragmentB] -- только B
// FragmentA: onDestroyView() вызван (View уничтожен)
// FragmentA: в back stack (CREATED state, жив)
```

**replace() = remove(all_in_container) + add(new)**

Это влияет на:
- **Память**: add() держит View обоих Fragment в памяти
- **Lifecycle**: при replace() у старого Fragment вызывается onDestroyView()
- **Back button**: при popBackStack() после replace() -- старый Fragment воссоздаёт View (onCreateView()); после add() -- новый Fragment удаляется, старый уже с View

**Рекомендация:**
- `replace()` -- для навигации между экранами (один экран за раз)
- `add()` -- для overlay UI (bottom sheets, dialogs поверх контента)

</details>

### Вопрос 6: Когда использовать navGraphViewModels() вместо activityViewModels()?

<details>
<summary>Ответ</summary>

`activityViewModels()` привязывает ViewModel к Activity -- она живёт пока жива Activity. Это означает, что данные checkout flow остаются в памяти даже после завершения checkout.

`navGraphViewModels(graphId)` привязывает ViewModel к Navigation Graph -- она живёт пока хотя бы один destination из этого графа в back stack.

```kotlin
// Навигационный граф:
// main_graph
//   ├── home (start)
//   ├── product_list
//   ├── product_detail
//   └── checkout_graph (nested)
//       ├── cart
//       ├── shipping
//       ├── payment
//       └── confirmation

// С activityViewModels():
// CheckoutViewModel живёт пока жива Activity
// Даже после завершения checkout и возврата на home
// Память не освобождается!

// С navGraphViewModels(R.id.checkout_graph):
// CheckoutViewModel живёт пока мы внутри checkout_graph
// При возврате на product_detail (вне checkout_graph)
// → ViewModel очищается → onCleared() → память освобождена

class CartFragment : Fragment() {
    // ✅ Правильный scope для checkout flow
    private val vm: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)
}
```

**Правило:** используйте минимальный scope, достаточный для ваших данных.

</details>

---

## Связи

### Lifecycle и состояния

**[[android-activity-lifecycle]]** -- Fragment lifecycle вложен в Activity lifecycle. Максимальное состояние Fragment не может превышать состояние хост-Activity. Если Activity в STOPPED, Fragment не может быть RESUMED. Понимание Activity lifecycle -- предпосылка для понимания Fragment lifecycle.

**[[android-state-management]]** -- savedInstanceState в Fragment работает аналогично Activity, но с дополнительной сложностью View lifecycle. onSaveInstanceState() в Fragment вызывается отдельно от Activity. FragmentManager управляет сохранением и восстановлением состояния всех Fragment'ов.

### Навигация

**[[android-navigation]]** -- Jetpack Navigation Component построен поверх Fragment'ов. NavHostFragment -- специальный Fragment, который управляет навигацией. NavController выполняет FragmentTransaction'ы под капотом. Понимание Fragment lifecycle необходимо для правильной работы с Navigation.

**[[android-navigation-evolution]]** -- эволюция подходов к навигации: от ручных FragmentTransaction к Navigation Component и Navigation Compose. Fragment остаётся промежуточным слоем даже в Navigation Compose (через NavHostFragment).

### Архитектура

**[[android-viewmodel-internals]]** -- ViewModel scoping зависит от ViewModelStoreOwner. Fragment реализует ViewModelStoreOwner. viewModels() использует Fragment как owner, activityViewModels() -- Activity, navGraphViewModels() -- NavBackStackEntry. Понимание ViewModel lifecycle критично для правильного scoping.

**[[android-context-internals]]** -- Fragment получает Context через onAttach(). requireContext() зависит от attach-состояния Fragment. После onDetach() Context недоступен. getContext() возвращает null после detach.

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Android Developers: Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle) | Документация | Официальное описание состояний и callbacks |
| 2 | [Fragments: Rebuilding the Internals (Ian Lake)](https://medium.com/androiddevelopers/fragments-rebuilding-the-internals-61913f8bf48e) | Статья | Архитектура FragmentStateManager и SpecialEffectsController |
| 3 | [Android Developers: FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager) | Документация | Операции с Fragment, back stack, transactions |
| 4 | [Android Developers: Communicate with fragments](https://developer.android.com/guide/fragments/communicate) | Документация | Fragment Result API, ViewModel sharing |
| 5 | [Android Developers: ViewModel APIs](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-apis) | Документация | viewModels(), activityViewModels(), navGraphViewModels() |
| 6 | [The Many Flavors of commit() (Bryan Herbst)](https://medium.com/@bherbst/the-many-flavors-of-commit-186608a015b1) | Статья | Детальное сравнение commit/commitNow/commitAllowingStateLoss |
| 7 | [Fragment Transaction Commit State Loss (Alex Lockwood)](https://www.androiddesignpatterns.com/2013/08/fragment-transaction-commit-state-loss.html) | Статья | Глубокий анализ IllegalStateException при commit после state save |
| 8 | [Demystifying commitAllowingStateLoss (InLoopx)](https://medium.com/inloopx/demystifying-androids-commitallowingstateloss-cb9011a544cc) | Статья | Когда допустимо использовать commitAllowingStateLoss |
| 9 | [Mastering Fragment Lifecycle & View Lifecycle](https://medium.com/@javainiyan/mastering-fragment-lifecycle-view-lifecycle-in-android-cd0359a2bec0) | Статья | Различие Fragment lifecycle и View lifecycle с диаграммами |
| 10 | [AOSP: FragmentStateManager.java](https://cs.android.com/androidx/platform/frameworks/support/+/androidx-main:fragment/fragment/src/main/java/androidx/fragment/app/FragmentStateManager.java) | Исходный код | Внутренняя реализация lifecycle переходов |
| 11 | [AOSP: FragmentManager.java](https://cs.android.com/androidx/platform/frameworks/support/+/androidx-main:fragment/fragment/src/main/java/androidx/fragment/app/FragmentManager.java) | Исходный код | Центральный координатор Fragment'ов |
| 12 | [AOSP: BackStackRecord.java](https://cs.android.com/androidx/platform/frameworks/support/+/androidx-main:fragment/fragment/src/main/java/androidx/fragment/app/BackStackRecord.java) | Исходный код | Реализация FragmentTransaction и back stack записи |
| 13 | [Android Developers: Fragment Testing](https://developer.android.com/guide/fragments/test) | Документация | FragmentScenario, testing с FragmentFactory |
| 14 | [Android Developers: Interoperability APIs (Compose in Fragment)](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis) | Документация | ComposeView в Fragment, ViewCompositionStrategy |
| 15 | [Android Developers: ViewCompositionStrategy](https://developer.android.com/reference/kotlin/androidx/compose/ui/platform/ViewCompositionStrategy) | Документация | Стратегии dispose для ComposeView в Fragment |
| 16 | [Chet Haase, Romain Guy: ADS 2022 - Fragments: Past, Present, and Future](https://www.youtube.com/watch?v=OE-tDh3d1F4) | Видео | Эволюция Fragment API, планы на будущее |

---

*Проверено: 2026-01-27 -- Педагогический контент проверен*
