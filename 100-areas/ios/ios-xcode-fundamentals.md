---
title: "iOS Xcode Fundamentals: проекты, targets, schemes"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/xcode
  - level/beginner
---

# iOS Xcode Fundamentals: проекты, targets, schemes

> **TL;DR:** Xcode проект — это контейнер, организующий исходный код, ресурсы и настройки сборки. Target определяет конкретный продукт (app, framework, tests), Scheme управляет процессом сборки и запуска. Понимание этих концепций критично для правильной организации проекта, настройки CI/CD и отладки build-ошибок.

---

## Зачем это нужно?

Понимание структуры Xcode проекта объясняет:

- **Почему проект не собирается:** неправильные зависимости между targets, отсутствующие файлы в target membership
- **Почему Debug работает, а Release падает:** разные Build Settings для конфигураций
- **Почему CI/CD pipeline не работает:** неправильно настроенные schemes
- **Почему приложение весит много:** лишние ресурсы включены в bundle
- **Почему code signing не работает:** неверные настройки в Build Settings

**Числа:**
- 80% build-ошибок связаны с неправильной конфигурацией проекта
- Среднее iOS приложение имеет 3-5 targets (App, Unit Tests, UI Tests, Extensions)
- 15+ лет эволюции Xcode (с 2003 года)

---

## Аналогии из жизни

### 1. Project = здание с квартирами

```
┌─────────────────────────────────────────────────┐
│                ЗДАНИЕ (Project)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Квартира 1│  │Квартира 2│  │Квартира 3│       │
│  │  (App)   │  │ (Tests)  │  │(Extension)│      │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                  │
│  Общие коммуникации: электричество, вода        │
│  (Shared Sources, Frameworks)                   │
└─────────────────────────────────────────────────┘
```

Здание — это контейнер для квартир. Оно определяет общую инфраструктуру (фундамент, коммуникации), но каждая квартира имеет свою планировку и назначение.

### 2. Target = одна квартира с конкретным назначением

```
┌─────────────────────────────────────────────────┐
│              КВАРТИРА (Target)                   │
│                                                  │
│  Тип: Жилая / Офис / Студия                     │
│       (App / Framework / Unit Tests)            │
│                                                  │
│  Содержимое:                                    │
│  - Комнаты (Source files)                       │
│  - Мебель (Resources)                           │
│  - Техника (Linked Frameworks)                  │
│                                                  │
│  Документы:                                     │
│  - Адрес (Bundle Identifier)                    │
│  - Планировка (Info.plist)                      │
└─────────────────────────────────────────────────┘
```

Квартира определяет, что именно строится. Офис не имеет спальни (Unit Tests не имеют UI). Жилая квартира требует кухню (App требует AppDelegate/SceneDelegate).

### 3. Scheme = инструкция как войти в квартиру

```
┌─────────────────────────────────────────────────┐
│              ИНСТРУКЦИЯ (Scheme)                 │
│                                                  │
│  1. Войти в подъезд (Build)                     │
│  2. Нажать код на домофоне (Configuration)      │
│  3. Подняться на лифте (Run)                    │
│  4. Проверить газ и воду (Test)                 │
│  5. Вызвать оценщика (Profile)                  │
│  6. Провести инспекцию (Analyze)                │
│  7. Подготовить к продаже (Archive)             │
└─────────────────────────────────────────────────┘
```

Scheme — это последовательность действий. Можно создать разные инструкции для одной квартиры: "войти утром" (Debug) vs "войти вечером" (Release).

### 4. Build Configuration = режим отопления

```
┌─────────────────────────────────────────────────┐
│           РЕЖИМ ОТОПЛЕНИЯ (Configuration)        │
│                                                  │
│  Debug = Максимум тепла                         │
│  ├── Батареи на максимум (No optimization)      │
│  ├── Окна открыты (Debug symbols)               │
│  └── Термометры везде (Assertions enabled)      │
│                                                  │
│  Release = Экономный режим                      │
│  ├── Термостат оптимизирует (Optimization -O)   │
│  ├── Окна закрыты (Stripped symbols)            │
│  └── Минимум датчиков (Assertions disabled)     │
└─────────────────────────────────────────────────┘
```

Debug = максимум информации для разработчика (медленно, но удобно отлаживать).
Release = максимум производительности для пользователя (быстро, но сложно отлаживать).

### 5. Workspace = жилой комплекс из нескольких зданий

```
┌─────────────────────────────────────────────────────────────┐
│                  ЖИЛОЙ КОМПЛЕКС (Workspace)                  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Здание A   │  │  Здание B   │  │  Здание C   │          │
│  │(MainApp.    │  │(NetworkKit. │  │(UIKit.      │          │
│  │ xcodeproj)  │  │ xcodeproj)  │  │ xcodeproj)  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  Общая территория: парковка, детская площадка               │
│  (Shared build settings, schemes)                           │
└─────────────────────────────────────────────────────────────┘
```

