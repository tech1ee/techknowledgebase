---
title: "Cultural Dimensions: Hofstede и Lewis Model"
created: 2026-02-09
modified: 2026-02-09
type: concept
status: published
tags:
  - topic/communication
  - type/concept
  - level/intermediate
related:
  - "[[remote-team-communication]]"
prerequisites:
  - "[[communication-models]]"
  - "[[communication-barriers]]"
reading_time: 15
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Cultural Dimensions: Hofstede и Lewis Model

## TL;DR

Культурные различия = **системные**, не личные. Модель Hofstede: 6 измерений (Power Distance, Individualism, etc.). Модель Lewis: 3 типа культур (Linear-Active, Multi-Active, Reactive). Знание культурных паттернов превращает "странное поведение" в предсказуемое.

---

## Зачем это нужно

**Статистика:**
- 70% международных проектов терпят неудачу из-за культурных различий (KPMG)
- $2 trillion ежегодно теряется из-за miscommunication в global teams (Economist Intelligence Unit)
- 86% руководителей считают cultural intelligence критически важным навыком (PwC)
- Remote работа увеличила межкультурные команды на **300%** с 2020 года

**Проблема:**
```
БЕЗ КУЛЬТУРНОГО ПОНИМАНИЯ:
┌─────────────────────────────────────────────────────┐
│ American dev: "Just tell me if there's a problem!" │
│ Japanese dev: "Hmm... it might be challenging..."  │
│                                                     │
│ American: *thinks everything is fine*               │
│ Japanese: *clearly communicated big problem*       │
│                                                     │
│ Result: Deadline missed, both frustrated            │
└─────────────────────────────────────────────────────┘

С КУЛЬТУРНЫМ ПОНИМАНИЕМ:
┌─────────────────────────────────────────────────────┐
│ American dev: "Hmm, 'challenging' — in Japanese    │
│               context this means serious issue."    │
│                                                     │
│ American: "Let me ask directly: is this a blocker? │
│            What resources do you need?"             │
│                                                     │
│ Result: Problem addressed early                     │
└─────────────────────────────────────────────────────┘
```

---

## Для кого этот материал

| Уровень | Применение |
|---------|------------|
| **Junior** | Work with offshore teams, understand code review styles |
| **Middle** | Lead cross-cultural projects, client communication |
| **Senior** | Build global team culture, international hiring |
| **Lead** | Design processes for distributed teams |

---

## Ключевые термины

| Термин | Определение |
|--------|-------------|
| **Cultural Intelligence (CQ)** | Способность эффективно работать в cross-cultural среде |
| **High-context culture** | Много implicitly communicated (Japan, China) |
| **Low-context culture** | Всё explicitly stated (US, Germany, Netherlands) |
| **Monochronic** | Время линейно, one task at a time (Germany, Switzerland) |
| **Polychronic** | Время гибко, multiple tasks (Latin America, Middle East) |

---

## Модель Hofstede: 6 измерений

### Обзор измерений

```
HOFSTEDE'S 6 DIMENSIONS:

1. POWER DISTANCE (PDI)
   Low ◄──────────────────► High
   Equality                  Hierarchy

2. INDIVIDUALISM vs COLLECTIVISM (IDV)
   Collectivist ◄──────────► Individualist
   We-culture               I-culture

3. MASCULINITY vs FEMININITY (MAS)
   Feminine ◄──────────────► Masculine
   Quality of life          Achievement

4. UNCERTAINTY AVOIDANCE (UAI)
   Low ◄──────────────────► High
   Comfortable with ambiguity   Need for rules

5. LONG-TERM ORIENTATION (LTO)
   Short-term ◄─────────────► Long-term
   Tradition                Future-oriented

6. INDULGENCE vs RESTRAINT (IVR)
   Restraint ◄──────────────► Indulgence
   Strict norms             Enjoying life
```

### 1. Power Distance Index (PDI)

**Что измеряет:** Acceptance of unequal power distribution

| Low PDI (Score < 50) | High PDI (Score > 50) |
|----------------------|-----------------------|
| Austria, Israel, Denmark | Malaysia, Philippines, Russia |
| Flat hierarchy | Vertical hierarchy |
| Boss accessible | Boss is authority |
| Challenge decisions | Accept decisions |
| Informal communication | Formal communication |

