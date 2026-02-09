---
title: "Масштабирование инженерной организации"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: advanced
target-role: [director, vpe, cto]
prerequisites:
  - "[[building-engineering-team]]"
teaches:
  - stages of growth
  - reorgs
  - coordination patterns
unlocks:
  - "[[team-structures]]"
tags: [leadership, scaling, org-design, growth]
sources: [elegant-puzzle, team-topologies, conways-law]
---

# Масштабирование инженерной организации

> **TL;DR:** Scaling ≠ hiring more. Это изменение структур, процессов, культуры. Conway's Law: архитектура отражает org structure. Key stages: 10 → 30 → 100 → 300 engineers. Каждый требует разных подходов. Span of control: 5-8 reports на менеджера.

---

## Stages of Growth

```
STAGE 1: 1-10 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: One team, flat
Communication: Direct, informal
Process: Minimal
Leadership: Founder/Tech Lead

Challenges:
• Establishing culture
• First processes
• Defining roles

STAGE 2: 10-30 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: 2-4 teams
Communication: Still mostly direct
Process: Light (standups, reviews)
Leadership: First managers

Challenges:
• First reorg
• Manager/IC split
• Cross-team coordination

STAGE 3: 30-100 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Teams of teams
Communication: Formalized
Process: Necessary
Leadership: Manager layer, directors

Challenges:
• Communication overhead
• Culture dilution
• Middle management
• Platform/product split

STAGE 4: 100-300 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Departments
Communication: Structured
Process: Heavy
Leadership: VPs, multiple directors

Challenges:
• Coordination at scale
• Career paths
• Bureaucracy risk
• Maintaining velocity

STAGE 5: 300+ ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Multiple orgs
Communication: Async-heavy
Process: Platform-based
Leadership: Executive team

Challenges:
• Division autonomy
• Consistency vs flexibility
• Innovation pace
• Political complexity
```

## Conway's Law

```
"Organizations design systems that mirror
their communication structure."

IMPLICATION:
Want microservices? → Organize as small teams
Want platform? → Create platform team
Want speed? → Minimize dependencies

INVERSE CONWAY:
Design org to get architecture you want.
```

## Span of Control

```
OPTIMAL: 5-8 direct reports

<5 reports:
• Manager may micromanage
• Overhead high for value
• Career bottleneck

>8 reports:
• Not enough time per person
• 1-on-1s suffer
• Growth neglected

CALCULATION:
1-on-1s: 30 min × 8 = 4 hours/week
Team meetings: 2 hours/week
Admin/hiring: 5 hours/week
Stakeholders: 5 hours/week
Leaves: 20-24 hours for actual work
```

## When to Reorg

```
SIGNALS YOU NEED REORG:
• Team boundaries don't match architecture
• Too much cross-team coordination
• Teams too big (>10) or too small (<4)
• Unclear ownership
• Repeated conflicts
• Talent bottleneck

REORG PRINCIPLES:
1. Minimize disruption
2. Clear ownership post-reorg
3. Communicate extensively
4. Don't reorg too often (<18 months between)
5. Solve real problems, not perceived
```

## Coordination Mechanisms

```
AS YOU SCALE:

DIRECT (small):
Just talk to each other.

LIAISONS (medium):
Designated cross-team contacts.

CEREMONIES (medium-large):
Sync meetings, demos, planning.

DOCUMENTATION (large):
RFCs, ADRs, runbooks.

PLATFORM (very large):
Self-service, internal products.
```

---

## Связанные темы

- [[team-structures]] — структуры команд
- [[building-engineering-team]] — базовые принципы
- [[startup-cto]] — scaling в стартапах

## Источники

| Источник | Тип |
|----------|-----|
| [An Elegant Puzzle](https://www.amazon.com/Elegant-Puzzle-Systems-Engineering-Management/dp/1732265186) | Book |
| [Team Topologies](https://teamtopologies.com/) | Book |
| Conway's Law | Concept |

---

*Последнее обновление: 2026-01-18*
