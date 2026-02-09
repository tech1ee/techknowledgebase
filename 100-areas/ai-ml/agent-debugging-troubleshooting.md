---
title: "AI Agent Debugging & Troubleshooting"
tags:
  - topic/ai-ml
  - agents
  - debugging
  - troubleshooting
  - observability
  - langgraph
  - tracing
  - production
  - type/concept
  - level/intermediate
category: ai-ml
level: intermediate-advanced
created: 2026-01-11
updated: 2026-01-11
sources:
  - langchain.com
  - arize.ai
  - anthropic.com
  - openai.com
status: published
---

# AI Agent Debugging & Troubleshooting: Полное руководство

---

## TL;DR

> Отладка AI-агентов — это искусство поиска причин непредсказуемого поведения в системах с недетерминированным ядром (LLM). В отличие от классического debugging где ошибка = баг в коде, здесь ошибка может быть в промпте, контексте, инструментах, модели или их комбинации. Этот гайд даёт систематический подход к диагностике и исправлению проблем на всех уровнях.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание AI Agents** | Архитектура агентов | [[ai-agents-advanced]] |
| **Tool Use / Function Calling** | Понимание как работают tools | [[structured-outputs-tools]] |
| **LangGraph или другой фреймворк** | Практика работы с агентами | [[tutorial-ai-agent]] |
| **Промпт-инжиниринг** | Важно для debugging промптов | [[prompt-engineering-masterclass]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ После туториала | Сначала [[tutorial-ai-agent]] |
| **AI Engineer** | ✅ Да | Основная аудитория |
| **Backend Developer** | ✅ Да | Integration debugging |
| **SRE/DevOps** | ✅ Да | Production troubleshooting |

### Терминология для новичков

> **Debugging агентов** = детективная работа — ищем, почему агент сделал не то, что ожидали

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Trace** | Полный лог выполнения агента | **Запись видеорегистратора** — всё что происходило |
| **Span** | Один шаг внутри trace | **Один кадр** — конкретное действие |
| **Hallucination** | Агент "выдумывает" несуществующее | **Фантазии** — придумал tool или факт |
| **Loop** | Агент застрял в бесконечном цикле | **Заевшая пластинка** — повторяет одно и то же |
| **Context Overflow** | Превышен лимит токенов | **Переполнение памяти** — слишком много данных |
| **Tool Failure** | Инструмент вернул ошибку | **Сломанный молоток** — tool не работает |
| **Prompt Injection** | Вредоносный ввод меняет поведение | **Социальная инженерия** — манипуляция агентом |
| **Observability** | Способность видеть что происходит внутри | **Прозрачность** — всё видно изнутри |

---

## Философия: почему отладка агентов сложнее обычного debugging

### Классический debugging vs Agent debugging

```
КЛАССИЧЕСКИЙ DEBUGGING:
Input → Code → Output
  ↓
Детерминированный: один input = один output
Воспроизводимый: запускаешь снова = тот же результат
Локализуемый: ошибка в конкретной строке кода

AGENT DEBUGGING:
Input → [LLM + Tools + Memory + State] → Output
                    ↓
Стохастический: один input = разные outputs
Контекстозависимый: история влияет на результат
Многослойный: ошибка может быть в промпте, модели, tool, memory
```

### Три уникальных вызова

**1. Недетерминизм LLM**
Одинаковый промпт → разные ответы (temperature > 0). Баг может быть "плавающим" и проявляться только в 30% случаев.

**2. Эмерджентное поведение**
Агент может "придумать" стратегию, которую вы не программировали. Иногда это хорошо (креативность), иногда плохо (unexpected behavior).

**3. Каскадные ошибки**
Ошибка на шаге 1 → неверный tool call на шаге 2 → галлюцинация на шаге 3 → полный провал на шаге 4.

---

## Уровни отладки: систематический подход

```
┌────────────────────────────────────────────────────────────┐
│                    DEBUGGING PYRAMID                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  L5: SYSTEM LEVEL                                           │
│      Production issues, scaling, integration                │
│                     ▲                                       │
│  L4: ORCHESTRATION LEVEL                                    │
│      Multi-agent coordination, handoffs, workflows          │
│                     ▲                                       │
│  L3: STATE & MEMORY LEVEL                                   │
│      Context window, memory corruption, state bugs          │
│                     ▲                                       │
│  L2: TOOL LEVEL                                             │
│      Tool failures, wrong tool selection, invalid params    │
│                     ▲                                       │
│  L1: LLM LEVEL                                              │
│      Prompt issues, hallucinations, reasoning failures      │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Level 1: LLM-Level Debugging

### Симптом 1: Галлюцинации (Hallucinations)

**Что происходит:** Агент уверенно утверждает ложное — выдумывает факты, несуществующие tools, или "помнит" то, чего не было.

**Диагностика:**
```python
# Добавляем проверку фактов в trace
def diagnose_hallucination(response: str, ground_truth: dict) -> dict:
    """Проверяем ответ на галлюцинации"""
    issues = []

    # 1. Проверяем упомянутые tools
    mentioned_tools = extract_tool_names(response)
    for tool in mentioned_tools:
        if tool not in AVAILABLE_TOOLS:
            issues.append(f"Hallucinated tool: {tool}")

    # 2. Проверяем факты (если есть ground truth)
    for fact, expected in ground_truth.items():
        if fact in response and expected not in response:
            issues.append(f"Wrong fact: expected {expected}")

    return {
        "has_hallucinations": len(issues) > 0,
        "issues": issues
    }
```

**Решения:**

| Причина | Решение | Пример |
|---------|---------|--------|
| Слишком широкий system prompt | Сузить scope, добавить constraints | "Отвечай только на вопросы о продуктах компании X" |
| Нет grounding | Добавить RAG или tool verification | Проверять факты через search tool |
| Temperature высокий | Снизить для factual tasks | `temperature=0.1` для data extraction |
| Модель не знает | Добавить "Скажи если не знаешь" | `"If uncertain, respond with 'I don't have this information'"` |

### Симптом 2: Неправильный reasoning

**Что происходит:** Агент неверно интерпретирует задачу, делает нелогичные выводы, или пропускает очевидные шаги.

**Диагностика с Chain-of-Thought:**
```python
# Добавляем explicit reasoning в промпт
DEBUGGING_SYSTEM_PROMPT = """
Before taking any action, you MUST:
1. State your understanding of the current task
2. List what information you have
3. List what information you need
4. Explain your reasoning for the next step
5. Only then execute the action

Format your thinking in <thinking> tags:
<thinking>
Task: [your understanding]
Have: [known information]
Need: [missing information]
Reasoning: [why this action]
</thinking>
"""
```

**Анализ reasoning traces:**
```python
def analyze_reasoning_quality(trace: list[dict]) -> dict:
    """Анализируем качество рассуждений агента"""
    issues = []

    for step in trace:
        thinking = extract_thinking(step.get("content", ""))
        action = step.get("action")

        # Проверяем логичность перехода thinking → action
        if thinking and action:
            coherence = check_thinking_action_coherence(thinking, action)
            if coherence < 0.7:
                issues.append({
                    "step": step["step_number"],
                    "issue": "Reasoning doesn't match action",
                    "thinking": thinking[:200],
                    "action": action
                })

        # Проверяем на circular reasoning
        if is_circular_reasoning(thinking):
            issues.append({
                "step": step["step_number"],
                "issue": "Circular reasoning detected"
            })

    return {"reasoning_issues": issues}
```

### Симптом 3: Prompt sensitivity

**Что происходит:** Минимальные изменения в формулировке задачи приводят к драматически разным результатам.

**Тестирование стабильности:**
```python
async def test_prompt_stability(agent, base_prompt: str, n_runs: int = 10) -> dict:
    """Тестируем стабильность ответов на один промпт"""
    variations = [
        base_prompt,
        base_prompt + " ",  # Trailing space
        base_prompt.lower(),
        "Please " + base_prompt,
        base_prompt + " Thanks!",
    ]

    results = {}
    for variant in variations:
        responses = []
        for _ in range(n_runs):
            response = await agent.run(variant)
            responses.append(normalize_response(response))

        # Считаем уникальные ответы
        unique_responses = len(set(responses))
        consistency = 1 - (unique_responses - 1) / n_runs

        results[variant[:50]] = {
            "consistency": consistency,
            "unique_responses": unique_responses
        }

    return results
```

---

## Level 2: Tool-Level Debugging

### Симптом 1: Wrong tool selection

**Что происходит:** Агент выбирает неподходящий инструмент для задачи.

**Диагностика:**
```python
from typing import Literal

class ToolSelectionDebugger:
    def __init__(self, tools: list[dict]):
        self.tools = {t["name"]: t for t in tools}
        self.selection_log = []

    def log_selection(
        self,
        query: str,
        selected_tool: str,
        expected_tool: str | None = None
    ):
        entry = {
            "query": query,
            "selected": selected_tool,
            "expected": expected_tool,
            "tool_description": self.tools[selected_tool].get("description"),
            "is_correct": selected_tool == expected_tool if expected_tool else None
        }
        self.selection_log.append(entry)

    def analyze_misselections(self) -> list[dict]:
        """Анализируем паттерны неправильного выбора tools"""
        misselections = [e for e in self.selection_log if e["is_correct"] == False]

        # Группируем по паттернам
        patterns = {}
        for m in misselections:
            key = f"{m['expected']} → {m['selected']}"
            if key not in patterns:
                patterns[key] = {"count": 0, "examples": []}
            patterns[key]["count"] += 1
            patterns[key]["examples"].append(m["query"][:100])

        return patterns
```

**Решения:**

| Причина | Решение |
|---------|---------|
| Похожие описания tools | Сделать descriptions более distinct |
| Нечёткая формулировка задачи | Добавить примеры в tool description |
| Слишком много tools | Группировать в категории, использовать router |
| Ambiguous naming | Переименовать tools более явно |

**Пример улучшения tool description:**
```python
# ПЛОХО: похожие описания
tools = [
    {"name": "search", "description": "Search for information"},
    {"name": "lookup", "description": "Look up information"},
]

# ХОРОШО: чёткие различия
tools = [
    {
        "name": "web_search",
        "description": "Search the internet for current events, news, and real-time information. Use when you need up-to-date data that may have changed recently."
    },
    {
        "name": "knowledge_lookup",
        "description": "Look up information in our internal knowledge base. Use for company policies, product specifications, and established facts that don't change."
    },
]
```

### Симптом 2: Invalid tool parameters

**Что происходит:** Агент вызывает tool с неправильными или невалидными параметрами.

**Диагностика и валидация:**
```python
from pydantic import BaseModel, ValidationError
from typing import Any

class ToolCallValidator:
    def __init__(self, tool_schemas: dict[str, type[BaseModel]]):
        self.schemas = tool_schemas
        self.validation_errors = []

    def validate_call(self, tool_name: str, params: dict[str, Any]) -> tuple[bool, str | None]:
        """Валидируем параметры вызова tool"""
        if tool_name not in self.schemas:
            return False, f"Unknown tool: {tool_name}"

        try:
            self.schemas[tool_name](**params)
            return True, None
        except ValidationError as e:
            error_msg = str(e)
            self.validation_errors.append({
                "tool": tool_name,
                "params": params,
                "error": error_msg
            })
            return False, error_msg

    def get_common_errors(self) -> dict:
        """Анализируем частые ошибки валидации"""
        error_patterns = {}
        for err in self.validation_errors:
            # Извлекаем тип ошибки
            if "missing" in err["error"].lower():
                pattern = "missing_required_field"
            elif "type" in err["error"].lower():
                pattern = "wrong_type"
            elif "value" in err["error"].lower():
                pattern = "invalid_value"
            else:
                pattern = "other"

            key = f"{err['tool']}:{pattern}"
            error_patterns[key] = error_patterns.get(key, 0) + 1

        return error_patterns
```

**Добавляем self-healing:**
```python
async def call_tool_with_retry(
    agent,
    tool_name: str,
    params: dict,
    max_retries: int = 2
) -> Any:
    """Вызываем tool с автоматическим исправлением ошибок"""
    for attempt in range(max_retries + 1):
        is_valid, error = validator.validate_call(tool_name, params)

        if is_valid:
            return await execute_tool(tool_name, params)

        if attempt < max_retries:
            # Просим агента исправить параметры
            fix_prompt = f"""
            Your tool call had validation errors:
            Tool: {tool_name}
            Params: {params}
            Error: {error}

            Please provide corrected parameters.
            """
            params = await agent.fix_params(fix_prompt)
        else:
            raise ToolValidationError(f"Failed after {max_retries} retries: {error}")
```

### Симптом 3: Tool timeout/failure

**Что происходит:** Tool не отвечает или возвращает ошибку.

**Graceful degradation pattern:**
```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

class ResilientToolExecutor:
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.failure_log = []

    async def execute_with_fallback(
        self,
        primary_tool: Callable[..., T],
        fallback_tool: Callable[..., T] | None,
        *args, **kwargs
    ) -> tuple[T | None, str]:
        """Выполняем tool с fallback и timeout"""

        # Пробуем primary tool
        for attempt in range(self.max_retries):
            try:
                result = await asyncio.wait_for(
                    primary_tool(*args, **kwargs),
                    timeout=self.timeout
                )
                return result, "success"
            except asyncio.TimeoutError:
                self.failure_log.append({
                    "tool": primary_tool.__name__,
                    "error": "timeout",
                    "attempt": attempt
                })
            except Exception as e:
                self.failure_log.append({
                    "tool": primary_tool.__name__,
                    "error": str(e),
                    "attempt": attempt
                })

        # Пробуем fallback
        if fallback_tool:
            try:
                result = await asyncio.wait_for(
                    fallback_tool(*args, **kwargs),
                    timeout=self.timeout
                )
                return result, "fallback"
            except Exception as e:
                return None, f"all_failed: {e}"

        return None, "all_failed"
```

---

## Level 3: State & Memory Debugging

### Симптом 1: Context window overflow

**Что происходит:** Агент "забывает" ранние части разговора или tool outputs обрезаются.

**Диагностика:**
```python
import tiktoken

class ContextWindowMonitor:
    def __init__(self, model: str, max_tokens: int):
        self.encoder = tiktoken.encoding_for_model(model)
        self.max_tokens = max_tokens
        self.usage_history = []

    def check_usage(self, messages: list[dict]) -> dict:
        """Проверяем использование контекстного окна"""
        total_tokens = 0
        breakdown = []

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):  # Multimodal
                content = str(content)
            tokens = len(self.encoder.encode(content))
            total_tokens += tokens
            breakdown.append({
                "role": msg.get("role"),
                "tokens": tokens,
                "preview": content[:100]
            })

        usage = total_tokens / self.max_tokens
        self.usage_history.append(usage)

        return {
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "usage_percent": usage * 100,
            "is_near_limit": usage > 0.8,
            "is_over_limit": usage > 1.0,
            "breakdown": breakdown,
            "largest_messages": sorted(breakdown, key=lambda x: -x["tokens"])[:5]
        }

    def suggest_optimizations(self, usage_info: dict) -> list[str]:
        """Предлагаем оптимизации при высоком usage"""
        suggestions = []

        if usage_info["is_near_limit"]:
            # Анализируем breakdown
            for msg in usage_info["largest_messages"]:
                if msg["tokens"] > 2000:
                    suggestions.append(
                        f"Large {msg['role']} message ({msg['tokens']} tokens): "
                        f"Consider summarizing or truncating"
                    )

            suggestions.append("Consider implementing conversation summarization")
            suggestions.append("Implement sliding window for message history")

        return suggestions
