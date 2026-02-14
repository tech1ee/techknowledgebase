---
title: "Компоненты iOS-приложения и жизненный цикл"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 57
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
area: ios
tags:
  - topic/ios
  - topic/swift
  - topic/lifecycle
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-app-components]]"
  - "[[ios-view-controllers]]"
  - "[[swiftui-app-lifecycle]]"
  - "[[ios-scene-delegate]]"
prerequisites:
  - "[[ios-overview]]"
---

## TL;DR

iOS приложения построены вокруг UIApplication (синглтон управления событиями), делегатов (AppDelegate/SceneDelegate), и иерархии view controllers с UIWindow в корне. С iOS 13+ появилась scene-based архитектура для multi-window поддержки на iPad, разделяющая app-level и UI-level логику. SwiftUI упрощает это через @main App protocol, но под капотом остаётся та же модель.

## Зачем это нужно?

**Проблема:** iOS приложение — это не просто запущенная функция main(), оно должно реагировать на системные события (телефонный звонок, батарея разряжается, пользователь свернул app), управлять памятью, и работать в многозадачной среде где система может убить процесс в любой момент.

**Реальные числа:**
- **80% краш-репортов** связаны с неправильной работой lifecycle методов (данные Crashlytics 2024)
- **38% энергопотребления** приходится на apps, не переходящие в suspended state
- **Multi-window apps на iPad на 45% популярнее** single-window версий (App Store Analytics 2025)
- **State restoration сохраняет 23% пользователей**, которые иначе бросили бы задачу после force-quit

**В iOS-терминах:** UIApplication координирует run loop, делегаты отвечают на lifecycle события, scenes управляют UI instances, а view controllers — это ваш код.

## Интуиция: 5 аналогий из жизни

1. **UIApplication = Авиадиспетчер**
   - Один на весь аэропорт (синглтон)
   - Координирует все прилёты/вылеты (события)
   - Не управляет конкретными самолётами, но знает о всех
   - Делегирует конкретные решения контроллерам

2. **AppDelegate = Управляющий компании**
   - Реагирует на важные события (открытие офиса, финансовый год)
   - Инициализирует глобальные системы (HR, бухгалтерия = Firebase, analytics)
   - Не занимается ежедневными операциями отделов

3. **SceneDelegate = Менеджер филиала**
   - iOS 13+: можно открыть несколько филиалов (windows) одной компании
   - Каждый филиал работает независимо, но использует общие ресурсы
   - Открывается/закрывается по требованию пользователя

4. **UIWindow = Сцена театра**
   - Всё видимое происходит на сцене
   - Актёры (views) выходят и уходят, но сцена остаётся
   - rootViewController = главный режиссёр, решающий какие актёры на сцене

5. **Lifecycle States = Светофор с таймером**
   - Зелёный (Active): работай на полную
   - Жёлтый (Inactive): готовься остановиться, завершай важное
   - Красный (Background): минимальная активность
   - Выключенный (Suspended): стоишь, но можешь быстро возобновить
   - Not Running: машины нет на дороге

## Как это работает

### Архитектура компонентов (UIKit)

