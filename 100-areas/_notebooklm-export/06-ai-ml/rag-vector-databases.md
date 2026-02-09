# Vector Databases: Infrastructure for Semantic Search

Vector databases are specialized systems designed to store, index, and retrieve high-dimensional vectors efficiently. As embeddings become central to AI applications, vector databases have emerged as critical infrastructure, enabling semantic search at scales from thousands to billions of vectors. Understanding vector databases reveals how the theoretical promise of embeddings becomes practical reality.

## Why Vector Databases Exist

Traditional databases are built for structured data—rows and columns, keys and values. They excel at exact matches: find the customer with ID 12345, retrieve all orders from last Tuesday. But semantic search needs similarity matches: find documents whose meaning is close to this query.

Similarity search over vectors is fundamentally different from traditional database queries. There's no index that immediately returns the most similar items. We need to compare the query against many candidates, combining scores to find the closest matches.

Brute force comparison—checking every vector against the query—works for small collections but scales poorly. With a million vectors, each query requires a million similarity computations. With a billion vectors, a billion comparisons. Response times become unacceptable, and computational costs explode.

Vector databases solve this through specialized indexing that enables approximate nearest neighbor (ANN) search. By preprocessing vectors into intelligent data structures, they reduce the number of comparisons needed from all vectors to a small fraction while still finding most of the truly nearest neighbors.

The tradeoff between accuracy and speed defines ANN search. Faster search means checking fewer candidates, potentially missing some true nearest neighbors. Vector databases provide knobs to tune this tradeoff: how much accuracy can you sacrifice for how much speed improvement?

## Indexing Strategies

Different indexing strategies offer different tradeoffs. Understanding the major approaches helps in selecting and tuning vector databases.

Inverted file indexes (IVF) partition vectors into clusters. Each cluster has a centroid—a representative vector. At query time, we find the clusters whose centroids are closest to the query, then search only within those clusters. This dramatically reduces comparisons: instead of searching a million vectors, we search maybe a thousand in the nearest clusters.

The number of clusters and how many to search are key parameters. More clusters means smaller clusters and faster search within each, but we might need to search more clusters to find all nearest neighbors. Fewer clusters means larger clusters and slower search, but better accuracy. Typical configurations search one to ten percent of clusters.

IVF requires training—running clustering on a sample of vectors to determine centroids. This is a one-time cost but can be substantial for large collections. The quality of clustering affects search quality.

Hierarchical Navigable Small World (HNSW) graphs represent vectors as nodes in a multi-layer graph. Each layer is sparser than the one below, enabling navigation from coarse to fine granularity. Search starts at the top layer, finds the approximate region, then drills down through layers to find the nearest neighbors.

HNSW provides excellent search speed with high accuracy. It doesn't require explicit training—the graph builds incrementally as vectors are added. This makes HNSW popular for production systems where data arrives continuously.

The main HNSW parameters are the number of connections per node and the number of layers. More connections mean a more connected graph and potentially better search paths, but larger index size. These parameters tune the speed-accuracy tradeoff.

Product quantization (PQ) compresses vectors for faster comparison and smaller storage. It divides vectors into segments and quantizes each segment independently. Compressed vectors enable faster distance computation and fit more vectors in memory.

PQ trades accuracy for efficiency. The compression is lossy—reconstructed vectors differ from originals. This introduces error in similarity computation. But the efficiency gains can be dramatic, enabling search over collections that wouldn't otherwise fit in memory.

Hybrid approaches combine techniques. IVF-PQ uses clustering for coarse search and product quantization for compressed storage within clusters. HNSW can use quantized vectors for memory efficiency. Real systems often layer multiple techniques.

## Core Vector Database Features

Beyond basic similarity search, vector databases provide features needed for production applications.

Metadata filtering combines vector similarity with attribute-based filtering. "Find documents similar to this query that were published after 2023 and tagged as 'technical.'" This requires indexes on both vectors and metadata, with query planning that efficiently combines them.

Filtering can happen before or after vector search. Pre-filtering restricts the candidate set before similarity computation—efficient if filters are selective, but complex to implement with ANN indexes. Post-filtering runs similarity search first, then applies filters to results—simpler but may return fewer results than requested if many matches are filtered out.

Multi-tenancy isolates data between users or applications. A single vector database might serve multiple applications, each seeing only their own vectors. This requires efficient filtering by tenant while maintaining performance.

Real-time updates handle continuous data changes. Documents are added, modified, and deleted constantly. The index must update without becoming stale or requiring expensive rebuilds. Different indexing strategies handle updates differently—HNSW is naturally incremental; IVF may require periodic retraining.

Horizontal scaling distributes vectors across multiple machines. A billion-vector collection doesn't fit on one server. Sharding partitions vectors; replication provides redundancy. Distributed queries aggregate results from multiple shards.

Persistence and durability ensure data survives failures. Vectors and indexes are stored durably, not just in memory. Recovery after crashes restores the database to a consistent state.

## Major Vector Database Options

The vector database landscape includes purpose-built systems and extensions to existing databases.

Pinecone is a managed vector database service. Users don't operate infrastructure—Pinecone handles scaling, durability, and operations. The managed model simplifies deployment but creates vendor dependency. Pinecone emphasizes ease of use and production reliability.

Weaviate is an open-source vector database with additional AI capabilities. Beyond similarity search, it can call embedding models and integrate with LLMs. Weaviate can be self-hosted or used as a managed service.

Qdrant is a high-performance open-source vector database written in Rust. It emphasizes query speed and supports rich filtering. Qdrant can run embedded in applications, as a service, or in distributed mode.

