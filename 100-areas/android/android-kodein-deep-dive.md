# Kodein: Deep-Dive

---
type: deep-dive
level: intermediate
topics: [kotlin, kmp, dependency-injection, kodein, runtime, multiplatform]
related: [[dependency-injection-fundamentals]], [[android-koin-deep-dive]], [[android-kotlin-inject-deep-dive]]
version: "2024-2025"
---

## TL;DR

**Kodein** (KOtlin DEpendency INjection) — runtime DI framework для Kotlin с поддержкой KMP. Альтернатива Koin с ключевым отличием: поддержка **множественных контейнеров** (не только глобальный). Type-safe DSL без reflection. Идеален для разработки SDK/библиотек где нужна изоляция DI. Версия 7.x, поддерживает все KMP таргеты. Менее популярен чем Koin, но более гибкий в модульной архитектуре.

---

## ПОЧЕМУ: Зачем нужен Kodein

### Проблема глобального контейнера (Koin)

```kotlin
// KOIN: Один глобальный контейнер
// library/build.gradle
startKoin {  // Кто вызовет в библиотеке?
    modules(libraryModule)
}

// app/build.gradle
startKoin {  // А если app тоже вызывает?
    modules(appModule)
}
// Конфликт! Koin требует единственный startKoin

// KODEIN: Множественные контейнеры
// library/
val libraryDI = DI {
    bind<LibraryService>() with singleton { LibraryServiceImpl() }
}

// app/
val appDI = DI {
    extend(libraryDI)  // Включаем library DI
    bind<AppService>() with singleton { AppServiceImpl() }
}
// Нет конфликта — каждый модуль независим
```

### Позиционирование Kodein

```
┌─────────────────────────────────────────────────────────────┐
│                    RUNTIME DI FRAMEWORKS                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      KOIN                           │   │
│  │  • Глобальный контейнер                             │   │
│  │  • Простой API                                      │   │
│  │  • Популярнее                                       │   │
│  │  • Отличная документация                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     KODEIN                          │   │
│  │  • Множественные контейнеры                         │   │
│  │  • Гибкая модульность                               │   │
│  │  • Идеален для SDK/библиотек                        │   │
│  │  • Более verbose                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Общее:                                                     │
│  • Runtime DI (не compile-time)                            │
│  • KMP support                                              │
│  • Без reflection                                           │
│  • Ошибки в runtime                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда выбирать Kodein

| Сценарий | Kodein | Koin |
|----------|--------|------|
| **Разработка SDK/библиотеки** | ✅ Идеально | ⚠️ Проблемы с глобальным контейнером |
| **Множественные DI контейнеры** | ✅ | ❌ |
| **Модульная архитектура** | ✅ | ✅ |
| **Простота** | Средняя | ✅ Проще |
| **Популярность/Community** | Меньше | ✅ Больше |
| **Документация** | Хорошая | ✅ Отличная |

**Идеально для:**
- Разработки SDK, где потребитель может использовать другой DI
- Сложных модульных архитектур с изолированными графами
- Проектов, где нужны независимые DI контейнеры

**Не подходит для:**
- Простых приложений (Koin проще)
- Проектов где нужна compile-time safety (Dagger/Hilt)
- Команд без опыта DI (Koin легче для обучения)

---

## ИСТОРИЯ

```
2017    Kodein 4.x — первые версии
        └── KMP support с ранних версий

2018    Kodein 5.x — стабилизация API

2019    Kodein 6.x — переход на новое именование
        └── Разделение на kodein-di-*

2020    Kodein 7.0 — текущий major release
        └── Улучшенная модульность

2024    Kodein 7.27 — актуальная версия
        ├── Kotlin 2.2+ support
        └── JDK 17 minimum
```

### Экосистема Kodein (kosi-libs)

Kodein — часть экосистемы KOSI (Kodein Open Source Initiative):
- **Kodein-DI** — Dependency Injection
- **Kodein-DB** — NoSQL база данных
- **Kodein-Log** — Logging
- **Kodein-Memory** — Memory management

---

## ЧТО: Архитектура Kodein

### Основные концепции

```
┌─────────────────────────────────────────────────────────────┐
│                    KODEIN ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │   DI Container  │  ◀── Контейнер зависимостей           │
│  │   DI { ... }    │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           │ содержит                                        │
│           ▼                                                 │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │    Bindings     │      │    Modules      │             │
│  │  bind<T>() with │      │ DI.Module { }   │             │
│  └─────────────────┘      └─────────────────┘             │
│                                                             │
│  Binding Types:                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │singleton │ │ provider │ │ factory  │ │ multiton │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                             │
│  Retrieval:                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │instance()│ │provider()│ │ factory()│                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │          Multiple Containers            │               │
│  │  extend(), import(), copy()            │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Binding Types