Workspace объединяет несколько проектов. Жители здания A могут ходить в гости к жителям здания B (cross-project dependencies).

---

## Как устроен Xcode проект

### Структура файлов

```
MyApp/
├── MyApp.xcodeproj/           # Или MyApp.xcworkspace
│   ├── project.pbxproj        # Главный файл — все настройки проекта
│   ├── xcuserdata/            # Личные настройки разработчика (не коммитить!)
│   └── xcshareddata/          # Общие настройки (schemes, breakpoints)
│
├── MyApp/                     # Sources — исходный код приложения
│   ├── AppDelegate.swift
│   ├── SceneDelegate.swift
│   ├── ContentView.swift
│   ├── Models/
│   ├── Views/
│   ├── ViewModels/
│   ├── Resources/
│   │   ├── Assets.xcassets
│   │   └── Localizable.strings
│   └── Info.plist
│
├── MyAppTests/               # Unit Tests target
│   └── MyAppTests.swift
│
├── MyAppUITests/             # UI Tests target
│   └── MyAppUITests.swift
│
└── Packages/                 # Local Swift Packages
    └── CoreKit/
```

### .xcodeproj vs .xcworkspace

```
┌─────────────────────────────────────────────────────────────┐
│                       .xcodeproj                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Один проект = один .xcodeproj                        │    │
│  │                                                      │    │
│  │ Когда использовать:                                  │    │
│  │ - Простые приложения без внешних зависимостей       │    │
│  │ - Проекты без CocoaPods/Carthage                    │    │
│  │ - Учебные проекты                                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       .xcworkspace                           │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │   MainApp.       │  │   Pods.          │                 │
│  │   xcodeproj      │  │   xcodeproj      │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  Когда использовать:                                        │
│  - CocoaPods (создаёт автоматически)                       │
│  - Несколько связанных проектов                            │
│  - Shared frameworks между проектами                        │
└─────────────────────────────────────────────────────────────┘
```

### Project.pbxproj — сердце проекта

```
// Упрощённая структура project.pbxproj
{
    archiveVersion = 1;
    classes = {};
    objectVersion = 56;

    objects = {
        // Build Files — какие файлы включены в сборку
        ABC123 = {
            isa = PBXBuildFile;
            fileRef = DEF456;
        };

        // File References — все файлы проекта
        DEF456 = {
            isa = PBXFileReference;
            path = "ContentView.swift";
        };

        // Groups — папки в навигаторе
        GHI789 = {
            isa = PBXGroup;
            children = (DEF456);
            name = "Views";
        };

        // Native Targets — targets проекта
        JKL012 = {
            isa = PBXNativeTarget;
            name = "MyApp";
            buildPhases = (...);
            dependencies = (...);
        };

        // Build Configurations
        MNO345 = {
            isa = XCBuildConfiguration;
            name = "Debug";
            buildSettings = {...};
        };
    };

    rootObject = PQR678; // Ссылка на проект
}
```

> **Важно:** Никогда не редактируйте project.pbxproj вручную! Это частая причина merge-конфликтов. Используйте Xcode или инструменты типа XcodeGen/Tuist.

---

## Targets в деталях

### Что такое Target?

Target — это набор инструкций для создания конкретного продукта (app, framework, test bundle).

```
┌─────────────────────────────────────────────────────────────┐
│                         TARGET                               │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Входные данные:                                      │    │
│  │ ├── Source files (*.swift, *.m, *.c)                │    │
│  │ ├── Resources (images, strings, storyboards)        │    │
│  │ ├── Info.plist (metadata)                           │    │
│  │ └── Entitlements (capabilities)                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Build Phases (в порядке выполнения):                │    │
│  │ 1. Dependencies                                     │    │
│  │ 2. Compile Sources                                  │    │
│  │ 3. Link Binary With Libraries                       │    │
│  │ 4. Copy Bundle Resources                            │    │
│  │ 5. [Custom Scripts]                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Выходной продукт:                                   │    │
│  │ - MyApp.app (Application)                           │    │
│  │ - MyFramework.framework (Framework)                 │    │
│  │ - MyAppTests.xctest (Test Bundle)                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Типы Targets

```
┌─────────────────────────────────────────────────────────────┐
│                      ТИПЫ TARGETS                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Application                                                 │
│  ├── iOS App                    (.app)                      │
│  ├── watchOS App                (.app)                      │
│  ├── macOS App                  (.app)                      │
│  └── tvOS App                   (.app)                      │
│                                                              │
│  Framework & Library                                        │
│  ├── Framework                  (.framework)                │
│  ├── Static Library             (.a)                        │
│  └── Dynamic Library            (.dylib)                    │
│                                                              │
│  Tests                                                      │
│  ├── Unit Testing Bundle        (.xctest)                   │
│  └── UI Testing Bundle          (.xctest)                   │
│                                                              │
│  App Extensions                                             │
│  ├── Widget Extension           (.appex)                    │
│  ├── Share Extension            (.appex)                    │
│  ├── Notification Service       (.appex)                    │
│  ├── Notification Content       (.appex)                    │
│  └── Intents Extension          (.appex)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Target Dependencies

