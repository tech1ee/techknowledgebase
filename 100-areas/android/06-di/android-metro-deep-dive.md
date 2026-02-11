---
title: "Metro: Deep-Dive — DI фреймворк нового поколения"
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
  - "[[android-kotlin-inject-deep-dive]]"
prerequisites:
  - "[[android-architecture-patterns]]"
  - "[[android-dagger-deep-dive]]"
  - "[[android-kotlin-inject-deep-dive]]"
---

# Metro: Deep-Dive

## TL;DR

**Metro** — новейший (апрель 2025) compile-time DI framework от Zac Sweers. Реализован как **Kotlin compiler plugin** (не annotation processor), что даёт до 60% ускорения билдов. Объединяет лучшее из Dagger, Anvil и kotlin-inject: compile-time safety + Anvil-style aggregation + kotlin-inject API + KMP support. Cash App успешно мигрировал 1500 модулей. Поддерживает optional dependencies, top-level function injection, Composable injection.

---

## ПОЧЕМУ: Зачем нужен Metro

### Проблема: Фрагментация DI инструментов

```
┌─────────────────────────────────────────────────────────────┐
│                    DI ECOSYSTEM BEFORE METRO                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dagger           │  Anvil          │  kotlin-inject       │
│  ─────────────    │  ─────────────  │  ─────────────────   │
│  • Compile-time   │  • Aggregation  │  • KMP support       │
│  • Performance    │  • Contrib DI   │  • Kotlin-first      │
│  • Complex API    │  • K1 only!     │  • Simple API        │
│  • No KMP         │  • Dagger req.  │  • No aggregation    │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ПРОБЛЕМА: Нужно выбирать между:                           │
│  • Compile-time safety (Dagger) OR KMP (kotlin-inject)     │
│  • Simple API (kotlin-inject) OR Aggregation (Anvil)       │
│  • K2 support (kotlin-inject) OR Performance (Dagger)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Metro: Объединение лучшего

```
┌─────────────────────────────────────────────────────────────┐
│                         METRO                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Dagger    │  │   Anvil     │  │kotlin-inject│        │
│  │  runtime    │  │ aggregation │  │    API      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                     │
│              │   METRO = ALL IN ONE  │                     │
│              │                       │                     │
│              │  • Compiler Plugin    │ ◀── НЕ annotation   │
│              │  • FIR/IR codegen     │     processor       │
│              │  • K2 compatible      │                     │
│              │  • KMP support        │                     │
│              │  • Anvil aggregation  │                     │
│              │  • Dagger interop     │                     │
│              │  • kotlin-inject API  │                     │
│              │                       │                     │
│              │  + NEW FEATURES:      │                     │
│              │  • Optional deps      │                     │
│              │  • Top-level inject   │                     │
│              │  • Composable inject  │                     │
│              │  • Private providers  │                     │
│              └───────────────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Почему compiler plugin лучше annotation processor

| Аспект | KAPT/KSP | Metro (Compiler Plugin) |
|--------|----------|-------------------------|
| **Запуск** | Отдельная фаза | Интегрирован в компиляцию |
| **Frontend invocations** | Дополнительные | Нет |
| **Code output** | Source files | FIR/IR напрямую |
| **Private access** | ❌ Невозможен | ✅ Поддерживается |
| **Default values** | ❌ Копирование | ✅ Reuse выражений |
| **Build speed** | Baseline | До 60% быстрее |

### Production adoption: Cash App

Cash App мигрировал **1500 Android модулей** на Metro:

| Метрика | До (Dagger/Anvil) | После (Metro) | Улучшение |
|---------|-------------------|---------------|-----------|
| Clean build | 243s | 202s | **-17%** |
| Incremental (ABI) | Baseline | | **-47%** |
| Incremental (non-ABI) | Baseline | | **-59%** |

---

## ИСТОРИЯ

```
2025-04-03  Zac Sweers анонсирует Metro
            ├── Compiler plugin (не KSP)
            ├── K2 compatible с первого дня
            └── Interop с Dagger и kotlin-inject

2025-04     Cash App начинает миграцию
            └── 1500 модулей

2025-09     DroidKaigi 2025: доклад "Navigating DI with Metro"

2025-Q4     Metro набирает популярность
            ├── Версия 0.1.x
            └── Active development
```

