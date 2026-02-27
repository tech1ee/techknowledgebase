---
title: "AI/ML Engineering: Карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: published
confidence: high
tags:
  - topic/ai-ml
  - ai-engineering
  - type/moc
related:
  - "[[architecture-overview]]"
  - "[[cloud-overview]]"
  - "[[programming-overview]]"
reading_time: 10
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AI/ML Engineering: Карта раздела

> От prompt engineering до production AI systems — практическое руководство по современному AI Engineering

---

## TL;DR

- **AI Engineering** — создание продуктов на базе LLM и других AI моделей
- **Ключевые навыки:** Prompt engineering, RAG, fine-tuning, evaluation, production deployment
- **2024-2025 тренды:** Agents, multimodal AI, reasoning models, structured outputs
- **Главный инсайт:** 90% задач решаются через prompt engineering + RAG, fine-tuning нужен редко

---

## Теоретические основы

> **AI Engineering** — инженерная дисциплина создания production-ready приложений на базе foundation models (Bommasani et al., 2021). В отличие от ML Engineering (обучение моделей) и Data Science (анализ данных), AI Engineering фокусируется на интеграции предобученных LLM в продукты.

### Место AI Engineering в ландшафте дисциплин

| Дисциплина | Фокус | Ключевые задачи | Основатели/Источники |
|------------|-------|-----------------|---------------------|
| **Data Science** | Анализ данных | Статистика, визуализация, гипотезы | Tukey (1962), EDA |
| **ML Engineering** | Обучение моделей | Training, MLOps, feature engineering | Sculley et al. (2015), ML debt |
| **AI Engineering** | Интеграция LLM | RAG, agents, prompt engineering, API | Huyen (2022), Karpathy (2023) |

### Иерархия подходов к адаптации

> **Правило 90/10:** По оценкам индустрии (Karpathy, 2023; Anthropic, 2024), ~90% задач решаются через prompt engineering + RAG, и только ~10% требуют fine-tuning или pre-training. Это фундаментальный принцип AI Engineering.

```
PRE-TRAINING → FINE-TUNING → RAG → PROMPT ENGINEERING
    │               │          │           │
 Максимум       Средние      Дни       Минуты
 ресурсов       ресурсы
 (месяцы)       (часы-дни)
```

### Ключевые теоретические работы

- **Vaswani et al. (2017)** — архитектура Transformer, основа всех современных LLM
- **Bommasani et al. (2021)** — концепция foundation models и их влияние на AI
- **Russell & Norvig (2020)** — AI: A Modern Approach, системный взгляд на AI
- **Jurafsky & Martin (2023)** — Speech and Language Processing, основа NLP

**Связи:** [[llm-fundamentals]] (как работают LLM), [[ai-engineering-intro]] (введение в AI Engineering), [[models-landscape-2025]] (обзор моделей)

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| С чего начать? | [[ai-engineering-intro]] → [[ai-engineer-roadmap]] |
| Как писать промпты? | [[rag-and-prompt-engineering]] |
| Нужны AI агенты? | [[ai-agents-autonomous-systems]] |
| Fine-tuning vs RAG? | [[ai-fine-tuning-adaptation]] |
| Как измерить качество? | [[ai-evaluation-metrics]] |
| Как деплоить в прод? | [[ai-production-systems]] |
| Какие инструменты? | [[ai-engineer-tech-stack]] |

---

