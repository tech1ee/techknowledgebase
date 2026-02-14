---
title: "Таксономия тегов"
created: 2026-02-09
modified: 2026-02-09
type: reference
status: published
confidence: high
tags:
  - system/guidelines
  - system/metadata
related:
  - "[[frontmatter-standard]]"
  - "[[content-types]]"
  - "[[content-levels]]"
---

# Таксономия тегов

> Единая система тегов с namespace-разделением. Каждый файл получает минимум 2 тега: `topic/*` + `type/*`.

---

## Структура

```
tags:
  - topic/{область}       # ЧТО — домен знаний
  - type/{тип-контента}   # КАК — формат подачи
  - level/{сложность}     # ДЛЯ КОГО — целевой уровень
```

---

## topic/ — Область знаний

20 доменов, распределены по 5 зонам знаний (`100-foundations/`, `200-platforms/`, `300-systems/`, `400-ai-ml/`, `500-craft/`):

### Fundamentals

| Тег | Область | Файлов |
|-----|---------|:------:|
| `topic/cs-fundamentals` | Алгоритмы, структуры данных, паттерны | ~63 |
| `topic/os` | Процессы, память, файловые системы | ~10 |
| `topic/jvm` | JVM, GC, concurrency, байткод | ~37 |
| `topic/programming` | Clean code, SOLID, design patterns | ~8 |

### Platforms

| Тег | Область | Файлов |
|-----|---------|:------:|
| `topic/android` | Lifecycle, Architecture, Compose, Build | ~68 |
| `topic/ios` | SwiftUI, UIKit, async/await, ARC | ~47 |
| `topic/cross-platform` | iOS vs Android сравнения | ~24 |
| `topic/kmp` | Kotlin Multiplatform: iOS, Web, Desktop | ~37 |
| `topic/cs-foundations` | Низкоуровневые основы для KMP | ~61 |
| `topic/cloud` | AWS, GCP, Serverless | ~7 |

### Practices

| Тег | Область | Файлов |
|-----|---------|:------:|
| `topic/architecture` | API Design, Microservices, Distributed | ~11 |
| `topic/devops` | CI/CD, Docker, Kubernetes, GitOps | ~10 |
| `topic/security` | OWASP, Crypto, Auth, API Protection | ~8 |
| `topic/databases` | SQL, NoSQL, Optimization, Design | ~8 |
| `topic/networking` | HTTP, TCP/IP, DNS, TLS, Mobile | ~23 |

### AI & Data

| Тег | Область | Файлов |
|-----|---------|:------:|
| `topic/ai-ml` | LLM, RAG, Agents, Embeddings | ~33 |

### Soft Skills

| Тег | Область | Файлов |
|-----|---------|:------:|
| `topic/career` | Interview, Job Search, Resume | ~30 |
| `topic/leadership` | Roles, Strategy, Executive | ~44 |
| `topic/communication` | Fundamentals, Cross-cultural | ~26 |
| `topic/thinking` | Cognitive Load, Deep Work, Learning | ~22 |

### Дополнительные topic-теги

Для файлов, которые относятся к поддомену:

| Тег | Когда использовать |
|-----|-------------------|
| `topic/kotlin` | Файлы о языке Kotlin (не KMP) |
| `topic/swift` | Файлы о языке Swift |
| `topic/docker` | Специфично Docker (не весь DevOps) |
| `topic/kubernetes` | Специфично K8s |
| `topic/aws` | Специфично AWS |
| `topic/gcp` | Специфично GCP |

Правило: если файл относится к конкретному поддомену, добавляй **оба** тега:
```yaml
tags:
  - topic/devops      # основная область
  - topic/docker      # конкретная технология
```

---

## type/ — Тип контента

| Тег | Соответствует `type:` | Описание |
|-----|----------------------|----------|
| `type/deep-dive` | deep-dive | Глубокое погружение (1000+ слов) |
| `type/concept` | concept | Объяснение одной концепции (400-800 слов) |
| `type/comparison` | comparison | Сравнение A vs B |
| `type/reference` | reference | Справочник, cheat sheet |
| `type/tutorial` | tutorial | Пошаговое руководство |
| `type/guide` | guide | Практическое руководство |
| `type/overview` | overview | Входная точка в область |
| `type/moc` | moc | Map of Content |
| `type/interview-prep` | — | Материал для подготовки к интервью |

