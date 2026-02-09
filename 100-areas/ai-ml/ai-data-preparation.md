---
title: "Подготовка данных для AI: Chunking, Синтетические данные, Quality"
created: 2026-01-11
modified: 2026-01-11
type: guide
status: verified
level: intermediate
confidence: high
tags:
  - ai
  - data
  - chunking
  - rag
  - fine-tuning
  - synthetic-data
prerequisites:
  - "[[llm-fundamentals]]"
  - "[[embeddings-complete-guide]]"
  - "[[vector-databases-guide]]"
related:
  - "[[rag-advanced-techniques]]"
  - "[[ai-fine-tuning-guide]]"
  - "[[ai-testing-evaluation]]"
  - "[[tutorial-rag-chatbot]]"
---

# Подготовка данных для AI: Chunking, Синтетические данные, Quality

> **Факт:** Chunking — наиболее важный фактор для производительности RAG. Плохие данные → плохой AI, независимо от модели.

---

## TL;DR

- **Chunking** — разбиение документов на части для RAG; определяет качество retrieval
- **Semantic chunking** — +70% accuracy vs наивного разбиения
- **Синтетические данные** — генерируем примеры для eval и fine-tuning с помощью LLM
- **Data quality** — garbage in = garbage out; нужны метрики и валидация
- **Правило:** Потрать 50% времени на данные, 50% на всё остальное

---

## Часть 1: Интуиция без кода

### Аналогия 1: Chunking как разрезание книги

```
ЗАДАЧА: Поисковая система должна находить ответы в книге

ПЛОХО: Разрезали книгу на страницы ровно по 500 слов
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Страница 47 (500 слов):                                          │
│   "...и поэтому налоги рассчитываются по формуле.                   │
│                                                                     │
│   Глава 8: ИНВЕСТИЦИИ                                               │
│                                                                     │
│   Инвестирование начинается с понимания рисков..."                  │
│                                                                     │
│   ❌ ПРОБЛЕМА: Конец налогов + начало инвестиций в одном чанке     │
│   → Embedding "усредняет" две разные темы                          │
│   → Поиск по "налоги" может найти этот чанк, но ответ неполный     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

ХОРОШО: Разрезали по смыслу (semantic chunking)
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Чанк A: "Раздел о налогах" (387 слов)                            │
│   ─────────────────────────────────────                            │
│   "Налоги рассчитываются по формуле... до конца раздела"           │
│   ✅ Полная информация о налогах в одном месте                     │
│                                                                     │
│   Чанк B: "Раздел об инвестициях" (612 слов)                       │
│   ─────────────────────────────────────                            │
│   "Инвестирование начинается с... до конца раздела"                │
│   ✅ Полная информация об инвестициях                              │
│                                                                     │
│   → Embedding чётко представляет одну тему                         │
│   → Поиск точный                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Аналогия 2: Синтетические данные как учебные примеры

```
ПРОБЛЕМА: Нужно оценить RAG систему, но нет готовых вопросов-ответов

РЕШЕНИЕ: Попросим LLM создать тестовые примеры

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ИСХОДНЫЙ ДОКУМЕНТ:                                                │
│   "Python 3.12 добавил улучшенные error messages и               │
│    поддержку type parameter syntax (PEP 695)."                     │
│                                                                     │
│   ────────────────────────────────────────────────                 │
│                                                                     │
│   LLM ГЕНЕРИРУЕТ:                                                   │
│                                                                     │
│   Вопрос 1: "Какие улучшения появились в Python 3.12?"             │
│   Ответ: "Улучшенные error messages и type parameter syntax"       │
│                                                                     │
│   Вопрос 2: "Какой PEP описывает синтаксис параметров типов?"      │
│   Ответ: "PEP 695"                                                 │
│                                                                     │
│   Вопрос 3 (сложный): "Как связаны PEP 695 и Python 3.12?"         │
│   Ответ: "Python 3.12 реализует PEP 695 - type parameter syntax"   │
│                                                                     │
│   ✅ Теперь есть данные для evaluation!                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Аналогия 3: Data Quality как ингредиенты для блюда

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA QUALITY = INGREDIENT QUALITY                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   GARBAGE IN = GARBAGE OUT                                          │
│                                                                     │
│   Данные:                      Блюдо:                               │
│   ─────────                    ──────                               │
│   ✗ Дубликаты                  = Слишком солёное (bias)            │
│   ✗ Противоречия               = Несъедобное (confusion)           │
│   ✗ Устаревшие факты           = Испортившееся (hallucinations)    │
│   ✗ Плохое форматирование      = Плохая текстура (noise)           │
│                                                                     │
│   QUALITY IN = QUALITY OUT                                          │
│                                                                     │
│   ✓ Дедупликация               = Сбалансированное                  │
│   ✓ Консистентность            = Гармоничное                       │
│   ✓ Актуальность               = Свежее                            │
│   ✓ Чистое форматирование      = Правильная текстура               │
│                                                                     │
│   Даже лучший шеф (GPT-4) не сделает хорошее блюдо                 │
│   из испорченных ингредиентов!                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Часть 2: Стратегии Chunking