## Ландшафт AI Engineering 2025

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI ENGINEERING LANDSCAPE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FOUNDATION MODELS                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   OpenAI    │  │  Anthropic  │  │   Google    │  │    Meta     │        │
│  │  GPT-4o     │  │  Claude 3   │  │  Gemini 2   │  │  Llama 3    │        │
│  │  o1/o3      │  │  Opus/Sonnet│  │  Flash      │  │  Open       │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│         └────────────────┴────────────────┴────────────────┘                │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ADAPTATION TECHNIQUES                          │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │   │
│  │  │   Prompting   │  │      RAG      │  │  Fine-tuning  │           │   │
│  │  │               │  │               │  │               │           │   │
│  │  │ • Zero-shot   │  │ • Embeddings  │  │ • Full FT     │           │   │
│  │  │ • Few-shot    │  │ • Vector DB   │  │ • LoRA/QLoRA  │           │   │
│  │  │ • Chain-of-   │  │ • Chunking    │  │ • Adapters    │           │   │
│  │  │   Thought     │  │ • Reranking   │  │               │           │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘           │   │
│  │                                                                     │   │
│  │  Сложность: ▓░░░░░░░░░  ▓▓▓▓░░░░░░   ▓▓▓▓▓▓▓▓▓▓                   │   │
│  │  Эффект:    ▓▓▓▓▓▓▓▓░░  ▓▓▓▓▓▓▓▓▓░   ▓▓▓▓▓▓▓░░░                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        AI APPLICATIONS                              │   │
│  │                                                                     │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │   │
│  │  │Chatbots │  │ Agents  │  │ Search  │  │ Content │  │Analytics│  │   │
│  │  │   Q&A   │  │AutoGPT  │  │Semantic │  │  Gen    │  │  Code   │  │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Терминология

| Термин | Значение |
|--------|----------|
| **LLM** | Large Language Model — большая языковая модель |
| **RAG** | Retrieval-Augmented Generation — поиск + генерация |
| **Fine-tuning** | Дообучение модели на специфичных данных |
| **Embedding** | Векторное представление текста |
| **Prompt** | Инструкция/запрос к модели |
| **Token** | Минимальная единица текста для LLM (~4 символа) |
| **Context window** | Максимальный размер входа модели |
| **Inference** | Процесс генерации ответа моделью |
| **Agent** | AI система с возможностью использовать инструменты |
| **Hallucination** | Генерация правдоподобной, но неверной информации |

---

## Структура раздела

### Foundation — Введение в AI Engineering

| Статья | Описание |
|--------|----------|
| [[ai-engineering-intro]] | Что такое AI Engineering, отличие от ML Engineering |
| [[ai-engineer-roadmap]] | Путь обучения, навыки, карьера |
| [[ai-engineer-tech-stack]] | Инструменты: LangChain, LlamaIndex, Vector DBs |

### Core Skills — Основные техники

| Статья | Описание |
|--------|----------|
| [[rag-and-prompt-engineering]] | Промпты, RAG архитектура, best practices |
| [[ai-fine-tuning-adaptation]] | LoRA, QLoRA, когда fine-tuning нужен |
| [[ai-agents-autonomous-systems]] | Tool use, planning, multi-agent systems |

### Production — Продакшн системы

| Статья | Описание |
|--------|----------|
| [[ai-evaluation-metrics]] | Метрики качества, RAGAS, human eval |
| [[ai-production-systems]] | Serving, scaling, cost optimization |

---

## Когда что использовать

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     DECISION TREE: ADAPTATION METHOD                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Задача требует свежих/специфичных данных?                                 │
│                    │                                                        │
│         ┌─────────┴─────────┐                                              │
│         │ ДА               │ НЕТ                                           │
│         ▼                   ▼                                               │
│    ┌─────────┐        Нужен особый стиль/формат?                           │
│    │   RAG   │                   │                                         │
│    └─────────┘        ┌─────────┴─────────┐                                │
│                       │ ДА               │ НЕТ                             │
│                       ▼                   ▼                                 │
│                  Есть >1000         ┌──────────────┐                       │
│                  примеров?          │   Prompting  │                       │
│                       │             │  (few-shot)  │                       │
│            ┌─────────┴─────────┐    └──────────────┘                       │
│            │ ДА               │ НЕТ                                        │
│            ▼                   ▼                                            │
│       ┌─────────┐        ┌──────────────┐                                  │
│       │Fine-tune│        │   Prompting  │                                  │
│       │(LoRA)   │        │  (few-shot)  │                                  │
│       └─────────┘        └──────────────┘                                  │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Сравнение методов

