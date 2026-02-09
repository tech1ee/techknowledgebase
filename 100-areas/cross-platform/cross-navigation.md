---
title: "Cross-Platform: Navigation — NavigationStack vs Navigation Component"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - navigation
  - ios
  - android
  - type/comparison
  - level/intermediate
---

# Кросс-платформенная навигация: NavigationStack vs Navigation Component

## TL;DR

| Аспект | iOS (SwiftUI) | Android (Compose) |
|--------|---------------|-------------------|
| **Основная концепция** | Stack (стек) | Graph (граф) |
| **Главный компонент** | `NavigationStack` | `NavHost` + `NavController` |
| **Определение маршрутов** | Type-safe через `Hashable` | Routes как строки или type-safe |
| **Передача параметров** | Через `Binding` или модель | Arguments в Bundle или type-safe |
| **Deep linking** | Встроен в `NavigationStack` | Через `deepLink` в `composable()` |
| **Обратная навигация** | Автоматический back button | `popBackStack()` |
| **Анимации** | Встроенные, кастомизация через `navigationTransition` | `AnimatedNavHost`, `EnterTransition` |
| **Сохранение состояния** | `@SceneStorage`, `@AppStorage` | `rememberSaveable`, SavedStateHandle |
| **Вложенная навигация** | Вложенные `NavigationStack` | Nested graphs |
| **Legacy API** | `NavigationView` (deprecated) | Fragment Navigation |

---

## Философия навигации

### iOS: Стековая модель

iOS исторически построена на концепции **стека экранов**. Пользователь "проваливается" вглубь приложения, а затем возвращается назад. Это отражает физическую метафору стопки карточек:

```
┌─────────────┐
│   Screen C  │  ← Текущий экран (вершина стека)
├─────────────┤
│   Screen B  │
├─────────────┤
│   Screen A  │  ← Корневой экран
└─────────────┘
```

**Ключевые принципы iOS:**
- Линейная навигация (push/pop)
- Каждый экран знает только о своих данных
- Обратная навигация всегда предсказуема
- Модальные экраны как исключение из стека

### Android: Графовая модель

Android использует **граф навигации** — сеть связанных экранов с множественными путями:

```
        ┌──────────┐
        │  Home    │
        └────┬─────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│ List │ │Search│ │Profile│
└──┬───┘ └──────┘ └───┬───┘
   │                  │
   ▼                  ▼
┌──────┐          ┌──────┐
│Detail│◄─────────│Settings│
└──────┘          └──────┘
```

**Ключевые принципы Android:**
- Множественные пути к одному экрану
- Actions определяют переходы
- Deep linking как первоклассный гражданин
- Back stack может быть манипулирован

---

## 5 аналогий для понимания

### Аналогия 1: Книга vs Веб-сайт

| iOS Navigation | Android Navigation |
|----------------|-------------------|
| Чтение книги: страница за страницей, закладки для возврата | Веб-сёрфинг: гиперссылки, множество вкладок, история браузера |

### Аналогия 2: Лифт vs Метро

**iOS** — это **лифт**: движение вверх-вниз по одной шахте. Можно остановиться на любом этаже, но путь линеен.

**Android** — это **метро**: сеть станций с пересадками. Можно добраться из A в B разными маршрутами.

### Аналогия 3: Стопка тарелок vs Карта города

**iOS NavigationStack** — стопка тарелок. Добавляешь сверху (`push`), снимаешь сверху (`pop`). Нельзя вытащить тарелку из середины без последствий.

**Android NavGraph** — карта города. Можешь проложить маршрут между любыми точками, есть главные улицы и переулки.

### Аналогия 4: Театр vs Кинотеатр-мультиплекс

**iOS** — классический театр с одной сценой. Спектакли идут последовательно.

**Android** — мультиплекс с несколькими залами. Можно переключаться между фильмами (bottom navigation), каждый зал имеет свою историю просмотра.

### Аналогия 5: Git rebase vs Git merge

**iOS** — `git rebase`: линейная история, чистый стек коммитов.

**Android** — `git merge`: ветвления, слияния, сложный граф истории.

---

## SwiftUI NavigationStack vs Jetpack Navigation Component

