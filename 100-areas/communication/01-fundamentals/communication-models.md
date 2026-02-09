---
title: "Модели коммуникации"
created: 2026-01-18
updated: 2026-01-18
type: deep-dive
status: complete
difficulty: beginner
prerequisites: []
teaches:
  - Shannon-Weaver model
  - Transactional model
  - SMCR model
  - Types of noise
unlocks:
  - [[communication-barriers]]
  - [[active-listening]]
  - [[giving-feedback]]
tags: [communication, theory, models, fundamentals]
---

# Модели коммуникации

> **TL;DR:** Коммуникация — не передача информации, а совместное создание смысла. Линейные модели (Shannon-Weaver) объясняют что может пойти не так. Транзакционные модели (Barnlund) показывают как коммуникация работает на самом деле. Понимание моделей = диагностика проблем коммуникации.

---

## Зачем это нужно?

### Представьте ситуацию

**Technical discussion.** Senior Developer объясняет архитектурное решение Junior'у.

**Без понимания моделей:**
```
Senior: "Давай использовать event-driven архитектуру с message broker."
Junior: "Окей." (кивает)
...через неделю...
Junior реализовал REST polling вместо pub/sub.
```

**Проблема:** Senior думал что передал информацию. Junior думал что понял. Никто не проверил.

**С пониманием моделей:**
```
Senior: "Давай использовать event-driven архитектуру с message broker."
        [Распознаёт: потенциальный semantic noise — термины могут быть незнакомы]
Senior: "Ты работал с Kafka или RabbitMQ раньше?"
Junior: "Нет, только REST API."
Senior: "Понял. Event-driven — это когда сервисы общаются через события,
        а не через прямые вызовы. Похоже на подписку на YouTube:
        ты не проверяешь канал каждую минуту, а получаешь уведомление."
Junior: "То есть вместо polling будет push-notification для сервисов?"
Senior: "Именно!"
```

**Результат:** Понимание достигнуто через проверку и адаптацию сообщения.

### Проблема в числах

```
┌──────────────────────────────────────────────────────────────────┐
│                 КОММУНИКАЦИЯ: СТАТИСТИКА                        │
├──────────────────────────────────────────────────────────────────┤
│  50%           Того, что говорится, реально слышится            │
│  услышано      (Harvard Business School research)                │
├──────────────────────────────────────────────────────────────────┤
│  60-80%        Времени Senior+ тратят на коммуникацию           │
│  времени       (не на код)                                       │
├──────────────────────────────────────────────────────────────────┤
│  75%           Проблем на работе — коммуникационные             │
│  проблем       (Project Management Institute)                    │
├──────────────────────────────────────────────────────────────────┤
│  $359B         Ежегодно — стоимость конфликтов в США            │
│  потерь        (CPP Global Human Capital Report)                 │
├──────────────────────────────────────────────────────────────────┤
│  83%           Конфликтов происходят от недопонимания           │
│  конфликтов    (не от реальных разногласий)                     │
└──────────────────────────────────────────────────────────────────┘
```

**Вывод:** Проблемы коммуникации — не от "сложных людей", а от непонимания механики процесса.

---

## Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | Необходим | Понять почему тебя не понимают (и ты не понимаешь) |
| **Middle** | Необходим | Cross-team communication требует осознанности |
| **Senior** | Критичен | Диагностика проблем в команде |
| **Tech Lead** | Критичен | Основа для всех остальных навыков |

---

## Терминология

| Термин | Что это (простыми словами) | IT-аналогия |
|--------|---------------------------|-------------|
| **Sender** | Тот, кто инициирует сообщение | Client в client-server |
| **Receiver** | Тот, кто получает сообщение | Server в client-server |
| **Encoding** | Превращение мысли в слова/жесты | Serialization (JSON.stringify) |
| **Decoding** | Превращение слов обратно в смысл | Deserialization (JSON.parse) |
| **Channel** | Среда передачи (речь, email, Slack) | Transport layer (HTTP, WebSocket) |
| **Noise** | Любые помехи в передаче | Packet loss, corruption |
| **Feedback** | Ответная реакция получателя | Response в request-response |
| **Context** | Окружение и обстоятельства | Environment variables |

---

## Как это работает?

