---
title: "Tutorial: Production-Ready RAG Chatbot с нуля"
tags:
  - topic/ai-ml
  - rag
  - tutorial
  - langchain
  - chromadb
  - qdrant
  - openai
  - project
  - production
  - type/tutorial
  - level/intermediate
category: ai-ml
level: practical
created: 2025-01-15
updated: 2026-02-13
reading_time: 82
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - [rag-advanced-techniques]]
  - "[[embeddings-complete-guide]]"
  - "[[vector-databases-guide]"
status: published
---

# Tutorial: Production-Ready RAG Chatbot с нуля

> Пошаговое руководство по созданию AI-чатбота, который отвечает на вопросы по вашим документам. От загрузки PDF до production-деплоя за 2-3 часа.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Python 3.10+** | Весь код на Python, используем современный синтаксис | Любой курс Python |
| **LLM основы** | Понимание что такое LLM, токены, промпты | [[llm-fundamentals]] |
| **REST API** | Работа с OpenAI/Cohere API | [[ai-api-integration]] |
| **Базовый async/await** | Асинхронные вызовы для производительности | Python asyncio docs |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ✅ Да | Отличная точка входа в AI |
| **Intermediate** | ✅ Да | Фокус на best practices |
| **Advanced** | ✅ Да | Production-паттерны и evaluation |

### Терминология для новичков

> 💡 **RAG (Retrieval-Augmented Generation)** = LLM отвечает не из головы, а сначала ищет информацию в твоих документах. Как Google + ChatGPT вместе.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **RAG** | Поиск + Генерация: сначала найди, потом отвечай | **Студент на экзамене с конспектом** — ищет ответ, потом формулирует |
| **Embedding** | Текст → числовой вектор (список чисел) | **GPS-координаты для смысла** — похожие тексты рядом |
| **Vector Database** | База данных для хранения и поиска векторов | **Библиотека с GPS-навигацией** — быстро находит похожие книги |
| **Chunk** | Кусок документа (обычно 200-500 слов) | **Страница из книги** — документ делим на части |
| **Chunking** | Процесс разбиения документа на chunks | **Нарезка пиццы** — большой документ режем на куски |
| **Hybrid Search** | Vector + keyword поиск вместе | **Смысл + точные слова** — ищем и по смыслу, и по терминам |
| **BM25** | Классический алгоритм текстового поиска | **Ctrl+F на стероидах** — умный поиск по ключевым словам |
| **Reranking** | Пересортировка результатов поиска | **Второе мнение** — эксперт переоценивает что важнее |
| **Faithfulness** | Ответ основан на документах (не выдумка) | **Честность** — LLM говорит только то, что видел в документах |
| **RAGAS** | Метрики качества RAG систем | **Оценка 1-10** — насколько хорошо работает система |

---

## Теоретические основы

> **RAG (Retrieval-Augmented Generation)** — архитектурный паттерн, где генеративная модель дополняется внешним поиском релевантной информации. Формально: $P(answer|query) = \sum_z P(z|query) \cdot P(answer|z, query)$, где $z$ — retrieved документы (Lewis et al., 2020).

Этот tutorial реализует RAG pipeline, основанный на следующих теоретических компонентах:

| Компонент | Теория | Реализация в tutorial |
|-----------|--------|----------------------|
| **Embedding** | Distributional semantics (Harris, 1954; Mikolov, 2013) | OpenAI text-embedding-3-small |
| **Vector Search** | Approximate Nearest Neighbor (Malkov & Yashunin, 2018) | ChromaDB / Qdrant (HNSW) |
| **Hybrid Search** | RRF fusion (Cormack et al., 2009) | BM25 + vector с RRF |
| **Reranking** | Cross-encoder (Nogueira & Cho, 2019) | Cohere Rerank / BGE |
| **Generation** | Conditional text generation (Vaswani et al., 2017) | OpenAI GPT-4o с контекстом |
| **Evaluation** | RAGAS (Es et al., 2023) | Faithfulness, relevance, recall |

> **Ключевая идея RAG**: вместо хранения знаний в параметрах модели (что дорого и быстро устаревает), знания хранятся во внешней базе и подаются в контекст на момент запроса. Это решает проблемы: hallucination, устаревание, domain-специфичность.

**Pipeline этого tutorial:**

```
Documents → Chunking → Embedding → Vector DB
                                       ↓
User Query → Embedding → Hybrid Search → Reranking → LLM → Answer
```

Каждый этап имеет свои параметры и tradeoffs, которые разбираются в соответствующих секциях.

См. также: [[rag-advanced-techniques|RAG Advanced]] — продвинутые паттерны, [[embeddings-complete-guide|Embeddings]] — теория embeddings, [[vector-databases-guide|Vector DBs]] — ANN-алгоритмы.

---

## Зачем это нужно / Какую проблему решает

**Представьте ситуацию:** у вашей компании 500+ страниц документации, политик, FAQ. Сотрудники тратят часы на поиск информации. Вы хотите чатбот, который мгновенно находит ответы.

**Проблема с обычными LLM:**
- ChatGPT не знает ваших внутренних документов
- Fine-tuning дорогой ($10-100k+) и требует перетренировки при каждом обновлении
- Модель может "галлюцинировать" — придумывать несуществующие факты

**RAG решает эти проблемы:**
- Модель ищет в ваших документах перед ответом
- Обновление данных — просто загрузить новые файлы
- Каждый ответ содержит ссылки на источники
- По данным 2025 года, **70% enterprise AI-приложений используют RAG** ([Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/07/silent-killers-of-production-rag/))

**Кому подойдёт этот tutorial:**
- Backend/fullstack разработчикам, которые хотят добавить AI в продукт
- Data engineers, строящим knowledge management системы
- Стартапам, которым нужен MVP чатбота за выходные

---

## Что построим

> Полноценный production-ready RAG chatbot с веб-интерфейсом, который отвечает на вопросы по вашим документам. Стек: LangChain + Qdrant/ChromaDB + OpenAI + Streamlit + Hybrid Search + Reranking + Observability.

**Время:** 2-3 часа
**Уровень:** Intermediate
**Результат:** Работающий chatbot с best practices 2025 года

### Чему вы научитесь

1. **Indexing Pipeline** — загрузка PDF/MD/DOCX, chunking, embeddings
2. **Vector Search** — как работает семантический поиск и когда его недостаточно
3. **Hybrid Search** — комбинация vector + keyword для +20% recall
4. **Reranking** — Cross-encoder для +25% precision
5. **RAG Chain** — prompt engineering против галлюцинаций
6. **Evaluation** — RAGAS метрики для измерения качества
7. **Production Deploy** — Docker, observability, типичные ошибки

### Prerequisities

- Python 3.10+
- OpenAI API key (или другой LLM provider)
- Базовое понимание Python async/await
- (Опционально) Cohere API key для reranking

### Стоимость запуска

| Компонент | Бесплатно | С оплатой |
|-----------|-----------|-----------|
| Vector DB | ChromaDB (local), Qdrant (local) | Pinecone ($70/mo), Qdrant Cloud ($25/mo) |
| Embeddings | — | OpenAI text-embedding-3: ~$0.02/1M tokens |
| LLM | — | GPT-4o-mini: ~$0.15/1M tokens, GPT-4o: ~$2.50/1M tokens |
| Reranking | — | Cohere: $1/1000 searches |

**Типичная стоимость для MVP:** $5-20/месяц при 1000 запросах/день

