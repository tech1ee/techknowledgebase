---
title: "SwiftUI: декларативный UI для iOS"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 67
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
  - topic/swiftui
  - type/deep-dive
  - level/intermediate
related:
  - "[[ios-swiftui-vs-uikit]]"
  - "[[ios-state-management]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-uikit-fundamentals]]"
---

# SwiftUI: Декларативный UI для iOS

## TL;DR

SwiftUI — это декларативный фреймворк от Apple для построения пользовательских интерфейсов на всех платформах экосистемы (iOS, macOS, watchOS, tvOS). Вместо императивного подхода UIKit ("как построить UI") используется декларативный ("что должно быть на экране"). Основан на системе состояний, автоматически обновляющей UI при изменении данных.

**Ключевые особенности:**
- Декларативный синтаксис на Swift
- Реактивная система управления состоянием
- Композиция view через модификаторы
- Live Preview в Xcode
- Кроссплатформенность в экосистеме Apple
- Встроенная поддержка анимаций и accessibility

## Зачем это нужно?

**Статистика внедрения (2026):**
- 78% новых iOS-приложений используют SwiftUI полностью или частично
- 92% iOS-разработчиков считают SwiftUI основным направлением развития
- В 3-4 раза меньше кода по сравнению с UIKit для типовых UI
- На 40% быстрее разработка MVP-приложений

**Причины перехода:**
1. **Производительность разработки** — Live Preview ускоряет итерации
2. **Поддержка Apple** — все новые фичи (Dynamic Island, Live Activities) сначала в SwiftUI
3. **Меньше boilerplate** — нет делегатов, IBOutlet, segue
4. **Естественная композиция** — переиспользование компонентов через @ViewBuilder
5. **Декларативные анимации** — автоматическая интерполяция состояний

---

## 5 жизненных аналогий

### 1. Декларативный UI = Заказ в ресторане
**Императивный подход (UIKit):**
```
Повар, возьми сковороду. Налей масло. Подожди 30 секунд.
Разбей 2 яйца. Жарь 2 минуты. Переверни. Жарь еще минуту. Посоли.
```

**Декларативный подход (SwiftUI):**
```
Мне яичницу из двух яиц, средней прожарки, с солью.
```

Вы описываете **результат**, а не **процесс**. SwiftUI сам решает, как обновить UI.

### 2. State = Термостат в доме
Когда температура (state) меняется, термостат автоматически включает/выключает обогрев (UI update). Вы не говорите батареям "нагрейтесь до 23°", вы просто устанавливаете желаемую температуру.

```swift
@State private var temperature = 20 // ПОЧЕМУ @State: SwiftUI следит за изменениями

Text("Температура: \(temperature)°C") // ПОЧЕМУ автообновление: при изменении temperature SwiftUI перерисует Text
```

### 3. View Modifiers = Слои бургера
Каждый модификатор добавляет новый слой поверх view, возвращая новую view. Порядок имеет значение!

```
Text("Hello")           // Булочка
    .padding()          // Салат
    .background(.blue)  // Котлета
    .cornerRadius(8)    // Сыр
```

Меняешь порядок — получишь другой результат (как если положить котлету поверх булочки).

### 4. @Binding = Пульт дистанционного управления
У вас дома один телевизор (source of truth), но несколько пультов (bindings). Любой пульт может изменить канал, и все видят результат.

```swift
struct ParentView: View {
    @State private var volume = 50 // ПОЧЕМУ @State: источник истины

    var body: some View {
        VolumeControl(volume: $volume) // ПОЧЕМУ $: передаём binding (двустороннюю связь)
    }
}

struct VolumeControl: View {
    @Binding var volume: Int // ПОЧЕМУ @Binding: пульт управления
}
```

### 5. ViewBuilder = Конструктор LEGO
`@ViewBuilder` позволяет складывать view как детали LEGO, используя естественный синтаксис Swift (if/else, for). Компилятор собирает их в единую структуру.

```swift
@ViewBuilder
var content: some View {
    if isLoggedIn {
        HomeView()      // ПОЧЕМУ нет return: @ViewBuilder создаёт implicit returns
    } else {
        LoginView()
    }
}
```

---

## ASCII Диаграммы

### View Hierarchy (Иерархия представлений)

```
                    ContentView (root)
                          |
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    VStack            Image             HStack
        |                               ┌──┴──┐
    ┌───┼───┐                          ▼     ▼
    ▼   ▼   ▼                       Button  Text
  Text Text Text

ПОЧЕМУ дерево: каждая view может содержать другие views
ПОЧЕМУ struct: lightweight, value types, быстрое копирование
```

### Data Flow (Поток данных)

```
┌─────────────────────────────────────────────────────────┐
│  ParentView                                             │
│  ┌──────────────────────────────────────┐              │
│  │ @StateObject var store = AppStore()  │ ← Source of Truth
│  └──────────────────────────────────────┘              │
│                     │                                   │
│         ┌───────────┼───────────┐                      │
│         ▼                       ▼                       │
│  ┌─────────────┐         ┌─────────────┐              │
│  │ ChildView A │         │ ChildView B │              │
│  │ @ObservedO. │         │ @ObservedO. │              │
│  └─────────────┘         └─────────────┘              │
│         │                       │                       │
│         └───────────┬───────────┘                      │
│                     ▼                                   │
│              ┌──────────────┐                          │
│              │ GrandChild   │                          │
│              │ @Environment │                          │
│              └──────────────┘                          │
└─────────────────────────────────────────────────────────┘

Направление потока данных:
  ──► @ObservedObject: наблюдает за изменениями
  ──► @Environment: получает из окружения
  ◄── @Binding: двусторонняя связь
```

### State Management Pattern (Паттерн управления состоянием)

```
┌──────────────────────────────────────────────────────┐
│  View Layer                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐               │
│  │ View A │  │ View B │  │ View C │               │
│  └───┬────┘  └───┬────┘  └───┬────┘               │
│      │           │           │                      │
│      └───────────┼───────────┘                      │
│                  │ @ObservedObject / @StateObject    │
├──────────────────┼──────────────────────────────────┤
│  State Layer     ▼                                   │
│  ┌──────────────────────────────┐                  │
│  │ ObservableObject (ViewModel) │                  │
│  │  @Published var items        │                  │
│  └────────┬─────────────────────┘                  │
│           │ objectWillChange.send()                 │
├───────────┼──────────────────────────────────────────┤
│  Data     ▼                                          │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  Repository  │  │  API Client  │               │
│  └──────────────┘  └──────────────┘               │
└──────────────────────────────────────────────────────┘

ПОЧЕМУ разделение: Separation of Concerns
ПОЧЕМУ @Published: автоматическая нотификация об изменениях
```

