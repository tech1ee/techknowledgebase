---
title: "Manual DI и альтернативные фреймворки"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/android
  - topic/kotlin
  - topic/dependency-injection
  - type/deep-dive
  - level/intermediate
related:
  - "[[dependency-injection-fundamentals]]"
  - "[[android-dagger-deep-dive]]"
  - "[[android-metro-deep-dive]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-architecture-patterns]]"
---

# Manual DI & Alternative Frameworks

## TL;DR

**Manual DI** — dependency injection без фреймворков, используя containers и factories. Рекомендуется Google для простых приложений. Даёт полный контроль, но требует много boilerplate в больших проектах. **Anvil** — расширение Dagger от Square для multi-module проектов, теперь в **maintenance mode** (июль 2025) — рекомендуется мигрировать на Metro. **Toothpick** — scope-based DI, больше не активно развивается.

---

## ЧАСТЬ 1: Manual DI

### Почему Manual DI

```kotlin
// ПРОБЛЕМА: Жёсткие зависимости
class UserRepository {
    private val api = RetrofitClient.create()  // Жёсткая связь
    private val db = RoomDatabase.get()        // Жёсткая связь
}

// РЕШЕНИЕ: Constructor Injection
class UserRepository(
    private val api: UserApi,
    private val db: UserDatabase
)

// Но КТО создаёт UserRepository и его зависимости?
// Ответ: Composition Root (Container / Factory)
```

### Когда использовать Manual DI

| Сценарий | Manual DI | Framework |
|----------|-----------|-----------|
| **Простое приложение** | ✅ Идеально | Overkill |
| **Обучение DI** | ✅ Понимание основ | Магия |
| **100+ классов** | ⚠️ Много boilerplate | ✅ |
| **Multi-module** | ⚠️ Сложно | ✅ |
| **Тестирование** | ✅ Просто | ✅ |

### Архитектура Manual DI

```
┌─────────────────────────────────────────────────────────────┐
│                    MANUAL DI ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │  Application    │  ◀── Composition Root                 │
│  │  (создаёт       │                                       │
│  │   Container)    │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ владеет                                         │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ AppContainer    │  ◀── Держит singleton-ы               │
│  │                 │      Создаёт зависимости              │
│  │ • userRepo      │                                       │
│  │ • analytics     │                                       │
│  │ • httpClient    │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ предоставляет                                   │
│           ▼                                                 │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │   Activities    │      │   ViewModels    │             │
│  │   Fragments     │      │   Services      │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │          Flow Containers                │               │
│  │  LoginContainer, CheckoutContainer...   │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Практическое использование

#### 1. Базовый AppContainer

```kotlin
// AppContainer — держит все зависимости приложения
class AppContainer(private val context: Context) {

    // Lazy singleton-ы
    val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val userApi: UserApi by lazy {
        retrofit.create(UserApi::class.java)
    }

    val database: AppDatabase by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }

    // Repositories
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(userApi, database.userDao())
    }

    val analyticsRepository: AnalyticsRepository by lazy {
        AnalyticsRepositoryImpl()
    }
}
```

#### 2. Application

```kotlin
class MyApp : Application() {

    // Composition Root — единственное место создания контейнера
    val appContainer by lazy { AppContainer(this) }

    override fun onCreate() {
        super.onCreate()
        // Инициализация eager зависимостей если нужно
        // appContainer.analytics.init()
    }
}

// Extension для удобного доступа
val Context.appContainer: AppContainer
    get() = (applicationContext as MyApp).appContainer
