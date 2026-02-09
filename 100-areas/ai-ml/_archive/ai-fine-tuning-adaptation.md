---
title: "Fine-tuning и адаптация моделей: LoRA, QLoRA, когда и зачем"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/ai-ml
  - fine-tuning
  - lora
  - ml
  - type/concept
  - level/intermediate
related:
  - "[[ai-ml-overview]]"
  - "[[rag-and-prompt-engineering]]"
  - "[[ai-evaluation-metrics]]"
---

# Fine-tuning и адаптация моделей: LoRA, QLoRA, когда и зачем

> Fine-tuning — не первый выбор. Это последний resort, когда prompting и RAG не работают.

---

## TL;DR

- **Fine-tuning** — дообучение модели на своих данных для специфичного поведения
- **Когда нужен:** Уникальный стиль/формат, специфичная domain knowledge, latency requirements
- **LoRA/QLoRA** — эффективные методы: обучаем ~1% параметров вместо 100%
- **Главное правило:** Prompting → RAG → Fine-tuning (в таком порядке)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Fine-tuning** | Дообучение pre-trained модели на новых данных |
| **Full Fine-tuning** | Обновление всех параметров модели |
| **LoRA** | Low-Rank Adaptation — обучение малых адаптеров |
| **QLoRA** | LoRA + Quantization — ещё эффективнее |
| **PEFT** | Parameter-Efficient Fine-Tuning — общее название |
| **Adapter** | Малый обучаемый модуль, добавляемый к frozen модели |
| **Rank (r)** | Размерность LoRA матриц (чем больше, тем мощнее) |
| **Quantization** | Снижение precision весов (16bit → 4bit) |

---

## Когда нужен Fine-tuning

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   DECISION: DO YOU NEED FINE-TUNING?                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❓ Задача требует специфичного стиля/формата?                             │
│     │                                                                       │
│     ├── НЕТ → Используй Prompting                                          │
│     │                                                                       │
│     └── ДА → Можно достичь few-shot примерами?                             │
│              │                                                              │
│              ├── ДА → Используй Few-shot Prompting                         │
│              │                                                              │
│              └── НЕТ → Есть >1000 качественных примеров?                   │
│                        │                                                    │
│                        ├── НЕТ → Собирай данные или используй Prompting    │
│                        │                                                    │
│                        └── ДА → Fine-tuning может помочь                   │
│                                                                             │
│  ❓ Задача требует актуальных/специфичных знаний?                          │
│     │                                                                       │
│     ├── ДА → RAG (знания обновляемы, прозрачны)                            │
│     │                                                                       │
│     └── НЕТ → Можно через prompting                                        │
│                                                                             │
│  ❓ Критична latency (нужен быстрый ответ)?                                │
│     │                                                                       │
│     ├── ДА, и RAG слишком медленный → Fine-tuning "вшивает" знания         │
│     │                                                                       │
│     └── НЕТ → RAG + Caching                                                │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Сравнение методов адаптации

| Метод | Плюсы | Минусы | Когда использовать |
|-------|-------|--------|-------------------|
| **Prompting** | Быстро, дёшево, гибко | Ограничен контекстом | Всегда начинай с него |
| **RAG** | Актуальные данные, прозрачность | Latency, сложность | Нужны свежие/специфичные данные |
| **Fine-tuning** | Качество на узкой задаче | Дорого, данные, overfitting | Уникальный стиль, формат |

---

## Методы Fine-tuning

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     FINE-TUNING METHODS COMPARISON                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FULL FINE-TUNING                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Обновляем: ████████████████████████████████████ 100% параметров   │   │
│  │                                                                      │   │
│  │  + Максимальная адаптация                                           │   │
│  │  - Требует много GPU памяти (7B = ~56GB)                           │   │
│  │  - Риск catastrophic forgetting                                     │   │
│  │  - Долго и дорого                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  LoRA (Low-Rank Adaptation)                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Обновляем: ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0.1-1% параметров │   │
│  │                                                                      │   │
│  │  + 10-100x меньше памяти                                            │   │
│  │  + Быстрое обучение                                                 │   │
│  │  + Можно хранить много адаптеров                                    │   │
│  │  - Чуть меньше качество (обычно незаметно)                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  QLoRA (Quantized LoRA)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Обновляем: █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ~0.1% параметров  │   │
│  │  Модель: 4-bit quantized                                            │   │
│  │                                                                      │   │
│  │  + 7B модель на 1x 24GB GPU                                        │   │
│  │  + 70B модель на 2x 48GB GPU                                       │   │
│  │  + Качество близко к full fine-tuning                              │   │
│  │  - Inference чуть медленнее                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Как работает LoRA

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        LoRA MECHANISM                                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Original Weight Matrix W (frozen)                                         │
│  ┌──────────────────────────────────┐                                      │
│  │                                  │  d × k                               │
│  │         W (large)                │  (e.g., 4096 × 4096)                │
│  │                                  │                                      │
│  └──────────────────────────────────┘                                      │
│                                                                             │
│  LoRA adds low-rank decomposition:                                         │
│                                                                             │
│  ┌────────┐                                                                │
│  │   A    │  d × r                    W' = W + BA                          │
│  │(down)  │  (4096 × 16)                                                   │
│  └───┬────┘                           Trainable params:                    │
│      │                                - Original: 4096 × 4096 = 16.7M      │
│      ▼                                - LoRA (r=16): 4096×16 + 16×4096     │
│  ┌────────┐                                        = 131K (0.8%)           │
│  │   B    │  r × k                                                         │
│  │ (up)   │  (16 × 4096)                                                   │
│  └────────┘                                                                │
│                                                                             │
│  Output = W×x + B×A×x                                                      │
│           ↑       ↑                                                        │
│        frozen  trainable                                                   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Ключевые параметры LoRA

