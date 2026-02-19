---
title: "MVC и MVP на Android: от God Activity к первому разделению ответственности"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
status: published
cs-foundations: [separation-of-concerns, passive-view, supervising-controller, contract-pattern, lifecycle-management]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-architecture-evolution]]"
  - "[[android-architecture-patterns]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-activity-lifecycle]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
  - "[[observer-pattern]]"
  - "[[testing-fundamentals]]"
  - "[[mocking-strategies]]"
  - "[[dependency-injection-fundamentals]]"
prerequisites:
  - "[[android-activity-lifecycle]]"
  - "[[android-overview]]"
reading_time: 35
difficulty: 5
study_status: not_started
mastery: 0
---

# MVC и MVP на Android: от God Activity к первому разделению ответственности

MVP умирал на Android трижды. Первый раз --- когда Google проигнорировал его в официальных гайдах (2014). Второй --- когда Google сам выпустил Architecture Blueprints с MVP, а через год заменил их на MVVM (2017). Третий --- когда Jetpack ViewModel сделал attach/detach ненужным. И всё же MVP не исчез. Он оставил наследие: **Contract-интерфейсы**, **Passive View**, разделение ответственности --- всё, что мы используем в MVVM и MVI, родилось или окрепло в эпоху MVP. Понимание MVC/MVP --- это не история ради истории. Это понимание ПОЧЕМУ архитектура Android работает так, как работает сегодня.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Activity Lifecycle | Без lifecycle нельзя понять, почему MVP ломается | [[android-activity-lifecycle]] |
| Основы Android | Activity, Fragment, Intent | [[android-overview]] |
| ООП и интерфейсы | Contract pattern построен на интерфейсах | [[oop-fundamentals]] |

---

## MVC на Android: паттерн, которого не было

### Классический MVC: Smalltalk-80

В 1979 году Трюгве Реенскауг (Trygve Reenskaug) придумал MVC для Smalltalk-80. Оригинальная идея предельно проста:

```
ОРИГИНАЛЬНЫЙ MVC (Smalltalk-80)

┌──────────┐    наблюдает     ┌──────────┐
│   VIEW   │ ◄────────────── │  MODEL   │
│ Рисует   │    (Observer)    │ Данные + │
│ UI       │                  │ логика   │
└────▲─────┘                  └────▲─────┘
     │ обновляет                   │ изменяет
┌────┴─────────────────────────────┴─────┐
│              CONTROLLER                 │
│  Принимает ввод (клавиатура, мышь)     │
│  Решает, что делать                     │
│  Обновляет Model или View              │
└─────────────────────────────────────────┘

Ключевое: Controller обрабатывает ВВОД,
View ТОЛЬКО рисует, Model УВЕДОМЛЯЕТ через Observer
```

В Smalltalk UI-элементы (кнопки, текстовые поля) умели только рисовать себя. Они НЕ обрабатывали клики --- этим занимался Controller. View подписывался на Model через Observer pattern и перерисовывался при изменении данных.

### Почему MVC не работает на Android

На Android роли смешаны на уровне фреймворка:

```
"MVC" НА ANDROID

              ACTIVITY
  setContentView()          ← View?
  findViewById()            ← View?
  button.setOnClickListener ← Controller?
  loadData()                ← Controller?
  showError()               ← View?
  saveToDatabase()          ← Model?
  onCreate/onDestroy        ← Lifecycle

  Activity = View + Controller + Lifecycle = GOD OBJECT

Проблема: Android widget (Button, TextView) сам обрабатывает
ввод. Controller как отдельная сущность не нужен.
Activity берёт на себя ВСЁ.
```

**Почему так вышло:**

1. **Android виджеты самодостаточны** --- `Button` сам обрабатывает клики, `EditText` сам управляет фокусом. Роль Controller из Smalltalk исчезла.
2. **Activity --- точка входа** --- система создаёт Activity, передаёт ей Intent, управляет lifecycle. Activity вынуждена быть "хабом".
3. **XML Layout --- это View, но Activity им управляет** --- `setContentView()`, `findViewById()`, обновление виджетов --- всё идёт через Activity.

### God Activity: пример из 2010 года

```kotlin
// ❌ Типичная Activity 2010 года
// Activity = View + Controller + Model + Lifecycle manager
class UserListActivity : Activity() {

    private val users = mutableListOf<User>()
    private var isLoading = false
    private lateinit var db: SQLiteDatabase
    private lateinit var adapter: ArrayAdapter<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_users)

        // View: настройка UI
        adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1)
        findViewById<ListView>(R.id.listView).adapter = adapter

        // Controller: обработка кликов
        findViewById<Button>(R.id.loadButton).setOnClickListener {
            loadUsers()  // бизнес-логика прямо здесь
        }

        // Model: инициализация БД
        db = DatabaseHelper(this).writableDatabase
    }

    // Controller + Model: загрузка данных
    private fun loadUsers() {
        isLoading = true
        updateUI()

        // Сетевой запрос через AsyncTask (утечка памяти!)
        object : AsyncTask<Void, Void, List<User>>() {
            override fun doInBackground(vararg p: Void?): List<User> {
                val url = URL("https://api.example.com/users")
                val conn = url.openConnection() as HttpURLConnection
                return parseJson(conn.inputStream) // парсинг вручную
            }

            override fun onPostExecute(result: List<User>) {
                // Activity может быть уже уничтожена!
                isLoading = false
                users.clear()
                users.addAll(result)
                cacheToDb(result) // Model: кеширование
                updateUI()        // View: обновление
            }
        }.execute()
    }

    // Model: работа с БД
    private fun cacheToDb(list: List<User>) {
        db.beginTransaction()
        try {
            list.forEach { user ->
                val cv = ContentValues().apply {
                    put("id", user.id)
                    put("name", user.name)
                }
                db.insertWithOnConflict("users", null, cv, CONFLICT_REPLACE)
            }
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
        }
    }

    // View: обновление интерфейса
    private fun updateUI() {
        findViewById<ProgressBar>(R.id.progress).visibility =
            if (isLoading) View.VISIBLE else View.GONE
        adapter.clear()
        adapter.addAll(users.map { it.name })
    }

    override fun onDestroy() {
        super.onDestroy()
        db.close() // А если AsyncTask ещё работает?
    }
}
```

