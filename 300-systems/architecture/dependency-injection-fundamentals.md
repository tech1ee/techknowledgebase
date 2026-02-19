---
title: "Dependency Injection: фундаментальные концепции"
created: 2026-01-29
modified: 2026-01-29
type: deep-dive
status: published
area: architecture
confidence: high
cs-foundations:
  - dependency-inversion-principle
  - inversion-of-control
  - strategy-pattern
  - factory-pattern
  - composition-root
tags:
  - dependency-injection
  - solid
  - design-patterns
  - topic/architecture
  - ioc
  - type/deep-dive
  - level/beginner
related:
  - "[[solid-principles]]"
  - "[[design-patterns-overview]]"
  - "[[android-dependency-injection]]"
  - "[[spring-dependency-injection]]"
reading_time: 40
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Dependency Injection: фундаментальные концепции

Dependency Injection (DI) — паттерн проектирования, при котором зависимости объекта передаются ему извне, а не создаются внутри. Это фундаментальная техника для достижения слабой связности (loose coupling), тестируемости и гибкости архитектуры.

> **Prerequisites:**
> - Понимание ООП (классы, интерфейсы, наследование)
> - Базовое знакомство с SOLID принципами
> - Понимание unit-тестирования

---

## Терминология

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Dependency** | Объект, который нужен другому объекту для работы | Инструмент, нужный рабочему |
| **Injection** | Передача зависимости объекту извне | Выдача инструмента рабочему |
| **Consumer/Client** | Класс, который использует зависимость | Рабочий |
| **Service** | Класс, предоставляющий функциональность | Инструмент |
| **Container/Injector** | Механизм, который создаёт и передаёт зависимости | Склад инструментов |
| **Composition Root** | Единственное место, где собирается граф объектов | Точка сборки |
| **Scope/Lifetime** | Время жизни зависимости | Срок аренды инструмента |

---

## Зачем это нужно: проблема жёстких зависимостей

### Код без DI

```java
// ❌ Жёсткие зависимости — класс сам создаёт то, что ему нужно
public class OrderService {
    // Прямое создание зависимостей внутри класса
    private final EmailSender emailSender = new SmtpEmailSender();
    private final PaymentGateway paymentGateway = new StripePaymentGateway();
    private final OrderRepository repository = new MySqlOrderRepository();

    public void placeOrder(Order order) {
        // Бизнес-логика...
        paymentGateway.charge(order.getTotal());
        repository.save(order);
        emailSender.send(order.getCustomerEmail(), "Order confirmed");
    }
}
```

### Что не так с этим кодом

```
┌─────────────────────────────────────────────────────────────────┐
│                    ПРОБЛЕМЫ ЖЁСТКИХ ЗАВИСИМОСТЕЙ                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. НЕВОЗМОЖНО ТЕСТИРОВАТЬ                                      │
│  ─────────────────────────                                      │
│  • Unit-тест требует реальный SMTP сервер                       │
│  • Нельзя проверить логику без реального Stripe                 │
│  • Каждый тест делает запись в MySQL                            │
│                                                                 │
│  2. НЕЛЬЗЯ ИЗМЕНИТЬ РЕАЛИЗАЦИЮ                                  │
│  ─────────────────────────────                                  │
│  • Переход на SendGrid требует изменения OrderService           │
│  • Каждое изменение = риск сломать существующий код             │
│                                                                 │
│  3. НАРУШЕНИЕ SINGLE RESPONSIBILITY                              │
│  ───────────────────────────────                                │
│  • OrderService знает КАК создавать EmailSender                 │
│  • Знает конфигурацию SMTP, Stripe, MySQL                       │
│  • Смешана бизнес-логика и инфраструктурный код                 │
│                                                                 │
│  4. НЕВОЗМОЖНО ПЕРЕИСПОЛЬЗОВАТЬ                                 │
│  ─────────────────────────────                                  │
│  • В другом проекте нужен другой PaymentGateway                 │
│  • Нельзя использовать OrderService без Stripe                  │
│                                                                 │
│  5. СКРЫТЫЕ ЗАВИСИМОСТИ                                         │
│  ──────────────────────                                         │
│  • Сигнатура класса не показывает что ему нужно                 │
│  • "Сюрприз" при попытке использовать                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Код с DI

```java
// ✅ Dependency Injection — зависимости передаются извне
public class OrderService {
    private final EmailSender emailSender;
    private final PaymentGateway paymentGateway;
    private final OrderRepository repository;

    // Конструктор ДЕКЛАРИРУЕТ что нужно классу
    public OrderService(
        EmailSender emailSender,
        PaymentGateway paymentGateway,
        OrderRepository repository
    ) {
        this.emailSender = emailSender;
        this.paymentGateway = paymentGateway;
        this.repository = repository;
    }

    public void placeOrder(Order order) {
        // Только бизнес-логика, без создания объектов
        paymentGateway.charge(order.getTotal());
        repository.save(order);
        emailSender.send(order.getCustomerEmail(), "Order confirmed");
    }
}

