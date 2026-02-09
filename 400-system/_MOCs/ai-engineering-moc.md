---
title: "AI Engineering MOC"
created: 2025-11-24
modified: 2025-12-28
type: moc
tags:
  - moc
  - ai-ml
---

# AI Engineering MOC

> AI Engineering: от основ LLM до production-ready систем. 32 материала в 6 уровнях.

---

## Быстрая навигация

- **Полная карта знаний** → [[ai-ml-overview-v2]] (рекомендуется)
- **Новичок?** → Level 1: [[llm-fundamentals]], [[models-landscape-2025]]
- **Интегрируешь API?** → [[ai-api-integration]] — OpenAI, Claude, LiteLLM ← NEW
- **Строишь RAG?** → [[rag-advanced-techniques]], [[tutorial-rag-chatbot]]
- **Создаёшь агентов?** → [[ai-agents-advanced]], [[tutorial-ai-agent]]
- **Локальные LLM?** → [[local-llms-self-hosting]] — теперь с on-device (iOS/Android)
- **Production deploy?** → Level 4: [[ai-devops-deployment]], [[llm-inference-optimization]]
- **Выбор инструментов?** → [[ai-tools-ecosystem-2025]], [[agent-frameworks-comparison]]

---

## Путь обучения (6 уровней)

```
LEVEL 1: Foundations                    ████░░░░░░░░ Beginner
├── [[llm-fundamentals]]                 Архитектура Transformer
├── [[models-landscape-2025]]            GPT-4o, Claude, Gemini, Llama
└── [[ai-engineering-intro]]             Роль AI Engineer

LEVEL 2: Core Skills                    ████████░░░░ Junior
├── [[prompt-engineering-masterclass]]   Zero-shot, Few-shot, CoT
├── [[embeddings-complete-guide]]        Embeddings, similarity
├── [[vector-databases-guide]]           Pinecone, Weaviate, Qdrant
├── [[ai-api-integration]]               OpenAI, Anthropic, LiteLLM ← NEW
└── [[rag-advanced-techniques]]          Chunking, retrieval, reranking

LEVEL 3: Advanced AI                    ████████████ Middle
├── [[structured-outputs-tools]]         JSON mode, function calling
├── [[mcp-model-context-protocol]]       Anthropic MCP
├── [[reasoning-models-guide]]           o1, o3, DeepSeek R1
├── [[multimodal-ai-guide]]              Vision, Audio, Video
└── [[ai-agents-advanced]]               ReAct, LangGraph, CrewAI

LEVEL 4: Production                     ████████████ Senior
├── [[llm-inference-optimization]]       vLLM, TensorRT-LLM
├── [[local-llms-self-hosting]]          Ollama, LM Studio, On-device
├── [[ai-cost-optimization]]             Caching, Batching
├── [[ai-observability-monitoring]]      Langfuse, LangSmith
└── [[ai-devops-deployment]]             Docker, K8s, CI/CD

LEVEL 5: Practical Projects             ████████████ Hands-on
├── [[tutorial-rag-chatbot]]             RAG чат-бот с кодом
├── [[tutorial-ai-agent]]                AI Agent с инструментами
└── [[tutorial-document-qa]]             Document Q&A + extraction

LEVEL 6: Ecosystem                      ████████████ Reference
├── [[agent-frameworks-comparison]]      LangGraph vs CrewAI vs AutoGen
└── [[ai-tools-ecosystem-2025]]          Полный каталог инструментов
```

**Полная карта:** [[ai-ml-overview-v2]]

---

## RAG vs Fine-tuning: Decision Matrix

### Decision Tree

```
Нужны актуальные данные в реальном времени?
├── ДА → RAG (retrieval из свежих источников)
│
└── НЕТ → Нужен специфический стиль/тон ответа?
          ├── ДА → Fine-tuning (стиль baked in)
          │
          └── НЕТ → Достаточно ли prompt engineering?
                    ├── ДА → Просто prompting (начни здесь!)
                    └── НЕТ → RAG для coverage, Fine-tuning для специализации
```

### Сравнение подходов

