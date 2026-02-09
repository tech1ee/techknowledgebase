---
title: iOS Process Memory Management & ARC
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
area: ios
tags: [ios, memory, arc, swift, retain-cycles, reference-counting, jetsam]
cs-foundations: [[reference-counting-arc]]
related: [[android-process-memory]], [[swift-value-types]], [[instruments-profiling]], [[ios-performance]]
---

## TL;DR

iOS использует ARC (Automatic Reference Counting) для управления памятью объектов, подсчитывая ссылки на них и автоматически освобождая объекты с нулевым счётчиком. В отличие от garbage collection (Android/Java), ARC работает детерминированно на этапе компиляции, но требует явного разрыва retain cycles через `weak`/`unowned`. При превышении лимита памяти (1.2-2GB на устройстве) процесс жёстко убивается демоном Jetsam без возможности восстановления.

## Зачем это нужно?

**Реальные лимиты памяти iOS:**
- iPhone SE (2020): ~1.2 GB доступной памяти для приложения
- iPhone 12/13: ~1.5-1.8 GB
- iPhone 14 Pro/15 Pro: ~2.0-2.5 GB
- iPad Pro: ~3-4 GB
- Background режим: всего 50-200 MB до принудительного завершения

**Критические проблемы без правильного управления памятью:**

1. **Jetsam kills** - iOS убивает приложение мгновенно при превышении лимита (без крэш-репорта)
2. **Memory leaks** - утекающая память в 1 MB/сек = крэш через 20 минут на iPhone SE
3. **Retain cycles** - замкнутые ссылки означают, что объекты никогда не освободятся
4. **UI freezes** - выделение больших объектов (>100MB) блокирует main thread
5. **App rejections** - App Store отклоняет приложения с явными утечками памяти

**Почему ARC, а не GC?**
- **Детерминизм**: объекты освобождаются сразу, когда счётчик = 0
- **Производительность**: нет пауз для сборки мусора (критично для 60/120 FPS UI)
- **Предсказуемость**: вы точно знаете, когда `deinit` вызовется
- **Низкий overhead**: только счётчик ссылок, нет mark-and-sweep алгоритмов

## Интуиция: 5 аналогий из жизни

### 1. Библиотечная книга (ARC механизм)
```
Библиотека выдаёт книгу:
- Каждый читатель ставит свою подпись в формуляре (+1 к счётчику)
- Когда возвращают книгу - подпись стирается (-1)
- Когда формуляр пуст (0) - книгу утилизируют

let book = Book()        // создали книгу, RC=1
let reader1 = book       // читатель 1 взял, RC=2
let reader2 = book       // читатель 2 взял, RC=3
reader1 = nil            // вернул, RC=2
reader2 = nil            // вернул, RC=1
// в конце scope RC=0 → deinit вызывается
```

### 2. Круговая порука (Retain Cycle)
```
Два человека держат друг друга за руки над обрывом:
- Каждый держится за другого, чтобы не упасть
- Даже если все остальные ушли, они продолжают висеть
- Никто не может отпустить первым → утечка памяти

class Parent {
    var child: Child?  // strong
}
class Child {
    var parent: Parent?  // strong → RETAIN CYCLE!
}
```

### 3. Фотография vs Указатель в справочнике (Strong vs Weak)
```
Strong: Фотография человека в альбоме
- Пока фото существует, "образ" человека сохранён
- Даже если человек уехал, фото осталось

Weak: Номер телефона в справочнике
- Указывает на человека, пока он существует
- Если человек выбросил SIM-карту → номер стал nil
- Справочник не "владеет" человеком

weak var delegate: MyDelegate?  // может стать nil
```

### 4. Квартирная субаренда (Unowned)
```
Unowned: Договор субаренды без проверки
- Субарендатор живёт, пока есть основной арендатор
- Если основной съехал, но субарендатор попытался войти → краш
- Используется, когда "знаете", что объект переживёт ссылку

unowned let owner: Person  // краш, если owner удалён
```

### 5. Музей со счётчиком посетителей (Autoreleasepool)
```
Турникет на выходе считает, сколько осталось:
- Объекты помечаются "к выходу" (autorelease)
- Но реально уходят только когда счётчик обнулится в конце цикла runloop
- Полезно при массовых операциях в цикле

autoreleasepool {
    for i in 1...10000 {
        let temp = UIImage(named: "photo\(i)")
        // без pool накопится 10000 объектов до конца runloop
    }
} // здесь всё освобождается принудительно
```

## Как это работает

### ARC Reference Counting Mechanism