```

**Стратегии управления контекстом:**
```python
class ContextManager:
    """Умное управление контекстом"""

    def __init__(self, max_tokens: int, reserve_tokens: int = 1000):
        self.max_tokens = max_tokens
        self.reserve = reserve_tokens  # Для ответа модели
        self.available = max_tokens - reserve_tokens

    def smart_truncate(self, messages: list[dict]) -> list[dict]:
        """Умная обрезка с сохранением важного контекста"""
        # Всегда сохраняем: system prompt, последние N сообщений
        system = [m for m in messages if m["role"] == "system"]
        others = [m for m in messages if m["role"] != "system"]

        # Последние 5 сообщений — священны
        recent = others[-5:] if len(others) >= 5 else others
        older = others[:-5] if len(others) > 5 else []

        # Суммаризируем старые сообщения
        if older:
            summary = self.summarize_messages(older)
            summary_msg = {"role": "system", "content": f"Previous context summary: {summary}"}
            return system + [summary_msg] + recent

        return system + recent

    def summarize_messages(self, messages: list[dict]) -> str:
        """Суммаризация через LLM"""
        # Упрощённая версия — в production используйте LLM
        actions = []
        for m in messages:
            if m.get("tool_calls"):
                actions.append(f"Called {m['tool_calls'][0]['function']['name']}")
        return f"Previous actions: {', '.join(actions[-10:])}"