Target dependencies определяют порядок сборки.

```
┌──────────────────────────────────────────────────────────────┐
│                    ЗАВИСИМОСТИ TARGETS                        │
│                                                               │
│    ┌─────────────┐                                           │
│    │  MyApp      │ ◄── Главный target (собирается последним) │
│    └──────┬──────┘                                           │
│           │                                                   │
│           │ depends on                                        │
│           │                                                   │
│    ┌──────▼──────┐                                           │
│    │ NetworkKit  │ ◄── Framework (собирается раньше)         │
│    └──────┬──────┘                                           │
│           │                                                   │
│           │ depends on                                        │
│           │                                                   │
│    ┌──────▼──────┐                                           │
│    │  CoreKit    │ ◄── Базовый framework (собирается первым) │
│    └─────────────┘                                           │
│                                                               │
│  Порядок сборки: CoreKit → NetworkKit → MyApp                │
└──────────────────────────────────────────────────────────────┘
```

```swift
// Target: CoreKit (Framework)
// Файл: CoreKit/Logger.swift
public struct Logger {
    public static func log(_ message: String) {
        // Базовая функциональность логирования
        // Доступна всем targets, которые зависят от CoreKit
        print("[LOG] \(message)")
    }
}

// Target: NetworkKit (Framework, depends on CoreKit)
// Файл: NetworkKit/APIClient.swift
import CoreKit  // Можем импортировать, потому что CoreKit — dependency

public class APIClient {
    public func fetch(url: URL) async throws -> Data {
        Logger.log("Fetching: \(url)")  // Используем CoreKit
        // ...
    }
}

// Target: MyApp (App, depends on NetworkKit)
// Файл: MyApp/ContentView.swift
import NetworkKit  // NetworkKit автоматически тянет CoreKit
import CoreKit     // Можно импортировать явно

struct ContentView: View {
    let client = APIClient()

    var body: some View {
        Button("Fetch") {
            Logger.log("Button tapped")
        }
    }
}
```

### Linked Frameworks

```
┌─────────────────────────────────────────────────────────────┐
│                  LINKED FRAMEWORKS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  System Frameworks (поставляются с iOS)                     │
│  ├── UIKit.framework        — UI компоненты                 │
│  ├── Foundation.framework   — базовые типы                  │
│  ├── CoreData.framework     — persistence                   │
│  └── MapKit.framework       — карты                         │
│                                                              │
│  Your Frameworks (ваши или сторонние)                       │
│  ├── NetworkKit.framework   — local framework               │
│  ├── Alamofire.framework    — third-party                   │
│  └── Firebase.framework     — third-party                   │
│                                                              │
│  Linking Types:                                             │
│  ├── Required — crash если отсутствует                      │
│  └── Optional — работает без framework (weak linking)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Bundle Identifier

Bundle Identifier — уникальный идентификатор приложения в экосистеме Apple.

```
┌─────────────────────────────────────────────────────────────┐
│                    BUNDLE IDENTIFIER                         │
│                                                              │
│  Format: com.company.appname                                │
│                                                              │
│  Примеры:                                                   │
│  ├── com.mycompany.myapp           — основное приложение    │
│  ├── com.mycompany.myapp.widget    — widget extension       │
│  ├── com.mycompany.myapp.share     — share extension        │
│  └── com.mycompany.myapp.tests     — test bundle            │
│                                                              │
│  Правила:                                                   │
│  ├── Уникальный во всём App Store                          │
│  ├── Extension должен начинаться с parent app ID           │
│  ├── Регистрозависимый (case-sensitive)                    │
│  └── Нельзя менять после публикации (иначе новое приложение)│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

```swift
// Получение Bundle Identifier программно
let bundleID = Bundle.main.bundleIdentifier
// "com.mycompany.myapp"

// Проверка, что это основное приложение, а не extension
if bundleID == "com.mycompany.myapp" {
    // Код только для основного приложения
}
```

---

## Schemes и Configurations

