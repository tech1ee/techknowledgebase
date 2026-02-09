---
title: "Как нанимать инженеров: Полный гайд"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, tech-lead, hr]
teaches:
  - hiring philosophy
  - evaluation criteria
  - common mistakes
sources: [who-book, google-hiring, joel-spolsky, hiring-engineers]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[interview-process-design]]"
  - "[[sourcing-candidates]]"
  - "[[making-offers]]"
---

# Как нанимать инженеров: Полный гайд

> **TL;DR:** Hiring — самое важное решение, которое принимает менеджер. Плохой найм стоит 1.5-2x годовой зарплаты и демотивирует команду. Хороший найм — multiplier. Ключ: чёткие criteria ДО интервью, structured процесс, hire for trajectory не только current skills.

---

## Зачем это нужно?

### Типичная ситуация

Срочно нужен инженер. Процесс хаотичный — каждый interviewer спрашивает своё. Hire кандидата потому что "показался нормальным". Через 6 месяцев — не fit. Увольнение, обратно в search. Команда деморализована.

**Без системного подхода:**
- 50%+ hires не работают
- Время потрачено зря
- Team morale падает
- Technical debt от плохих решений

**С правильным процессом:**
- 80%+ successful hires
- Faster time-to-productivity
- A-players привлекают A-players
- Сильная engineering culture

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Стоимость плохого найма | 1.5-2x годовой зарплаты | SHRM |
| Время на замену | 3-6 месяцев | LinkedIn |
| Bad hires в первый год | 46% | Leadership IQ |
| Hires по referrals vs random | 5x better retention | ERE |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **EM/Director** | Critical | Hiring — core responsibility |
| **Tech Lead** | High | Участие в technical interviews |
| **HR/Recruiter** | Critical | Partnership с engineering |
| **Founder/CTO** | Critical | First 10 hires особенно важны |
| **IC** | Medium | Понять процесс для участия |

---

## Терминология

| Термин | Определение | Примечание |
|--------|-------------|------------|
| **Pipeline** | Поток кандидатов | От sourcing до offer |
| **Funnel** | Конверсия на каждом этапе | Top → Hire |
| **Bar** | Уровень требований | "Raise the bar" = hire выше average |
| **Culture Fit** | Совместимость с культурой | ≠ "похож на нас" |
| **Trajectory** | Потенциал роста | Важнее текущих skills |
| **Signal** | Индикатор качества | Vs noise |

### Типы hire

```
BACKFILL:
Замена ушедшего. Timeline: urgent.
Risk: поспешный найм.

GROWTH HIRE:
Новая позиция для роста команды.
Risk: unclear role definition.

UPGRADE HIRE:
Замена underperformer на stronger hire.
Risk: team dynamics.

OPPORTUNISTIC:
Отличный кандидат без открытой позиции.
Risk: unclear role, создать место для человека.
```

---

## Как это работает?

### Hiring Funnel

```
┌─────────────────────────────────────────────────────────────────┐
│                      HIRING FUNNEL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SOURCING                     Кол-во    Конверсия               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Referrals                      │         │                     │
│  Inbound applications           │  100    │  →  50% respond     │
│  Outbound (recruiters)          │         │                     │
│                                 ▼         │                     │
│  INITIAL SCREEN                 │         │                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Resume review                  │   50    │  →  50% pass        │
│  Phone/video screen             │         │                     │
│                                 ▼         │                     │
│  TECHNICAL ASSESSMENT           │         │                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Take-home / coding test        │   25    │  →  50% pass        │
│  Technical interview            │         │                     │
│                                 ▼         │                     │
│  ONSITE / FINAL ROUNDS          │         │                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  System design                  │   12    │  →  50% pass        │
│  Coding                         │         │                     │
│  Culture/values                 │         │                     │
│  Team match                     │         │                     │
│                                 ▼         │                     │
│  DECISION                       │         │                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Debrief                        │    6    │  →  50% accept      │
│  Offer                          │         │                     │
│                                 ▼         │                     │
│  ┌─────────────────────────────────────┐                        │
│  │              HIRE: 3                │                        │
│  └─────────────────────────────────────┘                        │
│                                                                 │
│  TYPICAL CONVERSION: 100 → 3 (3%)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Hiring Philosophy: "Who" Method

```
ЧЕТЫРЕ ВОПРОСА (от книги "Who"):

1. WHAT: Что нужно от роли?
   → Scorecard с outcomes, не activities