---

## Почему RAG, а не Fine-tuning?

RAG (Retrieval-Augmented Generation) решает ключевую проблему LLM: модели знают только то, на чём обучались. По данным 2025 года, **70% enterprise AI-приложений используют RAG** ([Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/07/silent-killers-of-production-rag/)).

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Fine-tuning** | Встроенные знания, быстрый inference | Дорого, данные устаревают, сложно обновлять |
| **RAG** | Актуальные данные, прозрачные источники, дешевле | Зависит от качества retrieval |

**RAG выигрывает когда:**
- Данные часто обновляются
- Нужны ссылки на источники
- Важна прозрачность ответов

---

## Архитектура RAG-системы

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Production RAG Architecture 2025                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │   Documents  │───▶│   Chunking   │───▶│  Embeddings  │               │
│  │  (.pdf,.md)  │    │  (Semantic/  │    │  (text-emb-  │               │
│  │              │    │   Recursive) │    │   3-large)   │               │
│  └──────────────┘    └──────────────┘    └──────┬───────┘               │
│                                                  │                       │
│                             ┌────────────────────┼────────────────────┐  │
│                             │                    ▼                    │  │
│                             │           ┌──────────────┐              │  │
│                             │           │  Vector DB   │              │  │
│                             │           │(Qdrant/Chroma│              │  │
│                             │           └──────────────┘              │  │
│                             │                    │                    │  │
│  ┌──────────────┐          │    ┌───────────────┴───────────────┐    │  │
│  │    User      │          │    │         HYBRID SEARCH         │    │  │
│  │   Question   │          │    │  ┌─────────┐    ┌─────────┐   │    │  │
│  └──────┬───────┘          │    │  │ Vector  │    │  BM25   │   │    │  │
│         │                   │    │  │ Search  │    │ Keyword │   │    │  │
│         ▼                   │    │  └────┬────┘    └────┬────┘   │    │  │
│  ┌──────────────┐          │    │       └──────┬───────┘        │    │  │
│  │Query Embed + │          │    │              ▼                │    │  │
│  │ Expansion    │──────────┼───▶│    ┌──────────────┐           │    │  │
│  └──────────────┘          │    │    │   RRF Fusion │           │    │  │
│                             │    │    └──────┬───────┘           │    │  │
│                             │    └───────────┼───────────────────┘    │  │
│                             │                ▼                        │  │
│                             │        ┌──────────────┐                 │  │
│                             │        │   Reranker   │                 │  │
│                             │        │ (Cohere/BGE) │                 │  │
│                             │        └──────┬───────┘                 │  │
│                             └────────────────┼────────────────────────┘  │
│                                              ▼                           │
│                                      ┌──────────────┐                    │
│                                      │  Top-K Docs  │                    │
│                                      │   Context    │                    │
│                                      └──────┬───────┘                    │
│                                              │                           │
│                                              ▼                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        LLM Generation                              │  │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │  │
│  │  │   System    │ + │   Context   │ + │   Query     │ ──▶ Answer   │  │
│  │  │   Prompt    │   │   (docs)    │   │             │              │  │
│  │  └─────────────┘   └─────────────┘   └─────────────┘              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                              │                           │
│                                              ▼                           │
│                                      ┌──────────────┐                    │
│                                      │   Answer +   │                    │
│                                      │   Citations  │                    │
│                                      └──────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Что происходит под капотом

1. **Indexing (офлайн):**
   - Документы загружаются и разбиваются на chunks
   - Каждый chunk превращается в embedding (вектор 1536/3072 размерности)
   - Векторы сохраняются в vector database с metadata

2. **Retrieval (рантайм):**
   - Вопрос пользователя превращается в embedding
   - Hybrid search: vector similarity + keyword BM25
   - Результаты объединяются через Reciprocal Rank Fusion
   - Reranker переранжирует top-N документов

3. **Generation (рантайм):**
   - Топ-K релевантных chunks передаются в LLM как контекст
   - LLM генерирует ответ на основе ТОЛЬКО этого контекста
   - Ответ возвращается с ссылками на источники

---

## Step 1: Setup проекта

### Структура проекта

```
rag-chatbot/
├── app.py                 # Streamlit UI
├── rag/
│   ├── __init__.py
│   ├── config.py          # Конфигурация
│   ├── document_loader.py # Загрузка документов
│   ├── chunking.py        # Стратегии chunking
│   ├── vectorstore.py     # Vector DB operations
│   ├── retriever.py       # Hybrid retrieval + reranking
│   ├── chain.py           # RAG chain
│   └── evaluation.py      # RAGAS metrics
├── documents/             # Ваши документы
├── data/                  # Vector DB storage
├── tests/
│   └── test_rag.py
├── requirements.txt
├── docker-compose.yml
└── .env
```

### Установка зависимостей

```bash
# requirements.txt
# Core
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
langchain-qdrant>=0.2.0

# Vector Databases
qdrant-client>=1.12.0
chromadb>=0.5.0

# Embeddings & Reranking
cohere>=5.0.0
sentence-transformers>=3.0.0

# Document Processing
pypdf>=4.0.0
unstructured>=0.15.0
python-docx>=1.0.0
tiktoken>=0.7.0

# Text Processing
rank-bm25>=0.2.2

# Web UI
streamlit>=1.38.0

# Evaluation
ragas>=0.2.0

# Observability
langfuse>=2.0.0

# Utils
python-dotenv>=1.0.0
pydantic>=2.0.0
```

```bash
pip install -r requirements.txt
```

### Переменные окружения

```bash
# .env
OPENAI_API_KEY=sk-...

# Optional: для reranking
COHERE_API_KEY=...

# Optional: для Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=...

# Optional: для observability
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

---

## Step 2: Конфигурация

```python
# rag/config.py
"""
Централизованная конфигурация RAG системы.

Почему отдельный файл конфигурации?
- Легко менять параметры без изменения кода
- Разные конфиги для dev/staging/prod
- Документирование дефолтных значений
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class RAGConfig(BaseSettings):
    """Конфигурация RAG пайплайна."""

    # === Chunking ===
    # Оптимальный размер 256-512 токенов по исследованиям 2025
    # https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025
    chunk_size: int = Field(
        default=512,
        description="Размер chunk в токенах. 256-512 для factoid queries, 1024+ для аналитических"
    )
    chunk_overlap: int = Field(
        default=50,
        description="Перекрытие между chunks. 10-20% от chunk_size сохраняет контекст на границах"
    )

    # === Embeddings ===
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="OpenAI модель. 'large' (3072 dim) точнее, 'small' (1536 dim) дешевле"
    )

    # === Vector Store ===
    vectorstore_type: Literal["qdrant", "chroma"] = Field(
        default="qdrant",
        description="Qdrant для production (Rust, быстрый), Chroma для прототипов"
    )
    collection_name: str = "documents"

    # === Retrieval ===
    retrieval_k: int = Field(
        default=20,
        description="Сколько документов извлекать до reranking. Больше = лучше recall, но дороже"
    )
    final_k: int = Field(
        default=5,
        description="Сколько документов передавать в LLM после reranking"
    )
    use_hybrid_search: bool = Field(
        default=True,
        description="Hybrid search улучшает recall на ~20% по бенчмаркам"
    )
    hybrid_alpha: float = Field(
        default=0.7,
        description="Баланс vector/keyword. 0.7 = 70% semantic, 30% keyword"
    )

    # === Reranking ===
    use_reranking: bool = Field(
        default=True,
        description="Reranking улучшает precision на 25-35% (Cohere benchmarks)"
    )
    rerank_model: str = Field(
        default="rerank-english-v3.0",
        description="Cohere rerank модель. rerank-v3 или rerank-multilingual-v3.0"
    )

    # === LLM ===
    llm_model: str = Field(
        default="gpt-4o",
        description="gpt-4o для качества, gpt-4o-mini для скорости/стоимости"
    )
    llm_temperature: float = Field(
        default=0.0,
        description="0.0 для детерминированных ответов, 0.3-0.7 для креативности"
    )

    class Config:
        env_file = ".env"
        env_prefix = "RAG_"


# Singleton instance
config = RAGConfig()
```

---

## Step 3: Document Loader

```python
# rag/document_loader.py
"""
Загрузка документов разных форматов.

Поддерживаемые форматы:
- PDF (с OCR для сканов)
- Markdown
- TXT
- DOCX
- HTML

Что происходит под капотом:
1. Определяется тип файла по расширению
2. Выбирается соответствующий loader
3. Документ парсится в текст + metadata
4. Metadata обогащается (source, file_type, page_number)
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    Docx2txtLoader,
)
from langchain.schema import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Универсальный загрузчик документов.

    Пример использования:
        loader = DocumentLoader()
        docs = loader.load_directory("./documents")
    """

    # Маппинг расширений на loaders
    # Каждый loader умеет извлекать текст из своего формата
    LOADERS = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".html": UnstructuredHTMLLoader,
        ".docx": Docx2txtLoader,
    }

    def __init__(self, extra_metadata: Optional[Dict[str, Any]] = None):
        """
        Args:
            extra_metadata: Дополнительные поля для всех документов
                           (например, {"project": "docs-v2"})
        """
        self.extra_metadata = extra_metadata or {}

    def load_file(self, file_path: str) -> List[Document]:
        """
        Загружает один файл.

        Args:
            file_path: Путь к файлу

        Returns:
            Список Document (для PDF - по одному на страницу)

        Raises:
            ValueError: Если формат не поддерживается
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in self.LOADERS:
            supported = ", ".join(self.LOADERS.keys())
            raise ValueError(
                f"Формат {suffix} не поддерживается. "
                f"Поддерживаемые: {supported}"
            )

        loader_class = self.LOADERS[suffix]
        loader = loader_class(str(path))

        try:
            documents = loader.load()
        except Exception as e:
            logger.error(f"Ошибка загрузки {file_path}: {e}")
            raise

        # Обогащаем metadata
        for doc in documents:
            doc.metadata.update({
                "source": path.name,
                "source_path": str(path.absolute()),
                "file_type": suffix,
                **self.extra_metadata
            })

        logger.info(f"Загружен: {path.name} ({len(documents)} частей)")
        return documents

    def load_directory(
        self,
        directory: str,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Загружает все документы из директории.

        Args:
            directory: Путь к директории
            recursive: Искать в поддиректориях
            exclude_patterns: Паттерны для исключения (например, ["*_draft.md"])

        Returns:
            Список всех загруженных документов
        """
        all_docs = []
        dir_path = Path(directory)
        exclude_patterns = exclude_patterns or []

        # Паттерн для поиска файлов
        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            # Пропускаем директории
            if not file_path.is_file():
                continue

            # Пропускаем неподдерживаемые форматы
            if file_path.suffix.lower() not in self.LOADERS:
                continue

            # Проверяем exclude patterns
            if any(file_path.match(pat) for pat in exclude_patterns):
                logger.debug(f"Пропущен (exclude): {file_path.name}")
                continue

            try:
                docs = self.load_file(str(file_path))
                all_docs.extend(docs)
            except Exception as e:
                logger.warning(f"Не удалось загрузить {file_path}: {e}")
                continue

        logger.info(
            f"Загружено {len(all_docs)} документов из {directory}"
        )
        return all_docs
```

---

## Step 4: Chunking - Ключевой компонент

```python
# rag/chunking.py
"""
Стратегии разбиения документов на chunks.

КРИТИЧЕСКИ ВАЖНО: Неправильный chunking может снизить качество на 9%!
https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025

Основные стратегии:
1. RecursiveCharacter - универсальный дефолт (88-90% recall)
2. Semantic - лучший recall (+9%), но дороже
3. Sentence - для Q&A контента
"""
from typing import List, Literal, Optional
from abc import ABC, abstractmethod
import logging

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from .config import config

logger = logging.getLogger(__name__)


class BaseChunker(ABC):
    """Базовый класс для chunking стратегий."""

    @abstractmethod
    def split(self, documents: List[Document]) -> List[Document]:
        """Разбивает документы на chunks."""
        pass


class RecursiveChunker(BaseChunker):
    """
    Рекурсивный chunking - РЕКОМЕНДУЕМЫЙ ДЕФОЛТ.

    Как работает:
    1. Пытается разбить по параграфам (\\n\\n)
    2. Если chunk слишком большой - по строкам (\\n)
    3. Затем по предложениям (. )
    4. В крайнем случае - по словам и символам

    Это сохраняет структуру документа максимально возможно.

    Типичные результаты:
    - 85-90% recall на стандартных бенчмарках
    - Быстрая обработка (без API вызовов)
    """

    def __init__(
        self,
        chunk_size: int = config.chunk_size,
        chunk_overlap: int = config.chunk_overlap,
    ):
        """
        Args:
            chunk_size: Максимальный размер chunk в символах.
                       512 символов ~ 128 токенов для английского
                       Рекомендация: 400-512 токенов
            chunk_overlap: Перекрытие между chunks.
                          10-20% от chunk_size сохраняет контекст
        """
        # Иерархия разделителей - от крупных к мелким
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",    # Параграфы (самый приоритетный)
                "\n",      # Строки
                ". ",      # Предложения
                ", ",      # Части предложений
                " ",       # Слова
                ""         # Символы (крайний случай)
            ],
            # Важно: добавляем индекс начала для отладки
            add_start_index=True,
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """
        Разбивает документы на chunks.

        Каждый chunk получает:
        - page_content: текст chunk
        - metadata: все поля родительского документа + start_index
        """
        chunks = self.splitter.split_documents(documents)

        # Добавляем chunk_id для трекинга
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)

        logger.info(
            f"Recursive chunking: {len(documents)} docs -> {len(chunks)} chunks"
        )
        return chunks


class SemanticChunker(BaseChunker):
    """
    Семантический chunking - ЛУЧШИЙ RECALL, но дороже.

    Как работает:
    1. Каждое предложение превращается в embedding
    2. Вычисляется косинусное расстояние между соседними предложениями
    3. Если расстояние > threshold - это граница chunk

    Результаты:
    - До +9% recall по сравнению с recursive
    - Но: требует embedding каждого предложения (дорого!)

    Когда использовать:
    - Документы с неявной структурой
    - Высокие требования к качеству
    - Бюджет позволяет
    """

    def __init__(
        self,
        breakpoint_threshold_type: Literal[
            "percentile", "standard_deviation", "interquartile"
        ] = "percentile",
        breakpoint_threshold_amount: float = 95,
    ):
        """
        Args:
            breakpoint_threshold_type: Как определять границы
                - "percentile": разрыв в топ-N% самых больших (рекомендуется)
                - "standard_deviation": разрыв > N стандартных отклонений
                - "interquartile": статистический метод
            breakpoint_threshold_amount: Порог для выбранного метода
                Для percentile: 95 = только топ 5% разрывов становятся границами
        """
        # Используем ту же embedding модель, что и для поиска
        embeddings = OpenAIEmbeddings(model=config.embedding_model)

        self.splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
            breakpoint_threshold_amount=breakpoint_threshold_amount,
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """Разбивает документы семантически."""
        chunks = self.splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunking_method"] = "semantic"

        logger.info(
            f"Semantic chunking: {len(documents)} docs -> {len(chunks)} chunks"
        )
        return chunks


def get_chunker(
    strategy: Literal["recursive", "semantic"] = "recursive"
) -> BaseChunker:
    """
    Фабричный метод для получения chunker.

    Args:
        strategy:
            - "recursive": быстрый, универсальный (рекомендуется для старта)
            - "semantic": лучше качество, дороже

    Рекомендация:
    Начните с recursive. Если recall < 85%, попробуйте semantic.
    Разница в 3-5% recall редко оправдывает 10x стоимость обработки.
    """
    if strategy == "recursive":
        return RecursiveChunker()
    elif strategy == "semantic":
        return SemanticChunker()
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
```

---

## Step 5: Vector Store - Выбор и настройка

### Сравнение Vector Databases (2025)

| Database | Best For | Performance | Cost |
|----------|----------|-------------|------|
| **ChromaDB** | Прототипы, < 10M vectors | ~20ms p50 на 100k | Бесплатно |
| **Qdrant** | Production, filtering | Rust-fast, sub-50ms | Open-source |
| **Pinecone** | Managed production | sub-50ms at scale | $$$ |

**Рекомендация:** Начните с ChromaDB для прототипа, мигрируйте на Qdrant для production.

Источник: [Firecrawl Vector DB Comparison 2025](https://www.firecrawl.dev/blog/best-vector-databases-2025)

```python
# rag/vectorstore.py
"""
Vector Store абстракция с поддержкой Qdrant и ChromaDB.

Под капотом:
1. Embeddings: текст -> вектор (OpenAI text-embedding-3)
2. Indexing: HNSW алгоритм для быстрого approximate nearest neighbor search
3. Storage: персистентное хранение на диске или в облаке
"""
from typing import List, Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod
import logging

from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import Chroma
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from .config import config

logger = logging.getLogger(__name__)


class BaseVectorStore(ABC):
    """Абстракция для vector store."""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Добавляет документы в store."""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """Поиск похожих документов."""
        pass

    @abstractmethod
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """Поиск с relevance scores."""
        pass


class QdrantStore(BaseVectorStore):
    """
    Qdrant Vector Store - рекомендуется для production.

    Почему Qdrant:
    - Написан на Rust (быстрый!)
    - Продвинутая фильтрация без потери производительности
    - Scalar quantization (4-8x экономия памяти)
    - Поддержка hybrid search из коробки

    Документация: https://qdrant.tech/documentation/
    """

    def __init__(
        self,
        collection_name: str = config.collection_name,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        path: str = "./data/qdrant",
    ):
        """
        Args:
            collection_name: Имя коллекции
            url: URL Qdrant Cloud (если None - локальный)
            api_key: API key для Qdrant Cloud
            path: Путь для локального хранения
        """
        # Embeddings модель
        # text-embedding-3-large: 3072 dimensions, лучше качество
        # text-embedding-3-small: 1536 dimensions, дешевле
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model
        )

        # Определяем размерность эмбеддингов
        self.embedding_dim = 3072 if "large" in config.embedding_model else 1536

        # Клиент Qdrant
        if url:
            # Cloud mode
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            # Local mode с persistence
            self.client = QdrantClient(path=path)

        self.collection_name = collection_name
        self._ensure_collection()

        # LangChain wrapper
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

    def _ensure_collection(self):
        """Создаёт коллекцию если не существует."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,  # Cosine similarity
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Добавляет документы с embeddings."""
        ids = self.vectorstore.add_documents(documents)
        logger.info(f"Added {len(ids)} documents to Qdrant")
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """
        Поиск похожих документов.

        Args:
            query: Поисковый запрос
            k: Количество результатов
            filter: Фильтры по metadata (например, {"file_type": ".pdf"})
        """
        return self.vectorstore.similarity_search(
            query, k=k, filter=filter
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """Поиск с cosine similarity scores (0-1, больше = лучше)."""
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def get_stats(self) -> Dict[str, Any]:
        """Статистика коллекции."""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }


