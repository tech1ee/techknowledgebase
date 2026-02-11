---
title: "Negotiation Fundamentals для IT-специалистов"
created: 2026-01-18
modified: 2026-01-18
type: deep-dive
status: published
difficulty: intermediate
teaches:
  - BATNA
  - ZOPA
  - Anchoring
  - Harvard principled negotiation
  - Iron Triangle
tags:
  - topic/communication
  - type/deep-dive
  - level/intermediate
related:
  - "[[active-listening]]"
  - "[[stakeholder-negotiation]]"
prerequisites:
  - "[[active-listening]]"
  - "[[communication-styles]]"
---

# Negotiation Fundamentals для IT-специалистов

> **TL;DR:** Переговоры — это поиск решения, выгодного обеим сторонам, а не война. Ключи: знай свой BATNA (альтернативу), фокусируйся на интересах (не позициях), используй anchoring для управления ожиданиями. Применяется в: deadline negotiations, scope discussions, salary talks.

---

## Зачем это нужно?

### Представьте ситуацию

**Sprint planning.** PM просит добавить ещё 3 фичи в и так загруженный спринт.

**Без навыка:**
```
PM: "Клиент требует эти 3 фичи к пятнице."
Dev: "Это невозможно."
PM: "Но клиент ждёт!"
Dev: "Ну... ладно, попробуем." (overtime, burnout, баги)

Или:

Dev: "Нет, не буду." (конфликт, репутация "сложного")
```

**С навыком:**
```
PM: "Клиент требует эти 3 фичи к пятнице."
Dev: "Понимаю что это важно для клиента. Давай посмотрим на варианты.
      [Фокус на интересах, не позициях]

      Сейчас в спринте 8 story points, capacity — 10.
      Эти 3 фичи — ещё 6 points. [Anchoring с данными]

      Варианты:
      A) Все 3 фичи → убираем Feature-X из спринта (lower priority)
      B) 2 фичи к пятнице + 1 к понедельнику
      C) MVP версии всех 3 (без edge cases) к пятнице

      Какой вариант лучше соответствует приоритетам клиента?"

PM: "Вариант B, наверное. Первые две — критичные."
Dev: "Договорились. Зафиксируем в Jira."
```

**Результат:** Win-win. PM получает главное, Dev — реалистичный scope.

### Проблема в числах

```
┌──────────────────────────────────────────────────────────────────┐
│                 ПЕРЕГОВОРЫ: СТАТИСТИКА                          │
├──────────────────────────────────────────────────────────────────┤
│  Каждый        Разработчики ведут переговоры ежедневно:         │
│  день          deadlines, scope, priorities, code review         │
├──────────────────────────────────────────────────────────────────┤
│  42%           Проектов превышают бюджет или сроки из-за        │
│  проектов      плохого scope management (PMI)                    │
├──────────────────────────────────────────────────────────────────┤
│  80%           Разработчиков недооценивают сроки                │
│                (planning fallacy) — нужно negotiate buffer      │
├──────────────────────────────────────────────────────────────────┤
│  $5-15K        Средняя разница в зарплате между теми кто        │
│  в год         negotiates и кто нет                              │
├──────────────────────────────────────────────────────────────────┤
│  70%           Конфликтов разрешаются через negotiation,        │
│                а не через эскалацию                              │
└──────────────────────────────────────────────────────────────────┘
```

**Вывод:** Навык переговоров — не опция, а ежедневная необходимость для IT-специалиста.

---

## Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | Необходим | Научись negotiate сроки, scope, и не говорить "да" всему |
| **Middle** | Критичен | Cross-team negotiations, stakeholder management |
| **Senior** | Критичен | Architecture decisions, resource allocation, influence |
| **Tech Lead** | Критичен | Budget, headcount, project priorities, salary for team |

---

## Терминология

| Термин | Что это (простыми словами) | IT-аналогия |
|--------|---------------------------|-------------|
| **BATNA** | Best Alternative To Negotiated Agreement — твой план B | Fallback strategy |
| **ZOPA** | Zone Of Possible Agreement — область где deal возможен | Overlapping range of acceptable values |
| **Anchoring** | Первое число задаёт точку отсчёта | Initial value in negotiation |
| **Position** | То, что человек ГОВОРИТ что хочет | Request |
| **Interest** | То, что человек РЕАЛЬНО хочет (почему) | Root cause / underlying need |
| **Iron Triangle** | Scope, Time, Resources — изменение одного влияет на другие | Project constraints tradeoff |
| **Win-Win** | Решение выгодное обеим сторонам | Mutual benefit |
| **Reservation Price** | Минимум/максимум на который готов согласиться | Threshold / boundary |

