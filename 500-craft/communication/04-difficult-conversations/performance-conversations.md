---
title: "Performance Conversations: reviews, PIPs и promotion talks"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: advanced
teaches:
  - performance-review-structure
  - pip-management
  - promotion-conversations
  - difficult-feedback-delivery
tags:
  - topic/communication
  - type/deep-dive
  - level/advanced
related:
  - "[[giving-feedback]]"
  - "[[receiving-feedback]]"
  - "[[active-listening]]"
  - "[[delivering-bad-news]]"
prerequisites:
  - "[[giving-feedback]]"
  - "[[receiving-feedback]]"
  - "[[active-listening]]"
reading_time: 12
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Performance Conversations: говорить о performance без разрушения отношений

> **TL;DR:** Performance conversations = подготовка + structure + follow-through. Три типа: regular reviews (ongoing), improvement plans (PIP), promotion discussions. Ключевая идея: feedback должен быть ongoing, а не surprise на review. Применяется в: 1-on-1, annual reviews, PIP meetings, promotion discussions.

---

## Зачем это нужно?

### Представьте ситуацию

Annual review. Ты говоришь разработчику: "За этот год твоя productivity ниже ожиданий." Он в шоке: "Почему я узнаю это только сейчас?! Год прошёл, и никто не говорил!" Relationship damage, демотивация, возможно resignation.

**Без правильного подхода:**
- Surprises на reviews → defensiveness
- Unclear expectations → frustration
- Delayed feedback → missed growth opportunities
- Damaged trust → turnover

**С правильным подходом:**
- Ongoing feedback → no surprises
- Clear expectations → accountability
- Early intervention → course correction
- Constructive dialogue → growth

### Проблема в числах

```
┌─────────────────────────────────────────────────────────────────┐
│           СТАТИСТИКА PERFORMANCE CONVERSATIONS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  28%       сотрудников получают feedback несколько раз в год    │
│  19%       получают feedback раз в год или реже (Gallup)        │
│                                                                 │
│  69%       сотрудников говорят что работали бы усерднее         │
│            если бы их усилия better recognized                  │
│                                                                 │
│  92%       согласны: негативный feedback улучшает               │
│            performance (если дан правильно)                     │
│                                                                 │
│  21%       managers считают себя хорошими в difficult           │
│            conversations (Gartner)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Источники:** [Gallup Workplace](https://www.gallup.com/workplace/), [Gartner HR Research](https://www.gartner.com/)

---

## Для кого этот материал

| Уровень | Подходит? | Фокус |
|---------|-----------|-------|
| **Junior** | ⚠️ Частично | Как prepared к своим reviews |
| **Middle** | ✅ | Peer feedback, готовность к promotion talk |
| **Senior** | ✅ | Mentoring feedback, self-advocacy |
| **Tech Lead** | ✅ | Проводить reviews, PIPs, promotion cases |

---

## Терминология

| Термин | Что это | IT-аналогия |
|--------|---------|-------------|
| **Performance Review** | Формальная оценка работы за период | Как sprint retrospective — review что было |
| **PIP** | Performance Improvement Plan — план улучшения | Как incident response plan — structured approach to fix issue |
| **Promotion Talk** | Обсуждение готовности к следующему уровню | Как architecture review — ready for production? |
| **Calibration** | Выравнивание оценок между managers | Как code review standards — consistency |
| **Self-Assessment** | Самооценка сотрудника | Как self-review PR — ты первый reviewer своей работы |

---

## Как это работает?

### Три типа Performance Conversations

```
┌─────────────────────────────────────────────────────────────────┐
│             ТРИ ТИПА PERFORMANCE CONVERSATIONS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. REGULAR PERFORMANCE REVIEWS                                 │
│     ─────────────────────────────                               │
│     Периодические (quarterly/annual)                            │
│     Цель: assess progress, set goals, recognize                 │
│     Тон: constructive, forward-looking                          │
│                                                                 │
│  2. PERFORMANCE IMPROVEMENT (PIP)                               │
│     ─────────────────────────────                               │
│     Когда performance below expectations                        │
│     Цель: structured path to improvement                        │
│     Тон: serious but supportive                                 │
│                                                                 │
│  3. PROMOTION DISCUSSIONS                                       │
│     ──────────────────────                                      │
│     Готовность к следующему уровню                              │
│     Цель: assess readiness, identify gaps                       │
│     Тон: developmental, aspirational                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ongoing Feedback Culture

