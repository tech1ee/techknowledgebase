---
title: "Управление техническим долгом"
created: 2026-01-18
modified: 2026-02-13
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
prerequisites:
  - "[[em-fundamentals]]"
  - "[[engineering-practices]]"
reading_time: 10
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Связь с другими темами

**[[architecture-decisions]]** — ADR и tech debt management тесно связаны: многие ADR фиксируют осознанные trade-offs, которые создают deliberate tech debt. Когда ADR документирует "мы выбрали X потому что deadline", это создаёт traceable debt с понятным context. Без ADR tech debt накапливается inadvertently, и через год никто не помнит, почему решение было принято и нужно ли его менять.

**[[engineering-practices]]** — Engineering practices (code review, testing, CI/CD) — первая линия обороны против inadvertent tech debt. Хорошие practices предотвращают accumulation reckless debt, но deliberately accumulated debt нуждается в systematic management. DORA metrics из engineering-practices помогают измерять impact tech debt: если cycle time растёт при стабильном scope — это debt signal.

**[[technical-vision]]** — Tech vision определяет target state, а gap между current state и target state — это часть tech debt. Tech debt management — operational mechanism для closing этого gap. Без vision tech debt management становится reactive (fix что болит), а с vision — strategic (fix что мешает двигаться к цели). 20% sprint tax на tech debt должен быть aligned с vision priorities.

## Источники и дальнейшее чтение

- **Kim et al., "The Phoenix Project" (2016)** — Ярко иллюстрирует, как накопленный tech debt (в книге — "unplanned work") может paralyzed целую организацию. Three Ways предлагают системный подход к управлению: flow (быстрая доставка), feedback (быстрое обнаружение проблем) и continuous learning (предотвращение повторения).
- **Will Larson, "An Elegant Puzzle" (2019)** — Содержит practical framework для prioritization tech debt: migrations approach, system health scoring и strategic investment planning. Larson показывает, как коммуницировать tech debt business stakeholders и получать buy-in на remediation.
- **Camille Fournier, "The Manager's Path" (2017)** — Описывает, как tech leaders на разных уровнях управляют tech debt: Tech Lead идентифицирует и prioritizes, EM балансирует с feature work, Director/VP устанавливает organizational policy.


## Проверь себя

> [!question]- Quantify cost для бизнеса
> VP Product спрашивает: 'Зачем тратить 2 недели на refactoring, если можно делать features?' Используя communication framework из файла, сформулируйте ответ с конкретными цифрами, показывающими ROI инвестиций в tech debt reduction.

> [!question]- Prudent vs Reckless debt
> Используя Tech Debt Quadrant Martin Fowler, классифицируйте следующие ситуации: (a) 'Мы знаем, что этот hack нужно починить после launch', (b) 'Что такое layering?', (c) 'Теперь знаем, как надо было сделать'. Какой тип debt наиболее опасен и почему?

> [!question]- Prioritization matrix
> У вас 20 tech debt items. Ресурс — 20% спринта. Как использовать prioritization matrix (impact x frequency) для выбора, что fix first? Почему не весь debt нужно платить?

## Ключевые карточки

Какая метафора tech debt и что такое 'interest'?
?
Как финансовый долг: Principal = изначальный shortcut. Interest = ongoing cost to work around. Если не платить — compound interest. 25-40% velocity теряется на неуправляемый долг.

Опиши Tech Debt Quadrant по Martin Fowler.
?
2 оси: Deliberate/Inadvertent x Prudent/Reckless. Best: Prudent-Deliberate ('знаем trade-off, идём осознанно'). Worst: Reckless-Inadvertent ('что такое layering?' — некомпетентность).

Назови 5 стратегий управления tech debt.
?
1. Tax (20% спринта). 2. Dedicated sprints (каждый 5-й). 3. Boy Scout Rule (leave code better). 4. Strategic initiatives (quarterly planning). 5. Opportunity-based (fix при изменении related code).

Как коммуницировать tech debt бизнесу?
?
Не говори: 'Нужно fix tech debt'. Говори: 'Без этого feature X займёт 3x времени'. Quantify cost, show trend, propose investment с ROI, make visible через dashboard.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[architecture-decisions]] | ADR для осознанного debt |
| Углубиться | [[technical-vision]] | Vision как guide для debt priorities |
| Смежная тема | [[technical-debt]] | Technical debt из perspective архитектуры |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
