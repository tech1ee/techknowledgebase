---
title: "LLM Inference Optimization - Полное Руководство"
tags:
  - topic/ai-ml
  - inference
  - performance
  - vllm
  - tensorrt
  - quantization
  - type/concept
  - level/advanced
category: ai-ml
level: advanced
created: 2025-01-15
updated: 2026-02-13
reading_time: 52
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
sources:
  - nvidia.com
  - vllm.ai
  - github.com/sgl-project
  - arxiv.org
  - lmsys.org
related:
  - "[[mobile-ai-ml-guide]]"
  - "[[local-llms-self-hosting]]"
status: published
---

# LLM Inference Optimization: От Теории к Production

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовое понимание LLM** | Как работают модели, attention | [[llm-fundamentals]] |
| **Python** | Все примеры на Python | Любой курс Python |
| **Docker/Kubernetes** | Deployment serving engines | [[devops-overview]] |
| **GPU Basics** | VRAM, CUDA, tensor cores | Документация NVIDIA |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок в AI** | ❌ Нет | Сначала [[llm-fundamentals]] и [[local-llms-self-hosting]] |
| **AI Engineer** | ✅ Да | Глубокое погружение в оптимизацию |
| **ML Platform Engineer** | ✅ Да | Production-grade serving |
| **DevOps/SRE** | ✅ Да | Понимание специфики LLM |

### Терминология для новичков

> 💡 **Inference Optimization** = как заставить LLM отвечать быстрее и дешевле

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Inference** | Процесс генерации ответа | **Консультация** — модель "думает" и отвечает |
| **TTFT** | Time To First Token | **Время ожидания официанта** — от заказа до первого блюда |
| **TPOT** | Time Per Output Token | **Скорость подачи** — как быстро приносят остальные блюда |
| **Throughput** | Запросов в секунду | **Пропускная способность** — сколько клиентов обслуживаешь |
| **Batching** | Обработка нескольких запросов вместе | **Групповой заказ** — готовить на всех сразу эффективнее |
| **KV Cache** | Кэш промежуточных вычислений | **Память о заказе** — не пересчитывать уже известное |
| **Quantization** | Сжатие модели | **Упаковка** — меньше места, чуть хуже качество |
| **PagedAttention** | Эффективное управление памятью | **Умный склад** — экономия 60-80% памяти |
| **Speculative Decoding** | Ускорение через предсказание | **Предугадывание заказа** — подготовить заранее |

---

## Теоретические основы

> **Inference optimization** — совокупность техник ускорения и удешевления процесса генерации текста LLM при сохранении качества. Включает оптимизации на уровнях: алгоритмическом (attention), системном (memory management), аппаратном (quantization) и архитектурном (batching).

Inference LLM — это автоколебательный процесс: модель генерирует токены один за другим, каждый раз пересчитывая attention. Основные bottleneck:

| Bottleneck | Теоретическая база | Решение |
|------------|-------------------|---------|
| **Memory bandwidth** | Roofline model (Williams et al., 2009) | Quantization: 16-bit → 4-bit, 4x меньше данных |
| **Quadratic attention** | $O(n^2)$ complexity (Vaswani et al., 2017) | KV Cache: не пересчитывать уже вычисленные пары |
| **KV Cache memory** | Fragmentation как в OS memory | PagedAttention (Kwon et al., 2023): виртуальная память для KV cache |
| **Sequential decoding** | Autoregressive nature | Speculative decoding (Leviathan et al., 2022): draft + verify |
| **GPU underutilization** | Batching theory | Continuous batching (Yu et al., 2022): ORCA scheduler |

> **PagedAttention** (Kwon et al., 2023, vLLM): применяет принцип виртуальной памяти (paging) из ОС к KV Cache. Вместо выделения непрерывного блока памяти для каждого запроса, KV Cache разбивается на страницы фиксированного размера. Это устраняет фрагментацию и позволяет обслуживать на **2-4x** больше запросов одновременно.

**Ключевые метрики inference:**

| Метрика | Определение | Target (production) |
|---------|-------------|-------------------|
| **TTFT** | Time To First Token — latency до первого токена | < 500ms |
| **TPOT** | Time Per Output Token — скорость генерации | < 50ms/token |
| **Throughput** | Requests/second при заданном SLA | Зависит от нагрузки |
| **GPU Utilization** | % использования вычислительных ресурсов | > 70% |

**Quantization** уменьшает precision весов модели: FP16 → INT8 → INT4. По теории информации (Shannon, 1948), потеря точности при переходе 16→4 бит минимальна для хорошо обученных моделей, так как распределение весов имеет низкую энтропию. На практике: INT4 quantization даёт <1% деградации на большинстве бенчмарков при 4x уменьшении памяти.

См. также: [[local-llms-self-hosting|Self-Hosting]] — практика self-hosting, [[ai-cost-optimization|Cost Optimization]] — экономический аспект, [[ai-devops-deployment|AI DevOps]] — deployment.

---

