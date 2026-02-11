---
title: "Koin Deep-dive: Kotlin-native DI для Android и KMP"
created: 2026-01-29
modified: 2026-01-29
type: deep-dive
area: android
confidence: high
cs-foundations: [dependency-injection, service-locator, kotlin-dsl, multiplatform]
tags:
  - topic/android
  - topic/kotlin
  - topic/dependency-injection
  - type/deep-dive
  - level/advanced
related:
  - "[[dependency-injection-fundamentals]]"
  - "[[android-dependency-injection]]"
  - "[[android-hilt-deep-dive]]"
  - "[[kotlin-multiplatform]]"
prerequisites:
  - "[[android-architecture-patterns]]"
  - "[[android-activity-lifecycle]]"
---

# Koin Deep-dive: Kotlin-native DI для Android и KMP

Koin — легковесный DI фреймворк на чистом Kotlin с DSL-based конфигурацией. Работает в runtime без code generation, поддерживает Kotlin Multiplatform.

> **Prerequisites:**
> - [[dependency-injection-fundamentals]] — базовые концепции DI
> - Знание Kotlin DSL
> - Опыт работы с Android/KMP

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Module** | Контейнер для определений зависимостей |
| **Definition** | Описание как создать зависимость |
| **single** | Singleton — один экземпляр на всё приложение |
| **factory** | Новый экземпляр при каждом запросе |
| **scoped** | Экземпляр привязан к scope |
| **Scope** | Область видимости зависимостей |
| **Qualifier** | Идентификатор для различения одинаковых типов |
| **get()** | Запрос зависимости из контейнера |
| **inject()** | Lazy-получение зависимости |

---

## Почему Koin

### Сравнение с Hilt

| Аспект | Koin 4.0 | Hilt 2.57 |
|--------|----------|-----------|
| **Проверка зависимостей** | Runtime | Compile-time |
| **Скорость сборки** | Быстрее (нет codegen) | Медленнее |
| **App startup** | Чуть медленнее | Быстрее |
| **Kotlin Multiplatform** | ✅ Полная поддержка | ❌ Только Android |
| **Сложность** | Низкая | Средняя |
| **Learning curve** | Простой DSL | Dagger концепции |
| **Boilerplate** | Минимум | Минимум |

### Когда выбрать Koin

```
┌─────────────────────────────────────────────────────────────────┐
│              KOIN: ИДЕАЛЬНЫЕ СЦЕНАРИИ                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ Kotlin Multiplatform проект                                  │
│     • Shared code для Android + iOS                             │
│     • Koin — единственный DI с полной KMP поддержкой            │
│                                                                 │
│  ✅ Быстрый старт / прототип                                     │
│     • Минимальная настройка                                     │
│     • Нет annotation processing                                 │
│     • Меньше времени на setup                                   │
│                                                                 │
│  ✅ Маленькая / средняя команда                                  │
│     • Простой DSL, быстро освоить                               │
│     • Меньше "магии"                                            │
│                                                                 │
│  ✅ Compose-first приложения                                     │
│     • Нативная интеграция с Compose                             │
│     • koinViewModel() из коробки                                │
│                                                                 │
│  ⚠️ С осторожностью для:                                        │
│     • Enterprise-scale apps (runtime ошибки)                    │
│     • Проектов с жёсткими требованиями к startup time           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Koin Architecture

### Как работает под капотом

```
┌─────────────────────────────────────────────────────────────────┐
│              KOIN INTERNALS                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  startKoin { modules(...) }                                     │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 KoinApplication                          │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              Koin Instance                       │   │   │
│  │  │                                                 │   │   │
│  │  │  ┌─────────────────────────────────────────┐   │   │   │
│  │  │  │        InstanceRegistry                  │   │   │   │
│  │  │  │                                         │   │   │   │
│  │  │  │  Map<Key, BeanDefinition<*>>            │   │   │   │
│  │  │  │                                         │   │   │   │
│  │  │  │  Key = Type + Qualifier                 │   │   │   │
│  │  │  │  Value = factory lambda + scope info    │   │   │   │
│  │  │  │                                         │   │   │   │
│  │  │  └─────────────────────────────────────────┘   │   │   │
│  │  │                                                 │   │   │
│  │  │  ┌─────────────────────────────────────────┐   │   │   │
│  │  │  │         ScopeRegistry                    │   │   │   │
│  │  │  │                                         │   │   │   │
│  │  │  │  Root Scope (singleton lifetime)        │   │   │   │
│  │  │  │    └── Child Scopes (custom lifetime)   │   │   │   │
│  │  │  │                                         │   │   │   │
│  │  │  └─────────────────────────────────────────┘   │   │   │
│  │  │                                                 │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  При запросе get<T>():                                          │
│  1. Найти BeanDefinition по типу T                              │
│  2. Проверить scope (есть ли закэшированный экземпляр)          │
│  3. Создать экземпляр через factory lambda                      │
│  4. Рекурсивно разрешить зависимости через get()                │
│  5. Закэшировать если scoped                                    │
│                                                                 │
│  ОТЛИЧИЕ ОТ SERVICE LOCATOR:                                    │
│  Koin технически использует Service Locator pattern, но:        │
│  • Module DSL декларативен                                      │
│  • Зависимости описаны явно                                     │
│  • Граф проверяется через verify()                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Runtime vs Compile-time

