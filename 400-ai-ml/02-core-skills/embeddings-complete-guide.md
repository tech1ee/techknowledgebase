---
title: "Embeddings: Полное руководство"
type: guide
status: published
tags:
  - topic/ai-ml
  - type/guide
  - level/intermediate
reading_time: 47
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - "[[vector-databases-guide]]"
  - "[[rag-advanced-techniques]]"
  - "[[aiml-databases-complete]]"
---

# Embeddings: Полное руководство

> От Word2Vec до современных моделей: как машины научились понимать смысл слов

**Последнее обновление:** Декабрь 2024

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание ML** | Embeddings — фундамент для любых ML-задач с текстом | [[ml-fundamentals]] |
| **Что такое вектор** | Embedding — это вектор чисел; нужно понимать что это | Школьная математика |
| **Нейронные сети (базово)** | Понимание как модели "обучаются" представлениям | [[deep-learning-basics]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Новичок** | Понимание что такое embeddings, зачем нужны, как выбрать модель |
| **Практик** | Рекомендации по chunking, quantization, fine-tuning для production |
| **Архитектор** | Trade-offs между моделями, benchmarks, стратегии масштабирования |

---

## Терминология

> 💡 **Главная аналогия для понимания embeddings:**
>
> Представьте **библиотеку**, где книги расставлены не по алфавиту, а **по смыслу**. Книги о любви стоят рядом, детективы — в другом углу, научная фантастика — на третьей полке. **Embedding** — это "адрес" книги в такой библиотеке: набор координат, который говорит где именно она стоит в пространстве смыслов.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Embedding** | Представление объекта (слова, предложения) как вектора чисел | **GPS-координаты смысла** — каждое слово имеет "адрес" в пространстве значений |
| **Вектор (Vector)** | Упорядоченный набор чисел [0.2, -0.5, 0.8, ...] | **Рецепт коктейля** — список ингредиентов и их пропорций |
| **Размерность (Dimensions)** | Количество чисел в векторе (256, 512, 1024, 3072) | **Количество характеристик** — как описать человека: рост, вес, возраст = 3 измерения |
| **Cosine Similarity** | Мера похожести двух векторов (от -1 до 1) | **Угол между стрелками компаса** — смотрят в одну сторону = похожи (1.0), в противоположные = антонимы (-1.0) |
| **Dot Product** | Скалярное произведение — сумма попарных умножений | **Совпадение вкусов** — если оба любят (×) одни жанры, сумма высокая |
| **Semantic Search** | Поиск по смыслу, а не по ключевым словам | **Умный библиотекарь** — понимает что "авто" и "машина" — одно и то же |
| **MTEB** | Massive Text Embedding Benchmark — стандарт оценки моделей | **ЕГЭ для embedding-моделей** — единый экзамен для сравнения |
| **Контекстуальные embeddings** | Разные представления для одного слова в разных контекстах | **Слово "ключ"** — дверной vs музыкальный vs к успеху — три разных embedding'а |
| **Quantization** | Сжатие векторов (float32 → int8 → binary) | **JPEG для векторов** — уменьшаем размер с небольшой потерей качества |
| **Matryoshka (MRL)** | Обучение, где можно обрезать вектор без потери качества | **Телескопическая удочка** — работает и в полном, и в сложенном виде |
| **Chunking** | Разбиение документа на части для embedding'а | **Нарезка книги на главы** — embedding для каждой главы отдельно |
| **Late Chunking** | Сначала embedding всего документа, потом разбиение | **Сначала прочитать книгу целиком**, потом выделить главы — каждая глава "помнит" контекст |
| **Hybrid Search** | Комбинация vector search + keyword search | **Два библиотекаря** — один ищет по смыслу, второй по точным словам, результаты объединяют |
| **Fine-tuning** | Дообучение модели на своих данных | **Репетитор для модели** — учит понимать специфическую терминологию (медицина, право) |
| **Reranking** | Переранжирование результатов более умной моделью | **Второе мнение** — сначала быстрый поиск 1000 кандидатов, потом эксперт отбирает top-10 |

### Математика простым языком

> 🎯 **Для новичка:** Не бойтесь математики! Вот три ключевых понятия:

**1. Вектор = список чисел**
```
Вектор "кошка" = [0.8, 0.2, -0.5, 0.9, ...]
                  ↑     ↑     ↑     ↑
               "пушистость" "размер" "опасность" "домашность"
               (условно — на самом деле измерения абстрактные)
```

**2. Cosine Similarity = насколько векторы смотрят в одну сторону**
```
           "собака"
              ↗
             /
            /  45°  → similarity = 0.71 (похожи!)
           /
    ------●-----→ "кошка"
           \
            \
             \
              ↘ "автомобиль"
                 90° → similarity = 0.0 (не связаны)
```

---

## Теоретические основы

### Формальное определение

> **Embedding** (векторное вложение) — отображение f: X → ℝⁿ, переводящее элементы дискретного множества X (слова, предложения, документы) в непрерывное векторное пространство ℝⁿ, где геометрическая близость отражает семантическую близость (Mikolov et al., 2013).

### Дистрибутивная гипотеза

> «You shall know a word by the company it keeps» — J.R. Firth (1957). Слова, встречающиеся в похожих контекстах, имеют похожие значения. Это фундаментальное допущение, лежащее в основе всех embedding-моделей, от Word2Vec до modern sentence transformers.

Harris (1954) впервые формализовал эту идею как **дистрибутивную гипотезу** в работе *"Distributional Structure"*.

### Эволюция подходов к представлению текста

| Год | Метод | Авторы | Размерность | Контекстуальность |
|-----|-------|--------|-------------|-------------------|
| 2003 | Neural LM embeddings | Bengio et al. | ~50 | Нет |
| 2013 | Word2Vec (CBOW, Skip-gram) | Mikolov et al. (Google) | 100-300 | Нет |
| 2014 | GloVe | Pennington et al. (Stanford) | 100-300 | Нет |
| 2017 | ELMo | Peters et al. (AllenNLP) | 1024 | Да |
| 2018 | BERT embeddings | Devlin et al. (Google) | 768 | Да |
| 2019 | Sentence-BERT | Reimers & Gurevych | 768 | Да |
| 2022 | text-embedding-ada-002 | OpenAI | 1536 | Да |
| 2024 | text-embedding-3-large | OpenAI | 3072 | Да |
| 2024 | Matryoshka (MRL) | Kusupati et al. | Adaptive | Да |

### Метрики сходства

| Метрика | Формула | Свойства | Применение |
|---------|---------|----------|------------|
| **Cosine Similarity** | cos(θ) = (A·B)/(‖A‖·‖B‖) | [-1, 1], инвариантна к масштабу | Semantic search, RAG |
| **Dot Product** | A·B = Σaᵢbᵢ | (-∞, +∞), учитывает magnitude | Рекомендации, ранжирование |
| **Euclidean Distance** | ‖A-B‖₂ = √Σ(aᵢ-bᵢ)² | [0, +∞), чувствительна к масштабу | Кластеризация |

### Проклятие размерности

> В высокоразмерных пространствах (d > 100) расстояния между точками становятся почти одинаковыми — феномен, известный как **проклятие размерности** (Bellman, 1957). Для embedding-моделей это означает: увеличение размерности сверх оптимума не улучшает качество поиска, но увеличивает стоимость хранения и вычислений. Подходы Matryoshka Representation Learning (Kusupati et al., 2022) позволяют обрезать вектор до нужной размерности без переобучения.

### Связь с [[vector-databases-guide|векторными базами данных]]

Embeddings хранятся и индексируются в специализированных системах (Pinecone, Qdrant, Weaviate), использующих алгоритмы приближённого поиска ближайших соседей (ANN): HNSW, IVF, PQ. Выбор embedding-модели напрямую влияет на качество [[rag-advanced-techniques|RAG-систем]].

---

**3. Размерность = детализация описания**
```
Описать человека:
- 2 измерения: [рост, вес] — грубо
- 10 измерений: + возраст, цвет глаз, ... — точнее
- 1024 измерения: все нюансы личности — очень точно

Больше измерений = точнее, но дороже хранить и обрабатывать
```

---

## Зачем это нужно

### Проблема: поиск по ключевым словам не понимает смысл

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Поиск "автомобиль" не находит "машина", "авто", "транспорт" | Keyword matching не знает синонимы | Пользователь не находит нужное |
| RAG возвращает нерелевантные документы | BM25 считает только TF-IDF | LLM галлюцинирует без контекста |
| Классификация требует ручных правил | Нет понимания семантики | Не масштабируется |
| Рекомендации только по explicit сигналам | Нет implicit similarity | Холодный старт, низкий engagement |

### Как embeddings решают эти проблемы

| Задача | Без embeddings | С embeddings |
|--------|----------------|--------------|
| **Семантический поиск** | Exact match, синонимы вручную | Понимание смысла автоматически |
| **RAG retrieval** | BM25, keyword overlap | Семантическая релевантность контексту |
| **Классификация** | Rule-based, features вручную | Automatic feature extraction |
| **Рекомендации** | Collaborative filtering only | Content-based + semantic similarity |
| **Кластеризация** | Topic modeling (LDA) | Dense representations, KMeans |
| **Duplicate detection** | Exact/fuzzy string matching | Semantic near-duplicates |

---

## Содержание

1. [Что такое embeddings?](#что-такое-embeddings)
2. [История: от Word2Vec до трансформеров](#история-от-word2vec-до-трансформеров)
3. [Как embeddings захватывают смысл](#как-embeddings-захватывают-смысл)
4. [Современные модели embeddings](#современные-модели-embeddings)
5. [Технические аспекты](#технические-аспекты)
6. [Практические рекомендации для RAG](#практические-рекомендации-для-rag)
7. [Сравнительная таблица моделей](#сравнительная-таблица-моделей)
8. [Источники](#источники)

---

## Что такое embeddings?

**Embeddings** (векторные представления) - это способ представления объектов (слов, предложений, изображений) в виде точек в многомерном пространстве, где расположение этих точек имеет семантический смысл для машинного обучения.

### Простая аналогия: GPS-координаты для смысла

Представьте, что каждое слово имеет свои "GPS-координаты" в пространстве значений:

- Слова "собака" и "кошка" находятся близко друг к другу (оба - домашние животные)
- Слово "автомобиль" находится далеко от них (другая категория)
- "Щенок" находится между "собакой" и "ребенок" (молодое существо)

\`\`\`
Пространство значений (упрощенно):

        живое
           |
    кошка  |  собака
           |
    -------|----------- домашнее
           |
           |  автомобиль
        неживое
\`\`\`

### Зачем нужны embeddings?

1. **Семантический поиск** - находить документы по смыслу, а не по ключевым словам
2. **RAG (Retrieval-Augmented Generation)** - предоставлять LLM релевантный контекст
3. **Классификация** - автоматически категоризировать тексты
4. **Кластеризация** - группировать похожие документы
5. **Рекомендательные системы** - находить похожий контент

---

## История: от Word2Vec до трансформеров

### 2013: Word2Vec - революция началась

**Word2Vec**, созданный Томашем Миколовым и командой в Google, стал первым подходом, производящим поразительно эффективные word embeddings. Он сделал возможным весь последующий прогресс в области NLP, включая трансформеры.

#### Две архитектуры Word2Vec

**CBOW (Continuous Bag of Words)**
- Предсказывает слово по его контексту
- Быстрее и эффективнее по памяти
- Пример: "The cat ___ on the mat" -> "sat"

**Skip-Gram**
- Предсказывает контекст по слову
- Лучше работает с редкими словами
- Пример: "sat" -> ["The", "cat", "on", "the", "mat"]

\`\`\`python
# Концептуальный пример Skip-Gram
# Входное слово "кот" -> предсказываем окружающие слова
input_word = "кот"
context_words = ["пушистый", "мурлычет", "спит", "на", "диване"]
\`\`\`

#### Главное ограничение Word2Vec

Word2Vec дает **одно представление для каждого слова**, независимо от контекста. Слово "bank" (банк реки vs. банк финансовый) получает усредненное представление, не отражающее ни один из смыслов точно.

### 2014: GloVe - глобальный взгляд

Stanford представил **GloVe (Global Vectors)**, который улучшил Word2Vec, анализируя глобальную статистику совместного появления слов во всем корпусе, а не только локальный контекст.

### 2016: FastText - морфология имеет значение

**FastText** от Facebook рассматривает слова как наборы символьных n-грамм. Это позволяет:
- Обрабатывать редкие слова
- Генерировать embeddings для слов, которых не было в обучающих данных
- Лучше работать с морфологически богатыми языками (включая русский)

### 2018: ELMo - контекст решает все

**ELMo (Embeddings from Language Models)** - первая модель с **контекстуальными embeddings**. Она использует двунаправленный LSTM и дает разные представления для одного слова в зависимости от контекста.

### 2017-2018: Трансформеры и BERT

**Трансформеры** ("Attention is All You Need", 2017) и **BERT** (2018) полностью изменили подход:

- **Self-attention** позволяет каждому слову "смотреть" на все остальные слова
- **Двунаправленный контекст** - BERT видит слова слева и справа одновременно
- **Pre-training + Fine-tuning** - универсальные представления, адаптируемые под задачу

\`\`\`
Эволюция: статические -> контекстуальные embeddings

Word2Vec (2013): "bank" = [0.2, 0.5, ...] (всегда одинаковый)
     |
     v
BERT (2018): "river bank" = [0.1, 0.7, ...]
             "money bank" = [0.8, 0.2, ...]
             (разные представления!)
\`\`\`

### 2022-2025: Специализированные embedding-модели

Современные модели обучаются специально для задач retrieval с использованием contrastive learning и instruction-tuning:
- Поддержка длинного контекста (до 32K токенов)
- Matryoshka Representation Learning для гибкости размерности
- Мультимодальность (текст + изображения)

---

## Как embeddings захватывают смысл

### Знаменитый пример: King - Man + Woman = Queen

Это самый известный пример векторной арифметики с word embeddings:

\`\`\`
vector("king") - vector("man") + vector("woman") ≈ vector("queen")
\`\`\`

#### Почему это работает?

Word2Vec анализирует огромные объемы текста и подсчитывает, какие слова часто появляются вместе. На основе этих co-occurrences создаются абстрактные представления - вектора из 200-300 чисел.

Вектор \`king - man\` захватывает концепцию "королевской особы" без гендерной составляющей. Добавляя \`woman\`, мы получаем "королевскую особу женского пола" = queen.

\`\`\`
Другие примеры:
- paris - france + poland ≈ warsaw (концепция "столица")
- walking - walk + swim ≈ swimming (преобразование формы глагола)
\`\`\`

#### Важная оговорка

В оригинальной статье входные слова (king, man, woman) исключаются при поиске ближайшего соседа. Без этого исключения результат часто остается "king". Это демонстрация работает благодаря некоторым "трюкам за кулисами".

Исследования показали, что такие аналогии хорошо работают для гендерных отношений, но значительно хуже для других семантических категорий.

### Как модели учатся семантике

1. **Гипотеза распределения** - слова в похожих контекстах имеют похожие значения
2. **Co-occurrence statistics** - подсчет совместных появлений слов
3. **Neural network training** - оптимизация весов для предсказания контекста
4. **Dimensionality reduction** - сжатие в плотное представление

---

## Современные модели embeddings

### OpenAI text-embedding-3 (Январь 2024)

| Модель | Размерность | MTEB | MIRACL | Цена |
|--------|-------------|------|--------|------|
| text-embedding-3-small | 1536 | ~62% | ~44% | \$0.02/1M токенов |
| text-embedding-3-large | 3072 | 64.6% | 54.9% | \$0.13/1M токенов |

**Ключевые особенности:**
- **Matryoshka Representation Learning** - можно урезать до 256/512/1024 dimensions
- 256-мерная версия text-embedding-3-large превосходит 1536-мерную ada-002
- 8,191 токенов контекстное окно
- Улучшение мультиязычности на 75% (с 31.4% до 54.9% на MIRACL)

### Voyage AI (2024-2025)

| Модель | Размерность | vs OpenAI | Контекст | Цена |
|--------|-------------|-----------|----------|------|
| voyage-3 | 1024 | +7.55% | 32K | \$0.06/1M токенов |
| voyage-3-lite | 512 | +3.82% | 32K | \$0.02/1M токенов |
| voyage-3-large | 2048 | +9.74% | 32K | ~\$0.12/1M токенов |
| voyage-code-3 | 1024 | +13.8% (код) | 32K | \$0.22/1M токенов |

**Ключевые особенности:**
- Лидер по качеству retrieval в январе 2025
- Поддержка Matryoshka + quantization (int8, binary)
- **voyage-multimodal-3** - текст + изображения + PDF screenshots
- **voyage-context-3** - сохранение глобального контекста документа в chunk embeddings
- Бесплатно: первые 200M токенов

### Cohere Embed v3

| Модель | Размерность | Языки | Цена |
|--------|-------------|-------|------|
| embed-english-v3.0 | 1024 | English | \$0.12/1M токенов |
| embed-multilingual-v3.0 | 1024 | 100+ | \$0.12/1M токенов |

**Ключевые особенности:**
- SOTA на мультиязычных benchmarks (MIRACL)
- Поддержка multimodal (текст + изображения) с января 2025
- Быстрее OpenAI на 50-60%
- Ограничение: 512 токенов на вход

### Google Gemini Embedding (2024-2025)

| Модель | Размерность | Цена |
|--------|-------------|------|
| gemini-embedding-001 | 768 | \$0.15/1M токенов |

**Ключевые особенности:**
- Топ-позиции на MTEB Multilingual leaderboard
- До 250 входов за запрос
- 2,048 токенов на вход (используются только первые)
- Бесплатно через Google AI Studio

### Open-source модели

#### BGE-M3 (BAAI, 2024)

\`\`\`
Характеристики:
- Размерность: 1024
- Параметры: 568M
- Контекст: 8,192 токена
- Языки: 170+
\`\`\`

**Уникальные возможности:**
- Три режима retrieval одновременно: dense, sparse, multi-vector
- SOTA на MIRACL (мультиязычный) и MKQA (кросс-язычный)
- Стабильная производительность даже на low-resource языках (арабский, кхмерский, иврит)

#### NVIDIA NV-Embed (2024-2025)

- Достиг 69.32 на MTEB (56 задач) - рекорд
- Новый latent attention layer
- Двухэтапное обучение: contrastive learning + hard negative mining

#### Stella (2024)

- Топ на MTEB retrieval с коммерческой лицензией
- Варианты 400M и 1.5B параметров

---

## Технические аспекты

### Выбор размерности (dimensions)

**Рекомендации по размерности:**

| Размер данных | Сложность задачи | Рекомендуемая размерность |
|---------------|------------------|---------------------------|
| < 100K предложений | Простая (keyword matching) | 50-100 |
| 100K - 1M | Средняя | 256-512 |
| > 1M | Сложная (semantic search) | 768-1024 |

**Sweet spot для text-embedding-3-large: 1024 dimensions**
- Практически та же производительность, что и 3072
- 3x меньше storage (4KB vs 12KB на вектор)

**Правило:** большие размерности захватывают больше нюансов, но требуют больше памяти и вычислений. Для 1M векторов: 1024d = 4GB, 256d = 1GB.

### Cosine Similarity vs Dot Product

\`\`\`python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def dot_product(a, b):
    return np.dot(a, b)
\`\`\`

**Когда использовать Cosine Similarity:**
- Когда важно только направление, не магнитуда
- Документы разной длины должны сравниваться одинаково
- Semantic search, классификация текстов

**Когда использовать Dot Product:**
- Когда магнитуда несет информацию (popularity, активность пользователя)
- Рекомендательные системы
- Когда embeddings уже нормализованы (dot product = cosine similarity)

**Важно:** Для L2-нормализованных векторов (большинство современных моделей) результаты идентичны. OpenAI и Vertex AI возвращают нормализованные embeddings.

### Quantization (квантизация)

Квантизация уменьшает размер embeddings с минимальной потерей качества:

| Тип | Размер | Ускорение | Потеря качества |
|-----|--------|-----------|-----------------|
| Float32 | 100% | 1x | 0% |
| Scalar (int8) | 25% | ~4x | ~1-3% |
| Binary (1-bit) | 3.1% | ~24x | ~5-10% |

**Практика в production:**
1. Binary quantization для первичного поиска (быстро, в памяти)
2. Scalar (int8) для rescoring (с диска)
3. Float32 только для финального ранжирования

\`\`\`python
# Пример rescoring pipeline
candidates = binary_search(query, top_k=1000)  # Быстрый поиск
reranked = scalar_rescore(query, candidates, top_k=100)  # Уточнение
final = full_precision_rank(query, reranked, top_k=10)  # Финал
\`\`\`

**MongoDB Atlas поддерживает:**
- Float32: максимальная точность
- Int8: 3.75x меньше RAM
- Binary: 24x меньше RAM

### Matryoshka Representation Learning (MRL)

MRL позволяет обучить модель так, чтобы embeddings можно было укорачивать без переобучения:

\`\`\`python
# Модель обучена на 1024 dimensions
full_embedding = model.encode("text")  # [1024 dimensions]

# Можно использовать любой префикс!
short_embedding = full_embedding[:256]  # [256 dimensions] - все еще работает!
\`\`\`

**Как это работает:**
- При обучении loss применяется к разным срезам: 768, 512, 256, 128, 64, 32
- Модель "front-loads" важную информацию в первые dimensions
- До 14x меньше storage при минимальной потере качества

**Модели с MRL:**
- OpenAI text-embedding-3-large
- Nomic nomic-embed-text-v1.5
- Voyage AI voyage-3-large
- Alibaba gte-multilingual-base

### Мультиязычные embeddings

**Ключевые модели:**

| Модель | Языки | Особенности |
|--------|-------|-------------|
| BGE-M3 | 170+ | Dense + sparse + multi-vector |
| LaBSE (Google) | 109 | Language-agnostic, работает даже на языках без training data |
| Cohere embed-multilingual-v3 | 100+ | Cross-lingual search |
| mE5 | 100+ | На базе XLM-RoBERTa |

**Cross-lingual retrieval:**
- Поиск на французском по финским документам
- Важно для международных компаний
- Проблема: "monolingual overfitting" - модели, обученные на английском, хуже работают на других языках даже с multilingual backbone

---

## Практические рекомендации для RAG

### Выбор модели embeddings

**Критерии выбора:**

1. **Соответствие домену** - модель должна понимать терминологию
2. **Benchmark производительность** - смотрите на Retrieval task в MTEB
3. **Context window** - достаточно ли для ваших документов?
4. **Latency и стоимость** - подходит ли для production?
5. **Мультиязычность** - нужна ли поддержка нескольких языков?

\`\`\`python
# Рекомендации по use cases
use_cases = {
    "general_english": "voyage-3 или text-embedding-3-large",
    "budget_conscious": "text-embedding-3-small или voyage-3-lite",
    "multilingual": "BGE-M3 или Cohere embed-multilingual-v3",
    "code": "voyage-code-3",
    "legal": "voyage-law-2",
    "finance": "voyage-finance-2",
    "self_hosted": "BGE-M3 или Stella"
}
\`\`\`

### Стратегии chunking

**Типы chunking:**

| Стратегия | Описание | Когда использовать |
|-----------|----------|-------------------|
| Fixed-size | Фиксированное количество токенов | Простой контент, скорость |
| Recursive | Иерархические разделители (\\n\\n, \\n, " ") | Структурированный текст |
| Semantic | Разбиение по смысловым границам | Когда качество важнее скорости |

**Рекомендуемые параметры:**
- **Размер chunk:** 400-512 токенов
- **Overlap:** 10-20% (50-100 токенов)
- **Стартовый вариант:** RecursiveCharacterTextSplitter

\`\`\`python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\\n\\n", "\\n", ". ", " ", ""]
)
\`\`\`

**Late Chunking (Jina AI, 2024):**

Новый подход, сохраняющий контекст документа:
1. Пропустить весь документ через transformer
2. Получить token-level embeddings с полным контекстом
3. Применить mean pooling к каждому chunk

\`\`\`python
# API-вызов с late chunking
response = client.embed(
    model="jina-embeddings-v3",
    input=["chunk1", "chunk2", "chunk3"],
    late_chunking=True  # Сохраняет контекст между chunks
)
\`\`\`

### Hybrid Search

Комбинация vector search и keyword search (BM25):

\`\`\`python
# Пример hybrid search с Anthropic's Contextual Retrieval
def hybrid_search(query, documents):
    # 1. Dense retrieval (semantic)
    dense_results = vector_search(query, documents, top_k=20)
    
    # 2. Sparse retrieval (keyword, BM25)
    sparse_results = bm25_search(query, documents, top_k=20)
    
    # 3. Fusion (RRF - Reciprocal Rank Fusion)
    combined = reciprocal_rank_fusion(dense_results, sparse_results)
    
    # 4. Reranking для финального ранжирования
    final = rerank(query, combined, top_k=5)
    
    return final
\`\`\`

**Anthropic Contextual Retrieval:**
- Уменьшает failed retrievals на 49%
- С reranking - на 67%

### Semantic Caching

Кэширование на основе семантического сходства запросов:

\`\`\`python
class SemanticCache:
    def __init__(self, similarity_threshold=0.95):
        self.cache = {}
        self.embeddings = {}
        self.threshold = similarity_threshold
    
    def get(self, query):
        query_embedding = embed(query)
        
        for cached_query, cached_response in self.cache.items():
            similarity = cosine_similarity(
                query_embedding, 
                self.embeddings[cached_query]
            )
            if similarity > self.threshold:
                return cached_response
        
        return None
    
    def set(self, query, response):
        self.cache[query] = response
        self.embeddings[query] = embed(query)
\`\`\`

**Результаты в production:**
- Снижение стоимости LLM inference до 86%
- Улучшение latency до 88% (с 2.7s до 0.3s)

**Лучшая модель для semantic caching:** \`all-mpnet-base-v2\` (баланс precision, recall, latency)

### Fine-tuning embeddings

**Когда fine-tuning нужен:**
- Специфическая доменная терминология (медицина, право, финансы)
- Off-the-shelf модели показывают плохие результаты
- Есть размеченные данные (query-document пары)

**Когда НЕ нужен:**
- Проблема в chunking, а не в модели
- Нужен exact keyword matching (используйте hybrid search)
- Мало обучающих данных
- Данные пересекаются с pre-training корпусом модели

**Результаты:**
- ~7% улучшение с 6.3K samples
- 3 минуты обучения на consumer GPU
- С MRL: 99% производительности при 6x меньшем storage

\`\`\`python
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import MultipleNegativesRankingLoss

# Fine-tuning с contrastive loss
model = SentenceTransformer('BAAI/bge-base-en-v1.5')
train_loss = MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100
)
\`\`\`

---

## Сравнительная таблица моделей

### Коммерческие API (Декабрь 2024)

| Модель | Размерность | Контекст | Цена (\$/1M токенов) | Примечания |
|--------|-------------|----------|---------------------|------------|
| **OpenAI text-embedding-3-small** | 1536 | 8K | \$0.02 | Лучшее соотношение цена/качество |
| **OpenAI text-embedding-3-large** | 3072* | 8K | \$0.13 | MRL (можно до 256d) |
| **Voyage voyage-3** | 1024 | 32K | \$0.06 | +7.55% vs OpenAI large |
| **Voyage voyage-3-large** | 2048* | 32K | ~\$0.12 | SOTA январь 2025 |
| **Voyage voyage-3-lite** | 512 | 32K | \$0.02 | Экономичный вариант |
| **Cohere embed-v3** | 1024 | 512 | \$0.12 | 100+ языков, multimodal |
| **Google gemini-embedding-001** | 768 | 2K | \$0.15 | Топ multilingual |

*Поддерживает MRL (сокращение размерности без потери качества)

### Open-source модели

| Модель | Размерность | Контекст | Параметры | Особенности |
|--------|-------------|----------|-----------|-------------|
| **BGE-M3** | 1024 | 8K | 568M | Dense+sparse+multi-vector, 170 языков |
| **Stella-1.5B** | 1024 | 8K | 1.5B | Топ MTEB retrieval, коммерческая лицензия |
| **NV-Embed** | 4096 | 32K | 8B | MTEB рекорд 69.32 |
| **gte-Qwen2-7B** | 4096 | 131K | 7B | Отличный multilingual |
| **jina-embeddings-v3** | 1024 | 8K | 570M | Late chunking, MRL |

---

## Актуальность 2024-2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **Voyage-3-large** | 🔥 SOTA (январь 2025) | +9.74% vs OpenAI v3-large, 32K контекст, multimodal support |
| **Gemini-embedding-001** | 🥇 MTEB #1 | Топ multilingual, 768 dims, бесплатно в Google AI Studio |
| **Matryoshka (MRL)** | ✅ Production-ready | До 14x меньше storage при 96-99% quality, front-loading info |
| **Late Chunking** | 🆕 Набирает популярность | Jina: 82-84% vs 70-75% similarity, сохраняет контекст документа |
| **Binary Quantization** | ✅ Production | 32x memory reduction, 96% performance с rescoring strategy |
| **Scalar (int8) Quantization** | ✅ Production | 4x memory reduction, 99% performance retention |
| **Sentence Transformers 3.0** | ✅ Релиз | MNR Loss, Matryoshka Loss, простой fine-tuning API |
| **Synthetic Contrastive Data** | 🔄 Best practice | LLM-generated hard negatives для fine-tuning |

### Community Sentiment (Reddit, HN, Stack Overflow)

**Что хвалят:**
- Voyage-3: "значительно лучше OpenAI для retrieval" (r/LocalLLaMA)
- BGE-M3: "лучший open-source для мультиязычных задач"
- MRL: "game-changer для production costs"

**Что критикуют:**
- OpenAI v3: "overhyped, Voyage лучше за те же деньги"
- Cohere: "512 токенов — слишком мало для реальных документов"
- Fine-tuning: "часто проблема в chunking, а не в модели"

### Benchmarks 2025

| Модель | MTEB Score | MIRACL (multilingual) | Retrieval |
|--------|------------|----------------------|-----------|
| Gemini-embedding-001 | 68.4 | — | — |
| Qwen3-Embedding | 68.2 | — | — |
| Voyage-3-large | ~67 | 59.2% | 64.9% |
| NV-Embed-v2 | 69.32 | — | — |
| OpenAI v3-large | 64.6 | 54.9% | — |

---

## Источники

### Теоретические основы
- Mikolov, T. et al. (2013). *Efficient Estimation of Word Representations in Vector Space* (Word2Vec). arXiv:1301.3781.
- Harris, Z. (1954). *Distributional Structure*. Word, 10(2-3), 146-162.
- Firth, J.R. (1957). *A Synopsis of Linguistic Theory*. Studies in Linguistic Analysis.
- Pennington, J. et al. (2014). *GloVe: Global Vectors for Word Representation*. EMNLP.
- Bengio, Y. et al. (2003). *A Neural Probabilistic Language Model*. JMLR.
- Reimers, N. & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP.
- Kusupati, A. et al. (2022). *Matryoshka Representation Learning*. NeurIPS.
- Bellman, R. (1957). *Dynamic Programming*. Princeton University Press. (проклятие размерности)

### Практические руководства
- [OpenAI Embeddings Docs](https://platform.openai.com/docs/guides/embeddings)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Contextual Retrieval — Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- [How to Choose Embedding Model — Weaviate](https://weaviate.io/blog/how-to-choose-an-embedding-model)
- [Late Chunking — Jina AI](https://jina.ai/news/late-chunking-in-long-context-embedding-models/)
- [Sentence Transformers 3.0 — HuggingFace](https://huggingface.co/blog/train-sentence-transformers)

---

## Quick Reference Card

\`\`\`
ВЫБОР МОДЕЛИ:
- Общее использование (EN): voyage-3 или text-embedding-3-large
- Бюджетный вариант: text-embedding-3-small (~\$0.02/1M)
- Мультиязычный: BGE-M3 или Cohere multilingual
- Код: voyage-code-3
- Self-hosted: BGE-M3 (568M params)

РАЗМЕРНОСТЬ:
- Production sweet spot: 512-1024
- Используйте MRL модели для гибкости
- 1024d embedding = 4KB storage

CHUNKING:
- Стартовый размер: 400-512 токенов
- Overlap: 10-20%
- Используйте recursive splitter
- Попробуйте late chunking для длинных документов

SIMILARITY:
- Нормализованные vectors: dot product = cosine (одинаково)
- OpenAI/Voyage возвращают нормализованные embeddings
- Используйте metric из документации модели

QUANTIZATION В PRODUCTION:
- Binary для поиска (32x экономия памяти)
- Int8 для rescoring (4x экономия)
- Float32 только для финального ранжирования
\`\`\`

---

*Последнее обновление: 2024-12-28*

---

## Связь с другими темами

### [[vector-databases-guide]]

Embeddings и vector databases — неразделимая пара: embeddings создают векторные представления, а vector databases хранят и ищут по ним. Выбор embedding модели (размерность вектора, quantization, скорость inference) напрямую влияет на требования к vector database: размер индекса, latency поиска, стоимость хранения. Понимание алгоритмов similarity search (HNSW, IVF, PQ) помогает выбрать правильную embedding модель — например, binary quantization совместима не со всеми алгоритмами.

### [[rag-advanced-techniques]]

Embeddings — фундамент retrieval-этапа в RAG pipeline. Качество embedding модели определяет, насколько точно система найдёт релевантные документы по запросу пользователя. Техники вроде HyDE (Hypothetical Document Embedding), semantic chunking и query expansion опираются на свойства embedding пространства. Fine-tuning embedding модели на domain-specific данных может дать до +7% improvement в retrieval accuracy, что каскадно улучшает качество всего RAG pipeline.

### [[aiml-databases-complete]]

Embeddings трансформируют традиционные подходы к хранению и поиску данных. Помимо специализированных vector databases, многие реляционные СУБД (PostgreSQL с pgvector, SQLite с sqlite-vss) добавляют поддержку vector search, что позволяет хранить embeddings вместе с metadata в одной системе. Понимание trade-offs между native vector databases и vector-расширениями SQL баз критично для архитектуры data layer в AI-приложениях.

---

[[ai-engineering-moc|← AI Engineering MOC]] | [[vector-databases-guide|Vector Databases →]]

---

---

## Проверь себя

> [!question]- Почему Matryoshka Representation Learning (MRL) считается прорывом для production-систем?
> MRL позволяет обрезать embedding вектор до любого префикса (например, 1024 -> 256 dimensions) без переобучения модели. Модель "front-loads" важную информацию в первые dimensions. Результат: до 14x экономия storage при 96-99% сохранении качества, адаптивный trade-off скорость/качество в runtime.

> [!question]- У вас RAG-система с 10M документов, latency поиска 500ms. Как снизить до <50ms с минимальной потерей качества?
> Трехуровневый pipeline: 1) Binary quantization для первичного поиска in-memory (32x экономия RAM, top-1000), 2) Scalar int8 rescoring (4x экономия, top-100), 3) Float32 reranking (top-10). С rescoring binary достигает 96%+ исходного качества при latency <50ms.

> [!question]- Когда fine-tuning embedding модели оправдан, а когда это пустая трата ресурсов?
> Оправдан: специфическая доменная терминология (медицина, право), off-the-shelf модели <70% accuracy, есть 5000+ query-document пар. Не оправдан: проблема в chunking а не в модели (проверьте сначала!), нужен exact matching (используйте hybrid search), мало данных (<1000 пар), general-purpose задачи.

> [!question]- Почему Late Chunking дает 82-84% similarity вместо 70-75% у традиционного chunking?
> Традиционный chunking разбивает документ, затем embed каждый chunk отдельно -- chunk теряет контекст. Late Chunking сначала пропускает весь документ через transformer (получая token-level embeddings с полным контекстом), затем применяет mean pooling к каждому chunk. Каждый chunk "помнит" о чем весь документ.

---

## Ключевые карточки

Что такое embedding и зачем нужен?
?
Числовое представление объекта (слова, предложения) в виде вектора. Похожие по смыслу тексты имеют близкие векторы. Применения: семантический поиск, RAG retrieval, классификация, кластеризация, рекомендации.

Cosine Similarity vs Dot Product -- когда что?
?
Cosine Similarity: когда важно только направление (семантический поиск, разные длины документов). Dot Product: когда магнитуда несет информацию (рекомендации, popularity). Для нормализованных векторов (OpenAI, Voyage) результаты идентичны.

Какую модель embeddings выбрать в 2025?
?
Общее (EN): Voyage-3 или text-embedding-3-large. Бюджет: text-embedding-3-small ($0.02/1M). Мультиязычный: BGE-M3 или Cohere multilingual. Код: voyage-code-3. Self-hosted: BGE-M3 (568M params). SOTA: Voyage-3-large (+9.74% vs OpenAI).

Оптимальные параметры chunking для RAG?
?
Размер chunk: 400-512 токенов. Overlap: 10-20% (50-100 токенов). Стартовый вариант: RecursiveCharacterTextSplitter. Для длинных документов: попробовать Late Chunking (Jina AI) для сохранения контекста.

Что такое Hybrid Search и зачем нужен?
?
Комбинация vector search (semantic similarity) и keyword search (BM25). Vector search понимает смысл, BM25 ловит точные термины. Объединение через Reciprocal Rank Fusion + reranking. Anthropic Contextual Retrieval: -49% failed retrievals, с reranking -67%.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[vector-databases-guide]] | Где и как хранить embeddings для быстрого поиска |
| Углубиться | [[rag-advanced-techniques]] | Продвинутые техники RAG, использующие embeddings |
| Смежная тема | [[database-design-optimization]] | Паттерны проектирования БД, применимые к vector storage |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
