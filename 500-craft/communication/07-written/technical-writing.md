---
title: "Technical Writing: RFC, ADR и документация"
created: 2026-02-09
modified: 2026-02-09
type: guide
status: published
tags:
  - topic/communication
  - type/guide
  - level/intermediate
related:
  - "[[async-communication]]"
  - "[[email-communication]]"
prerequisites:
  - "[[communication-models]]"
reading_time: 15
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Technical Writing: RFC, ADR и документация

## TL;DR

Хорошая техническая документация = **контекст** (зачем) + **решение** (что) + **обоснование** (почему). RFC для proposals, ADR для решений, README для onboarding. Правило: документ должен быть **полезен через 6 месяцев** человеку, который не участвовал в обсуждении.

---

## Зачем это нужно

**Статистика:**
- Разработчики тратят **~20% времени** на поиск документации (Stack Overflow Survey 2024)
- 74% проектов без ADR теряют контекст решений за **12 месяцев** (ThoughtWorks research)
- Onboarding без документации занимает в **3-4 раза дольше** (GitLab metrics)
- $26,000/год теряет средняя компания на каждого разработчика из-за плохой документации (Zoomin 2024)

**Проблемы без документации:**
```
СЦЕНАРИЙ 1: "Почему так?"
Junior: "Почему мы используем NoSQL для users?"
Senior: "Потому что... хм... наверное, была причина..."
*Никто не помнит, повторяют те же ошибки*

СЦЕНАРИЙ 2: "Это сломает?"
Dev: "Я хочу изменить этот интерфейс"
Team: "Не трогай, что-то сломаешь"
*Tech debt растёт, никто не рискует рефакторить*

СЦЕНАРИЙ 3: "Как это работает?"
New hire: "Как запустить проект?"
Team: "Спроси у Васи... хотя он в отпуске..."
*Onboarding превращается в квест*
```

---

## Для кого этот материал

| Уровень | Применение | Фокус |
|---------|------------|-------|
| **Junior** | README, Code comments | Basics: что + как |
| **Middle** | ADR, API docs | Контекст + обоснование |
| **Senior** | RFC, Design docs | Proposals + alternatives |
| **Lead/Architect** | Technical strategy docs | Vision + roadmap |

---

## Ключевые термины

| Термин | Определение | Когда использовать |
|--------|-------------|-------------------|
| **RFC** | Request for Comments — proposal на обсуждение | Значительные изменения |
| **ADR** | Architecture Decision Record — запись решения | Архитектурные решения |
| **README** | Entry point документации | Каждый репозиторий |
| **Design Doc** | Детальный дизайн системы | Перед implementation |
| **Runbook** | Инструкции для operations | Incident response |
| **Changelog** | История изменений | Каждый релиз |

---

## Виды технической документации

```
ПИРАМИДА ДОКУМЕНТАЦИИ:

                    ┌─────────────────┐
                    │    VISION       │  Strategy docs
                    │    (Why we)     │  Quarterly plans
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │       ARCHITECTURE        │  Design docs, RFC
               │       (How system)        │  ADR, Tech specs
               └─────────────┬─────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │              IMPLEMENTATION             │  API docs, Code comments
        │              (How to use)               │  README, Tutorials
        └────────────────────┬────────────────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │                  OPERATIONS                     │  Runbooks, Playbooks
    │                  (How to run)                   │  On-call guides
    └─────────────────────────────────────────────────┘
```

### Когда что использовать

| Документ | Цель | Аудитория | Lifecycle |
|----------|------|-----------|-----------|
| **RFC** | Propose change | Team/org | До решения |
| **ADR** | Record decision | Future devs | После решения |
| **Design Doc** | Detail design | Implementers | До coding |
| **README** | Quick start | New users | Постоянно |
| **API Docs** | Reference | Consumers | При изменениях |
| **Runbook** | Operate | On-call | При incidents |

---

## RFC (Request for Comments)

### Зачем нужен RFC

- Получить feedback **до** начала работы
- Документировать thought process
- Распределить knowledge
- Избежать "big reveal" surprises

