---
title: "Cross-Platform: Lifecycle — UIViewController vs Activity"
created: 2026-01-11
modified: 2026-01-11
type: comparison
status: published
tags:
  - type/comparison
  - topic/lifecycle
  - topic/ios
  - topic/android
  - level/intermediate
---

# Жизненный цикл: UIViewController vs Activity/Fragment

## TL;DR — Сравнительная таблица

| Аспект | iOS (UIViewController) | Android (Activity/Fragment) |
|--------|------------------------|----------------------------|
| **Философия** | View-driven (UI определяет состояние) | System-driven (ОС контролирует) |
| **Инициализация** | `init` → `loadView` → `viewDidLoad` | `onCreate(Bundle?)` |
| **Появление на экране** | `viewWillAppear` → `viewDidAppear` | `onStart` → `onResume` |
| **Уход с экрана** | `viewWillDisappear` → `viewDidDisappear` | `onPause` → `onStop` |
| **Уничтожение** | `deinit` | `onDestroy` |
| **Process Death** | Нет callback, jetsam убивает молча | `onSaveInstanceState` перед смертью |
| **Восстановление** | `NSCoding`, `@AppStorage`, SceneDelegate | `onCreate(savedInstanceState)` |
| **Поворот экрана** | Нет пересоздания по умолчанию | Activity пересоздаётся |
| **Сохранение состояния** | Вручную через UserDefaults/Files | Bundle + SavedStateHandle |
| **ViewModel выживает** | Нет нативного механизма | Да, через ViewModelStore |
| **Гарантия вызова deinit/onDestroy** | Нет (может быть retain cycle) | Нет (process death) |
| **Background limit** | ~30 сек, потом suspended | Система может убить в любой момент |

---

## Почему платформы выбрали разные подходы?

### iOS: View-driven Lifecycle

Apple проектировала iOS в эпоху, когда:
- Устройства имели достаточно памяти для одного активного приложения
- Пользователь фокусировался на одном приложении за раз
- Переключение между приложениями было редким

**Философия iOS:**
```
┌─────────────────────────────────────────────────────────────┐
│                     iOS App Lifecycle                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Приложение  ──────►  Приложение в   ──────►  Suspended    │
│   активно              фоне (30 сек)            (заморожено) │
│                                                              │
│   • UI в фокусе        • Может завершить     • Никакого      │
│   • Все callback         работу                 кода         │
│   • Полный контроль    • Ограниченное        • Jetsam может  │
│                          время                  убить        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**UIViewController привязан к UI:**
- Жизненный цикл контроллера = жизненный цикл его view
- Когда view появляется — `viewWillAppear`
- Когда view уходит — `viewWillDisappear`
- Контроллер живёт, пока на него есть strong reference

```swift
// iOS: Жизненный цикл предсказуем и связан с UI
class ProfileViewController: UIViewController {

    // Вызывается ОДИН раз при загрузке view
    override func viewDidLoad() {
        super.viewDidLoad()
        // Инициализация UI
    }

    // Вызывается КАЖДЫЙ раз при появлении
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Обновление данных
    }
}
```

### Android: System-driven Lifecycle

Google проектировала Android для:
- Устройств с ограниченной памятью
- Многозадачности (несколько приложений в памяти)
- Возможности системы убить приложение в любой момент

**Философия Android:**
```
┌─────────────────────────────────────────────────────────────┐
│                   Android App Lifecycle                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Activity    ──────►  Activity      ──────►  Process       │
│   resumed             stopped                 killed         │
│                                                              │
│   • В фокусе          • Не видна             • Система       │
│   • Полный            • Может быть             освободила    │
│     контроль            убита                  память        │
│                       • onSaveInstanceState  • Восстановле-  │
│                         вызван                 ние через     │
│                                                Bundle        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Activity может быть убита в любой момент:**
- Система решает, когда освободить память
- `onSaveInstanceState` — последний шанс сохранить данные
- При возврате — `onCreate(Bundle?)` с сохранённым состоянием

```kotlin
// Android: Система контролирует жизненный цикл
class ProfileActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Проверяем: это первый запуск или восстановление?
        if (savedInstanceState != null) {
            // Восстанавливаем состояние после process death
            val userId = savedInstanceState.getString("user_id")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохраняем состояние ПЕРЕД возможной смертью
        outState.putString("user_id", currentUserId)
    }
}
```

### Ключевые различия в дизайне

```
┌─────────────────────────────────────────────────────────────┐
│                    Сравнение философий                       │
├──────────────────────────┬──────────────────────────────────┤
│          iOS             │            Android               │
├──────────────────────────┼──────────────────────────────────┤
│                          │                                  │
│  "Приложение — царь"     │  "Система — царь"                │
│                          │                                  │
│  UI определяет жизнь     │  Ресурсы определяют жизнь        │
│  контроллера             │  Activity                        │
│                          │                                  │
│  Suspended = заморожен   │  Stopped = может умереть         │
│  (код не выполняется)    │  (система решает)                │
│                          │                                  │
│  Jetsam убивает молча    │  onSaveInstanceState             │
│  (нет callback)          │  перед смертью                   │
│                          │                                  │
│  Восстановление =        │  Восстановление =                │
│  ответственность         │  часть контракта                 │
│  разработчика            │  с системой                      │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

---

## Интуиция: 5 аналогий для понимания

### Аналогия 1: iOS VC = Актёр на сцене

```
┌─────────────────────────────────────────────────────────────┐
│                    Театральная сцена                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│   │ За      │ ───► │ На      │ ───► │ За      │             │
│   │ кулисами│      │ сцене   │      │ кулисами│             │
│   └─────────┘      └─────────┘      └─────────┘             │
│       │                │                │                    │
│   viewDidLoad     viewDidAppear    viewDidDisappear         │
│   (репетиция)     (выступление)    (уход со сцены)          │
│                                                              │
│   Актёр (UIViewController) контролирует своё появление      │
│   Режиссёр (приложение) решает, когда актёр выходит         │
│   Сцена (view) — это площадка для выступления               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Суть аналогии:**
- Актёр выходит на сцену (`viewWillAppear`)
- Актёр на сцене играет (`viewDidAppear`)
- Актёр уходит со сцены (`viewWillDisappear`, `viewDidDisappear`)
- Актёр знает, когда он на сцене и когда за кулисами
- Актёр не исчезает случайно во время выступления

### Аналогия 2: Android Activity = Гость в отеле

```
┌─────────────────────────────────────────────────────────────┐
│                       Отель "Android"                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│   │ Заселе- │ ───► │ В       │ ───► │ Выселе- │             │
│   │ ние     │      │ номере  │      │ ние     │             │
│   └─────────┘      └─────────┘      └─────────┘             │
│       │                │                │                    │
│   onCreate         onResume         onDestroy               │
│                                                              │
│   НО! Администрация (система) может выселить                │
│   гостя в любой момент, если нужен номер!                   │
│                                                              │
│   ┌─────────────────────────────────────────────┐           │
│   │  "Уважаемый гость, сохраните вещи в сейфе   │           │
│   │   (onSaveInstanceState), мы можем выселить  │           │
│   │   вас без предупреждения"                   │           │
│   └─────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Суть аналогии:**
- Гость заселяется (`onCreate`)
- Гость активен в номере (`onResume`)
- Гость может быть выселен системой в любой момент
- `onSaveInstanceState` = положить ценности в сейф
- При возвращении гость получает свои вещи из сейфа (`onCreate(bundle)`)

### Аналогия 3: iOS = Предсказуемый спектакль

```
┌─────────────────────────────────────────────────────────────┐
│                   Классический театр                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Акт 1     →     Акт 2     →     Акт 3     →     Финал     │
│   (init)       (viewDidLoad)  (viewDidAppear)   (deinit)    │
│                                                              │
│   • Сценарий известен заранее                               │
│   • Антракты предсказуемы (viewWillDisappear)               │
│   • Спектакль заканчивается по плану                        │
│   • Зритель (пользователь) контролирует паузу               │
│                                                              │
│   Исключение: Пожар в театре (jetsam) — всех выгоняют       │
│   без предупреждения, но это редкость                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Аналогия 4: Android = Импровизация с режиссёром-системой

