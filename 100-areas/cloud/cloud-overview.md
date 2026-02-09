---
title: "Cloud: карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: published
area: cloud
confidence: high
tags:
  - topic/cloud
  - aws
  - gcp
  - azure
  - type/moc
  - level/beginner
related:
  - "[[cloud-platforms-essentials]]"
  - "[[cloud-aws-core-services]]"
  - "[[cloud-gcp-core-services]]"
  - "[[cloud-serverless-patterns]]"
  - "[[cloud-networking-security]]"
  - "[[cloud-disaster-recovery]]"
---

# Cloud: карта раздела

> Облачные платформы — инфраструктура современных приложений. AWS, GCP, Azure предлагают сотни сервисов, но core концепции одинаковы.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовый Linux** | Облачные VM работают на Linux | Любой курс по Linux |
| **Networking** | VPC, IP, порты, балансировщики | [[networking-overview]] |
| **Что такое БД** | Managed databases — ключевой сервис | [[databases-overview]] |

### Терминология для новичков

> 💡 **Облако** = чужие компьютеры, которые ты арендуешь через интернет

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **IaaS** | Infrastructure as a Service (VM, сети) | **Аренда пустого офиса** — ты ставишь мебель |
| **PaaS** | Platform as a Service (managed DB, etc) | **Коворкинг** — мебель и Wi-Fi уже есть |
| **SaaS** | Software as a Service (Gmail, Slack) | **Готовый сервис** — просто пользуйся |
| **Serverless** | Код без управления серверами | **Такси** — платишь за поездку, не за машину |
| **Region** | Географический дата-центр | **Город** — Франкфурт, Сингапур |
| **AZ** | Availability Zone — независимый дата-центр | **Район города** — один сгорел, другие работают |

---

## TL;DR

- **IaaS** — виртуальные машины, сети, storage (EC2, Compute Engine)
- **PaaS** — managed services: БД, очереди, кэш (RDS, Cloud SQL)
- **Serverless** — функции без серверов (Lambda, Cloud Functions)
- **Выбор провайдера:** AWS для enterprise, GCP для ML/analytics, Azure для Microsoft стека

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Основы облачных моделей? | [[cloud-platforms-essentials]] |
| AWS сервисы для разработчика? | [[cloud-aws-core-services]] |
| GCP сервисы для разработчика? | [[cloud-gcp-core-services]] |
| Serverless архитектура? | [[cloud-serverless-patterns]] |
| VPC, Security Groups, IAM? | [[cloud-networking-security]] |
| Disaster Recovery в облаке? | [[cloud-disaster-recovery]] |

---

## Путь обучения

```
                    ┌─────────────────────────┐
                    │   Cloud Fundamentals    │
                    │   (IaaS, PaaS, SaaS,    │
                    │    модели ценообразов.) │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │   Compute       │ │   Storage     │ │   Networking  │
    │   (EC2, Lambda, │ │   (S3, EBS,   │ │   (VPC, ALB,  │
    │   ECS, EKS)     │ │   CloudFront) │ │   Route53)    │
    └─────────┬───────┘ └───────┬───────┘ └───────┬───────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   Managed Services      │
                    │   (RDS, ElastiCache,    │
                    │    SQS, SNS, etc.)      │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │   Security      │ │   Serverless  │ │   DR & HA     │
    │   (IAM, KMS,    │ │   (Lambda,    │ │   (Multi-AZ,  │
    │   Security Grp) │ │   API Gateway)│ │   Multi-Region│
    └─────────────────┘ └───────────────┘ └───────────────┘
```

---

## Статьи по категориям

### Фундамент

| Статья | Описание | Связи |
|--------|----------|-------|
| [[cloud-platforms-essentials]] | IaaS/PaaS/SaaS, сравнение провайдеров, модели стоимости | → все статьи |

### Провайдеры

| Статья | Описание | Связи |
|--------|----------|-------|
| [[cloud-aws-core-services]] | EC2, RDS, Lambda, S3, IAM — практические паттерны | → serverless |
| [[cloud-gcp-core-services]] | Compute Engine, Cloud SQL, Cloud Functions, BigQuery | → serverless |

### Архитектура

| Статья | Описание | Связи |
|--------|----------|-------|
| [[cloud-serverless-patterns]] | Lambda, event-driven, Step Functions, cold starts | → architecture |
| [[cloud-networking-security]] | VPC, Security Groups, IAM policies, Zero Trust | → security |
| [[cloud-disaster-recovery]] | Multi-AZ, Multi-Region, RTO/RPO, failover | → databases |

---

## AWS vs GCP vs Azure

