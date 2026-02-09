---
title: "Performance Management: Оценка и развитие"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: intermediate
target-role: [em, director, hr]
prerequisites:
  - "[[em-fundamentals]]"
  - "[[one-on-one-meetings]]"
teaches:
  - continuous feedback
  - performance reviews
  - managing underperformance
unlocks:
  - "[[difficult-conversations]]"
  - "[[hiring-engineers]]"
tags: [leadership, performance, feedback, reviews, coaching]
sources: [radical-candor, managers-path, netflix-culture, google-rework]
---

# Performance Management: Оценка и развитие

> **TL;DR:** Performance management — это не годовой review, а continuous process. Цель — не оценить, а развить. Feedback должен быть frequent (еженедельно), specific (поведение + impact), и timely (в течение 48 часов). Если review — сюрприз для сотрудника, ты провалил как менеджер.

---

## Зачем это нужно?

### Типичная ситуация

Performance review раз в год. Менеджер вспоминает последний месяц (recency bias). Сотрудник слышит о проблемах впервые. "Почему не сказал раньше?!" Frustration с обеих сторон. Документ уходит в HR, ничего не меняется.

**Без continuous performance management:**
- Проблемы накапливаются
- Top performers уходят (не видят growth)
- Underperformers не знают о проблемах
- Review = stress для всех

**С правильным процессом:**
- Постоянная обратная связь
- Раннее выявление проблем
- Чёткие expectations
- Development-focused culture

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Сотрудники недовольные feedback frequency | 65% | Gallup |
| Компании отказавшиеся от annual reviews | 30%+ | SHRM |
| Повышение engagement от continuous feedback | +14% | Gallup |
| Менеджеры тратящие <3ч/год на review каждого | 60% | McKinsey |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **New EM** | Critical | Начни с continuous feedback |
| **Experienced EM** | High | Проверь свой процесс |
| **Director** | High | Калибровка между командами |
| **HR/People Ops** | Critical | Дизайн системы |
| **IC** | Medium | Понять процесс и требовать feedback |

---

## Терминология

| Термин | Определение | IT-аналогия |
|--------|-------------|-------------|
| **Continuous Feedback** | Регулярная обратная связь | Continuous integration — merge часто, не copy |
| **Performance Review** | Формальная оценка (semi-annual/annual) | Release review — snapshot состояния |
| **Calibration** | Выравнивание оценок между менеджерами | Code review для reviews |
| **PIP** | Performance Improvement Plan | Debugging mode — structured fix attempt |
| **Rating** | Числовая/категориальная оценка | Test score — snapshot of performance |

### Компоненты performance management

```
CONTINUOUS (ongoing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Weekly 1-on-1 feedback
• Real-time recognition
• Coaching conversations
• Informal check-ins

PERIODIC (quarterly/semi-annual)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Goal setting/review
• Progress check
• Development planning
• Written documentation

FORMAL (annual/bi-annual)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Performance review
• Compensation decisions
• Promotion decisions
• Calibration
```

---

## Как это работает?

### Performance Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE CYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                     ┌──────────────┐                            │
│                     │  SET GOALS   │                            │
│                     │   (Q1 start) │                            │
│                     └──────┬───────┘                            │
│                            │                                    │
│        ┌───────────────────┼───────────────────┐                │
│        │                   │                   │                │
│        ▼                   ▼                   ▼                │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐           │
│  │ FEEDBACK  │◄────►│ FEEDBACK  │◄────►│ FEEDBACK  │           │
│  │  (weekly) │      │  (weekly) │      │  (weekly) │           │
│  └───────────┘      └───────────┘      └───────────┘           │
│        │                   │                   │                │
│        ▼                   ▼                   ▼                │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐           │
│  │  CHECKIN  │      │  CHECKIN  │      │  REVIEW   │           │
│  │   (Q1)    │      │   (Q2)    │      │  (mid-yr) │           │
│  └───────────┘      └───────────┘      └───────────┘           │
│        │                   │                   │                │
│        └───────────────────┼───────────────────┘                │
│                            │                                    │
│                            ▼                                    │
│                     ┌──────────────┐                            │
│                     │    ANNUAL    │                            │
│                     │   REVIEW     │                            │
│                     └──────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Feedback Framework: SBI

```
SITUATION → BEHAVIOR → IMPACT

SITUATION:
Конкретный контекст (когда, где, при каких обстоятельствах)
"На вчерашнем code review..."

BEHAVIOR:
Наблюдаемое действие (не интерпретация, не мотив)
"...ты отклонил PR без комментариев..."

IMPACT:
Результат этого поведения
"...это демотивировало junior разработчика
и замедлило релиз."

FULL EXAMPLE:
"На вчерашнем code review (S) ты отклонил PR
без объяснения почему (B). Это демотивировало
автора и команда не поняла, какие стандарты
ожидаются (I)."
```

