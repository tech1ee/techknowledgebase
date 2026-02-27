---
title: "Kubernetes Networking Deep Dive"
created: 2025-01-15
modified: 2026-02-13
tags:
  - topic/networking
  - topic/kubernetes
  - k8s
  - cni
  - service-mesh
  - topic/devops
  - type/deep-dive
  - level/advanced
related:
  - [network-docker-deep-dive]]
  - "[[network-cloud-modern]]"
  - "[[network-observability]"
prerequisites:
  - "[[network-docker-deep-dive]]"
  - "[[network-cloud-modern]]"
  - "[[network-ip-routing]]"
status: published
reading_time: 81
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Kubernetes Networking Deep Dive

---

## Теоретические основы

> **Сетевая модель Kubernetes** основана на трёх фундаментальных требованиях (K8s Networking Model): (1) каждый Pod получает уникальный IP-адрес; (2) любой Pod может связаться с любым другим Pod без NAT (flat network); (3) агенты на ноде могут связаться со всеми Pod на этой ноде. Эта модель формально определена в Kubernetes Design Proposals.

### CNI (Container Network Interface) — формальная архитектура

| Компонент | Роль | Спецификация |
|-----------|------|-------------|
| CNI спецификация | Стандарт интерфейса | CNCF CNI Spec v1.0 (2021) |
| ADD/DEL/CHECK | Операции плагина | Вызываются kubelet при создании/удалении Pod |
| IPAM plugin | Выделение IP-адресов | host-local, dhcp, aws-vpc-cni |
| Chained plugins | Композиция | Несколько плагинов в цепочке (bandwidth, portmap) |

### CNI-плагины: сравнительная таблица

| Плагин | Метод | Overlay | NetworkPolicy | eBPF | Производительность |
|--------|-------|---------|---------------|------|--------------------|
| Flannel | VXLAN / host-gw | Да | Нет | Нет | Базовая |
| Calico | BGP / VXLAN / eBPF | Опционально | Да (L3-L4) | Да (с v3.13) | Высокая |
| Cilium | eBPF native | Опционально | Да (L3-L7) | Да | Очень высокая |
| Weave | VXLAN mesh | Да | Да | Нет | Средняя |
| AWS VPC CNI | Native VPC routing | Нет | Через SG | Нет | Native |

### kube-proxy: режимы работы

- **iptables mode** (по умолчанию) — создаёт цепочки iptables для каждого Service. DNAT перенаправляет трафик на Pod endpoints. Сложность: O(n) правил, обновление при каждом изменении endpoints
- **IPVS mode** — использует IP Virtual Server (хэш-таблица в ядре). O(1) lookup, поддержка алгоритмов балансировки (rr, lc, sh). Рекомендуется при > 1000 Services
- **eBPF replacement** (Cilium) — полностью заменяет kube-proxy, обрабатывая Service routing в eBPF-программах на уровне сокетов

### Типы Service

| Тип | Доступность | Механизм | Когда использовать |
|-----|-------------|----------|-------------------|
| ClusterIP | Только внутри кластера | Virtual IP + kube-proxy | Межсервисная коммуникация |
| NodePort | Внешний доступ через порт ноды | ClusterIP + порт 30000-32767 | Dev/test, простые случаи |
| LoadBalancer | Внешний облачный LB | NodePort + Cloud Controller | Production ingress |
| ExternalName | DNS CNAME | Без проксирования | Внешние сервисы |

> **Flat network model** — каждый Pod получает IP из единого адресного пространства (Pod CIDR), маршрутизируемого между всеми нодами. Это исключает необходимость NAT и port mapping, упрощая service discovery и inter-pod communication. Реализация: underlay (BGP peering между нодами) или overlay (VXLAN-инкапсуляция).

**См. также:** [[network-docker-deep-dive]] (Linux networking примитивы под K8s), [[network-cloud-modern]] (облачная интеграция K8s networking), [[network-observability]] (observability в K8s-кластере)

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Docker networking** | K8s использует контейнеры | [[network-docker-deep-dive]] |
| **IP-адресация** | Pod IP, Service CIDR | [[network-ip-routing]] |
| **Kubernetes basics** | Pods, Services, Deployments | K8s getting started |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ Сначала basics | K8s fundamentals |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | CNI, Network Policies |

### Терминология для новичков

> 💡 **K8s Networking** = как Pods находят друг друга и внешний мир. В K8s нет NAT между подами — каждый Pod имеет уникальный IP.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Pod IP** | Уникальный IP для каждого Pod | **Прямой номер телефона** — звони напрямую |
| **Service** | Стабильный IP для группы Pods | **Номер отдела** — не меняется при смене сотрудников |
| **ClusterIP** | Внутренний IP сервиса | **Внутренний номер** — только для сотрудников |
| **NodePort** | Порт на всех нодах | **Общий вход** — с любого входа попадёшь |
| **LoadBalancer** | Внешний балансировщик | **Ресепшен** — распределяет звонки |
| **Ingress** | HTTP/HTTPS маршрутизация | **Умный секретарь** — по URL направит |
| **CNI** | Container Network Interface | **Телефонная компания** — обеспечивает связь |
| **kube-proxy** | Реализует Services | **АТС** — маршрутизирует звонки |
| **CoreDNS** | DNS для сервисов | **Справочная служба** — имя → IP |
| **Network Policy** | Файрвол для Pods | **Пропускная система** — кого пускать |
| **Service Mesh** | Istio, Linkerd — управление трафиком | **Система видеонаблюдения** — всё видит и контролирует |

---

## Часть 1: Интуиция без кода — Как думать о Kubernetes networking

> **Цель:** Понять, как pods находят друг друга и общаются с внешним миром, через метафоры из реальной жизни. K8s networking сложнее Docker — здесь больше абстракций.

### Аналогия 1: Kubernetes cluster как корпоративный офис