### Автор: Zac Sweers

Zac Sweers — известный Android разработчик:
- Работает в Cash App (Block/Square)
- Автор **Anvil-KSP** (форк для K2)
- Мейнтейнер **Moshi**, **kotlinx-metadata**
- Один из ведущих экспертов по Kotlin tooling

---

## ЧТО: Архитектура Metro

### Основные концепции

```
┌─────────────────────────────────────────────────────────────┐
│                    METRO ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │ @DependencyGraph│  ◀── Interface или abstract class     │
│  │                 │      (аналог @Component)              │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ содержит                                        │
│           ▼                                                 │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │  Entry points   │      │   @Provides     │             │
│  │  (properties)   │      │   (functions)   │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │@ContributesTo   │      │@ContributesBinding            │
│  │ (Anvil-style)   │      │ (auto-bind)     │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  UNIQUE FEATURES:                                          │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │ Optional deps   │      │ Top-level inject│             │
│  │ (default params)│      │ (Composable)    │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Annotations

| Annotation | Назначение | Dagger аналог |
|------------|------------|---------------|
| `@DependencyGraph` | Определение графа | `@Component` |
| `@Inject` | Constructor injection | `@Inject` |
| `@Provides` | Provide binding | `@Provides` |
| `@Binds` | Bind interface | `@Binds` |
| `@Scope` | Lifecycle управление | `@Scope` |
| `@Singleton` | Single instance | `@Singleton` |
| `@Qualifier` | Различение типов | `@Qualifier` |
| `@Assisted` | Runtime параметр | `@Assisted` |
| `@AssistedFactory` | Factory для assisted | `@AssistedFactory` |
| `@ContributesTo` | Auto-include в граф | Anvil `@ContributesTo` |
| `@ContributesBinding` | Auto-bind interface | Anvil `@ContributesBinding` |
| `@IntoSet` / `@IntoMap` | Multibindings | `@IntoSet` / `@IntoMap` |

---

## КАК: Практическое использование

### 1. Настройка проекта

```kotlin
// build.gradle.kts (project)
plugins {
    id("dev.zacsweers.metro") version "0.1.1" apply false
}

// build.gradle.kts (app)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("dev.zacsweers.metro")
}

// Опционально: конфигурация
metro {
    // debug = true  // Включить debug output
}
```

#### KMP проект

```kotlin
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("dev.zacsweers.metro")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    jvm()

    sourceSets {
        commonMain.dependencies {
            implementation("dev.zacsweers.metro:metro-runtime:0.1.1")
        }
    }
}
```

### 2. Базовый @DependencyGraph

```kotlin
// Определение графа (аналог Component)
@DependencyGraph
interface AppGraph {
    // Entry points — как получить зависимости
    val httpClient: HttpClient
    val userRepository: UserRepository
}

// Класс с @Inject
@Inject
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache
)

// Создание графа
val graph = AppGraph::class.createGraph()
val repo = graph.userRepository
```

### 3. @Provides: Внешние зависимости

```kotlin
@DependencyGraph
interface AppGraph {
    val retrofit: Retrofit

    // @Provides прямо в графе (как kotlin-inject)
    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    fun provideRetrofit(client: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(client)
            .build()
    }
}
```

### 4. Optional Dependencies (уникальная фича!)

```kotlin
// Metro поддерживает default parameter values!
@Inject
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache = InMemoryCache(),  // Default если нет binding
    private val logger: Logger = NoOpLogger()        // Optional dependency
)

@DependencyGraph
interface AppGraph {
    val userRepository: UserRepository

    // Если нет @Provides для Logger — используется default
    @Provides
    fun provideApi(): UserApi = UserApiImpl()

    @Provides
    fun provideCache(): UserCache = RoomCache()
    // Logger не предоставлен — будет NoOpLogger()
}
```

### 5. Private @Provides (уникальная фича!)

```kotlin
// Metro может генерировать код для private членов!
@DependencyGraph
interface AppGraph {
    val userRepository: UserRepository

    // Private @Provides — невозможно в Dagger/kotlin-inject
    @Provides
    private fun provideSecret(): ApiKey {
        return ApiKey(BuildConfig.API_KEY)
    }
}
```

### 6. Top-Level Function Injection

```kotlin
// Inject функций на верхнем уровне!
@Inject
fun processUser(
    repository: UserRepository,
    analytics: Analytics
): User {
    analytics.track("user_processed")
    return repository.getUser()
}