---

## Как это работает?

### Harvard Principled Negotiation

Метод из книги "Getting to Yes" (Fisher, Ury, Patton, 1981). Основа всех современных подходов к переговорам.

```
┌──────────────────────────────────────────────────────────────────┐
│             HARVARD PRINCIPLED NEGOTIATION                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. SEPARATE PEOPLE        2. FOCUS ON INTERESTS                │
│      FROM PROBLEM              NOT POSITIONS                     │
│                                                                  │
│   ┌─────────────┐           Position: "Хочу X"                   │
│   │ PERSON ≠    │               ↓                                │
│   │ PROBLEM     │           Interest: "Потому что Y"             │
│   └─────────────┘               ↓                                │
│                             Root need: Z                         │
│                                                                  │
│   3. INVENT OPTIONS         4. USE OBJECTIVE                     │
│      FOR MUTUAL GAIN           CRITERIA                          │
│                                                                  │
│   ┌─────────────┐           ┌─────────────┐                     │
│   │ Brainstorm  │           │ Market data │                     │
│   │ multiple    │           │ Benchmarks  │                     │
│   │ solutions   │           │ Standards   │                     │
│   └─────────────┘           └─────────────┘                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4 принципа подробно

**1. Separate People from Problem**

Проблема ≠ человек. Атакуй проблему, не человека.

```
Неправильно: "Ты всегда даёшь нереальные сроки!"
             (атака на человека → defensiveness)

Правильно:   "Сроки выглядят напряжённо. Давай разберёмся
              какие есть варианты."
             (фокус на проблеме → collaboration)
```

**2. Focus on Interests, Not Positions**

Position — это то, что человек требует.
Interest — это ПОЧЕМУ он этого требует.

```
ПРИМЕР: PM требует релиз в пятницу

Position:  "Релиз должен быть в пятницу!"

Interests (возможные):
├── Клиент уезжает в отпуск и хочет увидеть до
├── Есть маркетинговая кампания привязанная к дате
├── CEO обещал на board meeting
├── PM просто привык к "всё срочно"
└── KPI привязаны к количеству релизов

Разные interests → разные решения:
• Если клиент → можно demo вместо полного релиза
• Если маркетинг → можно feature flag, релиз для узкой аудитории
• Если CEO обещал → эскалация или partial delivery
• Если привычка → образование о реальных costs
```

**3. Invent Options for Mutual Gain**

Не бинарный выбор "да/нет", а генерация вариантов.

```
ВМЕСТО:
├── "Да, сделаю к пятнице" (overtime, баги)
└── "Нет, невозможно" (конфликт)

ГЕНЕРИРУЙ ОПЦИИ:
├── A: Полный scope → дедлайн сдвигается на среду
├── B: Reduced scope (MVP) → дедлайн в пятницу
├── C: Полный scope → добавляем ресурс (pair programming)
├── D: Partial release (feature flags) → остальное в понедельник
└── E: Demo в пятницу → production в понедельник

Пусть stakeholder выбирает — это его tradeoff.
```

**4. Use Objective Criteria**

Используй данные, а не мнения.

```
Неправильно: "Это займёт долго" (субъективно)

Правильно:   "Похожая задача в прошлом спринте заняла 5 дней.
              У нас есть метрики из Jira." (данные)

Объективные критерии:
├── Исторические данные (прошлые спринты, проекты)
├── Industry benchmarks
├── Velocity команды
├── Complexity metrics (story points)
└── Market rates (для salary negotiation)
```

---

## BATNA: Твой план B

### Что такое BATNA

BATNA (Best Alternative To Negotiated Agreement) — лучшее, что ты можешь получить БЕЗ этих переговоров.

```
┌──────────────────────────────────────────────────────────────────┐
│                        BATNA FRAMEWORK                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Если переговоры провалятся, что ты будешь делать?             │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    ТВОЯ СИТУАЦИЯ                        │   │
│   │                          │                              │   │
│   │            ┌─────────────┴─────────────┐                │   │
│   │            │                           │                │   │
│   │      Переговоры                   BATNA                 │   │
│   │      успешны                      (план B)              │   │
│   │            │                           │                │   │
│   │       Agreement                  Alternative            │   │
│   │                                                         │   │
│   │   Выбирай то, что ЛУЧШЕ                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Сильный BATNA = сильная позиция                               │
│   Слабый BATNA = слабая позиция                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Примеры BATNA в IT

