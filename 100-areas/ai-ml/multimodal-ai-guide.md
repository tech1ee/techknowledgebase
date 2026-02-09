---
title: "Multimodal AI: Полное руководство по мультимодальным системам (2025)"
type: guide
status: published
tags:
  - topic/ai-ml
  - type/guide
  - level/intermediate
---

# Multimodal AI: Полное руководство по мультимодальным системам (2025)

> Последнее обновление: Декабрь 2025
>
> Мультимодальный AI - это системы, способные обрабатывать и генерировать контент различных типов: текст, изображения, аудио и видео. Данный гайд охватывает все ключевые технологии, модели и практические аспекты применения.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Как работают языковые модели | [[llm-fundamentals]] |
| **Python** | Примеры кода, интеграция с API | Любой курс Python |
| **REST API** | Все модели работают через API | [[ai-api-integration]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ⚠️ Частично | Начните с [[ai-ml-overview-v2]], затем сюда |
| **AI Engineer** | ✅ Да | Полный обзор мультимодальных возможностей |
| **Product Manager** | ✅ Да | Понимание возможностей для продуктов |
| **Creative Professional** | ✅ Да | Генерация изображений, видео, аудио |

### Терминология для новичков

> 💡 **Multimodal AI** = AI, который понимает и создаёт разные типы контента (текст, изображения, аудио, видео)

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Modality** | Тип данных (текст, изображение, звук) | **Язык** — текст, картинки, музыка — разные "языки" для AI |
| **Vision** | Способность понимать изображения | **Зрение** — AI "смотрит" на картинку и понимает что там |
| **Omni-model** | Модель для всех типов контента | **Универсал** — одна модель вместо нескольких специализированных |
| **Image Generation** | Создание изображений по тексту | **Художник по описанию** — опиши, получи картину |
| **TTS** | Text-to-Speech (текст в речь) | **Диктор** — читает текст голосом |
| **STT/ASR** | Speech-to-Text (речь в текст) | **Стенографист** — записывает речь текстом |
| **Video Understanding** | Анализ видео контента | **Внимательный зритель** — понимает что происходит в видео |
| **Computer Use** | AI управляет интерфейсом как человек | **Удалённый помощник** — кликает мышкой, печатает |

---

## Содержание

1. [Обзор мультимодального AI](#обзор-мультимодального-ai)
2. [Vision Models - Понимание изображений](#vision-models---понимание-изображений)
3. [Audio & Speech - Аудио технологии](#audio--speech---аудио-технологии)
4. [Video Understanding - Анализ видео](#video-understanding---анализ-видео)
5. [Image Generation - Генерация изображений](#image-generation---генерация-изображений)
6. [Video Generation - Генерация видео](#video-generation---генерация-видео)
7. [Voice Synthesis - Синтез голоса](#voice-synthesis---синтез-голоса)
8. [Computer Use & Automation](#computer-use--automation)
9. [Production Integration](#production-integration)
10. [Сравнительные таблицы](#сравнительные-таблицы)

---

## Обзор мультимодального AI

### Что такое Multimodal AI?

**Multimodal AI** - это системы искусственного интеллекта, способные обрабатывать и генерировать информацию в нескольких модальностях (форматах данных) одновременно:

- **Text** - текстовая информация
- **Vision** - изображения и визуальные данные
- **Audio** - звук, речь, музыка
- **Video** - видеоконтент с временной динамикой

### Рыночный контекст (2025)

```
Размер рынка Multimodal AI:
- 2025: $2.51 миллиарда
- 2034 (прогноз): $42.38 миллиарда

Ключевое преимущество: один API-вызов вместо управления
Whisper + CLIP + GPT отдельно. Компании сообщают о
сокращении сложности пайплайнов на 50%.
```

### Эволюция подходов

```
2022: Отдельные модели для каждой модальности
      CLIP (vision) + GPT-3 (text) + Whisper (audio)

2023: Ранняя интеграция
      GPT-4V, LLaVA, Claude 3 Vision

2024: Omni-модели
      GPT-4o - единая модель для text/vision/audio

2025: Полная мультимодальность
      GPT-5, Gemini 3, Claude Opus 4.5, Sora 2
      Video understanding до 6 часов, Realtime Audio,
      Computer Use, нативная генерация изображений
```

### Ключевые игроки рынка (Декабрь 2025)

| Компания | Основные модели | Специализация |
|----------|----------------|---------------|
| **OpenAI** | GPT-4o, GPT-5, Whisper, Sora 2, gpt-realtime | Full-stack multimodal |
| **Anthropic** | Claude Opus 4.5, Sonnet 4.5, Haiku 4.5 | Vision, Computer Use |
| **Google** | Gemini 3 Pro/Flash | Long video (6+ часов) |
| **Meta** | LLaMA 4, Llama 3.2 Vision | Open-source multimodal |
| **Black Forest Labs** | FLUX.2 Pro/Dev/Klein | Image generation SOTA |
| **Runway** | Gen-4.5, Gen-4, Gen-3 Alpha | Video generation |
| **ElevenLabs** | Multilingual v2, Flash v2.5 | Voice synthesis leader |
| **Allen AI** | Molmo 2 (4B-8B) | Open-source video SOTA |

---

## Vision Models - Понимание изображений

### GPT-4 Vision / GPT-4o

**GPT-4o** ("o" = omni) - flagship мультимодальная модель OpenAI, объединяющая text, vision и audio в едином neural network.

#### Ключевые характеристики

```
Релиз: Май 2024
Response time: 320ms (сравнимо с человеком)
Модальности: text + image + audio input/output
Native image generation: Март 2025 (заменил DALL-E 3 в ChatGPT)
File uploads: до 512MB, 20 файлов на чат
```

#### Возможности Vision

| Функция | Описание | Качество |
|---------|----------|----------|
| **Object Detection** | Распознавание объектов и сцен | Excellent |
| **OCR (Text Extraction)** | Извлечение текста из изображений | Excellent |
| **Mathematical Analysis** | Анализ рукописных формул | Good |
| **Chart Interpretation** | Понимание графиков и диаграмм | Excellent |
| **Spatial Reasoning** | Пространственные отношения | Good |

#### Benchmark Performance (Июль 2025)

На основе исследования "How Well Does GPT-4o Understand Vision?":

```
GPT-4o vs другие модели на 6 CV tasks:
- Лучший среди non-reasoning моделей
- Top-1 в 4 из 6 задач
- Семантические задачи >> геометрические
- Reasoning models (o3) улучшают геометрию

Тестируемые модели: GPT-4o, o4-mini, Gemini 1.5 Pro,
Gemini 2.0 Flash, Claude 3.5 Sonnet, Qwen2-VL, Llama 3.2
```

#### API Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image? Analyze in detail."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg",
                        # Или base64: "data:image/jpeg;base64,..."
                        "detail": "high"  # low, high, auto
                    }
                }
            ]
        }
    ],
    max_tokens=1000
)
```

#### Ограничения

- Не распознает лица публичных персон (safety)
- Image comprehension error rate ~20% в медицинских задачах
- Геометрические задачи сложнее семантических
- Апрель 2025: rollback из-за excessive sycophancy

### Claude Vision (Anthropic)

**Claude 3.5 Sonnet** и **Claude Opus 4.5** - сильнейшие vision-модели Anthropic с превосходством в document understanding.

#### Технические характеристики

```
Форматы: JPEG, PNG, GIF, WebP
Лимиты:
  - claude.ai: до 20 изображений/запрос
  - API: до 100 изображений/запрос
  - Request size: 32MB max

Оптимальный размер: длинная сторона <= 1568px
Token cost: ~1600 tokens для большого изображения
```

#### Ключевые преимущества

1. **Chart/Graph Analysis** - "step-change improvements" для visual reasoning
2. **Text Transcription** - точное извлечение из несовершенных изображений
3. **Multi-image Reasoning** - анализ связей между изображениями
4. **Document Understanding** - shipping manifests, invoices, forms

#### Benchmark Performance

```
Claude 3.5 Sonnet превосходит:
- Claude 3 Opus на стандартных vision benchmarks
- GPT-4o и Gemini 1.5 Pro на MathVista, AI2D

Особая сила: retail, logistics, financial services
где нужно "glean more insights from an image than from text alone"
```

#### API Usage

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Extract all data from this invoice in JSON format"
                }
            ],
        }
    ],
)
```

### Open-Source Vision Models

#### LLaVA (Large Language-and-Vision Assistant)

```
Архитектура: CLIP ViT-L/14 + LLM (Vicuna/Llama/Qwen)
Параметры: 7B - 110B
Training:
  - Stage 1: 558K feature alignment (frozen encoder + LLM)
  - Stage 2: 665K instruction tuning (150K GPT + 515K VQA)

Performance: 85.1% relative score vs GPT-4 on synthetic benchmark
Science QA: 92.53% accuracy (LLaVA + GPT-4 synergy)
```

**Ключевые версии (2025):**

| Версия | Особенности |
|--------|-------------|
| **LLaVA-NeXT** | Llama-3 (8B), Qwen-1.5 (72B/110B), zero-shot video |
| **LLaVA-CoT** (ICCV 2025) | Chain-of-thought reasoning, beats GPT-4o-mini |
| **LLaVA-GM** | Lightweight, low-resource deployment |
| **LLaViT** | LLM как vision encoder, 2x performance vs baseline |

```python
# LLaVA через Ollama (локальный запуск)
import ollama

response = ollama.chat(
    model='llava:13b',
    messages=[{
        'role': 'user',
        'content': 'Describe this image in detail',
        'images': ['./photo.jpg']
    }]
)
```

#### Другие Open-Source Leaders (2025)

| Модель | Параметры | Особенности |
|--------|-----------|-------------|
| **Molmo 2** (Allen AI) | 4B-8B | SOTA open-source, video tracking |
| **Qwen2.5-VL** | 32B | 256K-1M context, frame-by-frame |
| **GLM-4.5V** (Zhipu) | 106B (12B active) | MoE, 3D-RoPE, 128K context |
| **InternVL** | Various | Strong Chinese support |
| **Gemma 3** (Google) | Lightweight | Text, image, short video |

---

## Audio & Speech - Аудио технологии

### OpenAI Whisper

**Whisper** - state-of-the-art модель для automatic speech recognition (ASR), выпущенная в сентябре 2022.

#### Архитектура

```
Type: Encoder-Decoder Transformer
Input: 30-second audio chunks -> Log-Mel spectrogram
Output: Text tokens + special tokens (language, timestamps)

Training Data:
- Whisper large: 680,000 hours supervised
- Whisper large-v3: 1M hours weakly labeled + 4M pseudo-labeled

Multilingual: 100+ языков
Zero-shot: работает без дообучения
```

#### Модели Whisper

| Model | Parameters | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| tiny | 39M | Fastest | Lower | Edge devices |
| base | 74M | Fast | OK | Quick transcription |
| small | 244M | Medium | Good | Balanced |
| medium | 769M | Slower | Better | Accuracy focus |
| large-v3 | 1.5B | Slowest | Best | Production quality |
| large-v3-turbo | ~800M | Fast | Great | Best balance |

#### Key Features

```
Robustness:
- 50% fewer errors vs specialized models
- Works with accents, background noise, technical language

Capabilities:
- Multilingual speech recognition
- Speech translation (to English)
- Language identification
- Voice activity detection

Limitations:
- Hallucinations (generates text not in audio)
- Repetition tendency (mitigated by beam search)
- File size: max 25 MB via API
- Formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
```

#### API Usage

```python
from openai import OpenAI

client = OpenAI()

# Transcription with timestamps
audio_file = open("meeting.mp3", "rb")
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)

for segment in transcript.segments:
    print(f"[{segment['start']:.2f}s] {segment['text']}")

# Translation to English
translation = client.audio.translations.create(
    model="whisper-1",
    file=audio_file
)
```

### Сравнение STT моделей (2025)

#### Commercial Leaders

| Model | WER | Latency | Languages | Streaming | Best For |
|-------|-----|---------|-----------|-----------|----------|
| **AssemblyAI Universal-2** | 14.5% | Low | 99+ | Yes | Most consistent |
| **Deepgram Nova-3** | ~18% | <300ms | Many | Yes | Real-time, noisy |
| **Google Chirp** | 11.6% | Medium | 125+ | Batch | Accuracy focus |
| **GPT-4o-Transcribe** | Low | Medium | Many | No | Accents, noise |
| **ElevenLabs Scribe** | ~3.3% | Low | 99 | Yes | Highest accuracy |

#### Open-Source Champions

| Model | Speed (RTFx) | Accuracy | Best For |
|-------|--------------|----------|----------|
| **NVIDIA Canary Qwen 2.5B** | Fast | Lowest WER | Medical, Financial |
| **NVIDIA Parakeet TDT** | >2000 | Good | Real-time apps |
| **Whisper large-v3-turbo** | Fast | Good | General purpose |
| **groq-distil-whisper** | Fastest | Good | English only |

**Trend 2025:** Multi-model strategies - leading companies combine multiple STT models for virtually error-free transcription.

### OpenAI Realtime API

**Realtime API** - low-latency speech-to-speech взаимодействие, GA с 28 августа 2025.

#### Ключевые характеристики

```
Model: gpt-realtime
Latency: ~320ms (human-like)
Connection: WebRTC, WebSocket, SIP

Benchmark (Big Bench Audio):
- gpt-realtime: 82.8% accuracy
- December 2024 model: 65.6% accuracy

No session limits: С 3 февраля 2025
```

#### Преимущества над классическим пайплайном

```
Классический пайплайн (1-3 секунды):
User Audio -> STT (Whisper) -> LLM (GPT-4) -> TTS -> Response
   500ms        500ms          800ms      500ms

Realtime API (300-500ms):
User Audio -> GPT-4o Native Audio -> Audio Response
              Единая модель
```

**Capabilities:**

- Native audio processing (no intermediate text)
- Non-verbal cues (laughs, sighs)
- Mid-sentence language switching
- Tone adaptation
- Interruption handling
- Accurate alphanumeric detection in multiple languages

#### Голоса

```
Built-in voices (13):
alloy, ash, ballad, coral, echo, fable, onyx,
nova, sage, shimmer, verse, marin, cedar

New in 2025: Marin, Cedar (most natural-sounding)

Custom voices: Available via reference audio sample
```

#### Pricing

```
gpt-realtime (20% cheaper than gpt-4o-realtime-preview):
- Input: $32/1M audio tokens
- Cached input: $0.40/1M tokens
- Output: $64/1M audio tokens
```

#### API Usage

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def realtime_conversation():
    async with client.realtime.connect(model="gpt-realtime") as connection:
        await connection.session.update(
            voice="sage",
            instructions="You are a helpful barista assistant",
            turn_detection={
                "type": "server_vad",
                "threshold": 0.5,
                "silence_duration_ms": 500
            }
        )

        # Send audio
        await connection.input_audio_buffer.append(audio_bytes)
        await connection.input_audio_buffer.commit()

        # Receive streaming response
        async for event in connection:
            if event.type == "response.audio.delta":
                play_audio(event.delta)
            elif event.type == "input_audio_buffer.speech_started":
                # User interrupted - cancel response
                await connection.send({"type": "response.cancel"})
```

---

## Video Understanding - Анализ видео

### Google Gemini Video

**Gemini 3 Pro/Flash** (Декабрь 2025) - лидеры в video understanding с поддержкой до 6 часов видео.

#### Технические характеристики

```
Gemini 3 Pro: "most capable multimodal model"
- SOTA on: document, spatial, screen, video understanding
- Benchmarks: MMMU Pro, Video MMMU

Context Windows:
- 2M tokens: up to 6 hours video (low res)
- 1M tokens: up to 3 hours video (low res)

Sampling: 1 frame per second
Fast-paced actions: >1 fps for better understanding

Token cost:
- Default: ~300 tokens/second (258 per frame + 32 audio)
- Low res: ~100 tokens/second (66 per frame + 32 audio)
```

#### Supported Formats

```
Video: MP4, MPEG, MOV, AVI, FLV, MPG, WebM, WMV, 3GPP

Input methods:
- Files API: videos >20MB or >1 minute
- Inline data: videos <20MB
- YouTube URLs: public videos (8-hour daily limit free)

Multi-video:
- Gemini 2.5+: up to 10 videos per request
- Earlier models: 1 video per request
```

#### Key Capabilities

```
Visual Analysis:
- Content description
- Scene segmentation
- Object tracking
- Speaker identification

Audio Integration:
- Synchronized audio-visual understanding
- Timeline correlation

Special Features:
- Time-specific Q&A with timestamps
- AI-generated video detection (SynthID watermark)
- Coach-level sports analysis
- Video-to-Learning-App transformation
```

#### API Usage

```python
import google.generativeai as genai
import time

genai.configure(api_key="YOUR_API_KEY")

# Upload video
video_file = genai.upload_file(path="video.mp4")

# Wait for processing
while video_file.state.name == "PROCESSING":
    time.sleep(10)
    video_file = genai.get_file(video_file.name)

# Analyze with Gemini 3
model = genai.GenerativeModel(model_name="gemini-3-pro")
response = model.generate_content(
    [video_file, """
    Analyze this video:
    1. Key events with timestamps
    2. Speaker identification
    3. Main topics discussed
    4. Action items mentioned
    """],
    generation_config={"media_resolution": "low"}  # for 6h videos
)

print(response.text)
```

### Other Video Understanding Models

#### Molmo 2 (Allen AI, Декабрь 2025)

```
Status: SOTA open-source for video

Benchmarks (leads open-weight models):
- Image QA
- Short-video QA
- Video counting
- Video tracking
- Human preference

Comparison: Just behind GPT-5/GPT-5 mini, ahead of Gemini 2.5 Pro
```

#### Microsoft MMCTAgent (Ноябрь 2025)

```
Purpose: Long-form video reasoning (hours of content)
Architecture: Multi-agent Planner-Critic on AutoGen

Approach:
- Structured reasoning over large-scale visual data
- Handles minutes-to-hours of video context
- Built for real-world reasoning tasks
```

#### Qwen3-VL

```
Context: 256K native, expandable to 1M tokens

Features:
- Frame-by-frame description
- Second-level video indexing
- Hours of video processing
- Detailed Q&A across long content
```

### Video Understanding Benchmarks (2025)

| Benchmark | Purpose | Notes |
|-----------|---------|-------|
| **Video-MME** | Comprehensive eval | CVPR 2025 |
| **VideoMind** | Long-form reasoning | Chain-of-LoRA |
| **MVU-Eval** | Multi-video understanding | - |
| **CrossVid** | Cross-video reasoning | AAAI 2026 |
| **OmniVideoBench** | Audio-visual in omni MLLMs | - |

---

## Image Generation - Генерация изображений

### DALL-E 3 (OpenAI)

**DALL-E 3** - модель генерации изображений OpenAI, интегрированная в ChatGPT. В марте 2025 заменена на GPT Image для нативной генерации.

#### Характеристики

```
Resolution: 1024x1024 (base)
Aspect ratios: horizontal, square, vertical
Quality modes: standard, hd
Style modes: vivid (hyper-real), natural

Integration: Built on ChatGPT (prompt enhancement)
Iterative editing: "Make his nose bigger", etc.

Safety:
- No public figures
- No living artist styles
- C2PA watermark (February 2024+)

Still available: Microsoft Copilot (via Bing Image Creator)
```

#### API Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic city with flying cars at sunset, photorealistic",
    size="1024x1024",
    quality="hd",
    style="vivid",
    n=1
)

image_url = response.data[0].url
revised_prompt = response.data[0].revised_prompt

# Editing capabilities (DALL-E 2/3)
# - Variations: generate variants of existing image
# - Inpainting: fill missing areas
# - Outpainting: expand image boundaries
```

#### Pricing

```
API: $0.02-0.08 per image (size/quality dependent)
ChatGPT Plus: ~100 images/day included ($20/month)
```

### FLUX (Black Forest Labs)

**FLUX.2** (Ноябрь 2025) - state-of-the-art image generation от создателей Stable Diffusion.

#### Модели FLUX.2

| Model | License | Resolution | Use Case |
|-------|---------|------------|----------|
| **FLUX.2 Pro** | Commercial | 4MP | Production quality |
| **FLUX.2 Flex** | - | 4MP | Flexible usage |
| **FLUX.2 Dev** | Non-commercial | 4MP | Development |
| **FLUX.2 Klein** | Apache 2.0 | - | Open-source |

#### Архитектура и возможности

```
Architecture: Latent Flow Matching + Rectified Flow
VLM: Mistral-3 (24B parameters)
VAE: Open-source Apache 2.0

Features:
- Photorealistic output (no "AI look")
- Character/style consistency across references
- Complex text rendering
- Brand guideline adherence
- 4MP editing with detail preservation
- Real-world lighting and physics
```

#### Key 2025 Milestones

```
January 2025: NVIDIA Blackwell partnership
May 2025: Flux.1 Kontext (in-context editing)
September 2025: Adobe Photoshop integration
November 2025: FLUX.2 release with NVIDIA ComfyUI optimization
```

#### Availability

```
APIs: Replicate, fal.ai, mystic
Local: ComfyUI with NVIDIA weight streaming
Adobe: Photoshop (beta) - Flux.1 Kontext Pro for generative fill
```

### Stable Diffusion 3.5 (Stability AI)

#### Модели

```
SD 3.5 Large: 8B parameters, up to 1MP
SD 3.5 Large Turbo: Distilled, faster
SD 3.5 Medium: Edge devices, 0.25-2MP

Architecture: Diffusion Transformer + Flow Matching
Backbone: Rectified Flow (new in 3.0)

Enterprise: Available on Amazon Bedrock
```

#### Hardware Requirements

```
Recommended VRAM:
- 12GB: RTX 3060 (minimum)
- 16GB: RTX 4060 Ti (comfortable)
- 24GB: RTX 3090/4090 (best performance)

Higher VRAM = faster generation + higher resolution
NVIDIA GPUs preferred (better software compatibility)
```

### Midjourney vs DALL-E 3 (2025)

| Aspect | DALL-E 3 | Midjourney V7 |
|--------|----------|---------------|
| **Strength** | Prompt accuracy, text in images | Artistic quality, aesthetics |
| **Style** | Photorealistic, clean | Emotional, atmospheric |
| **Interface** | ChatGPT, API | Discord (learning curve) |
| **API Access** | Yes (official) | No official API |
| **Pricing** | $20/mo (Plus) + API | $10-60/mo tiers |
| **Best For** | Marketing, product viz | Art, storytelling |

#### When to Choose

```
DALL-E 3:
- Professional marketing materials
- Accurate product visualizations
- ChatGPT integration
- Clear commercial licensing
- API for automation

Midjourney V7:
- Artistic quality priority
- Creative exploration
- Style consistency
- Community inspiration
- High-volume, cost-effective
```

---

## Video Generation - Генерация видео

### OpenAI Sora 2

**Sora 2** (30 сентября 2025) - flagship video/audio generation model, описываемая как "GPT-3.5 moment for video".

#### Характеристики

```
Platforms: sora.com, iOS app, Android (November 2025)
API: Available (sora-2, sora-2-2025-10-06, sora-2-2025-12-08)

Capabilities:
- Accurate physics simulation
- Basketball rebounds correctly
- Buoyancy, rigidity modeling
- Olympic gymnastics routines
- Backflips on paddleboard

Audio:
- Synchronized dialogue
- Sound effects
- Automatic music generation

Safety:
- Visible watermark
- C2PA metadata
- Content moderation
```

#### Notable Events (2025)

```
December 2025: Disney $1B investment
- Access to 200+ characters (Disney, Pixar, Marvel, Star Wars)

October 2025: Japan CODA request
- Stop using copyrighted content (Studio Ghibli, Square Enix)
```

#### Earlier Sora History

```
December 2024: Gradual public release (ChatGPT Pro/Plus, US/Canada)
February 2025: Integration plans with ChatGPT
```

### Runway Gen-4.5

**Runway** - пионер AI video generation.

#### Модели (2025)

| Model | Purpose | Duration | Notes |
|-------|---------|----------|-------|
| **Gen-4.5** | SOTA quality | - | "World's best video model" |
| **Gen-4** | High fidelity | 10s | Text-to-Video |
| **Gen-3 Alpha** | Standard | 10-11s | Most features |
| **Gen-3 Alpha Turbo** | Fast/cheap | 10s | Blocking/prototyping |
| **Aleph** | Video-to-Video | - | Recommended for V2V |

#### Gen-3 Alpha Features

```
Core:
- Text to Video
- Image to Video
- Video to Video (with Aleph)

Controls:
- Motion Brush
- Advanced Camera Controls
- Director Mode
- Structure, style, motion control

Safety: Visual moderation + C2PA standards
Recognition: TIME "200 Best Inventions" 2024
```

### Pika Labs

**Pika 2.5** - short-form video creation platform с 11M+ пользователей.

#### Features (2025)

```
Pika 2.5 Core:
- 10-second videos in 1080p
- Camera control
- Character/style consistency
- Multiple styles: 3D animation, anime, cinematic, live action

Special Tools:
- Pikaframes: Image-to-video with first/last frame
- Pikaformance: Lip-sync, facial expressions (TikTok, Reels)
- Pikatwists: Twist endings
- Pikaswaps: Object replacement in video
- Pikadditions: Add elements

Pricing: Free tier (480p), paid for full features
```

### Сравнение Video Generators

| Feature | Sora 2 | Runway Gen-4 | Pika 2.5 |
|---------|--------|--------------|----------|
| **Physics** | Best | Good | Good |
| **Audio** | Native sync | No | Limited |
| **Duration** | Variable | 10s | 10s |
| **API** | Yes | Yes | No |
| **Price** | High | Medium | Low |
| **Best For** | Quality | Professional | Short-form |

---

## Voice Synthesis - Синтез голоса

### ElevenLabs

**ElevenLabs** - лидер в realistic voice synthesis с deep learning.

#### Продукты

```
Core Products:
- Text-to-Speech (TTS): 32 languages, nuanced expression
- Speech-to-Speech (STS): Voice conversion
- Voice Cloning: Instant from seconds of audio
- Voice Library: 1000+ community voices
- Conversational AI: Interactive voice agents

2025 Additions:
- February 2025: AI audiobook platform (Reader app)
- August 2025: Eleven Music (studio-grade from text)
```

#### TTS Models

| Model | Latency | Quality | Best For |
|-------|---------|---------|----------|
| **Flash v2.5** | 75ms | Good | Real-time apps |
| **Multilingual v2** | Higher | Best | Nuanced expression |

#### Key Features

```
Voice Cloning:
- Instant cloning from seconds of audio
- Multilingual cloning (speak in different language)
- Only requires few seconds to minutes of reference

Voice Settings:
- stability: Consistency (higher = more consistent)
- similarity_boost: Closeness to original
- style: Expressiveness
- use_speaker_boost: Clarity enhancement
```

#### API Usage

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")

# Text-to-Speech
audio = client.text_to_speech.convert(
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    text="Welcome to the future of voice technology.",
    model_id="eleven_multilingual_v2",
    voice_settings={
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.5,
        "use_speaker_boost": True
    }
)

# Voice Cloning
voice = client.voices.clone(
    name="My Voice",
    files=[open("sample.mp3", "rb")],
    description="Professional, warm voice"
)

cloned_audio = client.text_to_speech.convert(
    voice_id=voice.voice_id,
    text="This sounds like me!"
)
```

### OpenAI TTS

```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1-hd",  # or "tts-1" for speed
    voice="alloy",     # alloy, echo, fable, onyx, nova, shimmer
    input="The quick brown fox jumps over the lazy dog."
)

response.stream_to_file("output.mp3")
```

#### Comparison: ElevenLabs vs OpenAI TTS

| Feature | ElevenLabs | OpenAI TTS |
|---------|------------|------------|
| **Voices** | 1000+ community | 6 built-in |
| **Cloning** | Yes (instant) | Custom API |
| **Languages** | 32 | ~10 |
| **Quality** | Premium | Good |
| **Latency** | 75ms+ | ~500ms |
| **Pricing** | Usage-based | $15/1M chars |

---

## Computer Use & Automation

### Claude Computer Use

**Computer Use** - beta feature для desktop automation через vision (Anthropic).

#### Как работает

```
Process:
1. Screenshot capture -> Claude analyzes
2. Vision identifies UI elements
3. Coordinate-based mouse/keyboard actions
4. Pixel-perfect accuracy

Technology: Advanced vision + coordinate-based interaction
```

#### Supported Models (December 2025)

| Model | Tool Version | Special Features |
|-------|--------------|------------------|
| **Claude Opus 4.5** | computer_20251124 | zoom action for detail |
| Other models | computer_20250124 | Standard capabilities |

#### Benchmark Performance

```
OSWorld (screenshot-only):
- Claude 3.5 Sonnet: 14.9% (2x better than next AI)
- With more steps: 22.0%

Note: Next best AI system scored only 7.8%
```

#### API Usage

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250514",
    max_tokens=1024,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Open browser and search for 'weather today'"
        }
    ]
)
```

#### Use Cases

```
Production Applications:
- E2E UI testing (natural language test cases)
- Background information gathering
- Automated software testing
- App evaluation during development (Replit Agent)

Best For:
- Non-speed-critical tasks
- Trusted environments
- Complex UI interactions
```

#### Safety Measures

```
- Prompt injection classifiers on screenshots
- User confirmation for suspicious actions
- Sandboxed environments recommended
- May hallucinate coordinates
```

---

## Production Integration

### Top Multimodal AI Platforms

#### 1. OpenAI Platform

```python
from openai import OpenAI

client = OpenAI()

# Unified multimodal: text + image + audio
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this..."},
                {"type": "image_url", "image_url": {"url": "..."}},
                {"type": "input_audio", "input_audio": {...}}
            ]
        }
    ]
)
```

#### 2. Google Vertex AI / Gemini API

```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-3-pro")

# Multimodal input
response = model.generate_content([
    "Describe what's happening",
    uploaded_image,
    uploaded_video,
    uploaded_audio
])
```

#### 3. Azure OpenAI Service

```
Enterprise Benefits:
- SSO integration
- VNet isolation
- Compliance certifications
- Same OpenAI models
```

#### 4. Amazon Bedrock

```
Available Models:
- Claude 3.5 Sonnet
- Stable Diffusion 3.5 Large
- Amazon Titan Multimodal
- Llama 3.2 Vision
```

### LangChain Multimodal Integration

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

model = ChatOpenAI(model="gpt-4o")

message = HumanMessage(
    content=[
        {"type": "text", "text": "Describe these images"},
        {"type": "image_url", "image_url": {"url": "image1.jpg"}},
        {"type": "image_url", "image_url": {"url": "image2.jpg"}}
    ]
)

response = model.invoke([message])
```

### Best Practices

#### 1. Image Optimization

```python
from PIL import Image
import io

def optimize_image(image_path, max_size=1568):
    """Reduce tokens by resizing large images."""
    img = Image.open(image_path)

    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()
```

#### 2. Caching

```python
import hashlib
from functools import lru_cache

def hash_content(content):
    return hashlib.md5(str(content).encode()).hexdigest()

@lru_cache(maxsize=1000)
def cached_vision_analysis(content_hash, prompt):
    return api_call(prompt)
```

#### 3. Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def generate_with_retry(client, prompt, image):
    try:
        return await client.chat.completions.create(
            model="gpt-4o",
            messages=[...],
            timeout=30
        )
    except RateLimitError:
        await asyncio.sleep(60)
        raise
```

#### 4. Monitoring

```python
from dataclasses import dataclass
import time

@dataclass
class MultimodalMetrics:
    latency_ms: float
    tokens_used: int
    modalities: list[str]
    model: str
    success: bool

def track_call(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        metrics = MultimodalMetrics(
            latency_ms=(time.time() - start) * 1000,
            tokens_used=result.usage.total_tokens,
            modalities=["text", "image"],
            model=kwargs.get("model"),
            success=True
        )
        log_metrics(metrics)
        return result
    return wrapper
```

---

## Сравнительные таблицы

### Vision Models Comparison

| Model | Provider | Context | Strengths | Best For |
|-------|----------|---------|-----------|----------|
| **GPT-4o** | OpenAI | 128K | Best overall, omni | General |
| **Claude Opus 4.5** | Anthropic | 200K | Computer use, charts | Documents |
| **Gemini 3 Pro** | Google | 2M | Long video, 6h+ | Video analysis |
| **LLaVA-CoT** | Open | - | Reasoning | Research |
| **Qwen2.5-VL** | Alibaba | 1M | Multi-lang | Chinese apps |
| **Molmo 2** | Allen AI | - | Open SOTA, tracking | Open-source |

### Audio Models Comparison

| Model | Type | Languages | Latency | Open |
|-------|------|-----------|---------|------|
| **Whisper large-v3** | STT | 100+ | Medium | Yes |
| **gpt-realtime** | S2S | Many | 320ms | No |
| **ElevenLabs Flash** | TTS | 32 | 75ms | No |
| **NVIDIA Canary** | STT | Many | Low | Yes |
| **AssemblyAI Universal-2** | STT | 99+ | Low | No |

### Image Generation Comparison

| Model | Style | Resolution | API | Open |
|-------|-------|------------|-----|------|
| **DALL-E 3** | Realistic | 1024px | Yes | No |
| **FLUX.2 Pro** | Photo | 4MP | Yes | No |
| **FLUX.2 Klein** | Various | - | Yes | Yes |
| **SD 3.5 Large** | Various | 1MP | Yes | Partial |
| **Midjourney V7** | Artistic | High | No | No |

### Video Generation Comparison

| Model | Duration | Audio | Physics | API |
|-------|----------|-------|---------|-----|
| **Sora 2** | Variable | Yes | Best | Yes |
| **Runway Gen-4** | 10s | No | Good | Yes |
| **Pika 2.5** | 10s | Limited | Good | No |

---

## Заключение

### Ключевые тренды 2025

1. **Unified Models** - одна модель для всех модальностей (GPT-4o, Gemini 3)
2. **Long Context** - до 6 часов видео (Gemini), 1M+ токенов
3. **Realtime Processing** - sub-second latency для voice/video
4. **Computer Use** - AI автоматизация через vision
5. **Open-Source Catch-Up** - Molmo 2, FLUX.2 Klein, LLaVA-CoT

### Рекомендации по выбору

```
Для Vision:
- Production: GPT-4o или Claude Opus 4.5
- Open-source: Molmo 2 или LLaVA-CoT
- Long video: Gemini 3 Pro

Для Audio:
- STT accuracy: AssemblyAI Universal-2 или ElevenLabs Scribe
- Open-source STT: Whisper large-v3
- Realtime voice: gpt-realtime
- Voice synthesis: ElevenLabs

Для Image Generation:
- API integration: DALL-E 3 или FLUX.2
- Artistic: Midjourney V7
- Open-source: FLUX.2 Klein, SD 3.5

Для Video Generation:
- Quality: Sora 2
- Professional: Runway Gen-4
- Short-form: Pika 2.5
```

---

## Источники

### Vision & Multimodal
- [GPT-4 Vision Guide - DataCamp](https://www.datacamp.com/tutorial/gpt-4-vision-comprehensive-guide)
- [Claude Vision Documentation](https://docs.claude.com/en/docs/build-with-claude/vision)
- [Gemini Video Understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- [LLaVA Project](https://llava-vl.github.io/)
- [Molmo 2 - Allen AI](https://allenai.org/blog/molmo2)
- [Anthropic Claude 3.5 Announcement](https://www.anthropic.com/news/claude-3-5-sonnet)

### Audio & Speech
- [Introducing Whisper - OpenAI](https://openai.com/index/whisper/)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [Best Speech-to-Text Models 2025](https://nextlevel.ai/best-speech-to-text-models/)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [gpt-realtime Introduction](https://openai.com/index/introducing-gpt-realtime/)

### Image Generation
- [DALL-E 3 Cookbook - OpenAI](https://cookbook.openai.com/articles/what_is_new_with_dalle_3)
- [FLUX.2 - Black Forest Labs](https://bfl.ai/blog/flux-2)
- [Stable Diffusion 3 - Stability AI](https://stability.ai/news/stable-diffusion-3)
- [Midjourney vs DALL-E 2025](https://vertu.com/lifestyle/midjourney-vs-dall-e-3-the-ultimate-ai-image-generation-showdown-for-2025/)

### Video Generation
- [Sora 2 - OpenAI](https://openai.com/index/sora-2/)
- [Runway Gen-3 Alpha](https://runwayml.com/research/introducing-gen-3-alpha)
- [Pika Labs Features 2025](https://pikalabs.net/pika-ai-features/)

### Computer Use & Automation
- [Claude Computer Use Documentation](https://docs.claude.com/en/docs/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Computer Use Announcement](https://www.anthropic.com/news/3-5-models-and-computer-use)

### Production & Integration
- [Top Platforms for Multimodal AI 2025](https://thirdeyedata.ai/top-18-tools-and-platforms-for-multimodal-ai-solutions-development-in-2025-26/)
- [Best Multimodal Chat APIs - Eden AI](https://www.edenai.co/post/best-multimodal-chat-apis)
- [Google Cloud Multimodal AI](https://cloud.google.com/use-cases/multimodal-ai)
- [Gemini Video Understanding Blog](https://developers.googleblog.com/en/gemini-2-5-video-understanding/)

---

*Проверено: 2026-01-09*
