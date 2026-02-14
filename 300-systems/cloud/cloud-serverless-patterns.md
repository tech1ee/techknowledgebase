---
title: "Serverless Patterns: Lambda, Event-Driven, Step Functions"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/cloud
  - serverless
  - lambda
  - event-driven
  - step-functions
  - type/concept
  - level/intermediate
related:
  - "[[cloud-overview]]"
  - "[[cloud-aws-core-services]]"
  - "[[architecture-event-driven]]"
prerequisites:
  - "[[cloud-platforms-essentials]]"
  - "[[cloud-aws-core-services]]"
reading_time: 12
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Serverless Patterns: Lambda, Event-Driven, Step Functions

> Serverless — не "без серверов", а "без управления серверами". Платишь за выполнение, не за простой. Идеально для event-driven и variable workloads.

---

## TL;DR

- **Cold start** — 100-500ms задержка при первом вызове
- **Event-driven** — реакция на события (S3, SQS, HTTP)
- **Step Functions** — оркестрация для сложных workflows
- **Ограничения** — 15 min timeout, stateless, vendor lock-in
- **Когда НЕ использовать** — долгие процессы, stateful, low-latency требования

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Cold Start** | Первый вызов после простоя, инициализация |
| **Warm Start** | Повторный вызов на "тёплом" instance |
| **Provisioned Concurrency** | Pre-warmed instances (нет cold starts) |
| **Event Source** | Триггер: HTTP, S3, SQS, Schedule |
| **Fan-out** | Один event → много обработчиков |
| **Saga** | Распределённая транзакция через события |
| **Step Functions** | AWS сервис для orchestration workflows |
| **DLQ** | Dead Letter Queue — очередь failed events |

---

## Serverless Compute: сравнение

```
┌─────────────────────────────────────────────────────────────────┐
│                SERVERLESS COMPUTE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AWS Lambda         GCP Cloud Functions    Azure Functions     │
│  ─────────────────  ─────────────────────  ─────────────────   │
│  • 15 min timeout   • 9 min (HTTP)         • 10 min (Consumption│
│  • 10GB memory      • 60 min (events)      • Unlimited (Premium)│
│  • Zip/Container    • 32GB memory          • Zip/Container     │
│                     • Zip/Container                             │
│                                                                 │
│  AWS Cloud Run      GCP Cloud Run          Azure Container Apps │
│  ─────────────────  ─────────────────────  ─────────────────   │
│  (App Runner)       • Any container        • Any container     │
│  • Containers       • 60 min timeout       • Scale to zero     │
│  • Auto-scale       • 32GB memory                              │
│                     • 1000 concurrent req                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cold Start: проблема и решения

```
┌─────────────────────────────────────────────────────────────────┐
│                     COLD START                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Request                                                        │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Cold Start (100-500ms+)                                 │   │
│  │ ├── Download code                                       │   │
│  │ ├── Start runtime (Node/Python/Java)                   │   │
│  │ ├── Initialize dependencies                            │   │
│  │ └── Run init code (outside handler)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Handler Execution (~50-200ms)                           │   │
│  │ └── Your business logic                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Cold starts зависят от:                                       │
│  • Runtime: Java/C# дольше, Python/Node быстрее              │
│  • Package size: больше = дольше                              │
│  • VPC: добавляет 1-10 секунд (AWS улучшил)                  │
│  • Init code: импорты, DB connections                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Оптимизация cold starts

```python
# ❌ Плохо: импорт внутри handler (каждый раз)
def handler(event, context):
    import pandas as pd  # Медленно!
    # ...

# ✅ Хорошо: импорт снаружи (один раз при cold start)
import pandas as pd

# Инициализация DB connection вне handler
db = create_connection()

def handler(event, context):
    # db уже готов
    result = db.query(...)
    return result
```

```yaml
# Provisioned Concurrency (AWS)
# Держит N warm instances всегда готовыми

Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    # ...

  ProvisionedConcurrency:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref MyFunction
      FunctionVersion: $LATEST
      Name: prod
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5
```

---

## Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              EVENT-DRIVEN PATTERNS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. REQUEST-RESPONSE (Sync)                                    │
│     Client ──▶ API Gateway ──▶ Lambda ──▶ Response             │
│                                                                 │
│  2. ASYNC PROCESSING                                           │
│     Client ──▶ API GW ──▶ SQS ──▶ Lambda (async)              │
│                    │                                            │
│                    └──▶ 202 Accepted (immediate)               │
│                                                                 │
│  3. FAN-OUT                                                    │
│                         ┌──▶ Lambda A ──▶ DB                   │
│     S3 Event ──▶ SNS ──┼──▶ Lambda B ──▶ ElasticSearch        │
│                         └──▶ Lambda C ──▶ Analytics            │
│                                                                 │
│  4. EVENT SOURCING                                             │
│     API ──▶ Lambda ──▶ EventBridge ──▶ Multiple consumers     │
│                             │                                   │
│                             └──▶ Event Store (audit log)       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Паттерн: Async с SQS

