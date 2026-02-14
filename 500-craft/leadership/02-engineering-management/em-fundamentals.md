---
title: "Engineering Management: Фундаментальные принципы"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
reading_time: 30
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
difficulty: intermediate
target-role: [tech-lead, em, director]
teaches:
  - понимание роли EM
  - ключевые ответственности
  - метрики успеха
sources: [manager-tools, rands-in-repose, camille-fournier, google-rework]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[ic-vs-management]]"
  - "[[tech-lead-role]]"
  - "[[transition-to-management]]"
  - "[[one-on-one-meetings]]"
  - "[[performance-management]]"
prerequisites:
  - "[[ic-vs-management]]"
---

# Engineering Management: Фундаментальные принципы

> **TL;DR:** Engineering Manager — это не "старший программист, который ещё и руководит". Это отдельная профессия с собственными навыками. Главная метрика успеха: не твой код, а output команды × их рост × retention. 70% времени — работа с людьми.

---

## Зачем это нужно?

### Типичная ситуация

Сильного инженера повысили до EM. Первые месяцы он продолжает писать код, "помогая" команде. На 1-on-1 разговаривает о технических задачах. Performance review откладывает. Через год — выгорание, текучка в команде, и сам хочет вернуться в IC.

**Без понимания фундамента EM:**
- 60% новых менеджеров fail в первые 2 года (DDI Research)
- Команда теряет и senior IC, и не получает хорошего менеджера
- Turnover в командах без хороших EM на 50% выше

**С пониманием фундамента:**
- Чёткое разделение ролей и ожиданий
- Команда растёт и delivery улучшается
- EM развивается в своей роли

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Влияние менеджера на engagement | 70% variance | Gallup |
| Новые EM, терпящие неудачу | 60% | DDI Research |
| Сотрудники, уходящие из-за менеджера | 50% | Gallup |
| ROI инвестиций в менеджеров | 300%+ | McKinsey |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **Senior IC** | High | Понять, что ждёт при переходе |
| **Tech Lead** | Critical | Отличия TL от EM |
| **New EM** | Critical | Фундамент для старта |
| **Experienced EM** | Medium | Проверить gaps |
| **Director+** | Medium | Понимать своих EM |

---

## Терминология

| Термин | Определение | IT-аналогия |
|--------|-------------|-------------|
| **Engineering Manager** | Руководитель, ответственный за людей, процессы и delivery команды | Не архитектор кода, а архитектор команды |
| **People Management** | Развитие, мотивация, retention инженеров | Memory management — но для людей |
| **Span of Control** | Количество direct reports | Thread pool size — оптимум 5-9 |
| **Output** | Результаты работы команды | Не KLOC, а delivered value |
| **Multiplier Effect** | Когда EM увеличивает output всей команды | Кэширование — ускоряет всю систему |

### Распространённые заблуждения

| Заблуждение | Реальность |
|-------------|------------|
| "EM — это promotion" | Это career change, другая профессия |
| "Хороший IC = хороший EM" | Разные навыки, корреляция слабая |
| "EM должен быть лучшим техническим" | Важнее: judgment, не expertise |
| "EM не пишет код" | Пишет меньше, но технический контекст нужен |
| "Менеджмент — это контроль" | Это enablement и service |

---

## Как это работает?

### Модель ответственности EM

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENGINEERING MANAGER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │     PEOPLE      │  │    DELIVERY     │  │    PROCESS      │  │
│  │    40-50%       │  │    25-30%       │  │    15-20%       │  │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  │
│  │ • 1-on-1s       │  │ • Project       │  │ • Ceremonies    │  │
│  │ • Hiring        │  │   tracking      │  │ • Code review   │  │
│  │ • Growth        │  │ • Dependencies  │  │   standards     │  │
│  │ • Performance   │  │ • Stakeholder   │  │ • On-call       │  │
│  │ • Retention     │  │   comms         │  │ • Tech debt     │  │
│  │ • Culture       │  │ • Risk mgmt     │  │ • Documentation │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    TECHNICAL (5-15%)                     │   │
│  │   Architecture input • Code review • Technical decisions │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Три фундаментальных принципа

