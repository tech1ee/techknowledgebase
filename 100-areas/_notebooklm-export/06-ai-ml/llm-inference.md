# LLM Inference: Optimization and Efficiency

Inference—the process of generating outputs from a trained model—is where large language models meet users. Every conversation, every completion, every API call requires inference. As LLMs scale to billions of parameters and serve millions of users, efficient inference becomes crucial for cost, latency, and user experience.

## The Anatomy of LLM Inference

Understanding inference optimization requires understanding what happens during generation. LLM inference is fundamentally autoregressive: we generate one token at a time, with each token depending on all previous tokens.

The process begins with a prompt. The prompt tokens are processed together in a forward pass through the model, producing a probability distribution over the next token. We sample from this distribution to select the next token. This token is then appended to the sequence, and the process repeats.

Each forward pass involves substantial computation. The input tokens must be embedded, processed through numerous transformer layers with attention and feedforward operations, and projected to vocabulary probabilities. For a model with billions of parameters, this means billions of floating-point operations per token.

The sequential nature creates a fundamental latency challenge. Generating a hundred tokens requires a hundred serial forward passes. Even if each pass is fast, latency accumulates. Users waiting for responses experience this as time to first token and time between tokens.

Throughput—tokens generated per second across all requests—is also critical. A service handling thousands of concurrent users must maximize how many tokens it can generate with available hardware. Higher throughput means serving more users with less cost.

These twin goals of latency and throughput often conflict. Optimizations that improve throughput may increase latency and vice versa. Understanding this tradeoff is central to inference optimization.

## The Compute and Memory Challenge

LLM inference is both compute-intensive and memory-intensive. Understanding the bottlenecks guides optimization efforts.

Compute intensity comes from the sheer number of operations. Each layer involves matrix multiplications scaling with sequence length, model dimension, and number of attention heads. Multiply this across dozens of layers and billions of parameters, and the compute adds up.

Memory intensity comes from storing the model and intermediate activations. A 70-billion-parameter model requires approximately 140 gigabytes just to store weights in 16-bit precision. Add activations and optimizer states, and memory requirements grow further.

Memory bandwidth is often the actual bottleneck. Moving data between GPU memory and compute units takes time. When models don't fit in cache, we must continually load weights from memory, and the speed of this loading limits throughput. Many inference optimizations aim to reduce memory bandwidth requirements.

The interplay between compute and memory varies by operation. Attention is memory-bound at short sequences (dominated by loading weights) but compute-bound at long sequences (dominated by the quadratic attention computation). Feedforward layers are typically memory-bound. Understanding which regime you're in guides optimization choices.

## Key-Value Caching: Avoiding Redundant Computation

Key-value caching is perhaps the most impactful inference optimization, eliminating redundant computation during autoregressive generation.

Recall that attention computes queries, keys, and values for each position, then uses queries to attend over keys and retrieve values. For each new token, we need its query to attend over all previous keys and values. But the keys and values for previous tokens don't change—they were computed during their generation and remain fixed.

KV caching stores the key and value vectors for all previously generated tokens. When generating the next token, we only compute keys and values for the new token, reusing cached values for all previous tokens. This reduces computation from quadratic in sequence length to linear for each new token.

The impact is substantial. Without caching, generating the hundredth token would require computing attention over all hundred positions' keys and values. With caching, we compute one new key-value pair and attend over ninety-nine cached pairs plus the new one.

But caching has costs. We must store key and value tensors for every layer and every previous token. For long sequences, this cache becomes large—potentially gigabytes. Cache memory limits maximum sequence length and number of concurrent requests.

Managing KV cache efficiently is crucial for serving systems. Techniques include paged attention, which manages cache memory like virtual memory pages, enabling dynamic allocation and sharing. Cache quantization reduces memory per cached element. Cache eviction strategies decide what to discard when memory is tight.

## Batching: Amortizing Overhead

Batching processes multiple requests together, amortizing fixed overhead across requests and improving hardware utilization.

Modern GPUs are massively parallel, with thousands of cores. Processing a single request may not saturate this parallelism, leaving compute unused. Processing multiple requests simultaneously better utilizes available compute.