### SwiftUI NavigationStack (iOS 16+)

```swift
// Определение навигации
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Product.self) { product in
                    ProductDetailView(product: product)
                }
                .navigationDestination(for: Category.self) { category in
                    CategoryView(category: category)
                }
        }
    }
}

// Навигация к экрану
struct HomeView: View {
    var body: some View {
        List(products) { product in
            NavigationLink(value: product) {
                ProductRow(product: product)
            }
        }
    }
}

// Программная навигация
Button("Go to Product") {
    path.append(Product(id: 1, name: "iPhone"))
}

// Возврат к корню
Button("Pop to Root") {
    path.removeLast(path.count)
}
```

### Jetpack Compose Navigation

```kotlin
// Определение навигации
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onProductClick = { productId ->
                    navController.navigate("product/$productId")
                }
            )
        }

        composable(
            route = "product/{productId}",
            arguments = listOf(
                navArgument("productId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val productId = backStackEntry.arguments?.getInt("productId") ?: 0
            ProductDetailScreen(productId = productId)
        }

        composable("category/{categoryId}") { backStackEntry ->
            CategoryScreen(
                categoryId = backStackEntry.arguments?.getString("categoryId") ?: ""
            )
        }
    }
}

// Программная навигация
Button(onClick = { navController.navigate("product/123") }) {
    Text("Go to Product")
}

// Возврат к корню
Button(onClick = {
    navController.popBackStack("home", inclusive = false)
}) {
    Text("Pop to Root")
}
```

### Type-safe Navigation (Compose 2.8+)

```kotlin
// Определение маршрутов через sealed class
@Serializable
sealed class Screen {
    @Serializable
    data object Home : Screen()

    @Serializable
    data class Product(val id: Int, val name: String) : Screen()

    @Serializable
    data class Category(val id: String) : Screen()
}

// Использование
NavHost(
    navController = navController,
    startDestination = Screen.Home
) {
    composable<Screen.Home> {
        HomeScreen()
    }

    composable<Screen.Product> { backStackEntry ->
        val product: Screen.Product = backStackEntry.toRoute()
        ProductDetailScreen(product.id, product.name)
    }
}

// Навигация
navController.navigate(Screen.Product(id = 123, name = "iPhone"))
```

---

## UINavigationController vs FragmentManager

### UIKit UINavigationController

```swift
class MainViewController: UIViewController {

    // Push экран
    func showDetail(for item: Item) {
        let detailVC = DetailViewController(item: item)
        navigationController?.pushViewController(detailVC, animated: true)
    }

    // Pop текущий экран
    func goBack() {
        navigationController?.popViewController(animated: true)
    }

    // Pop до корня
    func popToRoot() {
        navigationController?.popToRootViewController(animated: true)
    }

    // Pop до конкретного экрана
    func popToSpecific() {
        if let targetVC = navigationController?.viewControllers
            .first(where: { $0 is TargetViewController }) {
            navigationController?.popToViewController(targetVC, animated: true)
        }
    }

    // Замена всего стека
    func replaceStack() {
        let newRoot = NewRootViewController()
        navigationController?.setViewControllers([newRoot], animated: true)
    }
}

// Кастомизация navigation bar
extension DetailViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        title = "Детали"
        navigationItem.largeTitleDisplayMode = .never
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            systemItem: .action,
            primaryAction: UIAction { [weak self] _ in
                self?.shareItem()
            }
        )
    }
}
```

### Android FragmentManager (Legacy)

```kotlin
class MainActivity : AppCompatActivity() {

    // Добавление фрагмента
    fun showDetail(item: Item) {
        supportFragmentManager.commit {
            setReorderingAllowed(true)
            replace(R.id.fragment_container, DetailFragment.newInstance(item))
            addToBackStack("detail")
        }
    }

    // Pop текущий фрагмент
    fun goBack() {
        supportFragmentManager.popBackStack()
    }

    // Pop до конкретного фрагмента
    fun popToSpecific(name: String) {
        supportFragmentManager.popBackStack(name, 0)
    }

    // Pop до корня (очистка back stack)
    fun popToRoot() {
        supportFragmentManager.popBackStack(null, FragmentManager.POP_BACK_STACK_INCLUSIVE)
    }

    // Замена без добавления в back stack
    fun replaceWithoutBackStack(fragment: Fragment) {
        supportFragmentManager.commit {
            replace(R.id.fragment_container, fragment)
        }
    }
}

// Fragment с аргументами
class DetailFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(item: Item): DetailFragment {
            return DetailFragment().apply {
                arguments = bundleOf(ARG_ITEM_ID to item.id)
            }
        }
    }

    private val itemId: Int by lazy {
        requireArguments().getInt(ARG_ITEM_ID)
    }
}
```