**IT Application:**

| Ситуация | Low PDI | High PDI |
|----------|---------|----------|
| Code review от junior | Normal | Может быть awkward |
| Disagree with architect | Expected | Требует осторожности |
| Direct message to CTO | Normal | Через менеджера |
| Calling out issues | Open | Private first |

**Адаптация:**
```
HIGH PDI CULTURE:
✓ Respect titles and hierarchy
✓ Communicate through proper channels
✓ Acknowledge seniority in meetings
✓ Don't publicly challenge authority

LOW PDI CULTURE:
✓ Be prepared for direct challenges
✓ Justify decisions, not just announce
✓ Expect input from all levels
✓ Informal communication is normal
```

### 2. Individualism vs Collectivism (IDV)

**Что измеряет:** Individual achievement vs group harmony

| Individualist (High IDV) | Collectivist (Low IDV) |
|--------------------------|------------------------|
| USA, UK, Australia | China, Japan, Korea |
| "I" | "We" |
| Personal achievement | Group success |
| Speak your mind | Maintain harmony |
| Task > relationship | Relationship > task |

**IT Application:**

| Ситуация | Individualist | Collectivist |
|----------|---------------|--------------|
| Taking credit | "I did X" | "Our team achieved X" |
| Disagreement | Open debate | Private consensus |
| Decision making | Individual | Group consultation |
| Feedback | Direct | Indirect, face-saving |

**Адаптация:**
```
COLLECTIVIST TEAM:
✓ Credit the team, not individuals
✓ Build consensus before meetings
✓ Allow "face-saving" exits
✓ Invest in relationships first
✓ Group harmony > being right

INDIVIDUALIST TEAM:
✓ Recognize individual contributions
✓ Expect direct opinions
✓ Decisions can be made quickly
✓ Competition is normal
```

### 3. Masculinity vs Femininity (MAS)

**Что измеряет:** Achievement-focus vs quality-of-life-focus

| Feminine (Low MAS) | Masculine (High MAS) |
|--------------------|----------------------|
| Sweden, Norway, Netherlands | Japan, USA, Germany |
| Work-life balance | Live to work |
| Consensus | Competition |
| Modest | Assertive |
| Quality of life | Achievement & success |

**IT Application:**

| Ситуация | Feminine culture | Masculine culture |
|----------|------------------|-------------------|
| Overtime | Резко негативно | Expected for deadlines |
| Promotion | Team contribution | Individual achievement |
| Conflict | Seek compromise | Win the argument |
| Goals | Sustainable pace | Aggressive targets |

**Адаптация:**
```
FEMININE CULTURE:
✓ Respect work-life boundaries
✓ Seek win-win solutions
✓ Don't be overly competitive
✓ Quality > quantity

MASCULINE CULTURE:
✓ Be assertive and confident
✓ Show achievements
✓ Accept competitive environment
✓ Results matter most
```

### 4. Uncertainty Avoidance (UAI)

**Что измеряет:** Comfort with ambiguity

| Low UAI | High UAI |
|---------|----------|
| Singapore, Denmark, UK | Greece, Japan, France |
| Comfortable with ambiguity | Need clear rules |
| Innovation-friendly | Risk-averse |
| Flexible processes | Structured processes |
| "Let's try it" | "What are the risks?" |

**IT Application:**

| Ситуация | Low UAI | High UAI |
|----------|---------|----------|
| New technology | "Let's experiment" | "What's the documentation?" |
| Agile adoption | Natural fit | Needs more structure |
| Unclear requirements | Iterate as we go | Define everything first |
| Breaking changes | Move fast | Careful planning |

**Адаптация:**
```
HIGH UAI CULTURE:
✓ Provide detailed documentation
✓ Clear processes and procedures
✓ Risk assessment before changes
✓ Written communication over verbal
✓ Don't surprise them

LOW UAI CULTURE:
✓ Be comfortable with "figure it out"
✓ Expect pivots and changes
✓ Less process, more experimentation
✓ Quick decision-making
```

### 5. Long-Term Orientation (LTO)

**Что измеряет:** Focus on future vs respect for tradition

