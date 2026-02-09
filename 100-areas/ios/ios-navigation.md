---
date: 2026-01-11
type: deep-dive
area: ios
tags: [navigation, uikit, swiftui, architecture, routing]
---

# iOS Navigation: Полное руководство по UIKit и SwiftUI

## TL;DR

Навигация в iOS — это управление переходами между экранами приложения. UIKit предоставляет императивный подход через UINavigationController и модальные презентации, SwiftUI использует декларативный подход с NavigationStack и привязкой к состоянию. Оба фреймворка поддерживают три основных паттерна: навигационный стек (иерархия), вкладки (параллельные потоки) и модальные окна (временный контекст).

**Ключевые концепции:**
- **UIKit**: UINavigationController (push/pop), UITabBarController, present/dismiss
- **SwiftUI**: NavigationStack, NavigationPath, TabView, sheet/fullScreenCover
- **Universal**: Deep linking, state restoration, coordinator pattern

---

## Зачем это нужно?

Навигация — это скелет любого iOS приложения. Она определяет, как пользователь перемещается по вашему контенту, как приложение реагирует на глубокие ссылки, и как сохраняется состояние при сворачивании приложения.

**Без правильной навигации:**
- Пользователи теряются в интерфейсе
- Невозможно реализовать deep linking
- Теряется состояние приложения при переключении
- Усложняется тестирование и модульность кода

**С правильной навигацией:**
- Интуитивный пользовательский опыт
- Поддержка Universal Links и Spotlight
- State restoration "из коробки"
- Четкая архитектура и тестируемый код

---

## Жизненные аналогии

### 1. Навигационный стек = Стопка книг
Когда вы читаете книгу и видите ссылку на другую книгу, вы кладете текущую на стол и берете новую. Чтобы вернуться, вы просто откладываете верхнюю книгу. UINavigationController работает так же: каждый новый экран кладется на стек, свайп назад — снимает верхний экран.

```
[Book 3: Detail]     ← Текущая книга
[Book 2: List]       ← Предыдущая
[Book 1: Home]       ← Начальная
```

### 2. TabBar = Комнаты в квартире
У вас есть кухня, спальня, ванная — каждая комната существует параллельно. Вы можете мгновенно перейти из кухни в спальню, и вещи в кухне останутся на своих местах. TabBar работает так же: каждая вкладка — независимый контекст с собственным состоянием.

### 3. Модальное окно = Звонок в дверь
Вы готовите ужин, и вдруг звонят в дверь. Вы прерываете готовку, открываете дверь (модальное окно), решаете вопрос, закрываете дверь и возвращаетесь к готовке. Модальные окна — это временное прерывание основного потока для важного действия.

### 4. Deep Link = Закладка в книге
Вместо того, чтобы читать книгу с начала, вы открываете её на нужной странице по закладке. Deep link позволяет открыть приложение сразу на конкретном экране, минуя весь путь навигации.

---

## ASCII диаграммы навигационных иерархий

### UIKit Navigation Stack

```
┌─────────────────────────────────────────┐
│       UINavigationController            │
│  ┌──────────────────────────────────┐   │
│  │  Navigation Bar                  │   │
│  │  [< Back]      Title      [Edit] │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │                                  │   │
│  │    View Controller Content       │   │
│  │                                  │   │
│  │  Stack: [Root → List → Detail]  │   │
│  │                        ↑ Current │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘

Push:    Root → List → Detail → EditDetail
Pop:     Root → List → Detail ← (removed)
```

### UIKit Tab Bar Structure

```
┌──────────────────────────────────────────┐
│          UITabBarController              │
├──────────────┬──────────────┬────────────┤
│   Nav Stack  │  Nav Stack   │  Nav Stack │
│   ┌────┐     │   ┌────┐     │  ┌────┐    │
│   │Feed│     │   │Search    │  │Profile  │
│   └────┘     │   └────┘     │  └────┘    │
│     ↓        │     ↓         │    ↓       │
│   Detail     │   Results     │  Settings  │
└──────────────┴──────────────┴────────────┘
   [Feed]        [Search]       [Profile]
    (selected)
```

### SwiftUI NavigationStack (iOS 16+)