class ChromaStore(BaseVectorStore):
    """
    ChromaDB - для быстрого прототипирования.

    Плюсы:
    - Zero setup (embedded mode)
    - Простой API
    - Достаточно для < 10M vectors

    Минусы:
    - Не для production scale
    - Менее зрелый чем Qdrant/Pinecone
    """

    def __init__(
        self,
        collection_name: str = config.collection_name,
        persist_directory: str = "./data/chroma",
    ):
        self.embeddings = OpenAIEmbeddings(model=config.embedding_model)

        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        self.collection_name = collection_name

    def add_documents(self, documents: List[Document]) -> List[str]:
        ids = self.vectorstore.add_documents(documents)
        logger.info(f"Added {len(ids)} documents to Chroma")
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        return self.vectorstore.similarity_search_with_score(query, k=k)


def get_vectorstore(
    store_type: str = config.vectorstore_type
) -> BaseVectorStore:
    """Фабричный метод для получения vector store."""
    if store_type == "qdrant":
        return QdrantStore()
    elif store_type == "chroma":
        return ChromaStore()
    else:
        raise ValueError(f"Unknown store type: {store_type}")
```

---

## Step 6: Hybrid Search + Reranking

```python
# rag/retriever.py
"""
Продвинутый retriever с Hybrid Search и Reranking.

Hybrid Search объединяет:
- Vector search (semantic similarity) - понимает смысл
- BM25 (keyword search) - точное совпадение терминов

Результат: recall +20% по сравнению с чистым vector search.
https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking

Reranking (Cohere/BGE):
- Cross-encoder модель оценивает пары (query, document)
- Точнее чем bi-encoder embeddings
- Но медленнее, поэтому применяется к top-N результатам
- Улучшает precision на 25-35%
"""
from typing import List, Optional, Tuple
import logging