```
Создание объекта и изменение счётчика:

let obj = MyClass()          Reference Count: 1
    │
    ├─ Strong ref created    ┌──────────────┐
    │                        │  MyClass     │
    │                        │  RC: 1       │
    └────────────────────────┤  data: [...]  │
                             └──────────────┘

let ref1 = obj              Reference Count: 2
let ref2 = obj              Reference Count: 3

ref1 = nil                  Reference Count: 2
ref2 = nil                  Reference Count: 1
// конец scope obj          Reference Count: 0 → deinit!


ARC инструкции (вставляются компилятором):

func process(item: Item) {
    swift_retain(item)       // RC += 1 (начало функции)

    // ваш код работает с item
    item.doSomething()

    swift_release(item)      // RC -= 1 (конец функции)
    // если RC стал 0 → вызов deinit
}
```

### Retain Cycle Visualization

```
❌ ПРОБЛЕМА: Круговая ссылка

┌─────────────┐              ┌─────────────┐
│  ViewController │  strong    │   Closure   │
│   RC: 1       ├────────────>│   RC: 1     │
│               │              │             │
│               │<────────────┤  captures   │
└─────────────┘    strong    └─────────────┘
                  self

Даже когда VC уходит с экрана:
- VC держит closure (strong property)
- Closure захватила self (strong по умолчанию)
- RC обоих никогда не станет 0 → LEAK


✅ РЕШЕНИЕ: Weak capture

┌─────────────┐              ┌─────────────┐
│ ViewController │  strong    │   Closure   │
│   RC: 1       ├────────────>│   RC: 1     │
│               │              │             │
│               │<┄┄┄┄┄┄┄┄┄┄┄┄│  captures   │
└─────────────┘     weak     └─────────────┘
                  [weak self]

Когда VC уходит с экрана:
- Closure имеет только weak ссылку
- RC ViewController становится 0 → deinit
- Closure продолжает жить, но self внутри = nil
```

### Strong vs Weak vs Unowned

```
┌────────────────────────────────────────────────────────┐
│                 Reference Types                        │
├──────────────┬──────────────┬────────────┬─────────────┤
│   Type       │  RC Change   │  Nullable  │  When Safe  │
├──────────────┼──────────────┼────────────┼─────────────┤
│ strong       │  +1          │    No      │  Default    │
│ weak         │   0          │   Yes      │  Delegates  │
│ unowned      │   0          │    No      │  Parent→Child│
└──────────────┴──────────────┴────────────┴─────────────┘

Memory Layout:

Strong:
┌──────┐         ┌────────────┐
│ ref  ├────────>│  Object    │
└──────┘         │  RC: 2     │
                 └────────────┘

Weak:
┌──────┐         ┌────────────┐
│ ref? ├┄┄┄┄┄┄┄┄>│  Object    │
└──────┘         │  RC: 1     │
  (Optional)     │  weak_refs:1│
                 └────────────┘
                 Когда RC=0:
┌──────┐         все weak → nil
│ nil  │
└──────┘

Unowned:
┌──────┐         ┌────────────┐
│ ref  ├┄┄┄┄┄┄┄┄>│  Object    │
└──────┘         │  RC: 1     │
  (Non-opt)      │  unowned:1 │
                 └────────────┘
                 Если RC=0:
┌──────┐         краш при доступе!
│ ref  ├─X──>💥
└──────┘
```

### Value Types vs Reference Types

```
Reference Types (class):        Value Types (struct, enum):
┌─────────────┐                ┌─────────────┐
│  var a      │                │  var a      │
│  ┌───────┐  │                │  ┌───────┐  │
│  │ ptr   ├──┼───┐            │  │ value │  │
│  └───────┘  │   │            │  │  = 5  │  │
└─────────────┘   │            └─────────────┘
                  ▼                     │
┌─────────────┐ ┌─────┐               │ copy
│  var b = a  │ │ Obj │               ▼
│  ┌───────┐  │ │ RC:2│         ┌─────────────┐
│  │ ptr   ├──┼─┤     │         │  var b = a  │
│  └───────┘  │ └─────┘         │  ┌───────┐  │
└─────────────┘                 │  │ value │  │
Обе ссылаются                   │  │  = 5  │  │
на ОДИН объект                  └─────────────┘
                                Независимые копии

Изменение a:                    Изменение a:
a.value = 10                    a.value = 10
b.value // тоже 10!             b.value // всё ещё 5!

Copy-on-Write Optimization (Array, String):

let arr1 = [1, 2, 3]
var arr2 = arr1              // share storage (не копируется!)

arr1 ───┐
        ├──> [1, 2, 3]  RC: 2
arr2 ───┘

arr2.append(4)               // copy-on-write triggered!

arr1 ───> [1, 2, 3]  RC: 1
arr2 ───> [1, 2, 3, 4]  RC: 1  (новая копия)
```

