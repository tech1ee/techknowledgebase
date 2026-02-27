---
title: "Делегирование: Отпустить контроль"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
reading_time: 28
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
difficulty: intermediate
target-role: [tech-lead, em, director]
teaches:
  - когда делегировать
  - как делегировать эффективно
  - ошибки делегирования
sources: [turn-the-ship-around, managers-path, high-output-management]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[one-on-one-meetings]]"
  - "[[scaling-engineering-org]]"
  - "[[building-engineering-team]]"
prerequisites:
  - "[[em-fundamentals]]"
  - "[[one-on-one-meetings]]"
---

# Делегирование: Отпустить контроль

> **TL;DR:** Делегирование — не "сбросить работу", а инвестиция в рост команды. Главная ошибка: делегировать task, а не outcome. Правильно: передать ответственность за результат, дать authority, обеспечить support. Если делаешь сам "потому что быстрее" — ты bottleneck и команда не растёт.

---

## Теоретические основы

### Теория делегирования в менеджменте

> **Определение:** Делегирование — передача полномочий (authority) и ответственности (responsibility) за выполнение задачи или достижение результата от руководителя к подчинённому при сохранении accountability (подотчётности) за итоговый результат у руководителя.

Классическое различие authority/responsibility/accountability восходит к работам Henri Fayol (*"Administration Industrielle et Generale"*, 1916), который определил delegation как один из 14 принципов управления.

### Матрица Эйзенхауэра и приоритизация делегирования

Dwight D. Eisenhower предложил матрицу urgent/important, которая стала основой для принятия решений о делегировании (популяризирована Stephen Covey, *"The 7 Habits of Highly Effective People"*, 1989):

| | **Urgent** | **Not Urgent** |
|---|-----------|----------------|
| **Important** | Делай сам (кризисы, дедлайны) | Планируй и **делегируй** (стратегия, развитие) |
| **Not Important** | **Делегируй** (рутина, запросы) | Устрани (time wasters) |

### Situational Leadership и уровни делегирования

Hersey & Blanchard (1969) определили, что уровень делегирования зависит от зрелости сотрудника. L. David Marquet в *"Turn the Ship Around!"* (2012) расширил эту модель, предложив **7 уровней authority** — от «скажи мне что делать» до «действуй самостоятельно, сообщай периодически»:

| Уровень | Формулировка | Когда применять |
|---------|-------------|-----------------|
| 1 | «Скажи мне что делать» | Новичок, критическая ситуация |
| 2 | «Изучи и предложи варианты» | Junior, новая область |
| 3 | «Предложи решение, я одобрю» | Mid-level, знакомая задача |
| 4 | «Действуй, но сообщи до исполнения» | Senior, важная задача |
| 5 | «Действуй и сообщи после» | Доверенный специалист |
| 6 | «Действуй, сообщай периодически» | Staff-level, его зона |
| 7 | «Действуй, сообщай по необходимости» | Full ownership |

### RACI-матрица

> **RACI** — инструмент распределения ответственности: **R**esponsible (кто делает), **A**ccountable (кто отвечает за результат), **C**onsulted (кого спрашивают), **I**nformed (кого информируют). Формализует делегирование на уровне процессов и проектов.

RACI помогает EM избежать двух крайностей: **micromanagement** (менеджер остаётся R для всего) и **abdication** (менеджер отпускает без A). Правильное делегирование: менеджер = A, сотрудник = R, с чёткими check-in points в [[one-on-one-meetings|1-on-1]].

---

## Зачем это нужно?

### Типичная ситуация

Менеджер перегружен. Команда ждёт его решений. Инженеры скучают — интересные tasks у менеджера. При его отсутствии работа встаёт. Сам менеджер работает 60 часов, выгорает, жалуется что "некому делегировать".

**Без эффективного делегирования:**
- Manager = bottleneck
- Team не развивается
- Single point of failure
- Burnout менеджера
- Low engagement команды

**С правильным делегированием:**
- Масштабируемость
- Team ownership
- Growth opportunities
- Manager focus на стратегию
- Resilient organization

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Время менеджеров на tasks для делегирования | 21% | Harvard Business Review |
| ROI от развития через delegation | 6x | McKinsey |
| Managers считающие себя хорошими delegators | 53% | Gallup |
| Их direct reports согласны | 28% | Gallup |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **New EM** | Critical | Научись отпускать coding |
| **Experienced EM** | High | Audit текущее делегирование |
| **Tech Lead** | High | Даже без formal authority |
| **Director+** | Critical | Делегировать whole areas |
| **IC** | Medium | Как принимать делегированное |

