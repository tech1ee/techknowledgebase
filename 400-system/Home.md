---
title: "Home"
created: 2025-11-24
modified: 2026-02-09
type: index
aliases:
  - Home
  - Dashboard
tags:
  - type/index
  - navigation
---

# Knowledge Vault

> Персональная база знаний по IT, архитектуре и мышлению.
> **640 материалов** в 20 областях знаний.

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Готовлюсь к интервью? | [[cs-fundamentals-overview]] → [[cs-fundamentals-moc]] |
| Изучаю Android? | [[android-overview]] → [[android-moc]] |
| Изучаю iOS? | [[ios-overview]] → [[ios-moc]] |
| Изучаю Kotlin Multiplatform? | [[kmp-overview]] → [[kmp-moc]] |
| Сравниваю iOS и Android? | [[cross-platform-overview]] → [[cross-platform-moc]] |
| Хочу понять JVM? | [[jvm-overview]] → [[jvm-moc]] |
| Проектирую архитектуру? | [[architecture-overview]] → [[architecture-moc]] |
| Работаю с базами данных? | [[databases-overview]] → [[databases-moc]] |
| Настраиваю CI/CD? | [[devops-overview]] → [[devops-moc]] |
| Безопасность приложения? | [[security-overview]] → [[security-moc]] |
| Работаю с AI/ML? | [[ai-ml-overview-v2]] → [[ai-engineering-moc]] |
| Ищу работу? | [[career-moc]] |
| Хочу стать лидером? | [[leadership-overview]] → [[leadership-moc]] |
| Улучшаю коммуникацию? | [[communication-overview]] → [[communication-moc]] |

---

## Учебные маршруты

> Структурированные пути обучения от основ до экспертного уровня по ключевым областям.

| Область | Путь обучения | Файлов |
|---------|---------------|--------|
| Android | [[android-learning-path]] | 66 |
| CS Fundamentals | [[cs-fundamentals-learning-path]] | 62 |
| iOS | [[ios-learning-path]] | 45 |
| JVM | [[jvm-learning-path]] | 37 |
| Kotlin Multiplatform | [[kmp-learning-path]] | 37 |
| CS Foundations | [[cs-foundations-learning-path]] | 23 |

---

## Области знаний

### Fundamentals — Фундаментальные знания

#### CS Fundamentals
> 63 материала: алгоритмы, структуры данных, паттерны решения

**Рекомендуемый путь:** [[cs-fundamentals-overview]]

**Ключевые материалы:**
- [[patterns-overview]] — 30+ алгоритмических паттернов
- [[two-pointers-pattern]] — Two Pointers, Fast/Slow
- [[dp-patterns]] — Dynamic Programming
- [[binary-search-pattern]] — Binary Search и вариации

**MOC:** [[cs-fundamentals-moc]]

---

#### Operating Systems
> 8 материалов: процессы, память, файловые системы

- [[os-overview]] — Обзор ОС
- [[os-processes-threads]] — Процессы и потоки
- [[os-memory-management]] — Управление памятью
- [[os-synchronization]] — Синхронизация
- [[os-scheduling]] — Планировщики
- [[os-file-systems]] — Файловые системы
- [[os-io-devices]] — I/O
- [[os-virtualization]] — Виртуализация

**MOC:** [[os-moc]]

---

#### JVM Platform
> 37 материалов: JVM internals, Java, Kotlin

**Рекомендуемый путь:** [[jvm-overview]]

**JVM Internals:**
- [[jvm-basics-history]] — История, архитектура
- [[jvm-memory-model]] — Память, GC
- [[jvm-concurrency-overview]] — Concurrency, JMM
- [[jvm-production-debugging]] — Профилирование, debugging

**Kotlin:**
- [[kotlin-overview]] — Обзор языка
- [[kotlin-coroutines]] — Корутины
- [[kotlin-flow]] — Reactive streams

**MOC:** [[jvm-moc]], [[kotlin-moc]]

---

#### Programming Fundamentals
> 12 материалов: чистый код, паттерны, принципы

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

### Platforms — Платформы разработки

#### Android Development
> 66 материалов: от основ до продвинутых паттернов

**Рекомендуемый путь:** [[android-overview]]

