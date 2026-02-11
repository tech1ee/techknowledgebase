---
title: "Android Navigation: Полный гайд по всем подходам"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [graph-traversal, stack-data-structure, state-machine, deep-linking]
tags:
  - topic/android
  - topic/navigation
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-navigation-evolution]]"
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-app-components]]"
  - "[[android-compose]]"
  - "[[android-bundle-parcelable]]"
  - "[[android-intent-internals]]"
---

# Android Navigation: Полный гайд по всем подходам

> **Эволюция навигации**: См. [[android-navigation-evolution]] для обзора всех подходов с 2008 по 2025 год и decision tree для выбора правильного подхода.

Navigation Component — официальная библиотека Google для навигации между экранами. Она решает проблемы ручного управления Fragment transactions, back stack, deep links и передачи данных между экранами.

> **Prerequisites:**
> - [[android-activity-lifecycle]] — lifecycle и back stack
> - [[android-compose]] или [[android-ui-views]] — понимание UI layer
> - Понимание что такое back stack

---

## Терминология

| Термин | Значение |
|--------|----------|
| **NavController** | Управляет навигацией (текущий экран, back stack) |
| **NavHost** | Контейнер для отображения destinations |
| **NavGraph** | Граф всех экранов и переходов между ними |
| **Destination** | Экран (Fragment, Composable, Activity) |
| **Action** | Переход между destinations |
| **Safe Args** | Type-safe передача аргументов |
| **Deep Link** | URL, открывающий конкретный экран |

---

## Почему Navigation Component, а не ручной FragmentManager?

### Проблема: ручное управление Fragment

```kotlin
// ❌ Ручная навигация — типичные проблемы
class MainActivity : AppCompatActivity() {

    fun navigateToDetail(itemId: Long) {
        // Проблема 1: Boilerplate на каждый переход
        val fragment = DetailFragment().apply {
            arguments = Bundle().apply {
                putLong("item_id", itemId)  // Строковый ключ — легко опечататься
            }
        }

        supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)
            .addToBackStack(null)  // Проблема 2: Как правильно именовать?
            .commit()

        // Проблема 3: commitAllowingStateLoss vs commit?
        // Проблема 4: Что если Activity уже destroyed?
    }

    fun navigateToSettings() {
        // Копипаста того же кода...
    }

    // Проблема 5: Deep links? Писать вручную парсинг URL
    // Проблема 6: Back stack — как реализовать "до главного экрана"?
    // Проблема 7: Conditional navigation (авторизован ли пользователь?)
}
```

### Что ломается без Navigation Component

| Проблема | Последствие |
|----------|-------------|
| **Back stack вручную** | Inconsistent behavior, crashes при повороте |
| **Arguments через Bundle** | Runtime crashes при опечатках в ключах |
| **Deep links вручную** | Много кода, легко забыть case |
| **Состояние при rotation** | Fragment пересоздаётся, нужно сохранять arguments |
| **Тестирование** | Сложно протестировать navigation flow |
| **Визуализация** | Нет общей картины "откуда куда можно перейти" |

### Как Navigation Component решает проблемы

```xml
<!-- nav_graph.xml — визуальное описание всех переходов -->
<navigation
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">

        <!-- Явно описанные переходы -->
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment">

        <!-- Type-safe аргументы -->
        <argument
            android:name="itemId"
            app:argType="long" />
    </fragment>

</navigation>
```

```kotlin
// ✅ Навигация с Navigation Component
class HomeFragment : Fragment() {

    fun navigateToDetail(itemId: Long) {
        // Safe Args — compile-time проверка
        val action = HomeFragmentDirections.actionHomeToDetail(itemId)
        findNavController().navigate(action)

        // Никаких:
        // - Bundle вручную
        // - FragmentManager transactions
        // - Строковых ключей
        // - Проблем с back stack
    }
}
```

---

## Настройка Navigation Component

### Dependencies

```kotlin
// build.gradle.kts (project)
plugins {
    id("androidx.navigation.safeargs.kotlin") version "2.7.6" apply false
}

// build.gradle.kts (app)
plugins {
    id("androidx.navigation.safeargs.kotlin")
}

dependencies {
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.6")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.6")
}
```

### Nav Graph

```xml
<!-- res/navigation/nav_graph.xml -->
<?xml version="1.0" encoding="utf-8"?>
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.ui.HomeFragment"
        android:label="Home">

        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment"
            app:enterAnim="@anim/slide_in_right"
            app:exitAnim="@anim/slide_out_left"
            app:popEnterAnim="@anim/slide_in_left"
            app:popExitAnim="@anim/slide_out_right" />

        <action
            android:id="@+id/action_home_to_settings"
            app:destination="@id/settingsFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.ui.DetailFragment"
        android:label="Detail">

        <argument
            android:name="itemId"
            app:argType="long" />

        <argument
            android:name="itemName"
            app:argType="string"
            android:defaultValue="" />

        <!-- Deep link -->
        <deepLink
            android:id="@+id/deepLink"
            app:uri="example://item/{itemId}" />
    </fragment>

    <fragment
        android:id="@+id/settingsFragment"
        android:name="com.example.ui.SettingsFragment"
        android:label="Settings" />

</navigation>
```

### Activity Setup

```xml
<!-- activity_main.xml -->
<androidx.fragment.app.FragmentContainerView
    android:id="@+id/nav_host_fragment"
    android:name="androidx.navigation.fragment.NavHostFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:defaultNavHost="true"
    app:navGraph="@navigation/nav_graph" />
```

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        // Setup ActionBar с Navigation
        setupActionBarWithNavController(navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}
```

---

## Safe Args: type-safe аргументы

### Проблема с Bundle

```kotlin
// ❌ Bundle — runtime ошибки
// Отправитель
val bundle = Bundle().apply {
    putLong("item_id", 42)  // Ключ "item_id"
}

// Получатель
val itemId = arguments?.getLong("itemId")  // Ключ "itemId" — ОПЕЧАТКА!
// itemId = 0 (default), не 42!
```

### Safe Args решение

```kotlin
// ✅ Safe Args — compile-time проверка

// Отправитель
val action = HomeFragmentDirections.actionHomeToDetail(
    itemId = 42,
    itemName = "My Item"
)
findNavController().navigate(action)