```python
# Producer: отправляет в очередь
import boto3

sqs = boto3.client('sqs')

def api_handler(event, context):
    order = json.loads(event['body'])

    # Отправить в очередь для async обработки
    sqs.send_message(
        QueueUrl='https://sqs.../orders-queue',
        MessageBody=json.dumps(order)
    )

    return {
        'statusCode': 202,
        'body': json.dumps({'status': 'accepted', 'orderId': order['id']})
    }

# Consumer: обрабатывает из очереди
def process_order(event, context):
    for record in event['Records']:
        order = json.loads(record['body'])

        # Долгая обработка
        process_payment(order)
        update_inventory(order)
        send_notification(order)
```

---

## Step Functions: Orchestration

```
┌─────────────────────────────────────────────────────────────────┐
│                   STEP FUNCTIONS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Когда использовать:                                           │
│  • Workflow > 15 минут                                         │
│  • Branching logic (if/else)                                   │
│  • Retry с backoff                                             │
│  • Human approval steps                                        │
│  • Parallel execution                                          │
│                                                                 │
│  Пример: Order Processing                                      │
│                                                                 │
│  Start ──▶ Validate ──▶ Process  ──▶ Notify ──▶ End           │
│               │         Payment        │                        │
│               │            │           │                        │
│               │      ┌─────┴─────┐     │                        │
│               │      │           │     │                        │
│               │    Success     Fail    │                        │
│               │      │           │     │                        │
│               │      ▼           ▼     │                        │
│               │   Reserve    Refund    │                        │
│               │   Inventory    (retry) │                        │
│               │      │                 │                        │
│               └──────┴─────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step Functions Definition (ASL)

```json
{
  "Comment": "Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:validate-order",
      "Next": "ProcessPayment",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "OrderFailed"
      }]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:process-payment",
      "Retry": [{
        "ErrorEquals": ["PaymentError"],
        "IntervalSeconds": 5,
        "MaxAttempts": 3,
        "BackoffRate": 2
      }],
      "Next": "ParallelTasks"
    },
    "ParallelTasks": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "ReserveInventory",
          "States": {
            "ReserveInventory": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:...:reserve-inventory",
              "End": true
            }
          }
        },
        {
          "StartAt": "SendNotification",
          "States": {
            "SendNotification": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:...:send-notification",
              "End": true
            }
          }
        }
      ],
      "Next": "OrderComplete"
    },
    "OrderComplete": {
      "Type": "Succeed"
    },
    "OrderFailed": {
      "Type": "Fail",
      "Error": "OrderProcessingFailed"
    }
  }
}
```

---

## Anti-patterns и Best Practices

### Что НЕ делать

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANTI-PATTERNS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ Lambda вызывает Lambda синхронно                            │
│     (используй Step Functions или SQS)                         │
│                                                                 │
│  ❌ Долгие операции в Lambda (> 5 min)                          │
│     (используй Step Functions, ECS, или batch)                 │
│                                                                 │
│  ❌ Stateful logic в Lambda                                     │
│     (используй DynamoDB, Redis для state)                      │
│                                                                 │
│  ❌ Large payloads через Lambda                                 │
│     (используй S3 для больших файлов)                          │
│                                                                 │
│  ❌ Нет error handling и retries                                │
│     (DLQ для failed events, retry policies)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Best Practices

```python
# ✅ Идемпотентность: обработка дублей
def handler(event, context):
    idempotency_key = event['idempotencyKey']

    # Проверить был ли уже обработан
    if already_processed(idempotency_key):
        return existing_result(idempotency_key)

    result = process(event)
    save_result(idempotency_key, result)
    return result


# ✅ Structured logging
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(json.dumps({
        'event': 'order_created',
        'order_id': event['orderId'],
        'user_id': event['userId'],
        'request_id': context.aws_request_id
    }))


# ✅ Error handling с DLQ
# serverless.yml
functions:
  processOrder:
    handler: handler.process
    events:
      - sqs:
          arn: !GetAtt OrdersQueue.Arn
    maximumRetryAttempts: 3
    deadLetterQueue:
      arn: !GetAtt OrdersDLQ.Arn