| Метод | Когда использовать | Плюсы | Минусы |
|-------|-------------------|-------|--------|
| **Prompting** | Большинство задач | Быстро, дёшево, гибко | Ограничен контекстом |
| **RAG** | Нужны актуальные данные | Свежие данные, transparency | Сложность системы |
| **Fine-tuning** | Специфичный формат/стиль | Качество на узкой задаче | Дорого, сложно, риск overfitting |
| **Agents** | Многошаговые задачи | Автономность, tool use | Непредсказуемость, стоимость |

---

## Ключевые метрики AI систем

| Метрика | Что измеряет | Целевое значение |
|---------|--------------|------------------|
| **Latency** | Время ответа | < 2s для чатботов |
| **Cost per query** | Стоимость запроса | < $0.01 для массовых |
| **Accuracy** | Правильность ответов | > 90% для критичных |
| **Hallucination rate** | Частота галлюцинаций | < 5% |
| **User satisfaction** | Удовлетворённость | > 4.0/5.0 |

---

## Архитектура типичной AI системы

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION AI SYSTEM ARCHITECTURE                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                                                          │
│  │    User      │                                                          │
│  └──────┬───────┘                                                          │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────┐     ┌──────────────┐                                    │
│  │   API GW     │────▶│   Rate       │                                    │
│  │   (Auth)     │     │   Limiter    │                                    │
│  └──────┬───────┘     └──────────────┘                                    │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                        AI Orchestration Layer                     │     │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐               │     │
│  │  │  Prompt    │   │    RAG     │   │   Agent    │               │     │
│  │  │  Manager   │   │  Pipeline  │   │  Runtime   │               │     │
│  │  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘               │     │
│  │        │                │                │                       │     │
│  │        └────────────────┴────────────────┘                       │     │
│  │                         │                                        │     │
│  └─────────────────────────┼────────────────────────────────────────┘     │
│                            │                                               │
│         ┌──────────────────┼──────────────────┐                           │
│         ▼                  ▼                  ▼                            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                  │
│  │  Vector DB   │   │  LLM APIs    │   │    Tools     │                  │
│  │  (Pinecone)  │   │(OpenAI/Claude│   │  (Search,    │                  │
│  │              │   │   /Local)    │   │   Code, DB)  │                  │
│  └──────────────┘   └──────────────┘   └──────────────┘                  │
│                            │                                               │
│                            ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                    Observability & Evaluation                     │     │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐               │     │
│  │  │  Logging   │   │  Metrics   │   │   Eval     │               │     │
│  │  │(LangSmith) │   │(Prometheus)│   │  (RAGAS)   │               │     │
│  │  └────────────┘   └────────────┘   └────────────┘               │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Путь обучения

### Junior AI Engineer (0-1 год)

```
1. Foundations
   ├── Python + API basics
   ├── Prompt engineering fundamentals
   └── OpenAI/Anthropic API usage

2. Core Skills
   ├── RAG with LangChain/LlamaIndex
   ├── Vector databases (Pinecone, Chroma)
   └── Basic evaluation

3. First Projects
   ├── Chatbot with RAG
   ├── Document Q&A system
   └── Simple automation agent
```

### Middle AI Engineer (1-3 года)

```
1. Advanced Techniques
   ├── Advanced RAG (reranking, hybrid search)
   ├── Fine-tuning (LoRA, evaluation)
   └── Multi-agent systems

2. Production Skills
   ├── LLM serving & optimization
   ├── Cost optimization
   └── Evaluation pipelines

3. Projects
   ├── Production AI features
   ├── Complex agent systems
   └── Custom evaluation frameworks
```

### Senior AI Engineer (3+ лет)

```
1. Architecture
   ├── AI system design
   ├── Model selection & evaluation
   └── Scaling strategies

2. Leadership
   ├── Team guidance on AI adoption
   ├── Vendor evaluation
   └── Ethics & safety
```

---

## Проверь себя

<details>
<summary>1. Когда использовать RAG вместо fine-tuning?</summary>

**Ответ:**

