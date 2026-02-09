---
title: "AI Agent Cost Optimization"
tags:
  - topic/ai-ml
  - agents
  - cost
  - optimization
  - tokens
  - caching
  - routing
  - production
  - type/concept
  - level/advanced
category: ai-ml
level: intermediate-advanced
created: 2026-01-11
updated: 2026-01-11
sources:
  - openai.com
  - anthropic.com
  - langchain.com
  - together.ai
status: published
---

# AI Agent Cost Optimization: Полное руководство

---

## TL;DR

> AI-агенты могут быть невероятно дорогими: многошаговое выполнение, большие контексты, использование дорогих моделей. Один сложный агент может стоить $1-10 за задачу. Но при правильной оптимизации те же задачи решаются за $0.01-0.10. Этот гайд покрывает все уровни оптимизации: от выбора модели до архитектурных паттернов, снижающих costs в 10-100 раз.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание AI Agents** | Архитектура агентов | [[ai-agents-advanced]] |
| **LLM API и pricing** | Понимание токенов и стоимости | [[ai-api-integration]] |
| **Production агенты** | Практика работы | [[tutorial-ai-agent]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ После базы | Сначала [[ai-agents-advanced]] |
| **AI Engineer** | ✅ Да | Основная аудитория |
| **Tech Lead** | ✅ Да | Budget planning |
| **FinOps** | ✅ Да | Cost management |

### Терминология

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Token** | Единица текста (~0.75 слова) | **Буква в SMS** — платишь за каждую |
| **Input Tokens** | Токены в запросе | **Входящий звонок** — платишь за время слушания |
| **Output Tokens** | Токены в ответе | **Исходящий звонок** — платишь за время говорения |
| **Context Window** | Максимум токенов | **Память телефона** — сколько влезет |
| **Model Routing** | Выбор модели под задачу | **Такси vs автобус** — дорого быстро или дёшево долго |
| **Prompt Caching** | Кэширование промптов | **Шаблон письма** — не писать каждый раз заново |
| **Batch Processing** | Пакетная обработка | **Оптовая закупка** — скидка за объём |

---

## Анатомия стоимости агента

### Формула стоимости

```
Total Cost = Σ (Steps) × [
    (Input Tokens × Input Price) +
    (Output Tokens × Output Price) +
    (Tool Costs) +
    (Infrastructure Costs)
]
```

### Breakdown типичного агента

```
┌────────────────────────────────────────────────────────────┐
│                    COST BREAKDOWN                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  TASK: "Research company X and write a summary"            │
│                                                             │
│  Step 1: Planning                                           │
│    ├─ System prompt: 500 tokens × $0.01/1K = $0.005        │
│    ├─ User input: 50 tokens                                 │
│    └─ Output: 200 tokens × $0.03/1K = $0.006               │
│                                                             │
│  Step 2: Web Search (tool)                                  │
│    ├─ Context (accumulated): 750 tokens                    │
│    ├─ Output: 100 tokens                                    │
│    └─ Search API call: $0.01                               │
│                                                             │
│  Step 3: Process Results                                    │
│    ├─ Context: 850 tokens + 2000 tokens (search results)   │
│    └─ Output: 150 tokens                                    │
│                                                             │
│  Step 4: Additional Search                                  │
│    ├─ Context: 3000 tokens                                 │
│    └─ Output: 100 tokens                                    │
│                                                             │
│  Step 5: Write Summary                                      │
│    ├─ Context: 5000 tokens                                 │
│    └─ Output: 500 tokens                                    │
│                                                             │
│  TOTAL: ~8000 input tokens + 1050 output tokens            │
│         + 2 API calls + infrastructure                      │
│                                                             │
│  With GPT-4: ~$0.30                                         │
│  With Claude 3 Opus: ~$0.45                                │
│  With GPT-3.5: ~$0.02                                      │
│  With local Llama: ~$0.001                                 │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Где теряются деньги

| Проблема | Impact | Как обнаружить |
|----------|--------|----------------|
| **Избыточные шаги** | 2-5x | Trajectory analysis |
| **Большой system prompt** | 20-50% | Token counting |
| **Накопление контекста** | 2-10x | Context window monitoring |
| **Неоптимальная модель** | 5-50x | Cost/quality analysis |
| **Loops и retries** | 2-10x | Loop detection |
| **Отсутствие кэширования** | 2-5x | Cache hit rate |

---

## Уровень 1: Выбор правильной модели

### Матрица Model Selection

```
TASK COMPLEXITY vs MODEL COST

                    Low Complexity    Medium           High Complexity
                    ──────────────    ──────           ───────────────
High Cost           ❌ WASTE          ⚠️ Consider      ✅ OK
(GPT-4, Claude 3)

Medium Cost         ⚠️ Consider       ✅ SWEET SPOT    ⚠️ May struggle
(GPT-4o, Sonnet)

Low Cost            ✅ PERFECT        ⚠️ May struggle  ❌ FAIL
(GPT-4o-mini, Haiku)
```

### Model Routing Pattern

```python
from enum import Enum
from pydantic import BaseModel

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class ModelConfig(BaseModel):
    name: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    max_tokens: int
    capabilities: list[str]

MODELS = {
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        input_cost_per_1k=0.0025,
        output_cost_per_1k=0.01,
        max_tokens=128000,
        capabilities=["reasoning", "code", "multimodal", "tools"]
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
        max_tokens=128000,
        capabilities=["basic_reasoning", "code", "tools"]
    ),
    "claude-3-5-sonnet": ModelConfig(
        name="claude-3-5-sonnet-20241022",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=200000,
        capabilities=["reasoning", "code", "multimodal", "tools", "long_context"]
    ),
    "claude-3-5-haiku": ModelConfig(
        name="claude-3-5-haiku-20241022",
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.005,
        max_tokens=200000,
        capabilities=["basic_reasoning", "code", "tools"]
    ),
}