```

### Симптом 2: State corruption

**Что происходит:** Состояние агента становится inconsistent — содержит противоречивую информацию.

**Диагностика:**
```python
from pydantic import BaseModel, model_validator
from typing import Any

class AgentState(BaseModel):
    """Состояние агента с валидацией consistency"""
    messages: list[dict]
    current_task: str | None = None
    completed_tasks: list[str] = []
    tool_results: dict[str, Any] = {}
    error_count: int = 0

    @model_validator(mode='after')
    def check_consistency(self):
        # Текущая задача не должна быть в completed
        if self.current_task and self.current_task in self.completed_tasks:
            raise ValueError(
                f"Inconsistent state: '{self.current_task}' is both current and completed"
            )

        # Error count должен соответствовать реальным ошибкам
        actual_errors = sum(
            1 for m in self.messages
            if "error" in str(m.get("content", "")).lower()
        )
        if self.error_count < actual_errors:
            raise ValueError(
                f"Error count mismatch: recorded {self.error_count}, found {actual_errors}"
            )

        return self

class StateDebugger:
    def __init__(self):
        self.state_snapshots = []

    def snapshot(self, state: AgentState, step: int):
        """Сохраняем snapshot состояния"""
        self.state_snapshots.append({
            "step": step,
            "state": state.model_dump(),
            "hash": hash(str(state.model_dump()))
        })

    def find_corruption_point(self) -> int | None:
        """Находим момент когда состояние стало inconsistent"""
        for i, snapshot in enumerate(self.state_snapshots):
            try:
                AgentState(**snapshot["state"])
            except ValueError as e:
                return i, str(e)
        return None

    def diff_states(self, step1: int, step2: int) -> dict:
        """Сравниваем два состояния"""
        s1 = self.state_snapshots[step1]["state"]
        s2 = self.state_snapshots[step2]["state"]

        diff = {}
        for key in set(s1.keys()) | set(s2.keys()):
            if s1.get(key) != s2.get(key):
                diff[key] = {"before": s1.get(key), "after": s2.get(key)}

        return diff
