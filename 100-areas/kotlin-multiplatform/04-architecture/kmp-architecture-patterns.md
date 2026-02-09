---
title: "KMP Architecture Patterns: Clean Architecture, MVI, MVVM"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, architecture, clean-architecture, mvi, mvvm, patterns]
related:
  - "[[00-kmp-overview]]"
  - "[[kmp-di-patterns]]"
  - "[[kmp-state-management]]"
cs-foundations:
  - "[[software-architecture-principles]]"
  - "[[separation-of-concerns]]"
  - "[[dependency-inversion-principle]]"
  - "[[state-machines-theory]]"
  - "[[unidirectional-data-flow]]"
---

# KMP Architecture Patterns

> **TL;DR:** В KMP работают все популярные паттерны: MVVM, MVI, Clean Architecture. MVVM — самый популярный с shared ViewModel через `lifecycle-viewmodel-compose` или moko-mvvm. MVI (MVIKotlin, Orbit) — для complex state management с unidirectional data flow. Clean Architecture: domain (use cases) полностью shared, data (repositories) частично shared, presentation (ViewModels) shared. Feature-oriented модульность для больших команд. Netflix, McDonald's, Forbes используют эти паттерны в production.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin Coroutines | Async operations | [[kotlin-coroutines]] |
| StateFlow/SharedFlow | State management | [[kotlin-flow]] |
| KMP Project Structure | Source sets | [[kmp-project-structure]] |
| Compose Basics | UI framework | [[compose-basics]] |
| **CS-foundations** | | |
| SOLID Principles | Dependency Inversion in layers | [[solid-principles]] |
| Finite State Machines | Понимание MVI pattern | [[state-machines-theory]] |
| Separation of Concerns | Слоистая архитектура | [[separation-of-concerns]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Clean Architecture** | Слоистая архитектура по Uncle Bob | Луковица — каждый слой зависит только от внутреннего |
| **MVVM** | Model-View-ViewModel | Переводчик между данными и UI |
| **MVI** | Model-View-Intent | Конвейер: действие → состояние → UI |
| **UseCase** | Единица бизнес-логики | Рецепт приготовления блюда |
| **Repository** | Абстракция над данными | Библиотекарь, знающий где что лежит |
| **Store** | MVI контейнер состояния | Сейф с единственным источником правды |
| **Intent** | Намерение пользователя | Запрос клиента в ресторане |

---

## Почему архитектурные паттерны критичны для Multiplatform?

### Проблема: Code Sharing ≠ Architecture Sharing

**Без правильной архитектуры KMP превращается в ад:**

Когда разработчики начинают KMP проект без архитектурного плана, они сталкиваются с фундаментальной проблемой — **платформенный bias**. Android-разработчики создают ViewModels, заточенные под Android lifecycle. iOS-разработчики не понимают Kotlin coroutines и дублируют логику в SwiftUI views. Результат: 30% shared code вместо заявленных 80%.

**Научное обоснование (Separation of Concerns):**

Clean Architecture и слоистые паттерны основаны на принципе **Separation of Concerns** (SoC), впервые формализованном Edsger Dijkstra в 1974. Суть: каждый модуль программы должен отвечать за отдельный аспект функциональности.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY INVERSION В KMP                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────────────────────────────────────────────┐         │
│   │                HIGH-LEVEL MODULES                     │         │
│   │   Domain Layer (UseCases, Entities)                   │         │
│   │   100% Kotlin, 100% Shared                            │         │
│   └───────────────────────┬──────────────────────────────┘         │
│                           │                                         │
│                           │ зависит от АБСТРАКЦИЙ                   │
│                           ▼                                         │
│   ┌──────────────────────────────────────────────────────┐         │
│   │                   ABSTRACTIONS                        │         │
│   │   Repository interfaces, DataSource interfaces        │         │
│   │   Определены в Domain, реализованы в Data             │         │
│   └───────────────────────┬──────────────────────────────┘         │
│                           │                                         │
│                           │ реализуют                               │
│                           ▼                                         │
│   ┌──────────────────────────────────────────────────────┐         │
│   │                 LOW-LEVEL MODULES                     │         │
│   │   Data Layer (Ktor, SQLDelight, platform APIs)        │         │
│   │   expect/actual для platform-specific                 │         │
│   └──────────────────────────────────────────────────────┘         │
│                                                                     │
│   "High-level modules should not depend on low-level modules.       │
│    Both should depend on abstractions." — Uncle Bob                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Почему MVI — это Finite State Machine?

**MVI (Model-View-Intent)** — это реализация **Finite State Machine (FSM)** в UI-контексте:

| FSM Concept | MVI Equivalent | Описание |
|-------------|----------------|----------|
| States | State data class | Конечное множество состояний UI |
| Alphabet (inputs) | Intents | Входные события от пользователя |
| Transition function | Reducer | δ(state, intent) = newState |
| Output | Labels/SideEffects | Одноразовые события (navigation, toast) |

**Формально:**
```
MVI Store = (S, Σ, δ, s₀, F)
где:
  S = множество всех возможных State
  Σ = множество всех Intent
  δ = Reducer функция
  s₀ = initialState
  F = финальные состояния (optional)
```

**Преимущества FSM-подхода:**
- **Детерминизм**: одинаковый Intent в одинаковом State даёт одинаковый результат
- **Тестируемость**: легко проверить все переходы
- **Time-travel debugging**: можно "перемотать" цепочку состояний
- **Predictability**: UI всегда отражает текущий State

### Почему MVVM проще, но MVI надёжнее?

**MVVM** работает как **Event-Driven Architecture**:
- ViewModel принимает события и обновляет state
- Нет строгих правил для transitions
- Проще написать, сложнее дебажить

**MVI** работает как **State Machine**:
- Все transitions через Reducer — чистую функцию
- Побочные эффекты изолированы в Executor
- Сложнее написать, проще дебажить

```
// MVVM: мутации в любом месте
class ViewModel {
    fun doSomething() {
        _state.value = state.value.copy(loading = true)  // мутация 1
        viewModelScope.launch {
            _state.value = state.value.copy(data = fetch())  // мутация 2
            _state.value = state.value.copy(loading = false)  // мутация 3
        }
    }
}

// MVI: все мутации через Reducer
sealed class Message {
    object Loading : Message()
    data class DataLoaded(val data: Data) : Message()
}

object Reducer {
    fun reduce(state: State, msg: Message): State = when (msg) {
        Loading -> state.copy(loading = true)
        is DataLoaded -> state.copy(data = msg.data, loading = false)
    }
}
// Reducer — ЧИСТАЯ ФУНКЦИЯ без side effects!
```

### Когда что выбирать (Decision Framework)

```
┌─────────────────────────────────────────────────────────────────────┐
│               ARCHITECTURE SELECTION DECISION TREE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Размер команды?                                                   │
│       │                                                             │
│       ├─► 1-3 разработчика                                          │
│       │       │                                                     │
│       │       └─► Сложность state?                                  │
│       │               │                                             │
│       │               ├─► Простой ──► MVVM + StateFlow              │
│       │               └─► Complex ──► Orbit MVI (simpler than MVI)  │
│       │                                                             │
│       ├─► 4-10 разработчиков                                        │
│       │       │                                                     │
│       │       └─► Modularization ──► Clean Architecture + MVVM      │
│       │                              или MVI для critical features   │
│       │                                                             │
│       └─► 10+ разработчиков                                         │
│               │                                                     │
│               └─► Full Clean Architecture + Feature Modules          │
│                   + MVI (MVIKotlin) для shared business logic       │
│                                                                     │
│   Shared UI (Compose Multiplatform)?                                │
│       ├─► Да ──► Navigation Compose + любой pattern                 │
│       └─► Нет (SwiftUI + Compose) ──► Decompose + MVIKotlin         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Обзор паттернов

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE PATTERNS В KMP                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   MVVM (Model-View-ViewModel)                                       │
│   ─────────────────────────────                                     │
│   • Самый популярный для KMP                                        │
│   • Shared ViewModel через lifecycle-viewmodel-compose              │
│   • StateFlow для реактивного state                                 │
│   • Хорошо для простых-средних приложений                           │
│                                                                     │
│   MVI (Model-View-Intent)                                           │
│   ─────────────────────────────                                     │
│   • Unidirectional data flow                                        │
│   • Predictable state management                                    │
│   • MVIKotlin, Orbit MVI frameworks                                 │
│   • Хорошо для complex state, enterprise apps                       │
│                                                                     │
│   Clean Architecture                                                │
│   ─────────────────────────────                                     │
│   • Layered: UI → Presentation → Domain → Data                      │
│   • Domain layer 100% shared                                        │
│   • Максимальная testability и maintainability                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Clean Architecture

### Слои

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLEAN ARCHITECTURE LAYERS                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐                                                   │
│   │     UI      │  Compose / SwiftUI                                │
│   │  (View)     │  Platform-specific                                │
│   └──────┬──────┘                                                   │
│          │                                                          │
│   ┌──────▼──────┐                                                   │
│   │ Presentation│  ViewModel, State, Events                         │
│   │ (ViewModel) │  SHARED in commonMain                             │
│   └──────┬──────┘                                                   │
│          │                                                          │
│   ┌──────▼──────┐                                                   │
│   │   Domain    │  UseCases, Entities, Interfaces                   │
│   │ (UseCases)  │  100% SHARED, pure Kotlin                         │
│   └──────┬──────┘                                                   │
│          │                                                          │
│   ┌──────▼──────┐                                                   │
│   │    Data     │  Repositories, DataSources, Mappers               │
│   │ (Repository)│  SHARED implementation + platform DI              │
│   └─────────────┘                                                   │
│                                                                     │
│   Dependency Rule: Inner layers know NOTHING about outer            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Domain Layer (100% Shared)

```kotlin
// commonMain/domain/model/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String
)

