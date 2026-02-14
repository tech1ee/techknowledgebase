---
title: "Feedback Frameworks: SBI vs COIN vs DESC vs STAR vs CEDAR"
created: 2026-01-18
modified: 2026-01-18
type: comparison
status: published
difficulty: intermediate
teaches:
  - sbi-model
  - coin-model
  - desc-model
  - star-feedback
  - cedar-model
  - framework-selection
tags:
  - topic/communication
  - type/comparison
  - level/intermediate
related:
  - "[[giving-feedback]]"
  - "[[performance-conversations]]"
prerequisites:
  - "[[giving-feedback]]"
reading_time: 14
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Feedback Frameworks: какую модель выбрать и когда

> **TL;DR:** Нет "лучшего" feedback framework — есть подходящий для ситуации. SBI — для быстрой коррекции, COIN — для developmental conversations, DESC — для assertive requests, STAR — для structured reviews, CEDAR — для collaborative dialog. Ключевая идея: выбирай framework по цели, не по привычке.

---

## Зачем это нужно?

### Представьте ситуацию

Ты менеджер. В команде проблема: разработчик регулярно сдаёт задачи поздно. Ты используешь SBI: "Вчера ты сдал задачу на день позже дедлайна, это задержало релиз." Разработчик соглашается, но через неделю — та же история. Почему? SBI диагностирует проблему, но не создаёт action plan. Нужен был COIN с "Next Steps".

**Без понимания разных frameworks:**
- Используешь один подход для всех ситуаций
- Feedback диагностирует, но не решает
- Пропускаешь возможности для development
- Frustration от повторяющихся проблем

**С пониманием:**
- Выбираешь инструмент под задачу
- SBI для быстрой коррекции
- COIN для поведенческих изменений
- DESC для assertive boundaries
- Результат: реальные изменения

### Сравнение frameworks: обзор

```
┌─────────────────────────────────────────────────────────────────┐
│                    5 FEEDBACK FRAMEWORKS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SBI         Situation-Behavior-Impact                          │
│  ────        Quick, observation-based, diagnostic               │
│              Best for: Code review, quick corrections           │
│                                                                 │
│  COIN        Context-Observation-Impact-Next Steps              │
│  ────        Developmental, forward-looking, action-oriented    │
│              Best for: Behavioral change, 1-on-1 development    │
│                                                                 │
│  DESC        Describe-Express-Specify-Consequences              │
│  ────        Assertive, boundary-setting, clear expectations    │
│              Best for: Setting boundaries, assertive requests   │
│                                                                 │
│  STAR        Situation-Task-Action-Result                       │
│  ────        Comprehensive, context-rich, evidence-based        │
│              Best for: Performance reviews, detailed feedback   │
│                                                                 │
│  CEDAR       Context-Examples-Diagnosis-Actions-Review          │
│  ────        Collaborative, two-way, ensures alignment          │
│              Best for: Complex issues, coaching conversations   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Для кого этот материал

| Уровень | Подходит? | Фокус |
|---------|-----------|-------|
| **Junior** | ✅ | SBI для code review, понимание разных подходов |
| **Middle** | ✅ | COIN для peer feedback, DESC для boundaries |
| **Senior** | ✅ | Выбор framework по ситуации, mentoring |
| **Tech Lead** | ✅ | Все frameworks для 1-on-1, reviews, coaching |

---

## Терминология

| Термин | Что это | IT-аналогия |
|--------|---------|-------------|
| **SBI** | Situation-Behavior-Impact: структура для observation-based feedback | Как debug log — что случилось, где, какой эффект |
| **COIN** | Context-Observation-Impact-Next Steps: developmental feedback | Как CI/CD — выявили проблему, прописали fix |
| **DESC** | Describe-Express-Specify-Consequences: assertive communication | Как SLA — clear expectations и последствия |
| **STAR** | Situation-Task-Action-Result: comprehensive structured feedback | Как detailed ticket — полный context |
| **CEDAR** | Context-Examples-Diagnosis-Actions-Review: collaborative coaching | Как pair programming review — вместе разбираем |

---

## Как это работает?

### Framework 1: SBI (Center for Creative Leadership)

**Структура:**
```
┌─────────────────────────────────────────────────────────────────┐
│                          SBI MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  S — SITUATION                                                  │
│      Когда и где произошло                                      │
│      "На вчерашнем code review..."                              │
│                                                                 │
│  B — BEHAVIOR                                                   │
│      Конкретное наблюдаемое действие                            │
│      "...ты написал комментарий 'это плохой код'..."            │
│                                                                 │
│  I — IMPACT                                                     │
│      Эффект на тебя/команду/проект                              │
│      "...автор PR не понял что исправить и потратил час"        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Когда использовать:**
- Быстрая коррекция поведения
- Code review комментарии
- Позитивный feedback (SBI работает и для похвалы)
- Когда нужно быть конкретным без long discussion

