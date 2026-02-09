---
title: iOS App Components и Lifecycle
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
area: ios
tags: [ios, app-architecture, lifecycle, uikit, swiftui, cs-foundations]
related: [[android-app-components]], [[ios-view-controllers]], [[swiftui-app-lifecycle]], [[ios-scene-delegate]]
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

## Проверь себя

<details>
<summary><strong>Вопрос 1:</strong> iPad app поддерживает multi-window. Пользователь открыл 3 окна с разными документами, затем закрыл второе окно. Что произойдёт с AppDelegate и SceneDelegate?</summary>

**Ответ:**

1. **AppDelegate:** Ничего не произойдёт! AppDelegate управляет жизненным циклом приложения, а не отдельных окон.

2. **SceneDelegate:** Вызовется `sceneDidDisconnect(_:)` для закрытого окна.

**Последовательность:**
```swift
// Закрытие второго окна
SceneDelegate (Window 2):
    1. sceneWillResignActive(_:)        // окно теряет фокус
    2. sceneDidEnterBackground(_:)      // уходит в background
    3. sceneDidDisconnect(_:)           // scene уничтожается

// AppDelegate НЕ вызывается!

// Окна 1 и 3 продолжают работать независимо
```

**Важно:**
- `sceneDidDisconnect` ≠ app termination
- SceneSession сохраняется системой для state restoration
- Если пользователь откроет окно снова, вызовется `scene(_:willConnectTo:)` с тем же session ID

**Код для очистки:**
```swift
func sceneDidDisconnect(_ scene: UIScene) {
    // ПОЧЕМУ: очищаем ресурсы конкретного окна
    documentViewController?.closeDocument()
    window = nil

    // ПОЧЕМУ: НЕ очищаем глобальные ресурсы (Firebase, UserDefaults)
    // они используются другими окнами!
}

func application(_ application: UIApplication,
                 didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
    // ПОЧЕМУ: вызывается когда пользователь явно закрыл окно в app switcher
    // можно удалить сохранённое состояние scene
    for session in sceneSessions {
        deleteSceneState(for: session.persistentIdentifier)
    }
}
```

</details>

<details>
<summary><strong>Вопрос 2:</strong> SwiftUI app использует @Environment(\.scenePhase). Пользователь открыл Control Center, затем вернулся в app. Какие значения примет scenePhase и в каком порядке?</summary>

**Ответ:**

```swift
active → inactive → active
```

**Детальная последовательность:**
```
1. User swipes up для Control Center
   scenePhase: .active → .inactive
   onChange вызывается с (oldPhase: .active, newPhase: .inactive)

2. Control Center отображается
   scenePhase остаётся .inactive
   App видна, но не принимает touch events

3. User закрывает Control Center
   scenePhase: .inactive → .active
   onChange вызывается с (oldPhase: .inactive, newPhase: .active)
```

**Важно:** App НЕ переходит в `.background` при Control Center!

**Контраст с Home button:**
```
Home button press:
   .active → .inactive → .background → .suspended

Control Center / Notification Center / Incoming Call:
   .active → .inactive → .active
```

**Практический пример:**
```swift
@main
struct GameApp: App {
    @StateObject var gameEngine = GameEngine()
    @Environment(\.scenePhase) var scenePhase

    var body: some Scene {
        WindowGroup {
            GameView()
                .environmentObject(gameEngine)
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                // ПОЧЕМУ: возобновляем игру только если была пауза
                if gameEngine.isPaused {
                    gameEngine.resume()
                }

            case .inactive:
                // ПОЧЕМУ: ВСЕГДА паузим игру при inactive
                // Control Center, incoming call, notification — во всех случаях
                gameEngine.pause()

            case .background:
                // ПОЧЕМУ: сохраняем state для восстановления
                gameEngine.saveState()
                gameEngine.cleanup()

            @unknown default:
                break
            }
        }
    }
}
```

**Сравнение с UIKit:**
```swift
// UIKit equivalent
NotificationCenter.default.addObserver(
    self,
    selector: #selector(willResignActive),
    name: UIApplication.willResignActiveNotification,
    object: nil
)

NotificationCenter.default.addObserver(
    self,
    selector: #selector(didBecomeActive),
    name: UIApplication.didBecomeActiveNotification,
    object: nil
)
```