### Performance Rating Framework

```
TYPICAL 5-LEVEL SCALE:

┌────────────────────────────────────────────────────────────┐
│ 5 │ EXCEPTIONAL    │ Significantly exceeds expectations  │
│   │                │ Top 5-10%. Role model.              │
├───┼────────────────┼─────────────────────────────────────┤
│ 4 │ EXCEEDS        │ Consistently exceeds expectations   │
│   │                │ Top 20-30%. High performer.         │
├───┼────────────────┼─────────────────────────────────────┤
│ 3 │ MEETS          │ Fully meets expectations            │
│   │                │ Solid contributor. Target level.    │
├───┼────────────────┼─────────────────────────────────────┤
│ 2 │ DEVELOPING     │ Partially meets expectations        │
│   │                │ New to role or needs improvement.   │
├───┼────────────────┼─────────────────────────────────────┤
│ 1 │ DOES NOT MEET  │ Below expectations                  │
│   │                │ PIP candidate. Urgent action.       │
└───┴────────────────┴─────────────────────────────────────┘

DISTRIBUTION GUIDELINE (not forced):
5: ~5%   4: ~20%   3: ~60%   2: ~10%   1: ~5%
```

### Goal Setting: SMART → OKRs

```
SMART GOALS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S - Specific (конкретная)
M - Measurable (измеримая)
A - Achievable (достижимая)
R - Relevant (релевантная)
T - Time-bound (с дедлайном)

Example: "Reduce page load time from 3s to 1.5s
by Q2 through implementing lazy loading."

OKR FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Qualitative goal (ambitious, inspiring)
Key Results: Quantitative metrics (3-5 per objective)

Example:
Objective: Become the most reliable service in platform

Key Results:
KR1: Reduce P99 latency from 500ms to 200ms
KR2: Achieve 99.9% uptime (from 99.5%)
KR3: Zero critical incidents in Q2
```

---

## Пошаговый процесс

### Давать регулярный feedback

**Шаг 1: Observe**
```
КАЖДЫЙ ДЕНЬ замечай:
□ Wins (даже маленькие)
□ Teachable moments
□ Patterns (positive и negative)
□ Peer feedback
```

**Шаг 2: Document (private notes)**
```
DATE: 2026-01-15
WHO: Alice
OBSERVATION: Led debugging session, kept team
focused, found root cause in 30 min
IMPACT: Saved 2 days of investigation
TO DO: Recognize in team meeting + 1-on-1
```

**Шаг 3: Deliver (timely)**
```
TIMING RULES:
• Positive: в течение 24 часов
• Constructive: в течение 48 часов
• Critical: сразу (private)

FORMAT:
• Positive: можно public
• Constructive: always private (1-on-1)
```

### Проводить performance review

**Шаг 1: Подготовка (2-3 недели до)**
```
□ Собрать все notes за период
□ Peer feedback (360 если есть)
□ Self-assessment от сотрудника
□ Review goals и deliverables
□ Draft written review
```

**Шаг 2: Calibration (если есть)**
```
С другими менеджерами:
• Обсудить "borderline" cases
• Убедиться в consistency
• Challenge assumptions
• Document rationale
```

**Шаг 3: Review meeting**
```
СТРУКТУРА (60-90 min):

[5 min] Set context
"Цель — обсудить твою performance и growth"

[10 min] Self-assessment
"Начни с твоей оценки этого периода"

[20 min] Feedback delivery
Strengths → Areas for growth → Rating

[15 min] Discussion
"Как это резонирует? Что surprises?"

[15 min] Goals for next period
Collaborative goal setting

[5 min] Wrap up
Compensation mention (if applicable)
Clear next steps
```

**Шаг 4: Follow-up**
```
□ Отправить written summary
□ Schedule follow-up 1-on-1
□ Create development plan
□ Track progress
```

### Managing underperformance

```
СТАДИЯ 1: Early Warning (informal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Обсуждение в 1-on-1
• Clear expectations
• Documented в личных notes
• Timeline: 2-4 недели

"Я заметил [pattern]. Это не соответствует
ожиданиям [level]. Давай обсудим, как
исправить."

СТАДИЯ 2: Formal Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Явный разговор о gap
• Written follow-up
• Конкретные milestones
• Check-in каждую неделю
• Timeline: 4-6 недель

"Мы обсуждали [issue] несколько раз.
Прогресс недостаточный. Это серьёзно.
Вот что нужно изменить..."

СТАДИЯ 3: PIP (Performance Improvement Plan)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Formal HR document
• Specific expectations
• Clear success criteria
• Weekly reviews
• Timeline: 30-60-90 дней
• Outcome: improve or exit

СТАДИЯ 4: Exit (если PIP не успешен)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Termination или mutual separation
• With HR involvement
• Respectful process
```

