# Large Language Models: How They Work

Large language models represent a profound shift in artificial intelligence, demonstrating that scaling up a simple objective—predicting the next word—can produce systems capable of conversation, reasoning, coding, and creative writing. Understanding how LLMs work reveals both their remarkable capabilities and their fundamental limitations.

## The Core Insight: Next Token Prediction

At their heart, large language models are prediction engines. Given a sequence of text, they predict what comes next. This seemingly simple task, pursued at massive scale with enormous datasets, produces something that looks remarkably like understanding.

The training objective is straightforward: given all the words so far, predict the probability distribution over the next word. The model sees "The cat sat on the" and learns to predict high probability for "mat," "couch," "floor," and lower probability for unrelated words. Do this across billions of examples from books, websites, conversations, and code, and the model internalizes patterns spanning grammar, facts, reasoning styles, and world knowledge.

The word "token" deserves clarification. Models don't actually process words directly. They process tokens, which are pieces of text that might be words, parts of words, or punctuation. Tokenization breaks text into these pieces using learned vocabularies. Common words become single tokens; rare words are split into subword pieces. The token vocabulary typically ranges from thirty thousand to one hundred thousand entries.

Predicting the next token requires understanding context. To predict that "mat" follows "The cat sat on the," the model must understand English syntax, the typical behaviors of cats, common phrases and idioms. As context grows, predictions require integrating more information. Predicting the ending of a mystery novel requires tracking plot threads, character knowledge, and narrative conventions across thousands of tokens.

This is where scale becomes crucial. Small models can capture local patterns—grammar, common phrases. Larger models capture longer-range dependencies—narrative structure, logical reasoning, factual associations. The largest models demonstrate capabilities that seem qualitatively different from smaller versions, exhibiting emergent behaviors that weren't explicitly trained.

## The Transformer Architecture

Modern LLMs are built on the Transformer architecture, which enables processing long contexts efficiently through its attention mechanism. The Transformer's ability to directly connect any position in the sequence to any other position makes it uniquely suited for language modeling.

A Transformer language model consists of stacked layers, each containing self-attention and feedforward components. The input tokens are first converted to embeddings—dense vectors representing each token. Positional encodings add information about where each token appears in the sequence. These embedded tokens then flow through the Transformer layers.

Self-attention allows each position to gather information from all other positions. But for language modeling, there's a crucial constraint: a token can only attend to tokens that came before it. The model cannot look ahead to future tokens when predicting—that would be cheating. This causal masking ensures the model only uses past context for prediction.

Within each attention head, every token creates a query, key, and value vector. The query represents what information this position is looking for. The key represents what information this position offers. Values represent the actual content to be retrieved. Queries compare against all previous keys, producing attention weights that combine the corresponding values.

Consider the sentence "The trophy doesn't fit in the suitcase because it is too big." When processing "it," attention helps determine what "it" refers to. The query from "it" matches against keys from "trophy" and "suitcase." Learning through training, the model develops attention patterns that correctly resolve such references based on context.

Multiple attention heads learn different types of relationships. One head might track syntactic dependencies, another semantic similarity, another coreference. The multi-head structure enables capturing diverse relationship types simultaneously.

The feedforward layers following attention provide capacity for processing and transformation. These dense layers, applied independently to each position, can be thought of as where knowledge is stored. Research suggests that factual knowledge is encoded in feedforward weights, while attention handles more dynamic routing and combination of information.

Layer normalization and residual connections enable stable training of deep networks. Residual connections add each layer's input to its output, providing gradient highways and allowing layers to learn refinements rather than complete transformations.

## Attention: The Heart of Understanding

The attention mechanism deserves deeper exploration because it's central to how LLMs process and understand text. Attention creates a dynamic, content-based retrieval system where each position can gather relevant information from its context.

The attention computation can be understood as a soft lookup table. Traditional lookup tables use exact key matching—you provide a key and get the corresponding value. Attention uses similarity-based matching—your query is compared against all keys, and you get a weighted combination of values based on how similar each key is to your query.

