---
title: "Clean Code и SOLID: код, который не стыдно показать"
created: 2025-11-24
modified: 2025-12-19
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/programming
  - programming/clean-code
  - programming/solid
  - best-practices
  - type/concept
  - level/intermediate
related:
  - "[[design-patterns]]"
  - "[[technical-debt]]"
  - "[[microservices-vs-monolith]]"
---

# Clean Code и SOLID: код, который не стыдно показать

80% времени мы читаем код, 20% — пишем. Чистый код экономит время всей команды. Но чистый код без меры = over-engineering. Баланс важнее догмы.

---

## TL;DR

**Clean Code** — код, который легко читать и изменять. Не "красивый", а понятный.

**SOLID** — 5 принципов ООП дизайна от Robert C. Martin (2000). Не законы физики, а эвристики для 80% случаев.

**Главная ошибка**: слепое следование правилам без понимания ПОЧЕМУ они существуют.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **SOLID** | 5 принципов объектно-ориентированного дизайна |
| **SRP** | Single Responsibility — один класс = одна причина изменений |
| **OCP** | Open/Closed — открыт для расширения, закрыт для изменений |
| **LSP** | Liskov Substitution — подтипы заменяют базовый тип |
| **ISP** | Interface Segregation — много специфичных интерфейсов лучше одного |
| **DIP** | Dependency Inversion — зависимости от абстракций, не реализаций |
| **Технический долг** | Стоимость будущих исправлений из-за быстрых решений сегодня |

---

## Зачем вообще "чистый код"?

### Проблема, которую решает Clean Code

```
Типичный проект через 6 месяцев:

"Нужно добавить новую фичу"
    ↓
Открываешь код
    ↓
function processData(d, t, x, flag1, flag2) {
  // TODO: fix later
  if (flag1 && !flag2 || x > 0) {
    for (let i = 0; i < d.length; i++) {
      if (d[i].t === t || (flag2 && d[i].x)) {
        // старый код, не трогать
        ...
      }
    }
  }
}
    ↓
"Что это делает?"
    ↓
2 часа на разбор 50 строк
    ↓
"Проще переписать"
    ↓
Технический долг растёт
```

### Статистика

| Факт | Источник |
|------|----------|
| 80% времени читаем код, 20% пишем | Robert C. Martin, "Clean Code" |
| Плохой код замедляет команду в 2-10 раз | Исследование Microsoft Research |
| "Потом поправлю" = никогда | Любой проект старше 6 месяцев |

### Цена плохого кода: реальный пример

**Knight Capital Group (1 августа 2012)**

Компания потеряла **$440 миллионов за 45 минут** из-за проблем с кодом:

- Устаревший код ("Power Peg") оставался в production годами после отключения функции
- При деплое новой версии на 8 серверов, на одном сервере забыли обновить код
- Старый код активировался флагом, который переиспользовали для новой функции
- Система SMARS не имела pre-trade risk checks — "просто выполняла ордера"
- Отсутствовали процедуры incident response — команда не знала что делать

**Причины провала:**
- Отсутствие code review при деплое
- Переиспользование флагов вместо удаления старого кода
- Нет автоматизированного деплоя (человеческий фактор)
- Нет kill switch и capital thresholds

