---
title: "iOS Architecture: Darwin, XNU и слои системы"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
area: ios
confidence: high
tags:
  - topic/ios
  - topic/architecture
  - type/deep-dive
  - level/advanced
cs-foundations:
  - "[[os-overview]]"
  - "[[os-processes-threads]]"
related:
  - "[[ios-overview]]"
  - "[[ios-app-components]]"
  - "[[ios-process-memory]]"
  - "[[android-architecture]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-app-components]]"
---

# iOS Architecture: Darwin, XNU и слои системы

> **TL;DR:** iOS построен на Darwin — open-source ядре, которое включает XNU (гибрид Mach + BSD). Система организована в 4 слоя: Core OS → Core Services → Media → Cocoa Touch. Каждый слой предоставляет абстракции поверх нижнего. Приложения работают в sandbox с ограниченным доступом к системе.

---

## Зачем это нужно?

Понимание архитектуры iOS объясняет:

- **Почему iOS такой стабильный:** sandbox изоляция + микроядерная архитектура
- **Почему приложения ограничены:** security model с entitlements
- **Почему нельзя делать background что угодно:** kernel-level ограничения
- **Почему interop с C/ObjC важен:** всё построено на Darwin APIs

**Числа:**
- 99.5% uptime iOS devices (vs 97% Android) — sandbox архитектура
- 15+ лет эволюции от iPhone OS 1.0 (2007)
- XNU kernel ~6 million lines of code

---

## Интуиция: 5 аналогий из жизни

### 1. Слои как этажи небоскрёба

```
┌─────────────────────────────┐
│   Penthouse (Cocoa Touch)   │ ← Приложения живут здесь
├─────────────────────────────┤
│   Business floor (Media)    │ ← Графика, звук, видео
├─────────────────────────────┤
│   Services (Core Services)  │ ← Инфраструктура (сеть, данные)
├─────────────────────────────┤
│   Foundation (Core OS)      │ ← Ядро, безопасность
└─────────────────────────────┘
```

Чем выше этаж, тем удобнее (лучший вид, сервис), но дальше от "земли" (hardware).

### 2. XNU как мультитул

XNU объединяет лучшее из разных миров:
- **Mach (лезвие)** — базовый механизм: процессы, память, IPC
- **BSD (ножницы)** — Unix APIs: файлы, сети, пользователи
- **IOKit (отвёртка)** — драйверы устройств

### 3. Sandbox как квартира в доме

Каждое приложение живёт в своей "квартире":
- Свои комнаты (файлы)
- Нельзя заходить к соседям без разрешения (entitlements)
- Общие зоны (shared frameworks) доступны всем
- Консьерж (система) контролирует доступ

### 4. Frameworks как готовые ингредиенты

Вместо готовить с нуля (raw system calls), используешь полуфабрикаты:
- UIKit = готовое тесто (UI компоненты)
- Foundation = базовые продукты (strings, collections)
- Core Foundation = сырые ингредиенты (C APIs)

### 5. Entitlements как пропуски

Entitlements — это пропуски для доступа к функциям:
- Push notifications = пропуск в серверную
- iCloud = пропуск в облачное хранилище
- HealthKit = пропуск в медицинские данные

---

## Как это работает: архитектура iOS

### Стек технологий

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           YOUR APPLICATION                               │
│                        Swift / Objective-C code                          │
├─────────────────────────────────────────────────────────────────────────┤
│                         COCOA TOUCH LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  UIKit   │  │ SwiftUI  │  │ MapKit   │  │ EventKit │  │ PushKit  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                           MEDIA LAYER                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Core Anim │  │ AVFound  │  │Core Audio│  │ Core Img │  │ SceneKit │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                        CORE SERVICES LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Foundation│  │Core Data │  │ CloudKit │  │Core Locat│  │ StoreKit │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                          CORE OS LAYER                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Security │  │Accelerate│  │Core Bluet│  │ Keychain │  │ LocalAuth│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                            DARWIN / XNU                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │      Mach       │  │       BSD       │  │      IOKit      │         │
│  │  (microkernel)  │  │   (Unix APIs)   │  │    (drivers)    │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
├─────────────────────────────────────────────────────────────────────────┤
│                            HARDWARE                                      │
│           ARM64 (A-series / M-series chips) + Secure Enclave            │
└─────────────────────────────────────────────────────────────────────────┘
```

### XNU Kernel: гибридная архитектура

```
                        XNU KERNEL INTERNALS
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         BSD LAYER                                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │  VFS     │  │ Sockets  │  │ Processes│  │  Files   │           │ │
│  │  │(filesys) │  │(network) │  │ (fork)   │  │  (I/O)   │           │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│                                  ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        MACH LAYER                                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │  Tasks   │  │ Threads  │  │  Ports   │  │   VM     │           │ │
│  │  │(processes)│  │(execution)│  │  (IPC)   │  │ (memory) │           │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│                                  ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        IOKIT LAYER                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │ Display  │  │ Storage  │  │ Sensors  │  │ Network  │           │ │
│  │  │ driver   │  │  driver  │  │  driver  │  │  driver  │           │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Mach (Carnegie Mellon, 1985):**
- Микроядро — минимальный набор функций
- Tasks (процессы) и Threads (потоки)
- Ports — механизм IPC (inter-process communication)
- Virtual Memory management

