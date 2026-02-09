---
title: "KMP DI Patterns: Koin, kotlin-inject, Manual DI"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, dependency-injection, koin, kotlin-inject, di, patterns]
related:
  - "[[00-kmp-overview]]"
  - "[[kmp-architecture-patterns]]"
  - "[[kmp-project-structure]]"
cs-foundations:
  - "[[inversion-of-control]]"
  - "[[dependency-inversion-principle]]"
  - "[[object-lifecycle-management]]"
  - "[[service-locator-vs-di]]"
---

# KMP Dependency Injection Patterns

> **TL;DR:** Koin — самый популярный DI для KMP (runtime, простой DSL, быстрая сборка). kotlin-inject — compile-time альтернатива (Dagger-like API, безопасность на этапе компиляции). Manual DI — подходит для маленьких проектов. Koin 4.0+ поддерживает все KMP targets и Compose Multiplatform. Используйте expect/actual для platform-specific dependencies (Context, UIDevice). Koin Annotations (KSP) — современный подход без reflection.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Project Structure | Source sets | [[kmp-project-structure]] |
| expect/actual | Platform code | [[kmp-expect-actual]] |
| Interfaces | Абстракции | [[kotlin-overview]] |
| **CS-foundations** | | |
| SOLID Principles | DIP в архитектуре | [[solid-principles]] |
| Inversion of Control | Базовая концепция DI | [[inversion-of-control]] |
| Object Lifecycle | Scopes и время жизни | [[object-lifecycle-management]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Dependency Injection** | Внедрение зависимостей извне | Официант приносит блюдо, а не клиент готовит |
| **Service Locator** | Реестр зависимостей | Справочное бюро, где можно найти нужное |
| **Module** | Группа зависимостей | Отдел в магазине |
| **Scope** | Время жизни зависимости | Срок годности продукта |
| **Single** | Singleton экземпляр | Единственный директор компании |
| **Factory** | Новый экземпляр каждый раз | Конвейер производства |
| **KSP** | Kotlin Symbol Processing | Автоматический генератор кода |

---

## Почему Dependency Injection критичен для KMP?

### Проблема: Platform Dependencies Everywhere

**Без DI в KMP вы получаете:**

```kotlin
// ❌ АНТИПАТТЕРН: Hardcoded platform dependencies
class UserRepository {
    // Как создать это в commonMain?
    private val context: Context = ???  // Android-only!
    private val nsUserDefaults: NSUserDefaults = ???  // iOS-only!
}
```

Dependency Injection решает **фундаментальную проблему KMP** — как передавать platform-specific зависимости в shared code без прямых зависимостей.

### Inversion of Control (IoC) — научная основа DI

**Martin Fowler (2004)** формализовал Inversion of Control:

> "Don't call us, we'll call you" — Hollywood Principle

**Традиционный control flow:**
```
Ваш код → вызывает → Library code
```

**Inverted control flow (DI):**
```
Framework → создаёт и передаёт → Ваши зависимости
```

```
┌─────────────────────────────────────────────────────────────────────┐
│              INVERSION OF CONTROL В КОНТЕКСТЕ KMP                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   БЕЗ IoC (прямые зависимости):                                     │
│   ┌──────────────┐      creates      ┌──────────────┐               │
│   │  Repository  │ ───────────────►  │   ApiClient  │               │
│   └──────────────┘                   └──────────────┘               │
│         │                                                           │
│         │  НО! Repository в commonMain                              │
│         │  не знает как создать platform-specific ApiClient         │
│         ▼                                                           │
│      ПРОБЛЕМА: tight coupling к конкретной реализации               │
│                                                                     │
│   С IoC (dependency injection):                                     │
│   ┌──────────────┐     depends on    ┌──────────────┐               │
│   │  Repository  │ ◄───────────────  │  interface   │               │
│   │ (commonMain) │    abstraction    │   ApiClient  │               │
│   └──────────────┘                   └──────────────┘               │
│         ▲                                   ▲                       │
│         │                                   │                       │
│         │ injected                          │ implements            │
│         │                                   │                       │
│   ┌──────────────┐               ┌──────────────────────┐           │
│   │ DI Container │               │ AndroidApiClient     │           │
│   │ (Koin/etc)   │               │ IOSApiClient         │           │
│   └──────────────┘               └──────────────────────┘           │
│                                                                     │
│   РЕЗУЛЬТАТ: Repository не знает о платформе!                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Service Locator vs Dependency Injection

**Технически Koin — это Service Locator**, не чистый DI:

| Паттерн | Как работает | Пример |
|---------|-------------|--------|
| **Dependency Injection** | Зависимости передаются через конструктор | `class Repo(val api: Api)` |
| **Service Locator** | Код сам запрашивает зависимости | `val api: Api by inject()` |

**Martin Fowler различает:**
- **DI**: "dependencies are pushed from outside"
- **Service Locator**: "dependencies are pulled from a registry"

```kotlin
// Pure DI (kotlin-inject)
@Inject
class UserRepository(
    private val api: UserApi  // ← pushed from outside
)

// Service Locator (Koin)
class UserRepository : KoinComponent {
    private val api: UserApi by inject()  // ← pulled from registry
}
```

**Почему Koin всё равно считается DI?**
- На практике оба подхода решают одну проблему — loose coupling
- Koin DSL поддерживает constructor injection синтаксис
- "Service Locator" звучит плохо из-за anti-pattern stigma, но с proper scoping работает отлично

### Compile-time vs Runtime DI

```
┌─────────────────────────────────────────────────────────────────────┐
│                 COMPILE-TIME vs RUNTIME DI                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   COMPILE-TIME (kotlin-inject, Dagger):                             │
│   ─────────────────────────────────────                             │
│                                                                     │
│   Source Code ──► KSP/KAPT ──► Generated Code ──► Compiled App      │
│                      │                                              │
│                      ▼                                              │
│              Dependency graph                                       │
│              validated at BUILD                                     │
│                                                                     │
│   ✅ Ошибки видны при компиляции                                    │
│   ✅ Быстрый runtime (no reflection)                                │
│   ❌ Медленная сборка (code generation)                             │
│   ❌ Больше generated code                                          │
│                                                                     │
│   RUNTIME (Koin):                                                   │
│   ─────────────────────────────────────                             │
│                                                                     │
│   Source Code ──► Compiled directly ──► App starts ──► DI resolves  │
│                                              │                      │
│                                              ▼                      │
│                                       Dependencies                  │
│                                       resolved at RUNTIME           │
│                                                                     │
│   ✅ Быстрая сборка                                                 │
│   ✅ Меньше boilerplate                                             │
│   ❌ Ошибки только в runtime                                        │
│   ❌ Чуть медленнее startup                                         │
│                                                                     │
│   КОМПРОМИСС: Koin checkModules() — тесты ловят ошибки!            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Scopes и Object Lifecycle

**Почему scopes важны?**

В multiplatform приложении объекты имеют разное время жизни:

| Scope | Время жизни | Пример |
|-------|-------------|--------|
| **Singleton** | Весь lifetime приложения | HttpClient, Database |
| **Session** | Пока пользователь залогинен | AuthToken, UserProfile |
| **Screen** | Пока экран на стеке | ViewModel |
| **Request** | Один вызов | UseCase результат |

```kotlin
// Правильное использование scopes
val appModule = module {
    // Singleton — создаётся один раз
    single { HttpClient() }
    single { Database(get()) }

    // Factory — каждый раз новый
    factory { GetUserUseCase(get()) }

    // Scoped — живёт пока scope открыт
    scope<UserSession> {
        scoped { AuthenticatedApiClient(get()) }
    }
}
```

**Memory leak prevention:**
```kotlin
class CheckoutViewModel : KoinComponent {
    // Создаём scope
    private val scope = getKoin().createScope<CheckoutScope>()

    override fun onCleared() {
        scope.close()  // ← КРИТИЧНО! Иначе memory leak
    }
}
```

---

## Обзор DI решений

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DI SOLUTIONS FOR KMP                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   KOIN (Runtime)                                                    │
│   ─────────────────────────────                                     │
│   • Самый популярный для KMP                                        │
│   • Простой DSL                                                     │
│   • Быстрая сборка                                                  │
│   • Runtime resolution                                              │
│   • Ошибки в runtime                                                │
│                                                                     │
│   KOTLIN-INJECT (Compile-time)                                      │
│   ─────────────────────────────                                     │
│   • Dagger-like API                                                 │
│   • Compile-time safety                                             │
│   • Быстрый runtime                                                 │
│   • Дольше сборка                                                   │
│                                                                     │
│   MANUAL DI                                                         │
│   ─────────────────────────────                                     │
│   • Полный контроль                                                 │
│   • Нет зависимостей                                                │
│   • Больше boilerplate                                              │
│   • Для маленьких проектов                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Сравнение

| Аспект | Koin | kotlin-inject | Manual DI |
|--------|------|---------------|-----------|
| **Build time** | ✅ Быстрая | ❌ Медленнее | ✅ Самая быстрая |
| **Runtime perf** | ⚠️ Медленнее старт | ✅ Быстрый | ✅ Самый быстрый |
| **Error detection** | ❌ Runtime | ✅ Compile-time | ✅ Compile-time |
| **Learning curve** | ✅ Простой | ⚠️ Средняя | ✅ Простой |
| **Boilerplate** | ✅ Минимальный | ⚠️ Annotations | ❌ Много |
| **KMP support** | ✅ Полная | ✅ Полная | ✅ Полная |

---

## Koin (Рекомендуется для KMP)

### Setup

**gradle/libs.versions.toml:**

```toml
[versions]
koin = "4.2.0"

[libraries]
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin" }
koin-test = { module = "io.insert-koin:koin-test", version.ref = "koin" }
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin" }
koin-compose = { module = "io.insert-koin:koin-compose", version.ref = "koin" }
koin-compose-viewmodel = { module = "io.insert-koin:koin-compose-viewmodel", version.ref = "koin" }
```

**shared/build.gradle.kts:**

```kotlin
kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.koin.core)
        }
        commonTest.dependencies {
            implementation(libs.koin.test)
        }
        androidMain.dependencies {
            implementation(libs.koin.android)
        }
    }
}
```

**composeApp/build.gradle.kts:**

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.koin.compose)
            implementation(libs.koin.compose.viewmodel)
        }
    }
}
```

### Module Definition

```kotlin
// commonMain/di/CommonModule.kt
import org.koin.core.module.dsl.singleOf
import org.koin.dsl.module