```kotlin
// Koin: Runtime resolution
val userRepository: UserRepository = get()
// Если UserRepository не зарегистрирован → RuntimeException при вызове

// Hilt: Compile-time resolution
@Inject lateinit var userRepository: UserRepository
// Если UserRepository не зарегистрирован → Ошибка компиляции
```

**Mitigation:** Используйте `verify()` или `checkModules()` в тестах.

---

## Базовая настройка

### Gradle Setup (Koin 4.0)

```kotlin
// build.gradle.kts (app module)
dependencies {
    // Core
    implementation("io.insert-koin:koin-core:4.0.0")

    // Android
    implementation("io.insert-koin:koin-android:4.0.0")

    // Compose
    implementation("io.insert-koin:koin-compose:4.0.0")
    implementation("io.insert-koin:koin-compose-viewmodel:4.0.0")

    // Optimized startup (optional)
    implementation("io.insert-koin:koin-androidx-startup:4.0.0")

    // Testing
    testImplementation("io.insert-koin:koin-test:4.0.0")
    testImplementation("io.insert-koin:koin-test-junit5:4.0.0")
}
```

### Application Setup

```kotlin
// Standard approach
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            // Android context
            androidContext(this@MyApplication)

            // Logging
            androidLogger(Level.DEBUG)

            // Modules
            modules(
                networkModule,
                databaseModule,
                repositoryModule,
                viewModelModule
            )
        }
    }
}

// Optimized startup (Koin 4.0) — до 40% быстрее
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        onKoinStartup {
            androidContext(this@MyApplication)
            modules(appModules)
        }
    }
}
```

---

## Koin DSL

### Module Definition

```kotlin
// Базовые definitions
val networkModule = module {

    // single — один экземпляр на всё приложение (Singleton)
    single {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    // single с типом (для интерфейсов)
    single<ApiService> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get())  // Получаем OkHttpClient
            .build()
            .create(ApiService::class.java)
    }

    // factory — новый экземпляр каждый раз
    factory { RequestBuilder(get()) }
}

val repositoryModule = module {

    // Зависимости разрешаются через get()
    single<UserRepository> {
        UserRepositoryImpl(
            api = get(),      // ApiService
            dao = get(),      // UserDao
            dispatcher = get(named("io"))  // Именованный dispatcher
        )
    }
}

val viewModelModule = module {

    // viewModel — специальный scope для ViewModel
    viewModel { HomeViewModel(get()) }

    // viewModel с параметрами
    viewModel { params ->
        DetailViewModel(
            userId = params.get(),  // Runtime параметр
            repository = get()
        )
    }
}
```

### Constructor DSL (Koin 3.3+)

