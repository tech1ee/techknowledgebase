---
title: "Technical Presentations для IT-специалистов"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
teaches:
  - Minto Pyramid
  - Tech talk structure
  - Demo techniques
  - Q&A handling
tags:
  - topic/communication
  - type/deep-dive
  - level/intermediate
related:
  - "[[communication-models]]"
  - "[[presentation-design]]"
  - "[[storytelling-tech]]"
---

# Technical Presentations для IT-специалистов

> **TL;DR:** Главное первым (Minto Pyramid), три supporting points, demo > slides. Tech talks — career multiplier: visibility, влияние, networking. Структура: Hook → Problem → Solution → Demo → Call to Action.

---

## Зачем это нужно?

### Представьте ситуацию

**Architecture review.** Нужно презентовать новый подход команде и stakeholders.

**Без навыка:**
```
[Слайд 1-15: Background, история проекта, все детали реализации]
[Слайд 16: "В итоге предлагаем microservices"]

Stakeholder: "Подождите, я потерялся на слайде 5.
              Так что вы предлагаете и почему?"

Developer: "Ну... это я объяснял в начале..."

Результат: 45 минут потеряно. Решение не принято. Повторная встреча.
```

**С навыком:**
```
[BLUF]: "Предлагаем перейти на микросервисы. Это сократит
         time-to-market на 40% и позволит scaling команд."

[3 supporting points]:
1. Текущая проблема: monolith блокирует независимый deploy
2. Решение: bounded contexts → independent services
3. Plan: 6-месячная миграция, начинаем с [модуль]

[Demo]: "Вот POC — один сервис уже выделен. Можно деплоить за 5 минут."

[Q&A]: Прицельные вопросы, структурированные ответы.

Результат: 30 минут. Решение одобрено. Следующие шаги понятны.
```

### Проблема в числах

```
┌──────────────────────────────────────────────────────────────────┐
│              ПРЕЗЕНТАЦИИ: СТАТИСТИКА                            │
├──────────────────────────────────────────────────────────────────┤
│  10 сек        Время чтобы захватить внимание аудитории         │
│                (потом attention падает)                         │
├──────────────────────────────────────────────────────────────────┤
│  60-80%        Senior+ времени = communication                  │
│                (презентации — ключевая часть)                    │
├──────────────────────────────────────────────────────────────────┤
│  3x            Во столько раз люди лучше запоминают             │
│  больше        stories vs факты                                  │
├──────────────────────────────────────────────────────────────────┤
│  Rule of 3    После 3 supporting points credibility             │
│                начинает падать (research)                        │
├──────────────────────────────────────────────────────────────────┤
│  55%          Коммуникации — невербальная                       │
│                (body language, tone)                             │
└──────────────────────────────────────────────────────────────────┘
```

**Вывод:** Visibility через презентации = career growth. Tech talks демонстрируют expertise и leadership potential.

---

## Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | Полезен | Demo для команды, lightning talks |
| **Middle** | Важен | Tech talks внутри компании, architecture reviews |
| **Senior** | Критичен | Conference talks, влияние на решения |
| **Tech Lead** | Обязателен | Постоянные presentations stakeholders'ам |

---

## Терминология

| Термин | Что это (простыми словами) | IT-аналогия |
|--------|---------------------------|-------------|
| **Minto Pyramid** | Структура: главное первым, потом supporting | return first, then explain |
| **SCQA** | Situation-Complication-Question-Answer | Bug report structure |
| **Hook** | Захват внимания в первые 10 секунд | Click-bait, но полезный |
| **Call to Action** | Что аудитория должна СДЕЛАТЬ после | Function return value |
| **Demo** | Показать вживую, а не рассказать | Show, don't tell |
| **Q&A** | Вопросы и ответы после презентации | Code review comments |
| **Lightning Talk** | Короткий доклад 5-10 минут | Sprint demo |

---

## Как это работает?

### Minto Pyramid Principle

Разработан Barbara Minto в McKinsey. Суть: **главное первым, детали потом**.

