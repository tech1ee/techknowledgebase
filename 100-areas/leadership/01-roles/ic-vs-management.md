---
title: "IC Track vs Management Track: как выбрать"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [senior, staff, tech-lead, em]
teaches:
  - Различия IC и Management tracks
  - Self-assessment для выбора
  - Engineer/Manager Pendulum
sources: [charity.wtf, staffeng.com, pragmaticengineer, leaddev]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[transition-to-management]]"
  - "[[em-fundamentals]]"
---

# IC Track vs Management Track: как выбрать

> **TL;DR:** IC (Individual Contributor) track ведёт к Staff → Principal → Distinguished Engineer. Management track — к EM → Director → VP. Это **не** вопрос "лучше/хуже" — это разные роли с разным фокусом.
>
> **Главное заблуждение:** "Management — это promotion". Нет. Это career change. Другие навыки, другой feedback loop, другой источник satisfaction.
>
> **Charity Majors' insight:** "The Engineer/Manager Pendulum" — можно переключаться между треками каждые 3-5 лет. Это не "назад", это накопление разных skills.

---

## Зачем это понимать?

### Типичная ситуация

Тебе 5-7 лет опыта. Ты Senior Engineer, и manager говорит: "Хочешь попробовать management? У нас открывается позиция Tech Lead/EM". Без ясного понимания:

**Без понимания:**
- Соглашаешься "потому что это следующий шаг" (спойлер: нет)
- Обнаруживаешь, что ненавидишь 1-on-1 и performance reviews
- Через год burnout и мысли "я плохой менеджер"
- Или: отказываешься, думая что "остаёшься на месте"

**С пониманием:**
- Осознанный выбор на основе сильных сторон
- Знаешь, что IC track — это полноценный путь к Principal/Distinguished
- Можешь попробовать и вернуться (pendulum)
- Compensation comparable на обоих треках

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| % инженеров выбирающих IC track | ~70% | Pragmatic Engineer |
| Staff+ инженеров в Big Tech | ~15% | levels.fyi |
| Новых EM терпящих неудачу за 2 года | 60% | Harvard Business |
| TC Staff (L6) vs EM в Google | Comparable (~$500K) | levels.fyi |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **Mid Engineer** | Medium | Начинай думать о направлении |
| **Senior Engineer** | Critical | Момент выбора обычно здесь |
| **Tech Lead** | Critical | Определить: IC или EM |
| **Junior EM** | High | Проверить, правильный ли выбор |
| **Staff Engineer** | Medium | Подтвердить выбор IC |

---

## Терминология

| Термин | Определение | Примеры ролей |
|--------|-------------|---------------|
| **IC (Individual Contributor)** | Технический специалист без direct reports | Staff, Principal, Distinguished |
| **Management Track** | Руководитель с direct reports | EM, Director, VP |
| **Tech Lead** | Hybrid роль: technical leadership + coordination | Может быть входом в оба трека |
| **Terminal Level** | Уровень где нет expectation дальнейшего роста | Senior (L5) в большинстве компаний |

### Распространённые заблуждения

| Заблуждение | Реальность |
|-------------|------------|
| "Management — promotion" | Это career change, не promotion |
| "IC track — потолок Senior" | Staff → Principal → Distinguished |
| "Менеджеры зарабатывают больше" | TC comparable на аналогичных уровнях |
| "Менеджеры не кодируют" | EM может кодировать 10-20% |
| "Staff — это менеджер без direct reports" | Staff — про technical leadership и scope |

---

## Сравнение треков

### Основные различия

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    IC TRACK vs MANAGEMENT TRACK                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│         IC TRACK                         MANAGEMENT TRACK                │
│         ────────                         ─────────────────               │
│                                                                          │
│    ┌───────────────┐                    ┌───────────────┐               │
│    │   Technical   │                    │    People     │               │
│    │   Leverage    │                    │   Leverage    │               │
│    └───────────────┘                    └───────────────┘               │
│                                                                          │
│    Impact через:                        Impact через:                   │
│    • Архитектуру                        • Hiring                        │
│    • Code & Design                      • Team building                 │
│    • Technical influence                • Coaching                      │
│    • Mentoring (not managing)           • Removing blockers             │
│                                                                          │
│    Feedback loop: быстрый               Feedback loop: медленный        │
│    (код работает/не работает)           (люди растут через месяцы)      │
│                                                                          │
│    Stress: технические проблемы         Stress: interpersonal issues    │
│                                                                          │
│    Meetings: 30-50%                     Meetings: 60-80%                │
│    Coding: 20-50%                       Coding: 0-20%                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Детальное сравнение