```kotlin
// Краткий синтаксис без lambda
val module = module {
    // Вместо single { UserRepository(get(), get()) }
    singleOf(::UserRepositoryImpl) { bind<UserRepository>() }

    // Вместо factory { RequestBuilder(get()) }
    factoryOf(::RequestBuilder)

    // ViewModel
    viewModelOf(::HomeViewModel)
}

class UserRepositoryImpl(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository
```

### Qualifiers

```kotlin
val dispatcherModule = module {
    // Named qualifiers
    single(named("io")) { Dispatchers.IO }
    single(named("main")) { Dispatchers.Main }
    single(named("default")) { Dispatchers.Default }
}

// Использование
class UserRepository(
    @InjectedParam private val ioDispatcher: CoroutineDispatcher
) {
    // ...
}

// Или через get()
single {
    UserRepository(
        dispatcher = get(named("io"))
    )
}

// Custom qualifier
val ApiQualifier = named("api")
val DatabaseQualifier = named("database")

module {
    single(ApiQualifier) { provideApiLogger() }
    single(DatabaseQualifier) { provideDatabaseLogger() }
}
```

### Includes & Module Composition

```kotlin
// Разделение модулей
val dataModule = module {
    includes(networkModule, databaseModule)

    single<UserRepository> { UserRepositoryImpl(get(), get()) }
}

// Условная загрузка
val analyticsModule = module {
    if (BuildConfig.DEBUG) {
        single<Analytics> { DebugAnalytics() }
    } else {
        single<Analytics> { FirebaseAnalytics(get()) }
    }
}

// Lazy modules (загрузка по требованию)
val featureModule = lazyModule {
    single { FeatureRepository(get()) }
    viewModelOf(::FeatureViewModel)
}

// Загрузка lazy module
fun loadFeature() {
    loadKoinModules(featureModule)
}
```

---

## Scopes

### Built-in Scopes

```kotlin
// Root scope — singleton lifetime
single { Database() }  // Живёт всё время приложения

// No scope — factory
factory { RequestBuilder() }  // Новый экземпляр каждый раз

// Custom scope
scope<UserSession> {
    scoped { UserPreferences(get()) }  // Живёт пока живёт scope
}
```

### Android Scopes

```kotlin
// Activity scope
class MainActivity : AppCompatActivity() {

    // Scope привязан к Activity lifecycle
    private val activityScope = lifecycleScope

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Создаём scope для Activity
        val scope = getKoin().createScope<MainActivity>()

        // Получаем scoped зависимость
        val prefs: ActivityPreferences = scope.get()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Scope автоматически закрывается с Activity
    }
}

// Определение
val activityModule = module {
    scope<MainActivity> {
        scoped { ActivityPreferences(get()) }
        scoped { ActivityAnalytics(get()) }
    }
}
```

### Custom Scopes

```kotlin
// Scope для user session
val sessionModule = module {
    scope(named("userSession")) {
        scoped { UserSession(get()) }
        scoped { UserPreferences(get()) }
        scoped { UserAnalytics(get()) }
    }
}

// Управление scope
class SessionManager(private val koin: Koin) {

    private var sessionScope: Scope? = null

    fun login(userId: String) {
        // Создаём scope при логине
        sessionScope = koin.createScope("session_$userId", named("userSession"))
    }

    fun logout() {
        // Закрываем scope при логауте
        sessionScope?.close()
        sessionScope = null
    }

    fun <T : Any> get(clazz: KClass<T>): T {
        return sessionScope?.get(clazz)
            ?: throw IllegalStateException("No active session")
    }
}
```

---

## Koin + Compose

### koinViewModel()

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = koinViewModel()  // Автоматическая инъекция
) {
    val users by viewModel.users.collectAsStateWithLifecycle()

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}

// ViewModel definition
val viewModelModule = module {
    viewModelOf(::UserViewModel)
}

