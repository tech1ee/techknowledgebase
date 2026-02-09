# Research Report: Stacks & Queues — Teaching Approach

**Date:** 2025-12-29
**Sources Evaluated:** 25+
**Research Depth:** Deep (педагогический фокус)

## Executive Summary

Stack и Queue — линейные структуры данных с ограниченным доступом к элементам. Stack работает по принципу LIFO (Last In, First Out) — как стопка тарелок. Queue работает по FIFO (First In, First Out) — как очередь в магазине. Лучшие аналогии: для стека — PEZ-конфеты, Ctrl+Z (undo), стопка блинов; для очереди — очередь в кассу, принтер, эскалатор. Deque — двусторонняя очередь, комбинирует возможности обоих. Monotonic Stack — мощный паттерн для "Next Greater Element" задач.

---

## Key Findings for Teaching

### 1. Best Analogies for Beginners

| Concept | Analogy | Why It Works |
|---------|---------|--------------|
| **Stack (LIFO)** | Стопка тарелок в кафетерии | Можно взять только верхнюю тарелку |
| **Stack Push** | Положить тарелку сверху | Новый элемент становится top |
| **Stack Pop** | Взять верхнюю тарелку | Удаляем последний добавленный |
| **Stack Peek** | Посмотреть на верхнюю тарелку | Видим, но не убираем |
| **Queue (FIFO)** | Очередь в кассу магазина | Первый пришёл — первый обслужен |
| **Enqueue** | Встать в конец очереди | Новый элемент в rear |
| **Dequeue** | Первый в очереди уходит | Убираем из front |
| **Deque** | Метро (входы с обеих сторон) | Можно добавлять/убирать с обоих концов |
| **Circular Queue** | Карусель/Кольцевой буфер | Конец соединён с началом, нет потерь памяти |

**Дополнительные аналогии:**

| Stack | Queue |
|-------|-------|
| PEZ-конфеты (первая загружённая — последняя съеденная) | Вендинговый автомат (снизу загрузили — сверху выпадает) |
| Ctrl+Z (undo) — последнее действие отменяется первым | Принтер — документы печатаются в порядке отправки |
| Стопка блинов на тарелке | Эскалатор — первый встал, первый сошёл |
| Стопка книг на столе | Автомойка — машины проезжают по порядку |
| Покерные фишки в стопке | Очередь бутылок на конвейере |

### 2. Stack vs Queue — Core Comparison

| Aspect | Stack | Queue |
|--------|-------|-------|
| **Principle** | LIFO (Last In, First Out) | FIFO (First In, First Out) |
| **Access Points** | Один конец (top) | Два конца (front и rear) |
| **Pointers** | 1 (top) | 2 (front, rear) |
| **Operations** | push, pop, peek | enqueue, dequeue, peek |
| **Implementation** | Проще | Сложнее (два указателя) |
| **Use Case** | Undo/Redo, рекурсия, DFS | Scheduling, BFS, буферизация |

**Time Complexity (все O(1)):**

| Operation | Stack | Queue |
|-----------|-------|-------|
| Push/Enqueue | O(1) | O(1) |
| Pop/Dequeue | O(1) | O(1) |
| Peek/Front | O(1) | O(1) |
| isEmpty | O(1) | O(1) |
| Search | O(n) | O(n) |

### 3. Real-World Applications

**Stack Applications:**

| Application | How Stack is Used |
|-------------|-------------------|
| **Undo/Redo** | Каждое действие — push. Undo — pop последнего действия |
| **Browser Back/Forward** | Две стопки: back stack и forward stack |
| **Function Call Stack** | При вызове функции — push frame, при return — pop |
| **Expression Evaluation** | Postfix/Prefix expressions, калькуляторы |
| **Parenthesis Matching** | Push открывающие, pop и сравнивай закрывающие |
| **DFS (Depth-First Search)** | Можно реализовать через явный stack вместо рекурсии |
| **Backtracking** | Sudoku, лабиринты — возврат на предыдущий шаг |

**Queue Applications:**

| Application | How Queue is Used |
|-------------|-------------------|
| **OS Task Scheduling** | Процессы ждут в очереди на выполнение |
| **Print Spooler** | Документы печатаются в порядке добавления |
| **BFS (Breadth-First Search)** | Обход графа "по уровням" |
| **Message Queues** | Kafka, RabbitMQ — messages in FIFO order |
| **Request Handling** | Web servers handle requests in order |
| **Buffering** | Streaming video/audio data |
| **Call Center** | Звонки обрабатываются по очереди |

### 4. Types of Queues

**Linear Queue:**
```
FRONT                           REAR
  ↓                               ↓
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │ D │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┘

Problem: After dequeue, front moves right.
Eventually, REAR reaches end but front has empty spaces!
This wastes memory.
```