### Эволюция моделей коммуникации

```
1948: Shannon-Weaver          1960: Berlo SMCR          1970: Barnlund
     (Linear)                     (Linear+)               (Transactional)

┌───┐    ┌───┐    ┌───┐      S ──► M ──► C ──► R       ┌──────────────┐
│ S │───►│ C │───►│ R │                                 │ Person A ◄──►│
└───┘    └───┘    └───┘      + skills                  │              │
  ▲        │                 + attitudes               │ Person B ◄──►│
  │        ▼                 + knowledge               │              │
  │     [noise]              + social context          │ Simultaneous │
  │                                                    │ encoding/    │
Односторонняя           Учитывает                      │ decoding     │
передача                характеристики                 └──────────────┘
                        участников
                                                       Двусторонний
                                                       процесс
```

---

## Модель 1: Shannon-Weaver (1948)

### Суть модели

Изначально создана для телефонной связи (Bell Labs). Объясняет коммуникацию как **передачу сигнала** от источника к получателю.

```
┌──────────────────────────────────────────────────────────────────┐
│                   SHANNON-WEAVER MODEL                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────┐    ┌───────────┐    ┌─────────┐    ┌──────────┐   │
│   │ Source │───►│Transmitter│───►│ Channel │───►│ Receiver │   │
│   │        │    │ (Encoder) │    │         │    │(Decoder) │   │
│   └────────┘    └───────────┘    └────┬────┘    └──────────┘   │
│                                       │                         │
│                                       ▼                         │
│                                   [ NOISE ]                     │
│                                                                  │
│   "Идея"     "Слова/текст"      "Речь/email"   "Интерпретация" │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Компоненты

| Компонент | Описание | IT-пример |
|-----------|----------|-----------|
| **Source** | Инициатор сообщения | Developer пишет PR description |
| **Transmitter** | Кодирует идею в сигнал | Формулирует мысли в текст |
| **Channel** | Среда передачи | GitHub PR, Slack, email |
| **Receiver** | Декодирует сигнал | Reviewer читает description |
| **Destination** | Конечный получатель смысла | Reviewer понимает что менялось |
| **Noise** | Помехи в передаче | Jargon, многозадачность, контекст |

### Применение в IT

**Сценарий: Код review comment**

```
Source:      Reviewer хочет указать на проблему с производительностью
Encoding:    "This could be optimized with caching"
Channel:     GitHub comment
Decoding:    Author читает комментарий
Noise:       Author не знает какой тип caching имеется в виду
Destination: Author может понять как угодно (Redis? Memoization? CDN?)
```

**Диагностика:** Если author реализовал не то — noise в semantic layer.

### Ограничения модели

```
ОГРАНИЧЕНИЯ SHANNON-WEAVER:

1. ЛИНЕЙНОСТЬ
   ┌───┐ ──────────────► ┌───┐
   │ S │   (нет feedback) │ R │
   └───┘                   └───┘

   Реальность: коммуникация двусторонняя

2. ПАССИВНЫЙ RECEIVER
   Receiver просто "принимает"

   Реальность: receiver активно интерпретирует

3. ИГНОРИРОВАНИЕ КОНТЕКСТА
   Не учитывает отношения, историю, культуру

   Реальность: контекст определяет смысл

4. ONE-TO-ONE FOCUS
   Не работает для групповой коммуникации

   Реальность: митинги, каналы, broadcasts
```

### Когда модель полезна

| Ситуация | Применение |
|----------|------------|
| Email не дошёл | Проверь channel (spam, wrong address) |
| Инструкция непонятна | Проверь encoding (слишком сложно?) |
| Коллега понял неправильно | Проверь noise (jargon? assumptions?) |

---

## Модель 2: Berlo SMCR (1960)

### Суть модели

Расширяет Shannon-Weaver, добавляя **характеристики участников**. Коммуникация успешна когда sender и receiver "на одном уровне".

```
┌──────────────────────────────────────────────────────────────────┐
│                        BERLO SMCR MODEL                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SOURCE          MESSAGE         CHANNEL         RECEIVER       │
│   ┌─────┐         ┌─────┐         ┌─────┐         ┌─────┐       │
│   │Skills│         │Content│       │Seeing│        │Skills│      │
│   │Attit.│ ──────► │Struct.│ ────► │Hearing│ ───► │Attit.│      │
│   │Knowl.│         │Code   │       │Touch │        │Knowl.│      │
│   │Soc.  │         │Treat. │       │Smell │        │Soc.  │      │
│   │Cult. │         │Elem.  │       │Taste │        │Cult. │      │
│   └─────┘         └─────┘         └─────┘         └─────┘       │
│                                                                  │
│    Кто            Что             Как             Кому           │
│    говорит        говорит         передаётся      говорит        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Компоненты Source/Receiver

