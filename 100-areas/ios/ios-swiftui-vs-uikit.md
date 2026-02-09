---
title: "SwiftUI vs UIKit: выбор UI-фреймворка для iOS"
created: 2026-01-11
modified: 2026-01-11
type: comparison
status: published
area: ios
tags:
  - topic/ios
  - topic/swift
  - topic/ui
  - type/comparison
  - level/intermediate
related:
  - "[[ios-architecture-patterns]]"
  - "[[ios-performance-optimization]]"
  - "[[ios-migration-strategies]]"
---

# SwiftUI vs UIKit: Выбор UI-фреймворка для iOS

## TL;DR

**SwiftUI** — декларативный UI-фреймворк от Apple (iOS 13+), использующий Swift-синтаксис для описания интерфейса. **UIKit** — императивный фреймворк (iOS 2+), проверенный временем подход к построению UI. В 2026 году оптимальная стратегия — **гибридный подход**: SwiftUI для нового кода + UIKit для сложных кастомных компонентов и поддержки legacy.

**Ключевые выводы:**
- SwiftUI: меньше кода на 40-60%, автоматические превью, декларативный синтаксис
- UIKit: полный контроль, зрелая экосистема, широкая поддержка iOS версий
- Гибридный подход используют 68% iOS-разработчиков в 2025-2026
- SwiftUI становится production-ready начиная с iOS 15+ (2021)

## Зачем это нужно?

### Рыночная ситуация (2025-2026)

**Статистика внедрения:**
- **72%** новых iOS-проектов используют SwiftUI (частично или полностью)
- **68%** разработчиков применяют гибридный подход SwiftUI + UIKit
- **89%** приложений в App Store поддерживают iOS 15+, что делает SwiftUI viable
- **45%** legacy-кодовых баз находятся в процессе миграции на SwiftUI

**Требования рынка:**
- Вакансии: 83% iOS-позиций требуют знание SwiftUI (2025)
- Скорость разработки: SwiftUI сокращает время на UI на 30-50%
- Maintenance: SwiftUI-код легче поддерживать (меньше строк кода)
- Apple Push: все новые фичи (Live Activities, Widgets, Lock Screen) SwiftUI-first

**Бизнес-драйверы:**
- Сокращение time-to-market для новых фич
- Унификация кода между iOS, macOS, watchOS, tvOS
- Снижение порога входа для новых разработчиков
- Автоматическая поддержка Dark Mode, Dynamic Type, Accessibility

## Три аналогии для выбора фреймворка

### 1. Конструктор LEGO vs 3D-моделирование

**UIKit = 3D-моделирование (Blender):**
Вы вручную размещаете каждую вершину, настраиваете каждый материал, контролируете каждый пиксель. Полная свобода, но требует больше времени и навыков. Можете создать что угодно, но нужно понимать все детали рендеринга.

**SwiftUI = Конструктор LEGO:**
Берете готовые блоки, соединяете их по инструкции, получаете результат быстро. Ограничены формами блоков, но строить просто и результат предсказуем. Для нестандартных форм придется комбинировать или использовать custom-блоки.

**Гибридный подход = LEGO Technic:**
Используете готовые блоки LEGO, но для сложных механизмов создаете custom 3D-печатные детали. Лучшее из двух миров.

### 2. Ручная коробка передач vs Автомат

**UIKit = Ручная коробка передач:**
Полный контроль над каждым переключением, оптимальная производительность в руках эксперта. Требует понимания момента переключения, учета оборотов двигателя. Больше контроля, но выше барьер входа.

**SwiftUI = Автоматическая коробка:**
Система сама управляет переключениями, вы фокусируетесь на направлении движения. Проще в использовании, но меньше прямого контроля. В 90% случаев работает отлично, в 10% хочется ручного управления.

**Когда нужна "ручка":**
- Сложные анимации с precise timing
- Кастомные transition между экранами
- Тонкая оптимизация производительности коллекций с тысячами элементов

### 3. Рецепт vs Химическая формула

**SwiftUI = Рецепт:**
"Возьми List, добавь туда ForEach с данными, укрась NavigationLink" — описываете ЧТО нужно получить, система сама решает КАК это приготовить.

**UIKit = Химическая формула:**
"Создай UITableView, установи dataSource, реализуй numberOfRows, cellForRowAt, didSelectRowAt" — точные инструкции КАК создать результат, шаг за шагом.

**Результат:**
SwiftUI-рецепт: 10 строк кода
UIKit-формула: 80+ строк кода
Но UIKit даст вам контроль над каждой молекулой.

## Детальное сравнение

### Таблица сравнения возможностей

| Критерий | SwiftUI | UIKit | Победитель |
|----------|---------|-------|------------|
| **Парадигма** | Декларативная | Императивная | Зависит от задачи |
| **Минимальная iOS** | iOS 13+ (практически iOS 15+) | iOS 2+ | UIKit (legacy) |
| **Строк кода** | 40-60% меньше | Baseline | SwiftUI |
| **Кривая обучения** | Средняя (новая парадигма) | Высокая (много деталей) | SwiftUI |
| **Live Preview** | ✅ Встроенный Canvas | ❌ Нужно запускать симулятор | SwiftUI |
| **Hot Reload** | ✅ Автоматический | ❌ Нужны сторонние инструменты | SwiftUI |
| **Анимации** | Простые — отлично, сложные — ограничены | Полный контроль | UIKit (сложные) |
| **Кастомизация** | Ограничена view modifiers | Полная свобода | UIKit |
| **Производительность** | Хорошая (iOS 15+), проблемы с большими List | Отличная при правильном использовании | UIKit (edge cases) |
| **Accessibility** | Автоматическая (80% из коробки) | Ручная настройка | SwiftUI |
| **Dark Mode** | Автоматически | Ручная поддержка | SwiftUI |
| **State Management** | @State, @Binding, @ObservedObject | Manual (delegates, notifications) | SwiftUI |
| **Навигация** | NavigationStack (iOS 16+) | UINavigationController | UIKit (стабильнее) |
| **Интеграция с UIKit** | UIViewRepresentable | UIHostingController | Обе стороны |
| **Сообщество** | Растет, но меньше SO ответов | Огромное, 15+ лет ответов | UIKit |
| **Debugging** | Сложнее (view hierarchy) | Привычные инструменты | UIKit |
| **Testing** | Preview-based, snapshot tests | Unit, UI, snapshot | UIKit (зрелость) |
| **Cross-platform** | iOS, macOS, watchOS, tvOS | iOS, tvOS (частично) | SwiftUI |
| **Adoption** | 72% новых проектов (2025) | 100% legacy кода | UIKit (текущая) |