---

## Deep Linking: сравнение подходов

### iOS Deep Linking

```swift
// SwiftUI с NavigationStack
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: DeepLinkDestination.self) { destination in
                    switch destination {
                    case .product(let id):
                        ProductView(id: id)
                    case .category(let name):
                        CategoryView(name: name)
                    case .profile(let userId):
                        ProfileView(userId: userId)
                    }
                }
        }
        .onOpenURL { url in
            handleDeepLink(url)
        }
    }

    private func handleDeepLink(_ url: URL) {
        // myapp://product/123
        // myapp://category/electronics
        // myapp://profile/user456

        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let host = components.host else { return }

        let pathComponents = components.path.split(separator: "/")

        switch host {
        case "product":
            if let idString = pathComponents.first,
               let id = Int(idString) {
                path.append(DeepLinkDestination.product(id: id))
            }
        case "category":
            if let name = pathComponents.first {
                path.append(DeepLinkDestination.category(name: String(name)))
            }
        case "profile":
            if let userId = pathComponents.first {
                path.append(DeepLinkDestination.profile(userId: String(userId)))
            }
        default:
            break
        }
    }
}

enum DeepLinkDestination: Hashable {
    case product(id: Int)
    case category(name: String)
    case profile(userId: String)
}
```

### Android Deep Linking

```kotlin
// В NavHost
NavHost(navController, startDestination = "home") {
    composable(
        route = "product/{productId}",
        arguments = listOf(
            navArgument("productId") { type = NavType.IntType }
        ),
        deepLinks = listOf(
            navDeepLink {
                uriPattern = "myapp://product/{productId}"
            },
            navDeepLink {
                uriPattern = "https://myapp.com/product/{productId}"
            }
        )
    ) { backStackEntry ->
        ProductScreen(
            productId = backStackEntry.arguments?.getInt("productId") ?: 0
        )
    }

    composable(
        route = "category/{categoryName}",
        deepLinks = listOf(
            navDeepLink {
                uriPattern = "myapp://category/{categoryName}"
                action = Intent.ACTION_VIEW
            }
        )
    ) { backStackEntry ->
        CategoryScreen(
            categoryName = backStackEntry.arguments?.getString("categoryName") ?: ""
        )
    }
}

// AndroidManifest.xml
/*
<activity android:name=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="myapp"
            android:host="product" />
        <data
            android:scheme="https"
            android:host="myapp.com"
            android:pathPrefix="/product" />
    </intent-filter>
</activity>
*/

// Программный deep link
fun handleIntent(intent: Intent) {
    navController.handleDeepLink(intent)
}
```

### Сравнительная таблица Deep Linking

| Аспект | iOS | Android |
|--------|-----|---------|
| **Регистрация схемы** | Info.plist | AndroidManifest.xml |
| **Universal Links** | apple-app-site-association | assetlinks.json |
| **Обработка** | `onOpenURL` modifier | `intent-filter` + `handleDeepLink` |
| **Параметры** | Ручной парсинг URL | Автоматически через arguments |
| **Валидация** | Ручная | Встроенная в NavType |

---

## Передача аргументов между экранами

### iOS: Передача данных

