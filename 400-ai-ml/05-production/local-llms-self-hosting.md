---
title: "Локальные LLM и Self-Hosting - Полное Руководство"
tags:
  - topic/ai-ml
  - local
  - ollama
  - llama-cpp
  - self-hosting
  - open-source
  - deepseek
  - qwen
  - llama
  - mobile
  - on-device
  - edge
  - mediapipe
  - executorch
  - mlx
  - type/concept
  - level/intermediate
category: ai-ml
level: advanced
created: 2025-01-15
updated: 2026-02-13
reading_time: 81
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
sources:
  - ollama.com
  - lmstudio.ai
  - github.com/ggerganov/llama.cpp
  - huggingface.co
  - mistral.ai
  - deepseek.com
  - ai.google.dev/edge
  - pytorch.org/executorch
  - developer.apple.com/mlx
related:
  - "[[mobile-ai-ml-guide]]"
status: published
---

# Локальные LLM: Ollama, LM Studio, llama.cpp

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Что такое модели, токены, inference | [[llm-fundamentals]] |
| **Linux/Terminal** | Запуск, настройка, мониторинг | Базовый курс Linux |
| **Hardware** | Понимание GPU, VRAM, quantization | Документация вендоров |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Частично | Начните с Ollama — самый простой вариант |
| **AI Engineer** | ✅ Да | Полный обзор self-hosting опций |
| **DevOps/SRE** | ✅ Да | Production deployment, масштабирование |
| **Privacy-focused** | ✅ Да | Данные не покидают ваш сервер |

### Терминология для новичков

> 💡 **Self-hosting LLM** = запуск AI-модели на своём железе (не через API)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Ollama** | Простой инструмент для запуска LLM | **Docker для LLM** — одна команда и работает |
| **llama.cpp** | Низкоуровневый inference engine | **Движок** — максимум производительности, требует настройки |
| **GGUF** | Формат файлов моделей | **Формат видео** — как MP4 для видео, GGUF для моделей |
| **Quantization** | Сжатие модели с потерей точности | **Сжатие JPEG** — меньше места, чуть хуже качество |
| **Q4_K_M** | Популярный уровень квантизации | **Оптимальный баланс** — хорошее качество, умеренный размер |
| **VRAM** | Видеопамять GPU | **Оперативка видеокарты** — сколько модели туда поместится |
| **tok/s** | Токенов в секунду | **Скорость генерации** — чем больше, тем быстрее ответы |
| **Context Length** | Максимум токенов на вход | **Рабочая память** — сколько текста можно обработать |

---

## TL;DR

> **Локальные LLM** - запуск моделей на своем железе для приватности, скорости (sub-10ms vs 200-800ms API), и экономии.
>
> **Desktop/Server:** Ollama (простейший setup), LM Studio (GUI + MLX), llama.cpp (max performance). Лучшие модели: DeepSeek R1 (reasoning, MIT), Qwen 3 (multilingual, 1M context), Llama 3.3/4 (general), Mistral Small 3.1 (24B, 150 tok/s). RTX 5090 (32GB) - лидер 2025 с 213 tok/s.
>
> **Mobile/Edge (NEW 2025):** Gemma 3n (60-70 tok/s на Pixel, multimodal), Llama 3.2 1B/3B (iPhone/Android), Qwen3 0.6B (edge). Frameworks: MediaPipe (Android), MLX Swift (iOS), ExecuTorch (cross-platform). Реалистичные ограничения: 1-4B модели, 50% батареи за 90 мин, Q4 квантизация обязательна.

---

## История развития Local LLM (2023-2025)

```
+----------------------------------------------------------------------------+
|                    Эволюция Open-Source LLM экосистемы                     |
+----------------------------------------------------------------------------+
|                                                                            |
|  2023: ЗАРОЖДЕНИЕ                                                          |
|  ~~~~~~~~~~~~~~~~                                                          |
|  - Meta выпускает LLaMA 1 и LLaMA 2 (первые качественные open-weight)     |
|  - Появление llama.cpp (Georgi Gerganov) - inference на CPU               |
|  - Формат GGML для квантизации моделей                                    |
|  - Первые версии Ollama упрощают локальный запуск                         |
|  - Ratio: до 284 tokens/parameter (Llama 2)                               |
|                                                                            |
|  2024: УСКОРЕНИЕ                                                           |
|  ~~~~~~~~~~~~~~~                                                           |
|  - GGUF заменяет GGML (лучшая совместимость)                              |
|  - LM Studio получает MLX поддержку для Apple Silicon                     |
|  - Mixtral 8x7B (MoE) показывает эффективность архитектуры                |
|  - Llama 3: ratio 1,875 tok/param (8B на 15T токенов)                     |
|  - Qwen 2.5 и DeepSeek-Coder поднимают планку для coding                  |
|  - vLLM и SGLang для production high-throughput                           |
|                                                                            |
|  2025: ПАРИТЕТ С CLOSED-SOURCE                                             |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~                                              |
|  - DeepSeek R1 (671B MoE) - сравним с OpenAI o1, MIT license              |
|  - Qwen 3: 1M context, thinking mode, Apache 2.0                          |
|  - Llama 4: нативный multimodal (Scout, Maverick)                         |
|  - Mistral Small 3.1: 24B с 150 tok/s, vision                             |
|  - RTX 5090 (32GB VRAM) - 213 tok/s на 8B                                 |
|  - "Год агентов" - модели обучены для tool use                            |
|  - Open-weight догнали closed по качеству                                 |
|                                                                            |
+----------------------------------------------------------------------------+
```

**Ключевой сдвиг 2025**: специализация вместо универсальности. Вопрос изменился с "Какая LLM лучшая?" на "Какая модель идеальна для конкретной задачи?"

---

## Глоссарий терминов

| Термин | Определение |
|--------|-------------|
| **GGUF** | Формат моделей для llama.cpp (замена GGML), оптимизирован для inference |
| **Quantization** | Снижение точности весов (Q2-Q8) для уменьшения размера и ускорения |
| **K-Quants** | Улучшенная квантизация (Q4_K_M, Q5_K_M) с лучшим сохранением качества |
| **VRAM** | Видеопамять GPU для загрузки модели |
| **Unified Memory** | Общая память CPU/GPU на Apple Silicon |
| **Context Length** | Максимальная длина контекста в токенах |
| **Tokens/sec** | Скорость генерации |
| **MoE** | Mixture of Experts - активация части параметров (экономия ресурсов) |
| **Instruct** | Модель fine-tuned для следования инструкциям |
| **Thinking Mode** | Режим "размышления" модели для сложных задач (chain-of-thought) |
| **MLX** | Apple framework для ML на Apple Silicon |

---

## Теоретические основы

> **Self-hosting LLM** — запуск языковых моделей на собственной инфраструктуре (on-premises, private cloud), обеспечивающий полный контроль над данными, латентностью и стоимостью inference. Это альтернатива Model-as-a-Service (MaaS), обоснованная при высоких объёмах или строгих требованиях к privacy.

Возможность self-hosting стала реальной благодаря нескольким теоретическим прорывам:

| Прорыв | Авторы | Вклад |
|--------|--------|-------|
| **Quantization** | Dettmers et al. (2022), NeurIPS | INT8/INT4: модель 70B в 40GB → 10GB VRAM |
| **GGUF format** | Gerganov (2023), llama.cpp | Унифицированный формат для квантизованных моделей |
| **PagedAttention** | Kwon et al. (2023), vLLM | 2-4x больше concurrent requests |
| **Distillation** | Hinton et al. (2015) | Transfer знаний из большой модели в маленькую |
| **Open-weight movement** | Meta (Llama), DeepSeek, Mistral | Модели уровня GPT-4 в open access |