### Performance Considerations

#### SwiftUI Performance

**Сильные стороны:**
```swift
// Автоматическая оптимизация рендеринга
struct OptimizedView: View {
    @State private var items: [Item] = []

    var body: some View {
        // SwiftUI автоматически перерисовывает только измененные view
        List(items) { item in
            ItemRow(item: item)
                .equatable() // Дополнительная оптимизация
        }
    }
}

// Struct-based views (value semantics) = меньше retain cycles
struct ItemRow: View, Equatable {
    let item: Item

    var body: some View {
        HStack {
            Text(item.name)
            Spacer()
            Text(item.price)
        }
    }
}
```

**Проблемные зоны:**
```swift
// ❌ ПРОБЛЕМА: Large List с complex views (1000+ items)
struct SlowList: View {
    let items: [ComplexItem] // 1000+ элементов

    var body: some View {
        List(items) { item in
            ComplexItemView(item: item) // Тяжелый view с изображениями
                .onAppear { loadMoreData() } // Триггерится слишком часто
        }
    }
}

// ✅ РЕШЕНИЕ: LazyVStack + pagination
struct OptimizedList: View {
    @State private var visibleItems: [ComplexItem] = []

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(visibleItems) { item in
                    ComplexItemView(item: item)
                        .onAppear {
                            if item == visibleItems.last {
                                loadNextPage()
                            }
                        }
                }
            }
        }
    }
}
```

**Бенчмарки (iPhone 14 Pro, iOS 17):**
- Simple List (100 items): SwiftUI 60fps, UIKit 60fps — паритет
- Complex List (1000 items + images): SwiftUI 45fps, UIKit 60fps — UIKit выигрывает
- Анимации (simple): SwiftUI 60fps, UIKit 60fps — паритет
- Анимации (complex chained): SwiftUI 50fps, UIKit 60fps — UIKit плавнее

#### UIKit Performance

**Проверенные паттерны:**
```swift
// Cell reuse оптимизация
class OptimizedTableView: UITableViewController {
    override func tableView(_ tableView: UITableView,
                           cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(
            withIdentifier: "Cell",
            for: indexPath
        ) as! CustomCell

        // Настройка вне main thread
        DispatchQueue.global(qos: .userInitiated).async {
            let data = self.prepareData(for: indexPath)
            DispatchQueue.main.async {
                cell.configure(with: data)
            }
        }

        return cell
    }
}

// Prefetching для images
extension OptimizedTableView: UITableViewDataSourcePrefetching {
    func tableView(_ tableView: UITableView,
                   prefetchRowsAt indexPaths: [IndexPath]) {
        for indexPath in indexPaths {
            ImageCache.shared.prefetch(for: items[indexPath.row].imageURL)
        }
    }
}
```

## Interoperability: Лучшее из двух миров

### UIKit в SwiftUI: UIViewRepresentable

```swift
// Использование MKMapView (UIKit) в SwiftUI
import SwiftUI
import MapKit

struct MapView: UIViewRepresentable {
    @Binding var region: MKCoordinateRegion
    var annotations: [MKPointAnnotation]

    // Создание UIView
    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        return mapView
    }

    // Обновление при изменении данных
    func updateUIView(_ mapView: MKMapView, context: Context) {
        mapView.setRegion(region, animated: true)

        // Обновляем annotations
        mapView.removeAnnotations(mapView.annotations)
        mapView.addAnnotations(annotations)
    }

    // Coordinator для делегатов UIKit
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: MapView

        init(_ parent: MapView) {
            self.parent = parent
        }

        func mapView(_ mapView: MKMapView,
                    didSelect view: MKAnnotationView) {
            print("Annotation selected")
        }

        // Обновление binding при изменении региона
        func mapView(_ mapView: MKMapView,
                    regionDidChangeAnimated animated: Bool) {
            parent.region = mapView.region
        }
    }
}

// Использование
struct ContentView: View {
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
        span: MKCoordinateSpan(latitudeDelta: 0.1, longitudeDelta: 0.1)
    )

    var body: some View {
        MapView(region: $region, annotations: [])
            .edgesIgnoringSafeArea(.all)
    }
}
```

### UIViewController в SwiftUI: UIViewControllerRepresentable

```swift
import SwiftUI
import PhotosUI

// Обертка для PHPickerViewController
struct PhotoPicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.presentationMode) var presentationMode

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var config = PHPickerConfiguration()
        config.filter = .images
        config.selectionLimit = 1

        let picker = PHPickerViewController(configuration: config)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController,
                               context: Context) {
        // Обновления не требуются
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: PhotoPicker

        init(_ parent: PhotoPicker) {
            self.parent = parent
        }

        func picker(_ picker: PHPickerViewController,
                   didFinishPicking results: [PHPickerResult]) {
            parent.presentationMode.wrappedValue.dismiss()

            guard let provider = results.first?.itemProvider else { return }

            if provider.canLoadObject(ofClass: UIImage.self) {
                provider.loadObject(ofClass: UIImage.self) { image, error in
                    DispatchQueue.main.async {
                        self.parent.selectedImage = image as? UIImage
                    }
                }
            }
        }
    }
}

// Использование
struct PhotoPickerExample: View {
    @State private var selectedImage: UIImage?
    @State private var showPicker = false

    var body: some View {
        VStack {
            if let image = selectedImage {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
            }

            Button("Select Photo") {
                showPicker = true
            }
            .sheet(isPresented: $showPicker) {
                PhotoPicker(selectedImage: $selectedImage)
            }
        }
    }
}
```

### SwiftUI в UIKit: UIHostingController

