---
title: "Управление техническим долгом"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, tech-lead, cto]
teaches:
  - что такое tech debt
  - приоритизация
  - коммуникация с бизнесом
sources: [martin-fowler, elegant-puzzle, tech-debt-research]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[architecture-decisions]]"
  - "[[engineering-practices]]"
---

# Управление техническим долгом

> **TL;DR:** Tech debt — не всегда плохо. Это trade-off: скорость сейчас vs скорость потом. Как финансовый долг — вопрос в управлении, не в избегании. 25-40% velocity теряется на обслуживание неуправляемого долга. Главное: visibility (измеряй), prioritization (не всё fix), communication (бизнес должен понимать).

---

## Что такое Tech Debt

```
ОПРЕДЕЛЕНИЕ (Ward Cunningham):
"Несовершенный код, который мы решили
выпустить, чтобы узнать что-то раньше."

МЕТАФОРА:
Финансовый долг:
• Principal = изначальный shortcut
• Interest = ongoing cost to work around
• Если не платить — compound interest

ТИПЫ ДОЛГА:

DELIBERATE vs INADVERTENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deliberate: "Знаем что hack, но deadline"
Inadvertent: "Не знали лучшего способа"

PRUDENT vs RECKLESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prudent: "Понимаем trade-off, идём на risk"
Reckless: "Какой дизайн? Давай быстрее"
```

```
QUADRANT (Martin Fowler):

             PRUDENT              RECKLESS
         ┌──────────────────┬──────────────────┐
DELIBER- │ "Мы должны ship  │ "У нас нет      │
ATE      │ сейчас, fix      │ времени на      │
         │ позже"           │ дизайн"         │
         ├──────────────────┼──────────────────┤
INADVER- │ "Теперь знаем    │ "Что такое      │
TENT     │ как надо было"   │ layering?"      │
         └──────────────────┴──────────────────┘

BEST: Prudent-Deliberate (осознанный компромисс)
WORST: Reckless-Inadvertent (некомпетентность)
```

## Как измерять

```
PROXY METRICS:

VELOCITY DRAG:
% времени на bugs, incidents, working around
Target: <20%

CYCLE TIME TRENDS:
Если растёт при стабильном scope — debt signal

DEFECT RATE:
Bugs per feature increasing

DEPLOY FREQUENCY:
Падает? Возможно debt

DEVELOPER SURVEY:
"How easy is it to change X?"
1-5 scale, track over time

HOTSPOT ANALYSIS:
Files часто меняемые + часто buggy = debt
```

## Приоритизация

```
НЕ ВЕСЬ DEBT НУЖНО ПЛАТИТЬ:

PRIORITIZATION MATRIX:
              HIGH IMPACT          LOW IMPACT
           ┌──────────────────┬──────────────────┐
HIGH       │    FIX NOW       │   MAYBE LATER    │
FREQUENCY  │                  │                  │
           │  Часто трогаем,  │  Редко нужно,    │
           │  сильно мешает   │  но болит        │
           ├──────────────────┼──────────────────┤
LOW        │   OPPORTUNISTIC  │    IGNORE        │
FREQUENCY  │                  │                  │
           │  Fix когда       │  "Не трогай      │
           │  рядом           │  если работает"  │
           └──────────────────┴──────────────────┘

RULE: Fix debt in areas you're actively developing
```

## Стратегии

```
1. TAX (постоянный %)
"20% каждого спринта на tech debt"
+ Predictable
- May not hit highest priority

2. DEDICATED SPRINTS
"Каждый 5й спринт — tech debt"
+ Deep focus
- Business resistance

3. BOY SCOUT RULE
"Leave code better than found"
+ Continuous improvement
- Slow for big issues

4. STRATEGIC INITIATIVES
Quarterly planning включает debt items
+ Aligned with business
- Requires good measurement

5. OPPORTUNITY-BASED
Fix when changing related code
+ Efficient
- Some areas never touched
```

## Коммуникация с бизнесом

```
НЕ ГОВОРИ: "Нам нужно fix tech debt"
ГОВОРИ:    "Без этого feature X займёт 3x времени"

FRAMEWORK:

1. QUANTIFY COST:
"Каждая фича в payment system берёт
+2 дня из-за legacy архитектуры.
За год это 40 engineer-days."

2. SHOW TREND:
"6 месяцев назад changes брали 2 дня.
Сейчас — 5 дней. Через год будет 10."

3. PROPOSE INVESTMENT:
"2 недели на refactoring сэкономят
80 engineer-days за следующий год."

4. MAKE VISIBLE:
Dashboard с debt metrics
Regular reporting
```

---

## Связанные темы

- [[architecture-decisions]] — документирование решений
- [[engineering-practices]] — практики качества
- [[technical-vision]] — долгосрочное планирование

## Источники

| Источник | Тип |
|----------|-----|
| [Martin Fowler: Tech Debt](https://martinfowler.com/bliki/TechnicalDebt.html) | Article |
| [An Elegant Puzzle](https://www.amazon.com/Elegant-Puzzle-Systems-Engineering-Management/dp/1732265186) | Book |

---

*Последнее обновление: 2026-01-18*
