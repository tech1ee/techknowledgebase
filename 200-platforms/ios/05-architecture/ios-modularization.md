---
title: "Модуляризация iOS-приложений"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 58
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/architecture
  - type/deep-dive
  - level/advanced
related:
  - "[[android-modularization]]"
  - "[[ios-architecture-patterns]]"
prerequisites:
  - "[[ios-architecture-patterns]]"
  - "[[ios-xcode-fundamentals]]"
  - "[[ios-dependency-injection]]"
---

# iOS Модularизация

## TL;DR

Модульная архитектура iOS-приложений через Swift Package Manager (SPM) позволяет разделить монолитное приложение на независимые модули с явными границами. Это ускоряет сборку (благодаря инкрементальной компиляции), улучшает переиспользование кода, упрощает тестирование и масштабирование команды. Ключевые концепции: feature-модули, interface-модули для абстракций, core-модули для shared-логики, и правильная настройка зависимостей через Package.swift.

## Аналогии

**Модули как комнаты в доме**: Монолитное приложение — это студия, где всё в одном пространстве. Модульное — дом с отдельными комнатами (кухня, спальня, ванная). Каждая комната имеет дверь (public API), и вы не можете просто взять что-то из спальни, находясь на кухне — нужно пройти через дверь (импортировать модуль).

**SPM как IKEA**: Swift Package Manager — это как инструкция сборки мебели IKEA. Package.swift описывает, какие детали (модули) нужны, как они соединяются (зависимости), и что получится в итоге. Вы можете использовать готовые детали (remote packages) или сделать свои (local packages).

**Interface модули как контракты**: Interface-модуль — это как юридический контракт. Он определяет, ЧТО должно быть сделано (протоколы), но не КАК (реализация). Разные модули могут подписать этот контракт (имплементировать интерфейс), оставаясь независимыми.

## Диаграммы

### Архитектура многомодульного проекта

```
┌─────────────────────────────────────────────────────────────┐
│                        Main App                              │
│                    (App Target)                              │
└───────────┬─────────────────────────────────────┬───────────┘
            │                                     │
            ├─────────────┬──────────────────────┬┘
            │             │                      │
            ▼             ▼                      ▼
    ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
    │   Profile    │ │   Feed       │  │   Auth       │
    │   Feature    │ │   Feature    │  │   Feature    │
    └──────┬───────┘ └──────┬───────┘  └──────┬───────┘
           │                │                  │
           └────────┬───────┴──────────────────┘
                    │
                    ▼
           ┌────────────────┐
           │   CoreKit      │
           │ (Networking,   │
           │  Storage, etc) │
           └────────┬───────┘
                    │
                    ▼
           ┌────────────────┐
           │  DesignSystem  │
           │ (UI Components)│
           └────────────────┘
```

### Зависимости с Interface модулями

```
┌──────────────────┐
│   ProfileFeature │
│  (Implementation)│
└────────┬─────────┘
         │ implements
         ▼
┌──────────────────┐     ┌──────────────────┐
│ProfileFeatureAPI │◄────│   FeedFeature    │
│   (Interface)    │     │                  │
└──────────────────┘     └──────────────────┘
         ▲
         │ depends on
         │
    (dependency injection)
```

### Уровни модульной архитектуры

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: App Layer                                  │
│ - App target (entry point)                          │
│ - Dependency injection container                    │
│ - App-level configuration                           │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│ Layer 3: Feature Layer                              │
│ - ProfileFeature, FeedFeature, AuthFeature          │
│ - Feature-specific UI and business logic            │
│ - Can depend on Interface and Core modules          │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│ Layer 2: Interface Layer                            │
│ - Protocols and data models                         │
│ - No implementations                                │
│ - Defines contracts between features                │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│ Layer 1: Core Layer                                 │
│ - CoreKit (Networking, Storage, Analytics)          │
│ - DesignSystem (UI Components)                      │
│ - Extensions, Utilities                             │
└─────────────────────────────────────────────────────┘
```

## Почему модульризация важна

### Проблемы монолитной архитектуры

В монолитном iOS-приложении весь код находится в одном таргете. По мере роста проекта возникают проблемы:

1. **Медленная сборка**: Xcode пересобирает весь проект даже при изменении одного файла
2. **Tight coupling**: Классы и модули слишком сильно связаны, изменения в одном месте ломают другое
3. **Сложное масштабирование команды**: Разработчики конфликтуют в одних и тех же файлах
4. **Невозможность переиспользования**: Логика привязана к конкретному приложению
5. **Проблемы с тестированием**: Сложно изолировать и тестировать отдельные компоненты

### Преимущества модульной архитектуры

1. **Инкрементальная компиляция**: SPM кэширует скомпилированные модули, пересобирая только изменённые
2. **Явные зависимости**: Package.swift явно описывает, какой модуль от чего зависит
3. **Изоляция кода**: Модули видят только public API друг друга
4. **Параллельная разработка**: Команды работают над разными модулями независимо
5. **Переиспользование**: Модули можно использовать в разных проектах (iOS app, widgets, extensions)
6. **Лучшее тестирование**: Каждый модуль тестируется изолированно

## Swift Package Manager модули

### Локальные пакеты (Local Packages)

Локальные пакеты находятся в структуре вашего проекта и разрабатываются вместе с приложением.

**Структура проекта с локальными пакетами:**

```
MyApp/
├── MyApp.xcodeproj
├── MyApp/
│   ├── AppDelegate.swift
│   └── SceneDelegate.swift
├── Packages/
│   ├── Features/
│   │   ├── ProfileFeature/
│   │   │   ├── Package.swift
│   │   │   └── Sources/
│   │   │       └── ProfileFeature/
│   │   │           ├── ProfileView.swift
│   │   │           └── ProfileViewModel.swift
│   │   └── FeedFeature/
│   │       ├── Package.swift
│   │       └── Sources/
│   └── Core/
│       ├── CoreKit/
│       │   ├── Package.swift
│       │   └── Sources/
│       │       └── CoreKit/
│       │           ├── Networking/
│       │           └── Storage/
│       └── DesignSystem/
│           ├── Package.swift
│           └── Sources/
```

**Пример Package.swift для локального модуля:**

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ProfileFeature",
    platforms: [.iOS(.v17)],
    products: [
        .library(
            name: "ProfileFeature",
            targets: ["ProfileFeature"]
        )
    ],
    dependencies: [
        // Зависимость от другого локального модуля
        .package(path: "../../Core/CoreKit"),
        .package(path: "../../Core/DesignSystem")
    ],
    targets: [
        .target(
            name: "ProfileFeature",
            dependencies: [
                .product(name: "CoreKit", package: "CoreKit"),
                .product(name: "DesignSystem", package: "DesignSystem")
            ]
        ),
        .testTarget(
            name: "ProfileFeatureTests",
            dependencies: ["ProfileFeature"]
        )
    ]
)
```

