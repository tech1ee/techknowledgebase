---
title: "Техническое Due Diligence"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [cto, vpe, investor, acquirer]
teaches:
  - technical assessment
  - risk evaluation
  - due diligence process
sources: [m-and-a, vc-due-diligence, technical-assessment]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[engineering-practices]]"
  - "[[architecture-decisions]]"
  - "[[startup-cto]]"
prerequisites:
  - "[[engineering-practices]]"
  - "[[architecture-decisions]]"
  - "[[startup-cto]]"
reading_time: 14
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Техническое Due Diligence

> **TL;DR:** Technical due diligence = assessing tech health before investment/acquisition. Focus: architecture, code quality, team, security, scalability. Goal: find hidden risks, validate claims. Prepare: documentation, clean code, honest assessment. Both sides benefit from transparency.

---

## When DD Happens

```
SCENARIOS:

FUNDING ROUND:
Investor wants to verify technical claims.
Usually Series A+ (not seed).
1-5 days of assessment.

ACQUISITION:
Acquirer assessing technical assets.
Deeper than funding DD.
1-2 weeks typically.

PARTNERSHIP:
Enterprise customer validating vendor.
Focus: security, reliability.
Questionnaire + calls.

BOARD/AUDIT:
Internal technical review.
Annual or triggered by issues.
```

## Due Diligence Areas

```
┌─────────────────────────────────────────────────────────┐
│                TECHNICAL DUE DILIGENCE                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │ ARCHITECTURE  │  │   CODEBASE    │  │    TEAM     │ │
│  │               │  │               │  │             │ │
│  │ • Structure   │  │ • Quality     │  │ • Skills    │ │
│  │ • Scalability │  │ • Tech debt   │  │ • Key people│ │
│  │ • Decisions   │  │ • Testing     │  │ • Culture   │ │
│  └───────────────┘  └───────────────┘  └─────────────┘ │
│                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│  │   SECURITY    │  │  OPERATIONS   │  │    DATA     │ │
│  │               │  │               │  │             │ │
│  │ • Vulns       │  │ • Deployment  │  │ • Storage   │ │
│  │ • Compliance  │  │ • Monitoring  │  │ • Privacy   │ │
│  │ • Access      │  │ • Incidents   │  │ • Backups   │ │
│  └───────────────┘  └───────────────┘  └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Architecture Assessment

```
QUESTIONS:

OVERVIEW:
• What's the high-level architecture?
• Why were these technologies chosen?
• What are the main components?

SCALABILITY:
• Current load handling?
• What's the bottleneck?
• Plan for 10x growth?

TECHNICAL DEBT:
• Known debt areas?
• Planned refactoring?
• Blocking any initiatives?

DEPENDENCIES:
• Critical third-party services?
• Single points of failure?
• Vendor lock-in risks?

RED FLAGS:
✗ No clear architecture diagram
✗ "We'll figure it out when we scale"
✗ Critical logic in one service
✗ No documentation of decisions
✗ Outdated major dependencies

GREEN FLAGS:
✓ Clear separation of concerns
✓ Documented ADRs
✓ Scalability tested
✓ Modern, maintained stack
```

## Codebase Review

```
WHAT TO EXAMINE:

CODE QUALITY:
• Consistent style?
• Readable/maintainable?
• Appropriate abstractions?
• Error handling?

TESTING:
• Test coverage %?
• Unit, integration, e2e?
• Tests actually run in CI?
• Flaky tests?

TECHNICAL DEBT:
• TODO/FIXME density?
• Obvious code smells?
• Copy-paste patterns?
• Dead code?

SECURITY:
• Secrets in code?
• SQL injection risks?
• Input validation?
• Auth implementation?

SAMPLE REVIEW APPROACH:
1. Get overview from team (30 min)
2. Review core domain logic (2 hours)
3. Review API layer (1 hour)
4. Review tests (1 hour)
5. Search for red flags (grep/ripgrep)

METRICS TO REQUEST:
• Lines of code by language
• Test coverage
• Cyclomatic complexity
• Dependency audit
```

## Team Assessment

```
KEY QUESTIONS:

COMPOSITION:
• Team size and roles?
• Tenure of key people?
• Recent departures?
• Hiring pipeline?

SKILLS:
• Technology expertise?
• Domain knowledge?
• Leadership capability?
• Single points of failure?

PROCESS:
• How are decisions made?
• Code review practices?
• Sprint/planning cadence?
• Documentation habits?

CULTURE:
• How do they handle disagreements?
• What happens when things break?
• Learning and growth focus?