### Build Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                  BUILD CONFIGURATIONS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Debug (для разработки)                                     │
│  ├── SWIFT_OPTIMIZATION_LEVEL = -Onone (без оптимизации)   │
│  ├── DEBUG_INFORMATION_FORMAT = dwarf-with-dsym            │
│  ├── ENABLE_TESTABILITY = YES                              │
│  ├── SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG           │
│  └── Быстрая сборка, полная отладка                        │
│                                                              │
│  Release (для публикации)                                   │
│  ├── SWIFT_OPTIMIZATION_LEVEL = -O (оптимизация скорости)  │
│  ├── SWIFT_COMPILATION_MODE = wholemodule                  │
│  ├── ENABLE_TESTABILITY = NO                               │
│  ├── Медленная сборка, максимальная производительность     │
│  └── Strip debug symbols                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Custom Configurations

```
┌─────────────────────────────────────────────────────────────┐
│                 CUSTOM CONFIGURATIONS                        │
│                                                              │
│  Типичный набор для production-приложения:                  │
│                                                              │
│  ┌─────────────┐                                            │
│  │   Debug     │ → Локальная разработка                     │
│  │             │   API: localhost                           │
│  │             │   Logs: verbose                            │
│  └─────────────┘                                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │  Staging    │ → Тестирование QA                          │
│  │             │   API: staging.api.com                     │
│  │             │   Logs: info                               │
│  └─────────────┘                                            │
│                                                              │
│  ┌─────────────┐                                            │
│  │ Production  │ → App Store                                │
│  │             │   API: api.com                             │
│  │             │   Logs: error only                         │
│  └─────────────┘                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Создание custom configuration:
1. Project → Info → Configurations
2. Нажать "+" и дублировать существующую (Debug или Release)
3. Переименовать в "Staging"

```swift
// Использование разных configurations в коде
// Build Settings: SWIFT_ACTIVE_COMPILATION_CONDITIONS = STAGING (для Staging config)

#if DEBUG
let apiURL = URL(string: "http://localhost:8080")!
let logLevel: LogLevel = .verbose
#elseif STAGING
let apiURL = URL(string: "https://staging.api.com")!
let logLevel: LogLevel = .info
#else // RELEASE/PRODUCTION
let apiURL = URL(string: "https://api.com")!
let logLevel: LogLevel = .error
#endif
```

### Scheme — полный контроль

```
┌─────────────────────────────────────────────────────────────┐
│                         SCHEME                               │
│                                                              │
│  Scheme = Target + Configuration + Environment + Actions    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                     ACTIONS                          │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │                                                      │    │
│  │  1. Build                                           │    │
│  │     ├── Targets to build: MyApp, CoreKit           │    │
│  │     └── Find Implicit Dependencies: YES            │    │
│  │                                                      │    │
│  │  2. Run (Cmd+R)                                     │    │
│  │     ├── Build Configuration: Debug                 │    │
│  │     ├── Executable: MyApp.app                      │    │
│  │     ├── Arguments: --verbose                       │    │
│  │     └── Environment Variables: API_KEY=xxx        │    │
│  │                                                      │    │
│  │  3. Test (Cmd+U)                                    │    │
│  │     ├── Build Configuration: Debug                 │    │
│  │     ├── Test Targets: MyAppTests, MyAppUITests    │    │
│  │     └── Code Coverage: YES                         │    │
│  │                                                      │    │
│  │  4. Profile (Cmd+I)                                 │    │
│  │     ├── Build Configuration: Release               │    │
│  │     └── Opens Instruments                          │    │
│  │                                                      │    │
│  │  5. Analyze (Cmd+Shift+B)                          │    │
│  │     ├── Build Configuration: Debug                 │    │
│  │     └── Static analysis (memory leaks, etc.)      │    │
│  │                                                      │    │
│  │  6. Archive                                         │    │
│  │     ├── Build Configuration: Release               │    │
│  │     └── Creates .xcarchive for App Store          │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Несколько Schemes для разных целей

```
┌─────────────────────────────────────────────────────────────┐
│                    ТИПИЧНЫЕ SCHEMES                          │
│                                                              │
│  MyApp                                                      │
│  └── Run: Debug, Profile: Release, Archive: Release         │
│                                                              │
│  MyApp-Staging                                              │
│  └── Run: Staging, Archive: Staging                         │
│      └── Для QA тестирования                               │
│                                                              │
│  MyApp-Production                                           │
│  └── Run: Release, Archive: Release                         │
│      └── Для финального тестирования перед релизом         │
│                                                              │
│  MyApp-AllTests                                             │
│  └── Test: Debug (Unit + UI + Performance tests)           │
│      └── Для CI/CD pipeline                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Build Settings

### Иерархия Build Settings

```
┌─────────────────────────────────────────────────────────────┐
│               BUILD SETTINGS INHERITANCE                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Level 1: Platform Default                            │    │
│  │ (Xcode/iOS SDK defaults)                            │    │
│  └───────────────────────┬─────────────────────────────┘    │
│                          │ overridden by                     │
│  ┌───────────────────────▼─────────────────────────────┐    │
│  │ Level 2: Project Settings                            │    │
│  │ (MyApp.xcodeproj → Build Settings)                  │    │
│  └───────────────────────┬─────────────────────────────┘    │
│                          │ overridden by                     │
│  ┌───────────────────────▼─────────────────────────────┐    │
│  │ Level 3: Target Settings                             │    │
│  │ (MyApp target → Build Settings)                     │    │
│  └───────────────────────┬─────────────────────────────┘    │
│                          │ overridden by                     │
│  ┌───────────────────────▼─────────────────────────────┐    │
│  │ Level 4: xcconfig File                               │    │
│  │ (Debug.xcconfig, Release.xcconfig)                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Resolved = финальное значение после всех override          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Важнейшие Build Settings

