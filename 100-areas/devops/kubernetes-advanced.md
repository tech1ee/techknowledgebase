---
title: "Kubernetes Advanced: RBAC, Network Policies, Operators"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - devops
  - kubernetes
  - rbac
  - security
  - operators
related:
  - "[[kubernetes-basics]]"
  - "[[devops-overview]]"
  - "[[security-overview]]"
---

# Kubernetes Advanced: RBAC, Network Policies, Operators

> За пределами Pods и Deployments — security, networking и extensibility в production Kubernetes.

---

## TL;DR

- **RBAC** — Role-Based Access Control, кто что может делать в кластере
- **Network Policies** — firewall для pods, default deny + explicit allow
- **Secrets** — хранение sensitive данных (лучше с external secrets)
- **Operators** — Custom Controllers для управления сложными приложениями

---

## Терминология

| Термин | Значение |
|--------|----------|
| **RBAC** | Role-Based Access Control |
| **ServiceAccount** | Identity для pods в кластере |
| **Role/ClusterRole** | Набор permissions |
| **RoleBinding** | Связь Role с пользователем/SA |
| **NetworkPolicy** | Firewall rules для pods |
| **CRD** | Custom Resource Definition |
| **Operator** | Controller + CRD для управления app |
| **Admission Controller** | Валидация/мутация ресурсов |

---

## RBAC (Role-Based Access Control)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          KUBERNETES RBAC                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHO (Subjects)              WHAT (Verbs)              WHERE (Resources)   │
│  ┌──────────────┐           ┌──────────────┐          ┌──────────────┐    │
│  │ • User       │           │ • get        │          │ • pods       │    │
│  │ • Group      │           │ • list       │          │ • services   │    │
│  │ • Service    │           │ • watch      │          │ • secrets    │    │
│  │   Account    │           │ • create     │          │ • configmaps │    │
│  └──────┬───────┘           │ • update     │          │ • deployments│    │
│         │                   │ • delete     │          └──────────────┘    │
│         │                   │ • patch      │                 │             │
│         │                   └──────────────┘                 │             │
│         │                          │                         │             │
│         │                          ▼                         │             │
│         │              ┌────────────────────────┐           │             │
│         │              │   Role / ClusterRole   │◀──────────┘             │
│         │              │                        │                          │
│         │              │  rules:                │                          │
│         │              │  - apiGroups: [""]     │                          │
│         │              │    resources: [pods]   │                          │
│         │              │    verbs: [get, list]  │                          │
│         │              └───────────┬────────────┘                          │
│         │                          │                                        │
│         │                          │                                        │
│         │              ┌───────────┴────────────┐                          │
│         │              │                        │                          │
│         ▼              ▼                        ▼                          │
│  ┌─────────────────────────┐    ┌─────────────────────────┐               │
│  │    RoleBinding          │    │   ClusterRoleBinding    │               │
│  │    (namespace-scoped)   │    │   (cluster-wide)        │               │
│  │                         │    │                         │               │
│  │  subjects: [...]        │    │  subjects: [...]        │               │
│  │  roleRef: role-name     │    │  roleRef: clusterrole   │               │
│  └─────────────────────────┘    └─────────────────────────┘               │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### RBAC Examples

```yaml
# ✅ ServiceAccount for application
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: production

---
# ✅ Role - namespace-scoped permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]

---
# ✅ RoleBinding - bind Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

---
# ✅ ClusterRole - cluster-wide permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
  # ❌ No "create", "update", "delete" - read-only

---
# ✅ ClusterRoleBinding with Group
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: developers-view
subjects:
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: view  # Built-in read-only role
  apiGroup: rbac.authorization.k8s.io
```

### Common Built-in Roles

| Role | Permissions |
|------|-------------|
| **view** | Read-only access to most resources |
| **edit** | Read/write, no RBAC or quota changes |
| **admin** | Full access in namespace |
| **cluster-admin** | Full access everywhere (dangerous!) |

---

