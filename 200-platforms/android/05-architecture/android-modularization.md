---
title: "Модуляризация Android-приложений"
created: 2025-01-15
modified: 2026-02-13
type: deep-dive
status: published
cs-foundations: [module-systems, dependency-graph, build-optimization, encapsulation]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/advanced
related:
  - "[[android-gradle-fundamentals]]"
  - "[[android-architecture-patterns]]"
  - "[[android-dependencies]]"
  - "[[android-viewmodel-internals]]"
prerequisites:
  - "[[android-gradle-fundamentals]]"
  - "[[android-architecture-patterns]]"
  - "[[android-dependencies]]"
reading_time: 39
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Android Modularization — Under the Hood

> Разделение Android-приложения на независимые Gradle-модули для улучшения build time, масштабируемости и maintainability.

---

## Зачем это нужно

### Проблема: Монолит не масштабируется

Когда проект растёт, монолитная архитектура (один `:app` модуль) создаёт критические проблемы:

| Проблема | Влияние | Данные |
|----------|---------|--------|
| **Build time** | Любое изменение пересобирает ВСЁ | 5+ минут на каждый билд |
| **Merge conflicts** | Все работают в одних файлах | 30% времени на резолв конфликтов |
| **Tight coupling** | Изменение в A ломает B, C, D | Регрессии при каждом релизе |
| **Testing** | Нельзя тестировать изолированно | Медленные, flaky тесты |

### Индустриальные данные

Согласно опросам Google и сообщества Android:

- **86% разработчиков** работают с multi-module проектами
- **90%+ рекомендуют** модуляризацию как best practice
- **83% приложений >500K строк** испытывают проблемы с build performance без модуляризации
- Все крупные приложения Google (YouTube, Play Store, Google News) — модульные

### Кому и когда это нужно

| Ситуация | Нужна модуляризация? |
|----------|---------------------|
| Solo проект, <10K строк | ❌ Нет — overhead не оправдан |
| 1-2 разработчика, 10-50K строк | ⚠️ Базовая — core модули |
| Команда 3-5 человек, 50-200K строк | ✅ Да — feature модули |
| Большая команда, >200K строк | ✅✅ Обязательно — полная модуляризация |

### Что даёт модуляризация

```
Monolith:                    Multi-Module:
┌─────────────┐              ┌─────────────┐
│    :app     │              │    :app     │ ← minimal code
│   500K LOC  │              └──────┬──────┘
│   5 min     │                     │
│   rebuild   │         ┌──────┬────┴────┬──────┐
└─────────────┘         ▼      ▼         ▼      ▼
                    :home  :search  :profile  :settings
                     15s     15s      15s       15s
                   rebuild  rebuild  rebuild  rebuild
```

**Конкретные выгоды:**
- **Parallel builds**: независимые модули собираются параллельно
- **Incremental builds**: изменение в `:feature:home` НЕ пересобирает `:feature:search`
- **Encapsulation**: `internal` классы недоступны из других модулей
- **Team ownership**: каждая команда владеет своими модулями
- **Testability**: модуль тестируется изолированно

---

## Обзор

Модуляризация — разделение приложения на независимые Gradle-модули. Это не просто "хорошая практика", а **необходимость** для приложений среднего и большого размера.

```
Эволюция:
2008-2015: Monolith (один app модуль)
2015-2018: Library modules (переиспользование)
2018-2020: Feature modules (масштабирование команд)
2020-2025: Convention Plugins + Version Catalogs (индустриальный стандарт)
```

---

## Зачем модуляризация?

### Проблемы монолита

```
Monolith App (один модуль):
┌─────────────────────────────────────────────────────┐
│                      :app                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Feature A│ │ Feature B│ │ Feature C│            │
│  │          │ │          │ │          │            │
│  │  ──────►─┼─┼──►───────┼─┼──►───────│            │
│  │  ◄──────┼─┼──◄───────┼─┼──◄───────│            │
│  └──────────┘ └──────────┘ └──────────┘            │
│        ▲           ▲           ▲                   │
│        │           │           │                   │
│        └───────────┴───────────┘                   │
│              Всё знает обо всём                    │
│                                                     │
│  Problems:                                          │
│  • Build time: 5+ minutes на каждое изменение      │
│  • Tight coupling: изменение A ломает B и C        │
│  • Merge conflicts: все работают в одних файлах    │
│  • No encapsulation: любой код доступен отовсюду   │
│  • Testing: нельзя тестировать в изоляции          │
└─────────────────────────────────────────────────────┘
```

