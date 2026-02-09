---
title: "AI Agents: автономные системы с tool use"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/ai-ml
  - agents
  - tool-use
  - autonomous-systems
  - type/concept
  - level/intermediate
related:
  - "[[ai-ml-overview]]"
  - "[[rag-and-prompt-engineering]]"
  - "[[ai-production-systems]]"
---

# AI Agents: автономные системы с tool use

> AI Agent = LLM + Tools + Memory + Planning. Модель не просто отвечает, а выполняет задачи автономно.

---

## TL;DR

- **Agent** — AI система, которая может планировать, использовать инструменты и действовать автономно
- **Ключевые компоненты:** LLM (мозг), Tools (руки), Memory (контекст), Planning (стратегия)
- **Use cases:** Coding assistants, data analysis, research, automation
- **Риски:** Непредсказуемость, стоимость, безопасность

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Agent** | AI система с возможностью автономных действий |
| **Tool Use** | Способность модели вызывать внешние функции |
| **Function Calling** | API механизм для tool use (OpenAI/Anthropic) |
| **ReAct** | Reasoning + Acting — паттерн "думай-действуй" |
| **Planning** | Декомпозиция задачи на шаги |
| **Multi-agent** | Несколько агентов, работающих вместе |
| **MCP** | Model Context Protocol — стандарт интеграции tools |
| **Orchestrator** | Агент, управляющий другими агентами |

---

## Архитектура AI Agent

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         AI AGENT ARCHITECTURE                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         ┌──────────────────┐                               │
│                         │      USER        │                               │
│                         │     Request      │                               │
│                         └────────┬─────────┘                               │
│                                  │                                          │
│                                  ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                         AGENT CORE                                 │    │
│  │                                                                    │    │
│  │   ┌────────────────────────────────────────────────────────────┐  │    │
│  │   │                      LLM (Brain)                           │  │    │
│  │   │                                                            │  │    │
│  │   │    1. Understand task                                      │  │    │
│  │   │    2. Plan steps                                           │  │    │
│  │   │    3. Decide which tool to use                             │  │    │
│  │   │    4. Interpret results                                    │  │    │
│  │   │    5. Continue or finish                                   │  │    │
│  │   │                                                            │  │    │
│  │   └────────────────────────────────────────────────────────────┘  │    │
│  │                              │                                     │    │
│  │              ┌───────────────┼───────────────┐                    │    │
│  │              ▼               ▼               ▼                    │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │    │
│  │   │    Memory    │  │    Tools     │  │   Planning   │          │    │
│  │   │              │  │              │  │              │          │    │
│  │   │ • Short-term │  │ • Search     │  │ • Task       │          │    │
│  │   │ • Long-term  │  │ • Code exec  │  │   decomp.    │          │    │
│  │   │ • Retrieved  │  │ • Database   │  │ • Strategy   │          │    │
│  │   │   context    │  │ • APIs       │  │   selection  │          │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘          │    │
│  │                                                                    │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                  │                                          │
│                                  ▼                                          │
│                         ┌──────────────────┐                               │
│                         │     Response     │                               │
│                         │    + Actions     │                               │
│                         └──────────────────┘                               │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## ReAct Pattern

ReAct (Reasoning + Acting) — основной паттерн работы агентов.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           ReAct LOOP                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Task: "Find the current weather in Tokyo and suggest what to wear"        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Thought 1: I need to find the current weather in Tokyo.             │   │
│  │            I should use the weather API tool.                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Action 1: weather_api(location="Tokyo")                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Observation 1: {"temp": 15, "condition": "cloudy", "rain": 30%}     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Thought 2: It's 15°C and cloudy with 30% chance of rain.            │   │
│  │            I have enough info to make clothing suggestions.          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Final Answer: "Tokyo is 15°C and cloudy. Wear a light jacket        │   │
│  │               and bring an umbrella just in case."                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Tool Use Implementation

### OpenAI Function Calling

