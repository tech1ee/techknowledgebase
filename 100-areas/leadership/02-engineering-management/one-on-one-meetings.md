---
title: "1-on-1 Meetings: Главный инструмент менеджера"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
target-role: [tech-lead, em, director]
teaches:
  - структура 1-on-1
  - вопросы для разных ситуаций
  - частые ошибки
sources: [manager-tools, rands-in-repose, lara-hogan, ben-horowitz]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[performance-management]]"
  - "[[delegation]]"
prerequisites:
  - "[[em-fundamentals]]"
---

# 1-on-1 Meetings: Главный инструмент менеджера

> **TL;DR:** 1-on-1 — это не status update и не твоё время. Это время сотрудника для обсуждения того, что важно ему. Регулярные качественные 1-on-1 — единственный масштабируемый способ строить trust, давать feedback и развивать людей. 30 минут в неделю × 5 reports = 2.5 часа инвестиции с ROI > 1000%.

---

## Зачем это нужно?

### Типичная ситуация

EM встречается с командой только на standups. Когда проблемы накапливаются — удивление: "Почему не сказал раньше?". Performance review раз в год — шок для обоих. Ценный инженер уходит без предупреждения.

**Без регулярных 1-on-1:**
- Проблемы обнаруживаются когда уже поздно
- Feedback накапливается и даётся "залпом"
- Trust не строится
- Люди чувствуют себя invisible

**С хорошими 1-on-1:**
- Ранние сигналы проблем
- Continuous feedback loop
- Глубокие рабочие отношения
- Retention и engagement растут

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| Сотрудники с регулярными 1-on-1 engaged | 3x выше | Gallup |
| Проблемы, обнаруженные на 1-on-1 vs случайно | 80% vs 20% | Manager Tools |
| Turnover при отсутствии 1-on-1 | +40% | SHRM |
| Время до trust building без 1-on-1 | 2-3x дольше | First Round |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **New EM** | Critical | Начни проводить сразу |
| **Experienced EM** | High | Проверь качество своих 1-on-1 |
| **Tech Lead** | High | Даже без formal authority |
| **Director** | High | Skip-levels + direct reports |
| **IC** | Medium | Понять, чего требовать от своего EM |

---

## Терминология

| Термин | Определение | IT-аналогия |
|--------|-------------|-------------|
| **1-on-1** | Регулярная встреча менеджера с direct report | Heartbeat — регулярный ping |
| **Skip-level** | 1-on-1 через уровень (Director → IC) | Health check на всю систему |
| **Coaching** | Помощь найти решение самому | Rubber duck debugging |
| **Mentoring** | Передача опыта и советов | Code review с объяснениями |
| **Status Update** | Чем 1-on-1 НЕ является | Standup, не 1-on-1 |

### Что 1-on-1 НЕ является

| Это НЕ 1-on-1 | Почему |
|---------------|--------|
| Status meeting | Для этого есть standup, Jira |
| Project review | Отдельная встреча |
| Только твои вопросы | Это время сотрудника |
| Решение технических проблем | Отдельная сессия |
| Performance review | Отдельный formal process |

---

## Как это работает?

### Структура эффективного 1-on-1

```
┌─────────────────────────────────────────────────────────────────┐
│                        1-ON-1 STRUCTURE                         │
│                         (30-60 min)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [5 min] OPENING                                         │   │
│  │ "Что на уме? С чего хочешь начать?"                     │   │
│  │ Их agenda first. Показать что это ИХ время.             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [15-20 min] THEIR TOPICS                                │   │
│  │ • Текущие challenges                                    │   │
│  │ • Что хотят обсудить                                    │   │
│  │ • Blockers, concerns                                    │   │
│  │ Слушать > Говорить (80/20)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [10-15 min] YOUR TOPICS (if time)                       │   │
│  │ • Feedback                                              │   │
│  │ • Context sharing                                       │   │
│  │ • Career discussion                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [5 min] CLOSE                                           │   │
│  │ • Action items                                          │   │
│  │ • "Что-нибудь ещё?"                                     │   │
│  │ • Schedule next                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Типы 1-on-1 разговоров

```
WEEKLY REGULAR (80% meetings)
─────────────────────────────────────
Focus: Текущие дела, small talk, blockers
Depth: Operational
Duration: 30 min
Tone: Casual, supportive