---

## Терминология

| Термин | Определение | IT-аналогия |
|--------|-------------|-------------|
| **Delegation** | Передача ответственности за результат | Fork with ownership |
| **Abdication** | Бросить task без support | Fire and forget (плохо) |
| **Micromanagement** | Контроль каждого шага | Sync calls блокируют всё |
| **Outcome Delegation** | Делегировать ЧТО, не КАК | API contract, не implementation |
| **Authority** | Право принимать решения | Admin permissions |

### Матрица делегирования

```
            LOW SKILL        HIGH SKILL
         ┌─────────────────┬─────────────────┐
         │                 │                 │
HIGH     │    DEVELOP      │    DELEGATE     │
WILL     │  Coach + Guide  │  Trust + Check  │
         │                 │                 │
         ├─────────────────┼─────────────────┤
         │                 │                 │
LOW      │    DIRECT       │    MOTIVATE     │
WILL     │ Specific tasks  │  Understand why │
         │ Close followup  │  Rebuild trust  │
         │                 │                 │
         └─────────────────┴─────────────────┘
```

---

## Как это работает?

### Уровни делегирования

```
LEVEL 1: TELL ME WHAT TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manager решает всё.
Delegate только execution.
"Сделай X, потом Y, потом Z."

Когда: Новичок, critical task, learning.
Risk: Нет роста, bottleneck.

LEVEL 2: RESEARCH AND RECOMMEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Person исследует options.
Рекомендует решение.
Manager одобряет или корректирует.
"Изучи варианты и приходи с recommendation."

Когда: Developing skill, moderate risk.
Risk: Медленнее, но рост.

LEVEL 3: DECIDE AND INFORM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Person принимает решение.
Информирует manager.
Manager может вмешаться (редко).
"Реши сам и сообщи мне."

Когда: Competent, reversible decisions.
Risk: Нужен alignment upfront.

LEVEL 4: ACT INDEPENDENTLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Person действует автономно.
Сообщает периодически (status).
Manager узнаёт из results.
"Это твоя область. Держи в курсе."

Когда: Expert, trusted, low-risk domain.
Risk: May miss synergies.

LEVEL 5: OWN THE OUTCOME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Person отвечает за whole area.
Сам решает что делать и как.
Manager обеспечивает resources.
"Ты owner этого. Чем помочь?"

Когда: Senior, strategic area.
Risk: Alignment на goals critical.
```

### Что можно делегировать

```
ДЕЛЕГИРУЙ:
✓ Operational tasks (повторяющиеся)
✓ Development opportunities (stretch)
✓ Decisions в их expertise
✓ Process ownership
✓ Cross-functional collaboration
✓ Technical research
✓ Documentation
✓ Onboarding новичков

НЕ ДЕЛЕГИРУЙ:
✗ Hire/Fire decisions
✗ Performance reviews (можно собрать input)
✗ Confidential HR matters
✗ Crisis communication (ты on the hook)
✗ Team culture (можно involve, но ты owner)
✗ Relationships с stakeholders (можно share)
✗ Strategic decisions (можно input)
```

### Delegation Framework: RACI-like

```
WHAT: Чёткий outcome
WHO: Owner (single point)
WHEN: Deadlines и checkpoints
HOW MUCH: Scope и authority level
WHY: Context и priority
SUPPORT: Resources available

EXAMPLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT: Implement caching layer for API
WHO: Alice (owner), Bob (consulted)
WHEN: Design by Friday, implementation by Q end
HOW MUCH: Level 3 — decide and inform
WHY: P99 latency критичен для sales deal
SUPPORT: Can use $5K for tools, my time for blockers
```

---

## Пошаговый процесс

### Перед делегированием

**Шаг 1: Определи что делегировать**
```
AUDIT ТВОЕГО ВРЕМЕНИ:
□ Что забирает много времени?
□ Что может сделать кто-то другой?
□ Что даст growth opportunity?
□ Что ты делаешь "по привычке"?

WARNING SIGNS:
• "Только я могу это сделать" (red flag)
• "Быстрее сам" (short-term thinking)
• "Никто не хочет" (не спросил)
```

