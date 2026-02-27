---
title: "OKRs и KPIs для инженерии"
created: 2026-01-18
modified: 2026-02-13
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
prerequisites:
  - "[[engineering-metrics]]"
  - "[[em-fundamentals]]"
reading_time: 7
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# OKRs и KPIs для инженерии

> **TL;DR:** OKRs (Objectives + Key Results) — framework для ambitious goals. KPIs — ongoing health metrics. OKRs: quarterly, stretch (70% = good). KPIs: continuous, 100% target. Не превращай OKRs в to-do list. Engineering OKRs: balance бизнес-outcome и tech health.

---

## Теоретические основы

### OKR: от MBO Drucker к Google

> **Определение:** OKR (Objectives and Key Results) — система целеполагания, при которой Objective (амбициозная качественная цель) измеряется через 2-5 Key Results (количественных показателей). Развитие Management by Objectives (MBO) Drucker через Andy Grove (Intel) к John Doerr (Google).

Хронология эволюции OKR:

| Год | Событие | Автор | Ключевая идея |
|-----|---------|-------|---------------|
| 1954 | **MBO** (Management by Objectives) | Peter Drucker | Цели согласуются сверху вниз |
| ~1975 | **OKR** в Intel | Andy Grove | MBO + measurable results, stretch goals |
| 1999 | OKR в Google | John Doerr (инвестор) | Привнёс OKR из Intel в Google |
| 2018 | *"Measure What Matters"* | John Doerr | Популяризация OKR globally |

### Balanced Scorecard (Kaplan & Norton, 1992)

Robert Kaplan и David Norton в *"The Balanced Scorecard"* (Harvard Business Review, 1992) предложили рассматривать организацию через четыре перспективы:

> **Balanced Scorecard** — framework стратегического управления, балансирующий **Financial** (revenue, costs), **Customer** (satisfaction, retention), **Internal Process** (efficiency, quality), **Learning & Growth** (innovation, skills).

Для engineering организации Balanced Scorecard трансформируется: Financial = cost of engineering, Customer = internal customers + end users, Internal Process = [[engineering-metrics|DORA metrics]], Learning & Growth = developer satisfaction, tech debt ratio.

Различие OKR и KPI теоретически формализовано: OKR задают **direction** (stretch goals, 70% = success), KPI отслеживают **health** (operational metrics, 100% = target). Andy Grove подчеркивал: «OKRs are not a to-do list. They are a way to think about what really matters.»

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

## Связь с другими темами

**[[engineering-metrics]]** — OKR и KPI тесно связаны с инженерными метриками, так как именно метрики (DORA, SPACE) формируют измеримые Key Results. Без понимания того, что и как измерять, невозможно построить качественные OKR. Метрики предоставляют объективные данные для оценки прогресса по OKR и определения health KPI для инженерной организации.

**[[strategic-thinking]]** — OKR являются инструментом трансляции стратегии в конкретные измеримые цели для команд. Стратегическое мышление определяет направление (куда идём), а OKR превращают это направление в квартальные цели с конкретными результатами. Без стратегического контекста OKR превращаются в бессмысленный список задач, оторванный от бизнес-целей компании.

## Источники

### Теоретические основы
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Drucker P. "The Practice of Management" — Harper, 1954 | Книга | Management by Objectives (MBO) |
| 2 | Grove A. "High Output Management" — Random House, 1983 | Книга | OKR в Intel, output менеджера |
| 3 | Kaplan R., Norton D. "The Balanced Scorecard" — HBR, 1992 | Статья | Четыре перспективы стратегического управления |
| 4 | Doerr J. "Measure What Matters" — Portfolio/Penguin, 2018 | Книга | OKR methodology, Google examples |

### Практические руководства
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Google re:Work OKRs](https://rework.withgoogle.com/guides/set-goals-with-okrs/) | Guide | Google OKR practices |
| 2 | **Radical Focus** (Christina Wodtke, 2016) | Книга | OKR implementation guide |


## Проверь себя

> [!question]- OKR vs To-Do list
> Команда написала OKR: 'O: Улучшить платформу. KR1: Мигрировать на Kubernetes. KR2: Обновить React до v19. KR3: Написать 50 unit тестов.' Почему это to-do list, а не OKR? Перепишите, используя правильный формат с outcome-based Key Results.

> [!question]- Scoring 1.0 = bar too low
> Команда получила score 1.0 на все OKR два квартала подряд. Руководство хвалит. Используя Google method scoring, объясните почему это проблема и как правильно калибровать ambitious goals.

## Ключевые карточки

Чем OKR отличаются от KPI?
?
OKR: quarterly goals, ambitious/stretch, 70% = success, drive change, few (3-5). KPI: ongoing health metrics, target = expected, 100% = success, monitor status, many possible.

Как scoring OKR по Google method?
?
0.0-0.3 = Red (need attention). 0.4-0.6 = Yellow (progress). 0.7-1.0 = Green (strong). Score 1.0 = bar set too low. Ideal target = 0.7.

Назови 5 common mistakes в OKR.
?
Too many OKRs (>5), not ambitious enough (all 1.0s), Key Results are tasks not outcomes, set and forget, tied to bonuses (discourages stretch).

Приведи пример quality-focused engineering OKR.
?
O: Dramatically improve engineering quality. KR1: Test coverage 60% -> 80%. KR2: Change failure rate 20% -> 10%. KR3: Code review turnaround < 4 hours.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[engineering-metrics]] | Метрики как основа Key Results |
| Углубиться | [[strategic-thinking]] | OKR как трансляция стратегии |
| Смежная тема | [[performance-management]] | OKR в performance reviews |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