## Введение: Почему это критически важно

Представьте, что у вас есть мощный спорткар (LLM), но вы застряли в пробке (плохо оптимизированный инференс). Сколько бы лошадиных сил ни было под капотом, вы никуда не едете. Именно так выглядит production-deployment LLM без оптимизации: модель есть, но пользователи ждут по 10-20 секунд ответа, а счета за GPU растут как снежный ком.

**Масштаб проблемы в 2025 году:**
- По данным Andreessen Horowitz, 49% компаний сообщают, что большая часть их compute-бюджета уходит на инференс (против 29% в 2024)
- Расходы на API моделей выросли с $3.5B до $8.4B за год
- McKinsey фиксирует рост использования GenAI в бизнесе с 33% до 67%

Оптимизация инференса - это не просто "nice to have", а критический фактор, определяющий будут ли ваши LLM-системы экономически жизнеспособны.

---

## TL;DR для занятых

> **Ключевые техники оптимизации:**
> - **Continuous Batching** - 2-23x throughput vs static batching
> - **PagedAttention** - экономия 60-80% памяти KV cache
> - **Speculative Decoding** - 2-3.5x ускорение latency без потери качества
> - **Quantization** - AWQ/GPTQ для 4-bit, FP8 для H100+
>
> **Движки (от простого к сложному):**
> 1. **vLLM** - быстрый старт, OpenAI-совместимость, 24x vs HuggingFace
> 2. **SGLang** - лучшая стабильность latency, RadixAttention
> 3. **TensorRT-LLM** - максимум производительности на NVIDIA H100/B200
>
> **Правило большого пальца:** Начните с vLLM + AWQ quantization, потом оптимизируйте под ваш use case.

---

## Глоссарий терминов

| Термин | Определение | Аналогия |
|--------|-------------|----------|
| **TTFT** | Time To First Token - время до первого токена | Время от заказа до появления официанта |
| **TPOT** | Time Per Output Token - время генерации каждого токена | Скорость подачи блюд |
| **Throughput** | Токенов/секунду при обработке запросов | Пропускная способность ресторана |
| **Goodput** | Запросов/сек в рамках SLO | Довольные клиенты в час |
| **KV Cache** | Кэш Key-Value для внимания | Записная книжка официанта |
| **Prefill** | Обработка входного промпта (compute-bound) | Чтение и понимание заказа |
| **Decode** | Генерация выходных токенов (memory-bound) | Приготовление и подача еды |
| **PagedAttention** | Paged memory для KV cache | Система бронирования столов |

---

## Архитектура LLM инференса: Понимание узких мест

Прежде чем оптимизировать, нужно понять где именно "бутылочное горлышко". LLM инференс состоит из двух принципиально разных фаз:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Inference Pipeline                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Request Queue ───▶ SCHEDULER ───▶ EXECUTION ENGINE            │
│                          │                 │                     │
│                          │                 ▼                     │
│                          │    ┌─────────────────────────────┐   │
│                          │    │  Phase 1: PREFILL           │   │
│                          │    │  • Обрабатывает весь промпт │   │
│                          │    │  • Compute-bound (GPU busy) │   │
│                          │    │  • Параллельная обработка   │   │
│                          │    └──────────────┬──────────────┘   │
│                          │                   │                   │
│                          │                   ▼                   │
│                          │    ┌─────────────────────────────┐   │
│                          │    │  Phase 2: DECODE            │   │
│                          │    │  • Генерирует по 1 токену   │   │
│                          │    │  • Memory-bound (GPU idle)  │   │
│                          │    │  • Последовательная работа  │   │
│                          │    └─────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│               ┌──────────────────────────────────────────────┐  │
│               │              KV CACHE                         │  │
│               │  Хранит K/V тензоры для всех токенов          │  │
│               │  Может занимать до 1.7GB на sequence (70B)   │  │
│               └──────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Почему decode фаза такая медленная?

**Аналогия:** Представьте конвейер по сборке автомобилей. В prefill-фазе вы одновременно обрабатываете все детали заказа (параллельно). В decode-фазе вы собираете машину по одной детали, и каждый раз должны сходить на склад за следующей деталью (memory access).

GPU предоставляет огромную вычислительную мощность, но большая часть простаивает, потому что:
1. Каждый токен требует полного forward pass
2. Нужно загрузить веса модели из памяти для каждого токена
3. Генерация строго последовательная: token N зависит от token N-1

**Ключевой инсайт:** Оптимизация инференса - это борьба с memory bandwidth bottleneck.

---

## Ключевые метрики: Что измерять

### Latency Breakdown

```
Request ─────▶ [  Queue  ] ─▶ [  TTFT  ] ─▶ [  TPOT  ] ─▶ ... ─▶ [End]
               │           │ │          │   │          │
               └───────────┘ └──────────┘   └──────────┘
                 Ожидание      Prefill        Decode (per token)

E2E Latency = Queue Time + TTFT + (Output Tokens × TPOT)

Пример для Llama 70B на H100:
• TTFT: 100-300ms (зависит от длины промпта)
• TPOT: 20-50ms/token
• 100 токенов output = 2-5 секунд total
```

