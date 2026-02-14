---
title: "LLM API Integration - Практическое руководство 2025"
tags:
  - topic/ai-ml
  - api
  - openai
  - anthropic
  - google
  - litellm
  - streaming
  - production
  - sdk
  - type/concept
  - level/intermediate
category: ai-ml
level: intermediate
created: 2025-12-28
updated: 2025-12-28
sources:
  - platform.openai.com
  - docs.anthropic.com
  - ai.google.dev
  - docs.litellm.ai
  - github.com/BerriAI/litellm
status: published
reading_time: 41
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - "[[structured-outputs-tools]]"
  - "[[agent-cost-optimization]]"
  - "[[api-design]]"
---

# LLM API Integration: Практическое руководство 2025

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Python** | Все примеры на Python, async/await | Любой курс Python |
| **REST API** | Понимание HTTP запросов, headers | [[api-design]] |
| **JSON** | Формат данных для всех LLM API | Базовое программирование |
| **Async программирование** | Streaming, параллельные запросы | Python asyncio |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в программировании** | ❌ Нет | Сначала Python + REST API |
| **Бэкенд разработчик** | ✅ Да | Идеальный уровень для старта |
| **Frontend разработчик** | ⚠️ Частично | Фокус на SDK разделах |
| **DevOps/SRE** | ✅ Да | Фокус на LiteLLM Proxy, production checklist |

### Терминология для новичков

> 💡 **LLM API** = веб-сервис, через который ваше приложение общается с AI-моделью

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **SDK** | Software Development Kit — библиотека для работы с API | **Готовый инструмент** — не пишешь HTTP-запросы вручную |
| **Streaming** | Получение ответа по частям в реальном времени | **Прямой эфир** — видишь текст по мере генерации |
| **Rate Limit** | Ограничение количества запросов | **Очередь в магазине** — нельзя всё сразу |
| **Token** | Единица тарификации и текста | **Слог** — платишь за "кусочки" текста |
| **Exponential Backoff** | Стратегия повторных попыток | **Отступить и попробовать снова** — ждать всё дольше между попытками |
| **Circuit Breaker** | Паттерн защиты от каскадных сбоев | **Автомат в электросети** — выключается при перегрузке |
| **Prompt Caching** | Кэширование начала промпта для экономии | **Шаблон письма** — не пишешь каждый раз с нуля |
| **Structured Output** | Гарантированный JSON-формат ответа | **Форма с полями** — модель заполняет, не импровизирует |
| **Tool Use / Function Calling** | LLM вызывает внешние функции | **Помощник с телефоном** — может позвонить узнать погоду |
| **Fallback** | Запасной вариант при ошибке | **План Б** — если OpenAI не работает, идём в Anthropic |

---

## TL;DR

> **LLM API Integration** - интеграция с провайдерами AI (OpenAI, Anthropic, Google) через их SDK и API.
>
> **Ключевые паттерны 2025:**
> - **Streaming** для UX (SSE events, chunk handling)
> - **Structured Outputs** (Pydantic/Zod схемы, 100% schema compliance)
> - **Tool Use** (function calling, MCP интеграция)
> - **Error Handling** (exponential backoff, circuit breaker, fallback)
> - **Cost Optimization** (prompt caching до 90% скидка, model routing, batch API)
>
> **Unified API:** LiteLLM — один интерфейс для 100+ LLM, OpenAI-совместимый формат.

---

## Зачем это нужно

```
+----------------------------------------------------------------------------+
|                    Проблемы при интеграции с LLM API                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  БЕЗ ПРАВИЛЬНЫХ ПАТТЕРНОВ:              С ПРАВИЛЬНЫМИ ПАТТЕРНАМИ:         |
|                                                                            |
|  - Rate limit errors крашат приложение  + Exponential backoff + fallback  |
|  - Непредсказуемые ответы               + Structured outputs              |
|  - Высокие costs при масштабировании    + Caching (90% экономия)          |
|  - Медленный UX (ожидание ответа)       + Streaming для мгновенного UX    |
|  - Vendor lock-in                       + LiteLLM — unified API           |
|  - Разные SDK для каждого провайдера    + OpenAI-compatible interface     |
|                                                                            |
|  ЭКОНОМИКА:                                                                |
|  - Prompt caching: 90% скидка на cached tokens                            |
|  - Batch API: 50% скидка за async обработку                               |
|  - Model routing: 63% экономия через cascading                            |
|  - Правильные паттерны: -30-80% costs без потери качества                 |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 1. OpenAI SDK (Python)

### Установка и базовая настройка

```python
# pip install openai>=1.0.0

