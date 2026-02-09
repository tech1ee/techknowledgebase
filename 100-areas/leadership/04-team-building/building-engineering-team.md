---
title: "Строительство инженерной команды"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, cto, founder]
teaches:
  - team composition
  - growth stages
  - building from scratch
sources: [managers-path, elegant-puzzle, first-round-review]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[hiring-engineers]]"
  - "[[em-fundamentals]]"
  - "[[team-culture]]"
  - "[[scaling-engineering-org]]"
---

# Строительство инженерной команды

> **TL;DR:** Команда — не коллекция инженеров, а система с emergent properties. Оптимальный размер: 5-8 человек. Разнообразие (skills, experience, perspectives) важнее однородности. First hires определяют culture надолго. Building ≠ hiring — это creating условий для collaboration, trust и psychological safety.

---

## Зачем это нужно?

### Типичная ситуация

Стартап растёт. Нужно нанять 5 инженеров быстро. Нанимают похожих людей — "culture fit". Через год: все думают одинаково, нет diverse perspectives, senior engineers конкурируют вместо collaboration, juniors не развиваются.

**Без intentional team building:**
- Случайная композиция
- Skill gaps и redundancies
- Culture проблемы
- High turnover
- Slow delivery

**С правильным подходом:**
- Complementary skills
- Diverse perspectives
- Strong culture
- High retention
- 5x productivity

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| High-performing teams vs average | 5x more productive | Google Research |
| Team diversity impact on innovation | +35% | McKinsey |
| Optimal team size | 5-8 | Amazon, research |
| First 5 hires determine culture for | 3-5 years | First Round |

---

## Модели команды

### Team Composition Framework

```
┌─────────────────────────────────────────────────────────────────┐
│              OPTIMAL TEAM COMPOSITION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SIZE: 5-8 people (Two-pizza rule)                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  < 5: Not enough capacity, single points of failure             │
│  > 8: Communication overhead increases exponentially            │
│                                                                 │
│  SKILL MIX:                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  ┌────────────────────────────────────────────┐                 │
│  │ 1-2 Senior (tech lead, architecture)       │                 │
│  │ 3-4 Mid (core execution)                   │                 │
│  │ 1-2 Junior (fresh perspectives, growth)    │                 │
│  └────────────────────────────────────────────┘                 │
│                                                                 │
│  ROLES COVERAGE:                                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  □ Frontend specialists                                         │
│  □ Backend specialists                                          │
│  □ Full-stack generalists                                       │
│  □ Infrastructure/DevOps                                        │
│  □ Domain experts (if needed)                                   │
│                                                                 │
│  DIVERSITY DIMENSIONS:                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│  • Experience level (junior to senior)                          │
│  • Background (FAANG, startups, bootcamp)                       │
│  • Thinking style (creative vs structured)                      │
│  • Demographics (gender, ethnicity, etc.)                       │
│  • Timezone (if distributed)                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Team Topology Types

```
STREAM-ALIGNED TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aligned to business stream/product.
End-to-end ownership.

Best for: Product delivery
Example: "Checkout team" owns entire checkout flow

ENABLING TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Helps other teams adopt new capabilities.
Temporary engagement.

Best for: Capability uplift
Example: "Platform team" helps teams adopt K8s

COMPLICATED SUBSYSTEM TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Owns technically complex subsystem.
Requires deep specialist knowledge.

Best for: Complex domains
Example: "ML platform" team

PLATFORM TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provides internal services.
Treats other teams as customers.

Best for: Shared capabilities
Example: "Developer experience" team
```

---

## Stages of Team Building

### Stage Model

```
STAGE 1: FOUNDING (0-3 people)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Characteristics:
• Everyone does everything
• No formal process
• Direct communication
• Move fast

Focus:
• Ship product
• Find product-market fit
• Establish core culture

Team needs:
• Generalists
• Self-starters
• Comfortable with ambiguity

STAGE 2: GROWING (4-8 people)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Characteristics:
• Specialization emerges
• Need some process
• Communication still direct
• One team feeling

Focus:
• Scale delivery
• Establish practices
• Build culture intentionally

Team needs:
• Mix of generalists and specialists
• Some senior for mentorship
• EM (or tech lead) emerges

STAGE 3: SCALING (9-20 people)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Characteristics:
• Multiple sub-teams
• Process necessary
• Communication overhead
• Culture at risk of dilution

Focus:
• Team boundaries
• Coordination mechanisms
• Culture documentation
• Management layer

Team needs:
• Clear leadership
• Specialists by area
• Strong senior bench

STAGE 4: MATURE (20+ people)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Characteristics:
• Multiple teams
• Formal processes
• Cross-team coordination
• Culture institutionalized

Focus:
• Organizational design
• Career paths
• Scale efficiency

Team needs:
• Management hierarchy
• Staff+ engineers
• Dedicated HR/recruiting
```

---

## Пошаговый процесс

### Building from Zero (First 5 Hires)

**Шаг 1: Define Culture Foundation**
```
BEFORE FIRST HIRE, DEFINE:
□ Core values (3-5)
□ Working style (async vs sync, remote vs office)
□ Decision-making approach
□ Communication norms
□ Quality bar