**Что здесь не так (считаем ответственности):**

| Ответственность | Строки | Роль в MVC |
|----------------|--------|-----------|
| Инициализация UI | onCreate | View |
| Обработка кликов | setOnClickListener | Controller |
| Сетевой запрос | AsyncTask | Model/Controller |
| Парсинг JSON | parseJson | Model |
| Кеширование в БД | cacheToDb | Model |
| Обновление UI | updateUI | View |
| Управление lifecycle | onDestroy | Ни одна из ролей |

**Шесть ответственностей в одном классе.** Activity знает обо всём: о сети, о БД, об UI, о lifecycle. Это прямое нарушение SRP (см. [[solid-principles]]), и классический пример high coupling + low cohesion (см. [[coupling-cohesion]]).

> **Вывод:** MVC на Android --- это миф. Activity не может быть чистым Controller, потому что фреймворк делает её одновременно View, Controller и lifecycle-хостом. Термин "MVC на Android" --- это ретроспективное название для отсутствия архитектуры.

---

## MVP приходит на помощь (2014--2016)

К 2014 году боль стала нестерпимой: Activity на 2000+ строк, невозможность написать юнит-тест, крэши при повороте экрана. Сообщество обратилось к десктопному и веб-опыту --- к паттерну Model-View-Presenter.

### Определения по Мартину Фаулеру

В 2006 году Мартин Фаулер опубликовал статью "GUI Architectures", в которой разделил MVP на два подпаттерна:

```
ДВА ВАРИАНТА MVP (Martin Fowler, 2006)

PASSIVE VIEW                        SUPERVISING CONTROLLER
─────────────                       ─────────────────────
View полностью пассивна.            View имеет data binding
Presenter управляет ВСЕМ:           для простых случаев.
- Читает данные из Model            Presenter — для сложной
- Форматирует                       логики: валидация,
- Обновляет каждый элемент          условная логика,
  View через setter-ы               координация.

┌───────┐    ┌───────────┐          ┌───────┐    ┌───────────┐
│ View  │◄───│ Presenter │          │ View  │◄───│ Presenter │
│       │    │ (всё)     │          │       │    │ (сложное) │
└───────┘    └─────┬─────┘          └───┬───┘    └─────┬─────┘
                   │                    │ bind          │
                   ▼                    ▼               ▼
             ┌───────────┐        ┌───────────┐  ┌───────────┐
             │   Model   │        │   Model   │  │   Model   │
             └───────────┘        └───────────┘  └───────────┘

+ Максимальная тестируемость      + Меньше кода в Presenter
- Много кода в Presenter          - Часть логики в View (хуже
- Presenter знает детали UI         тестируется)

Android-сообщество выбрало Passive View.
Причина: максимальная тестируемость + чистое разделение.
```

Android-сообщество почти единогласно выбрало **Passive View**. Причины:
- Data binding на Android не существовал до 2015 года
- Главная цель --- тестируемость, а Passive View тестируется лучше
- Контракт-интерфейс чётко определяет границу View/Presenter

### Contract Pattern: сердце MVP на Android

Ключевая идея Android MVP --- **Contract-интерфейс**, объединяющий контракты View и Presenter в одном файле:

```kotlin
// ✅ Contract: единая точка входа для понимания экрана
interface UsersContract {

    interface View {
        fun showLoading()
        fun hideLoading()
        fun showUsers(users: List<UserUiModel>)
        fun showError(message: String)
        fun showEmpty()
        fun navigateToDetail(userId: Long)
    }

    interface Presenter {
        fun attachView(view: View)
        fun detachView()
        fun loadUsers()
        fun onUserClicked(user: UserUiModel)
        fun onRefresh()
    }
}
```

**Зачем Contract:** открываешь один файл --- видишь ВСЕ возможности экрана. Что может View, что может Presenter. Это документация через код.

### Полная реализация Passive View