**Пример для code review:**
```
[S] В PR #1234, в методе processOrder
[B] ты используешь raw SQL вместо prepared statements
[I] это создаёт риск SQL injection и не пройдёт security review
```

**Ограничения SBI:**
- Не включает action plan
- Лучше для диагностики, чем для development
- Может звучать "обвинительно" если не балансировать

---

### Framework 2: COIN (Anna Carroll)

**Структура:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         COIN MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  C — CONTEXT                                                    │
│      Ситуация и обстоятельства                                  │
│      "На последних трёх стендапах..."                           │
│                                                                 │
│  O — OBSERVATION                                                │
│      Что ты видел/слышал (не интерпретация)                     │
│      "...ты присоединялся через 5-10 минут после начала"        │
│                                                                 │
│  I — IMPACT                                                     │
│      Эффект на людей и процессы                                 │
│      "...команда ждала или пересказывала обсуждённое"           │
│                                                                 │
│  N — NEXT STEPS                                                 │
│      Что делать дальше (совместно)                              │
│      "Что поможет приходить вовремя? Как я могу помочь?"        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое отличие от SBI:** Next Steps создаёт forward-looking action plan и вовлекает получателя в решение.

**Когда использовать:**
- Behavioral change нужен
- Development conversations (1-on-1)
- Сложные поведенческие паттерны
- Когда хочешь collaborative solution

**Пример для 1-on-1:**
```
[C] "За последний спринт
[O] я заметил, что estimation твоих задач отличался от факта
     в среднем на 2-3 дня.
[I] Это усложняет планирование для team и создаёт stress перед
     дедлайнами.
[N] Давай разберём — что влияет на estimation? Может, нужна
     помощь с decomposition задач или другой буфер на unknowns?"
```

**Ограничения COIN:**
- Требует больше времени
- Нужен two-way dialogue
- Не подходит для quick corrections

---

### Framework 3: DESC (Sharon & Gordon Bower)

**Структура:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         DESC MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  D — DESCRIBE                                                   │
│      Опиши ситуацию объективно                                  │
│      "Когда ты берёшь мои задачи без согласования..."           │
│                                                                 │
│  E — EXPRESS                                                    │
│      Вырази свои чувства (I-statements)                         │
│      "...я чувствую, что мой вклад не ценится"                  │
│                                                                 │
│  S — SPECIFY                                                    │
│      Чётко укажи чего хочешь                                    │
│      "Я хочу, чтобы ты спрашивал меня перед переназначением"    │
│                                                                 │
│  C — CONSEQUENCES                                               │
│      Позитивные последствия если request выполнится             │
│      "Так мы оба будем в курсе workload и сможем лучше          │
│       планировать"                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое отличие:** DESC assertive — ты чётко говоришь что хочешь и какие последствия. Это boundary-setting tool.

**Когда использовать:**
- Нужно установить границы
- Assertive request
- Когда ты уверен что прав
- Профессиональные boundaries

**Пример для boundary-setting:**
```
[D] "Когда в 11 вечера приходят slack-сообщения с пометкой urgent
[E] я чувствую стресс даже в нерабочее время, это влияет на
     мой rest и продуктивность на следующий день.
[S] Я прошу: если не P0 инцидент — давай обсуждать рабочие
     вопросы в рабочее время.
[C] Так я буду более эффективен и available когда это реально
     срочно."
```