| Параметр | Типичные значения | Эффект |
|----------|-------------------|--------|
| **r (rank)** | 8, 16, 32, 64 | Больше = мощнее, но больше памяти |
| **alpha** | 16, 32, 64 | Scaling factor, обычно = 2×r |
| **target_modules** | q, k, v, o, gate, up, down | Какие слои адаптировать |
| **dropout** | 0.05-0.1 | Регуляризация |

---

## Практический Fine-tuning

### Подготовка данных

```python
# ✅ Правильный формат данных для instruction tuning
training_data = [
    {
        "instruction": "Summarize the following customer feedback",
        "input": "The product arrived late but quality was excellent...",
        "output": "Mixed feedback: delivery issues but product quality praised."
    },
    {
        "instruction": "Classify the sentiment of this review",
        "input": "Absolutely love this! Best purchase ever!",
        "output": "positive"
    }
]

# Конвертация в chat format (современный подход)
def to_chat_format(example):
    return {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{example['instruction']}\n\n{example['input']}"},
            {"role": "assistant", "content": example['output']}
        ]
    }

# Минимум данных для fine-tuning
# - 100 примеров: Минимум для заметного эффекта
# - 500-1000: Хороший баланс качество/стоимость
# - 10000+: Для серьёзной адаптации
```

### QLoRA с Hugging Face

```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 1. Quantization config (4-bit)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

# 2. Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
tokenizer.pad_token = tokenizer.eos_token

# 3. Prepare for training
model = prepare_model_for_kbit_training(model)

# 4. LoRA config
lora_config = LoraConfig(
    r=16,                          # Rank
    lora_alpha=32,                 # Scaling
    target_modules=[               # Which layers to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 5. Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 41,943,040 || all params: 8,030,261,248 || trainable%: 0.52%

# 6. Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    save_strategy="epoch",
    bf16=True,                     # Use bfloat16
    optim="paged_adamw_8bit"       # Memory-efficient optimizer
)

# 7. Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=2048,
    dataset_text_field="text"
)

trainer.train()

# 8. Save adapter (only ~100MB instead of 16GB)
model.save_pretrained("./lora-adapter")
```

### OpenAI Fine-tuning

```python
from openai import OpenAI

client = OpenAI()

# 1. Prepare JSONL file
# training_data.jsonl:
# {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
# {"messages": [...]}

# 2. Upload file
file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# 3. Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",  # Base model
    hyperparameters={
        "n_epochs": 3,
        "batch_size": "auto",
        "learning_rate_multiplier": "auto"
    }
)

# 4. Monitor progress
while True:
    status = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {status.status}")
    if status.status in ["succeeded", "failed"]:
        break
    time.sleep(60)

# 5. Use fine-tuned model
response = client.chat.completions.create(
    model=status.fine_tuned_model,  # ft:gpt-4o-mini-2024-07-18:org::abc123
    messages=[{"role": "user", "content": "..."}]
)
```

---

## Типичные ошибки

```python
# ❌ Неправильно: Слишком мало данных
dataset = [{"text": "example 1"}, {"text": "example 2"}]
# Fine-tuning с 2 примерами = overfitting

# ✅ Правильно: Минимум 100-500 примеров
dataset = load_dataset("my_data")  # 500+ examples

# ❌ Неправильно: Нет валидационного сплита
trainer.train(train_dataset=full_dataset)

# ✅ Правильно: Train/Validation split
train_dataset = dataset["train"]
eval_dataset = dataset["validation"]

# ❌ Неправильно: Слишком много эпох
training_args = TrainingArguments(num_train_epochs=20)  # Overfitting

# ✅ Правильно: 1-3 эпохи обычно достаточно
training_args = TrainingArguments(
    num_train_epochs=3,
    eval_strategy="epoch",  # Monitor validation loss
    load_best_model_at_end=True
)

# ❌ Неправильно: Не проверяем базовую модель
model.train()  # Сразу fine-tuning

# ✅ Правильно: Сначала проверь, нужен ли fine-tuning
# 1. Попробуй prompting
# 2. Попробуй few-shot
# 3. Измерь baseline метрики
# 4. Только потом fine-tuning
```

