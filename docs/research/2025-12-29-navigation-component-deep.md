# Research Report: Navigation Component Deep Patterns

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep (official docs, community patterns)

## Executive Summary

Jetpack Navigation Component (версия 2.9.6) — стабильная библиотека для Fragment-based навигации. Ключевые паттерны: multiple back stacks для bottom navigation (с 2.4.0), Safe Args для type-safety, nested graphs для auth flows, deep links для external navigation. Основные проблемы: fragment lifecycle сложности, state restoration при configuration changes, testing требует изоляции от NavController.

---

## Key Findings

### 1. Multiple Back Stacks (Navigation 2.4.0+)

**Проблема:** В bottom navigation пользователь переключается между табами и ожидает сохранения позиции в каждом табе.

**Решение с NavigationUI (рекомендуется):**
```kotlin
// Автоматическое управление back stacks — никакого дополнительного кода!
val navController = findNavController(R.id.nav_host_fragment)
val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)

NavigationUI.setupWithNavController(bottomNav, navController)
// При переключении табов:
// 1. Текущий back stack сохраняется
// 2. Back stack выбранного таба восстанавливается
```

**Ручная реализация (для кастомной навигации):**
```kotlin
// Kotlin DSL
navController.navigate(selectedRoute) {
    launchSingleTop = true
    restoreState = true
    popUpTo(navController.graph.findStartDestination().id) {
        saveState = true
    }
}
```

**XML атрибуты:**
```xml
<action
    android:id="@+id/action_switch_tab"
    app:destination="@id/other_tab"
    app:restoreState="true"
    app:popUpTo="@id/current_tab"
    app:popUpToSaveState="true" />
```

**Ключевые атрибуты:**
| Атрибут | Описание |
|---------|----------|
| `saveState` | Сохраняет state при pop |
| `restoreState` | Восстанавливает ранее сохранённый state |
| `popUpTo` | Указывает до какого destination очищать stack |
| `launchSingleTop` | Предотвращает дублирование destination |

---

### 2. Safe Args с Custom Types

**Базовые типы:**
```xml
<argument
    android:name="userId"
    app:argType="string" />

<argument
    android:name="count"
    app:argType="integer"
    android:defaultValue="0" />
```

**Parcelable types:**
```kotlin
// 1. Создать Parcelable класс
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val age: Int
) : Parcelable

// 2. Определить в nav_graph.xml
<argument
    android:name="user"
    app:argType="com.example.app.User"
    android:defaultValue="@null"
    app:nullable="true" />

// 3. Передать аргумент
val action = HomeFragmentDirections.actionHomeToProfile(user = currentUser)
findNavController().navigate(action)

// 4. Получить аргумент
class ProfileFragment : Fragment() {
    private val args: ProfileFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val user = args.user  // User?
    }
}
```

**Sealed class subclasses:**
```xml
<!-- Используй $ вместо точки -->
<argument
    android:name="animal"
    app:argType="com.example.app.Animal$Cat" />
```

**Nullable arguments:**
```xml
<!-- String, Parcelable, Serializable могут быть nullable -->
<argument
    android:name="optionalId"
    app:argType="string"
    android:defaultValue="@null"
    app:nullable="true" />
```

**ProGuard/R8 правила:**
```proguard
-keepnames class * implements android.os.Parcelable
-keepnames class * implements java.io.Serializable
-keepnames class * extends java.lang.Enum
```

---

### 3. Conditional Navigation (Auth Flow)