from langchain.schema import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from rank_bm25 import BM25Okapi
import cohere

from .vectorstore import BaseVectorStore, get_vectorstore
from .config import config

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid Retriever = Vector Search + BM25 + Reranking.

    Pipeline:
    1. Parallel: vector search (top-K) + BM25 search (top-K)
    2. Fusion: Reciprocal Rank Fusion объединяет результаты
    3. Reranking: Cohere rerank переранжирует объединённые результаты
    4. Return: top-N лучших документов

    Пример:
        retriever = HybridRetriever(documents)
        results = retriever.retrieve("What is RAG?", k=5)
    """

    def __init__(
        self,
        documents: Optional[List[Document]] = None,
        vectorstore: Optional[BaseVectorStore] = None,
        use_hybrid: bool = config.use_hybrid_search,
        use_reranking: bool = config.use_reranking,
        hybrid_alpha: float = config.hybrid_alpha,
    ):
        """
        Args:
            documents: Документы для BM25 (нужны если use_hybrid=True)
            vectorstore: Vector store (создаётся автоматически если None)
            use_hybrid: Использовать hybrid search
            use_reranking: Использовать reranking
            hybrid_alpha: Вес vector search (1.0 = только vector, 0.0 = только BM25)
        """
        self.use_hybrid = use_hybrid
        self.use_reranking = use_reranking
        self.hybrid_alpha = hybrid_alpha

        # Vector store
        self.vectorstore = vectorstore or get_vectorstore()

        # BM25 retriever (для hybrid search)
        self.bm25_retriever = None
        if use_hybrid and documents:
            self._init_bm25(documents)

        # Cohere reranker
        self.reranker = None
        if use_reranking:
            self._init_reranker()

    def _init_bm25(self, documents: List[Document]):
        """
        Инициализирует BM25 retriever.

        BM25 (Best Matching 25) - классический алгоритм текстового поиска:
        - TF (Term Frequency): частота термина в документе
        - IDF (Inverse Document Frequency): редкость термина в корпусе
        - Length normalization: нормализация по длине документа

        Преимущества над vector search:
        - Точное совпадение терминов (аббревиатуры, коды, имена)
        - Не требует GPU/API
        - Interpretable
        """
        self.bm25_retriever = BM25Retriever.from_documents(
            documents,
            k=config.retrieval_k,
        )
        logger.info(f"BM25 initialized with {len(documents)} documents")

    def _init_reranker(self):
        """
        Инициализирует Cohere Reranker.

        Как работает cross-encoder reranking:
        1. Bi-encoder (embeddings): encode(query) и encode(doc) отдельно
           - Быстро, но теряет взаимодействие между query и doc
        2. Cross-encoder (reranker): encode(query + doc) вместе
           - Медленно, но видит все взаимосвязи
           - Поэтому применяем только к top-N кандидатам

        Cohere Rerank 3.5:
        - 32K context window
        - +25% precision на challenging queries
        - Доступен через AWS Bedrock
        """
        try:
            self.reranker = CohereRerank(
                model=config.rerank_model,
                top_n=config.final_k,
            )
            logger.info(f"Cohere reranker initialized: {config.rerank_model}")
        except Exception as e:
            logger.warning(f"Cohere reranker init failed: {e}. Continuing without reranking.")
            self.use_reranking = False

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        Извлекает релевантные документы.

        Args:
            query: Поисковый запрос
            k: Количество результатов (default: config.final_k)
            filter: Фильтры по metadata

        Returns:
            Список релевантных документов, отсортированных по релевантности
        """
        k = k or config.final_k

        # Step 1: Initial retrieval
        if self.use_hybrid and self.bm25_retriever:
            docs = self._hybrid_retrieve(query, filter)
        else:
            docs = self._vector_retrieve(query, filter)

        # Step 2: Reranking
        if self.use_reranking and self.reranker and len(docs) > 0:
            docs = self._rerank(query, docs)

        # Step 3: Limit to k
        return docs[:k]

    def _vector_retrieve(
        self,
        query: str,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Pure vector search."""
        return self.vectorstore.similarity_search(
            query,
            k=config.retrieval_k,
            filter=filter,
        )

    def _hybrid_retrieve(
        self,
        query: str,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Hybrid search с Reciprocal Rank Fusion.

        RRF Score = sum(1 / (k + rank_i)) для каждого retriever
        где k = 60 (константа сглаживания)

        Это позволяет комбинировать ранги из разных источников
        без необходимости нормализовать scores.
        """
        # Vector retriever
        vector_retriever = self.vectorstore.vectorstore.as_retriever(
            search_kwargs={"k": config.retrieval_k}
        )

        # Ensemble с весами
        # alpha = 0.7 означает 70% веса vector, 30% веса BM25
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, self.bm25_retriever],
            weights=[self.hybrid_alpha, 1 - self.hybrid_alpha],
        )

        docs = ensemble.invoke(query)
        logger.debug(f"Hybrid search returned {len(docs)} documents")
        return docs

    def _rerank(
        self,
        query: str,
        documents: List[Document]
    ) -> List[Document]:
        """
        Reranking с Cohere.

        Cross-encoder оценивает каждую пару (query, document)
        и возвращает relevance score.
        """
        if not documents:
            return []

        try:
            # Cohere rerank через LangChain
            compressed_docs = self.reranker.compress_documents(
                documents=documents,
                query=query,
            )
            logger.debug(f"Reranking: {len(documents)} -> {len(compressed_docs)} documents")
            return list(compressed_docs)
        except Exception as e:
            logger.warning(f"Reranking failed: {e}. Returning original docs.")
            return documents

    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[Tuple[Document, float]]:
        """Retrieval с relevance scores (для отладки и UI)."""
        k = k or config.final_k
        return self.vectorstore.similarity_search_with_score(query, k=k)