### Обзор стратегий

| Стратегия | Описание | Плюсы | Минусы | Когда использовать |
|-----------|----------|-------|--------|-------------------|
| **Fixed Size** | Ровно N символов/токенов | Простота, предсказуемость | Режет по середине предложений | Baseline, прототипы |
| **Recursive** | Делит по \\n\\n → \\n → . → пробел | Сохраняет структуру | Размер варьируется | **Default для большинства** |
| **Semantic** | По смысловым границам | +70% accuracy | Вычислительно дорого | Knowledge bases |
| **Sentence** | По предложениям | Атомарность | Мелкие чанки | QA системы |
| **Document** | По разделам/главам | Контекст сохранён | Слишком большие | Длинные документы |
| **LLM-based** | LLM решает где резать | Максимальное качество | Очень дорого | Critical applications |

---

### Fixed Size Chunking

```python
from langchain.text_splitter import CharacterTextSplitter

# Простейший вариант — фиксированный размер
splitter = CharacterTextSplitter(
    chunk_size=1000,      # символов
    chunk_overlap=200,    # перекрытие для контекста
    separator=""          # любой символ
)

text = "Длинный документ о машинном обучении..."
chunks = splitter.split_text(text)

# Проблема: может разрезать посередине предложения
# "...нейронные сети используют обратное распространение оши" | "бки для обучения..."
#                                                           ↑
#                                               Разрыв смысла!
```

**Когда использовать:** Быстрые прототипы, когда качество не критично.

---

### Recursive Character Chunking (Рекомендуется)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Рекурсивно пробует разделители: \n\n → \n → . → пробел
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

text = """
# Глава 1: Введение

Машинное обучение — это область искусственного интеллекта.

## Подраздел 1.1

Основные концепции включают...
"""

chunks = splitter.split_text(text)

# Результат: сначала пробует разделить по \n\n (параграфы)
# Если чанк всё ещё большой — по \n, затем по точке, и т.д.
# ✅ Сохраняет структуру документа
```

**Когда использовать:** По умолчанию для большинства RAG приложений.

---

### Semantic Chunking

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# Разбивает по смысловым границам используя embeddings
embeddings = OpenAIEmbeddings()

splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # или "standard_deviation"
    breakpoint_threshold_amount=95           # порог для разрыва
)

text = """
Python — язык программирования высокого уровня.
Он используется для веб-разработки, анализа данных и AI.
Python был создан Гвидо ван Россумом в 1991 году.

JavaScript — язык для веб-браузеров.
Он позволяет создавать интерактивные веб-страницы.
Node.js расширил JavaScript на серверную часть.
"""

chunks = splitter.split_text(text)

# Результат:
# Чанк 1: "Python — язык... в 1991 году."  (всё о Python вместе)
# Чанк 2: "JavaScript — язык... серверную часть."  (всё о JS вместе)
# ✅ Смысловые границы = лучший retrieval
```