CAREER DEVELOPMENT (Monthly/Quarterly)
─────────────────────────────────────
Focus: Growth, goals, trajectory
Depth: Strategic
Duration: 45-60 min
Tone: Coaching, exploratory

FEEDBACK SESSION (As needed)
─────────────────────────────────────
Focus: Specific behavior/situation
Depth: Tactical
Duration: 30 min
Tone: Direct, constructive

DIFFICULT CONVERSATION (As needed)
─────────────────────────────────────
Focus: Performance issues, concerns
Depth: Deep
Duration: 45-60 min
Tone: Compassionate but clear
```

### Listening Framework

```
LEVELS OF LISTENING:

Level 1: DOWNLOADING
┌────────────────────────────────────┐
│ Ждёшь своей очереди говорить.      │
│ Думаешь о своём ответе.            │
│ ✗ Не подходит для 1-on-1           │
└────────────────────────────────────┘

Level 2: FACTUAL
┌────────────────────────────────────┐
│ Слышишь факты и информацию.        │
│ Можешь пересказать что сказали.    │
│ ⚠ Минимальный уровень              │
└────────────────────────────────────┘

Level 3: EMPATHETIC
┌────────────────────────────────────┐
│ Слышишь эмоции и concerns.         │
│ Понимаешь perspective собеседника. │
│ ✓ Целевой уровень                  │
└────────────────────────────────────┘

Level 4: GENERATIVE
┌────────────────────────────────────┐
│ Создаёте новое понимание вместе.   │
│ Инсайты возникают в разговоре.     │
│ ✓ Идеальный уровень (coaching)     │
└────────────────────────────────────┘
```

---

## 130+ вопросов для 1-on-1

### Opening Questions (начать разговор)

```
GENERAL:
• "Что на уме?"
• "С чего хочешь начать сегодня?"
• "Как неделя?"
• "Что самое важное обсудить?"

ENERGY CHECK:
• "По шкале 1-10, как энергия?"
• "Что подзарядило на этой неделе? Что опустошило?"

IF SILENCE:
• "Можем начать с любой темы — работа, карьера, или просто catch up."
• "Если бы не нужно было обсуждать работу, о чём бы поговорили?"
```

### Work & Projects

```
CURRENT WORK:
• "Что занимает большую часть времени?"
• "Что идёт хорошо в текущем проекте?"
• "Что frustrating?"
• "Где чувствуешь stuck?"

BLOCKERS:
• "Что замедляет твою работу?"
• "Какие dependencies тебя блокируют?"
• "Что могу сделать, чтобы помочь?"

PRIORITIES:
• "Понятны ли текущие приоритеты?"
• "Есть ли конфликтующие приоритеты?"
• "Чувствуешь ли что работаешь над важным?"

WORKLOAD:
• "Как нагрузка — sustainable?"
• "Есть что-то, что можно убрать с твоей тарелки?"
• "Достаточно ли challenge? Или слишком много?"
```

### Team & Collaboration

```
TEAM DYNAMICS:
• "Как атмосфера в команде?"
• "С кем легко работать? С кем сложнее?"
• "Чувствуешь ли support от команды?"

COMMUNICATION:
• "Достаточно ли информации получаешь?"
• "Есть ли что-то, что должен знать, но не знаю?"
• "Как общение с другими командами?"

MEETINGS:
• "Какие meetings полезны? Какие — нет?"
• "Достаточно ли focus time?"
```

### Career & Growth

```
DEVELOPMENT:
• "Чему хочешь научиться в ближайшие 6 месяцев?"
• "Какие навыки хочешь развить?"
• "Какой тип работы хотел бы делать больше?"

CAREER:
• "Где видишь себя через 2-3 года?"
• "Интересует ли менеджмент или глубина в IC?"
• "Какой следующий career step видишь?"

FEEDBACK ON GROWTH:
• "Чувствуешь ли что растёшь?"
• "Что помогает расти? Что мешает?"
• "Какие возможности хотел бы получить?"

ASPIRATIONS:
• "Если бы мог работать над чем угодно, что бы это было?"
• "Какой impact хочешь создать?"
```

### Feedback & Recognition

```
ASKING FOR FEEDBACK:
• "Что могу делать лучше как менеджер?"
• "Есть ли что-то, что я делаю и это мешает тебе?"
• "Как предпочитаешь получать feedback?"

GIVING RECOGNITION:
• "Хотел отметить [конкретное достижение]."
• "Заметил, как ты [behavior] — это очень помогло [impact]."