| Фактор | Описание | IT-контекст |
|--------|----------|-------------|
| **Skills** | Навыки говорения, слушания, письма | Технический writing, презентации |
| **Attitudes** | Отношение к теме, себе, получателю | Отношение к legacy code, к team |
| **Knowledge** | Знания по теме | Domain expertise, tech stack |
| **Social System** | Социальные нормы, иерархия | Startup vs Enterprise culture |
| **Culture** | Культурный контекст | Remote vs office, US vs EU |

### Компоненты Message

| Элемент | Описание | Пример |
|---------|----------|--------|
| **Content** | Само содержание | "Нужен рефакторинг" |
| **Structure** | Организация информации | Проблема → Причина → Решение |
| **Code** | Язык, символы | Технический жаргон vs plain language |
| **Treatment** | Стиль подачи | Формальный vs casual |
| **Elements** | Невербальные элементы | Tone в тексте, emoji |

### Применение в IT

**Сценарий: Объяснение архитектуры Junior'у**

```
SOURCE (Senior):
├── Skills: Высокие технические, средние presentation
├── Knowledge: Глубокое понимание системы
├── Attitude: Нетерпеливость (хочет быстро объяснить)
└── Social: Старший по позиции

MESSAGE:
├── Content: Микросервисная архитектура
├── Code: Технический жаргон (CQRS, event sourcing)
├── Structure: Начинает с деталей, не с overview
└── Treatment: Формальный, dense

CHANNEL: Zoom call без screen sharing

RECEIVER (Junior):
├── Skills: Базовые, учится
├── Knowledge: Только monolith опыт
├── Attitude: Боится показаться глупым
└── Social: Младший, не задаёт вопросы

РЕЗУЛЬТАТ: Miscommunication
```

**Диагностика по SMCR:**
- Knowledge gap: Senior знает больше → нужен bridging
- Code mismatch: Jargon непонятен → упростить
- Social barrier: Иерархия мешает вопросам → создать safe space

### Ключевой принцип SMCR

> **"Для эффективной коммуникации Source и Receiver должны быть на одном уровне."**

Это не значит "одинаковые знания". Это значит:
- Sender адаптирует message под receiver
- Sender проверяет понимание
- Sender выбирает правильный channel и code

---

## Модель 3: Barnlund Transactional (1970)

### Суть модели

Коммуникация — не передача информации, а **совместное создание смысла**. Оба участника одновременно являются и sender, и receiver.

