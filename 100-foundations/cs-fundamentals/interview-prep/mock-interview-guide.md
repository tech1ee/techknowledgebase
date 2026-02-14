---
title: "Руководство по мок-интервью"
created: 2026-02-09
modified: 2026-02-13
type: guide
status: published
tags:
  - topic/cs-fundamentals
  - type/guide
  - level/intermediate
  - interview
related:
  - "[[leetcode-roadmap]]"
  - "[[common-mistakes]]"
  - "[[problem-solving-framework]]"
prerequisites:
  - "[[problem-solving-framework]]"
  - "[[big-o-complexity]]"
reading_time: 20
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Mock Interview Guide

## TL;DR

Mock interviews критически важны — симулируют давление реального интервью. **Минимум 1 mock в неделю** при активной подготовке. Ключевые навыки: think aloud, whiteboard coding, STAR для behavioral. Платформы: Pramp (бесплатно), Interviewing.io, peer practice.

---

## Интуиция

### Аналогия 1: Mock как репетиция перед концертом

```
МУЗЫКАНТ = КАНДИДАТ:

"Я отлично играю дома" ≠ "Я сыграю на сцене"

Домашняя практика:        Концерт (интервью):
• Тишина                  • Публика смотрит
• Можно остановиться      • Нужно продолжать
• Нет давления            • Стресс, адреналин
• Ошибки незаметны        • Все видят

Mock interview = генеральная репетиция со зрителями.
Лучше провалить репетицию, чем концерт!
```

### Аналогия 2: Think Aloud как GPS для интервьюера

```
БЕЗ THINK ALOUD:              С THINK ALOUD:
┌──────────────────┐          ┌──────────────────┐
│ Кандидат молчит  │          │ "Я думаю об      │
│ *думает*         │          │  этом подходе,   │
│ *думает*         │          │  потому что..."  │
│                  │          │                  │
│ Интервьюер:      │          │ Интервьюер:      │
│ "Что происходит?"│          │ "Можно подсказать│
│ "Он завис?"      │          │  что HashMap     │
│                  │          │  будет быстрее"  │
└──────────────────┘          └──────────────────┘

Молчание = чёрный ящик. Think aloud = прозрачность.
```

---

## Частые ошибки

### Ошибка 1: Практиковать только алгоритмы, не формат

**СИМПТОМ:** "Я решаю Hard на LeetCode, но провалил интервью"

```
Домашняя практика:          Интервью:
• Безлимитное время         • 45 минут на всё
• IDE с автодополнением     • Whiteboard/простой редактор
• Тишина                    • Нужно объяснять каждый шаг
• Можно гуглить             • Только своя память
```

**РЕШЕНИЕ:** 1 mock в неделю имитирует реальные условия.

### Ошибка 2: Не получать feedback после mock

**СИМПТОМ:** Повторяешь одни и те же ошибки

```
// НЕПРАВИЛЬНО:
Mock → "Было хорошо" → Следующий mock → Те же ошибки

// ПРАВИЛЬНО:
Mock → Конкретный feedback:
  - "Ты молчал 2 минуты на строке 15"
  - "Не проверил null input"
  - "Complexity неправильный"
→ Работа над конкретными проблемами → Следующий mock
```

### Ошибка 3: Слишком много mock без практики между ними

**СИМПТОМ:** 5 mock в неделю, все провальные

```
Mock без подготовки = повторение ошибок.

ПРАВИЛЬНЫЙ ЦИКЛ:
Mock → Feedback → 3-5 дней практики → Mock → Feedback...

НЕ: Mock → Mock → Mock → Mock → "Почему не улучшаюсь?"
```

---

## Ментальные модели

### Модель 1: "Интервьюер хочет тебя нанять"

```
MINDSET SHIFT:

❌ "Интервьюер ищет причины отказать"
✅ "Интервьюер ищет причины нанять"

ПОСЛЕДСТВИЯ:
• Hints = помощь, не ловушка
• Follow-up вопросы = интерес, не критика
• Сложные задачи = возможность показать себя

Интервьюер потратил время на тебя.
Он ХОЧЕТ найти хорошего кандидата.
```

