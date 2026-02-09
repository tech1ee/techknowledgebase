---
title: "Event-Driven Architecture: реактивные системы"
created: 2025-11-24
modified: 2026-01-03
type: concept
status: verified
confidence: high
sources_verified: true
tags:
  - architecture/eda
  - architecture/messaging
  - tools/kafka
related:
  - "[[microservices-vs-monolith]]"
  - "[[design-patterns]]"
  - "[[observability]]"
  - "[[architecture-resilience-patterns]]"
---

# Event-Driven Architecture: реактивные системы

Представь доску объявлений в офисе. Вместо того чтобы лично искать каждого коллегу и передавать информацию ("Новый заказ пришёл! Платёжный отдел — прими оплату! Склад — подготовь товар!"), ты просто **вешаешь объявление**. Кому надо — тот прочитает и сделает своё дело. Ты не знаешь кто именно следит за доской, и тебе это не важно. **Event-Driven Architecture — это та самая доска объявлений для микросервисов.**

---

## Prerequisites (Что нужно знать заранее)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **REST API** | Понимание синхронного request/response | [[api-design]] |
| **Микросервисы** | EDA обычно используется в микросервисах | [[microservices-vs-monolith]] |
| **JSON** | Формат сообщений в очередях | Базовые знания |
| **Async/await** | Асинхронный код в примерах | TypeScript/JavaScript docs |
| **Базы данных** | Для паттерна Outbox и Event Sourcing | [[databases-overview]] |

---

## TL;DR (если совсем нет времени)

- **EDA** = сервисы общаются через события, а не прямые вызовы
- **Главная аналогия:** Доска объявлений — повесил новость, кому надо — прочитает
- **Ключевые компоненты:** Producer → Message Broker (Kafka/RabbitMQ) → Consumer
- **Паттерны:** Event Notification, Event-Carried State, Event Sourcing, CQRS
- **Брокеры:** Kafka (high throughput, 1M+ msg/sec, replay), RabbitMQ (task queues, проще)
- **Главные проблемы:** Eventual consistency, сложная отладка, дублирование сообщений
- **Решения:** Idempotency keys, Outbox pattern, Correlation IDs
- **Кто использует:** Netflix (1B+ events/day), Uber (миллионы rides), Shopify (66M msg/sec peak)

---

## Кто использует EDA в production

| Компания | Масштаб | Технологии |
|----------|---------|------------|
| **Netflix** | 1+ млрд событий/день, 260M подписчиков | Kafka, Event Sourcing, CQRS |
| **Uber** | Миллионы rides/день, real-time matching | Kafka, Flink, exactly-once |
| **Shopify** | 66M сообщений/сек (пик) | Kafka как backbone |
| **LinkedIn** | Все real-time features | Kafka (создатели Kafka!) |
| **ING Bank** | Real-time транзакции | Kafka, event sourcing |

*"Event-driven architecture is the backbone of scaling systems in 2025"* — Growin Engineering

---

## Терминология (с аналогиями)

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Event** | Факт о том, что что-то произошло | Объявление: "Заказ создан!" |
| **Producer** | Сервис, который создаёт события | Тот, кто вешает объявление на доску |
| **Consumer** | Сервис, который обрабатывает события | Тот, кто читает объявления и реагирует |
| **Message Broker** | Посредник (Kafka, RabbitMQ) | Сама доска объявлений |
| **Topic/Queue** | Категория сообщений | Раздел доски: "Заказы", "Платежи" |
| **Event Sourcing** | События = источник истины, состояние = replay | Бухгалтерская книга: записи vs баланс |
| **CQRS** | Разделение записи и чтения | Касса (запись) vs витрина (чтение) |
| **Idempotency** | Повторная обработка = тот же результат | Дважды нажал лифт — приедет один раз |
| **Dead Letter Queue** | Очередь для необработанных событий | Ящик для "неразобранных писем" |
| **Eventual Consistency** | Данные согласуются со временем | Банковский перевод: ушло сегодня — придёт завтра |
| **Correlation ID** | ID связывающий все события одного flow | Номер заказа на всех документах |
| **Partition** | Часть топика для параллелизма (Kafka) | Несколько касс в супермаркете |
| **Consumer Group** | Группа consumers, делящих нагрузку | Смена кассиров: один отдыхает — другой работает |