BEFORE GIVING CONSTRUCTIVE:
• "Можно поделиться наблюдением?"
• "Есть feedback, который может быть полезен."
```

### Well-being & Motivation

```
ENERGY:
• "Как баланс работы и жизни?"
• "Высыпаешься?"
• "Когда последний раз брал отпуск?"

MOTIVATION:
• "Что мотивирует тебя сейчас?"
• "Что демотивирует?"
• "Чувствуешь ли connection с миссией команды?"

STRESS:
• "Что вызывает stress на работе?"
• "Как справляешься с pressure?"
• "Есть ли что-то, что я могу убрать?"
```

### Manager Effectiveness

```
SUPPORT:
• "Получаешь ли достаточно support от меня?"
• "Что могу делать больше? Меньше?"
• "Как я могу быть более полезным?"

COMMUNICATION:
• "Достаточно ли context даю?"
• "Предпочитаешь больше или меньше check-ins?"
• "Как лучше с тобой коммуницировать?"

TRUST:
• "Комфортно ли приходить ко мне с проблемами?"
• "Есть ли что-то, что боишься обсуждать?"
```

### Skip-Level Specific

```
TEAM HEALTH:
• "Как дела в команде в целом?"
• "Есть ли что-то, о чём твой менеджер может не знать?"
• "Что работает хорошо под руководством [name]?"

ORGANIZATIONAL:
• "Понятна ли стратегия компании?"
• "Есть ли процессы, которые мешают?"
• "Что бы изменил в организации?"
```

### Closing Questions

```
• "Что-нибудь ещё?"
• "Есть ли что-то, что забыли обсудить?"
• "Как я могу помочь на этой неделе?"
• "Когда следующий 1-on-1 удобен?"
```

---

## Templates и Скрипты

### 1-on-1 Note Template

```markdown
## 1-on-1: [Name] — [Date]

### Their Topics
- [ ] [Topic 1]
- [ ] [Topic 2]

### My Topics
- [ ] [Topic 1]
- [ ] [Feedback if any]

### Discussion Notes
[Free-form notes]

### Action Items
- [ ] [Person]: [Action] — due [date]
- [ ] [Person]: [Action] — due [date]

### Follow-up for Next Time
- [ ] [Topic to revisit]

### Career Notes (periodic)
- Goals discussed:
- Growth areas:
- Opportunities to provide:
```

### Agenda Template (shared doc)

```markdown
# 1-on-1: [Manager] <> [Report]
Updated: [Date]

## Standing Items
- Energy check (1-10)
- Priorities clear?
- Any blockers?

## [Report]'s Topics
_Add topics here before the meeting_
1.
2.

## [Manager]'s Topics
_Manager adds topics here_
1.
2.

## Notes & Actions
_Captured during meeting_

### [Date]
- Notes:
- Actions:

### [Previous Date]
- Notes:
- Actions:
```

### First 1-on-1 Script (Lara Hogan)

```
"Я хочу узнать несколько вещей, чтобы быть
лучшим менеджером для тебя.

1. Grumpiness: Что тебя делает grumpy?
   Что я могу заметить, чтобы понять что
   что-то не так?

2. Feedback: Как предпочитаешь получать feedback?
   - В момент или позже?
   - Письменно или устно?
   - Private или public recognition?

3. Needs: Что тебе нужно от менеджера?
   - Больше direction или autonomy?
   - Больше context или меньше details?

4. Growth: Над чем хочешь расти?
   Чему научиться в следующие 6 месяцев?

5. Anything else: Есть что-то, что должен знать?"
```

### Difficult Conversation Opener

```
"Хочу обсудить кое-что важное.
[Pause — дать подготовиться]

Я заметил [specific observation].
Это влияет на [impact].
Хочу понять твою perspective."

[Слушать. Не защищаться. Не перебивать.]

"Спасибо что поделился. Я слышу [summary].
Давай обсудим, как двигаться вперёд."
```

---

## Распространённые ошибки

### Ошибка 1: Status Update Meeting

**Как выглядит:**
"Что делал вчера? Что будешь делать сегодня? Есть blockers?"

**Почему это проблема:**
- Для этого есть standup
- Нет глубины
- Теряется trust-building opportunity

**Как исправить:**
```
ВМЕСТО: "Расскажи чем занимаешься"
ДЕЛАЙ:  "Что на уме? Что хочешь обсудить?"