```

### Симптом 3: Memory leaks (Long-term memory issues)

**Что происходит:** Долгосрочная память накапливает мусор или теряет важную информацию.

**Мониторинг памяти:**
```python
class MemoryHealthChecker:
    def __init__(self, memory_store):
        self.store = memory_store

    async def health_check(self) -> dict:
        """Проверяем здоровье памяти"""
        stats = {
            "total_entries": await self.store.count(),
            "stale_entries": 0,
            "duplicate_entries": 0,
            "orphan_entries": 0,
        }

        # Проверяем на stale (старые неиспользуемые)
        all_entries = await self.store.get_all()
        now = datetime.now()

        for entry in all_entries:
            # Stale: не использовалось > 30 дней
            if (now - entry.last_accessed).days > 30:
                stats["stale_entries"] += 1

            # Duplicates: похожий контент
            similar = await self.store.find_similar(entry.content, threshold=0.95)
            if len(similar) > 1:
                stats["duplicate_entries"] += 1

        stats["health_score"] = self._calculate_health_score(stats)
        return stats

    def _calculate_health_score(self, stats: dict) -> float:
        """Оценка здоровья памяти 0-1"""
        total = stats["total_entries"]
        if total == 0:
            return 1.0

        bad_ratio = (
            stats["stale_entries"] +
            stats["duplicate_entries"] +
            stats["orphan_entries"]
        ) / total

        return max(0, 1 - bad_ratio)