// Получатель
class DetailFragment : Fragment() {

    // Автоматически сгенерированный класс
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val itemId = args.itemId  // Long, не Long?
        val itemName = args.itemName  // String
    }
}
```

### Поддерживаемые типы аргументов

| Тип | argType | Пример |
|-----|---------|--------|
| Integer | `integer` | `app:argType="integer"` |
| Long | `long` | `app:argType="long"` |
| Float | `float` | `app:argType="float"` |
| Boolean | `boolean` | `app:argType="boolean"` |
| String | `string` | `app:argType="string"` |
| Enum | `com.example.MyEnum` | Full class name |
| Parcelable | `com.example.MyData` | Implements Parcelable |
| Serializable | `com.example.MyData` | Implements Serializable |

---

## Deep Links

### Implicit Deep Links

```xml
<!-- В nav_graph.xml -->
<fragment android:id="@+id/detailFragment">

    <deepLink
        app:uri="https://example.com/item/{itemId}"
        app:action="android.intent.action.VIEW"
        app:mimeType="*/*" />

    <deepLink app:uri="example://item/{itemId}" />

</fragment>
```

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".MainActivity">
    <nav-graph android:value="@navigation/nav_graph" />
</activity>
```

```kotlin
// Открытие deep link
val uri = Uri.parse("example://item/42")
findNavController().navigate(uri)

// Или Intent извне приложения
// adb shell am start -a android.intent.action.VIEW -d "example://item/42"
```

### Explicit Deep Links (PendingIntent)

```kotlin
// Создание PendingIntent для уведомления
val deepLinkIntent = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.detailFragment)
    .setArguments(bundleOf("itemId" to 42L))
    .createPendingIntent()

// Использование в Notification
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("New item")
    .setContentIntent(deepLinkIntent)
    .build()
```

---

## Navigation в Compose

### Setup

```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.navigation:navigation-compose:2.7.6")
}
```

### Базовая навигация

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onItemClick = { itemId ->
                    navController.navigate("detail/$itemId")
                }
            )
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.LongType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getLong("itemId") ?: 0
            DetailScreen(itemId = itemId)
        }

        composable("settings") {
            SettingsScreen()
        }
    }
}
```

### Type-safe navigation в Compose (2.8+)

```kotlin
// Определение routes как sealed class
@Serializable
sealed class Screen {
    @Serializable
    data object Home : Screen()

    @Serializable
    data class Detail(val itemId: Long) : Screen()

    @Serializable
    data object Settings : Screen()
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.Home
    ) {
        composable<Screen.Home> {
            HomeScreen(
                onItemClick = { itemId ->
                    navController.navigate(Screen.Detail(itemId))
                }
            )
        }

        composable<Screen.Detail> { backStackEntry ->
            val detail: Screen.Detail = backStackEntry.toRoute()
            DetailScreen(itemId = detail.itemId)
        }
    }
}
```

---

## Compose Navigation Advanced (2024-2025)

### Navigation 3 (Google I/O 2025, Alpha)

**Революционный подход** — полностью декларативное управление back stack:

```kotlin
// Dependencies
implementation("androidx.navigation3:navigation3:1.0.0-alpha01")

// Back stack как SnapshotStateList — полный контроль
@Composable
fun App() {
    var backStack by rememberSaveable {
        mutableStateOf(listOf<Route>(Route.Home))
    }

    NavDisplay(
        backStack = backStack,
        onBack = { backStack = backStack.dropLast(1) }
    ) { route ->
        when (route) {
            Route.Home -> HomeScreen(
                onNavigateToProfile = { userId ->
                    backStack = backStack + Route.Profile(userId)
                }
            )
            is Route.Profile -> ProfileScreen(
                userId = route.userId,
                onBack = { backStack = backStack.dropLast(1) }
            )
        }
    }
}

@Serializable
sealed class Route {
    @Serializable
    data object Home : Route()

    @Serializable
    data class Profile(val userId: String) : Route()
}
```

**Scenes API** — адаптивные layouts (phone ↔ tablet):

```kotlin
@Composable
fun AdaptiveApp() {
    val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass

    NavDisplay(backStack = backStack) { route ->
        if (windowSizeClass.windowWidthSizeClass == WindowWidthSizeClass.EXPANDED) {
            // Tablet: List-Detail layout
            Scene(
                key = SceneKey.ListDetail,
                content = { ListDetailLayout(route) }
            )
        } else {
            // Phone: Single pane
            Scene(
                key = SceneKey.SinglePane,
                content = { SinglePaneContent(route) }
            )
        }
    }
}
```

**Почему Navigation 3:**
- Back stack как **first-class state** — полный контроль
- **Kotlin Multiplatform** support из коробки
- **Declarative** — нет imperative NavController calls
- **Scenes API** — адаптивные UI паттерны built-in

### Nested Navigation Graphs

```kotlin
@Serializable
sealed class AppRoutes {
    @Serializable data object Home : AppRoutes()
    @Serializable data object Auth : AppRoutes()
    @Serializable data object Settings : AppRoutes()
}

@Serializable
sealed class AuthRoutes {
    @Serializable data object Login : AuthRoutes()
    @Serializable data object Register : AuthRoutes()
    @Serializable data object ForgotPassword : AuthRoutes()
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = AppRoutes.Home) {
        composable<AppRoutes.Home> { HomeScreen() }

        // Nested graph для Auth
        navigation<AppRoutes.Auth>(startDestination = AuthRoutes.Login) {
            composable<AuthRoutes.Login> {
                LoginScreen(
                    onRegister = { navController.navigate(AuthRoutes.Register) },
                    onForgotPassword = { navController.navigate(AuthRoutes.ForgotPassword) },
                    onLoginSuccess = {
                        navController.navigate(AppRoutes.Home) {
                            popUpTo(AppRoutes.Auth) { inclusive = true }
                        }
                    }
                )
            }
            composable<AuthRoutes.Register> { RegisterScreen() }
            composable<AuthRoutes.ForgotPassword> { ForgotPasswordScreen() }
        }

        composable<AppRoutes.Settings> { SettingsScreen() }
    }
}
```

### Multi-Module Navigation

**Approach 1: Shared Routes Module**

```
:app
  └── depends on :feature:home, :feature:profile, :navigation