**Ключевые материалы:**
- [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture
- [[android-compose]] — Jetpack Compose
- [[android-coroutines-mistakes]] — Ошибки с корутинами
- [[android-dependency-injection]] — Hilt, Koin, Dagger

**MOC:** [[android-moc]]

---

#### iOS Development
> 45 материалов: SwiftUI, UIKit, async/await, архитектура

**Рекомендуемый путь:** [[ios-overview]]

**Ключевые материалы:**
- [[ios-architecture-patterns]] — MVVM, VIPER, TCA
- [[ios-swiftui]] — SwiftUI
- [[ios-concurrency-mistakes]] — async/await, Actors
- [[ios-process-memory]] — ARC, retain cycles

**MOC:** [[ios-moc]]

---

#### Cross-Platform
> 24 материала: iOS vs Android сравнения по аспектам

**Рекомендуемый путь:** [[cross-platform-overview]]

- [[cross-memory-management]] — ARC vs GC
- [[cross-lifecycle]] — Lifecycle сравнение
- [[cross-architecture]] — Архитектурные паттерны

**MOC:** [[cross-platform-moc]]

---

#### Kotlin Multiplatform
> 70 материалов: shared code, Compose MP, production

**Рекомендуемый путь:** [[kmp-overview]]

- [[kmp-overview]] — Обзор KMP
- [[kmp-architecture-patterns]] — Архитектура KMP проектов
- [[compose-mp-overview]] — Compose Multiplatform

**MOC:** [[kmp-moc]]

---

#### CS Foundations (KMP)
> 61 материал: низкоуровневые основы для кроссплатформы

**Рекомендуемый путь:** [[cs-foundations-overview]]

- Memory, Compilation, Concurrency
- Type Systems, Platform Interop

**MOC:** [[cs-foundations-moc]]

---

#### Cloud & Infrastructure
> 7 материалов: AWS, GCP, Azure, Serverless

- [[cloud-overview]] — Обзор облачных платформ
- [[cloud-platforms-essentials]] — AWS, GCP, Azure основы
- [[cloud-aws-core-services]] — EC2, S3, Lambda, RDS
- [[cloud-gcp-core-services]] — Compute, Storage, BigQuery
- [[cloud-serverless-patterns]] — Serverless
- [[cloud-networking-security]] — VPC, Security Groups
- [[cloud-disaster-recovery]] — DR стратегии

**MOC:** [[cloud-moc]]

---

### Practices — Практики разработки

#### Архитектура систем
> 12 материалов: проектирование систем, паттерны, технический долг

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

#### DevOps & Platform
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

#### Databases
> 16 материалов: SQL, NoSQL, оптимизация запросов

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

#### Networking
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

#### Security
> 13 материалов: безопасность приложений, OWASP, DevSecOps

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

### AI & Machine Learning

#### AI/ML Engineering
> 43 материала: от основ LLM до production-ready AI систем

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

**MOC:** [[ai-engineering-moc]]

---

### Soft Skills — Навыки лидера

#### Карьера и поиск работы
> 37 материалов: от анализа рынка до negotiation

**Рекомендуемый путь:** [[career-moc]]

**Ключевые материалы:**
- [[se-interview-foundation]] — Основы интервью SE
- [[android-senior-2026]] — Android Senior подготовка
- [[salary-benchmarks]] — Зарплаты по регионам
- [[ai-interview-preparation]] — AI-powered подготовка

**MOC:** [[career-moc]]

---

#### Leadership
> 44 материала: менеджмент, найм, командная динамика, стратегия

**Рекомендуемый путь:** [[leadership-overview]]

- Роли: Tech Lead, Engineering Manager, Director
- Engineering Management, найм, 1-1
- Организационный дизайн, tech strategy

**MOC:** [[leadership-moc]]

---

#### Communication
> 26 материалов: презентации, переговоры, письменная речь

**Рекомендуемый путь:** [[communication-overview]]

- Fundamentals → Listening → Feedback
- Difficult Conversations → Negotiations
- Presentations → Written → Cross-cultural

**MOC:** [[communication-moc]]

---

#### Мышление и обучение
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

## Структура базы

```
100-areas/     → Основные области знаний (640 файлов)
  ├── ai-ml/              → 43 файла: AI Engineering
  ├── android/            → 66 файлов: Android Development
  ├── architecture/       → 12 файлов: Архитектура систем
  ├── career/             → 37 файлов: Карьера, поиск работы
  ├── cloud/              → 7 файлов: AWS, GCP, Azure
  ├── communication/      → 26 файлов: Коммуникация
  ├── cross-platform/     → 24 файла: iOS vs Android
  ├── cs-foundations-kmp/  → 61 файл: Низкоуровневые основы
  ├── cs-fundamentals/    → 63 файла: Алгоритмы и паттерны
  ├── databases/          → 16 файлов: SQL, NoSQL
  ├── devops/             → 10 файлов: Docker, K8s, CI/CD
  ├── ios/                → 45 файлов: iOS Development
  ├── jvm/                → 37 файлов: JVM, Java, Kotlin
  ├── kotlin-multiplatform/ → 70 файлов: KMP, Compose MP
  ├── leadership/         → 44 файла: Лидерство и менеджмент
  ├── networking/         → 23 файла: Сети
  ├── operating-systems/  → 8 файлов: ОС
  ├── programming/        → 12 файлов: Код, паттерны
  ├── security/           → 13 файлов: OWASP, Auth
  └── thinking/           → 22 файла: Мышление
200-resources/ → Справочники
400-system/    → Навигация, индексы, мета
  ├── _MOCs/          → Maps of Content (21 карта)
  ├── _indexes/       → Сводные индексы
  ├── _meta/          → Стандарты контента
  ├── _plans/         → Планы развития
  └── _templates/     → Шаблоны заметок
```

---

## Статистика

| Область | Файлов |
|---------|--------|
| Kotlin Multiplatform | 70 |
| Android | 66 |
| CS Fundamentals | 63 |
| CS Foundations KMP | 61 |
| iOS | 45 |
| Leadership | 44 |
| AI/ML | 43 |
| JVM | 37 |
| Career | 37 |
| Communication | 26 |
| Cross-Platform | 24 |
| Networking | 23 |
| Thinking | 22 |
| Databases | 16 |
| Security | 13 |
| Programming | 12 |
| Architecture | 12 |
| DevOps | 10 |
| Operating Systems | 8 |
| Cloud | 7 |
| **Всего** | **640** |

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
│   400-system  │       │  100-areas    │       │ 200-resources │
│   /_MOCs/     │       │  (контент)    │       │ (справочники) │
├───────────────┤       └───────────────┘       └───────────────┘
│21 карта навиг.│
│по всем областям│      Каждая область имеет:
│               │       ├── *-overview.md (вход в тему)
│               │       └── *-moc.md     (карта навигации)
└───────────────┘
```

---

*Последнее обновление: 2026-02-09*
