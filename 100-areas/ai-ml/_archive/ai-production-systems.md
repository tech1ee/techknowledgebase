---
title: "AI Production Systems: serving, scaling, cost optimization"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - ai
  - production
  - mlops
  - serving
  - optimization
related:
  - "[[ai-ml-overview]]"
  - "[[ai-evaluation-metrics]]"
  - "[[cloud-serverless-patterns]]"
---

# AI Production Systems: serving, scaling, cost optimization

> Production AI — это не только модель. Это система: serving, caching, monitoring, cost control.

---

## TL;DR

- **LLM Serving:** API providers vs self-hosted, latency vs cost tradeoffs
- **Cost optimization:** Caching, model routing, prompt compression
- **Scaling:** Rate limiting, queuing, horizontal scaling
- **Monitoring:** Latency, cost, quality metrics, drift detection

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Inference** | Процесс генерации ответа моделью |
| **Serving** | Инфраструктура для обслуживания inference requests |
| **TTFT** | Time to First Token — время до первого токена |
| **TPS** | Tokens per Second — скорость генерации |
| **Throughput** | Количество запросов в секунду |
| **Batching** | Группировка запросов для эффективности |
| **Quantization** | Снижение precision для скорости/памяти |
| **KV Cache** | Кэш ключей/значений для attention |

---