```
┌─────────────────────────────────────────────────────────────────┐
│                СРАВНЕНИЕ ПРОВАЙДЕРОВ                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AWS (Amazon Web Services)                                      │
│  • Крупнейший: ~32% рынка                                      │
│  • Больше всего сервисов (200+)                                │
│  • Лучшая документация и community                             │
│  • Enterprise-ready                                            │
│  • Use case: любой, default выбор                              │
│                                                                 │
│  GCP (Google Cloud Platform)                                    │
│  • ~10% рынка                                                  │
│  • Лучший для ML/AI (Vertex AI, TPU)                          │
│  • BigQuery — лучший data warehouse                           │
│  • Kubernetes native (GKE от создателей K8s)                  │
│  • Use case: analytics, ML, Kubernetes                         │
│                                                                 │
│  Azure (Microsoft)                                              │
│  • ~23% рынка                                                  │
│  • Интеграция с Microsoft (AD, Office 365)                    │
│  • Hybrid cloud (Azure Arc)                                    │
│  • Enterprise с Windows стеком                                 │
│  • Use case: Microsoft shops, enterprise                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Соответствие сервисов

| Категория | AWS | GCP | Azure |
|-----------|-----|-----|-------|
| **Compute** | EC2 | Compute Engine | Virtual Machines |
| **Containers** | ECS, EKS | Cloud Run, GKE | AKS, Container Apps |
| **Serverless** | Lambda | Cloud Functions | Azure Functions |
| **Object Storage** | S3 | Cloud Storage | Blob Storage |
| **SQL DB** | RDS | Cloud SQL | Azure SQL |
| **NoSQL** | DynamoDB | Firestore | Cosmos DB |
| **Caching** | ElastiCache | Memorystore | Azure Cache |
| **Queue** | SQS | Pub/Sub | Service Bus |
| **CDN** | CloudFront | Cloud CDN | Azure CDN |
| **DNS** | Route 53 | Cloud DNS | Azure DNS |
| **IAM** | IAM | Cloud IAM | Azure AD |
| **Secrets** | Secrets Manager | Secret Manager | Key Vault |
| **Monitoring** | CloudWatch | Cloud Monitoring | Azure Monitor |

---

## Ключевые концепции

| Концепция | Что это | Почему важно |
|-----------|---------|--------------|
| **Region** | Географическая локация (us-east-1) | Latency, compliance, DR |
| **Availability Zone (AZ)** | Изолированный датацентр в регионе | High Availability |
| **VPC** | Virtual Private Cloud — изолированная сеть | Security, network isolation |
| **IAM** | Identity and Access Management | Who can do what |
| **Security Group** | Firewall на уровне instance | Ingress/egress control |
| **Auto Scaling** | Автоматическое масштабирование | Cost optimization, HA |
| **Load Balancer** | Распределение трафика | HA, scaling |

---

## Числа, которые нужно знать

| Метрика | Значение | Контекст |
|---------|----------|----------|
| Lambda cold start | 100-500ms | Первый вызов после простоя |
| Lambda timeout | 15 min max | Для долгих задач — Step Functions |
| S3 durability | 99.999999999% | "11 nines" — практически не теряет |
| S3 availability | 99.99% | 52 минуты downtime в год |
| RDS Multi-AZ failover | 60-120 sec | Автоматический при сбое |
| Cross-region latency | 50-150ms | Для DR и geo-distribution |
| Reserved vs On-Demand | до 72% экономии | 1-3 года commitment |
| Spot instances | до 90% экономии | Может быть прерван |

---

## Связи с другими разделами

- [[databases-overview]] — managed databases (RDS, Cloud SQL)
- [[devops-overview]] — IaC, CI/CD в облаке
- [[security-overview]] — cloud security, IAM
- [[architecture-overview]] — cloud-native архитектура
- [[kubernetes-basics]] — managed Kubernetes (EKS, GKE)

---

## Инструменты

### Infrastructure as Code
- **Terraform** — multi-cloud IaC
- **AWS CDK** — IaC на TypeScript/Python
- **Pulumi** — IaC на общих языках

### CLI
- **AWS CLI** — aws s3 cp, aws ec2 describe-instances
- **gcloud CLI** — gcloud compute instances list
- **Azure CLI** — az vm list

### Стоимость
- **AWS Cost Explorer** — анализ затрат
- **Infracost** — cost estimation для Terraform
- **Spot.io** — оптимизация spot instances

---

## Источники

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Azure Documentation](https://docs.microsoft.com/azure/)
- "Cloud Native Patterns" by Cornelia Davis

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего статей | 7 |
| Категорий | 3 |
| Последнее обновление | 2025-12-22 |

---

*Создано: 2025-12-22*

---

*Проверено: 2026-01-09*