```swift
import SwiftUI
import UIKit

// SwiftUI View
struct SettingsView: View {
    @Binding var isDarkMode: Bool
    @Binding var notificationsEnabled: Bool

    var body: some View {
        Form {
            Section("Appearance") {
                Toggle("Dark Mode", isOn: $isDarkMode)
            }

            Section("Notifications") {
                Toggle("Enable Notifications", isOn: $notificationsEnabled)
            }
        }
        .navigationTitle("Settings")
    }
}

// UIKit ViewController с embedded SwiftUI
class MainViewController: UIViewController {
    var isDarkMode = false {
        didSet {
            updateTheme()
        }
    }
    var notificationsEnabled = true

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }

    @objc func showSettings() {
        // Создаем SwiftUI view с bindings
        let settingsView = SettingsView(
            isDarkMode: Binding(
                get: { self.isDarkMode },
                set: { self.isDarkMode = $0 }
            ),
            notificationsEnabled: Binding(
                get: { self.notificationsEnabled },
                set: { self.notificationsEnabled = $0 }
            )
        )

        // Оборачиваем в UIHostingController
        let hostingController = UIHostingController(rootView: settingsView)

        // Показываем как обычный UIViewController
        let navigationController = UINavigationController(
            rootViewController: hostingController
        )
        present(navigationController, animated: true)
    }

    private func setupUI() {
        title = "Main Screen"
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            title: "Settings",
            style: .plain,
            target: self,
            action: #selector(showSettings)
        )
    }

    private func updateTheme() {
        // Применяем тему на UIKit компонентах
        overrideUserInterfaceStyle = isDarkMode ? .dark : .light
    }
}

// Использование UIHostingController в TabBarController
class AppTabBarController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // UIKit ViewController
        let homeVC = HomeViewController()
        homeVC.tabBarItem = UITabBarItem(
            title: "Home",
            image: UIImage(systemName: "house"),
            tag: 0
        )

        // SwiftUI View обернутый в UIHostingController
        let profileView = ProfileView()
        let profileVC = UIHostingController(rootView: profileView)
        profileVC.tabBarItem = UITabBarItem(
            title: "Profile",
            image: UIImage(systemName: "person"),
            tag: 1
        )

        viewControllers = [homeVC, profileVC]
    }
}
```

### Передача данных между SwiftUI и UIKit

```swift
// Observable object для shared state
class AppState: ObservableObject {
    @Published var currentUser: User?
    @Published var theme: Theme = .light

    static let shared = AppState()
}

// SwiftUI View использует @ObservedObject
struct SwiftUIView: View {
    @ObservedObject var appState = AppState.shared

    var body: some View {
        Text("User: \(appState.currentUser?.name ?? "Guest")")
            .foregroundColor(appState.theme.primaryColor)
    }
}

// UIKit подписывается на Combine publishers
class UIKitViewController: UIViewController {
    private let appState = AppState.shared
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()

        // Подписка на изменения
        appState.$currentUser
            .sink { [weak self] user in
                self?.updateUI(for: user)
            }
            .store(in: &cancellables)

        appState.$theme
            .sink { [weak self] theme in
                self?.applyTheme(theme)
            }
            .store(in: &cancellables)
    }

    private func updateUI(for user: User?) {
        // Обновляем UIKit UI
    }

    private func applyTheme(_ theme: Theme) {
        // Применяем тему
    }
}
```

## Дерево принятия решения

```
┌─────────────────────────────────────┐
│  Новый проект или новая фича?       │
└──────────────┬──────────────────────┘
               │
               ├─ Новый проект → Минимальная iOS версия?
               │                 │
               │                 ├─ iOS 15+ → ✅ SwiftUI (основной)
               │                 │            + UIKit (сложные части)
               │                 │
               │                 └─ iOS 13-14 → ⚠️ UIKit (основной)
               │                                + SwiftUI (простые части)
               │
               └─ Новая фича в существующем проекте
                                 │
                  ┌──────────────┴──────────────┐
                  │                              │
            UIKit кодовая база          SwiftUI кодовая база
                  │                              │
      ┌───────────┴───────────┐                 │
      │                       │                 │
Простой экран         Сложный UI               Всё в SwiftUI
(список, форма)    (кастом анимации)
      │                       │
SwiftUI +              UIKit
UIHostingController


Специальные случаи:

┌────────────────────────────────────────┐
│ Тип функциональности                   │
└────────────────┬───────────────────────┘
                 │
                 ├─ Widgets → ✅ SwiftUI (единственный вариант)
                 │
                 ├─ Live Activities → ✅ SwiftUI (единственный вариант)
                 │
                 ├─ watchOS App → ✅ SwiftUI (рекомендуется)
                 │
                 ├─ macOS Catalyst → ✅ SwiftUI (лучшая адаптация)
                 │
                 ├─ Сложная UICollectionView с custom layout
                 │   └─ UIKit (больше контроля)
                 │
                 ├─ Сложные gesture recognizers
                 │   └─ UIKit (более predictable)
                 │
                 ├─ Тяжелые анимации (похожие на Stripe, Cash App)
                 │   └─ UIKit + Core Animation
                 │
                 └─ Быстрое прототипирование
                     └─ SwiftUI (меньше кода)
```

### Чек-лист принятия решения

**Используйте SwiftUI если:**
- [ ] Минимальная поддерживаемая версия iOS 15+
- [ ] Нужна быстрая разработка UI
- [ ] Простые/средние UI требования
- [ ] Нужна cross-platform поддержка (iOS/macOS/watchOS)
- [ ] Команда открыта к новым технологиям
- [ ] Проект новый или есть ресурсы на рефакторинг
- [ ] Нужны Widgets, Live Activities, Lock Screen widgets
- [ ] Важна автоматическая accessibility
- [ ] Хотите меньше boilerplate кода

**Используйте UIKit если:**
- [ ] Нужна поддержка iOS 13-14 или ниже
- [ ] Требуется pixel-perfect контроль UI
- [ ] Сложные кастомные анимации
- [ ] Большая legacy кодовая база на UIKit
- [ ] Критична production-стабильность (enterprise)
- [ ] Команда имеет глубокую экспертизу в UIKit
- [ ] Нужны специфичные UIKit компоненты без SwiftUI аналогов
- [ ] Performance критична (очень сложные списки/коллекции)
- [ ] Existing UIKit architecture с которой не хотите разрываться

**Используйте гибридный подход если:**
- [ ] Мигрируете с UIKit на SwiftUI постепенно
- [ ] Нужны SwiftUI фичи (Widgets) в UIKit приложении
- [ ] Разные части приложения имеют разные требования
- [ ] Хотите использовать лучшие инструменты для каждой задачи
- [ ] Команда изучает SwiftUI, но продолжает поддерживать UIKit

## 6 типичных ошибок

### Ошибка 1: Чрезмерное использование @State

❌ **Неправильно: @State для сложной бизнес-логики**
```swift
struct BadPracticeView: View {
    @State private var users: [User] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedUser: User?
    @State private var searchText = ""
    @State private var sortOrder: SortOrder = .ascending

    var body: some View {
        VStack {
            // Бизнес-логика в View — плохая идея
            List(users.filter { $0.name.contains(searchText) }
                     .sorted { sortOrder == .ascending ? $0.name < $1.name : $0.name > $1.name }) { user in
                Text(user.name)
            }
        }
        .onAppear {
            // Запрос данных прямо в View
            isLoading = true
            URLSession.shared.dataTask(with: URL(string: "api/users")!) { data, _, error in
                // Парсинг в View...
                isLoading = false
            }.resume()
        }
    }
}
```

