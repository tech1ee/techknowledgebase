# Research Report: Mobile Models & Quantization (2024-2025)

**Date:** 2025-12-29
**Sources Evaluated:** 30+
**Research Depth:** Deep (comprehensive multi-source)

---

## Executive Summary

Mobile-optimized LLMs and quantization techniques have matured significantly in 2024-2025. Key developments:

1. **Gemma 3n** (Google) — E2B/E4B with 2-4GB memory, multimodal support
2. **Llama 3.2 Quantized** (Meta) — 1B/3B with 2-4x speedup, 56% size reduction
3. **Phi-3/4** (Microsoft) — 3.8B rivaling GPT-3.5, runs on phones
4. **Qwen3-0.6B** (Alibaba) — 0.6B with 100+ languages, Strong-to-Weak distillation
5. **GGUF Q4_K_M** — Best balance of quality vs size for mobile
6. **On-device LoRA** — Now possible with QVAC-fabric-llm and MobileFineTuner

---

## Mobile-Optimized Models Comparison

### LLM Models for On-Device Inference

| Model | Parameters | Memory | Performance | Multimodal | Context |
|-------|------------|--------|-------------|------------|---------|
| Gemma 3n E2B | 5B (2B effective) | ~2GB | 1300+ Elo | Text, Image, Audio, Video | 32K |
| Gemma 3n E4B | 8B (4B effective) | ~3GB | GPT-4.1-nano level | Text, Image, Audio, Video | 32K |
| Llama 3.2 1B (Q4) | 1B | ~600MB | Good for basic tasks | Text only | 8K (128K original) |
| Llama 3.2 3B (Q4) | 3B | ~1.5GB | Competitive | Text only | 8K (128K original) |
| Phi-3-mini | 3.8B | ~2GB | 69% MMLU, 8.38 MT-bench | Text only | 4K/128K |
| Qwen3-0.6B | 0.6B | ~400MB | Strong distilled | Text only | 32K |
| SmolLM3-3B | 3B | ~1.5GB | Outperforms Llama-3.2-3B | Text only | Varies |

### Vision & Multimodal Models

| Model | Size | Capability | Mobile SDK |
|-------|------|------------|------------|
| MobileViT | ~6M | Image classification | CoreML, TFLite |
| EfficientNet-Lite | 5-25M | Image classification | TFLite |
| YOLO (Nano/Small) | 3-10M | Object detection | CoreML, TFLite |
| MobileSAM | ~10M | Segmentation | ExecuTorch |
| Whisper Tiny/Base | 39M/74M | Speech-to-text | CoreML, TFLite |

---

## Detailed Model Analysis

### 1. Google Gemma 3n (2025)