---

## Evaluation после Fine-tuning

```python
# ✅ Правильно: Comprehensive evaluation
def evaluate_fine_tuned_model(base_model, fine_tuned_model, test_data):
    results = {
        "base": {"correct": 0, "total": 0},
        "fine_tuned": {"correct": 0, "total": 0}
    }

    for example in test_data:
        # Base model
        base_output = base_model.generate(example["input"])
        if is_correct(base_output, example["expected"]):
            results["base"]["correct"] += 1
        results["base"]["total"] += 1

        # Fine-tuned model
        ft_output = fine_tuned_model.generate(example["input"])
        if is_correct(ft_output, example["expected"]):
            results["fine_tuned"]["correct"] += 1
        results["fine_tuned"]["total"] += 1

    # Calculate improvement
    base_acc = results["base"]["correct"] / results["base"]["total"]
    ft_acc = results["fine_tuned"]["correct"] / results["fine_tuned"]["total"]

    print(f"Base accuracy: {base_acc:.2%}")
    print(f"Fine-tuned accuracy: {ft_acc:.2%}")
    print(f"Improvement: {(ft_acc - base_acc):.2%}")

    # Check for regression on general tasks
    general_eval = evaluate_general_capabilities(fine_tuned_model)
    print(f"General capability retention: {general_eval:.2%}")
```

---

## Стоимость Fine-tuning

| Метод | GPU требования | Время | Стоимость (примерно) |
|-------|---------------|-------|---------------------|
| **Full FT 7B** | 8x A100 80GB | Hours | $100-500 |
| **LoRA 7B** | 1x A100 40GB | 1-2h | $10-50 |
| **QLoRA 7B** | 1x RTX 4090 24GB | 2-4h | $5-20 |
| **OpenAI FT** | Managed | 1-2h | $25 per 1M tokens |

---

## Проверь себя

<details>
<summary>1. Когда fine-tuning НЕ поможет?</summary>

**Ответ:**

Fine-tuning не поможет когда:
1. **Данные часто обновляются** → RAG лучше
2. **Мало примеров (<100)** → Few-shot prompting
3. **Нужна прозрачность** → RAG показывает источники
4. **Задача требует reasoning** → Лучше модель, не fine-tuning
5. **Нужны разные "личности"** → Prompting гибче

**Правило:** Fine-tuning меняет КАК модель отвечает, не ЧТО она знает.

</details>

<details>
<summary>2. Чем LoRA лучше полного fine-tuning?</summary>

**Ответ:**

**Преимущества LoRA:**
1. **Память:** 10-100x меньше GPU RAM
2. **Скорость:** Быстрее обучается
3. **Хранение:** Адаптер ~100MB vs модель ~16GB
4. **Модульность:** Можно менять адаптеры на лету
5. **Меньше overfitting:** Меньше параметров = меньше риск

**Когда full FT лучше:**
- Радикальная смена домена
- Критично максимальное качество
- Есть ресурсы и много данных

</details>

<details>
<summary>3. Что такое catastrophic forgetting и как избежать?</summary>

**Ответ:**

**Catastrophic forgetting** — модель забывает оригинальные способности после fine-tuning на узких данных.

**Как избежать:**
1. **Используй LoRA** — оригинальные веса не меняются
2. **Добавь general data** — mix специфичных и общих примеров
3. **Регуляризация** — weight decay, dropout
4. **Меньше эпох** — early stopping
5. **Проверяй** — тестируй на общих задачах после fine-tuning

</details>

<details>
<summary>4. Как выбрать rank (r) для LoRA?</summary>

**Ответ:**

**Эмпирические правила:**

| Задача | r | Почему |
|--------|---|--------|
| Простая (формат) | 8 | Мало изменений нужно |
| Средняя (стиль) | 16-32 | Баланс качество/эффективность |
| Сложная (домен) | 64+ | Нужно больше capacity |

**Подход:**
1. Начни с r=16
2. Если underfitting → увеличивай
3. Если overfitting → уменьшай
4. Следи за validation loss

**alpha обычно = 2×r** (например r=16, alpha=32)

</details>

---

## Связи

- [[ai-ml-overview]] — обзор AI Engineering
- [[rag-and-prompt-engineering]] — альтернатива fine-tuning
- [[ai-evaluation-metrics]] — как оценить результат
- [[ai-production-systems]] — деплой fine-tuned моделей

---

## Источники

- [LoRA Paper](https://arxiv.org/abs/2106.09685) — оригинальная статья
- [QLoRA Paper](https://arxiv.org/abs/2305.14314) — quantized LoRA
- [Hugging Face PEFT](https://huggingface.co/docs/peft) — библиотека
- [OpenAI Fine-tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Sebastian Raschka: Fine-tuning Guide](https://magazine.sebastianraschka.com/)

---

*Проверено: 2025-12-22*

---

*Проверено: 2026-01-09*
