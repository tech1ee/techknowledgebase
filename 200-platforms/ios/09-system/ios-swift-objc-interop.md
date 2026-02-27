---
title: "iOS Swift-Objective-C Interop: bridging, @objc, runtime"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 72
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/interop
  - level/advanced
related:
  - "[[kotlin-interop]]"
  - "[[cross-interop]]"
  - "[[ffi-foreign-function-interface]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-compilation-pipeline]]"
  - "[[ios-app-components]]"
---

# iOS Swift-Objective-C Interop

## TL;DR

Swift и Objective-C могут работать вместе в одном проекте благодаря механизмам интеропа: Bridging Header позволяет Swift видеть ObjC код, а сгенерированный `-Swift.h` header делает Swift доступным для ObjC. Objective-C Runtime обеспечивает динамическую диспетчеризацию, которую Swift использует через атрибут `@objc`, что критично для KVO, селекторов и работы с legacy-кодом.

---

## Теоретические основы

> **Language Interoperability** (интероп) — способность кода на одном языке вызывать код на другом языке в рамках единого процесса. Swift-ObjC interop реализует **bidirectional FFI** (Foreign Function Interface): Swift может вызывать Objective-C через bridging header, а Objective-C может вызывать Swift через generated header (-Swift.h).

### Академический контекст

Интероп между Swift и Objective-C основан на фундаментальных концепциях языковых runtime:

| Концепция | Автор / год | Суть | Проявление в Swift-ObjC interop |
|-----------|-------------|------|----------------------------------|
| Foreign Function Interface | Различные, 1980-е | Вызов функций между языками | Bridging Header (ObjC→Swift), -Swift.h (Swift→ObjC) |
| Dynamic Dispatch | Smalltalk (Kay, 1972) | Метод определяется в runtime через message passing | objc_msgSend, @objc атрибут, #selector |
| Static vs Dynamic Typing | Кардинальное различие | Проверка типов на этапе компиляции vs runtime | Swift (static) ↔ ObjC (dynamic); bridging конвертирует |
| Name Mangling | C++ (1980-е) | Кодирование сигнатуры в имени символа | Swift name mangling vs ObjC flat naming |
| Runtime Reflection | Smalltalk, CLOS | Самоанализ типов в runtime | ObjC Runtime (class_getName, method_getImplementation) |

### Два мира: Static Swift vs Dynamic Objective-C

| Аспект | Swift | Objective-C |
|--------|-------|-------------|
| Dispatch | Static (vtable) по умолчанию | Dynamic (objc_msgSend) всегда |
| Типизация | Static, compile-time | Dynamic, runtime (id) |
| Nullability | Optional<T> — часть типа | Nullable/Nonnull — аннотации |
| ARC | Compile-time (SIL-оптимизации) | Compile-time (но с dynamic overhead) |
| Generics | Monomorphization + type erasure | Нет (NSArray, NSDictionary — untyped) |
| Метапрограммирование | Macros (compile-time) | Runtime: method swizzling, KVO |

> **Ключевой компромисс**: @objc атрибут «понижает» Swift до динамической диспетчеризации ObjC Runtime, теряя преимущества статической оптимизации (inlining, devirtualization). Это необходимая цена за совместимость с UIKit (target-action, KVO, NSNotification), который построен на ObjC Runtime message passing.

### Связь с CS-фундаментом

- [[ios-compilation-pipeline]] — bridging на этапе компиляции: ClangImporter для ObjC
- [[ios-app-components]] — UIKit API требует @objc для target-action, KVO, selectors
- [[ffi-foreign-function-interface]] — общая теория FFI между языками
- [[kotlin-interop]] — Kotlin-Java interop как аналогичная проблема на Android
- [[ios-process-memory]] — ARC в Swift vs ARC в ObjC: различия в оптимизации

---

## Зачем это нужно?

### Legacy-код и постепенная миграция

```
Реальность iOS-разработки:
+--------------------------------------------------+
|  Новые фичи на Swift    |  Старый код на ObjC    |
|  (SwiftUI, Combine)     |  (годы разработки)     |
+-------------------------+------------------------+
          |                         |
          +--- Должны работать вместе ---+
```

**Причины использования интеропа:**

1. **Огромная кодовая база** - переписать всё невозможно
2. **Проверенный код** - ObjC код работает годами
3. **Постепенная миграция** - новые фичи на Swift
4. **Сторонние библиотеки** - многие всё ещё на ObjC
5. **Apple frameworks** - внутри много ObjC

### Где без интеропа не обойтись

```swift
// Target-Action паттерн требует @objc
button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)

@objc func buttonTapped() { } // Без @objc - ошибка компиляции

// KVO требует dynamic dispatch
@objc dynamic var name: String = ""

// Notification selectors
NotificationCenter.default.addObserver(
    self,
    selector: #selector(handleNotification),
    name: .someNotification,
    object: nil
)
```

---

## Аналогии из жизни

### 1. Bridging Header = Переводчик между странами

```
+-------------------+     +------------------+     +-------------------+
|                   |     |                  |     |                   |
|   SWIFT-ЛЕНД     |<--->|   ПЕРЕВОДЧИК    |<--->|   OBJC-ЛЕНД      |
|   (говорит Swift) |     |   (Bridging     |     |   (говорит ObjC)  |
|                   |     |    Header)       |     |                   |
+-------------------+     +------------------+     +-------------------+

Переводчик (Bridging Header):
- Знает оба языка
- Переводит объявления ObjC → Swift
- Один на весь проект
- Должен знать ВСЕ ObjC классы, которые нужны Swift
```

### 2. @objc = Паспорт для Swift-кода в мир ObjC