Если они начинают со status:
"Это полезно знать. А есть что-то помимо status,
что хочешь обсудить? Challenges, concerns?"
```

### Ошибка 2: Только когда есть проблемы

**Как выглядит:**
Отменяешь 1-on-1 когда "всё хорошо". Проводишь только при кризисе.

**Почему это проблема:**
- 1-on-1 ассоциируется с негативом
- Trust не строится
- Упускаешь early signals

**Как исправить:**
```
ПРАВИЛО: Никогда не отменяй 1-on-1

Если совсем занят — перенеси, не отменяй.
Короткий 1-on-1 лучше чем никакого.
Регулярность важнее длительности.
```

### Ошибка 3: Монолог менеджера

**Как выглядит:**
EM говорит 80% времени. Даёт советы. Решает проблемы за человека.

**Почему это проблема:**
- Их время, не твоё
- Не развивает ownership
- Упускаешь важную информацию

**Как исправить:**
```
ПРАВИЛО 80/20: Они говорят 80%, ты — 20%

Техники:
• Задавай вопросы вместо советов
• "Что думаешь?" вместо "Вот что нужно"
• Пауза после их ответа (они добавят больше)
• Count to 5 before responding
```

### Ошибка 4: Нет записей

**Как выглядит:**
После 1-on-1 — ничего не записано. Через месяц не помнишь, о чём говорили.

**Почему это проблема:**
- Action items теряются
- Patterns не замечаются
- Performance review — стресс

**Как исправить:**
```
ПОСЛЕ КАЖДОГО 1-on-1:
□ 2-3 ключевых point
□ Action items с owners
□ Темы для follow-up
□ Mood/energy observation

Занимает: 2-3 минуты
ROI: Огромный при performance reviews
```

### Ошибка 5: Отмены "потому что busy"

**Как выглядит:**
"Давай перенесём, у меня срочный meeting". Повторяется каждую неделю.

**Почему это проблема:**
- Сигнал: "Ты не приоритет"
- Trust разрушается
- Проблемы копятся

**Как исправить:**
```
1-ON-1 = СВЯЩЕННЫЙ СЛОТ

Единственные причины отмены:
• PTO (отпуск)
• Actual emergency
• Они попросили