```swift
// Способ 1: Через NavigationLink value (рекомендуемый)
struct Product: Hashable, Identifiable {
    let id: Int
    let name: String
    let price: Double
}

struct ProductListView: View {
    let products: [Product]

    var body: some View {
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

// Способ 2: Через Environment
class CartManager: ObservableObject {
    @Published var items: [Product] = []
}

struct ContentView: View {
    @StateObject private var cartManager = CartManager()

    var body: some View {
        NavigationStack {
            HomeView()
        }
        .environmentObject(cartManager)
    }
}

struct ProductDetailView: View {
    @EnvironmentObject var cartManager: CartManager
    let product: Product

    var body: some View {
        Button("Add to Cart") {
            cartManager.items.append(product)
        }
    }
}

// Способ 3: Через Binding (для редактирования)
struct EditProductView: View {
    @Binding var product: Product

    var body: some View {
        TextField("Name", text: $product.name)
    }
}
```

### Android: Передача данных

```kotlin
// Способ 1: Через route arguments (примитивы)
composable(
    route = "product/{id}/{name}",
    arguments = listOf(
        navArgument("id") { type = NavType.IntType },
        navArgument("name") {
            type = NavType.StringType
            nullable = true
            defaultValue = null
        }
    )
) { backStackEntry ->
    ProductDetailScreen(
        id = backStackEntry.arguments?.getInt("id") ?: 0,
        name = backStackEntry.arguments?.getString("name")
    )
}

// Навигация с аргументами
navController.navigate("product/123/iPhone")

// Способ 2: Type-safe navigation (Compose 2.8+)
@Serializable
data class ProductRoute(
    val id: Int,
    val name: String,
    val price: Double
)

composable<ProductRoute> { backStackEntry ->
    val route: ProductRoute = backStackEntry.toRoute()
    ProductDetailScreen(route.id, route.name, route.price)
}

navController.navigate(ProductRoute(123, "iPhone", 999.0))

// Способ 3: Через ViewModel + SavedStateHandle
@HiltViewModel
class ProductViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val productId: Int = savedStateHandle["productId"] ?: 0

    val product = savedStateHandle.getStateFlow("product", Product())
}

// Способ 4: Передача результата назад
// Экран A
val result = navController.currentBackStackEntry
    ?.savedStateHandle
    ?.getStateFlow<Product?>("selected_product", null)
    ?.collectAsState()

// Экран B (выбор продукта)
fun onProductSelected(product: Product) {
    navController.previousBackStackEntry
        ?.savedStateHandle
        ?.set("selected_product", product)
    navController.popBackStack()
}
```

### Сравнение передачи данных

| Сценарий | iOS | Android |
|----------|-----|---------|
| **Простые данные** | `NavigationLink(value:)` | Route arguments |
| **Сложные объекты** | Передача напрямую (Hashable) | Serializable route или ViewModel |
| **Глобальное состояние** | `@EnvironmentObject` | Hilt + ViewModel |
| **Результат назад** | Callback или Binding | SavedStateHandle |
| **Редактирование** | `@Binding` | StateFlow в ViewModel |

---

## Управление Back Stack

### iOS: NavigationPath

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView(path: $path)
                .navigationDestination(for: Screen.self) { screen in
                    screenView(for: screen)
                }
        }
    }
}

enum Screen: Hashable {
    case list
    case detail(id: Int)
    case settings
    case profile
}

struct NavigationManager {
    var path: Binding<NavigationPath>

    // Push один экран
    func push(_ screen: Screen) {
        path.wrappedValue.append(screen)
    }

    // Push несколько экранов
    func pushMultiple(_ screens: [Screen]) {
        screens.forEach { path.wrappedValue.append($0) }
    }

    // Pop один экран
    func pop() {
        if !path.wrappedValue.isEmpty {
            path.wrappedValue.removeLast()
        }
    }

    // Pop N экранов
    func pop(count: Int) {
        let removeCount = min(count, path.wrappedValue.count)
        path.wrappedValue.removeLast(removeCount)
    }

    // Pop до корня
    func popToRoot() {
        path.wrappedValue.removeLast(path.wrappedValue.count)
    }

