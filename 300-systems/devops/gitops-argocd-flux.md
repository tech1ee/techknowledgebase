---
title: "GitOps: ArgoCD, Flux, Declarative Deployments"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/devops
  - gitops
  - argocd
  - flux
  - topic/kubernetes
  - type/concept
  - level/intermediate
related:
  - "[[devops-overview]]"
  - "[[kubernetes-basics]]"
  - "[[ci-cd-pipelines]]"
prerequisites:
  - "[[kubernetes-basics]]"
  - "[[ci-cd-pipelines]]"
  - "[[git-workflows]]"
reading_time: 14
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# GitOps: ArgoCD, Flux, Declarative Deployments

> GitOps: Git как single source of truth для инфраструктуры и приложений. Push to Git = Deploy.

---

## TL;DR

- **GitOps** — Git является единственным источником правды для desired state
- **Pull-based** — operator в кластере сам sync'ает с Git (не CI push'ит)
- **ArgoCD** — популярный GitOps controller с UI
- **Flux** — CNCF GitOps toolkit, более модульный

---

## Терминология

| Термин | Значение |
|--------|----------|
| **GitOps** | Git как source of truth для infrastructure |
| **Desired State** | Что должно быть (в Git) |
| **Actual State** | Что есть сейчас (в кластере) |
| **Reconciliation** | Приведение actual к desired |
| **Drift** | Расхождение actual от desired |
| **Sync** | Процесс reconciliation |
| **Application** | ArgoCD ресурс, описывающий что деплоить |
| **Kustomization** | Flux ресурс для кастомизации манифестов |

---

## GitOps vs Traditional CI/CD

```
┌────────────────────────────────────────────────────────────────────────────┐
│                  TRADITIONAL CI/CD (Push-based)                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Developer ──▶ Git Push ──▶ CI Pipeline ──▶ kubectl apply ──▶ Cluster    │
│                                                   │                         │
│                                           credentials in CI                │
│                                           imperative commands              │
│                                                                             │
│   Problems:                                                                │
│   • CI needs cluster credentials (security risk)                          │
│   • No drift detection (manual changes not tracked)                       │
│   • Hard to audit who changed what                                        │
│   • Rollback = re-run old pipeline                                        │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                     GITOPS (Pull-based)                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Developer ──▶ Git Push ──▶ Git Repository                                │
│                                     │                                       │
│                                     │ watched by                           │
│                                     ▼                                       │
│                            ┌─────────────────┐                             │
│                            │  GitOps Agent   │ (ArgoCD/Flux)               │
│                            │  (in cluster)   │                             │
│                            └────────┬────────┘                             │
│                                     │                                       │
│                                     │ reconcile                            │
│                                     ▼                                       │
│                            ┌─────────────────┐                             │
│                            │    Cluster      │                             │
│                            └─────────────────┘                             │
│                                                                             │
│   Benefits:                                                                │
│   • No external credentials needed                                        │
│   • Continuous drift detection                                            │
│   • Full audit trail in Git                                               │
│   • Rollback = git revert                                                 │
│   • Declarative, reproducible                                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## GitOps Principles

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      GITOPS PRINCIPLES                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DECLARATIVE                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  System described declaratively (YAML, not scripts)                 │   │
│  │                                                                      │   │
│  │  ❌ kubectl run nginx --image=nginx --replicas=3                    │   │
│  │  ✅ Deployment YAML in Git                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. VERSIONED AND IMMUTABLE                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Desired state stored in Git (versioned, auditable)                 │   │
│  │                                                                      │   │
│  │  • Every change = Git commit                                        │   │
│  │  • Full history preserved                                           │   │
│  │  • Immutable releases (tags)                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. PULLED AUTOMATICALLY                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Agents PULL changes from Git (not CI pushing)                      │   │
│  │                                                                      │   │
│  │  • Agent runs inside cluster                                        │   │
│  │  • Continuously watches Git                                         │   │
│  │  • No external access needed                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. CONTINUOUSLY RECONCILED                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Agents ensure actual state matches desired state                   │   │
│  │                                                                      │   │
│  │  • Detect drift automatically                                       │   │
│  │  • Self-healing (revert manual changes)                            │   │
│  │  • Alert on persistent drift                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## ArgoCD

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       ARGOCD ARCHITECTURE                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ARGOCD COMPONENTS                           │   │
│  │                                                                      │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │   │
│  │  │ API Server  │   │   Repo      │   │Application  │               │   │
│  │  │             │   │   Server    │   │ Controller  │               │   │
│  │  │ • REST API  │   │             │   │             │               │   │
│  │  │ • UI        │   │ • Git clone │   │ • Reconcile │               │   │
│  │  │ • gRPC      │   │ • Helm      │   │ • Sync      │               │   │
│  │  │ • Auth      │   │ • Kustomize │   │ • Health    │               │   │
│  │  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘               │   │
│  │         │                 │                 │                       │   │
│  │         └─────────────────┼─────────────────┘                       │   │
│  │                           │                                         │   │
│  │                           ▼                                         │   │
│  │                    ┌─────────────┐                                  │   │
│  │                    │    Redis    │ (cache)                         │   │
│  │                    └─────────────┘                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                    ┌─────────────┐                                         │
│                    │ Git Repo    │                                         │
│                    │ (manifests) │                                         │
│                    └─────────────┘                                         │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### ArgoCD Application

```yaml
# ✅ ArgoCD Application resource
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/k8s-manifests.git
    targetRevision: main
    path: apps/my-app/overlays/production

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true        # Delete resources not in Git
      selfHeal: true     # Revert manual changes
      allowEmpty: false  # Don't sync empty dirs
    syncOptions:
    - CreateNamespace=true
    - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

