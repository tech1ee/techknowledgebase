---
title: "CTO в стартапе"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [cto, founder, technical-cofounder]
teaches:
  - startup CTO role evolution
  - technical cofounder responsibilities
  - build vs buy decisions
sources: [startup-cto-handbook, first-round-review, a16z]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[cto-vs-vpe]]"
  - "[[technical-vision]]"
  - "[[scaling-from-zero]]"
prerequisites:
  - "[[cto-vs-vpe]]"
  - "[[technical-vision]]"
  - "[[scaling-from-zero]]"
reading_time: 12
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# CTO в стартапе

> **TL;DR:** Startup CTO ≠ Big Company CTO. Early stage: 80% coding, 20% everything else. Role evolves dramatically as company grows. Key: know when to stop coding and start leading. Technical cofounder = business partner, not just engineer.

---

## CTO Role Evolution

```
STAGE 1: PRE-SEED / SEED (1-5 people)
┌─────────────────────────────────────────────┐
│ CODING: 80-90%                              │
│ • Build MVP yourself                        │
│ • Make all technical decisions              │
│ • Set up infrastructure                     │
│                                             │
│ OTHER: 10-20%                               │
│ • Investor technical diligence              │
│ • Hiring first engineers                    │
│ • Product discussions with CEO              │
└─────────────────────────────────────────────┘

STAGE 2: SERIES A (5-20 people)
┌─────────────────────────────────────────────┐
│ CODING: 40-60%                              │
│ • Critical features only                    │
│ • Architecture decisions                    │
│ • Code review                               │
│                                             │
│ MANAGEMENT: 30-40%                          │
│ • Hiring and onboarding                     │
│ • Process establishment                     │
│ • Team structure                            │
│                                             │
│ STRATEGY: 10-20%                            │
│ • Technical roadmap                         │
│ • Build vs buy                              │
│ • Vendor selection                          │
└─────────────────────────────────────────────┘

STAGE 3: SERIES B+ (20-50+ people)
┌─────────────────────────────────────────────┐
│ CODING: 0-20%                               │
│ • Prototypes only                           │
│ • Emergency fixes                           │
│                                             │
│ LEADERSHIP: 50-60%                          │
│ • Hiring leaders                            │
│ • Organization design                       │
│ • Culture and values                        │
│                                             │
│ STRATEGY: 30-40%                            │
│ • Technical vision                          │
│ • Board/investor relations                  │
│ • Partnerships                              │
└─────────────────────────────────────────────┘
```

## Technical Cofounder Responsibilities

```
BEYOND CODING:

PRODUCT:
• Translate business needs → technical solutions
• Say "no" to infeasible features
• Propose technical differentiators
• Understand user problems deeply

BUSINESS:
• Investor meetings (technical credibility)
• Customer calls (technical sales)
• Partnership discussions
• Due diligence preparation

TEAM:
• Hiring first engineers (crucial!)
• Setting engineering culture
• Technical mentorship
• Retention of key people

OPERATIONS:
• Budget for tech (cloud, tools)
• Security and compliance
• Incident response
• Vendor management

COFOUNDER RELATIONSHIP:
• Regular sync with CEO
• Disagree and commit
• Unified front to team
• Trust and transparency
```

## Early Stage Decisions

```
BUILD vs BUY:

BUILD WHEN:
✓ Core differentiator
✓ No good solution exists
✓ Integration too complex
✓ Long-term cost advantage

BUY WHEN:
✓ Commodity functionality
✓ Not your expertise
✓ Time-to-market critical
✓ Vendor does it better

COMMON MISTAKES:
✗ Building auth system (use Auth0, Clerk)
✗ Building payment (use Stripe)
✗ Building email (use SendGrid)
✗ Building analytics (use Amplitude, Mixpanel)

TECHNOLOGY CHOICES:

PRINCIPLES:
• Boring technology preferred
• Speed > perfection
• Hire-ability matters
• Cloud-native from start

COMMON STACK (2024-2025):
Frontend: React/Next.js, TypeScript
Backend: Node.js, Python, Go
Database: PostgreSQL, Redis
Cloud: AWS, GCP, or Vercel
Infra: Terraform, Docker, K8s (later)
```

## MVP Development

```
MVP MINDSET:

GOAL: Learn, not ship perfect product

PRINCIPLES:
• Smallest thing that tests hypothesis
• Manual before automated
• Fake it before you make it
• Launch embarrassingly early

TIMELINE:
4-8 weeks for initial MVP
Not 6 months of "foundation"

TECHNICAL DEBT:
✓ Acceptable: messy code, no tests
✓ Acceptable: manual processes
✗ Unacceptable: security shortcuts
✗ Unacceptable: data integrity issues

WHAT TO SKIP:
• Comprehensive testing (some critical paths only)
• Perfect architecture
• Scalability (until you need it)
• Admin tools (do it manually)

WHAT NOT TO SKIP:
• Basic security (auth, encryption)
• Data backups
• Monitoring (basic)
• Deployment automation (basic)
```

## Hiring First Engineers

```
FIRST 5 HIRES:

PROFILE:
• Generalists, not specialists
• Self-directed, low management
• Comfortable with ambiguity
• High ownership mentality
• Can ship end-to-end

RED FLAGS:
• "That's not my job"
• Needs detailed specs
• Only worked at big companies
• Uncomfortable with messy code

WHERE TO FIND:
• Your network first
• Former colleagues
• Angel List / Wellfound
• Twitter/X tech community
• Local meetups

COMPENSATION:
• Below market salary
• Significant equity (0.5-2% for early)
• Explain equity clearly
• 4-year vest, 1-year cliff standard

INTERVIEW FOCUS:
• Can they ship?
• Will they thrive in chaos?
• Do they care about the problem?
• Culture fit with founders?
```

