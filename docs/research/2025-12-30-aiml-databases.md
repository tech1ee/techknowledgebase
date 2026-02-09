# Research Report: AI/ML Databases — Vector Databases & Embeddings

**Date:** 2025-12-30
**Sources Evaluated:** 22+
**Research Depth:** Deep (comprehensive multi-source analysis)

## Executive Summary

Vector databases — специализированные хранилища для high-dimensional embeddings, critical для RAG, semantic search, recommendation systems. Рынок вырос с $1.73B (2024) до projected $10.6B (2032). Лидеры: **Pinecone** (managed, serverless), **Milvus** (billion-scale, GPU), **Qdrant** (Rust, high performance), **Weaviate** (hybrid search), **Chroma** (local dev). Ключевые алгоритмы: HNSW (высокая точность), IVF (масштабируемость), PQ (сжатие). pgvector позволяет использовать PostgreSQL как vector store. Embedding models: OpenAI text-embedding-3-large (3072 dims), Sentence Transformers, CLIP для multimodal. Chunking strategy критична — 400-512 tokens с 10-20% overlap. Cost break-even для self-hosted vs managed: ~80-100M queries/month.

---

## Key Findings

### 1. Vector Database Landscape [HIGH CONFIDENCE]

| Database | Type | Architecture | Best For |
|----------|------|--------------|----------|
| Pinecone | Managed | Serverless, cloud-native | Zero-ops production |
| Milvus | OSS/Managed | Distributed, GPU support | Billion-scale, high control |
| Qdrant | OSS/Managed | Rust, HNSW | Performance, edge |
| Weaviate | OSS/Managed | GraphQL, modules | Hybrid search, RAG |
| Chroma | OSS | Local-first | Prototyping, LangChain |
| FAISS | Library | In-memory, GPU | Research, custom solutions |
| pgvector | Extension | PostgreSQL native | Existing Postgres users |

**Market Stats:**
- Milvus: 35,000+ GitHub stars (leader)
- Qdrant: 9,000+ stars
- Weaviate: 8,000+ stars
- Chroma: 6,000+ stars

### 2. Core Algorithms [HIGH CONFIDENCE]

**HNSW (Hierarchical Navigable Small World):**
- Иерархический граф для approximate nearest neighbor
- Параметры: M (connections), ef_search (quality/speed trade-off)
- High recall (>99%), logarithmic complexity
- Memory-intensive

**IVF (Inverted File Index):**
- Clustering-based approach
- Параметры: nlist (clusters), nprobe (search clusters)
- Better for large datasets
- Lower memory than HNSW

**Product Quantization (PQ):**
- Vector compression 4-16x
- Slight accuracy loss
- Essential for billion-scale

**DiskANN:**
- SSD-based indexing
- Handles datasets larger than RAM
- Supported by Milvus

### 3. Similarity Metrics [HIGH CONFIDENCE]

| Metric | Formula | Use Case |
|--------|---------|----------|
| Cosine | cos(θ) = A·B / (‖A‖·‖B‖) | Text embeddings, normalized vectors |
| Dot Product | A·B | Pre-normalized, OpenAI embeddings |
| Euclidean (L2) | √Σ(ai-bi)² | Image embeddings, spatial data |
| Manhattan (L1) | Σ‖ai-bi‖ | Sparse vectors, specific domains |

**Recommendation:** Cosine similarity для текста (нормализует длину), Dot Product если embeddings pre-normalized.

### 4. Embedding Models [HIGH CONFIDENCE]

**OpenAI:**
- text-embedding-3-large: 3072 dimensions, best quality
- text-embedding-3-small: 1536 dimensions, cost-effective
- Matryoshka representation: can truncate dimensions

**Open Source (MTEB Benchmark leaders):**
- Sentence Transformers (all-MiniLM-L6-v2): 384 dims, fast
- BGE-large-en: 1024 dims, high quality
- E5-large: 1024 dims, multilingual

**Multimodal:**
- CLIP: text + image in same space (512 dims)
- Jina CLIP v2: multilingual, 3% improvement over v1
- Voyage Multimodal-3: unified encoder for text/images

### 5. pgvector — PostgreSQL Extension [HIGH CONFIDENCE]

**Features:**
- Native PostgreSQL integration
- HNSW and IVFFlat indexes
- No separate infrastructure

**Performance (May 2025 benchmarks):**
- pgvectorscale: 471 QPS at 99% recall on 50M vectors
- 11.4x faster than Qdrant (41 QPS) at same recall
- Sub-100ms query latencies