> **Экономический порог self-hosting**: при стоимости GPU-инстанса ~$2/час (A100 80GB) и средней стоимости API-вызова $0.01, точка безубыточности — **~200 запросов/час** (без учёта DevOps overhead). При >1000 запросов/час self-hosting экономит 60-80%.

**Quantization — ключевая технология:**

| Уровень | Bits | Размер 7B | Размер 70B | Потеря качества |
|---------|------|-----------|------------|-----------------|
| FP16 | 16 | 14 GB | 140 GB | Baseline |
| INT8 | 8 | 7 GB | 70 GB | <0.5% |
| **Q4_K_M** | 4.5 | ~4 GB | ~40 GB | <1% |
| Q2_K | 2.5 | ~2.5 GB | ~25 GB | 3-5% |

Теоретическое обоснование quantization: распределение весов обученной модели имеет низкую энтропию (большинство весов близки к нулю). По теореме Шеннона, такое распределение можно кодировать значительно меньшим числом бит без существенной потери информации.

См. также: [[llm-inference-optimization|Inference Optimization]] — оптимизация, [[mobile-ai-ml-guide|Mobile AI]] — on-device inference, [[ai-cost-optimization|Cost Optimization]] — экономика.

---

## Зачем локальные LLM?

```
+----------------------------------------------------------------------------+
|                        Cloud vs Local LLM (2025)                           |
+----------------------------------------------------------------------------+
|                                                                            |
|  CLOUD API (GPT-4o, Claude 3.5)      LOCAL LLM (Ollama, LM Studio)        |
|                                                                            |
|  + Лучшее качество (пока)            + 100% приватность данных            |
|  + Нет затрат на железо              + Нет costs per token                |
|  + Всегда latest version             + Latency sub-10ms (vs 200-800ms)    |
|  + Простой старт                     + Работает офлайн                    |
|                                       + Полный контроль и кастомизация    |
|  - $0.01-0.15/1K tokens              + Fine-tuning возможен               |
|  - Data отправляется наружу                                               |
|  - Rate limits                        - Требует GPU/железо                |
|  - Latency 200-800ms                  - Качество чуть ниже GPT-4o         |
|  - Зависимость от провайдера          - Нужно обновлять модели            |
|                                                                            |
|  КОГДА ВЫБИРАТЬ LOCAL:                                                     |
|  - Приватные данные (медицина, финансы, персональные документы)           |
|  - Высокий объем запросов (1-10M+ токенов/день - ROI 6-12 месяцев)       |
|  - Низкая latency критична (real-time applications)                       |
|  - Офлайн работа обязательна                                              |
|  - Кастомизация/fine-tuning под домен                                     |
|  - Compliance требования (данные не покидают инфраструктуру)              |
|                                                                            |
+----------------------------------------------------------------------------+
```

**Экономика 2025**: При обработке 1-10M токенов ежедневно, single RTX 4090/5090 с quantized моделями окупается за 6-12 месяцев по сравнению с API.

---

## 1. Hardware Requirements

### Расчет VRAM

```
+----------------------------------------------------------------------------+
|                       VRAM Calculation Formula                              |
+----------------------------------------------------------------------------+
|                                                                            |
|  VRAM (GB) = (Parameters x Bits / 8) x 1.2 + KV Cache                     |
|                                                                            |
|  Пример: Llama 3.3 70B в разных форматах:                                 |
|                                                                            |
|  FP16 (16 bit): 70 x 16/8 x 1.2 = 168 GB   (datacenter only)             |
|  INT8 (8 bit):  70 x 8/8 x 1.2  = 84 GB    (multi-GPU)                   |
|  Q4 (4 bit):    70 x 4/8 x 1.2  = 42 GB    (2x RTX 4090)                 |
|  Q3 (3 bit):    70 x 3/8 x 1.2  = 32 GB    (single RTX 5090)             |
|                                                                            |
|  + KV Cache для context (зависит от длины контекста)                      |
|                                                                            |
|  КРИТИЧНО: Если модель + KV cache > VRAM:                                 |
|  Скорость падает с 50-100 tok/s до 2-5 tok/s (CPU spill)                 |
|  Лучше меньшая модель в VRAM, чем большая с offload                      |
|                                                                            |
+----------------------------------------------------------------------------+
```

### GPU Recommendations (2025)

| GPU | VRAM | Модели | Tokens/sec | Цена USD | Примечание |
|-----|------|--------|-----------|----------|------------|
| RTX 4060 Ti 16GB | 16GB | 7-13B (Q4) | 25-35 | ~$500 | Entry-level для разработки |
| RTX 3090 | 24GB | 13-32B (Q4) | 25-40 | ~$800-900 (used) | Best value 24GB |
| RTX 4090 | 24GB | 32B (Q4) | 30-50 | ~$1,600 | Проверенный выбор |
| **RTX 5090** | **32GB** | **32B (Q5), 49B (Q4)** | **61-213** | **~$2,000** | **Новый лидер 2025** |
| 2x RTX 4090 | 48GB | 70B (Q4) | 20-30 | ~$3,200 | Multi-GPU setup |
| Intel Arc B580 | 12GB | 7-8B | 15-25 | ~$250 | Budget experimentation |

**Сравнение RTX 5090 vs RTX 4090:**
- VRAM: 32GB vs 24GB (+33%)
- Bandwidth: 1,792 GB/s vs 1,010 GB/s (+77%)
- 8B модели: 213 tok/s vs 128 tok/s (+67%)
- 32B модели: 61 tok/s (RTX 5090 позволяет запускать)

### Apple Silicon Performance (2025)

```
+----------------------------------------------------------------------------+
|                  Apple Silicon + MLX Performance                            |
+----------------------------------------------------------------------------+
|                                                                            |
|  UNIFIED MEMORY ADVANTAGE:                                                 |
|  CPU и GPU делят память без копирования - идеально для LLM                |
|                                                                            |
|  Chip          Memory BW    8B Model (Q4)    Рекомендуемые модели         |
|  ----------------------------------------------------------------         |
|  M2            100 GB/s     ~6.5 tok/s       3-7B                         |
|  M2 Pro        200 GB/s     ~13 tok/s        7-8B                         |
|  M2 Max        400 GB/s     ~25 tok/s        8-14B                        |
|  M3 Pro        150 GB/s     ~12 tok/s        7-8B                         |
|  M3 Max        400 GB/s     ~28 tok/s        8-14B                        |
|  M4            120 GB/s     ~10 tok/s        7-8B                         |
|  M4 Pro        200 GB/s     ~16 tok/s        8-14B                        |
|  M4 Max        550 GB/s     ~35 tok/s        14-32B                       |
|  M5 (2025)     153+ GB/s    19-27% faster    +4x TTFT с Neural Accel     |
|                                                                            |
|  MLX vs llama.cpp на Apple Silicon:                                       |
|  MLX (~230 tok/s) > llama.cpp (~150 tok/s) > Ollama (20-40 tok/s)        |
|                                                                            |
|  Рекомендация: LM Studio с MLX backend для Mac                            |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Рекомендуемые конфигурации 2025

```
+----------------------------------------------------------------------------+
|                       Recommended Setups 2025                               |
+----------------------------------------------------------------------------+
|                                                                            |
|  ENTRY ($500-800):                                                         |
|  - GPU: RTX 4060 Ti 16GB или Intel Arc B580                               |
|  - Model: Qwen3 8B, Mistral 7B, DeepSeek R1 7B                            |
|  - Tool: Ollama                                                            |
|  - Speed: 25-35 tok/s                                                      |
|  - Use: Тестирование, обучение, простые задачи                            |
|                                                                            |
|  DEVELOPER ($1,000-1,500):                                                 |
|  - GPU: Used RTX 3090 (24GB) или Mac M3/M4 Pro                            |
|  - Model: Qwen3 14B, DeepSeek R1 14B, Mistral Small 3.1                   |
|  - Tool: Ollama + Open WebUI / LM Studio (Mac)                            |
|  - Speed: 30-50 tok/s                                                      |
|  - Use: Разработка, RAG, coding assistant                                 |
|                                                                            |
|  POWER USER ($2,000-3,000):                                                |
|  - GPU: RTX 5090 (32GB) или RTX 4090                                      |
|  - Model: Qwen3 32B, DeepSeek R1 32B, Llama 3.3 70B (Q3)                  |
|  - Tool: Ollama + Open WebUI                                               |
|  - Speed: 30-60 tok/s                                                      |
|  - Use: Production-ready local inference                                   |
|                                                                            |
|  ENTERPRISE:                                                               |
|  - GPU: 2x RTX 4090/5090, H100, MI300X                                    |
|  - Model: Llama 3.3 70B, DeepSeek R1 (full), Qwen3 235B                   |
|  - Tool: vLLM, TGI (production throughput)                                |
|  - Speed: 15-30 tok/s (70B), optimized for throughput                     |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 2. Топ Open-Source модели (2025)

