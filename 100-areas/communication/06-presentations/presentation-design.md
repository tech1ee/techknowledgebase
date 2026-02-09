# Presentation Design: Структура и визуальный дизайн презентаций

## TL;DR

Эффективная презентация = **Пирамида Минто** (главное вперёд) + **правило 10-20-30** (слайды-минуты-шрифт) + **один слайд = одна идея**. Аудитория запоминает 10% услышанного, но 65% увиденного — визуальный дизайн критичен.

---

## Зачем это нужно

**Статистика:**
- 91% презентаторов чувствуют себя увереннее с хорошо структурированной презентацией (Prezi, 2024)
- Аудитория формирует мнение о презентации за первые **7 секунд** (Princeton research)
- 79% слушателей считают слайды "перегруженными текстом" главной проблемой (Duarte, 2024)
- Презентации с визуальными элементами на **43% более убедительны** (3M Corporation)

**Проблема в IT:**
```
ТИПИЧНЫЙ ANTI-PATTERN:
┌─────────────────────────────────────┐
│ Слайд 1: "Архитектура системы"      │
│ • 47 bullet points                  │
│ • Шрифт 10pt                        │
│ • Диаграмма на весь экран           │
│ • Все детали сразу                  │
│                                     │
│ Результат: Cognitive overload       │
│ Аудитория: 😵 *листает телефон*     │
└─────────────────────────────────────┘
```

