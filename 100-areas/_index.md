---
title: "Tech Knowledge Base: главный индекс"
created: 2026-01-09
modified: 2026-01-11
type: index
status: verified
confidence: high
tags:
  - type/index
  - navigation
---

# Tech Knowledge Base

> **515 файлов** систематизированных знаний по разработке программного обеспечения.

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Готовлюсь к интервью? | [[cs-fundamentals-overview]] → [[coding-challenges]] |
| Изучаю Android? | [[android-overview]] → [[android-architecture-patterns]] |
| Изучаю iOS? | [[ios-overview]] → [[ios-architecture-patterns]] |
| Изучаю Kotlin Multiplatform? | [[kmp-overview]] → [[cs-foundations-overview]] |
| Сравниваю iOS и Android? | [[cross-platform-overview]] → [[cross-memory-management]] |
| Хочу понять JVM? | [[jvm-overview]] → [[kotlin-overview]] |
| Проектирую архитектуру? | [[architecture-overview]] → [[cloud-overview]] |
| Настраиваю CI/CD? | [[devops-overview]] → [[ci-cd-pipelines]] |
| Безопасность приложения? | [[security-overview]] → [[authentication-authorization]] |
| Работаю с AI/ML? | [[ai-ml-overview-v2]] → [[ai-engineering-moc]] |
| Ищу работу? | [[career-moc]] → [[job-search-strategy]] |

---

## Карта разделов

```
                              TECH KNOWLEDGE BASE
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
    FUNDAMENTALS                 PLATFORMS                   PRACTICES
          │                           │                           │
    ┌─────┴─────┐         ┌───────────┼───────────┐        ┌──────┴──────┐
    │           │         │     │     │     │     │        │             │
 CS-Fund    OS/JVM    Android iOS   KMP  Cross  Cloud  Architecture  DevOps
    │           │         │     │     │     │     │        │             │
    ├─DSA       ├─OS      ├─UI  ├─UI  ├─Share├─Compare├─AWS  ├─API Design  ├─CI/CD
    ├─Patterns  ├─JVM     ├─Arch├─Arch├─MP   ├─Memory├─GCP  ├─Microserv   ├─Docker
    └─BigO      └─Memory  └─Build└─Xcode└─Desk└─Life └─Sec  └─Events      └─K8s
```

---

## Разделы по категориям

### Fundamentals — Фундаментальные знания

| Раздел | Описание | Файлов | Вход |
|--------|----------|--------|------|
| **CS Fundamentals** | Алгоритмы, структуры данных, паттерны | 56 | [[cs-fundamentals-overview]] |
| **Operating Systems** | Процессы, память, файловые системы | 8 | [[os-overview]] |
| **JVM** | Java Virtual Machine, GC, concurrency | 37 | [[jvm-overview]] |
| **Programming** | Clean code, SOLID, design patterns | 8 | [[clean-code-solid]] |

### Platforms — Платформы разработки

| Раздел | Описание | Файлов | Вход |
|--------|----------|--------|------|
| **Android** | Lifecycle, Architecture, Compose, Build | 45 | [[android-overview]] |
| **iOS** | SwiftUI, UIKit, async/await, Xcode, ARC | 45 | [[ios-overview]] |
| **Cross-Platform** | iOS vs Android: память, lifecycle, UI, KMP | 24 | [[cross-platform-overview]] |
| **Kotlin Multiplatform** | iOS, Web, Desktop, Compose MP | 37 | [[kmp-overview]] |
| **CS Foundations KMP** | Низкоуровневые основы для KMP | 61 | [[cs-foundations-overview]] |
| **Cloud** | AWS, GCP, Serverless, Networking | 7 | [[cloud-overview]] |

### Practices — Практики разработки