// commonMain/domain/repository/UserRepository.kt
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun getUsers(): List<User>
    suspend fun saveUser(user: User)
}

// commonMain/domain/usecase/GetUserUseCase.kt
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(id: String): Result<User> {
        return runCatching {
            repository.getUser(id)
        }
    }
}

// commonMain/domain/usecase/GetUsersUseCase.kt
class GetUsersUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(): Result<List<User>> {
        return runCatching {
            repository.getUsers()
        }
    }
}
```

### Data Layer (Shared Implementation)

```kotlin
// commonMain/data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return try {
            val user = remoteDataSource.getUser(id)
            localDataSource.saveUser(user)
            user
        } catch (e: Exception) {
            localDataSource.getUser(id) ?: throw e
        }
    }

    override suspend fun getUsers(): List<User> {
        return remoteDataSource.getUsers()
    }

    override suspend fun saveUser(user: User) {
        localDataSource.saveUser(user)
        remoteDataSource.saveUser(user)
    }
}

// commonMain/data/remote/UserRemoteDataSource.kt
class UserRemoteDataSource(
    private val httpClient: HttpClient
) {
    suspend fun getUser(id: String): User {
        return httpClient.get("users/$id").body()
    }

    suspend fun getUsers(): List<User> {
        return httpClient.get("users").body()
    }

    suspend fun saveUser(user: User) {
        httpClient.post("users") {
            setBody(user)
        }
    }
}
```

### Presentation Layer (Shared ViewModel)

```kotlin
// commonMain/presentation/UserListViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class UserListViewModel(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            getUsersUseCase()
                .onSuccess { users ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        users = users,
                        error = null
                    )
                }
                .onFailure { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = error.message
                    )
                }
        }
    }

    fun refresh() {
        loadUsers()
    }
}

