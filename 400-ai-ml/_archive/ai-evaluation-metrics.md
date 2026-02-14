---
title: "AI Evaluation: метрики качества LLM систем"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/ai-ml
  - evaluation
  - metrics
  - ragas
  - type/concept
  - level/intermediate
related:
  - "[[ai-ml-overview]]"
  - "[[ai-production-systems]]"
  - "[[rag-and-prompt-engineering]]"
reading_time: 12
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# AI Evaluation: метрики качества LLM систем

> "If you can't measure it, you can't improve it." — оценка AI систем критична для production.

---

## TL;DR

- **Evaluation** — систематическое измерение качества AI системы
- **Типы метрик:** Automated (RAGAS, BLEU), LLM-as-judge, Human evaluation
- **Для RAG:** Faithfulness, Relevance, Context Recall, Answer Correctness
- **Главное:** Измеряй до и после каждого изменения, строй eval pipeline

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Ground truth** | Эталонный правильный ответ |
| **Faithfulness** | Ответ соответствует контексту (не галлюцинация) |
| **Relevance** | Ответ отвечает на вопрос |
| **Recall** | Найден ли нужный контекст |
| **Precision** | Релевантен ли найденный контекст |
| **LLM-as-judge** | LLM оценивает ответы другой LLM |
| **RAGAS** | Framework для оценки RAG систем |
| **Benchmark** | Стандартный набор тестов для сравнения |

---

## Архитектура Evaluation Pipeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     EVALUATION PIPELINE ARCHITECTURE                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        TEST DATASET                                  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │ Question | Context (optional) | Ground Truth Answer           │  │   │
│  │  │──────────┼────────────────────┼─────────────────────────────  │  │   │
│  │  │ Q1       │ C1                 │ A1                            │  │   │
│  │  │ Q2       │ C2                 │ A2                            │  │   │
│  │  │ ...      │ ...                │ ...                           │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AI SYSTEM UNDER TEST                           │   │
│  │                                                                      │   │
│  │     Question ──▶ [RAG/LLM System] ──▶ Generated Answer              │   │
│  │                        │                                            │   │
│  │                        └──▶ Retrieved Context                       │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       EVALUATION ENGINE                             │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │   │
│  │  │   Automated    │  │  LLM-as-Judge  │  │    Human       │        │   │
│  │  │   Metrics      │  │                │  │    Review      │        │   │
│  │  │                │  │                │  │                │        │   │
│  │  │ • BLEU/ROUGE   │  │ • Faithfulness │  │ • Correctness  │        │   │
│  │  │ • Exact match  │  │ • Relevance    │  │ • Helpfulness  │        │   │
│  │  │ • F1 score     │  │ • Coherence    │  │ • Preference   │        │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │   │
│  │                                                                      │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       METRICS & DASHBOARD                           │   │
│  │                                                                      │   │
│  │   Faithfulness: 0.87    Relevance: 0.92    Latency: 1.2s           │   │
│  │   Recall: 0.78          Precision: 0.85    Cost: $0.003/query      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Метрики для RAG систем (RAGAS)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         RAGAS METRICS                                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RETRIEVAL QUALITY                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Context Recall                    Context Precision                 │   │
│  │  ┌─────────────────────┐          ┌─────────────────────┐          │   │
│  │  │ Ground Truth        │          │ Retrieved Context   │          │   │
│  │  │ ┌─────┐ ┌─────┐    │          │ ┌─────┐ ┌─────┐    │          │   │
│  │  │ │ A   │ │ B   │    │          │ │ A   │ │ X   │    │          │   │
│  │  │ └─────┘ └─────┘    │          │ └─────┘ └─────┘    │          │   │
│  │  │                     │          │                     │          │   │
│  │  │ Retrieved: A        │          │ Relevant: A         │          │   │
│  │  │ Recall = 1/2 = 50%  │          │ Precision = 1/2 = 50%│         │   │
│  │  └─────────────────────┘          └─────────────────────┘          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  GENERATION QUALITY                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Faithfulness                      Answer Relevance                 │   │
│  │  ┌─────────────────────┐          ┌─────────────────────┐          │   │
│  │  │ Context: "Paris is  │          │ Question: "Capital  │          │   │
│  │  │ the capital of      │          │ of France?"         │          │   │
│  │  │ France"             │          │                     │          │   │
│  │  │                     │          │ Answer: "Paris is   │          │   │
│  │  │ Answer: "Paris,     │          │ the capital, known  │          │   │
│  │  │ founded in 3rd      │          │ for Eiffel Tower"   │          │   │
│  │  │ century BC"         │          │                     │          │   │
│  │  │                     │          │ Relevant? ✓ Yes     │          │   │
│  │  │ Faithful? ✗ No      │          │ (answers question)  │          │   │
│  │  │ (date not in        │          └─────────────────────┘          │   │
│  │  │ context)            │                                            │   │
│  │  └─────────────────────┘                                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### RAGAS Implementation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from datasets import Dataset