### Модель 2: "STAR для любого вопроса"

```
STAR FRAMEWORK (behavioral):

S - Situation: "В прошлом проекте..."
T - Task: "Моя задача была..."
A - Action: "Я сделал..."
R - Result: "В результате..."

ПРИМЕНЕНИЕ:
"Расскажи о сложном баге"
S: "В production упала база"
T: "Нужно было найти причину за 30 минут"
A: "Проверил логи, нашёл deadlock, добавил timeout"
R: "Downtime 15 минут, добавили мониторинг"
```

---

## Зачем это нужно?

**Реальность:**

Знание алгоритмов ≠ прохождение интервью. Mock interviews тренируют:
- Работу под давлением
- Вербальную коммуникацию
- Time management
- Получение и применение hints

**Статистика:**
- Кандидаты с 5+ mock interviews имеют в 3 раза больше шансов
- 70% кандидатов говорят, что mock interviews были crucial
- Первые 2-3 mock interviews обычно провальные — это нормально!

---

## Типы интервью

### 1. Coding Interview (45-60 min)

```
Структура:
├─ 5 min: Intro & icebreaker
├─ 35-45 min: 1-2 coding problems
├─ 5-10 min: Your questions
└─ Optional: Follow-up questions

Что оценивают:
□ Problem solving process
□ Code quality
□ Communication
□ Handling of edge cases
□ Time/space complexity analysis
```

### 2. System Design (45-60 min)

```
Структура:
├─ 5 min: Problem statement
├─ 35-45 min: Design discussion
├─ 5-10 min: Deep dive on component
└─ 5 min: Your questions

Что оценивают:
□ Requirements gathering
□ High-level architecture
□ Trade-off analysis
□ Scalability thinking
□ Technical depth
```

### 3. Behavioral Interview (30-45 min)

```
Структура:
├─ 5 min: Intro
├─ 25-35 min: 4-6 behavioral questions
└─ 5 min: Your questions

Формат: STAR method
□ Situation — контекст
□ Task — твоя роль
□ Action — что сделал
□ Result — результат (с метриками!)
```

---

## Coding Interview Playbook

### Before Interview (1 день до)

```
□ Выспаться (8 часов минимум)
□ Подготовить environment:
  - Тихое место
  - Стабильный интернет
  - Рабочая камера/микрофон
  - Блокнот для заметок
□ Повторить слабые паттерны
□ Решить 1-2 Easy для разогрева
```

### During Interview

#### Фаза 1: Understanding (5-7 min)

```
1. Выслушай задачу
2. Переформулируй:
   "So let me make sure I understand correctly:
   Given [input], I need to return [output]..."

3. Уточни constraints:
   - "What's the size range of input?"
   - "Can there be duplicates?"
   - "Is the array sorted?"
   - "What should I return if no solution?"

4. Проверь на примере:
   "For input [1,2,3] with target 5,
   the output would be [1,2], correct?"
```

#### Фаза 2: Planning (3-5 min)

```
1. Озвучь brute force:
   "The brute force would be O(n²) with two loops..."

2. Обсуди optimization:
   "But we can use a HashMap to achieve O(n)..."

3. Confirm approach:
   "Should I proceed with this approach?"

4. Обозначь edge cases:
   "I'll handle empty array and no solution cases"
```

#### Фаза 3: Coding (20-25 min)

```
1. Пиши и объясняй:
   "First, I'll initialize a HashMap..."

2. Используй meaningful names:
   // ❌ int a, b, c
   // ✅ int left, right, maxSum

3. Обрабатывай edge cases первыми:
   if (nums.isEmpty()) return -1

4. Think aloud:
   "Now I'm iterating through the array..."
   "Here I'm checking if complement exists..."

5. Если застрял:
   "I'm thinking about how to handle..."
   "Could you give me a hint on this part?"
```

#### Фаза 4: Testing (5-7 min)

```
1. Trace through example:
   "Let me walk through with [1,2,3], target=5:
    - i=0: num=1, complement=4, not found, add to map
    - i=1: num=2, complement=3, not found, add to map
    - i=2: num=3, complement=2, found! return [1,2]"

2. Check edge cases:
   "For empty array: returns -1 ✓
    For no solution: returns -1 ✓"

3. Fix bugs calmly:
   "I see an issue here, let me fix it..."
```

