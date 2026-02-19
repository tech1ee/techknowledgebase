---
title: "Clean Architecture на Android: слои, Use Cases и Dependency Rule"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
status: published
cs-foundations: [dependency-inversion, layered-architecture, separation-of-concerns, domain-driven-design, hexagonal-architecture]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/advanced
related:
  - "[[android-architecture-patterns]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-modularization]]"
  - "[[android-repository-pattern]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
  - "[[composition-vs-inheritance]]"
  - "[[adapter-pattern]]"
  - "[[factory-pattern]]"
  - "[[testing-fundamentals]]"
  - "[[mocking-strategies]]"
  - "[[error-handling]]"
  - "[[dependency-injection-fundamentals]]"
  - "[[android-hilt-deep-dive]]"
prerequisites:
  - "[[android-architecture-patterns]]"
  - "[[solid-principles]]"
reading_time: 45
difficulty: 7
study_status: not_started
mastery: 0
---

# Clean Architecture на Android: слои, Use Cases и Dependency Rule

Clean Architecture Дяди Боба **НЕ** была создана для мобильных приложений. Оригинальный пост Роберта Мартина (2012) описывает серверные системы с годами жизни, командами в десятки человек и базами данных, которые меняются раз в пять лет. Android-приложение живёт в другом мире: UI обновляется каждый релиз, база данных -- это Room на телефоне пользователя, а "сервер" -- чужой API, который ты не контролируешь. Тем не менее, адаптированная версия Clean Architecture стала де-факто стандартом на Android. Вопрос не в том, "нужна ли Clean Architecture", а в том, **какие её части** нужны вашему проекту и когда они превращаются в over-engineering.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Архитектурные паттерны Android | MVP, MVVM, MVI -- контекст для Clean Architecture | [[android-architecture-patterns]] |
| SOLID | DIP -- ядро Clean Architecture | [[solid-principles]] |
| Coupling и Cohesion | Метрики, которые Clean Architecture оптимизирует | [[coupling-cohesion]] |
| Repository Pattern | Data Layer строится на Repository | [[android-repository-pattern]] |

---

## Оригинальная Clean Architecture (Robert C. Martin, 2012)

13 августа 2012 года Роберт Мартин опубликовал пост "The Clean Architecture" в блоге Clean Coder. Это не было открытием -- Мартин явно объединил три предшествующих подхода:

| Год | Автор | Концепция | Ключевая идея |
|-----|-------|-----------|---------------|
| 2005 | Alistair Cockburn | Hexagonal Architecture (Ports & Adapters) | Приложение = ядро + порты для внешнего мира |
| 2008 | Jeffrey Palermo | Onion Architecture | Зависимости направлены к центру, как слои луковицы |
| 2012 | Robert C. Martin | Clean Architecture | Dependency Rule + чёткие четыре круга |

Мартин взял общий принцип -- **изолировать бизнес-логику от деталей реализации** -- и дал ему конкретную структуру.

### Четыре концентрических круга

```
┌─────────────────────────────────────────────────────────────────────┐
│                  FRAMEWORKS & DRIVERS                               │
│   Web, UI, DB, Devices, External Interfaces                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │               INTERFACE ADAPTERS                               │  │
│  │   Controllers, Gateways, Presenters                            │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │              USE CASES                                   │  │  │
│  │  │   Application-specific business rules                    │  │  │
│  │  │  ┌───────────────────────────────────────────────────┐  │  │  │
│  │  │  │            ENTITIES                                │  │  │  │
│  │  │  │   Enterprise-wide business rules                   │  │  │  │
│  │  │  │   (самый стабильный код)                           │  │  │  │
│  │  │  └───────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

             Dependency Rule: зависимости → ВНУТРЬ
             Внутренние круги ничего не знают о внешних
```

### Dependency Rule -- единственное правило

> *"Source code dependencies can only point inwards. Nothing in an inner circle can know anything at all about something in an outer circle."*
> -- Robert C. Martin, 2012

Это **единственное** правило, которое делает архитектуру "чистой". Всё остальное -- следствие:

- **Entities** не знают о Use Cases
- **Use Cases** не знают о Controllers или UI
- **Interface Adapters** не знают о конкретных фреймворках
- Данные пересекают границы в виде **простых структур данных** (DTO), а не Entity или Database Row

### Что это даёт

```
Без Dependency Rule:                С Dependency Rule:
┌──────────┐   ┌──────────┐       ┌──────────┐   ┌──────────┐
│   UI     │──▶│  Domain  │       │   UI     │──▶│  Domain  │
│          │   │          │       │          │   │          │
└──────────┘   └────┬─────┘       └──────────┘   └──────────┘
                    │                                  ▲
               ┌────▼─────┐                      ┌────┴─────┐
               │   Data   │                      │   Data   │
               │ (знает   │                      │ (зависит │
               │  о Room) │                      │  от      │
               └──────────┘                      │  Domain  │
                                                 │  через   │
Domain зависит от Data!                          │  интер-  │
Смена DB требует правок                          │  фейс)   │
в бизнес-логике.                                 └──────────┘

                                                 Domain чист!
                                                 Смена DB --
                                                 только Data.
```

Dependency Inversion Principle (DIP) из [[solid-principles]] -- это механизм реализации Dependency Rule. Интерфейс Repository объявляется в Domain, реализация живёт в Data.

---

## Android-адаптация: три слоя

Оригинальные четыре круга на Android сжимаются до **трёх слоёв**. Entities и Use Cases сливаются в Domain Layer, Interface Adapters распределяются между Presentation и Data, а Frameworks & Drivers становятся частью обоих внешних слоёв.