| Short-term (Low LTO) | Long-term (High LTO) |
|----------------------|----------------------|
| USA, UK, Australia | China, Japan, South Korea |
| Quick results | Persistent effort |
| Quarterly thinking | 5-10 year planning |
| Spend now | Save for future |
| Absolute truths | Context-dependent |

**IT Application:**

| Ситуация | Short-term | Long-term |
|----------|------------|-----------|
| Tech debt | "Fix later" | "Build right first time" |
| Career growth | Fast promotion | Gradual development |
| Architecture | MVP first | Design for scale |
| Relationships | Transaction-based | Investment-based |

### 6. Indulgence vs Restraint (IVR)

**Что измеряет:** Freedom to enjoy life

| Restraint (Low IVR) | Indulgence (High IVR) |
|---------------------|----------------------|
| Russia, China, India | Mexico, Sweden, USA |
| Strict social norms | Personal freedom |
| Duty over pleasure | Work-life balance |
| Formal relationships | Casual relationships |

---

## Country Profiles (IT-relevant)

### Comparison Table

| Country | PDI | IDV | MAS | UAI | LTO | IVR |
|---------|-----|-----|-----|-----|-----|-----|
| **USA** | 40 | 91 | 62 | 46 | 26 | 68 |
| **Germany** | 35 | 67 | 66 | 65 | 83 | 40 |
| **Japan** | 54 | 46 | 95 | 92 | 88 | 42 |
| **India** | 77 | 48 | 56 | 40 | 51 | 26 |
| **China** | 80 | 20 | 66 | 30 | 87 | 24 |
| **UK** | 35 | 89 | 66 | 35 | 51 | 69 |
| **Netherlands** | 38 | 80 | 14 | 53 | 67 | 68 |
| **Russia** | 93 | 39 | 36 | 95 | 81 | 20 |

### Working with Specific Cultures

**USA:**
```
СТИЛЬ: Direct, informal, results-oriented
✓ Get to the point quickly
✓ Don't over-explain (time = money)
✓ First-name basis is normal
✓ Expect fast decisions
✓ "No" is acceptable
✗ Don't be overly formal
✗ Don't take silence as agreement
```

**Germany:**
```
СТИЛЬ: Precise, planned, quality-focused
✓ Be punctual (early is on time)
✓ Provide detailed documentation
✓ Follow processes
✓ Separate personal and professional
✓ Direct feedback is normal
✗ Don't be vague
✗ Don't reschedule last minute
```

**Japan:**
```
СТИЛЬ: Hierarchical, consensus-oriented, indirect
✓ Respect hierarchy (titles matter)
✓ "Yes" might mean "I heard you"
✓ Build consensus before meetings
✓ Silence is thinking, not rejection
✓ Face-saving is critical
✗ Don't put people on the spot
✗ Don't be too casual with seniors
```

**India:**
```
СТИЛЬ: Hierarchical, relationship-focused, flexible
✓ Build personal relationships first
✓ "Yes" might mean "I'll try"
✓ Deadlines are starting points
✓ Indirect communication is common
✓ Respect seniority
✗ Don't be too direct with criticism
✗ Don't skip small talk
```

**China:**
```
СТИЛЬ: Hierarchical, relationship-driven, long-term
✓ Guanxi (relationships) first
✓ Face-saving is paramount
✓ Group > individual
✓ Patience and persistence
✓ Written confirmation important
✗ Don't cause loss of face publicly
✗ Don't expect quick decisions
```

---

## Lewis Model: 3 Cultural Types

### The Triangle

```
                    LINEAR-ACTIVE
                         ▲
                        /│\
                       / │ \
                      /  │  \
                     /   │   \
                    /    │    \
                   /     │     \
                  /      │      \
                 /       │       \
                /        │        \
               ◄─────────┼─────────►
         MULTI-ACTIVE           REACTIVE
```

### Characteristics

| Linear-Active | Multi-Active | Reactive |
|---------------|--------------|----------|
| Germany, Switzerland, USA, UK | Italy, Spain, Latin America | Japan, China, Finland |
| Task-oriented | People-oriented | Respect-oriented |
| One thing at a time | Many things at once | React to others |
| Planning | Improvising | Listening |
| Factual | Emotional | Indirect |
| Talks half the time | Talks most | Listens most |
| Punctual | Flexible with time | Punctual but flexible |

### IT Application

