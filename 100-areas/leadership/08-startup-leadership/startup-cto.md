---
title: "CTO в стартапе"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: advanced
target-role: [cto, founder, technical-cofounder]
teaches:
  - startup CTO role evolution
  - technical cofounder responsibilities
  - build vs buy decisions
sources: [startup-cto-handbook, first-round-review, a16z]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[cto-vs-vpe]]"
  - "[[technical-vision]]"
  - "[[scaling-from-zero]]"
---

# CTO в стартапе

> **TL;DR:** Startup CTO ≠ Big Company CTO. Early stage: 80% coding, 20% everything else. Role evolves dramatically as company grows. Key: know when to stop coding and start leading. Technical cofounder = business partner, not just engineer.

---

## CTO Role Evolution

```
STAGE 1: PRE-SEED / SEED (1-5 people)
┌─────────────────────────────────────────────┐
│ CODING: 80-90%                              │
│ • Build MVP yourself                        │
│ • Make all technical decisions              │
│ • Set up infrastructure                     │
│                                             │
│ OTHER: 10-20%                               │
│ • Investor technical diligence              │
│ • Hiring first engineers                    │
│ • Product discussions with CEO              │
└─────────────────────────────────────────────┘

STAGE 2: SERIES A (5-20 people)
┌─────────────────────────────────────────────┐
│ CODING: 40-60%                              │
│ • Critical features only                    │
│ • Architecture decisions                    │
│ • Code review                               │
│                                             │
│ MANAGEMENT: 30-40%                          │
│ • Hiring and onboarding                     │
│ • Process establishment                     │
│ • Team structure                            │
│                                             │
│ STRATEGY: 10-20%                            │
│ • Technical roadmap                         │
│ • Build vs buy                              │
│ • Vendor selection                          │
└─────────────────────────────────────────────┘

STAGE 3: SERIES B+ (20-50+ people)
┌─────────────────────────────────────────────┐
│ CODING: 0-20%                               │
│ • Prototypes only                           │
│ • Emergency fixes                           │
│                                             │
│ LEADERSHIP: 50-60%                          │
│ • Hiring leaders                            │
│ • Organization design                       │
│ • Culture and values                        │
│                                             │
│ STRATEGY: 30-40%                            │
│ • Technical vision                          │
│ • Board/investor relations                  │
│ • Partnerships                              │
└─────────────────────────────────────────────┘
```

## Technical Cofounder Responsibilities

```
BEYOND CODING:

PRODUCT:
• Translate business needs → technical solutions
• Say "no" to infeasible features
• Propose technical differentiators
• Understand user problems deeply

BUSINESS:
• Investor meetings (technical credibility)
• Customer calls (technical sales)
• Partnership discussions
• Due diligence preparation

TEAM:
• Hiring first engineers (crucial!)
• Setting engineering culture
• Technical mentorship
• Retention of key people

OPERATIONS:
• Budget for tech (cloud, tools)
• Security and compliance
• Incident response
• Vendor management

COFOUNDER RELATIONSHIP:
• Regular sync with CEO
• Disagree and commit
• Unified front to team
• Trust and transparency
```

## Early Stage Decisions

```
BUILD vs BUY:

BUILD WHEN:
✓ Core differentiator
✓ No good solution exists
✓ Integration too complex
✓ Long-term cost advantage

BUY WHEN:
✓ Commodity functionality
✓ Not your expertise
✓ Time-to-market critical
✓ Vendor does it better

COMMON MISTAKES:
✗ Building auth system (use Auth0, Clerk)
✗ Building payment (use Stripe)
✗ Building email (use SendGrid)
✗ Building analytics (use Amplitude, Mixpanel)

TECHNOLOGY CHOICES:

PRINCIPLES:
• Boring technology preferred
• Speed > perfection
• Hire-ability matters
• Cloud-native from start

COMMON STACK (2024-2025):
Frontend: React/Next.js, TypeScript
Backend: Node.js, Python, Go
Database: PostgreSQL, Redis
Cloud: AWS, GCP, or Vercel
Infra: Terraform, Docker, K8s (later)
```

## MVP Development

