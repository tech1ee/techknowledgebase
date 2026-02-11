---
title: "Что такое AI Engineering"
created: 2025-11-24
modified: 2025-12-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/ai-ml
  - ai-ml/basics
  - career/ai-engineer
  - type/concept
  - level/intermediate
related:
  - "[[rag-and-prompt-engineering]]"
  - "[[ai-engineer-tech-stack]]"
  - "[[ai-engineer-roadmap]]"
---

# Что такое AI Engineering

**AI Engineering** - это дисциплина на стыке software engineering и искусственного интеллекта, фокусирующаяся на интеграции готовых AI-моделей в production-приложения. AI Engineer не создает модели с нуля - он использует существующие foundation models (GPT-4, Claude, Llama) для построения интеллектуальных систем: чат-ботов, RAG-систем, AI-агентов.

---

## Краткая история: от академической дисциплины к профессии

### Рождение AI как области исследований (1950-1956)

Искусственный интеллект как академическая дисциплина был основан в **1956 году** на знаменитой Дартмутской конференции. Джон Маккарти, организатор конференции, ввел сам термин "artificial intelligence" годом ранее, описав его как "науку и инженерию создания интеллектуальных машин".

Однако концептуальные основы заложил **Алан Тьюринг** еще раньше:
- 1948: отчет "Intelligent Machinery" с центральными концепциями AI
- 1950: знаменитая статья "Computing Machinery and Intelligence" и тест Тьюринга

### Эволюция и "зимы AI" (1960-2010)

Поле прошло через несколько циклов оптимизма и разочарований:

```
1960-1970: Первый расцвет → экспертные системы
1970-1980: Первая "зима AI" → недофинансирование
1980-1990: Второй расцвет → Японский проект FGCP ($400M)
1990-2000: Вторая "зима" → разочарование в экспертных системах
2000-2010: Возрождение через Machine Learning → Big Data
```

### Emergence AI Engineering как профессии (2012-настоящее)

**2012**: AlexNet побеждает в ImageNet - начало deep learning революции
**2017**: Статья "Attention is All You Need" - архитектура Transformer
**2020**: GPT-3 демонстрирует few-shot learning
**Ноябрь 2022**: Выход ChatGPT - переломный момент

До ChatGPT работа с AI требовала глубокой экспертизы в ML. После - появилась возможность строить AI-продукты через API, что создало спрос на новый тип специалиста:

```
До 2022: Хочешь AI в продукте?
         → Собери данные (месяцы)
         → Найми ML-команду ($500k+)
         → Обучи модель (месяцы)
         → Задеплой инфраструктуру
         → Итого: 6-12 месяцев

После 2022: Хочешь AI в продукте?
            → pip install openai
            → response = client.chat("Сделай X")
            → Итого: 1 день и $0.01 за запрос
```

Это как разница между "построй свою электростанцию" и "воткни вилку в розетку".

---

## Терминология

| Термин | Значение |
|--------|----------|
| **LLM** | Large Language Model - большая языковая модель (GPT-4, Claude, Llama) |
| **Foundation Model** | Универсальная модель, обученная на огромных данных, адаптируемая под разные задачи |
| **API** | Интерфейс для вызова модели (OpenAI, Anthropic, Google) |
| **Token** | Единица текста (~4 символа на английском, 1-2 на русском) |
| **Prompt** | Запрос к модели с инструкциями |
| **Context window** | Максимальное количество токенов, которое модель "видит" за раз |
| **Fine-tuning** | Дообучение модели на специфических данных |
| **RAG** | Retrieval-Augmented Generation - поиск + генерация |
| **Embedding** | Векторное представление текста для семантического поиска |
| **Agentic AI** | AI-системы, способные автономно выполнять задачи |

---

## AI Engineer vs ML Engineer vs Data Scientist

Эти три роли часто путают. Разберем ключевые различия:

### Сравнительная таблица