### Архитектурная диаграмма

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ANDROID APPLICATION                           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                PRESENTATION LAYER                            │    │
│  │  :feature:home, :feature:search, :feature:profile            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │  Composables │  │  ViewModel   │  │  UiState /       │  │    │
│  │  │  Activities  │  │  (Hilt)      │  │  UiEvent /       │  │    │
│  │  │  Fragments   │  │              │  │  UiModel         │  │    │
│  │  └──────────────┘  └──────┬───────┘  └──────────────────┘  │    │
│  └───────────────────────────┼─────────────────────────────────┘    │
│                              │ depends on                           │
│  ┌───────────────────────────▼─────────────────────────────────┐    │
│  │                  DOMAIN LAYER                                │    │
│  │  :core:domain  (ЧИСТЫЙ Kotlin -- БЕЗ Android SDK)            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │  Use Cases   │  │  Domain      │  │  Repository      │  │    │
│  │  │  (operator   │  │  Models      │  │  INTERFACES      │  │    │
│  │  │   invoke)    │  │  (User,      │  │  (UserRepo,      │  │    │
│  │  │              │  │   Order)     │  │   OrderRepo)     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  └───────────────────────────▲─────────────────────────────────┘    │
│                              │ implements                           │
│  ┌───────────────────────────┴─────────────────────────────────┐    │
│  │                    DATA LAYER                                │    │
│  │  :core:data, :core:network, :core:database                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │  Repository  │  │  Data        │  │  Mappers         │  │    │
│  │  │  IMPL        │  │  Sources     │  │  (DTO → Domain,  │  │    │
│  │  │              │  │  (Retrofit,  │  │   Entity →       │  │    │
│  │  │              │  │   Room,      │  │   Domain)        │  │    │
│  │  │              │  │   DataStore) │  │                  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ПРАВИЛО: Зависимости направлены ВНУТРЬ (к Domain Layer)             │
│  Domain не знает ни о Retrofit, ни о Room, ни о Compose              │
└──────────────────────────────────────────────────────────────────────┘
```

### Что содержит каждый слой

| Слой | Содержимое | Gradle plugin | Знает о |
|------|-----------|---------------|---------|
| **Presentation** | Compose/XML UI, ViewModel, UiState, Navigation | `com.android.library` | Domain |
| **Domain** | Use Cases, Domain Models, Repository interfaces | `kotlin("jvm")` -- **без Android** | Ничего |
| **Data** | Repository impl, DataSource, DTO, Entity, Mapper | `com.android.library` | Domain |

Ключевое: **Domain Layer -- чистый Kotlin модуль**. Никаких `android.` импортов. Это даёт три преимущества:

1. **Тестируемость** -- JUnit тесты без Robolectric, запуск за секунды
2. **KMP-ready** -- модуль можно переиспользовать в iOS через Kotlin Multiplatform
3. **Скорость компиляции** -- `kotlin("jvm")` компилируется быстрее, чем `com.android.library`

---

## Domain Layer: самый спорный слой

### Google's позиция: "optional"

Google в официальной документации Guide to App Architecture явно говорит:

> *"The domain layer is an **optional** layer that sits between the UI layer and the data layer."*

Это не формальность. Google подразумевает: **не добавляйте Domain Layer, если вам нечего в него положить**. В "Now in Android" (NiA) -- официальном reference-приложении Google -- Domain Layer используется **выборочно**: UseCase есть для комбинирования данных из нескольких репозиториев, но для простых операций (follow/unfollow topic) UI вызывает Repository напрямую.

### Когда Domain Layer оправдан

```
Domain Layer НУЖЕН, когда:                Domain Layer НЕ нужен, когда:

✓ UseCase комбинирует 2+ репозитория      ✗ UseCase просто вызывает repo.getAll()
✓ Есть бизнес-валидация перед действием   ✗ Простой CRUD без логики
✓ Логика переиспользуется в 3+ ViewModel ✗ Логика нужна только одному экрану
✓ Нужна KMP-совместимость                ✗ Проект только Android
✓ Команда 5+ человек, нужны границы      ✗ 1-2 разработчика
✓ Сложная трансформация данных            ✗ Данные приходят "готовые" из API
```

### Pure Kotlin модуль: зачем

```kotlin
// build.gradle.kts для :core:domain
plugins {
    kotlin("jvm") // НЕ com.android.library!
}