```python
# ✅ Правильно: Tool definition with types
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
                        "description": "City name, e.g., 'Tokyo'"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Make request with tools
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"  # or "required" or specific tool
)

# Handle tool call
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    # Execute the actual function
    result = get_weather(**arguments)

    # Send result back to model
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    })

    # Get final response
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
```

### Anthropic Tool Use

```python
# ✅ Anthropic Claude tool definition
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Weather in Tokyo?"}]
)

# Handle tool use
for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_input = block.input
        tool_use_id = block.id

        # Execute tool
        result = execute_tool(tool_name, tool_input)

        # Continue conversation with result
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": str(result)
            }]
        })
```

---

## Agent Frameworks

### LangChain Agent

```python
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation
    return search_results

@tool
def run_python(code: str) -> str:
    """Execute Python code and return the output."""
    # Sandboxed execution
    return exec_result

# Create agent
llm = ChatOpenAI(model="gpt-4o")
tools = [search_web, run_python]

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,  # Prevent infinite loops
    handle_parsing_errors=True
)

# Run
result = agent_executor.invoke({
    "input": "Find Python adoption statistics and create a bar chart"
})
```

### CrewAI Multi-Agent

```python
from crewai import Agent, Task, Crew

# Define specialized agents
researcher = Agent(
    role="Research Analyst",
    goal="Find accurate and up-to-date information",
    backstory="Expert researcher with attention to detail",
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging and accurate content",
    backstory="Experienced technical writer",
    tools=[],
    llm=llm
)

# Define tasks
research_task = Task(
    description="Research the latest trends in AI agents",
    expected_output="Comprehensive research report with sources",
    agent=researcher
)

writing_task = Task(
    description="Write a blog post based on the research",
    expected_output="Engaging blog post, 1000 words",
    agent=writer,
    context=[research_task]  # Depends on research
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process="sequential",  # or "hierarchical"
    verbose=True
)

# Execute
result = crew.kickoff()
```

---

## Planning Strategies

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        PLANNING STRATEGIES                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ZERO-SHOT (No planning)                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Task → LLM → Action → Result                                       │   │
│  │  Simple, fast, but limited for complex tasks                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. PLAN-AND-EXECUTE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Task → Plan all steps → Execute step by step → Result              │   │
│  │                                                                      │   │
│  │  Plan:                                                               │   │
│  │  1. Search for data                                                  │   │
│  │  2. Process data                                                     │   │
│  │  3. Generate visualization                                           │   │
│  │  4. Write summary                                                    │   │
│  │                                                                      │   │
│  │  Good for: Predictable workflows                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. ReAct (ITERATIVE)                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Task → Think → Act → Observe → Think → Act → ... → Result          │   │
│  │                                                                      │   │
│  │  Flexible, adapts to observations                                   │   │
│  │  Good for: Dynamic tasks, unknown requirements                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. TREE OF THOUGHTS                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Task                                              │   │
│  │                      │                                               │   │
│  │         ┌────────────┼────────────┐                                 │   │
│  │         ▼            ▼            ▼                                 │   │
│  │     Approach A   Approach B   Approach C                            │   │
│  │         │            │            │                                 │   │
│  │      Evaluate     Evaluate     Evaluate                             │   │
│  │         │            │            │                                 │   │
│  │         └────────────┴─────┬──────┘                                 │   │
│  │                            ▼                                        │   │
│  │                    Best approach → Execute                          │   │
│  │                                                                      │   │
│  │  Good for: Complex decisions, exploration                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Memory Types

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    VectorStoreRetrieverMemory
)

# 1. Buffer Memory (full history)
# ✅ Simple, but grows unbounded
buffer_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 2. Summary Memory (compressed)
# ✅ Bounded size, but loses details
summary_memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history"
)

# 3. Vector Memory (semantic search)
# ✅ Retrieves relevant context
vector_memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )
)