### View Lifecycle & Redraw (Жизненный цикл)

```
┌─────────────────────────────────────────────────┐
│ 1. State Changes                                │
│    @State var count = 0                         │
│           │                                     │
│           ▼                                     │
│ 2. SwiftUI marks view as "needs update"        │
│           │                                     │
│           ▼                                     │
│ 3. body computed (struct creation)             │
│    var body: some View { ... }                 │
│           │                                     │
│           ▼                                     │
│ 4. Diffing algorithm                           │
│    Old View Tree ←→ New View Tree              │
│           │                                     │
│           ▼                                     │
│ 5. Minimal UI updates                          │
│    (only changed elements)                     │
└─────────────────────────────────────────────────┘

ПОЧЕМУ struct: быстрое создание и сравнение
ПОЧЕМУ diffing: эффективность (не перерисовывает всё)
```

### Layout System (Система раскладки)

```
HStack(spacing: 10) {
    ┌──────────┬───┬──────────┬───┬──────────┐
    │  View 1  │ S │  View 2  │ S │  View 3  │
    │  fixed   │ p │ flexible │ p │  fixed   │
    │  width   │ a │  (fills) │ a │  width   │
    └──────────┴─c─┴──────────┴─c─┴──────────┘
}                 i             i
                  n             n
                  g             g

Layout Process:
1. Родитель предлагает размер детям
2. Дети выбирают свой размер (в пределах предложенного)
3. Родитель размещает детей согласно alignment
4. Родитель выбирает свой размер на основе детей

ПОЧЕМУ снизу вверх: гибкость и предсказуемость
ПОЧЕМУ spacing отдельно: не входит в размер view
```

---

## Основные концепции

### 1. Декларативный vs Императивный подход

**Императивный (UIKit):**
```swift
// ПОЧЕМУ сложно: нужно управлять состоянием вручную
class ViewController: UIViewController {
    let label = UILabel()
    var count = 0

    override func viewDidLoad() {
        super.viewDidLoad()

        // Описываем КАК создать UI
        label.text = "Count: 0"
        label.frame = CGRect(x: 100, y: 100, width: 200, height: 40)
        view.addSubview(label)

        let button = UIButton(frame: CGRect(x: 100, y: 150, width: 200, height: 40))
        button.setTitle("Increment", for: .normal)
        button.addTarget(self, action: #selector(increment), for: .touchUpInside)
        view.addSubview(button)
    }

    @objc func increment() {
        count += 1
        // ПОЧЕМУ проблема: синхронизация state и UI вручную
        label.text = "Count: \(count)"
    }
}
```

**Декларативный (SwiftUI):**
```swift
struct ContentView: View {
    // ПОЧЕМУ @State: SwiftUI автоматически следит за изменениями
    @State private var count = 0

    var body: some View {
        // Описываем ЧТО должно быть на экране
        VStack(spacing: 20) {
            Text("Count: \(count)") // ПОЧЕМУ автообновление: при изменении count SwiftUI пересоздаст view

            Button("Increment") {
                count += 1 // ПОЧЕМУ достаточно: изменение state → автоматическое обновление UI
            }
        }
    }
}
```

**Ключевые различия:**

| Аспект | UIKit (Императивный) | SwiftUI (Декларативный) |
|--------|---------------------|------------------------|
| Подход | Как построить UI | Что должно быть на экране |
| Синхронизация | Вручную | Автоматически |
| Состояние | Scattered (разбросано) | Centralized (централизовано) |
| Код | Больше boilerplate | Меньше кода |
| Анимации | Явные команды | Изменение состояния |

### 2. View Protocol и body property

```swift
// ПОЧЕМУ protocol: контракт для всех SwiftUI views
public protocol View {
    // ПОЧЕМУ associatedtype: каждая view возвращает свой тип
    associatedtype Body: View

    // ПОЧЕМУ @ViewBuilder: позволяет использовать if/else, for
    @ViewBuilder var body: Self.Body { get }
}

struct MyView: View {
    // ПОЧЕМУ some View: opaque type, компилятор знает точный тип
    var body: some View {
        VStack {
            Text("Hello")
            Text("World")
        }
        // ПОЧЕМУ возвращает ModifiedContent<VStack<TupleView<...>>>:
        // каждый модификатор оборачивает view в новый тип
    }
}
```

**Почему struct, а не class:**
```swift
// ❌ Не используйте class для View
class BadView: View { // ПОЧЕМУ плохо:
    var body: some View { // 1. Тяжелее (heap allocation)
        Text("Bad")       // 2. Сложнее оптимизировать
    }                     // 3. Reference semantics (побочные эффекты)
}

// ✅ Используйте struct
struct GoodView: View { // ПОЧЕМУ хорошо:
    var body: some View { // 1. Value type (stack allocation)
        Text("Good")      // 2. Неизменяемость (immutability)
    }                     // 3. Лёгкое копирование и сравнение
}
```

**Body вычисляется каждый раз:**
```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        // ПОЧЕМУ body вызывается часто: при каждом изменении @State
        print("Body computed") // Увидите это при каждом нажатии

        return VStack {
            Text("Count: \(count)")
            Button("Increment") { count += 1 }
        }
    }
}

// ПОЧЕМУ это нормально: body — это описание, а не выполнение
// SwiftUI использует diffing для минимизации реальных изменений UI
```

### 3. State Management (Управление состоянием)

#### @State — Локальное состояние view

```swift
struct ToggleView: View {
    // ПОЧЕМУ @State: view не может изменять свои свойства напрямую (struct immutable)
    // ПОЧЕМУ private: состояние принадлежит только этой view
    @State private var isOn = false

    var body: some View {
        Toggle("Switch", isOn: $isOn) // ПОЧЕМУ $: передаём binding (read-write доступ)

        // ПОЧЕМУ работает: @State создаёт хранилище вне struct,
        // изменение которого триггерит перерисовку
    }
}
```

