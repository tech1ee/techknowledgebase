# Сравнение Agent Frameworks: Полное руководство 2025

> Глубокий анализ фреймворков для построения AI-агентов: архитектура, философия, практическое применение

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание AI Agents** | Что такое агенты, зачем нужны | [[ai-agents-advanced]] |
| **Tool Use / Function Calling** | Основа всех фреймворков | [[structured-outputs-tools]] |
| **Python** | Все фреймворки на Python | Любой курс Python |
| **Async программирование** | Агенты работают асинхронно | Python asyncio |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Сложно | Сначала [[ai-agents-advanced]] |
| **AI Engineer** | ✅ Да | Выбор фреймворка под задачу |
| **Tech Lead** | ✅ Да | Архитектурные решения |
| **Backend Developer** | ✅ Да | Интеграция агентов |

### Терминология для новичков

> 💡 **Agent Framework** = библиотека/SDK для создания AI-агентов (не писать с нуля)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **LangGraph** | Graph-based orchestration от LangChain | **Диаграмма состояний** — агент как граф переходов |
| **CrewAI** | Multi-agent с ролями | **Команда специалистов** — каждый агент со своей ролью |
| **OpenAI Agents SDK** | Production-ready от OpenAI | **Официальный набор** — от создателей GPT |
| **Pydantic AI** | Type-safe agents | **Строгая типизация** — ошибки на этапе компиляции |
| **Handoff** | Передача между агентами | **Эстафета** — один агент передаёт другому |
| **State Machine** | Управление состоянием | **Диаграмма переходов** — что после чего |
| **Orchestration** | Координация агентов | **Дирижёр** — кто когда играет |
| **MCP** | Model Context Protocol | **USB для агентов** — стандарт подключения к сервисам |

---

## Оглавление

