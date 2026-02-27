---
title: "Масштабирование инженерной организации"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [director, vpe, cto]
teaches:
  - stages of growth
  - reorgs
  - coordination patterns
sources: [elegant-puzzle, team-topologies, conways-law]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[building-engineering-team]]"
  - "[[team-structures]]"
prerequisites:
  - "[[building-engineering-team]]"
  - "[[team-structures]]"
  - "[[em-fundamentals]]"
reading_time: 7
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Масштабирование инженерной организации

> **TL;DR:** Scaling ≠ hiring more. Это изменение структур, процессов, культуры. Conway's Law: архитектура отражает org structure. Key stages: 10 → 30 → 100 → 300 engineers. Каждый требует разных подходов. Span of control: 5-8 reports на менеджера.

---

## Теоретические основы

### Законы масштабирования организаций

> **Определение:** Organizational Scaling — процесс увеличения численности и сложности организации при сохранении (или улучшении) эффективности, скорости и качества.

Несколько фундаментальных законов определяют ограничения масштабирования:

| Закон | Автор, год | Формулировка | Следствие для engineering org |
|-------|-----------|-------------|------------------------------|
| **Brooks's Law** | Fred Brooks, 1975 | «Добавление людей к опаздывающему проекту задерживает его ещё больше» | Коммуникационные каналы растут как n(n-1)/2 |
| **Conway's Law** | Melvin Conway, 1968 | Архитектура = org structure | [[team-structures\|Inverse Conway Maneuver]] |
| **Dunbar's Number** | Robin Dunbar, 1992 | Когнитивный лимит ~150 стабильных отношений | Максимум для single-context org |
| **Two-Pizza Rule** | Jeff Bezos, ~2002 | Команда должна быть накормлена двумя пиццами | 5-8 человек = optimal team size |

Fred Brooks в *"The Mythical Man-Month"* (1975) показал, что communication overhead растёт квадратично: при 10 инженерах — 45 каналов, при 50 — 1225. Это объясняет, почему каждый transition (10→30→100→300) требует fundamentally разных подходов к координации.

> «Adding manpower to a late software project makes it later.» — Fred Brooks, *"The Mythical Man-Month"* (1975)

Robin Dunbar в *"How Many Friends Does One Person Need?"* (2010) формализовал социальные круги: ~5 (близкие), ~15 (доверенные), ~50 (знакомые по имени), ~150 (активные связи). Это объясняет, почему при >150 инженерах организация неизбежно фрагментируется и требует формальных coordination mechanisms.

Will Larson в *"An Elegant Puzzle"* (2019) описал модель «four states of a team» (falling behind, treading water, repaying debt, innovating) и определил, что задача [[cto-vs-vpe|VP Engineering]] — довести каждую команду до состояния innovation.

---

## Stages of Growth

```
STAGE 1: 1-10 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: One team, flat
Communication: Direct, informal
Process: Minimal
Leadership: Founder/Tech Lead

Challenges:
• Establishing culture
• First processes
• Defining roles

STAGE 2: 10-30 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: 2-4 teams
Communication: Still mostly direct
Process: Light (standups, reviews)
Leadership: First managers

Challenges:
• First reorg
• Manager/IC split
• Cross-team coordination

STAGE 3: 30-100 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Teams of teams
Communication: Formalized
Process: Necessary
Leadership: Manager layer, directors

Challenges:
• Communication overhead
• Culture dilution
• Middle management
• Platform/product split

STAGE 4: 100-300 ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Departments
Communication: Structured
Process: Heavy
Leadership: VPs, multiple directors

Challenges:
• Coordination at scale
• Career paths
• Bureaucracy risk
• Maintaining velocity

STAGE 5: 300+ ENGINEERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: Multiple orgs
Communication: Async-heavy
Process: Platform-based
Leadership: Executive team

Challenges:
• Division autonomy
• Consistency vs flexibility
• Innovation pace
• Political complexity
```

## Conway's Law

```
"Organizations design systems that mirror
their communication structure."

IMPLICATION:
Want microservices? → Organize as small teams
Want platform? → Create platform team
Want speed? → Minimize dependencies

INVERSE CONWAY:
Design org to get architecture you want.
```

## Span of Control