### Сравнение моделей

```
+----------------------------------------------------------------------------+
|                   Open Source LLM Comparison 2025                           |
+----------------------------------------------------------------------------+
|                                                                            |
|  Model               Size      License      Best For                       |
|  -------------------------------------------------------------------------  |
|  DeepSeek R1         671B*     MIT          Reasoning, Math, Code         |
|  DeepSeek V3.2       ~200B*    MIT          Code, large projects          |
|  Llama 4             ~400B*    Llama        Multimodal, general           |
|  Llama 3.3           70B       Llama        General, широкая ecosystem    |
|  Qwen3               235B*     Apache 2     Multilingual, 1M context      |
|  Qwen3-Coder         ~480B*    Apache 2     Code generation (SOTA)        |
|  Mistral Small 3.1   24B       Apache 2     Fast (150 tok/s), vision      |
|  Phi-4               14B       MIT          Efficient, research           |
|  Gemma 2             27B       Apache 2     Instruction following         |
|                                                                            |
|  * MoE - активных параметров значительно меньше                           |
|                                                                            |
|  Quality Ranking (бенчмарки 2025):                                        |
|  DeepSeek R1 ~ GPT-4o > Qwen3 235B > Llama 3.3 70B > Mistral Small 3.1   |
|                                                                            |
+----------------------------------------------------------------------------+
```

### По задачам (2025)

| Задача | Лучший выбор | Альтернатива | VRAM (Q4) |
|--------|--------------|--------------|-----------|
| General Chat | Llama 3.3 70B | Qwen3 32B | 40GB / 18GB |
| Coding | DeepSeek V3.2, Qwen3-Coder | NVIDIA Nemotron 9B | varies / 6GB |
| Reasoning/Math | DeepSeek R1 | Qwen3 (thinking mode) | 40GB+ |
| Multilingual | Qwen3 (29+ языков) | Llama 3.3 | varies |
| Long Context | Qwen3 (1M tokens) | Llama 3.1 (128K) | varies |
| Vision | Mistral Small 3.1, Qwen3-VL | Llava | 16GB |
| Edge/Mobile | Phi-4, Gemma 2B | Qwen3 0.5B | 2-4GB |
| Fast Response | Mistral Small 3.1 | Qwen3 8B | 16GB |
| RAG | Qwen3, Mistral | Llama 3.3 | varies |

### DeepSeek R1 - детальный разбор

```bash
# DeepSeek R1 - лучший open-source reasoning model (MIT license)
# Сравним с OpenAI o1, но открытый и бесплатный

# Distilled версии (на базе Qwen/Llama):
ollama run deepseek-r1:1.5b    # ~1GB  VRAM, базовый reasoning
ollama run deepseek-r1:7b      # ~4GB  VRAM, хороший баланс
ollama run deepseek-r1:8b      # ~5GB  VRAM, Llama-based
ollama run deepseek-r1:14b     # ~8GB  VRAM, сильный reasoning
ollama run deepseek-r1:32b     # ~18GB VRAM, продвинутый
ollama run deepseek-r1:70b     # ~40GB VRAM, топовый distilled

# Полная версия (671B MoE, 37B активных параметров):
# Требует 48GB+ VRAM для Q4 (или datacenter: 8x H100)
# Можно запустить на Mac Studio M2 Ultra 192GB (~$5.6k)
# Или использовать 1.58-bit quantization (131GB)
```

**Hardware requirements для DeepSeek R1:**
- 1.5B: 6GB VRAM (RTX 3060)
- 7B/8B: 8GB VRAM (RTX 4060)
- 14B: 12-16GB VRAM (RTX 4070 Ti)
- 32B: 24GB VRAM (RTX 4090)
- 70B distilled: 48GB+ (2x RTX 4090)
- 671B full: datacenter или Mac Studio 192GB

### Qwen3 - ключевые возможности

```bash
# Qwen3 - Apache 2.0, thinking mode, до 1M context

# Dense модели:
ollama run qwen3:0.6b     # Edge/mobile
ollama run qwen3:4b       # Быстрый, 8GB RAM достаточно
ollama run qwen3:8b       # 25+ tok/s на ноутбуке
ollama run qwen3:14b      # Баланс качества/скорости
ollama run qwen3:32b      # Высокое качество

# MoE модели (эффективнее):
ollama run qwen3:30b-a3b  # 30B total, 3B active

# Режимы работы:
# Thinking Mode - для сложных задач (math, reasoning)
# Non-thinking Mode - быстрые ответы (chat)
# Переключение внутри одной модели!

# Qwen3-2507 (обновление августа 2025):
# - 1M токенов context
# - Улучшенный thinking
# - Варианты: 235B-A22B, 30B-A3B, 4B
```

### Mistral Small 3.1 - sweet spot

```bash
# 24B параметров, 150 tok/s, vision, 128K context
# Помещается на RTX 4090 или 32GB MacBook (quantized)

ollama run mistral-small:24b

# Преимущества:
# - 81% MMLU (сравнимо с GPT-4o Mini)
# - 3x быстрее чем Llama 3.3 70B на том же железе
# - Vision понимание (изображения)
# - Apache 2.0 license
# - Оптимизирован для function calling

# Идеально для:
# - Fast-response chatbots
# - Low-latency tool calling
# - Fine-tuning под домен
# - Локальный inference с приватными данными
```

### Рекомендации по выбору для 8GB VRAM

```
+----------------------------------------------------------------------------+
|                    Best Models for 8GB VRAM (2025)                          |
+----------------------------------------------------------------------------+
|                                                                            |
|  TOP PICKS (по данным r/LocalLLaMA и бенчмаркам):                         |
|                                                                            |
|  1. Qwen3 8B (Standard)    - лучший all-around                            |
|  2. Qwen3 8B (Reasoning)   - math и сложные задачи                        |
|  3. NVIDIA Nemotron Nano 9B - лучший для кода                             |
|  4. DeepSeek R1 0528 Qwen3 8B - сильный reasoning                         |
|  5. Granit 3.3 Instruct 8B - хороший general purpose                      |
|  6. Ministral 8B           - быстрый и качественный                       |
|                                                                            |
|  ПО ЗАДАЧАМ:                                                               |
|  - Math/Reasoning: Qwen3 8B (Reasoning) или DeepSeek R1 8B                |
|  - Coding: NVIDIA Nemotron Nano 9B (Reasoning)                            |
|  - General: Qwen3 8B (Standard) или DeepSeek R1 Distill Llama 8B          |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 3. Ollama

### Установка

```bash
# macOS / Linux (одна команда)
curl -fsSL https://ollama.com/install.sh | sh

# Windows - скачать installer с ollama.com

# Docker (базовый)
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Docker с NVIDIA GPU
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama

# Проверка установки
ollama --version
```

### Основные команды

```bash
# Скачать и запустить модель (одной командой)
ollama run llama3.3:70b
ollama run qwen3:32b
ollama run deepseek-r1:14b
ollama run mistral-small:24b

# Управление моделями
ollama list                    # Список установленных
ollama pull qwen3:8b           # Скачать без запуска
ollama rm llama3.3:70b         # Удалить модель
ollama show qwen3:8b           # Информация о модели
ollama cp qwen3:8b my-qwen     # Копировать/переименовать

# Сервер
ollama serve                   # Запуск сервера (автоматически)

# API запрос
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:8b",
  "prompt": "Explain quantum computing",
  "stream": false
}'
```

### Новые фичи Ollama 2025

```
+----------------------------------------------------------------------------+
|                      Ollama Updates 2025                                    |
+----------------------------------------------------------------------------+
|                                                                            |
|  СЕНТЯБРЬ 2025:                                                            |
|  - New Model Scheduling - меньше OOM crashes, лучше multi-GPU             |
|  - Cloud Models Preview - запуск больших моделей на datacenter            |
|  - Web Search API - встроенный поиск (free tier)                          |
|                                                                            |
|  МАЙ 2025:                                                                 |
|  - Streaming with Tool Calling - real-time tools                          |
|  - Thinking Toggle - контроль reasoning mode                              |
|  - Structured Outputs - JSON schema constraints                           |
|                                                                            |
|  ОКТЯБРЬ 2025:                                                             |
|  - OpenAI gpt-oss-safeguard (20B/120B safety models)                      |
|  - MiniMax M2 - coding и agentic workflows                                |
|  - Qwen3-Coder-480B, GLM-4.6, Qwen3-VL multimodal                        |
|  - NVIDIA DGX Spark optimization                                          |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Создание кастомной модели

```dockerfile
# Modelfile
FROM qwen3:14b

# Системный промпт
SYSTEM """
Ты эксперт по Python программированию.
Всегда предоставляй работающие примеры кода с комментариями.
Объясняй код понятным языком. Используй type hints.
"""

# Параметры генерации
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
PARAMETER stop "<|im_end|>"

# Template (для Qwen3)
TEMPLATE """
{{- if .System }}
<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
```

```bash
# Создание и использование
ollama create python-expert -f Modelfile
ollama run python-expert "Write async web scraper with aiohttp"
```

### Python SDK

```python
import ollama

# Простой запрос
response = ollama.chat(
    model='qwen3:14b',
    messages=[
        {'role': 'user', 'content': 'Explain transformer architecture'}
    ]
)
print(response['message']['content'])

# Streaming
for chunk in ollama.chat(
    model='qwen3:14b',
    messages=[{'role': 'user', 'content': 'Write a haiku about AI'}],
    stream=True
):
    print(chunk['message']['content'], end='', flush=True)

# Thinking mode (Qwen3)
response = ollama.chat(
    model='qwen3:14b',
    messages=[
        {'role': 'user', 'content': 'Solve: what is 23 * 47 + 156 / 12?'}
    ],
    options={'think': True}  # Включить reasoning
)

# Structured Output (JSON)
response = ollama.chat(
    model='qwen3:14b',
    messages=[{'role': 'user', 'content': 'List 3 programming languages'}],
    format={
        'type': 'object',
        'properties': {
            'languages': {
                'type': 'array',
                'items': {'type': 'string'}
            }
        }
    }
)

# Embeddings
embedding = ollama.embeddings(
    model='nomic-embed-text',
    prompt='The quick brown fox'
)
print(f"Embedding dimension: {len(embedding['embedding'])}")

# List models
models = ollama.list()
for model in models['models']:
    size_gb = model['size'] / (1024**3)
    print(f"{model['name']}: {size_gb:.1f} GB")
```

### OpenAI-compatible API

```python
from openai import OpenAI

# Ollama как drop-in замена OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="not-needed"  # Любое значение
)

# Chat completions
response = client.chat.completions.create(
    model="qwen3:14b",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function for binary search"}
    ],
    temperature=0.7,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Function calling (tool use)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="mistral-small:24b",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)
```

---

## 4. LM Studio

### Преимущества

```
+----------------------------------------------------------------------------+
|                       LM Studio Features 2025                               |
+----------------------------------------------------------------------------+
|                                                                            |
|  CORE FEATURES:                                                            |
|  + Красивый GUI для управления моделями                                   |
|  + Интеграция с Hugging Face (поиск и скачивание)                         |
|  + Встроенный chat interface                                               |
|  + Local server с OpenAI-compatible API                                   |
|  + Автоматический выбор квантизации под железо                            |
|  + Мультиплатформенный (Mac, Windows, Linux)                              |
|                                                                            |
|  2025 UPDATES:                                                             |
|  + 1000+ pre-configured моделей в Enhanced Model Library                  |
|  + Team collaboration - multi-user management                             |
|  + Advanced monitoring - performance metrics                              |
|  + Plugin Ecosystem - third-party интеграции                              |
|  + Mobile Companion - iOS/Android для remote management                   |
|  + RTX 50-series support (CUDA 12.8)                                      |
|                                                                            |
|  APPLE SILICON (MLX):                                                      |
|  + Нативная MLX поддержка - быстрее чем llama.cpp на Mac                 |
|  + MLX модели используют меньше памяти                                    |
|  + До 230 tok/s (vs 150 tok/s llama.cpp)                                 |
|                                                                            |
|  ЛУЧШЕ ВСЕГО ДЛЯ:                                                          |
|  - Начинающих пользователей                                               |
|  - Тестирования разных моделей                                            |
|  - Пользователей Mac (MLX)                                                |
|  - Визуального сравнения квантизаций                                      |
|  - Быстрого прототипирования                                              |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Использование

1. Скачать с [lmstudio.ai](https://lmstudio.ai)
2. Search -> Найти модель (Hugging Face интеграция)
3. Выбрать квантизацию:
   - Q4_K_M - рекомендуется для большинства
   - Q5_K_M - если VRAM позволяет
   - Q8_0 - максимальное качество
4. Download -> Load в Chat или Server mode

### API Server

```python
# LM Studio server mode
# 1. Загрузить модель
# 2. Local Server tab -> Start Server
# 3. Default port: 1234

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # Любой ключ
)

