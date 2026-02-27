---
title: "Vector Databases: Полное руководство"
created: 2025-12-24
updated: 2026-02-13
author: AI Assistant
reading_time: 75
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
level: intermediate-advanced
type: guide
topics:
  - vector-database
  - embeddings
  - similarity-search
  - RAG
  - HNSW
  - IVF
  - PQ
  - DiskANN
  - hybrid-search
  - production
status: published
tags:
  - topic/ai-ml
  - type/guide
  - level/intermediate
related:
  - "[[embeddings-complete-guide]]"
  - "[[rag-advanced-techniques]]"
  - "[[aiml-databases-complete]]"
---

# Vector Databases: Полное руководство

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Embeddings** | Как текст превращается в вектор | [[embeddings-complete-guide]] |
| **Базовое понимание SQL** | Сравнение с традиционными БД | [[databases-fundamentals-complete]] |
| **Python** | Примеры интеграции | Любой курс Python |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Частично | Сначала [[embeddings-complete-guide]] |
| **Backend Developer** | ✅ Да | Интеграция vector search в приложения |
| **AI/ML Engineer** | ✅ Да | RAG, semantic search, similarity |
| **DevOps** | ✅ Да | Deployment и масштабирование |

### Терминология для новичков

> 💡 **Vector Database** = база данных для поиска "по смыслу", а не по ключевым словам

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Vector/Embedding** | Числовое представление смысла | **Координаты** — каждый текст = точка в пространстве смыслов |
| **Similarity Search** | Поиск похожих векторов | **Найти соседей** — кто ближе всего в пространстве |
| **Cosine Similarity** | Мера похожести (угол между векторами) | **Угол зрения** — одинаковое направление = похоже |
| **HNSW** | Hierarchical Navigable Small World | **Граф связей** — быстрый поиск через соседей соседей |
| **ANN** | Approximate Nearest Neighbors | **Примерный поиск** — быстрее, чем точный, но не 100% |
| **Index** | Структура для быстрого поиска | **Оглавление** — не читаем всё, сразу к нужному |
| **Hybrid Search** | Vector + keyword поиск вместе | **Двойная проверка** — и по смыслу, и по словам |
| **Recall** | Доля найденных релевантных результатов | **Полнота** — сколько нужного нашли из всего нужного |

---

## Теоретические основы

### Формальное определение

> **Векторная база данных** — специализированная СУБД, оптимизированная для хранения, индексирования и поиска высокоразмерных векторов (embeddings). Основная операция — поиск k ближайших соседей (k-NN): для запроса q найти k векторов из коллекции, минимизирующих функцию расстояния d(q, vᵢ).

### Проблема точного поиска

Точный k-NN поиск в пространстве ℝⁿ имеет сложность O(n·d), где n — количество векторов, d — размерность. При миллионах векторов и размерности 1536+ это неприемлемо медленно. Отсюда потребность в алгоритмах **приближённого поиска ближайших соседей (ANN)**.

### Ключевые алгоритмы ANN

| Алгоритм | Год | Авторы | Принцип | Complexity (query) |
|----------|-----|--------|---------|-------------------|
| **LSH** | 1999 | Gionis, Indyk, Motwani | Хеширование в бакеты | O(d · n^ρ), ρ < 1 |
| **IVF** (Inverted File) | 2003 | Jégou et al. | Кластеризация + поиск в кластерах | O(d · nprobe · n/nlist) |
| **PQ** (Product Quantization) | 2011 | Jégou, Douze, Schmid | Разбиение на субвекторы + кодбук | O(d · k) |
| **HNSW** | 2018 | Malkov & Yashunin | Навигируемый граф малого мира | O(d · log n) |
| **DiskANN** | 2019 | Subramanya et al. (Microsoft) | HNSW на диске, Vamana graph | O(d · log n) |
| **ScaNN** | 2020 | Guo et al. (Google) | Anisotropic quantization | O(d · √n) |

### HNSW: доминирующий алгоритм

> **Hierarchical Navigable Small World** (Malkov & Yashunin, 2018) строит многоуровневый навигируемый граф. На верхних уровнях — разреженный граф для грубого поиска, на нижних — плотный для точного. Аналогия: сеть автострад (верхний уровень) и городских улиц (нижний уровень). HNSW обеспечивает O(log n) сложность запроса при recall > 95%.

### Гибридный поиск: теоретическое обоснование

Комбинация [[embeddings-complete-guide|семантического поиска]] (vector) и лексического (BM25) повышает recall, поскольку методы имеют ортогональные сильные стороны:
- **Vector search**: находит семантически близкое ("автомобиль" ≈ "машина")
- **BM25**: находит точные совпадения (акронимы, имена, ID)

Стандартный подход к объединению — **Reciprocal Rank Fusion (RRF)**: score(d) = Σ 1/(k + rank_i(d)).

---

## Начнем с интуиции

Представь, что у тебя есть библиотека с миллионами фотографий. Пользователь загружает фото котенка и хочет найти похожие изображения. Как бы ты это сделал?

Первая мысль: "Сравню каждую фотографию с запросом". Но миллион сравнений займет секунды или даже минуты. А если фотографий миллиард?

Вторая мысль: "Может, организовать фото по папкам?" Отличная идея! Но по каким признакам? Цвет? Объекты? Настроение? И как искать "похожие", а не "точно такие же"?

Именно для решения этой проблемы и существуют **vector databases** -- специализированные базы данных, которые хранят не просто данные, а их математические "отпечатки" (embeddings) и умеют молниеносно находить похожие отпечатки среди миллиардов.

---

## Зачем это нужно

### Проблема: keyword search не понимает смысл

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Поиск "машина" не находит "автомобиль" | Keyword matching ищет точные совпадения | Пользователь не находит релевантное |
| RAG возвращает нерелевантный контекст | BM25 оптимизирован для TF-IDF, не семантику | LLM галлюцинирует |
| Поиск по миллионам занимает секунды | Brute-force O(n) на каждый запрос | UX неприемлем |
| Сложно добавить похожий контент | Exact match не понимает "похожесть" | Рекомендации не работают |

### Как vector databases решают проблемы

| Задача | Без vector DB | С vector DB |
|--------|---------------|-------------|
| **Семантический поиск** | Keyword + синонимы вручную | Автоматическое понимание смысла |
| **RAG retrieval** | BM25 fails на перефразировках | 95%+ recall на semantic queries |
| **Latency на миллионах** | Секунды (brute-force) | <50ms (HNSW, ANN) |
| **Похожие товары** | Category matching | Semantic similarity |
| **Multi-modal search** | Отдельные системы для текста/картинок | Единый embedding space |

---

## Оглавление