```
KUBERNETES CLUSTER = КОРПОРАТИВНЫЙ ОФИС:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  PODS = СОТРУДНИКИ                                              │
│  ─────────────────────────────────────────────────────────────  │
│  • Каждый сотрудник имеет прямой номер (Pod IP)                 │
│  • Сотрудники могут звонить друг другу напрямую                 │
│  • Сотрудники приходят и уходят (pods эфемерны)                 │
│  • Новый сотрудник = новый номер телефона                       │
│                                                                 │
│  SERVICES = НОМЕРА ОТДЕЛОВ                                      │
│  ─────────────────────────────────────────────────────────────  │
│  • "Позвони в бухгалтерию" (my-service.default.svc)             │
│  • Номер отдела НЕ меняется, даже если сотрудники уходят        │
│  • АТС (kube-proxy) переключает на свободного сотрудника        │
│  • Не нужно знать личные номера — только номер отдела           │
│                                                                 │
│  CNI = ТЕЛЕФОННАЯ КОМПАНИЯ                                      │
│  ─────────────────────────────────────────────────────────────  │
│  • Прокладывает провода (настраивает сеть для pods)             │
│  • Выдаёт номера (IP через IPAM)                                │
│  • Разные провайдеры: Calico, Cilium, Flannel                   │
│  • От провайдера зависит качество связи и функции               │
│                                                                 │
│  COREDNS = СПРАВОЧНАЯ СЛУЖБА                                    │
│  ─────────────────────────────────────────────────────────────  │
│  • "Какой номер у бухгалтерии?" → 10.96.0.15                    │
│  • Знает все отделы (Services) и их номера                      │
│  • Обновляется автоматически при появлении новых сервисов       │
│                                                                 │
│  NETWORK POLICY = ПРОПУСКНАЯ СИСТЕМА                            │
│  ─────────────────────────────────────────────────────────────  │
│  • "Бухгалтерия общается только с HR и директором"              │
│  • По умолчанию ВСЕ могут звонить ВСЕМ                          │
│  • Политики ограничивают — кто с кем может общаться             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему это важно:** В K8s не нужно знать IP конкретного pod — используйте имя Service. Это главное отличие от Docker: абстракция Service делает систему устойчивой к перезапускам pods.

### Аналогия 2: Service как виртуальный ресепшен

```
SERVICE = ВИРТУАЛЬНЫЙ РЕСЕПШЕН:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   КЛИЕНТ                        СЕРВИС                PODS      │
│                                                                 │
│   "Мне нужна                   "Сейчас              ┌────────┐  │
│    бухгалтерия"                 соединю"            │ Pod 1  │  │
│        │                           │                │10.0.1.5│  │
│        │    my-service            │                └────────┘  │
│        │    10.96.0.15            │                            │
│        ▼         │                ▼                ┌────────┐  │
│   ┌─────────────────────────────────────────────┐  │ Pod 2  │  │
│   │                                             │  │10.0.1.6│  │
│   │   ClusterIP: 10.96.0.15                     │  └────────┘  │
│   │                                             │              │
│   │   kube-proxy смотрит: какие pods ready?     │  ┌────────┐  │
│   │   Endpoints: 10.0.1.5, 10.0.1.6, 10.0.2.3   │  │ Pod 3  │  │
│   │                                             │  │10.0.2.3│  │
│   │   Выбирает случайный → направляет трафик    │  └────────┘  │
│   │                                             │              │
│   └─────────────────────────────────────────────┘              │
│                                                                 │
│   ClusterIP — ВИРТУАЛЬНЫЙ IP:                                   │
│   • Не существует на сетевых интерфейсах                        │
│   • Живёт только в iptables/IPVS правилах                       │
│   • kube-proxy на каждой ноде знает: ClusterIP → Pod IPs        │
│                                                                 │
│   ENDPOINT = "Кто сейчас на смене?"                             │
│   • K8s следит: Pod ready? → добавить в endpoints               │
│   • Pod не ready/deleted? → убрать из endpoints                 │
│   • Клиент не замечает — Service всегда отвечает                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему это важно:** ClusterIP — это иллюзия. Реального интерфейса с этим IP нет. kube-proxy перехватывает пакеты к ClusterIP и перенаправляет на реальные pod IP.

### Аналогия 3: Типы Services как способы связи с внешним миром

```
ТИПЫ SERVICES = УРОВНИ ДОСТУПА:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  📞 ClusterIP = ВНУТРЕННИЙ НОМЕР                                │
│  ─────────────────────────────────────────────────────────────  │
│  • Только для сотрудников офиса                                 │
│  • Извне не позвонить                                           │
│  • Для: backend → database, service → service                   │
│  • Самый частый тип (по умолчанию)                              │
│                                                                 │
│  🚪 NodePort = ВХОД С ЛЮБОГО ЭТАЖА                              │
│  ─────────────────────────────────────────────────────────────  │
│  • На каждом этаже (ноде) открыта дверь 30000-32767             │
│  • Войти можно с любого этажа — попадёшь в нужный отдел         │
│  • Минус: нужно знать адрес этажа (Node IP)                     │
│  • Для: dev/test, когда нет LoadBalancer                        │
│                                                                 │
│  🏢 LoadBalancer = ГЛАВНЫЙ РЕСЕПШЕН                             │
│  ─────────────────────────────────────────────────────────────  │
│  • Один внешний адрес для всего офиса                           │
│  • Облачный провайдер выделяет публичный IP                     │
│  • Трафик распределяется по этажам автоматически                │
│  • Для: production, публичные API                               │
│  • Минус: каждый LB стоит денег!                                │
│                                                                 │
│  🎯 Ingress = УМНЫЙ СЕКРЕТАРЬ                                   │
│  ─────────────────────────────────────────────────────────────  │
│  • Один LB, много сервисов                                      │
│  • "api.example.com → отдел API"                                │
│  • "app.example.com → отдел Frontend"                           │
│  • L7 routing: по URL, headers, host                            │
│  • Для: множество HTTP-сервисов за одним IP                     │
│                                                                 │
│  КОГДА ЧТО ИСПОЛЬЗОВАТЬ:                                        │
│  ClusterIP  → внутренняя коммуникация (90% случаев)             │
│  NodePort   → dev/test без cloud LB                             │
│  LoadBalancer → один публичный сервис                           │
│  Ingress    → много HTTP-сервисов за одним IP (экономия)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему это важно:** Ошибка новичка — создавать LoadBalancer для каждого сервиса. Это дорого. Ingress позволяет иметь один LB для всех HTTP-сервисов.

### Аналогия 4: CNI как подрядчик по коммуникациям

```
CNI = ПОДРЯДЧИК, ПРОКЛАДЫВАЮЩИЙ СЕТИ:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Kubernetes говорит: "Мне нужен Pod с сетью"                   │
│   CNI отвечает: "Сделаю!"                                       │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  kubelet создаёт Pod                                    │   │
│   │        │                                                │   │
│   │        ▼                                                │   │
│   │  kubelet вызывает CNI: "Настрой сеть для этого Pod"     │   │
│   │        │                                                │   │
│   │        ▼                                                │   │
│   │  CNI:                                                   │   │
│   │  1. Создаёт network namespace                           │   │
│   │  2. Создаёт veth pair                                   │   │
│   │  3. Выделяет IP (IPAM)                                  │   │
│   │  4. Настраивает routing                                 │   │
│   │        │                                                │   │
│   │        ▼                                                │   │
│   │  Pod готов к работе!                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   РАЗНЫЕ ПОДРЯДЧИКИ — РАЗНЫЕ ВОЗМОЖНОСТИ:                       │
│                                                                 │
│   FLANNEL = БЮДЖЕТНЫЙ ПОДРЯДЧИК                                 │
│   ├── Простая overlay-сеть (VXLAN)                              │
│   ├── Нет Network Policies                                      │
│   └── Для: dev/test, простые кластеры                           │
│                                                                 │
│   CALICO = КОРПОРАТИВНЫЙ ПОДРЯДЧИК                              │
│   ├── BGP routing (без overlay)                                 │
│   ├── Мощные Network Policies                                   │
│   └── Для: production, security-focused                         │
│                                                                 │
│   CILIUM = ИННОВАЦИОННЫЙ ПОДРЯДЧИК                              │
│   ├── eBPF вместо iptables (быстрее)                            │
│   ├── L7 policies (HTTP, gRPC)                                  │
│   ├── Observability из коробки (Hubble)                         │
│   └── Для: modern production, observability                     │
│                                                                 │
│   ⚠️ ВАЖНО: Выбор CNI — архитектурное решение!                  │
│   Менять CNI в работающем кластере — очень сложно.              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему это важно:** CNI — это не просто "плагин для сети". От выбора CNI зависит: поддержка Network Policies, производительность, observability. Flannel НЕ поддерживает Network Policies!