**Ограничения DESC:**
- Звучит директивно
- Не для collaborative exploration
- Лучше когда знаешь решение

---

### Framework 4: STAR (David Bonham-Carter)

**Структура:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         STAR MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  S — SITUATION                                                  │
│      Контекст события                                           │
│      "Во время миграции на новую версию API..."                 │
│                                                                 │
│  T — TASK                                                       │
│      Конкретная задача                                          │
│      "...твоя задача была обеспечить backward compatibility"    │
│                                                                 │
│  A — ACTION                                                     │
│      Что человек сделал                                         │
│      "...ты создал adapter layer и написал integration tests"   │
│                                                                 │
│  R — RESULT                                                     │
│      Конкретный результат                                       │
│      "...благодаря этому миграция прошла без downtime"          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Расширение STAR-AR:** Добавляет Alternative Action и Alternative Result для developmental feedback.

**Когда использовать:**
- Performance reviews
- Detailed feedback sessions
- Documenting achievements
- Когда нужен полный context

**Пример для performance review:**
```
[S] "В Q3, когда мы переходили на Kubernetes
[T] ты был ответственен за CI/CD pipeline migration
[A] ты провёл аудит текущих процессов, создал rollback strategy,
     и организовал postmortem после каждого этапа
[R] миграция завершилась на 2 недели раньше срока с 99.9% uptime"
```

**Ограничения STAR:**
- Длинный формат
- Не для quick feedback
- Требует preparation

---

### Framework 5: CEDAR

**Структура:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        CEDAR MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  C — CONTEXT                                                    │
│      Объясни ситуацию и зачем этот разговор                     │
│                                                                 │
│  E — EXAMPLES                                                   │
│      Приведи конкретные примеры (2-3)                           │
│                                                                 │
│  D — DIAGNOSIS                                                  │
│      Спроси мнение получателя о причинах                        │
│      "Как ты видишь ситуацию? Что происходит?"                  │
│                                                                 │
│  A — ACTIONS                                                    │
│      Совместно определите действия                              │
│      "Что ты предлагаешь? Как могу помочь?"                     │
│                                                                 │
│  R — REVIEW                                                     │
│      Подтверди понимание и agreement                            │
│      "Итак, мы договорились о X, Y, Z. Верно?"                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое отличие:** CEDAR maximally collaborative — получатель участвует в diagnosis и action planning. Review в конце ensures alignment.

**Когда использовать:**
- Coaching conversations
- Сложные/sensitive issues
- Когда нужен buy-in
- Long-term development

**Пример для coaching:**
```
[C] "Хочу обсудить communication с stakeholders — это важно
     для твоего роста в senior.
[E] Вот примеры: на встрече с продуктом ты использовал много
     технических терминов, и на ретро PM сказал что не понял
     timeline.
[D] Как ты видишь эти ситуации? Что было challenging?
[A] Что думаешь — как можно адаптировать communication?
     Чем могу помочь?
[R] Окей, итак: ты попробуешь готовить 1-pager summary
     для non-tech audience, и мы review'им вместе перед
     следующей презентацией. Согласен?"
```

**Ограничения CEDAR:**
- Занимает много времени
- Требует trust и openness
- Не для quick corrections

---

