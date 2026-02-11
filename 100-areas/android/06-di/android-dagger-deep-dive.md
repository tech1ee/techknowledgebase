---
title: "Dagger и Dagger 2: Deep-Dive — compile-time DI"
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
  - "[[android-hilt-deep-dive]]"
  - "[[android-koin-deep-dive]]"
---

# Dagger & Dagger 2: Deep-Dive

## TL;DR

**Dagger 2** — compile-time DI framework от Google (изначально Square), стандарт де-факто для сложных Android-приложений. Использует annotation processing для генерации кода — без reflection, 100% Proguard-friendly. Hilt построен поверх Dagger 2. Начиная с версии 2.48, поддерживает KSP (до 2x быстрее KAPT). Ключевые концепции: Component, Module, Scope, Subcomponent. Сложнее Koin/Hilt, но даёт полный контроль над графом зависимостей.

---

## ПОЧЕМУ: Зачем нужен Dagger

### Проблема, которую решает Dagger

```kotlin
// БЕЗ DI: жёсткие зависимости, сложное тестирование
class UserRepository {
    private val api = RetrofitClient.createApi() // Жёсткая связь
    private val cache = RoomDatabase.getInstance() // Жёсткая связь
    private val logger = Logger() // Жёсткая связь

    fun getUser(id: String): User {
        logger.log("Fetching user $id")
        return cache.getUser(id) ?: api.fetchUser(id).also {
            cache.saveUser(it)
        }
    }
}

// Проблемы:
// 1. Невозможно подменить зависимости для тестирования
// 2. Невозможно переиспользовать с другим API/Cache
// 3. Скрытые зависимости — непонятно что нужно для работы
```

```kotlin
// С DAGGER: явные зависимости, легко тестировать
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val cache: UserCache,
    private val logger: Logger
) {
    fun getUser(id: String): User {
        logger.log("Fetching user $id")
        return cache.getUser(id) ?: api.fetchUser(id).also {
            cache.saveUser(it)
        }
    }
}

// Преимущества:
// 1. Зависимости явные — видны в конструкторе
// 2. Легко подменить для тестов
// 3. Dagger проверяет граф на этапе компиляции
```

### Почему именно Dagger (а не другие решения)

| Критерий | Dagger 2 | Koin | Manual DI |
|----------|----------|------|-----------|
| **Проверка графа** | Compile-time | Runtime | Нет |
| **Производительность** | Максимальная (codegen) | Хорошая | Зависит от реализации |
| **Reflection** | Нет | Нет | Нет |
| **Proguard** | 100% совместим | Совместим | Совместим |
| **Обнаружение ошибок** | При компиляции | При запуске | При запуске |
| **Кривая обучения** | Крутая | Пологая | Средняя |
| **Масштабируемость** | Отличная | Хорошая | Плохая |

### Когда выбирать Dagger 2

**Идеально подходит для:**
- Больших enterprise-приложений (100+ модулей)
- Команд, которым нужна максимальная type-safety
- Проектов с жёсткими требованиями к производительности
- Legacy-проектов, где уже используется Dagger

**Не подходит для:**
- Небольших приложений (избыточная сложность)
- Kotlin Multiplatform проектов (Dagger — Android/JVM only)
- Быстрого прототипирования
- Команд без опыта работы с DI

> **Рекомендация 2024:** Для новых Android-проектов Google рекомендует **Hilt** (построен на Dagger 2, но проще в использовании). Чистый Dagger 2 — для специфических случаев или понимания того, как работает Hilt под капотом.

---

## ИСТОРИЯ: От Square до Google

### Timeline

```
2012    Square создаёт Dagger 1
        ├── Частично reflection-based
        ├── Проблемы с Proguard
        └── ObjectGraph для композиции графа

2014    Google форкает Dagger → Dagger 2
        ├── 100% compile-time, без reflection
        ├── Annotation processing
        └── @Component вместо ObjectGraph

2015    Dagger 2.0 релиз
        ├── JSR-330 совместимость
        ├── Полная генерация кода
        └── Traceable, debuggable code

2016    dagger.android модуль
        ├── Упрощение для Android
        ├── @ContributesAndroidInjector
        └── HasAndroidInjector

2020    Hilt релиз (на базе Dagger 2)
        ├── Стандартные компоненты
        ├── Jetpack интеграция
        └── Упрощённый API

2023    Dagger 2.48 — KSP support (alpha)
        ├── До 2x быстрее KAPT
        └── Kotlin 2.0 готовность

2024    Dagger 2.52+ — стабильный KSP
        ├── KSP2 поддержка
        └── Рекомендация мигрировать с KAPT
```