**BSD (FreeBSD-derived):**
- POSIX APIs — стандартные Unix системные вызовы
- VFS (Virtual File System) — абстракция файловых систем
- Networking stack — TCP/IP, sockets
- Process model поверх Mach tasks

**IOKit (Apple C++ framework):**
- Объектно-ориентированная модель драйверов
- Hot-plugging устройств
- Power management

### Application Sandbox

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         iOS SANDBOX MODEL                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   App Process                           System Services                  │
│  ┌────────────────┐                   ┌────────────────┐                │
│  │                │                   │                │                │
│  │  Your Code     │ ──── XPC ────────▶│   daemon.d     │                │
│  │                │                   │   (system)     │                │
│  │  Entitlements  │                   └────────────────┘                │
│  │  ┌──────────┐  │                                                     │
│  │  │aps-env  │  │◀─── Only entitled ────                              │
│  │  │icloud   │  │     capabilities                                    │
│  │  │healthkit│  │                                                      │
│  │  └──────────┘  │                                                     │
│  │                │                                                     │
│  │  Sandbox       │                                                     │
│  │  ┌──────────┐  │                                                     │
│  │  │Documents/│  │ ◀── Can read/write                                 │
│  │  │Library/  │  │                                                     │
│  │  │tmp/      │  │                                                     │
│  │  └──────────┘  │                                                     │
│  │                │                                                     │
│  │  ┌──────────┐  │                                                     │
│  │  │ /System/ │  │ ◀── Read-only                                      │
│  │  │ /usr/    │  │                                                     │
│  │  └──────────┘  │                                                     │
│  │                │                                                     │
│  │  ┌──────────┐  │                                                     │
│  │  │Other apps│  │ ◀── No access                                      │
│  │  └──────────┘  │                                                     │
│  └────────────────┘                                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Слои системы в деталях

### Layer 1: Core OS

Самый низкий уровень, ближе всего к hardware.

| Framework | Назначение | Примеры использования |
|-----------|------------|----------------------|
| **Security** | Криптография, Keychain | Хранение паролей, шифрование |
| **Accelerate** | SIMD операции, DSP | Обработка изображений, ML |
| **LocalAuthentication** | Face ID, Touch ID | Биометрическая аутентификация |
| **Core Bluetooth** | BLE коммуникация | Фитнес-трекеры, IoT |
| **System** | POSIX, libc | Низкоуровневые операции |

### Layer 2: Core Services

Фундаментальные сервисы для приложений.

| Framework | Назначение | Swift vs ObjC |
|-----------|------------|---------------|
| **Foundation** | Базовые типы: String, Array, Date | Swift-native |
| **Core Data** | Object graph & persistence | ObjC roots, Swift wrappers |
| **CloudKit** | iCloud sync | Swift-native |
| **Core Location** | GPS, геолокация | Both |
| **Core Motion** | Акселерометр, гироскоп | Both |
| **StoreKit** | In-App Purchases | Swift-native (StoreKit 2) |

### Layer 3: Media

Графика, аудио, видео.

| Framework | Назначение | Performance |
|-----------|------------|-------------|
| **Core Animation** | Layer-based анимации | GPU-accelerated |
| **Core Graphics** | 2D rendering (Quartz) | CPU |
| **Core Image** | Image processing | GPU (Metal) |
| **AVFoundation** | Audio/Video playback | Hardware-accelerated |
| **Metal** | Low-level GPU | Maximum performance |
| **SceneKit/RealityKit** | 3D graphics | GPU |

### Layer 4: Cocoa Touch

Высокоуровневые UI frameworks.

| Framework | Назначение | Paradigm |
|-----------|------------|----------|
| **UIKit** | UI компоненты (classic) | Imperative |
| **SwiftUI** | UI компоненты (modern) | Declarative |
| **MapKit** | Карты | Both |
| **WebKit** | Web content | Imperative |
| **NotificationCenter** | Push/Local notifications | Both |

---

## Распространённые ошибки

### ❌ Ошибка 1: Использование низкоуровневых APIs без необходимости

**Симптом:** Код сложный, много boilerplate, сложно поддерживать