This softness is powerful. Instead of retrieving exactly one piece of information, attention retrieves a blend based on relevance. Multiple pieces of context can contribute to processing each position, with weights reflecting relative importance.

The quadratic cost of attention—every position attending to every other—becomes problematic for long sequences. Processing a thousand tokens requires a million attention computations per layer. Processing a million tokens would require a trillion computations, which is infeasible. This limits context length and has motivated research into efficient attention variants.

Attention patterns are learned, not programmed. The model discovers through training which contexts are relevant for which predictions. Early layers tend to develop local attention patterns—nearby tokens attending to each other. Later layers develop more global patterns—long-range dependencies and abstract relationships.

Visualizing attention reveals what the model focuses on for different predictions. Certain heads specialize: some track syntactic structures, some handle coreference, some detect semantic similarity. This specialization emerges from training without explicit supervision.

## Tokenization: The Interface Between Text and Model

Before text reaches the model, it must be converted to tokens. Tokenization is the process of breaking text into pieces the model can process. The choice of tokenization scheme significantly impacts model behavior.

Early language models used word-level tokenization, treating each word as a unit. This creates a fixed vocabulary with out-of-vocabulary problems—new or rare words can't be processed. Character-level tokenization avoids this but creates very long sequences and requires more computation.

Modern models use subword tokenization, a middle ground. Algorithms like Byte Pair Encoding (BPE), WordPiece, and SentencePiece learn to segment text into meaningful pieces. Common words become single tokens; rare words are broken into subword units. "Understanding" might be one token, while "reconceptualization" might be split into "re," "concept," "ual," "ization."

The tokenization vocabulary is learned from training data. Starting with character-level segments, the algorithm iteratively merges frequent pairs until reaching a target vocabulary size. The resulting vocabulary captures meaningful units—morphemes, common words, frequent character combinations.

Tokenization has quirks that affect model behavior. The same semantic content can tokenize differently depending on spacing, capitalization, or surrounding context. Numbers often tokenize digit by digit, making arithmetic challenging. Non-English languages may be split into more tokens, requiring more compute for the same content.

The tokenizer defines the model's interface. Different models have different tokenizers that aren't interchangeable. Prompts that work well with one model might tokenize poorly with another, affecting performance in unexpected ways.

## Training at Scale

Training a large language model requires massive computation applied to massive data. The scale of modern LLM training is difficult to grasp—thousands of GPUs running for months, processing trillions of tokens.

The training data typically includes diverse text: books, websites, code, conversations, scientific papers. Data quality matters enormously—models learn whatever patterns exist in training data, including errors, biases, and toxic content. Careful curation, filtering, and deduplication improve resulting model quality.

Training proceeds through gradient descent on the language modeling objective. For each training example—a sequence of tokens—the model predicts each token given the preceding tokens. The loss measures how far predictions fall from the actual tokens. Gradients flow backward through the network, updating parameters to improve predictions.

The mathematics are identical to smaller neural networks, but the engineering challenges multiply. Distributing computation across thousands of GPUs requires sophisticated parallelism strategies. Model parallelism splits the model across devices; data parallelism processes different examples on different devices; pipeline parallelism overlaps computation and communication.

Training stability becomes critical at scale. Small numerical issues that would be negligible in smaller models compound across billions of parameters and trillions of operations. Mixed-precision training uses lower-precision arithmetic for efficiency while maintaining higher-precision for stability-critical operations.

Hyperparameters matter more at scale because experiments are expensive. Learning rate schedules, batch sizes, and optimization choices are often determined through careful experimentation on smaller models, then scaled up.

The compute required to train frontier models doubles roughly every six to twelve months. This scaling continues because performance improves predictably with scale—more parameters and more data yield more capable models, following empirical scaling laws.

## Scaling Laws: The Predictable Power of Size

Research has revealed that LLM performance scales predictably with model size, dataset size, and compute. These scaling laws allow predicting how much capability will emerge from a given training investment.