### Dagger 1 vs Dagger 2

| Аспект | Dagger 1 (Square) | Dagger 2 (Google) |
|--------|-------------------|-------------------|
| **Граф** | ObjectGraph (runtime) | @Component (compile-time) |
| **Reflection** | Частичное использование | Нет |
| **Proguard** | Проблемы | 100% совместим |
| **Производительность** | ~80ms граф (Nexus 7) | ~40ms граф (Nexus 7) |
| **Debug** | Сложно | Легко (generated code) |
| **Module override** | Поддерживается | Не поддерживается |
| **Статус** | Deprecated | Активно развивается |

---

## ЧТО: Архитектура Dagger 2

### Основные концепции

```
┌─────────────────────────────────────────────────────────────┐
│                      DAGGER 2 ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    provides    ┌─────────────┐            │
│  │   @Module   │───────────────▶│  @Component │            │
│  │  @Provides  │                │  interface  │            │
│  │  @Binds     │                │             │            │
│  └─────────────┘                └──────┬──────┘            │
│                                        │                    │
│                                        │ injects            │
│                                        ▼                    │
│                                 ┌─────────────┐            │
│                                 │  @Inject    │            │
│                                 │  classes    │            │
│                                 └─────────────┘            │
│                                                             │
│  ┌─────────────┐    extends     ┌─────────────┐            │
│  │@Subcomponent│◀───────────────│ @Component  │            │
│  │  (child)    │                │  (parent)   │            │
│  └─────────────┘                └─────────────┘            │
│                                                             │
│  ┌─────────────┐    controls    ┌─────────────┐            │
│  │   @Scope    │───────────────▶│  Lifecycle  │            │
│  │ @Singleton  │                │  Instance   │            │
│  └─────────────┘                └─────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### JSR-330 Annotations (стандарт Java)

Dagger 2 полностью совместим с JSR-330 (javax.inject):

```kotlin
import javax.inject.Inject
import javax.inject.Singleton
import javax.inject.Named
import javax.inject.Provider
import javax.inject.Qualifier
import javax.inject.Scope
```

| Annotation | Назначение |
|------------|------------|
| `@Inject` | Запрос зависимости (конструктор, поле, метод) |
| `@Singleton` | Scope: один экземпляр |
| `@Named` | Qualifier: различение зависимостей одного типа |
| `@Qualifier` | Создание custom qualifiers |
| `@Scope` | Создание custom scopes |
| `Provider<T>` | Ленивое/множественное получение зависимости |

### Dagger-specific Annotations

```kotlin
import dagger.Module
import dagger.Provides
import dagger.Binds
import dagger.Component
import dagger.Subcomponent
import dagger.Lazy
import dagger.Reusable
import dagger.multibindings.IntoSet
import dagger.multibindings.IntoMap
import dagger.assisted.Assisted
import dagger.assisted.AssistedFactory
import dagger.assisted.AssistedInject
```

---

## КАК: Практическое использование

### 1. Базовая настройка проекта

#### Gradle конфигурация (KSP — рекомендуется)

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
    // Dagger 2 core
    implementation("com.google.dagger:dagger:2.52")
    ksp("com.google.dagger:dagger-compiler:2.52")

    // Для Android-специфичных фич (опционально)
    implementation("com.google.dagger:dagger-android:2.52")
    implementation("com.google.dagger:dagger-android-support:2.52")
    ksp("com.google.dagger:dagger-android-processor:2.52")
}
```

#### Gradle конфигурация (KAPT — legacy)

```kotlin
// build.gradle.kts (app)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.kapt")
}

dependencies {
    implementation("com.google.dagger:dagger:2.52")
    kapt("com.google.dagger:dagger-compiler:2.52")
}
```

### 2. @Inject: Запрос зависимостей

#### Constructor Injection (рекомендуется)

```kotlin
// Dagger автоматически знает как создать этот класс
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val cache: UserCache
) {
    fun getUser(id: String): User =
        cache.getUser(id) ?: api.fetchUser(id)
}

// Если класс не имеет зависимостей
class Logger @Inject constructor() {
    fun log(message: String) = println(message)
}

// Цепочка зависимостей — Dagger разрешит автоматически
class UserService @Inject constructor(
    private val repository: UserRepository, // Dagger создаст
    private val logger: Logger              // Dagger создаст
) {
    fun loadUser(id: String): User {
        logger.log("Loading user $id")
        return repository.getUser(id)
    }
}
```

#### Field Injection (для Android компонентов)

