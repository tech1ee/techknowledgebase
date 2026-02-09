---
title: "Negotiation Frameworks: Harvard Method и другие подходы"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: intermediate
prerequisites:
  - [[negotiation-fundamentals]]
teaches:
  - harvard-method
  - principled-negotiation
  - win-win-strategies
  - integrative-bargaining
unlocks:
  - [[stakeholder-negotiation]]
  - [[salary-negotiation]]
tags: [communication, soft-skills, negotiation, frameworks, harvard]
---

# Negotiation Frameworks: от Harvard Method до современных подходов

> **TL;DR:** Harvard Method (Principled Negotiation) = Focus on Interests, not Positions + Invent Options + Use Objective Criteria + Separate People from Problem. Альтернативы: Competitive (win-lose), Accommodating, Avoiding. Ключевая идея: лучшие переговоры = обе стороны уходят с value. Применяется в: salary talks, contract negotiations, cross-team resource allocation, vendor negotiations.

---

## Зачем это нужно?

### Представьте ситуацию

Sprint planning. PM хочет 5 фич в sprint, ты как tech lead знаешь что реально 3. Позиционный торг: "Нужно 5" — "Только 3" — "Ладно, 4" — "3.5 не бывает." Результат: компромисс где никто не доволен, и половина фич будет сделана плохо.

С Harvard Method: "Какая цель этого sprint? Что критично для бизнеса?" Оказывается, 2 фичи критичны для demo клиенту, остальные — nice to have. Результат: 2 фичи качественно + начало третьей, клиент happy, команда не выгорела.

**Без framework:**
- Позиционный торг → compromise
- Win-lose mentality
- Damaged relationships
- Suboptimal outcomes

**С framework:**
- Interests-based → creative solutions
- Value creation
- Preserved relationships
- Better outcomes for both

---

## Для кого этот материал

| Уровень | Подходит? | Фокус |
|---------|-----------|-------|
| **Junior** | ✅ | Понимание принципов, scope negotiations |
| **Middle** | ✅ | Cross-team negotiations, resource allocation |
| **Senior** | ✅ | Strategic negotiations, architectural decisions |
| **Tech Lead** | ✅ | Team negotiations, stakeholder management, budget |

---

## Терминология

| Термин | Что это | IT-аналогия |
|--------|---------|-------------|
| **Positional Bargaining** | Торг по позициям: "хочу X" vs "хочу Y" | Как hardcoded values — негибко |
| **Interest-Based** | Переговоры по интересам за позициями | Как interface — focus on what matters |
| **BATNA** | Best Alternative to Negotiated Agreement | Как fallback strategy — что если no deal |
| **ZOPA** | Zone of Possible Agreement | Как overlap в Venn diagram — где agreement possible |
| **Integrative Bargaining** | Создание value для обеих сторон | Как win-win architecture — обе systems benefit |
| **Distributive Bargaining** | Деление fixed pie | Как zero-sum game — один wins, другой loses |

---

## Как это работает?

### Сравнение подходов к переговорам