val commonModule = module {
    // Singleton
    single<UserRepository> { UserRepositoryImpl(get(), get()) }

    // Factory (новый instance каждый раз)
    factory { GetUserUseCase(get()) }

    // С параметрами
    factory { (userId: String) -> UserDetailViewModel(userId, get()) }

    // Bind interface
    singleOf(::UserRepositoryImpl) bind UserRepository::class
}

val networkModule = module {
    single {
        HttpClient {
            install(ContentNegotiation) {
                json()
            }
        }
    }

    single { UserApi(get()) }
}

fun appModule() = listOf(commonModule, networkModule, platformModule())
```

### Platform-Specific Modules

```kotlin
// commonMain/di/PlatformModule.kt
expect fun platformModule(): Module

// androidMain/di/PlatformModule.android.kt
import android.content.Context
import org.koin.dsl.module

actual fun platformModule() = module {
    single<Logger> { AndroidLogger(get()) }
    single<FileStorage> { AndroidFileStorage(get<Context>()) }
}

class AndroidLogger(private val context: Context) : Logger {
    override fun log(message: String) {
        android.util.Log.d("App", message)
    }
}

// iosMain/di/PlatformModule.ios.kt
import platform.Foundation.NSLog
import org.koin.dsl.module

actual fun platformModule() = module {
    single<Logger> { IOSLogger() }
    single<FileStorage> { IOSFileStorage() }
}