```

---

## Step 7: RAG Chain

```python
# rag/chain.py
"""
RAG Chain - основной пайплайн вопрос-ответ.

Два подхода (по документации LangChain 2025):
1. RAG Agent: LLM решает когда искать (гибко, 2+ вызова LLM)
2. RAG Chain: всегда ищет (быстро, 1 вызов LLM)

Мы используем Chain для предсказуемости и скорости.
"""
from typing import List, Dict, Any, Optional, Generator
import logging

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from .retriever import HybridRetriever
from .config import config

logger = logging.getLogger(__name__)


# === PROMPT ENGINEERING ===
# Критически важный компонент! Плохой промпт = галлюцинации.

SYSTEM_PROMPT = """You are a precise assistant that answers questions based ONLY on the provided context.

## STRICT RULES:
1. Answer ONLY using information from the context below
2. If the context doesn't contain the answer, say: "I don't have enough information to answer this question based on the available documents."
3. NEVER make up information or use knowledge outside the context
4. Cite sources using [1], [2] etc. format
5. Be concise but comprehensive
6. Use the same language as the question

## Context:
{context}

## Question: {question}

## Answer:"""

# Альтернативный промпт для аналитических вопросов
ANALYTICAL_PROMPT = """You are an expert analyst. Analyze the provided context to answer the question thoroughly.

## Instructions:
1. Use ONLY the provided context
2. Structure your answer with clear sections
3. Cite sources with [1], [2] format
4. If information is incomplete, state what's missing
5. Provide actionable insights where appropriate

## Context:
{context}

## Question: {question}

## Analysis:"""


