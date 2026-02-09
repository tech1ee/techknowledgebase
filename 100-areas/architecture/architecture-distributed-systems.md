---
title: "Distributed Systems: CAP, consistency, Saga pattern"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/architecture
  - distributed-systems
  - cap
  - consistency
  - saga
  - type/concept
  - level/intermediate
related:
  - "[[architecture-overview]]"
  - "[[architecture-resilience-patterns]]"
  - "[[databases-transactions-acid]]"
---

# Distributed Systems: CAP, consistency, Saga pattern

> Распределённые системы — это trade-offs. Нет идеального решения, есть подходящее для контекста.

---

## TL;DR

- **CAP Theorem:** При network partition выбирай между Consistency и Availability
- **Consistency models:** Strong, Eventual, Causal — разные гарантии
- **Distributed transactions:** 2PC (блокирующий), Saga (eventual)
- **Главное:** Понимай trade-offs, выбирай осознанно

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Partition** | Network failure между узлами |
| **Consistency** | Все узлы видят одинаковые данные |
| **Availability** | Каждый запрос получает ответ |
| **Linearizability** | Самая сильная consistency — как single node |
| **Eventual Consistency** | Данные синхронизируются "в итоге" |
| **Quorum** | Минимум узлов для операции (W + R > N) |
| **Saga** | Распределённая транзакция через компенсации |
| **2PC** | Two-Phase Commit — атомарный протокол |

---

## CAP Theorem

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          CAP THEOREM                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         CONSISTENCY                                         │
│                              ▲                                              │
│                             ╱ ╲                                             │
│                            ╱   ╲                                            │
│                           ╱     ╲                                           │
│                          ╱       ╲                                          │
│                         ╱   CP    ╲                                         │
│                        ╱  Systems  ╲                                        │
│                       ╱             ╲                                       │
│                      ╱  • MongoDB    ╲                                      │
│                     ╱   • HBase       ╲                                     │
│                    ╱    • Redis       ╲                                     │
│                   ╱      (cluster)     ╲                                    │
│                  ╱─────────────────────╲                                   │
│                 ╱                       ╲                                   │
│                ╱         CA              ╲                                  │
│               ╱       (No partition)      ╲                                 │
│              ╱                             ╲                                │
│             ╱      • PostgreSQL             ╲                               │
│            ╱       • MySQL                   ╲                              │
│           ╱        (single node)              ╲                             │
│          ╱─────────────────────────────────────╲                           │
│         ╱                                       ╲                           │
│        ╱              AP Systems                 ╲                          │
│       ╱                                           ╲                         │
│      ╱   • Cassandra    • DynamoDB    • CouchDB   ╲                        │
│     ╱                                               ╲                       │
│    ▼─────────────────────────────────────────────────▶                     │
│  AVAILABILITY                                    PARTITION                  │
│                                                  TOLERANCE                  │
│                                                                             │
│  ⚠️  В реальной распределённой системе P неизбежен.                        │
│      Выбор между C и A делается для случая partition.                      │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### CAP на практике

| Система | Тип | Поведение при Partition |
|---------|-----|------------------------|
| **PostgreSQL (single)** | CA | Нет partition — не применимо |
| **PostgreSQL (sync replica)** | CP | Ждёт sync replica, может быть недоступен |
| **Cassandra** | AP | Принимает writes, разрешает конфликты позже |
| **MongoDB** | CP | Primary unavailable → election → downtime |
| **DynamoDB** | Tunable | Strong или eventual consistency per request |

---

## Consistency Models

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      CONSISTENCY SPECTRUM                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STRONG                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LINEARIZABILITY                                                    │   │
│  │  • Как single-node база                                             │   │
│  │  • Каждая операция видит результат предыдущей                      │   │
│  │  • Пример: Zookeeper, etcd                                         │   │
│  │  • Cost: Высокая latency, низкая availability                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SEQUENTIAL CONSISTENCY                                             │   │
│  │  • Операции одного клиента упорядочены                             │   │
│  │  • Разные клиенты могут видеть разный порядок                      │   │
│  │  • Пример: Некоторые in-memory databases                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CAUSAL CONSISTENCY                                                 │   │
│  │  • Причинно связанные операции упорядочены                         │   │
│  │  • Если A → B, то все видят A перед B                              │   │
│  │  • Пример: MongoDB (с causal sessions)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  WEAK                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EVENTUAL CONSISTENCY                                               │   │
│  │  • Данные синхронизируются "в конечном счёте"                      │   │
│  │  • Временно могут быть разные версии                               │   │
│  │  • Пример: Cassandra, DynamoDB (default)                           │   │
│  │  • Benefit: Высокая availability, низкая latency                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Distributed Transactions

