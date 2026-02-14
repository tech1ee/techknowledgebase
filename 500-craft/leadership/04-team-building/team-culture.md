---
title: "Культура инженерной команды"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, cto, founder]
teaches:
  - что такое культура
  - как строить культуру
  - примеры компаний
sources: [netflix-culture, valve-handbook, gitlab-handbook]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[building-engineering-team]]"
  - "[[team-dynamics]]"
  - "[[company-handbooks]]"
prerequisites:
  - "[[building-engineering-team]]"
  - "[[em-fundamentals]]"
reading_time: 22
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Культура инженерной команды

> **TL;DR:** Культура — не ping-pong столы и бесплатная еда. Это "как мы здесь делаем вещи". Определяется через behaviors, не values на стене. Создаётся action лидеров, не HR-программами. Netflix: "Adequate performance gets a generous severance." Это культура. "We value excellence" на стене — нет.

---

## Зачем это нужно?

### Типичная ситуация

Стартап пишет "core values". Вешает на стену: Integrity, Excellence, Teamwork, Innovation. Через год — токсичная среда, каждый сам за себя, blame culture. "Но у нас же values!"

**Без intentional culture:**
- Culture happens by accident (usually bad)
- First toxic hire infects others
- "How we do things" = chaos
- Good people leave

**С сознательной культурой:**
- Attracts right people
- Repels wrong people
- Self-reinforcing behaviors
- Competitive advantage

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Employees who consider culture important | 77% | Glassdoor |
| Culture impact on job satisfaction | 30-50% variance | McKinsey |
| Strong culture correlation with returns | 4x | John Kotter |
| Toxic culture attrition risk | 10x | MIT |

---

## Что такое культура?

### Culture = Behavior

```
CULTURE IS NOT:                 CULTURE IS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Values on the wall            • How people actually behave
• HR policies                   • What gets rewarded
• Perks and benefits           • What gets punished
• Mission statement            • What happens when no one watches
• What leaders say             • What leaders do

FORMULA:
Culture = What leaders tolerate + What gets rewarded
```

### Culture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     CULTURE COMPONENTS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  VALUES                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  What we believe is important                                   │
│  Must be actionable, not generic                                │
│  Example: "Customer obsession" vs "We value customers"          │
│                                                                 │
│  NORMS                                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Expected behaviors                                             │
│  How we communicate, decide, collaborate                        │
│  Example: "Disagree and commit" norm                            │
│                                                                 │
│  RITUALS                                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Recurring practices that reinforce values                      │
│  Example: Weekly demo, blameless post-mortems                   │
│                                                                 │
│  STORIES                                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Narratives that transmit values                                │
│  Example: "Remember when X did Y? That's who we are"            │
│                                                                 │
│  SYMBOLS                                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Physical/visible manifestations                                │
│  Example: Open office (collaboration), no titles (flat)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Примеры культур

### Netflix: Freedom & Responsibility

```
CORE PRINCIPLES:
• High talent density
• Context, not control
• Adequate performance = generous severance
• No vacation tracking
• Radical transparency

WHAT THIS MEANS:
┌────────────────────────────────────────────────┐
│ "We're a team, not a family."                  │
│                                                │
│ Families don't fire children.                  │
│ Teams cut players who don't perform.           │
│                                                │
│ → High expectations                            │
│ → Low tolerance for B-players                  │
│ → Freedom for A-players                        │
└────────────────────────────────────────────────┘

TRADEOFFS:
+ High performance
+ Attracts top talent
- High pressure
- Not for everyone
- Can feel cold
```

### GitLab: Transparency

```
CORE PRINCIPLES:
• Handbook-first culture
• Public by default
• Async communication
• No secrets (almost)
• Boring solutions

WHAT THIS MEANS:
┌────────────────────────────────────────────────┐
│ Everything documented publicly.                │
│ 3000+ page public handbook.                    │
│ Salary calculator public.                      │
│ Company OKRs public.                           │
│ Meeting recordings public.                     │
└────────────────────────────────────────────────┘

TRADEOFFS:
+ Scales remote work
+ Reduces meetings
+ Removes politics
- Information overload
- Takes discipline
- Not everyone comfortable
```

### Basecamp: Calm Company

```
CORE PRINCIPLES:
• 40-hour weeks
• No growth at all costs
• Profitable is more important
• Protect maker time
• Question everything

WHAT THIS MEANS:
┌────────────────────────────────────────────────┐
│ Sustainable pace over hustle.                  │
│ Profit over growth.                            │
│ Quality over quantity.                         │
│                                                │
│ "We're not curing cancer."                     │
│ "It's okay to be small."                       │
└────────────────────────────────────────────────┘

TRADEOFFS:
+ Sustainable
+ Attracts work-life focused
- Slower growth
- May not attract ambitious
- Controversial decisions
```

