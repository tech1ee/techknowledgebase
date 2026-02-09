---
title: "Cross-Platform: Declarative UI — SwiftUI vs Compose"
created: 2026-01-11
type: comparison
tags: [cross-platform, swiftui, compose, ui]
---

# Declarative UI: SwiftUI vs Jetpack Compose

## TL;DR: Сравнительная таблица

| Характеристика | SwiftUI | Jetpack Compose |
|----------------|---------|-----------------|
| **Появление** | WWDC 2019 (iOS 13) | Stable 1.0 (2021) |
| **Язык** | Swift | Kotlin |
| **State wrapper** | `@State` | `remember { mutableStateOf() }` |
| **Two-way binding** | `@Binding` | value + callback (State Hoisting) |
| **ViewModel owner** | `@StateObject` | `viewModel()` |
| **ViewModel observer** | `@ObservedObject` | `collectAsStateWithLifecycle()` |
| **Recomposition trigger** | `@Published` | `State<T>` изменение |
| **Layout vertical** | `VStack` | `Column` |
| **Layout horizontal** | `HStack` | `Row` |
| **Layout overlay** | `ZStack` | `Box` |
| **Modifier syntax** | `.modifier(value)` | `Modifier.modifier(value)` |
| **Animation implicit** | `.animation()` | `animate*AsState` |
| **Lazy lists** | `LazyVStack`, `List` | `LazyColumn` |
| **Multiplatform** | Apple only | KMP (iOS, Android, Desktop, Web) |

---

## Почему обе платформы перешли на Declarative UI (2019-2021)?

### Проблема: Imperative UI Hell

**iOS (UIKit):**
```swift
class ProfileViewController: UIViewController {
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var loadingIndicator: UIActivityIndicatorView!

    private var user: User? { didSet { updateUI() } }

    func updateUI() {
        // ПРОБЛЕМА: 10+ мест для обновления, легко забыть одно
        nameLabel.text = user?.name
        loadingIndicator.isHidden = user != nil
    }
}
```

**Android (View System):**
```kotlin
class ProfileActivity : AppCompatActivity() {
    private lateinit var nameTextView: TextView
    private var user: User? = null
        set(value) { field = value; updateUI() }

    private fun updateUI() {
        // ПРОБЛЕМА: ручная синхронизация state и UI
        nameTextView.text = user?.name
    }
}
```

### Решение: UI = f(State)

```
┌─────────────────────────────────────────────────────────────────┐
│  ФОРМУЛА:  UI = f(State)                                        │
│                                                                 │
│  State изменился → Framework автоматически пересоздаёт UI       │
│                                                                 │
│  SwiftUI:   @State var count = 0  →  var body  →  Text("\(count)")
│  Compose:   var count by remember →  @Composable →  Text("$count")
└─────────────────────────────────────────────────────────────────┘
```

**Timeline:**
- 2013: React доказал концепцию
- 2017: Flutter (Dart + widgets)
- 2019: SwiftUI (Apple)
- 2021: Jetpack Compose (Google)

---

## 5 аналогий для понимания

### 1. Blueprint vs Building (Чертёж vs Строительство)

**Императивно:** "Возьми кирпич, положи сюда, нанеси раствор..."
**Декларативно:** "Вот чертёж дома: 2 этажа, 4 комнаты"

```swift
// SwiftUI — чертёж
var body: some View {
    VStack { Floor(rooms: 4); Floor(rooms: 4) }
}
```

```kotlin
// Compose — чертёж
@Composable fun House() {
    Column { Floor(rooms = 4); Floor(rooms = 4) }
}
```

### 2. Термостат (State Management)

**Императивно:** "18°C? Включи на 50%. 20°C? Уменьши до 30%..."
**Декларативно:** "Желаемая температура: 21°C" (термостат сам решает)

```swift
@State private var targetTemp = 21
Slider(value: $targetTemp, in: 16...28)
```

```kotlin
var targetTemp by remember { mutableStateOf(21f) }
Slider(value = targetTemp, onValueChange = { targetTemp = it })
```

### 3. Рецепт vs Инструкция повару

**Инструкция:** "Возьми сковороду, налей масло, подожди..."
**Рецепт:** "Яичница: 2 яйца, средняя прожарка, соль"

### 4. Пульт ДУ и телевизор (Binding)

