---
title: "Кризисный менеджмент"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [director, vpe, cto]
teaches:
  - incident response
  - communication during crisis
  - post-mortem leadership
sources: [incident-management, crisis-leadership, blameless-postmortems]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[stakeholder-management]]"
  - "[[executive-communication]]"
  - "[[startup-cto]]"
prerequisites:
  - "[[stakeholder-management]]"
  - "[[executive-communication]]"
  - "[[em-fundamentals]]"
reading_time: 12
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Кризисный менеджмент

> **TL;DR:** Crisis reveals leadership. Key: быстро assess, clear communication, decisive action. During crisis — solve, not blame. After — blameless postmortem. Preparation: runbooks, war games, clear escalation. Your calm = team's calm.

---

## Types of Engineering Crises

```
TECHNICAL:
• Production outage (P0/P1)
• Security breach / data leak
• Data loss or corruption
• Major performance degradation

ORGANIZATIONAL:
• Key person departure (bus factor)
• Team conflict escalation
• Mass resignation threat
• Deadline impossible to meet

EXTERNAL:
• Vendor/partner failure
• Regulatory compliance issue
• PR/reputation crisis
• Customer escalation (enterprise)

BUSINESS:
• Funding crisis
• Acquisition/layoffs
• Pivot announcement
• Major customer loss
```

## Incident Response Framework

```
PHASE 1: DETECT & ASSESS (0-5 min)
┌─────────────────────────────────┐
│ • What's broken?                │
│ • Who's affected?               │
│ • What's the blast radius?      │
│ • Is it getting worse?          │
└─────────────────────────────────┘

PHASE 2: ASSEMBLE & ASSIGN (5-15 min)
┌─────────────────────────────────┐
│ • Incident Commander (you?)     │
│ • Technical Lead               │
│ • Communications Lead           │
│ • Scribe/Note-taker            │
└─────────────────────────────────┘

PHASE 3: MITIGATE (15 min - hours)
┌─────────────────────────────────┐
│ • Stop the bleeding            │
│ • Rollback if possible         │
│ • Workaround if needed         │
│ • Regular status updates       │
└─────────────────────────────────┘

PHASE 4: RESOLVE & COMMUNICATE
┌─────────────────────────────────┐
│ • Confirm fix                  │
│ • Monitor for recurrence       │
│ • Final stakeholder update     │
│ • Schedule postmortem          │
└─────────────────────────────────┘
```

## Incident Commander Role

```
RESPONSIBILITIES:
• Own the incident end-to-end
• Make decisions (even imperfect ones)
• Coordinate resources
• Manage communication flow
• Keep everyone focused

DO:
✓ Stay calm (your panic spreads)
✓ Make decisions with 70% info
✓ Delegate clearly
✓ Communicate frequently
✓ Document everything
✓ Take breaks if long incident

DON'T:
✗ Debug yourself (coordinate instead)
✗ Let chaos reign (assign roles)
✗ Go silent (status every 30 min)
✗ Blame anyone during incident
✗ Make permanent decisions under stress
```

## Communication During Crisis

```
INTERNAL COMMUNICATION:

WAR ROOM UPDATES (every 15-30 min):
"Status update: [timestamp]
Current state: [what's happening]
Actions in progress: [who doing what]
Next update: [time]"

ESCALATION TO EXEC:
"[Severity] incident started [time].
Impact: [customer/revenue/data].
Team is working on [action].
ETA to resolution: [estimate or unknown].
I'll update in [time] or if significant change."

EXTERNAL COMMUNICATION:

TO CUSTOMERS (via support/status page):
"We're aware of [issue] affecting [what].
Our team is actively working on resolution.
We'll update every [time] or when resolved.
We apologize for the inconvenience."

POST-RESOLUTION:
"[Issue] has been resolved as of [time].
Root cause: [brief, non-technical].
We're implementing measures to prevent recurrence.
Full postmortem available [when/where]."
```

## Decision Making Under Pressure

```
THE 70% RULE:
Make decision with 70% information.
Waiting for 100% = too late.

REVERSIBLE vs IRREVERSIBLE:
• Reversible: decide fast, adjust later
• Irreversible: pause, get more input

WHEN STUCK:
1. What's the worst case if we do X?
2. What's the worst case if we do nothing?
3. Which is worse?
4. Act accordingly.

DECISION LOG:
[Time] Decision: [what]
        Options considered: [A, B, C]
        Chose [X] because [reason]
        Owner: [who]
```

## Blameless Postmortem

```
TIMING:
• Schedule within 48-72 hours
• While memory is fresh
• After people have rested

PARTICIPANTS:
• All involved in incident
• Relevant stakeholders
• Optional: learning observers

STRUCTURE:
1. Timeline reconstruction
2. What happened (facts only)
3. Contributing factors
4. What went well
5. What could improve
6. Action items with owners

BLAMELESS PRINCIPLES:
• Assume good intent
• Focus on systems, not people
• "What" not "who"
• Human error = system failure
• Learning > punishment

QUESTIONS TO ASK:
• What made this possible?
• What information was missing?
• What would have prevented this?
• What made detection/recovery slow?
• What would help next time?
```

## Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date:** [Date]
**Severity:** P0/P1/P2
**Duration:** [Start] - [End] ([total time])
**Author:** [Name]
**Status:** Draft / Final

## Summary
[2-3 sentences: what happened, impact, resolution]

## Impact
- Users affected: [number]
- Revenue impact: [if applicable]
- Data affected: [if applicable]

## Timeline (all times UTC)
| Time | Event |
|------|-------|
| 14:00 | Alert fired for... |
| 14:05 | On-call acknowledged... |
| ... | ... |

## Root Cause
[Technical explanation of what caused the incident]

## Contributing Factors
1. [Factor 1]
2. [Factor 2]

