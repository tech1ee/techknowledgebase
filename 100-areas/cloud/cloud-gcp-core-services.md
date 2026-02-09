---
title: "GCP Core Services: Compute Engine, Cloud SQL, BigQuery"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/cloud
  - gcp
  - bigquery
  - compute-engine
  - cloud-functions
  - type/concept
  - level/intermediate
related:
  - "[[cloud-overview]]"
  - "[[cloud-serverless-patterns]]"
  - "[[cloud-networking-security]]"
---

# GCP Core Services: Compute Engine, Cloud SQL, BigQuery

> GCP — облако от Google. Сильные стороны: Kubernetes (GKE), BigQuery, ML/AI (Vertex AI). Меньше сервисов чем AWS, но более интегрированные.

---

## TL;DR

- **Compute Engine** — виртуальные машины (аналог EC2)
- **Cloud Run** — serverless containers (killer feature)
- **Cloud SQL** — managed PostgreSQL/MySQL
- **BigQuery** — serverless data warehouse, лучший в индустрии
- **GKE** — Kubernetes от создателей K8s

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Project** | Контейнер для ресурсов (аналог AWS Account) |
| **Region/Zone** | Локация: us-central1-a, europe-west1-b |
| **Service Account** | IAM identity для сервисов (аналог IAM Role) |
| **gcloud** | CLI для GCP |
| **Cloud Console** | Web UI для управления |
| **Preemptible VM** | Spot instance в GCP (до 80% дешевле) |

---

## GCP vs AWS: ключевые различия

```
┌─────────────────────────────────────────────────────────────────┐
│                    GCP vs AWS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  СТРУКТУРА                                                      │
│  AWS: Account → Region → VPC → Resources                       │
│  GCP: Organization → Folder → Project → Resources              │
│                                                                 │
│  NETWORKING                                                     │
│  AWS: VPC per region, need peering                             │
│  GCP: Global VPC, subnets per region                           │
│                                                                 │
│  IAM                                                            │
│  AWS: Policies attached to users/roles                         │
│  GCP: Roles granted on resources (project/folder/org level)   │
│                                                                 │
│  KILLER FEATURES                                                │
│  AWS: Breadth of services, enterprise adoption                 │
│  GCP: BigQuery, GKE, global networking, ML/AI                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Compute Engine

### Machine Types

| Family | Use Case | Example |
|--------|----------|---------|
| **E2** | Cost-optimized, general | e2-medium (2 vCPU, 4GB) |
| **N2/N2D** | Balanced | n2-standard-4 (4 vCPU, 16GB) |
| **C2/C2D** | Compute-optimized | c2-standard-4 |
| **M2/M3** | Memory-optimized | m2-ultramem-208 |
| **A2** | GPU (NVIDIA A100) | a2-highgpu-1g |
| **T2A/T2D** | ARM (Tau) | t2a-standard-1 |

### Практические команды

```bash
# Авторизация
gcloud auth login
gcloud config set project my-project

# Создать VM
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud

# SSH
gcloud compute ssh my-vm --zone=us-central1-a

# Список instances
gcloud compute instances list

# Остановить/запустить
gcloud compute instances stop my-vm --zone=us-central1-a
gcloud compute instances start my-vm --zone=us-central1-a

# Preemptible (spot)
gcloud compute instances create spot-vm \
  --preemptible \
  --zone=us-central1-a \
  --machine-type=e2-medium
```

---

## Cloud Run: Serverless Containers

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLOUD RUN                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Docker Container → Cloud Run → HTTPS Endpoint                 │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ Dockerfile  │ ──▶ │ Container   │ ──▶ │   Cloud     │       │
│  │             │     │ Registry    │     │    Run      │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                 │               │
│                                                 ▼               │
│                                        https://my-service-xxx   │
│                                        .run.app                 │
│                                                                 │
│  Преимущества:                                                 │
│  • Любой язык/framework (контейнер)                            │
│  • Scale to zero (платишь за использование)                   │
│  • Автоматический HTTPS                                        │
│  • Concurrency: до 1000 req/instance                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Deploy в Cloud Run

```bash
# Из исходников (Cloud Build)
gcloud run deploy my-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Из Docker image
gcloud run deploy my-service \
  --image gcr.io/my-project/my-image:latest \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --allow-unauthenticated

# Traffic splitting (canary)
gcloud run services update-traffic my-service \
  --to-revisions=my-service-v2=10 \
  --region us-central1
```

---

## Cloud SQL

### Создание

```bash
# PostgreSQL instance
gcloud sql instances create my-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=secure-password

# Создать БД
gcloud sql databases create mydb --instance=my-postgres

# Создать пользователя
gcloud sql users create appuser \
  --instance=my-postgres \
  --password=app-password

# Подключение через Cloud SQL Proxy
cloud-sql-proxy my-project:us-central1:my-postgres &
psql "host=127.0.0.1 port=5432 user=appuser dbname=mydb"
```

### High Availability

```bash
# HA configuration
gcloud sql instances create my-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-2 \
  --region=us-central1 \
  --availability-type=REGIONAL  # Multi-zone HA

# Read replica
gcloud sql instances create my-replica \
  --master-instance-name=my-postgres \
  --region=us-central1
