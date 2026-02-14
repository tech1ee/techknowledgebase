---
title: "Интервью на EM/Director/VP/CTO"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [em, director, vpe, cto, hr]
teaches:
  - оценка leadership кандидатов
  - вопросы для разных уровней
  - red flags
sources: [topgrading, executive-search, who-book]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
  - interview
related:
  - "[[hiring-engineers]]"
  - "[[interview-process-design]]"
  - "[[first-90-days]]"
  - "[[cto-vs-vpe]]"
prerequisites:
  - "[[hiring-engineers]]"
  - "[[interview-process-design]]"
  - "[[em-fundamentals]]"
reading_time: 24
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Интервью на EM/Director/VP/CTO

> **TL;DR:** Leadership hiring — highest stakes, highest failure rate (40-50% при executive level). Technical skills вторичны — оценивай leadership competencies: people development, strategic thinking, execution, communication. Past behavior predicts future: глубокое погружение в track record. References критичны — 5-10 calls для senior roles.

---

## Зачем это нужно?

### Типичная ситуация

Нужен Engineering Manager. Наняли лучшего IC — "он знает продукт, команда его уважает". Через год: не справляется с people management, команда разваливается, сам выгорает. Или: наняли VP Engineering с great resume. Через 6 месяцев — culture clash, half the team leaves.

**Без специального процесса для leadership:**
- 40-50% executive hires fail
- Дорогая ошибка (сотни тысяч $)
- Team disruption
- Упущенное время

**С правильным процессом:**
- Better prediction
- Culture alignment
- Clear expectations
- Higher success rate

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Executive hiring failures | 40-50% | HBR |
| Cost of failed executive | $2.7M average | CEB |
| Time to identify misfit | 18 months average | DDI |
| Importance of references | 5-10 calls = 3x better outcomes | ghSmart |

---

## Levels и что оценивать

### Competencies by Level

