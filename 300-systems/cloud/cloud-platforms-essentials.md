---
title: "Cloud Platforms: от bare metal до serverless"
created: 2025-11-24
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/cloud
  - cloud/aws
  - cloud/gcp
  - cloud/azure
  - devops/cloud
  - type/concept
  - level/intermediate
related:
  - "[[infrastructure-as-code]]"
  - "[[kubernetes-basics]]"
  - "[[ci-cd-pipelines]]"
  - "[[network-cloud-modern]]"
  - "[[networking-overview]]"
prerequisites:
  - "[[network-fundamentals-for-developers]]"
reading_time: 23
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Cloud Platforms: от bare metal до serverless

On-premise: $50k + 4 недели настройки. Cloud: 5 минут и $5/месяц на старт. AWS — 33% рынка, самый mature. GCP — лучший K8s и BigQuery. Azure — для Microsoft стека. Trade-off: vendor lock-in.

---

## Теоретические основы

> **Cloud Platform** — интегрированная экосистема облачных сервисов от одного провайдера, предоставляющая compute, storage, networking, managed services и инструменты разработки через единый API и консоль.

### Историческая хронология

| Год | Событие |
|-----|---------|
| 2006 | AWS запускает S3 и EC2 — начало modern cloud |
| 2008 | Google App Engine (PaaS) |
| 2010 | Microsoft Azure (GA) |
| 2011 | NIST публикует определение Cloud Computing (SP 800-145) |
| 2014 | AWS Lambda — начало serverless эры |
| 2015 | Google открывает Kubernetes (CNCF) |
| 2019 | Multi-cloud становится корпоративным стандартом |

### Рынок облачных платформ (2025)

| Провайдер | Доля рынка | Сильные стороны |
|-----------|-----------|-----------------|
| **AWS** | ~32% | Самый зрелый, 200+ сервисов, наибольшая экосистема |
| **Azure** | ~23% | Microsoft интеграция, Enterprise, Hybrid (Azure Arc) |
| **GCP** | ~12% | Kubernetes, BigQuery, ML/AI, networking |

### AWS Well-Architected Framework: 6 столпов

| Столп | Принцип |
|-------|---------|
| **Operational Excellence** | Автоматизация, IaC, observability |
| **Security** | Least privilege, encryption, compliance |
| **Reliability** | Fault tolerance, auto-recovery |
| **Performance Efficiency** | Правильный выбор ресурсов под workload |
| **Cost Optimization** | Оплата только за используемое (FinOps) |
| **Sustainability** | Минимизация environmental impact |

> **См. также**: [[cloud-overview]] — карта раздела, [[infrastructure-as-code]] — IaC

---

## Зачем это нужно

### Проблема: On-premise требует капитальных затрат и экспертизы

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| **"Сервер заказали 6 недель назад"** | Hardware procurement, доставка, установка | Медленный time-to-market |
| **"Black Friday положил сервера"** | Нет эластичности, фиксированная capacity | Потеря выручки, недоступность |
| **"Нужна команда DevOps 24/7"** | Ответственность за всё (hardware, сети, security) | Рост затрат на персонал |
| **"DR? Это же ещё $100k"** | Второй data center для disaster recovery | Нет resilience или огромные затраты |

### Кому нужны облачные платформы

| Роль | Зачем нужно | Глубина |
|------|-------------|---------|
| **Backend Developer** | Деплой, managed services, serverless | Средняя |
| **DevOps/SRE** | Инфраструктура, CI/CD, мониторинг | Глубокая |
| **Tech Lead** | Архитектурные решения, cost optimization | Средняя |
| **Startup Founder** | Быстрый старт без upfront costs | Базовая-Средняя |

---

## Актуальность 2024-2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **FinOps** | 🔥 Критично | Управление cloud costs — отдельная дисциплина, требует tooling |
| **Multi-Cloud** | ⚠️ Осторожно | Сложность растёт экспоненциально, оправдано редко |
| **Serverless Containers** | ✅ Mainstream | AWS Fargate, Cloud Run, Azure Container Apps — K8s без управления нодами |
| **AI/ML Services** | 🆕 Растёт | Vertex AI, SageMaker, Azure ML — managed ML infrastructure |
| **Edge Computing** | 🆕 2024-2025 | CloudFront Functions, Cloudflare Workers — вычисления ближе к пользователю |
| **Sustainability** | ✅ Важно | Carbon footprint cloud regions, Green regions |