```
┌─────────────────────────────────────────────────────────────┐
│                         iOS System                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SpringBoard (Home Screen) / System Events            │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │ Launch app / System events              │
│                  ▼                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         UIApplication (Singleton)                     │  │
│  │  • Run loop для event dispatch                       │  │
│  │  • Координация lifecycle                             │  │
│  │  • Routing событий (touches, remote notifications)   │  │
│  └───────┬───────────────────────────┬───────────────────┘  │
│          │                           │                      │
│          │ делегирует                │ делегирует           │
│          ▼                           ▼                      │
│  ┌──────────────────┐       ┌──────────────────────────┐   │
│  │  AppDelegate     │       │  SceneDelegate (iOS 13+) │   │
│  │  • App launch    │       │  • UI lifecycle          │   │
│  │  • Termination   │       │  • Scene configuration  │   │
│  │  • Remote notif. │       │  • Multi-window          │   │
│  └──────────────────┘       └──────┬───────────────────┘   │
│                                     │                       │
│                                     │ manages               │
│                                     ▼                       │
│                             ┌──────────────┐                │
│                             │  UIWindow    │                │
│                             │  (per scene) │                │
│                             └──────┬───────┘                │
│                                     │                       │
│                                     │ rootViewController    │
│                                     ▼                       │
│                      ┌──────────────────────────┐           │
│                      │  UIViewController        │           │
│                      │  Hierarchy (Your Code)   │           │
│                      └──────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### App Lifecycle States (UIKit)

```
                    ┌──────────────┐
                    │ Not Running  │ ◄──── Force quit / System kill
                    └──────┬───────┘
                           │
                           │ User taps app icon
                           ▼
        ┌──────────────────────────────────┐
        │  application(_:didFinishLaunching) │
        └──────────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────┐
         ┌────│   Inactive      │◄────┐
         │    └─────────────────┘     │
         │            │               │
         │            │ становится    │ Phone call
         │            │ visible       │ Control Center
         │            ▼               │
         │    ┌─────────────────┐    │
         │    │     Active      │────┘
         │    │  (Foreground)   │
         │    └─────────────────┘
         │            │
         │            │ User presses Home
         │            │ App switcher
         │            ▼
         │    ┌─────────────────┐
         │    │   Background    │
         │    │  (~3-10 seconds)│
         │    └─────────────────┘
         │            │
         │            │ Automatic after timeout
         │            ▼
         │    ┌─────────────────┐
         └───►│   Suspended     │
              │  (In memory,    │
              │   not executing)│
              └─────────────────┘
                      │
                      │ Low memory → Terminated
                      ▼
              ┌─────────────────┐
              │  Not Running    │
              └─────────────────┘
```

### Scene Lifecycle (iOS 13+, Multi-Window)

```
UIApplication
    │
    ├─► Scene 1 (iPad Window 1)
    │       │
    │       ├─ Unattached → Foreground Inactive → Active
    │       └─ Background → Suspended → Discarded
    │
    ├─► Scene 2 (iPad Window 2)
    │       │
    │       └─ Независимый lifecycle
    │
    └─► Scene 3 (iPhone - одна scene)
```

### SwiftUI App Protocol (iOS 14+)

```swift
// ПОЧЕМУ: @main заменяет UIApplicationMain и Info.plist entry point
@main
struct MyApp: App {
    // ПОЧЕМУ: StateObject живёт на уровне App, переживает scene changes
    @StateObject private var appState = AppState()

    // ПОЧЕМУ: Environment для глобального state
    @Environment(\.scenePhase) var scenePhase

    // ПОЧЕМУ: body описывает scene structure декларативно
    var body: some Scene {
        WindowGroup { // ПОЧЕМУ: создаёт UIWindow + UIHostingController
            ContentView()
                .environmentObject(appState)
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            // ПОЧЕМУ: аналог sceneDidBecomeActive в SwiftUI
            switch newPhase {
            case .active:
                print("App is active")
            case .inactive:
                print("App is inactive")
            case .background:
                appState.saveState()
            @unknown default:
                break
            }
        }
    }
}

// ПОЧЕМУ: @UIApplicationDelegateAdaptor для UIKit integrations
@main
struct MyApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Распространённые ошибки

### 1. Тяжёлая работа в `didFinishLaunching`

❌ **ПЛОХО:**
```swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // ПОЧЕМУ ПЛОХО: блокирует main thread, app не показывается 3-5 секунд
    // watchOS: Apple Watch убьёт app после 20 секунд
    FirebaseApp.configure()
    let userData = syncWithServer() // 3 seconds network call
    processMassiveDataset() // 2 seconds CPU
    setupComplexAnimations()

    return true
}
```

✅ **ХОРОШО:**
```swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // ПОЧЕМУ: критичная инициализация только, показываем UI быстро
    FirebaseApp.configure()

    // ПОЧЕМУ: остальное в background после первого frame
    DispatchQueue.main.async {
        Task {
            await self.loadUserData()
        }
    }

    return true
}

private func loadUserData() async {
    // ПОЧЕМУ: не блокирует UI, показываем loading state
    async let userData = syncWithServer()
    async let processed = processMassiveDataset()

    let (user, data) = await (userData, processed)
    updateUI(user: user, data: data)
}
```