dependencies {
    // Только чистый Kotlin + корутины
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")

    // НЕТ зависимостей на:
    // - androidx.*
    // - com.google.android.*
    // - Room, Retrofit, Hilt

    // Для DI: только javax.inject (JSR-330)
    implementation("javax.inject:javax.inject:1")

    // Тестирование
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

Модуль `:core:domain` не имеет `android {}` блока. Это **физическая** гарантия того, что Domain Layer не может зависеть от Android SDK. Если разработчик попытается импортировать `android.content.Context` -- код не скомпилируется.

---

## Use Case паттерны: от антипаттерна до идиоматики

Use Case (или Interactor) -- класс с **единственной ответственностью**, который инкапсулирует одну операцию бизнес-логики. Google рекомендует именование:

```
[глагол в настоящем времени] + [существительное (опционально)] + UseCase

Примеры:
  FormatDateUseCase
  GetLatestNewsWithAuthorsUseCase
  LogOutUserUseCase
  ValidateOrderUseCase
```

Ниже -- шесть паттернов: от антипаттерна, который нужно распознавать, до production-ready решений.

### a) Proxy UseCase -- антипаттерн

```kotlin
// ❌ АНТИПАТТЕРН: UseCase-прокси
// Просто делегирует вызов в Repository. Нулевая ценность.
class GetUsersUseCase @Inject constructor(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(): List<User> {
        return userRepository.getUsers() // ← и всё?
    }
}

// В ViewModel:
class UsersViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch {
            val users = getUsersUseCase() // можно было вызвать repo напрямую
        }
    }
}
```

**Почему это плохо:**
- UseCase не добавляет никакой логики -- просто forwarding
- Дополнительный класс, файл, тест -- ради нуля пользы
- Увеличивает cognitive load: разработчик открывает UseCase, чтобы понять, что он ничего не делает
- Google в NiA **не создаёт** UseCase для таких случаев -- ViewModel вызывает Repository напрямую

**Красный флаг:** если UseCase содержит **одну строку** -- `return repository.method()` -- это прокси. Удалите его.

### b) Orchestrating UseCase -- комбинирование репозиториев

```kotlin
// ✅ ХОРОШИЙ UseCase: комбинирует данные из двух источников
class GetUserWithPostsUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val postsRepository: PostsRepository
) {
    suspend operator fun invoke(userId: Long): Result<UserWithPosts> {
        return runCatching {
            // Параллельная загрузка из двух репозиториев
            coroutineScope {
                val userDeferred = async { userRepository.getUser(userId) }
                val postsDeferred = async { postsRepository.getPostsByUser(userId) }

                val user = userDeferred.await()
                val posts = postsDeferred.await()

                UserWithPosts(
                    user = user,
                    posts = posts.sortedByDescending { it.createdAt },
                    totalLikes = posts.sumOf { it.likes }
                )
            }
        }
    }
}

// Domain model, которой нет в отдельном репозитории
data class UserWithPosts(
    val user: User,
    val posts: List<Post>,
    val totalLikes: Int
)
```

**Почему это хороший UseCase:**
- Комбинирует данные из `UserRepository` и `PostsRepository`
- Добавляет логику: сортировка, подсчёт лайков
- Создаёт новую Domain Model (`UserWithPosts`), которой нет в отдельном репозитории
- Параллельная загрузка -- оптимизация, которую ViewModel не должен знать

### c) Streaming UseCase -- возвращает Flow

```kotlin
// ✅ Реактивный UseCase: наблюдение за изменениями в реальном времени
class ObserveUserUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val settingsRepository: SettingsRepository
) {
    operator fun invoke(userId: Long): Flow<UserProfile> {
        return combine(
            userRepository.observeUser(userId),
            settingsRepository.observeSettings()
        ) { user, settings ->
            UserProfile(
                user = user,
                displayName = if (settings.showFullName) {
                    "${user.firstName} ${user.lastName}"
                } else {
                    user.firstName
                },
                avatarUrl = user.avatarUrl ?: settings.defaultAvatarUrl
            )
        }
    }
}
```

**Обратите внимание:** `invoke` здесь **не** suspend -- он возвращает `Flow`, который сам по себе холодный. Suspend нужен только для one-shot операций.

### d) Parameterized UseCase с sealed Result

```kotlin
// ✅ UseCase с типизированными ошибками
class SearchProductsUseCase @Inject constructor(
    private val productRepository: ProductRepository,
    private val searchHistoryRepository: SearchHistoryRepository
) {
    suspend operator fun invoke(params: Params): SearchResult {
        // Валидация параметров
        if (params.query.length < 2) {
            return SearchResult.Error(SearchError.QueryTooShort)
        }
        if (params.maxPrice < params.minPrice) {
            return SearchResult.Error(SearchError.InvalidPriceRange)
        }

        return try {
            val products = productRepository.search(
                query = params.query,
                minPrice = params.minPrice,
                maxPrice = params.maxPrice,
                category = params.category
            )
            // Сохраняем в историю только успешные поиски
            searchHistoryRepository.save(params.query)

            if (products.isEmpty()) {
                SearchResult.Empty(suggestion = "Попробуйте: ${params.query.take(3)}")
            } else {
                SearchResult.Success(products)
            }
        } catch (e: Exception) {
            SearchResult.Error(SearchError.NetworkError(e.message))
        }
    }

    data class Params(
        val query: String,
        val minPrice: Double = 0.0,
        val maxPrice: Double = Double.MAX_VALUE,
        val category: String? = null
    )
}

// Sealed-иерархия для результатов
sealed interface SearchResult {
    data class Success(val products: List<Product>) : SearchResult
    data class Empty(val suggestion: String) : SearchResult
    data class Error(val error: SearchError) : SearchResult
}

sealed interface SearchError {
    data object QueryTooShort : SearchError
    data object InvalidPriceRange : SearchError
    data class NetworkError(val message: String?) : SearchError
}
```

**Преимущества sealed Result:**
- Компилятор заставляет обработать **все** ветки в `when`
- Нет неожиданных исключений -- ошибки явные (см. [[error-handling]])
- `Params` data class вместо россыпи параметров -- легче тестировать и расширять

### e) UseCase с бизнес-валидацией

```kotlin
// ✅ UseCase с бизнес-правилами: создание заказа
class CreateOrderUseCase @Inject constructor(
    private val orderRepository: OrderRepository,
    private val inventoryRepository: InventoryRepository,
    private val userRepository: UserRepository,
    private val pricingService: PricingService
) {
    suspend operator fun invoke(request: OrderRequest): OrderResult {
        // 1. Проверяем пользователя
        val user = userRepository.getUser(request.userId)
            ?: return OrderResult.Failure(OrderError.UserNotFound)

        if (user.isBlocked) {
            return OrderResult.Failure(OrderError.UserBlocked)
        }

        // 2. Проверяем наличие товаров
        val unavailable = mutableListOf<String>()
        for (item in request.items) {
            val stock = inventoryRepository.getStock(item.productId)
            if (stock < item.quantity) {
                unavailable += item.productId
            }
        }
        if (unavailable.isNotEmpty()) {
            return OrderResult.Failure(OrderError.OutOfStock(unavailable))
        }

        // 3. Рассчитываем цену с учётом скидок
        val totalPrice = pricingService.calculate(
            items = request.items,
            promoCode = request.promoCode,
            userTier = user.loyaltyTier
        )

        // 4. Проверяем лимиты
        if (totalPrice > MAX_ORDER_AMOUNT) {
            return OrderResult.Failure(
                OrderError.ExceedsLimit(max = MAX_ORDER_AMOUNT, actual = totalPrice)
            )
        }

        // 5. Создаём заказ
        return try {
            val order = orderRepository.create(
                Order(
                    userId = user.id,
                    items = request.items,
                    totalPrice = totalPrice,
                    status = OrderStatus.PENDING
                )
            )
            // 6. Резервируем товары
            inventoryRepository.reserve(order.id, request.items)
            OrderResult.Success(order)
        } catch (e: Exception) {
            OrderResult.Failure(OrderError.Unknown(e.message))
        }
    }

    companion object {
        private const val MAX_ORDER_AMOUNT = 1_000_000.0
    }
}

sealed interface OrderResult {
    data class Success(val order: Order) : OrderResult
    data class Failure(val error: OrderError) : OrderResult
}

sealed interface OrderError {
    data object UserNotFound : OrderError
    data object UserBlocked : OrderError
    data class OutOfStock(val productIds: List<String>) : OrderError
    data class ExceedsLimit(val max: Double, val actual: Double) : OrderError
    data class Unknown(val message: String?) : OrderError
}
```

**Это идеальный кандидат для UseCase:** 6 шагов бизнес-логики, 4 репозитория, множество условий. Без UseCase вся эта логика оказалась бы в ViewModel -- и тестировать её без Android-фреймворка было бы невозможно.

### f) Operator invoke -- идиоматический Kotlin

Зачем `operator fun invoke()` вместо `fun execute()`?

```kotlin
// С invoke:
val users = getUsersUseCase()           // читается как вызов функции
val posts = getPostsUseCase(userId)     // естественный синтаксис

// Без invoke:
val users = getUsersUseCase.execute()   // Java-стиль, verbose
val posts = getPostsUseCase.execute(userId)
```

`operator fun invoke` делает объект **вызываемым как функцию**. Это идиоматический Kotlin: UseCase -- это по сути функция с зависимостями, и `invoke` подчёркивает, что у него **одна операция**. Если вам нужно два метода -- это уже не UseCase, а сервис.

Google использует `operator fun invoke` во всех UseCase в NiA. Это стандарт индустрии.

> [!tip] UseCase lifecycle
> UseCase не имеет собственного lifecycle. Google: *"Use cases don't have their own lifecycle. Instead, they're scoped to the class that uses them."* Каждый раз, когда UseCase передаётся как зависимость, создаётся новый экземпляр. UseCase не должен хранить mutable state.

---

## Domain модели vs DTOs vs UI models

Три модели для одной сущности -- частая боль Clean Architecture. Когда это оправдано, а когда -- over-engineering?

### Три модели: DTO, Domain, UiModel

```kotlin
// ── DATA LAYER ──────────────────────────────────

// DTO: то, что приходит из API
@Serializable
data class UserDto(
    val id: Long,
    val first_name: String,     // snake_case от API
    val last_name: String,
    val email: String,
    val avatar_url: String?,
    val created_at: String,     // ISO 8601 строка
    val role: String            // "admin", "user", "moderator"
)

// Entity: то, что хранится в Room
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Long,
    val firstName: String,
    val lastName: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Long,        // timestamp
    val role: String,
    val cachedAt: Long          // метаданные кэширования
)

// Mappers: extension functions
fun UserDto.toDomain() = User(
    id = id,
    firstName = first_name,
    lastName = last_name,
    email = email,
    avatarUrl = avatar_url,
    createdAt = Instant.parse(created_at),
    role = UserRole.fromString(role)
)

fun UserEntity.toDomain() = User(
    id = id,
    firstName = firstName,
    lastName = lastName,
    email = email,
    avatarUrl = avatarUrl,
    createdAt = Instant.fromEpochMilliseconds(createdAt),
    role = UserRole.fromString(role)
)

fun User.toEntity(cachedAt: Long = System.currentTimeMillis()) = UserEntity(
    id = id, firstName = firstName, lastName = lastName,
    email = email, avatarUrl = avatarUrl,
    createdAt = createdAt.toEpochMilliseconds(),
    role = role.name.lowercase(),
    cachedAt = cachedAt
)

// ── DOMAIN LAYER ────────────────────────────────

// Domain Model: бизнес-сущность
data class User(
    val id: Long,
    val firstName: String,
    val lastName: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Instant,     // типизированная дата
    val role: UserRole          // enum вместо строки
)

enum class UserRole {
    ADMIN, USER, MODERATOR;

    companion object {
        fun fromString(value: String): UserRole =
            entries.find { it.name.equals(value, ignoreCase = true) } ?: USER
    }
}

// ── PRESENTATION LAYER ──────────────────────────

// UI Model: то, что видит экран
data class UserUiModel(
    val id: Long,
    val displayName: String,        // "Иван Петров" -- готовый формат
    val email: String,
    val avatarUrl: String,          // с fallback, не nullable
    val memberSince: String,        // "Участник с января 2024"
    val roleBadge: RoleBadge        // цвет и текст для UI
)

fun User.toUiModel() = UserUiModel(
    id = id,
    displayName = "$firstName $lastName",
    email = email,
    avatarUrl = avatarUrl ?: "https://example.com/default-avatar.png",
    memberSince = "Участник с ${createdAt.formatAsMonthYear()}",
    roleBadge = when (role) {
        UserRole.ADMIN -> RoleBadge("Админ", Color.Red)
        UserRole.MODERATOR -> RoleBadge("Модератор", Color.Blue)
        UserRole.USER -> RoleBadge("Пользователь", Color.Gray)
    }
)
```

### Когда сколько моделей

```
┌──────────────────────────────────────────────────────────────────┐
│                  СКОЛЬКО МОДЕЛЕЙ НУЖНО?                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Три модели (DTO + Domain + UiModel):                           │
│  • API и UI имеют разные форматы (snake_case vs camelCase)      │
│  • Нужны вычисляемые поля для UI (displayName, memberSince)     │
│  • Domain модель содержит типизированные поля (Instant, enum)   │
│  • Реальные проекты: банки, маркетплейсы, social apps           │
│                                                                  │
│  Две модели (DTO + Domain, Domain = UiModel):                   │
│  • UI показывает данные "как есть", без трансформации            │
│  • Нет сложной бизнес-логики                                    │
│  • Domain Model можно напрямую показать в Compose                │
│  • Реальные проекты: утилиты, todo-приложения                   │
│                                                                  │
│  Одна модель (DTO = Domain = UiModel):                          │
│  • Простой CRUD, поля совпадают                                  │
│  • Нет кэширования в Room                                       │
│  • Прототип или MVP                                              │
│  • ⚠️ Нарушает Separation of Concerns                           │
│                                                                  │
│  ПРАВИЛО: начинай с двух моделей (DTO + Domain).                │
│  Добавляй UiModel, когда трансформация появится.                │
│  НЕ создавай три модели "на будущее".                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Layer: реализация

> Полные детали реализации Data Layer -- стратегии кэширования, offline-first, синхронизация -- описаны в [[android-repository-pattern]]. Здесь -- только то, что специфично для Clean Architecture.

### Repository Implementation

Repository Interface объявляется в Domain Layer. Implementation -- в Data Layer. Это DIP в действии:

```kotlin
// ── :core:domain (kotlin-jvm модуль) ──
interface ProductRepository {
    suspend fun getProducts(): List<Product>
    fun observeProducts(): Flow<List<Product>>
    suspend fun getProduct(id: String): Product?
    suspend fun search(query: String, minPrice: Double, maxPrice: Double,
                       category: String?): List<Product>
}

// ── :core:data (android library модуль) ──
class ProductRepositoryImpl @Inject constructor(
    private val api: ProductApiService,
    private val dao: ProductDao,
    private val mapper: ProductMapper
) : ProductRepository {

    override suspend fun getProducts(): List<Product> {
        return try {
            val dtos = api.getProducts()
            val entities = dtos.map { mapper.dtoToEntity(it) }
            dao.insertAll(entities)
            entities.map { mapper.entityToDomain(it) }
        } catch (e: Exception) {
            dao.getAll().map { mapper.entityToDomain(it) }
        }
    }

    override fun observeProducts(): Flow<List<Product>> {
        return dao.observeAll().map { entities ->
            entities.map { mapper.entityToDomain(it) }
        }
    }

    // ... остальные методы
}
```

### Mapper стратегии

Три подхода к маппингу, от простого к формальному:

**1. Extension functions (рекомендуется для большинства проектов):**

```kotlin
// Просто, читаемо, нет лишних классов
fun ProductDto.toDomain() = Product(id = id, name = name, price = price)
fun ProductEntity.toDomain() = Product(id = id, name = name, price = price)
```

**2. Dedicated Mapper class (для сложных трансформаций):**

```kotlin
class ProductMapper @Inject constructor(
    private val currencyFormatter: CurrencyFormatter
) {
    fun dtoToDomain(dto: ProductDto) = Product(
        id = dto.id,
        name = dto.name,
        formattedPrice = currencyFormatter.format(dto.price, dto.currency)
    )
}
```

**3. Inline mapping (для одноразовых простых маппингов):**

```kotlin
// Прямо в месте использования, без отдельной функции
val products = dtos.map { Product(id = it.id, name = it.name, price = it.price) }
```

Подробнее о координации нескольких DataSource (Room + Retrofit + DataStore) см. [[android-repository-pattern]].

---

## Dependency Rule: как соблюдать

### Gradle module boundaries

Самый надёжный способ соблюдать Dependency Rule -- **Gradle модули**. Если `:core:domain` не имеет зависимости на `:core:data` в `build.gradle.kts`, то ни один класс из Domain не сможет импортировать класс из Data. Компилятор гарантирует.

```
settings.gradle.kts:
  include(":app")
  include(":core:domain")      // kotlin-jvm, БЕЗ Android
  include(":core:data")        // android-library
  include(":core:network")     // android-library
  include(":core:database")    // android-library
  include(":core:common")      // kotlin-jvm, утилиты
  include(":feature:home")     // android-library
  include(":feature:search")   // android-library
  include(":feature:profile")  // android-library

Граф зависимостей:
  :app → :feature:* → :core:domain
  :core:data → :core:domain
  :core:data → :core:network
  :core:data → :core:database
  :core:domain → :core:common (опционально)

  :core:domain НЕ зависит от :core:data  ← Dependency Rule!
```

### Interface-based dependency inversion

Интерфейс объявляется в модуле, от которого зависят все. Реализация -- в модуле, о котором знает только DI:

```
┌──────────────┐    depends on    ┌──────────────┐
│ :feature:home│───────────────▶│ :core:domain │
│              │                  │              │
│ HomeViewModel│                  │ UserRepo     │ ← interface
│ uses UseCase │                  │ (interface)  │
└──────────────┘                  └──────────────┘
                                        ▲
                                        │ implements
                                  ┌──────────────┐
                                  │ :core:data   │
                                  │              │
                                  │ UserRepoImpl │ ← class
                                  └──────────────┘
                                        │
                            Hilt связывает interface → impl
```

### Hilt DI wiring

```kotlin
// ── :core:data ──

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    // @Binds -- для связывания interface → implementation
    // Эффективнее @Provides: не создаёт wrapper-метод
    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    @Singleton
    abstract fun bindProductRepository(
        impl: ProductRepositoryImpl
    ): ProductRepository

    @Binds
    @Singleton
    abstract fun bindOrderRepository(
        impl: OrderRepositoryImpl
    ): OrderRepository
}