```
OPTIMAL: 5-8 direct reports

<5 reports:
• Manager may micromanage
• Overhead high for value
• Career bottleneck

>8 reports:
• Not enough time per person
• 1-on-1s suffer
• Growth neglected

CALCULATION:
1-on-1s: 30 min × 8 = 4 hours/week
Team meetings: 2 hours/week
Admin/hiring: 5 hours/week
Stakeholders: 5 hours/week
Leaves: 20-24 hours for actual work
```

## When to Reorg

```
SIGNALS YOU NEED REORG:
• Team boundaries don't match architecture
• Too much cross-team coordination
• Teams too big (>10) or too small (<4)
• Unclear ownership
• Repeated conflicts
• Talent bottleneck

REORG PRINCIPLES:
1. Minimize disruption
2. Clear ownership post-reorg
3. Communicate extensively
4. Don't reorg too often (<18 months between)
5. Solve real problems, not perceived
```

## Coordination Mechanisms

```
AS YOU SCALE:

DIRECT (small):
Just talk to each other.

LIAISONS (medium):
Designated cross-team contacts.

CEREMONIES (medium-large):
Sync meetings, demos, planning.

DOCUMENTATION (large):
RFCs, ADRs, runbooks.

PLATFORM (very large):
Self-service, internal products.
```

---

## Связь с другими темами

**[[building-engineering-team]]** — Масштабирование организации начинается с умения строить отдельные команды. Принципы формирования команды — найм, онбординг, создание культуры — остаются фундаментом на каждом этапе роста. Понимание динамики малых групп критично для того, чтобы при масштабировании не потерять качество отдельных команд ради количества.

**[[team-structures]]** — Выбор структуры команд (stream-aligned, platform, enabling) является ключевым решением при масштабировании инженерной организации. Conway's Law показывает, что архитектура системы отражает структуру организации, поэтому правильный выбор team topology напрямую определяет архитектурные возможности. На каждом этапе роста (10, 30, 100, 300+ инженеров) оптимальная структура команд меняется.

## Источники

### Теоретические основы
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Brooks F. "The Mythical Man-Month" — Addison-Wesley, 1975 | Книга | Brooks's Law, communication overhead |
| 2 | Conway M. "How Do Committees Invent?" — Datamation, 1968 | Статья | Conway's Law |
| 3 | Dunbar R. "How Many Friends Does One Person Need?" — Faber & Faber, 2010 | Книга | Dunbar's Number (~150), social circles |
| 4 | Larson W. "An Elegant Puzzle" — Stripe Press, 2019 | Книга | Four states of a team, scaling models |

### Практические руководства
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Fournier C. "The Manager's Path" — O'Reilly, 2017 | Книга | Growth stages, org transitions |
| 2 | Horowitz B. "The Hard Thing About Hard Things" — Harper Business, 2014 | Книга | Scaling in crisis |


## Проверь себя

> [!question]- Conway's Law на практике
> Ваша компания хочет перейти на микросервисную архитектуру, но организационная структура — одна большая команда из 25 человек. Используя Conway's Law и Inverse Conway Maneuver, объясните почему архитектурный переход без org change обречён. Как должна выглядеть org structure?

> [!question]- Span of control расчёт
> Director of Engineering имеет 12 direct reports (все EM). Он жалуется на отсутствие времени для strategy и 1-on-1s. Используя расчёт из файла, покажите arithmetic почему 12 reports не работает и предложите restructuring.

## Ключевые карточки

Что гласит Conway's Law?
?
'Organizations design systems that mirror their communication structure.' Inverse Conway: проектируй org structure, чтобы получить желаемую архитектуру. Want microservices? Organize as small autonomous teams.

Какой optimal span of control для менеджера?
?
5-8 direct reports. <5: может micromanage, overhead high. >8: недостаточно времени на каждого, 1-on-1s suffer. Расчёт: 1-on-1s (4h) + team meetings (2h) + admin/hiring (5h) + stakeholders (5h) = 16h из 40.

Назови 5 стадий роста инженерной организации.
?
1-10: flat, one team. 10-30: 2-4 teams, first managers. 30-100: teams of teams, directors. 100-300: departments, VPs. 300+: multiple orgs, executive team.

Когда нужна реорганизация?
?
Signals: team boundaries don't match architecture, too much cross-team coordination, teams too big (>10) or too small (<4), unclear ownership. Но не реорганизуй чаще чем раз в 18 месяцев.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[team-structures]] | Модели организации команд |
| Углубиться | [[engineering-metrics]] | Метрики эффективности масштабирования |
| Смежная тема | [[microservices-vs-monolith]] | Архитектура при масштабировании |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