    // Заменить весь стек
    func replaceStack(with screens: [Screen]) {
        path.wrappedValue = NavigationPath()
        screens.forEach { path.wrappedValue.append($0) }
    }
}
```

### Android: NavController Back Stack

```kotlin
@Composable
fun BackStackManager(navController: NavController) {

    // Push (navigate)
    fun navigateTo(route: String) {
        navController.navigate(route)
    }

    // Pop один экран
    fun pop(): Boolean {
        return navController.popBackStack()
    }

    // Pop до конкретного экрана
    fun popTo(route: String, inclusive: Boolean = false) {
        navController.popBackStack(route, inclusive)
    }

    // Pop до корня
    fun popToRoot() {
        navController.popBackStack(
            navController.graph.startDestinationId,
            inclusive = false
        )
    }

    // Navigate с очисткой back stack
    fun navigateAndClearStack(route: String) {
        navController.navigate(route) {
            popUpTo(navController.graph.id) {
                inclusive = true
            }
        }
    }

    // Single top (не дублировать экран)
    fun navigateSingleTop(route: String) {
        navController.navigate(route) {
            launchSingleTop = true
        }
    }

    // Сохранение и восстановление состояния
    fun navigateWithStateRestore(route: String) {
        navController.navigate(route) {
            popUpTo(navController.graph.findStartDestination().id) {
                saveState = true
            }
            launchSingleTop = true
            restoreState = true
        }
    }
}

// Проверка текущего состояния back stack
@Composable
fun BackStackInfo(navController: NavController) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    // Количество экранов в back stack
    val backStackSize = navController.currentBackStack.value.size

    Text("Current: $currentRoute, Stack size: $backStackSize")
}
```

### Bottom Navigation с сохранением состояния

```swift
// iOS: TabView с NavigationStack в каждой вкладке
struct MainTabView: View {
    @State private var selectedTab = 0
    @State private var homePath = NavigationPath()
    @State private var searchPath = NavigationPath()
    @State private var profilePath = NavigationPath()

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack(path: $homePath) {
                HomeView()
            }
            .tabItem { Label("Home", systemImage: "house") }
            .tag(0)

            NavigationStack(path: $searchPath) {
                SearchView()
            }
            .tabItem { Label("Search", systemImage: "magnifyingglass") }
            .tag(1)

            NavigationStack(path: $profilePath) {
                ProfileView()
            }
            .tabItem { Label("Profile", systemImage: "person") }
            .tag(2)
        }
    }
}
```

```kotlin
// Android: Nested navigation graphs
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                bottomNavItems.forEach { item ->
                    NavigationBarItem(
                        selected = currentDestination?.hierarchy?.any {
                            it.route == item.route
                        } == true,
                        onClick = {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(item.icon, contentDescription = item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "home_graph",
            modifier = Modifier.padding(padding)
        ) {
            // Nested graph для Home
            navigation(
                startDestination = "home",
                route = "home_graph"
            ) {
                composable("home") { HomeScreen() }
                composable("home/detail/{id}") { DetailScreen() }
            }

            // Nested graph для Search
            navigation(
                startDestination = "search",
                route = "search_graph"
            ) {
                composable("search") { SearchScreen() }
                composable("search/results") { ResultsScreen() }
            }

            // Nested graph для Profile
            navigation(
                startDestination = "profile",
                route = "profile_graph"
            ) {
                composable("profile") { ProfileScreen() }
                composable("profile/settings") { SettingsScreen() }
            }
        }
    }
}
```

---

## KMP Navigation: Decompose и Voyager

### Decompose

```kotlin
// Определение компонента
interface RootComponent {
    val stack: Value<ChildStack<*, Child>>

    sealed class Child {
        class Home(val component: HomeComponent) : Child()
        class Details(val component: DetailsComponent) : Child()
    }

    fun onHomeClicked()
    fun onDetailsClicked(id: Long)
}

// Реализация
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

    private fun child(config: Config, context: ComponentContext): RootComponent.Child =
        when (config) {
            is Config.Home -> RootComponent.Child.Home(
                DefaultHomeComponent(context)
            )
            is Config.Details -> RootComponent.Child.Details(
                DefaultDetailsComponent(context, config.id)
            )
        }

    override fun onHomeClicked() {
        navigation.popTo(0)
    }

    override fun onDetailsClicked(id: Long) {
        navigation.push(Config.Details(id))
    }

    @Serializable
    private sealed interface Config {
        @Serializable
        data object Home : Config

        @Serializable
        data class Details(val id: Long) : Config
    }
}

