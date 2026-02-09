---
title: "kotlin-inject: Deep-Dive — compile-time DI для KMP"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/android
  - topic/kotlin
  - topic/dependency-injection
  - type/deep-dive
  - level/advanced
related:
  - "[[dependency-injection-fundamentals]]"
  - "[[android-dagger-deep-dive]]"
  - "[[android-hilt-deep-dive]]"
  - "[[android-koin-deep-dive]]"
---

# kotlin-inject: Deep-Dive

## TL;DR

**kotlin-inject** — compile-time DI библиотека для Kotlin от Evan Tatarka. Главное преимущество: **полная поддержка Kotlin Multiplatform** (Android, iOS, Desktop, Web) с compile-time проверками как у Dagger. Использует KSP для генерации кода. API похож на Dagger (@Component, @Inject, @Provides), но без Modules — всё через component inheritance. Поддерживает lambda injection, assisted injection, multibindings. Отличный выбор для KMP проектов с Dagger-подобным подходом.

---

## ПОЧЕМУ: Зачем нужен kotlin-inject

### Проблема: Dagger не работает в KMP

```kotlin
// Dagger/Hilt — только Android/JVM
@HiltAndroidApp  // Не работает на iOS!
class MyApp : Application()

// Koin — работает везде, но runtime
startKoin {
    modules(appModule)  // Ошибки только в runtime
}

// kotlin-inject — compile-time + KMP
@Component
abstract class AppComponent {
    abstract val repository: UserRepository  // Ошибка компиляции если нет binding
}
```

### Позиционирование kotlin-inject

```
┌─────────────────────────────────────────────────────────────┐
│                    DI FRAMEWORKS COMPARISON                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Compile-time        │         Runtime                     │
│  ──────────────────  │  ─────────────────                  │
│                      │                                      │
│  ┌──────────┐        │  ┌──────────┐                       │
│  │  Dagger  │        │  │   Koin   │                       │
│  │  (JVM)   │        │  │  (KMP)   │                       │
│  └──────────┘        │  └──────────┘                       │
│       │              │       │                              │
│       ▼              │       ▼                              │
│  ┌──────────┐        │  ┌──────────┐                       │
│  │   Hilt   │        │  │  Kodein  │                       │
│  │(Android) │        │  │  (KMP)   │                       │
│  └──────────┘        │  └──────────┘                       │
│                      │                                      │
│  ┌──────────────────────────────────┐                      │
│  │         kotlin-inject            │  ◀── BEST OF BOTH    │
│  │   Compile-time + KMP support     │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
│  ┌──────────────────────────────────┐                      │
│  │            Metro                 │  ◀── NEWEST (2025)   │
│  │   Compiler plugin + KMP + more   │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда выбирать kotlin-inject

| Сценарий | kotlin-inject | Dagger/Hilt | Koin |
|----------|---------------|-------------|------|
| **KMP проект** | ✅ Идеально | ❌ Нет | ✅ Runtime |
| **Compile-time safety** | ✅ | ✅ | ❌ |
| **Android-only** | ✅ | ✅ Лучше | ✅ |
| **Dagger знакомый API** | ✅ Похожий | ✅ | ❌ DSL |
| **Jetpack интеграция** | ❌ Ручная | ✅ Встроенная | ✅ |
| **Простота** | Средняя | Сложная | Простая |

**Идеально для:**
- Kotlin Multiplatform проектов с требованием compile-time safety
- Разработчиков с опытом Dagger, переходящих на KMP
- Проектов где важна type-safety и ранее обнаружение ошибок

**Не подходит для:**
- Android-only проектов (Hilt проще и лучше интегрирован)
- Быстрого прототипирования (Koin быстрее в настройке)
- Проектов с глубокой интеграцией Jetpack (ViewModel, WorkManager)

---

## ИСТОРИЯ

```
2018    Evan Tatarka создаёт kotlin-inject
        └── Цель: Dagger-подобный DI для Kotlin

2020    Версия 0.3 — стабилизация API
        ├── KSP support
        └── Multiplatform support

2023    Версия 0.6 — major improvements
        ├── @AssistedFactory
        ├── Improved scoping
        └── Better error messages