class RAGChain:
    """
    Production RAG Chain с best practices.

    Features:
    - Hybrid retrieval + reranking
    - Structured prompts с citations
    - Streaming support
    - Source tracking
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        model_name: str = config.llm_model,
        temperature: float = config.llm_temperature,
        prompt_type: str = "default",
    ):
        """
        Args:
            retriever: Configured HybridRetriever
            model_name: OpenAI model (gpt-4o, gpt-4o-mini)
            temperature: 0.0 для детерминированности, 0.3+ для креативности
            prompt_type: "default" или "analytical"
        """
        self.retriever = retriever

        # LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            # Streaming для лучшего UX
            streaming=True,
        )

        # Prompt template
        template = ANALYTICAL_PROMPT if prompt_type == "analytical" else SYSTEM_PROMPT
        self.prompt = ChatPromptTemplate.from_template(template)

        # Output parser
        self.output_parser = StrOutputParser()

    def _format_docs(self, docs: List[Document]) -> str:
        """
        Форматирует документы для контекста LLM.

        Формат:
        [1] Source: filename.pdf (page 5)
        Content here...

        [2] Source: another.md
        More content...
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            page_info = f" (page {page})" if page else ""

            formatted.append(
                f"[{i}] Source: {source}{page_info}\n{doc.page_content}"
            )

        return "\n\n---\n\n".join(formatted)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Выполняет RAG query.

        Returns:
            {
                "question": str,
                "answer": str,
                "sources": List[{
                    "content": str,
                    "source": str,
                    "score": float (if available)
                }]
            }
        """
        # Step 1: Retrieve
        docs = self.retriever.retrieve(question)

        if not docs:
            return {
                "question": question,
                "answer": "I couldn't find any relevant information in the documents.",
                "sources": []
            }

        # Step 2: Format context
        context = self._format_docs(docs)

        # Step 3: Generate
        chain = self.prompt | self.llm | self.output_parser
        answer = chain.invoke({
            "context": context,
            "question": question,
        })

        # Step 4: Format sources
        sources = [
            {
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page"),
                "chunk_id": doc.metadata.get("chunk_id"),
            }
            for doc in docs
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }

    def stream(self, question: str) -> Generator[str, None, None]:
        """
        Streaming ответ для лучшего UX.

        Использование:
            for chunk in chain.stream("What is RAG?"):
                print(chunk, end="", flush=True)
        """
        docs = self.retriever.retrieve(question)

        if not docs:
            yield "I couldn't find any relevant information in the documents."
            return

        context = self._format_docs(docs)
        chain = self.prompt | self.llm | self.output_parser

        for chunk in chain.stream({
            "context": context,
            "question": question,
        }):
            yield chunk

    async def aquery(self, question: str) -> Dict[str, Any]:
        """Async версия query для высоконагруженных приложений."""
        docs = self.retriever.retrieve(question)

        if not docs:
            return {
                "question": question,
                "answer": "I couldn't find any relevant information.",
                "sources": []
            }

        context = self._format_docs(docs)
        chain = self.prompt | self.llm | self.output_parser

        answer = await chain.ainvoke({
            "context": context,
            "question": question,
        })

        sources = [
            {
                "content": doc.page_content[:300] + "...",
                "source": doc.metadata.get("source", "Unknown"),
            }
            for doc in docs
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
```

---

## Step 8: Evaluation с RAGAS

```python
# rag/evaluation.py
"""
Evaluation RAG системы с RAGAS metrics.

RAGAS (Retrieval Augmented Generation Assessment) - стандарт индустрии.
https://docs.ragas.io/

Ключевые метрики:
1. Faithfulness - ответ основан на контексте? (anti-hallucination)
2. Answer Relevancy - ответ релевантен вопросу?
3. Context Precision - извлечённый контекст релевантен?
4. Context Recall - все нужные документы найдены?

Типичные бенчмарки (2025):
- Faithfulness > 0.9 (критично!)
- Answer Relevancy > 0.85
- Context Precision > 0.7
- Context Recall > 0.7
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationSample:
    """Один пример для evaluation."""
    question: str
    answer: str
    contexts: List[str]  # Retrieved contexts
    ground_truth: Optional[str] = None  # Правильный ответ (если есть)


class RAGEvaluator:
    """
    Evaluator для RAG системы.

    Использование:
        evaluator = RAGEvaluator()

        samples = [
            EvaluationSample(
                question="What is RAG?",
                answer="RAG is...",
                contexts=["RAG stands for..."],
                ground_truth="RAG is Retrieval Augmented Generation..."
            )
        ]

        results = evaluator.evaluate(samples)
        print(results)
    """

    def __init__(self):
        """Инициализация RAGAS."""
        try:
            from ragas import evaluate
            from ragas.metrics import (
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            )
            self.evaluate_fn = evaluate
            self.metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ]
            self._available = True
        except ImportError:
            logger.warning("RAGAS not installed. Run: pip install ragas")
            self._available = False

    def evaluate(
        self,
        samples: List[EvaluationSample],
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        Оценивает качество RAG системы.

        Args:
            samples: Список примеров для оценки
            metrics: Какие метрики считать (default: все)

        Returns:
            {"faithfulness": 0.92, "answer_relevancy": 0.88, ...}
        """
        if not self._available:
            return self._fallback_evaluate(samples)

        from datasets import Dataset

        # Преобразуем в RAGAS формат
        data = {
            "question": [s.question for s in samples],
            "answer": [s.answer for s in samples],
            "contexts": [s.contexts for s in samples],
        }

        # Ground truth нужен для context_recall
        if all(s.ground_truth for s in samples):
            data["ground_truth"] = [s.ground_truth for s in samples]

        dataset = Dataset.from_dict(data)

        # Evaluate
        results = self.evaluate_fn(
            dataset=dataset,
            metrics=self.metrics,
        )

        return dict(results)

    def _fallback_evaluate(
        self,
        samples: List[EvaluationSample]
    ) -> Dict[str, float]:
        """
        Простая оценка без RAGAS (для быстрой разработки).

        Проверяет базовые эвристики:
        - Ответ не пустой
        - Ответ использует слова из контекста
        - Ответ адекватной длины
        """
        scores = {
            "answer_not_empty": 0.0,
            "uses_context": 0.0,
            "reasonable_length": 0.0,
        }

        for sample in samples:
            # Check non-empty
            if sample.answer.strip():
                scores["answer_not_empty"] += 1

            # Check uses context words
            context_words = set()
            for ctx in sample.contexts:
                context_words.update(ctx.lower().split())
            answer_words = set(sample.answer.lower().split())
            overlap = len(context_words & answer_words)
            if overlap > 5:
                scores["uses_context"] += 1

            # Check reasonable length
            if 50 < len(sample.answer) < 2000:
                scores["reasonable_length"] += 1

        # Normalize
        n = len(samples)
        return {k: v / n for k, v in scores.items()}


def create_test_dataset(
    questions: List[str],
    ground_truths: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Создаёт тестовый датасет для evaluation.

    Рекомендации по созданию тестов:
    1. Включайте разные типы вопросов (factoid, analytical, comparison)
    2. Добавляйте edge cases (вопросы без ответа в документах)
    3. Минимум 20-50 примеров для статистической значимости
    4. Регулярно обновляйте при изменении данных
    """
    dataset = []
    for i, q in enumerate(questions):
        item = {"question": q}
        if ground_truths and i < len(ground_truths):
            item["ground_truth"] = ground_truths[i]
        dataset.append(item)
    return dataset
```

---

## Step 9: Streamlit UI

```python
# app.py
"""
Streamlit UI для RAG Chatbot.

Запуск: streamlit run app.py
"""
import os
from pathlib import Path
import logging

import streamlit as st
from dotenv import load_dotenv

from rag.document_loader import DocumentLoader
from rag.chunking import get_chunker
from rag.vectorstore import get_vectorstore
from rag.retriever import HybridRetriever
from rag.chain import RAGChain
from rag.config import config

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="[BOT]",
    layout="wide"
)


