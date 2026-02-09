---
title: "Kubernetes: оркестрация контейнеров"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/kubernetes
  - infrastructure/orchestration
  - containers/k8s
  - type/concept
  - level/beginner
related:
  - "[[docker-for-developers]]"
  - "[[microservices-vs-monolith]]"
  - "[[ci-cd-pipelines]]"
  - "[[network-cloud-modern]]"
  - "[[networking-overview]]"
---

# Kubernetes: оркестрация контейнеров

Node упал → Pod автоматически переехал. Нагрузка выросла → автоскейлинг. Деплой → rolling update без downtime. K8s оправдан только при реальной потребности в масштабировании.

---

## Терминология

### Базовые концепции

| Термин | Значение |
|--------|----------|
| **Cluster** | Набор машин (nodes) под управлением K8s |
| **Control Plane** | Мозг кластера: API server, scheduler, controller manager, etcd |
| **Worker Node** | Машина, где запускаются Pod'ы |
| **Pod** | Минимальная единица — 1+ контейнеров с общей сетью и storage |
| **ReplicaSet** | Поддерживает заданное количество идентичных Pod'ов |
| **Deployment** | Декларативное управление ReplicaSet + rolling updates |
| **Service** | Стабильный сетевой endpoint для набора Pod'ов |
| **Namespace** | Логическая изоляция ресурсов (dev/staging/prod) |

### Компоненты Control Plane

| Термин | Значение |
|--------|----------|
| **kube-apiserver** | REST API кластера, точка входа для kubectl |
| **etcd** | Distributed key-value store, хранит состояние кластера |
| **kube-scheduler** | Выбирает на какой Node запустить Pod |
| **controller-manager** | Запускает контроллеры (ReplicaSet, Deployment, etc.) |

### Компоненты Worker Node

| Термин | Значение |
|--------|----------|
| **kubelet** | Агент на каждой ноде, запускает Pod'ы |
| **kube-proxy** | Сетевой прокси, реализует Service |
| **Container Runtime** | Docker, containerd, CRI-O — запускает контейнеры |

### Сеть и доступ

| Термин | Значение |
|--------|----------|
| **ClusterIP** | Service внутри кластера (default), недоступен извне |
| **NodePort** | Service доступен на порту каждой ноды (30000-32767) |
| **LoadBalancer** | Создаёт облачный Load Balancer с публичным IP |
| **Ingress** | L7 HTTP/HTTPS маршрутизация, TLS termination |
| **Ingress Controller** | Реализация Ingress (nginx, traefik, ALB) |

### Конфигурация и хранение

| Термин | Значение |
|--------|----------|
| **ConfigMap** | Key-value конфигурация (не секретная) |
| **Secret** | Конфиденциальные данные (base64, не encryption!) |
| **PersistentVolume (PV)** | Кусок storage в кластере |
| **PersistentVolumeClaim (PVC)** | Запрос на storage от Pod'а |

### Важные концепции

| Термин | Значение |
|--------|----------|
| **Labels** | Key-value метки на объектах для селекции |
| **Selector** | Выбор объектов по labels (matchLabels) |
| **Rolling Update** | Постепенная замена Pod'ов без downtime |
| **Sidecar** | Вспомогательный контейнер в Pod'е (логи, прокси) |
| **livenessProbe** | Проверка: жив ли контейнер? (рестарт при fail) |
| **readinessProbe** | Проверка: готов принимать трафик? |
| **startupProbe** | Проверка при старте (для медленных приложений) |
| **HPA** | HorizontalPodAutoscaler — автомасштабирование по CPU/memory |

### Единицы измерения

| Единица | Значение |
|---------|----------|
| **m (millicores)** | 1000m = 1 CPU ядро. 250m = 0.25 ядра |
| **Mi (Mebibytes)** | 128Mi = 128 × 1024² bytes ≈ 134MB |
| **Gi (Gibibytes)** | 1Gi = 1024Mi ≈ 1.07GB |