**Как работает @State:**
```
┌──────────────────────────────────────┐
│ ToggleView (struct, immutable)       │
│                                      │
│  @State private var isOn = false     │
│         │                            │
│         └─────┐                      │
└───────────────┼──────────────────────┘
                ▼
        ┌───────────────┐
        │ State Storage │  ← В памяти SwiftUI
        │  isOn: false  │  ← Mutable
        └───────────────┘

ПОЧЕМУ отдельное хранилище: struct неизменяемые,
но состояние должно меняться
```

#### @Binding — Двусторонняя связь

```swift
struct ParentView: View {
    @State private var username = ""

    var body: some View {
        VStack {
            // ПОЧЕМУ $username: создаём Binding<String> из @State
            TextField("Enter name", text: $username)

            ChildView(name: $username) // Передаём binding вниз
        }
    }
}

struct ChildView: View {
    // ПОЧЕМУ @Binding: не владеет данными, только читает/изменяет
    @Binding var name: String

    var body: some View {
        Text("Hello, \(name)!")

        Button("Clear") {
            name = "" // ПОЧЕМУ работает: изменение через binding обновляет source
        }
    }
}

// Поток данных:
// ParentView.username (source) ←→ ChildView.name (binding)
```

#### @StateObject — Владение reference type

```swift
class UserStore: ObservableObject {
    // ПОЧЕМУ @Published: автоматически отправляет уведомления об изменениях
    @Published var users: [User] = []

    func loadUsers() {
        // API call...
        // ПОЧЕМУ objectWillChange.send() вызывается автоматически:
        // @Published делает это перед изменением
        users = fetchedUsers
    }
}

struct UserListView: View {
    // ПОЧЕМУ @StateObject: создаёт и владеет экземпляром
    // ПОЧЕМУ не @State: @State для value types, @StateObject для reference types
    @StateObject private var store = UserStore()

    var body: some View {
        List(store.users) { user in
            Text(user.name)
        }
        .onAppear {
            store.loadUsers()
        }
    }

    // ПОЧЕМУ важно: @StateObject сохраняет экземпляр между перерисовками
    // @ObservedObject создавал бы новый при каждой перерисовке родителя!
}
```

#### @ObservedObject — Наблюдение за reference type

```swift
struct ParentView: View {
    @StateObject private var store = UserStore() // Владелец

    var body: some View {
        ChildView(store: store) // Передаём reference
    }
}

struct ChildView: View {
    // ПОЧЕМУ @ObservedObject: не владеет, только наблюдает
    // ПОЧЕМУ не @StateObject: родитель уже владеет
    @ObservedObject var store: UserStore

    var body: some View {
        List(store.users) { user in
            Text(user.name)
        }
    }
}

// Правило: используй @StateObject там, где создаёшь объект
//          используй @ObservedObject там, где получаешь из вне
```

#### @EnvironmentObject — Dependency Injection

```swift
class ThemeManager: ObservableObject {
    @Published var isDarkMode = false
}

@main
struct MyApp: App {
    @StateObject private var theme = ThemeManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                // ПОЧЕМУ environmentObject: доступен всем дочерним views
                .environmentObject(theme)
        }
    }
}

struct DeepNestedView: View {
    // ПОЧЕМУ @EnvironmentObject: получаем из environment без передачи через всю цепочку
    @EnvironmentObject var theme: ThemeManager

    var body: some View {
        Text("Theme")
            .foregroundStyle(theme.isDarkMode ? .white : .black)
    }
}

// ПОЧЕМУ удобно: избегаем prop drilling (передачи через 10 уровней)
// ПОЧЕМУ осторожно: crash если не передан в .environmentObject()
```

#### @Environment — Системные значения

```swift
struct MyView: View {
    // ПОЧЕМУ @Environment: доступ к системным настройкам
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss
    @Environment(\.horizontalSizeClass) var sizeClass

    var body: some View {
        VStack {
            Text("Current scheme: \(colorScheme == .dark ? "Dark" : "Light")")

            Button("Close") {
                dismiss() // ПОЧЕМУ работает: dismiss закрывает текущий экран
            }

            if sizeClass == .compact {
                CompactLayout()
            } else {
                RegularLayout()
            }
        }
    }
}

// Собственные environment values:
private struct UserIDKey: EnvironmentKey {
    static let defaultValue: String = "guest"
}

extension EnvironmentValues {
    var userID: String {
        get { self[UserIDKey.self] }
        set { self[UserIDKey.self] = newValue }
    }
}

struct ParentView: View {
    var body: some View {
        ChildView()
            .environment(\.userID, "12345") // ПОЧЕМУ удобно: передача контекста
    }
}
```

**Сравнение Property Wrappers:**

| Wrapper | Владение | Тип данных | Использование |
|---------|----------|-----------|---------------|
| @State | Да | Value type | Локальное состояние |
| @Binding | Нет | Любой | Двусторонняя связь |
| @StateObject | Да | Reference type | Создание ObservableObject |
| @ObservedObject | Нет | Reference type | Наблюдение за переданным объектом |
| @EnvironmentObject | Нет | Reference type | DI через окружение |
| @Environment | Нет | Любой | Системные/кастомные значения |

### 4. View Modifiers и Композиция

```swift
// ПОЧЕМУ модификаторы возвращают новую view:
Text("Hello")
    .font(.title)           // → ModifiedContent<Text, FontModifier>
    .foregroundStyle(.blue) // → ModifiedContent<ModifiedContent<...>, ColorModifier>
    .padding()              // → ModifiedContent<ModifiedContent<ModifiedContent<...>, PaddingModifier>

// Каждый модификатор оборачивает предыдущую view
```

**Порядок модификаторов имеет значение:**

```swift
// ❌ Неправильный порядок
Text("Hello")
    .background(.blue)  // Фон только под текстом
    .padding()          // Padding снаружи фона
// Результат: текст с синим фоном, padding вокруг фона

// ✅ Правильный порядок
Text("Hello")
    .padding()          // Сначала добавляем пространство
    .background(.blue)  // Потом фон покрывает всё
// Результат: текст с padding внутри синего фона
```