### Удалённые пакеты (Remote Packages)

Удалённые пакеты подключаются через Git URL и версионируются.

**Пример использования remote packages:**

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "CoreKit",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "CoreKit", targets: ["CoreKit"])
    ],
    dependencies: [
        // Подключение популярных библиотек
        .package(
            url: "https://github.com/Alamofire/Alamofire.git",
            from: "5.8.0"
        ),
        .package(
            url: "https://github.com/realm/SwiftLint.git",
            from: "0.54.0"
        )
    ],
    targets: [
        .target(
            name: "CoreKit",
            dependencies: [
                .product(name: "Alamofire", package: "Alamofire")
            ]
        )
    ]
)
```

## Архитектура Feature-модулей

Feature-модуль инкапсулирует всю логику одной функциональности приложения: UI, бизнес-логику, модели данных.

### Структура feature-модуля

```
ProfileFeature/
├── Package.swift
├── Sources/
│   └── ProfileFeature/
│       ├── Views/
│       │   ├── ProfileView.swift
│       │   ├── ProfileEditView.swift
│       │   └── Components/
│       │       └── ProfileHeaderView.swift
│       ├── ViewModels/
│       │   ├── ProfileViewModel.swift
│       │   └── ProfileEditViewModel.swift
│       ├── Models/
│       │   ├── UserProfile.swift
│       │   └── ProfileSettings.swift
│       ├── Services/
│       │   └── ProfileService.swift
│       └── ProfileFeature.swift (public API)
└── Tests/
    └── ProfileFeatureTests/
        ├── ViewModelTests.swift
        └── ServiceTests.swift
```

### Пример feature-модуля

```swift
// ProfileFeature/Sources/ProfileFeature/ProfileFeature.swift
import SwiftUI
import CoreKit
import DesignSystem

// Public API модуля
public struct ProfileFeature {
    public init() {}

    public func makeProfileView(userID: String) -> some View {
        ProfileView(viewModel: ProfileViewModel(
            userID: userID,
            profileService: ProfileService()
        ))
    }
}

// ProfileFeature/Sources/ProfileFeature/Views/ProfileView.swift
import SwiftUI
import DesignSystem

struct ProfileView: View {
    @StateObject var viewModel: ProfileViewModel

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                ProfileHeaderView(profile: viewModel.profile)

                DSButton(title: "Edit Profile") {
                    viewModel.showEditProfile()
                }
            }
            .padding()
        }
        .navigationTitle("Profile")
        .task {
            await viewModel.loadProfile()
        }
    }
}

// ProfileFeature/Sources/ProfileFeature/ViewModels/ProfileViewModel.swift
import Foundation
import CoreKit

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserProfile?
    @Published var isLoading = false

    private let userID: String
    private let profileService: ProfileServiceProtocol

    init(userID: String, profileService: ProfileServiceProtocol) {
        self.userID = userID
        self.profileService = profileService
    }

    func loadProfile() async {
        isLoading = true
        defer { isLoading = false }

        do {
            profile = try await profileService.fetchProfile(userID: userID)
        } catch {
            // Handle error
        }
    }

    func showEditProfile() {
        // Navigation logic
    }
}
```

## Interface (API) модули

Interface-модули содержат только протоколы и data models без реализации. Это позволяет разорвать циклические зависимости между feature-модулями.

### Зачем нужны Interface модули

**Проблема**: FeedFeature хочет показать профиль пользователя, а ProfileFeature — ленту пользователя. Возникает циклическая зависимость.

**Решение**: Создать ProfileFeatureAPI с протоколом, который реализует ProfileFeature, а FeedFeature зависит только от API.

### Структура Interface модуля

```
ProfileFeatureAPI/
├── Package.swift
└── Sources/
    └── ProfileFeatureAPI/
        ├── ProfileServiceProtocol.swift
        ├── ProfileCoordinatorProtocol.swift
        └── Models/
            ├── UserProfile.swift
            └── ProfileSettings.swift
```

### Пример Interface модуля

```swift
// ProfileFeatureAPI/Sources/ProfileFeatureAPI/ProfileServiceProtocol.swift
import Foundation

public protocol ProfileServiceProtocol {
    func fetchProfile(userID: String) async throws -> UserProfile
    func updateProfile(_ profile: UserProfile) async throws
}

// ProfileFeatureAPI/Sources/ProfileFeatureAPI/Models/UserProfile.swift
import Foundation

public struct UserProfile: Identifiable, Codable {
    public let id: String
    public let username: String
    public let avatarURL: URL?
    public let bio: String?

    public init(
        id: String,
        username: String,
        avatarURL: URL? = nil,
        bio: String? = nil
    ) {
        self.id = id
        self.username = username
        self.avatarURL = avatarURL
        self.bio = bio
    }
}

// ProfileFeatureAPI/Sources/ProfileFeatureAPI/ProfileCoordinatorProtocol.swift
import SwiftUI