:feature:home
  └── depends on :navigation
:feature:profile
  └── depends on :navigation
:navigation (shared)
  └── Contains all Routes sealed classes
```

```kotlin
// :navigation module
@Serializable
sealed class Routes {
    @Serializable data object Home : Routes()
    @Serializable data class Profile(val id: String) : Routes()
}

// :feature:home module
fun NavGraphBuilder.homeGraph(navController: NavController) {
    composable<Routes.Home> {
        HomeScreen(
            onProfileClick = { navController.navigate(Routes.Profile(it)) }
        )
    }
}

// :app module
NavHost(navController, startDestination = Routes.Home) {
    homeGraph(navController)
    profileGraph(navController)
}
```

**Approach 2: Interface-based (looser coupling)**

```kotlin
// :navigation-api module
interface Navigator {
    fun navigateToProfile(userId: String)
    fun navigateToHome()
    fun navigateBack()
}

// :app module implements Navigator
class AppNavigator(
    private val navController: NavController
) : Navigator {
    override fun navigateToProfile(userId: String) {
        navController.navigate(Routes.Profile(userId))
    }
    // ...
}
```

### Bottom Sheet Navigation

**Material 3 с navigation-compose:**

```kotlin
// Dependencies
implementation("androidx.compose.material3:material3:1.2.0")

// Bottom Sheet как destination
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppWithBottomSheet() {
    val sheetState = rememberModalBottomSheetState()
    var showBottomSheet by remember { mutableStateOf(false) }

    Scaffold { paddingValues ->
        MainContent(
            modifier = Modifier.padding(paddingValues),
            onShowSheet = { showBottomSheet = true }
        )

        if (showBottomSheet) {
            ModalBottomSheet(
                onDismissRequest = { showBottomSheet = false },
                sheetState = sheetState
            ) {
                BottomSheetContent(
                    onDismiss = { showBottomSheet = false }
                )
            }
        }
    }
}
```

**Для production:** Используй [eygraber/compose-material3-navigation](https://github.com/eygraber/compose-material3-navigation) для bottom sheet как navigation destinations.

### Shared Element Transitions (Compose 1.7+)

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementNavigation() {
    SharedTransitionLayout {
        val navController = rememberNavController()

        NavHost(navController, startDestination = "list") {
            composable("list") {
                ListScreen(
                    onItemClick = { item ->
                        navController.navigate("detail/${item.id}")
                    },
                    animatedVisibilityScope = this
                )
            }

            composable("detail/{id}") { backStackEntry ->
                val id = backStackEntry.arguments?.getString("id")
                DetailScreen(
                    itemId = id,
                    animatedVisibilityScope = this
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedTransitionScope.ListScreen(
    onItemClick: (Item) -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    LazyColumn {
        items(items) { item ->
            Row(
                modifier = Modifier
                    .clickable { onItemClick(item) }
                    .sharedElement(
                        state = rememberSharedContentState(key = "image-${item.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
            ) {
                AsyncImage(
                    model = item.imageUrl,
                    modifier = Modifier
                        .size(80.dp)
                        .sharedElement(
                            state = rememberSharedContentState(key = "image-${item.id}"),
                            animatedVisibilityScope = animatedVisibilityScope
                        )
                )
                Text(
                    text = item.title,
                    modifier = Modifier.sharedBounds(
                        sharedContentState = rememberSharedContentState(key = "title-${item.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                )
            }
        }
    }
}
```

**Ключевые модификаторы:**
- `Modifier.sharedElement()` — элемент перемещается между экранами
- `Modifier.sharedBounds()` — bounds морфируются, контент fade in/out

### Navigation Animations

```kotlin
NavHost(
    navController = navController,
    startDestination = Routes.Home,
    enterTransition = {
        slideIntoContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Left,
            animationSpec = tween(300)
        )
    },
    exitTransition = {
        slideOutOfContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Left,
            animationSpec = tween(300)
        )
    },
    popEnterTransition = {
        slideIntoContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Right,
            animationSpec = tween(300)
        )
    },
    popExitTransition = {
        slideOutOfContainer(
            towards = AnimatedContentTransitionScope.SlideDirection.Right,
            animationSpec = tween(300)
        )
    }
) {
    // destinations
}

// Per-destination animations
composable<Routes.Detail>(
    enterTransition = { fadeIn(animationSpec = tween(500)) },
    exitTransition = { fadeOut(animationSpec = tween(500)) }
) {
    DetailScreen()
}
```

### ViewModel Scoping

```kotlin
// Dependencies
implementation("androidx.hilt:hilt-navigation-compose:1.2.0")

// ViewModel scoped to destination
@Composable
fun ProfileScreen() {
    val viewModel: ProfileViewModel = hiltViewModel()
    // ViewModel живёт пока destination в back stack
}

// ViewModel scoped to nav graph
@Composable
fun FeatureNavHost() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "feature") {
        navigation(
            startDestination = "step1",
            route = "feature"
        ) {
            composable("step1") {
                // ViewModel shared across feature graph
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("feature")
                }
                val sharedViewModel: FeatureViewModel = hiltViewModel(parentEntry)
                Step1Screen(sharedViewModel)
            }

            composable("step2") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("feature")
                }
                val sharedViewModel: FeatureViewModel = hiltViewModel(parentEntry)
                Step2Screen(sharedViewModel)
            }
        }
    }
}
```

### Testing Compose Navigation

```kotlin
@HiltAndroidTest
class NavigationTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createComposeRule()

    private lateinit var navController: TestNavHostController

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun navigateToProfile_showsProfileScreen() {
        composeTestRule.setContent {
            navController = TestNavHostController(LocalContext.current)
            navController.navigatorProvider.addNavigator(ComposeNavigator())

            AppNavigation(navController = navController)
        }

        // Click on profile button
        composeTestRule
            .onNodeWithContentDescription("Profile")
            .performClick()

        // Assert navigation happened
        val route = navController.currentBackStackEntry?.destination?.route
        assertEquals("profile/{userId}", route)
    }

    @Test
    fun backPress_returnsToHome() {
        composeTestRule.setContent {
            navController = TestNavHostController(LocalContext.current)
            navController.navigatorProvider.addNavigator(ComposeNavigator())

            AppNavigation(navController = navController)
        }

        // Navigate to profile
        composeTestRule.runOnUiThread {
            navController.navigate(Routes.Profile("123"))
        }

        // Press back
        Espresso.pressBack()

        // Assert we're back at home
        assertEquals(Routes.Home::class.qualifiedName,
            navController.currentBackStackEntry?.destination?.route)
    }
}
```

