---
title: "Hilt Deep-dive: от Dagger до production"
created: 2026-01-29
modified: 2026-01-29
type: deep-dive
area: android
confidence: high
cs-foundations: [dependency-injection, annotation-processing, code-generation, compile-time-validation]
tags:
  - topic/android
  - topic/dependency-injection
  - type/deep-dive
  - level/advanced
related:
  - "[[dependency-injection-fundamentals]]"
  - "[[android-dependency-injection]]"
  - "[[android-koin-deep-dive]]"
  - "[[android-architecture-patterns]]"
---

# Hilt Deep-dive: от Dagger до production

Hilt — официальная DI библиотека Google для Android, построенная поверх Dagger 2. Предоставляет предопределённые компоненты, scopes и интеграцию с Jetpack, значительно упрощая настройку Dagger.

> **Prerequisites:**
> - [[dependency-injection-fundamentals]] — базовые концепции DI
> - Понимание Kotlin annotations
> - Опыт работы с Jetpack (ViewModel, Navigation)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Component** | Контейнер, хранящий граф зависимостей |
| **Module** | Класс, описывающий как создавать зависимости |
| **Scope** | Время жизни зависимости внутри компонента |
| **Binding** | Связь между типом и его провайдером |
| **Provider** | Фабрика, создающая экземпляр зависимости |
| **@Inject** | Маркер для constructor/field injection |
| **@Provides** | Метод, создающий зависимость |
| **@Binds** | Связь интерфейса с реализацией |
| **Entry Point** | Точка доступа к зависимостям извне Hilt |

---

## Почему Hilt, а не Dagger напрямую

### Проблема Dagger

```kotlin
// Dagger: МНОГО boilerplate
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
    fun inject(fragment: HomeFragment)
    // Нужно добавлять для каждого Activity/Fragment!

    // SubComponent builders
    fun activityComponentBuilder(): ActivityComponent.Builder
}

@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    @Subcomponent.Builder
    interface Builder {
        fun activityModule(module: ActivityModule): Builder
        fun build(): ActivityComponent
    }
}

// В Application
class MyApp : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .networkModule(NetworkModule())
            .build()
    }
}

// В каждой Activity
class MainActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: MainViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}
```

### Решение Hilt

```kotlin
// Hilt: минимум boilerplate
@HiltAndroidApp
class MyApp : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()
}

@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()

// Hilt делает за нас:
// ✅ Создаёт Component
// ✅ Создаёт SubComponent для Activity/Fragment
// ✅ Управляет scopes
// ✅ Интегрируется с ViewModel
```

### Сравнение

| Аспект | Dagger | Hilt |
|--------|--------|------|
| Component | Создавать вручную | Предопределённые |
| SubComponent | Описывать самим | Автоматические |
| Scopes | Определять самим | @Singleton, @ViewModelScoped, etc. |
| ViewModel | Сложная настройка | @HiltViewModel |
| Boilerplate | Много | Минимум |

---

## Dagger под капотом

### Как работает Annotation Processing

```
┌─────────────────────────────────────────────────────────────────┐
│              DAGGER COMPILATION PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Source Code                Annotation Processor    Generated  │
│   ────────────               ───────────────────    ─────────   │
│                                                                 │
│   @Module                                                       │
│   class NetworkModule {      ┌─────────────────┐                │
│       @Provides              │                 │    NetworkModule│
│       fun provideApi()  ───► │  KAPT / KSP     │───► _ProvideApi│
│   }                          │                 │     Factory    │
│                              │  Dagger         │                │
│   @Inject                    │  Compiler       │    UserRepo_   │
│   class UserRepository  ───► │                 │───► Factory    │
│                              │                 │                │
│   @Component                 │                 │    Dagger      │
│   interface AppComponent ──► │                 │───► AppComponent│
│                              └─────────────────┘                │
│                                                                 │
│   Validation: Полный граф проверяется на этапе компиляции       │
│   Если зависимость отсутствует → Ошибка компиляции              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Что генерирует Dagger

**1. Factory для @Provides:**

```kotlin
// Исходный код
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder().build()
    }
}

// Сгенерированный код (упрощённо)
public final class NetworkModule_ProvideOkHttpClientFactory implements Provider<OkHttpClient> {

    @Override
    public OkHttpClient get() {
        return provideOkHttpClient();
    }