Телевизор = Source of Truth, Пульты = Bindings

```swift
// SwiftUI
@State private var volume = 50  // Телевизор
RemoteControl(volume: $volume)  // Пульт (binding)
```

```kotlin
// Compose — State Hoisting
var volume by remember { mutableStateOf(50) }
RemoteControl(volume = volume, onVolumeChange = { volume = it })
```

### 5. LEGO (Composition)

Готовые детали соединяются предсказуемо, легко заменить одну другой.

---

## Синтаксис: State Management

### @State vs remember

```swift
// SwiftUI
struct CounterView: View {
    @State private var count = 0
    var body: some View {
        Button("Count: \(count)") { count += 1 }
    }
}
```

```kotlin
// Compose
@Composable
fun CounterView() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) { Text("Count: $count") }
}
```

### @Binding vs State Hoisting

```swift
// SwiftUI
struct Parent: View {
    @State private var text = ""
    var body: some View { Child(text: $text) }
}
struct Child: View {
    @Binding var text: String
    var body: some View { TextField("", text: $text) }
}
```

```kotlin
// Compose
@Composable
fun Parent() {
    var text by remember { mutableStateOf("") }
    Child(text = text, onTextChange = { text = it })
}
@Composable
fun Child(text: String, onTextChange: (String) -> Unit) {
    TextField(value = text, onValueChange = onTextChange)
}
```

### @StateObject vs ViewModel

```swift
// SwiftUI
class UserVM: ObservableObject {
    @Published var users: [User] = []
}
struct UserList: View {
    @StateObject private var vm = UserVM()
    var body: some View { List(vm.users) { Text($0.name) } }
}
```

```kotlin
// Compose
class UserVM : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()
}
@Composable
fun UserList(vm: UserVM = viewModel()) {
    val users by vm.users.collectAsStateWithLifecycle()
    LazyColumn { items(users, key = { it.id }) { Text(it.name) } }
}
```

---

## Recomposition: body vs @Composable

### Процесс обновления UI

```
┌─────────────────────────────────────────────────────────────────┐
│                    SWIFTUI REDRAW                               │
│                                                                 │
│  1. @State/@Published изменение                                 │
│  2. body вызывается ЦЕЛИКОМ (новый View struct)                │
│  3. Attribute Graph сравнивает старое/новое дерево             │
│  4. Только изменившиеся элементы обновляются в render tree     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    COMPOSE RECOMPOSITION                        │
│                                                                 │
│  1. State<T> изменение                                          │
│  2. Compose находит composables, читающие этот state           │
│  3. ТОЛЬКО эти composables вызываются заново                    │
│  4. Slot Table обновляется, layout/draw phases                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Сравнение гранулярности

```swift
// SwiftUI — body вызывается целиком
struct ParentView: View {
    @State private var counter = 0
    @State private var name = "Alice"

