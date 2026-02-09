---
title: "OKRs и KPIs для инженерии"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, vpe]
teaches:
  - OKR framework
  - KPIs vs OKRs
  - engineering-specific OKRs
sources: [measure-what-matters, radical-focus, google-okrs]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[engineering-metrics]]"
  - "[[strategic-thinking]]"
---

# OKRs и KPIs для инженерии

> **TL;DR:** OKRs (Objectives + Key Results) — framework для ambitious goals. KPIs — ongoing health metrics. OKRs: quarterly, stretch (70% = good). KPIs: continuous, 100% target. Не превращай OKRs в to-do list. Engineering OKRs: balance бизнес-outcome и tech health.

---

## OKRs vs KPIs

```
OKRs:                           KPIs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Quarterly goals               • Ongoing health metrics
• Ambitious (stretch)           • Target = expected
• 70% = success                 • 100% = success
• Drive change                  • Monitor status
• Few (3-5 per level)           • Many possible
• Public, collaborative         • Operational

EXAMPLE:
OKR: "Reduce page load time by 50%"
     (Ambitious, time-bound)

KPI: "P99 latency < 200ms"
     (Ongoing threshold)
```

## OKR Structure

```
OBJECTIVE:
Qualitative, inspiring, time-bound
"What do we want to achieve?"

KEY RESULTS (3-5 per objective):
Quantitative, measurable
"How do we know we achieved it?"

EXAMPLE:
Objective: Become the most reliable platform

Key Results:
KR1: Achieve 99.9% uptime (from 99.5%)
KR2: Reduce P99 latency to 200ms (from 500ms)
KR3: Zero critical incidents in Q2
KR4: Customer complaints about reliability -50%

SCORING (Google method):
0.0-0.3 = Red (need attention)
0.4-0.6 = Yellow (progress)
0.7-1.0 = Green (strong)

1.0 = You set bar too low
0.7 = Ideal target
```

## Engineering OKR Examples

```
DELIVERY-FOCUSED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O: Ship product X that delights customers
KR1: Launch V1 by March 15
KR2: 100 beta users with NPS > 50
KR3: <5 critical bugs in first month

QUALITY-FOCUSED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O: Dramatically improve engineering quality
KR1: Test coverage 60% → 80%
KR2: Change failure rate 20% → 10%
KR3: Code review turnaround < 4 hours

VELOCITY-FOCUSED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O: Increase delivery speed sustainably
KR1: Deploy frequency daily (from weekly)
KR2: Lead time 1 day (from 5 days)
KR3: Developer satisfaction score > 4/5

PLATFORM-FOCUSED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O: Enable product teams to move faster
KR1: Time to first deploy for new service < 1 day
KR2: Self-service for 90% of infra needs
KR3: Platform NPS from internal teams > 40
```

## OKR Process

```
QUARTERLY CYCLE:

WEEK 1-2: Draft OKRs
• Leadership drafts company OKRs
• Teams draft aligned team OKRs
• Individual goals (optional)

WEEK 3: Alignment
• Review cross-team dependencies
• Adjust for conflicts
• Finalize

WEEKS 4-12: Execute
• Check in weekly (are we on track?)
• Adjust tactics, not OKRs

WEEK 13: Score & Reflect
• Score each KR (0.0-1.0)
• Retrospective: what worked?
• Feed into next quarter

COMMON MISTAKES:
✗ Too many OKRs (>5)
✗ Not ambitious enough (all 1.0s)
✗ Key Results are tasks, not outcomes
✗ Set and forget
✗ Tied to bonuses (discourages stretch)
```

## KPIs для Engineering

```
STANDARD ENGINEERING KPIs:

RELIABILITY:
• Uptime %
• MTTR
• Incident count

VELOCITY:
• Deploy frequency
• Lead time
• Cycle time

QUALITY:
• Bug escape rate
• Change failure rate
• Technical debt ratio

DEVELOPER EXPERIENCE:
• Build time
• Test suite time
• Onboarding time

TEAM HEALTH:
• Developer satisfaction
• Attrition rate
• Referral rate
```

---

## Связанные темы

- [[engineering-metrics]] — what to measure
- [[strategic-thinking]] — setting direction
- [[performance-management]] — individual goals

## Источники

| Источник | Тип |
|----------|-----|
| [Measure What Matters](https://www.whatmatters.com/) | Book (John Doerr) |
| [Radical Focus](https://www.amazon.com/Radical-Focus-Achieving-Important-Objectives/dp/0996006028) | Book |
| [Google OKRs](https://rework.withgoogle.com/guides/set-goals-with-okrs/) | Guide |

---

*Последнее обновление: 2026-01-18*
