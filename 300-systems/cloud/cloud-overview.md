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
  - topic/aws
  - topic/gcp
  - topic/azure
  - type/moc
  - level/beginner
related:
  - "[[cloud-platforms-essentials]]"
  - "[[cloud-aws-core-services]]"
  - "[[cloud-gcp-core-services]]"
  - "[[cloud-serverless-patterns]]"
  - "[[cloud-networking-security]]"
  - "[[cloud-disaster-recovery]]"
reading_time: 6
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Cloud: карта раздела

> Облачные платформы — инфраструктура современных приложений. AWS, GCP, Azure предлагают сотни сервисов, но core концепции одинаковы.

---

## Теоретические основы

> **Cloud Computing** — модель предоставления вычислительных ресурсов (серверы, хранилища, сети, ПО) по запросу через интернет с оплатой по использованию. Формализовано NIST (2011) через 5 обязательных характеристик.

### 5 характеристик облака (NIST SP 800-145)

| Характеристика | Определение |
|----------------|-------------|
| **On-demand self-service** | Потребитель может выделить ресурсы самостоятельно, без участия провайдера |
| **Broad network access** | Доступ через стандартные сетевые механизмы (HTTP, SSH) с любого устройства |
| **Resource pooling** | Ресурсы провайдера обслуживают множество потребителей (multi-tenancy) |
| **Rapid elasticity** | Ресурсы масштабируются быстро и автоматически по спросу |
| **Measured service** | Использование измеряется, контролируется и тарифицируется |

### Три модели обслуживания

| Модель | Что управляет провайдер | Что управляет клиент | Пример |
|--------|------------------------|---------------------|--------|
| **IaaS** | Hardware, networking, hypervisor | OS, middleware, apps, data | EC2, Compute Engine |
| **PaaS** | + OS, middleware, runtime | Apps, data | App Engine, Elastic Beanstalk |
| **SaaS** | Всё | Данные и конфигурация | Gmail, Salesforce |

> **См. также**: [[cloud-platforms-essentials]] — AWS/GCP/Azure, [[os-virtualization]] — основы виртуализации

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

### Теоретические основы
- NIST SP 800-145 (2011). *The NIST Definition of Cloud Computing*. — Формальное определение 5 характеристик, 3 моделей обслуживания, 4 моделей развёртывания
- Armbrust M. et al. (2010). *A View of Cloud Computing* (Berkeley). — Академический взгляд на облачные вычисления

