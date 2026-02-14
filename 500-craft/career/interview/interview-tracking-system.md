---
title: "Interview Tracking System 2026: templates и отчёты"
created: 2026-01-11
modified: 2026-02-13
type: reference
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/intermediate
  - interview
related:
  - "[[interview-process]]"
  - "[[job-search-strategy]]"
  - "[[ai-interview-preparation]]"
prerequisites:
  - "[[interview-process]]"
  - "[[job-search-strategy]]"
reading_time: 23
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Interview Tracking System 2026

> **TL;DR:** Системный подход к поиску работы = 3x конверсия. Этот гайд содержит готовые шаблоны для трекинга applications, interview stages, preparation и post-mortem анализа. Copy-paste в Notion, Excel или любой tool.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INTERVIEW TRACKING SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  PIPELINE   │ →  │   PREP      │ →  │   DEBRIEF   │                 │
│  │  TRACKER    │    │   SYSTEM    │    │   & LEARN   │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         ↓                 ↓                  ↓                          │
│  • Applications     • Per-company      • Post-interview                 │
│  • Stages           • Per-stage        • Weekly review                  │
│  • Deadlines        • Checklists       • Conversion analysis            │
│  • Status           • Practice log     • Pattern recognition            │
│                                                                          │
│  METRICS TO TRACK:                                                       │
│  ├── Applications sent: [count]                                         │
│  ├── Response rate: [%]                                                 │
│  ├── Phone screen → Onsite: [%]                                        │
│  ├── Onsite → Offer: [%]                                               │
│  └── Average time to offer: [days]                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Application Pipeline Tracker

### Master Tracker Template

```markdown
## 📋 JOB APPLICATION TRACKER

### Quick Stats
| Metric | Value | Target |
|--------|-------|--------|
| Total Applications | 0 | 30-50 |
| Response Rate | 0% | >15% |
| Active Processes | 0 | 5-8 |
| Offers | 0 | 2-3 |

---

### Pipeline

| # | Company | Role | Level | Applied | Status | Next Step | Deadline | Priority | Notes |
|---|---------|------|-------|---------|--------|-----------|----------|----------|-------|
| 1 | [Company] | [Role] | [L5] | [Date] | [Status] | [Action] | [Date] | [H/M/L] | [Notes] |

### Status Legend
- 🟡 Applied - Waiting for response
- 🔵 Recruiter Screen - Scheduled/Completed
- 🟣 Technical Screen - Scheduled/Completed
- 🟢 Onsite - Scheduled/Completed
- ✅ Offer - Received
- ❌ Rejected - At [stage]
- ⏸️ On Hold - Company paused
- ❄️ Ghosted - No response 2+ weeks
```

### Per-Application Card Template

```markdown
## 🏢 [COMPANY NAME]

### Basic Info
| Field | Value |
|-------|-------|
| **Role** | Senior Android Developer |
| **Level** | L5 / E5 / equivalent |
| **Location** | Remote / City |
| **Salary Range** | $X - $Y |
| **Applied Date** | YYYY-MM-DD |
| **Source** | LinkedIn / Referral / Direct |
| **Referrer** | [name if applicable] |

---

### Why This Company
- [ ] Strong product I believe in
- [ ] Tech stack matches goals
- [ ] Growth opportunity
- [ ] Compensation meets target
- [ ] Culture seems good

**My 3-sentence pitch:**
> [Why you want to work here specifically]

---

### Interview Timeline

| Stage | Date | Interviewer | Result | Notes |
|-------|------|-------------|--------|-------|
| Applied | | - | ⏳ | |
| Recruiter Screen | | | | |
| Technical Screen | | | | |
| Onsite Round 1 | | | | |
| Onsite Round 2 | | | | |
| Onsite Round 3 | | | | |
| Team Match | | | | |
| Offer/Reject | | | | |

---

### Research Notes

**Company:**
- Founded:
- Size:
- Funding:
- Recent news:

**Team/Role:**
- Team size:
- Manager:
- Key projects:
- Tech stack:

**Glassdoor Insights:**
- Interview difficulty:
- Common questions:
- Culture notes:

---

### Questions to Ask
1. [ ] What does success look like in 6 months?
2. [ ] What's the biggest challenge the team faces?
3. [ ] How do you measure Android team performance?
4. [ ] What's the path to Staff/Principal?
5. [ ] [Custom question based on research]

---

### Documents
- [ ] Resume tailored for this role
- [ ] Cover letter (if required)
- [ ] Portfolio links prepared
- [ ] References ready
```

