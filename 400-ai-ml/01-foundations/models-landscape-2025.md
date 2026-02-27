---
title: "Ландшафт LLM моделей 2025"
type: concept
status: published
tags:
  - topic/ai-ml
  - type/concept
  - level/intermediate
reading_time: 53
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - "[[llm-fundamentals]]"
  - "[[reasoning-models-guide]]"
  - "[[ai-api-integration]]"
---

# Ландшафт LLM моделей 2025

> Последнее обновление: Декабрь 2024
> Актуальность данных: Q4 2024 - Q1 2025

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Что такое токены, контекст, inference | [[llm-fundamentals]] |
| **Терминология AI** | Понимание benchmark'ов, метрик | [[ai-ml-overview-v2]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ✅ Да | Отличный обзор для понимания рынка |
| **AI Engineer** | ✅ Да | Выбор модели под конкретные задачи |
| **Tech Lead** | ✅ Да | Стратегическое планирование |
| **Product Manager** | ✅ Да | Понимание возможностей и ограничений |

### Терминология для новичков

> 💡 **LLM Landscape** = обзор всех доступных AI-моделей и их возможностей

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Closed-source** | Модель доступна только через API | **Аренда** — пользуешься, но не владеешь |
| **Open-weight** | Веса модели открыты для скачивания | **Покупка** — можешь запустить сам |
| **Benchmark** | Тест для сравнения моделей | **Экзамен** — кто лучше справляется с задачами |
| **Context Window** | Сколько текста модель "видит" | **Рабочая память** — чем больше, тем больше контекста |
| **MMLU** | Massive Multitask Language Understanding | **Универсальный тест знаний** — от математики до истории |
| **SWE-bench** | Benchmark по программированию | **Экзамен для программистов** — решение реальных issue |
| **MoE** | Mixture of Experts | **Консилиум** — разные эксперты для разных задач |
| **tok/s** | Токенов в секунду | **Скорость печати** — сколько слов генерирует за секунду |
| **Input/Output pricing** | Цена за входящие/исходящие токены | **Тариф** — платишь за вопросы и ответы отдельно |

---

## Зачем это нужно

### Проблема: выбор модели критичен для успеха проекта

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Расходы на API в 10x выше чем нужно | Неправильный выбор модели для задачи | Проект нерентабелен |
| Качество ответов неудовлетворительное | Модель не подходит для use case | Плохой UX, жалобы пользователей |
| Latency >5 секунд | Overkill reasoning model для простой задачи | Пользователи уходят |
| Код с багами, галлюцинации | Устаревшая или слабая модель | Technical debt, потеря доверия |

### Как правильный выбор модели решает проблемы

| Сценарий | Неправильный выбор | Правильный выбор |
|----------|-------------------|------------------|
| **Классификация чата** | GPT-4o ($2.50/M) | GPT-4o mini ($0.15/M) — 16x экономия |
| **Сложный coding** | Claude Haiku | Claude Sonnet — 77% SWE-bench |
| **Математика/reasoning** | GPT-4o | o1/o3 или DeepSeek R1 |
| **Длинные документы** | Модель с 8K context | Gemini/Claude с 1M+ context |
| **Budget-sensitive** | Закрытые API | Llama/Qwen self-hosted — 86% экономия |

---

## Оглавление