---

## Распространённые паттерны

### Условная навигация (Auth)

```kotlin
// В nav_graph.xml — два отдельных графа
<navigation>
    <navigation
        android:id="@+id/auth_graph"
        app:startDestination="@id/loginFragment">
        <fragment android:id="@+id/loginFragment" />
        <fragment android:id="@+id/registerFragment" />
    </navigation>

    <navigation
        android:id="@+id/main_graph"
        app:startDestination="@id/homeFragment">
        <fragment android:id="@+id/homeFragment" />
    </navigation>
</navigation>
```

```kotlin
// При старте проверяем авторизацию
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)

        if (!authManager.isLoggedIn) {
            navController.navigate(R.id.auth_graph)
        }
    }
}
```

### Navigate с очисткой back stack

```kotlin
// Переход на Home и очистка всего стека
navController.navigate(R.id.homeFragment) {
    popUpTo(R.id.nav_graph) {
        inclusive = true
    }
}

// Logout — очистить всё и на Login
navController.navigate(R.id.loginFragment) {
    popUpTo(R.id.nav_graph) {
        inclusive = true
    }
    launchSingleTop = true
}
```

### Bottom Navigation

```kotlin
// Setup с NavigationUI
val navController = findNavController(R.id.nav_host_fragment)
binding.bottomNavigation.setupWithNavController(navController)

// При переключении табов — не добавлять в back stack
binding.bottomNavigation.setOnItemSelectedListener { item ->
    NavigationUI.onNavDestinationSelected(item, navController)
    true
}
```

### Multiple Back Stacks (Navigation 2.4+)

**Проблема:** При переключении табов теряется state каждого таба.

**Решение:** `saveState` и `restoreState` в Navigation 2.4+:

```kotlin
// Автоматическое сохранение при использовании setupWithNavController
binding.bottomNavigation.setupWithNavController(navController)

// Или вручную
binding.bottomNavigation.setOnItemSelectedListener { item ->
    navController.navigate(item.itemId) {
        // Pop до start destination, но сохрани state
        popUpTo(navController.graph.findStartDestination().id) {
            saveState = true
        }
        // Не создавай multiple copies
        launchSingleTop = true
        // Восстанови state если есть
        restoreState = true
    }
    true
}
```

**Как это работает:**
```
Tab A: Home → Profile → Settings (user navigates)
       ↓
User switches to Tab B
       ↓
Tab A back stack SAVED: [Home, Profile, Settings]
Tab B back stack RESTORED (or created fresh)
       ↓
User returns to Tab A
       ↓
Tab A back stack RESTORED: [Home, Profile, Settings]
```

### Safe Args с Parcelable

```kotlin
// Data class с @Parcelize
@Parcelize
data class User(
    val id: String,
    val name: String,
    val email: String
) : Parcelable

// В nav_graph.xml
<fragment android:id="@+id/profileFragment">
    <argument
        android:name="user"
        app:argType="com.example.model.User" />
</fragment>

// Отправка
val user = User("123", "John", "john@example.com")
val action = HomeFragmentDirections.actionHomeToProfile(user = user)
findNavController().navigate(action)

// Получение
class ProfileFragment : Fragment() {
    private val args: ProfileFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val user = args.user  // Type-safe User object
        binding.nameText.text = user.name
    }
}
```

### Testing Navigation Component

```kotlin
@RunWith(AndroidJUnit4::class)
class NavigationTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testNavigationToDetail() {
        // Получить NavController
        val navController = activityRule.scenario.onActivity { activity ->
            activity.findNavController(R.id.nav_host_fragment)
        }

        // Trigger navigation
        onView(withId(R.id.item_list))
            .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(0, click()))

        // Assert destination
        assertEquals(R.id.detailFragment, navController.currentDestination?.id)
    }

    @Test
    fun testBackNavigation() {
        // Navigate forward
        onView(withId(R.id.goToDetailButton)).perform(click())

        // Press back
        pressBack()

        // Assert we're back at home
        activityRule.scenario.onActivity { activity ->
            val navController = activity.findNavController(R.id.nav_host_fragment)
            assertEquals(R.id.homeFragment, navController.currentDestination?.id)
        }
    }
}
```

**TestNavHostController для unit tests:**
```kotlin
@Test
fun testNavigationWithTestController() {
    val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

    launchFragmentInContainer<HomeFragment>().onFragment { fragment ->
        Navigation.setViewNavController(fragment.requireView(), navController)
    }

    // Set the graph
    navController.setGraph(R.navigation.nav_graph)

    // Navigate
    navController.navigate(R.id.action_home_to_detail)

    // Assert
    assertEquals(R.id.detailFragment, navController.currentDestination?.id)
}
```

---

## Fragment Transactions Deep Dive

> **Контекст:** Этот раздел для понимания legacy кода и работы Navigation Component под капотом. Для новых проектов используй Navigation Component или Compose Navigation.

### FragmentManager Internals

**Back Stack = Transactions, не Fragments:**

```kotlin
// ВАЖНО: Back stack содержит FragmentTransaction, не Fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
    .addToBackStack("profile")  // Эта TRANSACTION добавлена в back stack
    .commit()

// popBackStack() отменяет transaction, не убирает fragment напрямую
supportFragmentManager.popBackStack()
```

**Визуализация:**
```
Back Stack (transactions):
┌─────────────────────────────┐
│ Transaction 3: add Settings │  ← Top (current)
├─────────────────────────────┤
│ Transaction 2: replace Prof │
├─────────────────────────────┤
│ Transaction 1: add Home     │
└─────────────────────────────┘

Fragment Manager View:
[HomeFragment, ProfileFragment, SettingsFragment]
                                        ↑ visible
```

### Transaction Operations