---

## Part 2: Stage-Specific Prep Checklists

### Recruiter Screen Checklist

```markdown
## 📞 RECRUITER SCREEN PREP

**Company:** [name]
**Date/Time:** [datetime]
**Duration:** 30 min expected
**Interviewer:** [name, title]

---

### Before Call (24h)
- [ ] Research company (product, news, culture)
- [ ] Review job description
- [ ] Prepare 1-min pitch
- [ ] Salary research for this role/company
- [ ] Prepare 3 questions for recruiter
- [ ] Test video/audio setup

### During Call - Key Points
- [ ] Express genuine interest in company/role
- [ ] Share relevant experience highlights
- [ ] Ask about next steps and timeline
- [ ] Discuss visa/relocation if applicable
- [ ] Note interviewer's name for follow-up

### Questions They'll Ask (Prepare Answers)
1. "Tell me about yourself" → [2-min pitch ready]
2. "Why this company?" → [specific reasons]
3. "Why leave current role?" → [positive framing]
4. "Salary expectations?" → [range ready, deflect if early]
5. "Timeline?" → [when can you start]

### My Questions to Ask
1. What does the interview process look like?
2. How is the Android team structured?
3. What's the timeline for this role?

---

### Post-Call Notes
**Date completed:**
**Duration:**
**Key takeaways:**

**Next steps:**
- [ ] Send thank you email (within 24h)
- [ ] Update tracker status
- [ ] Prepare for next stage
```

### Technical Screen Checklist

```markdown
## 💻 TECHNICAL SCREEN PREP

**Company:** [name]
**Date/Time:** [datetime]
**Duration:** 45-60 min expected
**Interviewer:** [name, title]
**Format:** [CoderPad/HackerRank/Video/AI-enabled]

---

### Before Interview (48h)
- [ ] Review DSA fundamentals
- [ ] Practice 5-10 relevant problems
- [ ] Review company's known question types
- [ ] Practice "think aloud" approach
- [ ] Test coding environment

### Before Interview (2h)
- [ ] Light warm-up problem (easy)
- [ ] Review common patterns
- [ ] Prepare desk/environment
- [ ] Water, notes ready
- [ ] Deep breaths

### During Interview
- [ ] Clarify problem before coding
- [ ] Think aloud throughout
- [ ] Start with brute force, then optimize
- [ ] Test on examples
- [ ] Analyze complexity
- [ ] Ask if time for questions

### Common Technical Topics to Review
- [ ] Arrays/Strings manipulation
- [ ] Hash tables for O(1) lookup
- [ ] Tree traversals (BFS/DFS)
- [ ] Sliding window
- [ ] Two pointers
- [ ] [Company-specific topics]

### If AI-Enabled Interview
- [ ] Practice using AI as assistant
- [ ] Know when to use vs. code yourself
- [ ] Always verify AI output
- [ ] Show your own thinking

---

### Post-Interview Notes
**Problems given:**
1. [problem] - [how I did]
2. [problem] - [how I did]

**What went well:**

**What to improve:**

**Follow-up:**
- [ ] Thank you email
- [ ] Update tracker
- [ ] Practice weak areas identified
```

### System Design Checklist