### Valve: Flat Structure

```
CORE PRINCIPLES:
• No managers
• Choose your projects
• Move your desk
• Peer-driven review

WHAT THIS MEANS:
┌────────────────────────────────────────────────┐
│ Employees decide what to work on.              │
│ No formal hierarchy.                           │
│ Peer evaluation drives decisions.              │
│ High autonomy, high ambiguity.                 │
└────────────────────────────────────────────────┘

TRADEOFFS:
+ Innovation
+ Attracts self-starters
- Hard to coordinate
- Can be cliquey
- Doesn't scale easily
- New hires struggle
```

---

## Пошаговый процесс

### Building Culture Intentionally

**Шаг 1: Define Values (3-5)**
```
GOOD VALUES:                    BAD VALUES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Actionable                    • Generic ("excellence")
• Have trade-offs               • Everyone would agree
• Controversial to some         • Just nice words
• Observable in behavior        • Aspirational only

PROCESS:
1. What behaviors do you want to see?
2. What behaviors do you NOT tolerate?
3. What makes top performers different?
4. What would you defend even if costly?

EXAMPLES OF ACTIONABLE VALUES:
• "Disagree and commit" (Amazon)
• "Move fast and break things" (early FB)
• "Don't be evil" (early Google)
• "Context, not control" (Netflix)
```

**Шаг 2: Model Behaviors**
```
LEADER MODELING:

"Culture is what leaders DO,
not what they SAY."

□ Act according to values visibly
□ Call out when you violate (own it)
□ Thank those who live values
□ Give feedback when values violated
□ Fire values-violators (even high performers)

EXAMPLE:
Value: "Transparency"
Leader action: Share salary bands openly
               Share strategic decisions early
               Admit mistakes publicly
```

**Шаг 3: Reinforce Through Systems**
```
HIRING:
• Screen for culture fit/add
• Interview questions about values
• Reference check for behaviors

PERFORMANCE:
• Include values in review
• 360 feedback on behaviors
• Promotion tied to values

RECOGNITION:
• Celebrate values-aligned wins
• Public recognition
• Stories in all-hands

CONSEQUENCES:
• Feedback for violations
• Termination for serious/repeated
• Even high performers
```

**Шаг 4: Ritualize**
```
CREATE RITUALS THAT REINFORCE:

Weekly demo (transparency, shipping)
Blameless post-mortems (learning culture)
Team retros (continuous improvement)
AMA sessions (openness)
Failure celebration (risk-taking)
Peer recognition (collaboration)

RITUAL REQUIREMENTS:
• Regular cadence
• Clear format
• Visible participation
• Connected to values
```

---

## Culture Challenges

### Scaling Culture

```
CHALLENGE:
Culture strong at 10 people.
At 100, it's diluted or lost.

SOLUTIONS:

DOCUMENTATION:
Write it down. Handbook culture.
New hires read and understand.

ONBOARDING:
Culture-focused onboarding.
Not just "here's your laptop."
Stories, history, why.

HIRING:
Culture interview mandatory.
Train interviewers.
Explicit criteria.

LEADERSHIP:
Promote culture-carriers.
Culture = performance criterion.
Remove culture-violators.
```

### Changing Culture

```
CHALLENGE:
Existing culture is broken or wrong.
Need to change.

PROCESS:
1. NAME the problem honestly
   "We have a blame culture."

2. DEFINE target behavior
   "We want blameless learning."

3. MODEL new behavior
   Leaders go first. Visible.

4. REWARD new behavior
   Celebrate examples.

5. CONSEQUENCES for old
   Feedback. Ultimately, exit.

6. PERSISTENCE
   Culture change = years, not months.
   Backsliding normal.

TIMELINE:
First signs: 3-6 months
Noticeable shift: 12-18 months
New normal: 2-3 years
```

### Remote Culture

```
CHALLENGE:
No watercooler. No visible behavior.
How to build culture remotely?

SOLUTIONS:

DOCUMENTATION-FIRST:
• Write everything down
• Async by default
• GitLab handbook model

INTENTIONAL CONNECTION:
• Virtual social events
• 1-on-1 coffee chats
• Team offsites (in person)

VISIBLE BEHAVIOR:
• Decisions in public channels
• Work in public
• Open calendars

RITUALS (adapted):
• Virtual standups
• Recorded demos
• Online team events

TRUST:
• Assume good intent
• Measure output, not presence
• Over-communicate
```