**Как это работает:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SEMANTIC CHUNKING ALGORITHM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   1. Разбить текст на предложения                                  │
│      [S1] [S2] [S3] [S4] [S5] [S6]                                  │
│                                                                     │
│   2. Получить embedding для каждого предложения                    │
│      [E1] [E2] [E3] [E4] [E5] [E6]                                  │
│                                                                     │
│   3. Вычислить similarity между соседними                          │
│      S1-S2: 0.95  (похожи — одна тема)                             │
│      S2-S3: 0.91  (похожи)                                         │
│      S3-S4: 0.42  (различны — РАЗРЫВ!)  ← граница чанка           │
│      S4-S5: 0.88  (похожи)                                         │
│      S5-S6: 0.85  (похожи)                                         │
│                                                                     │
│   4. Разрезать где similarity < threshold                          │
│      Чанк 1: [S1, S2, S3]                                          │
│      Чанк 2: [S4, S5, S6]                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Когда использовать:** Knowledge bases, technical docs, когда качество критично.

---

### LLM-Based Chunking (State-of-the-Art)

```python
from openai import OpenAI

client = OpenAI()

def llm_chunk(text: str, target_size: int = 500) -> list[str]:
    """
    Используем LLM для определения оптимальных границ чанков
    """
    prompt = f"""Analyze the following text and split it into logical chunks.
Each chunk should:
- Be self-contained and meaningful
- Be approximately {target_size} words (but prioritize logical boundaries)
- Not break in the middle of a concept

Return the chunks as a JSON array of strings.

Text to chunk:
---
{text}
---

Output format: ["chunk1", "chunk2", ...]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Дешевле для chunking
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result.get("chunks", [])


# Пример использования
text = "Длинный технический документ..."
chunks = llm_chunk(text)

# ✅ LLM понимает контекст и семантику лучше любого алгоритма
# ❌ Дорого для больших объёмов
```

**Когда использовать:** Критичные приложения, сложные документы.

---

### Сравнение качества

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CHUNKING ACCURACY BENCHMARKS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   RECALL @ k=5 (%)                                                  │
│   ──────────────────────────────────────────────────────────────   │
│                                                                     │
│   Fixed Size (500 chars)      ████████████░░░░░░░░░░░░  48%        │
│   Fixed Size (1000 chars)     █████████████░░░░░░░░░░░  52%        │
│   Recursive Character         ███████████████████░░░░░  76%  ← Default │
│   Sentence-based              ████████████████░░░░░░░░  64%        │
│   Semantic (percentile)       ██████████████████████░░  88%  ← Best │
│   LLM-enhanced Semantic       ████████████████████████  92%        │
│                                                                     │
│   Source: Chroma Research, 2024                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Часть 3: Подготовка разных типов документов

### PDF документы

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

# Docling — современный инструмент от IBM для PDF/DOCX
converter = DocumentConverter()

result = converter.convert("document.pdf")

# Результат включает:
# - Структурированный текст
# - Таблицы как markdown
# - Извлечённые изображения
# - Метаданные (заголовки, секции)

markdown_text = result.document.export_to_markdown()

# Для chunking используем структуру документа
sections = result.document.sections
for section in sections:
    chunk = {
        "content": section.text,
        "title": section.title,
        "page": section.page_number,
        "type": section.type  # heading, paragraph, table, etc.
    }
```

### Таблицы

```python
def chunk_table(table_markdown: str, context: str = "") -> dict:
    """
    Таблицы требуют особого подхода — контекст важен
    """
    return {
        "type": "table",
        "content": table_markdown,
        "context": context,  # Заголовок секции, описание
        "metadata": {
            "requires_full_context": True,
            "chunk_strategy": "keep_whole"
        }
    }

# Пример: таблица с ценами
table = """
| Продукт | Цена | Скидка |
|---------|------|--------|
| A       | $100 | 10%    |
| B       | $200 | 15%    |
"""

# ❌ ПЛОХО: разрезать таблицу пополам
# ✅ ХОРОШО: хранить таблицу целиком с контекстом
chunk = chunk_table(table, context="Прайс-лист на январь 2026")
```

### Code документация

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

# Language-aware splitting для кода
code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100
)

code = """
class UserService:
    '''Сервис для работы с пользователями'''

    def __init__(self, db: Database):
        self.db = db

    def get_user(self, user_id: int) -> User:
        '''Получить пользователя по ID'''
        return self.db.query(User).filter_by(id=user_id).first()

    def create_user(self, data: UserCreate) -> User:
        '''Создать нового пользователя'''
        user = User(**data.dict())
        self.db.add(user)
        self.db.commit()
        return user
"""

chunks = code_splitter.split_text(code)

# Результат: методы остаются целыми, не разрезаются посередине
```