</details>

<details>
<summary><strong>Вопрос 3:</strong> App запланировал BGAppRefreshTask на 2:00 AM. В 1:50 AM пользователь открыл app и работает с ним. Что произойдёт в 2:00 AM?</summary>

**Ответ:**

**Система НЕ запустит BGAppRefreshTask в 2:00 AM!**

**Причины:**
1. **Foreground priority:** Пока app в foreground (active/inactive), background tasks не запускаются
2. **Opportunistic scheduling:** `earliestBeginDate` — это МИНИМУМ, не гарантированное время
3. **System discretion:** iOS выбирает оптимальное время на основе:
   - User patterns (когда обычно не используется app)
   - Device charging status
   - Network availability (WiFi vs Cellular)
   - Battery level

**Когда запустится task:**
```
Сценарий 1: User продолжает использовать app
    → Task отложится до следующего периода неактивности
    → Может запуститься в 3:00 AM, 4:00 AM, или вообще на следующий день

Сценарий 2: User закрыл app в 2:05 AM
    → Система может запустить task через 15-30 минут неактивности
    → НЕ сразу после закрытия app

Сценарий 3: iPhone заряжается на WiFi
    → Выше приоритет, может запуститься раньше

Сценарий 4: Low Power Mode включён
    → Background tasks полностью отключены системой
```

**Как система принимает решение:**
```
┌─────────────────────────────────────────┐
│ BGTaskScheduler Decision Engine        │
├─────────────────────────────────────────┤
│ 1. App state: Background? ✓             │
│ 2. earliestBeginDate passed? ✓          │
│ 3. Battery level > 20%? ✓               │
│ 4. On WiFi? ✓                           │
│ 5. User pattern: likely inactive? ✓     │
│ 6. System resources available? ✓        │
│                                         │
│ → Decision: Run task NOW                │
└─────────────────────────────────────────┘
```

**Код для monitoring:**
```swift
func handleAppRefresh(task: BGAppRefreshTask) {
    let taskStartTime = Date()
    print("BGAppRefreshTask started at \(taskStartTime)")
    // ПОЧЕМУ: фактическое время может отличаться от earliestBeginDate

    // ПОЧЕМУ: всегда планируем следующий запуск
    scheduleNextRefresh()

    task.expirationHandler = {
        // ПОЧЕМУ: система даёт ~30 секунд, потом прерывает
        print("Task expired after \(Date().timeIntervalSince(taskStartTime)) seconds")
    }

    Task {
        await refreshContent()
        task.setTaskCompleted(success: true)
    }
}

func scheduleNextRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")

    // ПОЧЕМУ: минимум 15 минут между запусками
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        // ПОЧЕМУ: может fail если уже запланировано или invalid identifier
        print("Failed to schedule: \(error)")
    }
}
```

**Testing в Xcode:**
```bash
# ПОЧЕМУ: симулируем запуск вручную для debugging
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.app.refresh"]

# ПОЧЕМУ: проверяем что task зарегистрирован
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateExpirationForTaskWithIdentifier:@"com.app.refresh"]
```

**Важно:** Background tasks — это "best effort", не guaranteed execution. Для критичных операций используйте Push Notifications → silent push → background URLSession.

</details>

<details>
<summary><strong>Вопрос 4 (Бонус):</strong> В чём фундаментальное отличие между iOS UIApplication lifecycle и Android Activity lifecycle? Почему iOS app может быть killed в Suspended state без уведомления?</summary>

**Ответ:**

### Фундаментальное отличие архитектур

**iOS: Application-centric model**
```
UIApplication (Singleton)
    │
    ├─ App целиком в памяти или terminated
    └─ Suspended → Terminated: без уведомления кода!
```

**Android: Component-centric model** (см. [[android-app-components]])
```
Каждый Activity/Service — независимый lifecycle
    │
    ├─ onPause() → onStop() → onDestroy() всегда вызываются
    └─ Process kill идёт после onDestroy()
```

### Почему iOS может убить app без уведомления?

**Причина 1: Suspended state не выполняет код**
```swift
// iOS lifecycle
applicationDidEnterBackground()
    → ~30 секунд на cleanup
    → Suspended (процесс жив, но НЕ выполняет код)
    → [Low Memory] → Terminated (без вызова кода!)

// ПОЧЕМУ: в Suspended нет CPU time, нечему вызывать applicationWillTerminate
```