```
┌─────────────────────────────────────────────────────────────┐
│                 CRITICAL BUILD SETTINGS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ВЕРСИИ И ИДЕНТИФИКАЦИЯ                                     │
│  ├── PRODUCT_BUNDLE_IDENTIFIER                             │
│  │   com.company.app — уникальный ID приложения            │
│  │                                                          │
│  ├── MARKETING_VERSION (CFBundleShortVersionString)        │
│  │   1.0.0 — версия для пользователей                      │
│  │                                                          │
│  └── CURRENT_PROJECT_VERSION (CFBundleVersion)             │
│      42 — build number для App Store                       │
│                                                              │
│  SWIFT                                                      │
│  ├── SWIFT_VERSION                                         │
│  │   5.9 — версия Swift compiler                           │
│  │                                                          │
│  ├── SWIFT_OPTIMIZATION_LEVEL                              │
│  │   -Onone (Debug) / -O (Release) / -Osize               │
│  │                                                          │
│  └── SWIFT_ACTIVE_COMPILATION_CONDITIONS                   │
│      DEBUG / STAGING — для #if условий                     │
│                                                              │
│  DEPLOYMENT                                                 │
│  ├── IPHONEOS_DEPLOYMENT_TARGET                            │
│  │   15.0 — минимальная версия iOS                         │
│  │                                                          │
│  └── TARGETED_DEVICE_FAMILY                                │
│      1 (iPhone) / 2 (iPad) / 1,2 (Universal)              │
│                                                              │
│  CODE SIGNING                                               │
│  ├── CODE_SIGN_STYLE                                       │
│  │   Automatic / Manual                                    │
│  │                                                          │
│  ├── DEVELOPMENT_TEAM                                      │
│  │   ABCD1234EF — Team ID от Apple Developer              │
│  │                                                          │
│  ├── CODE_SIGN_IDENTITY                                    │
│  │   "Apple Development" / "Apple Distribution"           │
│  │                                                          │
│  └── PROVISIONING_PROFILE_SPECIFIER                        │
│      Profile name (для Manual signing)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### xcconfig файлы

xcconfig — текстовые файлы для Build Settings. Версионируются в Git, легко читаются и переиспользуются.

```
// Файл: Config/Base.xcconfig
// Базовые настройки для всех конфигураций

// Идентификация
PRODUCT_NAME = MyApp
PRODUCT_BUNDLE_IDENTIFIER = com.mycompany.myapp

// Swift
SWIFT_VERSION = 5.9

// Deployment
IPHONEOS_DEPLOYMENT_TARGET = 15.0
TARGETED_DEVICE_FAMILY = 1,2

// Code Signing (Automatic)
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = ABCD1234EF
```

```
// Файл: Config/Debug.xcconfig
// Настройки для Debug конфигурации

#include "Base.xcconfig"

// Оптимизация выключена для быстрой сборки
SWIFT_OPTIMIZATION_LEVEL = -Onone

// Полная отладочная информация
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym

// Включаем testability для unit tests
ENABLE_TESTABILITY = YES

// Compilation conditions для #if DEBUG
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG

// Другой bundle ID для одновременной установки
PRODUCT_BUNDLE_IDENTIFIER = com.mycompany.myapp.debug
```

```
// Файл: Config/Release.xcconfig
// Настройки для Release конфигурации

#include "Base.xcconfig"

// Максимальная оптимизация
SWIFT_OPTIMIZATION_LEVEL = -O

// Whole Module Optimization для лучшей производительности
SWIFT_COMPILATION_MODE = wholemodule

// Минимальная отладочная информация
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
STRIP_INSTALLED_PRODUCT = YES

// Выключаем testability
ENABLE_TESTABILITY = NO

