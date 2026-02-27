---
title: "AI Cost Optimization - Полное Руководство"
tags:
  - topic/ai-ml
  - cost
  - performance
  - pricing
  - tokens
  - caching
  - batch
  - rag
  - routing
  - type/concept
  - level/advanced
category: ai-ml
level: advanced
created: 2025-01-15
updated: 2026-02-13
reading_time: 86
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - [llm-fundamentals]]
  - "[[ai-observability-monitoring]]"
  - "[[rag-systems]"
sources:
  - openai.com
  - anthropic.com
  - cloud.google.com
  - deepseek.com
  - microsoft.com
status: published
---

# AI Cost Optimization: Сокращение затрат на 60-95%

> Полное руководство по оптимизации затрат на LLM API: от простых настроек до production-grade инфраструктуры.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Понимание токенов, контекста, inference | [[llm-fundamentals]] |
| **LLM API интеграция** | Работа с OpenAI, Anthropic, Google API | [[ai-api-integration]] |
| **Python** | Примеры кода, скрипты оптимизации | Любой курс Python |
| **Мониторинг/логирование** | Tracking затрат | [[ai-observability-monitoring]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Рано | Сначала [[llm-fundamentals]] и [[ai-api-integration]] |
| **Разработчик с AI опытом** | ✅ Да | Фокус на практических техниках |
| **Tech Lead / Architect** | ✅ Да | Стратегические решения, ROI |
| **DevOps/FinOps** | ✅ Да | Мониторинг, бюджетирование, инфраструктура |

### Терминология для новичков

> 💡 **Cost Optimization** = получить тот же результат за меньшие деньги (или лучший результат за те же деньги)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Input/Output Tokens** | Входные и выходные "кусочки" текста | **Такси** — платишь за километры туда (input) и обратно (output) |
| **Prompt Caching** | Кэширование повторяющихся частей запроса | **Шаблон письма** — не печатаешь шапку каждый раз |
| **Batch API** | Асинхронная обработка со скидкой | **Оптовая покупка** — дешевле за объём, но ждать дольше |
| **Model Routing** | Выбор модели по сложности задачи | **Такси vs метро** — для простой поездки не нужен лимузин |
| **Semantic Caching** | Кэширование похожих по смыслу запросов | **"Как дела?" = "Как поживаешь?"** — один ответ на оба |
| **Token Compression** | Сжатие промпта без потери смысла | **Telegram вместо email** — короче, но суть та же |
| **Self-hosting** | Запуск модели на своих серверах | **Своя машина vs такси** — дорого купить, дёшево ездить |

---

## Теоретические основы

> **Cost Optimization** LLM-систем — инженерная дисциплина минимизации совокупной стоимости владения (TCO) AI-приложениями при сохранении целевых метрик качества. Включает оптимизацию на уровнях промптов, моделей, кэширования, инфраструктуры и архитектуры.

Экономика LLM имеет уникальную структуру, отличающуюся от классических SaaS:

| Концепция | Теоретическая база | Применение к LLM |
|-----------|-------------------|------------------|
| **Scaling Laws** | Kaplan et al. (2020), arXiv:2001.08361 | Качество растёт как $\log(C)$ от compute; 10x cost → линейное улучшение |
| **Information Theory** | Shannon (1948) | Минимальное количество битов для передачи информации → нижняя граница сжатия промпта |
| **Caching Theory** | Belady (1966), оптимальный алгоритм | Prompt caching: 90% экономия на повторяющихся system prompts |
| **Queueing Theory** | Little's Law: $L = \lambda W$ | Batch processing: оптимальный размер batch для throughput/latency tradeoff |
| **Make vs Buy** | Williamson (1975), Transaction Cost Economics | Self-hosting vs API: при каком объёме выгоднее собственная инфраструктура |

> **Фундаментальная формула стоимости LLM:** $Cost = \sum_{i=1}^{N} (T_{in}^i \cdot P_{in} + T_{out}^i \cdot P_{out}) \cdot (1 - cache\_hit\_rate)$, где $T$ — токены, $P$ — цена за токен, $N$ — количество вызовов. Каждый множитель в формуле — точка оптимизации.

**Иерархия техник оптимизации (по impact):**

| Уровень | Техника | Теория | Экономия |
|---------|---------|--------|----------|
| **Архитектурный** | Model routing | Mixture of Experts (Shazeer, 2017) | 40-70% |
| **Кэширование** | Prompt + Semantic caching | Cache theory + nearest neighbor search | 30-90% |
| **Промпт** | Компрессия, сокращение | Information theory, LLMLingua (Jiang et al., 2023) | 20-50% |
| **Batch** | Batch API, continuous batching | Queueing theory | 50% |
| **Инфраструктурный** | Self-hosting, spot instances | TCO analysis | 60-95% |

Парадокс: самая дешёвая модель ≠ самое дешёвое решение. **Quality-adjusted cost** учитывает retry rate, error rate и downstream impact ошибок.

См. также: [[ai-api-integration|API Integration]] — pricing моделей, [[agent-cost-optimization|Agent Cost Optimization]] — специфика агентов, [[llm-inference-optimization|Inference Optimization]] — ускорение inference.

---

## Зачем это нужно

**Проблема:** LLM API стоят дорого при масштабировании. Компания с 10K запросов/день на GPT-4o платит ~$3,000/месяц только за input tokens.

**Решение:** Комбинация техник оптимизации снижает затраты на 60-95% без потери качества:
- **Prompt Caching** — 50-90% экономия на повторяющихся промптах
- **Model Routing** — дешёвые модели для простых задач (70% трафика)
- **Batch API** — 50% скидка на асинхронные задачи
- **RAG** — 70-90% снижение контекста

**Кому подойдёт:**
- Стартапам, масштабирующим AI-продукты
- Enterprise командам с большими объёмами API вызовов
- Data scientists, строящим production ML пайплайны

**Что вы узнаете:**
1. Актуальные цены всех провайдеров (декабрь 2025)
2. 10 техник оптимизации с кодом
3. ROI калькуляторы для принятия решений
4. Production мониторинг затрат

---

## TL;DR

> **Оптимизация затрат на LLM API** критически важна при масштабировании. Ключевые стратегии 2025:
> - **Prompt Caching**: 50-90% экономия на повторных запросах (OpenAI 50%, Anthropic до 90%)
> - **Batch API**: 50% скидка у всех провайдеров
> - **Model Routing**: направление 70% запросов на дешёвые модели (GPT-4o-mini, Gemini Flash)
> - **Semantic Caching**: 2-10x ускорение + снижение API-вызовов через GPTCache
> - **Token Compression**: LLMLingua обеспечивает до 20x сжатие промптов
> - **Self-hosting**: окупается при 2M+ токенов/день
>
> **Типичный результат**: 60-95% снижение затрат. Компании в финансовом секторе достигают экономии до 99.7%.
>
> **Цены декабрь 2025**: DeepSeek V3 $0.28/1M input, Gemini 2.0 Flash $0.10/1M, GPT-4o $2.50/1M, Claude Sonnet 4 $3/1M, Claude Opus 4.1 $20/1M.

---

## Глоссарий терминов

| Термин | Определение |
|--------|-------------|
| **Tokens** | Единица измерения текста (~4 символа = 1 token) |
| **Input Tokens** | Токены в запросе (промпт + контекст) |
| **Output Tokens** | Токены в ответе (генерация), обычно в 2-5x дороже input |
| **Thinking Tokens** | Токены "размышления" модели (Claude 4.1, o1/o3) |
| **Prompt Caching** | Кэширование повторяющихся префиксов на стороне провайдера |
| **Semantic Caching** | Кэширование похожих по смыслу запросов (GPTCache) |
| **Batch API** | Асинхронная обработка со скидкой 50% (до 24ч) |
| **Model Routing** | Направление запросов на разные модели по сложности |
| **RAG** | Retrieval-Augmented Generation - снижение контекста |
| **Token Compression** | Сжатие промптов (LLMLingua - до 20x) |
| **Fine-tuning** | Дообучение модели под задачу |
| **PEFT/LoRA** | Parameter-Efficient Fine-Tuning - дешёвое дообучение |

---

## 1. Pricing Landscape (Декабрь 2025)

### Сравнительная таблица цен

```
+===========================================================================+
|                    LLM API Pricing (per 1M tokens)                        |
|                         Декабрь 2025                                      |
+===========================================================================+
|                                                                           |
|  Model                   Input      Output     Context    Batch    Notes  |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  ULTRA-BUDGET TIER (< $0.50/1M):                                          |
|  Gemini 2.0 Flash        $0.10      $0.40      1M         50%     Best!   |
|  GPT-4o-mini             $0.15      $0.60      128K       50%     Fast    |
|  DeepSeek V3.2           $0.28      $0.42      128K       -       MIT     |
|  Gemini 2.5 Flash        $0.30      $2.50      1M         50%     Reason  |
|  Gemini 3 Flash          $0.50      $3.00      1M         50%     NEW!    |
|                                                                           |
|  BUDGET TIER ($0.50-$2.00):                                               |
|  Claude 3.5 Haiku        $0.80      $4.00      200K       50%     Fast    |
|  Gemini 2.5 Pro          $1.25      $10.00     1M         50%     Reason  |
|                                                                           |
|  MID TIER ($2.00-$5.00):                                                  |
|  GPT-4o                  $2.50      $10.00     128K       50%     Std     |
|  Claude Sonnet 4         $3.00      $15.00     200K       50%     Best    |
|  Claude Sonnet 4.5       $3.00      $15.00     200K       50%     Latest  |
|  Claude 4.1 Sonnet       $5.00      $25.00     200K       50%     +Think  |
|                                                                           |
|  PREMIUM TIER ($15+):                                                     |
|  Claude 4.1 Opus         $20.00     $80.00     200K       50%     Best    |
|  o1                      $15.00     $60.00     200K       50%     Reason  |
|  o3-mini                 $1.10      $4.40      128K       50%     Reason  |
|  o3                      $10.00     $40.00     128K       50%     NEW!    |
|                                                                           |
|  -----------------------------------------------------------------------  |
|  Price Ratio: Premium vs Ultra-Budget = 50x-200x difference!              |
|                                                                           |
|  KEY INSIGHT: Gemini 2.0 Flash at $0.10/1M is 200x cheaper than           |
|  Claude 4.1 Opus at $20/1M - choose wisely!                               |
|                                                                           |
+===========================================================================+
```

### Дополнительные расходы (Thinking Tokens)

```python
# Claude 4.1 ввёл новую категорию: Thinking Tokens
# Это токены "размышления" модели, которые оплачиваются отдельно

# Claude 4.1 Sonnet thinking pricing:
# Input: $5.00/1M
# Output: $25.00/1M
# Thinking: $10.00/1M  <-- Новая категория!

# При сложных задачах thinking tokens могут составлять 30-50% от общего usage
# Это важно учитывать при бюджетировании
```

### ROI Калькулятор

```python
def calculate_monthly_cost(
    requests_per_day: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price: float,  # per 1M tokens
    output_price: float,  # per 1M tokens
    cache_hit_rate: float = 0,  # 0-1
    cache_discount: float = 0.5,  # OpenAI 50%, Anthropic 90%
    batch_eligible_pct: float = 0  # % запросов через Batch API
) -> dict:
    """
    Расчёт месячных затрат на LLM API с учётом оптимизаций

    Returns:
        dict с base_cost, optimized_cost, savings
    """
    monthly_requests = requests_per_day * 30

    # Базовая стоимость (без оптимизаций)
    base_input_cost = (monthly_requests * avg_input_tokens / 1_000_000) * input_price
    base_output_cost = (monthly_requests * avg_output_tokens / 1_000_000) * output_price
    base_cost = base_input_cost + base_output_cost

    # С учётом prompt caching
    cached_input_cost = base_input_cost * (1 - cache_hit_rate * cache_discount)

    # С учётом Batch API (50% скидка на eligible запросы)
    batch_savings = (cached_input_cost + base_output_cost) * batch_eligible_pct * 0.5

    optimized_cost = cached_input_cost + base_output_cost - batch_savings

    return {
        "base_cost": base_cost,
        "optimized_cost": optimized_cost,
        "monthly_savings": base_cost - optimized_cost,
        "savings_percent": (1 - optimized_cost / base_cost) * 100 if base_cost > 0 else 0
    }

# ПРИМЕР 1: 10K запросов/день, 2000 input + 500 output tokens

# Вариант A: GPT-4o без оптимизаций
gpt4_base = calculate_monthly_cost(10000, 2000, 500, 2.50, 10.00)
# base_cost = $3,000/месяц

# Вариант B: GPT-4o с caching (60% hit rate) + 30% batch
gpt4_optimized = calculate_monthly_cost(
    10000, 2000, 500, 2.50, 10.00,
    cache_hit_rate=0.6, cache_discount=0.5, batch_eligible_pct=0.3
)
# optimized_cost = ~$1,575/месяц (47% экономия)

# Вариант C: GPT-4o-mini для 70% запросов + GPT-4o для 30%
mixed_cost = (
    calculate_monthly_cost(7000, 2000, 500, 0.15, 0.60)["base_cost"] +  # mini
    calculate_monthly_cost(3000, 2000, 500, 2.50, 10.00)["base_cost"]   # full
)
# = $126 + $900 = $1,026/месяц (66% экономия)

# Вариант D: Gemini 2.0 Flash для всего (если качество достаточно)
gemini_cost = calculate_monthly_cost(10000, 2000, 500, 0.10, 0.40)
# = $180/месяц (94% экономия!)

print(f"""
Сравнение вариантов (10K req/day):
---------------------------------
GPT-4o базовый:        ${gpt4_base['base_cost']:,.0f}/мес
GPT-4o оптимизированный: ${gpt4_optimized['optimized_cost']:,.0f}/мес (-47%)
Mixed routing:          ${mixed_cost:,.0f}/мес (-66%)
Gemini 2.0 Flash:       ${gemini_cost['base_cost']:,.0f}/мес (-94%)
""")
```

---

## 2. Prompt Caching

### Сравнение подходов провайдеров

```
+===========================================================================+
|                       Prompt Caching Comparison                           |
+===========================================================================+
|                                                                           |
|  Provider    | Discount | Min Tokens | TTL      | Implementation          |
|  -----------------------------------------------------------------------  |
|  OpenAI      | 50%      | 1,024      | 5-60 min | Automatic               |
|  Anthropic   | 90%      | 1,024-2048 | 5 min    | Explicit cache_control  |
|  Google      | -        | 32,000     | -        | Context caching API     |
|                                                                           |
|  ВАЖНО: Anthropic взимает +25% за Cache Write, но -90% за Cache Read     |
|  Break-even: 3-5 запросов с одним prefix                                  |
|                                                                           |
+===========================================================================+
```

### OpenAI Prompt Caching (Автоматический)

```python
from openai import OpenAI

client = OpenAI()

# Prompt caching включён АВТОМАТИЧЕСКИ для:
# - GPT-4o, GPT-4o-mini, o1, o1-mini, o3, o3-mini
# - Промптов > 1024 токенов
# - Cache hits в increments по 128 токенов

# КЛЮЧ К УСПЕХУ: статический контент в НАЧАЛЕ промпта

# Структура для максимального cache hit:
STATIC_SYSTEM_PROMPT = """
You are a customer support assistant for TechCorp.
[Детальные инструкции - 2000+ токенов]
[Документация продуктов - 3000+ токенов]
[Политики и процедуры - 1000+ токенов]
"""  # 6000+ токенов - будет закэширован

def support_query(user_question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": STATIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_question}  # Динамическая часть
        ]
    )

    # Проверяем cache hit в usage
    usage = response.usage
    if hasattr(usage, 'prompt_tokens_details'):
        cached = usage.prompt_tokens_details.cached_tokens
        total = usage.prompt_tokens
        print(f"Cache hit rate: {cached/total*100:.1f}% ({cached}/{total} tokens)")

    return response.choices[0].message.content

# Первый запрос: cache miss, полная цена
# Последующие запросы: ~6000 tokens cached = 50% скидка на них
# При 6000 cached из 6100 total = 49% экономия на input tokens
```

### Anthropic Prompt Caching (Явный)

```python
import anthropic

client = anthropic.Anthropic()

# Anthropic требует ЯВНЫХ cache_control breakpoints
# Pricing: Cache Write +25%, Cache Read -90%

# Пример: анализ контрактов (длинный контекст)
def analyze_contract(contract_text: str, question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": """You are a legal assistant specialized in contract law.
                [Детальные инструкции на 1500+ токенов]""",
                "cache_control": {"type": "ephemeral"}  # Кэшировать system prompt
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": contract_text,  # Большой документ
                        "cache_control": {"type": "ephemeral"}  # Кэшировать контракт
                    },
                    {
                        "type": "text",
                        "text": f"Question: {question}"  # Переменный вопрос
                    }
                ]
            }
        ]
    )

    return response.content[0].text

# РАСЧЁТ ЭКОНОМИИ (Claude Sonnet 4: $3/1M input):
# Контракт: 5000 tokens, System: 1500 tokens, Question: 100 tokens
#
# Без кэширования (10 вопросов):
# 10 × 6600 tokens × $3/1M = $0.198
#
# С кэшированием (10 вопросов):
# Cache write: 6500 × $3.75/1M = $0.024 (+25%)
# Cache reads: 9 × 6500 × $0.30/1M = $0.018 (-90%)
# Uncached: 10 × 100 × $3/1M = $0.003
# Total: $0.045
#
# ЭКОНОМИЯ: 77% ($0.198 → $0.045)
```

### Best Practices для кэширования

```python
# ========================================
# ПРАВИЛА СТРУКТУРИРОВАНИЯ ПРОМПТОВ
# ========================================

# DO: Статический контент в начале
messages = [
    {"role": "system", "content": long_static_instructions},  # Кэшируется
    {"role": "user", "content": static_few_shot_examples},    # Кэшируется
    {"role": "user", "content": variable_user_query}          # НЕ кэшируется
]

# DON'T: Динамический контент в начале (ломает кэш)
messages = [
    {"role": "system", "content": f"Current time: {datetime.now()}"},  # BAD!
    {"role": "user", "content": long_instructions}  # Не закэшируется
]

# DON'T: Рандомизация порядка few-shot примеров
# Каждый новый порядок = новый cache key

# ========================================
# МИНИМАЛЬНЫЕ РАЗМЕРЫ ДЛЯ КЭШИРОВАНИЯ
# ========================================

CACHE_MINIMUMS = {
    "openai": 1024,      # tokens, автоматически
    "anthropic_haiku": 1024,
    "anthropic_sonnet": 2048,
    "anthropic_opus": 2048,
    "google": 32768,     # Требует Context Caching API
}

# ========================================
# МОНИТОРИНГ CACHE HIT RATE
# ========================================

class CacheMonitor:
    def __init__(self):
        self.hits = 0
        self.total_cached_tokens = 0
        self.total_input_tokens = 0

    def record(self, response):
        usage = response.usage
        if hasattr(usage, 'prompt_tokens_details'):
            cached = usage.prompt_tokens_details.cached_tokens
            self.total_cached_tokens += cached
            self.total_input_tokens += usage.prompt_tokens
            if cached > 0:
                self.hits += 1

    @property
    def hit_rate(self):
        if self.total_input_tokens == 0:
            return 0
        return self.total_cached_tokens / self.total_input_tokens

# Target: >60% cache hit rate для production workloads
```

---

## 3. Semantic Caching (GPTCache)

### Концепция

```
+===========================================================================+
|                      Semantic Caching vs Exact Caching                    |
+===========================================================================+
|                                                                           |
|  EXACT CACHING (Prompt Caching):                                          |
|  Query: "What is the capital of France?"                                  |
|  Cache Key: exact string hash                                             |
|  Hit: только идентичный запрос                                            |
|                                                                           |
|  SEMANTIC CACHING (GPTCache):                                             |
|  Query: "What is the capital of France?"                                  |
|  Similar: "Tell me France's capital city"                                 |
|  Similar: "Which city is the capital of France?"                          |
|  → Все возвращают cached response!                                        |
|                                                                           |
|  РЕЗУЛЬТАТЫ:                                                              |
|  - 2-10x ускорение на cache hits                                          |
|  - Исследования показывают: 31% запросов пользователя семантически        |
|    похожи на предыдущие запросы                                           |
|                                                                           |
+===========================================================================+
```

### Реализация GPTCache

```python
# pip install gptcache

from gptcache import Cache
from gptcache.adapter import openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

# Инициализация semantic cache
def init_gptcache():
    # Embedding model для семантического поиска
    onnx = Onnx()

    # Storage backends
    cache_base = CacheBase("sqlite")  # Метаданные
    vector_base = VectorBase("faiss", dimension=onnx.dimension)  # Векторы

    data_manager = get_data_manager(cache_base, vector_base)

    cache = Cache()
    cache.init(
        embedding_func=onnx.to_embeddings,
        data_manager=data_manager,
        similarity_evaluation=SearchDistanceEvaluation(),
    )

    return cache

# Использование с OpenAI
cache = init_gptcache()

# Запросы через адаптер GPTCache
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    cache_obj=cache
)

# Семантически похожий запрос - cache hit!
response2 = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me the capital city of France"}],
    cache_obj=cache
)
# response2 возвращается из кэша без API вызова
```

### GPTCache vs MeanCache (2025)

```python
# GPTCache - классическое решение, но есть проблемы:
# - 233 false hits на 1000 запросов (23% ошибок)
# - Нет generative caching

# MeanCache (IPDPS 2025) - улучшенная версия:
# - Только 89 false hits на 1000 запросов (9% ошибок)
# - Federated learning для улучшения similarity model
# - Privacy-preserving (локальный кэш на устройстве)

# GenerativeCache (март 2025) - самое быстрое:
# - 9x быстрее GPTCache
# - Поддержка generative caching
# - Настраиваемый similarity algorithm

# РЕКОМЕНДАЦИЯ:
# - Для простых use cases: GPTCache (зрелое решение, интеграция с LangChain)
# - Для production с высокими требованиями: MeanCache или GenerativeCache
```

### Метрики эффективности

```python
class SemanticCacheMetrics:
    """Мониторинг эффективности semantic cache"""

    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.false_positives = 0  # Неверные cache hits
        self.latency_with_cache = []
        self.latency_without_cache = []

    def record_hit(self, latency_ms: float, was_correct: bool):
        self.cache_hits += 1
        self.latency_with_cache.append(latency_ms)
        if not was_correct:
            self.false_positives += 1

    def record_miss(self, latency_ms: float):
        self.cache_misses += 1
        self.latency_without_cache.append(latency_ms)

    @property
    def hit_rate(self):
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0

    @property
    def false_positive_rate(self):
        return self.false_positives / self.cache_hits if self.cache_hits > 0 else 0

    @property
    def avg_speedup(self):
        if not self.latency_with_cache or not self.latency_without_cache:
            return 1.0
        avg_hit = sum(self.latency_with_cache) / len(self.latency_with_cache)
        avg_miss = sum(self.latency_without_cache) / len(self.latency_without_cache)
        return avg_miss / avg_hit if avg_hit > 0 else 1.0

# Целевые метрики:
# - Hit rate: 20-40% (зависит от domain)
# - False positive rate: <5%
# - Speedup: 5-10x на cache hits
```

---

## 4. Batch API

### 50% скидка на все провайдеры

```
+===========================================================================+
|                         Batch API Comparison                              |
+===========================================================================+
|                                                                           |
|  Provider   | Discount | Max Wait | Max Requests | Status                 |
|  -----------------------------------------------------------------------  |
|  OpenAI     | 50%      | 24h      | 50,000       | Production             |
|  Anthropic  | 50%      | 24h      | Unlimited    | Production             |
|  Google     | 50%      | -        | -            | Vertex AI              |
|                                                                           |
|  USE CASES:                                                               |
|  - Content moderation at scale                                            |
|  - Document summarization                                                 |
|  - Data enrichment / classification                                       |
|  - Report generation                                                      |
|  - Embeddings generation                                                  |
|  - Bulk translations                                                      |
|                                                                           |
|  НЕ ПОДХОДИТ ДЛЯ:                                                         |
|  - Real-time chat                                                         |
|  - Interactive applications                                               |
|  - Latency-sensitive operations                                           |
|                                                                           |
+===========================================================================+
```

### OpenAI Batch API Implementation

```python
from openai import OpenAI
import json
import time
from pathlib import Path

client = OpenAI()

class BatchProcessor:
    """Production-ready batch processor для OpenAI"""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = OpenAI()

    def create_batch_file(self, requests: list[dict], filepath: str) -> str:
        """Создаёт JSONL файл для batch processing"""

        batch_requests = []
        for i, req in enumerate(requests):
            batch_requests.append({
                "custom_id": req.get("id", f"request-{i}"),
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "messages": req["messages"],
                    "max_tokens": req.get("max_tokens", 1000)
                }
            })

        with open(filepath, "w") as f:
            for req in batch_requests:
                f.write(json.dumps(req) + "\n")

        return filepath

    def submit_batch(self, filepath: str) -> str:
        """Загружает файл и создаёт batch job"""

        # Upload file
        with open(filepath, "rb") as f:
            batch_file = self.client.files.create(file=f, purpose="batch")

        # Create batch job
        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        print(f"Batch job created: {batch_job.id}")
        return batch_job.id

    def wait_for_completion(self, batch_id: str, poll_interval: int = 60) -> dict:
        """Ожидает завершения batch job"""

        while True:
            status = self.client.batches.retrieve(batch_id)
            print(f"Status: {status.status} | "
                  f"Completed: {status.request_counts.completed}/"
                  f"{status.request_counts.total}")

            if status.status == "completed":
                return self._get_results(status.output_file_id)
            elif status.status in ["failed", "expired", "cancelled"]:
                raise Exception(f"Batch failed: {status.status}")

            time.sleep(poll_interval)

    def _get_results(self, output_file_id: str) -> dict:
        """Парсит результаты из output file"""

        content = self.client.files.content(output_file_id)
        results = {}

        for line in content.text.strip().split("\n"):
            result = json.loads(line)
            custom_id = result["custom_id"]
            if result["response"]["status_code"] == 200:
                results[custom_id] = result["response"]["body"]["choices"][0]["message"]["content"]
            else:
                results[custom_id] = {"error": result["error"]}

        return results


# ПРИМЕР ИСПОЛЬЗОВАНИЯ
processor = BatchProcessor(model="gpt-4o")

# Подготовка запросов
requests = [
    {"id": f"doc-{i}", "messages": [
        {"role": "user", "content": f"Summarize document {i}: {doc_content}"}
    ]}
    for i, doc_content in enumerate(documents)
]

# Создание и отправка batch
filepath = processor.create_batch_file(requests, "batch_requests.jsonl")
batch_id = processor.submit_batch(filepath)

# Ожидание и получение результатов
results = processor.wait_for_completion(batch_id)

# ЭКОНОМИЯ при 1000 документов, 2000 tokens каждый:
# Real-time: 1000 × 2000 × $2.50/1M = $5.00
# Batch:     1000 × 2000 × $1.25/1M = $2.50 (50% экономия)
```

### Anthropic Batch API

```python
import anthropic

client = anthropic.Anthropic()

# Batch запрос
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"doc-{i}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": f"Analyze document {i}: {content}"}
                ]
            }
        }
        for i, content in enumerate(documents)
    ]
)

print(f"Batch ID: {batch.id}")

# Проверка статуса
while True:
    status = client.messages.batches.retrieve(batch.id)
    print(f"Status: {status.processing_status}")

    if status.processing_status == "ended":
        break
    time.sleep(60)

# Получение результатов
results = {}
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        results[result.custom_id] = result.result.message.content[0].text
    else:
        results[result.custom_id] = {"error": result.result.error}
```

---

## 5. Model Routing

### Tiered Architecture

```
+===========================================================================+
|                     Intelligent Model Routing                             |
+===========================================================================+
|                                                                           |
|  User Query                                                               |
|       |                                                                   |
|       v                                                                   |
|  +--------------------------------------------+                           |
|  |     ROUTER (GPT-4o-mini or rule-based)     |                           |
|  |  Classifies: simple | medium | complex     |                           |
|  +--------------------------------------------+                           |
|            |              |              |                                |
|            v              v              v                                |
|       +---------+    +---------+    +---------+                           |
|       |  NANO   |    |  MINI   |    |  FULL   |                           |
|       | $0.10/M |    | $0.15/M |    | $3.00/M |                           |
|       |  65%    |    |  25%    |    |  10%    |                           |
|       +---------+    +---------+    +---------+                           |
|       Gemini        GPT-4o-mini     Claude                                |
|       Flash                         Sonnet 4                              |
|                                                                           |
|  -----------------------------------------------------------------------  |
|  Query Distribution → Model:                                              |
|  - FAQ, simple lookups → NANO (65%)                                       |
|  - Summarization, classification → MINI (25%)                             |
|  - Complex reasoning, code → FULL (10%)                                   |
|                                                                           |
|  COST CALCULATION:                                                        |
|  Without routing: 100% × $3.00 = $3.00 avg                                |
|  With routing: 65%×$0.10 + 25%×$0.15 + 10%×$3.00 = $0.40 avg             |
|  SAVINGS: 87%!                                                            |
|                                                                           |
+===========================================================================+
```

### Production Router Implementation

```python
from openai import OpenAI
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import anthropic

class ModelTier(Enum):
    NANO = "nano"
    MINI = "mini"
    STANDARD = "standard"
    PREMIUM = "premium"

@dataclass
class ModelConfig:
    provider: str
    model: str
    input_price: float  # per 1M tokens
    output_price: float
    max_tokens: int

MODEL_CONFIGS = {
    ModelTier.NANO: ModelConfig(
        provider="google",
        model="gemini-2.0-flash",
        input_price=0.10,
        output_price=0.40,
        max_tokens=8192
    ),
    ModelTier.MINI: ModelConfig(
        provider="openai",
        model="gpt-4o-mini",
        input_price=0.15,
        output_price=0.60,
        max_tokens=16384
    ),
    ModelTier.STANDARD: ModelConfig(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        input_price=3.00,
        output_price=15.00,
        max_tokens=8192
    ),
    ModelTier.PREMIUM: ModelConfig(
        provider="anthropic",
        model="claude-4-1-opus-20251024",
        input_price=20.00,
        output_price=80.00,
        max_tokens=8192
    ),
}

class IntelligentRouter:
    """Production router с multiple strategies"""

    def __init__(self):
        self.openai = OpenAI()
        self.anthropic = anthropic.Anthropic()

        # Keyword-based quick routing (no LLM call needed)
        self.simple_patterns = [
            "what is", "who is", "when was", "where is",
            "define", "meaning of", "translate",
        ]
        self.complex_patterns = [
            "analyze", "compare", "design", "architect",
            "write code", "debug", "review", "explain in detail",
        ]

    def classify_query(self, query: str) -> ModelTier:
        """Классификация с fallback стратегиями"""

        query_lower = query.lower()

        # 1. Rule-based quick classification (бесплатно)
        if any(p in query_lower for p in self.simple_patterns):
            if len(query) < 100:  # Короткий простой запрос
                return ModelTier.NANO

        if any(p in query_lower for p in self.complex_patterns):
            return ModelTier.STANDARD

        # 2. LLM-based classification для неопределённых случаев
        return self._llm_classify(query)

    def _llm_classify(self, query: str) -> ModelTier:
        """LLM classification (дёшево через mini)"""

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Classify query complexity. Respond with ONE word:
                    SIMPLE: factual questions, greetings, lookups, definitions
                    MEDIUM: summarization, basic analysis, standard tasks
                    COMPLEX: multi-step reasoning, code, architecture, creative
                    EXPERT: research, complex analysis requiring top models"""
                },
                {"role": "user", "content": query[:500]}  # Ограничиваем длину
            ],
            max_tokens=10,
            temperature=0
        )

        classification = response.choices[0].message.content.strip().upper()

        tier_map = {
            "SIMPLE": ModelTier.NANO,
            "MEDIUM": ModelTier.MINI,
            "COMPLEX": ModelTier.STANDARD,
            "EXPERT": ModelTier.PREMIUM,
        }

        return tier_map.get(classification, ModelTier.MINI)

    def route_and_execute(self, query: str, system_prompt: Optional[str] = None) -> dict:
        """Полный pipeline: classify → route → execute"""

        tier = self.classify_query(query)
        config = MODEL_CONFIGS[tier]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        # Execute on appropriate provider
        if config.provider == "openai":
            response = self.openai.chat.completions.create(
                model=config.model,
                messages=messages,
                max_tokens=config.max_tokens
            )
            content = response.choices[0].message.content
            usage = {"input": response.usage.prompt_tokens,
                     "output": response.usage.completion_tokens}

        elif config.provider == "anthropic":
            response = self.anthropic.messages.create(
                model=config.model,
                messages=messages[1:] if system_prompt else messages,
                system=system_prompt if system_prompt else None,
                max_tokens=config.max_tokens
            )
            content = response.content[0].text
            usage = {"input": response.usage.input_tokens,
                     "output": response.usage.output_tokens}

        # Calculate cost
        cost = (
            usage["input"] / 1_000_000 * config.input_price +
            usage["output"] / 1_000_000 * config.output_price
        )

        return {
            "tier": tier.value,
            "model": config.model,
            "content": content,
            "usage": usage,
            "cost": cost
        }


# ИСПОЛЬЗОВАНИЕ
router = IntelligentRouter()

# Примеры routing
queries = [
    "What is Python?",                    # → NANO
    "Summarize this article: ...",        # → MINI
    "Design a microservices architecture for e-commerce", # → STANDARD
    "Analyze the implications of...",     # → STANDARD/PREMIUM
]

for query in queries:
    result = router.route_and_execute(query)
    print(f"Query: {query[:50]}...")
    print(f"  Routed to: {result['tier']} ({result['model']})")
    print(f"  Cost: ${result['cost']:.6f}")
```

---

## 6. Token Compression (LLMLingua)

### До 20x сжатие промптов

```
+===========================================================================+
|                         LLMLingua Compression                             |
+===========================================================================+
|                                                                           |
|  BEFORE COMPRESSION (800 tokens):                                         |
|  "I would like you to help me with summarizing a document. The document   |
|   is about artificial intelligence and machine learning. I would like     |
|   you to provide a concise summary that captures the main points. Please  |
|   make sure to include the key findings and conclusions. The summary      |
|   should be clear and easy to understand. Can you help me with this?      |
|   Here is the document: [content]"                                        |
|                                                                           |
|  AFTER COMPRESSION (80 tokens):                                           |
|  "Summarize document. AI/ML topic. Concise, main points, key findings,    |
|   conclusions. Clear, understandable. Document: [content]"                |
|                                                                           |
|  COMPRESSION RATIO: 10x                                                   |
|  QUALITY RETENTION: 95%+                                                  |
|                                                                           |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  COST IMPACT (RAG pipeline, 10K queries/day, GPT-4o):                     |
|  Before: 10K × 5000 tokens × $2.50/1M = $125/day                          |
|  After:  10K × 500 tokens × $2.50/1M = $12.50/day                         |
|  SAVINGS: $112.50/day = $3,375/month (90%)                                |
|                                                                           |
+===========================================================================+
```

### Implementation

```python
# pip install llmlingua

from llmlingua import PromptCompressor

class CostOptimizedLLM:
    """LLM client с автоматическим сжатием промптов"""

    def __init__(self, compression_rate: float = 0.5):
        self.compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,  # Более быстрая версия
        )
        self.compression_rate = compression_rate
        self.openai = OpenAI()

        # Статистика
        self.original_tokens = 0
        self.compressed_tokens = 0

    def compress_prompt(self, prompt: str, force_tokens: list[str] = None) -> str:
        """Сжимает промпт с сохранением ключевых токенов"""

        result = self.compressor.compress_prompt(
            prompt,
            rate=self.compression_rate,
            force_tokens=force_tokens or [],  # Токены, которые нельзя удалять
            drop_consecutive=True,  # Удалять последовательные токены
        )

        self.original_tokens += result["origin_tokens"]
        self.compressed_tokens += result["compressed_tokens"]

        return result["compressed_prompt"]

    def chat(self,
             user_message: str,
             system_prompt: str = None,
             compress_user: bool = True,
             compress_system: bool = False) -> str:
        """Chat с опциональной компрессией"""

        messages = []

        if system_prompt:
            if compress_system and len(system_prompt) > 500:
                system_prompt = self.compress_prompt(system_prompt)
            messages.append({"role": "system", "content": system_prompt})

        if compress_user and len(user_message) > 500:
            user_message = self.compress_prompt(user_message)

        messages.append({"role": "user", "content": user_message})

        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return response.choices[0].message.content

    @property
    def compression_stats(self) -> dict:
        """Статистика сжатия"""
        if self.original_tokens == 0:
            return {"ratio": 1.0, "savings_pct": 0}

        ratio = self.original_tokens / self.compressed_tokens
        savings = 1 - (self.compressed_tokens / self.original_tokens)

        return {
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "compression_ratio": ratio,
            "savings_percent": savings * 100
        }


# ИСПОЛЬЗОВАНИЕ
llm = CostOptimizedLLM(compression_rate=0.3)  # Сжать до 30%

# RAG context compression
long_context = """
Based on the retrieved documents, here is the relevant information:

Document 1: Introduction to Machine Learning
Machine learning is a subset of artificial intelligence that provides systems
the ability to automatically learn and improve from experience without being
explicitly programmed. Machine learning focuses on the development of computer
programs that can access data and use it to learn for themselves.
[... ещё 4000 токенов ...]
"""

response = llm.chat(
    user_message="What is the definition of machine learning?",
    system_prompt=long_context,
    compress_system=True  # Сжимаем контекст
)

print(f"Compression stats: {llm.compression_stats}")
# Типичный результат: 5-10x сжатие
```

### LongLLMLingua для RAG

```python
from llmlingua import PromptCompressor

# LongLLMLingua специально оптимизирован для RAG
# Решает проблему "lost in the middle" в длинном контексте

compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    use_llmlingua2=True,
)

def compress_rag_context(
    question: str,
    retrieved_docs: list[str],
    target_ratio: float = 0.25  # Сжать до 25%
) -> str:
    """Сжимает RAG контекст с учётом релевантности к вопросу"""

    # Объединяем документы
    context = "\n\n".join([
        f"Document {i+1}:\n{doc}"
        for i, doc in enumerate(retrieved_docs)
    ])

    # LongLLMLingua сохраняет релевантные к вопросу части
    result = compressor.compress_prompt(
        context,
        question=question,  # Учитывает вопрос при сжатии
        rate=target_ratio,
        condition_in_question="after_condition",
        reorder_context="sort",  # Переупорядочивает по релевантности
    )

    return result["compressed_prompt"]

# Пример
docs = [
    "Large document about Python basics...",
    "Document about machine learning algorithms...",
    "Document about web development...",
]

compressed = compress_rag_context(
    question="What machine learning algorithms are mentioned?",
    retrieved_docs=docs,
    target_ratio=0.25
)

# Результат: 75% токенов удалено, но релевантная информация о ML сохранена
```

---

## 7. RAG для сокращения контекста

### RAG Cost Analysis

```
+===========================================================================+
|                      RAG vs Full Context Cost                             |
+===========================================================================+
|                                                                           |
|  SCENARIO: Customer support with 100-page knowledge base                  |
|                                                                           |
|  WITHOUT RAG (Full Context):                                              |
|  +--------------------------------------------------------+               |
|  | [Entire Documentation: 50,000 tokens] [Query: 50 tok]  |               |
|  | Cost per query: 50,050 × $2.50/1M = $0.125             |               |
|  +--------------------------------------------------------+               |
|  Monthly (10K queries): $1,250                                            |
|                                                                           |
|  WITH RAG (Top-5 Chunks):                                                 |
|  +--------------------------------------------------------+               |
|  | [5 Relevant Chunks: 2,500 tokens] [Query: 50 tokens]   |               |
|  | Cost per query: 2,550 × $2.50/1M = $0.006              |               |
|  +--------------------------------------------------------+               |
|  Monthly (10K queries): $63.75                                            |
|                                                                           |
|  SAVINGS: 95% ($1,186.25/month)                                           |
|                                                                           |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  RAG INFRASTRUCTURE COSTS (monthly):                                      |
|  - Embedding generation (one-time): ~$5-20                                |
|  - Vector DB (Pinecone): $70-700                                          |
|  - Retrieval queries: negligible                                          |
|                                                                           |
|  NET SAVINGS: >90% even with infrastructure costs                         |
|                                                                           |
+===========================================================================+
```

### Cost-Optimized RAG Implementation

```python
from openai import OpenAI
import chromadb
from dataclasses import dataclass

@dataclass
class RAGConfig:
    """Конфигурация для cost-optimized RAG"""

    # Retrieval settings
    top_k: int = 5  # Количество chunks
    chunk_size: int = 500  # Размер chunk в токенах

    # Model settings
    embedding_model: str = "text-embedding-3-small"  # $0.02/1M tokens
    llm_model: str = "gpt-4o-mini"  # Дешёвая модель для большинства
    llm_fallback: str = "gpt-4o"  # Fallback для сложных запросов

    # Optimization
    use_reranking: bool = True
    max_context_tokens: int = 3000
    compress_context: bool = True


class CostOptimizedRAG:
    """Production RAG с оптимизацией затрат"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.openai = OpenAI()
        self.chroma = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma.get_or_create_collection("docs")

        # Для LLMLingua compression
        if config.compress_context:
            from llmlingua import PromptCompressor
            self.compressor = PromptCompressor(use_llmlingua2=True)

    def embed_documents(self, documents: list[str], ids: list[str]):
        """Embeddings через дешёвую модель"""

        # text-embedding-3-small: $0.02/1M tokens (vs $0.13 for large)
        response = self.openai.embeddings.create(
            model=self.config.embedding_model,
            input=documents
        )

        embeddings = [e.embedding for e in response.data]

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids
        )

    def retrieve(self, query: str) -> list[str]:
        """Retrieve top-k relevant chunks"""

        # Query embedding
        query_embedding = self.openai.embeddings.create(
            model=self.config.embedding_model,
            input=[query]
        ).data[0].embedding

        # Vector search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.config.top_k * 2  # Retrieve more for reranking
        )

        documents = results['documents'][0]

        # Optional: Reranking with Cohere or cross-encoder
        if self.config.use_reranking and len(documents) > self.config.top_k:
            documents = self._rerank(query, documents)[:self.config.top_k]

        return documents[:self.config.top_k]

    def _rerank(self, query: str, documents: list[str]) -> list[str]:
        """Simple LLM-based reranking (можно заменить на Cohere)"""
        # Для production рекомендуется Cohere rerank API
        # Здесь упрощённая версия
        return documents

    def query(self, user_query: str) -> dict:
        """Full RAG pipeline"""

        # 1. Retrieve relevant chunks
        chunks = self.retrieve(user_query)
        context = "\n\n".join(chunks)

        # 2. Compress context if needed
        if self.config.compress_context and len(context) > 2000:
            result = self.compressor.compress_prompt(
                context,
                question=user_query,
                rate=0.5
            )
            context = result["compressed_prompt"]

        # 3. Truncate if still too long
        # (Approximate: 1 token ≈ 4 chars)
        max_chars = self.config.max_context_tokens * 4
        if len(context) > max_chars:
            context = context[:max_chars]

        # 4. Generate response
        messages = [
            {
                "role": "system",
                "content": f"""Answer based only on the provided context.
                If the context doesn't contain the answer, say "I don't have this information."

                Context:
                {context}"""
            },
            {"role": "user", "content": user_query}
        ]

        response = self.openai.chat.completions.create(
            model=self.config.llm_model,
            messages=messages,
            max_tokens=500
        )

        # Calculate cost
        usage = response.usage
        model_prices = {
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4o": (2.50, 10.00)
        }
        input_price, output_price = model_prices.get(
            self.config.llm_model, (0.15, 0.60)
        )
        cost = (
            usage.prompt_tokens / 1_000_000 * input_price +
            usage.completion_tokens / 1_000_000 * output_price
        )

        return {
            "answer": response.choices[0].message.content,
            "chunks_used": len(chunks),
            "context_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "cost": cost
        }


# ИСПОЛЬЗОВАНИЕ
config = RAGConfig(
    top_k=5,
    llm_model="gpt-4o-mini",
    compress_context=True
)

rag = CostOptimizedRAG(config)

# Index documents (one-time)
# rag.embed_documents(documents, ids)

# Query
result = rag.query("What is the return policy?")
print(f"Answer: {result['answer']}")
print(f"Cost: ${result['cost']:.6f}")  # Typically $0.0001-0.001
```

---

## 8. Self-Hosting vs API

### When to Self-Host

```
+===========================================================================+
|                    Self-Hosting Decision Matrix                           |
+===========================================================================+
|                                                                           |
|  SELF-HOST IF:                          | USE API IF:                     |
|  ---------------------------------------|-------------------------------- |
|  - >2M tokens/day consistently          | - Variable/low volume           |
|  - Strict compliance (HIPAA, PCI)       | - Standard security OK          |
|  - Need custom fine-tuned models        | - General-purpose tasks         |
|  - No rate limits required              | - Need latest models            |
|  - Have ML infrastructure team          | - Small team, no ML expertise   |
|  - Predictable workload                 | - Spiky/unpredictable load      |
|                                                                           |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  COST COMPARISON (2M tokens/day):                                         |
|                                                                           |
|  GPT-4o API:                                                              |
|  - 2M tokens × 30 days × $2.50/1M = $150/month (input only)               |
|  - Total with output: ~$500-800/month                                     |
|                                                                           |
|  Self-hosted Llama 3.1 70B (A100 GPU):                                    |
|  - AWS p4d.24xlarge: ~$25,000/month                                       |
|  - But: unlimited tokens, no per-token cost                               |
|  - Break-even: ~50M tokens/day                                            |
|                                                                           |
|  Self-hosted Llama 3.1 8B (cheaper):                                      |
|  - AWS g5.2xlarge: ~$850/month                                            |
|  - Supports ~1-2M tokens/day                                              |
|  - Break-even: ~10M tokens/day                                            |
|                                                                           |
+===========================================================================+
```

### Cost Analysis

```python
from dataclasses import dataclass
from enum import Enum

class DeploymentType(Enum):
    API = "api"
    SELF_HOSTED = "self_hosted"
    HYBRID = "hybrid"

@dataclass
class CostAnalysis:
    """Анализ стоимости API vs Self-hosting"""

    # Daily usage
    tokens_per_day: int

    # API costs (per 1M tokens)
    api_input_price: float = 2.50  # GPT-4o
    api_output_price: float = 10.00
    input_output_ratio: float = 0.7  # 70% input, 30% output

    # Self-hosting costs
    gpu_monthly_cost: float = 850  # g5.2xlarge
    gpu_tokens_per_day: int = 2_000_000  # Capacity
    setup_cost: float = 5000  # One-time
    maintenance_hours_per_month: int = 10
    hourly_rate: float = 100  # DevOps/ML engineer

    def calculate_api_cost(self) -> float:
        """Monthly API cost"""
        monthly_tokens = self.tokens_per_day * 30
        input_tokens = monthly_tokens * self.input_output_ratio
        output_tokens = monthly_tokens * (1 - self.input_output_ratio)

        return (
            input_tokens / 1_000_000 * self.api_input_price +
            output_tokens / 1_000_000 * self.api_output_price
        )

    def calculate_self_hosted_cost(self) -> float:
        """Monthly self-hosted cost"""
        num_gpus = max(1, self.tokens_per_day / self.gpu_tokens_per_day)

        gpu_cost = num_gpus * self.gpu_monthly_cost
        maintenance = self.maintenance_hours_per_month * self.hourly_rate

        return gpu_cost + maintenance

    def calculate_tco(self, months: int = 12) -> dict:
        """Total Cost of Ownership over period"""

        api_total = self.calculate_api_cost() * months

        self_hosted_total = (
            self.setup_cost +
            self.calculate_self_hosted_cost() * months
        )

        break_even_months = None
        if self.calculate_self_hosted_cost() < self.calculate_api_cost():
            # Self-hosted cheaper per month
            monthly_savings = self.calculate_api_cost() - self.calculate_self_hosted_cost()
            break_even_months = self.setup_cost / monthly_savings if monthly_savings > 0 else None

        recommendation = DeploymentType.API
        if self.tokens_per_day > 10_000_000:
            recommendation = DeploymentType.SELF_HOSTED
        elif self.tokens_per_day > 2_000_000:
            recommendation = DeploymentType.HYBRID

        return {
            "api_monthly": self.calculate_api_cost(),
            "self_hosted_monthly": self.calculate_self_hosted_cost(),
            "api_total_tco": api_total,
            "self_hosted_total_tco": self_hosted_total,
            "break_even_months": break_even_months,
            "recommendation": recommendation.value,
            "savings_if_self_hosted": api_total - self_hosted_total
        }


# ПРИМЕРЫ АНАЛИЗА

# Scenario 1: Low volume startup
low_volume = CostAnalysis(tokens_per_day=500_000)
print("Low volume (500K tokens/day):")
print(f"  API: ${low_volume.calculate_api_cost():,.0f}/month")
print(f"  Self-hosted: ${low_volume.calculate_self_hosted_cost():,.0f}/month")
print(f"  Recommendation: API")

# Scenario 2: High volume enterprise
high_volume = CostAnalysis(tokens_per_day=20_000_000)
print("\nHigh volume (20M tokens/day):")
print(f"  API: ${high_volume.calculate_api_cost():,.0f}/month")
print(f"  Self-hosted: ${high_volume.calculate_self_hosted_cost():,.0f}/month")
tco = high_volume.calculate_tco(12)
print(f"  12-month savings: ${tco['savings_if_self_hosted']:,.0f}")
print(f"  Recommendation: {tco['recommendation']}")
```

---

## 9. Fine-Tuning vs Prompting

### Decision Framework

```
+===========================================================================+
|                  Fine-Tuning vs Prompting Decision                        |
+===========================================================================+
|                                                                           |
|  USE PROMPTING WHEN:                    | USE FINE-TUNING WHEN:           |
|  ---------------------------------------|-------------------------------- |
|  - Still defining product/UX            | - Stable, well-defined task     |
|  - Need flexibility to iterate          | - Need consistent outputs       |
|  - Low-medium volume                    | - High volume (cost savings)    |
|  - General-purpose tasks                | - Domain-specific knowledge     |
|  - RAG can provide context              | - Knowledge must be embedded    |
|  - Budget for premium models            | - Need to use smaller model     |
|                                                                           |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  COST COMPARISON (1M requests/month):                                     |
|                                                                           |
|  PROMPTING (GPT-4o with 2000 token system prompt):                        |
|  - Per request: 2000 tokens × $2.50/1M = $0.005                           |
|  - Monthly: 1M × $0.005 = $5,000 just for system prompt                   |
|                                                                           |
|  FINE-TUNED (GPT-4o-mini, no system prompt needed):                       |
|  - Fine-tuning cost: ~$500-2000 (one-time)                                |
|  - Per request: 100 tokens × $0.30/1M = $0.00003                          |
|  - Monthly: 1M × $0.00003 = $30                                           |
|  - SAVINGS: 99.4%                                                         |
|                                                                           |
|  OPEN-SOURCE FINE-TUNED (Llama 3.1 8B):                                   |
|  - Fine-tuning: $300-700 (LoRA)                                           |
|  - Inference: ~$0.001 per 1K tokens (self-hosted)                         |
|  - Monthly: ~$100-200                                                     |
|  - Total control, no API limits                                           |
|                                                                           |
+===========================================================================+
```

### Fine-Tuning Cost Estimates (2025)

```python
# Примерные затраты на fine-tuning разных моделей

FINE_TUNING_COSTS = {
    # Open-source с LoRA (Parameter-Efficient)
    "phi-2_2.7B_lora": {
        "training_cost": "$300-700",
        "training_time": "2-4 hours",
        "gpu_required": "1x A100",
        "inference_cost": "~$0.001/1K tokens"
    },

    "mistral_7B_lora": {
        "training_cost": "$1,000-3,000",
        "training_time": "4-8 hours",
        "gpu_required": "1x A100",
        "inference_cost": "~$0.002/1K tokens"
    },

    "llama3.1_8B_lora": {
        "training_cost": "$1,000-3,000",
        "training_time": "4-8 hours",
        "gpu_required": "1x A100",
        "inference_cost": "~$0.002/1K tokens"
    },

    "llama3.1_70B_lora": {
        "training_cost": "$5,000-15,000",
        "training_time": "12-24 hours",
        "gpu_required": "4-8x A100",
        "inference_cost": "~$0.01/1K tokens"
    },

    # Proprietary (OpenAI)
    "gpt-4o-mini_finetuning": {
        "training_cost": "$0.30/1M tokens trained",
        "inference_cost": "$0.30 input / $1.20 output per 1M",
        "min_examples": 10,
        "recommended_examples": "50-100"
    },

    "gpt-4o_finetuning": {
        "training_cost": "$25/1M tokens trained",
        "inference_cost": "$3.75 input / $15 output per 1M",
        "min_examples": 10,
        "recommended_examples": "50-100"
    }
}

# ROI калькулятор для fine-tuning
def calculate_finetuning_roi(
    current_cost_per_request: float,
    finetuned_cost_per_request: float,
    finetuning_cost: float,
    requests_per_month: int
) -> dict:
    """Расчёт ROI от fine-tuning"""

    monthly_savings = (current_cost_per_request - finetuned_cost_per_request) * requests_per_month
    break_even_months = finetuning_cost / monthly_savings if monthly_savings > 0 else float('inf')
    yearly_savings = monthly_savings * 12 - finetuning_cost

    return {
        "monthly_savings": monthly_savings,
        "break_even_months": break_even_months,
        "yearly_roi": yearly_savings / finetuning_cost * 100 if finetuning_cost > 0 else 0,
        "yearly_net_savings": yearly_savings
    }

# Пример: переход с GPT-4o + длинный промпт на fine-tuned GPT-4o-mini
roi = calculate_finetuning_roi(
    current_cost_per_request=0.005,      # GPT-4o с 2000 token prompt
    finetuned_cost_per_request=0.0003,   # Fine-tuned GPT-4o-mini, короткий prompt
    finetuning_cost=1000,                # Стоимость fine-tuning
    requests_per_month=100_000
)

print(f"""
Fine-Tuning ROI Analysis:
-------------------------
Monthly savings: ${roi['monthly_savings']:,.0f}
Break-even: {roi['break_even_months']:.1f} months
Yearly ROI: {roi['yearly_roi']:.0f}%
Yearly net savings: ${roi['yearly_net_savings']:,.0f}
""")
```

---

## 10. Cost Monitoring & Alerts

### Production Monitoring System

```python
import time
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
import json

@dataclass
class UsageRecord:
    timestamp: float
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost: float
    request_id: str
    tier: str = "standard"

@dataclass
class Budget:
    daily_limit: float
    monthly_limit: float
    alert_threshold: float = 0.8  # Alert at 80%
    critical_threshold: float = 0.95  # Critical at 95%

class LLMCostTracker:
    """Production-grade cost tracking system"""

    # Updated prices December 2025
    PRICES = {
        # OpenAI
        "gpt-4o": {"input": 2.50, "output": 10.00, "cached": 1.25},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cached": 0.075},
        "o1": {"input": 15.00, "output": 60.00, "cached": 7.50},
        "o3-mini": {"input": 1.10, "output": 4.40, "cached": 0.55},

        # Anthropic
        "claude-sonnet-4": {"input": 3.00, "output": 15.00, "cached": 0.30},
        "claude-4-1-sonnet": {"input": 5.00, "output": 25.00, "cached": 0.50},
        "claude-4-1-opus": {"input": 20.00, "output": 80.00, "cached": 2.00},
        "claude-3-5-haiku": {"input": 0.80, "output": 4.00, "cached": 0.08},

        # Google
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40, "cached": 0.05},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "cached": 0.625},
        "gemini-3-flash": {"input": 0.50, "output": 3.00, "cached": 0.25},

        # DeepSeek
        "deepseek-v3": {"input": 0.28, "output": 0.42, "cached": 0.028},
    }

    def __init__(self, budget: Budget):
        self.budget = budget
        self.records: list[UsageRecord] = []
        self.alerts_sent: set = set()

    def track(self, response, model: str, provider: str = "openai") -> UsageRecord:
        """Track usage from API response"""

        usage = response.usage
        prices = self.PRICES.get(model, {"input": 0, "output": 0, "cached": 0})

        # Extract tokens
        input_tokens = getattr(usage, 'prompt_tokens', 0) or getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'completion_tokens', 0) or getattr(usage, 'output_tokens', 0)

        # Cached tokens (provider-specific)
        cached_tokens = 0
        if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
            cached_tokens = getattr(usage.prompt_tokens_details, 'cached_tokens', 0)

        # Calculate cost
        uncached_input = input_tokens - cached_tokens
        input_cost = (uncached_input / 1_000_000) * prices["input"]
        cached_cost = (cached_tokens / 1_000_000) * prices["cached"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        total_cost = input_cost + cached_cost + output_cost

        record = UsageRecord(
            timestamp=time.time(),
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost=total_cost,
            request_id=getattr(response, 'id', 'unknown')
        )

        self.records.append(record)
        self._check_alerts()

        return record

    def _check_alerts(self):
        """Check budget thresholds and send alerts"""

        daily = self.get_daily_cost()
        monthly = self.get_monthly_cost()

        # Daily alerts
        daily_pct = daily / self.budget.daily_limit
        if daily_pct >= self.budget.critical_threshold:
            self._send_alert("CRITICAL", f"Daily spend at {daily_pct*100:.1f}%: ${daily:.2f}")
        elif daily_pct >= self.budget.alert_threshold:
            self._send_alert("WARNING", f"Daily spend at {daily_pct*100:.1f}%: ${daily:.2f}")

        # Monthly alerts
        monthly_pct = monthly / self.budget.monthly_limit
        if monthly_pct >= self.budget.critical_threshold:
            self._send_alert("CRITICAL", f"Monthly spend at {monthly_pct*100:.1f}%: ${monthly:.2f}")
        elif monthly_pct >= self.budget.alert_threshold:
            self._send_alert("WARNING", f"Monthly spend at {monthly_pct*100:.1f}%: ${monthly:.2f}")

    def _send_alert(self, level: str, message: str):
        """Send alert (integrate with Slack, PagerDuty, etc.)"""
        alert_key = f"{level}:{datetime.now().strftime('%Y-%m-%d-%H')}"
        if alert_key not in self.alerts_sent:
            print(f"[{level}] {message}")
            self.alerts_sent.add(alert_key)
            # TODO: Integrate with alerting system

    def get_daily_cost(self) -> float:
        """Today's total cost"""
        today_start = time.time() - 86400
        return sum(r.cost for r in self.records if r.timestamp > today_start)

    def get_monthly_cost(self) -> float:
        """Current month's total cost"""
        month_start = time.time() - (30 * 86400)
        return sum(r.cost for r in self.records if r.timestamp > month_start)

    def get_summary(self) -> dict:
        """Comprehensive usage summary"""

        today_start = time.time() - 86400
        daily_records = [r for r in self.records if r.timestamp > today_start]

        by_model = {}
        for r in daily_records:
            if r.model not in by_model:
                by_model[r.model] = {"cost": 0, "requests": 0, "tokens": 0}
            by_model[r.model]["cost"] += r.cost
            by_model[r.model]["requests"] += 1
            by_model[r.model]["tokens"] += r.input_tokens + r.output_tokens

        total_input = sum(r.input_tokens for r in daily_records)
        total_cached = sum(r.cached_tokens for r in daily_records)
        cache_hit_rate = total_cached / total_input if total_input > 0 else 0

        return {
            "daily_cost": self.get_daily_cost(),
            "monthly_cost": self.get_monthly_cost(),
            "daily_limit": self.budget.daily_limit,
            "monthly_limit": self.budget.monthly_limit,
            "daily_usage_pct": self.get_daily_cost() / self.budget.daily_limit * 100,
            "monthly_usage_pct": self.get_monthly_cost() / self.budget.monthly_limit * 100,
            "requests_today": len(daily_records),
            "cache_hit_rate": cache_hit_rate * 100,
            "by_model": by_model,
            "avg_cost_per_request": self.get_daily_cost() / len(daily_records) if daily_records else 0
        }


# ИСПОЛЬЗОВАНИЕ
budget = Budget(daily_limit=100.0, monthly_limit=2000.0)
tracker = LLMCostTracker(budget)

# После каждого API вызова
response = openai.chat.completions.create(...)
record = tracker.track(response, "gpt-4o")

# Периодически проверяем статистику
summary = tracker.get_summary()
print(f"""
Daily Summary:
--------------
Spent: ${summary['daily_cost']:.2f} / ${summary['daily_limit']:.2f} ({summary['daily_usage_pct']:.1f}%)
Requests: {summary['requests_today']}
Cache hit rate: {summary['cache_hit_rate']:.1f}%
Avg cost/request: ${summary['avg_cost_per_request']:.6f}
""")
```

---

## 11. Optimization Checklist

```
+===========================================================================+
|                     COST OPTIMIZATION CHECKLIST                           |
+===========================================================================+
|                                                                           |
|  QUICK WINS (implement first, 1-2 days):                     Est. Savings |
|  -----------------------------------------------------------------------  |
|  [ ] Use cheaper models for 60-70% of requests               30-50%       |
|  [ ] Enable prompt caching (structure prompts correctly)     15-30%       |
|  [ ] Set reasonable max_tokens limits                        10-20%       |
|  [ ] Move batch workloads to Batch API                       50%          |
|  [ ] Remove redundant tokens from prompts                    10-20%       |
|                                                                           |
|  MEDIUM EFFORT (1-2 weeks):                                               |
|  -----------------------------------------------------------------------  |
|  [ ] Implement model routing based on complexity             30-50%       |
|  [ ] Add RAG to reduce context size                          70-90%       |
|  [ ] Set up semantic caching (GPTCache)                      20-40%       |
|  [ ] Implement cost tracking & alerts                        5-10%        |
|  [ ] Use structured outputs for predictable length           15-25%       |
|                                                                           |
|  ADVANCED (1-2 months):                                                   |
|  -----------------------------------------------------------------------  |
|  [ ] LLMLingua prompt compression                            60-80%       |
|  [ ] Fine-tune smaller model for specific tasks              40-80%       |
|  [ ] Self-host for high-volume workloads                     50-90%       |
|  [ ] Implement distillation pipeline                         50-85%       |
|  [ ] Build evaluation framework for quality monitoring       -            |
|                                                                           |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  EXPECTED CUMULATIVE RESULTS:                                             |
|  - Quick wins only: 40-60% reduction                                      |
|  - Quick + Medium: 60-80% reduction                                       |
|  - Full implementation: 80-95% reduction                                  |
|                                                                           |
|  CASE STUDIES:                                                            |
|  - Fintech company: 99.7% reduction ($937,500 -> $3,000/month)           |
|  - Customer support: 50%+ reduction in servicing workload                 |
|  - Financial services: 40% reduction in back-office costs                 |
|                                                                           |
+===========================================================================+
```

---

## 12. Проверь себя

1. **Q: Какую экономию даёт prompt caching у разных провайдеров?**
   A: OpenAI: 50% на cached tokens (автоматически для >1024 tokens). Anthropic: до 90% на cache reads, но +25% на cache write. Break-even: 3-5 запросов.

2. **Q: Когда использовать Batch API?**
   A: Для задач без realtime требований: content moderation, data enrichment, bulk classification, report generation. Все провайдеры дают 50% скидку, latency до 24 часов.

3. **Q: Как работает semantic caching и какие инструменты использовать?**
   A: GPTCache конвертирует запросы в embeddings и находит семантически похожие. 31% запросов пользователей похожи на предыдущие. Альтернативы: MeanCache (меньше false positives), GenerativeCache (9x быстрее).

4. **Q: Когда окупается self-hosting?**
   A: При >2M tokens/day и/или строгих compliance требованиях. Break-even для Llama 8B на g5.2xlarge ($850/month) примерно при 10M tokens/day vs GPT-4o API.

5. **Q: Fine-tuning vs Prompting - когда что использовать?**
   A: Prompting: ранние стадии продукта, гибкость, RAG достаточен. Fine-tuning: stable tasks, high volume, need consistency, domain knowledge, хотите использовать дешёвую модель.

6. **Q: Какую реальную экономию показывают кейсы?**
   A: Финтех компании: 99.7% (с $937K до $3K/month). Financial services: 40% back-office costs. Customer support: 50%+ снижение нагрузки через LLM assistants.

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Kaplan J. et al. (2020). *Scaling Laws for Neural Language Models*. arXiv:2001.08361 | Зависимость качества от compute — основа cost/quality tradeoff |
| 2 | Shannon C. (1948). *A Mathematical Theory of Communication*. Bell System Technical Journal | Теоретический минимум информации → нижняя граница сжатия |
| 3 | Jiang H. et al. (2023). *LLMLingua: Compressing Prompts for Accelerated Inference*. arXiv:2310.05736 | Prompt compression без потери качества |
| 4 | Shazeer N. et al. (2017). *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer*. ICLR | MoE — основа model routing |
| 5 | Williamson O. (1975). *Markets and Hierarchies: Analysis and Antitrust Implications*. Free Press | Transaction Cost Economics — make vs buy для self-hosting |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [OpenAI API Pricing](https://platform.openai.com/docs/pricing) | Актуальные цены |
| 2 | [Anthropic Claude Pricing](https://www.anthropic.com/pricing) | Pricing + prompt caching |
| 3 | [LLMLingua — Microsoft Research](https://github.com/microsoft/LLMLingua) | Token compression 80% |
| 4 | [GPTCache](https://github.com/zilliztech/GPTCache) | Semantic caching |
| 5 | [Continuous Batching — Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference) | 23x throughput |
| 6 | [LLM TCO 2025 — Ptolemay](https://www.ptolemay.com/post/llm-total-cost-of-ownership) | Self-hosting TCO analysis |

---

## Связанные заметки

- [[llm-fundamentals]] - Основы LLM
- [[llm-inference-optimization]] - Оптимизация инференса
- [[local-llms-self-hosting]] - Self-hosting (0 API costs)
- [[ai-observability-monitoring]] - Мониторинг AI систем
- [[rag-systems]] - RAG архитектуры
- [[prompt-engineering]] - Prompt Engineering

---

## Проверь себя

> [!question]- Какие три основных рычага снижения стоимости LLM-приложений существуют?
> Оптимизация токенов (сокращение промптов, кэширование, компрессия контекста), выбор модели (маршрутизация на дешёвые модели для простых задач), и инфраструктура (batch processing, self-hosting для высоких объёмов). Каждый рычаг даёт 30-70% экономии, вместе --- до 90%.

> [!question]- Когда self-hosting LLM выгоднее API-провайдеров?
> При стабильном объёме >100K запросов/день, когда утилизация GPU >70%. Точка безубыточности зависит от модели: для 7B моделей --- от 50K запросов/день, для 70B --- от 200K. Нужно учитывать стоимость GPU, DevOps-инженеров, электричества и downtime.

> [!question]- Как Batch API снижает стоимость и когда его использовать?
> Batch API (OpenAI, Anthropic) обрабатывает запросы асинхронно со скидкой 50%. Подходит для non-real-time задач: аналитика данных, генерация контента, обработка документов, evaluation datasets. Результат приходит в течение 24 часов.

> [!question]- Как построить систему мониторинга затрат на AI?
> Трекать: стоимость по модели, по feature, по пользователю. Метрики: cost-per-task, cost-per-token, cache hit rate. Алерты на аномалии (>2x от baseline). Dashboard с breakdown по компонентам. Инструменты: LangSmith, Helicone, или custom на OpenTelemetry.

---

## Ключевые карточки

Какие модели ценообразования существуют у LLM-провайдеров?
?
Pay-per-token (основной), batch pricing (скидка 50% за асинхронность), committed use discounts (предоплата за объём), и cached pricing (дешевле за повторные промпты). У каждого провайдера своя модель кэширования.

Что такое prompt caching и как оно работает?
?
Провайдер сохраняет обработанный системный промпт и возвращает результат из кэша при повторном запросе с тем же префиксом. Anthropic: автоматический, скидка 90% на cached tokens. OpenAI: prefix caching, скидка 50%.

Как работает model routing для оптимизации стоимости?
?
Классификатор анализирует сложность запроса и направляет на подходящую модель. Простые запросы --- GPT-4o-mini/Haiku ($0.15/M), сложные --- GPT-4o/Sonnet ($3-15/M). Экономия 60-80% при сохранении качества.

Что такое token optimization и какие техники существуют?
?
Сокращение количества токенов в запросах/ответах. Техники: компрессия промптов (убрать лишнее), structured outputs (JSON вместо текста), max_tokens ограничение, сокращение few-shot примеров, и context window management.

Как рассчитать TCO (Total Cost of Ownership) для AI-системы?
?
TCO = API costs + infrastructure + development + maintenance. API: tokens x price. Infrastructure: GPU/CPU, storage, networking. Development: инженеры, testing, evaluation. Maintenance: мониторинг, обновления, incident response.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[agent-cost-optimization]] | Оптимизация стоимости агентов |
| Углубиться | [[llm-inference-optimization]] | Оптимизация inference для self-hosting |
| Смежная тема | [[performance-optimization]] | Общие паттерны оптимизации производительности |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI Engineering |

*Проверено: 2026-01-09*