public protocol ProfileCoordinatorProtocol {
    func showProfile(userID: String)
    func showEditProfile()
}
```

**ProfileFeature реализует интерфейс:**

```swift
// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI")
]

// ProfileFeature/Sources/ProfileFeature/Services/ProfileService.swift
import Foundation
import ProfileFeatureAPI
import CoreKit

final class ProfileService: ProfileServiceProtocol {
    private let networkService: NetworkServiceProtocol

    init(networkService: NetworkServiceProtocol = NetworkService.shared) {
        self.networkService = networkService
    }

    func fetchProfile(userID: String) async throws -> UserProfile {
        try await networkService.request(
            endpoint: ProfileEndpoint.getProfile(userID: userID)
        )
    }

    func updateProfile(_ profile: UserProfile) async throws {
        try await networkService.request(
            endpoint: ProfileEndpoint.updateProfile(profile)
        )
    }
}
```

**FeedFeature зависит только от API:**

```swift
// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI") // Только API!
]

// FeedFeature/Sources/FeedFeature/Views/FeedItemView.swift
import SwiftUI
import ProfileFeatureAPI

struct FeedItemView: View {
    let item: FeedItem
    let profileCoordinator: ProfileCoordinatorProtocol

    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(item.author.username)
                    .font(.headline)
                Spacer()
            }
            .contentShape(Rectangle())
            .onTapGesture {
                // Переход на профиль через протокол
                profileCoordinator.showProfile(userID: item.author.id)
            }

            Text(item.content)
        }
    }
}
```

## Core и Shared модули

### CoreKit - инфраструктурный модуль

CoreKit содержит общую инфраструктуру: networking, storage, analytics, utilities.

```
CoreKit/
├── Package.swift
└── Sources/
    └── CoreKit/
        ├── Networking/
        │   ├── NetworkService.swift
        │   ├── NetworkServiceProtocol.swift
        │   ├── HTTPMethod.swift
        │   ├── Endpoint.swift
        │   └── NetworkError.swift
        ├── Storage/
        │   ├── KeychainService.swift
        │   ├── UserDefaultsService.swift
        │   └── CoreDataStack.swift
        ├── Analytics/
        │   ├── AnalyticsService.swift
        │   └── AnalyticsEvent.swift
        └── Extensions/
            ├── String+Extensions.swift
            └── Date+Extensions.swift
```

**Пример NetworkService:**

```swift
// CoreKit/Sources/CoreKit/Networking/NetworkServiceProtocol.swift
import Foundation

public protocol NetworkServiceProtocol {
    func request<T: Decodable>(endpoint: Endpoint) async throws -> T
}

// CoreKit/Sources/CoreKit/Networking/NetworkService.swift
import Foundation

public final class NetworkService: NetworkServiceProtocol {
    public static let shared = NetworkService()

    private let session: URLSession
    private let decoder = JSONDecoder()

    public init(session: URLSession = .shared) {
        self.session = session
    }

    public func request<T: Decodable>(endpoint: Endpoint) async throws -> T {
        let request = try endpoint.asURLRequest()
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode)
        }

        return try decoder.decode(T.self, from: data)
    }
}
```

### DesignSystem - UI компоненты

DesignSystem модуль содержит переиспользуемые UI компоненты, цвета, шрифты, стили.

```
DesignSystem/
├── Package.swift
└── Sources/
    └── DesignSystem/
        ├── Theme/
        │   ├── Colors.swift
        │   ├── Typography.swift
        │   └── Spacing.swift
        ├── Components/
        │   ├── DSButton.swift
        │   ├── DSTextField.swift
        │   ├── DSCard.swift
        │   └── DSLoadingView.swift
        └── Modifiers/
            ├── CardModifier.swift
            └── ShimmerModifier.swift
```

**Пример DesignSystem компонента:**

```swift
// DesignSystem/Sources/DesignSystem/Theme/Colors.swift
import SwiftUI

public enum DSColors {
    public static let primary = Color("Primary", bundle: .module)
    public static let secondary = Color("Secondary", bundle: .module)
    public static let background = Color("Background", bundle: .module)
    public static let text = Color("Text", bundle: .module)
}

// DesignSystem/Sources/DesignSystem/Components/DSButton.swift
import SwiftUI

public struct DSButton: View {
    public enum Style {
        case primary
        case secondary
        case text
    }

    let title: String
    let style: Style
    let action: () -> Void

    public init(
        title: String,
        style: Style = .primary,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.style = style
        self.action = action
    }

    public var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(foregroundColor)
                .frame(maxWidth: .infinity)
                .padding()
                .background(backgroundColor)
                .cornerRadius(12)
        }
    }

    private var backgroundColor: Color {
        switch style {
        case .primary: return DSColors.primary
        case .secondary: return DSColors.secondary
        case .text: return .clear
        }
    }

    private var foregroundColor: Color {
        switch style {
        case .primary, .secondary: return .white
        case .text: return DSColors.primary
        }
    }
}
```

## Зависимости модулей и видимость

### Access Control уровни

```swift
// internal (по умолчанию) - виден только внутри модуля
class InternalViewModel { }

// public - виден в других модулях, но нельзя наследовать/переопределять
public class PublicService { }

// open - можно наследовать и переопределять в других модулях
open class OpenBaseViewModel { }

// private - виден только в файле
private func helperFunction() { }

// fileprivate - виден в файле
fileprivate struct Configuration { }
```

### Правила зависимостей модулей

**Хорошая архитектура зависимостей:**

```
App → Features → Interfaces → Core
```

1. **App зависит от Feature модулей** - собирает приложение
2. **Feature модули зависят от Interface и Core** - используют общие API
3. **Interface модули независимы или зависят от Core** - только протоколы
4. **Core модули независимы** - базовая инфраструктура

**Запрещённые зависимости:**

```
❌ Feature → Feature (прямая зависимость между фичами)
❌ Core → Feature (обратная зависимость)
❌ Interface → Feature (интерфейс не должен знать о реализации)
```

### Граф зависимостей проекта

```swift
// App/Package.swift
dependencies: [
    .package(path: "./Packages/Features/ProfileFeature"),
    .package(path: "./Packages/Features/FeedFeature"),
    .package(path: "./Packages/Features/AuthFeature")
]

// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI"),
    .package(path: "../../Core/CoreKit"),
    .package(path: "../../Core/DesignSystem")
]

// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI"), // Только API!
    .package(path: "../../Core/CoreKit"),
    .package(path: "../../Core/DesignSystem")
]

// ProfileFeatureAPI/Package.swift
dependencies: [
    // Только Foundation, никаких других модулей
]

// CoreKit/Package.swift
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0")
]

// DesignSystem/Package.swift
dependencies: [
    // Только SwiftUI/UIKit
]
```

## Конфигурация Package.swift

### Полный пример Package.swift

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    // 1. Имя пакета
    name: "ProfileFeature",

    // 2. Поддерживаемые платформы
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
        .watchOS(.v10)
    ],

    // 3. Products - что экспортирует этот пакет
    products: [
        .library(
            name: "ProfileFeature",
            targets: ["ProfileFeature"]
        )
    ],

    // 4. Зависимости от других пакетов
    dependencies: [
        // Локальный пакет
        .package(path: "../ProfileFeatureAPI"),
        .package(path: "../../Core/CoreKit"),

        // Удалённый пакет с версией
        .package(
            url: "https://github.com/Alamofire/Alamofire.git",
            from: "5.8.0"
        ),

        // Точная версия
        .package(
            url: "https://github.com/realm/SwiftLint.git",
            exact: "0.54.0"
        ),

        // Диапазон версий
        .package(
            url: "https://github.com/apple/swift-collections.git",
            "1.0.0"..<"2.0.0"
        ),

        // Ветка
        .package(
            url: "https://github.com/pointfreeco/swift-composable-architecture",
            branch: "main"
        )
    ],

    // 5. Targets - модули кода
    targets: [
        // Основной target
        .target(
            name: "ProfileFeature",
            dependencies: [
                // Зависимость от другого target в этом пакете
                "ProfileFeatureAPI",

                // Зависимость от product другого пакета
                .product(name: "CoreKit", package: "CoreKit"),
                .product(name: "Alamofire", package: "Alamofire")
            ],
            // Путь к исходникам (опционально)
            path: "Sources/ProfileFeature",
            // Ресурсы (изображения, JSON и т.д.)
            resources: [
                .process("Resources")
            ],
            // Swift settings
            swiftSettings: [
                .enableUpcomingFeature("BareSlashRegexLiterals"),
                .define("DEBUG", .when(configuration: .debug))
            ]
        ),

        // Test target
        .testTarget(
            name: "ProfileFeatureTests",
            dependencies: ["ProfileFeature"],
            path: "Tests/ProfileFeatureTests"
        )
    ]
)
```

### Управление версиями зависимостей

```swift
// Semantic versioning
.package(url: "...", from: "1.0.0")           // >= 1.0.0, < 2.0.0
.package(url: "...", "1.0.0"..<"2.0.0")       // [1.0.0, 2.0.0)
.package(url: "...", "1.0.0"..."1.5.0")       // [1.0.0, 1.5.0]
.package(url: "...", exact: "1.2.3")          // Точно 1.2.3

// Branch/commit
.package(url: "...", branch: "develop")       // Конкретная ветка
.package(url: "...", revision: "abc123")      // Конкретный commit
```

## Границы модулей и Access Control

### Правильное использование public API

```swift
// ❌ ПЛОХО: Всё public
public class ProfileViewModel {
    public var profile: UserProfile?
    public var internalState: String? // Внутренняя деталь не должна быть public

    public func loadProfile() async { }
    public func helperMethod() { } // Helper не должен быть public
}

// ✅ ХОРОШО: Только необходимый API
public class ProfileViewModel {
    // Public - доступно снаружи
    public private(set) var profile: UserProfile?

    // Internal - видно только внутри модуля
    var internalState: String?

    public init() { }

    public func loadProfile() async { }

    // Private - только в этом файле
    private func helperMethod() { }
}
```

### Создание чистого API модуля

```swift
// ProfileFeature/Sources/ProfileFeature/ProfileFeature.swift
// Это единственная точка входа в модуль

import SwiftUI

/// Public фасад для ProfileFeature модуля
public struct ProfileFeature {
    public init() {}

    /// Создаёт view профиля пользователя
    public func makeProfileView(
        userID: String,
        coordinator: ProfileCoordinatorProtocol
    ) -> some View {
        ProfileView(
            viewModel: makeViewModel(userID: userID),
            coordinator: coordinator
        )
    }

    /// Создаёт сервис профиля (для dependency injection)
    public func makeProfileService() -> ProfileServiceProtocol {
        ProfileService()
    }

    // Internal factory methods
    func makeViewModel(userID: String) -> ProfileViewModel {
        ProfileViewModel(
            userID: userID,
            profileService: ProfileService()
        )
    }
}

// Остальные классы (ProfileView, ProfileViewModel) internal
```

### @_exported import для упрощения API

```swift
// ProfileFeature/Sources/ProfileFeature/ProfileFeature.swift

// Реэкспортируем API модуль, чтобы клиенты не импортировали оба
@_exported import ProfileFeatureAPI

public struct ProfileFeature {
    // ...
}

// Теперь клиенту достаточно:
import ProfileFeature // Автоматически получает и ProfileFeatureAPI
```

## Оптимизация времени сборки

### Как модули ускоряют сборку

1. **Инкрементальная компиляция**: SPM кэширует скомпилированные модули
2. **Параллельная сборка**: Независимые модули компилируются параллельно
3. **Избежание ре-компиляции**: Изменение в одном модуле не пересобирает другие

### Стратегии оптимизации

**1. Мелкие, сфокусированные модули**

