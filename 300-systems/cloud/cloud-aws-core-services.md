---
title: "AWS Core Services: EC2, RDS, Lambda, S3, IAM"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/cloud
  - topic/aws
  - ec2
  - lambda
  - s3
  - rds
  - type/concept
  - level/intermediate
related:
  - "[[cloud-overview]]"
  - "[[cloud-serverless-patterns]]"
  - "[[cloud-networking-security]]"
prerequisites:
  - "[[cloud-platforms-essentials]]"
reading_time: 14
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AWS Core Services: EC2, RDS, Lambda, S3, IAM

> AWS имеет 200+ сервисов, но 80% задач решаются 10-15 core сервисами. Фокус на практических паттернах и типичных use cases.

---

## TL;DR

- **EC2** — виртуальные машины, основа compute
- **Lambda** — serverless функции, event-driven
- **S3** — object storage, безлимитный и дешёвый
- **RDS** — managed PostgreSQL/MySQL, Multi-AZ для HA
- **IAM** — кто может делать что, Least Privilege

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Region** | Географическая локация (us-east-1, eu-west-1) |
| **AZ** | Availability Zone — датацентр внутри региона |
| **VPC** | Virtual Private Cloud — изолированная сеть |
| **Instance** | Виртуальная машина EC2 |
| **AMI** | Amazon Machine Image — образ для запуска EC2 |
| **Security Group** | Виртуальный firewall для instance |
| **IAM Role** | Набор permissions для сервиса |
| **ARN** | Amazon Resource Name — уникальный ID ресурса |

---

## EC2: Elastic Compute Cloud

### Instance Types

```
┌─────────────────────────────────────────────────────────────────┐
│                   EC2 INSTANCE TYPES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Naming: [family][generation].[size]                           │
│  Example: t3.medium, m6i.xlarge, r5.2xlarge                    │
│                                                                 │
│  FAMILY:                                                        │
│  ├── T (Burstable) — web servers, dev environments            │
│  ├── M (General)   — balanced CPU/memory                       │
│  ├── C (Compute)   — CPU intensive (encoding, gaming)          │
│  ├── R (Memory)    — databases, caching                        │
│  ├── G/P (GPU)     — ML training, graphics                     │
│  └── I (Storage)   — high IOPS databases                       │
│                                                                 │
│  SIZE:                                                          │
│  nano < micro < small < medium < large < xlarge < 2xlarge...  │
│                                                                 │
│  GENERATION: Новее = лучше price/performance                   │
│  t2 → t3 → t3a (AMD) → t4g (ARM Graviton)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pricing Models

| Модель | Описание | Экономия | Use Case |
|--------|----------|----------|----------|
| **On-Demand** | Платишь за час/секунду | 0% | Dev, testing, unpredictable |
| **Reserved** | 1-3 года commitment | до 72% | Production, stable workload |
| **Savings Plans** | $/час commitment | до 66% | Гибче Reserved |
| **Spot** | Unused capacity | до 90% | Batch, fault-tolerant |

### Практические команды

```bash
# Запустить instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-12345678 \
  --subnet-id subnet-12345678

# Список instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType,IP:PublicIpAddress}'

# SSH подключение
ssh -i my-key.pem ec2-user@<public-ip>

# Остановить/запустить
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

---

## Lambda: Serverless Functions

### Концепция

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS LAMBDA                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Trigger          Lambda Function         Destination           │
│  ┌─────────┐      ┌─────────────┐        ┌─────────┐           │
│  │API GW   │──────│             │────────│DynamoDB │           │
│  │S3 Event │──────│  Your Code  │────────│S3       │           │
│  │SQS      │──────│  (handler)  │────────│SQS      │           │
│  │Schedule │──────│             │────────│SNS      │           │
│  └─────────┘      └─────────────┘        └─────────┘           │
│                                                                 │
│  Платишь за:                                                   │
│  • Количество вызовов                                          │
│  • Время выполнения (GB-seconds)                               │
│  • Free tier: 1M вызовов + 400K GB-sec/месяц                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Пример Lambda (Python)

