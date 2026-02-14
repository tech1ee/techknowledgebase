---
title: "Design Patterns: решения, которые уже работают"
created: 2025-11-24
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/programming
  - programming/patterns
  - architecture/design
  - best-practices
  - type/concept
  - level/intermediate
related:
  - "[[clean-code-solid]]"
  - "[[microservices-vs-monolith]]"
  - "[[api-design]]"
prerequisites:
  - "[[clean-code-solid]]"
  - "[[type-systems-theory]]"
reading_time: 31
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Design Patterns: решения, которые уже работают

Паттерн ради паттерна — антипаттерн. Знать все 23 GoF-паттерна не нужно, но 5-7 ключевых превратят спагетти-код в понятную архитектуру.

---

## TL;DR

**Design Patterns** — каталогизированные решения типичных проблем проектирования. Не изобретение, а **документирование** того, что уже работало.

**Что важно понимать:**
- Паттерн = **Intent** (зачем) + **Participants** (кто участвует) + **Consequences** (trade-offs)
- У каждого паттерна есть **ключевые компоненты** — упустишь один, паттерн не работает
- Паттерн без контекста = антипаттерн (Cargo Cult Programming)

**Главные ошибки:**
1. **Cargo Cult** — применять паттерн "потому что так правильно", не понимая ПОЧЕМУ
2. **Golden Hammer** — один паттерн для всех проблем
3. **Overengineering** — Factory для `new User(name)`

---

## Терминология

| Термин | Значение |
|--------|----------|
| **GoF** | Gang of Four — авторы книги "Design Patterns" (1994) |
| **Intent** | Что паттерн делает и какую проблему решает |
| **Participants** | Ключевые компоненты паттерна (классы, интерфейсы, роли) |
| **Creational** | Паттерны создания объектов |
| **Structural** | Паттерны структуры и композиции |
| **Behavioral** | Паттерны поведения и взаимодействия |
| **Loose coupling** | Слабая связанность компонентов |

---

## История и контекст

**Gang of Four (GoF)** — Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides. Книга "Design Patterns: Elements of Reusable Object-Oriented Software" (1994).

**Что они сделали:** Не изобрели паттерны, а **каталогизировали** решения, которые уже использовались в индустрии. 23 паттерна с формальным описанием.

**Структура описания паттерна в GoF:**

| Секция | Что описывает |
|--------|---------------|
| **Intent** | Зачем паттерн существует, какую проблему решает |
| **Motivation** | Сценарий, где паттерн полезен |
| **Applicability** | Когда применять |
| **Structure** | UML-диаграмма классов |
| **Participants** | Роли каждого компонента |
| **Collaborations** | Как компоненты взаимодействуют |
| **Consequences** | Trade-offs: плюсы и минусы |
| **Implementation** | Практические советы |

> "Design patterns should not be applied indiscriminately. Often they achieve flexibility and variability by introducing additional levels of indirection, and that can complicate a design and/or cost you some performance." — GoF Book

---

## Зачем вообще паттерны?

```
Без паттернов:

"Мне нужно создавать разные типы уведомлений..."
    ↓
if (type === "email") {
  // 50 строк кода email
} else if (type === "sms") {
  // 50 строк кода sms
} else if (type === "push") {
  // 50 строк кода push
}
    ↓
Через месяц: добавить Telegram
    ↓
Ещё один else if, код разрастается
    ↓
Через год: 500 строк в одном файле, страшно трогать

С паттерном (Factory + Strategy):

const notification = NotificationFactory.create(type);
notification.send(message);
    ↓
Добавить Telegram = создать новый класс
    ↓
Старый код не трогаем
```

---

## Три категории паттернов

```
┌─────────────────────────────────────────────────────────────────┐
│                      DESIGN PATTERNS                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   CREATIONAL    │   STRUCTURAL    │        BEHAVIORAL           │
│   (Создание)    │   (Структура)   │        (Поведение)          │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ Factory         │ Adapter         │ Strategy                    │
│ Builder         │ Decorator       │ Observer                    │
│ Singleton       │ Facade          │ Command                     │
│ Prototype       │ Composite       │ State                       │
│                 │ Proxy           │ Iterator                    │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ КАК создавать   │ КАК собирать    │ КАК объекты                 │
│ объекты?        │ объекты?        │ взаимодействуют?            │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## Factory: создание без new

### Intent (Зачем)

**Проблема:** Код, который создаёт объекты, жёстко привязан к конкретным классам. Добавление нового типа требует изменения этого кода.

**Решение:** Делегировать создание объектов специальному методу или классу. Клиентский код работает с интерфейсом, не зная конкретных классов.

### Participants (Ключевые компоненты)

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Product** | Интерфейс объектов, которые создаёт фабрика | Без него нет полиморфизма |
| **ConcreteProduct** | Конкретные реализации Product | Это то, что фабрика создаёт |
| **Creator** | Объявляет factory method (может быть абстрактным) | Без него логика создания размазана |
| **ConcreteCreator** | Реализует factory method, решает какой ConcreteProduct создать | Здесь живёт логика выбора |

```
┌─────────────────────────────────────────────────────────────┐
│                     FACTORY METHOD                          │
├─────────────────────────────────────────────────────────────┤
│   Creator (abstract)          Product (interface)           │
│   ├── factoryMethod()         ├── operation()               │
│   └── someOperation()         │                             │
│          ↑                            ↑                     │
│   ConcreteCreator             ConcreteProductA              │
│   └── factoryMethod()         ConcreteProductB              │
│       return new ConcreteProductA()                         │
└─────────────────────────────────────────────────────────────┘
```

### Проблема (без паттерна)

```typescript
// Плохо: код знает о всех типах
function createPayment(type: string) {
  if (type === "card") {
    return new CardPayment(apiKey, merchantId, timeout);
  } else if (type === "paypal") {
    return new PayPalPayment(clientId, secret);
  } else if (type === "crypto") {
    return new CryptoPayment(walletAddress, network);
  }
  // Каждый новый тип = изменение этого файла
}
```

### Решение: Factory

```typescript
// Интерфейс — контракт для всех платежей
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
  refund(transactionId: string): Promise<void>;
}