```
┌─────────────────────────────────────────┐
│      NavigationStack(path: $path)       │
│  ┌──────────────────────────────────┐   │
│  │  NavigationBar (automatic)       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Root View                       │   │
│  │    NavigationLink → Destination  │   │
│  │                                  │   │
│  │  path: [Item1, Item2, Item3]    │   │
│  │                          ↑       │   │
│  │                     Current      │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘

path.append(item)  → adds to stack
path.removeLast()  → pops back
path = []          → returns to root
```

### SwiftUI Modal Presentation Flow

```
┌─────────────────────────────────────────┐
│         Main View (Base Layer)          │
│  ┌──────────────────────────────────┐   │
│  │  Content                         │   │
│  │  Button → .sheet(isPresented:)  │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Sheet (slides up from bottom)        │
│  ┌──────────────────────────────────┐   │
│  │  Modal Content                   │   │
│  │  Dismiss → isPresented = false   │   │
│  └──────────────────────────────────┘   │
│  [ Swipe down to dismiss ]              │
└─────────────────────────────────────────┘

Variants:
.sheet          → Card with dismiss gesture
.fullScreenCover → Full screen, no dismiss gesture
.popover        → iPad/Mac popover balloon
```

### Deep Linking Navigation Flow

```
Universal Link: https://app.com/user/123/post/456
                        ↓
┌─────────────────────────────────────────┐
│  App Delegate / Scene Delegate          │
│  func scene(_ scene: continue:)         │
└─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────┐
│  Router / Coordinator                    │
│  Parse: /user/123/post/456              │
└─────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────┐
│  Build Navigation Stack:                 │
│  Root → UserProfile(123) → Post(456)    │
└─────────────────────────────────────────┘
```

---

## 6 типичных ошибок

### ❌ Ошибка 1: Retain Cycle в UIKit навигации

```swift
// ПЛОХО: Захватываем self в замыкании без [weak self]
class ProductListViewController: UIViewController {
    func showDetail(product: Product) {
        let detailVC = ProductDetailViewController()
        // ПОЧЕМУ плохо: При push создается сильная ссылка,
        // и если detailVC захватывает self, получается retain cycle
        detailVC.onDelete = {
            self.removeProduct(product) // Утечка памяти!
        }
        navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

### ✅ Правильно: Используем [weak self]

```swift
// ХОРОШО: Разрываем цикл с [weak self]
class ProductListViewController: UIViewController {
    func showDetail(product: Product) {
        let detailVC = ProductDetailViewController()
        // ПОЧЕМУ хорошо: weak self позволяет контроллеру
        // освободиться, если пользователь уйдет со страницы
        detailVC.onDelete = { [weak self] in
            self?.removeProduct(product)
        }
        navigationController?.pushViewController(detailVC, animated: true)
    }
}
```

---

### ❌ Ошибка 2: Неправильная очистка стека в UIKit

```swift
// ПЛОХО: Попытка вернуться на корень через pop
class SettingsViewController: UIViewController {
    func logout() {
        // ПОЧЕМУ плохо: Если в стеке 5 экранов,
        // это создаст 5 анимаций подряд = плохой UX
        while navigationController?.viewControllers.count ?? 0 > 1 {
            navigationController?.popViewController(animated: true)
        }
    }
}
```

### ✅ Правильно: Используем popToRootViewController

```swift
// ХОРОШО: Одна анимация возвращает на корень
class SettingsViewController: UIViewController {
    func logout() {
        // ПОЧЕМУ хорошо: Одна плавная анимация,
        // все промежуточные контроллеры освобождаются сразу
        navigationController?.popToRootViewController(animated: true)

        // Или прямой переход к конкретному контроллеру
        if let targetVC = navigationController?.viewControllers
            .first(where: { $0 is LoginViewController }) {
            navigationController?.popToViewController(targetVC, animated: true)
        }
    }
}
```

---

### ❌ Ошибка 3: Множественные NavigationStack в SwiftUI

```swift
// ПЛОХО: NavigationStack внутри NavigationStack
struct ContentView: View {
    var body: some View {
        NavigationStack {
            NavigationStack { // ПОЧЕМУ плохо: Двойная навигация!
                List {
                    NavigationLink("Item", value: "detail")
                }
            }
            .navigationTitle("Outer")
        }
    }
}
// Результат: Две навигационные панели, конфликты анимаций
```

### ✅ Правильно: Один NavigationStack на корневом уровне

```swift
// ХОРОШО: Один NavigationStack управляет всей иерархией
struct ContentView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Item", value: "detail")
            }
            .navigationTitle("Main")
            // ПОЧЕМУ хорошо: Одна навигация,
            // все дочерние экраны автоматически получают back button
            .navigationDestination(for: String.self) { value in
                DetailView(value: value)
            }
        }
    }
}
```

---

### ❌ Ошибка 4: Игнорирование NavigationPath для программной навигации

```swift
// ПЛОХО: Использование isActive для сложной навигации
struct ProductsView: View {
    @State private var showDetail1 = false
    @State private var showDetail2 = false
    @State private var showDetail3 = false
    // ПОЧЕМУ плохо: Не масштабируется, сложно управлять

