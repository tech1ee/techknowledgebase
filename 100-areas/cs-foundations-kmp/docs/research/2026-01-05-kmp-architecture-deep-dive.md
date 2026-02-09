# Research Report: KMP Architecture Deep Dive 2025

**Date:** 2026-01-05
**Sources Evaluated:** 30+
**Research Depth:** Deep

## Executive Summary

KMP архитектура в 2025 строится на Clean Architecture + MVVM/MVI. Официальный AndroidX ViewModel (lifecycle-viewmodel-compose 2.9.6+) теперь полностью multiplatform — нет необходимости в moko-mvvm для новых проектов. Koin 4.2.0 лидирует в DI благодаря простому DSL и Compose integration; kotlin-inject даёт compile-time safety ценой build time. Navigation: Compose Navigation 2.9+ (official, type-safe) для CMP, Decompose для SwiftUI+Compose, Voyager для быстрого старта. MVI frameworks: MVIKotlin (complex apps, time-travel debugging), Orbit MVI (simpler, less boilerplate), FlowMVI (76 features, all KMP targets). Главные анти-паттерны: Android-centric ViewModels, логика в SwiftUI views, background state updates на iOS.

## Key Findings

### 1. Clean Architecture для KMP

**Три слоя (Feature-Oriented):**

| Layer | Content | Sharing |
|-------|---------|---------|
| Domain | UseCases, Entities, Repository interfaces | 100% shared |
| Data | Repository impl, DataSources, expect/actual | 95%+ shared |
| Presentation | ViewModel, State, Events | 80-100% shared |

**Структура модулей (2025 best practice):**
```
project/
├── core/
│   ├── network/
│   ├── database/
│   └── common/
├── feature/
│   ├── auth/
│   │   ├── domain/
│   │   ├── data/
│   │   └── presentation/
│   └── profile/
└── composeApp/  ← navigation, DI wiring
```

**Error Handling Pattern:**
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
}
// Принудительная обработка ошибок на каждом уровне
```

### 2. ViewModel Sharing (Official Support)

**AndroidX Multiplatform ViewModel (2.8.0+):**
```kotlin
// commonMain - build.gradle.kts
implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose:2.9.6")
implementation("org.jetbrains.androidx.lifecycle:lifecycle-runtime-compose:2.9.6")

// Shared ViewModel
class ProfileViewModel : ViewModel() {
    private val _state = MutableStateFlow(ProfileState())
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    fun onEvent(event: ProfileEvent) {
        viewModelScope.launch { /* ... */ }
    }
}
```

**iOS Integration:**
- `IosViewModelStoreOwner` для lifecycle management
- ViewModel lifecycle cleared при deinit SwiftUI view
- Полная совместимость с AndroidX patterns

**Альтернативы:**
- moko-mvvm — legacy, для старых проектов
- kmp-viewmodel (hoc081098) — SavedStateHandle support
- Custom — для специфических требований

### 3. Dependency Injection

**Koin 4.2.0 (Рекомендация):**
```kotlin
// commonMain
val appModule = module {
    single<AuthRepository> { AuthRepositoryImpl(get()) }
    viewModel { ProfileViewModel(get()) }
}

// Compose
@Composable
fun ProfileScreen() {
    val viewModel = koinViewModel<ProfileViewModel>()
}
```

**Koin 4.1+ Features:**
- Automatic context management (inject() without LocalKoin)
- koinActivityViewModel() / sharedViewModel()
- Graph verification
- Compose 1.8/MPP first-class support

**kotlin-inject (Alternative):**
```kotlin
@Component
abstract class AppComponent {
    abstract val profileViewModel: ProfileViewModel

    @Provides
    fun provideRepository(): AuthRepository = AuthRepositoryImpl()
}
```

| Criteria | Koin | kotlin-inject |
|----------|------|---------------|
| Build time | Fast | Slower (KSP) |
| Runtime | Slower | Faster |
| Safety | Runtime checks | Compile-time |
| Learning curve | Easy | Moderate |
| KMP support | Full | Growing |

### 4. Navigation Libraries

**Compose Navigation (Official, 2.9.1+):**
```kotlin
@Serializable
data class ProfileRoute(val userId: String)

