---
title: "Backend Engineer: интерливинг-путь обучения"
created: 2026-02-14
modified: 2026-02-14
type: guide
tags:
  - type/guide
  - navigation
  - learning-path
---

# Backend Engineer: интерливинг-путь обучения

> **Принцип интерливинга:** вместо изучения одной темы блоком, мы чередуем домены каждый день. Мозг формирует более прочные связи между смежными концепциями, когда вынужден переключаться между контекстами. Это сложнее, но эффективнее для долгосрочного запоминания.

---

## Как использовать этот путь

**Ежедневный план:**
- Читай **2-3 файла в день** (~60-90 минут)
- Чередуй домены: не читай два файла из одной области подряд
- На Review Day — пересмотри заметки за неделю, запиши связи между темами
- Отмечай `- [x]` после завершения каждого файла

**Домены и цветовая маркировка:**
- `[ARCH]` — Архитектура и API
- `[DB]` — Базы данных
- `[SEC]` — Безопасность и аутентификация
- `[OPS]` — DevOps
- `[CLD]` — Облачные платформы
- `[NET]` — Сетевые технологии

**Общая длительность:** ~8-9 недель (5 дней/неделю, 60-90 мин/день)

---

## Неделя 1: Фундамент — API, данные, безопасность, DevOps

> Цель: заложить основы во всех шести доменах. К концу недели — понимание REST API, реляционных БД, базовой безопасности и Git-процессов.

**День 1** (~70 мин)
- [ ] `[ARCH]` [[api-design]] — проектирование API: принципы, версионирование, документация ⏱ 30m
- [ ] `[DB]` [[databases-fundamentals-complete]] — модели данных, CAP-теорема, нормализация ⏱ 41m

**День 2** (~63 мин)
- [ ] `[SEC]` [[security-fundamentals]] — CIA-триада, Defense in Depth, threat landscape ⏱ 34m
- [ ] `[DB]` [[databases-sql-fundamentals]] — SQL: SELECT, JOIN, индексы, оптимизация запросов ⏱ 29m

**День 3** (~60 мин)
- [ ] `[ARCH]` [[api-rest-deep-dive]] — REST: HATEOAS, идемпотентность, коды ответов, пагинация ⏱ 40m
- [ ] `[NET]` [[network-fundamentals-for-developers]] — OSI/TCP-IP модель, пакеты, маршрутизация ⏱ 20m

**День 4** (~56 мин)
- [ ] `[OPS]` [[git-workflows]] — Git Flow, Trunk-Based, стратегии ветвления ⏱ 12m
- [ ] `[OPS]` [[ci-cd-pipelines]] — CI/CD: GitHub Actions, Jenkins, стадии пайплайна ⏱ 13m
- [ ] `[SEC]` [[auth-sessions-jwt-tokens]] — сессии, JWT, refresh tokens, хранение ⏱ 31m

**День 5** — Review
- [ ] :memo: **Review Day:** пересмотри заметки Недели 1. Запиши в заметку: как связаны API-дизайн и SQL-запросы? Зачем JWT при проектировании REST?

---

## Неделя 2: Углубление — контейнеры, OAuth, транспорт, SQL

> Цель: Docker и контейнеризация, OAuth2 flow, TCP/UDP, продвинутый SQL.

> [!tip] Если у тебя уже есть опыт с Docker и Git
> Можешь пропустить [[git-workflows]], [[ci-cd-pipelines]] и [[docker-for-developers]], но обязательно прочитай [[kubernetes-basics]] на Неделе 3.

**День 1** (~69 мин)
- [ ] `[DB]` [[sql-databases-complete]] — PostgreSQL, MySQL, SQLite: архитектура, сравнение ⏱ 36m
- [ ] `[SEC]` [[auth-oauth2-oidc]] — OAuth 2.0, OIDC: Authorization Code, PKCE, scopes ⏱ 31m