# Prepare evaluation dataset
eval_data = {
    "question": [
        "What is the capital of France?",
        "When was Python created?"
    ],
    "answer": [
        "Paris is the capital of France.",
        "Python was created in 1991 by Guido van Rossum."
    ],
    "contexts": [
        ["Paris is the capital and largest city of France."],
        ["Python is a programming language created by Guido van Rossum."]
    ],
    "ground_truth": [
        "The capital of France is Paris.",
        "Python was created in 1991."
    ]
}

dataset = Dataset.from_dict(eval_data)

# Run evaluation
results = evaluate(
    dataset,
    metrics=[
        faithfulness,        # Is answer grounded in context?
        answer_relevancy,    # Does answer address question?
        context_precision,   # Is retrieved context relevant?
        context_recall,      # Did we find all needed context?
        answer_correctness   # Is answer factually correct?
    ]
)

print(results)
# {'faithfulness': 0.95, 'answer_relevancy': 0.88, ...}
```

---

## LLM-as-Judge

```python
# ✅ LLM-as-Judge implementation
from openai import OpenAI

def evaluate_with_llm(question: str, answer: str, reference: str) -> dict:
    """Use LLM to evaluate answer quality."""

    client = OpenAI()

    evaluation_prompt = f"""Evaluate the following answer against the reference.

Question: {question}

Generated Answer: {answer}

Reference Answer: {reference}

Rate on these dimensions (1-5):
1. Correctness: Is the answer factually correct?
2. Completeness: Does it cover all important points?
3. Relevance: Does it answer the actual question?
4. Clarity: Is it clear and well-written?

Respond in JSON format:
{{
    "correctness": <1-5>,
    "completeness": <1-5>,
    "relevance": <1-5>,
    "clarity": <1-5>,
    "explanation": "<brief explanation>"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": evaluation_prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

# Pairwise comparison (A/B testing)
def compare_answers(question: str, answer_a: str, answer_b: str) -> str:
    """Compare two answers and pick the better one."""

    prompt = f"""Compare these two answers to the question.

Question: {question}

Answer A: {answer_a}

Answer B: {answer_b}

Which answer is better and why? Respond with:
- "A" if Answer A is better
- "B" if Answer B is better
- "TIE" if they are equally good

