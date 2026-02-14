---
title: "Масштабирование с нуля"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [cto, vpe, founding-engineer]
teaches:
  - growth stages challenges
  - technical scaling
  - organizational scaling
sources: [high-growth-handbook, scaling-teams, blitzscaling]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[startup-cto]]"
  - "[[scaling-engineering-org]]"
  - "[[technical-vision]]"
prerequisites:
  - "[[startup-cto]]"
  - "[[scaling-engineering-org]]"
  - "[[technical-vision]]"
reading_time: 15
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Масштабирование с нуля

> **TL;DR:** Scaling = solving different problems at each stage. 0→10: find product-market fit, speed over everything. 10→50: add process, first managers. 50→100+: organizational design, platform thinking. What worked yesterday breaks tomorrow. Rewrite is normal.

---

## Growth Stages Overview

```
STAGE 0→10 PEOPLE: SURVIVAL
┌─────────────────────────────────────────────────────┐
│ Focus: Find product-market fit                      │
│ Tech: MVP, speed over quality                       │
│ Org: Everyone does everything                       │
│ Risk: Building wrong thing                          │
└─────────────────────────────────────────────────────┘
          │
          ▼
STAGE 10→30 PEOPLE: FOUNDATION
┌─────────────────────────────────────────────────────┐
│ Focus: Repeatable growth                            │
│ Tech: Pay some tech debt, basic platform            │
│ Org: First managers, basic processes                │
│ Risk: Moving too slow, process overhead             │
└─────────────────────────────────────────────────────┘
          │
          ▼
STAGE 30→100 PEOPLE: STRUCTURE
┌─────────────────────────────────────────────────────┐
│ Focus: Scale what works                             │
│ Tech: Platform team, reliability focus              │
│ Org: Team structure, career ladders                 │
│ Risk: Politics, silos, losing culture               │
└─────────────────────────────────────────────────────┘
          │
          ▼
STAGE 100+ PEOPLE: OPTIMIZATION
┌─────────────────────────────────────────────────────┐
│ Focus: Efficiency at scale                          │
│ Tech: Microservices, dedicated teams                │
│ Org: Directors, VPs, formal hierarchy               │
│ Risk: Bureaucracy, innovation death                 │
└─────────────────────────────────────────────────────┘
```

## Stage 0→10: Survival Mode

```
TECHNICAL PRIORITIES:

DO:
✓ Ship fast, iterate faster
✓ Talk to customers daily
✓ Simple architecture (monolith OK)
✓ Use managed services (SaaS everything)
✓ Basic CI/CD

DON'T:
✗ Premature optimization
✗ Perfect code coverage
✗ Complex microservices
✗ Build what you can buy
✗ Plan for 10M users

TECHNOLOGY CHOICES:
• Monolith is fine
• PostgreSQL for everything
• One cloud provider
• Off-the-shelf auth/payments
• Simple deployment (Heroku, Railway, Render)

TEAM DYNAMICS:
• Everyone is full-stack
• CTO codes 80% of time
• No formal processes
• Decisions in Slack/Discord
• Async standups (if any)

TYPICAL PROBLEMS:
• What to build next?
• Running out of money?
• Finding first customers?
• Staying motivated?
```

## Stage 10→30: Building Foundation

```
TECHNICAL PRIORITIES:

DO:
✓ Pay critical tech debt
✓ Add monitoring and alerting
✓ Improve deployment reliability
✓ Document key systems
✓ Add basic testing (critical paths)

DON'T:
✗ Rewrite everything
✗ Over-engineer
✗ Complex org structures
✗ Too many processes

INFRASTRUCTURE EVOLUTION:
From: Heroku/Railway
To: AWS/GCP with Terraform

From: Single database
To: Read replicas, caching

From: Manual deployments
To: CI/CD with rollback

TEAM STRUCTURE:
• 2-3 teams (product, platform, mobile?)
• First managers (or tech leads)
• Weekly planning meetings
• Basic on-call rotation

HIRING CHALLENGES:
• Finding senior people
• Keeping culture while growing
• Onboarding speed
• First bad hire (and handling it)

COMMON MISTAKES:
• Hiring too fast
• Not hiring managers soon enough
• Ignoring tech debt too long
• Process for process sake
```

## Stage 30→100: Adding Structure

```
TECHNICAL PRIORITIES:

DO:
✓ Platform team formation
✓ Service decomposition (careful)
✓ Observability investment
✓ Developer productivity focus
✓ Security formalization

DON'T:
✗ Rewrite to microservices "just because"
✗ Ignore reliability
✗ Let teams diverge too much
✗ Forget documentation

ARCHITECTURE EVOLUTION:

Monolith → Modular Monolith → Services

Step 1: Modularize the monolith
• Clear boundaries between domains
• Internal APIs
• Separate databases (logical)

Step 2: Extract critical services
• High-change areas
• Different scaling needs
• Clear ownership possible

Step 3: Platform capabilities
• Shared auth/authz
• Observability
• Deployment pipeline

TEAM STRUCTURE:
• Squad model (careful of cargo cult)
• Engineering managers essential
• Tech leads in each team
• Architects / Staff engineers

ORGANIZATIONAL CHALLENGES:
• Communication overhead increases
• "Us vs them" between teams
• Inconsistent practices
• Career growth questions
```