**Визуально:**
```
background → padding:          padding → background:
┌───────────────┐             ┌─────────────────────┐
│  ░░░░░░░░░░░  │             │         BLUE        │
│  ░ Hello ░    │             │                     │
│  ░░░░░░░░░░░  │             │      Hello          │
└───────────────┘             │                     │
                              └─────────────────────┘
```

**Переиспользуемые модификаторы:**

```swift
// ПОЧЕМУ ViewModifier protocol: создание переиспользуемых стилей
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.white)
            .cornerRadius(12)
            .shadow(radius: 5)
    }
}

extension View {
    // ПОЧЕМУ extension: удобный синтаксис применения
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// Использование:
Text("Card content")
    .cardStyle() // ПОЧЕМУ чисто: переиспользуемый стиль
```

**Условные модификаторы:**

```swift
extension View {
    // ПОЧЕМУ @ViewBuilder не нужен: возвращаем один тип
    func `if`<Transform: View>(
        _ condition: Bool,
        transform: (Self) -> Transform
    ) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

// Использование:
Text("Hello")
    .if(isHighlighted) { view in
        view.foregroundStyle(.red) // ПОЧЕМУ работает: применяется только если true
    }
```

### 5. Layout System (Система раскладки)

#### VStack, HStack, ZStack

```swift
// VStack — вертикальная раскладка
VStack(alignment: .leading, spacing: 16) {
    Text("Title")
        .font(.headline)
    Text("Subtitle")
        .font(.subheadline)
    Text("Body text")
}
// ПОЧЕМУ spacing: расстояние между элементами
// ПОЧЕМУ alignment: выравнивание по горизонтали (.leading, .center, .trailing)

// HStack — горизонтальная раскладка
HStack(alignment: .center, spacing: 12) {
    Image(systemName: "star.fill")
    Text("Featured")
    Spacer() // ПОЧЕМУ Spacer: занимает всё доступное пространство
    Text("New")
}
// ПОЧЕМУ alignment: выравнивание по вертикали (.top, .center, .bottom)

// ZStack — слои (z-axis)
ZStack(alignment: .topLeading) {
    Rectangle()
        .fill(.blue)
        .frame(width: 100, height: 100)

    Text("Badge")
        .padding(4)
        .background(.red)
        .cornerRadius(4)
}
// ПОЧЕМУ ZStack: элементы накладываются друг на друга
// ПОЧЕМУ alignment: положение дочерних элементов относительно друг друга
```

**Layout Priority:**

```swift
HStack {
    Text("Short")
        .layoutPriority(1) // ПОЧЕМУ priority: получает пространство первым

    Text("This is a very long text that should truncate")
        .lineLimit(1)
        .layoutPriority(0) // ПОЧЕМУ 0: получает пространство после priority 1
}
// Результат: "Short" всегда полностью виден, длинный текст обрезается
```

#### LazyVStack и LazyHStack

```swift
// ❌ VStack — загружает все элементы сразу
ScrollView {
    VStack {
        ForEach(0..<1000) { i in
            HeavyView(index: i) // ПОЧЕМУ плохо: создаёт 1000 views сразу
        }
    }
}

// ✅ LazyVStack — загружает только видимые
ScrollView {
    LazyVStack {
        ForEach(0..<1000) { i in
            HeavyView(index: i) // ПОЧЕМУ хорошо: создаёт только видимые views
        }
    }
}
// ПОЧЕМУ "Lazy": views создаются on-demand, когда появляются на экране
```

**Pinned Headers:**

```swift
ScrollView {
    LazyVStack(pinnedViews: [.sectionHeaders]) {
        Section {
            ForEach(items) { item in
                ItemRow(item: item)
            }
        } header: {
            Text("Section Title")
                .font(.headline)
                .padding()
                .frame(maxWidth: .infinity)
                .background(.gray.opacity(0.2))
        }
    }
}
// ПОЧЕМУ pinnedViews: заголовок прикрепляется к верху при скролле
```

### 6. List и ForEach

```swift
struct Item: Identifiable {
    let id = UUID() // ПОЧЕМУ Identifiable: SwiftUI нужен уникальный ID
    let name: String
}

struct ListView: View {
    let items = [
        Item(name: "Apple"),
        Item(name: "Banana"),
        Item(name: "Cherry")
    ]

    var body: some View {
        List(items) { item in
            Text(item.name)
        }
        // ПОЧЕМУ List знает об обновлениях: использует Identifiable.id
    }
}
```

**List vs ForEach:**

```swift
// List — оптимизированный контейнер для списков
List {
    Text("Header")
        .font(.headline)

    ForEach(items) { item in
        Text(item.name)
    }

    Text("Footer")
}
// ПОЧЕМУ List снаружи: добавляет стандартный стиль, разделители, поведение

// ForEach — только итерация
VStack {
    ForEach(items) { item in
        Text(item.name)
    }
}
// ПОЧЕМУ ForEach отдельно: можно использовать в любом контейнере
```

**Редактирование списка:**

```swift
struct EditableList: View {
    @State private var items = ["A", "B", "C"]

    var body: some View {
        List {
            ForEach(items, id: \.self) { item in
                Text(item)
            }
            .onDelete { indexSet in
                items.remove(atOffsets: indexSet)
                // ПОЧЕМУ IndexSet: может быть несколько выбранных элементов
            }
            .onMove { source, destination in
                items.move(fromOffsets: source, toOffset: destination)
            }
        }
        .toolbar {
            EditButton() // ПОЧЕМУ EditButton: переключает режим редактирования
        }
    }
}
```

**Секции в List:**

```swift
List {
    Section("Fruits") {
        ForEach(fruits) { fruit in
            Text(fruit.name)
        }
    }

    Section {
        ForEach(vegetables) { veg in
            Text(veg.name)
        }
    } header: {
        Text("Vegetables")
    } footer: {
        Text("\(vegetables.count) items")
    }
}
// ПОЧЕМУ Section: логическая группировка с header/footer
```

### 7. Navigation

#### NavigationStack (iOS 16+)