## Network Policies

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       NETWORK POLICIES                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEFAULT: All pods can talk to all pods (no isolation)                    │
│                                                                             │
│  WITH NETWORK POLICY: Explicit allow rules                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        NAMESPACE: production                         │   │
│  │                                                                      │   │
│  │   ┌─────────────┐                         ┌─────────────┐           │   │
│  │   │   frontend  │                         │   backend   │           │   │
│  │   │   pods      │ ────── ALLOWED ───────▶ │   pods      │           │   │
│  │   │             │        (port 8080)      │             │           │   │
│  │   │  app=frontend                         │  app=backend│           │   │
│  │   └─────────────┘                         └──────┬──────┘           │   │
│  │                                                   │                  │   │
│  │                                                   │ ALLOWED          │   │
│  │                                                   │ (port 5432)      │   │
│  │   ┌─────────────┐                                ▼                  │   │
│  │   │   random    │ ─── BLOCKED ──────▶    ┌─────────────┐           │   │
│  │   │   pod       │     (no policy)        │  postgres   │           │   │
│  │   └─────────────┘                        │  pods       │           │   │
│  │                                          │             │           │   │
│  │   External ──── BLOCKED ───────────────▶ │  app=db     │           │   │
│  │   Traffic       (no ingress rule)        └─────────────┘           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Network Policy Examples

```yaml
# ✅ Default deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress

---
# ✅ Allow traffic from frontend to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# ✅ Allow backend to database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 5432

---
# ✅ Allow ingress from specific namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Prometheus metrics

---
# ✅ Egress policy - restrict outbound
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # Allow database
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## Secrets Management

```yaml
# ❌ Wrong: Secret in plain YAML (encoded, not encrypted!)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  # Base64 encoded - NOT SECURE!
  password: cGFzc3dvcmQxMjM=

---
# ✅ Better: External Secrets Operator
# Syncs secrets from AWS Secrets Manager, Vault, etc.
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: db-credentials
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: production/database
      property: password

---
# ✅ Sealed Secrets (encrypt secrets for Git)
# Install kubeseal, then:
# kubeseal --format yaml < secret.yaml > sealed-secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  encryptedData:
    password: AgBy8hCe...encrypted...data...

---
# ✅ Using secrets in Pod
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
    # Or mount as file
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-credentials
```

---

## Custom Resource Definitions (CRDs)

```yaml
# ✅ Define custom resource type
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: certificates.cert-manager.io
spec:
  group: cert-manager.io
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required:
            - secretName
            - issuerRef
            properties:
              secretName:
                type: string
              dnsNames:
                type: array
                items:
                  type: string
              issuerRef:
                type: object
                properties:
                  name:
                    type: string
                  kind:
                    type: string
  scope: Namespaced
  names:
    plural: certificates
    singular: certificate
    kind: Certificate
    shortNames:
    - cert

---
# ✅ Use custom resource
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-app-tls
  namespace: production
spec:
  secretName: my-app-tls-secret
  dnsNames:
  - myapp.example.com
  - www.myapp.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

---

## Operators Pattern

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        OPERATOR PATTERN                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional: Manual operations                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │   Human Operator                                                    │   │
│  │        │                                                            │   │
│  │        │ manual commands                                            │   │
│  │        ▼                                                            │   │
│  │   kubectl scale, kubectl exec, scripts, runbooks                   │   │
│  │        │                                                            │   │
│  │        ▼                                                            │   │
│  │   Database (scale replicas, backup, failover)                      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Operator: Automated operations                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │   ┌────────────────────┐         ┌────────────────────┐            │   │
│  │   │   Custom Resource  │         │     Operator       │            │   │
│  │   │   (PostgresCluster)│ ◀─────▶ │   (Controller)     │            │   │
│  │   │                    │  watch  │                    │            │   │
│  │   │  spec:             │  react  │  • Create pods     │            │   │
│  │   │    replicas: 3     │         │  • Setup replicas  │            │   │
│  │   │    storage: 100Gi  │         │  • Handle failover │            │   │
│  │   │    backup: daily   │         │  • Schedule backup │            │   │
│  │   └────────────────────┘         └────────────────────┘            │   │
│  │                                           │                         │   │
│  │                                           │ manages                 │   │
│  │                                           ▼                         │   │
│  │                                  ┌────────────────────┐            │   │
│  │                                  │   Kubernetes       │            │   │
│  │                                  │   Resources        │            │   │
│  │                                  │                    │            │   │
│  │                                  │  • StatefulSet     │            │   │
│  │                                  │  • Services        │            │   │
│  │                                  │  • PVCs            │            │   │
│  │                                  │  • ConfigMaps      │            │   │
│  │                                  │  • CronJobs        │            │   │
│  │                                  └────────────────────┘            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Popular Operators:                                                        │
│  • Prometheus Operator (monitoring)                                       │
│  • Cert-Manager (TLS certificates)                                        │
│  • Strimzi (Kafka)                                                        │
│  • Zalando Postgres Operator                                              │
│  • ArgoCD (GitOps)                                                        │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Operator Example (Prometheus)