```

---

## Level 4: Orchestration Debugging

### Симптом 1: Infinite loops

**Что происходит:** Агент застревает в бесконечном цикле, повторяя одни и те же действия.

**Детекция и предотвращение:**
```python
from collections import Counter

class LoopDetector:
    def __init__(self, max_iterations: int = 25, loop_threshold: int = 3):
        self.max_iterations = max_iterations
        self.loop_threshold = loop_threshold
        self.action_history = []

    def record_action(self, action: dict) -> bool:
        """Записываем действие и проверяем на loop"""
        # Нормализуем action для сравнения
        action_key = self._normalize_action(action)
        self.action_history.append(action_key)

        # Проверяем на простой loop
        if self._detect_simple_loop():
            return True

        # Проверяем на cycle loop
        if self._detect_cycle_loop():
            return True

        # Проверяем на max iterations
        if len(self.action_history) >= self.max_iterations:
            return True

        return False

    def _normalize_action(self, action: dict) -> str:
        """Нормализуем action для сравнения"""
        if "tool" in action:
            return f"tool:{action['tool']}:{hash(str(action.get('args', {})))}"
        return f"message:{hash(action.get('content', '')[:100])}"

    def _detect_simple_loop(self) -> bool:
        """Обнаруживаем простой loop (AAA)"""
        if len(self.action_history) < self.loop_threshold:
            return False

        last_n = self.action_history[-self.loop_threshold:]
        return len(set(last_n)) == 1

    def _detect_cycle_loop(self) -> bool:
        """Обнаруживаем cycle loop (ABCABC)"""
        if len(self.action_history) < 6:
            return False

        # Проверяем паттерны длиной 2-5
        for pattern_len in range(2, 6):
            recent = self.action_history[-pattern_len * 2:]
            first_half = tuple(recent[:pattern_len])
            second_half = tuple(recent[pattern_len:])

            if first_half == second_half:
                return True

        return False

    def get_loop_info(self) -> dict:
        """Информация о обнаруженном loop"""
        counter = Counter(self.action_history[-10:])
        return {
            "total_actions": len(self.action_history),
            "recent_actions": self.action_history[-10:],
            "most_common": counter.most_common(3),
            "unique_ratio": len(set(self.action_history[-10:])) / min(10, len(self.action_history))
        }
```

**Интеграция в агента:**
```python
class AgentWithLoopProtection:
    def __init__(self, base_agent):
        self.agent = base_agent
        self.loop_detector = LoopDetector()

    async def run(self, task: str) -> str:
        while True:
            action = await self.agent.decide_next_action()

            if self.loop_detector.record_action(action):
                # Loop detected — intervention
                loop_info = self.loop_detector.get_loop_info()

                intervention_prompt = f"""
                WARNING: You appear to be stuck in a loop.
                Recent actions: {loop_info['recent_actions'][-5:]}

                Please:
                1. Acknowledge the loop
                2. Explain why you were repeating
                3. Choose a DIFFERENT approach
                """

                await self.agent.inject_message(intervention_prompt)
                self.loop_detector = LoopDetector()  # Reset
                continue

            result = await self.agent.execute_action(action)

            if self.agent.is_done:
                return result
```

### Симптом 2: Handoff failures

**Что происходит:** Передача между агентами происходит некорректно — теряется контекст или выбирается неверный агент.

**Диагностика handoffs:**
```python
class HandoffDebugger:
    def __init__(self):
        self.handoff_log = []

    def log_handoff(
        self,
        from_agent: str,
        to_agent: str,
        context_passed: dict,
        context_received: dict,
        reason: str
    ):
        self.handoff_log.append({
            "timestamp": datetime.now(),
            "from": from_agent,
            "to": to_agent,
            "context_passed": context_passed,
            "context_received": context_received,
            "reason": reason,
            "context_diff": self._diff_contexts(context_passed, context_received)
        })

    def _diff_contexts(self, passed: dict, received: dict) -> dict:
        """Находим что потерялось при передаче"""
        lost = {}
        for key in passed:
            if key not in received:
                lost[key] = {"status": "missing", "value": passed[key]}
            elif passed[key] != received[key]:
                lost[key] = {
                    "status": "modified",
                    "original": passed[key],
                    "received": received[key]
                }
        return lost

    def analyze_handoff_quality(self) -> dict:
        """Анализируем качество handoffs"""
        total = len(self.handoff_log)
        if total == 0:
            return {"status": "no_handoffs"}

        issues = [h for h in self.handoff_log if h["context_diff"]]

        return {
            "total_handoffs": total,
            "handoffs_with_issues": len(issues),
            "success_rate": (total - len(issues)) / total,
            "common_lost_fields": self._find_common_lost_fields(issues),
            "problematic_routes": self._find_problematic_routes()
        }

    def _find_common_lost_fields(self, issues: list) -> list:
        """Какие поля чаще всего теряются"""
        lost_fields = []
        for issue in issues:
            lost_fields.extend(issue["context_diff"].keys())
        return Counter(lost_fields).most_common(5)

    def _find_problematic_routes(self) -> list:
        """Какие маршруты передачи проблемные"""
        routes = []
        for h in self.handoff_log:
            if h["context_diff"]:
                routes.append(f"{h['from']} → {h['to']}")
        return Counter(routes).most_common(3)
