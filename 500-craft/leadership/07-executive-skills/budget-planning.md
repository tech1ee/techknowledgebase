---
title: "Планирование бюджета"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [director, vpe, cto]
teaches:
  - headcount planning
  - opex vs capex
  - budget justification
sources: [cfo-partnership, engineering-budgets]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[strategic-thinking]]"
  - "[[executive-communication]]"
prerequisites:
  - "[[strategic-thinking]]"
  - "[[executive-communication]]"
  - "[[engineering-metrics]]"
reading_time: 6
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Планирование бюджета

> **TL;DR:** Budget = план в деньгах. Headcount обычно 70-80% engineering budget. Know the difference: CapEx (capital, depreciates) vs OpEx (operating, immediate expense). Justify investment with ROI. Work with Finance — they're partners, not gatekeepers.

---

## Budget Components

```
ENGINEERING BUDGET:

HEADCOUNT (70-80%):
• Salaries
• Benefits
• Bonuses
• Contractors

TOOLS & INFRASTRUCTURE (15-20%):
• Cloud (AWS, GCP, Azure)
• SaaS tools (GitHub, Jira, etc.)
• Licenses
• Hardware

OTHER (5-10%):
• Training/conferences
• Recruiting fees
• Travel
• Office/remote stipends
```

## Headcount Planning

```
BOTTOM-UP APPROACH:
1. What projects/initiatives planned?
2. How many people needed for each?
3. What roles (IC, manager, specialist)?
4. What seniority mix?
5. When needed?

TOP-DOWN APPROACH:
1. Revenue target
2. Engineering as % of revenue
3. Available budget
4. How to allocate

TYPICAL RATIOS:
• Revenue per engineer: $200K-$500K+
• Engineer:PM ratio: 5-10:1
• Engineer:Designer: 5-15:1
• Manager:IC: 1:5-8

BACKFILL vs NET NEW:
• Backfill: replace departures
• Net new: growth
• Plan for ~10-15% attrition
```

## CapEx vs OpEx

```
CapEx (Capital Expenditure):
• Long-term assets (>1 year)
• Depreciated over time
• Example: servers, major software build
• Tax treatment: spread over years

OpEx (Operating Expenditure):
• Day-to-day costs
• Immediate expense
• Example: SaaS subscriptions, cloud
• Tax treatment: deduct this year

WHY IT MATTERS:
Finance cares about the split.
Some companies prefer CapEx (asset on books).
Others prefer OpEx (flexibility).
Ask Finance for preference.
```

## Budget Justification

```
FOR HEADCOUNT:
"2 engineers for project X will deliver
feature Y by Q3, expected to generate
$500K ARR. ROI: 5x salary cost."

FOR TOOLS:
"Tool X costs $50K/year. Saves 2 hours/week
per developer. 50 developers × 2 hours ×
$100/hour × 50 weeks = $500K saved."

FOR INFRASTRUCTURE:
"Current spend: $X. With optimization: $Y.
Investment in platform team: $Z.
Net savings: $X - $Y - $Z over 2 years."

ALWAYS INCLUDE:
• Business impact (revenue, cost savings)
• Alternatives considered
• Risk of not investing
• Timeline to value
```

## Annual Planning Process

```
TYPICAL TIMELINE:

Q3 (AUGUST-SEPTEMBER):
• Finance sends templates
• Top-down targets shared
• Departments draft requests

Q4 (OCTOBER-NOVEMBER):
• Reviews and negotiations
• Trade-offs discussed
• Final allocation

Q1:
• Budget finalized
• Hiring plans activated
• Quarterly check-ins

TIPS:
• Start early
• Build relationships with Finance
• Have backup plans (what if -20%?)
• Document assumptions
```

## Working with Finance

```
DO:
✓ Learn finance language (ROI, EBITDA, etc.)
✓ Provide data they need
✓ Be transparent about risks
✓ Propose alternatives
✓ Meet deadlines

DON'T:
✗ Surprise them
✗ Pad requests expecting cuts
✗ Ignore their constraints
✗ Be adversarial
```

---

## Связь с другими темами

**[[strategic-thinking]]** — Бюджет является финансовым выражением стратегии: куда направить ресурсы, а где сэкономить. Без стратегического мышления планирование бюджета превращается в механическое распределение денег, а не в инструмент достижения целей. Умение обосновать инвестиции через ROI и связать каждую статью расходов со стратегическими приоритетами — ключевой навык VP+ уровня.

**[[executive-communication]]** — Представление бюджета руководству требует навыков executive communication: BLUF (Bottom Line Up Front), Pyramid Principle, бизнес-язык вместо технического жаргона. Успешное согласование бюджета зависит не только от качества расчётов, но и от умения убедительно представить данные, ответить на вопросы и показать альтернативы. Каждый запрос на ресурсы должен проходить тест «So what?» с точки зрения бизнес-влияния.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Drucker P. (2006) *The Effective Executive: The Definitive Guide to Getting the Right Things Done* | Книга |
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |


## Проверь себя

> [!question]- ROI обоснование для headcount
> Вам нужно обосновать найм 3 инженеров на проект, который потенциально принесёт $2M ARR. Используя framework budget justification из файла, составьте business case с ROI, timeline to value и альтернативами.

> [!question]- CapEx vs OpEx для CFO
> Finance Director спрашивает: 'Почему вы перешли с on-premise серверов (CapEx) на облако (OpEx)? Это ухудшает нашу balance sheet.' Объясните разницу CapEx и OpEx и почему для engineering OpEx часто предпочтительнее.

## Ключевые карточки

Каков типичный breakdown engineering budget?
?
Headcount: 70-80% (salaries, benefits, bonuses, contractors). Tools & Infrastructure: 15-20% (cloud, SaaS, licenses). Other: 5-10% (training, recruiting fees, travel).

Чем CapEx отличается от OpEx?
?
CapEx: long-term assets (>1 year), depreciated over time, tax spread over years. OpEx: day-to-day costs, immediate expense, deduct this year. Finance cares about the split.

Какие типичные ratios в engineering?
?
Revenue per engineer: $200K-$500K+. Engineer:PM = 5-10:1. Engineer:Designer = 5-15:1. Manager:IC = 1:5-8. Plan for ~10-15% attrition.

Как обосновать инвестицию в инструменты?
?
'Tool X costs $50K/year. Saves 2h/week per developer. 50 devs x 2h x $100/h x 50 weeks = $500K saved.' Always include: business impact, alternatives, risk of not investing, timeline to value.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[executive-communication]] | Как представить бюджет руководству |
| Углубиться | [[strategic-thinking]] | Бюджет в контексте стратегии |
| Смежная тема | [[cloud-platforms-essentials]] | Cloud cost management |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