### Two-Phase Commit (2PC)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        TWO-PHASE COMMIT (2PC)                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: PREPARE                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │               ┌──────────────┐                                      │   │
│  │               │ Coordinator  │                                      │   │
│  │               └──────┬───────┘                                      │   │
│  │                      │ PREPARE?                                     │   │
│  │           ┌──────────┼──────────┐                                   │   │
│  │           ▼          ▼          ▼                                   │   │
│  │    ┌──────────┐ ┌──────────┐ ┌──────────┐                          │   │
│  │    │ Node A   │ │ Node B   │ │ Node C   │                          │   │
│  │    │ READY ✓  │ │ READY ✓  │ │ READY ✓  │                          │   │
│  │    └──────────┘ └──────────┘ └──────────┘                          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 2: COMMIT (if all ready)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │               ┌──────────────┐                                      │   │
│  │               │ Coordinator  │                                      │   │
│  │               └──────┬───────┘                                      │   │
│  │                      │ COMMIT!                                      │   │
│  │           ┌──────────┼──────────┐                                   │   │
│  │           ▼          ▼          ▼                                   │   │
│  │    ┌──────────┐ ┌──────────┐ ┌──────────┐                          │   │
│  │    │ Node A   │ │ Node B   │ │ Node C   │                          │   │
│  │    │ COMMITTED│ │ COMMITTED│ │ COMMITTED│                          │   │
│  │    └──────────┘ └──────────┘ └──────────┘                          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ⚠️ PROBLEMS:                                                              │
│  • Blocking: Если coordinator падает после PREPARE — все ждут            │
│  • Single point of failure                                                │
│  • High latency (multiple round trips)                                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Saga Pattern

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          SAGA PATTERN                                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HAPPY PATH (все успешно)                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │    T1              T2              T3              T4               │   │
│  │  ┌─────┐         ┌─────┐         ┌─────┐         ┌─────┐           │   │
│  │  │Order│  ──▶    │Pay  │  ──▶    │Ship │  ──▶    │Email│           │   │
│  │  │Create│        │ment │         │     │         │     │           │   │
│  │  └──┬──┘         └──┬──┘         └──┬──┘         └──┬──┘           │   │
│  │     │ ✓             │ ✓             │ ✓             │ ✓            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  COMPENSATION (T3 fails)                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │    T1              T2              T3                               │   │
│  │  ┌─────┐         ┌─────┐         ┌─────┐                           │   │
│  │  │Order│  ──▶    │Pay  │  ──▶    │Ship │ ✗ FAIL                   │   │
│  │  │Create│        │ment │         │     │                           │   │
│  │  └──┬──┘         └──┬──┘         └─────┘                           │   │
│  │     │               │                │                              │   │
│  │     │               │                │ trigger compensation         │   │
│  │     │               │                ▼                              │   │
│  │     │            ┌─────┐         ┌─────┐                           │   │
│  │     │     ◀──    │Refund│  ◀──   │     │                           │   │
│  │     │            │ C2   │        │     │                           │   │
│  │     │            └─────┘         └─────┘                           │   │
│  │     ▼                                                               │   │
│  │  ┌─────┐                                                            │   │
│  │  │Cancel│                                                           │   │
│  │  │Order │                                                           │   │
│  │  │ C1   │                                                           │   │
│  │  └─────┘                                                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Types:                                                                    │
│  • Choreography: Events между сервисами                                   │
│  • Orchestration: Центральный orchestrator                                │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Saga Implementation