```kotlin
// ── Presenter ──────────────────────────────────────────────────
class UsersPresenter(
    private val repository: UserRepository
) : UsersContract.Presenter {

    private var view: UsersContract.View? = null

    override fun attachView(view: UsersContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null
    }

    override fun loadUsers() {
        view?.showLoading()

        repository.getUsers(object : UserRepository.Callback {
            override fun onSuccess(users: List<User>) {
                view?.hideLoading()
                if (users.isEmpty()) {
                    view?.showEmpty()
                } else {
                    view?.showUsers(users.map { it.toUiModel() })
                }
            }

            override fun onError(error: Throwable) {
                view?.hideLoading()
                view?.showError(error.message ?: "Неизвестная ошибка")
            }
        })
    }

    override fun onUserClicked(user: UserUiModel) {
        view?.navigateToDetail(user.id)
    }

    override fun onRefresh() {
        loadUsers()
    }

    private fun User.toUiModel() = UserUiModel(
        id = id,
        displayName = "$firstName $lastName",
        avatarUrl = avatarUrl
    )
}

// ── Activity (View) ────────────────────────────────────────────
class UsersActivity : AppCompatActivity(), UsersContract.View {

    private lateinit var presenter: UsersContract.Presenter
    private lateinit var adapter: UsersAdapter
    private lateinit var binding: ActivityUsersBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUsersBinding.inflate(layoutInflater)
        setContentView(binding.root)

        adapter = UsersAdapter { user -> presenter.onUserClicked(user) }
        binding.recyclerView.adapter = adapter
        binding.swipeRefresh.setOnRefreshListener { presenter.onRefresh() }

        // Создание Presenter (в реальном коде — через DI)
        presenter = UsersPresenter(UserRepositoryImpl(ApiService(), UserDao()))
        presenter.attachView(this)
        presenter.loadUsers()
    }

    override fun onDestroy() {
        presenter.detachView()
        super.onDestroy()
    }

    // ── View interface implementation ──────────────────────────
    override fun showLoading() {
        binding.progressBar.isVisible = true
    }

    override fun hideLoading() {
        binding.progressBar.isVisible = false
        binding.swipeRefresh.isRefreshing = false
    }

    override fun showUsers(users: List<UserUiModel>) {
        binding.recyclerView.isVisible = true
        binding.emptyView.isVisible = false
        adapter.submitList(users)
    }

    override fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }

    override fun showEmpty() {
        binding.recyclerView.isVisible = false
        binding.emptyView.isVisible = true
    }

    override fun navigateToDetail(userId: Long) {
        startActivity(UserDetailActivity.newIntent(this, userId))
    }
}
```

**Что изменилось по сравнению с God Activity:**

```
God Activity                         MVP
──────────────────────              ──────────────────────
Activity: 6 ответственностей  →    Activity: только UI (1)
Тестирование: невозможно      →    Presenter: unit test без Android
Изменение UI: трогаем логику  →    Изменение UI: только Activity
Изменение логики: трогаем UI  →    Изменение логики: только Presenter
```

---

## MVP-библиотеки: золотая эра (2014--2017)

Проблема "ручного" MVP --- lifecycle. Кто хранит Presenter при повороте экрана? Кто вызывает attach/detach? Четыре библиотеки предложили свои ответы.

### Nucleus (Konstantin Mikheev, 2014)

Первая серьёзная MVP-библиотека на Android. Главная идея: **Presenter переживает configuration change** через headless retained Fragment.

```kotlin
// Nucleus: Presenter привязан к Bundle → переживает поворот
class UsersPresenter : RxPresenter<UsersView>() {

    // restartableFirst: запрос перезапускается при восстановлении
    override fun onCreate(savedState: Bundle?) {
        super.onCreate(savedState)

        restartableFirst(REQUEST_USERS,
            { userRepository.getUsers() },  // Observable<List<User>>
            { view, users -> view.showUsers(users) },
            { view, error -> view.showError(error.message) }
        )
    }

    fun loadUsers() {
        start(REQUEST_USERS)
    }

    companion object {
        private const val REQUEST_USERS = 1
    }
}

// Activity наследует NucleusAppCompatActivity
class UsersActivity : NucleusAppCompatActivity<UsersPresenter>(), UsersView {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Presenter создаётся/восстанавливается автоматически
        if (savedInstanceState == null) {
            presenter.loadUsers()
        }
    }

    override fun showUsers(users: List<User>) { /* ... */ }
    override fun showError(message: String?) { /* ... */ }
}
```

**Ключевые решения Nucleus:**
- Presenter хранится в retained headless Fragment
- Bundle для сохранения аргументов запросов (не самих данных)
- Тесная интеграция с RxJava 1 (`RxPresenter`)
- Автоматический переподписка Observable при восстановлении

**Проблема:** проект перестал развиваться. Автор пришёл к выводу, что Redux-архитектура масштабируется лучше MVP.

### Mosby (Hannes Dorfmann, 2015)

Самая популярная MVP-библиотека. Названа в честь Теда Мосби из "How I Met Your Mother" (он архитектор). Три ключевые концепции: **MvpPresenter**, **ViewState**, **LCE**.

```kotlin
// ── Mosby: MvpPresenter с ViewState ────────────────────────────

// View interface наследует MvpView
interface UsersView : MvpView {
    fun showLoading()
    fun showContent(users: List<User>)
    fun showError(message: String)
}

// Presenter наследует MvpBasePresenter
class UsersPresenter(
    private val repository: UserRepository
) : MvpBasePresenter<UsersView>() {

    fun loadUsers() {
        ifViewAttached { view -> view.showLoading() }

        repository.getUsers()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { users ->
                    ifViewAttached { view -> view.showContent(users) }
                },
                { error ->
                    ifViewAttached { view ->
                        view.showError(error.message ?: "Error")
                    }
                }
            )
    }
}

// ViewState: запоминает последнее состояние View
class UsersViewState : MvpViewState<UsersView> {

    private var state: State = State.Loading
    private var users: List<User> = emptyList()
    private var errorMessage: String = ""

    sealed class State { /* Loading, Content, Error */ }

    fun setLoading() { state = State.Loading }

    fun setContent(users: List<User>) {
        state = State.Content
        this.users = users
    }

    fun setError(message: String) {
        state = State.Error
        errorMessage = message
    }

    // Вызывается при повороте — восстанавливает View
    override fun apply(view: UsersView) {
        when (state) {
            State.Loading -> view.showLoading()
            State.Content -> view.showContent(users)
            State.Error -> view.showError(errorMessage)
        }
    }
}

// Activity использует MvpViewStateActivity
class UsersActivity : MvpViewStateActivity<UsersView, UsersPresenter>(),
    UsersView {

    override fun createPresenter() = UsersPresenter(repository)
    override fun createViewState() = UsersViewState()

    override fun onNewViewStateInstance() {
        presenter.loadUsers() // первый запуск
    }

    override fun showLoading() {
        (viewState as UsersViewState).setLoading()
        // показать прогресс
    }

    override fun showContent(users: List<User>) {
        (viewState as UsersViewState).setContent(users)
        // показать список
    }

    override fun showError(message: String) {
        (viewState as UsersViewState).setError(message)
        // показать ошибку
    }
}
```