**Паттерн с nested graphs:**
```xml
<navigation
    android:id="@+id/main_graph"
    app:startDestination="@id/splashFragment">

    <!-- Splash для проверки auth -->
    <fragment
        android:id="@+id/splashFragment"
        android:name=".SplashFragment">

        <action
            android:id="@+id/action_to_auth"
            app:destination="@id/auth_graph"
            app:popUpTo="@id/main_graph"
            app:popUpToInclusive="true" />

        <action
            android:id="@+id/action_to_home"
            app:destination="@id/home_graph"
            app:popUpTo="@id/main_graph"
            app:popUpToInclusive="true" />
    </fragment>

    <!-- Auth nested graph -->
    <navigation
        android:id="@+id/auth_graph"
        app:startDestination="@id/loginFragment">

        <fragment android:id="@+id/loginFragment" />
        <fragment android:id="@+id/registerFragment" />

        <action
            android:id="@+id/action_auth_to_home"
            app:destination="@id/home_graph"
            app:popUpTo="@id/auth_graph"
            app:popUpToInclusive="true" />
    </navigation>

    <!-- Home nested graph -->
    <navigation
        android:id="@+id/home_graph"
        app:startDestination="@id/homeFragment">

        <fragment android:id="@+id/homeFragment" />
        <fragment android:id="@+id/profileFragment" />
    </navigation>
</navigation>
```

**Kotlin код:**
```kotlin
class SplashFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            val isLoggedIn = authRepository.isLoggedIn()

            if (isLoggedIn) {
                findNavController().navigate(R.id.action_to_home)
            } else {
                findNavController().navigate(R.id.action_to_auth)
            }
        }
    }
}
```

**Best Practices:**
- Используй nested graphs для группировки связанных экранов
- `popUpToInclusive="true"` для удаления splash/login из back stack
- Проверяй auth state в SplashScreen, не в каждом fragment

---

### 4. Deep Links

**Implicit Deep Links (в nav_graph.xml):**
```xml
<fragment
    android:id="@+id/productFragment"
    android:name=".ProductFragment">

    <!-- Web URL deep link -->
    <deepLink
        app:uri="https://example.com/product/{productId}" />

    <!-- Custom scheme deep link -->
    <deepLink
        app:uri="myapp://product/{productId}" />

    <argument
        android:name="productId"
        app:argType="string" />
</fragment>
```

**AndroidManifest.xml:**
```xml
<activity android:name=".MainActivity">
    <!-- Автогенерация intent-filters из nav_graph -->
    <nav-graph android:value="@navigation/nav_graph" />
</activity>
```

**Explicit Deep Links (для Notifications):**
```kotlin
// Создание PendingIntent
val deepLinkIntent = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.productFragment)
    .setArguments(bundleOf("productId" to "12345"))
    .createPendingIntent()

// Использование в Notification
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("New Product")
    .setContentIntent(deepLinkIntent)
    .build()
```

**Multi-Flavor Deep Links:**
```kotlin
// build.gradle.kts
android {
    productFlavors {
        create("dev") {
            manifestPlaceholders["scheme"] = "myapp-dev"
            manifestPlaceholders["host"] = "dev.example.com"
        }
        create("prod") {
            manifestPlaceholders["scheme"] = "myapp"
            manifestPlaceholders["host"] = "example.com"
        }
    }
}
```

```xml
<!-- nav_graph.xml -->
<deepLink app:uri="${scheme}://${host}/product/{id}" />
```

**Тестирование deep links:**
```bash
adb shell am start -W -a android.intent.action.VIEW \
    -d "myapp://product/12345" \
    com.example.app
```

---

### 5. Testing Navigation Component

**Dependencies:**
```kotlin
// build.gradle.kts
androidTestImplementation("androidx.navigation:navigation-testing:2.9.6")
debugImplementation("androidx.fragment:fragment-testing:1.7.0")
testImplementation("org.mockito:mockito-core:5.0.0")
androidTestImplementation("org.mockito:mockito-android:5.0.0")
```

**Подход 1: Mock NavController (Unit Testing):**
```kotlin
@RunWith(AndroidJUnit4::class)
class HomeFragmentTest {

    @get:Rule
    val activityScenarioRule = launchFragmentInContainer<HomeFragment>()

    private val mockNavController = mock<NavController>()

    @Before
    fun setup() {
        activityScenarioRule.onFragment { fragment ->
            Navigation.setViewNavController(fragment.requireView(), mockNavController)
        }
    }

    @Test
    fun clickProfile_navigatesToProfileScreen() {
        onView(withId(R.id.btn_profile)).perform(click())

        verify(mockNavController).navigate(
            HomeFragmentDirections.actionHomeToProfile()
        )
    }
}
```