**Шаг 2: Выбери правильного человека**
```
КРИТЕРИИ:
□ Skill level (или potential + time)
□ Interest и motivation
□ Current workload
□ Development goals alignment

MATCHING:
• Stretch assignment → High potential, eager
• Critical task → Proven, reliable
• Learning opportunity → Developing, willing
```

**Шаг 3: Определи уровень автономии**
```
ФАКТОРЫ:
• Person's experience with similar
• Reversibility of decisions
• Impact of failure
• Your availability for support

Rule: Err on more autonomy, not less.
Micromanagement costs more than mistakes.
```

### Во время делегирования

**Шаг 4: Handoff conversation**
```
СТРУКТУРА (30-45 min):

1. CONTEXT [10 min]
"Вот background и почему это важно..."
• Business context
• History/constraints
• Stakeholders

2. OUTCOME [5 min]
"Success looks like..."
• Specific deliverable
• Quality criteria
• Timeline

3. AUTHORITY [5 min]
"Ты можешь..."
• Decision level
• Budget (if any)
• Who to involve

4. SUPPORT [5 min]
"Я помогу с..."
• Resources available
• Escalation path
• My availability

5. QUESTIONS [10 min]
"Что неясно?"
• Clarify all ambiguity
• Document decisions
```

**Шаг 5: Confirm understanding**
```
НЕ: "Всё понятно?"
ДА: "Расскажи, как понял задачу?"

Listen for:
• Correct understanding of outcome
• Awareness of constraints
• Realistic assessment of challenges
• Clear first steps
```

### После делегирования

**Шаг 6: Check-in without micromanaging**
```
TIMING:
• Complex task: daily standup + weekly deep-dive
• Routine task: weekly mention
• Strategic: monthly review

QUESTIONS TO ASK:
"Как продвигается?"
"Есть blockers где нужна моя помощь?"
"Что-то изменилось что я должен знать?"

QUESTIONS TO AVOID:
"Почему сделал так, а не так?"
"Покажи каждый шаг"
"Я бы сделал по-другому..."
```

**Шаг 7: Feedback and Recognition**
```
AFTER COMPLETION:
□ Acknowledge результат публично
□ Дай specific feedback (что хорошо, что улучшить)
□ Обсуди learning в 1-on-1
□ Document для performance review
```

---

## Скрипты и Templates

### Delegation Conversation Script

```
"Хочу предложить тебе [task/project].

CONTEXT:
[Почему это важно, background]

OUTCOME:
Успех выглядит как [specific deliverable]
К [deadline].

AUTHORITY:
Это Level [X] delegation — [объяснить что это значит].
Ты можешь [specific decisions].
Для [что-то] нужно согласование со мной.

SUPPORT:
Я доступен [когда].
[Resources] в твоём распоряжении.
Если blockers — сразу ко мне.

Как это звучит? Что нужно уточнить?"
```

### Declining to Do It Yourself

```
Когда просят сделать тебя самого:

"Я понимаю urgency. Но лучше если это
сделает [Name], потому что:
1. Это в области её развития
2. У неё есть context
3. Это создаст precedent для future

Я помогу ей быстро онбордиться.
Timeline может быть [adjustment]."
```

### Check-in Questions

```
ОТКРЫТЫЕ (начать разговор):
"Как идёт [project]?"
"Что самое сложное сейчас?"

КОНКРЕТНЫЕ (если нужно больше):
"Какой статус [milestone]?"
"Когда ожидаешь [deliverable]?"

SUPPORT (предложить помощь):
"Есть что-то, где нужна моя помощь?"
"Какие blockers я могу убрать?"

НЕ ГОВОРИ:
✗ "Почему так медленно?"
✗ "Я бы сделал иначе"
✗ "Дай я сам посмотрю"
```

### Task Delegation Template

```markdown
# Delegation: [Task Name]

## Context
[Why this matters, background, stakeholders]

## Outcome
**Success looks like:**
- [Specific deliverable 1]
- [Specific deliverable 2]

**Quality criteria:**
- [Criterion 1]
- [Criterion 2]

## Timeline
- Start: [Date]
- Checkpoint 1: [Date] — [What]
- Checkpoint 2: [Date] — [What]
- Complete: [Date]

## Authority Level
Level [1-5]: [Description]

**You can decide:**
- [Decision area]

**Check with me before:**
- [Decision area]

## Support Available
- Budget: [Amount/None]
- Resources: [Tools, people]
- My time: [Availability]
- Escalation: [How]

## Owner
[Name]

## Documented: [Date]
```