```markdown
## 🏗️ SYSTEM DESIGN PREP

**Company:** [name]
**Date/Time:** [datetime]
**Duration:** 45-60 min expected
**Interviewer:** [name, title]
**Level:** [Mobile SD / Backend SD / Full-stack]

---

### Before Interview (Week)
- [ ] Review SD fundamentals
- [ ] Practice 3-5 similar problems
- [ ] Review mobile-specific considerations
- [ ] Prepare framework (RESHADED)

### Before Interview (Day)
- [ ] Review common components
- [ ] Practice drawing diagrams
- [ ] Prepare trade-off discussions
- [ ] Review scaling patterns

### Framework Reminder (RESHADED)
```
R - Requirements (5 min)
E - Estimations (3 min)
S - Storage Schema (5 min)
H - High-Level Design (10 min)
A - API Design (5 min)
D - Detailed Deep-Dive (15 min)
E - Evaluate Trade-offs (5 min)
D - Distinctive Additions (2 min)
```

### Mobile SD Specific
- [ ] Offline-first considerations
- [ ] Battery/network optimization
- [ ] Caching strategies (memory/disk)
- [ ] Sync mechanisms
- [ ] Error handling patterns
- [ ] Push notification design

### Components to Know
- [ ] MVVM/MVI architecture
- [ ] Repository pattern
- [ ] Local caching (Room)
- [ ] Network layer (Retrofit)
- [ ] Image loading (Coil/Glide)
- [ ] Pagination

---

### Post-Interview Notes
**Problem given:**

**My approach:**

**Trade-offs discussed:**

**What went well:**

**What to improve:**
```

### Behavioral Interview Checklist

```markdown
## 🗣️ BEHAVIORAL PREP

**Company:** [name]
**Date/Time:** [datetime]
**Duration:** 45-60 min expected
**Interviewer:** [name, title]
**Focus:** [General / Amazon LP / Google Googleyness]

---

### Before Interview (Week)
- [ ] Review 7 STAR stories
- [ ] Practice each story out loud
- [ ] Map stories to company values
- [ ] Research interviewer on LinkedIn

### Before Interview (Day)
- [ ] Re-read company values
- [ ] Select top 5 stories for this company
- [ ] Practice 2-3 aloud

### My STAR Stories Ready

| # | Story | Dimensions Covered | Duration |
|---|-------|-------------------|----------|
| 1 | [brief name] | Leadership, Impact | 2 min |
| 2 | [brief name] | Conflict, Teamwork | 2.5 min |
| 3 | [brief name] | Failure, Learning | 2 min |
| 4 | [brief name] | Ambiguity, Decision | 2 min |
| 5 | [brief name] | Mentoring, Growth | 2 min |
| 6 | [brief name] | Technical, Impact | 2 min |
| 7 | [brief name] | Cross-team, Leadership | 2.5 min |

### Company-Specific Values to Demonstrate
- [ ] [Value 1]: Story ready → [#]
- [ ] [Value 2]: Story ready → [#]
- [ ] [Value 3]: Story ready → [#]

### Questions to Ask Interviewer
1. What do you enjoy most about working here?
2. How does the team handle technical disagreements?
3. What does success look like in this role?

---

### Post-Interview Notes
**Questions asked:**
1. [question] - Story used: [#] - How it went:
2. [question] - Story used: [#] - How it went:

**What went well:**

**What to improve:**

**Follow-up questions I received:**
```

### Onsite Day Checklist

```markdown
## 🎯 ONSITE DAY PREP

**Company:** [name]
**Date:** [date]
**Format:** [Virtual / In-person]
**Duration:** [X hours]
**Rounds:** [list rounds]

---

### Week Before
- [ ] Confirm all logistics
- [ ] Review all prep materials
- [ ] Schedule 2+ mock interviews
- [ ] Research all interviewers
- [ ] Prepare questions for each

### Day Before
- [ ] Light review only (no cramming)
- [ ] Prepare outfit (if in-person)
- [ ] Test all tech (if virtual)
- [ ] Early sleep
- [ ] Pack: laptop, charger, water, notes

### Morning Of
- [ ] Light breakfast
- [ ] 1 easy warm-up problem
- [ ] Review 3 key STAR stories
- [ ] Deep breathing/meditation
- [ ] Arrive early / login early

### During Onsite
- [ ] Stay energized (water, snacks)
- [ ] Each round: fresh start mindset
- [ ] Take brief notes between rounds
- [ ] Ask questions in every round
- [ ] Thank each interviewer

### Virtual Onsite Specifics
- [ ] Camera at eye level
- [ ] Good lighting
- [ ] Quiet environment
- [ ] Backup internet plan
- [ ] Close unnecessary apps

---

### Round-by-Round Notes

**Round 1: [Type]**
- Interviewer:
- Topics:
- How it went:
- Concerns:

**Round 2: [Type]**
- Interviewer:
- Topics:
- How it went:
- Concerns:

[Continue for each round...]

---

### Overall Assessment
**Confidence level:** [1-10]
**Strongest round:**
**Weakest round:**
**Deal-breakers identified:**
**Red flags from company:**
```