## Архитектура Production AI System

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   PRODUCTION AI SYSTEM ARCHITECTURE                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         CLIENTS                                       │  │
│  │        Web App        Mobile App        Internal Services             │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      API GATEWAY                                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │   Auth   │  │  Rate    │  │  Request │  │  Response│             │  │
│  │  │          │  │  Limit   │  │  Valid.  │  │  Cache   │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   AI ORCHESTRATION LAYER                              │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    MODEL ROUTER                                  │ │  │
│  │  │                                                                  │ │  │
│  │  │    Simple queries ──▶ GPT-4o-mini (cheap, fast)                 │ │  │
│  │  │    Complex queries ──▶ Claude Opus (expensive, smart)           │ │  │
│  │  │    Coding tasks ──▶ Specialized model                           │ │  │
│  │  │                                                                  │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │                               │                                       │  │
│  │  ┌────────────┐  ┌────────────┼────────────┐  ┌────────────┐        │  │
│  │  │  Semantic  │  │            ▼            │  │   Prompt   │        │  │
│  │  │   Cache    │◀─┤    RAG Pipeline         │──▶│  Manager   │        │  │
│  │  │            │  │                         │  │            │        │  │
│  │  └────────────┘  └─────────────────────────┘  └────────────┘        │  │
│  │                                                                        │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                             │
│         ┌─────────────────────┼─────────────────────┐                      │
│         ▼                     ▼                     ▼                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐               │
│  │   OpenAI     │     │  Anthropic   │     │  Self-hosted │               │
│  │    API       │     │    API       │     │    (vLLM)    │               │
│  │              │     │              │     │              │               │
│  │  GPT-4o      │     │  Claude 3    │     │  Llama 3     │               │
│  │  GPT-4o-mini │     │  Opus/Sonnet │     │  Mistral     │               │
│  └──────────────┘     └──────────────┘     └──────────────┘               │
│                               │                                             │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      OBSERVABILITY                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │ Logging  │  │ Metrics  │  │  Traces  │  │  Eval    │             │  │
│  │  │(LangSmith│  │(DataDog) │  │ (Jaeger) │  │ (RAGAS)  │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Cost Optimization

### Model Routing

```python
# ✅ Smart model routing based on query complexity
class ModelRouter:
    def __init__(self):
        self.models = {
            "fast": "gpt-4o-mini",      # $0.15/1M input
            "balanced": "gpt-4o",        # $2.50/1M input
            "powerful": "claude-opus"    # $15/1M input
        }
        self.classifier = self._load_classifier()

    def route(self, query: str, context: dict) -> str:
        """Route query to appropriate model."""

        # Simple heuristics first
        if len(query) < 50 and not context.get("requires_reasoning"):
            return self.models["fast"]

        # Use classifier for complex routing
        complexity = self.classifier.predict(query)

        if complexity == "simple":
            return self.models["fast"]
        elif complexity == "medium":
            return self.models["balanced"]
        else:
            return self.models["powerful"]

    def _load_classifier(self):
        """Load query complexity classifier."""
        # Fine-tuned classifier or rule-based
        return ComplexityClassifier()

# Usage
router = ModelRouter()
model = router.route(user_query, {"requires_reasoning": False})
response = call_llm(model, user_query)
```

### Semantic Caching

```python
from typing import Optional
import numpy as np

class SemanticCache:
    """Cache responses based on semantic similarity."""

    def __init__(self, embedding_model, threshold: float = 0.95):
        self.embedding_model = embedding_model
        self.threshold = threshold
        self.cache = {}  # {embedding_hash: (query, response, embedding)}
        self.index = None  # FAISS or similar for fast search

    def get(self, query: str) -> Optional[str]:
        """Get cached response if similar query exists."""
        query_embedding = self.embedding_model.encode(query)

        # Search for similar queries
        if self.index is not None:
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1), k=1
            )

            if distances[0][0] < (1 - self.threshold):
                cached_key = list(self.cache.keys())[indices[0][0]]
                return self.cache[cached_key]["response"]

        return None

    def set(self, query: str, response: str):
        """Cache query-response pair."""
        query_embedding = self.embedding_model.encode(query)
        cache_key = hash(query)

        self.cache[cache_key] = {
            "query": query,
            "response": response,
            "embedding": query_embedding,
            "timestamp": time.time()
        }

        # Update index
        self._rebuild_index()

    def _rebuild_index(self):
        """Rebuild FAISS index with all embeddings."""
        import faiss

        embeddings = np.array([
            v["embedding"] for v in self.cache.values()
        ]).astype('float32')

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

# ✅ Usage with fallback
cache = SemanticCache(embedding_model, threshold=0.92)

def get_response(query: str) -> str:
    # Try cache first
    cached = cache.get(query)
    if cached:
        log_metric("cache_hit", 1)
        return cached

    # Generate new response
    log_metric("cache_miss", 1)
    response = llm.generate(query)

    # Cache for future
    cache.set(query, response)
    return response
```

### Cost Comparison

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    COST COMPARISON (per 1M tokens)                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODEL                    INPUT        OUTPUT       USE CASE               │
│  ────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  GPT-4o-mini             $0.15        $0.60        Simple tasks            │
│  ████░░░░░░░░░░░░░░░░                              Classification          │
│                                                    Extraction              │
│                                                                             │
│  GPT-4o                  $2.50        $10.00       Complex reasoning       │
│  ████████████░░░░░░░░                              Multi-step tasks        │
│                                                    Code generation         │
│                                                                             │
│  Claude 3.5 Sonnet       $3.00        $15.00       Long context            │
│  ██████████████░░░░░░                              Analysis                │
│                                                    Writing                 │
│                                                                             │
│  Claude 3 Opus           $15.00       $75.00       Most complex            │
│  ████████████████████                              Critical decisions      │
│                                                    Expert analysis         │
│                                                                             │
│  Self-hosted Llama 3     ~$0.50*      ~$0.50*      High volume             │
│  ███░░░░░░░░░░░░░░░░░                              Privacy needs           │
│  (*infrastructure cost)                            Custom models           │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Serving Options

### API Providers vs Self-Hosted

| Aspect | API Providers | Self-Hosted |
|--------|--------------|-------------|
| **Setup time** | Minutes | Days-Weeks |
| **Cost (low volume)** | Lower | Higher (infra) |
| **Cost (high volume)** | Higher | Lower |
| **Latency** | Variable | Controlled |
| **Privacy** | Data leaves network | Full control |
| **Customization** | Limited | Full |
| **Scaling** | Automatic | Manual |
| **Maintenance** | Zero | Significant |

### Self-Hosted with vLLM

```python
# ✅ vLLM deployment for high throughput
from vllm import LLM, SamplingParams

# Initialize model with optimizations
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2,  # Use 2 GPUs
    gpu_memory_utilization=0.9,
    max_model_len=8192,
    quantization="awq"  # 4-bit quantization
)

# Sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512
)

# Single request
outputs = llm.generate(["What is Python?"], sampling_params)

# Batch processing (more efficient)
prompts = ["Question 1", "Question 2", "Question 3"]
outputs = llm.generate(prompts, sampling_params)  # Batched automatically

# Streaming (via vLLM server)
# Start server: python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.1-8B-Instruct
```

### Deployment Configuration

```yaml
# Kubernetes deployment for vLLM
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-server
  template:
    metadata:
      labels:
        app: llm-server
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
        - --model=meta-llama/Llama-3.1-8B-Instruct
        - --tensor-parallel-size=1
        - --gpu-memory-utilization=0.9
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "32Gi"
            cpu: "8"
        ports:
        - containerPort: 8000
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: llm-service
spec:
  selector:
    app: llm-server
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Rate Limiting & Queuing

```python
# ✅ Token bucket rate limiter
import asyncio
from collections import defaultdict
import time

class TokenBucketRateLimiter:
    def __init__(
        self,
        tokens_per_minute: int,
        requests_per_minute: int
    ):
        self.tokens_per_minute = tokens_per_minute
        self.requests_per_minute = requests_per_minute
        self.buckets = defaultdict(lambda: {
            "tokens": tokens_per_minute,
            "requests": requests_per_minute,
            "last_update": time.time()
        })

    def _refill(self, user_id: str):
        """Refill bucket based on elapsed time."""
        bucket = self.buckets[user_id]
        now = time.time()
        elapsed = now - bucket["last_update"]
        minutes = elapsed / 60

        bucket["tokens"] = min(
            self.tokens_per_minute,
            bucket["tokens"] + int(minutes * self.tokens_per_minute)
        )
        bucket["requests"] = min(
            self.requests_per_minute,
            bucket["requests"] + int(minutes * self.requests_per_minute)
        )
        bucket["last_update"] = now

    async def acquire(
        self,
        user_id: str,
        estimated_tokens: int
    ) -> bool:
        """Try to acquire tokens for request."""
        self._refill(user_id)
        bucket = self.buckets[user_id]

        if bucket["tokens"] >= estimated_tokens and bucket["requests"] >= 1:
            bucket["tokens"] -= estimated_tokens
            bucket["requests"] -= 1
            return True
        return False

    def get_retry_after(self, user_id: str) -> float:
        """Get seconds until tokens available."""
        bucket = self.buckets[user_id]
        if bucket["tokens"] <= 0:
            return 60 - (time.time() - bucket["last_update"])
        return 0

# ✅ Request queue for overflow
class RequestQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.processing = False

    async def enqueue(self, request: dict) -> str:
        """Add request to queue, return ticket."""
        ticket = str(uuid.uuid4())
        await self.queue.put({"ticket": ticket, "request": request})
        return ticket

    async def process_queue(self, handler):
        """Process queued requests."""
        while True:
            item = await self.queue.get()
            try:
                result = await handler(item["request"])
                await self.notify_completion(item["ticket"], result)
            except Exception as e:
                await self.notify_error(item["ticket"], e)
            finally:
                self.queue.task_done()
```

---

## Monitoring & Observability

```python
# ✅ Comprehensive monitoring setup
import time
from prometheus_client import Counter, Histogram, Gauge

# Metrics
REQUEST_COUNT = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

LATENCY_HISTOGRAM = Histogram(
    'llm_request_duration_seconds',
    'Request latency',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

TOKEN_USAGE = Counter(
    'llm_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: input/output
)

COST_COUNTER = Counter(
    'llm_cost_dollars',
    'Total cost in dollars',
    ['model']
)

QUALITY_GAUGE = Gauge(
    'llm_quality_score',
    'Rolling quality score',
    ['metric']  # faithfulness, relevance, etc.
)

class LLMMonitor:
    def __init__(self):
        self.cost_rates = {
            "gpt-4o": {"input": 2.5 / 1_000_000, "output": 10.0 / 1_000_000},
            "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.6 / 1_000_000},
            "claude-sonnet": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000}
        }

    async def track_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_seconds: float,
        success: bool
    ):
        """Track all metrics for a request."""

        # Request count
        REQUEST_COUNT.labels(
            model=model,
            status="success" if success else "error"
        ).inc()

        # Latency
        LATENCY_HISTOGRAM.labels(model=model).observe(latency_seconds)

        # Tokens
        TOKEN_USAGE.labels(model=model, type="input").inc(input_tokens)
        TOKEN_USAGE.labels(model=model, type="output").inc(output_tokens)

        # Cost
        if model in self.cost_rates:
            rates = self.cost_rates[model]
            cost = (input_tokens * rates["input"] +
                    output_tokens * rates["output"])
            COST_COUNTER.labels(model=model).inc(cost)

    def update_quality_metrics(self, metrics: dict):
        """Update quality gauges from evaluation."""
        for name, value in metrics.items():
            QUALITY_GAUGE.labels(metric=name).set(value)

