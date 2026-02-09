---
title: "KMP Navigation: Decompose, Voyager, Compose Navigation"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, navigation, decompose, voyager, compose-navigation, routing]
related:
  - "[[00-kmp-overview]]"
  - "[[kmp-architecture-patterns]]"
  - "[[compose-mp-overview]]"
cs-foundations:
  - "[[graph-data-structures]]"
  - "[[stack-data-structure]]"
  - "[[state-machines-theory]]"
  - "[[component-lifecycle]]"
---

# KMP Navigation

> **TL;DR:** Три основных решения: Compose Navigation (официальный, type-safe с @Serializable, deep linking), Decompose (lifecycle-aware BLoC, навигация в shared code), Voyager (простой, Compose-first). Compose Navigation 2.9.1+ — рекомендуется для новых проектов с CMP. Decompose — если нужна навигация независимая от UI (SwiftUI + Compose). Voyager — быстрый старт, Compose-only. Все поддерживают nested navigation, tabs, back stack.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Compose Basics | UI framework | [[compose-basics]] |
| KMP Project Structure | Source sets | [[kmp-project-structure]] |
| kotlinx.serialization | Type-safe routes | [[kotlin-serialization]] |
| **CS-foundations** | | |
| Stack (LIFO) | Back stack operations | [[stack-data-structure]] |
| Graph Traversal | Navigation graph | [[graph-data-structures]] |
| State Machines | Screen transitions | [[state-machines-theory]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **NavController** | Управляет navigation stack | GPS-навигатор |
| **NavHost** | Контейнер для destinations | Автомобиль |
| **Back Stack** | История навигации | История посещений |
| **Deep Link** | Прямая ссылка на экран | Адрес квартиры |
| **Component** | Decompose unit с lifecycle | Живой организм |
| **Screen** | Voyager unit | Страница книги |
| **Child Stack** | Decompose navigation model | Стопка карт |

---

## Почему Navigation — это Stack + Graph?

### Фундамент: Back Stack как Stack (LIFO)

**Navigation back stack** — это классическая структура данных Stack с операциями:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACK STACK = STACK (LIFO)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Операции:                                                         │
│   ─────────────────────────────                                     │
│   push(Screen) — добавить экран в стек   │ navigate()               │
│   pop()        — убрать верхний экран    │ popBackStack()           │
│   peek()       — посмотреть верхний      │ currentDestination       │
│                                                                     │
│   Пример навигации:                                                 │
│   ─────────────────────────────                                     │
│                                                                     │
│   User actions:     Stack state:                                    │
│   ─────────────     ────────────                                    │
│   Start app      →  [Home]                                          │
│   Tap "Profile"  →  [Home, Profile]         push(Profile)           │
│   Tap "Settings" →  [Home, Profile, Settings]  push(Settings)       │
│   Press Back     →  [Home, Profile]         pop()                   │
│   Press Back     →  [Home]                  pop()                   │
│                                                                     │
│   Time Complexity: push O(1), pop O(1)                              │
│   Space Complexity: O(n) где n = количество экранов в стеке         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Navigation Graph — это Directed Graph

**Navigation destinations** образуют **directed graph**:
- Вершины (nodes) = Screens/Destinations
- Рёбра (edges) = Possible transitions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NAVIGATION GRAPH                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   NavGraph = (V, E) где:                                            │
│   V = {Home, Profile, Settings, UserDetail, ...}                    │
│   E = {(Home → Profile), (Home → UserDetail), (Profile → Settings)} │
│                                                                     │
│            ┌──────────────┐                                         │
│            │     Home     │                                         │
│            └──────┬───────┘                                         │
│                   │                                                 │
│         ┌────────┼────────┐                                         │
│         ▼        ▼        ▼                                         │
│   ┌──────────┐ ┌──────────┐ ┌──────────────┐                        │
│   │ Profile  │ │  Search  │ │ UserDetail   │                        │
│   └────┬─────┘ └──────────┘ └──────────────┘                        │
│        │                                                            │
│        ▼                                                            │
│   ┌──────────┐                                                      │
│   │ Settings │                                                      │
│   └──────────┘                                                      │
│                                                                     │
│   Type-safe routes (@Serializable) = Type-safe edges                │
│   Deep links = Direct paths to any node                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Почему Decompose использует Component Tree?

**Decompose** моделирует навигацию как **дерево компонентов** с lifecycle:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPONENT TREE (DECOMPOSE)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   RootComponent                                                     │
│       │                                                             │
│       ├── HomeComponent (active)                                    │
│       │       │                                                     │
│       │       └── ItemListComponent                                 │
│       │                                                             │
│       ├── DetailsComponent (in back stack)                          │
│       │       │                                                     │
│       │       └── CommentsComponent                                 │
│       │                                                             │
│       └── DialogComponent (slot, null if hidden)                    │
│                                                                     │
│   Lifecycle follows tree structure:                                 │
│   ─────────────────────────────────                                 │
│   Parent.onDestroy() → все children уничтожаются                    │
│   Только active child получает lifecycle events                     │
│   Back stack children сохраняют state но "paused"                   │
│                                                                     │
│   Child types:                                                      │
│   ─────────────────────────────────                                 │
│   Child Stack — для navigation history (LIFO)                       │
│   Child Slot  — для dialogs, bottom sheets (0 or 1 child)           │
│   Child Pages — для pagers (multiple children with selection)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Преимущества Component Tree:**
- **Lifecycle management** — каждый component знает свой lifecycle
- **State persistence** — components в back stack сохраняют state
- **UI independence** — дерево существует отдельно от UI framework
- **Testability** — components тестируются без UI

### State Machine в контексте Navigation

**Screen transitions** можно моделировать как **Finite State Machine**:

```kotlin
// Navigation как State Machine
sealed class NavState {
    object Home : NavState()
    object Profile : NavState()
    data class UserDetail(val userId: String) : NavState()
}

sealed class NavEvent {
    object GoToProfile : NavEvent()
    data class GoToUser(val id: String) : NavEvent()
    object GoBack : NavEvent()
}

// Transition function: (State, Event) → State
fun transition(state: NavState, event: NavEvent): NavState = when {
    state is NavState.Home && event is NavEvent.GoToProfile -> NavState.Profile
    state is NavState.Home && event is NavEvent.GoToUser -> NavState.UserDetail(event.id)
    event is NavEvent.GoBack -> NavState.Home  // simplified
    else -> state  // invalid transition, stay
}
```

**Compose Navigation** реализует это через:
- `@Serializable` routes = States
- `navigate()` calls = Events
- NavController = State Machine с back stack

### Deep Links = Direct Graph Traversal

**Deep link** — это прямой путь к узлу графа без прохождения промежуточных:

```
Normal navigation:     App Start → Home → Profile → Settings
Deep link:            App Start ──────────────────→ Settings
                                    (direct edge)
```

Технически deep link создаёт **синтетический back stack**:
```kotlin
// Deep link to Settings создаёт:
backStack = [Home, Settings]  // не [Home, Profile, Settings]
```

---

## Обзор решений

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NAVIGATION SOLUTIONS FOR KMP                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   COMPOSE NAVIGATION (Official)                                     │
│   ─────────────────────────────                                     │
│   • Type-safe routes с @Serializable                                │
│   • Deep linking support                                            │
│   • AndroidX Navigation API                                         │
│   • Рекомендуется для новых CMP проектов                            │
│                                                                     │
│   DECOMPOSE (Arkivanov)                                             │
│   ─────────────────────────────                                     │
│   • Lifecycle-aware Components                                      │
│   • Навигация в shared code (UI independent)                        │
│   • Поддержка SwiftUI + Compose + React                             │
│   • Для complex navigation scenarios                                │
│                                                                     │
│   VOYAGER (Adriel Café)                                             │
│   ─────────────────────────────                                     │
│   • Compose-first design                                            │
│   • Простой API                                                     │
│   • ScreenModel (ViewModel alternative)                             │
│   • Быстрый старт                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Сравнение

| Аспект | Compose Nav | Decompose | Voyager |
|--------|-------------|-----------|---------|
| **Type safety** | ✅ @Serializable | ✅ Sealed classes | ⚠️ Runtime |
| **Deep linking** | ✅ Built-in | ⚠️ Manual | ⚠️ Manual |
| **UI independence** | ❌ Compose only | ✅ Pluggable UI | ❌ Compose only |
| **Learning curve** | Low | Medium | Low |
| **SwiftUI support** | ❌ | ✅ | ❌ |
| **Lifecycle** | ViewModelScope | ComponentContext | ScreenModel |
| **Back handling** | ✅ Built-in | ✅ Built-in | ✅ Built-in |

---

## Compose Navigation (Official)

### Setup

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("org.jetbrains.androidx.navigation:navigation-compose:2.9.1")
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-core:1.7.3")
        }
    }
}