## Распространённые ошибки

### 1. Retain Cycle в замыкании с self

❌ **ПЛОХО:**
```swift
class ImageDownloader {
    var onComplete: (() -> Void)?

    func download(url: URL) {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            // Closure захватывает self strongly!
            self.processImage(data)
            self.onComplete?()  // RETAIN CYCLE
        }.resume()
    }
}

// ImageDownloader никогда не освободится
let downloader = ImageDownloader()
downloader.download(url: someURL)
downloader = nil  // но объект в памяти остался!
```

✅ **ХОРОШО:**
```swift
class ImageDownloader {
    var onComplete: (() -> Void)?

    func download(url: URL) {
        URLSession.shared.dataTask(with: url) { [weak self] data, _, _ in
            guard let self = self else { return }
            self.processImage(data)
            self.onComplete?()
        }.resume()
    }

    deinit {
        print("ImageDownloader освобождён")  // теперь вызовется!
    }
}
```

### 2. Delegate без weak

❌ **ПЛОХО:**
```swift
protocol DataSourceDelegate: AnyObject {
    func didUpdateData()
}

class DataSource {
    var delegate: DataSourceDelegate?  // strong reference!
}

class ViewController: UIViewController, DataSourceDelegate {
    let dataSource = DataSource()

    override func viewDidLoad() {
        super.viewDidLoad()
        dataSource.delegate = self  // RETAIN CYCLE!
        // VC → dataSource (strong) → delegate → VC (strong)
    }

    func didUpdateData() { }
}
```

✅ **ХОРОШО:**
```swift
protocol DataSourceDelegate: AnyObject {
    func didUpdateData()
}

class DataSource {
    weak var delegate: DataSourceDelegate?  // weak reference
}

class ViewController: UIViewController, DataSourceDelegate {
    let dataSource = DataSource()

    override func viewDidLoad() {
        super.viewDidLoad()
        dataSource.delegate = self  // безопасно
    }

    deinit {
        print("ViewController освобождён")
    }
}
```

### 3. Timer retain cycle

❌ **ПЛОХО:**
```swift
class CountdownView: UIView {
    var timer: Timer?
    var count = 10

    func startCountdown() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            self.count -= 1  // Timer → closure → self (strong)
            if self.count == 0 {
                self.timer?.invalidate()
            }
        }
    }

    deinit {
        print("CountdownView deinit")  // НИКОГДА не вызовется!
    }
}

// Timer держит view alive, даже если view удалён с экрана
```

✅ **ХОРОШО:**
```swift
class CountdownView: UIView {
    var timer: Timer?
    var count = 10

    func startCountdown() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else {
                // view был освобождён → останавливаем timer
                return
            }
            self.count -= 1
            if self.count == 0 {
                self.timer?.invalidate()
            }
        }
    }

    deinit {
        timer?.invalidate()  // обязательно invalidate!
        print("CountdownView освобождён")
    }
}
```

### 4. Неправильное использование unowned

❌ **ПЛОХО:**
```swift
class Customer {
    var card: CreditCard?
}

class CreditCard {
    unowned let owner: Customer  // предполагаем, что customer всегда жив

    init(owner: Customer) {
        self.owner = owner
    }

    func processPayment() {
        print("Processing for \(owner.name)")
    }
}

// Опасность:
var customer: Customer? = Customer()
let card = CreditCard(owner: customer!)
customer = nil  // customer освобождён!

card.processPayment()  // 💥 КРАШ! unowned ссылка на освобождённый объект
```

✅ **ХОРОШО:**
```swift
class Customer {
    var card: CreditCard?
}

class CreditCard {
    weak var owner: Customer?  // используем weak вместо unowned

    init(owner: Customer) {
        self.owner = owner
    }

    func processPayment() {
        guard let owner = owner else {
            print("Customer больше не существует")
            return
        }
        print("Processing for \(owner.name)")
    }
}

// Безопасно:
var customer: Customer? = Customer()
let card = CreditCard(owner: customer!)
customer = nil

card.processPayment()  // безопасно: "Customer больше не существует"
```

### 5. Утечка в autoreleasepool

❌ **ПЛОХО:**
```swift
func processImages() {
    for i in 0..<10000 {
        let image = UIImage(named: "large_photo_\(i)")
        // Временные объекты накапливаются в autoreleasepool
        // Освобождение только в конце runloop iteration
        let processed = image?.applying(filter: heavyFilter)
        save(processed)
    }
    // К этому моменту в памяти ~10000 UIImage объектов!
    // Memory warning → Jetsam kill
}
```