    var body: some View {
        NavigationStack {
            VStack {
                NavigationLink(isActive: $showDetail1) {
                    DetailView1()
                } label: { Text("Detail 1") }

                NavigationLink(isActive: $showDetail2) {
                    DetailView2()
                } label: { Text("Detail 2") }
            }
        }
    }
}
```

### ✅ Правильно: Используем NavigationPath для типобезопасности

```swift
// ХОРОШО: Централизованное управление навигацией
struct ProductsView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            List {
                Button("Show Product 1") {
                    // ПОЧЕМУ хорошо: Можно добавлять любые типы,
                    // легко управлять всем стеком программно
                    navigationPath.append(Product(id: 1))
                }

                Button("Deep Link: Product → Reviews") {
                    // Программный переход на несколько уровней
                    navigationPath.append(Product(id: 2))
                    navigationPath.append(ReviewsScreen())
                }

                Button("Go to Root") {
                    // Одна строка очищает весь стек
                    navigationPath.removeLast(navigationPath.count)
                }
            }
            .navigationDestination(for: Product.self) { product in
                ProductDetailView(product: product)
            }
            .navigationDestination(for: ReviewsScreen.self) { _ in
                ReviewsView()
            }
        }
    }
}
```

---

### ❌ Ошибка 5: Неправильная обработка dismiss в модальных окнах SwiftUI

```swift
// ПЛОХО: Передача Binding глубоко в иерархию
struct ParentView: View {
    @State private var showSheet = false

    var body: some View {
        Button("Show") { showSheet = true }
            .sheet(isPresented: $showSheet) {
                // ПОЧЕМУ плохо: Передача Binding создает
                // тесную связь между уровнями
                ModalView(isPresented: $showSheet)
            }
    }
}

struct ModalView: View {
    @Binding var isPresented: Bool

    var body: some View {
        ChildView(isPresented: $isPresented) // Передаем дальше
    }
}
```

### ✅ Правильно: Используем @Environment(\.dismiss)

```swift
// ХОРОШО: Environment автоматически доступен везде
struct ParentView: View {
    @State private var showSheet = false

    var body: some View {
        Button("Show") { showSheet = true }
            .sheet(isPresented: $showSheet) {
                ModalView()
                // ПОЧЕМУ хорошо: Не нужно передавать Binding
            }
    }
}

struct ModalView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ChildView() // Дочерний компонент тоже может dismiss
                .toolbar {
                    Button("Close") { dismiss() }
                }
        }
    }
}

struct ChildView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        Button("Save & Close") {
            // ПОЧЕМУ хорошо: Любой уровень вложенности
            // может закрыть модальное окно без Binding
            saveData()
            dismiss()
        }
    }
}
```

---

### ❌ Ошибка 6: Игнорирование State Restoration

```swift
// ПЛОХО: Нет поддержки восстановления состояния
class ProductListViewController: UIViewController {
    var products: [Product] = []
    var selectedProduct: Product?

    // ПОЧЕМУ плохо: Если пользователь свернет приложение
    // на детальном экране товара, при возврате
    // он окажется на списке товаров (потеря контекста)

    override func viewDidLoad() {
        super.viewDidLoad()
        loadProducts()
    }
}
```

### ✅ Правильно: Реализуем State Restoration

```swift
// ХОРОШО: UIKit State Restoration
class ProductListViewController: UIViewController {
    var products: [Product] = []
    var selectedProduct: Product?

    override func viewDidLoad() {
        super.viewDidLoad()
        // ПОЧЕМУ хорошо: iOS запомнит путь навигации
        restorationIdentifier = "ProductList"
        restorationClass = ProductListViewController.self
        loadProducts()
    }

