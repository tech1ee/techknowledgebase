# AI-ML Curriculum Plan: От нуля до Senior AI Engineer

> **Дата аудита:** 2026-01-11
> **Текущий статус:** 78% покрытие (26 активных файлов, ~36,000 строк)
> **Цель:** 100% покрытие для пути от новичка до Senior AI Engineer

---

## Результаты аудита

### Сильные стороны (5/5)
- LLM Theory: transformers, attention, MoE, RoPE
- RAG Systems: от базового до GraphRAG, Self-RAG, CRAG + туториал
- Agents: философия → фреймворки → MCP → multi-agent
- Production: DevOps, K8s, GPU, costs, monitoring
- API Integration: OpenAI, Anthropic, Google + structured outputs

### Критические пробелы (требуют заполнения)

| Приоритет | Тема | Статус | Действие |
|-----------|------|--------|----------|
| P0 | Fine-tuning & Adaptation | В архиве | Промоутить + обновить для 2025 |
| P0 | Security & Safety | Отсутствует | Создать новый гайд |
| P0 | Testing & Evaluation | Частично | Промоутить + расширить |
| P0 | Data Preparation | Отсутствует | Создать новый гайд |
| P1 | Advanced Retrieval | Частично | Создать deep-dive |
| P1 | Multi-Agent Production | Частично | Расширить patterns |
| P2 | Business ROI & Strategy | Отсутствует | Создать гайд |
| P2 | Career Path | Частично | Создать roadmap |

---

## Новая структура (Learning Path)

```
AI ENGINEERING CURRICULUM
│
├── УРОВЕНЬ 0: Prerequisites (что нужно знать до старта)
│   ├── 00-python-for-ai.md (NEW)          ← Python basics для AI
│   ├── 00-api-basics.md (NEW)             ← REST, JSON, HTTP
│   └── 00-math-intuition.md (NEW)         ← Линейная алгебра интуитивно
│
├── УРОВЕНЬ 1: Foundations (фундамент)
│   ├── ai-engineering-intro.md            ← Что такое AI Engineering
│   ├── llm-fundamentals.md                ← Как работают LLM
│   ├── ai-api-integration.md              ← Первые API вызовы
│   └── prompt-engineering-basics.md (NEW) ← Базовый промптинг
│
├── УРОВЕНЬ 2: Core Skills (ключевые навыки)
│   ├── embeddings-complete-guide.md       ← Эмбеддинги
│   ├── vector-databases-guide.md          ← Векторные БД
│   ├── rag-fundamentals.md (NEW)          ← Базовый RAG
│   ├── structured-outputs-tools.md        ← Function calling
│   └── prompt-engineering-masterclass.md  ← Продвинутый промптинг
│
├── УРОВЕНЬ 3: Production Skills (продакшн)
│   ├── rag-advanced-techniques.md         ← Продвинутый RAG
│   ├── ai-agents-advanced.md              ← Агенты
│   ├── ai-data-preparation.md (NEW)       ← Подготовка данных
│   ├── ai-fine-tuning-guide.md (PROMOTE)  ← Fine-tuning
│   ├── ai-testing-evaluation.md (PROMOTE) ← Тестирование
│   └── ai-security-safety.md (NEW)        ← Безопасность
│
├── УРОВЕНЬ 4: Advanced (продвинутый)
│   ├── llm-inference-optimization.md      ← Оптимизация
│   ├── local-llms-self-hosting.md         ← Self-hosting
│   ├── mcp-model-context-protocol.md      ← MCP
│   ├── advanced-retrieval-patterns.md (NEW) ← Advanced retrieval
│   └── multi-agent-production.md (NEW)    ← Multi-agent
│
├── УРОВЕНЬ 5: Architecture & Leadership (архитектура)
│   ├── ai-devops-deployment.md            ← MLOps/LLMOps
│   ├── ai-observability-monitoring.md     ← Observability
│   ├── ai-cost-optimization.md            ← Cost optimization
│   ├── ai-governance-compliance.md (NEW)  ← Governance
│   └── ai-architecture-patterns.md (NEW)  ← System design
│
├── ПРАКТИКА: Tutorials (туториалы)
│   ├── tutorial-first-llm-app.md (NEW)    ← Первое приложение
│   ├── tutorial-rag-chatbot.md            ← RAG чатбот
│   ├── tutorial-ai-agent.md               ← Агент
│   ├── tutorial-document-qa.md            ← Document QA
│   └── tutorial-multimodal.md (NEW)       ← Multimodal
│
├── СПРАВОЧНИКИ: Reference (справочные)
│   ├── models-landscape-2025.md           ← Ландшафт моделей
│   ├── ai-tools-ecosystem-2025.md         ← Экосистема
│   ├── agent-frameworks-comparison.md     ← Сравнение фреймворков
│   ├── reasoning-models-guide.md          ← Reasoning модели
│   └── multimodal-ai-guide.md             ← Multimodal
│
└── КАРЬЕРА: Career (карьерный путь)
    ├── ai-engineer-roadmap.md (NEW)       ← Roadmap
    └── ai-interview-preparation.md (NEW)  ← Подготовка к интервью
```

---

## План реализации

### Фаза 1: Промоутить из архива (1 день)

