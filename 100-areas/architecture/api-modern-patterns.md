---
title: "API Modern Patterns: tRPC, Webhooks, API Gateway, BFF"
created: 2026-02-10
modified: 2026-02-10
type: deep-dive
status: published
confidence: high
sources_verified: true
tags:
  - topic/architecture
  - architecture/api
  - architecture/patterns
  - backend/trpc
  - backend/webhooks
  - type/deep-dive
  - level/intermediate
related:
  - "[[api-design]]"
  - "[[api-rest-deep-dive]]"
  - "[[api-graphql-deep-dive]]"
  - "[[api-grpc-deep-dive]]"
  - "[[event-driven-architecture]]"
  - "[[microservices-vs-monolith]]"
  - "[[network-realtime-protocols]]"
cs-foundations:
  - type-safety
  - event-driven
  - gateway-pattern
  - client-server
  - message-signing
  - idempotency
---

# API Modern Patterns: tRPC, Webhooks, API Gateway, BFF

REST, GraphQL, gRPC — три столпа API-мира. Но в 2024 году TypeScript-проект с 35K GitHub-звёзд тихо изменил подход fullstack-команд к API. Нет schema-файла, нет кодогенерации, нет runtime-overhead. Ты меняешь сигнатуру функции на сервере — и TypeScript мгновенно подсвечивает ошибку на клиенте. Это tRPC. Рядом с ним — Webhooks (78% SaaS-платформ используют их для интеграций), API Gateway (единая точка входа для микросервисов) и BFF (отдельный backend для каждого типа клиента). Разберём каждый паттерн.

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **REST API** | Базовое понимание request/response | [[api-rest-deep-dive]] |
| **TypeScript** | tRPC целиком построен на TypeScript | Основы TS |
| **HTTP** | Webhooks работают через HTTP callbacks | [[network-http-evolution]] |
| **Микросервисы** | API Gateway и BFF — паттерны для микросервисов | [[microservices-vs-monolith]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **tRPC** | TypeScript Remote Procedure Call — type-safe API без codegen | Телепатия между frontend и backend: меняешь на одном конце — второй мгновенно «видит» |
| **Webhook** | HTTP callback: сервер отправляет POST на указанный URL при событии | Уведомление на телефон: подписался — получаешь, когда что-то происходит |
| **API Gateway** | Единая точка входа для всех клиентов, маршрутизация к микросервисам | Ресепшен в бизнес-центре: все идут через одну дверь |
| **BFF** | Backend for Frontend — отдельный backend для каждого типа клиента | Персональный переводчик: каждому клиенту — свой формат |
| **HMAC** | Hash-based Message Authentication Code — подпись сообщения | Печать на конверте: доказывает, что отправитель — настоящий |
| **SOAP** | Simple Object Access Protocol — XML-based RPC (legacy) | Бюрократический протокол: конверт → заголовок → тело → подпись |
| **JSON:API** | Спецификация для JSON-based REST API | ГОСТ для JSON: стандартные поля, связи, пагинация |

---

## tRPC: type-safe API без codegen

### Проблема, которую решает tRPC

TypeScript-разработчик создаёт fullstack-приложение. Backend возвращает JSON. Frontend ожидает определённую структуру. Между ними — пропасть:

```
REST + TypeScript:
──────────────────
// Backend (Express)
app.get('/users/:id', (req, res) => {
  res.json({ id: 1, name: "Иван", email: "ivan@mail.com" });
});

// Frontend
const response = await fetch('/users/1');
const user = await response.json();
// user: any  ← TypeScript не знает структуру!
// Опечатался в user.nmae? Узнаешь только в runtime.

Решения «до tRPC»:
1. OpenAPI + codegen → Генерируй типы из Swagger. Но: отдельный шаг сборки,
   типы могут устареть, boilerplate.
2. GraphQL + codegen → graphql-codegen. Но: сложнее, отдельный SDL,
   build step, schema ≠ TypeScript types.
3. Общие types в монорепо → Ручная синхронизация. Ломается при изменениях.
```

### Как tRPC решает это

tRPC использует **TypeScript inference** — типы передаются от сервера к клиенту через import, без кодогенерации, без runtime-overhead, без build step.

```typescript
// ========================
// server.ts (tRPC Router)
// ========================
import { initTRPC } from '@trpc/server';
import { z } from 'zod';  // Валидация + type inference

const t = initTRPC.create();

// Определяем router с процедурами
export const appRouter = t.router({
  // Query: чтение данных (как GET)
  getUser: t.procedure
    .input(z.object({
      id: z.number().positive()   // Валидация + тип: { id: number }
    }))
    .query(async ({ input }) => {
      const user = await db.user.findUnique({ where: { id: input.id } });
      return user;  // TypeScript знает тип возврата!
    }),

  // Mutation: изменение данных (как POST/PUT)
  createUser: t.procedure
    .input(z.object({
      name: z.string().min(1),
      email: z.string().email()
    }))
    .mutation(async ({ input }) => {
      return db.user.create({ data: input });
    }),

  // Subscription: real-time
  onNewMessage: t.procedure
    .subscription(() => {
      return observable<Message>((emit) => {
        const handler = (msg: Message) => emit.next(msg);
        eventEmitter.on('message', handler);
        return () => eventEmitter.off('message', handler);
      });
    }),
});

// ЭТА СТРОКА — КЛЮЧ К МАГИИ:
export type AppRouter = typeof appRouter;
// Экспортируем ТИП router'а, не runtime-код!


// ========================
// client.ts (Frontend)
// ========================
import type { AppRouter } from '../server';  // Только тип! 0 bytes в bundle
import { createTRPCClient, httpBatchLink } from '@trpc/client';

const trpc = createTRPCClient<AppRouter>({
  links: [httpBatchLink({ url: '/api/trpc' })],
});

// ВСЁ ТИПИЗИРОВАНО:
const user = await trpc.getUser.query({ id: 123 });
// user: { id: number, name: string, email: string } | null
// IDE показывает автокомплит для user.name, user.email

// Ошибка на этапе компиляции:
const user2 = await trpc.getUser.query({ id: "abc" });
//                                        ~~~ Error: expected number
```

### Когда использовать tRPC

```
┌──────────────────────────────────────────────────────────────┐
│                  tRPC DECISION TREE                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  TypeScript на backend И frontend?                            │
│  ├── Нет → REST или GraphQL (tRPC не подходит)               │
│  └── Да ↓                                                     │
│                                                               │
│  Монорепо или shared types возможны?                          │
│  ├── Нет → REST + OpenAPI codegen                            │
│  └── Да ↓                                                     │
│                                                               │
│  Одна команда (fullstack)?                                    │
│  ├── Нет → GraphQL (контракт между командами)                │
│  └── Да ↓                                                     │
│                                                               │
│  Public API для третьих лиц?                                  │
│  ├── Да → REST + OpenAPI (стандарт для интеграций)           │
│  └── Нет ↓                                                    │
│                                                               │
│  → tRPC — идеальный выбор!                                    │
│    Admin panels, внутренние tools, SaaS fullstack             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

| Сценарий | tRPC? | Альтернатива |
|----------|:---:|-------------|
| TypeScript монорепо, одна команда | **Да** | — |
| Internal tools, admin panels | **Да** | — |
| Public API для третьих лиц | Нет | REST + OpenAPI |
| Multi-language backend | Нет | REST или gRPC |
| Мобильные клиенты (не TS) | Нет | REST или GraphQL |
| Микросервисы на разных языках | Нет | gRPC |
| Сложный граф данных | Нет | GraphQL |

---

## Webhooks: event notification pattern

### Проблема: push vs pull

Как узнать, что на сервере произошло событие? Два подхода:

```
POLLING (pull):
───────────────
Клиент каждые 5 секунд: "Есть новый платёж?"
Сервер: "Нет."
Клиент: "Есть новый платёж?"
Сервер: "Нет."
Клиент: "Есть новый платёж?"
Сервер: "Да! Вот он."

Проблема: 95% запросов впустую. Нагрузка на сервер.
Задержка: до 5 секунд.

WEBHOOK (push):
───────────────
Клиент: "Вот мой URL. Когда будет платёж — POST мне."
...тишина...
Сервер: POST https://myapp.com/webhooks/stripe
         {"event": "payment.succeeded", "amount": 1500}

Нет пустых запросов. Мгновенная доставка.
```

### Как Webhooks работают

```
┌──────────────────────────────────────────────────────────────┐
│                  WEBHOOK LIFECYCLE                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. РЕГИСТРАЦИЯ                                               │
│     Ваше приложение → Provider (Stripe, GitHub, Slack):       │
│     "Подпишись на event: payment.succeeded"                   │
│     "URL: https://myapp.com/webhooks/stripe"                  │
│     Provider сохраняет URL + генерирует signing secret.       │
│                                                               │
│  2. СОБЫТИЕ ПРОИСХОДИТ                                        │
│     Stripe обрабатывает платёж → payment.succeeded            │
│                                                               │
│  3. ДОСТАВКА                                                  │
│     Stripe → POST https://myapp.com/webhooks/stripe           │
│     Headers:                                                  │
│       Stripe-Signature: t=1707566400,v1=abc123...             │
│       Content-Type: application/json                          │
│     Body: {"type": "payment.succeeded", "data": {...}}        │
│                                                               │
│  4. ОБРАБОТКА                                                 │
│     a) Верифицировать подпись (HMAC-SHA256)                   │
│     b) Проверить timestamp (< 5 минут)                        │
│     c) Ответить 200 OK БЫСТРО (< 5 секунд)                   │
│     d) Поставить в очередь для async-обработки                │
│                                                               │
│  5. RETRY (если 200 не получен)                               │
│     Stripe: 8 попыток за 3 дня                               │
│     GitHub: до 3 попыток                                      │
│     Exponential backoff: 1m, 5m, 30m, 2h...                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### HMAC-подпись: защита от подделки