### Преимущества модуляризации

```
Multi-module App:
┌────────────────────────────────────────────────────────┐
│                        :app                            │
│            (только склеивает модули)                   │
└──────────┬────────────┬────────────┬──────────────────┘
           │            │            │
     ┌─────▼─────┐┌─────▼─────┐┌─────▼─────┐
     │ :feature: ││ :feature: ││ :feature: │
     │   home    ││  search   ││  profile  │
     └─────┬─────┘└─────┬─────┘└─────┬─────┘
           │            │            │
     ┌─────▼────────────▼────────────▼─────┐
     │              :core:ui               │
     │         (shared components)         │
     └─────────────────┬───────────────────┘
                       │
     ┌─────────────────▼───────────────────┐
     │            :core:domain             │
     │         (business logic)            │
     └─────────────────┬───────────────────┘
                       │
     ┌─────────────────▼───────────────────┐
     │             :core:data              │
     │    (repositories, data sources)     │
     └─────────────────────────────────────┘

Benefits:
✓ Parallel builds: независимые модули собираются параллельно
✓ Incremental builds: изменение в :feature:home не пересобирает :feature:search
✓ Encapsulation: internal классы недоступны из других модулей
✓ Ownership: команда владеет своими модулями
✓ Testability: каждый модуль тестируется изолированно
```

---

## Типы модулей

### Стандартная архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                         APPLICATION                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                        :app                           │ │
│  │   • Application class                                 │ │
│  │   • MainActivity (single activity)                    │ │
│  │   • DI setup (Hilt/Koin root)                        │ │
│  │   • Navigation graph                                  │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                          FEATURES                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  :feature:  │ │  :feature:  │ │  :feature:  │           │
│  │    home     │ │   search    │ │   profile   │           │
│  │             │ │             │ │             │           │
│  │ • Screens   │ │ • Screens   │ │ • Screens   │           │
│  │ • ViewModels│ │ • ViewModels│ │ • ViewModels│           │
│  │ • DI module │ │ • DI module │ │ • DI module │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                           CORE                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │
│  │ :core:ui  │ │:core:data │ │:core:domain│ │:core:common│  │
│  │           │ │           │ │           │ │           │   │
│  │ • Theme   │ │ • Repos   │ │ • UseCases│ │ • Utils   │   │
│  │ • Design  │ │ • Sources │ │ • Models  │ │ • Exts    │   │
│  │   System  │ │ • DTOs    │ │ • Logic   │ │ • Constants│  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘   │
├─────────────────────────────────────────────────────────────┤
│                        INFRASTRUCTURE                       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │
│  │:core:network│:core:database│:core:analytics│:core:testing│
│  │           │ │           │ │           │ │           │   │
│  │ • Retrofit│ │ • Room    │ │ • Firebase│ │ • Fakes   │   │
│  │ • OkHttp  │ │ • DAO     │ │ • Custom  │ │ • Fixtures│   │
│  │ • ApiService││ • Migrations││ • Events │ │ • Rules   │   │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Детальное описание типов

#### 1. App Module

```kotlin
// :app/build.gradle.kts
plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dagger.hilt.android.plugin")
}

android {
    namespace = "com.example.app"
    defaultConfig {
        applicationId = "com.example.app"
        versionCode = 1
        versionName = "1.0.0"
    }
}

dependencies {
    // Все feature модули
    implementation(project(":feature:home"))
    implementation(project(":feature:search"))
    implementation(project(":feature:profile"))
    implementation(project(":feature:settings"))

    // Core модули для DI setup
    implementation(project(":core:ui"))
    implementation(project(":core:data"))

    // Hilt
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
}
```

```kotlin
// :app/src/main/.../App.kt
@HiltAndroidApp
class App : Application() {

    override fun onCreate() {
        super.onCreate()
        // Минимум логики — только инициализация
        initTimber()
        initStrictMode()
    }
}
```

#### 2. Feature Modules

```kotlin
// :feature:home/build.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
    id("dagger.hilt.android.plugin")
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    // Только необходимые core модули
    implementation(project(":core:ui"))
    implementation(project(":core:domain"))
    implementation(project(":core:common"))

    // НЕ зависит от других feature модулей!
    // Навигация через :core:navigation
    implementation(project(":core:navigation"))
}
```