```swift
struct NavigationExample: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(1..<10) { i in
                NavigationLink("Item \(i)", value: i)
                    // ПОЧЕМУ value: типобезопасная навигация
            }
            .navigationDestination(for: Int.self) { value in
                DetailView(number: value)
                    // ПОЧЕМУ for: связывает тип с destination
            }
            .navigationTitle("Numbers")
            .toolbar {
                Button("Jump to 5") {
                    path.append(5) // ПОЧЕМУ programmatic: навигация из кода
                }
            }
        }
    }
}

// ПОЧЕМУ NavigationPath: type-erased контейнер для разных типов
```

**Программная навигация:**

```swift
struct ProgrammaticNav: View {
    @State private var path: [String] = []

    var body: some View {
        NavigationStack(path: $path) {
            VStack {
                Button("Go to A → B → C") {
                    path = ["A", "B", "C"]
                    // ПОЧЕМУ массив: весь путь навигации
                }

                Button("Go back to root") {
                    path = []
                    // ПОЧЕМУ пустой массив: возврат в корень
                }
            }
            .navigationDestination(for: String.self) { value in
                Text("Screen: \(value)")
            }
        }
    }
}
```

**Deep Linking:**

```swift
struct DeepLinkApp: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            ContentView()
                .navigationDestination(for: Product.self) { product in
                    ProductView(product: product)
                }
        }
        .onOpenURL { url in
            // myapp://product/123
            if let productID = url.pathComponents.last,
               let product = loadProduct(id: productID) {
                path.append(product)
                // ПОЧЕМУ работает: программная навигация через path
            }
        }
    }
}
```

#### Sheet, FullScreenCover, Alert

```swift
struct PresentationExample: View {
    @State private var showSheet = false
    @State private var showFullScreen = false
    @State private var showAlert = false

    var body: some View {
        VStack(spacing: 20) {
            Button("Show Sheet") { showSheet = true }
            Button("Show Full Screen") { showFullScreen = true }
            Button("Show Alert") { showAlert = true }
        }
        .sheet(isPresented: $showSheet) {
            SheetView()
            // ПОЧЕМУ sheet: модальное окно с dismiss gesture
        }
        .fullScreenCover(isPresented: $showFullScreen) {
            FullScreenView()
            // ПОЧЕМУ fullScreenCover: полноэкранная модалка
        }
        .alert("Warning", isPresented: $showAlert) {
            Button("OK", role: .cancel) { }
            Button("Delete", role: .destructive) { }
            // ПОЧЕМУ role: определяет стиль кнопки
        } message: {
            Text("Are you sure?")
        }
    }
}
```

**Item-based presentation:**

```swift
struct ItemPresentation: View {
    @State private var selectedUser: User?

    var body: some View {
        List(users) { user in
            Button(user.name) {
                selectedUser = user
                // ПОЧЕМУ nil → User: триггерит презентацию
            }
        }
        .sheet(item: $selectedUser) { user in
            UserDetailView(user: user)
            // ПОЧЕМУ item: автоматически закрывается при nil
        }
    }
}
```

### 8. Animations (Анимации)

#### Implicit (неявные) анимации

```swift
struct ImplicitAnimation: View {
    @State private var scale: CGFloat = 1.0

    var body: some View {
        Circle()
            .frame(width: 100 * scale, height: 100 * scale)
            .animation(.spring(duration: 0.5), value: scale)
            // ПОЧЕМУ .animation: анимирует изменения этого свойства
            // ПОЧЕМУ value: только когда scale меняется
            .onTapGesture {
                scale = scale == 1.0 ? 1.5 : 1.0
            }
    }
}
```

#### Explicit (явные) анимации

```swift
struct ExplicitAnimation: View {
    @State private var offset: CGFloat = 0

    var body: some View {
        Circle()
            .offset(x: offset)
            .onTapGesture {
                withAnimation(.easeInOut(duration: 1.0)) {
                    offset = offset == 0 ? 100 : 0
                    // ПОЧЕМУ withAnimation: анимирует все изменения в блоке
                }
            }
    }
}
```

**Разница implicit vs explicit:**

```swift
@State private var isExpanded = false

// Implicit — анимирует только конкретное свойство
Rectangle()
    .frame(width: isExpanded ? 200 : 100)
    .animation(.spring(), value: isExpanded)
    // Анимируется только frame

// Explicit — анимирует все изменения состояния
Button("Toggle") {
    withAnimation(.spring()) {
        isExpanded.toggle()
    }
}
// Анимируются ВСЕ view, зависящие от isExpanded
```

**Custom Animations:**

```swift
struct CustomAnimation: View {
    @State private var rotation: Double = 0

    var body: some View {
        Image(systemName: "arrow.right")
            .rotationEffect(.degrees(rotation))
            .onAppear {
                withAnimation(
                    .linear(duration: 2.0)
                    .repeatForever(autoreverses: false)
                ) {
                    rotation = 360
                    // ПОЧЕМУ repeatForever: бесконечная анимация
                }
            }
    }
}
```

**Transitions (переходы):**

```swift
struct TransitionExample: View {
    @State private var show = false

    var body: some View {
        VStack {
            Button("Toggle") {
                withAnimation(.spring()) {
                    show.toggle()
                }
            }

            if show {
                Text("Hello!")
                    .transition(.scale.combined(with: .opacity))
                    // ПОЧЕМУ transition: определяет появление/исчезновение
                    // ПОЧЕМУ combined: композиция нескольких переходов
            }
        }
    }
}
```

**Custom Transition:**

```swift
extension AnyTransition {
    static var moveAndFade: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .trailing).combined(with: .opacity),
            removal: .move(edge: .leading).combined(with: .opacity)
        )
        // ПОЧЕМУ asymmetric: разные анимации для появления и исчезновения
    }
}
```

### 9. ViewBuilder и Result Builders

```swift
// ПОЧЕМУ @ViewBuilder: позволяет использовать declarative синтаксис
@ViewBuilder
func conditionalContent(isLoggedIn: Bool) -> some View {
    if isLoggedIn {
        Text("Welcome back!")
        Button("Logout") { }
    } else {
        Text("Please login")
        Button("Login") { }
    }
    // ПОЧЕМУ нет return: @ViewBuilder создаёт implicit returns
    // ПОЧЕМУ работает if/else: result builder трансформирует код
}
```

**Как работает @ViewBuilder:**

