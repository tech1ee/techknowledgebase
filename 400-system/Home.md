---
title: "Home"
created: 2025-11-24
modified: 2025-12-27
type: navigation
aliases:
  - Home
  - Dashboard
---

# Knowledge Vault

> Персональная база знаний по IT, архитектуре и мышлению.
> **246 материалов** в 13 областях знаний.

---

## Области знаний

### AI & ML Engineering
> 31 материал: от основ LLM до production-ready AI систем

**Рекомендуемый путь:** [[ai-ml-overview-v2]] — полная карта знаний

**Быстрый старт:**
- [[llm-fundamentals]] — Архитектура Transformer, токенизация
- [[models-landscape-2025]] — GPT-4o, Claude, Gemini, Llama, DeepSeek
- [[prompt-engineering-masterclass]] — Zero-shot, Few-shot, CoT, ReAct

**Практические проекты:**
- [[tutorial-rag-chatbot]] — RAG чат-бот с LangChain + ChromaDB
- [[tutorial-ai-agent]] — AI Agent с инструментами
- [[tutorial-document-qa]] — Document Q&A с extraction

**Справочники:**
- [[ai-tools-ecosystem-2025]] — Каталог инструментов 2025
- [[agent-frameworks-comparison]] — LangGraph vs CrewAI vs AutoGen

**MOC:** [[ai-ml-overview-v2]]

---

### Android Development
> 43 материала: от основ до продвинутых паттернов

**Рекомендуемый путь:** [[android-overview]]