**1. Servant Leadership**
```
Традиционное мышление:    Servant Leadership:
     [Manager]                 [Team]
         ↓                       ↑
      [Team]                 [Manager]
   "Команда для меня"      "Я для команды"
```

Твоя работа — убирать препятствия, давать ресурсы, создавать условия для лучшей работы.

**2. Multiplier vs Diminisher**
```
DIMINISHER:                    MULTIPLIER:
• Micromanagement              • Context + autonomy
• "Я знаю лучше"               • "Что думаешь?"
• Собирает talent              • Развивает talent
• Создаёт зависимость          • Создаёт независимость

Result: 50% capacity           Result: 200% capacity
```

**3. Psychological Safety**
```
Google Project Aristotle:
5 факторов эффективных команд (по важности):

#1 ████████████████████████ Psychological Safety
#2 ████████████████████ Dependability
#3 ██████████████████ Structure & Clarity
#4 ████████████████ Meaning
#5 ██████████████ Impact

Psychological Safety = можно рисковать без страха наказания
```

---

## Ежедневная работа EM

### Типичная неделя

```
ПОНЕДЕЛЬНИК:
┌────────────────────────────────────────────────┐
│ 09:00  Team standup (15 min)                   │
│ 09:30  Planning buffer / async catch-up        │
│ 10:00  1-on-1 (Alice)                          │
│ 11:00  1-on-1 (Bob)                            │
│ 12:00  Lunch                                   │
│ 13:00  Sprint planning / Backlog grooming      │
│ 15:00  Director sync                           │
│ 16:00  Focus time: docs, planning, admin       │
└────────────────────────────────────────────────┘

ВТОРНИК-ЧЕТВЕРГ:
┌────────────────────────────────────────────────┐
│ 09:00  Standup                                 │
│ 09:30  1-on-1 (2-3 per day)                    │
│ 11:00  Cross-team sync / stakeholder meetings  │
│ 13:00  Focus time: interviews, reviews, docs   │
│ 15:00  Architecture review / tech discussions  │
│ 16:00  Ad-hoc support, blockers                │
└────────────────────────────────────────────────┘

ПЯТНИЦА:
┌────────────────────────────────────────────────┐
│ 09:00  Standup                                 │
│ 10:00  Team retro (bi-weekly)                  │
│ 11:00  Demo / showcase                         │
│ 13:00  Week planning for next week             │
│ 14:00  Learning time / tech exploration        │
│ 16:00  Week reflection, prep for next week     │
└────────────────────────────────────────────────┘
```

### Время на задачи (в неделю)

| Категория | Часы | Активности |
|-----------|------|------------|
| 1-on-1s | 5-7 | 30-60 min × 5-8 reports |
| Meetings | 8-10 | Standups, planning, stakeholders |
| Hiring | 3-5 | Sourcing, interviews, debrief |
| Admin | 2-3 | Expenses, docs, approvals |
| Focus time | 5-10 | Planning, strategy, docs |
| Ad-hoc | 5-8 | Blockers, escalations, support |
| Technical | 2-5 | Code review, architecture |

---

## Метрики успеха EM

### Team Health Metrics