### Почему важны разные метрики для разных use cases

| Use Case | Приоритет | TTFT Target | TPOT Target | Почему |
|----------|-----------|-------------|-------------|--------|
| **Chatbot** | Perceived speed | <500ms | <50ms | Пользователь видит "печатание" |
| **Code completion** | Instant feedback | <200ms | <30ms | IDE должен быть быстрым |
| **Voice assistant** | Real-time | <100ms | <20ms | Паузы заметны на слух |
| **Batch processing** | Cost efficiency | <5s | <100ms | Throughput важнее latency |
| **RAG pipeline** | Balance | <1s | <80ms | Многошаговая обработка |

---

## 1. Continuous Batching: Почему это game-changer

### Проблема Static Batching

**Аналогия:** Представьте автобус, который ждет пока все пассажиры доедут до конечной, даже если кто-то выходит раньше. Места простаивают, новые пассажиры ждут следующий автобус.

```
STATIC BATCHING (неэффективно):

Batch 1: [R1████████] [R2██████████████] [R3████]
         ↑            ↑                   ↑
         Готов рано   Самый длинный      Готов рано
         но ждёт      определяет время   но ждёт

──────────────────────────────────────────────────▶ time
         │◄────────── Весь batch ждёт ──────────►│
                   GPU простаивает!

CONTINUOUS BATCHING (эффективно):

[R1████████]──▶ done → сразу добавляем R4
[R2██████████████]────────────────▶ done → добавляем R5
[R3████]──▶ done
      [R4███████████]
            [R5██████████████████]

──────────────────────────────────────────────────▶ time
         GPU всегда занят, нет ожидания!
```

### Результаты

По данным Anyscale, continuous batching в vLLM дает **23x throughput** и снижение p50 latency по сравнению с naive подходом.

### Как это работает под капотом

Continuous batching оперирует на уровне итераций (iteration-level scheduling), а не запросов:

```python
# Псевдокод continuous batching scheduler
def schedule_iteration():
    active_batch = []

    # 1. Удаляем завершённые запросы
    for request in current_batch:
        if request.is_complete():
            yield_response(request)
        else:
            active_batch.append(request)

    # 2. Добавляем новые запросы пока есть место
    while has_capacity() and pending_queue.not_empty():
        new_request = pending_queue.pop()
        active_batch.append(new_request)

    # 3. Выполняем одну итерацию decode для всего batch
    run_forward_pass(active_batch)
```

### Включение в vLLM

```python
from vllm import LLM, SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs

engine_args = AsyncEngineArgs(
    model="meta-llama/Llama-3.1-70B-Instruct",

    # Continuous batching настройки
    max_num_seqs=256,            # Max sequences в batch
    max_num_batched_tokens=8192,  # Max токенов на итерацию

    # Scheduling
    scheduler_delay_factor=0.0,   # Немедленный scheduling
    enable_chunked_prefill=True,  # Chunked prefill для latency
)
```

---

## 2. PagedAttention: Революция в управлении памятью

### Проблема: KV Cache занимает слишком много памяти

**Аналогия:** Традиционный подход - как бронировать весь ресторан на вечер, даже если придут только 3 человека. PagedAttention - как система бронирования столов: занимаете только то, что нужно.

KV Cache для Llama-13B может занимать **до 1.7GB на одну последовательность**. При batch size 32 и 4K контексте это уже ~20GB только на кэш. А ещё нужно место для весов модели!

**Ключевая проблема:** Традиционные системы выделяют память под максимальную длину последовательности заранее, даже если реальный output будет короче. Результат: **60-80% памяти тратится впустую**.

### Как работает PagedAttention

Вдохновлено виртуальной памятью в операционных системах:

```
Традиционный KV Cache:
┌──────────────────────────────────────────────────────────────┐
│ Seq 1: [K1V1 K2V2 K3V3 K4V4 K5V5 ░░░░░░░░░░░░░░░░░░░░░░░░] │
│        └─── используется ───┘  └────── потеряно ───────┘   │
│        (5 токенов)              (выделено под 32 токена)    │
└──────────────────────────────────────────────────────────────┘

PagedAttention:
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Block 0 │ │ Block 1 │ │ Block 2 │ │ Block 3 │  ← Физические блоки
│ [K1-K16]│ │ [K17-32]│ │ [free]  │ │ [free]  │
└────┬────┘ └────┬────┘ └─────────┘ └─────────┘
     │           │
     └─────┬─────┘
           ▼
      Page Table
┌────────────────────┐
│ Seq 1: [0, 1]     │  ← Логические → Физические блоки
│ Seq 2: [1, 2]     │  ← Block 1 SHARED между Seq 1 и 2!
│ Seq 3: [0]        │
└────────────────────┘

Результат: ~4% потерь памяти vs 60-80% ранее
```