---

## Зачем Event-Driven?

```
Синхронная архитектура (Request/Response):

Order Service ──HTTP──▶ Payment Service
                              │
                              ├──HTTP──▶ Inventory Service
                              │
                              └──HTTP──▶ Notification Service

Проблемы:
• Payment упал = Order не работает
• Добавить Analytics = изменить Order Service
• Latency = сумма всех вызовов
• Tight coupling — всё связано

─────────────────────────────────────────────────────────

Event-Driven архитектура:

Order Service ──event──▶ Message Broker ──▶ Payment Service
                              │
                              ├────────────▶ Inventory Service
                              │
                              ├────────────▶ Notification Service
                              │
                              └────────────▶ Analytics Service

Преимущества:
• Payment упал → события в очереди, обработаются позже
• Добавить Analytics = подписаться на события
• Latency = только публикация события
• Loose coupling — сервисы независимы
```

---

## Паттерны событий

### 1. Event Notification

```
Событие = "что-то произошло", без деталей

┌─────────────┐  { type: "OrderCreated",   ┌──────────────┐
│   Order     │    orderId: "123" }        │   Message    │
│   Service   │───────────────────────────▶│   Broker     │
└─────────────┘                            └──────┬───────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────┐
                    │                             │                     │
                    ▼                             ▼                     ▼
            ┌──────────────┐            ┌──────────────┐      ┌──────────────┐
            │   Payment    │            │  Inventory   │      │  Analytics   │
            │   Service    │            │   Service    │      │   Service    │
            └──────────────┘            └──────────────┘      └──────────────┘
                    │                             │
                    │ GET /orders/123             │ GET /orders/123
                    └────────────────────────────▶│ (каждый запрашивает данные)
                                                  ▼

Плюсы:
+ Простые события
+ Producer не знает о consumers

Минусы:
- Consumers делают callback для данных
- Больше сетевых запросов
```

### 2. Event-Carried State Transfer

```
Событие содержит все нужные данные

{
  type: "OrderCreated",
  orderId: "123",
  payload: {
    userId: "user_456",
    items: [
      { productId: "prod_1", quantity: 2, price: 29.99 },
      { productId: "prod_2", quantity: 1, price: 49.99 }
    ],
    totalAmount: 109.97,
    shippingAddress: { ... },
    createdAt: "2025-11-24T10:30:00Z"
  }
}

Плюсы:
+ Consumers не зависят от producer (нет callbacks)
+ Данные доступны сразу
+ Можно реплицировать данные локально

Минусы:
- Большие события
- Дублирование данных
- Версионирование схемы события
```

### 3. Event Sourcing

```
События — единственный источник истины
Состояние = replay всех событий

┌─────────────────────────────────────────────────────────────────┐
│                     EVENT STORE                                 │
├─────────────────────────────────────────────────────────────────┤
│  1. AccountCreated    { id: "acc_1", owner: "John" }            │
│  2. MoneyDeposited    { accountId: "acc_1", amount: 100 }       │
│  3. MoneyWithdrawn    { accountId: "acc_1", amount: 30 }        │
│  4. MoneyDeposited    { accountId: "acc_1", amount: 50 }        │
│  5. MoneyWithdrawn    { accountId: "acc_1", amount: 25 }        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Replay
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Current State:                                                 │
│  Account { id: "acc_1", owner: "John", balance: 95 }            │
│                                                                 │
│  Расчёт: 0 + 100 - 30 + 50 - 25 = 95                            │
└─────────────────────────────────────────────────────────────────┘

Плюсы:
+ Полная история изменений (аудит)
+ Можно восстановить состояние на любой момент
+ Можно добавить новые проекции задним числом

Минусы:
- Сложная реализация
- Производительность при большом количестве событий
- Eventual consistency между проекциями
```