// Теперь можно тестировать с mock-объектами
class OrderServiceTest {
    @Test
    void shouldSendEmailAfterOrder() {
        // Создаём mock-зависимости
        var mockEmail = mock(EmailSender.class);
        var mockPayment = mock(PaymentGateway.class);
        var mockRepo = mock(OrderRepository.class);

        // Инжектируем mock'и
        var service = new OrderService(mockEmail, mockPayment, mockRepo);

        service.placeOrder(testOrder);

        // Проверяем что email был отправлен
        verify(mockEmail).send(any(), eq("Order confirmed"));
    }
}
```

### Визуализация разницы

```
┌─────────────────────────────────────────────────────────────────┐
│          БЕЗ DI: Класс сам создаёт зависимости                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────────────────────────────────────┐                │
│    │              OrderService                 │                │
│    │                                          │                │
│    │   new SmtpEmailSender() ─────────────┐   │                │
│    │   new StripePaymentGateway() ────────┤   │                │
│    │   new MySqlOrderRepository() ────────┤   │                │
│    │                                      │   │                │
│    │   placeOrder() { ... }               │   │                │
│    │                                      │   │                │
│    └──────────────────────────────────────────┘                │
│                                              │                  │
│    Класс ВЛАДЕЕТ созданием зависимостей      │                  │
│    Невозможно подменить ─────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           С DI: Зависимости передаются извне                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────────┐                                              │
│    │  Injector/  │                                              │
│    │  Container  │                                              │
│    └──────┬──────┘                                              │
│           │ создаёт и передаёт                                  │
│           ▼                                                     │
│    ┌──────────────────────────────────────────┐                │
│    │              OrderService                 │                │
│    │                                          │                │
│    │   EmailSender ◄──────────────────────┐   │                │
│    │   PaymentGateway ◄───────────────────┤   │                │
│    │   OrderRepository ◄──────────────────┤   │                │
│    │                                      │   │                │
│    │   placeOrder() { ... }               │   │                │
│    │                                      │   │                │
│    └──────────────────────────────────────────┘                │
│                                              │                  │
│    Класс ПОЛУЧАЕТ готовые зависимости        │                  │
│    Легко подменить на mock ──────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## CS-фундамент: почему DI работает

### Dependency Inversion Principle (SOLID)

**Автор:** Robert C. Martin (Uncle Bob), 1996
**Источник:** "The Dependency Inversion Principle", C++ Report

**Формулировка:**

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."
>
> "Abstractions should not depend on details. Details should depend on abstractions."

**Перевод:**
- Высокоуровневые модули не должны зависеть от низкоуровневых. Оба должны зависеть от абстракций.
- Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций.

```
┌─────────────────────────────────────────────────────────────────┐
│              DEPENDENCY INVERSION PRINCIPLE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ БЕЗ DIP: Высокоуровневый зависит от низкоуровневого         │
│                                                                 │
│     ┌─────────────────┐                                         │
│     │  OrderService   │  ← High-level (бизнес-логика)           │
│     │  (high-level)   │                                         │
│     └────────┬────────┘                                         │
│              │ depends on                                       │
│              ▼                                                  │
│     ┌─────────────────┐                                         │
│     │ MySqlRepository │  ← Low-level (инфраструктура)           │
│     │  (low-level)    │                                         │
│     └─────────────────┘                                         │
│                                                                 │
│     Изменение MySQL → изменение OrderService                    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ✅ С DIP: Оба зависят от абстракции                            │
│                                                                 │
│     ┌─────────────────┐                                         │
│     │  OrderService   │                                         │
│     │  (high-level)   │                                         │
│     └────────┬────────┘                                         │
│              │ depends on                                       │
│              ▼                                                  │
│     ┌─────────────────┐  ← Абстракция (интерфейс)               │
│     │ OrderRepository │                                         │
│     │  (interface)    │                                         │
│     └────────▲────────┘                                         │
│              │ implements                                       │
│     ┌────────┴────────┐                                         │
│     │ MySqlRepository │  ← Деталь реализации                    │
│     │  (low-level)    │                                         │
│     └─────────────────┘                                         │
│                                                                 │
│     Изменение MySQL НЕ затрагивает OrderService                 │
│     Можно легко заменить на PostgresRepository                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Связь DIP и DI:**

DIP — это **принцип** (ПОЧЕМУ нужно зависеть от абстракций).
DI — это **техника** (КАК передавать абстракции в класс).

```java
// DIP говорит: зависи от абстракции
interface OrderRepository { ... }

// DI говорит: получай абстракцию через конструктор
class OrderService {
    public OrderService(OrderRepository repo) { ... }
}
```

### Inversion of Control (IoC)

**Автор:** Stefano Mazzocchi (Apache Avalon), 1998
**Популяризация:** Martin Fowler, 2004

**Формулировка:**

> "The control being inverted is how the dependent object is obtained."

**Hollywood Principle:**

> "Don't call us, we'll call you."

IoC — это **общий принцип**, при котором поток управления инвертируется. Вместо того чтобы ваш код вызывал библиотеку, библиотека/фреймворк вызывает ваш код.

```
┌─────────────────────────────────────────────────────────────────┐
│              INVERSION OF CONTROL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ТРАДИЦИОННЫЙ КОНТРОЛЬ                                          │
│  ─────────────────────                                          │
│                                                                 │
│    main() {                                                     │
│        UserService service = new UserService();                 │
│        EmailSender sender = new EmailSender();                  │
│        service.setEmailSender(sender);    // Вы контролируете   │
│        service.registerUser(...);                               │
│    }                                                            │
│                                                                 │
│    Ваш код решает:                                              │
│    • Что создавать                                              │
│    • Когда создавать                                            │
│    • Как соединять                                              │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ИНВЕРТИРОВАННЫЙ КОНТРОЛЬ                                       │
│  ────────────────────────                                       │
│                                                                 │
│    class UserService {                                          │
│        @Inject EmailSender sender;  // Контейнер инжектирует    │
│                                                                 │
│        void registerUser(...) {                                 │
│            sender.send(...);                                    │
│        }                                                        │
│    }                                                            │
│                                                                 │
│    Контейнер/фреймворк решает:                                  │
│    • Что создавать                                              │
│    • Когда создавать                                            │
│    • Как соединять                                              │
│                                                                 │
│    Ваш код только ДЕКЛАРИРУЕТ потребности                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Типы IoC:**