// UI для Compose
@Composable
fun RootContent(component: RootComponent) {
    Children(
        stack = component.stack,
        animation = stackAnimation(fade() + scale())
    ) { child ->
        when (val instance = child.instance) {
            is RootComponent.Child.Home -> HomeContent(instance.component)
            is RootComponent.Child.Details -> DetailsContent(instance.component)
        }
    }
}

// UI для SwiftUI
struct RootView: View {
    let component: RootComponent

    @ObservedObject
    private var stack: ObservableValue<ChildStack<AnyObject, RootComponentChild>>

    init(_ component: RootComponent) {
        self.component = component
        self.stack = ObservableValue(component.stack)
    }

    var body: some View {
        StackView(
            stackValue: stack,
            getTitle: { _ in "" },
            onBack: { component.onHomeClicked() }
        ) { child in
            switch child {
            case let child as RootComponentChildHome:
                HomeView(child.component)
            case let child as RootComponentChildDetails:
                DetailsView(child.component)
            default:
                EmptyView()
            }
        }
    }
}
```

### Voyager

```kotlin
// Определение Screen
class HomeScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Column {
            Text("Home Screen")
            Button(onClick = { navigator.push(DetailsScreen(123)) }) {
                Text("Go to Details")
            }
        }
    }
}

data class DetailsScreen(val id: Long) : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Column {
            Text("Details for $id")
            Button(onClick = { navigator.pop() }) {
                Text("Go Back")
            }
        }
    }
}

// Корневой Navigator
@Composable
fun App() {
    Navigator(HomeScreen()) { navigator ->
        SlideTransition(navigator)
    }
}

// Tab Navigation
@Composable
fun TabNavigationExample() {
    TabNavigator(HomeTab) {
        Scaffold(
            bottomBar = {
                NavigationBar {
                    TabNavigationItem(HomeTab)
                    TabNavigationItem(SearchTab)
                    TabNavigationItem(ProfileTab)
                }
            }
        ) {
            CurrentTab()
        }
    }
}

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
        Navigator(HomeScreen())
    }
}
```

### Сравнение KMP решений

| Аспект | Decompose | Voyager |
|--------|-----------|---------|
| **Архитектура** | Component-based | Screen-based |
| **Сложность** | Выше (больше boilerplate) | Ниже (проще начать) |
| **Типобезопасность** | Полная | Частичная |
| **Lifecycle** | Полный контроль | Автоматический |
| **State preservation** | Встроено | Требует настройки |
| **iOS поддержка** | Отличная | Хорошая |
| **Тестируемость** | Высокая | Средняя |
| **Анимации** | Через Essenty | Встроенные |

---

## 6 типичных ошибок навигации

### Ошибка 1: Навигация в @Composable / body

```swift
// iOS: НЕПРАВИЛЬНО
struct BadView: View {
    @State private var path = NavigationPath()

    var body: some View {
        // Вызов навигации в body вызовет бесконечный цикл!
        path.append(Screen.home) // ПЛОХО!

        NavigationStack(path: $path) {
            Text("Hello")
        }
    }
}

// iOS: ПРАВИЛЬНО
struct GoodView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Text("Hello")
        }
        .onAppear {
            path.append(Screen.home) // OK в onAppear
        }
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО
@Composable
fun BadScreen(navController: NavController) {
    // Навигация во время композиции!
    navController.navigate("details") // ПЛОХО!

    Text("Hello")
}

// Android: ПРАВИЛЬНО
@Composable
fun GoodScreen(navController: NavController) {
    LaunchedEffect(Unit) {
        navController.navigate("details") // OK в LaunchedEffect
    }

    // Или через callback
    Button(onClick = { navController.navigate("details") }) {
        Text("Go to Details")
    }
}
```

### Ошибка 2: Утечка NavController / NavigationPath

```kotlin
// Android: НЕПРАВИЛЬНО - хранение NavController в ViewModel
class BadViewModel : ViewModel() {
    lateinit var navController: NavController // Утечка!

    fun navigateToDetails() {
        navController.navigate("details")
    }
}

