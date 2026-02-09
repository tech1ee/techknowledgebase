---
title: "Миграция с React Native на KMP"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - migration
  - react-native
  - javascript
  - topic/cross-platform
  - type/concept
  - level/intermediate
related:
  - [kmp-migration-from-native]]
  - "[[kmp-migration-from-flutter]]"
  - "[[kmp-getting-started]"
cs-foundations:
  - interoperability-patterns
  - bridge-architecture
  - incremental-migration
  - language-translation
status: published
---

# Миграция с React Native на KMP

> **TL;DR:** RN → KMP миграция возможна поэтапно: через Kotlin/JS можно интегрировать shared Kotlin модуль в существующее RN приложение (reakt-native-toolkit). Или полная перезапись: JS/TS → Kotlin + нативный UI. KMP дает 15-20% меньше памяти, 30% быстрее запуск, 90-95% code reuse. Airbnb перешли на KMP в 2025 с 95% shared code. RN остается лучше для быстрых MVP с JS командой.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Basics | Понимать куда мигрируем | [[kmp-getting-started]] |
| Kotlin | Новый язык | Kotlin docs |
| Native UI | SwiftUI/Compose | Platform docs |
| React Native/JS | Понимать откуда мигрируем | RN docs |
| **CS: Bridge Architecture** | Почему RN медленнее | [[cs-bridge-patterns]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| React Native | Cross-platform на JS | Переводчик между JS и Native |
| Bridge | Связь JS ↔ Native | Мост между городами |
| JSI/TurboModules | Новый RN bridge (2025) | Скоростная магистраль |
| Kotlin/JS | Kotlin → JavaScript | Kotlin говорит на JS |
| reakt-native-toolkit | KMP для RN | Мост KMP → RN |

## Почему RN → KMP уникальна среди миграций?

**Bridge vs Native:** RN использует JS→Native bridge (даже с JSI/TurboModules). KMP компилируется напрямую в native code. Это даёт 15-20% меньше памяти и 30% быстрее старт.

**Incremental путь существует:** Через Kotlin/JS можно скомпилировать KMP shared module в JS и использовать в RN как npm package. Это позволяет мигрировать business logic постепенно.

**reakt-native-toolkit:** Генерирует native modules из KMP common code + expose Kotlin Flows напрямую в RN. Гибридный подход без полной переписки.

**Когда полная перезапись:** Если команда знает Kotlin лучше JS, или если performance критичен (CPU-intensive, battery-sensitive apps).

## Когда мигрировать с RN на KMP

### Причины для миграции

| Причина | Описание |
|---------|----------|
| Производительность | 15-20% меньше памяти, 30% быстрее старт |
| Type Safety | Kotlin статически типизирован |
| Нативный опыт | 100% нативные API без bridge |
| Kotlin команда | Команда знает Kotlin лучше JS |
| Сложная логика | CPU-intensive задачи |
| Battery | 10-15% меньше потребление |

### Когда НЕ мигрировать

| Ситуация | Почему оставаться на RN |
|----------|-------------------------|
| JS/Web команда | Быстрее на знакомом стеке |
| Быстрый MVP | RN 30-40% быстрее до рынка |
| Простое приложение | RN достаточно |
| Expo экосистема | Много готовых решений |
| Работающий продукт | Риски перевешивают пользу |

## Сравнение 2025

### Производительность

| Метрика | React Native | Kotlin Multiplatform |
|---------|--------------|----------------------|
| Memory usage | Baseline | -15-20% |
| Startup time | Baseline | -30% |
| UI animations | 60fps (Fabric) | 60fps+ |
| Data processing | Baseline | +25% faster |
| Battery drain | Baseline | -10-15% |
| Code reuse | 70-85% | 90-95% |

### Market Share (2025)

```
React Native: ████████████████████ 42%
KMP:          ████████████ 23% (+11% за 18 мес)
Flutter:      ███████████████ 30%
Native:       ████ 5%
```

### Стеки

| Аспект | React Native | KMP |
|--------|--------------|-----|
| **Язык** | JavaScript/TypeScript | Kotlin + Swift |
| **UI** | React Components | Compose + SwiftUI |
| **Типизация** | Dynamic (TS static) | Static |
| **State** | Redux, MobX, Zustand | ViewModel + StateFlow |
| **DI** | Context, Inversify | Koin, kotlin-inject |
| **Network** | Axios, fetch | Ktor Client |
| **Storage** | AsyncStorage | SQLDelight |
| **Navigation** | React Navigation | Decompose, Voyager |

## Стратегии миграции

### Вариант 1: Постепенная через Kotlin/JS

```
React Native App
       │
       ▼
┌──────────────────────────────────────┐
│     Kotlin Multiplatform Module      │
│     (compiled to JS via Kotlin/JS)   │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  Business Logic (Kotlin)       │  │
│  │  - Ktor for networking         │  │
│  │  - kotlinx-serialization       │  │
│  │  - Coroutines → Promises       │  │
│  └────────────────────────────────┘  │
│              ↓ compiles to           │
│         JavaScript module            │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│         React Native App             │
│  import { api } from 'kmp-shared'    │
└──────────────────────────────────────┘
```

#### Пример: Kotlin/JS integration

```kotlin
// shared/build.gradle.kts
kotlin {
    js(IR) {
        browser()
        binaries.library()
    }

    sourceSets {
        jsMain.dependencies {
            implementation(libs.ktor.client.js)
            implementation(libs.kotlinx.coroutines.core.js)
        }
    }
}

// shared/src/jsMain/kotlin/Api.kt
@JsExport
suspend fun fetchUsers(): Array<User> {
    return api.getUsers().toTypedArray()
}

// Использование в React Native
import { fetchUsers } from 'kmp-shared'

const users = await fetchUsers()
```

### Вариант 2: reakt-native-toolkit

```kotlin
// build.gradle.kts
plugins {
    id("de.voize.reakt-native-toolkit")
}

// shared/src/commonMain/kotlin/Api.kt
@ReactNativeModule
class UserApi(private val client: HttpClient) {

    @ReactNativeMethod
    suspend fun getUsers(): List<User> = client.get("users").body()

    @ReactNativeFlow
    fun observeUsers(): Flow<List<User>> = userRepository.observeUsers()
}

// Генерирует native modules для iOS и Android
// Можно использовать в RN как обычный native module
```

```javascript
// React Native
import { UserApi } from 'react-native-shared'

const users = await UserApi.getUsers()

// Flow → EventEmitter
UserApi.observeUsers().subscribe(users => {
    setUsers(users)
})
```

### Вариант 3: Полная миграция

```
Этап 1: Создание KMP проекта
        ─────────────────────
        - shared module
        - androidApp
        - iosApp

Этап 2: Миграция моделей
        ─────────────────
        TypeScript → Kotlin data classes

Этап 3: Миграция API
        ───────────
        Axios/fetch → Ktor Client

Этап 4: Миграция хранения
        ─────────────────
        AsyncStorage → SQLDelight

Этап 5: Миграция state
        ───────────────
        Redux → ViewModel + StateFlow

Этап 6: Нативный UI
        ──────────
        React Components → Compose/SwiftUI
```

## Маппинг кода

### Models

```typescript
// React Native (TypeScript)
interface User {
    id: number
    name: string
    email: string
    createdAt: Date
}

// Parsing
const user: User = JSON.parse(jsonString)
```

```kotlin
// KMP (Kotlin)
@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String,
    @Serializable(with = InstantSerializer::class)
    val createdAt: Instant
)

// Parsing — compile-time safe
val user: User = Json.decodeFromString(jsonString)
```

### Networking

```typescript
// React Native (Axios)
const api = axios.create({
    baseURL: 'https://api.example.com/',
    timeout: 30000
})

async function getUsers(): Promise<User[]> {
    const response = await api.get('/users')
    return response.data
}
```

```kotlin
// KMP (Ktor)
val client = HttpClient {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    defaultRequest {
        url("https://api.example.com/")
    }
}

suspend fun getUsers(): List<User> =
    client.get("users").body()
```

### State Management

```typescript
// React Native (Redux Toolkit)
const userSlice = createSlice({
    name: 'users',
    initialState: { users: [], loading: false, error: null },
    reducers: {
        setLoading: (state) => { state.loading = true },
        setUsers: (state, action) => {
            state.users = action.payload
            state.loading = false
        },
        setError: (state, action) => {
            state.error = action.payload
            state.loading = false
        }
    }
})

// Thunk
export const fetchUsers = createAsyncThunk(
    'users/fetch',
    async () => {
        const users = await api.getUsers()
        return users
    }
)
```

```kotlin
// KMP (ViewModel + StateFlow)
class UserViewModel(
    private val getUsers: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            getUsers()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message) }
        }
    }
}

sealed interface UiState {
    data object Initial : UiState
    data object Loading : UiState
    data class Success(val users: List<User>) : UiState
    data class Error(val message: String?) : UiState
}
```

### Storage

```typescript
// React Native (AsyncStorage)
import AsyncStorage from '@react-native-async-storage/async-storage'

async function saveUser(user: User): Promise<void> {
    await AsyncStorage.setItem(`user_${user.id}`, JSON.stringify(user))
}

async function getUser(id: number): Promise<User | null> {
    const json = await AsyncStorage.getItem(`user_${id}`)
    return json ? JSON.parse(json) : null
}
```

```kotlin
// KMP (SQLDelight)
-- User.sq
CREATE TABLE User (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

insertUser:
INSERT OR REPLACE INTO User(id, name, email) VALUES (?, ?, ?);

selectById:
SELECT * FROM User WHERE id = ?;

// Kotlin
suspend fun saveUser(user: User) {
    queries.insertUser(user.id, user.name, user.email)
}

fun getUser(id: Long): User? =
    queries.selectById(id).executeAsOneOrNull()
```

## Маппинг зависимостей

| React Native | KMP | Заметки |
|--------------|-----|---------|
| axios | Ktor Client | Похожий API |
| fetch | Ktor Client | Built-in |
| AsyncStorage | multiplatform-settings | Key-value |
| Realm | SQLDelight | SQL-first |
| Redux | ViewModel + StateFlow | Different pattern |
| MobX | StateFlow | Reactive |
| Zustand | StateFlow | Simpler |
| React Navigation | Decompose / Voyager | Type-safe |
| react-native-reanimated | Compose animations | Native |
| react-native-gesture-handler | Native gestures | Built-in |
| react-native-fast-image | Coil 3.x | Image loading |
| react-native-firebase | Firebase KMP | Official |
| react-native-mmkv | multiplatform-settings | Fast storage |

## Case Study: Airbnb (2025)

> "After six months of migration to KMP, we achieved 95% code sharing between platforms and cut release cycles from monthly to weekly."

**Результаты:**
- 95% shared code
- Monthly → Weekly releases
- Improved performance
- Better type safety
- Unified business logic

## Case Study: Wantedly

> Moving from React Native to Kotlin Multiplatform allowed us to maintain native UI while sharing all business logic.

**Процесс:**
1. Gradual migration feature by feature
2. Kept RN screens during transition
3. Eventually replaced all RN with native UI
4. 6 months total migration

## Timeline оценка

| Размер | RN screens | Миграция через Kotlin/JS | Полная миграция |
|--------|------------|--------------------------|-----------------|
| Small | 5-10 | 1-2 месяца | 3-4 месяца |
| Medium | 10-30 | 2-3 месяца | 5-8 месяцев |
| Large | 30+ | 3-6 месяцев | 8-12 месяцев |

## Чек-лист миграции

### Подготовка
- [ ] Аудит RN приложения (JS/TS код)
- [ ] Определить shared vs platform-specific
- [ ] Выбрать стратегию (Kotlin/JS vs полная)
- [ ] Создать KMP проект

### Постепенная миграция (Kotlin/JS)
- [ ] Настроить Kotlin/JS компиляцию
- [ ] Или интегрировать reakt-native-toolkit
- [ ] Мигрировать API layer
- [ ] Мигрировать models
- [ ] Тестирование

### Полная миграция
- [ ] Models (TypeScript → Kotlin)
- [ ] Networking (Axios → Ktor)
- [ ] Storage (AsyncStorage → SQLDelight)
- [ ] State (Redux → ViewModel)
- [ ] Android UI (React → Compose)
- [ ] iOS UI (React → SwiftUI)
- [ ] Тестирование
- [ ] CI/CD

## Best Practices

1. **Feature flags** — переключение между RN и native экранами
2. **Shared API contracts** — одинаковые типы в JS и Kotlin
3. **Параллельная разработка** — новые фичи на KMP
4. **Постепенная миграция** — экран за экраном
5. **Monitoring** — сравнение метрик RN vs native

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "RN → KMP = полная перезапись" | Kotlin/JS позволяет incremental |
| "TypeScript = type safety как Kotlin" | Kotlin строже, compile-time гарантии |
| "RN New Architecture решает все проблемы" | JSI быстрее, но всё ещё bridge |
| "KMP сложнее для JS разработчиков" | Kotlin похож на TypeScript |
| "RN экосистема больше" | KMP использует весь Android ecosystem |

## CS-фундамент

| Концепция | Применение в миграции |
|-----------|----------------------|
| Bridge Architecture | RN JS↔Native overhead |
| Native Compilation | KMP → machine code |
| Interoperability | Kotlin/JS для hybrid подхода |
| Incremental Migration | reakt-native-toolkit |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMP vs RN Official](https://kotlinlang.org/docs/multiplatform/kotlin-multiplatform-react-native.html) | Official | JetBrains comparison |
| [reakt-native-toolkit](https://github.com/voize-gmbh/reakt-native-toolkit) | GitHub | RN + KMP integration |
| [RN to KMP Migration](https://github.com/HenryQuan/react-native-kmp-migration) | GitHub | Migration example |
| [Wantedly Migration](https://medium.com/wantedly-engineering/moving-from-react-native-to-kotlin-multiplatform-292c7569692) | Blog | Real case study |
| [RN vs KMP 2026 Guide](https://www.luciq.ai/blog/react-native-vs-kotlin-mutliplatform-guide) | Blog | Detailed comparison |

---
*Проверено: 2026-01-09 | KMP Stable, React Native 0.76+*
