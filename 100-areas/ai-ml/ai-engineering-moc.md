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

[[ai-ml-overview-v2|← AI/ML Overview]] | [[llm-fundamentals|LLM Fundamentals →]]