## What Went Well
- [Positive 1]
- [Positive 2]

## What Could Improve
- [Improvement 1]
- [Improvement 2]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | Open |

## Lessons Learned
[Key takeaways for the team/org]
```

## Crisis Prevention

```
RUNBOOKS:
Document common failure scenarios.
Step-by-step recovery procedures.
Contact lists and escalation paths.
Update after each incident.

WAR GAMES:
Regular disaster simulations.
"Game day" exercises.
Test runbooks work.
Build muscle memory.

MONITORING & ALERTS:
Detect before customers do.
Actionable alerts (not noise).
Clear severity definitions.
On-call rotation.

ARCHITECTURE RESILIENCE:
Graceful degradation.
Circuit breakers.
Rollback capabilities.
Backup and recovery tested.
```

## Organizational Crisis Leadership

```
LAYOFFS / REORG:

BEFORE ANNOUNCEMENT:
• Plan communication carefully
• Prepare FAQ
• Brief managers first
• Have 1-on-1 time scheduled

DURING:
• Be direct and compassionate
• Explain the why
• Be available for questions
• Don't disappear

AFTER:
• Address survivor guilt
• Reset expectations
• Rebuild trust over time

KEY PERSON DEPARTURE:

IMMEDIATE:
• Assess knowledge gaps
• Identify bus factor risks
• Communication to team

SHORT-TERM:
• Knowledge transfer sessions
• Document critical processes
• Redistribute responsibilities

LONG-TERM:
• Hire replacement or restructure
• Reduce single points of failure
• Cross-training programs
```

## Leader's Self-Care During Crisis

```
DURING CRISIS:
• Take 5-min breaks
• Eat and hydrate
• Rotate if long incident
• It's OK to not know everything

AFTER CRISIS:
• Debrief with peer/mentor
• Rest before postmortem
• Acknowledge the stress
• Thank your team

SIGNS OF BURNOUT:
• Decision fatigue
• Snapping at people
• Tunnel vision
• Physical exhaustion

REMEMBER:
You can't pour from empty cup.
Your team mirrors your energy.
It's not your fault (usually).
This too shall pass.
```

---

## Связь с другими темами

**[[stakeholder-management]]** — Во время кризиса управление stakeholders становится критически важным: нужно правильно эскалировать, информировать руководство и управлять ожиданиями клиентов. Кризис обнажает качество отношений со стейкхолдерами — доверие, построенное заранее, позволяет быстрее принимать решения и получать поддержку. Навыки influence without authority особенно важны при координации кросс-функциональной команды реагирования.

**[[executive-communication]]** — Коммуникация во время кризиса требует предельной ясности: BLUF формат, регулярные апдейты, чёткие escalation templates. Умение быстро структурировать информацию по Pyramid Principle позволяет донести суть проблемы до C-level за секунды, а не за минуты. Пост-кризисная коммуникация (postmortem, lessons learned) также требует навыков executive communication для трансляции уроков на уровень организации.

**[[startup-cto]]** — В стартапе CTO часто является единственным лидером, способным управлять техническим кризисом, и одновременно несёт ответственность за коммуникацию с инвесторами и клиентами. Стартап-контекст добавляет экзистенциальный риск: серьёзный инцидент может поставить под угрозу выживание компании. Опыт кризисного менеджмента — одна из ключевых компетенций, отличающих опытного CTO от начинающего.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |
| Lencioni P. (2002) *The Five Dysfunctions of a Team: A Leadership Fable* | Книга |


## Проверь себя

> [!question]- Incident Commander под давлением
> Production outage в 3 AM. P0 severity. 50K пользователей affected. Вы — Incident Commander. Первые 15 минут: alert fired, on-call engineer acknowledged, но не может определить root cause. Используя Incident Response Framework, опишите конкретные шаги по фазам: Detect & Assess, Assemble & Assign, Mitigate.

> [!question]- Blameless postmortem vs blame culture
> После серьёзного incident CTO публично обвинил инженера, который сделал deploy. Команда замкнулась: никто не хочет деплоить. Используя blameless postmortem principles, объясните почему blame разрушителен и как провести правильный postmortem с фокусом на systems, not people.

> [!question]- 70% rule для решений
> Во время incident у вас два варианта: rollback (safe но потеря 2 дней работы) или hotfix (risky но сохраняет progress). У вас 70% информации, что hotfix сработает. Используя framework 'Decision Making Under Pressure', как принять решение? Когда decide fast, когда pause?

## Ключевые карточки

Назови 4 фазы Incident Response Framework.
?
1. Detect & Assess (0-5 min): что сломалось, кто affected, blast radius. 2. Assemble & Assign (5-15 min): IC, Tech Lead, Comms Lead, Scribe. 3. Mitigate (15 min - hours): stop bleeding, rollback, workaround. 4. Resolve & Communicate: confirm fix, monitor, schedule postmortem.

Что делает Incident Commander?
?
Owns incident end-to-end, makes decisions (even imperfect), coordinates resources, manages communication. DO: stay calm, decide with 70% info, delegate. DON'T: debug yourself, go silent, blame.

Назови принципы blameless postmortem.
?
Assume good intent, focus on systems not people, 'what' not 'who', human error = system failure, learning > punishment. Schedule within 48-72 hours. Structure: timeline, facts, contributing factors, what went well, improvements, action items.

Что такое 70% Rule для decisions under pressure?
?
Make decision with 70% information. Waiting for 100% = too late. Reversible decisions: decide fast, adjust later. Irreversible: pause, get more input.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[executive-communication]] | Коммуникация во время кризиса |
| Углубиться | [[stakeholder-management]] | Управление stakeholders в кризис |
| Смежная тема | [[devops-incident-management]] | Incident management процессы |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