2. SOURCE: Откуда брать кандидатов?
   → Referrals > inbound > outbound

3. SELECT: Как оценивать?
   → Structured interviews с criteria

4. SELL: Как закрыть?
   → Sell throughout, не только на offer stage
```

### Scorecard Template

```
ROLE: Senior Backend Engineer
TEAM: Payments
HIRING MANAGER: [Name]

MISSION:
Build and maintain payment processing
infrastructure handling $XM daily.

OUTCOMES (что должен достичь за 12 месяцев):
1. Ship payment gateway v2 (Q1-Q2)
2. Reduce payment failures from 2% to 0.5%
3. Mentor 2 junior engineers
4. On-call rotation ownership

COMPETENCIES (что нужно для success):
Technical:
□ Distributed systems (5+ yrs)
□ Payment domain knowledge
□ Security best practices
□ Performance optimization

Behavioral:
□ Ownership mentality
□ Clear communication
□ Collaborative approach
□ Learning agility

CULTURE FIT:
□ Direct communication
□ Data-driven decisions
□ Customer focus
```

---

## Критерии оценки

### Technical Assessment

```
CODING SKILLS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Problem solving approach
• Code quality и readability
• Edge cases handling
• Testing mindset
• Communication while coding

Rating: 1-5 where 3 = meets bar

SYSTEM DESIGN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Requirements clarification
• High-level architecture
• Trade-off analysis
• Scalability considerations
• Real-world constraints

DOMAIN EXPERTISE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Depth in relevant area
• Breadth awareness
• Current с industry trends
• Hands-on experience
```

### Behavioral Assessment

```
PAST BEHAVIOR → FUTURE PERFORMANCE

STAR METHOD для оценки:
S - Situation (контекст)
T - Task (задача)
A - Action (что сделал)
R - Result (результат)

ВОПРОСЫ:
"Расскажи о проекте, где был технический risk.
Как справился? Каков результат?"

ОЦЕНИВАЙ:
• Ownership (я vs мы vs они)
• Problem-solving approach
• Learning from failures
• Collaboration style
• Communication clarity
```

### Culture/Values Assessment

```
НЕ "CULTURE FIT" (похож на нас)
А "CULTURE ADD" (усилит культуру)

SIGNALS:
✓ Aligned с company values
✓ Diverse perspective
✓ Constructive challenges
✓ Growth mindset
✓ Intellectual curiosity

RED FLAGS:
✗ Blame others for failures
✗ "That's not my job"
✗ Dismissive of others' ideas
✗ Only interested in title/money
✗ Badmouths previous employers
```

### The "Airport Test" (осторожно)

```
OLD VERSION (problematic):
"Would I want to be stuck in airport with them?"
→ Leads to hiring "like us" bias

BETTER VERSION:
"Will they make the team stronger?"
→ Focus on contribution, не likability

"Can they teach us something?"
→ Value diverse skills и perspectives
```

---

## Пошаговый процесс

### Pre-Hiring

**Шаг 1: Define the Role**
```
□ Clear mission statement
□ 3-5 key outcomes for first year
□ Must-have vs nice-to-have skills
□ Level and compensation range
□ Team context and challenges

AVOID:
✗ Copy-paste job descriptions
✗ Unrealistic requirements ("10 years React")
✗ Vague responsibilities
```

**Шаг 2: Align Interview Team**
```
□ Assign interviewers to focus areas
□ Training on bias и evaluation
□ Calibrate on scoring
□ Define decision-making process

INTERVIEW PANEL:
• Technical coding: [Name]
• System design: [Name]
• Behavioral/values: [Name]
• Team fit: [Name]
• Hiring manager: [Name]
```

### During Hiring

**Шаг 3: Source Candidates**
```
PRIORITY ORDER:
1. Referrals (best ROI)
2. Internal mobility
3. Inbound applications
4. Passive outreach (recruiters)

FOR REFERRALS:
"Who's the best engineer you worked with
who might be looking?"

See [[sourcing-candidates]] для details.
```

**Шаг 4: Screen**
```
RESUME REVIEW (2-3 min max):
□ Relevant experience?
□ Trajectory (growth pattern)?
□ Red flags?

PHONE SCREEN (30 min):
□ Background и motivation
□ Basic technical questions
□ Role fit
□ Logistics (timeline, salary expectations)
```

**Шаг 5: Interview**
```
СТРУКТУРИРОВАННОЕ ИНТЕРВЬЮ:
• Same questions for all candidates
• Defined evaluation criteria
• Independent scoring before debrief
• Documented feedback