```
┌─────────────────────────────────────────────────────────────┐
│                   TEAM HEALTH DASHBOARD                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DELIVERY                      PEOPLE                       │
│  ─────────                     ──────                       │
│  Velocity trend: ↑ 15%         Retention: 95%               │
│  Sprint commitment: 85%        eNPS: +45                    │
│  Cycle time: 3.2 days          Growth: 3/5 promoted         │
│  Bug escape rate: 2%           Engagement: 4.2/5            │
│                                                             │
│  PROCESS                       TECHNICAL                    │
│  ───────                       ─────────                    │
│  PR review time: 4h            Tech debt ratio: 20%         │
│  Meeting load: 25%             Test coverage: 78%           │
│  Documentation: Current        Incidents: 2/month           │
│  On-call burden: Fair          Deploy frequency: Daily      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Ключевые индикаторы

**Lagging Indicators (результаты):**
- Team velocity / throughput
- Quality metrics (bugs, incidents)
- Retention rate
- Promotion rate

**Leading Indicators (предсказатели):**
- 1-on-1 качество и регулярность
- Skip-level feedback
- Team engagement scores
- Psychological safety index

### The Rands Test

11 вопросов для оценки здоровья команды:

```
□ 1. Есть ли регулярные 1-on-1?
□ 2. Есть ли регулярные team meetings?
□ 3. У каждого понятны текущие приоритеты?
□ 4. Есть ли status report?
□ 5. Можно ли найти информацию без спроса?
□ 6. Участвует ли менеджер в hiring?
□ 7. Можно ли не согласиться с менеджером?
□ 8. Знает ли команда стратегию компании?
□ 9. Понятен ли карьерный путь каждому?
□ 10. Делается ли что-то нетехническое вместе?
□ 11. Есть ли back-channel feedback?

Scoring: 8+ = healthy, 5-7 = at risk, <5 = red flag
```

---

## Пошаговый процесс

### Как оценить состояние команды (первые 30 дней)

**Шаг 1: Собери данные**
```
КОЛИЧЕСТВЕННЫЕ:
□ Velocity за 3-6 месяцев
□ Bug/incident trends
□ Turnover история
□ Survey results (если есть)

КАЧЕСТВЕННЫЕ:
□ 1-on-1 с каждым (first 2 weeks)
□ Skip-level (если ты не первый EM)
□ Stakeholder interviews
□ Team observation (meetings, slack)
```

**Шаг 2: Найди паттерны**
```
СИГНАЛЫ ПРОБЛЕМ:
• Velocity падает при стабильном headcount
• Много "critical" bugs
• Люди избегают определённых тем
• Низкая активность на meetings
• Slack молчит или токсичен

СИГНАЛЫ ЗДОРОВЬЯ:
• Velocity стабильна или растёт
• Люди предлагают идеи
• Конструктивные споры
• Помощь между членами команды
• Смех и шутки
```

**Шаг 3: Приоритизируй actions**
```
СРОЧНО (первые 30 дней):
• Trust issues
• Unclear expectations
• Critical blockers

ВАЖНО (30-60 дней):
• Process inefficiencies
• Growth opportunities
• Technical debt

СТРАТЕГИЧЕСКИ (60-90 дней):
• Career paths
• Team structure
• Long-term vision
```

---

## Скрипты и Templates

### 1-on-1 opening questions

**Первая встреча:**
```
"Как тебе лучше всего даётся feedback —
письменно или устно, сразу или нужно время?"

"Какой стиль менеджмента тебя мотивирует,
а какой демотивирует?"

"Что бы ты хотел, чтобы я знал о тебе?"
```

**Регулярные 1-on-1:**
```
"Что занимает твои мысли на этой неделе?"

"Что могу сделать, чтобы помочь тебе быть
более эффективным?"

"Есть ли что-то, что я должен знать,
но возможно не знаю?"
```

### Feedback формулы

**SBI (Situation-Behavior-Impact):**
```
"Вчера на code review [ситуация]
ты отклонил PR без объяснения [поведение].
Это демотивировало junior-разработчика [impact]."
```

**COIN (Context-Observation-Impact-Next):**
```
"В спринте [context],
я заметил что tasks часто переоткрываются [observation].
Это влияет на velocity [impact].
Давай обсудим, как улучшить definition of done [next]."
```

### Status report template

```markdown
## Team [Name] — Week of [Date]

