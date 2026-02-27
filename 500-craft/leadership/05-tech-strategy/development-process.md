---
title: "Процессы разработки"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, tech-lead]
teaches:
  - git workflows
  - sprint planning
  - release management
sources: [trunk-based-dev, git-flow, continuous-delivery]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[engineering-practices]]"
  - "[[agile-practices]]"
prerequisites:
  - "[[engineering-practices]]"
reading_time: 8
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Процессы разработки

> **TL;DR:** Process должен помогать, не мешать. Trunk-based development > Git Flow для большинства. Short-lived branches (<1 day), feature flags для incomplete work. Sprint planning: realistic commitments. Release: часто, маленькими частями, автоматизированно.

---

## Теоретические основы

### Эволюция моделей разработки ПО

> **Определение:** Software Development Life Cycle (SDLC) — формализованный процесс планирования, создания, тестирования и развёртывания программного обеспечения. Эволюционировал от линейных моделей к итеративным и непрерывным.

| Эпоха | Модель | Ключевая идея | Ограничения |
|-------|--------|---------------|-------------|
| 1970 | **Waterfall** (Royce) | Последовательные фазы: requirements → design → code → test → deploy | Невозможность изменений, поздний feedback |
| 1986 | **Spiral** (Boehm) | Итерации с анализом рисков | Сложность, overhead |
| 2001 | **Agile** (Manifesto) | Working software, responding to change | Размытые практики без Scrum/XP |
| 2009 | **DevOps** (Allspaw & Hammond) | Dev + Ops как единый процесс, continuous delivery | Организационное сопротивление |
| 2019 | **DevSecOps** | Security shift-left, integrated в CI/CD | Tooling complexity |

### Cynefin Framework (Snowden, 2007)

Dave Snowden в *"A Leader's Framework for Decision Making"* (Harvard Business Review, 2007) предложил Cynefin framework для выбора подхода к работе в зависимости от контекста:

> **Cynefin** — framework принятия решений, классифицирующий ситуации по четырём доменам: **Clear** (best practices), **Complicated** (good practices, нужен эксперт), **Complex** (emergent practices, нужен experiment), **Chaotic** (novel practices, действуй немедленно).

Для выбора [[agile-practices|development process]]: Waterfall работает в Clear-домене (требования известны), Agile/Scrum — в Complicated, Kanban — в Complex (непредсказуемый поток). Jez Humble и David Farley в *"Continuous Delivery"* (2010) формализовали CD как ответ на потребность в быстром feedback loop.

---

## Git Workflows

```
TRUNK-BASED DEVELOPMENT (recommended):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main ─●─●─●─●─●─●─●─●→
       ↑ ↑   ↑
       Short-lived feature branches
       (hours, max 1-2 days)

+ Continuous integration
+ Less merge conflicts
+ Forces small changes
+ Works with feature flags

GIT FLOW (legacy, avoid):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main    ─●───────────●─────→
develop ─●─●─●─●─●─●─●─●─●─→
feature ──┬─●─●─●─┘
          Long-lived branches

- Merge conflicts
- Delayed integration
- Complex branching

GITHUB FLOW (simple):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
main ─●─●─●─●─●─●→
       ↑ ↑
       Feature branches + PR
       Deploy from main

Good balance for most teams.
```

## Sprint Process

```
SPRINT PLANNING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Duration: 1-2 weeks
Commitment: 80% of capacity (buffer)

INPUT:
• Prioritized backlog
• Team capacity
• Carry-over from last sprint

OUTPUT:
• Sprint goal
• Committed items
• Clear acceptance criteria

DAILY STANDUP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Duration: 15 min max
Focus: Blockers, not status

Format:
1. What I completed
2. What I'm working on
3. Any blockers

SPRINT REVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demo working software
Stakeholder feedback
Celebrate wins

RETROSPECTIVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What worked well?
What didn't?
What to try next sprint?
ACTION ITEMS (1-3 max)
```

## Release Management

```
RELEASE FREQUENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Deploy frequently, small changes

Daily: Ideal for web apps
Weekly: Common for APIs
Bi-weekly: If more coordination needed

RELEASE CHECKLIST:
□ Tests passing
□ Code reviewed
□ Staging verified
□ Rollback plan ready
□ Monitoring in place
□ Communication sent

FEATURE FLAGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploy code hidden behind flags.
Enable for % of users.
Instant rollback = disable flag.

Tools: LaunchDarkly, Split, internal

ROLLBACK STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Database migrations reversible
• Feature flags for instant disable
• Automated rollback on error spike
• Previous version always deployable
```