```
┌──────────────────────────────────────────────────────────────────┐
│                    MINTO PYRAMID                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│             ТРАДИЦИОННЫЙ           MINTO PYRAMID                │
│             ПОДХОД                                              │
│                                                                  │
│             ┌─────┐               ┌─────────────┐               │
│         ┌───┤Detail├───┐          │ MAIN POINT  │               │
│         │   └─────┘   │          │ (Answer)    │               │
│        ...  ...  ... ...         └──────┬──────┘               │
│          │   │   │   │                  │                       │
│         ┌┴───┴───┴───┴┐          ┌──────┴──────┐               │
│         │  Analysis   │          │  SUPPORTING │               │
│         └──────┬──────┘          │  POINTS     │               │
│                │                 │  (3 max)    │               │
│         ┌──────┴──────┐          └──────┬──────┘               │
│         │ CONCLUSION  │                 │                       │
│         │ (buried!)   │          ┌──────┴──────┐               │
│         └─────────────┘          │  DETAILS    │               │
│                                  │  & EVIDENCE │               │
│                                  └─────────────┘               │
│                                                                  │
│    "Думаем снизу вверх,                                         │
│     но ПРЕЗЕНТУЕМ сверху вниз"                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### SCQA Framework

Структура для engaging storytelling:

```
┌──────────────────────────────────────────────────────────────────┐
│                       SCQA FRAMEWORK                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   S - SITUATION                                                 │
│   "Наше приложение обслуживает 100K DAU на monolith."          │
│                                                                  │
│   C - COMPLICATION                                              │
│   "При росте до 500K DAU response time деградирует на 300%."   │
│                                                                  │
│   Q - QUESTION (implicit)                                       │
│   "Как масштабировать систему?"                                 │
│                                                                  │
│   A - ANSWER                                                    │
│   "Переход на микросервисы решит проблему. Вот план."          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Rule of Three

После 3 supporting points credibility падает. Причина: когнитивная нагрузка.

```
ЭФФЕКТ КОЛИЧЕСТВА АРГУМЕНТОВ:

1 argument:  "Недостаточно обосновано"     ──► Weak
2 arguments: "Хорошо, но..."               ──► Better
3 arguments: "Убедительно"                 ──► Optimal
4 arguments: "Hmm, overcompensating?"      ──► Declining trust
5+ arguments: "Что-то не так с основной    ──► Backfires
               идеей если столько обоснований"
```

---

## Типы Technical Presentations

### 1. Architecture Review / Design Review

**Цель:** Получить approval на техническое решение.

```
СТРУКТУРА:

1. CONTEXT (2 мин)
   └── Какая проблема решается?

2. PROPOSAL (5 мин)
   └── Что предлагаем? (высокоуровнево)
   └── Diagram обязательна

3. ALTERNATIVES CONSIDERED (3 мин)
   └── Почему не X, не Y?
   └── Показывает что думали over options

4. RISKS & MITIGATIONS (3 мин)
   └── Какие риски? Как митигируем?

5. PLAN (2 мин)
   └── Timeline, milestones

6. ASK (1 мин)
   └── Что конкретно нужно от аудитории?

7. Q&A (10-15 мин)
```

### 2. Tech Talk / Knowledge Sharing

**Цель:** Обучить команду, повысить visibility.

```
СТРУКТУРА:

1. HOOK (1 мин)
   └── Почему это важно? Какую проблему решает?

2. PROBLEM STATEMENT (3 мин)
   └── Конкретная боль которую испытывали

3. SOLUTION / CONCEPT (10-15 мин)
   └── Теория + практика
   └── Live coding / demo предпочтительнее slides

4. REAL EXAMPLE (5 мин)
   └── Как применили в нашем проекте
   └── Before/after metrics

5. TAKEAWAYS (2 мин)
   └── 3 главные мысли для запоминания

6. RESOURCES (1 мин)
   └── Где узнать больше

7. Q&A
```

### 3. Sprint Demo / Product Demo

**Цель:** Показать progress stakeholders'ам.

```
СТРУКТУРА:

1. WHAT WE COMMITTED (1 мин)
   └── Что обещали сделать

2. WHAT WE DELIVERED (bulk of time)
   └── SHOW, don't tell
   └── Реальные user flows
   └── Happy path + edge cases

3. WHAT WE LEARNED (2 мин)
   └── Surprises, blockers, discoveries

4. WHAT'S NEXT (1 мин)
   └── Preview следующего sprint

5. FEEDBACK (open discussion)
```