```
┌─────────────────────────────────────────────────────────────────┐
│              ONGOING vs ANNUAL FEEDBACK                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ ANNUAL-ONLY:                                                │
│                                                                 │
│  Jan ─────────────────────────────────────────────── Dec        │
│                                        [SURPRISE! You're below] │
│                                                                 │
│  ✅ ONGOING:                                                    │
│                                                                 │
│  Jan ──●──●──●──●──●──●──●──●──●──●──●──● Dec                  │
│        │  │  │  │  │  │  │  │  │  │  │  │                       │
│     small feedback touchpoints throughout year                  │
│     Review = summary, no surprises                              │
│                                                                 │
│  ПРИНЦИП: "If it's a surprise on review, you failed as manager" │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Источник:** [Radical Candor: Performance Development](https://www.radicalcandor.com/blog/performance-development-conversations/)

---

## Пошаговый процесс

### A. Regular Performance Review

#### Подготовка (за 2+ недели)

**Manager:**
1. Собери данные: achievements, feedback от peers, metrics
2. Review goals set in previous period
3. Prepare talking points (не script)
4. Schedule 60-90 минут в private setting

**Employee (self-assessment):**
1. List key accomplishments с impact
2. Note areas of growth
3. Identify challenges faced
4. Prepare questions/development goals

#### Структура разговора

**Шаг 1: Set the Stage (5 min)**
```
"Цель сегодня — обсудить твою работу за [период],
признать wins, обсудить areas for growth, и
поговорить о целях на следующий период.

Начнём с твоего self-assessment — как ты видишь
свою работу за это время?"
```

**Шаг 2: Employee Self-Assessment (15-20 min)**
- Дай employee говорить first
- Active listening, не перебивай
- Take notes

**Шаг 3: Manager Perspective (15-20 min)**

Используй STAR для specific examples:
```
"Хочу отметить [achievement] — когда ты [ситуация],
ты [действие], и это [результат]. Это exactly
то что мы хотим видеть на твоём уровне."

"Область для роста — [topic]. Например, [STAR
example]. Это важно потому что [why it matters]."
```

**Шаг 4: Discussion & Alignment (15-20 min)**
```
"Как ты видишь эти feedback points?"
"Что из этого resonates? Что вызывает вопросы?"
"Какая support нужна?"
```

**Шаг 5: Goals for Next Period (10-15 min)**
```
"На следующий [период] давай сфокусируемся на:
1. [Goal 1] — measured by [metric]
2. [Goal 2] — measured by [metric]

Как тебе эти цели? Реалистичны?"
```

**Шаг 6: Close with Next Steps (5 min)**
```
"Резюме: [key points]. Я отправлю written summary.
Следующий check-in [дата]. Questions?"
```

---

### B. Performance Improvement Plan (PIP)

#### Когда PIP необходим

```
┌─────────────────────────────────────────────────────────────────┐
│                    КОГДА НАЧИНАТЬ PIP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ PIP APPROPRIATE:                                            │
│  • Performance consistently below expectations                  │
│  • После нескольких feedback conversations без improvement      │
│  • Behavior patterns affecting team                             │
│  • Skills gap that needs structured development                 │
│                                                                 │
│  ❌ PIP NOT APPROPRIATE:                                        │
│  • One-time mistake (use regular feedback)                      │
│  • External factors beyond control                              │
│  • Unclear expectations (fix expectations first)                │
│  • As surprise — feedback должен быть ДО PIP                    │
│                                                                 │
│  ⚠️ PIP НЕ ДОЛЖЕН БЫТЬ ПЕРВЫМ FEEDBACK                         │
│     Это escalation после ongoing conversations                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### PIP Conversation Structure

**Pre-meeting:** Подготовь документ с HR/legal review

**Шаг 1: Direct Opening**
```
"Спасибо что пришёл. У нас серьёзный разговор.
Как мы обсуждали в [previous conversations],
есть concerns о твоём performance. Сегодня
мы формализуем план улучшения — PIP."
```

**Шаг 2: Present Specific Issues**
```
"Вот конкретные areas:
1. [Issue 1] — examples: [STAR]
2. [Issue 2] — examples: [STAR]

Это не соответствует expectations для
твоей роли, которые включают [criteria]."
```

