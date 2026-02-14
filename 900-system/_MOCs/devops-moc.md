---
title: "DevOps MOC"
created: 2025-11-24
modified: 2025-11-24
type: moc
tags:
  - topic/devops
  - type/moc
  - navigation
---

# DevOps MOC

> Контейнеры, CI/CD, инфраструктура

---

## Статьи

### Контейнеры
- [[docker-for-developers]] — От хаоса к порядку. Best practices, ошибки, production checklist

### CI/CD и автоматизация
- [[ci-cd-pipelines]] — GitHub Actions, DevSecOps, Quality Gates. Elite команды деплоят в 973x чаще
- [[git-workflows]] — Trunk-Based vs GitFlow, feature flags, стратегии ветвления

### Infrastructure as Code
- [[infrastructure-as-code]] — Terraform, state management, модули. Инфраструктура как код

### Cloud Platforms
- [[cloud-platforms-essentials]] — AWS vs GCP vs Azure, Serverless, Storage, Cost optimization

### Оркестрация и мониторинг
- [[kubernetes-basics]] — Pods, Deployments, Services. Когда нужен K8s и когда нет
- [[observability]] — Logs + Metrics + Traces. OpenTelemetry как стандарт

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Trunk-Based Development | Короткие ветки, частая интеграция | [[git-workflows]] |
| Feature Flags | Код в main, фича скрыта | [[git-workflows]] |
| Quality Gates | Автоматические проверки качества | [[ci-cd-pipelines]] |
| DevSecOps | Безопасность встроена в pipeline | [[ci-cd-pipelines]] |
| DORA Metrics | Deployment Frequency, Lead Time, MTTR | [[ci-cd-pipelines]] |
| Pod/Deployment/Service | Ключевые абстракции K8s | [[kubernetes-basics]] |
| Health Probes | Liveness, Readiness, Startup | [[kubernetes-basics]] |
| Three Pillars | Logs + Metrics + Traces | [[observability]] |
| OpenTelemetry | Vendor-neutral телеметрия | [[observability]] |
| RED/USE Methods | Метрики для сервисов и ресурсов | [[observability]] |
| Terraform State | Связь кода с реальными ресурсами | [[infrastructure-as-code]] |
| Remote Backend | S3 + DynamoDB для командной работы | [[infrastructure-as-code]] |
| Terraform Modules | Переиспользуемые компоненты IaC | [[infrastructure-as-code]] |
| IaaS vs PaaS vs FaaS | Спектр compute моделей | [[cloud-platforms-essentials]] |
| Serverless | Платишь за миллисекунды | [[cloud-platforms-essentials]] |
| Reserved Instances | 35%+ экономия | [[cloud-platforms-essentials]] |

---

## Связанные темы

- [[microservices-vs-monolith]] — Архитектура для Docker
- [[technical-debt]] — Инфраструктурный долг тоже существует
- [[api-design]] — API для микросервисов

---

## Планируется

- Terraform продвинутые темы (Terragrunt, модули registry)
- Ansible и Configuration Management
- Cloud-native архитектура

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 7 |
| Последнее обновление | 2025-11-24 |

---

*Последнее обновление: 2025-11-24*