```
┌─────────────────────────────────────────────────────────────┐
│                        ПАСПОРТ (@objc)                       │
├─────────────────────────────────────────────────────────────┤
│  Владелец: func calculateTotal()                            │
│  Гражданство: Swift                                          │
│  Виза: Objective-C Runtime                                   │
│                                                              │
│  Права:                                                      │
│  ✓ Вызов через селектор                                     │
│  ✓ Участие в KVO/KVC                                        │
│  ✓ Target-Action                                             │
│  ✓ Видимость из ObjC кода                                   │
└─────────────────────────────────────────────────────────────┘

Без паспорта (@objc) Swift-функция:
- Невидима для ObjC Runtime
- Не может быть селектором
- Не участвует в динамической диспетчеризации
```

### 3. ObjC Runtime = Посольство

```
                    ┌─────────────────────────────┐
                    │    ПОСОЛЬСТВО               │
                    │    (Objective-C Runtime)    │
                    ├─────────────────────────────┤
                    │                             │
                    │  📋 Реестр классов          │
                    │     - Регистрация           │
                    │     - Поиск по имени        │
                    │                             │
                    │  📝 Реестр методов          │
                    │     - Селекторы             │
                    │     - Implementations       │
                    │                             │
                    │  🔄 Услуги                  │
                    │     - Method swizzling      │
                    │     - Associated objects    │
                    │     - Message forwarding    │
                    │                             │
                    └─────────────────────────────┘

В посольстве можно:
1. Зарегистрировать новый класс (objc_allocateClassPair)
2. Найти класс по имени (NSClassFromString)
3. Поменять метод местами (method_exchangeImplementations)
4. Прикрепить данные к объекту (objc_setAssociatedObject)
```

### 4. Name Mangling = Транслитерация имени

```
Swift имя:                 Mangled имя (внутреннее):
─────────────────────────────────────────────────────
func greet()           →  _$s7MyApp4UserC5greetyyF
                          │ │  │   │  │ │    │
                          │ │  │   │  │ │    └─ F = function
                          │ │  │   │  │ └───── yy = () -> ()
                          │ │  │   │  └─────── greet
                          │ │  │   └────────── User class
                          │ │  └────────────── 7 символов
                          │ └───────────────── MyApp module
                          └─────────────────── Swift prefix

Как "Армен" транслитерируется в "Armen" в загранпаспорте,
так Swift имена "транслитерируются" для линкера.

@objc сохраняет читаемое имя для ObjC Runtime!
```

### 5. NS_SWIFT_NAME = Предпочтительное имя в другой стране

```
┌─────────────────────────────────────────────────────────┐
│  В Objective-C меня зовут:                               │
│  + (instancetype)colorWithRed:green:blue:alpha:         │
│                                                          │
│  Но в Swift я предпочитаю:                              │
│  init(red:green:blue:alpha:)                            │
│                                                          │
│  NS_SWIFT_NAME(init(red:green:blue:alpha:))             │
└─────────────────────────────────────────────────────────┘

Аналогия:
- В России: Александр
- В США: Alex
- NS_SWIFT_NAME("Alex") - официальное предпочтительное имя
```

---

## Архитектура интеропа

### Общая схема

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           iOS PROJECT                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌─────────────────┐         ┌─────────────────┐                        │
│   │  Swift Files    │         │  ObjC Files     │                        │
│   │  *.swift        │         │  *.h / *.m      │                        │
│   └────────┬────────┘         └────────┬────────┘                        │
│            │                           │                                  │
│            ▼                           ▼                                  │
│   ┌─────────────────────────────────────────────────────┐                │
│   │              Compiler Infrastructure                 │                │
│   ├─────────────────────────────────────────────────────┤                │
│   │                                                      │                │
│   │   Swift → ObjC:                ObjC → Swift:        │                │
│   │   ┌──────────────┐            ┌──────────────┐      │                │
│   │   │ Module-      │            │ Bridging-    │      │                │
│   │   │ Swift.h      │            │ Header.h     │      │                │
│   │   │ (generated)  │            │ (manual)     │      │                │
│   │   └──────────────┘            └──────────────┘      │                │
│   │                                                      │                │
│   └─────────────────────────────────────────────────────┘                │
│                              │                                            │
│                              ▼                                            │
│   ┌─────────────────────────────────────────────────────┐                │
│   │              Objective-C Runtime                     │                │
│   │  - Dynamic dispatch                                  │                │
│   │  - Message sending                                   │                │
│   │  - Class/method registry                            │                │
│   └─────────────────────────────────────────────────────┘                │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Детальная схема взаимодействия

```
                    SWIFT CODE                    OBJECTIVE-C CODE
                    ==========                    ================
                        │                               │
                        │ uses                          │ uses
                        ▼                               ▼
            ┌───────────────────┐           ┌───────────────────┐
            │ Import ObjC       │           │ Import Swift      │
            │ (Bridging Header) │           │ (Generated Header)│
            │                   │           │                   │
            │ #import "Foo.h"   │           │ #import           │
            │ #import "Bar.h"   │           │ "Module-Swift.h"  │
            └─────────┬─────────┘           └─────────┬─────────┘
                      │                               │
                      │ exposes                       │ exposes
                      ▼                               ▼
            ┌───────────────────┐           ┌───────────────────┐
            │ ObjC API          │           │ Swift API         │
            │ as Swift types    │           │ marked with @objc │
            │                   │           │                   │
            │ - NSString → String           │ - Classes         │
            │ - NSArray → [Any] │           │ - @objc methods   │
            │ - Blocks → Closures           │ - @objc properties│
            └───────────────────┘           └───────────────────┘
```