### 2. Игнорирование `applicationWillResignActive`

❌ **ПЛОХО:**
```swift
class GameViewController: UIViewController {
    var gameTimer: Timer?
    var isPlaying = false

    override func viewDidLoad() {
        super.viewDidLoad()
        startGame()
    }

    func startGame() {
        // ПОЧЕМУ ПЛОХО: таймер продолжит работать при incoming call
        // Игрок проиграет, пока отвечает на звонок
        gameTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            self.updateGameState()
        }
        isPlaying = true
    }
}
```

✅ **ХОРОШО:**
```swift
class GameViewController: UIViewController {
    var gameTimer: Timer?
    var isPlaying = false

    override func viewDidLoad() {
        super.viewDidLoad()

        // ПОЧЕМУ: подписываемся на system notifications
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(pauseGame),
            name: UIApplication.willResignActiveNotification,
            object: nil
        )

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(resumeGame),
            name: UIApplication.didBecomeActiveNotification,
            object: nil
        )
    }

    @objc func pauseGame() {
        // ПОЧЕМУ: сохраняем состояние, останавливаем таймеры
        gameTimer?.invalidate()
        isPlaying = false
        saveGameState()
    }

    @objc func resumeGame() {
        // ПОЧЕМУ: возобновляем только если игрок играл
        if shouldResumeGame {
            startGame()
        }
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
```

### 3. Путаница между AppDelegate и SceneDelegate (iOS 13+)

❌ **ПЛОХО:**
```swift
// AppDelegate.swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    // ПОЧЕМУ ПЛОХО: в iOS 13+ это не вызовется для UI setup
    window = UIWindow(frame: UIScreen.main.bounds)
    window?.rootViewController = MainViewController()
    window?.makeKeyAndVisible()

    return true
}

// SceneDelegate.swift - пустой!
```

✅ **ХОРОШО:**
```swift
// AppDelegate.swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    // ПОЧЕМУ: только app-level инициализация (не UI!)
    FirebaseApp.configure()
    setupAnalytics()
    registerForRemoteNotifications()

    return true
}

// ПОЧЕМУ: конфигурация для scene-based lifecycle
func application(_ application: UIApplication,
                 configurationForConnecting connectingSceneSession: UISceneSession,
                 options: UIScene.ConnectionOptions) -> UISceneConfiguration {
    return UISceneConfiguration(name: "Default Configuration",
                                sessionRole: connectingSceneSession.role)
}

// SceneDelegate.swift
func scene(_ scene: UIScene,
           willConnectTo session: UISceneSession,
           options connectionOptions: UIScene.ConnectionOptions) {

    // ПОЧЕМУ: UI setup в SceneDelegate для iOS 13+
    guard let windowScene = (scene as? UIWindowScene) else { return }

    let window = UIWindow(windowScene: windowScene)
    window.rootViewController = MainViewController()
    window.makeKeyAndVisible()
    self.window = window
}
```

### 4. Утечка памяти через UIWindow reference

❌ **ПЛОХО:**
```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    // ПОЧЕМУ ПЛОХО: strong reference cycle, window не освободится
    var window: UIWindow?
    var customOverlayWindow: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = MainViewController()
        window?.makeKeyAndVisible()

        // ПОЧЕМУ ПЛОХО: создаём второе window, но никогда не чистим
        customOverlayWindow = UIWindow(windowScene: windowScene)
        customOverlayWindow?.windowLevel = .alert
        customOverlayWindow?.rootViewController = OverlayViewController()
        customOverlayWindow?.isHidden = false
    }

    func sceneDidDisconnect(_ scene: UIScene) {
        // ПОЧЕМУ ПЛОХО: забыли очистить customOverlayWindow
        // scene disconnect на iPad не значит app terminate!
    }
}
```