Static batching groups requests and processes them together. All requests in a batch move through the model in lockstep. This maximizes hardware utilization but requires all requests to complete together, potentially wasting compute if requests have different lengths.

Dynamic batching improves on this. Requests can join a batch mid-processing (when they arrive) and leave when complete (when they hit their end token). This continuous batching keeps hardware busy without forcing long waits.

The tradeoff is complexity versus efficiency. Static batching is simpler to implement but less efficient. Dynamic batching is more efficient but requires sophisticated orchestration. Most production serving systems use some form of dynamic batching.

Batch size optimization balances latency and throughput. Larger batches improve throughput through better utilization but may increase latency as requests wait to be batched or process more slowly due to memory constraints. Finding the sweet spot requires experimentation.

## Quantization: Reducing Precision

Quantization reduces the numerical precision of model weights and activations, decreasing memory requirements and often speeding computation.

Neural network weights are typically stored as 32-bit or 16-bit floating-point numbers. Quantization might represent them as 8-bit integers (INT8) or even 4-bit integers (INT4). This reduces memory by 2-8x, directly impacting how many models fit in GPU memory and how much bandwidth is needed to load weights.

The key question is whether reduced precision impacts output quality. Remarkably, for LLMs, aggressive quantization often has minimal quality impact. Models are relatively robust to small errors in individual weights; what matters is the overall pattern.

Post-training quantization applies quantization to an already-trained model. Various calibration techniques determine how to map floating-point values to integer representations. This is the most common approach as it requires no additional training.

Quantization-aware training incorporates quantization into the training process, allowing the model to adapt to lower precision. This can produce better quality at very low bit widths but requires access to training data and compute.

Different quantization schemes have different tradeoffs. Weight-only quantization keeps activations in higher precision, which is simpler but less beneficial for memory-bound operations. Weight-and-activation quantization reduces both, maximizing benefit but risking more quality degradation.

GPTQ, AWQ, and similar techniques are sophisticated post-training quantization methods designed for LLMs. They achieve 4-bit weight quantization with minimal quality loss, enabling models that normally require expensive GPUs to run on consumer hardware.

## Model Parallelism: Distributing Large Models

When models don't fit on a single device, parallelism distributes them across multiple devices. Different parallelism strategies have different characteristics.

Tensor parallelism splits individual layers across devices. A single matrix multiplication is partitioned, with each device computing part of the result. This requires communication to aggregate partial results but keeps latency similar to single-device execution.

Pipeline parallelism splits the model into stages, with different devices handling different layers. Input flows through stages sequentially. This reduces communication but introduces pipeline bubbles—idle time when devices wait for inputs from previous stages.

Sequence parallelism distributes different positions in the sequence across devices. This is particularly relevant for long sequences where attention computation is substantial. Clever algorithms minimize the communication needed for attention across sequence partitions.

Expert parallelism applies to mixture-of-experts models, where different experts reside on different devices. Routing determines which device handles each input, naturally distributing load.

The choice of parallelism strategy depends on model architecture, hardware topology, and workload characteristics. Production systems often combine multiple strategies, using tensor parallelism within nodes and pipeline parallelism across nodes.

## Speculative Decoding: Parallel Drafting

Speculative decoding attacks the serial nature of autoregressive generation by drafting multiple tokens in parallel and verifying them.

The idea is to use a smaller, faster draft model to generate candidate tokens quickly. The main model then verifies these candidates in a single forward pass. If the candidates match what the main model would have generated, we've generated multiple tokens in the time of one main-model forward pass.

Verification exploits the fact that computing the probability of a known sequence is cheaper than generating it. The main model can evaluate the probability of all draft tokens in parallel, checking whether each would have been selected.

When speculation succeeds—draft tokens are accepted—latency improves dramatically. When it fails, we fall back to normal generation from the point of failure. The speedup depends on how well the draft model predicts the main model.

Draft model selection is crucial. It must be much faster than the main model but accurate enough that speculation usually succeeds. Smaller versions of the same model family often work well. Sometimes the draft model is a fine-tuned version optimized for speed.

Variants include self-speculation, where the main model does its own drafting (perhaps using fewer layers), and tree speculation, which generates multiple draft sequences and verifies them as a tree.

