---
title: "Архитектурные решения (ADR)"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [tech-lead, em, staff-engineer]
teaches:
  - ADR формат
  - принятие решений
  - документирование
sources: [adr-github, thoughtworks, michael-nygard]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[tech-lead-role]]"
  - "[[technical-vision]]"
prerequisites:
  - "[[tech-lead-role]]"
  - "[[engineering-practices]]"
---

# Архитектурные решения (ADR)

> **TL;DR:** ADR (Architecture Decision Record) — документ фиксирующий ПОЧЕМУ приняли решение, не только ЧТО. Контекст теряется, люди уходят, через год никто не помнит почему так. ADR: Status, Context, Decision, Consequences. Хранить в repo рядом с кодом.

---

## Зачем ADR

```
БЕЗ ADR:
"Почему мы используем X?"
"Не знаю, так было когда я пришёл."
"Наверное можно переписать на Y..."
[Месяц работы, discover why X was chosen]
[X был правильным выбором]

С ADR:
"Почему мы используем X?"
[Читает ADR-003]
"А, потому что [контекст]. Это всё ещё актуально."
```

## ADR Format (Michael Nygard)

```markdown
# ADR-[number]: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[What is the issue? What forces are at play?]
- Technical constraints
- Business requirements
- Team capabilities
- Timeline pressure

## Decision
[What is the change we're making?]
We will use [X] because [Y].

## Consequences
[What becomes easier or harder?]

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Tradeoff 1]
- [Tradeoff 2]

### Risks
- [Risk and mitigation]

---
Date: YYYY-MM-DD
Authors: [Names]
```

## Example ADR

```markdown
# ADR-015: Use PostgreSQL for primary database

## Status
Accepted

## Context
We need to choose a primary database for our
new order management system. Requirements:
- ACID transactions for financial data
- Complex queries for reporting
- Team has SQL experience
- Expected 100K orders/day

Options considered:
1. PostgreSQL
2. MySQL
3. MongoDB

## Decision
We will use PostgreSQL because:
- Strong ACID compliance
- Rich feature set (JSONB, full-text search)
- Team experience
- Excellent tooling
- Active community

## Consequences

### Positive
- Reliable transactions
- Familiar technology
- Good performance for our scale
- Can use JSONB for flexible schemas

### Negative
- Horizontal scaling more complex than NoSQL
- Need to manage connections carefully

### Risks
- If scale exceeds 10x projection, may need sharding
- Mitigation: design for read replicas from start

---
Date: 2026-01-15
Authors: Alice, Bob
Reviewers: CTO
```

## When to Write ADR

```
WRITE ADR FOR:
✓ Database choices
✓ Major framework decisions
✓ API design patterns
✓ Security approaches
✓ Integration patterns
✓ Significant refactorings
✓ Technology adoption/deprecation

DON'T NEED ADR FOR:
✗ Library version bumps
✗ Minor refactoring
✗ Obvious choices
✗ Temporary experiments
```

## Decision Making Process

```
1. IDENTIFY: Architectural decision needed

2. RESEARCH: Options, trade-offs, constraints

3. PROPOSE: Write ADR in "Proposed" status

4. REVIEW: Team discussion, async or meeting

5. DECIDE: Update to "Accepted" or reject

6. IMPLEMENT: Reference ADR in code/PRs

7. REVISIT: Update if context changes

STORAGE:
docs/adr/ or similar in repo
Version controlled with code
```

## Связанные темы

- [[tech-debt-management]] — долг от плохих решений
- [[technical-vision]] — долгосрочное направление
- [[engineering-practices]] — практики принятия решений

## Источники

| Источник | Тип |
|----------|-----|
| [ADR GitHub](https://adr.github.io/) | Resource |
| [Michael Nygard ADR](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Article |
| [ThoughtWorks Tech Radar](https://www.thoughtworks.com/radar) | Reference |

---

## Связь с другими темами

**[[tech-lead-role]]** — Tech Lead — основной author и driver ADR в команде. Архитектурные решения — одна из ключевых обязанностей Tech Lead, и ADR формализует этот процесс. Без ADR решения принимаются устно и теряются, когда люди уходят. Tech Lead, создающий culture of documentation через ADR, оставляет lasting impact, который переживёт его пребывание в команде.

**[[technical-vision]]** — ADR и tech vision работают на разных уровнях абстракции: vision описывает направление (куда идём), а ADR фиксирует конкретные решения (как идём). Каждый ADR должен быть aligned с tech vision, и вместе они формируют coherent technical narrative. Без vision ADR становятся изолированными решениями, без ADR vision остаётся абстрактным документом без execution.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Описывает, как принимаются архитектурные решения на разных уровнях организации: от Tech Lead, принимающего решения для команды, до CTO, определяющего strategic technical direction. Процесс decision-making — ключевая competency на каждом уровне.
- **Kim et al., "The Phoenix Project" (2016)** — Демонстрирует, как отсутствие documented decisions и poor communication между командами приводит к organizational chaos. ADR — это один из инструментов, предотвращающих ситуации, описанные в книге, когда "никто не знает, почему мы это делаем".
- **Will Larson, "Staff Engineer" (2022)** — Описывает writing architecture documents как одну из core activities Staff Engineer. Larson показывает, как writing (включая ADR и design docs) является инструментом influence и alignment на organizational level.

---

*Последнее обновление: 2026-01-18*