| Тип | Описание | Пример |
|-----|----------|--------|
| **Dependency Injection** | Зависимости передаются извне | Constructor/Setter injection |
| **Service Locator** | Код запрашивает зависимости из реестра | `ServiceLocator.get(EmailSender.class)` |
| **Template Method** | Фреймворк вызывает ваши методы | `onCreate()` в Android |
| **Event-driven** | Обработчики регистрируются, система вызывает | `onClick()` listeners |

**DI — это одна из форм IoC**, наиболее предпочтительная для управления зависимостями.

---

## Типы Dependency Injection

### Constructor Injection (рекомендуемый)

Зависимости передаются через конструктор.

```java
// ✅ Constructor Injection — лучший выбор для обязательных зависимостей
public class OrderService {
    private final EmailSender emailSender;
    private final PaymentGateway paymentGateway;

    // Зависимости передаются при создании объекта
    public OrderService(EmailSender emailSender, PaymentGateway paymentGateway) {
        this.emailSender = Objects.requireNonNull(emailSender);
        this.paymentGateway = Objects.requireNonNull(paymentGateway);
    }
}
```

**Преимущества:**

| Преимущество | Объяснение |
|--------------|------------|
| **Иммутабельность** | Поля `final`, нельзя изменить после создания |
| **Полная инициализация** | Объект либо создан полностью, либо не создан |
| **Явные зависимости** | Видно из сигнатуры конструктора что нужно |
| **Легко тестировать** | Просто передать mock'и в конструктор |
| **Нет null** | Можно проверить в конструкторе |

**Рекомендация Spring Team:**

> "The Spring team generally advocates constructor injection as it enables implementation of application components as immutable objects and ensures required dependencies are not null."

### Setter Injection (Method Injection)

Зависимости передаются через setter-методы.

```java
// Setter Injection — для опциональных зависимостей
public class OrderService {
    private EmailSender emailSender;
    private Logger logger;  // Опциональный

    @Required  // Spring: обязательная зависимость
    public void setEmailSender(EmailSender emailSender) {
        this.emailSender = emailSender;
    }

    // Опциональная зависимость с дефолтом
    public void setLogger(Logger logger) {
        this.logger = logger;
    }

    private Logger getLogger() {
        return logger != null ? logger : NullLogger.INSTANCE;
    }
}
```

**Когда использовать:**

| Сценарий | Почему Setter Injection |
|----------|------------------------|
| **Опциональные зависимости** | Можно не вызывать setter |
| **Значения по умолчанию** | Setter переопределяет дефолт |
| **Много зависимостей** | Избежать "telescoping constructor" |
| **Циклические зависимости** | Spring может разрешить через setter |
| **Реконфигурация** | Изменить зависимость после создания |

**Недостатки:**

```java
// ❌ Проблема: объект в неполном состоянии
OrderService service = new OrderService();
service.placeOrder(order);  // NullPointerException!
// Забыли вызвать setEmailSender()
```

### Field Injection (не рекомендуется)

Зависимости инжектируются напрямую в поля через reflection.

```java
// ⚠️ Field Injection — удобно, но проблематично
public class OrderService {
    @Inject  // или @Autowired в Spring
    private EmailSender emailSender;

    @Inject
    private PaymentGateway paymentGateway;
}
```

**Почему НЕ рекомендуется:**

| Проблема | Объяснение |
|----------|------------|
| **Скрытые зависимости** | Не видно из публичного API |
| **Сложно тестировать** | Нужен reflection или DI-контейнер |
| **Нет иммутабельности** | Поля не могут быть `final` |
| **Нарушает инкапсуляцию** | Reflection обходит private |
| **Tight coupling к DI** | Класс не работает без контейнера |

```java
// ❌ Как тестировать Field Injection?
class OrderServiceTest {
    @Test
    void test() {
        OrderService service = new OrderService();
        // Как установить emailSender? Оно private!

        // Вариант 1: Reflection (хрупко)
        Field field = OrderService.class.getDeclaredField("emailSender");
        field.setAccessible(true);
        field.set(service, mockSender);

        // Вариант 2: Использовать DI-контейнер в тестах (медленно)
    }
}
```

### Interface Injection (редко используется)

Зависимость определяет интерфейс, который реализует потребитель.

```java
// Interface Injection — исторический подход (Avalon framework)
interface EmailSenderAware {
    void setEmailSender(EmailSender sender);
}

public class OrderService implements EmailSenderAware {
    private EmailSender emailSender;

    @Override
    public void setEmailSender(EmailSender sender) {
        this.emailSender = sender;
    }
}

// Контейнер проверяет: реализует ли класс *Aware интерфейс?
// Если да — вызывает соответствующий setter
```

**Примеры в современных фреймворках:**