```typescript
// Event Sourcing пример
interface Event {
  type: string;
  aggregateId: string;
  timestamp: Date;
  payload: unknown;
}

interface AccountState {
  id: string;
  owner: string;
  balance: number;
}

// Reducer — как в Redux
function accountReducer(state: AccountState | null, event: Event): AccountState {
  switch (event.type) {
    case 'AccountCreated':
      return {
        id: event.aggregateId,
        owner: event.payload.owner,
        balance: 0
      };

    case 'MoneyDeposited':
      return {
        ...state!,
        balance: state!.balance + event.payload.amount
      };

    case 'MoneyWithdrawn':
      return {
        ...state!,
        balance: state!.balance - event.payload.amount
      };

    default:
      return state!;
  }
}

// Восстановление состояния
async function getAccountState(accountId: string): Promise<AccountState> {
  const events = await eventStore.getEvents(accountId);
  return events.reduce(accountReducer, null);
}

// Команда с валидацией
async function withdraw(accountId: string, amount: number): Promise<void> {
  const state = await getAccountState(accountId);

  // Бизнес-логика
  if (state.balance < amount) {
    throw new InsufficientFundsError();
  }

  // Сохраняем событие, не состояние
  await eventStore.append({
    type: 'MoneyWithdrawn',
    aggregateId: accountId,
    timestamp: new Date(),
    payload: { amount }
  });
}
```

---

## Message Brokers

### Сравнение

```
┌─────────────────────────────────────────────────────────────────┐
│                    MESSAGE BROKERS                              │
├──────────────┬─────────────────┬────────────────────────────────┤
│              │ RabbitMQ        │ Apache Kafka                   │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Модель       │ Message Queue   │ Distributed Log                │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Доставка     │ Push (broker →  │ Pull (consumer ← broker)       │
│              │ consumer)       │                                │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Хранение     │ До acknowledge  │ По времени/размеру             │
│              │                 │ (дни/недели)                   │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Replay       │ Нет             │ Да (перечитать с offset)       │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Throughput   │ ~50K msg/sec    │ ~1M+ msg/sec                   │
├──────────────┼─────────────────┼────────────────────────────────┤
│ Когда        │ Task queues,    │ Event streaming, logs,         │
│              │ RPC, небольшие  │ высокая нагрузка, replay       │
│              │ нагрузки        │                                │
└──────────────┴─────────────────┴────────────────────────────────┘
```

### Kafka basics

```
Kafka архитектура:

┌─────────────────────────────────────────────────────────────────┐
│                         KAFKA CLUSTER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Topic: orders                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Partition 0: [msg1][msg2][msg3][msg4]...                │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Partition 1: [msg1][msg2][msg3]...                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Partition 2: [msg1][msg2][msg3][msg4][msg5]...          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  • Partition = ordered, append-only log                         │
│  • Сообщения с одним key идут в одну partition                  │
│  • Consumer Group читает каждую partition одним consumer        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Consumer Groups:

  Partition 0 ──▶ Consumer A (Group 1)
  Partition 1 ──▶ Consumer B (Group 1)
  Partition 2 ──▶ Consumer C (Group 1)

  Partition 0 ──▶ Consumer X (Group 2)  ← Другая группа
  Partition 1 ──▶ Consumer X (Group 2)     получает те же
  Partition 2 ──▶ Consumer X (Group 2)     сообщения
```