```
ПОЧЕМУ НУЖНА ПОДПИСЬ:
─────────────────────
Любой может послать POST на ваш webhook-URL.
Без проверки — принимаете фейковые платежи, фейковые заказы.

КАК РАБОТАЕТ HMAC-SHA256:
─────────────────────────
1. Provider и ваше приложение знают общий секрет (signing secret)
2. Provider подписывает payload:
   HMAC-SHA256(secret, timestamp + "." + payload) → signature
3. Отправляет signature в заголовке
4. Ваше приложение повторяет вычисление и сравнивает
```

```javascript
// Верификация webhook-подписи (Stripe)
const crypto = require('crypto');

function verifyStripeWebhook(payload, signature, secret) {
  // Stripe формат: t=timestamp,v1=signature
  const parts = signature.split(',');
  const timestamp = parts.find(p => p.startsWith('t=')).slice(2);
  const sig = parts.find(p => p.startsWith('v1=')).slice(3);

  // 1. Проверяем timestamp (защита от replay-атак)
  const age = Math.floor(Date.now() / 1000) - parseInt(timestamp);
  if (age > 300) {  // > 5 минут
    throw new Error('Webhook too old — possible replay attack');
  }

  // 2. Вычисляем ожидаемую подпись
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(`${timestamp}.${payload}`)
    .digest('hex');

  // 3. Timing-safe сравнение (защита от timing-атак)
  const expected = Buffer.from(expectedSig, 'hex');
  const received = Buffer.from(sig, 'hex');
  if (!crypto.timingSafeEqual(expected, received)) {
    throw new Error('Invalid signature');
  }

  return JSON.parse(payload);
}
```