1. **ai-fine-tuning-adaptation.md** → **ai-fine-tuning-guide.md**
   - Добавить: LoRA, QLoRA, DPO, ORPO
   - Добавить: When to fine-tune vs RAG
   - Добавить: Cost analysis

2. **ai-evaluation-metrics.md** → **ai-testing-evaluation.md**
   - Добавить: Unit tests for prompts
   - Добавить: Integration testing
   - Добавить: CI/CD for AI

### Фаза 2: Критические новые гайды (2-3 дня)

3. **ai-security-safety.md** (NEW)
   - Prompt injection attacks
   - Data leakage prevention
   - Rate limiting
   - Compliance (GDPR, HIPAA)

4. **ai-data-preparation.md** (NEW)
   - Chunking strategies
   - Data quality metrics
   - Synthetic data generation
   - Annotation workflows

### Фаза 3: Prerequisites для новичков (1-2 дня)

5. **00-prerequisites-overview.md** (NEW)
   - Python basics check
   - API concepts check
   - Math intuition check

6. **rag-fundamentals.md** (NEW)
   - Простое объяснение RAG
   - Первый RAG за 30 минут
   - Мост к advanced

### Фаза 4: Advanced patterns (2 дня)

7. **advanced-retrieval-patterns.md** (NEW)
   - DPR, ColBERT
   - Query expansion
   - Multi-hop reasoning

8. **multi-agent-production.md** (NEW)
   - Agent hierarchies
   - Consensus patterns
   - Failure recovery

### Фаза 5: Career & Governance (1-2 дня)

9. **ai-governance-compliance.md** (NEW)
   - Model versioning
   - Audit trails
   - Documentation standards

10. **ai-engineer-roadmap.md** (NEW)
    - Junior → Senior path
    - Skills by level
    - Interview preparation

### Фаза 6: Tutorials (2 дня)

11. **tutorial-first-llm-app.md** (NEW)
    - Hello World с LLM
    - От нуля до работающего приложения

12. **tutorial-multimodal.md** (NEW)
    - Vision + text
    - Image understanding RAG

---

## Приоритеты по файлам

### P0 (Критично - эта неделя)

| Файл | Тип | Размер | Описание |
|------|-----|--------|----------|
| ai-security-safety.md | NEW | 60 KB | Безопасность LLM приложений |
| ai-data-preparation.md | NEW | 50 KB | Подготовка данных для RAG/Fine-tuning |
| ai-fine-tuning-guide.md | PROMOTE | 50 KB | Fine-tuning с LoRA, DPO |
| ai-testing-evaluation.md | PROMOTE | 45 KB | Тестирование AI систем |

### P1 (Высокий - в течение 2 недель)

| Файл | Тип | Размер | Описание |
|------|-----|--------|----------|
| rag-fundamentals.md | NEW | 40 KB | Базовый RAG для новичков |
| advanced-retrieval-patterns.md | NEW | 50 KB | Advanced retrieval |
| multi-agent-production.md | NEW | 45 KB | Production multi-agent |
| 00-prerequisites-overview.md | NEW | 30 KB | Чеклист prerequisites |

### P2 (Средний - в течение месяца)

| Файл | Тип | Размер | Описание |
|------|-----|--------|----------|
| ai-governance-compliance.md | NEW | 40 KB | Governance & compliance |
| ai-engineer-roadmap.md | NEW | 35 KB | Career roadmap |
| tutorial-first-llm-app.md | NEW | 40 KB | Первое приложение |
| tutorial-multimodal.md | NEW | 45 KB | Multimodal tutorial |

---

## Методология контента

Каждый новый материал должен содержать:

### Для начинающих (Level 0-1)
```
1. TL;DR (3-5 предложений)
2. Prerequisites (что нужно знать)
3. Аналогия из реального мира
4. Объяснение "для пятилетнего"
5. Первый практический пример (Hello World)
6. Типичные ошибки новичков
7. Следующие шаги
```

### Для среднего уровня (Level 2-3)
```
1. TL;DR
2. Prerequisites matrix
3. Теория с диаграммами
4. Production patterns
5. Code examples (Python)
6. Trade-offs analysis
7. Common mistakes + solutions
8. Deep dive links
```

### Для продвинутых (Level 4-5)
```
1. Executive summary
2. Architecture decisions
3. Performance benchmarks
4. Cost analysis
5. Failure modes & recovery
6. Case studies
7. Research papers references
```

---

## Метрики успеха

| Метрика | Текущее | Цель |
|---------|---------|------|
| Файлов в разделе | 26 | 40+ |
| Покрытие curriculum | 78% | 95% |
| Level 0 (prerequisites) | 0 | 3 |
| Tutorials | 3 | 6 |
| Кросс-ссылок | 396 | 500+ |
| Career guides | 0 | 2 |

---

## Источники для исследования

### Официальная документация
- OpenAI Cookbook
- Anthropic Documentation
- LangChain/LangGraph docs
- LlamaIndex docs

### Курсы и гайды
- DeepLearning.AI courses
- Hugging Face courses
- fast.ai
- Full Stack LLM Bootcamp

### Research papers
- Attention Is All You Need
- RAFT, Self-RAG, CRAG papers
- Constitutional AI
- Chain-of-Thought papers

### Практические ресурсы
- AI Engineer World's Fair talks
- Latent Space podcast
- Simon Willison's blog
- Chip Huyen's blog

---

*План создан: 2026-01-11*
*Статус: В работе*