**Подход 2: TestNavHostController (Integration Testing):**
```kotlin
@RunWith(AndroidJUnit4::class)
class NavigationIntegrationTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    private lateinit var navController: TestNavHostController

    @Before
    fun setup() {
        composeTestRule.activityRule.scenario.onActivity { activity ->
            navController = TestNavHostController(activity).apply {
                navigatorProvider.addNavigator(FragmentNavigator(activity, activity.supportFragmentManager, R.id.nav_host_fragment))
            }
            navController.setGraph(R.navigation.nav_graph)
        }
    }

    @Test
    fun navigateToProfile_currentDestinationIsProfile() {
        navController.navigate(R.id.profileFragment)

        assertEquals(R.id.profileFragment, navController.currentDestination?.id)
    }
}
```

**Best Practice — Decouple from NavController:**
```kotlin
// НЕ передавай NavController в Fragment
// Используй callbacks
class HomeFragment : Fragment() {

    interface NavigationListener {
        fun onProfileClicked(userId: String)
        fun onSettingsClicked()
    }

    private var navigationListener: NavigationListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        navigationListener = context as? NavigationListener
    }

    private fun onProfileClick() {
        navigationListener?.onProfileClicked(currentUserId)
    }
}

// Activity реализует listener
class MainActivity : AppCompatActivity(), HomeFragment.NavigationListener {

    override fun onProfileClicked(userId: String) {
        findNavController(R.id.nav_host).navigate(
            HomeFragmentDirections.actionHomeToProfile(userId)
        )
    }
}
```

---

### 6. Fragment Lifecycle Issues

**Проблема: Lifecycle overlap при навигации**
```
Fragment A → Fragment B:
1. A.onPause() вызывается ПОСЛЕ B.onResume() из-за анимации
2. Оба fragment видимы одновременно
```

**Решение — используй viewLifecycleOwner:**
```kotlin
class MyFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ✅ Привязка к lifecycle view, не fragment
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { updateUI(it) }
        }

        // ✅ BackPressedCallback с viewLifecycleOwner
        requireActivity().onBackPressedDispatcher.addCallback(viewLifecycleOwner) {
            // Handle back press
        }
    }
}
```

**Проблема: ViewModel scoped to nav graph crashes**
```kotlin
// ❌ Crash при configuration change
class MyFragment : Fragment() {
    private val viewModel: SharedViewModel by navGraphViewModels(R.id.my_graph)
}
// Причина: onViewCreated вызывается до Activity.onCreate завершения
```

**Решение:**
```kotlin
// ✅ Используй hiltNavGraphViewModels или проверяй graph
class MyFragment : Fragment() {
    private val viewModel: SharedViewModel by lazy {
        val navBackStackEntry = findNavController().getBackStackEntry(R.id.my_graph)
        ViewModelProvider(navBackStackEntry)[SharedViewModel::class.java]
    }
}
```

**Проблема: LiveData с SavedStateHandle после dialog**
```kotlin
// При dialog destination предыдущий fragment остаётся STARTED
// getCurrentBackStackEntry() вернёт dialog, не предыдущий fragment!
```

**Решение:**
```kotlin
// Используй getPreviousBackStackEntry() для результатов
findNavController().previousBackStackEntry?.savedStateHandle?.set("result", data)
```

---

### 7. Common Mistakes & Anti-Patterns

**1. Passing complex objects as arguments:**
```kotlin
// ❌ Anti-pattern
data class User(val id: String, val name: String, val avatar: ByteArray)
// Передача большого объекта через navigation

// ✅ Передавай только ID
navController.navigate(ProfileFragmentDirections.actionToProfile(userId = "123"))
// Загружай данные в destination
```

