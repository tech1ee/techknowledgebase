---
title: "Engineering Manager: роль и обязанности"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
reading_time: 33
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
difficulty: intermediate
target-role: [senior, tech-lead, em]
teaches:
  - Обязанности Engineering Manager
  - Различия с Tech Lead
  - Ключевые навыки EM
sources: [managersPath, randsinrepose, leaddev, firstround]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[ic-vs-management]]"
  - "[[tech-lead-role]]"
  - "[[em-fundamentals]]"
  - "[[one-on-one-meetings]]"
  - "[[hiring-engineers]]"
prerequisites:
  - "[[ic-vs-management]]"
  - "[[em-fundamentals]]"
---

# Engineering Manager: роль и обязанности

> **TL;DR:** Engineering Manager (EM) — это people-focused leader. Главная ответственность: **развитие людей** и **delivery команды**. EM не обязательно лучший технический специалист — он лучший в том, чтобы сделать команду эффективной.
>
> **Ключевое отличие от Tech Lead:** EM владеет **людьми** (hiring, performance, career), Tech Lead владеет **технологией** (architecture, quality). Часто работают в паре.
>
> **Главная ошибка новых EM:** Продолжать делать technical work вместо people work. EM — это career change, не promotion.

---

## Зачем понимать эту роль?

### Типичная ситуация

Ты Senior Engineer или Tech Lead. Компания растёт, и CEO/Director говорит: "Нам нужен Engineering Manager для команды. Хочешь попробовать?"

**Без понимания роли:**
- Думаешь, что будешь кодировать + немного management
- Удивляешься количеству meetings и 1-on-1
- Не понимаешь, как измеряется твой success
- Через год: burnout или возврат на IC

**С пониманием:**
- Осознанный переход с clear expectations
- Знаешь, что coding будет 0-20%
- Понимаешь, что impact через людей, не код
- Можешь оценить, подходит ли тебе роль

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Время EM на meetings | 60-80% | Industry average |
| Время EM на coding | 0-20% | Pragmatic Engineer |
| Новых EM failing в 2 года | 60% | Harvard Business |
| Optimal span of control | 5-9 direct reports | Management research |
| EM → Director timeline | 3-5 лет | Industry average |

---

## Определение роли

### Engineering Manager — это...

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENGINEERING MANAGER: CORE RESPONSIBILITIES            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌────────────────────┐                               │
│                    │ ENGINEERING MANAGER │                               │
│                    └─────────┬──────────┘                               │
│                              │                                          │
│       ┌──────────────────────┼──────────────────────┐                  │
│       │                      │                      │                  │
│       ▼                      ▼                      ▼                  │
│  ┌─────────┐           ┌─────────┐           ┌─────────┐              │
│  │ PEOPLE  │           │ DELIVERY│           │ PROCESS │              │
│  └─────────┘           └─────────┘           └─────────┘              │
│                                                                          │
│  • Hiring               • Sprint planning      • Agile/Scrum           │
│  • 1-on-1s              • Roadmap execution    • Team rituals          │
│  • Performance          • Dependencies         • Communication         │
│  • Career growth        • Risk management      • Cross-team coord      │
│  • Team health          • Stakeholders         • Continuous impr       │
│  • Retention                                                            │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════   │
│  PRIMARY METRIC: Team delivers value while people grow and are happy   │
│  ═══════════════════════════════════════════════════════════════════   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Что EM делает (breakdown)

| Категория | % времени | Ключевые активности |
|-----------|-----------|---------------------|
| **People** | 40-50% | 1-on-1s, hiring, performance, coaching |
| **Delivery** | 25-30% | Planning, unblocking, stakeholders |
| **Process** | 15-20% | Meetings, rituals, improvement |
| **Technical** | 0-20% | Code review, architecture input |

---

## Обязанности EM

### 1. People Management (40-50%)

#### 1-on-1 Meetings