```
Feature Module Structure:
:feature:home/
├── src/main/
│   ├── kotlin/com/example/feature/home/
│   │   ├── HomeScreen.kt           # Composable UI
│   │   ├── HomeViewModel.kt        # ViewModel
│   │   ├── HomeUiState.kt          # UI State
│   │   ├── HomeNavigation.kt       # Navigation setup
│   │   ├── di/
│   │   │   └── HomeModule.kt       # Hilt module
│   │   └── components/             # Internal components
│   │       ├── HomeHeader.kt
│   │       └── HomeList.kt
│   └── res/
│       ├── values/strings.xml      # Feature-specific strings
│       └── drawable/               # Feature-specific drawables
└── src/test/
    └── kotlin/com/example/feature/home/
        └── HomeViewModelTest.kt
```

#### 3. Core Modules

```kotlin
// :core:domain/build.gradle.kts
plugins {
    id("kotlin-jvm")  // Чистый Kotlin, без Android!
}

dependencies {
    // Только Kotlin stdlib и coroutines
    implementation(libs.kotlinx.coroutines.core)

    // Для DI
    implementation(libs.javax.inject)
}
```

```kotlin
// :core:domain/.../usecase/GetUserUseCase.kt
class GetUserUseCase @Inject constructor(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return userRepository.getUser(userId)
    }
}

// Domain model — чистый Kotlin
data class User(
    val id: String,
    val name: String,
    val email: String
)

// Repository interface — в domain модуле!
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<Unit>
}
```

```kotlin
// :core:data/build.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
    id("dagger.hilt.android.plugin")
}

dependencies {
    implementation(project(":core:domain"))
    implementation(project(":core:network"))
    implementation(project(":core:database"))

    // Room, Retrofit доступны через infrastructure модули
}
```

```kotlin
// :core:data/.../repository/UserRepositoryImpl.kt
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao,
    private val dispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(id: String): Result<User> =
        withContext(dispatcher) {
            try {
                // Network first, cache fallback
                val dto = api.getUser(id)
                dao.insertUser(dto.toEntity())
                Result.success(dto.toDomain())
            } catch (e: Exception) {
                val cached = dao.getUser(id)
                if (cached != null) {
                    Result.success(cached.toDomain())
                } else {
                    Result.failure(e)
                }
            }
        }
}
```

---

## Dependency Graph

### Правила зависимостей

```
DEPENDENCY RULES (Dependency Inversion):

┌─────────────────────────────────────────────────────────────────┐
│                        ALLOWED                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   :app ──────────►  :feature:*     (app знает о features)      │
│                                                                 │
│   :feature:* ─────► :core:*        (features знают о core)     │
│                                                                 │
│   :core:data ─────► :core:domain   (data реализует domain)     │
│                                                                 │
│   :core:* ────────► :core:common   (все могут использовать)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       FORBIDDEN                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   :feature:home ──X──► :feature:search  (features изолированы) │
│                                                                 │
│   :core:* ───────X──► :feature:*        (core не знает о features)│
│                                                                 │
│   :core:domain ──X──► :core:data        (domain чистый)        │
│                                                                 │
│   :core:* ───────X──► :app              (никто не знает об app)│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Визуализация графа

```
                              :app
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
      :feature:home      :feature:search     :feature:profile
            │                   │                   │
            │         ┌────────┴────────┐          │
            │         │                 │          │
            ▼         ▼                 ▼          ▼
       :core:ui   :core:navigation   :core:domain
            │         │                 │
            │         │    ┌────────────┤
            │         │    │            │
            ▼         ▼    ▼            ▼
       :core:common  :core:data   :core:analytics
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        :core:network           :core:database

Legend:
─────► = implementation dependency
```

### Проверка графа

```kotlin
// build.gradle.kts (root)
// Используем dependency-analysis-gradle-plugin

plugins {
    id("com.autonomousapps.dependency-analysis") version "1.28.0"
}

dependencyAnalysis {
    structure {
        // Запрещаем feature → feature зависимости
        bundle("features") {
            includeGroup("com.example.feature")
        }
    }

    issues {
        all {
            onUsedTransitiveDependencies {
                severity("fail")
            }
        }
    }
}
```

```bash
# Проверка структуры
./gradlew buildHealth

# Визуализация графа
./gradlew projectDependencyGraph
```

---

## API Modules Pattern

### Проблема: Feature знает о Feature

```
Проблема:
:feature:home хочет навигироваться на :feature:profile
Но зависимость :feature:home → :feature:profile запрещена!