@DependencyGraph
interface AppGraph {
    // Получаем inject-нутую функцию
    val processUser: () -> User
}
```

### 7. Composable Injection (уникальная фича!)

```kotlin
// Inject @Composable функций!
@Inject
@Composable
fun UserScreen(
    viewModel: UserViewModel,  // DI
    modifier: Modifier = Modifier  // UI параметр
) {
    val state by viewModel.state.collectAsState()
    // ...
}

@DependencyGraph
interface AppGraph {
    // Получаем inject-нутый Composable
    val userScreen: @Composable (Modifier) -> Unit
}

// Использование
@Composable
fun App() {
    val graph = remember { AppGraph::class.createGraph() }
    graph.userScreen(Modifier.fillMaxSize())
}
```

### 8. @Scope: Lifecycle управление

```kotlin
@Scope
annotation class Singleton

@Scope
annotation class ActivityScope

@Singleton
@DependencyGraph
interface AppGraph {
    val analytics: Analytics  // Singleton

    @Singleton
    @Provides
    fun provideAnalytics(): Analytics = AnalyticsImpl()
}

@ActivityScope
@DependencyGraph
interface ActivityGraph {
    @get:ActivityScope
    val presenter: MainPresenter
}
```

### 9. Graph Hierarchy (Parent/Child)

```kotlin
// Parent graph
@Singleton
@DependencyGraph
interface AppGraph {
    val analytics: Analytics
}

// Child graph — наследует от parent
@ActivityScope
@DependencyGraph
interface ActivityGraph {
    // Включаем parent
    @get:Includes
    val parent: AppGraph

    val presenter: MainPresenter  // Может использовать Analytics из parent
}

// Использование
val appGraph = AppGraph::class.createGraph()
val activityGraph = ActivityGraph::class.createGraph(parent = appGraph)
```

### 10. Anvil-Style Aggregation

```kotlin
// Автоматическое добавление в граф — как Anvil!
@ContributesTo(AppGraph::class)
interface AnalyticsComponent {
    @Provides
    fun provideAnalytics(): Analytics = AnalyticsImpl()
}

// Auto-bind интерфейса
@ContributesBinding(AppGraph::class)
@Inject
class UserRepositoryImpl(
    private val api: UserApi
) : UserRepository

// Граф автоматически включает все @ContributesTo
@DependencyGraph
interface AppGraph {
    val userRepository: UserRepository  // UserRepositoryImpl auto-bound
}
```

### 11. Multibindings

```kotlin
// Set multibinding
@ContributesBinding(AppGraph::class)
@IntoSet
@Inject
class LoggingPlugin : Plugin

@ContributesBinding(AppGraph::class)
@IntoSet
@Inject
class AnalyticsPlugin : Plugin

@DependencyGraph
interface AppGraph {
    val plugins: Set<Plugin>  // Contains both plugins
}

// Map multibinding
@MapKey
annotation class StringKey(val value: String)

@ContributesBinding(AppGraph::class)
@IntoMap
@StringKey("login")
@Inject
class LoginHandler : Handler

@DependencyGraph
interface AppGraph {
    val handlers: Map<String, Handler>
}
```

### 12. Assisted Injection

```kotlin
@Inject
class UserDetailViewModel(
    @Assisted private val userId: String,  // Runtime
    private val repository: UserRepository  // DI
)

@AssistedFactory
interface UserDetailViewModelFactory {
    fun create(userId: String): UserDetailViewModel
}

@DependencyGraph
interface AppGraph {
    val viewModelFactory: UserDetailViewModelFactory
}

// Использование
val factory = graph.viewModelFactory
val viewModel = factory.create("user-123")
```

---

## Interop с Dagger и kotlin-inject

### Dagger Interop

Metro может использовать Dagger-сгенерированные фабрики:

```kotlin
// Dagger Module (существующий)
@Module
class LegacyModule {
    @Provides
    fun provideApi(): Api = ApiImpl()
}

// Metro Graph с Dagger interop
@DependencyGraph
interface AppGraph {
    // Включаем Dagger component
    @get:Includes
    val daggerComponent: LegacyDaggerComponent