**Circular Queue:**
```
       ┌───┐
    ┌──┤ E │──┐
  ┌─┤  └───┘  │─┐
┌─┤ │    ↑    │ │─┐
│ D │    │    │ A │
└───┘  REAR   └───┘
  ↑           ↓
┌───┐       ┌───┐
│ C │←──────│ B │
└───┘ FRONT └───┘

Solution: Rear wraps around to use empty spaces at front!
Memory utilization: 100%
```

**Priority Queue:**
```
Elements have priorities. Highest priority dequeued first.
Not strictly FIFO — highest priority "cuts the line"

Use cases: Dijkstra's algorithm, job scheduling, emergency rooms
```

**Deque (Double-Ended Queue):**
```
        ┌───────────────────────┐
        │ Can add/remove here   │
        ↓                       ↓
FRONT ←→ [A][B][C][D][E] ←→ REAR
        ↑                       ↑
        │ Can add/remove here   │
        └───────────────────────┘

Can function as BOTH stack AND queue!
```

### 5. Monotonic Stack Pattern

**Что это:**
Стек, где элементы всегда упорядочены (только возрастают или только убывают).

**Когда использовать:**
- Next Greater Element
- Previous Smaller Element
- Largest Rectangle in Histogram
- Daily Temperatures
- Stock Span

**Ключевое правило:**

| Problem Type | Stack Type | Scan Direction |
|--------------|------------|----------------|
| Next Greater | Decreasing | Left → Right |
| Next Smaller | Increasing | Left → Right |
| Previous Greater | Decreasing | Left → Right |
| Previous Smaller | Increasing | Left → Right |

**Алгоритм (Pop-Record-Push):**
```
1. While stack not empty AND current violates order:
   - Pop element
   - Record answer for popped element (current is its boundary)
2. Push current element
3. For remaining elements: no boundary found (use -1 or sentinel)
```

**Визуализация (Next Greater Element):**
```
Array: [4, 5, 2, 10, 8]
Stack: [] (decreasing)

i=0: stack=[], push 4      → stack=[4]
i=1: 5 > 4, pop 4         → ans[0]=5, push 5 → stack=[5]
i=2: 2 < 5, push 2        → stack=[5,2]
i=3: 10 > 2, pop 2        → ans[2]=10
     10 > 5, pop 5        → ans[1]=10, push 10 → stack=[10]
i=4: 8 < 10, push 8       → stack=[10,8]

Remaining: ans[3]=-1, ans[4]=-1

Result: [5, 10, 10, -1, -1]
```

**Complexity Benefit:**
- Brute Force: O(n²)
- Monotonic Stack: O(n) — каждый элемент push/pop максимум 1 раз!

### 6. Common Interview Problems

| # | Problem | Difficulty | Pattern |
|---|---------|------------|---------|
| 20 | Valid Parentheses | Easy | Stack matching |
| 155 | Min Stack | Medium | Auxiliary stack |
| 232 | Implement Queue using Stacks | Easy | Two stacks |
| 225 | Implement Stack using Queues | Easy | Two queues |
| 739 | Daily Temperatures | Medium | Monotonic stack |
| 84 | Largest Rectangle in Histogram | Hard | Monotonic stack |
| 42 | Trapping Rain Water | Hard | Monotonic stack / Two pointers |
| 150 | Evaluate Reverse Polish Notation | Medium | Stack evaluation |
| 394 | Decode String | Medium | Two stacks |
| 901 | Online Stock Span | Medium | Monotonic stack |
| 622 | Design Circular Queue | Medium | Array with pointers |
| 503 | Next Greater Element II | Medium | Monotonic + circular |

**Essential (must solve):**
1. Valid Parentheses — базовый stack pattern
2. Implement Queue using Stacks — понимание LIFO → FIFO
3. Min Stack — auxiliary stack technique
4. Daily Temperatures — intro to monotonic stack

### 7. Common Mistakes and Gotchas

| Mistake | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| **Stack Underflow** | Pop from empty stack | ALWAYS check `isEmpty()` before pop |
| **Stack Overflow** | Push to full array-based stack | Check capacity or use dynamic structure |
| **Forgetting edge cases** | Empty stack, single element | Test with 0, 1, 2 elements |
| **Wrong pointer in queue** | Confusing front and rear | Draw diagram, trace carefully |
| **O(n) dequeue in array queue** | Using array.shift() in JS | Use two stacks or proper circular queue |
| **Memory leak (linked implementation)** | Not freeing popped nodes | Always free/delete removed nodes |
| **Wrong monotonic direction** | Confusion increasing vs decreasing | State invariant explicitly before coding |