Решение: API modules
```

### Структура с API модулями

```
:feature:profile/
├── :feature:profile:api     # Только интерфейсы и модели
│   ├── ProfileNavigator.kt
│   └── ProfileDeeplink.kt
│
└── :feature:profile:impl    # Реализация (internal)
    ├── ProfileScreen.kt
    ├── ProfileViewModel.kt
    └── ProfileNavigatorImpl.kt
```

```kotlin
// :feature:profile:api/ProfileNavigator.kt
interface ProfileNavigator {
    fun navigateToProfile(userId: String)
    fun navigateToEditProfile()
}

data class ProfileDeeplink(
    val userId: String
)
```

```kotlin
// :feature:profile:impl/ProfileNavigatorImpl.kt
internal class ProfileNavigatorImpl @Inject constructor(
    private val navController: NavController
) : ProfileNavigator {

    override fun navigateToProfile(userId: String) {
        navController.navigate("profile/$userId")
    }

    override fun navigateToEditProfile() {
        navController.navigate("profile/edit")
    }
}
```

```kotlin
// :feature:home/build.gradle.kts
dependencies {
    // Зависит ТОЛЬКО от API!
    implementation(project(":feature:profile:api"))

    // НЕ от implementation
    // implementation(project(":feature:profile:impl")) // ❌
}
```

```kotlin
// :feature:home/HomeScreen.kt
@Composable
fun HomeScreen(
    profileNavigator: ProfileNavigator  // Инжектится через DI
) {
    Button(onClick = { profileNavigator.navigateToProfile("123") }) {
        Text("Go to Profile")
    }
}
```

### Dependency Graph с API модулями

```
                           :app
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼                                       ▼
   :feature:home                          :feature:profile:impl
         │                                       │
         │                                       │
         ▼                                       ▼
   :feature:profile:api ◄────────────────────────┘

:app зависит от impl (для регистрации в DI)
:feature:home зависит только от api
:feature:profile:impl зависит от api и реализует его
```

---

## Navigation между модулями

### Проблема централизованной навигации

```kotlin
// ❌ Плохо: Все routes в одном месте
// :core:navigation/Routes.kt
object Routes {
    const val HOME = "home"
    const val SEARCH = "search"
    const val PROFILE = "profile/{userId}"
    const val SETTINGS = "settings"
    // ... 50+ routes
}

// Проблемы:
// 1. Каждый feature должен знать о routes других features
// 2. Merge conflicts
// 3. Нарушение encapsulation
```

### Решение: Decentralized Navigation

```kotlin
// :feature:home/HomeNavigation.kt
// Каждый feature объявляет свою навигацию

const val HOME_ROUTE = "home"

fun NavGraphBuilder.homeScreen(
    onNavigateToSearch: () -> Unit,
    onNavigateToProfile: (String) -> Unit
) {
    composable(route = HOME_ROUTE) {
        HomeRoute(
            onSearchClick = onNavigateToSearch,
            onProfileClick = onNavigateToProfile
        )
    }
}

fun NavController.navigateToHome() {
    navigate(HOME_ROUTE) {
        popUpTo(HOME_ROUTE) { inclusive = true }
    }
}
```

```kotlin
// :feature:profile/ProfileNavigation.kt
const val PROFILE_ROUTE = "profile/{userId}"
const val PROFILE_ARG_USER_ID = "userId"

fun NavGraphBuilder.profileScreen(
    onBackClick: () -> Unit
) {
    composable(
        route = PROFILE_ROUTE,
        arguments = listOf(
            navArgument(PROFILE_ARG_USER_ID) { type = NavType.StringType }
        )
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getString(PROFILE_ARG_USER_ID) ?: ""
        ProfileRoute(
            userId = userId,
            onBackClick = onBackClick
        )
    }
}

fun NavController.navigateToProfile(userId: String) {
    navigate("profile/$userId")
}
```

```kotlin
// :app/AppNavigation.kt
// App собирает навигацию из всех features

@Composable
fun AppNavigation(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = HOME_ROUTE
    ) {
        // Home feature
        homeScreen(
            onNavigateToSearch = { navController.navigateToSearch() },
            onNavigateToProfile = { userId -> navController.navigateToProfile(userId) }
        )

        // Search feature
        searchScreen(
            onNavigateToProfile = { userId -> navController.navigateToProfile(userId) },
            onBackClick = { navController.popBackStack() }
        )

        // Profile feature
        profileScreen(
            onBackClick = { navController.popBackStack() }
        )
    }
}
```

### Type-Safe Navigation (Compose Navigation 2.8+)

```kotlin
// :feature:profile/ProfileNavigation.kt
@Serializable
data class ProfileRoute(val userId: String)

