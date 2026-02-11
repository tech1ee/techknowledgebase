---
title: "Структуры команд"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, vpe]
teaches:
  - spotify model
  - team topologies
  - trade-offs
sources: [team-topologies, spotify-model, scaling-up]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[scaling-engineering-org]]"
  - "[[engineering-metrics]]"
prerequisites:
  - "[[building-engineering-team]]"
  - "[[em-fundamentals]]"
---

# Структуры команд

> **TL;DR:** Нет универсальной structure. Spotify model часто misunderstood (сами Spotify от него отошли). Team Topologies: stream-aligned, platform, enabling, complicated-subsystem. Главное: minimize cognitive load, clear ownership, fast flow.

---

## Team Topologies

```
4 ТИПА КОМАНД:

1. STREAM-ALIGNED TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aligned to business stream/flow.
End-to-end ownership.
Primary type (~80% of teams).

Example: "Checkout team", "Onboarding team"

2. ENABLING TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Helps other teams adopt capabilities.
Temporary engagement.
Coaches, not builds.

Example: "DevOps enablement", "Security coaching"

3. COMPLICATED-SUBSYSTEM TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Owns complex subsystem requiring specialists.
Reduces cognitive load for stream teams.

Example: "ML platform", "Payment processing"

4. PLATFORM TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provides internal services/platform.
Treats other teams as customers.
Enables self-service.

Example: "Developer experience", "Infrastructure"
```

## Spotify Model (Critically)

```
ORIGINAL COMPONENTS:
• Squads: Cross-functional teams (~8)
• Tribes: Collection of squads (same area)
• Chapters: Functional group across squads
• Guilds: Interest communities

WHAT PEOPLE GET WRONG:
✗ It's a "model" to copy
✗ It still works at Spotify
✗ Matrix structures are simple

REALITY:
• Spotify evolved past this
• Works for some, not all
• Matrix reporting is hard
• Requires strong culture

TAKEAWAYS:
✓ Autonomy for teams
✓ Cross-team knowledge sharing
✓ Community of practice
✗ Exact structure to copy
```

## Functional vs Cross-Functional

```
FUNCTIONAL (by skill):
┌─────────────────────────────────────┐
│         Engineering                 │
├───────────┬───────────┬────────────┤
│ Frontend  │ Backend   │ DevOps     │
└───────────┴───────────┴────────────┘

+ Deep expertise
+ Clear career paths
- Handoffs between groups
- Slower delivery

CROSS-FUNCTIONAL (by product):
┌─────────────────────────────────────┐
│ Product A  │ Product B  │ Product C │
│ FE+BE+Ops  │ FE+BE+Ops  │ FE+BE+Ops │
└────────────┴────────────┴───────────┘

+ Fast delivery
+ End-to-end ownership
- Duplication possible
- Career growth harder
```

## Choosing Structure

```
CONSIDERATIONS:

1. COGNITIVE LOAD
   Can team understand their domain?
   Too big scope = overwhelm

2. DEPENDENCIES
   How often need other teams?
   High deps = slow flow

3. COMMUNICATION
   Who needs to talk?
   Design org to minimize required comm

4. OWNERSHIP
   Clear who owns what?
   Unclear = dropped balls

5. GROWTH
   Career paths visible?
   Specialist vs generalist tracks

RULE OF THUMB:
• Small (<30): functional often ok
• Medium (30-100): hybrid
• Large (100+): product-aligned
```

---

## Связь с другими темами

**[[scaling-engineering-org]]** — Структуры команд являются основным инструментом масштабирования инженерной организации. При росте с 10 до 300+ инженеров необходимо пересматривать team topology — от плоской структуры к stream-aligned, platform и enabling командам. Правильный выбор структуры минимизирует cognitive load, обеспечивает clear ownership и ускоряет поток создания ценности.

**[[engineering-metrics]]** — Эффективность выбранной структуры команд можно и нужно измерять через инженерные метрики. DORA metrics (deployment frequency, lead time) показывают, насколько хорошо структура команд поддерживает быструю доставку. Если метрики ухудшаются при росте — это сигнал к пересмотру team topology и организационного дизайна.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |
| Lencioni P. (2002) *The Five Dysfunctions of a Team: A Leadership Fable* | Книга |
| Drucker P. (2006) *The Effective Executive: The Definitive Guide to Getting the Right Things Done* | Книга |

---

*Последнее обновление: 2026-01-18*