2024    Версия 0.7
        ├── kotlin-inject-runtime-kmp artifact
        ├── @KmpComponentCreate
        └── Kotlin 2.0 compatibility

2025    Версия 0.8 (текущая)
        ├── Improved KMP support
        ├── Better IDE integration
        └── kotlin-inject-anvil (Amazon)
```

### Влияние на экосистему

- **Metro** (Zac Sweers, 2025) черпает вдохновение из kotlin-inject
- **kotlin-inject-anvil** (Amazon) — расширения для large-scale проектов
- JetBrains рассматривает kotlin-inject для Ktor DI

---

## ЧТО: Архитектура kotlin-inject

### Основные концепции

```
┌─────────────────────────────────────────────────────────────┐
│                  KOTLIN-INJECT ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │   @Component    │  ◀── Abstract class                   │
│  │   abstract class│      Dagger: @Component interface     │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ defines                                         │
│           ▼                                                 │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │ Abstract props  │      │   @Provides     │             │
│  │ (entry points)  │      │   functions     │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  NO @Module! All bindings via:                             │
│  - @Inject on classes                                      │
│  - @Provides in component                                  │
│  - Component inheritance                                    │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │  @Scope         │      │  @Qualifier     │             │
│  │  (lifecycle)    │      │  (disambiguation)│             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │     Component Inheritance               │               │
│  │     (instead of Subcomponents)          │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Ключевое отличие от Dagger: Нет Modules!

```kotlin
// DAGGER: Component + Module
@Component(modules = [NetworkModule::class])
interface AppComponent

@Module
class NetworkModule {
    @Provides
    fun provideApi(): Api = ...
}

// KOTLIN-INJECT: Всё в Component
@Component
abstract class AppComponent {
    // Entry point
    abstract val api: Api

    // Provider (вместо @Module)
    @Provides
    protected fun provideApi(): Api = ApiImpl()
}
```

### Annotations

| Annotation | Назначение | Аналог в Dagger |
|------------|------------|-----------------|
| `@Component` | Определяет граф зависимостей | `@Component` |
| `@Inject` | Запрос зависимости | `@Inject` |
| `@Provides` | Предоставление зависимости | `@Provides` |
| `@Scope` | Определение scope | `@Scope` |
| `@Qualifier` | Различение одинаковых типов | `@Qualifier` |
| `@Assisted` | Runtime параметр | `@Assisted` |
| `@AssistedFactory` | Фабрика для assisted | `@AssistedFactory` |
| `@IntoSet` | Multibinding в Set | `@IntoSet` |
| `@IntoMap` | Multibinding в Map | `@IntoMap` |

---

## КАК: Практическое использование

### 1. Настройка проекта

#### Android проект (KSP)

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.google.devtools.ksp") version "2.0.21-1.0.27" apply false
}

// build.gradle.kts (app)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("me.tatarka.inject:kotlin-inject-runtime:0.8.0")
    ksp("me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
}
```

#### Kotlin Multiplatform проект

```kotlin
// build.gradle.kts (shared)
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.google.devtools.ksp")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation("me.tatarka.inject:kotlin-inject-runtime-kmp:0.8.0")
        }
    }
}