```typescript
// Kafka Producer (Node.js + kafkajs)
import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'order-service',
  brokers: ['kafka1:9092', 'kafka2:9092']
});

const producer = kafka.producer();

async function publishOrderCreated(order: Order) {
  await producer.connect();

  await producer.send({
    topic: 'orders',
    messages: [
      {
        key: order.id,  // Гарантирует порядок для одного заказа
        value: JSON.stringify({
          type: 'OrderCreated',
          timestamp: new Date().toISOString(),
          payload: order
        }),
        headers: {
          'correlation-id': order.correlationId
        }
      }
    ]
  });
}

// Consumer
const consumer = kafka.consumer({ groupId: 'payment-service' });

async function startConsumer() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'orders', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const event = JSON.parse(message.value.toString());

      console.log({
        topic,
        partition,
        offset: message.offset,
        type: event.type
      });

      switch (event.type) {
        case 'OrderCreated':
          await processPayment(event.payload);
          break;
        case 'OrderCancelled':
          await refundPayment(event.payload);
          break;
      }
    }
  });
}
```

### RabbitMQ basics

```typescript
// RabbitMQ с amqplib
import amqp from 'amqplib';

// Publisher
async function publishEvent(exchange: string, routingKey: string, event: object) {
  const connection = await amqp.connect('amqp://localhost');
  const channel = await connection.createChannel();

  await channel.assertExchange(exchange, 'topic', { durable: true });

  channel.publish(
    exchange,
    routingKey,
    Buffer.from(JSON.stringify(event)),
    {
      persistent: true,
      contentType: 'application/json',
      messageId: crypto.randomUUID()
    }
  );
}

// Использование
await publishEvent('orders', 'order.created', {
  orderId: '123',
  userId: 'user_456',
  items: [...]
});

// Consumer
async function startConsumer() {
  const connection = await amqp.connect('amqp://localhost');
  const channel = await connection.createChannel();

  const queue = 'payment-service-orders';
  await channel.assertQueue(queue, { durable: true });
  await channel.bindQueue(queue, 'orders', 'order.*');

  // Prefetch — сколько сообщений обрабатывать параллельно
  channel.prefetch(10);

  channel.consume(queue, async (msg) => {
    if (!msg) return;

    try {
      const event = JSON.parse(msg.content.toString());
      await processEvent(event);

      // Подтверждаем успешную обработку
      channel.ack(msg);
    } catch (error) {
      // Negative ack — вернуть в очередь или в dead letter
      channel.nack(msg, false, false);
    }
  });
}
```

---

## Паттерны надёжности

### Идемпотентность

```
Проблема:
Сообщение может прийти дважды (network retry, consumer restart)

Пример:
1. Consumer получил "OrderCreated"
2. Обработал, списал деньги
3. Упал ДО acknowledge
4. Kafka переотправляет
5. Consumer снова списывает деньги
6. Клиент платит дважды 💸

Решение: Idempotency Key
```

```typescript
// Идемпотентная обработка
class IdempotentEventProcessor {
  constructor(
    private processedEvents: Set<string>,  // В реальности — Redis/DB
    private handler: (event: Event) => Promise<void>
  ) {}

  async process(event: Event): Promise<void> {
    const eventId = event.id || `${event.type}:${event.aggregateId}:${event.timestamp}`;

    // Проверяем, не обработано ли уже
    if (await this.isProcessed(eventId)) {
      console.log(`Event ${eventId} already processed, skipping`);
      return;
    }

    // Обрабатываем
    await this.handler(event);

    // Отмечаем как обработанное
    await this.markProcessed(eventId);
  }

  private async isProcessed(eventId: string): Promise<boolean> {
    return this.processedEvents.has(eventId);
  }

  private async markProcessed(eventId: string): Promise<void> {
    this.processedEvents.add(eventId);
  }
}

// В реальном коде — с Redis
async function processEventIdempotently(event: Event) {
  const eventId = event.id;
  const lockKey = `event:processed:${eventId}`;

  // Атомарная проверка и установка
  const wasSet = await redis.set(lockKey, '1', 'NX', 'EX', 86400);

  if (!wasSet) {
    // Уже обработано
    return;
  }

  await actualEventHandler(event);
}
```

### Outbox Pattern