Milvus is an open-source vector database designed for scale. It handles billions of vectors with distributed architecture. Zilliz provides a managed cloud version. Milvus suits large-scale production deployments.

Chroma positions itself as a developer-friendly embedding database. It's lightweight and easy to get started with, popular for prototyping and smaller applications. Chroma can run in-memory or persist to disk.

PostgreSQL with pgvector extends the familiar PostgreSQL database with vector capabilities. For teams already using PostgreSQL, pgvector adds vector search without introducing new infrastructure. Performance and features are more limited than purpose-built systems but sufficient for many applications.

Elasticsearch and OpenSearch have added vector search capabilities. If you're already using these for text search, dense vector search can complement sparse keyword search.

The choice depends on scale requirements, operational preferences, existing infrastructure, and feature needs. Managed services trade cost for operational simplicity. Open-source systems offer control and customization.

## Designing for Vector Search

Building applications on vector databases requires thoughtful design decisions.

Choosing embedding dimensions involves tradeoffs. Higher dimensions capture more nuance but require more storage and computation. For most applications, embeddings from standard models (768-1536 dimensions) work well. Larger dimensions rarely justify the costs.

Index type selection depends on your priorities. If you need high accuracy and have memory budget, HNSW is often best. If memory is constrained, IVF-PQ compresses effectively. If you need very low latency, tuning index parameters is critical.

Capacity planning estimates storage and compute needs. Each vector requires space for its dimensions—1536 float32 dimensions is about 6KB per vector. A million vectors needs roughly 6GB just for vectors, plus index overhead. Query load determines compute requirements.

Partitioning strategies affect performance at scale. Sharding by tenant keeps each tenant's data together. Sharding by content distributes load but requires scatter-gather queries. The right strategy depends on query patterns.

Caching hot vectors improves performance for common queries. If some vectors are accessed much more often than others, caching avoids repeated retrieval. Query result caching can also help for repeated queries.

## Performance Optimization

Squeezing performance from vector databases requires understanding their internals and tuning appropriately.

Index tuning is often the biggest lever. More connections in HNSW graphs improve accuracy but slow construction and increase memory. More clusters in IVF can improve speed but require searching more clusters for accuracy. Experiment with parameters on representative queries to find the sweet spot.

Batch operations are more efficient than individual operations. Inserting vectors one at a time is much slower than inserting batches. Similarly, batching queries when possible improves throughput.

Memory management affects latency. Indexes that fit in memory serve queries much faster than those requiring disk access. Monitor memory usage and scale up or partition if the working set exceeds available memory.

Query patterns guide optimization. If queries always include certain filters, ensure indexes support those filters efficiently. If queries tend to access certain vector subsets, consider partitioning strategies that keep related vectors together.

Monitoring reveals bottlenecks. Track query latency, throughput, and error rates. Monitor index size and memory usage. Alerting on degradation catches problems early.

## Operational Considerations

Running vector databases in production involves operational challenges beyond query performance.

Backup and recovery protect against data loss. Regular backups of vectors and indexes enable recovery from failures. Test restore procedures to ensure they actually work.

Security requires attention. Authentication and authorization control who can access what data. Encryption protects data in transit and at rest. Network isolation limits exposure.

Upgrades and migrations need planning. Schema changes, index rebuilds, and version upgrades can cause downtime or require careful migration procedures. Test upgrades in staging before production.

Cost management matters for managed services. Costs scale with storage volume, query volume, and cluster size. Monitor costs and optimize by removing unnecessary data, right-sizing clusters, and using appropriate index types.

Multi-region deployment provides geographic distribution for global applications. Replicating vectors across regions reduces latency for distributed users but adds complexity and cost.

## Beyond Basic Similarity Search

Advanced applications extend basic vector search with additional capabilities.

Hybrid search combines vector similarity with keyword matching. Sometimes exact keyword matches are important alongside semantic similarity. Hybrid approaches score both and combine results.

Reranking improves result quality. Initial vector search retrieves a broader set of candidates; a more expensive reranking model reorders them. This two-stage approach balances efficiency and quality.

Clustering discovered structure in vectors. Beyond retrieval, understanding how vectors group reveals patterns in the data. Vector databases may support clustering operations or export data for external clustering.

Analytics on vector collections provides insights. What's the distribution of distances? Are there outliers? How do vectors cluster? Understanding the embedding space helps diagnose retrieval issues.

Integration with ML pipelines connects vector databases to broader systems. Vectors flow from embedding models to storage; retrieval results flow to language models. APIs and SDKs facilitate this integration.

## The Vector Database Ecosystem

Vector databases are one component in a broader ecosystem for semantic search and RAG applications.

Embedding models produce the vectors that databases store. The choice of embedding model affects search quality more than database choice. Databases are agnostic to what the vectors represent.

Orchestration frameworks like LangChain and LlamaIndex simplify building applications that include vector databases. They provide abstractions for loading documents, creating embeddings, storing in vector databases, and retrieving for generation.

Observability tools track system behavior. Logging queries and results enables debugging. Metrics reveal performance characteristics. Tracing shows how queries flow through the system.

Evaluation frameworks measure retrieval quality. Test sets with queries and known relevant documents enable quantitative evaluation. Regular evaluation ensures the system meets quality requirements.

Vector databases have become essential infrastructure for AI applications. They enable the semantic search that makes RAG systems practical, turning theoretical embedding capabilities into efficient retrieval at scale. Understanding their capabilities, limitations, and operational requirements enables building robust applications that find and use information by meaning.