**When to use:**
- Already using PostgreSQL
- Need ACID transactions with vectors
- Moderate scale (<100M vectors)
- Want single database for all data

**Limitations:**
- Not as optimized as specialized DBs
- Requires more tuning for large scale

### 6. Pinecone Deep Dive [HIGH CONFIDENCE]

**Serverless Architecture (January 2024):**
- 50x lower cost vs pod-based
- No capacity planning needed
- Auto-scaling based on usage

**Pricing:**
- Storage: $0.33/GB/month
- Read units: $8.25/million
- Write units: $2/million
- $100 free credits to start

**Pod vs Serverless:**
| Aspect | Pods | Serverless |
|--------|------|------------|
| Pricing | Per-pod per-minute | Usage-based |
| Scaling | Manual/vertical | Automatic |
| Min cost | Pod baseline | Zero when idle |
| Regions | All | AWS (GCP coming) |

### 7. Qdrant Architecture [HIGH CONFIDENCE]

**Key Features:**
- Written in Rust (memory safety, no GC)
- HNSW with quantization
- Powerful metadata filtering
- ACID transactions
- Multi-tenancy with flexible sharding

**Performance:**
- Consistently low latency
- High throughput under load
- Compact memory footprint

**JWT-based RBAC (v1.9.0+):**
- Granular access control
- Collection-level permissions
- Document-level filtering

### 8. Milvus for Scale [HIGH CONFIDENCE]

**Architecture:**
- Cloud-native, decoupled compute/storage
- GPU acceleration (CUDA)
- Supports trillion-vector datasets
- Kubernetes-native

**Index Types:**
- IVF_FLAT, IVF_SQ8, IVF_PQ
- HNSW
- DiskANN
- GPU indexes (GPU_IVF_FLAT, GPU_IVF_PQ)

**Zilliz Cloud Pricing:**
- Serverless: $4/million vCUs
- Dedicated: from $99/month
- Enterprise: custom

### 9. Weaviate Hybrid Search [HIGH CONFIDENCE]

**Architecture:**
- Vector + BM25 keyword search
- Modular design (vectorizers, generators)
- GraphQL API

**Fusion Algorithms:**
- Ranked Fusion (default)
- Relative Score Fusion

**Alpha Parameter (0.0-1.0):**
- 0.0 = pure BM25 (keyword)
- 0.5 = equal weight (default)
- 1.0 = pure vector search

**Modules:**
- text2vec-openai: auto-vectorization
- generative-openai: RAG integration
- multi2vec-clip: multimodal

### 10. Chunking Strategies [HIGH CONFIDENCE]

**Recommended Starting Point:**
- RecursiveCharacterTextSplitter
- 400-512 tokens
- 10-20% overlap

**NVIDIA 2024 Benchmark Results:**
- Page-level chunking: 0.648 accuracy (winner)
- Lowest standard deviation (0.107)

**Chroma Technical Report (July 2024):**
- ClusterSemanticChunker (400 tokens): 91.3% recall
- RecursiveCharacterTextSplitter (200 tokens, no overlap): consistent performance
- Reducing overlap improved IoU (efficiency)

**Key Insight:**
> "Chunking configuration has a critical impact on retrieval performance—comparable to, or greater than, the influence of the embedding model itself."

**Trade-offs:**
- Smaller chunks → better for fine-grained retrieval
- Larger chunks → better for summarization
- Overlap → better context, more storage

### 11. Hybrid Search (Vector + BM25) [HIGH CONFIDENCE]

**Why Hybrid:**
- Vector: semantic understanding
- BM25: exact keyword matching
- Combined: best of both worlds

**Implementation:**
1. Run vector search in parallel with BM25
2. Apply fusion algorithm (RRF or score-based)
3. Return merged, re-ranked results

**Reciprocal Rank Fusion (RRF):**
```
score = Σ 1/(k + rank)
```
Where k is typically 60.

**Use Cases:**
- E-commerce: product names + descriptions
- Legal: exact terms + semantic context
- Support: ticket matching

### 12. LangChain Integration [HIGH CONFIDENCE]

**Officially Supported:**
- Chroma, FAISS, Pinecone, Milvus, Qdrant, Weaviate, PGVector

**When to Use Each:**
| Vector Store | Best For |
|--------------|----------|
| Chroma | Quick prototyping, education |
| FAISS | Local development, research |
| Pinecone | Production, real-time, scale |
| Milvus | Billion-scale, self-hosted |
| Qdrant | Performance, complex filters |