Format: {{"winner": "A/B/TIE", "reason": "..."}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
```

---

## Human Evaluation

```python
# ✅ Human evaluation framework
class HumanEvaluation:
    def __init__(self, questions: list):
        self.questions = questions
        self.results = []

    def create_evaluation_batch(self, answers: list) -> list:
        """Create batch for human reviewers."""
        batch = []
        for q, a in zip(self.questions, answers):
            batch.append({
                "id": str(uuid.uuid4()),
                "question": q,
                "answer": a,
                "ratings": {
                    "correctness": None,  # 1-5
                    "helpfulness": None,  # 1-5
                    "safety": None,       # Yes/No
                    "comments": None
                }
            })
        return batch

    def calculate_inter_annotator_agreement(self, ratings: list) -> float:
        """Calculate Cohen's Kappa for agreement."""
        from sklearn.metrics import cohen_kappa_score
        # Compare ratings from multiple annotators
        return cohen_kappa_score(ratings[0], ratings[1])

# Guidelines for human evaluators
EVALUATION_GUIDELINES = """
## Rating Guidelines

### Correctness (1-5)
1 = Completely wrong or harmful
2 = Mostly incorrect
3 = Partially correct
4 = Mostly correct with minor issues
5 = Fully correct

### Helpfulness (1-5)
1 = Not helpful at all
2 = Barely helpful
3 = Somewhat helpful
4 = Helpful
5 = Very helpful, exceeds expectations

### Safety
- Yes = Safe to show to users
- No = Contains harmful/inappropriate content
"""
```

---

## Automated Metrics

### Text Similarity Metrics

```python
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
import numpy as np

# BLEU Score (translation quality)
def calculate_bleu(reference: str, candidate: str) -> float:
    """BLEU score for generation quality."""
    reference_tokens = reference.lower().split()
    candidate_tokens = candidate.lower().split()
    return sentence_bleu([reference_tokens], candidate_tokens)

# ROUGE Score (summarization quality)
def calculate_rouge(reference: str, candidate: str) -> dict:
    """ROUGE scores for text overlap."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
    scores = scorer.score(reference, candidate)
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure
    }

# Semantic Similarity (embeddings)
def semantic_similarity(text1: str, text2: str, model) -> float:
    """Cosine similarity between embeddings."""
    emb1 = model.encode(text1)
    emb2 = model.encode(text2)
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

# Exact Match
def exact_match(reference: str, candidate: str) -> bool:
    """Normalize and compare."""
    def normalize(text):
        return ' '.join(text.lower().split())
    return normalize(reference) == normalize(candidate)
```

### Classification Metrics

```python
from sklearn.metrics import precision_score, recall_score, f1_score

def evaluate_classification(y_true: list, y_pred: list) -> dict:
    """Evaluate classification tasks."""
    return {
        "accuracy": sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true),
        "precision": precision_score(y_true, y_pred, average='weighted'),
        "recall": recall_score(y_true, y_pred, average='weighted'),
        "f1": f1_score(y_true, y_pred, average='weighted')
    }

# Confusion matrix for multi-class
from sklearn.metrics import confusion_matrix
import seaborn as sns

def plot_confusion_matrix(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    sns.heatmap(cm, annot=True, xticklabels=labels, yticklabels=labels)
```

---

## Evaluation Best Practices

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION BEST PRACTICES                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. BUILD EVAL DATASET FIRST                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ✅ Before building AI system, create:                              │   │
│  │     • 50-100 representative questions                               │   │
│  │     • Ground truth answers                                          │   │
│  │     • Edge cases and failure modes                                  │   │
│  │                                                                      │   │
│  │  ❌ Don't wait until production to think about evaluation          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. MEASURE BASELINE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Before changes:                                                    │   │
│  │  • Run eval on current system                                       │   │
│  │  • Document baseline metrics                                        │   │
│  │  • Compare after each change                                        │   │
│  │                                                                      │   │
│  │  Baseline: Faithfulness=0.82, Relevance=0.85                       │   │
│  │  After RAG tuning: Faithfulness=0.91 ✓, Relevance=0.83 ✗          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. MULTIPLE METRICS                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Don't optimize for single metric:                                  │   │
│  │                                                                      │   │
│  │  Quality:  Faithfulness, Relevance, Correctness                    │   │
│  │  System:   Latency, Cost, Throughput                               │   │
│  │  Business: User satisfaction, Task completion                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. CONTINUOUS EVALUATION                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Production monitoring:                                             │   │
│  │  • Sample N% of production queries                                  │   │
│  │  • Auto-evaluate with LLM-as-judge                                 │   │
│  │  • Alert on metric degradation                                     │   │
│  │  • Weekly human review of edge cases                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Production Evaluation Pipeline

```python
# ✅ Complete evaluation pipeline
class EvaluationPipeline:
    def __init__(self, config: dict):
        self.automated_metrics = config.get("automated_metrics", [])
        self.llm_judge_enabled = config.get("llm_judge", True)
        self.sample_rate = config.get("sample_rate", 0.1)  # 10%

    async def evaluate_production_query(
        self,
        question: str,
        answer: str,
        context: list,
        latency_ms: float
    ) -> dict:
        """Evaluate a single production query."""

        # Sample based on rate
        if random.random() > self.sample_rate:
            return None

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "question_hash": hash(question),
            "latency_ms": latency_ms,
            "answer_length": len(answer),
            "context_count": len(context)
        }

        # Automated metrics
        if "answer_length_check" in self.automated_metrics:
            metrics["answer_too_short"] = len(answer) < 10
            metrics["answer_too_long"] = len(answer) > 2000

        # LLM-as-judge (async for production)
        if self.llm_judge_enabled:
            judge_result = await self.llm_judge(question, answer, context)
            metrics.update(judge_result)

        # Store for analysis
        await self.store_metrics(metrics)

        # Alert if below threshold
        if metrics.get("faithfulness", 1.0) < 0.7:
            await self.alert("Low faithfulness detected", metrics)

        return metrics

    async def llm_judge(self, question, answer, context) -> dict:
        """Quick LLM evaluation for production."""
        # Use fast model for production eval
        prompt = f"""Rate this answer (1-5) on:
1. Faithfulness: Is it grounded in context?
2. Relevance: Does it answer the question?

Question: {question}
Context: {context[:500]}...
Answer: {answer}

JSON: {{"faithfulness": N, "relevance": N}}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    async def weekly_report(self) -> dict:
        """Generate weekly evaluation report."""
        metrics = await self.get_metrics_last_week()

        return {
            "total_queries": len(metrics),
            "avg_faithfulness": np.mean([m["faithfulness"] for m in metrics]),
            "avg_relevance": np.mean([m["relevance"] for m in metrics]),
            "avg_latency_ms": np.mean([m["latency_ms"] for m in metrics]),
            "low_quality_count": sum(1 for m in metrics if m["faithfulness"] < 0.7),
            "trend": self.calculate_trend(metrics)
        }
```

---

## Benchmarks

| Benchmark | Задача | Метрики |
|-----------|--------|---------|
| **MMLU** | General knowledge | Accuracy |
| **HumanEval** | Code generation | Pass@k |
| **TruthfulQA** | Factuality | % truthful |
| **MT-Bench** | Multi-turn chat | LLM-judge score |
| **HELM** | Holistic evaluation | Multiple |

---

## Проверь себя

<details>
<summary>1. Чем Faithfulness отличается от Relevance?</summary>

**Ответ:**

**Faithfulness** (верность):
- Ответ соответствует предоставленному контексту
- Нет hallucinations
- Можно проверить по источникам
- Пример: Если контекст говорит "X = 5", ответ не должен говорить "X = 10"

**Relevance** (релевантность):
- Ответ отвечает на заданный вопрос
- Не уходит от темы
- Полезен пользователю
- Пример: На вопрос "Какая погода?" не отвечать про историю метеорологии

**Можно быть faithful, но не relevant** (цитировать контекст, но не отвечать на вопрос).

</details>

<details>
<summary>2. Почему нужны разные типы метрик?</summary>

**Ответ:**

| Тип | Плюсы | Минусы | Когда использовать |
|-----|-------|--------|-------------------|
| **Automated** | Быстро, дёшево, масштабируемо | Поверхностно, не понимает смысл | Первичный фильтр |
| **LLM-as-judge** | Понимает контекст, гибко | Стоимость, bias модели | Production sampling |
| **Human** | Золотой стандарт | Дорого, медленно, не масштабируется | Ground truth, edge cases |

**Комбинация:**
- Automated: 100% queries (fast filter)
- LLM-judge: 10% queries (quality sampling)
- Human: 1% queries (ground truth validation)

</details>

<details>
<summary>3. Как построить evaluation dataset?</summary>

**Ответ:**

**Структура:**
1. **Representative queries** — типичные вопросы пользователей
2. **Edge cases** — граничные случаи
3. **Adversarial** — попытки "сломать" систему
4. **Domain coverage** — все области применения

**Источники данных:**
- Production logs (anonymized)
- User interviews
- Domain experts
- Synthetic generation

**Размер:**
- MVP: 50-100 примеров
- Production: 500-1000 примеров
- Comprehensive: 5000+ примеров

**Обновление:** Добавляй failure cases из production.

</details>

<details>
<summary>4. Что такое LLM bias в evaluation?</summary>

**Ответ:**

**LLM-as-judge имеет biases:**

1. **Position bias** — предпочитает первый/последний вариант
2. **Verbosity bias** — длинные ответы кажутся лучше
3. **Self-preference** — GPT предпочитает GPT ответы
4. **Format bias** — структурированные ответы выше

**Как бороться:**
- Рандомизировать порядок вариантов
- Нормализовать длину при сравнении
- Использовать разные модели-судьи
- Валидировать против human eval
- Промпт инженеринг для деbiasing

</details>

---

## Ключевые карточки

Чем Faithfulness отличается от Relevance в оценке RAG-систем?
?
Faithfulness — ответ основан на предоставленном контексте (нет галлюцинаций). Relevance — ответ действительно отвечает на заданный вопрос. Можно быть faithful, но не relevant: точно цитировать контекст, но не отвечать на вопрос.

Какие четыре основные метрики использует RAGAS?
?
Context Recall (найден ли нужный контекст), Context Precision (релевантен ли найденный контекст), Faithfulness (ответ основан на контексте), Answer Relevancy (ответ отвечает на вопрос). Первые две оценивают retrieval, вторые — generation.

Что такое LLM-as-Judge и какие у него bias?
?
LLM-as-Judge — использование LLM для оценки ответов другой LLM. Основные bias: position bias (предпочитает первый/последний вариант), verbosity bias (длинные ответы кажутся лучше), self-preference (GPT предпочитает GPT-ответы), format bias (структурированные ответы выше).

Как комбинировать три типа метрик (automated, LLM-judge, human)?
?
Automated — 100% запросов (быстрый фильтр), LLM-as-judge — 10% запросов (sampling качества), Human — 1% запросов (валидация ground truth). Automated дёшево, но поверхностно; human — золотой стандарт, но не масштабируется.

Что такое Ground Truth и зачем он нужен?
?
Ground Truth — эталонный правильный ответ для тестового вопроса. Нужен для объективного измерения качества: без ground truth невозможно вычислить correctness и recall. Источники: логи продакшена, доменные эксперты, синтетическая генерация.

Какие основные LLM-бенчмарки существуют и что они измеряют?
?
MMLU — общие знания (accuracy), HumanEval — генерация кода (pass@k), TruthfulQA — фактологичность (% truthful), MT-Bench — мультитурновый чат (LLM-judge score), HELM — холистическая оценка по множеству метрик.

Что такое BLEU и ROUGE, и когда они полезны?
?
BLEU — метрика для оценки качества перевода/генерации по совпадению n-грамм с эталоном. ROUGE — метрика для оценки суммаризации по overlap текста. Обе автоматические и дешёвые, но поверхностные — не понимают семантику.

Как построить evaluation dataset для AI-системы?
?
Включить representative queries (типичные вопросы), edge cases (граничные случаи), adversarial (попытки сломать систему), domain coverage (все области). MVP: 50-100 примеров, production: 500-1000. Регулярно добавлять failure cases из продакшена.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[agent-evaluation-testing]] | Оценка и тестирование агентных систем |
| Углубиться | [[ai-observability-monitoring]] | Мониторинг качества AI в production |
| Смежная тема | [[rag-and-prompt-engineering]] | RAG-системы, качество которых оцениваем |
| Смежная тема | [[ai-fine-tuning-adaptation]] | Оценка результатов fine-tuning |
| Практика | [[ai-production-systems]] | Evaluation pipeline в production |
| Обзор | [[ai-engineering-moc]] | Вернуться к карте AI/ML раздела |

---

## Связи

- [[ai-ml-overview]] — обзор AI Engineering
- [[ai-production-systems]] — деплой и мониторинг
- [[rag-and-prompt-engineering]] — RAG системы
- [[ai-fine-tuning-adaptation]] — оценка fine-tuning

---

## Источники

- [RAGAS Documentation](https://docs.ragas.io/) — RAG evaluation
- [LangSmith](https://docs.smith.langchain.com/) — evaluation platform
- [OpenAI Evals](https://github.com/openai/evals) — evaluation framework
- [HELM Benchmark](https://crfm.stanford.edu/helm/) — holistic evaluation
- [Judging LLM-as-Judge Paper](https://arxiv.org/abs/2306.05685)

---

*Проверено: 2025-12-22*

---

*Проверено: 2026-01-09*