### Аналогия 5: Network Policy как пропускная система

```
NETWORK POLICY = ОХРАНА И ПРОПУСКА:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   БЕЗ NETWORK POLICY (по умолчанию):                            │
│   ─────────────────────────────────────────────────────────     │
│   Все двери открыты. Любой может зайти куда угодно.             │
│   Frontend → Database? Пожалуйста!                              │
│   Random pod → Production secrets? Конечно!                     │
│                                                                 │
│   С DEFAULT DENY:                                               │
│   ─────────────────────────────────────────────────────────     │
│   Все двери заперты. Никто никуда не может.                     │
│   Теперь выдаём пропуска только нужным.                         │
│                                                                 │
│   ┌──────────────────────────────────────────────────────┐      │
│   │                    NAMESPACE: production              │      │
│   │                                                      │      │
│   │  ┌─────────┐      ┌─────────┐      ┌─────────┐       │      │
│   │  │frontend │ ──?──│ backend │ ──?──│database │       │      │
│   │  │  app    │      │   api   │      │  mysql  │       │      │
│   │  └─────────┘      └─────────┘      └─────────┘       │      │
│   │       │                │                │            │      │
│   │       ▼                ▼                ▼            │      │
│   │   INGRESS          INGRESS          INGRESS          │      │
│   │   Policy:          Policy:          Policy:          │      │
│   │   from: ingress    from: frontend   from: backend    │      │
│   │   port: 80         port: 8080       port: 3306       │      │
│   │                                                      │      │
│   └──────────────────────────────────────────────────────┘      │
│                                                                 │
│   РЕЗУЛЬТАТ:                                                    │
│   ✓ ingress → frontend:80      (разрешено)                      │
│   ✓ frontend → backend:8080    (разрешено)                      │
│   ✓ backend → database:3306    (разрешено)                      │
│   ✗ frontend → database:3306   (ЗАБЛОКИРОВАНО!)                 │
│   ✗ random-pod → anything      (ЗАБЛОКИРОВАНО!)                 │
│                                                                 │
│   ⚠️ НЕ ЗАБУДЬ DNS!                                             │
│   При default deny — DNS тоже заблокирован!                     │
│   Нужно явно разрешить egress к kube-dns на порт 53.            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему это важно:** Network Policies — это Zero Trust в K8s. Без них любой скомпрометированный pod может атаковать всё остальное. Default deny + явные разрешения = безопасность.

---

## Часть 2: Почему это сложно — Типичные ошибки в Kubernetes networking

> **Цель:** Научиться распознавать и избегать ловушек, в которые попадают даже опытные K8s-инженеры. Сетевые проблемы в K8s — одни из самых сложных для диагностики.

### Ошибка 1: Network Policy без разрешения DNS

**СИМПТОМ:**
```bash
# Применили default deny
$ kubectl apply -f default-deny.yaml

# Pod перестал резолвить DNS!
$ kubectl exec my-pod -- nslookup my-service
;; connection timed out; no servers could be reached

"Всё сломалось после Network Policy!"
```

**РЕШЕНИЕ:**
```yaml
# ВСЕГДА разрешайте DNS при default deny!
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}  # Все pods в namespace
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

**Правило:** При создании NetworkPolicy первым делом создавайте правило для DNS. Без DNS ничего не работает.

### Ошибка 2: Flannel + NetworkPolicy = не работает

**СИМПТОМ:**
```bash
# Применили NetworkPolicy
$ kubectl apply -f deny-all.yaml
networkpolicy.networking.k8s.io/deny-all created

# Но pods всё ещё общаются!
$ kubectl exec pod-a -- curl pod-b:8080
HTTP/1.1 200 OK

"NetworkPolicy не работает! Баг в Kubernetes!"
```

**РЕШЕНИЕ:**
```bash
# Проверьте CNI
$ kubectl get pods -n kube-system | grep -E "flannel|calico|cilium"
kube-flannel-ds-xxxxx   1/1   Running

# Flannel НЕ ПОДДЕРЖИВАЕТ NetworkPolicy!
# NetworkPolicy применяется, но игнорируется.

# Решение: использовать Calico или Cilium
# Установка Calico поверх Flannel:
$ kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

**Правило:** Перед использованием NetworkPolicy убедитесь, что ваш CNI их поддерживает. Flannel — НЕ поддерживает.

### Ошибка 3: Service без endpoints

**СИМПТОМ:**
```bash
$ kubectl get svc my-service
NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)
my-service   ClusterIP   10.96.0.15     <none>        80/TCP

$ kubectl get endpoints my-service
NAME         ENDPOINTS
my-service   <none>  # ← ПУСТО!

$ kubectl exec debug-pod -- curl my-service:80
# Connection refused или timeout
```

**РЕШЕНИЕ:**
```bash
# Endpoints пусты = selector не матчит pods

# 1. Проверить selector сервиса
$ kubectl describe svc my-service | grep Selector
Selector: app=my-app

# 2. Проверить labels pods
$ kubectl get pods --show-labels
NAME       READY   STATUS    LABELS
my-pod-1   1/1     Running   app=myapp  # ← "myapp" != "my-app"!

# 3. Исправить labels
$ kubectl label pod my-pod-1 app=my-app --overwrite

# Или исправить Service selector
$ kubectl patch svc my-service -p '{"spec":{"selector":{"app":"myapp"}}}'
```

**Правило:** `kubectl get endpoints` — первая команда при проблемах с Service. Пустые endpoints = selector не матчит или pods не Ready.

### Ошибка 4: Хардкодинг Pod IP вместо Service DNS

**СИМПТОМ:**
```python
# config.py
DATABASE_HOST = "10.0.1.5"  # IP конкретного pod

# После рестарта pod:
$ kubectl get pods -o wide
NAME      IP
db-pod    10.0.2.8  # Новый IP!

# Приложение: "Connection refused to 10.0.1.5"
```

**РЕШЕНИЕ:**
```python
# НИКОГДА не хардкодьте Pod IP!

# Правильно: использовать Service DNS
DATABASE_HOST = "db-service"
# или полное имя:
DATABASE_HOST = "db-service.default.svc.cluster.local"

# Для StatefulSet:
# Headless Service + конкретный pod:
DATABASE_HOST = "db-0.db-service.default.svc.cluster.local"
```

```yaml
# Service для database
apiVersion: v1
kind: Service
metadata:
  name: db-service
spec:
  selector:
    app: database
  ports:
    - port: 5432
```

**Правило:** Pod IP эфемерны. Всегда используйте Service DNS. Для StatefulSet используйте Headless Service с предсказуемыми именами.

### Ошибка 5: kube-proxy iptables mode при 1000+ services

**СИМПТОМ:**
```bash
# Первый запрос к сервису — 2-3 секунды latency
# Последующие запросы — нормально