**Причина 2: Memory pressure**
```
iOS memory management:
1. Active apps: полный доступ к памяти
2. Background apps: ограниченное время (~30 сек)
3. Suspended apps: frozen в памяти (RAM snapshot)
4. Low memory: Suspended apps killed молча (oldest first)

Android:
1. onLowMemory() callback ПЕРЕД kill
2. onDestroy() успевает вызваться
```

**Сравнительная таблица:**

| Аспект | iOS | Android |
|--------|-----|---------|
| **Гарантированные callbacks** | `didEnterBackground` | `onPause` → `onStop` → `onDestroy` |
| **Ungraceful termination** | Suspended → killed без callback | Редко (только system crash) |
| **Когда сохранять state** | `applicationDidEnterBackground` (всегда!) | `onPause` (лучше), `onStop` (обязательно) |
| **Время на cleanup** | ~30 секунд (с beginBackgroundTask) | Unlimited в onDestroy |
| **Multi-window** | Scenes (iOS 13+), каждая с lifecycle | Multi-Activity всегда, независимые lifecycles |

**Практический пример последствий:**

```swift
// ❌ ОПАСНО в iOS
func applicationDidEnterBackground(_ application: UIApplication) {
    // ПОЧЕМУ: можем НЕ успеть, app suspended через 5 секунд
    saveLargeDatabase() // 10 seconds
}

func applicationWillTerminate(_ application: UIApplication) {
    // ПОЧЕМУ: этот метод НЕ вызовется если app killed из Suspended!
    saveUserData() // НИКОГДА НЕ ВЫПОЛНИТСЯ при normal termination
}

// ✅ ПРАВИЛЬНО
func applicationDidEnterBackground(_ application: UIApplication) {
    var backgroundTask: UIBackgroundTaskIdentifier = .invalid

    backgroundTask = application.beginBackgroundTask {
        // ПОЧЕМУ: expiration handler — последний шанс
        emergencySave() // 1 second max
        application.endBackgroundTask(backgroundTask)
    }

    Task {
        await saveCriticalData() // ВСЕГДА сохраняем здесь
        await saveUserPreferences()

        application.endBackgroundTask(backgroundTask)
    }
}
```

**Android equivalent:**
```kotlin
// Android ГАРАНТИРУЕТ onDestroy() callback
override fun onStop() {
    super.onStop()
    // ПОЧЕМУ: сохраняем в onStop, onDestroy может не вызваться только при system kill
    saveCriticalData()
}

override fun onDestroy() {
    super.onDestroy()
    // ПОЧЕМУ: cleanup ресурсов, этот метод почти всегда вызывается
    closeConnections()
    releaseResources()
}
```

### Ключевой вывод

**iOS философия:** "Background apps — это frozen snapshots, не running processes"
- Экономит батарею (no CPU для suspended apps)
- Быстрый app switching (resume из RAM)
- ЦЕНА: developer должен сохранять state в `didEnterBackground`, не полагаясь на `willTerminate`

**Android философия:** "Components lifecycle — это contract"
- Callbacks гарантированы (кроме force stop)
- Больше гибкости, но больше энергопотребления
- Easier для developers (explicit cleanup в onDestroy)

**Мантра iOS разработки:**
> "Treat every transition to background as potential termination. Save everything in didEnterBackground/sceneDidEnterBackground."

</details>

## Связанные темы

- [[android-app-components]] — сравнение с Activity/Service lifecycle
- [[ios-view-controllers]] — UIViewController lifecycle и view hierarchy
- [[swiftui-app-lifecycle]] — App protocol, ScenePhase, WindowGroup
- [[ios-scene-delegate]] — multi-window architecture на iPad
- [[ios-state-restoration]] — сохранение и восстановление UI state
- [[ios-background-modes]] — background execution capabilities
- [[ios-push-notifications]] — remote notifications и app lifecycle
- [[uikit-responder-chain]] — как события доходят до view controllers
- [[ios-app-extensions]] — lifecycle widget, share extension, today extension
- [[core-data-concurrency]] — работа с данными в разных lifecycle states

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
