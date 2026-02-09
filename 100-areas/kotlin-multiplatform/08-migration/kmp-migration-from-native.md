---
title: "Миграция на KMP с Native (Android + iOS)"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - migration
  - android
  - ios
  - native
  - type/concept
  - level/intermediate
related:
  - [kmp-getting-started]]
  - "[[kmp-project-structure]]"
  - "[[kmp-ios-deep-dive]"
cs-foundations:
  - strangler-fig-pattern
  - incremental-adoption
  - modular-architecture
  - risk-management
status: published
---

# Миграция на KMP с Native (Android + iOS)

> **TL;DR:** Миграция на KMP выполняется поэтапно: Model → Data Sources → Use Cases → Repository. Начинай с создания shared модуля через Android Studio Meerkat+. Заменяй Retrofit → Ktor, Hilt → Koin, Room → SQLDelight. iOS интегрируется через XCFramework (CocoaPods/SPM). Монорепо рекомендуется для тесного сотрудничества. Netflix, McDonald's, Duolingo — в production с 50-70% shared code.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Basics | Понимать что мигрируем | [[kmp-getting-started]] |
| Project Structure | Структура shared модуля | [[kmp-project-structure]] |
| iOS Integration | Интеграция в Xcode | [[kmp-ios-deep-dive]] |
| Clean Architecture | Понимать слои | Architecture patterns |
| **CS: Strangler Fig Pattern** | Стратегия безопасной миграции | [[cs-strangler-fig]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Migration | Перенос кода в KMP | Переезд в новый дом |
| Shared Module | Общий код для всех платформ | Общая кухня в коммуналке |
| Gradual Adoption | Поэтапное внедрение | Ремонт по комнате за раз |
| Monorepo | Один репозиторий для всего | Один адрес для всех |
| XCFramework | Бинарный пакет для iOS | Готовый модуль для подключения |

## Почему Strangler Fig, а не Big Bang?

**Big Bang Risk:** Полная переписка = месяцы без релизов + высокий риск провала. Если что-то пойдёт не так, откатить сложно.

**Strangler Fig Pattern (Martin Fowler):** Legacy система "обвивается" новой по частям. Старый код продолжает работать, пока новый не заменит его полностью.

**KMP идеален для Strangler Fig:** shared module добавляется как обычная dependency. Android потребляет напрямую, iOS через XCFramework. Можно мигрировать feature за feature.

**Начинать с low-risk modules:** Analytics, validation, networking — self-contained, без UI зависимостей, легко тестировать.

## Зачем мигрировать

### Проблемы без KMP

| Проблема | Влияние |
|----------|---------|
| Дублирование кода | 2x время на разработку |
| Разные баги | Bug на iOS ≠ Bug на Android |
| Синхронизация команд | Координация затратна |
| Разные реализации | Разное поведение |
| Двойные тесты | 2x время на QA |

### Результаты после миграции

| Компания | Shared Code | Результат |
|----------|-------------|-----------|
| Netflix | 50-60% | Unified business logic |
| McDonald's | ~60% | 60% меньше platform bugs |
| Quizlet | 60-70% | 25% faster iOS, -8MB app size |
| Feres | 100% logic | 90%+ shared UI |

## Стратегия миграции

### Порядок слоёв

```
Рекомендуемый порядок миграции:

1. Model/Domain Layer     ← Начать здесь (наименее зависим)
   └── Data classes
   └── Domain entities
   └── Enums, sealed classes

2. Data Sources           ← Следующий шаг
   └── Remote API (Retrofit → Ktor)
   └── Local Storage (Room → SQLDelight)
   └── Preferences (SharedPrefs → multiplatform-settings)

3. Repository Layer
   └── Repository interfaces
   └── Repository implementations

4. Use Cases / Interactors
   └── Business logic

5. ViewModel Layer        ← Опционально
   └── С KMP ViewModel (Jetpack)
   └── Или оставить нативным

6. UI Layer               ← Последний или оставить нативным
   └── Compose Multiplatform
   └── Или нативный UI
```

### Визуализация

```
BEFORE (Native only)          AFTER (With KMP)
┌─────────────────────┐      ┌─────────────────────────────────┐
│     Android App     │      │          Android App            │
├─────────────────────┤      ├─────────────────────────────────┤
│ UI (Compose)        │      │ UI (Compose)                    │
│ ViewModels          │      │ ViewModels                      │
│ UseCases            │      │ ────────┬────────               │
│ Repository          │      │         │                       │
│ DataSource          │      │    ┌────▼────┐                  │
│ API (Retrofit)      │      │    │ Shared  │                  │
│ DB (Room)           │      │    │ Module  │                  │
│ Models              │      │    │         │                  │
└─────────────────────┘      │    │ Models  │                  │
                             │    │ UseCases│                  │
┌─────────────────────┐      │    │ Repos   │                  │
│      iOS App        │      │    │ Ktor    │                  │
├─────────────────────┤      │    │SQLDelight│                 │
│ UI (SwiftUI)        │      │    └────▲────┘                  │
│ ViewModels          │      │         │                       │
│ UseCases (Swift)    │      │ ────────┴────────               │
│ Repository (Swift)  │      └─────────────────────────────────┘
│ DataSource (Swift)  │      ┌─────────────────────────────────┐
│ API (URLSession)    │      │           iOS App               │
│ DB (CoreData)       │      ├─────────────────────────────────┤
│ Models (Swift)      │      │ UI (SwiftUI)                    │
└─────────────────────┘      │ ViewModels                      │
                             │ ────────┬────────               │
                             │         │ (via XCFramework)     │
                             │    Uses Shared Module           │
                             └─────────────────────────────────┘
```

## Шаг 1: Создание Shared Module

### Android Studio Meerkat+

```
File → New → New Module → Kotlin Multiplatform Shared Module

Настройки:
- Module name: shared
- Package name: com.example.shared
- iOS framework name: SharedKit
```

### Ручное создание

```kotlin
// settings.gradle.kts
include(":shared")

// shared/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("com.android.library")
}

kotlin {
    androidTarget {
        compilations.all {
            compileTaskProvider.configure {
                compilerOptions {
                    jvmTarget.set(JvmTarget.JVM_17)
                }
            }
        }
    }

    listOf(
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "SharedKit"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.json)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }

        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}

android {
    namespace = "com.example.shared"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

### Подключение к Android App

```kotlin
// androidApp/build.gradle.kts
dependencies {
    implementation(project(":shared"))

    // Или с Type-safe project accessors:
    // implementation(projects.shared)
}
```

## Шаг 2: Миграция Model Layer

### До (Android)

```kotlin
// Android: com.example.app.data.model.User.kt
data class User(
    val id: Long,
    val name: String,
    val email: String,
    val createdAt: Long
)
```

### После (KMP Shared)

```kotlin
// shared/src/commonMain/kotlin/com/example/shared/domain/model/User.kt
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String,
    val createdAt: Long
)
```

### Рефакторинг в Android Studio

```
1. Правый клик на класс → Refactor → Move
2. Выбрать destination: shared/src/commonMain/kotlin/...
3. Android Studio обновит imports автоматически
```

## Шаг 3: Миграция Data Layer

### Retrofit → Ktor

```kotlin
// ДО: Android Retrofit
interface UserApi {
    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Long): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User
}