Example values:
• Ownership: Own it end-to-end
• Transparency: Default to open
• Iteration: Ship fast, learn fast
• Excellence: High bar, not perfectionism
```

**Шаг 2: First Hire — Set the Tone**
```
FIRST HIRE CRITERIA:
□ Technical excellence
□ Culture setter (will attract similar)
□ Self-directed
□ Can wear many hats
□ Will challenge you constructively

⚠️ WARNING:
First hire defines culture more than
any document. Choose very carefully.
```

**Шаг 3: Build Complementary Team**
```
HIRE 2-5: Fill gaps, add diversity

AVOID: 5 copies of hire #1
DO: Complementary skills and perspectives

Example mix:
• #1: Strong backend, experienced
• #2: Strong frontend, mid-level
• #3: Full-stack, junior but high potential
• #4: Infrastructure/DevOps leaning
• #5: Senior generalist, leadership potential
```

**Шаг 4: Establish Norms Early**
```
BY HIRE #5, DOCUMENT:
□ Code review process
□ On-call expectations
□ Meeting cadence
□ Communication tools and norms
□ Definition of done
□ Incident response

"Culture is what happens when no one
is watching. Define it early."
```

### Growing an Existing Team

**Шаг 1: Assess Current State**
```
TEAM HEALTH CHECK:
□ Skill coverage (gaps?)
□ Experience distribution
□ Turnover patterns
□ Engagement signals
□ Delivery metrics
□ Team dynamics (collaboration?)
```

**Шаг 2: Identify Gaps**
```
SKILL MAP:
| Skill       | Current | Needed | Gap |
|-------------|---------|--------|-----|
| Frontend    | 2       | 3      | +1  |
| Backend     | 3       | 3      | 0   |
| DevOps      | 0       | 1      | +1  |
| Leadership  | 1       | 2      | +1  |

EXPERIENCE MAP:
| Level  | Current | Target | Gap |
|--------|---------|--------|-----|
| Junior | 3       | 2      | -1  |
| Mid    | 2       | 4      | +2  |
| Senior | 1       | 2      | +1  |
```

**Шаг 3: Plan Hiring Sequence**
```
PRIORITIZE:
1. Critical skill gaps (blocking work)
2. Leadership gaps (senior mentorship)
3. Capacity gaps (just need more people)
4. Future needs (preparing for growth)

DON'T: Hire juniors without seniors to mentor
DO: Build senior bench before scaling juniors
```

---

## Team Dynamics

### Tuckman's Stages

```
FORMING → STORMING → NORMING → PERFORMING

FORMING:
• Polite, getting to know each other
• Looking to leader for direction
• Unclear roles
• Low productivity

Manager role: Provide clear direction

STORMING:
• Conflict emerges
• Roles challenged
• Frustration normal
• Still low productivity

Manager role: Facilitate conflict resolution

NORMING:
• Norms established
• Roles clarified
• Collaboration begins
• Productivity increasing

Manager role: Reinforce positive behaviors

PERFORMING:
• High collaboration
• Self-organizing
• High productivity
• Continuous improvement

Manager role: Remove obstacles, celebrate wins
```

### Psychological Safety

```
GOOGLE'S PROJECT ARISTOTLE:
#1 predictor of team effectiveness: Psychological Safety

DEFINITION:
"Belief that one can speak up without risk of
punishment or humiliation."

SIGNS OF SAFETY:
✓ People ask questions
✓ Mistakes are discussed openly
✓ New ideas welcomed
✓ Constructive disagreement
✓ People admit "I don't know"

SIGNS OF UNSAFETY:
✗ Silence in meetings
✗ Mistakes hidden
✗ Ideas shot down
✗ Blame culture
✗ Fear of speaking up

HOW TO BUILD:
• Leader models vulnerability
• Thank people for speaking up
• Handle mistakes constructively
• Encourage dissent
• Celebrate questions
```

---

## Скрипты и Templates

### Team Charter Template

```markdown
# Team [Name] Charter

## Mission
[Why this team exists — one sentence]

## Scope
**We own:**
- [Service/feature 1]
- [Service/feature 2]

**We don't own:**
- [Out of scope]

## Team Members
| Name | Role | Skills | Timezone |
|------|------|--------|----------|
| | | | |

## Ways of Working

### Communication
- Primary: [Slack channel]
- Async by default. Sync for [what]
- Response time: [expectations]

### Meetings
| Meeting | Frequency | Who | Purpose |
|---------|-----------|-----|---------|
| Standup | Daily | All | Sync |
| Planning | Weekly | All | Sprint plan |
| Retro | Bi-weekly | All | Improve |

### Decision Making
- Technical: [How decisions made]
- Process: [How process changes happen]

### On-Call
[Rotation, expectations, escalation]

## Definition of Done
- [ ] Code reviewed
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] Product sign-off

## Values
1. [Value with explanation]
2. [Value with explanation]
3. [Value with explanation]