✅ **ХОРОШО:**
```swift
func processImages() {
    for i in 0..<10000 {
        autoreleasepool {
            let image = UIImage(named: "large_photo_\(i)")
            let processed = image?.applying(filter: heavyFilter)
            save(processed)
            // image и processed освобождаются здесь
        }
    }
    // Пиковое потребление памяти = только 1 изображение
}
```

### 6. Closure capture list неполный

❌ **ПЛОХО:**
```swift
class ChatViewController: UIViewController {
    var chatService: ChatService?
    var messageLabel: UILabel?

    func loadMessage() {
        chatService?.fetchLatestMessage { [weak self] message in
            // self weak, но chatService и messageLabel захвачены strongly!
            self?.chatService?.markAsRead(message)
            self?.messageLabel?.text = message.text
            // Если chatService сложный объект → утечка
        }
    }
}
```

✅ **ХОРОШО:**
```swift
class ChatViewController: UIViewController {
    var chatService: ChatService?
    var messageLabel: UILabel?

    func loadMessage() {
        chatService?.fetchLatestMessage { [weak self] message in
            guard let self = self else { return }
            // Теперь все обращения через self
            self.chatService?.markAsRead(message)
            self.messageLabel?.text = message.text
        }
    }

    // Или явно захватить зависимости:
    func loadMessageExplicit() {
        guard let service = chatService, let label = messageLabel else { return }

        service.fetchLatestMessage { [weak label] message in
            label?.text = message.text
            // chatService не захвачен вообще
        }
    }
}
```

## Ментальные модели

### 1. Модель "Владение и заимствование" (Ownership)
```
Strong reference = ВЛАДЕНИЕ
- Вы отвечаете за жизнь объекта
- Пока вы держите strong ref, объект жив

Weak reference = ЗАИМСТВОВАНИЕ
- Вы не владеете, только наблюдаете
- Объект может исчезнуть в любой момент

Parent-Child relationships:
Parent ──[strong]──> Child      // родитель владеет ребёнком
Child ──[weak]────> Parent      // ребёнок не владеет родителем

Delegate pattern:
Owner ──[strong]──> Helper      // owner владеет helper
Helper ──[weak]───> Owner       // helper не владеет owner (delegate)
```

### 2. Модель "Граф зависимостей"
```
Представьте граф с направленными рёбрами:

A ──strong──> B ──strong──> C
↑                           │
└────────weak───────────────┘

Объект живёт, пока к нему есть хотя бы один STRONG путь от корня (stack/global)

Root (stack)
 ├──> A (RC: 1)
 ├──> B (RC: 2, +1 от A, +1 от Root)
 └──> C (RC: 1)

Если удалить Root → A:
Root (nil)
 ├──X A (RC: 0) → deinit
 ├──> B (RC: 1) ← всё ещё жив!
 └──> C (RC: 1)

Weak ссылка C→A не продлевает жизнь A
```

### 3. Модель "Счётчик в баре"
```
Бармен считает заказы:
- Каждый заказ напитка = +1
- Каждый выпитый = -1
- Когда счёт = 0, бармен убирает стакан

Strong:  Полноценный заказ (входит в счёт)
Weak:    Наблюдатель (не входит в счёт, смотрит "есть ли напиток")
Unowned: VIP-пропуск (уверенность, что напиток не уберут)

let drink = Drink()        // заказ +1, count=1
let friend = drink         // ещё заказ +1, count=2
weak var waiter = drink    // наблюдает, count=2
friend = nil               // выпил -1, count=1
// drink существует, waiter видит его

drink = nil                // count=0, стакан убран
// waiter теперь nil (стакан исчез)
```

### 4. Модель "Дерево с листьями"
```
Root (ViewController)
 ├── Branch (View)
 │   ├── Leaf (Subview)
 │   └── Leaf (Subview)
 └── Branch (DataSource)
     └── Leaf (Cache)

Strong references идут ОТ корня К листьям (top-down)
Weak references идут ОТ листьев К корню (bottom-up)

Правило: Child никогда не владеет Parent
         Helper никогда не владеет Owner

UIViewController ──[strong]──> UIView
UIView ──[weak]──> UIViewController (через delegate/target)

UIButton ──[weak]──> Target (action pattern)
```

### 5. Модель "Жизненный цикл аренды"
```
Strong = Договор аренды на неопределённый срок
- Пока договор действует, квартира занята
- Можно передать другому (copy reference)
- Квартира освобождается, когда ВСЕ договоры расторгнуты

Weak = Ключ от квартиры БЕЗ договора
- Можете попытаться войти
- Но если арендаторов не осталось → дверь заперта (nil)
- Не продлеваете срок аренды

Unowned = Ключ с предположением "точно открыто"
- Не проверяете, есть ли арендаторы
- Если ошиблись → попытка войти в пустую квартиру = краш

Copy-on-Write = Shared room до первого конфликта
- Пока все согласны, комната одна
- Как только кто-то хочет изменить → создаётся копия
```

