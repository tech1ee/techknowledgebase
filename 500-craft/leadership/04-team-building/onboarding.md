---
title: "Онбординг инженеров"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: beginner
target-role: [em, tech-lead, hr]
teaches:
  - 30-60-90 day plan
  - onboarding checklist
  - buddy system
sources: [first-round-review, managers-path, gitlab-onboarding]
tags:
  - topic/leadership
  - type/deep-dive
  - level/beginner
related:
  - "[[building-engineering-team]]"
  - "[[team-culture]]"
reading_time: 6
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Онбординг инженеров

> **TL;DR:** Первые 90 дней определяют успех найма. Structured onboarding: +62% productivity, -50% time to first contribution. Цель: время до первого meaningful contribution. Buddy + manager + documentation. Not "sink or swim" — это дорого и cruel.

---

## 30-60-90 Day Framework

```
DAY 1-30: LEARN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Understand context
• Meet team, stakeholders
• Read documentation
• Set up environment
• Small tasks, PRs
• Learn culture/norms

Success: Can explain what team does

DAY 31-60: CONTRIBUTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Add value
• Own small features
• Participate in planning
• Give/receive code review
• Understand dependencies
• Start on-call shadowing

Success: Shipped meaningful work

DAY 61-90: IMPACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Independent contributor
• Own larger projects
• Influence decisions
• Help others
• Full on-call rotation
• Identify improvements

Success: Autonomous, adding value
```

## First Day Checklist

```
BEFORE DAY 1:
□ Laptop ready
□ Accounts created (email, Slack, GitHub)
□ Calendar invites sent
□ Buddy assigned
□ Manager 1-on-1 scheduled
□ Welcome email sent

DAY 1 MORNING:
□ Welcome by manager
□ Introduction to team
□ Workspace setup
□ IT/Security training

DAY 1 AFTERNOON:
□ Buddy lunch
□ Team overview
□ First small task
□ End-of-day check-in

END OF WEEK 1:
□ 1-on-1 with manager
□ Met all team members
□ First PR (even small)
□ Understood roadmap
□ Questions documented
```

## Buddy System

```
BUDDY ROLE:
• Not manager, not mentor — peer support
• Daily check-ins first 2 weeks
• Answer "dumb" questions
• Navigate culture/politics
• Social introduction

BUDDY SELECTION:
□ Same team, different role
□ Tenured (6+ months)
□ Patient and helpful
□ Volunteered (not forced)

BUDDY RESPONSIBILITIES:
Week 1: Daily 15-min check-ins
Week 2-4: Every other day
Month 2: Weekly as needed
Month 3: On-demand
```

## Onboarding Doc Template

```markdown
# Welcome to [Team Name]!

## Quick Links
- [Team Slack channel]
- [Documentation]
- [Codebase]
- [On-call runbook]

## Your First Week
Day 1: [Tasks]
Day 2: [Tasks]
...

## Key People
| Name | Role | Contact for |
|------|------|-------------|
| [Manager] | Manager | 1-on-1s, priorities |
| [Buddy] | Buddy | Daily questions |
| [Tech Lead] | Tech Lead | Architecture |

## Team Norms
- [How we communicate]
- [How we code review]
- [Meeting schedule]

## First Tasks
1. [ ] Set up environment
2. [ ] First PR (starter issue)
3. [ ] Read [key doc]

## 30-Day Goals
- [ ] [Goal 1]
- [ ] [Goal 2]

## Questions to Ask
- [Good questions for new person]
```

## Common Mistakes

```
❌ SINK OR SWIM:
"Figure it out yourself"
→ Slow ramp, frustration, turnover

❌ NO BUDDY:
"Everyone's too busy"
→ New hire feels isolated

❌ NO EARLY WINS:
First task takes months
→ Demoralization

❌ INFORMATION OVERLOAD:
60-page doc on day 1
→ Overwhelm, nothing retained

✓ INSTEAD:
Structured plan + buddy + small early wins
```

---

## Источники

| Источник | Тип |
|----------|-----|
| [GitLab Onboarding](https://about.gitlab.com/handbook/people-group/general-onboarding/) | Example |
| [First Round: Onboarding](https://review.firstround.com/) | Articles |
| [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) | Book |

## Связь с другими темами

### [[building-engineering-team]]

Онбординг — заключительный этап процесса найма и первый этап интеграции нового члена команды. Даже идеальный hiring pipeline обесценивается, если новый инженер уходит через 3 месяца из-за плохого onboarding. Structured onboarding (+62% productivity) напрямую влияет на retention rate и time-to-productivity, которые являются ключевыми метриками успешного team building.

### [[team-culture]]

Первые 30 дней — окно, в котором новый инженер впитывает культуру команды. Buddy system, 1:1 с менеджером, первый code review — всё это формирует восприятие культуры. Если заявленные ценности (collaboration, psychological safety) расходятся с реальным опытом onboarding ("sink or swim"), новый сотрудник усвоит реальную культуру, а не декларируемую. Onboarding — лакмусовая бумажка для team culture.


## Проверь себя

> [!question]- Sink or swim vs structured onboarding
> Стартап нанимает пятого инженера, но у команды нет процесса onboarding. Первый инженер говорит: 'Я сам разобрался, и новый разберётся'. Используя статистику (+62% productivity, -50% time to first contribution), обоснуйте необходимость structured onboarding и предложите минимальный plan для стартапа.

> [!question]- Buddy system эффективность
> Новый инженер на второй неделе боится задавать 'глупые' вопросы менеджеру. Как buddy system решает эту проблему? Какие критерии выбора buddy и какой cadence check-ins?

> [!question]- 30-60-90 адаптация
> На Day 45 новый senior инженер ещё не сделал ни одного meaningful commit. Менеджер обеспокоен. Используя 30-60-90 framework, определите: это нормально или red flag? Какие success criteria для каждого этапа?

## Ключевые карточки

Какие три фазы 30-60-90 day framework для onboarding?
?
Day 1-30: LEARN (understand context, meet team, small PRs). Day 31-60: CONTRIBUTE (own small features, code review, on-call shadowing). Day 61-90: IMPACT (own larger projects, influence decisions, full on-call).

Какой impact structured onboarding на productivity?
?
+62% productivity, -50% time to first contribution. Structured onboarding напрямую влияет на retention rate и time-to-productivity.

Кто такой Buddy и чем он отличается от mentor/manager?
?
Buddy — peer support, не manager и не mentor. Daily check-ins первые 2 недели, отвечает на 'глупые' вопросы, помогает навигировать культуру. Выбирается из tenured (6+ мес), patient, volunteered.

Что должно быть готово ДО Day 1 нового инженера?
?
Laptop ready, accounts created (email, Slack, GitHub), calendar invites sent, buddy assigned, manager 1-on-1 scheduled, welcome email sent.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[building-engineering-team]] | Онбординг как завершение найма |
| Углубиться | [[team-culture]] | Онбординг как передача культуры |
| Смежная тема | [[first-90-days]] | Первые 90 дней для лидера |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
