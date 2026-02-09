---
title: "Практикум: Document Q&A System"
tags: [ai, rag, documents, pdf, qa, tutorial, python, pydantic, extraction]
category: ai-engineering
date: 2025-12-24
status: complete
level: intermediate
related:
  - "[[tutorial-rag-chatbot]]"
  - "[[embeddings-vector-databases]]"
  - "[[langchain-ecosystem]]"
---

# Практикум: Document Q&A с извлечением структурированных данных

> **TL;DR**: Создаем production-ready систему для работы с документами: извлечение данных из PDF, structured outputs с Pydantic AI, сравнение документов и цитирование источников. Обзор современных инструментов 2025: Docling, LlamaParse, PyMuPDF4LLM, Mistral OCR.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Python основы** | Весь код примеров на Python | Любой курс Python |
| **RAG основы** | Document QA — это специализированный RAG | [[tutorial-rag-chatbot]] |
| **Pydantic** | Structured outputs используют Pydantic схемы | [Pydantic docs](https://docs.pydantic.dev/) |
| **Vector databases** | Хранение и поиск chunks документов | [[vector-databases-guide]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ С подготовкой | Сначала изучи RAG основы |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | Фокус на production-паттерны |

### Терминология для новичков

> 💡 **Document Q&A** = система, которая извлекает **точные данные** из документов (не просто "примерно отвечает", а возвращает конкретные суммы, даты, условия)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Structured Output** | Ответ LLM в строгом формате (JSON, Pydantic) | **Анкета vs письмо** — анкета имеет поля, письмо свободное |
| **Docling** | IBM библиотека для извлечения текста из PDF | **Сканер документов** — превращает PDF в текст |
| **LlamaParse** | SaaS сервис для парсинга сложных PDF | **Профессиональный OCR** — платный, но очень точный |
| **Pydantic AI** | Framework для LLM с типизированными выходами | **Strict TypeScript для LLM** — LLM не может отклониться от схемы |
| **GraphRAG** | RAG с knowledge graph для связей | **Карта связей** — находит как сущности связаны между собой |
| **Hybrid Search** | Vector + keyword поиск вместе | **Google + точный поиск** — понимает смысл И ищет термины |
| **Reranking** | Переранжирование результатов cross-encoder'ом | **Второе мнение эксперта** — точнее оценивает релевантность |
| **Citation** | Ссылка на источник в ответе | **Сноска в книге** — откуда взята информация |
| **Chunking** | Разбиение документа на части | **Нарезка пиццы** — большой документ делим на куски |

---

## Зачем это нужно

### Проблема: Неструктурированные данные в документах

| Проблема | Пример | Последствия |
|----------|--------|-------------|
| **Ручной ввод данных** | Перенос данных из PDF-счетов в ERP | Ошибки, потеря времени |
| **Поиск информации** | "Какие условия оплаты в контракте?" | Часы на чтение документов |
| **Сравнение версий** | Два варианта договора — что изменилось? | Риск пропустить важное |
| **Соответствие требованиям** | Проверка compliance в 100+ документах | Невозможно вручную |

**80% корпоративных данных** — неструктурированные документы (PDF, DOCX, сканы). Традиционный RAG отвечает "примерно" — а бизнесу нужны **точные данные**: даты, суммы, стороны договора.

### Что даёт Document Q&A

```
Обычный RAG:                    Document Q&A:
┌─────────────────────┐         ┌─────────────────────┐
│ "Сумма около        │         │ {                   │
│  10000 долларов"    │         │   "total": 10450.00,│
│                     │         │   "currency": "USD",│
│ (свободный текст)   │         │   "tax": 450.00     │
└─────────────────────┘         │ }                   │
                                │ + цитата + страница │
                                └─────────────────────┘
```

**Результат:** Точные структурированные данные, готовые для интеграции с ERP, CRM, базами данных.

### Актуальность 2024-2025

| Инструмент | Статус | Что нового |
|------------|--------|------------|
| **Pydantic AI** | ✅ Production-ready | Structured outputs как first-class feature |
| **Docling (IBM)** | ✅ Open-source | 97.9% точность таблиц, MIT лицензия |
| **LlamaParse** | ✅ SaaS | ~99% точность, multimodal parsing |
| **GraphRAG** | ✅ Microsoft | Knowledge graphs для связей между сущностями |
| **Mistral OCR** | 🆕 2024 | 2000 стр/мин, отличное качество |

**Тренды 2025:**
- Structured outputs — killer feature для production LLM
- Vision-language модели (Gemini 2.0, GPT-4o) для document understanding
- Hybrid search (vector + keyword) становится стандартом

---

## Что такое Document Q&A

**Document Q&A** (Document Question Answering) - это задача получения ответов на вопросы пользователя на основе содержимого документов. В отличие от базового RAG, здесь фокус на:

- **Точном извлечении данных** - даты, суммы, имена, условия контрактов
- **Цитировании источников** - каждый ответ подкреплен ссылкой на документ и страницу
- **Структурированном выводе** - результат в формате JSON/Pydantic, а не свободный текст
- **Сравнении документов** - анализ различий между версиями контрактов

```
+------------------------------------------------------------------+
|                    Document Q&A System                            |
+------------------------------------------------------------------+
|                                                                   |
|  Documents ---> Extraction ---> Chunking ---> Vector Store        |
|  (PDF, DOCX)        |              |              |               |
|                     v              v              v               |
|               +----------+   +----------+   +----------+          |
|               | Tables   |   | Markdown |   | ChromaDB |          |
|               +----------+   +----------+   +----------+          |
|                                                   |               |
|  User Query --------------------------------------+               |
|       |                                                           |
|       v                                                           |
|  +--------------------------------------------------------+       |
|  |              Structured QA Chain                        |       |
|  |  - Answer with citations                                |       |
|  |  - Extract structured data (Pydantic)                   |       |
|  |  - Compare documents                                    |       |
|  +--------------------------------------------------------+       |
|                          |                                        |
|                          v                                        |
|              JSON / Pydantic Response                             |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Ландшафт инструментов 2025

### PDF Extraction: сравнение подходов

Качество RAG напрямую зависит от качества извлечения текста из документов. В 2025 году существует несколько подходов:

| Инструмент | Тип | Точность таблиц | Скорость | OCR | Лицензия |
|------------|-----|-----------------|----------|-----|----------|
| **[Docling](https://docling-project.github.io/docling/)** | Open-source (IBM) | 97.9% | Средняя | Да | MIT |
| **[LlamaParse](https://www.llamaindex.ai/llamaparse)** | SaaS | ~99% | ~6 сек/док | Да | Proprietary |
| **[PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/)** | Open-source | Хорошая | Быстрая | Нет | AGPL/Commercial |
| **[Mistral OCR](https://docs.mistral.ai/)** | API | Отличная | ~2000 стр/мин | Да | Proprietary |
| **Unstructured.io** | Open-source/SaaS | Средняя | Средняя | Да | Apache 2.0 |

#### Docling (IBM Granite-Docling)

[Docling](https://github.com/DS4SD/docling) - открытый инструмент от IBM Research, который стал стандартом для enterprise RAG:

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("contract.pdf")

# Markdown с сохранением структуры
markdown = result.document.export_to_markdown()

# Структурированный JSON
json_output = result.document.export_to_dict()
```

**Преимущества:**
- Сохраняет структуру документа (таблицы, заголовки, списки)
- Использует AI-модели DocLayNet и TableFormer
- 258M параметров - работает на обычном ноутбуке
- Интеграция с LangChain и LlamaIndex

**[Granite-Docling](https://www.ibm.com/new/announcements/granite-docling-end-to-end-document-conversion)** (2025) - эволюция с vision-language моделью, сохраняющая связь с исходным контентом.

#### LlamaParse

[LlamaParse](https://www.llamaindex.ai/llamaparse) - коммерческий сервис от LlamaIndex для сложных документов:

```python
from llama_parse import LlamaParse

parser = LlamaParse(
    api_key="...",
    result_type="markdown",
    parsing_instruction="Extract all tables with full precision"
)

documents = parser.load_data("financial_report.pdf")
```

**Преимущества:**
- Почти 99% точность на сложных документах
- Multimodal parsing (диаграммы, графики)
- Markdown сохраняет структуру для chunking
- 1000 страниц/день бесплатно

#### PyMuPDF4LLM

[PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) - быстрое извлечение в Markdown, оптимизированное для LLM:

```python
import pymupdf4llm

# Простое извлечение
md_text = pymupdf4llm.to_markdown("input.pdf")

# С разбиением по страницам
pages = pymupdf4llm.to_markdown("input.pdf", page_chunks=True)

# С извлечением изображений
md_with_images = pymupdf4llm.to_markdown(
    "input.pdf",
    write_images=True,
    image_path="./images"
)
```

**Ограничения:** Не работает со сканированными документами (нет OCR).

---

## Structured Output: ключ к надежности

### Почему structured output важен

Structured output - "killer app для LLM" ([Simon Willison, 2025](https://simonwillison.net/2025/Feb/28/llm-schemas/)). Преимущества:

1. **Гарантированный формат** - LLM не может вернуть невалидный JSON
2. **Типизация** - Pydantic валидирует данные на runtime
3. **Интеграция** - Downstream системы получают предсказуемый ввод
4. **Снижение галлюцинаций** - Жесткая схема ограничивает "творчество" модели

### Pydantic AI Framework

[Pydantic AI](https://ai.pydantic.dev/) - agent framework от создателей Pydantic, приносящий "FastAPI feeling" в GenAI разработку:

```python
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from datetime import date

class Invoice(BaseModel):
    """Схема для извлечения данных из счета."""
    invoice_number: str = Field(description="Номер счета")
    invoice_date: date = Field(description="Дата выставления")
    total_amount: float = Field(description="Итоговая сумма")
    currency: str = Field(default="USD", description="Валюта")
    vendor_name: str = Field(description="Название поставщика")
    items: list[dict] = Field(default_factory=list, description="Позиции счета")

# Создаем агента с типизированным выходом
agent = Agent(
    "openai:gpt-4o",
    output_type=Invoice,
    system_prompt="Extract invoice data from the document. Be precise with numbers and dates."
)

# Извлекаем данные
result = await agent.run(document_text)
invoice: Invoice = result.output  # Pydantic модель, готовая к использованию
```

**Ключевые возможности Pydantic AI:**

- **Model-agnostic** - OpenAI, Anthropic, Gemini, DeepSeek, Ollama и др.
- **Streamed outputs** - Потоковый вывод с валидацией в реальном времени
- **Tool use** - Инструменты как typed functions
- **Dependency injection** - Контекст и зависимости через RunContext
- **MCP integration** - Model Context Protocol для внешних инструментов

### Альтернативы: LangChain with_structured_output

LangChain также поддерживает structured output через `with_structured_output()`:

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class ContractSummary(BaseModel):
    parties: list[str] = Field(description="Стороны контракта")
    effective_date: str = Field(description="Дата вступления в силу")
    term_months: int = Field(description="Срок действия в месяцах")
    total_value: float = Field(description="Сумма контракта")
    key_obligations: list[str] = Field(description="Основные обязательства")

llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm = llm.with_structured_output(ContractSummary)

result = structured_llm.invoke(f"Extract contract details:\n\n{contract_text}")
```

### Instructor: универсальный подход

[Instructor](https://github.com/jxnl/instructor) - библиотека для structured extraction с любым LLM:

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())

class Citation(BaseModel):
    quote: str
    page: int
    document: str

class AnswerWithCitations(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float

response = client.chat.completions.create(
    model="gpt-4o",
    response_model=AnswerWithCitations,
    messages=[
        {"role": "system", "content": "Answer based on documents. Include citations."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
    ]
)
```

---

## Продвинутые RAG-паттерны для Document QA

### GraphRAG: связи между сущностями

[GraphRAG](https://microsoft.github.io/graphrag/) (Microsoft) строит knowledge graph из документов:

```
Traditional RAG: Query -> Vector Search -> Chunks -> LLM -> Answer

GraphRAG: Query -> Graph Traversal -> Related Entities -> Context -> LLM -> Answer
```

**Преимущества для Document QA:**
- Находит связи, неочевидные при vector search
- Лучше отвечает на вопросы типа "Какие компании связаны с X?"
- Explainability - можно показать путь рассуждений

```python
from graphrag import GraphRAG

# Построение графа
graph = GraphRAG()
graph.build_from_documents(documents)

# Запрос с traversal
result = graph.query(
    "What are the payment obligations of Party A?",
    traversal_depth=2  # До 2 связей от найденных entities
)
```

### Hybrid Search: лучшее из двух миров

Комбинация vector search (семантика) и keyword search (BM25):

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma

# Vector retriever
vector_store = Chroma.from_documents(documents, embeddings)
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# BM25 retriever
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# Ensemble с весами
ensemble = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # 70% семантика, 30% keywords
)
```

### Reranking: улучшение top-k

После первичного retrieval применяем cross-encoder для reranking:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# Base retriever возвращает больше документов
base_retriever = vector_store.as_retriever(search_kwargs={"k": 20})

# Reranker оставляет лучшие
reranker = CohereRerank(model="rerank-v3.5", top_n=5)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)
```

---

## Практическая реализация

### Структура проекта

```
document-qa/
├── pyproject.toml
├── .env
├── documents/
│   ├── contracts/
│   ├── invoices/
│   └── reports/
├── src/
│   ├── __init__.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── docling_extractor.py   # IBM Docling
│   │   ├── pymupdf_extractor.py   # PyMuPDF4LLM
│   │   └── llama_extractor.py     # LlamaParse
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── chunker.py             # Smart chunking
│   │   └── embeddings.py
│   ├── qa/
│   │   ├── __init__.py
│   │   ├── structured.py          # Pydantic AI extraction
│   │   └── citations.py           # QA with citations
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── invoice.py
│   │   ├── contract.py
│   │   └── common.py
│   └── vectorstore.py
├── api.py                         # FastAPI
└── cli.py                         # CLI interface
```

### Зависимости

```toml
[project]
name = "document-qa"
version = "2.0.0"
requires-python = ">=3.11"
dependencies = [
    # Extraction
    "docling>=2.15.0",
    "pymupdf4llm>=0.0.17",
    "llama-parse>=0.5.0",

    # LLM & RAG
    "pydantic-ai>=0.0.39",
    "langchain>=0.3.14",
    "langchain-openai>=0.2.14",
    "langchain-chroma>=0.2.0",

    # Vector Store
    "chromadb>=0.5.23",

    # Utilities
    "pydantic>=2.10.0",
    "python-dotenv>=1.0.0",
    "rich>=13.9.0",

    # API
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
]
```

### Extractor с выбором backend

```python
"""
src/extractors/factory.py
Фабрика для выбора экстрактора на основе документа.
"""
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import hashlib


class ExtractorType(Enum):
    DOCLING = "docling"
    PYMUPDF = "pymupdf"
    LLAMAPARSE = "llamaparse"
    AUTO = "auto"


@dataclass
class ExtractedDocument:
    """Унифицированный результат извлечения."""
    filename: str
    file_hash: str
    markdown: str
    pages: list[dict]  # [{"page": 1, "content": "..."}, ...]
    tables: list[str]
    metadata: dict


class BaseExtractor(ABC):
    """Базовый класс для экстракторов."""

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractedDocument:
        pass

    def _compute_hash(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]


class DoclingExtractor(BaseExtractor):
    """IBM Docling - лучший выбор для enterprise документов."""

    def extract(self, file_path: Path) -> ExtractedDocument:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(str(file_path))

        doc = result.document
        markdown = doc.export_to_markdown()

        # Извлекаем страницы
        pages = []
        for i, page in enumerate(doc.pages):
            pages.append({
                "page": i + 1,
                "content": page.export_to_markdown() if hasattr(page, 'export_to_markdown') else ""
            })

        # Извлекаем таблицы
        tables = []
        for table in doc.tables:
            tables.append(table.export_to_markdown())

        return ExtractedDocument(
            filename=file_path.name,
            file_hash=self._compute_hash(file_path),
            markdown=markdown,
            pages=pages,
            tables=tables,
            metadata={"format": file_path.suffix, "extractor": "docling"}
        )


class PyMuPDFExtractor(BaseExtractor):
    """PyMuPDF4LLM - быстрый вариант для нативных PDF."""

    def extract(self, file_path: Path) -> ExtractedDocument:
        import pymupdf4llm

        # Извлекаем с разбиением по страницам
        page_data = pymupdf4llm.to_markdown(
            str(file_path),
            page_chunks=True,
            show_progress=False
        )

        pages = []
        tables = []
        full_text_parts = []

        for i, page in enumerate(page_data):
            content = page.get("text", "")
            pages.append({"page": i + 1, "content": content})
            full_text_parts.append(content)

            # Извлекаем таблицы из markdown
            tables.extend(self._extract_tables(content))

        return ExtractedDocument(
            filename=file_path.name,
            file_hash=self._compute_hash(file_path),
            markdown="\n\n---\n\n".join(full_text_parts),
            pages=pages,
            tables=tables,
            metadata={"format": "PDF", "extractor": "pymupdf4llm"}
        )

    def _extract_tables(self, markdown: str) -> list[str]:
        """Извлекает markdown таблицы."""
        tables = []
        lines = markdown.split("\n")
        table_lines = []
        in_table = False

        for line in lines:
            if line.startswith("|"):
                in_table = True
                table_lines.append(line)
            elif in_table:
                if table_lines:
                    tables.append("\n".join(table_lines))
                    table_lines = []
                in_table = False

        if table_lines:
            tables.append("\n".join(table_lines))

        return tables


class ExtractorFactory:
    """Фабрика для создания экстракторов."""

    @staticmethod
    def create(
        extractor_type: ExtractorType = ExtractorType.AUTO,
        file_path: Path | None = None
    ) -> BaseExtractor:

        if extractor_type == ExtractorType.AUTO and file_path:
            # Автоопределение на основе файла
            suffix = file_path.suffix.lower()
            if suffix in [".pdf"]:
                # Проверяем, нужен ли OCR
                return PyMuPDFExtractor()  # Быстрее для нативных PDF
            elif suffix in [".docx", ".pptx", ".xlsx"]:
                return DoclingExtractor()  # Лучше для Office

        extractors = {
            ExtractorType.DOCLING: DoclingExtractor,
            ExtractorType.PYMUPDF: PyMuPDFExtractor,
        }

        return extractors.get(extractor_type, DoclingExtractor)()
```

### Pydantic-схемы для extraction

```python
"""
src/schemas/invoice.py
Схема для структурированного извлечения данных из счетов.
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class MonetaryAmount(BaseModel):
    """Денежная сумма с валютой."""
    amount: float = Field(description="Числовое значение суммы")
    currency: str = Field(default="USD", description="Код валюты ISO 4217")


class VendorInfo(BaseModel):
    """Информация о поставщике."""
    name: str = Field(description="Название компании")
    address: Optional[str] = Field(default=None, description="Адрес")
    tax_id: Optional[str] = Field(default=None, description="ИНН/Tax ID")
    email: Optional[str] = Field(default=None, description="Email")


class InvoiceItem(BaseModel):
    """Позиция в счете."""
    description: str = Field(description="Описание товара/услуги")
    quantity: float = Field(default=1.0, description="Количество")
    unit_price: MonetaryAmount = Field(description="Цена за единицу")
    total: MonetaryAmount = Field(description="Итого по позиции")


class Invoice(BaseModel):
    """Полная схема счета для extraction."""
    # Идентификация
    invoice_number: str = Field(description="Номер счета")
    invoice_date: date = Field(description="Дата выставления счета")
    due_date: Optional[date] = Field(default=None, description="Срок оплаты")

    # Стороны
    vendor: VendorInfo = Field(description="Информация о поставщике")
    customer_name: str = Field(description="Название покупателя")

    # Позиции
    items: list[InvoiceItem] = Field(
        default_factory=list,
        description="Список позиций счета"
    )

    # Суммы
    subtotal: MonetaryAmount = Field(description="Сумма до налогов")
    tax_rate: Optional[float] = Field(default=None, description="Ставка налога %")
    tax_amount: Optional[MonetaryAmount] = Field(default=None, description="Сумма налога")
    total: MonetaryAmount = Field(description="Итоговая сумма к оплате")

    # Дополнительно
    payment_terms: Optional[str] = Field(default=None, description="Условия оплаты")
    notes: Optional[str] = Field(default=None, description="Примечания")

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-2025-001",
                "invoice_date": "2025-01-15",
                "vendor": {"name": "Acme Corp", "tax_id": "12-3456789"},
                "customer_name": "Client LLC",
                "items": [
                    {
                        "description": "Consulting services",
                        "quantity": 10,
                        "unit_price": {"amount": 150.0, "currency": "USD"},
                        "total": {"amount": 1500.0, "currency": "USD"}
                    }
                ],
                "subtotal": {"amount": 1500.0, "currency": "USD"},
                "tax_rate": 10.0,
                "tax_amount": {"amount": 150.0, "currency": "USD"},
                "total": {"amount": 1650.0, "currency": "USD"}
            }
        }
```

```python
"""
src/schemas/common.py
Общие схемы для QA с цитированием.
"""
from pydantic import BaseModel, Field
from typing import Optional


class Citation(BaseModel):
    """Цитата из документа."""
    quote: str = Field(description="Точная цитата из документа")
    document: str = Field(description="Название документа")
    page: Optional[int] = Field(default=None, description="Номер страницы")


class AnswerWithCitations(BaseModel):
    """Ответ с подтверждающими цитатами."""
    answer: str = Field(description="Полный ответ на вопрос")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Цитаты, подтверждающие ответ"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Уверенность в ответе от 0 до 1"
    )

    def format_answer(self) -> str:
        """Форматирует ответ с цитатами для отображения."""
        result = [self.answer, "", "Sources:"]
        for i, c in enumerate(self.citations, 1):
            page_info = f", p.{c.page}" if c.page else ""
            result.append(f"[{i}] \"{c.quote}\" - {c.document}{page_info}")
        return "\n".join(result)


class DocumentComparison(BaseModel):
    """Результат сравнения двух документов."""
    document1: str = Field(description="Название первого документа")
    document2: str = Field(description="Название второго документа")
    key_differences: list[str] = Field(description="Ключевые различия")
    similarities: list[str] = Field(description="Общие положения")
    risk_assessment: str = Field(description="Оценка рисков")
    recommendation: str = Field(description="Рекомендация")
```

### Structured QA с Pydantic AI

```python
"""
src/qa/structured.py
Q&A система с Pydantic AI для structured outputs.
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Type, TypeVar
import os

from ..schemas.common import AnswerWithCitations, Citation, DocumentComparison
from ..schemas.invoice import Invoice
from ..vectorstore import VectorStoreManager


T = TypeVar('T', bound=BaseModel)


class StructuredQA:
    """
    Q&A система с гарантированными structured outputs.
    Использует Pydantic AI для типобезопасного извлечения.
    """

    def __init__(
        self,
        vectorstore: VectorStoreManager,
        model: str = "openai:gpt-4o",
        temperature: float = 0.0
    ):
        self.vectorstore = vectorstore
        self.model = model
        self.temperature = temperature

    async def ask_with_citations(
        self,
        question: str,
        k: int = 5
    ) -> AnswerWithCitations:
        """
        Отвечает на вопрос с цитатами из документов.

        Args:
            question: Вопрос пользователя
            k: Количество chunks для контекста

        Returns:
            AnswerWithCitations с ответом и источниками
        """
        # Получаем релевантные chunks
        results = self.vectorstore.search(question, k=k)

        # Форматируем контекст
        context_parts = []
        for doc, score in results:
            source = doc.metadata.get("filename", "unknown")
            page = doc.metadata.get("page_number", "?")
            context_parts.append(
                f"[Source: {source}, Page: {page}]\n{doc.page_content}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Создаем агента с типизированным выходом
        agent = Agent(
            self.model,
            output_type=AnswerWithCitations,
            system_prompt="""You are a document analysis assistant.
Answer questions based ONLY on the provided context.

RULES:
1. Use only information from the provided documents
2. Include direct quotes as citations
3. If information is not in documents, say "Not found in documents"
4. Rate confidence based on how well documents support your answer
5. Always cite the source document and page number

Context:
{context}
""".format(context=context)
        )

        result = await agent.run(question)
        return result.output

    async def extract_structured(
        self,
        document_text: str,
        schema: Type[T],
        instructions: str = ""
    ) -> T:
        """
        Извлекает структурированные данные из документа.

        Args:
            document_text: Текст документа
            schema: Pydantic схема для извлечения
            instructions: Дополнительные инструкции

        Returns:
            Заполненная Pydantic модель
        """
        system_prompt = f"""You are an expert document data extractor.
Extract information from the document into the specified structure.
If a field cannot be found, use null/None.

{instructions}

Document:
{document_text}
"""

        agent = Agent(
            self.model,
            output_type=schema,
            system_prompt=system_prompt
        )

        result = await agent.run("Extract the data from this document.")
        return result.output

    async def compare_documents(
        self,
        doc1_text: str,
        doc1_name: str,
        doc2_text: str,
        doc2_name: str
    ) -> DocumentComparison:
        """
        Сравнивает два документа и возвращает структурированный анализ.
        """
        system_prompt = f"""You are a legal/business document comparison expert.
Compare the two documents and identify differences, similarities, risks.

Document 1 ({doc1_name}):
{doc1_text}

---

Document 2 ({doc2_name}):
{doc2_text}
"""

        agent = Agent(
            self.model,
            output_type=DocumentComparison,
            system_prompt=system_prompt
        )

        result = await agent.run("Compare these documents and provide analysis.")
        output = result.output
        output.document1 = doc1_name
        output.document2 = doc2_name
        return output

    async def extract_invoice(self, document_text: str) -> Invoice:
        """Специализированное извлечение данных из счета."""
        return await self.extract_structured(
            document_text,
            Invoice,
            "Focus on extracting all line items with precise amounts. "
            "Pay attention to tax calculations and totals."
        )
```

### Vector Store с ChromaDB

```python
"""
src/vectorstore.py
Управление ChromaDB для Document QA.
"""
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pathlib import Path
import os


class VectorStoreManager:
    """
    Менеджер для работы с ChromaDB.
    Поддерживает multi-document search и фильтрацию.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str | None = None,
        embedding_model: str = "text-embedding-3-small"
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR", "./chroma_db"
        )

        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(
        self,
        documents: list[Document],
        doc_id: str | None = None
    ) -> list[str]:
        """Добавляет документы с опциональным doc_id для группировки."""
        if doc_id:
            for doc in documents:
                doc.metadata["doc_id"] = doc_id

        return self.vectorstore.add_documents(documents)

    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: dict | None = None,
        score_threshold: float | None = None
    ) -> list[tuple[Document, float]]:
        """Семантический поиск с опциональной фильтрацией."""
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=k, filter=filter_dict
        )

        if score_threshold:
            results = [(doc, score) for doc, score in results if score >= score_threshold]

        return results

    def search_in_document(self, query: str, doc_id: str, k: int = 5) -> list[Document]:
        """Поиск только внутри одного документа."""
        results = self.search(query, k=k, filter_dict={"doc_id": doc_id})
        return [doc for doc, _ in results]

    def get_retriever(self, search_kwargs: dict | None = None):
        """Возвращает retriever для использования в chains."""
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs or {"k": 5}
        )

    def list_documents(self) -> list[str]:
        """Возвращает список уникальных doc_id."""
        results = self.vectorstore.get()
        if results and results.get("metadatas"):
            return list({m["doc_id"] for m in results["metadatas"] if m and "doc_id" in m})
        return []

    def delete_document(self, doc_id: str) -> bool:
        """Удаляет документ по ID."""
        try:
            self.vectorstore.delete(filter={"doc_id": doc_id})
            return True
        except Exception:
            return False
```

### Smart Chunking

```python
"""
src/processing/chunker.py
Интеллектуальное разбиение с сохранением структуры.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain_core.documents import Document
from dataclasses import dataclass
import re


@dataclass
class ChunkingConfig:
    """Конфигурация chunking."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    preserve_tables: bool = True
    preserve_headers: bool = True


class SmartChunker:
    """
    Chunker, сохраняющий структуру документа.
    Таблицы и заголовки обрабатываются особым образом.
    """

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

        self.md_splitter = MarkdownTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_document(
        self,
        text: str,
        metadata: dict | None = None
    ) -> list[Document]:
        """
        Разбивает документ на chunks с сохранением контекста.

        Args:
            text: Markdown текст документа
            metadata: Метаданные документа

        Returns:
            Список Document chunks
        """
        metadata = metadata or {}

        # Извлекаем таблицы отдельно
        if self.config.preserve_tables:
            text, tables = self._extract_tables(text)
        else:
            tables = []

        # Разбиваем основной текст
        if self._is_markdown(text):
            chunks = self.md_splitter.split_text(text)
        else:
            chunks = self.text_splitter.split_text(text)

        # Создаем Documents
        documents = []
        current_header = ""

        for i, chunk in enumerate(chunks):
            if self.config.preserve_headers:
                header = self._extract_header(chunk)
                if header:
                    current_header = header

            chunk_meta = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks) + len(tables),
                "section": current_header,
                "content_type": "text"
            }

            documents.append(Document(page_content=chunk, metadata=chunk_meta))

        # Таблицы как отдельные chunks
        for j, table in enumerate(tables):
            table_meta = {
                **metadata,
                "chunk_index": len(chunks) + j,
                "content_type": "table",
                "table_index": j
            }
            documents.append(Document(page_content=table, metadata=table_meta))

        return documents

    def _extract_tables(self, text: str) -> tuple[str, list[str]]:
        """Извлекает markdown таблицы из текста."""
        tables = []
        pattern = r'(\|[^\n]+\|\n(?:\|[-:| ]+\|\n)?(?:\|[^\n]+\|\n)+)'

        def replace(match):
            tables.append(match.group(1))
            return f"\n[TABLE_{len(tables)}]\n"

        text_without_tables = re.sub(pattern, replace, text)
        return text_without_tables, tables

    def _extract_header(self, chunk: str) -> str:
        """Извлекает первый заголовок из chunk."""
        for line in chunk.strip().split("\n"):
            if line.startswith("#"):
                return line.lstrip("#").strip()
        return ""

    def _is_markdown(self, text: str) -> bool:
        """Проверяет, является ли текст markdown."""
        patterns = [r'^#{1,6}\s', r'\*\*[^*]+\*\*', r'^\|.+\|$']
        return any(re.search(p, text, re.MULTILINE) for p in patterns)
```

---

## Примеры использования

### CLI для работы с документами

```python
"""
cli.py
Интерактивный CLI для Document QA.
"""
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from src.extractors.factory import ExtractorFactory, ExtractorType
from src.processing.chunker import SmartChunker
from src.vectorstore import VectorStoreManager
from src.qa.structured import StructuredQA

console = Console()


async def main():
    # Инициализация
    chunker = SmartChunker()
    vectorstore = VectorStoreManager(collection_name="doc_qa")
    qa = StructuredQA(vectorstore)

    console.print(Panel.fit(
        "[bold]Document Q&A System[/bold]\n\n"
        "Commands:\n"
        "  load <file>      - Load document\n"
        "  ask <question>   - Ask question\n"
        "  invoice <file>   - Extract invoice data\n"
        "  compare <f1> <f2> - Compare documents\n"
        "  exit             - Exit"
    ))

    while True:
        try:
            cmd = Prompt.ask("\n[green]>[/green]").strip()
            if not cmd:
                continue

            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "exit":
                break

            elif command == "load":
                path = Path(args)
                extractor = ExtractorFactory.create(ExtractorType.AUTO, path)
                doc = extractor.extract(path)

                chunks = chunker.chunk_document(
                    doc.markdown,
                    {"filename": doc.filename, "hash": doc.file_hash}
                )

                vectorstore.add_documents(chunks, doc_id=doc.file_hash)
                console.print(f"[green]Loaded: {doc.filename} ({len(chunks)} chunks)[/green]")

            elif command == "ask":
                result = await qa.ask_with_citations(args)

                console.print(f"\n[bold]Answer:[/bold] {result.answer}")
                console.print(f"[dim]Confidence: {result.confidence:.0%}[/dim]")

                if result.citations:
                    console.print("\n[bold]Sources:[/bold]")
                    for c in result.citations:
                        console.print(Panel(
                            f'"{c.quote}"',
                            title=f"[{c.document}, p.{c.page or '?'}]",
                            border_style="dim"
                        ))

            elif command == "invoice":
                path = Path(args)
                extractor = ExtractorFactory.create(ExtractorType.AUTO, path)
                doc = extractor.extract(path)

                invoice = await qa.extract_invoice(doc.markdown)

                table = Table(title=f"Invoice {invoice.invoice_number}")
                table.add_column("Field", style="cyan")
                table.add_column("Value")

                table.add_row("Number", invoice.invoice_number)
                table.add_row("Date", str(invoice.invoice_date))
                table.add_row("Vendor", invoice.vendor.name)
                table.add_row("Customer", invoice.customer_name)
                table.add_row("Total", f"{invoice.total.amount} {invoice.total.currency}")

                console.print(table)

            else:
                console.print(f"[red]Unknown command: {command}[/red]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
```

### FastAPI сервер

```python
"""
api.py
REST API для Document Q&A.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil

from src.extractors.factory import ExtractorFactory, ExtractorType
from src.processing.chunker import SmartChunker
from src.vectorstore import VectorStoreManager
from src.qa.structured import StructuredQA
from src.schemas.invoice import Invoice
from src.schemas.common import AnswerWithCitations

app = FastAPI(title="Document Q&A API", version="2.0.0")

# Globals
chunker = SmartChunker()
vectorstore = VectorStoreManager(collection_name="api_docs")
qa = StructuredQA(vectorstore)


class QuestionRequest(BaseModel):
    question: str
    k: int = 5


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a document."""
    suffix = Path(file.filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        extractor = ExtractorFactory.create(ExtractorType.AUTO, tmp_path)
        doc = extractor.extract(tmp_path)

        chunks = chunker.chunk_document(
            doc.markdown,
            {"filename": doc.filename}
        )

        vectorstore.add_documents(chunks, doc_id=doc.file_hash)

        return {
            "doc_id": doc.file_hash,
            "filename": doc.filename,
            "chunks": len(chunks)
        }
    finally:
        tmp_path.unlink()


@app.post("/qa/ask", response_model=AnswerWithCitations)
async def ask_question(request: QuestionRequest):
    """Ask a question about uploaded documents."""
    return await qa.ask_with_citations(request.question, k=request.k)


@app.post("/extract/invoice", response_model=Invoice)
async def extract_invoice(file: UploadFile = File(...)):
    """Extract structured invoice data."""
    suffix = Path(file.filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        extractor = ExtractorFactory.create(ExtractorType.AUTO, tmp_path)
        doc = extractor.extract(tmp_path)
        return await qa.extract_invoice(doc.markdown)
    finally:
        tmp_path.unlink()


@app.get("/documents")
async def list_documents():
    """List all indexed documents."""
    return {"documents": vectorstore.list_documents()}


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Best Practices

### 1. Выбор extractor под задачу

| Сценарий | Рекомендация |
|----------|--------------|
| Enterprise PDF с таблицами | Docling |
| Быстрый parsing нативных PDF | PyMuPDF4LLM |
| Сложные layouts, диаграммы | LlamaParse |
| Сканированные документы | Mistral OCR / Docling |
| Office документы | Docling |

### 2. Chunking strategy

- **Размер chunk**: 500-1500 токенов оптимально для большинства моделей
- **Overlap**: 10-20% от размера chunk
- **Таблицы**: Всегда отдельными chunks
- **Заголовки**: Сохранять в metadata для context

### 3. Structured output tips

- Начинай с простых схем, усложняй по мере необходимости
- Используй `Field(description=...)` - это часть prompt для модели
- Валидируй критичные поля с `@field_validator`
- Тестируй на edge cases (пустые документы, неполные данные)

### 4. RAG evaluation

Метрики для оценки Document QA ([Evidently AI](https://www.evidentlyai.com/llm-guide/rag-evaluation)):

- **Retrieval metrics**: Precision@k, Recall@k, MRR
- **Generation metrics**: Faithfulness, Answer relevancy
- **End-to-end**: Human evaluation, LLM-as-judge

---

## Проверь себя

1. **Почему Docling лучше простого OCR для RAG?**
   > Docling сохраняет структуру документа (таблицы, заголовки, секции), используя AI-модели DocLayNet и TableFormer. Обычный OCR возвращает плоский текст без структуры.

2. **Что дает with_structured_output() / Pydantic AI?**
   > Гарантирует, что LLM вернет данные в точном формате Pydantic схемы. Модель не может "отклониться" от структуры, что делает вывод программно обрабатываемым.

3. **Когда использовать GraphRAG вместо vector RAG?**
   > Когда нужно находить связи между сущностями в разных документах. Например: "Какие компании связаны с этим договором?" требует traversal графа отношений.

4. **Зачем таблицы хранить отдельными chunks?**
   > Таблицы содержат структурированные данные, которые теряют смысл при разбиении. Целая таблица как chunk сохраняет контекст строк и колонок.

5. **Как обеспечить точность extraction из счетов?**
   > Использовать типизированные Pydantic схемы с описаниями полей, добавить примеры через json_schema_extra, запросить confidence score, валидировать критичные поля.

---

## Источники

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Docling (IBM)](https://docling-project.github.io/docling/) | Docs | Open-source document extraction |
| 2 | [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) | Docs | Быстрый PDF → Markdown |
| 3 | [LlamaParse](https://www.llamaindex.ai/llamaparse) | Tool | ~99% точность parsing |
| 4 | [Pydantic AI](https://ai.pydantic.dev/) | Docs | Structured outputs framework |
| 5 | [LLM Schemas — Simon Willison](https://simonwillison.net/2025/Feb/28/llm-schemas/) | Blog | Почему structured output важен |
| 6 | [GraphRAG (Microsoft)](https://microsoft.github.io/graphrag/) | Docs | Knowledge graphs для RAG |
| 7 | [RAG Evaluation — Evidently AI](https://www.evidentlyai.com/llm-guide/rag-evaluation) | Guide | Метрики оценки RAG |
| 8 | [PaperQA2](https://github.com/Future-House/paper-qa) | GitHub | Scientific document QA |
| 9 | [Instructor](https://github.com/jxnl/instructor) | GitHub | Structured extraction library |
| 10 | [PDF Extraction Benchmark 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) | Blog | Сравнение инструментов |

---

## Связанные темы

- [[tutorial-rag-chatbot]] — базовая RAG система
- [[embeddings-complete-guide]] — работа с embeddings
- [[vector-databases-guide]] — vector stores
- [[structured-outputs-tools]] — structured outputs в деталях
- [[rag-advanced-techniques]] — продвинутые RAG паттерны

---

*Последнее обновление: 2025-12-28*

---

*Проверено: 2026-01-09*