// Без debug флагов
SWIFT_ACTIVE_COMPILATION_CONDITIONS =
```

### Присваивание xcconfig к конфигурациям

```
┌─────────────────────────────────────────────────────────────┐
│           PROJECT → Info → Configurations                    │
│                                                              │
│  Configuration          Based on Configuration File         │
│  ─────────────────────────────────────────────────────────  │
│  Debug                  Config/Debug.xcconfig               │
│  └── MyApp target       Config/Debug.xcconfig               │
│  └── MyAppTests target  Config/DebugTests.xcconfig         │
│                                                              │
│  Release                Config/Release.xcconfig             │
│  └── MyApp target       Config/Release.xcconfig             │
│  └── MyAppTests target  Config/ReleaseTests.xcconfig       │
│                                                              │
│  Staging                Config/Staging.xcconfig             │
│  └── MyApp target       Config/Staging.xcconfig             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Распространённые ошибки

### 1. Файл не включён в Target Membership

```swift
// ❌ НЕПРАВИЛЬНО: файл создан, но не добавлен в target
// Xcode: "Cannot find 'MyHelper' in scope"

// Файл существует в проекте, но checkbox в Target Membership не отмечен
// File Inspector → Target Membership → MyApp ☐ (не отмечено!)

// ✅ ПРАВИЛЬНО: файл добавлен в нужный target
// File Inspector → Target Membership → MyApp ☑ (отмечено!)

// Проверка в коде (должно компилироваться):
let helper = MyHelper()
```

### 2. Import framework без добавления в Linked Frameworks

```swift
// ❌ НЕПРАВИЛЬНО: импортируем framework, но не добавили в Link Binary
// Build Error: "No such module 'Alamofire'"

import Alamofire  // Framework не слинкован!

// ✅ ПРАВИЛЬНО: сначала добавить framework
// Target → Build Phases → Link Binary With Libraries → + Alamofire.framework

import Alamofire  // Теперь работает
```

### 3. Неправильный порядок Target Dependencies

```swift
// ❌ НЕПРАВИЛЬНО: MyApp пытается собраться раньше NetworkKit
// Build Error: "No such module 'NetworkKit'"

// MyApp target зависит от NetworkKit, но dependency не указана
import NetworkKit  // NetworkKit ещё не собран!

// ✅ ПРАВИЛЬНО: добавить dependency
// MyApp target → Build Phases → Dependencies → + NetworkKit

// Xcode соберёт NetworkKit первым, затем MyApp
import NetworkKit  // NetworkKit уже собран и доступен
```

### 4. Debug-код попадает в Release

```swift
// ❌ НЕПРАВИЛЬНО: отладочный код всегда выполняется
func loadData() {
    print("DEBUG: Loading data...")  // Попадёт в Release!
    // Пользователи увидят эти логи
}

// ✅ ПРАВИЛЬНО: использовать compilation conditions
func loadData() {
    #if DEBUG
    print("DEBUG: Loading data...")  // Только в Debug
    #endif

    // Или через Logger с уровнями
    Logger.debug("Loading data...")  // Logger отключен в Release
}
```

### 5. Hardcoded paths вместо Build Settings

```swift
// ❌ НЕПРАВИЛЬНО: hardcoded URL
struct Config {
    static let apiURL = URL(string: "https://api.production.com")!
    // Как тестировать на staging? Менять код каждый раз?
}

// ✅ ПРАВИЛЬНО: использовать Build Settings и Info.plist
// 1. Добавить в Build Settings: API_BASE_URL = https://api.production.com
// 2. Добавить в Info.plist: APIBaseURL = $(API_BASE_URL)
// 3. Читать в коде:

struct Config {
    static let apiURL: URL = {
        guard let urlString = Bundle.main.object(forInfoDictionaryKey: "APIBaseURL") as? String,
              let url = URL(string: urlString) else {
            fatalError("APIBaseURL not configured in Info.plist")
        }
        return url
    }()
}

// Теперь можно менять URL через конфигурации:
// Debug.xcconfig: API_BASE_URL = http://localhost:8080
// Staging.xcconfig: API_BASE_URL = https://staging.api.com
// Release.xcconfig: API_BASE_URL = https://api.production.com
```

### 6. Один Scheme для всего

```swift
// ❌ НЕПРАВИЛЬНО: один scheme, переключаем configuration вручную
// Scheme "MyApp":
//   Run → Configuration: Debug (меняем на Release вручную для тестирования)
//   Archive → Configuration: Release

// Проблема: легко забыть переключить, запустить Release-сборку с debug-данными

// ✅ ПРАВИЛЬНО: отдельные schemes для разных целей

// Scheme "MyApp-Debug":
//   Run → Configuration: Debug
//   Используем для ежедневной разработки

// Scheme "MyApp-Staging":
//   Run → Configuration: Staging
//   Archive → Configuration: Staging
//   Для QA тестирования

// Scheme "MyApp-Release":
//   Run → Configuration: Release
//   Archive → Configuration: Release
//   Для финального тестирования и App Store

// CI/CD script:
// xcodebuild -scheme "MyApp-Release" -configuration Release archive
```

---

## Ментальные модели

### 1. Модель "Фабрика"