## Когда использовать weak vs unowned

### Таблица принятия решений

```
┌─────────────────────────────────────────────────────────────┐
│              weak vs unowned Decision Tree                  │
└─────────────────────────────────────────────────────────────┘

Вопрос 1: Может ли referenced объект быть освобождён раньше?
    ├─ ДА → weak var (optional, может стать nil)
    └─ НЕТ → переходим к вопросу 2

Вопрос 2: Гарантировано ли, что объект переживёт ссылку?
    ├─ ДА (100% уверенность) → unowned let
    └─ НЕТ УВЕРЕННОСТИ → weak var (безопаснее)

Вопрос 3: Требуется ли optional?
    ├─ ДА (логика допускает nil) → weak var
    └─ НЕТ (объект должен быть всегда) → unowned let
```

### Практические правила

**Используйте `weak`:**
```swift
// 1. Delegates (стандартный паттерн)
protocol ViewDelegate: AnyObject { }
class View {
    weak var delegate: ViewDelegate?
}

// 2. Parent references в child объектах
class ChildView: UIView {
    weak var parentController: ParentViewController?
}

// 3. Observers и notification handlers
class Observer {
    weak var observedObject: DataModel?
}

// 4. Closures, где self может исчезнуть
someAsyncTask { [weak self] in
    guard let self = self else { return }
    self.updateUI()
}

// 5. IBOutlet (могут быть nil после unload view)
class ViewController: UIViewController {
    @IBOutlet weak var tableView: UITableView!
}

// 6. Временные references в кэшах
class Cache<T: AnyObject> {
    private var storage: [String: Weak<T>] = [:]
}
```

**Используйте `unowned`:**
```swift
// 1. Child → Parent когда parent ВСЕГДА переживёт child
class Country {
    var capital: City?
}
class City {
    unowned let country: Country  // город всегда часть страны
    init(country: Country) {
        self.country = country
    }
}

// 2. Closures в синхронных операциях
class DataProcessor {
    func process(data: Data) {
        let transform: (Data) -> Data = { [unowned self] input in
            // closure живёт только внутри этой функции
            return self.apply(filter: input)
        }
        let result = transform(data)
    }
}

// 3. Child НИКОГДА не существует без parent
class Customer {
    var card: CreditCard?
}
class CreditCard {
    unowned let owner: Customer  // карта не может быть без владельца
    init(owner: Customer) {
        self.owner = owner
        owner.card = self
    }
}

// 4. Immutable backreferences в тесно связанных объектах
class HTMLElement {
    let tag: String
    unowned let document: HTMLDocument

    init(tag: String, document: HTMLDocument) {
        self.tag = tag
        self.document = document
    }
}
```

**НЕ используйте `unowned` если:**
```swift
// ❌ Объект может быть освобождён извне
class ViewController {
    var service: NetworkService?

    func fetch() {
        service?.getData { [unowned self] data in
            // ОПАСНО! VC может быть dismissed до завершения запроса
            self.updateUI(data)  // 💥 краш если VC уже deinit
        }
    }
}

// ✅ Правильно:
func fetch() {
    service?.getData { [weak self] data in
        guard let self = self else { return }
        self.updateUI(data)
    }
}
```

### Сравнительная таблица

```
┌─────────────┬──────────┬──────────┬──────────────┬─────────────┐
│  Критерий   │  strong  │   weak   │   unowned    │  Рекоменд.  │
├─────────────┼──────────┼──────────┼──────────────┼─────────────┤
│ RC +1       │    ✓     │    ✗     │      ✗       │             │
│ Optional    │    ✗     │    ✓     │      ✗       │             │
│ Safe nil    │    N/A   │    ✓     │      ✗       │             │
│ Crash risk  │    ✗     │    ✗     │      ✓       │             │
│ Performance │  Slow    │  Medium  │    Fast      │  unowned    │
│ Safety      │  Cycles  │   Safe   │   Dangerous  │  weak       │
├─────────────┼──────────┼──────────┼──────────────┼─────────────┤
│ Delegates   │    ✗     │    ✓     │      ✗       │   weak      │
│ Parents     │    ✗     │    ✓     │      ✓*      │   weak      │
│ Closures    │    ✗     │    ✓     │      ✓**     │   weak      │
│ Owned child │    ✓     │    ✗     │      ✗       │   strong    │
└─────────────┴──────────┴──────────┴──────────────┴─────────────┘

* только если parent гарантировано переживёт child
** только в синхронных, коротких closures
```

## Memory Debugging & Tools