| Binding | Описание | Когда использовать |
|---------|----------|-------------------|
| `singleton` | Один экземпляр | Shared state, repositories |
| `eagerSingleton` | Создаётся сразу | Инициализация при старте |
| `provider` | Новый каждый раз | Stateless services |
| `factory` | Новый с аргументом | Параметризованные объекты |
| `multiton` | Singleton per argument | Cache per key |

### Retrieval Methods

| Method | Описание |
|--------|----------|
| `instance()` | Получить экземпляр |
| `instanceOrNull()` | Получить или null |
| `provider()` | Получить функцию-провайдер |
| `factory()` | Получить функцию-фабрику |

---

## КАК: Практическое использование

### 1. Настройка проекта

```kotlin
// build.gradle.kts

// Core library
implementation("org.kodein.di:kodein-di:7.27.0")

// Android specific
implementation("org.kodein.di:kodein-di-framework-android-x:7.27.0")

// ViewModel support
implementation("org.kodein.di:kodein-di-framework-android-x-viewmodel:7.27.0")

// Compose support
implementation("org.kodein.di:kodein-di-framework-compose:7.27.0")
```

#### KMP проект

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("org.kodein.di:kodein-di:7.27.0")
        }
        androidMain.dependencies {
            implementation("org.kodein.di:kodein-di-framework-android-x:7.27.0")
        }
    }
}
```

### 2. Базовый DI контейнер

```kotlin
// Создание контейнера
val di = DI {
    // Singleton — один экземпляр
    bind<UserRepository>() with singleton {
        UserRepositoryImpl(instance())
    }

    // Provider — новый каждый раз
    bind<Logger>() with provider {
        ConsoleLogger()
    }

    // Eager singleton — создаётся сразу
    bind<Analytics>() with eagerSingleton {
        AnalyticsImpl()
    }
}

// Получение зависимостей
val repository: UserRepository by di.instance()
val logger: Logger by di.instance()
```

### 3. Bindings в деталях

#### Singleton

```kotlin
val di = DI {
    // Singleton — lazy initialization, один экземпляр
    bind<Database>() with singleton {
        Room.databaseBuilder(
            instance(), // Context
            AppDatabase::class.java,
            "app.db"
        ).build()
    }
}

// Всегда один и тот же экземпляр
val db1: Database by di.instance()
val db2: Database by di.instance()
assert(db1 === db2) // true
```

#### Provider

```kotlin
val di = DI {
    // Provider — новый экземпляр каждый раз
    bind<RequestHandler>() with provider {
        RequestHandler(instance())
    }
}

val handler1: RequestHandler by di.instance()
val handler2: RequestHandler by di.instance()
assert(handler1 !== handler2) // true — разные экземпляры
```

#### Factory

```kotlin
val di = DI {
    // Factory — принимает аргумент
    bind<UserSession>() with factory { userId: String ->
        UserSession(userId, instance())
    }
}

// Использование
val sessionFactory: (String) -> UserSession by di.factory()
val session = sessionFactory("user-123")

// Или напрямую с аргументом
val session: UserSession by di.instance(arg = "user-123")
```

#### Multiton

```kotlin
val di = DI {
    // Multiton — singleton per argument
    bind<UserCache>() with multiton { userId: String ->
        UserCache(userId)
    }
}

// Для одного userId — один и тот же экземпляр
val cache1: UserCache by di.instance(arg = "user-1")
val cache2: UserCache by di.instance(arg = "user-1")
val cache3: UserCache by di.instance(arg = "user-2")

assert(cache1 === cache2) // true — тот же userId
assert(cache1 !== cache3) // true — разные userId
```

### 4. Tags (Qualifiers)

```kotlin
val di = DI {
    // Tagged bindings для различения одинаковых типов
    bind<String>(tag = "baseUrl") with singleton { "https://api.example.com" }
    bind<String>(tag = "authUrl") with singleton { "https://auth.example.com" }

    bind<CoroutineDispatcher>(tag = "io") with singleton { Dispatchers.IO }
    bind<CoroutineDispatcher>(tag = "main") with singleton { Dispatchers.Main }
}

// Получение с тегом
val baseUrl: String by di.instance(tag = "baseUrl")
val ioDispatcher: CoroutineDispatcher by di.instance(tag = "io")
```

### 5. Modules

```kotlin
// Определение модуля
val networkModule = DI.Module("network") {
    bind<OkHttpClient>() with singleton {
        OkHttpClient.Builder().build()
    }

    bind<Retrofit>() with singleton {
        Retrofit.Builder()
            .client(instance())
            .baseUrl("https://api.example.com/")
            .build()
    }

    bind<UserApi>() with singleton {
        instance<Retrofit>().create(UserApi::class.java)
    }
}

