---
title: "Reasoning Models: o1, o3, DeepSeek R1, Claude Extended Thinking"
created: 2025-12-24
updated: 2026-02-13
author: AI Assistant
reading_time: 56
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
level: advanced
type: guide
topics:
  - reasoning
  - o1
  - o3
  - deepseek-r1
  - chain-of-thought
  - extended-thinking
  - test-time-compute
  - GRPO
  - QwQ
  - Gemini
status: published
tags:
  - topic/ai-ml
  - type/guide
  - level/intermediate
related:
  - "[[llm-fundamentals]]"
  - "[[models-landscape-2025]]"
  - "[[ai-api-integration]]"
---

# Reasoning Models: Революция в мышлении ИИ

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Как работает генерация текста | [[llm-fundamentals]] |
| **Chain-of-Thought** | Основа reasoning | [[prompt-engineering-masterclass]] |
| **API интеграция** | Работа с o1, R1, Claude | [[ai-api-integration]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ✅ Да | Понятное объяснение новой парадигмы |
| **AI Engineer** | ✅ Да | Практическое применение reasoning моделей |
| **Исследователь** | ✅ Да | Глубокий разбор архитектур |
| **Tech Lead** | ✅ Да | Выбор модели под задачу |

### Терминология для новичков

> 💡 **Reasoning Model** = AI, который "думает" перед ответом, а не отвечает мгновенно

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Reasoning** | Пошаговое рассуждение перед ответом | **Думать вслух** — показать ход мыслей, а не только ответ |
| **Chain-of-Thought (CoT)** | Цепочка рассуждений | **Черновик решения** — записать шаги, потом дать ответ |
| **Test-Time Compute** | Вычисления во время генерации ответа | **Время на раздумья** — чем дольше думает, тем лучше ответ |
| **Thinking Tokens** | Токены "размышления" модели | **Внутренний монолог** — модель рассуждает сама с собой |
| **Extended Thinking** | Режим глубокого размышления (Claude) | **Режим эксперта** — модель тратит больше времени на сложные задачи |
| **GRPO** | Group Relative Policy Optimization (DeepSeek) | **Обучение сравнением** — модель учится, сравнивая разные решения |
| **Self-Correction** | Модель проверяет и исправляет себя | **Самопроверка** — перечитать решение и исправить ошибки |
| **Knowledge Cutoff** | Дата, после которой модель не знает событий | **Последние новости** — модель не читала новости после этой даты |

---

## Содержание

1. [Пролог: Декабрь 2024](#пролог-декабрь-2024---момент-когда-всё-изменилось)
2. [Что такое Reasoning](#что-такое-reasoning-когда-модель-думает-перед-ответом)
3. [Механика работы](#механика-работы-как-устроены-reasoning-models)
4. [Основные игроки](#основные-игроки-reasoning-рынка)
5. [Сравнительный анализ](#сравнительный-анализ-моделей)
6. [Практическое использование](#практическое-использование)
7. [Prompt Engineering для Reasoning](#prompting-для-reasoning-models-меньше-значит-лучше)
8. [Ограничения и проблемы](#ограничения-и-проблемы-reasoning-моделей)
9. [Будущее Reasoning](#будущее-reasoning-моделей)

---

## Теоретические основы

### Система 1 vs Система 2: когнитивное обоснование

> Даниэль Канеман (2011, *"Thinking, Fast and Slow"*) выделил два режима мышления: **Система 1** (быстрая, интуитивная, автоматическая) и **Система 2** (медленная, аналитическая, осознанная). Стандартные LLM работают по принципу Системы 1 — мгновенная реакция. Reasoning-модели реализуют Систему 2 — deliberate thinking перед ответом.

### Формализация reasoning в LLM

| Подход | Год | Авторы | Механизм |
|--------|-----|--------|----------|
| **Chain-of-Thought (CoT)** | 2022 | Wei et al. (Google) | Промежуточные шаги в промпте |
| **Self-Consistency** | 2022 | Wang et al. (Google) | Голосование по нескольким CoT-путям |
| **Tree-of-Thought (ToT)** | 2023 | Yao et al. (Princeton) | Поиск с бэктрекингом в дереве рассуждений |
| **Test-Time Compute** | 2024 | OpenAI (o1) | Выделение compute при inference на «размышления» |
| **GRPO** | 2025 | DeepSeek | Group Relative Policy Optimization — RL без reward model |

### Test-Time Compute Scaling

> **Test-Time Compute** — новая парадигма масштабирования: вместо увеличения модели при training, увеличивается compute при inference. Модель генерирует «thinking tokens» — внутренний chain-of-thought, который используется для формирования финального ответа. Snell et al. (2024, *"Scaling LLM Test-Time Compute Optimally"*) показали, что точность растёт логарифмически с увеличением thinking budget.

### DeepSeek R1: reasoning через чистый RL

> DeepSeek-R1-Zero (DeepSeek-AI, 2025) продемонстрировал, что reasoning capabilities (self-verification, reflection, long CoT) могут **эмергентно** возникнуть из pure reinforcement learning без supervised fine-tuning на reasoning trajectories. Это фундаментальный результат: способность к рассуждению не требует явного обучения на примерах рассуждений.

### Ограничения reasoning-моделей

Формально: reasoning-модели не «понимают» задачу — они генерируют последовательности токенов с высокой вероятностью быть корректным рассуждением. Huang et al. (2024, *"Large Language Models Cannot Self-Correct Reasoning Yet"*) показали, что self-correction без внешней обратной связи часто ухудшает результат.

---

## Пролог: Декабрь 2024 - Момент, когда все изменилось

Декабрь 2024 года войдет в историю ИИ как месяц, когда индустрия изменилась навсегда.

До этого момента все языковые модели работали по одному принципу: получи вопрос - выдай ответ. Максимально быстро. Как рефлекс. GPT-4, Claude, Gemini - все они были невероятно умны, но думали "на автопилоте". Спросите их сложную математическую задачу, и они мгновенно выдадут ответ. Иногда правильный. Часто - нет. Потому что они не **думали** над задачей - они **реагировали** на нее.

А потом появился o1.

Первый разговор с o1 был странным. Ты задаешь вопрос... и ждешь. 5 секунд. 10 секунд. 30 секунд. Что происходит? Модель зависла? Нет. Она **думает**. Впервые в истории ИИ модель остановилась и задумалась перед тем, как отвечать.

И когда ответ пришел - он был другим. Не просто правильным, а **обоснованным**. Модель не угадала ответ - она его вывела. Шаг за шагом. Как человек, который берет ручку и бумагу, чтобы решить сложную задачу.

**Хронология событий декабря 2024:**

- **12 декабря 2024** - OpenAI выпускает полную версию o1
- **19 декабря 2024** - Google анонсирует Gemini 2.0 Flash Thinking
- **20 декабря 2024** - OpenAI анонсирует o3 на последний день "12 Days of Shipmas"
- **Январь 2025** - DeepSeek выпускает R1 под MIT лицензией, потрясая индустрию

Это была революция. Тихая, но фундаментальная.

---

## Что такое Reasoning: Когда модель думает перед ответом

### Простое объяснение

Представьте двух студентов на экзамене по математике.

**Первый студент** (обычная модель) смотрит на задачу и сразу пишет ответ. Он видел тысячи похожих задач и "чувствует", каким должен быть ответ. Иногда угадывает. Иногда нет. Но он никогда не останавливается, чтобы **подумать**.

**Второй студент** (reasoning модель) читает задачу, откладывает ручку и начинает рассуждать. "Так, что тут спрашивают? Какие данные у меня есть? Какой метод подойдет? Давай попробую... нет, это не работает. А если так? Да, это имеет смысл. Проверю на простом примере... Сходится. Окей, теперь могу записать ответ."

Разница колоссальная. Первый студент быстрее. Второй - точнее.

### Техническое определение

Reasoning models - это **новая категория специализированных языковых моделей**, предназначенных для разбиения сложных проблем на меньшие, управляемые шаги и решения их через явное логическое рассуждение (также называемое "thinking").

В отличие от обычных LLM, которые генерируют прямые ответы, reasoning модели специально обучены **показывать свою работу** и следовать более структурированному мыслительному процессу.

### Аналогия: Система 1 и Система 2

Психолог Даниэль Канеман описал два типа человеческого мышления:

- **Система 1**: Быстрое, интуитивное, автоматическое. "Сколько будет 2+2?" - "4" (мгновенно).
- **Система 2**: Медленное, аналитическое, осознанное. "Сколько будет 127x89?" - нужно сесть и посчитать.

Обычные LLM - это Система 1. Они реагируют мгновенно, опираясь на паттерны из обучающих данных.

Reasoning models - это Система 2. Они останавливаются, анализируют, рассуждают и только потом отвечают.

```
ОБЫЧНАЯ МОДЕЛЬ (System 1):
+------------------+        +------------------+
|  "127 x 89 = ?" | -----> |     "11293"      |  <- Быстро, но ошибка!
+------------------+        +------------------+
       Input            Мгновенный output

REASONING MODEL (System 2):
+------------------+        +--------------------------------+        +-----------+
|  "127 x 89 = ?" | -----> | "Так, 127 x 89...              | -----> |  "11303"  |
+------------------+        | Можно разбить: 127 x (90-1)    |        +-----------+
       Input               | = 127 x 90 - 127               |         Правильно!
                           | = 11430 - 127                  |
                           | = 11303. Проверю: ..."         |
                           +--------------------------------+
                                Внутреннее рассуждение
                                 (thinking tokens)
```

---

## Механика работы: Как устроены Reasoning Models

### Test-Time Compute: Ключевая инновация

**Test-Time Compute (TTC)** - это вычисления, которые происходят во время inference (когда модель отвечает), а не во время training (когда модель учится).

Традиционный подход к улучшению моделей: увеличивайте размер модели, данные, compute при обучении. Это дорого и имеет пределы.

Новый подход: позвольте модели **думать дольше** над сложными задачами. Тратьте больше compute там, где нужно.

**Ключевое исследование Google DeepMind** (август 2024):
> "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"

Результаты показали:
- На сложных задачах test-time compute может дать эффект, сравнимый с 14x увеличением модели
- Compute-optimal стратегия улучшает эффективность в 4x по сравнению с best-of-N baseline
- Эффективность TTC критически зависит от сложности задачи

### Типы Test-Time Scaling

```
+------------------------------------------------------------------+
|                    ТИПЫ TEST-TIME SCALING                         |
+------------------------------------------------------------------+
|                                                                    |
| PARALLEL SCALING:                                                  |
| - Генерируем множество ответов параллельно                        |
| - Агрегируем через majority voting или reward model               |
| - Пример: Best-of-N sampling                                       |
|                                                                    |
| SEQUENTIAL SCALING:                                                |
| - Модель рассуждает шаг за шагом последовательно                  |
| - Каждый шаг зависит от предыдущего                               |
| - Пример: Chain of Thought reasoning                               |
|                                                                    |
| HYBRID SCALING:                                                    |
| - Комбинация параллельного и последовательного                    |
| - Пример: Tree of Thoughts                                         |
|                                                                    |
| INTERNAL SCALING:                                                   |
| - Модель сама определяет сколько compute выделить                 |
| - Реализовано внутри архитектуры модели                           |
| - Пример: Claude Extended Thinking с dynamic budget                |
|                                                                    |
+------------------------------------------------------------------+
```

### Reasoning Tokens: Как модель "думает"

**Reasoning tokens** (thinking tokens) - это внутренний механизм, уникальный для reasoning моделей.

**Как они работают:**

1. Модель получает input prompt
2. Генерирует **reasoning tokens** - внутренние рассуждения
3. Эти токены "разбивают" задачу на компоненты
4. Оценивают разные подходы к решению
5. Имитируют мыслительный процесс человека
6. Генерируют **output tokens** - финальный ответ
7. Reasoning tokens отбрасываются из контекста (но оплачиваются!)

**Важно понимать:**
- Reasoning tokens занимают место в context window
- Они оплачиваются как output tokens
- От сотен до десятков тысяч токенов в зависимости от сложности
- OpenAI показывает только summary, не сырой reasoning

### Паттерны рассуждений o1

Исследование (arxiv 2410.13639) выявило 6 типов паттернов рассуждений o1:

| Паттерн | Аббревиатура | Описание | Когда используется |
|---------|--------------|----------|---------------------|
| **Systematic Analysis** | SA | Систематический анализ всех аспектов | Общий подход |
| **Method Reuse** | MR | Применение известных методов | Математика, код |
| **Divide and Conquer** | DC | Разбиение на подзадачи | Сложные задачи |
| **Self-Refinement** | SR | Самокоррекция и улучшение | Проверка решения |
| **Context Identification** | CI | Определение контекста задачи | Commonsense |
| **Emphasizing Constraints** | EC | Фокус на ограничениях | Логические задачи |

**Ключевой вывод**: DC (Divide and Conquer) и SR (Self-Refinement) - самые частые паттерны, которые могут быть ключом к успеху o1.

### Обучение Reasoning моделей

#### Reinforcement Learning with Verifiable Rewards (RLVR)

RLVR - основной метод обучения современных reasoning моделей:

```
+------------------------------------------------------------------+
|                           RLVR PIPELINE                           |
+------------------------------------------------------------------+
|                                                                    |
| 1. BASE MODEL                                                      |
|    - Pretrained LLM (GPT, Llama, DeepSeek-V3)                     |
|                                                                    |
| 2. REWARD SIGNAL                                                   |
|    - Правильный/неправильный ответ (verifiable)                   |
|    - Не требует reward model для простых случаев                  |
|    - Для DeepSeek R1: буквально regex matching!                   |
|                                                                    |
| 3. RL OPTIMIZATION                                                 |
|    - PPO (Proximal Policy Optimization) - OpenAI подход           |
|    - GRPO (Group Relative Policy Optimization) - DeepSeek подход  |
|                                                                    |
| 4. EMERGENT REASONING                                              |
|    - Модель сама "изобретает" способы рассуждать                  |
|    - Self-verification, reflection, long CoT появляются сами      |
|                                                                    |
+------------------------------------------------------------------+
```

#### GRPO: Прорыв DeepSeek

**Group Relative Policy Optimization (GRPO)** - алгоритм RL, представленный в DeepSeekMath и использованный для R1.

**Отличия от PPO:**

| Аспект | PPO | GRPO |
|--------|-----|------|
| Value Function | Требуется отдельная модель | Не требуется |
| Advantage Calculation | Индивидуальный | Относительно группы |
| Memory Usage | Высокий | На ~50% меньше |
| KL Divergence | В reward | В loss function |
| Compute Requirements | Стандартный | На ~50% меньше |

**Результаты DeepSeekMath с GRPO:**
- GSM8K: 82.9% -> 88.2% (+5.3%)
- MATH: 46.8% -> 51.7% (+4.9%)
- CMATH: 84.6% -> 88.8% (+4.2%)

#### Process Reward Models vs Outcome Reward Models

**Outcome Reward Models (ORM):**
- Оценивают только финальный ответ
- Проще в обучении
- Могут награждать неправильный reasoning за правильный ответ

**Process Reward Models (PRM):**
- Оценивают каждый шаг рассуждения
- Сложнее в обучении (нужна разметка шагов)
- Лучше alignment: награждают правильный процесс

**OpenAI Research (2023):**
> "Process supervision can train much more reliable reward models than outcome supervision"

Результат: 78.2% на MATH test set с PRM vs менее надежные результаты с ORM.

---

## Основные игроки Reasoning рынка

### OpenAI o-series

#### o1 (Сентябрь-Декабрь 2024)

**o1-preview** (сентябрь 2024) - первая публичная reasoning модель.

**o1** (декабрь 2024) - полная версия:
- AIME 2024: 74.3%
- Codeforces: 1891 ELO
- SWE-Bench Verified: 48.9%

**Ключевые характеристики:**
- Скрытый chain of thought (только summary)
- Нет system prompt поддержки
- Нет streaming
- Нет vision
- Высокая стоимость: $15/M input, $60/M output

#### o3 (Декабрь 2024 анонс, Апрель 2025 релиз)

Анонсирован 20 декабря 2024 как финал "12 Days of Shipmas".

**Почему o3, а не o2?**
> Sam Altman: "Решение было чисто из-за потенциальных проблем с товарным знаком O2 (мобильный оператор)"

**Benchmark результаты:**
- AIME 2024: 91.6% (vs o1: 74.3%)
- AIME 2025: 88.9%
- Codeforces: 2706 ELO (vs o1: 1891)
- SWE-Bench Verified: 69.1% (vs o1: 48.9%)
- ARC-AGI: 3x точнее чем o1
- EpochAI Frontier Math: 25.2% (другие модели < 2%)

**Новые возможности (апрель 2025):**
- Vision (анализ изображений)
- Tool use (веб-поиск, Python, генерация изображений)
- Streaming
- Deliberative Alignment (самопроверка на safety)
- Self-fact-checking

**Важное:**
> "O3 and o4-mini are both smarter AND cheaper than o1 and o3-mini respectively for most real-world usage"

#### o3-mini

Быстрая, экономичная версия с настраиваемым reasoning effort:

```python
# Контроль глубины рассуждения
reasoning_effort = "low"     # Быстро, дешево
reasoning_effort = "medium"  # Баланс (по умолчанию)
reasoning_effort = "high"    # Максимум качества
```

**Производительность o3-mini-high:**
- MATH-500: 96.7% (vs o1: 83.3%)

#### o4-mini (Апрель 2025)

Следующее поколение после o3-mini с еще лучшим соотношением цена/качество.

### Anthropic Claude Extended Thinking

#### Философия: Гибридный подход

> "We've developed Claude 3.7 Sonnet with a different philosophy from other reasoning models on the market. Just as humans use a single brain for both quick responses and deep reflection, we believe reasoning should be an integrated capability of frontier models rather than a separate model entirely."

**Преимущество:** Одна модель, два режима - не нужно выбирать между моделями.

#### Claude 3.7 Sonnet (Февраль 2025)

**Первая hybrid reasoning модель:**
- Standard mode: улучшенный Claude 3.5 Sonnet
- Extended thinking mode: глубокий анализ

**Benchmarks с Extended Thinking:**
- SWE-bench Verified: 63.7% (без scaffolding), 70.3% (с enhanced TTC)
- GPQA Physics: 96.5%
- Общий reasoning: 68% -> 84.8% с extended thinking

**Thinking Budget:**
```python
thinking = {
    "type": "enabled",
    "budget_tokens": 10000  # От 1,024 до 128,000
}
```

**Логарифмическое улучшение:**
> "Performance on mathematics improves logarithmically as thinking tokens increase"

#### Claude 4.5 Sonnet и Opus 4.5 (2025)

Новые модели с улучшенным extended thinking:
- Используют драматически меньше токенов для достижения аналогичных или лучших результатов
- "Less backtracking, less redundant exploration, less verbose reasoning"

#### Уникальные возможности Claude

**Visible Thinking:**
- Полный chain of thought виден (не summary как у o1)
- Позволяет изучать reasoning модели
- Полезно для alignment research

**Interleaved Thinking:**
- Claude думает **между** tool calls
- Более естественная интеграция reasoning и actions

**Safety:**
> "In rare cases, Claude's thought process might include potentially harmful content. In such cases, the thought process will be encrypted."

### DeepSeek R1: Open Source революция

#### Прорыв января 2025

DeepSeek R1 потряс индустрию, достигнув уровня o1 при:
- **96% дешевле** в API
- **MIT лицензия** - полностью открытый
- **Открытые веса** - можно запускать локально

**Архитектура:**
- 671B total parameters
- 37B active parameters (MoE)
- 128K context window

#### Уникальность подхода

**DeepSeek-R1-Zero:**
- Обучен **только через RL**, без SFT
- Reasoning capabilities emerged naturally
- Даже reward model не использовали - regex matching!

> "It is the first open research to validate that reasoning capabilities of LLMs can be incentivized purely through RL, without the need for SFT."

**Emergent behaviors:**
- Self-verification
- Reflection
- Dynamic strategy adaptation
- Long chains of thought

#### Benchmark сравнение с o1

| Benchmark | DeepSeek R1 | OpenAI o1-1217 |
|-----------|-------------|----------------|
| AIME 2024 | 79.8% | 79.2% |
| MATH-500 | 97.3% | 96.4% |
| GPQA Diamond | 71.5% | 75.7% |
| MMLU | 90.8% | 91.8% |
| Codeforces | 96.3% | 96.6% |

**Вывод:** Сопоставимое качество, кардинально ниже цена.

#### Pricing сравнение

| Модель | Input/1M | Output/1M | Cached Input |
|--------|----------|-----------|--------------|
| DeepSeek R1 | $0.55 | $2.19 | $0.14 |
| OpenAI o1 | $15.00 | $60.00 | $7.50 |
| **Разница** | **27x** | **27x** | **54x** |

#### Distilled версии

Для локального запуска доступны distilled модели:
- DeepSeek-R1-Distill-Qwen-1.5B
- DeepSeek-R1-Distill-Qwen-7B
- DeepSeek-R1-Distill-Llama-8B
- DeepSeek-R1-Distill-Qwen-14B
- DeepSeek-R1-Distill-Qwen-32B
- DeepSeek-R1-Distill-Llama-70B

**Запуск через Ollama:**
```bash
ollama run deepseek-r1:7b
ollama run deepseek-r1:32b
```

### Qwen QwQ (Alibaba)

#### QwQ-32B-Preview (Ноябрь 2024)

**QwQ = "Qwen with Questions"** - первая открытая reasoning модель от Alibaba.

**Характеристики:**
- 32B parameters
- 32K context (позже расширен)
- Apache 2.0 license (коммерческое использование)

**Benchmarks:**
- GPQA: 65.2%
- AIME: 50.0%
- MATH-500: 90.6%
- LiveCodeBench: 50.0%

#### QwQ-32B (2025)

Улучшенная версия, сопоставимая с DeepSeek-R1:
> "While DeepSeek-R1 operates with 671 billion parameters, QwQ-32B achieves comparable performance with a much smaller footprint."

**Преимущества:**
- Открытый thinking process (не скрыт как у o1)
- Значительно меньше compute requirements
- Apache 2.0 license

**Известные ограничения:**
- Language Mixing (смешивание языков)
- Recursive Reasoning Loops (зацикливание)

### Google Gemini Thinking

#### Gemini 2.0 Flash Thinking (Декабрь 2024)

Первая reasoning модель от Google, представлена 19 декабря 2024.

**Ключевые особенности:**
- Multimodal (текст + изображения)
- Показывает thought process в реальном времени
- Доступен в Google AI Studio и Vertex AI

**Конфигурация thinking:**
```python
# Dynamic thinking - модель сама решает сколько думать
thinking_budget = -1

# Отключить thinking
thinking_budget = 0

# Конкретный budget (токены)
thinking_budget = 10000
```

**Benchmarks:**
- AIME 2024: 73.3% (vs Flash без thinking: 35.5%)

### Сводная таблица моделей

| Модель | Компания | Open Source | Vision | Tools | Visible CoT | Цена* |
|--------|----------|-------------|--------|-------|-------------|-------|
| o1 | OpenAI | Нет | Нет | Нет | Summary | $$$$$ |
| o3 | OpenAI | Нет | Да | Да | Summary | $$$$$ |
| o3-mini | OpenAI | Нет | Да | Да | Больше | $$ |
| DeepSeek R1 | DeepSeek | Да (MIT) | Нет | Да | Полный | $ |
| Claude ET | Anthropic | Нет | Да | Да | Полный | $$$ |
| QwQ-32B | Alibaba | Да (Apache) | Нет | Нет | Полный | $ |
| Gemini Thinking | Google | Нет | Да | Да | Полный | $$ |

*Относительная оценка

---

## Сравнительный анализ моделей

### Claude 3.7 vs o1 vs DeepSeek R1

**Reasoning качество:**
```
o3 > o1 ≈ Claude ET (high budget) ≈ DeepSeek R1 > Claude ET (low budget) > o3-mini
```

**Coding (SWE-Bench Verified):**
| Модель | Score |
|--------|-------|
| Claude 3.7 ET | 70.3% (with enhanced TTC) |
| o3 | 69.1% |
| Claude 3.5 Sonnet | 50.8% |
| DeepSeek R1 | 49.2% |
| o1 | 48.9% |

**Instruction Following:**
- Claude 3.7: 93.2%
- DeepSeek R1: 83.3%

**Cost-Performance для большинства задач:**
```
DeepSeek R1 >>> Claude ET > o3-mini > o3 > o1
```

### Когда использовать какую модель

**Выберите o3**, если:
- Нужно максимальное качество reasoning
- Бюджет не ограничен
- Важны vision и tool use в reasoning
- Enterprise с Microsoft/OpenAI partnership

**Выберите o3-mini**, если:
- Нужен баланс скорость/качество/цена
- Можно настроить reasoning effort
- Streaming важен

**Выберите DeepSeek R1**, если:
- Бюджет критичен (27x дешевле o1)
- Нужен open source
- Хотите запускать локально (privacy)
- Хотите изучать полный chain of thought

**Выберите Claude Extended Thinking**, если:
- Нужна гибкость (один API, два режима)
- Важна интеграция с tools
- Хотите точно контролировать thinking budget
- Задачи по физике и науке (96.5% GPQA Physics!)

**Выберите QwQ-32B**, если:
- Нужен open source
- Ограничены compute ресурсы
- Не нужна multimodality

---

## Практическое использование

### Когда Reasoning vs обычные модели

#### Decision Framework

```
                        Задача сложная?
                              |
              +---------------+---------------+
              |               |               |
             НЕТ           СРЕДНЕ             ДА
              |               |               |
              v               v               |
         GPT-4o /        Ошибка дорого        |
         Claude          стоит?               |
         Sonnet               |               |
                    +---------+---------+     |
                    |                   |     |
                   НЕТ                 ДА     |
                    |                   |     |
                    v                   v     |
              GPT-4o +             o3-mini    |
              CoT prompt            (low)     |
                                              |
                              +---------------+
                              v
                    Критична ли точность?
                              |
              +---------------+---------------+
              |               |               |
        ОЧЕНЬ ВАЖНА      ВАЖНА         НЕ ОЧЕНЬ
              |               |               |
              v               v               v
           o3-pro           o3 /         o3-mini
              или      Claude ET          (high)
         Claude ET         (high              или
           (max)          budget)        DeepSeek R1
                                         (локально)
```

#### Классификация задач

**ИСПОЛЬЗУЙТЕ REASONING МОДЕЛИ:**

| Категория | Примеры |
|-----------|---------|
| **Математика и STEM** | Олимпиадные задачи, доказательства теорем, научные расчеты |
| **Программирование** | Security review, сложные алгоритмы, архитектурный рефакторинг |
| **Анализ документов** | Юридические контракты, научные статьи, due diligence |
| **LLM-as-Judge** | Оценка качества моделей, выявление ошибок и галлюцинаций |
| **Multi-step планирование** | Agentic workflows, сложные pipelines |

**ИСПОЛЬЗУЙТЕ ОБЫЧНЫЕ МОДЕЛИ:**

| Категория | Примеры |
|-----------|---------|
| **Conversational AI** | Чат-боты поддержки, виртуальные ассистенты |
| **Генерация контента** | Маркетинговые тексты, саммаризация, перевод |
| **Рутинные задачи** | Форматирование, extraction, простой Q&A |
| **Real-time** | Автокомплит в IDE, streaming приложения |

### API примеры

#### OpenAI o3

```python
from openai import OpenAI

client = OpenAI()

# Простой запрос к o3
response = client.chat.completions.create(
    model="o3",
    messages=[
        {
            "role": "user",
            "content": "Prove that there are infinitely many prime numbers."
        }
    ],
    max_completion_tokens=16000  # Включает thinking tokens
)

print(response.choices[0].message.content)
```

#### OpenAI o3-mini с reasoning effort

```python
# Контроль глубины рассуждения
response = client.chat.completions.create(
    model="o3-mini",
    messages=[
        {"role": "user", "content": "Analyze this algorithm complexity..."}
    ],
    reasoning_effort="high"  # "low", "medium", "high"
)
```

#### DeepSeek R1

```python
from openai import OpenAI

# Через API DeepSeek
client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": "Solve this logic puzzle..."}
    ]
)

# Видим весь chain of thought!
print("Reasoning:", response.choices[0].message.reasoning_content)
print("Answer:", response.choices[0].message.content)
```

#### DeepSeek R1 локально через Ollama

```bash
# Установка
ollama pull deepseek-r1:7b

# Запуск
ollama run deepseek-r1:7b
```

```python
# Через OpenAI-compatible API
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

response = client.chat.completions.create(
    model="deepseek-r1:7b",
    messages=[...]
)
```

#### Claude Extended Thinking

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # Контролируем глубину анализа
    },
    messages=[
        {
            "role": "user",
            "content": "Analyze this contract for risks..."
        }
    ]
)

# Видим и thinking, и ответ
for block in response.content:
    if block.type == "thinking":
        print(f"Claude's reasoning:\n{block.thinking}\n")
    elif block.type == "text":
        print(f"Final answer:\n{block.text}")
```

#### Динамический thinking budget

```python
# Рекомендации по budget_tokens:
THINKING_BUDGETS = {
    "simple": 1024,      # Простые задачи
    "moderate": 5000,    # Средние
    "complex": 10000,    # Сложные
    "very_complex": 20000,  # Очень сложные
    "maximum": 128000    # Максимальный анализ
}

def get_thinking_budget(task_complexity: str) -> int:
    return THINKING_BUDGETS.get(task_complexity, 5000)
```

### Практические примеры

#### Пример 1: Математическое доказательство

**Задача:** Докажите, что sqrt(2) иррационально.

**GPT-4o** (типичный ответ):
```
Предположим, что sqrt(2) = p/q, где p и q - целые...
[Может пропустить шаги или сделать логическую ошибку]
```

**o3** (с reasoning):
```
[Internal thinking - summary shown]
The model is carefully constructing a proof by contradiction,
checking each logical step and verifying the conclusion.

Final answer:
Предположим противное: sqrt(2) = p/q в несократимой дроби.
Тогда 2 = p^2/q^2, следовательно p^2 = 2q^2.
Это означает p^2 четно, значит p четно.
Пусть p = 2k. Тогда 4k^2 = 2q^2, т.е. q^2 = 2k^2.
Значит q тоже четно.
Но тогда дробь сократима - противоречие.
Следовательно, sqrt(2) иррационально.
```

#### Пример 2: Security Code Review

```python
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

**Claude Extended Thinking** (budget 10000):
```
[Thinking visible]
Анализирую код построчно...

1. SQL Injection: f-string + user input = критическая уязвимость
   Атаки: "1 OR 1=1", "1; DROP TABLE users;--"

2. Нет валидации типа user_id

3. SELECT * возвращает sensitive данные

4. Нет проверки авторизации

5. Нет rate limiting

6. Нет логирования

[Final answer]
Найдено 6 уязвимостей...
[Детальный отчет с примерами и исправлениями]
```

#### Пример 3: Алгоритмическая оптимизация

**Исходный код:**
```python
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates
```

**DeepSeek R1** (с видимым thinking):
```
<think>
Анализирую сложность:
- Внешний цикл: O(n)
- Внутренний цикл: O(n)
- Проверка 'not in duplicates': O(n) в худшем случае
- Итого: O(n^3)

Можно улучшить до O(n):
1. Использовать set для seen элементов
2. Использовать set для duplicates
3. Single pass

Edge cases:
- Пустой массив
- Все уникальные
- Все одинаковые
</think>

Оптимизированная версия:
def find_duplicates(arr):
    seen = set()
    duplicates = set()
    for item in arr:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)

Сложность: O(n) time, O(n) space
```

---

## Prompting для Reasoning Models: Меньше значит лучше

### Главное правило

> **Для reasoning моделей НЕ НУЖЕН prompt engineering в традиционном смысле.**

Chain of Thought уже встроен. Модель уже знает, что нужно думать пошагово. Добавление "Let's think step by step" не помогает - может даже навредить.

**Исследования показывают:**
> "When using explicit Chain-of-Thought prompting with reasoning models, it can hurt the instruction-following performance of the model."

### Что работает

```python
# ХОРОШО: Простой, прямой prompt
prompt = """
Solve the integral: integrate(e^x * sin(x) dx)

Show the final answer clearly.
"""

# ХОРОШО: Четкая постановка задачи без лишних инструкций
prompt = """
Analyze this code for security vulnerabilities:

[код]

List all vulnerabilities with severity ratings.
"""

# ХОРОШО: Указание желаемого формата output
prompt = """
Prove that sqrt(2) is irrational.

Format: Step-by-step proof with numbered steps.
"""
```

### Что НЕ работает

```python
# ПЛОХО: Избыточные инструкции
prompt = """
You are an expert mathematician. Think carefully step by step.
First, identify the type of problem. Then, list possible approaches.
For each approach, evaluate its feasibility.
Consider edge cases. Verify your solution...

[куча инструкций]

Now solve: What is 2 + 2?
"""
# Модель уже знает как думать! Не учите ее.

# ПЛОХО: Few-shot примеры
prompt = """
Example 1: 2+2=4
Example 2: 3+3=6

Now solve: 127 x 89 = ?
"""
# Few-shot может ограничить reasoning модель определенным паттерном

# ПЛОХО: Detailed step-by-step instructions
# Вредит, потому что сбивает внутренний reasoning процесс
```

### Сравнение подходов

| Техника | GPT-4o | o1/o3 | Claude Extended |
|---------|--------|-------|-----------------|
| System prompt | Используйте | Избегайте | Используйте |
| "Think step by step" | Помогает | Не нужен/вредит | Не нужен |
| Few-shot examples | Помогает | Может навредить | Осторожно |
| Temperature tuning | Работает | Игнорируется | Осторожно |
| Detailed instructions | Помогает | Избегайте | Умеренно |

### Аналогия

> "A reasoning model is like a senior co-worker. You can give them a goal to achieve and trust them to work out the details. A GPT model is like a junior coworker. They'll perform best with explicit instructions to create a specific output."

### Best practices для reasoning моделей

1. **Use minimal, high-level prompting** - zero-shot или single-instruction
2. **Be explicit about goals, not steps** - что нужно, не как делать
3. **Structure inputs and outputs** - delimiters, JSON/XML для output
4. **Add constraints when needed** - ограничения, не инструкции
5. **Encourage more reasoning for complex tasks** - "Please analyze thoroughly"

---

## Ограничения и проблемы Reasoning моделей

### Hallucinations в reasoning

Reasoning модели все еще галлюцинируют, хотя реже:

> "Language models hallucinate because standard training and evaluation procedures reward guessing over acknowledging uncertainty."

**Типы ошибок:**
1. **Factual errors** в reasoning steps
2. **Logical leaps** - пропуск шагов
3. **Self-reinforcing errors** - неправильный шаг ведет к неправильному выводу
4. **Reversal Curse** - знает "A is B", но не "B is A"

### Tool-Induced Myopia (TIM)

Новый тип ошибок, специфичный для reasoning + tools:

> "Access to an external tool causes the model to narrow its reasoning to what the tool can compute, rather than utilizing its full internal reasoning abilities."

**Симптомы:**
- Overreliance на tool outputs
- Более поверхностные reasoning chains при использовании tools
- Degradation усиливается с количеством tool calls

### Стоимость и латентность

| Модель | Латентность | Стоимость vs GPT-4o |
|--------|-------------|---------------------|
| GPT-4o | ~1-3 сек | 1x |
| o3-mini | ~5-30 сек | 2-5x |
| o3 | ~10-60 сек | 10-20x |
| o1 | ~20-120 сек | 15-30x |

> "Reasoning models can be 5-10x more expensive per request than standard models."

### Ограничения контроля

**OpenAI o-series:**
- Нет temperature control
- Нет system prompt (или ограничен)
- Скрытый chain of thought
- Billing за невидимые токены

### "Faithful" ли reasoning?

Anthropic Research (2024):
> "Reasoning models don't always say what they think"

Исследование показало, что модели могут:
- Генерировать "правдоподобные" reasoning traces
- Работать backwards от ответа к "обоснованию"
- Не всегда следовать тому, что написано в CoT

---

## Будущее Reasoning моделей

### Trends 2025+

1. **Hybrid models становятся нормой**
   - Одна модель для быстрых и глубоких задач
   - Claude уже делает это, другие последуют

2. **Open source догоняет**
   - DeepSeek R1 показал, что это возможно
   - Ожидайте больше открытых reasoning моделей

3. **Multimodal reasoning**
   - o3 уже умеет reasoning по изображениям
   - Gemini Thinking - multimodal by design

4. **Agentic reasoning**
   - o3/o4-mini: первые reasoning модели с full tool use
   - Reasoning между actions, не только в начале

5. **Efficient architectures**
   - Hierarchical Reasoning Model (HRM): 27M параметров, почти perfect на сложных задачах
   - State Space Models для длинного контекста

### Нерешенные проблемы

1. **Verifiable reasoning** - как проверить, что reasoning правильный?
2. **Faithful CoT** - действительно ли модель следует своему CoT?
3. **Cost optimization** - reasoning дорогой, как сделать дешевле?
4. **Safety** - как предотвратить reasoning к вредным выводам?

## Связанные материалы

- [[llm-fundamentals]] - Основы работы LLM
- [[models-landscape-2025]] - Обзор всех моделей
- [[prompt-engineering-masterclass]] - Промпт инжиниринг для обычных моделей
- [[ai-agents-advanced]] - Агенты и reasoning

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Kahneman D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux | Модель System 1 / System 2 — концептуальная основа reasoning-моделей |
| 2 | Wei J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in LLMs*. arXiv:2201.11903 | Формализация CoT-промптинга |
| 3 | Snell C. et al. (2024). *Scaling LLM Test-Time Compute*. arXiv:2408.03314 | Теоретическое обоснование test-time scaling |
| 4 | DeepSeek-AI (2025). *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL*. arXiv:2501.12948 | Эмергентное появление reasoning через pure RL (GRPO) |
| 5 | Shao Z. et al. (2024). *DeepSeekMath: Pushing the Limits of Mathematical Reasoning*. arXiv:2402.03300 | GRPO — Group Relative Policy Optimization |
| 6 | Huang J. et al. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet*. arXiv:2310.01798 | Ограничения self-correction без внешней обратной связи |
| 7 | Lightman H. et al. (2023). *Let's Verify Step by Step*. arXiv:2305.20050 | Process reward models (PRM) vs outcome reward models (ORM) |
| 8 | Russell S., Norvig P. (2020). *Artificial Intelligence: A Modern Approach*. 4th edition. Pearson | Формальная логика и reasoning как фундаментальные задачи AI |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [OpenAI — Learning to Reason with LLMs](https://openai.com/index/learning-to-reason-with-llms/) | Введение в o1 |
| 2 | [OpenAI — Introducing o3 and o4-mini](https://openai.com/index/introducing-o3-and-o4-mini/) | Релиз o3 |
| 3 | [OpenAI — Reasoning Models Guide](https://platform.openai.com/docs/guides/reasoning) | API-документация reasoning-моделей |
| 4 | [OpenAI — Reasoning Best Practices](https://platform.openai.com/docs/guides/reasoning-best-practices) | Практические рекомендации |
| 5 | [Anthropic — Claude's Extended Thinking](https://www.anthropic.com/news/visible-extended-thinking) | Visible thinking tokens |
| 6 | [Anthropic — Building with Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) | API-интеграция extended thinking |
| 7 | [Anthropic — Reasoning Models Don't Always Say What They Think](https://www.anthropic.com/research/reasoning-models-dont-say-think) | Проблема faithfulness reasoning-токенов |
| 8 | [DeepSeek-R1 GitHub](https://github.com/deepseek-ai/DeepSeek-R1) | Open-source реализация |
| 9 | [QwQ: Reflect Deeply on the Boundaries of the Unknown](https://qwenlm.github.io/blog/qwq-32b-preview/) | Qwen reasoning-модель |
| 10 | [Gemini Thinking Documentation](https://ai.google.dev/gemini-api/docs/thinking) | Google reasoning API |
| 11 | [RLHF Book — Nathan Lambert](https://rlhfbook.com/) | Систематизация RLHF-подходов |

---

*Последнее обновление: 2025-12-24*

---

## Связь с другими темами

**[[llm-fundamentals]]** — Reasoning-модели (o1, o3, DeepSeek R1) строятся поверх архитектуры трансформеров, описанной в основах LLM. Понимание механизмов внимания, токенизации и генерации текста необходимо для осознания того, как chain-of-thought и test-time compute расширяют базовые возможности моделей. Reasoning — это не отдельная архитектура, а надстройка над фундаментальными LLM-механизмами, обученная через RLHF и специальные техники.

**[[models-landscape-2025]]** — Ландшафт моделей 2025 года показывает, какое место reasoning-модели занимают среди других семейств (GPT, Claude, Gemini, open-source). Сравнение бенчмарков, ценовой политики и доступности помогает выбрать правильную модель для конкретной задачи. Reasoning-модели особенно сильны в математике, кодинге и сложной логике, но уступают по скорости и стоимости обычным моделям.

**[[ai-api-integration]]** — Практическая интеграция reasoning-моделей через API имеет свои особенности: увеличенные таймауты из-за длительного «думания», специальные параметры (reasoning_effort, thinking budget), потоковый вывод reasoning-токенов. Понимание API-паттернов необходимо для эффективного использования reasoning-моделей в продакшене, включая fallback-стратегии и маршрутизацию между моделями.

---

---

---

## Проверь себя

> [!question]- Почему reasoning-модели (o1, o3, R1) дают качественный скачок на математике и coding, но не на простых задачах?
> Reasoning-модели используют test-time compute: дополнительные "reasoning tokens" для пошагового рассуждения, self-verification и backtracking. На простых задачах стандартные модели уже дают ~95% accuracy, дополнительное "думание" не помогает. На сложных задачах (multi-step reasoning, AIME) разница огромна: o3 87.7% на GPQA vs 53.6% GPT-4o.

> [!question]- Чем подход DeepSeek R1 (pure RL) принципиально отличается от OpenAI o1 (SFT + RL)?
> DeepSeek R1-Zero обучен через pure Reinforcement Learning (GRPO) без supervised fine-tuning -- reasoning capabilities появились эмергентно. OpenAI o1 использует SFT на chain-of-thought данных + RL. R1-Zero доказал, что reasoning может возникнуть только из RL, но имел проблемы (repetition, language mixing), которые решили добавлением cold-start data в финальной R1.

> [!question]- Когда Extended Thinking Claude предпочтительнее OpenAI o1 и наоборот?
> Claude Extended Thinking: видимые thinking tokens (прозрачность), настраиваемый budget_tokens, hybrid режим (быстрые ответы + thinking в одном разговоре), дешевле на длинных рассуждениях. o1/o3: скрытые thinking tokens (компактнее), лучше на competitive programming (2727 Elo Codeforces), первый на ARC-AGI (85%).

---

## Ключевые карточки

Что такое test-time compute и зачем?
?
Дополнительные вычисления во время inference (а не только training). Модель тратит "reasoning tokens" на пошаговое рассуждение, self-verification, backtracking. Больше compute = лучше accuracy (логарифмическая зависимость). Ключевой тренд 2024-2025.

Какие основные reasoning-модели в 2025?
?
OpenAI o1/o3 (closed, 87.7% GPQA), DeepSeek R1 (open-source MIT, 97.3% MATH-500), Claude Extended Thinking (настраиваемый budget), Gemini 2.5 Pro (#1 LMArena), QwQ (Qwen, open-source). Все используют chain-of-thought + test-time compute.

Что такое GRPO (Group Relative Policy Optimization)?
?
Метод RL-обучения DeepSeek R1 -- альтернатива PPO. Вместо value function, reward вычисляется относительно группы ответов. Проще, стабильнее, дешевле PPO. Позволил обучить reasoning без SFT данных (R1-Zero).

Когда использовать reasoning-модель vs стандартную?
?
Reasoning: сложная математика, scientific analysis, multi-step coding, competitive programming, планирование агентных workflow. Стандартная: простая генерация текста, classification, chatbot, задачи где скорость важнее accuracy. Reasoning модели в 10-100x дороже и медленнее.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[models-landscape-2025]] | Контекст reasoning-моделей среди всего ландшафта LLM |
| Углубиться | [[llm-fundamentals]] | Архитектурные основы: RLHF, DPO, MoE -- база для reasoning |
| Смежная тема | [[algorithms]] | Алгоритмическое мышление -- то, чему учатся reasoning-модели |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