    var body: some View {  // Вызывается при изменении counter ИЛИ name
        VStack {
            Text("Counter: \(counter)")  // Нужно обновить
            Text("Name: \(name)")        // Не нужно, но body вызван
            Button("Increment") { counter += 1 }
        }
    }
}
```

```kotlin
// Compose — гранулярная recomposition
@Composable
fun ParentView() {
    var counter by remember { mutableStateOf(0) }
    var name by remember { mutableStateOf("Alice") }

    Column {
        CounterText(counter)  // Recompose только если counter изменился
        NameText(name)        // Не затронут при изменении counter
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}

@Composable
fun CounterText(counter: Int) { Text("Counter: $counter") }

@Composable
fun NameText(name: String) { Text("Name: $name") }
```

### Оптимизация: key и identity

```swift
// SwiftUI — Equatable для skip redraw
struct ExpensiveView: View, Equatable {
    let data: ExpensiveData
    var body: some View { /* ... */ }
    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.data.id == rhs.data.id
    }
}
```

```kotlin
// Compose — key для identity
@Composable
fun ItemList(items: List<Item>) {
    LazyColumn {
        items(items, key = { it.id }) { item ->  // key помогает отслеживать
            ItemRow(item)
        }
    }
}
```

---

## Layout: VStack/HStack vs Column/Row

```swift
// SwiftUI
VStack(alignment: .leading, spacing: 16) {
    Text("Title").font(.title)
    HStack(spacing: 8) {
        Image(systemName: "star.fill")
        Text("Featured")
    }
}
```

```kotlin
// Compose
Column(
    verticalArrangement = Arrangement.spacedBy(16.dp),
    horizontalAlignment = Alignment.Start
) {
    Text("Title", style = MaterialTheme.typography.titleLarge)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Icon(Icons.Default.Star, null)
        Text("Featured")
    }
}
```

| SwiftUI | Compose | Назначение |
|---------|---------|------------|
| `VStack` | `Column` | Вертикальный |
| `HStack` | `Row` | Горизонтальный |
| `ZStack` | `Box` | Наложение |
| `LazyVStack` | `LazyColumn` | Ленивый список |

---

## Modifiers: порядок важен!

```swift
// SwiftUI — РАЗНЫЙ результат
Text("A").padding().background(.red)   // Padding внутри красного
Text("B").background(.red).padding()   // Padding снаружи красного
```

```kotlin
// Compose — РАЗНЫЙ результат
Text("A", Modifier.padding(16.dp).background(Color.Red))
Text("B", Modifier.background(Color.Red).padding(16.dp))
```

| Функция | SwiftUI | Compose |
|---------|---------|---------|
| Padding | `.padding(16)` | `Modifier.padding(16.dp)` |
| Background | `.background(.blue)` | `Modifier.background(Color.Blue)` |
| Corner | `.cornerRadius(8)` | `Modifier.clip(RoundedCornerShape(8.dp))` |
| Click | `.onTapGesture {}` | `Modifier.clickable {}` |

---

## Animation

### Implicit анимации

```swift
// SwiftUI — .animation() modifier
struct AnimatedView: View {
    @State private var expanded = false

    var body: some View {
        VStack {
            Rectangle()
                .frame(width: expanded ? 200 : 100, height: 100)
                .animation(.spring(), value: expanded)  // Implicit

            Button("Toggle") {
                withAnimation(.easeInOut(duration: 0.3)) {  // Explicit block
                    expanded.toggle()
                }
            }
        }
    }
}
```

```kotlin
// Compose — animate*AsState
@Composable
fun AnimatedView() {
    var expanded by remember { mutableStateOf(false) }

    val width by animateDpAsState(
        targetValue = if (expanded) 200.dp else 100.dp,
        animationSpec = spring()
    )

    Column {
        Box(
            modifier = Modifier
                .width(width)
                .height(100.dp)
                .background(Color.Blue)
        )
        Button(onClick = { expanded = !expanded }) { Text("Toggle") }
    }
}
```

### Visibility анимации

```swift
// SwiftUI — transitions
struct TransitionExample: View {
    @State private var showDetail = false

    var body: some View {
        VStack {
            if showDetail {
                Text("Detail View")
                    .transition(.slide)  // или .opacity, .scale
            }
            Button("Toggle") {
                withAnimation { showDetail.toggle() }
            }
        }
    }
}
```

```kotlin
// Compose — AnimatedVisibility
@Composable
fun TransitionExample() {
    var showDetail by remember { mutableStateOf(false) }

    Column {
        AnimatedVisibility(
            visible = showDetail,
            enter = slideInHorizontally() + fadeIn(),
            exit = slideOutHorizontally() + fadeOut()
        ) {
            Text("Detail View")
        }
        Button(onClick = { showDetail = !showDetail }) { Text("Toggle") }
    }
}
```

### Animation Specs сравнение

| Тип | SwiftUI | Compose |
|-----|---------|---------|
| Linear | `.linear(duration: 0.3)` | `tween(300, easing = LinearEasing)` |
| Ease | `.easeInOut(duration: 0.3)` | `tween(300, easing = FastOutSlowInEasing)` |
| Spring | `.spring()` | `spring()` |
| Repeat | `.repeatForever()` | `infiniteRepeatable(tween(1000))` |

---

## KMP: Compose Multiplatform на iOS

```
Shared Code (commonMain)
    │
    ├── Android Target → Skia + OpenGL/Vulkan → Android
    ├── iOS Target     → Skia + Metal        → iOS
    └── Desktop Target → Skia + OpenGL/Metal → Windows/macOS