plugins {
    kotlin("plugin.serialization") version "2.1.0"
}
```

### Type-Safe Routes

```kotlin
import kotlinx.serialization.Serializable

// Simple routes
@Serializable
object Home

@Serializable
object Profile

@Serializable
object Settings

// Routes with parameters
@Serializable
data class UserDetail(val userId: String)

@Serializable
data class ProductDetail(
    val productId: Int,
    val showReviews: Boolean = false
)
```

### NavHost Configuration

```kotlin
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Home
    ) {
        composable<Home> {
            HomeScreen(
                onNavigateToProfile = { navController.navigate(Profile) },
                onNavigateToUser = { userId ->
                    navController.navigate(UserDetail(userId))
                }
            )
        }

        composable<Profile> {
            ProfileScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable<UserDetail> { backStackEntry ->
            val userDetail: UserDetail = backStackEntry.toRoute()
            UserDetailScreen(
                userId = userDetail.userId,
                onBack = { navController.popBackStack() }
            )
        }

        composable<ProductDetail> { backStackEntry ->
            val product: ProductDetail = backStackEntry.toRoute()
            ProductDetailScreen(
                productId = product.productId,
                showReviews = product.showReviews
            )
        }
    }
}
```

### Navigation Actions

```kotlin
@Composable
fun HomeScreen(
    onNavigateToProfile: () -> Unit,
    onNavigateToUser: (String) -> Unit
) {
    Column {
        Button(onClick = onNavigateToProfile) {
            Text("Go to Profile")
        }

        Button(onClick = { onNavigateToUser("user123") }) {
            Text("View User")
        }
    }
}
```

### Deep Links

```kotlin
import androidx.navigation.navDeepLink

