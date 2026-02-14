---
title: "AI/ML Databases: Vector Databases & Embeddings"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/intermediate
related:
  - "[[vector-databases-guide]]"
  - "[[embeddings-complete-guide]]"
  - "[[nosql-databases-complete]]"
modified: 2026-02-13
prerequisites:
  - "[[nosql-databases-complete]]"
reading_time: 24
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AI/ML Databases: Vector Databases & Embeddings

> Полный гайд по vector databases для RAG, semantic search и AI-приложений

**Уровень:** Advanced
**Время чтения:** 45 минут
**Последнее обновление:** 2025-12-30

---

## Prerequisites

| Тема            | Зачем нужно                                 | Где изучить                         |
| --------------- | ------------------------------------------- | ----------------------------------- |
| **Embeddings**  | Понимание что такое векторные представления | [[embeddings-complete-guide]]       |
| **LLM basics**  | Что такое GPT, RAG, промпты                 | [[llm-fundamentals]]                |
| **Python**      | Код примеры на Python                       | [[python-basics]]                   |
| **Базы данных** | Понимание индексов, запросов                | [[databases-fundamentals-complete]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **ML Engineer** | Выбор vector DB, chunking strategies, production deployment |
| **Backend разработчик** | Интеграция vector search в приложение |
| **AI Architect** | Сравнение решений, hybrid search, масштабирование |

---

## Терминология

> 💡 **Главная аналогия:**
>
> **Vector Database** = библиотека, где книги стоят **по смыслу**, а не по алфавиту. "Найди похожее на эту книгу" работает мгновенно, потому что похожие книги рядом.

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Vector/Embedding** | Числовое представление текста/изображения | **GPS-координаты смысла** — где находится в пространстве значений |
| **Similarity Search** | Поиск ближайших векторов | **Найди книги рядом** — ближайшие = самые похожие |
| **ANN** | Approximate Nearest Neighbors | **Примерный поиск** — не 100% точный, но в 1000x быстрее |
| **HNSW** | Hierarchical Navigable Small World graph | **Карта метро** — быстрая навигация через связи |
| **IVF** | Inverted File Index | **Деление на районы** — сначала найди район, потом ищи в нём |
| **Cosine Similarity** | Мера похожести (угол между векторами) | **Угол между стрелками** — смотрят в одну сторону = похожи |
| **Dimension** | Размерность вектора (768, 1536, 3072) | **Количество характеристик** — больше = точнее, но дороже |
| **Chunking** | Разбиение документа на части | **Нарезка книги на главы** — каждая глава = отдельный вектор |
| **Hybrid Search** | Vector + keyword search | **Два библиотекаря** — один по смыслу, второй по словам |
| **Reranking** | Повторное ранжирование результатов | **Второе мнение** — эксперт пересматривает top-100 |
| **Quantization** | Сжатие векторов | **JPEG для чисел** — меньше места, чуть меньше точности |
| **Metadata Filtering** | Фильтрация по атрибутам | **Только книги 2024 года** — сначала фильтр, потом similarity |

---

## Содержание

1. [Введение в Vector Databases](#введение-в-vector-databases)
2. [Как работают Embeddings](#как-работают-embeddings)
3. [Алгоритмы поиска](#алгоритмы-поиска)
4. [Pinecone](#pinecone)
5. [Milvus](#milvus)
6. [Qdrant](#qdrant)
7. [Weaviate](#weaviate)
8. [Chroma](#chroma)
9. [FAISS](#faiss)
10. [pgvector](#pgvector)
11. [Chunking Strategies](#chunking-strategies)
12. [Hybrid Search](#hybrid-search)
13. [LangChain Integration](#langchain-integration)
14. [Security & Access Control](#security--access-control)
15. [Production Best Practices](#production-best-practices)
16. [Cost Analysis](#cost-analysis)
17. [Выбор решения](#выбор-решения)

---

## Введение в Vector Databases

### Что такое Vector Database?

Vector database — специализированное хранилище для **высокоразмерных векторов (embeddings)**, оптимизированное для similarity search.

```
Traditional DB:
┌─────────────┐
│ SELECT *    │ → Exact match
│ WHERE id=1  │
└─────────────┘

Vector DB:
┌─────────────────────┐
│ Find similar to     │ → Approximate nearest neighbors
│ [0.1, 0.3, ..., 0.8]│
└─────────────────────┘
```

### Зачем нужны Vector Databases?

```
┌──────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Documents → Chunks → Embeddings → Vector DB                 │
│                                        ↓                     │
│  Query → Embedding → Similarity Search → Context → LLM      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Use Cases:**
- **RAG (Retrieval-Augmented Generation):** Поиск релевантного контекста для LLM
- **Semantic Search:** Поиск по смыслу, не по ключевым словам
- **Recommendation Systems:** Похожие товары, контент
- **Image Search:** Поиск изображений по описанию или другому изображению
- **Anomaly Detection:** Поиск outliers в данных

### Рынок Vector Databases

```
Market Growth:
2024: $1.73B
2032: $10.6B (projected)

GitHub Stars (Dec 2025):
Milvus:    ████████████████████ 35,000+
Qdrant:    █████████ 9,000+
Weaviate:  ████████ 8,000+
Chroma:    ██████ 6,000+
```

---

## Как работают Embeddings

### Embedding = Vector Representation

```
Text: "The cat sat on the mat"
          ↓
    Embedding Model
          ↓
Vector: [0.12, -0.34, 0.56, ..., 0.78]
         └──────────────────────────┘
              1536 or 3072 dimensions
```

### Embedding Models Comparison

| Model | Dimensions | Quality | Speed | Cost |
|-------|------------|---------|-------|------|
| text-embedding-3-large | 3072 | Best | Slow | $$$ |
| text-embedding-3-small | 1536 | Good | Fast | $ |
| BGE-large-en | 1024 | Very Good | Medium | Free |
| all-MiniLM-L6-v2 | 384 | OK | Very Fast | Free |

### OpenAI Embeddings

```python
from openai import OpenAI

client = OpenAI()

# Create embedding
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here",
    dimensions=3072  # Can reduce: 256, 512, 1024, 1536
)

embedding = response.data[0].embedding
print(f"Dimensions: {len(embedding)}")  # 3072
```

**Matryoshka Representation:**
```python
# Full embedding
full = client.embeddings.create(
    model="text-embedding-3-large",
    input="text",
    dimensions=3072
)

# Truncated (still useful!)
small = client.embeddings.create(
    model="text-embedding-3-large",
    input="text",
    dimensions=512  # 6x less storage
)
```

### Sentence Transformers (Open Source)

```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings
sentences = ["This is a sentence", "Another sentence"]
embeddings = model.encode(sentences)

print(embeddings.shape)  # (2, 384)
```

### Similarity Metrics

```
Cosine Similarity:
cos(A, B) = (A · B) / (||A|| × ||B||)
Range: [-1, 1]
Best for: Text embeddings (normalized)

Dot Product:
A · B = Σ(ai × bi)
Range: unbounded
Best for: Pre-normalized vectors (OpenAI)

Euclidean Distance (L2):
√Σ(ai - bi)²
Range: [0, ∞)
Best for: Image embeddings, spatial data
```

**Python Example:**

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def dot_product(a, b):
    return np.dot(a, b)

def euclidean_distance(a, b):
    return np.linalg.norm(a - b)

# Compare
vec1 = np.array([0.1, 0.2, 0.3])
vec2 = np.array([0.15, 0.25, 0.35])

print(f"Cosine: {cosine_similarity(vec1, vec2):.4f}")  # ~0.9986
print(f"Dot:    {dot_product(vec1, vec2):.4f}")        # ~0.185
print(f"L2:     {euclidean_distance(vec1, vec2):.4f}")  # ~0.0866
```

---

## Алгоритмы поиска

### Почему не Brute Force?

```
Brute Force:
- Compare query to ALL vectors
- O(n × d) complexity
- 1M vectors × 1536 dims = 1.5B operations per query
- Too slow for production
```

### HNSW (Hierarchical Navigable Small World)

```
                    Layer 2 (sparse)
                    ○───────○
                   /         \
                  /           \
              Layer 1 (medium)
              ○───○───○───○
             /|   |   |   |\
            / |   |   |   | \
       Layer 0 (dense - all nodes)
       ○─○─○─○─○─○─○─○─○─○─○─○

Search: Start from top, navigate down
```

**Характеристики:**
- **Pros:** High recall (>99%), logarithmic complexity
- **Cons:** Memory-intensive, slow index build
- **Parameters:**
  - `M`: Connections per node (16-64)
  - `ef_construction`: Build quality (100-500)
  - `ef_search`: Search quality/speed trade-off

```python
# Qdrant HNSW config
from qdrant_client.models import HnswConfigDiff

collection_config = {
    "hnsw_config": HnswConfigDiff(
        m=16,                    # Connections per node
        ef_construct=100,        # Build quality
        full_scan_threshold=10000  # When to use brute force
    )
}
```

### IVF (Inverted File Index)

```
       Cluster 1    Cluster 2    Cluster 3
       ┌───────┐    ┌───────┐    ┌───────┐
       │ ○ ○ ○ │    │ ○ ○ ○ │    │ ○ ○ ○ │
       │ ○ ○   │    │ ○ ○ ○ │    │ ○ ○   │
       └───────┘    └───────┘    └───────┘
           ↑            ↑            ↑
           └────────────┼────────────┘
                        │
                  Query: Find nearest cluster(s)
                         then search within
```

**Характеристики:**
- **Pros:** Scalable, less memory than HNSW
- **Cons:** Lower recall, requires training
- **Parameters:**
  - `nlist`: Number of clusters (sqrt(n) to 4*sqrt(n))
  - `nprobe`: Clusters to search (1-nlist)

### Product Quantization (PQ)

```
Original vector: [0.12, 0.34, 0.56, 0.78, ...]  (1536 floats = 6KB)
                          ↓ Quantize
Compressed:      [code1, code2, code3, ...]     (192 bytes = 32x smaller)
```

**Trade-off:** 4-16x compression, slight accuracy loss

### Algorithm Selection

| Algorithm | Memory | Speed | Recall | Best For |
|-----------|--------|-------|--------|----------|
| HNSW | High | Fast | 99%+ | Production, quality-critical |
| IVF | Medium | Medium | 95%+ | Large datasets |
| IVF+PQ | Low | Medium | 90%+ | Billion-scale |
| DiskANN | Low | Medium | 95%+ | Larger than RAM |

---

## Pinecone

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                    PINECONE                                │
├────────────────────────────────────────────────────────────┤
│ Type:        Fully managed, cloud-native                   │
│ Architecture: Serverless (Jan 2024) or Pods               │
│ Best for:    Zero-ops production, fast time-to-market     │
│ Pricing:     Usage-based (storage + RU + WU)              │
└────────────────────────────────────────────────────────────┘
```

### Serverless vs Pods

| Aspect | Serverless | Pods |
|--------|------------|------|
| Scaling | Automatic | Manual |
| Pricing | Usage-based | Per-pod/minute |
| Cost at idle | Near zero | Pod baseline |
| Setup | Instant | Configure capacity |

**Recommendation:** Serverless for most new projects

### Quick Start

```python
from pinecone import Pinecone, ServerlessSpec

# Initialize
pc = Pinecone(api_key="YOUR_API_KEY")

# Create serverless index
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Connect
index = pc.Index("my-index")

# Upsert vectors
index.upsert(
    vectors=[
        {
            "id": "doc1",
            "values": [0.1, 0.2, ...],  # 1536 dims
            "metadata": {"title": "Document 1", "category": "tech"}
        }
    ]
)

# Query
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    include_metadata=True,
    filter={"category": {"$eq": "tech"}}
)
```

### Pricing (Dec 2025)

```
Serverless:
├── Storage:     $0.33/GB/month
├── Read Units:  $8.25/million
├── Write Units: $2.00/million
└── Free:        $100 credits to start

Pods:
├── Starter:     $0.00 (1 pod, limited)
├── Standard:    $0.0833/hour/pod
└── Enterprise:  Custom pricing
```

---

## Milvus

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                      MILVUS                                │
├────────────────────────────────────────────────────────────┤
│ Type:        Open-source, distributed                      │
│ Architecture: Cloud-native, compute/storage separation    │
│ Best for:    Billion-scale, GPU acceleration, full control│
│ Managed:     Zilliz Cloud                                 │
└────────────────────────────────────────────────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Milvus Cluster                          │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Proxy      │   Query Node │   Data Node  │   Index Node  │
│   (routing)  │   (search)   │   (storage)  │   (indexing)  │
└──────┬───────┴──────────────┴──────┬───────┴───────────────┘
       │                              │
       ▼                              ▼
┌──────────────┐              ┌───────────────┐
│  etcd        │              │  MinIO/S3     │
│  (metadata)  │              │  (storage)    │
└──────────────┘              └───────────────┘
```

### Index Types

| Index | Type | GPU | Best For |
|-------|------|-----|----------|
| FLAT | Brute force | No | <10K vectors |
| IVF_FLAT | Clustering | No | General use |
| IVF_SQ8 | Quantized | No | Memory-constrained |
| IVF_PQ | Compressed | No | Billion-scale |
| HNSW | Graph | No | High recall |
| GPU_IVF_FLAT | GPU | Yes | Fast ingestion |
| GPU_IVF_PQ | GPU | Yes | Large + fast |
| DiskANN | SSD | No | Larger than RAM |

### Quick Start

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Connect
connections.connect("default", host="localhost", port="19530")

# Define schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
]
schema = CollectionSchema(fields, "Document embeddings")

# Create collection
collection = Collection("documents", schema)

# Insert
data = [
    ["doc1", "doc2"],  # texts
    [[0.1, 0.2, ...], [0.3, 0.4, ...]]  # embeddings
]
collection.insert(data)

# Create index
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 256}
}
collection.create_index("embedding", index_params)

# Load and search
collection.load()
results = collection.search(
    data=[[0.1, 0.2, ...]],
    anns_field="embedding",
    param={"metric_type": "COSINE", "params": {"ef": 64}},
    limit=5
)
```

### Zilliz Cloud Pricing

```
Serverless:
├── Compute:  $4/million vCUs
├── Storage:  $0.02/GB/hour
└── Free tier available

Dedicated:
├── Starter:    $99/month
├── Standard:   $299/month
└── Enterprise: Custom
```

---

## Qdrant

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                      QDRANT                                │
├────────────────────────────────────────────────────────────┤
│ Type:        Open-source, written in Rust                  │
│ Architecture: Single binary, HNSW-based                   │
│ Best for:    Performance, complex filtering, edge         │
│ Managed:     Qdrant Cloud                                 │
└────────────────────────────────────────────────────────────┘
```

### Key Features

- **Rust:** Memory safety, no GC pauses
- **HNSW with Quantization:** High recall + compression
- **Powerful Filtering:** Complex boolean queries
- **Multi-tenancy:** Flexible sharding
- **ACID Transactions:** Data integrity

### Quick Start

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

# Insert points
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],
            payload={"title": "Doc 1", "category": "tech"}
        )
    ]
)

# Search with filtering
results = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],
    query_filter={
        "must": [
            {"key": "category", "match": {"value": "tech"}}
        ]
    },
    limit=5
)
```

### Advanced Filtering

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Complex filter
filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="tech")
        ),
        FieldCondition(
            key="year",
            range=Range(gte=2023)
        )
    ],
    must_not=[
        FieldCondition(
            key="status",
            match=MatchValue(value="draft")
        )
    ]
)

results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=filter,
    limit=10
)
```

### Quantization for Memory Savings

```python
from qdrant_client.models import ScalarQuantizationConfig, ScalarType

# Enable scalar quantization (4x memory reduction)
client.update_collection(
    collection_name="documents",
    quantization_config=ScalarQuantizationConfig(
        type=ScalarType.INT8,
        quantile=0.99,
        always_ram=True
    )
)
```

---

## Weaviate

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                     WEAVIATE                               │
├────────────────────────────────────────────────────────────┤
│ Type:        Open-source, modular                          │
│ Architecture: GraphQL API, plugin modules                  │
│ Best for:    Hybrid search, RAG, multimodal               │
│ Managed:     Weaviate Cloud                               │
└────────────────────────────────────────────────────────────┘
```

### Key Features

- **Hybrid Search:** Vector + BM25 in one query
- **Modules:** Vectorizers, generators, rankers
- **GraphQL API:** Flexible queries
- **Generative Search:** Built-in RAG

### Quick Start

```python
import weaviate
from weaviate.classes.init import Auth

# Connect to Cloud
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="YOUR_URL",
    auth_credentials=Auth.api_key("YOUR_KEY")
)

# Create collection with vectorizer
client.collections.create(
    name="Document",
    vectorizer_config=[
        weaviate.classes.config.Configure.Vectorizer.text2vec_openai()
    ],
    generative_config=weaviate.classes.config.Configure.Generative.openai()
)

# Add data (auto-vectorized!)
collection = client.collections.get("Document")
collection.data.insert({
    "title": "My Document",
    "content": "This is the content..."
})

# Hybrid search
results = collection.query.hybrid(
    query="machine learning",
    alpha=0.5,  # 0=BM25, 1=vector
    limit=5
)

# Generative search (RAG)
results = collection.generate.near_text(
    query="What is ML?",
    grouped_task="Summarize these documents",
    limit=3
)
```

### Hybrid Search Deep Dive

```python
# Alpha controls blend
#   alpha=0.0  →  Pure BM25 (keyword)
#   alpha=0.5  →  Equal blend (default)
#   alpha=1.0  →  Pure vector (semantic)

# Keyword-focused
results = collection.query.hybrid(
    query="python tutorial",
    alpha=0.2,  # More keyword weight
    limit=10
)

# Semantic-focused
results = collection.query.hybrid(
    query="how to learn programming",
    alpha=0.8,  # More vector weight
    limit=10
)
```

### Fusion Algorithms

```
Ranked Fusion (default):
- Combines ranks from both searches
- Simple, works well generally

Relative Score Fusion:
- Normalizes scores before combining
- Better when score magnitudes differ
```

---

## Chroma

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                      CHROMA                                │
├────────────────────────────────────────────────────────────┤
│ Type:        Open-source, local-first                      │
│ Architecture: Embedded or client-server                    │
│ Best for:    Prototyping, LangChain, development          │
│ Status:      Production features evolving                  │
└────────────────────────────────────────────────────────────┘
```

### Quick Start

```python
import chromadb
from chromadb.utils import embedding_functions

# In-memory (development)
client = chromadb.Client()

# Persistent (production-like)
client = chromadb.PersistentClient(path="./chroma_db")

# With OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_KEY",
    model_name="text-embedding-3-small"
)

# Create collection
collection = client.create_collection(
    name="documents",
    embedding_function=openai_ef,
    metadata={"hnsw:space": "cosine"}
)

# Add documents (auto-embedded!)
collection.add(
    documents=["Document 1 text", "Document 2 text"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["What is machine learning?"],
    n_results=5,
    where={"source": "doc1"}
)
```

### LangChain Integration

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load and split documents
loader = TextLoader("document.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
splits = text_splitter.split_documents(documents)

# Create vector store
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# Retrieve
retriever = vectorstore.as_retriever(
    search_type="mmr",  # Maximum Marginal Relevance
    search_kwargs={"k": 5}
)

docs = retriever.invoke("What is the main topic?")
```

---

## FAISS

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                       FAISS                                │
├────────────────────────────────────────────────────────────┤
│ Type:        Library (not a database)                      │
│ By:          Facebook AI Research                          │
│ Architecture: In-memory, GPU support                       │
│ Best for:    Research, custom solutions, benchmarks        │
└────────────────────────────────────────────────────────────┘
```

### Key Features

- **GPU Acceleration:** CUDA support
- **Multiple Indexes:** Flat, IVF, HNSW, PQ
- **No Server:** Just a library
- **Battle-tested:** Used in production at Meta

### Quick Start

```python
import faiss
import numpy as np

# Create random embeddings
d = 1536  # dimension
nb = 10000  # database size
np.random.seed(42)
xb = np.random.random((nb, d)).astype('float32')

# Build index
index = faiss.IndexFlatL2(d)  # Brute-force L2
index.add(xb)

print(f"Total vectors: {index.ntotal}")

# Search
k = 5  # top-k results
xq = np.random.random((1, d)).astype('float32')  # query

D, I = index.search(xq, k)
print(f"Distances: {D}")
print(f"Indices: {I}")
```

### Index Types

```python
# 1. Flat (brute-force, exact)
index = faiss.IndexFlatL2(d)

# 2. IVF (clustering)
nlist = 100  # number of clusters
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist)
index.train(xb)  # Required!
index.add(xb)

# 3. HNSW
index = faiss.IndexHNSWFlat(d, 32)  # 32 = M parameter
index.add(xb)

# 4. IVF + PQ (compressed)
m = 8  # bytes per vector
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
index.train(xb)
index.add(xb)
```

### GPU Acceleration

```python
# Single GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)

# Multiple GPUs
gpu_index = faiss.index_cpu_to_all_gpus(index)
```

### LangChain Integration

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Create from documents
vectorstore = FAISS.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings()
)

# Save/Load
vectorstore.save_local("faiss_index")
loaded = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)
```

---

## pgvector

### Overview

```
┌────────────────────────────────────────────────────────────┐
│                     pgvector                               │
├────────────────────────────────────────────────────────────┤
│ Type:        PostgreSQL extension                          │
│ Best for:    Existing Postgres users, ACID + vectors       │
│ Performance: Competitive with specialized DBs (2025)       │
│ Limitation:  Requires PostgreSQL expertise                 │
└────────────────────────────────────────────────────────────┘
```

### Installation

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)
);

-- Insert
INSERT INTO documents (content, embedding)
VALUES ('Sample text', '[0.1, 0.2, ...]');
```

### Index Types

```sql
-- HNSW (recommended)
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat (faster build, lower recall)
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Queries

```sql
-- Nearest neighbors (cosine)
SELECT id, content, embedding <=> '[0.1, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.1, ...]'
LIMIT 5;

-- With filtering
SELECT id, content
FROM documents
WHERE category = 'tech'
ORDER BY embedding <=> '[0.1, ...]'
LIMIT 5;
```

### Python Integration

```python
import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect("dbname=mydb")
register_vector(conn)

cur = conn.cursor()

# Search
embedding = [0.1, 0.2, ...]
cur.execute("""
    SELECT id, content, embedding <=> %s AS distance
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 5
""", (embedding, embedding))

results = cur.fetchall()
```

### Performance (2025 Benchmarks)

```
pgvectorscale vs Qdrant (50M vectors, 99% recall):
┌───────────────┬─────────┐
│ pgvectorscale │ 471 QPS │ ← 11.4x faster
│ Qdrant        │  41 QPS │
└───────────────┴─────────┘

Both achieve sub-100ms p99 latency
```

---

## Chunking Strategies

### Why Chunking Matters

```
Document (5000 tokens)
        ↓
  Chunking Strategy
        ↓
┌────────────────────────────────────────┐
│ Chunk 1  │ Chunk 2  │ Chunk 3  │ ...  │
│ 400 tok  │ 400 tok  │ 400 tok  │      │
└────────────────────────────────────────┘
        ↓
  Embeddings (one per chunk)
        ↓
  Vector Database
```

### Recommended Settings

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Starting point (most projects)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # ~400-512 tokens
    chunk_overlap=50,    # 10-20% overlap
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(documents)
```

### Strategy Comparison

| Strategy | Recall | Precision | Best For |
|----------|--------|-----------|----------|
| Fixed size | Good | Medium | General use |
| Semantic | Best | Good | Quality-critical |
| Page-level | Good | Good | Structured docs |
| No overlap | Medium | Best | Storage-constrained |

### NVIDIA 2024 Benchmark Results

```
Accuracy by Strategy:
Page-level:     ████████████████ 0.648 (winner)
Semantic 400:   ███████████████  0.620
Recursive 200:  ██████████████   0.580
```

### Advanced: Contextual Chunking (Anthropic 2024)

```python
# Idea: Add context to each chunk before embedding

def add_context(document, chunk):
    """Use LLM to add document context to chunk"""
    prompt = f"""
    Document: {document[:1000]}

    Chunk: {chunk}

    Add a brief context sentence before this chunk.
    """
    context = llm.invoke(prompt)
    return f"{context}\n\n{chunk}"

# Each chunk now includes document-level context
contextualized_chunks = [
    add_context(full_doc, chunk)
    for chunk in chunks
]
```

---

## Hybrid Search

### Why Hybrid?

```
Query: "Python 3.12 new features"

Vector Search (semantic):
✓ "Latest Python version improvements"
✗ "JavaScript ES2024 features"

BM25 Search (keyword):
✓ Documents containing "Python 3.12"
✗ "Latest Python version improvements" (no exact match)

Hybrid (combined):
✓ Best of both worlds
```

### Reciprocal Rank Fusion (RRF)

```
RRF Score = Σ 1/(k + rank)

Example (k=60):
Document A: rank 1 in vector, rank 5 in BM25
  RRF = 1/(60+1) + 1/(60+5) = 0.016 + 0.015 = 0.031

Document B: rank 3 in vector, rank 2 in BM25
  RRF = 1/(60+3) + 1/(60+2) = 0.016 + 0.016 = 0.032 ← Winner
```

### Implementation with Weaviate

```python
# Hybrid search
results = collection.query.hybrid(
    query="Python tutorial",
    alpha=0.5,  # Equal weight
    limit=10,
    fusion_type="relative_score"  # or "ranked"
)

# Adjust for use case
# Legal docs: alpha=0.3 (more keyword)
# Creative search: alpha=0.8 (more semantic)
```

### Implementation with Qdrant

```python
from qdrant_client import models

# Requires BM25 pre-indexing
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="text",
                match=models.MatchText(text="Python")
            )
        ]
    ),
    limit=10
)
```

---

## LangChain Integration

### Unified Interface

```python
from langchain_community.vectorstores import (
    Chroma, FAISS, Pinecone, Qdrant, Weaviate, Milvus, PGVector
)
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# All follow same pattern:
# vectorstore = VectorStore.from_documents(docs, embeddings)
# retriever = vectorstore.as_retriever()
# docs = retriever.invoke("query")
```

### Complete RAG Pipeline

```python
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Vector store
vectorstore = Chroma.from_documents(docs, embeddings)

# 2. Retriever
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20}
)

# 3. LLM
llm = ChatOpenAI(model="gpt-4o")

# 4. Prompt
prompt = ChatPromptTemplate.from_template("""
Answer based on the following context:

{context}

Question: {input}
""")

# 5. Chain
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# 6. Invoke
result = retrieval_chain.invoke({"input": "What is the main topic?"})
print(result["answer"])
```

### Search Types

```python
# 1. Similarity (default)
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# 2. MMR (Maximum Marginal Relevance) - reduces redundancy
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,  # Fetch more, then diversify
        "lambda_mult": 0.5  # Balance relevance/diversity
    }
)

# 3. Similarity with threshold
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.7  # Only highly relevant
    }
)
```

---

## Security & Access Control

### Key Challenges

```
Security Risks:
├── Embedding Inversion Attack
│   └── Reconstruct original data from embeddings
├── All-or-Nothing Access
│   └── API keys grant full access
├── Multi-tenant Data Leakage
│   └── User A sees User B's data
└── Missing Encryption
    └── Data at rest/in transit exposed
```

### RBAC Implementation (Qdrant)

```python
from qdrant_client import QdrantClient
import jwt

# Generate JWT with permissions
payload = {
    "sub": "user123",
    "access": [
        {"collection": "public_docs", "access": "r"},
        {"collection": "user123_private", "access": "rw"}
    ]
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Connect with token
client = QdrantClient(
    url="https://your-qdrant-instance.com",
    api_key=token  # JWT as API key
)

# User can only access permitted collections
```

### Multi-tenancy Patterns

```python
# Pattern 1: Collection per tenant
client.create_collection(f"tenant_{tenant_id}")

# Pattern 2: Payload filtering
client.upsert(
    collection_name="shared",
    points=[
        PointStruct(
            id=1,
            vector=[...],
            payload={"tenant_id": "tenant123"}
        )
    ]
)

# Search with mandatory filter
results = client.search(
    collection_name="shared",
    query_vector=[...],
    query_filter={"must": [{"key": "tenant_id", "match": {"value": current_tenant}}]}
)
```

### Best Practices Checklist

```
[ ] Enable TLS/HTTPS for all connections
[ ] Use short-lived tokens (JWT with expiry)
[ ] Implement RBAC at collection/document level
[ ] Encrypt data at rest (if supported)
[ ] Audit access logs
[ ] Regular security assessments
[ ] Compliance verification (SOC2, HIPAA, etc.)
```

---

## Production Best Practices

### Scaling Strategies

```
Horizontal Scaling:
┌────────────────────────────────────────────┐
│          Load Balancer                      │
└────────────┬─────────────┬─────────────────┘
             │             │
     ┌───────▼───────┐ ┌───▼───────────┐
     │  Replica 1    │ │   Replica 2   │
     │  (reads)      │ │   (reads)     │
     └───────────────┘ └───────────────┘
             │
     ┌───────▼───────┐
     │   Primary     │
     │   (writes)    │
     └───────────────┘

Sharding:
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Shard 1    │ │  Shard 2    │ │  Shard 3    │
│  (A-H)      │ │  (I-P)      │ │  (Q-Z)      │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Performance Optimization

```python
# 1. Batch operations
# BAD: Individual upserts
for doc in documents:
    client.upsert(collection_name="docs", points=[doc])

# GOOD: Batch upsert
client.upsert(collection_name="docs", points=documents)

# 2. Vector compression
client.update_collection(
    collection_name="docs",
    quantization_config=ScalarQuantizationConfig(
        type=ScalarType.INT8,  # 4x memory reduction
        quantile=0.99,
        always_ram=True
    )
)

# 3. Pre-filtering
# Instead of searching all vectors, filter first
results = client.search(
    collection_name="docs",
    query_vector=[...],
    query_filter={"must": [{"key": "category", "match": {"value": "tech"}}]},
    limit=10
)
```

### Monitoring Metrics

```
Key Metrics to Track:
├── Latency
│   ├── p50 (median)
│   ├── p99 (critical!)  ← Focus here
│   └── p999
├── Throughput
│   ├── Queries per second
│   └── Inserts per second
├── Recall
│   └── Accuracy vs brute-force
├── Resources
│   ├── Memory usage
│   ├── CPU utilization
│   └── Disk I/O
└── Errors
    ├── Timeout rate
    └── Error rate
```

### Production Checklist

```
[ ] High availability (replicas)
[ ] Automatic failover
[ ] Backup strategy
[ ] Monitoring & alerting
[ ] Load testing completed
[ ] Security audit passed
[ ] Documentation updated
[ ] Runbook for incidents
```

---

## Cost Analysis

### Break-Even: Managed vs Self-Hosted

```
Break-even point:
~80-100 million queries/month
~100 million vectors with high query volume

Below threshold → Managed (Pinecone, Zilliz, Qdrant Cloud)
Above threshold → Self-hosted (Milvus, Qdrant OSS)
```

### Cost Comparison Table

| Provider | Free Tier | Entry Paid | Enterprise |
|----------|-----------|------------|------------|
| Pinecone | $100 credits | ~$70/mo | Custom |
| Qdrant Cloud | 1GB free | ~$100/mo | Custom |
| Zilliz (Milvus) | Free tier | $89/mo | Custom |
| Weaviate | $25/mo | ~$50/mo | Custom |
| Self-hosted | - | $200-500/mo* | - |

*Self-hosted includes compute, storage, operations

### Hidden Costs (Self-Hosted)

```
Self-hosted TCO:
├── Compute (EC2, GKE, etc.)
├── Storage (SSD for HNSW)
├── Dependencies
│   ├── Kafka/Pulsar (Milvus WAL)
│   ├── etcd (metadata)
│   └── Kubernetes
├── Operations
│   ├── Monitoring (Prometheus, Grafana)
│   ├── Backups
│   └── Updates
└── Engineering time
    └── Often the biggest cost!
```

### Recommendations

```
Startup/POC:
→ Managed (Pinecone, Chroma Cloud)
→ Minimize ops, focus on product

Growth stage (<100M vectors):
→ Managed with cost monitoring
→ Consider Qdrant Cloud for cost-effectiveness

Scale (>100M vectors, high QPS):
→ Self-hosted (Milvus, Qdrant OSS)
→ Dedicated infrastructure team
```

---

## Выбор решения

### Decision Flowchart

```
Start
  │
  ▼
Already using PostgreSQL? ──Yes──► pgvector
  │
  No
  │
  ▼
Need zero ops? ──Yes──► Pinecone Serverless
  │
  No
  │
  ▼
Billion-scale + GPU? ──Yes──► Milvus/Zilliz
  │
  No
  │
  ▼
Complex filtering needed? ──Yes──► Qdrant
  │
  No
  │
  ▼
Need hybrid search? ──Yes──► Weaviate
  │
  No
  │
  ▼
Prototyping/LangChain? ──Yes──► Chroma
  │
  No
  │
  ▼
Custom/Research? ──Yes──► FAISS
```

### Summary Table

| Solution | Best For | Pros | Cons |
|----------|----------|------|------|
| Pinecone | Zero-ops production | Managed, fast | Cost at scale |
| Milvus | Billion-scale | GPU, indexes | Complex ops |
| Qdrant | Performance | Rust, filtering | Smaller community |
| Weaviate | Hybrid search | Modules, RAG | Resource heavy |
| Chroma | Prototyping | Simple, LangChain | Not production-ready |
| FAISS | Research | GPU, flexible | Not a database |
| pgvector | Postgres users | ACID, existing | Requires tuning |

### Final Recommendations

```
For most RAG projects:
1. Development: Chroma
2. Production: Pinecone or Qdrant Cloud
3. Scale: Milvus self-hosted

Embedding models:
1. Quality: text-embedding-3-large
2. Cost-effective: text-embedding-3-small
3. Open source: BGE-large-en

Chunking:
1. Start: 400-512 tokens, 10-20% overlap
2. Test with your data
3. Consider semantic chunking for quality
```

---

## Полезные ресурсы

### Официальная документация
- [Pinecone Docs](https://docs.pinecone.io/)
- [Milvus Docs](https://milvus.io/docs)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Weaviate Docs](https://weaviate.io/developers/weaviate)
- [Chroma Docs](https://docs.trychroma.com/)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [pgvector](https://github.com/pgvector/pgvector)

### LangChain Integration
- [LangChain Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

### Benchmarks
- [Qdrant Benchmarks](https://qdrant.tech/benchmarks/)
- [ANN Benchmarks](https://ann-benchmarks.com/)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

## Связь с другими темами

[[vector-databases-guide]] — Этот гайд по векторным базам данных даёт концептуальное введение в embeddings, similarity search и ANN-алгоритмы. Текущий документ углубляет эту тему практическими сравнениями конкретных решений (Pinecone, Milvus, Qdrant, Weaviate) и production-паттернами. Рекомендуется сначала прочитать vector-databases-guide для понимания теории, затем этот материал для выбора конкретного решения.

[[embeddings-complete-guide]] — Полный гайд по embeddings объясняет, как создаются и используются векторные представления текста и изображений. Без понимания природы embeddings (размерность, метрики сходства, модели генерации) невозможно правильно выбрать vector database и настроить chunking-стратегию. Этот материал является обязательным пререквизитом.

[[nosql-databases-complete]] — NoSQL-базы данных (MongoDB, Redis, Cassandra) решают задачи неструктурированного хранения, которые пересекаются с vector databases. Понимание Document DB и Key-Value stores помогает оценить, когда достаточно NoSQL с vector-расширением (MongoDB Atlas Vector Search), а когда нужна специализированная vector DB. Рекомендуется для формирования целостной картины.

[[databases-fundamentals-complete]] — Фундаментальные концепции баз данных (индексы, транзакции, CAP-теорема) применимы и к vector databases: HNSW — это тип индекса, metadata filtering использует стандартную фильтрацию, а выбор между managed и self-hosted определяется теми же критериями. Полезен как теоретическая база перед изучением специализированных решений.

## Источники и дальнейшее чтение

- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Главы о хранилищах данных, индексах и распределённых системах дают фундамент для понимания архитектуры vector databases и trade-offs между consistency, availability и performance.
- Petrov A. (2019). *Database Internals*. — Глубокий разбор алгоритмов индексации (B-Tree, LSM-Tree), который помогает понять, почему ANN-алгоритмы (HNSW, IVF) работают принципиально иначе и какие trade-offs они предлагают.
- Redmond E., Wilson J.R. (2012). *Seven Databases in Seven Weeks*. — Обзор различных моделей данных (document, graph, key-value), который помогает выбрать правильный тип хранилища для AI/ML-задач и понять, когда vector DB необходима, а когда достаточно расширения существующей БД.

---

---

## Проверь себя

> [!question]- Почему для RAG часто достаточно pgvector в PostgreSQL, а не отдельная vector database?
> pgvector позволяет хранить embeddings и выполнять similarity search прямо в PostgreSQL, рядом с остальными данными. Нет необходимости синхронизировать данные между двумя системами. Для < 10 млн векторов и когда уже используется PostgreSQL — pgvector проще и дешевле. Отдельная vector DB нужна при: > 100 млн векторов, необходимости специализированных фич (multi-tenancy, hybrid search), или когда PostgreSQL не используется.

> [!question]- Чем HNSW отличается от IVF и когда какой алгоритм выбрать?
> HNSW (Hierarchical Navigable Small World): граф с несколькими уровнями, высокое recall (>95%), быстрый поиск, но потребляет много RAM (весь граф в памяти). IVF (Inverted File Index): кластеризация + поиск по ближайшим кластерам, меньше памяти, но ниже recall. HNSW для высокой точности при умеренных объёмах. IVF для больших объёмов с ограниченной RAM.

> [!question]- Почему chunking-стратегия критична для качества RAG-системы?
> Слишком большие chunks — потеря точности (много нерелевантного контекста в ответе). Слишком маленькие — потеря смысла (фрагмент без контекста). Оптимальный размер зависит от контента: 200-500 токенов для документации, с overlap 10-20%. Semantic chunking (по границам смысловых блоков) лучше fixed-size. Плохой chunking нельзя компенсировать лучшим индексом.

> [!question]- Когда вместо vector database достаточно keyword search (BM25)?
> BM25 лучше для: точных терминов (коды ошибок, ID, имена), known-item search (пользователь знает что ищет), когда контент структурирован и термины однозначны. Vector search лучше для: семантического поиска (вопросы на естественном языке), multimodal (текст + изображения), когда синонимы и перефразирования важны. Лучший подход — hybrid search (BM25 + vector с reranking).

---

## Ключевые карточки

Что такое Vector Database?
?
БД, оптимизированная для хранения и поиска embeddings (высокоразмерных векторов). Основная операция — similarity search (найти K ближайших векторов). Используется для RAG, semantic search, рекомендаций. Примеры: Pinecone, Milvus, Qdrant, Weaviate.

Что такое HNSW индекс?
?
Hierarchical Navigable Small World — граф для ANN (Approximate Nearest Neighbor) поиска. Многоуровневая структура: верхние уровни — грубый поиск, нижние — точный. Recall > 95%, O(log N) поиск. Используется в Pinecone, Qdrant, pgvector. Основной trade-off: RAM vs качество.

Чем отличаются cosine similarity, L2 и dot product?
?
Cosine — угол между векторами (не зависит от длины), стандарт для текста. L2 (Euclidean) — расстояние в пространстве, для нормализованных векторов = cosine. Dot product — для моделей с magnitude-информацией. Выбор зависит от модели embeddings.

Что такое pgvector?
?
Расширение PostgreSQL для хранения и поиска векторов. Тип vector(1536), операторы <=> (cosine), <-> (L2). Индексы: ivfflat (IVF), hnsw. Преимущество: все данные в одной БД, привычный SQL, транзакции. Подходит для < 10 млн векторов.

Что такое hybrid search в контексте RAG?
?
Комбинация keyword search (BM25) и vector search (semantic). BM25 ловит точные совпадения, vector — семантическое сходство. Результаты объединяются через reciprocal rank fusion или cross-encoder reranking. Лучшее качество, чем любой метод по отдельности.

Что такое chunking в RAG?
?
Разбиение документов на фрагменты перед embedding и индексацией. Стратегии: fixed-size (по токенам), semantic (по границам абзацев/секций), recursive (по иерархии). Overlap 10-20% между chunks. Размер 200-500 токенов — типичный баланс точности и контекста.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[vector-databases-guide]] | Теория embeddings и similarity search |
| Углубиться | [[embeddings-complete-guide]] | Как создаются и используются embeddings |
| Углубиться | [[rag-advanced-techniques]] | Продвинутые RAG-паттерны и оптимизация |
| Смежная тема | [[nosql-databases-complete]] | MongoDB Atlas Vector Search, Redis Vector |
| Смежная тема | [[llm-fundamentals]] | Основы LLM, токенизация, контекстное окно |
| Обзор | [[databases-overview]] | Вернуться к карте раздела |

---

*Документ создан: 2025-12-30*
*На основе deep research (22+ источников)*