### 4. Lightning Talk (5-10 min)

**Цель:** Быстро донести одну идею.

```
СТРУКТУРА:

1. HOOK (30 сек)
   └── Provocative statement / question

2. PROBLEM (1 мин)
   └── Одна конкретная боль

3. SOLUTION (3-5 мин)
   └── Одна идея, глубоко

4. DEMO (1-2 мин)
   └── Если возможно — показать

5. CALL TO ACTION (30 сек)
   └── Попробуйте X / Прочитайте Y
```

---

## Пошаговый процесс

### Подготовка (до презентации)

```
1. ОПРЕДЕЛИ ЦЕЛЬ
   □ Что аудитория должна СДЕЛАТЬ после презентации?
   □ Approve? Learn? Change behavior?

2. ЗНАЙ АУДИТОРИЮ
   □ Технический уровень?
   □ Что уже знают о теме?
   □ Какие у них concerns?

3. СТРУКТУРИРУЙ ПО MINTO
   □ Main point первым
   □ 3 supporting points
   □ Evidence для каждого point

4. СОЗДАЙ SLIDES (если нужны)
   □ 1 idea per slide
   □ Минимум текста
   □ Диаграммы > bullets

5. ПОДГОТОВЬ DEMO
   □ Протестируй заранее
   □ Backup plan если demo fails
   □ "Сырые" demos лучше чем recorded

6. АНТИЦИПИРУЙ ВОПРОСЫ
   □ Какие вопросы зададут?
   □ Подготовь ответы
   □ Hidden slides для deep-dive questions
```

### Delivery (во время презентации)

```
1. OPENING (первые 30 секунд критичны)
   □ Memorize first sentence
   □ Начни с hook, не с "Меня зовут..."

2. BODY
   □ Следуй структуре
   □ Eye contact с разными людьми
   □ Pause после важных points

3. DEMO
   □ Рассказывай что делаешь
   □ Масштаб достаточный для видимости
   □ Если что-то пошло не так — acknowledge, move on

4. CLOSING
   □ Вернись к main point
   □ Clear call to action
   □ "Вопросы?"

5. Q&A
   □ Повтори вопрос (для всех и для себя)
   □ Отвечай кратко
   □ "Хороший вопрос" — не нужно каждый раз
   □ "Не знаю, вернусь с ответом" — ok
```

### Post-презентация

```
1. FOLLOW-UP
   □ Отправь slides/recording
   □ Ответь на вопросы которые обещал

2. FEEDBACK
   □ Попроси feedback у trusted colleagues
   □ Что сработало? Что улучшить?

3. ITERATE
   □ Записывай learnings
   □ Улучшай для следующего раза
```

---

## Скрипты и Templates

### Use Case 1: Architecture Review Opening

**Ситуация:** Начало architecture review

**Скрипт:**
```
"Сегодня прошу одобрить переход на [архитектура X].

Проблема: [конкретная боль — 1 предложение].
Решение: [высокоуровневое — 1 предложение].
Ожидаемый результат: [метрика — 1 предложение].

Далее покажу:
1. Почему текущий подход не работает
2. Как предложенное решение это исправляет
3. План миграции

В конце нужен ваш approval на начало работы."
```

### Use Case 2: Tech Talk Hook

**Ситуация:** Начало tech talk о новой технологии

**Варианты hooks:**

```
1. СТАТИСТИКА:
"Мы тратим 40% времени на debugging. Сегодня покажу
как сократить это до 15%."

2. ПРОБЛЕМА:
"Поднимите руку если ваш deploy занимает больше часа.
[пауза] Расскажу как мы сократили до 5 минут."

3. ИСТОРИЯ:
"В прошлую пятницу мы выкатили баг в production.
То что произошло потом изменило наш подход навсегда."

4. ВОПРОС:
"Кто может объяснить разницу между concurrency и parallelism?
[пауза] Сегодня разберёмся раз и навсегда."
```

### Use Case 3: Demo Script

**Ситуация:** Демонстрация нового feature