```
┌─────────────────────────────────────────────────────────────┐
│                Импровизационный театр                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Актёр (Activity) выходит на сцену... но!                  │
│                                                              │
│   РЕЖИССЁР (система): "Стоп! Мне нужна эта сцена            │
│   для другого актёра. Запиши свой текст (saveState)         │
│   и уходи. Когда вернёшься — продолжишь с того места."     │
│                                                              │
│   ┌─────────────────────────────────────────────┐           │
│   │  Актёр: *записывает текст на бумажку*       │           │
│   │         (onSaveInstanceState)               │           │
│   │                                             │           │
│   │  ... время проходит ...                     │           │
│   │                                             │           │
│   │  Актёр: *возвращается, читает бумажку*      │           │
│   │         (onCreate с Bundle)                 │           │
│   └─────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Аналогия 5: Process Death = Пожарная эвакуация

```
┌─────────────────────────────────────────────────────────────┐
│                    Пожарная эвакуация                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   iOS (Jetsam):                                             │
│   ┌─────────────────────────────────────────────┐           │
│   │  🔥 ПОЖАР! Все на выход! Немедленно!        │           │
│   │                                             │           │
│   │  Приложение: "Но я не успел сохранить..."   │           │
│   │  Система: "Неважно. Выход. Сейчас."         │           │
│   │                                             │           │
│   │  → Никакого callback                        │           │
│   │  → Данные потеряны (если не сохранены)      │           │
│   └─────────────────────────────────────────────┘           │
│                                                              │
│   Android (Low Memory Killer):                              │
│   ┌─────────────────────────────────────────────┐           │
│   │  ⚠️ Внимание! Возможна эвакуация!           │           │
│   │                                             │           │
│   │  Система: "У вас 5 минут. Соберите вещи     │           │
│   │           (onSaveInstanceState) и ждите."   │           │
│   │                                             │           │
│   │  Приложение: *сохраняет состояние*          │           │
│   │                                             │           │
│   │  ... позже ...                              │           │
│   │                                             │           │
│   │  Система: "Можете вернуться. Вот ваши       │           │
│   │           вещи (Bundle)."                   │           │
│   └─────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Детальное сравнение Lifecycle Callbacks

### iOS (UIViewController) — Полный цикл

```
┌─────────────────────────────────────────────────────────────┐
│              UIViewController Lifecycle                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                                                      │  │
│   │     init(coder:) / init(nibName:bundle:)            │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │              loadView()                              │  │
│   │              (создание view)                         │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │             viewDidLoad()                            │  │
│   │         (view загружен в память)                     │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │     ┌─────► viewWillAppear(_:)                      │  │
│   │     │       (view скоро появится)                    │  │
│   │     │              │                                 │  │
│   │     │              ▼                                 │  │
│   │     │       viewDidAppear(_:)                        │  │
│   │     │       (view на экране)                         │  │
│   │     │              │                                 │  │
│   │     │              ▼                                 │  │
│   │     │      viewWillDisappear(_:)                     │  │
│   │     │      (view скоро уйдёт)                        │  │
│   │     │              │                                 │  │
│   │     │              ▼                                 │  │
│   │     │      viewDidDisappear(_:)                      │  │
│   │     │      (view ушёл с экрана)                      │  │
│   │     │              │                                 │  │
│   │     └──────────────┘ (может повториться)             │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │               deinit                                 │  │
│   │          (освобождение памяти)                       │  │
│   │                                                      │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Примеры кода для каждого callback

```swift
import UIKit

class ProfileViewController: UIViewController {

    // MARK: - Properties

    private var userId: String
    private var profileData: ProfileData?
    private var isFirstAppearance = true

    // MARK: - Initialization

    /// Вызывается при создании контроллера программно
    /// Используется для: инициализации свойств, dependency injection
    init(userId: String) {
        self.userId = userId
        super.init(nibName: nil, bundle: nil)

        // ✅ Можно: инициализация свойств
        // ✅ Можно: настройка зависимостей
        // ❌ Нельзя: работа с UI (view ещё не существует)

        print("init: контроллер создан для userId: \(userId)")
    }

    required init?(coder: NSCoder) {
        self.userId = ""
        super.init(coder: coder)
    }

    // MARK: - View Lifecycle

    /// Вызывается ОДИН раз для создания view
    /// Используется для: кастомного создания view иерархии
    override func loadView() {
        // Если не переопределять — загрузится из Storyboard/XIB
        // или создастся пустой UIView

        let customView = ProfileView()
        self.view = customView

        // ✅ Можно: создание кастомной view иерархии
        // ❌ Нельзя: вызывать super.loadView() если создаём view сами

        print("loadView: view создан")
    }

    /// Вызывается ОДИН раз после загрузки view в память
    /// Используется для: начальной настройки UI, которая нужна один раз
    override func viewDidLoad() {
        super.viewDidLoad()

        // ✅ Настройка UI элементов
        setupNavigationBar()
        setupTableView()
        setupConstraints()

        // ✅ Настройка observers
        setupNotificationObservers()

        // ✅ Начальная загрузка данных (если не зависит от visibility)
        loadInitialData()

        // ❌ Не использовать для работы, которая зависит от размеров view
        // (bounds могут быть неправильными на этом этапе)

        print("viewDidLoad: начальная настройка завершена")
    }

    /// Вызывается КАЖДЫЙ раз перед появлением view на экране
    /// Используется для: обновления данных, подготовки к отображению
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)

        // ✅ Обновление данных
        refreshDataIfNeeded()

        // ✅ Настройка navigation bar
        navigationController?.setNavigationBarHidden(false, animated: animated)

        // ✅ Запуск анимаций, которые должны быть видны при появлении
        startAnimations()

        // ✅ Подписка на уведомления (если отписываемся в viewWillDisappear)
        subscribeToUpdates()

        print("viewWillAppear: подготовка к появлению")
    }

    /// Вызывается КАЖДЫЙ раз после появления view на экране
    /// Используется для: запуска аналитики, тяжёлых операций
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)

        // ✅ Аналитика просмотра экрана
        Analytics.trackScreenView("Profile")

        // ✅ Запуск тяжёлых операций (view уже на экране)
        if isFirstAppearance {
            loadHeavyContent()
            isFirstAppearance = false
        }

        // ✅ Показ диалогов, которые должны появиться после перехода
        showPendingAlerts()

        // ✅ Начало отслеживания геолокации, датчиков
        startLocationTracking()

        print("viewDidAppear: view полностью виден")
    }

    /// Вызывается КАЖДЫЙ раз перед уходом view с экрана
    /// Используется для: сохранения состояния, остановки операций
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)

        // ✅ Сохранение введённых данных
        saveDraftData()

        // ✅ Остановка операций, которые не нужны когда view не виден
        stopAnimations()

        // ✅ Скрытие клавиатуры
        view.endEditing(true)

        // ✅ Отписка от уведомлений (если подписываемся в viewWillAppear)
        unsubscribeFromUpdates()

        print("viewWillDisappear: подготовка к уходу")
    }

    /// Вызывается КАЖДЫЙ раз после ухода view с экрана
    /// Используется для: остановки ресурсоёмких операций
    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)

        // ✅ Остановка геолокации, датчиков
        stopLocationTracking()

        // ✅ Остановка видео/аудио
        pauseMediaPlayback()

        // ✅ Отмена сетевых запросов (если не нужны в фоне)
        cancelPendingRequests()

        print("viewDidDisappear: view полностью скрыт")
    }

    // MARK: - Memory Management

    /// Вызывается при освобождении контроллера
    /// НЕ ГАРАНТИРОВАН при process death!
    deinit {
        // ✅ Отписка от NotificationCenter
        NotificationCenter.default.removeObserver(self)

        // ✅ Отмена операций
        cancelAllOperations()

        // ✅ Освобождение ресурсов
        releaseResources()

        print("deinit: контроллер освобождён")
    }

    // MARK: - Private Methods

    private func setupNavigationBar() { /* ... */ }
    private func setupTableView() { /* ... */ }
    private func setupConstraints() { /* ... */ }
    private func setupNotificationObservers() { /* ... */ }
    private func loadInitialData() { /* ... */ }
    private func refreshDataIfNeeded() { /* ... */ }
    private func startAnimations() { /* ... */ }
    private func stopAnimations() { /* ... */ }
    private func subscribeToUpdates() { /* ... */ }
    private func unsubscribeFromUpdates() { /* ... */ }
    private func loadHeavyContent() { /* ... */ }
    private func showPendingAlerts() { /* ... */ }
    private func startLocationTracking() { /* ... */ }
    private func stopLocationTracking() { /* ... */ }
    private func saveDraftData() { /* ... */ }
    private func pauseMediaPlayback() { /* ... */ }
    private func cancelPendingRequests() { /* ... */ }
    private func cancelAllOperations() { /* ... */ }
    private func releaseResources() { /* ... */ }
}
```

### Android (Activity) — Полный цикл

```
┌─────────────────────────────────────────────────────────────┐
│                  Activity Lifecycle                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                                                      │  │
│   │            onCreate(Bundle?)                         │  │
│   │         (Activity создана)                           │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │     ┌─────►   onStart()                             │  │
│   │     │      (Activity видна)                          │  │
│   │     │              │                                 │  │
│   │     │              ▼                                 │  │
│   │     │   ┌─────► onResume()                          │  │
│   │     │   │    (Activity в фокусе)                     │  │
│   │     │   │          │                                 │  │
│   │     │   │          ▼                                 │  │
│   │     │   │     [RUNNING]                              │  │
│   │     │   │          │                                 │  │
│   │     │   │          ▼                                 │  │
│   │     │   │      onPause()                             │  │
│   │     │   │   (Activity теряет фокус)                  │  │
│   │     │   │          │                                 │  │
│   │     │   └──────────┘ (может вернуться в onResume)    │  │
│   │     │              │                                 │  │
│   │     │              ▼                                 │  │
│   │     │         onStop()                               │  │
│   │     │      (Activity не видна)                       │  │
│   │     │              │                                 │  │
│   │     └──────────────┘ (может вернуться через         │  │
│   │                       onRestart → onStart)           │  │
│   │                    │                                 │  │
│   │                    ├─── onSaveInstanceState() ───┐   │  │
│   │                    │    (сохранение состояния)   │   │  │
│   │                    ▼                             │   │  │
│   │              onDestroy()                         │   │  │
│   │         (Activity уничтожена)                    │   │  │
│   │                                                  │   │  │
│   │                    ИЛИ                           │   │  │
│   │                                                  ▼   │  │
│   │              [PROCESS KILLED]  ◄─────────────────┘   │  │
│   │              (система убила процесс)                 │  │
│   │                    │                                 │  │
│   │                    ▼                                 │  │
│   │            onCreate(Bundle) ◄── savedInstanceState   │  │
│   │            (восстановление)                          │  │
│   │                                                      │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Примеры кода для каждого callback