// Android: ПРАВИЛЬНО - использование событий
class GoodViewModel : ViewModel() {
    private val _navigationEvent = MutableSharedFlow<NavigationEvent>()
    val navigationEvent = _navigationEvent.asSharedFlow()

    fun navigateToDetails() {
        viewModelScope.launch {
            _navigationEvent.emit(NavigationEvent.ToDetails)
        }
    }
}

@Composable
fun Screen(viewModel: GoodViewModel, navController: NavController) {
    LaunchedEffect(Unit) {
        viewModel.navigationEvent.collect { event ->
            when (event) {
                NavigationEvent.ToDetails -> navController.navigate("details")
            }
        }
    }
}
```

### Ошибка 3: Неправильная обработка конфигурационных изменений

```kotlin
// Android: НЕПРАВИЛЬНО - потеря состояния
@Composable
fun BadScreen() {
    var data by remember { mutableStateOf<Data?>(null) } // Потеряется при повороте!
}

// Android: ПРАВИЛЬНО - сохранение состояния
@Composable
fun GoodScreen() {
    var data by rememberSaveable { mutableStateOf<Data?>(null) }
}

// Или через ViewModel
@HiltViewModel
class ScreenViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    val data = savedStateHandle.getStateFlow<Data?>("data", null)
}
```

### Ошибка 4: Дублирование экранов в стеке

```swift
// iOS: НЕПРАВИЛЬНО
Button("Go to Profile") {
    path.append(Screen.profile) // Может добавить дубликаты!
}

// iOS: ПРАВИЛЬНО
Button("Go to Profile") {
    // Проверить, что экрана ещё нет
    if !path.codable.contains(where: {
        ($0 as? Screen) == .profile
    }) {
        path.append(Screen.profile)
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО
Button(onClick = { navController.navigate("profile") }) {
    Text("Go to Profile")
}

// Android: ПРАВИЛЬНО
Button(onClick = {
    navController.navigate("profile") {
        launchSingleTop = true // Предотвращает дубликаты
    }
}) {
    Text("Go to Profile")
}
```

### Ошибка 5: Игнорирование системной кнопки "Назад"

```kotlin
// Android: НЕПРАВИЛЬНО - не обрабатывает системный back
@Composable
fun BadScreen(onBack: () -> Unit) {
    Column {
        Button(onClick = onBack) {
            Text("Back")
        }
    }
}

// Android: ПРАВИЛЬНО - обработка системного back
@Composable
fun GoodScreen(onBack: () -> Unit) {
    BackHandler(enabled = true) {
        onBack()
    }

    Column {
        Button(onClick = onBack) {
            Text("Back")
        }
    }
}
```

```swift
// iOS: Обработка edge swipe
struct DetailView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack {
            Text("Detail")
        }
        .navigationBarBackButtonHidden(false) // Не скрывать!
        .gesture(
            DragGesture()
                .onEnded { value in
                    if value.translation.width > 100 {
                        dismiss()
                    }
                }
        )
    }
}
```

### Ошибка 6: Смешивание парадигм навигации

```swift
// iOS: НЕПРАВИЛЬНО - смешивание NavigationStack и sheet
struct BadView: View {
    @State private var showSheet = false

    var body: some View {
        NavigationStack {
            VStack {
                NavigationLink("Push") { DetailView() }
                Button("Show Sheet") { showSheet = true }
            }
            .sheet(isPresented: $showSheet) {
                // Sheet с вложенным NavigationStack - путаница!
                NavigationStack {
                    SettingsView()
                }
            }
        }
    }
}