## Stage 100+: Organizational Scale

```
TECHNICAL PRIORITIES:

DO:
✓ Platform engineering investment
✓ Internal developer portal
✓ Clear service ownership
✓ Cost optimization
✓ Multi-region / DR

CHALLENGES:

COORDINATION:
• Cross-team dependencies
• Release coordination
• API versioning
• Shared services governance

CONSISTENCY:
• Technology choices (golden paths)
• Security standards
• Operational practices
• Data management

EFFICIENCY:
• Cloud cost management
• Developer productivity metrics
• Reducing toil
• Build vs buy decisions

TEAM TOPOLOGIES:
• Stream-aligned teams (product)
• Platform teams (enablement)
• Complicated subsystem teams
• Enabling teams

LEADERSHIP STRUCTURE:
CTO
├── VP Engineering
│   ├── Engineering Directors
│   │   └── Engineering Managers
│   │       └── Tech Leads / Engineers
│   └── ...
├── VP Platform (maybe)
├── Chief Architect (maybe)
└── CISO (maybe)
```

## Technical Scaling Patterns

```
DATABASE SCALING:

STAGE 1: Single PostgreSQL
• Vertical scaling first
• Connection pooling (PgBouncer)
• Query optimization

STAGE 2: Read scaling
• Read replicas
• Caching layer (Redis)
• Denormalization

STAGE 3: Write scaling
• Sharding (careful!)
• Separate databases per service
• Event-driven architecture

API SCALING:

STAGE 1: Single API server
• Horizontal scaling (load balancer)
• CDN for static assets

STAGE 2: Service decomposition
• API gateway
• Service discovery
• Rate limiting

STAGE 3: Advanced patterns
• CQRS where needed
• Event sourcing (where needed)
• Multi-region

DEPLOYMENT SCALING:

STAGE 1: Simple CI/CD
• GitHub Actions / GitLab CI
• Single environment

STAGE 2: Structured pipeline
• Multiple environments
• Feature flags
• Canary deployments

STAGE 3: Advanced deployment
• Multi-region deployment
• Blue/green
• Automated rollback
```

## Organizational Scaling Patterns

```
PROCESS EVOLUTION:

STAGE 1 (0-10):
• No formal process
• Direct communication
• Everyone knows everything

STAGE 2 (10-30):
• Light scrum/kanban
• Regular planning
• Basic documentation
• 1-on-1s start

STAGE 3 (30-100):
• Formal sprint planning
• OKRs introduction
• Cross-team coordination
• Architecture review

STAGE 4 (100+):
• RFC process
• Architecture council
• Formal roadmap planning
• Regular retrospectives

COMMUNICATION SCALING:

0-10: Slack channel, everyone reads everything
10-30: Team channels, weekly all-hands
30-100: Structured updates, skip-levels
100+: Internal newsletters, formal cascading

DECISION MAKING:

0-10: CTO decides or quick consensus
10-30: Tech leads decide in their area
30-100: RFC process for big decisions
100+: Architecture review board, ADRs
```

## When to Rewrite

```
SIGNS IT'S TIME:

• Deploys take hours (should be minutes)
• Every change breaks something
• Can't hire because of stack
• Security fundamentally broken
• Cost scaling faster than revenue

REWRITE PRINCIPLES:

STRANGLER FIG PATTERN:
1. New features in new system
2. Gradually migrate traffic
3. Eventually sunset old system

RULES:
• Never stop shipping features
• Rewrite piece by piece
• Old and new must coexist
• Define clear cutover criteria

WHAT TO REWRITE:
• Core domain logic
• Performance bottlenecks
• Security-critical paths

WHAT NOT TO REWRITE:
• Working admin tools
• Rarely changed code
• Things that will change anyway

TIMELINE EXPECTATION:
Small service: 1-3 months
Core service: 3-6 months
Full platform: 1-2 years (incremental)
```

## Cultural Scaling

```
CULTURE AT EACH STAGE:

STARTUP (0-30):
• Founder-driven culture
• Implicit values
• High trust, low process
• "Family" feeling

GROWTH (30-100):
• Values need documentation
• Subcultures form in teams
• Trust must be explicit
• Culture carriers needed

SCALE (100+):
• Formal culture programs
• Onboarding crucial
• Values in hiring/reviews
• Leadership modeling

PRESERVING CULTURE:

DO:
✓ Document values early
✓ Hire for culture add (not fit)
✓ Culture in interview process
✓ Leaders model values
✓ Celebrate culture examples

DON'T:
✗ Assume culture just happens
✗ Ignore culture problems
✗ Let jerks succeed
✗ Scale too fast to absorb

WARNING SIGNS:
• "Things were better before"
• Values only on wall
• Different rules for top performers
• Blame culture emerging
• Innovation slowing
```