class IOSLogger : Logger {
    override fun log(message: String) {
        NSLog(message)
    }
}
```

### Initialization

**Android:**

```kotlin
// androidApp/src/main/kotlin/MyApplication.kt
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidContext(this@MyApplication)
            modules(appModule())
        }
    }
}
```

**iOS:**

```kotlin
// commonMain/KoinHelper.kt
fun initKoin(appDeclaration: KoinAppDeclaration = {}) {
    startKoin {
        appDeclaration()
        modules(appModule())
    }
}

// Для iOS без параметров (Kotlin default params не работают в ObjC)
fun initKoinIos() {
    initKoin {}
}
```

```swift
// iOSApp/App.swift
import SwiftUI
import SharedKit

@main
struct iOSApp: App {
    init() {
        KoinHelperKt.initKoinIos()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### Usage in Compose

```kotlin
// commonMain/ui/UserListScreen.kt
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun UserListScreen(
    viewModel: UserListViewModel = koinViewModel()
) {
    val state = viewModel.state.collectAsState()

    LazyColumn {
        items(state.value.users) { user ->
            UserItem(user)
        }
    }
}
```

### Usage in iOS (Swift)

```kotlin
// commonMain/KoinHelper.kt
class KoinHelper : KoinComponent {
    private val userRepository: UserRepository by inject()

    fun getUsers(): List<User> {
        return runBlocking { userRepository.getUsers() }
    }
}
```

```swift
// SwiftUI
struct UserListView: View {
    let helper = KoinHelper()

    var body: some View {
        List(helper.getUsers(), id: \.id) { user in
            Text(user.name)
        }
    }
}
```

### Scopes

```kotlin
val featureModule = module {
    // Session scope
    scope<UserSession> {
        scoped { SessionManager() }
        scoped { AuthenticatedApi(get()) }
    }

    // Named scope
    scope(named("checkout")) {
        scoped { CartService() }
        scoped { PaymentProcessor() }
    }
}

// Использование
class CheckoutViewModel : KoinComponent {
    private val scope = getKoin().createScope("checkoutScope", named("checkout"))
    private val cart: CartService = scope.get()

    fun onCleared() {
        scope.close()  // Важно: закрыть scope!
    }
}
```

---

## Koin Annotations (Modern Approach)

### Setup

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.insert-koin:koin-core:4.2.0")
            implementation("io.insert-koin:koin-annotations:2.0.0")
        }
    }
}

