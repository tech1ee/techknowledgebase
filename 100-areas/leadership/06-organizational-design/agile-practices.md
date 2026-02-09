---
title: "Agile практики"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: beginner
target-role: [em, tech-lead, scrum-master]
prerequisites:
  - "[[development-process]]"
teaches:
  - scrum vs kanban
  - что работает
  - критический взгляд
unlocks:
  - "[[engineering-practices]]"
tags: [leadership, agile, scrum, kanban, methodology]
sources: [agile-manifesto, scrum-guide, kanban-method]
---

# Agile практики

> **TL;DR:** Agile — mindset, не framework. Scrum и Kanban — implementations. Scrum: sprints, ceremonies, roles. Kanban: flow, WIP limits, visualize. Оба работают. Проблема: "cargo cult agile" — ceremonies без понимания why. Ретроспективы — самая ценная практика.

---

## Agile Manifesto (напоминание)

```
ЦЕННОСТИ:

Individuals & interactions    > Processes & tools
Working software              > Comprehensive docs
Customer collaboration        > Contract negotiation
Responding to change          > Following a plan

"То что слева важнее, но правое тоже имеет ценность"
```

## Scrum Essentials

```
ROLES:
• Product Owner: what to build, priorities
• Scrum Master: process, remove blockers
• Dev Team: how to build, execution

CEREMONIES:
• Sprint Planning: what to commit
• Daily Standup: sync, blockers
• Sprint Review: demo to stakeholders
• Retrospective: improve process

ARTIFACTS:
• Product Backlog: all work items
• Sprint Backlog: committed for sprint
• Increment: working software

SPRINT:
Duration: 1-4 weeks (2 common)
Goal: Ship potentially releasable increment
```

## Kanban Essentials

```
PRINCIPLES:
1. Visualize work
2. Limit WIP (work in progress)
3. Manage flow
4. Make policies explicit
5. Feedback loops
6. Improve collaboratively

BOARD:
┌──────────┬──────────┬──────────┬──────────┐
│ Backlog  │ In Prog  │ Review   │ Done     │
│          │ (WIP: 3) │ (WIP: 2) │          │
├──────────┼──────────┼──────────┼──────────┤
│ Item A   │ Item B   │ Item D   │ Item E   │
│ Item C   │ Item F   │          │ Item G   │
│          │ Item H   │          │          │
└──────────┴──────────┴──────────┴──────────┘

WIP LIMITS:
Prevent overload.
Force finishing before starting.
```

## Scrum vs Kanban

```
                 SCRUM              KANBAN
─────────────────────────────────────────────────
Cadence          Fixed sprints      Continuous
Roles            Defined (PO, SM)   Flexible
Changes          Next sprint        Anytime
Metrics          Velocity           Lead time, WIP
Planning         Sprint planning    JIT planning
Best for         New products       Operations, support
```

## What Actually Works

```
KEEP (высокая ценность):
✓ Retrospectives
✓ Daily standups (short!)
✓ Visual boards
✓ WIP limits
✓ Demo/review with stakeholders
✓ Regular planning

OPTIONAL (depends on context):
○ Story points
○ Strict sprint boundaries
○ Formal roles
○ Burn-down charts

AVOID (low value, high cost):
✗ Estimation obsession
✗ Ceremonies without purpose
✗ "Agile police"
✗ Metrics gaming
```

## Common Anti-Patterns

```
❌ ZOMBIE SCRUM
Daily standups + no improvement.
Going through motions.

❌ CARGO CULT
"We do sprints" but no iteration.
Ceremonies without understanding.

❌ WATERFALL IN DISGUISE
3-month "sprint" = waterfall.
Big upfront planning.

❌ NO STAKEHOLDER INVOLVEMENT
Team works in vacuum.
Demo to empty room.

❌ SKIPPING RETROS
"We're too busy."
→ Never improve.
```

---

## Связанные темы

- [[development-process]] — процессы разработки
- [[team-dynamics]] — team ceremonies
- [[engineering-practices]] — technical practices

## Источники

| Источник | Тип |
|----------|-----|
| [Agile Manifesto](https://agilemanifesto.org/) | Foundation |
| [Scrum Guide](https://scrumguides.org/) | Guide |
| [Kanban Method](https://kanbanize.com/kanban-resources/getting-started/what-is-kanban) | Guide |

---

*Последнее обновление: 2026-01-18*