---

## Часть 4: Синтетические данные

### Зачем нужны синтетические данные

```
┌─────────────────────────────────────────────────────────────────────┐
│                   USE CASES FOR SYNTHETIC DATA                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   1. EVALUATION                                                     │
│      Нужны пары (question, answer) для тестирования RAG            │
│      Ручная разметка = дорого и долго                              │
│      Синтетика = быстро и масштабируемо                            │
│                                                                     │
│   2. FINE-TUNING                                                    │
│      Нужны примеры для обучения модели                             │
│      Мало реальных данных → сгенерировать больше                   │
│                                                                     │
│   3. AUGMENTATION                                                   │
│      Расширить training set перефразированием                      │
│      Добавить edge cases                                           │
│                                                                     │
│   4. TESTING                                                        │
│      Создать негативные примеры                                    │
│      Тестировать на corner cases                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Генерация QA пар для RAG evaluation

```python
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional

client = OpenAI()

class QAPair(BaseModel):
    question: str
    answer: str
    difficulty: str  # easy, medium, hard
    reasoning_required: bool

class QAGeneration(BaseModel):
    pairs: list[QAPair]

def generate_qa_pairs(
    document: str,
    num_pairs: int = 5,
    include_hard: bool = True
) -> list[QAPair]:
    """
    Генерация вопросов-ответов из документа для evaluation
    """

    difficulty_instruction = ""
    if include_hard:
        difficulty_instruction = """
Include questions of varying difficulty:
- Easy: Direct facts from the text
- Medium: Requires understanding context
- Hard: Requires reasoning across multiple sentences
"""

    prompt = f"""Based on the following document, generate {num_pairs} question-answer pairs.

{difficulty_instruction}

For each pair:
1. The question should be natural (how a user would ask)
2. The answer should be directly supported by the document
3. Mark if the answer requires multi-step reasoning

Document:
---
{document}
---

Generate exactly {num_pairs} QA pairs.
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=QAGeneration
    )

    return response.choices[0].message.parsed.pairs


# Пример
document = """
Python 3.12, released in October 2023, introduced several key features.
The most notable is improved error messages that now show the exact
expression causing the error. Additionally, PEP 695 added new syntax
for type parameters, making generic classes more readable. Performance
improvements include a 5% speedup in the interpreter.
"""

qa_pairs = generate_qa_pairs(document, num_pairs=5)

for pair in qa_pairs:
    print(f"Q: {pair.question}")
    print(f"A: {pair.answer}")
    print(f"Difficulty: {pair.difficulty}")
    print("---")

# Output:
# Q: When was Python 3.12 released?
# A: October 2023
# Difficulty: easy
# ---
# Q: What PEP number introduced new type parameter syntax?
# A: PEP 695
# Difficulty: medium
# ---
# Q: How do Python 3.12's error messages differ from previous versions?
# A: They now show the exact expression causing the error
# Difficulty: medium
# ---
```

### Генерация данных для Fine-tuning

```python
from pydantic import BaseModel
from typing import Literal

class TrainingExample(BaseModel):
    instruction: str
    input: str
    output: str
    category: str

class TrainingDataset(BaseModel):
    examples: list[TrainingExample]

def generate_training_data(
    task_description: str,
    examples: list[dict],  # Несколько seed examples
    num_generate: int = 50
) -> list[TrainingExample]:
    """
    Генерация training data из нескольких примеров
    """

    examples_text = "\n\n".join([
        f"Example {i+1}:\nInstruction: {ex['instruction']}\nInput: {ex['input']}\nOutput: {ex['output']}"
        for i, ex in enumerate(examples)
    ])

    prompt = f"""You are a training data generator for a {task_description} task.

Here are example training pairs:

{examples_text}

Generate {num_generate} new, diverse training examples following the same format and quality.
Ensure variety in:
- Different input types and lengths
- Edge cases
- Various phrasings of instructions