```kotlin
// Для Activity/Fragment/Service — нельзя использовать constructor injection
class MainActivity : AppCompatActivity() {

    // Field должен быть НЕ private
    @Inject
    lateinit var userService: UserService

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        // ВАЖНО: inject ДО super.onCreate()
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)

        // Теперь можно использовать
        val user = userService.loadUser("123")
    }
}
```

#### Method Injection (редко используется)

```kotlin
class LegacyService @Inject constructor() {

    private lateinit var logger: Logger

    // Dagger вызовет этот метод после создания объекта
    @Inject
    fun setLogger(logger: Logger) {
        this.logger = logger
    }
}
```

### 3. @Module и @Provides: Предоставление зависимостей

#### Когда нужен @Module

```kotlin
// @Inject работает для ваших классов
class MyRepository @Inject constructor() // OK

// Для внешних библиотек нужен @Module
// Retrofit, Room, OkHttp — вы не можете добавить @Inject
```

#### Базовый Module

```kotlin
@Module
class NetworkModule {

    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient) // Dagger inject-ит автоматически
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }
}
```

#### @Binds: Привязка интерфейса к реализации

```kotlin
// Интерфейс
interface UserRepository {
    fun getUser(id: String): User
}

// Реализация
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi
) : UserRepository {
    override fun getUser(id: String): User = api.fetchUser(id)
}

// Module с @Binds (эффективнее @Provides для интерфейсов)
@Module
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    // @Binds:
    // - Не создаёт дополнительный код
    // - Только для abstract методов
    // - Один параметр = реализация
    // - Return type = интерфейс
}
```

#### Комбинирование @Provides и @Binds

```kotlin
@Module
abstract class DataModule {

    // @Binds для интерфейсов
    @Binds
    abstract fun bindRepository(impl: UserRepositoryImpl): UserRepository

    companion object {
        // @Provides для объектов из библиотек
        @Provides
        fun provideDatabase(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "app.db"
            ).build()
        }
    }
}
```

### 4. @Component: Мост между Module и Inject

#### Базовый Component

```kotlin
@Component(modules = [NetworkModule::class, DataModule::class])
interface AppComponent {

    // Способ 1: Provision method — получить зависимость напрямую
    fun getUserService(): UserService

    // Способ 2: Members-injection method — inject в существующий объект
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)

    // Builder для создания Component
    @Component.Builder
    interface Builder {
        @BindsInstance
        fun context(context: Context): Builder

        fun build(): AppComponent
    }
}
```

#### Создание и использование Component

```kotlin
class MyApp : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()

        // Создаём Component
        appComponent = DaggerAppComponent.builder()
            .context(this) // @BindsInstance
            .build()
    }
}

// В Activity
class MainActivity : AppCompatActivity() {

    @Inject lateinit var userService: UserService

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)

        // userService готов к использованию
    }
}
```

#### @Component.Factory (альтернатива Builder)

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {

    @Component.Factory
    interface Factory {
        fun create(
            @BindsInstance context: Context,
            @BindsInstance config: AppConfig
        ): AppComponent
    }
}

// Использование
val component = DaggerAppComponent.factory()
    .create(context, config)
```

### 5. @Scope: Управление жизненным циклом

#### Встроенный @Singleton

```kotlin
@Singleton // Один экземпляр на весь Component
@Component(modules = [AppModule::class])
interface AppComponent {
    // ...
}

@Module
class AppModule {

    @Provides
    @Singleton // Один OkHttpClient на всё приложение
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder().build()
    }
}

// Или на классе
@Singleton
class Analytics @Inject constructor() {
    // Один экземпляр на всё приложение
}
```

#### Custom Scopes

```kotlin
// Определяем scope для Activity
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

// Определяем scope для Fragment
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope

// Использование
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}
```

#### Правила Scopes

```kotlin
// ПРАВИЛО 1: Scope Component = Scope зависимостей в нём
@Singleton
@Component
interface AppComponent // Может содержать @Singleton зависимости

@ActivityScope
@Subcomponent
interface ActivityComponent // Может содержать @ActivityScope зависимости

// ПРАВИЛО 2: Subcomponent НЕ может иметь тот же scope что и parent
@Singleton
@Component
interface AppComponent

@Singleton // ОШИБКА КОМПИЛЯЦИИ!
@Subcomponent
interface ActivityComponent

// ПРАВИЛО 3: Unscoped зависимости — новый экземпляр каждый раз
@Provides // Без scope
fun provideLogger(): Logger = Logger() // Новый каждый раз