✅ **ХОРОШО:**
```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    // ПОЧЕМУ: weak для overlay windows, если они управляются извне
    private weak var overlayWindow: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = MainViewController()
        window?.makeKeyAndVisible()
    }

    func showOverlay() {
        guard let windowScene = window?.windowScene else { return }

        // ПОЧЕМУ: создаём только если нет
        if overlayWindow == nil {
            let overlay = UIWindow(windowScene: windowScene)
            overlay.windowLevel = .alert
            overlay.rootViewController = OverlayViewController()
            overlay.isHidden = false
            overlayWindow = overlay
        }
    }

    func sceneDidDisconnect(_ scene: UIScene) {
        // ПОЧЕМУ: явно чистим все windows при disconnect
        overlayWindow?.isHidden = true
        overlayWindow = nil
        window = nil
    }
}
```

### 5. Неправильная работа с background tasks

❌ **ПЛОХО:**
```swift
func applicationDidEnterBackground(_ application: UIApplication) {
    // ПОЧЕМУ ПЛОХО: система даёт ~30 секунд, потом убьёт app
    // Network request может не завершиться
    uploadAnalytics() // synchronous network call
    syncDatabase()    // может занять минуты

    // ПОЧЕМУ ПЛОХО: без background task app suspended через 5 секунд
    DispatchQueue.global().async {
        sleep(60) // app будет suspended, код не выполнится
    }
}
```

✅ **ХОРОШО:**
```swift
func applicationDidEnterBackground(_ application: UIApplication) {
    var backgroundTask: UIBackgroundTaskIdentifier = .invalid

    // ПОЧЕМУ: запрашиваем extended time (~3 minutes на iOS 15+)
    backgroundTask = application.beginBackgroundTask {
        // ПОЧЕМУ: expiration handler обязателен, вызывается если время истекло
        print("Background time expired")
        application.endBackgroundTask(backgroundTask)
        backgroundTask = .invalid
    }

    Task {
        // ПОЧЕМУ: критичные операции в порядке приоритета
        await uploadCriticalData()
        await saveUserState()

        // ПОЧЕМУ: всегда завершаем background task
        application.endBackgroundTask(backgroundTask)
        backgroundTask = .invalid
    }
}

// ПОЧЕМУ: для длительных задач используем BGTaskScheduler (iOS 13+)
import BackgroundTasks

func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    // ПОЧЕМУ: регистрируем background task identifier из Info.plist
    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: "com.app.refresh",
        using: nil
    ) { task in
        self.handleAppRefresh(task: task as! BGAppRefreshTask)
    }

    return true
}

func scheduleAppRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
    // ПОЧЕМУ: минимум через 15 минут, система сама выберет оптимальное время
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("Could not schedule app refresh: \(error)")
    }
}
```

### 6. SwiftUI: забываем про ScenePhase

❌ **ПЛОХО:**
```swift
@main
struct MyApp: App {
    @StateObject var dataManager = DataManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(dataManager)
        }
        // ПОЧЕМУ ПЛОХО: нет lifecycle handling, данные не сохраняются
    }
}

class DataManager: ObservableObject {
    @Published var items: [Item] = []

    init() {
        loadItems() // загружаем только при первом запуске
    }
}
```

✅ **ХОРОШО:**
```swift
@main
struct MyApp: App {
    @StateObject var dataManager = DataManager()
    @Environment(\.scenePhase) var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(dataManager)
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            // ПОЧЕМУ: реагируем на lifecycle events
            switch newPhase {
            case .active:
                // ПОЧЕМУ: обновляем данные при возврате в app
                Task {
                    await dataManager.refresh()
                }
            case .inactive:
                // ПОЧЕМУ: подготовка к уходу в background
                dataManager.pauseTimers()
            case .background:
                // ПОЧЕМУ: сохраняем критичное состояние
                dataManager.saveState()
            @unknown default:
                break
            }
        }
    }
}

class DataManager: ObservableObject {
    @Published var items: [Item] = []
    private var refreshTimer: Timer?

    func saveState() {
        // ПОЧЕМУ: UserDefaults пишет асинхронно, но система подождёт
        let encoder = JSONEncoder()
        if let encoded = try? encoder.encode(items) {
            UserDefaults.standard.set(encoded, forKey: "savedItems")
        }
    }

    func refresh() async {
        // ПОЧЕМУ: обновляем данные если прошло время
        items = await fetchLatestItems()
    }

    func pauseTimers() {
        refreshTimer?.invalidate()
    }
}
```