    public static OkHttpClient provideOkHttpClient() {
        return NetworkModule.INSTANCE.provideOkHttpClient();
    }

    public static NetworkModule_ProvideOkHttpClientFactory create() {
        return InstanceHolder.INSTANCE;
    }
}
```

**2. Factory для @Inject constructor:**

```kotlin
// Исходный код
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val db: UserDao
)

// Сгенерированный код
public final class UserRepository_Factory implements Provider<UserRepository> {
    private final Provider<ApiService> apiProvider;
    private final Provider<UserDao> dbProvider;

    public UserRepository_Factory(
        Provider<ApiService> apiProvider,
        Provider<UserDao> dbProvider
    ) {
        this.apiProvider = apiProvider;
        this.dbProvider = dbProvider;
    }

    @Override
    public UserRepository get() {
        return new UserRepository(apiProvider.get(), dbProvider.get());
    }
}
```

**3. Component Implementation:**

```kotlin
// @Component генерирует полную реализацию
public final class DaggerAppComponent implements AppComponent {
    private Provider<OkHttpClient> okHttpClientProvider;
    private Provider<ApiService> apiServiceProvider;
    private Provider<UserRepository> userRepositoryProvider;

    private void initialize() {
        // Связывание всех Provider'ов
        this.okHttpClientProvider = DoubleCheck.provider(
            NetworkModule_ProvideOkHttpClientFactory.create()
        );
        this.apiServiceProvider = DoubleCheck.provider(
            NetworkModule_ProvideApiServiceFactory.create(okHttpClientProvider)
        );
        this.userRepositoryProvider = UserRepository_Factory.create(
            apiServiceProvider,
            userDaoProvider
        );
    }

    @Override
    public UserRepository getUserRepository() {
        return userRepositoryProvider.get();
    }
}
```

### Provider Pattern в Dagger

```
┌─────────────────────────────────────────────────────────────────┐
│              PROVIDER PATTERN                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Provider<T> — фабрика, возвращающая экземпляр T                │
│                                                                 │
│  interface Provider<T> {                                        │
│      T get();  // Каждый вызов может вернуть новый или тот же   │
│  }                                                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    UNSCOPED                              │   │
│  │                                                         │   │
│  │  Provider<User> ──► get() → new User()                  │   │
│  │                 ──► get() → new User()  // Каждый раз   │   │
│  │                 ──► get() → new User()  // новый!       │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SCOPED (@Singleton)                   │   │
│  │                                                         │   │
│  │  DoubleCheck.provider(factory)                          │   │
│  │                                                         │   │
│  │  Provider<User> ──► get() → new User() ─┐               │   │
│  │                 ──► get() ──────────────┼─► same User   │   │
│  │                 ──► get() ──────────────┘               │   │
│  │                                                         │   │
│  │  DoubleCheck: thread-safe lazy initialization           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### KAPT vs KSP

| Аспект | KAPT | KSP (рекомендуется) |
|--------|------|---------------------|
| **Скорость** | Медленнее (стабы) | До 2x быстрее |
| **Kotlin support** | Через Java стабы | Нативная поддержка Kotlin |
| **Kotlin 2.0** | Ограниченная | Полная поддержка |
| **Hilt 2.57+** | Поддерживается | Рекомендуется |

```kotlin
// build.gradle.kts — настройка KSP
plugins {
    id("com.google.devtools.ksp") version "2.0.21-1.0.28"
    id("com.google.dagger.hilt.android")
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.57.1")
    ksp("com.google.dagger:hilt-compiler:2.57.1")  // KSP вместо KAPT
}
```

---