| Раздел | Описание | Файлов | Вход |
|--------|----------|--------|------|
| **Architecture** | API Design, Microservices, Distributed | 11 | [[architecture-overview]] |
| **DevOps** | CI/CD, Docker, Kubernetes, GitOps | 10 | [[devops-overview]] |
| **Security** | OWASP, Crypto, Auth, API Protection | 8 | [[security-overview]] |
| **Databases** | SQL, NoSQL, Optimization, Design | 8 | [[databases-overview]] |
| **Networking** | HTTP, TCP/IP, DNS, TLS, Mobile | 23 | [[network-overview]] |

### Specialized — Специализированные области

| Раздел | Описание | Файлов | Вход |
|--------|----------|--------|------|
| **AI/ML** | LLM, RAG, Agents, Embeddings, Tools | 33 | [[ai-ml-overview-v2]] |
| **Thinking** | Cognitive Load, Deep Work, Learning | 22 | [[cognitive-load-theory]] |
| **Career** | Interview, Job Search, Resume, Regions | 30 | [[career-moc]] |

---

## Граф связей между разделами

```
                    ┌──────────────────┐
                    │  CS Fundamentals  │
                    │  (DSA, Patterns)  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │    OS    │   │   JVM    │   │Programming│
       │(Processes│◄─►│ (Memory, │   │ (Patterns │
       │ Memory)  │   │  GC)     │   │  SOLID)   │
       └────┬─────┘   └────┬─────┘   └─────┬────┘
            │              │               │
       ┌────┴────┐    ┌────┴────┐          │
       │         │    │         │          │
       ▼         ▼    ▼         ▼          ▼
   ┌───────┐ ┌───────┐ ┌─────┐ ┌────────┐ ┌─────────┐
   │Android│ │  iOS  │ │Kotlin│ │  KMP   │ │Architect│
   │(UI,   │◄┤(Swift │◄┤     ├►│(Share, │ │(API,Dist│
   │Compose│ │ UIKit)│ │     │ │MP,Web) │ │Systems) │
   └───┬───┘ └───┬───┘ └──┬──┘ └────┬───┘ └────┬────┘
       │         │        │         │          │
       │ ┌───────┴────────┤         │          │
       │ │  Cross-Platform│         │          │
       │ │  (Comparisons) │         │          │
       │ └───────┬────────┘         │          │
       └─────────┴──────────────────┘          │
                          │                    │
              ┌───────────┴───────────┐        │
              │                       │        │
              ▼                       ▼        ▼
       ┌──────────┐            ┌──────────┐  ┌──────────┐
       │  DevOps  │◄──────────►│  Cloud   │◄►│ Security │
       │(CI/CD,K8s│            │(AWS,GCP) │  │(Auth,TLS)│
       └──────────┘            └──────────┘  └──────────┘
```

---

## Путь изучения по уровням

### Уровень 1: Junior Developer

```
CS Fundamentals (DSA) → Programming (Clean Code) → Android/Backend basics
```

### Уровень 2: Middle Developer

```
OS basics → JVM → Architecture → Cloud fundamentals → DevOps basics
```

### Уровень 3: Senior Developer

```
Distributed Systems → Security → Performance → KMP → AI/ML integration
```

### Уровень 4: Tech Lead / Architect

```
System Design → Team processes → Technical debt → Strategy
```

---

## Статистика базы знаний

| Метрика | Значение |
|---------|----------|
| Всего файлов | 515 |
| Разделов | 18 |
| Обработано педагогически | 473 (~92%) |
| Learning Paths | 12+ |

---

## Последние обновления

| Дата | Что добавлено |
|------|---------------|
| 2026-01-11 | **Cross-Platform раздел** — 24 файла: iOS vs Android сравнения, ARC vs GC, lifecycle, UI, KMP patterns |
| 2026-01-11 | **iOS раздел** — 45 файлов: SwiftUI, UIKit, async/await, Core Data, Xcode, CI/CD |
| 2026-01-09 | Learning Paths в devops, architecture, os, career |
| 2026-01-09 | Критические файлы: patterns-overview, type-systems, build-systems |
| 2026-01-09 | Педагогическая обработка AI-ML, Thinking, Career |

---

*Создано: 2026-01-09*

---

*Проверено: 2026-01-11*