```

#### 3. Factory для ViewModels

```kotlin
// Factory создаёт ViewModel с зависимостями
class UserViewModelFactory(
    private val userRepository: UserRepository
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            return UserViewModel(userRepository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Использование в Activity
class UserActivity : AppCompatActivity() {

    private val viewModel by viewModels<UserViewModel> {
        UserViewModelFactory(appContainer.userRepository)
    }
}
```

#### 4. Flow Containers (Scoped)

```kotlin
// Container для login flow
class LoginContainer(private val appContainer: AppContainer) {

    // Зависимости живут только пока жив LoginContainer
    val loginValidator by lazy { LoginValidator() }

    val loginUseCase by lazy {
        LoginUseCase(
            userApi = appContainer.userApi,
            validator = loginValidator
        )
    }

    val loginViewModel by lazy {
        LoginViewModel(loginUseCase)
    }
}

// Использование
class LoginActivity : AppCompatActivity() {

    // Создаём container при старте flow
    private var loginContainer: LoginContainer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loginContainer = LoginContainer(appContainer)
        val viewModel = loginContainer!!.loginViewModel
    }

    override fun onDestroy() {
        super.onDestroy()
        // Очищаем container
        loginContainer = null
    }
}
```

#### 5. Activity/Fragment с Manual DI

```kotlin
class UserFragment : Fragment() {

    // Доступ к зависимостям через container
    private val userRepository: UserRepository
        get() = requireContext().appContainer.userRepository

    // Или передаём через arguments/factory
    companion object {
        fun newInstance(): UserFragment {
            return UserFragment()
        }
    }

    private val viewModel by viewModels<UserViewModel> {
        UserViewModelFactory(userRepository)
    }
}
```

#### 6. Организация в Multi-Module

```kotlin
// core/di/CoreContainer.kt
class CoreContainer(context: Context) {
    val httpClient: OkHttpClient by lazy { ... }
    val database: AppDatabase by lazy { ... }
}

// feature-user/di/UserContainer.kt
class UserContainer(private val core: CoreContainer) {
    val userApi: UserApi by lazy { ... }
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(userApi, core.database.userDao())
    }
}

// feature-orders/di/OrdersContainer.kt
class OrdersContainer(private val core: CoreContainer) {
    val ordersApi: OrdersApi by lazy { ... }
    val ordersRepository: OrdersRepository by lazy { ... }
}

// app/di/AppContainer.kt
class AppContainer(context: Context) {
    val core = CoreContainer(context)
    val user = UserContainer(core)
    val orders = OrdersContainer(core)
}
```

---

### Проблемы Manual DI

#### 1. Boilerplate

```kotlin
// Много повторяющегося кода
val viewModelFactory = UserViewModelFactory(
    userRepository = appContainer.userRepository,
    analyticsRepository = appContainer.analyticsRepository,
    settingsRepository = appContainer.settingsRepository,
    // ... ещё 10 зависимостей
)
```

#### 2. Управление lifecycle

```kotlin
// Нужно вручную очищать scoped containers
override fun onDestroy() {
    super.onDestroy()
    loginContainer = null  // Забыл — memory leak!
}
```

#### 3. Нет compile-time проверок

```kotlin
// Ошибка обнаружится только в runtime
class UserViewModel(
    private val userRepository: UserRepository,
    private val analytics: Analytics  // Забыли добавить в Container!
)
```

---

### Best Practices для Manual DI

1. **Composition Root в Application** — единственное место создания контейнера
2. **Lazy initialization** — создавать зависимости по требованию
3. **Flow Containers** — для scoped зависимостей
4. **Factory pattern** — для ViewModels и параметризованных объектов
5. **Extension functions** — для удобного доступа к контейнеру

---

## ЧАСТЬ 2: Anvil

### Что такое Anvil

**Anvil** — Kotlin compiler plugin от Square для упрощения Dagger в multi-module проектах. Автоматически генерирует и мержит Dagger modules.

> **ВАЖНО (Июль 2025):** Anvil переходит в **maintenance mode**. Square рекомендует мигрировать на **Metro**.

### Проблема которую решает Anvil

```kotlin
// БЕЗ ANVIL: Нужно вручную мержить modules
@Component(modules = [
    NetworkModule::class,
    DatabaseModule::class,
    UserModule::class,
    OrdersModule::class,
    AnalyticsModule::class,
    // ... ещё 50 modules из разных feature modules
])
interface AppComponent