## Hilt Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│              HILT COMPONENT HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SingletonComponent                                      │   │
│  │  @Singleton                                              │   │
│  │  Lifecycle: Application onCreate → Application onDestroy │   │
│  │  Примеры: Retrofit, OkHttpClient, Room Database          │   │
│  └────────────────────────────┬────────────────────────────┘   │
│                               │                                 │
│              ┌────────────────┴────────────────┐                │
│              │                                 │                │
│              ▼                                 ▼                │
│  ┌───────────────────────┐      ┌───────────────────────┐      │
│  │ ServiceComponent      │      │ActivityRetainedComponent│     │
│  │ @ServiceScoped        │      │@ActivityRetainedScoped │      │
│  │ Service lifecycle     │      │Survives config changes │      │
│  └───────────────────────┘      └───────────┬───────────┘      │
│                                             │                   │
│                          ┌──────────────────┼──────────────┐   │
│                          │                  │              │   │
│                          ▼                  ▼              │   │
│             ┌─────────────────────┐  ┌─────────────┐       │   │
│             │  ViewModelComponent │  │ActivityComp │       │   │
│             │  @ViewModelScoped   │  │@ActivityScoped│      │   │
│             │  ViewModel lifecycle│  │Activity life│       │   │
│             │  SavedStateHandle   │  │             │       │   │
│             └─────────────────────┘  └──────┬──────┘       │   │
│                                             │              │   │
│                               ┌─────────────┴─────────────┐│   │
│                               │                           ││   │
│                               ▼                           ▼│   │
│                    ┌─────────────────┐         ┌─────────────┐ │
│                    │FragmentComponent│         │ ViewComponent│ │
│                    │@FragmentScoped  │         │ @ViewScoped  │ │
│                    │Fragment lifecycle│        │ View lifecycle││
│                    └────────┬────────┘         └─────────────┘ │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                         │
│                    │ViewWithFragment │                         │
│                    │   Component     │                         │
│                    └─────────────────┘                         │
│                                                                 │
│  ПРАВИЛО: Дочерний компонент имеет доступ к зависимостям       │
│           родительского, но НЕ наоборот                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Scopes и их использование

| Scope | Component | Lifecycle | Типичное использование |
|-------|-----------|-----------|----------------------|
| `@Singleton` | SingletonComponent | App lifetime | Retrofit, Database, SharedPrefs |
| `@ActivityRetainedScoped` | ActivityRetainedComponent | Survives rotation | Shared data across fragments |
| `@ViewModelScoped` | ViewModelComponent | ViewModel lifetime | Use cases, interactors |
| `@ActivityScoped` | ActivityComponent | Activity lifetime | Activity-specific helpers |
| `@FragmentScoped` | FragmentComponent | Fragment lifetime | Fragment-specific state |
| `@ViewScoped` | ViewComponent | View lifetime | Custom view dependencies |

### Default Bindings

Каждый компонент предоставляет default bindings:

```kotlin
// SingletonComponent
@ApplicationContext context: Context  // Application context

// ActivityComponent
@ActivityContext context: Context     // Activity context
activity: Activity                    // Current activity

// FragmentComponent
fragment: Fragment                    // Current fragment

// ViewModelComponent
savedStateHandle: SavedStateHandle    // From ViewModel factory
```

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle  // Auto-injected!
) : ViewModel() {

    // Получаем navigation arguments
    private val userId: String = savedStateHandle.get<String>("userId")!!
}
```

---

## Базовая настройка Hilt

### Gradle Setup (2025)

```kotlin
// build.gradle.kts (project level)
plugins {
    id("com.google.dagger.hilt.android") version "2.57.1" apply false
    id("com.google.devtools.ksp") version "2.0.21-1.0.28" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

android {
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    // Hilt core
    implementation("com.google.dagger:hilt-android:2.57.1")
    ksp("com.google.dagger:hilt-compiler:2.57.1")

    // Compose integration
    implementation("androidx.hilt:hilt-navigation-compose:1.3.0")

    // Testing
    testImplementation("com.google.dagger:hilt-android-testing:2.57.1")
    kspTest("com.google.dagger:hilt-compiler:2.57.1")
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.57.1")
    kspAndroidTest("com.google.dagger:hilt-compiler:2.57.1")
}
```

### Application

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt генерирует базовый класс и компонент
}
```

### Modules

```kotlin
// Network dependencies
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

// Database dependencies
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### @Binds vs @Provides

```kotlin
// @Provides — когда нужна кастомная логика создания
@Module
@InstallIn(SingletonComponent::class)
object AnalyticsModule {
    @Provides
    @Singleton
    fun provideAnalytics(@ApplicationContext context: Context): Analytics {
        return FirebaseAnalytics.getInstance(context)
    }
}

// @Binds — когда просто связываем интерфейс с реализацией (эффективнее)
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @Singleton
    abstract fun bindOrderRepository(impl: OrderRepositoryImpl): OrderRepository
}

// Реализация с @Inject constructor
class UserRepositoryImpl @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository {
    // ...
}
```

### Qualifiers

```kotlin
// Когда нужно различать зависимости одного типа
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default
}

