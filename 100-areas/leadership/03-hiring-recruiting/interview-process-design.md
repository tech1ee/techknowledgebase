---
title: "Дизайн процесса интервью"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, hr, tech-lead]
teaches:
  - структура процесса
  - типы интервью
  - оценка кандидатов
sources: [google-rework, stripe-interviews, structured-hiring]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
  - interview
related:
  - "[[hiring-engineers]]"
  - "[[leadership-interviews]]"
  - "[[making-offers]]"
  - "[[sourcing-candidates]]"
prerequisites:
  - "[[hiring-engineers]]"
---

# Дизайн процесса интервью

> **TL;DR:** Хороший процесс интервью: structured (одинаковые вопросы), evidence-based (конкретные наблюдения), и respectful (candidate experience). Цель — максимизировать signal при минимизации bias и времени. Rule of thumb: 4-5 интервью достаточно, больше не добавляет signal.

---

## Зачем это нужно?

### Типичная ситуация

Каждый interviewer спрашивает что хочет. После debrief: "Мне понравился" vs "Мне не очень". Нет общих criteria. Решение на "gut feel". Иногда hire хорошие, иногда — нет. Невозможно понять что работает.

**Без структурированного процесса:**
- Bias доминирует
- Inconsistent decisions
- Нельзя improve (нет data)
- Плохой candidate experience

**Со структурированным процессом:**
- Objective evaluation
- Better predictions
- Improvable process
- Fair и respectful

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Structured vs unstructured interview validity | 0.51 vs 0.38 | Schmidt & Hunter |
| Bias reduction с structure | -40% | Google Research |
| Optimal number of interviews | 4 | Google (diminishing returns) |
| Candidate experience impact на employer brand | 60% share negative | Glassdoor |

---

## Типы интервью

### Overview

```
PHONE SCREEN (30-45 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Basic qualification, mutual fit
Who: Recruiter или hiring manager
Evaluates: Background, motivation, logistics

TECHNICAL CODING (45-60 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Coding ability, problem-solving
Who: Engineer
Evaluates: Code quality, thinking process

SYSTEM DESIGN (45-60 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Architecture, trade-offs
Who: Senior engineer
Evaluates: Scalability, design decisions

BEHAVIORAL (45-60 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Past behavior, soft skills
Who: Manager или team member
Evaluates: Collaboration, communication

CULTURE/VALUES (30-45 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Alignment с company values
Who: Cross-functional или senior
Evaluates: Culture add, long-term fit

HIRING MANAGER (45-60 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Role fit, team dynamics
Who: Hiring manager
Evaluates: Motivation, expectations
```

### Interview Structure by Level

```
JUNIOR/NEW GRAD:
┌─────────────────────────────────────────────────┐
│ 1. Phone screen (30 min)                        │
│ 2. Take-home OR live coding (60-90 min)         │
│ 3. Technical deep-dive (45 min)                 │
│ 4. Behavioral + hiring manager (45 min)         │
└─────────────────────────────────────────────────┘
Total: 3-4 interviews, 3-4 hours

MID-LEVEL:
┌─────────────────────────────────────────────────┐
│ 1. Phone screen (30 min)                        │
│ 2. Technical coding (60 min)                    │
│ 3. System design (45 min)                       │
│ 4. Behavioral (45 min)                          │
│ 5. Hiring manager (45 min)                      │
└─────────────────────────────────────────────────┘
Total: 4-5 interviews, 4-5 hours

SENIOR/STAFF:
┌─────────────────────────────────────────────────┐
│ 1. Phone screen (45 min)                        │
│ 2. System design (60 min)                       │
│ 3. Technical deep-dive (60 min)                 │
│ 4. Leadership/influence (45 min)                │
│ 5. Behavioral + culture (45 min)                │
│ 6. Hiring manager + team (60 min)               │
└─────────────────────────────────────────────────┘
Total: 5-6 interviews, 5-6 hours
```

---

## Как это работает?

### Structured Interview Design

```
┌─────────────────────────────────────────────────────────────────┐
│                 STRUCTURED INTERVIEW DESIGN                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DEFINE CRITERIA                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  What competencies matter for this role?                        │
│  • Technical skills (coding, design, domain)                    │
│  • Behavioral (collaboration, communication)                    │
│  • Values (culture fit/add)                                     │
│                                 ↓                               │
│  2. DESIGN QUESTIONS                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Questions that elicit evidence for criteria                    │
│  Same questions for all candidates                              │
│  Behavioral: STAR format                                        │
│                                 ↓                               │
│  3. CREATE RUBRIC                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  What does 1-5 look like for each criteria?                     │
│  Specific examples for each score                               │
│                                 ↓                               │
│  4. TRAIN INTERVIEWERS                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Calibrate on scoring                                           │
│  Bias awareness                                                 │
│  Practice sessions                                              │
│                                 ↓                               │
│  5. CONDUCT & SCORE                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  Score immediately after                                        │
│  Independent (before debrief)                                   │
│  Evidence-based notes                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Evaluation Framework

```
SCORING SCALE (1-5):