### Instruments - Memory Profiling

```
Основные инструменты:

1. Leaks Instrument
   - Детектит retain cycles
   - Показывает граф объектов
   - Находит "unreachable" память

2. Allocations Instrument
   - Отслеживает каждую аллокацию
   - Показывает рост heap
   - Mark Generation для поиска утечек

3. Memory Graph Debugger (Xcode)
   - Визуальный граф памяти
   - Показывает retain cycles фиолетовым !
   - Backtrace каждого объекта

Как найти утечку:
┌─────────────────────────────────────┐
│ 1. Запустить профилирование         │
│ 2. Выполнить действие (открыть/     │
│    закрыть экран)                   │
│ 3. Mark Generation в Allocations    │
│ 4. Повторить действие 5-10 раз      │
│ 5. Посмотреть рост между генерациями│
│ 6. Найти объекты, которые не        │
│    освобождаются                    │
└─────────────────────────────────────┘
```

### Memory Warnings & Jetsam

```swift
// Обработка memory warnings
class MyViewController: UIViewController {

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()

        // 1. Очистить кэши
        imageCache.removeAll()

        // 2. Освободить тяжёлые ресурсы
        largeDataSet = nil

        // 3. Перезагрузить данные при необходимости
        shouldReloadData = true

        print("⚠️ Memory warning received!")
    }
}

// Глобальный обработчик
NotificationCenter.default.addObserver(
    forName: UIApplication.didReceiveMemoryWarningNotification,
    object: nil,
    queue: .main
) { _ in
    // Очистка глобальных кэшей
    URLCache.shared.removeAllCachedResponses()
    ImageCache.shared.clear()
}

// Jetsam priority levels (JetsamPriority)
Foreground:        ~1400 MB (iPhone 12)
Background:        ~50-200 MB
Background Audio:  ~100-300 MB
Location:          ~100 MB

// Получение текущего memory usage
func reportMemoryUsage() {
    var info = mach_task_basic_info()
    var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4

    let result = withUnsafeMutablePointer(to: &info) {
        $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
            task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
        }
    }

    if result == KERN_SUCCESS {
        let usedMB = Double(info.resident_size) / 1024.0 / 1024.0
        print("Memory used: \(usedMB) MB")

        if usedMB > 1200 {
            print("⚠️ Approaching Jetsam limit!")
        }
    }
}
```

### Сравнение с Android GC

```
┌────────────────────────────────────────────────────────────┐
│            iOS ARC vs Android GC                           │
├────────────────┬──────────────────┬────────────────────────┤
│   Характеристика   │   iOS ARC        │  Android GC        │
├────────────────┼──────────────────┼────────────────────────┤
│ Алгоритм       │ Reference Counting│ Mark & Sweep (Tracing)│
│ Когда          │ Compile-time     │ Run-time              │
│ Паузы          │ Нет              │ Да (GC pause)         │
│ Детерминизм    │ Да (deinit точно)│ Нет (недетерм. timing)│
│ Overhead       │ Низкий (RC++)    │ Высокий (mark phase)  │
│ Cycles         │ Leak!            │ Собираются автоматом  │
│ Developer      │ Нужно думать     │ Меньше забот          │
├────────────────┼──────────────────┼────────────────────────┤
│ Плюсы          │ - Предсказуемо   │ - Автомат. cycles     │
│                │ - Нет пауз       │ - Проще для разраб.   │
│                │ - Низкий latency │ - Меньше ошибок       │
├────────────────┼──────────────────┼────────────────────────┤
│ Минусы         │ - Retain cycles! │ - GC паузы            │
│                │ - Надо weak/unown│ - Непредсказуемость   │
│                │ - Более сложно   │ - Больше overhead     │
└────────────────┴──────────────────┴────────────────────────┘

Пример retain cycle:

iOS:                          Android:
A → B → A (LEAK!)            A → B → A (GC соберёт!)
│       ↑                    GC пройдётся по графу,
└───────┘                    найдёт unreachable → free
RC A: 1 (от B)
RC B: 1 (от A)               Marking phase:
Никогда не освободится!      Root → mark reachable
                             A и B не достижимы от root
Решение:                     → Sweep phase → free
weak var B: A?

Подробнее см: [[android-process-memory]]
```

## Swift Value Types & Copy-on-Write