### Почему это работает

1. **Блоки фиксированного размера** - нет фрагментации памяти
2. **Аллокация по требованию** - память выделяется только когда нужна
3. **Sharing** - общие префиксы (system prompt) хранятся один раз
4. **Copy-on-write** - копируем блоки только при модификации

### Результаты

vLLM с PagedAttention показывает **до 24x throughput** по сравнению с HuggingFace Transformers и позволяет обслуживать **в 2-4x больше параллельных запросов** при том же объёме GPU памяти.

---

## 3. Prefix Caching: Переиспользование вычислений

### Идея

Если у вас 100 запросов с одинаковым system prompt, зачем вычислять его KV cache 100 раз?

**Аналогия:** Если каждый гость заказывает одинаковый салат, шеф-повар готовит одну большую порцию, а не 100 маленьких отдельно.

### Automatic Prefix Caching (APC) в vLLM

```python
from vllm import LLM

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    enable_prefix_caching=True  # Включает APC
)

# Общий system prompt
system_prompt = """You are a helpful assistant specialized in Python.
Always provide working code examples with explanations."""

# Запрос 1 - вычисляет KV cache для system_prompt
response1 = llm.generate([f"{system_prompt}\n\nUser: Write a sort function"])

# Запрос 2 - ПЕРЕИСПОЛЬЗУЕТ KV cache (быстрее!)
response2 = llm.generate([f"{system_prompt}\n\nUser: Explain decorators"])
# TTFT значительно ниже, потому что prefill для system_prompt пропущен
```

### Как работает хеширование

APC использует хеши для идентификации блоков:
- Каждый блок KV cache получает хеш на основе токенов в нём и хеша предыдущего блока (parent chaining)
- Если хеш блока N совпадает, то блоки 0..N-1 гарантированно идентичны (свойство causal attention)
- LRU eviction для управления памятью

### RadixAttention (SGLang): Умнее, чем простой prefix caching

SGLang использует Radix Tree для более эффективного кэширования:

```
Radix Tree для KV Cache:
                    [system_prompt]
                    /              \
           [few_shot_1]         [few_shot_2]
           /          \              |
    [query_A]     [query_B]     [query_C]
```

**Преимущества:**
- Автоматически находит общие префиксы
- Эффективно работает с structured workloads (few-shot, multi-turn)
- До **6.4x throughput** на benchmark задачах

**Результаты в production (Chatbot Arena):**
- 52.4% cache hit rate для LLaVA-Next-34B
- 74.1% cache hit rate для Vicuna-33B
- 1.7x снижение TTFT в среднем

---

## 4. Speculative Decoding: Параллелизм там, где его не должно быть

### Проблема

Decode фаза последовательна по природе: token N зависит от token N-1. Казалось бы, параллелизм невозможен. Но есть хитрость!

### Ключевой инсайт

Что если маленькая быстрая модель (draft) предскажет несколько токенов, а большая модель (verifier) проверит их все параллельно?

```
Стандартный Decoding (последовательный):

Large Model: [T1] → [T2] → [T3] → [T4] → [T5]
              100ms  100ms  100ms  100ms  100ms = 500ms total

Speculative Decoding:

Draft Model:  [T1 T2 T3 T4 T5]    ← Быстро генерирует 5 токенов
                   20ms

                    ↓

Large Model:  [Verify ALL]        ← Проверяет все параллельно
                   150ms

                    ↓

Result: Accept T1,T2,T3 ✓  Reject T4,T5 ✗
        → Генерируем T4 заново

Total: 170ms для 3-4 токенов vs 300-400ms стандартно = ~2x speedup
```

### Почему это работает

1. **Верификация дешевле генерации** - проверить N токенов параллельно почти так же быстро, как проверить 1
2. **Draft модель часто угадывает** - особенно для "простых" продолжений
3. **Гарантия качества** - output distribution идентична большой модели (mathematical guarantee)

### Реализация в vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",  # Target (большая)
    speculative_model="meta-llama/Llama-3.1-8B-Instruct",  # Draft (маленькая)
    num_speculative_tokens=5,  # Сколько токенов предсказывать
    speculative_draft_tensor_parallel_size=1,  # Draft на 1 GPU
    tensor_parallel_size=4  # Target на 4 GPU
)

# Greedy sampling для лучшего acceptance rate
sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=512
)

