---
title: "Коммуникация с руководством"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: advanced
target-role: [director, vpe, cto]
teaches:
  - executive summaries
  - board communication
  - presenting to C-level
sources: [pyramid-principle, hbr-communication]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[stakeholder-management]]"
  - "[[crisis-management]]"
prerequisites:
  - "[[stakeholder-management]]"
  - "[[em-fundamentals]]"
  - "[[strategic-thinking]]"
---

# Коммуникация с руководством

> **TL;DR:** Executives have 10 minutes, not 60. Lead with conclusion (Pyramid Principle). No jargon. Business impact, not technical details. BLUF (Bottom Line Up Front). "So what?" for every slide. Prepare for questions, not to present more.

---

## Pyramid Principle (Minto)

```
STRUCTURE:

        ┌─────────────┐
        │ CONCLUSION  │ ← Start here
        └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐
│ Why 1 │ │ Why 2 │ │ Why 3 │ ← Supporting points
└───────┘ └───────┘ └───────┘
    │         │         │
    ▼         ▼         ▼
 Details   Details   Details  ← Only if asked

ANTI-PATTERN (bottom-up):
"We analyzed... then we found... therefore..."
Executive stops listening.

PYRAMID (top-down):
"We should do X because A, B, C.
Here's the evidence for A..."
```

## BLUF: Bottom Line Up Front

```
BAD EMAIL:
"Hi, I've been looking at our infrastructure
costs over the past quarter. We noticed some
trends in EC2 usage and also saw that our
database costs increased. After analyzing
multiple vendors..."

[3 paragraphs later]

"...so we need $50K for migration."

GOOD EMAIL:
"We need $50K to migrate to new infra.
This will save $200K/year.

Background:
• Current costs: $X
• New solution: $Y
• Savings: $Z

Timeline: 2 months
Risk: Low (reversible)

Can we discuss Thursday?"
```

## Presenting to Executives

```
RULES:

1. 10 MINUTES, NOT 60
   Prepare for interruptions.
   Have backup slides, not more slides.

2. START WITH THE ASK
   "I need X. Here's why."

3. BUSINESS IMPACT FIRST
   Revenue, customers, risk — not technology.

4. NO JARGON
   "Latency" → "Page load time"
   "Microservices" → "Independent teams"

5. ANTICIPATE QUESTIONS
   What will they ask?
   Have data ready.

6. BE CONCISE
   "We need to migrate databases."
   Not: "We've been evaluating our current
   database architecture and considering
   several options..."

7. "SO WHAT?" TEST
   For every point: why should they care?
```

## Executive Summary Template

```markdown
## Executive Summary: [Title]

### Recommendation
[One sentence: what you want]

### Business Impact
- [Revenue/cost impact]
- [Customer impact]
- [Risk if we don't do this]

### Key Facts
1. [Most important fact]
2. [Second important fact]
3. [Third important fact]

### Timeline & Resources
- Timeline: [Duration]
- Investment: [Cost/people]
- Dependencies: [What we need]

### Risk Assessment
- Main risk: [Risk and mitigation]

### Decision Needed
[Specific ask: approve/fund/decide by date]

---
[Detailed appendix below for those who want it]
```

## Board Communication

```
BOARD CONTEXT:
• 30-60 min for your topic
• Quarterly cadence
• Non-technical audience
• Want: metrics, risks, strategy

FORMAT:
• Written pre-read (they read ahead)
• Meeting is for discussion, not presentation
• Answer questions, don't re-present

CONTENT:
• Key metrics vs targets
• Major initiatives status
• Risks and mitigations
• Strategic decisions needed
• Team health summary
```

---

## Связь с другими темами

**[[stakeholder-management]]** — Коммуникация с руководством неразрывно связана с управлением stakeholders, поскольку эффективная коммуникация — главный инструмент влияния на стейкхолдеров. Понимание того, что каждый stakeholder хочет услышать (business impact vs technical details), определяет формат и содержание коммуникации. Mapping stakeholders по power/interest матрице помогает выбрать правильную частоту и глубину коммуникации для каждого.

**[[crisis-management]]** — Навыки executive communication критически важны во время кризиса, когда каждое сообщение должно быть максимально чётким и действенным. Pyramid Principle и BLUF формат позволяют быстро донести суть проблемы, текущий статус и необходимые решения до руководства. Умение структурировать escalation updates и post-incident reports — прямое применение принципов коммуникации с руководством.

## Источники и дальнейшее чтение

| Источник | Тип |
|----------|-----|
| Drucker P. (2006) *The Effective Executive: The Definitive Guide to Getting the Right Things Done* | Книга |
| Fournier C. (2017) *The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change* | Книга |
| Horowitz B. (2014) *The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers* | Книга |

---

*Последнее обновление: 2026-01-18*