### Highlights
- [Major accomplishment]
- [Major accomplishment]

### Lowlights / Risks
- [Issue] — [Mitigation]
- [Risk] — [Plan]

### Key Metrics
| Metric | This Week | Trend |
|--------|-----------|-------|
| Velocity | X | ↑/↓/→ |
| Open bugs | X | ↑/↓/→ |

### Next Week Focus
1. [Priority 1]
2. [Priority 2]

### Needs from Leadership
- [Ask if any]
```

---

## Распространённые ошибки

### Ошибка 1: Продолжать писать код

**Как выглядит:**
EM берёт critical tasks "потому что быстрее сам". Команда ждёт его решений. EM работает 60+ часов.

**Почему это проблема:**
- Bottleneck на EM
- Команда не растёт
- EM выгорает
- Single point of failure

**Как исправить:**
```
Вместо: "Я это сделаю"
Делай:  "Как бы ты это решил? Давай обсудим."

Вместо: Писать код
Делай:  Code review с обучающим feedback
```

### Ошибка 2: Избегать сложных разговоров

**Как выглядит:**
Performance issue не обсуждается месяцами. Токсичный инженер остаётся. Проблемы копятся.

**Почему это проблема:**
- Команда страдает
- Top performers уходят
- Проблема растёт exponentially

**Как исправить:**
```
Правило 24 часов: Если видишь проблему,
начни разговор в течение 24 часов.

Script: "Я заметил [behavior].
Это влияет на [impact].
Можем обсудить?"
```

### Ошибка 3: "Busy" ≠ "Effective"

**Как выглядит:**
Календарь забит meetings. Inbox под контролем. Но команда не растёт, delivery не улучшается.

**Почему это проблема:**
- Activity ≠ Results
- Нет времени на стратегическое мышление
- Реактивный режим

**Как исправить:**
```
Аудит календаря:
- Какие meetings можно отменить?
- Какие можно делегировать?
- Где нужен я лично?