**Реальность:**
- Tech talk на 45 минут требует **20-30 часов** подготовки
- Demo падает в 40% случаев (Murphy's Law)
- Stakeholder'ы принимают решения на 5-м слайде, а не на 45-м

---

## Для кого этот материал

| Уровень | Зачем нужно | Фокус |
|---------|-------------|-------|
| **Junior** | Sprint demo, tech talks | Базовая структура |
| **Middle** | Architecture reviews, proposals | Storytelling |
| **Senior** | C-level presentations, conferences | Influence & persuasion |
| **Lead/Manager** | Board presentations, strategy | Executive communication |

---

## Ключевые термины

| Термин | Определение | IT-аналогия |
|--------|-------------|-------------|
| **Minto Pyramid** | Структура "главное вперёд": вывод → аргументы → данные | `return result;` в начале функции, потом логика |
| **SCQA** | Situation-Complication-Question-Answer — framework для intro | Try-catch-finally для внимания аудитории |
| **Signposting** | Навигационные фразы ("Во-первых...", "Переходим к...") | Comments и section headers в коде |
| **Assertion-Evidence** | Слайд = утверждение (заголовок) + доказательство (визуал) | Test name + assertion |
| **Progressive disclosure** | Постепенное раскрытие информации | Lazy loading для внимания |

---

## Пирамида Минто (Minto Pyramid Principle)

### Происхождение

Barbara Minto, McKinsey, 1960-е. Золотой стандарт для business communication.

### Принцип

```
              ┌─────────────┐
              │  ВЫВОД      │  ← Начинай с ответа
              │  (So what?) │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │Аргумент│  │Аргумент│  │Аргумент│  ← Почему?
   │   1    │  │   2    │  │   3    │
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
   ┌────┴────┐  ┌────┴────┐  ┌────┴────┐
   │Факты    │  │Факты    │  │Факты    │  ← Доказательства
   └─────────┘  └─────────┘  └─────────┘
```

### Почему это работает

**Когнитивная наука:**
- Рабочая память = 4±1 элементов (Miller's Law)
- Primacy effect: первое запоминается лучше
- Busy executives читают только первый абзац

### Анти-паттерн vs Minto

**❌ Bottom-up (как обычно делают):**
```
Слайд 1:  "История проекта"
Слайд 2:  "Что мы исследовали"
Слайд 3:  "Технические детали"
...
Слайд 25: "Наконец-то, вывод"

Проблема: CEO ушёл на слайде 5
```

**✅ Minto (top-down):**
```
Слайд 1:  "Нам нужен Kubernetes — это сэкономит $200K/год"
Слайд 2:  "3 причины: масштабирование, reliability, cost"
Слайд 3:  "Причина 1: текущая система не масштабируется"
...

Преимущество: Даже если остановят на слайде 3,
              главное уже сказано
```

---

## SCQA Framework для вступления

### Структура

| Элемент | Что это | Пример |
|---------|---------|--------|
| **S**ituation | Контекст, который аудитория знает | "Наш сервис обрабатывает 1M запросов в день" |
| **C**omplication | Проблема, вызов | "Но латенси выросла с 50ms до 500ms" |
| **Q**uestion | Вопрос, который возникает | "Как вернуть performance?" |
| **A**nswer | Ваше решение (тезис презентации) | "Нужно перейти на event-driven архитектуру" |

### Пример для Architecture Review

```
SITUATION:
"Наш e-commerce backend написан на монолите 5 лет назад.
 Он стабилен и команда его знает."

COMPLICATION:
"Но Black Friday показал: при 10x нагрузке checkout падает.
 Потеряли $2M за 4 часа даунтайма."

QUESTION:
"Как обеспечить масштабируемость к следующему Black Friday?"

ANSWER:
"Предлагаю выделить checkout в отдельный микросервис.
 ROI — 6 месяцев при $2M потенциальных потерь."
```

### Timing

SCQA должен занимать **первые 2-3 минуты** (или 2-3 слайда).

---

## Структура презентации

### Правило 10-20-30 (Guy Kawasaki)

| Параметр | Значение | Почему |
|----------|----------|--------|
| **10** слайдов | Максимум для pitch | Больше = потеря фокуса |
| **20** минут | Максимум для презентации | Attention span ~18 минут |
| **30** pt шрифт | Минимум размер | Если не влезает — слишком много текста |

### Универсальная структура (для tech talk)

```
OPENING (10% времени)
├── Hook — зацепить внимание
├── SCQA — контекст и тезис
└── Agenda — что будет (3-4 пункта)

BODY (80% времени)
├── Section 1 + evidence
├── Section 2 + evidence
├── Section 3 + evidence
└── [Demo если есть]

CLOSING (10% времени)
├── Summary — повторить ключевые points
├── Call to action — что делать дальше
└── Q&A setup
```

### Структура для разных форматов

| Формат | Время | Слайдов | Структура |
|--------|-------|---------|-----------|
| **Sprint Demo** | 5-10 мин | 3-5 | What → Demo → Feedback |
| **Tech Talk** | 30-45 мин | 15-25 | SCQA → 3 sections → Summary |
| **Architecture Review** | 60 мин | 20-30 | Context → Options → Recommendation → Discussion |
| **Executive Update** | 15 мин | 5-7 | Status → Risks → Ask |
| **Conference Talk** | 45 мин | 30-40 | Story → Problem → Solution → Lessons |

---

## Дизайн слайдов

### Принцип Assertion-Evidence

**Традиционный слайд:**
```
┌──────────────────────────────────────┐
│ Performance Optimization             │ ← Тема (бессмысленно)
├──────────────────────────────────────┤
│ • We analyzed the system             │
│ • Found 3 bottlenecks                │
│ • Implemented caching                │
│ • Results improved                   │
│ • More details on next slide         │
└──────────────────────────────────────┘
```

**Assertion-Evidence слайд:**
```
┌──────────────────────────────────────┐
│ Caching reduced latency by 70%       │ ← Утверждение (вывод)
├──────────────────────────────────────┤
│                                      │
│    ┌──────────────────────────┐      │
│    │ [График: Before/After]  │      │ ← Визуальное
│    │    50ms → 15ms          │      │   доказательство
│    └──────────────────────────┘      │
│                                      │
└──────────────────────────────────────┘
```

### Правило 1-6-6

| Элемент | Максимум | Почему |
|---------|----------|--------|
| **1** идея | на слайд | Cognitive load |
| **6** bullet points | на слайд | 4±1 rule |
| **6** слов | на bullet | Scanning vs reading |

### Визуальная иерархия

```
ВЫСОКИЙ КОНТРАСТ          НИЗКИЙ КОНТРАСТ
(привлекает внимание)     (фон, детали)

┌─────────────────────────────────────────┐
│                                         │
│   ████████████████████  ← Заголовок     │
│                         (самый крупный) │
│                                         │
│   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     ← Key message   │
│                         (средний)       │
│                                         │
│   ░░░░░░░░░░░░░░░░░░   ← Детали        │
│                         (мелкий)        │
└─────────────────────────────────────────┘
```

### Цветовые схемы

**Для tech презентаций:**

| Фон | Текст | Акцент | Когда использовать |
|-----|-------|--------|-------------------|
| Тёмный (#1a1a2e) | Светлый (#eaeaea) | Синий (#4361ee) | Конференции, демо |
| Светлый (#ffffff) | Тёмный (#2b2d42) | Зелёный (#06d6a0) | Дневные митинги |
| Нейтральный (#f8f9fa) | Тёмный (#212529) | Оранжевый (#ff6b35) | Формальные |

**Правило 60-30-10:**
- 60% — основной цвет (фон)
- 30% — вторичный (текст, блоки)
- 10% — акцент (CTA, важное)

---

## Визуализация данных

### Выбор типа графика

| Цель | Тип графика | Пример использования |
|------|-------------|---------------------|
| **Сравнение** | Bar chart | Latency разных сервисов |
| **Тренд** | Line chart | Performance за 6 месяцев |
| **Пропорции** | Pie chart (max 5 секторов) | Распределение трафика |
| **Корреляция** | Scatter plot | CPU vs Response time |
| **Процесс** | Flowchart | CI/CD pipeline |
| **Иерархия** | Tree diagram | Микросервисы |

### Правила визуализации

**❌ Плохо:**
```
┌─────────────────────────────┐
│ Response Time by Service    │
│                             │
│ Auth:        145.7823ms     │
│ Users:       89.2341ms      │
│ Products:    234.1298ms     │
│ Payments:    567.9012ms     │
│ Inventory:   123.4567ms     │
│ Shipping:    345.6789ms     │
└─────────────────────────────┘
```

**✅ Хорошо:**
```
┌─────────────────────────────────────────┐
│ Payments — bottleneck (568ms)           │
│                                         │
│ Payments  ████████████████████████ 568  │
│ Shipping  ██████████████           346  │
│ Products  █████████                234  │
│ Auth      █████                    146  │
│ Inventory ████                     123  │
│ Users     ███                       89  │
│                                         │
│ Target: <200ms ─────────┼               │
└─────────────────────────────────────────┘
```

### Data-Ink Ratio (Edward Tufte)

```
Data-Ink Ratio = Ink used for data / Total ink used

Цель: Максимизировать (убрать визуальный шум)

УБРАТЬ:
✗ 3D эффекты
✗ Тени
✗ Градиенты
✗ Gridlines (или сделать subtle)
✗ Redundant labels
```

---

## Progressive Disclosure

### Принцип

Показывать информацию **постепенно**, не всё сразу.

### Техники

**1. Build animations (появление по клику):**
```
Клик 1:  [Шаг 1]
Клик 2:  [Шаг 1] → [Шаг 2]
Клик 3:  [Шаг 1] → [Шаг 2] → [Шаг 3]
```

**2. Layered diagrams:**
```
Слайд 1: Высокоуровневая архитектура (3 блока)
Слайд 2: Zoom in на блок 1 (детали)
Слайд 3: Zoom in на блок 2 (детали)
```

**3. Highlight technique:**
```
┌─────────────────────────────────────────┐
│                                         │
│   [Dim] ───→ [Dim] ───→ [HIGHLIGHT]     │
│                         ▲               │
│                         │               │
│                    Текущий фокус        │
└─────────────────────────────────────────┘
```

### Пример для Architecture Diagram

**Плохо:** Показать всю диаграмму из 20 компонентов сразу

**Хорошо:**
```
Слайд 1: "Наша система состоит из 3 слоёв"
         [Frontend] → [Backend] → [Data]

Слайд 2: "Frontend layer"
         [React App] → [Next.js] → [CDN]

Слайд 3: "Backend layer"
         [API Gateway] → [Microservices] → [Message Queue]
```

---

## Скрипты и шаблоны

### Opening hooks (первые 30 секунд)

**1. Статистика:**
```
"Каждую секунду наш сервис обрабатывает 10,000 запросов.
 Вчера один из них занял 47 секунд.
 Сегодня я расскажу, почему."
```

**2. Вопрос:**
```
"Поднимите руку, кто хоть раз ждал deploy больше часа.
 [пауза]
 А теперь — кто делал это в пятницу вечером?
 [смех]
 Давайте поговорим о CI/CD."
```

**3. Контраст:**
```
"В 2020 году наш релиз занимал 4 часа.
 Сегодня — 4 минуты.
 Вот как мы это сделали."
```

**4. История:**
```
"В 3 часа ночи в субботу мне позвонил PagerDuty.
 500 errors, 90% пользователей не могут залогиниться.
 То, что я узнал за следующие 6 часов, изменило нашу архитектуру."
```

### Transition phrases (signposting)

| Переход | Фраза |
|---------|-------|
| К следующему разделу | "Теперь перейдём к..." |
| Углубление | "Давайте рассмотрим подробнее..." |
| Пример | "Позвольте проиллюстрировать это..." |
| Возврат | "Как я упоминал ранее..." |
| Итог секции | "Итак, ключевой вывод здесь..." |
| К действию | "Что это означает на практике?" |

### Closing templates

**Summary:**
```
"Давайте подведём итоги. Мы обсудили три вещи:
 1. [Первый key point]
 2. [Второй key point]
 3. [Третий key point]"
```

**Call to action:**
```
"Если вы заберёте из этой презентации одну мысль,
 пусть это будет: [ГЛАВНЫЙ ТЕЗИС].

 Следующий шаг: [КОНКРЕТНОЕ ДЕЙСТВИЕ]."
```

**Q&A setup:**
```
"У нас есть 10 минут на вопросы.
 Если не успеем — я доступен в Slack @username.
 Какие вопросы?"
```

---

## Распространённые ошибки

### 1. "Wall of Text"

```
❌ ПРОБЛЕМА:
┌─────────────────────────────────────────────────────────┐
│ The implementation of microservices architecture        │
│ requires careful consideration of service boundaries,   │
│ data consistency patterns, inter-service communication  │
│ protocols, deployment strategies, monitoring and        │
│ observability requirements, security considerations,    │
│ and team organizational structures following Conway's   │
│ Law principles to ensure optimal alignment between...   │
└─────────────────────────────────────────────────────────┘

✅ РЕШЕНИЕ:
┌─────────────────────────────────────────────────────────┐
│ Microservices need 3 things:                            │
│                                                         │
│ 1. Clear boundaries  →  Domain-driven design            │
│ 2. Smart communication  →  Async messaging              │
│ 3. Observable systems  →  Distributed tracing           │
└─────────────────────────────────────────────────────────┘
```

### 2. "Death by Demo"

**❌ Проблема:** Live demo без подготовки
- IDE не настроена
- Данные не подготовлены
- Network fail

**✅ Решение:**
```
DEMO SAFETY NET:

1. Record backup video
2. Prepare fallback screenshots
3. Use demo-specific environment
4. Script every step
5. Have "demo mode" with mock data
6. Test 3 раза before presentation
```

### 3. "Audience Amnesia"

**❌ Проблема:** Не повторять key points

**✅ Решение (Rule of 3):**
```
1. PREVIEW:  "I'm going to tell you X"
2. DELIVER:  "Here is X"
3. REVIEW:   "I told you X"
```

### 4. "Orphan Slides"

**❌ Проблема:** Слайды без контекста перехода

**✅ Решение:** Каждый слайд связывать с предыдущим
```
"Мы обсудили проблему масштабирования.
 [клик]
 Теперь посмотрим на решение — кэширование."
```

### 5. "False Ending"

**❌ Проблема:** После "Спасибо за внимание" ещё 5 слайдов

**✅ Решение:**
```
Структура финала:
1. Summary slide
2. Call to action
3. Contact info
4. "Questions?" slide
5. [Appendix slides — backup only, не показывать]
```

---

## Когда использовать / НЕ использовать

### Когда слайды нужны

| Ситуация | Почему слайды |
|----------|---------------|
| **>15 минут** | Удержание внимания |
| **Визуальные данные** | Графики, диаграммы, архитектура |
| **Asynchronous viewing** | Документ для sharing |
| **Formal settings** | Board, investors, conferences |
| **Complex topics** | Progressive disclosure |

### Когда слайды НЕ нужны

| Ситуация | Альтернатива |
|----------|--------------|
| **5-min update** | Устно + whiteboard |
| **Brainstorming** | Whiteboard, Miro |
| **1-on-1 discussion** | Разговор |
| **Code review** | Screen share IDE |
| **Quick demo** | Live share |

### Альтернативы слайдам

| Формат | Когда использовать |
|--------|-------------------|
| **Amazon-style 6-pager** | Deep strategy discussions |
| **Loom video** | Async demos, walkthroughs |
| **Notion doc** | Technical RFCs |
| **Live coding** | Teaching, workshops |
| **Whiteboard** | Architecture brainstorming |

---

## Практические задания

### Задание 1: Minto Restructure

**Ситуация:** Вы написали 20 слайдов о миграции на Kubernetes

**Задача:** Перестройте по Minto Pyramid
1. Какой главный вывод? (1 предложение)
2. 3 поддерживающих аргумента
3. Какие слайды можно убрать в Appendix?

### Задание 2: Assertion-Evidence

**Исходный слайд:**
```
"Database Performance"
• Query optimization done
• Indexes added
• Connection pooling implemented
• Results show improvement
```

**Задача:** Перепишите в assertion-evidence формате

**Ожидаемый результат:**
```
"Query optimization reduced load time by 60%"
[График: Before 500ms → After 200ms]
```

### Задание 3: SCQA для Sprint Demo

**Контекст:** Вы сделали фичу "export to PDF" для отчётов

**Задача:** Напишите SCQA opening (4 предложения)

### Задание 4: Hook Creation

**Тема:** "Why We Switched from REST to GraphQL"

**Задача:** Придумайте 3 разных hook:
1. Статистика
2. Вопрос к аудитории
3. Мини-история

### Задание 5: Slide Audit

**Задача:** Возьмите свою последнюю презентацию (или найдите публичную) и проведите аудит:

```
□ Minto: Главный вывод на слайде 1-3?
□ SCQA: Есть контекст проблемы?
□ 10-20-30: Соблюдается?
□ 1-6-6: Один слайд = одна идея?
□ Assertion-Evidence: Заголовки — утверждения?
□ Signposting: Есть переходы?
□ Progressive disclosure: Информация раскрывается постепенно?
□ Closing: Есть summary + CTA?
```

---

## Чеклист презентации

### Перед созданием

```
□ Определена цель: что аудитория должна СДЕЛАТЬ после?
□ Определена аудитория: кто? что знают? что важно им?
□ Определён формат: сколько времени? онлайн/офлайн?
□ Главный тезис сформулирован в 1 предложении
```

### Структура

```
□ Minto: вывод в начале, не в конце
□ SCQA: контекст задан в первые 2-3 минуты
□ 3 основных раздела (не больше 5)
□ Каждый раздел имеет свой вывод
□ Summary повторяет ключевые points
□ Есть чёткий Call to Action
```

### Дизайн

```
□ 1 идея на слайд
□ Шрифт ≥30pt
□ Заголовки — утверждения, не темы
□ Визуалы > текста
□ Консистентный стиль (цвета, шрифты)
□ Контрастность достаточная
```

### Подготовка

```
□ Прогон вслух ≥3 раза
□ Тайминг проверен
□ Demo протестировано (backup есть)
□ Технические проверки (проектор, звук, интернет)
□ Q&A: подготовлены ответы на 5 likely questions
```

---

## Инструменты

| Инструмент | Для чего | Особенности |
|------------|----------|-------------|
| **Keynote/PowerPoint** | Классические презентации | Full control, offline |
| **Google Slides** | Collaborative editing | Real-time, web-based |
| **Figma** | Custom design | Pixel-perfect, но steep learning curve |
| **Canva** | Quick professional look | Templates, easy |
| **Marp** | Slides as code (Markdown) | Git-friendly, developers love it |
| **reveal.js** | Interactive web presentations | HTML/JS, custom animations |
| **Pitch** | Modern collaborative | Beautiful defaults |

### Для диаграмм

| Инструмент | Тип |
|------------|-----|
| **Mermaid** | Diagrams as code |
| **Excalidraw** | Hand-drawn style |
| **Miro** | Collaborative whiteboard |
| **Lucidchart** | Professional diagrams |
| **draw.io** | Free, full-featured |

---

## Связанные темы

### Prerequisites
- [[storytelling-tech]] — нарративные техники
- [[technical-presentations]] — специфика tech talks

### Unlocks
- [[conference-speaking]] — выступления на конференциях
- [[executive-communication]] — презентации C-level

### Интеграция
- [[negotiation-fundamentals]] — убеждение в презентациях
- [[stakeholder-negotiation]] — адаптация под стейкхолдеров

---

## Источники

1. Minto, B. "The Minto Pyramid Principle" (McKinsey classic)
2. Reynolds, G. "Presentation Zen" (2024 edition)
3. Duarte, N. "Resonate" и "slide:ology"
4. Kawasaki, G. "The Art of the Start" (10-20-30 rule)
5. Tufte, E. "The Visual Display of Quantitative Information"
6. Prezi State of Presentations Report (2024)
7. Microsoft Research on attention spans
8. 3M Corporation visual communication studies
9. Garr Reynolds Blog (presentationzen.com)
10. assertion-evidence.com — научный подход к слайдам

---

**Последнее обновление:** 2025-01-18
**Статус:** Завершён