| Аспект | IC Track (Staff+) | Management Track |
|--------|-------------------|------------------|
| **Главный output** | Technical decisions, architecture | Team performance |
| **Leverage** | Через системы и влияние | Через людей |
| **Feedback loop** | Дни-недели (код работает) | Месяцы-годы (люди растут) |
| **Meetings** | 30-50% | 60-80% |
| **Coding** | 20-50% | 0-20% |
| **1-on-1** | Mentoring (не обязательно) | Performance mgmt (обязательно) |
| **Career options** | Меньше позиций, выше специализация | Больше позиций, шире scope |
| **Stress type** | Technical debt, scaling issues | People problems, politics |
| **Compensation** | Comparable | Comparable |

### Career Ladders

```
IC TRACK                           MANAGEMENT TRACK
════════                           ════════════════

Distinguished (L10)                VP Engineering
      │                                  │
Principal (L8)                     Director
      │                                  │
Sr Staff (L7)                      Sr Engineering Manager
      │                                  │
Staff (L6)          ←─────────→    Engineering Manager
      │                                  │
════════════════════════════════════════════════════════
▲ Здесь обычно происходит выбор (Senior L5) ▲
════════════════════════════════════════════════════════
      │
Senior (L5) — Terminal Level
      │
Software Engineer (L4)
      │
Junior (L3)
```

---

## Self-Assessment: какой трек твой

### Checklist: IC Track

```
□ Получаю энергию от решения технических проблем
□ Предпочитаю глубокую работу над meetings
□ Комфортно с тем, что меня оценивают по коду/архитектуре
□ Не особо нравятся difficult conversations с людьми
□ Быстрый feedback важен (хочу видеть результат)
□ Идеальный день = 4+ часа deep work
□ "Люди — это сложно" (не в негативном смысле)
□ Технические книги читаю охотнее чем про management
□ Влияние через код и документы > через meetings

6+ из 9 = Strong IC fit
```

### Checklist: Management Track

```
□ Получаю энергию от помощи другим расти
□ Комфортно с difficult conversations (feedback, performance)
□ Могу работать без видимого прогресса месяцами
□ Нравится строить команды и культуру
□ "Мой успех = успех команды" — это ок
□ Идеальный день = помог 3-4 людям разблокироваться
□ Политика и stakeholder management — это интересно
□ Готов отпустить coding (не полностью, но значительно)
□ Influence через relationships > через code

6+ из 9 = Strong Management fit
```

### Red Flags: не иди в management если...

```
❌ "Это единственный путь роста в моей компании"
   → Ищи компанию с IC track

❌ "Хочу больше денег"
   → TC comparable, это не аргумент

❌ "Устал от coding"
   → Burnout решается иначе, не career change

❌ "Менеджеры ничего не делают, легко"
   → Серьёзное заблуждение

❌ "Хочу контроль над решениями"
   → Staff/Principal дают influence без людей
```

### Red Flags: не оставайся на IC если...

```
❌ "Боюсь difficult conversations"
   → Это навык, его можно развить

❌ "Люди — это слишком сложно"
   → Staff тоже требует people skills

❌ "Не хочу ответственности"
   → Staff = огромная ответственность (другая)
```

---

## The Engineer/Manager Pendulum (Charity Majors)

### Концепция

Charity Majors предлагает не думать о выборе как о "одном навсегда". Можно переключаться:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE ENGINEER/MANAGER PENDULUM                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    Year 0-5        Year 5-8        Year 8-11       Year 11-14           │
│    ───────         ────────        ─────────       ──────────           │
│                                                                          │
│    Engineer    →   Manager     →   Engineer    →   Manager              │
│    (build      (build people   (stay          (leverage                │
│    skills)     skills)         technical)     both)                    │
│                                                                          │
│    ════════════════════════════════════════════════════════════════     │
│    Каждый swing добавляет perspective, которого нет у "чистых" людей   │
│    ════════════════════════════════════════════════════════════════     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Преимущества Pendulum

| Преимущество | Почему важно |
|--------------|--------------|
| **Broader perspective** | Понимаешь обе стороны |
| **Empathy** | EM понимает инженеров, и наоборот |
| **Avoid staleness** | Новые challenge каждые 3-5 лет |
| **Career optionality** | Можешь занять любую роль |
| **Avoid burnout** | Смена контекста освежает |

### Как переключаться

**IC → Management:**
- Начни с Tech Lead роли (hybrid)
- Попроси 1-2 direct reports
- Formal training по management
- Ожидай 6-12 месяцев transition

**Management → IC:**
- Честно поговори с hiring manager
- Будь готов к "downlevel" по title (EM → Senior IC)
- Покажи, что technical skills актуальны
- Ожидай вопросов "почему назад?"