1. [Введение и контекст 2025](#введение-и-контекст-2025)
2. [Эволюция Agent Frameworks](#эволюция-agent-frameworks)
3. [LangGraph](#langgraph)
4. [CrewAI](#crewai)
5. [OpenAI Agents SDK](#openai-agents-sdk)
6. [Pydantic AI](#pydantic-ai)
7. [AutoGen / Microsoft Agent Framework](#autogen--microsoft-agent-framework)
8. [LlamaIndex Agents](#llamaindex-agents)
9. [SmolAgents (HuggingFace)](#smolagents-huggingface)
10. [DSPy (Stanford)](#dspy-stanford)
11. [Agno (ex-Phidata)](#agno-ex-phidata)
12. [Google ADK](#google-adk)
13. [Amazon Bedrock AgentCore](#amazon-bedrock-agentcore)
14. [BeeAI (IBM)](#beeai-ibm)
15. [Atomic Agents](#atomic-agents)
16. [Сравнительная таблица](#сравнительная-таблица)
17. [Критерии выбора](#критерии-выбора)
18. [Emerging Standards: MCP и A2A](#emerging-standards-mcp-и-a2a)
19. [Заключение](#заключение)

---

## Введение и контекст 2025

2025 год стал переломным для AI-агентов. По данным Gartner, к 2028 году около **33% enterprise-приложений** будут включать agentic AI capabilities (по сравнению с менее чем 1% в 2024). Рынок AI-агентов достиг **$7.6 млрд** в 2025 году с прогнозируемым ежегодным ростом **49.6%**.

### Что такое AI Agent?

**AI Agent** - это автономная система на базе LLM, способная:
- Понимать инструкции на естественном языке
- Планировать последовательность действий
- Использовать инструменты (tools) для взаимодействия с внешним миром
- Принимать решения на основе контекста
- Итеративно улучшать результаты

### Ключевые термины

| Термин | Описание |
|--------|----------|
| **Agentic AI** | AI-системы с автономией: планируют, используют tools, оценивают результаты |
| **Multi-agent systems** | Системы из нескольких специализированных агентов |
| **Orchestration** | Координация между агентами |
| **State Machine** | Граф состояний для управления потоком |
| **Tool Calling** | Способность агента вызывать внешние функции |
| **Human-in-the-Loop (HITL)** | Участие человека в процессе принятия решений |
| **Handoff** | Передача управления между агентами |
| **Checkpointing** | Сохранение состояния для recovery |

---

## Эволюция Agent Frameworks

### Timeline ключевых релизов

```
2022 Февраль   - Начало исследований DSPy в Stanford NLP
2022 Октябрь   - Релиз LangChain
2023 Сентябрь  - Microsoft выпускает AutoGen
2023 Ноябрь    - OpenAI анонсирует Assistants API
2024 Январь    - Официальный запуск CrewAI
2024 Октябрь   - IBM выпускает Bee Agent Framework
2024 Ноябрь    - Релиз Pydantic AI
2024 Декабрь   - HuggingFace представляет SmolAgents
2025 Январь    - AutoGen 0.4 с новой архитектурой
2025 Март      - OpenAI Agents SDK (замена Swarm)
2025 Апрель    - Google ADK на Cloud NEXT 2025
2025 Октябрь   - Microsoft Agent Framework (слияние AutoGen + Semantic Kernel)
2025 Декабрь   - LangGraph 1.0 и LangChain 1.0, Pydantic AI v1.39
```

### Три поколения фреймворков

**Поколение 1 (2022-2023)**: Линейные chains
- LangChain как пионер
- Последовательная обработка
- Ограниченный state management

**Поколение 2 (2023-2024)**: Multi-agent systems
- AutoGen, CrewAI
- Ролевые агенты
- Коллаборативное решение задач

**Поколение 3 (2024-2025)**: Production-ready frameworks
- LangGraph 1.0, OpenAI Agents SDK
- Stateful execution
- Human-in-the-loop
- Enterprise observability
- Cloud provider solutions (Bedrock, ADK)

---

## LangGraph

### История и философия

LangGraph создан командой LangChain как ответ на ограничения линейных chains. **LangGraph 1.0** достиг production-ready статуса в декабре 2025.

> "State machines для AI-агентов" - превращение хаотичного поведения агентов в контролируемые, наблюдаемые системы.

Философия: **явное лучше неявного**. Агент моделируется как конечный автомат с узлами (nodes), ребрами (edges) и состоянием (state).

### Архитектура

LangGraph построен на концепции **StateGraph**:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]
    current_step: str

def research_node(state: State):
    return {"messages": ["Research completed"], "current_step": "analyze"}

def analyze_node(state: State):
    return {"messages": ["Analysis done"], "current_step": "report"}

# Создание графа
workflow = StateGraph(State)
workflow.add_node("research", research_node)
workflow.add_node("analyze", analyze_node)
workflow.add_edge(START, "research")
workflow.add_edge("research", "analyze")
workflow.add_edge("analyze", END)

# Компиляция с checkpointer для persistence
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# Запуск с thread_id для сохранения состояния
config = {"configurable": {"thread_id": "session_1"}}
result = graph.invoke({"messages": [], "current_step": "start"}, config)
```

### Ключевые возможности

#### 1. Persistence и Checkpointing

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Production-ready persistence
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
)
graph = workflow.compile(checkpointer=checkpointer)

# Time-travel: откат к предыдущему состоянию
previous_state = graph.get_state(
    {"configurable": {"thread_id": "1", "checkpoint_id": "checkpoint_123"}}
)
```

Возможности:
- **Human-in-the-loop**: Прерывание для подтверждения
- **Memory**: Сохранение контекста между сессиями
- **Time-travel**: Откат и воспроизведение
- **Fault-tolerance**: Восстановление после сбоев

#### 2. Conditional Edges

```python
def should_continue(state: State) -> str:
    if state["confidence"] > 0.8:
        return "execute"
    elif state["retries"] < 3:
        return "retry"
    return "fallback"

workflow.add_conditional_edges(
    "analyze",
    should_continue,
    {"execute": "execute_node", "retry": "research", "fallback": "human_review"}
)
```

#### 3. Cross-Thread Memory (Store)

```python
from langgraph.store.redis import RedisStore

# Долгосрочная память между сессиями
store = RedisStore(redis_url="redis://localhost:6379")
graph = workflow.compile(checkpointer=checkpointer, store=store)
```

### Enterprise Case Studies

| Компания | Use Case | Результат |
|----------|----------|-----------|
| **LinkedIn** | AI Recruiter, SQL Bot | Hierarchical agent system для hiring |
| **Uber** | Code migrations | Автоматизация unit test generation |
| **Klarna** | Customer support | 80% сокращение времени resolution |
| **Elastic** | Threat detection | Real-time security agent network |
| **AppFolio** | Realm-X copilot | 2x accuracy, 10+ часов/неделю экономии |

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Полный контроль над потоком | Крутая кривая обучения |
| Встроенный checkpointing | State должен быть определен заранее |
| Самый быстрый по latency | Больше boilerplate кода |
| Интеграция с LangSmith | Документация отстает от развития |
| API stability (1.0) | |

---

## CrewAI

### История и философия

CrewAI создан Joao Moura в январе 2024 года. Философия:

> "Become a Multi-Agent Expert in Hours" - multi-agent разработка через role-based подход.

CrewAI **независим от LangChain** - standalone Python framework с **100,000+ certified developers**.

**Статистика:**
- 1.4 миллиарда agentic automations
- 60%+ Fortune 500 компаний
- 150 enterprise customers за первые 6 месяцев

### Ключевые концепции

| Компонент | Описание |
|-----------|----------|
| **Agents** | Специалисты с role, goal, backstory |
| **Tasks** | Конкретные задания с expected_output |
| **Crews** | Команды агентов |
| **Flows** | Event-driven оркестрация |

### Crews vs Flows

| Crews | Flows |
|-------|-------|
| Автономное сотрудничество | Event-driven workflows |
| Параллельное выполнение | Линейный/ветвящийся процесс |
| Inter-agent communication | Precise execution control |
| Role-based delegation | State management |

### Пример: Crew

```python
from crewai import Agent, Crew, Process, Task

analyst = Agent(
    role="Senior Market Analyst",
    goal="Conduct deep market analysis with expert insight",
    backstory="You're a veteran analyst known for identifying subtle market patterns",
    verbose=True
)

researcher = Agent(
    role="Data Researcher",
    goal="Gather and validate supporting market data",
    backstory="You excel at finding and correlating multiple data sources"
)

analysis_task = Task(
    description="Analyze {sector} sector data for the past {timeframe}",
    expected_output="Detailed market analysis with confidence score",
    agent=analyst
)

research_task = Task(
    description="Find supporting data to validate the analysis",
    expected_output="Corroborating evidence and potential contradictions",
    agent=researcher
)

crew = Crew(
    agents=[analyst, researcher],
    tasks=[analysis_task, research_task],
    process=Process.sequential,
    verbose=True,
    memory=True
)

result = crew.kickoff(inputs={"sector": "tech", "timeframe": "1W"})
```

### Пример: Flow с интеграцией Crew

```python
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel

class MarketState(BaseModel):
    sentiment: str = "neutral"
    confidence: float = 0.0
    recommendations: list = []

class MarketAnalysisFlow(Flow[MarketState]):

    @start()
    def fetch_market_data(self):
        self.state.sentiment = "analyzing"
        return {"sector": "tech", "timeframe": "1W"}

    @listen(fetch_market_data)
    def analyze_with_crew(self, market_data):
        result = crew.kickoff(inputs=market_data)
        self.state.confidence = 0.85
        return result

    @router(analyze_with_crew)
    def determine_next_steps(self):
        if self.state.confidence > 0.8:
            return "high_confidence"
        return "low_confidence"

    @listen("high_confidence")
    def execute_strategy(self):
        return strategy_crew.kickoff()
```

### CrewAI AOP (Agent Operations Platform)

Первая платформа для agents в production - "the OS for agents in production".

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Быстрый старт (POC за часы) | Logging сложен для debugging |
| Интуитивная role-based модель | Не для real-time interaction |
| 5.76x быстрее LangGraph (в некоторых cases) | Routing иногда к неправильному агенту |
| Встроенная memory система | Менее гибкий для complex logic |

---

## OpenAI Agents SDK

### История и философия

OpenAI Agents SDK выпущен в марте 2025 как **production-ready замена Swarm**.

> Минимализм и ergonomics - всего 4 core primitives.

### Core Primitives

1. **Agents** - LLMs с instructions и tools
2. **Handoffs** - делегирование между агентами
3. **Guardrails** - валидация input/output
4. **Sessions** - автоматическое сохранение history

### Пример

```python
from openai.agents import Agent, Runner

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22C, sunny"

@function_tool
def book_flight(origin: str, destination: str, date: str) -> str:
    """Book a flight."""
    return f"Flight booked: {origin} -> {destination}"

weather_agent = Agent(
    name="weather_assistant",
    instructions="Answer weather questions.",
    tools=[get_weather]
)

travel_agent = Agent(
    name="travel_assistant",
    instructions="Help with travel bookings.",
    tools=[book_flight]
)

triage_agent = Agent(
    name="triage",
    instructions="Route to appropriate specialist.",
    handoffs=[weather_agent, travel_agent]
)

runner = Runner()
result = runner.run(
    agent=triage_agent,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}]
)
```

### Ключевые особенности

- **Function tools**: Любая Python функция = tool
- **Built-in tracing**: Визуализация и debugging
- **Provider-agnostic**: 100+ LLMs через LiteLLM
- **TypeScript support**: Полноценный SDK

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Минимальный порог входа | Нет state management |
| Встроенный tracing | Нет memory |
| Отличная производительность | Ограниченный orchestration |
| Provider-agnostic | Молодая экосистема |

---

## Pydantic AI

### История и философия

Pydantic AI создан командой Pydantic (Samuel Colvin). Версия **v1.39.0** достигла Production/Stable в декабре 2025.

> "Bring that FastAPI feeling to GenAI app development"

### Ключевые возможности

- **Model Agnostic**: OpenAI, Anthropic, Gemini, Ollama, 100+ providers
- **Type Safety**: Полная типизация с IDE support
- **Observability**: Pydantic Logfire (OpenTelemetry)
- **Structured Outputs**: Гарантированная валидация
- **MCP, A2A Integration**: Model Context Protocol, Agent2Agent
- **Durable Execution**: Persistence across failures

### Пример

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent(
    'openai:gpt-4o',
    output_type=CityLocation,
    system_prompt='Extract location information.'
)

result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)  # city='London' country='United Kingdom'
```

### Structured Output с валидацией

```python
from pydantic_ai import Agent, ToolOutput, NativeOutput

class ProductRecommendation(BaseModel):
    product_name: str
    price: float
    reasoning: str

# ToolOutput: модель вызывает tool
tool_agent = Agent('openai:gpt-4o', output_type=ToolOutput(ProductRecommendation))

# NativeOutput: native structured output (быстрее)
native_agent = Agent('openai:gpt-4o', output_type=NativeOutput(ProductRecommendation))
```

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Самый быстрый execution | Не для free-form text |
| A+ state management | Overhead на схемы |
| Type safety из коробки | Требует понимания Pydantic |
| Отличная документация | |

---

## AutoGen / Microsoft Agent Framework

### Эволюция

- **2023 Сентябрь**: AutoGen v0.1
- **2025 Январь**: AutoGen v0.4 - полный редизайн
- **2025 Октябрь**: Microsoft Agent Framework (слияние с Semantic Kernel)

### AutoGen 0.4 Архитектура

Ключевые изменения:
- **Actor Model**: Event-driven, distributed agents
- **Asynchronous Messaging**: Event-driven и request/response
- **Modular Design**: Pluggable components
- **Cross-Language**: Python и .NET

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

planner = AssistantAgent(
    "planner",
    model_client=OpenAIChatCompletionClient(model="gpt-4"),
    description="Plans travel itineraries",
    system_message="You suggest travel plans."
)

researcher = AssistantAgent(
    "researcher",
    model_client=OpenAIChatCompletionClient(model="gpt-4"),
    description="Researches local activities"
)

termination = TextMentionTermination("TERMINATE")
team = RoundRobinGroupChat(
    participants=[planner, researcher],
    termination_condition=termination
)

result = await team.run(task="Plan a 3-day trip to Tokyo")
```

### Microsoft Agent Framework (Октябрь 2025)

> "Agent Framework is the next generation of both Semantic Kernel and AutoGen"

Объединение:
- Simple abstractions от AutoGen
- Enterprise-grade features от Semantic Kernel
- Thread-based state management
- Type safety, filters, telemetry

**Backwards compatibility**: Существующие workloads safe.

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| 45,000+ GitHub stars | Сложность абстракций |
| Distributed architecture | Transition к Agent Framework |
| Microsoft backing | Documentation fragmentation |
| Cross-language support | |

---

## LlamaIndex Agents

### Философия

> "The leading framework for building LLM-powered agents over your data"

LlamaIndex начинался как data framework для RAG, эволюционировал в agent платформу.

### Workflows 1.0 (Июнь 2025)

```python
from llama_index.core.agent import FunctionAgent
from llama_index.core.tools import FunctionTool

def search_web(query: str) -> str:
    return "Search results..."

def calculate(expression: str) -> float:
    return eval(expression)

agent = FunctionAgent.from_tools(
    tools=[
        FunctionTool.from_defaults(fn=search_web),
        FunctionTool.from_defaults(fn=calculate)
    ],
    llm=llm,
    verbose=True
)

response = agent.chat("What is 15% of Tokyo's population?")
```

### Multi-Agent Systems (llama-agents)

```python
from llama_agents import AgentService, ControlPlaneServer

research_service = AgentService(
    agent=research_agent,
    message_queue=message_queue,
    service_name="research"
)

control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=orchestrator
)
```

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Лучший для data-heavy workflows | Менее intuitive для простых agents |
| Native RAG интеграция | Фокус на data избыточен для simple cases |
| Day-zero support новых моделей | |

---

## SmolAgents (HuggingFace)

### Философия

> "Agents that think in code" - minimalist library (~1000 строк кода)

Successor transformers.agents, CodeAgent как primary paradigm.

### Ключевые особенности

- **Code Agents**: 30% меньше шагов vs standard tool-calling
- **Multi-modal**: Text, vision, audio
- **Security**: Sandboxed execution (E2B, Modal, Docker)
- **Model Agnostic**: Любой LLM через LiteLLM

```python
from smolagents import CodeAgent, tool, LiteLLMModel

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22C, sunny"

model = LiteLLMModel(model_id="gpt-4o")
agent = CodeAgent(tools=[get_weather], model=model)

result = agent.run("What's the weather in Paris?")
```

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Минималистичный | Менее enterprise features |
| Hub integration | Молодая экосистема |
| CLI tools | |

---

## DSPy (Stanford)

### Философия

> "Programming—not prompting—language models"

DSPy начался в Stanford NLP в феврале 2022. Вместо brittle prompts - compositional Python code.

### Core Concepts

```python
import dspy

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""
    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)
```

### Optimizers

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=answer_exact_match)
compiled_rag = optimizer.compile(RAG(), trainset=trainset)
```

**Результаты:**
- Outperforms few-shot prompting за минуты
- 770M T5 конкурирует с GPT-3.5
- 250+ contributors

### Плюсы и минусы

| Преимущества | Недостатки |
|--------------|------------|
| Programmatic approach | Другая парадигма |
| Automatic optimization | Требует training data |
| Academic backing | |

---

## Agno (ex-Phidata)

### Философия

> "Simple, fast, and truly model-agnostic"

Phidata переименован в Agno - lightweight framework с 18.5k+ GitHub stars.

### Ключевые особенности

- **Privacy First**: AgentOS в вашем cloud
- **Multi-Modal**: Любой model, любой provider
- **Performance**: Optimized для скорости

```python
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGo

agent = Agent(
    name="Web Agent",
    model="openai:gpt-4o",
    tools=[DuckDuckGo()],
    instructions="Search the web for information."
)

response = agent.run("What's happening in AI today?")
```

---

## Google ADK

### Agent Development Kit

Анонсирован на **Cloud NEXT 2025** - open-source framework для multi-agent development.

### Ключевые особенности

- **Multi-agent design**: Hierarchical agent composition
- **Rich tool ecosystem**: MCP support, 3rd-party integrations
- **LiteLLM integration**: 100+ models
- **Workflow Agents**: SequentialAgent, ParallelAgent, LoopAgent
- **Bidirectional streaming**: Audio/video

```python
from google.adk import Agent, SequentialAgent

research_agent = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    tools=[search_tool]
)

workflow = SequentialAgent(
    agents=[research_agent, analysis_agent, report_agent]
)
```

### Deployment

Google рекомендует **Vertex AI Agent Engine Runtime** для production.

---

## Amazon Bedrock AgentCore

### Production Platform для Enterprise

Bedrock AgentCore - agentic platform для building, deploying, operating agents.

### 2025 Features

- **Policy**: Natural language boundaries для agent actions
- **Evaluations**: 13 built-in evaluators
- **Memory**: Episodic learning
- **Multi-agent collaboration**: GA в марте 2025

### Enterprise Adoption

Компании: Amazon, PwC, NTT Data, MongoDB, Thomson Reuters, Workday, S&P Global.

### Strands Agents SDK

Open-source Python SDK с native MCP integration.

---

## BeeAI (IBM)

### Overview

BeeAI Framework - open-source под Linux Foundation для production-grade multi-agent systems.

### Agent Communication Protocol (ACP)

Построен на Anthropic's MCP, добавляет:
- Agent discovery
- Cross-framework communication
- Run agents from any framework

```python
from beeai import Agent

agent = Agent(
    model="granite-3.1-8b",
    tools=[aider, gpt_researcher]
)
```

### Поддерживаемые providers

- Anthropic Claude, OpenAI GPT, DeepSeek
- IBM watsonx, Meta Llama (via Ollama)
- Agents from LangChain и других frameworks

---

## Atomic Agents

### Философия

> "Atomicity - маленькие, reusable components"

Lightweight framework от BrainBlend AI на базе Instructor и Pydantic.

### Core Concepts

```python
from atomic_agents import Agent

agent = Agent(
    system_prompt="You are a helpful assistant.",
    input_schema=InputSchema,
    output_schema=OutputSchema
)
```

### Ключевые особенности

- **Modularity**: Single-purpose components
- **Predictability**: Clear input/output schemas
- **Control**: Fine-tune каждой части
- **Multiple providers**: OpenAI, Anthropic, Groq, Ollama

Версия: 2.5.0

---

## Сравнительная таблица

### Overview

| Framework | Компания | Focus | Learning Curve | Production | Multi-Agent | Stars |
|-----------|----------|-------|----------------|------------|-------------|-------|
| **LangGraph** | LangChain | Stateful workflows | High | Yes (1.0) | Yes | 8k+ |
| **CrewAI** | CrewAI Inc | Role-based teams | Low | Yes | Yes | 25k+ |
| **OpenAI SDK** | OpenAI | Minimalist agents | Low | Yes | Limited | 11k+ |
| **Pydantic AI** | Pydantic | Type-safe agents | Low | Yes (1.39) | Limited | 7k+ |
| **AutoGen** | Microsoft | Conversational | Medium | Transitioning | Yes | 45k+ |
| **LlamaIndex** | LlamaIndex | Data-centric | Medium | Yes | Yes | 40k+ |
| **SmolAgents** | HuggingFace | Code agents | Low | Yes | Yes | 15k+ |
| **DSPy** | Stanford | Programming LMs | High | Research | Limited | 20k+ |
| **Agno** | Agno AGI | Multi-modal | Low | Yes | Yes | 18k+ |
| **Google ADK** | Google | Multi-agent | Medium | Yes | Yes | New |
| **Bedrock** | AWS | Enterprise | Medium | Yes | Yes | N/A |
| **BeeAI** | IBM | ACP Protocol | Medium | Yes | Yes | New |

### Performance

| Framework | Latency | Token Efficiency | Complex Tasks |
|-----------|---------|------------------|---------------|
| LangGraph | Fastest | High | Excellent |
| CrewAI | Fast | Medium | Good |
| Pydantic AI | Fastest | High | Good |
| Agno | Fastest | High | Good |
| AutoGen | Medium | Medium | Excellent |
| LangChain | Slowest | Low | Medium |

---

## Критерии выбора

### Decision Tree

```
Какой ваш primary use case?
│
├─ Rapid prototyping / POC
│   └─ CrewAI или Pydantic AI
│
├─ Complex stateful workflows
│   └─ LangGraph
│
├─ Multi-agent collaboration
│   ├─ Role-based teams → CrewAI
│   ├─ Conversational → AutoGen
│   └─ Data-heavy → LlamaIndex
│
├─ Type-safe, maintainable code
│   └─ Pydantic AI
│
├─ Enterprise production
│   ├─ AWS ecosystem → Bedrock AgentCore
│   ├─ Google ecosystem → ADK
│   ├─ Microsoft ecosystem → Agent Framework
│   └─ Vendor-agnostic → LangGraph
│
├─ Research / Optimization
│   └─ DSPy
│
└─ Minimalist approach
    └─ OpenAI SDK или SmolAgents
```

### По Use Cases

| Use Case | Рекомендация | Альтернатива |
|----------|--------------|--------------|
| Customer support | CrewAI | LangGraph |
| Code generation | SmolAgents | Pydantic AI |
| Research automation | LlamaIndex | DSPy |
| Enterprise workflows | LangGraph | Bedrock AgentCore |
| Quick prototypes | Pydantic AI | CrewAI |
| Multi-modal apps | Agno | Google ADK |
| Conversational AI | AutoGen | OpenAI SDK |

---

## Emerging Standards: MCP и A2A

### Model Context Protocol (MCP)

Universal standard для tool definitions от Anthropic:

```python
@mcp.tool()
def search_database(query: str) -> list:
    """Search the company database."""
    return db.search(query)
```

**Поддержка:** Pydantic AI, Google ADK, BeeAI, LangGraph, Bedrock

### Agent-to-Agent Protocol (A2A)

Communication standard для inter-agent collaboration:
- Агенты на разных frameworks могут общаться
- Delegation задач между системами
- Emerging standard в 2025

---

## Заключение

### Текущее состояние (декабрь 2025)

1. **LangGraph 1.0** - production standard для complex workflows
2. **CrewAI** - лидер для role-based multi-agent teams
3. **Pydantic AI v1.39** - выбор для type-safe development
4. **AutoGen → Agent Framework** - Microsoft's unified approach
5. **Cloud providers** - Bedrock, ADK активно развивают solutions

### Тренды 2026

- **Interoperability**: MCP и A2A станут must-have
- **Specialization**: Frameworks фокусируются на нишах
- **Enterprise adoption**: 33% apps с agentic AI к 2028
- **Local execution**: SmolAgents, Ollama - privacy-first

### Рекомендации

> **Для старта**: Pydantic AI или CrewAI
>
> **Для production**: LangGraph с LangSmith
>
> **Для enterprise**: Cloud provider solutions + LangGraph
>
> **Для research**: DSPy

---

## Ссылки и ресурсы

### Официальная документация

| Framework | URL |
|-----------|-----|
| LangGraph | https://langchain-ai.github.io/langgraph/ |
| CrewAI | https://docs.crewai.com/ |
| OpenAI SDK | https://openai.github.io/openai-agents-python/ |
| Pydantic AI | https://ai.pydantic.dev/ |
| AutoGen | https://microsoft.github.io/autogen/ |
| LlamaIndex | https://docs.llamaindex.ai/ |
| SmolAgents | https://huggingface.co/docs/smolagents/ |
| DSPy | https://dspy.ai/ |
| Google ADK | https://google.github.io/adk-docs/ |

### GitHub Repositories

- langchain-ai/langgraph
- crewAIInc/crewAI
- openai/openai-agents-python
- pydantic/pydantic-ai
- microsoft/autogen
- run-llama/llama_index
- huggingface/smolagents
- stanfordnlp/dspy
- google/adk-python
- i-am-bee/beeai-framework

### Образовательные ресурсы

- [LangChain Academy](https://academy.langchain.com/)
- [DeepLearning.AI - Multi AI Agent Systems](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/)
- [HuggingFace Agents Course](https://huggingface.co/learn/agents-course/)

---

*Последнее обновление: декабрь 2025*

---

*Проверено: 2026-01-09*