class UserViewModel(
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

### ViewModel с параметрами

```kotlin
// ViewModel с runtime параметрами
class DetailViewModel(
    private val userId: String,
    private val repository: UserRepository
) : ViewModel() {
    // ...
}

// Definition с parametersOf
val viewModelModule = module {
    viewModel { params ->
        DetailViewModel(
            userId = params.get(),
            repository = get()
        )
    }
}

// Использование в Compose
@Composable
fun DetailScreen(userId: String) {
    val viewModel: DetailViewModel = koinViewModel(
        parameters = { parametersOf(userId) }
    )
    // ...
}
```

### Shared ViewModel

```kotlin
// Shared ViewModel для нескольких экранов
@Composable
fun WizardFlow(navController: NavController) {
    // ViewModel shared между step1 и step2
    val sharedViewModel: WizardViewModel = koinViewModel()

    NavHost(navController, startDestination = "step1") {
        composable("step1") {
            Step1Screen(
                viewModel = sharedViewModel,
                onNext = { navController.navigate("step2") }
            )
        }
        composable("step2") {
            Step2Screen(
                viewModel = sharedViewModel,
                onSubmit = { /* ... */ }
            )
        }
    }
}
```

### Koin Compose Multiplatform

```kotlin
// Compose Multiplatform с Koin
@Composable
fun App() {
    KoinApplication(application = {
        modules(commonModule, platformModule)
    }) {
        MaterialTheme {
            MainScreen()
        }
    }
}

// Общий модуль (commonMain)
val commonModule = module {
    single<UserRepository> { UserRepositoryImpl(get()) }
    viewModelOf(::MainViewModel)
}

// Platform-specific (androidMain / iosMain)
expect val platformModule: Module
```

---

## Kotlin Multiplatform

### Project Structure

```
┌─────────────────────────────────────────────────────────────────┐
│              KMP + KOIN STRUCTURE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  shared/                                                        │
│  ├── commonMain/                                                │
│  │   └── kotlin/                                                │
│  │       ├── di/                                                │
│  │       │   ├── CommonModule.kt      ← Общие зависимости       │
│  │       │   └── PlatformModule.kt    ← expect declarations     │
│  │       ├── data/                                              │
│  │       │   └── UserRepository.kt    ← Общий код               │
│  │       └── domain/                                            │
│  │           └── User.kt                                        │
│  │                                                              │
│  ├── androidMain/                                               │
│  │   └── kotlin/                                                │
│  │       └── di/                                                │
│  │           └── PlatformModule.kt    ← actual Android          │
│  │                                                              │
│  └── iosMain/                                                   │
│      └── kotlin/                                                │
│          └── di/                                                │
│              └── PlatformModule.kt    ← actual iOS              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Common Module

```kotlin
// commonMain/di/CommonModule.kt
val commonModule = module {
    // Общие зависимости (не platform-specific)
    single { Json { ignoreUnknownKeys = true } }

    // Repository зависит от platform-specific HttpClient
    single<UserRepository> {
        UserRepositoryImpl(
            httpClient = get(),
            json = get()
        )
    }

    // ViewModel (multiplatform с koin-core-viewmodel)
    viewModelOf(::UserViewModel)
}
```

### Platform Module (expect/actual)

```kotlin
// commonMain/di/PlatformModule.kt
expect val platformModule: Module

// androidMain/di/PlatformModule.kt
actual val platformModule = module {
    single {
        HttpClient(Android) {
            install(ContentNegotiation) {
                json(get())
            }
        }
    }

    single<DataStore<Preferences>> {
        createDataStore(androidContext())
    }
}

// iosMain/di/PlatformModule.kt
actual val platformModule = module {
    single {
        HttpClient(Darwin) {
            install(ContentNegotiation) {
                json(get())
            }
        }
    }

    single<DataStore<Preferences>> {
        createDataStore(NSUserDefaults.standardUserDefaults)
    }
}
```

### Initialization

```kotlin
// Android — MainActivity или Application
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        startKoin {
            androidContext(this@MainActivity)
            modules(commonModule, platformModule)
        }

        setContent {
            App()
        }
    }
}

// iOS — iOSMain entry point
fun initKoin() {
    startKoin {
        modules(commonModule, platformModule)
    }
}

// Swift side
@main
struct iOSApp: App {
    init() {
        KoinKt.doInitKoin()
    }
    // ...
}
```

### Pattern: Interface + Platform Implementations

```kotlin
// commonMain — интерфейс
interface PlatformLogger {
    fun log(message: String)
}

