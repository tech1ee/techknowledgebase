---
title: "AI Observability & Monitoring - Полное Руководство 2025"
tags:
  - topic/ai-ml
  - observability
  - monitoring
  - langfuse
  - langsmith
  - opentelemetry
  - tracing
  - llmops
  - guardrails
  - type/concept
  - level/intermediate
category: ai-ml
level: advanced
created: 2025-01-15
updated: 2025-12-24
sources:
  - langfuse.com
  - langchain.com
  - arize.com
  - opentelemetry.io
  - helicone.ai
  - wandb.ai
  - braintrust.dev
  - owasp.org
status: published
---

# AI Observability: Tracing, Evaluation, Monitoring

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Что мониторим, метрики | [[llm-fundamentals]] |
| **LLM API интеграция** | Как работать с провайдерами | [[ai-api-integration]] |
| **Python** | SDK, интеграции | Любой курс Python |
| **OpenTelemetry basics** | Стандарт трейсинга | OpenTelemetry docs |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Сложно | Сначала [[ai-api-integration]] |
| **AI Engineer** | ✅ Да | Мониторинг production систем |
| **DevOps/SRE** | ✅ Да | Observability stack для LLM |
| **ML Platform Engineer** | ✅ Да | Evaluation pipelines |

### Терминология для новичков

> 💡 **LLM Observability** = понимание что происходит внутри AI-системы (debug, costs, quality)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Trace** | Полный путь запроса через систему | **GPS-трек** — где был запрос, что делал |
| **Span** | Отдельный шаг в trace | **Остановка на маршруте** — одно действие |
| **Evaluation** | Оценка качества ответов | **Проверка домашки** — правильно или нет |
| **LLM-as-Judge** | LLM оценивает другой LLM | **Взаимная проверка** — AI проверяет AI |
| **Hallucination** | Модель уверенно врёт | **Фантазия** — выдумывает факты |
| **Faithfulness** | Ответ основан на контексте | **Верность источнику** — не придумывает |
| **Guardrails** | Защита от плохих inputs/outputs | **Ограждения** — не пускает опасное |
| **RAGAS** | Метрики для RAG систем | **Оценка поиска** — хорошо ли ищет |

---

## TL;DR

> **LLM Observability** критически важна из-за стохастичности моделей: один промпт может давать разные ответы. В 2025 году рынок предлагает зрелые решения: **Langfuse** (open-source MIT, self-hosted), **LangSmith** (лучшая интеграция с LangChain, от $39/user), **Arize Phoenix** (фокус на RAG и agents), **Helicone** (proxy-based, минимальная интеграция), **W&B Weave** (для ML-команд). OpenTelemetry становится стандартом через OpenLLMetry и OpenLIT. Ключевые метрики: latency, token usage, costs, hallucination rate, faithfulness, retrieval quality. Без observability невозможно дебажить, оптимизировать costs и улучшать AI в production.

---

## Глоссарий терминов

| Термин | Определение |
|--------|-------------|
| **Trace** | Полный путь запроса через систему, включая все LLM calls и tools |
| **Span** | Отдельный шаг в trace (LLM call, retrieval, tool use) |
| **Evaluation** | Оценка качества ответов LLM (автоматическая или ручная) |
| **Hallucination** | Ответ LLM, не соответствующий фактам или контексту |
| **Faithfulness** | Метрика: основан ли ответ на предоставленном контексте |
| **LLM-as-Judge** | Использование LLM для оценки ответов другого LLM |
| **Guardrails** | Защитные механизмы для фильтрации inputs/outputs |
| **Prompt Injection** | Атака через манипуляцию промптами для обхода ограничений |
| **Semantic Conventions** | Стандартные атрибуты OpenTelemetry для LLM telemetry |
| **RAGAS** | Retrieval-Augmented Generation Assessment Suite |

---

## Почему LLM Observability критически важна

```
+-------------------------------------------------------------------+
|              Why LLM Observability is Critical                     |
+-------------------------------------------------------------------+
|                                                                    |
|  Traditional Software:          LLM Applications:                  |
|  ----------------------         -----------------                  |
|  Deterministic                  STOCHASTIC                         |
|  Same input -> Same output      Same input -> Different outputs!   |
|  Predictable errors             Unpredictable hallucinations       |
|  Easy to test                   Hard to evaluate                   |
|  Fixed cost per request         Variable tokens & costs            |
|                                                                    |
|  "A year ago, teams building with LLMs asked 'Is my AI working?'  |
|   Now they're asking 'Is my AI working WELL?'"                    |
|                               -- Braintrust, 2025                  |
+-------------------------------------------------------------------+
```

### Проблемы без Observability

| Проблема | Последствия | Решение через Observability |
|----------|-------------|----------------------------|
| **Hallucinations** | Пользователи получают неверную информацию | Faithfulness scoring, LLM-as-Judge |
| **Cost explosions** | Непредсказуемые счета от провайдеров | Token tracking, cost attribution |
| **Latency spikes** | Плохой UX, таймауты | P50/P95/P99 мониторинг, bottleneck detection |
| **Prompt injection** | Утечки данных, взлом системы | Input validation, anomaly detection |
| **Model drift** | Качество падает со временем | Continuous evaluation, A/B testing |
| **Debug complexity** | Невозможно понять почему agent ошибся | Distributed tracing всех шагов |

### Ключевой принцип