@Provides
@Singleton // Один на Component
fun provideAnalytics(): Analytics = Analytics()
```

### 6. Subcomponents: Иерархия компонентов

#### Зачем нужны Subcomponents

```
AppComponent (@Singleton)
    │
    ├── ActivityComponent (@ActivityScope)
    │       │
    │       └── FragmentComponent (@FragmentScope)
    │
    └── ServiceComponent (@ServiceScope)

Subcomponent наследует ВСЕ зависимости от parent.
Зависимости Subcomponent не видны parent-у.
```

#### Определение Subcomponent

```kotlin
// Parent Component
@Singleton
@Component(modules = [AppModule::class])
interface AppComponent {

    // Фабрика для создания Subcomponent
    fun activityComponentFactory(): ActivityComponent.Factory

    fun inject(app: MyApp)
}

// Subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {

    fun inject(activity: MainActivity)
    fun inject(activity: SettingsActivity)

    // Вложенный Subcomponent
    fun fragmentComponentFactory(): FragmentComponent.Factory

    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }
}

// Вложенный Subcomponent
@FragmentScope
@Subcomponent
interface FragmentComponent {

    fun inject(fragment: UserFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(): FragmentComponent
    }
}
```

#### Регистрация Subcomponent в Module

```kotlin
// ВАЖНО: Нужно зарегистрировать Subcomponent в Module родителя
@Module(subcomponents = [ActivityComponent::class])
class AppModule {
    // ...
}

@Module(subcomponents = [FragmentComponent::class])
class ActivityModule {
    // ...
}
```

#### Использование иерархии

```kotlin
class MyApp : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.create()
    }
}

class MainActivity : AppCompatActivity() {

    lateinit var activityComponent: ActivityComponent

    @Inject lateinit var presenter: MainPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        // Создаём ActivityComponent из AppComponent
        activityComponent = (application as MyApp)
            .appComponent
            .activityComponentFactory()
            .create(this)

        activityComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}

class UserFragment : Fragment() {

    @Inject lateinit var viewModel: UserViewModel

    override fun onAttach(context: Context) {
        super.onAttach(context)

        // Создаём FragmentComponent из ActivityComponent
        (activity as MainActivity)
            .activityComponent
            .fragmentComponentFactory()
            .create()
            .inject(this)
    }
}
```

### 7. Qualifiers: Различение зависимостей одного типа

#### @Named (встроенный qualifier)

```kotlin
@Module
class NetworkModule {

    @Provides
    @Named("base")
    fun provideBaseUrl(): String = "https://api.example.com/"

    @Provides
    @Named("auth")
    fun provideAuthUrl(): String = "https://auth.example.com/"

    @Provides
    fun provideApiRetrofit(@Named("base") baseUrl: String): Retrofit {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .build()
    }
}

// Использование
class ApiClient @Inject constructor(
    @Named("base") private val baseUrl: String,
    @Named("auth") private val authUrl: String
)
```

#### Custom Qualifiers (рекомендуется)

```kotlin
// Определение
@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class BaseUrl

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class AuthUrl

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class MainDispatcher

// Использование в Module
@Module
class AppModule {

    @Provides
    @BaseUrl
    fun provideBaseUrl(): String = "https://api.example.com/"

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

// Использование в классе
class UserRepository @Inject constructor(
    @BaseUrl private val baseUrl: String,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
)
```

### 8. Provider и Lazy: Отложенное получение

#### Provider<T>: Получение нового экземпляра

```kotlin
class OrderProcessor @Inject constructor(
    // Каждый вызов .get() создаёт НОВЫЙ RequestHandler
    private val handlerProvider: Provider<RequestHandler>
) {
    fun processOrders(orders: List<Order>) {
        orders.forEach { order ->
            // Новый handler для каждого заказа
            val handler = handlerProvider.get()
            handler.handle(order)
        }
    }
}
```

#### Lazy<T>: Отложенная инициализация

```kotlin
class ExpensiveService @Inject constructor(
    // Создаётся только при первом .get()
    private val heavyDependency: Lazy<HeavyDependency>
) {
    fun doWork() {
        if (needsHeavyWork) {
            // HeavyDependency создаётся только здесь
            heavyDependency.get().process()
        }
    }
}
```

#### Комбинирование с Scope

```kotlin
@Singleton
class SingletonService @Inject constructor()

class Consumer @Inject constructor(
    // Provider от Singleton — всегда один и тот же экземпляр
    private val singletonProvider: Provider<SingletonService>,

    // Lazy от Singleton — один экземпляр, отложенная инициализация
    private val singletonLazy: Lazy<SingletonService>
)
```

### 9. Multibindings: Коллекции зависимостей

#### Set Multibindings

```kotlin
// Интерфейс плагина
interface Plugin {
    fun execute()
}

// Реализации
class LoggingPlugin @Inject constructor() : Plugin {
    override fun execute() = println("Logging")
}

class AnalyticsPlugin @Inject constructor() : Plugin {
    override fun execute() = println("Analytics")
}

// Module с multibindings
@Module
abstract class PluginModule {