```java
// Spring: ApplicationContextAware
public class MyBean implements ApplicationContextAware {
    @Override
    public void setApplicationContext(ApplicationContext ctx) {
        // Получаем доступ к контексту
    }
}

// Android: LifecycleOwner (косвенно)
```

### Сравнение типов DI

```
┌─────────────────────────────────────────────────────────────────┐
│                    СРАВНЕНИЕ ТИПОВ DI                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Критерий          │ Constructor │ Setter │ Field │ Interface  │
│  ──────────────────┼─────────────┼────────┼───────┼──────────  │
│  Иммутабельность   │     ✅      │   ❌   │  ❌   │    ❌      │
│  Обязательность    │     ✅      │   ⚠️   │  ⚠️   │    ⚠️      │
│  Тестируемость     │     ✅      │   ✅   │  ❌   │    ✅      │
│  Явность           │     ✅      │   ⚠️   │  ❌   │    ⚠️      │
│  Простота          │     ✅      │   ✅   │  ✅   │    ❌      │
│  Циклы             │     ❌      │   ✅   │  ✅   │    ✅      │
│  ──────────────────┼─────────────┼────────┼───────┼──────────  │
│  Рекомендация      │  DEFAULT    │ Опцион │ Избег │   Редко    │
│                                                                 │
│  ✅ = хорошо   ⚠️ = зависит   ❌ = проблемно                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Правило выбора (Spring recommendation):**

> "Use constructor injection for mandatory dependencies and setter injection for optional dependencies."

---

## DI vs Service Locator

### Service Locator Pattern

```java
// Service Locator — класс сам запрашивает зависимости
public class OrderService {
    public void placeOrder(Order order) {
        // Класс сам "тянет" зависимости из локатора
        EmailSender sender = ServiceLocator.get(EmailSender.class);
        PaymentGateway gateway = ServiceLocator.get(PaymentGateway.class);

        gateway.charge(order.getTotal());
        sender.send(order.getCustomerEmail(), "Confirmed");
    }
}

// Где-то глобально
class ServiceLocator {
    private static Map<Class<?>, Object> services = new HashMap<>();

    public static void register(Class<?> type, Object instance) {
        services.put(type, instance);
    }

    public static <T> T get(Class<T> type) {
        return (T) services.get(type);
    }
}
```

### Почему Service Locator — антипаттерн

**Mark Seemann (автор "Dependency Injection in .NET"):**

> "The problem with Service Locator is that it hides complexity."

```
┌─────────────────────────────────────────────────────────────────┐
│              SERVICE LOCATOR: ПРОБЛЕМЫ                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. СКРЫТЫЕ ЗАВИСИМОСТИ                                         │
│  ──────────────────────                                         │
│                                                                 │
│  // Что нужно классу? Непонятно из сигнатуры!                   │
│  class OrderService {                                           │
│      void placeOrder() {                                        │
│          var x = ServiceLocator.get(...);  // Сюрприз!          │
│      }                                                          │
│  }                                                              │
│                                                                 │
│  vs                                                             │
│                                                                 │
│  // DI: всё видно из конструктора                               │
│  class OrderService {                                           │
│      OrderService(EmailSender e, PaymentGateway p) { ... }      │
│  }                                                              │
│                                                                 │
│  2. ОШИБКИ В RUNTIME                                            │
│  ───────────────────                                            │
│                                                                 │
│  ServiceLocator.get(EmailSender.class);                         │
│  // Если не зарегистрировано → Exception в runtime              │
│  // Компилятор не поможет                                       │
│                                                                 │
│  3. СЛОЖНО ТЕСТИРОВАТЬ                                          │
│  ─────────────────────                                          │
│                                                                 │
│  @Test void test() {                                            │
│      // Нужно настраивать глобальный ServiceLocator             │
│      ServiceLocator.register(EmailSender.class, mock);          │
│      // Тесты влияют друг на друга!                             │
│  }                                                              │
│                                                                 │
│  4. DISHONEST API                                               │
│  ───────────────                                                │
│                                                                 │
│  // API обманывает: выглядит просто, но требует настройки       │
│  var service = new OrderService();  // Кажется, что ready       │
│  service.placeOrder(order);  // CRASH: ServiceLocator empty     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Сравнение

| Критерий | Dependency Injection | Service Locator |
|----------|---------------------|-----------------|
| **Явность зависимостей** | ✅ Видно из конструктора | ❌ Скрыто внутри |
| **Compile-time проверка** | ✅ Ошибка компиляции | ❌ Runtime exception |
| **Тестируемость** | ✅ Передать mock в конструктор | ⚠️ Настраивать глобальное состояние |
| **Coupling к инфраструктуре** | ✅ Класс не знает о DI | ❌ Зависит от ServiceLocator |
| **Reusability** | ✅ Работает везде | ❌ Требует ServiceLocator |

### Когда Service Locator допустим

**Jimmy Bogard:**

> "Like any pattern, it's not so cut and dry."

Service Locator может быть оправдан:

1. **Legacy код** — постепенный рефакторинг
2. **Инфраструктурный код** — middleware, interceptors
3. **Фреймворки** — когда DI технически невозможен
4. **Cross-cutting concerns** — logging, telemetry

```java
// Пример: логирование как cross-cutting concern
public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    // Logger через "Service Locator" (LoggerFactory) — общепринятая практика
    // Не все зависимости стоит инжектировать
}
```

---

## История Dependency Injection