| Ситуация | Слабый BATNA | Сильный BATNA |
|----------|--------------|---------------|
| **Salary negotiation** | Нет других offers | 2 competing offers |
| **Scope negotiation** | "Придётся делать overtime" | "Можем отложить feature Y" |
| **Vendor negotiation** | Один vendor на рынке | 3 конкурирующих vendor'а |
| **Deadline negotiation** | "Клиент уйдёт" | "Можем partial delivery" |

### Как улучшить BATNA

**1. Перед salary negotiation:**
```
□ Получи несколько offers (даже если не планируешь уходить)
□ Знай свою market value (levels.fyi, Glassdoor)
□ Имей savings на 6 месяцев (можешь уйти)
```

**2. Перед scope negotiation:**
```
□ Знай какие features можно отложить (low priority)
□ Имей данные о velocity и capacity
□ Подготовь варианты partial delivery
```

**3. Перед vendor negotiation:**
```
□ Research альтернативных vendors
□ Prototype с альтернативой
□ Знай switching costs
```

---

## ZOPA: Зона возможного соглашения

### Что такое ZOPA

ZOPA (Zone Of Possible Agreement) — диапазон, где интересы обеих сторон пересекаются.

```
┌──────────────────────────────────────────────────────────────────┐
│                         ZOPA DIAGRAM                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SELLER (Company)                                               │
│   "Минимум готовы платить: $90K"                                │
│                                                                  │
│            $90K ─────────────────────────► $120K                │
│                  [  Company's range  ]                          │
│                                                                  │
│                        ┌────────────┐                           │
│                        │    ZOPA    │                           │
│                        │ ($90K-$110K)│                          │
│                        └────────────┘                           │
│                                                                  │
│            $80K ─────────────────────────► $110K                │
│                  [  Candidate's range  ]                        │
│                                                                  │
│   BUYER (Candidate)                                             │
│   "Максимум готов принять: $110K"                               │
│                                                                  │
│   ───────────────────────────────────────────────────────────   │
│                                                                  │
│   Если ZOPA нет:                                                │
│                                                                  │
│            $120K ─────────────────────────► $150K               │
│                  [  Company: min $120K  ]                       │
│                                                                  │
│            $80K ─────────────────────────► $100K                │
│                  [  Candidate: max $100K ]                      │
│                                                                  │
│   НЕТ ПЕРЕСЕЧЕНИЯ → deal невозможен                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Как найти ZOPA в IT-переговорах

**Сценарий: Deadline negotiation**

```
PM хочет: релиз к пятнице (position)
Dev оценивает: реалистично — среда следующей недели

Исследуй interests:
• PM: Почему пятница? → "Презентация для CEO в понедельник"
• Dev: Почему среда? → "Тестирование + buffer на баги"

ZOPA может появиться через:
• Partial release (demo-ready к пятнице)
• Reduced scope (core features к пятнице)
• Added resources (pair programming)

Без понимания interests → ZOPA не видна
```

### Расширение ZOPA

Если ZOPA слишком мала или отсутствует:

```
СПОСОБЫ РАСШИРИТЬ ZOPA:

1. ДОБАВИТЬ ПЕРЕМЕННЫЕ
   Не только деньги, но и:
   ├── Remote work days
   ├── Equity / bonus
   ├── Learning budget
   ├── Title upgrade
   └── Project assignment

2. ИЗМЕНИТЬ TIMEFRAME
   ├── "Не сейчас, но через 6 месяцев review"
   └── "Staged delivery вместо big bang"

3. НАЙТИ CREATIVE OPTIONS
   ├── Feature flags для partial delivery
   ├── Beta release для subset of users
   └── Technical debt payoff later
```

---

## Anchoring: Управление ожиданиями

### Как работает anchoring

Первое число в переговорах становится "якорем" — точкой отсчёта для всех последующих обсуждений.

```
┌──────────────────────────────────────────────────────────────────┐
│                     ANCHORING EFFECT                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   БЕЗ ANCHOR:                                                   │
│   "Сколько это стоит?" → Неопределённость                       │
│                                                                  │
│   С ANCHOR:                                                     │
│   "Похожие проекты стоят $50-80K" → Дискуссия вокруг этих цифр │
│                                                                  │
│   ─────────────────────────────────────────────────────────────  │
│                                                                  │
│   High Anchor ($80K)          Low Anchor ($50K)                 │
│         │                           │                           │
│         ▼                           ▼                           │
│   Итог: ~$65K                  Итог: ~$55K                      │
│                                                                  │
│   Первый anchor сильно влияет на финальный результат            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Когда ставить anchor первым