NavHost(navController = navController, startDestination = Home) {
    composable<UserDetail>(
        deepLinks = listOf(
            navDeepLink<UserDetail>(
                basePath = "myapp://users"
            )
        )
    ) { backStackEntry ->
        val userDetail: UserDetail = backStackEntry.toRoute()
        UserDetailScreen(userId = userDetail.userId)
    }
}

// URL: myapp://users/user123
// → UserDetail(userId = "user123")
```

### Nested Navigation

```kotlin
@Serializable
object MainGraph

@Serializable
object AuthGraph

NavHost(navController = navController, startDestination = AuthGraph) {
    navigation<AuthGraph>(startDestination = Login) {
        composable<Login> { /* ... */ }
        composable<Register> { /* ... */ }
    }

    navigation<MainGraph>(startDestination = Home) {
        composable<Home> { /* ... */ }
        composable<Profile> { /* ... */ }
    }
}
```

### Transitions

```kotlin
NavHost(
    navController = navController,
    startDestination = Home,
    enterTransition = {
        slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Left)
    },
    exitTransition = {
        slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Left)
    },
    popEnterTransition = {
        slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Right)
    },
    popExitTransition = {
        slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Right)
    }
) {
    // destinations
}
```

---

## Decompose

### Setup

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("com.arkivanov.decompose:decompose:3.2.2")
            implementation("com.arkivanov.decompose:extensions-compose:3.2.2")
        }
    }
}
```

### Component Definition