    override func encodeRestorableState(with coder: NSCoder) {
        super.encodeRestorableState(with: coder)
        // Сохраняем состояние
        if let productID = selectedProduct?.id {
            coder.encode(productID, forKey: "selectedProductID")
        }
    }

    override func decodeRestorableState(with coder: NSCoder) {
        super.decodeRestorableState(with: coder)
        // Восстанавливаем состояние
        if let productID = coder.decodeObject(forKey: "selectedProductID") as? String {
            selectedProduct = products.first { $0.id == productID }
        }
    }
}

// SwiftUI автоматически сохраняет NavigationPath:
struct ProductsView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            // ПОЧЕМУ хорошо: SwiftUI автоматически
            // сохраняет и восстанавливает navigationPath
            // при условии, что типы Codable
            List(products) { product in
                NavigationLink(value: product) {
                    Text(product.name)
                }
            }
            .navigationDestination(for: Product.self) { product in
                ProductDetailView(product: product)
            }
        }
    }
}
```

---

## 4 ментальные модели

### 1. Стек vs Граф: Понимание навигационной структуры

**Стек (Stack)**: Линейная история переходов
- Можно вернуться только на предыдущий экран
- LIFO (Last In, First Out) — последний добавленный, первый удаляется
- UINavigationController, NavigationStack

**Граф (Graph)**: Произвольные переходы
- Можно перейти куда угодно из любого места
- Требует явного управления состоянием
- Coordinator pattern, Deep links

```
Стек:              Граф:
A → B → C          A ⟷ B
    ↑                ↕   ↕
   Back            C ⟷ D
                     ↕
                     E
```

**Когда использовать:**
- **Стек**: Drill-down навигация (список → деталь → редактирование)
- **Граф**: Сложные потоки (онбординг, многошаговые формы)

---

### 2. Ownership: Кто владеет навигацией?

**View-Driven (SwiftUI по умолчанию)**:
- View решает, когда и куда переходить
- Навигация привязана к состоянию UI
- Просто для простых случаев, сложно тестировать

**Coordinator-Driven (рекомендуется для больших проектов)**:
- Отдельный объект управляет навигацией
- View не знает о других экранах
- Легко тестировать, переиспользовать, менять потоки

```swift
// View-Driven (простой случай)
struct UserListView: View {
    var body: some View {
        NavigationLink("User", value: user) // View решает
    }
}

// Coordinator-Driven (масштабируемый)
class UserCoordinator {
    func showUserDetail(_ user: User) {
        // Coordinator решает КАК и ГДЕ показать
        let detailView = UserDetailView(user: user)
        navigationController.push(detailView)
    }
}
```

---

### 3. Модальность: Прерывание vs Продолжение

**Modal = Прерывание потока**:
- Требует действия перед возвратом
- Должен быть способ закрыть (dismiss button)
- Примеры: создание контента, авторизация, алерт

**Push = Продолжение потока**:
- Естественное углубление в контент
- Back button автоматически добавляется
- Примеры: детали товара, профиль пользователя

```
Вопрос: Модально или push?

Создать пост       → Modal (прерывание, нужно Save/Cancel)
Открыть пост       → Push (продолжение просмотра)
Войти в аккаунт    → Modal (блокирует основной поток)
Настройки профиля  → Push (часть основного потока)
```

---

### 4. Императив vs Декларатив: Разные философии

**UIKit (Императивный)**: Вы говорите КАК навигировать
```swift
// Явно вызываете методы навигации
navigationController?.pushViewController(vc, animated: true)
present(modal, animated: true)
dismiss(animated: true)
```

**SwiftUI (Декларативный)**: Вы описываете КАКОЕ состояние ведет к навигации
```swift
// Навигация — следствие изменения состояния
@State private var isShowingDetail = true