## Сравнительная таблица

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    СРАВНЕНИЕ FEEDBACK FRAMEWORKS                          │
├──────────┬────────────┬────────────┬──────────────┬────────────────────────┤
│ Framework│ Время      │ Direction  │ Лучше для    │ Ограничения            │
├──────────┼────────────┼────────────┼──────────────┼────────────────────────┤
│ SBI      │ 1-2 мин    │ One-way    │ Quick fix,   │ Нет action plan        │
│          │            │            │ code review  │                        │
├──────────┼────────────┼────────────┼──────────────┼────────────────────────┤
│ COIN     │ 5-10 мин   │ Two-way    │ Behavioral   │ Требует dialogue       │
│          │            │            │ change       │                        │
├──────────┼────────────┼────────────┼──────────────┼────────────────────────┤
│ DESC     │ 2-3 мин    │ One-way    │ Boundaries,  │ Директивный тон        │
│          │            │            │ assertive    │                        │
├──────────┼────────────┼────────────┼──────────────┼────────────────────────┤
│ STAR     │ 5-10 мин   │ One-way    │ Performance  │ Требует preparation    │
│          │            │            │ review       │                        │
├──────────┼────────────┼────────────┼──────────────┼────────────────────────┤
│ CEDAR    │ 15-30 мин  │ Two-way    │ Coaching,    │ Time-intensive         │
│          │            │            │ development  │                        │
└──────────┴────────────┴────────────┴──────────────┴────────────────────────┘
```

---

## Пошаговый процесс выбора

### Decision Tree

```
                        ┌─────────────────────┐
                        │ Какой тип feedback? │
                        └─────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │ Quick   │   │ Develop-│   │ Boundary│
              │ correct │   │ mental  │   │ setting │
              └────┬────┘   └────┬────┘   └────┬────┘
                   │             │             │
                   ▼             │             ▼
              ┌─────────┐       │        ┌─────────┐
              │   SBI   │       │        │  DESC   │
              └─────────┘       │        └─────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              ┌─────────┐ ┌─────────┐ ┌─────────┐
              │ Simple  │ │ Complex │ │ Perfor- │
              │ behavior│ │ coaching│ │ review  │
              └────┬────┘ └────┬────┘ └────┬────┘
                   │           │           │
                   ▼           ▼           ▼
              ┌─────────┐ ┌─────────┐ ┌─────────┐
              │  COIN   │ │  CEDAR  │ │  STAR   │
              └─────────┘ └─────────┘ └─────────┘
```

### Вопросы для выбора

1. **Сколько времени есть?**
   - < 2 мин → SBI или DESC
   - 5-10 мин → COIN или STAR
   - 15+ мин → CEDAR

2. **Нужен ли dialogue?**
   - Нет, я знаю решение → SBI, DESC, STAR
   - Да, хочу collaborative → COIN, CEDAR

3. **Это про behavior change или boundary?**
   - Behavior change → COIN, CEDAR
   - Boundary → DESC

4. **Это performance review?**
   - Да, formal → STAR
   - Нет, ongoing → другие

---

## Скрипты и Templates

### Use Case 1: Code Review (SBI)

**Ситуация:** Неоптимальный код в PR

**Template:**
```
[S] В файле payment_service.py, строка 145
[B] используется синхронный HTTP call внутри цикла
[I] это создаёт N+1 проблему и замедлит checkout при
    большом количестве items

Предлагаю: batch request или async. Что думаешь?
```

### Use Case 2: 1-on-1 Development (COIN)

**Ситуация:** Разработчик не участвует в design discussions

**Template:**
```
[C] "Хочу обсудить твоё участие в technical discussions.
     Это важно для роста в senior.

[O] На последних трёх architecture reviews я заметил,
     что ты не высказывал мнение, даже когда обсуждали
     систему которую ты знаешь лучше всех.

[I] Команда упускает твою экспертизу, и это влияет
     на качество решений.

[N] Что мешает участвовать активнее? Чем могу помочь —
     может, предварительно обсуждать ideas перед митингом?"
```

### Use Case 3: Setting Boundaries (DESC)

**Ситуация:** Коллега часто прерывает твою работу

**Template:**
```
[D] "Когда ты подходишь с вопросами несколько раз в час
     без предупреждения

[E] мне сложно сосредоточиться на сложных задачах,
     и я теряю context каждый раз

[S] Давай договоримся: несрочные вопросы через Slack,
     я отвечу в ближайший break. Срочные — конечно,
     подходи сразу.

[C] Так я смогу быть более продуктивным и отвечать
     на твои вопросы quality time."
```

### Use Case 4: Performance Review (STAR)

**Ситуация:** Годовой review с примером achievement

**Template:**
```
[S] "В Q2, когда случился security incident с утечкой
     credentials