**Linear-Active Developer:**
```
CHARACTERISTICS:
- One task at a time
- Detailed planning before coding
- Direct communication
- Written specs preferred
- Deadline = deadline

WORKING WITH THEM:
✓ Clear requirements upfront
✓ Don't interrupt flow
✓ Respect scheduled meetings
✓ Written follow-ups
```

**Multi-Active Developer:**
```
CHARACTERISTICS:
- Multiple projects simultaneously
- Flexible with plans
- Relationship-focused
- Verbal communication preferred
- Deadline = target

WORKING WITH THEM:
✓ Build rapport first
✓ Allow discussion and debate
✓ Expect enthusiasm
✓ Flexible on process
✓ Check in frequently
```

**Reactive Developer:**
```
CHARACTERISTICS:
- Responds to context
- Listens more than speaks
- Indirect communication
- Consensus-seeking
- Deadline = consideration

WORKING WITH THEM:
✓ Give time to respond
✓ Don't mistake silence for ignorance
✓ Create safe space for opinions
✓ Read between the lines
✓ Patience with decision-making
```

---

## High-Context vs Low-Context

### Edward Hall's Model

```
LOW-CONTEXT                          HIGH-CONTEXT
│                                              │
│ Germany                             Japan    │
│ Switzerland         China                    │
│ USA               Korea                      │
│ Netherlands      India                       │
│ UK             Brazil                        │
│              Italy                           │
│           France                             │
│         Spain                                │
│                                              │
├─────────────────────────────────────────────►
Explicit message              Implicit meaning
```

### Communication Differences

| Low-Context | High-Context |
|-------------|--------------|
| Direct: "This won't work" | Indirect: "This might be challenging" |
| Written contracts | Verbal agreements + relationships |
| Task first, relationship second | Relationship first, task second |
| Конкретные инструкции | Read between the lines |
| What is said = what is meant | Context matters more than words |

### IT Examples

**Code Review:**
```
LOW-CONTEXT (US/Germany):
"This function has O(n²) complexity.
 Use a hashmap for O(n) lookup.
 See line 47."

HIGH-CONTEXT (Japan/China):
"This is an interesting approach.
 I wonder if there might be opportunities
 for optimization in certain scenarios..."

TRANSLATION:
Both mean "please fix this"
```

**Asking for Help:**
```
LOW-CONTEXT:
"I'm stuck. Can you help me with X?"

HIGH-CONTEXT:
"This problem is very interesting...
 I've been researching various approaches..."

TRANSLATION:
Both need help, high-context is hinting
```

---

## Практические скрипты

### Adapting Feedback

**To High-PDI culture:**
```
❌ "This code is wrong. Fix it."
✅ "I noticed something in the code that
    might benefit from a different approach.
    Would you like to discuss?"
```

**To Low-context culture:**
```
❌ "There might be some considerations..."
✅ "There's a bug on line 47.
    The loop condition should be '<' not '<='."
```

### Requesting Work

**From collectivist culture:**
```
❌ "John, you need to fix this by Friday."
✅ "The team has identified this issue.
    What support do you need from us
    to address it this week?"
```

**From high-UAI culture:**
```
❌ "Figure out the best approach."
✅ "Here are the requirements, the existing patterns,
    and the documentation for similar implementations."
```

### Disagreeing Professionally

**With high-PDI senior:**
```
❌ "I disagree. This won't work because..."
✅ "I appreciate your perspective.
    I've noticed some data that might be relevant.
    Would you have time to review it?"
```

**With high-context colleague:**
```
❌ "So you're saying there's a problem?"
✅ Listen to what's NOT being said.
   "It sounds like there might be some concerns.
    I'd like to understand better—
    can we schedule time to discuss?"
```

---

## Distributed Team Strategies

### Multi-Cultural Team Charter

```
TEAM NORMS (example):

COMMUNICATION:
□ Written > verbal for decisions
□ Explicit > implicit
□ Overcommunicate context
□ No assumptions about understanding

MEETINGS:
□ Agenda shared 24h before
□ Start with relationship check-in
□ Rotate meeting times for timezones
□ Written summary after

FEEDBACK:
□ Default to private
□ Specific and actionable
□ Assume positive intent
□ Ask before giving

DECISIONS:
□ Async discussion period
□ Clear decision owner
□ Document reasoning
□ Respect different paces
```