**LCE pattern (Loading-Content-Error):** Mosby стандартизировал три состояния экрана. `MvpLceView<D>` предоставлял `showLoading()`, `showContent(data: D)`, `showError(e: Throwable)` из коробки.

**Mosby 3** добавил `ifViewAttached {}` --- лямбда выполняется только если View прикреплена. Это решало проблему null-проверок `view?.`.

### Moxy (Arello Mobile, 2016)

Российская библиотека, решившая главную проблему MVP --- **потерю команд при повороте экрана**. Ключевая инновация: **ViewCommand queue** + автоматическая генерация ViewState через annotation processing.

```kotlin
// ── Moxy: автоматический ViewState через аннотации ─────────────

// View interface: аннотации определяют стратегию
interface UsersView : MvpView {

    @StateStrategyType(AddToEndSingleStrategy::class)
    fun showLoading()

    @StateStrategyType(AddToEndSingleStrategy::class)
    fun showUsers(users: List<User>)

    @StateStrategyType(AddToEndSingleStrategy::class)
    fun showError(message: String)

    @StateStrategyType(OneExecutionStateStrategy::class)
    fun showToast(text: String)  // показать один раз, не повторять

    @StateStrategyType(SkipStrategy::class)
    fun navigateToDetail(userId: Long)  // не сохранять в очередь
}

// Presenter: @InjectViewState генерирует ViewState-прокси
@InjectViewState
class UsersPresenter(
    private val repository: UserRepository
) : MvpPresenter<UsersView>() {

    override fun onFirstViewAttach() {
        loadUsers()  // вызывается один раз при первом attach
    }

    fun loadUsers() {
        viewState.showLoading()  // viewState — сгенерированный прокси

        repository.getUsers()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { users -> viewState.showUsers(users) },
                { error -> viewState.showError(error.message ?: "Error") }
            )
    }

    fun onUserClicked(user: User) {
        viewState.navigateToDetail(user.id)
    }
}

// Activity: минимум boilerplate
class UsersActivity : MvpAppCompatActivity(), UsersView {

    @InjectPresenter
    lateinit var presenter: UsersPresenter

    override fun showLoading() { /* показать прогресс */ }
    override fun showUsers(users: List<User>) { /* показать список */ }
    override fun showError(message: String) { /* показать ошибку */ }
    override fun showToast(text: String) { Toast.makeText(this, text, LENGTH_SHORT).show() }
    override fun navigateToDetail(userId: Long) { /* навигация */ }
}
```

**Как работает Moxy под капотом:**

```
Presenter вызывает: viewState.showUsers(users)
            │
            ▼
┌───────────────────────────────────────────────────────┐
│  Сгенерированный ViewState$$State                     │
│                                                       │
│  Очередь команд:                                      │
│  [1] ShowLoadingCommand (AddToEndSingle)  ← удалена   │
│  [2] ShowUsersCommand(users) (AddToEndSingle) ← акт.  │
│  [3] ShowToastCommand("Saved!") (OneExecution)         │
└───────────────────┬───────────────────────────────────┘
                    │  Поворот экрана → View пересоздана
                    ▼
attachView(): воспроизвести очередь команд
→ showUsers(users)    — воспроизведена
→ showToast("Saved!") — выполнена + удалена из очереди

Стратегии:
• AddToEndSingle — одна команда данного типа (заменяет старую)
• AddToEnd       — команды накапливаются в очереди
• OneExecution   — выполнить один раз, потом удалить
• SkipStrategy   — не сохранять (навигация, диалоги)
```

**Главная инновация Moxy:** разработчик не пишет ViewState вручную. Annotation processor генерирует:
1. `ViewState$$State` --- прокси, записывающий команды
2. `ViewCommand` для каждого метода View-интерфейса
3. Логику стратегий (когда добавлять, когда заменять, когда удалять)

### ThirtyInch (grandcentrix, 2016)

Минималистичная немецкая библиотека с фокусом на простоте API:

```kotlin
class UsersPresenter : TiPresenter<UsersView>() {

    override fun onAttachView(view: UsersView) {
        super.onAttachView(view)
        loadUsers()
    }

    private fun loadUsers() {
        // sendToView: безопасная отправка команды
        // если View detached — подождёт attach
        sendToView { view -> view.showUsers(repository.getUsers()) }
    }
}

class UsersActivity : TiActivity<UsersPresenter, UsersView>(), UsersView {
    override fun providePresenter(): UsersPresenter = UsersPresenter()
    override fun showUsers(users: List<User>) { /* ... */ }
}
```