---

## Распространённые ошибки

### Ошибка 1: Delegation = Abdication

**Как выглядит:**
"Сделай это" и исчезаешь. Нет context, нет support, нет check-ins. Потом удивление что результат не тот.

**Почему это проблема:**
- Person set up for failure
- No learning happens
- Trust damaged
- Результат плохой

**Как исправить:**
```
DELEGATION ≠ ABANDONMENT

Формула: Delegate + Support + Check-in

• Дай полный context
• Будь доступен для questions
• Check in регулярно
• Помогай с blockers
```

### Ошибка 2: Delegate Task, Not Outcome

**Как выглядит:**
"Сделай API endpoint для X, используй Y framework, структура Z."

**Почему это проблема:**
- Нет ownership
- Нет learning
- Зависимость от тебя
- Демотивация

**Как исправить:**
```
ВМЕСТО: "Сделай X способом Y"
ДЕЛАЙ:  "Нам нужен результат Z. Как бы ты подошёл?"

Outcome delegation:
"API должен handle 1000 rps, latency <100ms,
backward compatible. Как планируешь?"
```

### Ошибка 3: Taking It Back

**Как выглядит:**
При первой сложности забираешь task обратно. "Давай я сам."

**Почему это проблема:**
- Person не учится справляться
- Signal: "Я тебе не доверяю"
- Ты остаёшься bottleneck

**Как исправить:**
```
ВМЕСТО забирать:

1. Coach через проблему
   "Какие варианты ты видишь?"

2. Provide resources
   "Вот человек/документ который поможет"

3. Pair temporarily
   "Давай вместе разберём, потом ты продолжишь"

Забирай ТОЛЬКО если:
• Critical deadline + no other way
• Person просит (и это reasonable)
```

### Ошибка 4: Upward Delegation

**Как выглядит:**
Person приходит: "Что мне делать?" Ты отвечаешь. Теперь ты решаешь все их проблемы.

**Почему это проблема:**
- Ты делаешь чужую работу
- Person не растёт
- Bottleneck на тебе

**Как исправить:**
```
ВМЕСТО: Дать ответ

ДЕЛАЙ: Coach к самостоятельному решению

"Какие варианты ты рассматривал?"
"Что бы ты порекомендовал и почему?"
"Если бы я был недоступен, что бы сделал?"

RULE: Они уходят с СВОИМ решением,
не с твоим.
```

### Ошибка 5: Only Delegate "Grunt Work"

**Как выглядит:**
Делегируешь только скучное. Интересное оставляешь себе.

**Почему это проблема:**
- Team не растёт
- Демотивация
- Не готовишь succession

**Как исправить:**
```
ДЕЛЕГИРУЙ СПЕЦИАЛЬНО:
• Stretch assignments
• Visibility opportunities
• Decision-making
• Stakeholder meetings

Ask yourself:
"What am I keeping that would
develop someone else?"
```

---

## Когда применять

### Делегируй больше, когда:

- У тебя нет capacity
- Task — growth opportunity для кого-то
- Это повторяющаяся work
- Другой имеет better expertise
- Нужен succession plan

### Делегируй меньше (или осторожнее), когда:

- Critical deadline + no buffer
- Person перегружен
- Task requires your authority
- Confidential/sensitive information
- Relationship-dependent (stakeholders знают только тебя)

### Red flags: ты недостаточно делегируешь

```
🚩 Работаешь больше 50 часов регулярно
🚩 Команда ждёт твоих решений
🚩 Только ты можешь сделать многое
🚩 Нет vacation backup
🚩 Команда не растёт
🚩 Говоришь "быстрее сам сделаю"
```

---

## Кейсы

### Turn the Ship Around: Intent-Based Leadership

**Контекст:** David Marquet — капитан подводной лодки USS Santa Fe, худшей по показателям в fleet.

**Проблема:** Traditional "leader-follower" model не работает в сложных средах.

**Решение: Intent-Based Leadership**
```
ВМЕСТО: "Погрузиться на 100 футов" (приказ)
ДЕЛАЙ:  "Капитан, я намерен погрузиться на 100 футов" (intent)

Leader: "Что ты думаешь? Какие риски?"
```

**Результат:** Santa Fe стала лучшей лодкой. 10+ офицеров стали капитанами.