```swift
// ❌ ПЛОХО: Один огромный модуль
CoreKit (1000+ файлов)

// ✅ ХОРОШО: Несколько маленьких модулей
CoreNetworking (50 файлов)
CoreStorage (30 файлов)
CoreAnalytics (20 файлов)
CoreUtilities (40 файлов)
```

**2. Минимизация зависимостей**

```swift
// ❌ ПЛОХО: ProfileFeature зависит от всего CoreKit
dependencies: [
    .package(path: "../../Core/CoreKit") // Огромный модуль
]

// ✅ ХОРОШО: Зависит только от нужных подмодулей
dependencies: [
    .package(path: "../../Core/CoreNetworking"),
    .package(path: "../../Core/CoreStorage")
]
```

**3. Использование Binary Frameworks для больших зависимостей**

```swift
// Package.swift
targets: [
    .binaryTarget(
        name: "GoogleMaps",
        path: "./Frameworks/GoogleMaps.xcframework"
    )
]
```

**4. Избегание циклических зависимостей**

```swift
// ❌ ПЛОХО: Циклическая зависимость
ProfileFeature → FeedFeature → ProfileFeature

// ✅ ХОРОШО: Через Interface модуль
ProfileFeature → ProfileFeatureAPI ← FeedFeature
```

### Измерение времени сборки

```bash
# Включить подробную статистику компиляции
xcodebuild -showBuildTimingSummary

# Анализ времени сборки каждого файла
xcodebuild -destination 'platform=iOS Simulator,name=iPhone 15' \
  -enableAddressSanitizer NO \
  -enableThreadSanitizer NO \
  -enableUndefinedBehaviorSanitizer NO \
  OTHER_SWIFT_FLAGS="-Xfrontend -debug-time-function-bodies"
```

## Micro-features архитектура

Micro-features — это подход, где каждая маленькая функциональность выделена в отдельный модуль.

### Принципы micro-features

1. **Один модуль = одна функциональность**
2. **Feature + Feature API + Feature Tests**
3. **Полная изоляция и независимость**
4. **Легко добавлять/удалять фичи**

### Пример структуры micro-features

```
Packages/
├── Features/
│   ├── Auth/
│   │   ├── AuthFeature/
│   │   ├── AuthFeatureAPI/
│   │   └── AuthFeatureTests/
│   ├── Profile/
│   │   ├── ProfileFeature/
│   │   ├── ProfileFeatureAPI/
│   │   └── ProfileFeatureTests/
│   ├── Feed/
│   │   ├── FeedFeature/
│   │   ├── FeedFeatureAPI/
│   │   └── FeedFeatureTests/
│   ├── Posts/
│   │   ├── PostCreation/
│   │   │   ├── PostCreationFeature/
│   │   │   └── PostCreationFeatureAPI/
│   │   ├── PostDetails/
│   │   │   ├── PostDetailsFeature/
│   │   │   └── PostDetailsFeatureAPI/
│   │   └── PostList/
│   │       ├── PostListFeature/
│   │       └── PostListFeatureAPI/
│   └── Settings/
│       ├── SettingsFeature/
│       ├── SettingsFeatureAPI/
│       └── SettingsFeatureTests/
└── Core/
    ├── CoreNetworking/
    ├── CoreStorage/
    ├── CoreAnalytics/
    └── DesignSystem/
```

### Feature Flags для micro-features

```swift
// FeatureFlags/Sources/FeatureFlags/FeatureFlags.swift
public struct FeatureFlags {
    public static var isProfileFeatureEnabled = true
    public static var isNewFeedEnabled = false
    public static var isPostCreationEnabled = true
}

// App/AppView.swift
import SwiftUI
import FeatureFlags
import ProfileFeature
import FeedFeature

struct AppView: View {
    var body: some View {
        TabView {
            if FeatureFlags.isNewFeedEnabled {
                FeedView()
                    .tabItem { Label("Feed", systemImage: "house") }
            }

            if FeatureFlags.isProfileFeatureEnabled {
                ProfileView()
                    .tabItem { Label("Profile", systemImage: "person") }
            }
        }
    }
}
```

### Coordinator для навигации между micro-features

```swift
// Navigation/Sources/Navigation/AppCoordinator.swift
import SwiftUI
import ProfileFeatureAPI
import FeedFeatureAPI
import PostCreationFeatureAPI

@MainActor
public final class AppCoordinator: ObservableObject {
    @Published public var navigationPath = NavigationPath()

    private let profileFeature: ProfileFeature
    private let feedFeature: FeedFeature
    private let postCreationFeature: PostCreationFeature

    public init() {
        self.profileFeature = ProfileFeature()
        self.feedFeature = FeedFeature()
        self.postCreationFeature = PostCreationFeature()
    }

    // MARK: - Navigation Methods

    public func showProfile(userID: String) {
        let view = profileFeature.makeProfileView(userID: userID, coordinator: self)
        navigationPath.append(view)
    }

    public func showPostCreation() {
        let view = postCreationFeature.makePostCreationView(coordinator: self)
        navigationPath.append(view)
    }

    public func pop() {
        if !navigationPath.isEmpty {
            navigationPath.removeLast()
        }
    }
}

// App/AppView.swift
struct AppView: View {
    @StateObject private var coordinator = AppCoordinator()

    var body: some View {
        NavigationStack(path: $coordinator.navigationPath) {
            ContentView()
                .navigationDestination(for: ???) { view in
                    view
                }
        }
        .environmentObject(coordinator)
    }
}
```

## Практические примеры структуры проектов

### Пример 1: Маленькое приложение (1-3 фичи)

```
MyApp/
├── MyApp.xcodeproj
├── MyApp/
│   ├── MyAppApp.swift
│   └── ContentView.swift
└── Packages/
    ├── Features/
    │   └── MainFeature/
    │       ├── Package.swift
    │       └── Sources/MainFeature/
    └── Core/
        ├── CoreKit/
        │   ├── Package.swift
        │   └── Sources/CoreKit/
        └── DesignSystem/
            ├── Package.swift
            └── Sources/DesignSystem/
```