```
Проблема:
Нужно атомарно: сохранить в БД И отправить событие

Плохо:
1. Сохранили в БД
2. Отправляем событие — сеть упала
3. Данные в БД есть, события нет

Решение: Outbox Table
```

```typescript
// Outbox Pattern
async function createOrder(orderData: OrderInput): Promise<Order> {
  return await db.transaction(async (trx) => {
    // 1. Создаём заказ
    const order = await trx('orders').insert(orderData).returning('*');

    // 2. Записываем событие в outbox (в той же транзакции!)
    await trx('outbox').insert({
      id: crypto.randomUUID(),
      aggregate_type: 'Order',
      aggregate_id: order.id,
      event_type: 'OrderCreated',
      payload: JSON.stringify(order),
      created_at: new Date()
    });

    return order;
  });
  // Транзакция коммитится — и данные и событие записаны
}

// Отдельный процесс читает outbox и публикует
async function outboxProcessor() {
  while (true) {
    const events = await db('outbox')
      .where('published_at', null)
      .orderBy('created_at')
      .limit(100);

    for (const event of events) {
      try {
        await publishToKafka(event.event_type, event.payload);

        await db('outbox')
          .where('id', event.id)
          .update({ published_at: new Date() });
      } catch (error) {
        // Retry на следующей итерации
        console.error('Failed to publish', event.id, error);
      }
    }

    await sleep(1000);
  }
}
```

### Saga Pattern

```
Проблема:
Распределённая транзакция через несколько сервисов

Пример: Заказ
1. Reserve inventory
2. Process payment
3. Ship order

Если payment fails — нужно откатить inventory

Saga = последовательность локальных транзакций + компенсации
```

```typescript
// Saga Orchestrator
class OrderSaga {
  private steps: SagaStep[] = [
    {
      name: 'reserveInventory',
      execute: (ctx) => inventoryService.reserve(ctx.order.items),
      compensate: (ctx) => inventoryService.release(ctx.order.items)
    },
    {
      name: 'processPayment',
      execute: (ctx) => paymentService.charge(ctx.order.userId, ctx.order.total),
      compensate: (ctx) => paymentService.refund(ctx.paymentId)
    },
    {
      name: 'createShipment',
      execute: (ctx) => shippingService.create(ctx.order),
      compensate: (ctx) => shippingService.cancel(ctx.shipmentId)
    }
  ];

  async execute(order: Order): Promise<SagaResult> {
    const context: SagaContext = { order };
    const completedSteps: SagaStep[] = [];

    try {
      for (const step of this.steps) {
        console.log(`Executing step: ${step.name}`);
        const result = await step.execute(context);

        // Сохраняем результат для компенсации
        context[`${step.name}Result`] = result;
        completedSteps.push(step);
      }

      return { success: true, context };
    } catch (error) {
      console.error('Saga failed, compensating...', error);

      // Откатываем в обратном порядке
      for (const step of completedSteps.reverse()) {
        try {
          await step.compensate(context);
        } catch (compensateError) {
          // Логируем и продолжаем — manual intervention needed
          console.error(`Compensation failed for ${step.name}`, compensateError);
        }
      }

      return { success: false, error };
    }
  }
}
```

---

## Подводные камни

### Проблема 1: Eventual Consistency

```
Синхронная система:
  Write → Read → Гарантированно новые данные

Event-Driven:
  Write → Event → ... → Consumer → Write
  Read (в это время) → Возможно старые данные!

Пользователь:
1. Создал заказ
2. Перешёл на страницу заказов
3. Заказа нет! (ещё не обработан)
4. "Баг!!!"

Решения:
• UI показывает pending state
• Optimistic UI (показать сразу, обновить при подтверждении)
• Read-your-writes consistency (читать из того же источника)
```

### Проблема 2: Debugging & Tracing

```
Синхронный код:
  Request → Service A → Service B → Response
  Stack trace показывает весь путь

Event-Driven:
  Request → Event → ??? → где проблема?

Решение: Distributed Tracing
• Correlation ID в каждом событии
• OpenTelemetry для трейсинга
• Централизованные логи
```