```kotlin
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.activity.viewModels

class ProfileActivity : AppCompatActivity() {

    // MARK: - Properties

    private val viewModel: ProfileViewModel by viewModels()
    private var userId: String = ""
    private var isFirstResume = true

    // MARK: - Lifecycle

    /**
     * Вызывается при создании Activity
     * - Первый запуск: savedInstanceState == null
     * - После process death: savedInstanceState содержит сохранённые данные
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        // Получаем данные из Intent (всегда доступны)
        userId = intent.getStringExtra("USER_ID") ?: ""

        // Проверяем: первый запуск или восстановление
        if (savedInstanceState == null) {
            // ✅ Первый запуск — инициализация
            Log.d(TAG, "onCreate: первый запуск")
            initializeNewSession()
        } else {
            // ✅ Восстановление после process death
            Log.d(TAG, "onCreate: восстановление после process death")
            restoreState(savedInstanceState)
        }

        // ✅ Настройка UI (всегда)
        setupViews()
        setupObservers()

        // ❌ Не делать здесь работу, зависящую от lifecycle
        // (observers сами обработают это в onStart/onResume)
    }

    /**
     * Вызывается когда Activity становится видимой
     * Используется для: запуска UI-связанных операций
     */
    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart: Activity видна")

        // ✅ Подключение к сервисам, которые нужны когда UI виден
        connectToService()

        // ✅ Регистрация BroadcastReceiver для UI-обновлений
        registerReceivers()

        // ✅ Запуск наблюдения за LiveData/Flow
        // (если не используется lifecycle-aware observers)
        startObserving()
    }

    /**
     * Вызывается когда Activity получает фокус
     * Используется для: запуска операций, требующих взаимодействия
     */
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume: Activity в фокусе")

        // ✅ Обновление данных
        refreshData()

        // ✅ Запуск анимаций
        startAnimations()

        // ✅ Запуск отслеживания (геолокация, датчики)
        startTracking()

        // ✅ Аналитика (первое появление)
        if (isFirstResume) {
            Analytics.trackScreenView("Profile")
            isFirstResume = false
        }

        // ✅ Возобновление воспроизведения медиа
        resumeMediaPlayback()
    }

    /**
     * Вызывается когда Activity теряет фокус
     * Используется для: сохранения состояния, приостановки операций
     */
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause: Activity теряет фокус")

        // ✅ Приостановка анимаций
        pauseAnimations()

        // ✅ Сохранение черновика
        saveDraft()

        // ✅ Приостановка отслеживания
        pauseTracking()

        // ✅ Приостановка воспроизведения медиа
        pauseMediaPlayback()

        // ВАЖНО: onPause должен быть быстрым!
        // Следующая Activity ждёт завершения onPause
    }

    /**
     * Вызывается когда Activity становится невидимой
     * Используется для: освобождения ресурсов, не нужных в фоне
     */
    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop: Activity не видна")

        // ✅ Отключение от сервисов
        disconnectFromService()

        // ✅ Отмена регистрации BroadcastReceiver
        unregisterReceivers()

        // ✅ Остановка наблюдения
        stopObserving()

        // ✅ Освобождение ресурсов, связанных с UI
        releaseUIResources()
    }

    /**
     * КРИТИЧЕСКИ ВАЖНО: Сохранение состояния перед возможной смертью
     * Вызывается ПЕРЕД onStop() (на API 28+) или ПОСЛЕ onStop() (до API 28)
     */
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        Log.d(TAG, "onSaveInstanceState: сохранение состояния")

        // ✅ Сохраняем UI состояние
        outState.putString(KEY_USER_ID, userId)
        outState.putInt(KEY_SCROLL_POSITION, getScrollPosition())
        outState.putString(KEY_DRAFT_TEXT, getDraftText())
        outState.putBoolean(KEY_IS_EDITING, isEditing())

        // ✅ Для сложных объектов используем Parcelable
        outState.putParcelable(KEY_FORM_STATE, formState)

        // ВАЖНО: Bundle имеет ограничение ~1MB!
        // Для больших данных используйте ViewModel + SavedStateHandle
    }

    /**
     * Вызывается при уничтожении Activity
     * НЕ ГАРАНТИРОВАН при process death!
     */
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy: Activity уничтожена")

        // Проверяем причину уничтожения
        if (isFinishing) {
            // ✅ Пользователь закрыл Activity (finish() или back)
            cleanupPermanently()
        } else {
            // ✅ Конфигурация изменилась (поворот экрана)
            // или система уничтожает для освобождения памяти
            cleanupTemporarily()
        }

        // ✅ Освобождение ресурсов
        releaseResources()
    }

    // MARK: - State Restoration

    private fun restoreState(savedInstanceState: Bundle) {
        userId = savedInstanceState.getString(KEY_USER_ID, "")
        val scrollPosition = savedInstanceState.getInt(KEY_SCROLL_POSITION, 0)
        val draftText = savedInstanceState.getString(KEY_DRAFT_TEXT, "")
        val isEditing = savedInstanceState.getBoolean(KEY_IS_EDITING, false)

        // Восстанавливаем UI состояние
        restoreScrollPosition(scrollPosition)
        restoreDraftText(draftText)
        if (isEditing) enterEditMode()
    }

    // MARK: - Private Methods

    private fun initializeNewSession() { /* ... */ }
    private fun setupViews() { /* ... */ }
    private fun setupObservers() { /* ... */ }
    private fun connectToService() { /* ... */ }
    private fun disconnectFromService() { /* ... */ }
    private fun registerReceivers() { /* ... */ }
    private fun unregisterReceivers() { /* ... */ }
    private fun startObserving() { /* ... */ }
    private fun stopObserving() { /* ... */ }
    private fun refreshData() { /* ... */ }
    private fun startAnimations() { /* ... */ }
    private fun pauseAnimations() { /* ... */ }
    private fun startTracking() { /* ... */ }
    private fun pauseTracking() { /* ... */ }
    private fun saveDraft() { /* ... */ }
    private fun resumeMediaPlayback() { /* ... */ }
    private fun pauseMediaPlayback() { /* ... */ }
    private fun releaseUIResources() { /* ... */ }
    private fun cleanupPermanently() { /* ... */ }
    private fun cleanupTemporarily() { /* ... */ }
    private fun releaseResources() { /* ... */ }
    private fun getScrollPosition(): Int = 0
    private fun getDraftText(): String = ""
    private fun isEditing(): Boolean = false
    private fun restoreScrollPosition(position: Int) { /* ... */ }
    private fun restoreDraftText(text: String) { /* ... */ }
    private fun enterEditMode() { /* ... */ }

    companion object {
        private const val TAG = "ProfileActivity"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_DRAFT_TEXT = "draft_text"
        private const val KEY_IS_EDITING = "is_editing"
        private const val KEY_FORM_STATE = "form_state"
    }
}
```

### Fragment Lifecycle (дополнительно)