1. [Почему обычные базы данных не подходят](#почему-обычные-базы-данных-не-подходят)
2. [Как работают vector databases](#как-работают-vector-databases)
3. [Алгоритмы индексации: магия быстрого поиска](#алгоритмы-индексации)
4. [Метрики расстояния: какую выбрать](#метрики-расстояния)
5. [Обзор баз данных 2025](#обзор-баз-данных-2025)
6. [pgvector: когда PostgreSQL достаточно](#pgvector)
7. [Hybrid Search: лучшее из двух миров](#hybrid-search)
8. [Reranking: финальная полировка результатов](#reranking)
9. [Embedding Models: выбор модели](#embedding-models)
10. [Chunking Strategies: как разбивать документы](#chunking-strategies)
11. [Multi-tenancy: изоляция данных](#multi-tenancy)
12. [Production Best Practices](#production-best-practices)
13. [Практические истории из реальных проектов](#практические-истории)
14. [Как выбрать свою базу данных](#как-выбрать-базу-данных)
15. [Проверь себя](#проверь-себя)

---

## Почему обычные базы данных не подходят

### Проблема на пальцах

Допустим, ты описал каждую фотографию в виде вектора из 1536 чисел (это стандартный размер embedding от OpenAI). Каждое число отражает какую-то характеристику изображения -- яркость, наличие определенных объектов, эмоциональную окраску.

Теперь у тебя 10 миллионов таких векторов. Чтобы найти 10 самых похожих к запросу, нужно:

```
10,000,000 векторов x 1536 измерений = 15.36 миллиарда операций
```

Даже на современном железе это займет секунды. А пользователь ждать не будет.

### Почему SQL не поможет

Традиционные базы данных оптимизированы для точных запросов:
- "Найди пользователя с ID = 12345" -- это легко, есть индексы
- "Найди все заказы за вчера" -- тоже просто, дата -- это число

Но "найди похожие" -- это совсем другая задача. B-tree индексы, которые делают SQL быстрым, работают с упорядоченными данными. Вектор из 1536 измерений нельзя "упорядочить" в традиционном смысле.

### Решение: приближенный поиск

Вместо того чтобы проверять каждый вектор (точный поиск, или exact search), vector databases используют **Approximate Nearest Neighbor (ANN)** -- приближенный поиск ближайших соседей.

Идея проста: мы готовы потерять 1-5% точности ради ускорения в 1000 раз. Вместо проверки всех 10 миллионов векторов, умные алгоритмы проверяют только ~10,000 -- и находят 95-99% тех же результатов.

Это как искать книгу в библиотеке: можно проверить каждую полку (точно, но долго), а можно сначала пойти в нужный раздел, потом на нужную полку (быстро и почти всегда правильно).

---

## Как работают vector databases

### Анатомия vector database

Прежде чем погружаться в алгоритмы, давай разберемся, из чего состоит типичная vector database. Это не просто "хранилище векторов" -- это сложная система с несколькими слоями.

**API Layer** -- точка входа. Ты отправляешь запросы (вставить вектор, найти похожие, удалить), а этот слой их обрабатывает. Обычно это REST API, gRPC или SDK для популярных языков.

**Index Layer** -- сердце системы. Здесь живут структуры данных, которые делают поиск быстрым. Именно здесь работают алгоритмы HNSW, IVF и другие, о которых мы поговорим дальше.

**Storage Layer** -- где физически хранятся векторы. Часто используется memory-mapping (mmap), чтобы работать с данными, которые не помещаются в RAM.

**Metadata Layer** -- дополнительная информация о векторах. Когда ты ищешь похожие документы, тебе часто нужно фильтровать: "только за последний месяц", "только категория 'технологии'". Metadata позволяет это делать.

**Distributed Layer** -- когда данных много, одного сервера не хватает. Этот слой отвечает за шардирование (разделение данных между серверами) и репликацию (копии для надежности).

### Что делает vector database особенной

Обычная база данных отвечает на вопрос: "Дай мне запись с ID = 123".

Vector database отвечает на вопрос: "Дай мне записи, наиболее похожие на этот вектор".

Это фундаментально разные задачи, и для их решения нужны разные структуры данных.

---

## Алгоритмы индексации

Теперь самое интересное -- алгоритмы, которые делают vector databases быстрыми. Основные: HNSW, IVF, PQ и DiskANN. Каждый решает проблему по-своему.

### HNSW: карта метро с экспресс-станциями

**Hierarchical Navigable Small World** -- самый популярный алгоритм в 2025 году. Его используют Pinecone, Qdrant, Weaviate, pgvector.

#### Аналогия

Представь карту метро большого города. Есть обычные станции, где поезда останавливаются постоянно. А есть экспресс-линии, которые пропускают мелкие станции и быстро доставляют тебя в нужный район.

HNSW работает так же. Он строит несколько "слоев" графа:

- **Верхний слой (Layer 3)** -- редкие "экспресс-станции". Всего несколько узлов, соединенных длинными ребрами. Здесь мы быстро "прыгаем" в нужный район.

- **Средние слои (Layer 1-2)** -- больше станций, более короткие переходы. Уточняем позицию.

- **Нижний слой (Layer 0)** -- все станции. Здесь все векторы, и мы ищем точный ответ среди ближайших соседей.

#### Как происходит поиск

1. Начинаем с верхнего слоя. Находим ближайший узел к нашему запросу.
2. Спускаемся на слой ниже, используя найденный узел как стартовую точку.
3. Повторяем, пока не дойдем до нижнего слоя.
4. На нижнем слое возвращаем top-k ближайших соседей.

Сложность поиска -- O(log n). Это означает, что для 10 миллионов векторов нужно примерно 23 шага вместо 10 миллионов.

#### Параметры HNSW: детальная настройка

У HNSW есть три ключевых параметра, и понимание их -- разница между "работает" и "работает хорошо".

**M (количество связей на узел)** -- сколько "соседей" может иметь каждый узел в графе на каждом уровне иерархии. Больше связей = лучше recall и точность (поиск имеет больше путей для исследования), но больше памяти и медленнее вставка.

Рекомендации по M:
- **M = 5-12** -- для датасетов с низкой внутренней размерностью
- **M = 12-48** -- подходит для большинства случаев
- **M = 48-64** -- для высокоразмерных данных (word embeddings, face descriptors)
- **M = 2-100** -- общий разумный диапазон

Потребление памяти: примерно M * 8-10 байт на хранимый элемент.

**ef_construction (размер поиска при построении)** -- контролирует количество кандидатов-соседей, исследуемых при вставке узла в граф. Более высокое значение (например, 400 vs 200) позволяет алгоритму находить более оптимальные связи, что приводит к более качественному графу и лучшему recall. Однако это значительно увеличивает время построения.

Рекомендации:
- Начните с **ef_construction = 100-200** для большинства случаев
- Для высокого recall используйте **ef_construction = 400-500**
- Правило: если recall при ef = ef_construction меньше 0.9, есть потенциал для улучшения

**ef_search (размер поиска при запросе)** -- размер динамического списка ближайших соседей во время поиска. Большее значение ведет к более точному, но медленному поиску. Значение ef_search не может быть меньше k (количество запрашиваемых соседей).

Влияние на производительность:
- **ef_search = 100**: ~85% recall, ~1ms latency
- **ef_search = 500**: ~98% recall, ~5ms latency

**Рекомендуемые конфигурации:**

| Сценарий | M | ef_construction | ef_search |
|----------|---|-----------------|-----------|
| Real-time система | 12 | 200 | 100 |
| Высокий recall | 24 | 400 | 500 |
| Баланс | 16 | 128 | 128 |
| Максимальный recall | 64 | 256 | 256 |

```python
# Пример настройки HNSW в Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,  # Размерность OpenAI embeddings
        distance=Distance.COSINE
    ),
    hnsw_config=HnswConfigDiff(
        m=16,                    # Золотая середина
        ef_construct=100,        # Достаточно для хорошего качества
        full_scan_threshold=10000  # До 10K записей делаем brute force
    )
)
```

### IVF: библиотека с разделами по темам

**Inverted File Index** -- более старый, но все еще полезный подход. Это partition-based индекс, основанный на хранении, в отличие от HNSW, который in-memory.

#### Аналогия

Представь большую библиотеку. Вместо того чтобы искать книгу среди всех полок, ты сначала идешь в нужный раздел: "Художественная литература", потом "Фантастика", потом "Научная фантастика". И только там ищешь среди сотни книг вместо миллиона.

IVF делает то же самое с векторами. Он разбивает все пространство на кластеры с помощью k-means, и при поиске сначала определяет, какие кластеры ближе всего к запросу.

#### Как это работает

**Этап 1: Обучение (Clustering Phase).** Берем все векторы (или их выборку) и применяем k-means кластеризацию. Получаем N центроидов (центров кластеров). Каждый вектор "привязывается" к ближайшему центроиду.

K-means -- итеративный алгоритм: сначала случайно выбираются K точек как центроиды, затем на каждой итерации все точки присваиваются ближайшему центроиду, и центроиды обновляются до среднего значения каждого кластера.

**Этап 2: Поиск.** Получив запрос:
1. Находим nprobe ближайших центроидов к запросу
2. Ищем только среди векторов в этих кластерах
3. Возвращаем top-k

**Два ключевых параметра:**

**nlist** -- количество кластеров. Обычно берут корень из числа векторов.
- Для 1 миллиона -- около 1000 кластеров
- Увеличение кластеров ускоряет поиск в каждом, но требует проверки большего числа центроидов

**nprobe** -- сколько кластеров проверять при поиске.
- Больше = лучше recall, медленнее поиск
- Обычно 10-100
- Для датасета с 1M векторов и 1000 кластеров, nprobe=10 означает проверку ~1% данных

### HNSW vs IVF: детальное сравнение

| Характеристика | HNSW | IVF |
|----------------|------|-----|
| **Тип структуры** | Граф | Кластеры |
| **Производительность** | 3x лучше чем IVFFlat | Базовая |
| **Память** | Много (хранит связи) | Мало (особенно с PQ) |
| **Время построения** | Долгое | Быстрое |
| **Динамические обновления** | Отлично | Плохо (нужен rebuild) |
| **Recall** | Очень высокий | Зависит от качества кластеров |
| **Filtered search** | Менее эффективен | Более эффективен |
| **Высокоразмерные данные** | Хорошо держит | Деградирует (curse of dimensionality) |
| **Стоимость (AWS пример)** | ~$75/час | ~$11/час (с IVFPQ) |

**Выбирай HNSW**, если:
- Данные часто обновляются (новые документы, удаления)
- Нужен максимальный recall
- Память не проблема
- Высокоразмерные embeddings

**Выбирай IVF**, если:
- Данные обновляются batch'ами (раз в день, раз в неделю)
- Память ограничена
- Нужна эффективная фильтрация (pre-filtering)
- Огромные датасеты с бюджетными ограничениями

### PQ: сжатие для экономии памяти

**Product Quantization** решает проблему памяти. HNSW и IVF ускоряют поиск, но сами векторы все еще занимают много места. Вектор из 1536 float32 -- это 6 KB. Миллиард таких -- 6 TB только на векторы!

#### Аналогия

Когда ты отправляешь фото в мессенджере, оно сжимается. Да, качество немного падает, но файл становится в 10 раз меньше. PQ делает то же самое с векторами.

#### Как это работает

1. **Разбиваем вектор на части (субвекторы).** Например, вектор из 128 измерений разбиваем на 8 частей по 16 измерений.

2. **Для каждой части создаем "словарь" (codebook)** из 256 типичных значений. Этот словарь создается на обучающих данных с помощью k-means.

3. **Кодируем:** Вместо хранения реального субвектора храним индекс ближайшего значения из словаря (1 byte!).

4. **Результат:** Весь вектор вместо 512 bytes (128 x 4) теперь занимает 8 bytes (8 индексов по 1 byte).

**Сжатие в 64 раза!** PQ может обеспечить сжатие до 64x, тогда как обычная scalar quantization -- до 32x.

#### Ключевые преимущества

- **Массивная компрессия:** для некоторых приложений сжатие может превышать 95%
- **Эффективное использование памяти:** если оригинальный вектор разбит на n частей, он кодируется n числами
- **Оптимальное хранение:** количество центроидов k обычно выбирается степенью 2 для эффективности, требуя n * log(k) бит на вектор

#### Trade-offs

PQ -- lossy compression, часть информации теряется:
- Recall падает на 1-5%
- Расстояния становятся приблизительными
- Для компенсации используется rescoring с полными векторами

**Параметры PQ:**
- **m** -- количество субвекторов (размерность должна делиться на m)
- **code_size** -- биты на субвектор (обычно 8)
- Рекомендация: code_size = 8, затем настраивайте m для баланса памяти и recall

### IVF_PQ: комбинированный подход

IVF_PQ объединяет IVF для грубого сужения поиска и PQ для сжатия векторов:

1. IVF быстро сужает область поиска до нескольких кластеров
2. PQ позволяет хранить больше векторов в памяти
3. Итог: значительно улучшенная скорость при меньшем потреблении памяти

**Benchmark:** IVFPQ+HNSW занимает всего 154 MB -- это в 15 раз меньше чем HNSW alone!

### Binary Quantization: 40x ускорение

Binary Quantization (BQ) -- еще более агрессивный метод сжатия, появившийся в 2024 году.

#### Как работает

Все числа больше нуля становятся 1, остальные -- 0. Каждое измерение кодируется 1 битом вместо 32.

**Результат:**
- **32x сжатие памяти:** 100K OpenAI Ada-002 векторов: 900 MB -> 128 MB
- **До 40x ускорение поиска** благодаря использованию Hamming distance (XOR операции)

#### Когда использовать

Binary quantization эффективна только для:
- **Высокоразмерных векторов** (>=1024 dimensions)
- **Центрированного распределения** компонент

Реальные результаты:
- OpenAI text-embedding-ada-002 (1536d): 0.98 recall@100 с 4x oversampling
- Cohere embed-english-v2.0 (4096d): 0.98 recall@50 с 2x oversampling
- mxbai-embed-large-v1: сохраняет >96% производительности при 32x сжатии

**Поддержка:**
- Qdrant: автоматическая BQ при индексации
- OpenSearch 2.17+: поддержка 1, 2, или 4 бит на измерение
- Weaviate: BQ для flat и HNSW индексов
- pgvector 0.7+: binary_quantize функция

### DiskANN: миллиард векторов на одном сервере

**DiskANN** -- прорыв от Microsoft Research для billion-scale поиска на SSD.

#### Проблема, которую решает DiskANN

HNSW достигает 95% recall при <5ms для 100M векторов, но требует ~500GB RAM. На 1B векторов стоимость RAM в облаке превышает $10k/месяц.

#### Как работает

DiskANN использует алгоритм **Vamana** для построения графа:
1. Граф и полные векторы хранятся на SSD
2. В памяти только квантизованные embeddings для первичного поиска
3. Точные расстояния вычисляются по запросу с SSD

**Результаты:**
- Индексирует 5-10x больше точек на машину чем DRAM-based решения
- 1 миллиард векторов с 95% accuracy при 5ms latency
- Требует 15-50x меньше RAM чем HNSW
- Latency ~10-20ms на NVMe SSD (приемлемо для многих use cases)

**Применение:**
- Огромные датасеты с бюджетными ограничениями
- Когда HNSW слишком дорог по памяти
- Single-node deployments с миллиардами векторов

---

## Метрики расстояния

Выбор метрики расстояния критически важен -- она должна соответствовать той, что использовалась при обучении embedding модели.

### Cosine Similarity

**Что измеряет:** Угол между двумя векторами, игнорируя их длину.

**Когда использовать:**
- **Текстовые данные и NLP** -- стандарт для similarity
- Когда важно направление, а не магнитуда
- Сравнение документов разной длины

**Пример:** all-MiniLM-L6-v2 обучена с cosine similarity -- используйте её же для индекса.

### Dot Product (Inner Product)

**Что измеряет:** И направление, и магнитуду векторов.

**Когда использовать:**
- Многие LLM обучены с dot product (например, msmarco-bert-base-dot-v5)
- Рекомендательные системы, где магнитуда = популярность/качество
- Когда один продукт с тем же направлением, но большей магнитудой, "лучше"

**Важно:** Если данные нормализованы, cosine и dot product эквивалентны.

### Euclidean Distance

**Что измеряет:** Абсолютное расстояние между точками в пространстве.

**Когда использовать:**
- Модели без специфической loss function
- LSH (Locality Sensitive Hashing) методы
- K-Means кластеризация
- Anomaly detection -- ловим точки на большом расстоянии
- Когда магнитуда несет информацию о counts/measures

### Практическая рекомендация

```python
# Правило: match metric to training
distance_map = {
    "text-embedding-3-small": "cosine",
    "text-embedding-3-large": "cosine",
    "msmarco-bert-base-dot-v5": "dot",
    "all-MiniLM-L6-v2": "cosine",
    "cohere-embed-v3": "cosine",
}
```

---

## Обзор баз данных 2025

Теперь, когда мы понимаем алгоритмы, давай посмотрим на конкретные базы данных с реальными benchmarks.

### Pinecone: "Просто работает"

#### Архитектура Serverless (2024-2025)

Pinecone Serverless переосмыслил архитектуру vector database:
- **Compute-storage separation** -- эластичное масштабирование
- **Vector clustering на blob storage** для low-latency поиска
- **Multi-tenant compute layer** с usage-based billing
- **Поддержка миллионов namespaces** на индекс без потери производительности

Оптимизации для agentic workloads (2025):
- Adaptive indexing с log-structured merge trees
- Поддержка bursty, непредсказуемых query patterns

#### Ценообразование (2024)

| План | Стоимость | Включено |
|------|-----------|----------|
| Starter (free) | $0 | 2GB storage, 2M write units/mo, 1M read units/mo |
| Standard | $50/mo minimum | $6/M writes, $24/M reads |
| Serverless | Pay-as-you-go | $0.33/GB storage, $8.25/M reads, $2/M writes |
| Enterprise | Custom | Dedicated, compliance |

#### Для кого Pinecone

- Стартапы без DevOps
- Enterprise с бюджетом, где время важнее денег
- Production за неделю, а не за месяц

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

# Serverless -- масштабируется автоматически
pc.create_index(
    name="semantic-search",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

### Qdrant: мощь Rust для перфекционистов

#### Benchmark производительности

Согласно benchmark-ам 2024:
- **Highest RPS и lowest latencies** в большинстве сценариев
- **4x RPS gains** на некоторых датасетах
- **Sub-10ms p50** на 1M-scale датасетах
- SOC 2 Type II сертификация (2024)

#### Уникальные возможности

**Pre-filtering:** Фильтрация ВО ВРЕМЯ vector search, а не после. Критично для производительности с filtered queries.

**Quantization из коробки:** Scalar, binary, product -- выбирай под сценарий.

**Hybrid Cloud (2024):** Первый managed vector database, деплоящийся в любом окружении (on-prem, air-gapped).

#### Ценообразование

- Free 1GB cluster
- $0.014/hour hybrid cloud
- Custom private cloud pricing

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, Range

client = QdrantClient(host="localhost", port=6333)

# Pre-filtering -- фильтры применяются ДО vector search
results = client.search(
    collection_name="articles",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="published_date", range=Range(gte="2025-01-01")),
            FieldCondition(key="category", match={"value": "technology"})
        ]
    ),
    limit=10
)
```

### Weaviate: лучший Hybrid Search

#### Уникальная архитектура

Weaviate сочетает vector search, object storage и inverted index:
- **Нативный hybrid search** -- не добавлен позже, а заложен с начала
- **BM25F** -- взвешенный BM25 для множественных полей
- **GraphQL API** -- мощный и гибкий
- **Модульные vectorizers** -- OpenAI, Cohere, local models

#### Fusion Algorithms

**Relative Score Fusion** (default from v1.24):
- Нормализует scores от обоих поисков
- Highest = 1, lowest = 0, остальные пропорционально

**Ranked Fusion** (RRF):
- Ранг-based scoring
- Менее чувствителен к абсолютным значениям

#### Alpha Parameter

```python
# alpha = 0: только BM25
# alpha = 0.5: баланс
# alpha = 1: только vector

result = client.query.get("Document", ["content"])\
    .with_hybrid(query="machine learning", alpha=0.5)\
    .with_limit(10).do()
```

#### Scalability

- **50,000+ active tenants** per node
- **1 million tenants** на 20-node кластере
- GDPR-compliant deletes через tenant isolation

### Milvus: GPU-ускорение для миллиардов

#### GPU Acceleration (2024)

Milvus 2.4 с NVIDIA CAGRA (RAPIDS cuVS):
- **До 50x быстрее** чем CPU-based HNSW
- **21x speedup** для index building vs CPU
- **Index building:** 56 минут на 8 DGX H100 vs ~6.22 дней на CPU

#### GPU Index Types

- **GPU_CAGRA:** Graph-based, оптимизирован для GPU
- **GPU_IVF_FLAT:** Partition-based для GPU
- **GPU_BRUTE_FORCE:** Гарантированный recall = 1

#### Когда GPU имеет смысл

GPU vector search не всегда снижает latency:
- Нужен **высокий QPS** (сотни-тысячи) для полного использования параллелизма
- GPU memory меньше CPU RAM и дороже
- Лучше для batch processing и high-throughput

### ChromaDB: быстрый прототип

#### Возможности и ограничения

**Подходит для:**
- RAG прототипов
- Рекомендательных систем (PoC)
- Обучения и экспериментов
- До ~10-50 миллионов embeddings

**Ограничения:**
- Single-node -- не масштабируется бесконечно
- HNSW index в RAM -- memory-hungry
- Только один поток может читать/писать в индекс
- Library mode имеет проблемы с Gunicorn workers

```python
import chromadb

client = chromadb.Client()  # In-memory
collection = client.create_collection("my_collection")

collection.add(
    documents=["Doc about ML", "Doc about DBs"],
    ids=["doc1", "doc2"]
)
```

### Сравнительная таблица 2025

| Критерий | Pinecone | Qdrant | Weaviate | Milvus | Chroma | pgvector |
|----------|----------|--------|----------|--------|--------|----------|
| **Open Source** | Нет | Да | Да | Да | Да | Да |
| **Сложность старта** | Легко | Средне | Средне | Сложно | Легко | Легко |
| **Self-hosting** | Нет | Да | Да | Да | Да | Да |
| **Масштаб** | Миллиарды | Сотни M | Сотни M | Миллиарды | Десятки M | 50-100M |
| **Latency (p50, 1M)** | <20ms | <10ms | 20-50ms | <10ms | 10-50ms | 10-50ms |
| **GPU Support** | Нет | Нет | Нет | Да | Нет | Нет |
| **Hybrid Search** | Да | Да | Лучший | Да | Нет | Ограничен |
| **Фильтрация** | Post | Pre | Post | Pre | Базовая | SQL |
| **Compliance** | SOC2/HIPAA | SOC2 | SOC2/HIPAA | - | - | - |

---

## pgvector

### Когда PostgreSQL достаточно

Особая ситуация: ты уже используешь PostgreSQL. Настроены бэкапы, репликация, мониторинг. Команда знает psql.

**pgvector** -- расширение PostgreSQL, добавляющее vector search в существующую базу.

### Почему это часто лучший выбор

**Всё в одном месте:**

```sql
-- Найди похожие документы И покажи автора
SELECT d.content, u.name as author,
       1 - (d.embedding <=> query_embedding) AS similarity
FROM documents d
JOIN users u ON d.author_id = u.id
ORDER BY d.embedding <=> query_embedding
LIMIT 10;
```

С Pinecone понадобится два запроса и объединение на стороне приложения.

**ACID транзакции:** Добавление документа и embedding -- атомарная операция.

**Знакомые инструменты:** psql, pgAdmin, DBeaver, Datagrip, существующий мониторинг.

### pgvector 0.8.0 (Ноябрь 2024): Major Update

**Iterative Index Scans** -- главная новинка:
- Решает проблему "overfiltering" -- когда фильтры возвращают меньше результатов чем ожидалось
- Включается через `hnsw.iterative_scan` и `ivfflat.iterative_scan`
- Два режима: relaxed_order и strict_order

**Производительность:**
- **До 5.7x улучшение** для специфичных query patterns vs 0.7.4
- **До 9x быстрее** на Aurora PostgreSQL
- **100x более релевантные результаты** в filtered queries
- E-commerce запросы: 120ms -> 70ms

**pgvector 0.7.0 (Апрель 2024):**
- **halfvec:** 2-byte floats (до 4000 dimensions)
- **sparsevec:** до 1000 nonzero dimensions
- **bit vectors:** до 64000 dimensions
- **Parallel HNSW build**
- **binary_quantize** функция

```sql
-- Установка
CREATE EXTENSION IF NOT EXISTS vector;

-- Таблица с embeddings
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB
);

-- HNSW индекс
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Iterative scan для лучших filtered results (0.8.0)
SET hnsw.iterative_scan = relaxed_order;
```

### pgvector vs Pinecone Benchmark (2024)

На 50M Cohere embeddings (ANN-benchmarks fork):
- **28x lower p95 latency** с pgvector + pgvectorscale
- **16x higher throughput** at 99% recall
- Comparison was at storage-optimized tier

### Когда pgvector не хватит

- **> 50-100M векторов** -- PostgreSQL не был создан для такого масштаба
- **Distributed cluster** -- pgvector на одном сервере
- **Hybrid search критичен** -- менее элегантно чем Weaviate

---

## Hybrid Search

### Почему одного vector search недостаточно

Ты построил RAG-систему. Работает отлично -- до запроса "SKU-12345".

**Vector search** понимает смысл, но "SKU-12345" -- точный идентификатор. Vector search может вернуть другие SKU, "похожие по контексту".

**Другой пример:** "Найди документы про Иванова" -- vector search может вернуть Петрова (оба русские фамилии, семантически похожи).

### Решение: Hybrid Search = Vector + BM25

**BM25** -- улучшенный TF-IDF с нормализацией по длине документа. Находит точные совпадения.

**Vector Search** -- понимает семантику и контекст.

Вместе покрывают оба сценария.

### Архитектура Hybrid Search

1. Получаем запрос
2. Параллельно выполняем vector search и BM25
3. Объединяем через fusion algorithm (RRF)
4. (Опционально) reranking для финальной сортировки
5. Возвращаем top-k

### Reciprocal Rank Fusion (RRF)

Самый популярный алгоритм объединения. Важен ранг, а не абсолютный score.

```python
def reciprocal_rank_fusion(results_lists: list, k: int = 60) -> list:
    """
    Формула: score(doc) = sum(1 / (k + rank_in_list))
    k=60 -- стандартное значение, сглаживает разницу между рангами.
    """
    doc_scores = {}
    for results in results_lists:
        for rank, (doc_id, _) in enumerate(results, start=1):
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
            doc_scores[doc_id] += 1 / (k + rank)
    return sorted(doc_scores.items(), key=lambda x: -x[1])

# doc2 высоко в ОБОИХ списках -> будет первым
```

**Почему RRF лучше усреднения scores?** Scores из разных систем несопоставимы. BM25 score 0.8 и vector similarity 0.8 -- разные вещи. Ранги сравнивать можно.

### Alpha Parameter

- `alpha = 0` -- только BM25
- `alpha = 0.5` -- баланс (default)
- `alpha = 1` -- только vector

**Рекомендации:**
- **Технические документы с кодами:** alpha = 0.3-0.4
- **Художественные тексты:** alpha = 0.7-0.8
- **Универсальный:** alpha = 0.5
- Тестируйте на своих данных!

### Практическая реализация

```python
# Weighted score combination
# FinalScore = (VectorScore * 0.5) + (KeywordScore * 0.3) + (RecencyScore * 0.2)

def hybrid_search(query: str, weights: dict = None):
    weights = weights or {"vector": 0.5, "keyword": 0.3, "recency": 0.2}

    vector_results = vector_search(query)
    bm25_results = keyword_search(query)

    # Normalize scores to 0-1
    vector_scores = normalize(vector_results)
    bm25_scores = normalize(bm25_results)

    # Combine
    combined = {}
    for doc_id, score in vector_scores.items():
        combined[doc_id] = score * weights["vector"]
    for doc_id, score in bm25_scores.items():
        combined[doc_id] = combined.get(doc_id, 0) + score * weights["keyword"]

    return sorted(combined.items(), key=lambda x: -x[1])
```

---

## Reranking

### Зачем нужен Reranking

Даже после hybrid search результаты можно улучшить. **Cross-Encoder Reranker** смотрит на каждую пару (query, document) и оценивает релевантность.

### Bi-Encoder vs Cross-Encoder

**Bi-Encoder (embedding models):**
- Быстрый, scalable
- Query и document кодируются отдельно
- Менее точный

**Cross-Encoder:**
- Медленный, не scalable для всего корпуса
- Query и document обрабатываются вместе через transformer
- Более точный (attention across query and document)

**Решение:** Bi-Encoder для retrieval top-100, Cross-Encoder для rerank top-10.

### Production Reranking

```python
import cohere

co = cohere.Client("YOUR_API_KEY")

def rerank(query: str, documents: list[str], top_n: int = 5):
    """
    На практике поднимает precision на 5-15%.
    """
    results = co.rerank(
        query=query,
        documents=documents,
        model="rerank-english-v3.0",
        top_n=top_n
    )
    return [(r.document.text, r.relevance_score) for r in results.results]
```

### Рекомендуемые модели

Из MTEB Leaderboard (reranking task):
- **BAAI/bge-reranker-large** (278M params) -- высокое качество
- **Xenova/ms-marco-MiniLM-L-6-v2** -- легковесный
- **Cohere rerank-v3.0** -- managed API

### Cross-Encoders vs LLM-based Rerankers

Исследование 2024 показало: cross-encoders остаются конкурентоспособными с LLM-based rerankers при значительно меньших затратах на inference.

### Latency Considerations

Cross-encoder inference для 100 документов может занять заметное время. Рекомендации:
- Держите reranking window небольшим (10-50 документов)
- Кэшируйте популярные queries
- Рассмотрите async reranking для UX

---

## Embedding Models

### Как выбрать модель

**MTEB Leaderboard** -- ключевой ресурс:
- 58 datasets, 112 языков
- Фильтры по task (retrieval, classification, clustering)
- Фильтры по языку и домену

### Ключевые параметры

**Embedding Dimensions:**
- Больше != всегда лучше
- Большие dimensions захватывают больше нюансов
- Меньшие -- быстрее inference, меньше storage
- Баланс: 768-1536 для большинства cases

**Max Tokens:**
- Предел текста для одного embedding
- RAG chunks обычно 200-500 tokens
- 512 tokens достаточно для большинства cases
- Есть модели с 8192+ tokens для длинных документов

### OpenAI Models Comparison

| Модель | Dimensions | MTEB Avg | MIRACL | Цена/1M tokens |
|--------|------------|----------|--------|----------------|
| text-embedding-ada-002 | 1536 | 61.0% | 31.4% | Устаревшая |
| text-embedding-3-small | 1536 | 62.3% | 44.0% | $0.02 |
| text-embedding-3-large | 3072 | 64.6% | 54.9% | $0.13 |

**text-embedding-3-large ключевые преимущества:**
- Matryoshka Representation Learning -- можно truncate dimensions
- 256-dimensional version превосходит полный ada-002!
- Лучшая multilingual производительность

### OpenAI vs Cohere

| Аспект | OpenAI 3-large | Cohere Embed v3 |
|--------|----------------|-----------------|
| **Accuracy (nDCG@10)** | 0.811 | 0.686-0.781 |
| **Цена/1M tokens** | $1.30 | $0.50 (1024d) |
| **Storage cost** | 4x больше | Меньше |
| **Typo tolerance** | Высокая | Ниже |
| **Multilingual** | Хорошая | 100+ языков |

**Рекомендации:**
- **Cohere** -- для multilingual, budget-conscious, open-domain RAG
- **OpenAI 3-large** -- для semantic search, classification, когда нужна максимальная точность

### Важно: Upgradability

При смене embedding модели нужно **переиндексировать все данные**. Проектируйте систему с этим учетом!

---

## Chunking Strategies

### Почему Chunking критичен

**Chunking -- arguably самый важный фактор для RAG performance.** Плохие chunks = плохой retrieval, даже с идеальным retriever.

**Две причины chunking:**
1. Embedding models имеют context windows -- excess tokens truncated
2. Chunks должны содержать информацию, достаточную для search

### Размер Chunk

> "Если размер embeddings wildly отличается от размера query, получите lower similarity score."

Рекомендуемые размеры:
- **200-500 tokens** для большинства RAG
- **Overlap 50-100 tokens** для сохранения контекста

### Основные стратегии

#### 1. Fixed-Size Chunking
```python
# Простой, но грубый подход
chunks = [text[i:i+500] for i in range(0, len(text), 500)]
```
**Плюсы:** Простота, consistent sizes
**Минусы:** Разрывает предложения/параграфы, теряет семантику

#### 2. Recursive Chunking (LangChain style)
1. Сначала по параграфам/секциям
2. Если chunk > limit, split дальше по предложениям
3. Если всё ещё > limit, split по словам

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "]
)
```

#### 3. Semantic Chunking
- Split по semantic boundaries
- Merge consecutive similar segments
- Более coherent chunks

#### 4. LLM-Based Chunking
- LLM решает где split
- Может добавлять context/summaries
- Самый мощный, но дорогой

### Contextual Retrieval (Anthropic, 2024)

Anthropic представила новый подход:
1. Промптим Claude с полным документом + chunk
2. Claude генерирует contextualized description
3. Description prepends к chunk перед embedding
4. Сохраняет high-level meaning в каждом chunk

**Оптимизация:** Document cached в prompt для всех chunks.

### Pre-Chunking vs Post-Chunking

**Pre-Chunking (стандарт):**
- Chunks создаются заранее
- Быстрый retrieval
- Требует upfront решений о размере

**Post-Chunking:**
- Embedding целых документов
- Chunking at query time для retrieved docs
- Caching делает быстрее со временем

### Практические советы

1. **Match chunk size to embedding model training** -- если модель обучена на параграфах, используйте параграфы
2. **Сохраняйте metadata** -- link на оригинал, категории, timestamps
3. **Test different strategies** на своих данных
4. **Consider domain** -- код vs проза требуют разных подходов

---

## Multi-tenancy

### Зачем нужна изоляция

Multi-tenancy -- архитектура где один instance обслуживает множество customers с изоляцией данных.

**Требования:**
- Data privacy между tenants
- Performance isolation (no noisy neighbors)
- GDPR compliance (right to be forgotten)

### Стратегии изоляции

#### 1. Namespace/Partition Level (рекомендуется)

```python
# Pinecone namespaces
index.upsert(vectors=vectors, namespace="tenant_123")
index.query(vector=query, namespace="tenant_123", top_k=10)
```

**Плюсы:** Простота, эффективность, хорошая изоляция
**Минусы:** Нельзя query across tenants

#### 2. Metadata Filtering

```python
# Filter by tenant_id
results = client.search(
    collection="shared",
    query_vector=query,
    filter={"tenant_id": "tenant_123"}
)
```

**Плюсы:** Flexibility, cross-tenant queries possible
**Минусы:** Меньшая изоляция, потенциальные performance issues

#### 3. Database/Collection Level

Каждый tenant имеет отдельную database/collection.

**Плюсы:** Максимальная изоляция
**Минусы:** Resource overhead, scalability limits

### Platform-Specific Implementations

**Weaviate:** Данные хранятся per-tenant отдельно
- Быстрые deletes (GDPR compliance)
- Dedicated high-performance index per tenant
- 50,000+ active tenants per node

**Milvus:** Database, collection, и partition-level strategies

**Pinecone:** Namespaces -- стандартный подход

### Best Practices

1. **Design namespace architecture** -- isolated namespaces per tenant
2. **Implement RBAC** -- access controls per tenant
3. **Monitor per-tenant metrics** -- latency, error rates
4. **Balance isolation vs efficiency** -- strict SLAs may need dedicated resources

---

## Production Best Practices

### Indexing & Query Optimization

1. **Choose index type wisely:**
   - HNSW для high-recall, dynamic data
   - IVF для batch updates, memory constraints
   - PQ/BQ для memory optimization

2. **Batch operations:**
   - Reduce network overhead
   - Bulk inserts более эффективны

3. **Metadata filtering:**
   - Filter FIRST, then vector search
   - Сужает search space

### RAG Pipeline Best Practices

1. **Hybrid retrieval:**
   - Vector + BM25 (или SPLADE)
   - RRF fusion

2. **Smart chunking:**
   - 200-500 tokens с overlap
   - Preserve semantic boundaries

3. **Re-ranking:**
   - Cross-encoder для top-k
   - 5-15% precision improvement

### Scalability

1. **Horizontal scaling:**
   - Sharding by user_id, region, или hash
   - Добавление nodes для большего throughput

2. **Vector compression:**
   - Scalar quantization: 4x compression
   - Binary quantization: 32x compression
   - Product quantization: до 64x

3. **Caching:**
   - Semantic caching для similar queries
   - Embedding cache для frequent inputs

### Monitoring

**Key metrics:**
- Query latency (p50, p95, p99)
- Recall@k
- Index size и memory usage
- QPS и throughput

**Tools:** Prometheus, Grafana, LangSmith, Phoenix

### Security

1. **Encryption** at rest and in transit
2. **RBAC** для tenant isolation
3. **Audit logs**
4. **PII detection** в embeddings pipeline

### Cost Optimization

1. **Right-size dimensions:**
   - 768d vs 1536d может быть достаточно
   - Matryoshka embeddings для flexibility

2. **Quantization:**
   - Scalar: минимальная потеря recall
   - Binary: 32x memory reduction

3. **Tiered storage:**
   - Hot data в RAM
   - Cold data на SSD (DiskANN)

---

## Практические истории

### История 1: Стартап строит AI-ассистента

**Ситуация:** 4 человека делают SaaS для юристов. Нужен чат-бот на основе документов.

**Решение:** Chroma для PoC -> Pinecone для production.

**Почему:** Zero ops, время важнее денег на старте. $100/месяц -- ничто vs время разработчика.

### История 2: E-commerce с миллионами товаров

**Ситуация:** 10M товаров, поиск за 50ms, сложная фильтрация, self-hosting.

**Решение:** Qdrant self-hosted.

**Почему:** Pre-filtering во время vector search, Rust даёт стабильную latency, open source.

```python
results = client.search(
    collection_name="products",
    query_vector=get_embedding("красное платье на выпускной"),
    query_filter=Filter(
        must=[
            FieldCondition(key="category", match=MatchValue(value="dresses")),
            FieldCondition(key="price", range=Range(lte=10000)),
            FieldCondition(key="in_stock", match=MatchValue(value=True))
        ]
    ),
    limit=20
)
```

### История 3: Enterprise Knowledge Base

**Ситуация:** 50,000 сотрудников, документация разбросана, нужен точный И смысловой поиск.

**Решение:** Weaviate с hybrid search.

**Почему:** Лучший hybrid search, BM25 для "документ 12345", vector для "как настроить VPN".

### История 4: PostgreSQL уже есть

**Ситуация:** Средний SaaS, PostgreSQL работает, нужен умный поиск по 500K статей.

**Решение:** pgvector.

**Почему:** Один запрос с JOIN, существующая инфраструктура, ACID гарантии.

```sql
SELECT a.title, a.content, u.name as author,
       1 - (a.embedding <=> $1) as similarity
FROM articles a
JOIN users u ON a.author_id = u.id
WHERE a.published = true
ORDER BY a.embedding <=> $1
LIMIT 10;
```

---

## Как выбрать базу данных

### Decision Tree

#### Шаг 1: Определи масштаб

**< 1M векторов:**
- PostgreSQL + pgvector (если уже используете)
- Chroma (прототип)
- Qdrant Cloud / Pinecone (managed)

**1-100M векторов:**
- Qdrant или Weaviate
- Pinecone (если бюджет позволяет)

**> 100M векторов:**
- Milvus (с data engineering экспертизой)
- Pinecone Enterprise
- DiskANN-based solutions

#### Шаг 2: Операционные возможности

**Нет DevOps:**
- Pinecone (дорого, zero ops)
- Qdrant Cloud (дешевле)

**Есть DevOps, готовы self-host:**
- Qdrant (оптимальный баланс)
- Weaviate (GraphQL, hybrid search)
- Milvus (огромный масштаб)

#### Шаг 3: Специальные требования

| Требование | Рекомендация |
|------------|--------------|
| Уже на PostgreSQL | pgvector |
| Лучший hybrid search | Weaviate |
| Мощная фильтрация | Qdrant |
| GPU acceleration | Milvus |
| Edge/IoT | Qdrant (маленький binary) |
| Billions on SSD | DiskANN / pgvectorscale |

### Сводная рекомендация

| Сценарий | Рекомендация | Причина |
|----------|--------------|---------|
| Стартап, MVP | Chroma -> Pinecone | Быстро начать |
| Enterprise SaaS | Pinecone | SLA, compliance |
| Self-hosted < 50M | Qdrant | Performance/cost |
| Self-hosted > 1B | Milvus | Проверен на масштабе |
| Уже на PostgreSQL | pgvector | Минимум изменений |
| Hybrid search важен | Weaviate | Лучшая реализация |
| Budget + Billions | DiskANN | SSD-based |

---

## Актуальность 2024-2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **pgvector 0.8.0** | ✅ Production | Iterative scans, 5.7x improvement, 28x lower p95 vs Pinecone |
| **Qdrant Hybrid Cloud** | 🔥 Industry first | SOC 2 Type II, deploy anywhere (on-prem, air-gapped) |
| **Pinecone Serverless** | ✅ GA | Multi-tenant compute, pay-as-you-go, миллионы namespaces |
| **Weaviate v1.30** | ✅ New | Native generative module, HIPAA compliance (AWS) |
| **Milvus GPU (CAGRA)** | 🆕 Performance | До 50x быстрее CPU HNSW, 21x speedup index building |
| **Binary Quantization** | ✅ Mainstream | 32x memory reduction, 96% recall with rescoring |
| **DiskANN/pgvectorscale** | 🔥 Cost-effective | Billions на SSD, 75% cheaper vs managed services |

### Market & GitHub (2025)

| Database | GitHub Stars | Docker Pulls/mo | Key Strength |
|----------|--------------|-----------------|--------------|
| **Milvus** | ~35k | ~700k | Billion-scale, GPU |
| **Qdrant** | ~9k | — | Performance, Rust, filtering |
| **Weaviate** | ~8k | >1M | Best hybrid search |
| **Chroma** | ~6k | — | Simplest prototyping |
| **pgvector** | ~4k | — | PostgreSQL ecosystem |

### Community Sentiment (Reddit, HN)

**Что хвалят:**
- pgvector: "75% дешевле Pinecone, benchmarks говорят сами"
- Qdrant: "Rust performance + pre-filtering — killer combo"
- Reddit выбрала Milvus для 1B+ scale после тестов Qdrant и Milvus

**Что критикуют:**
- Pinecone: "отличный, но дорогой для scale"
- Weaviate: "requires more memory at very large scale"
- Chroma: "single-node limits, not for billions"

**Общий консенсус:**
> "Most RAG failures are self-inflicted, not database-inflicted" — focus на chunking и embedding quality

### Pricing Comparison 2025

| Database | Free Tier | 1M vectors estimate |
|----------|-----------|---------------------|
| **Pinecone** | 2GB, 2M writes/mo | ~$41-89/mo |
| **Qdrant Cloud** | 1GB forever | ~$102/mo (AWS) |
| **Zilliz (Milvus)** | 5GB | ~$89-114/mo |
| **pgvector** | Self-hosted | Infrastructure only |
| **Weaviate** | 2 weeks trial | Paid after |

## Заключение

Vector databases -- фундаментальный инструмент для работы с AI. Ключевые takeaways:

1. **HNSW** -- стандарт для большинства случаев
2. **Hybrid search** (vector + BM25) значительно улучшает качество
3. **Quantization** (scalar, binary, PQ) экономит память
4. **DiskANN** делает billions доступными на SSD
5. **pgvector** часто достаточно для существующих PostgreSQL deployments
6. **Chunking** критичен для RAG performance

Начни с простого (Chroma или pgvector), построй прототип, пойми свои требования -- и только потом думай о "настоящей" vector database.

---

## Связанные материалы

- [[embeddings-complete-guide]] -- Как создавать embeddings
- [[rag-advanced-techniques]] -- Продвинутые RAG стратегии
- [[llm-fundamentals]] -- Основы LLM

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Pinecone: HNSW Explained](https://www.pinecone.io/learn/series/faiss/hnsw/) | Guide | HNSW алгоритм, параметры |
| 2 | [OpenSearch: HNSW Hyperparameters](https://opensearch.org/blog/a-practical-guide-to-selecting-hnsw-hyperparameters/) | Guide | M, ef настройка |
| 3 | [Microsoft DiskANN](https://www.microsoft.com/en-us/research/project/project-akupara-approximate-nearest-neighbor-search-for-large-scale-semantic-search/) | Research | Billion-scale на SSD |
| 4 | [Qdrant Benchmarks 2024](https://qdrant.tech/benchmarks/) | Benchmark | QPS, latency сравнения |
### Теоретические основы
- Malkov, Yu. & Yashunin, D. (2018). *Efficient and Robust Approximate Nearest Neighbor using Hierarchical Navigable Small World Graphs*. IEEE TPAMI. arXiv:1603.09320.
- Jégou, H., Douze, M. & Schmid, C. (2011). *Product Quantization for Nearest Neighbor Search*. IEEE TPAMI.
- Subramanya, S. et al. (2019). *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node*. NeurIPS. Microsoft Research.
- Guo, R. et al. (2020). *Accelerating Large-Scale Inference with Anisotropic Vector Quantization* (ScaNN). ICML. Google.
- Gionis, A., Indyk, P. & Motwani, R. (1999). *Similarity Search in High Dimensions via Hashing*. VLDB.

### Практические руководства
- [Weaviate Hybrid Search](https://weaviate.io/blog/hybrid-search-explained)
- [Qdrant vs Pinecone](https://qdrant.tech/blog/comparing-qdrant-vs-pinecone-vector-databases/)
- [pgvector 0.8.0](https://www.postgresql.org/about/news/pgvector-080-released-2952/)
- [Chunking Strategies — Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Best Vector Databases 2025](https://www.firecrawl.dev/blog/best-vector-databases-2025)

---

*Последнее обновление: 2024-12-28*

---

[[ai-engineering-moc|← AI Engineering MOC]] | [[embeddings-complete-guide|← Embeddings]] | [[rag-advanced-techniques|RAG Advanced →]]

---

## Связь с другими темами

**[[embeddings-complete-guide]]** — Эмбеддинги и векторные базы данных неразрывно связаны: эмбеддинги преобразуют текст, изображения и другие данные в числовые векторы, а векторные БД обеспечивают их эффективное хранение и поиск. Выбор модели эмбеддингов определяет размерность векторов и качество семантического сходства, что напрямую влияет на выбор индекса (HNSW, IVF) и настройку параметров векторной БД.

**[[rag-advanced-techniques]]** — Векторные базы данных являются инфраструктурным слоем для RAG-пайплайнов. Продвинутые RAG-техники (hybrid search, multi-index routing, hierarchical retrieval) требуют специфических возможностей от векторной БД: поддержка sparse+dense поиска, фильтрация по метаданным, namespace-изоляция. Понимание внутреннего устройства векторных БД позволяет оптимизировать retrieval-этап RAG.

**[[aiml-databases-complete]]** — Полное руководство по базам данных для AI/ML расширяет тему векторных БД в контекст всей инфраструктуры данных. Векторные БД часто работают в связке с реляционными (метаданные, аналитика) и документными (хранение исходных текстов) базами. Выбор архитектуры хранения данных — интегрированная векторная поддержка (pgvector) vs специализированная векторная БД — зависит от масштаба и требований проекта.

---

## Проверь себя

> [!question]- Почему HNSW стал стандартом для ANN-поиска в vector databases вместо IVF или brute-force?
> HNSW (Hierarchical Navigable Small World) обеспечивает субмиллисекундный поиск через иерархический граф: верхние уровни для грубой навигации, нижние для точного поиска. Recall 95%+ при latency <50ms на миллионах векторов. IVF быстрее строится, но хуже на recall. Brute-force O(n) неприемлем для production.

> [!question]- У вас 50M документов, 1024-мерные embeddings, бюджет $500/месяц. Какую vector database выберете -- Pinecone, Qdrant или pgvector?
> Qdrant self-hosted: open-source, нет лицензионных затрат, высокая производительность, scalar quantization снижает RAM в 4x. Pinecone managed проще, но дороже на таком объеме. pgvector подойдет если уже есть PostgreSQL и объем <10M, но на 50M производительность значительно хуже специализированных решений.

> [!question]- Когда Hybrid Search (vector + BM25) критически необходим, а когда vector search достаточен?
> Hybrid критичен: доменная терминология (медицина, право), exact match важен (номера документов, коды), мультиязычные запросы. Vector search достаточен: общие вопросы на естественном языке, когда синонимы и перефразировки важнее точных терминов, RAG для general knowledge.

---

## Ключевые карточки

Что такое vector database и зачем нужна?
?
Специализированная БД для хранения embeddings (числовых представлений смысла) и быстрого поиска похожих векторов. Решает проблему семантического поиска: "автомобиль" находит "машина", "авто". Latency <50ms на миллионах векторов через ANN алгоритмы.

HNSW vs IVF vs DiskANN?
?
HNSW: иерархический граф, лучший recall (95%+), стандарт для in-memory. IVF: кластеризация, быстрое построение, хуже recall. DiskANN: работает с SSD, для масштабов >100M при ограниченной RAM. PQ (Product Quantization): сжатие векторов для экономии памяти.

Какие основные vector databases в 2025?
?
Pinecone: managed, простой старт. Qdrant: open-source, высокая производительность. Weaviate: модульный, GraphQL. Chroma: embedded, для прототипов. pgvector: PostgreSQL extension. Milvus: enterprise-scale. Выбор зависит от масштаба, бюджета, managed vs self-hosted.

Что такое metadata filtering и зачем?
?
Фильтрация результатов vector search по структурированным метаданным (дата, автор, категория, язык). Пример: "найди похожие документы, но только за 2024 год от отдела HR". Критично для multi-tenant приложений и fine-grained control над результатами.

Как выбрать между managed и self-hosted vector DB?
?
Managed (Pinecone, Weaviate Cloud): быстрый старт, auto-scaling, нет DevOps. Self-hosted (Qdrant, Milvus): полный контроль, data privacy, экономия на масштабе. Правило: прототип на managed, production >10M vectors -- рассмотреть self-hosted.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[rag-advanced-techniques]] | Как использовать vector DB в RAG pipeline -- от chunking до evaluation |
| Углубиться | [[aiml-databases-complete]] | Vector DB в контексте всей экосистемы баз данных для AI |
| Смежная тема | [[databases-fundamentals-complete]] | Фундаменты БД: индексы, B-tree, hash -- для сравнения с ANN |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте раздела AI Engineering |

*Проверено: 2026-01-09*