```swift
// ❌ ПЛОХО: Core Foundation для простых операций
import CoreFoundation

let cfString = "Hello" as CFString
let cfMutable = CFStringCreateMutableCopy(nil, 0, cfString)
CFStringAppend(cfMutable, " World" as CFString)
let result = cfMutable as String
```

```swift
// ✅ ХОРОШО: Foundation (высокоуровневый API)
let result = "Hello" + " World"
```

**Решение:** Используй высокоуровневые APIs (Foundation, UIKit) когда возможно. Низкоуровневые (Core Foundation, Security) — только для специфичных задач.

### ❌ Ошибка 2: Игнорирование entitlements

**Симптом:** Функция не работает в production, хотя работала в development

```swift
// ❌ ПЛОХО: Код использует push без entitlement
UNUserNotificationCenter.current().requestAuthorization { granted, error in
    // Работает в simulator, fails на устройстве без entitlement
}
```

```swift
// ✅ ХОРОШО: Проверяем capabilities перед использованием
// 1. Добавить aps-environment entitlement в Xcode
// 2. Проверять состояние
UNUserNotificationCenter.current().getNotificationSettings { settings in
    guard settings.authorizationStatus == .authorized else {
        // Handle not authorized
        return
    }
}
```

**Решение:** Всегда добавляй required entitlements в Xcode Capabilities.

### ❌ Ошибка 3: Непонимание sandbox ограничений

**Симптом:** App не может прочитать файлы, хотя путь правильный

```swift
// ❌ ПЛОХО: Попытка читать вне sandbox
let path = "/var/mobile/Library/SMS/sms.db"
let data = try? Data(contentsOf: URL(fileURLWithPath: path))
// data = nil, нет доступа
```

```swift
// ✅ ХОРОШО: Работа внутри sandbox
let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
let fileURL = documentsURL.appendingPathComponent("data.json")
let data = try? Data(contentsOf: fileURL)
```

**Решение:** Используй только sandbox directories: Documents/, Library/, tmp/

### ❌ Ошибка 4: Вызов C APIs без понимания memory management

**Симптом:** Memory leaks или crashes

```swift
// ❌ ПЛОХО: Утечка памяти с Core Foundation
func createCGImage() -> CGImage {
    let colorSpace = CGColorSpaceCreateDeviceRGB() // Retains
    // ...
    // colorSpace не освобождается — leak!
}
```

```swift
// ✅ ХОРОШО: Swift автоматически управляет CF types
func createCGImage() -> CGImage? {
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    // Swift автоматически вызывает release при выходе из scope
    // если вернуть — ownership передаётся caller
}
```

**Решение:** Swift автоматически bridge-ит Core Foundation types. Но при работе с unmanaged types — используй `.takeRetainedValue()` или `.takeUnretainedValue()`.

### ❌ Ошибка 5: Синхронные операции на Main Thread

**Симптом:** UI freeze при работе с файлами/сетью

```swift
// ❌ ПЛОХО: Синхронное чтение большого файла на Main Thread
@IBAction func loadData() {
    let data = try! Data(contentsOf: largeFileURL) // Блокирует UI
    process(data)
}
```

```swift
// ✅ ХОРОШО: Async на background queue
@IBAction func loadData() {
    Task {
        let data = try await loadDataFromDisk()
        await MainActor.run {
            process(data)
        }
    }
}

func loadDataFromDisk() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        DispatchQueue.global().async {
            do {
                let data = try Data(contentsOf: largeFileURL)
                continuation.resume(returning: data)
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
}
```

### ❌ Ошибка 6: Жёсткая привязка к iOS версии

**Симптом:** Crash на старых устройствах

```swift
// ❌ ПЛОХО: Использование нового API без проверки
let appearance = UINavigationBarAppearance() // iOS 13+ only
// Crash на iOS 12
```

```swift
// ✅ ХОРОШО: Проверка доступности
if #available(iOS 13.0, *) {
    let appearance = UINavigationBarAppearance()
    // Use new API
} else {
    // Fallback for older versions
}
```

---

## Ментальные модели

### 1. Думай слоями

Каждый слой — абстракция над нижним:
- **Хочешь максимальный контроль?** → Core OS, C APIs
- **Хочешь продуктивность?** → Cocoa Touch, Swift APIs
- **Хочешь баланс?** → Core Services, Foundation

### 2. Думай sandbox-first

Всё, что приложение делает — внутри sandbox:
- Файлы = только свои directories
- Сеть = через system APIs
- Hardware = через frameworks с entitlements

### 3. Думай framework selection

Выбор framework определяет:
- **Performance:** Metal > Core Graphics > UIKit
- **Complexity:** Metal > Core Graphics > UIKit
- **Maintainability:** UIKit > Core Graphics > Metal