data class UserListUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)
```

---

## MVVM Pattern

### Shared ViewModel (Official Approach)

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose:2.9.6")
        }
        // Для Desktop добавить:
        jvmMain.dependencies {
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.8.0")
        }
    }
}
```

```kotlin
// commonMain/presentation/ProfileViewModel.kt
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class ProfileViewModel : ViewModel() {
    private val _state = MutableStateFlow(ProfileState())
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    fun updateName(name: String) {
        _state.value = _state.value.copy(name = name)
    }

    fun save() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isSaving = true)
            // Save logic
            _state.value = _state.value.copy(isSaving = false)
        }
    }
}

data class ProfileState(
    val name: String = "",
    val email: String = "",
    val isSaving: Boolean = false
)
```

```kotlin
// commonMain/ui/ProfileScreen.kt
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun ProfileScreen(
    // ВАЖНО: На non-JVM platforms нужен initializer
    viewModel: ProfileViewModel = viewModel { ProfileViewModel() }
) {
    val state = viewModel.state.collectAsState()

    Column {
        TextField(
            value = state.value.name,
            onValueChange = { viewModel.updateName(it) }
        )

        Button(
            onClick = { viewModel.save() },
            enabled = !state.value.isSaving
        ) {
            Text(if (state.value.isSaving) "Saving..." else "Save")
        }
    }
}
```