fun NavGraphBuilder.profileScreen(
    onBackClick: () -> Unit
) {
    composable<ProfileRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ProfileRoute>()
        ProfileScreen(
            userId = route.userId,
            onBackClick = onBackClick
        )
    }
}

fun NavController.navigateToProfile(userId: String) {
    navigate(ProfileRoute(userId))
}
```

---

## Convention Plugins

### Проблема: Дублирование конфигурации

```kotlin
// ❌ Каждый модуль повторяет одно и то же
// :feature:home/build.gradle.kts
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("dagger.hilt.android.plugin")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.example.feature.home"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
    // ... много повторяющихся зависимостей
}
```

### Решение: build-logic module

```
Project Structure:
├── build-logic/
│   ├── convention/
│   │   ├── build.gradle.kts
│   │   └── src/main/kotlin/
│   │       ├── AndroidApplicationConventionPlugin.kt
│   │       ├── AndroidLibraryConventionPlugin.kt
│   │       ├── AndroidFeatureConventionPlugin.kt
│   │       ├── AndroidComposeConventionPlugin.kt
│   │       └── KotlinLibraryConventionPlugin.kt
│   └── settings.gradle.kts
├── app/
├── feature/
├── core/
└── settings.gradle.kts
```

```kotlin
// build-logic/convention/build.gradle.kts
plugins {
    `kotlin-dsl`
}

dependencies {
    compileOnly(libs.android.gradle.plugin)
    compileOnly(libs.kotlin.gradle.plugin)
    compileOnly(libs.compose.gradle.plugin)
}

gradlePlugin {
    plugins {
        register("androidApplication") {
            id = "example.android.application"
            implementationClass = "AndroidApplicationConventionPlugin"
        }
        register("androidLibrary") {
            id = "example.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidFeature") {
            id = "example.android.feature"
            implementationClass = "AndroidFeatureConventionPlugin"
        }
        register("androidCompose") {
            id = "example.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
import com.android.build.gradle.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure

class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            with(pluginManager) {
                apply("com.android.library")
                apply("org.jetbrains.kotlin.android")
            }

            extensions.configure<LibraryExtension> {
                configureKotlinAndroid(this)
                defaultConfig.targetSdk = 34
            }
        }
    }
}

// Shared configuration
internal fun Project.configureKotlinAndroid(
    extension: com.android.build.api.dsl.CommonExtension<*, *, *, *, *, *>
) {
    extension.apply {
        compileSdk = 34

        defaultConfig {
            minSdk = 24
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_17
            targetCompatibility = JavaVersion.VERSION_17
        }
    }

    configureKotlin()
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply {
                apply("example.android.library")
                apply("example.android.compose")
                apply("dagger.hilt.android.plugin")
            }

            dependencies {
                // Общие зависимости для всех feature модулей
                add("implementation", project(":core:ui"))
                add("implementation", project(":core:domain"))
                add("implementation", project(":core:common"))

                add("implementation", libs.findLibrary("hilt.android").get())
                add("kapt", libs.findLibrary("hilt.compiler").get())

                add("testImplementation", project(":core:testing"))
            }
        }
    }
}
```

### Использование Convention Plugins

```kotlin
// :feature:home/build.gradle.kts
// Вместо 50+ строк — 4 строки!
plugins {
    id("example.android.feature")
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    // Только специфичные для этого модуля зависимости
    implementation(libs.coil)
}
```

```kotlin
// :core:domain/build.gradle.kts
plugins {
    id("example.kotlin.library")  // Чистый Kotlin
}

dependencies {
    implementation(libs.kotlinx.coroutines.core)
    implementation(libs.javax.inject)
}
```

---

## Build Performance

### Измерение времени сборки

```bash
# Профилирование сборки
./gradlew assembleDebug --profile --scan

# Результат: build/reports/profile/
```

### Влияние модуляризации

```
Monolith (1 module):
┌─────────────────────────────────────────────┐
│ Full rebuild: 5 minutes                     │
│ Incremental (any change): 2-3 minutes       │
│                                             │
│ Problem: Любое изменение перекомпилирует    │
│ весь проект                                 │
└─────────────────────────────────────────────┘