### Практические руководства
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Azure Documentation](https://docs.microsoft.com/azure/)
- Davis C. (2019). *Cloud Native Patterns*. — Паттерны облачных приложений

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего статей | 7 |
| Категорий | 3 |
| Последнее обновление | 2025-12-22 |

---

## Проверь себя

> [!question]- Почему Availability Zone (AZ) — это не просто "ещё один сервер", а архитектурная концепция? Как AZ связана с High Availability?
> AZ — это физически изолированный дата-центр внутри региона с независимым питанием, охлаждением и сетью. Архитектурная суть: размещение приложения в нескольких AZ означает, что выход из строя одного дата-центра (пожар, отключение питания) не останавливает сервис. Это не просто резервная копия — это параллельная работа. Multi-AZ deployment + Load Balancer = автоматический failover без участия человека. Сравните с [[cloud-disaster-recovery]] — Multi-Region идёт ещё дальше, защищая от катастроф на уровне целого региона.

> [!question]- Компания с Windows-стеком и Active Directory выбирает облако. Почему Azure — не единственный вариант, но объективно лучший выбор? Какие аргументы против AWS/GCP?
> Azure интегрирован с Microsoft экосистемой нативно: Azure AD заменяет on-premises AD, Office 365 и Azure работают в единой среде, .NET приложения деплоятся без адаптации. AWS и GCP могут работать с Windows workloads (EC2/Compute Engine поддерживают Windows Server), но интеграция с AD потребует настройки коннекторов, лицензирование Microsoft ПО обойдётся дороже, а hybrid cloud сценарии (Azure Arc) проще реализовать на Azure. Главный аргумент "за" AWS/GCP — если команда уже имеет экспертизу в этих платформах, переход на Azure ради AD может не окупиться.

> [!question]- Reserved instances дают до 72% экономии, spot instances — до 90%. Почему тогда не перевести всё на spot?
> Spot instances облачный провайдер может забрать в любой момент (с уведомлением ~2 минуты), когда ему нужны ресурсы для on-demand клиентов. Это делает их непригодными для stateful-сервисов (БД, очереди) и latency-sensitive приложений. Spot подходит для batch-обработки, CI/CD runners, тренировки ML-моделей — задач, которые можно прервать и перезапустить. Reserved — для стабильной базовой нагрузки (baseline), on-demand — для пиков, spot — для задач, толерантных к прерыванию. Это связано с [[cloud-serverless-patterns]] — serverless решает проблему иначе: платишь только за реальное использование.

> [!question]- Как связаны VPC, Security Groups и IAM? Почему одного из этих механизмов недостаточно для безопасности?
> Это три уровня защиты по принципу defense in depth. VPC — сетевая изоляция (кто вообще может видеть ваши ресурсы). Security Groups — firewall на уровне экземпляра (какой трафик пропускать). IAM — управление доступом на уровне API (кто что может делать с ресурсами). Без VPC — ресурсы в общей сети. Без Security Groups — любой трафик внутри VPC проходит. Без IAM — любой аутентифицированный пользователь может удалить всё. Подробнее в [[cloud-networking-security]].

---

## Ключевые карточки

IaaS, PaaS, SaaS — в чём разница на примере?
?
IaaS (EC2) — аренда пустого сервера, вы ставите всё сами. PaaS (RDS) — готовая платформа, управляете только данными. SaaS (Gmail) — готовый продукт, просто пользуетесь.

Что такое Region и Availability Zone в облаке?
?
Region — географическая локация с несколькими дата-центрами (например, us-east-1). AZ — изолированный дата-центр внутри региона с независимым питанием и сетью. Multi-AZ = высокая доступность.

AWS vs GCP vs Azure — ключевые различия?
?
AWS (~32% рынка) — крупнейший, больше всего сервисов, default выбор. GCP (~10%) — лучший для ML/AI и Kubernetes (GKE). Azure (~23%) — интеграция с Microsoft стеком и hybrid cloud.

Какова durability S3 и что это значит практически?
?
S3 durability — 99.999999999% (11 nines). Это означает, что при хранении 10 миллионов объектов вы статистически потеряете один объект раз в 10,000 лет. Availability при этом 99.99% — ~52 минуты downtime в год.

Lambda cold start — что это и сколько длится?
?
Cold start — задержка при первом вызове Lambda после простоя (загрузка контейнера, инициализация runtime). Длится 100-500ms. Для долгих задач (>15 мин) Lambda не подходит — используйте Step Functions.

Чем отличается Serverless от IaaS?
?
IaaS — вы управляете VM, платите за аренду сервера 24/7. Serverless — код выполняется без управления серверами, платите только за время выполнения. Аналогия: IaaS = аренда машины, Serverless = такси.

Что такое VPC и зачем он нужен?
?
VPC (Virtual Private Cloud) — изолированная виртуальная сеть в облаке. Обеспечивает сетевую изоляцию ресурсов, контроль IP-адресации, маршрутизации и правил доступа. Без VPC ресурсы были бы в общей публичной сети.

Reserved vs On-Demand vs Spot instances?
?
On-Demand — платишь по часам без обязательств. Reserved — commitment на 1-3 года, экономия до 72%. Spot — свободные мощности провайдера, экономия до 90%, но может быть прервано в любой момент.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cloud-platforms-essentials]] | Углубиться в модели облака: IaaS/PaaS/SaaS, ценообразование |
| Углубиться | [[cloud-aws-core-services]] | Практические паттерны работы с EC2, RDS, Lambda, S3 |
| Углубиться | [[cloud-gcp-core-services]] | Сервисы GCP: Compute Engine, BigQuery, Cloud Functions |
| Смежная тема | [[databases-overview]] | Managed databases — ключевой cloud-сервис (RDS, Cloud SQL) |
| Смежная тема | [[devops-overview]] | IaC, CI/CD и деплой в облачной инфраструктуре |
| Смежная тема | [[kubernetes-basics]] | Managed Kubernetes (EKS, GKE, AKS) — оркестрация в облаке |
| Обзор | [[cloud-networking-security]] | VPC, Security Groups, IAM — безопасность облака |

---

*Создано: 2025-12-22*

---

*Проверено: 2026-01-09*