class ModelRouter:
    """Выбирает оптимальную модель под задачу"""

    def __init__(self, classifier_model: str = "gpt-4o-mini"):
        self.classifier = classifier_model

    async def route(self, task: str, context: dict = None) -> str:
        """Определяем сложность и выбираем модель"""

        complexity = await self._classify_complexity(task)
        required_capabilities = self._detect_required_capabilities(task, context)

        return self._select_model(complexity, required_capabilities)

    async def _classify_complexity(self, task: str) -> TaskComplexity:
        """Классифицируем сложность задачи"""

        prompt = f"""
        Classify the complexity of this task:
        "{task}"

        Respond with one word: simple, medium, or complex

        Guidelines:
        - simple: single-step, factual, formatting, basic extraction
        - medium: multi-step reasoning, some ambiguity, standard code
        - complex: deep analysis, creative, complex code, edge cases
        """

        response = await llm.complete(
            model=self.classifier,
            prompt=prompt
        )

        return TaskComplexity(response.strip().lower())

    def _detect_required_capabilities(
        self,
        task: str,
        context: dict | None
    ) -> list[str]:
        """Определяем необходимые capabilities"""
        capabilities = []

        if "image" in task.lower() or context and context.get("has_images"):
            capabilities.append("multimodal")

        if "code" in task.lower() or "function" in task.lower():
            capabilities.append("code")

        if context and context.get("context_length", 0) > 100000:
            capabilities.append("long_context")

        return capabilities

    def _select_model(
        self,
        complexity: TaskComplexity,
        required_capabilities: list[str]
    ) -> str:
        """Выбираем самую дешёвую подходящую модель"""

        # Фильтруем по capabilities
        suitable = [
            (name, config) for name, config in MODELS.items()
            if all(cap in config.capabilities for cap in required_capabilities)
        ]

        # Сортируем по стоимости
        suitable.sort(key=lambda x: x[1].input_cost_per_1k)

        # Выбираем по сложности
        if complexity == TaskComplexity.SIMPLE:
            return suitable[0][0]  # Самая дешёвая
        elif complexity == TaskComplexity.MEDIUM:
            return suitable[len(suitable) // 2][0]  # Средняя
        else:
            return suitable[-1][0]  # Самая мощная
```

### Cascade Pattern (Escalation)

```python
class CascadeRouter:
    """Начинаем с дешёвой модели, эскалируем если нужно"""

    def __init__(self):
        self.models = ["gpt-4o-mini", "gpt-4o", "claude-3-5-sonnet"]
        self.max_retries = 2

    async def run_with_cascade(
        self,
        task: str,
        quality_threshold: float = 0.7
    ) -> tuple[str, str, float]:
        """
        Returns: (response, model_used, quality_score)
        """

        for model in self.models:
            response = await llm.complete(model=model, prompt=task)

            # Оцениваем качество (быстрая проверка)
            quality = await self._quick_quality_check(task, response)

            if quality >= quality_threshold:
                return response, model, quality

            # Если качество низкое, пробуем следующую модель
            continue

        # Если все модели не справились, возвращаем последний результат
        return response, self.models[-1], quality

    async def _quick_quality_check(
        self,
        task: str,
        response: str
    ) -> float:
        """Быстрая проверка качества через дешёвую модель"""

        check_prompt = f"""
        Task: {task}
        Response: {response}

        Is this response adequate? Score 0-1.
        Respond with just a number.
        """

        score = await llm.complete(
            model="gpt-4o-mini",
            prompt=check_prompt
        )

        return float(score.strip())
```

---

## Уровень 2: Оптимизация промптов

### Сжатие System Prompt

```python
class PromptOptimizer:
    """Оптимизация промптов для снижения токенов"""

    def __init__(self, target_reduction: float = 0.3):
        self.target_reduction = target_reduction

    async def compress_system_prompt(
        self,
        original: str,
        preserve_critical: list[str] = None
    ) -> str:
        """Сжимаем system prompt сохраняя смысл"""

        original_tokens = count_tokens(original)

        compress_prompt = f"""
        Compress this system prompt to use fewer tokens while
        preserving ALL critical instructions.

        Critical elements to preserve:
        {preserve_critical or ['all instructions']}

        Original prompt:
        {original}

        Rules:
        1. Remove redundancy and filler words
        2. Use abbreviations where clear
        3. Combine similar instructions
        4. Keep technical terms intact
        5. Target: reduce by {self.target_reduction * 100}%

        Compressed version:
        """

        compressed = await llm.complete(
            model="gpt-4o",
            prompt=compress_prompt
        )

        new_tokens = count_tokens(compressed)
        reduction = (original_tokens - new_tokens) / original_tokens

        return compressed, {
            "original_tokens": original_tokens,
            "compressed_tokens": new_tokens,
            "reduction": reduction
        }


# Пример оптимизации
ORIGINAL_PROMPT = """
You are a helpful and knowledgeable customer support assistant for
TechCorp Inc. Your primary goal is to assist customers with their
questions and issues in a friendly and professional manner.

When responding to customers, you should:
1. Always greet them warmly and thank them for contacting us
2. Listen carefully to understand their problem
3. Provide clear and concise solutions
4. If you don't know the answer, say so honestly
5. Always end with asking if there's anything else you can help with

You have access to the following tools:
- search_knowledge_base: search our internal documentation
- check_order_status: look up customer orders
- create_ticket: escalate to human support

Remember to be patient, empathetic, and solution-oriented.
Always maintain a positive and helpful tone.
"""

OPTIMIZED_PROMPT = """
TechCorp support agent. Be helpful, professional, concise.

Guidelines:
- Greet warmly
- Understand before solving
- Be honest if unsure
- End with "Anything else?"

Tools: search_knowledge_base, check_order_status, create_ticket
"""

# Original: ~150 tokens → Optimized: ~50 tokens (67% reduction!)
```

### Динамический контекст

```python
class DynamicContextManager:
    """Управление контекстом для минимизации токенов"""

    def __init__(self, max_context_tokens: int = 4000):
        self.max_tokens = max_context_tokens

    def build_context(
        self,
        system_prompt: str,
        messages: list[dict],
        tool_results: list[dict],
        priority: str = "recent"  # recent, relevant, balanced
    ) -> list[dict]:
        """Строим оптимальный контекст"""

        budget = self.max_tokens
        context = []

        # System prompt всегда включаем
        budget -= count_tokens(system_prompt)

        # Резервируем для ответа
        budget -= 500  # ~500 токенов на ответ

        if priority == "recent":
            context = self._recent_priority(messages, tool_results, budget)
        elif priority == "relevant":
            context = self._relevant_priority(messages, tool_results, budget)
        else:
            context = self._balanced_priority(messages, tool_results, budget)

        return context

    def _recent_priority(
        self,
        messages: list,
        tool_results: list,
        budget: int
    ) -> list:
        """Приоритет недавним сообщениям"""
        result = []
        used = 0

        # Идём с конца
        for msg in reversed(messages):
            tokens = count_tokens(str(msg))
            if used + tokens <= budget:
                result.insert(0, msg)
                used += tokens
            else:
                break

        return result

    def _relevant_priority(
        self,
        messages: list,
        tool_results: list,
        budget: int
    ) -> list:
        """Приоритет релевантным сообщениям"""
        # Используем embeddings для определения релевантности
        # к текущей задаче
        pass

    def summarize_old_context(self, messages: list) -> str:
        """Суммаризация старого контекста"""
        if len(messages) < 5:
            return ""

        old_messages = messages[:-3]  # Все кроме последних 3

        summary_prompt = f"""
        Summarize this conversation history in 2-3 sentences:
        {old_messages}

        Focus on: decisions made, information gathered, current state.
        """

        return llm.complete(model="gpt-4o-mini", prompt=summary_prompt)
```

---

## Уровень 3: Кэширование

### Prompt Caching (Anthropic / OpenAI)

```python
import anthropic
from anthropic import HUMAN_PROMPT, AI_PROMPT

class CachedAgent:
    """Агент с кэшированием промптов"""

    def __init__(self):
        self.client = anthropic.Anthropic()

        # Статический system prompt — кэшируется
        self.system_prompt = """
        You are an expert AI assistant...
        [длинный system prompt ~2000 tokens]
        """

        # Статические примеры — кэшируются
        self.few_shot_examples = """
        Example 1: ...
        Example 2: ...
        [примеры ~3000 tokens]
        """

    async def run(self, user_input: str) -> str:
        """Запрос с кэшированием"""

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Кэшируем!
                },
                {
                    "type": "text",
                    "text": self.few_shot_examples,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {"role": "user", "content": user_input}
            ]
        )

        # Проверяем cache hit
        if hasattr(response, 'usage'):
            print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
            print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")

        return response.content[0].text