val databaseModule = DI.Module("database") {
    bind<AppDatabase>() with singleton {
        Room.databaseBuilder(instance(), AppDatabase::class.java, "app.db").build()
    }
}

// Использование модулей
val di = DI {
    import(networkModule)
    import(databaseModule)

    // Дополнительные bindings
    bind<UserRepository>() with singleton {
        UserRepositoryImpl(instance(), instance())
    }
}
```

### 6. Extending Containers

```kotlin
// Базовый контейнер
val baseDI = DI {
    bind<Logger>() with singleton { ConsoleLogger() }
}

// Расширенный контейнер
val extendedDI = DI {
    extend(baseDI)  // Наследуем все bindings

    // Добавляем новые
    bind<UserRepository>() with singleton {
        UserRepositoryImpl(instance())
    }
}

// Copy — создаёт копию с возможностью override
val overriddenDI = baseDI.copy {
    bind<Logger>(overrides = true) with singleton { FileLogger() }
}
```

### 7. Android Integration

#### Application

```kotlin
class MyApp : Application(), DIAware {

    override val di = DI.lazy {
        import(androidXModule(this@MyApp))  // Android bindings

        bind<UserRepository>() with singleton {
            UserRepositoryImpl(instance())
        }
    }
}
```

#### Activity

```kotlin
class MainActivity : AppCompatActivity(), DIAware {

    // Получаем DI от ближайшего parent (Application)
    override val di by closestDI()

    // Или можно создать свой
    // override val di by retainedSubDI { ... }

    private val userRepository: UserRepository by instance()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // userRepository готов к использованию
    }
}
```

#### Fragment

```kotlin
class UserFragment : Fragment(), DIAware {

    override val di by closestDI()

    private val viewModel: UserViewModel by instance()
}
```

### 8. ViewModel Integration

```kotlin
// Binding ViewModel
val viewModelModule = DI.Module("viewModel") {
    // Provider binding для plain ViewModel
    bindProvider {
        UserViewModel(instance(), instance())
    }

    // Factory binding для ViewModel с SavedStateHandle
    bindFactory { savedStateHandle: SavedStateHandle ->
        DetailViewModel(savedStateHandle, instance())
    }
}

// В Activity/Fragment
class UserActivity : AppCompatActivity(), DIAware {

    override val di by closestDI()

    // Plain ViewModel
    private val viewModel: UserViewModel by viewModel()

    // ViewModel с SavedStateHandle
    private val detailViewModel: DetailViewModel by viewModelWithSavedStateHandle()
}
```

#### ViewModel с DIAware

```kotlin
class MyViewModel(
    app: Application
) : AndroidViewModel(app), DIAware {

    override val di by di()  // Получаем DI из Application

    private val repository: UserRepository by instance()

    fun loadUser(id: String) = viewModelScope.launch {
        repository.getUser(id)
    }
}
```

### 9. Scopes

#### AndroidLifecycleScope

```kotlin
val di = DI {
    // Scope привязанный к lifecycle Activity
    bind<Presenter>() with scoped(AndroidLifecycleScope<Activity>()).singleton {
        MainPresenter(instance())
    }

    // Scope привязанный к lifecycle Fragment
    bind<Controller>() with scoped(AndroidLifecycleScope<Fragment>()).singleton {
        FragmentController(context)
    }
}
```

#### Custom Scopes

```kotlin
// Создание custom scope
val sessionScope = object : Scope<UserSession> {
    private val registry = ScopeRegistry()

    override fun getRegistry(context: UserSession): ScopeRegistry = registry

    fun clear() = registry.clear()
}

val di = DI {
    bind<SessionService>() with scoped(sessionScope).singleton {
        SessionServiceImpl()
    }
}

// Очистка scope
sessionScope.clear()
```

### 10. Compose Integration

```kotlin
// LocalDI для Compose
@Composable
fun App() {
    val di = DI {
        bind<UserRepository>() with singleton { UserRepositoryImpl() }
    }

    withDI(di) {
        // Все дочерние Composables имеют доступ к DI
        MainScreen()
    }
}

@Composable
fun MainScreen() {
    val repository: UserRepository by rememberInstance()

    // Использование repository
}

