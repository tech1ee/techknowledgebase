---
title: "AI Engineering MOC: карта AI инженера"
created: 2026-01-09
modified: 2026-01-09
type: moc
status: published
confidence: high
tags:
  - topic/ai-ml
  - rag
  - agents
  - type/moc
related:
  - "[[ai-ml-overview-v2]]"
  - "[[llm-fundamentals]]"
  - "[[rag-advanced-techniques]]"
  - "[[ai-agents-advanced]]"
reading_time: 7
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AI Engineering MOC: карта AI инженера

> **TL;DR:** AI Engineering — это дисциплина создания production-ready AI систем. Не путать с ML Engineering (обучение моделей) или Data Science (анализ данных). AI инженер интегрирует LLM в приложения, строит RAG системы, создаёт агентов и оптимизирует inference.

---

## Что такое AI Engineering?

```
DATA SCIENCE          ML ENGINEERING          AI ENGINEERING
     │                      │                       │
 Анализ данных         Обучение моделей      Интеграция LLM
 Статистика            MLOps, pipelines      RAG, Agents
 Визуализация          Feature engineering   Prompt engineering
 Гипотезы              Training infra        API интеграция
     │                      │                       │
     └──────────────────────┴───────────────────────┘
                            │
                    Все нужны для AI продукта
```

### AI Engineer отвечает за:

- Интеграцию LLM (OpenAI, Claude, Gemini) в приложения
- Построение RAG систем (retrieval-augmented generation)
- Создание AI агентов с инструментами
- Prompt engineering и оптимизация
- Мониторинг и observability AI систем
- Cost optimization (LLM дорогие!)

---

## Quick Navigation

| Вопрос | Куда идти |
|--------|-----------|
| Как работают LLM? | [[llm-fundamentals]] |
| Как писать промпты? | [[prompt-engineering-masterclass]] |
| Что такое RAG? | [[rag-advanced-techniques]] |
| Как подготовить данные? | [[ai-data-preparation]] |
| Как делать embeddings? | [[embeddings-complete-guide]] |
| Какую vector DB выбрать? | [[vector-databases-guide]] |
| Как создать агента? | [[ai-agents-advanced]] → [[tutorial-ai-agent]] |
| Как отлаживать агента? | [[agent-debugging-troubleshooting]] |
| Как тестировать агента? | [[agent-evaluation-testing]] |
| Как деплоить агента? | [[agent-production-deployment]] |
| Как оптимизировать стоимость агента? | [[agent-cost-optimization]] |
| RAG + Agents? | [[agentic-rag]] |
| Как защитить AI систему? | [[ai-security-safety]] |
| Как дообучить модель? | [[ai-fine-tuning-guide]] |
| Как интегрировать API? | [[ai-api-integration]] |
| Какие модели выбрать? | [[models-landscape-2025]] |
| Как оптимизировать стоимость? | [[ai-cost-optimization]] |
| Как мониторить AI систему? | [[ai-observability-monitoring]] |

---

## Learning Path: от новичка до эксперта

```
                    УРОВЕНЬ 1: Основы
                    ┌─────────────────┐
                    │ LLM Fundamentals│
                    │ Prompt Basics   │
                    │ API Integration │
                    └────────┬────────┘
                             │
                    УРОВЕНЬ 2: RAG
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐
    │ Embeddings│     │  Vector DBs │    │  Chunking   │
    │           │     │             │    │  Strategies │
    └─────┬─────┘     └──────┬──────┘    └──────┬──────┘
          │                  │                  │
                    УРОВЕНЬ 3: Advanced
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐
    │   Agents  │     │  Structured │    │  Fine-tuning│
    │   & Tools │     │   Outputs   │    │             │
    └─────┬─────┘     └──────┬──────┘    └──────┬──────┘
          │                  │                  │
                    УРОВЕНЬ 4: Production
                    ┌─────────────────┐
                    │  Observability  │
                    │  Cost Optim.    │
                    │  Evaluation     │
                    │  Deployment     │
                    └─────────────────┘
```

### Рекомендуемый порядок изучения

