---
title: "Миграция с Flutter на KMP"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, migration, flutter, dart, cross-platform]
related: [[kmp-migration-from-native]], [[kmp-migration-from-rn]], [[kmp-getting-started]]
cs-foundations: [rewrite-vs-refactor, architecture-migration, language-translation, platform-abstraction]
---

# Миграция с Flutter на KMP

> **TL;DR:** Flutter → KMP требует полную перезапись: Dart → Kotlin (shared logic) + нативный UI (или Compose MP). Причины миграции: нативный UI/UX, интеграция с существующими Kotlin/Swift кодбазами, постепенное внедрение. Миграция сложнее чем с native, но дает 100% нативную производительность. Netflix, VMware, Philips используют KMP. Flutter лучше для MVP и единого UI.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Basics | Понимать куда мигрируем | [[kmp-getting-started]] |
| Kotlin | Новый язык | Kotlin docs |
| Native UI | SwiftUI/Compose | Platform docs |
| Flutter/Dart | Понимать откуда мигрируем | Flutter docs |
| **CS: Rewrite vs Refactor** | Когда переписывать с нуля | [[cs-rewrite-vs-refactor]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Flutter | Cross-platform с единым UI | IKEA мебель — одинаковая везде |
| KMP | Cross-platform с нативным UI | Дизайнерская мебель под заказ |
| Dart | Язык Flutter | Инструмент Flutter |
| Widget | UI компонент Flutter | Готовый блок конструктора |
| Compose MP | Cross-platform UI от JetBrains | Альтернатива Flutter UI |

## Почему Flutter → KMP — это rewrite, а не migration?

**Фундаментальное отличие:** Flutter = single codebase (Dart) с rendered UI. KMP = shared logic (Kotlin) + platform UI. Нет прямого пути перевода.

**Dart → Kotlin:** Языки схожи синтаксически, но экосистемы разные. Каждый BLoC/Provider → MVI/MVVM. Каждый Widget → Compose/SwiftUI.

**Что переносится:** Бизнес-требования, тестовые сценарии, API contracts. Код — нет.

**ROI расчёт:** Если Flutter работает — не трогай. Мигрируй только если native feel критичен или есть существующая Kotlin/Swift кодбаза.

## Когда мигрировать с Flutter на KMP

### Причины для миграции

| Причина | Описание |
|---------|----------|
| Нативный UI/UX | iOS должен выглядеть как iOS, Android как Android |
| Производительность | 100% нативная скорость без промежуточного слоя |
| Существующий код | Есть Kotlin/Swift кодбаза |
| Platform APIs | Глубокая интеграция с платформой |
| Native expertise | Команда знает Kotlin/Swift лучше Dart |
| Модульность | Нужна частичная миграция |

### Когда НЕ мигрировать

| Ситуация | Почему оставаться на Flutter |
|----------|------------------------------|
| Единый UI везде | Flutter быстрее для одинакового UI |
| MVP/прототип | Flutter быстрее для первой версии |
| Маленькая команда | Один Dart-разработчик vs два специалиста |
| Анимации фокус | Flutter отлично рендерит анимации |
| Работающее приложение | "If it ain't broke, don't fix it" |

## Ключевые различия

### Архитектура

```
FLUTTER                          KOTLIN MULTIPLATFORM
┌─────────────────────┐          ┌─────────────────────┐
│    Flutter App      │          │    Android App      │
├─────────────────────┤          ├─────────────────────┤
│ Dart UI (Widgets)   │          │ Compose UI          │
│ Dart BLoC/Riverpod  │          │ ViewModel           │
│ Dart Repository     │          │ ─────────────────   │
│ Dart API Client     │          │         ↓           │
│ Dart Models         │          │  ┌─────────────┐    │
└─────────────────────┘          │  │   Shared    │    │
                                 │  │   Module    │    │
Рендерится через Skia            │  │  (Kotlin)   │    │
на Canvas                        │  │             │    │
                                 │  │ Repository  │    │
                                 │  │ API Client  │    │
┌─────────────────────┐          │  │ Models      │    │
│     iOS App         │          │  │ Use Cases   │    │
├─────────────────────┤          │  └─────────────┘    │
│ (тот же Dart код)   │          │         ↑           │
│                     │          │ ─────────────────   │
└─────────────────────┘          └─────────────────────┘
                                 ┌─────────────────────┐
Один Dart код для обеих          │     iOS App         │
платформ                         ├─────────────────────┤
                                 │ SwiftUI             │
                                 │ ViewModel (Swift)   │
                                 │ Uses Shared Module  │
                                 └─────────────────────┘

                                 Нативный UI + общая логика
```

### Сравнение стеков

| Аспект | Flutter | KMP |
|--------|---------|-----|
| **Язык** | Dart | Kotlin + Swift |
| **UI** | Widgets (единый) | Compose + SwiftUI (нативный) |
| **Рендеринг** | Skia Canvas | Нативные view |
| **Hot Reload** | Есть | Compose Hot Reload |
| **State** | BLoC, Riverpod, Provider | ViewModel + StateFlow |
| **DI** | get_it, Riverpod | Koin, kotlin-inject |
| **Network** | Dio, http | Ktor Client |
| **DB** | sqflite, Hive, Drift | SQLDelight, Room KMP |
| **Serialization** | json_serializable | kotlinx-serialization |

## План миграции

### Фаза 1: Подготовка (1-2 недели)

```
1. Аудит Flutter приложения
   └── Определить бизнес-логику vs UI
   └── Список зависимостей Dart
   └── Маппинг на KMP альтернативы

2. Создание KMP проекта
   └── shared модуль
   └── androidApp модуль
   └── iosApp модуль

3. Настройка CI/CD для нового проекта
```

### Фаза 2: Миграция Models (1 неделя)

```dart
// Flutter/Dart
@freezed
class User with _$User {
  factory User({
    required int id,
    required String name,
    required String email,
    required DateTime createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) =>
      _$UserFromJson(json);
}
```

```kotlin
// KMP Kotlin
@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String,
    @Serializable(with = InstantSerializer::class)
    val createdAt: Instant
)
```

### Фаза 3: Миграция Data Layer (2-3 недели)

```dart
// Flutter/Dart - Dio
class UserApiClient {
  final Dio _dio;

  UserApiClient(this._dio);

  Future<List<User>> getUsers() async {
    final response = await _dio.get('/users');
    return (response.data as List)
        .map((json) => User.fromJson(json))
        .toList();
  }
}
```

```kotlin
// KMP Kotlin - Ktor
class UserApiClient(private val httpClient: HttpClient) {

    suspend fun getUsers(): List<User> =
        httpClient.get("users").body()

    suspend fun getUser(id: Long): User =
        httpClient.get("users/$id").body()
}
```

### Фаза 4: Миграция Repository (1-2 недели)

```dart
// Flutter/Dart - Repository
class UserRepository {
  final UserApiClient _api;
  final UserLocalDataSource _local;

  UserRepository(this._api, this._local);

  Stream<List<User>> watchUsers() async* {
    yield await _local.getUsers();

    try {
      final remote = await _api.getUsers();
      await _local.saveUsers(remote);
      yield remote;
    } catch (e) {
      // Return cached on error
    }
  }
}
```

```kotlin
// KMP Kotlin - Repository
class UserRepository(
    private val api: UserApiClient,
    private val local: UserLocalDataSource
) {
    fun observeUsers(): Flow<List<User>> = flow {
        emit(local.getUsers())

        try {
            val remote = api.getUsers()
            local.saveUsers(remote)
            emit(remote)
        } catch (e: Exception) {
            // Return cached on error
        }
    }
}
```

### Фаза 5: Миграция State Management (2 недели)

```dart
// Flutter/Dart - BLoC
class UserBloc extends Bloc<UserEvent, UserState> {
  final GetUsersUseCase _getUsers;

  UserBloc(this._getUsers) : super(UserInitial()) {
    on<LoadUsers>(_onLoadUsers);
  }

  Future<void> _onLoadUsers(
    LoadUsers event,
    Emitter<UserState> emit,
  ) async {
    emit(UserLoading());
    try {
      final users = await _getUsers();
      emit(UserLoaded(users));
    } catch (e) {
      emit(UserError(e.toString()));
    }
  }
}
```

```kotlin
// KMP Kotlin - ViewModel (shared или platform-specific)
class UserViewModel(
    private val getUsers: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Initial)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            getUsers()
                .onSuccess { users ->
                    _uiState.value = UserUiState.Success(users)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(error.message)
                }
        }
    }
}

sealed interface UserUiState {
    data object Initial : UserUiState
    data object Loading : UserUiState
    data class Success(val users: List<User>) : UserUiState
    data class Error(val message: String?) : UserUiState
}
```

### Фаза 6: UI Implementation (3-4 недели)

#### Android (Compose)

```kotlin
// Android Compose
@Composable
fun UserListScreen(
    viewModel: UserViewModel = koinViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> LoadingIndicator()
        is UserUiState.Success -> UserList(state.users)
        is UserUiState.Error -> ErrorMessage(state.message)
        else -> Unit
    }
}

@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

#### iOS (SwiftUI)

```swift
// iOS SwiftUI
struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        Group {
            switch viewModel.uiState {
            case .loading:
                ProgressView()
            case .success(let users):
                List(users, id: \.id) { user in
                    UserRow(user: user)
                }
            case .error(let message):
                Text(message ?? "Unknown error")
            default:
                EmptyView()
            }
        }
        .onAppear {
            viewModel.loadUsers()
        }
    }
}
```

### Или: Compose Multiplatform (shared UI)

```kotlin
// Shared Compose UI (commonMain)
@Composable
fun UserListScreen(
    viewModel: UserViewModel = koinViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UserUiState.Loading -> CircularProgressIndicator()
        is UserUiState.Success -> {
            LazyColumn {
                items(state.users) { user ->
                    Text(user.name)
                }
            }
        }
        is UserUiState.Error -> Text("Error: ${state.message}")
        else -> {}
    }
}
```

## Маппинг зависимостей

| Flutter (Dart) | KMP (Kotlin) | Заметки |
|----------------|--------------|---------|
| dio | Ktor Client | Похожий API |
| http | Ktor Client | Simpler alternative |
| freezed | data class | Built-in Kotlin |
| json_serializable | kotlinx-serialization | Compile-time |
| sqflite | SQLDelight | SQL-first |
| hive | multiplatform-settings | Key-value |
| drift | Room KMP / SQLDelight | ORM-like |
| get_it | Koin | Service locator |
| riverpod | Koin + StateFlow | Different paradigm |
| bloc | ViewModel + StateFlow | Different pattern |
| provider | Koin | DI |
| go_router | Decompose / Voyager | Navigation |
| shared_preferences | multiplatform-settings | Key-value |
| path_provider | kotlinx-io | File paths |
| flutter_secure_storage | Keychain/Keystore | Platform-specific |
| cached_network_image | Coil 3.x | Image loading |
| intl | kotlinx-datetime | Date/time |

## Timeline оценка

| Размер проекта | Flutter screens | Время миграции |
|----------------|-----------------|----------------|
| Small | 5-10 | 2-3 месяца |
| Medium | 10-30 | 4-6 месяцев |
| Large | 30+ | 6-12 месяцев |

### Факторы влияющие на время

| Фактор | Ускоряет | Замедляет |
|--------|----------|-----------|
| Опыт команды | Знают Kotlin/Swift | Только Dart |
| Архитектура | Clean Architecture | Spaghetti code |
| Тесты | Хорошее покрытие | Нет тестов |
| UI сложность | Простые экраны | Сложные анимации |
| Native интеграции | Мало | Много platform channels |

## Case Studies

### Netflix

> "Kotlin Multiplatform allows us to share approximately 50% of our business logic between Android and iOS, improving rollout speed and ensuring reliable behavior."

### VMware

> "We implement common foundation for networking and authentication layers, cutting time-to-market by up to 40%."

### Philips Healthcare

> "Shared Kotlin code for Bluetooth communication and data validation reduced critical errors by 35%."

## Альтернатива: Compose Multiplatform

Если главная причина на Flutter — единый UI, рассмотри Compose Multiplatform:

| Аспект | Flutter | Compose MP |
|--------|---------|------------|
| UI код | Единый (Dart) | Единый (Kotlin) |
| iOS status | Stable | Stable (май 2025) |
| Язык | Dart | Kotlin |
| Производительность | Canvas рендеринг | Native views (iOS) |
| Ecosystem | Mature | Growing fast |

## Best Practices

1. **Поэтапная миграция** — начни с одного модуля
2. **Параллельная разработка** — новые фичи на KMP, старые на Flutter
3. **Feature flags** — переключение между реализациями
4. **Общие тесты** — мигрируй тесты вместе с кодом
5. **API contract** — сохраняй совместимость backend

## Чек-лист миграции

- [ ] Аудит Flutter приложения
- [ ] Создание KMP проекта
- [ ] Миграция models
- [ ] Миграция networking (Dio → Ktor)
- [ ] Миграция database (sqflite → SQLDelight)
- [ ] Миграция repositories
- [ ] Миграция state management
- [ ] Android UI (Compose)
- [ ] iOS UI (SwiftUI или Compose MP)
- [ ] Тестирование
- [ ] CI/CD настройка

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Можно конвертировать Dart в Kotlin автоматом" | Требуется ручная переписка |
| "Flutter виджеты станут Compose компонентами" | Полная пересборка UI |
| "KMP медленнее Flutter" | Native compilation = максимальная скорость |
| "Compose MP = Flutter замена" | Разные подходы, разные trade-offs |
| "Миграция займёт пару недель" | 3-6 месяцев для среднего приложения |

## CS-фундамент

| Концепция | Применение в миграции |
|-----------|----------------------|
| Rewrite vs Refactor | Flutter → KMP = rewrite |
| Language Translation | Dart → Kotlin (manual) |
| Platform Abstraction | Общий код vs platform-specific |
| Architecture Mapping | BLoC → MVI/MVVM |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Flutter vs KMP 2025](https://www.instabug.com/blog/flutter-vs-kotlin-mutliplatform-guide) | Blog | Сравнение |
| [Migration Journey](https://medium.com/@tsortanidis.ch/from-flutter-to-kotlin-multiplatform-a-flutter-developers-migration-journey-864d1fac0be6) | Blog | Personal experience |
| [Switching from Flutter to KMP](https://medium.com/@tomerglick/switching-from-flutter-to-kmp-00a129f25cab) | Blog | Migration story |
| [KMP vs Flutter official](https://kotlinlang.org/docs/multiplatform/kotlin-multiplatform-flutter.html) | Official | JetBrains comparison |
| [Full Comparison](https://guarana-technologies.com/blog/flutter-vs-kotlin-multiplatform-2025) | Blog | Detailed analysis |

---
*Проверено: 2026-01-09 | KMP Stable, Compose MP iOS Stable*