| Ситуация | Ставь anchor первым? | Причина |
|----------|---------------------|---------|
| У тебя много информации | Да | Можешь обосновать |
| Ты в сильной позиции (BATNA) | Да | Можешь держать anchor |
| Мало информации о другой стороне | Нет | Можешь промахнуться |
| Другая сторона — эксперт в теме | Осторожно | Они распознают нереалистичный anchor |

### Anchor в IT-переговорах

**Salary negotiation:**
```
Вопрос: "Какие ваши ожидания по зарплате?"

Плохо:  "Ну... не знаю... что-нибудь рыночное"
        (отдаёшь anchor другой стороне)

Хорошо: "По моему research, позиции такого уровня в этом
         регионе оплачиваются $120-140K. Учитывая мой опыт
         с [specific skills], я ориентируюсь на верхнюю
         границу этого диапазона."
         (anchor + justification)
```

**Effort estimation:**
```
Вопрос: "Сколько займёт эта фича?"

Плохо:  "Дней 5, наверное..." (weak anchor)

Хорошо: "Похожая задача в прошлом спринте заняла 8 дней.
         Эта чуть проще, но есть интеграция с [X].
         Оцениваю в 6-8 дней + 2 дня на тестирование."
         (anchor с data + buffer)
```

### Защита от чужого anchor

```
ТЕХНИКИ COUNTER-ANCHORING:

1. ПРИЗНАЙ, НО НЕ ПРИНИМАЙ
   "Понимаю откуда эта цифра, но давай посмотрим на данные..."

2. ПЕРЕКЛЮЧИ НА CRITERIA
   "Какие критерии использовались для этой оценки?"

3. RE-ANCHOR
   "По нашим метрикам, реалистичная оценка — X"

4. IGNORE (для явно нереалистичных)
   "Давай отложим цифры и сначала определим scope"
```

---

## Iron Triangle: Scope, Time, Resources

### Суть концепции

В любом проекте три переменные связаны: изменение одной требует изменения других.

```
┌──────────────────────────────────────────────────────────────────┐
│                      IRON TRIANGLE                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        SCOPE                                     │
│                       (Features)                                 │
│                          /\                                      │
│                         /  \                                     │
│                        /    \                                    │
│                       / QUAL \                                   │
│                      /  ITY   \                                  │
│                     /          \                                 │
│                    /            \                                │
│             TIME ───────────────── RESOURCES                     │
│           (Deadline)            (People, Budget)                 │
│                                                                  │
│   ─────────────────────────────────────────────────────────────  │
│                                                                  │
│   ПРАВИЛО: Можно зафиксировать ТОЛЬКО 2 из 3                    │
│                                                                  │
│   Fix Scope + Time    → Resources must flex (more people)       │
│   Fix Scope + Resources → Time must flex (delay)                │
│   Fix Time + Resources  → Scope must flex (cut features)        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Применение в переговорах

**Сценарий: PM хочет всё и сразу**

```
PM: "Нужны все 5 features к пятнице, команда та же."
    (фиксирует все 3 переменные)

Dev (используя Iron Triangle):
    "Давай посмотрим на трейдоффы:

    Если scope (все 5 features) + time (пятница) фиксированы:
    → Нужен ещё один developer или overtime (resources flex)

    Если scope + resources фиксированы:
    → Deadline сдвигается на среду следующей недели (time flex)

    Если time + resources фиксированы:
    → Делаем 3 приоритетных features, 2 — в следующем спринте (scope flex)

    Какой constraint для вас приоритетнее?"
```

Это переводит разговор из "давай просто сделаем" в осознанный tradeoff.

---

## Пошаговый процесс переговоров

### Preparation (до переговоров)

```
PREPARATION CHECKLIST:

1. INTERESTS
   □ Какие МОИ реальные interests? (не позиции)
   □ Какие interests у ДРУГОЙ стороны? (предположения)
   □ Где interests могут совпадать?