---

## Part 3: Post-Interview Debrief Templates

### Interview Debrief Report

```markdown
## 📝 INTERVIEW DEBRIEF REPORT

**Company:** [name]
**Role:** [role]
**Interview Date:** [date]
**Stage:** [Recruiter / Tech Screen / Onsite]

---

### Quick Assessment
| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Technical | | |
| Communication | | |
| Culture Fit | | |
| Problem Solving | | |
| Overall Confidence | | |

**Predicted Outcome:** [ ] Move Forward [ ] Borderline [ ] Likely Reject

---

### What Went Well
1.
2.
3.

### What Could Improve
1.
2.
3.

### Specific Moments to Remember

**Best Moment:**
> [What happened, what you said/did]

**Worst Moment:**
> [What happened, what you should have done]

---

### Questions They Asked

| Question | My Answer Quality (1-5) | Better Answer |
|----------|------------------------|---------------|
| | | |

### My Questions & Their Answers

| My Question | Their Answer | Signal |
|-------------|--------------|--------|
| | | |

---

### Follow-Up Actions
- [ ] Send thank you email (24h)
- [ ] Practice [weak area]
- [ ] Prepare [topic] for next round
- [ ] Research [unanswered question]

---

### For Future Interviews
**What to do again:**

**What to change:**

**New story needed for:**
```

### Weekly Progress Report

```markdown
## 📊 WEEKLY PROGRESS REPORT

**Week of:** [date range]
**Week #:** [X] of job search

---

### Pipeline Summary

| Stage | Count | Change |
|-------|-------|--------|
| Applied | | +/- |
| Recruiter Screen | | +/- |
| Technical Screen | | +/- |
| Onsite | | +/- |
| Offer | | +/- |
| Rejected | | +/- |

### This Week's Activities

| Day | Activity | Result |
|-----|----------|--------|
| Mon | | |
| Tue | | |
| Wed | | |
| Thu | | |
| Fri | | |

### Interviews Completed
1. [Company] - [Stage] - [Outcome/Pending]
2.

### Key Wins
1.
2.

### Challenges
1.
2.

### Practice Stats
- DSA problems solved: [X]
- Mock interviews: [X]
- System design practice: [X hours]

---

### Conversion Analysis

| Funnel Stage | Total | Converted | Rate |
|--------------|-------|-----------|------|
| Applied → Response | | | % |
| Response → Screen | | | % |
| Screen → Onsite | | | % |
| Onsite → Offer | | | % |

**Benchmark:**
- Cold apply: ~2% response
- Referral: ~20% response
- Networking: ~15% response

---

### Next Week Goals
1. [ ]
2. [ ]
3. [ ]

### Blockers / Help Needed
-

---

### Reflection
**Energy level:** [1-10]
**Confidence trend:** [↑/↓/→]
**Biggest learning:**
```

---

## Part 4: Analysis & Patterns

### Rejection Analysis Template

```markdown
## ❌ REJECTION ANALYSIS

**Company:** [name]
**Stage Rejected At:** [stage]
**Date:** [date]
**Feedback Received:** [ ] Yes [ ] No

---

### Feedback Summary
> [paste or summarize feedback if received]

### My Assessment

**Most Likely Cause:**
- [ ] Technical skills gap
- [ ] System design weakness
- [ ] Behavioral concerns
- [ ] Culture mismatch
- [ ] Overqualified/Underqualified
- [ ] Better candidate
- [ ] Unknown

**Specific Weaknesses Exposed:**
1.
2.

---

### Action Items
- [ ] Practice [specific topic]
- [ ] Prepare new story for [dimension]
- [ ] Adjust approach for [situation type]

### Pattern Check
**Have I been rejected at this stage before?** [ ] Yes [ ] No
**Similar feedback pattern?** [ ] Yes [ ] No
**Systemic issue to address?**
```