```typescript
// Correlation ID
interface Event {
  id: string;
  type: string;
  correlationId: string;  // Связывает все события одного flow
  causationId: string;    // ID события, которое вызвало это
  timestamp: string;
  payload: unknown;
}

// При создании первого события
const orderCreatedEvent = {
  id: 'evt_1',
  type: 'OrderCreated',
  correlationId: 'corr_abc123',  // Уникальный ID для всего flow
  causationId: 'cmd_createOrder',
  timestamp: new Date().toISOString(),
  payload: order
};

// При создании дочернего события
const paymentProcessedEvent = {
  id: 'evt_2',
  type: 'PaymentProcessed',
  correlationId: 'corr_abc123',  // Тот же correlation ID
  causationId: 'evt_1',          // Вызвано OrderCreated
  timestamp: new Date().toISOString(),
  payload: payment
};
```

### Проблема 3: Schema Evolution

```
v1: { orderId: string, total: number }
v2: { orderId: string, totalAmount: number, currency: string }

Старые события в Kafka — с v1 схемой
Новый consumer ожидает v2

Решения:
• Schema Registry (Confluent)
• Версионирование событий
• Backward/Forward compatibility
```

---

## Actionable

**Начни с простого:**
```typescript
// In-process Event Bus (для начала)
class EventBus {
  private handlers: Map<string, Set<Function>> = new Map();

  on(event: string, handler: Function) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
  }

  emit(event: string, data: any) {
    this.handlers.get(event)?.forEach(h => h(data));
  }
}

// Использование
const events = new EventBus();

events.on('order:created', (order) => {
  emailService.sendConfirmation(order);
});

events.on('order:created', (order) => {
  analyticsService.track('purchase', order);
});

// В сервисе
await db.orders.create(order);
events.emit('order:created', order);
```

**Чеклист для перехода к EDA:**
```
□ Определить domain events (что происходит в системе)
□ Выбрать message broker (RabbitMQ для начала)
□ Реализовать idempotent consumers
□ Добавить correlation IDs
□ Настроить мониторинг очередей
□ Продумать dead letter queue
```

---

## Связи

- EDA в микросервисах: [[microservices-vs-monolith]]
- Observer паттерн: [[design-patterns]]
- Трейсинг событий: [[observability]]

---

## Источники

### Концепции и паттерны
- [Martin Fowler: Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html) — каноническое описание
- [Confluent: Event Sourcing](https://www.confluent.io/learn/event-sourcing/) — Event Sourcing подробно
- [Microsoft: Event-driven architecture style](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven) — Azure perspective

### Кейсы компаний (2024-2025)
- [Medium: How Netflix and Uber Handle Billions of Events](https://developerport.medium.com/the-power-of-event-driven-architecture-how-netflix-and-uber-handle-billions-of-events-daily-0a2d09d7308c) — Netflix и Uber в деталях
- [Estuary: 10 Event-Driven Architecture Examples](https://estuary.dev/blog/event-driven-architecture-examples/) — Amazon, Shopify, ING
- [Growin: EDA Done Right 2025](https://www.growin.com/blog/event-driven-architecture-scale-systems-2025/) — best practices 2025

### Технические статьи
- [DZone: EDA Real-World Lessons](https://dzone.com/articles/event-driven-architecture-real-world-iot) — уроки из production
- [Gravitee: Best Architectural Patterns](https://www.gravitee.io/blog/event-driven-architecture-patterns) — паттерны
- [AxonIQ: Event-Driven Microservices](https://www.axoniq.io/concepts/event-driven-microservices) — концепции

### Документация инструментов
- [KafkaJS Documentation](https://kafka.js.org/) — Kafka для Node.js
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) — официальная документация
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html) — туториалы RabbitMQ

---

**Последняя верификация**: 2026-01-03
**Уровень достоверности**: high
**Количество источников**: 15+

---

*Проверено: 2026-01-09*