// ПОСЛЕ: KMP Ktor
class UserApi(private val client: HttpClient) {

    suspend fun getUsers(): List<User> =
        client.get("users").body()

    suspend fun getUser(id: Long): User =
        client.get("users/$id").body()

    suspend fun createUser(request: CreateUserRequest): User =
        client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
}

// HttpClient factory
expect fun createHttpClient(): HttpClient

// androidMain
actual fun createHttpClient(): HttpClient = HttpClient(OkHttp) {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    defaultRequest {
        url("https://api.example.com/")
    }
}

// iosMain
actual fun createHttpClient(): HttpClient = HttpClient(Darwin) {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    defaultRequest {
        url("https://api.example.com/")
    }
}
```

### Room → SQLDelight

```kotlin
// ДО: Android Room
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Long,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "email") val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<UserEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)
}

// ПОСЛЕ: KMP SQLDelight
// shared/src/commonMain/sqldelight/com/example/shared/db/User.sq

CREATE TABLE UserEntity (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

selectAll:
SELECT * FROM UserEntity;

insertUser:
INSERT OR REPLACE INTO UserEntity(id, name, email)
VALUES (?, ?, ?);

selectById:
SELECT * FROM UserEntity WHERE id = ?;

// Kotlin wrapper
class UserLocalDataSource(private val queries: UserQueries) {

    fun getAllUsers(): Flow<List<UserEntity>> =
        queries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.Default)

    suspend fun insertUser(user: UserEntity) {
        queries.insertUser(user.id, user.name, user.email)
    }
}
```

### Hilt → Koin

```kotlin
// ДО: Android Hilt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi =
        retrofit.create(UserApi::class.java)
}