```yaml
# ✅ Install Prometheus via Operator
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: main
  namespace: monitoring
spec:
  replicas: 2
  retention: 30d
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: fast
        resources:
          requests:
            storage: 100Gi
  serviceMonitorSelector:
    matchLabels:
      team: backend
  alerting:
    alertmanagers:
    - namespace: monitoring
      name: alertmanager-main
      port: web

---
# ✅ ServiceMonitor - tell Prometheus what to scrape
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: production
  labels:
    team: backend
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

## Pod Security

```yaml
# ✅ Pod Security Standards (PSS)
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Enforce restricted policy
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted

---
# ✅ Secure Pod configuration
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
      requests:
        memory: "128Mi"
        cpu: "100m"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

---

## Проверь себя

<details>
<summary>1. Role vs ClusterRole — когда что?</summary>

**Ответ:**

**Role:**
- Namespace-scoped
- Permissions только в одном namespace
- Use case: Team access to their namespace

**ClusterRole:**
- Cluster-wide
- Может быть использован:
  - С ClusterRoleBinding → permissions везде
  - С RoleBinding → permissions в конкретном namespace

**Примеры:**
```yaml
# Role: read pods in "dev" namespace only
kind: Role
namespace: dev
rules:
- resources: [pods]
  verbs: [get, list]

# ClusterRole: read nodes (cluster-wide resource)
kind: ClusterRole
rules:
- resources: [nodes]
  verbs: [get, list]
```

</details>

<details>
<summary>2. Как реализовать "zero trust" networking в K8s?</summary>

**Ответ:**

**Принцип:** Default deny, explicit allow

**Шаги:**

1. **Default deny ingress в каждом namespace:**
```yaml
kind: NetworkPolicy
spec:
  podSelector: {}
  policyTypes: [Ingress]
```

2. **Default deny egress:**
```yaml
kind: NetworkPolicy
spec:
  podSelector: {}
  policyTypes: [Egress]
```

3. **Explicit allow rules** для каждой легитимной связи

4. **Allow DNS** (иначе ничего не работает):
```yaml
egress:
- to:
  - namespaceSelector: {}
    podSelector:
      matchLabels:
        k8s-app: kube-dns
  ports:
  - port: 53
    protocol: UDP
```

5. **Service Mesh** (Istio/Linkerd) для mTLS между pods

</details>

<details>
<summary>3. Как безопасно хранить secrets в GitOps?</summary>

**Ответ:**

**Проблема:** Secrets нельзя коммитить в Git в plain text.

**Решения:**

1. **Sealed Secrets:**
   - Encrypt locally с публичным ключом
   - Только controller в кластере может decrypt
   - Safe to commit encrypted version

2. **External Secrets Operator:**
   - Secrets хранятся в AWS/GCP/Vault
   - ESO синхронизирует в K8s Secrets
   - В Git только reference

3. **SOPS (Mozilla):**
   - Encrypt YAML files
   - Decrypt при деплое
   - Integration с ArgoCD

4. **Vault + CSI Driver:**
   - Secrets inject напрямую в pods
   - Не создаются K8s Secrets вообще

**Best practice:** External Secrets + Vault/AWS Secrets Manager

</details>

<details>
<summary>4. Что такое Operator и зачем он нужен?</summary>

**Ответ:**

**Operator = Custom Controller + CRD**

**Зачем:**
- Автоматизация Day 2 operations
- Encoding operational knowledge в код
- Self-healing для сложных приложений

**Пример: Database Operator**
- Без оператора: Ручной failover, backup, scaling
- С оператором: Декларативно опиши что хочешь

```yaml
apiVersion: postgres-operator.crunchydata.com/v1beta1
kind: PostgresCluster
spec:
  replicas: 3
  backup:
    schedule: "0 * * * *"  # hourly
  highAvailability:
    enabled: true
```

Оператор сам:
- Создаёт StatefulSet, Services, PVCs
- Настраивает репликацию
- Делает failover при падении primary
- Запускает backup по расписанию

</details>

---

## Связи

- [[kubernetes-basics]] — основы K8s
- [[devops-overview]] — DevOps practices
- [[security-overview]] — security fundamentals
- [[gitops-argocd-flux]] — GitOps deployments

---

## Источники

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Operator Pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [External Secrets Operator](https://external-secrets.io/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

---

*Проверено: 2025-12-22*