```

---

## Level 5: Production Debugging

### Observability Stack для агентов

```
┌────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY STACK                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   TRACING   │  │   METRICS   │  │    LOGS     │        │
│  │             │  │             │  │             │        │
│  │ LangSmith   │  │ Prometheus  │  │ Structured  │        │
│  │ Arize       │  │ Datadog     │  │ JSON logs   │        │
│  │ Phoenix     │  │ Grafana     │  │ ELK Stack   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│                  ┌─────────────┐                           │
│                  │  DASHBOARD  │                           │
│                  │             │                           │
│                  │ • Latency   │                           │
│                  │ • Errors    │                           │
│                  │ • Costs     │                           │
│                  │ • Quality   │                           │
│                  └─────────────┘                           │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Интеграция с LangSmith

```python
from langsmith import traceable, Client
from langsmith.run_helpers import get_current_run_tree

# Настройка
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "agent-debugging"

client = Client()

@traceable(name="agent_task")
async def run_agent_task(task: str) -> str:
    """Выполняем задачу агента с полным tracing"""

    # Добавляем метаданные для debugging
    run = get_current_run_tree()
    run.metadata = {
        "task_type": classify_task(task),
        "expected_tools": predict_tools(task),
        "user_id": get_current_user(),
    }

    result = await agent.run(task)

    # Добавляем feedback для анализа
    run.outputs = {"result": result}

    return result

# Анализ traces
def analyze_failed_traces(project_name: str, days: int = 7):
    """Анализируем неудачные traces"""
    runs = client.list_runs(
        project_name=project_name,
        filter="has(error)",
        start_time=datetime.now() - timedelta(days=days)
    )

    error_patterns = {}
    for run in runs:
        error_type = classify_error(run.error)
        if error_type not in error_patterns:
            error_patterns[error_type] = {
                "count": 0,
                "examples": [],
                "common_inputs": []
            }
        error_patterns[error_type]["count"] += 1
        error_patterns[error_type]["examples"].append(run.id)
        error_patterns[error_type]["common_inputs"].append(run.inputs)

    return error_patterns
```

### Structured Logging для агентов

```python
import structlog
from typing import Any

# Настройка structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger()

class AgentLogger:
    def __init__(self, agent_id: str):
        self.log = log.bind(agent_id=agent_id)

    def log_step(
        self,
        step_type: str,
        step_number: int,
        details: dict[str, Any]
    ):
        self.log.info(
            "agent_step",
            step_type=step_type,
            step_number=step_number,
            **details
        )

    def log_tool_call(
        self,
        tool_name: str,
        params: dict,
        result: Any,
        latency_ms: float,
        success: bool
    ):
        self.log.info(
            "tool_call",
            tool_name=tool_name,
            params=params,
            result_preview=str(result)[:500],
            latency_ms=latency_ms,
            success=success
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: dict,
        recoverable: bool
    ):
        self.log.error(
            "agent_error",
            error_type=error_type,
            error_message=error_message,
            context=context,
            recoverable=recoverable
        )
```

### Metrics для Prometheus/Grafana

```python
from prometheus_client import Counter, Histogram, Gauge

# Определяем метрики
AGENT_TASKS_TOTAL = Counter(
    'agent_tasks_total',
    'Total number of agent tasks',
    ['agent_id', 'task_type', 'status']
)

AGENT_TASK_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Duration of agent tasks',
    ['agent_id', 'task_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

AGENT_TOOL_CALLS = Counter(
    'agent_tool_calls_total',
    'Total number of tool calls',
    ['agent_id', 'tool_name', 'status']
)

AGENT_TOKEN_USAGE = Counter(
    'agent_token_usage_total',
    'Total tokens used',
    ['agent_id', 'token_type']  # input, output
)

AGENT_ACTIVE_TASKS = Gauge(
    'agent_active_tasks',
    'Number of currently active agent tasks',
    ['agent_id']
)

# Использование
class InstrumentedAgent:
    def __init__(self, agent_id: str, base_agent):
        self.agent_id = agent_id
        self.agent = base_agent

    async def run(self, task: str, task_type: str = "general") -> str:
        AGENT_ACTIVE_TASKS.labels(agent_id=self.agent_id).inc()

        with AGENT_TASK_DURATION.labels(
            agent_id=self.agent_id,
            task_type=task_type
        ).time():
            try:
                result = await self.agent.run(task)
                AGENT_TASKS_TOTAL.labels(
                    agent_id=self.agent_id,
                    task_type=task_type,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                AGENT_TASKS_TOTAL.labels(
                    agent_id=self.agent_id,
                    task_type=task_type,
                    status="error"
                ).inc()
                raise
            finally:
                AGENT_ACTIVE_TASKS.labels(agent_id=self.agent_id).dec()
```