// commonMain — module
val commonModule = module {
    single<UserService> {
        UserServiceImpl(logger = get())  // PlatformLogger будет injected
    }
}

// androidMain
actual val platformModule = module {
    single<PlatformLogger> { AndroidLogger() }
}

class AndroidLogger : PlatformLogger {
    override fun log(message: String) {
        Log.d("App", message)
    }
}

// iosMain
actual val platformModule = module {
    single<PlatformLogger> { IOSLogger() }
}

class IOSLogger : PlatformLogger {
    override fun log(message: String) {
        NSLog(message)
    }
}
```

---

## Testing

### Configuration Verification

```kotlin
// verify() — быстрая проверка конфигурации (рекомендуется)
class KoinModulesTest {

    @Test
    fun `verify all modules`() {
        commonModule.verify(
            extraTypes = listOf(
                SavedStateHandle::class,
                CoroutineDispatcher::class
            )
        )
    }
}

// checkModules() — полная проверка с созданием экземпляров
class KoinCheckModulesTest : KoinTest {

    @Test
    fun `check all modules`() {
        koinApplication {
            modules(commonModule, testPlatformModule)
            checkModules {
                // Для definitions с параметрами
                withInstance<String>("testUserId")
                withInstance(Dispatchers.Unconfined)
            }
        }
    }
}
```

### Unit Tests

```kotlin
class UserViewModelTest : KoinTest {

    // Mock module
    private val testModule = module {
        single<UserRepository> { mockk(relaxed = true) }
        viewModelOf(::UserViewModel)
    }

    @BeforeEach
    fun setup() {
        startKoin { modules(testModule) }
    }

    @AfterEach
    fun teardown() {
        stopKoin()
    }

    @Test
    fun `loads users on init`() = runTest {
        // Given
        val mockRepo: UserRepository = get()
        val users = listOf(User("1", "Alice"))
        coEvery { mockRepo.getUsers() } returns users

        // When
        val viewModel: UserViewModel = get()

        // Then
        assertEquals(users, viewModel.users.value)
    }
}
```

### Mock Injection

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(repositoryModule)
    }

    @get:Rule
    val mockProvider = MockProviderRule.create { clazz ->
        mockkClass(clazz)
    }

    @Test
    fun `fetches users from api`() = runTest {
        // Declare mock on the fly
        val mockApi = declareMock<ApiService> {
            coEvery { getUsers() } returns listOf(testUser)
        }

        val repository: UserRepository by inject()

        val result = repository.getUsers()

        assertEquals(listOf(testUser), result)
        coVerify { mockApi.getUsers() }
    }
}
```

### Instrumented Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    private val testModule = module {
        single<UserRepository> { FakeUserRepository() }
        viewModelOf(::UserViewModel)
    }

    @Before
    fun setup() {
        // Load test module before activity starts
        loadKoinModules(testModule)
    }

    @After
    fun teardown() {
        unloadKoinModules(testModule)
    }

    @Test
    fun displaysUserList() {
        // Test with FakeUserRepository
        onView(withText("Alice")).check(matches(isDisplayed()))
    }
}
```

### Compose UI Tests

```kotlin
class UserScreenTest {

    @get:Rule
    val composeRule = createComposeRule()

    private val fakeRepository = FakeUserRepository()

    private val testModule = module {
        single<UserRepository> { fakeRepository }
        viewModelOf(::UserViewModel)
    }

    @Before
    fun setup() {
        startKoin { modules(testModule) }
    }

    @After
    fun teardown() {
        stopKoin()
    }

    @Test
    fun showsUserList() {
        // Prepare data
        fakeRepository.setUsers(listOf(User("1", "Alice")))

        composeRule.setContent {
            UserScreen()
        }

        composeRule.onNodeWithText("Alice").assertIsDisplayed()
    }
}
```

---

## Common Pitfalls

### 1. Missing Dependency

```kotlin
// ❌ UserDao не зарегистрирован
val module = module {
    single { UserRepository(get()) }  // get<UserDao>() fails at runtime!
}