### Инструменты

| Термин | Значение |
|--------|----------|
| **kubectl** | CLI для управления кластером |
| **minikube** | Локальный K8s кластер (1 node) для разработки |
| **kind** | Kubernetes IN Docker — K8s кластер в Docker контейнерах |
| **EKS** | Amazon Elastic Kubernetes Service (managed) |
| **GKE** | Google Kubernetes Engine (managed) |
| **AKS** | Azure Kubernetes Service (managed) |
| **ArgoCD / Flux** | GitOps — деплой из Git репозитория |
| **RBAC** | Role-Based Access Control — права доступа |
| **Network Policy** | Firewall правила между Pod'ами |
| **PodDisruptionBudget** | Гарантия минимума Pod'ов при обслуживании |

---

## Архитектура K8s кластера

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES CLUSTER                              │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      CONTROL PLANE (Master)                          │ │
│  │                                                                      │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌────────────────┐            │ │
│  │   │ kube-apiserver│  │kube-scheduler│  │controller-mgr │            │ │
│  │   │              │  │              │  │                │            │ │
│  │   │ REST API     │  │ Куда        │  │ Следит за     │            │ │
│  │   │ kubectl →    │  │ Pod → Node? │  │ desired state │            │ │
│  │   └──────────────┘  └──────────────┘  └────────────────┘            │ │
│  │                              │                                       │ │
│  │                              ▼                                       │ │
│  │                    ┌──────────────────┐                              │ │
│  │                    │       etcd       │                              │ │
│  │                    │                  │                              │ │
│  │                    │ Состояние        │                              │ │
│  │                    │ кластера (KV)    │                              │ │
│  │                    └──────────────────┘                              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                      │
│                                    │ (network)                            │
│               ┌────────────────────┼────────────────────┐                │
│               │                    │                    │                │
│               ▼                    ▼                    ▼                │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐   │
│  │   WORKER NODE 1    │ │   WORKER NODE 2    │ │   WORKER NODE 3    │   │
│  │                    │ │                    │ │                    │   │
│  │ ┌────────────────┐ │ │ ┌────────────────┐ │ │ ┌────────────────┐ │   │
│  │ │    kubelet     │ │ │ │    kubelet     │ │ │ │    kubelet     │ │   │
│  │ │ Запускает Pods │ │ │ │ Запускает Pods │ │ │ │ Запускает Pods │ │   │
│  │ └────────────────┘ │ │ └────────────────┘ │ │ └────────────────┘ │   │
│  │                    │ │                    │ │                    │   │
│  │ ┌────────────────┐ │ │ ┌────────────────┐ │ │ ┌────────────────┐ │   │
│  │ │   kube-proxy   │ │ │ │   kube-proxy   │ │ │ │   kube-proxy   │ │   │
│  │ │ Service → Pods │ │ │ │ Service → Pods │ │ │ │ Service → Pods │ │   │
│  │ └────────────────┘ │ │ └────────────────┘ │ │ └────────────────┘ │   │
│  │                    │ │                    │ │                    │   │
│  │ ┌─────┐ ┌─────┐   │ │ ┌─────┐ ┌─────┐   │ │ ┌─────┐           │   │
│  │ │Pod 1│ │Pod 2│   │ │ │Pod 3│ │Pod 4│   │ │ │Pod 5│           │   │
│  │ └─────┘ └─────┘   │ │ └─────┘ └─────┘   │ │ └─────┘           │   │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Как работает деплой:**

```
1. kubectl apply -f deployment.yaml
        │
        ▼
2. kube-apiserver принимает запрос, сохраняет в etcd
        │
        ▼
3. controller-manager видит: "Нужно 3 Pod'а, есть 0"
        │
        ▼
4. Создаёт Pod'ы в etcd (пока без node assignment)
        │
        ▼
5. kube-scheduler видит "unscheduled pods"
        │
        ▼
6. Выбирает Node для каждого Pod'а (по ресурсам, affinity)
        │
        ▼
7. kubelet на выбранной Node видит "мой Pod"
        │
        ▼
8. kubelet скачивает образ, запускает контейнер
        │
        ▼
9. Pod running! kube-proxy настраивает сеть для Service
```