// Использование
class UserRepository @Inject constructor(
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getUsers() = withContext(ioDispatcher) {
        // ...
    }
}
```

---

## Hilt + Jetpack Compose

### hiltViewModel()

```kotlin
// Новый артефакт (Hilt 1.3.0+)
// implementation("androidx.hilt:hilt-navigation-compose:1.3.0")

@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()  // Автоматическая инъекция
) {
    val users by viewModel.users.collectAsStateWithLifecycle()

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}
```

### Scoping to Navigation

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {

        // ViewModel scoped to this destination
        composable("home") {
            val viewModel: HomeViewModel = hiltViewModel()
            HomeScreen(viewModel, navController)
        }

        // ViewModel scoped to this destination
        composable("detail/{userId}") { backStackEntry ->
            val viewModel: DetailViewModel = hiltViewModel()
            // userId доступен через SavedStateHandle в ViewModel
            DetailScreen(viewModel)
        }

        // Shared ViewModel for wizard flow
        navigation(startDestination = "step1", route = "wizard") {
            composable("step1") {
                // Shared ViewModel scoped to "wizard" nav graph
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("wizard")
                }
                val sharedViewModel: WizardViewModel = hiltViewModel(parentEntry)
                Step1Screen(sharedViewModel, navController)
            }

            composable("step2") {
                val parentEntry = remember(it) {
                    navController.getBackStackEntry("wizard")
                }
                val sharedViewModel: WizardViewModel = hiltViewModel(parentEntry)
                Step2Screen(sharedViewModel, navController)
            }
        }
    }
}
```

### Assisted Injection (Hilt 2.56+)

Для runtime параметров, которые неизвестны при компиляции:

```kotlin
@HiltViewModel(assistedFactory = DetailViewModel.Factory::class)
class DetailViewModel @AssistedInject constructor(
    @Assisted private val userId: String,      // Runtime parameter
    @Assisted private val mode: ViewMode,      // Runtime parameter
    private val repository: UserRepository     // Injected by Hilt
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userId: String, mode: ViewMode): DetailViewModel
    }

    // ViewModel logic...
}

// Использование в Compose
@Composable
fun DetailScreen(userId: String, mode: ViewMode) {
    val viewModel = hiltViewModel<DetailViewModel>(
        creationCallback = { factory: DetailViewModel.Factory ->
            factory.create(userId, mode)
        }
    )

    // Screen content...
}
```

### Best Practices для Compose

```kotlin
// ✅ Хорошо: передавать данные и callbacks, не ViewModel
@Composable
fun UserList(
    users: List<User>,
    onUserClick: (User) -> Unit,
    onRefresh: () -> Unit
) {
    // Stateless composable, легко тестировать и preview
}

@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsStateWithLifecycle()

    UserList(
        users = users,
        onUserClick = viewModel::onUserClick,
        onRefresh = viewModel::refresh
    )
}

// ❌ Плохо: передавать ViewModel вниз
@Composable
fun UserList(viewModel: UserViewModel) {  // Сложно тестировать!
    val users by viewModel.users.collectAsStateWithLifecycle()
    // ...
}
```

---

## Multi-Module Architecture

### Regular Gradle Modules

```
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-MODULE STRUCTURE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  :app                                                           │
│  ├── @HiltAndroidApp                                            │
│  └── depends on: :feature:*, :core:*                            │
│                                                                 │
│  :core:network                                                  │
│  ├── NetworkModule (@InstallIn(SingletonComponent))             │
│  └── ApiService interface                                       │
│                                                                 │
│  :core:database                                                 │
│  ├── DatabaseModule (@InstallIn(SingletonComponent))            │
│  └── DAOs                                                       │
│                                                                 │
│  :core:data                                                     │
│  ├── RepositoryModule (@Binds)                                  │
│  └── Repository implementations                                 │
│                                                                 │
│  :feature:home                                                  │
│  ├── HomeViewModel (@HiltViewModel)                             │
│  └── HomeScreen                                                 │
│                                                                 │
│  :feature:profile                                               │
│  ├── ProfileViewModel (@HiltViewModel)                          │
│  └── ProfileScreen                                              │
│                                                                 │
│  Hilt автоматически собирает все @InstallIn модули              │
│  из транзитивных зависимостей                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
// :core:network/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService = // ...
}

// :feature:home/HomeViewModel.kt
// Hilt автоматически найдёт ApiService из :core:network
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val api: ApiService
) : ViewModel()
```