2. BATNA
   □ Что я буду делать если договориться не удастся?
   □ Насколько привлекателен мой BATNA?
   □ Могу ли улучшить BATNA до переговоров?

3. ZOPA
   □ Какой мой reservation price (минимум/максимум)?
   □ Какой может быть reservation price другой стороны?
   □ Есть ли потенциальный ZOPA?

4. ANCHOR
   □ Какую первую цифру/предложение озвучить?
   □ Чем могу обосновать anchor (данные, benchmarks)?

5. OPTIONS
   □ Какие варианты кроме бинарного да/нет?
   □ Какие tradeoffs возможны (Iron Triangle)?
```

### Negotiation (во время переговоров)

```
NEGOTIATION FLOW:

1. ОТКРЫТИЕ
   ├── Установи rapport (small talk, common ground)
   ├── Обозначь цель встречи
   └── Подтверди что обе стороны заинтересованы в решении

2. EXPLORATION
   ├── Задавай открытые вопросы об interests
   │   "Что для вас важнее всего в этом проекте?"
   │   "Почему именно этот deadline критичен?"
   ├── Слушай активно (paraphrase, clarify)
   └── Ищи underlying interests за positions

3. GENERATING OPTIONS
   ├── "Какие варианты мы видим?"
   ├── Brainstorm без оценки
   └── Используй Iron Triangle для структурирования

4. EVALUATING OPTIONS
   ├── Используй objective criteria
   ├── Обсуди tradeoffs каждого варианта
   └── Найди вариант в ZOPA

5. CLOSING
   ├── Резюмируй agreement
   ├── Зафиксируй (email, Jira, документ)
   └── Определи next steps
```

### Post-negotiation

```
ПОСЛЕ ПЕРЕГОВОРОВ:

1. ЗАФИКСИРУЙ ПИСЬМЕННО
   ├── Email с summary: "Как я понял, мы договорились о..."
   ├── Обнови Jira/task tracker
   └── Если нужно — formal document

2. РЕФЛЕКСИЯ
   ├── Что сработало?
   ├── Что можно было сделать лучше?
   ├── Какие interests я не учёл?
   └── Как улучшить BATNA на будущее?

3. FOLLOW-THROUGH
   └── Выполни свою часть agreement
```

---

## Скрипты и Templates

### Use Case 1: Deadline Negotiation

**Ситуация:** Нереалистичный deadline от stakeholder

**Скрипт:**
```
1. ACKNOWLEDGE:
   "Понимаю, что [deadline] важен для [причина]."

2. EXPLORE INTERESTS:
   "Помоги мне понять — что критично к этой дате?
    Есть конкретное событие или это желаемый срок?"

3. PRESENT DATA:
   "По нашим метрикам, этот объём работы занимает
    [X дней]. Вот данные из прошлых спринтов."

4. OFFER OPTIONS (Iron Triangle):
   "Вижу три варианта:
    A) Полный scope → [реалистичный deadline]
    B) Сокращённый scope [что именно] → [желаемый deadline]
    C) [Желаемый deadline] + дополнительный ресурс

    Какой приоритет для тебя важнее?"

5. CLOSE:
   "Отлично, договорились на вариант [X].
    Обновлю Jira и пришлю summary email."
```

### Use Case 2: Scope Creep Resistance

**Ситуация:** В середине спринта добавляют новые требования

**Скрипт:**
```
1. ACKNOWLEDGE WITHOUT AGREEING:
   "Вижу что это важно. Давай разберёмся как это влияет
    на текущий план."

2. SHOW IMPACT:
   "Сейчас у нас [X] points committed.
    Это добавляет ещё [Y] points.
    Capacity команды — [Z]."

3. ASK ABOUT PRIORITY:
   "Это более приоритетно чем [текущая задача]?
    Если да — что убираем из спринта?"

4. DOCUMENT:
   "Если берём — нужно пересогласовать sprint commitment
    со всеми stakeholders. Ок?"
```

### Use Case 3: Resource Request

**Ситуация:** Нужен дополнительный ресурс для проекта

**Скрипт:**
```
1. STATE THE PROBLEM (not solution):
   "У нас risk не успеть к [deadline].
    Причина: [конкретно]."

2. PRESENT DATA:
   "Velocity команды — [X] points/sprint.
    Требуется — [Y] points. Gap — [Z]."