### Когда писать RFC

```
НУЖЕН RFC:
✓ Изменение затрагивает >1 команду
✓ Breaking changes в API
✓ Новая технология в стеке
✓ Изменение архитектуры
✓ Security-sensitive changes

НЕ НУЖЕН RFC:
✗ Bug fixes
✗ Minor refactoring
✗ Internal changes одного сервиса
✗ Documentation updates
```

### Структура RFC

```markdown
# RFC: [Название]

## Meta
- **Author(s):** [имена]
- **Status:** Draft | Under Review | Accepted | Rejected | Superseded
- **Created:** [дата]
- **Last Updated:** [дата]
- **Reviewers:** [кто должен одобрить]

## Summary
[2-3 предложения: что предлагаем]

## Motivation
[Почему это нужно? Какую проблему решаем?]

## Proposal
[Детальное описание решения]

## Alternatives Considered
[Другие варианты и почему не они]

## Implementation Plan
[Этапы, timeline, milestones]

## Risks & Mitigations
[Что может пойти не так и как защищаемся]

## Open Questions
[Что ещё не решено, нужен input]

## References
[Ссылки на related docs, research]
```

### Пример RFC (сокращённый)

```markdown
# RFC: Migrate User Service to PostgreSQL

## Meta
- **Author:** Maria Ivanova (@maria)
- **Status:** Under Review
- **Created:** 2025-01-15
- **Reviewers:** @backend-team, @dba-team

## Summary
Предлагаю мигрировать User Service с MongoDB на PostgreSQL
для улучшения data consistency и упрощения queries.

## Motivation
Текущие проблемы с MongoDB:
1. Complex joins требуют multiple queries (N+1)
2. Transactions ограничены single document
3. $40K/year на Atlas vs $5K для RDS

User data хорошо структурированы — relational model лучше подходит.

## Proposal
### Phase 1: Dual-write (Week 1-2)
- Все writes идут в обе базы
- Reads остаются из MongoDB

### Phase 2: Shadow reads (Week 3-4)
- Read from both, compare, alert on differences
- Fix data inconsistencies

### Phase 3: Switchover (Week 5)
- Switch reads to PostgreSQL
- MongoDB as fallback

### Phase 4: Cleanup (Week 6)
- Remove MongoDB writes
- Decommission MongoDB cluster

## Alternatives Considered

### Keep MongoDB
- Pro: No migration risk
- Con: Problems will grow with scale

### CockroachDB
- Pro: Distributed SQL
- Con: Team doesn't have expertise, higher cost

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss | Critical | Dual-write, extensive testing |
| Performance regression | High | Load testing before switch |
| Extended migration | Medium | Clear rollback plan |

## Open Questions
1. Should we migrate auth tokens too or separate service?
2. Timeline overlap with Q2 OKRs?

## References
- [MongoDB vs PostgreSQL benchmarks](link)
- [Similar migration at Stripe](link)
```

### RFC Workflow

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│   Draft   │───▶│  Review   │───▶│ Approved  │───▶│Implemented│
└───────────┘    └─────┬─────┘    └───────────┘    └───────────┘
                       │
                       ▼
                ┌───────────┐
                │ Rejected/ │
                │ Deferred  │
                └───────────┘

Review period: 1-2 weeks (depending on scope)
Approval: Required reviewers + no blocking concerns
```

---

## ADR (Architecture Decision Record)

### Зачем нужен ADR

- **Память проекта:** почему приняли решение
- **Onboarding:** новички понимают context
- **Reversibility:** когда условия меняются
- **Accountability:** кто, когда, почему

### ADR vs RFC

| Аспект | RFC | ADR |
|--------|-----|-----|
| **Timing** | До решения | После решения |
| **Purpose** | Propose & discuss | Record & explain |
| **Mutable** | Да, до approval | Нет, immutable |
| **Length** | Detailed | Concise |
| **Audience** | Decision makers | Future developers |

### Структура ADR (Y-Statement)

```markdown
# ADR-0001: [Название решения]