5 — EXCEPTIONAL
   Clear signal above bar. Would advocate strongly.
   "This is exactly what we need, maybe better."

4 — STRONG
   Above bar. Comfortable hiring.
   "Solid fit for the role."

3 — MEETS BAR
   Acceptable. Some concerns but passable.
   "Would be okay, not excited."

2 — BELOW BAR
   Notable gaps. Would not recommend.
   "Missing key requirements."

1 — SIGNIFICANTLY BELOW
   Clear miss. Strong no hire.
   "Not qualified for this role."

RULE: Score on CRITERIA, not "overall impression."
```

### Bias Awareness

```
COMMON BIASES IN INTERVIEWS:

CONFIRMATION BIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"First impression" sets the tone.
After that, look for evidence to confirm.

Mitigation: Score criteria independently.
            Seek disconfirming evidence.

SIMILARITY BIAS ("Like Me")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Favor candidates similar to self.
Same school, hobbies, background.

Mitigation: Focus on JOB criteria.
            Diverse interview panels.

HALO/HORN EFFECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
One strong trait colors everything.
Good at coding → "must be good leader."

Mitigation: Evaluate each criteria separately.

ANCHORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
First candidate sets the benchmark.
Or first interviewer's opinion dominates.

Mitigation: Independent scoring.
            Absolute criteria, not relative.

RECENCY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remember end of interview more than start.

Mitigation: Take notes throughout.
            Score immediately after.
```

---

## Типы вопросов

### Technical Coding Interview

```
PROBLEM SELECTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Solvable in 30-45 minutes
• Multiple approaches possible
• Extendable (follow-ups)
• Relevant to actual work

STRUCTURE (60 min total):
[5 min]  Intro, make comfortable
[5 min]  Problem statement
[35 min] Solving (with hints as needed)
[10 min] Testing, edge cases
[5 min]  Questions from candidate

WHAT TO EVALUATE:
□ Problem solving approach
□ Communication while thinking
□ Code quality
□ Testing mindset
□ Response to hints

EXAMPLE RUBRIC:
5: Optimal solution, clean code, all edge cases
4: Good solution, minor issues, most edge cases
3: Working solution, some issues, basic tests
2: Partial solution, struggles significantly
1: Cannot make meaningful progress
```

### System Design Interview

```
PROBLEM SELECTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Open-ended (no single answer)
• Scalability considerations
• Trade-offs to discuss
• Relevant to company domain

STRUCTURE (60 min total):
[5 min]  Intro
[10 min] Requirements clarification
[25 min] High-level design
[15 min] Deep dive on component
[5 min]  Wrap-up, questions

WHAT TO EVALUATE:
□ Requirement gathering
□ Breaking down complexity
□ Trade-off reasoning
□ Scalability awareness
□ Communication clarity

EXAMPLE TOPICS:
• Design URL shortener
• Design rate limiter
• Design notification system
• Design [your product feature]
```

### Behavioral Interview

```
STAR METHOD QUESTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Questions about PAST BEHAVIOR
(not hypotheticals)

PATTERN:
"Tell me about a time when..."
"Give me an example of..."
"Describe a situation where..."

TOPICS TO COVER:
□ Teamwork and collaboration
□ Conflict resolution
□ Handling ambiguity
□ Failure and learning
□ Leadership (for senior roles)
□ Prioritization
□ Communication

EXAMPLE QUESTIONS:
"Tell me about a time you disagreed with
a technical decision. How did you handle it?"

"Describe a project that didn't go well.
What happened? What did you learn?"

"Give me an example of when you had to
make a decision with incomplete information."
```

---

## Пошаговый процесс дизайна

### Шаг 1: Map Criteria to Interviews

```
ПРИМЕР ДЛЯ SENIOR ENGINEER:

CRITERIA              INTERVIEW        INTERVIEWER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coding ability        Coding           Engineer A
System design         Design           Engineer B (Sr)
Collaboration         Behavioral       Engineer C
Domain expertise      Technical        Engineer B
Communication         All              All
Culture fit           Culture          Cross-func D
Role fit              HM interview     Hiring Manager
```

### Шаг 2: Create Question Bank

```
ДЛЯ КАЖДОГО ТИПА ИНТЕРВЬЮ:

1. Primary questions (3-5)
   То что ТОЧНО спросить