# Экономия при кэшировании:
# Без кэша: 5000 input tokens × $0.003 = $0.015 за запрос
# С кэшем: 100 input tokens × $0.003 + 4900 cached × $0.0003 = $0.00177
# Экономия: 88% на input tokens!
```

### Semantic Caching

```python
import hashlib
from typing import Any
import numpy as np

class SemanticCache:
    """Кэш на основе семантического сходства"""

    def __init__(
        self,
        similarity_threshold: float = 0.95,
        max_cache_size: int = 10000
    ):
        self.threshold = similarity_threshold
        self.max_size = max_cache_size
        self.cache = {}  # embedding -> (response, metadata)
        self.embeddings = []

    async def get_or_compute(
        self,
        query: str,
        compute_fn,
        **kwargs
    ) -> tuple[str, bool]:
        """
        Returns: (response, cache_hit)
        """

        # Получаем embedding запроса
        query_embedding = await self._get_embedding(query)

        # Ищем похожий в кэше
        cached = self._find_similar(query_embedding)
        if cached:
            return cached["response"], True

        # Вычисляем и кэшируем
        response = await compute_fn(query, **kwargs)

        self._add_to_cache(
            embedding=query_embedding,
            query=query,
            response=response
        )

        return response, False

    def _find_similar(self, embedding: np.ndarray) -> dict | None:
        """Ищем семантически похожий запрос"""
        if not self.embeddings:
            return None

        similarities = [
            np.dot(embedding, cached_emb) /
            (np.linalg.norm(embedding) * np.linalg.norm(cached_emb))
            for cached_emb in self.embeddings
        ]

        max_sim = max(similarities)
        if max_sim >= self.threshold:
            idx = similarities.index(max_sim)
            return list(self.cache.values())[idx]

        return None

    async def _get_embedding(self, text: str) -> np.ndarray:
        """Получаем embedding"""
        response = await openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding)

    def _add_to_cache(
        self,
        embedding: np.ndarray,
        query: str,
        response: str
    ):
        """Добавляем в кэш"""
        if len(self.cache) >= self.max_size:
            # LRU eviction
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.embeddings.pop(0)

        key = hashlib.md5(query.encode()).hexdigest()
        self.cache[key] = {
            "query": query,
            "response": response,
            "created_at": time.time()
        }
        self.embeddings.append(embedding)

    def get_stats(self) -> dict:
        """Статистика кэша"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size
        }
```

### Tool Result Caching

```python
class ToolCache:
    """Кэширование результатов tools"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get_cache_key(self, tool_name: str, params: dict) -> str:
        """Создаём ключ кэша"""
        # Сортируем для консистентности
        sorted_params = json.dumps(params, sort_keys=True)
        return f"{tool_name}:{hashlib.md5(sorted_params.encode()).hexdigest()}"

    async def execute_with_cache(
        self,
        tool_name: str,
        params: dict,
        tool_fn
    ) -> tuple[Any, bool]:
        """
        Returns: (result, cache_hit)
        """
        key = self.get_cache_key(tool_name, params)

        # Проверяем кэш
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["created_at"] < self.ttl:
                return entry["result"], True

        # Выполняем tool
        result = await tool_fn(**params)

        # Кэшируем (для детерминированных tools)
        if self._is_cacheable(tool_name):
            self.cache[key] = {
                "result": result,
                "created_at": time.time()
            }

        return result, False

    def _is_cacheable(self, tool_name: str) -> bool:
        """Определяем можно ли кэшировать tool"""
        # Не кэшируем tools с side effects
        non_cacheable = [
            "send_email",
            "create_ticket",
            "update_database",
            "post_message"
        ]
        return tool_name not in non_cacheable