```
┌─────────────────────────────────────────────────────────────────┐
│              TIMELINE: ЭВОЛЮЦИЯ DI                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1994  Gang of Four — Design Patterns                           │
│        ─────────────────────────────                            │
│        Strategy, Factory, Abstract Factory — предтечи DI        │
│        "Favor composition over inheritance"                     │
│                                                                 │
│  1996  Robert C. Martin — Dependency Inversion Principle        │
│        ───────────────────────────────────────────────          │
│        C++ Report: "The Dependency Inversion Principle"         │
│        Теоретическое обоснование                                │
│                                                                 │
│  1998  Stefano Mazzocchi — Apache Avalon                        │
│        ──────────────────────────────                           │
│        Популяризация термина "Inversion of Control"             │
│        Первый IoC-контейнер для Java                            │
│                                                                 │
│  2002  Rod Johnson — Expert One-on-One J2EE                     │
│        ──────────────────────────────────                       │
│        Книга с концепциями, ставшими Spring Framework           │
│        Setter Injection описан                                  │
│                                                                 │
│  2003  Spring Framework 0.9 (SourceForge)                       │
│        ──────────────────────────────────                       │
│        Первый mainstream IoC-контейнер                          │
│        XML-конфигурация, Setter Injection                       │
│                                                                 │
│  2003  PicoContainer — Constructor Injection                    │
│        ─────────────────────────────────                        │
│        Paul Hammant, Aslak Hellesøy                             │
│        "Constructor injection более элегантен"                  │
│                                                                 │
│  DEC 2003  Термин "Dependency Injection" придуман               │
│        ───────────────────────────────────────                  │
│        Встреча в офисе ThoughtWorks, Лондон                     │
│        Присутствовали: Fowler, Rod Johnson, Paul Hammant        │
│                                                                 │
│  JAN 2004  Martin Fowler — статья                               │
│        ─────────────────────────                                │
│        "Inversion of Control Containers and                     │
│         the Dependency Injection pattern"                       │
│        Каноническое определение DI                              │
│                                                                 │
│  2007  Google Guice 1.0                                         │
│        ────────────────                                         │
│        Java 5 annotations вместо XML                            │
│        @Inject становится стандартом                            │
│                                                                 │
│  2009  JSR-330: @Inject                                         │
│        ─────────────────                                        │
│        Стандартизация DI annotations в Java EE                  │
│        javax.inject.Inject                                      │
│                                                                 │
│  2012  Dagger 1 (Square)                                        │
│        ────────────────                                         │
│        Compile-time DI для Android                              │
│        Быстрее чем reflection-based решения                     │
│                                                                 │
│  2015  Dagger 2 (Google)                                        │
│        ────────────────                                         │
│        100% compile-time, zero reflection                       │
│        Annotation processing                                    │
│                                                                 │
│  2017  Koin (Kotlin)                                            │
│        ────────────────                                         │
│        Kotlin DSL, runtime DI                                   │
│        Простота vs compile-time safety                          │
│                                                                 │
│  2020  Hilt (Google)                                            │
│        ─────────────                                            │
│        Dagger + Android Jetpack integration                     │
│        Официальная рекомендация для Android                     │
│                                                                 │
│  2024  Современное состояние                                    │
│        ─────────────────────                                    │
│        • Hilt 2.57 с KSP2 — Android стандарт                    │
│        • Koin 4.0 — Kotlin Multiplatform                        │
│        • Spring 6 — Java/Kotlin backend                         │
│        • .NET DI — built-in в ASP.NET Core                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ключевые фигуры

| Персона | Вклад |
|---------|-------|
| **Robert C. Martin** | Dependency Inversion Principle (1996) |
| **Stefano Mazzocchi** | Популяризация IoC, Apache Avalon (1998) |
| **Rod Johnson** | Spring Framework (2002) |
| **Martin Fowler** | Термин "Dependency Injection", каноническая статья (2004) |
| **Paul Hammant** | PicoContainer, Constructor Injection (2003) |
| **Bob Lee** | Google Guice, JSR-330 (2007) |
| **Jake Wharton** | Dagger 2 (2015) |
| **Mark Seemann** | "Dependency Injection in .NET", Service Locator critique |

---

## Composition Root

**Определение:** Единственное место в приложении, где собирается весь граф объектов.

```
┌─────────────────────────────────────────────────────────────────┐
│              COMPOSITION ROOT                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application Entry Point                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  COMPOSITION ROOT                        │   │
│  │                                                         │   │
│  │   // Все зависимости создаются ЗДЕСЬ                    │   │
│  │   EmailSender email = new SmtpEmailSender(config);      │   │
│  │   PaymentGateway payment = new StripeGateway(apiKey);   │   │
│  │   OrderRepository repo = new MySqlRepository(db);       │   │
│  │                                                         │   │
│  │   // Собираем граф                                      │   │
│  │   OrderService service = new OrderService(              │   │
│  │       email, payment, repo                              │   │
│  │   );                                                    │   │
│  │                                                         │   │
│  │   // Передаём в приложение                              │   │
│  │   Application app = new Application(service);           │   │
│  │   app.run();                                            │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION CODE                        │   │
│  │                                                         │   │
│  │   // Классы НЕ знают откуда пришли зависимости          │   │
│  │   // Не используют new для сервисов                     │   │
│  │   // Не используют ServiceLocator                       │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ПРАВИЛО: new для сервисов ТОЛЬКО в Composition Root           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Примеры Composition Root

**Console Application (Pure DI):**