2. Follow-up questions
   Для углубления

3. Backup questions
   Если primary не подходит

4. Red flag probes
   Если заметил concern

DOCUMENT:
□ Question text
□ What it evaluates
□ What good/bad answers look like
□ Follow-ups
```

### Шаг 3: Build Rubric

```
FOR EACH CRITERIA:

Example: "Collaboration"

5 — EXCEPTIONAL
Examples of leading cross-team initiatives.
Resolves conflicts constructively.
Others seek them for collaboration.
Mentors others effectively.

4 — STRONG
Works well across teams.
Handles disagreements maturely.
Seeks input from others.
Good communication.

3 — MEETS
Can work with others.
No red flags.
Basic communication.
Some examples of teamwork.

2 — BELOW
Limited collaboration examples.
Signs of difficulty with others.
Poor communication.

1 — SIGNIFICANTLY BELOW
Cannot work with others.
Blames team for failures.
Dismissive.
```

### Шаг 4: Interviewer Training

```
TRAINING INCLUDES:
□ Understanding the role and criteria
□ How to use the rubric
□ Bias awareness
□ Legal compliance (what NOT to ask)
□ Candidate experience tips
□ Practice interviews
□ Calibration exercises

CALIBRATION:
Watch same interview recording.
Each scores independently.
Compare and discuss differences.
Align on what each score means.
```

---

## Candidate Experience

### Best Practices

```
BEFORE INTERVIEW:
□ Clear job description
□ What to expect (process overview)
□ Who they'll meet
□ How long each round
□ How to prepare
□ Contact for questions

DURING INTERVIEW:
□ Start on time
□ Interviewer introduces self
□ Explain the format
□ Allow questions at end
□ Don't check phone
□ Be engaged

AFTER INTERVIEW:
□ Clear timeline for decision
□ Timely updates (даже если нет news)
□ Constructive rejection (if applicable)
□ Thank them regardless of outcome
```

### Timeline Expectations

```
RESPONSE TO APPLICATION:
< 1 week (ideally 3 days)

SCHEDULING:
< 1 week from screen to next round

BETWEEN ROUNDS:
< 3 days

POST-FINAL ROUND TO DECISION:
< 3 business days

TOTAL PROCESS:
2-4 weeks (faster wins)

COMMUNICATION:
• Every 3-5 days if waiting
• Immediate if status changes
```

---

## Скрипты и Templates

### Interview Opening Script

```
"Привет [Name], я [Your Name], [Role].
Я буду проводить [interview type] сегодня.

Формат такой: [explain structure]
У нас [X] минут. В конце будет время
для твоих вопросов.

Для меня важно понять твой thought process,
поэтому думай вслух когда решаешь.

Готов? Есть вопросы перед началом?"
```

### Coding Interview Problem Intro

```
"Сейчас я дам тебе задачу.
Сначала убедись что понял requirements.
Задавай вопросы — это encouraged.

Я буду смотреть на:
• Как ты подходишь к проблеме
• Твой код и design decisions
• Как общаешься в процессе

Можешь использовать любой язык.
Если застрянешь — спрашивай, я дам hints.

Вот задача: [problem statement]"
```

### Behavioral Question Probes

```
ОСНОВНОЙ ВОПРОС:
"Tell me about a time when you had to
deal with a difficult colleague."

IF VAGUE ANSWER:
"Can you give me a specific example?"
"What exactly did you do?"
"What was the outcome?"

IF HYPOTHETICAL:
"That's a good approach. Have you actually
done this? Can you walk me through a
real situation?"

IF BLAMING:
"What was YOUR role in that?"
"What could YOU have done differently?"

IF TOO SHORT:
"Tell me more about that."
"What happened next?"
```

### Debrief Template

```markdown
# Interview Debrief: [Candidate]
Date: [Date]
Participants: [Names]

## 1. Independent Scores (before discussion)

| Interviewer | Round | Score | Key Notes |
|-------------|-------|-------|-----------|
| [Name] | Coding | X | [brief] |
| [Name] | Design | X | [brief] |
| [Name] | Behavioral | X | [brief] |
| [Name] | Culture | X | [brief] |

## 2. Discussion Points
[What came up in discussion]

## 3. Concerns
[Specific concerns and whether resolved]

## 4. Decision
[ ] Strong Hire
[ ] Hire
[ ] No Hire
[ ] Strong No Hire

## 5. Rationale
[Why this decision]

## 6. Level Discussion (if hire)
[Appropriate level and why]