| Аспект | AI Engineer | ML Engineer | Data Scientist |
|--------|-------------|-------------|----------------|
| **Фокус** | Системы на базе AI | Создание и обучение моделей | Анализ данных и insights |
| **Главная задача** | Интеграция моделей в продукты | Построение ML-пайплайнов | Извлечение знаний из данных |
| **Типичные проекты** | RAG-системы, чат-боты, AI-агенты | Feature engineering, A/B тесты моделей | Дашборды, предиктивная аналитика |
| **Отношение к ML** | Использует готовые модели | Создает модели | Применяет ML для анализа |
| **Математика** | Базовая | Глубокая (линал, статистика, calculus) | Статистика, теория вероятностей |
| **Ключевые инструменты** | LangChain, LlamaIndex, Vector DBs | PyTorch, TensorFlow, MLflow | Pandas, scikit-learn, SQL |
| **Бэкграунд** | Software Engineering | Data Science / ML Research | Statistics / Analytics |

### Как они работают с ML

**Data Scientist** использует ML для поиска паттернов и предсказаний. Например, предсказывает, какие клиенты отменят подписку.

**ML Engineer** строит и обучает модели, создает пайплайны для их деплоя. Фокус на одной задаче, выполняемой очень хорошо.

**AI Engineer** интегрирует готовые модели в приложения. Например, строит чат-бота, который улучшает ответы с каждым разговором.

### Принцип разграничения

> AI Engineers живут в мире foundation models и generative AI. ML Engineers создают task-specific системы. Data Scientists интерпретируют данные и предоставляют actionable insights.

*На практике границы размыты. По данным исследований, термин "Machine Learning" встречается в 83% вакансий AI/ML, а "Artificial Intelligence" только в 3%. Смотри на требования, а не на название.*

---

## Что делает AI Engineer: конкретные задачи

### 1. Интеграция LLM в продукты

Подключить GPT/Claude к приложению - это не просто один API-вызов:

**Prompt Engineering** - формулировка запросов к модели:

```python
# Плохой промпт
response = openai.chat("Напиши текст")

# Хороший промпт
response = openai.chat("""
Ты опытный копирайтер для B2B SaaS продуктов.
Напиши описание функции "автоматическая отчетность" для лендинга.
Требования:
- 2-3 предложения
- Фокус на экономии времени
- Без воды и общих фраз
""")
```

**Production concerns:**
- Обработка ошибок и fallback-стратегии
- Кэширование одинаковых запросов
- Управление rate limits
- Мониторинг качества ответов
- Оптимизация costs (GPT-4 = $30-60 за 1M токенов)

### 2. Построение RAG-систем

**RAG (Retrieval-Augmented Generation)** - техника, дающая модели доступ к вашим данным.

**Почему нужен:** LLM знает только то, на чем обучена. Вашу корпоративную документацию она не знает. RAG решает эту проблему.

**Как работает:**
```
1. Пользователь задает вопрос
2. Система ищет релевантные документы в vector database
3. Найденные документы добавляются в контекст промпта
4. LLM генерирует ответ на основе этих документов
```

**Рынок RAG** по данным Grand View Research достиг $1.2 млрд в 2025 году и прогнозируется рост до $11 млрд к 2030.

### 3. Разработка AI-агентов

**AI-агент** - это LLM с возможностью действовать: искать в интернете, вызывать API, выполнять код, отправлять email.

```
Чат-бот (обычный):
Ты: "Какая погода в Москве?"
Бот: "Я не могу проверить текущую погоду, но обычно в ноябре..."
     ↑ Галлюцинирует, потому что не может выйти в интернет

Агент:
Ты: "Какая погода в Москве?"
Агент: [использует инструмент: weather_api("Moscow")]
       → Получает данные
       → "Сейчас в Москве -2°C, пасмурно, ветер 5 м/с"
      ↑ Реальные данные, потому что сходил и проверил
```