### Пример 2: Среднее приложение (5-10 фич)

```
MyApp/
├── MyApp.xcodeproj
├── MyApp/
│   ├── MyAppApp.swift
│   ├── DependencyContainer.swift
│   └── AppCoordinator.swift
└── Packages/
    ├── Features/
    │   ├── Auth/
    │   │   ├── AuthFeature/
    │   │   └── AuthFeatureAPI/
    │   ├── Profile/
    │   │   ├── ProfileFeature/
    │   │   └── ProfileFeatureAPI/
    │   ├── Feed/
    │   │   ├── FeedFeature/
    │   │   └── FeedFeatureAPI/
    │   ├── Search/
    │   │   ├── SearchFeature/
    │   │   └── SearchFeatureAPI/
    │   └── Settings/
    │       ├── SettingsFeature/
    │       └── SettingsFeatureAPI/
    ├── Core/
    │   ├── CoreNetworking/
    │   ├── CoreStorage/
    │   ├── CoreAnalytics/
    │   └── DesignSystem/
    └── Shared/
        ├── Models/
        └── Extensions/
```

### Пример 3: Большое приложение (20+ фич, несколько команд)

```
MyApp/
├── MyApp.xcodeproj
├── MyApp/
│   ├── MyAppApp.swift
│   ├── AppDelegate.swift
│   ├── DI/
│   │   ├── AppContainer.swift
│   │   └── FeatureFactory.swift
│   └── Navigation/
│       └── AppCoordinator.swift
└── Packages/
    ├── Features/
    │   ├── Authentication/
    │   │   ├── Login/
    │   │   │   ├── LoginFeature/
    │   │   │   ├── LoginFeatureAPI/
    │   │   │   └── LoginFeatureTests/
    │   │   ├── Registration/
    │   │   │   ├── RegistrationFeature/
    │   │   │   └── RegistrationFeatureAPI/
    │   │   └── PasswordRecovery/
    │   │       ├── PasswordRecoveryFeature/
    │   │       └── PasswordRecoveryFeatureAPI/
    │   ├── Profile/
    │   │   ├── ProfileView/
    │   │   ├── ProfileEdit/
    │   │   └── ProfileSettings/
    │   ├── Feed/
    │   │   ├── FeedList/
    │   │   ├── FeedFilters/
    │   │   └── FeedSearch/
    │   ├── Posts/
    │   │   ├── PostCreation/
    │   │   ├── PostDetails/
    │   │   ├── PostEditing/
    │   │   └── PostSharing/
    │   ├── Messaging/
    │   │   ├── ChatList/
    │   │   ├── ChatConversation/
    │   │   └── ChatSettings/
    │   ├── Notifications/
    │   │   ├── NotificationsList/
    │   │   └── NotificationSettings/
    │   └── Settings/
    │       ├── GeneralSettings/
    │       ├── PrivacySettings/
    │       └── AppearanceSettings/
    ├── Core/
    │   ├── Networking/
    │   │   ├── CoreNetworking/
    │   │   └── CoreNetworkingMocks/
    │   ├── Storage/
    │   │   ├── CoreStorage/
    │   │   ├── CoreDataStack/
    │   │   └── KeychainWrapper/
    │   ├── Analytics/
    │   │   ├── CoreAnalytics/
    │   │   └── AnalyticsEvents/
    │   ├── Infrastructure/
    │   │   ├── Logging/
    │   │   ├── FeatureFlags/
    │   │   └── Configuration/
    │   └── Platform/
    │       ├── Permissions/
    │       └── DeviceInfo/
    ├── UI/
    │   ├── DesignSystem/
    │   ├── CommonViews/
    │   └── Resources/
    └── Shared/
        ├── Models/
        ├── Extensions/
        └── Utilities/
```

### Dependency Injection контейнер

```swift
// MyApp/DI/AppContainer.swift
import Foundation
import ProfileFeature
import ProfileFeatureAPI
import FeedFeature
import FeedFeatureAPI
import CoreNetworking
import CoreStorage
import CoreAnalytics

final class AppContainer {
    // MARK: - Singletons

    lazy var networkService: NetworkServiceProtocol = {
        NetworkService()
    }()

    lazy var storageService: StorageServiceProtocol = {
        StorageService()
    }()

    lazy var analyticsService: AnalyticsServiceProtocol = {
        AnalyticsService()
    }()

    // MARK: - Feature Factories

    func makeProfileFeature() -> ProfileFeature {
        ProfileFeature(
            networkService: networkService,
            storageService: storageService,
            analyticsService: analyticsService
        )
    }

    func makeFeedFeature() -> FeedFeature {
        FeedFeature(
            networkService: networkService,
            analyticsService: analyticsService
        )
    }
}

// MyApp/MyAppApp.swift
import SwiftUI

@main
struct MyAppApp: App {
    private let container = AppContainer()
    @StateObject private var coordinator: AppCoordinator

    init() {
        let coordinator = AppCoordinator(
            profileFeature: container.makeProfileFeature(),
            feedFeature: container.makeFeedFeature()
        )
        _coordinator = StateObject(wrappedValue: coordinator)
    }

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $coordinator.navigationPath) {
                ContentView()
            }
            .environmentObject(coordinator)
        }
    }
}
```

## 6 типичных ошибок модульризации

### ❌ 1. Циклические зависимости между модулями

```swift
// ❌ ПЛОХО: ProfileFeature и FeedFeature зависят друг от друга
// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../FeedFeature") // ProfileFeature → FeedFeature
]

// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeature") // FeedFeature → ProfileFeature
]

// РЕЗУЛЬТАТ: Компиляция невозможна
```

```swift
// ✅ ХОРОШО: Используем Interface модуль
// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI")
]

// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI") // Оба зависят от API
]

// ProfileFeatureAPI/Package.swift
dependencies: [] // Никаких зависимостей
```