3. PROPOSE OPTIONS:
   "Варианты:
    A) Дополнительный developer → укладываемся в срок
    B) Outsource [конкретная часть] → частичное решение
    C) Сдвинуть deadline на [дата]

    Есть ли другие ресурсы которые я не рассматриваю?"

4. SUPPORT WITH BATNA:
   "Если ничего из этого невозможно, альтернатива —
    [что произойдёт, риски]."
```

### Use Case 4: Technical Decision Disagreement

**Ситуация:** Разногласие по архитектурному решению

**Скрипт:**
```
1. SEPARATE PEOPLE FROM PROBLEM:
   "Ценю что у тебя другой взгляд. Давай разберём
    оба подхода по объективным критериям."

2. EXPLORE INTERESTS:
   "Какие для тебя главные concerns?
    Performance? Maintainability? Time to market?"

3. USE OBJECTIVE CRITERIA:
   "Давай оценим оба варианта по:
    • Performance (benchmarks)
    • Development time (estimation)
    • Future maintenance cost
    • Team familiarity"

4. FIND COMMON GROUND:
   "Похоже мы оба хотим [общий interest].
    Может быть компромиссный вариант: [предложение]?"

5. AGREE ON EXPERIMENT:
   "Если не можем договориться сейчас — можем
    spike на 2 дня и сравнить результаты?"
```

### Template: Negotiation Preparation

```
# Negotiation Prep: [Тема]

## 1. Мои Interests
- Interest 1: [почему это важно для меня]
- Interest 2: ...

## 2. Их предполагаемые Interests
- Interest 1: [почему это может быть важно для них]
- Interest 2: ...

## 3. BATNA
- Мой: [что буду делать если не договоримся]
- Их предполагаемый: [что они могут делать]

## 4. ZOPA
- Мой reservation price: [минимум/максимум]
- Их предполагаемый: [оценка]
- Вероятная ZOPA: [диапазон]

## 5. Anchor
- Моё первое предложение: [X]
- Обоснование: [данные, benchmarks]