### Module Maps

```
┌─────────────────────────────────────────────────────────────┐
│                       module.modulemap                       │
├─────────────────────────────────────────────────────────────┤
│  module MyFramework {                                        │
│      umbrella header "MyFramework.h"                        │
│                                                              │
│      export *                                                │
│      module * { export * }                                   │
│  }                                                           │
├─────────────────────────────────────────────────────────────┤
│  Что это делает:                                            │
│  1. Объявляет модуль с именем MyFramework                   │
│  2. Указывает umbrella header (главный header)              │
│  3. Экспортирует все символы                                │
│  4. Позволяет Swift делать: import MyFramework              │
└─────────────────────────────────────────────────────────────┘

Без module map Swift не может импортировать ObjC framework!
```

---

## Bridging Header

### Что это такое

```
Bridging Header - это специальный .h файл, который служит
"мостом" для импорта Objective-C кода в Swift.

┌─────────────────────────────────────────────────────────────┐
│              ProjectName-Bridging-Header.h                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  // ObjC frameworks                                          │
│  #import <SomeFramework/SomeFramework.h>                    │
│                                                              │
│  // ObjC headers from your project                          │
│  #import "LegacyNetworkManager.h"                           │
│  #import "OldDataModel.h"                                   │
│  #import "ThirdPartyLibrary.h"                              │
│                                                              │
│  // C headers                                                │
│  #import "pure_c_library.h"                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Создание Bridging Header

```
Способ 1: Автоматически
─────────────────────────
1. Добавить .m файл в Swift-проект
2. Xcode спросит: "Create Bridging Header?"
3. Нажать "Create"

Способ 2: Вручную
─────────────────────────
1. File → New → Header File
2. Назвать: "ProjectName-Bridging-Header.h"
3. Build Settings → "Objective-C Bridging Header"
4. Указать путь: "$(SRCROOT)/ProjectName-Bridging-Header.h"
```

### Что импортировать

```objc
// ProjectName-Bridging-Header.h

// ✅ ПРАВИЛЬНО - импортировать:

// 1. Ваши ObjC классы
#import "NetworkManager.h"
#import "DataParser.h"

// 2. Сторонние ObjC библиотеки
#import <AFNetworking/AFNetworking.h>
#import <SDWebImage/SDWebImage.h>

// 3. C библиотеки
#import <CommonCrypto/CommonCrypto.h>
#import "sqlite3.h"

// ❌ НЕПРАВИЛЬНО - НЕ импортировать:

// Системные Swift-совместимые frameworks (используйте import в Swift)
// #import <Foundation/Foundation.h>  // Не нужно!
// #import <UIKit/UIKit.h>            // Не нужно!
```

### Build Settings

```
Build Settings для Bridging Header:

┌─────────────────────────────────────────────────────────────┐
│  Objective-C Bridging Header                                │
│  ──────────────────────────────────────────────────────────│
│  $(SRCROOT)/MyApp/MyApp-Bridging-Header.h                  │
├─────────────────────────────────────────────────────────────┤
│  Install Objective-C Compatibility Header                   │
│  ──────────────────────────────────────────────────────────│
│  YES (для framework targets)                                │
├─────────────────────────────────────────────────────────────┤
│  Objective-C Generated Interface Header Name                │
│  ──────────────────────────────────────────────────────────│
│  $(SWIFT_MODULE_NAME)-Swift.h                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Вызов Objective-C из Swift

### Nullability Annotations

```objc
// Objective-C Header

// Без аннотаций - всё становится ImplicitlyUnwrappedOptional
@interface User : NSObject
@property (nonatomic, copy) NSString *name;        // String! в Swift
- (NSArray *)friends;                               // [Any]! в Swift
@end

// С аннотациями - точные типы в Swift
@interface User : NSObject
@property (nonatomic, copy, nonnull) NSString *name;      // String
@property (nonatomic, copy, nullable) NSString *email;    // String?
- (nonnull NSArray<User *> *)friends;                     // [User]
- (nullable User *)bestFriend;                            // User?
@end
```

```swift
// Swift использование
let user = User()
let name: String = user.name           // Не optional!
let email: String? = user.email        // Optional
let friends: [User] = user.friends()   // Типизированный массив
```

### NS_ASSUME_NONNULL

```objc
// Вместо аннотации каждого свойства:

NS_ASSUME_NONNULL_BEGIN

@interface APIClient : NSObject

// Все указатели nonnull по умолчанию
@property (nonatomic, copy) NSString *baseURL;
@property (nonatomic, copy) NSString *apiKey;

// Явно указываем nullable
@property (nonatomic, copy, nullable) NSString *authToken;

- (void)fetchDataWithCompletion:(void (^)(NSData *data, NSError * _Nullable error))completion;

@end

NS_ASSUME_NONNULL_END
```

### Lightweight Generics

```objc
// Objective-C с generics
@interface DataStore<ObjectType> : NSObject

@property (nonatomic, strong) NSArray<ObjectType> *items;
@property (nonatomic, strong) NSDictionary<NSString *, ObjectType> *itemsByID;

- (void)addItem:(ObjectType)item;
- (nullable ObjectType)itemWithID:(NSString *)itemID;

@end

// Конкретный тип
@interface UserStore : DataStore<User *>
@end
```

```swift
// Swift видит типизированные коллекции
let store = UserStore()
let items: [User] = store.items           // [User], не [Any]!
let byID: [String: User] = store.itemsByID
store.addItem(User())                      // Компилятор проверяет тип
```

### Blocks → Closures