```
┌──────────────────────────────────────────────────────────────────┐
│                 BARNLUND TRANSACTIONAL MODEL                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│        ┌─────────────────────────────────────────────┐          │
│        │          SHARED FIELD OF EXPERIENCE         │          │
│        │  ┌─────────────────────────────────────┐   │          │
│        │  │                                     │   │          │
│        │  │   Person A         Person B         │   │          │
│        │  │   ┌─────┐         ┌─────┐          │   │          │
│        │  │   │Encode│ ◄─────► │Encode│         │   │          │
│        │  │   │Decode│         │Decode│         │   │          │
│        │  │   └─────┘         └─────┘          │   │          │
│        │  │      ▲                ▲             │   │          │
│        │  │      │   FEEDBACK     │             │   │          │
│        │  │      └────────────────┘             │   │          │
│        │  │                                     │   │          │
│        │  └─────────────────────────────────────┘   │          │
│        │                                             │          │
│        │   Private      Public       Private         │          │
│        │   Cues A       Cues         Cues B          │          │
│        └─────────────────────────────────────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Ключевые концепции

**1. Simultaneous Encoding/Decoding**
```
Пока ты говоришь, ты уже:
├── Наблюдаешь реакцию собеседника
├── Интерпретируешь его невербальные сигналы
├── Корректируешь своё сообщение в реальном времени
└── Декодируешь его feedback
```

**2. Типы cues (сигналов)**

| Тип | Описание | IT-пример |
|-----|----------|-----------|
| **Public Cues** | Общая среда, видимая обоим | Офис, Zoom background, канал Slack |
| **Private Cues** | Личный опыт, мысли, эмоции | Прошлый опыт с legacy, настроение |
| **Behavioral Cues** | Вербальное и невербальное поведение | Тон голоса, скорость печати, emoji |

**3. Field of Experience**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Person A's          SHARED           Person B's   │
│   Experience         EXPERIENCE        Experience   │
│   ┌────────┐        ┌────────┐       ┌────────┐   │
│   │        │        │        │       │        │   │
│   │ Unique │        │ Common │       │ Unique │   │
│   │        │◄──────►│ Ground │◄─────►│        │   │
│   │        │        │        │       │        │   │
│   └────────┘        └────────┘       └────────┘   │
│                          ▲                         │
│                          │                         │
│              Коммуникация возможна                 │
│              только в пересечении                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Применение в IT

**Сценарий: 1-on-1 с Tech Lead**

```
ОДНОВРЕМЕННО ПРОИСХОДИТ:

Developer (Person A):
├── Encoding: Объясняет причину delay
├── Decoding: Наблюдает реакцию Tech Lead
├── Private cues: "Боюсь что подумает что я плохой специалист"
└── Adjustment: Видит нахмуренные брови → добавляет контекст

Tech Lead (Person B):
├── Encoding: Кивает, говорит "понятно"
├── Decoding: Слушает объяснение, оценивает
├── Private cues: "Опять scope creep? Или реальная проблема?"
└── Adjustment: Понимает что developer напряжён → смягчает тон

Public cues: Zoom call, камеры включены, 1-on-1 setting
Shared experience: Оба знают проект, работали вместе 6 месяцев
```

**Ключевой вывод:** Коммуникация — не "я сказал, он услышал". Это динамический процесс где оба участника влияют друг на друга в реальном времени.

### Практические выводы из транзакционной модели

1. **Следи за feedback в реальном времени**
   - Выражение лица
   - Паузы в ответе
   - Уточняющие вопросы (или их отсутствие)

2. **Расширяй shared field of experience**
   - Уточни контекст: "Ты работал с Redis раньше?"
   - Используй общие reference points: "Помнишь как мы делали X?"

3. **Осознавай свои private cues**
   - Твоё настроение влияет на encoding
   - Твои assumptions влияют на decoding

---

## Noise: Типы помех в коммуникации

### Классификация noise

```
┌──────────────────────────────────────────────────────────────────┐
│                       TYPES OF NOISE                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   EXTERNAL (снаружи)              INTERNAL (внутри)              │
│   ┌─────────────────┐            ┌─────────────────┐            │
│   │ PHYSICAL        │            │ PSYCHOLOGICAL   │            │
│   │ • Background    │            │ • Bias          │            │
│   │   noise         │            │ • Stress        │            │
│   │ • Bad audio     │            │ • Preconceptions│            │
│   │ • Visual        │            │ • Emotions      │            │
│   │   distractions  │            │ • Wandering     │            │
│   └─────────────────┘            │   thoughts      │            │
│                                  └─────────────────┘            │
│   ┌─────────────────┐            ┌─────────────────┐            │
│   │ SEMANTIC        │            │ PHYSIOLOGICAL   │            │
│   │ • Jargon        │            │ • Fatigue       │            │
│   │ • Ambiguous     │            │ • Hunger        │            │
│   │   words         │            │ • Headache      │            │
│   │ • Cultural      │            │ • Illness       │            │
│   │   differences   │            │                 │            │
│   └─────────────────┘            └─────────────────┘            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Physical Noise

**Определение:** Внешние звуки и визуальные отвлечения.

| Пример | IT-контекст | Решение |
|--------|-------------|---------|
| Фоновый шум | Open office разговоры | Headphones, quiet room |
| Плохой звук | Zoom с плохим микрофоном | Попросить включить нормальный mic |
| Визуальные отвлечения | Slack notifications во время call | Включить DND mode |
| Многозадачность | Проверка email во время meeting | Закрыть другие tabs |