### Best practices для Webhooks

```
1. ОТВЕЧАЙ БЫСТРО (< 5 секунд)
   ❌ Обработка в request handler (может таймаутить)
   ✅ Ответить 200, поставить в очередь (Redis/SQS/RabbitMQ)

2. ИДЕМПОТЕНТНОСТЬ
   ❌ Дублировать обработку при retry
   ✅ Хранить event_id → проверять перед обработкой

3. THIN vs FAT EVENTS
   Thin: {"event": "order.created", "order_id": "123"}
         Клиент запрашивает данные по order_id.
         + Безопасно (минимум данных), - extra API call.

   Fat:  {"event": "order.created", "order": {полные данные}}
         Все данные в payload.
         + Нет extra call, - больше данных, проблемы с размером.

   Stripe, GitHub → fat events. Twilio → thin events.

4. МОНИТОРИНГ
   Отслеживай: успешность доставки, latency, retry count.
   Алерты: error rate > 5%, queue depth > 5000.

5. ORDERING
   ⚠️ Webhooks НЕ гарантируют порядок!
   order.updated может прийти раньше order.created.
   Решение: timestamp в event, обработка по порядку.
```

---

## API Gateway: единая точка входа

### Проблема: клиент vs микросервисы

Без API Gateway клиент общается с каждым сервисом напрямую:

