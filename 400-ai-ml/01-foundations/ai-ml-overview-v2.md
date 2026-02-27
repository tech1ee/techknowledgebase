---
title: "AI/ML Engineering: Карта знаний 2025"
tags:
  - topic/ai-ml
  - overview
  - curriculum
  - learning-path
  - type/moc
category: ai-engineering
date: 2025-01-15
status: published
type: moc
reading_time: 9
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AI/ML Engineering: Полная карта знаний

> **Map of Content (MOC)** для освоения AI Engineering — от основ до production-ready систем.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Python основы** | 95% AI инструментов на Python | Любой курс Python |
| **REST API** | Все LLM работают через API | [[api-design]] |
| **JSON** | Формат обмена данными с LLM | Базовое программирование |
| **Асинхронность** | Streaming, параллельные запросы | Python asyncio |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в программировании** | ⚠️ Частично | Сначала основы Python, потом сюда |
| **Разработчик без AI опыта** | ✅ Да | Начните с Level 1, идите последовательно |
| **Опытный разработчик** | ✅ Да | Используйте Quick Links для нужных тем |
| **Data Scientist/ML Engineer** | ✅ Да | Фокус на Levels 3-4 (production) |

### Терминология для новичков

> 💡 **AI Engineering** = создание приложений на основе готовых LLM (не обучение моделей с нуля)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **LLM** | Large Language Model — большая языковая модель | **Очень начитанный собеседник** — прочитал интернет и может отвечать на вопросы |
| **Token** | Единица текста для LLM (слово или часть слова) | **Слог** — LLM читает текст не буквами, а "кусочками" |
| **Prompt** | Текст-инструкция для LLM | **Задание для помощника** — чем точнее опишешь, тем лучше результат |
| **Embedding** | Числовое представление смысла текста | **Координаты смысла** — похожие тексты = близкие координаты |
| **RAG** | Retrieval-Augmented Generation | **Поиск + генерация** — LLM ищет в документах перед ответом |
| **Agent** | LLM с возможностью выполнять действия | **Умный помощник с руками** — не только отвечает, но и делает |
| **Fine-tuning** | Дообучение модели под задачу | **Специализация** — врач общей практики становится кардиологом |
| **Inference** | Процесс получения ответа от модели | **Консультация** — задаёшь вопрос, получаешь ответ |
| **Context Window** | Сколько текста "помнит" модель за раз | **Оперативная память** — чем больше, тем больше контекста |
| **Hallucination** | Когда LLM уверенно врёт | **Фантазия** — модель "додумывает" то, чего не знает |

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ENGINEERING CURRICULUM                     │
│                         23 материала                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LEVEL 1: Foundations                    ████░░░░░░░░ Beginner  │
│  LEVEL 2: Core Skills                    ████████░░░░ Junior    │
│  LEVEL 3: Advanced AI                    ████████████ Middle    │
│  LEVEL 4: Production                     ████████████ Senior    │
│  LEVEL 5: Practical Projects             ████████████ Hands-on  │
│  LEVEL 6: Ecosystem & Tools              ████████████ Reference │
│                                                                  │
│  Estimated time: 40-60 hours of focused study                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Теоретические основы

### Определение искусственного интеллекта

> **Искусственный интеллект** (Artificial Intelligence, AI) — область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, которые обычно требуют человеческого интеллекта: восприятие, рассуждение, обучение, принятие решений и взаимодействие на естественном языке (Russell & Norvig, 2020).

### Историческая периодизация AI

| Период | Эпоха | Ключевые события | Парадигма |
|--------|-------|------------------|-----------|
| 1943-1956 | Зарождение | Модель нейрона (McCulloch & Pitts, 1943), тест Тьюринга (1950), Дартмутская конференция (1956) | Символический AI |
| 1956-1974 | Первый расцвет | Perceptron (Rosenblatt, 1958), ELIZA (Weizenbaum, 1966) | Символические системы |
| 1974-1980 | Первая зима AI | Отчёт Лайтхилла (1973), прекращение финансирования DARPA | Разочарование |
| 1980-1987 | Экспертные системы | R1/XCON (Digital Equipment), Японский проект FGCP | Продукционные правила |
| 1987-1993 | Вторая зима AI | Крах рынка Lisp-машин, провал FGCP | Стагнация |
| 1993-2011 | Статистический ML | SVM (Vapnik, 1995), Random Forest (Breiman, 2001), Netflix Prize (2006) | Статистическое обучение |
| 2012-2017 | Глубокое обучение | AlexNet (Krizhevsky, 2012), GANs (Goodfellow, 2014), Transformer (Vaswani, 2017) | Нейросети |
| 2018-2022 | Эра Foundation Models | GPT (Radford, 2018), BERT (Devlin, 2018), GPT-3 (Brown, 2020) | Pre-training + Fine-tuning |
| 2022-н.в. | Эра AI Engineering | ChatGPT (2022), GPT-4 (2023), Reasoning models (2024) | Prompting + RAG + Agents |