> "The engineer who did the update still worked at KCG as of 2016. His entire management chain had been replaced." — [Henrico Dolfing, Case Study](https://www.henricodolfing.com/2019/06/project-failure-case-study-knight-capital.html)

---

## Clean Code: базовые правила

### Правило 1: Имена говорят сами за себя

**ПОЧЕМУ это важно:**

Мозг тратит когнитивные ресурсы на декодирование `d`, `t`, `x`. Понятные имена = меньше mental load = меньше багов.

```typescript
// Плохо — требует "перевод" в голове
const d = new Date();
const t = d.getTime();
const u = getUser(id);
const flag = u.a > 0;

// Хорошо — читается как текст
const currentDate = new Date();
const timestampMs = currentDate.getTime();
const user = getUserById(userId);
const hasPositiveBalance = user.accountBalance > 0;
```

**Конвенции именования:**

| Тип | Правило | Примеры |
|-----|---------|---------|
| Переменные | существительные | `user`, `orderTotal`, `isActive` |
| Функции | глаголы | `getUser()`, `calculateTotal()`, `validateEmail()` |
| Булевы | is/has/can/should | `isValid`, `hasAccess`, `canEdit` |
| Константы | SCREAMING_SNAKE | `MAX_RETRIES`, `API_BASE_URL` |

### Правило 2: Функции делают ОДНО

**ПОЧЕМУ это важно:**

Функция на 100 строк с 5 ответственностями — это 5 причин для изменения. Каждое изменение может сломать остальные 4 функции.

```typescript
// Плохо: функция делает 5 вещей — 5 причин для бага
async function processOrder(order: Order) {
  // 1. Валидация
  if (!order.items.length) throw new Error("Empty order");
  if (!order.userId) throw new Error("No user");

  // 2. Расчёт цены
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
    if (item.discount) total -= item.discount;
  }

  // 3. Проверка баланса
  const user = await db.users.findById(order.userId);
  if (user.balance < total) throw new Error("Insufficient funds");

  // 4. Списание
  user.balance -= total;
  await db.users.update(user);

  // 5. Уведомление
  await emailService.send(user.email, "Order confirmed", { order });

  return order;
}

// Хорошо: каждая функция — одна ответственность
async function processOrder(order: Order) {
  validateOrder(order);
  const total = calculateOrderTotal(order);
  const user = await getUser(order.userId);
  await chargeUser(user, total);
  const newOrder = await createOrder(order, total);
  await notifyOrderConfirmed(user, newOrder);
  return newOrder;
}
```

**Когда НЕ дробить:**

- Функция на 20 строк, которая делает одно логическое действие — OK
- 3 функции по 5 строк хуже одной на 15, если они используются только вместе

### Правило 3: Избегай магических чисел и строк

**ПОЧЕМУ это важно:**

`86400000` — это что? Миллисекунды в дне? Таймаут? Размер буфера? Через месяц не вспомнишь.

```typescript
// Плохо — что значит 1? 3? 86400000?
if (user.role === 1) { ... }
if (retries > 3) { ... }
setTimeout(fn, 86400000);

// Хорошо — самодокументирующийся код
const UserRole = { ADMIN: 1, USER: 2, GUEST: 3 } as const;
const MAX_RETRIES = 3;
const ONE_DAY_MS = 24 * 60 * 60 * 1000;

if (user.role === UserRole.ADMIN) { ... }
if (retries > MAX_RETRIES) { ... }
setTimeout(fn, ONE_DAY_MS);
```

### Правило 4: Комментарии — признак плохого кода (обычно)

**ПОЧЕМУ:**

Комментарий "что делает код" = код непонятен → исправь код, не пиши комментарий.

```typescript
// Плохо: комментарий объясняет непонятный код
// Проверяем, что пользователь активен и имеет доступ
if (u.s === 1 && u.p.includes(3)) { ... }

// Хорошо: код объясняет сам себя
const isActive = user.status === UserStatus.ACTIVE;
const hasAdminAccess = user.permissions.includes(Permission.ADMIN);
if (isActive && hasAdminAccess) { ... }
```

**Когда комментарии НУЖНЫ:**

| Ситуация | Пример |
|----------|--------|
| Объяснение ПОЧЕМУ | `// Binary search т.к. массив отсортирован и содержит миллионы элементов` |
| Ссылки на источники | `// Алгоритм: https://en.wikipedia.org/wiki/Levenshtein_distance` |
| TODO с контекстом | `// TODO(@user): убрать после миграции v2 API (PROJ-123)` |
| Предупреждения | `// WARNING: Не thread-safe, использовать только в main thread` |

### Правило 5: Обработка ошибок

**ПОЧЕМУ это важно:**

`catch (e) { return null }` — где ошибка? Сеть? 404? 500? Баг? Невозможно дебажить в production.

```typescript
// Плохо: ошибки теряются
async function getUser(id: string) {
  try {
    return await api.fetchUser(id);
  } catch (e) {
    return null;  // Какая ошибка? Непонятно
  }
}

// Хорошо: типизированные ошибки
class UserNotFoundError extends Error {
  constructor(public userId: string) {
    super(`User not found: ${userId}`);
    this.name = "UserNotFoundError";
  }
}

class NetworkError extends Error {
  constructor(public originalError: Error) {
    super(`Network error: ${originalError.message}`);
    this.name = "NetworkError";
  }
}

async function getUser(id: string): Promise<User> {
  try {
    const response = await api.fetchUser(id);
    if (response.status === 404) {
      throw new UserNotFoundError(id);
    }
    return response.data;
  } catch (error) {
    if (error instanceof UserNotFoundError) throw error;
    throw new NetworkError(error);
  }
}
```

---

## SOLID: 5 принципов хорошей архитектуры

### История и контекст

**Кто создал:** Robert C. Martin (Uncle Bob) описал принципы в статье "Design Principles and Design Patterns" (2000). Популяризовал в книге "Agile Software Development, Principles, Patterns, and Practices" (2003).

**Акроним SOLID:** придумал Michael Feathers около 2004 года.

**Зачем создали:** Martin заметил "запахи дизайна" — Rigidity (жёсткость), Fragility (хрупкость), Immobility (неподвижность). SOLID — ответ на эти проблемы.

> "These principles help answer: What are the symptoms of poor design? How can we know when the design of our systems is starting to degrade?" — Robert C. Martin

**Важно понимать:** SOLID — это эвристики, не законы. Их слепое применение ведёт к over-engineering. Понимание ПОЧЕМУ принцип существует важнее механического следования.

```
┌────┬──────────────────────────────────────────────────────────────┐
│ S  │ Single Responsibility — один класс, одна причина изменений   │
├────┼──────────────────────────────────────────────────────────────┤
│ O  │ Open/Closed — открыт для расширения, закрыт для изменения    │
├────┼──────────────────────────────────────────────────────────────┤
│ L  │ Liskov Substitution — подклассы заменяют родителей           │
├────┼──────────────────────────────────────────────────────────────┤
│ I  │ Interface Segregation — маленькие интерфейсы лучше большого  │
├────┼──────────────────────────────────────────────────────────────┤
│ D  │ Dependency Inversion — зависеть от абстракций                │
└────┴──────────────────────────────────────────────────────────────┘
```

---

### S — Single Responsibility Principle

#### Точное определение

**Оригинальная формулировка (Robert C. Martin):**

> "A class should have one, and only one, reason to change."

**Уточнение от самого Martin (2014):**

> "This principle is about people. When you write a software module, you want to make sure that when changes are requested, those changes can only originate from a single person, or rather, a single tightly coupled group of people representing a single narrowly defined business function."

Источник: [Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)

**Альтернативная формулировка:**

> "Gather together the things that change for the same reasons. Separate those things that change for different reasons."

Это другой способ определить **cohesion** (связность) и **coupling** (зацепление).

#### ГЛАВНОЕ ЗАБЛУЖДЕНИЕ

| Заблуждение | Правда |
|-------------|--------|
| "Класс должен делать одну вещь" | **Класс должен иметь одну причину для изменения** |
| SRP = маленькие классы | SRP = классы, которые меняются по одной причине |
| Функция = одно действие | Функция = один уровень абстракции |

**Почему это заблуждение опасно:**

Интерпретация "одна вещь" приводит к explosion of classes — проект из 10 классов превращается в 100 микроклассов. Каждый делает "одну вещь", но вместе они непонятны.

> "Often people who like tiny classes will use SRP to justify making many more even tinier classes. As an architecture decomposes components into smaller and smaller widgets, there sometimes comes an inflection point where the logic becomes expressed as many small classes spread out amongst a collection of files and folders." — [The Misunderstood SRP](https://www.softwareonthebrain.com/2022/01/the-misunderstood-single-responsibility.html)

#### Что такое "причина изменения"

**"Причина изменения" = Actor (актор/стейкхолдер)**

Пример: класс Employee в payroll системе:
- `calculatePay()` — меняется по требованию **бухгалтерии**
- `generateReport()` — меняется по требованию **менеджмента**
- `save()` — меняется по требованию **DBA**

Три актора = три причины изменения = нарушение SRP.

**Важно:** Debugging и refactoring — НЕ "причины изменения". SRP о бизнес-требованиях, не о технических улучшениях.

#### Пример нарушения и исправления

```typescript
// Нарушение SRP: 3 причины изменения (3 актора)
class Employee {
  calculatePay() { /* бухгалтерия */ }
  generateReport() { /* менеджмент */ }
  save() { /* DBA */ }
}

// Исправление: разделение по акторам
class Employee { /* только данные */ }
class PayCalculator { calculatePay(e: Employee) { } }
class ReportGenerator { generate(e: Employee) { } }
class EmployeeRepository { save(e: Employee) { } }
```

#### Когда НЕ применять

| Ситуация | Почему |
|----------|--------|
| Один актор для всего кода | Нет разных причин изменения |
| Прототип/MVP | Over-engineering убьёт скорость |
| Тесно связанная логика | Искусственное разделение хуже, чем cohesion |

> "Small classes are not automatically easier to understand. An explosion of classes creates complexity rather than reducing it." — [SOLID as an antipattern](https://blog.spinthemoose.com/2012/12/17/solid-as-an-antipattern/)

---

### O — Open/Closed Principle

#### Точное определение

**Оригинальная формулировка (Bertrand Meyer, 1988):**

> "A module will be said to be **open** if it is still available for extension."
> "A module will be said to be **closed** if it is available for use by other modules."

Источник: "Object-Oriented Software Construction" (1988)

**Meyer vs Martin — две интерпретации:**

| Meyer (1988) | Martin (1996) |
|--------------|---------------|
| Расширение через **наследование** | Расширение через **абстракции** |
| Наследование реализации | Полиморфизм и интерфейсы |
| Устарело (tight coupling) | Современный подход |

> "Robert C. Martin considered this principle as the most important principle of object-oriented design." — [Wikipedia](https://en.wikipedia.org/wiki/Open–closed_principle)

#### ГЛАВНОЕ ЗАБЛУЖДЕНИЕ

| Заблуждение | Правда |
|-------------|--------|
| "Никогда не модифицировать код" | **Минимизировать** изменения, не запрещать |
| OCP = всегда использовать интерфейсы | OCP = продумать точки расширения |
| Нельзя рефакторить | Рефакторинг != добавление функционала |

**Почему это заблуждение опасно:**

"Zero modification" интерпретация приводит к параличу — разработчики боятся трогать код. Но добавление новой функциональности **всегда** требует каких-то изменений (как минимум, регистрацию новой реализации).

> "Adding new functionalities to a codebase implies changing the existing code (refactoring), not only adding new code." — [Should We Follow OCP?](https://thevaluable.dev/open-closed-principle-revisited/)

#### Как правильно понимать OCP

**Цель OCP:** Добавление нового функционала не должно ломать существующий протестированный код.

**Механизм:** Выделить "точки расширения" (extension points) и защитить стабильный код.

```
Точки расширения:
┌─────────────────────────────────────────────────┐
│ PaymentProcessor  [ЗАКРЫТ для изменений]        │
│       ↓                                          │
│ PaymentHandler (interface) [ОТКРЫТ для расшир.] │
│       ↑                                          │
│ Card, PayPal, Crypto  [новые реализации]        │
└─────────────────────────────────────────────────┘
```

#### Пример

```typescript
// Плохо: каждый новый тип = изменение существующего кода
class PaymentProcessor {
  process(payment: Payment) {
    if (payment.type === "card") { /* ... */ }
    else if (payment.type === "paypal") { /* ... */ }
    // Добавить crypto? Менять этот файл
  }
}

// Хорошо: точка расширения через интерфейс
interface PaymentHandler {
  canHandle(p: Payment): boolean;
  process(p: Payment): Promise<Result>;
}

class PaymentProcessor {
  constructor(private handlers: PaymentHandler[]) {}
  process(payment: Payment) {
    const handler = this.handlers.find(h => h.canHandle(payment));
    return handler?.process(payment);
  }
}
// Добавить crypto = новый класс, PaymentProcessor не меняется
```

#### Когда НЕ применять

| Ситуация | Почему |
|----------|--------|
| 2-3 варианта навсегда | if/switch проще и понятнее |
| Неизвестно где будет расширение | Преждевременная абстракция |
| Performance-critical код | Виртуальные вызовы медленнее |

---

### L — Liskov Substitution Principle

#### Точное определение

**Оригинальная формулировка (Barbara Liskov, 1987):**

> "If for each object o₁ of type S there is an object o₂ of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o₁ is substituted for o₂, then S is a subtype of T."

**Простыми словами:** Если функция работает с базовым типом T, она должна корректно работать с любым подтипом S без изменений.

**Уточнение Liskov (2016):**

В интервью Liskov объяснила, что это была "informal rule". Позже с Jeannette Wing они формализовали её в статье "A behavioral notion of subtyping" (1994), введя понятие **behavioral subtyping**.

Источник: [Wikipedia - Liskov Substitution](https://en.wikipedia.org/wiki/Liskov_substitution_principle)

#### ГЛАВНОЕ ЗАБЛУЖДЕНИЕ

| Заблуждение | Правда |
|-------------|--------|
| LSP = наследование должно работать | LSP = **поведение** должно быть совместимо |
| Квадрат — это прямоугольник | Математически да, но **поведенчески** нет |
| Компилятор проверит LSP | LSP о **семантике**, не синтаксисе |

**Почему это заблуждение опасно:**

LSP — **semantic** принцип, не syntactic. Компилятор проверяет типы, но не поведение. Код компилируется, но ломается в runtime.

> "Strongly-typed OO languages force a consistent structure onto you, but not necessarily a consistent behavior. This can lead to runtime errors instead of compilation errors." — [SOLID in the wild](https://devonblog.com/software-development/solid-violations-wild-liskov-substitution-principle/)

#### Что такое "behavioral subtyping"

**Контракт базового типа включает:**
1. **Preconditions** — что ожидается на входе
2. **Postconditions** — что гарантируется на выходе
3. **Invariants** — что всегда истинно

**Правила LSP:**
- Подтип может **ослабить** preconditions (принимать больше)
- Подтип может **усилить** postconditions (гарантировать больше)
- Подтип **не может** нарушать invariants

#### Классический пример: Rectangle/Square

```typescript
// Нарушение LSP
class Rectangle {
  setWidth(w: number) { this.width = w; }  // Postcondition: height не меняется
  setHeight(h: number) { this.height = h; }
}

class Square extends Rectangle {
  setWidth(w: number) {
    this.width = w;
    this.height = w;  // НАРУШАЕТ postcondition!
  }
}
```

**Почему это нарушение:** `Rectangle.setWidth()` имеет implicit postcondition — "height не изменится". `Square` нарушает этот контракт.

#### Признаки нарушения LSP

| Признак | Почему это проблема |
|---------|---------------------|
| `instanceof` проверки | Клиент должен знать конкретный тип |
| `throw NotImplementedException` | Метод не поддерживается |
| Документация "не вызывать" | Контракт нарушен |
| Переопределение с другим поведением | Семантика изменена |

#### Когда НЕ применять строго

| Ситуация | Что делать |
|----------|------------|
| Legacy code | Документировать ограничения, не ломать существующее |
| Adapter pattern | Адаптер может частично реализовывать интерфейс |

---

### I — Interface Segregation Principle

#### Точное определение

**Оригинальная формулировка (Robert C. Martin):**

> "Clients should not be forced to depend upon interfaces that they do not use."

**История происхождения (Xerox, 1990-е):**

Martin разработал ISP консультируя Xerox. Проблема: класс `Job` использовался для печати, сканирования, факса, степлера. Каждая подсистема (Staple, Print) зависела от **всех** методов Job.

> "The design problem was that a single Job class was used by almost all of the tasks. This resulted in a 'fat' class with multitudes of methods specific to a variety of different clients." — [Wikipedia](https://en.wikipedia.org/wiki/Interface_segregation_principle)

Результат: изменение метода для степлера перекомпилировало модуль принтера.

#### ГЛАВНОЕ ЗАБЛУЖДЕНИЕ

| Заблуждение | Правда |
|-------------|--------|
| ISP = много маленьких интерфейсов | ISP = интерфейсы по **ролям клиентов** |
| Каждый метод — отдельный интерфейс | Методы группируются по **использованию** |
| ISP о размере интерфейса | ISP о **связях между клиентами** |

**Почему это заблуждение опасно:**

Дробление интерфейса на атомарные методы создаёт explosion of interfaces. Правильный подход — группировать методы по тому, какие клиенты их используют вместе.

**Ключевая проблема fat interfaces:**

> "Fat interfaces lead to inadvertent couplings between clients that ought otherwise to be isolated." — Robert C. Martin

Клиент A меняет метод X → перекомпиляция клиента B, который X не использует.

#### Пример: Xerox решение

```typescript
// Плохо: fat interface
interface Job {
  print(): void;
  staple(): void;
  fax(): void;
}

// Хорошо: role interfaces
interface Printable { print(): void; }
interface Stapleable { staple(): void; }
interface Faxable { fax(): void; }

class PrintJob implements Printable { print() { } }
class StapleJob implements Stapleable { staple() { } }
```

**Результат:** Изменение в Stapleable не затрагивает PrintJob.

#### Последствия нарушения ISP

| Проблема | Почему опасно |
|----------|---------------|
| **Пустые реализации** | `fax() { }` молча ничего не делает — скрытый баг |
| **Compile-time coupling** | Изменение в одном месте перекомпилирует несвязанный код |
| **LSP нарушение** | `throw NotSupportedException` ломает контракт |

#### Когда НЕ дробить интерфейсы

| Ситуация | Почему |
|----------|--------|
| Все клиенты используют все методы | Нет "жирности" |
| 3-4 cohesive метода | Дробить = лишняя сложность |
| Rapid prototyping | Сначала работает, потом рефакторим |

---

### D — Dependency Inversion Principle

#### Точное определение

**Оригинальная формулировка (Robert C. Martin):**

**Часть 1:** "High-level modules should not depend on low-level modules. Both should depend on abstractions."

**Часть 2:** "Abstractions should not depend on details. Details should depend on abstractions."

**Что значит "инверсия":**

```
Традиционная зависимость:        После инверсии:

Store                            Store
   │                                │
   │ зависит от                     │ зависит от
   ▼                                ▼
StripeAPI                     PaymentGateway (interface)
                                    ▲
                                    │ реализует
                               StripeGateway

Стрелка зависимости ИНВЕРТИРОВАНА — теперь детали зависят от абстракции.
```

#### ГЛАВНОЕ ЗАБЛУЖДЕНИЕ

| Заблуждение | Правда |
|-------------|--------|
| DIP = использовать интерфейсы везде | DIP = интерфейсы там, где нужна **гибкость** |
| DIP = Dependency Injection | DI — это **механизм**, DIP — это **принцип** |
| Все зависимости должны быть абстрактны | Стабильные зависимости (String, List) не абстрагируем |

**Почему это заблуждение опасно:**

> "Implementing generic interfaces everywhere in a project makes it harder to understand and maintain. At each step the reader will ask themself what are the other implementations of this interface and the response is generally: only mocks." — [DIP is a Tradeoff](https://naildrivin5.com/blog/2019/12/02/dependency-inversion-principle-is-a-tradeoff.html)

Интерфейс для каждого класса = непонятный код + overhead без пользы.

#### Когда DIP оправдан vs когда нет

| Оправдан | Не оправдан |
|----------|-------------|
| Реализация может измениться | Единственная реализация навсегда |
| Нужна testability с моками | Можно тестировать без моков |
| Внешние зависимости (API, DB) | Стабильные библиотеки (String, List) |

#### Пример

```typescript
// Плохо: tight coupling к конкретному API
class Store {
  private stripe = new StripeAPI();  // Жёсткая зависимость
  checkout(amount: number) {
    this.stripe.charge(amount);      // Stripe упал = Store не работает
  }
}

// Хорошо: зависимость от абстракции
interface PaymentGateway {
  charge(amount: number): Promise<void>;
}

class Store {
  constructor(private payment: PaymentGateway) {}
  async checkout(amount: number) {
    await this.payment.charge(amount);
  }
}

// Production
const store = new Store(new StripeGateway());

// Stripe упал? Быстрое переключение:
const store = new Store(new PayPalGateway());

// Тестирование без реальных платежей:
const store = new Store(new MockPaymentGateway());
```

**Преимущества:**
- Stripe упал? Быстрое переключение на PayPal
- Тестирование с MockPaymentGateway без реальных платежей
- High-level код (Store) не меняется при смене low-level (Stripe → PayPal)

#### Когда НЕ применять DIP

| Ситуация | Почему |
|----------|--------|
| Маленький скрипт | Overhead абстракций > пользы |
| Единственная реализация навсегда | `Math.random()` — не нужен interface |
| Stable dependencies | `String`, `List` — не абстрагируем |

---

## Over-engineering: когда SOLID вредит

### Проблема 1: Чистый код как догма

```
"Функция должна быть не длиннее 5 строк"
"Никогда не использовать else"
"Каждый класс — отдельный файл"

Реальность:
• 10-строчная функция может быть чище 3 пятистрочных
• else иногда читается лучше early return
• Группировка связанного кода важнее догм

Правило: Читаемость > Правила
```

### Проблема 2: Explosion of classes

```typescript
// Слишком много абстракций для простой задачи

// Плохо: 5 классов для сложения чисел
interface NumberOperation {
  execute(a: number, b: number): number;
}

class AdditionStrategy implements NumberOperation {
  execute(a: number, b: number) { return a + b; }
}

class Calculator {
  constructor(private strategy: NumberOperation) {}
  calculate(a: number, b: number) {
    return this.strategy.execute(a, b);
  }
}

const calc = new Calculator(new AdditionStrategy());
calc.calculate(2, 3);

// Хорошо: просто функция
function add(a: number, b: number): number {
  return a + b;
}
```

> "It is vitally important to start simple and introduce complexity only to solve existing problems." — [SOLID as an antipattern](https://blog.spinthemoose.com/2012/12/17/solid-as-an-antipattern/)

### Проблема 3: Преждевременная абстракция

```
Ситуация: Прототип, deadline через неделю

Плохо: "Сначала идеальная архитектура"
Результат: Не успели, проект закрыли

Хорошо: "Рабочий код сейчас, рефакторинг потом"
Результат: Запустились, улучшили после

Порядок приоритетов:
1. Работает
2. Правильно
3. Быстро
4. Красиво
```

### Когда God Class допустим

В early-stage prototyping "God Class" может быть оправдан:
- Минимум людей в команде
- Требования меняются каждый день
- Важнее проверить идею, чем писать идеальный код

**Ключ:** Признать это как временное решение и рефакторить когда продукт стабилизируется.

---

## Actionable

### Code Review чеклист

```
□ Имена понятны без контекста?
□ Функции делают одно?
□ Нет магических чисел/строк?
□ Ошибки обрабатываются явно?
□ Можно тестировать изолированно?
□ Нет дублирования логики?
```

### Рефакторинг приоритеты

```
1. Сначала: имена (дёшево, высокий impact)
2. Затем: extract method (средний effort)
3. Потом: SOLID (требует планирования)
```

### Эвристика: когда применять SOLID

| Условие | Рекомендация |
|---------|--------------|
| Код меняется часто | Применять SOLID |
| Код написан раз и забыт | Не усложнять |
| Команда > 3 человек | Применять SOLID |
| Solo проект | По ситуации |
| Проект > 6 месяцев | Применять SOLID |
| Хакатон / MVP | Не усложнять |

---

## Куда дальше

**Практическое применение SOLID:**
→ [[design-patterns]] — Factory, Strategy, Observer — паттерны, которые реализуют SOLID на практике.

**Последствия нарушений:**
→ [[technical-debt]] — что происходит когда игнорируешь чистый код.

**В контексте архитектуры:**
→ [[microservices-vs-monolith]] — как SOLID масштабируется на уровень сервисов.

---

## Источники

### Первоисточники (авторы принципов)
- Robert C. Martin, "Design Principles and Design Patterns" (2000) — [оригинальная статья](http://principles-wiki.net/collections:robert_c._martin_s_principle_collection)
- Robert C. Martin, [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) (2014) — уточнение "reason to change = actors"
- Robert C. Martin, [The Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) (2014)
- Bertrand Meyer, "Object-Oriented Software Construction" (1988) — OCP
- Barbara Liskov, "Data abstraction and hierarchy" (1987) — LSP
- Barbara Liskov & Jeannette Wing, "A behavioral notion of subtyping" (1994) — формализация LSP

### Официальная документация
- [Wikipedia: SOLID](https://en.wikipedia.org/wiki/SOLID) — история и контекст
- [Wikipedia: Single-responsibility principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)
- [Wikipedia: Open-closed principle](https://en.wikipedia.org/wiki/Open–closed_principle)
- [Wikipedia: Liskov substitution principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
- [Wikipedia: Interface segregation principle](https://en.wikipedia.org/wiki/Interface_segregation_principle)
- [Wikipedia: Dependency inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

### Реальные кейсы и нарушения
- [Knight Capital Disaster](https://www.henricodolfing.com/2019/06/project-failure-case-study-knight-capital.html) — $440M потеря за 45 минут
- [NLog LSP Violation](https://devonblog.com/software-development/solid-violations-wild-liskov-substitution-principle/) — пример LSP нарушения в production
- [SRP Case Study: Buildbot](https://www.codelord.net/2010/05/09/case-study-single-responsibility-principle-violation/)

### Критика и альтернативные взгляды
- [SOLID as an antipattern](https://blog.spinthemoose.com/2012/12/17/solid-as-an-antipattern/) — когда SOLID вредит
- [The Misunderstood SRP](https://www.softwareonthebrain.com/2022/01/the-misunderstood-single-responsibility.html) — разбор заблуждений
- [DIP is a Tradeoff](https://naildrivin5.com/blog/2019/12/02/dependency-inversion-principle-is-a-tradeoff.html) — критика DIP
- [Should We Follow OCP?](https://thevaluable.dev/open-closed-principle-revisited/) — переосмысление OCP
- [Stack Overflow: Why SOLID still matters](https://stackoverflow.blog/2021/11/01/why-solid-principles-are-still-the-foundation-for-modern-software-architecture/)

### Туториалы
- [DigitalOcean SOLID Guide](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Baeldung SOLID Principles](https://www.baeldung.com/solid-principles)
- [Refactoring Guru](https://refactoring.guru/refactoring/techniques)

---

**Последняя верификация**: 2025-12-19
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*