### moko-mvvm (Alternative)

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            api("dev.icerock.moko:mvvm-core:0.16.1")
            api("dev.icerock.moko:mvvm-flow:0.16.1")
            api("dev.icerock.moko:mvvm-compose:0.16.1")
        }
    }
}
```

```kotlin
// commonMain/presentation/ListViewModel.kt
import dev.icerock.moko.mvvm.viewmodel.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class ListViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<String>>(emptyList())
    val items: StateFlow<List<String>> = _items

    fun loadItems() {
        viewModelScope.launch {
            _items.value = fetchItems()
        }
    }
}
```

```swift
// iOS: SwiftUI интеграция
import SwiftUI
import shared
import mokoMvvmFlowSwiftUI

struct ListView: View {
    @StateObject var viewModel = ListViewModel()

    var body: some View {
        List(viewModel.items.collectAsState().value, id: \.self) { item in
            Text(item)
        }
        .onAppear { viewModel.loadItems() }
    }
}
```

---

## MVI Pattern

### Концепция

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MVI UNIDIRECTIONAL DATA FLOW                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     Intent      ┌──────────┐                         │
│   │          │ ───────────────>│          │                         │
│   │   View   │                 │   Store  │                         │
│   │          │<─────────────── │          │                         │
│   └──────────┘     State       └──────────┘                         │
│                                     │                               │
│                                     │ Label (one-time events)       │
│                                     ▼                               │
│                              Navigation, Toast, etc.                │
│                                                                     │
│   Flow:                                                             │
│   1. User interacts with View                                       │
│   2. View sends Intent to Store                                     │
│   3. Store processes Intent (Executor)                              │
│   4. Executor emits Message                                         │
│   5. Reducer creates new State from Message                         │
│   6. View renders new State                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### MVIKotlin Implementation

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("com.arkivanov.mvikotlin:mvikotlin:4.0.0")
            implementation("com.arkivanov.mvikotlin:mvikotlin-main:4.0.0")
            implementation("com.arkivanov.mvikotlin:mvikotlin-extensions-coroutines:4.0.0")
        }
    }
}
```

```kotlin
// commonMain/store/CounterStore.kt
import com.arkivanov.mvikotlin.core.store.Store

interface CounterStore : Store<CounterStore.Intent, CounterStore.State, CounterStore.Label> {

    sealed class Intent {
        object Increment : Intent()
        object Decrement : Intent()
        data class Add(val value: Int) : Intent()
    }

    data class State(
        val count: Int = 0,
        val isLoading: Boolean = false
    )

    sealed class Label {
        data class CountReached(val count: Int) : Label()
    }
}
```