# На нодах высокая CPU load при изменениях в кластере
$ top -b -n1 | grep kube-proxy
kube-proxy   98% CPU  # ← перегружен!

# В логах kube-proxy:
"iptables-restore: slow"
"Syncing iptables rules took 5.2s"
```

**РЕШЕНИЕ:**
```bash
# Проверить режим kube-proxy
$ kubectl get configmap kube-proxy -n kube-system -o yaml | grep mode
mode: ""  # пустое = iptables (default)

# Переключить на IPVS
$ kubectl edit configmap kube-proxy -n kube-system
# Изменить:
mode: "ipvs"

# Перезапустить kube-proxy
$ kubectl rollout restart daemonset kube-proxy -n kube-system

# Проверить
$ kubectl logs -n kube-system -l k8s-app=kube-proxy | grep "Using"
Using ipvs Proxier.  # ✓
```

**Правило:** При > 500 services переключайтесь на IPVS mode. iptables = O(n) lookup, IPVS = O(1).

### Ошибка 6: Ingress без Ingress Controller

**СИМПТОМ:**
```bash
$ kubectl apply -f my-ingress.yaml
ingress.networking.k8s.io/my-ingress created

$ kubectl get ingress
NAME         CLASS    HOSTS           ADDRESS   PORTS
my-ingress   nginx    app.example.com           80  # ← ADDRESS пустой!

$ curl http://app.example.com
# Connection refused
```

**РЕШЕНИЕ:**
```bash
# Ingress — это только МАНИФЕСТ. Нужен Controller!

# Проверить наличие Ingress Controller
$ kubectl get pods -n ingress-nginx
No resources found  # ← Controller не установлен!

# Установить nginx-ingress
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml

# Теперь ADDRESS появится
$ kubectl get ingress
NAME         CLASS    HOSTS           ADDRESS        PORTS
my-ingress   nginx    app.example.com 203.0.113.50   80
```

**Правило:** Ingress resource без Ingress Controller — просто текст в etcd. Controller (nginx, traefik, etc.) делает реальную работу.

---

## Часть 3: Ментальные модели для Kubernetes networking

> **Цель:** Сформировать устойчивые паттерны мышления, которые помогут быстро диагностировать проблемы и принимать архитектурные решения.

### Модель 1: "Четыре уровня коммуникации"

```
K8S NETWORKING = ЧЕТЫРЕ ПРОБЛЕМЫ:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  УРОВЕНЬ 1: CONTAINER-TO-CONTAINER (внутри Pod)                 │
│  ─────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────┐                        │
│  │  POD (общий network namespace)      │                        │
│  │  ┌─────────┐      ┌─────────┐       │                        │
│  │  │Container│◄────►│Container│       │                        │
│  │  │   A     │localhost│  B    │       │                        │
│  │  └─────────┘      └─────────┘       │                        │
│  └─────────────────────────────────────┘                        │
│  Решение: localhost — контейнеры в Pod делят network namespace  │
│                                                                 │
│  УРОВЕНЬ 2: POD-TO-POD (между Pods)                             │
│  ─────────────────────────────────────────────────────────────  │
│  ┌─────────┐                    ┌─────────┐                     │
│  │  Pod A  │◄──── Прямой IP ────►│  Pod B  │                     │
│  │10.0.1.5 │     (без NAT!)     │10.0.2.3 │                     │
│  └─────────┘                    └─────────┘                     │
│  Решение: CNI — каждый pod имеет уникальный routable IP         │
│                                                                 │
│  УРОВЕНЬ 3: POD-TO-SERVICE (к абстракции)                       │
│  ─────────────────────────────────────────────────────────────  │
│  ┌─────────┐      ┌─────────────┐      ┌─────────┐              │
│  │  Pod    │────►│   Service   │────►│  Pod 1  │              │
│  │ Client  │      │ 10.96.0.15  │      │  Pod 2  │              │
│  └─────────┘      └─────────────┘      │  Pod 3  │              │
│  Решение: kube-proxy — DNAT от ClusterIP к Pod IP               │
│                                                                 │
│  УРОВЕНЬ 4: EXTERNAL-TO-SERVICE (из внешнего мира)              │
│  ─────────────────────────────────────────────────────────────  │
│  ┌──────────┐     ┌────────────┐     ┌─────────┐               │
│  │ Internet │────►│LoadBalancer│────►│ Service │               │
│  │          │     │  / Ingress │     │         │               │
│  └──────────┘     └────────────┘     └─────────┘               │
│  Решение: NodePort / LoadBalancer / Ingress                     │
│                                                                 │
│  ОТЛАДКА: Определи на каком уровне проблема!                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Применение:** При проблеме с connectivity определите уровень: container↔container (localhost?), pod↔pod (CNI?), pod↔service (kube-proxy?), external↔service (Ingress/LB?).

### Модель 2: "Service — это iptables/IPVS правила"

```
CLUSTERIP = ВИРТУАЛЬНАЯ МАГИЯ:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ClusterIP 10.96.0.15 — ЭТО НЕ РЕАЛЬНЫЙ ИНТЕРФЕЙС!             │
│                                                                 │
│   $ ip addr | grep 10.96  # Ничего не найдётся                  │
│                                                                 │
│   Это правило в iptables/IPVS:                                  │
│                                                                 │
│   iptables mode:                                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ -A KUBE-SERVICES -d 10.96.0.15/32 -p tcp --dport 80     │   │
│   │   -j KUBE-SVC-XXXX                                      │   │
│   │                                                         │   │
│   │ -A KUBE-SVC-XXXX -m statistic --mode random             │   │
│   │   --probability 0.333 -j KUBE-SEP-POD1                  │   │
│   │ -A KUBE-SVC-XXXX -m statistic --mode random             │   │
│   │   --probability 0.500 -j KUBE-SEP-POD2                  │   │
│   │ -A KUBE-SVC-XXXX -j KUBE-SEP-POD3                       │   │
│   │                                                         │   │
│   │ -A KUBE-SEP-POD1 -j DNAT --to-destination 10.0.1.5:8080 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   IPVS mode:                                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ $ ipvsadm -Ln                                           │   │
│   │ TCP  10.96.0.15:80 rr                                   │   │
│   │   -> 10.0.1.5:8080    Masq  1  0  0                     │   │
│   │   -> 10.0.1.6:8080    Masq  1  0  0                     │   │
│   │   -> 10.0.2.3:8080    Masq  1  0  0                     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   СЛЕДСТВИЕ:                                                    │
│   • ping ClusterIP — работает (ICMP обрабатывается)             │
│   • curl ClusterIP:port — работает (DNAT к pod)                 │
│   • Но интерфейса с этим IP нет!                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Применение:** Service работает через kube-proxy правила. Если Service недоступен — проверьте endpoints (pods ready?) и iptables/ipvs правила.

### Модель 3: "DNS иерархия в K8s"

```
DNS РЕЗОЛВИНГ В KUBERNETES:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Pod делает запрос: "my-service"                               │
│          │                                                      │
│          ▼                                                      │
│   /etc/resolv.conf в Pod:                                       │
│   ┌───────────────────────────────────────────────────────┐     │
│   │ nameserver 10.96.0.10  ← CoreDNS ClusterIP            │     │
│   │ search default.svc.cluster.local svc.cluster.local    │     │
│   │        cluster.local                                  │     │
│   │ ndots: 5                                              │     │
│   └───────────────────────────────────────────────────────┘     │
│          │                                                      │
│          ▼                                                      │
│   ПОИСК ПО ЦЕПОЧКЕ (search domains):                            │
│                                                                 │
│   1. my-service.default.svc.cluster.local  ← НАЙДЕНО! ✓         │
│   2. my-service.svc.cluster.local                               │
│   3. my-service.cluster.local                                   │
│   4. my-service (external DNS)                                  │
│                                                                 │
│   DNS ФОРМАТЫ:                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Service:                                                │   │
│   │ my-service                         (в том же namespace) │   │
│   │ my-service.other-ns                (в другом namespace) │   │
│   │ my-service.other-ns.svc.cluster.local (FQDN)           │   │
│   │                                                         │   │
│   │ Pod (редко нужно):                                      │   │
│   │ 10-0-1-5.default.pod.cluster.local                      │   │
│   │                                                         │   │
│   │ Headless Service (StatefulSet):                         │   │
│   │ pod-0.my-service.default.svc.cluster.local              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ПРОБЛЕМА ndots:5                                              │
│   "google.com" имеет < 5 точек → сначала пробует search domains │
│   Это медленно! Решение: FQDN с точкой: "google.com."           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Применение:** Используйте короткое имя (my-service) в том же namespace, полное имя (my-service.other-ns) для cross-namespace. Для внешних доменов — FQDN с точкой.