```objc
// Objective-C blocks
typedef void (^CompletionHandler)(NSData * _Nullable data, NSError * _Nullable error);
typedef BOOL (^FilterBlock)(id item);

@interface NetworkManager : NSObject

- (void)fetchURL:(NSURL *)url completion:(CompletionHandler)completion;
- (NSArray *)filterItems:(NSArray *)items using:(FilterBlock)filter;

@end
```

```swift
// Swift closures - автоматическая конвертация
let manager = NetworkManager()

// Block → Closure
manager.fetchURL(url) { data, error in
    if let error = error {
        print("Error: \(error)")
        return
    }
    // handle data
}

// FilterBlock → (Any) -> Bool
let filtered = manager.filterItems(items) { item in
    guard let user = item as? User else { return false }
    return user.age >= 18
}
```

### Типы конвертации

```
┌──────────────────────┬──────────────────────┐
│    Objective-C       │       Swift          │
├──────────────────────┼──────────────────────┤
│ NSString             │ String               │
│ NSArray              │ [Any]                │
│ NSArray<NSString *>  │ [String]             │
│ NSDictionary         │ [AnyHashable: Any]   │
│ NSSet                │ Set<AnyHashable>     │
│ NSNumber             │ NSNumber (or Int/etc)│
│ NSData               │ Data                 │
│ NSDate               │ Date                 │
│ NSURL                │ URL                  │
│ NSError              │ Error (protocol)     │
│ id                   │ Any                  │
│ Class                │ AnyClass             │
│ SEL                  │ Selector             │
│ BOOL                 │ Bool                 │
│ int, NSInteger       │ Int                  │
│ float                │ Float                │
│ double               │ Double               │
│ void (^)(void)       │ () -> Void           │
└──────────────────────┴──────────────────────┘
```

---

## Вызов Swift из Objective-C

### @objc Attribute

```swift
// Swift класс доступный из ObjC

// Класс должен наследоваться от NSObject (или @objc class)
class NetworkService: NSObject {

    // @objc делает метод видимым для ObjC
    @objc func fetchData() {
        // ...
    }

    // @objc с кастомным именем
    @objc(fetchDataWithURL:completion:)
    func fetchData(url: URL, completion: @escaping (Data?) -> Void) {
        // ...
    }

    // @objc для свойств
    @objc var isLoading: Bool = false

    // @objc dynamic для KVO
    @objc dynamic var progress: Double = 0.0

    // Приватный для ObjC (без @objc)
    func internalMethod() {
        // Не видно из ObjC
    }
}
```

### @objcMembers

```swift
// Все члены автоматически @objc
@objcMembers
class User: NSObject {
    var name: String = ""           // автоматически @objc
    var age: Int = 0                // автоматически @objc

    func greet() { }                // автоматически @objc
    func calculateAge() -> Int { 0 } // автоматически @objc

    // Явно исключить из ObjC
    @nonobjc func swiftOnlyMethod() { }

    // Private всё ещё приватный
    private func privateMethod() { }
}

// В ObjC:
// User *user = [[User alloc] init];
// user.name = @"John";
// [user greet];
```

### ProductModule-Swift.h

```objc
// Objective-C файл

// Импорт сгенерированного header
#import "MyApp-Swift.h"  // или <MyFramework/MyFramework-Swift.h>

@implementation LegacyController

- (void)useSomeSwiftCode {
    // Создание Swift объекта
    NetworkService *service = [[NetworkService alloc] init];

    // Вызов метода
    [service fetchData];

    // Доступ к свойствам
    service.isLoading = YES;

    // KVO работает благодаря @objc dynamic
    [service addObserver:self
              forKeyPath:@"progress"
                 options:NSKeyValueObservingOptionNew
                 context:nil];
}

@end
```

### Ограничения (что недоступно в ObjC)

```swift
// ❌ Generics - НЕ доступны в ObjC
class Container<T> {
    var item: T?
}

// ❌ Structs - НЕ доступны в ObjC
struct Point {
    var x: Double
    var y: Double
}

// ❌ Enums без Int raw value - НЕ доступны в ObjC
enum Direction {
    case north, south, east, west
}

// ✅ Enums с @objc и Int raw value - ДОСТУПНЫ
@objc enum Status: Int {
    case pending = 0
    case active = 1
    case completed = 2
}

// ❌ Protocol extensions - НЕ доступны
// ❌ Tuples - НЕ доступны
// ❌ Swift-only types (Int?, optionals with non-ObjC types) - НЕ доступны
// ❌ Nested types - НЕ доступны
// ❌ Global functions - НЕ доступны
// ❌ Type aliases - НЕ доступны
// ❌ Swift-style error handling - НЕ доступны (используйте NSError)
```

```swift
// Workarounds для ограничений

// Struct → Class wrapper
struct UserData {
    var name: String
    var age: Int
}

@objc class UserDataWrapper: NSObject {
    @objc var name: String
    @objc var age: Int

    init(data: UserData) {
        self.name = data.name
        self.age = data.age
    }

    var swiftValue: UserData {
        UserData(name: name, age: age)
    }
}

// Complex enum → Int enum + extension
@objc enum PaymentStatus: Int {
    case pending, processing, completed, failed
}

extension PaymentStatus {
    var description: String {
        switch self {
        case .pending: return "Pending"
        case .processing: return "Processing"
        case .completed: return "Completed"
        case .failed: return "Failed"
        }
    }
}
```

---

## Objective-C Runtime

### Dynamic Dispatch