### Таксономия AI

> **Узкий AI (ANI, Artificial Narrow Intelligence)** — системы, решающие одну конкретную задачу. Все существующие AI-системы, включая GPT-4 и Claude, формально относятся к ANI, несмотря на впечатляющую генерализацию.
>
> **Общий AI (AGI, Artificial General Intelligence)** — гипотетическая система с интеллектом уровня человека. По оценке Metaculus (2025), медианный прогноз появления AGI — ~2030 год.
>
> **Сверхразумный AI (ASI, Artificial Superintelligence)** — гипотетическая система, превосходящая человека во всех когнитивных задачах (Bostrom, 2014).

### Фундаментальные подходы к AI

| Подход | Принцип | Представители | Эпоха |
|--------|---------|---------------|-------|
| **Символический AI** | Формальная логика и правила | GOFAI, экспертные системы | 1956-1990 |
| **Коннекционизм** | Обучение нейронных сетей | Перцептрон, deep learning | 1958-н.в. |
| **Статистический ML** | Оптимизация по данным | SVM, Random Forest, XGBoost | 1990-н.в. |
| **Foundation Models** | Предобучение на масштабе | GPT, BERT, [[llm-fundamentals\|Transformer]] | 2018-н.в. |

### Определение AI Engineering

AI Engineering как дисциплина отличается от смежных областей рядом ключевых характеристик, формализованных в работах Huyen (2024) и Bommasani et al. (2021, *"On the Opportunities and Risks of Foundation Models"*, Stanford CRFM):

1. **Использование предобученных моделей** — в отличие от ML Engineering, не требуется training from scratch
2. **Программирование на естественном языке** — промпты как новый тип интерфейса (Software 3.0, Karpathy)
3. **Композиция систем** — сборка из компонентов: LLM + RAG + Tools + Memory
4. **Фокус на application layer** — бизнес-логика поверх моделей, а не сами модели

---

## Как использовать эту карту

1. **Последовательно** — идите по уровням от 1 до 6
2. **По задаче** — выбирайте нужный раздел через Quick Links
3. **Как справочник** — возвращайтесь к материалам при необходимости

### Легенда сложности
- `[B]` Beginner — базовые концепции
- `[I]` Intermediate — требует понимания основ
- `[A]` Advanced — продвинутые техники
- `[P]` Practical — hands-on проекты

---

## Quick Links по задачам

| Задача | Материалы |
|--------|-----------|
| **Начать с нуля** | Level 1 → Level 2 |
| **Построить RAG** | [[rag-advanced-techniques]], [[tutorial-rag-chatbot]] |
| **Создать агента** | [[ai-agents-advanced]], [[tutorial-ai-agent]] |
| **Выбрать модель** | [[models-landscape-2025]], [[reasoning-models-guide]] |
| **Оптимизировать costs** | [[ai-cost-optimization]] |
| **Деплой в production** | [[ai-devops-deployment]], [[llm-inference-optimization]] |
| **Mobile/On-Device AI** | [[mobile-ai-ml-guide]], [[local-llms-self-hosting]] |
| **Выбрать инструменты** | [[ai-tools-ecosystem-2025]], [[agent-frameworks-comparison]] |

---

## Level 1: Foundations [B]

> Базовое понимание LLM, их возможностей и ограничений.