RED FLAGS:
✗ CTO leaving soon
✗ High turnover recently
✗ Single person knows critical system
✗ No process, pure chaos
✗ Blame culture visible

GREEN FLAGS:
✓ Stable, growing team
✓ Clear ownership areas
✓ Healthy debate visible
✓ Knowledge sharing practices
✓ Realistic self-assessment
```

## Security & Compliance

```
SECURITY CHECKLIST:

AUTHENTICATION:
□ Strong password policy
□ MFA available/required
□ Session management secure
□ OAuth implemented correctly

DATA PROTECTION:
□ Encryption at rest
□ Encryption in transit (TLS)
□ PII handling documented
□ Data retention policies

ACCESS CONTROL:
□ Principle of least privilege
□ Role-based access
□ Access reviews conducted
□ Offboarding process

INFRASTRUCTURE:
□ Network segmentation
□ Firewall rules documented
□ Secrets management (Vault, etc.)
□ Security patches current

COMPLIANCE:
□ SOC 2 (in progress/completed?)
□ GDPR compliance
□ HIPAA (if healthcare)
□ PCI DSS (if payments)

INCIDENT HISTORY:
□ Any breaches?
□ How were they handled?
□ Post-mortems available?
□ Improvements implemented?
```

## Operations & Reliability

```
DEPLOYMENT:

QUESTIONS:
• How often do you deploy?
• How long does deploy take?
• Can you rollback quickly?
• What's your CI/CD pipeline?

METRICS TO REQUEST:
• Deployment frequency
• Lead time for changes
• Mean time to restore (MTTR)
• Change failure rate

MONITORING:

QUESTIONS:
• What do you monitor?
• How do you get alerted?
• What's your on-call setup?
• SLAs defined?

SHOULD HAVE:
□ Application metrics
□ Infrastructure monitoring
□ Error tracking (Sentry, etc.)
□ Log aggregation
□ Uptime monitoring

INCIDENT MANAGEMENT:

QUESTIONS:
• Major incidents last year?
• Root cause and resolution?
• Post-mortems conducted?
• Runbooks exist?
```

## Data & Infrastructure

```
DATA ASSESSMENT:

STORAGE:
• Database choices and why
• Data volume and growth
• Backup strategy and testing
• Disaster recovery plan

DATA QUALITY:
• Data validation in place?
• Consistency guarantees?
• Migration history clean?
• Data lifecycle management?

INFRASTRUCTURE:

CLOUD:
• Provider and regions?
• Infrastructure as Code?
• Cost optimization?
• Multi-region/DR setup?

COSTS:
• Monthly infrastructure spend?
• Cost per customer?
• Cost trends?
• Optimization opportunities?

VENDOR DEPENDENCIES:
List all critical SaaS:
• What if Stripe goes down?
• What if AWS has outage?
• Contract terms reviewed?
• Exit strategy from vendors?
```

## Due Diligence Checklist

```
FOR ASSESSORS:

PRE-MEETING:
□ Review public information
□ Prepare question list
□ Define success criteria
□ Plan assessment schedule

DURING ASSESSMENT:
□ Architecture walkthrough
□ Code review (sample)
□ Team interviews
□ Security review
□ Operations review

DOCUMENTATION TO REQUEST:
□ Architecture diagrams
□ API documentation
□ Incident history
□ Org chart
□ Technology roadmap

POST-ASSESSMENT:
□ Synthesize findings
□ Risk categorization
□ Recommendations
□ Present to stakeholders
```

## Preparing for DD (Company Side)

```
DOCUMENTATION TO PREPARE:

ARCHITECTURE:
□ System overview diagram
□ Data flow diagram
□ Technology decisions (ADRs)
□ Third-party dependencies list

CODEBASE:
□ Repository access ready
□ README files current
□ Known tech debt documented
□ Test coverage report

SECURITY:
□ Security policies documented
□ Compliance status
□ Last penetration test results
□ Incident history

OPERATIONS:
□ Deployment documentation
□ Monitoring dashboards
□ Incident post-mortems
□ On-call procedures

TEAM:
□ Org chart
□ Role descriptions
□ Key person documentation
□ Hiring plan

TIPS:
• Be honest about weaknesses
• Prepare CTO for deep questions
• Have code owners available
• Clean up obvious issues beforehand
• Don't hide problems (they'll find them)
```

## Red Flags Summary

```
CRITICAL (deal breakers):
✗ Security breach covered up
✗ Core IP not owned by company
✗ CTO/key engineers leaving
✗ Fundamental scalability issue
✗ Compliance violation