See [[interview-process-design]] для details.
```

### Post-Interview

**Шаг 6: Debrief**
```
STRUCTURE:
1. Each interviewer shares independently (no influence)
2. Scoring on pre-defined criteria
3. Discussion of concerns
4. Hire/No Hire decision

RULES:
• No hiring by consensus (weak signal)
• Strong "no" = no hire (veto power)
• Document rationale
```

**Шаг 7: Decide**
```
HIRE IF:
✓ Meets bar on all critical criteria
✓ At least one "strong yes"
✓ No "strong no"
✓ Would raise team average

DON'T HIRE IF:
✗ "Good enough" mentality
✗ Filling headcount pressure
✗ One interviewer enthusiastic, others meh
```

**Шаг 8: Offer**
```
□ Competitive compensation
□ Sell the opportunity (not just money)
□ Address concerns
□ Deadline (reasonable)

See [[making-offers]] для details.
```

---

## Скрипты и Templates

### Referral Request

```
"Привет [Name],

Ищу [role] в команду. Ты работал с отличными
людьми в [company].

Кто лучший [engineer/designer/etc.] с кем
работал, кто мог бы быть открыт к разговору?

Буду благодарен за intro. Happy to return
the favor."
```

### Phone Screen Questions

```
INTRO (5 min):
"Расскажи о своём background и что привело
к интересу в этой роли?"

TECHNICAL (15 min):
"Опиши самый сложный технический проект.
Какие challenges? Как решил?"

"Какой tech stack предпочитаешь и почему?"

ROLE FIT (5 min):
"Что ищешь в следующей роли?"
"Какие вопросы о нас?"

LOGISTICS (5 min):
"Timeline? Salary expectations?
Other processes?"
```

### Interview Feedback Template

```markdown
## Interview Feedback: [Candidate Name]
Interviewer: [Name]
Date: [Date]
Round: [Type — coding/design/behavioral]

### Summary
[2-3 sentences: overall impression]

### Scoring
| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| [Criteria 1] | X | [Evidence] |
| [Criteria 2] | X | [Evidence] |
| [Criteria 3] | X | [Evidence] |

### Strengths
- [Specific strength + evidence]
- [Specific strength + evidence]

### Concerns
- [Specific concern + evidence]
- [Specific concern + evidence]

### Questions to Explore (for other interviewers)
- [Question]

### Recommendation
[ ] Strong Hire
[ ] Hire
[ ] No Hire
[ ] Strong No Hire

### Rationale
[1-2 sentences explaining recommendation]
```

### Rejection Email (Kind)

```
Subject: Update on your application to [Company]

Hi [Name],

Thank you for taking the time to interview
with us for the [Role] position.

After careful consideration, we've decided
not to move forward with your application
at this time. This was a difficult decision
as we had many strong candidates.

[Optional: specific, constructive feedback
if you can provide it]

We encourage you to apply again in the future
as our needs evolve.

Best of luck in your search.

[Name]
```

---

## Распространённые ошибки

### Ошибка 1: Hire for Skills, Not Trajectory

**Как выглядит:**
Hire кандидата с exact match skills. Через год — они не выросли, stuck на том же уровне.

**Почему это проблема:**
- Technology меняется
- Growth mindset важнее текущих skills
- Culture стагнирует

**Как исправить:**
```
ВМЕСТО: "5 years of React"
ОЦЕНИВАЙ: "Learning velocity"

Questions:
"Что изучил за последний год?"
"Как подходишь к новой технологии?"
"Расскажи о mistake и что learned"
```

### Ошибка 2: "Gut Feel" Decisions

**Как выглядит:**
"Мне показалось что хороший человек." Нет структуры, нет criteria.

**Почему это проблема:**
- Bias dominates
- Inconsistent decisions
- Can't improve process

**Как исправить:**
```
STRUCTURED PROCESS:
□ Pre-defined criteria (scorecard)
□ Same questions for all
□ Independent scoring
□ Evidence-based discussion

"What specific evidence supports this?"
```

### Ошибка 3: Lowering the Bar

**Как выглядит:**
Позиция открыта 3 месяца. Pressure от бизнеса. Hire "good enough" candidate.

**Почему это проблема:**
- A players leave when B players join
- Качество падает
- Ещё сложнее нанять потом

**Как исправить:**
```
"RAISE THE BAR" principle:
Каждый hire должен поднимать средний
уровень команды.

