---
title: "Алгоритмы на графах: BFS, DFS, Dijkstra"
created: 2025-12-29
modified: 2025-12-29
type: deep-dive
status: published
confidence: high
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - interview
related:
  - "[[big-o-complexity]]"
  - "[[graphs]]"
  - "[[dfs-bfs-patterns]]"
  - "[[topological-sort-pattern]]"
---

# Graph Algorithms: BFS, DFS, Dijkstra и beyond

Google Maps находит маршрут за миллисекунды среди миллионов дорог. Netflix рекомендует фильмы, анализируя связи между пользователями. Facebook находит друзей друзей. Всё это — графовые алгоритмы в действии.

---

## TL;DR

Графовые алгоритмы — основа работы с сетями и связями. **BFS** обходит по уровням (кратчайший путь в невзвешенном графе). **DFS** идёт вглубь (циклы, компоненты, топологическая сортировка). **Dijkstra** — кратчайшие пути во взвешенном графе O((V+E) log V). Ключ: выбор представления (список смежности vs матрица) и правильная структура данных (Queue для BFS, Stack/рекурсия для DFS, PriorityQueue для Dijkstra).

---

## Часть 1: Интуиция без кода

### Аналогия 1: BFS — волна на воде

Бросаешь камень в воду — волны расходятся кругами **одновременно во все стороны**.

```
Камень падает в центр:

    Время 0:        .          ← только центр
    Время 1:       .X.         ← первый круг
    Время 2:      .XXX.        ← второй круг
    Время 3:     .XXXXX.       ← третий круг

Каждый "круг" — это один уровень BFS.
Все вершины на одном уровне посещаются ПРЕЖДЕ,
чем мы переходим к следующему уровню.
```

**Применение:** Если хочешь найти **кратчайший путь** (минимум шагов) — используй BFS!

---

### Аналогия 2: DFS — исследователь лабиринта

Представь, что ты в лабиринте с одним входом. Ты **идёшь вглубь** по одному коридору, пока не упрёшься в тупик. Тогда **возвращаешься** и пробуешь другой путь.

```
Лабиринт:
┌───────────────────┐
│ START             │
│   ↓               │
│ ┌─┴─┐             │
│ │   │             │
│ ↓   ↓             │
│ A   B─────┐       │
│ │         │       │
│ ↓         ↓       │
│ C     D───E       │
│ │         │       │
│ ТУПИК     EXIT    │
└───────────────────┘

DFS путь: START → A → C → (тупик, возврат) → B → D → E → EXIT
```