### Как объяснять "step back" на интервью

```
НЕ ГОВОРИ:
"Management не для меня" (звучит как failure)
"Я ненавижу meetings" (negative)

ГОВОРИ:
"I've done both, and I want to maximize my impact
 through technical work at this stage of my career"

"I loved management and learned a lot. Now I want to
 apply that perspective while focusing on architecture"

"I believe in the pendulum approach —
 I've managed teams, now I want deep technical work"
```

---

## Day-in-the-Life сравнение

### Staff Engineer: типичный день

```
8:00  Deep work: architecture design doc
9:30  Coffee break (отдых важен для deep work)
10:00 Code review для 2-3 PRs (thoughtful feedback)
11:00 Design review meeting (facilitate, not decide)
12:00 Lunch
13:00 1-on-1 mentoring (junior engineer)
13:30 Deep work: prototyping new approach
15:30 RFC sync meeting (present trade-offs)
16:30 Reading: industry blog posts, papers
17:00 End of day

Meetings: ~4 hours (40%)
Coding/Design: ~4 hours (40%)
Reading/Learning: ~1 hour (10%)
```

### Engineering Manager: типичный день

```
8:00  Check Slack, email, priorities for team
8:30  1-on-1 with Senior Engineer
9:00  1-on-1 with Mid Engineer
9:30  1-on-1 with Junior Engineer
10:00 Sprint planning meeting
11:00 Hiring: resume review
11:30 Interview: phone screen
12:00 Lunch
13:00 Staff meeting with Director
14:00 Performance review prep
15:00 Cross-team alignment meeting
16:00 Blocking time: think about team roadmap
16:30 Quick Slack responses accumulated
17:00 Check tomorrow's calendar

Meetings: ~6 hours (60%)
1-on-1s: ~2 hours (20%)
Admin/Prep: ~1 hour (10%)
Strategic thinking: ~1 hour (10%)
```

---

## Compensation: реально ли comparable?

### Big Tech (US, 2025-2026)

| Level | IC Title | IC TC | Mgmt Title | Mgmt TC |
|-------|----------|-------|------------|---------|
| L6 | Staff Engineer | $450-600K | Engineering Manager | $400-550K |
| L7 | Sr Staff Engineer | $600-900K | Sr EM | $550-750K |
| L8 | Principal Engineer | $800K-1.2M | Director | $700K-1M |

*TC = Total Compensation (base + stock + bonus)*
*Source: levels.fyi, 2025-2026*

**Вывод:** IC TC часто даже выше на том же уровне. "Management pays more" — миф.

### Startup: другая картина

В стартапах IC track часто менее развит:
- Может не быть Staff/Principal titles
- Management = путь к equity influence
- Решение: выбирать компании с strong IC track

---

## Скрипты и Templates

### Сценарий 1: Менеджер предлагает перейти в EM

**Вопросы которые нужно задать:**

```
"Какие конкретно обязанности будут у меня как EM?"

"Сколько direct reports? Кто они?"

"Какой % времени на coding реалистичен?"

"Какая поддержка для first-time managers?"

"Могу ли я вернуться на IC track если пойму,
 что management — не моё?"

"Как выглядит IC track в компании?
 Есть ли Staff/Principal?"
```

### Сценарий 2: Выбор между IC offer и EM offer

**Framework для решения:**

```
┌───────────────────────────────────────────────┐
│         DECISION FRAMEWORK                     │
├───────────────────────────────────────────────┤
│                                               │
│  1. Что даёт больше энергии сейчас?          │
│     [ ] Technical problems                    │
│     [ ] Helping people grow                   │
│                                               │
│  2. Где я хочу быть через 5 лет?             │
│     [ ] Principal/Distinguished              │
│     [ ] VP/Director                           │
│                                               │
│  3. Что company культура поддерживает?       │
│     [ ] Strong IC track                       │
│     [ ] Management-heavy                      │
│                                               │
│  4. Reversibility?                            │
│     [ ] Легко вернуться на IC                │
│     [ ] Сложно вернуться                      │
│                                               │
└───────────────────────────────────────────────┘
```

### Template: Career Discussion с Manager

```
Тема: Career direction discussion

Хочу обсудить мой career path. У меня вопросы:

1. Как выглядит IC track в нашей компании?
   - Есть ли Staff/Principal позиции?
   - Примеры людей на этих ролях?

2. Как выглядит Management track?
   - Какой timeline Senior → EM?
   - Какая поддержка для новых менеджеров?

3. Что ты видишь как мои сильные стороны?
   - Technical leadership?
   - People leadership?

4. Можем ли мы составить plan на следующие 12 месяцев?
```