```python
# ✅ Orchestration-based Saga
from enum import Enum
from dataclasses import dataclass
from typing import List, Callable

class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    name: str
    execute: Callable
    compensate: Callable
    status: StepStatus = StepStatus.PENDING

class SagaOrchestrator:
    def __init__(self, steps: List[SagaStep]):
        self.steps = steps
        self.completed_steps = []

    async def execute(self, context: dict) -> bool:
        """Execute saga with compensation on failure."""
        try:
            for step in self.steps:
                print(f"Executing: {step.name}")
                await step.execute(context)
                step.status = StepStatus.COMPLETED
                self.completed_steps.append(step)

            return True

        except Exception as e:
            print(f"Saga failed at {step.name}: {e}")
            await self._compensate(context)
            return False

    async def _compensate(self, context: dict):
        """Execute compensations in reverse order."""
        for step in reversed(self.completed_steps):
            try:
                print(f"Compensating: {step.name}")
                await step.compensate(context)
                step.status = StepStatus.COMPENSATED
            except Exception as e:
                print(f"Compensation failed for {step.name}: {e}")
                # Log and alert — manual intervention needed

# Usage example
async def create_order(ctx):
    ctx["order_id"] = await order_service.create(ctx["items"])

async def cancel_order(ctx):
    await order_service.cancel(ctx["order_id"])

async def process_payment(ctx):
    ctx["payment_id"] = await payment_service.charge(
        ctx["order_id"], ctx["amount"]
    )

async def refund_payment(ctx):
    await payment_service.refund(ctx["payment_id"])

async def reserve_inventory(ctx):
    await inventory_service.reserve(ctx["order_id"], ctx["items"])

async def release_inventory(ctx):
    await inventory_service.release(ctx["order_id"])

# Create saga
order_saga = SagaOrchestrator([
    SagaStep("create_order", create_order, cancel_order),
    SagaStep("process_payment", process_payment, refund_payment),
    SagaStep("reserve_inventory", reserve_inventory, release_inventory),
])

# Execute
result = await order_saga.execute({
    "items": [{"id": 1, "qty": 2}],
    "amount": 100.00
})
```

---

## Quorum Systems

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        QUORUM CONSISTENCY                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  N = 5 (total replicas)                                                    │
│                                                                             │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                             │
│  │ R1  │  │ R2  │  │ R3  │  │ R4  │  │ R5  │                             │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘                             │
│                                                                             │
│  WRITE QUORUM (W)          READ QUORUM (R)         RULE                   │
│  ─────────────────         ───────────────         ──────────────────     │
│                                                                             │
│  Strong consistency: W + R > N                                             │
│                                                                             │
│  Example 1: W=3, R=3, N=5                                                  │
│  • Write to 3 replicas ✓                                                   │
│  • Read from 3 replicas ✓                                                  │
│  • W + R = 6 > 5 → always see latest write                                │
│                                                                             │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                             │
│  │ W✓  │  │ W✓  │  │ W✓  │  │ R✓  │  │ R✓  │                             │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘                             │
│                     │               │                                       │
│                     └───────────────┘                                       │
│                     At least 1 overlap                                      │
│                                                                             │
│  Example 2: W=1, R=1, N=5 (eventual consistency)                          │
│  • Write to 1 replica (fast!)                                              │
│  • Read from 1 replica (fast!)                                             │
│  • W + R = 2 < 5 → may read stale data                                    │
│                                                                             │
│  Trade-offs:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Config          Consistency    Write Speed    Read Speed           │   │
│  │  ─────────────   ───────────    ───────────    ──────────           │   │
│  │  W=N, R=1       Strong         Slow           Fast                  │   │
│  │  W=1, R=N       Strong         Fast           Slow                  │   │
│  │  W=Q, R=Q       Strong         Medium         Medium                │   │
│  │  W=1, R=1       Eventual       Fast           Fast                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  (Q = Quorum = (N/2)+1)                                                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Conflict Resolution