```
❌ БЕЗ GATEWAY:
───────────────
Mobile App ──→ User Service   (auth, profile)
           ──→ Order Service  (заказы)
           ──→ Payment Service (платежи)
           ──→ Notification Service (уведомления)

Проблемы:
• Клиент знает адреса всех сервисов
• Auth проверяется в каждом сервисе отдельно
• Rate limiting — в каждом сервисе
• CORS — в каждом сервисе
• Клиент делает 4 запроса вместо 1


✅ С GATEWAY:
─────────────
Mobile App ──→ API Gateway ──→ User Service
                            ──→ Order Service
                            ──→ Payment Service
                            ──→ Notification Service

Gateway берёт на себя:
• Маршрутизация (routing)
• Аутентификация/Авторизация
• Rate Limiting
• Request/Response transformation
• Кэширование
• Логирование и мониторинг
• SSL termination
• CORS
```

### API Gateway vs Service Mesh

```
┌──────────────────────────────────────────────────────────────┐
│         API GATEWAY vs SERVICE MESH                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  API GATEWAY                      SERVICE MESH                │
│  ───────────                      ────────────                │
│  North-South трафик               East-West трафик            │
│  (клиент → сервисы)               (сервис → сервис)           │
│                                                               │
│  ┌────────┐                       ┌────────┐   ┌────────┐    │
│  │ Client │                       │Svc A   │──→│Svc B   │    │
│  └───┬────┘                       │+sidecar│   │+sidecar│    │
│      │                            └────────┘   └────────┘    │
│  ┌───▼────────┐                                               │
│  │ API Gateway│                   Control Plane (Istio)       │
│  └─────┬──────┘                   управляет sidecar-прокси    │
│   ┌────┴────┐                                                 │
│   │Services │                                                 │
│   └─────────┘                                                 │
│                                                               │
│  Инструменты:                     Инструменты:                │
│  Kong, AWS API GW, Nginx          Istio, Linkerd, Consul      │
│  Apigee (Google), Envoy           Connect                     │
│                                                               │
│  Используют ВМЕСТЕ:                                           │
│  Gateway для внешних клиентов + Mesh для внутренней связи.    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Популярные решения

| Решение | Тип | Подходит для |
|---------|-----|-------------|
| **Kong** | Open source, Lua/Nginx | Self-hosted, enterprise |
| **AWS API Gateway** | Managed | AWS ecosystem, serverless |
| **Apigee** (Google) | Managed | Enterprise, analytics |
| **Nginx** | Open source | Custom, high performance |
| **Envoy** | Open source (CNCF) | Service mesh, gRPC |
| **Traefik** | Open source | Kubernetes-native, auto-discovery |

---

## BFF: Backend for Frontend

### Проблема: один API — разные клиенты

```
Мобильному приложению нужно:
• Компактный ответ (экономия трафика)
• Только основные поля (маленький экран)
• Агрегированные данные (один запрос — один экран)

Web-приложению нужно:
• Полные данные (большой экран)
• Lazy loading (подгружать по мере скролла)
• Богатые фильтры и сортировка

IoT-устройству нужно:
• Минимальный payload
• Бинарный формат
• Редкие обновления