```
┌─────────────────────────────────────────────────────────────┐
│                   Fragment Lifecycle                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   onAttach(context) ─────► Привязка к Activity              │
│         │                                                    │
│         ▼                                                    │
│   onCreate(Bundle?) ─────► Создание Fragment                │
│         │                                                    │
│         ▼                                                    │
│   onCreateView() ────────► Создание View                    │
│         │                                                    │
│         ▼                                                    │
│   onViewCreated() ───────► View создан                      │
│         │                                                    │
│         ▼                                                    │
│   onStart() ─────────────► Fragment виден                   │
│         │                                                    │
│         ▼                                                    │
│   onResume() ────────────► Fragment в фокусе                │
│         │                                                    │
│        ...                                                   │
│         │                                                    │
│         ▼                                                    │
│   onPause() ─────────────► Потеря фокуса                    │
│         │                                                    │
│         ▼                                                    │
│   onStop() ──────────────► Не виден                         │
│         │                                                    │
│         ▼                                                    │
│   onDestroyView() ───────► View уничтожен                   │
│         │                                                    │
│         ▼                                                    │
│   onDestroy() ───────────► Fragment уничтожен               │
│         │                                                    │
│         ▼                                                    │
│   onDetach() ────────────► Отвязка от Activity              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Ключевое различие: Process Death

### Что такое Process Death?

**Process Death** — это ситуация, когда операционная система убивает процесс приложения для освобождения памяти. Это фундаментальное различие между iOS и Android.

```
┌─────────────────────────────────────────────────────────────┐
│              Process Death: iOS vs Android                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   iOS (Jetsam):                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   Active ──► Background ──► Suspended ──► KILLED    │   │
│   │     │           │              │            │       │   │
│   │     │       ~30 секунд     Заморожен    Нет        │   │
│   │     │       на завершение  (нет кода)   callback!  │   │
│   │     │       работы                                  │   │
│   │     │                                               │   │
│   │     └─── applicationWillResignActive               │   │
│   │     └─── applicationDidEnterBackground             │   │
│   │                                                     │   │
│   │   При возврате: Полный перезапуск приложения       │   │
│   │   (application:didFinishLaunchingWithOptions:)     │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Android (Low Memory Killer / OOM Killer):                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   Resumed ──► Paused ──► Stopped ──► KILLED         │   │
│   │      │          │          │           │            │   │
│   │      │      onPause    onStop    onSaveInstance     │   │
│   │      │                    │        State            │   │
│   │      │                    │           │             │   │
│   │      │                    │           ▼             │   │
│   │      │                    │       Bundle            │   │
│   │      │                    │       сохранён          │   │
│   │      │                    │                         │   │
│   │   При возврате: onCreate(savedInstanceState)        │   │
│   │   (Activity пересоздаётся с Bundle)                 │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Сценарий Process Death

```
┌─────────────────────────────────────────────────────────────┐
│          Типичный сценарий Process Death                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Время    iOS                        Android                │
│   ─────────────────────────────────────────────────────────  │
│                                                              │
│   T+0      Пользователь               Пользователь           │
│            заполняет форму            заполняет форму        │
│                                                              │
│   T+1      Переключается              Переключается          │
│            на другое приложение       на другое приложение   │
│                                                              │
│   T+2      viewWillDisappear          onPause                │
│            viewDidDisappear           onStop                 │
│                                       onSaveInstanceState    │
│                                       ✅ Bundle сохранён     │
│                                                              │
│   T+3      applicationDidEnter        Activity в Stopped     │
│            Background                                        │
│                                                              │
│   T+10     Suspended                  Система решает         │
│            (код не выполняется)       освободить память      │
│                                                              │
│   T+30     Система освобождает        ❌ Процесс убит        │
│            память (jetsam)                                   │
│            ❌ Процесс убит                                   │
│            ❌ Нет callback!                                  │
│                                                              │
│   T+60     Пользователь               Пользователь           │
│            возвращается               возвращается           │
│                                                              │
│   T+61     ❌ Данные формы            ✅ onCreate(Bundle)    │
│               потеряны!                  Данные               │
│            ❌ Приложение                 восстановлены!      │
│               перезапускается                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Как симулировать Process Death

```swift
// iOS: Симуляция через Xcode
// 1. Запустите приложение
// 2. Нажмите Home (background)
// 3. В Xcode: Debug → Simulate Memory Warning
// 4. Или: Terminate приложение вручную

// Или программно (только для тестирования):
// exit(0) - НЕ РЕКОМЕНДУЕТСЯ, нарушает правила App Store
```

```kotlin
// Android: Симуляция через ADB
// Терминал:
// adb shell am kill com.example.app

// Или через Android Studio:
// 1. Запустите приложение
// 2. Нажмите Home
// 3. В Logcat найдите процесс и нажмите "X" (Terminate)

// Или программно (только для тестирования):
class DebugActivity : AppCompatActivity() {
    fun simulateProcessDeath() {
        // Сохраняем состояние вручную
        onSaveInstanceState(Bundle())

        // Убиваем процесс
        android.os.Process.killProcess(android.os.Process.myPid())
    }
}
```

### Последствия Process Death

```
┌─────────────────────────────────────────────────────────────┐
│            Что теряется при Process Death                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   iOS:                                                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  ❌ ВСЁ состояние в памяти                          │   │
│   │  ❌ Все view controller'ы                           │   │
│   │  ❌ Navigation stack                                │   │
│   │  ❌ Введённые данные (если не сохранены)            │   │
│   │  ❌ In-memory cache                                 │   │
│   │  ❌ Активные сетевые запросы                        │   │
│   │                                                     │   │
│   │  ✅ UserDefaults сохраняется                        │   │
│   │  ✅ Keychain сохраняется                            │   │
│   │  ✅ Core Data / Files сохраняются                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Android:                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  ❌ Все объекты в памяти                            │   │
│   │  ❌ ViewModel (если не SavedStateHandle)            │   │
│   │  ❌ Singletons                                      │   │
│   │  ❌ In-memory cache                                 │   │
│   │  ❌ Активные coroutines                             │   │
│   │                                                     │   │
│   │  ✅ Bundle из onSaveInstanceState                   │   │
│   │  ✅ SharedPreferences                               │   │
│   │  ✅ Room / SQLite                                   │   │
│   │  ✅ Files                                           │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## State Restoration

### iOS: Подходы к восстановлению состояния

#### 1. NSCoding / Codable + UserDefaults

```swift
// Модель данных
struct FormState: Codable {
    var name: String
    var email: String
    var selectedOption: Int
    var scrollPosition: CGFloat
}

class FormViewController: UIViewController {

    private var formState = FormState(
        name: "",
        email: "",
        selectedOption: 0,
        scrollPosition: 0
    )

    private let stateKey = "FormViewController.formState"

    override func viewDidLoad() {
        super.viewDidLoad()

        // Восстанавливаем состояние при загрузке
        restoreState()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)

        // Сохраняем состояние при уходе
        saveState()
    }

    // MARK: - State Persistence

    private func saveState() {
        // Обновляем formState из UI
        formState.name = nameTextField.text ?? ""
        formState.email = emailTextField.text ?? ""
        formState.scrollPosition = scrollView.contentOffset.y

        // Сохраняем в UserDefaults
        if let encoded = try? JSONEncoder().encode(formState) {
            UserDefaults.standard.set(encoded, forKey: stateKey)
        }
    }

    private func restoreState() {
        // Загружаем из UserDefaults
        if let data = UserDefaults.standard.data(forKey: stateKey),
           let decoded = try? JSONDecoder().decode(FormState.self, from: data) {
            formState = decoded

            // Восстанавливаем UI
            nameTextField.text = formState.name
            emailTextField.text = formState.email
            scrollView.contentOffset.y = formState.scrollPosition
        }
    }

    private func clearState() {
        // Очищаем после успешной отправки
        UserDefaults.standard.removeObject(forKey: stateKey)
    }
}
```

#### 2. @AppStorage (SwiftUI)

```swift
import SwiftUI

struct FormView: View {
    // Автоматически синхронизируется с UserDefaults
    @AppStorage("form_name") private var name: String = ""
    @AppStorage("form_email") private var email: String = ""
    @AppStorage("form_option") private var selectedOption: Int = 0

    var body: some View {
        Form {
            Section("Личные данные") {
                TextField("Имя", text: $name)
                TextField("Email", text: $email)
            }

            Section("Настройки") {
                Picker("Опция", selection: $selectedOption) {
                    Text("Опция 1").tag(0)
                    Text("Опция 2").tag(1)
                    Text("Опция 3").tag(2)
                }
            }

            Button("Отправить") {
                submitForm()
            }
        }
    }

    private func submitForm() {
        // После отправки очищаем
        name = ""
        email = ""
        selectedOption = 0
    }
}
```