### Модель 4: "Дерево выбора способа доступа"

```
КАК ПОЛУЧИТЬ ДОСТУП К СЕРВИСУ?
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              Откуда идёт трафик?                                │
│                    │                                            │
│         ┌─────────┴─────────┐                                   │
│         ▼                   ▼                                   │
│   Из кластера         Извне кластера                            │
│         │                   │                                   │
│         ▼                   ▼                                   │
│    ClusterIP          HTTP/HTTPS?                               │
│   (по умолчанию)            │                                   │
│                    ┌────────┴────────┐                          │
│                    ▼                 ▼                          │
│                   Да                Нет                         │
│                    │                 │                          │
│                    ▼                 ▼                          │
│               Ingress         Нужен ли LB?                      │
│              (экономия)             │                           │
│                            ┌────────┴────────┐                  │
│                            ▼                 ▼                  │
│                      Cloud есть?        Нет cloud               │
│                            │                 │                  │
│                            ▼                 ▼                  │
│                      LoadBalancer       NodePort                │
│                                                                 │
│  ПРИМЕРЫ:                                                       │
│  ─────────────────────────────────────────────────────────────  │
│  backend → database          → ClusterIP                        │
│  frontend → api              → ClusterIP                        │
│  users → web app (HTTP)      → Ingress                          │
│  users → TCP service         → LoadBalancer                     │
│  dev testing                 → NodePort                         │
│  gRPC service                → LoadBalancer / Ingress (L7)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Применение:** 90% сервисов — ClusterIP. Ingress для HTTP. LoadBalancer только когда Ingress не подходит (TCP/UDP, специальные требования).

### Модель 5: "Troubleshooting checklist"

```
ДИАГНОСТИКА K8S NETWORKING — ПОШАГОВЫЙ ЧЕКЛИСТ:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ШАГ 1: PODS RUNNING?                                           │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl get pods -o wide                                     │
│  • Все ли pods в Running?                                       │
│  • На каких нодах? (cross-node networking?)                     │
│                                                                 │
│  ШАГ 2: ENDPOINTS ЕСТЬ?                                         │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl get endpoints my-service                             │
│  • Endpoints пустые? → selector не матчит или pods не Ready     │
│  • Endpoints есть? → Service работает, проблема в другом        │
│                                                                 │
│  ШАГ 3: DNS РАБОТАЕТ?                                           │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl exec debug-pod -- nslookup my-service                │
│  • Timeout? → CoreDNS перегружен или NetworkPolicy блокирует    │
│  • NXDOMAIN? → Service не существует или не в том namespace     │
│                                                                 │
│  ШАГ 4: CONNECTIVITY ЕСТЬ?                                      │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl exec debug-pod -- curl my-service:port               │
│  • Connection refused? → Pod не слушает или не на том порту     │
│  • Timeout? → NetworkPolicy или CNI проблема                    │
│                                                                 │
│  ШАГ 5: NETWORK POLICY?                                         │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl get networkpolicy -n <namespace>                     │
│  • Есть deny policy? → Проверьте allow rules                    │
│  • CNI поддерживает? → Flannel не поддерживает!                 │
│                                                                 │
│  ШАГ 6: ГЛУБОКАЯ ДИАГНОСТИКА                                    │
│  ─────────────────────────────────────────────────────────────  │
│  $ kubectl run debug --image=nicolaka/netshoot -it --rm -- bash │
│  • tcpdump -i any port <port>                                   │
│  • ip route                                                     │
│  • iptables -L -n -v                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Применение:** Идите по шагам сверху вниз. 80% проблем находятся на шагах 1-3: pods не Ready, endpoints пустые, DNS не работает.

---

## Почему это важно

Kubernetes networking — одна из самых сложных тем в cloud-native. Правильное понимание позволяет:

- **Диагностировать** "pod не видит сервис" за минуты, а не часы
- **Безопасность** — изолировать workloads через Network Policies
- **Performance** — выбрать правильный CNI и kube-proxy mode
- **Масштабирование** — понимать ограничения при 1000+ сервисах

### Типичные проблемы

| Симптом | Возможная причина |
|---------|------------------|
| Pod не резолвит DNS | CoreDNS перегружен / NetworkPolicy блокирует |
| Service недоступен | kube-proxy не синхронизировал endpoints |
| Высокая latency | Overlay network overhead / неправильный CNI |
| Ingress 502 | Backend pods не ready / NetworkPolicy |

---

## Kubernetes Networking Model

### Четыре проблемы, которые решает K8s

1. **Container-to-Container** — решено через Pod (общий network namespace)
2. **Pod-to-Pod** — CNI plugin (каждый pod имеет уникальный IP)
3. **Pod-to-Service** — kube-proxy (iptables/IPVS)
4. **External-to-Service** — Ingress / LoadBalancer

### Фундаментальные правила

> 1. Каждый Pod получает **уникальный IP**
> 2. Pods общаются напрямую **без NAT**
> 3. Nodes могут общаться с Pods **без NAT**
> 4. IP который Pod видит у себя = IP который видят другие