| # | Тема | Статья | Время |
|---|------|--------|-------|
| 1 | Основы LLM | [[llm-fundamentals]] | 1 день |
| 2 | Prompt Engineering | [[prompt-engineering-masterclass]] | 2-3 дня |
| 3 | API интеграция | [[ai-api-integration]] | 1 день |
| 4 | Embeddings | [[embeddings-complete-guide]] | 1 день |
| 5 | Vector Databases | [[vector-databases-guide]] | 1-2 дня |
| 6 | RAG системы | [[rag-advanced-techniques]] | 3-4 дня |
| 7 | Structured Outputs | [[structured-outputs-tools]] | 1 день |
| 8 | AI Agents | [[ai-agents-advanced]] | 3-4 дня |
| 9 | Observability | [[ai-observability-monitoring]] | 1-2 дня |
| 10 | Cost Optimization | [[ai-cost-optimization]] | 1 день |

**Общее время:** ~2-3 недели интенсивного изучения

---

## Все материалы по категориям

### Fundamentals

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[llm-fundamentals]] | Как работают LLM, токенизация, context window | L1 |
| [[models-landscape-2025]] | Обзор моделей: GPT-4, Claude, Gemini, открытые | L1 |
| [[prompt-engineering-masterclass]] | Техники промптинга: few-shot, CoT, ReAct | L2 |
| [[ai-api-integration]] | Интеграция OpenAI, Anthropic, Google AI APIs | L1 |

### RAG (Retrieval-Augmented Generation)

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[embeddings-complete-guide]] | Векторные представления текста | L2 |
| [[vector-databases-guide]] | Pinecone, Weaviate, Qdrant, pgvector | L2 |
| [[ai-data-preparation]] | **NEW** Chunking, синтетические данные, quality | L2 |
| [[rag-advanced-techniques]] | Chunking, reranking, hybrid search | L3 |
| [[tutorial-rag-chatbot]] | Практика: RAG чатбот | L2 |
| [[tutorial-document-qa]] | Практика: Q&A по документам | L2 |

### Agents & Tools

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[ai-agents-advanced]] | Архитектуры агентов, ReAct, планирование | L3 |
| [[structured-outputs-tools]] | JSON mode, function calling, tool use | L2 |
| [[mcp-model-context-protocol]] | Anthropic MCP для интеграции инструментов | L3 |
| [[agent-frameworks-comparison]] | LangChain vs LlamaIndex vs Semantic Kernel | L2 |
| [[agentic-rag]] | **NEW** Agentic RAG: Self-RAG, CRAG, Adaptive | L3 |
| [[agent-debugging-troubleshooting]] | **NEW** Debugging и troubleshooting агентов | L3 |
| [[agent-evaluation-testing]] | **NEW** Тестирование и evaluation агентов | L3 |
| [[agent-cost-optimization]] | **NEW** Оптимизация стоимости агентов | L3 |
| [[agent-production-deployment]] | **NEW** Production deployment агентов | L4 |
| [[tutorial-ai-agent]] | Практика: создание агента | L3 |

### Production & Operations

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[ai-security-safety]] | **NEW** Prompt injection, guardrails, DLP | L3 |
| [[ai-cost-optimization]] | Оптимизация стоимости LLM вызовов | L3 |
| [[ai-observability-monitoring]] | Мониторинг, трейсинг, логирование | L3 |
| [[ai-devops-deployment]] | Деплой AI систем, CI/CD | L3 |
| [[llm-inference-optimization]] | Latency, throughput, кэширование | L4 |

### Fine-tuning & Adaptation

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[ai-fine-tuning-guide]] | **NEW** LoRA, QLoRA, DPO, ORPO | L3 |
| [[ai-data-preparation]] | Подготовка данных для fine-tuning | L2 |

### Specialized

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[multimodal-ai-guide]] | Vision, Audio, Video с LLM | L3 |
| [[reasoning-models-guide]] | o1, DeepSeek R1, reasoning модели | L3 |
| [[local-llms-self-hosting]] | Ollama, llama.cpp, self-hosted LLM | L3 |
| [[mobile-ai-ml-guide]] | AI на мобильных устройствах | L3 |
| [[ai-tools-ecosystem-2025]] | Обзор инструментов и фреймворков | L1 |

---

## Ключевые концепции