### Dynamic Feature Modules

Для Dynamic Feature Modules Hilt не может обработать annotations — нужен @EntryPoint:

```kotlin
// :app module — объявляем EntryPoint
@EntryPoint
@InstallIn(SingletonComponent::class)
interface FeatureModuleDependencies {
    fun apiService(): ApiService
    fun database(): AppDatabase
    fun analytics(): Analytics
}

// :feature:premium (Dynamic Feature Module)
// НЕ используем @AndroidEntryPoint!
class PremiumActivity : AppCompatActivity() {

    // Ручное получение зависимостей через EntryPoint
    private val dependencies: FeatureModuleDependencies by lazy {
        EntryPointAccessors.fromApplication(
            applicationContext,
            FeatureModuleDependencies::class.java
        )
    }

    private val apiService by lazy { dependencies.apiService() }
    private val database by lazy { dependencies.database() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Используем зависимости
    }
}

// Альтернатива: создать Dagger Component в feature module
@Component(dependencies = [FeatureModuleDependencies::class])
@FeatureScope
interface PremiumComponent {
    fun inject(activity: PremiumActivity)

    @Component.Builder
    interface Builder {
        fun dependencies(deps: FeatureModuleDependencies): Builder
        fun build(): PremiumComponent
    }
}
```

### Build Time Optimization

```properties
# gradle.properties

# Для deep multi-module projects (экспериментально)
android.defaults.enableExperimentalClasspathAggregation=true

# Incremental annotation processing
kapt.incremental.apt=true

# KSP (если используется)
ksp.incremental=true
```

---

## Testing с Hilt

### Unit Tests — Hilt НЕ нужен

```kotlin
// Unit tests: просто передаём mock'и в конструктор
class UserViewModelTest {

    private lateinit var viewModel: UserViewModel
    private val mockRepository = mockk<UserRepository>()

    @Before
    fun setup() {
        // Прямое создание без Hilt
        viewModel = UserViewModel(mockRepository)
    }

    @Test
    fun `loads users on init`() = runTest {
        // Given
        val users = listOf(User("1", "Alice"), User("2", "Bob"))
        coEvery { mockRepository.getUsers() } returns users

        // When
        viewModel = UserViewModel(mockRepository)

        // Then
        assertEquals(users, viewModel.users.value)
    }
}
```

### Instrumented Tests — @TestInstallIn

```kotlin
// Заменяет модуль для ВСЕХ тестов в test suite
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [NetworkModule::class]  // Заменяем production модуль
)
object FakeNetworkModule {

    @Provides
    @Singleton
    fun provideFakeApiService(): ApiService = FakeApiService()
}

// Fake implementation
class FakeApiService : ApiService {
    private val users = mutableListOf<User>()

    fun addUser(user: User) {
        users.add(user)
    }

    override suspend fun getUsers(): List<User> = users
}

// Тест
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class UserScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var fakeApi: FakeApiService  // Получаем Fake для настройки

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun displaysUsers() {
        // Given
        fakeApi.addUser(User("1", "Alice"))
        fakeApi.addUser(User("2", "Bob"))

        // Then
        composeRule.onNodeWithText("Alice").assertIsDisplayed()
        composeRule.onNodeWithText("Bob").assertIsDisplayed()
    }
}
```

### @UninstallModules + @BindValue — для одного теста

```kotlin
@HiltAndroidTest
@UninstallModules(AnalyticsModule::class)  // Убираем production модуль
class SpecificFeatureTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // ВАЖНО: инициализировать в field initializer, НЕ в @Before!
    @BindValue
    val mockAnalytics: Analytics = mockk(relaxed = true)

    @Test
    fun tracksScreenView() {
        // Тест с mock analytics
        verify { mockAnalytics.trackScreenView("Home") }
    }
}
```

### Compose UI Testing

```kotlin
@HiltAndroidTest
class UserScreenComposeTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createComposeRule()

    @Inject
    lateinit var userRepository: FakeUserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun showsLoadingState() {
        composeRule.setContent {
            UserScreen()
        }

        composeRule.onNodeWithTag("loading").assertIsDisplayed()
    }

    @Test
    fun showsUserList() {
        // Prepare data
        userRepository.setUsers(listOf(testUser))

        composeRule.setContent {
            UserScreen()
        }

        composeRule.waitUntilAtLeastOneExists(
            hasText(testUser.name),
            timeoutMillis = 5000
        )
    }
}
```