NavHost(navController, startDestination = HomeRoute) {
    composable<ProfileRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ProfileRoute>()
        ProfileScreen(route.userId)
    }
}
```

**Decompose (UI-agnostic):**
```kotlin
interface ProfileComponent {
    val model: StateFlow<Model>
    fun onBackClicked()
}

class DefaultProfileComponent(
    componentContext: ComponentContext,
    private val onFinished: () -> Unit
) : ProfileComponent, ComponentContext by componentContext {
    // Component lives in common code
    // UI can be Compose, SwiftUI, React
}
```

**Voyager (Simple):**
```kotlin
class ProfileScreen(val userId: String) : Screen {
    @Composable
    override fun Content() {
        val viewModel = rememberScreenModel { ProfileScreenModel() }
    }
}
```

| Feature | Compose Nav | Decompose | Voyager |
|---------|-------------|-----------|---------|
| Type safety | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Deep linking | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| UI independence | ★★☆☆☆ | ★★★★★ | ★☆☆☆☆ |
| Learning curve | Medium | High | Low |
| SwiftUI support | No | Yes | No |

**Recommendation:**
- New CMP projects → Compose Navigation
- SwiftUI + Compose → Decompose
- Quick prototypes → Voyager

### 5. State Management

**StateFlow (Standard):**
```kotlin
class ViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _events = Channel<UiEvent>()
    val events = _events.receiveAsFlow()
}
```

**iOS StateFlow Collection (SKIE):**
```swift
// With SKIE - automatic AsyncSequence generation
for await state in viewModel.state {
    updateUI(state)
}
```

**Critical iOS Considerations:**
1. **Main thread updates** — всегда dispatch на main
2. **Lifecycle** — cancel при deinit
3. **SKIE preferred** — better Swift API than KMP-NativeCoroutines

### 6. MVI Frameworks Comparison

**Top 4 (из 17 проанализированных):**

| Library | Features | Best For |
|---------|----------|----------|
| FlowMVI | 76 | All KMP targets, coroutines-first |
| Ballast | High | Documentation, debugging |
| MVIKotlin | 29 | Complex apps, time-travel |
| Orbit MVI | ~30 | Simplicity, less boilerplate |

**MVIKotlin Pattern:**
```kotlin
interface ProfileStore : Store<Intent, State, Label> {
    sealed class Intent {
        data class LoadProfile(val id: String) : Intent()
    }
    data class State(val profile: Profile? = null)
    sealed class Label {
        object ProfileLoaded : Label()
    }
}
```

**Orbit MVI Pattern:**
```kotlin
class ProfileViewModel : ContainerHost<ProfileState, ProfileSideEffect>, ViewModel() {
    override val container = container<ProfileState, ProfileSideEffect>(ProfileState())