// ПОСЛЕ: KMP Koin
// shared/src/commonMain/kotlin/di/SharedModule.kt
val sharedModule = module {
    single { createHttpClient() }
    single { UserApi(get()) }
    single { UserRepository(get(), get()) }
    factory { GetUsersUseCase(get()) }
}

// Android-specific
val androidModule = module {
    single { createDatabaseDriver(get()) }
    single { AppDatabase(get()) }
}

// iOS-specific (в Swift или Kotlin)
val iosModule = module {
    single { createDatabaseDriver() }
    single { AppDatabase(get()) }
}
```

## Шаг 4: iOS Интеграция

### XCFramework генерация

```bash
# Сборка XCFramework
./gradlew :shared:assembleSharedKitXCFramework

# Результат: shared/build/XCFrameworks/release/SharedKit.xcframework
```

### CocoaPods интеграция

```ruby
# iosApp/Podfile
platform :ios, '14.0'

target 'iosApp' do
  use_frameworks!

  # Локальная разработка
  pod 'SharedKit', :path => '../shared'
end
```

```bash
cd iosApp
pod install
open iosApp.xcworkspace
```

### SPM интеграция (с KMMBridge)

```kotlin
// shared/build.gradle.kts
plugins {
    id("co.touchlab.kmmbridge") version "1.2.0"
}

kmmbridge {
    mavenPublishArtifacts()
    spm()
    githubReleaseVersions()
}
```

### Использование в SwiftUI

```swift
// iosApp/ContentView.swift
import SwiftUI
import SharedKit  // Импорт KMP модуля

struct ContentView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users, id: \.id) { user in
            Text(user.name)
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}

// iosApp/ViewModels/UserViewModel.swift
import Foundation
import SharedKit

@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var error: String?

    private let useCase: GetUsersUseCase

    init() {
        // Koin injection
        self.useCase = KoinHelper().getUsersUseCase()
    }

    func loadUsers() async {
        isLoading = true
        do {
            // Suspend функция → Swift async/await
            users = try await useCase.invoke()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }
}

// KoinHelper для Swift
// shared/src/iosMain/kotlin/di/KoinHelper.kt
class KoinHelper {
    fun getUsersUseCase(): GetUsersUseCase =
        KoinPlatform.getKoin().get()
}
```

## Шаг 5: Структура репозитория

### Вариант 1: Monorepo (рекомендуется)

```
my-app/
├── androidApp/           # Android приложение
│   ├── build.gradle.kts
│   └── src/
├── iosApp/               # iOS приложение (Xcode project)
│   ├── iosApp.xcodeproj
│   └── iosApp/
├── shared/               # KMP модуль
│   ├── build.gradle.kts
│   └── src/
│       ├── commonMain/
│       ├── androidMain/
│       └── iosMain/
├── settings.gradle.kts
├── build.gradle.kts
└── gradle.properties
```

### Вариант 2: Git Submodule

```
android-app/              # Android репо
├── app/
├── shared/  →  git submodule (kmp-shared)
└── settings.gradle.kts

ios-app/                  # iOS репо
├── iosApp/
├── shared/  →  git submodule (kmp-shared)
└── Podfile