---

## Скрипты и Templates

### Positive Feedback Script

```
"Хотел отметить [specific action].

В ситуации [context] ты [specific behavior].
Это привело к [specific impact].

Это отличный пример [value/skill].
Спасибо!"

EXAMPLE:
"Хотел отметить как ты handled incident вчера.
Когда база упала, ты быстро собрал команду,
распределил tasks, и держал stakeholders
в курсе каждые 15 минут. Это сократило
downtime с типичных 4 часов до 45 минут
и customer complaints были минимальны.
Это образец incident response. Спасибо!"
```

### Constructive Feedback Script

```
"Можно обсудить одно наблюдение?

[SBI: Situation-Behavior-Impact]

Я вижу это как opportunity для growth.
Что думаешь? Как видишь ситуацию?"

[LISTEN]

"Спасибо за perspective. Как я могу
помочь с этим?"

EXAMPLE:
"Можно обсудить planning meeting вчера?

Ты перебивал других несколько раз когда
они предлагали идеи. Я заметил что после
этого Анна и Дима перестали участвовать.

Это создаёт риск: мы теряем хорошие идеи
и люди disengaged.

Как видишь ситуацию со своей стороны?"
```

### Performance Review Template

```markdown
# Performance Review: [Name]
Period: [Q1-Q2 2026]
Manager: [Name]
Review Date: [Date]

## 1. Role & Expectations Summary
[Brief description of role and level expectations]

## 2. Goal Achievement

| Goal | Weight | Achievement | Notes |
|------|--------|-------------|-------|
| [Goal 1] | 30% | Exceeds | [details] |
| [Goal 2] | 30% | Meets | [details] |
| [Goal 3] | 20% | Developing | [details] |
| [Goal 4] | 20% | Meets | [details] |

## 3. Competency Assessment

### Technical Skills
[Rating + evidence]

### Collaboration
[Rating + evidence]

### Communication
[Rating + evidence]

### Delivery
[Rating + evidence]

## 4. Key Strengths
1. [Strength + example]
2. [Strength + example]
3. [Strength + example]

## 5. Areas for Growth
1. [Area + specific feedback + suggestion]
2. [Area + specific feedback + suggestion]

## 6. Overall Rating
[Rating] — [Brief justification]

## 7. Next Period Goals
1. [Goal 1 — SMART format]
2. [Goal 2 — SMART format]
3. [Development goal]

## 8. Development Plan
[Specific actions for growth: training, projects, mentorship]

## 9. Employee Comments
[Space for employee response]

---
Employee Signature: _____________ Date: _______
Manager Signature: _____________ Date: _______
```

### PIP Template

```markdown
# Performance Improvement Plan

**Employee:** [Name]
**Manager:** [Name]
**Department:** [Engineering]
**Date:** [Date]
**Review Period:** 60 days

## 1. Current Performance Concerns

### Issue 1: [Title]
- **Observation:** [Specific examples with dates]
- **Impact:** [Business/team impact]
- **Expected Behavior:** [What success looks like]

### Issue 2: [Title]
- **Observation:** [Specific examples]
- **Impact:** [Business/team impact]
- **Expected Behavior:** [What success looks like]

## 2. Success Criteria
To successfully complete this PIP, [Name] must:

1. [ ] [Specific, measurable criterion]
2. [ ] [Specific, measurable criterion]
3. [ ] [Specific, measurable criterion]

## 3. Support Provided
- Weekly 1-on-1s with manager
- [Specific training/resources]
- [Mentorship if applicable]

## 4. Review Schedule
- **Week 2 Check-in:** [Date]
- **Week 4 Check-in:** [Date]
- **Week 6 Check-in:** [Date]
- **Final Review:** [Date]

## 5. Possible Outcomes
- **Successful:** Return to regular performance management
- **Partial:** Extension of PIP (rare)
- **Unsuccessful:** Employment termination

## 6. Acknowledgement
I have read and understand this plan.

Employee: _____________ Date: _______
Manager: _____________ Date: _______
HR: _____________ Date: _______
```

---

## Распространённые ошибки

### Ошибка 1: Recency Bias

**Как выглядит:**
Review основан на последних 2-4 неделях. Забыты achievements первой половины периода.

**Почему это проблема:**
- Unfair assessment
- Хорошая работа не признана
- Inconsistent signals

**Как исправить:**
```
ДОКУМЕНТИРУЙ CONTINUOUS:
□ Weekly notes после каждого 1-on-1
□ Monthly summary
□ "Brag doc" от самого сотрудника

При review: просмотри ВСЕ notes,
не только последние.
```

### Ошибка 2: Sandwich Feedback