    val api: Api  // Из Dagger
}
```

### kotlin-inject Interop

```kotlin
// kotlin-inject Component (существующий)
@Component
abstract class LegacyComponent {
    abstract val repository: Repository
}

// Metro Graph
@DependencyGraph
interface AppGraph {
    @get:Includes
    val kotlinInjectComponent: LegacyComponent

    val repository: Repository  // Из kotlin-inject
}
```

---

## Миграция с Dagger

### Стратегия (из опыта Cash App)

1. **Dual-build setup** — Gradle property для переключения
2. **Постепенная миграция** по модулям
3. **Interop** — Metro и Dagger работают вместе

```kotlin
// gradle.properties
mad.di=metro  # или dagger

// build.gradle.kts
val diFramework = project.findProperty("mad.di") ?: "dagger"

if (diFramework == "metro") {
    apply(plugin = "dev.zacsweers.metro")
} else {
    apply(plugin = "dagger.hilt.android.plugin")
}
```

### Основные изменения

| Dagger | Metro |
|--------|-------|
| `@Component` | `@DependencyGraph` |
| `@Component.Factory` | Factory-style creation |
| `@Module` | `@Provides` в графе или `@ContributesTo` |
| `@Binds` | `@ContributesBinding` |
| `@Subcomponent` | Graph hierarchy с `@Includes` |

### Типичные проблемы миграции

```kotlin
// 1. Scope на @Binds (Dagger) → на типе (Metro)

// DAGGER
@Module
abstract class RepoModule {
    @Binds
    @Singleton  // На методе
    abstract fun bind(impl: RepoImpl): Repo
}

// METRO
@ContributesBinding(AppGraph::class)
@Singleton  // На классе!
@Inject
class RepoImpl : Repo

// 2. Component.Builder → Factory

// DAGGER
@Component.Builder
interface Builder {
    @BindsInstance
    fun context(context: Context): Builder
    fun build(): AppComponent
}

// METRO
@DependencyGraph
interface AppGraph {
    @get:Provides
    val context: Context  // Передаётся при создании

    companion object {
        fun create(context: Context): AppGraph
    }
}
```

---

## Сравнение с альтернативами

| Feature | Metro | Dagger | kotlin-inject | Koin |
|---------|-------|--------|---------------|------|
| **Compile-time safety** | ✅ | ✅ | ✅ | ❌ |
| **KMP support** | ✅ | ❌ | ✅ | ✅ |
| **Aggregation** | ✅ Anvil-style | ❌ (Anvil) | ❌ | ❌ |
| **Optional deps** | ✅ | ❌ | ❌ | ✅ |
| **Private providers** | ✅ | ❌ | ❌ | — |
| **Composable inject** | ✅ | ❌ | ❌ | ❌ |
| **Build speed** | ⚡️ Fastest | Slow | Fast | — |
| **K2 support** | ✅ | ✅ | ✅ | ✅ |
| **Maturity** | New (2025) | Mature | Growing | Mature |

---

## Best Practices

### 1. Используйте Optional Dependencies

```kotlin
// ХОРОШО: Default values для опциональных зависимостей
@Inject
class UserRepository(
    private val api: UserApi,
    private val logger: Logger = NoOpLogger(),
    private val cache: Cache = InMemoryCache()
)

// ПЛОХО: Nullable с проверками
@Inject
class UserRepository(
    private val api: UserApi,
    private val logger: Logger?  // Проверки везде
)
```

### 2. @ContributesBinding для интерфейсов

```kotlin
// ХОРОШО: Auto-bind
@ContributesBinding(AppGraph::class)
@Inject
class UserRepositoryImpl : UserRepository

// ПЛОХО: Manual @Provides для каждого интерфейса
@DependencyGraph
interface AppGraph {
    @Provides
    fun bindRepo(impl: UserRepositoryImpl): UserRepository = impl
}
```

### 3. Организация по фичам

```kotlin
// feature-user/
@ContributesTo(AppGraph::class)
interface UserComponent {
    @Provides
    fun provideUserApi(): UserApi
}

@ContributesBinding(AppGraph::class)
@Inject
class UserRepositoryImpl : UserRepository

// feature-orders/
@ContributesTo(AppGraph::class)
interface OrdersComponent { ... }