### ❌ 2. Слишком крупные модули (God Module)

```swift
// ❌ ПЛОХО: Один огромный модуль со всем
CoreKit/
├── Networking/
│   ├── (50 файлов)
├── Storage/
│   ├── (40 файлов)
├── Analytics/
│   ├── (30 файлов)
├── UI/
│   ├── (100 файлов)
└── Utils/
    └── (200 файлов)

// Любое изменение в любом файле пересобирает весь CoreKit
// Feature модуль зависит от CoreKit целиком, даже если нужен только Networking
```

```swift
// ✅ ХОРОШО: Разделение на маленькие модули
Core/
├── CoreNetworking/
│   └── Sources/ (50 файлов)
├── CoreStorage/
│   └── Sources/ (40 файлов)
├── CoreAnalytics/
│   └── Sources/ (30 файлов)
├── DesignSystem/
│   └── Sources/ (100 файлов)
└── CoreUtilities/
    └── Sources/ (200 файлов)

// Feature модули зависят только от нужных подмодулей
// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../../Core/CoreNetworking"),
    .package(path: "../../Core/CoreStorage")
    // Не зависит от Analytics, UI, Utils
]
```

### ❌ 3. Утечка внутренних деталей через public API

```swift
// ❌ ПЛОХО: Внутренние детали торчат наружу
// ProfileFeature/Sources/ProfileFeature/ProfileViewModel.swift
public class ProfileViewModel: ObservableObject {
    public var profile: UserProfile?

    // Внутренняя деталь реализации не должна быть public
    public var cacheManager: CacheManager?
    public var networkTask: Task<Void, Never>?

    // Helper-метод не должен быть public
    public func updateInternalState() { }
}

// Клиентский код начинает зависеть от внутренностей
let viewModel = ProfileViewModel()
viewModel.cacheManager?.clearCache() // Tight coupling!
```

```swift
// ✅ ХОРОШО: Минимальный public API
// ProfileFeature/Sources/ProfileFeature/ProfileViewModel.swift
public class ProfileViewModel: ObservableObject {
    // Public read-only
    public private(set) var profile: UserProfile?

    // Internal детали
    var cacheManager: CacheManager?
    var networkTask: Task<Void, Never>?

    public init() { }

    // Только публичные методы
    public func loadProfile() async { }

    // Private helpers
    private func updateInternalState() { }
}

// Ещё лучше: Фасад модуля
// ProfileFeature/Sources/ProfileFeature/ProfileFeature.swift
public struct ProfileFeature {
    public init() {}

    public func makeProfileView(userID: String) -> some View {
        // ViewModel internal, снаружи не виден
        ProfileView(viewModel: ProfileViewModel(userID: userID))
    }
}
```

### ❌ 4. Прямые зависимости между Feature модулями

```swift
// ❌ ПЛОХО: FeedFeature напрямую зависит от ProfileFeature
// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeature")
]

// FeedFeature/Sources/FeedFeature/FeedItemView.swift
import ProfileFeature

struct FeedItemView: View {
    var body: some View {
        // Прямой вызов из другой фичи
        ProfileView(userID: "123")
    }
}

// ПРОБЛЕМЫ:
// 1. Нельзя собрать FeedFeature без ProfileFeature
// 2. Нельзя заменить реализацию ProfileFeature
// 3. Сложно тестировать FeedFeature изолированно
```

```swift
// ✅ ХОРОШО: Зависимость только от интерфейса + DI
// FeedFeature/Package.swift
dependencies: [
    .package(path: "../ProfileFeatureAPI") // Только API!
]

// FeedFeature/Sources/FeedFeature/FeedItemView.swift
import ProfileFeatureAPI

struct FeedItemView: View {
    let profileCoordinator: ProfileCoordinatorProtocol

    var body: some View {
        Button("Show Profile") {
            // Через протокол
            profileCoordinator.showProfile(userID: "123")
        }
    }
}

// FeedFeature собирается независимо
// В тестах легко подставить mock
class MockProfileCoordinator: ProfileCoordinatorProtocol {
    var shownUserID: String?
    func showProfile(userID: String) {
        shownUserID = userID
    }
}
```

### ❌ 5. Отсутствие versioning для shared модулей

```swift
// ❌ ПЛОХО: Все фичи зависят от CoreKit напрямую без версии
// ProfileFeature/Package.swift
dependencies: [
    .package(path: "../../Core/CoreKit") // Всегда последняя версия
]

// ПРОБЛЕМА: Изменение CoreKit ломает все фичи сразу
// CoreKit/Sources/CoreKit/NetworkService.swift
public class NetworkService {
    // Изменили сигнатуру метода
    public func request<T>(_ endpoint: Endpoint) async throws -> T {
        // Новая реализация
    }
}

// Теперь 20 feature-модулей не компилируются!
```

```swift
// ✅ ХОРОШО: Версионирование через git tags
// 1. CoreKit в отдельном репозитории с тегами v1.0.0, v1.1.0, etc.

// ProfileFeature/Package.swift
dependencies: [
    .package(
        url: "https://github.com/company/CoreKit.git",
        from: "1.0.0" // Конкретная версия
    )
]

// FeedFeature/Package.swift (может использовать другую версию)
dependencies: [
    .package(
        url: "https://github.com/company/CoreKit.git",
        from: "1.1.0"
    )
]

// Миграция на новую версию постепенная, не все сразу
```

### ❌ 6. Игнорирование dependency graph при добавлении зависимостей

```swift
// ❌ ПЛОХО: Бездумное добавление зависимостей
// DesignSystem/Package.swift
dependencies: [
    .package(path: "../CoreNetworking"), // Зачем UI-компонентам networking?
    .package(path: "../CoreAnalytics"),  // Зачем UI-компонентам analytics?
    .package(path: "../../Features/ProfileFeature") // UI зависит от фичи!
]

// ПРОБЛЕМЫ:
// 1. DesignSystem становится тяжёлым
// 2. Циклическая зависимость: ProfileFeature → DesignSystem → ProfileFeature
// 3. Невозможно переиспользовать DesignSystem в других проектах
```