```kotlin
import com.arkivanov.decompose.ComponentContext
import com.arkivanov.decompose.router.stack.*
import com.arkivanov.decompose.value.Value
import kotlinx.serialization.Serializable

interface RootComponent {
    val stack: Value<ChildStack<*, Child>>

    fun onBackClicked()

    sealed class Child {
        class HomeChild(val component: HomeComponent) : Child()
        class DetailsChild(val component: DetailsComponent) : Child()
    }
}

class DefaultRootComponent(
    componentContext: ComponentContext
) : RootComponent, ComponentContext by componentContext {

    private val navigation = StackNavigation<Config>()

    override val stack: Value<ChildStack<*, RootComponent.Child>> =
        childStack(
            source = navigation,
            serializer = Config.serializer(),
            initialConfiguration = Config.Home,
            handleBackButton = true,
            childFactory = ::child
        )

    private fun child(
        config: Config,
        componentContext: ComponentContext
    ): RootComponent.Child =
        when (config) {
            is Config.Home -> RootComponent.Child.HomeChild(
                DefaultHomeComponent(
                    componentContext = componentContext,
                    onItemSelected = { navigation.push(Config.Details(it)) }
                )
            )
            is Config.Details -> RootComponent.Child.DetailsChild(
                DefaultDetailsComponent(
                    componentContext = componentContext,
                    itemId = config.itemId,
                    onBack = { navigation.pop() }
                )
            )
        }

    override fun onBackClicked() {
        navigation.pop()
    }

    @Serializable
    sealed interface Config {
        @Serializable
        data object Home : Config

        @Serializable
        data class Details(val itemId: String) : Config
    }
}
```

### Child Components

```kotlin
interface HomeComponent {
    val items: Value<List<Item>>
    fun onItemClicked(id: String)
}

class DefaultHomeComponent(
    componentContext: ComponentContext,
    private val onItemSelected: (String) -> Unit
) : HomeComponent, ComponentContext by componentContext {

    private val _items = MutableValue(listOf<Item>())
    override val items: Value<List<Item>> = _items

    init {
        // Load items
    }

    override fun onItemClicked(id: String) {
        onItemSelected(id)
    }
}

interface DetailsComponent {
    val item: Value<Item?>
    fun onBackClicked()
}

class DefaultDetailsComponent(
    componentContext: ComponentContext,
    private val itemId: String,
    private val onBack: () -> Unit
) : DetailsComponent, ComponentContext by componentContext {

    private val _item = MutableValue<Item?>(null)
    override val item: Value<Item?> = _item

    init {
        // Load item by itemId
    }

    override fun onBackClicked() {
        onBack()
    }
}
```

### Compose UI

```kotlin
import com.arkivanov.decompose.extensions.compose.stack.Children
import com.arkivanov.decompose.extensions.compose.stack.animation.slide
import com.arkivanov.decompose.extensions.compose.stack.animation.stackAnimation

@Composable
fun RootContent(component: RootComponent) {
    Children(
        stack = component.stack,
        animation = stackAnimation(slide())
    ) { child ->
        when (val instance = child.instance) {
            is RootComponent.Child.HomeChild ->
                HomeContent(instance.component)
            is RootComponent.Child.DetailsChild ->
                DetailsContent(instance.component)
        }
    }
}

@Composable
fun HomeContent(component: HomeComponent) {
    val items by component.items.subscribeAsState()

    LazyColumn {
        items(items) { item ->
            Text(
                text = item.name,
                modifier = Modifier.clickable {
                    component.onItemClicked(item.id)
                }
            )
        }
    }
}
```

### Entry Point

```kotlin
// Android
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = retainedComponent { componentContext ->
            DefaultRootComponent(componentContext)
        }

        setContent {
            RootContent(root)
        }
    }
}

// iOS
fun MainViewController() = ComposeUIViewController {
    val root = remember {
        DefaultRootComponent(DefaultComponentContext(lifecycle = ...))
    }
    RootContent(root)
}
```

### Child Slot (Dialogs, Sheets)

```kotlin
private val dialogNavigation = SlotNavigation<DialogConfig>()

val dialogSlot: Value<ChildSlot<*, DialogChild>> =
    childSlot(
        source = dialogNavigation,
        serializer = DialogConfig.serializer(),
        handleBackButton = true,
        childFactory = ::dialogChild
    )

fun showDialog(config: DialogConfig) {
    dialogNavigation.activate(config)
}

fun dismissDialog() {
    dialogNavigation.dismiss()
}
```