[T] ты взял на себя response coordination: аудит,
     rotation secrets, и communication

[A] ты в течение 4 часов провёл полный audit, создал
     runbook для будущих инцидентов, и организовал
     blameless postmortem

[R] мы восстановили security за 6 часов вместо ожидаемых
     24, и внедрили secrets rotation automation"
```

### Use Case 5: Coaching Conversation (CEDAR)

**Ситуация:** Помочь разработчику улучшить estimation

**Template:**
```
[C] "Давай обсудим planning и estimation — это skill
     который откроет тебе путь к tech lead.

[E] Вот что я наблюдаю: задача по API миграции была
     estimated на 3 дня, заняла 8. Search refactoring —
     2 дня estimated, 5 фактически.

[D] Как ты сам видишь эти ситуации? Что влияет на gap?

[A] Что думаешь можно попробовать? Может, decomposition
     на более мелкие части? Или buffer на unknowns?

[R] Окей, итак: ты попробуешь разбивать задачи на
     chunks не больше 1 дня и добавлять 30% buffer.
     Review'им через 2 спринта. Согласен?"
```

---

## Распространённые ошибки

### Ошибка 1: One Framework for All

**Неправильно:**
Использовать SBI для coaching conversation

**Почему:**
SBI диагностирует, но не развивает. Для development нужен COIN или CEDAR.

**Правильно:**
Выбирать framework по цели

### Ошибка 2: Skipping Components

**Неправильно:**
```
COIN без Next Steps:
"Ты опаздываешь на митинги, это задерживает всех."
[И всё. Нет N.]
```

**Почему:**
Без Next Steps — это complaint, не developmental feedback.

**Правильно:**
```
"...Что поможет приходить вовремя? Может, reminder?"
```

### Ошибка 3: Impact Without Facts

**Неправильно:**
```
[B] "Ты был груб"  ← интерпретация
[I] "Все расстроились"  ← vague
```

**Правильно:**
```
[B] "Ты сказал 'это глупая идея'"  ← факт
[I] "После этого Маша не предлагала ничего остаток митинга"  ← specific
```

### Ошибка 4: DESC как угроза

**Неправильно:**
```
[C] "Если не перестанешь — я пойду к менеджеру"
```

**Почему:**
Consequences должны быть позитивными — что улучшится, если request выполнится.

**Правильно:**
```
[C] "Так мы оба будем эффективнее и сохраним хорошие отношения"
```

---

## Когда использовать / НЕ использовать

### Quick Reference

| Ситуация | Framework | Почему |
|----------|-----------|--------|
| Code review comment | SBI | Quick, specific |
| Behavioral pattern | COIN | Action-oriented |
| Personal boundary | DESC | Assertive, clear |
| Performance review | STAR | Comprehensive |
| Career coaching | CEDAR | Collaborative |

### НЕ используй

| Ситуация | Что НЕ использовать | Почему |
|----------|---------------------|--------|
| Quick Slack feedback | CEDAR | Too long |
| Sensitive topic | SBI only | Needs dialogue |
| Formal review | COIN only | Needs documentation |

---

## Практика

### Упражнение 1: Framework Matching

**Сценарии:**
1. Разработчик оставляет плохие code review comments
2. Нужно попросить коллегу не писать в нерабочее время
3. Performance review discussion
4. Помочь junior улучшить debugging skills

**Задача:** Выбери framework для каждого

<details><summary>Ответы</summary>

1. COIN — behavioral change нужен, не just pointing out
2. DESC — boundary setting
3. STAR — comprehensive, documented
4. CEDAR — collaborative coaching
</details>

### Упражнение 2: Convert SBI to COIN

**SBI feedback:**
```
На вчерашнем митинге ты перебил Сашу три раза.
Из-за этого она потеряла мысль и митинг затянулся.
```

**Задача:** Добавь Next Steps для COIN

<details><summary>Ответ</summary>

```
[C] На вчерашнем митинге
[O] ты перебил Сашу три раза
[I] из-за этого она потеряла мысль и митинг затянулся
[N] Что если попробовать паузу 2 секунды после того
    как человек замолчит, перед тем как говорить?
    Или использовать raise hand в Zoom?