```

---

## Связи

- [[cloud-overview]] — карта раздела
- [[cloud-aws-core-services]] — AWS Lambda детали
- [[architecture-event-driven]] — event-driven архитектура
- [[architecture-distributed-systems]] — Saga pattern

---

## Источники

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/)
- "Serverless Architectures on AWS" by Peter Sbarski

---

---

## Проверь себя

> [!question]- Почему Lambda-вызывающая-Lambda синхронно считается anti-pattern?
> Это создаёт tight coupling: вызывающая Lambda ждёт ответа, платит за время ожидания и может timeout. При ошибке во второй Lambda первая тоже падает. Лучше использовать SQS (async decoupling) или Step Functions (orchestration с retry и error handling). Это даёт loose coupling и независимое масштабирование.

> [!question]- В каком сценарии Provisioned Concurrency оправдан, несмотря на дополнительную стоимость?
> Когда приложение требует предсказуемо низкую latency — например, API, где cold start в 500ms+ неприемлем для пользовательского опыта. Также для Java/.NET рантаймов, где cold start особенно долгий. Provisioned Concurrency держит N warm instances, устраняя cold start полностью. Стоимость оправдана, если alternative — переход на EC2/ECS.

> [!question]- Сравните синхронный (request-response) и асинхронный (SQS) паттерны обработки. Когда выбрать какой?
> Синхронный — когда клиенту нужен немедленный результат (чтение данных, валидация). Асинхронный через SQS — когда обработка долгая (отправка email, генерация отчёта, обработка платежа) и клиенту достаточно получить 202 Accepted. Async также обеспечивает resilience: SQS сохраняет сообщения при падении consumer.

> [!question]- Почему идемпотентность критична для serverless и как её обеспечить?
> Lambda может быть вызвана повторно из-за retry (SQS, network timeout). Без идемпотентности повторный вызов создаст дублирующий заказ или двойное списание. Реализация: idempotency key из event, проверка в DynamoDB/Redis перед обработкой, сохранение результата с TTL. При повторе — возврат cached результата.

---

## Ключевые карточки

Что такое cold start и от чего он зависит?
?
Задержка 100-500ms+ при первом вызове Lambda после простоя. Зависит от: runtime (Java дольше, Python/Node быстрее), размера package, наличия VPC, объёма init-кода вне handler.

Что такое Dead Letter Queue (DLQ)?
?
Очередь для сообщений, которые не удалось обработать после заданного числа retry. Позволяет не потерять failed events и проанализировать их позже. Обязательна для production serverless.

Как оптимизировать cold start Lambda?
?
1) Импорты и DB connections вне handler. 2) Маленький package size (tree shaking). 3) Лёгкий runtime (Python/Node). 4) Provisioned Concurrency для критичных функций. 5) Избегать VPC без необходимости.

Чем Step Functions лучше цепочки Lambda -> Lambda?
?
Step Functions обеспечивают: retry с exponential backoff, branching (if/else), parallel execution, визуализацию workflow, audit trail. Прямой вызов Lambda -> Lambda — tight coupling, сложно дебажить, нет retry logic.

Что такое fan-out паттерн?
?
Одно событие запускает множество обработчиков параллельно. Например: файл загружен в S3 -> SNS -> Lambda A (thumbnail), Lambda B (index), Lambda C (analytics). SNS обеспечивает pub/sub распределение.

Когда serverless НЕ подходит?
?
1) Процессы дольше 15 минут. 2) Stateful workloads. 3) Требования latency < 10ms (cold starts). 4) Постоянная высокая нагрузка (EC2 дешевле). 5) Неприемлем vendor lock-in.

Что такое event sourcing в serverless?
?
Паттерн, где все изменения записываются как события в EventBridge/Kinesis. Multiple consumers подписываются на события независимо. Обеспечивает audit log, replay событий и loose coupling между сервисами.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cloud-disaster-recovery]] | DR стратегии для serverless и event-driven архитектур |
| Углубиться | [[event-driven-architecture]] | Глубокие паттерны event-driven: CQRS, event sourcing, saga |
| Углубиться | [[architecture-resilience-patterns]] | Паттерны устойчивости: circuit breaker, retry, bulkhead |
| Смежная тема | [[architecture-distributed-systems]] | Распределённые системы: Saga pattern, eventual consistency |
| Смежная тема | [[ai-api-integration]] | Интеграция AI API через serverless: cost-effective inference |
| Обзор | [[cloud-overview]] | Карта раздела Cloud с навигацией по всем статьям |

---

*Проверено: 2025-12-22*
