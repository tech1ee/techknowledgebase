---
title: "Планирование бюджета"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: advanced
target-role: [director, vpe, cto]
prerequisites:
  - "[[strategic-thinking]]"
teaches:
  - headcount planning
  - opex vs capex
  - budget justification
unlocks:
  - "[[executive-communication]]"
tags: [leadership, budget, finance, planning, headcount]
sources: [cfo-partnership, engineering-budgets]
---

# Планирование бюджета

> **TL;DR:** Budget = план в деньгах. Headcount обычно 70-80% engineering budget. Know the difference: CapEx (capital, depreciates) vs OpEx (operating, immediate expense). Justify investment with ROI. Work with Finance — they're partners, not gatekeepers.

---

## Budget Components

```
ENGINEERING BUDGET:

HEADCOUNT (70-80%):
• Salaries
• Benefits
• Bonuses
• Contractors

TOOLS & INFRASTRUCTURE (15-20%):
• Cloud (AWS, GCP, Azure)
• SaaS tools (GitHub, Jira, etc.)
• Licenses
• Hardware

OTHER (5-10%):
• Training/conferences
• Recruiting fees
• Travel
• Office/remote stipends
```

## Headcount Planning

```
BOTTOM-UP APPROACH:
1. What projects/initiatives planned?
2. How many people needed for each?
3. What roles (IC, manager, specialist)?
4. What seniority mix?
5. When needed?

TOP-DOWN APPROACH:
1. Revenue target
2. Engineering as % of revenue
3. Available budget
4. How to allocate

TYPICAL RATIOS:
• Revenue per engineer: $200K-$500K+
• Engineer:PM ratio: 5-10:1
• Engineer:Designer: 5-15:1
• Manager:IC: 1:5-8

BACKFILL vs NET NEW:
• Backfill: replace departures
• Net new: growth
• Plan for ~10-15% attrition
```

## CapEx vs OpEx

```
CapEx (Capital Expenditure):
• Long-term assets (>1 year)
• Depreciated over time
• Example: servers, major software build
• Tax treatment: spread over years

OpEx (Operating Expenditure):
• Day-to-day costs
• Immediate expense
• Example: SaaS subscriptions, cloud
• Tax treatment: deduct this year

WHY IT MATTERS:
Finance cares about the split.
Some companies prefer CapEx (asset on books).
Others prefer OpEx (flexibility).
Ask Finance for preference.
```

## Budget Justification

```
FOR HEADCOUNT:
"2 engineers for project X will deliver
feature Y by Q3, expected to generate
$500K ARR. ROI: 5x salary cost."

FOR TOOLS:
"Tool X costs $50K/year. Saves 2 hours/week
per developer. 50 developers × 2 hours ×
$100/hour × 50 weeks = $500K saved."

FOR INFRASTRUCTURE:
"Current spend: $X. With optimization: $Y.
Investment in platform team: $Z.
Net savings: $X - $Y - $Z over 2 years."

ALWAYS INCLUDE:
• Business impact (revenue, cost savings)
• Alternatives considered
• Risk of not investing
• Timeline to value
```

## Annual Planning Process

```
TYPICAL TIMELINE:

Q3 (AUGUST-SEPTEMBER):
• Finance sends templates
• Top-down targets shared
• Departments draft requests

Q4 (OCTOBER-NOVEMBER):
• Reviews and negotiations
• Trade-offs discussed
• Final allocation

Q1:
• Budget finalized
• Hiring plans activated
• Quarterly check-ins

TIPS:
• Start early
• Build relationships with Finance
• Have backup plans (what if -20%?)
• Document assumptions
```

## Working with Finance

```
DO:
✓ Learn finance language (ROI, EBITDA, etc.)
✓ Provide data they need
✓ Be transparent about risks
✓ Propose alternatives
✓ Meet deadlines

DON'T:
✗ Surprise them
✗ Pad requests expecting cuts
✗ Ignore their constraints
✗ Be adversarial
```

---

## Связанные темы

- [[strategic-thinking]] — budget follows strategy
- [[executive-communication]] — presenting to leadership
- [[scaling-engineering-org]] — growth planning

## Источники

| Источник | Тип |
|----------|-----|
| [CFO Partnership](https://hbr.org/topic/subject/finance) | HBR |
| [SaaS Metrics](https://www.saastr.com/) | Blog |

---

*Последнее обновление: 2026-01-18*
