---
title: "DevOps: Карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: verified
confidence: high
tags:
  - moc
  - devops
  - ci-cd
  - infrastructure
  - operations
related:
  - "[[cloud-overview]]"
  - "[[architecture-overview]]"
  - "[[security-overview]]"
---

# DevOps: Карта раздела

> DevOps — не инструменты, а культура. Автоматизация, collaboration, continuous improvement.

---

## TL;DR

- **DevOps** — practices для сокращения цикла от кода до production
- **Core principles:** Automation, CI/CD, IaC, Monitoring, Collaboration
- **Key metrics:** Deployment frequency, Lead time, MTTR, Change failure rate
- **Культура:** Blameless, shared responsibility, continuous learning

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Как настроить CI/CD? | [[ci-cd-pipelines]] |
| Git workflow? | [[git-workflows]] |
| Docker для разработчика? | [[docker-for-developers]] |
| Kubernetes основы? | [[kubernetes-basics]] |
| Kubernetes advanced? | [[kubernetes-advanced]] |
| GitOps (ArgoCD, Flux)? | [[gitops-argocd-flux]] |
| Infrastructure as Code? | [[infrastructure-as-code]] |
| Monitoring и логи? | [[observability]] |
| Incident management? | [[devops-incident-management]] |

---

## DevOps Culture & Principles

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       DEVOPS PRINCIPLES                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              CULTURE                                        │
│              ┌─────────────────────────────────────┐                       │
│              │   • Collaboration (Dev + Ops)       │                       │
│              │   • Shared responsibility          │                       │
│              │   • Blameless post-mortems         │                       │
│              │   • Continuous learning            │                       │
│              └─────────────────────────────────────┘                       │
│                                │                                            │
│           ┌───────────────────┼───────────────────┐                        │
│           ▼                   ▼                   ▼                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│  │   AUTOMATION    │ │   MEASUREMENT   │ │    SHARING      │              │
│  │                 │ │                 │ │                 │              │
│  │ • CI/CD         │ │ • Metrics       │ │ • Knowledge     │              │
│  │ • IaC           │ │ • Logging       │ │ • Tools         │              │
│  │ • Testing       │ │ • Tracing       │ │ • Practices     │              │
│  │ • Deployments   │ │ • Alerting      │ │ • Runbooks      │              │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘              │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────     │
│                                                                             │
│                         INFINITY LOOP                                       │
│                                                                             │
│       PLAN ──▶ CODE ──▶ BUILD ──▶ TEST                                    │
│         ▲                           │                                       │
│         │                           ▼                                       │
│      MONITOR ◀── OPERATE ◀── DEPLOY ◀── RELEASE                           │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Терминология

| Термин | Значение |
|--------|----------|
| **CI** | Continuous Integration — автоматическая сборка и тесты |
| **CD** | Continuous Delivery/Deployment — автоматический деплой |
| **IaC** | Infrastructure as Code — инфраструктура через код |
| **GitOps** | Git как source of truth для инфраструктуры |
| **SRE** | Site Reliability Engineering — reliability как feature |
| **MTTR** | Mean Time To Recovery — время восстановления |
| **DORA** | DevOps Research and Assessment — метрики эффективности |
| **Toil** | Ручная повторяющаяся работа, которую можно автоматизировать |

---

## DORA Metrics

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         DORA METRICS                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  THROUGHPUT (Velocity)                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Deployment Frequency                    Lead Time for Changes       │   │
│  │  ┌───────────────────────┐              ┌───────────────────────┐   │   │
│  │  │ How often do you      │              │ Time from commit to   │   │   │
│  │  │ deploy to production? │              │ production deployment │   │   │
│  │  │                       │              │                       │   │   │
│  │  │ Elite: Multiple/day   │              │ Elite: < 1 hour       │   │   │
│  │  │ High: Daily-Weekly    │              │ High: < 1 day         │   │   │
│  │  │ Medium: Monthly       │              │ Medium: < 1 week      │   │   │
│  │  │ Low: < Monthly        │              │ Low: > 1 month        │   │   │
│  │  └───────────────────────┘              └───────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  STABILITY (Quality)                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Change Failure Rate                    Time to Restore Service     │   │
│  │  ┌───────────────────────┐              ┌───────────────────────┐   │   │
│  │  │ % of deployments      │              │ Time to recover from  │   │   │
│  │  │ causing failure       │              │ production failure    │   │   │
│  │  │                       │              │                       │   │   │
│  │  │ Elite: 0-15%          │              │ Elite: < 1 hour       │   │   │
│  │  │ High: 16-30%          │              │ High: < 1 day         │   │   │
│  │  │ Medium: 16-30%        │              │ Medium: < 1 week      │   │   │
│  │  │ Low: > 30%            │              │ Low: > 1 week         │   │   │
│  │  └───────────────────────┘              └───────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Key insight: Elite performers have BOTH high throughput AND stability    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Путь обучения