outputs = llm.generate(["Explain machine learning:"], sampling_params)
```

### Результаты (NVIDIA H200, Llama 3.3 70B)

| Draft Model | Acceptance Rate | Speedup |
|-------------|-----------------|---------|
| Llama 3.3 8B | ~75% | 2.8x |
| Llama 3.3 3B | ~65% | 3.2x |
| Llama 3.3 1B | ~55% | 3.55x |

**Trade-off:** Меньше draft модель = больше speedup, но ниже acceptance rate.

### Eagle3 - State of the Art (2025)

Современные методы типа Eagle3 используют hidden states из нескольких слоёв verifier модели для более точного draft:

> "Eagle3 draft models take the hidden states from three layers of the verifier model as input, capturing the verifier's latent features."

Google активно использует speculative decoding в AI Overviews для Search, что подтверждает production-ready статус техники.

---

## 5. Quantization: Меньше бит = Быстрее инференс

### Почему это работает

**Аналогия:** Представьте, что вместо грузовиков с полной загрузкой вы используете мотоциклы. Да, каждый везёт меньше, но они намного быстрее и их можно отправить больше за то же время.

Quantization уменьшает размер весов модели:
- FP32 (32 бита) → FP16 (16 бит) → INT8 (8 бит) → INT4 (4 бита)
- Меньше данных = быстрее загрузка из памяти = быстрее инференс

```
Размер модели 70B параметров:

FP32:  280 GB  ████████████████████████████████
FP16:  140 GB  ████████████████
INT8:   70 GB  ████████
INT4:   35 GB  ████

Speedup: ~2x на каждом уровне (при правильной реализации)
```

### Сравнение методов (2025)

| Метод | Биты | Accuracy | Speed | Лучше всего для |
|-------|------|----------|-------|-----------------|
| **FP8** | 8 | ~99.5% | 2x | H100/H200/B200 (native support) |
| **AWQ** | 4 | ~98% | 3-4x | Универсальный GPU, лучшее качество 4-bit |
| **GPTQ** | 4 | ~97% | 3-4x | Coding tasks (по некоторым бенчмаркам) |
| **GGUF** | 2-8 | varies | 2-4x | CPU/hybrid, llama.cpp |

### AWQ vs GPTQ: Что выбрать?

**AWQ (Activation-aware Weight Quantization):**
- Защищает "важные" веса на основе анализа активаций
- Не требует backpropagation (быстрее квантизировать)
- **Стабильно лучше GPTQ на 70B+ моделях**

**GPTQ:**
- Минимизирует ошибку через Hessian-based оптимизацию
- Лучше на некоторых coding benchmarks
- Требует больше данных для калибровки

> "At the 70B scale, comparing Llama-2, Llama-3.1, and Llama-3.3, AWQ consistently surpassed GPTQ, delivering stable accuracy even at 4-bit quantization."

### Практическое применение AWQ

```python
# Квантизация модели
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-3.1-70B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-70B-Instruct")

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM"
}

model.quantize(tokenizer, quant_config=quant_config, calib_data="pileval")
model.save_quantized("./llama-70b-awq")

# Использование в vLLM
from vllm import LLM
llm = LLM(model="./llama-70b-awq", quantization="awq")
```

### FP8 для H100/H200/B200

Если у вас есть доступ к новейшим NVIDIA GPU, FP8 - лучший выбор:
- Нативная аппаратная поддержка
- Минимальная потеря качества (~99.5%)
- 2x speedup без сложной калибровки

```bash
# TensorRT-LLM с FP8
trtllm-build --checkpoint_dir ./llama-70b-ckpt \
             --output_dir ./llama-70b-fp8 \
             --use_fp8_context_fmha \
             --max_batch_size 64
```

### Рекомендации по размеру модели

| Модель | GPU Memory | Рекомендация |
|--------|------------|--------------|
| 7-8B | 8-16GB | FP16 или INT8 |
| 13B | 16-24GB | INT8 или AWQ 4-bit |
| 34B | 24-48GB | AWQ 4-bit |
| 70B | 80GB (H100) | FP8 или AWQ 4-bit |
| 70B | 40GB | AWQ 4-bit + tensor parallel |
| 405B | 8×80GB | FP8 + tensor parallel |

---

## 6. FlashAttention: Оптимизация на уровне железа

### Проблема

Стандартный attention имеет квадратичную сложность по памяти O(N²) - для sequence length 4K нужно хранить матрицу 4K×4K = 16M элементов.

### Как работает FlashAttention

**Аналогия:** Вместо того чтобы построить огромный склад для всех промежуточных результатов, FlashAttention работает "потоково" - обрабатывает данные маленькими порциями, держа только необходимое в быстрой памяти GPU.

Ключевые техники:
1. **Tiling** - разбивает матрицы на блоки, которые помещаются в SRAM
2. **Kernel fusion** - объединяет операции, уменьшая memory transfers
3. **Recomputation** - иногда выгоднее пересчитать, чем хранить

### FlashAttention-3 (для H100)

FlashAttention-3 использует **до 75% максимальной производительности H100** (против 35% ранее):
- 1.5-2x быстрее FlashAttention-2
- Поддержка FP8 для ещё большего ускорения
- Асинхронные операции через warp-specialization

### Влияние на контекст

FlashAttention позволил увеличить контексты LLM с 2-4K (GPT-3) до 128K (GPT-4) и даже 1M (Llama 3):
- 10x экономия памяти при sequence length 2K
- 20x экономия при sequence length 4K
- O(N) вместо O(N²) по памяти

---

## 7. Chunked Prefill: Баланс между TTFT и TPOT

### Проблема

Prefill и decode имеют разные характеристики:
- **Prefill**: compute-bound, высокая GPU utilization
- **Decode**: memory-bound, низкая GPU utilization

Когда длинный prefill выполняется, decode запросы "голодают", и их latency непредсказуема.

### Решение: Chunked Prefill

Разбиваем длинный prefill на chunks, чередуя с decode:

```
Без chunked prefill:
[Prefill R1████████████████████] [Decode R2, R3, R4]
                                 ↑
                            Decode голодает!