```
┌─────────────────────────────────────────────────────────────┐
│              Static vs Dynamic Dispatch                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Swift (по умолчанию):          ObjC / @objc dynamic:       │
│  ┌─────────────────────┐        ┌─────────────────────┐     │
│  │ STATIC DISPATCH     │        │ DYNAMIC DISPATCH    │     │
│  │                     │        │                     │     │
│  │ Компилятор знает    │        │ Runtime ищет        │     │
│  │ точный адрес        │        │ implementation      │     │
│  │ функции             │        │ в момент вызова     │     │
│  │                     │        │                     │     │
│  │ call 0x12345678     │        │ objc_msgSend(       │     │
│  │                     │        │   obj, @selector,   │     │
│  │ БЫСТРО              │        │   args...)          │     │
│  │ Нет overhead        │        │                     │     │
│  │ Inlining возможен   │        │ ГИБКО               │     │
│  └─────────────────────┘        │ Method swizzling    │     │
│                                 │ KVO возможен        │     │
│                                 └─────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

```swift
// Swift dispatch types

class Animal {
    // Table dispatch (vtable) - для классов по умолчанию
    func speak() { }
}

class Dog: Animal {
    override func speak() { print("Woof") }
}

final class Cat: Animal {
    // Direct dispatch - final класс, компилятор знает точный тип
    override func speak() { print("Meow") }
}

class Observable: NSObject {
    // Message dispatch - ObjC runtime
    @objc dynamic var value: Int = 0
}
```

### Method Swizzling

```swift
import ObjectiveC

// Подмена реализации метода в runtime

extension UIViewController {

    // Выполняется один раз при загрузке класса
    static let swizzleViewDidAppear: Void = {
        let originalSelector = #selector(viewDidAppear(_:))
        let swizzledSelector = #selector(swizzled_viewDidAppear(_:))

        guard let originalMethod = class_getInstanceMethod(UIViewController.self, originalSelector),
              let swizzledMethod = class_getInstanceMethod(UIViewController.self, swizzledSelector)
        else { return }

        // Подменяем реализации
        method_exchangeImplementations(originalMethod, swizzledMethod)
    }()

    @objc func swizzled_viewDidAppear(_ animated: Bool) {
        // Вызываем оригинальный метод (теперь он под swizzled selector!)
        swizzled_viewDidAppear(animated)

        // Наш дополнительный код
        print("Screen appeared: \(type(of: self))")
        Analytics.trackScreen(String(describing: type(of: self)))
    }
}

// Активация swizzling
// В AppDelegate или SceneDelegate:
_ = UIViewController.swizzleViewDidAppear
```

### Associated Objects

```swift
import ObjectiveC

// Добавление свойств к существующим классам через Runtime

private var customDataKey: UInt8 = 0

extension UIView {

    var customData: [String: Any]? {
        get {
            objc_getAssociatedObject(self, &customDataKey) as? [String: Any]
        }
        set {
            objc_setAssociatedObject(
                self,
                &customDataKey,
                newValue,
                .OBJC_ASSOCIATION_RETAIN_NONATOMIC
            )
        }
    }
}

// Использование
let view = UIView()
view.customData = ["key": "value"]
print(view.customData?["key"])  // "value"
```

```
Association Policies:
┌────────────────────────────────────┬───────────────────────────────┐
│ Policy                             │ Эквивалент в @property        │
├────────────────────────────────────┼───────────────────────────────┤
│ OBJC_ASSOCIATION_ASSIGN            │ assign (weak без zeroing)     │
│ OBJC_ASSOCIATION_RETAIN_NONATOMIC  │ strong, nonatomic             │
│ OBJC_ASSOCIATION_COPY_NONATOMIC    │ copy, nonatomic               │
│ OBJC_ASSOCIATION_RETAIN            │ strong, atomic                │
│ OBJC_ASSOCIATION_COPY              │ copy, atomic                  │
└────────────────────────────────────┴───────────────────────────────┘
```

### KVO/KVC

```swift
// Key-Value Observing требует @objc dynamic

class DataModel: NSObject {
    @objc dynamic var count: Int = 0
    @objc dynamic var name: String = ""
    @objc dynamic var items: [String] = []
}

class Observer: NSObject {
    var observation: NSKeyValueObservation?

    func observe(model: DataModel) {
        // Современный API с замыканием
        observation = model.observe(\.count, options: [.new, .old]) { object, change in
            print("Count changed from \(change.oldValue ?? 0) to \(change.newValue ?? 0)")
        }

        // Для массивов - специальные методы
        model.mutableArrayValue(forKey: "items").add("New Item")
    }
}

// Key-Value Coding
let model = DataModel()
model.setValue(42, forKey: "count")
let value = model.value(forKey: "count") as? Int  // 42

// Вложенные ключи
model.setValue("Test", forKeyPath: "name")
```

---

## Name Mangling

### Swift Name Mangling

```
Swift компилятор "искажает" имена для:
1. Уникальности символов
2. Кодирования типов
3. Поддержки перегрузки

┌──────────────────────────────────────────────────────────────┐
│ Swift код:                                                   │
│ func greet(name: String) -> String                          │
│                                                              │
│ Mangled имя:                                                │
│ _$s7MyModule5greet4nameS2S_tF                               │
│  │ │  │     │    │ │  │                                      │
│  │ │  │     │    │ │  └─ F = function                       │
│  │ │  │     │    │ └──── t = tuple separator                │
│  │ │  │     │    └────── S2S = String -> String             │
│  │ │  │     └─────────── name (parameter label)             │
│  │ │  └───────────────── greet (function name)              │
│  │ └──────────────────── 7 = MyModule length                │
│  └────────────────────── $s = Swift symbol prefix           │
└──────────────────────────────────────────────────────────────┘
```

### @objc с кастомным именем

```swift
class UserManager: NSObject {