#### 3. SceneDelegate / Scene Storage (iOS 13+)

```swift
// SceneDelegate.swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {

        // Восстанавливаем состояние из userActivity
        if let userActivity = connectionOptions.userActivities.first {
            restoreState(from: userActivity)
        }
    }

    func stateRestorationActivity(for scene: UIScene) -> NSUserActivity? {
        // Создаём userActivity для сохранения состояния
        let activity = NSUserActivity(activityType: "com.app.viewingProfile")

        // Сохраняем данные
        activity.userInfo = [
            "currentTab": getCurrentTabIndex(),
            "profileId": getCurrentProfileId(),
            "scrollPosition": getScrollPosition()
        ]

        return activity
    }

    private func restoreState(from activity: NSUserActivity) {
        guard let userInfo = activity.userInfo else { return }

        if let tabIndex = userInfo["currentTab"] as? Int {
            selectTab(tabIndex)
        }

        if let profileId = userInfo["profileId"] as? String {
            navigateToProfile(profileId)
        }
    }
}
```

```swift
// SwiftUI: @SceneStorage
struct ContentView: View {
    // Сохраняется автоматически при уходе в background
    @SceneStorage("selectedTab") private var selectedTab: Int = 0
    @SceneStorage("searchQuery") private var searchQuery: String = ""

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tag(0)

            SearchView(query: $searchQuery)
                .tag(1)

            ProfileView()
                .tag(2)
        }
    }
}
```

### Android: Подходы к восстановлению состояния

#### 1. onSaveInstanceState + onCreate

```kotlin
class FormActivity : AppCompatActivity() {

    private var name: String = ""
    private var email: String = ""
    private var selectedOption: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // Восстанавливаем состояние
        savedInstanceState?.let { bundle ->
            name = bundle.getString(KEY_NAME, "")
            email = bundle.getString(KEY_EMAIL, "")
            selectedOption = bundle.getInt(KEY_OPTION, 0)

            // Восстанавливаем UI
            binding.nameEditText.setText(name)
            binding.emailEditText.setText(email)
            binding.optionSpinner.setSelection(selectedOption)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Сохраняем текущее состояние
        outState.putString(KEY_NAME, binding.nameEditText.text.toString())
        outState.putString(KEY_EMAIL, binding.emailEditText.text.toString())
        outState.putInt(KEY_OPTION, binding.optionSpinner.selectedItemPosition)
    }

    companion object {
        private const val KEY_NAME = "name"
        private const val KEY_EMAIL = "email"
        private const val KEY_OPTION = "option"
    }
}
```

#### 2. SavedStateHandle в ViewModel

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Автоматически сохраняется и восстанавливается
    val name: MutableStateFlow<String> = savedStateHandle.getStateFlow(KEY_NAME, "")
    val email: MutableStateFlow<String> = savedStateHandle.getStateFlow(KEY_EMAIL, "")
    val selectedOption: MutableStateFlow<Int> = savedStateHandle.getStateFlow(KEY_OPTION, 0)

    fun updateName(value: String) {
        savedStateHandle[KEY_NAME] = value
    }

    fun updateEmail(value: String) {
        savedStateHandle[KEY_EMAIL] = value
    }

    fun updateOption(value: Int) {
        savedStateHandle[KEY_OPTION] = value
    }

    fun clearState() {
        savedStateHandle[KEY_NAME] = ""
        savedStateHandle[KEY_EMAIL] = ""
        savedStateHandle[KEY_OPTION] = 0
    }

    companion object {
        private const val KEY_NAME = "name"
        private const val KEY_EMAIL = "email"
        private const val KEY_OPTION = "option"
    }
}

// Использование в Activity/Fragment
class FormFragment : Fragment() {

    private val viewModel: FormViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Состояние автоматически восстанавливается через ViewModel
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.name.collect { name ->
                if (binding.nameEditText.text.toString() != name) {
                    binding.nameEditText.setText(name)
                }
            }
        }

        // Сохраняем изменения
        binding.nameEditText.doAfterTextChanged { text ->
            viewModel.updateName(text.toString())
        }
    }
}
```

#### 3. Jetpack Compose: rememberSaveable

```kotlin
@Composable
fun FormScreen() {
    // Автоматически сохраняется при configuration change и process death
    var name by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    var selectedOption by rememberSaveable { mutableStateOf(0) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Имя") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Для сложных объектов нужен кастомный Saver
        val formState by rememberSaveable(
            saver = FormStateSaver
        ) {
            mutableStateOf(FormState())
        }
    }
}

// Кастомный Saver для сложных объектов
@Parcelize
data class FormState(
    val items: List<String> = emptyList(),
    val selectedIds: Set<Int> = emptySet()
) : Parcelable

val FormStateSaver = Saver<MutableState<FormState>, FormState>(
    save = { it.value },
    restore = { mutableStateOf(it) }
)
```

### Сравнение подходов

```
┌─────────────────────────────────────────────────────────────┐
│           Сравнение методов State Restoration                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Метод              iOS                  Android            │
│   ─────────────────────────────────────────────────────────  │
│                                                              │
│   Простые            @AppStorage          rememberSaveable   │
│   значения           UserDefaults         SavedStateHandle   │
│                                                              │
│   Сложные            Codable +            Parcelable +       │
│   объекты            UserDefaults         Bundle             │
│                                                              │
│   Scene-уровень      @SceneStorage        Navigation +       │
│   состояние          NSUserActivity       SavedStateHandle   │
│                                                              │
│   Navigation         NavigationPath       NavController      │
│   stack              + Codable            + SavedState       │
│                                                              │
│   Ограничения        Нет жёстких          Bundle ~1MB        │
│   размера            (но разумно)         (Transaction       │
│                                           TooLargeException) │
│                                                              │
│   Когда              Вручную в            Автоматически      │
│   сохраняется        viewWillDisappear    в onSaveInstance   │
│                      / background         State              │
│                                                              │
│   Гарантия           Нет (jetsam)         Да (если не        │
│   вызова                                  finish())          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## KMP Approach: Кросс-платформенное управление Lifecycle

### Common ViewModel с expect/actual

```kotlin
// commonMain/src/commonMain/kotlin/ViewModel.kt

// Абстрактный базовый класс для ViewModel
expect abstract class PlatformViewModel() {
    // Вызывается при уничтожении ViewModel
    protected open fun onCleared()
}

// Общая реализация бизнес-логики
class ProfileViewModel : PlatformViewModel() {

    private val _state = MutableStateFlow(ProfileState())
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    private var loadingJob: Job? = null

    fun loadProfile(userId: String) {
        loadingJob?.cancel()
        loadingJob = viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }

            try {
                val profile = profileRepository.getProfile(userId)
                _state.update {
                    it.copy(isLoading = false, profile = profile)
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(isLoading = false, error = e.message)
                }
            }
        }
    }

    override fun onCleared() {
        loadingJob?.cancel()
    }
}

data class ProfileState(
    val isLoading: Boolean = false,
    val profile: Profile? = null,
    val error: String? = null
)
```

```kotlin
// androidMain/src/androidMain/kotlin/ViewModel.android.kt

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

actual abstract class PlatformViewModel : ViewModel() {

    // Используем Android viewModelScope
    protected actual val viewModelScope: CoroutineScope
        get() = (this as ViewModel).viewModelScope

    actual override fun onCleared() {
        super.onCleared()
    }
}
```

```swift
// iosMain/src/iosMain/kotlin/ViewModel.ios.kt

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel

actual abstract class PlatformViewModel {

    private val job = SupervisorJob()
    protected actual val viewModelScope: CoroutineScope =
        CoroutineScope(Dispatchers.Main + job)

    fun clear() {
        onCleared()
        viewModelScope.cancel()
    }

    protected actual open fun onCleared() {}
}
```

### Essenty: Общий Lifecycle для KMP

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.arkivanov.essenty:lifecycle:2.0.0")
    implementation("com.arkivanov.essenty:state-keeper:2.0.0")
    implementation("com.arkivanov.essenty:instance-keeper:2.0.0")
}
```

```kotlin
// commonMain - Использование Essenty Lifecycle
import com.arkivanov.essenty.lifecycle.Lifecycle
import com.arkivanov.essenty.lifecycle.LifecycleOwner
import com.arkivanov.essenty.lifecycle.doOnDestroy
import com.arkivanov.essenty.lifecycle.doOnStart
import com.arkivanov.essenty.lifecycle.doOnStop