---

## Зачем Kubernetes: проблема масштаба

```
Без оркестрации (Docker на 1 сервере):
┌─────────────────────────────────────┐
│ Server                              │
│  ┌─────┐ ┌─────┐ ┌─────┐           │
│  │ App │ │ App │ │ DB  │           │
│  └─────┘ └─────┘ └─────┘           │
└─────────────────────────────────────┘

Проблемы:
• Сервер упал → всё недоступно
• Нагрузка выросла → вручную добавлять серверы
• Деплой → downtime
• Rollback → ручной процесс

С Kubernetes:
┌─────────────────────────────────────────────────────┐
│ Kubernetes Cluster                                  │
│                                                     │
│ Node 1        Node 2        Node 3                 │
│ ┌─────┐      ┌─────┐       ┌─────┐                │
│ │Pod 1│      │Pod 2│       │Pod 3│                │
│ │ App │      │ App │       │ App │   ← 3 реплики │
│ └─────┘      └─────┘       └─────┘                │
│                                                     │
│ Автоматически:                                      │
│ • Node упал → Pod переехал на другой Node          │
│ • Нагрузка ↑ → автоскейлинг                        │
│ • Деплой → Rolling update без downtime             │
│ • Проблема → автоматический rollback               │
└─────────────────────────────────────────────────────┘
```

---

## Ключевые абстракции

### Pod: минимальная единица

```yaml
# pod.yaml — обычно не создаёшь напрямую
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  containers:
    - name: app
      image: my-app:1.0.0
      ports:
        - containerPort: 8080
      resources:
        requests:          # Минимум для запуска
          memory: "128Mi"
          cpu: "250m"
        limits:            # Максимум (будет убит при превышении)
          memory: "256Mi"
          cpu: "500m"
```

**Что значат эти единицы?**

```
CPU:
  "250m" = 250 millicores = 0.25 CPU ядра
  "1"    = 1 полное ядро
  "2"    = 2 ядра

Memory:
  "128Mi" = 128 Mebibytes = 128 × 1024² bytes ≈ 134 MB
  "1Gi"   = 1 Gibibyte = 1024 Mi ≈ 1.07 GB

  Mi/Gi (binary) vs MB/GB (decimal):
  128Mi = 134,217,728 bytes
  128M  = 128,000,000 bytes  (некоторые системы используют M вместо Mi)
```

**requests vs limits:**
- **requests** — гарантированный минимум. Scheduler не поставит Pod на ноду, где нет этих ресурсов.
- **limits** — жёсткий максимум. Превысил memory limit → OOM Kill. Превысил CPU limit → throttling.

```
Что такое Pod:

┌─────────────────────────────────────┐
│ Pod                                 │
│                                     │
│  ┌─────────┐    ┌─────────┐        │
│  │Container│    │Container│        │
│  │  (app)  │    │ (sidecar)│       │
│  └────┬────┘    └────┬────┘        │
│       │              │              │
│       └──────┬───────┘              │
│              │                      │
│    Общий network namespace          │
│    Общие volumes                    │
│    Общий IP-адрес                   │
└─────────────────────────────────────┘
```

**Что такое sidecar?**

Sidecar — вспомогательный контейнер, который работает рядом с основным приложением в одном Pod'е. Типичные примеры:

- **Log shipper** — собирает логи из файла и отправляет в ElasticSearch
- **Proxy** (Envoy, Istio) — перехватывает трафик для service mesh
- **Secrets sync** — подтягивает секреты из Vault

Sidecar делит с основным контейнером сеть (localhost) и volumes, что позволяет им взаимодействовать без сложной конфигурации.