kmp-shared/               # Отдельный репо
├── build.gradle.kts
└── src/
```

### Вариант 3: Remote Distribution

```
# Shared module публикуется как:
# - Maven artifact (для Android)
# - SPM package или CocoaPods pod (для iOS)

# Android
dependencies {
    implementation("com.example:shared:1.0.0")
}

# iOS (Podfile)
pod 'SharedKit', '~> 1.0.0'

# iOS (Package.swift)
.package(url: "https://github.com/example/shared-ios.git", from: "1.0.0")
```

## Чек-лист миграции

### Подготовка
- [ ] Изучить текущую архитектуру
- [ ] Определить слои для миграции
- [ ] Выбрать KMP-совместимые библиотеки
- [ ] Настроить shared модуль
- [ ] Выбрать структуру репозитория

### Model Layer
- [ ] Переместить data classes в commonMain
- [ ] Добавить @Serializable где нужно
- [ ] Обновить imports в Android

### Data Layer
- [ ] Retrofit → Ktor
- [ ] Room → SQLDelight (или Room KMP)
- [ ] SharedPreferences → multiplatform-settings
- [ ] Настроить expect/actual для платформ

### Domain Layer
- [ ] Переместить Use Cases
- [ ] Переместить Repository interfaces
- [ ] Обновить DI (Hilt → Koin)

### iOS Integration
- [ ] Настроить XCFramework сборку
- [ ] Интегрировать через CocoaPods/SPM
- [ ] Создать Swift wrappers для suspend функций
- [ ] Настроить Koin для iOS

### Testing
- [ ] Перенести unit тесты в commonTest
- [ ] Добавить platform-specific тесты
- [ ] Настроить CI для обеих платформ

## Замена библиотек

| Android | KMP Альтернатива | Заметки |
|---------|------------------|---------|
| Retrofit | Ktor Client | Полная совместимость |
| Room | SQLDelight / Room KMP | Room KMP stable в 2025 |
| Hilt/Dagger | Koin / kotlin-inject | Koin проще |
| Gson | kotlinx-serialization | Compile-time safety |
| SharedPreferences | multiplatform-settings | Drop-in replacement |
| Timber | Napier | Multiplatform logging |
| Glide/Coil | Coil 3.x | KMP поддержка |

## Типичные проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| Kotlin/Native freeze | Old memory model | Используй Kotlin 1.7.20+ |
| suspend в Swift | Не async/await | Используй SKIE или wrappers |
| iOS XCFramework большой | Все архитектуры | Билди только нужные targets |
| Room не видит entities | Не в commonMain | Используй Room KMP или SQLDelight |
| Koin не инициализирован | Забыли startKoin | Вызови в Application/AppDelegate |

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужно переписать всё сразу" | Strangler Fig: module за module |
| "iOS команда не примет Kotlin" | Swift остаётся для UI, только shared logic в KMP |
| "KMP требует монорепо" | Работает и с polyrepo через maven/SPM |
| "Миграция — это проект на год" | С модульной архитектурой — недели на module |
| "Compose Multiplatform обязателен" | UI может остаться нативным |

## CS-фундамент

| Концепция | Применение в миграции |
|-----------|----------------------|
| Strangler Fig Pattern | Постепенная замена legacy |
| Risk Management | Low-risk modules first |
| Modular Architecture | Prerequisite для миграции |
| Interface Segregation | Contracts между layers |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Add KMP to existing project](https://developer.android.com/kotlin/multiplatform/migrate) | Official | Google guide |
| [Migrating to KMP](https://proandroiddev.com/migrating-applications-to-kotlin-multiplatform-a-step-by-step-guide-47b365634924) | Blog | Step-by-step |
| [Convert Native to KMP](https://www.thedroidsonroids.com/blog/convert-native-project-to-kotlin-multiplatform-developers-guide) | Blog | Detailed guide |
| [KMP Shared Module Template](https://android-developers.googleblog.com/2025/05/kotlin-multiplatform-shared-module-templates.html) | Official | Android Studio |
| [Case Studies](https://kotlinlang.org/docs/multiplatform/case-studies.html) | Official | Real examples |

---
*Проверено: 2026-01-09 | KMP Stable, Android Studio Meerkat+*