```
┌─────────────────────────────────────────────────────────────────┐
│  1.1 [[llm-fundamentals]]                                       │
│      Архитектура Transformer, токенизация, attention            │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  1.2 [[models-landscape-2025]]                                  │
│      Обзор GPT-4o, Claude, Gemini, Llama, DeepSeek              │
│      Сравнение, выбор модели под задачу                         │
│      ⏱ 2 часа                                                   │
├─────────────────────────────────────────────────────────────────┤
│  1.3 [[ai-engineering-intro]]                                   │
│      Роль AI Engineer, отличия от ML Engineer                   │
│      Обзор экосистемы и карьерных путей                         │
│      ⏱ 1 час                                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Понимание что такое LLM, какие модели существуют, что делает AI Engineer.

---

## Level 2: Core Skills [I]

> Ключевые навыки работы с LLM: промпты, embeddings, RAG.

```
┌─────────────────────────────────────────────────────────────────┐
│  2.1 [[prompt-engineering-masterclass]]                         │
│      Zero-shot, Few-shot, Chain-of-Thought, ReAct               │
│      System prompts, prompt injection protection                │
│      ⏱ 4-5 часов                                                │
├─────────────────────────────────────────────────────────────────┤
│  2.2 [[embeddings-complete-guide]]                              │
│      Как работают embeddings, выбор модели                      │
│      Similarity search, практические применения                 │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  2.3 [[vector-databases-guide]]                                 │
│      Pinecone, Weaviate, Qdrant, Chroma                         │
│      Индексы (HNSW, IVF), metadata filtering                    │
│      ⏱ 3 часа                                                   │
├─────────────────────────────────────────────────────────────────┤
│  2.4 [[rag-advanced-techniques]]                                │
│      Chunking, retrieval, reranking, evaluation                 │
│      Naive → Advanced → Modular RAG                             │
│      ⏱ 4-5 часов                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Умение писать эффективные промпты, строить RAG-системы.

---

## Level 3: Advanced AI [A]

> Продвинутые концепции: агенты, reasoning, multimodal.

```
┌─────────────────────────────────────────────────────────────────┐
│  3.1 [[structured-outputs-tools]]                               │
│      JSON mode, function calling, tool use                      │
│      Pydantic schemas, structured extraction                    │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  3.2 [[mcp-model-context-protocol]]                             │
│      Anthropic MCP, server/client архитектура                   │
│      Интеграция с data sources                                  │
│      ⏱ 2 часа                                                   │
├─────────────────────────────────────────────────────────────────┤
│  3.3 [[reasoning-models-guide]]                                 │
│      o1, o3, DeepSeek R1, Claude с extended thinking            │
│      Chain-of-Thought vs test-time compute                      │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  3.4 [[multimodal-ai-guide]]                                    │
│      Vision (GPT-4o, Claude, Gemini)                            │
│      Audio (Whisper, TTS), Video (Sora)                         │
│      Image generation (DALL-E, Midjourney, Flux)                │
│      ⏱ 3-4 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  3.5 [[ai-agents-advanced]]                                     │
│      ReAct, Plan-and-Execute, Reflection                        │
│      LangGraph, CrewAI, multi-agent systems                     │
│      Claude Computer Use, guardrails                            │
│      ⏱ 4-5 часов                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Понимание advanced AI паттернов, умение проектировать агентов.

---

## Level 4: Production & Deployment [A]

> Всё необходимое для production-ready AI систем.

```
┌─────────────────────────────────────────────────────────────────┐
│  4.1 [[llm-inference-optimization]]                             │
│      vLLM, TensorRT-LLM, SGLang                                 │
│      Continuous batching, speculative decoding                  │
│      Quantization: AWQ, GPTQ, FP8                               │
│      ⏱ 3-4 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  4.2 [[local-llms-self-hosting]]                                │
│      Ollama, LM Studio, llama.cpp                               │
│      Hardware requirements, GPU выбор                           │
│      Open-source models: DeepSeek, Llama, Qwen                  │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  4.3 [[ai-cost-optimization]]                                   │
│      Prompt caching (90% savings)                               │
│      Batch API (50% discount)                                   │
│      Model routing, token optimization                          │
│      ⏱ 2-3 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  4.4 [[ai-observability-monitoring]]                            │
│      Langfuse, LangSmith, Arize Phoenix                         │
│      OpenTelemetry, LLM-as-Judge                                │
│      Metrics, alerting, evaluation                              │
│      ⏱ 3-4 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  4.5 [[ai-devops-deployment]]                                   │
│      Docker, Kubernetes GPU scheduling                          │
│      CI/CD for AI, deployment strategies                        │
│      Blue-green, canary, shadow                                 │
│      ⏱ 3-4 часа                                                 │
├─────────────────────────────────────────────────────────────────┤
│  4.6 [[mobile-ai-ml-guide]]                                     │
│      On-device LLM: Gemma 3n, Llama 3.2, Phi-3                  │
│      SDKs: LiteRT, CoreML, ExecuTorch, ONNX Runtime             │
│      NPU optimization: ANE, Hexagon, APU                        │
│      Quantization: GGUF Q4_K_M, production patterns             │
│      ⏱ 4-5 часов                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Умение деплоить, оптимизировать и мониторить AI в production.