`type/interview-prep` — дополнительный тег, ставится вместе с основным type:
```yaml
type: deep-dive
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - type/interview-prep    # помечает как полезный для интервью
```

---

## level/ — Уровень сложности

| Тег | Описание | Кто читатель |
|-----|----------|-------------|
| `level/beginner` | Основы, первое знакомство | Junior, студент |
| `level/intermediate` | Рабочие навыки, паттерны | Middle разработчик |
| `level/advanced` | Глубокие знания, edge cases | Senior разработчик |
| `level/expert` | Архитектура, трейдоффы, стратегия | Tech Lead, Architect |

Правила:
- Overview файлы: `level/beginner`
- MOC файлы: не ставить level (это навигация, не контент)
- Если файл покрывает несколько уровней, ставить **наивысший**

---

## system/ — Системные теги

Для файлов в `900-system/`:

| Тег | Для чего |
|-----|----------|
| `system/guidelines` | Правила и стандарты |
| `system/metadata` | Про метаданные и теги |
| `system/navigation` | Навигационные файлы |

---

## Специальные теги

| Тег | Когда использовать |
|-----|-------------------|
| `navigation` | Файлы-хабы навигации (MOC, overview, index) |
| `interview` | Любой материал полезный для интервью |
| `pattern` | Паттерны проектирования |
| `concurrency` | Многопоточность и асинхронность (кросс-доменный) |
| `performance` | Оптимизация производительности (кросс-доменный) |

---

## Миграция старых тегов

| Старый тег (flat) | Новый тег (namespace) |
|--------------------|----------------------|
| `android` | `topic/android` |
| `ios` | `topic/ios` |
| `jvm` | `topic/jvm` |
| `kotlin` | `topic/kotlin` |
| `security` | `topic/security` |
| `databases` | `topic/databases` |
| `architecture` | `topic/architecture` |
| `ai` | `topic/ai-ml` |
| `llm` | `topic/ai-ml` |
| `os` | `topic/os` |
| `compose` | `topic/android` |
| `moc` | `type/moc` |
| `deep-dive` | `type/deep-dive` |
| `interview` | `interview` (оставить как есть) |
| `pattern` | `pattern` (оставить как есть) |
| `concurrency` | `concurrency` (оставить как есть) |
| `performance` | `performance` (оставить как есть) |
| `optimization` | `performance` |

### Теги, содержащие `[[wikilinks]]`

В некоторых файлах поле `tags:` содержит wikilinks вида `"[[android-overview]]"`. Это **неправильно** — wikilinks должны быть в поле `related:`, не в `tags:`. При миграции:
- Переместить `"[[...]]"` из `tags:` → `related:`
- Оставить в `tags:` только текстовые теги

---

## Примеры миграции

### До (старый формат)

```yaml
---
title: "Kotlin Coroutines"
created: 2025-11-25
modified: 2025-11-25
type: deep-dive
status: verified
confidence: high
tags:
  - jvm
  - kotlin
  - concurrency
  - "[[kotlin-overview]]"
  - "[[android-threading]]"
---
```

### После (новый формат)

```yaml
---
title: "Kotlin Coroutines: асинхронность без callback hell"
created: 2025-11-25
modified: 2026-02-09
type: deep-dive
status: published
confidence: high
tags:
  - topic/jvm
  - topic/kotlin
  - type/deep-dive
  - level/intermediate
  - concurrency
related:
  - "[[kotlin-overview]]"
  - "[[android-threading]]"
  - "[[kotlin-flow]]"
---
```

---

## Связанные файлы

- [[frontmatter-standard]] — полный стандарт frontmatter
- [[content-types]] — структуры для каждого типа контента
- [[content-levels]] — уровни качества и Bloom's Taxonomy

---

*Создано: 2026-02-09*