```

---

## Уровень 4: Архитектурные оптимизации

### Speculative Execution

```python
class SpeculativeAgent:
    """Спекулятивное выполнение параллельных путей"""

    async def run_speculative(
        self,
        task: str,
        possible_paths: list[str]
    ) -> str:
        """
        Запускаем несколько путей параллельно,
        используем первый успешный
        """

        # Создаём задачи для каждого пути
        tasks = [
            self._execute_path(task, path)
            for path in possible_paths[:3]  # Ограничиваем параллелизм
        ]

        # Ждём первый успешный результат
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Получаем результат
        for task in done:
            result = task.result()
            if result["success"]:
                # Отменяем остальные
                for p in pending:
                    p.cancel()
                return result["response"]

        # Если все пути провалились
        raise Exception("All speculative paths failed")


# Экономия: вместо sequential A → B → C (если A и B fail)
# получаем parallel A | B | C, платим за 1 успешный + overhead
```

### Tool Batching

```python
class BatchToolExecutor:
    """Пакетное выполнение однотипных tools"""

    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.pending_calls = {}

    async def queue_call(
        self,
        tool_name: str,
        params: dict
    ) -> asyncio.Future:
        """Добавляем вызов в очередь"""
        if tool_name not in self.pending_calls:
            self.pending_calls[tool_name] = []

        future = asyncio.Future()
        self.pending_calls[tool_name].append({
            "params": params,
            "future": future
        })

        # Если набрали batch, выполняем
        if len(self.pending_calls[tool_name]) >= self.batch_size:
            await self._execute_batch(tool_name)

        return future

    async def _execute_batch(self, tool_name: str):
        """Выполняем batch"""
        calls = self.pending_calls.pop(tool_name, [])

        if tool_name == "search":
            # Batch search: один API call вместо N
            queries = [c["params"]["query"] for c in calls]
            results = await self._batch_search(queries)

            for call, result in zip(calls, results):
                call["future"].set_result(result)

    async def _batch_search(self, queries: list[str]) -> list:
        """Пакетный поиск"""
        # Многие API поддерживают batch запросы
        return await search_api.batch_search(queries)