---

## Common Pitfalls

### 1. Overuse @Singleton

```kotlin
// ❌ Плохо: всё Singleton
@Singleton class UserSession           // Проблема: stale data
@Singleton class FormValidator         // Проблема: shared state
@Singleton class ScreenState           // Проблема: memory leak

// ✅ Хорошо: правильные scopes
@Singleton class Database              // OK: долгоживущий ресурс
@ViewModelScoped class UserSession     // OK: живёт с ViewModel
// Без scope class FormValidator       // OK: новый для каждого использования
```

### 2. Circular Dependencies

```kotlin
// ❌ Circular dependency — ошибка компиляции
class A @Inject constructor(private val b: B)
class B @Inject constructor(private val a: A)

// ✅ Решение 1: Provider
class A @Inject constructor(private val bProvider: Provider<B>) {
    fun doSomething() {
        bProvider.get().work()  // Lazy получение
    }
}

// ✅ Решение 2: Lazy
class A @Inject constructor(private val b: Lazy<B>) {
    fun doSomething() {
        b.get().work()  // Lazy инициализация
    }
}

// ✅ Решение 3: Рефакторинг (лучший вариант)
// Выделить общую логику в третий класс
```

### 3. Забыть @AndroidEntryPoint

```kotlin
// ❌ @Inject поля не инициализируются
class MainActivity : AppCompatActivity() {
    @Inject lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        analytics.track("screen_view")  // UninitializedPropertyAccessException!
    }
}

// ✅ Добавить @AndroidEntryPoint
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var analytics: Analytics
    // Теперь работает
}
```

### 4. @BindValue в @Before

```kotlin
// ❌ Плохо: @BindValue в @Before
@HiltAndroidTest
class MyTest {
    @BindValue
    lateinit var mockService: MyService  // lateinit!

    @Before
    fun setup() {
        mockService = mockk()  // Слишком поздно!
    }
}

// ✅ Хорошо: инициализировать сразу
@HiltAndroidTest
class MyTest {
    @BindValue
    val mockService: MyService = mockk(relaxed = true)  // Сразу!
}
```

### 5. Missing Qualifier

```kotlin
// ❌ Две зависимости одного типа без qualifier
@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
    // Ошибка: дублирующий binding!
}

// ✅ Используем qualifiers
@Qualifier annotation class IoDispatcher
@Qualifier annotation class MainDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}
```

### Сводная таблица

| Ошибка | Симптом | Решение |
|--------|---------|---------|
| Overuse @Singleton | Memory bloat, stale data | Правильный scope |
| Circular dependencies | Compile error | Provider, Lazy, или рефакторинг |
| Missing @AndroidEntryPoint | UninitializedProperty | Добавить аннотацию |
| @BindValue в @Before | Test fails | Инициализировать в field |
| Missing Qualifier | Duplicate binding error | Добавить @Qualifier |
| Field injection | Hard to test | Constructor injection |

---

## Migration: Dagger → Hilt

### Пошаговая стратегия

```
1. Обновить зависимости
   ─────────────────────
   Добавить Hilt plugin и dependencies
   Убедиться в совместимости версий

2. Application → @HiltAndroidApp
   ─────────────────────────────
   @HiltAndroidApp
   class MyApplication : Application()

3. Modules → добавить @InstallIn
   ──────────────────────────────
   @Module
   @InstallIn(SingletonComponent::class)
   object NetworkModule { ... }

4. Activities → @AndroidEntryPoint
   ────────────────────────────────
   @AndroidEntryPoint
   class MainActivity : AppCompatActivity()

5. Fragments → @AndroidEntryPoint
   ────────────────────────────────
   @AndroidEntryPoint
   class HomeFragment : Fragment()

6. ViewModels → @HiltViewModel
   ────────────────────────────
   @HiltViewModel
   class MainViewModel @Inject constructor(...) : ViewModel()

7. Удалить старые Component/SubComponent
   ──────────────────────────────────────
   Hilt генерирует их автоматически

8. Тесты → @HiltAndroidTest
   ─────────────────────────
   Обновить test setup
```

### Incremental Migration

Если полная миграция невозможна сразу:

```kotlin
// Сохраняем legacy Dagger component на переходный период
@HiltAndroidApp
class MyApplication : Application(), HasAndroidInjector {

    @Inject
    lateinit var androidInjector: DispatchingAndroidInjector<Any>

    // Legacy component для старых экранов
    lateinit var legacyComponent: LegacyAppComponent

    override fun onCreate() {
        super.onCreate()
        legacyComponent = DaggerLegacyAppComponent.create()
    }

    override fun androidInjector() = androidInjector
}
```

---

## Performance Considerations

### Build Time

| Фактор | Влияние | Оптимизация |
|--------|---------|-------------|
| KAPT vs KSP | KSP до 2x быстрее | Мигрировать на KSP |
| Количество модулей | Больше = дольше | Gradle build cache |
| Incremental builds | Важно для dev | `kapt.incremental.apt=true` |

### Runtime

| Фактор | Влияние | Оптимизация |
|--------|---------|-------------|
| Graph size | Startup time | Lazy initialization |
| Scoping | Memory usage | Правильные scopes |
| Provider calls | Negligible | — |

### Memory

```kotlin
// ❌ Singleton хранит Activity reference → утечка
@Singleton
class Analytics @Inject constructor(
    private val activity: Activity  // УТЕЧКА!
)

// ✅ Используем Application context
@Singleton
class Analytics @Inject constructor(
    @ApplicationContext private val context: Context
)
```

---

## Проверь себя

**1. В чём разница между @Provides и @Binds?**

<details>
<summary>Ответ</summary>

`@Provides` — для методов, которые создают зависимость с кастомной логикой:
```kotlin
@Provides
fun provideRetrofit(): Retrofit = Retrofit.Builder()...build()
```

`@Binds` — для связывания интерфейса с реализацией (эффективнее, меньше generated code):
```kotlin
@Binds
abstract fun bindRepository(impl: UserRepositoryImpl): UserRepository
```

Используйте `@Binds` когда возможно — он генерирует меньше кода.

</details>

**2. Почему ViewModelComponent не является дочерним ActivityComponent?**

<details>
<summary>Ответ</summary>

ViewModelComponent является дочерним **ActivityRetainedComponent**, а не ActivityComponent.

Причина: ViewModel переживает configuration changes (rotation), а ActivityComponent — нет.

```
ActivityRetainedComponent (survives rotation)
├── ActivityComponent (destroyed on rotation)
└── ViewModelComponent (survives rotation)
```

Это позволяет ViewModel сохранять зависимости при повороте экрана.

</details>

**3. Когда использовать @EntryPoint?**

<details>
<summary>Ответ</summary>

`@EntryPoint` нужен когда:

1. **Dynamic Feature Modules** — Hilt не может обработать annotations
2. **ContentProvider** — создаётся до Application
3. **Код вне Hilt** — legacy код, third-party libraries
4. **Custom injection** — когда @AndroidEntryPoint не подходит

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MyEntryPoint {
    fun getRepository(): UserRepository
}

// Использование
val entryPoint = EntryPointAccessors.fromApplication(context, MyEntryPoint::class.java)
val repo = entryPoint.getRepository()
```

</details>

---

## Связи

**DI основы:**
→ [[dependency-injection-fundamentals]] — базовые концепции DI, DIP, IoC

**Android DI:**
→ [[android-dependency-injection]] — обзор DI решений для Android
→ [[android-koin-deep-dive]] — альтернатива Hilt для KMP

**Архитектура:**
→ [[android-architecture-patterns]] — MVVM, Clean Architecture с Hilt
→ [[android-testing]] — тестирование с Hilt

---

## Источники

**Официальная документация:**
- [Hilt — Android Developers](https://developer.android.com/training/dependency-injection/hilt-android)
- [Hilt Components — dagger.dev](https://dagger.dev/hilt/components.html)
- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module)
- [Hilt Testing Guide](https://developer.android.com/training/dependency-injection/hilt-testing)

**Deep dives:**
- [Scoping in Android and Hilt — Manuel Vivo](https://medium.com/androiddevelopers/scoping-in-android-and-hilt-c2e5222317c0)
- [Using Hilt's ViewModelComponent](https://medium.com/androiddevelopers/using-hilts-viewmodelcomponent-53b46515c4f4)
- [Dagger 2 Generated Code — MindOrks](https://medium.com/mindorks/dagger-2-generated-code-9def1bebc44b)

---

*Проверено: 2026-01-29 | Hilt 2.57.1, KSP 2.0 | Актуально*