```
ЧАСТОТА: Еженедельно с каждым direct report (30-60 мин)

ЦЕЛИ:
□ Build trust and relationship
□ Understand blockers and concerns
□ Provide feedback (positive and constructive)
□ Discuss career growth
□ Catch problems early

СТРУКТУРА:
1. Их agenda (что у них на уме)
2. Твоя agenda (feedback, updates)
3. Career/growth discussion
4. Action items
```

#### Hiring

```
EM OWNERSHIP:
□ Define hiring needs и requirements
□ Write job descriptions
□ Screen resumes
□ Conduct interviews (cultural fit, experience)
□ Make hiring decisions
□ Negotiate offers
□ Onboard new hires

COLLABORATE WITH:
- Recruiters: sourcing, scheduling
- Tech Lead: technical evaluation
- HR: compensation, legal
```

#### Performance Management

```
ONGOING:
□ Continuous feedback (не ждать review)
□ Track achievements и concerns
□ Document examples
□ Calibration с peers

FORMAL REVIEWS (quarterly/bi-annually):
□ Write performance reviews
□ Deliver feedback effectively
□ Create development plans
□ Handle underperformance (PIP)

COMPENSATION:
□ Salary adjustments
□ Promotion recommendations
□ Bonus recommendations
```

#### Career Development

```
FOR EACH DIRECT REPORT:
□ Understand career goals
□ Create development plan
□ Provide stretch opportunities
□ Connect with mentors
□ Advocate for promotions
□ Give honest feedback on gaps
```

### 2. Delivery Management (25-30%)

#### Sprint/Project Planning

```
EM ROLE:
□ Ensure team has clear priorities
□ Manage capacity (vacation, on-call, etc)
□ Remove blockers proactively
□ Manage dependencies with other teams
□ Communicate status to stakeholders
□ Escalate risks early

NOT EM ROLE (usually):
- Technical estimation (Tech Lead)
- Architecture decisions (Tech Lead)
- Individual task assignment (team self-organize)
```

#### Stakeholder Management

```
EM COMMUNICATES WITH:
□ Product Manager: priorities, tradeoffs
□ Director/VP: team status, needs
□ Other EMs: dependencies, coordination
□ Executives: summaries, escalations

KEY SKILLS:
- Translate tech to business language
- Set expectations realistically
- Say "no" constructively
- Escalate appropriately
```

### 3. Process & Operations (15-20%)

#### Team Rituals

```
EM FACILITATES OR DELEGATES:
□ Standups (often delegate to team)
□ Sprint planning
□ Retrospectives
□ Team meetings
□ All-hands presentations

EM OPTIMIZES:
□ Meeting effectiveness
□ Communication channels
□ Documentation practices
□ On-call processes
```

#### Continuous Improvement

```
□ Run retrospectives
□ Implement improvements
□ Track team metrics
□ Gather feedback
□ Experiment with processes
```

### 4. Technical Involvement (0-20%)

```
EM MAY DO:
□ Code review (selective)
□ Architecture discussions (input, not decision)
□ Technical interviews
□ Maintain technical currency

EM SHOULD NOT DO:
□ Be on critical path for delivery
□ Own architecture decisions
□ Write production code regularly
□ Be the "best coder" on team
```

---

## EM vs другие роли

### EM vs Tech Lead

| Аспект | Engineering Manager | Tech Lead |
|--------|---------------------|-----------|
| **Primary focus** | People | Technology |
| **Direct reports** | Yes (5-9) | No (usually) |
| **1-on-1s** | Performance-focused | Mentoring-focused |
| **Hiring** | Full ownership | Technical evaluation |
| **Career growth** | Primary owner | Technical guidance |
| **Coding** | 0-20% | 30-50% |
| **Performance reviews** | Writes them | Provides input |
| **Architecture** | Input | Ownership |

### EM vs Product Manager