```swift
// ✅ ХОРОШО: Минималистичные зависимости
// DesignSystem/Package.swift
dependencies: [
    // Только то, что действительно нужно для UI
]

targets: [
    .target(
        name: "DesignSystem",
        dependencies: [] // UI компоненты независимы!
    )
]

// Если нужна аналитика в кнопке - передать через замыкание
public struct DSButton: View {
    let title: String
    let onTap: () -> Void // Analytics вызывает клиент

    public var body: some View {
        Button(title, action: onTap)
    }
}

// Использование
DSButton(title: "Login") {
    analyticsService.track(.buttonTapped)
    coordinator.showLogin()
}
```

## Связь с другими темами

**[[android-modularization]]** — Android использует Gradle modules для модуляризации, в то время как iOS опирается на Swift Package Manager и Xcode targets. Несмотря на различия в инструментах, принципы идентичны: feature-модули для бизнес-логики, core-модули для shared-кода, interface-модули для абстракций. Сравнение двух подходов особенно полезно при работе с KMP, где shared-модуль должен интегрироваться с модульной архитектурой обеих платформ. Рекомендуется параллельное изучение для кросс-платформенных команд.

**[[ios-architecture-patterns]]** — модуляризация является реализацией архитектурных принципов на уровне проектной структуры. Clean Architecture определяет слои (presentation, domain, data), а модуляризация воплощает их в физические модули с явными границами и зависимостями. Без понимания архитектурных паттернов невозможно правильно определить границы модулей. Рекомендуется сначала освоить архитектурные паттерны, затем применять их через модуляризацию.

**[[ios-dependency-injection]]** — DI является связующим механизмом между модулями: каждый feature-модуль определяет свои протоколы (интерфейсы), а DI-контейнер на уровне App Target связывает реализации с абстракциями. Без продуманной DI-стратегии модуляризация приводит к циклическим зависимостям и жёстким связям между модулями. Обе темы необходимо изучать вместе.

---

## Источники и дальнейшее чтение

### Книги
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — подробно описывает работу со Swift Package Manager, targets и frameworks, что является технической основой модуляризации iOS-проектов.
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — практические примеры организации проекта с разделением ответственности, которые естественно масштабируются в модульную архитектуру.
- Eidhof C. et al. (2019). *Advanced Swift.* — объясняет access control, generics и protocol-oriented programming — ключевые языковые механизмы, обеспечивающие правильные границы между модулями.

---

**Итог**: Модульризация iOS-приложений через Swift Package Manager — мощный инструмент для масштабирования проекта. Ключевые принципы: разделение на мелкие модули, использование Interface-модулей для разрыва циклических зависимостей, минимизация public API, и правильная организация dependency graph. Начинайте с простой структуры и добавляйте модули по мере роста проекта.

---

## Проверь себя

> [!question]- Почему Interface-модули необходимы для разрыва циклических зависимостей между feature-модулями?
> Без Interface-модулей: FeatureA импортирует FeatureB (для навигации), FeatureB импортирует FeatureA -- цикл. С Interface-модулями: FeatureA зависит от FeatureBInterface (протокол), FeatureB реализует FeatureBInterface. Зависимости направлены к абстракциям, цикл разорван. Связывание происходит в Composition Root (App модуль).

> [!question]- Как Swift Package Manager (SPM) изменил подход к модуляризации по сравнению с CocoaPods/Carthage?
> SPM -- нативный инструмент Apple, интегрированный в Xcode. Преимущества: Package.swift как декларативная конфигурация, поддержка local packages (развитие в монорепо), автоматическое разрешение зависимостей, не нужен отдельный менеджер. Минус: менее зрелая экосистема, нет поддержки ресурсов в бинарных targets до SPM 5.9.

> [!question]- Сценарий: время сборки монолитного iOS-проекта -- 15 минут. Как модуляризация ускорит сборку?
> Инкрементальная компиляция: изменение в одном модуле перекомпилирует только его и зависимые модули, а не весь проект. Кэширование: неизмененные модули используют кэш. Параллельная сборка: независимые модули компилируются одновременно. Ожидаемое ускорение: 3-5x для инкрементальных билдов. Xcode Cloud и CI также выигрывают.

---

## Ключевые карточки

Какие типы модулей существуют в модульной iOS-архитектуре?
?
Feature-модули (экраны/фичи), Core-модули (общая логика: networking, persistence), Interface-модули (протоколы для разрыва зависимостей), UI-модули (shared компоненты, design system), App-модуль (Composition Root, связывает все модули).

Что такое access control в контексте модуляризации?
?
Swift access levels определяют границы модулей: public/open -- API модуля, internal (default) -- скрыт от других модулей, private/fileprivate -- внутри файла. Правило: минимизировать public API, все что не нужно снаружи -- internal. @testable import позволяет тестам видеть internal.

Как организовать dependency graph модулей?
?
Правило: зависимости направлены вниз (Feature -> Core -> Foundation). Без циклов (DAG). Feature-модули не зависят друг от друга напрямую (через Interface-модули). App-модуль -- единственный, кто знает о всех модулях. Визуализировать через swift package dump-package.

Какие проблемы решает модуляризация?
?
Время сборки (инкрементальная компиляция), масштабирование команды (параллельная разработка), code ownership (четкие границы), тестируемость (изолированные тесты модулей), переиспользование (модуль на iOS, macOS, watchOS), enforce architecture (import rules).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-dependency-injection]] | DI как механизм связывания модулей |
| Углубиться | [[ios-xcode-fundamentals]] | Настройка Xcode для модульных проектов |
| Смежная тема | [[android-modularization]] | Модуляризация Android для сравнения подходов |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