Для всего остального:
"Давай сократим до 15 минут"
лучше чем отмена.
```

---

## Когда применять разные форматы

### Weekly 30 min (стандарт)

**Когда:**
- Команда стабильна
- Отношения established
- Нет major changes

### Weekly 45-60 min

**Когда:**
- Новый report (первые 2-3 месяца)
- Career development discussions
- После significant events

### Bi-weekly (каждые 2 недели)

**Когда:**
- Senior, autonomous people
- Длительные рабочие отношения
- Они явно предпочитают
- ⚠️ Риск: можешь пропустить early signals

### Skip-levels

**Когда:**
- Ты Director+ с managers под тобой
- Frequency: monthly или quarterly
- Focus: team health, manager effectiveness, career

---

## Кейсы

### Ben Horowitz: Why 1-on-1s Matter

**Контекст:** Ben Horowitz — co-founder a16z, автор "The Hard Thing About Hard Things".

**Observation:**
```
"The key to a good 1-on-1 is understanding
that it's the employee's meeting, not yours."
```

**Framework:**
1-on-1 — единственное место где junior может обсудить что угодно без audience.

**Результат:** Компании с культурой 1-on-1 faster at identifying problems.

### Google: Manager Feedback

**Контекст:** Google's Upward Feedback Survey включает вопросы о 1-on-1.

**Что меряют:**
```
"My manager conducts effective 1-on-1s."
"I can discuss sensitive topics with my manager."
"My manager provides actionable feedback."
```

**Найдено:** Корреляция между этими metrics и team performance очень высокая.

### Netflix: No Formal 1-on-1 Policy

**Контекст:** Netflix не требует formal 1-on-1 schedule.

**Подход:**
- Trust adults to figure out communication
- Some do weekly, some ad-hoc
- Emphasis на "radical candor" в любом формате

**Урок:** Формат может быть flexible, но intentional communication critical.

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    1-ON-1 CHEAT SHEET                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  DO:                          DON'T:                       │
│  ✓ Их время, их agenda        ✗ Status updates            │
│  ✓ Listen 80%                  ✗ Монолог                   │
│  ✓ Take notes                  ✗ Отменять                  │
│  ✓ Follow up on action items   ✗ Skip difficult topics    │
│  ✓ Ask open questions          ✗ Дать совет сразу         │
│                                                            │
│  STRUCTURE:                                                │
│  [5 min] "Что на уме?"                                     │
│  [20 min] Their topics                                     │
│  [10 min] Your topics / feedback                           │
│  [5 min] Actions + close                                   │
│                                                            │
│  IF STUCK:                                                 │
│  "Как энергия по шкале 1-10?"                              │
│  "Что было highlight этой недели?"                         │
│  "Что могу сделать, чтобы помочь?"                         │
│                                                            │
│  AFTER:                                                    │
│  □ Key points documented                                   │
│  □ Action items with owners                                │
│  □ Next meeting scheduled                                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Связанные темы

### Prerequisites
- [[em-fundamentals]] — роль EM
- [[transition-to-management]] — если новый EM

### Следующие шаги
- [[performance-management]] — feedback и review
- [[delegation]] — empowering через 1-on-1
- [[communication/active-listening]] — навыки слушания
- [[communication/giving-feedback]] — feedback frameworks

### Связи с другими разделами
- [[communication/difficult-conversations]] — hard talks
- [[career/growth/]] — career development discussions

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Manager Tools: 1-on-1 Basics](https://www.manager-tools.com/2005/07/the-single-most-effective-management-tool-part-1) | Podcast | Core framework |
| 2 | [Lara Hogan: First 1-on-1 Questions](https://larahogan.me/blog/first-one-on-one-questions/) | Article | Question bank |
| 3 | [Rands: 1-on-1](https://randsinrepose.com/archives/the-update-the-vent-and-the-disaster/) | Article | Update/Vent/Disaster |
| 4 | [Ben Horowitz: 1-on-1s](https://a16z.com/2012/08/30/one-on-one/) | Article | Philosophy |
| 5 | [Gallup Q12](https://www.gallup.com/workplace/356063/gallup-q12-employee-engagement-survey.aspx) | Research | Engagement correlation |
| 6 | [Google re:Work](https://rework.withgoogle.com/guides/managers-coach-managers-to-coach/steps/hold-effective-1-1-meetings/) | Guide | Best practices |

### Дополнительное чтение

- "The Making of a Manager" by Julie Zhuo — 1-on-1 chapter
- "Radical Candor" by Kim Scott — direct but caring conversations
- "Resilient Management" by Lara Hogan — practical scripts

---

## Связь с другими темами

**[[em-fundamentals]]** — 1-on-1 встречи — это практическая реализация фундаментальных принципов EM. Servant leadership, multiplier effect и psychological safety — все эти концепции воплощаются именно через регулярные качественные 1-on-1. Без понимания фундамента EM 1-on-1 рискуют превратиться в бессодержательные status updates вместо мощного инструмента развития людей.

**[[performance-management]]** — 1-on-1 и performance management тесно переплетены: именно на 1-on-1 даётся continuous feedback, обсуждаются цели, отслеживается прогресс и проводятся career conversations. Если performance review становится сюрпризом для сотрудника, значит 1-on-1 проводились неправильно. Качественные еженедельные 1-on-1 делают формальные review предсказуемыми и нестрессовыми.

**[[delegation]]** — Делегирование и 1-on-1 — взаимодополняющие инструменты. На 1-on-1 происходит handoff делегированных задач, check-in на прогресс и coaching при затруднениях. Через 1-on-1 менеджер балансирует между micromanagement и abdication, находя правильный уровень involvement для каждого человека и каждой задачи.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Содержит практические рекомендации по проведению 1-on-1 на каждом уровне менеджмента, включая конкретные вопросы, структуры и anti-patterns. Особенно ценна глава о том, как 1-on-1 меняется при переходе от EM к Director.
- **Kim et al., "The Phoenix Project" (2016)** — Хотя книга фокусируется на DevOps transformation, она ярко иллюстрирует, как отсутствие коммуникации и feedback loops приводит к организационному хаосу. 1-on-1 — это тот самый feedback loop на уровне людей, который предотвращает накопление скрытых проблем.
- **Peter Drucker, "The Effective Executive" (2006)** — Концепция Drucker о "contribution focus" помогает менеджерам превратить 1-on-1 из reactive status meetings в proactive development conversations, где фокус на вкладе каждого человека в общий результат.

---

*Последнее обновление: 2026-01-18*
*Связано с: [[leadership-overview]]*