**День 2** (~68 мин)
- [ ] `[ARCH]` [[api-graphql-deep-dive]] — GraphQL: schema, resolvers, N+1, подписки, батчинг ⏱ 40m
- [ ] `[DB]` [[databases-transactions-acid]] — ACID, уровни изоляции, MVCC, deadlock ⏱ 28m

**День 3** (~67 мин)
- [ ] `[OPS]` [[docker-for-developers]] — Docker: образы, контейнеры, Dockerfile, compose ⏱ 16m
- [ ] `[SEC]` [[auth-authorization-models]] — RBAC, ABAC, ReBAC, policy engines ⏱ 31m
- [ ] `[NET]` [[network-transport-layer]] — TCP, UDP, congestion control, flow control ⏱ 20m

**День 4** (~60 мин)
- [ ] `[ARCH]` [[api-grpc-deep-dive]] — gRPC: protobuf, streaming, interceptors, load balancing ⏱ 40m
- [ ] `[CLD]` [[cloud-platforms-essentials]] — облачные модели: IaaS, PaaS, SaaS, multi-cloud ⏱ 15m

**День 5** — Review
- [ ] :memo: **Review Day:** связи между SQL-транзакциями и API-дизайном. Как OAuth2 влияет на архитектуру API? Зачем gRPC, если есть REST?

---

## Неделя 3: Инфраструктура — Kubernetes, NoSQL, HTTP, облако

> Цель: оркестрация контейнеров, NoSQL-модели, эволюция HTTP, AWS.

**День 1** (~73 мин)
- [ ] `[OPS]` [[kubernetes-basics]] — K8s: Pod, Service, Deployment, ConfigMap, архитектура ⏱ 18m
- [ ] `[DB]` [[nosql-databases-complete]] — MongoDB, Redis, Cassandra, DynamoDB: модели данных ⏱ 35m
- [ ] `[NET]` [[network-http-evolution]] — HTTP/1.1, HTTP/2, HTTP/3 (QUIC), сравнение ⏱ 20m

**День 2** (~69 мин)
- [ ] `[ARCH]` [[api-modern-patterns]] — webhooks, SSE, WebSocket, async API, API gateway ⏱ 40m
- [ ] `[DB]` [[databases-nosql-comparison]] — когда что использовать: документные, KV, колоночные, графовые ⏱ 29m

**День 3** (~66 мин)
- [ ] `[SEC]` [[auth-api-service-patterns]] — API keys, mTLS, service mesh auth, machine-to-machine ⏱ 28m
- [ ] `[CLD]` [[cloud-aws-core-services]] — EC2, S3, RDS, Lambda, IAM, VPC ⏱ 20m
- [ ] `[OPS]` [[infrastructure-as-code]] — Terraform, Pulumi, CloudFormation: IaC принципы ⏱ 13m

**День 4** (~61 мин)
- [ ] `[SEC]` [[auth-passwordless-mfa]] — Passkeys, WebAuthn, TOTP, biometrics ⏱ 31m
- [ ] `[ARCH]` [[microservices-vs-monolith]] — монолит, микросервисы, модульный монолит ⏱ 20m

> [!tip] Если ты frontend-инженер, переходящий в backend
> Файлы [[auth-api-service-patterns]] и [[auth-passwordless-mfa]] особенно важны -- они покрывают паттерны, с которыми сталкивается каждый backend.

**День 5** — Review
- [ ] :memo: **Review Day:** как NoSQL vs SQL влияет на выбор архитектуры (монолит vs микросервисы)? Как Kubernetes связан с облачными сервисами?

---

## Неделя 4: Продвинутые паттерны — кэширование, репликация, DNS

> Цель: паттерны кэширования, репликация БД, DNS/TLS, Kubernetes продвинутый.

**День 1** (~75 мин)
- [ ] `[ARCH]` [[caching-strategies]] — кэширование: CDN, Redis, write-through, invalidation ⏱ 55m
- [ ] `[DB]` [[databases-replication-sharding]] — репликация, шардирование, партиционирование ⏱ 20m