### Success Pattern Analysis

```markdown
## ✅ OFFER ANALYSIS

**Company:** [name]
**Role:** [role]
**Level:** [level]
**Compensation:** [details]

---

### What Worked

**In Application:**
-

**In Interviews:**
-

**Key Differentiator:**
-

---

### Patterns to Repeat
1.
2.
3.

### Leverage for Negotiation
- Other offers:
- Competing processes:
- Unique value I bring:
```

---

## Part 5: Tools & Integration

### Notion Template Structure

```
📁 Job Search 2026
├── 📋 Pipeline Dashboard
│   ├── All Applications (database)
│   ├── Active Processes (filtered view)
│   └── Stats & Charts
├── 🏢 Companies (linked database)
│   ├── Per-company pages
│   └── Research notes
├── 📝 Prep Materials
│   ├── STAR Stories
│   ├── DSA Patterns
│   └── SD Templates
├── 📊 Weekly Reports
│   └── Weekly notes
└── 📚 Resources
    └── Links, docs
```

### Spreadsheet Formula Examples

```
// Response Rate
=COUNTIF(Status,"Responded")/COUNT(Applications)*100

// Days in Pipeline
=TODAY()-Applied_Date

// Stage Conversion
=COUNTIF(Stage,"Onsite")/COUNTIF(Stage,"Tech Screen")*100

// Target vs Actual
=IF(Actual>=Target,"✅","❌")
```

### Automation Ideas

```
ZAPIER/MAKE WORKFLOWS:

1. New application → Add to tracker
2. Interview scheduled → Create prep checklist
3. Interview completed → Send reminder for debrief
4. Weekly → Generate progress report
5. Offer received → Notify for negotiation prep
```

---

## Metrics Benchmarks

### Healthy Funnel Rates

| Stage | Good | Excellent |
|-------|------|-----------|
| Apply → Response | 10-15% | 20%+ |
| Response → Screen | 50%+ | 70%+ |
| Screen → Onsite | 40%+ | 60%+ |
| Onsite → Offer | 25%+ | 40%+ |
| **End-to-End** | 2-5% | 8%+ |

### Time Benchmarks

| Metric | Typical | Optimized |
|--------|---------|-----------|
| Apply → Response | 1-2 weeks | < 1 week |
| Screen → Onsite | 1-2 weeks | < 1 week |
| Onsite → Decision | 1-2 weeks | < 1 week |
| **Full Process** | 4-8 weeks | 3-5 weeks |

### Activity Benchmarks

| Activity | Weekly Target |
|----------|---------------|
| Applications | 5-10 quality |
| Networking messages | 10-15 |
| DSA problems | 10-15 |
| Mock interviews | 1-2 |
| System Design study | 3-5 hours |

---

## Куда дальше

**Preparation:**
→ [[se-interview-foundation]] — Universal prep
→ [[ai-interview-preparation]] — AI-assisted prep

**Process:**
→ [[interview-process]] — Interview stages
→ [[negotiation]] — Offer negotiation

**Strategy:**
→ [[job-search-strategy]] — Overall approach

---

## Связь с другими темами

- [[interview-process]] — Tracking system из текущего материала накладывается на каждый этап процесса интервью. Pipeline tracker отслеживает прогресс от Applied до Offer, а stage-specific checklists соответствуют раундам из interview-process: Recruiter Screen, Technical Screen, Onsite. Вместе они дают полную систему: знание процесса + инструменты отслеживания.

- [[job-search-strategy]] — Стратегия поиска работы определяет, ЧТО отслеживать (target companies, networking contacts, conversion rates), а tracking system — КАК это делать. Weekly Progress Report из текущего материала помогает итерировать стратегию: если response rate < 10%, нужно улучшить outreach; если onsite → offer < 25%, нужно усилить interview prep.