#### Фаза 5: Optimization (2-3 min)

```
1. Анализируй complexity:
   "Time: O(n) - single pass
    Space: O(n) - HashMap storage"

2. Discuss trade-offs:
   "We could reduce space to O(1) by sorting,
    but that would make time O(n log n)"

3. Mention further optimizations:
   "If we needed to handle this repeatedly,
    we could precompute..."
```

---

## Communication Templates

### When Starting

```
"Thank you for the problem. Let me start by
understanding the requirements..."
```

### When Clarifying

```
"Just to confirm: when you say [X],
do you mean [interpretation A] or [interpretation B]?"
```

### When Planning

```
"My initial thought is to use [approach].
This would give us O(X) time and O(Y) space.
Does this sound like a reasonable direction?"
```

### When Stuck

```
"I'm considering a few approaches here.
Could you help me think about which direction
might be more fruitful?"
```

### When Finding Bug

```
"I see an issue in my logic here.
Let me trace through to find it...
Ah, the problem is [explanation].
Let me fix that."
```

### When Finishing

```
"I believe this solution handles all the cases we discussed.
It runs in O(X) time and O(Y) space.
Would you like me to optimize further or discuss
any edge cases?"
```

---

## Whiteboard Coding

### Challenges

```
No IDE:
- No autocomplete
- No syntax highlighting
- No compiler errors
- No running code

Physical:
- Limited space
- Erasing takes time
- Hard to insert code
```

### Strategies

```
1. Планируй layout:
   ┌─────────────────────────────────────┐
   │ Example:          │ Pseudocode:     │
   │ [1,2,3], target=5 │ 1. init map     │
   │                   │ 2. for each num │
   │ Edge cases:       │ 3. check comp   │
   │ - empty           │ 4. add to map   │
   │ - no solution     │                 │
   └─────────────────────────────────────┘

2. Оставляй пробелы:
   for (i in 0 until n) {

       // space for insertion

       map[num] = i
   }

3. Пиши разборчиво:
   - Большие буквы
   - Достаточный интервал
   - Отступы!
```

### Practice Without IDE

```
Weekly practice:
□ Solve 2-3 problems on paper
□ Practice on whiteboard app (Google Jamboard)
□ Type in plain text editor (no autocomplete)
□ Explain solution to rubber duck
```

---

## STAR Method для Behavioral

### Формат ответа

```
S - Situation (10-15 sec):
"In my previous role at [Company],
we had a [situation/problem]..."

T - Task (10-15 sec):
"My responsibility was to [task].
The goal was [measurable outcome]..."

A - Action (60-90 sec):
"First, I [action 1]...
Then, I [action 2]...
I also [action 3]..."

R - Result (20-30 sec):
"As a result, [quantifiable outcome].
This led to [business impact].
I learned [lesson]..."
```

### Common Questions + Framework

| Question | What They Want | Focus On |
|----------|---------------|----------|
| Tell me about yourself | Career narrative | Progression + why here |
| Biggest challenge | Problem-solving | Process + outcome |
| Conflict with teammate | Collaboration | Resolution + learning |
| Failure experience | Self-awareness | Ownership + growth |
| Why this company | Motivation | Research + fit |
| Why leave current job | Professionalism | Positive framing |

### Example Answer

```
Q: "Tell me about a time you disagreed with your manager"

S: "At [Company], my manager wanted to use technology X
   for our new feature, but I believed Y was better suited."

T: "I needed to either convince them or understand
   their reasoning and align with the decision."

A: "I prepared a comparison document with:
   - Performance benchmarks
   - Team expertise analysis
   - Long-term maintenance costs
   I scheduled a 1-on-1 to discuss objectively.
   I listened to their concerns about Y's learning curve.
   We compromised: start with X, migrate to Y later."

R: "We launched on time with X. Six months later,
   we migrated to Y with 30% better performance.
   I learned the value of data-driven discussions
   and finding middle ground."
```

---

## Mock Interview Platforms

### Free Options