## Common Scaling Mistakes

```
TECHNICAL:

✗ Microservices too early
"We have 3 engineers and 15 services"

✗ Ignoring reliability
"We'll fix it when we scale"

✗ Technology resume-driven
"Let's use Kubernetes for 5 users"

✗ Not investing in dev experience
"Deploy takes 2 hours but it's fine"

ORGANIZATIONAL:

✗ Hiring too fast
"We raised money, hire 50 people!"

✗ Not hiring managers
"We don't need managers, we're flat"

✗ Process cargo cult
"Let's do SAFe because Google does"

✗ Keeping wrong people
"They were here from the start"

LEADERSHIP:

✗ CTO still coding at 50 people
"But I'm the best engineer"

✗ Not delegating decisions
"I need to approve everything"

✗ Avoiding hard conversations
"Maybe they'll improve on their own"

✗ Not preparing for next stage
"We'll figure it out when we get there"
```

---

## Связь с другими темами

**[[startup-cto]]** — Масштабирование с нуля напрямую определяет эволюцию роли CTO: от 80% кодирования на стадии 0-10 до 0% кодирования на стадии 100+. CTO должен менять свой стиль лидерства на каждом этапе роста, и неспособность адаптироваться — одна из главных причин замены CTO в растущих компаниях. Понимание этапов масштабирования помогает CTO заранее готовиться к следующему transition.

**[[scaling-engineering-org]]** — Масштабирование с нуля в стартапе и масштабирование инженерной организации описывают один процесс с разных ракурсов: startup-контекст добавляет ограничения по бюджету, скорости и культуре. Организационные паттерны (Conway's Law, span of control, coordination mechanisms) применяются на каждом этапе роста стартапа, но с учётом ограниченных ресурсов. Reorg в стартапе из 30 человек кардинально отличается от реорганизации в компании с 300 инженерами.

**[[technical-vision]]** — Технический vision определяет архитектурные решения на каждом этапе масштабирования: когда переходить от монолита к сервисам, когда инвестировать в platform team. Без долгосрочного технического видения масштабирование превращается в постоянное тушение пожаров и бесконечные переписывания. Strangler Fig pattern и другие паттерны миграции — практическое применение технической vision при масштабировании.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Ries E. (2011) *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses* | Книга |
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |


## Проверь себя

> [!question]- Monolith -> Services timing
> Стартап с 5 инженерами и 3 services (auth, payment, core) — CTO решил начать с микросервисов. Deploy pipeline сложный, debugging cross-service issues занимает дни. Используя stage model 0->10, объясните почему microservices too early и предложите architecture rollback plan.

> [!question]- Strangler Fig pattern
> Монолит стартапа достиг предела: deploys take 2 hours, every change breaks something. 45 инженеров. Используя Strangler Fig pattern, опишите поэтапный plan миграции без остановки feature delivery.

> [!question]- Cultural scaling challenge
> 'Things were better before' — частая фраза в стартапе, выросшем с 15 до 60 человек за год. Используя Cultural Scaling section, определите root causes и предложите concrete preservation strategies.

## Ключевые карточки

Назови 4 стадии масштабирования стартапа.
?
0-10: SURVIVAL (find PMF, speed over everything). 10-30: FOUNDATION (first processes, pay tech debt). 30-100: STRUCTURE (team boundaries, platform thinking). 100+: OPTIMIZATION (efficiency at scale).

Что такое Strangler Fig pattern?
?
1. New features in new system. 2. Gradually migrate traffic. 3. Eventually sunset old system. Rules: never stop shipping features, rewrite piece by piece, old and new coexist, clear cutover criteria.

Какой правильный technology evolution при масштабировании?
?
0-10: monolith, PostgreSQL, simple deploy (Heroku/Railway). 10-30: AWS/GCP + Terraform, read replicas, CI/CD. 30-100: modular monolith -> services, platform team. 100+: microservices, internal developer portal.

Какие ошибки масштабирования наиболее опасны?
?
Tech: microservices too early, ignoring reliability, resume-driven tech. Org: hiring too fast, not hiring managers, process cargo cult. Leadership: CTO still coding at 50 people, not delegating decisions.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[startup-cto]] | Эволюция роли CTO при росте |
| Углубиться | [[scaling-engineering-org]] | Организационное масштабирование |
| Смежная тема | [[performance-optimization]] | Технические паттерны масштабирования |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