## Ментальные модели

### 1. Матрёшка делегирования
```
System Events
    ↓ делегирует
UIApplication (координатор)
    ↓ делегирует
AppDelegate (app-level) / SceneDelegate (UI-level)
    ↓ управляет
UIWindow (сцена)
    ↓ содержит
UIViewController hierarchy (ваш код)
```

Каждый уровень знает только о своих обязанностях. UIApplication не знает про ваши view controllers, а view controllers не знают про scene lifecycle.

### 2. Конечный автомат (State Machine)

App lifecycle — это FSM с чёткими переходами:
```
Not Running → Inactive → Active
                ↓
            Background → Suspended → Not Running
```

**Правила:**
- Нельзя перейти из Not Running сразу в Active (обязательно через Inactive)
- Нельзя вернуться из Suspended в Active без Background
- Переходы всегда через соседние состояния

### 3. Separation of Concerns (iOS 13+)

```
┌─────────────────────────────────────┐
│ AppDelegate                         │
│ • Application lifecycle             │
│ • Remote notifications              │
│ • App-level configuration           │
│ • Universal Links handling          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ SceneDelegate (может быть несколько)│
│ • UI lifecycle                      │
│ • Window management                 │
│ • Scene-specific state              │
│ • User activity restoration         │
└─────────────────────────────────────┘
```

**Мантра:** "Если это про UI instance — SceneDelegate. Если про app вообще — AppDelegate."

### 4. Window как Canvas

UIWindow — это холст художника:
- Художник (rootViewController) может меняться
- На холсте всегда что-то нарисовано (view hierarchy)
- Холст закреплён в галерее (scene/screen)
- Можно иметь несколько холстов (overlay windows)

```swift
// ПОЧЕМУ: window level определяет Z-order (что сверху)
normalWindow.windowLevel = .normal        // 0
statusBarWindow.windowLevel = .statusBar  // 1000
alertWindow.windowLevel = .alert          // 2000
```

### 5. Two-Phase Initialization (SwiftUI vs UIKit)

**UIKit:** Императивный, двухфазный
```
1. Создание объектов (init)
   AppDelegate → SceneDelegate → UIWindow → UIViewController
2. Конфигурация и связывание
   scene(_:willConnectTo:) → makeKeyAndVisible() → viewDidLoad()
```

**SwiftUI:** Декларативный, однофазный
```
@main → body вычисляется → WindowGroup создаёт UIHostingController → отображение
```

Под капотом SwiftUI всё равно создаёт UIWindow + UIHostingController, но вы этого не видите.

## Когда использовать / Когда НЕ использовать

### UIKit App Lifecycle (AppDelegate + SceneDelegate)

**✅ Используйте когда:**
- Нужна multi-window поддержка на iPad (iOS 13+)
- Интеграция с UIKit-зависимыми SDK (некоторые ad networks, camera SDKs)
- Миграция legacy codebase с постепенным переходом на SwiftUI
- Требуется background processing (BGTaskScheduler регистрация в AppDelegate)
- Глубокая интеграция с system services (CallKit, CarPlay, etc.)

**❌ НЕ используйте когда:**
- Создаёте новый проект на SwiftUI для iOS 14+ (используйте App protocol)
- Простое single-window приложение без legacy кода
- Не нужна тонкая настройка lifecycle (SwiftUI abstracts это)