### RAG Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                          │
│                                                          │
│  Документы ──► Chunking ──► Embedding ──► Vector DB     │
│                                              │           │
│                                              ▼           │
│  Query ──► Embedding ──► Semantic Search ──► Retrieve    │
│                                              │           │
│                                              ▼           │
│  Retrieved Context + Query ──► LLM ──► Response         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Agent Loop

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT LOOP                            │
│                                                          │
│  User Query                                              │
│       │                                                  │
│       ▼                                                  │
│  ┌─────────┐                                            │
│  │  Think  │ ◄────────────────────────────┐             │
│  └────┬────┘                              │             │
│       │                                   │             │
│       ▼                                   │             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┤             │
│  │   Act   │───►│  Tool   │───►│ Observe │             │
│  └─────────┘    └─────────┘    └─────────┘             │
│                                                          │
│  Loop until: Answer ready or max iterations              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Стек технологий 2025

### LLM Providers

| Provider | Модели | Сильные стороны |
|----------|--------|-----------------|
| **OpenAI** | GPT-4o, o1 | Лучший general-purpose |
| **Anthropic** | Claude 3.5 Sonnet | Coding, длинный контекст |
| **Google** | Gemini 2.0 | Multimodal, цена |
| **Meta** | Llama 3.3 | Open source |
| **Mistral** | Mixtral, Mistral Large | EU compliance |

### Frameworks

| Framework | Для чего | Когда использовать |
|-----------|----------|-------------------|
| **LangChain** | RAG, Agents | Сложные пайплайны |
| **LlamaIndex** | RAG | Фокус на retrieval |
| **Semantic Kernel** | Agents | Microsoft стек |
| **Haystack** | RAG | Production focus |
| **DSPy** | Prompt optimization | Автоматизация промптов |

### Vector Databases

| Database | Тип | Особенности |
|----------|-----|-------------|
| **Pinecone** | Managed | Простота, масштаб |
| **Weaviate** | Open source | Hybrid search |
| **Qdrant** | Open source | Performance |
| **pgvector** | PostgreSQL extension | Если уже есть PG |
| **Chroma** | Embedded | Для прототипов |

---

## Связи с другими разделами

- [[ai-ml-overview-v2]] — основной обзор AI/ML
- [[architecture-overview]] — архитектура AI систем
- [[databases-overview]] — vector databases
- [[devops-overview]] — деплой AI систем
- [[programming-overview]] — Python для AI

---

## Ресурсы