class ProfileComponent(
    componentContext: ComponentContext
) : ComponentContext by componentContext {

    private val _state = MutableStateFlow(ProfileState())
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    init {
        // Подписываемся на lifecycle события
        lifecycle.doOnStart {
            startObservingData()
        }

        lifecycle.doOnStop {
            stopObservingData()
        }

        lifecycle.doOnDestroy {
            cleanup()
        }
    }

    private fun startObservingData() {
        // Запускаем наблюдение при старте
    }

    private fun stopObservingData() {
        // Останавливаем при стопе
    }

    private fun cleanup() {
        // Финальная очистка
    }
}
```

```kotlin
// State Keeper для сохранения состояния
import com.arkivanov.essenty.statekeeper.StateKeeper
import com.arkivanov.essenty.statekeeper.consume
import com.arkivanov.essenty.statekeeper.register

class FormComponent(
    componentContext: ComponentContext
) : ComponentContext by componentContext {

    // Восстанавливаем состояние
    private val savedState: FormState? = stateKeeper.consume(KEY_STATE)

    private val _state = MutableStateFlow(
        savedState ?: FormState()
    )
    val state: StateFlow<FormState> = _state.asStateFlow()

    init {
        // Регистрируем для сохранения
        stateKeeper.register(KEY_STATE) {
            _state.value
        }
    }

    companion object {
        private const val KEY_STATE = "FormState"
    }
}

@Serializable
data class FormState(
    val name: String = "",
    val email: String = "",
    val selectedOption: Int = 0
)
```

```kotlin
// Instance Keeper для сохранения экземпляров
import com.arkivanov.essenty.instancekeeper.InstanceKeeper
import com.arkivanov.essenty.instancekeeper.getOrCreate

class MainComponent(
    componentContext: ComponentContext
) : ComponentContext by componentContext {

    // ViewModel выживает configuration changes (аналог Android ViewModel)
    private val viewModel = instanceKeeper.getOrCreate {
        MainViewModel()
    }

    val state: StateFlow<MainState> = viewModel.state
}

class MainViewModel : InstanceKeeper.Instance {

    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    private val _state = MutableStateFlow(MainState())
    val state: StateFlow<MainState> = _state.asStateFlow()

    override fun onDestroy() {
        scope.cancel()
    }
}
```

### Интеграция с платформами

```swift
// iOS: Использование KMP компонента
import SharedModule

class ProfileViewController: UIViewController {

    private var component: ProfileComponent!
    private var lifecycle: LifecycleRegistry!
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()

        // Создаём lifecycle
        lifecycle = LifecycleRegistryKt.LifecycleRegistry()

        // Создаём компонент
        component = ProfileComponent(
            componentContext: DefaultComponentContext(lifecycle: lifecycle)
        )

        // Подписываемся на состояние
        component.state
            .sink { [weak self] state in
                self?.updateUI(with: state)
            }
            .store(in: &cancellables)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        lifecycle.resume()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        lifecycle.stop()
    }

    deinit {
        lifecycle.destroy()
    }
}
```

```kotlin
// Android: Использование KMP компонента
class ProfileActivity : AppCompatActivity() {

    private val component by lazy {
        ProfileComponent(
            componentContext = defaultComponentContext()
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            val state by component.state.collectAsState()

            ProfileScreen(
                state = state,
                onRefresh = { component.refresh() }
            )
        }
    }
}

// Extension для создания ComponentContext
fun AppCompatActivity.defaultComponentContext(): ComponentContext {
    return DefaultComponentContext(
        lifecycle = essentyLifecycle(),
        stateKeeper = stateKeeper(),
        instanceKeeper = instanceKeeper()
    )
}
```

---

## 6 типичных ошибок

### Ошибка 1: Тяжёлая работа в viewDidLoad (iOS)

```swift
// ❌ НЕПРАВИЛЬНО: Блокируем main thread
class ProfileViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Синхронная загрузка данных — UI зависнет!
        let data = try! Data(contentsOf: largeFileURL)
        let profile = try! JSONDecoder().decode(Profile.self, from: data)

        // Синхронная загрузка изображения
        let imageData = try! Data(contentsOf: avatarURL)
        avatarImageView.image = UIImage(data: imageData)

        // Сложные вычисления
        let processedData = heavyComputation(profile.data)
        setupUI(with: processedData)
    }
}

// ✅ ПРАВИЛЬНО: Асинхронная загрузка
class ProfileViewController: UIViewController {

    private var loadingTask: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Быстрая настройка UI
        setupSkeletonUI()

        // Асинхронная загрузка
        loadingTask = Task { @MainActor in
            do {
                // Показываем loading state
                showLoadingState()

                // Загружаем данные асинхронно
                let profile = try await profileService.loadProfile()

                // Загружаем изображение асинхронно
                let avatarImage = try await imageLoader.load(profile.avatarURL)

                // Обновляем UI на main thread
                updateUI(with: profile, avatar: avatarImage)

            } catch {
                showError(error)
            }
        }
    }

    deinit {
        loadingTask?.cancel()
    }
}
```

### Ошибка 2: Игнорирование Process Death (Android)

```kotlin
// ❌ НЕПРАВИЛЬНО: Состояние теряется при process death
class FormActivity : AppCompatActivity() {

    // Данные хранятся только в памяти
    private var formData = FormData()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // После process death formData будет пустым!
        setupUI()
    }

    private fun onTextChanged(text: String) {
        formData.name = text
        // Данные потеряются при process death
    }
}

// ✅ ПРАВИЛЬНО: Сохраняем состояние
class FormActivity : AppCompatActivity() {

    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewModel с SavedStateHandle выживет process death
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                updateUI(state)
            }
        }
    }
}

class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Автоматически сохраняется и восстанавливается
    val name = savedStateHandle.getStateFlow("name", "")
    val email = savedStateHandle.getStateFlow("email", "")

    fun updateName(value: String) {
        savedStateHandle["name"] = value
    }
}
```

### Ошибка 3: Ожидание вызова deinit/onDestroy

```swift
// ❌ НЕПРАВИЛЬНО: Критическая логика в deinit
class UploadViewController: UIViewController {

    private var uploadProgress: Float = 0

    deinit {
        // ⚠️ Этот код может НИКОГДА не выполниться!
        // - Process death (jetsam)
        // - Retain cycle
        // - Force quit приложения

        saveUploadProgress()
        uploadAnalytics()
        cleanupTempFiles()
    }
}

// ✅ ПРАВИЛЬНО: Сохраняем состояние регулярно
class UploadViewController: UIViewController {

    private var uploadProgress: Float = 0 {
        didSet {
            // Сохраняем прогресс при каждом изменении
            UserDefaults.standard.set(uploadProgress, forKey: "uploadProgress")
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)

        // Сохраняем состояние при уходе с экрана
        saveCompleteState()
    }

    func applicationWillResignActive() {
        // Сохраняем при уходе в background
        saveCompleteState()
    }

    deinit {
        // Только лёгкая очистка
        cancelUploadIfNeeded()
    }
}
```

```kotlin
// ❌ НЕПРАВИЛЬНО: Критическая логика в onDestroy
class UploadActivity : AppCompatActivity() {

    override fun onDestroy() {
        super.onDestroy()

        // ⚠️ НЕ ВЫЗОВЕТСЯ при process death!
        saveProgress()
        sendAnalytics()
        cleanupFiles()
    }
}

// ✅ ПРАВИЛЬНО: Сохраняем в onSaveInstanceState и onStop
class UploadActivity : AppCompatActivity() {

    override fun onStop() {
        super.onStop()
        // Сохраняем при каждом onStop (вызывается перед process death)
        saveProgress()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохраняем UI состояние
        outState.putFloat("progress", uploadProgress)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Только лёгкая очистка
        if (isFinishing) {
            cancelUpload()
        }
    }
}
```

### Ошибка 4: Memory Leaks из-за Lifecycle Mismatch

```swift
// ❌ НЕПРАВИЛЬНО: Strong reference в closure
class ChatViewController: UIViewController {

    private var messageHandler: MessageHandler?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Strong reference на self — утечка памяти!
        messageHandler = MessageHandler { message in
            self.displayMessage(message)  // ← Retain cycle!
        }

        // Подписка без отписки
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleNotification),
            name: .newMessage,
            object: nil
        )
        // ← Забыли removeObserver в deinit
    }
}

// ✅ ПРАВИЛЬНО: Weak reference и cleanup
class ChatViewController: UIViewController {

    private var messageHandler: MessageHandler?
    private var notificationToken: NSObjectProtocol?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Weak reference — нет утечки
        messageHandler = MessageHandler { [weak self] message in
            self?.displayMessage(message)
        }

