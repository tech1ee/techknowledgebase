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

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |
| Lencioni P. (2002) *The Five Dysfunctions of a Team: A Leadership Fable* | Книга |


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