---

## Voyager

### Setup

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("cafe.adriel.voyager:voyager-navigator:1.1.0-beta02")
            implementation("cafe.adriel.voyager:voyager-screenmodel:1.1.0-beta02")
            implementation("cafe.adriel.voyager:voyager-transitions:1.1.0-beta02")
            implementation("cafe.adriel.voyager:voyager-tab-navigator:1.1.0-beta02")
        }
    }
}
```

### Screen Definition

```kotlin
import cafe.adriel.voyager.core.screen.Screen

// Simple screen
object HomeScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Column {
            Text("Home")
            Button(onClick = { navigator.push(DetailsScreen("item123")) }) {
                Text("Go to Details")
            }
        }
    }
}

// Screen with parameters
data class DetailsScreen(val itemId: String) : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Column {
            Text("Details: $itemId")
            Button(onClick = { navigator.pop() }) {
                Text("Back")
            }
        }
    }
}
```

### Navigator Setup

```kotlin
import cafe.adriel.voyager.navigator.Navigator
import cafe.adriel.voyager.transitions.SlideTransition

@Composable
fun App() {
    Navigator(HomeScreen) { navigator ->
        SlideTransition(navigator)
    }
}
```

### ScreenModel (ViewModel)

```kotlin
import cafe.adriel.voyager.core.model.ScreenModel
import cafe.adriel.voyager.core.model.screenModelScope

class HomeScreenModel : ScreenModel {
    private val _items = MutableStateFlow<List<Item>>(emptyList())
    val items: StateFlow<List<Item>> = _items.asStateFlow()

    init {
        screenModelScope.launch {
            _items.value = loadItems()
        }
    }
}

// Usage in Screen
object HomeScreen : Screen {
    @Composable
    override fun Content() {
        val screenModel = rememberScreenModel { HomeScreenModel() }
        val items by screenModel.items.collectAsState()

        LazyColumn {
            items(items) { item ->
                Text(item.name)
            }
        }
    }
}
```

### Tab Navigation

```kotlin
import cafe.adriel.voyager.navigator.tab.*

object HomeTab : Tab {
    override val options: TabOptions
        @Composable
        get() = TabOptions(
            index = 0u,
            title = "Home",
            icon = rememberVectorPainter(Icons.Default.Home)
        )

    @Composable
    override fun Content() {
        Text("Home Tab")
    }
}

object ProfileTab : Tab {
    override val options: TabOptions
        @Composable
        get() = TabOptions(
            index = 1u,
            title = "Profile",
            icon = rememberVectorPainter(Icons.Default.Person)
        )

    @Composable
    override fun Content() {
        Text("Profile Tab")
    }
}

@Composable
fun MainScreen() {
    TabNavigator(HomeTab) { tabNavigator ->
        Scaffold(
            bottomBar = {
                NavigationBar {
                    TabNavigationItem(HomeTab)
                    TabNavigationItem(ProfileTab)
                }
            }
        ) {
            CurrentTab()
        }
    }
}

@Composable
private fun RowScope.TabNavigationItem(tab: Tab) {
    val tabNavigator = LocalTabNavigator.current

    NavigationBarItem(
        selected = tabNavigator.current == tab,
        onClick = { tabNavigator.current = tab },
        icon = { Icon(tab.options.icon!!, tab.options.title) },
        label = { Text(tab.options.title) }
    )
}
```

### Nested Navigation

```kotlin
data class HomeScreen : Screen {
    @Composable
    override fun Content() {
        // Parent navigator
        val parentNavigator = LocalNavigator.currentOrThrow

        // Nested navigator for this screen
        Navigator(NestedHomeScreen) { nestedNavigator ->
            SlideTransition(nestedNavigator)
        }
    }
}

// Navigate to parent
val parentNavigator = LocalNavigator.current?.parent
parentNavigator?.push(OtherScreen)
```

---

## Когда что выбирать

```
✅ COMPOSE NAVIGATION:
   • Новые CMP проекты
   • Type-safe routes важны
   • Deep linking нужен
   • AndroidX экосистема