**Шаг 3: Present the Plan**
```
"Вот план улучшения:
• Duration: [30/60/90 дней]
• Goals: [specific, measurable]
• Check-ins: [weekly/bi-weekly]
• Support: [resources, training, mentorship]
• Success criteria: [what 'improved' looks like]"
```

**Шаг 4: Acknowledge Emotions**
```
"Понимаю, это сложно слышать. Это не приговор —
это structured opportunity для improvement.
Многие проходят через это успешно."
```

**Шаг 5: Employee Response**
```
"Как ты видишь ситуацию? Есть ли что-то что
я должен знать о circumstances?"
```

**Шаг 6: Commitment**
```
"Нужна твоя commitment к этому плану.
Вопросы по expectations или процессу?"
```

#### PIP Follow-up

- Weekly check-ins (documented)
- Clear milestone tracking
- Adjust support if needed
- Honest assessment at end

---

### C. Promotion Discussion

#### Когда сотрудник спрашивает о promotion

**Скрипт (если готов):**
```
"Рад что ты думаешь о росте. Давай обсудим.

Для [следующий уровень] ключевые expectations:
1. [Criteria 1]
2. [Criteria 2]
3. [Criteria 3]

Из того что я вижу, ты already демонстрируешь
[strengths]. Areas для focus: [gaps].

Давай построим план чтобы закрыть эти gaps.
Timeline для review: [when]."
```

**Скрипт (если не готов):**
```
"Ценю что ты думаешь о росте — это отлично.

Честно: сейчас есть gap между текущим уровнем
и [следующий уровень]. Вот что я вижу:

Strengths: [what's working]
Gaps: [specific areas]

Это не 'нет' — это 'not yet'. Давай построим
план. Что если focus на [specific area] в
следующий квартал?"
```

#### Promotion Readiness Framework

```
┌─────────────────────────────────────────────────────────────────┐
│               PROMOTION READINESS ASSESSMENT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Для promotion на следующий уровень:                            │
│                                                                 │
│  1. ALREADY PERFORMING at next level (не "will grow into")      │
│     □ Consistently meeting higher-level expectations            │
│     □ Examples over 6+ months (не one-time)                     │
│                                                                 │
│  2. IMPACT соответствует уровню                                 │
│     □ Scope of work matches level                               │
│     □ Business impact documented                                │
│                                                                 │
│  3. SKILLS & BEHAVIORS                                          │
│     □ Technical skills at level                                 │
│     □ Communication/leadership at level                         │
│     □ Collaboration/influence at level                          │
│                                                                 │
│  4. STAKEHOLDER FEEDBACK                                        │
│     □ Peers see them at next level                              │
│     □ Cross-functional positive feedback                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Скрипты и Templates

### Use Case 1: Positive Review с Areas for Growth

**Ситуация:** Strong performer с одной области для improvement

**Скрипт:**
```
"Отличный квартал. Хочу начать с wins:
[STAR example of achievement]
[STAR example of achievement]

Ты consistently превосходишь expectations в
[area]. Это exactly что нужно для [next level].

Одна область для focus: [area]. Вот что я заметил:
[STAR example]. Это важно потому что [why].

Overall: ты on track. Давай работать над [area]
в следующем квартале. Как звучит?"
```

### Use Case 2: Underperformance без PIP

**Ситуация:** Performance dip, нужен course correction

**Скрипт:**
```
"Хочу обсудить твою работу за последние [период].
Это не formal warning, но важный checkpoint.

Я заметил [specific examples] — это ниже того
что я обычно вижу от тебя и что ожидается.

Что происходит? Есть ли что-то affecting работу?"

[Listen]

"Понимаю. Вот что мне нужно увидеть в следующие
[period]: [specific expectations].

Какая support нужна чтобы вернуться on track?"
```

### Use Case 3: PIP Opening Conversation

**Ситуация:** Formalize improvement plan после previous feedback

**Скрипт:**
```
"Спасибо что пришёл. Это важный разговор.

Как мы обсуждали [date] и [date], есть persistent
concerns о [performance areas]. Несмотря на наши
разговоры, я не вижу достаточного improvement.

Сегодня мы формализуем это в Performance
Improvement Plan. Это серьёзно, но это также
structured opportunity для success.