### Conflict Prevention

```
PREVENTIVE PRACTICES:

1. EXPLICIT NORMS
   "In our team, it's okay to say 'I disagree'
    in code reviews."

2. OVERCOMMUNICATION
   State the obvious.
   "I'm asking this directly because
    in my culture that's normal."

3. CULTURAL DISCLAIMER
   "I'm being direct because I'm German.
    Please tell me if I'm being too blunt."

4. FEEDBACK LOOPS
   Regular check-ins: "How are we doing?"
   Safe space for culture friction.

5. EDUCATION
   Share this material with team.
   Discuss dimensions openly.
```

---

## Распространённые ошибки

### 1. Stereotyping

```
❌ ОШИБКА:
"He's German, so he must be rigid about rules."

✅ РЕАЛЬНОСТЬ:
Cultural dimensions are AVERAGES.
Individual variation is huge.
Use as starting hypothesis, not conclusion.
```

### 2. Self-Reference Criterion

```
❌ ОШИБКА:
Judging other cultures by your own norms.
"Why won't they just say what they mean?"

✅ FIX:
Their "normal" is different.
Neither is wrong.
```

### 3. Cultural Attribution Error

```
❌ ОШИБКА:
"He didn't respond because he's from high-context culture."

✅ РЕАЛЬНОСТЬ:
Maybe he's just busy.
Don't over-attribute to culture.
```

### 4. Static Culture View

```
❌ ОШИБКА:
"China is always hierarchical."

✅ РЕАЛЬНОСТЬ:
Cultures evolve.
Startups ≠ State enterprises.
Gen Z ≠ Boomers.
Urban ≠ Rural.
```

### 5. Ignoring Individual Preferences

```
❌ ОШИБКА:
Only using cultural frameworks.

✅ FIX:
ASK the person:
"What communication style works best for you?"
"How do you prefer to receive feedback?"
```

---

## Когда использовать / НЕ использовать

### Когда культурные фреймворки полезны

| Ситуация |
|----------|
| First interaction with new culture |
| Unexpected friction in cross-cultural team |
| Designing processes for global team |
| Preparing for international client |
| Onboarding team members from different cultures |

### Когда НЕ полагаться только на фреймворки

| Ситуация | Что делать |
|----------|------------|
| Working with individuals | Ask about their preferences |
| Long-term relationships | Build personal understanding |
| Hybrid cultural backgrounds | Don't assume |
| Startup vs corporate | Culture varies within country |

---

## Практические задания

### Задание 1: Cultural Profile

**Задача:** Проанализируйте свою культуру по 6 измерениям Hofstede.
- Где вы лично?
- Где ваша организационная культура?
- Есть ли расхождения?

### Задание 2: Team Mapping

**Задача:** Для вашей текущей команды:
1. Откуда коллеги? (страны)
2. Найдите scores на hofstede-insights.com
3. Где наибольшие различия?
4. Как это проявляется в работе?

### Задание 3: Communication Translation

**Сообщение из high-context культуры:**
```
"This approach is interesting.
 There might be some considerations
 regarding the timeline."
```

**Задача:** "Переведите" на low-context язык:
- Что реально говорится?
- Какой action нужен?

### Задание 4: Feedback Rewriting

**Direct feedback (US style):**
```
"This PR has several issues:
1. Missing error handling
2. No tests
3. Poor variable naming

Please fix before merge."
```

**Задача:** Перепишите для:
- Japanese colleague (high-context, face-saving)
- Indian colleague (hierarchical, relationship-focused)

### Задание 5: Team Charter Draft

**Задача:** Напишите раздел "Communication Norms" для multicultural team:
- Члены: USA, Germany, Japan, India
- Формат: Remote-first
- Что включить? (конкретные guidelines)

---

## Ресурсы

### Онлайн инструменты

| Ресурс | URL | Описание |
|--------|-----|----------|
| Hofstede Insights | hofstede-insights.com | Country comparison tool |
| The Culture Map | erinmeyer.com | Erin Meyer's framework |
| GlobeSmart | globesmart.com | Cultural profiles (paid) |
| Country Navigator | countrynavigator.com | Cultural training |

### Книги