```
Важно:
• 1 Pod = 1+ контейнеров (обычно 1, но бывают sidecars)
• Контейнеры в Pod делят сеть и storage
• Pod — эфемерен (может быть убит в любой момент)
• Никогда не создавай "naked pods" напрямую!
```

### Deployment: управление репликами

```yaml
# deployment.yaml — основной способ деплоя
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3                    # Всегда 3 копии
  selector:
    matchLabels:
      app: my-app                # ← Deployment управляет Pod'ами с этим label
  strategy:
    type: RollingUpdate          # Постепенная замена Pod'ов (см. ниже)
    rollingUpdate:
      maxSurge: 1                # +1 Pod сверх replicas во время апдейта
      maxUnavailable: 0          # 0 Pod'ов может быть недоступно → всегда 3+
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: my-app:1.0.0
          ports:
            - containerPort: 8080
          # Health checks — ОБЯЗАТЕЛЬНО для production
          # Без них K8s не знает, жив ли Pod и готов ли он к трафику
          livenessProbe:           # Жив? Если нет → рестарт контейнера
            httpGet:
              path: /health        # Endpoint, который вернёт 200 OK
              port: 8080
            initialDelaySeconds: 10  # Ждать 10с перед первой проверкой
            periodSeconds: 5         # Проверять каждые 5с
          readinessProbe:          # Готов? Если нет → убрать из Service
            httpGet:
              path: /ready         # Может быть тот же /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 3
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
```

**Как работают Labels и Selector?**

Labels — это key-value метки, которые вешаются на объекты K8s. Selector — механизм выборки по этим меткам.

```
selector:                      template.metadata.labels:
  matchLabels:                   app: my-app
    app: my-app
        │                              │
        └──────────────┬───────────────┘
                       │
            "Найди все Pod'ы, где label app=my-app"
```

Deployment создаёт Pod'ы с labels из `template.metadata.labels`. Затем через `selector.matchLabels` находит их и управляет ими. Если Pod с нужным label создан вручную — Deployment подхватит и его!

**Как работает RollingUpdate?**

При изменении image (или других полей в template), K8s постепенно заменяет Pod'ы:

```
replicas: 3, maxSurge: 1, maxUnavailable: 0

Начало:       [v1] [v1] [v1]           (3 Pod'а версии 1)
Создаём +1:   [v1] [v1] [v1] [v2]      (maxSurge: можно +1)
v2 ready:     [v1] [v1] [--] [v2]      (убираем 1 старый)
Создаём ещё:  [v1] [v1] [v2] [v2]
...           [v1] [v2] [v2] [v2]
Финиш:        [v2] [v2] [v2]           (все Pod'ы v2)

maxUnavailable: 0 гарантирует, что всегда >= 3 Pod'ов доступны
```

```
Что делает Deployment:

                    Deployment
                        │
                        ▼
                    ReplicaSet
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
         Pod 1        Pod 2        Pod 3

При обновлении (image: 1.0.0 → 2.0.0):

ReplicaSet v1              ReplicaSet v2
┌─────┬─────┬─────┐       ┌─────┐
│Pod 1│Pod 2│Pod 3│  →    │Pod 4│  (новая версия)
└─────┴─────┴─────┘       └─────┘
                               ↓
┌─────┬─────┐             ┌─────┬─────┐
│Pod 1│Pod 2│             │Pod 4│Pod 5│
└─────┴─────┘             └─────┴─────┘
                               ↓
┌─────┐                   ┌─────┬─────┬─────┐
│Pod 1│                   │Pod 4│Pod 5│Pod 6│
└─────┘                   └─────┴─────┴─────┘
   ↓
(удалён)

Zero downtime rolling update!
```

### Service: сетевой доступ

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app              # ← Тот же label, что в Pod'ах Deployment'а
  ports:
    - port: 80               # Порт, на котором слушает Service
      targetPort: 8080       # Порт контейнера (куда проксируется)
  type: ClusterIP            # Только внутри кластера (default)