    @Binds
    @IntoSet
    abstract fun bindLoggingPlugin(impl: LoggingPlugin): Plugin

    @Binds
    @IntoSet
    abstract fun bindAnalyticsPlugin(impl: AnalyticsPlugin): Plugin
}

// Использование — получаем Set<Plugin>
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin>
) {
    fun runAll() {
        plugins.forEach { it.execute() }
    }
}
```

#### Map Multibindings

```kotlin
// Enum для ключей
enum class Feature {
    LOGIN, PROFILE, SETTINGS
}

// Custom MapKey
@MapKey
annotation class FeatureKey(val value: Feature)

// Реализации
interface FeatureHandler {
    fun handle()
}

class LoginHandler @Inject constructor() : FeatureHandler {
    override fun handle() = println("Login")
}

class ProfileHandler @Inject constructor() : FeatureHandler {
    override fun handle() = println("Profile")
}

// Module
@Module
abstract class FeatureModule {

    @Binds
    @IntoMap
    @FeatureKey(Feature.LOGIN)
    abstract fun bindLoginHandler(impl: LoginHandler): FeatureHandler

    @Binds
    @IntoMap
    @FeatureKey(Feature.PROFILE)
    abstract fun bindProfileHandler(impl: ProfileHandler): FeatureHandler
}

// Использование
class FeatureRouter @Inject constructor(
    private val handlers: Map<Feature, @JvmSuppressWildcards FeatureHandler>
) {
    fun route(feature: Feature) {
        handlers[feature]?.handle()
    }
}
```

#### @ElementsIntoSet: Добавление нескольких элементов

```kotlin
@Module
class PluginModule {

    @Provides
    @ElementsIntoSet
    fun provideDefaultPlugins(): Set<Plugin> {
        return setOf(
            DefaultPlugin1(),
            DefaultPlugin2(),
            DefaultPlugin3()
        )
    }
}
```

### 10. Assisted Injection: Параметры времени выполнения

#### Проблема

```kotlin
// Нужно создать ViewModel с параметром userId
// userId известен только в runtime
class UserDetailViewModel(
    private val userId: String,      // Runtime параметр
    private val repository: UserRepository // Dagger зависимость
)
```

#### Решение с @AssistedInject

```kotlin
// ViewModel с assisted injection
class UserDetailViewModel @AssistedInject constructor(
    @Assisted private val userId: String,  // Runtime параметр
    private val repository: UserRepository  // Dagger inject-ит
) : ViewModel() {

    val user = repository.observeUser(userId)

    // Factory interface
    @AssistedFactory
    interface Factory {
        fun create(userId: String): UserDetailViewModel
    }
}

// Использование
class UserDetailFragment : Fragment() {

    @Inject
    lateinit var viewModelFactory: UserDetailViewModel.Factory

    private val viewModel by lazy {
        viewModelFactory.create(arguments?.getString("userId") ?: "")
    }
}
```

#### AutoFactory (альтернатива до Dagger 2.31)

```kotlin
// build.gradle
dependencies {
    implementation("com.google.auto.factory:auto-factory:1.0.1")
    kapt("com.google.auto.factory:auto-factory:1.0.1")
}

// Использование
@AutoFactory
class UserDetailPresenter(
    @Provided private val repository: UserRepository, // Dagger
    private val userId: String  // Runtime
)

// Сгенерированная фабрика
class UserDetailPresenterFactory @Inject constructor(
    private val repository: UserRepository
) {
    fun create(userId: String): UserDetailPresenter {
        return UserDetailPresenter(repository, userId)
    }
}
```

---

## Генерация кода: Что создаёт Dagger

### Структура сгенерированного кода

```
build/generated/ksp/debug/kotlin/
├── com/example/
│   ├── DaggerAppComponent.kt          // Реализация Component
│   ├── UserRepository_Factory.kt       // Factory для @Inject класса
│   ├── NetworkModule_ProvideOkHttpClientFactory.kt
│   └── MainActivity_MembersInjector.kt // Injector для Activity
```

### Пример сгенерированного кода

```kotlin
// Исходный код
class UserRepository @Inject constructor(
    private val api: UserApi
)