# Работает идентично OpenAI API
response = client.chat.completions.create(
    model="local-model",  # Имя загруженной модели
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain machine learning in simple terms"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### Ollama vs LM Studio - когда что выбирать

| Критерий | Ollama | LM Studio |
|----------|--------|-----------|
| Interface | CLI | GUI |
| License | MIT (open-source) | Proprietary freeware |
| Apple Silicon | Хорошо | Лучше (MLX) |
| NVIDIA GPU | Хорошо | Хорошо |
| Server mode | Встроен | Встроен |
| Model management | CLI команды | Visual browser |
| Scripting/Automation | Идеально | Ограничено |
| Privacy concerns | Open-source | Closed-source |
| Learning curve | Средняя | Низкая |

**Рекомендация:**
- **Developer/Automation**: Ollama
- **Visual tinkerer/Mac user**: LM Studio
- **Privacy-conscious**: Ollama (open-source)

---

## 5. llama.cpp

### Для максимальной производительности

```bash
# Клонирование
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# Сборка с CUDA (NVIDIA)
make GGML_CUDA=1

# Сборка с Metal (Apple Silicon)
make GGML_METAL=1

# Сборка с ROCm (AMD)
make GGML_HIP=1

# Сборка с Vulkan (кроссплатформенный)
make GGML_VULKAN=1

# CPU only (AVX2 recommended)
make
```

### Запуск модели

```bash
# Скачать GGUF модель с Hugging Face
# Популярные источники: TheBloke, официальные репо

# Интерактивный режим
./llama-cli \
    -m models/qwen3-14b-q4_k_m.gguf \
    -p "Write a Python function for" \
    -n 512 \
    --n-gpu-layers 40 \
    --ctx-size 8192 \
    --temp 0.7

# Server mode (OpenAI-compatible)
./llama-server \
    -m models/qwen3-14b-q4_k_m.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 40 \
    -c 8192 \
    --flash-attn

# Параметры:
# -ngl: layers на GPU (больше = быстрее, больше VRAM)
# -c: context size
# -t: threads для CPU
# --mlock: держать в RAM
# --flash-attn: Flash Attention (экономия памяти)
```

### Performance Tips 2025

```bash
# Оптимизация для multi-GPU (asymmetric)
# Пример: RTX 4090 + RTX 3080
./llama-cli \
    -m model.gguf \
    --tensor-split 97,3 \  # 97% на 4090, 3% на 3080
    -ngl 99 \
    -t 2  # Меньше threads для GPU inference

# AMD GPU оптимизация (wavefront 64)
# llama.cpp 2025 автоматически определяет

# Flash Attention для длинного контекста
./llama-server \
    -m model.gguf \
    --flash-attn \
    -c 32768  # 32K context
```

### Конвертация моделей

```bash
# HuggingFace -> GGUF
python convert_hf_to_gguf.py \
    /path/to/hf-model \
    --outfile model.gguf \
    --outtype q4_k_m

# Доступные квантизации (2025):
# q2_k    - 2-bit, минимум (70-80% quality)
# q3_k_m  - 3-bit, агрессивная (85-90%)
# q4_k_m  - 4-bit, РЕКОМЕНДУЕТСЯ (92-95%)
# q5_k_m  - 5-bit, высокое качество (95-97%)
# q6_k   - 6-bit, почти FP16 (98%)
# q8_0   - 8-bit, максимум GGUF (99%)

# I-Quants (2025) - лучшее качество при том же размере
# iq2_xxs, iq3_xxs, iq4_xs - improved quantization
```

---

## 6. GGUF Quantization - глубокий разбор

```
+----------------------------------------------------------------------------+
|                    GGUF Quantization Quality vs Size                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  Quantization   Quality    Size (70B)   Speed    Recommended For          |
|  -------------------------------------------------------------------------  |
|  FP16           100%       140 GB       1x       Production (datacenter)  |
|  Q8_0           99%        74 GB        1.2x     Max quality GGUF         |
|  Q6_K           98%        57 GB        1.4x     High quality             |
|  Q5_K_M         95-97%     48 GB        1.6x     Best balance             |
|  Q4_K_M         92-95%     40 GB        1.8x     * DEFAULT CHOICE         |
|  Q4_K_S         90-93%     38 GB        1.9x     Smaller Q4               |
|  Q3_K_M         85-90%     32 GB        2.0x     VRAM limited             |
|  Q2_K           70-80%     26 GB        2.2x     Last resort              |
|                                                                            |
|  K-QUANTS vs LEGACY:                                                       |
|  Q4_K_M > Q4_0 (K-quants лучше сохраняют важные веса)                     |
|  Q5_K_M > Q5_0 (меньше "derails" в reasoning)                             |
|                                                                            |
|  I-QUANTS (2025):                                                          |
|  iq4_xs, iq3_xxs - еще лучше quality/size ratio                          |
|                                                                            |
|  ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:                                                |
|  - Coding tasks: используй Q5_K_M+ (quantization больше влияет на код)   |
|  - Creative writing: Q4_K_M достаточно                                    |
|  - Math/Reasoning: Q5_K_M+ или larger model с Q4                         |
|                                                                            |
|  LADDER: Q4_K_M -> Q5_K_M -> Q8_0 (по мере доступности VRAM)             |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Выбор quantization метода

| Метод | Платформа | Преимущества | Когда использовать |
|-------|-----------|--------------|-------------------|
| **GGUF** | CPU, Apple Silicon | Универсальный, K-quants | Default для локального |
| **GPTQ** | NVIDIA GPU | Быстрый на GPU | High-throughput serving |
| **AWQ** | NVIDIA GPU | Лучше GPTQ по качеству | Production inference |
| **MLX** | Apple Silicon | Нативный для Mac | LM Studio на Mac |

---

## 7. Open WebUI

Веб-интерфейс для локальных LLM:

```bash
# Docker (с существующим Ollama)
docker run -d -p 3000:8080 \
    --add-host=host.docker.internal:host-gateway \
    -v open-webui:/app/backend/data \
    --name open-webui \
    --restart always \
    ghcr.io/open-webui/open-webui:main

# Доступ: http://localhost:3000
```

```yaml
# docker-compose.yml - полный стек
version: '3.8'
services:
  ollama:
    image: ollama/ollama
    volumes:
      - ollama:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama:
  open-webui:
```

### Возможности Open WebUI

- ChatGPT-like интерфейс
- Несколько моделей одновременно
- RAG с документами (upload PDF, txt)
- Промпт библиотека
- История чатов
- Мультипользовательский режим
- Интеграция с Ollama, OpenAI, Azure
- Web search integration
- Code execution sandbox

---

## 8. Production Self-Hosting

### vLLM для высокой нагрузки

```python
# vLLM - для production с высоким throughput
# Continuous batching, PagedAttention, tensor parallelism

from vllm import LLM, SamplingParams

llm = LLM(
    model="Qwen/Qwen3-32B-Instruct",
    tensor_parallel_size=2,  # 2 GPU
    quantization="awq",
    max_model_len=8192,
    gpu_memory_utilization=0.9
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=1024
)

outputs = llm.generate(["Explain quantum entanglement"], sampling_params)
```

```bash
# vLLM OpenAI-compatible server
vllm serve Qwen/Qwen3-32B-Instruct \
    --tensor-parallel-size 2 \
    --quantization awq \
    --port 8000 \
    --max-model-len 8192
```

### vLLM vs llama.cpp - когда что

| Сценарий | vLLM | llama.cpp |
|----------|------|-----------|
| High-throughput serving | +++ | + |
| Multi-user concurrent | +++ | ++ |
| Single-user latency | ++ | +++ |
| Portability | + | +++ |
| Memory efficiency | ++ | +++ |
| Startup time | -- | +++ |
| Consumer hardware | + | +++ |

**Рекомендация:**
- **vLLM**: Production API, много пользователей, datacenter
- **llama.cpp**: Локальная разработка, embedded, consumer GPU

### Text Generation Inference (TGI)

```bash
# Hugging Face TGI
docker run --gpus all -p 8080:80 \
    -v /data:/data \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id Qwen/Qwen3-32B-Instruct \
    --quantize awq \
    --max-input-length 4096 \
    --max-total-tokens 8192 \
    --max-batch-prefill-tokens 4096
```

### Kubernetes deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
          requests:
            memory: "16Gi"
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
        env:
        - name: OLLAMA_KEEP_ALIVE
          value: "24h"
        - name: OLLAMA_NUM_PARALLEL
          value: "4"
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

### Security Best Practices

```
+----------------------------------------------------------------------------+
|                    Security for Self-Hosted LLM                             |
+----------------------------------------------------------------------------+
|                                                                            |
|  NETWORK:                                                                  |
|  - VPN (Tailscale, headscale, netbird) для remote access                  |
|  - Firewall - ограничить exposed services                                 |
|  - Reverse proxy с authentication (2FA)                                   |
|                                                                            |
|  ACCESS CONTROL:                                                           |
|  - Open WebUI: enable authentication, user management                     |
|  - API keys для production endpoints                                      |
|  - Rate limiting per user/IP                                              |
|                                                                            |
|  DATA:                                                                     |
|  - Не хранить sensitive data в prompts/logs                               |
|  - Encryption at rest для model storage                                   |
|  - Audit logging для compliance                                           |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 9. Сравнение инструментов (2025)

| Критерий | Ollama | LM Studio | llama.cpp | vLLM | TGI |
|----------|--------|-----------|-----------|------|-----|
| **Простота** | +++++ | +++++ | ++ | +++ | +++ |
| **Performance** | ++++ | +++ | +++++ | +++++ | ++++ |
| **GUI** | - | +++++ | Web | - | - |
| **API** | +++++ | ++++ | ++++ | +++++ | ++++ |
| **Production** | +++ | ++ | +++ | +++++ | +++++ |
| **Model support** | ++++ | +++++ | +++++ | ++++ | ++++ |
| **Apple Silicon** | ++++ | +++++ | ++++ | + | + |
| **Multi-GPU** | +++ | ++ | ++++ | +++++ | +++++ |

### Когда что использовать

```
+----------------------------------------------------------------------------+
|                       Tool Selection Guide 2025                             |
+----------------------------------------------------------------------------+
|                                                                            |
|  "Хочу просто попробовать LLM локально"                                   |
|  -> Ollama (curl install, ollama run qwen3:8b)                            |
|                                                                            |
|  "Хочу GUI для тестирования разных моделей"                               |
|  -> LM Studio                                                              |
|                                                                            |
|  "У меня Mac, хочу максимальную скорость"                                 |
|  -> LM Studio с MLX backend                                               |
|                                                                            |
|  "Нужен максимальный контроль и performance"                              |
|  -> llama.cpp                                                              |
|                                                                            |
|  "Production API с высоким трафиком"                                      |
|  -> vLLM или TGI                                                          |
|                                                                            |
|  "Красивый веб-интерфейс для команды"                                     |
|  -> Ollama + Open WebUI                                                   |
|                                                                            |
|  "Хочу интегрировать в существующий код (OpenAI SDK)"                     |
|  -> Ollama или LM Studio (оба OpenAI-compatible)                          |
|                                                                            |
|  "Максимальная приватность, open-source only"                             |
|  -> Ollama + llama.cpp                                                    |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 10. On-Device LLM (Mobile, Edge) — 2025 State

### Зачем LLM на устройстве?

```
+----------------------------------------------------------------------------+
|                    On-Device vs Cloud LLM (2025)                            |
+----------------------------------------------------------------------------+
|                                                                            |
|  ПРЕИМУЩЕСТВА ON-DEVICE:                                                   |
|  + 100% приватность — данные не покидают устройство                       |
|  + Latency sub-50ms (vs 200-800ms cloud)                                  |
|  + Работает офлайн                                                         |
|  + Нет costs per token                                                     |
|  + Compliance (HIPAA, GDPR) — проще, данные локальны                      |
|                                                                            |
|  ОГРАНИЧЕНИЯ:                                                              |
|  - Модели ограничены 1-4B параметрами (реально usable)                    |
|  - Качество ниже GPT-4o / Claude 3.5                                      |
|  - Потребление батареи: 50% за 90 минут активного использования           |
|  - Нагрев устройства при длительной работе                                |
|  - Занимает 2-6GB storage                                                  |
|                                                                            |
|  КОГДА ИСПОЛЬЗОВАТЬ:                                                       |
|  ✓ Медицина/здоровье — приватность критична                               |
|  ✓ Простые задачи: summarization, transcription, Q&A                      |
|  ✓ Offline режим обязателен                                                |
|  ✓ Мгновенный отклик критичен                                             |
|  ✗ Сложный reasoning, math — лучше cloud                                  |
|  ✗ Long-form generation — качество важнее скорости                        |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Фреймворки для Mobile (2025)

| Framework | Платформы | Оптимизация | Лучше для | GitHub Stars |
|-----------|-----------|-------------|-----------|--------------|
| **MediaPipe LLM** | Android, iOS, Web | GPU, NPU | Google models (Gemma) | 27k+ |
| **ExecuTorch** | iOS, Android | CPU, GPU, NPU | Llama, Qwen | 2.5k+ |
| **MLX Swift** | iOS, macOS | Apple Silicon | Apple devices | 18k+ |
| **llama.cpp** | Everywhere | CPU, GPU | GGUF models | 72k+ |
| **MLC-LLM** | All | GPU optimized | High performance | 19k+ |
| **CoreML** | iOS, macOS | Neural Engine | Apple native | Apple SDK |

### Модели для Mobile (декабрь 2025)

```
+----------------------------------------------------------------------------+
|                    Best Models for Mobile 2025                              |
+----------------------------------------------------------------------------+
|                                                                            |
|  GEMMA 3n (Google) — РЕКОМЕНДУЕТСЯ для Android                            |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                              |
|  - E2B: 5B params, ~2GB RAM (effective 2B)                                |
|  - E4B: 8B params, ~3GB RAM (effective 4B)                                |
|  - Multimodal: text + image + audio + video                               |
|  - 60-70 tok/s на Pixel, 0.3s time-to-first-token                        |
|  - LMArena 1338 — первая <10B модель с 1300+ score                       |
|  - 140 языков текст, 35 языков multimodal                                 |
|                                                                            |
|  LLAMA 3.2 1B/3B (Meta) — УНИВЕРСАЛЬНЫЙ ВЫБОР                             |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                              |
|  - 1B: любой iOS (6GB+ RAM), mid-range Android                           |
|  - 3B: iPhone 12 Pro+, Samsung S21 Ultra+                                 |
|  - 128K context, instruction-tuned                                        |
|  - Quantized: 2-4x быстрее, -56% размер, -41% память                     |
|  - 8-10 tok/s на Snapdragon 8 Gen 2                                      |
|                                                                            |
|  PHI-4 MINI (Microsoft) — REASONING                                       |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                              |
|  - 3.8B параметров                                                        |
|  - Отличный для coding и math                                             |
|  - MIT license                                                             |
|                                                                            |
|  QWEN3 0.6B (Alibaba) — EDGE/IoT                                          |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                              |
|  - Ультра-компактный                                                      |
|  - ~40 tok/s на Pixel 8, iPhone 15 Pro                                   |
|  - Подходит для wearables                                                 |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Performance Benchmarks (декабрь 2025)

| Устройство | Модель | Tokens/sec | RAM | Framework |
|------------|--------|------------|-----|-----------|
| **iPhone 17 Pro** | LFM2-VL-450m | 136 | 2GB | Cactus |
| **iPhone 15 Pro** | Llama 3.2 1B | 17 (CPU) / 12.8 (GPU) | 4GB | llama.cpp |
| **iPhone 15 Pro** | Qwen3 0.6B | ~40 | 2GB | ExecuTorch |
| **Pixel 8 Pro** | Gemma 3n E2B | 60-70 | 2GB | MediaPipe |
| **Samsung S25 Ultra** | LFM2-VL-450m | 91 | 2GB | Cactus |
| **Snapdragon 8 Gen 2** | Llama 3.2 3B | 8-10 | 6GB | llama.cpp |
| **Galaxy A54 (6GB)** | 2B model | ~5 | 6GB | MediaPipe |
| **Mac M4 Pro** | — | 173 | — | Cactus |

**Важные наблюдения:**
- CPU может быть быстрее GPU на iPhone (17 vs 12.8 tok/s) из-за overhead копирования памяти
- Q4 квантизация дает значительный прирост скорости без критической потери качества
- NPU (Neural Engine) эффективнее по батарее, но требует специфичных форматов

### Квантизация для Mobile

```
+----------------------------------------------------------------------------+
|                    Mobile Quantization Guide                                |
+----------------------------------------------------------------------------+
|                                                                            |
|  РЕКОМЕНДУЕМЫЕ ФОРМАТЫ:                                                    |
|                                                                            |
|  Q4_K_M — Оптимальный выбор для mobile                                    |
|  - 3.4x быстрее, 3.2x меньше памяти vs FP16                              |
|  - 68% сокращение размера модели                                          |
|  - 84-87% сохранение качества на GSM8K (math)                            |
|                                                                            |
|  РАЗМЕРЫ МОДЕЛЕЙ ПО КВАНТИЗАЦИИ (3B модель):                              |
|  FP16: ~6GB -> Q4_K_M: ~1.9GB -> Q2_K: ~1.2GB                            |
|                                                                            |
|  TRADE-OFFS:                                                               |
|  - Q4: хорошо для chat, summarization                                     |
|  - Q5+: нужен для math, coding (более чувствительны)                     |
|  - Q2-Q3: только для очень ограниченного RAM                             |
|                                                                            |
|  ФАКТЫ (исследование 2025):                                                |
|  - INT4 увеличивает perplexity на 5-15% vs FP32                          |
|  - MMLU чувствителен к квантизации — избегать Q3 и ниже                  |
|  - GSM8K (math) устойчив — Q4_K_M сохраняет 84-87%                       |
|                                                                            |
+----------------------------------------------------------------------------+
```

### iOS: MLX Swift + CoreML

```swift
// MLX Swift — нативный для Apple Silicon
// Доступен через mlx-swift-lm package

import MLXLM
import MLXLMCommon

// 1. Загрузка модели
let modelContainer = try await LLMModelFactory.shared.loadContainer(
    configuration: .init(id: "mlx-community/Llama-3.2-1B-Instruct-4bit")
)

// 2. Генерация
let prompt = "Explain machine learning in simple terms"
let result = try await modelContainer.perform { context in
    let output = try await context.generate(
        prompt: prompt,
        maxTokens: 256
    )
    return output.text
}

// 3. Streaming
for try await token in modelContainer.generate(prompt: prompt) {
    print(token, terminator: "")
}
```

```swift
// CoreML + Transformers — для Neural Engine
import CoreML
import NaturalLanguage

// 1. Загрузка CoreML модели (конвертированной)
let config = MLModelConfiguration()
config.computeUnits = .all  // CPU + GPU + Neural Engine

let model = try MLModel(
    contentsOf: modelURL,
    configuration: config
)

// 2. State management для KV-cache (WWDC'24 feature)
// CoreML поддерживает stateful models для эффективного inference
```

**Ресурсы для iOS:**
- [ml-explore/mlx-swift](https://github.com/ml-explore/mlx-swift) — MLX Swift API
- [swift-transformers](https://github.com/huggingface/swift-transformers) — HuggingFace Swift
- [Private LLM](https://privatellm.app/) — готовое приложение

### Android: MediaPipe + llama.cpp

```kotlin
// MediaPipe LLM Inference — рекомендуется для Gemma
// build.gradle: implementation("com.google.mediapipe:tasks-genai:0.10.27")

import com.google.mediapipe.tasks.genai.llminference.LlmInference

class OnDeviceLLM(private val context: Context) {
    private lateinit var llmInference: LlmInference

    suspend fun initialize() {
        val options = LlmInference.LlmInferenceOptions.builder()
            .setModelPath("/path/to/gemma-3n-e2b.task")
            .setMaxTokens(1024)
            .setResultListener { partialResult, done ->
                // Streaming callback
                println(partialResult)
            }
            .build()

        llmInference = LlmInference.createFromOptions(context, options)
    }

    suspend fun generate(prompt: String): String {
        return llmInference.generateResponse(prompt)
    }

    // Multimodal (Gemma 3n)
    suspend fun generateWithImage(prompt: String, image: Bitmap): String {
        val mpImage = BitmapImageBuilder(image).build()
        return llmInference.generateResponse(prompt, listOf(mpImage))
    }
}
```

```kotlin
// llama.cpp через Kotlin binding
// Kotlin-LlamaCpp или InferKt

// 1. Gradle dependency
// implementation("com.github.user:kotlin-llama-cpp:version")

import com.example.llamacpp.LlamaModel

class LlamaInference {
    private val model = LlamaModel()

    fun load(modelPath: String) {
        model.loadModel(
            path = modelPath,
            contextSize = 2048,
            gpuLayers = 0  // CPU only для совместимости
        )
    }

    fun generate(prompt: String, maxTokens: Int = 256): Flow<String> = flow {
        model.generateStream(prompt, maxTokens).collect { token ->
            emit(token)
        }
    }
}
```

**Ресурсы для Android:**
- [MediaPipe LLM Samples](https://github.com/google-ai-edge/mediapipe-samples/tree/main/examples/llm_inference/android)
- [Kotlin-LlamaCpp](https://github.com/ljcamargo/kotlinllamacpp)
- [SmolChat](https://github.com/user/smolchat) — open-source GGUF runner

### ExecuTorch (Cross-Platform от Meta)

```bash
# ExecuTorch — production framework от Meta
# Используется в Instagram, WhatsApp, Messenger

# 1. Установка
pip install executorch

# 2. Экспорт модели
python -m executorch.examples.models.llama.export_llama \
    --model Qwen/Qwen3-0.6B-Instruct \
    --output qwen3-0.6b.pte \
    --quantize int4

# 3. Размер runtime: 50KB base footprint
```

```kotlin
// Android с ExecuTorch AAR
// build.gradle: implementation("org.pytorch:executorch:1.0.0")

import org.pytorch.executorch.Module

val module = Module.load("qwen3-0.6b.pte")
val output = module.forward(inputTensor)
```

```swift
// iOS с ExecuTorch
import ExecuTorch

let module = try Module(fileAtPath: "qwen3-0.6b.pte")
let output = try module.forward([inputTensor])
```

### React Native с ExecuTorch

```typescript
// React Native ExecuTorch — JS API для mobile
// npm install react-native-executorch

import { useLLM } from 'react-native-executorch';

function ChatComponent() {
    const { generate, isLoading } = useLLM({
        modelPath: 'qwen3-0.6b.pte',
        maxTokens: 256
    });

    const handleChat = async (prompt: string) => {
        const response = await generate(prompt);
        console.log(response);
    };

    // Streaming
    const handleStreamChat = async (prompt: string) => {
        for await (const token of generate(prompt, { stream: true })) {
            console.log(token);
        }
    };
}
```

### Ограничения и Gotchas (2025)

```
+----------------------------------------------------------------------------+
|                    Mobile LLM — Реальные ограничения                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  ПАМЯТЬ:                                                                   |
|  - iOS лимит bundle: 4GB (модель нужно качать после установки)            |
|  - 7B модель = 28GB (FP32) / 14GB (FP16) / 3.5GB (Q4)                    |
|  - Если модель + KV cache > RAM → crash или swap (очень медленно)        |
|  - TinyLlama 1B занимает >50% RAM iPhone 14 (6GB)                        |
|                                                                            |
|  БАТАРЕЯ:                                                                  |
|  - 7B модель: ~2 часа до полного разряда                                  |
|  - 50% батареи за 90 минут активного использования                        |
|  - GPU = как игра: сильный нагрев, быстрый разряд                         |
|  - NPU эффективнее, но требует специфичных форматов                       |
|                                                                            |
|  ПРОИЗВОДИТЕЛЬНОСТЬ:                                                       |
|  - 8-10 tok/s на flagship (vs 50-100 tok/s desktop GPU)                  |
|  - Cold start 5-15 секунд для загрузки модели                            |
|  - Mid-range (Galaxy A54): даже 2B модель "тормозит"                     |
|                                                                            |
|  GPU vs CPU:                                                               |
|  - GPU не всегда быстрее! (iPhone 15: CPU 17 tok/s > GPU 12.8 tok/s)     |
|  - Причина: overhead копирования памяти в GPU                             |
|  - GPU занят другими приложениями (UI rendering)                          |
|                                                                            |
|  ТЕПЛО:                                                                    |
|  - Телефон перегревается при длительном inference                         |
|  - Thermal throttling снижает производительность                          |
|  - Рекомендуется: короткие сессии, не более 5-10 минут                   |
|                                                                            |
|  ПРАКТИЧЕСКИЕ СОВЕТЫ:                                                      |
|  1. Тестируйте на реальных устройствах (эмуляторы не работают)           |
|  2. Измеряйте: cold start, inference latency, память, температуру        |
|  3. Адаптивная загрузка: 2B на старых, 4B на новых устройствах           |
|  4. Cloud fallback: на слабых устройствах → cloud API                    |
|  5. Caching частых запросов экономит батарею                             |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Production Apps с On-Device LLM (2025)

| Приложение | Модель | Платформа | Использование |
|------------|--------|-----------|---------------|
| **Apple Intelligence** | 3B (Apple) | iOS 18+ | Siri, Writing Tools |
| **Samsung Galaxy AI** | On-device + Cloud | Galaxy S24+ | Translation, Summary |
| **Google AI Edge Gallery** | Gemma 3n | Android | Experimental demos |
| **Private LLM** | GGUF models | iOS | Privacy-first chat |
| **Enclave AI** | Local models | iOS/Mac | Zero tracking |
| **SmolChat** | GGUF models | Android | Open-source |
| **Meta Apps** | ExecuTorch | iOS/Android | Instagram, WhatsApp |

### Decision Tree: Cloud vs On-Device

```
                           ┌──────────────────────────┐
                           │   Нужна приватность?     │
                           └────────────┬─────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
                      ДА                              НЕТ
                        │                               │
            ┌───────────┴───────────┐                   │
            │ Сложность задачи?     │                   │
            └───────────┬───────────┘                   │
                        │                               │
           ┌────────────┴────────────┐                  │
           ▼                         ▼                  │
      ПРОСТАЯ                     СЛОЖНАЯ               │
    (summary, Q&A)             (reasoning, code)        │
           │                         │                  │
           ▼                         ▼                  ▼
    ┌──────────────┐         ┌──────────────┐   ┌──────────────┐
    │  ON-DEVICE   │         │ HYBRID:      │   │    CLOUD     │
    │  Gemma 3n    │         │ On-device +  │   │  GPT-4o /    │
    │  Llama 3.2   │         │ Cloud backup │   │  Claude 3.5  │
    └──────────────┘         └──────────────┘   └──────────────┘
```

---

## 11. Quick Start Guides

### Быстрый старт (5 минут)

```bash
# 1. Установка Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Запуск модели (автоматически скачает)
ollama run qwen3:8b

# 3. Готово! Чат в терминале
# Для выхода: /bye
```

### Разработчик Setup (30 минут)

```bash
# 1. Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Скачать модели для разных задач
ollama pull qwen3:14b           # General purpose
ollama pull deepseek-r1:14b     # Reasoning
ollama pull qwen3-coder:7b      # Coding (если есть)

# 3. Open WebUI для UI
docker run -d -p 3000:8080 \
    --add-host=host.docker.internal:host-gateway \
    -v open-webui:/app/backend/data \
    --name open-webui \
    ghcr.io/open-webui/open-webui:main

# 4. Python integration
pip install ollama openai

# 5. Test
python -c "import ollama; print(ollama.chat(model='qwen3:14b', messages=[{'role':'user','content':'Hello!'}])['message']['content'])"
```

### Production Setup

```bash
# 1. Docker Compose stack
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

  webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_data:
  webui_data:
EOF

# 2. Запуск
docker compose up -d

# 3. Preload моделей
docker exec ollama ollama pull qwen3:32b
docker exec ollama ollama pull mistral-small:24b

# 4. Health check
curl http://localhost:11434/api/tags
```
---

## Проверь себя

> [!question]- Какие hardware требования для запуска моделей разного размера локально?
> 7B модели: 4-8 GB VRAM (quantized), consumer GPU (RTX 3060+). 13B: 8-16 GB VRAM, RTX 4070+. 70B: 40-80 GB VRAM, A100/H100 или multi-GPU. На CPU: llama.cpp с GGUF, 7B работает на 16 GB RAM, но в 10-50x медленнее GPU. Apple Silicon (M1-M4): unified memory, 7B-13B комфортно.

> [!question]- Чем Ollama отличается от LM Studio и llama.cpp?
> Ollama: CLI-first, Docker-like UX (pull/run), REST API, хорош для серверов и автоматизации. LM Studio: GUI, простой для начинающих, OpenAI-compatible API. llama.cpp: C++ библиотека, максимальная производительность и контроль, basis для Ollama. Для production --- Ollama или vLLM, для экспериментов --- LM Studio.

> [!question]- Когда self-hosting выгоднее облачных API и как это рассчитать?
> Считать: monthly API cost vs (GPU lease + electricity + DevOps time). Break-even при стабильных 50-100K запросов/день для 7B моделей. Также self-hosting нужен для: data privacy, air-gapped environments, offline access, и custom model modifications.

---

## Ключевые карточки

Что такое GGUF формат и зачем он нужен?
?
Формат файла для квантизованных моделей, используемый llama.cpp и Ollama. Содержит модель + метаданные + tokenizer в одном файле. Поддерживает разные уровни квантизации (Q4_K_M, Q5_K_M, Q8_0). Оптимизирован для CPU и смешанного CPU+GPU inference.

Какие open-source модели лидируют в 2025?
?
Llama 3.1 (Meta, 8B-405B), DeepSeek V3/R1 (reasoning), Qwen 2.5 (Alibaba, multilingual), Mistral (7B-Large), и Gemma 2 (Google, 2B-27B). Выбор зависит от задачи: DeepSeek для reasoning, Qwen для multilingual, Llama для общих задач.

Как настроить Ollama для production использования?
?
Docker deployment с GPU passthrough, nginx reverse proxy для load balancing, environment variables для model storage и concurrency. Мониторинг: prometheus metrics endpoint, health checks. Ограничения: нет built-in auth, нужен proxy layer для security.

Что такое on-device AI и для каких задач оно подходит?
?
Запуск моделей прямо на мобильном устройстве (phone/tablet). Инструменты: MediaPipe (Google), ExecuTorch (Meta), Core ML (Apple), MLX (Apple Silicon). Подходит для: real-time classification, text summarization, on-device translation. Ограничение: модели до 3B параметров.

Как выбрать уровень квантизации для модели?
?
Q8_0: минимальная потеря качества, -50% memory. Q5_K_M: хороший баланс quality/size, рекомендуется для большинства задач. Q4_K_M: максимальная компрессия при приемлемом качестве. Q3/Q2: заметная деградация, только для экспериментов. Тестировать на своих eval datasets.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[llm-inference-optimization]] | Оптимизация inference-сервера |
| Углубиться | [[mobile-ai-ml-guide]] | AI на мобильных устройствах |
| Смежная тема | [[docker-for-developers]] | Docker для контейнеризации моделей |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI Engineering |

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Dettmers T. et al. (2022). *GPT3.int8(): 8-bit Matrix Multiplication for Transformers*. NeurIPS | INT8 quantization |
| 2 | Hinton G. et al. (2015). *Distilling the Knowledge in a Neural Network*. arXiv:1503.02531 | Knowledge distillation |
| 3 | Kwon W. et al. (2023). *Efficient Memory Management for LLM Serving with PagedAttention*. SOSP | vLLM, PagedAttention |
| 4 | Frantar E. et al. (2022). *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers*. arXiv:2210.17323 | GPTQ quantization |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [Ollama](https://ollama.com/) | Самый простой self-hosting |
| 2 | [LM Studio](https://lmstudio.ai/) | GUI для self-hosting |
| 3 | [llama.cpp](https://github.com/ggerganov/llama.cpp) | Low-level inference engine |
| 4 | [HuggingFace Models](https://huggingface.co/models) | Каталог open-weight моделей |
| 5 | [MLX — Apple](https://github.com/ml-explore/mlx) | Inference на Apple Silicon |

*Проверено: 2026-01-09*