# Вместо 10 × $0.01 = $0.10
# Batch: 1 × $0.03 = $0.03 (70% экономия)
```

### Lazy Loading Context

```python
class LazyContextLoader:
    """Ленивая загрузка контекста"""

    def __init__(self):
        self.context_registry = {}

    def register_context(
        self,
        key: str,
        loader,
        tokens_estimate: int
    ):
        """Регистрируем контекст с lazy loader"""
        self.context_registry[key] = {
            "loader": loader,
            "tokens": tokens_estimate,
            "loaded": False,
            "content": None
        }

    async def get_context(self, keys: list[str]) -> str:
        """Загружаем только нужный контекст"""
        result = []

        for key in keys:
            if key not in self.context_registry:
                continue

            entry = self.context_registry[key]

            if not entry["loaded"]:
                entry["content"] = await entry["loader"]()
                entry["loaded"] = True

            result.append(entry["content"])

        return "\n".join(result)


# Использование
loader = LazyContextLoader()

# Регистрируем разные контексты
loader.register_context(
    "company_policies",
    lambda: fetch_policies(),
    tokens_estimate=2000
)
loader.register_context(
    "product_catalog",
    lambda: fetch_catalog(),
    tokens_estimate=5000
)
loader.register_context(
    "faq",
    lambda: fetch_faq(),
    tokens_estimate=1000
)