```swift
// Что вы пишете:
VStack {
    Text("A")
    Text("B")
    Text("C")
}

// Что компилятор создаёт:
VStack {
    ViewBuilder.buildBlock(
        Text("A"),
        Text("B"),
        Text("C")
    )
}
// ПОЧЕМУ buildBlock: result builder method для композиции views
```

**Условная логика:**

```swift
@ViewBuilder
var content: some View {
    Text("Always visible")

    if condition {
        Text("Conditional") // ПОЧЕМУ работает: buildIf
    }

    if let user = currentUser {
        Text("Hello, \(user.name)") // ПОЧЕМУ работает: buildOptional
    }

    switch mode {
    case .compact:
        CompactView() // ПОЧЕМУ работает: buildEither
    case .regular:
        RegularView()
    }
}
```

**Собственный Result Builder:**

```swift
@resultBuilder
struct StringBuilder {
    static func buildBlock(_ components: String...) -> String {
        components.joined(separator: "\n")
    }

    static func buildOptional(_ component: String?) -> String {
        component ?? ""
    }

    static func buildEither(first component: String) -> String {
        component
    }

    static func buildEither(second component: String) -> String {
        component
    }
}

@StringBuilder
func buildMessage(includeGreeting: Bool) -> String {
    if includeGreeting {
        "Hello!"
    }
    "This is a message"
    "Goodbye!"
}

print(buildMessage(includeGreeting: true))
// Hello!
// This is a message
// Goodbye!
```

---

## Сравнение с Jetpack Compose (Android)

| Аспект | SwiftUI | Jetpack Compose |
|--------|---------|-----------------|
| **Язык** | Swift | Kotlin |
| **Декларативность** | `var body: some View` | `@Composable fun Content()` |
| **State** | `@State`, `@Binding` | `remember`, `mutableStateOf` |
| **ViewModel** | `@StateObject`, `@ObservedObject` | `viewModel()`, `collectAsState()` |
| **Layouts** | `VStack`, `HStack`, `ZStack` | `Column`, `Row`, `Box` |
| **Lists** | `List`, `LazyVStack` | `LazyColumn`, `LazyRow` |
| **Модификаторы** | `.padding()`, `.background()` | `.padding()`, `.background()` |
| **Navigation** | `NavigationStack` | `NavController`, `NavHost` |
| **Анимации** | `withAnimation`, `.animation()` | `animate*AsState`, `AnimatedVisibility` |
| **DI** | `@EnvironmentObject` | `CompositionLocal` |
| **Preview** | `#Preview { ... }` | `@Preview @Composable` |

**Примеры кода:**

```swift
// SwiftUI
struct Counter: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") {
                count += 1
            }
        }
    }
}
```

```kotlin
// Jetpack Compose
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Ключевые сходства:**
- Декларативный подход к UI
- Реактивное обновление при изменении state
- Композиция через модификаторы
- Type-safe навигация

**Ключевые различия:**
- SwiftUI использует property wrappers (`@State`), Compose — делегаты (`by remember`)
- SwiftUI — protocol-oriented (`View`), Compose — function-based (`@Composable`)
- SwiftUI — `ObservableObject`, Compose — `StateFlow`/`LiveData`
- SwiftUI компилирует в native UIKit/AppKit, Compose — в Android Views

---

## 6 типичных ошибок

### ❌ Ошибка 1: @ObservedObject вместо @StateObject

```swift
// ❌ НЕПРАВИЛЬНО
struct ParentView: View {
    var body: some View {
        ChildView()
    }
}

struct ChildView: View {
    @ObservedObject var viewModel = ViewModel()
    // ПОЧЕМУ плохо: создаёт новый экземпляр при каждой перерисовке родителя!

    var body: some View {
        Text(viewModel.data)
    }
}

// ✅ ПРАВИЛЬНО
struct ChildView: View {
    @StateObject private var viewModel = ViewModel()
    // ПОЧЕМУ хорошо: создаёт один раз и сохраняет между перерисовками

    var body: some View {
        Text(viewModel.data)
    }
}
```

**Последствия:** Потеря состояния, лишние инициализации, утечки памяти.

### ❌ Ошибка 2: Тяжёлые вычисления в body

```swift
// ❌ НЕПРАВИЛЬНО
struct SlowView: View {
    @State private var items: [Item] = []

    var body: some View {
        let sortedItems = items.sorted { $0.price < $1.price }
        // ПОЧЕМУ плохо: сортировка при КАЖДОЙ перерисовке!

        List(sortedItems) { item in
            Text(item.name)
        }
    }
}

// ✅ ПРАВИЛЬНО (вариант 1: computed property)
struct FastView: View {
    @State private var items: [Item] = []

    private var sortedItems: [Item] {
        items.sorted { $0.price < $1.price }
        // ПОЧЕМУ лучше: всё равно вызывается каждый раз, но явно
    }

    var body: some View {
        List(sortedItems) { item in
            Text(item.name)
        }
    }
}

// ✅ ПРАВИЛЬНО (вариант 2: кеширование)
struct OptimalView: View {
    @State private var items: [Item] = []
    @State private var sortedCache: [Item] = []

    var body: some View {
        List(sortedCache) { item in
            Text(item.name)
        }
        .onChange(of: items) { oldValue, newValue in
            sortedCache = newValue.sorted { $0.price < $1.price }
            // ПОЧЕМУ оптимально: сортировка только при изменении items
        }
    }
}
```

### ❌ Ошибка 3: Неправильный порядок модификаторов

```swift
// ❌ НЕПРАВИЛЬНО
Text("Tap me")
    .background(.blue)
    .padding()
    .onTapGesture {
        print("Tapped")
    }
// ПОЧЕМУ плохо: onTapGesture срабатывает только на padding области,
// не на синем фоне!

// ✅ ПРАВИЛЬНО
Text("Tap me")
    .padding()
    .background(.blue)
    .onTapGesture {
        print("Tapped")
    }
// ПОЧЕМУ хорошо: onTapGesture на всей синей области
```

**Визуализация:**
```
❌ background → padding → tap:
┌─────────────────┐
│  ┌───────────┐  │ ← tap area (только серая зона)
│  │   BLUE    │  │
│  └───────────┘  │
└─────────────────┘