**2. NavController в Composable:**
```kotlin
// ❌ Anti-pattern — сложно тестировать
@Composable
fun ProfileScreen(navController: NavController) {
    Button(onClick = { navController.navigate("settings") })
}

// ✅ Callbacks
@Composable
fun ProfileScreen(onNavigateToSettings: () -> Unit) {
    Button(onClick = onNavigateToSettings)
}
```

**3. Multiple navigators:**
```kotlin
// ❌ Не рендери несколько NavHost в одном Activity
// Каждый NavHost имеет свой state, не могут взаимодействовать
```

**4. Modularization: Layer-based vs Feature-based:**
```
// ❌ Layer-based (anti-pattern)
:data
:domain
:presentation

// ✅ Feature-based
:feature:home
:feature:profile
:feature:auth
:core:navigation
```

**5. Rapid navigation calls:**
```kotlin
// ❌ Race condition
button.setOnClickListener {
    navController.navigate(R.id.next)
}
// Быстрый double-click = crash

// ✅ Debounce clicks
button.setOnClickListener {
    if (!isNavigating) {
        isNavigating = true
        navController.navigate(R.id.next)
    }
}
```

---

## Community Sentiment

### Positive Feedback
- Multiple back stacks работают "из коробки" с NavigationUI
- Safe Args значительно уменьшают runtime crashes
- Deep links интегрируются с nav_graph
- Хорошая документация от Google

### Negative Feedback / Concerns
- Fragment lifecycle сложности при animation overlap
- ViewModel scoping к nav graph имеет edge cases
- Testing требует много boilerplate
- Configuration change + nav graph scoped ViewModel = crashes
- Deep links сложно отлаживать

---

## Recommendations

1. **Для bottom navigation:**
   - Используй `NavigationUI.setupWithNavController()` — multiple back stacks автоматически

2. **Для auth flows:**
   - Nested graphs для auth/main
   - `popUpToInclusive` для очистки auth screens

3. **Для testing:**
   - Decouple fragments от NavController
   - Используй callbacks/interfaces
   - Mock NavController для unit tests

4. **Для lifecycle:**
   - Всегда `viewLifecycleOwner` для coroutines
   - Проверяй `isAdded` перед navigation
   - Используй `launchWhenStarted` для UI operations

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Android Developers - Multi Back Stacks](https://developer.android.com/guide/navigation/backstack/multi-back-stacks) | Official | 0.95 | Multiple back stacks |
| 2 | [Medium - Navigation Multiple Back Stacks](https://medium.com/androiddevelopers/navigation-multiple-back-stacks-6c67ba41952f) | Official Blog | 0.95 | Implementation details |
| 3 | [Android Developers - Pass Data](https://developer.android.com/guide/navigation/use-graph/pass-data) | Official | 0.95 | Safe Args |
| 4 | [Android Developers - Deep Links](https://developer.android.com/guide/navigation/design/deep-link) | Official | 0.95 | Deep links |
| 5 | [Android Developers - Testing](https://developer.android.com/guide/navigation/testing) | Official | 0.95 | Navigation testing |
| 6 | [Medium - Common Issues](https://medium.com/@mmelihgultekin/navigation-component-common-issues-we-can-face-e9d1e1ad2f51) | Blog | 0.80 | Lifecycle issues |
| 7 | [Kodeco - Safe Args](https://www.kodeco.com/19327407-using-safe-args-with-the-android-navigation-component) | Tutorial | 0.85 | Safe Args examples |
| 8 | [Medium - Conditional Navigation](https://medium.com/backtocoding/advanced-jetpack-compose-navigation-nested-graphs-conditional-flows-android-navigation-62806e11f9ad) | Blog | 0.80 | Auth patterns |
| 9 | [ProAndroidDev - Modularization Anti-Patterns](https://proandroiddev.com/structural-and-navigation-anti-patterns-in-modularized-android-applications-a7d667e35cd6) | Blog | 0.85 | Architecture |
| 10 | [GitHub - nav3-recipes](https://github.com/android/nav3-recipes) | Official | 0.95 | Navigation patterns |

---

*Generated: 2025-12-29*
*Purpose: Research for android-navigation.md expansion*