## Status
Accepted | Superseded by ADR-XXXX | Deprecated

## Context
[Ситуация, которая требовала решения]

## Decision
In the context of [situation],
facing [concern/challenge],
we decided [option],
and neglected [other options],
to achieve [goal],
accepting [tradeoffs].

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Tradeoff 1]
- [Tradeoff 2]

## Notes
- Date: [when decided]
- Deciders: [who]
- Related: [links to related ADRs, RFCs]
```

### Пример ADR

```markdown
# ADR-0023: Use JWT for API Authentication

## Status
Accepted

## Context
Наш API использует session-based auth с Redis store.
При горизонтальном масштабировании возникают проблемы:
- Session affinity требует sticky sessions
- Redis становится single point of failure
- Cross-service auth требует shared session store

## Decision
In the context of scaling our API horizontally,
facing challenges with session management across instances,
we decided to use JWT (JSON Web Tokens) for authentication,
and neglected session cookies and OAuth tokens,
to achieve stateless authentication,
accepting increased token size and inability to instant revoke.

### Token Structure
```
Header: { alg: RS256, typ: JWT }
Payload: { sub, role, exp, iat }
Signature: RSA-SHA256
```

### Key Management
- Private key: Vault, rotated quarterly
- Public key: Distributed to all services

## Consequences

### Positive
- Stateless: любой instance может validate
- Cross-service: другие сервисы могут verify
- Performance: нет Redis lookup на каждый request

### Negative
- Token revocation: нужен blacklist для logout
- Token size: ~500 bytes vs ~32 bytes session ID
- Clock sync: exp validation requires synchronized clocks

## Notes
- Date: 2025-01-10
- Deciders: @backend-team, @security-team
- Related: ADR-0015 (API Gateway), RFC-042 (Auth redesign)
```

### ADR Naming Convention

```
docs/adr/
├── 0001-record-architecture-decisions.md
├── 0002-use-postgresql-for-storage.md
├── 0003-choose-kubernetes-for-orchestration.md
├── 0004-implement-event-sourcing.md
└── template.md
```

### Когда ADR устаревает

```markdown
# ADR-0002: Use MongoDB for User Data

## Status
~~Accepted~~ Superseded by ADR-0023

[Остальной текст остаётся как исторический record]

## Supersession Note
This decision was superseded on 2025-01-15.
See ADR-0023 for current approach.
Reason: Scalability concerns, cost optimization.
```

---

## README

### Золотое правило

> README должен позволить новому разработчику запустить проект за **5 минут**.

### Структура идеального README

```markdown
# Project Name

One-liner: что делает проект.

## Quick Start
```bash
git clone ...
npm install
npm run dev
```

## Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)

## Installation
[Детальные инструкции]

## Usage
[Примеры использования]

## Architecture
[Высокоуровневая диаграмма или ссылка на docs]

## Development
### Running Tests
```bash
npm test
```

### Code Style
```bash
npm run lint
```

## Deployment
[Как деплоить или ссылка на docs]

## Contributing
[Guidelines или ссылка на CONTRIBUTING.md]

## License
[Тип лицензии]
```

### README Anti-Patterns

```
❌ ANTI-PATTERNS:

1. "Read the code" README
   # Project
   A project that does things.

2. "Wall of Text" README
   [10,000 words без структуры]

3. "Outdated" README
   # Setup
   npm install (но на самом деле уже yarn)

4. "Incomplete" README
   ## Installation
   TODO
```

---

## API Documentation

### Структура API Doc

```markdown
# API Reference

## Authentication
[Как получить и использовать токен]

## Base URL
`https://api.example.com/v1`

## Endpoints

### GET /users
Get list of users.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | int | No | Max results (default 20) |
| offset | int | No | Skip first N results |

