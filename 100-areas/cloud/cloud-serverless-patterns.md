---
title: "Serverless Patterns: Lambda, Event-Driven, Step Functions"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - cloud
  - serverless
  - lambda
  - event-driven
  - step-functions
related:
  - "[[cloud-overview]]"
  - "[[cloud-aws-core-services]]"
  - "[[architecture-event-driven]]"
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

## Проверь себя

<details>
<summary>1. Что такое cold start и как его уменьшить?</summary>

**Ответ:** Cold start — задержка при первом вызове Lambda после простоя (инициализация runtime, код, dependencies).

Как уменьшить:
- Маленький package size (tree shaking, минимум dependencies)
- Init код вне handler (connections, imports)
- Provisioned Concurrency (pre-warmed instances)
- Легкий runtime (Python/Node vs Java)
- Избегать VPC если не нужен

</details>

<details>
<summary>2. Когда использовать Step Functions вместо цепочки Lambda?</summary>

**Ответ:**
- Workflow дольше 15 минут
- Нужны retries с exponential backoff
- Branching logic (if/else)
- Parallel execution
- Human approval
- Визуализация workflow
- Audit trail

Lambda→Lambda напрямую — anti-pattern (tight coupling, hard to debug).

</details>

<details>
<summary>3. Как сделать Lambda идемпотентной?</summary>

**Ответ:** Идемпотентность — повторный вызов даёт тот же результат.

Реализация:
1. Уникальный idempotency key в event
2. Сохранять processed keys в DynamoDB/Redis
3. При повторе — возвращать cached результат

```python
if dynamo.get_item(idempotency_key):
    return cached_result
result = process(event)
dynamo.put_item(idempotency_key, result, TTL=24h)
return result
```

</details>

<details>
<summary>4. Когда serverless НЕ подходит?</summary>

**Ответ:**
- Долгие процессы (> 15 min) — ECS/EKS
- Stateful workloads — containers
- Low latency требования (< 10ms) — cold starts мешают
- Высокий постоянный traffic — EC2 дешевле
- Complex networking — VPC добавляет latency
- Vendor lock-in неприемлем

</details>

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

*Проверено: 2025-12-22*