**День 2** (~62 мин)
- [ ] `[NET]` [[network-dns-tls]] — DNS: резолвинг, записи, DNSSEC; TLS handshake, сертификаты ⏱ 15m
- [ ] `[SEC]` [[web-security-owasp]] — OWASP Top 10: XSS, CSRF, injection, broken auth ⏱ 9m
- [ ] `[ARCH]` [[technical-debt]] — технический долг: классификация, управление, метрики ⏱ 20m
- [ ] `[OPS]` [[kubernetes-advanced]] — Helm, operators, HPA, сети, storage classes ⏱ 16m

> [!tip] Если кэширование -- твоя слабая сторона
> После [[caching-strategies]] сделай паузу и нарисуй схему: где кэш в типичном backend-приложении? CDN -> API Gateway -> Application cache -> DB query cache.

**День 3** (~72 мин)
- [ ] `[ARCH]` [[event-driven-architecture]] — EDA: Kafka, RabbitMQ, event sourcing, CQRS ⏱ 30m
- [ ] `[DB]` [[database-internals-complete]] — B-Tree, LSM-Tree, WAL, buffer pool, query planner ⏱ 22m
- [ ] `[CLD]` [[cloud-gcp-core-services]] — Compute Engine, GKE, Cloud SQL, BigQuery, Pub/Sub ⏱ 20m

**День 4** (~61 мин)
- [ ] `[SEC]` [[security-https-tls]] — HTTPS: TLS 1.3, certificate pinning, HSTS ⏱ 6m
- [ ] `[NET]` [[network-realtime-protocols]] — WebSocket, SSE, gRPC streaming, MQTT ⏱ 15m
- [ ] `[ARCH]` [[dependency-injection-fundamentals]] — DI: IoC, контейнеры, composition root ⏱ 40m

**День 5** — Review
- [ ] :memo: **Review Day:** как кэширование связано с репликацией БД? Как event-driven архитектура влияет на consistency? Зачем знать DNS при проектировании систем?

---

## Неделя 5: Устойчивость — resilience, мониторинг, криптография

> Цель: паттерны устойчивости, observability, криптография, облачные БД.

**День 1** (~72 мин)
- [ ] `[ARCH]` [[architecture-resilience-patterns]] — Circuit Breaker, Retry, Bulkhead, Timeout, Fallback ⏱ 55m
- [ ] `[DB]` [[databases-backup-recovery]] — стратегии бэкапов: полные, инкрементальные, PITR ⏱ 17m

**День 2** (~60 мин)
- [ ] `[OPS]` [[observability]] — логи, метрики, трейсы: Prometheus, Grafana, OpenTelemetry ⏱ 11m
- [ ] `[DB]` [[databases-monitoring-security]] — мониторинг БД: slow queries, connection pools, алерты ⏱ 19m
- [ ] `[SEC]` [[threat-modeling]] — STRIDE, DREAD, attack trees, threat modeling для API ⏱ 30m

**День 3** (~63 мин)
- [ ] `[ARCH]` [[architecture-rate-limiting]] — rate limiting: token bucket, sliding window, distributed ⏱ 55m
- [ ] `[SEC]` [[security-cryptography-fundamentals]] — симметричная/асимметричная, хеширование, подписи ⏱ 7m

**День 4** (~73 мин)
- [ ] `[CLD]` [[cloud-databases-complete]] — Aurora, Cloud Spanner, DynamoDB, Cosmos DB ⏱ 41m
- [ ] `[DB]` [[database-design-optimization]] — нормализация, денормализация, индексы, partitioning ⏱ 31m

> [!tip] Если ты уже работал с облачными БД
> Сравни свой опыт с материалом в [[cloud-databases-complete]]. Обрати внимание на разницу между managed и serverless БД.