// Конкретные реализации
class CardPayment implements PaymentProcessor {
  constructor(private config: CardConfig) {}

  async process(amount: number): Promise<PaymentResult> {
    // Логика карточного платежа
    return { success: true, transactionId: "card_123" };
  }

  async refund(transactionId: string): Promise<void> {
    // Возврат на карту
  }
}

class PayPalPayment implements PaymentProcessor {
  constructor(private config: PayPalConfig) {}

  async process(amount: number): Promise<PaymentResult> {
    // PayPal API
    return { success: true, transactionId: "pp_456" };
  }

  async refund(transactionId: string): Promise<void> {
    // PayPal refund
  }
}

// Factory — единая точка создания
class PaymentFactory {
  private static processors: Map<string, () => PaymentProcessor> = new Map();

  static register(type: string, creator: () => PaymentProcessor) {
    this.processors.set(type, creator);
  }

  static create(type: string): PaymentProcessor {
    const creator = this.processors.get(type);
    if (!creator) {
      throw new Error(`Unknown payment type: ${type}`);
    }
    return creator();
  }
}

// Регистрация (при старте приложения)
PaymentFactory.register("card", () => new CardPayment(cardConfig));
PaymentFactory.register("paypal", () => new PayPalPayment(paypalConfig));

// Использование — код не знает о конкретных классах
const payment = PaymentFactory.create(userSelectedType);
await payment.process(99.99);
```

### Когда использовать

```
✅ Используй Factory когда:
• Тип объекта определяется в runtime
• Создание объекта сложное (много зависимостей)
• Хочешь скрыть детали создания от клиентского кода
• Нужна возможность легко добавлять новые типы

❌ Не используй когда:
• Всегда создаёшь один конкретный тип
• Создание простое (new User(name))
```

### ⚠️ Anti-Pattern: Factory ради Factory

```typescript
// ПЛОХО: Factory без смысла
class UserFactory {
  create(name: string) {
    return new User(name);  // Просто обёртка над new
  }
}

// Вопрос: зачем это?
// - Тип всегда один (User)
// - Создание тривиальное
// - Никакой гибкости не добавляет

// ДОСТАТОЧНО:
const user = new User(name);
```

> "Having a separate factory for each class, particularly when they're just 'wrap the new', is something to avoid; I'm tempted to call it an anti-pattern." — [Manning: Abuse of Abstract Factories](https://freecontent.manning.com/dependency-injection-in-net-2nd-edition-abuse-of-abstract-factories/)

**Признаки злоупотребления Factory:**
- Factory создаёт только один тип объекта
- Метод `create()` — просто `return new X()`
- Нет сложной логики инициализации
- Factory создаёт Factory, которая создаёт Factory...

---

## Strategy: взаимозаменяемые алгоритмы

### Intent (Зачем)

**Проблема:** Алгоритм захардкожен в классе. Чтобы изменить поведение, нужно менять сам класс. Условные операторы (if/else, switch) разрастаются.

**Решение:** Выделить семейство алгоритмов в отдельные классы с общим интерфейсом. Клиент выбирает алгоритм в runtime.

### Participants (Ключевые компоненты)

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Strategy** | Интерфейс, общий для всех алгоритмов | Без него нет взаимозаменяемости |
| **ConcreteStrategy** | Реализация конкретного алгоритма | Каждая стратегия = один алгоритм |
| **Context** | Использует Strategy, делегирует работу | **ЧАСТО ЗАБЫВАЮТ!** Без Context стратегии висят в воздухе |

```
┌─────────────────────────────────────────────────────────────┐
│                       STRATEGY                              │
├─────────────────────────────────────────────────────────────┤
│   Context                       Strategy (interface)        │
│   ├── strategy: Strategy        └── execute()               │
│   └── doWork() {                       ↑                    │
│         strategy.execute()      ┌──────┴──────┐             │
│       }                   ConcreteA    ConcreteB            │
│                           execute()    execute()            │
└─────────────────────────────────────────────────────────────┘
```

**Почему Context важен:**
- Context **владеет** ссылкой на стратегию
- Context решает **когда** вызывать стратегию
- Context может передавать **контекстные данные** стратегии
- Без Context клиенты напрямую работают со стратегиями → tight coupling

### Проблема (без паттерна)

```typescript
// Плохо: алгоритм захардкожен
class PriceCalculator {
  calculate(items: Item[], userType: string): number {
    let total = items.reduce((sum, item) => sum + item.price, 0);

    // Скидки вперемешку с основной логикой
    if (userType === "premium") {
      total *= 0.9;  // -10%
    } else if (userType === "vip") {
      total *= 0.8;  // -20%
    } else if (userType === "employee") {
      total *= 0.7;  // -30%
    }

    // Акции
    if (isBlackFriday()) {
      total *= 0.85;
    }

    // Бонусы
    if (items.length > 10) {
      total *= 0.95;
    }

    return total;
  }
}
// 50+ строк, невозможно тестировать отдельно
```

### Решение: Strategy

```typescript
// Интерфейс стратегии
interface DiscountStrategy {
  apply(total: number, context: OrderContext): number;
}