| Platform | Type | Pros | Cons |
|----------|------|------|------|
| [Pramp](https://pramp.com) | Peer | Free, real practice | Varying partner skill |
| [Interviewing.io](https://interviewing.io) | Expert | Anonymous, real engineers | Limited free slots |
| Friends/Colleagues | Peer | Comfortable, flexible | May not be rigorous |

### Paid Options

| Platform | Price | Best For |
|----------|-------|----------|
| Interviewing.io Premium | $100+ | Expert feedback |
| Exponent | $12/mo | Mock + courses |
| Prepfully | Pay per mock | Specific companies |

### DIY Mock Interview

```
With a friend:
1. Выберите роли (interviewer/candidate)
2. Interviewer готовит 1-2 задачи
3. Строгий тайминг (45 min)
4. No помощь (только hints)
5. Feedback session после (10-15 min)
6. Поменяйтесь ролями

Feedback template:
□ Что было хорошо
□ Что улучшить
□ Communication score (1-5)
□ Problem solving score (1-5)
□ Code quality score (1-5)
```

---

## Self-Mock Interview

### Solo Practice Technique

```
1. Выбери задачу (Medium, не решал раньше)
2. Установи таймер: 45 min
3. Запиши себя (Loom, OBS)
4. Решай вслух
5. После: посмотри запись
6. Оцени себя по критериям
```

### Self-Evaluation Checklist

```
Communication:
□ Прояснил requirements?
□ Объяснил approach перед coding?
□ Думал вслух?
□ Реагировал на stuck спокойно?

Problem Solving:
□ Рассмотрел brute force?
□ Оптимизировал?
□ Обработал edge cases?
□ Проанализировал complexity?

Code Quality:
□ Readable names?
□ Clean structure?
□ No syntax errors?
□ Tested solution?
```

---

## Week Before Interview

### Day-by-Day Plan

```
Day 7: Review weak patterns
Day 6: 2 Medium problems, focus on speed
Day 5: Mock interview (coding)
Day 4: System design review (if applicable)
Day 3: Behavioral prep (STAR stories)
Day 2: Light review, 1-2 Easy problems
Day 1: Rest, prepare logistics

Day 0 (Interview day):
- Wake up early
- Light breakfast
- 1 Easy problem for warm-up
- Review your notes
- Arrive/connect early
```

### Last Minute Checklist

```
□ Rested (7-8 hours sleep)
□ Ate (but not too heavy)
□ Environment ready:
  - Quiet space
  - Good lighting
  - Stable internet
  - Water nearby
□ Tech check:
  - Camera works
  - Microphone works
  - Screen share works
  - IDE/editor ready
□ Notes ready:
  - Company research
  - Your questions
  - STAR stories
```

---

## After Interview

### Immediate Debrief

```
Запиши сразу после:
□ Какие вопросы были?
□ Что пошло хорошо?
□ Где застрял?
□ Какой feedback получил?
□ Что бы сделал по-другому?
```

### Follow-up Email Template

```
Subject: Thank you for the interview

Dear [Interviewer Name],

Thank you for taking the time to interview me today
for the [Position] role. I enjoyed our discussion
about [specific topic discussed].

I'm particularly excited about [something specific
about the role/company mentioned in interview].

If you have any additional questions, please don't
hesitate to reach out.

Best regards,
[Your Name]
```

---

## Common Mistakes in Mocks

### 1. Not treating it seriously

```
❌ НЕПРАВИЛЬНО:
"It's just practice, I'll joke around"

✅ ПРАВИЛЬНО:
Treat every mock as a real interview
```

### 2. Not getting feedback

```
❌ НЕПРАВИЛЬНО:
Finish mock, move on

✅ ПРАВИЛЬНО:
10-15 min feedback discussion:
"What was my weakest area?"
"How was my communication?"
"Would you have hired me?"
```

### 3. Same type of problems

```
❌ НЕПРАВИЛЬНО:
Practice only arrays every time

✅ ПРАВИЛЬНО:
Rotate: Arrays → Trees → Graphs → DP → ...
```

### 4. Skipping behavioral

```
❌ НЕПРАВИЛЬНО:
"I'll just wing the behavioral"

✅ ПРАВИЛЬНО:
Practice STAR answers out loud
Record yourself, review
```

---

## Связанные темы

### Prerequisites
- [LeetCode Roadmap](./leetcode-roadmap.md) — что практиковать
- [Common Mistakes](./common-mistakes.md) — что избегать

### Next Steps
- System Design preparation
- Company-specific preparation
- Negotiation skills

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Pramp](https://pramp.com) | Platform | Free mock interviews |
| 2 | [Design Gurus](https://www.designgurus.io/blog/mock-interviews-for-software-engineers) | Guide | Mock strategy |
| 3 | [Total Career Solutions](https://www.totalcareersolutions.com/whiteboard-coding-interview-strategies/) | Guide | Whiteboard tips |
| 4 | [Bomberbot](https://www.bomberbot.com/career-advice/how-to-ace-your-software-engineering-technical-interview-in-2024/) | Blog | STAR method |
| 5 | [Tech Interview Handbook](https://www.techinterviewhandbook.org) | Guide | Overall strategy |


---

## Проверь себя

> [!question]- Почему mock interview эффективнее самостоятельной практики на LeetCode?
> Mock симулирует стресс: 1) Наблюдатель (pressure). 2) Time constraint (45 мин). 3) Think aloud (вербализация). 4) Feedback от peer. LeetCode дома: нет давления, можно гуглить, нет нужды объяснять. На реальном интервью 30-40% кандидатов 'замирают' от стресса — mock тренирует resistance.

> [!question]- Как правильно давать feedback после mock interview?
> Структура: 1) Что хорошо (конкретно). 2) Что улучшить (конкретно). 3) Actionable advice. Пример: 'Хорошо: быстро определил паттерн. Улучшить: не проверил edge case empty array. Совет: добавь чеклист edge cases перед submit.' Не 'было нормально' — конкретика помогает.