RAG предпочтительнее когда:
- Данные часто обновляются
- Нужна прозрачность (источники)
- Мало данных для fine-tuning
- Важна гибкость (разные источники)

Fine-tuning лучше когда:
- Нужен специфичный стиль/формат
- Есть >1000 качественных примеров
- Данные статичны
- Критична латентность

**Правило:** Начинай с prompting → RAG → fine-tuning только если первые не работают.

</details>

<details>
<summary>2. Что такое hallucination и как с ней бороться?</summary>

**Ответ:**

**Hallucination** — генерация правдоподобной, но фактически неверной информации.

Методы борьбы:
1. **RAG** — привязка к реальным источникам
2. **Structured output** — ограничение формата ответа
3. **Fact verification** — проверка через другую модель
4. **Temperature = 0** — детерминированные ответы
5. **Prompt engineering** — "If you don't know, say so"
6. **Human-in-the-loop** — проверка критичных ответов

</details>

<details>
<summary>3. Какие метрики важны для production AI системы?</summary>

**Ответ:**

**Технические:**
- Latency (P50, P95, P99)
- Throughput (requests/sec)
- Cost per query
- Error rate

**Качество:**
- Accuracy / Correctness
- Relevance (для RAG)
- Faithfulness (соответствие источникам)
- Hallucination rate

**Бизнес:**
- User satisfaction (NPS, CSAT)
- Task completion rate
- Retention / engagement

</details>

<details>
<summary>4. Как выбрать между OpenAI, Anthropic и open-source моделями?</summary>

**Ответ:**

| Фактор | OpenAI | Anthropic | Open Source |
|--------|--------|-----------|-------------|
| **Качество** | Высокое | Высокое | Зависит от модели |
| **Стоимость** | Средняя | Средняя | Низкая (инфра) |
| **Privacy** | Облако | Облако | Полный контроль |
| **Latency** | Низкая | Низкая | Зависит от инфры |
| **Customization** | Ограничена | Ограничена | Полная |

**Рекомендация:**
- Начинай с managed (OpenAI/Anthropic) для скорости
- Open source для privacy, cost optimization, специфичных требований
- Комбинируй: дешёвая модель для простых задач, мощная для сложных

</details>

---

## Ключевые карточки

Что такое AI Engineering и чем оно отличается от ML Engineering?
?
AI Engineering — создание продуктов на базе LLM и других AI-моделей. Фокус на интеграции готовых моделей (prompt engineering, RAG, fine-tuning), а не на обучении с нуля. ML Engineering больше про data pipelines и обучение моделей.

Какой порядок выбора метода адаптации модели?
?
Prompting (большинство задач) -> RAG (нужны актуальные/специфичные данные) -> Fine-tuning (специфичный стиль/формат, >1000 примеров). 90% задач решаются через prompting + RAG, fine-tuning нужен редко.

Что такое hallucination и как с ней бороться?
?
Hallucination — генерация правдоподобной, но фактически неверной информации. Методы борьбы: RAG (привязка к источникам), structured output, fact verification через другую модель, temperature=0, prompt engineering («если не знаешь — скажи»), human-in-the-loop.

Что такое RAG и когда его использовать?
?
RAG (Retrieval-Augmented Generation) — паттерн «поиск + генерация»: сначала находим релевантные документы, затем LLM генерирует ответ на их основе. Использовать когда нужны актуальные/специфичные данные, прозрачность (источники), гибкость.

Какие пять ключевых метрик для production AI системы?
?
Latency (<2 с для чатботов), Cost per query (<$0.01 для массовых), Accuracy (>90% для критичных), Hallucination rate (<5%), User satisfaction (>4.0/5.0).

Что такое Token и Context Window?
?
Token — минимальная единица текста для LLM, примерно 4 символа. Context Window — максимальный размер входа модели (количество токенов). От размера context window зависит, сколько информации можно подать модели за один запрос.

Как выбрать между OpenAI, Anthropic и open-source моделями?
?
Managed API (OpenAI/Anthropic) — для быстрого старта, высокого качества, низкой latency. Open-source — для privacy, cost optimization, полной кастомизации. Лучший подход — комбинировать: дешёвая модель для простых задач, мощная для сложных.