## Definition of Done

```
TASK DONE WHEN:
□ Code complete
□ Tests written and passing
□ Code reviewed
□ Documentation updated
□ Deployed to staging
□ Product sign-off (if needed)

SPRINT DONE WHEN:
□ All committed items done
□ Demos prepared
□ Retro action items from last sprint completed

RELEASE DONE WHEN:
□ Deployed to production
□ Monitoring confirms healthy
□ Stakeholders notified
□ Documentation public
```

---

## Связанные темы

- [[engineering-practices]] — практики качества
- [[agile-practices]] — agile методологии
- [[scaling-engineering-org]] — процессы при масштабе

## Источники

### Теоретические основы
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Royce W. "Managing the Development of Large Software Systems" — IEEE WESCON, 1970 | Статья | Waterfall model (и его ограничения) |
| 2 | Snowden D. "A Leader's Framework for Decision Making" — HBR, 2007 | Статья | Cynefin framework |
| 3 | Humble J., Farley D. "Continuous Delivery" — Addison-Wesley, 2010 | Книга | CD pipeline, deployment automation |

### Практические руководства
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Trunk Based Development](https://trunkbaseddevelopment.com/) | Guide | Short-lived branches |
| 2 | [Continuous Delivery](https://continuousdelivery.com/) | Book/Site | CD practices |
| 3 | [Feature Flags](https://martinfowler.com/articles/feature-toggles.html) | Article | Feature toggles taxonomy |

---

## Связь с другими темами

**[[engineering-practices]]** — Development process и engineering practices — два взаимодополняющих аспекта delivery. Process определяет workflow (git workflows, sprint cadence, release management), а practices определяют quality standards (code review, testing strategy, CI/CD). Без хороших practices процесс превращается в ceremony без substance, а без process practices не масштабируются.

**[[agile-practices]]** — Agile — это philosophy, а development process — конкретная реализация. Trunk-based development, sprint planning, retrospectives — все это implementations agile принципов. Важно помнить, что process должен serve team, а не наоборот: если процесс замедляет вместо ускорения, его нужно адаптировать, что является core agile principle.

## Источники и дальнейшее чтение

- **Kim et al., "The Phoenix Project" (2016)** — Через narrative form показывает, как broken development process (long release cycles, no CI/CD, manual deployments) приводит к organizational crisis. Three Ways (flow, feedback, continuous learning) — fundamental principles для дизайна development process.
- **Camille Fournier, "The Manager's Path" (2017)** — Описывает, как менеджер на каждом уровне участвует в определении и улучшении development process: от EM, facilitating retrospectives, до VP Engineering, устанавливающего org-wide standards.
- **Will Larson, "An Elegant Puzzle" (2019)** — Содержит practical frameworks для оптимизации development process, включая sizing sprints, managing technical debt и balancing feature work с infrastructure improvements. Системный подход к process design.


## Проверь себя

> [!question]- Trunk-based vs Git Flow
> Команда использует Git Flow с long-lived branches (feature branches живут 2-3 недели). Merge conflicts постоянны, integration поздний. Обоснуйте переход на trunk-based development и опишите конкретный transition plan, включая feature flags для incomplete work.

> [!question]- Sprint commitment vs reality
> Команда постоянно не выполняет sprint commitment: берут на 100% capacity, но доделывают 60%. Используя правила из файла, определите ошибку и предложите fix. Что значит 80% capacity rule?

## Ключевые карточки

Почему Trunk-based development лучше Git Flow для большинства команд?
?
Short-lived branches (hours, max 1-2 days), continuous integration, less merge conflicts, forces small changes, works with feature flags. Git Flow: merge conflicts, delayed integration, complex branching.

Какой формат daily standup наиболее эффективен?
?
15 min max. Focus на blockers, не status. Формат: 1. What I completed. 2. What I'm working on. 3. Any blockers. Если нет blockers — быстро.

Что включает Definition of Done для task?
?
Code complete, tests written and passing, code reviewed, documentation updated, deployed to staging, product sign-off (if needed).

Как feature flags помогают release management?
?
Deploy code hidden behind flags. Enable for % of users. Instant rollback = disable flag. Позволяет trunk-based development с incomplete features.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[agile-practices]] | Agile как philosophy за процессом |
| Углубиться | [[engineering-practices]] | Quality practices для процесса |
| Смежная тема | [[git-workflows]] | Git workflows в деталях |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