```
┌─────────────────────────────────────────────────────────────┐
│                    ФАБРИКА (Xcode)                           │
│                                                              │
│  Чертёж (Project)                                           │
│  └── Описывает ВСЕ возможные продукты                       │
│                                                              │
│  Производственная линия (Target)                            │
│  └── Создаёт ОДИН конкретный продукт                        │
│                                                              │
│  Инструкция для рабочего (Scheme)                           │
│  └── КАК запустить линию (Debug/Release/Test)              │
│                                                              │
│  Режим работы станка (Configuration)                        │
│  └── Настройки качества/скорости производства               │
│                                                              │
│  Детали и материалы (Sources + Resources)                   │
│  └── Из чего собирается продукт                             │
│                                                              │
│  Готовый продукт (App/Framework/Test Bundle)                │
│  └── То, что выходит с конвейера                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Модель "Рецепт"

```
┌─────────────────────────────────────────────────────────────┐
│                     РЕЦЕПТ (Target)                          │
│                                                              │
│  Ингредиенты:                                               │
│  ├── Мука (Swift files)                                     │
│  ├── Яйца (Resources)                                       │
│  └── Специи (Frameworks)                                    │
│                                                              │
│  Инструкция приготовления (Build Phases):                   │
│  1. Подготовить ингредиенты (Dependencies)                  │
│  2. Смешать и запечь (Compile Sources)                      │
│  3. Добавить соус (Link Binary)                             │
│  4. Украсить (Copy Resources)                               │
│  5. Добавить секретный ингредиент (Run Script)              │
│                                                              │
│  Настройки духовки (Build Configuration):                   │
│  ├── Debug: 100°C, медленно (без оптимизации)              │
│  └── Release: 200°C, быстро (с оптимизацией)               │
│                                                              │
│  Результат: пирог (MyApp.app)                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3. Модель "Гардероб"

```
┌─────────────────────────────────────────────────────────────┐
│                    ГАРДЕРОБ (Project)                        │
│                                                              │
│  Полки с одеждой (Targets):                                 │
│  ├── Повседневная (App) — носим каждый день                │
│  ├── Спортивная (Unit Tests) — для тренировок              │
│  └── Вечерняя (UI Tests) — для особых случаев              │
│                                                              │
│  Образы (Schemes):                                          │
│  ├── "На работу" — рубашка + брюки + туфли                 │
│  ├── "На пробежку" — футболка + шорты + кроссовки          │
│  └── "На вечеринку" — полный образ со всеми аксессуарами   │
│                                                              │
│  Сезонность (Configuration):                                │
│  ├── Debug = Лето (легко, комфортно, быстро одеться)       │
│  └── Release = Зима (тщательно, много слоёв, но тепло)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4. Модель "Оркестр"

```
┌─────────────────────────────────────────────────────────────┐
│                   ОРКЕСТР (Workspace)                        │
│                                                              │
│  Партитура (Scheme)                                         │
│  └── Описывает, кто и когда играет                          │
│                                                              │
│  Секции оркестра (Targets):                                 │
│  ├── Струнные (App) — основная мелодия                     │
│  ├── Духовые (Framework) — поддержка                       │
│  └── Ударные (Tests) — ритм и проверка                     │
│                                                              │
│  Дирижёр (Build System)                                     │
│  └── Координирует порядок (Dependencies)                    │
│                                                              │
│  Репетиция vs Концерт (Configuration)                       │
│  ├── Debug = Репетиция (можно остановиться, исправить)     │
│  └── Release = Концерт (всё должно быть идеально)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5. Модель "Город"

```
┌─────────────────────────────────────────────────────────────┐
│                     ГОРОД (Workspace)                        │
│                                                              │
│  Районы (Projects):                                         │
│  ├── Центр (MainApp.xcodeproj)                             │
│  ├── Промзона (Frameworks.xcodeproj)                       │
│  └── Тестовый полигон (Tests.xcodeproj)                    │
│                                                              │
│  Здания (Targets):                                          │
│  └── Каждое здание производит что-то конкретное            │
│                                                              │
│  Дороги (Dependencies):                                     │
│  └── Связывают здания, определяют порядок поставок         │
│                                                              │
│  Генплан (Scheme):                                          │
│  └── Какие здания работают, в каком режиме                 │
│                                                              │
│  Режим города (Configuration):                              │
│  ├── Debug = Дневной режим (всё открыто, много активности) │
│  └── Release = Ночной режим (только важное, оптимизировано)│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

### Вопрос 1: Что произойдёт?

```swift
// У вас есть два targets: MyApp и MyAppTests
// Файл Helper.swift добавлен только в MyApp target
// В MyAppTests вы пишете:

import XCTest
@testable import MyApp