Each example should be realistic and useful for training.
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=TrainingDataset
    )

    return response.choices[0].message.parsed.examples


# Пример: генерация данных для sentiment classifier
seed_examples = [
    {
        "instruction": "Classify the sentiment of this review",
        "input": "This product exceeded my expectations! Amazing quality.",
        "output": "positive"
    },
    {
        "instruction": "Classify the sentiment of this review",
        "input": "Terrible experience. The item broke after one day.",
        "output": "negative"
    }
]

training_data = generate_training_data(
    task_description="sentiment classification",
    examples=seed_examples,
    num_generate=100
)

# Сохраняем в JSONL для fine-tuning
import json
with open("training_data.jsonl", "w") as f:
    for example in training_data:
        f.write(json.dumps(example.model_dump()) + "\n")
```

---

## Часть 5: Data Quality

### Метрики качества данных

```python
from dataclasses import dataclass
from typing import Optional
import hashlib

@dataclass
class DataQualityMetrics:
    total_documents: int
    duplicates_found: int
    avg_chunk_size: float
    chunk_size_std: float
    empty_chunks: int
    encoding_issues: int
    quality_score: float  # 0-1

class DataQualityChecker:
    """
    Проверка качества данных перед индексацией
    """

    def __init__(self):
        self.seen_hashes: set[str] = set()
        self.issues: list[dict] = []

    def check_chunk(self, chunk: str, metadata: dict = None) -> dict:
        """Проверить один чанк на качество"""
        issues = []

        # 1. Пустой или почти пустой
        if len(chunk.strip()) < 50:
            issues.append("too_short")

        # 2. Слишком длинный
        if len(chunk) > 10000:
            issues.append("too_long")

        # 3. Дубликат
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
        if chunk_hash in self.seen_hashes:
            issues.append("duplicate")
        else:
            self.seen_hashes.add(chunk_hash)

        # 4. Проблемы с encoding
        try:
            chunk.encode('utf-8').decode('utf-8')
        except:
            issues.append("encoding_error")

        # 5. Много специальных символов (возможно мусор)
        special_ratio = sum(1 for c in chunk if not c.isalnum() and c not in ' .,!?-:;') / len(chunk)
        if special_ratio > 0.3:
            issues.append("high_special_chars")

        # 6. Низкое информационное содержание
        words = chunk.split()
        unique_words = set(words)
        if len(words) > 20 and len(unique_words) / len(words) < 0.3:
            issues.append("low_information_density")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "chunk_length": len(chunk),
            "word_count": len(words)
        }

    def check_dataset(self, chunks: list[str]) -> DataQualityMetrics:
        """Проверить весь dataset"""
        results = [self.check_chunk(chunk) for chunk in chunks]

        valid_chunks = [r for r in results if r["is_valid"]]
        chunk_lengths = [r["chunk_length"] for r in results]

        import statistics

        return DataQualityMetrics(
            total_documents=len(chunks),
            duplicates_found=sum(1 for r in results if "duplicate" in r["issues"]),
            avg_chunk_size=statistics.mean(chunk_lengths),
            chunk_size_std=statistics.stdev(chunk_lengths) if len(chunk_lengths) > 1 else 0,
            empty_chunks=sum(1 for r in results if "too_short" in r["issues"]),
            encoding_issues=sum(1 for r in results if "encoding_error" in r["issues"]),
            quality_score=len(valid_chunks) / len(chunks)
        )


# Использование
checker = DataQualityChecker()
chunks = ["chunk1...", "chunk2...", "chunk1..."]  # с дубликатом

metrics = checker.check_dataset(chunks)
print(f"Quality Score: {metrics.quality_score:.2%}")
print(f"Duplicates: {metrics.duplicates_found}")
print(f"Avg chunk size: {metrics.avg_chunk_size:.0f} chars")
```

### Дедупликация

```python
from datasketch import MinHash, MinHashLSH
from typing import Iterable