**Ключевые материалы:**
- [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture
- [[android-compose]] — Jetpack Compose
- [[android-coroutines-mistakes]] — Ошибки с корутинами
- [[android-dependency-injection]] — Hilt, Koin, Dagger

**MOC:** [[android-overview]]

---

### Архитектура систем
> 11 материалов: проектирование систем, паттерны, технический долг

- [[microservices-vs-monolith]] — Когда что выбирать
- [[technical-debt]] — $2 триллиона проблем
- [[api-design]] — REST, GraphQL и когда что использовать
- [[caching-strategies]] — Redis и стратегии кэширования
- [[event-driven-architecture]] — Kafka, Event Sourcing, Saga
- [[performance-optimization]] — От 3s до 300ms
- [[architecture-distributed-systems]] — Распределённые системы
- [[architecture-resilience-patterns]] — Circuit Breaker, Retry, Bulkhead

**MOC:** [[architecture-moc]]

---

### Cloud & Infrastructure
> 7 материалов: AWS, GCP, Azure, Serverless

- [[cloud-overview]] — Обзор облачных платформ
- [[cloud-platforms-essentials]] — AWS, GCP, Azure основы
- [[cloud-aws-core-services]] — EC2, S3, Lambda, RDS
- [[cloud-gcp-core-services]] — Compute, Storage, BigQuery
- [[cloud-serverless-patterns]] — Functions, Step Functions
- [[cloud-networking-security]] — VPC, Security Groups
- [[cloud-disaster-recovery]] — DR стратегии

**MOC:** [[cloud-moc]]

---

### Databases
> 8 материалов: SQL, NoSQL, оптимизация запросов

- [[databases-overview]] — Обзор баз данных
- [[databases-sql-fundamentals]] — SQL основы
- [[databases-transactions-acid]] — Транзакции, ACID
- [[databases-nosql-comparison]] — MongoDB, Redis, Cassandra
- [[database-design-optimization]] — Индексы, N+1
- [[databases-replication-sharding]] — Репликация, шардинг
- [[databases-backup-recovery]] — Бэкапы
- [[databases-monitoring-security]] — Мониторинг

**MOC:** [[databases-moc]]

---

### DevOps & Platform
> 10 материалов: контейнеры, CI/CD, инфраструктура, мониторинг

- [[devops-overview]] — Обзор DevOps практик
- [[docker-for-developers]] — Docker для разработчиков
- [[ci-cd-pipelines]] — Автоматизация от коммита до прода
- [[git-workflows]] — Trunk-Based, GitFlow
- [[kubernetes-basics]] — Оркестрация контейнеров
- [[kubernetes-advanced]] — HPA, Operators, Service Mesh
- [[observability]] — Logs, Metrics, Traces
- [[infrastructure-as-code]] — Terraform
- [[gitops-argocd-flux]] — GitOps практики
- [[devops-incident-management]] — Incident management

**MOC:** [[devops-moc]]

---

### JVM Platform
> 38 материалов: JVM internals, Java, Kotlin

**Рекомендуемый путь:** [[jvm-overview]]

**JVM Internals:**
- [[jvm-basics-history]] — История, архитектура
- [[jvm-memory-model]] — Память, GC
- [[jvm-concurrency-overview]] — Concurrency, JMM
- [[jvm-production-debugging]] — Профилирование, debugging

**Kotlin (15 материалов):**
- [[kotlin-overview]] — Обзор языка
- [[kotlin-coroutines]] — Корутины
- [[kotlin-flow]] — Reactive streams
- [[kotlin-multiplatform]] — KMP

**MOC:** [[programming-moc]], [[kotlin-moc]]

---

### Networking
> 23 материала: от физического уровня до cloud networking

- [[networking-overview]] — Обзор сетей
- [[network-physical-layer]] — L1: физический уровень
- [[network-ip-routing]] — L3: IP, маршрутизация
- [[network-transport-layer]] — L4: TCP, UDP
- [[network-dns-tls]] — DNS, TLS
- [[network-http-evolution]] — HTTP/1.1 → HTTP/3
- [[network-cloud-modern]] — Cloud networking
- [[os-networking]] — Сетевой стек ОС

**MOC:** [[networking-moc]]

---

### Operating Systems
> 8 материалов: процессы, память, файловые системы

- [[os-overview]] — Обзор ОС
- [[os-processes-threads]] — Процессы и потоки
- [[os-memory-management]] — Управление памятью
- [[os-scheduling]] — Планировщики
- [[os-synchronization]] — Синхронизация
- [[os-file-systems]] — Файловые системы
- [[os-io-devices]] — I/O
- [[os-virtualization]] — Виртуализация

**MOC:** [[os-overview]]

---

### Programming Fundamentals
> 8 материалов: чистый код, паттерны, принципы

- [[programming-overview]] — Обзор
- [[clean-code-solid]] — SOLID принципы
- [[design-patterns]] — Factory, Strategy, Observer
- [[testing-strategies]] — Пирамида тестов, TDD
- [[functional-programming]] — FP основы
- [[concurrency-parallelism]] — Concurrency
- [[error-handling-resilience]] — Обработка ошибок
- [[refactoring-techniques]] — Рефакторинг

**MOC:** [[programming-moc]]

---

### Security
> 8 материалов: безопасность приложений, OWASP, DevSecOps

- [[security-overview]] — Обзор безопасности
- [[web-security-owasp]] — OWASP Top 10
- [[authentication-authorization]] — JWT, OAuth 2.0
- [[security-cryptography-fundamentals]] — Криптография
- [[security-https-tls]] — HTTPS, TLS
- [[security-api-protection]] — API Security
- [[security-secrets-management]] — Secrets
- [[security-incident-response]] — Incident response

**MOC:** [[security-moc]]

---

### Мышление и обучение
> 22 материала: метакогниция, когнитивные искажения, фокус

- [[thinking-overview]] — Обзор
- [[metacognition]] — Думать о том, как думаешь
- [[cognitive-biases]] — Ловушки разума
- [[deep-work]] — Фокус в мире отвлечений
- [[mental-models]] — Инструментарий мышления
- [[systems-thinking]] — Системное мышление
- [[learning-complex-things]] — Как изучать сложное
- [[how-brain-learns]] — Нейронаука обучения
- [[flow-state]] — Состояние потока
- [[deliberate-practice]] — Осознанная практика

**MOC:** [[thinking-moc]]

---

### Карьера и поиск работы
> 29 материалов: от анализа рынка до negotiation

**Рекомендуемый путь:** [[_career-moc]]

**Ключевые материалы:**
- [[android-job-market-2025]] — состояние рынка, тренды 2025
- [[interview-process]] — 4-6 раундов: от recruiter до оффера
- [[android-questions]] — 50+ вопросов с ответами
- [[salary-benchmarks]] — зарплаты по регионам

**MOC:** [[_career-moc]]

---

## Структура базы

```
000-inbox/     → Входящие, несортированное
100-areas/     → Основные области знаний (246 файлов)
  ├── ai-ml/          → 31 файл: AI Engineering
  ├── android/        → 43 файла: Android Development
  ├── architecture/   → 11 файлов: Архитектура систем
  ├── career/         → 29 файлов: Карьера, поиск работы
  ├── cloud/          → 7 файлов: AWS, GCP, Azure
  ├── databases/      → 8 файлов: SQL, NoSQL
  ├── devops/         → 10 файлов: Docker, K8s, CI/CD
  ├── jvm/            → 38 файлов: JVM, Java, Kotlin
  ├── networking/     → 23 файла: Сети
  ├── operating-systems/ → 8 файлов: ОС
  ├── programming/    → 8 файлов: Код, паттерны
  ├── security/       → 8 файлов: OWASP, Auth
  └── thinking/       → 22 файла: Мышление
200-resources/ → Справочники (планируется)
400-system/    → Навигация, индексы, мета
  ├── _MOCs/          → Maps of Content
  ├── _indexes/       → Сводные индексы
  ├── _meta/          → Метаинформация
  └── _templates/     → Шаблоны заметок
_automation/   → Агенты и команды Claude Code
```

---

## Статистика

| Область | Заметок |
|---------|---------|
| AI & ML | 31 |
| Android | 43 |
| Architecture | 11 |
| Career | 29 |
| Cloud | 7 |
| Databases | 8 |
| DevOps | 10 |
| JVM Platform | 38 |
| Networking | 23 |
| Operating Systems | 8 |
| Programming | 8 |
| Security | 8 |
| Thinking | 22 |
| **Всего** | **246** |

---

## Карта навигации

```
                         ┌─────────────────┐
                         │     Home.md     │
                         │   (этот файл)   │
                         └────────┬────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   400-system  │       │  100-areas    │       │ 000-inbox     │
│   /_MOCs/     │       │  (контент)    │       │ (входящие)    │
├───────────────┤       ├───────────────┤       └───────────────┘
│ai-engineering │◄──────│  ai-ml/       │
│architecture   │◄──────│  architecture/│
│career-moc     │◄──────│  career/      │
│cloud-moc      │◄──────│  cloud/       │
│databases-moc  │◄──────│  databases/   │
│devops-moc     │◄──────│  devops/      │
│kotlin-moc     │◄──────│  jvm/         │
│programming    │◄──────│  programming/ │
│security-moc   │◄──────│  security/    │
│thinking-moc   │◄──────│  thinking/    │
└───────────────┘       └───────────────┘

Каждая область имеет:
├── *-overview.md  — обзор области в папке
└── *-moc.md       — карта контента в 400-system/_MOCs/
```

---

## Полезная информация

- **MOC файлы** содержат карты контента с рекомендуемым порядком изучения
- **400-system/** содержит навигацию, индексы и метаинформацию
- **_automation/** содержит агентов и slash-команды для Claude Code
- **000-inbox/** для быстрого сохранения идей перед сортировкой

---

*Последнее обновление: 2025-12-27*