// С ANVIL: Автоматический merge
@MergeComponent(AppScope::class)
interface AppComponent
// Anvil сам находит все @ContributesTo(AppScope::class) modules
```

### Основные аннотации

```kotlin
// @ContributesTo — автоматически добавляет module в component
@Module
@ContributesTo(AppScope::class)
class NetworkModule {
    @Provides
    fun provideApi(): Api = ApiImpl()
}

// @ContributesBinding — автоматический @Binds
@ContributesBinding(AppScope::class)
@Inject
class UserRepositoryImpl(
    private val api: Api
) : UserRepository

// @MergeComponent — component который мержит все contributions
@MergeComponent(AppScope::class)
interface AppComponent
```

### Настройка

```kotlin
// build.gradle.kts
plugins {
    id("com.squareup.anvil") version "2.5.0-beta11"  // KSP fork
}

dependencies {
    implementation("com.google.dagger:dagger:2.52")
    ksp("com.google.dagger:dagger-compiler:2.52")
}

anvil {
    generateDaggerFactories.set(true)  // Быстрее builds
}
```

### Пример использования

```kotlin
// Scope annotation
abstract class AppScope private constructor()
abstract class ActivityScope private constructor()

// Network module (feature-network/)
@Module
@ContributesTo(AppScope::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttp(): OkHttpClient = OkHttpClient.Builder().build()
}

// Repository (feature-user/)
@ContributesBinding(AppScope::class)
@Singleton
@Inject
class UserRepositoryImpl(
    private val api: UserApi
) : UserRepository

// App component (app/)
@Singleton
@MergeComponent(AppScope::class)
interface AppComponent {
    fun inject(app: MyApp)
}
```

### Статус Anvil (2025)

- **K1 only** — не поддерживает Kotlin 2.0+ нативно
- **Maintenance mode** — только critical fixes
- **Рекомендация** — мигрировать на **Metro**

```kotlin
// ANVIL → METRO миграция
// Anvil
@ContributesBinding(AppScope::class)
@Inject
class UserRepositoryImpl : UserRepository

// Metro
@ContributesBinding(AppGraph::class)
@Inject
class UserRepositoryImpl : UserRepository
// API почти идентичный!
```

---

## ЧАСТЬ 3: Другие альтернативы

### Toothpick

**Статус:** Не активно развивается

Scope-tree based DI framework. JSR-330 совместимый.

```kotlin
// Toothpick пример
@Singleton
class UserRepository @Inject constructor(
    private val api: UserApi
)

// Scope tree
val appScope = Toothpick.openScope(AppScope::class.java)
appScope.installModules(object : Module() {
    init {
        bind(UserApi::class.java).toInstance(apiInstance)
    }
})

val userRepository: UserRepository = appScope.getInstance(UserRepository::class.java)
```

**Особенности:**
- Scope tree для lifecycle management
- Support @Releasable для memory pressure
- Incremental annotation processing

**Почему не рекомендуется:**
- Не активно развивается с 2020
- Старые Gradle версии в документации
- Лучше использовать Hilt или Koin

### kInject2

Compile-time DI для KMP.

```kotlin
// kInject2 пример
@Graph
interface AppGraph {
    val userRepository: UserRepository
}