## 6. Options (варианты)
- A: [вариант + tradeoffs]
- B: [вариант + tradeoffs]
- C: [вариант + tradeoffs]
```

---

## Распространённые ошибки

### Ошибка 1: Positional Bargaining

**Неправильно:**
```
PM: "Нужно к пятнице."
Dev: "Не успеем, только к среде."
PM: "Ну хотя бы к понедельнику!"
Dev: "Ладно, к понедельнику."
```

**Почему это неправильно:**
Торговля позициями без понимания interests. Результат: compromise, не оптимальное решение.

**Правильно:**
Выясни interests ("Почему пятница?"), найди options (partial delivery, reduced scope).

### Ошибка 2: No BATNA

**Неправильно:**
Идти на negotiation без альтернативы.

**Почему это неправильно:**
Без BATNA ты вынужден согласиться на любые условия.

**Правильно:**
Всегда имей план B. Улучшай BATNA до переговоров.

### Ошибка 3: Weak Anchor

**Неправильно:**
"Ну... не знаю, может неделя?" (uncertain anchor)

**Почему это неправильно:**
Weak anchor легко сдвигается. Другая сторона будет давить.

**Правильно:**
"По данным из прошлых проектов, это 7-8 дней. Вот метрики." (anchor + data)

### Ошибка 4: Win-Lose Mindset

**Неправильно:**
"Я должен победить в этих переговорах."

**Почему это неправильно:**
Переговоры — не война. Win-lose создаёт resentment и портит relationships.

**Правильно:**
Ищи win-win. Долгосрочные отношения важнее краткосрочной "победы".

### Ошибка 5: Not Documenting

**Неправильно:**
"Ну вроде договорились..." (устно)

**Почему это неправильно:**
Без документации — разные интерпретации позже. "Но мы же договаривались!"

**Правильно:**
Всегда фиксируй письменно: email summary, Jira update, meeting notes.

---

## Когда использовать

### Используй переговорные техники, когда:

| Ситуация | Какие техники |
|----------|---------------|
| Обсуждение сроков | BATNA, Iron Triangle, Anchoring |
| Scope changes | Interests vs Positions, Iron Triangle |
| Technical disagreement | Objective Criteria, Options generation |
| Salary discussion | BATNA, ZOPA, Anchoring |
| Resource allocation | Interests exploration, Options |
| Vendor negotiation | BATNA, ZOPA, Anchoring |

### НЕ используй переговоры как manipulation:

| Ситуация | Неправильно | Правильно |
|----------|-------------|-----------|
| Deadline | Искусственно завышать estimates | Honest estimates с buffer |
| Salary | Fake competing offer | Real BATNA или honest |
| Technical | Манипулировать данными | Objective criteria |

---

## Практика

### Упражнение 1: BATNA Analysis

**Сценарий:** Ты хочешь работать remote 3 дня в неделю. Компания хочет 5 дней в офисе.

**Задача:** Определи свой BATNA и BATNA компании. Найди ZOPA.

**Эталонный ответ:**
<details><summary>Показать</summary>

**Твой BATNA:**
- Другие offers с remote
- Остаться на текущих условиях
- Freelance

**BATNA компании:**
- Найти другого кандидата (время, деньги)
- Потерять тебя (знания, onboarding нового)
- Продолжить переговоры

**Твой reservation price:** Минимум 2 дня remote
**Их reservation price:** Вероятно готовы на 1-2 дня

**ZOPA:** 1-2 дня remote

**Расширение ZOPA:**
- Trial period: "3 месяца remote, если KPIs — постоянно"
- Hybrid: 2 дня remote + гибкие часы
- Conditional: remote после probation

</details>

### Упражнение 2: Interests vs Positions

**Сценарий:** PM говорит "Эта фича должна быть сделана на React Native, а не native."

**Задача:** Какие могут быть interests за этой position?

**Эталонный ответ:**
<details><summary>Показать</summary>

**Возможные interests PM:**
1. Скорость delivery (RN быстрее для обеих платформ)
2. Бюджет (одна команда вместо двух)
3. Существующие навыки команды (уже знают RN)
4. Time to market pressure
5. Кто-то сказал что "RN — это будущее"

**Как выяснить:**
"Что для тебя главный приоритет в этом решении —
скорость, бюджет, или что-то ещё?"

**Возможные win-win:**
- Если priority = speed: "Native для критичного модуля,
  RN для остального"
- Если priority = budget: "Можем начать с одной платформы"
- Если это dogma: "Давай spike на 3 дня и сравним"

</details>

### Ежедневная практика

| День | Упражнение | Контекст |
|------|------------|----------|
| 1 | Определи BATNA | Перед любым обсуждением сроков |
| 2 | Найди interests | Когда stakeholder что-то требует |
| 3 | Используй anchor | В следующей estimation discussion |
| 4 | Предложи 3 варианта | Вместо бинарного да/нет |
| 5 | Зафиксируй письменно | Любое agreement |

---

## Связанные темы

### Prerequisites (изучить ДО)
- [[active-listening]] — слушать чтобы понять interests

### Эта тема открывает (изучить ПОСЛЕ)
- [[salary-negotiation]] — специализация для career
- [[stakeholder-negotiation]] — работа с руководством

### Связанные навыки
- [[conflict-resolution]] — когда negotiation переходит в конфликт
- [[saying-no]] — как отказывать без ущерба для отношений

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [BATNA and ZOPA - Harvard PON](https://www.pon.harvard.edu/daily/business-negotiations/how-to-find-the-zopa-in-business-negotiations/) | Article | BATNA/ZOPA fundamentals |
| 2 | [Principled Negotiation - Harvard PON](https://www.pon.harvard.edu/daily/negotiation-skills-daily/principled-negotiation-focus-interests-create-value/) | Article | Harvard method, 4 principles |
| 3 | [Getting to Yes - Wikipedia](https://en.wikipedia.org/wiki/Getting_to_Yes) | Reference | Fisher & Ury original framework |
| 4 | [Anchoring in Negotiation - PON](https://www.pon.harvard.edu/daily/negotiation-skills-daily/what-is-anchoring-in-negotiation/) | Article | Anchoring effect, techniques |
| 5 | [Anchoring Strategies - Red Bear](https://www.redbearnegotiation.com/blog/set-high-expectations-with-anchoring) | Article | Practical anchoring techniques |
| 6 | [Project Negotiation - APM](https://www.apm.org.uk/blog/how-to-successfully-negotiate-in-any-project/) | Article | IT project context |
| 7 | [Stakeholder Management - PMI](https://www.pmi.org/learning/library/negotiating-project-outcomes-develop-skills-6781) | Article | Stakeholder negotiation |
| 8 | [Understanding ZOPA - HBS](https://online.hbs.edu/blog/post/understanding-zopa) | Article | ZOPA deep dive |

*Исследование проведено: 2026-01-18*

---

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