Вот документ. Давай пройдём по пунктам..."
```

### Use Case 4: Employee Disagrees с Feedback

**Ситуация:** Employee pushes back на review

**Скрипт:**
```
"Слышу что ты не согласен с этой assessment.
Расскажи свою perspective."

[Listen fully]

"Спасибо за context. Вот как я это вижу:
[restate your perspective с examples].

Мы можем не agree полностью, но вот что
важно: moving forward, expectation это [X].
Что нужно чтобы это работало?"
```

### Use Case 5: Self-Advocating для Promotion

**Для сотрудника (не manager):**

**Скрипт:**
```
"Хочу обсудить мой career path. Я заинтересован
в [следующий уровень] и хочу understand
что нужно чтобы туда попасть.

Вот что я сделал за последний год:
• [Achievement with impact]
• [Achievement with impact]
• [How I've grown]

Как ты видишь мою readiness? Какие gaps
мне нужно закрыть?"
```

---

## Распространённые ошибки

### Ошибка 1: Surprise Feedback на Review

**Неправильно:**
Первый раз говорить о проблеме на annual review

**Почему плохо:**
- Employee чувствует betrayal
- Нет шанса исправить
- Defensive reaction

**Правильно:**
Ongoing feedback → review = summary

### Ошибка 2: Sandwich Feedback

**Неправильно:**
"Ты молодец! Но performance низкий. Зато хороший README!"

**Почему плохо:**
- Dilutes message
- Creates distrust
- People learn to ignore praise

**Правильно:**
Separate positive и developmental feedback

### Ошибка 3: Vague Feedback

**Неправильно:**
"Нужно быть более proactive"
"Улучши communication"

**Почему плохо:**
- Непонятно что менять
- Нет actionable steps

**Правильно:**
STAR examples + specific expectations

### Ошибка 4: PIP как Surprise

**Неправильно:**
Первый серьёзный feedback = PIP

**Почему плохо:**
- Legal риски
- Unfair to employee
- Looks like setup for termination

**Правильно:**
PIP только после documented previous feedback

### Ошибка 5: Avoiding Difficult Conversations

**Неправильно:**
"Не хочу демотивировать, промолчу"

**Почему плохо:**
- Проблема растёт
- Unfair to employee (no chance to improve)
- Unfair to team

**Правильно:**
[[Radical Candor]] — Care + Challenge

---

## Когда использовать / НЕ использовать

### Timing для разных conversations

| Тип | Когда | Как часто |
|-----|-------|-----------|
| Quick feedback | Real-time или same day | Daily/weekly |
| 1-on-1 check-in | Scheduled | Weekly/bi-weekly |
| Formal review | End of period | Quarterly/semi/annual |
| PIP | After multiple feedbacks fail | As needed |
| Promotion talk | When employee asks or ready | As appropriate |

### Red Flags: когда escalate

```
□ Repeated same issue after feedback
□ Performance affecting team
□ Behavioral concerns
□ No improvement after 2-3 conversations
→ Consider PIP или HR involvement
```

---

## Практика

### Упражнение 1: Prepare Review

**Задание:**
Выбери реального (или hypothetical) direct report.
Подготовь outline для review:

1. 2-3 specific achievements (STAR)
2. 1-2 areas for development (STAR)
3. Goals for next period

### Упражнение 2: Difficult Conversation Roleplay

**Сценарий:**
Employee пропускает дедлайны третий раз подряд.
Напиши script для conversation.

<details><summary>Example</summary>

```
"Хочу обсудить дедлайны. За последние три спринта
[specific dates] задачи [X, Y, Z] были сданы
с задержкой [N дней].

Это влияет на [team dependencies, release].

Расскажи что происходит с твоей стороны?

[Listen]

Вот что мне нужно увидеть: tasks delivered on time
или proactive communication о blockers ДО дедлайна.

Какая support нужна чтобы это работало?"
```
</details>

### Ежедневная практика

| День | Фокус | Действие |
|------|-------|----------|
| Пн | Ongoing feedback | Дай one piece of feedback someone |
| Вт | Document | Запиши feedback что дал/получил |
| Ср | Prepare | Review notes for upcoming 1-on-1 |
| Чт | Self-reflect | Как бы ты оценил свой performance? |
| Пт | Goals check | Progress против goals? |

---

## Связанные темы

### Prerequisites
- [[giving-feedback]] — SBI и Radical Candor
- [[receiving-feedback]] — для self-assessment
- [[active-listening]] — для hearing employee

### Эта тема открывает
- [[delivering-bad-news]] — включая termination
- [[career-development]] — growth planning

### Связанные навыки
- [[conflict-resolution]] — для difficult conversations
- [[negotiation-fundamentals]] — для promotion discussions

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Confirm: Difficult Review Conversations](https://www.confirm.com/blog/how-to-have-difficult-performance-review-conversations-a-guide-for-people-managers) | Guide | Structure, scripts |
| 2 | [Lattice: Mastering Performance Reviews](https://lattice.com/articles/mastering-the-performance-review-conversation) | Guide | Best practices |
| 3 | [Radical Candor: Performance Development](https://www.radicalcandor.com/blog/performance-development-conversations/) | Framework | Ongoing feedback |
| 4 | [First Round: 12 Expert Tips](https://review.firstround.com/elevate-your-performance-review-conversations-with-these-12-expert-tips/) | Guide | Detailed techniques |
| 5 | [UMN HR: Difficult Conversations](https://hr.umn.edu/supervising/resources/Difficult-Performance-Conversations) | Guide | University resources |
| 6 | [WeThrive: PIP Questions](https://wethrive.net/performance-management-resources/performance-improvement-plan-questions-5-things-to-consider/) | Guide | PIP structure |
| 7 | [AMA: Difficult Performance Reviews](https://www.amanet.org/difficult-performance-reviews-how-to-turn-painful-conversations-into-positive-results/) | Training | Turning negative to positive |
| 8 | [Mitratech: Tips for HR Leaders](https://mitratech.com/resource-hub/blog/navigating-difficult-conversations-in-performance-reviews-tips-for-hr-leaders/) | Guide | HR perspective |

*Исследование проведено: 2026-01-18*

---

---

## Проверь себя

> [!question]- Разработчик на PIP показал improvement за первые 2 недели, но затем вернулся к старым паттернам. Как ты перестроишь оставшийся план и weekly check-ins?
> Зафиксировать regression в документации с STAR-примерами. На ближайшем check-in прямо назвать паттерн: "Первые две недели я видел X, но последнюю неделю снова Y." Пересмотреть milestones — возможно, разбить крупные цели на более мелкие с недельным контролем. Добавить accountability partner или дополнительную support (mentorship, pair programming). Честно обсудить consequences: если improvement не устойчив, PIP считается не пройденным. Ключевое — не "перезапускать" PIP, а усилить structured support в рамках существующего плана.

> [!question]- Почему принцип "already performing at next level" для promotion важнее чем "will grow into the role"? Как это связано с calibration между менеджерами?
> Потому что promotion на основе потенциала создаёт inconsistency: разные менеджеры по-разному оценивают "потенциал", что ломает calibration. Если стандарт — demonstrated performance за 6+ месяцев, то calibration session имеет объективную базу: конкретные примеры, impact, stakeholder feedback. Это также защищает сотрудника: получив promotion, он уже уверенно работает на новом уровне и не попадает в ситуацию "promoted and struggling". Для организации это снижает риск regret promotions и последующих PIPs.

> [!question]- Менеджер из твоей команды жалуется: "Я дал честный feedback, а сотрудник подал resignation." Проанализируй, какие ошибки из раздела "Распространённые ошибки" он мог допустить и как их предотвратить.
> Вероятные ошибки: (1) Surprise feedback — если это был первый раз, сотрудник не имел шанса исправиться; (2) Sandwich feedback — если критика была "спрятана", сотрудник мог воспринять её как лицемерие; (3) Vague feedback без STAR — "будь более proactive" воспринимается как атака на личность. Предотвращение: ongoing feedback culture (no surprises на review), separate positive и developmental feedback, конкретные STAR-примеры с actionable next steps. Также важно: после критического feedback дать employee время обработать эмоции и вернуться к разговору через 1-2 дня.

> [!question]- Ты Tech Lead и хочешь обсудить promotion с менеджером, используя подход из Use Case 5. Как ты адаптируешь скрипт self-advocacy, учитывая что в [[staff-plus-engineering]] ключевой критерий — влияние за пределами своей команды?
> Стандартный скрипт фокусируется на личных achievements. Для Staff+ уровня нужно перестроить narrative: вместо "я сделал X" показать "благодаря моей инициативе Y, три команды смогли Z." Конкретно: подготовить примеры cross-team impact (архитектурные решения, shared libraries, mentoring в других командах), собрать feedback от stakeholders за пределами своей команды, показать influence without authority. В разговоре с менеджером: "Вот мой impact за пределами нашей команды: [примеры]. Как ты видишь мою readiness для Staff role с учётом scope of influence?"

---

## Ключевые карточки

Три типа performance conversations?
?
1) Regular Performance Reviews — периодические (quarterly/annual), assess progress и set goals. 2) Performance Improvement Plan (PIP) — когда performance consistently below expectations, structured path to improvement. 3) Promotion Discussions — оценка readiness к следующему уровню, identify gaps.

Какой главный принцип ongoing feedback culture?
?
"If it's a surprise on review, you failed as manager." Feedback должен быть ongoing (маленькие touchpoints на протяжении года), а review — только summary уже известной информации. Без surprises.

Какие 4 критерия Promotion Readiness Assessment?
?
1) Already performing at next level (consistently, 6+ месяцев, не "will grow into"). 2) Impact соответствует уровню (scope и business impact задокументированы). 3) Skills & Behaviors (technical, communication/leadership, collaboration/influence). 4) Stakeholder Feedback (peers видят на следующем уровне, cross-functional positive feedback).

Когда PIP appropriate, а когда нет?
?
Appropriate: performance consistently below expectations, после нескольких feedback conversations без improvement, behavior patterns affecting team, skills gap requiring structured development. NOT appropriate: one-time mistake (regular feedback), external factors beyond control, unclear expectations (fix expectations first), как surprise без предшествующего feedback.

Структура Regular Performance Review (6 шагов)?
?
1) Set the Stage (5 мин) — обозначить цель и начать с self-assessment. 2) Employee Self-Assessment (15-20 мин) — дать говорить первым. 3) Manager Perspective (15-20 мин) — STAR-примеры achievements и areas for growth. 4) Discussion & Alignment (15-20 мин) — что resonates, какие вопросы. 5) Goals for Next Period (10-15 мин) — measurable goals. 6) Close with Next Steps (5 мин) — summary, written follow-up, дата check-in.

Почему Sandwich Feedback — ошибка?
?
"Ты молодец! Но performance низкий. Зато хороший README!" — dilutes critical message, creates distrust (люди учатся игнорировать похвалу, ожидая "но"), employee не понимает серьёзность. Правильно: разделять positive и developmental feedback, давать каждый тип отдельно с конкретными STAR-примерами.

Как правильно открыть PIP-разговор?
?
Сослаться на предыдущие feedback conversations (даты), назвать конкретные areas с STAR-примерами, представить план (duration, goals, check-ins, support, success criteria), acknowledge emotions ("это не приговор, а structured opportunity"), дать employee высказаться, получить commitment. PIP никогда не должен быть первым feedback.

Скрипт self-advocacy для promotion — ключевые элементы?
?
1) Обозначить интерес к конкретному уровню. 2) Представить achievements с impact (не просто "я сделал", а "это привело к"). 3) Спросить о readiness и gaps. 4) Не требовать, а начать диалог: "Как ты видишь мою readiness? Какие gaps мне нужно закрыть?" Инициатива на сотруднике, но разговор collaborative.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Базовые навыки feedback | [[giving-feedback]] | SBI-фреймворк и Radical Candor — фундамент для всех performance conversations |
| Принимать feedback | [[receiving-feedback]] | Навык self-assessment и необоронительного восприятия критики |
| Сообщать плохие новости | [[delivering-bad-news]] | Следующий уровень: termination, layoffs, project cancellation |
| Разрешение конфликтов | [[conflict-resolution]] | Когда performance conversation переходит в конфликт или disagreement |
| Переговоры о promotion | [[negotiation-fundamentals]] | Тактики и фреймворки для promotion discussions и salary talks |
| Performance management (leadership) | [[performance-management]] | Системный взгляд менеджера: процессы, calibration, OKR-привязка |
| Staff+ карьерный трек | [[staff-plus-engineering]] | Критерии promotion на Staff/Principal — влияние за пределами команды |

---

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