// Сгенерированный Factory
class UserRepository_Factory @Inject constructor(
    private val apiProvider: Provider<UserApi>
) : Factory<UserRepository> {

    override fun get(): UserRepository {
        return UserRepository(apiProvider.get())
    }

    companion object {
        fun create(apiProvider: Provider<UserApi>): UserRepository_Factory {
            return UserRepository_Factory(apiProvider)
        }

        fun newInstance(api: UserApi): UserRepository {
            return UserRepository(api)
        }
    }
}
```

```kotlin
// Исходный Component
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// Сгенерированная реализация (упрощённо)
class DaggerAppComponent private constructor() : AppComponent {

    private val okHttpClientProvider: Provider<OkHttpClient>
    private val userRepositoryProvider: Provider<UserRepository>

    init {
        okHttpClientProvider = DoubleCheck.provider(
            AppModule_ProvideOkHttpClientFactory.create()
        )
        // ... остальные providers
    }

    override fun inject(activity: MainActivity) {
        injectMainActivity(activity)
    }

    private fun injectMainActivity(instance: MainActivity) {
        MainActivity_MembersInjector.injectUserService(
            instance,
            userServiceProvider.get()
        )
    }

    companion object {
        fun create(): AppComponent = DaggerAppComponent()
    }
}
```

### DoubleCheck для Scoped зависимостей

```kotlin
// @Singleton зависимости используют DoubleCheck
// Это thread-safe lazy initialization

public final class DoubleCheck<T> implements Provider<T>, Lazy<T> {
    private volatile Provider<T> provider;
    private volatile Object instance = UNINITIALIZED;

    @Override
    public T get() {
        Object result = instance;
        if (result == UNINITIALIZED) {
            synchronized (this) {
                result = instance;
                if (result == UNINITIALIZED) {
                    result = provider.get();
                    instance = result;
                    provider = null; // GC
                }
            }
        }
        return (T) result;
    }
}
```

---

## KSP vs KAPT

### Сравнение производительности

| Метрика | KAPT | KSP |
|---------|------|-----|
| **Скорость** | Baseline | До 2x быстрее |
| **Stub generation** | Требуется | Не требуется |
| **Kotlin понимание** | Через Java stubs | Нативное |
| **Инкрементальность** | Ограничена | Полная |

### Миграция с KAPT на KSP

```kotlin
// ШАГ 1: Добавить KSP plugin
// build.gradle.kts (project)
plugins {
    id("com.google.devtools.ksp") version "2.0.21-1.0.27" apply false
}

// ШАГ 2: Заменить kapt на ksp в app module
// build.gradle.kts (app)
plugins {
    id("com.google.devtools.ksp")
    // id("kotlin-kapt") // Удалить
}

dependencies {
    // Было
    // kapt("com.google.dagger:dagger-compiler:2.52")

    // Стало
    ksp("com.google.dagger:dagger-compiler:2.52")
}

// ШАГ 3: Убедиться что все kapt зависимости мигрированы
// Room, Moshi и другие тоже должны использовать ksp
```

### Требования для KSP

- Kotlin 1.9.0+
- Dagger 2.48+
- KSP 1.9.0-1.0.12+
- Все annotation processors должны поддерживать KSP

---

## dagger.android (Legacy)

### Зачем создавался dagger.android

До Hilt, inject в Android компоненты (Activity, Fragment, Service) требовал много boilerplate. dagger.android упрощал это:

```kotlin
// БЕЗ dagger.android
class MainActivity : AppCompatActivity() {
    @Inject lateinit var service: UserService

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent
            .activityComponentFactory()
            .create(this)
            .inject(this)
        super.onCreate(savedInstanceState)
    }
}

// С dagger.android
class MainActivity : DaggerAppCompatActivity() {
    @Inject lateinit var service: UserService

    // Inject происходит автоматически!
}
```

### Настройка dagger.android

```kotlin
// Application
class MyApp : DaggerApplication() {

    override fun applicationInjector(): AndroidInjector<out DaggerApplication> {
        return DaggerAppComponent.factory().create(this)
    }
}

// Component
@Singleton
@Component(modules = [
    AndroidInjectionModule::class,
    ActivityModule::class
])
interface AppComponent : AndroidInjector<MyApp> {

    @Component.Factory
    interface Factory : AndroidInjector.Factory<MyApp>
}

// Activity Module с @ContributesAndroidInjector
@Module
abstract class ActivityModule {

    @ContributesAndroidInjector(modules = [MainActivityModule::class])
    abstract fun contributeMainActivity(): MainActivity