# Агент загружает только нужное
if task_type == "policy_question":
    context = await loader.get_context(["company_policies"])
elif task_type == "product_question":
    context = await loader.get_context(["product_catalog", "faq"])
```

---

## Уровень 5: Мониторинг и контроль

### Cost Tracking

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CostEntry:
    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    task_type: str
    user_id: Optional[str] = None

class CostTracker:
    """Отслеживание расходов"""

    def __init__(self):
        self.entries: list[CostEntry] = []
        self.budgets = {}  # user_id -> daily_budget

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str,
        user_id: str = None
    ):
        """Записываем расход"""
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        entry = CostEntry(
            timestamp=time.time(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            task_type=task_type,
            user_id=user_id
        )

        self.entries.append(entry)

        # Проверяем бюджет
        if user_id and user_id in self.budgets:
            daily_spend = self._get_daily_spend(user_id)
            if daily_spend >= self.budgets[user_id]:
                raise BudgetExceededError(f"Daily budget exceeded for {user_id}")

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Считаем стоимость"""
        config = MODELS.get(model)
        if not config:
            return 0

        return (
            input_tokens * config.input_cost_per_1k / 1000 +
            output_tokens * config.output_cost_per_1k / 1000
        )

    def get_report(
        self,
        start_time: float = None,
        end_time: float = None,
        group_by: str = "model"  # model, task_type, user_id
    ) -> dict:
        """Генерируем отчёт"""
        filtered = [
            e for e in self.entries
            if (not start_time or e.timestamp >= start_time) and
               (not end_time or e.timestamp <= end_time)
        ]

        # Группировка
        groups = {}
        for entry in filtered:
            key = getattr(entry, group_by)
            if key not in groups:
                groups[key] = {
                    "count": 0,
                    "total_cost": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0
                }
            groups[key]["count"] += 1
            groups[key]["total_cost"] += entry.cost
            groups[key]["total_input_tokens"] += entry.input_tokens
            groups[key]["total_output_tokens"] += entry.output_tokens

        return {
            "period": {
                "start": start_time,
                "end": end_time
            },
            "total_cost": sum(e.cost for e in filtered),
            "total_requests": len(filtered),
            "by_group": groups
        }

    def _get_daily_spend(self, user_id: str) -> float:
        """Считаем дневной расход"""
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0
        ).timestamp()

        return sum(
            e.cost for e in self.entries
            if e.user_id == user_id and e.timestamp >= today_start
        )
```

### Budget Controls