## Founder Dynamics

```
CTO + CEO RELATIONSHIP:

HEALTHY PATTERNS:
• Weekly 1-on-1 (minimum)
• Disagree in private, united in public
• Clear decision rights
• Mutual respect

WARNING SIGNS:
• Avoiding hard conversations
• Blaming each other to team
• Misaligned on priorities
• Trust erosion

COMMON CONFLICTS:
• Speed vs quality
• Technical debt tolerance
• Hiring standards
• Resource allocation

RESOLUTION:
• Data over opinions
• Time-bound experiments
• External advisors
• Written agreements

WHEN CTO SHOULD PUSH BACK:
• Unrealistic timelines
• Security shortcuts
• Hiring wrong people fast
• Scope creep without resources
```

## Technical Due Diligence (Receiving End)

```
WHAT INVESTORS CHECK:

CODE:
• Architecture overview
• Code quality (samples)
• Tech debt assessment
• Security practices

TEAM:
• CTO background
• Team composition
• Hiring pipeline
• Key person risk

PROCESS:
• Deployment frequency
• Incident history
• Development workflow
• Documentation

INFRASTRUCTURE:
• Scalability path
• Cost structure
• Vendor dependencies
• Disaster recovery

HOW TO PREPARE:
• Architecture diagram (1-pager)
• Tech debt list (honest)
• Metrics dashboard
• Security checklist completed
• Clean code samples ready
```

## When to Stop Coding

```
SIGNS IT'S TIME:

• You're the bottleneck
• PRs wait for your review
• Team blocked on your decisions
• Hiring suffering
• Strategy neglected

TRANSITION APPROACH:

MONTH 1:
Identify what only you can do.
Start delegating everything else.

MONTH 2:
Find technical lead to own day-to-day.
You: architecture, hiring, strategy.

MONTH 3:
Stop committing to main.
Prototypes and experiments only.

EMOTIONAL CHALLENGES:
• Identity shift (I'm not coding!)
• Feeling useless
• Missing the flow state
• Imposter syndrome

COPING:
• Personal projects (weekends)
• Stay close to tech (reviews, design)
• Find fulfillment in team success
• Talk to other CTOs
```

---

## Связь с другими темами

**[[cto-vs-vpe]]** — Понимание различий между ролями CTO и VP Engineering критически важно для CTO стартапа, особенно при масштабировании. На ранней стадии CTO совмещает обе роли, но при росте до 20-50 инженеров приходится решать: остаться техническим лидером (CTO) или перейти к управлению людьми (VPE). Многие стартап-CTO нанимают VP Engineering, чтобы сфокусироваться на технической стратегии и product.

**[[technical-vision]]** — Формирование технического видения — одна из главных обязанностей CTO, которая становится всё более важной по мере роста компании. На стадии Seed-Series A это build vs buy решения и выбор стека, а на Series B+ — это долгосрочная архитектурная стратегия и технологический roadmap. CTO является главным хранителем технического видения и должен уметь транслировать его как команде инженеров, так и board of directors.

**[[scaling-from-zero]]** — CTO стартапа проживает все этапы масштабирования с нуля на собственном опыте, и каждый этап требует радикального изменения подхода к работе. Переход от «я пишу весь код» к «я не пишу код вообще» — один из самых сложных emotional transitions в карьере. Понимание этапов роста (0-10, 10-30, 30-100+) позволяет CTO заранее готовиться к необходимым изменениям в стиле лидерства.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Ries E. (2011) *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses* | Книга |
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |


## Проверь себя

> [!question]- Когда перестать кодить
> Вы CTO стартапа с 25 инженерами (Series A+). Вы всё ещё пишете 40% кода, но PRs ждут вашего review днями, hiring pipeline пуст, strategy neglected. Используя 'When to Stop Coding' framework, определите конкретный 3-month transition plan. Как справиться с emotional challenges?

> [!question]- Build vs Buy ошибки
> Стартап потратил 4 месяца на custom auth system, 3 месяца на custom payment integration и 2 месяца на custom analytics. Используя принципы Build vs Buy из файла, определите какие из этих решений были ошибкой и почему. Что следовало использовать вместо этого?

> [!question]- CTO + CEO relationship
> CEO хочет обещать клиенту feature через 2 недели. Вы как CTO считаете, что реалистичный срок — 6 недель. Используя healthy patterns для founder dynamics, как разрешить этот конфликт? Что значит 'disagree in private, united in public'?

## Ключевые карточки

Как эволюционирует роль CTO по стадиям стартапа?
?
Pre-seed: 80-90% coding, 10-20% other. Series A: 40-60% coding, 30-40% management, 10-20% strategy. Series B+: 0-20% coding, 50-60% leadership, 30-40% strategy.

Назови 4 распространённые Build vs Buy ошибки.
?
Building: auth system (use Auth0/Clerk), payment (use Stripe), email (use SendGrid), analytics (use Amplitude/Mixpanel). Build only core differentiators.

Что можно пропустить в MVP?
?
Skip: comprehensive testing, perfect architecture, scalability, admin tools. Do NOT skip: basic security (auth, encryption), data backups, basic monitoring, basic deployment automation.

Какие healthy patterns в CTO+CEO relationship?
?
Weekly 1-on-1 (minimum), disagree in private — united in public, clear decision rights, mutual respect. Warning signs: avoiding hard conversations, blaming each other to team.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[scaling-from-zero]] | Масштабирование после product-market fit |
| Углубиться | [[cto-vs-vpe]] | Когда нужен VP Engineering |
| Смежная тема | [[technical-due-diligence]] | Подготовка к DD инвесторов |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