**Фишка:** `sendToView {}` --- команда буферизуется, если View не прикреплена, и выполняется при attach. Аналог одной стратегии Moxy, но без кодогенерации.

### Сравнение MVP-библиотек

| Критерий | Nucleus | Mosby | Moxy | ThirtyInch |
|----------|---------|-------|------|------------|
| **Год** | 2014 | 2015 | 2016 | 2016 |
| **Автор** | K. Mikheev | H. Dorfmann | Arello Mobile | grandcentrix |
| **ViewState** | Bundle (аргументы) | Ручной | Автогенерация | sendToView buffer |
| **Retained Presenter** | Headless Fragment | Retained Fragment / Loader | Custom scope | Activity retained |
| **Кодогенерация** | Нет | Нет | Да (APT) | Нет |
| **RxJava** | Встроен | Опционально | Опционально | Опционально |
| **API-стиль** | Функциональный | OOP inheritance | Аннотации | Минималистичный |
| **LCE из коробки** | Нет | Да | Нет | Нет |
| **Стратегии ViewState** | Нет | Нет | 4 стратегии | Нет |
| **Поддержка (2026)** | Заброшен | Заброшен | Заброшен | Заброшен |

> Все четыре библиотеки заброшены. Это не случайность --- это следствие системных проблем MVP, которые невозможно решить библиотекой.

---

## Почему MVP проиграл

MVP решил проблему God Activity, но создал новые. Пять причин, по которым сообщество ушло от MVP.

### 1. Lifecycle Hell: attach/detach --- это ручное управление

```kotlin
// Проблема: когда вызывать attachView / detachView?
class UsersActivity : AppCompatActivity(), UsersContract.View {

    private lateinit var presenter: UsersPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UsersPresenter(repository)
        presenter.attachView(this)  // ← здесь? или в onStart?
    }

    override fun onStart() {
        super.onStart()
        // presenter.attachView(this)  // ← или здесь?
    }

    override fun onStop() {
        // presenter.detachView()  // ← или здесь?
        super.onStop()
    }

    override fun onDestroy() {
        presenter.detachView()  // ← или здесь?
        super.onDestroy()
    }
}
```

**Проблемы:**
- `attachView` в `onCreate` → callback может прийти, когда View ещё не полностью инициализирована
- `detachView` в `onDestroy` → Presenter держит reference на уничтожаемую Activity во время onStop→onDestroy
- `detachView` в `onStop` → пропускаем обновления, когда Activity в background
- Configuration change → `detachView` + `attachView` на НОВОЙ Activity, но Presenter может быть уничтожен вместе со старой
- Забыл `detachView` → **memory leak**. Activity не может быть собрана GC

```
ПОВОРОТ ЭКРАНА: MVP LIFECYCLE HELL

Activity A (portrait)              Activity B (landscape)
─────────────────────              ──────────────────────
onCreate
  presenter.attachView(A)
  presenter.loadUsers()
    ↓ запрос в сеть...

── ПОВОРОТ ЭКРАНА ──────────────────────────────────
onDestroy                          onCreate
  presenter.detachView()             presenter = ??? ← КТО СОЗДАЛ?
  (view = null)

Вариант 1: новый Presenter → данные потеряны, запрос заново
Вариант 2: retained Presenter → ответ от сети пришёл между
           detach и attach → ДАННЫЕ ПОТЕРЯНЫ (если не буферизованы)
Вариант 3: Moxy ViewCommand queue → работает! Но это уже
           полшага к ViewModel + LiveData
```

### 2. Boilerplate: интерфейс на каждый чих

Для одного экрана в MVP нужно минимум **4 файла**:

```
UsersContract.kt     — View + Presenter интерфейсы
UsersPresenter.kt    — реализация Presenter
UsersActivity.kt     — реализация View
UsersModule.kt       — DI-модуль (Dagger)
```

Для сложного экрана View-интерфейс разрастается до **15+ методов** (`showLoading`, `hideLoading`, `showUsers`, `showError`, `showEmpty`, `showFilterDialog`, `updateFilter`, `showDeleteConfirmation`, `navigateToDetail`, `navigateToCreate`, `showNetworkError`, `showRetryButton`, `hideRetryButton`...) --- и каждый нужно реализовать в Activity. Изменение одного метода требует правки в трёх местах: интерфейс + Presenter + Activity. Сравни с MVVM, где StateFlow с одним UI-state data class заменяет весь этот интерфейс.

### 3. Presenter держит ссылку на View

```kotlin
class UsersPresenter {
    private var view: UsersContract.View? = null  // ← ссылка на Activity!

    fun loadUsers() {
        view?.showLoading()  // null-check на каждый вызов

        repository.getUsers { result ->
            view?.hideLoading()  // view может быть null
            view?.showUsers(result)  // вызов на null = NOP, данные потеряны
        }
    }
}
```

**Проблемы:**
- `view?.` --- nullable-вызов на каждой строке, данные молча теряются
- Presenter "знает" о View --- это bidirectional dependency (см. [[coupling-cohesion]])
- Сравни с ViewModel: ViewModel НЕ знает о View. View подписывается через Observer (см. [[observer-pattern]]). Unidirectional dependency.

### 4. State не переживает process death