**Response:**
```json
{
  "users": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

**Errors:**
| Code | Description |
|------|-------------|
| 401 | Unauthorized |
| 429 | Rate limit exceeded |

**Example:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/v1/users?limit=10"
```
```

### API Doc Tools

| Tool | Pros | Cons |
|------|------|------|
| **OpenAPI/Swagger** | Standard, auto-generation | Verbose YAML |
| **Postman** | Interactive, collections | Vendor lock-in |
| **Readme.io** | Beautiful, hosted | Paid |
| **Docusaurus** | React-based, flexible | Requires setup |
| **Slate** | Clean, single page | Ruby dependency |

---

## Runbooks

### Зачем нужны Runbooks

- 3 AM incident: нет времени думать
- Любой on-call должен справиться
- Reduce Mean Time To Recovery (MTTR)

### Структура Runbook

```markdown
# Runbook: [Service Name] - [Problem Type]

## Overview
[Что это за проблема]

## Alert Details
- **Alert Name:** HighErrorRate
- **Severity:** Critical
- **SLO Impact:** Yes

## Investigation

### Step 1: Check Service Health
```bash
kubectl get pods -n production | grep service-name
```
Expected: All pods Running

### Step 2: Check Logs
```bash
kubectl logs -n production deployment/service-name --tail=100
```
Look for: ERROR, Exception, timeout

### Step 3: Check Dependencies
- [ ] Database: `pg_isready -h db.example.com`
- [ ] Redis: `redis-cli -h redis.example.com ping`
- [ ] External API: `curl https://api.external.com/health`

## Resolution

### Scenario A: OOM Errors
```bash
kubectl rollout restart deployment/service-name -n production
```

### Scenario B: Database Connection Issues
```bash
kubectl scale deployment/service-name --replicas=0 -n production
# Wait 30 seconds
kubectl scale deployment/service-name --replicas=3 -n production
```

### Scenario C: Needs Escalation
Contact: @backend-team in #incidents

## Post-Incident
1. Create incident ticket
2. Document timeline
3. Schedule postmortem if needed
```

---

## Принципы хорошей документации

### 1. Audience-First

```
КТО будет читать?

Новичок в проекте:
- Нужен context и setup instructions
- Не знает jargon и history

Experienced developer:
- Нужен quick reference
- Знает basics, нужны edge cases

On-call engineer:
- Нужны actionable steps
- Нет времени на context
```

### 2. Layered Information

```
PROGRESSIVE DISCLOSURE:

Level 1: TL;DR (2-3 sentences)
│
▼
Level 2: Overview (1 page)
│
▼
Level 3: Details (full documentation)
│
▼
Level 4: Deep Dive (implementation notes)
```

### 3. Keep It Updated

```
DOCUMENTATION DECAY:

Write ────┬──────────────────────────────▶ Time
          │
          │  ┌─────────────────────┐
Accuracy  │  │ Code diverges from │
          │  │ documentation      │
          ▼  └─────────────────────┘

SOLUTION:
- Docs-as-Code: docs live with code
- CI checks: links, examples must work
- Review cycle: quarterly audit
- Owner assignment: CODEOWNERS for docs
```

### 4. Examples > Explanations

```
❌ "The function accepts a configuration object with
   various parameters for customizing behavior..."

✅
```javascript
const config = {
  timeout: 5000,      // ms before giving up
  retries: 3,         // number of retry attempts
  backoff: 'exponential'  // 'linear' | 'exponential'
};

client.connect(config);
```
```

### 5. Teach the "Why"

```
❌ "Use prepared statements for SQL queries"

✅ "Use prepared statements for SQL queries
   to prevent SQL injection attacks.

   Bad:
   `db.query("SELECT * FROM users WHERE id = " + userId)`
   → userId = "1; DROP TABLE users" = disaster

   Good:
   `db.query("SELECT * FROM users WHERE id = $1", [userId])`
   → userId is always treated as data, never code"
```

---

## Распространённые ошибки

### 1. "Future Self" Assumption

```
❌ ОШИБКА: "Я и так помню, зачем это сделал"

✅ РЕАЛЬНОСТЬ: Через 6 месяцев вы — другой человек.
   Документируйте для него.
```

### 2. "Self-Documenting Code"

```
❌ ОШИБКА: "Код понятен, комментарии не нужны"