**День 5** — Review
- [ ] :memo: **Review Day:** как resilience-паттерны защищают от каскадных сбоев? Связь между rate limiting и безопасностью API. Как мониторинг БД встраивается в observability-стек?

---

## Неделя 6: Масштабирование — поиск, распределённые системы, сети

> Цель: поисковые системы, распределённые системы, облачные сети, GitOps.

**День 1** (~70 мин)
- [ ] `[ARCH]` [[architecture-search-systems]] — Elasticsearch, полнотекстовый поиск, ranking, шардинг ⏱ 45m
- [ ] `[ARCH]` [[architecture-distributed-systems]] — CAP, consensus, distributed transactions ⏱ 25m

**День 2** (~62 мин)
- [ ] `[OPS]` [[gitops-argocd-flux]] — GitOps: ArgoCD, Flux, декларативная инфраструктура ⏱ 14m
- [ ] `[NET]` [[network-cloud-modern]] — VPC, load balancers, CDN, service mesh networking ⏱ 15m
- [ ] `[SEC]` [[security-secrets-management]] — Vault, AWS Secrets Manager, rotation, envelope encryption ⏱ 9m
- [ ] `[CLD]` [[cloud-serverless-patterns]] — Lambda, Cloud Functions, event-driven serverless ⏱ 15m

**День 3** (~62 мин)
- [ ] `[NET]` [[network-docker-deep-dive]] — Docker networking: bridge, host, overlay, DNS ⏱ 20m
- [ ] `[CLD]` [[cloud-networking-security]] — VPC, Security Groups, WAF, DDoS protection ⏱ 15m
- [ ] `[SEC]` [[security-incident-response]] — playbooks, post-mortem, forensics, communication ⏱ 10m
- [ ] `[DB]` *(повторение)* пересмотри заметки по [[databases-replication-sharding]] в контексте distributed systems ⏱ ~15m

**День 4** (~65 мин)
- [ ] `[NET]` [[network-kubernetes-deep-dive]] — K8s networking: CNI, Ingress, Network Policies, Service Mesh ⏱ 25m
- [ ] `[ARCH]` [[performance-optimization]] — профилирование, bottleneck analysis, latency budgets ⏱ 55m

> [!tip] Связь сетей и инфраструктуры
> Файлы [[network-docker-deep-dive]] и [[network-kubernetes-deep-dive]] лучше читать после [[docker-for-developers]] и [[kubernetes-basics]]. Если ты следуешь этому пути по порядку, у тебя уже есть нужный контекст.

**День 5** — Review
- [ ] :memo: **Review Day:** как distributed systems связаны с CAP и репликацией БД? Как сетевая архитектура (VPC, Service Mesh) влияет на безопасность? Как GitOps меняет процесс деплоя?

---

## Неделя 7: Безопасность в глубину + DevOps + Cloud DR

> Цель: API protection, incident management, disaster recovery, network security.

**День 1** (~60 мин)
- [ ] `[SEC]` [[security-api-protection]] — API security: rate limiting, input validation, WAF rules ⏱ 7m
- [ ] `[NET]` [[network-security-fundamentals]] — firewall, IDS/IPS, VPN, zero trust ⏱ 15m
- [ ] `[CLD]` [[cloud-disaster-recovery]] — RPO/RTO, multi-region, failover, backup стратегии ⏱ 15m

> [!tip] Финальный блок безопасности
> К этому моменту ты прошёл все 13 файлов по безопасности. Сделай сводную заметку: какие паттерны безопасности применяются на каждом уровне (сеть, приложение, данные, инфраструктура)?

**День 2** (~59 мин)
- [ ] `[OPS]` [[devops-incident-management]] — on-call, escalation, post-mortem, SLO/SLA ⏱ 13m
- [ ] `[CLD]` *(повторение)* пересмотри [[cloud-aws-core-services]] и [[cloud-gcp-core-services]] -- сравни подходы к DR ⏱ ~30m