    fun loadProfile(id: String) = intent {
        reduce { state.copy(loading = true) }
        val profile = repository.getProfile(id)
        reduce { state.copy(profile = profile, loading = false) }
    }
}
```

### 7. Anti-Patterns и Ошибки

**iOS Integration Anti-Patterns:**

1. **Android-centric ViewModels**
   - Problem: ViewModels designed for Android lifecycle
   - Solution: Abstract lifecycle concerns, use interfaces

2. **Logic in SwiftUI Views**
   - Problem: iOS devs push logic to views to avoid Kotlin
   - Solution: Swift-friendly APIs, SKIE для type-safety

3. **Background State Updates**
   ```kotlin
   // WRONG - crashes on iOS
   withContext(Dispatchers.IO) {
       _state.value = newState
   }

   // CORRECT
   withContext(Dispatchers.Main.immediate) {
       _state.value = newState
   }
   ```

4. **Missing Cancellation**
   - Always cancel coroutine scopes on iOS deinit
   - Use structured concurrency

**Architecture Anti-Patterns:**

5. **Validation in ViewModel**
   - Move to UseCase layer for reusability

6. **Domain знает о frameworks**
   - Domain должен быть pure Kotlin only

7. **Dependency on architecture libraries**
   - MVVM doesn't need Circuit/BLOC
   - Simple is better for maintainability

**Team Anti-Patterns:**

8. **"Thin iOS layer" misconception**
   - iOS needs proper architecture too
   - Budget iOS engineering time properly

9. **Kotlin-only debugging**
   - iOS devs can't debug Kotlin in Xcode
   - Provide comprehensive logging

### 8. Production Recommendations

**Recommended Stack (2025):**
```
Architecture: Clean Architecture + Feature Modules
Pattern: MVVM (simple) or MVI (complex state)
ViewModel: AndroidX lifecycle-viewmodel-compose
DI: Koin 4.2+
Navigation: Compose Navigation (CMP) / Decompose (hybrid)
State: StateFlow + SKIE (iOS)
Async: kotlinx.coroutines
```

**Team Size Recommendations:**

| Team | Approach |
|------|----------|
| 1-3 devs | MVVM, Koin, Voyager, shared UI |
| 4-10 devs | Feature modules, Compose Nav, MVI optional |
| 10+ devs | Full Clean Arch, Decompose, strict contracts |

## Community Sentiment

### Positive
- AndroidX ViewModel multiplatform — game changer
- Koin 4.0+ Compose integration excellent
- SKIE dramatically improves iOS DX
- MVIKotlin time-travel debugging praised
- Clean Architecture maps naturally to KMP

### Negative / Concerns
- iOS tooling (Xcode debugging) still problematic
- StateFlow iOS bridging adds complexity
- MVI learning curve steep
- Feature modules increase setup time
- Documentation fragmented across sources

### Mixed
- MVVM vs MVI — team preference
- Decompose vs Compose Nav — depends on SwiftUI needs
- Koin vs kotlin-inject — build time vs safety trade-off

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Common ViewModel Docs](https://kotlinlang.org/docs/multiplatform/compose-viewmodel.html) | Official | ★★★★★ | Official ViewModel setup |
| 2 | [Koin KMP Docs](https://insert-koin.io/docs/reference/koin-mp/kmp/) | Official | ★★★★★ | DI patterns |
| 3 | [Compose Navigation](https://kotlinlang.org/docs/multiplatform/compose-navigation.html) | Official | ★★★★★ | Type-safe navigation |
| 4 | [KMP Architecture Best Practices](https://carrion.dev/en/posts/kmp-architecture/) | Blog | ★★★★☆ | Full architecture guide |
| 5 | [17 MVI Libraries Comparison](https://dev.to/nek12/i-compared-17-kotlin-mvi-libraries-across-103-criteria-here-are-the-best-4-5g89) | Expert | ★★★★☆ | MVI framework selection |
| 6 | [Feature-Oriented Clean Architecture](https://medium.com/@fadibouteraa/scaling-kotlin-multiplatform-a-feature-oriented-clean-architecture-for-real-products-2a838ddf1314) | Blog | ★★★★☆ | Scaling patterns |
| 7 | [MVIKotlin](https://arkivanov.github.io/MVIKotlin/) | Official | ★★★★★ | MVI framework |
| 8 | [Orbit MVI](https://orbit-mvi.org/) | Official | ★★★★★ | Simple MVI |
| 9 | [Decompose](https://arkivanov.github.io/Decompose/) | Official | ★★★★★ | Component navigation |
| 10 | [Koin 4.1 Release](https://blog.kotzilla.io/koin-4.1-is-here) | Official | ★★★★☆ | Latest Koin features |
| 11 | [KMP ViewModel Android Docs](https://developer.android.com/kotlin/multiplatform/viewmodel) | Official | ★★★★★ | AndroidX setup |
| 12 | [SKIE](https://skie.touchlab.co/) | Official | ★★★★★ | iOS StateFlow bridging |

## Research Methodology

- **Queries used:** 8 search queries
- **Sources found:** 40+ total
- **Sources used:** 30 (after quality filter)
- **Focus areas:** Architecture patterns, DI, Navigation, State Management, Anti-patterns
- **Combined with:** Existing research from 2026-01-03

---

*Проверено: 2026-01-09*