```swift
// Value types копируются, но умно!
struct Point {
    var x: Double
    var y: Double
}

var p1 = Point(x: 0, y: 0)
var p2 = p1  // немедленная копия (small struct)

// Copy-on-Write для больших коллекций
var array1 = Array(1...1000000)
var array2 = array1  // НЕ копируется! shared storage

print(isUniquelyReferenced(&array1._storage))  // false (shared)

array2.append(999)  // ЗДЕСЬ происходит копирование
print(isUniquelyReferenced(&array1._storage))  // true

// Как работает COW:
/*
array1 ───┐
          ├──> [1...1000000] RC: 2
array2 ───┘

После append:
array1 ───> [1...1000000] RC: 1
array2 ───> [1...1000000, 999] RC: 1 (новая копия)
*/

// Оптимизация для собственных типов:
struct MyBuffer {
    private var storage: [Int]

    mutating func append(_ value: Int) {
        if !isKnownUniquelyReferenced(&storage) {
            storage = storage  // force copy
        }
        storage.append(value)
    }
}
```

## Autoreleasepool в Swift

```swift
// Legacy Objective-C pattern, но всё ещё полезен

// Пример 1: Обработка больших объёмов данных
func processLargeDataset() {
    let items = loadMillionItems()

    for item in items {
        autoreleasepool {
            // Объекты из Objective-C API (UIImage, NSData)
            // помечаются autorelease
            let image = loadImage(item)
            let processed = applyFilters(image)  // UIKit вызовы
            save(processed)

            // Без autoreleasepool эти объекты накапливаются
            // до конца runloop iteration → OOM
        }
    }
}

// Пример 2: Background processing
DispatchQueue.global().async {
    autoreleasepool {
        // Background threads не имеют автоматического autorelease pool
        let data = fetchData()
        processData(data)
        // без pool = утечка autorelease объектов
    }
}

// Когда НЕ нужен autoreleasepool:
// - Pure Swift объекты (не используют autorelease)
// - Малое количество итераций (<100)
// - Нет вызовов Objective-C API

// Когда НУЖЕН:
// - Циклы с UIKit/Foundation объектами
// - Парсинг больших JSON/XML
// - Обработка тысяч изображений
// - Background threads с ObjC interop
```

## Проверь себя

<details>
<summary><strong>Вопрос 1:</strong> Что произойдёт с памятью в этом коде?</summary>

```swift
class Parent {
    var child: Child?
    deinit { print("Parent deinit") }
}

class Child {
    var parent: Parent?
    deinit { print("Child deinit") }
}

func test() {
    let parent = Parent()
    let child = Child()
    parent.child = child
    child.parent = parent
}

test()
// Что напечатается?
```

**Ответ:**
Ничего не напечатается! Оба объекта остаются в памяти (retain cycle).

**Объяснение:**
- `parent` держит strong ссылку на `child` → RC child = 1
- `child` держит strong ссылку на `parent` → RC parent = 1
- Когда `test()` заканчивается, локальные переменные освобождаются
- Но объекты держат друг друга → RC никогда не станет 0
- Утечка памяти: 2 объекта остаются в heap навсегда

**Решение:**
```swift
class Child {
    weak var parent: Parent?  // слабая ссылка
}
// Теперь:
// - parent освобождается → RC parent = 0 → deinit Parent
// - child.parent становится nil автоматически
// - child освобождается → RC child = 0 → deinit Child
```
</details>

<details>
<summary><strong>Вопрос 2:</strong> В чём ошибка и как исправить?</summary>

```swift
class NetworkManager {
    func fetchData(completion: @escaping (Data) -> Void) {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            if let data = data {
                completion(data)
            }
        }.resume()
    }
}

class ViewController: UIViewController {
    let manager = NetworkManager()
    var data: Data?

    func loadData() {
        manager.fetchData { data in
            self.data = data
            self.updateUI()
        }
    }
}
```

**Ответ:**
Retain cycle между ViewController и closure.

**Объяснение:**
1. `ViewController` → `manager` (strong)
2. `manager.fetchData` → `completion` closure (strong, @escaping)
3. `completion` захватывает `self` (strong по умолчанию)
4. Цикл: VC → manager → closure → VC

**Проблема:**
Даже если ViewController удаляется с экрана, closure продолжает держать strong ссылку на self. Если запрос долгий (30 сек) → VC будет в памяти 30 сек после dismiss.

**Решение:**
```swift
func loadData() {
    manager.fetchData { [weak self] data in
        guard let self = self else {
            print("VC был освобождён, игнорируем результат")
            return
        }
        self.data = data
        self.updateUI()
    }
}

// Или если нужно отменить запрос:
var currentTask: URLSessionDataTask?

func loadData() {
    currentTask = manager.fetchData { [weak self] data in
        guard let self = self else { return }
        self.data = data
        self.updateUI()
    }
}

deinit {
    currentTask?.cancel()  // отменить запрос при деинициализации
}
```
</details>

<details>
<summary><strong>Вопрос 3:</strong> Какой вариант лучше и почему?</summary>