## Efficient Attention Mechanisms

Attention's quadratic complexity with sequence length has motivated research into more efficient alternatives.

Flash Attention is an implementation optimization rather than a new mechanism. It restructures the attention computation to minimize memory movement, computing attention in blocks that fit in fast GPU cache. This dramatically speeds up attention without changing what's computed.

Sparse attention patterns attend only to subsets of positions. Local attention attends to nearby positions. Strided attention attends to every nth position. Combined patterns can approximate full attention with less compute.

Linear attention variants replace the softmax in attention with kernel functions that allow reformulation as linear operations. This reduces complexity from quadratic to linear but may sacrifice some modeling capability.

Sliding window attention limits attention to a fixed window of recent tokens. This works well when recent context is most relevant but may miss long-range dependencies. Some models use sliding windows in most layers with occasional full attention layers.

The right attention variant depends on the application. Full attention is still best for quality on tasks requiring long-range dependencies. Efficient variants trade some capability for speed and memory, worthwhile when context lengths are extreme or resources are limited.

## Inference Serving Systems

Production inference requires more than just model optimization—it requires serving infrastructure that handles load, maintains availability, and manages resources efficiently.

Request routing distributes incoming requests across available resources. Load balancing ensures even utilization. Priority systems may route important requests preferentially.

Queue management handles bursts of traffic. When request rate exceeds processing capacity, queues buffer requests. Queue policies determine ordering—first-come-first-served, priority-based, or deadline-based.

Resource allocation assigns GPU resources to requests. With heterogeneous hardware or multiple model variants, allocation decisions impact both throughput and latency. Dynamic allocation responds to changing demand.

Autoscaling adjusts capacity based on load. When demand increases, additional instances spin up. When demand decreases, instances scale down to save cost. Autoscaling policies balance responsiveness against cost.

Caching can speed repeated requests. If the same prompt is likely to recur, caching its generation avoids redundant computation. Semantic caching might even recognize similar (not identical) prompts.

Monitoring tracks system health and performance. Latency percentiles, throughput, error rates, and resource utilization all matter. Alerting catches problems before they impact users.

## The Cost of Inference

Inference cost is a major consideration for LLM applications. Understanding cost drivers enables cost-effective designs.

Compute cost scales with tokens generated. Longer outputs cost more. Bigger models cost more per token. High throughput amortizes fixed costs but requires substantial upfront capacity.

The cost structure varies by deployment model. Cloud GPU providers charge per hour regardless of utilization—underutilization wastes money. API providers charge per token—you pay only for what you use but at a markup.

Optimization directly impacts cost. A 2x throughput improvement halves compute cost. Quantization enabling smaller GPUs reduces hardware cost. Efficient batching improves utilization.

Prompt length impacts cost significantly. Long system prompts processed on every request add up. Prompt caching or fine-tuning to reduce prompt length can reduce costs.

Architectural choices affect inference cost. Retrieval augmentation may reduce model size needed for a task. Multiple specialized models might be more efficient than one general model. Choosing the right model size for the task avoids paying for unused capability.

## The Future of Inference

Inference optimization continues to evolve as models grow and applications expand.

Hardware specialization produces chips designed specifically for inference. TPUs, Groq's LPUs, and other accelerators offer different tradeoffs than general-purpose GPUs. Purpose-built hardware can dramatically improve efficiency.

Algorithm improvements continue. Better quantization methods achieve lower bit widths with less quality loss. Smarter speculation strategies improve acceptance rates. Novel attention mechanisms reduce complexity.

Systems research tackles serving at scale. Better batching algorithms, smarter scheduling, more efficient memory management—improvements compound to enable serving ever-larger models to ever-more users.

The gap between research models and production deployment continues to close. Techniques that once required specialized expertise become productized in serving frameworks. Optimization that was once the province of large labs becomes accessible to smaller teams.

Understanding inference is crucial for anyone deploying LLMs. The difference between naive and optimized inference can be 10x or more in cost and latency. This difference often determines whether an application is viable. As LLMs become central to more applications, inference optimization becomes not just nice to have but essential for competitive products.