## 7. Next Steps
[Offer / reject / additional info needed]
```

---

## Распространённые ошибки

### Ошибка 1: Inconsistent Questions

**Как выглядит:**
Каждый interviewer спрашивает что хочет. Нет сравнимых данных между кандидатами.

**Как исправить:**
```
STANDARDIZE:
□ Question bank для каждого round
□ Same questions for same role
□ Flexibility в follow-ups, не в core
```

### Ошибка 2: Group Discussion First

**Как выглядит:**
В debrief первый говорящий влияет на всех. "Мне понравился!" → все соглашаются.

**Как исправить:**
```
INDEPENDENT FIRST:
1. Submit scores BEFORE meeting
2. No discussion until all submitted
3. Then discuss differences
```

### Ошибка 3: No Clear Bar

**Как выглядит:**
"4 из 5, наверное hire?" Каждый интерпретирует scores по-своему.

**Как исправить:**
```
DEFINE THE BAR:
• What score = hire?
• What combinations work?
• What is automatic no-hire?

Example: "Average ≥3.5, no score <3 on core criteria"
```

### Ошибка 4: Too Many Interviews

**Как выглядит:**
8 rounds. Candidate exhausted. Same signals repeated. Time wasted.

**Как исправить:**
```
RESEARCH (Google):
After 4 interviews, diminishing returns.
Additional interviews add noise, not signal.

RULE: 4-5 interviews maximum.
If can't decide — problem is criteria, not data.
```

---

## Связанные темы

### Prerequisites
- [[hiring-engineers]] — общий подход к найму

### Следующие шаги
- [[leadership-interviews]] — интервью на leadership роли
- [[making-offers]] — после successful interviews
- [[sourcing-candidates]] — pipeline для interviews

### Связи с другими разделами
- [[career/interview/]] — perspective кандидата
- [[communication/]] — communication в interviews

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Google re:Work Hiring](https://rework.withgoogle.com/subjects/hiring/) | Research | Structured interviews |
| 2 | [Schmidt & Hunter Meta-Analysis](https://citeseerx.ist.psu.edu/document?doi=10.1.1.172.1733) | Research | Interview validity |
| 3 | [Stripe Interview Process](https://stripe.com/blog/bring-your-own-interview) | Article | Practical approach |
| 4 | [interviewing.io Research](https://interviewing.io/blog) | Research | Technical interview insights |
| 5 | [First Round Review: Interviews](https://review.firstround.com/) | Articles | Practical tips |

### Дополнительное чтение

- "Who" by Geoff Smart — structured hiring
- "Work Rules!" by Laszlo Bock — Google hiring
- "The Effective Hiring Manager" by Mark Horstman — Manager Tools

---

## Связь с другими темами

**[[hiring-engineers]]** — Hiring-engineers задаёт общую философию найма и критерии оценки, а interview-process-design превращает их в конкретный structured процесс. Без чётких hiring criteria процесс интервью становится subjective и inconsistent. Вместе они формируют полную систему: ЧТО оценивать (hiring-engineers) и КАК оценивать (interview-process-design).

**[[leadership-interviews]]** — Интервью на leadership роли (EM, Director, VP, CTO) требуют принципиально другого подхода, чем интервью IC. Фокус смещается с technical skills на leadership competencies: people development, strategic thinking, execution history. Failure rate при executive hiring составляет 40-50%, что делает правильный process design для leadership позиций особенно критичным.

**[[making-offers]]** — Дизайн interview процесса влияет не только на quality of hire, но и на candidate experience, которая определяет acceptance rate на этапе оффера. Затянутый, неорганизованный процесс теряет лучших кандидатов, даже если финальное решение правильное. Respect к времени кандидата через efficient process — часть employer brand.

**[[sourcing-candidates]]** — Sourcing и interview process должны быть согласованы: нет смысла sourcing'ить passive candidates через персонализированный outreach, а потом проводить generic, стрессовый interview. Candidate experience должна быть consistent от первого контакта до финального решения. Кроме того, feedback loop из interview результатов помогает улучшить sourcing quality.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Описывает, как менеджер на каждом уровне участвует в interview process: от проведения individual interviews до дизайна hiring pipeline для целого отдела. Практические рекомендации по calibration и debrief.
- **Kim et al., "The Phoenix Project" (2016)** — Хотя книга не о hiring напрямую, она демонстрирует, как системный подход к процессам (Theory of Constraints) применим к любому pipeline, включая hiring funnel. Bottleneck analysis помогает оптимизировать interview process.
- **Peter Drucker, "The Effective Executive" (2006)** — Глава о staffing decisions — одна из самых сильных. Drucker утверждает, что hiring — это единственное решение, которое executive не может отменить без последствий, и поэтому ему нужно уделять максимум внимания.

---

*Последнее обновление: 2026-01-18*
*Связано с: [[leadership-overview]]*