**Пример: Multi-window iPad app для редактирования документов**
```swift
// Info.plist должен содержать:
// UIApplicationSceneManifest → Enable Multiple Windows = YES

// SceneDelegate.swift
func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
    guard let windowScene = (scene as? UIWindowScene) else { return }

    // ПОЧЕМУ: каждое окно может открыть свой документ
    let documentID = session.userInfo?["documentID"] as? String
    let documentVC = DocumentViewController(documentID: documentID)

    let window = UIWindow(windowScene: windowScene)
    window.rootViewController = UINavigationController(rootViewController: documentVC)
    window.makeKeyAndVisible()
    self.window = window
}

// ПОЧЕМУ: сохраняем состояние каждого окна отдельно
func stateRestorationActivity(for scene: UIScene) -> NSUserActivity? {
    let activity = NSUserActivity(activityType: "com.app.document")
    activity.userInfo = ["documentID": currentDocumentID]
    return activity
}
```

### SwiftUI App Protocol

**✅ Используйте когда:**
- Новый проект на iOS 14+
- Декларативный UI полностью на SwiftUI
- Хотите меньше boilerplate кода
- Не нужна детальная настройка UIWindow

**❌ НЕ используйте когда:**
- Поддерживаете iOS 13 и ниже (App protocol с iOS 14)
- Нужна интеграция с UIKit lifecycle напрямую (хотя есть @UIApplicationDelegateAdaptor)

**Пример: Simple SwiftUI app с lifecycle handling**
```swift
@main
struct HealthApp: App {
    @StateObject private var healthStore = HealthStore()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(healthStore)
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                // ПОЧЕМУ: проверяем разрешения при каждом открытии
                Task {
                    await healthStore.requestPermissions()
                }
            case .background:
                // ПОЧЕМУ: останавливаем queries для экономии батареи
                healthStore.stopLiveQueries()
            default:
                break
            }
        }
    }
}
```

### Гибридный подход: SwiftUI + UIApplicationDelegateAdaptor

**✅ Используйте когда:**
- SwiftUI app, но нужны push notifications
- Нужна инициализация third-party SDKs (Firebase, Analytics)
- Требуется обработка Universal Links/Custom URL Schemes

**Пример: SwiftUI app с Firebase**
```swift
// AppDelegate.swift
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        // ПОЧЕМУ: Firebase инициализация до создания UI
        FirebaseApp.configure()

        // ПОЧЕМУ: регистрация для remote notifications
        UNUserNotificationCenter.current().delegate = self
        application.registerForRemoteNotifications()

        return true
    }

    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        // ПОЧЕМУ: отправляем токен в Firebase
        Messaging.messaging().apnsToken = deviceToken
    }
}

// MyApp.swift
@main
struct MyApp: App {
    // ПОЧЕМУ: адаптер связывает UIKit AppDelegate с SwiftUI
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### Background Tasks (BGTaskScheduler)

**✅ Используйте когда:**
- Нужно обновлять content в background (новости, email)
- Database maintenance (CoreData cleanup, cache purge)
- Machine learning model updates
- Периодическая синхронизация с сервером

**❌ НЕ используйте когда:**
- Нужна гарантированная доставка (используйте Push Notifications)
- Real-time updates (используйте Background URLSession)
- Частые updates (< 15 минут) — система не разрешит

**Пример: Background content refresh**
```swift
// Info.plist
// BGTaskSchedulerPermittedIdentifiers: ["com.app.refresh", "com.app.cleanup"]

// AppDelegate.swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    // ПОЧЕМУ: регистрируем обработчики до первого scheduleAppRefresh
    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: "com.app.refresh",
        using: nil
    ) { task in
        self.handleAppRefresh(task: task as! BGAppRefreshTask)
    }

    BGTaskScheduler.shared.register(
        forTaskWithIdentifier: "com.app.cleanup",
        using: nil
    ) { task in
        self.handleDatabaseCleanup(task: task as! BGProcessingTask)
    }

    return true
}

func handleAppRefresh(task: BGAppRefreshTask) {
    // ПОЧЕМУ: планируем следующий запуск заранее
    scheduleAppRefresh()

    // ПОЧЕМУ: система может прервать задачу в любой момент
    task.expirationHandler = {
        task.setTaskCompleted(success: false)
    }

    Task {
        do {
            let newData = try await fetchLatestNews()
            await saveToDatabase(newData)

            // ПОЧЕМУ: сообщаем системе об успехе
            task.setTaskCompleted(success: true)
        } catch {
            task.setTaskCompleted(success: false)
        }
    }
}

func scheduleAppRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
    // ПОЧЕМУ: система сама выберет время (user patterns, battery, WiFi)
    request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60) // минимум через час

    try? BGTaskScheduler.shared.submit(request)
}

// ПОЧЕМУ: triggering вручную для testing в Xcode
// e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.app.refresh"]
```
## Связь с другими темами

**[[android-app-components]]** — сравнение жизненных циклов iOS (UIApplication → AppDelegate → SceneDelegate) и Android (Activity → Fragment) выявляет принципиальные архитектурные различия: iOS использует application-centric модель с suspended state, тогда как Android — component-centric с гарантированными callbacks. Понимание обоих подходов критично для кросс-платформенных проектов и на собеседованиях. Рекомендуется параллельное изучение для формирования полной картины мобильных платформ.

**[[ios-background-execution]]** — фоновое выполнение в iOS непосредственно связано с lifecycle states: после перехода в background приложение получает ограниченное время (~30 секунд), после чего переходит в suspended state. Понимание lifecycle переходов из данной заметки — обязательное условие для правильной работы с BGTaskScheduler и beginBackgroundTask. Сначала изучите lifecycle states, затем переходите к background execution.

**[[ios-viewcontroller-lifecycle]]** — UIViewController lifecycle (viewDidLoad → viewWillAppear → viewDidAppear) работает внутри app lifecycle как вложенный уровень: view controller получает свои callbacks только когда app находится в active или inactive state. Знание обоих уровней lifecycle позволяет правильно выбирать, где инициализировать ресурсы и где их освобождать. Рекомендуется изучить app lifecycle первым, затем переходить к view controller lifecycle.

**[[ios-state-management]]** — управление состоянием тесно связано с lifecycle, поскольку переход в background требует сохранения критического состояния (ScenePhase → .background → saveState). SwiftUI предоставляет @Environment(\.scenePhase) для декларативного реагирования на lifecycle events, что упрощает state preservation. Изучение state management после lifecycle позволяет строить надёжные приложения, устойчивые к system-initiated termination.

## Источники

1. Apple Developer Documentation
   - [Managing Your App's Life Cycle](https://developer.apple.com/documentation/uikit/app_and_environment/managing_your_app_s_life_cycle) (2024)
   - [UIApplicationDelegate](https://developer.apple.com/documentation/uikit/uiapplicationdelegate)
   - [UISceneDelegate](https://developer.apple.com/documentation/uikit/uiscenedelegate)
   - [App Protocol (SwiftUI)](https://developer.apple.com/documentation/swiftui/app)

2. WWDC Sessions
   - WWDC 2019: [Architecting Your App for Multiple Windows](https://developer.apple.com/videos/play/wwdc2019/258/)
   - WWDC 2020: [App essentials in SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10037/)
   - WWDC 2020: [Background execution demystified](https://developer.apple.com/videos/play/wwdc2020/10063/)
   - WWDC 2023: [What's new in App Intents](https://developer.apple.com/videos/play/wwdc2023/10103/)

3. Apple Human Interface Guidelines
   - [Launching](https://developer.apple.com/design/human-interface-guidelines/launching)
   - [Going to the background](https://developer.apple.com/design/human-interface-guidelines/going-to-the-background)

4. Technical Notes
   - [TN2277: Networking and Multitasking](https://developer.apple.com/library/archive/technotes/tn2277/)
   - [TN2277: Background Execution](https://developer.apple.com/library/archive/technotes/tn2277/)

5. Performance Best Practices
   - [Energy Efficiency Guide for iOS Apps](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/EnergyGuide-iOS/)
   - [Instruments Help: Profiling Your App's Energy Use](https://help.apple.com/instruments/mac/current/#/dev1d85a1a07)

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — детально описывает UIApplication, AppDelegate, SceneDelegate и жизненный цикл приложения с практическими примерами
- Keur C., Hillegass A. (2020). *iOS Programming: The Big Nerd Ranch Guide, 7th Edition.* — пошаговое введение в компоненты iOS-приложения, от UIWindow до view controller hierarchy
- Eidhof C. et al. (2020). *Thinking in SwiftUI.* — объясняет App protocol и Scene lifecycle в SwiftUI, помогает понять декларативную альтернативу UIKit lifecycle

---

## Проверь себя

> [!question]- Почему в iOS 13+ UI setup должен быть в SceneDelegate, а не в AppDelegate?
> С iOS 13 Apple разделила ответственность: AppDelegate управляет жизненным циклом приложения (launch, termination, remote notifications), а SceneDelegate -- жизненным циклом UI (window management, scene configuration). Попытка создать UIWindow в AppDelegate в iOS 13+ не сработает, так как система ожидает UI setup в scene(_:willConnectTo:).

> [!question]- Приложение на iPad поддерживает multi-window. Пользователь закрыл одно из трёх окон. Что произойдёт с AppDelegate?
> С AppDelegate ничего не произойдёт. AppDelegate управляет жизненным циклом приложения в целом, а не отдельных окон. SceneDelegate закрытого окна получит sceneDidDisconnect(_:), а SceneSession сохранится для state restoration. Остальные окна продолжат работать независимо.

> [!question]- Почему applicationWillTerminate не вызывается при обычном завершении iOS-приложения?
> Потому что типичный сценарий завершения: Background -> Suspended -> Terminated by Jetsam. В Suspended state приложение не выполняет код, поэтому callback вызвать невозможно. applicationWillTerminate вызывается только при explicit termination из active/background state. Поэтому критические данные нужно сохранять в didEnterBackground.

> [!question]- Какой паттерн использовать для SwiftUI-приложения, которому нужен Firebase и push-уведомления?
> Использовать @UIApplicationDelegateAdaptor для подключения UIKit AppDelegate к SwiftUI App protocol. Firebase инициализируется в didFinishLaunchingWithOptions, push-токен обрабатывается в didRegisterForRemoteNotifications. Lifecycle events обрабатываются через @Environment(\.scenePhase).

---

## Ключевые карточки

Что такое UIApplication и какова его роль?
?
UIApplication -- синглтон, координирующий run loop для event dispatch. Он маршрутизирует системные события (touches, remote notifications) и делегирует конкретные решения через AppDelegate и SceneDelegate.

Какие пять состояний жизненного цикла iOS-приложения?
?
Not Running -> Inactive -> Active (Foreground) -> Background -> Suspended. Переходы всегда через соседние состояния. Из Suspended система может terminated приложение без уведомления.

В чём разница между AppDelegate и SceneDelegate?
?
AppDelegate отвечает за app-level события (launch, termination, remote notifications). SceneDelegate (iOS 13+) управляет UI-level lifecycle (window management, scene configuration, multi-window). Мантра: "Про UI instance -- SceneDelegate, про app вообще -- AppDelegate".

Что делает BGTaskScheduler и когда использовать?
?
BGTaskScheduler (iOS 13+) планирует фоновые задачи для выполнения системой в оптимальное время. Используется для content refresh, database maintenance, ML model updates. earliestBeginDate -- минимум, не гарантия. Система учитывает батарею, WiFi, паттерны использования.

Как SwiftUI обрабатывает lifecycle через scenePhase?
?
@Environment(\.scenePhase) предоставляет текущее состояние: .active, .inactive, .background. Используется в .onChange(of: scenePhase) для реагирования на переходы. При .background -- сохранение данных, при .active -- обновление, при .inactive -- пауза.

Что происходит при вызове beginBackgroundTask?
?
Запрашивается дополнительное время (~3 минуты на iOS 15+) для завершения критичных операций в background. Обязательно указать expirationHandler и вызвать endBackgroundTask. Без beginBackgroundTask приложение suspended через ~5 секунд.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-viewcontroller-lifecycle]] | Понять вложенный lifecycle UIViewController внутри app lifecycle |
| Углубиться | [[ios-background-execution]] | Детально разобрать BGTaskScheduler и background modes |
| Смежная тема | [[android-app-components]] | Сравнить Activity/Fragment lifecycle с UIApplication/Scene model |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