from openai import OpenAI
import os

# Best practice: API key из environment
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=60.0,  # таймаут для запросов
    max_retries=3  # автоматические ретраи
)

# Базовый запрос
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain REST API in 2 sentences."}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

### Streaming

```python
# Streaming для мгновенного UI feedback
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about coding"}],
    stream=True
)

# Обработка chunks
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Async streaming
import asyncio
from openai import AsyncOpenAI

async def stream_response():
    client = AsyncOpenAI()

    async for chunk in await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    ):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Использование
async def main():
    async for text in stream_response():
        print(text, end="", flush=True)

asyncio.run(main())
```

### Structured Outputs (Pydantic)

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# Определяем schema через Pydantic
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

# OpenAI гарантирует соответствие schema (100% compliance)
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",  # Требуется модель с поддержкой structured outputs
    messages=[
        {"role": "system", "content": "Extract event information."},
        {"role": "user", "content": "Meeting with John and Sarah tomorrow at 3pm to discuss Q4 planning"}
    ],
    response_format=CalendarEvent
)

event = response.choices[0].message.parsed
print(f"Event: {event.name}")
print(f"Date: {event.date}")
print(f"Participants: {event.participants}")

# Streaming с Structured Outputs
from openai import OpenAI
from pydantic import BaseModel

class Story(BaseModel):
    title: str
    characters: list[str]
    plot: str

client = OpenAI()

# Stream JSON fields по мере генерации
with client.beta.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": "Create a short story"}],
    response_format=Story
) as stream:
    for event in stream:
        if event.type == "content.delta":
            print(event.snapshot)  # Partial JSON
```

### Tool Use (Function Calling)

```python
from openai import OpenAI
import json

client = OpenAI()

# Определяем tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'London'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Первый запрос
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"  # или "required" для принудительного вызова
)

# Проверяем, нужен ли tool call
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)

        # Вызываем реальную функцию
        result = {"temperature": 22, "condition": "Sunny"}  # Заглушка

        # Отправляем результат обратно
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "What's the weather in Tokyo?"},
                message,  # Включаем assistant message с tool_calls
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
            ]
        )
        print(final_response.choices[0].message.content)
```

---

## 2. Anthropic Claude SDK (Python)

### Установка и базовая настройка

```python
# pip install anthropic>=0.25.0

import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Базовый запрос
message = client.messages.create(
    model="claude-sonnet-4-20250514",  # Последняя модель
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain microservices in 3 bullet points."}
    ]
)

print(message.content[0].text)
```

### Streaming

```python
import anthropic

client = anthropic.Anthropic()

# Streaming с helper методом
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem about AI"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Event-based streaming
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain quantum computing"}]
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(event.delta.text, end="")
        elif event.type == "message_stop":
            print("\n--- Done ---")

# Async streaming
from anthropic import AsyncAnthropic

async def stream_claude():
    client = AsyncAnthropic()

    async with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Tell me about Mars"}]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
```

### Tool Use

```python
import anthropic
import json

client = anthropic.Anthropic()

# Определяем tools
tools = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a given ticker symbol",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, GOOGL)"
                }
            },
            "required": ["ticker"]
        }
    }
]

# Tool use loop
messages = [{"role": "user", "content": "What's Apple's stock price?"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    # Проверяем stop reason
    if response.stop_reason == "end_turn":
        # Финальный ответ
        for block in response.content:
            if hasattr(block, 'text'):
                print(block.text)
        break

    elif response.stop_reason == "tool_use":
        # Обрабатываем tool calls
        for block in response.content:
            if block.type == "tool_use":
                # Вызываем реальную функцию
                result = {"price": 178.50, "change": "+1.2%"}  # Заглушка

                # Добавляем в историю
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    }]
                })
```

### Fine-grained Tool Streaming (Beta)

```python
import anthropic

client = anthropic.Anthropic()