**Цитата из [VisuAlgo](https://visualgo.net/en/dfsbfs):** "DFS ведёт себя так, будто ты в лабиринте с одним входом и выходом. Ты не можешь разделиться — идёшь по одному пути, пока не упрёшься."

---

### Аналогия 3: Социальные сети

**BFS — "степени удалённости" в LinkedIn:**

```
Ты → друзья (1 степень) → друзья друзей (2 степени) → ...

     ТЫ
    / | \
   A  B  C      ← 1-я степень (прямые связи)
  /|  |  |\
 D E  F  G H    ← 2-я степень
```

**DFS — "цепочка рекомендаций":**

```
Ты рекомендуешь Алексея →
  Алексей рекомендует Бориса →
    Борис рекомендует Веру →
      Вера рекомендует Галину → ...

Идём вглубь по одной "ветке" связей.
```

---

### Аналогия 4: Dijkstra — GPS-навигатор

Представь, что ты в городе и хочешь найти **самый быстрый** маршрут до работы.

```
          5 мин
    A ─────────── B
    │             │
2мин│             │3мин
    │             │
    C ─────────── D
          1 мин

Из A в D:
  Путь 1: A → B → D = 5 + 3 = 8 минут
  Путь 2: A → C → D = 2 + 1 = 3 минуты ✓ ОПТИМАЛЬНО
```

**Как работает Dijkstra:**
1. Начни с "текущей позиции" (расстояние = 0)
2. Посмотри все соседние точки
3. Выбери **ближайшую непосещённую**
4. Обнови расстояния через неё
5. Повторяй

**Ключ:** Используем **PriorityQueue** — всегда берём точку с минимальным расстоянием.

---

### Числовой пример: BFS находит кратчайший путь

**Задача:** Найти кратчайший путь от вершины 0 до вершины 5.

```
    0 ─── 1 ─── 2
    │           │
    3 ─── 4 ─── 5
```

**BFS от 0:**

```
Уровень 0: [0]         dist[0] = 0
Уровень 1: [1, 3]      dist[1] = 1, dist[3] = 1
Уровень 2: [2, 4]      dist[2] = 2, dist[4] = 2
Уровень 3: [5]         dist[5] = 3  ← ОТВЕТ!

Путь: 0 → 1 → 2 → 5 (или 0 → 3 → 4 → 5)
Длина: 3 ребра
```

**Почему BFS гарантирует кратчайший путь?**
BFS обрабатывает вершины **по уровням**. Когда мы впервые достигаем вершину — это гарантированно кратчайший путь (все более короткие пути уже обработаны).

---

### Визуализация: BFS vs DFS

```
Граф:
        1
       /|\
      0─┼─2
       \|/
        3

BFS от 0:                    DFS от 0:
Уровень 0: [0]               Стек: [0] → visit 0
Уровень 1: [1,2,3]           Стек: [1,2,3] → visit 1
Уровень 2: []                Стек: [2,3] → visit 2
                             Стек: [3] → visit 3

BFS порядок: 0, 1, 2, 3      DFS порядок: 0, 1, 2, 3 (или 0, 3, 2, 1)
(слой за слоем)              (вглубь по одной ветке)
```

**Главное отличие:**
- BFS: Queue (FIFO) — сначала добавленные, сначала обработанные
- DFS: Stack (LIFO) — последние добавленные, сначала обработанные

---

## Часть 2: Почему графовые алгоритмы сложные

### Типичные ошибки студентов

#### Ошибка 1: Забыть отметить visited

**Симптом:** Бесконечный цикл или TLE

```
// ❌ ОШИБКА: не отмечаем visited
fun bfs(graph: Map<Int, List<Int>>, start: Int) {
    val queue = ArrayDeque<Int>()
    queue.addLast(start)

    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        for (neighbor in graph[node] ?: emptyList()) {
            queue.addLast(neighbor)  // Добавляем даже посещённые!
        }
    }
}

// ✅ ПРАВИЛЬНО:
fun bfs(graph: Map<Int, List<Int>>, start: Int) {
    val visited = mutableSetOf<Int>()
    val queue = ArrayDeque<Int>()
    queue.addLast(start)
    visited.add(start)  // ← Отмечаем при добавлении!

    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                visited.add(neighbor)
                queue.addLast(neighbor)
            }
        }
    }
}
```

---

#### Ошибка 2: Отмечать visited слишком поздно

**Симптом:** Одна вершина добавляется в очередь несколько раз

```
// ❌ ОШИБКА: отмечаем при извлечении
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    visited.add(node)  // Слишком поздно!
    for (neighbor in graph[node] ?: emptyList()) {
        if (neighbor !in visited) {
            queue.addLast(neighbor)
        }
    }
}

// Проблема: если A и B оба ведут к C,
// C добавится в очередь ДВАЖДЫ!

// ✅ ПРАВИЛЬНО: отмечаем при добавлении
visited.add(start)  // До цикла!
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    for (neighbor in graph[node] ?: emptyList()) {
        if (neighbor !in visited) {
            visited.add(neighbor)  // ← Сразу при добавлении!
            queue.addLast(neighbor)
        }
    }
}
```

---

#### Ошибка 3: Путаница с представлением графа

**Симптом:** "У меня рёбра, а алгоритм ожидает список смежности"

```
// Вход: рёбра [[0,1], [1,2], [0,2]]
// Нужно: adj[0] = [1, 2], adj[1] = [0, 2], adj[2] = [1, 0]

// ❌ ОШИБКА: пытаемся итерировать по рёбрам напрямую
for (edge in edges) {
    // BFS не работает с рёбрами напрямую!
}

// ✅ ПРАВИЛЬНО: сначала строим граф
val graph = mutableMapOf<Int, MutableList<Int>>()
for ((u, v) in edges) {
    graph.getOrPut(u) { mutableListOf() }.add(v)
    graph.getOrPut(v) { mutableListOf() }.add(u)  // Для undirected
}
// Теперь можно использовать BFS/DFS
```

---

#### Ошибка 4: Использование BFS для взвешенных графов

**Симптом:** Неправильный "кратчайший" путь

```
Граф:
    A ───(10)─── B
    │            │
   (1)          (1)
    │            │
    C ───(1)──── D

BFS от A: путь A → B имеет расстояние 1 (по рёбрам)
Реальный кратчайший: A → C → D → B = 1 + 1 + 1 = 3 < 10

BFS НЕ УЧИТЫВАЕТ ВЕСА!
```

**Правило:** BFS — для невзвешенных графов. Dijkstra — для взвешенных.

---

#### Ошибка 5: Отрицательные веса в Dijkstra

**Симптом:** Неправильные расстояния

```
Граф:
    A ───(5)───→ B
    │            │
   (2)         (-4)
    ↓            ↓
    C ←─────────

Dijkstra: dist[B] = 5 (идём напрямую A → B)
Реально:  dist[B] = 2 + (-4) + ? — отрицательный цикл!

Dijkstra НЕ РАБОТАЕТ с отрицательными весами!
Используй Bellman-Ford.
```

---

#### Ошибка 6: Неправильное направление рёбер

**Симптом:** Топологическая сортировка не работает

```
// Задача: порядок курсов
// prerequisites = [[1,0], [2,1]] означает "0→1→2"

// ❌ ОШИБКА: добавляем рёбра в обратном направлении
for ((course, prereq) in prerequisites) {
    graph[course].add(prereq)  // Неправильно!
}

// ✅ ПРАВИЛЬНО: prereq → course
for ((course, prereq) in prerequisites) {
    graph[prereq].add(course)  // Стрелка от prerequisite к курсу
}
```

---

## Часть 3: Ментальные модели

### Модель 1: Структура данных определяет обход

```
┌───────────────────────────────────────────────────────┐
│            СТРУКТУРА → ПОВЕДЕНИЕ                      │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Queue (FIFO):  [1, 2, 3] → добавили 4 → [1, 2, 3, 4]│
│                 извлекаем: 1, 2, 3, 4 → BFS!         │
│                                                       │
│  Stack (LIFO):  [1, 2, 3] → добавили 4 → [1, 2, 3, 4]│
│                 извлекаем: 4, 3, 2, 1 → DFS!         │
│                                                       │
│  PriorityQueue: [(5,A), (3,B), (7,C)]                │
│                 извлекаем: B(3), A(5), C(7) → Dijkstra│
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

### Модель 2: BFS — "слой за слоем", DFS — "ветка за веткой"

```
Дерево:
        1
       /|\
      2 3 4
     /|   |
    5 6   7

BFS (по слоям):                DFS (по веткам):
Слой 0: [1]                    Ветка 1: 1 → 2 → 5
Слой 1: [2, 3, 4]              Ветка 2: 1 → 2 → 6
Слой 2: [5, 6, 7]              Ветка 3: 1 → 4 → 7

Порядок: 1, 2, 3, 4, 5, 6, 7   Порядок: 1, 2, 5, 6, 3, 4, 7
```

---

### Модель 3: Когда что использовать

```
┌─────────────────────────────────────────────────────────┐
│               ВЫБОР АЛГОРИТМА                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Кратчайший путь (невзвешенный) → BFS                   │
│ Кратчайший путь (взвешенный, +) → Dijkstra             │
│ Кратчайший путь (взвешенный, ±) → Bellman-Ford         │
│                                                         │
│ Обнаружение цикла → DFS + состояния (WHITE/GRAY/BLACK)│
│ Топологическая сортировка → DFS или Kahn's BFS         │
│ Компоненты связности → DFS/BFS + visited               │
│ Сильносвязные компоненты → Kosaraju/Tarjan (DFS)      │
│                                                         │
│ Проверка двудольности → BFS/DFS + 2-раскраска         │
│ Минимальное остовное дерево → Prim/Kruskal             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Модель 4: Три состояния вершины (для обнаружения циклов)

```
Состояния:
- WHITE (не посещена): ещё не видели
- GRAY (в обработке): начали обход, но не завершили
- BLACK (завершена): полностью обработана

ЦИКЛ = нашли ребро к GRAY вершине!

      A (GRAY)
     / \
    B   C (GRAY) ← если D ведёт к C, это цикл!
   /
  D
```

**Код:**

```kotlin
enum class Color { WHITE, GRAY, BLACK }

fun hasCycle(graph: Map<Int, List<Int>>): Boolean {
    val color = mutableMapOf<Int, Color>().withDefault { Color.WHITE }

    fun dfs(node: Int): Boolean {
        color[node] = Color.GRAY
        for (neighbor in graph[node] ?: emptyList()) {
            if (color.getValue(neighbor) == Color.GRAY) return true  // Цикл!
            if (color.getValue(neighbor) == Color.WHITE && dfs(neighbor)) return true
        }
        color[node] = Color.BLACK
        return false
    }

    return graph.keys.any { color.getValue(it) == Color.WHITE && dfs(it) }
}
```

---

### Модель 5: Шаблоны BFS и DFS

**BFS шаблон:**

```kotlin
fun bfs(graph: Map<Int, List<Int>>, start: Int) {
    val visited = mutableSetOf(start)
    val queue = ArrayDeque<Int>()
    queue.addLast(start)

    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        // Обработка node

        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                visited.add(neighbor)
                queue.addLast(neighbor)
            }
        }
    }
}
```

**DFS шаблон (рекурсия):**

```kotlin
fun dfs(graph: Map<Int, List<Int>>, start: Int, visited: MutableSet<Int>) {
    visited.add(start)
    // Обработка start

    for (neighbor in graph[start] ?: emptyList()) {
        if (neighbor !in visited) {
            dfs(graph, neighbor, visited)
        }
    }
}
```

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Graph** | Множество вершин (V) и рёбер (E) |
| **Vertex/Node** | Вершина графа |
| **Edge** | Ребро, соединяющее две вершины |
| **Directed** | Ориентированный граф (рёбра имеют направление) |
| **Undirected** | Неориентированный граф |
| **Weighted** | Взвешенный граф (рёбра имеют вес) |
| **Cycle** | Путь, начинающийся и заканчивающийся в одной вершине |
| **DAG** | Directed Acyclic Graph — ориентированный ациклический граф |
| **Connected** | Все вершины достижимы друг из друга |
| **Sparse** | Мало рёбер (E ≈ V) |
| **Dense** | Много рёбер (E ≈ V²) |

---

## Представление графов

### Adjacency Matrix

```
ГРАФ:                    МАТРИЦА:
    0 --- 1                  0  1  2  3
    |     |              0 [ 0  1  1  0 ]
    2 --- 3              1 [ 1  0  0  1 ]
                         2 [ 1  0  0  1 ]
                         3 [ 0  1  1  0 ]
```

**Kotlin:**

```kotlin
class GraphMatrix(private val size: Int) {
    private val matrix = Array(size) { IntArray(size) }

    fun addEdge(u: Int, v: Int, weight: Int = 1) {
        matrix[u][v] = weight
        matrix[v][u] = weight  // Для undirected
    }

    fun hasEdge(u: Int, v: Int): Boolean = matrix[u][v] != 0

    fun getNeighbors(u: Int): List<Int> =
        matrix[u].indices.filter { matrix[u][it] != 0 }
}
```

### Adjacency List

```
ГРАФ:                    СПИСОК:
    0 --- 1              0: [1, 2]
    |     |              1: [0, 3]
    2 --- 3              2: [0, 3]
                         3: [1, 2]
```

**Kotlin:**

```kotlin
class GraphList {
    private val adj = mutableMapOf<Int, MutableList<Int>>()

    fun addEdge(u: Int, v: Int) {
        adj.getOrPut(u) { mutableListOf() }.add(v)
        adj.getOrPut(v) { mutableListOf() }.add(u)  // Для undirected
    }

    fun getNeighbors(u: Int): List<Int> = adj[u] ?: emptyList()
}
```

**Java:**

```java
class GraphList {
    private Map<Integer, List<Integer>> adj = new HashMap<>();

    public void addEdge(int u, int v) {
        adj.computeIfAbsent(u, k -> new ArrayList<>()).add(v);
        adj.computeIfAbsent(v, k -> new ArrayList<>()).add(u);
    }

    public List<Integer> getNeighbors(int u) {
        return adj.getOrDefault(u, Collections.emptyList());
    }
}
```

**Python:**

```python
from collections import defaultdict

class GraphList:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u: int, v: int):
        self.adj[u].append(v)
        self.adj[v].append(u)  # Для undirected

    def get_neighbors(self, u: int) -> list:
        return self.adj[u]
```

### Сравнение представлений

| Операция | Matrix | List |
|----------|--------|------|
| Space | O(V²) | O(V + E) |
| Check edge | O(1) | O(degree) |
| Find neighbors | O(V) | O(degree) |
| Add edge | O(1) | O(1) |
| Best for | Dense | Sparse |

**Правило:** Для интервью чаще используй **adjacency list** (или hash of hashes).

---

## BFS: Breadth-First Search

### Концепция

```
BFS: обход по уровням (level by level)

Начало с вершины 0:

Level 0:     [0]
              ↓
Level 1:   [1, 2]
            ↓   ↓
Level 2:  [3]  [4]

Порядок посещения: 0 → 1 → 2 → 3 → 4
```

### Визуализация с Queue

```
       1 --- 2
      /|     |\
     0 |     | 5
      \|     |/
       3 --- 4

BFS от 0:

Step 0: Queue=[0], Visited={0}
Step 1: Pop 0, add neighbors → Queue=[1,3], Visited={0,1,3}
Step 2: Pop 1, add neighbors → Queue=[3,2], Visited={0,1,3,2}
Step 3: Pop 3, add neighbors → Queue=[2,4], Visited={0,1,3,2,4}
Step 4: Pop 2, add neighbors → Queue=[4,5], Visited={0,1,3,2,4,5}
Step 5: Pop 4, skip (neighbors visited)
Step 6: Pop 5, done

Result: [0, 1, 3, 2, 4, 5]
```

### Реализация

**Kotlin:**

```kotlin
fun bfs(graph: Map<Int, List<Int>>, start: Int): List<Int> {
    val visited = mutableSetOf<Int>()
    val queue = ArrayDeque<Int>()
    val result = mutableListOf<Int>()

    queue.addLast(start)
    visited.add(start)

    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        result.add(node)

        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                visited.add(neighbor)
                queue.addLast(neighbor)
            }
        }
    }

    return result
}
```

**Java:**

```java
public List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
    Set<Integer> visited = new HashSet<>();
    Queue<Integer> queue = new LinkedList<>();
    List<Integer> result = new ArrayList<>();

    queue.offer(start);
    visited.add(start);

    while (!queue.isEmpty()) {
        int node = queue.poll();
        result.add(node);

        for (int neighbor : graph.getOrDefault(node, List.of())) {
            if (!visited.contains(neighbor)) {
                visited.add(neighbor);
                queue.offer(neighbor);
            }
        }
    }

    return result;
}
```

**Python:**

```python
from collections import deque

def bfs(graph: dict, start: int) -> list:
    visited = set()
    queue = deque([start])
    result = []

    visited.add(start)

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result
```

### BFS для Shortest Path

```kotlin
fun shortestPath(graph: Map<Int, List<Int>>, start: Int, end: Int): Int {
    if (start == end) return 0

    val visited = mutableSetOf<Int>()
    val queue = ArrayDeque<Pair<Int, Int>>()  // (node, distance)

    queue.addLast(start to 0)
    visited.add(start)

    while (queue.isNotEmpty()) {
        val (node, dist) = queue.removeFirst()

        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor == end) return dist + 1

            if (neighbor !in visited) {
                visited.add(neighbor)
                queue.addLast(neighbor to dist + 1)
            }
        }
    }

    return -1  // Путь не найден
}
```

### Complexity

- **Time:** O(V + E) — каждая вершина и ребро посещаются один раз
- **Space:** O(V) — queue и visited set

---

## DFS: Depth-First Search

### Концепция

```
DFS: идём максимально глубоко, затем backtrack

       1 --- 2
      /|     |\
     0 |     | 5
      \|     |/
       3 --- 4

DFS от 0 (выбираем первого соседа):

0 → 1 → 2 → 4 → 3 (backtrack) → 5

Stack visualization:
[0] → [0,1] → [0,1,2] → [0,1,2,4] → [0,1,2,4,3]
                                    ↓ backtrack
                        [0,1,2,4] → [0,1,2,5] → done
```

### Рекурсивная реализация

**Kotlin:**

```kotlin
fun dfs(graph: Map<Int, List<Int>>, start: Int): List<Int> {
    val visited = mutableSetOf<Int>()
    val result = mutableListOf<Int>()

    fun dfsHelper(node: Int) {
        visited.add(node)
        result.add(node)

        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                dfsHelper(neighbor)
            }
        }
    }

    dfsHelper(start)
    return result
}
```

**Java:**

```java
public List<Integer> dfs(Map<Integer, List<Integer>> graph, int start) {
    Set<Integer> visited = new HashSet<>();
    List<Integer> result = new ArrayList<>();
    dfsHelper(graph, start, visited, result);
    return result;
}

private void dfsHelper(Map<Integer, List<Integer>> graph, int node,
                       Set<Integer> visited, List<Integer> result) {
    visited.add(node);
    result.add(node);

    for (int neighbor : graph.getOrDefault(node, List.of())) {
        if (!visited.contains(neighbor)) {
            dfsHelper(graph, neighbor, visited, result);
        }
    }
}
```

**Python:**

```python
def dfs(graph: dict, start: int) -> list:
    visited = set()
    result = []

    def dfs_helper(node: int):
        visited.add(node)
        result.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs_helper(neighbor)

    dfs_helper(start)
    return result
```

### Итеративная реализация (с explicit stack)

**Kotlin:**

```kotlin
fun dfsIterative(graph: Map<Int, List<Int>>, start: Int): List<Int> {
    val visited = mutableSetOf<Int>()
    val stack = ArrayDeque<Int>()
    val result = mutableListOf<Int>()

    stack.addLast(start)

    while (stack.isNotEmpty()) {
        val node = stack.removeLast()

        if (node in visited) continue
        visited.add(node)
        result.add(node)

        // Добавляем в обратном порядке для правильного обхода
        for (neighbor in (graph[node] ?: emptyList()).reversed()) {
            if (neighbor !in visited) {
                stack.addLast(neighbor)
            }
        }
    }

    return result
}
```

### BFS vs DFS

| Aspect | BFS | DFS |
|--------|-----|-----|
| Structure | Queue | Stack/Recursion |
| Order | Level by level | Deep first |
| Shortest Path | Yes (unweighted) | No |
| Memory | O(width) | O(depth) |
| Use Cases | Shortest path, levels | Cycle detection, topological |

---

## Cycle Detection

### Undirected Graph

**Идея:** Если встретили visited вершину, которая НЕ parent текущей → cycle.

```
    0 --- 1
    |     |
    2 --- 3

DFS от 0: 0 → 1 → 3 → 2
При проверке соседей 2: видим 0 (visited, но parent=3, не 0)
→ Цикл найден!
```

**Kotlin:**

```kotlin
fun hasCycleUndirected(graph: Map<Int, List<Int>>): Boolean {
    val visited = mutableSetOf<Int>()

    fun dfs(node: Int, parent: Int): Boolean {
        visited.add(node)

        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                if (dfs(neighbor, node)) return true
            } else if (neighbor != parent) {
                return true  // Cycle found!
            }
        }
        return false
    }

    // Проверяем все компоненты связности
    for (node in graph.keys) {
        if (node !in visited) {
            if (dfs(node, -1)) return true
        }
    }
    return false
}
```

### Directed Graph (Three Colors)

```
WHITE = 0 (unvisited)
GRAY  = 1 (in progress, in current DFS path)
BLACK = 2 (completed)

Если встретили GRAY → back edge → cycle!
```

**Kotlin:**

```kotlin
fun hasCycleDirected(graph: Map<Int, List<Int>>): Boolean {
    val color = mutableMapOf<Int, Int>()  // 0=white, 1=gray, 2=black

    fun dfs(node: Int): Boolean {
        color[node] = 1  // Gray

        for (neighbor in graph[node] ?: emptyList()) {
            when (color[neighbor]) {
                1 -> return true  // Back edge to gray = cycle
                0, null -> if (dfs(neighbor)) return true
            }
        }

        color[node] = 2  // Black
        return false
    }

    for (node in graph.keys) {
        if (color[node] != 2) {
            if (dfs(node)) return true
        }
    }
    return false
}
```

**Java:**

```java
public boolean hasCycleDirected(Map<Integer, List<Integer>> graph) {
    Map<Integer, Integer> color = new HashMap<>();

    for (int node : graph.keySet()) {
        if (color.getOrDefault(node, 0) != 2) {
            if (dfs(graph, node, color)) return true;
        }
    }
    return false;
}

private boolean dfs(Map<Integer, List<Integer>> graph, int node,
                    Map<Integer, Integer> color) {
    color.put(node, 1);  // Gray

    for (int neighbor : graph.getOrDefault(node, List.of())) {
        int c = color.getOrDefault(neighbor, 0);
        if (c == 1) return true;  // Cycle
        if (c == 0 && dfs(graph, neighbor, color)) return true;
    }

    color.put(node, 2);  // Black
    return false;
}
```

---

## Topological Sort

### Концепция

```
TOPOLOGICAL SORT: линейный порядок вершин DAG,
где для каждого ребра u→v вершина u идёт до v.

Граф зависимостей:
  A → B → D
  ↓   ↓
  C → E

Один из topological orders: A → B → C → D → E
                   или: A → C → B → E → D
```

### Kahn's Algorithm (BFS)

**Идея:**
1. Найти все вершины с indegree = 0
2. Удалять их и уменьшать indegree соседей
3. Повторять пока есть вершины с indegree = 0

**Kotlin:**

```kotlin
fun topologicalSortKahn(graph: Map<Int, List<Int>>, n: Int): List<Int>? {
    val indegree = IntArray(n)
    val result = mutableListOf<Int>()

    // Calculate indegrees
    for ((_, neighbors) in graph) {
        for (neighbor in neighbors) {
            indegree[neighbor]++
        }
    }

    // Start with nodes having indegree 0
    val queue = ArrayDeque<Int>()
    for (i in 0 until n) {
        if (indegree[i] == 0) queue.addLast(i)
    }

    while (queue.isNotEmpty()) {
        val node = queue.removeFirst()
        result.add(node)

        for (neighbor in graph[node] ?: emptyList()) {
            indegree[neighbor]--
            if (indegree[neighbor] == 0) {
                queue.addLast(neighbor)
            }
        }
    }

    // If result doesn't contain all nodes, there's a cycle
    return if (result.size == n) result else null
}
```

### DFS Approach

**Идея:** Post-order DFS, затем reverse.

**Kotlin:**

```kotlin
fun topologicalSortDFS(graph: Map<Int, List<Int>>, n: Int): List<Int>? {
    val visited = mutableSetOf<Int>()
    val inStack = mutableSetOf<Int>()
    val result = mutableListOf<Int>()

    fun dfs(node: Int): Boolean {
        if (node in inStack) return false  // Cycle
        if (node in visited) return true

        inStack.add(node)
        for (neighbor in graph[node] ?: emptyList()) {
            if (!dfs(neighbor)) return false
        }
        inStack.remove(node)
        visited.add(node)
        result.add(node)
        return true
    }

    for (node in 0 until n) {
        if (!dfs(node)) return null  // Cycle detected
    }

    return result.reversed()
}
```

**Python:**

```python
def topological_sort_dfs(graph: dict, n: int) -> list | None:
    visited = set()
    in_stack = set()
    result = []

    def dfs(node: int) -> bool:
        if node in in_stack:
            return False  # Cycle
        if node in visited:
            return True

        in_stack.add(node)
        for neighbor in graph.get(node, []):
            if not dfs(neighbor):
                return False
        in_stack.remove(node)
        visited.add(node)
        result.append(node)
        return True

    for node in range(n):
        if not dfs(node):
            return None

    return result[::-1]
```

---

## Dijkstra's Algorithm

### Концепция

```
DIJKSTRA: кратчайшие пути от одной вершины
          для графов с неотрицательными весами.

     2
  A ──── B
  │      │
1 │      │ 3
  │      │
  C ──── D
     1

Shortest paths from A:
  A → A: 0
  A → B: 2
  A → C: 1
  A → D: 2 (A → C → D)
```

### Алгоритм

```
1. dist[start] = 0, dist[all others] = ∞
2. PriorityQueue с (distance, node)
3. Pop минимальный
4. Для каждого соседа: relax edge
5. Повторять пока queue не пуст
```

### Реализация

**Kotlin:**

```kotlin
import java.util.PriorityQueue

fun dijkstra(
    graph: Map<Int, List<Pair<Int, Int>>>,  // node -> [(neighbor, weight)]
    start: Int,
    n: Int
): IntArray {
    val dist = IntArray(n) { Int.MAX_VALUE }
    dist[start] = 0

    // PriorityQueue: (distance, node)
    val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.first })
    pq.offer(0 to start)

    while (pq.isNotEmpty()) {
        val (d, u) = pq.poll()

        // Skip if we've found a better path
        if (d > dist[u]) continue

        for ((v, weight) in graph[u] ?: emptyList()) {
            val newDist = dist[u] + weight
            if (newDist < dist[v]) {
                dist[v] = newDist
                pq.offer(newDist to v)
            }
        }
    }

    return dist
}
```

**Java:**

```java
public int[] dijkstra(Map<Integer, List<int[]>> graph, int start, int n) {
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[start] = 0;

    // PriorityQueue: [distance, node]
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
    pq.offer(new int[]{0, start});

    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int d = curr[0], u = curr[1];

        if (d > dist[u]) continue;

        for (int[] edge : graph.getOrDefault(u, List.of())) {
            int v = edge[0], weight = edge[1];
            int newDist = dist[u] + weight;
            if (newDist < dist[v]) {
                dist[v] = newDist;
                pq.offer(new int[]{newDist, v});
            }
        }
    }

    return dist;
}
```

**Python:**

```python
import heapq

def dijkstra(graph: dict, start: int, n: int) -> list:
    dist = [float('inf')] * n
    dist[start] = 0

    # Min-heap: (distance, node)
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)

        if d > dist[u]:
            continue

        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    return dist
```

### Complexity

- **Time:** O((V + E) log V) с binary heap
- **Space:** O(V)

### Почему не работает с отрицательными весами

```
    A ──(1)── B
    │         │
   (2)      (-3)
    │         │
    C ────────┘

Dijkstra выберет A→B (dist=1), пометит B как done.
Но реальный shortest path: A→C→B = 2 + (-3) = -1

После "закрытия" B мы не можем его обновить!
```

Для отрицательных весов используй **Bellman-Ford**.

---

## Connected Components

### Undirected Graph

**Kotlin:**

```kotlin
fun countComponents(graph: Map<Int, List<Int>>, n: Int): Int {
    val visited = mutableSetOf<Int>()
    var count = 0

    fun dfs(node: Int) {
        visited.add(node)
        for (neighbor in graph[node] ?: emptyList()) {
            if (neighbor !in visited) {
                dfs(neighbor)
            }
        }
    }

    for (node in 0 until n) {
        if (node !in visited) {
            dfs(node)
            count++
        }
    }

    return count
}
```

### Number of Islands (Grid as Graph)

```kotlin
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val rows = grid.size
    val cols = grid[0].size
    var count = 0

    fun dfs(r: Int, c: Int) {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return
        if (grid[r][c] != '1') return

        grid[r][c] = '0'  // Mark as visited

        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    }

    for (r in 0 until rows) {
        for (c in 0 until cols) {
            if (grid[r][c] == '1') {
                dfs(r, c)
                count++
            }
        }
    }

    return count
}
```

---

## Bipartite Check

**Идея:** Граф bipartite если можно раскрасить в 2 цвета так, чтобы соседи имели разные цвета.

```kotlin
fun isBipartite(graph: Map<Int, List<Int>>, n: Int): Boolean {
    val color = IntArray(n) { -1 }

    fun bfs(start: Int): Boolean {
        val queue = ArrayDeque<Int>()
        queue.addLast(start)
        color[start] = 0

        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()

            for (neighbor in graph[node] ?: emptyList()) {
                if (color[neighbor] == -1) {
                    color[neighbor] = 1 - color[node]
                    queue.addLast(neighbor)
                } else if (color[neighbor] == color[node]) {
                    return false
                }
            }
        }
        return true
    }

    for (i in 0 until n) {
        if (color[i] == -1 && !bfs(i)) {
            return false
        }
    }
    return true
}
```

---

## Complexity Summary

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| BFS | O(V+E) | O(V) | Shortest path (unweighted) |
| DFS | O(V+E) | O(V) | Cycle detection, components |
| Topological Sort | O(V+E) | O(V) | DAG ordering |
| Dijkstra | O((V+E)logV) | O(V) | Shortest path (weighted, non-negative) |
| Bellman-Ford | O(VE) | O(V) | Shortest path (negative weights) |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest paths |

---

## Common Interview Problems

| # | Problem | Algorithm | Key Insight |
|---|---------|-----------|-------------|
| 1 | Number of Islands | DFS/BFS | Grid = implicit graph |
| 2 | Clone Graph | DFS + HashMap | Track cloned nodes |
| 3 | Course Schedule | Topological/Cycle | DAG if no cycle |
| 4 | Word Ladder | BFS | Shortest transformation |
| 5 | Pacific Atlantic Water | Multi-source BFS | Start from edges |
| 6 | Network Delay Time | Dijkstra | Weighted shortest path |
| 7 | Rotting Oranges | BFS | Multi-source, levels |
| 8 | Graph Valid Tree | Cycle + Components | n-1 edges, connected |

---

## Corner Cases

```
□ Empty graph (no nodes)
□ Single node
□ Disconnected components
□ Self-loops
□ Directed vs undirected
□ Negative weights (for Dijkstra)
□ Cycles in DAG problems
□ Grid boundary checks
```

---

## Связи

- [[big-o-complexity]] — анализ сложности алгоритмов
- [[data-structures/graphs]] — представление графов
- [[patterns/dfs-bfs-patterns]] — паттерны применения
- [[patterns/topological-sort-pattern]] — задачи на топологическую сортировку
- [[algorithms/graph-advanced]] — продвинутые алгоритмы

---

## Источники

- [Tech Interview Handbook - Graph](https://www.techinterviewhandbook.org/algorithms/graph/) — cheatsheet
- [GeeksforGeeks - BFS](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/) — tutorial
- [Wikipedia - Dijkstra](https://en.wikipedia.org/wiki/Dijkstra's_algorithm) — proof
- [CP-Algorithms - Cycle Detection](https://cp-algorithms.com/graph/finding-cycle.html) — implementation
- [USACO Guide - Toposort](https://usaco.guide/gold/toposort) — competitive
- [Research: Graph Algorithms](../docs/research/2025-12-29-graph-algorithms.md) — полное исследование

---

*Обновлено: 2026-01-08 — добавлены TL;DR и педагогические секции (интуиция BFS/DFS/Dijkstra, 6 типичных ошибок, 5 ментальных моделей)*

---

[[algorithms/recursion-fundamentals|← Recursion]] | [[algorithms/dynamic-programming|Dynamic Programming →]]