    @ContributesAndroidInjector
    abstract fun contributeSettingsActivity(): SettingsActivity
}
```

### Статус dagger.android в 2024

> **Deprecated:** Google рекомендует использовать **Hilt** вместо dagger.android для новых проектов. Hilt решает те же проблемы, но проще в использовании и лучше интегрирован с Jetpack.

---

## Тестирование с Dagger

### Unit Tests: Без Dagger

```kotlin
// Для unit tests Dagger не нужен!
// Просто создавайте объекты вручную

class UserRepositoryTest {

    private lateinit var repository: UserRepository
    private val mockApi: UserApi = mockk()

    @Before
    fun setup() {
        // Прямое создание с mock-ами
        repository = UserRepository(mockApi)
    }

    @Test
    fun `getUser returns user from api`() {
        // Arrange
        every { mockApi.fetchUser("123") } returns User("123", "John")

        // Act
        val user = repository.getUser("123")

        // Assert
        assertEquals("John", user.name)
    }
}
```

### Integration Tests: Test Component

```kotlin
// Test Module с fake реализациями
@Module
class TestNetworkModule {

    @Provides
    fun provideFakeApi(): UserApi = FakeUserApi()
}

// Test Component
@Component(modules = [TestNetworkModule::class, DataModule::class])
interface TestAppComponent : AppComponent {

    @Component.Builder
    interface Builder {
        @BindsInstance
        fun context(context: Context): Builder
        fun build(): TestAppComponent
    }
}

// Тест
@RunWith(AndroidJUnit4::class)
class UserFlowTest {

    private lateinit var component: TestAppComponent

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        component = DaggerTestAppComponent.builder()
            .context(context)
            .build()
    }

    @Test
    fun testUserFlow() {
        // component предоставляет fake зависимости
    }
}
```

---

## Common Pitfalls (Типичные ошибки)

### 1. Циклические зависимости

```kotlin
// ОШИБКА: A зависит от B, B зависит от A
class ServiceA @Inject constructor(private val b: ServiceB)
class ServiceB @Inject constructor(private val a: ServiceA)
// Compile error: Dependency cycle

// РЕШЕНИЕ 1: Provider/Lazy
class ServiceA @Inject constructor(private val bProvider: Provider<ServiceB>)
class ServiceB @Inject constructor(private val a: ServiceA)

// РЕШЕНИЕ 2: Рефакторинг архитектуры (лучше)
class ServiceA @Inject constructor(private val shared: SharedService)
class ServiceB @Inject constructor(private val shared: SharedService)
```

### 2. Missing Binding

```kotlin
// ОШИБКА: Dagger не знает как создать Context
class MyService @Inject constructor(private val context: Context)
// Error: Context cannot be provided without an @Inject constructor or @Provides method

// РЕШЕНИЕ: @BindsInstance
@Component.Builder
interface Builder {
    @BindsInstance
    fun context(context: Context): Builder
    fun build(): AppComponent
}
```

### 3. Scope Mismatch

```kotlin
// ОШИБКА: @Singleton в не-Singleton Component
@Component // Без @Singleton!
interface AppComponent {
    // ...
}

@Singleton // Ошибка!
class MyService @Inject constructor()

// РЕШЕНИЕ: Добавить scope на Component
@Singleton
@Component
interface AppComponent
```

### 4. Private Fields

```kotlin
// ОШИБКА: Dagger не может inject в private fields
class MainActivity : AppCompatActivity() {
    @Inject
    private lateinit var service: UserService // ОШИБКА!
}

// РЕШЕНИЕ: internal или public
@Inject
internal lateinit var service: UserService // OK

@Inject
lateinit var service: UserService // OK
```

### 5. Overuse of @Singleton

```kotlin
// ПЛОХО: Всё Singleton
@Singleton
class UserRepository @Inject constructor()

@Singleton
class OrderRepository @Inject constructor()

@Singleton
class ProductRepository @Inject constructor()
// Все живут в памяти всё время работы приложения!

// ЛУЧШЕ: Scope по необходимости
class UserRepository @Inject constructor() // Новый каждый раз

@ActivityScope // Живёт пока Activity
class SessionManager @Inject constructor()

@Singleton // Только когда действительно нужен один экземпляр
class Analytics @Inject constructor()
```

### 6. Kotlin Wildcards

```kotlin
// ОШИБКА в Kotlin с Set multibinding
class PluginManager @Inject constructor(
    private val plugins: Set<Plugin> // Error!
)
// Error: Set<? extends Plugin> cannot be provided