```
┌──────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                     │
│                                                              │
│  ┌─────────────┐         ┌─────────────┐                     │
│  │   Node A    │         │   Node B    │                     │
│  │             │         │             │                     │
│  │ ┌─────────┐ │         │ ┌─────────┐ │                     │
│  │ │  Pod 1  │ │◄───────►│ │  Pod 3  │ │                     │
│  │ │10.0.1.5 │ │  Direct │ │10.0.2.3 │ │                     │
│  │ └─────────┘ │  (no NAT)│ └─────────┘ │                     │
│  │             │         │             │                     │
│  │ ┌─────────┐ │         │ ┌─────────┐ │                     │
│  │ │  Pod 2  │ │         │ │  Pod 4  │ │                     │
│  │ │10.0.1.6 │ │         │ │10.0.2.4 │ │                     │
│  │ └─────────┘ │         │ └─────────┘ │                     │
│  └─────────────┘         └─────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Container Network Interface (CNI)

### Почему CNI, а не встроенный networking

**Kubernetes намеренно не реализует networking.** Это архитектурное решение: разные среды требуют разных сетевых решений. AWS хочет интеграцию с VPC. On-prem хочет BGP. Разработчики хотят простоту.

**CNI — это контракт:** "Дай мне network namespace, я настрою ему сеть". Kubernetes знает только этот интерфейс, не детали реализации.

**Почему это важно для вас:**
- Выбор CNI влияет на производительность, безопасность, observability
- Не все CNI поддерживают NetworkPolicy
- Миграция между CNI — сложная операция

### Как работает CNI

Kubernetes **не реализует** networking сам. Он делегирует это **CNI plugin**.

```
kubelet создаёт Pod
        ↓
kubelet вызывает CNI плагин
        ↓
CNI создаёт network namespace
        ↓
CNI выделяет IP через IPAM
        ↓
CNI создаёт veth pair
        ↓
Pod готов к работе
```

### Популярные CNI плагины

| CNI | Особенности | Когда использовать |
|-----|-------------|-------------------|
| **Flannel** | Простой, легковесный | Dev/test, маленькие кластеры |
| **Calico** | Network Policies, BGP, enterprise | Production, security-focused |
| **Cilium** | eBPF, L7 policies, observability | Modern production, eBPF-ready |
| **Weave** | Mesh networking, encryption | Multi-cloud, простота |
| **AWS VPC CNI** | Native AWS networking | EKS production |

### Сравнение производительности (2024)

Benchmark на 40Gbit сети:

| CNI | Throughput | CPU Usage | Latency Overhead |
|-----|-----------|-----------|------------------|
| **Cilium** | 28.5 Gbps | Низкий (10%) | +20-30% |
| **Calico** | 22.1 Gbps | Высокий (25%) | +25-35% |
| **Flannel** | ~22 Gbps | Низкий (10%) | +15-25% |

### Рекомендации

- **Маленький кластер, простота:** Flannel
- **Production, security:** Calico
- **Modern, eBPF, observability:** Cilium

---

## Services и kube-proxy

### Проблема, которую решают Services

**Pod IP эфемерны.** Pod умер → новый pod с другим IP. Нельзя хардкодить IP в конфигах. Нужна абстракция — стабильный адрес для группы pods.

**Service — это виртуальный load balancer.** Один IP (ClusterIP), за которым скрывается группа pods. Kubernetes автоматически:
- Следит за появлением/исчезновением pods (через labels)
- Обновляет endpoints
- Балансирует трафик между pods

**kube-proxy — реализация этой магии.** На каждой ноде kube-proxy программирует правила (iptables/IPVS), чтобы трафик на ClusterIP попадал на реальные pod IP.

### ClusterIP — базовый Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

Service получает **виртуальный IP (VIP)** — он не существует на интерфейсах, только в iptables/IPVS.

### kube-proxy modes

| Mode | Механизм | Performance | Когда использовать |
|------|----------|-------------|-------------------|
| **iptables** (default) | NAT rules | O(n) | < 1000 services |
| **IPVS** | Hash table | O(1) | > 1000 services |
| **nftables** (new) | Modern iptables | O(1) | Modern kernels |

### iptables mode

```bash
# Просмотр Service rules
iptables -t nat -L KUBE-SERVICES -n

# Пример chain для service
# KUBE-SVC-XXX → random selection → KUBE-SEP-YYY (endpoint)
```

**Проблема:** При 1000+ services traversal iptables chains занимает секунды!

### IPVS mode

```bash
# Включение IPVS
# kube-proxy --proxy-mode=ipvs

# Просмотр IPVS правил
ipvsadm -L -n

# Преимущества IPVS:
# - O(1) lookup через hash table
# - Множество алгоритмов балансировки
# - Лучше для > 1000 services
```

**Load balancing алгоритмы IPVS:**
- `rr` — Round Robin
- `lc` — Least Connections
- `sh` — Source Hashing
- `sed` — Shortest Expected Delay

---

## DNS и CoreDNS

### Как работает DNS в K8s

```
Pod делает запрос: my-service.default.svc.cluster.local
        ↓
/etc/resolv.conf → nameserver 10.96.0.10 (CoreDNS ClusterIP)
        ↓
CoreDNS смотрит в K8s API → находит Service IP
        ↓
Возвращает ClusterIP сервиса
```

### DNS форматы

| Ресурс | DNS формат |
|--------|-----------|
| Service | `<service>.<namespace>.svc.cluster.local` |
| Pod | `<pod-ip-dashed>.<namespace>.pod.cluster.local` |
| Headless Service | `<pod-name>.<service>.<namespace>.svc.cluster.local` |

### CoreDNS ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
        }
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

### Включение логирования

```yaml
# Добавить в Corefile
log    # логировать все запросы
```

```bash
# Перезапуск CoreDNS
kubectl -n kube-system rollout restart deployment coredns
```

### Troubleshooting DNS

```bash
# 1. Проверить CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 2. Проверить логи
kubectl logs -n kube-system -l k8s-app=kube-dns

# 3. Тестовый pod для диагностики
kubectl run -it --rm debug --image=nicolaka/netshoot -- \
    nslookup kubernetes.default

# 4. Проверить DNS из проблемного pod
kubectl exec my-pod -- nslookup my-service

# 5. CPU CoreDNS (перегрузка?)
kubectl top pods -n kube-system -l k8s-app=kube-dns
```

---

## Network Policies

### Зачем нужны

> По умолчанию K8s **не изолирует** pods. Любой pod может общаться с любым.

Network Policy — декларативный firewall для pods.

### Пример: Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}  # Все pods в namespace
  policyTypes:
    - Ingress
    - Egress
```

После применения — **весь трафик заблокирован**. Теперь разрешаем только нужное.

### Пример: Разрешить ingress от frontend к backend

```yaml
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
```

### Пример: Разрешить DNS (обязательно!)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
        - podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### Best Practices

1. **Default deny** — начни с блокировки всего
2. **Allow minimum required** — открывай только нужное
3. **Всегда разрешай DNS** — иначе service discovery не работает
4. **Используй labels** — не IP адреса (pods эфемерны)
5. **Тестируй в staging** — NetworkPolicy может "отключить" приложение

### CNI поддержка

> **Flannel НЕ поддерживает** NetworkPolicy!
> Используй Calico, Cilium, или Weave.

---

## Service Mesh

### Что это и зачем

Service Mesh добавляет L7 capabilities:
- **mTLS** между сервисами
- **Observability** — distributed tracing
- **Traffic management** — canary, A/B
- **Retries, timeouts** — circuit breaking

### Сравнение (2024)