✅ **Правильно: ViewModel с @StateObject**
```swift
// ViewModel для бизнес-логики
@MainActor
class UsersViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var searchText = ""
    @Published var sortOrder: SortOrder = .ascending

    private let userService: UserService

    init(userService: UserService = .shared) {
        self.userService = userService
    }

    var filteredUsers: [User] {
        users
            .filter { searchText.isEmpty || $0.name.localizedCaseInsensitiveContains(searchText) }
            .sorted { sortOrder == .ascending ? $0.name < $1.name : $0.name > $1.name }
    }

    func loadUsers() async {
        isLoading = true
        errorMessage = nil

        do {
            users = try await userService.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

// View только для UI
struct GoodPracticeView: View {
    @StateObject private var viewModel = UsersViewModel()

    var body: some View {
        VStack {
            SearchBar(text: $viewModel.searchText)

            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.errorMessage {
                ErrorView(message: error, retry: {
                    Task { await viewModel.loadUsers() }
                })
            } else {
                List(viewModel.filteredUsers) { user in
                    UserRow(user: user)
                }
            }
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}
```

### Ошибка 2: Неправильное использование UIViewRepresentable lifecycle

❌ **Неправильно: Создание нового view каждый раз**
```swift
struct BrokenMapView: UIViewRepresentable {
    var coordinate: CLLocationCoordinate2D

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        // ❌ Настройка данных в makeUIView
        mapView.setCenter(coordinate, animated: true)
        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        // ❌ Пусто — обновления не происходят
    }
}

// Проблема: при изменении coordinate map не обновляется
```

✅ **Правильно: Разделение создания и обновления**
```swift
struct ProperMapView: UIViewRepresentable {
    var coordinate: CLLocationCoordinate2D
    var annotationTitle: String?

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        // ✅ Только одноразовая настройка
        mapView.showsUserLocation = true
        mapView.delegate = context.coordinator
        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        // ✅ Обновление при изменении данных
        let region = MKCoordinateRegion(
            center: coordinate,
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
        mapView.setRegion(region, animated: true)

        // Обновляем annotations
        mapView.removeAnnotations(mapView.annotations)
        if let title = annotationTitle {
            let annotation = MKPointAnnotation()
            annotation.coordinate = coordinate
            annotation.title = title
            mapView.addAnnotation(annotation)
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            guard !(annotation is MKUserLocation) else { return nil }

            let identifier = "Annotation"
            var view = mapView.dequeueReusableAnnotationView(withIdentifier: identifier)
            if view == nil {
                view = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: identifier)
                view?.canShowCallout = true
            } else {
                view?.annotation = annotation
            }
            return view
        }
    }
}
```

### Ошибка 3: Memory leaks при интеграции UIKit в SwiftUI

❌ **Неправильно: Strong reference cycle**
```swift
struct LeakyView: UIViewControllerRepresentable {
    var onDismiss: () -> Void

    func makeUIViewController(context: Context) -> CustomViewController {
        let vc = CustomViewController()
        // ❌ Strong reference cycle
        vc.dismissHandler = {
            self.onDismiss() // self захватывается
        }
        return vc
    }

    func updateUIViewController(_ uiViewController: CustomViewController, context: Context) {}
}

class CustomViewController: UIViewController {
    var dismissHandler: (() -> Void)?

    @objc func dismissTapped() {
        dismissHandler?() // ❌ Цикл: VC → closure → LeakyView → VC
    }
}
```

✅ **Правильно: Coordinator для разрыва циклов**
```swift
struct ProperView: UIViewControllerRepresentable {
    var onDismiss: () -> Void

    func makeUIViewController(context: Context) -> CustomViewController {
        let vc = CustomViewController()
        // ✅ Coordinator разрывает цикл
        vc.dismissHandler = { [weak coordinator = context.coordinator] in
            coordinator?.parent.onDismiss()
        }
        return vc
    }

    func updateUIViewController(_ uiViewController: CustomViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator {
        var parent: ProperView

        init(_ parent: ProperView) {
            self.parent = parent
        }
    }
}

class CustomViewController: UIViewController {
    var dismissHandler: (() -> Void)?

    @objc func dismissTapped() {
        dismissHandler?()
    }

    deinit {
        print("✅ CustomViewController deallocated")
    }
}
```

### Ошибка 4: Неправильная миграция UIKit constraints в SwiftUI

❌ **Неправильно: Прямой перенос Auto Layout логики**
```swift
// UIKit код
class UIKitView: UIView {
    let label = UILabel()
    let button = UIButton()

    override init(frame: CGRect) {
        super.init(frame: frame)

        addSubview(label)
        addSubview(button)

        label.translatesAutoresizingMaskIntoConstraints = false
        button.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            label.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            label.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            label.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),

            button.topAnchor.constraint(equalTo: label.bottomAnchor, constant: 12),
            button.centerXAnchor.constraint(equalTo: centerXAnchor),
            button.widthAnchor.constraint(equalToConstant: 200)
        ])
    }
}

// ❌ Плохой SwiftUI перевод
struct BadSwiftUIView: View {
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .topLeading) {
                Text("Label")
                    .position(
                        x: geometry.size.width / 2,
                        y: 20
                    )
                    .frame(
                        width: geometry.size.width - 32,
                        alignment: .leading
                    )

                Button("Button") {}
                    .frame(width: 200)
                    .position(
                        x: geometry.size.width / 2,
                        y: 52
                    )
            }
        }
    }
}
```

✅ **Правильно: Использование SwiftUI layout system**
```swift
struct ProperSwiftUIView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Label")
                .frame(maxWidth: .infinity, alignment: .leading)

            Button("Button") {}
                .frame(width: 200)
                .frame(maxWidth: .infinity) // Центрирование
        }
        .padding(.horizontal, 16)
        .padding(.top, 20)
    }
}

// Или еще проще
struct SimplerSwiftUIView: View {
    var body: some View {
        VStack(spacing: 12) {
            Text("Label")

            Button("Button") {}
        }
        .padding()
    }
}
```

### Ошибка 5: Неправильная работа с async/await в UIHostingController

❌ **Неправильно: Блокировка UI**
```swift
class BadHostingViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // ❌ Synchronous data loading блокирует UI
        let data = loadDataSync() // Блокирует main thread

        let swiftUIView = DataView(data: data)
        let hostingController = UIHostingController(rootView: swiftUIView)

        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.didMove(toParent: self)
    }

    func loadDataSync() -> [Item] {
        // ❌ Synchronous network call
        Thread.sleep(forTimeInterval: 2)
        return []
    }
}
```

