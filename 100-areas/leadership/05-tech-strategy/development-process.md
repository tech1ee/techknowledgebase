---
title: "Процессы разработки"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: intermediate
target-role: [em, tech-lead]
prerequisites:
  - "[[engineering-practices]]"
teaches:
  - git workflows
  - sprint planning
  - release management
unlocks:
  - "[[agile-practices]]"
tags: [leadership, process, git, agile, development]
sources: [trunk-based-dev, git-flow, continuous-delivery]
---

# Процессы разработки

> **TL;DR:** Process должен помогать, не мешать. Trunk-based development > Git Flow для большинства. Short-lived branches (<1 day), feature flags для incomplete work. Sprint planning: realistic commitments. Release: часто, маленькими частями, автоматизированно.

---

## Git Workflows

```
TRUNK-BASED DEVELOPMENT (recommended):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main ─●─●─●─●─●─●─●─●→
       ↑ ↑   ↑
       Short-lived feature branches
       (hours, max 1-2 days)

+ Continuous integration
+ Less merge conflicts
+ Forces small changes
+ Works with feature flags

GIT FLOW (legacy, avoid):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main    ─●───────────●─────→
develop ─●─●─●─●─●─●─●─●─●─→
feature ──┬─●─●─●─┘
          Long-lived branches

- Merge conflicts
- Delayed integration
- Complex branching

GITHUB FLOW (simple):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main ─●─●─●─●─●─●→
       ↑ ↑
       Feature branches + PR
       Deploy from main

Good balance for most teams.
```

## Sprint Process

```
SPRINT PLANNING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Duration: 1-2 weeks
Commitment: 80% of capacity (buffer)

INPUT:
• Prioritized backlog
• Team capacity
• Carry-over from last sprint

OUTPUT:
• Sprint goal
• Committed items
• Clear acceptance criteria

DAILY STANDUP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Duration: 15 min max
Focus: Blockers, not status

Format:
1. What I completed
2. What I'm working on
3. Any blockers

SPRINT REVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demo working software
Stakeholder feedback
Celebrate wins

RETROSPECTIVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What worked well?
What didn't?
What to try next sprint?
ACTION ITEMS (1-3 max)
```

## Release Management

```
RELEASE FREQUENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Deploy frequently, small changes

Daily: Ideal for web apps
Weekly: Common for APIs
Bi-weekly: If more coordination needed

RELEASE CHECKLIST:
□ Tests passing
□ Code reviewed
□ Staging verified
□ Rollback plan ready
□ Monitoring in place
□ Communication sent

FEATURE FLAGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploy code hidden behind flags.
Enable for % of users.
Instant rollback = disable flag.

Tools: LaunchDarkly, Split, internal

ROLLBACK STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Database migrations reversible
• Feature flags for instant disable
• Automated rollback on error spike
• Previous version always deployable
```

## Definition of Done

```
TASK DONE WHEN:
□ Code complete
□ Tests written and passing
□ Code reviewed
□ Documentation updated
□ Deployed to staging
□ Product sign-off (if needed)

SPRINT DONE WHEN:
□ All committed items done
□ Demos prepared
□ Retro action items from last sprint completed

RELEASE DONE WHEN:
□ Deployed to production
□ Monitoring confirms healthy
□ Stakeholders notified
□ Documentation public
```

---

## Связанные темы

- [[engineering-practices]] — практики качества
- [[agile-practices]] — agile методологии
- [[scaling-engineering-org]] — процессы при масштабе

## Источники

| Источник | Тип |
|----------|-----|
| [Trunk Based Development](https://trunkbaseddevelopment.com/) | Guide |
| [Continuous Delivery](https://continuousdelivery.com/) | Book/Site |
| [Feature Flags](https://martinfowler.com/articles/feature-toggles.html) | Article |

---

*Последнее обновление: 2026-01-18*