| Mesh | Архитектура | Performance | Сложность |
|------|-------------|-------------|-----------|
| **Linkerd** | Rust sidecar | Лучшая (33% overhead) | Простая |
| **Istio** | Envoy sidecar | Средняя (166% mTLS overhead) | Сложная |
| **Cilium Mesh** | eBPF (sidecarless) | Хорошая (no sidecar overhead) | Средняя |

### Когда использовать

**Используй Service Mesh если:**
- Нужен mTLS между сервисами
- Требуется observability без изменения кода
- Сложные traffic patterns (canary, traffic splitting)

**Не используй если:**
- Маленький кластер (< 20 сервисов)
- Простые stateless workloads
- Нет ресурсов на операционную сложность

### Пример: Istio VirtualService

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
    - my-app
  http:
    - route:
        - destination:
            host: my-app
            subset: v1
          weight: 90
        - destination:
            host: my-app
            subset: v2
          weight: 10
```

---

## Ingress и Gateway API

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
```

### Gateway API (современная альтернатива)

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-route
spec:
  parentRefs:
    - name: my-gateway
  hostnames:
    - "app.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-service
          port: 80
```

**Gateway API преимущества:**
- Более выразительный
- Разделение ответственности (Gateway vs Route)
- Поддержка TCP/UDP, gRPC

---

## Troubleshooting

### Диагностика pod-to-pod

```bash
# 1. Pods на одной ноде или разных?
kubectl get pods -o wide

# 2. Проверить connectivity
kubectl exec pod-a -- ping <pod-b-ip>
kubectl exec pod-a -- curl http://<pod-b-ip>:8080

# 3. Проверить endpoints сервиса
kubectl get endpoints my-service

# 4. Описание сервиса
kubectl describe svc my-service
```

### Диагностика Service

```bash
# 1. Service существует?
kubectl get svc my-service

# 2. Endpoints привязаны?
kubectl get endpoints my-service
# Если пусто — selector не матчит pods!

# 3. Проверить selector
kubectl describe svc my-service | grep Selector

# 4. Проверить labels pods
kubectl get pods --show-labels
```

### Диагностика DNS

```bash
# Debug pod
kubectl run -it --rm debug --image=nicolaka/netshoot -- bash

# Внутри:
nslookup my-service
nslookup my-service.default.svc.cluster.local
dig my-service.default.svc.cluster.local

# Проверить resolv.conf
cat /etc/resolv.conf
```

### Network Policy debugging

```bash
# Проверить применённые policies
kubectl get networkpolicy -A

# Детали policy
kubectl describe networkpolicy my-policy

# Тест connectivity
kubectl exec pod-a -- nc -zv pod-b 8080

# Если Cilium — использовать Hubble
hubble observe --from-pod default/pod-a --to-pod default/pod-b
```

### Полезные инструменты

| Инструмент | Назначение |
|------------|-----------|
| **netshoot** | Swiss-army knife для networking |
| **kubectl debug** | Ephemeral debug containers |
| **Hubble (Cilium)** | Network observability |
| **tcpdump** | Packet capture |

---

## Подводные камни

### 1. Flannel + NetworkPolicy = не работает

Flannel **не поддерживает** NetworkPolicy. Применение policy ничего не сделает.

**Решение:** Используй Calico или Cilium.

### 2. NetworkPolicy без DNS egress

```yaml
# Заблокировали весь egress, забыли DNS
spec:
  policyTypes:
    - Egress
  egress: []  # Пусто = всё заблокировано, включая DNS!
```

**Решение:** Всегда разрешай UDP/TCP 53 к kube-dns.

### 3. Service без endpoints

```bash
kubectl get svc my-service
# EXTERNAL-IP: <pending> или Endpoints: <none>
```

**Причины:**
- Selector не матчит labels pods
- Pods не в состоянии Ready
- Pods в другом namespace

### 4. Pod IP меняется

Pods эфемерны — их IP меняется при пересоздании.

**Решение:** Никогда не хардкодь Pod IP. Используй Service DNS.

### 5. Headless Service для StatefulSet

```yaml
spec:
  clusterIP: None  # Headless