## Success Metrics
- [Metric 1]
- [Metric 2]

---
*Last updated: [Date]*
*Team lead: [Name]*
```

### First Team Meeting Agenda

```
PURPOSE: Align new team on mission and ways of working

AGENDA (60-90 min):

1. WELCOME (10 min)
   - Introduce yourself
   - Why this team, why now

2. MISSION (15 min)
   - What we're building
   - Why it matters
   - Success looks like...

3. TEAM INTRODUCTIONS (20 min)
   Each person: background, skills, fun fact
   What they want from this team

4. WAYS OF WORKING (15 min)
   - Communication norms
   - Meeting cadence
   - Decision making
   Collaborative input welcomed

5. IMMEDIATE PRIORITIES (15 min)
   - Next 30 days
   - First milestones

6. Q&A (15 min)
   - Open discussion
   - Concerns, ideas

FOLLOW-UP:
Send summary and team charter draft for feedback
```

### Hiring Priority Matrix

```markdown
# Team [Name] Hiring Priorities

## Current Team
[List current members and roles]

## Skill Assessment
| Skill | Coverage | Urgency | Priority |
|-------|----------|---------|----------|
| Frontend | 1/3 needed | High | P0 |
| Backend | 3/3 needed | Low | - |
| DevOps | 0/1 needed | High | P0 |

## Hiring Sequence
1. **[Role]** — [Why urgent]
2. **[Role]** — [Why needed]
3. **[Role]** — [Nice to have]

## Hiring Timeline
Q1: [Role 1]
Q2: [Role 2]
Q3: [Role 3]

## Budget Status
Approved headcount: X
Current: Y
Open: Z
```

---

## Распространённые ошибки

### Ошибка 1: Hiring Clones

**Как выглядит:**
All same background, same thinking style.
"Great culture fit!" = "Thinks like us"

**Почему это проблема:**
- Groupthink
- Missed perspectives
- Less innovation
- Harder to attract diverse talent later

**Как исправить:**
```
INTENTIONAL DIVERSITY:
• Different backgrounds (FAANG, startup, bootcamp)
• Different strengths (creative vs systematic)
• Different perspectives (junior, international)

Question to ask:
"Who will challenge our assumptions?"
```

### Ошибка 2: Too Junior, Too Fast

**Как выглядит:**
Hire 5 juniors because cheaper.
One senior can mentor them all, right?

**Почему это проблема:**
- Insufficient mentorship capacity
- Quality suffers
- Senior burns out
- Juniors don't develop properly

**Как исправить:**
```
RATIO RULE:
1 senior : 2-3 mid/junior MAX

BUILD SENIOR BENCH FIRST:
1. Senior engineer
2. Mid-level
3. Junior
4. Mid-level
5. Senior (or strong mid)

Then scale with ratio maintained.
```

### Ошибка 3: No Team Identity

**Как выглядит:**
People work together but no shared identity.
Just a collection of individuals.

**Почему это проблема:**
- No collaboration beyond necessary
- Low ownership
- People leave easily
- Fragmented culture

**Как исправить:**
```
BUILD IDENTITY:
□ Clear team name and mission
□ Team rituals (not just meetings)
□ Shared wins celebrated
□ Team goals (not just individual)
□ Casual team time
```

---

## Когда применять разные подходы

### Small Team (3-5)

```
FOCUS ON:
• Generalists over specialists
• Direct communication
• Minimal process
• Strong individual contributors
• Flexible roles

SKIP:
• Formal structure
• Heavy process
• Manager/IC separation
```

### Medium Team (6-10)

```
FOCUS ON:
• Clear tech lead
• Basic processes
• Some specialization
• Defined ownership areas
• Regular rituals

ADD:
• 1-on-1s
• Planning meetings
• Documentation
```

### Large Team (10+)

```
FOCUS ON:
• Split into sub-teams
• EM needed (separate from TL)
• Cross-team coordination
• Career development
• Scalable processes

ADD:
• Multiple tech leads
• Clear team boundaries
• Formal roadmap
```

---

## Связанные темы

### Prerequisites
- [[hiring-engineers]] — how to hire
- [[em-fundamentals]] — manager role

### Следующие шаги
- [[team-culture]] — culture building
- [[team-dynamics]] — team psychology
- [[onboarding]] — welcoming new members

### Связи с другими разделами
- [[scaling-engineering-org]] — multi-team
- [[career/]] — growth paths

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Team Topologies](https://teamtopologies.com/) | Book | Team types |
| 2 | [Google's Project Aristotle](https://rework.withgoogle.com/guides/understanding-team-effectiveness/) | Research | Psychological safety |
| 3 | [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) | Book | Team building stages |
| 4 | [An Elegant Puzzle](https://www.amazon.com/Elegant-Puzzle-Systems-Engineering-Management/dp/1732265186) | Book | Scaling teams |
| 5 | [First Round Review](https://review.firstround.com/) | Articles | First hires |

---

*Последнее обновление: 2026-01-18*
*Связано с: [[leadership-overview]]*