Правило: 20% времени на важное-но-не-срочное
```

### Ошибка 4: Игнорировать свой рост

**Как выглядит:**
EM так занят командой, что не развивает собственные навыки. Через 2 года — те же инструменты, что в начале.

**Как исправить:**
```
Блокируй время на обучение (2-4 часа/неделю):
□ Книги по менеджменту
□ Менторство (получать и давать)
□ EM community (Rands Slack, LeadDev)
□ Conferences / talks
```

---

## Когда применять

### Этот материал полезен, когда:

- Только стал EM или думаешь о переходе
- Чувствуешь, что что-то не так, но не понимаешь что
- Команда не растёт несмотря на усилия
- Хочешь проверить свой подход

### НЕ применяй напрямую, когда:

- Кризис требует hands-on involvement (но временно)
- Команда из 1-2 человек (больше TL, чем EM)
- Founding team стартапа (другие правила)

### Trade-offs подхода

| За | Против |
|----|--------|
| Масштабируемость | Медленнее на старте |
| Рост команды | Меньше личного delivery |
| Sustainable pace | Требует терпения |
| Retention | Нужны soft skills |

---

## Кейсы

### Google: Project Oxygen

**Контекст:** Google хотел доказать, что менеджеры не нужны. Провёл исследование.

**Что обнаружили:**
Менеджеры критичны. Определили 8 качеств лучших менеджеров:

```
1. Хороший коуч
2. Empowers team, не micromanages
3. Интересуется success и well-being людей
4. Продуктивен и results-oriented
5. Хороший коммуникатор
6. Помогает с career development
7. Имеет чёткое vision и strategy
8. Технические навыки для advice команде
```

**Результат:** Команды с лучшими менеджерами на 25% продуктивнее.

### Netflix: Freedom & Responsibility

**Контекст:** Netflix отказался от традиционного менеджмента.

**Что сделали:**
- Нет approval process для expenses
- Unlimited vacation
- "Context, not control"
- Высокий talent density

**Урок:** EM-фундамент не про процедуры, а про культуру и доверие. Работает при высокой планке найма.

### Stripe: Manager README

**Контекст:** Stripe формализовал expectations от менеджеров.

**Что сделали:**
Каждый менеджер пишет README:
- Как предпочитаю коммуникацию
- Что меня triggers
- Как даю feedback
- Чего ожидаю от команды

**Результат:** Быстрее onboarding, меньше friction в отношениях.

---

## Связанные темы

### Prerequisites
- [[ic-vs-management]] — понять, твой ли это путь
- [[tech-lead-role]] — отличия TL от EM

### Следующие шаги
- [[transition-to-management]] — как перейти из IC
- [[one-on-one-meetings]] — главный инструмент EM
- [[performance-management]] — оценка и развитие
- [[delegation]] — как отпустить контроль

### Связи с другими разделами
- [[communication/giving-feedback]] — техники feedback
- [[communication/difficult-conversations]] — сложные разговоры
- [[career/growth/]] — карьерное развитие

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [The Manager's Path](https://www.oreilly.com/library/view/the-managers-path/9781491973882/) | Book | Framework EM ответственностей |
| 2 | [High Output Management](https://www.goodreads.com/book/show/324750.High_Output_Management) | Book | Метрики, leverage |
| 3 | [Google re:Work](https://rework.withgoogle.com/) | Research | Project Oxygen, Aristotle |
| 4 | [Rands in Repose](https://randsinrepose.com/) | Blog | Практические советы EM |
| 5 | [Gallup Manager Research](https://www.gallup.com/workplace/insights.aspx) | Research | Impact statistics |
| 6 | [DDI Leadership Research](https://www.ddiworld.com/) | Research | Failure rates |
| 7 | [Manager Tools Podcast](https://www.manager-tools.com/) | Podcast | Tactical advice |
| 8 | [First Round Review](https://review.firstround.com/) | Articles | Case studies |

### Дополнительное чтение

- "An Elegant Puzzle" by Will Larson — для senior EM
- "Radical Candor" by Kim Scott — feedback culture
- "Multipliers" by Liz Wiseman — leverage через людей
- "The Five Dysfunctions of a Team" by Patrick Lencioni — team health

---

## Связь с другими темами

**[[ic-vs-management]]** — Понимание фундаментальных различий между IC и management треками — необходимый prerequisite для осознанного вхождения в роль EM. Без чёткого понимания, что management — это career change, а не promotion, новые EM часто пытаются совмещать обе роли и терпят неудачу. Ic-vs-management помогает сформировать правильные ожидания до перехода.

**[[tech-lead-role]]** — Tech Lead и EM формируют партнёрство, которое определяет успех команды. Понимание границ между ролями (TL — технология, EM — люди) предотвращает конфликты и обеспечивает полное покрытие всех аспектов командной работы. Многие EM приходят из Tech Lead роли, и умение отпустить технический контроль — одна из ключевых задач фундамента EM.

**[[transition-to-management]]** — Transition-to-management описывает сам процесс перехода из IC в EM, тогда как em-fundamentals фокусируется на навыках и практиках уже в роли. Вместе эти материалы покрывают полный цикл: от принятия решения о переходе до уверенной работы в новой роли. Identity shift, coding withdrawal и другие вызовы перехода нужно преодолеть, чтобы начать применять фундаментальные принципы EM.

**[[one-on-one-meetings]]** — 1-on-1 — главный инструмент в арсенале EM, и качество их проведения напрямую определяет успех менеджера. Через 1-on-1 реализуются все ключевые обязанности EM: feedback, career development, coaching, выявление проблем. Менеджер без хороших 1-on-1 — как инженер без IDE: формально может работать, но неэффективно.

**[[performance-management]]** — Performance management — это одна из наиболее сложных и ответственных частей работы EM. Фундамент EM закладывает понимание того, почему continuous feedback важнее годовых review, и как выстроить culture of growth. Навыки performance management определяют, будет ли команда расти или стагнировать.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Главная книга для Engineering Manager на любом этапе карьеры. Детально описывает обязанности, навыки и типичные ошибки на каждом уровне от Tech Lead до CTO. Должна быть прочитана в первый месяц работы EM.
- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — Модель пяти дисфункций команды помогает EM диагностировать проблемы и строить здоровые, высокоэффективные команды. Фокус на trust как фундаменте всего остального напрямую связан с принципом psychological safety.
- **L. David Marquet, "Turn the Ship Around!" (2012)** — Демонстрирует модель servant leadership на практике, показывая, как создать среду, где люди принимают решения сами. Intent-based leadership — альтернатива микроменеджменту, одной из главных ошибок новых EM.

---

---

## Проверь себя

> [!question]- Почему Servant Leadership эффективнее традиционной модели для Engineering Manager?
> В традиционной модели команда работает на менеджера. В Servant Leadership менеджер работает на команду -- убирает препятствия, даёт ресурсы, создаёт условия. Это создаёт multiplier effect: вместо 50% capacity (diminisher) достигается 200% capacity (multiplier), потому что люди получают autonomy и context вместо micromanagement.

> [!question]- EM заполнил весь календарь meetings, inbox под контролем, но команда не растёт и delivery не улучшается. В чём проблема?
> Activity не равно Results. EM в реактивном режиме без стратегического мышления. Нужен аудит календаря: какие meetings можно отменить/делегировать, 20% времени заблокировать на важное-но-не-срочное. "Busy" не значит "Effective".

> [!question]- Что такое The Rands Test и какой score является red flag?
> 11 вопросов о здоровье команды: регулярные 1-on-1, team meetings, понятные приоритеты, status report, доступность информации, hiring participation, disagreement safety, знание стратегии, career paths, нетехнические активности, back-channel feedback. Score <5 = red flag, требующий немедленных действий.

---

## Ключевые карточки

Какие три фундаментальных принципа EM?
?
1) Servant Leadership -- менеджер работает на команду, не наоборот. 2) Multiplier vs Diminisher -- создавать независимость, а не зависимость. 3) Psychological Safety -- можно рисковать без страха наказания (фактор #1 по Google Aristotle).

Какое влияние менеджер оказывает на engagement команды?
?
70% variance в engagement определяется менеджером (Gallup). 50% сотрудников уходят из-за менеджера. ROI инвестиций в менеджеров -- 300%+. Это делает quality of management самым важным фактором retention.

Что показало исследование Google Project Oxygen?
?
Google хотел доказать, что менеджеры не нужны, но обнаружил обратное. 8 качеств лучших менеджеров: хороший коуч, empowers team, интересуется well-being, results-oriented, хороший коммуникатор, помогает с career, чёткое vision, технические навыки. Команды с лучшими менеджерами на 25% продуктивнее.

Какие leading indicators предсказывают успех EM?
?
Leading indicators: качество и регулярность 1-on-1, skip-level feedback, team engagement scores, psychological safety index. Lagging indicators (результаты): team velocity, quality metrics, retention rate, promotion rate. Leading indicators позволяют действовать проактивно.

Какие формулы feedback наиболее эффективны?
?
SBI (Situation-Behavior-Impact): "Вчера на code review [S] ты отклонил PR без объяснения [B]. Это демотивировало junior [I]." COIN (Context-Observation-Impact-Next): добавляет следующий шаг. Ключ: конкретное поведение, не интерпретация мотивов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[one-on-one-meetings]] | Освоить главный инструмент EM |
| Углубиться | [[performance-management]] | Оценка и развитие инженеров |
| Смежная тема | [[cognitive-biases]] | Когнитивные искажения влияют на management decisions |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-02-13*
*Связано с: [[leadership-overview]]*