The loss—how well the model predicts next tokens—decreases as a power law with each scaling factor. Double the parameters, and loss decreases by a predictable fraction. Double the data, similar predictable decrease. These relationships hold across orders of magnitude.

Optimal allocation of compute depends on scale. For a given compute budget, there's an optimal balance between model size and data. Early scaling research suggested spending most compute on larger models; later research suggests more data than previously thought is optimal.

Scaling laws suggest a path forward: more compute produces more capable models. But they don't explain why language modeling at scale produces capabilities like reasoning, coding, and instruction following. These capabilities emerge at certain scales, not present in smaller models.

The emergence of capabilities is not fully understood. Small models might have fragments of an ability but fail to compose them correctly. At sufficient scale, these fragments cohere into functioning capabilities. This phase transition makes predicting when capabilities will emerge challenging.

## From Prediction to Conversation

Base language models predict text continuations. They complete documents, mimic writing styles, and continue patterns. But they don't naturally converse, follow instructions, or avoid harmful outputs. Additional training transforms predictors into assistants.

Supervised fine-tuning teaches models to follow instructions. Human contractors write examples of helpful responses to diverse prompts. The model is trained on this instruction-response data, learning to produce helpful outputs rather than mere continuations.

Reinforcement learning from human feedback (RLHF) further aligns models with human preferences. Human raters compare model outputs, indicating which is better. A reward model learns to predict these preferences. The language model is then trained to maximize predicted reward while staying close to the supervised fine-tuned model.

Constitutional AI and similar approaches reduce reliance on human labeling by using AI feedback. The model critiques its own outputs according to specified principles, generating preference data automatically. This enables iterating alignment more quickly and at lower cost.

These alignment techniques shape model behavior substantially. A base model might produce harmful content if trained on internet text containing it. Alignment training reduces such outputs, teaches refusal behaviors, and encourages helpful, harmless responses.

The alignment process involves tradeoffs. Models must balance helpfulness with safety, capability with controllability. Too restrictive and the model refuses reasonable requests; too permissive and it enables harm. Finding this balance remains an active area of research.

## What LLMs Know and Don't Know

LLMs encode vast knowledge absorbed from training data. They can recall facts, explain concepts, and synthesize information across domains. But this knowledge has important limitations.

Knowledge is frozen at training time. A model trained on data through 2023 doesn't know about 2024 events. Information changes—people die, companies merge, records break—and the model's knowledge becomes stale. This cutoff is a fundamental limitation requiring external knowledge retrieval for current information.

Knowledge is statistical, not guaranteed. The model learned associations between concepts, not verified facts. Popular misconceptions might be well-represented in training data and confidently repeated. Rare but true facts might be poorly learned or confused with similar-sounding false claims.

LLMs lack verification mechanisms. They produce text that patterns in training data suggest should come next, without checking whether claims are true. This leads to hallucination—confident statements that are plausible but false. The model doesn't know that it doesn't know.

The boundary between knowledge and reasoning is blurry. When an LLM solves a math problem, is it retrieving a memorized solution, recognizing a pattern from similar problems, or actually computing? Probably a mixture, varying by problem. This ambiguity makes understanding LLM capabilities challenging.

## Context Windows: Working Memory

The context window is the text the model can process at once—its working memory. Early models had windows of a few thousand tokens; modern models extend to hundreds of thousands or even millions.

Within the context window, the model can attend to any information. Placing relevant documents in context enables the model to answer questions about them. Placing example input-output pairs enables the model to learn tasks without fine-tuning. The context is a powerful interface for dynamic capability.

But context is not memory in the persistent sense. Information in context is only available for the current generation. In a long conversation, earlier exchanges might fall outside the context window and be forgotten. There's no learning from context—the model's weights don't update based on what it sees.

Longer context windows enable new applications. Entire codebases can fit in context for comprehension and editing. Long documents can be processed without chunking. Multi-turn conversations can maintain longer history. But longer contexts are more expensive to process due to attention's quadratic cost.

The position within context affects processing. Information early in long contexts might be attended to less effectively than information near the query—the "lost in the middle" phenomenon. Techniques like retrieval augmentation strategically place the most relevant information near the query.