| Operation | Behavior | Fragment State |
|-----------|----------|----------------|
| `add()` | Добавляет fragment в container | Created → Resumed |
| `remove()` | Убирает fragment из container | Stopped → Destroyed |
| `replace()` | = remove() all + add() new | Old destroyed, new created |
| `hide()` | Делает невидимым (View.GONE) | Stays Resumed |
| `show()` | Делает видимым | Stays Resumed |
| `attach()` | Recreates view (after detach) | Stopped → Resumed |
| `detach()` | Destroys view, keeps instance | Resumed → Stopped |

**Когда что использовать:**

```kotlin
// replace() — стандартная навигация (предыдущий fragment уничтожается)
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .addToBackStack(null)
    .commit()

// add() + hide()/show() — сохранить state (ViewPager style)
// Для bottom navigation где нужно сохранить scroll position
supportFragmentManager.beginTransaction()
    .hide(currentFragment)
    .show(targetFragment)
    .commit()

// detach()/attach() — освободить память, но сохранить instance
// Fragment state сохраняется, но view пересоздаётся
supportFragmentManager.beginTransaction()
    .detach(fragment)
    .commit()
```

### Commit Variants

| Method | Async | Back Stack | When to Use |
|--------|-------|------------|-------------|
| `commit()` | Yes (scheduled) | Yes | Default choice |
| `commitNow()` | No (immediate) | **NO** | Когда нужен результат сразу |
| `commitAllowingStateLoss()` | Yes | Yes | После onSaveInstanceState |
| `commitNowAllowingStateLoss()` | No | **NO** | Immediate + after state saved |

**Подробнее:**

```kotlin
// commit() — async, будет выполнен в следующем main loop pass
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    .addToBackStack(null)
    .commit()
// fragment ещё НЕ добавлен здесь!

// commitNow() — синхронный, но НЕ МОЖЕТ использовать addToBackStack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    // .addToBackStack(null)  // ← НЕЛЬЗЯ с commitNow!
    .commitNow()
// fragment УЖЕ добавлен здесь

// После onSaveInstanceState() commit() выбросит exception
// commitAllowingStateLoss() — принимает риск потери state
override fun onStop() {
    super.onStop()
    // После onSaveInstanceState
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, fragment)
        .commitAllowingStateLoss()  // Может потерять state при process death
}
```

**executePendingTransactions():**
```kotlin
// Принудительно выполнить все pending commits
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    .commit()

supportFragmentManager.executePendingTransactions()
// Теперь fragment точно добавлен
```

### Fragment Lifecycle During Navigation

```
Fragment A visible, start navigation to Fragment B:
─────────────────────────────────────────────────────
A.onPause()
    B.onAttach()
    B.onCreate()
    B.onCreateView()
    B.onViewCreated()
    B.onStart()
    B.onResume()      ← B visible
A.onStop()
─────────────────────────────────────────────────────

User presses Back (B returns to A):
─────────────────────────────────────────────────────
B.onPause()
    A.onStart()
    A.onResume()      ← A visible
B.onStop()
B.onDestroyView()
B.onDestroy()
B.onDetach()          ← B destroyed (если replace)
─────────────────────────────────────────────────────
```

### Fragment Result API

**Замена deprecated `setTargetFragment()`:**

```kotlin
// Fragment A: Устанавливает listener для результата
class FragmentA : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Слушать результат от child fragments
        childFragmentManager.setFragmentResultListener(
            "requestKey",
            this
        ) { requestKey, bundle ->
            val result = bundle.getString("resultKey")
            // Handle result
        }

        // ИЛИ слушать результат от sibling fragments
        parentFragmentManager.setFragmentResultListener(
            "requestKey",
            this
        ) { requestKey, bundle ->
            val result = bundle.getString("resultKey")
        }
    }
}

// Fragment B: Отправляет результат
class FragmentB : Fragment() {
    private fun sendResult() {
        val result = "some data"

        // Отправить результату parent
        parentFragmentManager.setFragmentResult(
            "requestKey",
            bundleOf("resultKey" to result)
        )

        // Вернуться назад
        parentFragmentManager.popBackStack()
    }
}
```

### Nested Fragments: childFragmentManager vs parentFragmentManager

```kotlin
// КРИТИЧЕСКИ ВАЖНО понимать разницу!

class ParentFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // childFragmentManager — для fragments ВНУТРИ этого fragment
        // Их back stack независим от parent
        childFragmentManager.beginTransaction()
            .replace(R.id.childContainer, ChildFragment())
            .addToBackStack(null)
            .commit()
    }
}

class ChildFragment : Fragment() {

    fun navigateToSibling() {
        // parentFragmentManager — FragmentManager родителя
        // Это childFragmentManager ParentFragment
        parentFragmentManager.beginTransaction()
            .replace(R.id.childContainer, SiblingFragment())
            .addToBackStack(null)
            .commit()
    }

    fun navigateOutsideParent() {
        // Чтобы повлиять на navigation уровнем выше
        // Нужен FragmentManager Activity
        requireActivity().supportFragmentManager.beginTransaction()
            .replace(R.id.activityContainer, OtherFragment())
            .addToBackStack(null)
            .commit()
    }
}
```

**Визуализация иерархии:**
```
Activity
├── supportFragmentManager
│   └── ParentFragment (R.id.activityContainer)
│       ├── childFragmentManager
│       │   └── ChildFragment (R.id.childContainer)
│       │       └── parentFragmentManager → childFragmentManager of ParentFragment
│       │   └── SiblingFragment
│       │       └── parentFragmentManager → childFragmentManager of ParentFragment
```

### Shared Element Transitions (Fragments)