// Конкретные стратегии — каждая делает ОДНО
class PremiumDiscount implements DiscountStrategy {
  apply(total: number): number {
    return total * 0.9;
  }
}

class VIPDiscount implements DiscountStrategy {
  apply(total: number): number {
    return total * 0.8;
  }
}

class BlackFridayDiscount implements DiscountStrategy {
  apply(total: number, context: OrderContext): number {
    if (context.isBlackFriday) {
      return total * 0.85;
    }
    return total;
  }
}

class BulkOrderDiscount implements DiscountStrategy {
  apply(total: number, context: OrderContext): number {
    if (context.itemCount > 10) {
      return total * 0.95;
    }
    return total;
  }
}

// Калькулятор использует стратегии
class PriceCalculator {
  private strategies: DiscountStrategy[] = [];

  addStrategy(strategy: DiscountStrategy) {
    this.strategies.push(strategy);
    return this; // Для chaining
  }

  calculate(items: Item[], context: OrderContext): number {
    let total = items.reduce((sum, item) => sum + item.price, 0);

    // Применяем все стратегии по очереди
    for (const strategy of this.strategies) {
      total = strategy.apply(total, context);
    }

    return total;
  }
}

// Использование — комбинируй как хочешь
const calculator = new PriceCalculator()
  .addStrategy(new PremiumDiscount())
  .addStrategy(new BlackFridayDiscount())
  .addStrategy(new BulkOrderDiscount());

const finalPrice = calculator.calculate(cartItems, {
  isBlackFriday: true,
  itemCount: 15
});

// Тестирование — каждая стратегия отдельно
test("PremiumDiscount applies 10% off", () => {
  const strategy = new PremiumDiscount();
  expect(strategy.apply(100)).toBe(90);
});
```

### Когда использовать

```
✅ Используй Strategy когда:
• Есть несколько вариантов алгоритма
• Алгоритм может меняться в runtime
• Хочешь избавиться от if/else цепочек
• Нужно тестировать варианты отдельно

❌ Не используй когда:
• Алгоритм один и не меняется
• Различия минимальны (один if)
```

### ⚠️ Anti-Pattern: Strategy для одного алгоритма

```typescript
// ПЛОХО: Strategy без вариантов
interface SortStrategy {
  sort(arr: number[]): number[];
}

class QuickSortStrategy implements SortStrategy {
  sort(arr: number[]) { return arr.sort((a, b) => a - b); }
}

class Sorter {
  constructor(private strategy: SortStrategy) {}
  sort(arr: number[]) { return this.strategy.sort(arr); }
}

// Вопрос: где другие стратегии?
// Если всегда QuickSort — зачем абстракция?

// ДОСТАТОЧНО:
function sort(arr: number[]) {
  return arr.sort((a, b) => a - b);
}
```

**Признаки злоупотребления Strategy:**
- Только одна ConcreteStrategy
- Стратегия никогда не меняется в runtime
- Алгоритмы почти идентичны (отличаются одной строкой)
- Добавление стратегии = копирование 90% кода

> "If the algorithms are very simple or similar, or closely linked with the data or state of your classes, using the strategy pattern can be redundant." — [LinkedIn: When Strategy is Overkill](https://www.linkedin.com/advice/3/when-strategy-pattern-useful-overkill-skills-object-oriented-design)

---

## Observer: реакция на события

### Intent (Зачем)

**Проблема:** Объект должен уведомлять другие объекты об изменениях, но не должен знать о них напрямую. Иначе — tight coupling.

**Решение:** Объект (Subject) ведёт список подписчиков (Observers) и уведомляет их при изменении состояния. Подписчики регистрируются сами.

### Participants (Ключевые компоненты)

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Subject** | Интерфейс для attach/detach observers | Без него нет управления подписками |
| **ConcreteSubject** | Хранит состояние, уведомляет observers | Источник событий |
| **Observer** | Интерфейс с методом update() | Контракт для всех подписчиков |
| **ConcreteObserver** | Реагирует на уведомления | **ВАЖНО:** хранит ссылку на Subject для синхронизации |

```
┌─────────────────────────────────────────────────────────────┐
│                       OBSERVER                              │
├─────────────────────────────────────────────────────────────┤
│   Subject (interface)           Observer (interface)        │
│   ├── attach(observer)          └── update()                │
│   ├── detach(observer)                 ↑                    │
│   └── notify()                  ConcreteObserverA           │
│          ↑                      ConcreteObserverB           │
│   ConcreteSubject                                           │
│   ├── state                                                 │
│   └── notify() { observers.forEach(o => o.update()) }       │
└─────────────────────────────────────────────────────────────┘
```

**Ключевой момент:** Subject и Observer связаны только через интерфейс. Subject не знает конкретных типов observers.

### Проблема (без паттерна)

```typescript
// Плохо: всё связано напрямую
class Order {
  complete() {
    this.status = "completed";

    // Order знает обо ВСЕХ, кто зависит от него
    emailService.sendConfirmation(this);
    inventoryService.updateStock(this.items);
    analyticsService.trackPurchase(this);
    loyaltyService.addPoints(this.user, this.total);
    notificationService.pushToMobile(this.user);
    // Каждый новый сервис = изменение Order
  }
}
```

### Решение: Observer (Event-Driven)

```typescript
// Типы событий
type EventMap = {
  "order:completed": { order: Order };
  "order:cancelled": { order: Order; reason: string };
  "user:registered": { user: User };
};

