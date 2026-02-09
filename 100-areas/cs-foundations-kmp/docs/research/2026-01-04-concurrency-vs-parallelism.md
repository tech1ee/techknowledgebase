# Research Report: Concurrency vs Parallelism

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Concurrency — структурирование программы для работы с несколькими задачами (dealing with). Parallelism — одновременное выполнение нескольких задач (doing). Rob Pike: "Concurrency is about structure, parallelism is about execution." Concurrency возможна на single-core (context switching), parallelism требует multi-core. CPU-bound задачи выигрывают от parallelism, IO-bound — от concurrency. Amdahl's Law: speedup ограничен sequential частью. Kotlin: Dispatchers.Default для CPU-bound, Dispatchers.IO для IO-bound, limitedParallelism для контроля.

## Key Findings

### 1. Определения (Rob Pike)

**Concurrency:**
- "Dealing with lots of things at once"
- Структурирование программы
- Композиция независимых процессов
- Возможна на single-core

**Parallelism:**
- "Doing lots of things at once"
- Одновременное выполнение
- Требует multiple cores
- Про execution, не структуру

**Ключевая фраза:**
"Concurrency is about structure, parallelism is about execution."

### 2. Визуальные аналогии

**Один повар vs много поваров:**
- Concurrency: один повар готовит несколько блюд, переключаясь
- Parallelism: несколько поваров, каждый готовит своё блюдо

**Кассиры:**
- Concurrency: один кассир быстро переключается между клиентами
- Parallelism: несколько кассиров обслуживают одновременно

### 3. CPU-bound vs IO-bound

| Тип задачи | Примеры | Лучший подход |
|------------|---------|---------------|
| **CPU-bound** | Вычисления, ML, рендеринг | Parallelism |
| **IO-bound** | Network, disk, DB | Concurrency |

**Почему:**
- CPU-bound: увеличение cores = увеличение throughput
- IO-bound: thread ждёт IO, можно делать другое

### 4. Amdahl's Law

**Формула:** S = 1 / ((1-P) + P/N)

- S = speedup
- P = parallelizable portion
- N = number of processors

**Предел:** S∞ = 1 / (1-P)

Если 90% parallelizable: max speedup = 10x (независимо от количества cores)

**Вывод:** Sequential часть — bottleneck. Нельзя бесконечно ускорять добавлением cores.

### 5. Kotlin Dispatchers

| Dispatcher | Для чего | Threads |
|------------|----------|---------|
| **Default** | CPU-bound | # cores |
| **IO** | IO-bound | 64 (или # cores) |
| **Main** | UI | 1 |

**limitedParallelism(n):**
- Создаёт view с ограниченным parallelism
- `IO.limitedParallelism(1)` — sequential execution
- Не создаёт новые threads

### 6. Комбинации

| Scenario | Concurrent? | Parallel? |
|----------|-------------|-----------|
| Single-core, multiple tasks | Yes | No |
| Multi-core, single task split | No | Yes |
| Multi-core, multiple tasks | Yes | Yes |
| Single task, single core | No | No |

### 7. Практические примеры

**Web server:**
- Concurrency: handle thousands of connections
- Parallelism: process requests on multiple cores

**Video rendering:**
- Parallelism: split frames across cores
- Less about concurrency

**Chat application:**
- Concurrency: multiple chats simultaneously
- IO-bound, single core OK

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Rob Pike: Concurrency is not Parallelism](https://go.dev/blog/waza-talk) | Talk | ★★★★★ | Original definitions |
| [Rakhim's Summary](https://rakhim.org/summary-of-concurrency-is-not-parallellism-a-talk-by-rob-pike/) | Summary | ★★★★☆ | Accessible explanation |
| [Baeldung: Concurrency vs Parallelism](https://www.baeldung.com/cs/concurrency-vs-parallelism) | Tutorial | ★★★★☆ | Clear distinctions |
| [ByteByteGo](https://bytebytego.com/guides/concurrency-is-not-parallelism/) | Visual | ★★★★★ | Great diagrams |
| [Wikipedia: Amdahl's Law](https://en.wikipedia.org/wiki/Amdahl's_law) | Reference | ★★★★☆ | Formula, history |
| [kt.academy: Dispatchers](https://kt.academy/article/cc-dispatchers) | Tutorial | ★★★★★ | Kotlin specifics |
| [Baeldung: IO vs Default Dispatcher](https://www.baeldung.com/kotlin/io-and-default-dispatcher) | Tutorial | ★★★★☆ | Practical Kotlin |

## Community Sentiment

### Positive
- Rob Pike's talk считается "must watch"
- Понимание разницы улучшает архитектурные решения
- Kotlin dispatchers хвалят за простоту

### Negative
- Терминология часто путается
- "Concurrent but not parallel" сложно для новичков
- Amdahl's Law часто игнорируется на практике

## Research Methodology
- **Queries used:** 5 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** Rob Pike, Amdahl's Law, CPU/IO bound, Kotlin Dispatchers

---

*Проверено: 2026-01-09*