**Как выглядит:**
"Ты делаешь хорошо X. Но Y — проблема. Зато Z отлично!"

**Почему это проблема:**
- Критика теряется
- Positive кажется неискренним
- Путает recipient

**Как исправить:**
```
ВМЕСТО СЭНДВИЧА:

Для позитивного: Дай отдельно, clearly
Для конструктивного: Дай отдельно, clearly

Не смешивай в одном разговоре.
If urgent: дай constructive clearly,
без cushioning.
```

### Ошибка 3: Избегать низких рейтингов

**Как выглядит:**
Все получают "Meets" или выше. Реальные проблемы не отражены.

**Почему это проблема:**
- Underperformers не знают о проблемах
- High performers frustrated (все "одинаковые")
- Legal риски при termination

**Как исправить:**
```
COURAGE:
"Это сложный разговор, но честность важнее
комфорта. Текущая performance — Developing.
Вот конкретно почему и как это исправить."

SUPPORT:
Низкий рейтинг + конкретный план улучшения
лучше чем фальшивый "Meets".
```

### Ошибка 4: No Follow-through

**Как выглядит:**
Review проведён. Документ подписан. Никаких follow-up actions.

**Почему это проблема:**
- Development не происходит
- Cynicism о процессе
- Goals forgotten

**Как исправить:**
```
AFTER REVIEW CHECKLIST:
□ Development actions в calendar
□ Goal milestones tracked
□ Monthly progress check-in
□ Quarterly goal review
□ Pre-work для следующего review
```

---

## Когда применять

### Continuous feedback подходит для:
- Всех, всегда
- Особенно: juniors, new hires, high-potentials
- После significant events (wins и misses)

### Formal review нужен когда:
- Компания требует (semi-annual/annual)
- Compensation decisions
- Promotion considerations
- Documentation для HR

### PIP необходим когда:
- Informal coaching не работает (6+ недель)
- Pattern of underperformance
- Serious issue (но не immediate termination)
- Legal documentation needed

### НЕ используй PIP когда:
- Первый performance issue
- Новый сотрудник (<6 месяцев)
- Issue из-за unclear expectations
- Уже решено terminate (PIP не должен быть формальностью)

---

## Кейсы

### Netflix: No Formal Reviews

**Контекст:** Netflix отказался от formal annual reviews.

**Подход:**
```
• Continuous 360 feedback
• "Keeper Test" (would I fight to keep?)
• Generous severance при exit
• High talent density
```

**Результат:** Высокая performance bar maintained через culture, не через процесс.

**Урок:** Formal process не единственный путь. Но требует сильную feedback culture.

### Google: OKRs + Performance

**Контекст:** Google использует OKRs для goals, отдельный process для performance.

**Ключевые insights:**
```
• OKRs на 60-70% achievement (ambitious)
• Performance = OKRs + HOW (behaviors)
• Calibration между managers critical
• Self-assessment required
```

**Урок:** Goals и performance rating — связаны, но не одно и то же.

### Adobe: Check-in Model

**Контекст:** Adobe отменил annual reviews в 2012.

**Новый подход:**
```
• Quarterly "check-ins"
• No ratings
• Focus на expectations + feedback + growth
• Manager discretion на compensation
```

**Результат:** Voluntary turnover снизился на 30%.

**Урок:** Можно убрать ratings, но нужна сильная feedback culture взамен.

---

## Связанные темы

### Prerequisites
- [[em-fundamentals]] — роль EM
- [[one-on-one-meetings]] — где даётся feedback

### Следующие шаги
- [[difficult-conversations]] — hard feedback
- [[hiring-engineers]] — performance criteria
- [[delegation]] — setting expectations

### Связи с другими разделами
- [[communication/giving-feedback]] — feedback techniques
- [[communication/difficult-conversations]] — PIPs, termination

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Radical Candor](https://www.radicalcandor.com/) | Book | Feedback philosophy |
| 2 | [Netflix Culture Deck](https://jobs.netflix.com/culture) | Document | No formal reviews |
| 3 | [Google re:Work: Performance](https://rework.withgoogle.com/guides/set-goals-with-okrs/steps/introduction/) | Guide | OKRs + calibration |
| 4 | [Adobe Check-in](https://www.adobe.com/check-in.html) | Case Study | Dropping annual reviews |
| 5 | [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) | Book | Performance conversations |
| 6 | [Gallup State of the American Manager](https://www.gallup.com/services/182138/state-american-manager.aspx) | Research | Feedback frequency stats |

### Дополнительное чтение

- "Thanks for the Feedback" by Stone & Heen — receiving feedback
- "Crucial Conversations" — difficult performance talks
- "Nine Lies About Work" by Buckingham — critique of ratings

---

*Последнее обновление: 2026-01-18*
*Связано с: [[00-leadership-overview]]*