**Урок:** Делегируй authority вместе с responsibility. "I intend to..." culture.

### Google: 20% Time

**Контекст:** Знаменитая (и controversial) практика Google.

**Подход:**
```
20% времени на проекты по выбору сотрудника.
Полное ownership и autonomy.
Многие продукты родились здесь (Gmail).
```

**Lesson:** Extreme delegation = innovation. Но нужна high-trust culture.

### Netflix: Context, Not Control

**Контекст:** Netflix Culture Deck.

**Принцип:**
```
"Give employees context to make decisions,
not rules and control."

Вместо approval process:
"Act in Netflix's best interest"
```

**Урок:** При высоком talent density можно делегировать больше. Trust as default.

---

## Quick Reference: Delegation Checklist

```
┌────────────────────────────────────────────────────────────┐
│                 DELEGATION CHECKLIST                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  BEFORE:                                                   │
│  □ Clear on outcome (not just task)?                       │
│  □ Right person identified?                                │
│  □ Appropriate authority level decided?                    │
│  □ Timeline and checkpoints set?                           │
│                                                            │
│  DURING HANDOFF:                                           │
│  □ Context provided (why it matters)?                      │
│  □ Success criteria explained?                             │
│  □ Authority boundaries clear?                             │
│  □ Support available explained?                            │
│  □ Understanding confirmed ("tell me back")?               │
│                                                            │
│  DURING EXECUTION:                                         │
│  □ Regular check-ins (not micromanaging)?                  │
│  □ Available for blockers?                                 │
│  □ Resisting urge to take over?                            │
│  □ Coaching through challenges?                            │
│                                                            │
│  AFTER:                                                    │
│  □ Recognized effort and result?                           │
│  □ Provided specific feedback?                             │
│  □ Discussed learnings?                                    │
│  □ Documented for performance review?                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Связанные темы

### Prerequisites
- [[em-fundamentals]] — роль EM
- [[one-on-one-meetings]] — где обсуждается delegation

### Следующие шаги
- [[building-engineering-team]] — team development
- [[scaling-engineering-org]] — org design
- [[motivation]] — intrinsic motivation через ownership

### Связи с другими разделами
- [[communication/giving-feedback]] — feedback на delegated work
- [[thinking/decision-making]] — delegation of decisions

---

## Источники

### Теоретические основы
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Fayol H. "Administration Industrielle et Generale" — 1916 | Книга | 14 принципов управления, delegation of authority |
| 2 | Hersey P., Blanchard K. "Management of Organizational Behavior" — 1969 | Книга | Situational Leadership, уровни зрелости |
| 3 | Covey S. "The 7 Habits of Highly Effective People" — Free Press, 1989 | Книга | Матрица Эйзенхауэра, stewardship delegation |
| 4 | Marquet L. D. "Turn the Ship Around!" — Portfolio/Penguin, 2012 | Книга | 7 уровней authority, intent-based leadership |

### Практические руководства
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [High Output Management](https://www.amazon.com/High-Output-Management-Andrew-Grove/dp/0679762884) | Book | Delegation and leverage |
| 2 | [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) | Book | Practical delegation |
| 3 | [Harvard Business Review: Delegation](https://hbr.org/topic/subject/delegation) | Articles | Research and frameworks |
| 4 | [Netflix Culture Deck](https://jobs.netflix.com/culture) | Document | Context not control |
| 5 | [Manager Tools: Delegation](https://www.manager-tools.com/2005/10/effective-delegation-hall-of-fame-guidance) | Podcast | Tactical how-to |
| 6 | **Multipliers** (Liz Wiseman, 2010) | Книга | How leaders amplify capability |
| 7 | **Drive** (Daniel Pink, 2009) | Книга | Motivation through autonomy |

---

## Связь с другими темами

**[[em-fundamentals]]** — Делегирование — один из фундаментальных навыков Engineering Manager, без которого невозможно масштабировать свой impact. Em-fundamentals описывает общую модель ответственности EM, где делегирование играет ключевую роль в переходе от индивидуального output к командному результату. Менеджер, который не умеет делегировать, остаётся bottleneck и не может эффективно выполнять другие обязанности EM.

**[[one-on-one-meetings]]** — 1-on-1 встречи — это основная площадка для обсуждения делегированных задач. Именно на 1-on-1 менеджер проводит handoff conversation, check-ins на прогресс, coaching при трудностях и feedback по завершении. Без регулярных качественных 1-on-1 делегирование превращается в abdication — задачи бросаются без support и follow-up.

**[[scaling-engineering-org]]** — При масштабировании инженерной организации делегирование становится не просто полезным навыком, а критической необходимостью. Директора и VP Engineering делегируют целые области ответственности менеджерам, которые в свою очередь делегируют дальше. Умение выстроить многоуровневую систему делегирования определяет, сможет ли организация вырасти без потери качества и скорости.

**[[building-engineering-team]]** — Делегирование — один из ключевых инструментов развития команды. Через stretch assignments и outcome delegation менеджер создаёт growth opportunities для инженеров. Правильно делегированная задача одновременно решает бизнес-потребность и развивает человека, формируя culture of ownership в команде.

## Источники и дальнейшее чтение

- **L. David Marquet, "Turn the Ship Around!" (2012)** — Фундаментальная книга об intent-based leadership, которая показывает, как передача authority вместе с responsibility трансформирует организацию. Пример USS Santa Fe демонстрирует, что делегирование на самом глубоком уровне создаёт лидеров на каждом уровне организации.
- **Peter Drucker, "The Effective Executive" (2006)** — Drucker формулирует принципы эффективного руководства, включая фокус на contribution и делегирование всего, что может быть сделано другими. Его концепция "what can I contribute that nobody else can?" помогает менеджерам определить, что не делегировать.
- **Camille Fournier, "The Manager's Path" (2017)** — Практическое руководство по делегированию на каждом уровне management карьеры, от Tech Lead до VP Engineering, с конкретными примерами и anti-patterns.

---

---

## Проверь себя

> [!question]- Почему "делегировать task" и "делегировать outcome" -- принципиально разные подходы?
> Task delegation ("сделай X способом Y") не даёт ownership и learning -- человек просто исполнитель. Outcome delegation ("нужен результат Z, как бы ты подошёл?") развивает thinking, создаёт ownership и готовит людей к более сложным задачам. Это разница между зависимостью и самостоятельностью.

> [!question]- Менеджер работает 60 часов, команда ждёт его решений, а интересные задачи всегда у менеджера. Какой паттерн ошибок здесь и как исправить?
> Три ошибки: 1) "быстрее сам" (short-term thinking), 2) делегирует только grunt work, 3) является single point of failure. Исправление: аудит времени, делегировать stretch assignments (не только скучное), определить уровни автономии по матрице skill/will, err on more autonomy.

> [!question]- Когда правильно забрать задачу обратно, а когда это ошибка?
> Забирать ТОЛЬКО если: critical deadline + no other way, или person просит (reasonable). Во всех остальных случаях -- coach через проблему ("какие варианты видишь?"), provide resources, pair temporarily. Забирание = signal "не доверяю", и ты остаёшься bottleneck.

---

## Ключевые карточки

Какие 5 уровней делегирования существуют?
?
Level 1: Tell me what to do (execute). Level 2: Research and recommend. Level 3: Decide and inform. Level 4: Act independently. Level 5: Own the outcome. Выбор уровня зависит от experience, risk, reversibility и availability for support.

Что такое Intent-Based Leadership (Turn the Ship Around)?
?
Вместо приказов ("погрузиться на 100 футов") -- намерения ("капитан, я намерен погрузиться на 100 футов"). Лидер спрашивает "что думаешь? какие риски?" и делегирует authority вместе с responsibility. USS Santa Fe стала лучшей лодкой, 10+ офицеров стали капитанами.

Какие red flags указывают на недостаточное делегирование?
?
Работаешь >50 часов регулярно, команда ждёт твоих решений, "только я могу сделать", нет vacation backup, команда не растёт, говоришь "быстрее сам сделаю". Каждый из этих сигналов = менеджер является bottleneck.

В чём разница между delegation и abdication?
?
Delegation = передать + support + check-in. Abdication = бросить без context и support. Формула: Delegate + Support + Check-in. Без context, availability для questions и regular check-ins -- это not delegation, а abandonment, ведущее к failure.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[building-engineering-team]] | Развитие команды через delegation |
| Углубиться | [[scaling-engineering-org]] | Многоуровневое делегирование при масштабировании |
| Смежная тема | [[motivation-science]] | Понять intrinsic motivation через autonomy |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-02-13*
*Связано с: [[leadership-overview]]*