// app/
@DependencyGraph
interface AppGraph  // Автоматически включает все @ContributesTo
```

### 4. Composable Injection для UI

```kotlin
// ХОРОШО: Inject Composable напрямую
@Inject
@Composable
fun UserScreen(viewModel: UserViewModel) { ... }

// ПЛОХО: Manual wiring в каждом экране
@Composable
fun UserScreen() {
    val viewModel = remember { graph.userViewModel }
    // ...
}
```

---

## Common Pitfalls

### 1. Забыть @Inject

```kotlin
// ОШИБКА
class UserRepository(private val api: UserApi)
// Error: No binding found

// РЕШЕНИЕ
@Inject
class UserRepository(private val api: UserApi)
```

### 2. Scope на @Provides вместо типа (при миграции с Dagger)

```kotlin
// DAGGER стиль (работает, но не рекомендуется)
@Provides
@Singleton
fun provideRepo(): Repository = RepositoryImpl()

// METRO рекомендация: scope на типе
@Singleton
@Inject
class RepositoryImpl : Repository
```

### 3. Circular dependencies

```kotlin
// ОШИБКА
@Inject
class A(private val b: B)

@Inject
class B(private val a: A)
// Error: Dependency cycle

// РЕШЕНИЕ: Lazy
@Inject
class A(private val b: Lazy<B>)
```

---

## Roadmap

Metro в активной разработке. Запланированные фичи:

- **Nullable bindings** — `@Provides fun maybeProvide(): Foo?`
- **@ContributesGraphExtension** — расширение графов
- **Unused binding detection** — обнаружение неиспользуемых зависимостей
- **IDE плагин** — улучшенная навигация

---

## Источники

### Официальные
- [Metro Documentation](https://zacsweers.github.io/metro/latest/)
- [Metro GitHub](https://github.com/ZacSweers/metro)
- [Introducing Metro (Zac Sweers)](https://www.zacsweers.dev/introducing-metro/)

### Case Studies
- [Cash Android Moves to Metro](https://code.cash.app/cash-android-moves-to-metro)

### Презентации
- [DroidKaigi 2025: Navigating DI with Metro](https://speakerdeck.com/zacsweers/navigating-dependency-injection-with-metro)

---

## Связь с другими темами

**[[dependency-injection-fundamentals]]** — теоретическая основа всех DI-фреймворков, включая Metro. Понимание принципов Inversion of Control, Composition Root и разницы между compile-time и runtime DI помогает оценить, почему Metro выбрал подход compiler plugin вместо annotation processing. Metro реализует все классические DI-паттерны, но оптимизирует их через интеграцию в Kotlin compiler. Начните с теории, затем переходите к Metro.

**[[android-dagger-deep-dive]]** — Dagger является предшественником Metro и основным фреймворком для interop при миграции. Metro поддерживает инклюд Dagger-компонентов через @Includes, что позволяет постепенную миграцию (опыт Cash App с 1500 модулями). Понимание Dagger concepts (Components, Modules, Scopes, Subcomponents) критично для эффективной миграции на Metro. Изучите Dagger первым, если работаете с legacy-проектом.

**[[android-kotlin-inject-deep-dive]]** — kotlin-inject разделяет с Metro подход к Kotlin-first API и KMP-поддержку. Metro заимствовал API-дизайн kotlin-inject (@Inject на конструкторах, @Provides прямо в графе), добавив Anvil-style aggregation. Понимание kotlin-inject помогает быстрее освоить Metro API и оценить уникальные фичи Metro (optional deps, Composable injection). Для KMP-проектов Metro предпочтительнее kotlin-inject благодаря aggregation.

---

## Источники и дальнейшее чтение

- Moskala (2021). *Effective Kotlin*. — best practices Kotlin, включая compiler plugins, DSL-дизайн и паттерны создания объектов, которые помогают понять архитектурные решения Metro как Kotlin compiler plugin.
- Bloch (2018). *Effective Java*. — классические принципы API-дизайна и dependency management (Item 5: Prefer dependency injection), которые лежат в основе всех DI-фреймворков включая Metro.
- Leiva (2017). *Kotlin for Android Developers*. — практические паттерны Kotlin для Android, включая организацию зависимостей и модульную архитектуру, что даёт контекст для понимания Metro в Android-проектах.