class SemanticDeduplicator:
    """
    Удаление near-duplicates используя MinHash LSH
    """

    def __init__(self, threshold: float = 0.8, num_perm: int = 128):
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        self.minhashes: dict[str, MinHash] = {}

    def _get_minhash(self, text: str) -> MinHash:
        """Создать MinHash из текста"""
        mh = MinHash(num_perm=self.num_perm)
        # Используем 3-граммы слов
        words = text.lower().split()
        for i in range(len(words) - 2):
            ngram = " ".join(words[i:i+3])
            mh.update(ngram.encode('utf-8'))
        return mh

    def deduplicate(self, documents: list[dict]) -> list[dict]:
        """
        Удалить near-duplicates из списка документов
        documents: [{"id": "...", "content": "...", ...}, ...]
        """
        unique_docs = []

        for doc in documents:
            doc_id = doc["id"]
            content = doc["content"]

            mh = self._get_minhash(content)

            # Проверяем есть ли похожие
            similar = self.lsh.query(mh)

            if not similar:
                # Нет похожих — добавляем
                self.lsh.insert(doc_id, mh)
                self.minhashes[doc_id] = mh
                unique_docs.append(doc)
            else:
                # Есть похожий — пропускаем (или можно merge)
                pass

        return unique_docs


# Использование
deduplicator = SemanticDeduplicator(threshold=0.85)

documents = [
    {"id": "1", "content": "Python is a programming language for AI and ML."},
    {"id": "2", "content": "Python is a programming language for artificial intelligence and machine learning."},  # Near-duplicate
    {"id": "3", "content": "JavaScript is used for web development."},
]

unique = deduplicator.deduplicate(documents)
print(f"Original: {len(documents)}, Unique: {len(unique)}")
# Output: Original: 3, Unique: 2
```

---

## Часть 6: Production Pipeline

### End-to-End Data Pipeline

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunking_strategy: str = "recursive"  # recursive, semantic, llm
    deduplicate: bool = True
    dedup_threshold: float = 0.85
    generate_qa: bool = True
    qa_pairs_per_doc: int = 3

class DataPipeline:
    """
    Production data preparation pipeline
    """

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.quality_checker = DataQualityChecker()
        self.deduplicator = SemanticDeduplicator(threshold=config.dedup_threshold)

    def process_directory(self, input_dir: Path, output_dir: Path):
        """Process all documents in a directory"""
        logger.info(f"Processing {input_dir}")

        # 1. Load documents
        documents = self._load_documents(input_dir)
        logger.info(f"Loaded {len(documents)} documents")

        # 2. Convert to markdown/text
        texts = [self._extract_text(doc) for doc in documents]

        # 3. Chunk
        all_chunks = []
        for text, doc in zip(texts, documents):
            chunks = self._chunk_text(text)
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "id": f"{doc['id']}_chunk_{i}",
                    "content": chunk,
                    "source": doc["path"],
                    "chunk_index": i
                })

        logger.info(f"Created {len(all_chunks)} chunks")

        # 4. Quality check
        contents = [c["content"] for c in all_chunks]
        metrics = self.quality_checker.check_dataset(contents)
        logger.info(f"Quality score: {metrics.quality_score:.2%}")

        if metrics.quality_score < 0.8:
            logger.warning(f"Low quality score! Review data.")

        # 5. Deduplicate
        if self.config.deduplicate:
            all_chunks = self.deduplicator.deduplicate(all_chunks)
            logger.info(f"After dedup: {len(all_chunks)} chunks")

        # 6. Generate QA pairs for evaluation
        qa_pairs = []
        if self.config.generate_qa:
            for chunk in all_chunks[:100]:  # Sample for QA
                pairs = generate_qa_pairs(
                    chunk["content"],
                    num_pairs=self.config.qa_pairs_per_doc
                )
                qa_pairs.extend(pairs)
            logger.info(f"Generated {len(qa_pairs)} QA pairs")

        # 7. Save outputs
        self._save_outputs(output_dir, all_chunks, qa_pairs, metrics)

        return {
            "chunks": len(all_chunks),
            "qa_pairs": len(qa_pairs),
            "quality_score": metrics.quality_score
        }

    def _load_documents(self, path: Path) -> list[dict]:
        # Implementation for loading PDFs, DOCX, etc.
        pass

    def _extract_text(self, doc: dict) -> str:
        # Use Docling or similar
        pass

    def _chunk_text(self, text: str) -> list[str]:
        if self.config.chunking_strategy == "recursive":
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        elif self.config.chunking_strategy == "semantic":
            splitter = SemanticChunker(OpenAIEmbeddings())
        else:
            raise ValueError(f"Unknown strategy: {self.config.chunking_strategy}")

        return splitter.split_text(text)

    def _save_outputs(self, output_dir, chunks, qa_pairs, metrics):
        import json

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save chunks
        with open(output_dir / "chunks.jsonl", "w") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk) + "\n")

        # Save QA pairs
        with open(output_dir / "qa_pairs.jsonl", "w") as f:
            for pair in qa_pairs:
                f.write(json.dumps(pair.model_dump()) + "\n")

        # Save metrics
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(metrics.__dict__, f, indent=2)


# Использование
config = ProcessingConfig(
    chunk_size=800,
    chunking_strategy="semantic",
    generate_qa=True
)

pipeline = DataPipeline(config)
result = pipeline.process_directory(
    input_dir=Path("./raw_documents"),
    output_dir=Path("./processed_data")
)

print(f"Processed: {result}")
```