// KSP для каждой платформы
dependencies {
    add("kspAndroid", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
    add("kspIosX64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
    add("kspIosArm64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
    add("kspIosSimulatorArm64", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
}
```

#### Альтернатива: Common source set generation

```kotlin
// Генерация кода в common source set
dependencies {
    add("kspCommonMainMetadata", "me.tatarka.inject:kotlin-inject-compiler-ksp:0.8.0")
}

kotlin {
    sourceSets {
        commonMain {
            kotlin.srcDir("build/generated/ksp/metadata/commonMain/kotlin")
        }
    }
}

// Настройка зависимостей задач
tasks.withType<KspAATask>().configureEach {
    if (name != "kspCommonMainKotlinMetadata") {
        dependsOn("kspCommonMainKotlinMetadata")
    }
}
```

### 2. Базовый Component

```kotlin
// Простейший Component
@Component
abstract class AppComponent {
    // Entry point — как получить зависимость
    abstract val userRepository: UserRepository
}

// Класс с @Inject конструктором
@Inject
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache
)

// Создание компонента
val component = AppComponent::class.create()
val repository = component.userRepository
```

### 3. @Provides: Внешние зависимости

```kotlin
@Component
abstract class AppComponent {
    abstract val retrofit: Retrofit
    abstract val userApi: UserApi

    // Для классов которые нельзя аннотировать @Inject
    @Provides
    protected fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    protected fun provideRetrofit(client: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    protected fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }
}
```

### 4. @Scope: Управление жизненным циклом

#### Определение Scope

```kotlin
// Создаём scope annotation
@Scope
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION, AnnotationTarget.PROPERTY_GETTER)
annotation class Singleton

@Scope
annotation class ActivityScope

@Scope
annotation class FragmentScope
```

#### Использование Scope

```kotlin
// Scope на Component
@Singleton
@Component
abstract class AppComponent {
    // Все @Singleton зависимости живут пока живёт AppComponent
    abstract val analytics: Analytics

    @Singleton
    @Provides
    protected fun provideAnalytics(): Analytics = AnalyticsImpl()
}

// Scope на классе
@Singleton
@Inject
class UserRepository(private val api: UserApi)

// БЕЗ Scope — новый экземпляр каждый раз
@Inject
class Logger
```

### 5. Component Inheritance (вместо Subcomponents)

```kotlin
// Parent Component
@Singleton
@Component
abstract class AppComponent {
    abstract val analytics: Analytics
    abstract val networkClient: OkHttpClient

    @Singleton
    @Provides
    protected fun provideAnalytics(): Analytics = AnalyticsImpl()
}

// Child Component — наследует от parent
@ActivityScope
@Component
abstract class ActivityComponent(
    @Component val parent: AppComponent  // Получает все зависимости parent
) {
    // Дополнительные зависимости для Activity
    abstract val presenter: MainPresenter

    @ActivityScope
    @Provides
    protected fun providePresenter(
        analytics: Analytics  // Из parent!
    ): MainPresenter = MainPresenter(analytics)
}

// Ещё один уровень вложенности
@FragmentScope
@Component
abstract class FragmentComponent(
    @Component val parent: ActivityComponent
) {
    abstract val viewModel: UserViewModel
}

// Использование
val appComponent = AppComponent::class.create()
val activityComponent = ActivityComponent::class.create(appComponent)
val fragmentComponent = FragmentComponent::class.create(activityComponent)
```

### 6. @Qualifier: Различение зависимостей одного типа

```kotlin
// Определяем qualifiers
@Qualifier
annotation class BaseUrl

@Qualifier
annotation class AuthUrl

@Qualifier
annotation class IoDispatcher

@Qualifier
annotation class MainDispatcher

// Использование в Component
@Component
abstract class AppComponent {

    @BaseUrl
    @Provides
    protected fun provideBaseUrl(): String = "https://api.example.com/"

    @AuthUrl
    @Provides
    protected fun provideAuthUrl(): String = "https://auth.example.com/"

    @IoDispatcher
    @Provides
    protected fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @MainDispatcher
    @Provides
    protected fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

// Использование в классе
@Inject
class ApiClient(
    @BaseUrl private val baseUrl: String,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
)
```

### 7. Lazy и Provider

```kotlin
// Lazy — отложенная инициализация, один экземпляр
@Inject
class ExpensiveService(
    private val heavyDependency: Lazy<HeavyDependency>
) {
    fun doWork() {
        if (needsHeavy) {
            heavyDependency.value.process()  // Создаётся здесь
        }
    }
}

// () -> T — фабрика, новый экземпляр каждый раз
@Inject
class OrderProcessor(
    private val createHandler: () -> RequestHandler
) {
    fun process(orders: List<Order>) {
        orders.forEach { order ->
            val handler = createHandler()  // Новый handler
            handler.handle(order)
        }
    }
}
```

### 8. Assisted Injection

#### Lambda-based (простой способ)

```kotlin
// Класс с runtime параметрами
@Inject
class UserDetailViewModel(
    @Assisted private val userId: String,  // Runtime параметр
    private val repository: UserRepository  // DI зависимость
)

// Inject как lambda
@Inject
class UserDetailFragment(
    private val createViewModel: (userId: String) -> UserDetailViewModel
) {
    fun onStart(userId: String) {
        val viewModel = createViewModel(userId)
    }
}
```

#### @AssistedFactory (именованные параметры)

```kotlin
// ViewModel
@Inject
class UserDetailViewModel(
    @Assisted private val userId: String,
    @Assisted private val initialState: State,
    private val repository: UserRepository
)

// Factory interface
@AssistedFactory
interface UserDetailViewModelFactory {
    fun create(
        userId: String,
        initialState: State = State.Loading  // Default значение!
    ): UserDetailViewModel
}

// Использование
@Inject
class UserDetailFragment(
    private val viewModelFactory: UserDetailViewModelFactory
) {
    fun onStart(userId: String) {
        val viewModel = viewModelFactory.create(userId)
        // или
        val viewModel = viewModelFactory.create(
            userId = userId,
            initialState = State.Empty
        )
    }
}
```

#### Ограничение: Assisted + Scope несовместимы

```kotlin
// ОШИБКА! Scoped + Assisted не работают вместе
@Singleton  // Scope
@Inject
class CachedViewModel(
    @Assisted userId: String,  // Assisted
    private val repo: UserRepository
)
// Error: Assisted injection doesn't work with scopes

// РЕШЕНИЕ: Убрать scope
@Inject
class CachedViewModel(
    @Assisted userId: String,
    private val repo: UserRepository
)
```

### 9. Multibindings

#### Set Multibinding

```kotlin
// Интерфейс
interface Plugin {
    fun execute()
}

// Реализации
@Inject
class LoggingPlugin : Plugin {
    override fun execute() = println("Logging")
}

@Inject
class AnalyticsPlugin : Plugin {
    override fun execute() = println("Analytics")
}

// Component
@Component
abstract class AppComponent {
    abstract val plugins: Set<Plugin>

    @IntoSet
    @Provides
    protected fun provideLoggingPlugin(): Plugin = LoggingPlugin()

    @IntoSet
    @Provides
    protected fun provideAnalyticsPlugin(): Plugin = AnalyticsPlugin()
}

// Использование
val plugins = appComponent.plugins
plugins.forEach { it.execute() }
```

#### Map Multibinding

```kotlin
// Key annotation
@MapKey
annotation class StringKey(val value: String)

// Component
@Component
abstract class AppComponent {
    abstract val handlers: Map<String, Handler>

    @IntoMap
    @StringKey("login")
    @Provides
    protected fun provideLoginHandler(): Handler = LoginHandler()

    @IntoMap
    @StringKey("logout")
    @Provides
    protected fun provideLogoutHandler(): Handler = LogoutHandler()
}
```

### 10. KMP: Платформо-специфичные зависимости

```kotlin
// commonMain - общий интерфейс
interface Platform {
    val name: String
}

@Component
abstract class CommonComponent {
    abstract val platform: Platform
}

// androidMain
@Inject
class AndroidPlatform : Platform {
    override val name: String = "Android ${Build.VERSION.SDK_INT}"
}

@Component
abstract class AndroidComponent : CommonComponent() {
    @Provides
    protected fun providePlatform(): Platform = AndroidPlatform()
}

// iosMain
@Inject
class IosPlatform : Platform {
    override val name: String = "iOS"
}

@Component
abstract class IosComponent : CommonComponent() {
    @Provides
    protected fun providePlatform(): Platform = IosPlatform()
}
```

#### @KmpComponentCreate для iOS

```kotlin
// commonMain
@Component
abstract class SharedComponent {
    abstract val repository: UserRepository

    companion object
}

// iosMain - expect/actual для создания
@KmpComponentCreate
expect fun SharedComponent.Companion.createKmp(): SharedComponent

// Использование в Swift
let component = SharedComponentCompanion().createKmp()
```

---

## Сравнение API с Dagger

### Component

```kotlin
// DAGGER
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
    fun userRepository(): UserRepository
}

// KOTLIN-INJECT
@Singleton
@Component
abstract class AppComponent {
    abstract val userRepository: UserRepository
    // Нет inject() — используем constructor injection или передаём компонент
}
```

### Module vs @Provides в Component

```kotlin
// DAGGER: Отдельные Modules
@Module
class NetworkModule {
    @Provides
    fun provideApi(): Api = ApiImpl()
}

@Component(modules = [NetworkModule::class])
interface AppComponent

// KOTLIN-INJECT: @Provides прямо в Component
@Component
abstract class AppComponent {
    @Provides
    protected fun provideApi(): Api = ApiImpl()
}
```

### Subcomponent vs Component Inheritance

```kotlin
// DAGGER: Subcomponent
@Subcomponent
interface ActivityComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

@Component
interface AppComponent {
    fun activityComponentFactory(): ActivityComponent.Factory
}

// KOTLIN-INJECT: Constructor с @Component parent
@Component
abstract class ActivityComponent(
    @Component val parent: AppComponent
)

val activityComponent = ActivityComponent::class.create(appComponent)
```

### Binds

```kotlin
// DAGGER: @Binds в abstract module
@Module
abstract class RepositoryModule {
    @Binds
    abstract fun bindRepo(impl: UserRepositoryImpl): UserRepository
}

// KOTLIN-INJECT: @Provides возвращает interface
@Component
abstract class AppComponent {
    // Вариант 1: Прямой @Provides
    @Provides
    protected fun provideRepo(impl: UserRepositoryImpl): UserRepository = impl

    // Вариант 2: @Inject на реализации, typealias
    protected val UserRepository.bind: UserRepository get() = this
}
```

---

## Генерация кода

### Что генерирует kotlin-inject

```
build/generated/ksp/
└── kotlin/
    └── com/example/
        ├── InjectAppComponent.kt     // Реализация Component
        ├── UserRepository_Factory.kt  // Factory для @Inject класса
        └── ...
```

### Пример сгенерированного кода

```kotlin
// Исходный Component
@Singleton
@Component
abstract class AppComponent {
    abstract val userRepository: UserRepository

    @Singleton
    @Provides
    protected fun provideApi(): UserApi = UserApiImpl()
}

// Сгенерированная реализация
class InjectAppComponent : AppComponent() {
    private val _api: UserApi by lazy { provideApi() }
    private val _userRepository: UserRepository by lazy {
        UserRepository(_api)
    }

    override val userRepository: UserRepository
        get() = _userRepository

    companion object {
        fun create(): AppComponent = InjectAppComponent()
    }
}
```

---

## kotlin-inject-anvil (Amazon)

### Что это

Расширения для kotlin-inject от Amazon для large-scale проектов. Добавляет:
- `@ContributesTo` — автоматическое добавление в Component
- `@ContributesBinding` — автоматический bind интерфейса
- `@ContributesAssistedFactory` — упрощённые assisted factories

### Настройка

```kotlin
dependencies {
    implementation("software.amazon.lastmile.kotlin.inject.anvil:runtime:0.0.4")
    ksp("software.amazon.lastmile.kotlin.inject.anvil:compiler:0.0.4")
}
```

### Использование

```kotlin
// Автоматически добавляется в AppScope Component
@ContributesBinding(AppScope::class)
@Inject
class UserRepositoryImpl(
    private val api: UserApi
) : UserRepository

// @ContributesTo для interfaces
@ContributesTo(AppScope::class)
interface AnalyticsComponent {
    @Provides
    fun provideAnalytics(): Analytics = AnalyticsImpl()
}

// Component автоматически включает все @ContributesTo
@Component
@MergeComponent(AppScope::class)
abstract class AppComponent
```

---

## Тестирование

### Unit Tests — без DI

```kotlin
class UserRepositoryTest {
    private val mockApi = mockk<UserApi>()
    private val repository = UserRepository(mockApi)

    @Test
    fun `getUser returns user from api`() {
        every { mockApi.fetchUser("123") } returns User("123", "John")

        val user = repository.getUser("123")

        assertEquals("John", user.name)
    }
}
```

### Integration Tests — Test Component

```kotlin
// Test Component с fake зависимостями
@Component
abstract class TestAppComponent {
    abstract val userRepository: UserRepository

    @Provides
    protected fun provideFakeApi(): UserApi = FakeUserApi()
}

class UserFlowTest {
    private val component = TestAppComponent::class.create()

    @Test
    fun testUserFlow() {
        val repo = component.userRepository
        // repo использует FakeUserApi
    }
}
```

---

## Best Practices

### 1. Используйте Component Inheritance вместо огромных Components

```kotlin
// ХОРОШО: Иерархия компонентов
@Singleton
@Component
abstract class AppComponent { ... }

@ActivityScope
@Component
abstract class ActivityComponent(
    @Component val app: AppComponent
) { ... }

// ПЛОХО: Один огромный Component
@Component
abstract class AppComponent {
    // 100+ зависимостей
}
```

### 2. Scope только когда нужно

```kotlin
// ХОРОШО: Scope по необходимости
@Singleton
@Inject
class Analytics  // Действительно нужен один

@Inject
class UserRepository  // Новый экземпляр OK

// ПЛОХО: Всё Singleton
@Singleton
@Inject
class Logger  // Зачем?
```

### 3. Используйте @AssistedFactory для сложных случаев

```kotlin
// ХОРОШО: Именованные параметры, defaults
@AssistedFactory
interface ViewModelFactory {
    fun create(
        userId: String,
        config: Config = Config.Default
    ): MyViewModel
}

// ПЛОХО: Lambda с неочевидными параметрами
val create: (String, Config) -> MyViewModel
```

### 4. Организация кода в KMP

```
shared/
├── commonMain/
│   └── di/
│       ├── CommonComponent.kt
│       └── Scopes.kt
├── androidMain/
│   └── di/
│       └── AndroidComponent.kt
└── iosMain/
    └── di/
        └── IosComponent.kt
```

---

## Common Pitfalls

### 1. Забыть @Inject

```kotlin
// ОШИБКА: Нет @Inject
class UserRepository(private val api: UserApi)
// Error: Cannot find an @Inject constructor or @Provides

// РЕШЕНИЕ
@Inject
class UserRepository(private val api: UserApi)
```

### 2. Циклические зависимости

```kotlin
// ОШИБКА
@Inject
class A(private val b: B)

@Inject
class B(private val a: A)
// Error: Dependency cycle

// РЕШЕНИЕ: Lazy или рефакторинг
@Inject
class A(private val b: Lazy<B>)
```

### 3. Scope mismatch

```kotlin
// ОШИБКА: @Singleton в unscoped Component
@Component  // Нет scope!
abstract class AppComponent {
    @Singleton  // Ошибка
    @Provides
    protected fun provideApi(): Api = ...
}

// РЕШЕНИЕ
@Singleton
@Component
abstract class AppComponent { ... }
```

### 4. Private @Provides

```kotlin
// ОШИБКА: Private не виден
@Component
abstract class AppComponent {
    @Provides
    private fun provideApi(): Api = ...  // Ошибка!
}

// РЕШЕНИЕ: protected или internal
@Provides
protected fun provideApi(): Api = ...
```

---

## Источники

### Официальные
- [kotlin-inject GitHub](https://github.com/evant/kotlin-inject)
- [kotlin-inject Documentation](https://github.com/evant/kotlin-inject/tree/main/docs)
- [kotlin-inject-anvil (Amazon)](https://github.com/amzn/kotlin-inject-anvil)

### Статьи
- [Koin vs kotlin-inject (Infinum)](https://infinum.com/blog/koin-vs-kotlin-inject-dependency-injection/)
- [From Dagger to kotlin-inject (droidcon)](https://www.droidcon.com/2023/03/23/from-dagger-hilt-into-the-multiplatform-world-with-kotlin-inject/)
- [Using kotlin-inject in KMP (John O'Reilly)](https://johnoreilly.dev/posts/kotlin-inject-kmp/)

---

## Связанные материалы

- [[dependency-injection-fundamentals]] — Теория DI
- [[android-dagger-deep-dive]] — Dagger (основа для Hilt)
- [[android-hilt-deep-dive]] — Hilt (Android-специфичный)
- [[android-koin-deep-dive]] — Koin (runtime альтернатива)
- [[android-metro-deep-dive]] — Metro (новейший compile-time)
