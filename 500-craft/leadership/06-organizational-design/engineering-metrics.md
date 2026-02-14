---
title: "Метрики инженерии"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, vpe]
teaches:
  - DORA metrics
  - productivity metrics
  - что НЕ мерить
sources: [accelerate, dora, space-framework]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[okrs-kpis]]"
prerequisites:
  - "[[em-fundamentals]]"
reading_time: 6
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Метрики инженерии

> **TL;DR:** Что меряешь — тем управляешь. Но: Lines of Code = bad metric. Story points = bad metric. DORA metrics (deploy frequency, lead time, MTTR, change failure) — научно validated. Developer satisfaction тоже metric. Не меряй всё — выбери 3-5 key metrics.

---

## DORA Metrics

```
4 KEY METRICS (Accelerate book):

1. DEPLOYMENT FREQUENCY
   Elite: On-demand (multiple/day)
   High: Weekly-Monthly
   Medium: Monthly-Yearly
   Low: <Once/Year

2. LEAD TIME FOR CHANGES
   Elite: <1 hour
   High: 1 day - 1 week
   Medium: 1 week - 1 month
   Low: 1-6 months

3. TIME TO RESTORE (MTTR)
   Elite: <1 hour
   High: <1 day
   Medium: 1 day - 1 week
   Low: 1 week - 1 month

4. CHANGE FAILURE RATE
   Elite: 0-15%
   High: 16-30%
   Medium: 31-45%
   Low: 46-60%

KEY INSIGHT:
High performers are high on ALL 4.
Speed and stability go together.
```

## SPACE Framework

```
S - Satisfaction & Well-being
    Developer happiness surveys
    Burnout indicators

P - Performance
    Code quality metrics
    Business impact

A - Activity
    Commits, PRs, reviews
    (careful — easy to game)

C - Communication & Collaboration
    PR review time
    Documentation quality

E - Efficiency & Flow
    Wait times
    Context switching
    Focus time
```

## Metrics to AVOID

```
❌ LINES OF CODE
   More ≠ better. Often worse.

❌ HOURS WORKED
   Presence ≠ output.

❌ STORY POINTS VELOCITY
   Easily gamed. Meaningless comparing teams.

❌ NUMBER OF COMMITS
   Incentivizes small useless commits.

❌ CODE COVERAGE %
   100% coverage ≠ good tests.
   Tests can be meaningless.

❌ BUGS FOUND
   Punishes those who find bugs.
```

## Good Metrics by Category

```
DELIVERY:
• Deploy frequency
• Lead time (commit → prod)
• Cycle time (start → done)
• Throughput (features/sprint)

QUALITY:
• Change failure rate
• Escaped bugs (prod incidents)
• MTTR (time to restore)
• Customer-reported issues

HEALTH:
• Developer satisfaction (survey)
• Attrition rate
• 1-on-1 attendance
• Learning time investment

EFFICIENCY:
• PR review time
• Build time
• Test suite time
• Time to first contribution (onboarding)
```

## Using Metrics

```
DO:
✓ Track trends over time
✓ Use for team discussion
✓ Combine multiple metrics
✓ Context matters
✓ Let team own their metrics

DON'T:
✗ Compare teams on velocity
✗ Tie metrics to bonuses directly
✗ Measure everything
✗ Ignore qualitative signals
✗ Punish bad metrics without understanding
```

---

## Связь с другими темами

**[[em-fundamentals]]** — Метрики инженерии являются одним из ключевых инструментов в арсенале engineering manager. Понимание DORA metrics и SPACE framework помогает менеджеру объективно оценивать здоровье команды и принимать data-driven решения. Без фундаментального понимания роли EM невозможно правильно интерпретировать и использовать метрики — они должны служить инструментом развития команды, а не инструментом контроля.

**[[okrs-kpis]]** — Метрики инженерии напрямую связаны с OKR и KPI фреймворками, поскольку именно метрики формируют Key Results в инженерных OKR. DORA metrics часто становятся основой для KPI команд разработки, а SPACE framework помогает выбрать сбалансированный набор показателей. Правильная связка метрик с OKR позволяет команде видеть свой прогресс и влияние на бизнес-результаты.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |
| Drucker P. (2006) *The Effective Executive: The Definitive Guide to Getting the Right Things Done* | Книга |
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |


## Проверь себя

> [!question]- Goodhart's Law в действии
> Менеджер привязал бонусы к code coverage. Через месяц coverage выросла с 60% до 95%, но количество bugs не уменьшилось — инженеры пишут бессмысленные тесты. Используя принцип 'metrics to avoid' и SPACE framework, предложите лучший набор метрик.

> [!question]- DORA для диагностики
> Deployment frequency упала с daily до weekly за 3 месяца. Lead time вырос с 1 дня до 5 дней. Change failure rate стабилен. Что это может сигнализировать? Используя DORA metrics correlation, предложите root cause analysis plan.

## Ключевые карточки

Какие метрики НЕЛЬЗЯ использовать для оценки инженеров?
?
Lines of Code (more != better), Hours Worked (presence != output), Story Points Velocity (easily gamed), Number of Commits (incentivizes useless commits), Code Coverage % (100% != good tests), Bugs Found (punishes finders).

Что такое SPACE framework?
?
S — Satisfaction & Well-being. P — Performance. A — Activity (careful — easy to game). C — Communication & Collaboration. E — Efficiency & Flow. Balanced подход к измерению developer productivity.

Назови правила использования метрик.
?
DO: track trends, use for team discussion, combine multiple metrics, context matters. DON'T: compare teams on velocity, tie to bonuses directly, measure everything, ignore qualitative signals.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[okrs-kpis]] | От метрик к целям |
| Углубиться | [[engineering-practices]] | DORA metrics в контексте practices |
| Смежная тема | [[observability]] | Observability как источник метрик |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