```python
# handler.py
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def handler(event, context):
    """
    API Gateway → Lambda → DynamoDB
    """
    # Получить данные из запроса
    body = json.loads(event['body'])

    # Записать в DynamoDB
    table.put_item(Item={
        'order_id': body['order_id'],
        'user_id': body['user_id'],
        'amount': body['amount']
    })

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Order created'})
    }
```

### Ограничения Lambda

| Параметр | Лимит |
|----------|-------|
| Timeout | 15 минут max |
| Memory | 128MB - 10GB |
| Package size | 50MB (zip), 250MB (unzipped) |
| /tmp storage | 512MB - 10GB |
| Concurrent executions | 1000 (default, можно увеличить) |
| Payload size | 6MB (sync), 256KB (async) |

---

## S3: Simple Storage Service

### Storage Classes

```
┌─────────────────────────────────────────────────────────────────┐
│                   S3 STORAGE CLASSES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STANDARD ─────────────────────────────────────────────────────│
│  • Частый доступ, низкая latency                               │
│  • 99.99% availability, 11 nines durability                    │
│  • Цена: $0.023/GB                                             │
│                                                                 │
│  INTELLIGENT-TIERING ──────────────────────────────────────────│
│  • Автоматическое перемещение между tiers                      │
│  • Для unpredictable access patterns                           │
│                                                                 │
│  STANDARD-IA (Infrequent Access) ──────────────────────────────│
│  • Редкий доступ, но быстрый когда нужен                      │
│  • Цена: $0.0125/GB + retrieval fee                            │
│                                                                 │
│  GLACIER ──────────────────────────────────────────────────────│
│  • Архив, retrieval от минут до часов                          │
│  • Цена: $0.004/GB                                             │
│                                                                 │
│  GLACIER DEEP ARCHIVE ─────────────────────────────────────────│
│  • Долгосрочный архив, retrieval 12+ часов                     │
│  • Цена: $0.00099/GB (самый дешёвый)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Практические команды

```bash
# Создать bucket
aws s3 mb s3://my-unique-bucket-name

# Загрузить файл
aws s3 cp file.txt s3://my-bucket/path/file.txt

# Синхронизация директории
aws s3 sync ./local-dir s3://my-bucket/remote-dir

# Скачать
aws s3 cp s3://my-bucket/file.txt ./local-file.txt

# Presigned URL (временный доступ)
aws s3 presign s3://my-bucket/private-file.pdf --expires-in 3600

# Lifecycle policy (JSON)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json
```

### S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-public-bucket/*"
    },
    {
      "Sid": "DenyNonSSL",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "Bool": { "aws:SecureTransport": "false" }
      }
    }
  ]
}
```

---

## RDS: Managed Databases

### Engines

| Engine | Use Case |
|--------|----------|
| **PostgreSQL** | General purpose, JSONB, extensions |
| **MySQL** | WordPress, legacy apps |
| **Aurora** | MySQL/PostgreSQL compatible, 5x faster |
| **MariaDB** | MySQL fork, open source |
| **SQL Server** | Microsoft shops |
| **Oracle** | Enterprise legacy |

### Multi-AZ vs Read Replicas

```
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-AZ vs READ REPLICAS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MULTI-AZ (High Availability)                                  │
│  ┌─────────────┐     Sync     ┌─────────────┐                  │
│  │   Primary   │ ──────────── │   Standby   │                  │
│  │   (AZ-a)    │  Replication │   (AZ-b)    │                  │
│  └─────────────┘              └─────────────┘                  │
│        ▲                             │                          │
│        │                    Failover │                          │
│   Writes/Reads               (auto)  │                          │
│                                      ▼                          │
│  • Automatic failover (60-120 sec)                             │
│  • Standby не доступен для чтения                              │
│  • Для HA, не для performance                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  READ REPLICAS (Scaling)                                       │
│  ┌─────────────┐     Async     ┌─────────────┐                 │
│  │   Primary   │ ──────────── │  Replica 1  │ ◀── Reads       │
│  │             │ ──────────── │  Replica 2  │ ◀── Reads       │
│  └─────────────┘              └─────────────┘                  │
│        ▲                                                        │
│        │                                                        │
│   Writes                                                        │
│                                                                 │
│  • До 15 replicas                                              │
│  • Cross-region возможно                                       │
│  • Для read scaling                                            │
│  • Async = eventual consistency                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Создание RDS

```bash
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --allocated-storage 20 \
  --multi-az \
  --vpc-security-group-ids sg-12345678