- [[ai-interview-preparation]] — AI-инструменты интегрируются в tracking system: AI для company research (Phase 1 prep), AI для mock interviews (practice log), AI для post-interview debrief (feedback analysis). Tracking system фиксирует, какие AI-промпты сработали лучше и для каких этапов.

## Источники и дальнейшее чтение

- Burnett B., Evans D. (2016). *Designing Your Life*. — Методология design thinking применима к job search tracking: prototype (подай 5 заявок), test (отследи результаты), iterate (улучши подход). Книга помогает превратить хаотичный поиск в системный эксперимент с метриками.

- McDowell G. L. (2015). *Cracking the Coding Interview*. — Содержит рекомендации по организации подготовки: timeline, checklists, practice schedule. Stage-specific checklists из текущего материала дополняют preparation framework из книги конкретными шаблонами для трекинга.

- Fournier C. (2017). *The Manager's Path*. — Понимание того, как debrief и решения принимаются внутри компаний, помогает правильно интерпретировать rejection analysis. Книга описывает hiring process с perspective hiring manager, что делает post-mortem анализ более точным.

---

## Проверь себя

> [!question]- Почему системный трекинг заявок даёт 3x конверсию по сравнению с хаотичным подходом?
> Трекинг позволяет: 1) выявить bottleneck (на каком этапе теряются заявки), 2) оптимизировать tailoring (какие keywords работают), 3) не забывать follow-up, 4) анализировать rejection patterns. Без данных невозможно улучшить процесс. Метрика: conversion rate по этапам показывает, где инвестировать усилия.

> [!question]- Какие метрики из трекинг-системы помогут определить, что стратегия поиска работы не работает?
> Red flags: 1) Application-to-Response rate < 10% -- проблема с резюме/ATS. 2) Response-to-Interview rate < 30% -- проблема с phone screen. 3) Interview-to-Offer rate < 20% -- проблема с техническими навыками. 4) Среднее время response > 2 недели -- неправильные каналы. Каждый bottleneck требует разной корректировки.

> [!question]- Как организовать post-mortem анализ отказов для улучшения будущих интервью?
> Template: 1) Stage отказа (ATS, phone, onsite round N). 2) Feedback если получен. 3) Self-assessment: что пошло не так. 4) Action items: конкретные улучшения. 5) Timeline: когда внедрить. Группировать по категориям: technical, behavioral, cultural fit. Повторяющиеся паттерны = приоритет для подготовки.

---

## Ключевые карточки

Interview Tracking -- какие поля трекать?
?
Company, Role, Level, Status (Applied/Response/Interview/Offer/Reject), Date applied, Contact person, Source (referral/cold/platform), Notes, Next action, Deadline. Минимум: status + dates + notes.

Conversion funnel -- target rates?
?
Application-to-Response: 15-25% (при tailoring). Response-to-Interview: 40-60%. Interview-to-Offer: 20-30%. Overall: 5-10% applications to offers. Ниже targets = пересмотреть стратегию на соответствующем этапе.

Post-mortem template -- 5 полей?
?
1) Stage отказа. 2) Feedback (если есть). 3) Self-assessment. 4) Action items (конкретные). 5) Timeline внедрения. Группировать по паттернам: technical gaps, behavioral weakness, cultural misfit.

Когда пересматривать стратегию?
?
После каждых 20 заявок анализировать conversion rates. Если Application-to-Response < 10% за 2 недели -- менять резюме. Если 3+ отказа на одном этапе подряд -- фокусная подготовка этого этапа. Weekly review + monthly strategic adjustment.

---

## Куда дальше

| Направление | Тема | Ссылка |
|------------|------|--------|
| Следующий шаг | AI-инструменты для оптимизации поиска | [[ai-era-job-search]] |
| Углубиться | Полный процесс интервью | [[interview-process]] |
| Смежная тема | OKR и метрики в инженерных командах | [[okrs-kpis]] |
| Обзор | Стратегия поиска работы | [[job-search-strategy]] |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