С chunked prefill:
[Prefill chunk 1][Decode][Prefill chunk 2][Decode][Prefill chunk 3][Decode]
     Чередование - decode не голодает
```

### Результаты

По данным TNG Technology Consulting, chunked prefill увеличивает throughput на **+50%** для evenly sized requests.

### Настройка в vLLM

```python
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    enable_chunked_prefill=True,
    max_num_batched_tokens=2048  # Chunk size
)
```

### Trade-offs

- **Больше chunk size** → лучше TTFT, хуже TPOT consistency
- **Меньше chunk size** → лучше TPOT, немного хуже TTFT
- Рекомендация: `max_num_batched_tokens > 8192` для throughput

---

## 8. Сравнение Inference Engines (2025)

### Benchmark результаты

```
Throughput (Llama 3 70B, H100, output tokens/sec):

TensorRT-LLM  ████████████████████████████████████  ~3000 t/s
SGLang        ██████████████████████████████░░░░░░  ~2500 t/s
vLLM v1       █████████████████████████████░░░░░░░  ~2400 t/s
vLLM v0.6     ████████████████████████░░░░░░░░░░░░  ~2000 t/s
HF Transform  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~150 t/s

TTFT Latency (single request):

TensorRT-LLM  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~35-50ms
SGLang        █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~50-80ms
vLLM          ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~80-100ms
```

### vLLM: Универсальный выбор

**Когда использовать:**
- Быстрый старт и прототипирование
- OpenAI-совместимый API
- Широкая поддержка моделей из HuggingFace
- Multi-cloud deployment

**Преимущества:**
- PagedAttention из коробки
- 24x быстрее HuggingFace Transformers
- vLLM V1 engine: +24% throughput vs v0.7.3

```bash
# Запуск vLLM сервера
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 8192 \
    --quantization awq \
    --enable-chunked-prefill \
    --enable-prefix-caching
```

### SGLang: Лучшая стабильность latency

**Когда использовать:**
- Multi-turn conversations
- Structured workloads (few-shot learning)
- Когда нужна предсказуемая latency

**Преимущества:**
- RadixAttention - до 6.4x throughput на structured tasks
- TPOT стабильнее: 4-21ms vs vLLM 5-30ms
- ~10% boost над vLLM в multi-turn scenarios

```python
import sglang as sgl

llm = sgl.Engine(
    model_path="meta-llama/Llama-3.1-70B-Instruct",
    tp_size=4,
    mem_fraction_static=0.85
)

@sgl.function
def chat(s, user_message):
    s += sgl.system("You are a helpful assistant.")
    s += sgl.user(user_message)
    s += sgl.assistant(sgl.gen("response", max_tokens=512))
```

### TensorRT-LLM: Максимум производительности

**Когда использовать:**
- Enterprise NVIDIA deployment (H100/H200/B200)
- Максимальный throughput критичен
- Готовы инвестировать время в настройку

**Преимущества:**
- ~20% выше throughput чем vLLM
- Нативная FP8 поддержка
- Лучший TTFT: 35-50ms vs 50-80ms

**Недостатки:**
- Требует компиляции модели (часы-дни)
- Сложнее настройка
- Только NVIDIA GPU

```bash
# Компиляция модели (offline, занимает время)
trtllm-build --checkpoint_dir ./llama-70b-ckpt \
             --output_dir ./llama-70b-engine \
             --gemm_plugin float16 \
             --max_batch_size 64 \
             --max_input_len 2048 \
             --max_output_len 512