// ✅ Зарегистрировать все зависимости
val module = module {
    single { provideDatabase().userDao() }
    single { UserRepository(get()) }
}

// ✅ Использовать verify() в тестах
@Test
fun `verify modules`() {
    module.verify()  // Поймает ошибку
}
```

### 2. Circular Dependency

```kotlin
// ❌ Circular dependency
val module = module {
    single { A(get()) }  // A depends on B
    single { B(get()) }  // B depends on A → StackOverflow!
}

// ✅ Использовать Lazy
val module = module {
    single { A(lazy { get<B>() }) }
    single { B(get()) }
}

class A(private val bLazy: Lazy<B>)
```

### 3. Scope Mismatch

```kotlin
// ❌ Scoped зависимость вне scope
val module = module {
    scope<MainActivity> {
        scoped { ActivityHelper() }
    }
}

class SomeClass : KoinComponent {
    val helper: ActivityHelper = get()  // Fails: no scope!
}

// ✅ Получать через scope
class MainActivity : AppCompatActivity(), AndroidScopeComponent {
    override val scope: Scope by activityScope()

    val helper: ActivityHelper by inject()  // OK: scope доступен
}
```

### 4. Забыть stopKoin() в тестах

```kotlin
// ❌ Koin не остановлен между тестами
class Test1 : KoinTest {
    @Before fun setup() { startKoin { modules(module1) } }
    @Test fun test() { /* ... */ }
    // Нет stopKoin()!
}

class Test2 : KoinTest {
    @Before fun setup() { startKoin { modules(module2) } }
    // Fails: Koin already started!
}

// ✅ Всегда stopKoin()
class Test1 : KoinTest {
    @Before fun setup() { startKoin { modules(module1) } }
    @After fun teardown() { stopKoin() }
    @Test fun test() { /* ... */ }
}
```

### 5. Overuse of get() in Composables

```kotlin
// ❌ get() каждый раз при recomposition
@Composable
fun UserScreen() {
    val repository: UserRepository = get()  // Called on every recomposition!
    // ...
}

// ✅ Использовать koinViewModel или remember
@Composable
fun UserScreen(
    viewModel: UserViewModel = koinViewModel()
) {
    // ViewModel создаётся один раз
}

// Или для non-ViewModel
@Composable
fun UserScreen() {
    val repository: UserRepository = remember { get() }
}
```

### Сводная таблица

| Ошибка | Симптом | Решение |
|--------|---------|---------|
| Missing dependency | `NoBeanDefFoundException` | verify(), зарегистрировать |
| Circular dependency | StackOverflow | Lazy injection |
| Scope mismatch | `NoScopeFoundException` | Правильный scope |
| Koin not stopped | Test fails | stopKoin() в @After |
| get() in Composable | Performance | koinViewModel, remember |

---

## Koin vs Hilt: Decision Guide

```
┌─────────────────────────────────────────────────────────────────┐
│              КОГДА ВЫБРАТЬ KOIN                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Вопрос                              Koin        Hilt           │
│  ────────────────────────────────────────────────────────────   │
│  Kotlin Multiplatform?               ✅ Yes      ❌ No          │
│                                                                 │
│  Важна скорость сборки?              ✅ Faster   ⚠️ Slower      │
│                                                                 │
│  Enterprise-scale app?               ⚠️ Runtime  ✅ Compile     │
│                                                                 │
│  Команда знакома с Dagger?           —          ✅ Yes          │
│                                                                 │
│  Быстрый старт / прототип?           ✅ Yes      —              │
│                                                                 │
│  Критичен app startup time?          ⚠️ Slower  ✅ Faster       │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  РЕКОМЕНДАЦИЯ:                                                  │
│                                                                 │
│  • KMP проект → Koin (единственный вариант)                     │
│  • Android-only + large team → Hilt (compile-time safety)       │
│  • Small/medium project → Koin (проще, быстрее)                 │
│  • Jetpack-heavy → Hilt (глубокая интеграция)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

**1. В чём главное отличие Koin от Hilt?**