# Connection string
psql "host=mydb.xxxxx.us-east-1.rds.amazonaws.com \
      port=5432 \
      dbname=mydb \
      user=admin \
      password=xxx"
```

---

## IAM: Identity and Access Management

### Концепция

```
┌─────────────────────────────────────────────────────────────────┐
│                        IAM                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WHO (Principal)         WHAT (Action)        WHERE (Resource) │
│  ┌─────────────┐        ┌─────────────┐      ┌─────────────┐  │
│  │ User        │        │ s3:GetObject│      │ arn:aws:s3::│  │
│  │ Role        │ ─────▶ │ ec2:Start*  │ ───▶ │ :bucket/*   │  │
│  │ Service     │        │ rds:Describe│      │             │  │
│  └─────────────┘        └─────────────┘      └─────────────┘  │
│                                                                 │
│  Policy = JSON документ с разрешениями                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    },
    {
      "Sid": "AllowDynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789:table/Users"
    },
    {
      "Sid": "DenyDeleteTable",
      "Effect": "Deny",
      "Action": "dynamodb:DeleteTable",
      "Resource": "*"
    }
  ]
}
```

### Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│                   IAM BEST PRACTICES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LEAST PRIVILEGE                                            │
│     • Минимально необходимые права                             │
│     • Начни с 0, добавляй по необходимости                    │
│                                                                 │
│  2. USE ROLES, NOT KEYS                                        │
│     • EC2/Lambda используют IAM Roles                          │
│     • Не хардкодь access keys                                  │
│                                                                 │
│  3. MFA EVERYWHERE                                             │
│     • Особенно для root account                                │
│     • Для sensitive operations                                 │
│                                                                 │
│  4. ROTATE CREDENTIALS                                         │
│     • Access keys каждые 90 дней                               │
│     • Автоматизируй через Secrets Manager                      │
│                                                                 │
│  5. USE CONDITIONS                                             │
│     • IP restrictions                                          │
│     • MFA required                                             │
│     • Time-based access                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Другие важные сервисы

| Сервис | Описание | Use Case |
|--------|----------|----------|
| **SQS** | Message queue | Async processing, decoupling |
| **SNS** | Pub/Sub notifications | Alerts, fan-out |
| **DynamoDB** | NoSQL key-value | Serverless, high scale |
| **ElastiCache** | Managed Redis/Memcached | Caching |
| **CloudFront** | CDN | Static content, global |
| **Route 53** | DNS | Domain management |
| **API Gateway** | REST/WebSocket APIs | Lambda frontend |
| **ECS/EKS** | Container orchestration | Docker workloads |
| **Secrets Manager** | Secrets storage | DB passwords, API keys |
| **CloudWatch** | Monitoring/Logging | Observability |

---

## Связи

- [[cloud-overview]] — карта раздела
- [[cloud-serverless-patterns]] — паттерны serverless
- [[cloud-networking-security]] — VPC, Security Groups
- [[infrastructure-as-code]] — Terraform для AWS

---

## Источники

- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Solutions Library](https://aws.amazon.com/solutions/)
- "AWS Certified Solutions Architect Study Guide"

---

---

## Проверь себя

> [!question]- Почему IAM Role предпочтительнее Access Keys для EC2 и Lambda, даже если Access Keys проще настроить?
> IAM Role предоставляет временные credentials, которые автоматически ротируются. Access Keys — долгоживущие секреты, которые можно случайно закоммитить в репозиторий или забыть ротировать. С Role нет secrets в коде вообще — AWS SDK автоматически получает credentials через instance metadata.

> [!question]- У вас SaaS-приложение с предсказуемой нагрузкой днём и почти нулевой ночью. Какую комбинацию EC2 pricing models вы выберете и почему?
> Reserved Instances для базовой дневной нагрузки (экономия до 72%), плюс On-Demand или Auto Scaling для пиков. Ночью Auto Scaling уменьшает количество инстансов до минимума. Spot не подходит для production API, но может использоваться для background jobs.

> [!question]- Сравните Multi-AZ RDS и Read Replicas: можно ли использовать standby в Multi-AZ для чтения?
> Нет. В Multi-AZ standby реплика синхронно копирует данные, но не доступна для чтения — она только для failover. Read Replicas используют async репликацию и доступны для чтения, но не дают автоматический failover. Для максимальной отказоустойчивости и производительности используют оба варианта вместе.

> [!question]- В каком случае S3 Intelligent-Tiering лучше, чем ручная настройка Lifecycle Policies?
> Когда паттерн доступа к данным непредсказуем. Intelligent-Tiering автоматически перемещает объекты между tiers на основе реального доступа. Lifecycle Policies фиксированы по времени (через 30 дней в IA). Если данные иногда запрашиваются через 60 дней, Lifecycle уже переместит их в Glacier, а Intelligent-Tiering оставит в быстром доступе.

---

## Ключевые карточки

Как расшифровывается имя EC2 instance type, например t3.medium?
?
t — family (Burstable), 3 — generation, medium — size. Family определяет назначение (T — web servers, C — compute, R — memory, G/P — GPU).

Какой free tier у AWS Lambda?
?
1 миллион вызовов + 400 000 GB-seconds в месяц бесплатно. Этого достаточно для многих небольших проектов и прототипов.

Чем S3 Standard отличается от S3 Glacier?
?
Standard — частый доступ, $0.023/GB, мгновенный доступ. Glacier — архивное хранение, $0.004/GB, retrieval от минут до часов. Glacier в 5-6 раз дешевле, но не для оперативных данных.

Что такое ARN в AWS?
?
Amazon Resource Name — уникальный идентификатор любого ресурса AWS. Формат: arn:aws:service:region:account:resource. Используется в IAM policies для указания конкретных ресурсов.

Какой максимальный timeout у Lambda?
?
15 минут. Для задач дольше 15 минут нужно использовать Step Functions для оркестрации или ECS/Fargate для контейнеров.

Что делает S3 Presigned URL?
?
Создаёт временную ссылку для доступа к private объекту в S3 без изменения permissions bucket. URL действителен ограниченное время (например, 1 час). Используется для безопасной раздачи файлов.

Какой принцип Least Privilege в IAM?
?
Давать минимально необходимые права. Начинать с нуля разрешений и добавлять только то, что реально нужно сервису. Никогда не использовать wildcard (*) в production policies без крайней необходимости.

Сколько Read Replicas поддерживает RDS?
?
До 15 replicas. Они используют асинхронную репликацию, могут быть cross-region, и подходят для масштабирования читающих запросов. Eventual consistency — данные могут отставать.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cloud-serverless-patterns]] | Углублённые паттерны Lambda: event-driven, Step Functions, cold starts |
| Следующий шаг | [[cloud-networking-security]] | VPC, Security Groups и IAM policies для защиты AWS ресурсов |
| Углубиться | [[cloud-disaster-recovery]] | Multi-AZ и Multi-Region стратегии для высокой доступности |
| Смежная тема | [[infrastructure-as-code]] | Terraform и AWS CDK для автоматизации инфраструктуры |
| Смежная тема | [[databases-fundamentals-complete]] | Фундамент работы с базами данных для понимания RDS и DynamoDB |
| Обзор | [[cloud-overview]] | Карта раздела Cloud с навигацией по всем статьям |

---

*Проверено: 2025-12-22*