# 4. Hybrid approach (recommended)
class HybridMemory:
    def __init__(self):
        self.short_term = []  # Last N messages
        self.long_term = VectorStore()  # Semantic search
        self.summary = ""  # Running summary

    def add(self, message):
        self.short_term.append(message)
        if len(self.short_term) > 10:
            # Summarize and move to long-term
            old = self.short_term.pop(0)
            self.long_term.add(old)
            self.update_summary()

    def get_context(self, query):
        relevant = self.long_term.search(query, k=3)
        return {
            "summary": self.summary,
            "recent": self.short_term[-5:],
            "relevant": relevant
        }
```

---

## Safety & Guardrails

```python
# ❌ Неправильно: No limits
agent.run(user_input)  # Could run forever, cost unlimited

# ✅ Правильно: With guardrails
class SafeAgent:
    def __init__(self, agent, config):
        self.agent = agent
        self.max_iterations = config.get("max_iterations", 10)
        self.max_cost = config.get("max_cost", 1.0)  # dollars
        self.allowed_tools = config.get("allowed_tools", [])
        self.blocked_actions = config.get("blocked_actions", [])

    def run(self, task: str) -> str:
        iterations = 0
        total_cost = 0

        while iterations < self.max_iterations:
            iterations += 1

            # Get next action
            action = self.agent.plan(task)

            # Validate action
            if not self._is_safe(action):
                return "Action blocked by safety policy"

            # Check cost
            estimated_cost = self._estimate_cost(action)
            if total_cost + estimated_cost > self.max_cost:
                return f"Cost limit reached: ${total_cost:.2f}"

            # Execute
            result = self.agent.execute(action)
            total_cost += estimated_cost

            if action.is_final:
                return result

        return "Max iterations reached"

    def _is_safe(self, action) -> bool:
        # Check tool is allowed
        if action.tool not in self.allowed_tools:
            return False

        # Check for blocked patterns
        for pattern in self.blocked_actions:
            if pattern in str(action):
                return False

        return True
```

### Common Safety Measures

| Measure | Description | Implementation |
|---------|-------------|----------------|
| **Iteration limit** | Max steps agent can take | `max_iterations=10` |
| **Cost limit** | Max $ to spend | Track token usage |
| **Tool whitelist** | Only allowed tools | `allowed_tools=[...]` |
| **Action approval** | Human confirms actions | Callback before execute |
| **Sandboxing** | Isolated execution | Docker, VM |
| **Output filtering** | Block sensitive data | Regex, classifiers |

---

## Multi-Agent Patterns

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-AGENT PATTERNS                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. SEQUENTIAL (Pipeline)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │   Agent A ──▶ Agent B ──▶ Agent C ──▶ Result                        │   │
│  │                                                                      │   │
│  │   Example: Research → Write → Review                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. HIERARCHICAL (Manager)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ┌──────────────┐                                 │   │
│  │                    │  Orchestrator │                                 │   │
│  │                    │   (Manager)   │                                 │   │
│  │                    └──────┬───────┘                                 │   │
│  │           ┌───────────────┼───────────────┐                         │   │
│  │           ▼               ▼               ▼                         │   │
│  │     ┌─────────┐     ┌─────────┐     ┌─────────┐                    │   │
│  │     │ Agent A │     │ Agent B │     │ Agent C │                    │   │
│  │     │(Search) │     │ (Code)  │     │(Review) │                    │   │
│  │     └─────────┘     └─────────┘     └─────────┘                    │   │
│  │                                                                      │   │
│  │   Manager delegates, aggregates results                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. COLLABORATIVE (Debate)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │     Agent A ◀────────────────────▶ Agent B                          │   │
│  │        │                               │                            │   │
│  │        └───────────┬───────────────────┘                            │   │
│  │                    ▼                                                │   │
│  │              ┌─────────┐                                            │   │
│  │              │ Judge   │                                            │   │
│  │              └─────────┘                                            │   │
│  │                                                                      │   │
│  │   Agents debate, judge decides                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Production Considerations

### Cost Management

```python
# Token tracking
class CostTracker:
    PRICES = {
        "gpt-4o": {"input": 0.0025, "output": 0.01},  # per 1K tokens
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "claude-sonnet": {"input": 0.003, "output": 0.015}
    }

    def __init__(self):
        self.total_cost = 0
        self.calls = []

    def track(self, model: str, input_tokens: int, output_tokens: int):
        prices = self.PRICES[model]
        cost = (input_tokens * prices["input"] +
                output_tokens * prices["output"]) / 1000
        self.total_cost += cost
        self.calls.append({
            "model": model,
            "input": input_tokens,
            "output": output_tokens,
            "cost": cost
        })
        return cost