# Beta: streaming tool parameters
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[{
        "name": "generate_story",
        "description": "Generate a story with given parameters",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "plot": {"type": "string"},
                "characters": {"type": "array", "items": {"type": "string"}}
            }
        }
    }],
    messages=[{"role": "user", "content": "Generate a sci-fi story"}],
    betas=["fine-grained-tool-streaming-2025-05-14"]  # Beta feature
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if hasattr(event.delta, 'partial_json'):
                # Streaming tool parameters
                print(f"Partial: {event.delta.partial_json}")
```

---

## 3. Google Gemini SDK (Python)

### Установка и базовая настройка

```python
# pip install google-genai>=1.0.0

from google import genai
import os

# Настройка клиента
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Базовый запрос
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain machine learning in simple terms."
)

print(response.text)
```

### Streaming

```python
from google import genai

client = genai.Client()

# Streaming
for chunk in client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents="Write a detailed explanation of neural networks."
):
    print(chunk.text, end="", flush=True)
```

### Grounding with Google Search

```python
from google import genai
from google.genai import types

client = genai.Client()

# Grounding — актуальная информация из поиска
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are the latest AI developments in December 2025?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)

print(response.text)

# Grounding metadata
if response.candidates[0].grounding_metadata:
    for source in response.candidates[0].grounding_metadata.grounding_chunks:
        print(f"Source: {source.web.title} - {source.web.uri}")
```

### Code Execution

```python
from google import genai
from google.genai import types

client = genai.Client()

# Code execution — модель пишет и выполняет Python код
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Calculate the fibonacci sequence up to 100 and plot it",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.CodeExecution())]
    )
)

# Результат включает код и вывод
for part in response.candidates[0].content.parts:
    if part.executable_code:
        print(f"Code:\n{part.executable_code.code}")
    if part.code_execution_result:
        print(f"Output:\n{part.code_execution_result.output}")
```

---

## 4. LiteLLM — Unified API

### Зачем LiteLLM?

```
+----------------------------------------------------------------------------+
|                    LiteLLM: One Interface, 100+ LLMs                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  ПРОБЛЕМА:                              РЕШЕНИЕ LiteLLM:                   |
|  - OpenAI SDK ≠ Anthropic SDK          + Единый OpenAI-совместимый API    |
|  - Разные форматы ответов              + Единый формат для всех          |
|  - Vendor lock-in                      + Легко менять провайдера          |
|  - Разные системы costs tracking       + Встроенный cost tracking         |
|                                                                            |
|  ПОДДЕРЖКА:                                                                |
|  OpenAI, Anthropic, Google Vertex AI, Azure OpenAI, AWS Bedrock,          |
|  Cohere, Replicate, Hugging Face, vLLM, Ollama, и ещё 90+ провайдеров    |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Базовое использование

```python
# pip install litellm

from litellm import completion

# OpenAI
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Anthropic — тот же интерфейс
response = completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Google Gemini
response = completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Ollama (локальный)
response = completion(
    model="ollama/qwen3:14b",
    messages=[{"role": "user", "content": "Hello!"}],
    api_base="http://localhost:11434"
)

# Все возвращают одинаковый формат!
print(response.choices[0].message.content)
```

### Streaming

```python
from litellm import completion

# Streaming работает одинаково для всех провайдеров
response = completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Async streaming
from litellm import acompletion

async def stream_any_llm(model: str, prompt: str):
    response = await acompletion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### LiteLLM Proxy (Production Gateway)

```yaml
# config.yaml для production
model_list:
  # OpenAI
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  # Anthropic
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

  # Fallback chain
  - model_name: main-model
    litellm_params:
      model: openai/gpt-4o
    model_info:
      priority: 1  # Primary

  - model_name: main-model  # Same name = fallback
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
    model_info:
      priority: 2  # Fallback если primary недоступен

router_settings:
  routing_strategy: simple-shuffle
  allowed_fails: 3
  cooldown_time: 60

litellm_settings:
  success_callback: ["langfuse"]  # Observability
  cache: True
  cache_params:
    type: redis
    host: localhost
    port: 6379

general_settings:
  master_key: sk-your-master-key
  database_url: postgresql://user:pass@host:5432/litellm