// Event Emitter (упрощённая версия)
class EventBus {
  private listeners: Map<string, Set<Function>> = new Map();

  on<K extends keyof EventMap>(
    event: K,
    callback: (data: EventMap[K]) => void
  ) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Возвращаем функцию отписки
    return () => this.listeners.get(event)?.delete(callback);
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]) {
    this.listeners.get(event)?.forEach(cb => cb(data));
  }
}

// Глобальный event bus
const events = new EventBus();

// Order теперь не знает о подписчиках
class Order {
  complete() {
    this.status = "completed";
    events.emit("order:completed", { order: this });
    // Всё! Order не знает кто слушает
  }
}

// Подписчики регистрируются сами
class EmailService {
  constructor() {
    events.on("order:completed", ({ order }) => {
      this.sendConfirmation(order);
    });
  }
}

class InventoryService {
  constructor() {
    events.on("order:completed", ({ order }) => {
      this.updateStock(order.items);
    });
  }
}

class AnalyticsService {
  constructor() {
    events.on("order:completed", ({ order }) => {
      this.trackPurchase(order);
    });

    events.on("order:cancelled", ({ order, reason }) => {
      this.trackCancellation(order, reason);
    });
  }
}

// Добавить новый сервис = создать класс, подписаться
// Order не меняется!
class TelegramNotifier {
  constructor() {
    events.on("order:completed", ({ order }) => {
      this.notify(order.user, "Заказ оформлен!");
    });
  }
}
```

### React: встроенный Observer

```tsx
// React hooks — это Observer под капотом
function OrderStatus({ orderId }: { orderId: string }) {
  // Компонент "подписан" на изменения состояния
  const [status, setStatus] = useState("pending");

  useEffect(() => {
    // Подписка на внешние события
    const unsubscribe = orderService.subscribe(orderId, (newStatus) => {
      setStatus(newStatus);  // Вызовет ре-рендер
    });

    return unsubscribe;  // Отписка при размонтировании
  }, [orderId]);

  return <div>Status: {status}</div>;
}
```

### Когда использовать

```
✅ Используй Observer когда:
• Изменение одного объекта должно влиять на другие
• Количество зависимых объектов неизвестно заранее
• Нужна слабая связанность (loose coupling)
• Event-driven архитектура

❌ Не используй когда:
• Связь 1-к-1 (проще вызвать напрямую)
• Порядок обработки критичен
• Нужна синхронная гарантия выполнения
```

### ⚠️ Anti-Pattern: Lapsed Listener Problem (Memory Leak)

**Одна из самых опасных проблем Observer паттерна** — утечки памяти из-за забытых подписок.

```typescript
// ПЛОХО: Observer не отписывается
class StockDisplay {
  constructor(private stockTracker: StockTracker) {
    // Подписались...
    stockTracker.subscribe(this);
  }

  update(price: number) {
    console.log(`Price: ${price}`);
  }

  // Пользователь закрыл окно, объект "уничтожен"
  // НО stockTracker всё ещё держит ссылку на this!
  // → StockDisplay НЕ собирается garbage collector
  // → Memory leak
}
```

**Почему это происходит:**

Subject держит **strong reference** на Observer. Даже если Observer больше не нужен, GC не может его удалить, потому что на него есть ссылка.

```
Subject.observers = [observer1, observer2, ...]
                          ↑
            GC не может удалить — есть ссылка
```

**Решение 1: Явная отписка**

```typescript
class StockDisplay {
  private unsubscribe: () => void;

  constructor(stockTracker: StockTracker) {
    this.unsubscribe = stockTracker.subscribe(this);
  }

  destroy() {
    this.unsubscribe();  // ОБЯЗАТЕЛЬНО!
  }
}
```

**Решение 2: Weak References (если язык поддерживает)**

```typescript
// Java/Kotlin: WeakReference<Observer>
// JavaScript: WeakRef (ES2021)
class Subject {
  private observers = new Set<WeakRef<Observer>>();