// Когда isShowingDetail == true, показывается sheet
.sheet(isPresented: $isShowingDetail) { DetailView() }
```

**Преимущества декларативного:**
- Навигация автоматически синхронизирована с состоянием
- Нет рассинхронизации UI и данных
- Легче рассуждать о коде

**Преимущества императивного:**
- Полный контроль над анимациями и таймингом
- Проще понять для начинающих (явные действия)
- Больше гибкости в сложных случаях

---

## Проверь себя

### Вопрос 1: Стек навигации
У вас есть стек: Root → List → Detail → Edit. Пользователь нажимает "Save" в Edit, и нужно вернуться на List, пропустив Detail. Как это сделать в SwiftUI с NavigationPath?

<details>
<summary>Ответ</summary>

```swift
// ПОЧЕМУ это работает: NavigationPath позволяет
// удалять элементы из середины стека
@State private var path = NavigationPath()

// В кнопке Save:
Button("Save") {
    saveData()
    // Удаляем последние 2 элемента (Edit и Detail)
    path.removeLast(2)
}

// Альтернатива: вернуться к корню и добавить нужный экран
Button("Save & Show List") {
    let listData = path[path.count - 3] // Сохраняем List
    path = NavigationPath()
    path.append(listData)
}
```
</details>

---

### Вопрос 2: Модальные окна
В SwiftUI у вас есть sheet с формой. Внутри sheet есть NavigationStack с несколькими экранами. Пользователь на 3-м уровне навигации нажимает "Cancel". Что произойдет при вызове `dismiss()`?

<details>
<summary>Ответ</summary>

`dismiss()` закроет весь sheet целиком, включая все уровни NavigationStack внутри него.

```swift
// ПОЧЕМУ: dismiss() закрывает ближайший presentation context,
// которым является sheet, а не отдельные уровни навигации

.sheet(isPresented: $showForm) {
    NavigationStack {
        FormLevel1()
            .navigationDestination(...) { FormLevel2() }
            .navigationDestination(...) { FormLevel3() }
    }
}

// В FormLevel3:
@Environment(\.dismiss) var dismiss
Button("Cancel") {
    dismiss() // Закроет весь sheet, не только Level3
}

// Чтобы закрыть только Level3:
@State private var path = NavigationPath()
Button("Back") {
    path.removeLast() // Только pop в NavigationStack
}
```
</details>

---

### Вопрос 3: UIKit Memory Management
У вас есть UINavigationController с 5 экранами в стеке. Вы вызываете `popToRootViewController(animated: true)`. Когда освободятся промежуточные 4 контроллера?

<details>
<summary>Ответ</summary>

Контроллеры освободятся сразу после завершения анимации, **если нет сильных ссылок на них** из других объектов.

```swift
// ПОЧЕМУ: popToRootViewController удаляет контроллеры
// из массива viewControllers, уменьшая retain count до 0

// ПРАВИЛЬНО: Контроллеры освободятся
navigationController?.popToRootViewController(animated: true)

// УТЕЧКА: Если вы держите сильную ссылку
class SomeManager {
    var cachedController: UIViewController? // Strong reference!
}

// После pop контроллер останется в памяти из-за cachedController

// ИСПРАВЛЕНИЕ: Используйте weak ссылки для кеширования
class SomeManager {
    weak var cachedController: UIViewController? // Weak!
}
```
</details>

---

### Вопрос 4: Deep Linking
Вам приходит Universal Link `myapp://products/123/reviews`. В SwiftUI с NavigationStack, как построить стек "Root → Product(123) → Reviews"?

<details>
<summary>Ответ</summary>

```swift
// ПОЧЕМУ это работает: NavigationPath принимает массив типов,
// которые соответствуют navigationDestination

struct AppView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            RootView()
                .navigationDestination(for: Product.self) { product in
                    ProductDetailView(product: product)
                }
                .navigationDestination(for: ReviewsDestination.self) { _ in
                    ReviewsView()
                }
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }

    func handleDeepLink(_ url: URL) {
        // Парсим: myapp://products/123/reviews
        guard let productID = extractProductID(from: url) else { return }

        // ПОЧЕМУ важен порядок: NavigationStack показывает
        // элементы в порядке добавления в path
        navigationPath.append(Product(id: productID))
        navigationPath.append(ReviewsDestination())

        // Результат: Root → Product(123) → Reviews
    }
}

struct ReviewsDestination: Hashable {}
```

Альтернатива для UIKit:
```swift
func handleDeepLink(_ url: URL) {
    guard let productID = extractProductID(from: url) else { return }

    let productVC = ProductDetailViewController(productID: productID)
    let reviewsVC = ReviewsViewController(productID: productID)

    // ПОЧЕМУ setViewControllers: мгновенно заменяет весь стек
    // без анимаций промежуточных переходов
    navigationController?.setViewControllers([
        rootVC,
        productVC,
        reviewsVC
    ], animated: true)
}
```
</details>