<details>
<summary>Ответ</summary>

**Koin** — runtime DI, ошибки обнаруживаются при запуске приложения.
**Hilt** — compile-time DI, ошибки обнаруживаются при компиляции.

Koin не использует annotation processing и code generation, работает через Kotlin DSL и Service Locator pattern под капотом.

</details>

**2. Как защититься от runtime ошибок в Koin?**

<details>
<summary>Ответ</summary>

Использовать `verify()` или `checkModules()` в тестах:

```kotlin
@Test
fun `verify all modules`() {
    module.verify()
}

@Test
fun `check all modules`() {
    koinApplication {
        modules(appModules)
        checkModules()
    }
}
```

Это поймает отсутствующие зависимости до production.

</details>

**3. Почему Koin — единственный вариант для KMP?**

<details>
<summary>Ответ</summary>

Hilt/Dagger используют annotation processing (KAPT/KSP), который работает только для JVM/Android.

Koin:
- Чистый Kotlin без code generation
- Не требует platform-specific tooling
- Работает на iOS, Android, JS, Desktop, WASM

</details>

---

## Связь с другими темами

**[[dependency-injection-fundamentals]]** — Koin реализует паттерн Service Locator с DI-подобным DSL API, и понимание разницы между true DI (constructor injection) и Service Locator критично для оценки архитектурных компромиссов Koin. Базовые концепции IoC, Composition Root и lifetime management объясняют, почему Koin работает иначе, чем Dagger/Hilt. Обязательно начинайте с теоретических основ DI.

**[[android-dependency-injection]]** — Обзорная статья по DI решениям для Android даёт общую картину экосистемы (Dagger, Hilt, Koin, Kodein, kotlin-inject) и помогает понять позиционирование Koin как наиболее простого в освоении runtime-фреймворка. Сравнительная таблица фреймворков из обзора дополняет детальный анализ Koin в этой статье. Рекомендуется прочитать обзор перед погружением в конкретный фреймворк.

**[[android-hilt-deep-dive]]** — Hilt является главной альтернативой Koin для Android-проектов, предлагая compile-time safety вместо runtime resolution. Понимание trade-off между простотой Koin (нет annotation processing, быстрая сборка) и надёжностью Hilt (ошибки при компиляции, не в runtime) — ключевой вопрос при выборе DI фреймворка для проекта. Изучайте оба фреймворка для осознанного выбора.

**[[kotlin-multiplatform]]** — Koin является одним из наиболее зрелых DI решений для Kotlin Multiplatform, поддерживая все KMP таргеты (Android, iOS, Desktop, Web, WASM) без platform-specific tooling. Паттерны использования Koin в KMP (expect/actual modules, platform-specific scopes) напрямую связаны с архитектурой KMP приложений. После освоения Koin изучайте KMP для применения DI в мультиплатформенных проектах.

---

## Источники и дальнейшее чтение

**Официальная документация:**
- [Koin Official Documentation](https://insert-koin.io/docs/quickstart/android/)
- [Koin KMP Guide](https://insert-koin.io/docs/reference/koin-mp/kmp/)
- [Koin Testing](https://insert-koin.io/docs/reference/koin-test/testing/)

**Релизы и roadmap:**
- [Koin 4.0 Official Release](https://blog.insert-koin.io/koin-4-0-official-release-f4827bbcfce3)
- [Koin 2025 Roadmap](https://blog.insert-koin.io/koin-framework-2025-roadmap-from-4-0-to-future-milestones-68b0558e56a9)

### Книги

- **Moskala M.** *Effective Kotlin* (2021) — лучшие практики проектирования Kotlin-кода, включая паттерны управления зависимостями и DSL-конструкции, используемые в Koin
- **Bloch J.** *Effective Java* (2018) — фундаментальные принципы проектирования, включая Favor composition over inheritance и DI паттерны, лежащие в основе Koin
- **Meier R.** *Professional Android* (2022) — практическое руководство по архитектуре Android-приложений с интеграцией DI фреймворков

---

*Проверено: 2026-01-29 | Koin 4.0 | Актуально*
