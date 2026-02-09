# Advanced RAG Techniques: Beyond Basic Retrieval

Basic RAG—embed documents, retrieve by similarity, generate from context—provides a strong foundation but leaves significant room for improvement. Advanced techniques address the limitations of simple RAG, improving retrieval quality, handling complex queries, and enhancing generation. Understanding these techniques enables building RAG systems that handle challenging real-world requirements.

## The Limitations of Basic RAG

Before exploring solutions, we must understand the problems. Basic RAG fails in predictable ways that advanced techniques address.

Single-shot retrieval assumes one query retrieves all needed information. But complex questions may require synthesizing information from multiple documents on different aspects. A question about comparing two products needs information about both products, which might not be retrieved by a single query.

Simple semantic similarity isn't always relevance. Documents about the same topic might be retrieved even if they don't answer the question. A query about troubleshooting a specific error might retrieve general product documentation that mentions similar errors without providing solutions.

Chunk boundaries can split crucial information. If the answer spans two chunks, neither might be retrieved because neither alone is sufficiently relevant. Important context might exist just outside the retrieved chunk.

Query-document mismatch happens when users express queries differently than documents express answers. The query "why won't my app open" might need to match documentation titled "Resolving application launch failures" with different vocabulary.

These limitations aren't fundamental—they're challenges that better techniques can address. The art of advanced RAG is matching techniques to specific problems.

## Hybrid Search: Best of Both Worlds

Hybrid search combines dense vector retrieval with sparse keyword retrieval, capturing both semantic similarity and exact term matches.

Dense retrieval using embeddings captures meaning. "Automobile" and "car" are similar even without shared words. This handles paraphrasing and semantic relationships. But dense retrieval might miss exact keyword matches that matter—product names, error codes, technical terms.

Sparse retrieval using keyword methods like BM25 captures exact term overlap. If the query contains "error 404" and a document contains "error 404," that's a strong signal regardless of overall semantic similarity. Sparse methods excel at exact matches and rare terms.

Hybrid search runs both retrieval methods and combines results. Various combination strategies exist: interleaving results, weighted fusion of scores, or reciprocal rank fusion that combines rankings without calibrating scores.

Reciprocal rank fusion is particularly elegant. Each retrieved document gets a score based on its rank in each retrieval method's results. Higher-ranked documents get higher scores. Scores from different methods simply add together. This avoids the challenge of calibrating similarity scores from different methods.

The weight between dense and sparse affects behavior. More weight on dense emphasizes semantic matching; more weight on sparse emphasizes keyword overlap. The optimal balance depends on your data and queries—experimentation guides the choice.

Hybrid search is often the single most impactful improvement over pure dense retrieval. The complementary strengths of semantic and keyword matching catch what either misses alone.

## Query Transformation

Query transformation modifies user queries before retrieval to improve match quality. The user's raw query may not be optimal for retrieving relevant documents.

Query expansion adds related terms to broaden retrieval. The query "ML models" might expand to "machine learning algorithms neural networks." This helps retrieve relevant documents using related terminology.

Expansion can use synonyms from knowledge bases, terms from relevant documents in a first retrieval pass, or LLM generation of related terms. The risk is topic drift—expanding too broadly retrieves irrelevant documents.

Query reformulation rewrites queries while preserving intent. An LLM can transform a casual query into a more precise form that better matches documentation style. "How do I make it work?" with context becomes "How to configure authentication for the API client library?"

Hypothetical Document Embedding (HyDE) has the LLM generate what a perfect answer might look like, then embeds that hypothetical answer for retrieval. The embedding of an answer-like text might better match relevant documents than the embedding of a question.

Step-back prompting has the LLM consider what higher-level question the user's query relates to. For a specific technical question, the step-back might be a broader concept question. Retrieving for both the specific and broader queries combines focused and background information.

Query decomposition breaks complex queries into subqueries. "Compare pricing and features of A and B" becomes separate queries about A's pricing, B's pricing, A's features, and B's features. Results from all subqueries combine for a comprehensive response.

The choice of transformation depends on query characteristics. Complex multi-part queries benefit from decomposition. Vague queries benefit from expansion. Misaligned vocabulary benefits from reformulation.

## Chunking Strategies

How documents are divided into chunks fundamentally affects what can be retrieved. Poor chunking loses information; good chunking preserves it.

Fixed-size chunking splits text into equal-sized pieces. It's simple and predictable but ignorant of content structure. Sentences might be split mid-thought; related information might span chunks.

Semantic chunking groups sentences by meaning similarity. Adjacent sentences are added to a chunk until adding the next sentence would change the topic significantly. This keeps semantically coherent content together.

Structure-aware chunking respects document structure—sections, paragraphs, code blocks. A section header starts a new chunk. A code example stays together. This preserves meaningful units that the document author created.

Hierarchical chunking creates multiple levels of granularity. A document has chunks at the section level, paragraph level, and sentence level. Different retrieval uses might query different levels. Summary-level questions use coarse chunks; detail questions use fine chunks.

Chunk size tradeoffs are important. Smaller chunks enable more precise retrieval—exactly the relevant sentence, not surrounding fluff. But smaller chunks lose context—the sentence alone might not make sense without surrounding text. Larger chunks provide context but dilute relevance with less relevant content.

A common pattern uses moderate-sized chunks (perhaps a few hundred words) with overlap. Overlap means adjacent chunks share some content, reducing the chance that crucial information falls at a boundary.

Parent-child relationships link chunks to larger context. When a small chunk is retrieved, its parent (the containing section or document) can be added to context. This provides both precision of small chunks and context of larger ones.

Metadata enrichment adds information to chunks beyond their text. Source document, section title, date, author—metadata can support filtering and provides context for the LLM.