```python
# ✅ Last-Write-Wins (LWW)
class LWWRegister:
    def __init__(self):
        self.value = None
        self.timestamp = 0

    def write(self, value, timestamp):
        if timestamp > self.timestamp:
            self.value = value
            self.timestamp = timestamp

    def merge(self, other):
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp

# ✅ Vector Clocks (для causal ordering)
from collections import defaultdict

class VectorClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock = defaultdict(int)

    def increment(self):
        self.clock[self.node_id] += 1

    def update(self, other_clock: dict):
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock[node], time)
        self.increment()

    def happens_before(self, other) -> bool:
        """Check if self happened before other."""
        return all(
            self.clock[k] <= other.clock[k]
            for k in self.clock
        ) and self.clock != other.clock

    def concurrent(self, other) -> bool:
        """Check if events are concurrent (conflict)."""
        return (
            not self.happens_before(other) and
            not other.happens_before(self)
        )

# ✅ CRDT (Conflict-free Replicated Data Type)
class GCounter:
    """Grow-only counter CRDT."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts = defaultdict(int)

    def increment(self, amount: int = 1):
        self.counts[self.node_id] += amount

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: 'GCounter'):
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts[node], count)

# Usage: Each node has its own counter
# Merge happens automatically, no conflicts
node1 = GCounter("node1")
node2 = GCounter("node2")

node1.increment(5)
node2.increment(3)

# After sync
node1.merge(node2)
node2.merge(node1)

assert node1.value() == node2.value() == 8  # Always converges
```

---

## Проверь себя

<details>
<summary>1. Почему CAP теорема важна на практике?</summary>

**Ответ:**

**Суть:** При network partition (P неизбежен в распределённой системе) нужно выбрать:
- **Consistency (CP):** Отклонять запросы до восстановления связи
- **Availability (AP):** Принимать запросы, но данные могут разойтись

**На практике важно потому что:**
1. Network failures случаются (даже в одном datacenter)
2. Выбор влияет на user experience и бизнес-логику
3. Разные части системы могут требовать разных trade-offs

**Пример:**
- Баланс счёта → CP (нельзя потерять деньги)
- Feed социальной сети → AP (лучше показать старые посты)

</details>

<details>
<summary>2. Когда использовать 2PC vs Saga?</summary>

**Ответ:**

**2PC (Two-Phase Commit):**
- Сильная consistency нужна
- Все участники в одном trust boundary
- Latency не критична
- Пример: Distributed database internals

**Saga:**
- Across microservices
- Eventual consistency приемлема
- Нужна высокая availability
- Длительные транзакции
- Пример: E-commerce checkout (order → payment → shipping)

**Saga преимущества:**
- Non-blocking
- Fault-tolerant
- Better suited for microservices

**Saga недостатки:**
- Сложнее реализовать
- Нужны idempotent операции
- Eventual consistency

</details>

<details>
<summary>3. Что такое split-brain и как избежать?</summary>

**Ответ:**

**Split-brain:** При network partition две части кластера считают себя primary и принимают writes → conflict.

**Решения:**

1. **Quorum:** W > N/2, R > N/2
   - Minority partition не может принимать writes

2. **Fencing tokens:**
   - Каждый leader получает monotonic token
   - Storage отклоняет запросы с старым токеном

3. **Witness node:**
   - Третий datacenter решает кто primary

4. **Manual failover:**
   - Не делать automatic failover
   - Человек принимает решение

**Пример:** Если 5 nodes split 2-3, только partition с 3 nodes может работать (quorum).

</details>

<details>
<summary>4. Как работает eventual consistency?</summary>

**Ответ:**

**Определение:** Если нет новых updates, все replicas eventually converge к одному значению.

**Механизмы:**
1. **Anti-entropy:** Периодически сравниваем replicas
2. **Read repair:** При чтении находим inconsistency → fix
3. **Gossip protocol:** Nodes обмениваются updates

**Проблемы:**
- Read-your-writes: Можешь не увидеть свой update
- Monotonic reads: Можешь увидеть "откат" во времени

**Решения:**
- Sticky sessions (всегда читай с того же replica)
- Causal consistency (track dependencies)
- Version vectors (detect conflicts)

**Когда ОК:**
- User-generated content (posts, comments)
- Analytics data
- Caching layers

</details>

---

## Связи

- [[architecture-overview]] — обзор архитектуры
- [[architecture-resilience-patterns]] — паттерны отказоустойчивости
- [[databases-transactions-acid]] — ACID транзакции
- [[databases-replication-sharding]] — репликация БД
- [[event-driven-architecture]] — event-driven patterns

---

## Источники

- "Designing Data-Intensive Applications" by Martin Kleppmann — Chapter 5, 7, 9
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [Jepsen](https://jepsen.io/) — distributed systems testing
- [Google Spanner Paper](https://research.google/pubs/pub39966/)

---

*Проверено: 2025-12-22*