```

---

## BigQuery: Serverless Data Warehouse

```
┌─────────────────────────────────────────────────────────────────┐
│                      BIGQUERY                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Serverless: no infra to manage                              │
│  • Petabyte scale                                              │
│  • SQL interface (Standard SQL)                                │
│  • Columnar storage                                            │
│  • Платишь за: storage ($0.02/GB) + queries ($5/TB scanned)   │
│                                                                 │
│  USE CASES:                                                     │
│  • Analytics / BI                                              │
│  • Data warehousing                                            │
│  • ML training (BigQuery ML)                                   │
│  • Log analysis                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Примеры запросов

```sql
-- Создать dataset и таблицу
CREATE SCHEMA my_dataset;

CREATE TABLE my_dataset.events (
  event_id STRING,
  user_id STRING,
  event_type STRING,
  timestamp TIMESTAMP,
  properties JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY user_id;

-- Загрузить данные из Cloud Storage
LOAD DATA INTO my_dataset.events
FROM FILES (
  format = 'PARQUET',
  uris = ['gs://my-bucket/events/*.parquet']
);

-- Аналитика
SELECT
  DATE(timestamp) as date,
  event_type,
  COUNT(*) as count,
  COUNT(DISTINCT user_id) as unique_users
FROM my_dataset.events
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date, event_type
ORDER BY date DESC, count DESC;

-- BigQuery ML: train model
CREATE OR REPLACE MODEL my_dataset.churn_model
OPTIONS(model_type='LOGISTIC_REG') AS
SELECT
  * EXCEPT(churned),
  churned as label
FROM my_dataset.user_features;
```

### Оптимизация стоимости

```sql
-- Проверить сколько данных будет прочитано
-- (dry run в консоли или bq --dry_run)

-- ✅ Partitioning: фильтруй по partition column
SELECT * FROM events
WHERE DATE(timestamp) = '2025-01-15';  -- сканирует только 1 partition

-- ✅ Clustering: колонки часто в WHERE/JOIN
CREATE TABLE events (...)
CLUSTER BY user_id, event_type;

-- ✅ SELECT только нужные колонки
SELECT user_id, event_type FROM events;  -- дешевле чем SELECT *

-- ✅ Materialized views для частых запросов
CREATE MATERIALIZED VIEW my_dataset.daily_stats AS
SELECT DATE(timestamp) as date, COUNT(*) as events
FROM my_dataset.events
GROUP BY date;
```

---

## Cloud Functions

```python
# main.py - HTTP function
import functions_framework

@functions_framework.http
def hello(request):
    name = request.args.get('name', 'World')
    return f'Hello, {name}!'

# Cloud event function (Pub/Sub trigger)
@functions_framework.cloud_event
def process_pubsub(cloud_event):
    import base64
    data = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    print(f"Received: {data}")
```

```bash
# Deploy HTTP function
gcloud functions deploy hello \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=hello \
  --trigger-http \
  --allow-unauthenticated

# Deploy Pub/Sub trigger
gcloud functions deploy process-events \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_pubsub \
  --trigger-topic=my-topic
```

---

## GKE: Google Kubernetes Engine

```bash
# Создать cluster
gcloud container clusters create my-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10

# Получить credentials
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Теперь kubectl работает
kubectl get nodes
kubectl apply -f deployment.yaml

# Autopilot (serverless K8s)
gcloud container clusters create-auto my-autopilot \
  --region us-central1
```

---

## Проверь себя

<details>
<summary>1. Чем Cloud Run отличается от Cloud Functions?</summary>

**Ответ:**
- **Cloud Functions:** Одна функция, event-driven, ограничения на runtime
- **Cloud Run:** Любой контейнер, полный контроль, больше flexibility

Cloud Run лучше для: web apps, APIs, микросервисы.
Cloud Functions лучше для: простые triggers, webhooks.

</details>

<details>
<summary>2. Почему BigQuery хорош для analytics?</summary>

**Ответ:**
- **Serverless:** Не нужно управлять инфраструктурой
- **Scale:** Петабайты данных, секунды на запрос
- **Columnar:** Эффективно для аналитических запросов
- **SQL:** Стандартный интерфейс, легко начать
- **Integrations:** Data Studio, Looker, ML

Pay-per-query модель: платишь только за прочитанные данные.

</details>

<details>
<summary>3. Что такое GKE Autopilot?</summary>

**Ответ:** Serverless Kubernetes — Google управляет nodes:
- Не нужно выбирать машины
- Автоматический scaling
- Платишь за pods, не за nodes
- Встроенные security best practices

Trade-off: меньше контроля, но проще в управлении.

</details>

<details>
<summary>4. Как GCP VPC отличается от AWS VPC?</summary>

**Ответ:**
- **GCP:** Глобальный VPC, subnets в регионах
- **AWS:** VPC per region, нужен peering

GCP проще для multi-region: один VPC, subnets везде.
AWS более изолированный по умолчанию.

</details>

---

## Связи

- [[cloud-overview]] — карта раздела
- [[cloud-aws-core-services]] — сравнение с AWS
- [[cloud-serverless-patterns]] — serverless архитектура
- [[kubernetes-basics]] — Kubernetes в GKE

---

## Источники

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

*Проверено: 2025-12-22*
