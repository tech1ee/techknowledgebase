---
title: "Сборка: AI-фича в приложении"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Добавление AI-фичи в приложение

Полное руководство: от выбора модели до мониторинга в продакшене.

---

## Фаза 1: Фундамент

### Понимание AI/ML
- [[ai-engineering-intro]] — введение в AI-инженерию
- [[llm-fundamentals]] — основы LLM
- [[models-landscape-2025]] — ландшафт моделей 2025
- [[ai-ml-overview-v2]] — обзор AI/ML

### Ключевые вопросы перед началом
```
1. Какую задачу решаем? (генерация, классификация, поиск, Q&A)
2. API модели или self-hosted?
3. Бюджет на API-вызовы?
4. Требования к latency?
5. Чувствительность данных (PII, compliance)?
```

### Чеклист
- [ ] Определить тип задачи
- [ ] Выбрать модель (GPT-4, Claude, Gemini, open-source)
- [ ] Оценить стоимость API-вызовов
- [ ] Проверить compliance требования

---

## Фаза 2: Основные навыки

### Промпт-инженерия
- [[prompt-engineering-masterclass]] — мастер-класс по промптам
  - System prompts, few-shot, chain-of-thought
  - Prompt templates и версионирование
  - Evaluation промптов

### Работа с API
- [[ai-api-integration]] — интеграция с AI API
  - OpenAI, Anthropic, Google AI
  - Streaming responses
  - Error handling и retry

### Embeddings и семантический поиск
- [[embeddings-complete-guide]] — полное руководство по embeddings
  - Текстовые embeddings
  - Similarity search
  - Выбор embedding-модели

### Чеклист
- [ ] Промпты: system + user, structured output
- [ ] API: клиент, rate limiting, error handling
- [ ] Embeddings: выбор модели, dimensionality

---

## Фаза 3: RAG (Retrieval-Augmented Generation)

### Если нужна работа с документами / базой знаний
- [[rag-advanced-techniques]] — продвинутые техники RAG
  - Chunking стратегии
  - Hybrid search (vector + keyword)
  - Re-ranking

### Векторные базы данных
- [[vector-databases-guide]] — руководство по векторным БД
  - Pinecone, Weaviate, ChromaDB, pgvector
  - Выбор в зависимости от масштаба

### Agentic RAG
- [[agentic-rag]] — агентный RAG
  - Multi-step retrieval
  - Self-correcting RAG
  - Query decomposition

### Чеклист
- [ ] Chunking: размер, overlap, стратегия
- [ ] Vector DB: выбор и настройка
- [ ] Indexing pipeline: загрузка → chunk → embed → store
- [ ] Retrieval: top-k, threshold, re-ranking
- [ ] Evaluation: relevance, faithfulness

---

## Фаза 4: AI-агенты

### Если нужна автономность
- [[ai-agents-advanced]] — продвинутые AI-агенты
  - ReAct, Plan-and-Execute
  - Tool calling
  - Multi-agent systems

### Фреймворки
- [[agent-frameworks-comparison]] — сравнение фреймворков
  - LangChain, LlamaIndex, CrewAI, AutoGen
  - Выбор по задаче

### Structured Outputs
- [[structured-outputs-tools]] — структурированные выходы и инструменты
  - JSON mode, function calling
  - Schema validation

### Чеклист
- [ ] Определить tools / functions для агента
- [ ] Guardrails: ограничения действий
- [ ] Timeout и fallback стратегии
- [ ] Логирование всех шагов агента

---

## Фаза 5: Продакшн

### Стоимость
- [[ai-cost-optimization]] — оптимизация стоимости AI
  - Кеширование ответов
  - Выбор модели по задаче (не всегда GPT-4)
  - Prompt compression
  - Batching

### Мониторинг
- [[ai-observability-monitoring]] — мониторинг AI-систем
  - Tracing LLM-вызовов
  - Quality metrics
  - Cost tracking

### Безопасность
- [[ai-security-safety]] — безопасность AI
  - Prompt injection protection
  - PII filtering
  - Content moderation
  - Rate limiting

### Fine-tuning (если нужно)
- [[ai-fine-tuning-guide]] — руководство по fine-tuning
- [[ai-data-preparation]] — подготовка данных

### Инфраструктура
- [[ai-devops-deployment]] — деплой AI-систем
- [[llm-inference-optimization]] — оптимизация инференса
- [[local-llms-self-hosting]] — self-hosted модели

### Чеклист
- [ ] Cost: кеширование, rate limiting, бюджет alerts
- [ ] Monitoring: latency, error rate, quality scores
- [ ] Security: input validation, output filtering
- [ ] Fallback: что делать если API недоступен
- [ ] A/B testing: сравнение моделей/промптов

---

## Фаза 6: Мобильная специфика

### AI на мобильных
- [[mobile-ai-ml-guide]] — руководство по AI/ML на мобильных
  - On-device inference
  - Edge AI
  - Hybrid: on-device + cloud

### Чеклист
- [ ] Latency: streaming для UX
- [ ] Offline: какие операции работают без сети
- [ ] Battery: оптимизация энергопотребления
- [ ] Size: модели и зависимости

---

## Туториалы

### Пошаговые руководства
- [[tutorial-rag-chatbot]] — создание RAG-чатбота
- [[tutorial-ai-agent]] — создание AI-агента
- [[tutorial-document-qa]] — система Q&A по документам

---

## Связанные материалы
- [[ai-engineering-moc]] — карта знаний AI-инженерии
- [[ai-tools-ecosystem-2025]] — экосистема AI-инструментов
- [[mcp-model-context-protocol]] — Model Context Protocol
- [[multimodal-ai-guide]] — мультимодальный AI
- [[reasoning-models-guide]] — reasoning-модели