```kotlin
// Fragment A — источник
class ListFragment : Fragment() {

    fun navigateToDetail(imageView: ImageView, item: Item) {
        val detailFragment = DetailFragment.newInstance(item.id)

        parentFragmentManager.beginTransaction()
            // Shared element
            .addSharedElement(imageView, "hero_image")
            // Transition animations
            .setReorderingAllowed(true)
            .replace(R.id.container, detailFragment)
            .addToBackStack(null)
            .commit()
    }
}

// Fragment A layout
<ImageView
    android:id="@+id/itemImage"
    android:transitionName="item_image_${item.id}" />

// Fragment B — destination
class DetailFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Задержать transition пока не загрузится image
        postponeEnterTransition()

        sharedElementEnterTransition = TransitionInflater.from(requireContext())
            .inflateTransition(R.transition.shared_image)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Установить transition name
        binding.heroImage.transitionName = "hero_image"

        // Загрузить image и запустить transition
        Glide.with(this)
            .load(imageUrl)
            .listener(object : RequestListener<Drawable> {
                override fun onResourceReady(...): Boolean {
                    startPostponedEnterTransition()
                    return false
                }
            })
            .into(binding.heroImage)
    }
}
```

### Common Fragment Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| `commit()` after `onSaveInstanceState()` | `IllegalStateException` | Use `commitAllowingStateLoss()` or check `isStateSaved` |
| Using Activity context in Fragment | Memory leak | Use `viewLifecycleOwner` for observers |
| `findFragmentById` returns null | Transaction not executed | Call `executePendingTransactions()` first |
| ViewPager fragments lose state | Wrong adapter | Use `FragmentStateAdapter` (not deprecated `FragmentPagerAdapter`) |
| Back doesn't work in nested fragments | Wrong FragmentManager | Handle back in parent or use `childFragmentManager.popBackStack()` |
| Fragment not attached exception | Using `requireContext()` after detach | Check `isAdded` or use `context?.let {}` |

---

## Activity-based Navigation

> **Контекст:** Базовый подход Android с 2008 года. Нужен для: legacy кода, системной интеграции (Camera, Share), cross-app navigation.

### Intent Types

**Explicit Intent — когда знаем exact destination:**
```kotlin
// Внутри своего приложения
val intent = Intent(this, ProfileActivity::class.java).apply {
    putExtra("USER_ID", userId)
    putExtra("USER_NAME", userName)
}
startActivity(intent)
```

**Implicit Intent — когда описываем action:**
```kotlin
// Открыть URL в браузере
val intent = Intent(Intent.ACTION_VIEW).apply {
    data = Uri.parse("https://example.com")
}
startActivity(intent)

// Отправить email
val intent = Intent(Intent.ACTION_SENDTO).apply {
    data = Uri.parse("mailto:")
    putExtra(Intent.EXTRA_EMAIL, arrayOf("support@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Support Request")
}
startActivity(intent)

// Поделиться текстом
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Check this out!")
}
startActivity(Intent.createChooser(intent, "Share via"))
```

### Intent Flags

| Flag | Effect | Use Case |
|------|--------|----------|
| `FLAG_ACTIVITY_NEW_TASK` | Start in new task | From Service/BroadcastReceiver |
| `FLAG_ACTIVITY_CLEAR_TOP` | Clear activities above target | Return to existing activity |
| `FLAG_ACTIVITY_SINGLE_TOP` | Reuse if at top of stack | Avoid duplicates |
| `FLAG_ACTIVITY_CLEAR_TASK` | Clear entire task | Logout flow |
| `FLAG_ACTIVITY_NO_HISTORY` | Don't add to back stack | Splash, intermediate screens |

**Примеры комбинаций:**

```kotlin
// После logout — полная очистка и на Login
val intent = Intent(this, LoginActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
}
startActivity(intent)
finish()

// Notification tap — вернуться к существующему экрану или создать
val intent = Intent(this, ChatActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
}

// Из Service — обязательно NEW_TASK
val intent = Intent(context, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
}
context.startActivity(intent)
```

### Launch Modes

**Объявляются в Manifest:**
```xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop" />
```

| Mode | Instances | Task | onNewIntent |
|------|-----------|------|-------------|
| **standard** | Multiple | Same as caller | No |
| **singleTop** | 1 at top | Same as caller | Yes (if at top) |
| **singleTask** | 1 system-wide | Own/affinity | Yes |
| **singleInstance** | 1 system-wide | Exclusive task | Yes |
| **singleInstancePerTask** | 1 per task | Root of task | Yes |

**Когда использовать:**
- **standard** — большинство activities (default)
- **singleTop** — notification handlers (избежать дубликатов)
- **singleTask** — main entry point (Home, Inbox)
- **singleInstance** — video call, system dialogs (очень редко!)

**onNewIntent handling:**
```kotlin
class ProfileActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
    }

    // Вызывается вместо onCreate если activity reused (singleTop/singleTask)
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        // ВАЖНО: обновить intent чтобы getIntent() возвращал новый
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        val userId = intent.getStringExtra("USER_ID")
        loadProfile(userId)
    }
}
```

### Activity Result API

**Замена deprecated `startActivityForResult()`:**

```kotlin
class MainActivity : AppCompatActivity() {

    // Регистрация callback — MUST be done before onCreate/onStart
    private val getContent = registerForActivityResult(GetContent()) { uri: Uri? ->
        // Handle returned URI
        uri?.let { processImage(it) }
    }

    private val takePicture = registerForActivityResult(TakePicturePreview()) { bitmap: Bitmap? ->
        bitmap?.let { displayImage(it) }
    }

    private val requestPermission = registerForActivityResult(RequestPermission()) { granted ->
        if (granted) {
            // Permission granted
        } else {
            // Permission denied
        }
    }

    // Custom contract для своих activities
    private val editProfile = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("updated_name")
            // Handle result
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Launch when needed
        binding.selectImageButton.setOnClickListener {
            getContent.launch("image/*")
        }

        binding.takePictureButton.setOnClickListener {
            takePicture.launch(null)
        }

        binding.editProfileButton.setOnClickListener {
            val intent = Intent(this, EditProfileActivity::class.java)
            editProfile.launch(intent)
        }
    }
}

// В EditProfileActivity — отправить результат
class EditProfileActivity : AppCompatActivity() {

    private fun saveAndReturn() {
        val resultIntent = Intent().apply {
            putExtra("updated_name", newName)
        }
        setResult(RESULT_OK, resultIntent)
        finish()
    }
}
```

