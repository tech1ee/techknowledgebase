---
title: "Android ViewModel Internals"
created: 2025-01-15
modified: 2026-01-05
tags:
  - android
  - viewmodel
  - lifecycle
  - savedstate
  - architecture
related:
  - "[[android-architecture-evolution]]"
  - "[[android-architecture-patterns]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-state-management]]"
  - "[[android-modularization]]"
  - "[[android-bundle-parcelable]]"
cs-foundations: [state-machine, separation-of-concerns, object-retention, serialization]
---

# Android ViewModel Internals: Как ViewModel переживает Configuration Change

> Глубокое погружение во внутреннее устройство ViewModel: ViewModelStore, NonConfigurationInstance, SavedStateHandle

---

## Зачем это нужно

**Для разработчика:** Понимание internals ViewModel критично для:
- **Диагностики багов** — почему данные потерялись после поворота? почему ViewModel не пережил background?
- **Правильного выбора scope** — Activity vs Fragment vs Navigation Graph
- **Предотвращения утечек памяти** — почему нельзя хранить Context?
- **Тестирования** — как мокать SavedStateHandle?

**Типичные проблемы без понимания internals:**
- Memory leaks при хранении Activity/View в ViewModel
- Потеря данных после process death (не использовали SavedStateHandle)
- "God ViewModel" — один огромный ViewModel на всё приложение
- Неправильный scope — данные shared ViewModel очищаются раньше времени

**Ключевой инсайт:** ViewModel переживает Configuration Change благодаря `NonConfigurationInstance` — специальному механизму Android, который сохраняет объекты между уничтожением и созданием Activity.

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **ViewModel** | Класс для хранения UI-related данных, переживает configuration changes |
| **ViewModelStore** | Хранилище ViewModels для конкретного scope (Activity/Fragment) |
| **ViewModelStoreOwner** | Интерфейс для объектов владеющих ViewModelStore |
| **ViewModelProvider** | Фабрика для создания и получения ViewModels |
| **SavedStateHandle** | Механизм сохранения state при process death |
| **Configuration Change** | Поворот экрана, смена языка, resize окна |
| **Process Death** | Система убивает процесс для освобождения памяти |
| **onCleared()** | Callback вызываемый при уничтожении ViewModel |

---

## Проблема, которую решает ViewModel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION CHANGE PROBLEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Поворот экрана (или другой config change):                                │
│                                                                             │
│  ┌─────────────────┐          ┌─────────────────┐                          │
│  │    Activity     │          │    Activity     │                          │
│  │    (Portrait)   │  rotate  │   (Landscape)   │                          │
│  │                 │ ───────▶ │                 │                          │
│  │  users = [...]  │  DESTROY │  users = []     │ ← Данные потеряны!       │
│  │  isLoading=false│   +      │  isLoading=true │ ← Снова загружаем       │
│  └─────────────────┘  CREATE  └─────────────────┘                          │
│                                                                             │
│  Без ViewModel:                                                             │
│  • Activity уничтожается                                                   │
│  • Все поля (users, isLoading) теряются                                    │
│  • Новая Activity создаётся                                                │
│  • Данные загружаются заново (сетевой запрос)                             │
│  • Пользователь видит loading снова                                        │
│                                                                             │
│  С ViewModel:                                                               │
│  ┌─────────────────┐          ┌─────────────────┐                          │
│  │    Activity     │          │    Activity     │                          │
│  │    (Portrait)   │  rotate  │   (Landscape)   │                          │
│  │        │        │ ───────▶ │        │        │                          │
│  │        │        │          │        │        │                          │
│  │        ▼        │          │        ▼        │                          │
│  │  ┌───────────┐  │          │  ┌───────────┐  │                          │
│  │  │ ViewModel │──┼──────────┼──│ ViewModel │  │ ← Тот же instance!      │
│  │  │users=[...]│  │  SURVIVE │  │users=[...]│  │ ← Данные сохранены      │
│  │  └───────────┘  │          │  └───────────┘  │                          │
│  └─────────────────┘          └─────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Как ViewModel переживает Configuration Change