```
┌─────────────────────────────────────────────────────────────────┐
│                   5 NEGOTIATION STYLES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│            HIGH                                                 │
│  ASSERTIVE  │                                                   │
│  (Concern   │  COMPETING          COLLABORATING                 │
│   for own   │  (Win-Lose)         (Win-Win)                     │
│   outcome)  │  "I win, you lose"  "Let's both win"              │
│             │                                                   │
│             │         COMPROMISING                              │
│             │         (Split the difference)                    │
│             │         "We each give some"                       │
│             │                                                   │
│             │  AVOIDING            ACCOMMODATING                │
│             │  (Lose-Lose)         (Lose-Win)                   │
│             │  "Let's not deal"    "You win, I give"            │
│            LOW                                                  │
│             └────────────────────────────────────────────────── │
│              LOW          COOPERATIVE          HIGH             │
│                    (Concern for other's outcome)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Harvard Method: 4 Principles

```
┌─────────────────────────────────────────────────────────────────┐
│          HARVARD PRINCIPLED NEGOTIATION                          │
│             (Getting to Yes — Fisher & Ury)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SEPARATE PEOPLE FROM PROBLEM                                │
│     ─────────────────────────────                               │
│     • Атакуй problem, не person                                 │
│     • Manage emotions separately                                │
│     • Build working relationship                                │
│                                                                 │
│     IT-пример: "Архитектура X имеет проблемы" ≠                │
│                "Ты сделал плохую архитектуру"                   │
│                                                                 │
│  2. FOCUS ON INTERESTS, NOT POSITIONS                           │
│     ─────────────────────────────────                           │
│     • Position: ЧТО ты хочешь                                   │
│     • Interest: ПОЧЕМУ ты это хочешь                            │
│     • Ask "WHY?" to find underlying needs                       │
│                                                                 │
│     IT-пример: Position: "Нужен deadline extension"             │
│                Interest: "Нужно quality, не хочу technical debt"│
│                                                                 │
│  3. INVENT OPTIONS FOR MUTUAL GAIN                              │
│     ───────────────────────────────                             │
│     • Brainstorm before deciding                                │
│     • Look for win-win solutions                                │
│     • Expand the pie before dividing                            │
│                                                                 │
│     IT-пример: Вместо "5 фич vs 3 фичи" →                       │
│                "Что если phased release? MVP + iteration?"      │
│                                                                 │
│  4. INSIST ON OBJECTIVE CRITERIA                                │
│     ──────────────────────────────                              │
│     • Use fair standards                                        │
│     • Market rates, expert opinion, precedent                   │
│     • Agree on criteria before specifics                        │
│                                                                 │
│     IT-пример: "Industry benchmark для этого scope: X weeks.    │
│                Наши velocity metrics показывают Y."             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Источник:** [Harvard PON: Getting to Yes](https://www.pon.harvard.edu/daily/negotiation-skills-daily/six-guidelines-for-getting-to-yes/)

### Когда какой стиль использовать

```
┌─────────────────────────────────────────────────────────────────┐
│              ВЫБОР NEGOTIATION STYLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  COLLABORATING (Harvard Method) — when:                         │
│  • Ongoing relationship важен                                   │
│  • Complex issue with multiple interests                        │
│  • Time available для exploration                               │
│  • Both parties willing to engage                               │
│  → Most IT negotiations: team, stakeholder, cross-functional    │
│                                                                 │
│  COMPETING — when:                                              │
│  • Quick decision needed                                        │
│  • One-time transaction                                         │
│  • Critical issue where you're right                            │
│  • Other party competitive                                      │
│  → Rare in IT: emergency decisions, firm boundaries             │
│                                                                 │
│  COMPROMISING — when:                                           │
│  • Time pressure                                                │
│  • Moderate importance                                          │
│  • Equal power                                                  │
│  → Sprint scope when both have valid points                     │
│                                                                 │
│  ACCOMMODATING — when:                                          │
│  • Issue more important to them                                 │
│  • Building goodwill / political capital                        │
│  • You're wrong                                                 │
│  → Minor technical decisions, helping junior grow               │
│                                                                 │
│  AVOIDING — when:                                               │
│  • Issue trivial                                                │
│  • Emotions high, need cooling                                  │
│  • No chance of winning                                         │
│  → Bikeshedding, toxic debates                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Пошаговый процесс Harvard Method

### Шаг 1: Prepare (До переговоров)

**Checklist:**
```
□ What are MY interests? (not just positions)
□ What are THEIR likely interests?
□ What is my BATNA?
□ What is their likely BATNA?
□ What objective criteria could we use?
□ What options might create mutual value?
```

### Шаг 2: Открытие (Separate People, Build Rapport)

**Скрипт:**
```
"Спасибо что нашёл время. Цель — найти solution
который работает для обеих сторон.

Прежде чем обсуждать specifics, хочу понять
твою perspective. Расскажи что для тебя важно?"
```

### Шаг 3: Explore Interests (Не позиции)

**Techniques:**
- Ask "Why is that important?"
- Ask "What would that give you?"
- Ask "Help me understand..."

**Скрипт:**
```
"Ты говоришь что нужно [position].
Помоги понять — почему это важно?
Что это даст?"
```

### Шаг 4: Invent Options (Brainstorm)

**Rules:**
- No criticism during brainstorm
- Quantity over quality initially
- Build on ideas

**Скрипт:**
```
"Давай отступим от positions и brainstorm.
Какие варианты могут удовлетворить оба
интереса: [your interest] и [their interest]?