    // Автоматическое имя: userManagerWithID:
    @objc func userManager(withID id: String) -> User? { nil }

    // Явное ObjC имя
    @objc(sharedManager)
    static var shared: UserManager { UserManager() }

    // Подробное кастомное имя
    @objc(fetchUserWithIdentifier:completionHandler:)
    func fetchUser(id: String, completion: @escaping (User?) -> Void) {
        // ...
    }

    // Убираем Swift конвенции для ObjC
    @objc(initWithConfiguration:)
    init(config: Configuration) {
        super.init()
    }
}
```

```objc
// Использование в ObjC:
UserManager *manager = [UserManager sharedManager];
[manager fetchUserWithIdentifier:@"123" completionHandler:^(User *user) {
    // ...
}];
```

### NS_SWIFT_NAME

```objc
// Objective-C API с Swift-friendly именами

// Для методов
@interface ColorFactory : NSObject

+ (UIColor *)colorWithRed:(CGFloat)red
                    green:(CGFloat)green
                     blue:(CGFloat)blue
                    alpha:(CGFloat)alpha
    NS_SWIFT_NAME(color(red:green:blue:alpha:));

// Фабричный метод → init
+ (instancetype)factoryWithName:(NSString *)name
    NS_SWIFT_NAME(init(name:));

// Глобальная функция → статический метод
+ (void)resetAllColors
    NS_SWIFT_NAME(resetAll());

@end

// Для enum
typedef NS_ENUM(NSInteger, NetworkStatus) {
    NetworkStatusUnknown,
    NetworkStatusNotReachable NS_SWIFT_NAME(notReachable),
    NetworkStatusReachableViaWiFi NS_SWIFT_NAME(wifi),
    NetworkStatusReachableViaCellular NS_SWIFT_NAME(cellular),
};

// Для typedef
typedef NSString * ColorName NS_TYPED_EXTENSIBLE_ENUM NS_SWIFT_NAME(Color.Name);

// Для констант
extern ColorName const ColorNameRed NS_SWIFT_NAME(Color.Name.red);
extern ColorName const ColorNameBlue NS_SWIFT_NAME(Color.Name.blue);
```

```swift
// Swift использование:
let color = ColorFactory.color(red: 1, green: 0, blue: 0, alpha: 1)
let factory = ColorFactory(name: "Custom")
ColorFactory.resetAll()

let status: NetworkStatus = .wifi

let colorName: Color.Name = .red
```

---

## Распространённые ошибки

### Ошибка 1: Забыли @objc для selector

```swift
// ❌ НЕПРАВИЛЬНО - крэш в runtime
class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let button = UIButton()
        button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)
    }

    func buttonTapped() {  // Ошибка: нет @objc
        print("Tapped")
    }
}

// ✅ ПРАВИЛЬНО
class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let button = UIButton()
        button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)
    }

    @objc func buttonTapped() {
        print("Tapped")
    }
}
```

### Ошибка 2: KVO без dynamic

```swift
// ❌ НЕПРАВИЛЬНО - KVO не работает
class ViewModel: NSObject {
    @objc var title: String = ""  // Только @objc недостаточно!
}

let vm = ViewModel()
vm.observe(\.title) { _, _ in
    print("Changed")  // Никогда не вызовется!
}
vm.title = "New"

// ✅ ПРАВИЛЬНО
class ViewModel: NSObject {
    @objc dynamic var title: String = ""  // @objc + dynamic
}

let vm = ViewModel()
vm.observe(\.title) { _, _ in
    print("Changed")  // Работает!
}
vm.title = "New"
```

### Ошибка 3: Import Swift header в ObjC header

```objc
// ❌ НЕПРАВИЛЬНО - циклическая зависимость
// MyObjCClass.h
#import "MyApp-Swift.h"  // НЕ импортировать в .h файле!

@interface MyObjCClass : NSObject
@property (nonatomic, strong) MySwiftClass *swiftObject;
@end

// ✅ ПРАВИЛЬНО - forward declaration
// MyObjCClass.h
@class MySwiftClass;  // Forward declaration

@interface MyObjCClass : NSObject
@property (nonatomic, strong) MySwiftClass *swiftObject;
@end

// MyObjCClass.m
#import "MyApp-Swift.h"  // Импорт в .m файле
#import "MyObjCClass.h"

@implementation MyObjCClass
// ...
@end
```

### Ошибка 4: Swift Optional в ObjC

```swift
// ❌ НЕПРАВИЛЬНО - необработанный optional
@objc class User: NSObject {
    @objc var middleName: String?  // ObjC не понимает Swift optionals правильно
}

// В ObjC:
// user.middleName может быть nil, но ObjC не ожидает это

// ✅ ПРАВИЛЬНО - используйте nullable в ObjC или unwrap
@objc class User: NSObject {
    // Вариант 1: Дефолтное значение
    @objc var middleName: String = ""

    // Вариант 2: Computed property с fallback
    private var _middleName: String?
    @objc var middleName: String {
        get { _middleName ?? "" }
        set { _middleName = newValue.isEmpty ? nil : newValue }
    }

    // Вариант 3: Nullable NSString (для сложных случаев)
    @objc var middleNameObjC: NSString? {
        _middleName as NSString?
    }
}
```

### Ошибка 5: Struct в @objc методе

```swift
// ❌ НЕПРАВИЛЬНО - struct нельзя использовать с @objc
struct UserInfo {
    var name: String
    var age: Int
}

@objc class UserService: NSObject {
    @objc func getUser() -> UserInfo {  // Ошибка компиляции!
        return UserInfo(name: "John", age: 30)
    }
}

// ✅ ПРАВИЛЬНО - используйте class или wrapper
@objc class UserInfo: NSObject {
    @objc var name: String
    @objc var age: Int