1. "The Culture Map" by Erin Meyer — лучшая для бизнеса
2. "Cultures and Organizations" by Hofstede — академическая база
3. "When Cultures Collide" by Richard Lewis — практические примеры
4. "Kiss, Bow, or Shake Hands" by Morrison & Conaway — quick reference

---

## Связанные темы

### Prerequisites
- [[communication-barriers]] — cultural barriers
- [[active-listening]] — cross-cultural listening

### Unlocks
- [[remote-team-communication]] — managing across cultures
- [[stakeholder-negotiation]] — international stakeholders

### Интеграция
- [[giving-feedback]] — culturally-aware feedback
- [[conflict-resolution]] — cross-cultural conflict

---

## Источники

1. Hofstede, G. "Cultures and Organizations" (3rd ed., 2010)
2. Meyer, E. "The Culture Map" (2014)
3. Lewis, R. "When Cultures Collide" (4th ed., 2018)
4. Hall, E.T. "Beyond Culture" (1976)
5. Hofstede Insights Country Comparison Tool
6. GLOBE Study (Global Leadership and Organizational Behavior Effectiveness)
7. World Values Survey
8. PwC Global Culture Survey (2024)
9. Harvard Business Review — Cross-cultural management articles
10. MIT Sloan Management Review — Global teams research

---

## Проверь себя

> [!question]- Ваша команда состоит из немцев (Low PDI, High UAI) и индийских разработчиков (High PDI, Low UAI). Как вы спроектируете процесс code review, чтобы он работал для обеих культур?
> Нужен гибридный подход. Для немецких коллег: чёткие критерии review (checklist, линтеры) — это удовлетворит High UAI. Для индийских коллег: фидбек по умолчанию приватный, через DM или 1-on-1, а не публичный комментарий — это учитывает High PDI и face-saving. Общее правило: письменные нормы («в нашей команде несогласие в review — нормально»), ревью анонимизировать где возможно, чтобы снизить влияние иерархии.

> [!question]- Почему модель Hofstede описывает средние показатели по стране, а не поведение конкретного человека? Какие риски возникают, если забыть об этом различии?
> Измерения Hofstede — статистические средние, полученные из опросов тысяч людей. Внутри любой культуры разброс огромен: стартап в Токио может быть более «flat», чем корпорация в Амстердаме. Если относиться к баллам как к предписаниям, вы попадаете в ловушку стереотипирования (ошибка №1 из раздела «Распространённые ошибки»). Правильный подход — использовать фреймворк как стартовую гипотезу и затем уточнять через прямой диалог: «Какой стиль обратной связи тебе подходит?»

> [!question]- Представьте, что вы проводите ретроспективу спринта с участниками из США (Linear-Active), Италии (Multi-Active) и Японии (Reactive). Какие проблемы возникнут и как их предотвратить?
> Американцы будут высказываться напрямую и ждать быстрых решений. Итальянцы будут говорить одновременно, эмоционально обсуждать — это норма Multi-Active стиля. Японские коллеги будут молчать, что остальные могут принять за согласие, хотя они обдумывают ответ. Решения: (1) async pre-retro — все пишут фидбек заранее, (2) round-robin формат вместо открытой дискуссии, (3) явное правило «тишина = обдумывание, не согласие», (4) follow-up через 24 часа для тех, кто предпочитает письменную коммуникацию.

> [!question]- Как связаны измерение Uncertainty Avoidance (Hofstede) и подходы к архитектуре ПО — например, выбор между «MVP first» и «design for scale»? Приведите конкретный пример из таблицы Country Profiles.
> High UAI культуры (Япония — 92, Россия — 95) стремятся минимизировать риски и неизвестность, поэтому склонны к тщательному проектированию архитектуры заранее («design for scale»). Low UAI культуры (Сингапур, Дания, UK — 35) комфортно чувствуют себя с неопределённостью и предпочитают «Let's try it» → MVP подход. Пример: немецкая команда (UAI 65) потребует подробную документацию и risk assessment перед внедрением нового фреймворка, тогда как американская (UAI 46) скажет «Let's experiment» и начнёт proof of concept. Ни один подход не лучше — важно осознанно выбирать стратегию, а не следовать культурной инерции.

---

## Ключевые карточки