# Use cheaper models for simple steps
def smart_routing(task_complexity: str) -> str:
    if task_complexity == "simple":
        return "gpt-4o-mini"  # 10x cheaper
    elif task_complexity == "medium":
        return "gpt-4o"
    else:
        return "claude-sonnet"  # Best for complex reasoning
```

### Observability

```python
# LangSmith integration for tracing
import langsmith

# Every agent call is traced
with langsmith.trace("agent_execution") as trace:
    trace.log_input({"task": task})

    for step in agent.run(task):
        trace.log_step({
            "thought": step.thought,
            "action": step.action,
            "observation": step.observation
        })

    trace.log_output({"result": result})
```

---

## Проверь себя

<details>
<summary>1. В чём разница между ReAct и Plan-and-Execute?</summary>

**Ответ:**

**Plan-and-Execute:**
- Сначала создаёт полный план
- Затем выполняет шаг за шагом
- Менее гибкий, но предсказуемый
- Хорош для известных workflow

**ReAct:**
- Чередует Thought → Action → Observation
- Адаптируется к результатам
- Более гибкий, но может "застрять"
- Хорош для exploratory задач

**Когда что:**
- Известный процесс → Plan-and-Execute
- Неизвестный/динамический → ReAct

</details>

<details>
<summary>2. Какие меры безопасности критичны для production агентов?</summary>

**Ответ:**

1. **Iteration limit** — предотвращает бесконечные циклы
2. **Cost limit** — контроль расходов
3. **Tool whitelist** — только разрешённые инструменты
4. **Sandboxing** — изоляция выполнения кода
5. **Human-in-the-loop** — подтверждение критичных действий
6. **Output filtering** — блокировка sensitive данных
7. **Audit logging** — запись всех действий

**Правило:** Никогда не давай агенту неограниченный доступ.

</details>

<details>
<summary>3. Как выбрать между single agent и multi-agent?</summary>

**Ответ:**

**Single agent:**
- Простая задача
- Требуется скорость
- Ограниченный бюджет
- Важна предсказуемость

**Multi-agent:**
- Задача требует разных "экспертиз"
- Важна верификация (агент проверяет агента)
- Параллельная обработка
- Сложные workflow с ветвлением

**Совет:** Начни с single agent, усложняй только если нужно.

</details>

<details>
<summary>4. Что такое MCP и зачем он нужен?</summary>

**Ответ:**

**MCP (Model Context Protocol)** — стандарт от Anthropic для интеграции tools с LLM.

**Проблема до MCP:**
- Каждый framework свой формат tools
- Сложно переиспользовать интеграции
- Дублирование кода

**Что даёт MCP:**
- Единый стандарт описания tools
- Готовые серверы для популярных сервисов
- Переносимость между LLM providers
- Безопасность и изоляция

**Аналогия:** MCP для AI tools — как USB для устройств.

</details>

---

## Связи

- [[ai-ml-overview]] — обзор AI Engineering
- [[rag-and-prompt-engineering]] — RAG и промпты
- [[ai-production-systems]] — деплой AI систем
- [[architecture-distributed-systems]] — распределённые системы

---

## Источники

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/) — документация
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use) — Claude tools
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [CrewAI](https://github.com/joaomdmoura/crewAI) — multi-agent framework
- [ReAct Paper](https://arxiv.org/abs/2210.03629) — оригинальная статья

---

*Проверено: 2025-12-22*

---

*Проверено: 2026-01-09*