```

**Как Service находит Pod'ы?**

Service использует selector для поиска Pod'ов. Все Pod'ы с matching labels автоматически добавляются в Service (endpoint'ы обновляются динамически).

```
Service: my-app-service           Pod'ы с label app=my-app
selector: app=my-app
         │                        ┌─────────────────────┐
         │                        │ Pod 1 (10.0.0.5)    │
         ├───────────────────────►│ labels:             │
         │                        │   app: my-app       │
         │                        └─────────────────────┘
         │                        ┌─────────────────────┐
         └───────────────────────►│ Pod 2 (10.0.0.6)    │
                                  │ labels:             │
                                  │   app: my-app       │
                                  └─────────────────────┘
```

**DNS внутри кластера:**

K8s автоматически создаёт DNS записи для Service'ов:
- `my-app-service` — внутри того же namespace
- `my-app-service.default` — полное имя (namespace = default)
- `my-app-service.default.svc.cluster.local` — FQDN

```
Типы Service:

1. ClusterIP (default) — только внутри кластера
   ┌─────────────────────────────────┐
   │ Cluster                         │
   │                                 │
   │  Service:ClusterIP              │
   │  ┌─────────────┐                │
   │  │ 10.0.0.50   │────► Pods      │
   │  └─────────────┘                │
   │                                 │
   │  Другие Pods могут обращаться   │
   │  по DNS: my-app-service         │
   └─────────────────────────────────┘

2. NodePort — доступ снаружи через порт ноды
   ┌─────────────────────────────────┐
   │ Cluster                         │
   │                                 │
   │  ┌─────────────┐                │
   │  │ NodePort    │                │
   │  │ :30080      │────► Pods      │
   │  └─────────────┘                │
   └──────────┬──────────────────────┘
              │
   External: http://node-ip:30080

3. LoadBalancer — облачный Load Balancer
   ┌─────────────────────────────────┐
   │ Cloud LB                        │
   │ ┌─────────────┐                 │
   │ │ Public IP   │                 │
   │ └──────┬──────┘                 │
   └────────│────────────────────────┘
            │
   ┌────────│────────────────────────┐
   │ Cluster│                        │
   │        ▼                        │
   │  ┌─────────────┐                │
   │  │ LoadBalancer│────► Pods      │
   │  └─────────────┘                │
   └─────────────────────────────────┘
```

### ConfigMap и Secret: конфигурация

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # postgres.default.svc = Service "postgres" в namespace "default"
  # Формат: <service-name>.<namespace>.svc
  DATABASE_HOST: "postgres.default.svc"
  LOG_LEVEL: "info"
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:                   # Будет закодировано в base64
  DATABASE_PASSWORD: "super-secret"
  API_KEY: "sk-1234567890"
```

```yaml
# Использование в Deployment
spec:
  containers:
    - name: app
      envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
      # Или отдельные переменные:
      env:
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_PASSWORD
```

---

## Минимальный рабочий пример

```yaml
# Полный пример: Deployment + Service
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
        - name: hello
          # nginx:alpine — минимальный образ (~40MB vs ~180MB для nginx:latest)
          # Alpine Linux использует musl libc вместо glibc
          # Подходит для stateless приложений, быстрый pull
          image: nginx:alpine
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: hello-service
spec:
  selector:
    app: hello
  ports:
    - port: 80
      targetPort: 80
  type: LoadBalancer
```