Лучше: продолжать искать
Чем: нанять mediocre
```

### Ошибка 4: Solo Decisions

**Как выглядит:**
Hiring manager принимает решение один. Команда узнаёт о new hire.

**Почему это проблема:**
- Один человек biased
- Team не bought in
- Miss signals others would catch

**Как исправить:**
```
PANEL DECISION:
• Multiple interviewers
• Independent feedback
• Collaborative debrief
• But hiring manager = final decision
```

### Ошибка 5: Overselling

**Как выглядит:**
Рассказать только хорошее. Скрыть проблемы. Candidate joins, разочарован.

**Почему это проблема:**
- Trust broken
- Early turnover
- Reputation damage

**Как исправить:**
```
REALISTIC JOB PREVIEW:
"Here's what's great: [positives]
Here's what's challenging: [honest]
Is this exciting to you?"

Honest = attract right people
```

---

## Когда применять разные подходы

### Heavy Process (большие компании)

```
КОГДА:
• 50+ engineers
• Compliance requirements
• Multiple teams hiring
• Need consistency

ВКЛЮЧАЕТ:
• Standardized interviews
• Calibration sessions
• Interview training
• Detailed scorecards
```

### Light Process (стартапы)

```
КОГДА:
• <15 engineers
• Speed critical
• Founders involved
• Flexible roles

ВКЛЮЧАЕТ:
• Core criteria defined
• Fewer interview rounds
• Faster decisions
• More gut (but tracked)
```

---

## Кейсы

### Google: Structured Hiring

**Подход:**
- 4 interviews max
- qDroid tool для questions
- Hiring committees (не managers)
- Data-driven decisions

**Результат:**
Quality predictors identified:
1. Work samples
2. Cognitive ability tests
3. Structured interviews

**Урок:** Structure beats intuition.

### Netflix: Culture First

**Подход:**
- Heavy emphasis на culture fit
- "Keeper test" applies to hiring
- High talent density priority
- Generous severance = high bar ok

**Урок:** Culture filter можно сделать explicit.

### Stripe: References-Heavy

**Подход:**
- Deep reference checks
- Call 5-10 references
- Specific questions about work style
- Red flags are disqualifying

**Урок:** Past behavior predicts future. References = rich signal.

---

## Anti-Patterns to Avoid

```
❌ "BRILLIANT JERK" HIRE
Exceptional skill + toxic behavior
→ Destroys team faster than adds value

❌ "CLONE HIRE"
Only hire people like existing team
→ No diversity of thought

❌ "RESUME HIRE"
Great credentials, poor interview
→ Past company ≠ individual contribution

❌ "DESPERATION HIRE"
"We need someone now!"
→ Bad hire costs more than empty seat

❌ "POTENTIAL WITHOUT EVIDENCE"
"They could be great"
→ Need demonstrated ability
```

---

## Связанные темы

### Prerequisites
- [[em-fundamentals]] — role of EM in hiring

### Следующие шаги
- [[interview-process-design]] — design interviews
- [[sourcing-candidates]] — where to find people
- [[making-offers]] — close candidates

### Связи с другими разделами
- [[career/interview/]] — candidate perspective
- [[team-building/onboarding]] — after hire

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Who: The A Method](https://www.amazon.com/Who-Method-Hiring-Geoff-Smart/dp/0345504194) | Book | Scorecard, process |
| 2 | [Google's Hiring Research](https://rework.withgoogle.com/subjects/hiring/) | Research | Structured interviews |
| 3 | [Joel Spolsky: Guerrilla Guide](https://www.joelonsoftware.com/2006/10/25/the-guerrilla-guide-to-interviewing-version-30/) | Article | Smart and Gets Things Done |
| 4 | [First Round: Hiring](https://review.firstround.com/hiring) | Articles | Startup hiring practices |
| 5 | [SHRM: Cost of Bad Hire](https://www.shrm.org/) | Research | Statistics |
| 6 | [Patrick McKenzie: Salary Negotiation](https://www.kalzumeus.com/2012/01/23/salary-negotiation/) | Article | Candidate perspective |

### Дополнительное чтение

- "Work Rules!" by Laszlo Bock — Google hiring
- "The Talent Delusion" by Tomas Chamorro-Premuzic — science of hiring
- "Hiring Engineers" newsletter by The Pragmatic Engineer

---

*Последнее обновление: 2026-01-18*
*Связано с: [[leadership-overview]]*