  notify() {
    for (const ref of this.observers) {
      const observer = ref.deref();
      if (observer) observer.update();
      else this.observers.delete(ref);  // Cleanup
    }
  }
}
```

**В React это встроено:**

```tsx
useEffect(() => {
  const unsubscribe = store.subscribe(handleChange);
  return () => unsubscribe();  // Cleanup при unmount
}, []);
```

> "The lapsed listener problem is a common source of memory leaks for object-oriented programming languages, among the most common ones for garbage collected languages." — [Wikipedia: Lapsed Listener Problem](https://en.wikipedia.org/wiki/Lapsed_listener_problem)

---

## Decorator: добавить поведение без наследования

### Intent (Зачем)

**Проблема:** Нужно добавить поведение к объекту динамически. Наследование не подходит — комбинаторный взрыв классов (2^n для n опций).

**Решение:** "Обернуть" объект в другой объект с таким же интерфейсом. Обёртка делегирует вызовы + добавляет своё поведение.

### Participants (Ключевые компоненты)

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Component** | Общий интерфейс для объектов и декораторов | Без него декоратор несовместим с объектом |
| **ConcreteComponent** | Базовый объект, который декорируем | То, что оборачиваем |
| **Decorator** | Абстрактный декоратор, хранит ссылку на Component | **КЛЮЧЕВОЙ!** Связывает цепочку |
| **ConcreteDecorator** | Добавляет конкретное поведение | Реальное расширение функциональности |

```
┌─────────────────────────────────────────────────────────────┐
│                       DECORATOR                             │
├─────────────────────────────────────────────────────────────┤
│   Component (interface)                                     │
│   └── operation()                                           │
│          ↑                                                  │
│   ┌──────┴───────────┐                                      │
│   │                  │                                      │
│   ConcreteComponent  Decorator (abstract)                   │
│   operation()        ├── component: Component               │
│                      └── operation() {                      │
│                            component.operation()            │
│                          }                                  │
│                               ↑                             │
│                      ConcreteDecoratorA                     │
│                      operation() {                          │
│                        super.operation()                    │
│                        // + дополнительное поведение        │
│                      }                                      │
└─────────────────────────────────────────────────────────────┘
```

**Почему Decorator (abstract) важен:**
- Хранит ссылку на **wrapped component**
- Реализует **делегирование** (по умолчанию просто вызывает component.operation())
- Позволяет **стековать** декораторы (decorator → decorator → component)

### Проблема (без паттерна)

```typescript
// Плохо: комбинаторный взрыв классов
class Coffee { cost() { return 5; } }
class CoffeeWithMilk extends Coffee { cost() { return 6; } }
class CoffeeWithSugar extends Coffee { cost() { return 5.5; } }
class CoffeeWithMilkAndSugar extends Coffee { cost() { return 6.5; } }
class CoffeeWithMilkAndSugarAndVanilla extends Coffee { ... }
// 2^n классов для n добавок
```

### Решение: Decorator

```typescript
interface Coffee {
  cost(): number;
  description(): string;
}

class SimpleCoffee implements Coffee {
  cost() { return 5; }
  description() { return "Coffee"; }
}

// Базовый декоратор
abstract class CoffeeDecorator implements Coffee {
  constructor(protected coffee: Coffee) {}

  cost() { return this.coffee.cost(); }
  description() { return this.coffee.description(); }
}

// Конкретные декораторы
class MilkDecorator extends CoffeeDecorator {
  cost() { return this.coffee.cost() + 1; }
  description() { return this.coffee.description() + ", milk"; }
}

class SugarDecorator extends CoffeeDecorator {
  cost() { return this.coffee.cost() + 0.5; }
  description() { return this.coffee.description() + ", sugar"; }
}

class VanillaDecorator extends CoffeeDecorator {
  cost() { return this.coffee.cost() + 1.5; }
  description() { return this.coffee.description() + ", vanilla"; }
}

// Комбинируй как угодно!
let order: Coffee = new SimpleCoffee();
order = new MilkDecorator(order);
order = new SugarDecorator(order);
order = new VanillaDecorator(order);

console.log(order.description());  // "Coffee, milk, sugar, vanilla"
console.log(order.cost());         // 8 (5 + 1 + 0.5 + 1.5)
```

### В реальном коде: middleware

```typescript
// Express middleware — это декораторы для request
app.use(cors());           // Добавляет CORS headers
app.use(helmet());         // Добавляет security headers
app.use(compression());    // Добавляет сжатие
app.use(rateLimiter());    // Добавляет rate limiting

// Каждый middleware "оборачивает" следующий
// request → cors → helmet → compression → handler → response
```

---

## Builder: сложное создание по шагам

### Intent (Зачем)

**Проблема:** Создание сложного объекта требует много параметров. Конструктор с 10+ аргументами нечитаем. Порядок параметров легко перепутать.

**Решение:** Выделить процесс создания в отдельный объект (Builder). Клиент вызывает методы пошагово, в конце получает готовый объект.

### Participants (Ключевые компоненты)

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Builder** | Интерфейс для пошагового создания | Определяет какие шаги возможны |
| **ConcreteBuilder** | Реализует шаги, собирает Product | Здесь живёт логика сборки |
| **Director** | Знает **порядок** вызова шагов | **ЧАСТО ПРОПУСКАЮТ!** Без него клиент сам управляет порядком |
| **Product** | Результат сборки | То, что мы создаём |

```
┌─────────────────────────────────────────────────────────────┐
│                       BUILDER                               │
├─────────────────────────────────────────────────────────────┤
│   Director                     Builder (interface)          │
│   ├── builder: Builder         ├── buildPartA()             │
│   └── construct() {            ├── buildPartB()             │
│         builder.buildPartA()   └── getResult(): Product     │
│         builder.buildPartB()           ↑                    │
│       }                        ConcreteBuilder              │
│                                ├── product: Product         │
│                                └── getResult()              │
└─────────────────────────────────────────────────────────────┘
```

**Почему Director важен:**
- Инкапсулирует **алгоритм сборки** (порядок шагов)
- Клиент не знает деталей — просто вызывает `director.construct()`
- Можно иметь **разные Directors** для разных конфигураций

**Когда Director пропускают:**
- Fluent Builder (method chaining) — Director заменяется самим клиентом
- Простые случаи, где порядок неважен

### Проблема (без паттерна)

```typescript
// Плохо: конструктор с 10+ параметрами
const query = new SQLQuery(
  "users",           // table
  ["id", "name"],    // columns
  { age: 25 },       // where
  "name",            // orderBy
  "ASC",             // direction
  10,                // limit
  0,                 // offset
  true,              // distinct
  null,              // groupBy
  null               // having
);
// Что значит каждый параметр? Какой порядок?
```

### Решение: Builder

```typescript
class QueryBuilder {
  private query: Partial<QueryConfig> = {};

