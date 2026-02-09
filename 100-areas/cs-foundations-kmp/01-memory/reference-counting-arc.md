---
title: "Reference Counting и ARC: как Swift управляет памятью"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, memory, arc, swift, kotlin-native, ios]
related:
  - "[[memory-model-fundamentals]]"
  - "[[garbage-collection-explained]]"
---

# Reference Counting и ARC: как Swift управляет памятью

> **TL;DR:** Reference Counting — подсчёт ссылок на объект: когда count = 0, объект удаляется. ARC (Automatic Reference Counting) в Swift автоматизирует этот процесс. Главная ловушка — retain cycles: объекты ссылаются друг на друга и никогда не освобождаются. Решение — weak и unowned ссылки. Для KMP критично: Kotlin/Native интегрируется с ARC при работе с iOS.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Stack vs Heap** | RC работает с heap-объектами | [[memory-model-fundamentals]] |
| **Garbage Collection** | Понять альтернативный подход | [[garbage-collection-explained]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Reference Count** | Счётчик ссылок на объект | Сколько людей держат верёвку |
| **retain** | Увеличить счётчик (+1) | Взяться за верёвку |
| **release** | Уменьшить счётчик (-1) | Отпустить верёвку |
| **Retain Cycle** | Объекты ссылаются друг на друга | Замкнутый круг рукопожатий |
| **strong** | Обычная ссылка, увеличивает count | Крепкое рукопожатие |
| **weak** | Слабая ссылка, не увеличивает count | Взгляд на человека |
| **unowned** | Как weak, но не optional | Доверие что человек рядом |

---

## ПОЧЕМУ появился Reference Counting

### До ARC: ручное управление памятью

В раннем Objective-C программисты вручную вызывали `retain` и `release`. Это называлось MRR (Manual Retain-Release).

```objc
// Objective-C до ARC
NSString *str = [[NSString alloc] init];  // count = 1
[str retain];                              // count = 2
[str release];                             // count = 1
[str release];                             // count = 0 → dealloc
```

Каждый `alloc` или `retain` требовал соответствующего `release`. Забыл `release` — memory leak. Лишний `release` — crash. Разработчики тратили огромное время на отладку.

### 2011: Apple вводит ARC

С iOS 5 и Xcode 4.2 Apple представила ARC. Компилятор (LLVM) сам вставляет retain/release в нужных местах. Разработчик больше не думает о count — код выглядит как будто память бесконечная.

```swift
// Swift с ARC
var str: String? = "Hello"  // ARC: retain
str = nil                    // ARC: release → dealloc
```

ARC — не garbage collection. Это compile-time оптимизация: компилятор анализирует код и вставляет нужные вызовы. Никаких пауз во время работы программы.

### Почему не GC?

Apple экспериментировала с garbage collection на macOS, но отказалась от него. Причины:

- **Непредсказуемые паузы.** GC может запуститься в любой момент, что критично для UI.
- **Больше памяти.** GC эффективен при 5-6x доступной памяти.
- **Мобильные устройства.** На iPhone ресурсы ограничены.

ARC даёт детерминистичное освобождение: объект удаляется сразу когда последняя ссылка исчезает.

---

## ЧТО такое Reference Counting

### Базовый принцип

Каждый объект в heap имеет скрытое поле — reference count. При создании ссылки count растёт, при удалении — падает. Когда count = 0, объект освобождается немедленно.

```
┌─────────────────────────────────────────────────────────────────┐
│                  ЖИЗНЕННЫЙ ЦИКЛ ОБЪЕКТА                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   let a = Person()         count = 1    [████░░░░░░]           │
│   let b = a                count = 2    [████████░░]           │
│   let c = a                count = 3    [████████████]         │
│                                                                 │
│   c = nil                  count = 2    [████████░░]           │
│   b = nil                  count = 1    [████░░░░░░]           │
│   a = nil                  count = 0    → DEALLOC              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Три типа ссылок в Swift

Swift предоставляет три типа ссылок с разным поведением:

**Strong (по умолчанию):**
```swift
var person: Person? = Person()  // strong reference, count+1
```
Увеличивает count. Объект живёт пока есть хотя бы одна strong ссылка.

**Weak:**
```swift
weak var delegate: PersonDelegate?  // НЕ увеличивает count
```
Не увеличивает count. ARC автоматически обнуляет (nil) когда объект удаляется. Всегда optional.

**Unowned:**
```swift
unowned var parent: Parent  // НЕ увеличивает count, НЕ optional
```
Как weak, но не optional. Если объект удалён, а ты обращаешься к unowned — crash. Использовать только когда уверен в lifetime.

### Сравнение типов ссылок

```
┌─────────────────────────────────────────────────────────────────┐
│                    ТИПЫ ССЫЛОК В SWIFT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Тип        count++?   Optional?   При dealloc объекта        │
│   ─────────────────────────────────────────────────────────    │
│   strong     Да         Опционально Ничего (ссылка держит)     │
│   weak       Нет        Обязательно Становится nil             │
│   unowned    Нет        Нет         CRASH при доступе          │
│                                                                 │
│   ─────────────────────────────────────────────────────────    │
│                                                                 │
│   Безопасность:  strong > weak > unowned                       │
│   Производительность: unowned > weak > strong                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Retain Cycles: главная проблема RC

### Почему GC не нужны weak/unowned?

Tracing GC (как в Java) находит живые объекты от корней. Если два объекта ссылаются друг на друга, но недостижимы от корней — они мусор.

Reference Counting не умеет так. Он смотрит только на count. Если A → B и B → A, оба имеют count > 0, оба "живые". Но если никто извне не ссылается на них — это memory leak.

```
┌─────────────────────────────────────────────────────────────────┐
│                      RETAIN CYCLE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│       ┌──────────┐          ┌──────────┐                       │
│       │ Person A │───────▶  │ Person B │                       │
│       │ count=1  │  strong  │ count=1  │                       │
│       └──────────┘          └──────────┘                       │
│              ▲                    │                             │
│              │      strong        │                             │
│              └────────────────────┘                             │
│                                                                 │
│   Никто извне не держит A и B, но count никогда не станет 0!   │
│   Результат: memory leak                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Типичные паттерны retain cycles

**1. Delegates:**
```swift
class ViewController {
    var tableView: TableView!

    func setup() {
        tableView = TableView()
        tableView.delegate = self  // VC → TableView → VC = cycle!
    }
}
```

**2. Closures:**
```swift
class ViewController {
    var handler: (() -> Void)?

    func setup() {
        handler = {
            self.doSomething()  // Closure захватывает self strongly
        }
        // VC → handler → VC = cycle!
    }
}
```

**3. Parent-Child:**
```swift
class Parent {
    var child: Child?
}

class Child {
    var parent: Parent?  // Если strong — cycle!
}
```

### Решение: разорвать цикл

Одна ссылка в цикле должна быть weak или unowned:

```swift
// Delegates — всегда weak
protocol TableViewDelegate: AnyObject {}

class TableView {
    weak var delegate: TableViewDelegate?  // weak разрывает cycle
}

// Closures — capture list
handler = { [weak self] in
    self?.doSomething()  // self теперь optional
}

// Parent-Child — child слабо ссылается на parent
class Child {
    weak var parent: Parent?
}
```

**Конвенция Apple:** parent → child = strong, child → parent = weak.

---

## КАК использовать weak и unowned

### Когда weak

Используй weak когда объект может быть deallocated во время жизни ссылки:

```swift
// Async операции
networkClient.fetch { [weak self] data in
    // ViewController мог быть закрыт пока шёл запрос
    guard let self = self else { return }
    self.updateUI(with: data)
}

// Delegates
class TableView {
    weak var delegate: TableViewDelegate?
}

// NotificationCenter
NotificationCenter.default.addObserver(
    forName: .appDidBecomeActive,
    object: nil,
    queue: .main
) { [weak self] _ in
    self?.refresh()
}
```

### Когда unowned

Используй unowned когда гарантирован lifetime — объект точно переживёт ссылку:

```swift
class Customer {
    let name: String
    var card: CreditCard?

    init(name: String) {
        self.name = name
    }
}

class CreditCard {
    let number: String
    unowned let customer: Customer  // Карта не существует без клиента

    init(number: String, customer: Customer) {
        self.number = number
        self.customer = customer
    }
}
```

Здесь CreditCard всегда создаётся с Customer, и Customer владеет картой. Карта не может пережить клиента.

### Правило безопасности

> Если сомневаешься — используй weak. unowned crash может случиться в продакшене и отладить его сложно.

```swift
// Опасно:
someAsyncOperation { [unowned self] in
    self.doSomething()  // Crash если self deallocated!
}

// Безопасно:
someAsyncOperation { [weak self] in
    self?.doSomething()  // Просто не выполнится
}
```

---

## Kotlin/Native и ARC: как они работают вместе

В KMP Kotlin-код компилируется в native для iOS. Kotlin/Native использует tracing GC, а Swift — ARC. Как они интегрируются?

### Kotlin → Swift

Когда Kotlin-объект передаётся в Swift, он оборачивается в специальную Swift-обёртку:

```
┌─────────────────────────────────────────────────────────────────┐
│             KOTLIN → SWIFT INTEROP                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Kotlin Side              Swift Side                           │
│   ┌──────────────┐         ┌──────────────────┐                │
│   │ KotlinObject │ ──────▶ │ SwiftWrapper     │                │
│   │ (GC tracked) │         │ (ARC tracked)    │                │
│   └──────────────┘         │ refCount: 1      │                │
│                            └──────────────────┘                │
│                                                                 │
│   ARC управляет SwiftWrapper                                   │
│   Kotlin GC видит что есть внешняя ссылка                      │
│   Объект не удаляется пока Swift держит wrapper                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Swift → Kotlin

Swift-объекты в Kotlin отслеживаются через "stable references":

```kotlin
// Kotlin видит Swift-объект
val swiftDelegate: NSObject = ...

// Kotlin GC держит stable reference
// ARC на Swift стороне продолжает управлять объектом
// Когда Kotlin отпускает — stable ref удаляется
// ARC может теперь освободить объект
```

### Особенности interop

**Deinitialization timing:**
```swift
class SwiftClass {
    deinit {
        print("deinit on \(Thread.current)")
    }
}
```
По умолчанию deinit вызывается на main thread. Можно изменить:
```properties
# gradle.properties
kotlin.native.binary.objcDisposeOnMain=false
```

**Сборка требует 2 GC cycles:**
Смешанные графы (Kotlin + Swift объекты) требуют двух проходов GC — сначала Kotlin, потом deinit Swift, потом опять Kotlin.

**autoreleasepool для loops:**
```kotlin
fun processMany() {
    repeat(1000) {
        autoreleasepool {
            // Swift interop операции
            callSwiftCode()
        }
    }
}
```

### Retain Cycles между языками

Kotlin GC обрабатывает циклы внутри Kotlin. ARC не обрабатывает циклы. Но если цикл проходит через оба языка — проблема:

```
Kotlin A → Swift B → Kotlin A

Ни Kotlin GC, ни ARC не могут разорвать!
```

**Решение:** weak ссылки на Swift стороне.

---

## Подводные камни

### Типичные ошибки

| Ошибка | Симптом | Решение |
|--------|---------|---------|
| Забыл [weak self] в closure | Memory leak, VC не освобождается | Добавить capture list |
| unowned на async операции | Crash | Использовать weak |
| Strong delegate | Cycle VC ↔ View | Weak delegate |
| Closure в NotificationCenter | Leak | [weak self] + removeObserver |

### Когда RC/ARC не подходит

- **Много циклических структур.** Графы, деревья с parent ссылками требуют внимания.
- **Hot loops с объектами.** Частые retain/release могут создать overhead.
- **Непредсказуемый lifetime.** Если сложно определить кто кого переживёт.

### Debugging

**Memory Graph Debugger (Xcode):**
Debug → Debug Memory Graph показывает все объекты и ссылки. Retain cycles видны как изолированные группы.

**Instruments:**
- Leaks — находит утечки
- Allocations — показывает что живёт дольше положенного

**Kotlin/Native:**
```properties
# Включить GC логи
-Xruntime-logs=gc=info
```

---

## Куда дальше

**Если здесь впервые:**
→ [[memory-model-fundamentals]] — основы работы памяти
→ [[garbage-collection-explained]] — альтернативный подход

**Практическое применение:**
→ [[kmp-ios-deep-dive]] — как это работает в реальном KMP проекте

---

## Источники

- [Swift Documentation: ARC](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/automaticreferencecounting/) — официальная документация
- [Kotlin/Native ARC Integration](https://kotlinlang.org/docs/native-arc-integration.html) — interop с Swift
- [SwiftLee: Weak Self](https://www.avanderlee.com/swift/weak-self/) — практические советы
- [Cocoacasts: Reference Cycles](https://cocoacasts.com/what-are-strong-reference-cycles) — паттерны и решения

---

*Проверено: 2026-01-09*