```kotlin
// Presenter хранит состояние в памяти
class UsersPresenter {
    private var cachedUsers: List<User>? = null  // ← в памяти
    private var currentPage = 1                   // ← в памяти
    private var activeFilter: Filter? = null       // ← в памяти
}

// Process death (система убила приложение) →
// Presenter уничтожен →
// cachedUsers = null, currentPage = 1, activeFilter = null →
// Пользователь видит пустой экран
```

Для сохранения state при process death нужно было вручную реализовать `onSaveState(bundle)` / `onRestoreState(bundle)` в Presenter. Это дополнительный boilerplate, и большинство разработчиков его не писали.

**ViewModel + SavedStateHandle** решает это автоматически.

### 5. Императивный, не реактивный

MVP --- это **императивный** подход: Presenter *командует* View, что делать.

```kotlin
// MVP: Presenter отдаёт команды
view?.showLoading()
view?.hideLoading()
view?.showUsers(users)
view?.showError(message)

// MVVM: ViewModel выставляет состояние, View реагирует
_uiState.value = UiState.Loading
_uiState.value = UiState.Success(users)
_uiState.value = UiState.Error(message)
```

В MVP сложно комбинировать данные из нескольких источников. Что если нужно показать список пользователей + баннер + счётчик непрочитанных? В MVP --- три отдельных метода в интерфейсе. В MVVM --- один data class с тремя полями в StateFlow.

---

## Миграция MVP → MVVM

Миграция выполняется поэтапно. Ключевые шаги:

### Шаг 1: Заменить View interface на UI State

```kotlin
// БЫЛО (MVP): 6 методов в интерфейсе
interface UsersContract.View {
    fun showLoading()
    fun hideLoading()
    fun showUsers(users: List<UserUiModel>)
    fun showError(message: String)
    fun showEmpty()
    fun navigateToDetail(userId: Long)
}

// СТАЛО (MVVM): один data class
data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<UserUiModel> = emptyList(),
    val error: String? = null
)

// Навигация — отдельный one-shot event
sealed class UsersEvent {
    data class NavigateToDetail(val userId: Long) : UsersEvent()
}
```

### Шаг 2: Заменить Presenter на ViewModel

```kotlin
// БЫЛО (MVP): Presenter с attach/detach, view?.method(), callback-и
// (полный код Presenter — см. выше в разделе «Полная реализация Passive View»)

// СТАЛО (MVVM): ViewModel с StateFlow
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    private val _events = Channel<UsersEvent>()
    val events: Flow<UsersEvent> = _events.receiveAsFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(
                        isLoading = false,
                        users = users.map { u -> u.toUiModel() }
                    ) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(
                        isLoading = false,
                        error = error.message ?: "Error"
                    ) }
                }
        }
    }

    fun onUserClicked(user: UserUiModel) {
        viewModelScope.launch {
            _events.send(UsersEvent.NavigateToDetail(user.id))
        }
    }
}
```

### Шаг 3: Упростить Activity

```kotlin
// БЫЛО: Activity implements View interface + attach/detach + 6 override-ов
// (полный код — см. выше)

// СТАЛО: Activity подписывается на StateFlow, нет attach/detach
class UsersActivity : AppCompatActivity() {

    private val viewModel: UsersViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding = ActivityUsersBinding.inflate(layoutInflater)
        setContentView(binding.root)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.uiState.collect { state ->
                        binding.progressBar.isVisible = state.isLoading
                        binding.recyclerView.isVisible = state.users.isNotEmpty()
                        binding.emptyView.isVisible =
                            !state.isLoading && state.users.isEmpty() && state.error == null
                        adapter.submitList(state.users)
                        state.error?.let { showSnackbar(it) }
                    }
                }
                launch {
                    viewModel.events.collect { event ->
                        when (event) {
                            is UsersEvent.NavigateToDetail ->
                                startActivity(UserDetailActivity.newIntent(this@UsersActivity, event.userId))
                        }
                    }
                }
            }
        }
    }
    // Нет onDestroy()! Lifecycle управляется автоматически.
}
```

**Что исчезло:**
- `attachView` / `detachView` --- lifecycle управляется `repeatOnLifecycle`
- View interface (6 методов) --- заменён одним `StateFlow<UiState>`
- Null-checks `view?.` --- ViewModel не знает о View
- Ручное сохранение state --- ViewModel переживает configuration change

---

## Мифы и заблуждения

**Миф 1: "MVP мёртв, его нельзя использовать"**

Реальность: MVP жив в legacy-проектах и прекрасно работает. Mosby, Moxy --- заброшены как библиотеки, но паттерн Contract + Presenter функционален. Для нового проекта выбирать MVP нет смысла, но рефакторить работающий MVP-код только ради "модности" --- тоже.

**Миф 2: "MVC на Android --- это правильный подход для простых экранов"**

Реальность: "MVC на Android" --- это эвфемизм для отсутствия архитектуры. Даже для простого экрана ViewModel + StateFlow дают тестируемость без дополнительных усилий. "Простой экран" имеет привычку становиться сложным.

**Миф 3: "MVVM --- это просто MVP с data binding"**

Реальность: Фундаментальное отличие --- направление зависимости. В MVP: Presenter → View (bidirectional, Presenter знает о View). В MVVM: View → ViewModel (unidirectional, ViewModel НЕ знает о View). Это меняет тестируемость, lifecycle-безопасность и coupling.

**Миф 4: "MVP лучше тестируется, чем MVVM"**