---

## Level 5: Practical Projects [P]

> Hands-on туториалы с рабочим кодом.

```
┌─────────────────────────────────────────────────────────────────┐
│  5.1 [[tutorial-rag-chatbot]]                                   │
│      RAG чат-бот: LangChain + ChromaDB + Streamlit              │
│      Document loading, chunking, retrieval                      │
│      Полная реализация с UI                                     │
│      ⏱ 4-6 часов практики                                       │
├─────────────────────────────────────────────────────────────────┤
│  5.2 [[tutorial-ai-agent]]                                      │
│      AI Agent с инструментами: LangGraph                        │
│      Web search, calculator, file ops                           │
│      Guardrails, human-in-the-loop                              │
│      ⏱ 4-6 часов практики                                       │
├─────────────────────────────────────────────────────────────────┤
│  5.3 [[tutorial-document-qa]]                                   │
│      Document Q&A с structured extraction                       │
│      PDF parsing, invoice/contract extraction                   │
│      Multi-document comparison                                  │
│      ⏱ 4-6 часов практики                                       │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Три работающих проекта в портфолио.

---

## Level 6: Ecosystem & Reference [I/A]

> Справочные материалы и сравнения инструментов.

```
┌─────────────────────────────────────────────────────────────────┐
│  6.1 [[agent-frameworks-comparison]]                            │
│      LangGraph vs CrewAI vs AutoGen vs OpenAI Agents            │
│      Pydantic AI, Agno, SmolAgents                              │
│      Бенчмарки, когда что использовать                          │
│      ⏱ 2 часа (справочник)                                      │
├─────────────────────────────────────────────────────────────────┤
│  6.2 [[ai-tools-ecosystem-2025]]                                │
│      Полный каталог инструментов                                │
│      IDE, APIs, Vector DBs, Observability                       │
│      Guardrails, Inference, RAG tools                           │
│      ⏱ 2 часа (справочник)                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Результат:** Знание экосистемы, умение выбрать правильные инструменты.

---

## Learning Paths

### Path 1: AI Engineer (Full Stack)
```
Недели 1-2: Level 1 + Level 2
Недели 3-4: Level 3 + Tutorial RAG
Недели 5-6: Level 4 + Tutorial Agent
Неделя 7:   Level 5.3 + Level 6
```

### Path 2: RAG Specialist
```
1. [[llm-fundamentals]]
2. [[embeddings-complete-guide]]
3. [[vector-databases-guide]]
4. [[rag-advanced-techniques]]
5. [[tutorial-rag-chatbot]]
6. [[tutorial-document-qa]]
7. [[ai-cost-optimization]]
```

### Path 3: Agent Developer
```
1. [[llm-fundamentals]]
2. [[prompt-engineering-masterclass]]
3. [[structured-outputs-tools]]
4. [[ai-agents-advanced]]
5. [[agent-frameworks-comparison]]
6. [[tutorial-ai-agent]]
7. [[ai-observability-monitoring]]
```

### Path 4: ML Ops / Platform
```
1. [[models-landscape-2025]]
2. [[llm-inference-optimization]]
3. [[local-llms-self-hosting]]
4. [[mobile-ai-ml-guide]]
5. [[ai-devops-deployment]]
6. [[ai-observability-monitoring]]
7. [[ai-cost-optimization]]
8. [[ai-tools-ecosystem-2025]]
```

---

## Карта связей

```
                    ┌──────────────────────┐
                    │  ai-ml-overview-v2   │
                    │       (MOC)          │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   MODELS &    │    │     RAG &     │    │   AGENTS &    │
│  FOUNDATIONS  │    │  EMBEDDINGS   │    │    TOOLS      │
├───────────────┤    ├───────────────┤    ├───────────────┤
│llm-fundamentals│   │embeddings-    │    │ai-agents-     │
│models-landscape│   │  complete     │    │  advanced     │
│reasoning-     │    │vector-dbs     │    │agent-frameworks│
│  models       │    │rag-advanced   │    │structured-    │
│multimodal-ai  │    │tutorial-rag   │    │  outputs      │
└───────────────┘    │tutorial-doc-qa│    │tutorial-agent │
                     └───────────────┘    │mcp-protocol   │
                                          └───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PRODUCTION   │    │  OBSERVABILITY│    │   ECOSYSTEM   │
├───────────────┤    ├───────────────┤    ├───────────────┤
│llm-inference  │    │ai-observability│   │ai-tools-      │
│local-llms     │    │ai-cost-       │    │  ecosystem    │
│mobile-ai-ml   │    │  optimization │    │ai-engineering │
│ai-devops      │    └───────────────┘    │  -intro       │
└───────────────┘                         └───────────────┘
```