✅ padding → background → tap:
┌─────────────────┐
│      BLUE       │ ← tap area (весь синий фон)
└─────────────────┘
```

### ❌ Ошибка 4: Прямое изменение @Binding в init

```swift
// ❌ НЕПРАВИЛЬНО
struct ChildView: View {
    @Binding var count: Int

    init(count: Binding<Int>) {
        _count = count
        count.wrappedValue = 0 // ПОЧЕМУ плохо: изменение в init!
    }

    var body: some View {
        Text("\(count)")
    }
}

// ✅ ПРАВИЛЬНО
struct ChildView: View {
    @Binding var count: Int

    var body: some View {
        Text("\(count)")
            .onAppear {
                count = 0 // ПОЧЕМУ хорошо: изменение в lifecycle методе
            }
    }
}
```

### ❌ Ошибка 5: Забытый id в ForEach

```swift
// ❌ НЕПРАВИЛЬНО
struct ListView: View {
    @State private var items = ["A", "B", "C"]

    var body: some View {
        List {
            ForEach(items) { item in // ПОЧЕМУ не компилируется: String не Identifiable
                Text(item)
            }
        }
    }
}

// ✅ ПРАВИЛЬНО (вариант 1: id по self)
List {
    ForEach(items, id: \.self) { item in
        Text(item)
    }
}
// ПОЧЕМУ работает: использует сам String как ID
// ПОЧЕМУ осторожно: дубликаты вызовут проблемы!

// ✅ ПРАВИЛЬНО (вариант 2: Identifiable модель)
struct Item: Identifiable {
    let id = UUID()
    let name: String
}

List {
    ForEach(items) { item in
        Text(item.name)
    }
}
// ПОЧЕМУ лучше: уникальный ID, безопасно для дубликатов
```

### ❌ Ошибка 6: Использование GeometryReader без необходимости

```swift
// ❌ НЕПРАВИЛЬНО
struct BadLayout: View {
    var body: some View {
        GeometryReader { geometry in
            VStack {
                Text("Title")
                Text("Subtitle")
            }
            .frame(width: geometry.size.width)
            // ПОЧЕМУ плохо: GeometryReader занимает ВСЁ доступное пространство,
            // растягивает VStack
        }
    }
}

// ✅ ПРАВИЛЬНО
struct GoodLayout: View {
    var body: some View {
        VStack {
            Text("Title")
            Text("Subtitle")
        }
        .frame(maxWidth: .infinity)
        // ПОЧЕМУ хорошо: VStack занимает только нужное пространство по вертикали
    }
}

// ✅ GeometryReader когда нужен
struct ValidUseCase: View {
    var body: some View {
        GeometryReader { geometry in
            Circle()
                .frame(
                    width: geometry.size.width * 0.5,
                    height: geometry.size.width * 0.5
                )
                // ПОЧЕМУ оправдано: нужен адаптивный размер на основе родителя
        }
    }
}
```

---

## 5 ментальных моделей

### 1. View как функция состояния: UI = f(State)

```
State → View → Rendered UI

При изменении State, SwiftUI:
1. Вызывает body (создаёт новое дерево View)
2. Сравнивает со старым деревом (diffing)
3. Обновляет только изменённые элементы в UI

Вы не управляете обновлениями — описываете результат.
```

### 2. Data Flow как система водопровода

```
┌──────────────┐
│ @State       │  Источник (кран)
└──────┬───────┘
       │ $binding (труба с клапаном)
       ▼
┌──────────────┐
│ @Binding     │  Потребитель (душ)
└──────────────┘

- @State — владеет водой (данными)
- $binding — труба с двусторонним потоком
- Изменение в любом месте обновляет всю систему
```

### 3. Модификаторы как матрёшки

```
Text("Core")
  .font(.title)           ← Слой 1
  .foregroundStyle(.red)  ← Слой 2
  .padding()              ← Слой 3
  .background(.blue)      ← Слой 4

Каждый слой оборачивает предыдущий.
Порядок = структура вложенности.
```

### 4. ObservableObject как радиовещание

```
┌────────────────────────┐
│ ObservableObject       │  Радиостанция
│ @Published var data    │
└──────────┬─────────────┘
           │ objectWillChange (сигнал)
     ┌─────┼─────┬─────┐
     ▼     ▼     ▼     ▼
   View1 View2 View3 View4  Радиоприёмники