```

```bash
# Запуск proxy
docker run -d \
  -p 4000:4000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  docker.litellm.ai/berriai/litellm:main-stable \
  --config /app/config.yaml

# Использование (OpenAI-compatible)
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-your-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "main-model",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

```python
# Python client через OpenAI SDK
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="sk-your-master-key"
)

response = client.chat.completions.create(
    model="main-model",  # Роутится согласно config
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## 5. Error Handling & Retry Patterns

### Exponential Backoff с Tenacity

```python
import tenacity
from openai import OpenAI, RateLimitError, APIError

client = OpenAI()

@tenacity.retry(
    wait=tenacity.wait_random_exponential(min=1, max=60),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type((RateLimitError, APIError)),
    before_sleep=lambda retry_state: print(f"Retry {retry_state.attempt_number}...")
)
def call_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Использование
try:
    result = call_openai("Hello!")
except tenacity.RetryError:
    print("Failed after all retries")
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    reset_timeout: int = 60
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half-open

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            print(f"Circuit breaker OPEN")

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True

        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.reset_timeout):
                self.state = "half-open"
                return True
            return False

        # half-open: allow one request
        return True

# Использование с несколькими провайдерами
class ResilientLLMClient:
    def __init__(self):
        self.providers = {
            "openai": CircuitBreaker(),
            "anthropic": CircuitBreaker()
        }

    def call(self, prompt: str) -> str:
        for provider, breaker in self.providers.items():
            if breaker.can_execute():
                try:
                    result = self._call_provider(provider, prompt)
                    breaker.record_success()
                    return result
                except Exception as e:
                    breaker.record_failure()
                    print(f"{provider} failed: {e}")
                    continue

        raise Exception("All providers failed")

    def _call_provider(self, provider: str, prompt: str) -> str:
        if provider == "openai":
            # OpenAI call
            pass
        elif provider == "anthropic":
            # Anthropic call
            pass
```

### Production Error Handler

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable
import httpx

class ErrorCategory(Enum):
    RETRYABLE = "retryable"      # 429, 500, 502, 503, 504
    NON_RETRYABLE = "non_retryable"  # 400, 401, 403, 404
    UNKNOWN = "unknown"

@dataclass
class LLMError:
    category: ErrorCategory
    message: str
    status_code: Optional[int] = None
    retry_after: Optional[int] = None

def classify_error(error: Exception) -> LLMError:
    """Классифицирует ошибку для правильной обработки"""

    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        retry_after = error.response.headers.get("Retry-After")

        if status == 429:
            return LLMError(
                category=ErrorCategory.RETRYABLE,
                message="Rate limited",
                status_code=status,
                retry_after=int(retry_after) if retry_after else 60
            )
        elif status in (500, 502, 503, 504):
            return LLMError(
                category=ErrorCategory.RETRYABLE,
                message=f"Server error: {status}",
                status_code=status
            )
        elif status in (400, 401, 403, 404):
            return LLMError(
                category=ErrorCategory.NON_RETRYABLE,
                message=f"Client error: {status}",
                status_code=status
            )

    return LLMError(
        category=ErrorCategory.UNKNOWN,
        message=str(error)
    )
```

---

## 6. Cost Optimization

### Prompt Caching

```python
# OpenAI: автоматический caching для prompts >1024 tokens
# Структурируй static content в начале prompt

from openai import OpenAI

client = OpenAI()

# Static system prompt + documents в начале
STATIC_CONTEXT = """
You are a legal document analyzer...
[Большой статический контекст > 1024 tokens]
"""

# Cached: static context переиспользуется между запросами
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": STATIC_CONTEXT},  # Cached
        {"role": "user", "content": "Analyze this contract: ..."}  # Unique
    ]
)

# Anthropic: явный cache control
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are a code reviewer with extensive knowledge...",
            "cache_control": {"type": "ephemeral"}  # 5-min cache
        }
    ],
    messages=[{"role": "user", "content": "Review this code: ..."}]
)

# Проверяем cache hit
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")
```

### Semantic Caching

