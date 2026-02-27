---
title: "Structured Outputs и Tool Use: От хаоса к порядку"
created: 2025-12-24
updated: 2026-02-13
author: AI Assistant
reading_time: 109
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
level: intermediate
type: guide
topics:
  - structured-outputs
  - function-calling
  - tool-use
  - JSON
  - Pydantic
  - Instructor
  - Outlines
  - constrained-decoding
status: published
tags:
  - topic/ai-ml
  - type/guide
  - level/intermediate
related:
  - "[[ai-api-integration]]"
  - "[[mcp-model-context-protocol]]"
  - "[[type-systems-theory]]"
---

# Structured Outputs и Tool Use: От хаоса к порядку

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Как работает генерация текста | [[llm-fundamentals]] |
| **JSON** | Формат структурированных данных | Базовое программирование |
| **Python + Pydantic** | Примеры кода, валидация схем | Python docs, Pydantic docs |
| **REST API** | Интеграция через API | [[ai-api-integration]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в программировании** | ❌ Нет | Сначала Python + JSON |
| **Бэкенд разработчик** | ✅ Да | Идеально — сразу применимо в production |
| **Data Engineer** | ✅ Да | Structured extraction из текста |
| **AI Engineer** | ✅ Да | Интеграция LLM в пайплайны |

### Терминология для новичков

> 💡 **Structured Output** = LLM возвращает данные в строгом формате (JSON), а не свободный текст

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Structured Output** | Гарантированный JSON вместо текста | **Анкета с полями** — заполни форму, а не пиши эссе |
| **JSON Schema** | Описание структуры данных | **Шаблон анкеты** — какие поля, какой тип |
| **Pydantic** | Python-библиотека для валидации | **Строгий секретарь** — проверит, что все поля заполнены правильно |
| **Function Calling** | LLM вызывает внешние функции | **Помощник с телефоном** — может позвонить и узнать информацию |
| **Tool Use** | Более общее название для Function Calling | **Набор инструментов** — калькулятор, поиск, база данных |
| **Constrained Decoding** | Ограничение генерации на уровне токенов | **Клавиатура с блокировкой** — невозможно нажать "неправильную" кнопку |
| **Response Format** | Параметр API для указания формата | **Выбор формы ответа** — текст, JSON, или по схеме |

---

## Теоретические основы

> **Structured Output** — преобразование неструктурированного выхода языковой модели в формально верифицируемую структуру данных, соответствующую заданной схеме (JSON Schema, Pydantic model, XML DTD). Это частный случай задачи **information extraction** в NLP.

Проблема формализации выхода генеративных моделей имеет глубокие корни в теории формальных языков. Хомский (1956) классифицировал формальные грамматики по иерархии сложности. Естественный язык относится к контекстно-зависимым грамматикам (Type 1), тогда как JSON — к контекстно-свободным (Type 2). **Constrained decoding** ограничивает генерацию модели подмножеством токенов, допустимых грамматикой целевого формата.

| Подход | Год | Механизм | Гарантия формата | Ограничения |
|--------|-----|----------|------------------|-------------|
| Prompt engineering | 2022 | Инструкция в промпте | ~35-40% | Модель может игнорировать |
| JSON Mode | 2023 | Fine-tuning + post-processing | ~90% | Нет гарантии соответствия схеме |
| Function Calling | 2023 | Специальные токены + training | ~95% | Ограниченные типы данных |
| **Constrained Decoding** | 2024 | **Маскирование токенов при sampling** | **100%** | Замедление генерации, ограничения грамматики |

> **Constrained Decoding** формально: на шаге $t$ вместо sampling из полного словаря $V$ модель выбирает из подмножества $V_t \subseteq V$, определяемого текущим состоянием конечного автомата, соответствующего целевой грамматике. Willard & Louf (2023), *Efficient Guided Generation for LLMs*. arXiv:2307.09702.

**Ключевые теоретические результаты:**

- **Context-Free Grammar (CFG) Guidance** — Scholak et al. (2021) показали, что constrained decoding с CFG не снижает качество генерации при правильном дизайне грамматики
- **XGrammar** — Dong et al. (2024) достигли 100x ускорения constrained decoding через предварительную компиляцию грамматик в pushdown automata. arXiv:2411.15100
- **Format ≠ Correctness** — Boundary ML (2024) продемонстрировали, что 100% JSON compliance не гарантирует семантическую корректность: модель может вернуть валидный JSON с неверными данными

Связь с [[type-systems-theory|теорией типов]]: JSON Schema и Pydantic-модели — это системы типов для runtime-валидации. Structured outputs реализуют принцип **"well-typed programs don't go wrong"** (Milner, 1978) в контексте LLM-генерации: если схема определена корректно, выход модели гарантированно соответствует ожидаемому типу.

См. также: [[ai-api-integration|API интеграция]] — практические аспекты structured outputs в API, [[mcp-model-context-protocol|MCP]] — стандартизация tool use.

---

## Введение: Почему это важно

Представь, что ты строишь production систему. Твой бэкенд ожидает JSON с полями `name`, `price`, `currency`. Ты отправляешь запрос к LLM: "Извлеки информацию о продукте из текста: iPhone 15 Pro стоит $999".

И получаешь ответ:

```
Конечно! Вот информация о продукте:
- Название: iPhone 15 Pro
- Цена: 999 долларов США
- Валюта: USD

Надеюсь, это поможет!
```

Как ты это распарсишь? Regex? А если в следующий раз модель ответит иначе? А если добавит эмодзи? А если перепутает порядок полей?

**Это фундаментальная проблема интеграции LLM в production системы** — языковые модели созданы для генерации естественного текста, а не машиночитаемых структур.

> По данным OpenAI, до появления Structured Outputs надёжность получения правильного формата через prompt engineering составляла ~35.9%. С включённым `strict: true` эта надёжность достигает **100%**.

В этом руководстве мы разберём:
1. Эволюцию решений: от хаков до native поддержки
2. Structured Outputs: как заставить LLM возвращать гарантированный JSON
3. Tool Use: как дать LLM "руки" для взаимодействия с внешним миром
4. Библиотеки и фреймворки: Instructor, Outlines, Pydantic AI, BAML, Guidance
5. Практические паттерны и типичные ошибки

---

## Оглавление

1. [Проблема: Почему LLM возвращает "что попало"](#проблема-почему-llm-возвращает-что-попало)
2. [Эволюция решений](#эволюция-решений)
3. [Structured Outputs: Глубокое погружение](#structured-outputs-глубокое-погружение)
4. [Tool Use: Руки для LLM](#tool-use-руки-для-llm)
5. [Constrained Decoding: Как это работает под капотом](#constrained-decoding-как-это-работает-под-капотом)
6. [Библиотеки и фреймворки](#библиотеки-и-фреймворки)
7. [Практическая реализация](#практическая-реализация)
8. [Типичные ошибки и как их избежать](#типичные-ошибки-и-как-их-избежать)
9. [Best Practices](#best-practices)
10. [Проверь себя](#проверь-себя)

---

## Проблема: Почему LLM возвращает "что попало"

### Как устроена генерация текста

Чтобы понять проблему, нужно понять как LLM генерирует текст. Это не "умная база данных", которая достаёт готовые ответы. Это **вероятностная машина**, которая предсказывает следующий токен.

```
Входной текст: "Столица Франции —"

LLM вычисляет вероятности следующего токена:
  "Париж"  → 0.85
  "город"  → 0.08
  "это"    → 0.03
  ...      → остальные

Выбирается токен с учётом temperature:
  temperature=0: всегда "Париж" (самый вероятный)
  temperature=1: случайный выбор по распределению
```

**Ключевой инсайт**: LLM не "знает", что тебе нужен JSON. Она просто предсказывает, какой текст наиболее вероятно следует за твоим промптом. Если в training data после подобных запросов чаще шёл prose text — она выдаст prose text.

### Почему это создаёт проблемы

```
Один и тот же запрос → Разные форматы ответа:

Запрос: "Извлеки имя и возраст: Джону 30 лет"

Ответ 1: "Имя: Джон, Возраст: 30"
Ответ 2: "{"name": "Джон", "age": 30}"
Ответ 3: "Джон (30 лет)"
Ответ 4: "Из текста можно извлечь: имя человека — Джон, его возраст — 30 лет."
Ответ 5: "{name: 'Джон', age: 30}"  ← Невалидный JSON!
```

**Проблемы для production:**
- **Непредсказуемость**: каждый запрос может дать разный формат
- **Хрупкость парсинга**: regex ломается на edge cases
- **Невалидный синтаксис**: JSON без кавычек, лишние запятые
- **Отсутствующие поля**: модель может "забыть" вернуть обязательное поле
- **Дополнительный текст**: "Вот ваш JSON: {...}" — как отделить JSON от текста?

---

## Эволюция решений

Индустрия прошла долгий путь от костылей к элегантным решениям. Понимание этой эволюции поможет тебе выбрать правильный подход.

### Этап 1: Prompt Engineering (2020-2022)

**Идея**: Если хорошо попросить — модель послушается.

```python
prompt = """
Извлеки информацию из текста и верни ТОЛЬКО валидный JSON.
Никакого дополнительного текста. Только JSON.

Формат:
{"name": "string", "price": number, "currency": "string"}

Текст: iPhone 15 Pro стоит $999

JSON:
"""

response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt
)

# Надеемся, что получим JSON...
try:
    data = json.loads(response.choices[0].text)
except json.JSONDecodeError:
    # Упс. Примерно в 10-20% случаев
    # модель добавит "Вот ваш JSON:" или сломает синтаксис
    pass
```

**Почему это работает (иногда)**:
- Модели обучены следовать инструкциям
- Чём чётче инструкция, тем выше вероятность соблюдения
- Few-shot примеры повышают success rate

**Почему это НЕ работает (часто)**:
- Нет гарантий — это всё ещё вероятностная генерация
- Длинные контексты "размывают" инструкции
- Сложные схемы увеличивают вероятность ошибки
- Temperature > 0 добавляет случайность

**Success rate**: ~80-90% для простых случаев, падает с ростом сложности.

### Этап 2: Regex Post-Processing (2021-2023)

**Идея**: Если модель возвращает мусор вокруг JSON — вырежем его.

```python
import re
import json

def extract_json_from_response(text: str) -> dict | None:
    """
    Пытаемся найти JSON в ответе модели.

    Типичные проблемы, которые решает эта функция:
    - "Вот ваш JSON: {...}"
    - "```json\n{...}\n```"
    - "{...}\n\nНадеюсь, это помогло!"
    """

    # Паттерн 1: JSON в markdown code block
    code_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
    match = re.search(code_block_pattern, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Паттерн 2: Просто найти {...}
    json_pattern = r'\{[^{}]*\}'
    match = re.search(json_pattern, text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Паттерн 3: Вложенные объекты (рекурсивный regex)
    # Это уже становится безумием...

    return None

# Использование
raw_response = """
Конечно! Вот извлечённая информация:

```json
{"name": "iPhone 15 Pro", "price": 999, "currency": "USD"}
```

Дайте знать, если нужно что-то ещё!
"""

data = extract_json_from_response(raw_response)
```

**Почему это работает**:
- Повышает success rate до ~95%
- Простая идея, легко реализовать

**Почему это ПЛОХО**:
- **Хрупкость**: Новый формат ответа — новый regex
- **Невалидный JSON**: Regex не исправит `{name: 'test'}` (нужны двойные кавычки)
- **Вложенные структуры**: Regex не предназначен для парсинга рекурсивных структур
- **Отсутствующие поля**: Regex не проверит, что все required поля присутствуют
- **Типы данных**: `"price": "999"` vs `"price": 999` — regex не различит

**Success rate**: ~90-95%, но без гарантий валидности схемы.

### Этап 3: JSON Mode (2023)

**Идея**: Пусть провайдер гарантирует хотя бы валидный синтаксис JSON.

OpenAI представил `response_format: {"type": "json_object"}` в ноябре 2023.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "system",
            "content": "Ты извлекаешь информацию о продуктах. Возвращай JSON с полями: name, price, currency."
        },
        {
            "role": "user",
            "content": "iPhone 15 Pro стоит $999"
        }
    ],
    response_format={"type": "json_object"}  # Магия здесь!
)

# Гарантированно валидный JSON (синтаксически)
data = json.loads(response.choices[0].message.content)

# НО! Схема не гарантирована:
# Может вернуть {"product": "iPhone", "cost": 999}
# вместо {"name": "iPhone", "price": 999, "currency": "USD"}
```

**Как это работает под капотом**:

JSON Mode использует **constrained decoding** — ограничение множества допустимых токенов на каждом шаге генерации:

```
Обычная генерация:
  После "{" допустимы 50,000+ токенов

JSON Mode:
  После "{" допустимы только:
    - '"' (начало ключа)
    - '}' (пустой объект)
    - whitespace

  После '{"name": "iPhone' допустимы:
    - любой текстовый токен (продолжение строки)
    - '"' (конец строки)
```

**Почему это прорыв**:
- **100% валидный JSON синтаксис** — невозможно получить `{name: value}` или незакрытые скобки
- Нативная поддержка на уровне inference engine
- Минимальный overhead по latency

**Почему этого недостаточно**:
- Нет гарантии соответствия конкретной схеме
- Поля могут быть named по-другому
- Типы могут не совпадать
- Required поля могут отсутствовать

**Success rate**: 100% для валидного JSON, ~90-95% для соответствия нужной схеме.

### Этап 4: Structured Outputs (2024-2025)

**Идея**: Constrained decoding, но с учётом JSON Schema.

OpenAI представил Structured Outputs в августе 2024. Anthropic добавил аналогичную функциональность в ноябре 2025 (beta). Это **game changer**.

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# Определяем точную схему через Pydantic
class Product(BaseModel):
    name: str
    price: float
    currency: str

# API гарантирует соответствие схеме
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "user", "content": "iPhone 15 Pro стоит $999"}
    ],
    response_format=Product
)

# Гарантированно:
# 1. Валидный JSON
# 2. Все поля присутствуют
# 3. Типы соответствуют схеме
product = response.choices[0].message.parsed
print(product.name)      # str, всегда
print(product.price)     # float, всегда
print(product.currency)  # str, всегда
```

**Это революция, потому что**:
- **100% соответствие схеме** — математически гарантировано
- Все required поля присутствуют
- Типы точно соответствуют
- Enum значения только из списка
- Вложенные объекты корректны

**Поддержка по провайдерам (декабрь 2025):**

| Провайдер | Модели | Механизм |
|-----------|--------|----------|
| OpenAI | gpt-4o, gpt-4o-mini, o1, o3 | Native `strict: true` |
| Anthropic | Claude Sonnet 4.5, Opus 4.1 | Beta `structured-outputs-2025-11-13` |
| Google | Gemini 2.0, 2.5 | `response_mime_type` + `response_schema` |
| Cohere | Command R, Command A | JSON Schema mode |
| vLLM/SGLang | Любые модели | XGrammar, Outlines backends |

**Success rate**: 100%.

### Сравнительная таблица

| Подход | Валидный JSON | Соответствие схеме | Гарантии | Сложность |
|--------|--------------|-------------------|----------|-----------|
| Prompt Engineering | ~85% | ~75% | Нет | Низкая |
| Regex Extraction | ~95% | ~85% | Нет | Средняя |
| JSON Mode | 100% | ~92% | Только синтаксис | Низкая |
| Structured Outputs | 100% | 100% | Полные | Низкая |
| Instructor + Retries | ~100% | ~99% | Почти полные | Низкая |

---

## Structured Outputs: Глубокое погружение

### Механизм: Constrained Decoding

Чтобы по-настоящему понять Structured Outputs, разберём как работает constrained decoding с конкретным примером.

**Схема:**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "pending"]
    },
    "count": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": ["status", "count"]
}
```

**Генерация шаг за шагом:**

```
Шаг 1: Начало объекта
  Допустимые токены: ["{"]
  Выбрано: "{"
  Текущий output: "{"

Шаг 2: Первый ключ (required: status или count)
  Допустимые токены: ["\"status\"", "\"count\""]
  Выбрано: "\"status\""
  Текущий output: "{\"status\""

Шаг 3: Разделитель
  Допустимые токены: [":"]
  Выбрано: ":"
  Текущий output: "{\"status\":"

Шаг 4: Значение для status (enum)
  Допустимые токены: ["\"active\"", "\"inactive\"", "\"pending\""]
  Модель "хочет" сказать "active" → Выбрано: "\"active\""
  Текущий output: "{\"status\":\"active\""

Шаг 5: Разделитель или продолжение
  Допустимые токены: [","]  (count ещё required)
  Выбрано: ","
  Текущий output: "{\"status\":\"active\","

Шаг 6: Второй ключ (осталось: count)
  Допустимые токены: ["\"count\""]
  Выбрано: "\"count\""
  Текущий output: "{\"status\":\"active\",\"count\""

Шаг 7: Разделитель и значение
  Допустимые токены: [":"] затем [цифры 0-9]
  ...

Шаг 8: Закрытие объекта
  Допустимые токены: ["}"]
  Текущий output: "{\"status\":\"active\",\"count\":42}"
```

**Ключевой инсайт**: На каждом шаге модель всё ещё выбирает токены на основе своих предсказаний, но выбор ограничен только теми токенами, которые ведут к валидному JSON по схеме. Это как писать текст, имея только нужные буквы на клавиатуре.

### OpenAI: Два способа использования

#### Способ 1: response_format с json_schema

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "user", "content": "Solve 8x + 7 = -23"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "math_reasoning",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": {"type": "string"},
                                "output": {"type": "string"}
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                        }
                    },
                    "final_answer": {"type": "string"}
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": False
            },
            "strict": True  # <-- Ключевой параметр!
        }
    }
)
```

#### Способ 2: Pydantic model через SDK

```python
from openai import OpenAI
from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()

# SDK автоматически конвертирует Pydantic → JSON Schema
response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Solve 8x + 7 = -23"}
    ],
    response_format=MathReasoning
)

# Прямой доступ к parsed объекту
reasoning = response.choices[0].message.parsed
print(reasoning.final_answer)  # "-3.75"
```

### Anthropic: Tool Use для Structured Outputs (2025 Beta)

Anthropic добавил нативные structured outputs в ноябре 2025:

```python
from pydantic import BaseModel
from anthropic import Anthropic

class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str

client = Anthropic()

# Новый метод parse() с beta header
response = client.beta.messages.parse(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    betas=["structured-outputs-2025-11-13"],  # Beta feature
    messages=[
        {"role": "user", "content": "Extract info: John Smith, john@email.com, interested in Pro plan"}
    ],
    output_format=ContactInfo,
)

contact = response.parsed_output
print(contact.name)  # "John Smith"
```

**Альтернативный подход через Tool Use:**

```python
from pydantic import BaseModel, Field
from typing import List
from anthropic import Anthropic

class TextAnalysis(BaseModel):
    sentiment: str = Field(description="Overall sentiment of the text")
    main_topics: List[str] = Field(description="List of main topics")
    word_count: int = Field(description="Total word count")

client = Anthropic()

# Генерируем JSON Schema из Pydantic модели
text_analysis_schema = TextAnalysis.model_json_schema()

tools = [
    {
        "name": "build_text_analysis_result",
        "description": "Build the text analysis object with extracted information",
        "input_schema": text_analysis_schema
    }
]

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1200,
    tools=tools,
    # Заставляем Claude использовать именно этот tool
    tool_choice={"type": "tool", "name": "build_text_analysis_result"},
    messages=[
        {"role": "user", "content": "Analyze this text: ..."}
    ]
)

# Извлекаем structured data из tool call
for block in message.content:
    if block.type == "tool_use":
        analysis = TextAnalysis(**block.input)
        print(analysis.sentiment)
```

### Google Gemini: JSON Schema Support

```python
import google.generativeai as genai
from typing import TypedDict

class Product(TypedDict):
    name: str
    price: float
    currency: str

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content(
    "Extract: iPhone 15 Pro costs $999",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": Product
    }
)

import json
product = json.loads(response.text)
```

> **Важно**: В ноябре 2025 Google добавил поддержку JSON Schema keywords `anyOf`, `$ref` и сохранение порядка ключей для Gemini 2.5 моделей.

### JSON Schema: Что поддерживается

OpenAI Structured Outputs поддерживает подмножество JSON Schema:

**Полностью поддерживается:**
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"  # default значения

class Person(BaseModel):
    # Примитивные типы
    name: str
    age: int
    score: float
    is_active: bool

    # Optional (nullable)
    nickname: Optional[str] = None

    # Enum через Literal
    role: Literal["admin", "user", "guest"]

    # Enum через Enum class
    status: Status

    # Массивы
    tags: List[str]

    # Вложенные объекты
    address: Address

    # Массив объектов
    friends: List["Person"] = []

    # Field с описанием (помогает модели понять контекст)
    bio: str = Field(description="Краткая биография пользователя")
```

**НЕ поддерживается (пока):**
```python
# Нельзя использовать:
from typing import Union, Any, Dict

class Invalid(BaseModel):
    # Union types (кроме Optional)
    value: Union[str, int]  # Ошибка!

    # Any type
    data: Any  # Ошибка!

    # Произвольные dict
    metadata: Dict[str, Any]  # Ошибка!

    # Рекурсивные ссылки (ограничено)
    # Работает для простых случаев, но не для глубокой рекурсии
```

---

## Tool Use: Руки для LLM

### Концепция: Зачем LLM нужны "руки"

LLM — это мозг. Очень умный мозг, который может анализировать, рассуждать, генерировать текст. Но у него нет возможности **действовать** в реальном мире.

Представь: ты спрашиваешь LLM "Какая сейчас погода в Москве?". Что она может ответить?

```
Без tools:
"Я не имею доступа к актуальным данным о погоде, так как мои знания
ограничены датой обучения. Рекомендую проверить погоду на weather.com."

С tools:
1. LLM понимает, что нужны актуальные данные
2. LLM решает вызвать функцию get_weather(city="Moscow")
3. Твой код выполняет реальный API запрос
4. LLM получает результат: {"temp": -5, "condition": "snow"}
5. LLM отвечает: "Сейчас в Москве -5°C, идёт снег."
```

**Tools = руки для LLM**. Это способ подключить языковую модель к внешнему миру:
- API запросы (погода, новости, курсы валют)
- Базы данных (поиск, CRUD операции)
- Файловая система (чтение, запись)
- Другие сервисы (email, Slack, календарь)
- Вычисления (калькулятор, code interpreter)

### Архитектура: Как это работает

```
┌──────────────────────────────────────────────────────────────────────┐
│                        TOOL USE ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────┐                                                     │
│   │    User     │                                                     │
│   │   Prompt    │                                                     │
│   └──────┬──────┘                                                     │
│          │                                                            │
│          ▼                                                            │
│   ┌──────────────┐      ┌─────────────────┐                          │
│   │    Your      │      │  Tool Schemas   │                          │
│   │    Code      │─────▶│  (JSON Schema)  │                          │
│   └──────┬───────┘      └─────────────────┘                          │
│          │                      │                                     │
│          │                      ▼                                     │
│          │              ┌───────────────┐                            │
│          │              │      LLM      │                            │
│          │              │  (Анализ +    │                            │
│          │              │   Решение)    │                            │
│          │              └───────┬───────┘                            │
│          │                      │                                     │
│          │         Два возможных пути:                               │
│          │         ┌────────────┴────────────┐                       │
│          │         ▼                         ▼                        │
│          │   ┌──────────┐            ┌─────────────┐                 │
│          │   │  Text    │            │  Tool Call  │                 │
│          │   │ Response │            │  Request    │                 │
│          │   └────┬─────┘            └──────┬──────┘                 │
│          │        │                         │                         │
│          │        ▼                         ▼                         │
│          │   ┌──────────┐            ┌─────────────┐                 │
│          │   │  Return  │            │ Your Code   │                 │
│          │   │  to User │            │ Executes    │◀─── ЭТО ВАЖНО! │
│          │   └──────────┘            │ Function    │     LLM не     │
│          │                           └──────┬──────┘     выполняет   │
│          │                                  │            функцию     │
│          │                                  ▼                         │
│          │                           ┌─────────────┐                 │
│          │                           │   Result    │                 │
│          │                           └──────┬──────┘                 │
│          │                                  │                         │
│          │◀─────────────────────────────────┘                        │
│          │                                                            │
│          │  Результат отправляется обратно в LLM                     │
│          ▼                                                            │
│   ┌──────────────┐                                                   │
│   │     LLM      │                                                   │
│   │  Формирует   │                                                   │
│   │   ответ      │                                                   │
│   └──────┬───────┘                                                   │
│          │                                                            │
│          ▼                                                            │
│   ┌──────────────┐                                                   │
│   │   Final      │                                                   │
│   │   Response   │                                                   │
│   └──────────────┘                                                   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Критически важно понимать**: LLM **НЕ ВЫПОЛНЯЕТ** функции. LLM только:
1. Анализирует запрос пользователя
2. Решает, какая функция нужна
3. Генерирует аргументы для этой функции
4. Возвращает структурированный "запрос на вызов"

**Твой код** отвечает за:
1. Получение tool_call от LLM
2. Валидацию аргументов (security!)
3. Выполнение реальной функции
4. Отправку результата обратно LLM

### Анатомия Tool Definition

```python
# Tool — это JSON Schema, описывающая функцию

tool_definition = {
    # Тип tool (пока только "function")
    "type": "function",

    "function": {
        # Имя функции — LLM будет использовать его для вызова
        # Лучше: глагол + существительное (search_products, get_weather)
        "name": "search_products",

        # Описание — КРИТИЧЕСКИ ВАЖНО!
        # LLM использует его для понимания, когда вызывать функцию
        # Чем лучше описание, тем точнее выбор функции
        "description": """
        Поиск продуктов в каталоге по названию, категории или ценовому диапазону.

        Используй эту функцию когда:
        - Пользователь ищет конкретный продукт
        - Нужно найти продукты в категории
        - Пользователь указывает бюджет

        НЕ используй для:
        - Получения деталей одного продукта (используй get_product_details)
        - Оформления заказа (используй create_order)
        """,

        # strict: true — гарантирует соответствие схеме (OpenAI)
        "strict": True,

        # Параметры функции как JSON Schema
        "parameters": {
            "type": "object",

            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос (название продукта или ключевые слова)"
                },

                "category": {
                    "type": "string",
                    # Enum ограничивает выбор
                    "enum": ["electronics", "clothing", "books", "home"],
                    "description": "Категория для фильтрации"
                },

                "min_price": {
                    "type": "number",
                    "description": "Минимальная цена в USD"
                },

                "max_price": {
                    "type": "number",
                    "description": "Максимальная цена в USD"
                },

                "in_stock_only": {
                    "type": "boolean",
                    "description": "Показывать только товары в наличии",
                    # Default можно указать в description
                    "default": True
                }
            },

            # Required поля — LLM обязана их заполнить
            "required": ["query"],

            # additionalProperties: false — запрещает лишние поля
            # Обязательно для strict mode!
            "additionalProperties": False
        }
    }
}
```

### Parallel Tool Calls: Эффективность

LLM может вернуть несколько tool calls за один запрос. Это мощный паттерн для оптимизации.

```
User: "Сравни погоду в Москве и Париже, и курс евро к рублю"

Без parallel calls:
  Request 1 → get_weather("Moscow")   → Response 1
  Request 2 → get_weather("Paris")    → Response 2
  Request 3 → get_exchange_rate()     → Response 3
  Request 4 → Final response

  Итого: 4 API calls, ~8 секунд

С parallel calls:
  Request 1 → [
    get_weather("Moscow"),
    get_weather("Paris"),
    get_exchange_rate()
  ]

  Твой код выполняет ВСЕ ТРИ параллельно (asyncio, threading)

  Request 2 → Final response (с тремя результатами)

  Итого: 2 API calls, ~3 секунды
```

**Реализация parallel execution:**

```python
import asyncio
from typing import List, Dict, Any

async def execute_tool(name: str, args: dict) -> dict:
    """Выполнение одного tool call"""
    if name == "get_weather":
        return await weather_api.get(args["city"])
    elif name == "get_exchange_rate":
        return await forex_api.get(args["from"], args["to"])
    # ... другие tools

async def execute_tools_parallel(tool_calls: List[dict]) -> List[dict]:
    """
    Параллельное выполнение нескольких tool calls.

    Критически важно:
    1. Все вызовы независимы друг от друга
    2. Результаты возвращаются в том же порядке
    3. Каждый результат связан с tool_call_id
    """
    tasks = [
        execute_tool(tc["function"]["name"], tc["function"]["arguments"])
        for tc in tool_calls
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        {
            "tool_call_id": tc["id"],
            "result": result if not isinstance(result, Exception) else {"error": str(result)}
        }
        for tc, result in zip(tool_calls, results)
    ]
```

---

## Constrained Decoding: Как это работает под капотом

### Finite State Machine (FSM) подход

Constrained decoding для structured outputs работает через формализм конечных автоматов. JSON Schema трансформируется в FSM, который отслеживает состояние генерации:

```
JSON Schema → Regular Expression → Finite State Machine

Пример для enum ["active", "inactive"]:

     ┌───────────────────────────────────────┐
     │                                       │
     │    ┌──┐  'a'   ┌──┐  'c'   ┌──┐      │
     ├───▶│S1│───────▶│S2│───────▶│S3│ ...  │
     │    └──┘        └──┘        └──┘      │
     │                                       │
     │    ┌──┐  'i'   ┌──┐  'n'   ┌──┐      │
     └───▶│S4│───────▶│S5│───────▶│S6│ ...  │
          └──┘        └──┘        └──┘
```

На каждом шаге генерации:
1. Определяем текущее состояние FSM
2. Получаем множество допустимых переходов (токенов)
3. Применяем маску к logits (вероятностям токенов)
4. Модель выбирает токен только из допустимых

### Основные реализации

#### XGrammar (MLC-AI)

XGrammar — default backend для vLLM, SGLang, TensorRT-LLM с декабря 2024.

```python
# XGrammar поддерживает context-free grammars через pushdown automaton
# Это мощнее чем FSM — позволяет рекурсивные структуры

# Пример использования с vLLM
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct")

# JSON Schema constraint
sampling_params = SamplingParams(
    temperature=0.7,
    guided_decoding_backend="xgrammar",  # или "outlines"
    guided_json={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
)

output = llm.generate(["Extract: John is 30 years old"], sampling_params)
```

**Производительность XGrammar:**
- До **100x** ускорение по сравнению с предыдущими решениями
- До **3.5x** быстрее Outlines на JSON workloads
- До **10x** быстрее на CFG-guided generation
- Почти нулевой overhead в end-to-end LLM serving

#### Outlines (dottxt-ai)

Outlines — pioneer библиотека для constrained generation, основанная на FSM:

```python
from outlines import models, generate
from pydantic import BaseModel

# Загружаем модель
model = models.transformers("mistralai/Mistral-7B-v0.1")

# Определяем схему
class Character(BaseModel):
    name: str
    age: int
    occupation: str

# Генерация с гарантией соответствия схеме
generator = generate.json(model, Character)
result = generator("Create a character for a story:")
print(result)  # Character(name="...", age=..., occupation="...")
```

**Поддерживаемые форматы:**
- JSON Schema / Pydantic models
- Regular expressions
- Context-free grammars (EBNF)
- Простые типы (int, float, bool, datetime)
- Choices / Literals

```python
from outlines import generate

# Regex constraint
phone_generator = generate.regex(model, r"\d{3}-\d{3}-\d{4}")
phone = phone_generator("Generate a US phone number:")  # "555-123-4567"

# Choice constraint
sentiment = generate.choice(model, ["positive", "negative", "neutral"])
result = sentiment("The movie was great!")  # "positive"
```

#### LM Format Enforcer

LM Format Enforcer использует динамическую проверку constraint-ов вместо precomputation:

```python
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.vllm import build_vllm_logits_processor

# Создаём parser из JSON Schema
schema = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    }
}
parser = JsonSchemaParser(schema)

# Интегрируем с vLLM
logits_processor = build_vllm_logits_processor(parser)
```

**Ключевые особенности:**
- Гибкость: модель контролирует whitespace и порядок полей
- Поддержка schemaless JSON mode
- Интеграция с Transformers, vLLM, llama.cpp, ExLlamaV2

#### Microsoft Guidance (llguidance)

Microsoft Guidance позволяет смешивать generation и control flow:

```python
from guidance import models, gen

# Загружаем модель
lm = models.LlamaCpp("path/to/model.gguf")

# Программа с constraints
program = lm + f"""\
Extract information from the text.

Text: {text}

Name: {gen('name', stop='\n')}
Age: {gen('age', regex='[0-9]+')}
City: {gen('city', stop='\n')}
"""

print(program['name'], program['age'], program['city'])
```

**Преимущества:**
- **50% reduction** в runtime через оптимизацию KV-cache
- Python-native синтаксис с constraints
- Поддержка conditionals, loops, tool use в рамках одной генерации

---

## Библиотеки и фреймворки

### Instructor: Лидер рынка

**Instructor** — самая популярная Python библиотека для structured outputs (3M+ downloads/month, 11k+ stars).

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# Патчим клиент
client = instructor.from_openai(OpenAI())

class ReviewAnalysis(BaseModel):
    """Анализ отзыва о продукте."""
    sentiment: str = Field(description="positive, negative, or neutral")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    pros: List[str] = Field(description="List of positive aspects")
    cons: List[str] = Field(description="List of negative aspects")

# Одна строка для structured extraction
analysis = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Analyze this review: {review_text}"}
    ],
    response_model=ReviewAnalysis,
    max_retries=3  # Автоматические retry при validation errors
)

print(analysis.sentiment)  # Гарантированно валидный тип
```

**Ключевые features:**
- **15+ провайдеров**: OpenAI, Anthropic, Google, Mistral, Cohere, Ollama, etc.
- **Automatic retries**: При ошибках валидации
- **Streaming**: `create_partial()` для partial results
- **Hooks**: Мониторинг и logging

```python
# Hooks для observability
client.on("completion:kwargs", lambda **kw: print(f"Request: {kw}"))
client.on("completion:response", lambda r: print(f"Response: {r}"))
client.on("completion:error", lambda e: log_error(e))

# Streaming partial results
for partial in client.chat.completions.create_partial(
    model="gpt-4o",
    messages=[...],
    response_model=LargeModel
):
    # Получаем частично заполненную модель
    print(f"Progress: {partial}")
```

### Pydantic AI: От создателей Pydantic

**Pydantic AI** — agent framework от команды Pydantic, идеально интегрированный со structured outputs:

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    country: str
    population: int

# Agent с типизированным output
agent = Agent(
    'openai:gpt-4o',
    output_type=CityInfo,  # Structured output
    instructions="You are a geography expert."
)

result = agent.run_sync("Tell me about Tokyo")
print(result.output)  # CityInfo(name="Tokyo", country="Japan", population=...)
```

**Tool definitions через декораторы:**

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-sonnet-4-0')

@agent.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city.

    Args:
        city: The city name to look up weather for
    """
    # Docstring становится описанием для LLM
    return {"temp": 20, "condition": "sunny"}

result = agent.run_sync("What's the weather in Paris?")
```

**Преимущества:**
- Нативная интеграция с Pydantic
- Type-safe tools через декораторы
- Dependency injection
- Async support
- Observability через Logfire

### BAML (Boundary ML): Schema-Aligned Parsing

**BAML** использует альтернативный подход: вместо constrained decoding парсит "сломанный" JSON:

```baml
// schema.baml
function ExtractResume(resume_text: string) -> Resume {
  client GPT4
  prompt #"
    Extract information from the resume.

    Resume:
    {{ resume_text }}
  "#
}

class Resume {
  name string
  email string
  skills string[]
  experience Experience[]
}

class Experience {
  company string
  role string
  years int
}
```

```python
# Python usage
from baml_client import b

result = b.ExtractResume(resume_text="...")
print(result.name)
```

**Философия BAML:**
- Structured outputs могут снижать качество reasoning (модель фокусируется на формате)
- Лучше дать модели писать naturally, потом распарсить
- SAP (Schema-Aligned Parsing) умеет обрабатывать:
  - Markdown внутри JSON
  - Chain-of-thought перед ответом
  - Небольшие синтаксические ошибки

### LangChain: with_structured_output

LangChain предоставляет унифицированный API для structured outputs:

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Joke(BaseModel):
    setup: str
    punchline: str

llm = ChatOpenAI(model="gpt-4o")
structured_llm = llm.with_structured_output(Joke)

result = structured_llm.invoke("Tell me a joke about programming")
print(result.setup)     # str
print(result.punchline) # str
```

**Режимы работы:**
- `function_calling`: Использует tool calling API
- `json_mode`: JSON без strict schema
- `json_schema`: Strict schema (default для совместимых моделей)

```python
# Выбор режима
structured_llm = llm.with_structured_output(
    Joke,
    method="json_schema",  # или "function_calling", "json_mode"
    strict=True
)
```

### LlamaIndex: Structured Extraction

LlamaIndex предоставляет высокоуровневые абстракции для extraction:

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List

class ProductInfo(BaseModel):
    name: str
    price: float
    features: List[str]

# Создаём query engine с structured output
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(
    output_parser=PydanticOutputParser(ProductInfo)
)

result = query_engine.query("What are the main features of Product X?")
# result.response — это ProductInfo object
```

### Marvin: AI Functions

Marvin предоставляет декларативный подход к AI operations:

```python
import marvin

# Extraction
names = marvin.extract(
    "I met John and Sarah at the conference",
    target=str,
    instructions="Extract person names"
)
# ["John", "Sarah"]

# Classification
sentiment = marvin.classify(
    "This product is amazing!",
    labels=["positive", "negative", "neutral"]
)
# "positive"

# Cast (type conversion через LLM)
@marvin.fn
def analyze_sentiment(text: str) -> Literal["positive", "negative", "neutral"]:
    """Analyze the sentiment of the given text."""

result = analyze_sentiment("I love this!")  # "positive"
```

### Сравнительная таблица библиотек

| Библиотека | Фокус | Провайдеры | Retries | Streaming | Complexity |
|------------|-------|------------|---------|-----------|------------|
| **Instructor** | Extraction | 15+ | Да | Да | Низкая |
| **Pydantic AI** | Agents | Major | Да | Да | Низкая |
| **BAML** | Schema parsing | All | Нет | Нет | Средняя |
| **LangChain** | Orchestration | Major | Да | Да | Высокая |
| **LlamaIndex** | RAG + Extraction | Major | Да | Да | Средняя |
| **Outlines** | Constrained gen | Local | Нет | Да | Средняя |
| **Marvin** | AI functions | OpenAI | Нет | Нет | Очень низкая |

---

## Практическая реализация

### OpenAI: Полный пример с обработкой ошибок

```python
"""
Полный production-ready пример Function Calling с OpenAI.

Включает:
- Определение tools с strict mode
- Обработка parallel tool calls
- Error handling и fallbacks
- Логирование для debugging
"""

import json
import logging
from typing import Callable, Dict, Any
from openai import OpenAI
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

# ============ TOOL DEFINITIONS ============

# Определяем tools как Python функции с документацией
def get_weather(city: str, units: str = "celsius") -> dict:
    """
    Получить текущую погоду в городе.

    В реальном приложении здесь был бы API call к weather service.
    """
    # Симуляция API response
    weather_data = {
        "Moscow": {"temp": -5, "condition": "snow", "humidity": 85},
        "Paris": {"temp": 8, "condition": "cloudy", "humidity": 70},
        "Tokyo": {"temp": 15, "condition": "sunny", "humidity": 60},
    }

    data = weather_data.get(city, {"temp": 20, "condition": "unknown", "humidity": 50})

    if units == "fahrenheit":
        data["temp"] = data["temp"] * 9/5 + 32

    return {**data, "city": city, "units": units}


def search_restaurants(
    location: str,
    cuisine: str | None = None,
    price_range: str | None = None,
    rating_min: float = 0.0
) -> list:
    """
    Поиск ресторанов по критериям.
    """
    # Симуляция поиска
    restaurants = [
        {"name": "Sakura", "cuisine": "japanese", "rating": 4.5, "price": "$$"},
        {"name": "La Maison", "cuisine": "french", "rating": 4.8, "price": "$$$"},
        {"name": "Pizza Roma", "cuisine": "italian", "rating": 4.2, "price": "$"},
    ]

    # Фильтрация
    results = restaurants
    if cuisine:
        results = [r for r in results if r["cuisine"] == cuisine]
    if rating_min:
        results = [r for r in results if r["rating"] >= rating_min]

    return results[:5]  # Limit results


# Реестр функций — связывает имена с реальными функциями
TOOL_REGISTRY: Dict[str, Callable] = {
    "get_weather": get_weather,
    "search_restaurants": search_restaurants,
}

# JSON Schema для каждой функции
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить текущую погоду в указанном городе. Используй когда пользователь спрашивает о погоде, температуре, осадках.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города на английском (например: Moscow, Paris, Tokyo)"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Единицы измерения температуры"
                    }
                },
                "required": ["city", "units"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Поиск ресторанов в указанном месте. Используй когда пользователь ищет где поесть, рестораны, кафе.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Город или район для поиска"
                    },
                    "cuisine": {
                        "type": "string",
                        "enum": ["italian", "japanese", "french", "chinese", "mexican"],
                        "description": "Тип кухни"
                    },
                    "price_range": {
                        "type": "string",
                        "enum": ["$", "$$", "$$$"],
                        "description": "Ценовой диапазон"
                    },
                    "rating_min": {
                        "type": "number",
                        "description": "Минимальный рейтинг (0-5)"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    }
]


# ============ EXECUTION ENGINE ============

def execute_tool_call(tool_call) -> str:
    """
    Выполнение одного tool call с обработкой ошибок.

    Returns:
        JSON string с результатом или ошибкой
    """
    function_name = tool_call.function.name

    try:
        # Парсим аргументы
        arguments = json.loads(tool_call.function.arguments)
        logger.info(f"Executing {function_name} with args: {arguments}")

        # Получаем функцию из реестра
        if function_name not in TOOL_REGISTRY:
            return json.dumps({"error": f"Unknown function: {function_name}"})

        func = TOOL_REGISTRY[function_name]

        # Выполняем функцию
        result = func(**arguments)

        logger.info(f"Result from {function_name}: {result}")
        return json.dumps(result, ensure_ascii=False)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse arguments: {e}")
        return json.dumps({"error": f"Invalid arguments JSON: {e}"})

    except TypeError as e:
        # Неверные аргументы функции
        logger.error(f"Invalid function arguments: {e}")
        return json.dumps({"error": f"Invalid arguments: {e}"})

    except Exception as e:
        # Любая другая ошибка
        logger.exception(f"Error executing {function_name}")
        return json.dumps({"error": f"Execution failed: {e}"})


def chat_with_tools(user_message: str, max_iterations: int = 5) -> str:
    """
    Полный цикл общения с поддержкой tool calls.

    Args:
        user_message: Сообщение пользователя
        max_iterations: Максимум итераций (защита от бесконечных циклов)

    Returns:
        Финальный текстовый ответ
    """
    messages = [
        {
            "role": "system",
            "content": """Ты полезный ассистент с доступом к инструментам.
            Используй инструменты когда нужна актуальная информация.
            Отвечай на русском языке."""
        },
        {"role": "user", "content": user_message}
    ]

    for iteration in range(max_iterations):
        logger.info(f"Iteration {iteration + 1}")

        # Запрос к LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"  # LLM сам решает, нужны ли tools
        )

        assistant_message = response.choices[0].message

        # Проверяем, есть ли tool calls
        if not assistant_message.tool_calls:
            # Нет tool calls — возвращаем текстовый ответ
            logger.info("No tool calls, returning text response")
            return assistant_message.content

        # Есть tool calls — выполняем их
        logger.info(f"Got {len(assistant_message.tool_calls)} tool calls")

        # Добавляем ответ ассистента в историю
        messages.append(assistant_message)

        # Выполняем каждый tool call
        for tool_call in assistant_message.tool_calls:
            result = execute_tool_call(tool_call)

            # Добавляем результат в историю
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    # Превышен лимит итераций
    logger.warning("Max iterations reached")
    return "Извините, не удалось завершить запрос. Попробуйте переформулировать."


# ============ USAGE ============

if __name__ == "__main__":
    # Пример 1: Простой запрос погоды
    print("=" * 50)
    result = chat_with_tools("Какая погода в Москве?")
    print(f"Response: {result}")

    # Пример 2: Parallel tool calls
    print("=" * 50)
    result = chat_with_tools("Сравни погоду в Москве и Париже")
    print(f"Response: {result}")

    # Пример 3: Поиск ресторанов
    print("=" * 50)
    result = chat_with_tools("Найди хорошие японские рестораны в центре")
    print(f"Response: {result}")

    # Пример 4: Без tools (LLM отвечает сам)
    print("=" * 50)
    result = chat_with_tools("Что такое машинное обучение?")
    print(f"Response: {result}")
```

### Anthropic: Реализация с Claude

Claude использует немного другой API, но концепция та же.

```python
"""
Tool Use с Anthropic Claude.

Ключевые отличия от OpenAI:
1. input_schema вместо parameters
2. Другой формат tool results
3. stop_reason для определения tool use
"""

import anthropic
import json
from typing import Dict, Any

client = anthropic.Anthropic()

# ============ TOOL DEFINITIONS (Anthropic format) ============

TOOLS = [
    {
        "name": "get_weather",
        # Anthropic использует input_schema, а не parameters
        "description": "Получить текущую погоду в городе",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Название города"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Выполнить математические вычисления",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Математическое выражение (например: 2 + 2 * 3)"
                }
            },
            "required": ["expression"]
        }
    }
]

# Реестр функций
def get_weather(city: str, units: str = "celsius") -> dict:
    weather_data = {
        "Moscow": {"temp": -5, "condition": "snow"},
        "Paris": {"temp": 8, "condition": "cloudy"},
    }
    return weather_data.get(city, {"temp": 20, "condition": "unknown"})

def calculate(expression: str) -> dict:
    try:
        # ВНИМАНИЕ: В production используйте безопасный eval!
        # Это только для демонстрации
        import ast
        # Безопасный eval через AST
        result = eval(compile(ast.parse(expression, mode='eval'), '', 'eval'))
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e)}

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate": calculate,
}


def chat_with_claude(user_message: str) -> str:
    """
    Полный цикл общения с Claude и tool use.
    """
    messages = [{"role": "user", "content": user_message}]

    while True:
        # Запрос к Claude
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        # Проверяем stop_reason
        # "tool_use" означает, что Claude хочет использовать инструменты
        if response.stop_reason != "tool_use":
            # Извлекаем текстовый ответ
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "No response generated"

        # Обрабатываем tool use
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                # Выполняем функцию
                func = TOOL_REGISTRY.get(block.name)
                if func:
                    result = func(**block.input)
                else:
                    result = {"error": f"Unknown tool: {block.name}"}

                # Формируем результат в формате Anthropic
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        # Добавляем ответ ассистента и результаты в историю
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    # Тест
    result = chat_with_claude("Какая погода в Москве и сколько будет 15 * 7 + 23?")
    print(result)
```

### Instructor: Упрощаем всё

Instructor — библиотека, которая абстрагирует boilerplate и добавляет Pydantic validation.

```python
"""
Instructor — самый простой способ работать со structured outputs.

Преимущества:
1. Pydantic models вместо JSON Schema
2. Автоматические retries при ошибках валидации
3. Единый API для разных провайдеров
4. Type safety и IDE autocomplete
"""

import instructor
from openai import OpenAI
from anthropic import Anthropic
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

# ============ PYDANTIC MODELS ============

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class ReviewAnalysis(BaseModel):
    """Анализ отзыва о продукте."""

    sentiment: Sentiment = Field(
        description="Общая тональность отзыва"
    )

    rating: int = Field(
        ge=1, le=5,
        description="Оценка от 1 до 5"
    )

    pros: List[str] = Field(
        description="Список плюсов продукта",
        min_length=0,
        max_length=5
    )

    cons: List[str] = Field(
        description="Список минусов продукта",
        min_length=0,
        max_length=5
    )

    summary: str = Field(
        max_length=200,
        description="Краткое резюме отзыва в 1-2 предложениях"
    )

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Summary too short")
        return v


class ExtractedEntity(BaseModel):
    """Извлечённая сущность из текста."""

    text: str = Field(description="Текст сущности как в оригинале")
    entity_type: str = Field(description="Тип: PERSON, ORG, LOCATION, DATE, MONEY")
    confidence: float = Field(ge=0, le=1, description="Уверенность от 0 до 1")


class NERResult(BaseModel):
    """Результат Named Entity Recognition."""
    entities: List[ExtractedEntity]

    @property
    def persons(self) -> List[ExtractedEntity]:
        return [e for e in self.entities if e.entity_type == "PERSON"]

    @property
    def organizations(self) -> List[ExtractedEntity]:
        return [e for e in self.entities if e.entity_type == "ORG"]


# ============ INSTRUCTOR SETUP ============

# Патчим клиент — это добавляет response_model поддержку
openai_client = instructor.from_openai(OpenAI())
anthropic_client = instructor.from_anthropic(Anthropic())


def analyze_review(review_text: str) -> ReviewAnalysis:
    """
    Анализ отзыва с автоматическими retries.

    Instructor автоматически:
    1. Конвертирует Pydantic model в JSON Schema
    2. Парсит ответ LLM
    3. Валидирует через Pydantic
    4. Retries если валидация failed
    """
    return openai_client.chat.completions.create(
        model="gpt-4o-mini",  # Можно использовать дешёвую модель
        messages=[
            {
                "role": "system",
                "content": "Ты эксперт по анализу отзывов. Извлекай структурированную информацию."
            },
            {
                "role": "user",
                "content": f"Проанализируй отзыв:\n\n{review_text}"
            }
        ],
        response_model=ReviewAnalysis,
        max_retries=3  # Повторить до 3 раз при ошибках
    )


def extract_entities(text: str) -> NERResult:
    """
    Named Entity Recognition через LLM.

    Показывает, как использовать LLM для задач NLP.
    """
    return openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Извлеки именованные сущности из текста.
                Типы: PERSON, ORG (организации), LOCATION, DATE, MONEY.
                Указывай confidence на основе контекста."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_model=NERResult
    )


# ============ STREAMING ============

def stream_analysis(text: str):
    """
    Streaming partial results.

    Полезно для:
    - Показа прогресса пользователю
    - Длинных извлечений
    - Улучшения UX
    """
    for partial in openai_client.chat.completions.create_partial(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Analyze: {text}"}
        ],
        response_model=ReviewAnalysis
    ):
        # partial — это частично заполненная модель
        # Поля появляются по мере генерации
        print(f"Current state: {partial}")

        if partial.sentiment:
            print(f"  Sentiment detected: {partial.sentiment}")
        if partial.pros:
            print(f"  Pros so far: {partial.pros}")


# ============ USAGE ============

if __name__ == "__main__":
    # Анализ отзыва
    review = """
    Купил iPhone 15 Pro месяц назад. Камера просто огонь - снимки
    как с профессионального фотоаппарата! Батарея держит весь день.
    Единственный минус - цена кусается, и зарядка в комплекте не идёт.
    В целом доволен покупкой, рекомендую!
    """

    analysis = analyze_review(review)
    print(f"Sentiment: {analysis.sentiment.value}")
    print(f"Rating: {analysis.rating}/5")
    print(f"Pros: {analysis.pros}")
    print(f"Cons: {analysis.cons}")
    print(f"Summary: {analysis.summary}")

    # NER
    text = """
    Илон Маск объявил, что Tesla откроет новый завод в Берлине
    в марте 2024 года. Инвестиции составят $5 млрд.
    """

    ner_result = extract_entities(text)
    print(f"\nPersons: {[e.text for e in ner_result.persons]}")
    print(f"Organizations: {[e.text for e in ner_result.organizations]}")
```

---

## Типичные ошибки и как их избежать

### Ошибка 1: Плохие описания tools

**Проблема**: LLM неправильно выбирает инструменты или не использует их.

```python
# ПЛОХО: Непонятно когда использовать
{
    "name": "search",
    "description": "Search function",
    "parameters": {
        "properties": {
            "q": {"type": "string"}
        }
    }
}

# ХОРОШО: Детальное описание с примерами
{
    "name": "search_knowledge_base",
    "description": """
    Поиск по внутренней базе знаний компании.

    ИСПОЛЬЗУЙ когда:
    - Пользователь спрашивает о политиках компании
    - Нужна информация о внутренних процессах
    - Вопросы о продуктах компании

    НЕ ИСПОЛЬЗУЙ для:
    - Общих вопросов (погода, новости)
    - Вопросов о других компаниях

    Примеры запросов:
    - "Какая политика отпусков?" → query: "vacation policy"
    - "Как подать expense report?" → query: "expense report process"
    """,
    "parameters": {
        "properties": {
            "query": {
                "type": "string",
                "description": "Поисковый запрос на английском, 2-5 ключевых слов"
            }
        }
    }
}
```

### Ошибка 2: Слишком много tools

**Проблема**: При большом количестве tools (>10-15) модель начинает путаться.

```python
# ПЛОХО: 30 отдельных tools
tools = [
    {"name": "get_user_profile", ...},
    {"name": "update_user_name", ...},
    {"name": "update_user_email", ...},
    {"name": "update_user_phone", ...},
    {"name": "delete_user", ...},
    # ... ещё 25 tools
]

# ХОРОШО: Группировка или RAG-based selection
# Вариант 1: Один tool с actions
{
    "name": "manage_user",
    "description": "Управление данными пользователя",
    "parameters": {
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get", "update", "delete"]
            },
            "user_id": {"type": "string"},
            "updates": {
                "type": "object",
                "description": "Поля для обновления (для action=update)"
            }
        }
    }
}

# Вариант 2: RAG-based tool selection
async def select_relevant_tools(user_query: str, all_tools: list) -> list:
    """Выбрать релевантные tools через semantic search."""
    query_embedding = await embed(user_query)
    tool_embeddings = await embed_tools(all_tools)

    similarities = cosine_similarity(query_embedding, tool_embeddings)
    top_indices = similarities.argsort()[-5:]  # Top 5 tools

    return [all_tools[i] for i in top_indices]
```

> **Anthropic Tool Search Tool (2025)**: Anthropic представил Tool Search Tool, который позволяет Claude работать с тысячами tools без загрузки всех определений в context window. Tools помечаются `defer_loading: true`, и Claude находит нужные через поиск.

### Ошибка 3: Отсутствие валидации аргументов

**Проблема**: Blind trust к аргументам от LLM = security риск.

```python
# ПЛОХО: Никакой валидации
def execute_sql(query: str) -> dict:
    return db.execute(query)  # SQL Injection!

# ПЛОХО: eval без санитизации
def calculate(expression: str) -> dict:
    return {"result": eval(expression)}  # Code Injection!

# ХОРОШО: Строгая валидация
from pydantic import BaseModel, field_validator
import re

class SQLQuery(BaseModel):
    table: str
    columns: list[str]
    where: dict | None = None
    limit: int = 100

    @field_validator("table")
    @classmethod
    def validate_table(cls, v: str) -> str:
        allowed_tables = {"users", "products", "orders"}
        if v not in allowed_tables:
            raise ValueError(f"Table {v} not allowed")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v > 1000:
            raise ValueError("Limit too high")
        return v

def safe_query(query: SQLQuery) -> dict:
    """Безопасный SQL через ORM или prepared statements."""
    return db.session.query(query.table).filter(**query.where).limit(query.limit).all()


class MathExpression(BaseModel):
    expression: str

    @field_validator("expression")
    @classmethod
    def validate_expression(cls, v: str) -> str:
        # Только цифры и базовые операторы
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', v):
            raise ValueError("Invalid characters in expression")
        return v

def safe_calculate(expr: MathExpression) -> dict:
    """Безопасные вычисления через ast.literal_eval или numexpr."""
    import ast
    return {"result": ast.literal_eval(expr.expression)}
```

### Ошибка 4: Огромные tool results

**Проблема**: Результаты tools переполняют context window.

```python
# ПЛОХО: Возвращаем всё
def search_database(query: str) -> dict:
    results = db.search(query)  # 10,000 записей
    return {"results": results}  # Убьёт context window

# ХОРОШО: Лимиты и пагинация
def search_database(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> dict:
    results = db.search(query, limit=limit, offset=offset)
    total = db.count(query)

    return {
        "results": results,
        "total": total,
        "has_more": total > offset + limit,
        "next_offset": offset + limit if total > offset + limit else None
    }

# ХОРОШО: Суммаризация больших результатов
def get_document(doc_id: str) -> dict:
    doc = db.get_document(doc_id)

    if len(doc["content"]) > 5000:
        # Суммаризация длинного документа
        summary = summarize(doc["content"])
        return {
            "id": doc_id,
            "title": doc["title"],
            "summary": summary,
            "full_content_available": True,
            "note": "Полный текст доступен через get_document_full()"
        }

    return doc
```

### Ошибка 5: Игнорирование ошибок выполнения

**Проблема**: LLM не знает, что пошло не так, и не может адаптироваться.

```python
# ПЛОХО: Молчаливый fail
def execute_tool(name: str, args: dict) -> str:
    try:
        result = REGISTRY[name](**args)
        return json.dumps(result)
    except Exception:
        return json.dumps({})  # LLM получит пустой результат без объяснения

# ХОРОШО: Информативные ошибки
def execute_tool(name: str, args: dict) -> str:
    try:
        result = REGISTRY[name](**args)
        return json.dumps({"success": True, "data": result})

    except KeyError:
        return json.dumps({
            "success": False,
            "error": "unknown_function",
            "message": f"Function '{name}' not found. Available: {list(REGISTRY.keys())}"
        })

    except TypeError as e:
        return json.dumps({
            "success": False,
            "error": "invalid_arguments",
            "message": f"Invalid arguments: {e}",
            "hint": "Check parameter names and types"
        })

    except PermissionError:
        return json.dumps({
            "success": False,
            "error": "permission_denied",
            "message": "This action requires elevated permissions"
        })

    except Exception as e:
        logging.exception(f"Unexpected error in {name}")
        return json.dumps({
            "success": False,
            "error": "internal_error",
            "message": "An unexpected error occurred. Please try again."
        })
```

### Ошибка 6: Format restrictions снижают качество reasoning

**Проблема**: Исследования показывают, что strict format constraints могут снижать качество reasoning.

```python
# ПЛОХО: Форсим структуру сразу для сложной задачи
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Solve this complex math problem..."}
    ],
    response_format=SolutionSchema  # Может снизить качество решения
)

# ХОРОШО: Двухэтапный подход
# Шаг 1: Свободное reasoning
reasoning = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Solve this problem step by step..."}
    ]
)

# Шаг 2: Структурирование результата
structured = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": f"Extract solution from: {reasoning.content}"}
    ],
    response_format=SolutionSchema
)
```

> **BAML подход**: BAML использует Schema-Aligned Parsing, позволяя модели генерировать naturally, а затем парсит результат. Это сохраняет качество reasoning.

---

## Best Practices

### 1. Проектирование Tool API

```
ПРИНЦИПЫ ХОРОШЕГО TOOL API:

1. Атомарность
   Каждый tool делает одну вещь хорошо

   ПЛОХО: manage_everything(action, entity, ...)
   ХОРОШО: get_user(), update_user(), delete_user()

2. Идемпотентность где возможно
   Повторный вызов с теми же аргументами даёт тот же результат

   ХОРОШО: get_weather("Moscow") → всегда одинаковый формат

3. Предсказуемые имена
   Глагол + существительное, snake_case

   ХОРОШО: search_products, get_weather, send_email
   ПЛОХО: doSearch, weatherGetter, email

4. Понятные описания
   Описание должно отвечать:
   - Что делает функция?
   - Когда её использовать?
   - Что она возвращает?
   - Какие ограничения?

5. Reasonable defaults
   Опциональные параметры с разумными значениями

   ХОРОШО: search(query, limit=10, offset=0)
```

### 2. Human-in-the-Loop для опасных операций

```python
from enum import Enum
from typing import Callable

class RiskLevel(str, Enum):
    SAFE = "safe"           # Чтение данных
    MODERATE = "moderate"   # Изменение данных
    DANGEROUS = "dangerous" # Удаление, платежи, рассылки

# Классификация tools по уровню риска
TOOL_RISK_LEVELS = {
    "get_weather": RiskLevel.SAFE,
    "search_products": RiskLevel.SAFE,
    "update_profile": RiskLevel.MODERATE,
    "send_email": RiskLevel.MODERATE,
    "delete_account": RiskLevel.DANGEROUS,
    "process_payment": RiskLevel.DANGEROUS,
    "send_mass_email": RiskLevel.DANGEROUS,
}


class HumanApprovalRequired(Exception):
    """Исключение для запроса одобрения."""
    def __init__(self, tool_name: str, arguments: dict, reason: str):
        self.tool_name = tool_name
        self.arguments = arguments
        self.reason = reason


def execute_with_approval(
    tool_name: str,
    arguments: dict,
    approval_callback: Callable[[str, dict], bool] | None = None
) -> dict:
    """
    Выполнение tool с учётом уровня риска.

    Args:
        tool_name: Имя функции
        arguments: Аргументы
        approval_callback: Функция для получения одобрения (UI, Slack, etc.)
    """
    risk_level = TOOL_RISK_LEVELS.get(tool_name, RiskLevel.MODERATE)

    if risk_level == RiskLevel.SAFE:
        # Безопасные операции — выполняем сразу
        return TOOL_REGISTRY[tool_name](**arguments)

    elif risk_level == RiskLevel.MODERATE:
        # Умеренный риск — логируем, но выполняем
        logging.info(f"MODERATE RISK: {tool_name} with {arguments}")
        return TOOL_REGISTRY[tool_name](**arguments)

    elif risk_level == RiskLevel.DANGEROUS:
        # Высокий риск — требуем одобрение
        if approval_callback is None:
            raise HumanApprovalRequired(
                tool_name=tool_name,
                arguments=arguments,
                reason=f"Dangerous operation requires human approval"
            )

        # Запрашиваем одобрение
        approved = approval_callback(tool_name, arguments)

        if approved:
            logging.warning(f"APPROVED DANGEROUS: {tool_name}")
            return TOOL_REGISTRY[tool_name](**arguments)
        else:
            return {"error": "Operation rejected by user"}
```

### 3. Мониторинг и Observability

```python
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolMetrics:
    tool_name: str
    arguments: dict
    result: Any
    duration_ms: float
    success: bool
    error: str | None = None

# Коллектор метрик (можно заменить на Prometheus, DataDog, etc.)
class MetricsCollector:
    def __init__(self):
        self.metrics: list[ToolMetrics] = []

    def record(self, metric: ToolMetrics):
        self.metrics.append(metric)

        # Отправка в мониторинг систему
        if not metric.success:
            logging.error(f"Tool failed: {metric.tool_name} - {metric.error}")

        if metric.duration_ms > 5000:
            logging.warning(f"Slow tool: {metric.tool_name} took {metric.duration_ms}ms")

collector = MetricsCollector()


def execute_with_metrics(tool_name: str, arguments: dict) -> dict:
    """Выполнение tool с метриками."""
    start_time = time.perf_counter()
    error = None
    success = True

    try:
        result = TOOL_REGISTRY[tool_name](**arguments)
    except Exception as e:
        result = {"error": str(e)}
        error = str(e)
        success = False

    duration_ms = (time.perf_counter() - start_time) * 1000

    collector.record(ToolMetrics(
        tool_name=tool_name,
        arguments=arguments,
        result=result,
        duration_ms=duration_ms,
        success=success,
        error=error
    ))

    return result
```

### 4. Тестирование Tools

```python
import pytest
from unittest.mock import patch, MagicMock

# ============ UNIT TESTS ============

def test_weather_tool_returns_correct_format():
    """Tool возвращает данные в ожидаемом формате."""
    result = get_weather("Moscow", "celsius")

    assert "temp" in result
    assert "condition" in result
    assert isinstance(result["temp"], (int, float))


def test_weather_tool_handles_unknown_city():
    """Tool корректно обрабатывает неизвестный город."""
    result = get_weather("UnknownCity123")

    # Должен вернуть дефолтные значения, а не упасть
    assert "temp" in result


# ============ INTEGRATION TESTS ============

@pytest.mark.integration
def test_llm_selects_correct_tool():
    """LLM выбирает правильный tool для запроса."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
        tools=TOOLS,
        tool_choice="auto"
    )

    assert response.choices[0].message.tool_calls is not None
    assert response.choices[0].message.tool_calls[0].function.name == "get_weather"


@pytest.mark.integration
def test_llm_extracts_correct_arguments():
    """LLM извлекает правильные аргументы."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Погода в Париже в фаренгейтах"}],
        tools=TOOLS,
    )

    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    assert args["city"] == "Paris"
    assert args["units"] == "fahrenheit"


# ============ ADVERSARIAL TESTS ============

@pytest.mark.security
def test_tool_rejects_injection_attempt():
    """Tool отклоняет попытки инъекции."""
    with pytest.raises(ValueError):
        # Попытка SQL injection
        safe_query(SQLQuery(
            table="users; DROP TABLE users;--",
            columns=["*"]
        ))


@pytest.mark.security
def test_calculator_rejects_code_execution():
    """Calculator не выполняет произвольный код."""
    with pytest.raises(ValueError):
        safe_calculate(MathExpression(
            expression="__import__('os').system('rm -rf /')"
        ))
```

### 5. Выбор подхода: Decision Tree

```
Нужен structured output от LLM?
│
├─ Используешь hosted API (OpenAI, Anthropic, Google)?
│   │
│   ├─ Простая extraction (1-2 поля)?
│   │   └─ Prompt engineering + JSON Mode достаточно
│   │
│   ├─ Сложная схема, нужны гарантии?
│   │   └─ Structured Outputs (strict: true)
│   │
│   └─ Нужны retries, streaming, multi-provider?
│       └─ Instructor
│
├─ Self-hosted модели (vLLM, SGLang)?
│   │
│   ├─ Простые schemas?
│   │   └─ XGrammar (default в vLLM 0.8+)
│   │
│   └─ Сложные грамматики, regex?
│       └─ Outlines или lm-format-enforcer
│
└─ Нужны agents с tools?
    │
    ├─ Full framework нужен?
    │   └─ LangChain / LangGraph
    │
    ├─ Pydantic-native, type-safe?
    │   └─ Pydantic AI
    │
    └─ Minimal, just extraction?
        └─ Instructor или Marvin
```

## Актуальность 2024-2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **OpenAI Structured Outputs** | ✅ GA (Aug 2024) | 100% schema compliance vs 35.9% с prompt engineering |
| **Anthropic Tool Use** | ✅ Production | Через tools API, нет native JSON mode, prefilling помогает |
| **Claude Extended Thinking** | 🆕 2025 | Reasoning + structured output = лучшее качество |
| **Instructor 1.x** | 🔥 3M+ downloads/mo | Единый API для 15+ провайдеров, retries, streaming |
| **XGrammar** | 🆕 Performance | До 100x быстрее regex-based constrained decoding |
| **MCP (Model Context Protocol)** | 🔥 Anthropic standard | Стандартизация tool definitions, cross-platform |
| **Gemini JSON Schema** | ✅ Native | Похоже на OpenAI Structured Outputs |
| **vLLM/SGLang structured** | ✅ Production | Server-side enforcement для self-hosted моделей |

### Provider Comparison 2025

| Provider | Native Structured Outputs | Reliability | Approach |
|----------|--------------------------|-------------|----------|
| **OpenAI** | ✅ Structured Outputs API | 100% schema | Constrained decoding |
| **Google Gemini** | ✅ responseSchema | High | Schema enforcement |
| **Anthropic** | ⚠️ Tools only | ~80-86% | Tool use + prefilling |
| **AWS Bedrock** | ⚠️ Depends on model | Varies | No native support |
| **Mistral** | ⚠️ JSON mode | Medium | No strict schema |

### Community Sentiment

**Что хвалят:**
- OpenAI Structured Outputs: "100% reliability — game changer для production"
- Instructor: "Must-have для любой extraction задачи"
- Pydantic AI: "Type-safe tools + agents = beautiful DX"

**Что критикуют:**
- Anthropic: "Нет native JSON mode — приходится использовать tool use workaround"
- Strict mode: "Иногда снижает reasoning quality — двухэтапный подход лучше"
- JSON Mode: "50% больше вариации чем Tool Calling при переименовании полей"

**Best Practice:**
> "Всегда предпочитайте Structured Outputs вместо JSON Mode. Structured Outputs — эволюция JSON mode с гарантией соответствия схеме." — OpenAI Docs

---

## Связанные материалы

- [[llm-fundamentals]] — Основы работы LLM
- [[prompt-engineering-masterclass]] — Промпт инжиниринг
- [[ai-agents-advanced]] — Агенты с tool use
- [[mcp-model-context-protocol]] — MCP для стандартизации tools
- [[local-llms-self-hosting]] — Self-hosted LLM с constrained decoding

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Chomsky N. (1956). *Three Models for the Description of Language*. IRE Transactions | Иерархия формальных грамматик — основа constrained decoding |
| 2 | Milner R. (1978). *A Theory of Type Polymorphism in Programming*. JCSS | Принцип типовой безопасности, применимый к JSON Schema |
| 3 | Willard B., Louf R. (2023). *Efficient Guided Generation for LLMs*. arXiv:2307.09702 | Формализация constrained decoding через конечные автоматы |
| 4 | Dong Y. et al. (2024). *XGrammar: Flexible and Efficient Structured Generation*. arXiv:2411.15100 | 100x ускорение через pushdown automata |
| 5 | Scholak T. et al. (2021). *PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding*. EMNLP | CFG-guided decoding без потери качества |
| 6 | Schick T. et al. (2023). *Toolformer: Language Models Can Teach Themselves to Use Tools*. arXiv:2302.04761 | Self-supervised обучение tool use |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) | API, strict mode, 100% compliance |
| 2 | [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) | Tool definitions, parallel calls |
| 3 | [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) | Claude tools API, input_schema |
| 4 | [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) | Computer use, MCP integration |
| 5 | [Gemini Structured Outputs](https://ai.google.dev/gemini-api/docs/structured-output) | responseSchema, native support |
| 6 | [Instructor Docs](https://python.useinstructor.com/) | Multi-provider, retries, streaming |
| 7 | [Pydantic AI](https://ai.pydantic.dev/) | Type-safe tools, agents |
| 8 | [Outlines](https://github.com/dottxt-ai/outlines) | Regex, grammar constraints |
| 9 | [BAML](https://github.com/BoundaryML/baml) | Schema-first, multi-language |
| 10 | [Martin Fowler: Function Calling](https://martinfowler.com/articles/function-call-LLM.html) | Architecture patterns |
| 11 | [Boundary ML: False Confidence](https://boundaryml.com/blog/structured-outputs-create-false-confidence) | Format ≠ correctness |

---

*Последнее обновление: 2024-12-28*

---

[[ai-engineering-moc|← AI Engineering MOC]] | [[prompt-engineering-masterclass|← Prompts]] | [[ai-agents-advanced|Agents →]]

---

## Связь с другими темами

**[[ai-api-integration]]** — Structured outputs и function calling являются ключевыми механизмами интеграции LLM через API. Если API-интеграция определяет «как» подключиться к модели, то structured outputs определяют «в каком формате» модель возвращает данные. JSON mode, response_format и tool definitions — всё это параметры API, которые превращают свободный текст в программно обрабатываемые структуры.

**[[mcp-model-context-protocol]]** — Model Context Protocol стандартизирует то, как LLM взаимодействует с внешними инструментами, а structured outputs обеспечивают надёжность этого взаимодействия. MCP определяет протокол коммуникации, а structured outputs гарантируют, что вызовы инструментов и их результаты соответствуют ожидаемым схемам. Вместе они формируют надёжный интерфейс между моделью и внешним миром.

**[[type-systems-theory]]** — Теория систем типов даёт формальную основу для понимания structured outputs. JSON Schema, Pydantic-модели и TypeScript-типы — это практические реализации типовых систем, обеспечивающих валидацию на этапе компиляции и рантайма. Понимание variance, generics и type inference помогает проектировать более точные и безопасные схемы для LLM-ответов.

---

---

---

## Проверь себя

> [!question]- Почему Structured Outputs (constrained decoding) дает 100% JSON compliance, а JSON mode -- нет?
> Structured Outputs модифицирует sampling процесс: на каждом шаге генерации маскируются токены, нарушающие JSON schema. Модель физически не может сгенерировать невалидный JSON. JSON mode просто добавляет инструкцию "ответь в JSON" без гарантий -- модель может нарушить структуру, пропустить поля или добавить лишние.

> [!question]- Вы извлекаете структурированные данные из 10000 invoices. Какой подход выберете: Structured Outputs, Instructor или ручной парсинг?
> Structured Outputs через Pydantic schema: 100% compliance, автоматическая валидация, типизация. Instructor -- если нужен retry с автоматическим исправлением ошибок валидации (передает ошибку модели для коррекции). Ручной парсинг -- только если модель не поддерживает structured outputs. Batch API для экономии 50%.

> [!question]- Чем Tool Use (function calling) отличается от Structured Outputs и когда использовать каждый?
> Structured Outputs: гарантированный формат ответа (извлечение данных, classification). Tool Use: модель решает какую функцию вызвать и с какими параметрами (weather API, database query). Structured Outputs для "дай мне данные в формате X". Tool Use для "используй инструмент Y когда нужно".

---

## Ключевые карточки

Что такое Structured Outputs?
?
Гарантированное соответствие JSON schema через constrained decoding. OpenAI: response_format с Pydantic моделью. Anthropic: tool_use с input_schema. Google: response_schema. 100% compliance -- модель физически не может нарушить schema.

Что такое Instructor и зачем нужен?
?
Python-библиотека для structured extraction с auto-retry. Оборачивает OpenAI/Anthropic SDK, добавляет Pydantic-валидацию и автоматическую коррекцию: при ошибке валидации ошибка передается модели для исправления. Поддерживает streaming partial objects.

Function Calling vs Tool Use -- в чем разница?
?
Функционально одно и то же. OpenAI называет "function calling" (в tools array), Anthropic -- "tool use". Модель получает описания функций, решает какую вызвать, генерирует аргументы. Разработчик вызывает функцию и возвращает результат модели.

Что такое Constrained Decoding?
?
Техника модификации sampling при генерации. На каждом шаге вычисляются допустимые следующие токены (по JSON schema), недопустимые маскируются (logit = -inf). Результат: 100% валидный JSON без post-processing. Используется в OpenAI Structured Outputs, Outlines, llama.cpp.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[mcp-model-context-protocol]] | MCP -- стандарт для tool integration, следующий уровень после function calling |
| Углубиться | [[ai-agents-advanced]] | Агенты активно используют tool use для автономных действий |
| Смежная тема | [[type-systems-theory]] | Теория систем типов -- основа для понимания schema validation |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