  from(table: string) {
    this.query.table = table;
    return this;
  }

  select(...columns: string[]) {
    this.query.columns = columns;
    return this;
  }

  where(conditions: Record<string, any>) {
    this.query.where = conditions;
    return this;
  }

  orderBy(column: string, direction: "ASC" | "DESC" = "ASC") {
    this.query.orderBy = { column, direction };
    return this;
  }

  limit(count: number) {
    this.query.limit = count;
    return this;
  }

  offset(count: number) {
    this.query.offset = count;
    return this;
  }

  distinct() {
    this.query.distinct = true;
    return this;
  }

  build(): string {
    // Валидация
    if (!this.query.table) throw new Error("Table is required");

    // Генерация SQL
    const columns = this.query.columns?.join(", ") || "*";
    const distinct = this.query.distinct ? "DISTINCT " : "";
    let sql = `SELECT ${distinct}${columns} FROM ${this.query.table}`;

    if (this.query.where) {
      const conditions = Object.entries(this.query.where)
        .map(([k, v]) => `${k} = '${v}'`)
        .join(" AND ");
      sql += ` WHERE ${conditions}`;
    }

    if (this.query.orderBy) {
      sql += ` ORDER BY ${this.query.orderBy.column} ${this.query.orderBy.direction}`;
    }

    if (this.query.limit) sql += ` LIMIT ${this.query.limit}`;
    if (this.query.offset) sql += ` OFFSET ${this.query.offset}`;

    return sql;
  }
}

// Использование — читается как предложение
const sql = new QueryBuilder()
  .from("users")
  .select("id", "name", "email")
  .where({ status: "active", role: "admin" })
  .orderBy("created_at", "DESC")
  .limit(10)
  .build();

// SELECT id, name, email FROM users
// WHERE status = 'active' AND role = 'admin'
// ORDER BY created_at DESC LIMIT 10
```

---

## Singleton: один экземпляр (⚠️ осторожно!)

### Intent (Зачем)

**Проблема:** Нужен ровно один экземпляр класса, доступный глобально (connection pool, logger, config).

**Решение:** Класс контролирует своё создание, предоставляя единственную точку доступа.

### Почему Singleton — "Король антипаттернов"

> "Singleton is considered 'the king of all anti-patterns.' Stay away from it at all costs." — [Yegor Bugayenko](https://www.yegor256.com/2016/02/03/design-patterns-and-anti-patterns.html)

| Проблема | Почему это плохо |
|----------|-----------------|
| **Скрытые зависимости** | Код использует `getInstance()` — зависимость неявная |
| **Global state** | По сути это глобальная переменная с "красивым" API |
| **Нарушает SRP** | Класс отвечает за бизнес-логику И за своё создание |
| **Сложно тестировать** | Нельзя подменить mock без хаков |
| **Concurrency issues** | Double-checked locking и другие ужасы |

### Если всё же нужен Singleton

```typescript
class DatabaseConnection {
  private static instance: DatabaseConnection;
  private connection: Pool;

  private constructor() {
    this.connection = new Pool(config);
  }

  static getInstance(): DatabaseConnection {
    if (!DatabaseConnection.instance) {
      DatabaseConnection.instance = new DatabaseConnection();
    }
    return DatabaseConnection.instance;
  }

  query(sql: string) {
    return this.connection.query(sql);
  }
}

const db1 = DatabaseConnection.getInstance();
const db2 = DatabaseConnection.getInstance();
db1 === db2  // true
```

### ✅ Лучшая альтернатива: Dependency Injection

```typescript
// Вместо Singleton — создай один экземпляр при старте
// и передавай явно через конструктор

class UserService {
  constructor(private db: DatabaseConnection) {}  // Явная зависимость!

  getUser(id: string) {
    return this.db.query(`SELECT * FROM users WHERE id = ?`, [id]);
  }
}

// При старте приложения
const db = new DatabaseConnection(config);  // Один экземпляр
const userService = new UserService(db);    // Передаём явно