Один REST API не может эффективно обслуживать всех!
```

### Паттерн BFF

```
┌──────────────────────────────────────────────────────────────┐
│                    BFF PATTERN                                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Mobile   │  │   Web    │  │   IoT    │                   │
│  │  Client  │  │  Client  │  │  Device  │                   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                   │
│       │              │              │                          │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐                   │
│  │ Mobile   │  │  Web     │  │  IoT     │                   │
│  │  BFF     │  │  BFF     │  │  BFF     │                   │
│  │          │  │          │  │          │                   │
│  │ Compact  │  │ Rich     │  │ Binary   │                   │
│  │ responses│  │ responses│  │ Protobuf │                   │
│  │ Aggregate│  │ Paginate │  │ Minimal  │                   │
│  └──┬───┬───┘  └──┬───┬───┘  └──┬───┬───┘                   │
│     │   │         │   │         │   │                         │
│     ▼   ▼         ▼   ▼         ▼   ▼                         │
│  ┌──────────────────────────────────────┐                     │
│  │       Shared Microservices           │                     │
│  │  ┌──────┐ ┌──────┐ ┌──────────┐     │                     │
│  │  │Users │ │Orders│ │Inventory │     │                     │
│  │  └──────┘ └──────┘ └──────────┘     │                     │
│  └──────────────────────────────────────┘                     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Когда использовать BFF:**
- Множество типов клиентов с разными потребностями
- Общий API становится «компромиссом для всех, идеальным ни для кого»
- Разные команды отвечают за разные клиенты

**Anti-patterns:**
- BFF как general-purpose прокси (просто пробрасывает запросы)
- Один BFF для всех клиентов (теряется смысл)
- Бизнес-логика в BFF (должна быть в микросервисах)

**Netflix:** Начинали с Zuul (API Gateway), пришли к federated GraphQL — по сути, BFF, где каждая команда управляет своей частью схемы.

---

## SOAP: исторический контекст

### Зачем знать о SOAP в 2025

SOAP мёртв для новых проектов, но живёт в enterprise-мире. Если ты интегрируешься с банками, госсистемами, SAP, Oracle ERP — столкнёшься с SOAP. Понимание «почему REST победил» помогает не повторять ошибки SOAP.

### Что такое SOAP

```xml
<!-- SOAP-запрос: получить пользователя -->
<!-- Обрати внимание на количество XML для простой операции -->

<soap:Envelope
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:usr="http://api.example.com/users">
  <soap:Header>
    <wsse:Security>
      <wsse:UsernameToken>
        <wsse:Username>admin</wsse:Username>
        <wsse:Password>secret</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>
  </soap:Header>
  <soap:Body>
    <usr:GetUser>
      <usr:UserId>123</usr:UserId>
    </usr:GetUser>
  </soap:Body>
</soap:Envelope>

<!-- То же самое в REST: -->
<!-- GET /users/123 + Authorization: Bearer token -->
<!-- Разница в объёме: ~500 байт SOAP vs ~50 байт REST -->
```

### Почему ушли от SOAP

| Проблема SOAP | Как REST решает |
|---------------|----------------|
| **XML обязателен** (verbose, ~500 байт для простого запроса) | JSON (компактный, ~50 байт) или любой формат |
| **Один endpoint, один метод (POST)** | Разные URL, разные HTTP-методы |
| **WSDL контракты** (сложный XML-schema) | OpenAPI/Swagger (JSON/YAML, человекочитаемый) |
| **WS-* стандарты** (WS-Security, WS-ReliableMessaging, WS-AtomicTransaction) | HTTP-заголовки, TLS, OAuth |
| **Специальные инструменты** (SoapUI, IDE-плагины) | curl, браузер, Postman |
| **Жёсткая связность** (WSDL привязывает клиента) | Loose coupling, гиперссылки |

### Где SOAP ещё живёт

- **Банки**: SWIFT, платёжные шлюзы (ACID-транзакции через WS-AtomicTransaction)
- **Госсистемы**: СМЭВ (Россия), Medicare (США), EU eDelivery
- **Enterprise ERP**: SAP, Oracle, Microsoft Dynamics (legacy-интеграции)
- **Здравоохранение**: HL7 v2 + SOAP (FHIR — это уже REST)
- **Телеком**: ONAP, TMF Open APIs (часть — SOAP)

**Совет:** Если нужно интегрироваться с SOAP — используй библиотеку (zeep для Python, node-soap для Node.js), не парси XML руками.

---

## JSON:API: стандарт для REST

### Что это

JSON:API — спецификация, стандартизирующая формат JSON-ответов в REST API. Вместо ad-hoc JSON-структур (у каждого API свой формат) — единый стандарт с relationships, pagination, sparse fieldsets.

### Формат