**Custom Contract:**
```kotlin
class PickRingtone : ActivityResultContract<Int, Uri?>() {

    override fun createIntent(context: Context, ringtoneType: Int): Intent {
        return Intent(RingtoneManager.ACTION_RINGTONE_PICKER).apply {
            putExtra(RingtoneManager.EXTRA_RINGTONE_TYPE, ringtoneType)
        }
    }

    override fun parseResult(resultCode: Int, intent: Intent?): Uri? {
        if (resultCode != Activity.RESULT_OK) return null
        return intent?.getParcelableExtra(RingtoneManager.EXTRA_RINGTONE_PICKED_URI)
    }
}

// Usage
private val pickRingtone = registerForActivityResult(PickRingtone()) { uri ->
    uri?.let { setRingtone(it) }
}

pickRingtone.launch(RingtoneManager.TYPE_NOTIFICATION)
```

### Passing Data Between Activities

**Primitives:**
```kotlin
// Send
intent.putExtra("USER_ID", 123)
intent.putExtra("NAME", "John")

// Receive
val userId = intent.getIntExtra("USER_ID", -1)
val name = intent.getStringExtra("NAME")
```

**Parcelable с @Parcelize:**
```kotlin
// build.gradle.kts
plugins {
    id("kotlin-parcelize")
}

// Data class
@Parcelize
data class User(
    val id: String,
    val name: String,
    val email: String
) : Parcelable

// Send
intent.putExtra("USER", user)

// Receive
val user = intent.getParcelableExtra<User>("USER")
// API 33+
val user = intent.getParcelableExtra("USER", User::class.java)
```

**ВАЖНО:** Не передавай большие объекты через Intent! Limit ~500KB.

### Activity Transitions

```kotlin
// Простая анимация
startActivity(intent)
overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)

// При закрытии
finish()
overridePendingTransition(R.anim.slide_in_left, R.anim.slide_out_right)

// Shared Element Transition
val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
    this,
    imageView,
    "hero_image"  // transitionName в обоих layouts
)
startActivity(intent, options.toBundle())

// Multiple shared elements
val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
    this,
    androidx.core.util.Pair(imageView, "hero_image"),
    androidx.core.util.Pair(titleView, "hero_title")
)
```

### PendingIntent (Android 12+ Requirements)

```kotlin
// Android 12+ REQUIRES FLAG_IMMUTABLE or FLAG_MUTABLE

// Для notifications — обычно IMMUTABLE
val pendingIntent = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)

// Для inline replies, bubbles — MUTABLE
val mutablePendingIntent = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)
```

### Process Death and State

```kotlin
class MyActivity : AppCompatActivity() {

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("search_query", searchQuery)
        outState.putInt("scroll_position", scrollPosition)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        savedInstanceState?.let { state ->
            searchQuery = state.getString("search_query", "")
            scrollPosition = state.getInt("scroll_position", 0)
        }
    }
}

// Или с SavedStateHandle в ViewModel
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    var searchQuery: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }
}
```

---

## Когда какой подход к навигации

### Navigation Component (рекомендуется)

**Используй когда:**
- Single Activity архитектура с Fragments
- Нужна type-safe передача данных (Safe Args)
- Требуются Deep Links
- Важна визуализация navigation flow (Navigation Editor)
- Проект среднего и большого размера
- Нужна интеграция с BottomNavigationView, Drawer, Toolbar

**Преимущества:**
- Автоматическое управление back stack
- Safe Args для compile-time проверки аргументов
- Встроенная поддержка анимаций
- Визуальный редактор nav_graph.xml
- Простая настройка Deep Links

**Недостатки:**
- Дополнительная зависимость
- XML конфигурация (может быть избыточной для простых приложений)
- Learning curve для новичков

---

### Manual Fragment Transactions

**Используй когда:**
- Очень простое приложение (2-3 экрана)
- Динамическая навигация, которую сложно описать в graph
- Нужен полный контроль над Fragment lifecycle
- Legacy проект без рефакторинга

**Преимущества:**
- Полный контроль над transitions
- Нет дополнительных зависимостей
- Гибкость в сложных сценариях

**Недостатки:**
- Много boilerplate кода
- Легко допустить ошибки в back stack
- Нет type-safety при передаче данных
- Сложно тестировать navigation flow
- Deep Links нужно реализовывать вручную

---

### Multiple Activities

**Используй когда:**
- Логически независимые flow (авторизация, основное приложение, settings)
- Нужен отдельный lifecycle для разных частей приложения
- Переход из одного приложения в другое (через Intent)
- Legacy код с Activity-based архитектурой

**Преимущества:**
- Чёткое разделение ответственности
- Независимые lifecycle
- Простая интеграция с system (Share, Camera Intent)

**Недостатки:**
- Медленнее чем Fragment transitions
- Больше памяти (каждая Activity — отдельный контекст)
- Сложнее передавать данные между Activity
- Нет единого back stack

---

### Compose Navigation

**Используй когда:**
- Проект полностью на Jetpack Compose
- Нужна type-safe навигация через sealed class/data class
- Динамическая навигация с условиями
- Современный проект без View-based UI

**Преимущества:**
- Type-safe navigation через Kotlin Serialization (Navigation 2.8+)
- Нет XML конфигурации
- Reactive navigation (state-driven)
- Проще интеграция с ViewModel и State

**Недостатки:**
- Нет визуального редактора
- Требует понимания Compose
- Debugging сложнее чем с Navigation Component

---

## Чеклист

```
□ Navigation Graph описывает все экраны и переходы
□ Safe Args для type-safe аргументов
□ Deep links настроены для нужных экранов
□ Single Activity архитектура (где возможно)
□ setupWithNavController для BottomNav/Toolbar
□ Обработка onSupportNavigateUp для back button
□ Conditional navigation для auth flow
□ Анимации переходов для UX
```

---

## Проверь себя

### 1. Что такое NavGraph и Safe Args?

**NavGraph** — это XML файл (или Kotlin DSL в Compose), который описывает все destinations (экраны) в приложении и возможные переходы между ними. Он является центральным местом для визуализации navigation flow.

**Safe Args** — это плагин для Gradle, который генерирует type-safe классы для передачи аргументов между destinations. Вместо Bundle с строковыми ключами, где легко допустить опечатку, Safe Args генерирует классы Directions и Args с compile-time проверкой типов.

Пример:
```kotlin
// Без Safe Args
val bundle = Bundle().apply { putLong("itemId", 42) }

// С Safe Args
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 42)
findNavController().navigate(action)
```