// В тестах
const mockDb = new MockDatabase();
const testService = new UserService(mockDb);  // Легко тестировать!
```

**Преимущества DI:**
- Зависимости **явные** (видны в конструкторе)
- **Легко тестировать** (подменяем mock)
- **Нет глобального состояния**
- Следует **Single Responsibility**

---

## Шпаргалка: когда какой паттерн

```
┌─────────────────────────────────────────────────────────────────┐
│                     ВЫБОР ПАТТЕРНА                              │
├────────────────────────┬────────────────────────────────────────┤
│ ПРОБЛЕМА               │ ПАТТЕРН                                │
├────────────────────────┼────────────────────────────────────────┤
│ Создать объект,        │ Factory                                │
│ тип в runtime          │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Много параметров       │ Builder                                │
│ при создании           │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Выбор алгоритма        │ Strategy                               │
│ в runtime              │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Реакция на событие     │ Observer                               │
│ без связанности        │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Добавить поведение     │ Decorator                              │
│ динамически            │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Упростить сложный      │ Facade                                 │
│ интерфейс              │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Адаптировать           │ Adapter                                │
│ несовместимый API      │                                        │
├────────────────────────┼────────────────────────────────────────┤
│ Объект с состояниями   │ State                                  │
│ и переходами           │                                        │
└────────────────────────┴────────────────────────────────────────┘
```

---

## Подводные камни

### Проблема 1: Паттерн ради паттерна

```
// Не нужно:
class UserFactory {
  create(name: string) {
    return new User(name);
  }
}

// Достаточно:
new User(name);

Паттерн оправдан когда решает РЕАЛЬНУЮ проблему
Если код проще без паттерна — не используй паттерн
```

### Проблема 2: Неправильный выбор

```
Нужно: выбрать алгоритм сортировки
Выбрали: Factory
Правильно: Strategy

Нужно: отправить уведомления при событии
Выбрали: Strategy
Правильно: Observer

Паттерны решают КОНКРЕТНЫЕ проблемы
Сначала пойми проблему, потом ищи паттерн
```

### Проблема 3: Over-engineering

```
Проект на 3 месяца с 1 разработчиком:

Плохо: "Давай сразу заложим Factory + Strategy + Observer + DI"
Хорошо: "Напишем просто, отрефакторим когда понадобится"