| Аспект | Engineering Manager | Product Manager |
|--------|---------------------|-----------------|
| **Focus** | How to build, team health | What to build, why |
| **Owns** | Engineering team | Product roadmap |
| **Success metric** | Team delivery + health | Product outcomes |
| **Stakeholders** | Engineers, Director | Customers, executives |
| **Technical depth** | Usually deep | Varies widely |

### EM Partnership Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EM + TECH LEAD + PM PARTNERSHIP                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│              Product Manager                                             │
│              ┌─────────────┐                                            │
│              │   WHAT      │                                            │
│              │ to build    │                                            │
│              └──────┬──────┘                                            │
│                     │                                                   │
│         ┌──────────┴──────────┐                                        │
│         │                     │                                        │
│         ▼                     ▼                                        │
│  ┌─────────────┐       ┌─────────────┐                                 │
│  │    HOW      │       │    WHO      │                                 │
│  │ to build    │       │  builds it  │                                 │
│  │  (Tech Lead)│       │    (EM)     │                                 │
│  └─────────────┘       └─────────────┘                                 │
│                                                                          │
│  PM: Product vision, priorities, customer needs                        │
│  Tech Lead: Architecture, technical quality, technical mentoring       │
│  EM: Team health, hiring, career growth, delivery                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## День типичного EM

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL DAY: ENGINEERING MANAGER                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  08:00  Email/Slack triage: что urgent?                                 │
│                                                                          │
│  08:30  1-on-1 with Senior Engineer (weekly)                           │
│         → Career discussion, upcoming promotion                         │
│                                                                          │
│  09:00  1-on-1 with Mid Engineer (weekly)                              │
│         → Blocker on project, need pairing                             │
│                                                                          │
│  09:30  Stand-up (observe, don't run)                                  │
│         → Note: Alice seems frustrated, follow up                      │
│                                                                          │
│  10:00  Interview: phone screen for open role                          │
│                                                                          │
│  10:45  Follow up with Alice (quick check-in)                          │
│                                                                          │
│  11:00  Staff meeting with Director                                    │
│         → Quarterly planning, headcount discussion                     │
│                                                                          │
│  12:00  Lunch (try to actually take it)                                │
│                                                                          │
│  13:00  Sprint planning (facilitate)                                   │
│                                                                          │
│  14:00  Cross-team sync (dependency management)                        │
│                                                                          │
│  14:30  Performance review writing                                     │
│                                                                          │
│  15:30  1-on-1 with Junior Engineer                                    │
│         → Onboarding check-in, first month                             │
│                                                                          │
│  16:00  Quick code review (stay somewhat technical)                    │
│                                                                          │
│  16:30  Prep for tomorrow's interviews                                 │
│                                                                          │
│  17:00  End of day: review action items                                │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  1-on-1s: 2.5 hours (25%)                                              │
│  Meetings: 3.5 hours (35%)                                             │
│  Admin/Prep: 2 hours (20%)                                             │
│  Interviews: 1 hour (10%)                                              │
│  Technical: 1 hour (10%)                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Ключевые навыки EM

### People Skills

| Навык | Почему критичен | Как развивать |
|-------|-----------------|---------------|
| **Активное слушание** | Понимать что реально беспокоит | Practice в 1-on-1, [[active-listening]] |
| **Feedback delivery** | Помогать людям расти | [[giving-feedback]], practice |
| **Difficult conversations** | PIP, conflicts, layoffs | [[difficult-conversations]], training |
| **Empathy** | Build trust | Conscious practice, ask questions |
| **Coaching** | Develop others | Learn coaching frameworks |

### Delivery Skills

| Навык | Почему критичен | Как развивать |
|-------|-----------------|---------------|
| **Prioritization** | Focus on what matters | Frameworks (ICE, RICE) |
| **Risk management** | Catch problems early | Experience, patterns |
| **Stakeholder mgmt** | Alignment and support | Practice, feedback |
| **Communication** | Clear status, expectations | Write more, get feedback |
| **Delegation** | Scale yourself | Start small, trust |

### Leadership Skills

| Навык | Почему критичен | Как развивать |
|-------|-----------------|---------------|
| **Influence w/o authority** | Change without power | Build relationships, show value |
| **Decision making** | Move team forward | Frameworks, practice |
| **Conflict resolution** | Healthy team | [[conflict-resolution]], practice |
| **Strategic thinking** | Long-term success | Read, learn from seniors |

---

## Span of Control

### Optimal Team Size

```
RESEARCH-BASED GUIDELINES:

New EM: 3-5 direct reports
  → Learn the role with manageable load

Experienced EM: 5-9 direct reports
  → Optimal for most organizations

Maximum: 10-12 direct reports
  → Only with very senior team, stable environment
  → Quality of 1-on-1s suffers beyond this

FACTORS THAT REDUCE CAPACITY:
- Junior engineers (need more support)
- Complex projects (more coordination)
- Hiring (interviews take time)
- Cross-team dependencies
- EM also doing technical work
```

### When to Split Teams

```
SIGNS IT'S TIME:
□ 1-on-1s are being skipped or rushed
□ Can't give adequate feedback
□ Don't know what each person is working on
□ Performance issues not being addressed
□ Team has >10 people

OPTIONS:
1. Promote Tech Lead to EM, split team
2. Hire external EM
3. Create sub-teams with Tech Leads
```

---

## EM Success Metrics

### How to Know You're Doing Well

```
LAGGING INDICATORS (результат):
□ Team ships on time with quality
□ Low attrition (people stay)
□ High engagement scores
□ Promotions happening
□ Good hiring (pipeline, quality)

LEADING INDICATORS (process):
□ Regular, quality 1-on-1s happening
□ Team knows priorities
□ Blockers resolved quickly
□ Feedback delivered regularly
□ Career conversations happening
```

### The Rands Test

From "Managing Humans" — 11 questions to assess EM health:

```
□ Do you have a 1:1 with your direct reports weekly?
□ Do you have a team meeting every week?
□ Do you have status reports?
□ Can you say "no" to your boss?
□ Can you explain strategy of your company?
□ Can you explain current priorities of your team?
□ Do you have time to think?
□ Are you comfortable with your compensation?
□ Is there a path for your career development?
□ Do you believe in what you're building?
□ Are you growing?

8+/11 = Healthy situation
5-7/11 = Areas to address
<5/11 = Consider changes
```

---

## Распространённые ошибки

### Ошибка 1: Продолжать кодировать как раньше

**Как выглядит:**
EM тратит 50%+ на coding, 1-on-1s отменяются.

**Почему проблема:**
- People work не делается
- Team не получает support
- EM — bottleneck на delivery
- Burnout (две работы одновременно)

**Как исправить:**
```
RULE: Coding должен быть 0-20%, не больше.

Если хочешь кодировать больше:
→ IC track лучше для тебя
→ Tech Lead роль лучше для тебя
```

### Ошибка 2: Быть "другом", не менеджером

**Как выглядит:**
EM избегает difficult feedback, все "great job!"

**Почему проблема:**
- Люди не растут
- Performance issues не решаются
- Credibility теряется
- Team качество падает

**Как исправить:**
```
[[radical-candor]]: Care personally AND challenge directly

Feedback должен быть:
- Specific (конкретные примеры)
- Timely (близко к событию)
- Actionable (что изменить)
- Caring (from place of wanting them to succeed)
```

### Ошибка 3: Микроменеджмент

**Как выглядит:**
EM проверяет каждую задачу, требует updates постоянно.

**Почему проблема:**
- Демотивирует senior людей
- Не масштабируется
- Команда не учится autonomy
- EM burnout

**Как исправить:**
```
DELEGATE:
- Set clear expectations
- Define success criteria
- Check in at milestones, not constantly
- Let people fail small (learning opportunity)
```

### Ошибка 4: Не защищать команду

**Как выглядит:**
EM соглашается на все requests сверху, команда перегружена.

**Почему проблема:**
- Burnout команды
- Quality drops
- Trust теряется
- Attrition grows

**Как исправить:**
```
EM ДОЛЖЕН:
□ Push back на unrealistic deadlines
□ Negotiate scope when needed
□ Shield team from politics
□ Escalate resource issues

SCRIPT:
"We can do X by deadline, or X+Y with 2 more weeks.
 Which is more important for the business?"
```

---

## Transition Path

### Путь к EM

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PATH TO ENGINEERING MANAGER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TYPICAL PATH:                                                           │
│                                                                          │
│  Senior Engineer (3-5 лет)                                              │
│       │                                                                 │
│       ▼                                                                 │
│  Tech Lead (1-2 года) ←──── Опционально, но полезно                    │
│       │                                                                 │
│       ▼                                                                 │
│  Engineering Manager                                                    │
│       │                                                                 │
│       ▼                                                                 │
│  Senior EM (2-3 года)                                                   │
│       │                                                                 │
│       ▼                                                                 │
│  Director of Engineering                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Как подготовиться

```
ДО ПЕРЕХОДА В EM:

□ Менторить junior/mid engineers
□ Вести 1-on-1 (даже informal)
□ Участвовать в hiring (интервью)
□ Давать feedback peers
□ Вести проекты (coordination)
□ Читать книги (Manager's Path, High Output Management)
□ Наблюдать за хорошими EM
```

---

## Книги для EM

| Книга | Автор | Когда читать |
|-------|-------|--------------|
| **The Manager's Path** | Camille Fournier | Первая книга |
| **High Output Management** | Andy Grove | Classic, must-read |
| **Radical Candor** | Kim Scott | Про feedback |
| **The Making of a Manager** | Julie Zhuo | First-time manager |
| **Managing Humans** | Michael Lopp | Practical advice |
| **An Elegant Puzzle** | Will Larson | Scaling teams |

---

## Связанные темы

### Prerequisites
- [[ic-vs-management]] — выбор трека
- [[tech-lead-role]] — часто предшествует EM

### Следующие шаги
- [[em-fundamentals]] — глубже в EM work
- [[one-on-one-meetings]] — главный инструмент
- [[hiring-engineers]] — критический навык

### Связи с другими разделами
- [[communication/giving-feedback]] — для 1-on-1 и performance
- [[communication/difficult-conversations]] — для PIP, conflicts

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | The Manager's Path (Camille Fournier) | Book | Role definition, progression |
| 2 | [Rands in Repose](https://randsinrepose.com) | Blog | Rands Test, practical advice |
| 3 | [What are signs of a great manager](https://rework.withgoogle.com) | Research | Google's management research |
| 4 | [First Round Review](https://review.firstround.com) | Articles | EM best practices |
| 5 | [LeadDev](https://leaddev.com) | Conference | Modern EM practices |

*Исследование проведено: 2026-01-18*

---

## Связь с другими темами

**[[ic-vs-management]]** — Решение о переходе в Engineering Manager — это фундаментальный карьерный выбор между IC и management треками. Понимание различий помогает осознанно принять решение, а не идти в management "потому что это следующий шаг". Многие успешные EM сначала тщательно оценили оба трека и поняли, что получают энергию от работы с людьми, а не от чистого coding.

**[[tech-lead-role]]** — Tech Lead и Engineering Manager часто работают в паре, формируя leadership duo команды. Tech Lead владеет технической стороной (архитектура, качество кода, технический менторинг), а EM — людьми и delivery. Чёткое понимание границ между ролями предотвращает конфликты и confusion в команде. Многие EM приходят из Tech Lead роли, и понимание обеих позиций делает их более эффективными.

**[[em-fundamentals]]** — Это следующий шаг после понимания роли EM: глубокое погружение в конкретные навыки и практики. Em-fundamentals покрывает тактические аспекты работы — как проводить 1-on-1, как давать feedback, как управлять performance. Если данная статья отвечает на вопрос "что такое EM", то em-fundamentals отвечает на "как быть хорошим EM".

**[[one-on-one-meetings]]** — 1-on-1 встречи — это главный инструмент Engineering Manager. Через регулярные 1-on-1 EM строит trust, понимает blockers, даёт feedback и обсуждает карьерный рост. Качество 1-on-1 напрямую коррелирует с эффективностью EM: плохие или нерегулярные 1-on-1 — первый признак struggling менеджера.

**[[hiring-engineers]]** — Найм — одна из самых важных обязанностей EM, потому что люди определяют всё. EM владеет полным циклом найма: от определения потребностей до onboarding нового члена команды. Ошибка в найме обходится в 6-12 месяцев потерянного времени, поэтому hiring skills критически важны для успеха EM.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Фундаментальная книга для любого Engineering Manager. Описывает полный карьерный путь от IC до CTO, с особенно детальными главами про переход в management, обязанности EM и типичные ошибки. Обязательна к прочтению перед или в первые месяцы роли EM.
- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — Помогает понять динамику команды и пять ключевых дисфункций, которые EM должен распознавать и адресовать: отсутствие доверия, страх конфликтов, недостаток приверженности, избегание ответственности и невнимание к результатам.
- **L. David Marquet, "Turn the Ship Around!" (2012)** — Модель leadership через intent-based leadership, где лидер создаёт среду для принятия решений на всех уровнях. Особенно полезна для EM, которые борются с микроменеджментом и хотят научиться эффективной делегации.

---

---

## Проверь себя

> [!question]- Почему EM, продолжающий кодировать 50%+ времени, вредит команде?
> People work не делается (1-on-1 отменяются, feedback не даётся), команда не получает support, EM становится bottleneck на delivery, и неизбежно burnout от двух работ одновременно. Coding должен быть 0-20% -- это не "бонус", а граница эффективности роли.

> [!question]- Новый EM избегает негативного feedback, говоря всем "great job". К каким последствиям это приведёт через 6 месяцев?
> Люди не растут (не знают о gaps), performance issues накапливаются, top performers frustrated (все "одинаковые"), credibility менеджера падает. Нужен Radical Candor: care personally AND challenge directly, с конкретными примерами и actionable suggestions.

> [!question]- Какой оптимальный span of control для EM и почему?
> 5-9 direct reports для опытного EM, 3-5 для нового. При >10 качество 1-on-1 страдает, нет времени на adequate feedback и career conversations. Факторы, уменьшающие capacity: junior инженеры, complex projects, active hiring, cross-team dependencies.

---

## Ключевые карточки

Как распределяется время EM по категориям?
?
People: 40-50% (1-on-1, hiring, performance, coaching), Delivery: 25-30% (planning, unblocking, stakeholders), Process: 15-20% (meetings, rituals, improvement), Technical: 0-20% (code review, architecture input).

Что входит в EM + Tech Lead + PM partnership?
?
PM определяет WHAT to build (product vision, priorities). Tech Lead определяет HOW to build (architecture, quality). EM определяет WHO builds (team health, hiring, career growth, delivery). Трио покрывает все аспекты команды.

Что такое The Rands Test?
?
11 вопросов для оценки здоровья команды: регулярные 1-on-1, team meetings, понятные приоритеты, status report, доступность информации, участие в hiring, возможность не согласиться, знание стратегии, карьерный путь, нетехническое общение, back-channel feedback. 8+ = healthy.

Какой типичный карьерный путь к EM?
?
Senior Engineer (3-5 лет) -> Tech Lead (1-2 года, опционально) -> Engineering Manager -> Senior EM (2-3 года) -> Director of Engineering. Tech Lead шаг полезен, но не обязателен.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[em-fundamentals]] | Глубже в навыки и практики EM |
| Углубиться | [[one-on-one-meetings]] | Главный инструмент EM |
| Смежная тема | [[conflict-resolution]] | Навыки разрешения конфликтов для people management |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

[[leadership-overview|← Leadership MOC]] | [[em-fundamentals|EM Fundamentals →]]