**Доля рынка Q1 2025:**
- AWS: 31%
- Azure: 25%
- GCP: 11%
- Остальные: 33%

---

## Терминология

| Термин | Значение |
|--------|----------|
| **IaaS** | Infrastructure as a Service (VM, сети) |
| **PaaS** | Platform as a Service (App Engine, Heroku) |
| **SaaS** | Software as a Service (Gmail, Slack) |
| **Serverless** | Платишь за вызовы, не за серверы |
| **Region** | Географический регион (us-east-1) |
| **Availability Zone** | Data center внутри региона |
| **VPC** | Virtual Private Cloud — изолированная сеть |
| **Vendor lock-in** | Зависимость от конкретного провайдера |
| **Multi-cloud** | Использование нескольких облаков |

---

## Зачем облако?

```
On-Premise (свой data center):

Купить серверы:       $50,000+
Настроить:            2-4 недели
Масштабирование:      заказать новое железо (недели)
Безопасность:         ты отвечаешь за всё
Обслуживание:         твоя команда 24/7
Disaster Recovery:    второй data center? +$100k

───────────────────────────────────────────────────────

Cloud:

Создать VM:           5 минут
Масштабирование:      автоматически (секунды)
Безопасность:         shared responsibility model
Обслуживание:         управляется провайдером
Disaster Recovery:    multi-region из коробки
Цена:                 $5-100/месяц для старта

Trade-offs:
+ Быстрый старт, нет upfront costs
+ Elasticity (scale up/down)
+ Global reach (data centers по всему миру)
- Дороже на длинной дистанции для stable workload
- Vendor lock-in
- Сложность управления стоимостью
```

---

## AWS vs GCP vs Azure: выбор провайдера

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS (Amazon Web Services)                    │
├─────────────────────────────────────────────────────────────────┤
│ Доля рынка:  33%                                                │
│ Год запуска: 2006                                               │
│                                                                 │
│ Плюсы:                                                          │
│ • Самый зрелый, больше всего сервисов (200+)                    │
│ • Огромное community, много документации                        │
│ • Enterprise-ready (compliance, support)                        │
│ • Самый большой выбор регионов                                  │
│                                                                 │
│ Минусы:                                                         │
│ • Сложная структура цен                                         │
│ • Legacy UI в некоторых сервисах                                │
│ • Крутая кривая обучения                                        │
│                                                                 │
│ Выбирай AWS если:                                               │
│ • Нужна максимальная гибкость                                   │
│ • Enterprise с compliance требованиями                          │
│ • Много разных сервисов (IoT, ML, analytics, etc)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 GCP (Google Cloud Platform)                     │
├─────────────────────────────────────────────────────────────────┤
│ Доля рынка:  10%                                                │
│ Год запуска: 2008                                               │
│                                                                 │
│ Плюсы:                                                          │
│ • Лучший Kubernetes (GKE) — они его создали                     │
│ • BigQuery — невероятная аналитика                              │
│ • Vertex AI — отличный ML stack                                 │
│ • Простой UI, лучший DX                                         │
│ • Дешевле AWS на ~20-30%                                        │
│                                                                 │
│ Минусы:                                                         │
│ • Меньше сервисов чем AWS                                       │
│ • Меньше регионов                                               │
│ • Enterprise support слабее AWS                                 │
│                                                                 │
│ Выбирай GCP если:                                               │
│ • Фокус на K8s, контейнеры                                      │
│ • Тяжёлая аналитика (BigQuery)                                  │
│ • ML/AI проекты                                                 │
│ • Хочешь лучший DX                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Azure (Microsoft Azure)                      │
├─────────────────────────────────────────────────────────────────┤
│ Доля рынка:  23%                                                │
│ Год запуска: 2010                                               │
│                                                                 │
│ Плюсы:                                                          │
│ • Лучший для Microsoft стека (.NET, Windows, AD)                │
│ • Hybrid cloud (Azure Arc)                                      │
│ • Enterprise интеграции (Office 365, etc)                       │
│ • Сильный focus на compliance                                   │
│                                                                 │
│ Минусы:                                                         │
│ • Запутанная структура сервисов                                 │
│ • UI менее интуитивный                                          │
│ • Иногда медленнее AWS/GCP                                      │
│                                                                 │
│ Выбирай Azure если:                                             │
│ • Уже используешь Microsoft ecosystem                           │
│ • Enterprise с Windows окружением                               │
│ • Hybrid cloud (on-prem + cloud)                                │
└─────────────────────────────────────────────────────────────────┘