```
MVP MINDSET:

GOAL: Learn, not ship perfect product

PRINCIPLES:
• Smallest thing that tests hypothesis
• Manual before automated
• Fake it before you make it
• Launch embarrassingly early

TIMELINE:
4-8 weeks for initial MVP
Not 6 months of "foundation"

TECHNICAL DEBT:
✓ Acceptable: messy code, no tests
✓ Acceptable: manual processes
✗ Unacceptable: security shortcuts
✗ Unacceptable: data integrity issues

WHAT TO SKIP:
• Comprehensive testing (some critical paths only)
• Perfect architecture
• Scalability (until you need it)
• Admin tools (do it manually)

WHAT NOT TO SKIP:
• Basic security (auth, encryption)
• Data backups
• Monitoring (basic)
• Deployment automation (basic)
```

## Hiring First Engineers

```
FIRST 5 HIRES:

PROFILE:
• Generalists, not specialists
• Self-directed, low management
• Comfortable with ambiguity
• High ownership mentality
• Can ship end-to-end

RED FLAGS:
• "That's not my job"
• Needs detailed specs
• Only worked at big companies
• Uncomfortable with messy code

WHERE TO FIND:
• Your network first
• Former colleagues
• Angel List / Wellfound
• Twitter/X tech community
• Local meetups

COMPENSATION:
• Below market salary
• Significant equity (0.5-2% for early)
• Explain equity clearly
• 4-year vest, 1-year cliff standard

INTERVIEW FOCUS:
• Can they ship?
• Will they thrive in chaos?
• Do they care about the problem?
• Culture fit with founders?
```

## Founder Dynamics

```
CTO + CEO RELATIONSHIP:

HEALTHY PATTERNS:
• Weekly 1-on-1 (minimum)
• Disagree in private, united in public
• Clear decision rights
• Mutual respect

WARNING SIGNS:
• Avoiding hard conversations
• Blaming each other to team
• Misaligned on priorities
• Trust erosion

COMMON CONFLICTS:
• Speed vs quality
• Technical debt tolerance
• Hiring standards
• Resource allocation

RESOLUTION:
• Data over opinions
• Time-bound experiments
• External advisors
• Written agreements

WHEN CTO SHOULD PUSH BACK:
• Unrealistic timelines
• Security shortcuts
• Hiring wrong people fast
• Scope creep without resources
```

## Technical Due Diligence (Receiving End)

```
WHAT INVESTORS CHECK:

CODE:
• Architecture overview
• Code quality (samples)
• Tech debt assessment
• Security practices

TEAM:
• CTO background
• Team composition
• Hiring pipeline
• Key person risk

PROCESS:
• Deployment frequency
• Incident history
• Development workflow
• Documentation

INFRASTRUCTURE:
• Scalability path
• Cost structure
• Vendor dependencies
• Disaster recovery

HOW TO PREPARE:
• Architecture diagram (1-pager)
• Tech debt list (honest)
• Metrics dashboard
• Security checklist completed
• Clean code samples ready
```

## When to Stop Coding

```
SIGNS IT'S TIME:

• You're the bottleneck
• PRs wait for your review
• Team blocked on your decisions
• Hiring suffering
• Strategy neglected

TRANSITION APPROACH:

MONTH 1:
Identify what only you can do.
Start delegating everything else.

MONTH 2:
Find technical lead to own day-to-day.
You: architecture, hiring, strategy.

MONTH 3:
Stop committing to main.
Prototypes and experiments only.

EMOTIONAL CHALLENGES:
• Identity shift (I'm not coding!)
• Feeling useless
• Missing the flow state
• Imposter syndrome

COPING:
• Personal projects (weekends)
• Stay close to tech (reviews, design)
• Find fulfillment in team success
• Talk to other CTOs
```

---

## Связанные темы

- [[cto-vs-vpe]] — role comparison
- [[technical-vision]] — setting direction
- [[founding-engineer]] — first hire perspective
- [[scaling-from-zero]] — growth challenges

## Источники

| Источник | Тип |
|----------|-----|
| [The Startup CTO's Handbook](https://github.com/ZachGoldberg/Startup-CTO-Handbook) | Book |
| [First Round Review](https://review.firstround.com/) | Blog |
| [a16z](https://a16z.com/tag/engineering/) | Blog |

---

*Последнее обновление: 2026-01-18*