```
УРОВЕНЬ 1: Developer (понимаю DevOps)
└── [[git-workflows]] → [[docker-for-developers]] → [[ci-cd-pipelines]]

УРОВЕНЬ 2: DevOps Practitioner (применяю DevOps)
└── [[kubernetes-basics]] → [[infrastructure-as-code]] → [[observability]]

УРОВЕНЬ 3: DevOps Engineer (проектирую DevOps)
└── [[kubernetes-advanced]] → [[gitops-argocd-flux]] → [[devops-incident-management]]

РЕКОМЕНДУЕМЫЙ ПОРЯДОК:
1. Git workflows (1-2 дня)        ← Основа командной работы
2. Docker (3-5 дней)              ← Контейнеризация
3. CI/CD (2-3 дня)                ← Автоматизация
4. Kubernetes basics (1 неделя)   ← Оркестрация
5. IaC (3-5 дней)                 ← Infrastructure as Code
6. Observability (2-3 дня)        ← Мониторинг
7. Kubernetes advanced (1 неделя) ← Продвинутая оркестрация
8. GitOps (2-3 дня)               ← Modern deployment
```

---

## Структура раздела

### CI/CD & Version Control

| Статья | Описание |
|--------|----------|
| [[ci-cd-pipelines]] | GitHub Actions, Jenkins, build/test/deploy |
| [[git-workflows]] | Git Flow, Trunk-Based Development, branching strategies |
| [[gitops-argocd-flux]] | GitOps principles, ArgoCD, Flux |

### Containers & Orchestration

| Статья | Описание |
|--------|----------|
| [[docker-for-developers]] | Docker internals, Dockerfile best practices |
| [[kubernetes-basics]] | Pods, Services, Deployments, ConfigMaps |
| [[kubernetes-advanced]] | RBAC, Network Policies, Operators, CRDs |

### Infrastructure & Operations

| Статья | Описание |
|--------|----------|
| [[infrastructure-as-code]] | Terraform, CloudFormation, Pulumi |
| [[observability]] | Logging, metrics, tracing (OpenTelemetry) |
| [[devops-incident-management]] | On-call, runbooks, post-mortems |

---

## DevOps Toolchain

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        DEVOPS TOOLCHAIN                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PLAN                  CODE                  BUILD                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │ • Jira       │     │ • VS Code    │     │ • GitHub     │               │
│  │ • Linear     │     │ • Git        │     │   Actions    │               │
│  │ • Notion     │     │ • GitHub     │     │ • Jenkins    │               │
│  │              │     │ • GitLab     │     │ • CircleCI   │               │
│  └──────────────┘     └──────────────┘     └──────────────┘               │
│                                                                             │
│  TEST                  RELEASE               DEPLOY                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │ • Jest       │     │ • Docker     │     │ • ArgoCD     │               │
│  │ • Pytest     │     │ • Harbor     │     │ • Flux       │               │
│  │ • Selenium   │     │ • ECR/GCR    │     │ • Spinnaker  │               │
│  │ • k6         │     │ • Artifactory│     │ • Terraform  │               │
│  └──────────────┘     └──────────────┘     └──────────────┘               │
│                                                                             │
│  OPERATE               MONITOR               FEEDBACK                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │ • Kubernetes │     │ • Prometheus │     │ • PagerDuty  │               │
│  │ • Helm       │     │ • Grafana    │     │ • Opsgenie   │               │
│  │ • Istio      │     │ • Datadog    │     │ • Slack      │               │
│  │ • Vault      │     │ • OpenTel.   │     │ • Statuspage │               │
│  └──────────────┘     └──────────────┘     └──────────────┘               │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Maturity Model

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     DEVOPS MATURITY MODEL                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LEVEL 1: Initial                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  □ Manual deployments                                                │   │
│  │  □ No automated tests                                                │   │
│  │  □ Silos between Dev and Ops                                        │   │
│  │  □ Deployments are stressful events                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  LEVEL 2: Managed                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ☑ CI pipeline (build + unit tests)                                 │   │
│  │  ☑ Basic monitoring                                                 │   │
│  │  □ Some manual steps in deployment                                  │   │
│  │  □ Inconsistent environments                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  LEVEL 3: Defined                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ☑ Full CI/CD pipeline                                              │   │
│  │  ☑ Infrastructure as Code                                           │   │
│  │  ☑ Consistent environments (staging = production)                   │   │
│  │  ☑ Automated testing (unit, integration, e2e)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  LEVEL 4: Measured                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ☑ DORA metrics tracked                                             │   │
│  │  ☑ SLOs defined and monitored                                       │   │
│  │  ☑ Feature flags for safe releases                                  │   │
│  │  ☑ Canary/Blue-green deployments                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  LEVEL 5: Optimized                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ☑ Continuous improvement culture                                   │   │
│  │  ☑ Chaos engineering                                                │   │
│  │  ☑ Developer self-service platform                                  │   │
│  │  ☑ Multiple deploys per day with confidence                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Best Practices Checklist

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    DEVOPS BEST PRACTICES                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VERSION CONTROL                                                           │
│  □ Everything in Git (code, config, IaC)                                  │
│  □ Small, frequent commits                                                │
│  □ Pull requests with code review                                         │
│  □ Branch protection rules                                                │
│                                                                             │
│  CI/CD                                                                     │
│  □ Automated build on every commit                                        │
│  □ Fast feedback (<10 min for basic checks)                              │
│  □ Automated tests (unit, integration)                                    │
│  □ Security scanning (SAST, dependencies)                                 │
│  □ Artifact versioning                                                    │
│                                                                             │
│  DEPLOYMENT                                                                │
│  □ One-click/automated deployments                                        │
│  □ Rollback capability                                                    │
│  □ Blue-green or canary deployments                                       │
│  □ Feature flags for gradual rollouts                                     │
│  □ Same process for all environments                                      │
│                                                                             │
│  INFRASTRUCTURE                                                            │
│  □ Infrastructure as Code (no manual changes)                             │
│  □ Immutable infrastructure                                               │
│  □ Environment parity (dev ≈ staging ≈ prod)                             │
│  □ Secrets management (not in code!)                                      │
│                                                                             │
│  OBSERVABILITY                                                             │
│  □ Centralized logging                                                    │
│  □ Metrics and dashboards                                                 │
│  □ Distributed tracing                                                    │
│  □ Alerting with runbooks                                                 │
│  □ SLIs/SLOs defined                                                      │
│                                                                             │
│  OPERATIONS                                                                │
│  □ On-call rotation                                                       │
│  □ Incident response process                                              │
│  □ Blameless post-mortems                                                 │
│  □ Documented runbooks                                                    │
│  □ Regular disaster recovery tests                                        │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