---
# ✅ Helm-based Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: prometheus
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://prometheus-community.github.io/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 45.0.0
    helm:
      values: |
        grafana:
          enabled: true
          adminPassword: secret
        prometheus:
          retention: 30d
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy:
    automated:
      selfHeal: true

---
# ✅ ApplicationSet for multiple environments
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app-envs
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - env: dev
        cluster: https://dev.k8s.local
      - env: staging
        cluster: https://staging.k8s.local
      - env: production
        cluster: https://prod.k8s.local
  template:
    metadata:
      name: 'my-app-{{env}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/k8s-manifests.git
        targetRevision: main
        path: 'apps/my-app/overlays/{{env}}'
      destination:
        server: '{{cluster}}'
        namespace: my-app
      syncPolicy:
        automated:
          selfHeal: true
```

---

## Flux

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        FLUX ARCHITECTURE                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       FLUX CONTROLLERS                               │   │
│  │                                                                      │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │   │
│  │  │  Source     │   │ Kustomize   │   │    Helm     │               │   │
│  │  │ Controller  │   │ Controller  │   │ Controller  │               │   │
│  │  │             │   │             │   │             │               │   │
│  │  │ • GitRepo   │   │ • Kustomize │   │ • HelmRepo  │               │   │
│  │  │ • HelmRepo  │──▶│   ation     │   │ • HelmRel   │               │   │
│  │  │ • Bucket    │   │             │   │   ease      │               │   │
│  │  └─────────────┘   └──────┬──────┘   └──────┬──────┘               │   │
│  │                           │                 │                       │   │
│  │                           └────────┬────────┘                       │   │
│  │                                    │                                │   │
│  │                                    ▼                                │   │
│  │                           ┌─────────────┐                          │   │
│  │                           │ Notification│                          │   │
│  │                           │ Controller  │                          │   │
│  │                           │ (Alerts)    │                          │   │
│  │                           └─────────────┘                          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Key difference from ArgoCD:                                               │
│  • More modular (separate controllers)                                     │
│  • No built-in UI (use Weave GitOps or custom)                            │
│  • Native Kustomize support                                               │
│  • Better multi-tenancy                                                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Flux Resources

```yaml
# ✅ GitRepository source
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/myorg/k8s-manifests.git
  ref:
    branch: main
  secretRef:
    name: git-credentials  # For private repos

---
# ✅ Kustomization (reconcile manifests)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  targetNamespace: production
  sourceRef:
    kind: GitRepository
    name: my-app
  path: ./apps/my-app/overlays/production
  prune: true
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: my-app
    namespace: production
  timeout: 3m

---
# ✅ HelmRepository
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami

---
# ✅ HelmRelease
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: redis
  namespace: production
spec:
  interval: 5m
  chart:
    spec:
      chart: redis
      version: '17.x'
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    architecture: replication
    replica:
      replicaCount: 3
  upgrade:
    remediation:
      retries: 3

---
# ✅ Notification (alerts)
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: slack-alert
  namespace: flux-system
spec:
  eventSeverity: error
  eventSources:
  - kind: Kustomization
    name: '*'
  - kind: HelmRelease
    name: '*'
  providerRef:
    name: slack
---
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: alerts
  secretRef:
    name: slack-webhook
```

---

## Repository Structure

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    GITOPS REPO STRUCTURE                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Option 1: Monorepo (App + Manifests together)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  my-app/                                                             │   │
│  │  ├── src/                    # Application code                      │   │
│  │  ├── Dockerfile                                                      │   │
│  │  └── k8s/                    # Kubernetes manifests                  │   │
│  │      ├── base/                                                       │   │
│  │      │   ├── deployment.yaml                                        │   │
│  │      │   ├── service.yaml                                           │   │
│  │      │   └── kustomization.yaml                                     │   │
│  │      └── overlays/                                                   │   │
│  │          ├── dev/                                                    │   │
│  │          ├── staging/                                                │   │
│  │          └── production/                                             │   │
│  │                                                                      │   │
│  │  ✅ Simple, everything in one place                                 │   │
│  │  ❌ App and infra changes coupled                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Option 2: Separate repos (Recommended for larger teams)                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  my-app/                     # Application repo                      │   │
│  │  ├── src/                                                            │   │
│  │  ├── Dockerfile                                                      │   │
│  │  └── .github/workflows/      # CI: build, test, push image          │   │
│  │                                                                      │   │
│  │  k8s-manifests/              # GitOps repo                          │   │
│  │  ├── apps/                                                           │   │
│  │  │   └── my-app/                                                     │   │
│  │  │       ├── base/                                                   │   │
│  │  │       └── overlays/                                               │   │
│  │  ├── infrastructure/         # Cluster-wide resources               │   │
│  │  │   ├── cert-manager/                                               │   │
│  │  │   ├── ingress-nginx/                                              │   │
│  │  │   └── monitoring/                                                 │   │
│  │  └── clusters/               # Cluster bootstrap                    │   │
│  │      ├── dev/                                                        │   │
│  │      ├── staging/                                                    │   │
│  │      └── production/                                                 │   │
│  │                                                                      │   │
│  │  ✅ Separation of concerns                                          │   │
│  │  ✅ Different permissions for app devs vs platform team            │   │
│  │  ✅ Better for multiple apps                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## ArgoCD vs Flux

| Feature | ArgoCD | Flux |
|---------|--------|------|
| **UI** | Built-in (great!) | No (use Weave GitOps) |
| **Architecture** | Monolithic | Modular (controllers) |
| **Multi-tenancy** | RBAC + Projects | Native namespace isolation |
| **Helm** | Via plugin | Native controller |
| **Kustomize** | Native | Native |
| **Image automation** | Argo Image Updater | Native (Image Automation) |
| **Notifications** | Notifications (addon) | Native controller |
| **Learning curve** | Easier | Steeper |
| **CNCF** | Graduated | Graduated |

**Рекомендация:**
- ArgoCD: Если важен UI, простой старт
- Flux: Если нужна модульность, multi-tenancy, image automation

---

## Связи

- [[devops-overview]] — DevOps practices
- [[kubernetes-basics]] — K8s fundamentals
- [[ci-cd-pipelines]] — CI часть
- [[kubernetes-advanced]] — RBAC, Secrets

---

## Источники

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Flux Documentation](https://fluxcd.io/docs/)
- [GitOps Principles](https://opengitops.dev/)
- [Weave GitOps](https://www.weave.works/product/gitops/)
- "GitOps and Kubernetes" by Billy Yuen

---

---

## Проверь себя

> [!question]- Почему pull-based подход (GitOps) безопаснее push-based (традиционный CI/CD)?
> В push-based CI pipeline имеет credentials для доступа к кластеру -- компрометация CI = доступ к production. В pull-based agent живёт внутри кластера и сам тянет изменения из Git -- не нужны внешние credentials. Плюс agent непрерывно сверяет actual state с desired state: если кто-то изменил ресурс вручную (drift), GitOps-контроллер это обнаружит и откатит. Rollback = git revert, а не повторный запуск pipeline.

> [!question]- Monorepo или separate repos для GitOps? Какой подход выбрать для команды из 20 человек?
> Для команды из 20 человек лучше separate repos: app-репозиторий (код + Dockerfile + CI) и k8s-manifests (GitOps-репозиторий). Separation of concerns: разные permissions для app devs и platform team, история деплоев отделена от истории кода, несколько приложений в одном GitOps-репо. Monorepo проще для маленьких команд с одним приложением.

> [!question]- Сравните ArgoCD и Flux. Какой инструмент подходит для enterprise с multi-tenancy?
> Для enterprise с multi-tenancy Flux предпочтительнее: модульная архитектура (отдельные controllers), нативная namespace-изоляция, встроенный Image Automation controller. ArgoCD проще для старта и имеет отличный UI, но multi-tenancy реализуется через Projects и RBAC. Оба -- CNCF Graduated. ArgoCD -- если важен UI и простота, Flux -- если модульность и multi-tenancy критичны.

> [!question]- Как обновить image tag в GitOps-workflow без ручного коммита?
> Три подхода: 1) Image Automation (Flux) или Argo Image Updater -- автоматически следят за registry и коммитят новый tag в Git. 2) CI-initiated PR: CI собирает образ, создаёт PR с новым tag, после merge GitOps деплоит. 3) Ручной коммит (для критических сервисов). Best practice: автоматизация для staging, PR-based для production.

---

## Ключевые карточки

Что такое GitOps?
?
Подход, в котором Git является единственным source of truth для desired state инфраструктуры и приложений. Агент в кластере непрерывно сверяет actual state с Git и приводит систему к desired state. Push to Git = Deploy.

Чем GitOps отличается от традиционного CI/CD?
?
Традиционный CI/CD (push-based): pipeline пушит изменения в кластер, нужны внешние credentials. GitOps (pull-based): agent в кластере сам тянет из Git, непрерывная reconciliation, drift detection, rollback через git revert.

Что такое Reconciliation в контексте GitOps?
?
Процесс приведения actual state (что есть в кластере) к desired state (что описано в Git). Если кто-то изменил ресурс вручную -- reconciliation вернёт его к описанному в Git состоянию. Происходит непрерывно.

Что такое ArgoCD Application?
?
Ресурс ArgoCD, описывающий что деплоить: source (Git repo + path), destination (cluster + namespace), syncPolicy (automated/manual, selfHeal, prune). ApplicationSet позволяет генерировать Application для нескольких environments.

Что делает syncPolicy.selfHeal в ArgoCD?
?
selfHeal: true автоматически откатывает ручные изменения в кластере. Если кто-то изменил Deployment через kubectl -- ArgoCD вернёт его к состоянию из Git. Это защита от drift.

Чем Flux Kustomization отличается от Kubernetes Kustomize?
?
Flux Kustomization -- CRD Flux'а для reconciliation: определяет sourceRef (GitRepository), path, interval, healthChecks. Kubernetes Kustomize -- инструмент для кастомизации YAML (overlays). Flux использует Kustomize внутри, но его Kustomization -- это абстракция уровнем выше.

Что такое progressive delivery в GitOps?
?
Постепенный деплой с автоматической проверкой метрик: canary (10% -> 50% -> 100% трафика), с паузами для analysis. Argo Rollouts или Flagger. При плохих метриках -- автоматический rollback. Commit в Git -> Rollout -> Analysis -> full deploy или rollback.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[devops-incident-management]] | Incident management: что делать когда GitOps-деплой пошёл не так |
| Углубиться | [[kubernetes-advanced]] | RBAC и Secrets management -- критичны для безопасного GitOps |
| Смежная тема | [[infrastructure-as-code]] | IaC (Terraform) для создания кластера, GitOps для деплоя приложений |
| Обзор | [[devops-overview]] | Вернуться к карте раздела DevOps |

*Проверено: 2025-12-22*