1. [Введение](#введение)
2. [OpenAI](#openai)
3. [Anthropic](#anthropic)
4. [Google DeepMind](#google-deepmind)
5. [Meta AI](#meta-ai)
6. [DeepSeek](#deepseek)
7. [Mistral AI](#mistral-ai)
8. [Alibaba Qwen](#alibaba-qwen)
9. [Сравнительные таблицы](#сравнительные-таблицы)
10. [Когда какую модель использовать](#когда-какую-модель-использовать)
11. [Источники](#источники)

---

## Теоретические основы

### Определение Foundation Model

> **Foundation Model** — предобученная на масштабных данных модель, которая может быть адаптирована к широкому спектру задач (Bommasani et al., 2021, Stanford CRFM). В отличие от task-specific моделей, foundation models обучаются один раз, а затем используются через fine-tuning, prompting или RAG.

### Таксономия архитектур LLM

| Архитектура | Примеры | Принцип | Применение |
|-------------|---------|---------|------------|
| **Dense Transformer** | GPT-4o, Claude Sonnet | Все параметры активны на каждом токене | Универсальные задачи |
| **Mixture of Experts (MoE)** | DeepSeek V3, Llama 4, Mixtral | Только часть параметров активна (sparse) | Масштаб при контроле стоимости |
| **Encoder-only** | BERT, RoBERTa | Bidirectional attention | Классификация, NER |
| **Encoder-Decoder** | T5, BART | Cross-attention | Перевод, суммаризация |
| **Decoder-only** | GPT, Claude, Llama | Causal (autoregressive) attention | Генерация текста |

### Эволюция законов масштабирования

Развитие подходов к масштабированию моделей прошло три ключевых этапа:

1. **Kaplan Scaling Laws** (2020, OpenAI) — потери модели снижаются по степенному закону при увеличении параметров, данных или вычислений. Приоритет отдавался увеличению числа параметров.
2. **Chinchilla Scaling** (Hoffmann et al., 2022, DeepMind) — показал, что оптимально увеличивать данные и параметры пропорционально (~20 токенов на параметр). Это привело к пересмотру подходов к обучению.
3. **Test-Time Compute Scaling** (2024, OpenAI o1) — новая парадигма: вместо масштабирования модели при обучении, масштабируется вычисление при [[reasoning-models-guide|inference через reasoning tokens]].

### Open Source vs Closed Source: теоретические trade-offs

> Дебат open vs closed source моделей имеет глубокие корни в теории инноваций. Согласно модели Раймонда (*"The Cathedral and the Bazaar"*, 1999), открытая разработка ускоряет инновации через crowdsourced improvements. В контексте LLM это проявляется: DeepSeek V3 (MIT license) обучен за $5.6M vs $100M+ для закрытых аналогов.

| Аспект | Closed Source | Open Weight | Теоретическое основание |
|--------|---------------|-------------|------------------------|
| **Безопасность** | Контролируемое alignment | Community audit | Linus's Law: "given enough eyes, all bugs are shallow" |
| **Стоимость** | API pricing | Self-hosting | Теория TCO: capex vs opex |
| **Кастомизация** | Ограничена API | Fine-tuning, merge | Гибкость vs vendor lock-in |
| **Приватность** | Данные уходят к провайдеру | Данные остаются локально | Data sovereignty requirements |
| **Воспроизводимость** | Невозможна | Полная | Научный метод |

### Бенчмарки: критический анализ

По данным Stanford HAI Report (2025), традиционные бенчмарки (MMLU, HumanEval) достигли "saturated" состояния — топовые модели показывают >90%, что затрудняет дифференциацию. Новое поколение бенчмарков:
- **GPQA** (graduate-level questions) — вопросы, сложные даже для экспертов
- **SWE-bench** — решение реальных GitHub issues
- **Humanity's Last Exam** — задачи, составленные экспертами специально для frontier моделей
- **LMArena (Chatbot Arena)** — Elo-рейтинг на основе human preferences (Zheng et al., 2023)

---

## Введение

2024-2025 годы стали переломными для индустрии больших языковых моделей. Мы наблюдаем несколько ключевых трендов:

**Конвергенция качества**: Разрыв между лидерами рынка стремительно сокращается. По данным Chatbot Arena, разница в Elo-рейтинге между топ-10 моделями сократилась с 11.9% в 2023 до 5.4% в начале 2025 года. К февралю 2025 разрыв между американскими и китайскими моделями сократился до 1.70%.

**Reasoning-модели**: Появился новый класс моделей с "цепочкой рассуждений" (chain-of-thought) - OpenAI o1/o3, Gemini Flash Thinking, DeepSeek R1. Они тратят больше времени на "размышления" перед ответом, используя "simulated reasoning".

**Открытый исходный код догоняет**: Open-source модели (DeepSeek, Llama, Qwen) достигли паритета с закрытыми моделями по многим бенчмаркам, предлагая 86% экономии на затратах и 7.3x лучшую ценовую эффективность.

**Взрывной рост контекстных окон**: От 4K токенов ChatGPT в 2022 до 10M токенов Llama 4 Scout в 2025. Рост примерно 30x в год. Эффективное использование контекста улучшилось ещё быстрее - 250x за 9 месяцев.

---

## OpenAI

### История компании

OpenAI была основана в 2015 году как некоммерческая исследовательская лаборатория Сэмом Альтманом, Илоном Маском и другими. Первоначальная миссия - обеспечить, чтобы AGI приносила пользу всему человечеству.

**Ключевые вехи:**
- **2018**: GPT-1 - первая модель серии
- **2020**: GPT-3 с 175B параметров произвел фурор
- **2022**: ChatGPT - самое быстрорастущее приложение в истории
- **2023**: GPT-4 - мультимодальная модель
- **2024**: GPT-4o (omni) в мае, o1-preview в сентябре, o3 в декабре
- **2025**: GPT-5, o3, GPT-4.1

### Линейка моделей

#### GPT-4o ("Omni")

**Релиз**: Май 2024, обновление декабрь 2024

**Характер модели**: Универсальный мультимодальный ассистент. GPT-4o - это "швейцарский нож" среди LLM: понимает текст, изображения, аудио и может генерировать ответы во всех этих модальностях. Ощущается как быстрый, уверенный собеседник.

**Ключевые характеристики**:
- Context window: 128K токенов
- Скорость: ~110 токенов/сек (в 3x быстрее GPT-4 Turbo)
- Время отклика на аудио: 232-320 мс (как у человека)
- Knowledge cutoff: Июнь 2024

**Benchmark достижения**:
- 88.7% на MMLU (улучшение на 2.2% vs GPT-4 Turbo)
- Значительные улучшения на GPQA (биология, физика, химия)
- Превосходит GPT-4 Turbo на non-English текстах

**Сильные стороны**:
- Нативная мультимодальность (текст + изображения + аудио + видео)
- Отличное следование инструкциям
- Real-time voice conversations
- Генерация изображений
- Очищенный frontend-код

**Слабые стороны**:
- На DROP benchmark (complex reasoning, arithmetic) GPT-4 Turbo всё ещё лучше
- Некоторые пользователи отмечают проблемы со следованием инструкциям vs GPT-4 Turbo
- Характерные фразы-маркеры AI-текста ("in today's ever-changing landscape", "let's dive in")

**API Pricing (за 1M токенов)**:
| Тип | Цена |
|-----|------|
| Input | $2.50 |
| Output | $10.00 |
| Cached Input | $1.25 |

#### GPT-4o mini

**Характер**: Быстрая и дешевая версия для простых задач. Идеальна для классификации, чат-ботов поддержки, простой генерации текста.

**API Pricing**:
| Тип | Цена |
|-----|------|
| Input | $0.15 |
| Output | $0.60 |

#### Серия o1/o3 (Reasoning Models)

**Релиз**: o1-preview сентябрь 2024, o1 GA декабрь 2024, o3 preview декабрь 2024, o3 GA апрель 2025

**Характер модели**: "Мыслители". Эти модели не спешат с ответом - они буквально "думают" от 5 секунд до нескольких минут, разбивая задачу на шаги, проверяя себя, меняя подходы. Это не баг, а фича.

**Как это работает**: Модели используют "reasoning tokens" помимо input/output токенов. После получения промпта модель переспрашивает себя, разбивает проблему на шаги. Этот процесс называется "simulated reasoning" или "chain-of-thought", но более продвинутый - с self-analysis и reflection.

**Ключевые достижения o3**:
- 87.7% на GPQA Diamond (экспертные вопросы по науке)
- 71.7% на SWE-bench Verified (решение реальных GitHub issues) vs 48.9% у o1
- 2727 Elo на Codeforces (o1 имел 1891)
- Первая модель, преодолевшая 85% на ARC AGI тесте

**Deliberative Alignment**: OpenAI использовала новый подход к безопасности - модели o1 и o3 "думают" о safety policy OpenAI во время inference.

**Когда использовать**:
- Сложные математические задачи
- Научный анализ
- Multi-step coding problems
- Планирование агентных workflow

**API Pricing (o1)**:
| Тип | Цена |
|-----|------|
| Input | $15.00 |
| Output | $60.00 |

#### GPT-5

**Релиз**: 2025

**Характер**: Новый флагман для сложных reasoning-задач и агентных workflow. Рекомендуется для high-accuracy reasoning, coding, и agentic workflows.

**API Pricing**:
| Тип | Цена |
|-----|------|
| Input | $1.25 |
| Output | $10.00 |

### Особенности экосистемы OpenAI

- **ChatGPT Plus**: $20/месяц - доступ к GPT-4o, o1, DALL-E, браузинг
- **API**: Pay-as-you-go, Batch API со скидкой 50%
- **Custom GPTs**: Создание специализированных ассистентов
- **Assistants API**: Function calling, file search, code interpreter
- **Realtime API**: Для голосовых приложений (8 голосов: alloy, ash, ballad, coral, echo, sage, shimmer, verse)
- **Web Search Tool**: Отдельная тарификация per 1000 calls + search content tokens

---

## Anthropic

### История компании

Anthropic была основана в 2021 году бывшими сотрудниками OpenAI, включая Дарио и Даниэлу Амодей. Компания позиционирует себя как "AI safety company" - они верят, что безопасность должна быть встроена в модели с самого начала.

Ключевой подход - Constitutional AI: модель обучается следовать набору принципов (конституции), что снижает необходимость в человеческой разметке и делает поведение более предсказуемым. Модели проходят независимую оценку UK AISI (Artificial Intelligence Safety Institute) перед релизом.

### Линейка моделей Claude

#### Claude 3.5 Sonnet

**Релиз**: Июнь 2024 (первая версия), Октябрь 2024 (обновление)

**Характер модели**: Если GPT-4o - это энергичный универсал, то Claude 3.5 Sonnet - вдумчивый эксперт. Он пишет более естественным языком, лучше понимает нюансы и юмор, реже использует клише. Особенно хорош для длинных текстов и кода.

**Ключевые характеристики**:
- Context window: 200K токенов (до 1M в long-context mode)
- Скорость: 2x быстрее Claude 3 Opus
- Лучшая vision-модель в линейке

**Benchmark достижения**:
- 64% на agentic coding evaluation (Opus - 38%)
- 49% на SWE-bench Verified (обновленная версия, ранее 33.4%)
- Превосходит Claude 3 Opus на GPQA (graduate-level reasoning)
- Лидер по MMLU, HumanEval

**Computer Use (октябрь 2024)**: Первая frontier-модель с публичным бета-доступом к "использованию компьютера" - Claude может смотреть на экран, двигать курсор, кликать, печатать. Направлять модель можно через API.

**Artifacts**: Динамическое рабочее пространство на claude.ai - код, документы, дизайны появляются в отдельном окне рядом с чатом. Можно редактировать и развивать в реальном времени.

**API Pricing (за 1M токенов)**:
| Тип | Цена |
|-----|------|
| Input | $3.00 |
| Output | $15.00 |
| Long-context (>200K) Input | $6.00 |
| Long-context Output | $22.50 |

#### Claude Opus 4.5

**Релиз**: 2025

**Характер**: Самая умная модель Anthropic. Для задач, где качество важнее скорости и стоимости.

**API Pricing**:
| Тип | Цена |
|-----|------|
| Input | $5.00 |
| Output | $25.00 |

#### Claude 4.1 Opus (Flagship)

**API Pricing**:
| Тип | Цена |
|-----|------|
| Input | $20.00 |
| Output | $80.00 |
| Thinking | $40.00 |

#### Claude Haiku

**Характер**: Самая быстрая и дешевая. Для высоконагруженных приложений, классификации, простых чат-ботов.

**API Pricing**:
| Тип | Цена |
|-----|------|
| Input | $0.25 |
| Output | $1.25 |

### Extended Thinking

**Что это**: Аналог o1 reasoning от Anthropic, доступный в Claude 3.7 Sonnet и Claude 4.

**Как работает**:
- Включается через `thinking` object с параметром `budget_tokens`
- Минимум 1024 токенов, рекомендуется начинать с минимума и увеличивать
- Claude генерирует hidden chain-of-thought (scratchpad), затем использует его для финального ответа
- Это НЕ отдельная модель - та же модель Claude просто может "думать дольше"
- Hybrid режим: модель может переключаться между быстрыми ответами и extended thinking в рамках одного разговора

**Результаты**:
- 80% на AIME 2024 (при 64K thinking budget, parallel mode)
- 96.2% на MATH 500
- 84.8% на GPQA overall, 96.5% на GPQA Physics
- Точность растёт логарифмически с увеличением thinking budget

**Важно**: Thinking-токены видны пользователю в сыром виде - это повышает доверие и помогает понять логику модели. Не summaries, а реальный internal reasoning.

### Особенности Anthropic

- **Нет бесплатного API** - только платный доступ
- **Batch API**: Скидка 50% для асинхронной обработки
- **Code Execution Tool**: 1,550 бесплатных часов/месяц, затем $0.05/час
- **Доступ через**: Anthropic API, Amazon Bedrock, Google Vertex AI
- **Claude.ai**: Бесплатный веб-интерфейс с лимитами, Claude Pro и Team для higher rate limits
- **Usage tiers**: Caps на monthly spend, rate limits на requests/minute и tokens/day

---

## Google DeepMind

### История

Google DeepMind образовался в 2023 году из слияния Google Brain и DeepMind. Компания имеет огромные вычислительные ресурсы и доступ к данным всего интернета через поиск Google. Transformer architecture, на которой построены ВСЕ современные LLM, была изобретена в Google.

После неудачного старта с Bard, Google нанёс ответный удар с Gemini 2.0 и 2.5, которые возглавили LMArena leaderboard.

### Линейка Gemini

#### Gemini 2.0 Flash

**Релиз**: Декабрь 2024 (experimental), Февраль 2025 (GA)

**Характер модели**: Быстрый и универсальный. Gemini 2.0 Flash создан для "agentic era" - он умеет не просто отвечать, а выполнять multi-step задачи автономно.

**Ключевые характеристики**:
- Context window: 1M токенов
- Outperforms Gemini 1.5 Pro на key benchmarks при 2x скорости
- Нативная мультимодальность: текст, изображения, видео, аудио на входе И выходе
- Встроенные инструменты: Google Search, Maps, code execution

**Уникальные возможности**:
- **Multimodal Live API**: Real-time аудио и видео взаимодействие
- **Native image generation**: Генерация изображений прямо в ответе с watermarking
- **Text-to-speech**: Контролируемая многоязычная озвучка (steerable TTS)
- **Deep Research**: AI-ассистент для исследований, создающий отчеты используя advanced reasoning и long context
- **Jules**: Экспериментальный AI coding agent для GitHub

#### Gemini 2.0 Flash Thinking

**Релиз**: Декабрь 2024

**Характер**: Reasoning-версия Flash с advanced reasoning capabilities. Анализирует задачи, думает на несколько шагов вперед. Превосходит OpenAI o1 на некоторых бенчмарках при меньших затратах.

#### Gemini 2.5 Pro

**Релиз**: 2025

**Характер**: Thinking-модель с лучшим балансом качества и стоимости. Изначально designed как thinking model.

**Ключевые достижения**:
- #1 на LMArena leaderboard (с значительным отрывом)
- 18.8% на Humanity's Last Exam
- 63.8% на SWE-bench Verified
- Context window: 1M токенов (2M в планах)
- Knowledge cutoff: Январь 2025 (на 7 месяцев свежее GPT-4o)

**Преимущества над GPT-4o**:
- Лучше с видео, документами и длинным контекстом
- Нативная интеграция с Google Workspace
- Дешевле при сравнимом качестве

**API Pricing (Gemini 2.5 Pro)**:
| Контекст | Input | Output |
|----------|-------|--------|
| До 128K | $1.25 | $5.00 |
| Более 128K | $2.50 | $10.00 |

### Google AI Studio

**Бесплатный tier**: Полноценная песочница для экспериментов. Важно: данные используются для обучения моделей на бесплатном плане.

**Pay-as-you-go**: Подключение Cloud Billing для production-использования. Данные НЕ используются для обучения.

**Tiering system**: Free -> Tier 1 -> Tier 2 -> Tier 3 (based on cumulative spending)

**Особенности**:
- Screen sharing с AI в реальном времени
- Генерация изображений бесплатно
- Возможность отключения safety filters
- Gemini 3 Flash доступен для бесплатного тестирования

**Image Output Pricing**:
- $120 / 1M tokens
- 1024x1024px (1K) to 2048x2048px (2K): ~$0.134/image
- Up to 4096x4096px (4K): ~$0.24/image

**Подписки для пользователей**:
- **Google AI Pro**: Доступ к 3 Pro, Deep Research, 1M context
- **Google AI Ultra**: Максимальные возможности + Veo 3.1 Fast video

---

## Meta AI

### История и философия

Meta (бывший Facebook) выбрала уникальную стратегию - open-source. Марк Цукерберг сравнивает это с тем, как Linux стал стандартом для cloud и mobile.

**Выгода для Meta:**
1. Сообщество улучшает модели бесплатно
2. Индустрия стандартизируется вокруг архитектуры Llama
3. Снижение затрат через экономию масштаба - inference на Llama 3.1 примерно 50% дешевле closed моделей типа GPT-4o
4. По словам Цукерберга, open-source позволяет "incorporate improvements back into Llama and products"

**Масштаб**: 650+ миллионов скачиваний Llama, ~1 миллион скачиваний в день. Meta AI на пути стать самым используемым AI-ассистентом с почти 600 миллионами MAU к концу 2024.

### Линейка Llama

#### Llama 3.3 70B

**Релиз**: Декабрь 2024

**Характер модели**: Лучшее соотношение качества и размера. Производительность сравнимая с Llama 3.1 405B при ~17% параметров.

**Ключевые характеристики**:
- Параметры: 70B
- Context window: 128K токенов
- Лицензия: Llama 3.3 Community License

**Benchmark результаты**:
- 92.1 на IFEval (следование инструкциям) - лучше Llama 3.1 405B (88.6), GPT-4o (84.6), близко к Claude 3.5 Sonnet (89.3)
- 86.0 на MMLU (0-shot, CoT)
- 88.4 на HumanEval (код)
- 77.0 на MATH (0-shot, CoT) - значительное улучшение vs Llama 3.1 70B (67.8)
- 91.1 на MGSM (мультиязычность) - близко к Claude 3.5 Sonnet (92.8)
- 50.5 на GPQA Diamond - немного позади Claude 3.5 Sonnet (65.0)

**Инференс**: До 276 токенов/сек на Groq - самый быстрый провайдер.

**Стоимость**: 88% дешевле в развертывании чем Llama 3.1 405B.

#### Llama 4 Scout

**Релиз**: Апрель 2025

**Характер**: Эффективная мультимодальная модель для edge-развертывания. Первая open-weight natively multimodal модель.

**Архитектура**:
- MoE (Mixture of Experts): 109B total / 17B active параметров
- 16 экспертов, 1 эксперт активен на токен
- Early fusion multimodality
- Interleaved global attention (без RoPE) и chunked local attention (с RoPE) в соотношении 1:3
- Запускается на одном H100 GPU (Int4)

**Революционный context window**: 10 миллионов токенов - industry-leading.

**Training**: До 40 триллионов токенов, 200 языков, fine-tuning на 12 языках включая арабский, испанский, немецкий, хинди.

**Результаты**: Превосходит Gemma 3, Gemini 2.0 Flash-Lite, Mistral 3.1.

#### Llama 4 Maverick

**Релиз**: Апрель 2025

**Характер**: Флагман для максимальной производительности. Generalist для chat, reasoning, image understanding, code.

**Архитектура**:
- MoE: 400B total / 17B active параметров
- 128 экспертов, 1 активен на токен
- Context window: 1M токенов

**Benchmark результаты**:
- 80.5% на MMLU Pro
- 69.8% на GPQA Diamond
- Превосходит GPT-4o и Gemini 2.0 Flash
- Сравним с DeepSeek V3 на reasoning и coding при менее чем половине активных параметров

**Pricing через провайдеров**: $0.19-0.49 / 1M токенов

#### Llama 4 Behemoth (в разработке)

**Статус**: В процессе обучения, teacher-модель для Scout и Maverick.

**Архитектура**:
- ~2 триллиона total параметров
- 288B активных параметров
- 16 экспертов

### Llama Impact

Meta запустила программы поддержки социально значимых проектов:
- **Llama Impact Hackathon (London)**: 200+ разработчиков, 56 команд, здравоохранение, clean energy, social mobility
- **Llama Impact Grants** (сентябрь 2024): Гранты для healthcare, agriculture, education

### Enterprise Adoption

- **Arcee AI**: 47% снижение TCO vs closed LLMs через fine-tuning
- **Block (Cash App)**: Интеграция в customer support с сохранением data privacy
- **Accenture**: Chatbot для intergovernmental body на AWS
- **Spotify**: Contextualized recommendations, artist discovery
- **LinkedIn**: Comparable или лучше качество vs commercial models при значительно меньших costs и latencies

### Где запускать Llama

- **Hugging Face**: Скачивание весов
- **Ollama**: Локальный запуск
- **Together AI, Groq, Fireworks**: API-провайдеры
- **AWS, Azure, GCP**: Облачные развертывания
- **vLLM**: Для production inference

---

## DeepSeek

### История компании

DeepSeek - китайский стартап, ставший сенсацией 2024-2025 годов. Основан в 2023, привлёк внимание когда DeepSeek R1 показал 96.3% на AIME (олимпиадная математика) против 79.2% у OpenAI o1.

**Прорыв в эффективности**: Модели мирового уровня обучены за $5-6 миллионов - в 100 раз меньше конкурентов. DeepSeek V3 требует только 2.788M H800 GPU-часов для полного обучения, pre-training на 1T токенов занимает всего 3.7 дня на кластере из 2048 H800.

### Линейка моделей

#### DeepSeek-V3

**Релиз**: Декабрь 2024

**Характер модели**: Экстремально эффективный универсал. Доказал, что можно достичь топового качества с меньшими ресурсами.

**Архитектура**:
- MoE: 671B total / 37B active параметров
- Multi-head Latent Attention (MLA)
- DeepSeekMoE architecture
- Context window: 128K токенов

**Benchmark результаты**:
- 88.5 на MMLU (лучше всех open-source)
- 75.9 на MMLU-Pro
- 59.1 на GPQA
- State-of-the-art на MATH-500 среди non-long-CoT моделей, даже превосходит o1-preview
- Top performance на LiveCodeBench (coding competition)
- Сравним с GPT-4o и Claude-3.5-Sonnet

**Лицензия**: MIT (fully open-source)

#### DeepSeek-R1

**Релиз**: Январь 2025

**Характер модели**: Reasoning-модель, обученная преимущественно через Reinforcement Learning без supervised fine-tuning (первый такой подход в индустрии).

**Ключевое открытие**: DeepSeek-R1-Zero показал, что reasoning capabilities (self-verification, reflection, long CoT) могут "эмергентно" появиться из pure RL без human-labelled reasoning trajectories.

**Архитектура**:
- 671B total / 37B active параметров
- Context window: 164K токенов
- Проблемы R1-Zero (endless repetition, poor readability, language mixing) решены добавлением cold-start data

**Training**: GRPO (Group Relative Policy Optimization) вместо традиционного PPO.

**Benchmark результаты**:
- ~90-91% на MMLU
- 97.3% на MATH-500
- ~79.8% на AIME
- 2029 Elo на Codeforces

**Дистилляция**: Доступны distilled-версии: 1.5B, 7B, 8B, 14B, 32B, 70B на базе Qwen2.5 и Llama3. Distilled 14B превосходит QwQ-32B-Preview.

**Обновление R1-0528** (май 2025):
- Reasoning tokens выросли с 12K до 23K на вопрос AIME
- Приближается к OpenAI o3 и Gemini 2.5 Pro

**DeepSeek-V3.1** (август 2025): Hybrid модель, объединяющая V3 и R1, 671B параметров (37B active), context до 128K.

### Преимущество в стоимости

| Метрика | DeepSeek | OpenAI |
|---------|----------|--------|
| Стоимость 100M токенов | ~$274 | ~$1,300 (GPT-4o) |
| Та же нагрузка | $10 | $270 |
| Обучение модели | $5-6M | $100M+ |

**27x дешевле** при сравнимом качестве! Processing times 0.5 sec vs 2 sec у OpenAI, 4x faster.

**Context caching**: Механизм кэширования для повторяющихся запросов - уникальная особенность, еще больше снижающая затраты.

### API Pricing

| Модель | Input | Output |
|--------|-------|--------|
| DeepSeek V3 | $0.27 | $1.10 |
| DeepSeek R1 | $0.55 | $2.19 |

### Ограничения

- **Text-only**: Нет vision, audio, video
- **Китайские сервера**: Возможные задержки, геополитические риски
- **Alignment**: Менее "осторожный" чем западные модели
- **Цензура**: Определённые политические темы обрабатываются иначе

---

## Mistral AI

### История компании

Французский стартап, основанный в 2023 году бывшими сотрудниками Meta и Google DeepMind. За год стал самым ценным AI-стартапом Европы. Философия: высокопроизводительные модели с открытыми весами, ориентация на enterprise.

### Линейка моделей

#### Mistral Large 2

**Релиз**: Июль 2024

**Характер модели**: Enterprise-класс для сложных задач. Позиционируется как европейская альтернатива GPT-4.

**Ключевые характеристики**:
- Параметры: 123B
- Context window: 128K токенов
- Single-node inference

**Возможности**:
- 80+ языков программирования
- Поддержка дюжины естественных языков (французский, немецкий, испанский, итальянский, португальский, арабский, хинди, русский, китайский, японский, корейский)
- Advanced function calling
- Значительно лучше в code generation, mathematics, reasoning vs predecessor

#### Mistral NeMo

**Релиз**: Июль 2024 (совместно с NVIDIA)

**Характер модели**: Лучшее в своем размере. Drop-in replacement для Mistral 7B с кардинальными улучшениями.

**Ключевые характеристики**:
- Параметры: 12B
- Context window: 128K токенов
- Лицензия: Apache 2.0

**Преимущества**:
- Обучена с quantization awareness - FP8 без потери качества
- Новый токенизатор Tekken на базе Tiktoken (100+ языков)
- 30% эффективнее на сжатии кода и европейских языков
- SOTA в своем размерном классе по reasoning, world knowledge, coding accuracy
- Лучше на multi-turn conversations vs Mistral 7B

#### Специализированные модели

- **Codestral** (январь 2025): Оптимизирована для кода
- **Pixtral** (сентябрь 2024): 12B мультимодальная модель, image understanding + text
- **Codestral Mamba** (июль 2024): Первая open-source Mamba 2 architecture
- **Mathstral 7B** (июль 2024): Для математических вычислений
- **Frontier multimodal** (май 2025): Новейшая frontier-class модель

### Рекомендации по выбору от Mistral

| Задача | Рекомендуемая модель |
|--------|---------------------|
| Простые (классификация, поддержка, text gen) | Mistral NeMo |
| Средние (извлечение данных, саммаризация, emails) | Mistral Small |
| Сложные (RAG, агенты, code gen, synthetic text) | Mistral Large |

---

## Alibaba Qwen

### История

Qwen (Tongyi Qianwen) - линейка LLM от Alibaba Cloud. Активно инвестирует в AI, Qwen стал одним из сильнейших open-source решений с 300+ миллионами скачиваний.

### Линейка моделей

#### Qwen 2.5

**Релиз**: Сентябрь 2024

**Характер серии**: Комплексное решение на любой размер. От 0.5B до 72B параметров, плюс специализированные версии для кода (Qwen2.5-Coder) и математики (Qwen2.5-Math).

**Данные обучения**: 18 триллионов токенов.

**Размерный ряд**: 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B

**Context window**: 128K токенов (генерация до 8K)

#### Qwen 2.5-72B-Instruct

**Характер**: Флагман серии, конкурент GPT-4.

**Benchmark результаты**:
- Превосходит Llama-3.1-405B на MMLU-redux, MATH, MBPP, MultiPL-E, LiveCodeBench, Arena-Hard, MTBench
- 5x меньше параметров при сравнимом качестве
- 83.1% на MATH (vs 69% у Qwen2)
- 81.2 Arena-Hard (vs 48.1 у Qwen2)
- 9.35 MT-Bench (vs 9.12 у Qwen2)
- 55.5 на LiveCodeBench, 75.1 на MultiPL-E, 88.2 на MBPP

#### Qwen 2.5 Coder

**Характер**: SOTA open-source модель для кода.

**Qwen 2.5-Coder-32B достижения**:
- Сравним с GPT-4o по качеству кода
- 73.7% на Aider code editing benchmark (#4 общий рейтинг, после Claude 3.5 Sonnet)
- Лучший среди open-source на EvalPlus, LiveCodeBench, BigCodeBench
- Работает на Mac локально

#### Qwen 2.5 Max

**Релиз**: Январь 2025

**Архитектура**: Масштабная MoE модель, 20T+ токенов обучения, SFT + RLHF post-training.

**Результаты**: Превосходит DeepSeek V3 на Arena-Hard, LiveBench, LiveCodeBench, GPQA-Diamond. Competitive на MMLU-Pro.

#### Qwen3

**Qwen3-235B-A22B** (flagship):
- 235B total, 22B active (MoE)
- Apache 2.0 (fully open-weight!)
- Сравним с GPT-5, DeepSeek-V3, Claude Opus 4

---

## Сравнительные таблицы

### Стоимость API (за 1M токенов, декабрь 2024)

| Модель | Input | Output | Примечание |
|--------|-------|--------|------------|
| **OpenAI** |
| GPT-4o | $2.50 | $10.00 | Универсал |
| GPT-4o mini | $0.15 | $0.60 | Для простых задач |
| o1 | $15.00 | $60.00 | Reasoning |
| GPT-5 | $1.25 | $10.00 | 2025 flagship |
| **Anthropic** |
| Claude Opus 4.5 | $5.00 | $25.00 | Максимум качества |
| Claude Sonnet 3.5 | $3.00 | $15.00 | Лучший баланс |
| Claude Haiku | $0.25 | $1.25 | Скорость |
| Claude 4.1 Opus | $20.00 | $80.00 | Flagship |
| **Google** |
| Gemini 2.5 Pro (<128K) | $1.25 | $5.00 | Выгодный |
| Gemini 2.5 Pro (>128K) | $2.50 | $10.00 | Long context |
| Gemini Flash-Lite | $0.075 | $0.30 | Ultra-budget |
| **DeepSeek** |
| DeepSeek V3 | $0.27 | $1.10 | Best value |
| DeepSeek R1 | $0.55 | $2.19 | Reasoning |
| **Meta Llama** |
| Llama 4 Maverick | $0.19 | $0.49 | Через провайдеров |

### Context Window

| Модель | Context Window |
|--------|---------------|
| Llama 4 Scout | 10M токенов |
| Magic LTM-2-Mini | 100M токенов |
| Gemini 2.5 Pro | 1M-2M токенов |
| Claude Sonnet (long) | 1M токенов |
| GPT-4.1 | 1M токенов |
| Llama 4 Maverick | 1M токенов |
| GPT-4o | 128K токенов |
| Llama 3.3 70B | 128K токенов |
| DeepSeek V3 | 128K токенов |
| Mistral Large 2 | 128K токенов |
| Qwen 2.5 | 128K токенов |

### Benchmark сравнение (примерные значения)

| Модель | MMLU | GPQA | HumanEval | MATH | SWE-bench |
|--------|------|------|-----------|------|-----------|
| GPT-4o | 88.7 | 53.6 | 90.2 | 76.6 | ~60% |
| o3 | - | 87.7 | - | - | 71.7% |
| Claude 3.5 Sonnet | 88.9 | 65.0 | 92.0 | 78.3 | 49% |
| Gemini 2.5 Pro | 89.2 | 67.0 | 90.0 | 82.0 | 63.8% |
| DeepSeek V3 | 88.5 | 59.1 | 89.0 | 84.0 | ~65% |
| DeepSeek R1 | 90-91 | - | - | 97.3 | - |
| Llama 3.3 70B | 86.0 | 50.5 | 88.4 | 77.0 | - |
| Llama 4 Maverick | 80.5 (Pro) | 69.8 | - | - | ~60% |
| Qwen 2.5-72B | 86.1 | - | 88.0 | 83.1 | - |

**Примечание**: MMLU и HumanEval уже считаются "saturated" бенчмарками. Новые бенчмарки (GPQA, SWE-bench, Humanity's Last Exam) более показательны.

---

## Когда какую модель использовать

### По задаче

| Задача | Лучший выбор | Альтернатива |
|--------|--------------|--------------|
| **Кодинг (сложный)** | Claude 3.5 Sonnet | DeepSeek V3, Qwen Coder |
| **Кодинг (простой)** | GPT-4o mini | Claude Haiku |
| **Математика/Наука** | DeepSeek R1, o1/o3 | Gemini 2.5 Pro |
| **Креативное письмо** | Claude Sonnet | GPT-4o |
| **Анализ документов** | Gemini 2.5 Pro | Claude Sonnet |
| **Мультимодал (видео)** | Gemini 2.0 Flash | Llama 4 Maverick |
| **Real-time voice** | GPT-4o Realtime | Gemini Live API |
| **RAG/Enterprise** | Mistral Large | GPT-4o |
| **Edge/Mobile** | Llama 4 Scout | Qwen 2.5 (small sizes) |
| **Бюджетные задачи** | DeepSeek V3 | Gemini Flash-Lite |
| **Multilingual (119 языков)** | Qwen3 | Llama 4 |

### По бюджету

| Бюджет | Модели |
|--------|--------|
| **Минимум затрат** | DeepSeek V3, Gemini Flash-Lite, self-hosted Llama |
| **Оптимальный баланс** | Claude Sonnet, GPT-4o, Gemini 2.5 Pro |
| **Максимум качества** | Claude Opus, o1/o3, Gemini 2.5 Pro |

### По требованиям

| Требование | Рекомендация |
|------------|--------------|
| **Приватность данных** | Self-hosted Llama, DeepSeek, Qwen |
| **Европейские данные** | Mistral (французская юрисдикция) |
| **Интеграция с Google** | Gemini |
| **Максимальный контекст** | Llama 4 Scout (10M), Gemini (2M) |
| **Safety-critical** | Claude (Constitutional AI) |
| **True open-source (Apache 2.0)** | Qwen3, Mistral NeMo |

### Характеры моделей (субъективно)

| Модель | "Личность" |
|--------|------------|
| **GPT-4o** | Энергичный универсал, любит буллет-поинты, иногда overconfident |
| **Claude Sonnet** | Вдумчивый эксперт, естественный язык, признаёт ограничения |
| **Gemini Pro** | Эрудированный, фактологичный, более "сухой" |
| **DeepSeek** | Прямолинейный, эффективный, дерзкий оптимизатор |
| **Llama** | Гибкий, настраиваемый, демократизатор |

---

## Источники

### Теоретические основы
- Bommasani, R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258.
- Kaplan, J. et al. (2020). *Scaling Laws for Neural Language Models*. arXiv:2001.08361.
- Hoffmann, J. et al. (2022). *Training Compute-Optimal Large Language Models* (Chinchilla). arXiv:2203.15556.
- Zheng, L. et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
- DeepSeek-AI (2025). *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL*. arXiv:2501.12948.
- DeepSeek-AI (2024). *DeepSeek-V3 Technical Report*. arXiv:2412.19437.
- Raymond, E. S. (1999). *The Cathedral and the Bazaar*. O'Reilly Media.

### Практические руководства
- [OpenAI Models Docs](https://platform.openai.com/docs/models)
- [Anthropic Claude 3.5](https://www.anthropic.com/news/claude-3-5-sonnet)
- [Google Gemini 2.0](https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/)
- [Meta Llama 4](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
- [Qwen 2.5 Blog](https://qwenlm.github.io/blog/qwen2.5-llm/)
- [Mistral Docs](https://docs.mistral.ai/getting-started/models)
- [Artificial Analysis Leaderboard](https://artificialanalysis.ai/leaderboards/models)
- [Stanford HAI 2025 Report](https://hai.stanford.edu/ai-index/2025-ai-index-report/technical-performance)
- [HuggingFace Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)

---

*Последнее обновление: 2024-12-28*

---

[[ai-engineering-moc|← AI Engineering MOC]] | [[llm-fundamentals|← LLM Fundamentals]] | [[prompt-engineering-masterclass|Prompts →]]

---

## Связь с другими темами

**[[llm-fundamentals]]** — Фундаменты LLM объясняют архитектурные различия между моделями, описанными в данном ландшафте. Почему DeepSeek использует MoE с 671B/37B параметрами? Чем GQA в Llama отличается от стандартного MHA? Зачем нужен RoPE вместо абсолютного позиционного кодирования? Без понимания этих концепций сравнение моделей сводится к сопоставлению бенчмарков без осознания причин различий.

**[[reasoning-models-guide]]** — Reasoning-модели (o1, o3, DeepSeek R1, Claude Extended Thinking) — один из ключевых трендов 2024-2025, упомянутых в данном обзоре. Гайд по reasoning моделям углубляется в механику test-time compute, GRPO, self-correction и объясняет, почему эти модели в 10-100x дороже стандартных, но дают качественный скачок на задачах математики, кодинга и научного анализа.

**[[ai-api-integration]]** — Практическая интеграция с моделями через API — следующий шаг после выбора модели. Гайд по API-интеграции описывает форматы запросов, обработку streaming-ответов, retry-логику, управление rate limits и стоимостью для каждого провайдера (OpenAI, Anthropic, Google, DeepSeek), упомянутого в данном ландшафте.

---

## Проверь себя

> [!question]- Ваш проект требует обработки документов на 5 языках с бюджетом $500/месяц на API. Какую модель выберете и почему?
> DeepSeek V3 ($0.27/1M input) или Gemini 2.5 Pro ($1.25/1M input). DeepSeek дает наилучшее соотношение цена/качество (27x дешевле GPT-4o при сопоставимом качестве). Для мультиязычности также подойдет self-hosted Qwen 2.5-72B. Gemini 2.5 Pro -- если нужен 1M контекст для длинных документов.

> [!question]- Почему reasoning-модели (o1, o3, DeepSeek R1) значительно дороже стандартных и когда их использование оправдано?
> Reasoning-модели используют "reasoning tokens" -- дополнительные вычисления на "размышления" перед ответом (5 секунд до нескольких минут). o1 стоит $15/$60 за 1M input/output vs $2.50/$10 у GPT-4o. Оправдано для сложной математики, научного анализа, multi-step coding, где стандартные модели дают ошибки.

> [!question]- Чем объясняется прорыв DeepSeek -- обучение модели мирового уровня за $5-6M вместо $100M+?
> Архитектурные инновации: MoE с 671B total / 37B active параметров, Multi-head Latent Attention (MLA), эффективное использование H800 GPU. Pre-training на 1T токенов за 3.7 дня на кластере из 2048 GPU. Также MIT лицензия позволяет community-оптимизации.

> [!question]- В каких сценариях open-source модели уже конкурируют с закрытыми, а в каких пока нет?
> Конкурируют: general reasoning (DeepSeek R1 vs o1), coding (Qwen Coder vs GPT-4o), multilingual (Llama 3.3 70B). Пока уступают: real-time voice (GPT-4o Realtime), computer use (Claude), native multimodal output (Gemini 2.0 Flash), максимальный уровень safety (Claude Constitutional AI).

---

## Ключевые карточки

Какие модели выбрать для coding задач?
?
Сложный coding: Claude 3.5 Sonnet (77% SWE-bench) или DeepSeek V3. Простой coding: GPT-4o mini или Claude Haiku. Open-source: Qwen 2.5-Coder-32B (73.7% Aider benchmark, сравним с GPT-4o).

Какова стоимость основных моделей за 1M токенов (input/output)?
?
GPT-4o: $2.50/$10. Claude Sonnet: $3/$15. Gemini 2.5 Pro: $1.25/$5. DeepSeek V3: $0.27/$1.10. GPT-4o mini: $0.15/$0.60. o1: $15/$60. DeepSeek R1: $0.55/$2.19.

Что такое context window и как он изменился?
?
Максимальное количество токенов, которые модель обрабатывает за раз. Рост ~30x в год: GPT-3.5 (4K, 2022) -> GPT-4o (128K) -> Gemini 2.5 Pro (1-2M) -> Llama 4 Scout (10M, 2025). Длинный контекст дороже из-за O(n^2) сложности attention.

Чем MoE модели отличаются от dense?
?
MoE (Mixture of Experts) активирует только часть параметров на каждый токен. Пример: DeepSeek V3 -- 671B total, но 37B active. Преимущества: качество большой модели при стоимости маленькой. Недостаток: все параметры должны быть в RAM.

Какие тренды определяют ландшафт LLM в 2024-2025?
?
Конвергенция качества (разрыв Elo топ-10 с 11.9% до 5.4%), reasoning-модели (o1, o3, R1), open-source паритет (DeepSeek, Llama, Qwen конкурируют с закрытыми), взрывной рост context window (30x/год), MoE архитектуры.

Когда выбрать Claude вместо GPT-4o?
?
Claude лучше для: coding (77% SWE-bench), длинных документов (200K-1M контекст), автономных агентов (Computer Use), safety-critical приложений (Constitutional AI). GPT-4o лучше для: мультимодальности (аудио, real-time voice), экосистемы (plugins, custom GPTs), скорости (110 tok/s).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ai-api-integration]] | Научиться практически интегрировать выбранную модель через API |
| Углубиться | [[reasoning-models-guide]] | Детальное понимание reasoning-моделей -- ключевого тренда 2024-2025 |
| Смежная тема | [[ai-cost-optimization]] | Оптимизация затрат при работе с LLM API в production |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