Multi-module (20 modules):
┌─────────────────────────────────────────────┐
│ Full rebuild: 3 minutes (parallel)          │
│ Incremental:                                │
│   • Change in :feature:home: 15 seconds     │
│   • Change in :core:domain: 45 seconds      │
│   • Change in :core:ui: 60 seconds          │
│                                             │
│ Benefit: Только затронутые модули           │
│ перекомпилируются                           │
└─────────────────────────────────────────────┘
```

### Implementation vs API

```kotlin
// КРИТИЧНО для build performance!

// ❌ api — изменение пробрасывается ВСЕМ зависимым модулям
dependencies {
    api(project(":core:network"))  // Изменение в network перекомпилирует всех
}

// ✅ implementation — изменение локально
dependencies {
    implementation(project(":core:network"))  // Изменение в network локально
}
```

```
api vs implementation rebuild:

:core:network изменился

С api зависимостью:
:core:network → :core:data → :feature:home → :app
                           → :feature:search → :app
                           → :feature:profile → :app
Всё перекомпилируется!

С implementation:
:core:network → :core:data
Только :core:data перекомпилируется
```

### Configuration Cache

```kotlin
// gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn

// Результат: конфигурация кэшируется между сборками
// Первый запуск: нормальное время
// Последующие: -10-20% от configuration phase
```

### Parallel Execution

```kotlin
// gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=8  // По количеству CPU cores

// Независимые модули собираются параллельно
// :feature:home, :feature:search, :feature:profile — одновременно
```

---

## Реальные примеры

### Now in Android (Google)

```
Структура NiA:
├── app/
├── feature/
│   ├── foryou/
│   ├── interests/
│   ├── bookmarks/
│   ├── topic/
│   └── search/
├── core/
│   ├── common/
│   ├── data/
│   ├── datastore/
│   ├── database/
│   ├── domain/
│   ├── model/
│   ├── network/
│   ├── ui/
│   ├── designsystem/
│   ├── notifications/
│   └── testing/
├── lint/
├── ui-test-hilt-manifest/
└── build-logic/
    └── convention/

Итого: ~25 модулей
Convention Plugins: 8 plugins
Version Catalog: libs.versions.toml
```

### Архитектура Тинькофф (40+ модулей)

```
tinkoff-app/
├── app/                          # Main app
├── feature/                      # ~15 feature модулей
│   ├── main/
│   ├── payments/
│   ├── investments/
│   ├── cashback/
│   └── ...
├── core/                         # ~10 core модулей
│   ├── network/
│   ├── database/
│   ├── analytics/
│   ├── auth/
│   └── ...
├── uikit/                        # Design system
│   ├── uikit-core/
│   ├── uikit-compose/
│   └── uikit-xml/
└── build-logic/
    └── convention/

Команды: 20+ команд, каждая владеет своими модулями
CI/CD: Параллельная сборка модулей
```

---

## Миграция на Multi-Module

### Пошаговая стратегия

```
Этап 1: Выделение Core
┌─────────────────────────────────────────────────────┐
│ :app (monolith)                                     │
│  │                                                  │
│  ├── Выделяем :core:network (Retrofit, OkHttp)     │
│  ├── Выделяем :core:database (Room)                │
│  └── Выделяем :core:common (extensions, utils)     │
└─────────────────────────────────────────────────────┘

Этап 2: Выделение Domain
┌─────────────────────────────────────────────────────┐
│ :app                                                │
│  │                                                  │
│  └── Выделяем :core:domain                         │
│      • UseCases                                     │
│      • Repository interfaces                        │
│      • Domain models                                │
└─────────────────────────────────────────────────────┘

Этап 3: Выделение Features (по одному)
┌─────────────────────────────────────────────────────┐
│ :app                                                │
│  │                                                  │
│  ├── Выделяем :feature:profile (самый простой)     │
│  ├── Выделяем :feature:settings                    │
│  └── ... по одному feature за раз                  │
└─────────────────────────────────────────────────────┘

Этап 4: Рефакторинг Navigation
┌─────────────────────────────────────────────────────┐
│ Заменяем прямые зависимости между features на:     │
│  • API modules                                      │
│  • Decentralized navigation                         │
│  • DI-based навигаторы                             │
└─────────────────────────────────────────────────────┘
```

### Checklist миграции

```markdown
## Pre-migration Checklist

- [ ] Version Catalog создан (libs.versions.toml)
- [ ] build-logic модуль настроен
- [ ] CI pipeline поддерживает multi-module
- [ ] Команда обучена модульной архитектуре

## Migration Checklist