```

### vLLM vs Ollama

Для production: vLLM показывает **793 TPS vs Ollama 41 TPS** и **80ms p99 latency vs 673ms** при максимальной нагрузке. vLLM до **3.23x быстрее** Ollama при 128 concurrent requests.

Ollama - отличный выбор для локальной разработки, но не для production.

### Таблица выбора

| Сценарий | Рекомендация | Причина |
|----------|--------------|---------|
| Быстрый старт | vLLM | Простота, OpenAI API |
| Multi-turn chat | SGLang | RadixAttention, стабильная latency |
| Max throughput NVIDIA | TensorRT-LLM | Глубокая оптимизация |
| Локальная разработка | Ollama | Простейший setup |
| Enterprise NVIDIA | NIM | Готовый контейнер, поддержка |
| AMD GPU | vLLM + ROCm | Официальная поддержка |

---

## 9. GPU Hardware: H100 vs H200 vs B200

### Сравнение характеристик

| GPU | Memory | Bandwidth | FP8 TFLOPS | Лучше всего для |
|-----|--------|-----------|------------|-----------------|
| **H100** | 80GB HBM3 | 3.35 TB/s | 1979 | Production workhorse |
| **H200** | 141GB HBM3e | 4.8 TB/s | 1979 | Large KV cache workloads |
| **B200** | 192GB HBM3e | 8 TB/s | 4500 | Max throughput, FP4 |

### Реальные benchmark результаты

**Llama-3.1-8B на vLLM (multi-GPU):**
- H200 показывает **9-10% выше throughput** чем H100
- B200 показывает **самую низкую latency**: 2.40ms на 8 GPU

**DeepSeek 671B:**
- B200 и H100 показывают примерно равную производительность на очень больших моделях

**TensorRT-LLM, 100 concurrent requests:**
- B200: TTFT 0.234s, throughput 7,236 t/s
- Один B200 ≈ 3-4 H100 по производительности

### Когда выбирать какой GPU

| Критерий | Рекомендация |
|----------|--------------|
| Бюджет и доступность | H100 (цены падают) |
| KV cache bottleneck | H200 (76% больше памяти) |
| Tokens/sec per watt | B200 (лучшая эффективность) |
| FP4 inference | B200 (нативная поддержка) |

---

## 10. Production Deployment

### Чеклист перед запуском

```python
PRODUCTION_CHECKLIST = {
    "performance": [
        "Quantization выбран под GPU (FP8 для H100+, AWQ для остальных)",
        "Continuous batching включён",
        "Prefix caching для повторяющихся промптов",
        "Tensor parallelism настроен для модели",
        "Max sequence length ограничен реальными нуждами",
        "Chunked prefill для стабильной latency"
    ],

    "reliability": [
        "Health checks endpoint работает",
        "Graceful shutdown handling",
        "Request timeout настроен (60-120s typical)",
        "Memory OOM handling (swap space настроен)",
        "Model warmup при старте (первые запросы медленнее)"
    ],

    "observability": [
        "Prometheus metrics exposed",
        "Latency percentiles: p50, p95, p99",
        "GPU utilization monitoring",
        "KV cache utilization",
        "Request queue depth",
        "Error rate tracking"
    ],

    "scaling": [
        "Horizontal scaling готов (load balancer)",
        "Auto-scaling по queue depth / latency",
        "Sticky sessions если нужен контекст",
        "Blue-green deployment для updates"
    ]
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama-70b
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm-llama
  template:
    metadata:
      labels:
        app: vllm-llama
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
          - "--model"
          - "meta-llama/Llama-3.1-70B-Instruct"
          - "--tensor-parallel-size"
          - "4"
          - "--max-model-len"
          - "8192"
          - "--quantization"
          - "awq"
          - "--enable-chunked-prefill"
          - "--enable-prefix-caching"
        resources:
          limits:
            nvidia.com/gpu: 4
            memory: 320Gi
          requests:
            nvidia.com/gpu: 4
            memory: 256Gi
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 300  # Model loading takes time!
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 300
          periodSeconds: 5
      nodeSelector:
        gpu-type: h100
```

### Мониторинг ключевых метрик

```python
# Prometheus metrics to expose
CRITICAL_METRICS = {
    # Latency
    "vllm_request_ttft_seconds": "Histogram of TTFT",
    "vllm_request_tpot_seconds": "Histogram of time per output token",
    "vllm_request_e2e_seconds": "End-to-end request latency",

    # Throughput
    "vllm_tokens_generated_total": "Counter of generated tokens",
    "vllm_requests_completed_total": "Counter of completed requests",

    # Resources
    "vllm_gpu_memory_used_bytes": "GPU memory usage",
    "vllm_kv_cache_usage_percent": "KV cache utilization",
    "vllm_running_requests": "Current running requests",
    "vllm_waiting_requests": "Requests in queue",
}
```

---

## Реальные кейсы компаний (2025)

### Convirza: 10x снижение стоимости

- **Задача:** Анализ миллионов звонков call-центра ежемесячно
- **Решение:** Llama 3B с LoRA adapters через Predibase
- **Результат:** Sub-0.1 second inference, 10x дешевле OpenAI

### ElevenLabs: 600:1 соотношение генерации

- **Инфраструктура:** GKE с NVIDIA H100
- **Stack:** NeMo + NIM для inference optimization
- **Результат:** Генерация 600 секунд аудио за 1 секунду real-time

### Klarna: Миллионы разговоров

- **Задача:** AI-ассистент для customer service
- **Результат:** Миллионы conversations/month, значительное снижение нагрузки на операторов

### Prosus (15,000 сотрудников)

- **Система:** "Toan" - RAG-based Q&A на Amazon Bedrock
- **Результат:** Hallucination rate < 2% через iterative optimization
---

## Проверь себя

> [!question]- Какие основные bottleneck'и LLM inference и как каждый из них решается?
> Memory bandwidth (модель не помещается в GPU) --- квантизация (INT8, INT4, GPTQ, AWQ). Compute (медленная генерация) --- batching, speculative decoding, tensor parallelism. KV-cache (растёт с длиной контекста) --- PagedAttention, multi-query attention. I/O (сетевые задержки) --- prefix caching, streaming.

> [!question]- Чем vLLM отличается от TensorRT-LLM и когда использовать каждый?
> vLLM: Python-native, PagedAttention, простой деплой, лучший throughput для общих случаев. TensorRT-LLM: NVIDIA-оптимизированный, компиляция графа, максимальная производительность на NVIDIA GPU, но сложнее в настройке. vLLM для большинства проектов, TensorRT-LLM для максимального performance на NVIDIA hardware.

> [!question]- Как квантизация влияет на качество модели и throughput?
> INT8 квантизация: потеря качества <1%, throughput +50-80%, memory -50%. INT4 (GPTQ/AWQ): потеря качества 1-3%, throughput +100-200%, memory -75%. Для больших моделей (70B+) потери качества меньше. AWQ обычно даёт лучшее quality/speed соотношение чем GPTQ.

> [!question]- Что такое speculative decoding и как оно ускоряет inference?
> Маленькая "draft" модель генерирует N токенов, большая модель проверяет их за один forward pass. Если draft-токены верные --- выигрыш в N раз. Типичный speedup 2-3x при правильном подборе draft модели. Работает лучше для предсказуемого текста.

---

## Ключевые карточки

Что такое PagedAttention и зачем он нужен?
?
Техника управления KV-cache, вдохновлённая виртуальной памятью OS. Вместо pre-allocation всего context window, KV-cache аллоцируется страницами по мере необходимости. Сокращает waste памяти на 60-80%, позволяя обслуживать больше concurrent запросов.

Какие основные inference-серверы для LLM существуют?
?
vLLM (open-source, PagedAttention), TensorRT-LLM (NVIDIA-оптимизированный), SGLang (радикальный scheduling), Text Generation Inference (HuggingFace), и Triton Inference Server (multi-framework). Выбор зависит от hardware и требований к latency.

Что такое continuous batching и чем оно лучше static batching?
?
Static batching: все запросы в batch ждут самый длинный. Continuous batching: завершённые запросы покидают batch, новые добавляются без ожидания. Throughput в 10-20x выше. Реализовано в vLLM, TGI, SGLang.

Какие методы квантизации LLM существуют?
?
Post-training: GPTQ (GPU-оптимизированный), AWQ (activation-aware, лучше quality), GGUF/llama.cpp (CPU-friendly). Training-aware: QLoRA, QLORA. Форматы: INT8, INT4, FP8. AWQ и GPTQ --- основные для production GPU inference.

Что такое tensor parallelism и model parallelism?
?
Tensor parallelism: один слой модели разделяется между GPU (для больших моделей, не помещающихся в 1 GPU). Pipeline parallelism: разные слои на разных GPU (sequential). Tensor parallelism даёт меньшую latency, pipeline --- лучший throughput.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[local-llms-self-hosting]] | Практический self-hosting с оптимизацией |
| Углубиться | [[ai-fine-tuning-guide]] | Fine-tuning для оптимизированных моделей |
| Смежная тема | [[jvm-gc-tuning]] | Аналогии оптимизации runtime в JVM |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI Engineering |

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Kwon W. et al. (2023). *Efficient Memory Management for LLM Serving with PagedAttention*. SOSP. arXiv:2309.06180 | vLLM, PagedAttention |
| 2 | Yu G. et al. (2022). *ORCA: A Distributed Serving System for Transformer-Based Generative Models*. OSDI | Continuous batching |
| 3 | Leviathan Y. et al. (2022). *Fast Inference from Transformers via Speculative Decoding*. arXiv:2211.17192 | Speculative decoding |
| 4 | Williams S. et al. (2009). *Roofline: An Insightful Visual Performance Model*. CACM | Roofline model — memory vs compute bound |
| 5 | Dettmers T. et al. (2022). *GPT3.int8(): 8-bit Matrix Multiplication for Transformers*. NeurIPS | INT8 quantization |
| 6 | Vaswani A. et al. (2017). *Attention Is All You Need*. NeurIPS | Transformer architecture |

### Практические руководства

| # | Источник | Вклад |
|---|----------|-------|
| 1 | [vLLM Documentation](https://docs.vllm.ai/) | PagedAttention serving engine |
| 2 | [TensorRT-LLM — NVIDIA](https://github.com/NVIDIA/TensorRT-LLM) | GPU-optimized inference |
| 3 | [SGLang](https://github.com/sgl-project/sglang) | Radix attention, structured generation |
| 4 | [Text Generation Inference (TGI)](https://huggingface.co/docs/text-generation-inference) | HuggingFace serving |
| 5 | [llama.cpp](https://github.com/ggerganov/llama.cpp) | CPU/GPU inference, GGUF format |

*Проверено: 2026-01-09*