По прогнозу Gartner, к 2028 году 33% enterprise-софта будет содержать agentic AI.

### 4. MLOps для LLM

- Мониторинг качества ответов и галлюцинаций
- A/B тесты промптов и моделей
- Управление версиями промптов
- CI/CD для AI-систем
- Containerization (Docker/Kubernetes)

---

## Навыки AI Engineer в 2025

### Must have

**Python** - основной язык. 90%+ AI-инструментов написаны на нем. Нужно владеть: async/await, работа с API, pandas.

**Работа с LLM API** - OpenAI, Anthropic, Google, open-source модели. Понимание различий, сильных/слабых сторон.

**Prompt Engineering** - по данным анализа вакансий, NLP (включая prompting) - самый востребованный навык (19.7% вакансий).

**RAG и Vector Databases** - Pinecone, Chroma, Qdrant, Weaviate, pgvector.

**Embeddings** - числовые представления текста для семантического поиска:

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    input="Как работает AI?",
    model="text-embedding-3-large"
)
# Результат: вектор из 3072 чисел
```

### High demand skills

**LangChain / LlamaIndex** - появляется в 10%+ всех AI вакансий:
- LangChain: лучше для rapid prototyping, 50K+ интеграций
- LlamaIndex: лучше для complex data ingestion, 150+ коннекторов

**Cloud Platforms:**
- Azure: 33% вакансий
- AWS: 26% вакансий
- GCP: остальное

**MLOps** - CI/CD, containerization, model monitoring, pipeline automation.

### Nice to have

- Fine-tuning и LoRA/QLoRA
- Computer Vision (CNNs, CLIP)
- Deep Learning frameworks (PyTorch, TensorFlow)
- Kubernetes для деплоя
- LangGraph для stateful агентов

### НЕ обязательно

- Глубокая математика (линал, calculus) - нужна для ML Engineer
- PhD - точно не требуется
- Опыт обучения моделей с нуля

---

## Рынок труда и зарплаты (2025)

### Зарплаты в США

По данным различных источников:

| Метрика | Значение |
|---------|----------|
| Средняя зарплата (Glassdoor) | $138,986 |
| Средняя зарплата (альтернативные оценки) | $206,000 (+$50K к 2024) |
| 25-й перцентиль | $110,824 |
| 75-й перцентиль | $176,648 |
| 90-й перцентиль | $217,654 |
| Топ-компании (Microsoft, Google) | до $340,000 |
| AI-стартапы (OpenAI, Anthropic) | $530,000 - $690,000 |

Для сравнения:
- ML Engineer: ~$155,000 - $202,000
- Data Scientist: ~$115,000 - $125,000

### Рост рынка

- **41.8%** рост вакансий AI/ML Engineer год к году (Q1 2025)
- **13.1%** рост квартал к кварталу
- **20%** прогнозируемый рост до 2034 года
- **1.3 млн** AI вакансий ожидается в США в ближайшие 2 года
- Менее **645,000** специалистов смогут их закрыть

### Географическое распределение

- **Калифорния**: 33% всех вакансий (Bay Area, LA)
- **Pacific Northwest**: Seattle
- **I-95 corridor**: New York, Boston, Washington D.C.
- **Канада**: Toronto, Montreal - растущие AI-хабы

---

## Карьерный путь

### Откуда приходят в AI Engineering

1. **Software Engineers** - самый естественный переход
2. **Backend Developers** - опыт с API и системами
3. **Data Engineers** - понимание data pipelines
4. **ML Engineers** - переход к application-focused работе

### Roadmap (6-8 месяцев)

**Месяц 1-2: Основы Python и ML**
- Python: синтаксис, async/await, работа с API
- Базовый ML: что такое embeddings, токены, context window

**Месяц 3-4: LLM и Prompt Engineering**
- Работа с OpenAI/Anthropic API
- Структурирование промптов
- Обработка ошибок, rate limits

**Месяц 5-6: RAG и Vector Databases**
- Chunking strategies
- Выбор и настройка vector store
- Реализация end-to-end RAG pipeline

**Месяц 7-8: Продвинутые темы**
- LangChain/LlamaIndex
- AI-агенты
- Deployment и MLOps
- Portfolio projects

### Portfolio Projects

Рекомендуется создать:
1. RAG-система для Q&A по документации
2. AI-агент с tool use
3. Fine-tuned модель для специфической задачи
4. Production-ready chatbot с мониторингом

---

## Ограничения и честные минусы

### Галлюцинации моделей

**Галлюцинации** - когда модель уверенно генерирует неправильную информацию. Это фундаментальное свойство LLM, не баг.

Решения: RAG, fact-checking, retrieval-based подходы. Но 100% решения пока нет.

### Зависимость от провайдеров

Строишь на OpenAI API - зависишь от их pricing, rate limits, политик. Диверсификация через multi-provider архитектуру.

### Быстрое устаревание знаний

То, что работало год назад, может быть неактуально. Непрерывное обучение - необходимость.

### Хайп vs реальность

Много экспериментов, меньше production-ready систем. По данным Gartner, 85% AI-проектов не доходят до продакшена.

---

## Инструменты и фреймворки 2025

### RAG Frameworks

| Framework | Лучше для | Особенности |
|-----------|-----------|-------------|
| **LangChain** | Rapid prototyping | 50K+ интеграций, chains и агенты |
| **LlamaIndex** | Complex data ingestion | 150+ коннекторов, продвинутый retrieval |
| **Haystack** | Enterprise NLP | Модульный, production-ready |
| **RAGFlow** | Простота | Pre-built компоненты |
| **Dify** | Low-code | Визуальный builder |
| **LangGraph** | Stateful агенты | Граф-based workflows |

### Vector Databases

- **Pinecone** - managed, простой старт
- **Qdrant** - open-source, высокая производительность
- **Weaviate** - модульный, GraphQL API
- **Chroma** - легковесный, для прототипов
- **pgvector** - если уже используешь PostgreSQL
- **Milvus** - enterprise-scale

### LLM Providers

- **OpenAI**: GPT-4o, GPT-4o-mini, o1
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku/Opus
- **Google**: Gemini Pro, Gemini Ultra
- **Open-source**: Llama 3.1/3.2, Mixtral, Qwen 2.5

---

## Продукты, построенные AI Engineers

```
Notion AI      → GPT API          → Саммаризация, генерация текста
GitHub Copilot → Codex (OpenAI)   → Автодополнение кода
Cursor         → GPT-4 + Claude   → AI-редактор кода, $100M+ ARR
Perplexity     → GPT + поиск      → AI-поисковик, $500M+ оценка
Jasper AI      → GPT + Claude     → Маркетинговые тексты, $125M ARR
Midjourney     → Custom models    → Генерация изображений
```

Ни один из этих продуктов не обучал модель с нуля. Все взяли готовое и построили вокруг него продукт.

---

## Связи

- Следующий шаг: [[rag-and-prompt-engineering]]
- Инструменты: [[ai-engineer-tech-stack]]
- Как начать: [[ai-engineer-roadmap]]
- Подход к обучению: [[learning-complex-things]]

---

## Источники

### Определение роли и обязанности
- [IntuitionLabs: AI Engineer Job Market 2025](https://intuitionlabs.ai/articles/ai-engineer-job-market-2025)
- [Coursera: What Is an AI Engineer](https://www.coursera.org/articles/ai-engineer)
- [Neural Concept: What Is an AI Engineer](https://www.neuralconcept.com/post/what-is-an-ai-engineer-key-skills-roles-and-career-paths-explained)

### AI Engineer vs ML Engineer
- [Vettio: AI Engineer vs ML Engineer](https://vettio.com/blog/ai-engineer-vs-ml-engineer/)
- [University of Manchester: ML Engineer vs AI Engineer](https://research-it.manchester.ac.uk/news/2025/10/14/ml-engineer-vs-ai-engineer/)
- [Index.dev: AI Engineer vs ML Engineer](https://www.index.dev/blog/ai-engineer-vs-machine-learning-engineer)
- [Pave: How Companies Structure AI/ML Roles](https://www.pave.com/blog-posts/differences-between-ai-engineers-ml-engineers)

### AI Engineer vs Data Scientist
- [TechTarget: AI Engineer vs Data Scientist](https://www.techtarget.com/searchenterpriseai/feature/AI-engineer-vs-data-scientist-Whats-the-difference)
- [DigitalDefynd: Data Engineer vs Data Scientist vs AI Engineer](https://digitaldefynd.com/IQ/data-engineer-vs-data-scientist-vs-ai-engineer/)
- [Upwork: AI Engineer vs Data Scientist](https://www.upwork.com/resources/ai-engineer-vs-data-scientist)

### Навыки и требования
- [DataCamp: 14 Essential AI Engineer Skills 2025](https://www.datacamp.com/blog/essential-ai-engineer-skills)
- [Udacity: How to Become an AI Engineer in 2025](https://www.udacity.com/blog/2025/06/how-to-become-an-ai-engineer-in-2025-skills-tools-and-career-paths.html)
- [Zero To Mastery: How to Become an AI Engineer](https://zerotomastery.io/blog/how-to-become-an-ai-engineer-from-scratch/)
- [Futurense: AI Skills in Demand 2025](https://futurense.com/blog/ai-skills-in-demand)

### Карьерный путь
- [roadmap.sh: AI Engineer Roadmap](https://roadmap.sh/ai-engineer)
- [OpenCV: 6-Month AI Engineer Roadmap](https://opencv.org/blog/ai-engineer-roadmap/)
- [Analytics Vidhya: Roadmap to Become an AI Engineer](https://www.analyticsvidhya.com/blog/2024/04/roadmap-to-become-an-ai-engineer/)
- [Codebasics: Ultimate AI Engineer Roadmap](https://codebasics.io/blog/ultimate-ai-engineer-roadmap)

### Рынок труда и зарплаты
- [365 Data Science: AI Engineer Job Outlook 2025](https://365datascience.com/career-advice/career-guides/ai-engineer-job-outlook-2025/)
- [Glassdoor: AI Engineer Salary](https://www.glassdoor.com/Salaries/ai-engineer-salary-SRCH_KO0,11.htm)
- [Veritone: AI Jobs Q1 2025 Labor Market Analysis](https://www.veritone.com/blog/ai-jobs-growth-q1-2025-labor-market-analysis/)
- [Mobilunity: AI Engineer Salary 2025](https://mobilunity.com/blog/ai-engineer-salary/)

### Инструменты и фреймворки
- [Firecrawl: 15 Best Open-Source RAG Frameworks](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks)
- [TechLife: AI Skills 2025 - LangChain, RAG, MLOps](https://techlife.blog/posts/ai-skills-2025-langchain-rag-mlops-guide/)
- [Pathway: Compare Top 7 RAG Frameworks](https://pathway.com/rag-frameworks/)
- [Sider: LangChain vs LlamaIndex 2025](https://sider.ai/blog/ai-tools/langchain-vs-llamaindex-which-rag-framework-wins-in-2025)

### История AI
- [Wikipedia: History of Artificial Intelligence](https://en.wikipedia.org/wiki/History_of_artificial_intelligence)
- [Britannica: History of AI](https://www.britannica.com/science/history-of-artificial-intelligence)
- [Stanford AI100: Short History of AI](https://ai100.stanford.edu/2016-report/appendix-i-short-history-ai)
- [Delve: History of AI in Engineering](https://www.delve.com/insights/a-history-of-ai-in-engineering-from-the-1970s-to-today)

---

**Последняя верификация**: 2025-12-24
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*
