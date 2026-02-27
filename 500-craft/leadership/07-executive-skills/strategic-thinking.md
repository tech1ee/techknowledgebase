---
title: "Стратегическое мышление"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
target-role: [director, vpe, cto]
teaches:
  - strategic vs tactical
  - frameworks
  - decision making
sources: [good-strategy-bad-strategy, playing-to-win]
tags:
  - topic/leadership
  - type/deep-dive
  - level/advanced
related:
  - "[[em-fundamentals]]"
  - "[[technical-vision]]"
  - "[[stakeholder-management]]"
prerequisites:
  - "[[em-fundamentals]]"
  - "[[stakeholder-management]]"
  - "[[engineering-metrics]]"
reading_time: 7
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Стратегическое мышление

> **TL;DR:** Strategy ≠ goals. Strategy = coherent set of choices about WHERE to play and HOW to win. Tactical: решаем текущие проблемы. Strategic: создаём будущее. 80% времени VP+ — strategy и politics, не execution. Learn to zoom out.

---

## Теоретические основы

### Стратегия: от военного искусства к бизнесу

> **Определение:** Стратегическое мышление — способность видеть системные паттерны, определять долгосрочное направление и делать осознанный выбор trade-offs между альтернативами. В контексте technology leadership — умение связывать технические решения с бизнес-результатами на горизонте 1-5 лет.

Richard Rumelt в *"Good Strategy Bad Strategy"* (2011) формализовал ключевое различие между плохой и хорошей стратегией. Плохая стратегия — набор амбициозных целей без конкретного плана. Хорошая стратегия содержит три обязательных компонента: **Diagnosis** (понимание ситуации), **Guiding Policy** (направляющий принцип), **Coherent Actions** (согласованные действия).

| Фреймворк | Автор, год | Ключевая идея | Применение в engineering |
|-----------|-----------|---------------|------------------------|
| **Good Strategy/Bad Strategy** | Rumelt, 2011 | Diagnosis → Policy → Actions | Формулирование tech strategy |
| **Playing to Win** | Lafley & Martin, 2013 | 5 стратегических выборов (where to play, how to win) | Product/platform strategy |
| **Porter's Five Forces** | Michael Porter, 1979 | Конкурентные силы определяют стратегию | Build vs buy, technology moats |
| **Blue Ocean Strategy** | Kim & Mauborgne, 2005 | Создание нового рыночного пространства | Innovation vs optimization |
| **Wardley Mapping** | Simon Wardley, 2016 | Визуализация value chain + evolution | Where to invest, where to outsource |

Michael Porter в *"Competitive Strategy"* (1979) предложил три generic strategies: Cost Leadership, Differentiation, Focus. Для engineering это определяет, куда инвестировать: оптимизация стоимости (infrastructure efficiency), уникальность (proprietary technology), или нише (specialized solutions).

> «The kernel of good strategy contains three elements: a diagnosis, a guiding policy, and coherent action.» — Richard Rumelt, *"Good Strategy Bad Strategy"* (2011)

Roger Martin и A.G. Lafley в *"Playing to Win"* (2013) предложили strategy as a cascade of choices: от winning aspiration через where to play и how to win к необходимым capabilities и management systems. Этот подход особенно ценен для [[technical-vision|технической стратегии]], где каждый уровень каскада транслируется в конкретные архитектурные и инвестиционные решения.

---

## Strategy vs Tactics

```
TACTICS:                        STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• How to win the battle         • Which battles to fight
• Short-term (weeks-months)     • Long-term (years)
• React to problems             • Create opportunities
• Optimize current              • Transform future
• Anyone can do                 • Leaders must do

EXAMPLE:
Tactical: "Fix this bug"
Strategic: "Invest in quality so bugs are rare"

Tactical: "Hire faster"
Strategic: "Build employer brand so hiring is easy"
```

## Good Strategy (Rumelt)

```
BAD STRATEGY:
• Fluffy goals without substance
• "Be the best" without how
• Wish list of objectives
• Avoids hard choices

GOOD STRATEGY HAS 3 PARTS:

1. DIAGNOSIS
   "What's actually going on?"
   Clear understanding of challenge.

2. GUIDING POLICY
   "What's our approach?"
   Overall direction that guides decisions.

3. COHERENT ACTIONS
   "What specifically will we do?"
   Set of actions that implement policy.

EXAMPLE:
Diagnosis: "Our platform is slow, losing users"
Policy: "Prioritize performance over features"
Actions:
• Dedicated performance team
• No new features until latency halved
• Performance budgets for all pages
```

## Strategic Frameworks

```
PLAYING TO WIN (Lafley):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5 strategic choices:
1. What is our winning aspiration?
2. Where will we play?
3. How will we win?
4. What capabilities must we have?
5. What management systems?

PORTER'S GENERIC STRATEGIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Cost leadership: Cheapest
• Differentiation: Unique value
• Focus: Niche market

WARDLEY MAPPING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Map value chain by evolution stage.
Genesis → Custom → Product → Commodity
Where to invest? Where to outsource?
```

## Developing Strategic Skill