```swift
// Вариант A:
class View {
    weak var delegate: ViewDelegate?
}

// Вариант B:
class View {
    unowned let delegate: ViewDelegate
}

// Вариант C:
class View {
    var delegate: ViewDelegate?
}
```

**Ответ:**
Вариант A (weak var) — стандарт для delegates.

**Сравнение:**

**Вариант A (weak var):**
✅ Безопасно: delegate может стать nil
✅ Гибко: delegate можно изменить
✅ Стандарт: все Apple frameworks используют weak delegates
✅ Optional: допускает отсутствие delegate

**Вариант B (unowned let):**
❌ Опасно: краш если delegate освобождён
❌ Негибко: нельзя изменить (let)
❌ Требует инициализации: усложняет код
⚠️ Возможно только если delegate ГАРАНТИРОВАННО переживёт view

**Вариант C (var):**
❌ Retain cycle: если delegate держит view
❌ Не следует convention
❌ Память: увеличивает RC delegate

**Когда использовать B:**
```swift
// ТОЛЬКО если view всегда часть delegate и никогда не переживёт его
class TableViewCell {
    unowned let tableView: UITableView
    // Ячейка не может существовать без таблицы
}
```

**Golden rule:**
Delegates ВСЕГДА weak (кроме очень редких исключений с unowned).
</details>

<details>
<summary><strong>Вопрос 4:</strong> Нужен ли здесь autoreleasepool?</summary>

```swift
// Сценарий A:
func loadImages() {
    for i in 0..<10000 {
        let image = UIImage(named: "photo_\(i)")
        processImage(image)
    }
}

// Сценарий B:
func parseJSON() {
    for item in jsonItems {
        let obj = MySwiftStruct(from: item)
        process(obj)
    }
}
```

**Ответ:**

**Сценарий A: ДА, нужен!**
```swift
func loadImages() {
    for i in 0..<10000 {
        autoreleasepool {
            let image = UIImage(named: "photo_\(i)")
            processImage(image)
            // UIImage использует autorelease под капотом
        }
    }
}
```

**Причины:**
- `UIImage(named:)` — Objective-C API
- Возвращает autoreleased объекты
- Без autoreleasepool накопится 10000 изображений до конца runloop
- При среднем размере 5 MB → 50 GB памяти → Jetsam kill

**Сценарий B: НЕТ, не нужен**
```swift
func parseJSON() {
    for item in jsonItems {
        let obj = MySwiftStruct(from: item)
        process(obj)
        // Pure Swift struct, нет autorelease
    }
}
```

**Причины:**
- `MySwiftStruct` — Swift value type
- Не использует autorelease механизм
- Память освобождается автоматически в конце каждой итерации
- autoreleasepool просто добавит overhead без пользы

**Правило:**
autoreleasepool нужен когда:
1. Вызовы UIKit/Foundation API в циклах
2. Background threads с Objective-C interop
3. Обработка тысяч объектов из Cocoa frameworks

НЕ нужен для pure Swift кода.
</details>

## Связанные темы

- [[reference-counting-arc]] — теоретические основы подсчёта ссылок
- [[android-process-memory]] — сравнение с garbage collection
- [[swift-value-types]] — структуры, перечисления, copy-on-write
- [[instruments-profiling]] — профилирование памяти и производительности
- [[ios-performance]] — общие практики оптимизации iOS
- [[swift-concurrency]] — async/await и actor isolation для безопасности памяти
- [[combine-framework]] — реактивное программирование и управление подписками
- [[core-data-memory]] — оптимизация памяти в Core Data
- [[uikit-lifecycle]] — жизненный цикл view controllers и memory warnings
- [[swiftui-state-management]] — @State, @StateObject и управление памятью в SwiftUI

## Источники

1. **Apple Documentation:**
   - [Understanding Swift Performance (WWDC)](https://developer.apple.com/videos/play/wwdc2016/416/)
   - [Swift ARC Memory Management](https://docs.swift.org/swift-book/LanguageGuide/AutomaticReferenceCounting.html)
   - [Advanced Memory Management Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/MemoryMgmt.html)

2. **Technical Papers:**
   - "iOS Memory Deep Dive" (WWDC 2018)
   - "Finding Reference Cycles in Swift" (WWDC 2021)
   - "Instruments Memory Profiling Best Practices"

3. **Community Resources:**
   - Swift Forums: Memory Management Discussions
   - Swift Evolution Proposals (ARC improvements)
   - Real-world iOS memory debugging case studies

4. **Books:**
   - "Advanced Swift" by Chris Eidhof — глава про ARC
   - "iOS and macOS Performance Tuning" by Marcel Weiher
   - "Optimizing Swift Performance" by Matthijs Hollemans