✅ РЕАЛЬНОСТЬ:
   - Код показывает WHAT, не WHY
   - Business context не в коде
   - Альтернативы не видны
```

### 3. Write-Once Documentation

```
❌ ОШИБКА: Написал и забыл

✅ РЕШЕНИЕ:
   - Docs как часть PR review
   - Automated freshness checks
   - Quarterly documentation sprints
```

### 4. Documentation in Wrong Place

```
❌ ОШИБКА: ADR в Confluence, code в GitHub, README в Wiki

✅ РЕШЕНИЕ: Документация рядом с кодом
   repo/
   ├── docs/
   │   ├── adr/
   │   ├── api/
   │   └── runbooks/
   ├── src/
   └── README.md
```

### 5. No Owner

```
❌ ОШИБКА: "Документация — общая ответственность" = ничья

✅ РЕШЕНИЕ:
   # CODEOWNERS
   /docs/adr/     @architects
   /docs/api/     @backend-team
   /docs/runbooks/ @sre-team
```

---

## Когда использовать / НЕ использовать

### Когда документировать

| Ситуация | Тип документа |
|----------|--------------|
| Архитектурное решение | ADR |
| Значительное изменение (proposal) | RFC |
| Новый сервис | README + Design Doc |
| API для внешних consumers | API Docs (OpenAPI) |
| Операционные процедуры | Runbook |
| Код с неочевидной логикой | Code comment |

### Когда НЕ документировать

| Ситуация | Почему |
|----------|--------|
| Очевидный код | `// increment counter` не нужен |
| Временный workaround | TODO comment достаточно |
| Internal implementation | Может измениться |
| Every design discussion | Только significant decisions |

### Принцип минимальной документации

```
DOCUMENT:
- What you wish you knew when you started
- What someone will ask you 3 times
- What's not obvious from code
- Why, not just what

DON'T DOCUMENT:
- What code already says clearly
- Temporary states
- Every conversation
- Things that change daily
```

---

## Практические задания

### Задание 1: Write an ADR

**Контекст:** Ваша команда решила перейти с REST на GraphQL для нового API.

**Задача:** Напишите ADR, включая:
- Context (почему рассматривали изменение)
- Decision (Y-statement format)
- Consequences (positive и negative)

### Задание 2: README Audit

**Задача:** Возьмите README вашего текущего проекта и проверьте:

```
□ Можно запустить проект за 5 минут?
□ Prerequisites чётко указаны?
□ Команды актуальны и работают?
□ Есть примеры использования?
□ Понятно, что проект делает (first paragraph)?
```

### Задание 3: Runbook Creation

**Сценарий:** Ваш сервис может упасть из-за исчерпания database connections.

**Задача:** Напишите runbook с:
- Investigation steps
- Resolution steps
- Escalation criteria

### Задание 4: RFC Practice

**Сценарий:** Вы хотите предложить добавление feature flags system.

**Задача:** Напишите RFC skeleton:
- Summary (2-3 предложения)
- Motivation (1 параграф)
- Alternatives (2-3 варианта)
- Open questions (3 вопроса для обсуждения)

### Задание 5: Comment Improvement

**Плохой комментарий:**
```javascript
// Process the data
function process(data) {
  // Check if valid
  if (!data) return null;
  // Transform
  return data.map(x => x * 2);
}
```

**Задача:** Перепишите комментарии так, чтобы они объясняли WHY, а не WHAT.

---

## Чеклист документации

### RFC Checklist

```
□ Summary понятен без чтения всего документа
□ Motivation объясняет проблему, не решение
□ Proposal достаточно детален для implementation
□ Alternatives включает "do nothing" option
□ Risks конкретны с mitigation strategies
□ Reviewers определены
□ Timeline для review указан
```

### ADR Checklist

```
□ Title чётко описывает решение
□ Context объясняет ситуацию
□ Decision в Y-statement format
□ Consequences включают negatives
□ Status актуален
□ Date и Deciders указаны
□ Related docs linked
```

### README Checklist

