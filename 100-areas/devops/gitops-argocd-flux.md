---
title: "GitOps: ArgoCD, Flux, Declarative Deployments"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/devops
  - gitops
  - argocd
  - flux
  - kubernetes
  - type/concept
  - level/intermediate
related:
  - "[[devops-overview]]"
  - "[[kubernetes-basics]]"
  - "[[ci-cd-pipelines]]"
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

## Проверь себя

<details>
<summary>1. Почему pull-based лучше push-based для GitOps?</summary>

**Ответ:**

**Push-based (traditional CI/CD):**
- CI pipeline имеет credentials к кластеру
- Security risk: компрометация CI = доступ к кластеру
- CI push'ит изменения → нет drift detection

**Pull-based (GitOps):**
- Agent внутри кластера
- Не нужны external credentials
- Agent сам тянет изменения из Git
- Continuous reconciliation → drift detection
- Self-healing при manual changes

**Плюс:** Rollback = `git revert` (не нужно re-run pipeline)

</details>

<details>
<summary>2. Как обновить image tag в GitOps?</summary>

**Ответ:**

**Варианты:**

1. **Manual commit:**
   - CI builds image → pushes to registry
   - Developer updates tag in Git manually
   - GitOps deploys

2. **Automated (Argo Image Updater / Flux Image Automation):**
```yaml
# Flux ImagePolicy
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImagePolicy
metadata:
  name: my-app
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: '>=1.0.0'
```
   - Автоматически обновляет tag в Git
   - Commit автоматически создаётся

3. **CI updates Git:**
   - CI builds image
   - CI делает PR с новым tag
   - После merge → GitOps deploys

**Best practice:** Используй image automation или CI-initiated PRs.

</details>

<details>
<summary>3. Как реализовать progressive delivery с GitOps?</summary>

**Ответ:**

**Инструменты:**
- Argo Rollouts
- Flagger (Flux)

**Пример с Argo Rollouts:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - analysis:
          templates:
          - templateName: success-rate
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
```

**Flow:**
1. Commit изменений в Git
2. GitOps создаёт Rollout
3. Argo Rollouts/Flagger управляет canary
4. Автоматический rollback при плохих метриках

</details>

<details>
<summary>4. Как организовать secrets в GitOps?</summary>

**Ответ:**

**Проблема:** Secrets нельзя коммитить в plain text.

**Решения:**

1. **Sealed Secrets:**
```yaml
# Encrypt locally
kubeseal < secret.yaml > sealed-secret.yaml
# Commit sealed-secret.yaml to Git
```

2. **External Secrets Operator:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
spec:
  secretStoreRef:
    name: aws-secrets-manager
  data:
  - secretKey: password
    remoteRef:
      key: prod/db-password
```
Коммитишь ExternalSecret, не сам secret.

3. **SOPS + ArgoCD/Flux:**
   - Encrypt YAML с SOPS
   - ArgoCD/Flux decrypt при sync

**Best practice:** External Secrets + Vault/AWS Secrets Manager

</details>

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

*Проверено: 2025-12-22*
