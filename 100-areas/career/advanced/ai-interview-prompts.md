---
title: "AI Interview Prompts Library: 100+ готовых промптов"
created: 2026-01-11
modified: 2026-01-11
type: reference
status: published
confidence: high
tags:
  - topic/career
  - topic/interview
  - topic/ai
  - topic/prompts
  - type/reference
related:
  - "[[ai-interview-preparation]]"
  - "[[ai-era-job-search]]"
  - "[[se-interview-foundation]]"
---

# AI Interview Prompts Library

> **TL;DR:** 100+ готовых промптов для каждого этапа подготовки к интервью. Copy-paste и используй. Промпты оптимизированы для Claude, GPT-4, и Gemini.

---

## Quick Index

| Category | Prompts | Jump |
|----------|---------|------|
| Resume | 15 | [→](#resume--linkedin) |
| Company Research | 10 | [→](#company-research) |
| DSA Practice | 20 | [→](#dsa-practice) |
| System Design | 15 | [→](#system-design) |
| Behavioral | 15 | [→](#behavioral-interview) |
| Android Specific | 15 | [→](#android-specific) |
| Mock Interview | 10 | [→](#mock-interview) |

---

## Resume & LinkedIn

### Resume Analysis

```
Analyze my resume for a [ROLE] position at [COMPANY]:

JOB DESCRIPTION:
[paste JD]

MY RESUME:
[paste resume]

Provide:
1. ATS compatibility score (1-10) with explanation
2. Top 5 missing keywords from JD
3. Bullets that need metrics
4. Red flags a recruiter might see
5. Specific improvements for each section
```

### Bullet Point Rewrite

```
Rewrite this resume bullet to be more impactful:

ORIGINAL: "[your bullet]"

CONTEXT:
- Role applying for: [role]
- Actual metric achieved: [metric]
- Team size: [number]
- Business impact: [impact]

Requirements:
1. Start with strong action verb
2. Include specific number/metric
3. Show business impact
4. Under 100 characters
5. No weak words (helped, assisted, various)

Give me 3 options ranked by impact.
```

### Resume Tailoring

```
I'm applying to [COMPANY] for [ROLE].

JOB DESCRIPTION:
[paste JD]

MY KEY EXPERIENCES:
1. [experience 1]
2. [experience 2]
3. [experience 3]

How should I tailor my resume?
1. Which keywords to add?
2. Which experiences to emphasize?
3. What to remove or minimize?
4. Suggested skills section order?
5. Any gaps I should address in cover letter?
```

### LinkedIn Headline

```
Create 5 LinkedIn headline options:

Current: [current role]
Target: [target role]
Key skills: [skills]
Differentiator: [what makes you unique]

Requirements:
- Max 120 characters each
- Include searchable keywords
- Show value proposition
- No clichés (passionate, rockstar)
- Professional but memorable
```

### LinkedIn Summary

```
Write a LinkedIn summary:

ABOUT ME:
- Years of experience: [X]
- Current focus: [technologies/domain]
- Career goal: [target role/company type]
- Unique achievement: [your differentiator]

FORMAT:
- 3 short paragraphs
- First line = hook
- Include 5-7 keywords naturally
- End with what I'm looking for
- Professional but with personality
```

### Achievement Quantification

```
Help me quantify this achievement:

ACHIEVEMENT: [describe what you did]

CONTEXT:
- Team size: [X]
- Timeline: [duration]
- Available metrics: [what you can measure]

Generate 3 ways to express this with numbers:
1. Impact on business (revenue, users, time)
2. Scale (size, volume, complexity)
3. Improvement (before/after comparison)
```

---

## Company Research

### Deep Dive

```
I have an interview at [COMPANY] for [ROLE].

Research and provide:
1. Company Overview
   - What they do (1-2 sentences)
   - Size, funding stage, key products

2. Recent News (last 6 months)
   - Product launches
   - Funding, acquisitions
   - Leadership changes

3. Tech Stack
   - Known technologies
   - Engineering blog highlights

4. Culture Signals
   - Values from website
   - Glassdoor themes
   - Interview process reputation

5. Questions I Should Ask
   - 3 thoughtful questions based on research
   - 2 role-specific questions
```

### Predict Interview Questions

```
Based on this job description, predict interview questions:

JOB DESCRIPTION:
[paste JD]

COMPANY: [name]
ROLE LEVEL: [Junior/Mid/Senior/Staff]

Predict:
1. 5 technical questions (based on required skills)
2. 3 system design topics (if senior+)
3. 5 behavioral questions (aligned with company values)
4. 2 "why us" questions
5. Curveball question they might ask

For each, give a brief note on how to prepare.
```

### Interviewer Research

```
Help me prepare for an interview with [INTERVIEWER NAME].

THEIR LINKEDIN: [paste or summarize]
THEIR ROLE: [title]
COMPANY: [company]

Provide:
1. Their likely focus areas based on role
2. Topics they might care about
3. Common ground I could mention
4. Questions I could ask them specifically
5. Potential red flags to avoid
```

### Glassdoor Analysis

```
Summarize these Glassdoor interview reviews for [COMPANY]:

REVIEWS:
[paste key excerpts]

Extract:
1. Common interview questions
2. Process description (rounds, duration)
3. Difficulty level assessment
4. What candidates say went well
5. What candidates say went poorly
6. Red flags about the company
```

---

## DSA Practice

### Problem Understanding

```
I need to solve this problem:

PROBLEM:
[paste problem statement]

Help me understand (WITHOUT solving it):
1. What are the key constraints?
2. What pattern category does this fall into?
3. What clarifying questions should I ask?
4. What edge cases should I consider?
5. Expected optimal complexity?
6. Similar problems to reference?
```

### Solution Explanation

```
I solved this problem. Please review:

PROBLEM: [brief description]

MY SOLUTION:
[paste code]

MY ANALYSIS:
- Time: O(?)
- Space: O(?)

Please:
1. Verify my complexity analysis
2. Identify bugs or edge cases I missed
3. Suggest optimizations
4. Show alternative approaches
5. Rate my solution quality (1-10)
```

### Pattern Deep Dive

```
Teach me the [PATTERN NAME] pattern:

1. Recognition signals (when to use)
2. Template/pseudocode to memorize
3. 3 example problems with brief solutions
4. Common mistakes with this pattern
5. Related patterns (and how they differ)
6. Time/space complexity typical for this pattern

Use simple examples with clear explanations.
```

### Complexity Analysis Practice

```
Analyze the complexity of this code:

[paste code]

For each significant operation:
1. What is its complexity?
2. How many times is it executed?

Final analysis:
- Time complexity: O(?)
- Space complexity: O(?)
- Explanation of how you derived it
```

### Edge Case Generator

```
For this problem type: [describe problem]

Generate comprehensive edge cases:
1. Empty input
2. Single element
3. All same elements
4. Maximum size input
5. Negative numbers (if applicable)
6. Duplicates
7. Already sorted / reverse sorted
8. Special characters (if string)
```

### Mock DSA Interviewer

```
Act as a coding interviewer at [COMPANY].

Give me a [EASY/MEDIUM/HARD] problem about [TOPIC].

Rules:
1. Present the problem clearly
2. Wait for my solution
3. Ask follow-up questions
4. Give hints if I'm stuck (but don't solve)
5. After my solution, provide detailed feedback

Start with the problem.
```

---

## System Design

### Requirements Clarification

```
I'm practicing system design for: "Design [SYSTEM]"

What clarifying questions should I ask?

Organize by:
1. Functional requirements questions
2. Non-functional requirements questions
3. Scale estimation questions
4. Constraints questions

For each question, provide a typical answer for a 45-min interview scope.
```

### Design Review

```
Review my system design for [PROBLEM]:

MY DESIGN:
[describe architecture]

COMPONENTS:
[list main components]

DATA FLOW:
[describe how data moves]

Evaluate:
1. Missing critical components?
2. Scalability bottlenecks?
3. Single points of failure?
4. Trade-offs to discuss?
5. Where should I dive deeper?
6. Questions an interviewer would ask?
```

### Component Explanation

```
Explain [COMPONENT] for system design interviews:

1. What it is (1-2 sentences)
2. When to use it (3-5 scenarios)
3. Key decisions/trade-offs
4. Popular technologies for it
5. How to discuss in interview (sample script)
6. Common follow-up questions
```

### Trade-off Discussion

```
I'm designing [SYSTEM] and need to choose between:

OPTION A: [describe]
OPTION B: [describe]

Help me discuss trade-offs:
1. When to choose A over B
2. When to choose B over A
3. Key metrics that influence choice
4. How to present this in interview
5. Sample dialogue with interviewer
```

### Mobile SD Specific

```
I'm designing [MOBILE APP FEATURE].

Mobile-specific considerations to address:
1. Offline support strategy
2. Battery optimization
3. Network handling (slow, unreliable)
4. Local storage approach
5. Sync mechanism
6. Error handling patterns
7. Performance targets (startup, scroll)

For each, provide approach and trade-offs.
```

---

## Behavioral Interview

### STAR Story Builder

```
Help me build a STAR story for: "[QUESTION]"

MY RAW EXPERIENCE:
[describe what happened briefly]

Build:
S - Situation (2-3 sentences, set context)
T - Task (what was MY specific responsibility)
A - Action (3-5 specific things I did)
R - Result (quantified outcome)

Also provide:
- How to make result more impactful
- Likely follow-up questions
- 1-minute condensed version
```

### Story Bank Mapping

```
I need to prepare behavioral stories. Here are my experiences:

1. [experience brief]
2. [experience brief]
3. [experience brief]
4. [experience brief]
5. [experience brief]

Map to these dimensions:
1. Leadership
2. Conflict Resolution
3. Failure/Learning
4. Teamwork
5. Ambiguity
6. Impact/Achievement
7. Mentoring

Identify:
- Which stories cover which dimensions
- Gaps where I need more stories
- Stories that could cover multiple dimensions
```

### Amazon LP Alignment

```
I'm preparing for Amazon. Here's my experience:

[describe experience]

Align to Amazon Leadership Principles:
1. Which LP does this best demonstrate?
2. How to frame the story for that LP?
3. What details to emphasize?
4. What to avoid saying?
5. LP conflicts to be aware of?
```

### Story Improvement

```
Here's my STAR story. Improve it:

CURRENT STORY:
S: [situation]
T: [task]
A: [action]
R: [result]

Make it better:
1. Strengthen the result with metrics
2. Add more "I" instead of "we"
3. Make actions more specific
4. Add impact statement
5. Shorten to 2 minutes max
```

### Behavioral Mock Interviewer

```
Act as a [COMPANY] behavioral interviewer.

Ask me a behavioral question about [DIMENSION].

After my answer:
1. Score STAR completeness (1-5)
2. Check for "I" vs "we" usage
3. Assess result quantification
4. Ask one probing follow-up
5. Provide improvement suggestions
```

### Weakness Question

```
Help me answer: "What's your biggest weakness?"

MY ACTUAL WEAKNESS: [honest weakness]

Create an answer that:
1. Is honest but not disqualifying
2. Shows self-awareness
3. Demonstrates improvement actions
4. Relates to the role positively
5. Avoids cliché answers
```

---

## Android Specific

### Technical Deep Dive

```
Explain [ANDROID TOPIC] for a Senior interview:

Structure:
1. What it is (concise definition)
2. How it works internally
3. When to use (and when not to)
4. Common pitfalls
5. Best practices
6. Interview question variations
7. Sample answer for "Explain [topic]"
```

### Code Review

```
Review this Android/Kotlin code:

[paste code]

Evaluate:
1. Correctness
2. Kotlin best practices
3. Android best practices
4. Performance implications
5. Thread safety
6. Memory leak potential
7. Suggested improvements
```

### Architecture Question

```
I'm asked: "[ARCHITECTURE QUESTION]"

Example: "Explain MVVM vs MVI trade-offs"

Provide:
1. Concise answer (2 min version)
2. Deep dive answer (5 min version)
3. Code example if applicable
4. When to recommend each
5. Follow-up questions to expect
```

### Compose Internals

```
Explain [COMPOSE CONCEPT] for interview:

Example: "How does recomposition work?"

Cover:
1. High-level explanation
2. Internal mechanism
3. Performance implications
4. Common mistakes
5. How to demonstrate knowledge
6. Sample code to discuss
```

### Android Mock Questions

```
Generate 10 Senior Android interview questions about [TOPIC]:

Topics: Lifecycle, Compose, Coroutines, Architecture, Performance

For each question:
1. The question itself
2. Key points to cover in answer
3. Depth expected for Senior level
4. Follow-up question interviewer might ask
```

---

## Mock Interview

### Full Loop Simulation

```
Simulate a 45-minute interview for [ROLE] at [COMPANY].

Structure:
1. 5 min: Intro & background review
2. 25 min: Technical (coding or design)
3. 10 min: Behavioral
4. 5 min: My questions for you

Act as the interviewer. Start with intro.
After each section, provide brief feedback.
At the end, give:
- Hire / No Hire recommendation
- Detailed strengths
- Areas to improve
- Scores by dimension
```

### Interview Scoring

```
Score my interview performance:

QUESTIONS & MY ANSWERS:
[paste Q&A]

Score each dimension (1-5):
1. Technical Accuracy
2. Problem-Solving Process
3. Communication Clarity
4. Code Quality (if applicable)
5. Time Management
6. Questions Asked

Overall assessment:
- Would you hire? Why/why not?
- Top 3 strengths demonstrated
- Top 3 areas to improve
- Specific actionable feedback
```

### Post-Interview Analysis

```
Analyze my interview experience:

COMPANY: [name]
ROLE: [role]
STAGE: [which round]

WHAT HAPPENED:
[describe the interview]

MY CONCERNS:
[what you're worried about]

Provide:
1. Objective performance assessment
2. What likely went well
3. Potential red flags
4. Likelihood of advancement
5. How to prepare for next round
6. What to improve for future interviews
```

### Feedback Interpretation

```
I received this interview feedback:

[paste feedback or describe]

Help me understand:
1. What this feedback really means
2. What they liked
3. What concerned them
4. Is this a rejection or borderline?
5. How to improve based on this
6. What to work on before next interview
```

---

## Negotiation

### Offer Analysis

```
Analyze this job offer:

OFFER:
- Base: [amount]
- Equity: [amount/vesting]
- Bonus: [amount]
- Benefits: [list]
- Other: [sign-on, relocation, etc.]

CONTEXT:
- My current comp: [amount]
- Market rate: [if known]
- Location: [city/remote]
- Other offers: [if any]

Provide:
1. Total compensation calculation
2. Comparison to market rate
3. Red flags in the offer
4. Negotiation leverage points
5. Suggested counter-offer strategy
```

### Counter-Offer Script

```
Help me negotiate this offer:

CURRENT OFFER: [details]
MY TARGET: [what I want]
LEVERAGE: [other offers, current comp, etc.]

Create:
1. Email template for counter-offer
2. Phone script for negotiation call
3. Responses to common pushbacks
4. Walk-away points
5. Non-salary items to negotiate
```

---

## Quick Reference

### Model-Specific Tips

| Model | Best For | Prompt Tips |
|-------|----------|-------------|
| **Claude** | Long context, nuanced analysis | Be detailed, ask for reasoning |
| **GPT-4o** | Fast iteration, coding | Structure with clear sections |
| **Gemini** | Research, summarization | Good for company research |

### Prompt Structure Template

```
[CONTEXT]
Brief background about the situation.

[TASK]
What you want the AI to do.

[FORMAT]
How you want the output structured.

[CONSTRAINTS]
Any limitations or requirements.

[EXAMPLES] (optional)
Good examples of desired output.
```

---

## Куда дальше

**Strategy:**
→ [[ai-interview-preparation]] — Full AI prep guide
→ [[ai-era-job-search]] — AI tools overview

**Practice:**
→ [[se-interview-foundation]] — Core interview skills
→ [[android-senior-2026]] — Android-specific prep

---

*Обновлено: 2026-01-11*