> [!question]- Сколько mock interview в неделю оптимально и когда начинать?
> Minimum: 1 mock в неделю при активной подготовке. Оптимально: 2-3 в неделю за 2-3 недели до интервью. Начинать: после 30-40 задач LeetCode (есть база паттернов). Слишком рано: демотивирует. Слишком поздно: не успеешь привыкнуть к формату.

## Ключевые карточки

Какие платформы для mock interview?
?
Бесплатные: Pramp (P2P matching, автоматический), LeetCode Discuss (найти peer). Платные: Interviewing.io ($225+ за mock с инженером из FAANG), Exponent. Peer practice: найти study buddy, чередовать роли interviewer/candidate.

Что такое Think Aloud и почему это критично?
?
Вербализация мыслительного процесса во время решения. Интервьюер оценивает HOW you think, не только ответ. Паттерн: 'Я вижу отсортированный массив, это подсказывает Binary Search или Two Pointers. Попробую Two Pointers потому что нужна пара...'. Тишина > 30 секунд = red flag.

Как структурировать 45-минутное coding interview?
?
0-5 мин: уточнить условие, edge cases. 5-10 мин: обсудить approach, complexity. 10-35 мин: кодирование. 35-40 мин: тестирование, walkthrough. 40-45 мин: оптимизация, вопросы. Не кодируй до согласования подхода!

Какие роли в mock interview?
?
Interviewer: задаёт задачу, даёт hints (не сразу), наблюдает за процессом, даёт feedback. Candidate: решает, думает вслух, задаёт вопросы. Чередуйте роли: быть interviewer учит оценивать решения и видеть паттерны хороших/плохих ответов.

Как преодолеть 'заморозку' на интервью?
?
1) Recognize: 'я застрял, это нормально'. 2) Вернись к basics: перечитай условие, проверь examples. 3) Brute force: начни с O(n^2), оптимизируй. 4) Попроси hint (не стыдно). 5) Переключи паттерн: если DP не работает — попробуй Greedy. Молчание — худший вариант.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[interview-prep/common-mistakes]] | Типичные ошибки на интервью |
| Углубиться | [[interview-prep/leetcode-roadmap]] | LeetCode Roadmap для подготовки |
| Смежная тема | [[competitive/contest-strategy]] | Contest strategy — схожие навыки |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |


---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