SERIOUS (negotiate/mitigate):
✗ High technical debt
✗ Single points of failure
✗ No testing culture
✗ Outdated technology
✗ Poor documentation

MODERATE (factor into valuation):
✗ Inconsistent code quality
✗ Manual deployment process
✗ Limited monitoring
✗ Bus factor concerns
✗ Some tech debt
```

## DD Report Template

```markdown
# Technical Due Diligence Report

**Company:** [Name]
**Date:** [Date]
**Assessor:** [Name/Firm]

## Executive Summary
[2-3 paragraph overview of findings]

## Overall Assessment
**Rating:** Green / Yellow / Red
**Recommendation:** Proceed / Proceed with cautions / Do not proceed

## Architecture
**Rating:** [1-5]
[Findings, risks, recommendations]

## Codebase
**Rating:** [1-5]
[Findings, risks, recommendations]

## Team
**Rating:** [1-5]
[Findings, risks, recommendations]

## Security
**Rating:** [1-5]
[Findings, risks, recommendations]

## Operations
**Rating:** [1-5]
[Findings, risks, recommendations]

## Key Risks
1. [Risk 1 with mitigation]
2. [Risk 2 with mitigation]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

## Appendix
- Detailed findings
- Interview notes
- Code review notes
```

---

## Связь с другими темами

**[[engineering-practices]]** — Техническое due diligence фактически оценивает качество инженерных практик компании: CI/CD, code review, testing, documentation, incident management. Компании с сильными инженерными практиками проходят DD значительно легче, поскольку их процессы прозрачны и измеримы. Инвестирование в инженерные практики задолго до DD — лучшая стратегия подготовки.

**[[architecture-decisions]]** — Документированные Architecture Decision Records (ADR) являются одним из ключевых артефактов, которые assessors ищут при техническом DD. ADR показывают не только текущую архитектуру, но и контекст принятия решений, рассмотренные альтернативы и trade-offs. Отсутствие документации архитектурных решений — серьёзный red flag при due diligence, указывающий на хаотичное техническое управление.

**[[startup-cto]]** — CTO стартапа несёт основную ответственность за подготовку к техническому DD и за прохождение самой процедуры. Инвесторы оценивают не только код и архитектуру, но и CTO как лидера: его способность честно оценить tech debt, сформулировать технический roadmap и ответить на глубокие технические вопросы. Подготовка к DD — это не одноразовое событие, а результат постоянной работы CTO над качеством инженерной организации.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Ries E. (2011) *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses* | Книга |
| Drucker P. (2006) *The Effective Executive: The Definitive Guide to Getting the Right Things Done* | Книга |


## Проверь себя

> [!question]- Red flags classification
> Вы проводите DD стартапа перед acquisition. Находите: (a) secrets в коде на GitHub, (b) test coverage 30%, (c) CTO уволился месяц назад, (d) manual deployment раз в 2 недели. Используя Red Flags Summary, классифицируйте каждый finding (critical/serious/moderate) и определите deal-breaker.

> [!question]- DD preparation от CTO
> Ваш стартап готовится к Series A. Investor requested technical DD через 2 недели. Используя 'Preparing for DD' checklist, составьте prioritized action plan: что подготовить в первую очередь и что можно honestly acknowledge как known debt.

## Ключевые карточки

Назови 6 областей Technical Due Diligence.
?
Architecture (structure, scalability, decisions), Codebase (quality, tech debt, testing), Team (skills, key people, culture), Security (vulns, compliance, access), Operations (deployment, monitoring, incidents), Data (storage, privacy, backups).

Какие red flags являются deal-breakers при DD?
?
Critical: security breach covered up, core IP not owned by company, CTO/key engineers leaving, fundamental scalability issue, compliance violation. Serious: high tech debt, single points of failure, no testing culture.

Какие DORA metrics запрашивают при DD?
?
Deployment frequency, lead time for changes, MTTR (mean time to restore), change failure rate. Эти метрики показывают зрелость engineering practices и operational capability.

Что нужно подготовить для DD со стороны компании?
?
Architecture diagrams, tech debt list (honest!), ADRs, test coverage report, security policies, deployment docs, incident post-mortems, org chart, roadmap. Tip: be honest about weaknesses, don't hide problems.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[startup-cto]] | CTO как главный ответственный за DD |
| Углубиться | [[architecture-decisions]] | ADR как артефакт для DD |
| Смежная тема | [[security-fundamentals]] | Security assessment при DD |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