### ViewModelStore и ViewModelStoreOwner

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VIEWMODELSTORE ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ComponentActivity implements ViewModelStoreOwner                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  class ComponentActivity : ... , ViewModelStoreOwner {              │   │
│  │                                                                     │   │
│  │      private var viewModelStore: ViewModelStore? = null             │   │
│  │                                                                     │   │
│  │      override fun getViewModelStore(): ViewModelStore {             │   │
│  │          // Получить из NonConfigurationInstance                    │   │
│  │          // или создать новый                                       │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ViewModelStore                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  class ViewModelStore {                                             │   │
│  │      private val map = HashMap<String, ViewModel>()                 │   │
│  │                                                                     │   │
│  │      fun put(key: String, viewModel: ViewModel)                     │   │
│  │      fun get(key: String): ViewModel?                               │   │
│  │      fun clear() { /* вызывает onCleared() для всех */ }           │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  // Ключ = полное имя класса ViewModel                             │   │
│  │  // "com.example.UsersViewModel"                                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### NonConfigurationInstance: секрет выживания

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NONCONFIGURATIONINSTANCE MECHANISM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Activity Lifecycle при Configuration Change:                              │
│                                                                             │
│  1. Activity 1 получает onDestroy(isChangingConfiguration = true)          │
│                                                                             │
│  2. Перед destroy:                                                          │
│     onRetainNonConfigurationInstance() вызывается                          │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │  // ComponentActivity.java                                      │    │
│     │  public final Object onRetainNonConfigurationInstance() {       │    │
│     │      NonConfigurationInstances nci = new NonConfigurationInstances();│
│     │      nci.viewModelStore = mViewModelStore; // ← Сохраняем!     │    │
│     │      return nci;                                                │    │
│     │  }                                                              │    │
│     └─────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  3. Activity 1 уничтожается                                                │
│                                                                             │
│  4. Activity 2 создаётся                                                   │
│                                                                             │
│  5. При создании Activity 2:                                               │
│     getLastNonConfigurationInstance() возвращает сохранённый объект        │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │  // ComponentActivity.java                                      │    │
│     │  public ViewModelStore getViewModelStore() {                    │    │
│     │      NonConfigurationInstances nc =                             │    │
│     │          (NonConfigurationInstances) getLastNonConfigurationInstance();│
│     │      if (nc != null && nc.viewModelStore != null) {            │    │
│     │          mViewModelStore = nc.viewModelStore; // ← Восстанавливаем!│  │
│     │      }                                                          │    │
│     │      return mViewModelStore;                                    │    │
│     │  }                                                              │    │
│     └─────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Результат: ViewModelStore (и все ViewModels) переживают rotation         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Визуализация жизненного цикла

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  VIEWMODEL LIFECYCLE vs ACTIVITY LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Activity 1          Config Change         Activity 2                      │
│  ────────────        ────────────          ────────────                    │
│                                                                             │
│  onCreate() ─────────────────────────────▶ onCreate()                      │
│      │                                         │                           │
│      │  ViewModel created                      │  Same ViewModel           │
│      │  ┌───────────────────────────────────────────────────────┐         │
│      │  │                    ViewModel                          │         │
│      │  │                  (Single Instance)                    │         │
│      │  └───────────────────────────────────────────────────────┘         │
│      │                                         │                           │
│  onStart() ──────────────────────────────▶ onStart()                       │
│      │                                         │                           │
│  onResume() ─────────────────────────────▶ onResume()                      │
│      │                                         │                           │
│  onPause() ──────────────────────────────▶ onPause()                       │
│      │                                         │                           │
│  onStop()                                  onStop()                        │
│      │                                         │                           │
│  onDestroy() ◀────── rotation ──────────▶ [Activity finished]             │
│      │                                         │                           │
│      X (Activity destroyed)                    │                           │
│                                                │                           │
│                                           onDestroy()                      │
│                                                │                           │
│                                           ViewModel.onCleared() ◀──────── │
│                                                                             │
│  ViewModel живёт от первого onCreate() до последнего onDestroy()          │
│  (когда Activity ФИНАЛЬНО уничтожается, не configuration change)          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ViewModelProvider: создание ViewModels

### Базовое использование

```kotlin
// Через делегат (рекомендуется)
class UsersActivity : ComponentActivity() {
    private val viewModel: UsersViewModel by viewModels()
}

// Через ViewModelProvider напрямую
class UsersActivity : ComponentActivity() {
    private lateinit var viewModel: UsersViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel = ViewModelProvider(this)[UsersViewModel::class.java]
        // или
        viewModel = ViewModelProvider(this).get(UsersViewModel::class.java)
    }
}

// Compose
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = viewModel()
) {
    // ...
}
```

### Как работает ViewModelProvider

```kotlin
// Упрощённая реализация
class ViewModelProvider(
    private val store: ViewModelStore,
    private val factory: Factory
) {
    operator fun <T : ViewModel> get(modelClass: Class<T>): T {
        // Ключ = полное имя класса
        val key = "androidx.lifecycle.ViewModelProvider.DefaultKey:" +
                  modelClass.canonicalName

        // Попробовать получить существующий
        var viewModel = store.get(key)

        // Если есть и правильный тип — вернуть
        if (modelClass.isInstance(viewModel)) {
            @Suppress("UNCHECKED_CAST")
            return viewModel as T
        }

        // Создать новый через фабрику
        viewModel = factory.create(modelClass)

        // Сохранить в store
        store.put(key, viewModel)

        @Suppress("UNCHECKED_CAST")
        return viewModel as T
    }
}
```

### ViewModelProvider.Factory

```kotlin
// Для ViewModel без параметров — не нужна фабрика
class SimpleViewModel : ViewModel()

// Для ViewModel с параметрами — нужна фабрика
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel()

// Способ 1: Ручная фабрика
class UsersViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UsersViewModel::class.java)) {
            return UsersViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Использование
val factory = UsersViewModelFactory(UserRepositoryImpl())
val viewModel = ViewModelProvider(this, factory)[UsersViewModel::class.java]

// Способ 2: viewModelFactory DSL (AndroidX)
val viewModel: UsersViewModel by viewModels {
    viewModelFactory {
        initializer {
            UsersViewModel(UserRepositoryImpl())
        }
    }
}

// Способ 3: Hilt (рекомендуется)
@HiltViewModel
class UsersViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()

// В Activity
@AndroidEntryPoint
class UsersActivity : ComponentActivity() {
    private val viewModel: UsersViewModel by viewModels()
}
```

---

## SavedStateHandle: выживание после Process Death

### Проблема Process Death

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROCESS DEATH PROBLEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ViewModel переживает Configuration Change, но НЕ переживает Process Death │
│                                                                             │
│  Сценарий:                                                                  │
│  1. User открывает приложение, загружает данные в ViewModel                │
│  2. User сворачивает приложение (Home)                                     │
│  3. User открывает тяжёлое приложение (игра)                              │
│  4. Android убивает ваш процесс (Low Memory Killer)                        │
│  5. User возвращается в ваше приложение                                    │
│  6. Process восстанавливается, но ViewModel создаётся ЗАНОВО              │
│  7. Все данные потеряны! users = [], isLoading = true                     │
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │   Active    │──▶│ Background  │──▶│Process Kill │──▶│  Restored   │    │
│  │   (VM=ok)   │   │   (VM=ok)   │   │  (VM=null)  │   │ (VM=new!)   │    │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘    │
│                                                                             │
│  Решение: SavedStateHandle                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SavedStateHandle использование

```kotlin
// SavedStateHandle сохраняет данные в Bundle
// Bundle восстанавливается после process death

class UsersViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: UserRepository
) : ViewModel() {

    // Автоматическое сохранение/восстановление
    private val searchQuery = savedStateHandle.getStateFlow("searchQuery", "")

    // Или через делегат
    var selectedUserId by savedStateHandle.saveable { mutableStateOf<Long?>(null) }

    // Сложные объекты — через Parcelable
    var selectedUser: User?
        get() = savedStateHandle["selectedUser"]
        set(value) { savedStateHandle["selectedUser"] = value }

    // Для LiveData
    val searchQueryLiveData: MutableLiveData<String> =
        savedStateHandle.getLiveData("searchQuery", "")

    fun onSearchChanged(query: String) {
        savedStateHandle["searchQuery"] = query
        // Автоматически сохраняется в Bundle
    }
}

// С Hilt — SavedStateHandle инжектируется автоматически
@HiltViewModel
class UsersViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val repository: UserRepository
) : ViewModel()
```

### Что можно сохранять в SavedStateHandle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAVEDSTATEHANDLE DATA TYPES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ Можно сохранять (всё что может быть в Bundle):                         │
│  • Primitive types: Int, Long, Float, Double, Boolean, Char, Byte, Short   │
│  • String, CharSequence                                                    │
│  • Parcelable и Parcelable[]                                               │
│  • Serializable (НЕ рекомендуется — медленнее)                            │
│  • ArrayList<> примитивов и Parcelable                                     │
│  • Bundle, SparseArray<Parcelable>                                         │
│                                                                             │
│  ❌ НЕЛЬЗЯ сохранять:                                                       │
│  • Большие объекты (> 1MB на весь Bundle)                                  │
│  • Bitmap (используйте URI)                                                │
│  • Context, View, Activity                                                 │
│  • Не-Parcelable классы                                                    │
│  • Closeable ресурсы (streams, connections)                               │
│                                                                             │
│  Лимит размера Bundle: ~1MB (TransactionTooLargeException)                 │
│                                                                             │
│  Что сохранять:                                                             │
│  • Текущий ID (userId, postId)                                             │
│  • Поисковый запрос                                                        │
│  • Позиция скролла                                                         │
│  • Выбранные фильтры                                                       │
│  • Navigation arguments                                                    │
│                                                                             │
│  Что НЕ сохранять:                                                          │
│  • Списки данных (загружайте из Repository/DB)                            │
│  • Большие изображения                                                     │
│  • Временное UI state (loading indicator)                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SavedStateHandle vs onSaveInstanceState

```kotlin
// Activity с ViewModel и SavedStateHandle
class UsersActivity : ComponentActivity() {

    private val viewModel: UsersViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // savedInstanceState — для Activity-specific state
        // (scroll position в View, keyboard state)

        // SavedStateHandle в ViewModel — для business state
        // (selected user ID, search query)
    }

    // Используется редко при наличии SavedStateHandle
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохраняем View state (RecyclerView scroll position)
        outState.putInt("scrollPosition", recyclerView.computeVerticalScrollOffset())
    }
}
```

---

## ViewModel Scopes: Activity vs Fragment vs Navigation

### Разные scopes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VIEWMODEL SCOPES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Activity Scope                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MainActivity                                                       │   │
│  │  ├── MainViewModel (scope = MainActivity)                           │   │
│  │  │                                                                  │   │
│  │  ├── FragmentA                                                      │   │
│  │  │   └── FragmentAViewModel (scope = FragmentA)                    │   │
│  │  │                                                                  │   │
│  │  └── FragmentB                                                      │   │
│  │      └── FragmentBViewModel (scope = FragmentB)                    │   │
│  │                                                                     │   │
│  │  MainViewModel живёт пока жива MainActivity                        │   │
│  │  FragmentAViewModel живёт пока жив FragmentA                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Shared ViewModel (Activity scope для Fragments)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // Fragment получает ViewModel из Activity scope                  │   │
│  │  class FragmentA : Fragment() {                                     │   │
│  │      // ViewModel привязан к Activity                              │   │
│  │      private val sharedViewModel: SharedViewModel by activityViewModels()│
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  class FragmentB : Fragment() {                                     │   │
│  │      // Тот же instance SharedViewModel                            │   │
│  │      private val sharedViewModel: SharedViewModel by activityViewModels()│
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  Используется для: communication между Fragments                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Navigation Graph Scope                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // ViewModel привязан к Navigation Graph                          │   │
│  │  @Composable                                                        │   │
│  │  fun UsersScreen(                                                   │   │
│  │      navController: NavController,                                  │   │
│  │      viewModel: UsersFlowViewModel = hiltViewModel(                 │   │
│  │          viewModelStoreOwner = navController.getBackStackEntry("users_flow")│
│  │      )                                                              │   │
│  │  )                                                                  │   │
│  │                                                                     │   │
│  │  Используется для: ViewModel на несколько экранов (wizard, flow)  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Примеры использования разных scopes

```kotlin
// Fragment с собственным ViewModel
class UsersListFragment : Fragment() {
    // ViewModel привязан к этому Fragment
    private val viewModel: UsersListViewModel by viewModels()
}

// Fragment с shared ViewModel
class UserDetailFragment : Fragment() {
    // ViewModel привязан к parent Activity
    private val sharedViewModel: UsersSharedViewModel by activityViewModels()

    // ViewModel привязан к parent Fragment
    private val parentViewModel: ParentViewModel by viewModels(
        ownerProducer = { requireParentFragment() }
    )
}

// Compose с Navigation Graph scope
@Composable
fun UserFlowScreen(navController: NavHostController) {
    val backStackEntry = remember(navController.currentBackStackEntry) {
        navController.getBackStackEntry("user_flow_graph")
    }

    val flowViewModel: UserFlowViewModel = hiltViewModel(backStackEntry)

    NavHost(navController, startDestination = "step1") {
        composable("step1") {
            Step1Screen(
                viewModel = flowViewModel,
                onNext = { navController.navigate("step2") }
            )
        }
        composable("step2") {
            Step2Screen(
                viewModel = flowViewModel, // Тот же instance!
                onNext = { navController.navigate("step3") }
            )
        }
    }
}
```

---

## ViewModel Anti-patterns и Best Practices

### Anti-patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VIEWMODEL ANTI-PATTERNS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ 1. Хранение Context в ViewModel                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class BadViewModel(                                                │   │
│  │      private val context: Context  // ❌ Memory leak!              │   │
│  │  ) : ViewModel()                                                    │   │
│  │                                                                     │   │
│  │  Проблема: ViewModel живёт дольше Activity → утечка памяти         │   │
│  │                                                                     │   │
│  │  Решение: AndroidViewModel или Hilt                                │   │
│  │  class GoodViewModel(                                               │   │
│  │      private val application: Application  // ✅ OK                │   │
│  │  ) : AndroidViewModel(application)                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 2. Хранение View/Fragment/Activity reference                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class BadViewModel : ViewModel() {                                 │   │
│  │      var fragment: Fragment? = null  // ❌ Memory leak!            │   │
│  │      var recyclerView: RecyclerView? = null  // ❌ Memory leak!    │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  Решение: ViewModel не должен знать о View                         │   │
│  │  Используйте StateFlow/LiveData для коммуникации                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 3. Бизнес-логика без coroutine scope                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class BadViewModel : ViewModel() {                                 │   │
│  │      fun loadData() {                                               │   │
│  │          GlobalScope.launch {  // ❌ Не отменяется при onCleared  │   │
│  │              // ...                                                 │   │
│  │          }                                                          │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  Решение: viewModelScope                                           │   │
│  │  class GoodViewModel : ViewModel() {                                │   │
│  │      fun loadData() {                                               │   │
│  │          viewModelScope.launch {  // ✅ Отменяется при onCleared  │   │
│  │              // ...                                                 │   │
│  │          }                                                          │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 4. Слишком большой ViewModel (God ViewModel)                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class GodViewModel : ViewModel() {                                 │   │
│  │      // 50 MutableStateFlows                                        │   │
│  │      // 30 методов                                                  │   │
│  │      // 1000+ строк                                                 │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  Решение: разделить на несколько ViewModels                        │   │
│  │  или использовать Use Cases для логики                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 5. Изменение state не через update/copy                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  data class UiState(val users: MutableList<User>)                   │   │
│  │                                                                     │   │
│  │  class BadViewModel : ViewModel() {                                 │   │
│  │      private val _state = MutableStateFlow(UiState(mutableListOf()))│   │
│  │                                                                     │   │
│  │      fun addUser(user: User) {                                      │   │
│  │          _state.value.users.add(user)  // ❌ UI не обновится!      │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  Решение: immutable data classes + copy()                          │   │
│  │  data class UiState(val users: List<User>)                          │   │
│  │                                                                     │   │
│  │  fun addUser(user: User) {                                          │   │
│  │      _state.update { it.copy(users = it.users + user) }  // ✅     │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Best Practices

```kotlin
// ✅ GOOD ViewModel
@HiltViewModel
class UsersViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val getUsersUseCase: GetUsersUseCase,
    private val deleteUserUseCase: DeleteUserUseCase
) : ViewModel() {

    // Immutable state exposed
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    // One-time events через Channel
    private val _events = Channel<UsersEvent>()
    val events: Flow<UsersEvent> = _events.receiveAsFlow()

    // Search query сохраняется при process death
    private val searchQuery = savedStateHandle.getStateFlow("searchQuery", "")

    init {
        loadUsers()
    }

    fun onSearchChanged(query: String) {
        savedStateHandle["searchQuery"] = query
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            getUsersUseCase(searchQuery.value)
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                    _events.send(UsersEvent.ShowError(e.message ?: "Error"))
                }
        }
    }

    fun onDeleteUser(userId: Long) {
        viewModelScope.launch {
            deleteUserUseCase(userId)
                .onSuccess {
                    _events.send(UsersEvent.ShowToast("User deleted"))
                    loadUsers()
                }
                .onFailure { e ->
                    _events.send(UsersEvent.ShowError(e.message ?: "Error"))
                }
        }
    }

    // Cleanup в onCleared() если нужно
    override fun onCleared() {
        super.onCleared()
        // Отмена работы, закрытие ресурсов
    }
}

// Immutable UI State
data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

// One-time events
sealed class UsersEvent {
    data class ShowToast(val message: String) : UsersEvent()
    data class ShowError(val message: String) : UsersEvent()
    data class NavigateToDetail(val userId: Long) : UsersEvent()
}
```

---

## Testing ViewModel

### Unit Test

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UsersViewModelTest {

    // Rule для замены Dispatchers.Main
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UsersViewModel
    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        fakeRepository = FakeUserRepository()
        viewModel = UsersViewModel(
            savedStateHandle = SavedStateHandle(),
            getUsersUseCase = GetUsersUseCase(fakeRepository),
            deleteUserUseCase = DeleteUserUseCase(fakeRepository)
        )
    }

    @Test
    fun `loadUsers updates state with users`() = runTest {
        // Given
        val users = listOf(User(1, "John"), User(2, "Jane"))
        fakeRepository.setUsers(users)

        // When
        viewModel.loadUsers()

        // Then
        val state = viewModel.uiState.first()
        assertEquals(users, state.users)
        assertFalse(state.isLoading)
        assertNull(state.error)
    }

    @Test
    fun `loadUsers updates state with error on failure`() = runTest {
        // Given
        fakeRepository.setShouldFail(true)

        // When
        viewModel.loadUsers()

        // Then
        val state = viewModel.uiState.first()
        assertTrue(state.users.isEmpty())
        assertFalse(state.isLoading)
        assertNotNull(state.error)
    }

    @Test
    fun `deleteUser sends ShowToast event`() = runTest {
        // Given
        val users = listOf(User(1, "John"))
        fakeRepository.setUsers(users)

        // When
        viewModel.onDeleteUser(1)

        // Then
        val event = viewModel.events.first()
        assertTrue(event is UsersEvent.ShowToast)
    }
}

// MainDispatcherRule для тестов
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Fake Repository
class FakeUserRepository : UserRepository {
    private var users = emptyList<User>()
    private var shouldFail = false

    fun setUsers(users: List<User>) {
        this.users = users
    }

    fun setShouldFail(fail: Boolean) {
        this.shouldFail = fail
    }

    override suspend fun getUsers(): List<User> {
        if (shouldFail) throw Exception("Test error")
        return users
    }

    override suspend fun deleteUser(userId: Long) {
        if (shouldFail) throw Exception("Test error")
        users = users.filter { it.id != userId }
    }
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "ViewModel сохраняет данные при process death" | **Нет!** ViewModel выживает только config changes (rotation). При process death (LMK убивает приложение) ViewModel уничтожается. Для process death нужен SavedStateHandle или persistent storage. |
| "SavedStateHandle — замена SharedPreferences" | SavedStateHandle для UI state (scroll position, выбранный tab). SharedPreferences/DataStore для user preferences и settings. Разные use cases. SavedStateHandle ограничен 1MB и привязан к Activity lifecycle. |
| "AndroidViewModel лучше обычного ViewModel" | AndroidViewModel нужен ТОЛЬКО когда требуется Application context (для системных сервисов). Обычный ViewModel + DI (Hilt) предпочтительнее — проще тестировать, меньше связей. |
| "ViewModel для каждого экрана обязателен" | Для простых stateless экранов ViewModel избыточен. Compose + remember + rememberSaveable может быть достаточно. ViewModel оправдан для бизнес-логики и shared state. |
| "viewModelScope.launch — всегда правильный выбор" | viewModelScope отменяется при onCleared(). Для операций, которые должны завершиться (сохранение в БД), используйте NonCancellable или externalScope. |
| "ViewModel должен быть в single module" | ViewModel может быть в feature module. shared: модуль с интерфейсами и contracts, impl: модуль с реализацией. Это улучшает build time и модульность. |
| "Нельзя иметь несколько ViewModels в одном экране" | Можно и иногда нужно. Разделяйте по responsibility: UserProfileViewModel + UserSettingsViewModel вместо одного большого. Compose + Hilt делает это удобным. |
| "SavedStateHandle работает автоматически" | SavedStateHandle требует явного сохранения данных через `set()` или delegation. Автоматически сохраняются только данные из `SavedStateHandle.getLiveData()` или `getStateFlow()`. |
| "ViewModel не нужен с Compose" | ViewModel нужен для state, переживающего config changes, и для бизнес-логики. Compose remember НЕ переживает rotation. ViewModel + StateFlow + collectAsStateWithLifecycle — best practice. |
| "Все поля ViewModel должны быть LiveData/StateFlow" | Private mutable state + public immutable exposure — это паттерн. Но не все поля должны быть observable. Computed properties, constants, и временные переменные могут быть обычными. |

---

## CS-фундамент

| CS-концепция | Применение в ViewModel |
|--------------|------------------------|
| **Separation of Concerns** | ViewModel отделяет UI logic от business logic. Activity/Fragment — только UI rendering. ViewModel — state management и бизнес операции. |
| **Lifecycle management** | ViewModel привязан к lifecycle scope (Activity/Fragment/NavGraph). Автоматический cleanup при уничтожении scope. onCleared() для manual cleanup. |
| **Object retention** | NonConfigurationInstance механизм Android: объект сохраняется при config change через специальный holder, не через Bundle serialization. |
| **Dependency Injection** | ViewModel получает зависимости через constructor (Hilt/Koin). Инверсия зависимостей: ViewModel зависит от интерфейсов, не реализаций. |
| **Observer pattern** | LiveData/StateFlow — Observable. UI подписывается и реагирует на изменения. ViewModel не знает о UI — только публикует state. |
| **Scope и Lifetime** | viewModelScope.coroutineContext привязан к ViewModel lifecycle. Child coroutines автоматически отменяются при onCleared(). Structured concurrency. |
| **Serialization** | SavedStateHandle использует Bundle serialization. Поддерживаются Parcelable, Serializable, primitives. Ограничение ~1MB на Bundle. |
| **State Machine** | UI State как sealed class: Loading, Success(data), Error(message). ViewModel управляет transitions между состояниями. Predictable state. |
| **Repository pattern** | ViewModel использует Repository для data access. Repository абстрагирует источники данных (network, database, cache). Single source of truth. |
| **Testability** | Constructor injection + fake dependencies = легко тестировать. runTest + TestDispatcher для корутин. Нет зависимости от Android framework. |

---

## Проверь себя

### Вопросы для самопроверки

1. **Как ViewModel переживает configuration change?**
   - Через NonConfigurationInstance механизм
   - ViewModelStore сохраняется при onRetainNonConfigurationInstance()
   - Восстанавливается через getLastNonConfigurationInstance()

2. **Чем SavedStateHandle отличается от обычных полей ViewModel?**
   - SavedStateHandle сохраняется при process death
   - Обычные поля теряются при process death
   - SavedStateHandle ограничен типами Bundle (~1MB)

3. **Почему нельзя хранить Context в ViewModel?**
   - ViewModel живёт дольше Activity
   - Reference на Activity = memory leak
   - Используйте AndroidViewModel для Application context

4. **Что такое viewModelScope?**
   - CoroutineScope привязанный к lifecycle ViewModel
   - Автоматически отменяется при onCleared()
   - Использует Dispatchers.Main.immediate

5. **Когда использовать activityViewModels() vs viewModels()?**
   - viewModels(): ViewModel для текущего Fragment
   - activityViewModels(): shared ViewModel между Fragments
   - Navigation scope: для wizard/flow экранов

---

## Связи

- **[[android-architecture-evolution]]** — эволюция от MVP к MVVM
- **[[android-architecture-patterns]]** — MVVM/MVI паттерны
- **[[android-state-management]]** — StateFlow vs LiveData
- **[[android-activity-lifecycle]]** — lifecycle и configuration changes

---

## Источники

1. [ViewModel Overview](https://developer.android.com/topic/libraries/architecture/viewmodel)
2. [SavedStateHandle](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate)
3. [ViewModel Source Code](https://cs.android.com/androidx/platform/frameworks/support/+/androidx-main:lifecycle/lifecycle-viewmodel/)
4. [Testing ViewModel](https://developer.android.com/training/testing/unit-testing/viewmodel-testing)
5. [Understanding ViewModel Persistence - droidcon 2025](https://www.droidcon.com/2025/01/13/understanding-viewmodel-persistence-across-configuration-changes-in-android/)

---

*Проверено: 2026-01-09 | Обновлено с Мифами и CS-фундаментом*