---

## Скрипты и Templates

### Values Definition Template

```markdown
# [Company/Team] Values

## Value 1: [Name]

**What it means:**
[2-3 sentences explanation]

**What it looks like:**
• [Observable behavior]
• [Observable behavior]
• [Observable behavior]

**What it doesn't mean:**
• [Common misconception]

**Example:**
[Story illustrating the value]

## Value 2: [Name]
...

---

## How we use these values

**Hiring:** Values interview, reference check
**Performance:** Part of review criteria
**Promotion:** Required for advancement
**Recognition:** Weekly shoutouts for values

## What happens when values are violated
1. Feedback conversation
2. Documented warning
3. Exit if not improved

*Even high performers are not exempt.*
```

### Culture Interview Questions

```
FOR EACH VALUE, QUESTIONS:

VALUE: Transparency

"Tell me about a time you shared bad news
with stakeholders. How did you approach it?"

"Describe a situation where you had to
balance transparency with confidentiality."

"How do you communicate decisions to
your team?"

VALUE: Ownership

"Tell me about a time something went wrong
on a project. What did you do?"

"How do you approach work outside your
direct responsibility?"

"Describe a time you disagreed with a
decision but had to execute it."

VALUE: Continuous learning

"What's the last significant thing you learned?
How did you learn it?"

"Tell me about a failure and what you learned."

"How do you stay current in your field?"
```

### Culture Onboarding Checklist

```markdown
# Culture Onboarding: [New Hire Name]

## Week 1

### Day 1-2: Read & Reflect
- [ ] Read company handbook
- [ ] Read values document
- [ ] Watch culture video/all-hands recording
- [ ] Reflect: What surprises you? What resonates?

### Day 3-5: Hear Stories
- [ ] 1-on-1 with manager: culture expectations
- [ ] Coffee chat with culture champion
- [ ] Attend team meeting, observe norms

## Week 2-4

### Observe & Ask
- [ ] What rituals exist? Purpose?
- [ ] How are decisions made?
- [ ] How is feedback given?
- [ ] Who are culture exemplars? Why?

### Discuss
- [ ] Check-in with manager on observations
- [ ] Questions about culture expectations
- [ ] Share what you're learning

## Month 2-3

### Live It
- [ ] Participate in rituals
- [ ] Give feedback using norms
- [ ] Contribute to culture discussions

### Reflect
- [ ] What's working for you?
- [ ] What's challenging?
- [ ] How can you contribute to culture?
```

---

## Распространённые ошибки

### Ошибка 1: Values Mismatch

**Как выглядит:**
Say "transparency" but information hoarded.
Say "innovation" but punish failure.

**Почему это проблема:**
- Cynicism
- Trust destroyed
- Values meaningless
- People leave

**Как исправить:**
```
AUDIT:
Do your systems support values?
Does leader behavior match?
Ask team for honest feedback.

Either change behavior to match values,
or change stated values to match reality.
```

### Ошибка 2: Culture = Perks

**Как выглядит:**
Focus on perks (food, games, beer).
Ignore actual working conditions.

**Почему это проблема:**
- Perks don't create culture
- Masks real problems
- Attracts wrong people
- Doesn't retain

**Как исправить:**
```
PERKS ≠ CULTURE

Focus on:
• How decisions are made
• How feedback is given
• How people are treated
• How failure is handled

NOT on:
• Free lunch
• Ping-pong table
• Happy hours
```

### Ошибка 3: Brilliant Jerks

**Как выглядит:**
High performer violates values.
Tolerated because "they're so talented."

**Почему это проблема:**
- Signals values are optional
- Others imitate
- Good people leave
- Culture destroyed

**Как исправить:**
```
RULE: No brilliant jerks.

"The cost of brilliant jerk to team
exceeds their individual contribution."

Action:
Feedback → Improvement plan → Exit if not

Even if they're your "10x engineer."
```

---

## Связанные темы

### Prerequisites
- [[building-engineering-team]] — team basics

### Следующие шаги
- [[team-dynamics]] — psychology of teams
- [[company-handbooks]] — examples of documentation
- [[onboarding]] — transmitting culture