### Semantic Noise

**Определение:** Непонимание значения слов.

| Пример | IT-контекст | Решение |
|--------|-------------|---------|
| Технический jargon | "Используй CQRS" — Junior не знает | Объясни термин или используй аналогию |
| Ambiguous words | "Скоро" = завтра или через месяц? | Конкретизируй: "к пятнице" |
| Acronyms | "Отправь в SRE" — новичок не знает | Расшифровывай при первом использовании |
| Cultural idioms | "Let's table this" (US vs UK meaning) | Избегай idioms в cross-cultural |

**IT-специфичный semantic noise:**
```
СЛОВО           ЗНАЧЕНИЯ
────────────────────────────────────────────────
"Deploy"        → to staging? to production? manual? automated?
"Fix"           → workaround? proper fix? hotfix?
"Soon"          → today? this week? this quarter?
"Simple"        → 1 hour? 1 day? 1 sprint?
"Refactor"      → rename? restructure? rewrite?
"Done"          → code done? tested? deployed? monitored?
```

### Psychological Noise

**Определение:** Внутренние отвлечения: bias, стресс, эмоции.

| Пример | IT-контекст | Решение |
|--------|-------------|---------|
| Preconceptions | "Этот человек всегда критикует" | Слушай содержание, не source |
| Stress | Deadline pressure во время discussion | Осознай влияние на восприятие |
| Defensiveness | "Мой код критикуют = меня критикуют" | Разделяй работу и личность |
| Mind wandering | Думаю о другой задаче во время meeting | Active listening techniques |

### Physiological Noise

**Определение:** Физическое состояние тела влияет на восприятие.

| Пример | IT-контекст | Решение |
|--------|-------------|---------|
| Fatigue | 8-часовой coding → meeting | Перерыв перед важным разговором |
| Hunger | Голодный на 11am standup | Перекус перед важными discussions |
| Headache | Мигрень во время code review | Перенеси если возможно |
| Timezone | 2am call = пониженное внимание | Распределяй timezone burden |

---

## Пошаговый процесс: Применение моделей

### Диагностика проблемы коммуникации

**Когда коммуникация не удалась, пройди чеклист:**

```
CHECKLIST: ЧТО ПОШЛО НЕ ТАК?

1. CHANNEL (Shannon-Weaver)
   □ Правильный ли канал выбран?
   □ Сообщение дошло физически?
   □ Качество канала достаточное?

2. NOISE (все модели)
   □ Physical: были отвлечения?
   □ Semantic: jargon понятен?
   □ Psychological: был bias?
   □ Physiological: физическое состояние?

3. ENCODING (SMCR)
   □ Message достаточно clear?
   □ Structure логичная?
   □ Code (язык) подходящий для receiver?

4. RECEIVER FACTORS (SMCR)
   □ Knowledge достаточное?
   □ Attitude не блокирующий?
   □ Skills для декодирования?

5. SHARED EXPERIENCE (Barnlund)
   □ Достаточно common ground?
   □ Feedback был получен и использован?
   □ Adjustment происходил?
```

### Пример диагностики

**Ситуация:** PR merged с багом, хотя reviewer "одобрил".

```
ДИАГНОСТИКА:

Channel:
✓ GitHub PR — правильный канал для code review

Noise:
✗ Reviewer делал review в пятницу вечером (physiological: fatigue)
✗ 15 files changed — cognitive overload (psychological)
✗ Complex diff без context (semantic)

Encoding:
✗ PR description был "Fixed bug" — недостаточно контекста
✗ Нет summary что изменено и почему

Receiver Factors:
✗ Reviewer не знаком с этим модулем (knowledge gap)
? Attitude: возможно "доверяю автору" без deep review

Shared Experience:
✗ Автор не указал на critical sections
✗ Feedback loop не включал вопросы

ВЫВОД: Проблема в encoding + noise + knowledge gap
РЕШЕНИЕ: Лучше PR descriptions, smaller PRs, указывать focus areas
```

---

## Скрипты и Templates

### Use Case 1: Объяснение сложной концепции

**Ситуация:** Нужно объяснить архитектурное решение Junior'у