---

## Debugging Playbook: пошаговые чеклисты

### Playbook 1: "Агент даёт неправильный ответ"

```
□ 1. СБОР ИНФОРМАЦИИ
  □ Получить полный trace (LangSmith / logs)
  □ Записать: input, expected output, actual output
  □ Определить: воспроизводится ли баг стабильно?

□ 2. ЛОКАЛИЗАЦИЯ УРОВНЯ
  □ Проверить: правильно ли понята задача? (L1: LLM)
  □ Проверить: правильные ли tools выбраны? (L2: Tools)
  □ Проверить: корректен ли контекст? (L3: State)
  □ Проверить: правильная ли последовательность шагов? (L4: Orchestration)

□ 3. L1 DEBUGGING (если проблема в понимании)
  □ Добавить explicit reasoning (<thinking> tags)
  □ Упростить system prompt
  □ Добавить few-shot examples
  □ Снизить temperature

□ 4. L2 DEBUGGING (если проблема в tools)
  □ Проверить tool descriptions на ясность
  □ Проверить параметры tool calls
  □ Проверить что tool возвращает
  □ Добавить валидацию параметров

□ 5. L3 DEBUGGING (если проблема в контексте)
  □ Проверить context window usage
  □ Проверить memory на corrupted state
  □ Проверить не теряется ли информация

□ 6. ВЕРИФИКАЦИЯ ФИКСА
  □ Воспроизвести оригинальный баг
  □ Применить fix
  □ Проверить что баг исправлен
  □ Проверить регрессии (другие сценарии)
```

### Playbook 2: "Агент застрял / не завершается"

```
□ 1. ОПРЕДЕЛИТЬ ТИП ЗАСТРЕВАНИЯ
  □ Infinite loop (повторяет одно действие)?
  □ Cycle loop (повторяет последовательность)?
  □ Waiting (ждёт чего-то)?
  □ Error loop (ошибка → retry → ошибка)?

□ 2. ДЛЯ INFINITE/CYCLE LOOP
  □ Проверить последние 10 actions
  □ Определить паттерн
  □ Добавить loop detection
  □ Добавить max_iterations limit
  □ Добавить intervention prompt

□ 3. ДЛЯ WAITING
  □ Что ожидает агент?
  □ Tool timeout? → увеличить timeout или добавить fallback
  □ Human input? → проверить HITL конфигурацию
  □ External API? → проверить health API

□ 4. ДЛЯ ERROR LOOP
  □ Какая ошибка повторяется?
  □ Почему retry не помогает?
  □ Добавить exponential backoff
  □ Добавить circuit breaker
  □ Добавить fallback strategy

□ 5. ПРЕВЕНТИВНЫЕ МЕРЫ
  □ Добавить global timeout
  □ Добавить loop detection
  □ Добавить progress tracking
  □ Настроить alerting
```

### Playbook 3: "Production incident"

```
□ 1. IMMEDIATE RESPONSE (первые 5 минут)
  □ Определить severity (P1/P2/P3)
  □ Включить incident channel
  □ Если P1: рассмотреть circuit breaker / fallback

□ 2. ДИАГНОСТИКА (5-15 минут)
  □ Проверить dashboards: latency, error rate, throughput
  □ Проверить recent deployments
  □ Проверить external dependencies (LLM API status)
  □ Получить sample traces с ошибками

□ 3. CATEGORIZATION
  □ LLM API issue? → check status page, switch provider
  □ Tool failure? → identify tool, check external service
  □ Rate limiting? → check quotas, implement backoff
  □ Code bug? → identify commit, rollback if needed
  □ Data issue? → check input patterns

□ 4. MITIGATION
  □ Implement temporary fix or workaround
  □ Communicate status to stakeholders
  □ Monitor for improvement

□ 5. POST-INCIDENT (после стабилизации)
  □ Документировать timeline
  □ Root cause analysis
  □ Preventive measures
  □ Update runbooks
```

---

## Инструменты debugging

### Сравнение инструментов

| Инструмент | Тип | Strengths | Когда использовать |
|------------|-----|-----------|-------------------|
| **LangSmith** | Tracing + Eval | Глубокая интеграция с LangChain | LangChain/LangGraph проекты |
| **Arize Phoenix** | Observability | Open source, vector search analysis | Любые LLM проекты |
| **Weights & Biases** | ML Ops | Experiment tracking, prompts | R&D и experimentation |
| **Datadog LLM** | APM | Enterprise monitoring | Production enterprise |
| **Helicone** | Proxy + Logging | Простая интеграция | Быстрый старт |
| **Braintrust** | Eval + Debug | Evaluation focused | Quality assurance |

### Quick setup: минимальный debugging stack