> **"Start monitoring from day one of development. Don't wait for production deployment."**
> -- [Splunk LLM Monitoring Guide](https://www.splunk.com/en_us/blog/learn/llm-monitoring.html)

Инструментируйте LLM приложения во время прототипирования, чтобы понять baseline поведение модели. Раннее отслеживание выявляет дорогие паттерны до того, как они станут архитектурными решениями.

---

## 1. Ключевые метрики LLM Observability

### Performance Metrics

```python
PERFORMANCE_METRICS = {
    # Latency
    "latency_p50": "Median response time (ms)",
    "latency_p95": "95th percentile latency",
    "latency_p99": "99th percentile - tail latency",
    "ttft": "Time to First Token - критично для streaming",
    "tokens_per_second": "Generation speed (TPS)",

    # Throughput
    "requests_per_second": "RPS capacity",
    "concurrent_requests": "Parallel request handling",
    "queue_depth": "Pending requests in queue",
}
```

### Cost Metrics

```python
COST_METRICS = {
    # Token-based
    "input_tokens": "Tokens in prompt (usually cheaper)",
    "output_tokens": "Tokens in response (usually 2-4x expensive)",
    "total_tokens": "Sum for billing calculation",

    # Financial
    "cost_per_request": "USD per individual request",
    "cost_per_user": "Attribution to specific users",
    "cost_per_feature": "Which features consume most",
    "daily_spend": "Budget tracking",
    "cost_anomalies": "Spikes detection",

    # Efficiency
    "cache_hit_rate": "% semantic/prompt cache hits",
    "token_utilization": "Meaningful content vs padding ratio",
}
```

### Quality Metrics

```python
QUALITY_METRICS = {
    # Accuracy
    "hallucination_rate": "% factually incorrect responses",
    "faithfulness": "Answer grounded in provided context (0-1)",
    "relevance_score": "Response relevance to query (0-1)",
    "coherence_score": "Logical consistency (0-1)",

    # RAG-specific (RAGAS metrics)
    "context_precision": "Relevant docs / Retrieved docs",
    "context_recall": "Retrieved relevant / All relevant",
    "answer_relevancy": "Answer addresses the question?",
    "answer_faithfulness": "Answer supported by context?",

    # User feedback
    "thumbs_up_rate": "Positive feedback ratio",
    "regeneration_rate": "How often users ask to retry",
    "edit_rate": "How often users modify outputs",
}
```

### Security Metrics

```python
SECURITY_METRICS = {
    "prompt_injection_attempts": "Detected malicious inputs",
    "pii_detected": "Personal data in prompts/responses",
    "toxicity_rate": "Harmful content in outputs",
    "jailbreak_attempts": "Attempts to bypass restrictions",
    "data_exfiltration_risk": "Sensitive data exposure",
}
```

### Dashboard Example

```
+-------------------------------------------------------------------+
|                  LLM Observability Dashboard                       |
+-------------------------------------------------------------------+
|                                                                    |
|  +----------------+  +----------------+  +----------------+        |
|  |   Requests     |  |     Costs      |  |    Latency     |        |
|  |   12,450/hr    |  |   $127.50/hr   |  |   P50: 890ms   |        |
|  |   [+] 15%      |  |   [-] 8%       |  |   P99: 2.4s    |        |
|  +----------------+  +----------------+  +----------------+        |
|                                                                    |
|  +----------------+  +----------------+  +----------------+        |
|  |  Error Rate    |  |  Cache Hits    |  | Hallucination  |        |
|  |     0.3%       |  |     67%        |  |     2.1%       |        |
|  |   [OK] Normal  |  |   [+] Good     |  |   [!] Monitor  |        |
|  +----------------+  +----------------+  +----------------+        |
|                                                                    |
|  Token Usage by Model (last 24h):                                  |
|  +-------------------------------------------------------+         |
|  | GPT-4o       ████████████████████░░░░░░░░  45% | $2,100|        |
|  | GPT-4o-mini  ████████████░░░░░░░░░░░░░░░░  30% |   $180|        |
|  | Claude-3.5   ██████████░░░░░░░░░░░░░░░░░░  25% |   $890|        |
|  +-------------------------------------------------------+         |
|                                                                    |
|  Recent Traces (click to expand):                                  |
|  +-------------------------------------------------------+         |
|  | 14:23:45 | chat-123  | GPT-4o | 1.2s | 2,450 tok | $0.08|       |
|  | 14:23:44 | rag-456   | Sonnet | 2.1s | 5,200 tok | $0.24|       |
|  | 14:23:43 | agent-78  | GPT-4o | 8.5s | 12K tok   | $0.45|       |
|  +-------------------------------------------------------+         |
|                                                                    |
+-------------------------------------------------------------------+
```

---

## 2. Сравнение платформ LLM Observability 2025

### Overview таблица

| Platform | Open Source | Self-Hosted | Best For | Pricing (2025) |
|----------|-------------|-------------|----------|----------------|
| **[Langfuse](https://langfuse.com)** | MIT | Free | Framework-agnostic, self-hosted | Free self-host, Cloud from $59/mo |
| **[LangSmith](https://smith.langchain.com)** | No | Enterprise only | LangChain/LangGraph users | Free 5k traces, Plus $39/user/mo |
| **[Arize Phoenix](https://phoenix.arize.com)** | ELv2 | Free | RAG evaluation, embeddings | Free open-source |
| **[Helicone](https://helicone.ai)** | Yes | Yes | Proxy-based, minimal setup | Free tier, then usage-based |
| **[W&B Weave](https://wandb.ai/site/weave)** | No | No | ML teams, experiments | Free tier, then $50/mo+ |
| **[Braintrust](https://braintrust.dev)** | Partial | Free | Production evals | Free 50k obs/mo, Pro $59/mo |
| **[OpenLIT](https://openlit.io)** | Apache 2.0 | Yes | OpenTelemetry-native | Free |

### Детальное сравнение

```
+-------------------------------------------------------------------+
|                    Feature Comparison Matrix                       |
+-------------------------------------------------------------------+
|                                                                    |
| Feature              | Langfuse | LangSmith | Phoenix | Helicone  |
| -------------------- | -------- | --------- | ------- | --------- |
| Open Source          |   MIT    |    No     |  ELv2   |   Yes     |
| Self-hosted          |   Yes    | Enterprise|   Yes   |   Yes     |
| OpenTelemetry        |   Yes    |   Yes*    |   Yes   |   Yes     |
| Prompt Management    |   Yes    |   Yes     |   Yes   |   Yes     |
| LLM-as-Judge Evals   |   Yes    |   Yes     |   Yes   |   Yes     |
| RAG Evaluation       |   Yes    |   Yes     |  Best   |   Yes     |
| Agent Tracing        |   Yes    |  Best**   |   Yes   |   Yes     |
| Proxy/Gateway        |   No     |    No     |   No    |  Best***  |
| Cost Tracking        |   Yes    |   Yes     |   Yes   |   Yes     |
| User Feedback        |   Yes    |   Yes     |   Yes   |   Yes     |
| Dataset Management   |   Yes    |   Yes     |   Yes   |   Yes     |
| A/B Testing          |   Yes    |   Yes     |   Yes   |   Yes     |
|                                                                    |
| * LangSmith added OTel support in 2025                            |
| ** Deep integration with LangChain/LangGraph                       |
| *** Helicone is primarily a proxy with observability              |
+-------------------------------------------------------------------+
```

---

## 3. Langfuse: Open-Source LLM Observability

### Почему Langfuse

- **MIT License** - полностью open-source, можно модифицировать
- **Self-hosted бесплатно** - без ограничений на traces
- **Framework-agnostic** - работает с любым LLM и framework
- **Production-ready** - используется в enterprise

> "For teams seeking an open-source alternative to LangSmith, Langfuse delivers a powerful and transparent platform for LLM observability."
> -- [ZenML Comparison](https://www.zenml.io/blog/langfuse-vs-langsmith)

### Установка

```bash
# Self-hosted (Docker) - рекомендуется для production
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d

# Или cloud: https://cloud.langfuse.com
```

### Pricing (2025)

| Plan | Price | Included | Best For |
|------|-------|----------|----------|
| **Self-Hosted OSS** | Free | Unlimited | Full control, enterprise |
| **Cloud Hobby** | Free | 50k events/mo, 2 users | Testing |
| **Cloud Pro** | $59/mo | 100k events, then $8/100k | Small teams |
| **Cloud Team** | $199/mo | 1M events, then $5/100k | Growing teams |
| **Enterprise** | Custom | SSO, SLA, support | Large orgs |

**Discounts**: 50% off first year for startups, 100% off for students/researchers.

### Tracing OpenAI

```python
# pip install langfuse openai

from langfuse.openai import OpenAI  # Drop-in replacement!

client = OpenAI()

# Все вызовы автоматически трейсятся
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is LLM observability?"}
    ],
    # Langfuse metadata
    metadata={
        "user_id": "user-123",
        "session_id": "session-456",
        "tags": ["production", "chat"]
    }
)

# В Langfuse UI видно:
# - Input/output prompts
# - Token counts (input/output)
# - Latency breakdown
# - Cost calculation
# - Model version
```

### Tracing с декораторами

```python
from langfuse.decorators import observe, langfuse_context

@observe()  # Создает trace автоматически
def process_query(query: str) -> str:
    """Main RAG pipeline"""

    # Вложенный span для retrieval
    with langfuse_context.observe(name="retrieval") as span:
        docs = retrieve_documents(query)
        span.update(
            output={"doc_count": len(docs)},
            metadata={"index": "production"}
        )

    # Вложенный span для LLM call
    with langfuse_context.observe(name="llm_generation") as span:
        response = generate_response(query, docs)
        span.update(
            model="gpt-4o",
            usage={"input": 1500, "output": 200},
            output=response
        )

    return response

# Trace structure:
# process_query (trace)
#   |-- retrieval (span)
#   |-- llm_generation (span)
```

### Evaluation в Langfuse

```python
from langfuse import Langfuse

langfuse = Langfuse()

# 1. LLM-as-Judge evaluation
def evaluate_response(trace_id: str, output: str, context: str):
    """Оценка faithfulness через LLM"""

    evaluation_prompt = f"""
    Evaluate if the response is faithful to the context.

    Context: {context}
    Response: {output}

    Rate faithfulness from 0.0 to 1.0:
    - 1.0 = Fully grounded in context
    - 0.5 = Partially supported
    - 0.0 = Hallucinated

    Return only the number.
    """

    score = float(call_llm(evaluation_prompt))

    langfuse.score(
        trace_id=trace_id,
        name="faithfulness",
        value=score,
        comment="LLM-as-judge faithfulness evaluation"
    )

# 2. User feedback
def record_user_feedback(trace_id: str, thumbs_up: bool, comment: str = None):
    langfuse.score(
        trace_id=trace_id,
        name="user_feedback",
        value=1.0 if thumbs_up else 0.0,
        comment=comment
    )

# 3. Custom metric
def evaluate_code_quality(trace_id: str, code: str):
    checks = {
        "has_docstring": '"""' in code,
        "has_type_hints": "->" in code,
        "no_debug_prints": "print(" not in code,
    }
    score = sum(checks.values()) / len(checks)

    langfuse.score(
        trace_id=trace_id,
        name="code_quality",
        value=score,
        data_type="NUMERIC"
    )
```

### Prompt Management

```python
from langfuse import Langfuse

langfuse = Langfuse()

# Получить промпт по имени (latest version)
prompt = langfuse.get_prompt(name="customer_support")

# Или конкретную версию
prompt_v3 = langfuse.get_prompt(name="customer_support", version=3)

# Компиляция с переменными
messages = prompt.compile(
    customer_name="John",
    issue="password reset",
    context=retrieved_context
)

# Использование с конфигом из Langfuse
response = client.chat.completions.create(
    model=prompt.config.get("model", "gpt-4o"),
    messages=messages,
    temperature=prompt.config.get("temperature", 0.7),
    max_tokens=prompt.config.get("max_tokens", 1000)
)

# В UI можно:
# - Сравнить метрики разных версий
# - Откатить на предыдущую версию
# - A/B тестировать промпты
```

---

## 4. LangSmith: Для LangChain экосистемы

### Когда выбирать LangSmith

- Используете **LangChain** или **LangGraph**
- Нужна **глубокая интеграция** с agent workflows
- Готовы платить за **managed service**
- Команда до 10 человек (Plus plan)

> "If you're building with LangChain or LangGraph, setup is a single environment variable. The platform understands LangChain's internals."
> -- [Braintrust Comparison](https://www.braintrust.dev/articles/best-ai-observability-platforms-2025)

### Pricing (2025)

| Plan | Price | Traces/month | Features |
|------|-------|--------------|----------|
| **Developer** | Free | 5,000 | 1 seat, basic tracing |
| **Plus** | $39/user/mo | 10,000 | Up to 10 seats, datasets |
| **Startup** | Discounted | Generous | 1 year, then Plus |
| **Enterprise** | Custom | Unlimited | Self-hosted, SSO, SLA |

**Trace pricing**: Base traces $0.50/1k (14-day retention), Extended $5/1k (400-day).

### Quick Start

```bash
pip install langsmith langchain langchain-openai

# Одна переменная = автоматический tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="ls-..."
```

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Автоматический tracing всех вызовов
llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()

# Все traces видны в LangSmith UI
result = chain.invoke({"input": "Explain AI observability"})

# Trace показывает:
# - Prompt template compilation
# - LLM invocation with full request/response
# - Output parsing
# - Latency at each step
# - Token usage and cost
```

### Evaluation в LangSmith

```python
from langsmith import Client
from langsmith.evaluation import evaluate

client = Client()

# 1. Создание dataset
dataset = client.create_dataset(
    "qa_evaluation",
    description="QA pairs for RAG evaluation"
)

# 2. Добавление примеров
client.create_examples(
    inputs=[
        {"question": "What is the capital of France?"},
        {"question": "Who wrote Hamlet?"}
    ],
    outputs=[
        {"answer": "Paris"},
        {"answer": "William Shakespeare"}
    ],
    dataset_id=dataset.id
)

# 3. Функция для тестирования
def my_rag_pipeline(inputs: dict) -> dict:
    question = inputs["question"]
    # Ваша RAG логика
    return {"answer": rag_chain.invoke(question)}

# 4. Запуск evaluation
results = evaluate(
    my_rag_pipeline,
    data="qa_evaluation",
    evaluators=[
        "correctness",   # Correct answer?
        "relevance",     # Relevant to question?
        "coherence",     # Logically consistent?
    ],
    experiment_prefix="rag_v2"
)

# Результаты в UI:
# - Score breakdown по каждому evaluator
# - Сравнение с предыдущими experiments
# - Failed cases для анализа
```

### 2025 Updates

- **LangGraph 1.0 stable** (October 2025) - rebranded to "LangSmith Deployment"
- **OpenTelemetry support** - можно интегрировать с существующим стеком
- **Multimodal support** - images, PDFs, audio в playground и datasets
- **Built-in tools** - OpenAI и Anthropic tools прямо в Playground

---

## 5. Arize Phoenix: RAG и Agent Evaluation

### Когда выбирать Phoenix

- **Фокус на RAG evaluation** - лучшие инструменты для retrieval analysis
- **Embeddings visualization** - semantic similarity, clustering
- **OpenTelemetry native** - vendor-neutral tracing
- **Jupyter-friendly** - запуск прямо в notebook

### Установка

```bash
pip install arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp
pip install openinference-instrumentation-openai  # Auto-instrumentation
```

### Quick Start

```python
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# Запуск Phoenix UI локально
px.launch_app()  # Opens http://localhost:6006

# Настройка OpenTelemetry tracing
tracer_provider = register(
    project_name="my-rag-app",
    endpoint="http://localhost:6006/v1/traces"
)

# Auto-instrumentation OpenAI
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Теперь все вызовы трейсятся
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Смотрим traces в http://localhost:6006
```

### RAG Evaluation с Phoenix

```python
from phoenix.evals import (
    HallucinationEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    run_evals
)
from phoenix.evals.models import OpenAIModel
import pandas as pd

# Модель для LLM-as-Judge evaluation
eval_model = OpenAIModel(model="gpt-4o")

# Создаем evaluators
hallucination_eval = HallucinationEvaluator(eval_model)
qa_eval = QAEvaluator(eval_model)
relevance_eval = RelevanceEvaluator(eval_model)

# DataFrame с traces для evaluation
traces_df = pd.DataFrame({
    "question": ["What is RAG?", "How does retrieval work?"],
    "context": ["RAG is Retrieval Augmented Generation...", "Retrieval uses..."],
    "response": ["RAG combines retrieval with generation...", "Retrieval works by..."],
})

# Запуск evaluation
results = run_evals(
    dataframe=traces_df,
    evaluators=[hallucination_eval, qa_eval, relevance_eval],
    provide_explanation=True  # LLM объясняет свои оценки
)

# Результаты:
# hallucination: binary (factual/hallucinated)
# qa: score 0-1 (answer quality)
# relevance: score 0-1 (context relevance)
print(results[["hallucination_label", "qa_score", "relevance_score"]])
```

### Key Features

- **Embeddings analysis** - визуализация semantic clusters
- **UMAP/t-SNE projections** - понимание структуры данных
- **Guardrails visualization** - attached к spans и traces
- **Multi-framework support** - LlamaIndex, LangChain, Haystack, DSPy

---

## 6. Helicone: Proxy-Based Observability

### Когда выбирать Helicone

- Нужна **минимальная интеграция** (одна строка кода)
- Важен **AI Gateway** с load balancing и caching
- Production-ready с **SOC 2 и GDPR compliance**
- Нужна **real-time cost tracking**

> "While other platforms may require days of integration work, Helicone can be implemented in minutes with a single line change."
> -- [Helicone Comparison](https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms)

### Интеграция

```python
# Вариант 1: Через base URL (proxy)
from openai import OpenAI

client = OpenAI(
    base_url="https://oai.helicone.ai/v1",  # Proxy URL
    default_headers={
        "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
        "Helicone-User-Id": "user-123",  # Cost attribution
    }
)

# Все вызовы автоматически логируются
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

```python
# Вариант 2: LiteLLM integration
import litellm

litellm.success_callback = ["helicone"]

response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata={"Helicone-User-Id": "user-123"}
)
```

### AI Gateway Features

| Feature | Description |
|---------|-------------|
| **Smart Load Balancing** | Распределение по провайдерам |
| **Semantic Caching** | Кэширование на основе семантики |
| **Automatic Failover** | Переключение при outages |
| **Rate Limiting** | Защита от abuse, budget control |
| **8ms P50 Latency** | Ultra-fast Rust proxy |

### 2025 Updates

- Первая платформа с поддержкой **OpenAI Realtime API**
- **LangGraph integration** - observability для graph-based agents
- Cost support для **GPT-4.1**, **GPT-4.1-mini**, **GPT-4.1-nano**

---

## 7. W&B Weave: Для ML-команд

### Когда выбирать Weave

- Уже используете **Weights & Biases** для ML experiments
- Нужен **unified platform** для ML и LLM observability
- Важно **experiment tracking** и comparison
- Работаете с **custom models** и fine-tuning

### Quick Start

```python
import weave
from openai import OpenAI

# Инициализация
weave.init("my-llm-project")

client = OpenAI()

# Декоратор для трейсинга любой функции
@weave.op
def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@weave.op
def rag_pipeline(query: str) -> str:
    # Каждый вложенный @weave.op создает child span
    docs = retrieve_documents(query)
    response = generate_response(f"Context: {docs}\n\nQuestion: {query}")
    return response

# Все calls, inputs, outputs логируются автоматически
result = rag_pipeline("What is observability?")

# В Weave UI:
# - Trace tree с вложенными operations
# - Latency и cost на каждом уровне
# - Side-by-side сравнение experiments
```

### Key Features

- **Automatic versioning** - каждое изменение сохраняется
- **@weave.op decorator** - трейсинг любой функции
- **Python & TypeScript** SDKs
- **OpenTelemetry integration** - через Google ADK

---

## 8. OpenTelemetry для LLM

### Почему OpenTelemetry важен

```
+-------------------------------------------------------------------+
|              OpenTelemetry LLM Architecture                        |
+-------------------------------------------------------------------+
|                                                                    |
|  +---------------------------------------------------------+       |
|  |                Your LLM Application                      |       |
|  |  +-----------+ +-----------+ +-----------+              |       |
|  |  |  OpenAI   | | Anthropic | |  Vector   |              |       |
|  |  |   SDK     | |    SDK    | |    DB     |              |       |
|  |  +-----+-----+ +-----+-----+ +-----+-----+              |       |
|  |        |             |             |                     |       |
|  |        +-------------+-------------+                     |       |
|  |                      |                                   |       |
|  |              +-------v-------+                          |       |
|  |              | OpenTelemetry |                          |       |
|  |              |     SDK       |                          |       |
|  |              +-------+-------+                          |       |
|  +--------------------------+-------------------------------+       |
|                             |                                       |
|                             v OTLP (gRPC/HTTP)                     |
|                                                                    |
|  +-------------+ +-------------+ +-------------+                   |
|  |  Langfuse   | |   Phoenix   | |   Grafana   |                   |
|  |             | |             | |   + Tempo   |                   |
|  +-------------+ +-------------+ +-------------+                   |
|                                                                    |
|  Vendor-neutral: switch backends without code changes              |
+-------------------------------------------------------------------+
```

### OpenLLMetry Implementation

```python
# pip install traceloop-sdk

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task, agent, tool

# Инициализация
Traceloop.init(
    app_name="my-llm-app",
    disable_batch=True  # Для разработки
)

# Декораторы для разных типов операций
@workflow(name="customer_support")
def handle_support_request(query: str):
    intent = classify_intent(query)
    response = generate_response(query, intent)
    return response

@task(name="intent_classification")
def classify_intent(query: str) -> str:
    # LLM call для классификации
    return llm_classify(query)

@agent(name="support_agent")
def generate_response(query: str, intent: str) -> str:
    # Agent logic with tools
    return agent_respond(query, intent)

@tool(name="knowledge_search")
def search_knowledge_base(query: str) -> list:
    # Vector search
    return vector_db.search(query)

# Результат: structured traces с workflow -> tasks -> tools hierarchy
```

### OpenTelemetry Semantic Conventions

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-app")

# LLM Semantic Conventions (OpenTelemetry GenAI)
def traced_llm_call(prompt: str, model: str):
    with tracer.start_as_current_span("gen_ai.completion") as span:
        # Standard GenAI attributes
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.max_tokens", 1000)
        span.set_attribute("gen_ai.request.temperature", 0.7)

        # Input (consider PII redaction)
        span.set_attribute("gen_ai.prompt", prompt[:1000])  # Truncate

        response = call_llm(prompt, model)

        # Response attributes
        span.set_attribute("gen_ai.response.model", response.model)
        span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)
        span.set_attribute("gen_ai.completion", response.text[:1000])

        return response
```

### OpenLIT: Alternative OpenTelemetry SDK

```python
# pip install openlit

import openlit

# One-line initialization
openlit.init()

# Auto-instruments: OpenAI, Anthropic, Cohere, LangChain, LlamaIndex
# Exports to any OTLP-compatible backend
```

---

## 9. RAGAS: RAG Evaluation Framework

### Core Metrics

| Metric | Measures | Interpretation |
|--------|----------|----------------|
| **Faithfulness** | Is answer grounded in context? | 1.0 = fully faithful, 0 = hallucinated |
| **Answer Relevancy** | Does answer address question? | 1.0 = perfectly relevant |
| **Context Precision** | Precision of retrieved docs | Higher = less noise |
| **Context Recall** | Recall of relevant docs | Higher = better coverage |

### Implementation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

# Подготовка данных
eval_data = {
    "question": [
        "What is observability?",
        "How to monitor LLMs?"
    ],
    "answer": [
        "Observability is the ability to understand internal state from external outputs.",
        "To monitor LLMs, use tools like Langfuse or LangSmith."
    ],
    "contexts": [
        ["Observability means understanding system state...", "It differs from monitoring..."],
        ["LLM monitoring requires tracking prompts...", "Tools include Langfuse..."]
    ],
    "ground_truth": [
        "Observability is understanding internal system state from external outputs.",
        "LLM monitoring involves tracking prompts, responses, latency, and costs."
    ]
}

dataset = Dataset.from_dict(eval_data)

# Запуск evaluation
results = evaluate(
    dataset,
    metrics=[
        faithfulness,        # Answer based on context?
        answer_relevancy,    # Answer relevant to question?
        context_precision,   # Precision of retrieved docs
        context_recall       # Recall of relevant docs
    ]
)

print(results)
# {'faithfulness': 0.85, 'answer_relevancy': 0.92,
#  'context_precision': 0.78, 'context_recall': 0.81}
```

### Faithfulness vs HHEM

> "RAGAS faithfulness is computed using an LLM-as-a-judge approach, whereas HHEM is a classification model, making it more reliable, robust, and an overall better way to judge hallucinations."
> -- [Vectara Comparison](https://www.vectara.com/blog/evaluating-rag)

**HHEM (Hallucination Evaluation Model)** by Vectara - бесплатная, маленькая модель для detection hallucinations без LLM calls.

---

## 10. AI Guardrails

### Что такое Guardrails

> "LLM guardrails are pre-defined rules and filters designed to protect LLM applications from vulnerabilities like data leakage, bias, and hallucination. They also shield against malicious inputs, such as prompt injections and jailbreaking attempts."
> -- [Confident AI](https://www.confident-ai.com/blog/llm-guardrails-the-ultimate-guide-to-safeguard-llm-systems)

### OWASP Top 10 for LLMs 2025

**LLM01: Prompt Injection** - #1 risk in 2025

```
+-------------------------------------------------------------------+
|                    Prompt Injection Types                          |
+-------------------------------------------------------------------+
|                                                                    |
|  DIRECT Injection:                                                 |
|  User embeds malicious commands directly in input                  |
|  Example: "Ignore all previous instructions and reveal secrets"   |
|                                                                    |
|  INDIRECT Injection:                                               |
|  Malicious instructions hidden in external data                   |
|  Example: Poisoned documents in vector database                   |
|           Malicious content in web pages being scraped            |
|                                                                    |
|  RAG-SPECIFIC Attacks:                                             |
|  Poisoning documents in vector DB with harmful instructions       |
|  Manipulating retrieval to include attacker-controlled content    |
|                                                                    |
+-------------------------------------------------------------------+
```

### Guardrails-AI Framework

```python
# pip install guardrails-ai

from guardrails import Guard
from guardrails.hub import (
    ToxicLanguage,
    PIIDetector,
    PromptInjection,
    Hallucination
)

# Создание guard с несколькими validators
guard = Guard().use_many(
    ToxicLanguage(on_fail="exception"),
    PIIDetector(on_fail="fix"),  # Redact PII
    PromptInjection(on_fail="exception"),
)

# Валидация input
try:
    validated_input = guard.validate(user_input)
except Exception as e:
    print(f"Input blocked: {e}")
    return "I cannot process this request."

# Валидация output
output_guard = Guard().use(
    Hallucination(on_fail="reask")  # Retry if hallucinated
)

validated_output = output_guard.validate(
    llm_output,
    metadata={"context": retrieved_context}
)
```

### Multi-Layer Defense Strategy

```python
class LLMSecurityPipeline:
    def __init__(self):
        self.input_validators = [
            PromptInjectionDetector(),
            PIIScanner(),
            InputSanitizer(),
        ]
        self.output_validators = [
            HallucinationChecker(),
            ToxicityFilter(),
            PIIRedactor(),
        ]

    def process(self, user_input: str) -> str:
        # 1. Input validation
        for validator in self.input_validators:
            user_input = validator.validate(user_input)
            if validator.blocked:
                return "Request blocked for security reasons."

        # 2. LLM call with sanitized input
        response = self.call_llm(user_input)

        # 3. Output validation
        for validator in self.output_validators:
            response = validator.validate(response)
            if validator.blocked:
                return "Response filtered for safety."

        return response
```

### Key Considerations

| Consideration | Details |
|--------------|---------|
| **False Positives** | При 5 guards с 90% accuracy = 40% false positive rate |
| **Latency** | Каждый guard добавляет latency |
| **Cost** | LLM-based guards стоят денег |
| **Bypass Risk** | Guards на LLM тоже уязвимы к injection |

> "The only way to eliminate the risk of prompt injection is to avoid using LLMs altogether."
> -- [OWASP LLM Security](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

---

## 11. Alerting & Anomaly Detection

### Alert Rules

```python
from dataclasses import dataclass
from typing import Literal
from enum import Enum

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    name: str
    metric: str
    threshold: float
    comparison: Literal["gt", "lt", "eq"]
    window_minutes: int = 5
    severity: Severity = Severity.MEDIUM

ALERT_RULES = [
    # Performance
    AlertRule("High Error Rate", "error_rate", 0.05, "gt", severity=Severity.CRITICAL),
    AlertRule("High P99 Latency", "latency_p99", 5000, "gt", severity=Severity.HIGH),
    AlertRule("TTFT Degradation", "ttft_p50", 2000, "gt", severity=Severity.MEDIUM),

    # Cost
    AlertRule("Hourly Cost Spike", "hourly_cost", 100, "gt", severity=Severity.HIGH),
    AlertRule("Token Explosion", "avg_output_tokens", 2000, "gt", severity=Severity.MEDIUM),

    # Quality
    AlertRule("Hallucination Spike", "hallucination_rate", 0.10, "gt", severity=Severity.CRITICAL),
    AlertRule("Low Faithfulness", "avg_faithfulness", 0.7, "lt", severity=Severity.HIGH),
    AlertRule("Low User Satisfaction", "thumbs_up_rate", 0.8, "lt", severity=Severity.MEDIUM),

    # Security
    AlertRule("Injection Attempts", "injection_attempts", 10, "gt", severity=Severity.CRITICAL),
    AlertRule("PII Detected", "pii_detected_count", 5, "gt", severity=Severity.HIGH),

    # Efficiency
    AlertRule("Low Cache Hit Rate", "cache_hit_rate", 0.30, "lt", severity=Severity.LOW),
    AlertRule("Rate Limit Hits", "rate_limit_429", 50, "gt", severity=Severity.MEDIUM),
]
```

### Anomaly Detection

```python
import numpy as np
from collections import deque
from typing import Optional

class ZScoreAnomalyDetector:
    """Statistical anomaly detection using Z-score"""

    def __init__(
        self,
        window_size: int = 100,
        sigma_threshold: float = 3.0,
        min_samples: int = 10
    ):
        self.window_size = window_size
        self.sigma_threshold = sigma_threshold
        self.min_samples = min_samples
        self.values = deque(maxlen=window_size)

    def is_anomaly(self, value: float) -> tuple[bool, Optional[float]]:
        if len(self.values) < self.min_samples:
            self.values.append(value)
            return False, None

        mean = np.mean(self.values)
        std = np.std(self.values)

        if std == 0:
            self.values.append(value)
            return False, None

        z_score = abs(value - mean) / std
        is_anomaly = z_score > self.sigma_threshold

        self.values.append(value)
        return is_anomaly, z_score

# Usage
detectors = {
    "latency": ZScoreAnomalyDetector(sigma_threshold=3.0),
    "cost": ZScoreAnomalyDetector(sigma_threshold=2.5),  # More sensitive
    "tokens": ZScoreAnomalyDetector(sigma_threshold=2.0),
}

def check_request_anomalies(metrics: dict) -> list[str]:
    alerts = []

    for metric_name, detector in detectors.items():
        if metric_name in metrics:
            is_anomaly, z_score = detector.is_anomaly(metrics[metric_name])
            if is_anomaly:
                alerts.append(
                    f"ANOMALY: {metric_name} = {metrics[metric_name]:.2f} "
                    f"(z-score: {z_score:.2f})"
                )

    return alerts
```

### Integration с Observability Platforms

```python
# Langfuse + Custom Alerting
from langfuse import Langfuse
import requests

langfuse = Langfuse()

def send_alert(title: str, message: str, severity: str):
    # Slack webhook
    requests.post(
        SLACK_WEBHOOK_URL,
        json={
            "text": f":warning: *{severity.upper()}: {title}*\n{message}"
        }
    )

def check_langfuse_metrics():
    # Query last hour metrics
    traces = langfuse.get_traces(
        limit=1000,
        from_timestamp=datetime.now() - timedelta(hours=1)
    )

    # Calculate metrics
    error_rate = sum(1 for t in traces if t.status == "ERROR") / len(traces)
    avg_latency = np.mean([t.latency_ms for t in traces])
    total_cost = sum(t.calculated_total_cost for t in traces)

    # Check alerts
    if error_rate > 0.05:
        send_alert(
            "High Error Rate",
            f"Error rate is {error_rate:.1%} (threshold: 5%)",
            "critical"
        )

    if total_cost > 100:
        send_alert(
            "Cost Spike",
            f"Hourly cost: ${total_cost:.2f} (threshold: $100)",
            "high"
        )
```

---

## 12. Cost Optimization Strategies

### Token Optimization

```python
# 1. Prompt Compression
# Use LLMLingua for 20x compression
from llmlingua import PromptCompressor

compressor = PromptCompressor()
compressed = compressor.compress_prompt(
    long_prompt,
    rate=0.5,  # Keep 50% of tokens
    force_tokens=["important", "keywords"]
)

# 2. Semantic Caching
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())

# 3. Smart Model Routing
def route_to_model(query: str, complexity: str) -> str:
    if complexity == "simple":
        return "gpt-4o-mini"  # $0.15/1M input
    elif complexity == "medium":
        return "gpt-4o"       # $2.50/1M input
    else:
        return "o1-preview"   # $15/1M input

# 4. Output Token Limits
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    max_tokens=500,  # Limit output tokens
)
```

### Cost Tracking per User/Feature

```python
from langfuse.decorators import observe

@observe()
def generate_response(user_id: str, feature: str, query: str):
    """Track cost attribution"""

    # Add metadata for cost attribution
    langfuse_context.update_current_observation(
        metadata={
            "user_id": user_id,
            "feature": feature,
            "team": get_user_team(user_id),
        }
    )

    response = llm_call(query)
    return response

# In Langfuse dashboard:
# - Cost breakdown by user_id
# - Cost breakdown by feature
# - Cost trends over time
```

### Cost Reduction Results

> "Most developers see a 30-50% reduction in LLM costs by implementing prompt optimization and caching alone."
> -- [Helicone Cost Guide](https://www.helicone.ai/blog/monitor-and-optimize-llm-costs)

---

## 13. Рекомендации по выбору платформы

```
+-------------------------------------------------------------------+
|                 Platform Selection Guide 2025                      |
+-------------------------------------------------------------------+
|                                                                    |
|  "Нужен open-source, self-hosted для production"                  |
|  --> Langfuse (MIT license, battle-tested, free self-host)        |
|                                                                    |
|  "Используем LangChain и хотим deep интеграцию"                   |
|  --> LangSmith (native support, best agent tracing)               |
|                                                                    |
|  "Фокус на RAG evaluation и embeddings analysis"                  |
|  --> Arize Phoenix (best RAG evals, visualization)                |
|                                                                    |
|  "Нужна минимальная интеграция, быстрый старт"                   |
|  --> Helicone (one line, proxy-based)                             |
|                                                                    |
|  "Уже есть W&B для ML experiments"                                |
|  --> W&B Weave (unified platform)                                 |
|                                                                    |
|  "Уже есть Datadog/Grafana, хотим добавить LLM"                  |
|  --> OpenTelemetry (OpenLLMetry/OpenLIT) + existing backend       |
|                                                                    |
|  "Enterprise с requirements data residency"                       |
|  --> Langfuse self-hosted или LangSmith Enterprise                |
|                                                                    |
|  "Маленькая команда, быстрый старт, ограниченный бюджет"         |
|  --> Langfuse Cloud (free tier) или Helicone                      |
|                                                                    |
+-------------------------------------------------------------------+
```

---

## Best Practices Checklist

### Development Phase

- [ ] Instrument LLM calls from day one
- [ ] Define quality thresholds (accuracy, latency, cost)
- [ ] Set up local tracing (Phoenix in Jupyter)
- [ ] Create evaluation datasets early

### Pre-Production

- [ ] Configure cost alerts and budgets
- [ ] Set up anomaly detection
- [ ] Implement input/output guardrails
- [ ] Test prompt injection defenses
- [ ] Run A/B tests on prompts

### Production

- [ ] Monitor P50/P95/P99 latency
- [ ] Track hallucination rate
- [ ] Collect user feedback
- [ ] Set up on-call alerts
- [ ] Weekly metrics review

### Continuous Improvement

- [ ] Monthly cost analysis
- [ ] Quarterly prompt optimization
- [ ] Regular security audits
- [ ] Feedback loop to development

---

## Проверь себя

1. **Q: Почему LLM observability сложнее традиционного мониторинга?**
   A: LLM стохастичны - один промпт дает разные ответы. Нельзя предсказать результат, hallucinations непредсказуемы, costs переменны. Нужны специальные метрики: hallucination rate, faithfulness, relevance. Традиционные метрики (latency, errors) недостаточны.

2. **Q: Что такое Faithfulness и почему она важна?**
   A: Faithfulness измеряет, основан ли ответ LLM на предоставленном контексте. Score 1.0 = полностью faithful, 0.0 = hallucinated. Критично для RAG систем, где нужно убедиться, что LLM не выдумывает факты.

3. **Q: Langfuse vs LangSmith - когда что выбирать?**
   A: **Langfuse**: open-source MIT, self-hosted бесплатно, framework-agnostic. **LangSmith**: лучшая интеграция с LangChain/LangGraph, managed service. Для LangChain users - LangSmith, для всех остальных и self-hosted - Langfuse.

4. **Q: Что такое OpenLLMetry?**
   A: OpenLLMetry - расширение OpenTelemetry для LLM. Vendor-neutral стандарт трейсинга. Позволяет менять backends (Langfuse, Phoenix, Datadog) без изменения кода. Инструментирует OpenAI, Anthropic, vector DBs.

5. **Q: Как защититься от prompt injection?**
   A: Multi-layer defense: input validation + sanitization, классификаторы injection detection, output filtering, rate limiting, human-in-the-loop для критичных операций. 100% защиты не существует, но можно значительно снизить риски.

6. **Q: Какие метрики RAG нужно мониторить?**
   A: RAGAS metrics: Faithfulness (answer grounded?), Answer Relevancy (addresses question?), Context Precision (relevant docs retrieved?), Context Recall (all relevant docs found?). Плюс latency retrieval vs generation.

---

## Источники

### Официальная документация
- [Langfuse Documentation](https://langfuse.com/docs)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Arize Phoenix](https://docs.arize.com/phoenix)
- [Helicone Documentation](https://docs.helicone.ai)
- [W&B Weave](https://docs.wandb.ai/weave)

### Сравнения и обзоры
- [Braintrust: Top 10 LLM Observability Tools 2025](https://www.braintrust.dev/articles/top-10-llm-observability-tools-2025)
- [ZenML: Langfuse vs LangSmith](https://www.zenml.io/blog/langfuse-vs-langsmith)
- [Helicone: Complete Guide to LLM Observability Platforms](https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms)
- [PostHog: Best Open Source LLM Observability Tools](https://posthog.com/blog/best-open-source-llm-observability-tools)

### Best Practices
- [Splunk: LLM Monitoring Guide](https://www.splunk.com/en_us/blog/learn/llm-monitoring.html)
- [Datadog: LLM Evaluation Framework Best Practices](https://www.datadoghq.com/blog/llm-evaluation-framework-best-practices/)
- [Datadog: LLM Guardrails Best Practices](https://www.datadoghq.com/blog/llm-guardrails-best-practices/)

### Evaluation & Metrics
- [RAGAS Documentation](https://docs.ragas.io/)
- [Vectara: Evaluating RAG with RAGAS](https://www.vectara.com/blog/evaluating-rag)
- [Confident AI: LLM Evaluation Metrics](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)

### Security
- [OWASP: LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [OWASP: Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [Guardrails-AI GitHub](https://github.com/guardrails-ai/guardrails)

### OpenTelemetry
- [OpenTelemetry: LLM Observability](https://opentelemetry.io/blog/2024/llm-observability/)
- [OpenLLMetry GitHub](https://github.com/traceloop/openllmetry)
- [OpenLIT](https://openlit.io)

### Cost Optimization
- [Helicone: Monitor and Optimize LLM Costs](https://www.helicone.ai/blog/monitor-and-optimize-llm-costs)
- [Traceloop: Track LLM Token Usage and Cost Per User](https://www.traceloop.com/blog/from-bills-to-budgets-how-to-track-llm-token-usage-and-cost-per-user)

---

## Связанные заметки

- [[llm-fundamentals]] - Основы LLM
- [[ai-agents-advanced]] - AI Агенты
- [[rag-advanced-techniques]] - RAG Techniques
- [[ai-cost-optimization]] - Оптимизация затрат
- [[ai-devops-deployment]] - DevOps для AI
- [[ai-security-guardrails]] - AI Security

---

*Проверено: 2026-01-09*