**Скрипт (применяет SMCR):**
```
1. CALIBRATE (проверь knowledge gap):
   "Ты раньше работал с [технология]?"

2. BRIDGE (создай общую базу):
   "Это похоже на [известная концепция], только..."

3. STRUCTURE (от simple к complex):
   "Начну с high-level: [overview]"
   "Теперь детали: [specifics]"

4. CHECK (получи feedback):
   "Как это соотносится с тем что ты знаешь?"
   "Что пока непонятно?"
```

### Use Case 2: Важное сообщение в async

**Ситуация:** Нужно сообщить о critical change всей команде

**Template (минимизирует noise):**
```
Subject: [ACTION REQUIRED] [Краткая суть]

TL;DR: [одно предложение — что изменилось и что делать]

Что изменилось:
• [пункт 1]
• [пункт 2]

Что нужно сделать:
• [конкретное действие 1] — до [дедлайн]
• [конкретное действие 2] — до [дедлайн]

Почему это важно:
[1-2 предложения]

Вопросы?
[Куда обращаться]
```

### Use Case 3: Уточнение непонятного требования

**Ситуация:** Stakeholder дал расплывчатое требование

**Скрипт (применяет transactional model):**
```
1. PARAPHRASE (проверь своё decoding):
   "Если я правильно понял, вы хотите..."

2. CONCRETE (устрани semantic noise):
   "Когда вы говорите 'быстро', это значит..."
   "Под 'пользователями' вы имеете в виду..."

3. EDGE CASES (расширь shared field):
   "А что должно происходить если..."

4. CONFIRM:
   "То есть acceptance criteria будут: ..."
```

---

## Распространённые ошибки

### Ошибка 1: Transmission Fallacy

**Неправильно:**
"Я же сказал! Почему ты не понял?"

**Почему это неправильно:**
Линейная модель (Shannon-Weaver) — это упрощение. Реальность: receiver активно интерпретирует. То что ты "передал" ≠ то что он "получил".

**Правильно:**
"Расскажи как ты понял задачу — хочу убедиться что мы на одной волне."

### Ошибка 2: Ignoring Context

**Неправильно:**
Одинаковое объяснение для Junior и Senior.

**Почему это неправильно:**
SMCR модель: receiver factors (knowledge, skills) влияют на decoding. Один message не подходит для разных receivers.

**Правильно:**
Калибруй message под receiver: "Ты работал с X раньше?"

### Ошибка 3: Assuming Shared Experience

**Неправильно:**
Использовать team-specific jargon с новичком.

**Почему это неправильно:**
Barnlund: коммуникация возможна только в shared field of experience. Без общего контекста — semantic noise.

**Правильно:**
Расшифровывай acronyms, объясняй local conventions.

### Ошибка 4: Ignoring Feedback

**Неправильно:**
Говорить монологом, не проверяя понимание.

**Почему это неправильно:**
Transactional model: feedback — это не опция, а часть процесса. Без feedback loop — коммуникация односторонняя.

**Правильно:**
Pause for questions, check understanding, watch non-verbal cues.

### Ошибка 5: Blaming Receiver

**Неправильно:**
"Он просто не слушает."

**Почему это неправильно:**
Responsibility за communication лежит на обоих. Sender отвечает за encoding, выбор channel, минимизацию noise.

**Правильно:**
"Что я могу изменить в своём сообщении?"

---

## Когда использовать

### Используй знание моделей, когда:

| Ситуация | Какая модель | Как применить |
|----------|--------------|---------------|
| Важное сообщение не дошло | Shannon-Weaver | Проверь channel и noise |
| Коллега понял неправильно | SMCR | Проверь knowledge gap |
| Долгое обсуждение без прогресса | Barnlund | Проверь shared field |
| Новый человек в команде | SMCR | Calibrate к его уровню |
| Cross-cultural communication | Все три | Maximum осознанность |

### НЕ используй как excuse:

| Ситуация | Неправильно | Правильно |
|----------|-------------|-----------|
| Ошибка в коммуникации | "Это semantic noise" | Исправь message |
| Непонимание | "У нас разный field of experience" | Расширь common ground |
| Конфликт | "Это psychological noise" | Разберись с root cause |

---

## Практика

### Упражнение 1: Диагностика по модели