class HelperTests: XCTestCase {
    func testHelper() {
        let helper = Helper()  // ???
    }
}
```

<details>
<summary>Ответ</summary>

Код скомпилируется и будет работать! `@testable import MyApp` делает internal-типы MyApp доступными в тестах. Helper.swift является частью MyApp, поэтому класс Helper доступен.

Но если бы Helper был в отдельном framework (например, CoreKit), и этот framework не был бы добавлен в зависимости MyAppTests, то был бы build error.

</details>

### Вопрос 2: Почему build падает?

```
// Структура проекта:
// - MyApp (app target)
//   - depends on NetworkKit
// - NetworkKit (framework target)
//   - depends on CoreKit
// - CoreKit (framework target)
//   - no dependencies

// Ошибка при сборке MyApp:
// "No such module 'CoreKit'" в файле MyApp/APIManager.swift
```

<details>
<summary>Ответ</summary>

MyApp напрямую использует CoreKit (`import CoreKit`), но в зависимостях MyApp указан только NetworkKit.

Хотя NetworkKit зависит от CoreKit (транзитивная зависимость), это не означает автоматический re-export. В Swift нужно либо:

1. Добавить CoreKit в явные зависимости MyApp
2. Использовать `@_exported import CoreKit` в NetworkKit (не рекомендуется)
3. Не импортировать CoreKit напрямую в MyApp, а использовать через NetworkKit API

</details>

### Вопрос 3: Debug vs Release

```swift
// В Debug всё работает, в Release — crash
// Что не так?

class DataManager {
    var cache: [String: Any] = [:]

    func getData() -> Data {
        assert(!cache.isEmpty, "Cache should not be empty")  // <-- тут
        return cache["data"] as! Data
    }
}
```

<details>
<summary>Ответ</summary>

`assert()` в Release-сборке удаляется компилятором (SWIFT_OPTIMIZATION_LEVEL = -O). Поэтому проверка `!cache.isEmpty` не выполняется, и force unwrap `as! Data` крашится на nil.

Правильный подход:
```swift
func getData() -> Data? {
    guard !cache.isEmpty else {
        assertionFailure("Cache should not be empty")  // Только в Debug
        return nil  // В Release возвращаем nil
    }
    return cache["data"] as? Data
}
```

Или использовать `precondition()` если проверка должна работать и в Release.

</details>

### Вопрос 4: Несколько конфигураций

```
// У вас 3 конфигурации: Debug, Staging, Release
// Вы хотите использовать разные API endpoints
// Какой подход лучше?

// A) #if DEBUG / #if STAGING / #if RELEASE в коде
// B) Разные Info.plist файлы для каждой конфигурации
// C) xcconfig файлы + одна переменная в Info.plist
// D) Разные targets для каждого environment
```

<details>
<summary>Ответ</summary>

**C) xcconfig файлы + одна переменная в Info.plist** — лучший подход.

- **A)** Работает, но захламляет код условными компиляциями
- **B)** Работает, но дублирование Info.plist — кошмар для поддержки
- **C)** ✅ Чистый код, одна точка конфигурации, легко менять
- **D)** Работает, но создаёт много targets, усложняет проект

Реализация C:
```
// Debug.xcconfig
API_BASE_URL = http://localhost:8080

// Staging.xcconfig
API_BASE_URL = https://staging.api.com

// Release.xcconfig
API_BASE_URL = https://api.com

// Info.plist
<key>APIBaseURL</key>
<string>$(API_BASE_URL)</string>

// Swift code
let url = Bundle.main.infoDictionary?["APIBaseURL"] as? String
```

</details>

---

## Связанные темы

### Prerequisites (изучить перед)
- [[ios-architecture]] — архитектура iOS и как приложения работают в системе

### Next Steps (изучить после)
- [[ios-compilation-pipeline]] — как Swift код превращается в исполняемый файл
- [[ios-code-signing]] — подписание кода и provisioning profiles
- [[ios-modularization]] — организация кода в модули через SPM

### Related (связанные темы)
- [[android-gradle-fundamentals]] — аналогичные концепции в Android (Gradle modules, build variants)

---

## Источники

### Apple Documentation
- [Xcode Project Management Guide](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build Settings Reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Creating a Build Configuration File](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)

### WWDC Sessions
- [WWDC 2018: Behind the Scenes of the Xcode Build Process](https://developer.apple.com/videos/play/wwdc2018/415/)
- [WWDC 2022: Link fast: Improve build and launch times](https://developer.apple.com/videos/play/wwdc2022/110362/)
- [WWDC 2023: Meet mergeable libraries](https://developer.apple.com/videos/play/wwdc2023/10268/)

### Books & Articles
- "iOS Development with Swift" — Chapter on Xcode Project Structure
- objc.io — "Build Configuration Management with xcconfig"
- Point-Free — "Modular Architecture for iOS"
