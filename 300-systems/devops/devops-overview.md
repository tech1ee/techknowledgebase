---
title: "DevOps: Карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: published
confidence: high
tags:
  - topic/devops
  - ci-cd
  - infrastructure
  - operations
  - type/moc
  - level/beginner
related:
  - "[[cloud-overview]]"
  - "[[architecture-overview]]"
  - "[[security-overview]]"
reading_time: 11
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Проверь себя

> [!question]- Почему DORA-метрики показывают, что elite-команды имеют одновременно высокий throughput И высокую stability? Разве скорость не противоречит качеству?
> Интуитивно кажется, что быстрые релизы = больше ошибок, но данные DORA опровергают это. Причина: маленькие, частые изменения проще тестировать, проще откатывать и проще дебажить. Деплой 5 строк кода vs 50,000 строк — в первом случае при ошибке сразу понятно, что пошло не так. Автоматизация (CI/CD, automated testing) убирает человеческие ошибки. Feature flags позволяют выкатывать код без активации функциональности. Связь с практикой: это подтверждает принцип "shift left" — чем раньше находишь проблему, тем дешевле её исправить.

> [!question]- Как DevOps Maturity Model связан с реальной инфраструктурой? Что конкретно нужно изменить, чтобы перейти с Level 2 на Level 3?
> Level 2 (Managed): есть CI с unit-тестами и базовый мониторинг, но деплой частично ручной, среды различаются. Для перехода на Level 3 (Defined) нужно: (1) Infrastructure as Code через [[infrastructure-as-code]] — Terraform/Pulumi вместо ручной настройки серверов; (2) полный CI/CD pipeline включая автоматический деплой через [[ci-cd-pipelines]]; (3) environment parity — staging = production (Docker + Kubernetes решают это); (4) расширение тестов: не только unit, но integration и e2e. Ключевое отличие Level 3: любой разработчик может задеплоить в production одной кнопкой, среды идентичны, результат воспроизводим.

> [!question]- Чем GitOps отличается от "просто IaC в Git-репозитории"? Почему GitOps — это не только хранение кода?
> IaC в Git — это хранение Terraform/CloudFormation в репозитории. GitOps идёт дальше: Git — единственный source of truth для desired state кластера. Отличия: (1) pull-модель — агент в кластере (ArgoCD, Flux) сам следит за Git и применяет изменения, вместо push из CI; (2) автоматическая синхронизация — drift detection, если кто-то изменил кластер вручную, GitOps вернёт к состоянию из Git; (3) аудит — каждое изменение = коммит с автором и описанием. Подробнее в [[gitops-argocd-flux]]. Связь с безопасностью: никому не нужен прямой kubectl-доступ к production.

> [!question]- Как observability (метрики, логи, трейсы) связана с incident management? Почему недостаточно просто "настроить алерты"?
> Алерты говорят ЧТО сломалось, но не ПОЧЕМУ. Три столпа observability (см. [[observability]]): метрики показывают аномалию (CPU 100%), логи дают контекст (какой запрос вызвал нагрузку), трейсы показывают путь запроса через микросервисы (где именно задержка). Без трейсов в микросервисной архитектуре инцидент превращается в "угадайку". Incident management (см. [[devops-incident-management]]) строится на этом: runbook ссылается на конкретные дашборды, blameless post-mortem анализирует данные, а не мнения. OpenTelemetry объединяет все три сигнала в единую систему.

> [!question]- Почему "shift left" в безопасности эффективнее penetration testing перед релизом? Как это связано с облачной инфраструктурой?
> Penetration test перед релизом — это поиск проблем в готовом продукте: дорого, долго, блокирует релиз. Shift left security: SAST-сканирование в CI на каждый коммит, проверка зависимостей (Dependabot, Snyk), IaC-сканирование (tfsec, checkov) для [[infrastructure-as-code]]. В облаке (см. [[cloud-overview]]) это критично вдвойне: misconfigured Security Group или публичный S3 bucket обнаруживается автоматически до деплоя, а не после утечки данных. Стоимость исправления бага на этапе кода — 1x, на этапе production — 100x.

---

## Ключевые карточки

Что такое DevOps в одном предложении?
?
DevOps — это культура и набор практик для сокращения цикла от написания кода до production, основанных на автоматизации, collaboration между Dev и Ops, и continuous improvement.

Четыре DORA-метрики?
?
1) Deployment Frequency — как часто деплоите. 2) Lead Time for Changes — время от коммита до production. 3) Change Failure Rate — % деплоев, вызвавших сбой. 4) Time to Restore Service (MTTR) — время восстановления. Elite: multiple/day, <1 hour, 0-15%, <1 hour.

Чем CI отличается от CD?
?
CI (Continuous Integration) — автоматическая сборка и тесты на каждый коммит, быстрая обратная связь. CD — Continuous Delivery (автоматическая подготовка к деплою, ручной trigger) или Continuous Deployment (полностью автоматический деплой в production).

Что такое IaC и зачем он нужен?
?
Infrastructure as Code — описание инфраструктуры кодом (Terraform, Pulumi, CloudFormation). Преимущества: version control, code review, воспроизводимость, автоматизация. Без IaC — ручные изменения, "снежинки" серверов, невозможность точного DR.

Чем DevOps отличается от SRE?
?
DevOps — культура и практики (CI/CD, automation, collaboration). SRE — конкретная реализация от Google: reliability как feature, error budgets, SLOs, toil reduction. SRE реализует принципы DevOps с добавлением формальных метрик надёжности.

Что такое "shift left" в DevOps?
?
Перенос активностей (тестирование, безопасность, quality checks) на более ранние этапы разработки. Вместо penetration test перед релизом — SAST в CI на каждый коммит. Раннее обнаружение = дешевле исправить.

Что такое GitOps?
?
Git как единственный source of truth для desired state инфраструктуры и приложений. Агент (ArgoCD, Flux) в кластере сам синхронизирует состояние с Git. Pull-модель, drift detection, полный аудит через git log.

Пять уровней DevOps Maturity Model?
?
1) Initial — ручные деплои, нет тестов. 2) Managed — CI с unit-тестами. 3) Defined — полный CI/CD, IaC, environment parity. 4) Measured — DORA-метрики, SLOs, canary/blue-green. 5) Optimized — chaos engineering, developer self-service, multiple deploys/day.

Что такое Toil и как с ним бороться?
?
Toil — ручная повторяющаяся работа, которую можно автоматизировать (ручные деплои, ручное масштабирование, ручная ротация сертификатов). SRE подход: измерять toil, автоматизировать его, тратить не более 50% времени на toil.

Infinity loop DevOps — какие фазы?
?
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor → (обратно к Plan). Бесконечный цикл непрерывного улучшения. Каждая фаза автоматизируется.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[git-workflows]] | Основа командной работы: Git Flow, Trunk-Based Development |
| Следующий шаг | [[docker-for-developers]] | Контейнеризация — фундамент современного DevOps |
| Углубиться | [[ci-cd-pipelines]] | GitHub Actions, Jenkins — автоматизация сборки и деплоя |
| Углубиться | [[kubernetes-basics]] | Оркестрация контейнеров: Pods, Services, Deployments |
| Смежная тема | [[cloud-overview]] | Облачные платформы — где деплоятся приложения |
| Смежная тема | [[databases-overview]] | Database operations: бэкапы, миграции, мониторинг в DevOps |
| Смежная тема | [[observability]] | Три столпа: логи, метрики, трейсы (OpenTelemetry) |
| Обзор | [[infrastructure-as-code]] | Terraform, Pulumi — инфраструктура как код |

---

*Проверено: 2025-12-22*