Цены (примерно):
• VM (2 vCPU, 8GB RAM): $50-70/месяц
• Database (managed, 2GB): $15-25/месяц
• Storage (100GB): $2-3/месяц
• Load Balancer: $15-20/месяц
```

---

## Compute: от VMs до Serverless

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPUTE SPECTRUM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IaaS: Virtual Machines                                         │
│  ───────────────────────                                        │
│  AWS: EC2 | GCP: Compute Engine | Azure: VMs                    │
│                                                                 │
│  • Полный контроль над OS                                       │
│  • Управление патчами, security                                 │
│  • Платишь за время работы ($/час)                              │
│                                                                 │
│  Когда: legacy apps, особые требования к OS                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CaaS: Containers                                               │
│  ──────────────────                                             │
│  AWS: ECS, EKS | GCP: GKE | Azure: AKS                          │
│                                                                 │
│  • Оркестрация контейнеров (K8s)                                │
│  • Автоскейлинг, health checks                                  │
│  • Платишь за nodes                                             │
│                                                                 │
│  Когда: микросервисы, cloud-native apps                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PaaS: Managed Application Platform                             │
│  ────────────────────────────────────                           │
│  AWS: Elastic Beanstalk | GCP: App Engine | Azure: App Service │
│                                                                 │
│  • Деплоишь код, инфраструктура управляется                     │
│  • Автоскейлинг, мониторинг из коробки                          │
│  • Платишь за compute + overhead                                │
│                                                                 │
│  Когда: хочешь focus на коде, не на инфраструктуре              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FaaS: Serverless Functions                                     │
│  ────────────────────────────                                   │
│  AWS: Lambda | GCP: Cloud Functions | Azure: Functions         │
│                                                                 │
│  • Запускается только при вызове                                │
│  • Автоматический scale (0 → 1000s)                             │
│  • Платишь за миллисекунды выполнения                           │
│                                                                 │
│  Когда: event-driven, спорадические нагрузки, API endpoints     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Пример расчёта:

VM (24/7):
  $50/месяц фиксированно

Serverless (100K requests/месяц, 500ms каждый):
  Compute: 100,000 * 0.5s * $0.0000166667 = $0.83
  Requests: 100,000 * $0.0000002 = $0.02
  Всего: ~$0.85/месяц

Но: если > 1M requests/месяц → VM может быть дешевле
```

### AWS Lambda Example

```javascript
// handler.js
export const handler = async (event) => {
  // event = HTTP request или event от другого сервиса
  const body = JSON.parse(event.body);

  // Бизнес-логика
  const result = await processOrder(body.orderId);

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(result)
  };
};

// Деплой через Serverless Framework
// serverless.yml
service: order-service

provider:
  name: aws
  runtime: nodejs20.x
  region: us-east-1
  environment:
    DATABASE_URL: ${env:DATABASE_URL}

functions:
  processOrder:
    handler: handler.handler
    events:
      - httpApi:
          path: /orders/{id}
          method: post
    timeout: 30
    memory: 512

# Деплой
npx serverless deploy

# URL: https://abc123.execute-api.us-east-1.amazonaws.com/orders/123
```

---

## Storage: объекты, блоки, файлы

```
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE TYPES                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Object Storage (S3, GCS, Blob Storage)                         │
│  ──────────────────────────────────────                         │
│  • Безлимитный размер                                           │
│  • HTTP API для доступа                                         │
│  • Дешёвый ($0.02/GB/месяц)                                     │
│  • Не может быть mounted как диск                               │
│                                                                 │
│  Для: статика, бэкапы, media, data lakes                        │
│                                                                 │
│  Block Storage (EBS, Persistent Disks, Managed Disks)           │
│  ───────────────────────────────────────────────                │
│  • Как обычный HDD/SSD                                          │
│  • Attach к VM                                                  │
│  • Быстрый (IOPS)                                               │
│  • Дороже ($0.10-0.20/GB/месяц)                                 │
│                                                                 │
│  Для: базы данных, приложения                                   │
│                                                                 │
│  File Storage (EFS, Filestore, Files)                           │
│  ─────────────────────────────────────                          │
│  • NFS, SMB протоколы                                           │
│  • Shared между VMs                                             │
│  • Дороже block storage                                         │
│                                                                 │
│  Для: shared files, legacy apps с file системой                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### S3 Example (AWS)

```javascript
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'us-east-1' });