# ✅ Structured logging
import structlog

logger = structlog.get_logger()

async def log_request(
    request_id: str,
    model: str,
    prompt: str,
    response: str,
    metadata: dict
):
    """Log request with structured data."""
    logger.info(
        "llm_request",
        request_id=request_id,
        model=model,
        prompt_length=len(prompt),
        response_length=len(response),
        input_tokens=metadata.get("input_tokens"),
        output_tokens=metadata.get("output_tokens"),
        latency_ms=metadata.get("latency_ms"),
        cache_hit=metadata.get("cache_hit", False)
    )
```

---

## A/B Testing

```python
# ✅ A/B testing framework for LLM systems
class LLMABTest:
    def __init__(self, experiment_name: str, variants: dict):
        """
        variants = {
            "control": {"model": "gpt-4o-mini", "prompt": prompt_v1},
            "treatment_a": {"model": "gpt-4o", "prompt": prompt_v1},
            "treatment_b": {"model": "gpt-4o-mini", "prompt": prompt_v2}
        }
        """
        self.experiment_name = experiment_name
        self.variants = variants
        self.assignment_cache = {}

    def assign_variant(self, user_id: str) -> str:
        """Consistent assignment based on user_id."""
        if user_id in self.assignment_cache:
            return self.assignment_cache[user_id]

        # Hash-based assignment for consistency
        hash_value = hash(f"{self.experiment_name}:{user_id}") % 100

        if hash_value < 50:
            variant = "control"
        elif hash_value < 75:
            variant = "treatment_a"
        else:
            variant = "treatment_b"

        self.assignment_cache[user_id] = variant
        return variant

    async def run_with_variant(
        self,
        user_id: str,
        query: str
    ) -> tuple[str, str]:
        """Run query with assigned variant."""
        variant = self.assign_variant(user_id)
        config = self.variants[variant]

        response = await call_llm(
            model=config["model"],
            prompt=config["prompt"].format(query=query)
        )

        # Log for analysis
        await self.log_experiment_event(
            user_id=user_id,
            variant=variant,
            query=query,
            response=response
        )

        return variant, response

    async def analyze_results(self) -> dict:
        """Analyze experiment results."""
        results = await self.get_all_events()

        analysis = {}
        for variant in self.variants:
            variant_results = [r for r in results if r["variant"] == variant]
            analysis[variant] = {
                "count": len(variant_results),
                "avg_latency": np.mean([r["latency"] for r in variant_results]),
                "avg_quality": np.mean([r["quality_score"] for r in variant_results]),
                "avg_cost": np.mean([r["cost"] for r in variant_results])
            }

        return analysis