### Связи с другими разделами
- [[communication/]] — culture of communication
- [[thinking/]] — decision-making culture

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Netflix Culture Deck](https://jobs.netflix.com/culture) | Document | F&R philosophy |
| 2 | [GitLab Handbook](https://about.gitlab.com/handbook/) | Document | Transparency culture |
| 3 | [Basecamp Handbook](https://github.com/basecamp/handbook) | Document | Calm company |
| 4 | [Valve Handbook](https://www.valvesoftware.com/en/publications) | Document | Flat structure |
| 5 | [HBR: Culture Research](https://hbr.org/topic/subject/organizational-culture) | Research | Data on culture |

---

## Связь с другими темами

**[[building-engineering-team]]** — Culture и team building — два неразделимых процесса. Культура формируется через actions и decisions при строительстве команды: кого нанимаем, как проводим onboarding, какие behaviors поощряем. Building-engineering-team описывает структурные аспекты (composition, sizing, roles), а team-culture — behavioral и values аспекты. Вместе они определяют, какой командой вы станете.

**[[team-dynamics]]** — Team dynamics — это то, как culture проявляется в ежедневных взаимодействиях. Культура определяет norms (как мы здесь делаем вещи), а dynamics показывает, как эти norms работают в реальности: как проходят meetings, как решаются конфликты, как принимаются решения. Healthy culture создаёт healthy dynamics, но динамика также влияет на культуру через feedback loops.

**[[company-handbooks]]** — Company handbooks — это documented culture, формализация неписаных правил и ценностей. Netflix Culture Deck, Valve Handbook, GitLab Handbook — примеры того, как explicit documentation культуры помогает масштабировать её и onboard новых людей. Handbook не создаёт культуру, но фиксирует её, делая transparent и accountable.

## Источники и дальнейшее чтение

- **Ed Catmull, "Creativity Inc." (2014)** — Глубокий взгляд на строительство creative culture в Pixar. Catmull показывает, что culture of candor (честность без политкорректности), trust и willingness to fail — не абстрактные ценности, а конкретные practices, которые нужно сознательно поддерживать. "Braintrust" meetings — пример culture practice.
- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — Модель Lencioni показывает, что здоровая culture строится послойно: trust → productive conflict → commitment → accountability → results. Попытка создать "culture of accountability" без фундамента trust обречена на провал.
- **Simon Sinek, "Start with Why" (2009)** — Culture начинается с "Why": зачем существует команда, какова её mission. Companies и teams с clear "Why" привлекают людей, которые верят в то же, что создаёт organic cultural alignment без необходимости enforce правила.


## Проверь себя

> [!question]- Culture = Behavior, не Values на стене
> Компания объявляет value 'Transparency', но менеджеры скрывают информацию о layoffs, зарплаты засекречены, решения принимаются за закрытыми дверями. Используя формулу 'Culture = What leaders tolerate + What gets rewarded', объясните почему заявленная culture не работает и что нужно изменить.

> [!question]- Brilliant Jerks дилемма
> Ваш лучший инженер (10x developer) систематически унижает junior разработчиков на code review. Он приносит 30% output команды. Используя принцип 'No Brilliant Jerks', обоснуйте решение и опишите action plan.

> [!question]- Netflix vs Basecamp
> Вы основатель стартапа и выбираете культурную модель. Сравните подходы Netflix (Freedom & Responsibility, high talent density) и Basecamp (Calm Company, 40-hour weeks). Какие trade-offs у каждой модели и для какого типа бизнеса каждая подходит лучше?

## Ключевые карточки

Какая формула определяет реальную культуру компании?
?
Culture = What leaders tolerate + What gets rewarded. Культура определяется не values на стене, а реальным поведением лидеров и тем, что поощряется или наказывается.

Назови 5 компонентов культуры.
?
Values (во что верим), Norms (ожидаемое поведение), Rituals (повторяющиеся практики), Stories (нарративы, передающие ценности), Symbols (видимые проявления).

Сколько времени занимает изменение культуры?
?
Первые признаки: 3-6 месяцев. Заметный сдвиг: 12-18 месяцев. Новая норма: 2-3 года. Backsliding нормален.

Что такое правило 'No Brilliant Jerks'?
?
Стоимость brilliant jerk для команды превышает его индивидуальный вклад. Действие: feedback -> improvement plan -> exit if not improved. Даже если это '10x engineer'.

Чем culture fit отличается от culture add?
?
Culture fit = 'думает как мы' (опасно — ведёт к groupthink). Culture add = разделяет values, но приносит новые perspectives и diverse thinking.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[company-handbooks]] | Документирование культуры в handbook |
| Углубиться | [[team-dynamics]] | Как культура проявляется в динамике |
| Смежная тема | [[remote-team-communication]] | Особенности культуры в remote командах |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
*Связано с: [[leadership-overview]]*