dependencies {
    add("kspCommonMainMetadata", "io.insert-koin:koin-ksp-compiler:2.0.0")
}
```

### Annotation Usage

```kotlin
// Автоматическая регистрация как singleton
@Single
class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase
) : UserRepository {
    // ...
}

// Factory
@Factory
class GetUserUseCase(
    private val repository: UserRepository
)

// Scoped
@Scope(SomeScope::class)
@Scoped
class ScopedService

// С named qualifier
@Single
@Named("remote")
class RemoteDataSource : DataSource

@Single
@Named("local")
class LocalDataSource : DataSource

// Module declaration
@Module
@ComponentScan("com.app.di")
class AppModule
```

### Generated Code

Koin Annotations генерирует модули автоматически:

```kotlin
// Сгенерированный код
val AppModule = module {
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    factory { GetUserUseCase(get()) }
}
```

---

## kotlin-inject (Compile-Time)

### Setup

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("me.tatarka.inject:kotlin-inject-runtime:0.7.2")
        }
    }
}

dependencies {
    add("kspCommonMainMetadata", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.7.2")
    add("kspAndroid", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.7.2")
    add("kspIosArm64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.7.2")
    add("kspIosX64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.7.2")
    add("kspIosSimulatorArm64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.7.2")
}
```

### Component Definition

```kotlin
// commonMain/di/AppComponent.kt
import me.tatarka.inject.annotations.*

@Inject
class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase
) : UserRepository

@Inject
class GetUserUseCase(
    private val repository: UserRepository
)

@Component
abstract class AppComponent {
    abstract val userRepository: UserRepository
    abstract val getUserUseCase: GetUserUseCase

    // Factory method
    protected val UserRepositoryImpl.bind: UserRepository
        @Provides get() = this
}

// Создание компонента
val component = AppComponent::class.create()
val repository = component.userRepository
```

### Scopes

```kotlin
@Scope
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION, AnnotationTarget.PROPERTY_GETTER)
annotation class Singleton

@Singleton
@Inject
class ApiClient

@Singleton
@Component
abstract class SingletonComponent {
    abstract val apiClient: ApiClient  // Singleton
}
```

### Platform-Specific