<details>
<summary>1. Чем DevOps отличается от SRE?</summary>

**Ответ:**

**DevOps:**
- Культура и практики
- Focus: Developer productivity
- Breaking silos between Dev and Ops
- CI/CD, automation, collaboration

**SRE (Site Reliability Engineering):**
- Конкретная реализация DevOps от Google
- Focus: Reliability как feature
- Error budgets, SLOs, toil reduction
- "Software engineering approach to operations"

**Связь:**
- SRE implements DevOps principles
- SRE adds specific practices (error budgets, SLOs)
- DevOps шире, SRE конкретнее

</details>

<details>
<summary>2. Почему "Everything as Code" важен?</summary>

**Ответ:**

**Benefits:**
1. **Version control** — история изменений
2. **Code review** — peer review для инфраструктуры
3. **Reproducibility** — одинаковый результат каждый раз
4. **Documentation** — код = документация
5. **Automation** — нет manual steps
6. **Disaster recovery** — можно восстановить всё из Git

**Что включает:**
- Infrastructure (Terraform)
- Configuration (Ansible, Helm)
- CI/CD pipelines (GitHub Actions)
- Monitoring/Alerting (Terraform + Grafana)
- Security policies (OPA)

</details>

<details>
<summary>3. Как измерить эффективность DevOps?</summary>

**Ответ:**

**DORA Metrics (основные):**

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deploy frequency | Multiple/day | Daily-weekly | Monthly | < Monthly |
| Lead time | < 1 hour | < 1 day | < 1 week | > 1 month |
| MTTR | < 1 hour | < 1 day | < 1 week | > 1 week |
| Change fail rate | 0-15% | 16-30% | 16-30% | > 30% |

**Дополнительные:**
- Build time (< 10 min goal)
- Test coverage
- Deployment success rate
- Mean time to deploy

**Важно:** Measure over time, focus on trends.

</details>

<details>
<summary>4. Что такое "shift left"?</summary>

**Ответ:**

**Shift Left** — перенос активностей на более ранние этапы.

**Традиционно:**
```
Code → Build → Test → Security → Deploy
                        ↑ проблемы находят поздно (дорого)
```

**Shift Left:**
```
Code → Build → Test → Security → Deploy
  ↑ security scanning в CI
  ↑ automated tests с первого коммита
  ↑ linting и static analysis локально
```

**Примеры:**
- **Security:** SAST в CI вместо penetration test перед релизом
- **Testing:** Unit tests пишут разработчики, не QA в конце
- **Quality:** Code review до merge, не после

**Benefit:** Раннее обнаружение = дешевле исправить.

</details>

---

## Связи с другими разделами

- [[cloud-overview]] — Cloud platforms для деплоя
- [[architecture-overview]] — Architecture влияет на deployment
- [[security-overview]] — DevSecOps practices
- [[databases-overview]] — Database operations
- [[programming-overview]] — Code quality practices

---

## Источники

- [DORA State of DevOps Report](https://dora.dev/)
- "The Phoenix Project" by Gene Kim
- "The DevOps Handbook" by Gene Kim, et al.
- [Google SRE Book](https://sre.google/books/)
- [Accelerate](https://itrevolution.com/book/accelerate/) by Nicole Forsgren

---

*Проверено: 2025-12-22*