// Загрузка файла
async function uploadFile(bucket, key, body) {
  await s3.send(new PutObjectCommand({
    Bucket: bucket,
    Key: key,
    Body: body,
    ContentType: 'image/jpeg',
    // Access control
    ACL: 'public-read',  // или 'private'
    // Lifecycle: автоудаление через 30 дней
    Tagging: 'temp=true'
  }));

  // URL: https://bucket.s3.amazonaws.com/key
  return `https://${bucket}.s3.amazonaws.com/${key}`;
}

// Скачивание
async function downloadFile(bucket, key) {
  const response = await s3.send(new GetObjectCommand({
    Bucket: bucket,
    Key: key
  }));

  // response.Body = stream
  return response.Body;
}

// Signed URL (временная ссылка)
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

async function getTemporaryUrl(bucket, key) {
  const command = new GetObjectCommand({ Bucket: bucket, Key: key });
  // URL действителен 1 час
  const url = await getSignedUrl(s3, command, { expiresIn: 3600 });
  return url;
}
```

### S3 Lifecycle Policies

```javascript
// Автоматическое управление данными
// S3 → Lifecycle rules

{
  "Rules": [
    {
      "Id": "Move old files to cheaper storage",
      "Status": "Enabled",
      "Transitions": [
        {
          // Через 30 дней → S3 Infrequent Access (дешевле)
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          // Через 90 дней → Glacier (очень дешёво, медленный доступ)
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        // Через 365 дней → удалить
        "Days": 365
      }
    }
  ]
}

// Цены (примерно):
// S3 Standard:       $0.023/GB
// S3 IA:             $0.0125/GB  (но плата за retrieval)
// S3 Glacier:        $0.004/GB   (медленный доступ)
// S3 Deep Archive:   $0.00099/GB (очень медленный)
```

---

## Databases: Managed Services

```
┌─────────────────────────────────────────────────────────────────┐
│              MANAGED DATABASES (примеры AWS)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RDS (Relational Database Service)                              │
│  ─────────────────────────────────                              │
│  • PostgreSQL, MySQL, MariaDB, Oracle, SQL Server               │
│  • Автобэкапы, патчи, failover                                  │
│  • Read replicas для масштабирования reads                      │
│                                                                 │
│  Aurora (AWS proprietary)                                       │
│  ────────────────────────                                       │
│  • PostgreSQL/MySQL совместимый                                 │
│  • 5x быстрее MySQL, 3x быстрее PostgreSQL                      │
│  • Автоматический scale storage (до 128TB)                      │
│  • Serverless версия (scale to zero)                            │
│                                                                 │
│  DynamoDB (NoSQL)                                               │
│  ─────────────────                                              │
│  • Key-value, document store                                    │
│  • Single-digit millisecond latency                             │
│  • Автоскейлинг, платишь за throughput                          │
│                                                                 │
│  ElastiCache (Redis, Memcached)                                 │
│  ────────────────────────────────                               │
│  • Managed in-memory cache                                      │
│  • Для кэша, сессий, real-time                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Плюсы managed DB:
+ Автобэкапы, point-in-time recovery
+ Автопатчи
+ High availability (multi-AZ)
+ Monitoring из коробки
+ Scale вертикально (bigger instance) и горизонтально (replicas)

Минусы:
- Дороже self-hosted на ~2-3x
- Меньше контроля (нет root access)
- Vendor lock-in

Цена (RDS PostgreSQL, db.t3.medium 2vCPU 4GB):
• $60-80/месяц single-AZ
• $120-160/месяц multi-AZ (HA)
```

---

## Networking: VPC, Load Balancers, CDN

```
┌─────────────────────────────────────────────────────────────────┐
│                  VPC (Virtual Private Cloud)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Internet                                                      │
│      │                                                          │
│      ▼                                                          │
│  ┌────────────────────────────────────────────────┐             │
│  │  VPC (10.0.0.0/16)                             │             │
│  │                                                │             │
│  │  ┌──────────────────┐  ┌──────────────────┐   │             │
│  │  │ Public Subnet    │  │ Private Subnet   │   │             │
│  │  │ 10.0.1.0/24      │  │ 10.0.2.0/24      │   │             │
│  │  │                  │  │                  │   │             │
│  │  │ [Load Balancer]  │  │ [App Servers]    │   │             │
│  │  │ [NAT Gateway]    │  │ [Databases]      │   │             │
│  │  │                  │  │                  │   │             │
│  │  │ Доступ из инета  │  │ Только внутри VPC│   │             │
│  │  └──────────────────┘  └──────────────────┘   │             │
│  │                                                │             │
│  └────────────────────────────────────────────────┘             │
│                                                                 │
│  Security Groups: firewall на уровне instance                   │
│  Network ACLs: firewall на уровне subnet                        │
└─────────────────────────────────────────────────────────────────┘
```

### Load Balancer

```
Application Load Balancer (Layer 7):
• HTTP/HTTPS routing
• Host/path based routing
• WebSocket support

Network Load Balancer (Layer 4):
• TCP/UDP
• Ultra-high performance (millions RPS)
• Static IP

Пример (AWS ALB):
┌──────────┐
│  Client  │
└────┬─────┘
     │ HTTPS
     ▼
┌────────────────┐
│ ALB            │
│ example.com    │
└────┬───────────┘
     │
     ├─▶ /api/*    → Target Group 1 (API servers)
     │
     └─▶ /*        → Target Group 2 (Frontend servers)

Health checks каждые 30s
Automatic failover
```

### CDN (Content Delivery Network)

```
AWS CloudFront | GCP Cloud CDN | Azure CDN

Без CDN:
  User (Tokyo) → Origin Server (US-East) → 200ms latency

С CDN:
  User (Tokyo) → Edge Location (Tokyo) → 20ms latency
                        │
                        ├─ Cache Hit: сразу отдаём
                        └─ Cache Miss: запрос к origin, кэшируем

Настройка CloudFront:
1. Origin: S3 bucket или custom (ALB, EC2)
2. Cache behaviors:
   - *.js, *.css: cache 1 year
   - *.html: cache 1 hour
   - /api/*: no cache
3. HTTPS: автоматический Let's Encrypt cert
4. Цена: $0.085/GB (первые 10TB)
```

---

## Cost Optimization

```
Проблема: Cloud bills растут незаметно

Месяц 1: $100
Месяц 6: $500
Месяц 12: $2000  ← что происходит?!
```

### Типичные причины роста затрат

```
1. Забытые ресурсы
   • Dev/staging environments работают 24/7
   • Orphaned EBS volumes (диски без VM)
   • Old snapshots

2. Over-provisioned resources
   • VM с 16GB RAM, использует 2GB
   • Database с 1000 IOPS, нужно 100

3. Неоптимальный тип инстансов
   • General purpose вместо compute/memory optimized
   • On-demand вместо Reserved/Spot

4. Data transfer costs
   • Cross-region transfers
   • Outbound traffic (egress)
```

### Стратегии оптимизации

```typescript
// 1. Auto-shutdown dev environments
// CloudWatch Events + Lambda
export const handler = async () => {
  const ec2 = new EC2Client({ region: 'us-east-1' });

  // Найти инстансы с тегом Environment=dev
  const instances = await ec2.send(new DescribeInstancesCommand({
    Filters: [
      { Name: 'tag:Environment', Values: ['dev', 'staging'] },
      { Name: 'instance-state-name', Values: ['running'] }
    ]
  }));

  // Остановить в нерабочее время (вечер, выходные)
  const hour = new Date().getHours();
  if (hour > 18 || hour < 8) {
    const instanceIds = instances.map(i => i.InstanceId);
    await ec2.send(new StopInstancesCommand({ InstanceIds: instanceIds }));
  }
};

// Экономия: ~70% (работает только 10 часов вместо 24)

// 2. Reserved Instances для stable workload
// Вместо: on-demand $0.10/час = $73/месяц
// Купить: 1-year reserved = $0.065/час = $47/месяц (35% дешевле)
// 3-year = ещё дешевле

// 3. Spot Instances для fault-tolerant workloads
// Batch jobs, data processing, CI/CD workers
// Цена: до 90% дешевле on-demand
// Но: могут быть прерваны с 2-минутным уведомлением

// 4. S3 Intelligent-Tiering
// Автоматически перемещает редко используемые файлы в дешёвые tiers
{
  "StorageClass": "INTELLIGENT_TIERING"
}

// 5. Monitoring с alerts
// CloudWatch Budget Alert
{
  "Budget": {
    "BudgetName": "MonthlyBudget",
    "BudgetLimit": {
      "Amount": "500",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "Notifications": [
      {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "Subscribers": [
          { "Address": "team@example.com", "SubscriptionType": "EMAIL" }
        ]
      }
    ]
  }
}
```

---

## Подводные камни

### Проблема 1: Vendor Lock-in

```
Сервисы с максимальным lock-in:
• Lambda (AWS-specific API)
• DynamoDB (proprietary NoSQL)
• GCP BigQuery (уникальный SQL dialect)
• Azure Cosmos DB (proprietary APIs)

Миграция = переписать код

Решения:
1. Абстракции
   interface Storage { get, set, delete }
   class S3Storage implements Storage { ... }
   class GCSStorage implements Storage { ... }

2. Open standards
   • Kubernetes → работает везде
   • PostgreSQL → RDS, Cloud SQL, Azure DB
   • Redis → ElastiCache, Memorystore, Azure Cache

3. Multi-cloud (сложно и дорого)
```

### Проблема 2: Latency между регионами

```
Задержки (примерно):
• Same AZ:       <1ms
• Same Region:   2-5ms
• US East <-> US West:  60-80ms
• US <-> Europe: 100-150ms
• US <-> Asia:   180-250ms

Проблема:
  Frontend (US) → API (US) → Database (EU) = 100ms+ на каждый запрос

Решения:
• Всё в одном регионе (trade-off: disaster recovery)
• Репликация БД в нескольких регионах (read replicas)
• CDN для статики
• Edge Functions (CloudFlare Workers, Lambda@Edge)
```

### Проблема 3: Compliance и data residency

```
GDPR: данные EU граждан должны храниться в EU
HIPAA: healthcare данные — особые требования
PCI DSS: payment card data — строгие правила

Нельзя просто "deploy to cloud"
Нужно:
• Выбрать правильный регион
• Включить encryption at rest/in transit
• Audit logging
• Access controls

AWS: Compliance programs
GCP: Compliance offerings
Azure: Trust Center
```

---

## Actionable

**Первые шаги:**
```bash
# AWS CLI setup
aws configure
# Access Key, Secret Key, Region

# Создать VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Создать EC2 instance
aws ec2 run-instances \
  --image-id ami-12345678 \
  --instance-type t3.micro \
  --key-name my-keypair \
  --security-group-ids sg-12345

# Deploy Lambda
npx serverless deploy
```

**Checklist для production:**
```
Infrastructure:
□ Multi-AZ deployment (high availability)
□ Auto-scaling groups
□ Load balancer с health checks
□ VPC с public/private subnets

Data:
□ Managed database (RDS, Aurora)
□ Automated backups (retention ≥ 7 days)
□ Encryption at rest и in transit

Security:
□ Security Groups (least privilege)
□ IAM roles (не использовать root user)
□ Secrets в Parameter Store/Secrets Manager
□ WAF для защиты от attacks

Monitoring:
□ CloudWatch alarms (CPU, memory, disk)
□ Log aggregation (CloudWatch Logs)
□ Billing alerts
□ APM/tracing (X-Ray, OpenTelemetry)

Cost:
□ Right-size instances (не over-provision)
□ Reserved Instances для stable workload
□ Lifecycle policies для S3
□ Auto-shutdown dev/staging
```

## Связи

- IaC для облака: [[infrastructure-as-code]]
- K8s в облаке: [[kubernetes-basics]]
- CI/CD деплой: [[ci-cd-pipelines]]

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | NIST SP 800-145 (2011). *The NIST Definition of Cloud Computing* | Формальное определение cloud computing |
| 2 | Armbrust M. et al. (2010). *A View of Cloud Computing* (Berkeley) | Экономическая модель облаков |
| 3 | [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) | 6 столпов архитектуры |

### Практические руководства

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework) | Docs | GCP patterns |
| 2 | [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) | Docs | Azure patterns |
| 3 | [Cloud Market Share Q1 2025 — Synergy Research](https://www.srgresearch.com/) | Report | Актуальная статистика рынка |
| 4 | [FinOps Foundation](https://www.finops.org/) | Guide | Cloud financial management |
| 5 | [AWS Pricing Calculator](https://calculator.aws/) | Tool | Оценка стоимости |
| 6 | [GCP Pricing Calculator](https://cloud.google.com/products/calculator) | Tool | Оценка стоимости GCP |
| 7 | [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) | Tool | Оценка стоимости Azure |

---

---

## Проверь себя

> [!question]- Почему managed database (RDS, Cloud SQL) стоит в 2-3 раза дороже self-hosted, но всё равно часто выбирают облачный вариант?
> Потому что managed DB снимает с команды ответственность за бэкапы, патчи, failover и мониторинг. Стоимость DevOps-инженера, который поддерживает self-hosted БД 24/7, часто превышает разницу в цене. Кроме того, автоматический Multi-AZ failover за 60-120 секунд сложно реализовать вручную.

> [!question]- В каком сценарии Spot Instances станут проблемой, а не экономией?
> Spot Instances могут быть прерваны с 2-минутным уведомлением. Для stateful сервисов (базы данных, long-running API) это катастрофа — потеря данных или обрыв соединений. Spot подходит только для fault-tolerant задач: batch processing, CI/CD workers, data processing pipelines.

> [!question]- Сравните подходы к vendor lock-in: абстракции в коде vs использование open standards. Какой эффективнее?
> Open standards (Kubernetes, PostgreSQL, Redis) эффективнее, потому что обеспечивают переносимость на уровне технологии, а не на уровне кода. Абстракции (interface Storage) требуют поддержки двух реализаций и тестирования обеих. Open standards работают одинаково на любом провайдере без дополнительного кода.

> [!question]- Почему multi-cloud стратегия "оправдана редко", хотя звучит как хорошая идея для снижения рисков?
> Потому что сложность растёт экспоненциально: нужно поддерживать IaC, мониторинг, security, networking для каждого провайдера. Команде нужна экспертиза в нескольких облаках. Реальный risk mitigation от multi-cloud минимален — AWS region outage случается раз в несколько лет, а operational overhead от multi-cloud — каждый день.

---

## Ключевые карточки

Чем IaaS отличается от PaaS?
?
IaaS (EC2, Compute Engine) — аренда виртуальных машин, ты управляешь OS и приложениями. PaaS (App Engine, Elastic Beanstalk) — деплоишь код, инфраструктура управляется провайдером.

Когда serverless дешевле VM?
?
При спорадической нагрузке: до ~1M запросов/месяц serverless стоит меньше доллара. При постоянной высокой нагрузке VM на reserved instance выгоднее.

Что такое Availability Zone и зачем нужны минимум две?
?
AZ — изолированный датацентр внутри региона. Если один AZ выходит из строя, приложение продолжает работать в другом. Multi-AZ обеспечивает High Availability.

Какие три главные причины роста облачных затрат?
?
1) Забытые ресурсы (dev/staging работают 24/7). 2) Over-provisioned instances (16GB RAM при использовании 2GB). 3) Data transfer costs (egress и cross-region трафик).

В чём главное преимущество GCP перед AWS?
?
Лучший Kubernetes (GKE от создателей K8s), BigQuery для аналитики, Vertex AI для ML. Также более простой UI и цены на 20-30% ниже.

Что такое S3 Lifecycle Policy?
?
Автоматическое перемещение данных между классами хранения по возрасту: Standard -> IA (30 дней) -> Glacier (90 дней) -> удаление (365 дней). Оптимизирует стоимость хранения.

Какой durability у S3 и что это значит?
?
99.999999999% (11 nines). Это означает, что при хранении 10 миллионов объектов можно ожидать потерю одного объекта раз в 10 000 лет.

Что такое shared responsibility model в облаке?
?
Провайдер отвечает за безопасность облака (hardware, сеть, физическая security). Клиент отвечает за безопасность в облаке (данные, IAM, encryption, конфигурация).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cloud-aws-core-services]] | Практические паттерны работы с основными AWS сервисами |
| Следующий шаг | [[cloud-gcp-core-services]] | Сервисы GCP: Compute Engine, BigQuery, Cloud Run |
| Углубиться | [[cloud-serverless-patterns]] | Паттерны serverless: Lambda, event-driven, Step Functions |
| Смежная тема | [[infrastructure-as-code]] | Управление облачной инфраструктурой через код (Terraform, CDK) |
| Смежная тема | [[network-cloud-modern]] | Сетевые технологии в облаке: overlay networks, service mesh |
| Обзор | [[cloud-overview]] | Карта раздела Cloud с навигацией по всем статьям |

---

*Последнее обновление: 2025-12-28*

---

*Проверено: 2026-01-09*