| Критерий | RAG | Fine-tuning | Prompting |
|----------|-----|-------------|-----------|
| **Свежесть данных** | Real-time | Статичные | Knowledge cutoff |
| **Кастомизация стиля** | Ограничена | Глубокая | Через системный промпт |
| **Hallucinations** | Меньше (grounded) | Зависит от данных | Больше |
| **Latency** | +retrieval step | Низкая | Низкая |
| **Стоимость внедрения** | Средняя | Высокая | Низкая |

**Подробнее:** [[rag-advanced-techniques]]

---

## Тренды AI Engineering 2025

| Тренд | Что это | Где изучить |
|-------|---------|-------------|
| **Agentic AI** | LLM с tools и автономными решениями | [[ai-agents-advanced]] |
| **Reasoning Models** | o1, o3, Claude с extended thinking | [[reasoning-models-guide]] |
| **MCP Protocol** | Anthropic's Model Context Protocol | [[mcp-model-context-protocol]] |
| **Multimodal** | Vision, Audio, Video в одной модели | [[multimodal-ai-guide]] |
| **Local LLMs** | Ollama, LM Studio, DeepSeek R1 | [[local-llms-self-hosting]] |
| **On-device AI** | MLX iOS, MediaPipe Android, Edge | [[local-llms-self-hosting]] |
| **Cost Optimization** | Caching 90%, Batching 50% | [[ai-cost-optimization]] |

---

## Ключевые концепции

| Концепция | Описание | Материал |
|-----------|----------|----------|
| **LLM** | Large Language Models | [[llm-fundamentals]] |
| **Embeddings** | Векторные представления | [[embeddings-complete-guide]] |
| **RAG** | Retrieval-Augmented Generation | [[rag-advanced-techniques]] |
| **Prompt Engineering** | Формулирование запросов | [[prompt-engineering-masterclass]] |
| **AI Agents** | Автономные LLM с tools | [[ai-agents-advanced]] |
| **Guardrails** | Content filters, safety | [[ai-observability-monitoring]] |
| **Tool Calling** | Function calling, MCP | [[structured-outputs-tools]] |
| **API Integration** | OpenAI, Anthropic, LiteLLM SDKs | [[ai-api-integration]] |

---

## Learning Paths

### RAG Specialist
```
llm-fundamentals → embeddings-complete-guide → vector-databases-guide
→ rag-advanced-techniques → tutorial-rag-chatbot → tutorial-document-qa
```

### Agent Developer
```
llm-fundamentals → prompt-engineering-masterclass → structured-outputs-tools
→ ai-agents-advanced → agent-frameworks-comparison → tutorial-ai-agent
```

### MLOps / Platform
```
models-landscape-2025 → llm-inference-optimization → local-llms-self-hosting
→ ai-devops-deployment → ai-observability-monitoring → ai-cost-optimization
```

---

## Связанные области

- [[api-design]] — REST/GraphQL для LLM APIs
- [[ci-cd-pipelines]] — MLOps, деплой моделей
- [[cloud-platforms-essentials]] — GPU instances, managed AI services
- [[observability]] — Мониторинг LLM performance
- [[kubernetes-basics]] — K8s для AI workloads

---

## Статус контента

| Уровень | Материалов | Статус |
|---------|------------|--------|
| Level 1: Foundations | 3 | Verified 2025-12 |
| Level 2: Core Skills | 5 | Verified 2025-12 |
| Level 3: Advanced | 5 | Verified 2025-12 |
| Level 4: Production | 5 | Verified 2025-12 |
| Level 5: Projects | 3 | Verified 2025-12 |
| Level 6: Ecosystem | 2 | Verified 2025-12 |
| **Всего** | **23 новых + 9 legacy** | |

---

## Legacy материалы

Следующие материалы устарели и заменены новыми:

| Старый | Заменён на |
|--------|------------|
| ai-ml-overview.md | [[ai-ml-overview-v2]] |
| ai-engineer-roadmap.md | Level structure в [[ai-ml-overview-v2]] |
| ai-engineer-tech-stack.md | [[ai-tools-ecosystem-2025]] |
| rag-and-prompt-engineering.md | [[rag-advanced-techniques]] + [[prompt-engineering-masterclass]] |
| ai-agents-autonomous-systems.md | [[ai-agents-advanced]] |

---

*Проверено: 2025-12-28 | 32 материала | Полная карта: [[ai-ml-overview-v2]]*