✅ DECOMPOSE:
   • UI-independent navigation
   • SwiftUI + Compose
   • Complex lifecycle requirements
   • Unit-testable navigation logic

✅ VOYAGER:
   • Быстрый старт
   • Compose-only проект
   • Простые requirements
   • ScreenModel для state
```

---

## Мифы и заблуждения

### Миф 1: "Compose Navigation — это только для Android"

**Реальность:** С версии 2.8+ navigation-compose полностью поддерживает Compose Multiplatform. `org.jetbrains.androidx.navigation:navigation-compose` работает на Android, iOS, Desktop, Web.

### Миф 2: "Decompose слишком сложный для простых приложений"

**Реальность:** Decompose **может** быть простым:
- Child Stack для basic navigation — несложнее Voyager
- Сложность появляется при multi-stack/slot scenarios
- "Сложность" — это цена за UI-independence и testability

Для CMP-only проектов Compose Navigation проще. Decompose нужен когда есть SwiftUI.

### Миф 3: "Voyager устарел из-за official navigation"

**Реальность:** Voyager активно развивается (1.1.0+) и имеет свою нишу:
- Простейший API для быстрого старта
- ScreenModel интегрирован
- Tab navigation из коробки
- Wasm поддержка

Voyager — valid choice для Compose-only проектов с простыми requirements.

### Миф 4: "Type-safe routes требуют много boilerplate"

**Реальность:** С `@Serializable` объектами boilerplate минимален:
```kotlin
@Serializable object Home  // Всё! Type-safe route готов
@Serializable data class User(val id: String)  // С параметрами
```

### Миф 5: "Deep links работают автоматически"

**Реальность:** Deep links требуют:
1. Platform configuration (AndroidManifest, Info.plist)
2. URL scheme регистрации
3. Правильного mapping routes → URLs
4. Тестирования на обеих платформах

Compose Navigation упрощает mapping, но не eliminates platform setup.

### Миф 6: "Нужно выбрать ОДИН подход навигации"

**Реальность:** Можно комбинировать:
- Compose Navigation для main flow
- Decompose для complex feature modules
- Custom solution для specific cases

Главное — consistency внутри каждого модуля.

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Navigation in Compose](https://kotlinlang.org/docs/multiplatform/compose-navigation.html) | Official | Type-safe navigation |
| [Deep Links](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-navigation-deep-links.html) | Official | Deep linking guide |
| [Decompose](https://arkivanov.github.io/Decompose/) | Official | Full documentation |
| [Voyager](https://voyager.adriel.cafe/) | Official | API reference |

### Статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [Navigation Solutions](https://proandroiddev.com/navigating-the-waters-of-kotlin-multiplatform-exploring-navigation-solutions-eef81aaa1a61) | Blog | Comparison |
| [Decompose Navigation](https://speednetsoftware.com/decompose-navigation/) | Blog | Practical guide |
| [Voyager Tutorial](https://medium.com/@italord.melo/voyager-compose-multiplatform-navigation-and-viewmodels-screenmodel-b36693484d98) | Blog | Getting started |

### Примеры

| Ресурс | Описание |
|--------|----------|
| [DecomposeNavigation](https://github.com/mkonkel/DecomposeNavigation) | Decompose showcase |
| [VoyagerNavigation](https://github.com/mkonkel/VoyagerNavigation) | Voyager showcase |
| [JetpackComposeNavigation](https://github.com/mkonkel/JetpackComposeNavigation) | Official Nav showcase |

### CS-фундамент

| Тема | Почему важно | Где изучить |
|------|--------------|-------------|
| Stack (LIFO) | Back stack implementation | [[stack-data-structure]] |
| Directed Graph | Navigation graph structure | [[graph-data-structures]] |
| State Machines | Screen transitions model | [[state-machines-theory]] |
| Tree Traversal | Component hierarchy | [[tree-data-structures]] |
| Lifecycle Patterns | Component lifecycle | [[component-lifecycle]] |

---

*Проверено: 2026-01-09 | navigation-compose 2.9.1, Decompose 3.2.2, Voyager 1.1.0-beta02*