```kotlin
// commonMain/store/CounterStoreFactory.kt
import com.arkivanov.mvikotlin.core.store.StoreFactory
import com.arkivanov.mvikotlin.extensions.coroutines.CoroutineExecutor
import kotlinx.coroutines.launch

class CounterStoreFactory(
    private val storeFactory: StoreFactory
) {
    fun create(): CounterStore =
        object : CounterStore,
            Store<CounterStore.Intent, CounterStore.State, CounterStore.Label> by storeFactory.create(
                name = "CounterStore",
                initialState = CounterStore.State(),
                executorFactory = ::ExecutorImpl,
                reducer = ReducerImpl
            ) {}

    private sealed class Message {
        data class CountChanged(val count: Int) : Message()
        data class Loading(val isLoading: Boolean) : Message()
    }

    private inner class ExecutorImpl :
        CoroutineExecutor<CounterStore.Intent, Nothing, CounterStore.State, Message, CounterStore.Label>() {

        override fun executeIntent(intent: CounterStore.Intent) {
            when (intent) {
                is CounterStore.Intent.Increment -> {
                    dispatch(Message.CountChanged(state().count + 1))
                    checkThreshold()
                }
                is CounterStore.Intent.Decrement -> {
                    dispatch(Message.CountChanged(state().count - 1))
                }
                is CounterStore.Intent.Add -> {
                    scope.launch {
                        dispatch(Message.Loading(true))
                        // Simulate async operation
                        delay(1000)
                        dispatch(Message.CountChanged(state().count + intent.value))
                        dispatch(Message.Loading(false))
                    }
                }
            }
        }

        private fun checkThreshold() {
            if (state().count >= 10) {
                publish(CounterStore.Label.CountReached(state().count))
            }
        }
    }

    private object ReducerImpl : Reducer<CounterStore.State, Message> {
        override fun CounterStore.State.reduce(msg: Message): CounterStore.State =
            when (msg) {
                is Message.CountChanged -> copy(count = msg.count)
                is Message.Loading -> copy(isLoading = msg.isLoading)
            }
    }
}
```

### Orbit MVI Implementation

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("org.orbit-mvi:orbit-core:9.0.0")
            implementation("org.orbit-mvi:orbit-compose:9.0.0")
        }
    }
}
```

```kotlin
// commonMain/viewmodel/CartViewModel.kt
import org.orbitmvi.orbit.ContainerHost
import org.orbitmvi.orbit.container
import org.orbitmvi.orbit.syntax.simple.intent
import org.orbitmvi.orbit.syntax.simple.postSideEffect
import org.orbitmvi.orbit.syntax.simple.reduce

data class CartState(
    val items: List<CartItem> = emptyList(),
    val total: Double = 0.0,
    val isLoading: Boolean = false
)

sealed class CartSideEffect {
    data class ShowToast(val message: String) : CartSideEffect()
    object NavigateToCheckout : CartSideEffect()
}

class CartViewModel : ContainerHost<CartState, CartSideEffect>, ViewModel() {

    override val container = container<CartState, CartSideEffect>(CartState())

    fun addItem(item: CartItem) = intent {
        reduce {
            state.copy(
                items = state.items + item,
                total = state.total + item.price
            )
        }
        postSideEffect(CartSideEffect.ShowToast("${item.name} added to cart"))
    }

    fun removeItem(itemId: String) = intent {
        val item = state.items.find { it.id == itemId } ?: return@intent
        reduce {
            state.copy(
                items = state.items.filter { it.id != itemId },
                total = state.total - item.price
            )
        }
    }

    fun checkout() = intent {
        if (state.items.isEmpty()) {
            postSideEffect(CartSideEffect.ShowToast("Cart is empty"))
            return@intent
        }
        postSideEffect(CartSideEffect.NavigateToCheckout)
    }
}
```

```kotlin
// commonMain/ui/CartScreen.kt
import org.orbitmvi.orbit.compose.collectAsState
import org.orbitmvi.orbit.compose.collectSideEffect