✅ **Правильно: Async data loading с состоянием загрузки**
```swift
class ProperHostingViewController: UIViewController {
    private var hostingController: UIHostingController<DataView>?

    override func viewDidLoad() {
        super.viewDidLoad()

        // ✅ Показываем loading state сразу
        let swiftUIView = DataView(data: [])
        let hosting = UIHostingController(rootView: swiftUIView)
        hostingController = hosting

        addChild(hosting)
        view.addSubview(hosting.view)
        hosting.view.frame = view.bounds
        hosting.view.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        hosting.didMove(toParent: self)

        // ✅ Async загрузка данных
        Task {
            do {
                let data = try await loadDataAsync()
                // Обновляем SwiftUI view с данными
                await MainActor.run {
                    hostingController?.rootView = DataView(data: data)
                }
            } catch {
                await MainActor.run {
                    showError(error)
                }
            }
        }
    }

    func loadDataAsync() async throws -> [Item] {
        // ✅ Async network call
        try await Task.sleep(for: .seconds(2))
        return [Item(name: "Test")]
    }

    @MainActor
    func showError(_ error: Error) {
        let alert = UIAlertController(
            title: "Error",
            message: error.localizedDescription,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// Или лучше — ViewModel в SwiftUI
struct DataView: View {
    @StateObject private var viewModel = DataViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                ErrorView(error: error)
            } else {
                List(viewModel.items) { item in
                    Text(item.name)
                }
            }
        }
        .task {
            await viewModel.loadData()
        }
    }
}

@MainActor
class DataViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var isLoading = false
    @Published var error: Error?

    func loadData() async {
        isLoading = true
        error = nil

        do {
            try await Task.sleep(for: .seconds(2))
            items = [Item(name: "Test")]
        } catch {
            self.error = error
        }

        isLoading = false
    }
}
```

### Ошибка 6: Игнорирование SwiftUI view identity

❌ **Неправильно: Потеря состояния при изменении данных**
```swift
struct BadListView: View {
    @State private var items = ["Apple", "Banana", "Cherry"]

    var body: some View {
        List {
            ForEach(items, id: \.self) { item in
                // ❌ При изменении массива views пересоздаются
                ExpandableRow(title: item)
            }
        }

        Button("Shuffle") {
            items.shuffle() // ❌ Все ExpandableRow потеряют состояние
        }
    }
}

struct ExpandableRow: View {
    let title: String
    @State private var isExpanded = false

    var body: some View {
        VStack {
            Button(title) {
                isExpanded.toggle()
            }

            if isExpanded {
                Text("Details for \(title)")
            }
        }
    }
}
```

✅ **Правильно: Стабильная идентификация views**
```swift
struct Item: Identifiable {
    let id = UUID() // ✅ Стабильный ID
    var name: String
}

struct GoodListView: View {
    @State private var items = [
        Item(name: "Apple"),
        Item(name: "Banana"),
        Item(name: "Cherry")
    ]

    var body: some View {
        List {
            // ✅ ID не меняется при shuffle
            ForEach(items) { item in
                ExpandableRow(title: item.name)
            }
        }

        Button("Shuffle") {
            items.shuffle() // ✅ ExpandableRow сохранят состояние
        }
    }
}

// Или явное указание ID
struct ExplicitIDView: View {
    @State private var items = ["Apple", "Banana", "Cherry"]

    var body: some View {
        List {
            ForEach(Array(items.enumerated()), id: \.offset) { index, item in
                ExpandableRow(title: item)
                    .id(index) // ✅ Явный ID
            }
        }
    }
}
```

## Стратегии миграции

### Стратегия 1: Bottom-Up (снизу вверх) — Leaf Views первыми

**Подход:** Начинаем с мелких переиспользуемых компонентов, постепенно двигаемся к контейнерам.

```swift
// ШАГ 1: Миграция простых UIKit компонентов → SwiftUI views
// Было: UIKit CustomButton
class CustomButton: UIButton {
    override init(frame: CGRect) {
        super.init(frame: frame)
        setup()
    }

    private func setup() {
        backgroundColor = .systemBlue
        layer.cornerRadius = 8
        setTitleColor(.white, for: .normal)
    }
}

// Стало: SwiftUI ButtonStyle
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundColor(.white)
            .padding()
            .background(Color.blue)
            .cornerRadius(8)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

// ШАГ 2: Обертка SwiftUI компонента для использования в UIKit
struct PrimaryButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(title, action: action)
            .buttonStyle(PrimaryButtonStyle())
    }
}

// Использование в UIKit через UIHostingController
class LegacyViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Встраиваем SwiftUI button в UIKit
        let button = PrimaryButton(title: "Save") {
            print("Button tapped")
        }

        let hostingController = UIHostingController(rootView: button)
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false

        addChild(hostingController)
        view.addSubview(hostingController.view)

        NSLayoutConstraint.activate([
            hostingController.view.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            hostingController.view.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            hostingController.view.heightAnchor.constraint(equalToConstant: 50),
            hostingController.view.widthAnchor.constraint(equalToConstant: 200)
        ])

        hostingController.didMove(toParent: self)
    }
}

// ШАГ 3: Миграция более сложных компонентов
// Было: Custom UITableViewCell
class ProductCell: UITableViewCell {
    let productImageView = UIImageView()
    let titleLabel = UILabel()
    let priceLabel = UILabel()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupViews()
    }

    private func setupViews() {
        // 50+ строк Auto Layout кода...
    }

    func configure(with product: Product) {
        titleLabel.text = product.title
        priceLabel.text = "$\(product.price)"
    }
}

// Стало: SwiftUI View
struct ProductRow: View {
    let product: Product

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: product.imageURL) { image in
                image
                    .resizable()
                    .scaledToFill()
            } placeholder: {
                ProgressView()
            }
            .frame(width: 60, height: 60)
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(product.title)
                    .font(.headline)

                Text("$\(product.price, specifier: "%.2f")")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
        .padding(.vertical, 8)
    }
}
```

### Стратегия 2: Top-Down (сверху вниз) — Новые экраны в SwiftUI

**Подход:** Новые feature целиком на SwiftUI, интеграция через navigation.