```python
# Кэширование на основе смысла, а не точного совпадения

import hashlib
from typing import Optional
import numpy as np
from openai import OpenAI

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.client = OpenAI()
        self.cache: dict[str, tuple[list[float], str]] = {}
        self.threshold = similarity_threshold

    def _get_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        a_np, b_np = np.array(a), np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))

    def get(self, query: str) -> Optional[str]:
        query_embedding = self._get_embedding(query)

        for cached_query, (embedding, response) in self.cache.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity >= self.threshold:
                print(f"Cache hit! Similarity: {similarity:.3f}")
                return response

        return None

    def set(self, query: str, response: str):
        embedding = self._get_embedding(query)
        self.cache[query] = (embedding, response)

# Использование
cache = SemanticCache(similarity_threshold=0.92)

# Первый запрос
query = "What is machine learning?"
cached = cache.get(query)
if not cached:
    response = call_llm(query)
    cache.set(query, response)

# Похожий запрос — cache hit
query2 = "Explain what machine learning is"
cached = cache.get(query2)  # Hit! Семантически похоже
```

### Model Routing / Cascading

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class ModelConfig:
    name: str
    cost_per_1k_tokens: float
    max_complexity: str  # "low", "medium", "high"

MODELS = {
    "cheap": ModelConfig("gpt-4o-mini", 0.15, "low"),
    "standard": ModelConfig("gpt-4o", 2.50, "medium"),
    "premium": ModelConfig("claude-opus-4", 15.00, "high")
}

def estimate_complexity(prompt: str) -> str:
    """Оценка сложности запроса"""
    # Эвристики или классификатор
    word_count = len(prompt.split())

    if "explain" in prompt.lower() or "summarize" in prompt.lower():
        return "low"
    elif "analyze" in prompt.lower() or "compare" in prompt.lower():
        return "medium"
    elif "reason" in prompt.lower() or "prove" in prompt.lower():
        return "high"

    return "medium" if word_count > 100 else "low"

def route_to_model(prompt: str) -> str:
    """Роутинг к подходящей модели по сложности"""
    complexity = estimate_complexity(prompt)

    if complexity == "low":
        return MODELS["cheap"].name
    elif complexity == "medium":
        return MODELS["standard"].name
    else:
        return MODELS["premium"].name

# Использование
model = route_to_model("Summarize this article...")  # -> gpt-4o-mini
model = route_to_model("Analyze the philosophical implications...")  # -> gpt-4o
```

### Batch API

```python
from openai import OpenAI
import json
import time

client = OpenAI()

# 1. Подготовка batch file
requests = [
    {
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": f"Summarize article {i}"}],
            "max_tokens": 100
        }
    }
    for i in range(100)
]

# Сохраняем в JSONL
with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# 2. Загружаем файл
batch_file = client.files.create(
    file=open("batch_input.jsonl", "rb"),
    purpose="batch"
)

# 3. Создаём batch job
batch_job = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"  # До 24 часов, 50% скидка
)

# 4. Проверяем статус
while True:
    status = client.batches.retrieve(batch_job.id)
    print(f"Status: {status.status}")

    if status.status == "completed":
        # Скачиваем результаты
        output_file = client.files.content(status.output_file_id)
        results = [json.loads(line) for line in output_file.text.split("\n") if line]
        break
    elif status.status == "failed":
        print(f"Failed: {status.errors}")
        break

    time.sleep(60)