```java
public class Main {
    public static void main(String[] args) {
        // === COMPOSITION ROOT ===
        var config = new Config(args);

        var emailSender = new SmtpEmailSender(config.getSmtpHost());
        var paymentGateway = new StripeGateway(config.getStripeKey());
        var repository = new MySqlOrderRepository(config.getDbUrl());

        var orderService = new OrderService(
            emailSender,
            paymentGateway,
            repository
        );

        var app = new OrderApplication(orderService);
        // === END COMPOSITION ROOT ===

        app.run();
    }
}
```

**Spring Boot:**

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        // Spring создаёт Composition Root автоматически
        SpringApplication.run(Application.class, args);
    }
}

// @Configuration классы — часть Composition Root
@Configuration
public class AppConfig {
    @Bean
    public OrderService orderService(
        EmailSender email,
        PaymentGateway payment,
        OrderRepository repo
    ) {
        return new OrderService(email, payment, repo);
    }
}
```

**Android Hilt:**

```kotlin
// Application — точка входа, Composition Root
@HiltAndroidApp
class MyApplication : Application()

// Modules описывают КАК создавать зависимости
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideOrderService(
        email: EmailSender,
        payment: PaymentGateway,
        repo: OrderRepository
    ): OrderService = OrderService(email, payment, repo)
}
```

---

## Связь с другими паттернами

### Strategy Pattern

DI — это способ применения Strategy паттерна.

```java
// Strategy: алгоритм может быть заменён
interface SortingStrategy {
    void sort(int[] array);
}

class QuickSort implements SortingStrategy { ... }
class MergeSort implements SortingStrategy { ... }

// DI инжектирует стратегию
class DataProcessor {
    private final SortingStrategy strategy;

    public DataProcessor(SortingStrategy strategy) {  // DI
        this.strategy = strategy;
    }
}
```

### Factory Pattern

Factory создаёт объекты, DI передаёт их.

```java
// Factory — когда нужно создавать объекты динамически
interface OrderFactory {
    Order create(Customer customer, List<Item> items);
}

class OrderService {
    private final OrderFactory factory;  // Инжектируем фабрику
    private final OrderRepository repo;

    public OrderService(OrderFactory factory, OrderRepository repo) {
        this.factory = factory;
        this.repo = repo;
    }

    public Order placeOrder(Customer customer, List<Item> items) {
        Order order = factory.create(customer, items);  // Фабрика создаёт
        return repo.save(order);
    }
}
```

### Decorator Pattern

DI позволяет легко добавлять декораторы.

```java
interface Logger {
    void log(String message);
}

class ConsoleLogger implements Logger { ... }
class TimestampDecorator implements Logger {
    private final Logger wrapped;

    public TimestampDecorator(Logger wrapped) {
        this.wrapped = wrapped;
    }

    public void log(String message) {
        wrapped.log("[" + Instant.now() + "] " + message);
    }
}

// В Composition Root легко собрать цепочку декораторов
Logger logger = new TimestampDecorator(
    new AsyncDecorator(
        new ConsoleLogger()
    )
);
```

---

## Мифы и заблуждения

### Миф 1: "DI = DI-контейнер"

**Реальность:** DI — это паттерн, контейнер — инструмент.

```java
// ✅ DI без контейнера (Pure DI / Poor Man's DI)
var service = new OrderService(
    new SmtpEmailSender(),
    new StripeGateway()
);

// Это тоже Dependency Injection!
// Контейнер просто автоматизирует сборку
```

### Миф 2: "DI усложняет код"

**Реальность:** DI делает сложность ВИДИМОЙ.

```java
// "Простой" код без DI
class OrderService {
    void placeOrder() {
        // 20 скрытых зависимостей внутри...
    }
}

// "Сложный" код с DI
class OrderService {
    OrderService(A a, B b, C c, D d, E e, F f, G g, H h, I i, J j) { }
    // Сложность была всегда, теперь она ВИДНА
    // Это сигнал к рефакторингу!
}
```

### Миф 3: "DI нужен всегда"

**Реальность:** Для маленьких проектов Manual DI или даже прямое создание достаточно.

```java
// Калькулятор — DI не нужен
class Calculator {
    int add(int a, int b) { return a + b; }
}

// Value objects — DI не нужен
class Money {
    Money(BigDecimal amount, Currency currency) { ... }
}

// Утилиты — DI обычно не нужен
class StringUtils {
    static String capitalize(String s) { ... }
}
```

### Миф 4: "Constructor Injection — единственный правильный способ"

**Реальность:** Setter injection валиден для опциональных зависимостей.

```java
class ReportGenerator {
    private final DataSource dataSource;  // Обязательная — constructor
    private Logger logger = NullLogger.INSTANCE;  // Опциональная — setter

    public ReportGenerator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public void setLogger(Logger logger) {
        this.logger = logger;
    }
}
```

### Миф 5: "@Singleton везде — хорошая идея"

**Реальность:** Overuse Singleton приводит к проблемам.

```java
// ❌ Всё Singleton
@Singleton UserSession session;      // Проблема: shared state между запросами!
@Singleton HttpRequest request;      // Проблема: request-specific данные!
@Singleton FormValidator validator;  // Проблема: stateful валидация!

// ✅ Правильные scopes
@Singleton DatabaseConnection db;          // OK: переиспользуем connection pool
@RequestScoped UserSession session;        // OK: новый для каждого запроса
@Prototype FormValidator validator;        // OK: новый экземпляр каждый раз
```

### Миф 6: "DI = тестируемость"

**Реальность:** DI УПРОЩАЕТ тестирование, но не гарантирует его.

```java
// С DI, но всё равно сложно тестировать
class BadService {
    private final Database db;