**Скрипт:**
```
"Сейчас покажу [feature] в action.

[Делаешь действие 1]
'Вот здесь пользователь нажимает [X]...'

[Результат]
'Обратите внимание на [важная деталь]...'

[Edge case]
'А что если пользователь попробует [нестандартное]?
Смотрите — система корректно обрабатывает.'

[Финиш]
'Это то, что раньше занимало 5 минут,
теперь — 30 секунд.'
"
```

### Use Case 4: Q&A Handling

**Ситуация:** Сложные вопросы после презентации

**Скрипты:**

```
ПОНЯЛ ВОПРОС:
"Вопрос про [paraphrase]. Да, [краткий ответ].
Хотите детальнее?"

НЕ ПОНЯЛ ВОПРОС:
"Хочу убедиться что правильно понял. Вы спрашиваете о [версия]?"

НЕ ЗНАЮ ОТВЕТ:
"Хороший вопрос. Не хочу давать неточный ответ —
вернусь к вам с ответом до [время]."

ВОПРОС OFF-TOPIC:
"Это важный вопрос, но выходит за scope сегодняшней темы.
Давай обсудим отдельно после / запланируем follow-up."

HOSTILE QUESTION:
"Понимаю concern. Мы рассматривали [альтернатива],
но выбрали [решение] потому что [факты].
Какие конкретные concerns остаются?"
```

### Template: Presentation Outline

```markdown
# [Название презентации]

## Meta
- Audience: [кто]
- Goal: [что должны СДЕЛАТЬ после]
- Time: [сколько минут]

## Outline

### Opening (1 min)
- Hook: [захват внимания]
- Main point: [главная мысль]
- Agenda preview: "Расскажу о..."

### Point 1 (X min)
- Claim: [утверждение]
- Evidence: [данные/пример]
- Transition: "Теперь о..."

### Point 2 (X min)
[аналогично]

### Point 3 (X min)
[аналогично]

### Demo (X min)
- Setup: [что показываю]
- Flow: [последовательность]
- Wow moment: [что впечатлит]

### Closing (1 min)
- Summary: [3 takeaways]
- Call to action: [что делать дальше]
- Questions: "Вопросы?"

## Backup
- Hidden slides для deep-dive
- Answers to anticipated questions
```

---

## Slides Best Practices

### Design Principles

```
┌──────────────────────────────────────────────────────────────────┐
│                 SLIDE DESIGN RULES                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. ONE IDEA PER SLIDE                                         │
│      ✗ Список из 10 пунктов                                     │
│      ✓ Один пункт, развёрнутый                                  │
│                                                                  │
│   2. МИНИМУМ ТЕКСТА                                             │
│      ✗ Полные предложения                                       │
│      ✓ Keywords + говоришь остальное                            │
│                                                                  │
│   3. КРУПНЫЙ ШРИФТ                                              │
│      ✗ 12pt (нечитаемо с 5 метров)                             │
│      ✓ 24pt+ для body, 36pt+ для titles                        │
│                                                                  │
│   4. CONTRAST                                                   │
│      ✗ Серый на сером                                           │
│      ✓ Тёмный на светлом или наоборот                          │
│                                                                  │
│   5. ВИЗУАЛИЗАЦИЯ                                               │
│      ✗ Описание архитектуры текстом                            │
│      ✓ Диаграмма архитектуры                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Slide Structure

```
ТИПЫ SLIDES:

1. TITLE SLIDE
   ├── Название
   ├── Твоё имя, команда
   └── Дата (опционально)

2. AGENDA SLIDE
   ├── 3-5 пунктов
   └── Показывает structure

3. CONTENT SLIDE
   ├── Headline = claim
   ├── Body = evidence
   └── Minimal text

4. DIAGRAM SLIDE
   ├── Visual занимает 80%+
   └── Minimal annotations

5. CODE SLIDE
   ├── Syntax highlighting
   ├── Только relevant code
   └── Highlight важные строки

6. SUMMARY SLIDE
   ├── 3 takeaways
   └── Call to action
```

---

## Demo Best Practices

### Preparation

```
DEMO CHECKLIST:

□ Протестирован на том же оборудовании что будет на презентации
□ Backup video recording если live demo fails
□ Environment clean (no notifications, clean desktop)
□ Font size увеличен для visibility
□ Data prepared (realistic, not "test test test")
□ Happy path + 1-2 edge cases готовы
```

### Execution

```
DURING DEMO:

DO:
├── Narrate что делаешь
├── Pause на важных моментах
├── Point cursor к важным элементам
├── Acknowledge errors gracefully
└── Have recovery plan

DON'T:
├── Молча кликать
├── Показывать слишком много деталей
├── Паниковать если что-то не работает
├── Говорить "это обычно работает..."
└── Показывать real user data
```

### Failure Recovery

```
IF DEMO FAILS:

1. ACKNOWLEDGE:
   "Окей, это не то что ожидал. Секунду."

2. TRY QUICK FIX (max 30 сек):
   "Попробую [действие]..."

3. SWITCH TO BACKUP:
   "Покажу на recorded version..."
   или
   "Давайте я объясню на diagram что должно произойти..."

4. MOVE ON:
   "Вернусь к демо позже, а пока..."
```

---

## Q&A Handling

### Types of Questions

```
┌──────────────────────────────────────────────────────────────────┐
│                    TYPES OF QUESTIONS                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CLARIFICATION                                                 │
│   "Можешь уточнить как..."                                      │
│   → Ответ: объясни другими словами                              │
│                                                                  │
│   CHALLENGE                                                      │
│   "А почему не [альтернатива]?"                                 │
│   → Ответ: acknowledge, дай reasoning                           │
│                                                                  │
│   EXPANSION                                                      │
│   "А что насчёт [related topic]?"                               │
│   → Ответ: краткий ответ или "off-scope, обсудим отдельно"     │
│                                                                  │
│   HOSTILE                                                        │
│   "Это никогда не сработает потому что..."                      │
│   → Ответ: stay calm, address specific concern, don't defend   │
│                                                                  │
│   SHOW-OFF                                                       │
│   "Я знаю про [tangent]..."                                     │
│   → Ответ: краткий acknowledge, redirect to topic               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Techniques

```
1. REPEAT/PARAPHRASE
   "Если я правильно понял, вопрос о [X]..."
   → Даёт время подумать
   → Убеждается что понял
   → Даёт context аудитории

2. BRIDGE
   "Хороший вопрос. Это связано с [topic from presentation]..."
   → Connects back to your content

3. DEFER
   "Важный вопрос. Давай обсудим после / follow up email."
   → Для off-topic или complex questions

4. REDIRECT TO ROOM
   "Интересный point. Кто-то в команде сталкивался с этим?"
   → Для open discussions
```

---

## Распространённые ошибки

### Ошибка 1: Buried Lead

**Неправильно:**
15 слайдов background, потом "Итак, наше предложение..."

**Почему это неправильно:**
Внимание падает после 10 минут. Главное должно быть в первые 2 минуты.

**Правильно:**
"Предлагаем [решение]. Сейчас объясню почему." (Minto Pyramid)

### Ошибка 2: Reading Slides

**Неправильно:**
Повернуться к экрану и читать текст со слайдов.

**Почему это неправильно:**
Аудитория может читать сама. Твоя задача — добавить value.

**Правильно:**
Slides как visual aid. Смотри на аудиторию, рассказывай своими словами.

### Ошибка 3: Too Much Detail

**Неправильно:**
Показать каждую строчку кода, каждый config file.

**Почему это неправильно:**
Cognitive overload. Аудитория теряет big picture.

**Правильно:**
Highlight только essential parts. Детали — в appendix или follow-up.

### Ошибка 4: No Practice

**Неправильно:**
"Я знаю material, просто буду говорить."

**Почему это неправильно:**
Timing off, transitions awkward, забываешь important points.

**Правильно:**
Минимум 2-3 прогона вслух. Перед важной презентацией — перед коллегой.

### Ошибка 5: Defensive Q&A

**Неправильно:**
"Нет, вы не понимаете, я же объяснял..."

**Почему это неправильно:**
Alienates audience, looks unprofessional.

**Правильно:**
"Понимаю concern. Давай разберём [конкретный аспект]."

---

## Практика

### Упражнение 1: Minto Restructure

**Задача:** Restructure этот outline по Minto Pyramid:

```
Original:
1. Background of the project
2. Current architecture details
3. Problems we encountered
4. Solutions we tried
5. What worked and what didn't
6. Our recommendation
7. Next steps
```

**Эталонный ответ:**
<details><summary>Показать</summary>

```
Minto structure:
1. Our recommendation (MAIN POINT FIRST)
2. Problem summary (why change needed)
3. Why this solution (vs alternatives)
4. Evidence it works (data, POC)
5. Implementation plan (next steps)
6. Appendix: detailed background, failed attempts
```

</details>

### Упражнение 2: Create a Hook

**Задача:** Напиши 3 варианта hook для презентации "Как мы ускорили CI/CD pipeline с 45 минут до 8 минут"

**Эталонный ответ:**
<details><summary>Показать</summary>

```
1. СТАТИСТИКА:
"Вчера наш pipeline сломался 3 раза. Каждый раз мы ждали
45 минут чтобы узнать результат. Сегодня расскажу как мы
это исправили — теперь ждём 8 минут."

2. ВОПРОС:
"Кто сегодня ждал больше 30 минут пока pipeline завершится?
[руки] А если бы это было 8 минут? Вот что мы сделали."

3. ИСТОРИЯ:
"В пятницу вечером наш release блокировался из-за flaky test.
Pipeline перезапускали 4 раза — каждый по 45 минут.
Этот инцидент заставил нас переосмыслить всё."
```

</details>

### Упражнение 3: Q&A Practice

**Задача:** Как ответить на вопрос "Почему вы не использовали [известный конкурент вашего решения]?"

**Эталонный ответ:**
<details><summary>Показать</summary>

```
"Хороший вопрос. Мы рассматривали [конкурент].

Он хорош для [use case X], но для нашей ситуации
[наше решение] лучше подходит потому что:

1. [Конкретная причина с фактами]
2. [Вторая причина если есть]

Если появится context где [конкурент] будет лучше —
обязательно рассмотрим. Но для текущей задачи
наш выбор оптимален."
```

Key points:
- Acknowledge alternative
- Don't dismiss it
- Give specific reasons
- Stay open
</details>

### Ежедневная практика

| День | Упражнение | Контекст |
|------|------------|----------|
| 1 | Запиши себя на video | 2-минутное объяснение чего-то технического |
| 2 | Посмотри tech talk | Разбери structure и hooks |
| 3 | Lightning talk | 5 минут на standup о том что изучил |
| 4 | Practice Q&A | Попроси коллегу задать сложные вопросы |
| 5 | Demo practice | Покажи feature вслух, как будто аудитория |

---

## Связанные темы

### Prerequisites (изучить ДО)
- [[communication-models]] — понимание как работает коммуникация

### Эта тема открывает (изучить ПОСЛЕ)
- [[presentation-design]] — продвинутый дизайн слайдов
- [[storytelling-tech]] — storytelling для технических тем

### Связанные навыки
- [[active-listening]] — для Q&A handling
- [[giving-feedback]] — для architecture reviews

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Minto Pyramid - PowerUser](https://www.powerusersoftwares.com/post/give-a-brilliant-structure-to-your-presentations-with-the-pyramid-principle) | Article | Pyramid structure |
| 2 | [SCQA Framework - ModelThinkers](https://modelthinkers.com/mental-model/minto-pyramid-scqa) | Article | SCQA details |
| 3 | [Tech Presentation Tips - Snappify](https://snappify.com/blog/technical-presentation-tips) | Article | Practical tips |
| 4 | [Conference Speaking - Draft.dev](https://draft.dev/learn/the-fundamentals-of-speaking-at-technology-conferences) | Article | Conference tips |
| 5 | [Rule of Three - SlideModel](https://slidemodel.com/presenting-using-the-pyramid-principle/) | Article | Supporting points |
| 6 | [TechYaks](https://techyaks.com/) | Resource | Best tech talks collection |
| 7 | [Architecture Review - Arch2O](https://www.arch2o.com/tips-architecture-project-presentation/) | Article | Presentation techniques |
| 8 | [Pyramid Principle - BetterUp](https://www.betterup.com/blog/minto-pyramid) | Article | Framework explanation |

*Исследование проведено: 2026-01-18*

---

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