```python
class BudgetController:
    """Контроль бюджета с rate limiting"""

    def __init__(self):
        self.limits = {
            "per_request": 1.0,  # Макс $1 на запрос
            "per_user_daily": 10.0,  # Макс $10 в день на юзера
            "global_daily": 1000.0  # Макс $1000 в день всего
        }
        self.tracker = CostTracker()

    async def check_and_execute(
        self,
        user_id: str,
        estimated_cost: float,
        execute_fn
    ) -> Any:
        """Проверяем бюджет перед выполнением"""

        # Проверка per-request limit
        if estimated_cost > self.limits["per_request"]:
            raise CostLimitError(
                f"Estimated cost ${estimated_cost:.2f} exceeds "
                f"per-request limit ${self.limits['per_request']}"
            )

        # Проверка daily limit
        daily_spend = self.tracker._get_daily_spend(user_id)
        if daily_spend + estimated_cost > self.limits["per_user_daily"]:
            raise CostLimitError(
                f"Daily budget would be exceeded. "
                f"Current: ${daily_spend:.2f}, "
                f"Limit: ${self.limits['per_user_daily']}"
            )

        # Выполняем
        try:
            result = await execute_fn()
            return result
        finally:
            # Записываем actual cost после выполнения
            pass

    def set_user_budget(self, user_id: str, daily_limit: float):
        """Устанавливаем индивидуальный лимит"""
        self.tracker.budgets[user_id] = daily_limit
```

### Cost Alerts

```python
class CostAlerter:
    """Система алертов по стоимости"""

    def __init__(self):
        self.thresholds = {
            "warning": 0.7,  # 70% от лимита
            "critical": 0.9  # 90% от лимита
        }
        self.notified = set()

    async def check_and_alert(
        self,
        tracker: CostTracker,
        limits: dict
    ):
        """Проверяем и отправляем алерты"""
        report = tracker.get_report(
            start_time=datetime.now().replace(
                hour=0, minute=0, second=0
            ).timestamp()
        )

        daily_spend = report["total_cost"]
        daily_limit = limits.get("global_daily", float('inf'))

        ratio = daily_spend / daily_limit

        if ratio >= self.thresholds["critical"]:
            if "critical" not in self.notified:
                await self._send_alert(
                    level="critical",
                    message=f"Daily spend at {ratio*100:.1f}% of limit! "
                           f"${daily_spend:.2f} / ${daily_limit:.2f}"
                )
                self.notified.add("critical")

        elif ratio >= self.thresholds["warning"]:
            if "warning" not in self.notified:
                await self._send_alert(
                    level="warning",
                    message=f"Daily spend at {ratio*100:.1f}% of limit"
                )
                self.notified.add("warning")

    async def _send_alert(self, level: str, message: str):
        """Отправляем алерт"""
        # Slack, email, PagerDuty etc.
        print(f"[{level.upper()}] {message}")
```

---

## Чек-лист оптимизации

### Quick wins (сделать первыми)

```
□ MODEL SELECTION
  □ Использовать routing по сложности задачи
  □ Не использовать GPT-4/Claude Opus для простых задач
  □ Включить cascade pattern для fallback

□ PROMPT OPTIMIZATION
  □ Сжать system prompt (цель: -50% токенов)
  □ Убрать избыточные инструкции
  □ Использовать abbreviations

□ CACHING
  □ Включить prompt caching (Anthropic/OpenAI)
  □ Кэшировать результаты tools
  □ Semantic cache для похожих запросов

□ CONTEXT MANAGEMENT
  □ Ограничить context window
  □ Суммаризировать старый контекст
  □ Lazy loading для контекста
```

### Advanced optimizations

```
□ ARCHITECTURE
  □ Batch processing для однотипных задач
  □ Speculative execution
  □ Parallel tool calls

□ MONITORING
  □ Cost tracking per request
  □ Budget limits per user
  □ Daily alerts

□ CONTINUOUS IMPROVEMENT
  □ A/B test model combinations
  □ Analyze cost/quality tradeoffs
  □ Regular prompt optimization
```

### ROI калькулятор

```
BEFORE OPTIMIZATION:
- 10,000 requests/day
- Average cost: $0.25/request
- Daily cost: $2,500
- Monthly: $75,000

AFTER OPTIMIZATION:
- Model routing: -40% cost ($0.15/request)
- Prompt compression: -20% tokens
- Caching (30% hit rate): -20% cost
- Combined: $0.09/request

New monthly: $27,000
Savings: $48,000/month (64%)
```

---

## Связанные материалы

- [[ai-agents-advanced]] — архитектура агентов
- [[agent-debugging-troubleshooting]] — debugging агентов
- [[ai-cost-optimization]] — общая оптимизация AI costs
- [[ai-observability-monitoring]] — мониторинг AI систем

---

*Создано: 2026-01-11*