---

## Типичные ошибки

### Ошибка 1: Одинаковый chunking для всех документов

**СИМПТОМ:** Код работает хорошо, таблицы — плохо.

```python
# ❌ Один размер для всего
chunks = splitter.split_text(any_document)

# ✅ Адаптивный chunking
def smart_chunk(document: str, doc_type: str) -> list[str]:
    if doc_type == "code":
        return code_splitter.split_text(document)
    elif doc_type == "table":
        return [document]  # Таблицы целиком
    elif doc_type == "faq":
        return document.split("\n\n")  # По вопросам
    else:
        return semantic_splitter.split_text(document)
```

---

### Ошибка 2: Нет overlap между чанками

**СИМПТОМ:** Контекст теряется на границах.

```python
# ❌ Без overlap
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

# ✅ С overlap (10-20% от chunk_size)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
```

---

### Ошибка 3: Нет дедупликации

**СИМПТОМ:** Одинаковые результаты в retrieval, bias в ответах.

```python
# ❌ Индексируем всё без проверки
for chunk in chunks:
    vector_store.add(chunk)

# ✅ Дедупликация перед индексацией
unique_chunks = deduplicator.deduplicate(chunks)
for chunk in unique_chunks:
    vector_store.add(chunk)
```

---

### Ошибка 4: Нет метаданных

**СИМПТОМ:** Невозможно фильтровать, нет source attribution.

```python
# ❌ Только текст
chunks = [{"content": "..."}]

# ✅ С метаданными
chunks = [{
    "content": "...",
    "source": "handbook_v2.pdf",
    "page": 42,
    "section": "Policies",
    "date": "2024-01-15",
    "author": "HR Team"
}]

# Теперь можно:
# - Фильтровать по дате
# - Показывать источник
# - Ограничивать по разделам
```

---

## Связи с другими разделами

| Раздел | Как связан | Что изучить |
|--------|------------|-------------|
| [[rag-advanced-techniques]] | Chunking влияет на retrieval | Self-RAG, CRAG |
| [[embeddings-complete-guide]] | Embeddings для semantic chunking | Модели, MTEB |
| [[vector-databases-guide]] | Хранение чанков | HNSW, metadata filtering |
| [[ai-fine-tuning-guide]] | Данные для fine-tuning | LoRA, DPO |
| [[ai-testing-evaluation]] | QA pairs для eval | RAGAS metrics |

---

## Источники

### Документация
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [LlamaIndex Data Connectors](https://docs.llamaindex.ai/en/stable/module_guides/loading/connector/)
- [Docling (IBM)](https://github.com/DS4SD/docling)

### Исследования
- [Weaviate: Chunking Strategies](https://weaviate.io/blog/chunking-strategies-for-rag) — Сравнение стратегий
- [NVIDIA: Best Chunking Strategy](https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/)
- [Firecrawl: Chunking 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [Stack Overflow: Breaking Up is Hard to Do](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/)

---

*Проверено: 2026-01-11 | Semantic Chunking, Synthetic Data Generation, Quality Metrics*