Преждевременная абстракция хуже дублирования
YAGNI: You Ain't Gonna Need It
```

---

## Actionable

**Начни с этих трёх:**
- **Factory** — когда создаёшь объекты разных типов
- **Strategy** — когда есть if/else для выбора алгоритма
- **Observer** — когда нужна слабая связанность

**Как применять:**
```
1. Заметил проблему (дублирование, связанность)
2. Вспомнил подходящий паттерн
3. Применил минимально
4. НЕ применяй заранее "на всякий случай"
```

---

## Куда дальше

**Фундамент:**
→ [[clean-code-solid]] — SOLID принципы. Паттерны без SOLID — это заклинания без понимания магии.

**Применение в архитектуре:**
→ [[microservices-vs-monolith]] — как паттерны меняются в распределённых системах.
→ [[api-design]] — паттерны при проектировании API (Builder для запросов, Strategy для обработки).

**Практика в Kotlin:**
→ [[kotlin-oop]] — как паттерны реализуются в Kotlin (часто проще чем в Java благодаря data class, sealed class).

---

## Источники

### Первоисточники
- [GoF Book: Design Patterns (1994)](https://en.wikipedia.org/wiki/Design_Patterns) — оригинальная книга Gang of Four
- [OODesign.com](https://www.oodesign.com/) — детальные UML-диаграммы и участники паттернов

### Туториалы и справочники
- [Refactoring Guru: Design Patterns](https://refactoring.guru/design-patterns) — лучший визуальный справочник
- [Patterns.dev: Modern Patterns](https://www.patterns.dev/) — паттерны в контексте JavaScript/React
- [Source Making: Design Patterns](https://sourcemaking.com/design_patterns) — с примерами на разных языках
- [DoFactory: .NET Patterns](https://www.dofactory.com/net/design-patterns) — примеры с UML

### Критика и антипаттерны
- [Design Patterns and Anti-Patterns, Love and Hate](https://www.yegor256.com/2016/02/03/design-patterns-and-anti-patterns.html) — критика от Yegor Bugayenko
- [Abuse of Abstract Factories](https://freecontent.manning.com/dependency-injection-in-net-2nd-edition-abuse-of-abstract-factories/) — когда Factory вредит
- [Wikipedia: Lapsed Listener Problem](https://en.wikipedia.org/wiki/Lapsed_listener_problem) — memory leaks в Observer
- [Wikipedia: Anti-pattern](https://en.wikipedia.org/wiki/Anti-pattern) — общий обзор антипаттернов
- [ByteByteGo: OOP Patterns and Anti-Patterns](https://blog.bytebytego.com/p/oop-design-patterns-and-anti-patterns) — что работает, что нет

### Статьи по конкретным паттернам
- [Strategy Pattern: When Useful vs Overkill](https://www.linkedin.com/advice/3/when-strategy-pattern-useful-overkill-skills-object-oriented-design)
- [Factory Method Pattern](https://www.oodesign.com/factory-method-pattern) — детальный разбор участников
- [Observer Pattern Pitfalls](https://themorningdev.com/observer-pattern/) — 7 критических ошибок

---

## Связь с другими темами

### [[clean-code-solid]]

SOLID-принципы — теоретический фундамент, на котором стоят Design Patterns. Каждый паттерн GoF воплощает один или несколько принципов SOLID: Strategy реализует Open/Closed (новые алгоритмы без изменения контекста), Observer — Dependency Inversion (Subject зависит от абстракции Observer, не от конкретных подписчиков), ISP воплощается через role interfaces в Adapter и Decorator. Изучение SOLID до паттернов позволяет понимать ПОЧЕМУ паттерн устроен именно так, а не просто запоминать структуру.

### [[microservices-vs-monolith]]

В распределённых системах классические GoF-паттерны трансформируются. Factory становится Service Registry, Observer превращается в Event Bus (Kafka, RabbitMQ), Strategy — в API Gateway с routing rules. Decorator реализуется через middleware/sidecar (Istio, Envoy). Понимание паттернов на уровне классов даёт интуицию для архитектурных паттернов на уровне сервисов, но важно учитывать сетевую задержку и partial failure, которых нет в монолите.

### [[api-design]]

API Design активно использует Design Patterns: Builder для формирования сложных запросов, Strategy для выбора формата ответа (JSON, XML, Protobuf), Facade для упрощения сложного backend в единый API endpoint. Понимание паттернов помогает проектировать API, которые легко расширяются (Open/Closed) и не навязывают клиентам лишнюю функциональность (Interface Segregation). Антипаттерн God Endpoint — это тот же God Class, только на уровне REST API.

---

**Последняя верификация**: 2025-12-19
**Уровень достоверности**: high

---

---

## Проверь себя

> [!question]- Почему использование паттерна Factory для создания `new User(name)` — это антипаттерн?
> Потому что Factory оправдана когда: тип объекта определяется в runtime, создание сложное (много зависимостей), или нужна возможность легко добавлять новые типы. Для простого `new User(name)` Factory — это обёртка без добавленной ценности (лишний слой индирекции). Ключевой признак злоупотребления: Factory создаёт только один тип и метод `create()` просто вызывает `new X()`.

> [!question]- В чём главная опасность паттерна Observer и как с ней бороться?
> Lapsed Listener Problem — утечки памяти. Subject держит strong reference на Observer, и даже если Observer больше не нужен, GC не может его удалить. Решения: явная отписка (unsubscribe) при уничтожении Observer, использование WeakRef (ES2021, Java WeakReference), или встроенные механизмы cleanup (как return в useEffect в React).

> [!question]- Сравните: когда лучше использовать Strategy, а когда Observer?
> Strategy — когда нужно выбрать один алгоритм из нескольких в runtime (например, способ расчёта скидки). Observer — когда изменение одного объекта должно уведомить неизвестное число других объектов (например, завершение заказа уведомляет email, SMS, аналитику). Разница: Strategy про выбор "как делать", Observer про "кто должен узнать".

> [!question]- Почему Singleton называют "королём антипаттернов", хотя он решает реальную задачу?
> Singleton скрывает зависимости (через getInstance()), создаёт глобальное состояние, нарушает SRP (класс управляет и логикой, и своим созданием), затрудняет тестирование. Альтернатива — Dependency Injection: один экземпляр создаётся при старте приложения и передаётся явно через конструктор. Результат тот же (один экземпляр), но зависимости явные и тестируемые.

---

## Ключевые карточки

Какие три категории паттернов GoF существуют и за что отвечает каждая?
?
Creational (создание объектов): Factory, Builder, Singleton. Structural (структура и композиция): Adapter, Decorator, Facade. Behavioral (поведение и взаимодействие): Strategy, Observer, Command.

Какие три компонента (Participants) обязательны для паттерна Strategy?
?
Strategy (интерфейс алгоритма), ConcreteStrategy (реализация конкретного алгоритма), Context (использует Strategy и делегирует ей работу). Без Context стратегии "висят в воздухе" — клиент напрямую связан с ними.

Чем Decorator отличается от наследования?
?
Decorator добавляет поведение динамически (в runtime) через композицию — объект оборачивается в другой объект с тем же интерфейсом. Наследование статическое (в compile-time) и создаёт комбинаторный взрыв классов (2^n для n опций). Decorator позволяет "стековать" обёртки в любых комбинациях.

Когда Builder оправдан, а когда — нет?
?
Оправдан при создании объекта с 5+ параметрами, где порядок легко перепутать. Не оправдан для простых конструкторов (2-3 параметра). Builder читается как предложение: `.from("users").select("id", "name").limit(10).build()`.

Что такое Lapsed Listener Problem?
?
Утечка памяти в паттерне Observer: Subject держит strong reference на Observer, GC не может удалить Observer даже если он больше не нужен. Решение: явная отписка, WeakRef, или cleanup-callback (как в React useEffect).

Как отличить Cargo Cult от обоснованного применения паттерна?
?
Cargo Cult — применение паттерна "потому что так правильно" без понимания проблемы. Обоснованное применение: 1) есть конкретная проблема, 2) паттерн решает именно эту проблему, 3) код без паттерна сложнее. Если код проще без паттерна — не используй паттерн.

В чём разница между Factory Method и Abstract Factory?
?
Factory Method — один метод создания объектов в подклассе Creator. Abstract Factory — семейство связанных объектов (например, UIFactory создаёт Button + Input + Modal для одной платформы). Abstract Factory группирует несколько Factory Method.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[functional-programming]] | FP-подход, где многие GoF-паттерны становятся тривиальными |
| Углубиться | [[kotlin-oop]] | Как паттерны реализуются в Kotlin (data class, sealed class) |
| Смежная тема | [[event-driven-architecture]] | Observer на уровне архитектуры — Event Bus, Kafka |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-01-09*