Какие основные тренды AI Engineering в 2025 году?
?
Reasoning models (o1, o3, DeepSeek R1), Multimodal AI (vision + audio + text), Agents (tool use, planning), Structured outputs (JSON mode, function calling), Local LLMs (Llama 3, Mistral — privacy и экономия).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ai-engineering-intro]] | Детальное введение в AI Engineering |
| Углубиться | [[llm-fundamentals]] | Фундаментальное устройство LLM |
| Углубиться | [[models-landscape-2025]] | Обзор моделей и провайдеров 2025 |
| Смежная тема | [[rag-and-prompt-engineering]] | Промпты и RAG — основные навыки |
| Смежная тема | [[ai-agents-autonomous-systems]] | AI-агенты и автономные системы |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI/ML раздела |

---

## Связи с другими разделами

- [[architecture-overview]] — AI system architecture patterns
- [[cloud-aws-core-services]] — AWS AI services (Bedrock, SageMaker)
- [[cloud-gcp-core-services]] — GCP AI services (Vertex AI)
- [[security-api-protection]] — API security для AI endpoints
- [[databases-overview]] — Vector databases, data storage

---

## Тренды 2025

| Тренд | Описание | Влияние |
|-------|----------|---------|
| **Reasoning models** | o1, o3, DeepSeek R1 | Сложные задачи без agents |
| **Multimodal** | Vision + Audio + Text | Расширение use cases |
| **Agents** | Tool use, planning | Автоматизация workflows |
| **Structured outputs** | JSON mode, function calling | Надёжная интеграция |
| **Local LLMs** | Llama 3, Mistral, Qwen | Privacy, cost savings |

---

## Источники

### Теоретические основы

- Vaswani A. et al. (2017). *Attention Is All You Need*. NeurIPS
- Bommasani R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258
- Russell S., Norvig P. (2020). *Artificial Intelligence: A Modern Approach*. 4th edition. Pearson
- Jurafsky D., Martin J.H. (2023). *Speech and Language Processing*. 3rd edition
- Huyen C. (2022). *Designing Machine Learning Systems*. O'Reilly
- Sculley D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS

### Практические руководства

- [Anthropic Documentation](https://docs.anthropic.com/) — Claude API
- [OpenAI Documentation](https://platform.openai.com/docs) — GPT API
- [LangChain Docs](https://python.langchain.com/) — AI orchestration
- [LlamaIndex Docs](https://docs.llamaindex.ai/) — RAG framework
- [Chip Huyen: Building LLM Applications](https://huyenchip.com/llm-engineering) — Best practices

---

*Проверено: 2025-12-22*

---

## Связь с другими темами

**[[architecture-overview]]** — Архитектурные паттерны (микросервисы, event-driven, API design) напрямую применяются при проектировании AI-систем. LLM-сервисы встраиваются в общую архитектуру приложения как отдельные компоненты с определёнными контрактами, SLA и паттернами отказоустойчивости. Понимание архитектурных принципов помогает проектировать AI-системы, которые масштабируются и поддерживаются как обычные продакшен-сервисы.

**[[cloud-overview]]** — Облачные платформы (AWS, GCP, Azure) предоставляют managed AI-сервисы (Bedrock, Vertex AI, Azure OpenAI), GPU-инстансы для инференса и инфраструктуру для ML-пайплайнов. Выбор между managed API и self-hosted решениями — одно из ключевых архитектурных решений в AI Engineering, зависящее от требований к privacy, latency и стоимости.

**[[programming-overview]]** — Фундаментальные принципы программирования (SOLID, паттерны проектирования, тестирование) полностью применимы к AI-коду. Prompt templates, chain-of-thought логика, tool definitions — всё это код, который нуждается в версионировании, тестировании и рефакторинге. AI Engineering — это прежде всего software engineering с дополнительными ML-специфичными паттернами.

---

*Проверено: 2026-01-09*