```
□ One-liner описывает что делает проект
□ Quick start позволяет запустить за 5 минут
□ Prerequisites полные и актуальные
□ Commands проверены и работают
□ Examples показывают реальное использование
□ License указана
□ Contribution guide есть
```

### General Documentation Checklist

```
□ Audience определена
□ Цель документа ясна
□ Examples > explanations
□ Jargon объяснён или avoided
□ Links работают
□ Owner assigned
□ Last updated date указана
```

---

## Инструменты

### Documentation Platforms

| Tool | Best For | Pros |
|------|----------|------|
| **GitHub/GitLab Wiki** | Internal docs | Free, integrated |
| **Notion** | Team knowledge base | Rich formatting |
| **Confluence** | Enterprise | Integration with Jira |
| **Docusaurus** | Public docs | React, versioning |
| **MkDocs** | Technical docs | Markdown, simple |
| **Gitbook** | Polished docs | Beautiful UI |

### Docs-as-Code Tools

| Tool | Purpose |
|------|---------|
| **Markdown** | Universal format |
| **AsciiDoc** | Complex technical docs |
| **OpenAPI** | API specifications |
| **Mermaid** | Diagrams in Markdown |
| **PlantUML** | UML diagrams |
| **Vale** | Prose linting |

### ADR Tools

| Tool | Description |
|------|-------------|
| **adr-tools** | CLI for ADR management |
| **Log4brains** | ADR viewer with UI |
| **Madr** | Markdown ADR template |

---

## Связанные темы

### Prerequisites
- [[communication-models]] — передача information
- [[email-communication]] — BLUF principle

### Unlocks
- [[async-communication]] — documentation as async tool
- [[onboarding-guide]] — documentation for new hires

### Интеграция
- [[giving-feedback]] — feedback на documentation
- [[stakeholder-negotiation]] — RFC approval process

---

## Источники

1. "Docs Like Code" by Anne Gentle (2017)
2. Google Technical Writing Courses (developers.google.com)
3. ThoughtWorks Technology Radar on ADRs
4. "Living Documentation" by Cyrille Martraire (2019)
5. GitHub's documentation style guide
6. Stripe's API documentation (gold standard)
7. Stack Overflow Developer Survey (2024)
8. Write the Docs community resources
9. Michael Nygard's ADR template (original)
10. RFC process at IETF, Rust, React

---

## Проверь себя

> [!question]- Команда написала RFC на переход с монолита на микросервисы. В секции Alternatives нет варианта "оставить как есть". Почему это критическая ошибка?
> "Do nothing" — обязательная альтернатива в любом RFC, потому что она задаёт **baseline** для сравнения. Без неё невозможно объективно оценить cost/benefit предлагаемого изменения. Рецензенты не могут ответить на вопрос "а стоит ли вообще что-то менять?". Это также защищает от confirmation bias — автор RFC уже решил действовать и может неосознанно исключать вариант бездействия.

> [!question]- У вас есть runbook для database connection exhaustion и ADR о выборе connection pool (HikariCP). DevOps-инженер при инциденте в 3 AM не может найти, почему выбран maxPoolSize=20. Какой документ должен ссылаться на какой, и как организовать связь между ними?
> Runbook должен содержать ссылку на ADR в секции Context/Background — чтобы on-call инженер мог быстро понять reasoning за конфигурацию. ADR фиксирует **почему** выбраны параметры (нагрузочное тестирование, лимиты БД), а runbook — **что делать** при проблемах. Связь двусторонняя: ADR в секции Related ссылается на runbook, runbook в Investigation ссылается на ADR. Принцип docs-as-code гарантирует, что оба документа лежат рядом в `docs/`.