```

```kotlin
// shared/src/commonMain/kotlin/App.kt
@Composable
fun App() {
    MaterialTheme {
        var count by remember { mutableStateOf(0) }
        Button(onClick = { count++ }) { Text("Count: $count") }
    }
}
```

```swift
// iosApp/ContentView.swift
struct ContentView: View {
    var body: some View {
        ComposeView().ignoresSafeArea()
    }
}
```

---

## 6 типичных ошибок

### 1. Создание объектов в body

```swift
// ПЛОХО
var body: some View {
    let formatter = DateFormatter()  // Каждый раз!
    Text(formatter.string(from: date))
}
// ХОРОШО: создайте formatter как property
```

```kotlin
// ПЛОХО
@Composable fun View() {
    val formatter = SimpleDateFormat()  // Каждая recomposition!
}
// ХОРОШО: val formatter = remember { SimpleDateFormat() }
```

### 2. Неправильный порядок модификаторов

`.padding().background()` ≠ `.background().padding()`

### 3. @ObservedObject вместо @StateObject

```swift
// ПЛОХО: ViewModel пересоздаётся
var body: some View {
    ChildView(viewModel: UserViewModel())  // Новый каждый раз!
}
// ХОРОШО: @StateObject private var vm = UserViewModel()
```

### 4. Забыли key для списка

```swift
ForEach(items, id: \.id) { ... }  // ХОРОШО
```

```kotlin
items(items, key = { it.id }) { ... }  // ХОРОШО
```

### 5. Side effects в body

```swift
// ПЛОХО: вызывается каждый render
var body: some View {
    viewModel.loadUsers()  // НЕТ!
}
// ХОРОШО: .task { await viewModel.loadUsers() }
```

```kotlin
// ПЛОХО
@Composable fun View() {
    viewModel.loadUsers()  // НЕТ!
}
// ХОРОШО: LaunchedEffect(Unit) { viewModel.loadUsers() }
```

### 6. Lambda без remember (Compose)

```kotlin
// С Kotlin 2.0 Strong Skipping менее критично, но:
val onClick = remember { { viewModel.doSomething() } }
// Или лучше: onClick = viewModel::doSomething
```

---

## Ментальные модели

### SwiftUI Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│  View = Struct + Description                                    │
│                                                                 │
│  struct MyView: View {                                          │
│      @State var count = 0    ← State живёт вне struct          │
│                                                                 │
│      var body: some View {   ← Описание, не создание UI         │
│          Text("\(count)")    ← View struct (cheap, immutable)   │
│      }                                                          │
│  }                                                              │
│                                                                 │
│  Цикл: State → body (new struct) → diffing → partial update    │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое понимание:**
- View struct — это описание UI, не сам UI
- body вызывается часто — делайте его дешёвым
- State отделён от View — struct immutable, state mutable

### Compose Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│  Composable = Function + Slot Table Entry                       │
│                                                                 │
│  @Composable                                                    │
│  fun MyView() {                                                 │
│      var count by remember { mutableStateOf(0) }  ← Slot Table │
│      Text("$count")    ← emit в Slot Table                     │
│  }                                                              │
│                                                                 │
│  Цикл: State → find affected composables → recompose → update  │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое понимание:**
- Composable — функция, которая "emits" UI в Slot Table
- remember — сохраняет значение в Slot Table между вызовами
- Recomposition гранулярная — только затронутые функции
- Порядок вызовов важен — Slot Table индексируется по call site

### Сравнение моделей

| Аспект | SwiftUI | Compose |
|--------|---------|---------|
| Единица UI | struct View | @Composable function |
| Хранение state | SwiftUI Storage | Slot Table |
| Гранулярность | Весь body | Только затронутые |
| Identity | Structural (тип + позиция) | Positional (call site) |
| Explicit identity | `.id()` modifier | `key { }` composable |

---

## Проверь себя

1. Что означает UI = f(State)?
2. Когда @State vs @StateObject?
3. Когда remember vs rememberSaveable?
4. Почему порядок модификаторов важен?
5. Почему нельзя вызывать API в body?
6. Зачем key для списков?

---

## Связи

- [[ios-swiftui]] — глубокое погружение в SwiftUI
- [[android-compose]] — глубокое погружение в Jetpack Compose
- [[cross-platform-overview]] — общий обзор iOS vs Android
- [[kotlin-multiplatform/03-compose-multiplatform/compose-mp-overview]] — Compose Multiplatform