---

### 2. Как передавать данные между destinations?

**Способ 1: Через аргументы (рекомендуется)**
```kotlin
// В nav_graph.xml
<argument
    android:name="itemId"
    app:argType="long" />

// Отправка
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 42)
findNavController().navigate(action)

// Получение
private val args: DetailFragmentArgs by navArgs()
val itemId = args.itemId
```

**Способ 2: Через ViewModel (для shared state)**
```kotlin
// Shared ViewModel между Fragments
class SharedViewModel : ViewModel() {
    val selectedItem = MutableLiveData<Item>()
}

// В обоих Fragments
private val sharedViewModel: SharedViewModel by activityViewModels()
```

**Способ 3: Через Navigation Back Stack Entry**
```kotlin
// Для возврата результата с предыдущего экрана
navController.previousBackStackEntry
    ?.savedStateHandle
    ?.set("result", myData)
```

**Что использовать:**
- Аргументы — для передачи данных вперёд (ID, примитивы, Parcelable)
- ViewModel — для shared state между destinations
- SavedStateHandle — для возврата результата назад

---

### 3. Чем Deep Link отличается от Explicit navigation?

**Explicit navigation** — программная навигация внутри приложения через NavController:
```kotlin
findNavController().navigate(R.id.detailFragment)
```
- Используется для обычных переходов внутри приложения
- Требует запущенный NavController
- Не работает извне приложения

**Deep Link** — навигация через URI, которая может быть вызвана извне:
```kotlin
// Implicit Deep Link (из браузера, другого приложения)
<deepLink app:uri="https://example.com/item/{itemId}" />

// Explicit Deep Link (из Notification, Widget)
val deepLinkIntent = NavDeepLinkBuilder(context)
    .setDestination(R.id.detailFragment)
    .setArguments(bundleOf("itemId" to 42L))
    .createPendingIntent()
```

**Ключевые отличия:**
- Deep Link работает даже когда приложение не запущено
- Deep Link может открываться из браузера, notifications, других приложений
- Explicit navigation работает только внутри запущенного приложения
- Deep Link требует настройки в AndroidManifest.xml

---

### 4. Когда Single Activity лучше Multiple Activities?

**Single Activity лучше когда:**
- Все экраны логически связаны (один flow)
- Нужны smooth transitions между экранами
- Важен shared state через ViewModel
- Используется Bottom Navigation или Drawer
- Проект на Jetpack Compose

**Преимущества Single Activity:**
```kotlin
// Быстрые transitions
findNavController().navigate(R.id.detailFragment)

// Shared ViewModel работает out-of-the-box
private val sharedViewModel: SharedViewModel by activityViewModels()

// Единый back stack
navController.popBackStack()
```

**Multiple Activities лучше когда:**
- Логически независимые модули (Auth flow отдельно от Main app)
- Нужен отдельный lifecycle (например, Settings как отдельная Activity)
- Интеграция с system (Camera Intent, Share Intent)
- Legacy код, где рефакторинг слишком дорогой

**Пример разделения:**
```
MainActivity (Single Activity)
├── HomeFragment
├── DetailFragment
├── ProfileFragment

AuthActivity (отдельная для auth flow)
├── LoginFragment
├── RegisterFragment

SettingsActivity (отдельная для настроек)
```

**Вывод:** Single Activity — современный подход для большинства случаев. Multiple Activities — для логически независимых flow или legacy кода.

---

## Связи

**Фундаментальные концепции:**
→ [[android-activity-lifecycle]] — back stack в Navigation Component основан на Activity/Fragment lifecycle. Понимание lifecycle критично для правильной обработки configuration changes и state restoration
→ [[android-app-components]] — Navigation работает с Activity и Fragments. Нужно понимать разницу между Single Activity и Multiple Activities архитектурой

**UI Frameworks:**
→ [[android-compose]] — Compose Navigation использует другой подход (type-safe routes через sealed classes). Если проект на Compose, Safe Args из XML не нужны
→ [[android-ui-views]] — Navigation Component изначально создан для View-based UI с Fragments. Deep Links и NavGraph работают с классическими XML layouts

**Архитектурные паттерны:**
→ [[android-viewmodel-internals]] — NavController интегрируется с ViewModel через savedStateHandle для сохранения state. Shared ViewModel между destinations работает через activityViewModels()
→ [[android-dependency-injection]] — NavController можно инжектить через Hilt/Koin для unit-тестирования navigation logic

**Дополнительно:**
→ [[android-overview]] — карта всего Android раздела
→ [[android-testing]] — тестирование navigation flow через NavigationTestRule

---

## Источники

**Official Documentation:**
- [Navigation - Android Developers](https://developer.android.com/guide/navigation) — Navigation Component
- [Navigate with Safe Args](https://developer.android.com/guide/navigation/use-graph/safe-args) — Safe Args
- [Deep Links](https://developer.android.com/guide/navigation/design/deep-link) — Deep Links
- [Navigation and the Back Stack](https://developer.android.com/guide/navigation/backstack) — Back Stack
- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — Activity Result API
- [Tasks and back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack) — Task management
- [Intents and intent filters](https://developer.android.com/guide/components/intents-filters) — Intent types
- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — Lifecycle
- [Fragments](https://developer.android.com/guide/fragments) — Fragment basics
- [Saving state](https://developer.android.com/topic/libraries/architecture/saving-states) — Process death

**Google I/O & Announcements:**
- [Navigation 3 at Google I/O 2025](https://developer.android.com/develop/ui/compose/navigation) — Navigation 3 preview
- [Type-safe Navigation in Compose (2.8+)](https://developer.android.com/guide/navigation/design/type-safety) — Kotlin Serialization

**Community & Guides:**
- [Tech Interview Handbook - Navigation](https://www.techinterviewhandbook.org/) — Patterns
- [CodePath Android Cliffnotes](https://guides.codepath.com/android) — Task stacks, transitions
- [Understand Activity launchMode](https://inthecheesefactory.com/blog/understand-android-activity-launchmode/en) — Launch modes visual guide

---

*Проверено: 2026-01-09 | Расширено разделами Compose Navigation Advanced, Fragment Transactions, Activity Navigation*