```bash
# Применить манифест (создать или обновить ресурсы)
kubectl apply -f hello-app.yaml

# Проверить статус
kubectl get pods              # STATUS: Running, Pending, Error
kubectl get services          # CLUSTER-IP, PORT
kubectl get deployments       # READY: 2/2

# Логи всех Pod'ов с label app=hello
kubectl logs -l app=hello

# Shell внутрь контейнера (-it = interactive + tty)
kubectl exec -it <pod-name> -- /bin/sh

# Изменить количество реплик "на лету"
kubectl scale deployment hello-app --replicas=5

# Обновить образ → триггерит Rolling Update
# "hello" здесь — имя контейнера из spec.containers[].name
kubectl set image deployment/hello-app hello=nginx:1.25

# Откатить на предыдущую версию
kubectl rollout undo deployment/hello-app
```

---

## Health Probes: три типа

Health probes — механизм, с помощью которого K8s проверяет состояние контейнеров. Без них K8s не знает, работает ли приложение.

```yaml
# Обязательно для production!
spec:
  containers:
    - name: app
      # 1. Liveness — жив ли контейнер?
      # Fail → K8s перезапустит контейнер
      # Используй для обнаружения deadlock'ов, зависших процессов
      livenessProbe:
        httpGet:
          path: /health      # Должен вернуть 200-399
          port: 8080
        initialDelaySeconds: 15  # Ждать 15с после старта (дать время на init)
        periodSeconds: 10        # Проверять каждые 10с
        timeoutSeconds: 1        # Таймаут на ответ (default: 1)
        failureThreshold: 3      # 3 fail'а подряд → рестарт

      # 2. Readiness — готов ли принимать трафик?
      # Fail → Pod убирается из Service endpoints (перестаёт получать трафик)
      # НО Pod НЕ перезапускается!
      # Используй когда: БД временно недоступна, кэш прогревается
      readinessProbe:
        httpGet:
          path: /ready       # Может проверять зависимости (DB, cache)
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
        successThreshold: 1      # Сколько успехов чтобы стать ready

      # 3. Startup — для медленно стартующих приложений
      # Пока не пройдёт — liveness/readiness не проверяются
      # Используй для Java-приложений с долгим стартом
      startupProbe:
        httpGet:
          path: /health
          port: 8080
        failureThreshold: 30     # 30 × 10с = 5 минут на старт
        periodSeconds: 10
```

**Другие типы проверок (кроме httpGet):**

```yaml
# TCP — проверка, что порт открыт
livenessProbe:
  tcpSocket:
    port: 3306

# Exec — выполнить команду в контейнере (exit 0 = success)
livenessProbe:
  exec:
    command:
      - cat
      - /tmp/healthy
```

```
Что происходит при провале:

Liveness failed:
  → Pod перезапускается
  → Хорошо для зависших процессов

Readiness failed:
  → Pod убирается из Service (не получает трафик)
  → Pod НЕ перезапускается
  → Хорошо для временных проблем (БД недоступна)

Startup failed:
  → Pod перезапускается
  → Liveness/Readiness не проверяются пока Startup не пройдёт
```

---

## Подводные камни

### Проблема 1: Kubernetes — это сложно

```
Минимальный production setup требует:

• Cluster (managed: EKS, GKE, AKS или self-hosted)
• Ingress Controller
• Certificate Manager
• Monitoring (Prometheus + Grafana)
• Logging (EFK/Loki)
• Secret Management
• Network Policies
• RBAC
• Backup strategy

Время на настройку: недели, не дни
Стоимость: $300-1000+/месяц минимум
```

### Проблема 2: Когда Kubernetes НЕ нужен

```
❌ Не используй K8s если:
• Команда < 5 человек
• Один сервис без микросервисов
• Нагрузка стабильная и небольшая
• Нет DevOps/SRE экспертизы
• MVP / ранняя стадия стартапа

✅ Альтернативы:
• Docker Compose + single server
• Cloud Run / AWS App Runner
• Heroku / Railway / Render
• Serverless (Lambda, Cloud Functions)
```

### Проблема 3: "It works on minikube"