```

---

## Проверь себя

<details>
<summary>1. Когда выгоднее self-hosted vs API providers?</summary>

**Ответ:**

**API providers лучше когда:**
- Низкий/средний объём (<100K запросов/день)
- Нужен быстрый старт
- Нет DevOps экспертизы
- Разные модели для разных задач

**Self-hosted лучше когда:**
- Высокий объём (>1M запросов/день)
- Строгие privacy requirements
- Нужна кастомизация (fine-tuned models)
- Предсказуемые latency requirements
- Долгосрочный проект

**Break-even примерно:** 500K-1M запросов/месяц

</details>

<details>
<summary>2. Как работает semantic caching?</summary>

**Ответ:**

**Принцип:**
1. Новый запрос → вычисляем embedding
2. Ищем похожие запросы в кэше (cosine similarity)
3. Если similarity > threshold → возвращаем кэшированный ответ
4. Иначе → вызываем LLM, кэшируем результат

**Преимущества над exact match:**
- "What is Python?" ≈ "Tell me about Python"
- "Capital of France?" ≈ "What's France's capital?"

**Параметры:**
- Threshold: 0.90-0.95 (высокий = меньше false positives)
- TTL: зависит от свежести данных
- Index: FAISS для быстрого поиска

**Cache hit rate:** 10-30% типично для Q&A систем

</details>

<details>
<summary>3. Какие метрики критичны для production AI?</summary>

**Ответ:**

**Latency:**
- TTFT (Time to First Token): < 500ms
- Total response time: < 5s для chat
- P95, P99 важнее чем average

**Cost:**
- Cost per query
- Cost per user/day
- Token efficiency (output/input ratio)

**Quality:**
- Faithfulness (no hallucinations)
- Relevance (answers question)
- User satisfaction (thumbs up/down)

**System:**
- Error rate < 1%
- Throughput (queries/sec)
- Cache hit rate

**Alerting на:**
- Latency P95 > threshold
- Error rate spike
- Quality score drop
- Cost anomalies

</details>

<details>
<summary>4. Как организовать A/B тестирование LLM?</summary>

**Ответ:**

**Что тестировать:**
- Разные модели (GPT-4o vs Claude)
- Разные промпты
- Разные RAG стратегии
- Temperature/parameters

**Как:**
1. **Consistent assignment** — один user всегда в одном варианте
2. **Достаточный размер** — минимум 1000 запросов на вариант
3. **Статистическая значимость** — p-value < 0.05

**Метрики для сравнения:**
- Quality (LLM-as-judge или human)
- Latency
- Cost
- User engagement (if available)

**Важно:**
- Не менять assignment mid-experiment
- Логировать все для post-hoc анализа
- Иметь kill switch для плохих вариантов

</details>

---

## Связи

- [[ai-ml-overview]] — обзор AI Engineering
- [[ai-evaluation-metrics]] — метрики качества
- [[cloud-serverless-patterns]] — serverless для AI
- [[architecture-rate-limiting]] — rate limiting patterns
- [[observability]] — мониторинг и логирование

---

## Источники

- [vLLM Documentation](https://docs.vllm.ai/) — high-throughput serving
- [LangSmith](https://docs.smith.langchain.com/) — LLM observability
- [OpenAI Cookbook](https://cookbook.openai.com/) — best practices
- [Anyscale Blog](https://www.anyscale.com/blog) — LLM serving insights
- [Modal](https://modal.com/) — serverless GPU inference

---

*Проверено: 2025-12-22*

---

*Проверено: 2026-01-09*