// iOS: ПРАВИЛЬНО - четкое разделение
struct GoodView: View {
    @State private var showSheet = false
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            VStack {
                NavigationLink(value: Screen.detail) {
                    Text("Push")
                }
                Button("Show Sheet") { showSheet = true }
            }
            .navigationDestination(for: Screen.self) { screen in
                // Все push-навигации здесь
            }
        }
        .sheet(isPresented: $showSheet) {
            // Модальное окно - отдельный контекст
            SettingsSheet()
        }
    }
}
```

---

## Проверь себя

### Вопрос 1
Какой тип должна реализовать модель для использования в `NavigationLink(value:)` в SwiftUI?

<details>
<summary>Ответ</summary>

`Hashable`. Модель должна соответствовать протоколу `Hashable`:

```swift
struct Product: Hashable {
    let id: Int
    let name: String
}
```
</details>

### Вопрос 2
Как в Jetpack Compose Navigation предотвратить добавление дубликатов экрана в back stack?

<details>
<summary>Ответ</summary>

Использовать `launchSingleTop = true`:

```kotlin
navController.navigate("profile") {
    launchSingleTop = true
}
```
</details>

### Вопрос 3
Что произойдет, если вызвать `navController.navigate()` непосредственно в `@Composable` функции?

<details>
<summary>Ответ</summary>

Произойдет бесконечный цикл перекомпозиции. Навигация вызывает изменение состояния, что триггерит рекомпозицию, которая снова вызывает навигацию.

Правильно: использовать `LaunchedEffect` или callback:

```kotlin
LaunchedEffect(Unit) {
    navController.navigate("destination")
}
```
</details>

### Вопрос 4
Как в SwiftUI очистить весь navigation stack и вернуться к корневому экрану?

<details>
<summary>Ответ</summary>

```swift
@State private var path = NavigationPath()

// Очистка стека
path.removeLast(path.count)

// Или
path = NavigationPath()
```
</details>

### Вопрос 5
Какой modifier в Android Compose позволяет обрабатывать системную кнопку "Назад"?

<details>
<summary>Ответ</summary>

`BackHandler`:

```kotlin
BackHandler(enabled = true) {
    // Обработка нажатия кнопки "Назад"
    onBack()
}
```
</details>

### Вопрос 6
Чем отличается `popUpTo` от `popBackStack` в Jetpack Navigation?

<details>
<summary>Ответ</summary>

- `popBackStack()` — немедленно удаляет экраны из back stack
- `popUpTo` — используется внутри `navigate()` для удаления экранов перед добавлением нового

```kotlin
// popBackStack - отдельная операция
navController.popBackStack("home", inclusive = false)

// popUpTo - часть навигации
navController.navigate("profile") {
    popUpTo("home") {
        inclusive = false
        saveState = true
    }
}
```
</details>

### Вопрос 7
Как передать результат с дочернего экрана на родительский в Jetpack Compose?

<details>
<summary>Ответ</summary>

Через `SavedStateHandle`:

```kotlin
// Дочерний экран (устанавливает результат)
navController.previousBackStackEntry
    ?.savedStateHandle
    ?.set("result_key", resultValue)
navController.popBackStack()

// Родительский экран (получает результат)
val result by navController.currentBackStackEntry
    ?.savedStateHandle
    ?.getStateFlow<ResultType?>("result_key", null)
    ?.collectAsState()
```
</details>

### Вопрос 8
Что такое `inclusive` параметр в `popBackStack` / `popUpTo`?

<details>
<summary>Ответ</summary>

`inclusive` определяет, будет ли целевой экран также удален из стека:

- `inclusive = false` — удаляет все экраны ДО целевого, оставляя целевой в стеке
- `inclusive = true` — удаляет все экраны ДО целевого И сам целевой экран

```kotlin
// Вернуться к Home, оставив Home в стеке
navController.popBackStack("home", inclusive = false)

// Удалить всё включая Home
navController.popBackStack("home", inclusive = true)
```
</details>

### Практическое задание

Реализуйте навигацию для приложения со следующей структурой:
- Home -> ProductList -> ProductDetail
- Bottom navigation: Home, Search, Cart, Profile
- Каждая вкладка имеет свой navigation stack
- Deep link: `myapp://product/{id}` открывает ProductDetail

Попробуйте реализовать на обеих платформах и сравните количество кода.

---

## Связи

- [[ios-navigation]] — Детальное руководство по навигации в iOS
- [[android-navigation]] — Полное руководство по Android Navigation Component
- [[swiftui-basics]] — Основы SwiftUI для понимания NavigationStack
- [[jetpack-compose-basics]] — Основы Compose для понимания NavHost
- [[kmp-architecture]] — Архитектура Kotlin Multiplatform приложений
- [[deep-linking-guide]] — Углублённое руководство по deep linking на обеих платформах