```
Local (minikube/kind):           Production (EKS/GKE):
─────────────────────            ─────────────────────
1 node                           3-100+ nodes
Без Ingress                      Ingress + TLS
Без real LoadBalancer            Cloud LoadBalancer
Без network policies             Network segmentation
Без resource limits              Resource quotas
Без PodDisruptionBudgets         High availability

То, что работает локально, может сломаться в production
```

### Проблема 4: Resource limits — двусторонний меч

```yaml
# Слишком низкие limits:
resources:
  limits:
    memory: "64Mi"   # OOMKilled при первом запросе

# Слишком высокие limits:
resources:
  limits:
    memory: "4Gi"    # Один pod занимает всю ноду
    cpu: "4"

# Без limits вообще:
resources: {}        # Pod может убить всю ноду
```

---

## Команды для повседневной работы

```bash
# Информация о кластере
kubectl cluster-info              # API server URL, CoreDNS
kubectl get nodes                 # STATUS: Ready/NotReady, VERSION

# Pods — основные команды
kubectl get pods                  # Список Pod'ов в текущем namespace
kubectl get pods -o wide          # +NODE, IP — на какой ноде, какой IP
kubectl get pods -w               # Watch mode — обновляется в реальном времени
kubectl describe pod <name>       # Полная информация + Events (для debug)
kubectl logs <pod> -f             # -f = follow, как tail -f
kubectl logs <pod> -c <container> # Если в Pod'е несколько контейнеров
kubectl logs <pod> --previous     # Логи ПРЕДЫДУЩЕГО инстанса (после рестарта)

# Deployments
kubectl get deployments           # READY: 3/3, UP-TO-DATE, AVAILABLE
kubectl describe deployment <name>
kubectl rollout status deployment/<name>   # Статус текущего деплоя
kubectl rollout history deployment/<name>  # История ревизий

# Debugging — когда что-то не работает
kubectl get events --sort-by='.lastTimestamp'  # События кластера
kubectl top pods                  # CPU/Memory (требует metrics-server)
kubectl exec -it <pod> -- /bin/sh # Shell в контейнер

# Namespaces — логическая изоляция
kubectl get namespaces            # default, kube-system, kube-public
kubectl get pods -n kube-system   # Системные Pod'ы K8s
kubectl get pods -A               # --all-namespaces, краткая форма
```

**Частые паттерны:**

```bash
# Найти Pod'ы по label
kubectl get pods -l app=my-app

# Удалить Pod (Deployment создаст новый)
kubectl delete pod <name>

# Принудительно рестартнуть Deployment (например, чтобы перечитать Secret)
kubectl rollout restart deployment/<name>

# Посмотреть YAML объекта (как он хранится в etcd)
kubectl get deployment <name> -o yaml

# Применить изменения из stdin
cat deployment.yaml | kubectl apply -f -
```

---

## Actionable

**Начало:**
- Установи minikube или kind локально
- Задеплой простое приложение (nginx)
- Попробуй scale, rollout, rollback

**Следующий шаг:**
- Добавь health probes
- Настрой ConfigMap и Secret
- Попробуй HorizontalPodAutoscaler

**Production:**
- Managed Kubernetes (EKS/GKE/AKS)
- GitOps (ArgoCD/Flux)
- Observability stack

---

## Связи

- Контейнеры для K8s: [[docker-for-developers]]
- Архитектура для K8s: [[microservices-vs-monolith]]
- CI/CD в K8s: [[ci-cd-pipelines]]
- Мониторинг K8s: [[observability]]

---

## Источники

- [Kubernetes Official: Concepts](https://kubernetes.io/docs/concepts/) — проверено 2025-11-24
- [Kubernetes: Configuration Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/) — проверено 2025-11-24
- [CloudZero: Kubernetes Best Practices 2024](https://www.cloudzero.com/blog/kubernetes-best-practices/) — проверено 2025-11-24
- [Plural: Kubernetes Pod Guide 2024](https://www.plural.sh/blog/kubernetes-pod/) — проверено 2025-11-24

---

**Последняя верификация**: 2025-11-24
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*