```kotlin
// commonMain
@Component
abstract class CommonComponent {
    abstract val logger: Logger
}

// androidMain
@Component
abstract class AndroidComponent(
    @get:Provides val context: Context
) : CommonComponent() {
    override val logger: Logger
        @Provides get() = AndroidLogger(context)
}

// iosMain
@Component
abstract class IOSComponent : CommonComponent() {
    override val logger: Logger
        @Provides get() = IOSLogger()
}
```

---

## Manual DI

### Simple Factory Pattern

```kotlin
// commonMain/di/AppContainer.kt
class AppContainer(
    // Platform dependencies injected from outside
    private val platformDependencies: PlatformDependencies
) {
    // Lazy singletons
    private val httpClient by lazy {
        HttpClient {
            install(ContentNegotiation) { json() }
        }
    }

    private val userApi by lazy {
        UserApi(httpClient)
    }

    private val userDatabase by lazy {
        UserDatabase(platformDependencies.databaseDriver)
    }

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(userApi, userDatabase)
    }

    // Factory methods
    fun createGetUserUseCase(): GetUserUseCase {
        return GetUserUseCase(userRepository)
    }

    fun createUserListViewModel(): UserListViewModel {
        return UserListViewModel(createGetUserUseCase())
    }
}

// Platform dependencies interface
interface PlatformDependencies {
    val databaseDriver: SqlDriver
    val logger: Logger
}
```

### Android Setup

```kotlin
// androidMain
class AndroidPlatformDependencies(
    private val context: Context
) : PlatformDependencies {
    override val databaseDriver: SqlDriver by lazy {
        AndroidSqliteDriver(Database.Schema, context, "app.db")
    }

    override val logger: Logger = AndroidLogger(context)
}

// Application
class MyApplication : Application() {
    val appContainer by lazy {
        AppContainer(AndroidPlatformDependencies(this))
    }
}

// Usage in Activity/Fragment
val viewModel = (application as MyApplication)
    .appContainer
    .createUserListViewModel()
```

### iOS Setup

```kotlin
// iosMain
class IOSPlatformDependencies : PlatformDependencies {
    override val databaseDriver: SqlDriver by lazy {
        NativeSqliteDriver(Database.Schema, "app.db")
    }

    override val logger: Logger = IOSLogger()
}

// Helper for iOS
object AppContainerProvider {
    val shared = AppContainer(IOSPlatformDependencies())
}
```

```swift
// Swift usage
let viewModel = AppContainerProvider.shared.createUserListViewModel()
```

---

## Best Practices

### 1. Interfaces for Shared Code

```kotlin
// ✅ Interface в commonMain
interface UserRepository {
    suspend fun getUser(id: String): User
}

// ✅ Implementation в commonMain или platform
class UserRepositoryImpl(
    private val api: UserApi
) : UserRepository {
    override suspend fun getUser(id: String) = api.getUser(id)
}

// ✅ DI регистрирует implementation
val module = module {
    single<UserRepository> { UserRepositoryImpl(get()) }
}
```

### 2. Separate Platform Modules

```kotlin
// ✅ Чёткое разделение
val commonModule = module { /* shared dependencies */ }
val networkModule = module { /* network dependencies */ }
val databaseModule = module { /* database dependencies */ }

// Platform modules
expect fun platformModule(): Module

fun appModule() = listOf(
    commonModule,
    networkModule,
    databaseModule,
    platformModule()
)
```

### 3. Testing

```kotlin
// Test module
val testModule = module {
    single<UserRepository> { FakeUserRepository() }
    single<UserApi> { MockUserApi() }
}

class UserViewModelTest : KoinTest {
    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(testModule)
    }

    private val viewModel: UserViewModel by inject()

    @Test
    fun testLoadUsers() {
        // ...
    }
}
```

### 4. Check Modules

```kotlin
class DiCheckTest : KoinTest {
    @Test
    fun checkAllModules() {
        koinApplication {
            modules(appModule())
        }.checkModules()
    }
}
```

---

## Когда что выбирать