Реальность: MVP тестируется хорошо (Presenter --- чистый Kotlin). Но MVVM тестируется ТАК ЖЕ хорошо (ViewModel --- чистый Kotlin) + не нужно мокать View interface. Тест ViewModel: emit action → assert state. Проще.

**Миф 5: "Contract interface --- это лишний boilerplate"**

Реальность: Contract --- одно из лучших наследий MVP. Он документирует возможности экрана через код. В MVVM роль Contract выполняет UI State data class + sealed class Event. Идея та же --- явный контракт между слоями.

**Миф 6: "Moxy/Mosby решили все проблемы MVP"**

Реальность: Библиотеки решили проблему ViewState, но не проблему bidirectional dependency, boilerplate интерфейсов и императивности. ViewCommand queue в Moxy --- это по сути ручная реализация того, что LiveData/StateFlow делает автоматически.

---

## CS-фундамент

| CS-концепция | Как проявляется в MVP |
|-------------|----------------------|
| **Separation of Concerns** | Presenter отделяет бизнес-логику от UI --- главная цель MVP |
| **Passive View** (Fowler) | View не принимает решений, только выполняет команды Presenter |
| **Supervising Controller** (Fowler) | View имеет data binding, Presenter --- для сложной логики |
| **Contract Pattern** | Интерфейс как контракт между View и Presenter |
| **Dependency Inversion** | View interface --- абстракция, от которой зависит Presenter |
| **Observer Pattern** | В чистом MVP нет Observer (императивные вызовы). MVVM добавляет Observer через LiveData/Flow |
| **Command Pattern** | Moxy ViewCommand --- команды как объекты в очереди |
| **Lifecycle Management** | Ручное attach/detach --- главная слабость MVP на Android |
| **State Machine** | LCE (Loading/Content/Error) --- конечный автомат состояний экрана |

---

## Связь с другими темами

**[[solid-principles]]** --- God Activity нарушает SRP (6 ответственностей в одном классе). MVP восстанавливает SRP: Activity отвечает за UI, Presenter --- за логику. DIP (Dependency Inversion Principle) проявляется в Contract: Presenter зависит от абстракции `UsersContract.View`, а не от конкретной `UsersActivity`. Это позволяет подставить mock в тестах.

**[[coupling-cohesion]]** --- MVP снижает coupling Activity (она больше не знает о сети и БД), но создаёт bidirectional coupling между Presenter и View (Presenter ↔ View через interface). MVVM разрывает эту связь: ViewModel не знает о View (unidirectional dependency). Cohesion растёт: Presenter содержит только бизнес-логику, Activity --- только UI.

**[[observer-pattern]]** --- Классический MVP использует императивные вызовы (`view.showUsers()`), а не Observer. Это фундаментальное отличие от MVVM, где View подписывается на изменения ViewModel через Observer (LiveData, StateFlow). Moxy ViewCommand queue --- промежуточный шаг: буферизация команд --- это уже почти реактивность.

**[[adapter-pattern]]** --- View Interface в MVP --- это по сути Adapter между Presenter (не знает об Android) и Activity (привязана к Android). Interface адаптирует абстрактные команды (`showUsers`) к конкретным Android-вызовам (`adapter.submitList()`).

**[[testing-fundamentals]]** --- MVP сделал unit-тестирование на Android возможным. Presenter --- чистый Kotlin-класс без Android-зависимостей. Можно тестировать бизнес-логику без эмулятора: создать Presenter, подставить mock View, вызвать метод, проверить вызовы на mock. До MVP unit-тесты Android-логики были практически невозможны.

**[[mocking-strategies]]** --- Mock View interface --- стандартный подход тестирования MVP. `verify(view).showUsers(expectedUsers)` --- типичный assert в MVP-тесте. Это просто, но требует создания mock для каждого теста. В MVVM мокать View не нужно --- тестируем StateFlow напрямую.

**[[composition-vs-inheritance]]** --- Mosby требовал наследование: `MvpActivity`, `MvpFragment`, `MvpPresenter`. Это классическая проблема inheritance-based frameworks: нельзя использовать свою базовую Activity. Moxy частично решила это через аннотации, но Presenter всё равно наследовал `MvpPresenter`. Jetpack ViewModel работает через composition: `by viewModels()`.

**[[android-architecture-evolution]]** --- MVP --- вторая эра в эволюции Android-архитектуры (2014--2016). Он стоит между God Activity (2008--2012) и MVVM (2017+). Хронологический контекст и обзор всех эр --- в файле эволюции.

**[[android-activity-lifecycle]]** --- Lifecycle --- главная причина провала MVP на Android. Activity пересоздаётся при повороте, при смене языка, при нехватке памяти. Presenter, не привязанный к lifecycle, должен вручную обрабатывать attach/detach. Jetpack ViewModel решает это, потому что он lifecycle-aware компонент --- он переживает configuration change автоматически.

---

## Источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Martin Fowler — GUI Architectures](https://martinfowler.com/eaaDev/uiArchs.html) | Статья (2006) | Определение Passive View и Supervising Controller. Первоисточник терминологии MVP |
| [Martin Fowler — Passive View](https://martinfowler.com/eaaDev/PassiveScreen.html) | Статья (2006) | Детальное описание паттерна Passive View |
| [Mosby — GitHub](https://github.com/sockeqwe/mosby) | Библиотека | MVP + MVI библиотека от Hannes Dorfmann. ViewState, LCE pattern |
| [Moxy — GitHub](https://github.com/Arello-Mobile/Moxy) | Библиотека | MVP с автоматической генерацией ViewState. ViewCommand queue, State Strategies |
| [Nucleus — GitHub](https://github.com/konmik/nucleus) | Библиотека | Первая MVP-библиотека. Retained Presenter, RxJava интеграция |
| [ThirtyInch — GitHub](https://github.com/grandcentrix/ThirtyInch) | Библиотека | Минималистичный MVP, sendToView буферизация |
| [Konstantin Mikheev — Introduction to MVP on Android](https://konmik.com/post/introduction_to_model_view_presenter_on_android/) | Статья | Философия MVP от автора Nucleus |
| [Antonio Leiva — MVP for Android](https://antonioleiva.com/mvp-android) | Статья | Практический гайд по MVP на Android |
| [Android Architecture Blueprints](https://github.com/android/architecture-samples) | Google | Официальные примеры от Google: MVP → MVVM → Compose |
| [Hannes Dorfmann — Mosby](https://hannesdorfmann.com/android/mosby/) | Статья | Оригинальная документация Mosby от автора |

---

## Проверь себя

> [!question]- Почему MVC в оригинальном понимании (Smalltalk-80) не работает на Android?
> В Smalltalk Controller обрабатывал пользовательский ввод (клавиатура, мышь), а View только рисовала. На Android виджеты (Button, EditText) сами обрабатывают ввод --- роль Controller исчезла. Activity вынуждена быть одновременно View (setContentView, обновление UI) и Controller (обработка кликов), а также управлять lifecycle. Это создаёт God Object с множеством ответственностей.

> [!question]- Чем Passive View отличается от Supervising Controller и какой вариант выбрало Android-сообщество?
> В Passive View --- View полностью пассивна, Presenter управляет всем (читает Model, форматирует данные, обновляет каждый элемент View через методы интерфейса). В Supervising Controller --- View имеет data binding для простых случаев, Presenter подключается для сложной логики. Android-сообщество выбрало Passive View, потому что: (1) data binding на Android появился поздно (2015), (2) Passive View даёт максимальную тестируемость, (3) Contract-интерфейс чётко фиксирует границу.

> [!question]- Назовите три ключевые проблемы MVP, которые решил MVVM с ViewModel + StateFlow.
> 1. **Lifecycle**: attach/detach заменён на автоматическое lifecycle-awareness ViewModel + `repeatOnLifecycle`. 2. **Bidirectional coupling**: Presenter знал о View через interface; ViewModel НЕ знает о View, View подписывается через Observer (unidirectional). 3. **Boilerplate**: View interface с 10+ методами заменён одним `StateFlow<UiState>` с data class.

---

## Ключевые карточки

**Q: Что такое Contract Pattern в MVP?**
A: Интерфейс (обычно один файл), объединяющий контракты View и Presenter. Открыв Contract, видишь ВСЕ возможности экрана: что может View (showLoading, showUsers...) и что может Presenter (loadUsers, onUserClicked...). Contract --- это документация через код.

**Q: Как Moxy решала проблему потери данных при повороте экрана?**
A: Через ViewCommand Queue: каждый вызов метода View (showUsers, showError) превращается в Command-объект и добавляется в очередь. При повороте экрана новая View получает attach --- и Moxy воспроизводит все команды из очереди. Стратегии (AddToEndSingle, OneExecution, Skip) определяют, какие команды сохранять, заменять или удалять.

**Q: Почему направление зависимости --- главное отличие MVP от MVVM?**
A: В MVP: Presenter → View (bidirectional, Presenter вызывает методы View). В MVVM: View → ViewModel (unidirectional, ViewModel не знает о View). Unidirectional dependency означает: (1) ViewModel проще тестировать (не нужен mock View), (2) нет risk утечки памяти (ViewModel не держит ссылку на Activity), (3) данные не теряются (StateFlow хранит последнее значение).

**Q: Какие четыре стратегии ViewCommand использовала Moxy?**
A: 1) **AddToEndSingle** --- одна команда данного типа (новая заменяет старую). 2) **AddToEnd** --- команды накапливаются в очереди. 3) **OneExecution** --- выполнить один раз при attach, затем удалить (для Toast). 4) **SkipStrategy** --- не сохранять (для навигации, которую нельзя повторять).

**Q: Что общего у LCE-паттерна из Mosby и sealed class UiState в MVVM?**
A: Оба представляют конечный автомат состояний экрана: Loading, Content (Success), Error. LCE из Mosby стал предшественником `sealed class UiState`. Разница: в Mosby LCE --- это три метода View-интерфейса, в MVVM --- три состояния одного data type в StateFlow. Идея одна, реализация эволюционировала от императивных команд к декларативному состоянию.

---

## Куда дальше

| Направление | Файл | Зачем |
|------------|------|-------|
| MVVM deep-dive | [[android-mvvm-deep-dive]] | Следующая эра: ViewModel, LiveData, StateFlow --- как MVP эволюционировал |
| Эволюция архитектуры | [[android-architecture-evolution]] | Хронологический контекст: от God Activity до Compose |
| SOLID принципы | [[solid-principles]] | SRP и DIP --- CS-фундамент, на котором построен MVP |
| Coupling и Cohesion | [[coupling-cohesion]] | Метрики, объясняющие почему MVP лучше God Activity, но хуже MVVM |
| Observer Pattern | [[observer-pattern]] | Паттерн, который отличает MVVM от MVP на фундаментальном уровне |
| Тестирование | [[testing-fundamentals]] | MVP сделал тестирование на Android возможным. Как именно |