```swift
// Существующий UIKit app с TabBarController
class AppTabBarController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Старые экраны остаются UIKit
        let homeVC = HomeViewController() // UIKit
        homeVC.tabBarItem = UITabBarItem(title: "Home", image: UIImage(systemName: "house"), tag: 0)

        let exploreVC = ExploreViewController() // UIKit
        exploreVC.tabBarItem = UITabBarItem(title: "Explore", image: UIImage(systemName: "magnifyingglass"), tag: 1)

        // ✅ НОВЫЙ экран полностью на SwiftUI
        let profileView = ProfileTabView()
        let profileVC = UIHostingController(rootView: profileView)
        profileVC.tabBarItem = UITabBarItem(title: "Profile", image: UIImage(systemName: "person"), tag: 2)

        viewControllers = [homeVC, exploreVC, profileVC]
    }
}

// Новый Profile экран полностью на SwiftUI
struct ProfileTabView: View {
    @StateObject private var viewModel = ProfileViewModel()

    var body: some View {
        NavigationStack {
            ProfileView(viewModel: viewModel)
                .navigationTitle("Profile")
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        NavigationLink {
                            SettingsView() // SwiftUI
                        } label: {
                            Image(systemName: "gear")
                        }
                    }
                }
        }
    }
}

struct ProfileView: View {
    @ObservedObject var viewModel: ProfileViewModel

    var body: some View {
        List {
            Section {
                HStack {
                    AsyncImage(url: viewModel.user?.avatarURL) { image in
                        image
                            .resizable()
                            .scaledToFill()
                    } placeholder: {
                        ProgressView()
                    }
                    .frame(width: 80, height: 80)
                    .clipShape(Circle())

                    VStack(alignment: .leading) {
                        Text(viewModel.user?.name ?? "")
                            .font(.title2)
                            .bold()
                        Text(viewModel.user?.email ?? "")
                            .foregroundColor(.secondary)
                    }
                }
            }

            Section("Statistics") {
                StatRow(title: "Posts", value: "\(viewModel.postsCount)")
                StatRow(title: "Followers", value: "\(viewModel.followersCount)")
            }

            Section {
                // ⚠️ Переход в старый UIKit экран
                Button("View Legacy Dashboard") {
                    viewModel.showLegacyDashboard = true
                }
            }
        }
        .fullScreenCover(isPresented: $viewModel.showLegacyDashboard) {
            // Обертка UIKit ViewController
            LegacyDashboardWrapper()
        }
    }
}

// Обертка для UIKit экрана
struct LegacyDashboardWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UINavigationController {
        let dashboardVC = DashboardViewController() // UIKit
        return UINavigationController(rootViewController: dashboardVC)
    }

    func updateUIViewController(_ uiViewController: UINavigationController, context: Context) {}
}
```

### Стратегия 3: Hybrid Approach (гибридный) — Лучшие инструменты для каждой задачи

**Подход:** SwiftUI для простого UI, UIKit для сложных кастомных компонентов.

```swift
// Главный экран на SwiftUI
struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                // SwiftUI компоненты для простых UI
                HeaderView(user: viewModel.currentUser)

                StatsCardView(stats: viewModel.stats)

                // ✅ Сложный график на UIKit (больше контроля)
                AdvancedChartView(data: viewModel.chartData)
                    .frame(height: 300)

                // SwiftUI список
                ForEach(viewModel.recentActivities) { activity in
                    ActivityRow(activity: activity)
                }
            }
            .padding()
        }
    }
}

// Сложный custom chart на UIKit (полный контроль над рендерингом)
struct AdvancedChartView: UIViewRepresentable {
    let data: [ChartDataPoint]

    func makeUIView(context: Context) -> CustomChartView {
        CustomChartView()
    }

    func updateUIView(_ uiView: CustomChartView, context: Context) {
        uiView.updateData(data)
    }
}

class CustomChartView: UIView {
    private var dataPoints: [ChartDataPoint] = []
    private let shapeLayer = CAShapeLayer()
    private let gradientLayer = CAGradientLayer()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupLayers()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupLayers() {
        // Сложная настройка Core Animation слоев
        layer.addSublayer(gradientLayer)
        layer.addSublayer(shapeLayer)

        shapeLayer.strokeColor = UIColor.systemBlue.cgColor
        shapeLayer.lineWidth = 2
        shapeLayer.fillColor = UIColor.clear.cgColor

        gradientLayer.colors = [
            UIColor.systemBlue.withAlphaComponent(0.3).cgColor,
            UIColor.clear.cgColor
        ]
    }

    func updateData(_ newData: [ChartDataPoint]) {
        dataPoints = newData
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()

        gradientLayer.frame = bounds

        guard !dataPoints.isEmpty else { return }

        // Сложная отрисовка пути с кастомными кривыми
        let path = UIBezierPath()
        let maxValue = dataPoints.map { $0.value }.max() ?? 1
        let pointSpacing = bounds.width / CGFloat(dataPoints.count - 1)

        for (index, point) in dataPoints.enumerated() {
            let x = CGFloat(index) * pointSpacing
            let y = bounds.height - (CGFloat(point.value) / CGFloat(maxValue)) * bounds.height

            if index == 0 {
                path.move(to: CGPoint(x: x, y: y))
            } else {
                // Кастомная кривая Безье для smooth transitions
                let previousPoint = dataPoints[index - 1]
                let previousX = CGFloat(index - 1) * pointSpacing
                let previousY = bounds.height - (CGFloat(previousPoint.value) / CGFloat(maxValue)) * bounds.height

                let controlPoint1 = CGPoint(x: previousX + pointSpacing / 3, y: previousY)
                let controlPoint2 = CGPoint(x: x - pointSpacing / 3, y: y)

                path.addCurve(to: CGPoint(x: x, y: y),
                            controlPoint1: controlPoint1,
                            controlPoint2: controlPoint2)
            }
        }

        shapeLayer.path = path.cgPath

        // Анимация при обновлении данных
        let animation = CABasicAnimation(keyPath: "strokeEnd")
        animation.fromValue = 0
        animation.toValue = 1
        animation.duration = 0.8
        shapeLayer.add(animation, forKey: "lineAnimation")
    }
}
```

### Стратегия 4: Module-by-Module (по модулям)

**Подход:** Мигрируем целые модули приложения постепенно.