### 4. Думай API Evolution

Apple постоянно добавляет высокоуровневые APIs:
- Core Foundation (C) → Foundation (ObjC) → Swift Standard Library
- UIKit → SwiftUI
- GCD → async/await

### 5. Думай security by design

iOS архитектура — security-first:
- Sandbox = defense in depth
- Entitlements = principle of least privilege
- Keychain = secure storage by default

---

## Когда использовать

### Низкоуровневые APIs (Core OS)

✅ **Используй когда:**
- Нужен максимальный performance (Accelerate, Metal)
- Работаешь с hardware напрямую (Core Bluetooth)
- Криптография (Security framework)

❌ **Не используй когда:**
- Есть высокоуровневая альтернатива
- Performance не критичен

### Framework Selection Guide

| Задача | Рекомендуемый framework | Альтернатива |
|--------|------------------------|--------------|
| UI (new project) | SwiftUI | UIKit |
| UI (existing) | UIKit | SwiftUI (partial) |
| 2D Graphics | Core Graphics | SwiftUI Canvas |
| 3D Graphics | RealityKit | SceneKit, Metal |
| Networking | URLSession | async/await wrappers |
| Data persistence | SwiftData (iOS 17+) | Core Data |
| Location | Core Location | - |
| Audio | AVFoundation | Core Audio (advanced) |

---

## Проверь себя

<details>
<summary>1. Из каких частей состоит XNU kernel?</summary>

**Ответ:** XNU = Mach + BSD + IOKit
- **Mach:** микроядро (tasks, threads, ports, VM)
- **BSD:** Unix APIs (VFS, sockets, processes)
- **IOKit:** драйверы устройств (C++ framework)

</details>

<details>
<summary>2. Почему приложение не может читать файлы другого приложения?</summary>

**Ответ:** Sandbox isolation. Каждое приложение работает в изолированной среде со своими директориями. Доступ к другим приложениям невозможен на уровне kernel. Исключение: App Groups с shared container (требует entitlement).

</details>

<details>
<summary>3. В чём разница между Foundation и Core Foundation?</summary>

**Ответ:**
- **Core Foundation:** C API, низкоуровневый, toll-free bridged с Foundation ObjC types
- **Foundation:** ObjC/Swift API, высокоуровневый, удобнее использовать

Swift автоматически bridge-ит CF types в Swift types. Используй Foundation если не нужен specific C API.

</details>

---

## Связь с другими темами

**[[ios-app-components]]** — Компоненты iOS-приложения (UIApplication, AppDelegate, SceneDelegate) работают поверх архитектурных слоёв Darwin/XNU, описанных в данной заметке. Понимание того, как Cocoa Touch абстрагирует Core OS и Core Services, объясняет ограничения sandbox-модели и почему приложения не могут напрямую обращаться к ядру. Рекомендуется сначала изучить системную архитектуру, затем переходить к компонентам приложения.

**[[ios-process-memory]]** — Управление памятью в iOS (ARC, virtual memory, jetsam) реализовано на уровне XNU kernel через Mach VM subsystem. Знание архитектуры ядра объясняет, почему iOS агрессивно убивает suspended apps при нехватке памяти и как работает memory pressure notification system. Изучите архитектуру системы для понимания «почему», затем переходите к практическому управлению памятью.

**[[android-architecture]]** — Сравнение архитектур iOS (Darwin/XNU, монолитный гибрид Mach+BSD) и Android (Linux kernel, HAL, Android Runtime) выявляет принципиальные различия в подходах к безопасности, управлению процессами и доступу к hardware. iOS использует закрытую экосистему с sandbox и entitlements, тогда как Android предоставляет более открытую модель с intent-based IPC. Параллельное изучение формирует глубокое понимание мобильных платформ.

---

## Источники

- [Apple's Darwin OS and XNU Kernel Deep Dive](https://tansanrao.com/blog/2025/04/xnu-kernel-and-darwin-evolution-and-architecture/)
- [iOS: The System Architecture - DEV Community](https://dev.to/hmcodes/ios-the-system-architecture-3hmm)
- [Apple Open Source - XNU](https://github.com/apple-oss-distributions/xnu)
- [Apple Developer Documentation - System Architecture](https://developer.apple.com/documentation/technologies)

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — описывает архитектуру iOS с точки зрения разработчика, включая слои системы и роль каждого фреймворка
- Levin J. (2016). *Mac OS X and iOS Internals: To the Apple's Core.* — глубокое погружение в XNU kernel, Mach subsystem, BSD layer и IOKit, необходимое для системного понимания платформы
- Apple (2023). *The Swift Programming Language.* — официальная документация языка, на котором построены все верхние слои iOS-архитектуры

---

*Проверено: 2026-01-11*