```
┌─────────────────────────────────────────────────────────────────┐
│          LEADERSHIP COMPETENCIES BY LEVEL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ENGINEERING MANAGER (EM)                                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  PRIMARY:                                                       │
│  • People development (hiring, coaching, feedback)              │
│  • Team execution (delivery, quality, process)                  │
│  • Technical judgment (not coding — decision quality)           │
│  • Communication (up, down, cross-functional)                   │
│                                                                 │
│  SECONDARY:                                                     │
│  • Strategic thinking (at team level)                           │
│  • Stakeholder management                                       │
│  • Culture building                                             │
│                                                                 │
│  DIRECTOR                                                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  PRIMARY:                                                       │
│  • Managing managers                                            │
│  • Organizational design                                        │
│  • Cross-functional leadership                                  │
│  • Strategic planning (org level)                               │
│                                                                 │
│  SECONDARY:                                                     │
│  • Executive presence                                           │
│  • Change management                                            │
│  • Talent strategy                                              │
│                                                                 │
│  VP ENGINEERING                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  PRIMARY:                                                       │
│  • Scaling organization                                         │
│  • Executive partnership (with CEO, product)                    │
│  • Talent acquisition strategy                                  │
│  • Operational excellence                                       │
│                                                                 │
│  SECONDARY:                                                     │
│  • Board communication                                          │
│  • Budget management                                            │
│  • M&A technical due diligence                                  │
│                                                                 │
│  CTO                                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  PRIMARY:                                                       │
│  • Technical vision and strategy                                │
│  • External representation                                      │
│  • Architecture and technical direction                         │
│  • Innovation leadership                                        │
│                                                                 │
│  SECONDARY:                                                     │
│  • Customer-facing technical sales                              │
│  • Partnership/M&A evaluation                                   │
│  • Industry thought leadership                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Interview Loop by Level

```
EM INTERVIEW LOOP (5-6 rounds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Phone screen (Recruiter/HM)
2. Technical assessment (Senior IC)
3. Management/behavioral (Director)
4. Team interaction (Prospective reports)
5. Cross-functional (PM/Design)
6. Hiring manager final (Director)

DIRECTOR LOOP (6-7 rounds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Phone screen (Recruiter/VP)
2. Leadership deep-dive (VP)
3. Technical strategy (CTO/Tech lead)
4. Managing managers (Senior EM)
5. Cross-functional (CPO/CFO)
6. Team interaction (Skip-levels)
7. Final (CEO or VP)

VP/CTO LOOP (7-10 rounds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Recruiter screen
2. Hiring manager (CEO/COO)
3. Leadership case study
4. Technical strategy (if CTO)
5. Executive team (CFO, CPO, etc.)
6. Board member(s)
7. Skip-level (Directors/Managers)
8. Reference deep-dive (5-10 calls)
9. Final (CEO)
```

---

## Вопросы по компетенциям

### People Development

```
EM LEVEL:
"Tell me about someone you developed from
junior to senior. What was your approach?"

"How do you handle an underperformer?
Walk me through a specific example."

"How do you approach 1-on-1s? What do you
typically discuss?"

DIRECTOR+ LEVEL:
"How have you built your management bench?
Give me an example of a manager you developed."

"Tell me about a time you had to let a
manager go. What led to that decision?"

"How do you ensure your managers are
effective? What signals do you look for?"

WHAT TO LISTEN FOR:
✓ Specific examples with outcomes
✓ Empathy + accountability balance
✓ Systematic approach
✓ Investment in others' growth

RED FLAGS:
✗ Vague answers ("I coach them")
✗ Taking credit for others' work
✗ No terminated/managed-out examples
✗ "I don't have underperformers" (unrealistic)
```

### Team Execution

```
EM LEVEL:
"Tell me about a project that was at risk
of missing deadline. What did you do?"

"How do you prioritize across competing
demands? Give me an example."

"Describe a process you implemented that
improved team delivery."

DIRECTOR+ LEVEL:
"How have you scaled delivery across
multiple teams? What worked? What didn't?"

"Tell me about a major initiative that
failed. What happened? What did you learn?"

"How do you balance technical debt with
feature delivery?"

WHAT TO LISTEN FOR:
✓ Structured approach to problems
✓ Data-driven decisions
✓ Balancing speed and quality
✓ Learning from failures

RED FLAGS:
✗ Only successes, no failures
✗ Blame on external factors
✗ Hero mentality ("I saved it")
✗ No process thinking
```

### Technical Judgment

```
EM LEVEL:
"How do you stay technical enough to make
good decisions without coding daily?"

"Tell me about a technical decision you
pushed back on. Why? What was the outcome?"

"How do you evaluate technical proposals
from your team?"

DIRECTOR+ LEVEL:
"How do you balance build vs buy decisions?
Give me an example."

"Tell me about an architectural decision
that went wrong. What would you do differently?"

"How do you maintain technical credibility
with your teams?"

VP/CTO LEVEL:
"How do you develop technical strategy?
Walk me through your process."

"Tell me about a major technology bet you
made. How did it play out?"

"How do you evaluate emerging technologies
for adoption?"

WHAT TO LISTEN FOR:
✓ Sound judgment process
✓ Knowing when to defer to experts
✓ Strategic thinking about technology
✓ Continuous learning

RED FLAGS:
✗ Overconfidence in technical opinions
✗ Not staying current
✗ Either too hands-on or too distant
✗ No examples of wrong calls
```

### Strategic Thinking

```
DIRECTOR+ LEVEL:
"How do you translate business goals into
engineering priorities?"

"Tell me about a strategy you developed
that didn't work. What did you learn?"

"How do you balance short-term delivery
with long-term technical health?"

VP/CTO LEVEL:
"How do you think about building vs
acquiring technology capabilities?"

"Tell me about a time you had to make a
significant pivot in technical direction."

"How do you structure your engineering
organization to support business strategy?"

WHAT TO LISTEN FOR:
✓ Big picture thinking
✓ Connection between tech and business
✓ Long-term perspective
✓ Ability to simplify complexity

RED FLAGS:
✗ Purely tactical thinking
✗ Can't explain strategy simply
✗ No business context
✗ Analysis paralysis
```

### Communication & Influence

```
ALL LEVELS:
"Tell me about a time you had to convince
stakeholders of a difficult technical decision."

"How do you communicate bad news upward?"

"Describe a conflict with another leader.
How did you resolve it?"

VP/CTO LEVEL:
"How do you communicate technical strategy
to the board?"

"Tell me about a time you had to push back
on the CEO/founder."

"How do you build relationships with
non-technical executives?"

WHAT TO LISTEN FOR:
✓ Clear, structured communication
✓ Ability to adjust to audience
✓ Constructive conflict approach
✓ Influence without authority

RED FLAGS:
✗ Technical jargon without awareness
✗ Avoid difficult conversations
✗ Us-vs-them mentality
✗ Can't simplify for non-technical
```

---

## Behavioral Deep-Dive (Topgrading Style)

### Chronological Walkthrough

```
FOR EACH PREVIOUS ROLE (last 3-4):

"Walk me through your time at [Company].

1. What were you hired to do?
2. What accomplishments are you most proud of?
3. What were your low points or failures?
4. What would your boss say about your
   performance? Strengths? Weaknesses?
5. Why did you leave?"

TIME PER ROLE: 20-30 minutes
TOTAL: 60-90 minute interview

KEY TECHNIQUE:
After each answer: "Tell me more about that"
Probe specifics: who, what, when, results
```

### Threat of Reference Check (TORC)

```
TECHNIQUE:
"When we speak with [boss name] — and we will
as part of reference checks — what will they
say about your performance?"

WHY IT WORKS:
• Creates honesty incentive
• Surfaces real weaknesses
• Identifies potential red flags

FOLLOW-UP:
"You mentioned they'd say [weakness].
Tell me more about that. What happened?"
```

---

## Reference Calls

### Who to Call

```
FOR SENIOR ROLES (Director+):

REQUIRED (5-7 calls):
• Former bosses (2-3)
• Former peers (2)
• Former reports (2)

NICE TO HAVE:
• Board members
• Customers/vendors
• People who worked with them years ago

WHO TO CALL:
✓ People THEY don't suggest (backdoor)
✓ People who know them well (2+ years)
✓ People who saw them under pressure
✓ Recent references + older ones

BACKDOOR REFERENCES:
Find through LinkedIn connections.
"I see you worked at [Company] same time as [Candidate].
Could I ask about your experience working with them?"
```

### Reference Questions

```
OPENING:
"Thanks for taking the time. I'll keep this
to 15-20 minutes.

[Name] is a finalist for [Role] at [Company].
I understand you [relationship].
Mind sharing your perspective?"

PERFORMANCE:
"On a scale of 1-10, how would you rate
[Name]'s overall performance?"
(Most say 7-8. Below 7 is concerning.)

"What were their biggest strengths?"
"What were their areas for development?"

SPECIFICS:
"How did they handle [specific situation
mentioned in interview]?"

"How did they build and develop their team?"

"How did they handle underperformers?"

"How were they at managing up?"

FINAL:
"Would you work with them again?"
(Hesitation is a red flag)

"Is there anything I should know that
I haven't asked?"

"Is there anyone else I should talk to?"
```

---

## Red Flags

### In Interview

```
PEOPLE MANAGEMENT:
🚩 Can't name specific people they developed
🚩 No examples of difficult conversations
🚩 "I don't have underperformers"
🚩 Taking credit for team's work
🚩 High turnover they can't explain

EXECUTION:
🚩 All successes, no failures
🚩 Blames others or circumstances
🚩 "Hero saves the day" stories only
🚩 No process or systems thinking
🚩 Can't quantify impact

JUDGMENT:
🚩 Overconfidence in technical opinions
🚩 Black-and-white thinking
🚩 Can't explain decisions simply
🚩 Dismissive of other viewpoints

COMMUNICATION:
🚩 Talks more than listens
🚩 Can't adjust to audience
🚩 Avoids direct answers
🚩 Badmouths previous companies
🚩 Us-vs-them language

CAREER:
🚩 Short tenures repeatedly (<18 months)
🚩 Gaps they can't explain
🚩 Progression doesn't make sense
🚩 Left too many roles involuntarily
```

### In References

```
🚩 "Would you hire them again?" → Hesitation
🚩 Unable to find good references
🚩 Off-list references are negative
🚩 Discrepancies from interview answers
🚩 Faint praise ("they were fine")
🚩 Emphasis on "difficult circumstances"
🚩 High turnover on their teams
🚩 Reference doesn't know them well
```

---

## Скрипты и Templates

### Leadership Interview Scorecard

```markdown
# Leadership Interview: [Candidate]
Role: [EM/Director/VP]
Interviewer: [Name]
Date: [Date]

## COMPETENCY SCORING

| Competency | Score (1-5) | Evidence |
|------------|-------------|----------|
| People Development | | |
| Team Execution | | |
| Technical Judgment | | |
| Strategic Thinking | | |
| Communication | | |
| Culture Fit | | |

## KEY OBSERVATIONS

### Strengths (with specific examples)
1.
2.
3.

### Concerns (with specific examples)
1.
2.
3.

## REFERENCE CHECK QUESTIONS
(Things to verify with references)
1.
2.

## RECOMMENDATION
[ ] Strong Hire
[ ] Hire
[ ] No Hire
[ ] Strong No Hire

## RATIONALE
[Why this recommendation]
```

### Reference Check Template

```markdown
# Reference Check: [Candidate]
Reference: [Name, Title, Company]
Relationship: [Boss/Peer/Report]
Dates worked together: [X to Y]
Interviewer: [Name]
Date: [Date]

## RATINGS
Overall performance (1-10): ___
Would hire again (Y/N): ___

## KEY POINTS

### Strengths mentioned:
1.
2.

### Development areas mentioned:
1.
2.

## SPECIFIC QUESTIONS ASKED

Q: [Question]
A: [Answer]

Q: [Question]
A: [Answer]

## VERIFICATION
(Match to interview claims)

Claim: [What candidate said]
Reference says: [What reference said]
Match? [Yes/No/Partial]

## ADDITIONAL NAMES SUGGESTED
-
-

## RED FLAGS / CONCERNS
-

## OVERALL IMPRESSION
[Summary]
```

---

## Когда применять разные подходы

### For EM Hiring

```
FOCUS ON:
• People management specifics
• Team-level execution
• Technical judgment (not coding)
• Communication with stakeholders

LESS EMPHASIS ON:
• Strategic thinking (not yet)
• Organizational design
• Executive presence
```

### For Director Hiring

```
FOCUS ON:
• Managing managers
• Scaling teams
• Cross-functional leadership
• Strategic planning

ADDITIONAL:
• Skip-level interviews
• References from reports
• Organizational design questions
```

### For VP/CTO Hiring

```
FOCUS ON:
• Executive partnership
• Scaling organization
• Technical vision (CTO)
• Board communication

ADDITIONAL:
• Board member interviews
• Extensive references (7-10)
• Leadership case study
• Extended process (weeks)
```

---

## Связанные темы

### Prerequisites
- [[hiring-engineers]] — general hiring
- [[interview-process-design]] — process design

### Следующие шаги
- [[first-90-days]] — onboarding leaders
- [[cto-vs-vpe]] — role clarity

### Связи с другими разделами
- [[career/interview/leadership]] — candidate perspective
- [[communication/]] — communication assessment

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Who: The A Method](https://www.amazon.com/Who-Method-Hiring-Geoff-Smart/dp/0345504194) | Book | Topgrading, TORC |
| 2 | [Topgrading](https://www.amazon.com/Topgrading-Hiring-Coaching-Keeping-Players/dp/1591845262) | Book | Chronological interview |
| 3 | [HBR: Executive Hiring](https://hbr.org/topic/subject/hiring) | Research | Failure rates |
| 4 | [First Round: Hiring Leaders](https://review.firstround.com/) | Articles | Practical tips |
| 5 | [ghSmart Research](https://ghsmart.com/) | Research | Reference importance |

---

## Связь с другими темами

**[[hiring-engineers]]** — Leadership hiring строится на тех же фундаментальных принципах, что и hiring инженеров (structured process, evidence-based evaluation), но с существенно другим фокусом. Вместо оценки coding skills оцениваются leadership competencies. Понимание общего hiring framework из hiring-engineers помогает адаптировать процесс для leadership позиций, сохраняя rigorous и fair подход.

**[[interview-process-design]]** — Для leadership ролей дизайн процесса приобретает дополнительные измерения: chronological interview (разбор всей карьерной истории), reference calls (5-10 для senior roles), cultural fit assessment и simulation exercises. Стандартные whiteboard interviews неприменимы, и процесс должен быть redesigned с учётом специфики оцениваемых компетенций.

**[[first-90-days]]** — Результат leadership hiring напрямую определяет успех первых 90 дней нового лидера. Вопросы, заданные на интервью, должны покрывать те же области, которые будут критичны в first-90-days: способность слушать и учиться, building relationships, execution capability. Плохой interview process нанимает людей, которые провалят первые 90 дней.

**[[cto-vs-vpe]]** — При найме на senior technology leadership позиции критически важно понимать разницу между CTO и VP Engineering ролями. Часто компании ищут "CTO", но на самом деле нужен VP Engineering (или наоборот). Clarity о роли до начала interview процесса предотвращает expectations mismatch и costly mis-hires.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Описывает компетенции, которые нужно оценивать на каждом уровне leadership: от первого EM до CTO. Помогает составить scorecard для leadership интервью с конкретными expectations по уровням.
- **Will Larson, "An Elegant Puzzle" (2019)** — Содержит практические рекомендации по hiring engineering leaders, включая разницу между hiring менеджеров "with experience" и "with potential". Larson описывает, как оценить, сможет ли кандидат масштабироваться с ростом организации.
- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — При оценке leadership кандидатов модель Lencioni помогает проверить, сможет ли кандидат строить trust, manage conflict productively и hold people accountable — три ключевые competencies, которые часто упускаются при focus на technical leadership.

---

## Проверь себя

> [!question]- Почему интервью на EM/Director/CTO принципиально отличается от интервью инженера?
> Leadership roles оценивают не technical skills, а people management, strategic thinking, organizational design и culture building. Behavioral evidence из прошлого опыта (tell me about a time...) важнее гипотетических ответов. Past performance = лучший predictor.

> [!question]- Как оценить, сможет ли кандидат на VP Eng масштабировать организацию, если он никогда этого не делал?
> Смотреть на adjacent experience: управлял ли ростом команды хотя бы 2x, принимал ли org design решения, нанимал ли менеджеров. Оценивать thinking frameworks (как бы подошёл к проблеме), self-awareness (что не знает), learning agility. Reference checks критичны.

> [!question]- Какие red flags при интервью на leadership позицию указывают на плохого кандидата?
> Всегда говорит "я" (не "мы"), не может назвать конкретные примеры неудач, blame others за проблемы, не задаёт вопросы о команде/культуре, generic ответы без specifics. Также: не может описать как развивал людей.

---

## Ключевые карточки

Какие компетенции оцениваются на leadership интервью?
?
People management (hiring, coaching, performance), Strategic thinking (vision, prioritization), Organizational design (team structures, processes), Technical judgment (не expertise, а judgment), Communication (executive presence, stakeholder management), Culture building.

Почему reference checks особенно важны для leadership позиций?
?
Leadership skills сложнее оценить за 4-5 часов интервью. References от direct reports (не только peers и managers) дают insight в реальный management style. Вопросы: "Как бы вы описали их стиль?", "Пошли бы за ним снова?".

Как отличить настоящий leadership experience от talk?
?
STAR framework (Situation, Task, Action, Result) с deep probing: "Какие конкретно решения принимал ты?", "Что пошло не так?", "Что бы сделал по-другому?". Настоящий опыт включает mistakes и learnings, не только success stories.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[first-90-days]] | Как онбордить нового лидера |
| Углубиться | [[cto-vs-vpe]] | Различия в оценке CTO vs VP Eng |
| Смежная тема | [[behavioral-interview]] | Техники behavioral интервью |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-02-13*
*Связано с: [[leadership-overview]]*