```
PRACTICES:

1. ZOOM OUT REGULARLY
   Ask: "What would 10x outcome look like?"
   Not: "How to solve this problem?"

2. SECOND-ORDER THINKING
   "If we do X, then what happens?"
   "And then what?"
   "And then?"

3. TIME HORIZONS
   What's true today vs 1 year vs 5 years?
   Make decisions for where you're going.

4. TRADE-OFF AWARENESS
   Every yes = many nos.
   Explicit trade-offs.

5. LEARN FROM OTHER DOMAINS
   Strategy books (military, business)
   Case studies
   Cross-industry patterns
```

## Common Strategy Mistakes

```
❌ GOALS WITHOUT STRATEGY
"We want 10x revenue" — that's goal, not strategy.

❌ AVOIDING HARD CHOICES
"We'll do everything" — resources are finite.

❌ CONFUSING VISION AND STRATEGY
Vision: where we want to be
Strategy: how we'll get there

❌ COPYING COMPETITORS
Their context ≠ your context.

❌ STRATEGY SET AND FORGOTTEN
Environment changes. Revisit quarterly.
```

---

## Связь с другими темами

**[[em-fundamentals]]** — Стратегическое мышление строится на фундаменте управленческих навыков: невозможно думать стратегически, не освоив тактический уровень менеджмента. EM-фундаментал даёт понимание операционной реальности, на основе которой строятся стратегические решения. По мере карьерного роста от EM к Director и VP доля стратегического мышления в работе возрастает с 10% до 80%.

**[[technical-vision]]** — Техническая стратегия (technical vision) является прямым применением стратегического мышления к технологическому контексту компании. Фреймворки Rumelt (diagnosis → guiding policy → coherent actions) и Playing to Win напрямую используются при формировании технической vision. Стратегическое мышление определяет «куда идём», а technical vision переводит это в конкретные технологические решения и архитектурные принципы.

**[[stakeholder-management]]** — Реализация стратегии невозможна без поддержки ключевых стейкхолдеров. Стратегическое мышление помогает понять контекст и приоритеты каждого стейкхолдера, а навыки influence without authority позволяют продвигать стратегические инициативы. Умение формулировать стратегию в терминах бизнес-ценности для каждого стейкхолдера — это пересечение стратегического мышления и stakeholder management.

## Источники

### Теоретические основы
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Rumelt R. "Good Strategy Bad Strategy" — Crown Business, 2011 | Книга | Diagnosis → Guiding Policy → Coherent Actions |
| 2 | Porter M. "Competitive Strategy" — Free Press, 1979 | Книга | Five Forces, generic strategies |
| 3 | Lafley A.G., Martin R. "Playing to Win" — Harvard Business Review Press, 2013 | Книга | 5 стратегических выборов |
| 4 | Kim W.C., Mauborgne R. "Blue Ocean Strategy" — Harvard Business Review Press, 2005 | Книга | Создание нового рыночного пространства |
| 5 | Wardley S. "Wardley Maps" — 2016 | Книга/Open Source | Value chain mapping, evolution stages |

### Практические руководства
| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | Drucker P. "The Effective Executive" — Harper Business, 2006 | Книга | Effectiveness practices |
| 2 | Horowitz B. "The Hard Thing About Hard Things" — Harper Business, 2014 | Книга | Strategic decision-making under pressure |
| 3 | Ries E. "The Lean Startup" — Crown Business, 2011 | Книга | Iterative strategy through experimentation |


## Проверь себя

> [!question]- Good Strategy по Rumelt
> CTO объявляет: 'Наша стратегия — стать лучшей платформой на рынке'. Используя framework Rumelt (diagnosis, guiding policy, coherent actions), объясните почему это bad strategy и трансформируйте в good strategy с конкретными тремя компонентами.

> [!question]- Second-order thinking
> Вы решили внедрить mandatory code review для всех PRs. First-order: code quality улучшится. Используя second-order thinking, продумайте 2-3 уровня последствий. Что произойдёт дальше? И потом?

## Ключевые карточки

Чем strategy отличается от tactics?
?
Tactics: how to win the battle, short-term, react to problems, anyone can do. Strategy: which battles to fight, long-term, create opportunities, leaders must do.

Назови 3 части Good Strategy по Rumelt.
?
1. Diagnosis — 'What's actually going on?' (clear understanding of challenge). 2. Guiding Policy — 'What's our approach?' (direction for decisions). 3. Coherent Actions — 'What specifically will we do?' (implementing policy).

Что такое Playing to Win framework (Lafley)?
?
5 strategic choices: 1. What is our winning aspiration? 2. Where will we play? 3. How will we win? 4. What capabilities must we have? 5. What management systems?

Назови 5 ошибок стратегического мышления.
?
Goals without strategy, avoiding hard choices ('do everything'), confusing vision and strategy, copying competitors, strategy set and forgotten.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[technical-vision]] | Применение стратегии к технологии |
| Углубиться | [[budget-planning]] | Бюджет как финансовое выражение стратегии |
| Смежная тема | [[systems-thinking]] | Системное мышление как основа стратегии |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