| Ресурс | Тип | Описание |
|--------|-----|----------|
| [LangChain Docs](https://python.langchain.com/) | Docs | Framework documentation |
| [OpenAI Cookbook](https://cookbook.openai.com/) | Tutorials | Примеры и best practices |
| [Anthropic Docs](https://docs.anthropic.com/) | Docs | Claude API и техники |
| [Pinecone Learning](https://www.pinecone.io/learn/) | Course | RAG и vector search |

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего статей | 35+ |
| Категорий | 6 |
| Tutorials | 3 |
| Agent Guides | 10 |
| Последнее обновление | 2026-01-11 |

---

*Проверено: 2026-01-11*

---

## Проверь себя

> [!question]- Почему AI Engineering выделяют в отдельную дисциплину, а не считают частью ML Engineering?
> Потому что задачи принципиально разные. ML Engineer обучает модели (тренировочные пайплайны, feature engineering, MLOps), а AI Engineer интегрирует уже готовые LLM в продукты: строит RAG-системы, проектирует агентов, оптимизирует промпты и управляет стоимостью inference. AI Engineer может вообще не обучать ни одной модели — он работает поверх API провайдеров (OpenAI, Anthropic, Google). Это разделение аналогично тому, как frontend-разработчик отличается от разработчика браузерного движка.

> [!question]- Компания хочет внедрить AI-поиск по внутренней документации (50 000 документов). Какой подход вы предложите и из каких этапов будет состоять пайплайн?
> Оптимальный подход — RAG (Retrieval-Augmented Generation). Пайплайн: (1) Chunking — разбить документы на фрагменты оптимального размера (500-1000 токенов) с перекрытием; (2) Embedding — превратить чанки в векторные представления через модель эмбеддингов; (3) Indexing — загрузить векторы в vector database (Qdrant, Pinecone, pgvector); (4) Retrieval — при запросе пользователя найти top-K релевантных чанков через semantic search; (5) Generation — передать найденный контекст вместе с запросом в LLM для генерации ответа. Для 50K документов важно также добавить hybrid search (семантический + keyword) и reranking для повышения точности.

> [!question]- В чём ключевое отличие ReAct-агента от простого цепочечного (chain) вызова LLM? В каком случае агент избыточен?
> ReAct-агент работает в цикле Think → Act → Observe: он сам решает, какой инструмент вызвать, анализирует результат и решает, продолжать или дать ответ. Chain — это жёстко заданная последовательность шагов без ветвления. Агент избыточен, когда задача полностью предсказуема и не требует адаптивных решений — например, простая классификация текста или извлечение данных по фиксированной схеме. В таких случаях chain дешевле, быстрее и надёжнее.

> [!question]- Вы запустили RAG-систему в production, и пользователи жалуются на неточные ответы. Какие три метрики вы будете отслеживать и почему?
> (1) Retrieval Precision/Recall — измеряет, насколько релевантные документы находит retrieval-этап. Если precision низкий, LLM получает мусорный контекст. (2) Faithfulness (groundedness) — проверяет, основан ли ответ LLM на найденном контексте или модель «галлюцинирует». (3) Answer Relevance — оценивает, насколько ответ соответствует вопросу пользователя. Проблема может быть на любом этапе: плохой chunking, слабая модель эмбеддингов, неоптимальный промпт для генерации — метрики помогают локализовать узкое место.

---

## Ключевые карточки

AI Engineering vs ML Engineering — в чём разница?
?
AI Engineer интегрирует готовые LLM в продукты (RAG, агенты, промпты, API). ML Engineer обучает модели (training pipelines, feature engineering, MLOps). AI Engineer может не обучать моделей вообще.

Из каких этапов состоит RAG pipeline?
?
Документы → Chunking → Embedding → Vector DB → (запрос) → Embedding запроса → Semantic Search → Retrieve top-K → Context + Query → LLM → Response.

Что такое ReAct паттерн в AI агентах?
?
Цикл Reasoning + Acting: агент думает (Think), выполняет действие через инструмент (Act), наблюдает результат (Observe), и повторяет до получения финального ответа или достижения лимита итераций.

Назови 5 категорий vector databases и примеры
?
Managed SaaS (Pinecone), Open-source standalone (Qdrant, Weaviate), PostgreSQL-расширение (pgvector), Embedded/in-memory (Chroma), Cloud-native (Zilliz/Milvus). Выбор зависит от масштаба, инфраструктуры и бюджета.

Когда fine-tuning предпочтительнее RAG?
?
Когда нужно изменить стиль/формат ответов модели, обучить специфичной терминологии или снизить latency (не нужен retrieval-этап). RAG лучше, когда данные часто обновляются или нужна атрибуция источников.

Четыре уровня AI Engineering learning path?
?
L1: Основы (LLM fundamentals, промпты, API). L2: RAG (embeddings, vector DB, chunking). L3: Advanced (агенты, structured outputs, fine-tuning). L4: Production (observability, cost optimization, deployment, evaluation).

Почему cost optimization критична для AI систем?
?
LLM-вызовы стоят денег за каждый токен. Без оптимизации затраты растут линейно с трафиком. Методы: кэширование ответов, выбор меньших моделей для простых задач, сокращение контекста, batching запросов, semantic caching.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Первый шаг | [[llm-fundamentals]] | Понять как работают LLM изнутри: токенизация, attention, context window |
| Практика RAG | [[tutorial-rag-chatbot]] | Построить RAG-чатбот руками — закрепить теорию пайплайна |
| Глубже в агентов | [[ai-agents-advanced]] | Архитектуры агентов: ReAct, планирование, multi-agent systems |
| Безопасность AI | [[ai-security-safety]] | Prompt injection, guardrails, DLP — критично для production |
| Кросс-домен: базы данных | [[databases-overview]] | Vector databases — часть экосистемы БД, полезно понимать контекст |
| Кросс-домен: DevOps | [[ai-devops-deployment]] | CI/CD для AI систем, контейнеризация моделей, инфраструктура |
| Кросс-домен: архитектура | [[clean-code-solid]] | Принципы чистого кода применимы и к AI-пайплайнам |

---

[[ai-ml-overview-v2|← AI/ML Overview]] | [[llm-fundamentals|LLM Fundamentals →]]