**Сценарий:** Ты отправил PR description. Reviewer задал 5 уточняющих вопросов.

**Задача:** Используя модели, определи что пошло не так.

**Эталонный ответ:**
<details><summary>Показать</summary>

**Возможные причины по моделям:**

Shannon-Weaver:
- Channel правильный (GitHub)
- Но noise: возможно PR слишком большой

SMCR:
- Encoding: description недостаточно detailed
- Code: возможно jargon без объяснения
- Receiver knowledge: reviewer не знаком с контекстом

Barnlund:
- Недостаточно shared context в description
- Нет pre-alignment перед PR

**Решение:**
1. Более детальный PR description (encoding)
2. Link на design doc / ticket (shared context)
3. Highlight critical sections (reduce noise)
4. Pre-review sync для complex PRs (expand shared field)

</details>

### Упражнение 2: Адаптация message

**Задача:** Объясни "микросервисная архитектура" для:
1. Junior без опыта
2. PM без технического background
3. Senior из monolith background

**Эталонный ответ:**
<details><summary>Показать</summary>

**Для Junior:**
```
"Представь что приложение — это компания. В монолите — все в одном
офисе, один бюджет, один начальник. В микросервисах — много маленьких
команд, каждая со своим бюджетом и ответственностью. Они общаются
через официальные каналы (API), а не крича через open space."
```

**Для PM:**
```
"Микросервисы позволяют командам работать независимо. Это значит:
- Быстрее релизы (каждая команда деплоит отдельно)
- Легче масштабировать (только нужные части)
- Но: сложнее координация (больше движущихся частей)"
```

**Для Senior (monolith):**
```
"Вместо одного deployable unit — много. Каждый сервис:
- Свой repo, CI/CD, database
- Общение через API/events
- Независимый scaling и deployment

Tradeoffs: distributed systems complexity (network calls, eventual
consistency) vs deployment flexibility и team autonomy."
```

</details>

### Ежедневная практика

| День | Упражнение | Контекст |
|------|------------|----------|
| 1 | Замечай noise | Что отвлекало на митингах? |
| 2 | Check encoding | Перечитай свои messages — понятны ли? |
| 3 | Calibrate receiver | Спроси о background перед объяснением |
| 4 | Get feedback | "Как ты понял?" после важного сообщения |
| 5 | Diagnose failure | Когда miscommunication — что по модели? |

---

## Связанные темы

### Prerequisites (изучить ДО)
- Отсутствуют — это фундаментальный материал

### Эта тема открывает (изучить ПОСЛЕ)
- [[communication-barriers]] — детально о барьерах и их преодолении
- [[active-listening]] — практические навыки слушания
- [[giving-feedback]] — применение моделей к feedback

### Связанные навыки
- [[communication-styles]] — DISC и другие модели стилей общения

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [Shannon-Weaver Model - HumanFocus](https://humanfocus.co.uk/blog/the-shannon-and-weaver-model-of-communication-at-work/) | Article | Model explanation, workplace application |
| 2 | [Transactional Models - Pumble](https://pumble.com/learn/communication/transactional-models-of-communication/) | Article | Barnlund model details |
| 3 | [Berlo SMCR Model - Toolshero](https://www.toolshero.com/communication-methods/berlos-smcr-model-of-communication/) | Article | SMCR components |
| 4 | [Communication Noise - Wikipedia](https://en.wikipedia.org/wiki/Communication_noise) | Reference | Noise types classification |
| 5 | [8 Communication Models - Slack](https://slack.com/blog/collaboration/communication-model) | Article | Models comparison, 2024 practices |
| 6 | [Noise in Communication - Prezent.ai](https://www.prezent.ai/blog/noise-in-communication) | Article | Noise types and examples |
| 7 | [Shannon-Weaver - CommunicationTheory.org](https://www.communicationtheory.org/shannon-and-weaver-model-of-communication/) | Article | Original model history |
| 8 | [Barnlund Model - Wikipedia](https://en.wikipedia.org/wiki/Barnlund's_model_of_communication) | Reference | Transactional model details |

*Исследование проведено: 2026-01-18*

---

*Последнее обновление: 2026-01-18*
*Шаблон: [[_meta/template-communication]]*