- [ ] :core:network выделен
- [ ] :core:database выделен
- [ ] :core:common выделен
- [ ] :core:domain выделен
- [ ] :core:data выделен
- [ ] :core:ui выделен
- [ ] Первый :feature модуль выделен
- [ ] Все :feature модули выделены
- [ ] Навигация рефакторена
- [ ] API modules созданы (если нужно)

## Post-migration Checklist

- [ ] Build time улучшился
- [ ] Dependency graph корректный
- [ ] CI/CD оптимизирован (кэширование модулей)
- [ ] Документация обновлена
```

---

## Anti-patterns

### 1. God Core Module

```kotlin
// ❌ Всё в одном core модуле
:core/
├── network/
├── database/
├── utils/
├── extensions/
├── ui/
├── domain/
└── ... 50+ packages

// Проблема: изменение в network перекомпилирует всех

// ✅ Разделяем по responsibilities
:core:network/
:core:database/
:core:common/
:core:ui/
:core:domain/
```

### 2. Feature → Feature зависимость

```kotlin
// ❌ Прямая зависимость
// :feature:home/build.gradle.kts
dependencies {
    implementation(project(":feature:profile"))  // ЗАПРЕЩЕНО!
}

// Проблемы:
// 1. Circular dependencies
// 2. Невозможно тестировать изолированно
// 3. Build time увеличивается

// ✅ Через API module или DI
dependencies {
    implementation(project(":feature:profile:api"))
}
```

### 3. Слишком много модулей

```kotlin
// ❌ Micro-modules
:core:string-utils/     // 3 функции
:core:date-utils/       // 2 функции
:core:number-utils/     // 1 функция

// Overhead модуля > пользы

// ✅ Группируем логически связанное
:core:common/
├── StringExtensions.kt
├── DateExtensions.kt
└── NumberExtensions.kt
```

### 4. Неправильный API/Implementation split

```kotlin
// ❌ Слишком много в API модуле
:feature:profile:api/
├── ProfileScreen.kt        // UI не должен быть в api!
├── ProfileViewModel.kt     // ViewModel не должен быть в api!
├── ProfileNavigator.kt     // ✅ Это ок
└── ProfileDeeplink.kt      // ✅ Это ок