```swift
// Модульная архитектура приложения
// App Structure:
// - Authentication Module (✅ Migrated to SwiftUI)
// - Home Module (⚠️ Hybrid)
// - Settings Module (✅ Migrated to SwiftUI)
// - Checkout Module (❌ Still UIKit - complex)

// 1. Authentication Module — полностью SwiftUI
struct AuthenticationCoordinator: View {
    @StateObject private var authViewModel = AuthenticationViewModel()

    var body: some View {
        NavigationStack {
            if authViewModel.isAuthenticated {
                MainAppView()
            } else {
                LoginView()
            }
        }
    }
}

// 2. Settings Module — полностью SwiftUI
struct SettingsCoordinator: View {
    var body: some View {
        NavigationStack {
            SettingsListView()
        }
    }
}

// 3. Checkout Module — остается UIKit (сложная логика платежей)
class CheckoutCoordinator {
    func startCheckout(from viewController: UIViewController,
                      with items: [CartItem]) {
        let checkoutVC = CheckoutViewController(items: items)
        let navigationController = UINavigationController(rootViewController: checkoutVC)
        viewController.present(navigationController, animated: true)
    }
}

// Главный app координатор объединяет модули
struct MainAppView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            // SwiftUI модуль
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)

            // SwiftUI модуль
            SettingsCoordinator()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(1)

            // UIKit модуль через обертку
            CheckoutWrapper()
                .tabItem {
                    Label("Cart", systemImage: "cart")
                }
                .tag(2)
        }
    }
}

struct CheckoutWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UINavigationController {
        let checkoutVC = CheckoutViewController(items: [])
        return UINavigationController(rootViewController: checkoutVC)
    }

    func updateUIViewController(_ uiViewController: UINavigationController, context: Context) {}
}
```

### Timeline миграции (типичный проект)

```
Месяц 1-2: Preparation & Small Wins
├─ Audit кодовой базы (выявить кандидатов на миграцию)
├─ Настройка SwiftUI Preview для существующих экранов
├─ Миграция 5-10 leaf components (кнопки, карточки)
└─ Training команды (SwiftUI basics)

Месяц 3-4: New Features in SwiftUI
├─ Все новые фичи пишем на SwiftUI
├─ Создание shared design system в SwiftUI
├─ Миграция 1-2 простых экранов целиком
└─ Настройка CI/CD для SwiftUI preview tests

Месяц 5-8: Major Screens Migration
├─ Миграция средних по сложности экранов
├─ Рефакторинг navigation flow (SwiftUI NavigationStack)
├─ Performance testing migrated screens
└─ Миграция 30-40% кодовой базы

Месяц 9-12: Complex Components
├─ Миграция сложных UIKit компонентов
├─ Или оставляем их в UIKit с обертками
├─ Finalize hybrid architecture
└─ 60-70% SwiftUI coverage

Долгосрочно (1+ год):
├─ Полная миграция (если целесообразно)
└─ Или стабильный hybrid подход
```

## Проверь себя

<details>
<summary><strong>Вопрос 1:</strong> Когда SwiftUI view пересоздается заново?</summary>

**Ответ:**

SwiftUI view (struct) **пересоздается (новый instance)** когда:
1. ✅ Изменяется `@State` property внутри view
2. ✅ Изменяется `@Binding` переданный в view
3. ✅ Изменяется `@ObservedObject` или `@StateObject` (их `@Published` свойства)
4. ✅ Parent view пересоздается и передает новые параметры
5. ✅ Изменяется `id()` modifier view

**Важно:** Пересоздание struct ≠ перерисовка UI. SwiftUI создает новый struct, но сравнивает его с предыдущим (diffing) и обновляет только измененные части UI.

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        // ✅ Этот body вызывается при каждом изменении @State
        print("Body called") // Увидите в консоли при каждом тапе

        return VStack {
            Text("Count: \(count)")
            Button("Increment") {
                count += 1 // Триггерит пересоздание view
            }
        }
    }
}
```

**View НЕ пересоздается когда:**
- Изменяются обычные (non-property-wrapper) свойства в другом месте
- Таймер тикает, но не обновляет tracked state
- Background task выполняется без обновления state
</details>

<details>
<summary><strong>Вопрос 2:</strong> Какая разница между @StateObject и @ObservedObject?</summary>

**Ответ:**

| Aspect | @StateObject | @ObservedObject |
|--------|--------------|-----------------|
| **Ownership** | View владеет объектом | View НЕ владеет, получает извне |
| **Lifecycle** | Создается 1 раз, живет пока view alive | Может пересоздаваться при recreate view |
| **Использование** | View создает и управляет ViewModel | Parent передает существующий объект |
| **Memory** | View ответственен за dealloc | Кто-то другой управляет памятью |

```swift
// ✅ @StateObject — view создает и владеет
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()
    // viewModel создается 1 раз и сохраняется даже при recreate ProfileView

    var body: some View {
        Text(viewModel.userName)
    }
}

// ✅ @ObservedObject — view получает извне
struct ProfileDetailView: View {
    @ObservedObject var viewModel: ProfileViewModel
    // viewModel передается от parent, может измениться при recreate

    var body: some View {
        Text(viewModel.userName)
    }
}

// Использование
struct ParentView: View {
    @StateObject private var sharedViewModel = ProfileViewModel()

    var body: some View {
        VStack {
            ProfileView() // Создает свой ViewModel

            ProfileDetailView(viewModel: sharedViewModel) // Получает shared
        }
    }
}
```

**Правило:**
- Используй `@StateObject` где создаешь объект (`= MyViewModel()`)
- Используй `@ObservedObject` где получаешь объект (parameter)
</details>

<details>
<summary><strong>Вопрос 3:</strong> Как правильно обновлять UIKit view из SwiftUI при изменении данных?</summary>

**Ответ:**

Используй метод `updateUIView(_:context:)` в `UIViewRepresentable`:

```swift
struct CorrectMapView: UIViewRepresentable {
    var coordinate: CLLocationCoordinate2D // SwiftUI следит за изменениями
    var zoomLevel: Double

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        // ✅ ТОЛЬКО одноразовая настройка здесь
        mapView.showsUserLocation = true
        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        // ✅ Вызывается при изменении coordinate или zoomLevel
        let region = MKCoordinateRegion(
            center: coordinate,
            span: MKCoordinateSpan(
                latitudeDelta: zoomLevel,
                longitudeDelta: zoomLevel
            )
        )
        mapView.setRegion(region, animated: true)
    }
}

// SwiftUI автоматически вызовет updateUIView при изменении
struct MapContainer: View {
    @State private var coordinate = CLLocationCoordinate2D(
        latitude: 37.7749,
        longitude: -122.4194
    )