Когда @Published меняется → все подписчики получают уведомление.
```

### 5. SwiftUI как автомобиль с автоматической коробкой передач

**UIKit = механическая коробка:**
- Контролируешь каждое переключение (addSubview, removeFromSuperview)
- Больше контроля, но больше работы
- Легко ошибиться

**SwiftUI = автоматическая коробка:**
- Описываешь желаемое состояние (скорость)
- Система сама решает, как переключать передачи (обновлять UI)
- Меньше контроля, но проще и безопаснее

---

## Связанные темы

- [[ios-uikit]] — императивный фреймворк iOS (predecessor SwiftUI)
- [[ios-combine]] — реактивное программирование для работы с async данными
- [[swift-concurrency]] — async/await, actors, structured concurrency
- [[ios-core-data]] — фреймворк для персистентности данных
- [[ios-navigation]] — паттерны навигации (Coordinator, MVVM-C)
- [[ios-animations]] — Core Animation, UIViewPropertyAnimator
- [[ios-testing]] — XCTest, UI Testing, TDD для SwiftUI
- [[android-compose]] — декларативный UI для Android (аналог SwiftUI)
- [[react-native]] — кроссплатформенный декларативный фреймворк
- [[flutter]] — декларативный UI от Google (Dart)
- [[design-patterns-mvvm]] — архитектурный паттерн для SwiftUI
- [[ios-accessibility]] — VoiceOver, Dynamic Type, инклюзивный дизайн
- [[apple-hig]] — Human Interface Guidelines

## Связь с другими темами

**[[ios-swiftui-vs-uikit]]** — Понимание различий между SwiftUI и UIKit необходимо для принятия архитектурных решений в iOS-проектах. SwiftUI использует декларативную парадигму с автоматическим diffing и реактивным state management, тогда как UIKit основан на императивном подходе с ручной синхронизацией состояния и UI. В реальных проектах оба фреймворка часто сосуществуют через UIViewRepresentable и UIHostingController, поэтому глубокое знание обоих подходов позволяет выбирать оптимальный инструмент для каждого конкретного компонента.

**[[ios-state-management]]** — Управление состоянием является центральной концепцией SwiftUI, определяющей всю архитектуру приложения. SwiftUI предоставляет иерархию property wrappers (@State, @Binding, @StateObject, @ObservedObject, @EnvironmentObject), каждый из которых решает конкретную задачу владения и передачи данных. Неправильный выбор wrapper-а приводит к потере состояния, лишним перерисовкам или утечкам памяти, поэтому понимание data flow в SwiftUI является фундаментальным навыком для продуктивной разработки.

## Источники и дальнейшее чтение

- **Eidhof C., Willeke F., et al. (2020). *Thinking in SwiftUI.* objc.io.** — Лучшая книга для формирования правильных ментальных моделей SwiftUI. Авторы детально разбирают layout system, view lifecycle и data flow, помогая перейти от императивного мышления UIKit к декларативному подходу SwiftUI.
- **Eidhof C., Airspeed Velocity, et al. (2019). *Advanced Swift.* objc.io.** — Глубокое погружение в Swift-механизмы, лежащие в основе SwiftUI: протоколы, generics, property wrappers и result builders (@ViewBuilder). Понимание этих концепций на уровне языка критически важно для написания эффективных и переиспользуемых SwiftUI-компонентов.
- **Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* O'Reilly.** — Комплексное руководство, охватывающее основы Swift, жизненный цикл iOS-приложения и новые возможности SwiftUI в iOS 17 (включая Observable macro, NavigationStack и интеграцию с SwiftData). Подходит как для начинающих, так и для опытных разработчиков, обновляющих знания.

---

## Полезные ресурсы

**Официальные:**
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui) — официальная документация Apple
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui) — пошаговые туториалы
- [WWDC Sessions](https://developer.apple.com/videos/swiftui) — видео с конференций Apple

**Сообщество:**
- [Hacking with Swift](https://www.hackingwithswift.com/quick-start/swiftui) — туториалы Paul Hudson
- [SwiftUI Lab](https://swiftui-lab.com) — продвинутые техники
- [objc.io SwiftUI](https://www.objc.io/blog/tags/swiftui/) — статьи и книги

**Инструменты:**
- [SF Symbols](https://developer.apple.com/sf-symbols/) — иконки для SwiftUI
- [SwiftUI Inspector](https://github.com/jonreid/SwiftUIInspector) — тестирование views

---

## Заключение

SwiftUI революционизировал разработку под iOS, сократив количество кода и повысив производительность. Декларативный подход требует смены мышления от "как построить UI" к "что должно быть на экране", но результат — более чистый, поддерживаемый и выразительный код.

**Ключевые принципы для запоминания:**
1. UI — это функция состояния: `UI = f(State)`
2. Используй правильные property wrappers для ownership
3. Порядок модификаторов имеет значение
4. View — это lightweight struct, создаваемый часто
5. SwiftUI сам управляет обновлениями через diffing

**Следующие шаги:**
- Изучи [[ios-combine]] для реактивного программирования
- Освой [[swift-concurrency]] для async/await
- Практикуй MVVM архитектуру с [[design-patterns-mvvm]]
- Сравни с [[android-compose]] для понимания кроссплатформенных концепций

---

## Проверь себя

> [!question]- Почему SwiftUI пересоздаёт struct View при каждом обновлении состояния, и не является ли это неэффективным?
> SwiftUI View -- это дешёвый value type (struct), описывающий UI декларативно. При изменении @State создаётся новый struct, но SwiftUI использует diffing алгоритм для определения минимальных изменений в реальном UI-дереве. Фактически обновляются только изменившиеся элементы, а не весь экран.

> [!question]- Вы видите, что экран мерцает при каждом нажатии кнопки. @State переменная обновляется в body. В чём проблема?
> Вероятно, тяжёлая операция выполняется синхронно в body или создаётся новый объект при каждом вызове body (например, StateObject в body вместо @StateObject property). Body должен быть чистой функцией без side effects. Тяжёлые операции -- в .task или .onAppear.

> [!question]- Почему @StateObject нужно использовать вместо @ObservedObject при создании объекта внутри View?
> @StateObject гарантирует, что объект создаётся один раз и переживает пересоздание struct View. @ObservedObject не владеет объектом -- если View пересоздаётся (что происходит часто), объект пересоздаётся тоже, теряя состояние. @StateObject = создатель, @ObservedObject = наблюдатель.

---

## Ключевые карточки

Чем декларативный подход SwiftUI отличается от императивного UIKit?
?
SwiftUI описывает "что" должно быть на экране, система сама определяет "как" обновлять. UIKit требует явного создания, настройки и обновления каждого элемента. SwiftUI автоматически обновляет UI при изменении состояния.

Что такое @State и когда его использовать?
?
@State -- property wrapper для локального состояния View. Хранит значение в отдельной памяти, переживающей пересоздание struct. Используется для простых value types (Bool, String, Int), принадлежащих только этому View.

В чём разница между @StateObject и @ObservedObject?
?
@StateObject создаёт и владеет ObservableObject (используется при первом создании). @ObservedObject только наблюдает за объектом, полученным извне. При пересоздании View @StateObject сохраняет объект, @ObservedObject -- нет.

Как работают модификаторы (modifiers) в SwiftUI?
?
Каждый модификатор создаёт новый View, оборачивающий предыдущий. Порядок модификаторов важен: .padding().background(.red) -- padding внутри красного фона, .background(.red).padding() -- padding снаружи красного фона.

Что такое @Binding и зачем он нужен?
?
@Binding создаёт двустороннюю связь с состоянием родительского View. Дочерний View может читать и изменять значение, не владея им. Передаётся через $: Toggle(isOn: $isEnabled). Обеспечивает single source of truth.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-state-management]] | Освоить @StateObject, @EnvironmentObject и продвинутое управление состоянием |
| Углубиться | [[ios-swiftui-vs-uikit]] | Понять когда SwiftUI, когда UIKit, и как их совмещать |
| Смежная тема | [[android-compose]] | Сравнить декларативные подходы Apple и Google |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