    @objc init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

@objc class UserService: NSObject {
    @objc func getUser() -> UserInfo {
        return UserInfo(name: "John", age: 30)
    }
}
```

### Ошибка 6: Неправильный module name в import

```objc
// ❌ НЕПРАВИЛЬНО - неверное имя модуля
#import "My-App-Swift.h"      // Дефисы заменяются на underscore
#import "myapp-Swift.h"       // Case sensitive!
#import "MyApp_Swift.h"       // Без -Swift

// ✅ ПРАВИЛЬНО
#import "MyApp-Swift.h"       // Точное имя модуля + "-Swift.h"

// Для framework:
#import <MyFramework/MyFramework-Swift.h>

// Если имя проекта "My App" (с пробелом):
#import "My_App-Swift.h"      // Пробелы → underscore

// Проверить имя модуля:
// Build Settings → Product Module Name
```

---

## Ментальные модели

### 1. Два мира с посольством

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────┐                    ┌──────────────────┐   │
│  │                  │                    │                  │   │
│  │   SWIFT WORLD    │                    │   OBJC WORLD     │   │
│  │                  │                    │                  │   │
│  │  - Статическая   │                    │  - Динамическая  │   │
│  │    типизация     │                    │    типизация     │   │
│  │  - Value types   │    ПОСОЛЬСТВО     │  - Reference     │   │
│  │  - Optionals     │◄──(ObjC Runtime)──►│    types         │   │
│  │  - Generics      │                    │  - Nil messaging │   │
│  │  - Protocol      │                    │  - Categories    │   │
│  │    extensions    │                    │  - KVO/KVC       │   │
│  │                  │                    │                  │   │
│  └──────────────────┘                    └──────────────────┘   │
│                                                                  │
│  Для пересечения границы нужны документы:                       │
│  - Swift → ObjC: @objc (паспорт)                                │
│  - ObjC → Swift: Bridging Header (виза)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Слои абстракции

```
┌─────────────────────────────────────────────────────────────────┐
│                      ВАШ КОД                                     │
│  ┌─────────────┐                    ┌─────────────┐             │
│  │ Swift код   │                    │ ObjC код    │             │
│  └──────┬──────┘                    └──────┬──────┘             │
├─────────┼──────────────────────────────────┼────────────────────┤
│         ▼         МОСТ (INTEROP)           ▼                    │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Bridging Header ◄─────────────► Generated Header │           │
│  │  (вы пишете)                      (Xcode создаёт) │           │
│  └──────────────────────────────────────────────────┘           │
├─────────────────────────────────────────────────────────────────┤
│                   OBJECTIVE-C RUNTIME                            │
│  ┌──────────────────────────────────────────────────┐           │
│  │  - Реестр классов и методов                       │           │
│  │  - Message dispatch (objc_msgSend)                │           │
│  │  - Dynamic method resolution                      │           │
│  │  - Associated objects                             │           │
│  └──────────────────────────────────────────────────┘           │
├─────────────────────────────────────────────────────────────────┤
│                        DARWIN / XNU                              │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Операционная система (macOS, iOS, ...)          │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Конвейер компиляции

```
                        COMPILE TIME
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Swift файлы           ObjC файлы                               │
│       │                     │                                    │
│       ▼                     ▼                                    │
│  ┌─────────┐           ┌─────────┐                              │
│  │ swiftc  │           │ clang   │                              │
│  └────┬────┘           └────┬────┘                              │
│       │                     │                                    │
│       │ ◄── Bridging Header ─┤                                   │
│       │                     │                                    │
│       │ ── Generated Header ─►                                   │
│       │                     │                                    │
│       ▼                     ▼                                    │
│  ┌─────────┐           ┌─────────┐                              │
│  │  .o     │           │  .o     │                              │
│  │ (ARM64) │           │ (ARM64) │                              │
│  └────┬────┘           └────┬────┘                              │
│       │                     │                                    │
│       └─────────┬───────────┘                                    │
│                 ▼                                                │
│            ┌─────────┐                                          │
│            │  LINKER │                                          │
│            └────┬────┘                                          │
│                 ▼                                                │
│            ┌─────────┐                                          │
│            │  .app   │                                          │
│            │ bundle  │                                          │
│            └─────────┘                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                        RUNTIME
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │             OBJECTIVE-C RUNTIME                   │           │
│  │                                                   │           │
│  │  При запуске:                                    │           │
│  │  1. Загрузка dylibs                              │           │
│  │  2. Регистрация классов (+initialize)            │           │
│  │  3. Setup method tables                          │           │
│  │  4. Resolve lazy symbols                         │           │
│  │                                                   │           │
│  │  При вызове @objc метода:                        │           │
│  │  1. objc_msgSend(receiver, selector, args...)    │           │
│  │  2. Lookup в method cache                        │           │
│  │  3. Если miss → поиск в class hierarchy          │           │
│  │  4. Вызов implementation                         │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Типы как валюта

```
┌─────────────────────────────────────────────────────────────────┐
│                    ОБМЕННЫЙ ПУНКТ                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Swift                          ObjC                           │
│   ──────                         ────                           │
│   String        ◄═══ бесплатно ═══►   NSString                  │
│   [Element]     ◄═══ бесплатно ═══►   NSArray                   │
│   [K: V]        ◄═══ бесплатно ═══►   NSDictionary              │
│   Data          ◄═══ бесплатно ═══►   NSData                    │
│   URL           ◄═══ бесплатно ═══►   NSURL                     │
│   Date          ◄═══ бесплатно ═══►   NSDate                    │
│                                                                  │
│   ─────────────────────────────────────────────────────         │
│                                                                  │
│   Int?          ════ ТРЕБУЕТ ════►   NSNumber? (обёртка)        │
│   Struct        ════ НЕВОЗМОЖНО ═►   (нужен class wrapper)      │
│   Enum+assoc    ════ НЕВОЗМОЖНО ═►   (нужен @objc enum)         │
│   Generics      ════ НЕВОЗМОЖНО ═►   (type erasure)             │
│                                                                  │
│   ─────────────────────────────────────────────────────         │
│                                                                  │
│   "Toll-free bridged" типы конвертируются без копирования!      │
│   Foundation типы имеют одинаковое memory layout.               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Dispatch как маршрутизация

```
┌─────────────────────────────────────────────────────────────────┐
│                  МАРШРУТИЗАЦИЯ ВЫЗОВОВ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Вызов метода: object.doSomething()                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              КАК НАЙТИ IMPLEMENTATION?                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│            ┌─────────────┴─────────────┐                        │
│            │                           │                        │
│            ▼                           ▼                        │
│     ┌────────────┐              ┌────────────┐                  │
│     │   STATIC   │              │  DYNAMIC   │                  │
│     │  DISPATCH  │              │  DISPATCH  │                  │
│     └─────┬──────┘              └─────┬──────┘                  │
│           │                           │                         │
│           ▼                           ▼                         │
│    ┌──────────────┐           ┌──────────────┐                  │
│    │ Direct Call  │           │ Table lookup │                  │
│    │              │           │              │                  │
│    │ call 0x1234  │           │  vtable[N]   │                  │
│    │              │           │  или         │                  │
│    │ final class  │           │  protocol    │                  │
│    │ struct       │           │  witness     │                  │
│    │ private      │           │  table       │                  │
│    └──────────────┘           └──────┬───────┘                  │
│                                      │                          │
│                                      ▼                          │
│                              ┌──────────────┐                   │
│                              │   MESSAGE    │                   │
│                              │   DISPATCH   │                   │
│                              │              │                   │
│                              │ objc_msgSend │                   │
│                              │              │                   │
│                              │ @objc dynamic│                   │
│                              │ NSObject     │                   │
│                              └──────────────┘                   │
│                                                                  │
│  Скорость: Static > Table > Message                             │
│  Гибкость: Message > Table > Static                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
---

## Проверь себя

> [!question]- Почему @objc атрибут увеличивает размер бинарника и снижает производительность, и когда его использование неизбежно?
> @objc делает метод/свойство видимым для Objective-C Runtime через message dispatch (objc_msgSend). Это медленнее, чем прямой вызов Swift (vtable/static dispatch). Увеличивает бинарник: генерируется Objective-C metadata. Неизбежно для: #selector (targets/actions, KVO), @IBAction/@IBOutlet, NSObject subclasses, dynamic dispatch для KVO/KVC, совместимость с ObjC frameworks.

> [!question]- Как Bridging Header и Generated Header (-Swift.h) обеспечивают двунаправленный interop?
> Bridging Header (MyApp-Bridging-Header.h): импортирует ObjC headers, делая их доступными в Swift. Один на target. Generated Header (MyApp-Swift.h): автоматически генерируется компилятором, содержит ObjC-совместимые Swift declarations (@objc marked). ObjC файлы импортируют его для доступа к Swift коду. Круг: Swift -> BH -> ObjC, ObjC -> Generated -> Swift.

> [!question]- Сценарий: вы добавляете Swift модуль в legacy ObjC-проект. Какие типичные проблемы interop и как их решить?
> 1) Swift optionals маппятся в nullable ObjC (пустота обязательна в Swift). 2) Swift enum не видны в ObjC без @objc и Int rawValue. 3) Structs, generics, протоколы без @objc не экспортируются. 4) Naming: module-prefix в -Swift.h (MyModule.MyClass). 5) Circular dependency: ObjC header в bridging и Swift в generated -- решается forward declarations (@class, @protocol).

---

## Ключевые карточки

Что такое Bridging Header в Swift/ObjC interop?
?
Файл (ProjectName-Bridging-Header.h), импортирующий ObjC headers для использования в Swift. Один на target. Создается автоматически при первом добавлении ObjC файла в Swift проект (или наоборот). Все imported ObjC типы доступны во всех Swift файлах target без import.

Что делает @objc атрибут в Swift?
?
Делает Swift declaration видимым для Objective-C Runtime. Необходим для: #selector, KVO, @IBAction, target-action, NSObject subclasses. @objc dynamic -- для KVO-совместимости. @objcMembers -- маркирует все members класса. Влияет на dispatch: message dispatch вместо vtable.

Как Swift типы маппятся в Objective-C?
?
String <-> NSString, Array <-> NSArray, Dictionary <-> NSDictionary, Int/Double <-> NSNumber (auto-bridging). Optional -> nullable. Struct, enum (без Int rawValue), generics -- не маппятся (только @objc compatible). Protocol -> @objc protocol. Class -> @objc class.

Что такое Objective-C Runtime и как Swift с ним взаимодействует?
?
Dynamic dispatch system: objc_msgSend для вызова методов по имени (selector). Swift использует для: @objc marked declarations, NSObject subclasses, KVO, method swizzling. Pure Swift типы не используют ObjC Runtime (статический/vtable dispatch), что быстрее.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-compilation-pipeline]] | Как interop влияет на компиляцию |
| Углубиться | [[ios-app-components]] | Runtime и lifecycle ObjC-совместимых компонентов |
| Смежная тема | [[kotlin-interop]] | Kotlin/Java interop для сравнения подходов |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