    var body: some View {
        VStack {
            CorrectMapView(coordinate: coordinate, zoomLevel: 0.1)

            Button("Move to New York") {
                coordinate = CLLocationCoordinate2D(
                    latitude: 40.7128,
                    longitude: -74.0060
                )
                // ✅ updateUIView вызовется автоматически
            }
        }
    }
}
```

**Ошибки которых избегать:**
- ❌ Обновлять данные в `makeUIView` — вызывается только 1 раз
- ❌ Не реализовывать `updateUIView` — изменения не применятся
- ❌ Создавать новый UIView в `updateUIView` — это для обновлений, не создания
</details>

<details>
<summary><strong>Вопрос 4:</strong> Когда выбрать UIKit вместо SwiftUI в новом проекте (2026)?</summary>

**Ответ:**

Выбирай UIKit если:

1. **Legacy Support Critical**
   ```swift
   // Нужна поддержка iOS 12 или ниже
   // SwiftUI требует минимум iOS 13
   ```

2. **Pixel-Perfect Custom UI**
   ```swift
   // Сложные custom shapes, animations, transitions
   // Например: banking app с custom charts, animated cards
   // UIKit + Core Animation дают больше контроля
   ```

3. **Performance Critical Lists**
   ```swift
   // Списки с 10,000+ элементов и complex cell UI
   // UITableView с prefetching более предсказуем
   // SwiftUI List может иметь frame drops на сложных данных
   ```

4. **Existing UIKit Team**
   ```swift
   // Команда имеет 5+ лет опыта UIKit, 0 опыта SwiftUI
   // Обучение займет 3-6 месяцев
   // Для tight deadline лучше использовать существующую экспертизу
   ```

5. **Enterprise Constraints**
   ```swift
   // Корпоративные политики требуют проверенные технологии
   // SwiftUI еще не одобрен security team
   // Нужна certification для медицинских/финансовых приложений
   ```

**НО в 2026 году для большинства новых проектов:**
✅ SwiftUI с iOS 15+ target — оптимальный выбор
✅ Гибридный подход (SwiftUI + UIKit для edge cases) — лучшая стратегия
❌ Pure UIKit для нового проекта — редко оправдано
</details>

<details>
<summary><strong>Вопрос 5:</strong> Как избежать memory leaks при интеграции SwiftUI и UIKit?</summary>

**Ответ:**

**Проблема:** Retain cycles между SwiftUI Coordinator и UIKit delegates.

**Решения:**

1. **Используй `[weak self]` в closures**
```swift
struct SafeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> CustomVC {
        let vc = CustomVC()
        vc.onDismiss = { [weak vc] in // ✅ weak reference
            vc?.dismiss(animated: true)
        }
        return vc
    }
}
```

2. **Coordinator для делегатов**
```swift
struct SafeMapView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: SafeMapView

        init(_ parent: SafeMapView) {
            self.parent = parent
        }

        // ✅ Coordinator разрывает retain cycle
        func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
            parent.onAnnotationTap()
        }
    }
}
```

3. **Cleanup в dismantleUIView**
```swift
struct ProperCleanupView: UIViewRepresentable {
    func makeUIView(context: Context) -> CustomView {
        let view = CustomView()
        view.delegate = context.coordinator
        return view
    }

    func updateUIView(_ uiView: CustomView, context: Context) {}

    static func dismantleUIView(_ uiView: CustomView, coordinator: Coordinator) {
        // ✅ Очистка при удалении view
        uiView.delegate = nil
        uiView.cleanup()
    }
}
```

4. **Testing leaks**
```swift
func testNoMemoryLeaks() {
    weak var weakVC: UIViewController?

    autoreleasepool {
        let vc = UIHostingController(rootView: MyView())
        weakVC = vc
        // Используем vc
    }

    XCTAssertNil(weakVC, "Memory leak detected") // ✅ Должен быть nil
}
```
</details>

<details>
<summary><strong>Вопрос 6:</strong> Какая производительность лучше: SwiftUI List vs UITableView?</summary>

**Ответ:**

**Зависит от сценария:**

| Сценарий | Победитель | Почему |
|----------|-----------|--------|
| Simple list (< 100 items) | Паритет | Оба 60fps |
| Simple list (< 1000 items) | SwiftUI | Меньше кода, такая же производительность |
| Complex cells (images, nested views) | UITableView | Лучше контроль над reuse |
| Dynamic height calculations | SwiftUI | Автоматический layout |
| Prefetching данных | UITableView | Explicit prefetching API |
| Smooth scrolling (10K+ items) | UITableView | Более предсказуемый |
| Разработка и поддержка | SwiftUI | 5-10x меньше кода |

**Бенчмарки (iPhone 14 Pro, iOS 17):**

```swift
// SwiftUI List — простые элементы
struct SwiftUIListTest: View {
    let items = (0..<10000).map { "Item \($0)" }

    var body: some View {
        List(items, id: \.self) { item in
            Text(item)
        }
    }
}
// Результат: 60fps, smooth scrolling ✅

// SwiftUI List — сложные элементы
struct ComplexSwiftUIList: View {
    let items: [ComplexItem] // 10,000 items

    var body: some View {
        List(items) { item in
            HStack {
                AsyncImage(url: item.imageURL)
                    .frame(width: 50, height: 50)
                VStack(alignment: .leading) {
                    Text(item.title).font(.headline)
                    Text(item.subtitle).font(.caption)
                }
            }
        }
    }
}
// Результат: 45-50fps, occasional stutters ⚠️

// UITableView — сложные элементы
class OptimizedTableView: UITableViewController {
    var items: [ComplexItem] = Array(repeating: ComplexItem(), count: 10000)

    override func tableView(_ tableView: UITableView,
                           cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        // Manual cell configuration with prefetching
        return cell
    }
}
// Результат: 60fps, smooth scrolling ✅
```

**Рекомендация 2026:**
- ✅ Используй SwiftUI List для 90% случаев
- ⚠️ Переходи на UITableView если видишь performance issues
- ✅ LazyVStack в SwiftUI как альтернатива List для большего контроля
</details>

## Связанные темы

- [[ios-architecture-patterns]] — MVVM, Clean Architecture, Coordinator
- [[ios-state-management]] — @State, @Binding, Combine, TCA
- [[ios-navigation-patterns]] — NavigationStack vs UINavigationController
- [[ios-performance-optimization]] — Instruments, memory profiling
- [[ios-testing-strategies]] — Unit tests, UI tests, Preview tests
- [[ios-async-await]] — Modern concurrency в SwiftUI и UIKit
- [[ios-combine-framework]] — Reactive programming для SwiftUI
- [[ios-core-animation]] — Custom animations в UIKit
- [[ios-accessibility]] — VoiceOver, Dynamic Type support
- [[ios-app-lifecycle]] — Scene-based lifecycle в SwiftUI
- [[ios-widgets-development]] — WidgetKit и Live Activities
- [[ios-design-system]] — Создание переиспользуемых компонентов
- [[swift-property-wrappers]] — @State, @Binding, custom wrappers
- [[ios-migration-best-practices]] — Стратегии постепенной миграции

---

**Последнее обновление:** 2026-01-11
**Автор:** iOS Development Knowledge Base
**Статус:** Production-ready guide для выбора между SwiftUI и UIKit