    public BadService(Database db) {
        this.db = db;
    }

    public void process() {
        // 500 строк смешанной логики
        // 20 вызовов db
        // Side effects везде
    }
}
// DI не спасёт от плохого дизайна
```

### Сводная таблица мифов

| Миф | Реальность |
|-----|------------|
| DI = контейнер | DI — паттерн, контейнер опционален |
| DI усложняет | DI делает сложность видимой |
| DI нужен всегда | Для маленьких проектов избыточен |
| Только Constructor | Setter для опциональных зависимостей |
| @Singleton везде | Используй правильные scopes |
| DI = тестируемость | DI упрощает, но не гарантирует |
| Field Injection удобен | Скрывает зависимости, ломает тесты |

---

## Когда НЕ использовать DI

### 1. Простые объекты (Value Objects, DTOs)

```java
// Нет смысла инжектировать
Money price = new Money(100, Currency.USD);
Point point = new Point(10, 20);
UserDto dto = new UserDto(name, email);
```

### 2. Утилиты и статические методы

```java
// Статические утилиты — DI не нужен
String result = StringUtils.capitalize(input);
int hash = Objects.hash(a, b, c);
```

### 3. Логгеры

```java
// Общепринятая практика — статическая фабрика
private static final Logger log = LoggerFactory.getLogger(MyClass.class);
// Хотя технически это Service Locator, для логгеров это OK
```

### 4. Очень маленькие проекты

```java
// Скрипт на 100 строк — Pure DI в main() достаточно
public static void main(String[] args) {
    var service = new MyService(new Dependency());
    service.run();
}
```

### 5. Внутренние детали реализации

```java
class OrderService {
    public void process(Order order) {
        // StringBuilder — внутренняя деталь, не инжектируем
        var sb = new StringBuilder();

        // ArrayList — внутренняя деталь
        var items = new ArrayList<Item>();
    }
}
```

## Связи

**Архитектура и паттерны:**
→ [[solid-principles]] — SOLID принципы, особенно Dependency Inversion Principle
→ [[design-patterns-overview]] — Strategy, Factory, Decorator — связанные паттерны

**Platform-specific DI:**
→ [[android-dependency-injection]] — обзор DI в Android (Hilt, Koin)
→ [[android-hilt-deep-dive]] — глубокое погружение в Hilt
→ [[android-koin-deep-dive]] — глубокое погружение в Koin
→ [[spring-dependency-injection]] — DI в Spring Framework
→ [[dotnet-dependency-injection]] — DI в .NET

---

## Источники

**Первоисточники:**
- [Martin Fowler — Inversion of Control Containers and the Dependency Injection pattern (2004)](https://martinfowler.com/articles/injection.html) — каноническая статья, определение DI
- [Robert C. Martin — The Dependency Inversion Principle (1996)](https://web.archive.org/web/20110714224327/http://www.objectmentor.com/resources/articles/dip.pdf) — оригинальная статья о DIP
- [Mark Seemann — Service Locator is an Anti-Pattern (2010)](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/) — критика Service Locator

**История:**
- [PicoContainer — Inversion of Control History](http://picocontainer.com/inversion-of-control-history.html) — история IoC контейнеров
- [Spring Framework History](https://springtutorials.com/spring-framework-history/) — эволюция Spring

**Книги:**
- "Dependency Injection Principles, Practices, and Patterns" — Mark Seemann, Steven van Deursen
- "Clean Architecture" — Robert C. Martin

---

*Проверено: 2026-01-29 | Актуально | На основе первоисточников (Fowler, Martin, Seemann)*

---

## Проверь себя

> [!question]- У вас Android-приложение с Hilt. Один из разработчиков предлагает использовать Field Injection (`@Inject lateinit var`) во всех ViewModel вместо Constructor Injection. Какие конкретные проблемы это вызовет при написании unit-тестов для ViewModel?
> С Field Injection тесты для ViewModel потребуют либо запуска Hilt-контейнера (что превращает unit-тест в интеграционный и замедляет его в 10-100 раз), либо использования reflection для установки private-полей (хрупко, ломается при рефакторинге). С Constructor Injection достаточно вызвать `MyViewModel(mockRepo, mockUseCase)` — тест быстрый, явный, без зависимости от фреймворка. Кроме того, Field Injection не позволяет сделать зависимости `val` (immutable), что создаёт риск их случайного изменения в runtime.

> [!question]- Почему Composition Root должен быть единственным местом создания сервисных зависимостей? Что произойдёт с архитектурой, если разрешить `new ServiceImpl()` в произвольных местах кода?
> Если `new` для сервисов разбросан по коду, каждое место создания становится неявной точкой связывания с конкретной реализацией. При смене реализации (например, миграция с MySQL на PostgreSQL) придётся искать и менять все точки создания вместо одной. Нарушается Single Responsibility — бизнес-логика смешивается с созданием объектов. Невозможно глобально управлять lifecycle (scopes) — один и тот же сервис может быть Singleton в одном месте и новым экземпляром в другом. Composition Root централизует сборку графа объектов, делая архитектуру предсказуемой и изменяемой.

> [!question]- Команда решает использовать Service Locator для всех зависимостей в новом проекте, аргументируя это тем, что "код проще — не нужен конструктор с 5 параметрами". Оцените это решение: какие долгосрочные последствия возникнут?
> Краткосрочный выигрыш в простоте обернётся долгосрочными проблемами. (1) Скрытые зависимости: API класса врёт — конструктор пуст, но класс требует 5 сервисов из локатора. Новый разработчик не поймёт зависимости без чтения всего кода. (2) Runtime-ошибки вместо compile-time: если забыть зарегистрировать сервис, это обнаружится только при выполнении, а не при компиляции. (3) Тесты будут влиять друг на друга через глобальное состояние ServiceLocator. (4) Аргумент "5 параметров слишком много" — это сигнал к декомпозиции класса (нарушение SRP), а не к сокрытию зависимостей. DI делает сложность видимой, а Service Locator её прячет.

> [!question]- В проекте есть класс `ReportGenerator`, который зависит от `DataSource` (обязательно) и `Logger` (опционально, есть дефолт `NullLogger`). Какой тип DI выбрать для каждой зависимости и почему? Как это связано с принципом Fail Fast?
> `DataSource` — Constructor Injection: зависимость обязательна, без неё объект не имеет смысла. Если `DataSource` не передан, ошибка возникает в момент создания объекта (fail fast), а не при вызове метода. Поле может быть `final` — иммутабельность. `Logger` — Setter Injection с дефолтным значением `NullLogger.INSTANCE`: зависимость опциональна, класс может работать без неё. Setter позволяет переопределить дефолт при необходимости. Это сочетание Constructor + Setter является рекомендацией Spring Team и обеспечивает баланс между безопасностью (обязательные зависимости гарантированы) и гибкостью (опциональные настраиваемы).

---

## Ключевые карточки

```
Что такое Dependency Injection и какую проблему он решает?
?
DI — паттерн проектирования, при котором зависимости объекта передаются ему извне, а не создаются внутри. Решает проблему жёсткой связности (tight coupling): без DI класс сам создаёт зависимости через `new`, что делает его невозможным для тестирования, переиспользования и замены реализации.
```

```
В чём разница между DIP (Dependency Inversion Principle) и DI (Dependency Injection)?
?
DIP — это принцип из SOLID, который говорит ЗАЧЕМ: высокоуровневые модули не должны зависеть от низкоуровневых, оба должны зависеть от абстракций. DI — это техника, которая говорит КАК: передавать абстракции в класс через конструктор, сеттер или интерфейс.
```

```
Почему Constructor Injection является рекомендуемым типом DI?
?
Constructor Injection обеспечивает иммутабельность (поля `final`), полную инициализацию (объект либо создан полностью, либо не создан), явность зависимостей (видно из сигнатуры конструктора), и лёгкость тестирования (достаточно передать mock в конструктор без reflection).
```

```
Что такое Composition Root и какое правило с ним связано?
?
Composition Root — единственное место в приложении, где собирается весь граф объектов. Правило: использовать `new` для сервисов ТОЛЬКО в Composition Root. Примеры: `main()` в консольных приложениях, `@Configuration` в Spring, `@HiltAndroidApp` + `@Module` в Android.
```

```
Почему Service Locator считается антипаттерном для бизнес-логики?
?
Service Locator скрывает зависимости (не видно из API класса), ошибки обнаруживаются только в runtime (если сервис не зарегистрирован), тесты влияют друг на друга через глобальное состояние, и API обманывает — класс выглядит простым, но требует настройки локатора.
```

```
Назовите 4 типа Inversion of Control (IoC).
?
(1) Dependency Injection — зависимости передаются извне через конструктор/сеттер. (2) Service Locator — код запрашивает зависимости из реестра. (3) Template Method — фреймворк вызывает ваши методы (например, `onCreate()` в Android). (4) Event-driven — обработчики регистрируются, система их вызывает (например, `onClick()`).
```

```
Когда НЕ нужно использовать Dependency Injection?
?
DI не нужен для: Value Objects и DTO (`new Money(100, USD)`), статических утилит (`StringUtils.capitalize()`), логгеров (статическая фабрика `LoggerFactory` — общепринятое исключение), внутренних деталей реализации (`StringBuilder`, `ArrayList`), и очень маленьких проектов.
```

```
Почему "DI усложняет код" — это миф?
?
DI не добавляет сложности, а делает существующую сложность ВИДИМОЙ. Конструктор с 10 параметрами показывает, что класс имеет 10 зависимостей — они были и без DI, просто скрыты внутри. Это сигнал к рефакторингу и декомпозиции класса, а не к сокрытию зависимостей.
```

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Обзор | [[architecture-overview]] | Карта всех архитектурных материалов |
| Углубление | [[solid-principles]] | SOLID принципы — теоретическая база для DI, особенно Dependency Inversion Principle |
| Углубление | [[design-patterns-overview]] | Strategy, Factory, Decorator — паттерны, тесно связанные с DI |
| Android | [[android-dependency-injection]] | Обзор DI-фреймворков в Android: Hilt, Koin, Dagger |
| Android | [[android-hilt-deep-dive]] | Compile-time DI с Hilt — официальная рекомендация Google для Android |
| Тестирование | [[testing-fundamentals]] | Как DI упрощает unit-тестирование через подмену зависимостей mock-объектами |
| Архитектура | [[microservices-vs-monolith]] | Как DI и IoC-контейнеры влияют на выбор между монолитом и микросервисами |