Power Distance Index (PDI) — что измеряет и как влияет на code review?
?
PDI измеряет принятие неравного распределения власти. Low PDI (Австрия, Дания): junior может свободно ревьюить код senior-а, несогласие ожидаемо. High PDI (Малайзия, Россия): ревью кода от junior-а может быть awkward, несогласие с архитектором требует осторожности, коммуникация часто идёт через менеджера.

Individualism vs Collectivism — как проявляется в IT-командах?
?
Индивидуалисты (США, UK): «I did X», открытые дебаты, быстрые решения, прямой фидбек. Коллективисты (Китай, Япония): «Our team achieved X», приватный консенсус, групповое принятие решений, непрямой фидбек с сохранением лица. Ключ: credit the team в коллективистских культурах, recognize individuals — в индивидуалистических.

Три типа культур по Lewis Model?
?
Linear-Active (Германия, Швейцария, США): task-oriented, одна задача за раз, планирование, пунктуальность, факты. Multi-Active (Италия, Испания, Латинская Америка): people-oriented, много задач параллельно, импровизация, эмоциональность. Reactive (Япония, Китай, Финляндия): respect-oriented, слушают больше, чем говорят, непрямая коммуникация, консенсус.

High-context vs Low-context — как «переводить» code review комментарии?
?
Low-context (США/Германия): «This function has O(n²). Use a hashmap for O(n).» High-context (Япония/Китай): «This is an interesting approach. I wonder if there might be opportunities for optimization...» Оба означают «please fix this». Правило: с low-context коллегами — будь конкретен, с high-context — читай между строк и не интерпретируй мягкость как одобрение.

Uncertainty Avoidance (UAI) — как влияет на adoption Agile?
?
Low UAI (Сингапур, Дания): Agile — natural fit, комфортно с «figure it out», быстрые решения, меньше процессов. High UAI (Греция, Япония, Франция): Agile требует больше структуры — детальная документация, чёткие процедуры, risk assessment перед изменениями, письменная коммуникация предпочтительнее устной. Ключ: не «surprises» — предупреждать заранее.

Пять распространённых ошибок при использовании культурных фреймворков?
?
(1) Стереотипирование — измерения это средние, не правила. (2) Self-Reference Criterion — оценка чужой культуры через свою. (3) Cultural Attribution Error — «он не ответил, потому что high-context» (а может, просто занят). (4) Static Culture View — культуры меняются: стартап ≠ госкорпорация, Gen Z ≠ бумеры. (5) Игнорирование индивидуальных предпочтений — всегда спрашивайте: «Какой стиль коммуникации тебе подходит?»

Как построить Team Charter для мультикультурной распределённой команды?
?
Четыре блока: (1) Communication — written > verbal, explicit > implicit, overcommunicate context. (2) Meetings — agenda за 24ч, relationship check-in в начале, ротация часовых поясов, письменное саммари. (3) Feedback — по умолчанию приватный, конкретный и actionable, assume positive intent. (4) Decisions — async discussion period, clear decision owner, document reasoning, respect different paces.

Long-Term vs Short-Term Orientation — как это влияет на tech debt?
?
Short-term (США, UK — LTO 26/51): «Fix later», MVP first, быстрые промоушены, quarterly thinking, транзакционные отношения. Long-term (Китай, Япония — LTO 87/88): «Build right first time», design for scale, постепенное карьерное развитие, 5-10 летнее планирование, инвестиционные отношения. Следствие: в short-term культурах tech debt накапливается быстрее, но и pivot происходит легче.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Барьеры коммуникации | [[communication-barriers]] | Глубже разобрать культурные барьеры как подтип коммуникационных |
| Активное слушание | [[active-listening]] | Навык «читать между строк» критичен для high-context культур |
| Обратная связь | [[giving-feedback]] | Научиться адаптировать фидбек под PDI и контекст культуры |
| Разрешение конфликтов | [[conflict-resolution]] | Культурные различия — частый источник конфликтов в командах |
| Работа с удалённой командой | [[remote-team-communication]] | Применить культурные фреймворки к distributed team практикам |
| Переговоры со стейкхолдерами | [[stakeholder-negotiation]] | Вести переговоры с международными клиентами и партнёрами |
| Модели коммуникации | [[communication-models]] | Фундамент: понять как культурный контекст встраивается в общие модели |

---

**Последнее обновление:** 2025-01-18
**Статус:** Завершён