// Или с LocalDI
@Composable
fun UserList() {
    val di = LocalDI.current
    val repository: UserRepository by di.instance()

    // ...
}
```

---

## Kodein vs Koin: Детальное сравнение

| Аспект | Kodein | Koin |
|--------|--------|------|
| **Контейнер** | Множественные | Единственный глобальный |
| **Инициализация** | Не требует startKoin | Требует startKoin |
| **Library-friendly** | ✅ Да | ⚠️ Проблематично |
| **Boilerplate** | Больше | Меньше |
| **DSL syntax** | `bind<T>() with singleton { }` | `single { }` |
| **Module system** | `DI.Module`, `import()` | `module { }`, `modules()` |
| **ViewModel** | `by viewModel()` | `by viewModel()` |
| **Compose** | `withDI()`, `rememberInstance()` | `KoinApplication`, `koinInject()` |
| **Популярность** | ~1.5K stars | ~9K stars |
| **Документация** | Хорошая | Отличная |

### Синтаксис: Kodein vs Koin

```kotlin
// KODEIN
val di = DI {
    bind<UserApi>() with singleton { UserApiImpl() }
    bind<UserRepository>() with singleton { UserRepositoryImpl(instance()) }
}

val repository: UserRepository by di.instance()

// KOIN
val appModule = module {
    single<UserApi> { UserApiImpl() }
    single<UserRepository> { UserRepositoryImpl(get()) }
}

startKoin { modules(appModule) }
val repository: UserRepository by inject()
```

---

## Best Practices

### 1. Используйте Modules для организации

```kotlin
// ХОРОШО: Модули по фичам
val networkModule = DI.Module("network") { ... }
val databaseModule = DI.Module("database") { ... }
val repositoryModule = DI.Module("repository") { ... }

val di = DI {
    importAll(networkModule, databaseModule, repositoryModule)
}

// ПЛОХО: Всё в одном контейнере
val di = DI {
    // 50+ bindings
}
```

### 2. Extend для изоляции

```kotlin
// ХОРОШО: Иерархия контейнеров
val coreDI = DI { ... }
val featureDI = DI { extend(coreDI); ... }

// ПЛОХО: Огромный плоский контейнер
```

### 3. Lazy initialization по умолчанию

```kotlin
// ХОРОШО: DI.lazy — контейнер создаётся при первом обращении
override val di = DI.lazy { ... }

// Используйте eagerSingleton только когда нужна инициализация сразу
```

### 4. Tags вместо множества интерфейсов

```kotlin
// ХОРОШО: Tags
bind<CoroutineDispatcher>(tag = "io") with singleton { Dispatchers.IO }

// ПЛОХО: Отдельные интерфейсы для каждого
interface IoDispatcher
interface MainDispatcher
```

---

## Common Pitfalls

### 1. Missing binding

```kotlin
// ОШИБКА: Зависимость не зарегистрирована
val di = DI {
    bind<UserRepository>() with singleton {
        UserRepositoryImpl(instance())  // UserApi не зарегистрирован!
    }
}
// Runtime exception: No binding found for UserApi

// РЕШЕНИЕ: Зарегистрировать все зависимости
val di = DI {
    bind<UserApi>() with singleton { UserApiImpl() }
    bind<UserRepository>() with singleton { UserRepositoryImpl(instance()) }
}
```

### 2. Circular dependency

```kotlin
// ОШИБКА: A зависит от B, B от A
val di = DI {
    bind<A>() with singleton { A(instance()) }  // B
    bind<B>() with singleton { B(instance()) }  // A
}
// Runtime: StackOverflow или DI exception

// РЕШЕНИЕ: Provider для разрыва цикла
val di = DI {
    bind<A>() with singleton { A(provider()) }  // Provider<B>
    bind<B>() with singleton { B(instance()) }
}
```

### 3. Scope mismatch

```kotlin
// ПРОБЛЕМА: Singleton зависит от scoped
val di = DI {
    bind<Context>() with scoped(AndroidLifecycleScope<Activity>()).singleton { ... }
    bind<Repository>() with singleton {
        RepositoryImpl(instance())  // Context может быть очищен!
    }
}

// РЕШЕНИЕ: Правильная иерархия scopes
```

---

## Источники

### Официальные
- [Kodein Documentation](https://kosi-libs.org/kodein/)
- [Kodein GitHub](https://github.com/kosi-libs/Kodein)
- [Kodein Android Guide](https://kosi-libs.org/kodein/7.22/framework/android.html)

### Статьи
- [Kodein DI (Baeldung)](https://www.baeldung.com/kotlin/kodein-dependency-injection)
- [Kotlin DI Frameworks Comparison](https://www.baeldung.com/kotlin/dependency-injection-libraries)
- [Kodein + ViewModels](https://medium.com/@RedthLight/kodein-viewmodels-4023b7bf4920)

---

## Связанные материалы

- [[dependency-injection-fundamentals]] — Теория DI
- [[android-koin-deep-dive]] — Koin (альтернатива)
- [[android-kotlin-inject-deep-dive]] — kotlin-inject (compile-time)
- [[android-dagger-deep-dive]] — Dagger (compile-time)