```

---

## 7. Production Checklist

```
+----------------------------------------------------------------------------+
|                    Production LLM Integration Checklist                     |
+----------------------------------------------------------------------------+
|                                                                            |
|  БЕЗОПАСНОСТЬ:                                                             |
|  [ ] API keys в environment variables или secrets manager                 |
|  [ ] Никогда не логировать API keys                                       |
|  [ ] Rate limiting на уровне приложения                                   |
|  [ ] Input validation (длина, формат)                                     |
|  [ ] Output sanitization (XSS, injection)                                 |
|                                                                            |
|  НАДЕЖНОСТЬ:                                                               |
|  [ ] Exponential backoff с jitter                                         |
|  [ ] Retry-After header handling                                          |
|  [ ] Circuit breaker для fallback                                         |
|  [ ] Timeout на все запросы                                               |
|  [ ] Graceful degradation (fallback responses)                            |
|                                                                            |
|  OBSERVABILITY:                                                            |
|  [ ] Логирование request/response (без sensitive data)                    |
|  [ ] Метрики: latency, tokens, cost, errors                               |
|  [ ] Tracing (LangSmith, Langfuse, etc.)                                  |
|  [ ] Alerting на error rate spikes                                        |
|                                                                            |
|  COST CONTROL:                                                             |
|  [ ] Budget limits per user/team                                          |
|  [ ] Prompt caching enabled                                               |
|  [ ] Model routing по сложности                                           |
|  [ ] Token limits на запросы                                              |
|  [ ] Cost tracking и dashboards                                           |
|                                                                            |
|  UX:                                                                       |
|  [ ] Streaming для всех chat interfaces                                   |
|  [ ] Loading states                                                       |
|  [ ] Error messages для пользователей                                     |
|  [ ] Cancellation support                                                  |
|                                                                            |
+----------------------------------------------------------------------------+
```
---

## Проверь себя

> [!question]- Почему LiteLLM предпочтительнее прямых SDK для production-приложений с несколькими LLM провайдерами?
> LiteLLM предоставляет единый OpenAI-совместимый интерфейс для 100+ провайдеров, автоматический fallback при сбоях, встроенный cost tracking, load balancing и Redis-кэширование. Один код работает с любым провайдером, что устраняет vendor lock-in и упрощает миграцию.

> [!question]- Ваш LLM-сервис получает 429 (Rate Limit) ошибки от OpenAI. Какую стратегию retry реализуете и почему именно её?
> Exponential backoff с jitter: начать с 1 секунды, удваивать до max 60 секунд, добавить random jitter для предотвращения thundering herd. Обязательно проверять Retry-After header. Дополнительно -- circuit breaker pattern с fallback на альтернативного провайдера (Anthropic).

> [!question]- Как prompt caching может сэкономить до 90% затрат на API?
> Статический контент (system prompt, документы) помещается в начало запроса. OpenAI автоматически кэширует промпты > 1024 токенов, Anthropic -- через cache_control. При повторных запросах cached tokens стоят на 50-90% дешевле. Для RAG с одним system prompt и разными вопросами -- огромная экономия.

> [!question]- В чем разница между Structured Outputs OpenAI и Tool Use Anthropic для получения JSON?
> OpenAI Structured Outputs через Pydantic-модели гарантируют 100% compliance с JSON schema -- модель физически не может вернуть невалидный JSON. Tool Use у Anthropic использует input_schema и tool_use/tool_result цикл, где модель решает какой инструмент вызвать. Structured Outputs -- для гарантированного формата, Tool Use -- для вызова внешних функций.

---

## Ключевые карточки

Какие три SDK для основных LLM провайдеров?
?
OpenAI: `openai` (pip install openai>=1.0.0). Anthropic: `anthropic` (pip install anthropic>=0.25.0). Google Gemini: `google-genai` (pip install google-genai>=1.0.0). Все поддерживают sync и async, streaming, tool use.

Что такое Circuit Breaker pattern для LLM?
?
Паттерн защиты от каскадных сбоев. Три состояния: closed (нормальная работа), open (запросы блокируются после N ошибок), half-open (пробный запрос после timeout). Позволяет fallback на альтернативного провайдера при сбое основного.

Как работает Batch API и какую экономию дает?
?
Batch API позволяет отправить до сотен запросов в JSONL файле для асинхронной обработки за 24 часа. Экономия 50% от стандартной цены. Подходит для background processing, когда мгновенный ответ не нужен.

Что такое Semantic Caching?
?
Кэширование на основе смысла запроса, а не точного совпадения строк. Используются embeddings для вычисления cosine similarity между запросами. При similarity > threshold (обычно 0.92-0.95) возвращается кэшированный ответ. Снижение costs до 86%, latency до 88%.

Как работает model routing для оптимизации затрат?
?
Классификация сложности запроса и маршрутизация к подходящей модели. Простые задачи -> GPT-4o mini ($0.15/1M), средние -> GPT-4o ($2.50/1M), сложные -> Claude Opus ($15/1M). Экономия до 63% через cascading.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[structured-outputs-tools]] | Глубокое погружение в JSON mode, function calling и tool use |
| Углубиться | [[ai-cost-optimization]] | Полное руководство по оптимизации затрат на LLM API |
| Смежная тема | [[api-design]] | REST API паттерны, применимые к LLM-интеграции |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