```
✅ KOIN:
   • KMP проекты (лучшая поддержка)
   • Быстрая итерация
   • Простой DSL
   • Интеграция с Compose

✅ KOTLIN-INJECT:
   • Compile-time safety критична
   • Dagger/Hilt опыт
   • Enterprise проекты
   • Сложные dependency graphs

✅ MANUAL DI:
   • Маленькие проекты
   • Библиотеки
   • Полный контроль
   • Без внешних зависимостей
```

---

## Мифы и заблуждения

### Миф 1: "Koin медленнее kotlin-inject на runtime"

**Реальность:** Разница в startup time составляет миллисекунды для типичного приложения. Koin 4.0+ оптимизирован, и для большинства проектов разница незаметна. kotlin-inject даёт выигрыш только при очень большом количестве зависимостей (1000+).

### Миф 2: "Service Locator — это всегда anti-pattern"

**Реальность:** Service Locator критикуют за скрытые зависимости, но Koin решает это через:
- `checkModules()` для валидации графа
- Явный DSL для определения зависимостей
- Constructor injection syntax (`singleOf(::Repository)`)

Mark Seemann (автор "Dependency Injection in .NET") признаёт, что Service Locator допустим в DI containers.

### Миф 3: "Для KMP обязательно нужен DI framework"

**Реальность:** Manual DI отлично работает для:
- Маленьких проектов (< 20 зависимостей)
- Библиотек (меньше внешних зависимостей)
- Полного контроля над lifecycle

Manual DI + interfaces + expect/actual — полноценное решение.

### Миф 4: "Dagger/Hilt работают с KMP"

**Реальность:** Dagger генерирует **Java код**, поэтому не работает с Kotlin/Native. Hilt — это Dagger wrapper, тоже не совместим. Для KMP используйте Koin или kotlin-inject.

### Миф 5: "Koin Annotations решают проблему runtime errors"

**Реальность:** Koin Annotations (KSP) генерируют модули из аннотаций, но:
- Dependency graph всё ещё резолвится в runtime
- Ошибки "missing dependency" — всё ещё runtime
- Преимущество — меньше boilerplate, не compile-time safety

Для настоящего compile-time safety — только kotlin-inject.

### Миф 6: "Можно использовать один DI container для всех platforms"

**Реальность:** Технически — да, но на практике:
- Android может использовать `androidContext()`
- iOS требует отдельную инициализацию
- Desktop может нуждаться в других lifecycle hooks

Используйте `expect fun platformModule()` для platform-specific dependencies.

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Koin KMP Docs](https://insert-koin.io/docs/reference/koin-mp/kmp/) | Official | Полная документация |
| [Koin Annotations](https://insert-koin.io/docs/reference/koin-annotations/kmp/) | Official | KSP annotations |
| [kotlin-inject](https://github.com/evant/kotlin-inject) | GitHub | Compile-time DI |

### Статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [Koin vs kotlin-inject](https://infinum.com/blog/koin-vs-kotlin-inject-dependency-injection/) | Blog | Сравнение |
| [Modern DI with Koin](https://medium.com/@felix.lf/a-guide-to-modern-dependency-injection-in-kmp-with-koin-annotations-dcc086a976f3) | Blog | Koin Annotations guide |
| [DI Showdown](https://www.droidcon.com/2024/08/30/koin-vs-kotlin-inject-the-ultimate-dependency-injection-showdown-on-the-kmp-arena/) | Droidcon | Deep comparison |

### Примеры

| Ресурс | Описание |
|--------|----------|
| [hello-kmp](https://github.com/InsertKoinIO/hello-kmp) | Koin official sample |
| [koin-annotations-example](https://github.com/felix-leyva/koin-annotations-example) | Annotations example |

### CS-фундамент

| Тема | Почему важно | Где изучить |
|------|--------------|-------------|
| Inversion of Control | Основа DI паттерна | [[inversion-of-control]] |
| Dependency Inversion Principle | SOLID "D" | [[solid-principles]] |
| Object Lifecycle | Scopes и memory management | [[object-lifecycle-management]] |
| Service Locator Pattern | Koin под капотом | [[service-locator-vs-di]] |
| Reflection vs Code Generation | Runtime vs compile-time | [[metaprogramming-basics]] |

---

*Проверено: 2026-01-09 | Koin 4.2.0, kotlin-inject 0.7.2, Kotlin 2.1.21*