---

### Вопрос 5: Tab Bar + Navigation
У вас TabBar с 3 вкладками, каждая с NavigationStack. Пользователь на вкладке A перешел на 3 уровень, переключился на вкладку B, потом вернулся на A. Где он окажется?

<details>
<summary>Ответ</summary>

На 3-м уровне вкладки A — состояние каждой вкладки сохраняется.

```swift
// ПОЧЕМУ: TabView (SwiftUI) и UITabBarController (UIKit)
// держат в памяти все вкладки и их состояние

// SwiftUI:
TabView {
    NavigationStack {
        ViewA() // Стек A сохраняется
    }
    .tabItem { Label("A", systemImage: "1.circle") }

    NavigationStack {
        ViewB() // Стек B сохраняется
    }
    .tabItem { Label("B", systemImage: "2.circle") }
}

// UIKit:
let tabBarController = UITabBarController()
let navA = UINavigationController(rootViewController: ViewControllerA())
let navB = UINavigationController(rootViewController: ViewControllerB())
tabBarController.viewControllers = [navA, navB]

// Каждый UINavigationController независим,
// их стеки не очищаются при переключении вкладок

// ВНИМАНИЕ: Если вкладок много (>5), iOS может выгрузить
// контроллеры неактивных вкладок для экономии памяти (viewDidLoad вызовется снова)
```
</details>

---

### Вопрос 6: Анимации навигации
В UIKit вы делаете `pushViewController(animated: false)` а затем сразу `popViewController(animated: true)`. Что увидит пользователь?

<details>
<summary>Ответ</summary>

Пользователь увидит анимацию pop (возврат назад), но не увидит push.

```swift
// ПОЧЕМУ: animated: false делает переход мгновенным
navigationController?.pushViewController(detailVC, animated: false)
// Стек сейчас: [Root, Detail]

navigationController?.popViewController(animated: true)
// Пользователь видит анимацию возврата с Detail на Root

// РЕАЛЬНЫЙ СЛУЧАЙ: Deep linking
func handleDeepLink() {
    // Строим стек без анимаций
    navigationController?.pushViewController(productVC, animated: false)
    navigationController?.pushViewController(reviewsVC, animated: false)

    // Последний переход с анимацией для UX
    navigationController?.pushViewController(commentVC, animated: true)

    // Пользователь видит только последний переход,
    // но стек правильный для back button
}

// ВАЖНО: Не вызывайте push/pop в viewDidLoad или viewWillAppear —
// это конфликтует с собственными анимациями навигации
```
</details>

---

## Связанные темы

- [[swift-concurrency]] — async/await для загрузки данных при навигации
- [[swiftui-state-management]] — @State, @Binding, @ObservedObject для навигации
- [[uikit-lifecycle]] — viewDidLoad, viewWillAppear для UIKit навигации
- [[combine-framework]] — реактивная навигация с Publishers
- [[coordinator-pattern]] — архитектурный паттерн для сложной навигации
- [[deep-linking-ios]] — Universal Links, URL Schemes, Spotlight
- [[ios-animations]] — кастомные transition анимации
- [[swiftui-architecture]] — MVVM, TCA для SwiftUI навигации
- [[uikit-storyboards-xibs]] — Segues и Storyboard навигация
- [[ios-accessibility]] — VoiceOver навигация и фокус менеджмент
- [[android-navigation]] — сравнение с Navigation Component, Jetpack Compose Navigation
- [[state-restoration-ios]] — восстановление навигационного стека
- [[ipad-multitasking]] — NavigationSplitView, Split View навигация
- [[ios-design-patterns]] — паттерны проектирования для навигации

---

## Практические примеры

### UIKit: Полноценный навигационный поток