        // Сохраняем token для отписки
        notificationToken = NotificationCenter.default.addObserver(
            forName: .newMessage,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            self?.handleNotification(notification)
        }
    }

    deinit {
        // Явная отписка
        if let token = notificationToken {
            NotificationCenter.default.removeObserver(token)
        }
    }
}
```

```kotlin
// ❌ НЕПРАВИЛЬНО: Утечка Activity через listener
class ChatActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Activity утекает через static handler!
        MessageService.addListener(object : MessageListener {
            override fun onMessage(message: Message) {
                displayMessage(message)  // ← Implicit reference to Activity
            }
        })
    }

    // Забыли removeListener в onDestroy
}

// ✅ ПРАВИЛЬНО: Lifecycle-aware components
class ChatActivity : AppCompatActivity() {

    private val messageObserver = object : MessageListener {
        override fun onMessage(message: Message) {
            displayMessage(message)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Используем lifecycle-aware подписку
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                MessageService.addListener(messageObserver)
            }

            override fun onStop(owner: LifecycleOwner) {
                MessageService.removeListener(messageObserver)
            }
        })
    }
}

// Ещё лучше: использовать Flow + repeatOnLifecycle
class ChatActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Автоматически отписывается при STOPPED
                messageService.messages.collect { message ->
                    displayMessage(message)
                }
            }
        }
    }
}
```

### Ошибка 5: Неправильный callback для инициализации

```swift
// ❌ НЕПРАВИЛЬНО: Работа с bounds в viewDidLoad
class ChartViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Bounds могут быть неправильными!
        // Auto Layout ещё не отработал
        let chartWidth = view.bounds.width
        let chartHeight = view.bounds.height

        setupChart(width: chartWidth, height: chartHeight)
    }
}

// ✅ ПРАВИЛЬНО: Используем viewDidLayoutSubviews
class ChartViewController: UIViewController {

    private var chartConfigured = false

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()

        // Bounds теперь корректные
        if !chartConfigured {
            let chartWidth = view.bounds.width
            let chartHeight = view.bounds.height

            setupChart(width: chartWidth, height: chartHeight)
            chartConfigured = true
        }
    }

    override func viewWillTransition(
        to size: CGSize,
        with coordinator: UIViewControllerTransitionCoordinator
    ) {
        super.viewWillTransition(to: size, with: coordinator)

        coordinator.animate { _ in
            // Перенастраиваем при rotation
            self.reconfigureChart(for: size)
        }
    }
}
```

```kotlin
// ❌ НЕПРАВИЛЬНО: Работа с размерами в onCreate
class ChartActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chart)

        // Размеры ещё не определены!
        val chartWidth = binding.chartContainer.width  // = 0
        val chartHeight = binding.chartContainer.height  // = 0

        setupChart(chartWidth, chartHeight)
    }
}

// ✅ ПРАВИЛЬНО: Используем ViewTreeObserver или doOnLayout
class ChartActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chart)

        // Вариант 1: doOnLayout
        binding.chartContainer.doOnLayout { view ->
            setupChart(view.width, view.height)
        }

        // Вариант 2: ViewTreeObserver (для сложных случаев)
        binding.chartContainer.viewTreeObserver.addOnGlobalLayoutListener(
            object : ViewTreeObserver.OnGlobalLayoutListener {
                override fun onGlobalLayout() {
                    binding.chartContainer.viewTreeObserver
                        .removeOnGlobalLayoutListener(this)

                    setupChart(
                        binding.chartContainer.width,
                        binding.chartContainer.height
                    )
                }
            }
        )
    }
}
```

### Ошибка 6: Игнорирование Lifecycle-aware компонентов

```kotlin
// ❌ НЕПРАВИЛЬНО: Ручное управление подписками
class LocationActivity : AppCompatActivity() {

    private var locationClient: FusedLocationProviderClient? = null
    private var locationCallback: LocationCallback? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        locationClient = LocationServices.getFusedLocationProviderClient(this)

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                updateLocation(result.lastLocation)
            }
        }
    }

    override fun onStart() {
        super.onStart()
        // Забыли проверить permissions
        locationClient?.requestLocationUpdates(
            locationRequest,
            locationCallback!!,
            Looper.getMainLooper()
        )
    }

    override fun onStop() {
        super.onStop()
        // Можем забыть вызвать это
        locationClient?.removeLocationUpdates(locationCallback!!)
    }

    // При process death — locationCallback становится null после восстановления
    // Краш при попытке removeLocationUpdates!
}

// ✅ ПРАВИЛЬНО: Lifecycle-aware компоненты
class LocationActivity : AppCompatActivity() {

    private val locationObserver = LocationLifecycleObserver()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Регистрируем lifecycle-aware observer
        lifecycle.addObserver(locationObserver)

        // Подписываемся на обновления
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                locationObserver.locationFlow.collect { location ->
                    updateLocation(location)
                }
            }
        }
    }
}

class LocationLifecycleObserver : DefaultLifecycleObserver {

    private var locationClient: FusedLocationProviderClient? = null
    private var locationCallback: LocationCallback? = null

    private val _locationFlow = MutableSharedFlow<Location>()
    val locationFlow: SharedFlow<Location> = _locationFlow.asSharedFlow()

    override fun onStart(owner: LifecycleOwner) {
        val context = (owner as? ComponentActivity)?.applicationContext ?: return

        locationClient = LocationServices.getFusedLocationProviderClient(context)

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { location ->
                    _locationFlow.tryEmit(location)
                }
            }
        }

        startLocationUpdates()
    }

    override fun onStop(owner: LifecycleOwner) {
        stopLocationUpdates()
        locationCallback = null
    }

    private fun startLocationUpdates() {
        locationCallback?.let { callback ->
            locationClient?.requestLocationUpdates(
                createLocationRequest(),
                callback,
                Looper.getMainLooper()
            )
        }
    }

    private fun stopLocationUpdates() {
        locationCallback?.let { callback ->
            locationClient?.removeLocationUpdates(callback)
        }
    }
}
```

---

## Ментальные модели

### iOS: "Я контролирую свою смерть"

```
┌─────────────────────────────────────────────────────────────┐
│              iOS Mental Model: Self-Control                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   UIViewController думает:                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   "Я знаю, когда появлюсь на экране"               │   │
│   │   "Я знаю, когда уйду с экрана"                    │   │
│   │   "Я контролирую свой жизненный цикл"              │   │
│   │   "Если меня удалят — deinit вызовется"            │   │
│   │                                                     │   │
│   │   НО: "Система может убить меня молча,             │   │
│   │        если я в suspended state"                    │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Последствия для разработчика:                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   ✓ Можно полагаться на предсказуемый lifecycle     │   │
│   │   ✓ Navigation stack стабилен                       │   │
│   │   ✓ View состояние сохраняется автоматически        │   │
│   │                                                     │   │
│   │   ✗ НО нужно вручную сохранять данные формы         │   │
│   │   ✗ НО jetsam убьёт без предупреждения              │   │
│   │   ✗ НО retain cycles могут помешать deinit          │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Android: "Система контролирует мою смерть"

```
┌─────────────────────────────────────────────────────────────┐
│            Android Mental Model: System Control              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Activity думает:                                          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   "Я могу быть убит в любой момент"                │   │
│   │   "Система решает, жить мне или умереть"           │   │
│   │   "Мне дадут шанс сохранить состояние"             │   │
│   │   "При возврате мне вернут сохранённое"            │   │
│   │                                                     │   │
│   │   "Поворот экрана = моя смерть и возрождение"      │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Последствия для разработчика:                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   ✓ Система гарантирует onSaveInstanceState        │   │
│   │   ✓ Bundle доступен в onCreate                      │   │
│   │   ✓ ViewModel выживает configuration change        │   │
│   │                                                     │   │
│   │   ✗ НО нужно тестировать process death             │   │
│   │   ✗ НО Bundle ограничен ~1MB                       │   │
│   │   ✗ НО onDestroy не гарантирован                   │   │
│   │   ✗ НО navigation state нужно восстанавливать      │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### State как источник истины

```
┌─────────────────────────────────────────────────────────────┐
│             Unidirectional Data Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Обе платформы сходятся к одной модели:                    │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │         ┌─────────────────────────┐                 │   │
│   │         │                         │                 │   │
│   │         │      STATE              │ ◄── Источник    │   │
│   │         │  (ViewModel/Store)      │     истины      │   │
│   │         │                         │                 │   │
│   │         └───────────┬─────────────┘                 │   │
│   │                     │                               │   │
│   │                     ▼                               │   │
│   │         ┌─────────────────────────┐                 │   │
│   │         │                         │                 │   │
│   │         │      VIEW               │ ◄── Отражение   │   │
│   │         │  (VC/Activity/Fragment) │     состояния   │   │
│   │         │                         │                 │   │
│   │         └───────────┬─────────────┘                 │   │
│   │                     │                               │   │
│   │                     │ User Action                   │   │
│   │                     ▼                               │   │
│   │         ┌─────────────────────────┐                 │   │
│   │         │                         │                 │   │
│   │         │      ACTION             │ ◄── Намерение   │   │
│   │         │  (Event/Intent)         │     изменить    │   │
│   │         │                         │                 │   │
│   │         └───────────┬─────────────┘                 │   │
│   │                     │                               │   │
│   │                     └─────────────────►  STATE      │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Правила:                                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │   1. State живёт отдельно от View                   │   │
│   │   2. View только отображает State                   │   │
│   │   3. Изменения через Actions/Events                 │   │
│   │   4. State персистируется независимо от View        │   │
│   │                                                     │   │
│   │   iOS:  StateObject + AppStorage/SceneStorage       │   │
│   │   Android: ViewModel + SavedStateHandle             │   │
│   │   KMP: Essenty StateKeeper + InstanceKeeper         │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