```python
# Минимальный stack для debugging

# 1. Structured logging
import structlog
log = structlog.get_logger()

# 2. Simple tracing decorator
from functools import wraps
from time import time

def trace(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        trace_id = generate_trace_id()

        log.info("function_start",
                 function=func.__name__,
                 trace_id=trace_id,
                 args=str(args)[:200])

        try:
            result = await func(*args, **kwargs)
            log.info("function_end",
                     function=func.__name__,
                     trace_id=trace_id,
                     duration_ms=(time() - start) * 1000,
                     success=True)
            return result
        except Exception as e:
            log.error("function_error",
                      function=func.__name__,
                      trace_id=trace_id,
                      error=str(e),
                      duration_ms=(time() - start) * 1000)
            raise
    return wrapper

# 3. Применяем к агенту
@trace
async def agent_step(state: dict) -> dict:
    ...
```

---

## Типичные ошибки и решения

### Ошибка 1: "Агент игнорирует инструкции"

**СИМПТОМ:** System prompt говорит "отвечай кратко", агент пишет эссе.

**ПРИЧИНЫ:**
1. Инструкции в конце system prompt (теряются в длинном контексте)
2. Конфликтующие инструкции
3. Few-shot examples противоречат инструкциям

**РЕШЕНИЕ:**
```python
# ПЛОХО: инструкции в конце
system_prompt = """
You are a helpful assistant...
[много текста]
...
Be concise in your responses.
"""

# ХОРОШО: инструкции в начале + reinforcement
system_prompt = """
CRITICAL: Your responses must be CONCISE (max 3 sentences).

You are a helpful assistant...
[текст]

REMINDER: Keep responses under 3 sentences.
"""
```

### Ошибка 2: "Tool output игнорируется"

**СИМПТОМ:** Агент вызывает tool, но не использует результат.

**ПРИЧИНЫ:**
1. Tool output слишком длинный (обрезается)
2. Tool output плохо структурирован
3. Агент не понимает формат результата

**РЕШЕНИЕ:**
```python
# ПЛОХО: сырой output
def search_tool(query: str) -> str:
    results = api.search(query)
    return str(results)  # Гигантский JSON

# ХОРОШО: structured и summarized
def search_tool(query: str) -> str:
    results = api.search(query)

    # Форматируем для LLM
    formatted = f"""
    Search Results for "{query}":
    Found {len(results)} results.

    Top 3 results:
    1. {results[0]['title']}: {results[0]['snippet'][:200]}
    2. {results[1]['title']}: {results[1]['snippet'][:200]}
    3. {results[2]['title']}: {results[2]['snippet'][:200]}

    Use these results to answer the user's question.
    """
    return formatted
```

### Ошибка 3: "Агент вызывает несуществующий tool"

**СИМПТОМ:** Агент пытается вызвать tool которого нет.

**ПРИЧИНЫ:**
1. Галлюцинация на основе названий других tools
2. Tool был в training data модели
3. Описание задачи подразумевает tool

**РЕШЕНИЕ:**
```python
# Добавляем strict tool validation
class StrictToolRouter:
    def __init__(self, available_tools: list[str]):
        self.tools = set(available_tools)

    def validate_and_route(self, tool_call: dict) -> dict:
        tool_name = tool_call.get("name")

        if tool_name not in self.tools:
            # Находим ближайший существующий tool
            closest = self._find_closest_tool(tool_name)

            return {
                "status": "error",
                "message": f"Tool '{tool_name}' does not exist. "
                          f"Did you mean '{closest}'? "
                          f"Available tools: {list(self.tools)}"
            }

        return {"status": "ok", "tool": tool_name}

    def _find_closest_tool(self, name: str) -> str:
        from difflib import get_close_matches
        matches = get_close_matches(name, self.tools, n=1, cutoff=0.6)
        return matches[0] if matches else list(self.tools)[0]
```

---

## Чек-лист Production Readiness

```
DEBUGGING INFRASTRUCTURE
□ Tracing настроен (LangSmith / Phoenix / custom)
□ Structured logging с trace_id
□ Метрики экспортируются (latency, errors, tokens)
□ Dashboards созданы
□ Alerts настроены

ERROR HANDLING
□ Graceful degradation для tool failures
□ Circuit breakers для external APIs
□ Retry с exponential backoff
□ Fallback responses

SAFETY MECHANISMS
□ Loop detection
□ Max iterations limit
□ Global timeout
□ Input validation
□ Output sanitization

DEBUGGING CAPABILITIES
□ Можно воспроизвести любой trace
□ Можно replay failed requests
□ A/B testing infrastructure
□ Canary deployments

DOCUMENTATION
□ Runbooks для типичных проблем
□ Escalation procedures
□ On-call rotation
□ Post-mortem templates
```

---

## Связанные материалы

- [[ai-agents-advanced]] — философия и архитектура агентов
- [[agent-frameworks-comparison]] — сравнение фреймворков
- [[tutorial-ai-agent]] — практикум по созданию агента
- [[ai-observability-monitoring]] — observability для AI систем
- [[ai-security-safety]] — безопасность AI приложений
- [[ai-testing-evaluation]] — тестирование AI систем

---

*Создано: 2026-01-11*