## Reranking: Improving Result Quality

Initial retrieval uses efficient approximate methods. Reranking uses more powerful but expensive methods to improve ordering of retrieved results.

The two-stage pattern retrieves a broader set of candidates (maybe 100 documents) with fast retrieval, then reranks to find the best subset (maybe 10 documents) with a more accurate model.

Cross-encoder rerankers score query-document pairs directly. Unlike bi-encoders that embed queries and documents separately, cross-encoders process them together, allowing richer interaction. This is too slow for searching millions of documents but tractable for reranking hundreds.

Cross-encoder models are trained on relevance judgments—query-document pairs labeled as relevant or not. They learn to score pairs by how well the document answers the query, not just semantic similarity.

The improvement from reranking can be substantial. Initial retrieval might place the best document at position 5; reranking might move it to position 1. For RAG, where only top documents go to the LLM, this improvement directly affects answer quality.

LLM-based reranking uses a language model to score relevance. The LLM sees the query and document and outputs a relevance judgment or score. This leverages the LLM's broad understanding but is slower and more expensive than specialized rerankers.

Diversity-aware reranking ensures retrieved documents aren't too similar to each other. If top results all say the same thing, context is wasted on redundancy. Maximal Marginal Relevance (MMR) balances relevance with diversity, preferring documents that are relevant but different from already-selected ones.

## Multi-Step Retrieval

Some questions can't be answered with a single retrieval pass. Multi-step retrieval iteratively refines results.

Iterative retrieval uses results from one retrieval to guide the next. Initial retrieval finds potentially relevant documents. Reading these might reveal that more specific information is needed. A refined query retrieves more targeted results.

Chain-of-thought retrieval interleaves retrieval with reasoning. The LLM reasons about what information it needs, retrieves it, reasons further, retrieves more, and so on. This mirrors how humans research complex questions.

Multi-hop reasoning follows chains of information. To answer "Where was the director of Inception born?", we might first retrieve who directed Inception, then retrieve where that person was born. Neither fact alone answers the question; the chain does.

Retrieval agents use LLMs to decide what to retrieve and when. The agent reasons about the question, formulates retrieval queries, evaluates results, and decides whether to retrieve more or answer. This flexible approach handles diverse query types but requires more computation.

Self-reflection has the LLM evaluate whether retrieved information is sufficient. If not, it generates additional queries to fill gaps. This continues until the LLM judges it has enough information or a limit is reached.

The tradeoff is quality versus latency and cost. Single-shot retrieval is fast and cheap. Multi-step retrieval takes longer and costs more but handles complex questions better.

## Context Assembly and Presentation

How retrieved documents are assembled into context for the LLM affects generation quality.

Relevance ordering places most relevant documents first. If context length limits force truncation, less relevant documents at the end are cut. But recent research suggests LLMs also attend well to context ends, motivating placing important content at beginning and end.

Deduplication removes redundant content. If multiple chunks contain the same information, including all wastes context. Identifying and removing redundancy makes room for diverse information.

Compression reduces content while preserving information. An LLM can summarize verbose documents before including them in context. This fits more information but risks losing important details.

Source attribution maintains links between context content and sources. When the LLM generates a response, it can cite which documents support which claims. This requires tracking provenance through the pipeline.

Context formatting helps the LLM parse the context. Clear separators between documents, labels indicating sources, and consistent structure improve comprehension. Poor formatting confuses the model.

Instructions guide context use. "Answer based only on the provided documents." "If the information isn't in the documents, say so." "Cite document numbers for each claim." These instructions shape how the LLM engages with context.

## Handling Edge Cases

Advanced RAG systems must handle cases where basic approaches fail.

No relevant documents found happens when the knowledge base doesn't cover the query. The system should recognize this rather than hallucinating an answer. Confidence thresholds on retrieval scores, explicit checks for relevance, or letting the LLM judge whether documents answer the question can catch this case.

Conflicting information occurs when different documents disagree. The system might surface this conflict to the user, attempt to reconcile based on source reliability or recency, or acknowledge uncertainty.

Queries outside scope request information the system isn't designed to provide. Clear boundaries and appropriate refusals maintain user trust. An insurance FAQ bot shouldn't attempt medical advice.

Adversarial queries attempt to manipulate the system. Prompt injection attacks embed instructions in retrieved documents hoping the LLM will execute them. Robust systems filter or escape potentially dangerous content.

Temporal queries require reasoning about time. "What's the current policy?" needs the most recent document. "What changed between versions?" needs comparison across time. Metadata and careful retrieval handle temporal reasoning.

## Evaluation and Improvement

Advanced RAG requires advanced evaluation to measure whether techniques actually help.

Component evaluation measures retrieval and generation separately. Retrieval precision and recall assess whether the right documents are found. Generation evaluation assesses whether answers are correct and grounded given the context.

End-to-end evaluation measures the whole system. Given a query, is the final answer correct? This is what users care about but doesn't identify which component is failing.

Evaluation datasets with queries, relevant documents, and correct answers enable quantitative measurement. Creating good evaluation sets requires effort but enables systematic improvement.

A/B testing compares techniques on real traffic. Does hybrid search improve user satisfaction compared to pure dense search? Real-world evaluation complements offline metrics.

Continuous monitoring tracks system performance over time. Query volumes, retrieval latencies, relevance scores, and user feedback reveal trends and problems.

Iterative improvement uses evaluation to guide changes. Identify failure modes, hypothesize improvements, implement and evaluate, repeat. RAG systems improve through cycles of analysis and refinement.

The advanced RAG landscape is rich with techniques addressing specific challenges. The key is matching techniques to problems—understanding what's failing and why, then selecting appropriate solutions. Not every system needs every technique. Start simple, measure, identify problems, and add complexity only where it helps.