@Composable
fun CartScreen(viewModel: CartViewModel = viewModel { CartViewModel() }) {
    val state = viewModel.collectAsState().value

    viewModel.collectSideEffect { sideEffect ->
        when (sideEffect) {
            is CartSideEffect.ShowToast -> {
                // Show toast
            }
            CartSideEffect.NavigateToCheckout -> {
                // Navigate
            }
        }
    }

    Column {
        LazyColumn {
            items(state.items) { item ->
                CartItemRow(
                    item = item,
                    onRemove = { viewModel.removeItem(item.id) }
                )
            }
        }

        Text("Total: $${state.total}")

        Button(onClick = { viewModel.checkout() }) {
            Text("Checkout")
        }
    }
}
```

---

## Feature-Oriented Architecture

### Структура модулей

```
project/
├── shared/
│   ├── core/                    # Общие utilities
│   │   ├── network/
│   │   ├── database/
│   │   └── utils/
│   ├── feature-auth/            # Авторизация
│   │   ├── domain/
│   │   ├── data/
│   │   └── presentation/
│   ├── feature-profile/         # Профиль
│   │   ├── domain/
│   │   ├── data/
│   │   └── presentation/
│   └── feature-feed/            # Лента
│       ├── domain/
│       ├── data/
│       └── presentation/
├── androidApp/
└── iosApp/
```

### Feature Module Structure

```kotlin
// shared/feature-auth/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":shared:core"))
            implementation(libs.ktor.client)
            implementation(libs.kotlinx.coroutines)
        }
    }
}
```

```kotlin
// shared/feature-auth/domain/usecase/LoginUseCase.kt
class LoginUseCase(
    private val authRepository: AuthRepository,
    private val tokenStorage: TokenStorage
) {
    suspend operator fun invoke(
        email: String,
        password: String
    ): Result<User> = runCatching {
        val authResult = authRepository.login(email, password)
        tokenStorage.saveToken(authResult.token)
        authResult.user
    }
}

// shared/feature-auth/domain/usecase/LogoutUseCase.kt
class LogoutUseCase(
    private val authRepository: AuthRepository,
    private val tokenStorage: TokenStorage
) {
    suspend operator fun invoke(): Result<Unit> = runCatching {
        authRepository.logout()
        tokenStorage.clearToken()
    }
}
```

### Преимущества Feature Modules

| Аспект | Преимущество |
|--------|--------------|
| **Team Scalability** | Команды владеют features end-to-end |
| **Build Speed** | Параллельная компиляция модулей |
| **Testing** | Изолированное тестирование |
| **Code Ownership** | Чёткие границы ответственности |
| **Dependency Management** | Минимальные межмодульные зависимости |

---

## Сравнение паттернов

| Аспект | MVVM | MVI | Clean + MVVM |
|--------|------|-----|--------------|
| **Сложность** | Низкая | Средняя-Высокая | Высокая |
| **Boilerplate** | Минимальный | Средний | Больше |
| **State Management** | StateFlow | Store/Container | StateFlow |
| **Predictability** | Средняя | Высокая | Высокая |
| **Testing** | Хорошая | Отличная | Отличная |
| **Learning Curve** | Низкая | Средняя | Средняя |
| **Best For** | Simple-Medium apps | Complex state | Enterprise |

### Когда что выбирать

```
✅ MVVM:
   • Простые-средние приложения
   • Быстрый старт
   • Команда знакома с Android MVVM

✅ MVI (MVIKotlin/Orbit):
   • Complex state management
   • Много async operations
   • Enterprise/Fintech приложения
   • Нужна time-travel debugging

✅ Clean Architecture:
   • Большие команды
   • Long-term проекты
   • Максимальная testability
   • Частые изменения requirements