@Factory
class UserRepositoryFactory(
    private val api: UserApi
) {
    fun create(): UserRepository = UserRepositoryImpl(api)
}
```

**Статус:** Менее популярен чем kotlin-inject и Metro.

---

## Сравнение всех решений

| Решение | Тип | KMP | Compile-time | Статус 2025 |
|---------|-----|-----|--------------|-------------|
| **Manual DI** | Pattern | ✅ | ❌ | ✅ Рекомендуется для простых apps |
| **Dagger 2** | Framework | ❌ | ✅ | ✅ Активен |
| **Hilt** | Framework | ❌ | ✅ | ✅ Рекомендуется Google |
| **Koin** | Framework | ✅ | ❌ | ✅ Популярен |
| **Kodein** | Framework | ✅ | ❌ | ✅ Активен |
| **kotlin-inject** | Framework | ✅ | ✅ | ✅ Растёт |
| **Metro** | Framework | ✅ | ✅ | ✅ Новейший, рекомендуется |
| **Anvil** | Extension | ❌ | ✅ | ⚠️ Maintenance |
| **Toothpick** | Framework | ❌ | ❌ | ❌ Не активен |

---

## Decision Tree: Какой выбрать

```
┌─────────────────────────────────────────────────────────────┐
│                  ВЫБОР DI РЕШЕНИЯ                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Простое приложение? ──YES──▶ Manual DI                    │
│        │                                                    │
│       NO                                                    │
│        │                                                    │
│        ▼                                                    │
│  Нужен KMP? ──YES──▶ Compile-time важен?                   │
│        │                    │                               │
│       NO                   YES ──▶ Metro / kotlin-inject   │
│        │                    │                               │
│        │                   NO ──▶ Koin / Kodein            │
│        ▼                                                    │
│  Android-only?                                              │
│        │                                                    │
│       YES                                                   │
│        │                                                    │
│        ▼                                                    │
│  Hilt (рекомендация Google)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Источники

### Manual DI
- [Android Developers - Manual DI](https://developer.android.com/training/dependency-injection/manual)
- [DI without Framework](https://blog.kotlin-academy.com/dependency-injection-the-pattern-without-the-framework-33cfa9d5f312)

### Anvil
- [Anvil GitHub](https://github.com/square/anvil)
- [Introducing Anvil-KSP](https://www.zacsweers.dev/introducing-anvil-ksp/)
- [Anvil Maintenance Mode](https://github.com/square/anvil/issues/1149)

### Toothpick
- [Toothpick GitHub](https://github.com/stephanenicolas/toothpick)

---

## Связь с другими темами

**[[dependency-injection-fundamentals]]** — теоретический фундамент dependency injection как паттерна проектирования. Без понимания принципов Inversion of Control, Composition Root и различий между Service Locator и DI невозможно осознанно выбирать между Manual DI и фреймворками. Manual DI — лучший способ изучить эти принципы на практике, потому что каждый паттерн реализуется вручную. Рекомендуется изучить теорию первой, затем реализовать Manual DI для закрепления.

**[[android-dagger-deep-dive]]** — Dagger является основой, на которой построен Anvil (рассмотренный в этом файле). Понимание Dagger Components, Modules и Scopes необходимо для работы с Anvil-аннотациями вроде @ContributesTo и @MergeComponent. При миграции с Manual DI на фреймворк Dagger часто является следующим шагом для Android-only проектов. Изучите Manual DI для понимания основ, затем Dagger для production.

**[[android-metro-deep-dive]]** — Metro является рекомендуемой заменой Anvil (который переходит в maintenance mode). API Metro почти идентичен Anvil (@ContributesBinding, @ContributesTo), что делает миграцию простой. Metro объединяет преимущества compile-time safety от Dagger и KMP-поддержку от kotlin-inject, устраняя необходимость в Manual DI для средних и крупных проектов. Читайте после освоения Manual DI и базового Dagger.

---

## Источники и дальнейшее чтение

- Leiva (2017). *Kotlin for Android Developers*. — практическое введение в Kotlin-паттерны, включая подходы к организации зависимостей без фреймворков, полезно для понимания Manual DI в Kotlin-стиле.
- Moskala (2021). *Effective Kotlin*. — best practices Kotlin, включая паттерны создания объектов, lazy initialization и организацию кода, которые напрямую применяются при реализации Manual DI containers.
- Bloch (2018). *Effective Java*. — классические паттерны Factory, Builder и принципы API-дизайна, на которых основан Manual DI подход с containers и factories.