Без оценки пока — просто идеи."
```

### Шаг 5: Apply Criteria

**Скрипт:**
```
"Из этих options, какой лучше по объективным
критериям?

Можем посмотреть на:
• Industry benchmarks
• Our past data
• Expert recommendations
• Fairness to both sides

Какие criteria важны для тебя?"
```

### Шаг 6: Reach Agreement

**Скрипт:**
```
"Итак, мы agreed на [option].

Резюмирую:
• Ты получаешь: [their value]
• Я получаю: [your value]
• Timeline: [specifics]
• Next steps: [actions]

Это верно? Что упустил?"
```

---

## Скрипты и Templates

### Use Case 1: Sprint Scope Negotiation

**Ситуация:** PM хочет 5 features, team capacity 3.

**Positional (Плохо):**
```
PM: "Нужно 5 фич."
You: "Только 3 реально."
PM: "Ладно, 4."
You: "Не успеем quality."
→ Compromise: 4 плохо сделанных фичи
```

**Harvard Method:**
```
You: "Давай разберёмся в interests.
Почему эти 5 важны? Какова цель sprint?"

PM: "Demo для клиента X требует фичи A и B.
Остальные — roadmap items."

You: "Понял. Мой interest — quality и sustainable pace.
Если сделаем 5 rushed, технический долг вырастет.

Варианты:
1. A и B в этот sprint качественно, C начинаем
2. Все 5, но C, D, E — MVP версии
3. Добавить ресурс на D и E

По velocity metrics, A+B = 3 недели quality work.
Что лучше подходит для demo?"

PM: "Вариант 1 — A и B нужны полноценные для demo."

You: "Договорились. A+B к [date], C начинаем."
```

### Use Case 2: Resource Allocation (Cross-team)

**Ситуация:** Две команды хотят одного senior engineer.

**Скрипт:**
```
"У нас competition за [name]. Прежде чем 'who wins',
давай поймём interests.

[К другой команде]
Что вам нужно от senior? Какие задачи?"

Team B: "Knowledge transfer на новых джунов."

You: "Нам нужен technical lead на архитектуру проекта.

Варианты:
1. 50/50 split времени
2. Консультации вместо full-time
3. [Name] на наш проект, но weekly sessions с вашими
4. Найти другого senior на одну из задач

Какой option покрывает оба interests?"
```

### Use Case 3: Deadline Extension Request

**Ситуация:** Нужно попросить больше времени у stakeholder.

**Скрипт:**
```
"Хочу обсудить timeline для [project].

Прежде чем говорить о датах — какой твой
главный interest? Что важно для бизнеса?"

Stakeholder: "Клиентская demo в [date]."

You: "Понял. Мой interest — deliver quality
без critical bugs.

Текущий scope не успеваем quality к [date].
Варианты:
1. Full scope, +2 недели
2. Reduced scope (без feature X), on time
3. MVP к demo date, polish после

По нашим metrics, вариант 2 или 3 achievable.
Что работает для demo?"
```

### Use Case 4: Architectural Decision Disagreement

**Ситуация:** Ты за microservices, коллега за monolith.

**Скрипт:**
```
"Вижу мы имеем разные views. Давай отойдём от
'microservices vs monolith' и поймём interests.

Мой interest: scalability при росте team,
independent deployments.

Какой твой главный concern?"

Colleague: "Complexity. У нас нет expertise
для distributed systems."

You: "Valid point. Общий interest — solution
который works для нашего context.

Варианты:
1. Monolith now, decompose later
2. Modular monolith (best of both)
3. Start with 2-3 services, не full micro
4. Invest в training, then micro

