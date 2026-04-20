# Requirements Gathering & User Interviewing — Deep Research

> Compiled 2026-04-02 | 30+ sources | Focus: actionable techniques for CLI-based AI assistant

---

## 1. Requirements Elicitation Techniques

### 1.1 Jobs-to-be-Done (JTBD)

**Framework**: Uncover what "job" the user is hiring the software to do.

**Template**:
```
When [situation], I want to [motivation], so I can [expected outcome].
```

**Universal Job Map Steps** (each step has desired outcomes to capture):
1. Define — what the user needs to accomplish
2. Locate — find inputs needed
3. Prepare — set up for execution
4. Confirm — verify readiness
5. Execute — perform the core task
6. Monitor — check progress
7. Modify — make adjustments
8. Conclude — finish and clean up

**CLI Application**: Ask "What are you trying to accomplish?" before "What feature do you want?" Forces problem-first thinking.

**Sources**:
- [JTBD Framework - Tony Ulwick](https://jobs-to-be-done.com/jobs-to-be-done-a-framework-for-customer-needs-c883cbf61c90)
- [JTBD Guide - Product School](https://productschool.com/blog/product-fundamentals/jtbd-framework)
- [JTBD Practical Guide - The Product Space](https://theproductspace.substack.com/p/jobs-to-be-done-framework-a-practical)

### 1.2 Impact Mapping (Gojko Adzic)

**4-Level Structure**:
```
WHY (Goal) → WHO (Actors) → HOW (Impacts) → WHAT (Deliverables)
```

**Question Sequence**:
1. "Why are we doing this? What business goal does it serve?"
2. "Who are the actors that can influence this goal?"
3. "How should their behavior change? What impact do we want?"
4. "What can we deliver to create that impact?"

**CLI Application**: Use as the opening interview structure — drill from goal to deliverables.

**Sources**:
- [Impact Mapping Official](https://www.impactmapping.org/)
- [Impact Mapping Example - Draft.io](https://draft.io/example/impact-mapping)

### 1.3 User Story Mapping (Jeff Patton)

**Structure**:
```
Backbone (Activities) → left-to-right narrative flow
    ↓
Steps (Tasks under each activity)
    ↓
Details (User stories, variations, edge cases)
```

**6-Step Process**:
1. Frame the problem — who is it for and why
2. Map the big picture — breadth, not depth
3. Explore — other users, edge cases
4. Slice out a release strategy
5. Slice out a learning strategy
6. Slice out a development strategy

**Walking Skeleton**: The top row = minimal end-to-end functionality.

**CLI Application**: Build the backbone first via broad questions, then drill into each activity.

**Sources**:
- [Jeff Patton Story Mapping](https://www.jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf)
- [Avion Story Mapping Guide](https://www.avion.io/what-is-user-story-mapping/)

### 1.4 Prioritization Frameworks

#### MoSCoW
```
Must Have   — critical to viability, non-negotiable
Should Have — important but not immediately critical
Could Have  — nice to have, not necessary
Won't Have  — explicitly excluded (this release)
```
Best for: quick scope alignment, MVP definition, cross-functional convergence.

#### RICE Scoring
```
Score = (Reach × Impact × Confidence) / Effort

Reach      = users affected per time period (use real metrics)
Impact     = 3 (massive), 2 (high), 1 (medium), 0.5 (low), 0.25 (minimal)
Confidence = 100%, 80%, 50% (high/medium/low)
Effort     = person-months
```
Best for: data-driven teams comparing many features.

#### Kano Model
```
Must-Be        — expected, absence = dissatisfaction
Performance    — more is better, linear satisfaction
Attractive     — unexpected delight, absence ≠ dissatisfaction
Indifferent    — no impact on satisfaction
Reverse        — presence = dissatisfaction
```
Best for: discovery phase, understanding emotional value.

#### Integrated Approach
Use Kano during discovery → RICE to score shortlist → MoSCoW to finalize release scope.

**Sources**:
- [Prioritization Guide - AltexSoft](https://www.altexsoft.com/blog/most-popular-prioritization-techniques-and-methods-moscow-rice-kano-model-walking-skeleton-and-others/)
- [Prioritization Frameworks - Atlassian](https://www.atlassian.com/agile/product-management/prioritization-framework)
- [Feature Prioritization - Plane](https://plane.so/blog/feature-prioritization-frameworks-rice-moscow-and-kano-explained)

---

## 2. Interview Question Frameworks

### 2.1 The "Starting Five" Questions

These 5 questions open any requirements conversation effectively:

1. **"What pain points are we trying to alleviate?"**
   - Follow-up: Who experiences this pain? Why does this problem exist?

2. **"What would happen if we don't build this?"**
   - Reveals true urgency and priority

3. **"How would you define success for this project?"**
   - Follow-up: How would you quantify it? What's the single most important outcome?

4. **"Who will be most excited to see this launched?"**
   - Identifies key stakeholders and beneficiaries

5. **"Is there anything else you think I should know that we haven't covered?"**
   - Catches everything the structured questions missed

**Source**: [Practical Analyst - Most Valuable Questions](https://practicalanalyst.com/requirements-elicitation-most-valuable-questions/)

### 2.2 The W-Framework (Who/What/When/Where/Why/How)

60 questions organized by dimension:
- **WHO**: Primary stakeholders? Hidden stakeholders? End users vs. buyers?
- **WHAT**: What problem? What types of requirements? Solutions vs. requirements?
- **WHEN**: When in lifecycle? Priority order? Deadlines?
- **WHERE**: Which platforms? Environments? Regions?
- **WHY**: Business justification? Cost of not doing?
- **HOW**: Integration? Migration? Deployment?

**Source**: [W-Framework - 60 Questions](https://thebusinessanalystjobdescription.com/requirements-gathering-interview-questions/)

### 2.3 Follow-Up Question Taxonomy (7 Types)

Research-backed taxonomy for generating follow-up questions:

| Type | Purpose | Context Needed | Example |
|------|---------|---------------|---------|
| **Topic Change** | Switch to unrelated topic | 0 turns | "Let's talk about authentication now." |
| **Answer Probing** | Dig deeper into what was said | 1 turn | "You mentioned caching — what invalidation strategy?" |
| **Confirmation** | Verify understanding | 1 turn | "So if I understand correctly, you want X?" |
| **Question Probing** | Ask about missing concepts in scope | 2+ turns | "We discussed reads but not writes — how should writes work?" |
| **Alternative-Seeking** | Explore other options | 2+ turns | "What other approaches have you considered?" |
| **Preference-Seeking** | Get yes/no on a specific option | 2+ turns | "Would batch processing be acceptable here?" |
| **Clarification** | Resolve ambiguity | 1 turn | "When you say 'fast', what response time do you mean?" |

**Key Finding**: 98% of follow-up questions need only 4 prior turns of context maximum.

**Source**: [Follow-Up Question Generation - arXiv](https://arxiv.org/html/2507.02858)

### 2.4 The 5 Whys Technique

Ask "Why?" up to 5 times to drill from symptom to root cause:

```
Problem: "We need a dashboard"
Why? → "To track order status"
Why? → "Customers keep calling about orders"
Why? → "They can't see status in the current system"
Why? → "The notification system is unreliable"
Why? → "Emails fail silently with no retry"

Root requirement: Fix notification reliability, not build a dashboard.
```

**CLI Application**: When user states a feature request, ask "Why do you need this?" recursively.

### 2.5 INVEST Criteria for User Stories

Every user story should be:
- **I**ndependent — no coupling to other stories
- **N**egotiable — not a fixed contract
- **V**aluable — delivers value to user or business
- **E**stimable — can estimate effort
- **S**mall — fits in one iteration
- **T**estable — has clear pass/fail criteria

**CLI Application**: Validate each captured requirement against INVEST before finalizing.

### 2.6 Given-When-Then (BDD Acceptance Criteria)

```
Given [precondition / initial context]
When  [action / event occurs]
Then  [expected outcome 1]
And   [expected outcome 2]
```

Example:
```
Given a logged-in user with items in cart
When  they click "Checkout" with an expired card
Then  show error "Card expired, please update payment method"
And   preserve cart contents
And   log the failed payment attempt
```

**CLI Application**: Generate acceptance criteria in this format for every requirement captured.

---

## 3. Gap Analysis Methods

### 3.1 Hidden Gap Categories

Gaps are not missing requirements — they are **missing considerations within existing ones**:

| Gap Type | What It Catches | Example Question |
|----------|----------------|-----------------|
| **Assumption Gap** | Unstated beliefs | "What assumptions are we making about user behavior?" |
| **Edge Case Gap** | Unusual but valid scenarios | "What happens with zero items? 10,000 items? Special characters?" |
| **Integration Gap** | System boundaries | "What happens when the API fails? Timeout? Retry?" |
| **Performance Gap** | Scale scenarios | "How many concurrent users? What's peak load?" |
| **Security Gap** | Threat vectors | "Who should NOT have access? What data is sensitive?" |
| **Error State Gap** | Failure modes | "What happens when X fails? How does user recover?" |
| **Temporal Gap** | Time-related issues | "What about timezone differences? Daylight saving? Leap years?" |
| **Data Gap** | Data lifecycle | "How long is data retained? What about deletion? GDPR?" |

**Source**: [Ticking Minds - Hidden Requirements Gaps](https://www.tickingminds.com/uncovering-hidden-requirements-gaps-the-technical-breakdown/)

### 3.2 Non-Functional Requirements Checklist

**MUST probe each category for every feature:**

| Category | Key Questions | Example Metric |
|----------|--------------|----------------|
| **Performance** | Response time? Throughput? | P95 latency < 200ms at 10 RPS |
| **Scalability** | Max concurrent users? Growth rate? | Handles 10x current load |
| **Availability** | Uptime requirement? Maintenance windows? | 99.9% uptime |
| **Reliability** | MTBF? MTTR? Data loss tolerance? | Recovers < 10 min |
| **Security** | Auth method? Data encryption? Compliance? | PCI DSS, HIPAA, GDPR |
| **Accessibility** | WCAG level? Screen reader support? | WCAG 2.2 AA |
| **Portability** | OS? Browser? Device? | iOS 16+, Android 12+ |
| **Compatibility** | Legacy systems? Data migration? | Backwards compatible 2 versions |
| **Maintainability** | Code standards? Documentation? | Deploy in < 1 hour |
| **Observability** | Logging? Metrics? Alerting? | Structured logs, dashboards |
| **Offline** | Offline capability? Sync strategy? | Works offline, syncs on reconnect |
| **Localization** | Languages? RTL? Date/currency formats? | EN, ES, AR (RTL) |

**Sources**:
- [Non-Functional Requirements - AltexSoft](https://www.altexsoft.com/blog/non-functional-requirements/)
- [NFR Examples - Perforce](https://www.perforce.com/blog/alm/what-are-non-functional-requirements-examples)
- [NFR Guide - BrowserStack](https://www.browserstack.com/guide/non-functional-requirements-examples)

### 3.3 "What Happens When..." Probe Template

For every feature, systematically ask:

```
What happens when...
├── the user has NO data?              (empty state)
├── the user has TOO MUCH data?        (pagination/performance)
├── the input is invalid?              (validation)
├── the input contains special chars?  (injection/encoding)
├── the network is slow/offline?       (resilience)
├── the API returns an error?          (error handling)
├── the user cancels mid-operation?    (state management)
├── two users do it simultaneously?    (concurrency)
├── the user is unauthorized?          (access control)
├── the data is stale/cached?          (consistency)
├── the user does it on mobile?        (responsive)
├── the user uses a screen reader?     (accessibility)
├── the session expires mid-task?      (auth recovery)
├── the feature is accessed for first time? (onboarding)
└── the operation partially fails?     (transaction/rollback)
```

### 3.4 The "Exception Path" Method

For every happy path, identify:
1. **Business exceptions** — "We always do X except when..."
2. **Technical exceptions** — timeouts, rate limits, capacity
3. **User exceptions** — accidental actions, unusual workflows
4. **External exceptions** — third-party failures, regulatory changes

**Source**: [Requirement Gathering Checklist - Manifestly](https://www.manifest.ly/use-cases/software-development/requirement-gathering-checklist)

---

## 4. Requirements Documentation Standards

### 4.1 PRD Template (Product Requirements Document)

```markdown
# PRD: [Feature Name]

## Change History
| Date | Author | Change |
|------|--------|--------|

## 1. Problem & Goal
- What problem are we solving?
- Who has this problem?
- Why now?
- Success metrics (measurable)

## 2. Users & Roles
| Role | Goals | Top Actions | Pain Points |
|------|-------|-------------|-------------|

## 3. User Journeys (top 3, prioritized)
Journey 1: [Name]
Step 1 → Step 2 → Step 3 → ...

## 4. Feature List (Prioritized)
### MVP (Must Have)
- FR-01: [Feature] — [Why]
### Phase 2 (Should Have)
- FR-05: [Feature] — [Why]
### Phase 3 (Could Have)
- FR-09: [Feature] — [Why]

## 5. Scope Boundaries
### In Scope
- ...
### Out of Scope
- ...

## 6. Non-Functional Requirements
- Performance: ...
- Security: ...
- Scalability: ...

## 7. Assumptions & Open Questions
- Assumption: ...
- Open: ...

## 8. Designs
[Link to wireframes/mockups]

## 9. Release Plan
- Milestones
- QA approach
- Rollback strategy
```

**Sources**:
- [PRD + SRS Template 2026](https://codeloomtechnologies.com/blogs/prd-srs-requirements-template-2026/)
- [PRD Template - Product School](https://productschool.com/blog/product-strategy/product-template-requirements-document-prd)
- [PRD Template - Inflectra](https://www.inflectra.com/Ideas/Topic/PRD-Template.aspx)

### 4.2 SRS Functional Requirement Format

```markdown
## FR-01: [Feature Name]
- **Description**: [What it does]
- **Inputs**: [What goes in]
- **Outputs**: [What comes out]
- **Business Rules**: [Logic/constraints]
- **Error States**: [What can go wrong]
- **Acceptance Criteria**:
  - Given [context] When [action] Then [result]
  - Given [context] When [action] Then [result]
```

### 4.3 ADR Template (Architecture Decision Record)

```markdown
# ADR-XXX: [Decision Title]

**Status**: Draft | In Discussion | Decided | Superseded
**Date**: YYYY-MM-DD
**Authors**: [names]

## Context
[Brief explanation of the need/problem]

## Decision
[One-sentence decision]

## Rationale
- [Reason 1]
- [Reason 2]

## Consequences
- [Expected outcome]
- [Second-order effect]

## Alternatives Considered
| Option | Pros | Cons | Why Rejected |
|--------|------|------|-------------|

## References
- [links]
```

### 4.4 RFC Template (Request for Comments)

```markdown
# RFC-XXX: [Title]

**Status**: Draft | Collecting Feedback | Accepted | Rejected
**Authors**: [names]
**Feedback Deadline**: YYYY-MM-DD

## Need
[Detailed problem with examples]

## Proposed Approach
[Detailed solution methodology]

## Pros & Cons
| Pros | Cons |
|------|------|

## Alternatives
| Option | Description | Trade-offs |
|--------|-------------|-----------|

## Open Questions
- [Question 1]

## References
- [links]
```

**Source**: [ADRs and RFCs - Candost's Blog](https://candost.blog/adrs-rfcs-differences-when-which/)

### 4.5 User Story Format

```
As a [role],
I want to [action],
So that [benefit].

Acceptance Criteria:
- Given [context] When [action] Then [result]

Notes:
- [Edge cases, constraints]
```

Validate against INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.

---

## 5. Progressive Disclosure in Interviews

### 5.1 Breadth First, Depth Later

**Principle**: Cover all areas at a shallow level before going deep on any one.

**Phase 1 — Broad Discovery** (understand the landscape):
- "Tell me about the overall goal of this project"
- "Who are the main users?"
- "What are the core workflows?"
- "What systems does this interact with?"

**Phase 2 — Identify Boundaries** (minimal viable scope):
- "Which of these workflows is most critical?"
- "What must be in the first release vs. later?"
- Apply MoSCoW to everything discussed

**Phase 3 — Deep Dive** (selected areas only):
- Take each Must-Have feature and drill:
  - Happy path → Edge cases → Error states → NFRs
- Generate acceptance criteria for each
- Validate with "What happens when..." probes

**Source**: [Jama Software - Requirements Elicitation Guide](https://www.jamasoftware.com/requirements-management-guide/requirements-gathering-and-management-processes/a-guide-to-requirements-elicitation-for-product-teams/)

### 5.2 The Funnel Technique

```
WIDE:  "What is the overall purpose of this system?"
  ↓
       "Who are the main user groups?"
  ↓
       "What are the core workflows for [user group]?"
  ↓
       "Walk me through [specific workflow] step by step"
  ↓
       "What happens when [specific step] fails?"
  ↓
NARROW: "What exact error message should appear?"
```

### 5.3 Progressive Elaboration Sequence

For a CLI assistant interviewing a developer:

**Round 1 — Context Setting** (2-3 questions):
1. "What are you building?" (goal)
2. "Who is it for?" (users)
3. "What problem does it solve?" (JTBD)

**Round 2 — Scope Mapping** (3-5 questions):
4. "What are the main features/workflows?"
5. "What's the MVP vs. nice-to-have?" (MoSCoW)
6. "What constraints exist?" (time, tech, budget)
7. "What existing systems does it integrate with?"

**Round 3 — Feature Deep-Dive** (per feature):
8. "Walk me through the happy path"
9. "What happens when things go wrong?" (error states)
10. "What are the edge cases?"
11. Generate acceptance criteria (Given-When-Then)

**Round 4 — NFR Sweep** (systematic):
12. "What performance is expected?"
13. "What security requirements exist?"
14. "What about offline/accessibility/i18n?"

**Round 5 — Validation**:
15. "Let me summarize what I've captured — is this correct?"
16. "What did I miss?"
17. "What's the riskiest assumption we're making?"

### 5.4 The 20 Tips for Elicitation

Key actionable tips from Inflectra's research:

1. Include diverse stakeholders
2. Meet quiet participants one-on-one
3. Listen actively — don't interrupt, don't lead
4. Drill down on disagreements
5. Keep asking "Why?" — be persistent
6. Allow tangential discussions (they reveal conflicts)
7. Distinguish needs from wants
8. Capture non-functional requirements explicitly
9. Break down complex problems (the breakdown itself is revealing)
10. Clarify ALL jargon — eliminate it if possible
11. Don't organize too formally at the start (constrains thinking)
12. Stress-test processes: "Under what conditions would this break?"
13. When users describe solutions, redirect to problems
14. Space out meetings — give time to think between sessions
15. Compare stories from multiple users — discuss discrepancies
16. Hypothesize extreme conditions and discuss resolutions

**Source**: [20 Tips - Inflectra](https://www.inflectra.com/Ideas/Entry/20-tips-for-effective-requirements-elicitation-294.aspx)

---

## 6. Anti-Patterns

### 6.1 The Big 10 Mistakes

| # | Anti-Pattern | Description | Fix |
|---|-------------|-------------|-----|
| 1 | **Vague Objectives** | "User-friendly", "fast", "scalable" without metrics | Require specific measurable criteria: "P95 < 200ms" |
| 2 | **Limited Stakeholders** | Only talking to 1-2 people | Include end users, ops, QA, compliance, support |
| 3 | **NFRs as Afterthought** | 48% of projects fail on performance because NFRs are skipped | Probe NFRs for every feature systematically |
| 4 | **Uncontrolled Scope** | No formal change management | Lock scope baseline, assess impact of every change |
| 5 | **Poor Documentation** | "Sentence fragments" as requirements | Use structured templates (PRD, SRS, user stories) |
| 6 | **Define by Absence** | "Not like the last one" — no positive requirements | Use 5 Whys to find root cause, define what TO build |
| 7 | **Mirror Image** | Copy competitor without differentiation | Apply Kano model, find unique value |
| 8 | **Fear of Feedback** | Building in isolation | Involve users continuously, prototype early |
| 9 | **Feature Overload** | Too many features, no prioritization | Apply MoSCoW, RICE, or Kano |
| 10 | **Agile Misconception** | "Requirements are always fluid" = no baseline | Establish freeze points, use change control |

### 6.2 Cognitive Biases in Requirements

| Bias | Effect | Mitigation |
|------|--------|-----------|
| **Confirmation** | Seek evidence supporting preferred solution | Use Six Thinking Hats, require dissenting views |
| **Anchoring** | First idea dominates all discussion | Collect ideas independently before discussing |
| **Availability** | Recent events get disproportionate focus | Use systematic checklists, not memory |
| **Overconfidence** | Skip reviews, optimistic timelines | Require external review, add uncertainty buffers |
| **Groupthink** | Suppress dissent for harmony | Anonymous feedback, rotate facilitators |

### 6.3 Interview-Specific Anti-Patterns

- **Leading questions**: "Don't you think we should use microservices?" → ask "What architecture would best serve these requirements?"
- **Accepting first answer**: Always probe deeper with "Why?" and "What else?"
- **Solution-jumping**: User says "Add a button" → ask "What are you trying to accomplish?"
- **Assuming shared understanding**: Always clarify jargon, paraphrase back
- **Asking multiple questions at once**: One question per turn, wait for answer
- **Not documenting decisions**: Record WHY a decision was made, not just WHAT

**Sources**:
- [Requirements Management Mistakes - Aqua Cloud](https://aqua-cloud.io/common-requirements-management-mistakes/)
- [5 Common Mistakes - Data Panda](https://www.data-panda.com/post/common-mistakes-during-requirements-gathering)
- [Requirements Gathering Mistakes - Requiment](https://www.requiment.com/common-requirements-gathering-and-management-mistakes-and-how-to-avoid-them/)

---

## 7. AI-Assisted Requirements Gathering

### 7.1 LLMREI — LLM-Based Requirements Elicitation Interviews

**Key Research Finding**: LLM chatbots can conduct requirements elicitation interviews at comparable quality to trained human interviewers.

**Architecture**: GPT-4o via chat interface, no human mediation during interview.

**Two Prompting Strategies**:

1. **Zero-Shot (short prompt)**: Minimal instruction — "You are an interviewer who elicits requirements." Results in more creative, context-enhancing questions (10-15% novel suggestions).

2. **Structured (long prompt)**: Incorporates interview best practices with 5-step structured process. Results in more consistent, systematic coverage.

**Question Generation Distribution**:
- 27-28% context-independent (standard opening/closing)
- 13-29% parametrized (basic contextual insertion)
- 32-44% context-deepening (follow-ups from prior answers)
- 10-15% context-enhancing (novel suggestions)

**Performance**: Short prompt extracted 60.94% of requirements fully + 12.76% partially (73.7% total). Comparable error rate to human interviewers.

**Key Design Principles**:
- One question at a time (never batch)
- Role-based framing prevents assistant-like behavior
- Adaptive termination when user signals time pressure
- Best used as preliminary tool — human analyst refines output

**Source**: [LLMREI - arXiv](https://arxiv.org/html/2507.02564v1)

### 7.2 Multi-Agent Requirements System

**4-Agent Architecture**:
1. **Product Owner Agent** — generates user stories from descriptions
2. **QA Agent** — validates against INVEST + ISO 29148
3. **Senior Developer Agent** — assesses technical feasibility
4. **Manager Agent** — synthesizes prioritization

**Workflow**: Generate stories → Quality check → Prioritize (using 100 Dollar Allocation, WSJF, AHP)

**Finding**: 100 Dollar Allocation was most consistent across models.

**Source**: [Multi-Agent RE - arXiv](https://arxiv.org/html/2409.00038v1)

### 7.3 LLM Error Prevention in Interviews

14 mistake criteria to avoid (from follow-up question generation research):

**Follow-up mistakes**:
- Tacit assumptions (assuming something not stated)
- Not exploring alternatives
- Not asking for clarification on ambiguity
- Not probing for tacit knowledge

**Question framing mistakes**:
- Generic/vague questions
- Questions too long
- Using jargon the user may not know
- Technical language when unnecessary
- Inappropriate scope (too broad or narrow)

**Source**: [Follow-Up Question Generation - arXiv](https://arxiv.org/html/2507.02858)

### 7.4 Practical LLM Integration for a CLI Assistant

Based on all research, the optimal approach for a CLI-based AI requirements gatherer:

1. **Use structured prompting** with role-based framing
2. **Follow breadth-first, depth-later** — map all features before drilling any
3. **One question at a time** — never batch questions
4. **Track coverage** — use NFR checklist + gap categories to know what's been asked
5. **Generate follow-ups** from the 7-type taxonomy (probe, confirm, clarify, etc.)
6. **Validate with user** — paraphrase back frequently (confirmation type)
7. **Output structured docs** — PRD, user stories with Given-When-Then, acceptance criteria
8. **Flag gaps** — systematically check "What happens when..." for every feature
9. **Apply INVEST** — validate each story before finalizing
10. **Prevent anti-patterns** — avoid leading questions, solution-jumping, assuming understanding

---

## 8. Master Checklist for CLI Requirements Interview

### Phase 1: Context (2-3 min)
- [ ] What are you building?
- [ ] Who is it for?
- [ ] What problem does it solve?
- [ ] What happens if we don't build it?

### Phase 2: Scope (5-10 min)
- [ ] What are the main features/workflows?
- [ ] What's MVP vs. later?
- [ ] What existing systems does it integrate with?
- [ ] What constraints exist (time, tech, budget)?
- [ ] What's explicitly out of scope?

### Phase 3: Feature Deep-Dive (per feature, 5-10 min each)
- [ ] Happy path walkthrough
- [ ] Error states / failure modes
- [ ] Edge cases (empty, max, invalid, concurrent)
- [ ] Acceptance criteria (Given-When-Then)
- [ ] User role / permission differences

### Phase 4: NFR Sweep (5-10 min)
- [ ] Performance requirements
- [ ] Security / authentication
- [ ] Scalability expectations
- [ ] Availability / uptime
- [ ] Accessibility (WCAG)
- [ ] Offline behavior
- [ ] Localization / i18n
- [ ] Observability (logging, monitoring)
- [ ] Data retention / privacy / compliance

### Phase 5: Gap Analysis (3-5 min)
- [ ] "What happens when..." probe for each feature
- [ ] Assumption identification
- [ ] Integration failure scenarios
- [ ] Temporal edge cases
- [ ] Data lifecycle questions

### Phase 6: Validation (2-3 min)
- [ ] Summarize back to user
- [ ] "What did I miss?"
- [ ] "What's the riskiest assumption?"
- [ ] Prioritize final list (MoSCoW)

### Output
- [ ] PRD with all sections filled
- [ ] User stories with acceptance criteria
- [ ] NFR specifications with metrics
- [ ] Open questions / assumptions documented
- [ ] Scope boundaries explicit

---

## Key Statistics

- **39%** of project failures caused by poor requirements (PMI)
- **78%** of project failures trace to poor requirements handling
- **48%** of ICT projects have performance issues from overlooked NFRs (Gartner)
- **10-100x** cost difference between catching issues early vs. post-deployment
- **73.7%** of requirements extractable by LLM-based interviewer (LLMREI study)
- **98%** of follow-up questions need only 4 prior turns of context