```

---

## Production Examples

| Компания | Архитектура | Результат |
|----------|-------------|-----------|
| **Netflix** | Clean + MVVM | 60% shared code |
| **McDonald's** | Feature modules | Unified experience |
| **Cash App** | MVI-like | Shared business logic |
| **Forbes** | MVVM | 80%+ shared code |
| **9GAG** | Clean Architecture | 70% shared code |

---

## Мифы и заблуждения

### Миф 1: "MVI — это overcomplicated MVVM"

**Реальность:** MVI — это формализованная State Machine, не усложнение MVVM. Если приложение имеет complex state transitions, MVI **упрощает** debugging и testing. Для simple apps MVI действительно overkill, но для fintech/enterprise — must-have.

### Миф 2: "Clean Architecture добавляет слишком много boilerplate"

**Реальность:** Boilerplate окупается в:
- **Testability**: каждый слой тестируется изолированно
- **Maintainability**: изменения в API не ломают UI
- **Team scaling**: разные команды работают над разными слоями
- **Code sharing**: Domain layer = 100% shared без изменений

Для solo-dev проекта Clean Architecture может быть overkill. Для команды 5+ — необходимость.

### Миф 3: "Shared ViewModel = проблемы с iOS lifecycle"

**Реальность:** С AndroidX `lifecycle-viewmodel-compose` 2.8.0+ и `IosViewModelStoreOwner` — lifecycle работает корректно на обеих платформах. Проблемы возникают только при неправильном использовании (обновление state из background thread на iOS).

### Миф 4: "Нужно выбрать moko-mvvm ИЛИ official ViewModel"

**Реальность:** С 2024 года официальный AndroidX ViewModel полностью поддерживает KMP. moko-mvvm был нужен раньше; сейчас для новых проектов рекомендуется official lifecycle-viewmodel-compose.

### Миф 5: "Feature modules замедляют сборку"

**Реальность:** Feature modules **ускоряют** incremental builds благодаря параллельной компиляции. Первичная full build может быть чуть дольше, но daily development быстрее.

### Миф 6: "MVIKotlin и Decompose — это одно и то же"

**Реальность:** Это разные инструменты от одного автора:
- **MVIKotlin** — MVI state management (Store, Reducer, Executor)
- **Decompose** — Component-based navigation и lifecycle
- Они **дополняют** друг друга, но используются для разных целей

### Миф 7: "Orbit MVI — это 'lite' версия MVIKotlin"

**Реальность:** Orbit — это отдельный framework с другой философией:
- MVIKotlin: strict MVI с Store/Executor/Reducer separation
- Orbit: pragmatic MVI с reduce/sideEffect DSL
- Оба production-ready, выбор зависит от team preferences

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Common ViewModel](https://kotlinlang.org/docs/multiplatform/compose-viewmodel.html) | Official | Shared ViewModel guide |
| [KMP Production Sample](https://github.com/Kotlin/kmp-production-sample) | GitHub | Reference architecture |

### Frameworks

| Framework | Описание | Ссылка |
|-----------|----------|--------|
| MVIKotlin | MVI framework с time-travel | [arkivanov/MVIKotlin](https://github.com/arkivanov/MVIKotlin) |
| Orbit MVI | Simple MVI framework | [orbit-mvi.org](https://orbit-mvi.org/) |
| moko-mvvm | MVVM components | [icerockdev/moko-mvvm](https://github.com/icerockdev/moko-mvvm) |
| kmp-viewmodel | ViewModel library | [hoc081098/kmp-viewmodel](https://github.com/hoc081098/kmp-viewmodel) |

### Статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [MVIKotlin in Practice](https://medium.com/@mikhaltchenkov/mvikotlin-in-practice-a-modern-architecture-framework-for-android-and-kmp-ca68e58be94b) | Blog | MVIKotlin tutorial |
| [MVVM for KMP](https://medium.com/@hardikkubavat/mvvm-for-multiplatform-apps-a-production-ready-kmp-architecture-guide-98bb62acd2f1) | Blog | Production MVVM guide |
| [Clean Architecture KMP](https://proandroiddev.com/clean-architecture-example-with-kotlin-multiplatform-c361bb283fd0) | Blog | Clean Architecture example |
| [17 MVI Libraries Comparison](https://dev.to/nek12/i-compared-17-kotlin-mvi-libraries-across-103-criteria-here-are-the-best-4-5g89) | Blog | MVI framework selection |
| [Feature-Oriented Architecture](https://medium.com/@fadibouteraa/scaling-kotlin-multiplatform-a-feature-oriented-clean-architecture-for-real-products-2a838ddf1314) | Blog | Scaling patterns |

### CS-фундамент

| Тема | Почему важно | Где изучить |
|------|--------------|-------------|
| Finite State Machines | MVI = FSM implementation | [[state-machines-theory]] |
| SOLID Principles | Clean Architecture foundation | [[solid-principles]] |
| Separation of Concerns | Layer isolation | [[separation-of-concerns]] |
| Dependency Inversion | Repository pattern | [[dependency-inversion-principle]] |
| Pure Functions | Reducer predictability | [[functional-programming-basics]] |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, lifecycle-viewmodel-compose 2.9.6, MVIKotlin 4.0.0, Orbit MVI 9.0.0, Koin 4.2.0*
