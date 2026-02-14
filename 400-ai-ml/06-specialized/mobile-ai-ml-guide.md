---
title: "Mobile AI/ML: Complete Guide to On-Device Inference (2024-2025)"
date: 2025-12-29
type: guide
status: published
tags:
  - mobile
  - topic/ai-ml
  - on-device
  - npu
  - quantization
  - production
  - type/guide
  - level/intermediate
modified: 2026-02-13
reading_time: 24
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
related:
  - "[[ai-ml-overview-v2]]"
  - "[[local-llms-self-hosting]]"
  - "[[android-overview]]"
  - "[[ios-development]]"
  - "[[llm-inference-optimization]]"
---

# Mobile AI/ML: Complete Guide to On-Device Inference

Comprehensive guide covering SDKs, hardware acceleration, mobile-optimized models, quantization techniques, and production patterns for on-device AI/ML as of late 2025.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание ML** | Что такое модели, inference | [[ai-ml-overview-v2]] |
| **Mobile Development** | iOS или Android разработка | [[android-overview]], iOS docs |
| **Оптимизация** | Понимание trade-offs | [[llm-inference-optimization]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Mobile Developer** | ✅ Да | Интеграция AI в приложения |
| **AI/ML Engineer** | ✅ Да | On-device deployment |
| **Product Manager** | ✅ Да | Понимание возможностей и ограничений |
| **Новичок в ML** | ⚠️ Сложно | Сначала [[ai-ml-overview-v2]] |

### Терминология для новичков

> 💡 **On-Device AI** = AI работает прямо на телефоне, без интернета и API

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **On-Device Inference** | Запуск модели на устройстве | **Офлайн калькулятор** — всё считает сам телефон |
| **NPU** | Neural Processing Unit | **AI-процессор** — специальный чип для нейросетей |
| **TOPS** | Trillions of Operations Per Second | **Мощность NPU** — чем больше, тем быстрее AI |
| **LiteRT** | Lite Runtime (бывший TensorFlow Lite) | **Лёгкий движок** — оптимизирован для мобильных |
| **ExecuTorch** | PyTorch для мобильных устройств | **PyTorch на телефоне** — привычный фреймворк, мобильный формат |
| **MLX** | Apple ML framework | **ML для iPhone/Mac** — оптимизирован под Apple Silicon |
| **Quantization** | Сжатие модели | **Уменьшение размера** — модель меньше, работает быстрее |
| **GGUF** | Формат мобильных моделей | **Формат файла** — как MP3 для музыки, GGUF для моделей |
| **tok/s** | Токенов в секунду | **Скорость ответа** — сколько слов генерирует за секунду |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [SDK Comparison](#sdk-comparison)
3. [Hardware Acceleration](#hardware-acceleration)
4. [Mobile-Optimized Models](#mobile-optimized-models)
5. [Quantization Techniques](#quantization-techniques)
6. [Production Patterns](#production-patterns)
7. [Platform Integration](#platform-integration)
8. [Decision Guide](#decision-guide)
9. [References](#references)

---

## Executive Summary

### State of Mobile AI in 2025

Mobile AI has matured from experimental to production-ready:

| Metric | 2023 | 2025 |
|--------|------|------|
| LLM on device | Experimental | Production (Gemma 3n, Llama 3.2) |
| NPU TOPS | 15-20 | 35-73 |
| Model size | 1-2GB max | 4-8GB viable |
| Inference speed | 5-10 tok/s | 20-45 tok/s |

### Key Developments (2024-2025)

1. **LiteRT** (Sep 2024) — TensorFlow Lite rebranded, multi-framework support
2. **ExecuTorch 1.0** (Oct 2024) — Native PyTorch deployment, 50KB runtime
3. **Gemma 3n** (2025) — 2-4GB effective memory, multimodal
4. **NNAPI Deprecated** — Migration to GPU delegates and NPU SDKs
5. **On-device LoRA** — Fine-tuning now possible on mobile GPUs

---

## SDK Comparison

### Overview Matrix

| SDK | Platforms | Format | NPU | GPU | Best For |
|-----|-----------|--------|-----|-----|----------|
| **LiteRT** | Android, iOS, Web | .tflite | Via delegates | Yes | Cross-platform, general |
| **CoreML** | iOS/macOS | .mlmodel | ANE | Metal | iOS-exclusive |
| **ONNX Runtime** | All | .onnx | Via EPs | Yes | Framework agnostic |
| **MediaPipe** | Android, iOS, Web | .task | Via TFLite | Yes | Pre-built tasks |
| **ExecuTorch** | Android, iOS, Embedded | .pte | QNN, CoreML | Vulkan, Metal | PyTorch native |

### LiteRT (TensorFlow Lite)

**Status:** Production-ready, actively developed
**Rebrand:** TensorFlow Lite → LiteRT (September 2024)

```kotlin
// Android: LiteRT inference
val interpreter = Interpreter(loadModelFile("model.tflite"))
interpreter.run(inputBuffer, outputBuffer)
```

**Key Features:**
- Multi-framework: PyTorch, JAX, TensorFlow, Keras
- Minimal runtime: ~300KB
- Hardware delegates: GPU, NNAPI (deprecated), CoreML, Hexagon

**Delegates:**
| Delegate | Platform | Acceleration |
|----------|----------|--------------|
| GPU | Android/iOS | OpenGL, Metal |
| CoreML | iOS | Apple Neural Engine |
| Hexagon | Qualcomm | DSP/NPU |
| XNNPACK | All | CPU optimization |

### CoreML

**Status:** iOS-exclusive, best for Apple devices

```swift
// iOS: CoreML inference
let config = MLModelConfiguration()
config.computeUnits = .all  // Use ANE
let model = try MyModel(configuration: config)
let prediction = try model.prediction(input: inputData)
```

**Optimization Tips:**
1. Use `.all` compute units (best performance)
2. Weight palettization (1-8 bits) for ANE
3. W8A8 quantization for A17 Pro/M4
4. EnumeratedShapes over dynamic inputs

### ONNX Runtime Mobile

**Status:** Cross-platform, framework agnostic

```java
// Android: ONNX Runtime
OrtEnvironment env = OrtEnvironment.getEnvironment();
OrtSession.SessionOptions opts = new OrtSession.SessionOptions();
opts.addXnnpack();  // CPU optimization
OrtSession session = env.createSession(modelPath, opts);
```

**Execution Providers:**
| EP | Platform | Status |
|----|----------|--------|
| CPU | All | Default |
| XNNPACK | Android/iOS | Best for float |
| CoreML | iOS | Stable |
| NNAPI | Android | **DEPRECATED** |
| QNN | Qualcomm | New recommended |

**Known Issue:** Operator coverage gaps — some models need CPU fallback for unsupported ops.

### MediaPipe

**Status:** Best for pre-built ML tasks, experimental for LLM

**Supported Tasks:**
- Vision: Object detection, segmentation, pose
- Audio: Speech recognition
- Text: Classification
- GenAI: LLM inference (experimental)

```kotlin
// Android: MediaPipe object detection
val detector = ObjectDetector.createFromOptions(context, options)
val results = detector.detect(image)
```

**LLM API (Experimental):**
- Models: Gemma 3n, Gemma 2B, Phi-2
- Features: Multimodal, LoRA adapters
- Devices: Pixel 8+, Samsung S23+ recommended

### ExecuTorch

**Status:** Production-ready (v1.0 Oct 2024), PyTorch native

```python
# Export model for mobile
import torch
from executorch.exir import to_edge

model = MyModel()
exported = torch.export.export(model, example_inputs)
edge_program = to_edge(exported)
et_program = edge_program.to_executorch()
```

**Key Advantages:**
- No format conversion needed
- 50KB base runtime
- 12+ hardware backends
- Production-proven at Meta

**Backends:**
| Backend | Vendor | Acceleration |
|---------|--------|--------------|
| XNNPACK | ARM | CPU |
| CoreML | Apple | ANE |
| MPS | Apple | Metal GPU |
| QNN | Qualcomm | Hexagon NPU |
| Vulkan | Cross-platform | GPU |
| NeuroPilot | MediaTek | APU |

---

## Hardware Acceleration

### NPU Comparison Matrix

| SoC | NPU | TOPS | LLM Speed | Power Efficiency |
|-----|-----|------|-----------|------------------|
| Apple A18 Pro | Neural Engine | 35 | ~33 tok/s (8B) | Best |
| Snapdragon 8 Gen 3 | Hexagon | 73 | 15 tok/s (10B) | Excellent |
| MediaTek D9300+ | APU 790 | 46 | 22 tok/s (7B) | Very Good |
| Samsung Exynos 2400 | Custom | 17 | - | Good |
| Google Tensor G4 | Edge TPU | ~15 | 45 tok/s (3.5B) | Good |

### Apple Neural Engine

**Optimization for ANE:**

```swift
// Best practices for CoreML on ANE
let config = MLModelConfiguration()

// 1. Use all compute units
config.computeUnits = .all

// 2. For specific ANE targeting
config.computeUnits = .cpuAndNeuralEngine  // Skip GPU

// 3. Fixed shapes for better optimization
let constraint = MLImageConstraint(
    pixelsWide: 224,
    pixelsHigh: 224
)
```

**Key Techniques:**
1. **Weight palettization** — Best for ANE (1-8 bits)
2. **W8A8 quantization** — int8-int8 compute path on A17+
3. **EnumeratedShapes** — Fixed inputs run faster
4. **Avoid custom ops** — Fall back to CPU

### Qualcomm Hexagon NPU

**QNN Integration:**

```kotlin
// Android: LiteRT with QNN delegate
dependencies {
    implementation("com.qualcomm.qnn:qnn-runtime:2.34.0")
    implementation("com.qualcomm.qnn:qnn-litert-delegate:2.34.0")
}

// Usage
val delegate = QnnDelegate(options)
interpreter.modifyGraphWithDelegate(delegate)
```

**Performance (llama.cpp QNN backend):**
- 7-10x improvement for quantized LLM inference
- Optimized for MULMAT operations

### NPU vs GPU Power Consumption

| Metric | NPU | GPU |
|--------|-----|-----|
| Peak power | 35W | 75W |
| Power savings | 35-70% less | Baseline |
| Latency | Sub-ms | Higher |
| Batch throughput | Lower | Higher |

**When to Use:**
- **NPU:** LLM inference, sustained workloads, battery-critical
- **GPU:** Batch processing, training, graphics-heavy

---

## Mobile-Optimized Models

### LLM Models

| Model | Params | Memory | Performance | Multimodal |
|-------|--------|--------|-------------|------------|
| Gemma 3n E2B | 5B (2B eff) | ~2GB | 1300+ Elo | Yes |
| Gemma 3n E4B | 8B (4B eff) | ~3GB | GPT-4.1-nano | Yes |
| Llama 3.2 1B Q4 | 1B | ~600MB | Basic | No |
| Llama 3.2 3B Q4 | 3B | ~1.5GB | Good | No |
| Phi-3-mini | 3.8B | ~2GB | 69% MMLU | No |
| Qwen3-0.6B | 0.6B | ~400MB | Strong | No |

### Gemma 3n (Google, 2025)

**Architecture: MatFormer**
- Nested smaller models within larger
- Per-Layer Embeddings (PLE)
- Selective parameter activation

**Features:**
- Multimodal: text, image, audio, video
- 140+ languages
- E2B: 2GB RAM, E4B: 3GB RAM

### Llama 3.2 Quantized (Meta, Oct 2024)

**Quantization Techniques:**
1. QAT with LoRA (QLoRA)
2. SpinQuant (post-training)

**Performance:**
| Metric | Improvement |
|--------|-------------|
| Decode speed | 2-4x |
| Prefill speed | 5x |
| Model size | -56% |
| Memory | -41% |

**Device Testing:**
- OnePlus 12: Full support
- Samsung S24+: 1B and 3B
- Samsung S22: 1B only

### Vision Models

| Model | Size | Task | SDK |
|-------|------|------|-----|
| MobileViT | ~6M | Classification | CoreML, TFLite |
| EfficientNet-Lite | 5-25M | Classification | TFLite |
| YOLO Nano/Small | 3-10M | Detection | CoreML, TFLite |
| MobileSAM | ~10M | Segmentation | ExecuTorch |

### Audio Models

| Model | Size | Task | Latency |
|-------|------|------|---------|
| Whisper Tiny | 39M | STT | Real-time |
| Whisper Base | 74M | STT | Real-time |
| OpenWakeWord | ~10M | Wake word | <50ms |

---

## Quantization Techniques

### GGUF Format

**Naming Convention:**
```
Q + [bits] + [type] + [variant]

Q4_0    — 4-bit legacy
Q4_K_M  — 4-bit K-quant medium (recommended)
Q5_K_M  — 5-bit K-quant medium
Q8_0    — 8-bit legacy
```

### Recommended Formats

| Device | RAM | Format | Use Case |
|--------|-----|--------|----------|
| iPhone 15 Pro+ | 8GB | Q5_K_M | Quality priority |
| iPhone 13/14 | 6GB | Q4_K_M | General |
| High-end Android | 12GB+ | Q5_K_M/Q8_0 | Quality |
| Mid-range Android | 8GB | Q4_K_M | General |
| Entry-level | 4-6GB | Q4_K_M (small) | Basic |

### Quality vs Size Trade-offs

| Format | Compression | Quality Loss | Recommendation |
|--------|-------------|--------------|----------------|
| FP16 | 1x | 0% | Development |
| Q8_0 | 2x | ~1% | Quality-critical |
| Q6_K | 2.7x | ~2% | Good balance |
| Q5_K_M | 3.2x | ~3% | Mac/iPad sweet spot |
| Q4_K_M | 4x | ~5% | Best for iPhone |
| Q2_K | 8x | ~20%+ | Not recommended |

### K-Quant vs Legacy

**K-Quant Advantages:**
- Adaptive precision by layer importance
- Super blocks reduce memory overhead
- Better quality at same bit width

### Mobile Quantization Best Practices

1. **Start with Q4_K_M** — Best balance for mobile
2. **Test on real device** — Simulator differs
3. **Measure latency** — Not just accuracy
4. **Consider memory** — Leave room for app
5. **Profile power** — Battery drain matters

---

## Production Patterns

### Hybrid Cloud+Edge Architecture

```
┌─────────────────────┐
│   User Request      │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Confidence Check   │
│  (threshold: 0.8)   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
   High        Low
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│On-Device│ │ Cloud   │
│Inference│ │ Fallback│
└─────────┘ └─────────┘
```

**Fallback Strategies:**
- Confidence-based: prediction < threshold
- Out-of-domain: input doesn't match training
- Timeout-based: local inference too slow

### Model Caching

**Cache Types:**
| Type | Purpose | Implementation |
|------|---------|----------------|
| Model Cache | Loaded models | Keep warm |
| KV Cache | LLM context | Token chunks |
| Prompt Cache | Repeated queries | Hash lookup |
| Semantic Cache | Similar queries | Embedding |

**KV Cache Optimization:**
- 2 orders of magnitude latency reduction
- Token-level granularity
- LCTRU eviction policy

### Model Preloading

```kotlin
// Android: Background preloading
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        CoroutineScope(Dispatchers.IO).launch {
            ModelManager.preload("model.tflite")
        }
    }
}
```

```swift
// iOS: Async preloading
class AppDelegate: UIApplicationDelegate {
    func application(...) -> Bool {
        Task.detached {
            try await ModelManager.shared.preload()
        }
        return true
    }
}
```

### OTA Model Updates

**A/B Partition Strategy:**
```
Partition A (active, v1.0)
Partition B (staging, v1.1)
          ↓
     Validation
          ↓
    Success → Swap A↔B
    Failure → Rollback
```

**Best Practices:**
1. Staged rollouts: 1% → 10% → 100%
2. Automatic rollback on failure
3. Version compatibility checks
4. Device capability tracking

### Privacy & Federated Learning

**Industry Adoption:**
- Google: Gboard, "Hey Google"
- Apple: Siri, Photos
- Meta: AI assistants with FL-DP

**Privacy Techniques:**
| Technique | Protection |
|-----------|------------|
| Differential Privacy | Individual data |
| Secure Aggregation | Model updates |
| Local-only Inference | No data transfer |

### Observability

**Key Metrics:**
| Category | Metrics |
|----------|---------|
| Performance | Latency, throughput |
| Accuracy | Confidence, corrections |
| Resource | Memory, battery, CPU/GPU |
| Health | Drift, staleness, version |

**Tools:**
- Arize AI: LLM observability
- Dynatrace: A/B testing
- Custom: OpenTelemetry integration

---

## Platform Integration

### Android (Kotlin)

```kotlin
// LiteRT setup
class AIService(context: Context) {
    private val interpreter: Interpreter

    init {
        val options = Interpreter.Options().apply {
            addDelegate(GpuDelegate())
            setNumThreads(4)
        }
        interpreter = Interpreter(loadModel(context), options)
    }

    fun predict(input: FloatArray): FloatArray {
        val output = FloatArray(outputSize)
        interpreter.run(input, output)
        return output
    }
}
```

### iOS (Swift)

```swift
// CoreML setup
class AIService {
    private var model: MLModel?

    func load() async throws {
        let config = MLModelConfiguration()
        config.computeUnits = .all
        model = try await MyModel.load(configuration: config)
    }

    func predict(input: MLFeatureProvider) throws -> MLFeatureProvider {
        return try model!.prediction(from: input)
    }
}
```

### Flutter

```dart
// TensorFlow Lite Flutter
import 'package:tflite_flutter/tflite_flutter.dart';

class AIService {
  late Interpreter _interpreter;

  Future<void> load() async {
    _interpreter = await Interpreter.fromAsset('model.tflite');
  }

  List<double> predict(List<double> input) {
    var output = List<double>.filled(outputSize, 0);
    _interpreter.run(input, output);
    return output;
  }
}
```

### React Native

```javascript
// react-native-fast-tflite
import { loadModel } from 'react-native-fast-tflite';

const model = await loadModel('model.tflite');
const output = model.run([inputData]);
```

### Kotlin Multiplatform

```kotlin
// Shared code with expect/actual
expect class AIService() {
    suspend fun load()
    fun predict(input: FloatArray): FloatArray
}

// Android actual
actual class AIService {
    private lateinit var interpreter: Interpreter
    // TFLite implementation
}

// iOS actual
actual class AIService {
    private var model: MLModel? = null
    // CoreML implementation
}
```

---

## Decision Guide

### SDK Selection Flowchart

```
Need mobile AI?
├── iOS only?
│   └── YES → CoreML (best ANE)
│
├── Android only?
│   └── YES → LiteRT (best ecosystem)
│
├── Cross-platform?
│   ├── PyTorch source? → ExecuTorch
│   ├── Max compatibility? → ONNX Runtime
│   └── Pre-built tasks? → MediaPipe
│
└── LLM specifically?
    ├── Production? → ExecuTorch/CoreML
    └── Prototype? → MediaPipe LLM API
```

### Model Selection by Device

| Device Class | Max Memory | Recommended Model |
|--------------|------------|-------------------|
| iPhone 15 Pro+ | 4-6GB | Gemma 3n E4B, Phi-3 |
| iPhone 13/14 | 2-3GB | Gemma 3n E2B, Llama 3.2 3B |
| Flagship Android | 6-8GB | Most models |
| Mid-range Android | 3-4GB | Llama 3.2 3B, Qwen3-1.7B |
| Entry Android | 1-2GB | Qwen3-0.6B, Llama 3.2 1B |

### Quantization Selection

```
Quality priority?
├── YES → Q8_0 or Q5_K_M
└── NO (size/speed priority)
    ├── iPhone → Q4_K_M
    ├── High-end Android → Q5_K_M
    └── Mid-range → Q4_K_M
```

### Hardware Acceleration Selection

```
Model type?
├── Quantized (INT8/4)
│   └── NPU (best efficiency)
│
├── Float32
│   └── GPU or XNNPACK
│
├── LLM
│   └── NPU (sustained low power)
│
└── Batch processing
    └── GPU (throughput)
```

---

## References

### Official Documentation

- [LiteRT (TensorFlow Lite)](https://ai.google.dev/edge/litert)
- [CoreML](https://developer.apple.com/documentation/coreml)
- [ONNX Runtime Mobile](https://onnxruntime.ai/docs/tutorials/mobile/)
- [MediaPipe](https://ai.google.dev/edge/mediapipe)
- [ExecuTorch](https://pytorch.org/executorch/)

### Research Papers

- [Gemma 3n Architecture](https://ai.google.dev/gemma/docs/gemma-3n)
- [Llama 3.2 Quantization](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/)
- [On-Device Language Models Survey](https://arxiv.org/html/2409.00088v1)

### Research Reports (This Guide)

- [Mobile AI SDKs Research](../docs/research/2025-12-29-mobile-ai-sdks.md)
- [NPU Hardware Acceleration](../docs/research/2025-12-29-mobile-npu-acceleration.md)
- [Mobile Models & Quantization](../docs/research/2025-12-29-mobile-models-quantization.md)
- [Production Mobile AI Patterns](../docs/research/2025-12-29-mobile-ai-production.md)

---

*Last updated: 2025-12-29*
*Research depth: 100+ sources across 4 deep research sessions*

---

## Связь с другими темами

**[[ai-ml-overview-v2]]** — Общий обзор AI/ML Engineering даёт контекст, в который вписывается мобильный AI. On-device inference — это одна из стратегий deployment, наряду с cloud API и self-hosted решениями. Понимание общей картины помогает принимать решения о том, какие задачи выносить на устройство, а какие оставить в облаке, учитывая trade-offs между latency, privacy, стоимостью и качеством.

**[[llm-inference-optimization]]** — Серверная оптимизация инференса и мобильная оптимизация решают одну и ту же фундаментальную проблему: memory bandwidth bottleneck. Техники квантизации (AWQ, GPTQ, FP8), описанные в серверном гайде, адаптированы для мобильных платформ в форматах GGUF и K-quant. KV cache management, описанный через PagedAttention на серверах, имеет мобильные аналоги с ещё более жёсткими ограничениями памяти.

**[[android-overview]]** — Android — одна из двух ключевых платформ для on-device AI. Интеграция с LiteRT (TensorFlow Lite), ExecuTorch и QNN delegate для Qualcomm Hexagon NPU описана в данном материале. Гайд по Android даёт общий контекст платформы: lifecycle management, background work, permissions — всё, что влияет на архитектуру мобильного AI-приложения.

---

## Источники и дальнейшее чтение

- **Huyen, C. (2022). *Designing Machine Learning Systems*. O'Reilly.** — Разделы об edge deployment, model compression и оптимизации inference напрямую применимы к мобильному AI. Книга объясняет принципы квантизации, pruning и knowledge distillation с системной точки зрения.

- **Goodfellow, I., Bengio, Y. & Courville, A. (2016). *Deep Learning*. MIT Press.** — Математические основы нейронных сетей, необходимые для понимания того, почему квантизация работает (или не работает) и какие архитектурные решения позволяют запускать модели на устройствах с ограниченными ресурсами.

- **Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer.** — Теоретическая база для понимания trade-offs между точностью и вычислительной сложностью моделей, что критично при выборе формата квантизации (Q4_K_M vs Q8_0) для мобильных устройств.

---

## Проверь себя

> [!question]- Какие SDK и фреймворки используются для on-device AI на Android и iOS?
> Android: MediaPipe (Google, универсальный), TensorFlow Lite (классический), ExecuTorch (Meta, PyTorch models). iOS: Core ML (Apple native), Create ML (обучение), MLX (Apple Silicon optimized). Кросс-платформенные: ONNX Runtime, MediaPipe. Для LLM: llama.cpp через C++ binding.

> [!question]- Какие ограничения существуют для on-device AI и как их обходить?
> Ограничения: размер модели (RAM), latency (CPU/NPU), battery drain, thermal throttling. Обходы: квантизация (INT8/INT4), model pruning, knowledge distillation (маленькая модель учится у большой), NPU delegation, и гибридный подход (простое on-device, сложное в облаке).

> [!question]- Что такое NPU и как он ускоряет AI на мобильных устройствах?
> Neural Processing Unit --- специализированный чип для ML inference. На iPhone: Apple Neural Engine (16-core), на Android: Qualcomm Hexagon, Google Tensor TPU, Samsung NPU. Ускорение 5-10x по сравнению с CPU, при меньшем энергопотреблении. Доступ через Core ML (iOS) или NNAPI (Android).

---

## Ключевые карточки

Какие форматы моделей используются на мобильных устройствах?
?
TFLite (.tflite) для TensorFlow Lite, Core ML (.mlmodel/.mlpackage) для iOS, ONNX (.onnx) кросс-платформенный, ExecuTorch (.pte) для PyTorch Mobile, и GGUF для llama.cpp. Конвертация между форматами через ONNX как промежуточный.

Как работает квантизация для мобильных моделей?
?
Преобразование весов из float32 в int8/int4, сокращение размера модели в 2-4x и ускорение inference. Post-training quantization: после обучения (проще). Quantization-aware training: во время обучения (точнее). Для мобильных --- INT8 стандарт, INT4 для агрессивной оптимизации.

Что такое MediaPipe и какие задачи он решает?
?
Google framework для on-device ML: object detection, face mesh, pose estimation, hand tracking, text classification, LLM inference. Кросс-платформенный (Android, iOS, Web, Python). Включает pre-trained модели и pipeline для custom задач.

Когда использовать on-device AI vs cloud API?
?
On-device: offline access, real-time (camera, audio), privacy-sensitive data, низкая latency (<50ms). Cloud: сложные задачи (GPT-4 level), большие модели, редкие запросы. Гибридный: simple tasks on-device, complex tasks in cloud. Решение зависит от UX и connectivity.

Как оптимизировать battery consumption для on-device AI?
?
Использовать NPU/GPU delegation вместо CPU, batch inference (обрабатывать пачками), throttle частоту inference, model caching (не загружать при каждом вызове), и background processing с low priority. iOS: Energy Gauges в Xcode, Android: Battery Historian.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[local-llms-self-hosting]] | Запуск LLM локально |
| Углубиться | [[llm-inference-optimization]] | Оптимизация inference |
| Смежная тема | [[android-app-startup-performance]] | Производительность мобильных приложений |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI Engineering |

*Проверено: 2026-01-09*