> [!question]- Вы пишете API-документацию для внешних потребителей. Middle-разработчик предлагает описать каждый endpoint одним предложением и ссылкой на исходный код. Проанализируйте, какие принципы хорошей документации это нарушает и для какой аудитории это особенно проблематично.
> Нарушены минимум три принципа: **(1) Audience-First** — внешние consumers не имеют доступа к исходному коду и не обязаны его читать; **(2) Examples > Explanations** — одно предложение без примеров запросов/ответов бесполезно для интеграции; **(3) Layered Information** — нет progressive disclosure (TL;DR → overview → details). Особенно проблематично для новичков в API: им нужны curl-примеры, описания параметров, коды ошибок и edge cases, а не ссылка на `handler.go`.

> [!question]- Архитектор записал ADR о выборе JWT для аутентификации. Через год требования изменились — нужен instant token revocation. Что делать с существующим ADR и почему нельзя просто отредактировать его?
> ADR — **immutable** документ. Редактирование уничтожает историю решений и контекст, в котором они принимались. Правильный подход: создать новый ADR (например, ADR-0045) со статусом Accepted, а старый ADR пометить как `Superseded by ADR-0045` с указанием даты и причины. Новый ADR в секции Context должен ссылаться на старый и объяснять, что изменилось. Это сохраняет **память проекта** — будущие разработчики поймут эволюцию решений.

---

## Ключевые карточки

RFC — когда писать?
?
Когда изменение затрагивает >1 команду, содержит breaking changes в API, вводит новую технологию, меняет архитектуру или касается security. НЕ нужен для bug fixes, minor refactoring, internal changes одного сервиса.

ADR — чем отличается от RFC?
?
RFC пишется **до** решения (propose & discuss), mutable до approval, детальный. ADR пишется **после** решения (record & explain), immutable, лаконичный. RFC — для decision makers, ADR — для future developers.

Y-Statement формат ADR — структура?
?
"In the context of [situation], facing [concern], we decided [option], and neglected [other options], to achieve [goal], accepting [tradeoffs]." Фиксирует контекст, решение, альтернативы, цель и компромиссы в одном абзаце.

Золотое правило README?
?
README должен позволить новому разработчику **запустить проект за 5 минут**. Обязательные секции: one-liner, Quick Start, Prerequisites, Installation, Usage, Architecture, Development, Deployment.

Принцип "Examples > Explanations" — почему?
?
Пример кода с комментариями передаёт больше информации, чем абзац текста. Разработчик может скопировать и адаптировать пример, а абстрактное описание требует мысленного перевода в код. Примеры также легче проверить на актуальность через CI.

Documentation Decay — как бороться?
?
Четыре стратегии: **(1)** Docs-as-Code — документация живёт рядом с кодом; **(2)** CI checks — проверка ссылок и примеров; **(3)** Quarterly audit — ревью актуальности; **(4)** CODEOWNERS — назначенные ответственные за каждую секцию.

Runbook — ключевые секции?
?
Overview (что за проблема), Alert Details (severity, SLO impact), Investigation (пошаговая диагностика с командами), Resolution (сценарии восстановления), Escalation (когда и кому передавать), Post-Incident (тикет, timeline, postmortem).

Принцип "Teach the Why" — что документировать?
?
Код показывает **что** (WHAT), но не **почему** (WHY). Документация должна объяснять business context, причины выбора, отвергнутые альтернативы и последствия. Пример: не "используйте prepared statements", а "используйте их для защиты от SQL injection — вот как выглядит атака".

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Асинхронная коммуникация | [[async-communication]] | Документация как инструмент async-работы в распределённых командах |
| Email и BLUF-принцип | [[email-communication]] | Структурированное письменное общение — та же дисциплина, что и в RFC |
| Архитектурные решения | [[architecture-decisions]] | Процесс принятия решений, которые фиксируются в ADR |
| CI/CD пайплайны | [[ci-cd-pipelines]] | Автоматизация проверки документации: линтинг, валидация ссылок, freshness |
| Процесс разработки | [[development-process]] | Встраивание документации в workflow команды (docs как часть PR review) |
| Онбординг | [[onboarding]] | Практическое применение README и design docs для новых сотрудников |
| Обратная связь | [[giving-feedback]] | Как давать конструктивный feedback на чужую документацию и RFC |

---

**Последнее обновление:** 2025-01-18
**Статус:** Завершён