```swift
import UIKit

// ПОЧЕМУ так: Coordinator убирает навигационную логику из контроллеров
class AppCoordinator {
    let navigationController: UINavigationController

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        let productsVC = ProductsViewController()
        productsVC.coordinator = self
        navigationController.pushViewController(productsVC, animated: false)
    }

    func showProductDetail(_ product: Product) {
        let detailVC = ProductDetailViewController(product: product)
        detailVC.coordinator = self
        // ПОЧЕМУ animated: true для пользовательских переходов
        navigationController.pushViewController(detailVC, animated: true)
    }

    func showReviews(for product: Product) {
        let reviewsVC = ReviewsViewController(product: product)
        navigationController.pushViewController(reviewsVC, animated: true)
    }

    func showCreateReview(for product: Product) {
        let createVC = CreateReviewViewController(product: product)
        createVC.coordinator = self
        let navVC = UINavigationController(rootViewController: createVC)
        // ПОЧЕМУ modal: создание контента — это прерывание основного потока
        navigationController.present(navVC, animated: true)
    }

    func dismissModal() {
        navigationController.dismiss(animated: true)
    }
}

class ProductsViewController: UIViewController {
    weak var coordinator: AppCoordinator?

    override func viewDidLoad() {
        super.viewDidLoad()
        // ПОЧЕМУ в viewDidLoad: настройка UI происходит один раз
        title = "Products"
        navigationItem.largeTitleDisplayMode = .always
        setupTableView()
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let product = products[indexPath.row]
        // ПОЧЕМУ coordinator: контроллер не знает о других экранах
        coordinator?.showProductDetail(product)
    }
}

class ProductDetailViewController: UIViewController {
    weak var coordinator: AppCoordinator?
    let product: Product

    init(product: Product) {
        self.product = product
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) not supported")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = product.name

        // ПОЧЕМУ navigationItem.rightBarButtonItem:
        // стандартное место для действий на iOS
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            title: "Reviews",
            style: .plain,
            target: self,
            action: #selector(showReviews)
        )
    }

    @objc func showReviews() {
        coordinator?.showReviews(for: product)
    }
}
```

---

### SwiftUI: Программная навигация с типобезопасностью

```swift
import SwiftUI

// ПОЧЕМУ enum: типобезопасность, централизованное управление
enum AppRoute: Hashable {
    case productDetail(Product)
    case reviews(Product)
    case createReview(Product)
    case userProfile(User)
}

class NavigationRouter: ObservableObject {
    @Published var path = NavigationPath()
    @Published var presentedSheet: AppRoute?

    func navigate(to route: AppRoute) {
        // ПОЧЕМУ switch: компилятор проверит все случаи
        switch route {
        case .productDetail, .reviews, .userProfile:
            // ПОЧЕМУ append: добавляем в стек для push-навигации
            path.append(route)
        case .createReview:
            // ПОЧЕМУ presentedSheet: модальное окно для создания
            presentedSheet = route
        }
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        // ПОЧЕМУ removeLast(count): одна операция вместо цикла
        path.removeLast(path.count)
    }
}

struct AppView: View {
    @StateObject private var router = NavigationRouter()

    var body: some View {
        NavigationStack(path: $router.path) {
            ProductListView()
                .navigationDestination(for: AppRoute.self) { route in
                    // ПОЧЕМУ switch: типобезопасное создание views
                    switch route {
                    case .productDetail(let product):
                        ProductDetailView(product: product)
                    case .reviews(let product):
                        ReviewsView(product: product)
                    case .userProfile(let user):
                        UserProfileView(user: user)
                    default:
                        EmptyView()
                    }
                }
                // ПОЧЕМУ sheet с item: автоматически показывает/скрывает
                .sheet(item: $router.presentedSheet) { route in
                    switch route {
                    case .createReview(let product):
                        CreateReviewView(product: product)
                    default:
                        EmptyView()
                    }
                }
        }
        .environmentObject(router)
    }
}

struct ProductListView: View {
    @EnvironmentObject var router: NavigationRouter
    let products = Product.samples

    var body: some View {
        List(products) { product in
            Button {
                // ПОЧЕМУ router.navigate: декларативно, тестируемо
                router.navigate(to: .productDetail(product))
            } label: {
                ProductRow(product: product)
            }
        }
        .navigationTitle("Products")
        .toolbar {
            // ПОЧЕМУ toolbar: автоматическая адаптация под iPhone/iPad
            Button("Profile") {
                router.navigate(to: .userProfile(User.current))
            }
        }
    }
}

struct ProductDetailView: View {
    @EnvironmentObject var router: NavigationRouter
    let product: Product

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                AsyncImage(url: product.imageURL) { image in
                    image.resizable().aspectRatio(contentMode: .fit)
                } placeholder: {
                    ProgressView()
                }

                Text(product.description)
                    .font(.body)

                Button("Show Reviews") {
                    router.navigate(to: .reviews(product))
                }
                .buttonStyle(.borderedProminent)

                Button("Write Review") {
                    // ПОЧЕМУ sheet для создания: модальный контекст
                    router.navigate(to: .createReview(product))
                }
                .buttonStyle(.bordered)
            }
            .padding()
        }
        .navigationTitle(product.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct CreateReviewView: View {
    @Environment(\.dismiss) var dismiss
    let product: Product
    @State private var rating = 5
    @State private var comment = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Rating") {
                    Stepper("Rating: \(rating)", value: $rating, in: 1...5)
                }

                Section("Comment") {
                    TextEditor(text: $comment)
                        .frame(height: 100)
                }
            }
            .navigationTitle("Write Review")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        // ПОЧЕМУ dismiss: закрывает весь modal context
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Submit") {
                        submitReview()
                        dismiss()
                    }
                }
            }
        }
    }

    func submitReview() {
        // Submit logic
        print("Review submitted: \(rating) stars - \(comment)")
    }
}

// ПОЧЕМУ Hashable: NavigationPath требует Hashable типы
struct Product: Identifiable, Hashable {
    let id: UUID
    let name: String
    let description: String
    let imageURL: URL?

    static let samples = [
        Product(id: UUID(), name: "iPhone", description: "Smartphone", imageURL: nil),
        Product(id: UUID(), name: "MacBook", description: "Laptop", imageURL: nil)
    ]
}

struct User: Hashable {
    let id: UUID
    let name: String

    static let current = User(id: UUID(), name: "John Doe")
}
```