```json
// Стандартный REST (ad-hoc):
{
  "id": 1,
  "title": "GraphQL Guide",
  "author": {
    "id": 42,
    "name": "Иван"
  }
}

// JSON:API формат:
{
  "data": {
    "type": "articles",
    "id": "1",
    "attributes": {
      "title": "GraphQL Guide"
    },
    "relationships": {
      "author": {
        "data": { "type": "people", "id": "42" }
      }
    }
  },
  "included": [
    {
      "type": "people",
      "id": "42",
      "attributes": { "name": "Иван" }
    }
  ]
}
```

### Когда использовать

| За | Против |
|----|--------|
| Стандартизированный формат | Verbose (больше JSON) |
| Relationships из коробки | Overkill для простых API |
| Sparse fieldsets (`?fields[articles]=title`) | Меньше гибкости в структуре |
| Compound documents (include related) | Learning curve |
| Pagination стандартизирована | Не все клиентские библиотеки поддерживают |

**Подходит:** Если строишь REST API с complex relationships и хочешь стандарт вместо изобретения формата. Альтернатива: custom REST (как Stripe) или GraphQL (если relationships очень сложные).

---

## Decision Tree: какой API выбрать

```
┌──────────────────────────────────────────────────────────────────┐
│                 ВЫБОР API-ТЕХНОЛОГИИ                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Public API для third-party?                                      │
│  ├── Да → REST + OpenAPI                                         │
│  └── Нет ↓                                                        │
│                                                                   │
│  Внутренняя связь между микросервисами?                           │
│  ├── Да → Нужен streaming?                                       │
│  │        ├── Да → gRPC                                          │
│  │        └── Нет → gRPC (performance) или REST (простота)       │
│  └── Нет ↓                                                        │
│                                                                   │
│  Fullstack TypeScript монорепо?                                   │
│  ├── Да → tRPC                                                   │
│  └── Нет ↓                                                        │
│                                                                   │
│  Сложный UI, множество клиентов с разными потребностями?          │
│  ├── Да → GraphQL                                                │
│  └── Нет ↓                                                        │
│                                                                   │
│  Нужны event notifications (платежи, статусы)?                    │
│  ├── Да → Webhooks (+ REST/gRPC для основного API)               │
│  └── Нет ↓                                                        │
│                                                                   │
│  Простой CRUD?                                                    │
│  └── REST — проще не бывает                                      │
│                                                                   │
│  ГИБРИДНЫЙ ПОДХОД (норма для 2025):                               │
│  ─────────────────────────────────                                │
│  • REST для публичного API                                        │
│  • gRPC между микросервисами                                      │
│  • GraphQL для сложных клиентов                                   │
│  • tRPC для внутренних TypeScript-инструментов                    │
│  • Webhooks для event notifications                               │
│  • API Gateway как единая точка входа                             │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| **«tRPC заменяет REST/GraphQL»** | tRPC — для TypeScript-монорепо с одной командой. Публичные API, мобильные клиенты, multi-language — не его ниша. Stripe не перейдёт на tRPC |
| **«Webhooks надёжны»** | Webhooks НЕ гарантируют доставку и порядок. Нужна: верификация подписи, идемпотентность, retry-логика, dead letter queue. Без этого — потерянные события |
| **«API Gateway = reverse proxy»** | Reverse proxy (Nginx) маршрутизирует трафик. API Gateway добавляет: auth, rate limiting, transformation, analytics, developer portal. Kong — API Gateway. Nginx — reverse proxy |
| **«BFF = ещё один слой абстракции»** | BFF не добавляет абстракцию — он *адаптирует* данные для конкретного клиента. Mobile BFF агрегирует 5 вызовов в 1. Web BFF отдаёт полные данные. Разные потребности — разные backends |
| **«SOAP устарел и не нужен»** | Банковские API, госсистемы, ERP — SOAP живёт. При интеграции с enterprise-системами знание SOAP обязательно. FHIR (здравоохранение) — уже REST, но HL7 v2 — ещё SOAP |
| **«JSON:API = лучший формат для REST»** | JSON:API стандартизирует формат, но добавляет verbose. Stripe, GitHub — custom JSON, не JSON:API. Подходит для проектов, где стандартизация важнее компактности |

---

## CS-фундамент

| Концепция | Применение |
|-----------|-----------|
| **Type Safety** | tRPC: TypeScript inference передаёт типы от сервера к клиенту без codegen. Ошибки ловятся в compile-time |
| **Event-Driven** | Webhooks — push-модель: publisher → subscriber. Связь с [[event-driven-architecture]]: Kafka, RabbitMQ используют тот же паттерн |
| **Gateway Pattern** | API Gateway: Single Entry Point из паттернов GoF/microservices. Централизация cross-cutting concerns |
| **Message Signing** | HMAC-SHA256 для webhook-подписей. Криптографическая аутентичность: доказывает авторство без раскрытия секрета |
| **Idempotency** | Webhook retry: одно событие может прийти несколько раз. Idempotency key = event_id для защиты от дублирования |
| **Adapter Pattern** | BFF адаптирует общий API под конкретного клиента. Структурный паттерн: один интерфейс → разные реализации |

---

## Куда дальше

Базовые API-технологии:
→ [[api-design]] — обзор REST, GraphQL, gRPC: когда что выбрать
→ [[api-rest-deep-dive]] — REST constraints, HATEOAS, идемпотентность
→ [[api-graphql-deep-dive]] — Schema, federation, subscriptions, caching
→ [[api-grpc-deep-dive]] — Protobuf, 4 паттерна, error model, load balancing

Event-driven архитектура (foundation для Webhooks):
→ [[event-driven-architecture]] — Kafka, RabbitMQ, Event Sourcing, Saga pattern

Микросервисы (контекст для API Gateway и BFF):
→ [[microservices-vs-monolith]] — Когда микросервисы, когда монолит

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [tRPC Official Docs](https://trpc.io/docs) | Документация | Router, procedures, subscriptions |
| 2 | [tRPC vs GraphQL vs REST — SD Times](https://sdtimes.com/graphql/trpc-vs-graphql-vs-rest-choosing-the-right-api-design-for-modern-web-applications/) | Статья | Сравнение подходов, decision framework |
| 3 | [tRPC vs GraphQL — Better Stack](https://betterstack.com/community/guides/scaling-nodejs/trpc-vs-graphql/) | Руководство | Type safety, performance comparison |
| 4 | [WunderGraph: GraphQL vs Federation vs tRPC vs REST vs gRPC](https://wundergraph.com/blog/graphql-vs-federation-vs-trpc-vs-rest-vs-grpc-vs-asyncapi-vs-webhooks) | Статья | Полное сравнение всех подходов |
| 5 | [Webhooks.fyi: HMAC Security](https://webhooks.fyi/security/hmac) | Руководство | HMAC-SHA256 для webhook подписей |
| 6 | [Webhook Best Practices Guide — Inventive HQ](https://inventivehq.com/blog/webhook-best-practices-guide) | Статья | Retry, idempotency, monitoring |
| 7 | [Webhook Signature Verification — Apidog](https://apidog.com/blog/webhook-signature-verification/) | Руководство | HMAC verification implementation |
| 8 | [Stripe Webhooks Implementation Guide](https://www.hooklistener.com/learn/stripe-webhooks-implementation) | Руководство | Stripe-specific patterns |
| 9 | [Kong API Gateway](https://konghq.com/) | Документация | Open source API Gateway |
| 10 | [AWS API Gateway](https://aws.amazon.com/api-gateway/) | Документация | Managed API Gateway |
| 11 | [Sam Newman: BFF Pattern](https://samnewman.io/patterns/architectural/bff/) | Статья | Original BFF pattern description |
| 12 | [Netflix: Federated GraphQL](https://netflixtechblog.com/) | Блог | BFF evolution at Netflix |
| 13 | [JSON:API Specification](https://jsonapi.org/) | Спецификация | Стандарт для JSON REST |
| 14 | [AWS: SOAP vs REST](https://aws.amazon.com/compare/the-difference-between-soap-rest/) | Документация | SOAP vs REST comparison |
| 15 | [colinhacks.com: Painless Typesafety](https://colinhacks.com/essays/painless-typesafety) | Блог | tRPC origins, Zod validation |

---

**Последняя верификация**: 2026-02-10
**Уровень достоверности**: high

---

*Проверено: 2026-02-10*