// РЕШЕНИЕ: @JvmSuppressWildcards
class PluginManager @Inject constructor(
    private val plugins: Set<@JvmSuppressWildcards Plugin>
)
```

---

## Best Practices

### 1. Prefer Constructor Injection

```kotlin
// ХОРОШО: Constructor injection
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val cache: UserCache
)

// ПЛОХО: Field injection где можно избежать
class UserRepository @Inject constructor() {
    @Inject lateinit var api: UserApi // Зачем?
}
```

### 2. Структура Modules

```kotlin
// ХОРОШО: Модули по фичам
@Module
class NetworkModule { ... }

@Module
class DatabaseModule { ... }

@Module
abstract class RepositoryModule { ... }

// ПЛОХО: Один огромный модуль
@Module
class AppModule {
    // 50+ @Provides методов
}
```

### 3. @Binds вместо @Provides для интерфейсов

```kotlin
// ХОРОШО: @Binds — эффективнее
@Module
abstract class RepositoryModule {
    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// ПЛОХО: @Provides для интерфейсов
@Module
class RepositoryModule {
    @Provides
    fun provideUserRepository(impl: UserRepositoryImpl): UserRepository = impl
}
```

### 4. Custom Qualifiers вместо @Named

```kotlin
// ХОРОШО: Type-safe qualifiers
@Qualifier
annotation class BaseUrl

class Api @Inject constructor(@BaseUrl url: String)

// ПЛОХО: String-based @Named
class Api @Inject constructor(@Named("baseUrl") url: String)
// Опечатка в строке = runtime ошибка
```

### 5. Component per Feature в Multi-module

```kotlin
// Feature module
@FeatureScope
@Subcomponent(modules = [FeatureModule::class])
interface FeatureComponent {
    fun inject(fragment: FeatureFragment)

    @Subcomponent.Factory
    interface Factory {
        fun create(): FeatureComponent
    }
}

// Регистрация в app module
@Module(subcomponents = [FeatureComponent::class])
interface FeatureBindingModule
```

---

## Dagger vs Hilt: Когда что использовать

| Критерий | Dagger 2 | Hilt |
|----------|----------|------|
| **Новый проект** | — | ✅ |
| **Legacy проект с Dagger** | Продолжать или мигрировать | Мигрировать постепенно |
| **Максимальный контроль** | ✅ | — |
| **Быстрый старт** | — | ✅ |
| **Compose/Jetpack** | Ручная интеграция | Встроенная |
| **Multi-module** | Ручная настройка | Автоматическая |
| **Понимание DI** | Глубокое | — |

### Когда оставаться на Dagger 2

1. Проект уже использует Dagger и работает стабильно
2. Нужен полный контроль над Component hierarchy
3. Специфические требования к scope management
4. Команда хорошо знает Dagger

### Когда мигрировать на Hilt

1. Новый проект
2. Упростить boilerplate
3. Лучшая интеграция с Jetpack (ViewModel, WorkManager, Navigation)
4. Стандартизация для команды

---

## Источники

### Официальная документация
- [Dagger Dev Guide](https://dagger.dev/dev-guide/)
- [Android Developers - Dagger](https://developer.android.com/training/dependency-injection/dagger-android)
- [Dagger KSP Migration](https://dagger.dev/dev-guide/ksp.html)

### Технические статьи
- [Vogella Dagger 2 Tutorial](https://www.vogella.com/tutorials/Dagger/article.html)
- [CodePath Dagger 2 Guide](https://guides.codepath.com/android/dependency-injection-with-dagger-2)
- [Baeldung Introduction to Dagger 2](https://www.baeldung.com/dagger-2)
- [Dagger 2 Multibindings](https://medium.com/mobile-app-development-publication/dagger-2-multibindings-reference-rewrite-70c23842b782)
- [Dagger 2 Scopes and Subcomponents](https://medium.com/tompee/dagger-2-scopes-and-subcomponents-d54d58511781)

### Миграция
- [Dagger 1 to 2 Migration](https://dagger.dev/dev-guide/dagger-1-migration.html)
- [KAPT to KSP Migration](https://developer.android.com/build/migrate-to-ksp)

---

## Связанные материалы

- [[dependency-injection-fundamentals]] — Теория DI
- [[android-hilt-deep-dive]] — Hilt (построен на Dagger)
- [[android-koin-deep-dive]] — Альтернатива: Koin
- [[android-kotlin-inject-deep-dive]] — Альтернатива: kotlin-inject
- [[android-metro-deep-dive]] — Новейший: Metro
