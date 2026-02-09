---
title: "Cloud MOC"
created: 2025-11-24
modified: 2025-12-18
type: moc
tags:
  - moc
  - cloud
---

# Cloud MOC

> AWS, GCP, Azure, Serverless — выбор compute модели и оптимизация затрат

---

## Быстрая навигация

- **Новичок?** → Начни с [[cloud-platforms-essentials]] — базовые концепции
- **Выбираешь compute модель?** → Раздел "Как выбрать: IaaS vs PaaS vs FaaS" ниже
- **Оптимизируешь затраты?** → Раздел "Стратегии экономии"
- **Деплоишь приложение?** → [[ci-cd-pipelines]], [[infrastructure-as-code]]

---

## Статьи

### Cloud Platforms
- [[cloud-platforms-essentials]] — AWS vs GCP vs Azure, Compute, Storage, Databases, Networking, Cost optimization

---

## Как выбрать: IaaS vs PaaS vs FaaS

**Почему это важно:** Неправильный выбор модели → либо переплата за неиспользуемые ресурсы, либо ограничения масштабируемости. По данным Gartner, расходы на PaaS достигнут $208.6 млрд в 2025 году (+21.6% год к году).

### Decision Tree

```
Нужен полный контроль над инфраструктурой?
├── ДА → У вас есть DevOps команда для управления?
│         ├── ДА → IaaS (EC2, Compute Engine, Azure VMs)
│         └── НЕТ → Рассмотрите PaaS или managed services
│
└── НЕТ → Какой тип нагрузки?
          ├── Веб-приложение (постоянно работает) → PaaS (App Service, Cloud Run, Heroku)
          ├── Event-driven (спорадические вызовы) → FaaS (Lambda, Cloud Functions)
          └── Контейнеры с оркестрацией → Managed K8s (EKS, GKE, AKS)
```

### Сравнение моделей

| Критерий | IaaS | PaaS | FaaS |
|----------|------|------|------|
| **Контроль** | Максимальный (OS, runtime) | Средний (только код + config) | Минимальный (только код) |
| **Управление** | Вы управляете VMs, сетью | Провайдер управляет платформой | Провайдер управляет всем |
| **Масштабирование** | Ручное или auto-scaling groups | Managed auto-scaling | Автоматическое (до 0) |
| **Биллинг** | За VM/час независимо от нагрузки | За ресурсы платформы | За вызов функции (мс) |
| **Cold start** | Нет | Минимальный | Есть (100ms-10s) |
| **Примеры** | EC2, GCE, Azure VMs | App Service, Cloud Run | Lambda, Cloud Functions |

### Когда что выбирать

**IaaS выбирай когда:**
- Нужен полный контроль над OS и middleware
- Есть compliance требования (PCI-DSS, HIPAA) требующие специфичной конфигурации
- Мигрируешь legacy приложение "как есть" (lift-and-shift)
- У тебя сильная DevOps команда

**PaaS выбирай когда:**
- Фокус на разработке, не на инфраструктуре
- Стартап или небольшая команда без выделенного DevOps
- Нужен быстрый time-to-market
- Стандартные веб-приложения (API, веб-сайты)

**FaaS выбирай когда:**
- Event-driven нагрузка (обработка файлов, webhooks, IoT)
- Непредсказуемый или спорадический трафик
- Микросервисы с независимым масштабированием
- Хочешь платить только за фактическое использование

**Когда НЕ использовать FaaS:**
- Stateful приложения (функции должны быть stateless)
- Long-running процессы (лимит 15 минут у Lambda)
- Критичны низкие latency (cold start проблема)

---

## Ключевые концепции

| Концепция | Суть | Когда важно | Подробнее |
|-----------|------|-------------|-----------|
| **IaaS vs PaaS vs FaaS** | Спектр compute моделей | При выборе архитектуры | См. decision tree выше |
| **Serverless** | Платишь за миллисекунды, масштабирование до 0 | Event-driven нагрузки | [[cloud-platforms-essentials]] |
| **S3 Lifecycle** | Автоперемещение в дешёвые tiers (Standard→IA→Glacier) | Долгосрочное хранение | [[cloud-platforms-essentials]] |
| **VPC** | Виртуальная приватная сеть, изоляция ресурсов | Любой production deployment | [[cloud-platforms-essentials]] |
| **Reserved Instances** | 35-72% экономия при commitment на 1-3 года | Stable workload | [[cloud-platforms-essentials]] |
| **CDN** | Edge locations для низкой latency | Статика, глобальные пользователи | [[cloud-platforms-essentials]] |

---

## Стратегии экономии

| Стратегия | Экономия | Применимость |
|-----------|----------|--------------|
| **Reserved Instances** | 35-72% | Predictable workloads |
| **Spot/Preemptible** | 60-90% | Batch jobs, CI/CD, dev environments |
| **Right-sizing** | 20-40% | Любые workloads (анализ utilization) |
| **S3 Lifecycle** | 50-90% | Архивные данные |
| **Auto-scaling** | 10-30% | Variable traffic |

**87% enterprise компаний** используют multi-cloud (Flexera 2024), комбинируя сильные стороны разных провайдеров.

---

## Связанные темы

- [[infrastructure-as-code]] — Terraform/Pulumi для облачной инфраструктуры как кода
- [[kubernetes-basics]] — K8s в облаке (EKS, GKE, AKS) — когда managed K8s лучше FaaS
- [[ci-cd-pipelines]] — Автоматизация деплоя в облако
- [[microservices-vs-monolith]] — Архитектурные решения влияющие на выбор compute модели

---

## Планируется

- Multi-cloud strategies — когда и как использовать несколько провайдеров
- Cloud Security & Compliance — IAM, encryption, compliance frameworks
- FinOps & Cost Management — практики оптимизации облачных затрат

---

## Источники

- [IaaS, PaaS, SaaS: What's the Difference? - IBM](https://www.ibm.com/think/topics/iaas-paas-saas) — официальное объяснение от IBM
- [Choose an Azure Compute Service - Microsoft](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree) — decision tree от Microsoft
- [SaaS vs PaaS vs IaaS - AWS](https://aws.amazon.com/types-of-cloud-computing/) — официальная документация AWS
- [PaaS vs IaaS vs SaaS - Google Cloud](https://cloud.google.com/learn/paas-vs-iaas-vs-saas) — сравнение от Google
- [Cloud Service Models - DataCamp](https://www.datacamp.com/blog/cloud-service-models) — практическое руководство
- [IaaS vs PaaS vs SaaS vs FaaS - Brainhub](https://brainhub.eu/library/cloud-architecture-saas-faas-xaas) — детальное сравнение всех моделей

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 1 |
| Последнее обновление | 2025-12-18 |

---

*Проверено: 2025-12-18 | На основе официальной документации AWS, Azure, GCP*