---

## Deprecated материалы

Следующие материалы устарели и заменены новыми:

| Старый | Заменён на |
|--------|------------|
| ai-ml-overview.md | **ai-ml-overview-v2.md** (этот файл) |
| ai-engineer-roadmap.md | [[ai-engineering-intro]] + Level structure |
| ai-engineer-tech-stack.md | [[ai-tools-ecosystem-2025]] |
| rag-and-prompt-engineering.md | [[rag-advanced-techniques]] + [[prompt-engineering-masterclass]] |
| ai-agents-autonomous-systems.md | [[ai-agents-advanced]] |
| ai-fine-tuning-adaptation.md | Частично в [[models-landscape-2025]] |
| ai-evaluation-metrics.md | [[ai-observability-monitoring]] |
| ai-production-systems.md | [[ai-devops-deployment]] |

---

## Changelog

### Version 2.0 (Январь 2025)
- Полная переработка на основе 2025 research
- 22 новых/обновлённых материала
- 6-уровневая структура обучения
- Практические туториалы с кодом
- Актуальные сравнения инструментов

---

## Следующие шаги

После освоения материалов:

1. **Постройте проект** — используйте туториалы как основу
2. **Изучите исходники** — LangChain, LlamaIndex, vLLM
3. **Следите за трендами** — подпишитесь на AI newsletters
4. **Практикуйтесь** — участвуйте в хакатонах
5. **Делитесь знаниями** — пишите статьи, выступайте

---

**Удачи в изучении AI Engineering!**

---

*Проверено: 2026-01-09*

---

## Проверь себя

> [!question]- Почему RAG-подход часто предпочтительнее fine-tuning для корпоративных приложений?
> Fine-tuning "вшивает" знания в веса модели -- это дорого, медленно обновляется и не даёт ссылок на источники. RAG позволяет: (1) обновлять данные без переобучения -- достаточно обновить документы в векторной базе; (2) давать ответы с указанием источника, что критично для доверия; (3) работать с конфиденциальными данными без их попадания в модель. Fine-tuning оправдан для изменения стиля/формата ответов, а RAG -- для работы с актуальными знаниями.

> [!question]- Компания хочет внедрить AI-агента для автоматизации поддержки клиентов. Какой Learning Path из карты вы бы выбрали и какие два аспекта из Level 4 критически важны до запуска?
> Оптимальный путь -- Path 3 (Agent Developer): от основ LLM через prompt engineering и structured outputs к агентам и фреймворкам. Из Level 4 критичны: (1) **Observability** (ai-observability-monitoring) -- без мониторинга невозможно отследить галлюцинации и деградацию качества в production; (2) **Cost optimization** (ai-cost-optimization) -- агенты выполняют цепочки вызовов LLM, и без prompt caching и model routing затраты могут вырасти в 10-50 раз относительно ожиданий.

> [!question]- В чём принципиальная разница между AI Engineer и ML Engineer, и почему это важно при планировании карьеры?
> ML Engineer фокусируется на обучении моделей с нуля: сбор данных, архитектура нейросетей, эксперименты с гиперпараметрами. AI Engineer использует уже готовые модели (GPT-4o, Claude, Gemini) как "строительные блоки" для создания приложений: промпты, RAG, агенты, orchestration. Это важно для карьеры, потому что AI Engineering имеет значительно более низкий порог входа (не нужна PhD и знание PyTorch), растущий рынок вакансий, и позволяет быстрее создавать бизнес-ценность.

> [!question]- Вы строите RAG-систему и получаете нерелевантные ответы. Какие три уровня pipeline стоит проверить и в каком порядке?
> Проверять нужно снизу вверх: (1) **Chunking** -- возможно, документы нарезаны слишком крупно или слишком мелко, и семантические единицы разорваны; (2) **Retrieval** -- проверить качество embeddings, параметры поиска (top-k, threshold), попробовать hybrid search (вектор + BM25) и reranking; (3) **Generation** -- убедиться, что system prompt правильно инструктирует модель использовать только найденный контекст. Порядок важен: если чанки плохие, никакой reranking или prompt не поможет.

---

## Ключевые карточки