```
</details>

### Ежедневная практика

| День | Упражнение | Контекст |
|------|------------|----------|
| Пн | SBI practice | Code review — используй SBI |
| Вт | COIN в 1-on-1 | Добавь Next Steps |
| Ср | DESC reflection | Где нужны boundaries? |
| Чт | STAR prep | Подготовь STAR для review |
| Пт | Framework review | Какой framework использовал на неделе? |

---

## Связанные темы

### Prerequisites
- [[giving-feedback]] — базовое понимание feedback

### Эта тема открывает
- [[performance-conversations]] — STAR для reviews
- [[difficult-conversations]] — все frameworks применимы

### Связанные навыки
- [[active-listening]] — важно для two-way frameworks (COIN, CEDAR)
- [[conflict-resolution]] — DESC для границ в конфликтах

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [CCL: SBI Model](https://www.ccl.org/articles/leading-effectively-articles/closing-the-gap-between-intent-vs-impact-sbii/) | Framework | SBI structure, examples |
| 2 | [Pop.Work: 5 Feedback Methods](https://blog.pop.work/popwork-management-tips/the-art-of-feedback-comparing-5-feedback-methods/) | Comparison | Framework comparison |
| 3 | [JOIN: 10 Feedback Models](https://join.com/recruitment-hr-blog/feedback-models) | Guide | COIN, DESC, CEDAR details |
| 4 | [Rahul Goyal: SBI vs COIN vs STAR](https://rahulgoyal.co/justdraft/feedback-frameworks-sbi-coin-star-methods/) | Comparison | Practical comparison |
| 5 | [Teamflect: Feedback Models 2025](https://teamflect.com/blog/employee-engagement/feedback-models) | Guide | Best practices |
| 6 | [Insperity: STAR Model](https://www.insperity.com/blog/start-with-star-how-to-avoid-saying-things-that-kill-employee-motivation/) | Tutorial | STAR examples |
| 7 | [Mirro: Feedback Framework](https://mirro.io/blog/feedback-framework/) | Overview | Framework principles |
| 8 | [Training Course Material: STAR](https://trainingcoursematerial.com/free-training-articles/coaching-feedback/star-feedback-model) | Tutorial | STAR detailed guide |

*Исследование проведено: 2026-01-18*

---

---

## Проверь себя

> [!question]- Разработчик третий спринт подряд занижает estimation задач. Ты — его тимлид. Какой framework ты выберешь и почему SBI здесь недостаточен?
> COIN или CEDAR. SBI лишь зафиксирует факт ("estimation отличается от факта на 2-3 дня") и его последствия, но не создаст action plan и не вовлечёт человека в поиск причин. COIN добавляет Next Steps ("Что влияет на gap? Как помочь с decomposition?"), а CEDAR идёт ещё дальше — через Diagnosis и совместный Actions. Повторяющийся паттерн требует developmental подхода, не quick fix.

> [!question]- Почему в DESC модели Consequences должны быть позитивными, а не угрожающими? Как это связано с принципами negotiation?
> Позитивные Consequences показывают выгоду для обеих сторон — это создаёт win-win framing вместо ультиматума. Угроза ("пойду к менеджеру") переводит разговор в adversarial режим — собеседник включает защиту. Это напрямую перекликается с principled negotiation (Fisher & Ury): фокус на интересах, а не на позициях. Позитивные последствия — это по сути BATNA для обеих сторон, показывающая совместную выгоду от сотрудничества.

> [!question]- Тебе нужно дать feedback в трёх ситуациях за один день: (1) неоптимальный SQL в PR, (2) 1-on-1 о том что junior не участвует в design discussions, (3) годовой performance review. Какой framework для каждой ситуации и сколько суммарно времени потребуется?
> (1) SBI — 1-2 мин: ситуация (PR, строка N), поведение (raw SQL), impact (N+1 проблема). (2) COIN — 5-10 мин: контекст, наблюдение, impact на команду, Next Steps с вовлечением. (3) STAR — 5-10 мин: Situation, Task, Action, Result с конкретными метриками. Суммарно: 11-22 мин. Ключевой принцип: глубина framework пропорциональна сложности задачи и доступному времени.

> [!question]- Представь, что ты применяешь CEDAR для coaching разработчика, но на этапе Diagnosis он говорит "всё нормально, проблем нет". Какие два шага предпримешь, чтобы продвинуть диалог, и чем CEDAR здесь лучше одностороннего STAR?
> Шаг 1: вернуться к Examples с конкретными данными ("estimation 3 дня, факт 8 — как объяснишь разницу?") — факты сложнее отрицать. Шаг 2: переформулировать Diagnosis не как проблему, а как growth opportunity ("Я вижу потенциал для senior-уровня, для этого нужен точный estimation — что поможет?"). CEDAR лучше STAR, потому что STAR — one-way: ты говоришь, человек слушает. CEDAR через двусторонний Diagnosis создаёт ownership — человек сам участвует в решении, что повышает вероятность реальных изменений.

---

## Ключевые карточки

SBI расшифровывается как...?
?
Situation-Behavior-Impact. Situation — когда и где, Behavior — конкретное наблюдаемое действие, Impact — эффект на команду/проект. Используется для быстрой коррекции (1-2 мин).

Чем COIN отличается от SBI?
?
COIN добавляет **Next Steps** — совместный action plan. SBI диагностирует проблему, COIN двигает к решению. COIN = Context-Observation-Impact-Next Steps. Требует two-way dialogue (5-10 мин).

Когда использовать DESC, а не COIN?
?
DESC — для **установки границ** (boundary setting), когда ты уверен в решении и нужен assertive request. COIN — для **развития поведения**, когда нужен collaborative поиск решения. DESC = Describe-Express-Specify-Consequences.

Почему Consequences в DESC должны быть позитивными?
?
Негативные последствия превращают feedback в угрозу и включают защитную реакцию. Позитивные Consequences показывают **win-win**: "Так мы оба будем эффективнее" вместо "Иначе я пойду к менеджеру".

STAR vs STAR-AR — в чём разница?
?
STAR = Situation-Task-Action-Result — для documenting achievements. STAR-AR добавляет **Alternative Action** и **Alternative Result** — показывает что можно было сделать иначе. STAR-AR = developmental feedback в performance review.

Какой framework самый collaborative и почему?
?
**CEDAR**. В нём получатель участвует в Diagnosis (анализ причин) и Actions (план действий), а Review в конце фиксирует agreement. Это создаёт ownership и buy-in. Занимает 15-30 мин — самый time-intensive.

В чём главная ошибка "COIN без N"?
?
Без Next Steps COIN превращается в **complaint** (жалобу), а не developmental feedback. "Ты опаздываешь, это задерживает всех" — это проблема без решения. Нужно: "Что поможет приходить вовремя? Может, reminder?"

Как выбрать framework по двум ключевым вопросам?
?
**Вопрос 1: Сколько времени?** < 2 мин — SBI/DESC, 5-10 мин — COIN/STAR, 15+ мин — CEDAR. **Вопрос 2: Нужен ли dialogue?** Нет — SBI/DESC/STAR (one-way). Да — COIN/CEDAR (two-way, collaborative).

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Основы feedback | [[giving-feedback]] | Prerequisite: базовые принципы до изучения frameworks |
| Получение feedback | [[receiving-feedback]] | Вторая сторона процесса — как принимать feedback по тем же моделям |
| Сложные разговоры | [[performance-conversations]] | Применение STAR и CEDAR в formal performance reviews |
| Разрешение конфликтов | [[conflict-resolution]] | DESC для границ в конфликтах, COIN для поведенческих изменений |
| Активное слушание | [[active-listening]] | Критично для two-way frameworks (COIN, CEDAR) — без listening нет dialogue |
| 1-on-1 встречи | [[one-on-one-meetings]] | Практический контекст для COIN и CEDAR — где именно применять |
| Управление перформансом | [[performance-management]] | Системный взгляд: feedback frameworks как часть performance cycle |

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