**Stack Underflow Example:**
```
WRONG:
  value = stack.pop()  // Crashes if empty!

RIGHT:
  if (!stack.isEmpty()) {
      value = stack.pop()
  }
```

**Queue Dequeue Inefficiency:**
```
WRONG (JavaScript):
  queue = [1, 2, 3, 4, 5]
  queue.shift()  // O(n) — all elements shift left!

RIGHT:
  Use Deque or two-stack approach for O(1) amortized
```

### 8. Implementation Notes by Language

| Language | Stack | Queue | Notes |
|----------|-------|-------|-------|
| **Java** | `Deque<E>` (prefer over `Stack`) | `Queue<E>` interface, `ArrayDeque` | Java Stack class is legacy, use Deque |
| **Python** | `list` (append/pop) | `collections.deque` | List as queue is O(n) for popleft! |
| **Kotlin** | `ArrayDeque` | `ArrayDeque` | Same class works for both |
| **C++** | `std::stack` | `std::queue` | Deque is underlying container |
| **JavaScript** | Array (push/pop) | Array inefficient, use custom | No built-in efficient queue |

**Python Warning:**
```python
# WRONG — O(n) dequeue
queue = []
queue.append(1)
queue.pop(0)  # Shifts all elements!

# RIGHT — O(1) dequeue
from collections import deque
queue = deque()
queue.append(1)
queue.popleft()  # O(1)
```

### 9. Teaching Progression

```
LEVEL 1: Understand Concepts
├── Stack: plate stack analogy, LIFO
├── Queue: cashier line analogy, FIFO
└── Operations: push/pop, enqueue/dequeue

LEVEL 2: Basic Implementation
├── Array-based stack
├── Array-based queue
└── Linked list implementation

LEVEL 3: Classic Problems
├── Valid Parentheses
├── Implement Queue using Stacks
├── Implement Stack using Queues
└── Min Stack

LEVEL 4: Intermediate Patterns
├── Expression evaluation (RPN)
├── Decode String (nested stacks)
└── Circular Queue

LEVEL 5: Advanced
├── Monotonic Stack intro
├── Daily Temperatures
├── Next Greater Element
└── Largest Rectangle in Histogram
```

---

## Corner Cases to Always Test

**Stack:**
- Empty stack (pop/peek)
- Single element stack
- Stack with two elements (boundary)

**Queue:**
- Empty queue (dequeue/peek)
- Single element queue
- Queue with two elements
- Full circular queue (wrap-around)

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Tech Interview Handbook - Stack](https://www.techinterviewhandbook.org/algorithms/stack/) | Guide | 0.95 | Interview patterns, complexity |
| 2 | [Tech Interview Handbook - Queue](https://www.techinterviewhandbook.org/algorithms/queue/) | Guide | 0.95 | Queue patterns, corner cases |
| 3 | [GeeksforGeeks - Stack vs Queue](https://www.geeksforgeeks.org/dsa/difference-between-stack-and-queue-data-structures/) | Reference | 0.90 | Comparison table |
| 4 | [DEV.to - Monotonic Stack Pattern](https://dev.to/alex_hunter_44f4c9ed6671e/monotonic-stacks-the-pattern-that-makes-next-greater-problems-easy-jd6) | Tutorial | 0.85 | Step-by-step monotonic |
| 5 | [DEV.to - Cracking Stack/Queue Problems](https://dev.to/emmanuelayinde/cracking-stack-and-queue-leetcode-problems-a-step-by-step-guide-to-solving-leetcode-challenges-5fme) | Tutorial | 0.85 | Problem patterns |
| 6 | [GeeksforGeeks - Circular Queue](https://www.geeksforgeeks.org/dsa/advantages-of-circular-queue-over-linear-queue/) | Reference | 0.90 | Circular queue benefits |
| 7 | [Baeldung - Deque vs Stack](https://www.baeldung.com/java-deque-vs-stack) | Tutorial | 0.90 | Java implementation |
| 8 | [TutorChase - Stack Errors](https://www.tutorchase.com/answers/ib/computer-science/what-errors-can-occur-when-working-with-stacks) | Tutorial | 0.85 | Common errors |
| 9 | [CodingDrills - Stack Underflow](https://www.codingdrills.com/tutorial/stack-data-structure/debugging-stack-undeflow-errors) | Tutorial | 0.85 | Debugging tips |
| 10 | [EnjoyAlgorithms - Stack Applications](https://www.enjoyalgorithms.com/blog/application-of-stack-data-structure-in-programming/) | Tutorial | 0.85 | Real-world applications |

---

*Generated: 2025-12-29*
*Purpose: Teaching-focused research for stacks-queues.md rewrite*