### Вопрос 1: Lifecycle Callbacks

**Сценарий:** Пользователь открывает ProfileViewController/ProfileActivity, затем переходит на SettingsViewController/SettingsActivity, затем возвращается назад.

**Какие lifecycle callbacks будут вызваны для Profile экрана?**

<details>
<summary>Ответ для iOS</summary>

```
ProfileViewController:
1. viewWillDisappear (перед переходом на Settings)
2. viewDidDisappear (после перехода)
3. viewWillAppear (перед возвратом)
4. viewDidAppear (после возврата)

Важно:
- viewDidLoad НЕ вызывается повторно
- Контроллер остаётся в памяти (navigation stack)
- deinit НЕ вызывается
```

</details>

<details>
<summary>Ответ для Android</summary>

```
ProfileActivity:
1. onPause (перед переходом)
2. onStop (после перехода, если Activity не видна)
3. onSaveInstanceState (может быть вызван)
4. onRestart (перед возвратом)
5. onStart (возврат)
6. onResume (Activity в фокусе)

Важно:
- onCreate НЕ вызывается повторно (если нет process death)
- Activity может быть убита в stopped state
- При process death: onCreate вызовется заново с Bundle
```

</details>

### Вопрос 2: Process Death

**Сценарий:** Пользователь заполняет форму регистрации, переключается на другое приложение, система убивает ваше приложение из-за нехватки памяти. Пользователь возвращается через 5 минут.

**Что произойдёт на каждой платформе? Как сохранить данные формы?**

<details>
<summary>Ответ</summary>

```
iOS:
- Приложение перезапускается полностью
- application:didFinishLaunchingWithOptions вызывается
- ВСЕ данные формы потеряны (если не сохранены вручную)
- Navigation stack потерян

Решение для iOS:
- Сохранять данные в UserDefaults/AppStorage в viewWillDisappear
- Использовать @SceneStorage для UI состояния
- Сохранять в applicationDidEnterBackground

Android:
- onCreate вызывается с savedInstanceState Bundle
- Данные из onSaveInstanceState доступны
- Navigation stack восстанавливается автоматически

Решение для Android:
- Использовать onSaveInstanceState для UI состояния
- Использовать SavedStateHandle в ViewModel
- rememberSaveable в Compose
```

</details>

### Вопрос 3: Memory Leaks

**Найдите утечку памяти в этом коде:**

```swift
class ChatViewController: UIViewController {
    private var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()

        timer = Timer.scheduledTimer(
            withTimeInterval: 1.0,
            repeats: true
        ) { _ in
            self.updateTimestamp()
        }
    }
}
```

<details>
<summary>Ответ</summary>

```swift
// Проблема: Timer удерживает strong reference на self
// ChatViewController никогда не освободится (deinit не вызовется)
// Timer продолжит работать даже после ухода с экрана

// Решение 1: weak self
timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
    self?.updateTimestamp()
}

// Решение 2: invalidate в deinit (но deinit не вызовется из-за retain cycle!)

// Решение 3: invalidate в viewWillDisappear
override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    timer?.invalidate()
    timer = nil
}

// Решение 4: Использовать Combine или async/await
private var timerTask: Task<Void, Never>?

override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)

    timerTask = Task { @MainActor in
        while !Task.isCancelled {
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            updateTimestamp()
        }
    }
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    timerTask?.cancel()
}
```

</details>

### Вопрос 4: Configuration Changes

**Сценарий:** Пользователь вращает устройство во время сетевого запроса. Какие проблемы могут возникнуть?

<details>
<summary>Ответ для iOS</summary>

```
iOS:
- UIViewController НЕ пересоздаётся при rotation
- Сетевой запрос продолжает выполняться
- Callback придёт в тот же ViewController

Потенциальные проблемы:
- UI может неправильно отображаться после rotation
  (если не используется Auto Layout)
- viewWillTransition вызывается, нужно обновить layout

Решение:
override func viewWillTransition(
    to size: CGSize,
    with coordinator: UIViewControllerTransitionCoordinator
) {
    super.viewWillTransition(to: size, with: coordinator)

    coordinator.animate { _ in
        self.updateLayout(for: size)
    } completion: { _ in
        // Обновить UI после rotation
    }
}
```

</details>

<details>
<summary>Ответ для Android</summary>

```
Android:
- Activity ПЕРЕСОЗДАЁТСЯ при rotation
- Сетевой запрос продолжает выполняться
- Callback придёт в СТАРЫЙ (уничтоженный) Activity
- Результат потеряется!

Проблемы:
1. Утечка памяти (старый Activity в callback)
2. Потерянный результат запроса
3. Повторный запрос при onCreate

Решения:

1. ViewModel (переживает configuration change):
class MyViewModel : ViewModel() {
    private val _result = MutableLiveData<Result>()
    val result: LiveData<Result> = _result

    fun loadData() {
        viewModelScope.launch {
            _result.value = repository.getData()
        }
    }
}

2. android:configChanges (не рекомендуется):
<activity android:configChanges="orientation|screenSize" />

3. rememberCoroutineScope в Compose:
val scope = rememberCoroutineScope()
// scope отменяется при recomposition
```

</details>

---

## Связанные темы

- [[ios-viewcontroller-lifecycle]] — Детальное руководство по UIViewController lifecycle
- [[android-activity-lifecycle]] — Полный lifecycle Activity и Fragment
- [[ios-app-lifecycle]] — Application lifecycle на iOS
- [[android-app-lifecycle]] — Application lifecycle на Android
- [[process-death]] — Глубокое погружение в process death
- [[state-restoration]] — Техники восстановления состояния
- [[kmp-lifecycle]] — Lifecycle в Kotlin Multiplatform
- [[swiftui-lifecycle]] — Lifecycle в SwiftUI
- [[compose-lifecycle]] — Lifecycle в Jetpack Compose
- [[memory-management-mobile]] — Управление памятью на мобильных платформах

---

## Источники

### Официальная документация

1. **Apple Developer Documentation**
   - [UIViewController](https://developer.apple.com/documentation/uikit/uiviewcontroller)
   - [Managing Your App's Life Cycle](https://developer.apple.com/documentation/uikit/app_and_environment/managing_your_app_s_life_cycle)
   - [Preserving Your App's UI Across Launches](https://developer.apple.com/documentation/uikit/view_controllers/preserving_your_app_s_ui_across_launches)

2. **Android Developer Documentation**
   - [Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
   - [Handle Activity State Changes](https://developer.android.com/guide/components/activities/state-changes)
   - [Saved State module for ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel-savedstate)
   - [Process and Application Lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle)

### Библиотеки

3. **Essenty** — Lifecycle для Kotlin Multiplatform
   - [GitHub: arkivanov/Essenty](https://github.com/arkivanov/Essenty)

4. **Decompose** — Navigation и Lifecycle для KMP
   - [GitHub: arkivanov/Decompose](https://github.com/arkivanov/Decompose)

### Статьи и видео

5. **WWDC Sessions**
   - [WWDC 2019: Architecting Your App for Multiple Windows](https://developer.apple.com/videos/play/wwdc2019/258/)
   - [WWDC 2020: App Essentials in SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10037/)

6. **Android Dev Summit / Google I/O**
   - [Android Lifecycle Codelab](https://developer.android.com/codelabs/android-lifecycles)
   - [Handling Lifecycles with Lifecycle-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)

7. **Community Resources**
   - [Process Death is the Rule, Not the Exception](https://medium.com/androiddevelopers/process-death-is-the-rule-not-the-exception)
   - [iOS Background Execution Demystified](https://developer.apple.com/documentation/backgroundtasks)