// ✅ Только контракты в API
:feature:profile:api/
├── ProfileNavigator.kt     // Interface
└── ProfileArgs.kt          // Data class для навигации
```

---

## Связь с другими темами

**[[android-gradle-fundamentals]]** — Gradle является движком модуляризации: каждый модуль — это отдельный Gradle project с собственным build.gradle. Понимание Gradle configurations (implementation vs api), task graph и Convention Plugins критично для правильной настройки multi-module проекта. Без знания Gradle невозможно настроить Version Catalogs, build variants и incremental compilation для модулей. Изучите Gradle перед началом модуляризации.

**[[android-architecture-patterns]]** — модуляризация и архитектурные паттерны (MVVM, MVI, Clean Architecture) взаимосвязаны: модули отражают архитектурные слои (data, domain, presentation). Feature-модули инкапсулируют полный вертикальный срез от UI до data layer. Правильная архитектура упрощает модуляризацию, а модуляризация делает архитектурные границы физическими (не только логическими). Рекомендуется определить архитектуру до начала разбиения на модули.

**[[android-repository-pattern]]** — Repository pattern определяет, как feature-модули взаимодействуют с данными через data-модули. В multi-module архитектуре Repository interface живёт в domain/api модуле, а реализация — в data модуле. Это обеспечивает инверсию зависимостей: feature-модули зависят только от абстракций, не от конкретных реализаций Room или Retrofit. Изучите Repository после понимания базовой модульной структуры.

**[[android-dependencies]]** — Version Catalogs и BOM решают критическую проблему multi-module проектов: согласованность версий зависимостей. Без централизованного управления зависимостями каждый модуль может использовать разные версии одной библиотеки, что ведёт к конфликтам и увеличению размера APK. Version Catalogs (libs.versions.toml) стали индустриальным стандартом для модульных проектов. Настройте Version Catalog при создании первого модуля.

---

## Ключевые выводы

1. **Модуляризация — инвестиция**: Требует времени на настройку, но окупается
2. **Convention Plugins — обязательны**: Иначе копипаста конфигурации
3. **Feature изоляция**: Features не должны знать друг о друге напрямую
4. **API modules**: Решают проблему навигации между features
5. **implementation > api**: Для минимизации rebuild scope
6. **Мигрируйте постепенно**: Core → Domain → Features по одному

---

## Источники

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Guide to Android app modularization](https://developer.android.com/topic/modularization) | Official Docs | Основные концепции, best practices |
| 2 | [Common modularization patterns](https://developer.android.com/topic/modularization/patterns) | Official Docs | Паттерны модуляризации |
| 3 | [Approaches for Multi-Module Feature Architecture](https://www.droidcon.com/2024/08/30/approaches-for-multi-module-feature-architecture-on-android/) | Conference | 4 паттерна архитектуры 2024 |
| 4 | [Making your Android project modular with convention plugins](https://michiganlabs.com/blogs/making-your-android-project-modular-with-convention-plugins) | Blog | Практика convention plugins |
| 5 | [Now in Android](https://github.com/android/nowinandroid) | GitHub | Референсная реализация от Google |
| 6 | [Modularization at Scale](https://medium.com/@hiren6997/modularization-at-scale-how-to-split-a-million-line-android-app-without-losing-your-mind-569c98e86512) | Blog | Опыт крупных проектов |
| 7 | [The Pitfalls of Preliminary Over-Modularization](https://www.techyourchance.com/preliminary-over-modularization-of-android-projects/) | Blog | Анти-паттерны, когда НЕ нужно |

---

## Источники и дальнейшее чтение

- Meier (2022). *Professional Android*. — охватывает модульную архитектуру Android-приложений, Gradle конфигурации для multi-module проектов и практические рекомендации по организации feature-модулей.
- Phillips et al. (2022). *Android Programming: The Big Nerd Ranch Guide*. — пошаговое руководство по структурированию Android-проектов, включая разделение на модули и управление зависимостями между ними.
- Moskala (2021). *Effective Kotlin*. — принципы модульного дизайна в Kotlin, включая visibility modifiers (internal), API design для модулей и best practices организации кода.

---

---

## Проверь себя

> [!question]- Почему модуляризация ускоряет сборку, хотя добавляет overhead на конфигурацию модулей?
> Gradle компилирует модули параллельно на разных CPU cores. При изменении кода в одном модуле перекомпилируется только он и зависимые модули (incremental). Без модуляризации: изменение одного файла может trigger recompilation всего проекта. При 20+ модулях параллельная сборка дает 2-5x ускорение.

> [!question]- Сценарий: два feature модуля должны общаться, но не должны зависеть друг от друга. Как реализовать?
> 1) Через :core:navigation: общий навигационный граф с маршрутами. Feature A navigate по route, Feature B регистрирует destination. 2) Через :core:common: shared interfaces. Feature A вызывает interface, Feature B реализует. DI связывает. 3) Event bus (SharedFlow в :core:common). Выбор зависит от типа взаимодействия.


---

## Ключевые карточки

Какие типы модулей в Android-проекте?
?
:app (application), :feature:* (экраны/фичи), :core:* (shared логика), :core:ui (shared UI), :core:network (API), :core:database (БД), :core:domain (бизнес-логика, чистый Kotlin). Зависимости: app -> feature -> core.

Что такое Convention Plugins?
?
Shared Gradle конфигурация для модулей. Вместо копирования build.gradle в каждый модуль -- один plugin. Например: android-library-convention задает compileSdk, minSdk, dependencies. Применяется через plugins { id('convention.android.library') }.

Какие правила зависимостей между модулями?
?
1) feature не зависит от feature. 2) core не зависит от feature. 3) app зависит от feature. 4) feature зависит от core. 5) Циклические зависимости запрещены. Проверка: ./gradlew buildHealth (Dependency Analysis plugin).

Чем implementation отличается от api в контексте модулей?
?
implementation: зависимость видна только внутри модуля. api: зависимость транзитивно видна потребителям модуля. Правило: всегда implementation, api только для public API. implementation уменьшает recompilation scope.

Что такое Dynamic Feature Module?
?
Модуль, загружаемый по требованию (Play Feature Delivery). Не входит в base APK. Пример: AR-функция загружается только когда пользователь её открывает. Экономит размер установки. Поддерживает install-time, on-demand, conditional delivery.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-gradle-fundamentals]] | Gradle для многомодульных проектов |
| Углубиться | [[android-architecture-patterns]] | Архитектурные паттерны в модульном проекте |
| Смежная тема | [[ios-modularization]] | Модуляризация в iOS: Swift Packages и Frameworks |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-01-09 — Педагогический контент проверен*
