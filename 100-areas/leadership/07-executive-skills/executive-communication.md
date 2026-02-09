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

## Связанные темы

- [[stakeholder-management]] — who you're communicating with
- [[strategic-thinking]] — what to communicate
- [[communication/]] — communication fundamentals

## Источники

| Источник | Тип |
|----------|-----|
| [The Pyramid Principle](https://www.amazon.com/Pyramid-Principle-Logic-Writing-Thinking/dp/0273710516) | Book |
| [HBR: Executive Communication](https://hbr.org/topic/subject/communication) | Articles |

---

*Последнее обновление: 2026-01-18*