# === Session State Initialization ===
def init_session_state():
    """Инициализация состояния сессии."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = get_vectorstore()

    if "documents" not in st.session_state:
        st.session_state.documents = []

    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None


init_session_state()


# === Sidebar: Document Management ===
with st.sidebar:
    st.title("[DOC] Document Management")

    # Upload
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                loader = DocumentLoader()
                chunker = get_chunker("recursive")

                # Temp save
                temp_dir = Path("./temp_uploads")
                temp_dir.mkdir(exist_ok=True)

                all_chunks = []
                for file in uploaded_files:
                    file_path = temp_dir / file.name
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())

                    # Load and chunk
                    docs = loader.load_file(str(file_path))
                    chunks = chunker.split(docs)
                    all_chunks.extend(chunks)

                    st.write(f"- {file.name}: {len(chunks)} chunks")

                # Add to vectorstore
                st.session_state.vectorstore.add_documents(all_chunks)
                st.session_state.documents.extend(all_chunks)

                # Initialize RAG chain
                retriever = HybridRetriever(
                    documents=st.session_state.documents,
                    vectorstore=st.session_state.vectorstore,
                )
                st.session_state.rag_chain = RAGChain(retriever)

                st.success(f"Processed {len(all_chunks)} chunks from {len(uploaded_files)} files")

                # Cleanup
                for file in temp_dir.glob("*"):
                    file.unlink()

    st.divider()

    # Stats
    try:
        if hasattr(st.session_state.vectorstore, 'get_stats'):
            stats = st.session_state.vectorstore.get_stats()
            st.metric("Documents in DB", stats.get("vectors_count", 0))
    except Exception:
        st.metric("Documents loaded", len(st.session_state.documents))

    # Settings
    st.subheader("[GEAR] Settings")

    retrieval_k = st.slider(
        "Number of sources",
        min_value=1,
        max_value=10,
        value=config.final_k,
        help="How many documents to retrieve"
    )

    use_hybrid = st.checkbox(
        "Hybrid Search",
        value=config.use_hybrid_search,
        help="Combine vector + keyword search"
    )

    use_rerank = st.checkbox(
        "Reranking",
        value=config.use_reranking,
        help="Use Cohere reranker for better precision"
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# === Main Chat Interface ===
st.title("[BOT] RAG Chatbot")
st.caption("Ask questions about your documents")

# Check if system is ready
if not st.session_state.rag_chain:
    st.info("Please upload documents in the sidebar to get started.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("[DOC] Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**[{i}] {source['source']}**")
                    st.caption(source["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    if not st.session_state.rag_chain:
        st.warning("Please upload documents first!")
    else:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.rag_chain.query(prompt)

                st.markdown(result["answer"])

                # Show sources
                if result["sources"]:
                    with st.expander("[DOC] Sources"):
                        for i, source in enumerate(result["sources"], 1):
                            st.markdown(f"**[{i}] {source['source']}**")
                            st.caption(source["content"])

        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
```

---

## Step 10: Типичные ошибки и как их избежать

### 80% RAG проектов терпят неудачу. Вот почему:

По данным [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/07/silent-killers-of-production-rag/), большинство enterprise RAG проектов не доходят до production. Основные причины:

| Проблема | Симптомы | Решение |
|----------|----------|---------|
| **Плохой chunking** | Ответы неточные, контекст обрывается | Используйте recursive/semantic chunking, 256-512 токенов |
| **Только vector search** | Пропускает точные термины, аббревиатуры | Hybrid search (vector + BM25) |
| **Нет reranking** | Много нерелевантных документов в контексте | Добавьте Cohere/BGE reranker |
| **Монолитная knowledge base** | Разные типы данных требуют разных стратегий | Разделите по доменам, настройте отдельно |
| **Vendor lock-in** | Зависимость от одного LLM/API | Абстракции, fallback на другие модели |
| **Нет мониторинга** | Не знаете когда система деградирует | LangFuse/LangSmith с метриками |
| **Устаревшие данные** | Knowledge base не обновляется | Автоматический re-indexing pipeline |

### Debugging checklist:

```python
# Чек-лист диагностики RAG системы

def diagnose_rag_issues(rag_chain, test_questions):
    """
    Диагностика типичных проблем.
    """
    issues = []

    for q in test_questions:
        result = rag_chain.query(q)

        # 1. Пустой retrieval
        if not result["sources"]:
            issues.append({
                "type": "empty_retrieval",
                "question": q,
                "fix": "Проверьте: документы загружены? Embeddings совпадают?"
            })
            continue

        # 2. Irrelevant sources
        # Здесь можно добавить автоматическую проверку relevance

        # 3. Hallucination (ответ не основан на источниках)
        # Требует RAGAS evaluation

        # 4. Incomplete answer
        if len(result["answer"]) < 50:
            issues.append({
                "type": "short_answer",
                "question": q,
                "fix": "Возможно, недостаточно контекста или слишком строгий prompt"
            })

    return issues
```

---

## Step 11: Production Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - RAG_VECTORSTORE_TYPE=qdrant
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant
    volumes:
      - ./documents:/app/documents

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p documents data

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Запуск

```bash
# Development
streamlit run app.py

# Production с Docker
docker-compose up -d

# Откроется: http://localhost:8501
```

---

## 8 архитектур RAG (2025)

По материалам [Humanloop](https://humanloop.com/blog/rag-architectures):

1. **Simple RAG** - базовый retrieval + generation
2. **RAG with Memory** - сохраняет контекст диалога
3. **Branched RAG** - выбирает нужный source по типу вопроса
4. **HyDE** - генерирует гипотетический ответ для улучшения поиска
5. **Adaptive RAG** - динамически выбирает стратегию retrieval
6. **Corrective RAG (CRAG)** - проверяет релевантность и повторяет поиск
7. **Self-RAG** - модель сама решает когда и что искать
8. **Agentic RAG** - агенты координируют сложные multi-step запросы

**Рекомендация:** Начните с Simple RAG + Hybrid Search + Reranking. Это покрывает 90% use cases.

---

## Метрики качества (RAGAS)

Ключевые метрики по [RAGAS Documentation](https://docs.ragas.io/en/latest/concepts/metrics/):

| Метрика | Что измеряет | Target |
|---------|-------------|--------|
| **Faithfulness** | Ответ основан на контексте (anti-hallucination) | > 0.9 |
| **Answer Relevancy** | Ответ релевантен вопросу | > 0.85 |
| **Context Precision** | Извлечённые документы релевантны | > 0.7 |
| **Context Recall** | Все нужные документы найдены | > 0.7 |

```python
# Пример evaluation
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

results = evaluate(
    dataset=test_dataset,
    metrics=[faithfulness, answer_relevancy]
)
print(results)
# {"faithfulness": 0.92, "answer_relevancy": 0.88}
```

---

## Observability

Для production обязательно добавьте мониторинг:

**LangFuse** (open-source, self-hosted):
- Tracing каждого запроса
- Latency breakdown (retrieval vs generation)
- Cost tracking
- A/B тестирование промптов

```python
# Интеграция LangFuse
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler()

chain.invoke(
    {"question": "What is RAG?"},
    config={"callbacks": [langfuse_handler]}
)
```

**LangSmith** (managed, LangChain team):
- Глубокая интеграция с LangChain
- Production monitoring
- Debugging tools

Источники: [LangFuse](https://langfuse.com/blog/2025-10-28-rag-observability-and-evals), [LangSmith](https://www.metacto.com/blogs/what-is-langsmith-a-comprehensive-guide-to-llm-observability)

---

## Production Checklist

Перед запуском в production убедитесь:

### Indexing Pipeline
- [ ] Документы загружаются без ошибок (проверить все форматы)
- [ ] Chunk size оптимален (256-512 токенов для factoid, 1024+ для аналитики)
- [ ] Chunk overlap 10-20% сохраняет контекст
- [ ] Metadata включает source, page, timestamp

### Retrieval Quality
- [ ] Hybrid search включён (vector + BM25)
- [ ] Reranking включён (Cohere или BGE)
- [ ] Тестовый датасет из 20+ вопросов создан
- [ ] Context Precision > 0.7
- [ ] Context Recall > 0.7

### Generation Quality
- [ ] Промпт явно запрещает галлюцинации
- [ ] Faithfulness > 0.9 (проверено через RAGAS)
- [ ] Answer Relevancy > 0.85
- [ ] Ответы содержат citations [1], [2]

### Operations
- [ ] Observability настроен (LangFuse/LangSmith)
- [ ] Latency < 3s на p95
- [ ] Error handling для API failures
- [ ] Rate limiting настроен
- [ ] Costs мониторятся

### Security
- [ ] API keys в environment variables
- [ ] Пользовательский ввод санитизируется
- [ ] PII не сохраняется в логах

---

## Куда дальше

После освоения базового RAG, изучите продвинутые техники:

```
Этот tutorial (Simple RAG)
        │
        ├── Улучшение Retrieval
        │   ├── [[rag-advanced-techniques]] → HyDE, Query Expansion
        │   ├── [[embeddings-complete-guide]] → Fine-tuning embeddings
        │   └── [[vector-databases-guide]] → Scaling, production
        │
        ├── Улучшение Generation
        │   ├── [[prompt-engineering-masterclass]] → Structured outputs
        │   └── [[ai-cost-optimization]] → Уменьшение costs
        │
        └── Production
            ├── [[ai-observability-monitoring]] → Monitoring, alerts
            └── [[ai-devops-deployment]] → Kubernetes, autoscaling
```

**Следующий уровень:**
- **Agentic RAG** — LLM сам решает когда и что искать
- **Multi-modal RAG** — поиск по изображениям и видео
- **Self-RAG** — модель оценивает качество своих ответов

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Lewis P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401 | Формализация RAG |
| 2 | Malkov Y., Yashunin D. (2018). *Efficient and Robust Approximate Nearest Neighbor using HNSW Graphs*. arXiv:1603.09320 | HNSW — основа vector search |
| 3 | Cormack G. et al. (2009). *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*. SIGIR | RRF для hybrid search |
| 4 | Es S. et al. (2023). *RAGAS: Automated Evaluation of RAG*. arXiv:2309.15217 | Метрики качества RAG |
| 5 | Nogueira R., Cho K. (2019). *Passage Re-ranking with BERT*. arXiv:1901.04085 | Cross-encoder reranking |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [LangChain RAG Tutorial](https://docs.langchain.com/oss/python/langchain/rag) | Официальный tutorial |
| 2 | [Humanloop: 8 RAG Architectures](https://humanloop.com/blog/rag-architectures) | Архитектурные паттерны |
| 3 | [Weaviate: Chunking Strategies](https://weaviate.io/blog/chunking-strategies-for-rag) | Стратегии chunking |
| 4 | [Cohere Rerank](https://cohere.com/rerank) | Reranking API |
| 5 | [RAGAS Documentation](https://docs.ragas.io/en/stable/) | RAG evaluation |
- [FutureAGI: RAG Evaluation Metrics 2025](https://futureagi.com/blogs/rag-evaluation-metrics-2025)
- [Cohorte: Evaluating RAG Systems in 2025](https://www.cohorte.co/blog/evaluating-rag-systems-in-2025-ragas-deep-dive-giskard-showdown-and-the-future-of-context)

### Observability
- [LangFuse: RAG Observability](https://langfuse.com/blog/2025-10-28-rag-observability-and-evals)
- [Langflow: LLM Observability Explained](https://www.langflow.org/blog/llm-observability-explained-feat-langfuse-langsmith-and-langwatch)
- [Firecrawl: Best LLM Observability Tools](https://www.firecrawl.dev/blog/best-llm-observability-tools)

---

## Связанные заметки

- [[rag-advanced-techniques]] - Продвинутые RAG техники (Agentic RAG, Self-RAG)
- [[embeddings-complete-guide]] - Embeddings модели и fine-tuning
- [[vector-databases-guide]] - Детальное сравнение vector databases
- [[ai-observability-monitoring]] - Мониторинг AI систем
- [[langchain-masterclass]] - Глубокое погружение в LangChain

---

## Проверь себя

> [!question]- Какие компоненты нужны для production-ready RAG chatbot?
> Document loader + chunker, embedding model, vector store (Qdrant/ChromaDB), retrieval pipeline (query -> search -> rerank), LLM для generation, chat memory (conversation history), и frontend (Streamlit/Gradio или API). Для production добавить: evaluation, caching, rate limiting, observability.

> [!question]- Как организовать conversation memory в RAG chatbot?
> Short-term: последние N сообщений в контексте (window memory). Long-term: summarization предыдущих сообщений. Для RAG: chat history используется для reformulation запроса (standalone question), чтобы retrieval работал правильно. Пример: "А что насчёт цены?" -> "Какова цена продукта X, упомянутого ранее?"

> [!question]- Как оценить качество RAG chatbot и какие метрики использовать?
> Retrieval: precision@k, recall@k, MRR. Generation: faithfulness (нет hallucination), relevance (ответ по теме), completeness. End-to-end: answer correctness vs ground truth. User metrics: satisfaction score, follow-up rate. Инструменты: RAGAS framework для автоматической оценки.

> [!question]- Какие ошибки часто допускают при создании RAG chatbot?
> Слишком большие/маленькие chunks, отсутствие overlap, игнорирование metadata при retrieval, нет reranking (полагаются только на embedding similarity), нет evaluation pipeline, и отсутствие fallback для вопросов вне scope документов.

---

## Ключевые карточки

Из каких этапов состоит RAG pipeline?
?
Indexing: load documents -> chunk -> embed -> store in vector DB. Retrieval: user query -> embed -> similarity search -> (optional) rerank -> top-k chunks. Generation: retrieved chunks + query -> LLM prompt -> answer. Evaluation: automated metrics + human feedback.

Что такое reranking и зачем он нужен в RAG?
?
Повторное ранжирование retrieved документов с помощью cross-encoder модели (Cohere Rerank, bge-reranker). Embedding search (bi-encoder) быстрый но approximate. Reranker точнее оценивает relevance пары (query, document). Типичный flow: retrieve 20 -> rerank -> top 5.

Как выбрать vector store для RAG chatbot?
?
Прототип: ChromaDB (in-memory, простой). Production: Qdrant (Rust, быстрый, self-hosted), Pinecone (managed, масштабируемый). PostgreSQL проект: pgvector. Критерии: масштаб данных, hosting preference, filtering capabilities, и стоимость.

Что такое hybrid search и когда его использовать?
?
Комбинация semantic search (embeddings) и keyword search (BM25). Semantic находит семантически похожие документы, keyword --- точные совпадения терминов. Hybrid даёт лучшие результаты для технических документов, где важны и смысл, и точные термины. Qdrant и Weaviate поддерживают нативно.

Как деплоить RAG chatbot в production?
?
Backend: FastAPI/Flask с async, vector store как отдельный сервис. Frontend: Streamlit (быстро), React (полноценный UI). Infra: Docker Compose для dev, Kubernetes для production. Мониторинг: LangSmith/Langfuse для traces, Prometheus для infra. Кэширование: semantic cache для частых вопросов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[tutorial-document-qa]] | Специализированная Document Q&A система |
| Углубиться | [[rag-advanced-techniques]] | Продвинутые техники RAG |
| Смежная тема | [[api-design]] | Проектирование API для chatbot |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI Engineering |

*Проверено: 2026-01-09*