**День 3** — Итоговый Review всех доменов
- [ ] :memo: **Большой Review:** нарисуй mind map или таблицу: как 6 доменов связаны между собой. Ключевые вопросы:
  - Как API-дизайн влияет на выбор БД?
  - Как security-паттерны встраиваются в CI/CD пайплайн?
  - Как облачная инфраструктура влияет на архитектурные решения?
  - Как сетевые знания помогают при отладке production-проблем?

---

## Неделя 8: Интеграция и закрепление

> Эта неделя -- для повторения и построения связей. Нет новых материалов.

**День 1** — Архитектура + БД
- [ ] :memo: Пересмотри: [[api-design]], [[api-rest-deep-dive]], [[api-graphql-deep-dive]], [[api-grpc-deep-dive]]. Составь сравнительную таблицу: когда использовать REST vs GraphQL vs gRPC?
- [ ] :memo: Пересмотри: [[databases-fundamentals-complete]], [[sql-databases-complete]], [[nosql-databases-complete]]. Запиши: как выбор БД зависит от требований к consistency, масштабированию, модели данных?

**День 2** — Безопасность + DevOps
- [ ] :memo: Пересмотри: [[security-fundamentals]], [[auth-sessions-jwt-tokens]], [[auth-oauth2-oidc]], [[auth-authorization-models]]. Нарисуй auth flow для типичного backend-приложения.
- [ ] :memo: Пересмотри: [[docker-for-developers]], [[kubernetes-basics]], [[ci-cd-pipelines]]. Составь чеклист: минимальный DevOps-стек для нового проекта.

**День 3** — Облако + Сети
- [ ] :memo: Пересмотри: [[cloud-platforms-essentials]], [[cloud-aws-core-services]], [[cloud-gcp-core-services]]. Сравни: какие сервисы выбрать для типичного backend?
- [ ] :memo: Пересмотри: [[network-fundamentals-for-developers]], [[network-http-evolution]], [[network-dns-tls]]. Запиши: как сетевые знания помогают при дебаге latency-проблем?

**День 4** — Системный дизайн
- [ ] :memo: Финальное упражнение: спроектируй backend-систему (например, URL shortener или notification service), используя знания из всех 6 доменов:
  - API: REST? gRPC? WebSocket?
  - БД: SQL? NoSQL? Комбинация?
  - Безопасность: auth flow, rate limiting, secrets
  - DevOps: CI/CD, Docker, K8s
  - Облако: какие managed-сервисы?
  - Сеть: CDN, load balancing, DNS

**День 5** — Финальный Review
- [ ] :memo: **Финальный Review:** оцени свой прогресс. Какие темы требуют дополнительного изучения? Составь список из 3-5 тем для углубления.

---

## Статистика пути

| Домен | Файлов | Общее время |
|-------|--------|-------------|
| Архитектура (ARCH) | 15 | ~595 мин |
| Базы данных (DB) | 12 | ~378 мин |
| Безопасность (SEC) | 13 | ~243 мин |
| DevOps (OPS) | 9 | ~128 мин |
| Облако (CLD) | 6 | ~100 мин |
| Сети (NET) | 9 | ~165 мин |
| **Итого** | **64** | **~1609 мин (~27 ч)** |

С учётом Review Days: **~8 недель** при темпе 60-90 мин/день, 5 дней/неделю.

---

## Связанные материалы

- [[architecture-overview]] — обзор раздела архитектуры
- [[databases-overview]] — обзор раздела баз данных
- [[security-overview]] — обзор раздела безопасности
- [[devops-overview]] — обзор раздела DevOps
- [[cloud-overview]] — обзор раздела облачных платформ
- [[networking-overview]] — обзор раздела сетевых технологий
- [[cognitive-science-rules]] — правила обучения на основе когнитивной науки
- [[deliberate-practice]] — принципы осознанной практики
- [[desirable-difficulties]] — почему сложность улучшает обучение (интерливинг -- одна из "желательных трудностей")