---

### Deep Linking с Universal Links

```swift
// UIKit Approach
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    func scene(
        _ scene: UIScene,
        continue userActivity: NSUserActivity
    ) {
        // ПОЧЕМУ NSUserActivity: единая точка для Universal Links и Handoff
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let url = userActivity.webpageURL else { return }

        handleDeepLink(url)
    }

    func handleDeepLink(_ url: URL) {
        // myapp://products/123/reviews
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
              let productID = components.path.split(separator: "/").dropFirst().first,
              let id = UUID(uuidString: String(productID)) else { return }

        let product = Product(id: id, name: "", description: "", imageURL: nil)

        // ПОЧЕМУ setViewControllers: мгновенно строит нужный стек
        guard let navController = window?.rootViewController as? UINavigationController else { return }

        let productVC = ProductDetailViewController(product: product)

        if url.path.contains("reviews") {
            let reviewsVC = ReviewsViewController(product: product)
            navController.setViewControllers([navController.viewControllers[0], productVC, reviewsVC], animated: false)
        } else {
            navController.setViewControllers([navController.viewControllers[0], productVC], animated: false)
        }
    }
}

// SwiftUI Approach
struct AppView: View {
    @StateObject private var router = NavigationRouter()

    var body: some View {
        NavigationStack(path: $router.path) {
            ProductListView()
                .navigationDestination(for: AppRoute.self) { route in
                    // Destination views...
                }
        }
        .environmentObject(router)
        .onOpenURL { url in
            // ПОЧЕМУ onOpenURL: SwiftUI-native способ обработки
            handleDeepLink(url)
        }
    }

    func handleDeepLink(_ url: URL) {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
              let productIDString = components.path.split(separator: "/").dropFirst().first,
              let id = UUID(uuidString: String(productIDString)) else { return }

        let product = Product(id: id, name: "", description: "", imageURL: nil)

        // ПОЧЕМУ очищаем path: начинаем с чистого стека
        router.path = NavigationPath()
        router.path.append(AppRoute.productDetail(product))

        if url.path.contains("reviews") {
            // ПОЧЕМУ последовательное append: строим правильный стек
            router.path.append(AppRoute.reviews(product))
        }
    }
}
```

---

**Итог**: Навигация в iOS — это фундамент UX. UIKit дает императивный контроль, SwiftUI — декларативную простоту. Выбирайте подход под задачу: для простых иерархий SwiftUI идеален, для сложных потоков используйте Coordinator pattern в обоих фреймворках. Всегда помните о State Restoration, Deep Linking и модульности кода.