Какой balances scalability + complexity best
для нашей ситуации?"
```

---

## Распространённые ошибки

### Ошибка 1: Jumping to Positions

**Неправильно:**
Сразу "Нужно X" vs "Нужно Y"

**Правильно:**
Сначала explore interests

### Ошибка 2: Win-Lose Mentality

**Неправильно:**
"Я должен победить в этих переговорах"

**Правильно:**
"Как создать value для обоих?"

### Ошибка 3: Ignoring BATNA

**Неправильно:**
Negotiate without knowing alternatives

**Правильно:**
Know your BATNA, improve it if weak

### Ошибка 4: Getting Personal

**Неправильно:**
"Ты всегда нереалистичные deadlines ставишь!"

**Правильно:**
"Этот deadline создаёт risk для quality. Давай обсудим."

### Ошибка 5: Single Option Focus

**Неправильно:**
"Только один вариант: X"

**Правильно:**
Generate multiple options before choosing

---

## Когда использовать / НЕ использовать

### Harvard Method работает, когда:

| Ситуация | Почему подходит |
|----------|-----------------|
| Ongoing relationships | Preserves trust |
| Complex multi-issue | Finds creative solutions |
| Both parties rational | Requires good faith |
| Time to explore | Needs dialogue |

### Ограничения:

| Ситуация | Что делать |
|----------|------------|
| Emergency decision | Be more directive |
| Bad faith other party | Protect yourself first |
| Clear right answer | State facts, don't over-negotiate |
| Power imbalance | Build BATNA first |

---

## Практика

### Упражнение 1: Find the Interest

**Positions:**
1. "Нужен новый hire в команду"
2. "Нельзя использовать this library"
3. "Документация должна быть на русском"

**Задание:** Найди possible interests за каждой position.

<details><summary>Ответы</summary>

1. Interest: Team overwhelmed, need help with workload
   OR want specific skill OR worried about bus factor

2. Interest: Security concerns? License issues?
   Performance? Maintenance burden?

3. Interest: Team не читает английский? Compliance?
   Faster onboarding?
</details>

### Упражнение 2: Generate Options

**Situation:**
Team A needs dedicated QA. Team B needs the only QA person full-time.

**Задание:** Generate 5 options using integrative approach.

<details><summary>Ideas</summary>

1. Shared QA with schedule (MWF team A, TT team B)
2. QA for critical paths only, teams do own testing
3. Cross-train developer to help with QA
4. Hire second QA (if budget)
5. Automate testing to reduce QA load
6. QA leads, teams execute on automation
7. Contract QA for overflow periods
</details>

### Ежедневная практика

| День | Фокус | Действие |
|------|-------|----------|
| Пн | Interests | При request, ask "Why is this important?" |
| Вт | Options | В любом disagreement, generate 3+ options |
| Ср | Criteria | Reference objective data в discussion |
| Чт | Separate | Если frustrated, check: problem or person? |
| Пт | BATNA | For ongoing negotiation, strengthen BATNA |

---

## Связанные темы

### Prerequisites
- [[negotiation-fundamentals]] — BATNA, ZOPA, basics

### Эта тема открывает
- [[stakeholder-negotiation]] — applying to execs/PM
- [[salary-negotiation]] — personal negotiation

### Связанные навыки
- [[conflict-resolution]] — negotiation in conflict
- [[saying-no]] — negotiation of boundaries

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Harvard PON: Principled Negotiation](https://www.pon.harvard.edu/daily/negotiation-skills-daily/principled-negotiation-focus-interests-create-value/) | Guide | Core principles |
| 2 | [Getting to Yes Summary](https://www.beyondintractability.org/bksum/fisher-getting) | Book Summary | 4 principles detailed |
| 3 | [Wikipedia: Getting to Yes](https://en.wikipedia.org/wiki/Getting_to_Yes) | Reference | Background |
| 4 | [InLoox: Harvard Principle](https://www.inloox.com/company/blog/articles/getting-to-yes-how-to-negotiate-using-the-harvard-principle/) | Guide | Practical application |
| 5 | [Six Guidelines for Getting to Yes](https://www.pon.harvard.edu/daily/negotiation-skills-daily/six-guidelines-for-getting-to-yes/) | Guide | Extended guidelines |
| 6 | Fisher, Ury, Patton: "Getting to Yes" | Book | Original source |
| 7 | [ReadingGraphics: Book Summary](https://readingraphics.com/book-summary-getting-to-yes/) | Summary | Visual summary |
| 8 | [Triple Session: Harvard Principles](https://triplesession.com/session/the-harvard-principles-of-negotiation-from-the-erich-pommer-institut) | Course | Training perspective |

*Исследование проведено: 2026-01-18*

---

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