---

## Распространённые ошибки

### Ошибка 1: "Management — это faster promotion"

**Как выглядит:**
Выбираешь EM потому что "Senior уже 2 года, нужно двигаться"

**Почему это проблема:**
- Management — не promotion, это lateral move
- Если не любишь people work — будет мучением
- Staff → Principal — тоже рост (и в compensation)

**Как исправить:**
- Понять, что Senior → Staff — тоже progression
- Оценить, где ТВОИ сильные стороны

### Ошибка 2: "IC track — это остаться на месте"

**Как выглядит:**
"Я хочу расти, поэтому надо в management"

**Почему это проблема:**
- Staff/Principal — огромный scope и влияние
- TC часто выше чем у EM
- Impact через технологию — это тоже рост

**Как исправить:**
- Изучить что делают Staff/Principal
- Посмотреть compensation data
- Поговорить с people на IC track

### Ошибка 3: "Попробую management, всегда можно вернуться"

**Как выглядит:**
"Попробую год, если не понравится — вернусь"

**Почему это частично правда:**
- Да, pendulum возможен
- НО: нужно prepared объяснять "почему назад"
- И: technical skills могут "заржаветь"

**Как исправить:**
- Если пробуешь — пробуй seriously (2-3 года)
- Поддерживай technical currency
- Планируй pendulum заранее, а не как "escape"

---

## Кейсы из реальных людей

### Charity Majors: Engineer → Manager → Engineer → Manager

**Путь:**
- Senior Engineer → Engineering Manager (first time)
- Поняла, что хочет обратно → Senior Engineer
- Основала компанию (Honeycomb) → CTO/Manager again

**Урок:** "Both experiences made me better at both roles. The pendulum is not weakness — it's strength."

### Will Larson: Engineer → Staff → Manager → Writer

**Путь:**
- IC → Staff Engineer at Uber
- Engineering Manager → Director
- Написал "Staff Engineer" и "An Elegant Puzzle"

**Урок:** Глубокое понимание обоих треков позволило писать о них авторитетно.

### Gergely Orosz: Engineer → Manager → IC (Author)

**Путь:**
- IC в Skyscanner, Uber
- Engineering Manager
- Ушёл на IC work (writing, consulting)

**Урок:** "I realized I get more energy from creating content than managing people day-to-day"

---

## Checklist для принятия решения

```
ПЕРЕД ВЫБОРОМ ТРЕКА:

□ Провёл honest self-assessment (checklists выше)
□ Поговорил с 2+ Staff Engineers о их работе
□ Поговорил с 2+ Engineering Managers о их работе
□ Понял compensation на обоих треках в моей компании
□ Понял, есть ли реальный IC track (Staff/Principal)
□ Обсудил с текущим менеджером обе опции
□ Подумал о 5-year horizon, не о следующем шаге
□ Принял, что можно pendulum (это не failure)
□ Готов попробовать на 2-3 года (не 6 месяцев)
```

---

## Связанные темы

### Prerequisites
- Опыт Senior Engineer (понимание обязанностей)
- [[career/staff-plus-engineering]] — детали IC track

### Следующие шаги
- [[transition-to-management]] — если выбрал management
- [[staff-roles]] — если выбрал IC track
- [[em-fundamentals]] — основы EM

### Связи с другими разделами
- [[communication/difficult-conversations]] — нужно для обоих
- [[career/staff-plus-engineering]] — IC track details

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [The Engineer/Manager Pendulum](https://charity.wtf/2017/05/11/the-engineer-manager-pendulum/) | Article | Core framework |
| 2 | [17 Reasons Not to Be a Manager](https://charity.wtf/2019/09/08/reasons-not-to-be-a-manager/) | Article | Red flags |
| 3 | [StaffEng.com](https://staffeng.com) | Book/Site | IC track details |
| 4 | [levels.fyi](https://levels.fyi) | Data | Compensation comparison |
| 5 | [If Management Isn't a Promotion](https://charity.wtf/2020/09/06/if-management-isnt-a-promotion-then-engineering-isnt-a-demotion/) | Article | Mindset shift |
| 6 | [Engineering Career Paths](https://newsletter.pragmaticengineer.com/p/engineering-career-paths) | Newsletter | Big Tech comparison |

### Дополнительное чтение
- **The Manager's Path** (Camille Fournier) — полный путь обоих треков
- **Staff Engineer** (Will Larson) — глубокий dive в IC track
- **An Elegant Puzzle** (Will Larson) — management perspective

*Исследование проведено: 2026-01-18*

---

[[leadership-overview|← Leadership MOC]] | [[transition-to-management|Transition to Management →]]