AI Engineering vs ML Engineering -- в чём разница?
?
AI Engineer строит приложения на основе **готовых LLM** (промпты, RAG, агенты). ML Engineer **обучает модели** с нуля (данные, архитектура, гиперпараметры). AI Engineering = "software engineering поверх LLM".

Что такое RAG и из каких трёх этапов состоит pipeline?
?
RAG (Retrieval-Augmented Generation) -- LLM ищет в документах перед ответом. Этапы: (1) **Indexing** -- нарезка документов на чанки и создание embeddings; (2) **Retrieval** -- поиск релевантных чанков по запросу; (3) **Generation** -- LLM генерирует ответ на основе найденного контекста.

Что такое embedding и почему "похожие тексты = близкие координаты"?
?
Embedding -- числовой вектор (например, 1536 чисел), представляющий **смысл** текста. Модель обучена так, что семантически близкие тексты получают близкие векторы в многомерном пространстве. Это позволяет находить релевантные документы через **cosine similarity** без точного совпадения слов.

Назовите 4 ключевых техники prompt engineering
?
(1) **Zero-shot** -- задача без примеров; (2) **Few-shot** -- задача с 2-5 примерами; (3) **Chain-of-Thought (CoT)** -- пошаговое рассуждение; (4) **ReAct** -- рассуждение + действие (reasoning + acting). Выбор техники зависит от сложности задачи и наличия примеров.

Что такое Context Window и почему это ограничение критично?
?
Context window -- максимальный объём текста (в токенах), который модель может "видеть" одновременно. Например, GPT-4o -- 128K токенов, Claude -- 200K. Ограничение критично для RAG: если контекст не вмещает все релевантные чанки, модель не сможет их учесть. Также влияет на стоимость -- больше токенов = дороже запрос.

AI Agent vs обычный LLM-вызов -- в чём отличие?
?
Обычный вызов: вопрос -> ответ (один шаг). Agent: LLM получает **инструменты** (поиск, калькулятор, API) и может **самостоятельно решать**, какие использовать, выполнять действия в цикле (observe -> think -> act), и останавливаться по достижению цели. Ключевые паттерны: ReAct, Plan-and-Execute, Reflection.

Prompt caching -- что это и какую экономию даёт?
?
Prompt caching -- повторное использование уже обработанных частей промпта (system prompt, few-shot примеры). Провайдеры кэшируют prefix промпта и при повторных вызовах не пересчитывают его. Экономия: до **90%** стоимости на cached-токенах. Особенно эффективно для RAG и агентов с длинным system prompt.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[llm-fundamentals]] | Понять архитектуру Transformer, токенизацию и attention -- база для всего остального |
| Модели | [[models-landscape-2025]] | Сравнить GPT-4o, Claude, Gemini, DeepSeek и выбрать модель под задачу |
| Практика | [[tutorial-rag-chatbot]] | Построить первый RAG-проект с LangChain + ChromaDB от начала до конца |
| Агенты | [[ai-agents-advanced]] | Освоить паттерны ReAct, Plan-and-Execute и мультиагентные системы |
| Смежная область | [[design-patterns-overview]] | Паттерны проектирования -- пригодятся при архитектуре AI-приложений |
| Инфраструктура | [[ai-devops-deployment]] | Docker, Kubernetes для AI, CI/CD pipeline и стратегии деплоя |
| Карьера | [[ai-era-job-search]] | Стратегия поиска работы в эпоху AI -- как позиционировать AI-навыки |

---

## Источники

### Теоретические основы
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson.
- Turing, A. (1950). *Computing Machinery and Intelligence*. Mind, 59(236), 433-460.
- McCarthy, J. et al. (1956). *A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence*.
- Bostrom, N. (2014). *Superintelligence: Paths, Dangers, Strategies*. Oxford University Press.
- Bommasani, R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258. Stanford CRFM.
- Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS.
- Brown, T. et al. (2020). *Language Models are Few-Shot Learners*. NeurIPS. (GPT-3)
- Krizhevsky, A. et al. (2012). *ImageNet Classification with Deep Convolutional Neural Networks*. NeurIPS. (AlexNet)

### Практические руководства
- Huyen, C. (2024). *AI Engineering: Building Applications with Foundation Models*. O'Reilly.
- [roadmap.sh: AI Engineer Roadmap](https://roadmap.sh/ai-engineer)
- [Stanford AI100: Gathering Strength, Gathering Storms](https://ai100.stanford.edu/) — ежегодный отчёт о прогрессе AI