## Generation: From Probabilities to Text

At inference time, the model generates text by repeatedly predicting the next token and sampling from the resulting distribution. This autoregressive generation continues until a stopping condition is met.

The sampling strategy significantly affects outputs. Greedy decoding always picks the highest-probability token, which can produce repetitive, dull text. Pure random sampling can produce incoherent text by occasionally picking low-probability tokens.

Temperature controls the randomness of sampling. Higher temperature flattens the probability distribution, making unlikely tokens more likely to be chosen. Lower temperature sharpens the distribution, concentrating probability on top choices. Temperature of zero reduces to greedy decoding.

Top-k sampling restricts consideration to the k highest-probability tokens, then samples from this restricted set. This prevents very unlikely tokens from being chosen while maintaining diversity among reasonable choices.

Top-p sampling, also called nucleus sampling, dynamically adjusts the number of tokens considered. It includes tokens until their cumulative probability exceeds p, then samples from this set. This adapts to the distribution shape—considering more tokens when the distribution is flat, fewer when it's peaked.

These parameters—temperature, top-k, top-p—are inference-time controls that users can adjust without modifying the model. Lower temperatures and tighter sampling produce more deterministic, focused outputs. Higher temperatures and looser sampling produce more creative, varied outputs.

Generation is inherently sequential because each token prediction depends on all previous tokens. This creates a latency floor—generating a thousand tokens requires a thousand forward passes. Techniques like speculative decoding attempt to parallelize by guessing multiple tokens ahead and verifying in parallel.

## The Emergent Phenomena

Large language models exhibit behaviors that seem surprising given their simple training objective. Understanding these emergent capabilities—and their limitations—is essential for effective use.

In-context learning allows models to learn from examples provided in the prompt. Show a few examples of a task, and the model performs the task on new inputs. This requires no gradient updates—the model adapts dynamically based on context. How this works mechanically is not fully understood, but it enables remarkable flexibility.

Chain-of-thought reasoning improves performance on complex problems by generating intermediate reasoning steps. Instead of jumping directly to an answer, the model explains its thinking, and this explanation process helps it reach correct answers more often. The reasoning steps provide a form of working memory external to the model's internal state.

Instruction following generalizes beyond training examples. Models learn to follow novel instructions unlike any in training data by abstracting the pattern of instruction-following. This abstraction enables zero-shot performance on new tasks given clear instructions.

These capabilities emerge from the interaction of scale, training data diversity, and architectural choices. They weren't explicitly designed but arose from the pressure to predict text well. Understanding their scope and reliability remains an active research area.

## The Limits of Language Modeling

Despite remarkable capabilities, LLMs have fundamental limitations rooted in their nature as next-token predictors.

They lack persistent memory. Each conversation starts fresh, with no memory of previous interactions beyond what's in context. They can't truly learn from conversations, only simulate learning through what's provided in context.

They lack grounding in the physical world. All knowledge comes from text, not from interacting with reality. They can describe how to ride a bicycle but have no sensorimotor understanding of balance and pedaling. This limits their understanding of physical processes and embodied cognition.

They lack robust reasoning. While they can perform impressive feats of apparent reasoning, they also fail on problems that should be trivial given their capabilities. Their reasoning is pattern matching rather than formal logic, making it unreliable and inconsistent.

They lack genuine understanding of truth. They model what text looks like, not what the world is like. Falsehoods that are well-represented in training data are reproduced fluently. The model has no way to check claims against reality.

Understanding these limitations is essential for effective use. LLMs are powerful tools when used appropriately—for generating drafts, exploring ideas, explaining concepts, writing code. They are unreliable when used as authoritative sources of truth, formal reasoners, or substitutes for expertise.

The remarkable thing about LLMs is that next-token prediction, pursued at sufficient scale, produces systems that seem to understand, reason, and create. The challenging thing is understanding where this seeming ends and real capability begins. This boundary continues to shift as models scale, but it hasn't disappeared.