**Common Pattern:**
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever(
    search_type="mmr",  # Maximum Marginal Relevance
    search_kwargs={"k": 5}
)
```

### 13. Security & Access Control [HIGH CONFIDENCE]

**Key Challenges:**
- Embedding inversion attacks (reconstruct original data)
- All-or-nothing API keys
- Multi-tenant data isolation

**Best Practices:**
1. **RBAC**: Role-based access control
2. **JWT**: Granular token permissions
3. **MFA**: Multi-factor authentication
4. **ABAC**: Attribute-based rules
5. **Encryption**: At rest and in transit

**Qdrant RBAC (v1.9.0+):**
- JWT-based tokens
- Collection-level permissions
- Document-level filtering

**Compliance:**
- HIPAA (healthcare)
- PCI DSS (finance)
- SOC 2 (enterprise)

### 14. Production Best Practices [HIGH CONFIDENCE]

**Scaling:**
- Horizontal scaling with sharding
- Read replicas for query load
- Shard by tenant or time

**Performance:**
- Compress vectors with PQ/OPQ (4-16x storage reduction)
- Tune HNSW: M and ef_search
- Bulk ingest, reindex off-peak
- Cache frequent queries

**Architecture:**
- Separate storage from compute (Milvus)
- Hybrid: vector for semantic, keyword for exact, warehouse for analytics
- Pre-filter with keywords before dense retrieval

**Monitoring:**
- Track p99 latency (not just median)
- Monitor recall accuracy
- Set alerts on query failures

### 15. Cost Analysis [HIGH CONFIDENCE]

**Break-Even Point (Self-hosted vs Managed):**
- ~80-100 million queries/month
- ~100 million vectors with high query volume

**Managed Services:**
| Provider | Free Tier | Paid |
|----------|-----------|------|
| Pinecone | $100 credits | $0.33/GB + RU/WU |
| Qdrant Cloud | 1GB free | ~$102/month (standard) |
| Zilliz (Milvus) | Free tier | $89-114/month |
| Weaviate | $25/month | $2.64/AI unit |

**Self-Hosted Hidden Costs:**
- Infrastructure (compute, storage)
- Dependencies (Kafka/Pulsar, etcd, K8s)
- Operations (monitoring, updates)
- Engineering time

**Recommendation:**
- <10M vectors, low query: Managed
- >100M vectors, high query: Self-hosted
- POC/Prototype: Always managed

---

## Community Sentiment

### Pinecone
**Positive:**
- "Truly serverless, zero ops"
- "Best documentation"
- "Fast time-to-production"

**Negative:**
- "Expensive at scale"
- "Vendor lock-in"
- "Limited self-hosting option"

### Milvus
**Positive:**
- "Industrial-scale proven"
- "GPU acceleration is game-changer"
- "Most indexing options"

**Negative:**
- "Complex to operate"
- "Steep learning curve"
- "Requires data engineering expertise"

### Qdrant
**Positive:**
- "Rust = fast and safe"
- "Excellent filtering"
- "Great cost/performance ratio"

**Negative:**
- "Smaller community than Milvus"
- "Less enterprise tooling"

### pgvector
**Positive:**
- "Use existing Postgres"
- "No new infrastructure"
- "ACID with vectors"

**Negative:**
- "Not as fast as specialized DBs"
- "Requires tuning"

### Chroma
**Positive:**
- "Perfect for prototyping"
- "LangChain native"
- "Easy to start"

**Negative:**
- "Not production-ready"
- "Limited scale"

---

## Conflicting Information

**Topic:** pgvector vs Specialized DBs Performance
- **Pro-pgvector:** "pgvectorscale 11.4x faster than Qdrant" (Timescale benchmarks)
- **Pro-Specialized:** "Specialized DBs optimized for vector workloads"
- **Resolution:** Benchmarks vary by scenario; test with your data

**Topic:** Self-hosted vs Managed Cost
- **Pro-Self-hosted:** "Cheaper at scale"
- **Pro-Managed:** "Hidden costs make self-hosted expensive"
- **Resolution:** Break-even at ~80-100M queries/month

**Topic:** Chunking Strategy
- **Some:** "Semantic chunking is best"
- **Others:** "Simple recursive splitter works well"
- **Resolution:** NVIDIA 2024 shows page-level wins; test for your use case

---

## Recommendations

### By Use Case

**RAG Production (Enterprise):**
1. Pinecone Serverless (zero ops)
2. Milvus/Zilliz (billion-scale)
3. Qdrant Cloud (cost-effective)

**RAG Development/Prototyping:**
1. Chroma (LangChain native)
2. FAISS (local, free)
3. pgvector (existing Postgres)

**Existing PostgreSQL Users:**
→ pgvector with pgvectorscale

**Billion-Scale + GPU:**
→ Milvus with GPU indexes

**Complex Filtering + Performance:**
→ Qdrant

**Hybrid Search (Vector + Keyword):**
→ Weaviate or Qdrant

**Multimodal (Text + Images):**
→ Weaviate with CLIP module

### Embedding Model Selection

| Requirement | Model |
|-------------|-------|
| Best quality (cost ok) | text-embedding-3-large |
| Cost-effective | text-embedding-3-small |
| Open source | BGE-large-en, E5-large |
| Fast, small | all-MiniLM-L6-v2 |
| Multimodal | CLIP, Voyage Multimodal-3 |

### Chunking Strategy

- Start: 400-512 tokens, 10-20% overlap
- Fine-grained retrieval: 200-300 tokens
- Summarization: 800-1000 tokens
- Always test with your data

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Pinecone Serverless Blog](https://www.pinecone.io/blog/serverless/) | Official | 0.95 | Serverless architecture |
| 2 | [Qdrant Benchmarks](https://qdrant.tech/benchmarks/) | Official | 0.90 | Performance data |
| 3 | [Weaviate Hybrid Search](https://weaviate.io/blog/hybrid-search-explained) | Official | 0.90 | Hybrid search details |
| 4 | [Milvus GitHub](https://github.com/milvus-io/milvus) | Official | 0.95 | Architecture, features |
| 5 | [pgvector vs Qdrant](https://www.tigerdata.com/blog/pgvector-vs-qdrant) | Tech Blog | 0.85 | Benchmark comparison |
| 6 | [LangChain Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/) | Official | 0.95 | Integration guide |
| 7 | [Chroma LangChain](https://blog.langchain.com/langchain-chroma/) | Official | 0.90 | Chroma integration |
| 8 | [FAISS GitHub](https://github.com/facebookresearch/faiss) | Official | 0.95 | Library documentation |
| 9 | [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) | Official | 0.95 | Embedding best practices |
| 10 | [Pinecone Chunking](https://www.pinecone.io/learn/chunking-strategies/) | Official | 0.90 | Chunking strategies |
| 11 | [Weaviate Chunking](https://weaviate.io/blog/chunking-strategies-for-rag) | Official | 0.90 | Chunking for RAG |
| 12 | [Stack Overflow Chunking](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/) | Expert | 0.85 | Practical insights |
| 13 | [Qdrant RBAC](https://qdrant.tech/articles/data-privacy/) | Official | 0.90 | Security features |
| 14 | [Cisco Vector Security](https://sec.cloudapps.cisco.com/security/center/resources/securing-vector-databases) | Official | 0.90 | Security best practices |
| 15 | [Zilliz Scaling](https://zilliz.com/learn/Building-Scalable-AI-with-Vector-Databases-A-2024-Strategy) | Official | 0.90 | Production scaling |
| 16 | [Vector DB Comparison](https://www.firecrawl.dev/blog/best-vector-databases-2025) | Tech Blog | 0.85 | 2025 comparison |
| 17 | [Cost Analysis](https://openmetal.io/resources/blog/when-self-hosting-vector-databases-becomes-cheaper-than-saas/) | Tech Blog | 0.80 | Cost break-even |
| 18 | [CLIP Pinecone](https://www.pinecone.io/learn/series/image-search/clip/) | Official | 0.90 | Multimodal embeddings |
| 19 | [Voyage Multimodal](https://blog.voyageai.com/2024/11/12/voyage-multimodal-3/) | Official | 0.90 | Latest multimodal |
| 20 | [Jina CLIP v2](https://huggingface.co/jinaai/jina-clip-v2) | Official | 0.90 | Multilingual CLIP |
| 21 | [MTEB Benchmark](https://huggingface.co/spaces/mteb/leaderboard) | Official | 0.95 | Embedding rankings |
| 22 | [SingleStore Benchmark](https://benchant.com/blog/single-store-vector-vs-pinecone-zilliz-2025) | Tech Blog | 0.80 | Performance comparison |

---

## Research Methodology

- **Queries used:** 22 search queries covering vector databases, algorithms, embeddings, chunking, security, production, costs
- **Source types:** Official documentation, vendor blogs, tech blogs, GitHub, benchmarks
- **Coverage:** Pinecone, Milvus, Qdrant, Weaviate, Chroma, FAISS, pgvector, OpenAI embeddings, CLIP, security, production deployment
- **Key updates:** Pinecone Serverless (Jan 2024), pgvectorscale benchmarks (May 2025), Voyage Multimodal-3 (Nov 2024)