**Architecture Innovation: MatFormer**
> "Gemma 3n models use a Matryoshka Transformer or MatFormer model architecture that contains nested, smaller models within a single, larger model." — [Google AI](https://ai.google.dev/gemma/docs/gemma-3n)

**Key Features:**
- **Per-Layer Embeddings (PLE)** — Reduces memory without quality loss
- **Selective Activation** — Only 2B/4B parameters active at runtime
- **140+ languages** — Trained on diverse multilingual data
- **Multimodal** — Text, image, video, and audio input

**Performance:**
- E4B: First sub-10B model to exceed 1300 Elo on LMArena
- E2B: ~10-15% accuracy drop vs E4B, 2x faster

**SDK Support:**
- LiteRT (.tflite preview)
- MediaPipe LLM API
- Qualcomm, MediaTek, Samsung chip compatibility

---

### 2. Meta Llama 3.2 Quantized (October 2024)

**Quantization Techniques:**
1. **QAT with LoRA (QLoRA)** — Quantization-aware training
2. **SpinQuant** — State-of-the-art post-training quantization

**Quantization Scheme:**
```
Transformer Layers: 4-bit weights (group size 32)
Activations: 8-bit dynamic quantization
```

**Performance Improvements:**
| Metric | Improvement |
|--------|-------------|
| Decode speed | 2-4x |
| Prefill speed | 5x |
| Model size | 56% reduction |
| Memory footprint | 41% reduction |

**Device Testing:**
- OnePlus 12: Full compatibility
- Samsung S24+: 1B and 3B models
- Samsung S22: 1B model only

**Framework:** ExecuTorch with ARM CPU backend

**Limitations:**
- Context reduced to 8K tokens (vs 128K original)
- Quality ~1% lower than BF16

---

### 3. Microsoft Phi-3/Phi-4 (2024)

**Phi-3-mini Specs:**
- 3.8B parameters
- Trained on 3.3T tokens
- 69% MMLU (rivals Mixtral 8x7B)
- 8.38 MT-bench score

> "This model is performing as well as some of the models that are 100 times its size. It does not require large compute hardware and can literally run on your cell phone." — [Microsoft Source](https://news.microsoft.com/source/features/ai/the-phi-3-small-language-models-with-big-potential/)

**Key Advantage:**
- Works offline — ideal for rural areas without connectivity
- MIT License — open source for commercial use

**Limitations:**
- Lower factual knowledge (TriviaQA performance)
- Best for reasoning, not knowledge retrieval

---

### 4. Qwen3-0.6B (April 2025)

**Strong-to-Weak Distillation:**
> "Qwen 3 0.6B, 1.7B, 4B were trained through Strong-to-Weak Distillation, where large Frontier Models (Qwen3-235B, Qwen3-32B) guide training of smaller models." — [GitHub QwenLM](https://github.com/QwenLM/Qwen3)

**Features:**
- 100+ languages/dialects
- Hybrid behavior (deep reasoning ↔ fast responses)
- Runs on entry-level Apple Silicon
- Most downloaded text-gen model on HuggingFace (Dec 2025)

---

### 5. SmolLM3-3B (Hugging Face, 2025)

**Open Source Transparency:**
- Full engineering blueprint published
- Architecture decisions, data mixture, post-training methodology

**Performance:**
- Outperforms Llama-3.2-3B and Qwen2.5-3B
- Competitive with 4B-class models

---

## Quantization Techniques

### GGUF Format Overview

**What is GGUF?**
> "GPT-Generated Unified Format — a binary file format designed for efficient storage and inference of LLMs, optimized for frameworks like llama.cpp." — [Multiple sources]

### GGUF Naming Convention

```
Q + [bits] + [type] + [variant]

Examples:
Q4_0    — 4-bit, legacy linear quantization
Q4_K_M  — 4-bit, K-quant, medium blocks
Q5_K_M  — 5-bit, K-quant, medium blocks
Q8_0    — 8-bit, legacy linear quantization
```

### K-Quant vs Legacy

| Feature | Legacy (Q4_0) | K-Quant (Q4_K_M) |
|---------|---------------|------------------|
| Precision | Uniform | Adaptive by layer |
| Important layers | Same precision | Higher precision |
| Memory overhead | Higher | Lower (super blocks) |
| Quality | Lower | Higher |

### Recommended Quantization for Mobile

| Device | RAM | Recommended Format |
|--------|-----|-------------------|
| iPhone 15 Pro+ | 8GB | Q5_K_M |
| iPhone 13/14 | 6GB | Q4_K_M |
| High-end Android | 12GB+ | Q5_K_M or Q8_0 |
| Mid-range Android | 8GB | Q4_K_M |
| Entry-level | 4-6GB | Q4_K_M (smaller models) |

### Quality vs Compression Trade-offs

| Format | Compression | Perplexity Impact | Use Case |
|--------|-------------|-------------------|----------|
| FP16 | Baseline | 0% | Development/testing |
| Q8_0 | 2x | ~1% | Quality-critical |
| Q6_K | 2.7x | ~2% | Good balance |
| Q5_K_M | 3.2x | ~3% | Sweet spot for Mac/iPad |
| Q4_K_M | 4x | ~5% | Best for iPhone |
| Q4_0 | 4x | ~10-15% | Not recommended |
| Q2_K | 8x | ~20%+ | Emergency only |

### Mobile-Specific Research (2025)

**PTQ for Llama 3.2 3B:**
- 4-bit quantization (BitsAndBytes 'nf4')
- 68.66% reduction in model size
- Successfully runs on standard Android devices

> "INT4 exhibits more noticeable degradation, with perplexity increases of 5-15% compared to FP32. Methods like GPTQ and q4_k_m tend to perform better than simpler 4-bit schemes." — [arXiv](https://www.arxiv.org/pdf/2512.06490)

---

## On-Device Fine-Tuning

### QVAC-fabric-llm

> "First successful fine-tuning runs on mobile GPUs (Mali, Adreno, Apple)." — [Tether Data](https://tether.io/news/tether-data-introduces-qvac-fabric-llm-the-edge-first-llm-inference-runtime-and-generalized-llm-lora-fine-tuning-framework-for-modern-ai-models-on-heterogeneous-gpus-smartphones-laptops-and-server/)

**Features:**
- LoRA fine-tuning in llama.cpp ecosystem
- Supports smartphones, laptops, servers
- Mali, Adreno, Apple GPU backends

### MobileFineTuner

**Capabilities:**
- Full-parameter fine-tuning (Full-FT)
- Parameter-efficient fine-tuning (PEFT/LoRA)
- Federated fine-tuning interfaces

**API Design:**
- High-level APIs abstracting low-level complexity
- Minimal integration effort

### MobiZO (Research)

**Approach:**
1. Parallelized randomized gradient estimator
2. Multi-Perturbed LoRA (MP-LoRA) module
3. ExecuTorch integration for on-device training

### EdgeLoRA (Multi-Tenant)

**Problem:** Serving multiple LoRA adapters on edge devices
**Solution:** Efficient multi-tenant serving system for resource-constrained devices

---

## Model Compression Techniques

### Technique Comparison

| Technique | Size Reduction | Accuracy Impact | Speed Impact | Use Case |
|-----------|---------------|-----------------|--------------|----------|
| Quantization (INT8) | 4x | ~1% | 2-4x faster | General deployment |
| Quantization (INT4) | 8x | ~5-15% | 4-8x faster | Memory-constrained |
| Pruning | 2-10x | ~1-5% | Faster | Structure optimization |
| Distillation | Varies | Minimal | Depends | Training small models |
| Hybrid (all three) | 3-12x | ~2-5% | 3-6x faster | Best results |

### Pruning Methods

**Types:**
1. **Unstructured** — Remove individual weights
2. **Structured** — Remove entire neurons/channels
3. **Dynamic** — Runtime pruning decisions

**Results:**
> "Pruning was found to be excellent in all aspects: model compression, accuracy loss minimization, and delay minimization." — [PMC Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9571348/)

### Knowledge Distillation

**Process:**
```
Teacher Model (Large) → Knowledge Transfer → Student Model (Small)
```

**Benefits:**
- Improves accuracy without size increase
- No additional latency
- Works with other compression techniques

**Real-World Example:**
- Qwen3-0.6B trained from Qwen3-235B/32B teachers
- Gemma 3n uses similar approach

### Hybrid Compression

**Best Practice Combination:**
```
1. Knowledge Distillation (during training)
   ↓
2. Pruning (post-training)
   ↓
3. Quantization (final step)
```

**Results:**
> "Hybrid approach combining pruning, quantization, and knowledge distillation produced a model 3x smaller while achieving 97% accuracy." — [ResearchGate](https://www.researchgate.net/publication/391424111_A_Hybrid_Lightweight_Deep_Learning_Model_for_Edge_Devices_Combining_Knowledge_Distillation_Pruning_and_Quantization)

---

## Mobile Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Quantization | Memory |
|----------|------------------|--------------|--------|
| Chat assistant | Gemma 3n E2B | Q4_K_M | ~2GB |
| Multimodal (text+image) | Gemma 3n E4B | Q5_K_M | ~3GB |
| Coding assistant | Phi-3-mini | Q4_K_M | ~2GB |
| Multilingual | Qwen3-0.6B | Q8_0 | ~600MB |
| Fast responses | Llama 3.2 1B | Q4 | ~600MB |
| Quality priority | Llama 3.2 3B | Q5_K_M | ~2GB |

### By Device

| Device Class | Max Model Size | Examples |
|--------------|----------------|----------|
| iPhone 15 Pro+ (8GB) | 4-6GB | Gemma 3n E4B, Phi-3 |
| iPhone 13/14 (6GB) | 2-3GB | Gemma 3n E2B, Llama 3.2 3B |
| Flagship Android (12GB+) | 6-8GB | Most models |
| Mid-range Android (8GB) | 3-4GB | Llama 3.2 3B, Qwen3-1.7B |
| Entry Android (4-6GB) | 1-2GB | Qwen3-0.6B, Llama 3.2 1B |

---

## Model Availability

### Official Sources

| Model | HuggingFace | LiteRT | ExecuTorch | GGUF |
|-------|-------------|--------|------------|------|
| Gemma 3n | [Preview](https://huggingface.co/google/gemma-3n-E2B-it-litert-preview) | Yes | Yes | Community |
| Llama 3.2 Q | [Official](https://huggingface.co/meta-llama) | Via conversion | Yes | Official |
| Phi-3-mini | [Official](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) | Via conversion | Community | Community |
| Qwen3-0.6B | [Official](https://huggingface.co/Qwen/Qwen3-0.6B) | Via conversion | Community | Community |
| SmolLM3 | [Official](https://huggingface.co/HuggingFaceTB) | Via conversion | Community | Community |

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Google AI - Gemma 3n](https://ai.google.dev/gemma/docs/gemma-3n) | Official | 0.95 | Gemma 3n architecture |
| 2 | [Meta AI - Llama 3.2](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/) | Official | 0.95 | Llama 3.2 launch |
| 3 | [PyTorch - Llama Quantized](https://pytorch.org/blog/unleashing-ai-mobile/) | Official | 0.95 | Quantization details |
| 4 | [Microsoft - Phi-3](https://news.microsoft.com/source/features/ai/the-phi-3-small-language-models-with-big-potential/) | Official | 0.95 | Phi-3 capabilities |
| 5 | [GitHub QwenLM](https://github.com/QwenLM/Qwen3) | Official | 0.90 | Qwen3 training |
| 6 | [Enclave AI - GGUF Guide](https://enclaveai.app/blog/2025/11/12/practical-quantization-guide-iphone-mac-gguf/) | Blog | 0.80 | Practical quantization |
| 7 | [arXiv - Mobile LLM Quantization](https://arxiv.org/html/2512.06490) | Academic | 0.90 | INT4 research |
| 8 | [Tether Data - QVAC](https://tether.io/news/tether-data-introduces-qvac-fabric-llm-the-edge-first-llm-inference-runtime-and-generalized-llm-lora-fine-tuning-framework-for-modern-ai-models-on-heterogeneous-gpus-smartphones-laptops-and-server/) | Official | 0.85 | On-device fine-tuning |
| 9 | [Applied Intelligence - Compression](https://link.springer.com/article/10.1007/s10489-024-05747-w) | Academic | 0.90 | Compression techniques |
| 10 | [SmythOS - Gemma 3n](https://smythos.com/developers/ai-models/gemma-3n-googles-edge-first-model-built-to-do-more-with-less/) | Blog | 0.75 | Gemma 3n overview |

---

## Research Methodology

- **Queries used:** 12+ targeted searches
- **Sources found:** 45+ total
- **Sources used:** 30 (after quality filter)
- **Research duration:** ~35 minutes
- **Focus areas:** Model specs, quantization techniques, on-device fine-tuning, compression