@Module
@InstallIn(SingletonComponent::class)
object DataSourceModule {

    // @Provides -- для объектов, которые нельзя inject через конструктор
    @Provides
    @Singleton
    fun provideProductApi(retrofit: Retrofit): ProductApiService {
        return retrofit.create(ProductApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideProductDao(database: AppDatabase): ProductDao {
        return database.productDao()
    }
}
```

Подробнее о Hilt-конфигурации: [[android-hilt-deep-dive]]. О теории DI: [[dependency-injection-fundamentals]].

### Architecture tests: Konsist

Gradle модули защищают от нарушений на уровне компиляции. Но если архитектура определена **пакетами** внутри одного модуля (например, в маленьком проекте), нужны runtime-проверки. Konsist -- это Kotlin-native библиотека для архитектурных тестов:

```kotlin
// ── src/test/kotlin/ArchitectureTest.kt ──

class ArchitectureTest {

    @Test
    fun `domain layer does not depend on data or presentation`() {
        Konsist
            .scopeFromProject()
            .assertArchitecture {
                val domain = Layer("Domain", "com.myapp.domain..")
                val data = Layer("Data", "com.myapp.data..")
                val presentation = Layer("Presentation", "com.myapp.presentation..")

                domain.dependsOnNothing()
                presentation.dependsOn(domain)
                data.dependsOn(domain)
            }
    }

    @Test
    fun `use cases have single public invoke method`() {
        Konsist
            .scopeFromProject()
            .classes()
            .withNameEndingWith("UseCase")
            .assert { useCase ->
                val publicMethods = useCase.functions()
                    .filter { it.hasPublicOrDefaultModifier }
                publicMethods.size == 1 && publicMethods.first().name == "invoke"
            }
    }
}
```

Konsist пишет проверки в форме обычных JUnit-тестов. Упал тест -- нарушена архитектура. Это дешевле, чем code review.

---

## Вариации в сообществе

Clean Architecture на Android -- не монолит. Разные команды адаптируют её по-разному.

### Google "Now in Android" (NiA)

- **Domain Layer:** есть, но **выборочный**. UseCase создаётся только когда нужно комбинировать данные из нескольких репозиториев
- **Пример:** `GetUserNewsResourcesUseCase` объединяет `NewsRepository` + `UserDataRepository` в один поток `UserNewsResource`
- **Простые операции:** ViewModel вызывает Repository напрямую (toggle bookmark, follow topic)
- **Философия:** pragmatic, не dogmatic

### Fernando Cejas (2014)

- **Пионер** Clean Architecture на Android
- **Strict 3-layer:** Domain Layer обязателен, все операции через UseCase
- **RxJava:** абстрактный базовый `UseCase<T>` с `Observable`
- **Влияние:** определил стиль целого поколения Android-разработчиков
- **Проблема:** многие скопировали структуру, не поняв принципы -- породили тысячи proxy UseCase

### Square/Block

- **Molecule:** UI как функция состояния
- **Упрощённые слои:** меньше церемонии, больше прагматизма
- **Нет формального Domain Layer** -- бизнес-логика в Presenter/Workflow

### "Clean MVVM" -- самый распространённый вариант

Большинство Android-проектов используют **гибрид:**

```
• MVVM (ViewModel + StateFlow + Compose)
• Repository Pattern (Data Layer)
• UseCase (ТОЛЬКО для сложной логики)
• Package-based separation (НЕ отдельные Gradle модули)
```

Это не "каноническая" Clean Architecture -- но это **рабочее решение** для 80% проектов. Отдельные Gradle модули добавляют, когда проект перерастает 50-100K строк.

---

## Когда Clean Architecture вредит

### Over-engineering метрики

Признаки того, что Clean Architecture применена чрезмерно:

| Признак | Пример | Решение |
|---------|--------|---------|
| UseCase-прокси | `GetUsersUseCase { return repo.getUsers() }` | Удалить UseCase, вызывать repo из ViewModel |
| 3 модели для простой сущности | DTO, Domain, UiModel с одинаковыми полями | Объединить Domain и UiModel |
| Пустой Domain модуль | 2 UseCase, оба -- прокси | Убрать модуль, перенести интерфейсы в Data |
| Mapper без трансформации | `fun toDomain() = Domain(id=id, name=name)` | Использовать одну модель |
| Абстракция ради абстракции | `interface DataSource` с одной реализацией | Удалить интерфейс |

### 3 модели для одной сущности: когда лишнее

```kotlin
// ❌ Over-engineering: три модели с ОДИНАКОВЫМИ полями
data class UserDto(val id: Long, val name: String, val email: String)
data class User(val id: Long, val name: String, val email: String)     // = DTO
data class UserUiModel(val id: Long, val name: String, val email: String) // = Domain

// ✅ Достаточно: одна модель + DTO
@Serializable
data class UserDto(val id: Long, val name: String, val email: String)

data class User(val id: Long, val name: String, val email: String)
// ViewModel использует User напрямую -- трансформации нет
```

### Decision framework: нужен ли Domain Layer?

```
                        ┌──────────────────────┐
                        │ Есть ли бизнес-логика │
                        │ помимо CRUD?          │
                        └───────┬──────────────┘
                           ┌────┴────┐
                           │         │
                          Да        Нет ──────────▶ НЕ нужен Domain Layer.
                           │                        ViewModel → Repository.
                           ▼
                 ┌───────────────────┐
                 │ Переиспользуется  │
                 │ в 2+ ViewModels?  │
                 └───────┬───────────┘
                    ┌────┴────┐
                    │         │
                   Да        Нет
                    │         │
                    ▼         ▼
          ┌─────────────┐  ┌────────────────────────────┐
          │ UseCase в    │  │ Логика в одном ViewModel?  │
          │ Domain Layer │  │ Выносить UseCase рано.     │
          │ (✅ нужен)   │  │ Вынесете, когда повторится.│
          └─────────────┘  └────────────────────────────┘
                    │
                    ▼
          ┌──────────────────────┐
          │ Команда 5+ человек   │
          │ или проект > 50K LOC?│
          └───────┬──────────────┘
             ┌────┴────┐
             │         │
            Да        Нет
             │         │
             ▼         ▼
    ┌────────────┐  ┌────────────────────┐
    │ Отдельный  │  │ Package-based      │
    │ Gradle     │  │ separation         │
    │ модуль     │  │ (пакеты внутри     │
    │ :core:     │  │  одного модуля)    │
    │  domain    │  │                    │
    └────────────┘  └────────────────────┘
```

### Cost of abstraction

| Фактор | Полная Clean Architecture | Упрощённая (без Domain) |
|--------|--------------------------|-------------------------|
| Классов на фичу | ~15-20 | ~8-10 |
| Время onboarding | 2-3 недели | 1 неделя |
| Compile time (cold) | +15-25% (больше модулей) | baseline |
| Cognitive load | Высокий (3 модели, маппинг) | Средний |
| Тестируемость | Отличная | Хорошая |
| Рефакторинг | Безопасный (границы) | Рискованнее |

**Правило:** добавляйте сложность, когда она окупается. Начните с упрощённой архитектуры и усложняйте по мере роста.

---

## Тестирование Clean Architecture

Главное преимущество Clean Architecture -- **каждый слой тестируется изолированно**. Domain Layer не зависит от Android, значит тесты -- чистый JUnit, без Robolectric, без эмулятора.

### Unit test: UseCase с fake Repository

```kotlin
// ── Fake Repository (НЕ mock -- fake!) ──
class FakeUserRepository : UserRepository {

    private val users = mutableListOf<User>()
    var shouldThrow = false

    fun addUsers(vararg newUsers: User) {
        users.addAll(newUsers)
    }

    override suspend fun getUsers(): List<User> {
        if (shouldThrow) throw IOException("Network error")
        return users.toList()
    }

    override suspend fun getUser(id: Long): User? {
        if (shouldThrow) throw IOException("Network error")
        return users.find { it.id == id }
    }
}

// ── Unit Test ──
class GetUserWithPostsUseCaseTest {

    private val fakeUserRepo = FakeUserRepository()
    private val fakePostsRepo = FakePostsRepository()
    private val useCase = GetUserWithPostsUseCase(fakeUserRepo, fakePostsRepo)

    @Test
    fun `returns user with sorted posts and total likes`() = runTest {
        // Given
        fakeUserRepo.addUsers(User(id = 1, firstName = "Иван", lastName = "Петров",
            email = "ivan@test.com", avatarUrl = null,
            createdAt = Instant.parse("2024-01-01T00:00:00Z"), role = UserRole.USER))
        fakePostsRepo.addPosts(
            Post(id = 1, userId = 1, title = "First", likes = 10,
                 createdAt = Instant.parse("2024-01-01T00:00:00Z")),
            Post(id = 2, userId = 1, title = "Second", likes = 25,
                 createdAt = Instant.parse("2024-02-01T00:00:00Z"))
        )

        // When
        val result = useCase(userId = 1)

        // Then
        assertTrue(result.isSuccess)
        val data = result.getOrThrow()
        assertEquals("Иван", data.user.firstName)
        assertEquals(2, data.posts.size)
        assertEquals("Second", data.posts.first().title) // отсортированы по дате DESC
        assertEquals(35, data.totalLikes)
    }

    @Test
    fun `returns failure on network error`() = runTest {
        fakeUserRepo.shouldThrow = true

        val result = useCase(userId = 1)

        assertTrue(result.isFailure)
    }
}
```

**Почему fake, а не mock:** fake содержит реальную (упрощённую) логику. Mock проверяет вызовы методов, а fake -- поведение. Подробнее: [[mocking-strategies]].

### Integration: Repository с in-memory data sources

```kotlin
@Test
fun `repository returns cached data on network failure`() = runTest {
    // Given: данные есть в Room
    val dao = FakeProductDao()
    dao.insertAll(listOf(
        ProductEntity(id = "1", name = "Product", price = 100.0, cachedAt = now())
    ))
    val api = FakeProductApi(shouldFail = true) // API недоступен
    val repo = ProductRepositoryImpl(api, dao, ProductMapper())

    // When
    val products = repo.getProducts()

    // Then
    assertEquals(1, products.size)
    assertEquals("Product", products.first().name)
}
```

### Architecture tests: Konsist rules

```kotlin
class CleanArchitectureRulesTest {

    @Test
    fun `UseCases are in domain package`() {
        Konsist
            .scopeFromProject()
            .classes()
            .withNameEndingWith("UseCase")
            .assert { it.resideInPackage("com.myapp.domain..") }
    }

    @Test
    fun `Repository interfaces are in domain, implementations in data`() {
        Konsist.scopeFromProject().interfaces()
            .withNameEndingWith("Repository")
            .assert { it.resideInPackage("com.myapp.domain..") }

        Konsist.scopeFromProject().classes()
            .withNameEndingWith("RepositoryImpl")
            .assert { it.resideInPackage("com.myapp.data..") }
    }

    @Test
    fun `domain layer has no Android imports`() {
        Konsist
            .scopeFromModule(":core:domain")
            .files
            .assert { file ->
                file.imports.none { it.name.startsWith("android.") }
                    && file.imports.none { it.name.startsWith("androidx.") }
            }
    }
}
```

Каждый тест -- один assert, одно правило. Тесты запускаются при каждом PR. Нарушил архитектуру -- тест падает раньше, чем code review.

---

## Мифы и заблуждения

**Миф 1: "UseCase = бизнес-логика"**

**Реальность:** UseCase = **оркестрация**. Бизнес-правила могут жить в Domain Model (Rich Domain Model) или в отдельных Validator/Policy классах. UseCase координирует вызовы: получить данные из репозитория A, проверить правилом B, сохранить через репозиторий C. UseCase, который сам содержит всю логику -- это God UseCase, и он так же плох, как God Activity.

**Миф 2: "Domain Layer обязателен"**

**Реальность:** Google явно говорит "optional". В NiA для простых операций ViewModel вызывает Repository напрямую. Domain Layer оправдан только когда есть бизнес-логика, требующая оркестрации или переиспользования.

**Миф 3: "Mapper для каждого DTO обязателен"**

**Реальность:** если DTO и Domain Model имеют одинаковые поля -- mapper добавляет только boilerplate. Используй DTO как Domain Model (с `typealias` если хочется семантики) до тех пор, пока поля не начнут расходиться. Mapper нужен, когда форматы реально отличаются (snake_case API vs camelCase Kotlin, строка даты vs `Instant`).

**Миф 4: "Clean Architecture = 3 Gradle модуля"**

**Реальность:** Clean Architecture -- это **принцип** (Dependency Rule), а не конкретная структура модулей. Можно соблюдать Dependency Rule через пакеты внутри одного модуля + Konsist тесты. Отдельные модули -- надёжнее (компилятор enforce), но не обязательны для маленьких проектов.

**Миф 5: "Repository всегда возвращает Domain Model"**

**Реальность:** зависит от контекста. Если Domain Model = DTO (поля одинаковые), возвращайте DTO. Маппинг ради маппинга -- не архитектура, а cargo cult. Маппинг нужен, когда модели реально отличаются.

**Миф 6: "Android Clean Architecture = Uncle Bob's Clean Architecture"**

**Реальность:** Android-вариант -- **упрощение**. Оригинал имеет 4 круга (Entities, Use Cases, Interface Adapters, Frameworks). Android использует 3 слоя, Entities сливаются с Use Cases в Domain Layer. Оригинал описывает enterprise-системы с базами данных и web-серверами. Android -- мобильное приложение с Room и Retrofit. Принцип (Dependency Rule) тот же, реализация -- другая.

**Миф 7: "Чем больше слоёв, тем лучше архитектура"**

**Реальность:** каждый слой -- это cost. Дополнительный класс, файл, тест, маппинг. Хорошая архитектура -- не та, у которой больше слоёв, а та, где каждый слой **оправдан**. Один слой, который решает проблему -- лучше трёх слоёв, которые её создают.

---

## CS-фундамент

| CS-концепция | Роль в Clean Architecture | Где изучить |
|-------------|--------------------------|-------------|
| Dependency Inversion Principle | **THE core principle.** Repository interface в Domain, impl в Data | [[solid-principles]] |
| Separation of Concerns | Каждый слой -- своя ответственность | [[coupling-cohesion]] |
| Layered Architecture | Presentation → Domain → Data | [[android-architecture-patterns]] |
| Hexagonal Architecture | Предшественник Clean Architecture (Ports & Adapters) | [[android-architecture-patterns]] |
| Information Hiding | Domain не знает о Retrofit, Room, Compose | [[coupling-cohesion]] |
| Adapter Pattern | Mapper = адаптер между слоями; Repository = адаптер к данным | [[adapter-pattern]] |
| Factory Pattern | Создание Domain объектов из DTO | [[factory-pattern]] |
| Interface Segregation | Маленькие Repository interfaces вместо God Repository | [[solid-principles]] |

---

## Связь с другими темами

### [[solid-principles]] -- DIP как фундамент

Dependency Inversion Principle -- **единственный** принцип из SOLID, без которого Clean Architecture невозможна. DIP говорит: "Зависеть от абстракций, а не от реализаций." В Clean Architecture это означает: `UserRepository` (interface) живёт в `:core:domain`, а `UserRepositoryImpl` (class) -- в `:core:data`. Domain не знает о Room или Retrofit. SRP тоже играет роль: каждый слой имеет одну причину для изменений (UI меняется из-за дизайна, Data -- из-за API, Domain -- из-за бизнес-правил). А ISP напоминает: не создавайте God Repository с 20 методами -- разделите на `UserReadRepository` и `UserWriteRepository`.

### [[coupling-cohesion]] -- Clean Architecture как оптимизатор

Clean Architecture -- это системное применение принципа Low Coupling + High Cohesion. Domain Layer имеет **максимальную cohesion**: все классы связаны с бизнес-логикой. Coupling между слоями -- **минимальный**: только через интерфейсы. Смена Retrofit на Ktor не затрагивает Domain. Смена Compose на XML не затрагивает Data. Каждый слой можно менять независимо.

### [[composition-vs-inheritance]] -- композиция UseCase

В Clean Architecture наследование практически отсутствует в Domain Layer. UseCase -- это финальные классы (Kotlin `class` без `open`), которые получают зависимости через конструктор (композиция). Абстрактный `BaseUseCase<P, R>` -- частый антипаттерн из ранних реализаций (Fernando Cejas 2014). Современный подход: каждый UseCase -- отдельный класс с `operator fun invoke`, без иерархии наследования. Kotlin `final by default` поддерживает это на уровне языка.

### [[adapter-pattern]] -- Mappers и Repository как адаптеры

Mapper -- это классический Adapter: преобразует интерфейс одного слоя в интерфейс другого. `UserDto.toDomain()` адаптирует формат API (snake_case, строки) в формат Domain (camelCase, типизированные поля). Repository -- тоже адаптер: скрывает за единым интерфейсом множество DataSource (API, Room, DataStore). ViewModel не знает, откуда данные -- из сети или кэша.

### [[error-handling]] -- Result и sealed errors

В Clean Architecture ошибки -- часть контракта Domain Layer. UseCase возвращает `Result<T>` или sealed class вместо выбрасывания исключений. Это делает ошибки **явными**: ViewModel обязан обработать `SearchResult.Error`, потому что `when` expression в Kotlin требует exhaustive matching. Подробнее о стратегиях обработки ошибок -- в [[error-handling]].

### [[android-repository-pattern]] -- Data Layer в деталях

Clean Architecture определяет **что** делает Data Layer (реализует интерфейсы из Domain). [[android-repository-pattern]] объясняет **как**: стратегии кэширования (Cache-First, Network-First, Stale-While-Revalidate), offline-first, синхронизация, conflict resolution. Эти два файла дополняют друг друга.

### [[android-modularization]] -- модули как enforcement

Clean Architecture можно реализовать через пакеты или через Gradle модули. [[android-modularization]] объясняет, почему модули надёжнее: компилятор гарантирует Dependency Rule, `internal` visibility скрывает детали реализации, параллельная компиляция ускоряет билд. Типичная структура Clean Architecture: `:core:domain` (kotlin-jvm), `:core:data` (android-library), `:feature:*` (android-library).

### [[dependency-injection-fundamentals]] и [[android-hilt-deep-dive]]

Без DI Clean Architecture -- мучение. Кто создаёт `UserRepositoryImpl` и передаёт его в `GetUsersUseCase`? Руками -- громоздко. Hilt автоматизирует связывание: `@Binds` в Data-модуле маппит `UserRepositoryImpl → UserRepository`. ViewModel получает UseCase через `@Inject constructor`. Теория DI -- в [[dependency-injection-fundamentals]], Hilt-специфика -- в [[android-hilt-deep-dive]].

### [[testing-fundamentals]] и [[mocking-strategies]]

Clean Architecture делает тестирование тривиальным. Domain Layer не зависит от Android -- тесты на чистом JUnit. UseCase тестируется с fake Repository (не mock!). Fake содержит упрощённую реализацию, mock -- проверяет вызовы. Fakes надёжнее: они ломаются, когда ломается логика, а не когда меняется внутренняя реализация. Подробнее: [[testing-fundamentals]] и [[mocking-strategies]].

---

## Источники

| Источник | Тип | URL |
|----------|-----|-----|
| Robert C. Martin "The Clean Architecture" (2012) | Блог-пост (оригинал) | [blog.cleancoder.com](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) |
| Robert C. Martin "Clean Architecture" (2017) | Книга | [ISBN 978-0134494166](https://www.goodreads.com/book/show/18043011-clean-architecture) |
| Google "Guide to App Architecture -- Domain Layer" | Документация | [developer.android.com](https://developer.android.com/topic/architecture/domain-layer) |
| Google "Now in Android" -- Architecture | Reference app | [github.com/android/nowinandroid](https://github.com/android/nowinandroid/blob/main/docs/ArchitectureLearningJourney.md) |
| Konsist -- Architecture testing | Документация | [docs.konsist.lemonappdev.com](https://docs.konsist.lemonappdev.com/) |
| Fernando Cejas "Architecting Android...The clean way?" (2014) | Блог-пост | [fernandocejas.com](https://fernandocejas.com/2014/09/03/architecting-android-the-clean-way/) |
| Yoel Gluschnaider "Clean Architecture on Android: Over Engineering?" | Блог-пост | [medium.com](https://yoelglus.medium.com/clean-architecture-on-android-over-engineering-or-just-common-sense-aac54aecc4e4) |
| UseCase Red Flags (Teknasyon Engineering) | Блог-пост | [engineering.teknasyon.com](https://engineering.teknasyon.com/usecase-red-flags-and-best-practices-in-clean-architecture-76e2f6d921eb) |

---

## Проверь себя

<details>
<summary><strong>1. Почему Repository interface объявляется в Domain Layer, а не в Data Layer? Какой принцип SOLID это реализует?</strong></summary>

Это реализация **Dependency Inversion Principle (DIP)**: модули высокого уровня (Domain) не должны зависеть от модулей низкого уровня (Data). Оба должны зависеть от абстракций.

Если interface в Data -- Domain зависит от Data (нарушение Dependency Rule). Если interface в Domain -- Data зависит от Domain (правильно: зависимости направлены внутрь).

Практический эффект: `:core:domain` -- чистый Kotlin модуль без зависимости на `:core:data`. Смена Room на SQLDelight или Retrofit на Ktor не затрагивает Domain Layer.

</details>

<details>
<summary><strong>2. Вот UseCase. Это антипаттерн или нет? Почему?</strong>

```kotlin
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts()
}
```

</summary>

Это **антипаттерн "Proxy UseCase"**. UseCase просто делегирует вызов в Repository без добавления логики. Он не комбинирует данные, не валидирует, не трансформирует -- добавляет класс ради класса.

**Решение:** ViewModel вызывает `productRepository.getProducts()` напрямую. UseCase создаётся, когда появится реальная бизнес-логика (комбинация репозиториев, валидация, трансформация).

Google в NiA использует именно этот подход: UseCase только для сложных случаев.

</details>

<details>
<summary><strong>3. В проекте 3 модели: UserDto, User (domain), UserUiModel. Все три имеют одинаковые поля: id, name, email. Что вы предложите?</strong></summary>

Три модели с одинаковыми полями -- **over-engineering**. Предложения:

1. **Убрать UserUiModel** -- если UI показывает данные без трансформации, ViewModel может использовать Domain Model напрямую
2. **Оставить UserDto + User** -- DTO нужен для сериализации (API может измениться), Domain Model -- для бизнес-логики
3. **Если даже DTO = Domain** -- использовать одну модель с `@Serializable` и добавить mapper только когда форматы начнут расходиться

Правило: **начинать с минимума моделей, добавлять по мере необходимости**. Предвидеть будущие различия -- оправдание для over-engineering.

</details>

---

## Ключевые карточки

**Q:** Что такое Dependency Rule в Clean Architecture?
**A:** Зависимости исходного кода направлены только ВНУТРЬ. Внутренние круги (Entities, Use Cases) не знают ничего о внешних кругах (UI, Database, Frameworks). Данные пересекают границы в виде простых структур (DTO).

---

**Q:** Зачем Domain Layer делать `kotlin("jvm")` модулем без Android SDK?
**A:** Три причины: (1) Тесты на чистом JUnit без Robolectric -- запуск за секунды. (2) KMP-ready -- можно переиспользовать на iOS. (3) Физическая гарантия: попытка импортировать `android.*` сломает компиляцию.

---

**Q:** Что такое Proxy UseCase и почему это антипаттерн?
**A:** UseCase, который просто вызывает один метод Repository без добавления логики: `invoke() = repo.getAll()`. Не комбинирует данные, не валидирует, не трансформирует. Добавляет класс, файл и тест ради нуля ценности. Решение: ViewModel вызывает Repository напрямую.

---

**Q:** Когда UseCase оправдан?
**A:** Когда он добавляет реальную ценность: (1) комбинирует данные из 2+ репозиториев, (2) содержит бизнес-валидацию, (3) переиспользуется в 3+ ViewModels, (4) выполняет нетривиальную трансформацию данных.

---

**Q:** Как Konsist проверяет Dependency Rule?
**A:** Определяет слои через пакеты (`Layer("Domain", "com.myapp.domain..")`) и утверждает зависимости: `domain.dependsOnNothing()`, `presentation.dependsOn(domain)`, `data.dependsOn(domain)`. Тесты запускаются как обычные JUnit -- нарушение архитектуры = упавший тест.

---

**Q:** Чем Android Clean Architecture отличается от оригинала Uncle Bob?
**A:** Оригинал: 4 круга (Entities, Use Cases, Interface Adapters, Frameworks & Drivers) для enterprise-систем. Android-адаптация: 3 слоя (Presentation, Domain, Data), Entities + Use Cases сливаются в Domain Layer. Domain Layer опциональный (Google). Принцип (Dependency Rule) -- тот же, структура -- упрощённая.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Архитектурные паттерны (обзор) | [[android-architecture-patterns]] | Контекст: MVP, MVVM, MVI -- альтернативы Presentation Layer |
| MVVM deep dive | [[android-mvvm-deep-dive]] | Presentation Layer в деталях: ViewModel, StateFlow, Compose |
| MVI deep dive | [[android-mvi-deep-dive]] | Продвинутый Presentation Layer: unidirectional data flow |
| Repository Pattern | [[android-repository-pattern]] | Data Layer в деталях: кэширование, offline-first, SSOT |
| Модуляризация | [[android-modularization]] | Gradle модули как enforcement механизм для Clean Architecture |
| Hilt DI | [[android-hilt-deep-dive]] | DI wiring: @Binds, @Provides, Scoping |
| SOLID | [[solid-principles]] | DIP, SRP, ISP -- принципы за Clean Architecture |
| Тестирование | [[testing-fundamentals]] | Как тестировать каждый слой |