```

Для StatefulSet нужен Headless Service, чтобы каждый pod имел стабильный DNS.

### 6. kube-proxy iptables при 1000+ services

При большом количестве services iptables mode вызывает:
- Высокую latency при первом подключении
- CPU spikes при обновлении rules

**Решение:** Переключись на IPVS mode.

### 7. CoreDNS throttling

CoreDNS может стать bottleneck при высокой нагрузке.

**Признаки:**
- Высокий CPU у CoreDNS pods
- DNS timeout ошибки

**Решение:**
```bash
kubectl scale deployment coredns -n kube-system --replicas=5
```

---

## Чек-лист

### Production readiness

- [ ] CNI поддерживает NetworkPolicy (не Flannel)
- [ ] Default deny NetworkPolicy в каждом namespace
- [ ] DNS egress разрешён
- [ ] kube-proxy mode = IPVS (если > 500 services)
- [ ] CoreDNS scaled appropriately
- [ ] Ingress/Gateway настроен с TLS

### Troubleshooting

- [ ] `kubectl get endpoints` — endpoints привязаны?
- [ ] `kubectl exec ... nslookup` — DNS работает?
- [ ] `kubectl get networkpolicy` — не блокирует?
- [ ] `kubectl logs -n kube-system -l k8s-app=kube-dns` — ошибки CoreDNS?

---

## Связанные материалы

- [[network-docker-deep-dive]] — Docker networking, namespaces
- [[network-security-fundamentals]] — Zero Trust, firewall
- [[network-observability]] — Distributed tracing, metrics
- [[network-cloud-modern]] — Cloud-native patterns
- [[network-troubleshooting-advanced]] — Диагностика проблем

---

## Источники

### Теоретические основы
- CNCF CNI Specification v1.0 (2021). Container Network Interface — стандарт сетевого интерфейса для контейнеров
- Kubernetes Design Proposals: Networking Model — формальное определение требований к сетевой модели K8s
- RFC 7348 (2014). VXLAN — основа overlay-сетей в Flannel, Weave
- Rizzo L. (2012). "netmap: A Novel Framework for Fast Packet I/O" — USENIX ATC (основа высокопроизводительного packet processing)

### Практические руководства

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [K8s Cluster Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/) | Docs | Official networking concepts |
| 2 | [K8s Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) | Docs | Policy specification |
| 3 | [K8s DNS Debugging](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/) | Docs | DNS troubleshooting |
| 4 | [Tigera kube-proxy Comparison](https://www.tigera.io/blog/comparing-kube-proxy-modes-iptables-or-ipvs/) | Blog | iptables vs IPVS |
| 5 | [CNI Benchmark 2024](https://itnext.io/benchmark-results-of-kubernetes-network-plugins-cni-over-40gbit-s-network-2024-156f085a5e4e) | Blog | CNI performance |
| 6 | [Cilium vs Calico vs Flannel](https://www.civo.com/blog/calico-vs-flannel-vs-cilium) | Blog | CNI comparison |
| 7 | [Service Mesh Comparison](https://livewyer.io/blog/service-meshes-decoded-istio-vs-linkerd-vs-cilium/) | Blog | Istio vs Linkerd vs Cilium |
| 8 | [Network Policy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes) | GitHub | Policy examples |
| 9 | [Tigera Network Policy Guide](https://www.tigera.io/learn/guides/kubernetes-security/kubernetes-network-policy/) | Guide | Policy best practices |
| 10 | [Spacelift K8s Networking](https://spacelift.io/blog/kubernetes-networking) | Blog | Architecture overview |
| 11 | [Tetrate CNI Essentials](https://tetrate.io/blog/kubernetes-networking) | Blog | CNI deep dive |
| 12 | [AWS EKS IPVS](https://docs.aws.amazon.com/eks/latest/best-practices/ipvs.html) | Docs | IPVS in production |
| 13 | [Ground Cover DNS Issues](https://www.groundcover.com/kubernetes-troubleshooting/dns-issues) | Blog | DNS troubleshooting |
| 14 | [Buoyant Linkerd vs Istio](https://www.buoyant.io/linkerd-vs-istio) | Blog | Service mesh comparison |
| 15 | [Container Solutions Debugging](https://blog.container-solutions.com/debugging-kubernetes-networking) | Blog | Practical troubleshooting |

---

## Связь с другими темами

**[[network-docker-deep-dive]]** — Docker networking является фундаментом для понимания Kubernetes networking: каждый Pod работает в сетевом namespace аналогично контейнеру, а CNI-плагины используют те же Linux-примитивы (veth pairs, bridges, iptables), что и Docker. Без понимания Docker networking невозможно диагностировать проблемы на уровне Pod-to-Pod коммуникации или понять, как CNI-плагин создаёт сетевую связность. Обязательно изучите Docker networking перед Kubernetes.

**[[network-cloud-modern]]** — Kubernetes в облаке (EKS, GKE, AKS) интегрируется с облачными сетевыми сервисами: LoadBalancer Service создаёт облачный Load Balancer, Ingress может использовать ALB/NLB, а CNI-плагины (aws-vpc-cni) выделяют Pod IP из VPC subnet. Понимание облачных сетей необходимо для проектирования production-grade Kubernetes-кластеров и корректной настройки сетевой изоляции. Изучайте параллельно с K8s networking.

**[[network-observability]]** — Наблюдаемость сети в Kubernetes реализуется через специализированные инструменты: Cilium Hubble для eBPF-based мониторинга, Jaeger/Zipkin для distributed tracing через service mesh, Prometheus для сбора сетевых метрик. Kubernetes networking генерирует сложные паттерны трафика (east-west, north-south), которые невозможно диагностировать без правильно настроенной observability. Рекомендуется изучать observability после понимания основ K8s networking.

---

## Источники и дальнейшее чтение

### Теоретические основы
- **Tanenbaum, Wetherall (2011).** *Computer Networks.* — фундаментальные сетевые принципы, без которых невозможно понять, как CNI-плагины реализуют overlay и underlay сети в Kubernetes.
- **Kurose, Ross (2021).** *Computer Networking: A Top-Down Approach.* — современный учебник с покрытием SDN и виртуализации сетей, что напрямую применимо к пониманию сетевой модели Kubernetes.

### Практические руководства
- **Peterson, Davie (2011).** *Computer Networks: A Systems Approach.* — системный подход к сетевой архитектуре, включая виртуальные сети и туннелирование (VXLAN, GRE), которые используют CNI-плагины для pod-to-pod коммуникации между нодами.
- **Burns B. et al. (2019).** *Kubernetes Up & Running.* — практическое руководство по K8s с главами о networking, Services и Ingress.

---

---

## Проверь себя

> [!question]- NetworkPolicy запрещает весь egress-трафик из namespace, и приложение не может резолвить DNS-имена. Почему и как исправить?
> NetworkPolicy по умолчанию блокирует весь трафик, не указанный в правилах. DNS использует UDP/TCP порт 53 к kube-dns (CoreDNS) в namespace kube-system. Нужно явно добавить egress-правило, разрешающее трафик на порт 53 UDP/TCP к pods с label k8s-app: kube-dns. Это самая частая ошибка при внедрении NetworkPolicy.

> [!question]- Почему Flannel как CNI не поддерживает NetworkPolicy, и что использовать вместо?
> Flannel --- простой overlay-сетевой плагин, который обеспечивает только L3-связность между подами. NetworkPolicy требует программируемой фильтрации пакетов, которую Flannel не реализует. Альтернативы: Calico (eBPF/iptables-based policies), Cilium (eBPF), или комбинация Flannel + Calico (Canal).

> [!question]- При масштабировании до 5000 Services kube-proxy в режиме iptables создаёт заметную задержку. В чём причина и решение?
> kube-proxy в iptables mode создаёт O(n) правил: для каждого Service цепочка с DNAT-правилами. При 5000 Services тысячи правил, обновление занимает секунды. Решение: переключить kube-proxy на IPVS mode (O(1) lookup через хэш-таблицу) или использовать Cilium, который заменяет kube-proxy через eBPF.

---

## Ключевые карточки

Какие четыре типа Service существуют в K8s?
?
ClusterIP --- внутренний виртуальный IP, доступен только внутри кластера. NodePort --- ClusterIP + порт на каждой ноде (30000-32767). LoadBalancer --- NodePort + внешний облачный балансировщик. ExternalName --- CNAME-alias на внешний DNS-имя без проксирования.

Что такое CNI и какие плагины бывают?
?
CNI (Container Network Interface) --- стандарт для настройки сети контейнеров. Плагины: Flannel (простой overlay), Calico (BGP + NetworkPolicy), Cilium (eBPF, L7 policies, observability), Weave (mesh overlay). CNI отвечает за IP-выделение и связность pod-to-pod.

Как работает DNS в Kubernetes?
?
CoreDNS --- кластерный DNS. Иерархия: pod-name.namespace.svc.cluster.local. Service "my-svc" в namespace "default" резолвится как my-svc.default.svc.cluster.local. Поды автоматически настроены использовать ClusterIP CoreDNS. Headless Service (clusterIP: None) возвращает IP подов напрямую.

Что такое NetworkPolicy?
?
NetworkPolicy --- K8s-ресурс для контроля трафика на уровне L3/L4. Определяет ingress/egress правила для подов по labels, namespaces, IP-блокам. По умолчанию всё разрешено. Первая NetworkPolicy, выбирающая под, делает остальной неуказанный трафик запрещённым (default deny).

Чем Ingress отличается от Service LoadBalancer?
?
LoadBalancer --- L4, один внешний IP на один Service, платный в облаке. Ingress --- L7, один внешний IP + маршрутизация по host/path к множеству Services. Ingress дешевле (один LoadBalancer), поддерживает TLS termination, виртуальные хосты, path-based routing.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[network-cloud-modern]] | VPC, Load Balancers, CDN в облаке |
| Углубиться | [[network-observability]] | Мониторинг и трассировка сетевого трафика в K8s |
| Смежная тема | [[network-docker-deep-dive]] | Docker networking как основа K8s networking |
| Обзор | [[networking-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-01-09 --- Добавлены педагогические секции: 5 аналогий (K8s cluster, Service, типы Services, CNI, Network Policy), 6 типичных ошибок с СИМПТОМ/РЕШЕНИЕ, 5 ментальных моделей*
