---
title: "Алгоритмы кратчайших путей"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/advanced
  - interview
related:
  - "[[graph-algorithms]]"
  - "[[graphs]]"
  - "[[greedy-algorithms]]"
  - "[[dynamic-programming]]"
---

# Shortest Path Algorithms

## TL;DR

Shortest path — поиск пути минимального веса между вершинами. **Dijkstra** — O(E log V), только positive weights. **Bellman-Ford** — O(VE), negative weights + cycle detection. **Floyd-Warshall** — O(V³), all-pairs. **0-1 BFS** — O(V+E) для весов 0/1. Выбор зависит от: single/all-pairs, negative weights, sparse/dense.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Dijkstra — "жадный турист"

Представь, что ты турист в незнакомом городе. Хочешь дойти от отеля до музея **быстрее всего**.

```
Отель
  │
  │ 5 мин      Кафе ─── 2 мин ─── Парк
  │           /                     │
  └─── Площадь ─── 3 мин ─── Музей ─┘
        │                      │
        └───── 10 мин ────────┘
```

**Стратегия Dijkstra:** Исследуй ближайшие места сначала.

```
Шаг 0: Отель (dist=0) — начинаем здесь
Шаг 1: Площадь (dist=5) — ближайшая от отеля
Шаг 2: Кафе (dist=7) — через площадь: 5+2=7
Шаг 3: Парк (dist=9) — через кафе: 7+2=9
Шаг 4: Музей (dist=8) — через площадь: 5+3=8 ✓

Кратчайший путь: Отель → Площадь → Музей (8 мин)
```

**Почему это работает?** Когда мы достигаем места с минимальным расстоянием — это ФИНАЛЬНЫЙ ответ. Никакой более длинный путь не сможет стать короче!

---

### Аналогия 2: Bellman-Ford — "терпеливый почтальон"

Почтальон доставляет письма по городу. Он не знает кратчайших путей, но **готов проверить все дороги много раз**.

```
Правило почтальона:
"Для каждой дороги: если я могу улучшить
 расстояние до конца — улучшаю!"

Повторяю V-1 раз (для V городов).
```

**Пример с отрицательными весами:**

```
    A ──(5)──→ B
    │          │
   (3)       (-4)  ← отрицательное!
    ↓          ↓
    C ←─(2)─── D

Dijkstra провалится:
  dist[B] = 5 → финализировано!
  Но реально: A→C→D→B = 3+2+(-4) = 1 < 5

Bellman-Ford работает:
  Итерация 1: dist[B]=5, dist[C]=3
  Итерация 2: dist[D]=5, dist[B]=min(5, 3+2-4)=1 ✓
```

---

### Аналогия 3: Floyd-Warshall — "всезнающий картограф"

Картограф составляет таблицу расстояний между ВСЕМИ парами городов.

```
Идея: "Можно ли улучшить путь A→B,
       если пойти через промежуточный город K?"

       A → B  vs  A → K → B

Проверяем для КАЖДОГО K = 1, 2, ..., V
```

**Числовой пример:**

```
Граф:
    1 ──2── 2
    │       │
    1       3
    │       │
    3 ──4── 4

Начальная матрица:    После проверки k=1,2,3,4:
    1   2   3   4         1   2   3   4
1 [ 0   2   1   ∞ ]   1 [ 0   2   1   4 ]
2 [ 2   0   ∞   3 ]   2 [ 2   0   3   3 ]
3 [ 1   ∞   0   4 ]   3 [ 1   3   0   4 ]
4 [ ∞   3   4   0 ]   4 [ 4   3   4   0 ]

dist[1→4] = 4 (через 3): 1→3→4 = 1+3 ✗ → нет, 1+4=5
dist[1→4] = 4 (через 2): 1→2→4 = 2+3 = 5 ✗
Но подождите... dist[3→4] можно улучшить?

После k=2: dist[3→4] = min(4, dist[3→2]+dist[2→4]) = min(4, 3+3) = 4
Нет улучшения.

Финал: dist[1→4] = 4 (напрямую через ребро... которого нет)
На самом деле: 1→3→4 = 1+4 = 5, 1→2→4 = 2+3 = 5
```

---

### Аналогия 4: 0-1 BFS — "бесплатные эскалаторы"

В метро есть лестницы (стоят 1 минуту) и эскалаторы (бесплатно, 0 минут).

```
Вопрос: как быстрее добраться до платформы?

    Вход ─(0)─→ Эскалатор ─(0)─→ Холл
      │                          │
     (1)                        (1)
      ↓                          ↓
   Лестница                  Платформа

Идея 0-1 BFS:
- Рёбра веса 0 → добавляем В НАЧАЛО очереди (deque)
- Рёбра веса 1 → добавляем В КОНЕЦ очереди

Это работает за O(V+E)!
```

**Почему это эффективнее Dijkstra?**

```
Dijkstra: PriorityQueue O(log V) на каждую операцию
0-1 BFS:  Deque O(1) на каждую операцию

При только весах 0/1 — 0-1 BFS быстрее!
```

---

### Числовой пример: Выбор алгоритма

**Задача:** Найти кратчайшие пути от вершины 0.

```
Граф:
    0 ──(2)── 1 ──(3)── 2
    │                   │
   (1)                 (-1)  ← отрицательный вес!
    │                   │
    3 ──(4)───────────── 4
```

**Какой алгоритм выбрать?**

```
✗ Dijkstra — есть отрицательный вес (-1)
✓ Bellman-Ford — работает с отрицательными весами

Bellman-Ford:
Инициализация: dist = [0, ∞, ∞, ∞, ∞]

Итерация 1 (проверяем все рёбра):
  0→1: dist[1] = min(∞, 0+2) = 2
  0→3: dist[3] = min(∞, 0+1) = 1
  1→2: dist[2] = min(∞, 2+3) = 5
  2→4: dist[4] = min(∞, 5-1) = 4
  3→4: dist[4] = min(4, 1+4) = 4 (без изменений)

Итерация 2: без изменений

Результат: dist = [0, 2, 5, 1, 4]
```

---

## Часть 2: Почему Shortest Path алгоритмы сложные

### Типичные ошибки студентов

#### Ошибка 1: Использование Dijkstra с отрицательными весами

**Симптом:** Неправильные расстояния

```
// ❌ ОШИБКА: Dijkstra + отрицательные веса
val graph = mapOf(
    0 to listOf(1 to 5, 2 to 2),
    2 to listOf(1 to -4)  // Отрицательный!
)
dijkstra(graph, 0)  // Выдаст dist[1] = 5, но реально = 2+(-4) = -2

// ✓ Симптомы:
// - Dijkstra финализирует dist[1] = 5 при первом извлечении
// - Но путь 0→2→1 = 2+(-4) = -2 < 5
// - Dijkstra уже не пересмотрит dist[1]!

// ✅ ПРАВИЛЬНО: используй Bellman-Ford
bellmanFord(graph, 0)  // Корректно: dist[1] = -2
```

---

#### Ошибка 2: Забыть проверку на отрицательный цикл

**Симптом:** Бесконечный цикл или неправильные (очень маленькие) расстояния

```
// Граф с отрицательным циклом:
// 0 → 1 → 2 → 0 с суммой = -1

// ❌ ОШИБКА: просто запускаем Bellman-Ford
fun bellmanFord(graph, start): IntArray {
    // V-1 итераций...
    return dist  // Может вернуть -∞ если есть цикл!
}

// ✅ ПРАВИЛЬНО: добавляем проверку
fun bellmanFordWithCycleCheck(graph, start): IntArray? {
    // V-1 итераций...

    // V-я итерация: если что-то улучшилось — есть цикл!
    for (edge in edges) {
        if (dist[edge.to] > dist[edge.from] + edge.weight) {
            return null  // Отрицательный цикл!
        }
    }
    return dist
}
```

---

#### Ошибка 3: Неправильное использование PriorityQueue в Dijkstra

**Симптом:** TLE или неправильные результаты

```
// ❌ ОШИБКА 1: не пропускаем устаревшие записи
while (pq.isNotEmpty()) {
    val (d, u) = pq.poll()
    // Пропустили проверку d > dist[u]!
    for ((v, w) in graph[u]) {
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w
            pq.offer(dist[v] to v)
        }
    }
}

// Проблема: PriorityQueue может содержать УСТАРЕВШИЕ пары
// Обрабатываем одну вершину несколько раз!

// ✅ ПРАВИЛЬНО: пропускаем устаревшие
while (pq.isNotEmpty()) {
    val (d, u) = pq.poll()
    if (d > dist[u]) continue  // ← Устаревшая запись!
    // ...
}
```

---

#### Ошибка 4: Floyd-Warshall — неправильный порядок циклов

**Симптом:** Неправильные расстояния

```
// ❌ ОШИБКА: k не внешний цикл
for (i in 0 until n) {
    for (j in 0 until n) {
        for (k in 0 until n) {  // k должен быть ВНЕШНИМ!
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        }
    }
}

// Проблема: когда обрабатываем пару (i,j),
// dist[i][k] и dist[k][j] ещё не финализированы для всех k!

// ✅ ПРАВИЛЬНО: k — внешний цикл
for (k in 0 until n) {  // ← ВНЕШНИЙ!
    for (i in 0 until n) {
        for (j in 0 until n) {
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        }
    }
}
```

---

#### Ошибка 5: Переполнение при сложении

**Симптом:** Неправильные большие числа

```
// ❌ ОШИБКА: dist[u] = Int.MAX_VALUE
if (dist[u] + weight < dist[v]) {  // Int.MAX_VALUE + weight = OVERFLOW!
    dist[v] = dist[u] + weight
}

// ✅ ПРАВИЛЬНО: проверка на Int.MAX_VALUE
if (dist[u] != Int.MAX_VALUE && dist[u] + weight < dist[v]) {
    dist[v] = dist[u] + weight
}

// Или использовать Long:
val dist = LongArray(n) { Long.MAX_VALUE / 2 }  // Делим на 2 для безопасности
```

---

#### Ошибка 6: 0-1 BFS с обычной Queue

**Симптом:** Неправильный порядок обработки, неверные расстояния

```
// ❌ ОШИБКА: используем обычную Queue
val queue = ArrayDeque<Int>()
// ...
if (weight == 0) queue.addLast(v)  // Должно быть addFirst!
else queue.addLast(v)

// ✅ ПРАВИЛЬНО: Deque с addFirst для веса 0
val deque = ArrayDeque<Int>()
// ...
if (weight == 0) {
    deque.addFirst(v)  // Вес 0 → в начало!
} else {
    deque.addLast(v)   // Вес 1 → в конец
}
```

---

## Часть 3: Ментальные модели

### Модель 1: Decision Tree выбора алгоритма

```
                    Shortest Path?
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Single-source                   All-pairs
         │                               │
    ┌────┴────┐                    ┌────┴────┐
    │         │                    │         │
Negative?  Positive            Dense?    Sparse?
    │         │                    │         │
    ↓         ↓                    ↓         ↓
Bellman   Dijkstra            Floyd     Johnson's
 -Ford                        O(V³)      O(V²logV)
O(VE)     O(ElogV)

         ┌────────┐
         │ Bonus  │
         └────┬───┘
              │
    Веса только 0/1? → 0-1 BFS O(V+E)
    Невзвешенный?    → BFS O(V+E)
    Есть цель?       → A* (эвристика)
```

---

### Модель 2: Relaxation — ключевая операция

**Релаксация ребра (u, v):**

```
Если dist[u] + weight(u,v) < dist[v]:
    dist[v] = dist[u] + weight(u,v)
    parent[v] = u  // Для восстановления пути

Интуиция:
"Нашли более короткий путь до v — обновляем!"
```

**Все алгоритмы кратчайших путей используют relaxation:**

```
┌─────────────────┬──────────────────────────────────────┐
│ Алгоритм        │ Как использует relaxation            │
├─────────────────┼──────────────────────────────────────┤
│ Dijkstra        │ Relaxation по приоритету (min dist)  │
│ Bellman-Ford    │ Relaxation всех рёбер V-1 раз        │
│ Floyd-Warshall  │ Relaxation через все промежуточные k │
│ 0-1 BFS         │ Relaxation с Deque (0 → front)       │
└─────────────────┴──────────────────────────────────────┘
```

---

### Модель 3: Почему Dijkstra не работает с отрицательными весами

```
Инвариант Dijkstra:
"Когда вершина извлечена из PQ — её расстояние ФИНАЛЬНОЕ"

С положительными весами:
  Если dist[u] финализировано, любой другой путь до u
  через непосещённые вершины будет ДЛИННЕЕ
  (потому что мы извлекли u с минимальным dist).

С отрицательными весами:
  Путь через непосещённую вершину может стать КОРОЧЕ
  благодаря отрицательному ребру!

Пример:
    A ──(10)──→ B
    │           │
   (1)        (-20)
    ↓           ↓
    C ←─────────

Dijkstra финализирует dist[B] = 10.
Но реальный shortest: A→C = 1, потом C←B с весом -20...
На самом деле dist[B] = 1 + (что-то через C) = ???
```

---

### Модель 4: Floyd-Warshall как DP

```
Состояние:
  dp[k][i][j] = кратчайший путь от i до j,
                используя только вершины {0, 1, ..., k-1} как промежуточные

Переход:
  dp[k][i][j] = min(
      dp[k-1][i][j],           // Не используем k
      dp[k-1][i][k] + dp[k-1][k][j]  // Идём через k
  )

Оптимизация пространства:
  k используется только для обращения к k-1
  → можно переиспользовать один 2D массив!

for k in 0..n:
    for i in 0..n:
        for j in 0..n:
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

---

### Модель 5: Когда какой алгоритм

```
┌────────────────────────────────────────────────────────────┐
│                 ВЫБОР АЛГОРИТМА                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 1. НЕВЗВЕШЕННЫЙ граф?                                     │
│    → BFS O(V+E) — самый быстрый                           │
│                                                            │
│ 2. Веса ТОЛЬКО 0 или 1?                                   │
│    → 0-1 BFS O(V+E) — Deque вместо PriorityQueue          │
│                                                            │
│ 3. ВСЕ веса ПОЛОЖИТЕЛЬНЫЕ?                                │
│    → Dijkstra O(E log V) — стандартный выбор              │
│                                                            │
│ 4. Есть ОТРИЦАТЕЛЬНЫЕ веса?                               │
│    → Bellman-Ford O(VE) — медленнее, но работает          │
│    → SPFA O(E) average — на практике быстрее              │
│                                                            │
│ 5. Нужны пути между ВСЕМИ парами?                         │
│    → Floyd-Warshall O(V³) — просто, но медленно           │
│    → Johnson's O(V² log V + VE) — для разреженных         │
│                                                            │
│ 6. Есть ЭВРИСТИКА до цели?                                │
│    → A* — оптимизация Dijkstra с направлением             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно?

**Проблема:**

```
GPS навигация: найти быстрейший маршрут A → B
Социальная сеть: shortest path между пользователями
Routing: оптимальный путь пакета в сети

Разные ситуации требуют разных алгоритмов!
```

**Классификация задач:**

| Тип | Описание | Алгоритм |
|-----|----------|----------|
| Single-source | От одной вершины ко всем | Dijkstra, Bellman-Ford |
| Single-pair | Между двумя вершинами | A*, Bidirectional |
| All-pairs | Между всеми парами | Floyd-Warshall, Johnson's |

---

## Что это такое?

### Для 5-летнего

```
Представь карту с городами и дорогами.
На каждой дороге написано число — время в пути.

Shortest path — это маршрут, где сумма
всех чисел на дорогах МИНИМАЛЬНАЯ.

Разные алгоритмы — как разные способы искать:
- Dijkstra: идём от близких городов к дальним
- Bellman-Ford: проверяем ВСЕ дороги много раз
- Floyd-Warshall: сразу считаем пути между ВСЕМИ городами
```

### Формально

**Shortest Path** от s до t в взвешенном графе G = (V, E, w):
- Путь P = (v₀, v₁, ..., vₖ) где v₀ = s, vₖ = t
- Минимизирует w(P) = Σᵢ w(vᵢ, vᵢ₊₁)

**Свойства:**

| Свойство | Описание |
|----------|----------|
| Optimal Substructure | Subpath кратчайшего пути — тоже кратчайший |
| Triangle Inequality | d(u,v) ≤ d(u,x) + d(x,v) |
| No negative cycles | Иначе shortest path не определён (−∞) |

---

## Обзор алгоритмов

### Сравнительная таблица

| Алгоритм | Время | Negative | Задача | Лучше для |
|----------|-------|----------|--------|-----------|
| BFS | O(V+E) | ✗ | Single-source | Unweighted |
| 0-1 BFS | O(V+E) | ✗ | Single-source | Weights 0/1 |
| Dijkstra | O(E log V) | ✗ | Single-source | General |
| Bellman-Ford | O(VE) | ✓ | Single-source | Negative weights |
| SPFA | O(E) avg | ✓ | Single-source | Sparse + negative |
| Floyd-Warshall | O(V³) | ✓ | All-pairs | Dense |
| Johnson's | O(V²logV + VE) | ✓ | All-pairs | Sparse |
| A* | O(E) ~ O(b^d) | ✗ | Single-pair | Known goal |

---

## Dijkstra's Algorithm

### Ключевая идея

```
Greedy: всегда обрабатываем вершину с минимальным известным расстоянием.

Инвариант: когда вершина извлечена из очереди,
           её расстояние ФИНАЛЬНОЕ (если нет negative weights)

WHY no negative weights?
Если есть отрицательное ребро, финализированная вершина
может получить лучший путь позже → инвариант нарушен!
```

### Визуализация

```
Граф:
    A ──2── B
    │       │
    1       3
    │       │
    C ──1── D

Dijkstra от A:

Step 0: dist = [A:0, B:∞, C:∞, D:∞]
        PQ = [(0,A)]

Step 1: Extract A, process neighbors
        dist = [A:0, B:2, C:1, D:∞]
        PQ = [(1,C), (2,B)]

Step 2: Extract C (min), process neighbors
        dist = [A:0, B:2, C:1, D:2]
        PQ = [(2,B), (2,D)]

Step 3: Extract B or D (tie), finish
        Final: [A:0, B:2, C:1, D:2]
```

### Реализация (Kotlin)

```kotlin
class Dijkstra(private val n: Int) {
    data class Edge(val to: Int, val weight: Long)

    private val adj = Array(n) { mutableListOf<Edge>() }

    fun addEdge(from: Int, to: Int, weight: Long) {
        adj[from].add(Edge(to, weight))
    }

    fun shortestPaths(source: Int): LongArray {
        val dist = LongArray(n) { Long.MAX_VALUE }
        dist[source] = 0

        // Min-heap (приоритетная очередь) по расстоянию
        // Всегда извлекаем вершину с минимальным dist — это оптимально!
        val pq = PriorityQueue<Pair<Long, Int>>(compareBy { it.first })
        pq.add(0L to source)

        while (pq.isNotEmpty()) {
            val (d, u) = pq.poll()

            // ВАЖНО: пропускаем устаревшие записи!
            // В очереди могут быть старые (d, u) с большим d.
            // Если d > dist[u], значит мы уже нашли путь короче.
            if (d > dist[u]) continue

            for ((v, w) in adj[u]) {
                // RELAXATION — ключевая операция Дейкстры
                // Если через u путь до v короче — обновляем
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w
                    pq.add(dist[v] to v)
                }
            }
        }

        return dist
    }

    /**
     * Вариант с восстановлением пути
     * Сохраняем parent[v] = откуда пришли в v
     */
    fun shortestPath(source: Int, target: Int): List<Int>? {
        val dist = LongArray(n) { Long.MAX_VALUE }
        val parent = IntArray(n) { -1 }
        dist[source] = 0

        val pq = PriorityQueue<Pair<Long, Int>>(compareBy { it.first })
        pq.add(0L to source)

        while (pq.isNotEmpty()) {
            val (d, u) = pq.poll()
            if (d > dist[u]) continue

            // ОПТИМИЗАЦИЯ: если нашли цель — можно остановиться!
            // Дейкстра гарантирует: когда вершина извлекается из pq,
            // кратчайший путь до неё уже найден
            if (u == target) break

            for ((v, w) in adj[u]) {
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w
                    parent[v] = u
                    pq.add(dist[v] to v)
                }
            }
        }

        if (dist[target] == Long.MAX_VALUE) return null

        // Восстанавливаем путь: идём от target к source по parent[]
        // Путь получается "задом наперёд", поэтому reversed()
        val path = mutableListOf<Int>()
        var current = target
        while (current != -1) {
            path.add(current)
            current = parent[current]
        }
        return path.reversed()
    }
}
```

### Оптимизации

| Heap | Extract-min | Decrease-key | Total |
|------|-------------|--------------|-------|
| Binary | O(log V) | O(log V) | O(E log V) |
| Fibonacci | O(log V) | O(1) amort | O(E + V log V) |
| Bucket | O(1) | O(1) | O(V + E) * |

*Bucket queue работает только для ограниченных integer весов.

---

## 0-1 BFS

### Когда использовать

```
Веса рёбер только 0 или 1.
Пример: сетка где проход по пустой клетке = 0, через препятствие = 1.

WHY быстрее Dijkstra?
Используем deque вместо priority queue:
- Вес 0 → добавляем в начало
- Вес 1 → добавляем в конец

Порядок обработки сохраняется без сортировки!
```

### Реализация (Kotlin)

```kotlin
/**
 * 0-1 BFS — специальный случай для графов с весами 0 и 1
 *
 * Deque (двусторонняя очередь) вместо priority queue!
 * PriorityQueue даёт O(E log V), Deque даёт O(E) — намного быстрее.
 *
 * Почему работает?
 * - Рёбра с весом 0 НЕ УВЕЛИЧИВАЮТ расстояние → добавляем в НАЧАЛО
 * - Рёбра с весом 1 увеличивают на 1 → добавляем в КОНЕЦ
 * В итоге порядок обработки такой же, как у Дейкстры!
 */
fun bfs01(n: Int, adj: Array<MutableList<Pair<Int, Int>>>, source: Int): IntArray {
    val dist = IntArray(n) { Int.MAX_VALUE }
    dist[source] = 0

    val deque = ArrayDeque<Int>()
    deque.addFirst(source)

    while (deque.isNotEmpty()) {
        val u = deque.removeFirst()

        for ((v, w) in adj[u]) {
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w

                // Ключевая идея: куда добавлять?
                // w=0 → в НАЧАЛО (обработаем сразу, как продолжение текущего)
                // w=1 → в КОНЕЦ (обработаем после всех с текущим расстоянием)
                if (w == 0) {
                    deque.addFirst(v)
                } else {
                    deque.addLast(v)
                }
            }
        }
    }

    return dist
}
```

### Сложность

- Time: **O(V + E)**
- Space: O(V)

---

## Bellman-Ford Algorithm

### Когда использовать

```
1. Граф содержит отрицательные веса
2. Нужно обнаружить negative cycle
3. Ограничение на количество рёбер в пути

Dijkstra не работает с negative weights!
```

### Ключевая идея

```
Релаксация: dist[v] = min(dist[v], dist[u] + weight(u,v))

После k итераций релаксации всех рёбер:
dist[v] = кратчайший путь к v с ≤ k рёбрами

После V-1 итераций:
Все кратчайшие пути найдены (путь имеет макс V-1 рёбер)

После V итераций:
Если что-то улучшилось → negative cycle!
```

### Реализация (Kotlin)

```kotlin
class BellmanFord(private val n: Int) {
    data class Edge(val from: Int, val to: Int, val weight: Long)

    private val edges = mutableListOf<Edge>()

    fun addEdge(from: Int, to: Int, weight: Long) {
        edges.add(Edge(from, to, weight))
    }

    /**
     * Возвращает кратчайшие расстояния или null если есть отрицательный цикл
     */
    fun shortestPaths(source: Int): LongArray? {
        val dist = LongArray(n) { Long.MAX_VALUE / 2 }
        dist[source] = 0

        // V-1 итераций ГАРАНТИРОВАННО достаточно!
        // Почему? Кратчайший путь содержит максимум V-1 рёбер
        // (иначе есть цикл, а цикл либо положительный = не нужен,
        // либо отрицательный = бесконечно улучшаем)
        repeat(n - 1) {
            var changed = false
            for (e in edges) {
                if (dist[e.from] + e.weight < dist[e.to]) {
                    dist[e.to] = dist[e.from] + e.weight
                    changed = true
                }
            }
            // ОПТИМИЗАЦИЯ: если ничего не изменилось — все пути найдены
            if (!changed) return dist
        }

        // V-я итерация: проверка на ОТРИЦАТЕЛЬНЫЙ ЦИКЛ
        // Если после V-1 итераций ещё можно улучшить — есть neg cycle
        for (e in edges) {
            if (dist[e.from] + e.weight < dist[e.to]) {
                return null  // Отрицательный цикл обнаружен!
            }
        }

        return dist
    }

    /**
     * Кратчайший путь с ОГРАНИЧЕНИЕМ на количество рёбер
     *
     * Классическая задача: "Cheapest Flight with K Stops" (LeetCode 787)
     * Нужен путь не более чем с k пересадками (k+1 рёбер)
     */
    fun shortestPathWithKEdges(source: Int, k: Int): LongArray {
        var dist = LongArray(n) { Long.MAX_VALUE / 2 }
        dist[source] = 0

        repeat(k) {
            val newDist = dist.copyOf()
            for (e in edges) {
                if (dist[e.from] + e.weight < newDist[e.to]) {
                    newDist[e.to] = dist[e.from] + e.weight
                }
            }
            dist = newDist
        }

        return dist
    }
}
```

### Сложность

- Time: **O(VE)**
- Space: O(V)

---

## Floyd-Warshall Algorithm

### Когда использовать

```
1. Нужны расстояния между ВСЕМИ парами вершин
2. Граф плотный (E ≈ V²)
3. Возможны отрицательные веса (но не циклы)
```

### Ключевая идея

```
DP: dp[k][i][j] = shortest i→j path using vertices {0..k-1} as intermediate

Переход:
dp[k][i][j] = min(dp[k-1][i][j],           // не через k
                  dp[k-1][i][k] + dp[k-1][k][j])  // через k

Оптимизация: dp[k-1] → dp[k] in-place
```

### Реализация (Kotlin)

```kotlin
class FloydWarshall(private val n: Int) {
    private val INF = Long.MAX_VALUE / 2
    private val dist = Array(n) { i -> LongArray(n) { j -> if (i == j) 0 else INF } }

    fun addEdge(from: Int, to: Int, weight: Long) {
        dist[from][to] = minOf(dist[from][to], weight)
    }

    /**
     * ПОРЯДОК ЦИКЛОВ K-I-J КРИТИЧЕН!
     *
     * k — внешний цикл, это "промежуточные вершины"
     * На итерации k мы рассматриваем пути через вершины {0..k}
     *
     * Если поставить k внутрь — алгоритм СЛОМАЕТСЯ!
     * Потому что dist[i][k] может быть ещё не вычислен
     */
    fun compute(): Boolean {
        for (k in 0 until n) {
            for (i in 0 until n) {
                for (j in 0 until n) {
                    if (dist[i][k] < INF && dist[k][j] < INF) {
                        dist[i][j] = minOf(dist[i][j], dist[i][k] + dist[k][j])
                    }
                }
            }
        }

        // Проверка на отрицательный цикл:
        // Если dist[i][i] < 0, значит можно "удешевить" путь i→i
        // Это возможно только при наличии отрицательного цикла
        for (i in 0 until n) {
            if (dist[i][i] < 0) return false
        }
        return true
    }

    fun getDistance(from: Int, to: Int): Long = dist[from][to]
}
```

### Сложность

- Time: **O(V³)**
- Space: O(V²)

---

## Выбор алгоритма

### Decision Tree

```
                    Shortest Path Problem
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
         Single-source              All-pairs
              │                         │
    ┌─────────┴─────────┐         ┌─────┴─────┐
    ▼                   ▼         ▼           ▼
Negative           Non-negative  Sparse      Dense
weights?                        │           │
    │                   │       ▼           ▼
    ▼                   ▼    Johnson's   Floyd-Warshall
Bellman-Ford      ┌─────┴─────┐
                  ▼           ▼
               Weights      Weights
               0/1?         general?
                  │           │
                  ▼           ▼
               0-1 BFS    Dijkstra
```

### Практические рекомендации

| Ситуация | Рекомендация |
|----------|--------------|
| Unweighted graph | BFS |
| Non-negative, sparse | Dijkstra (binary heap) |
| Non-negative, dense | Dijkstra (Fibonacci heap) |
| Negative weights | Bellman-Ford |
| Negative, sparse, random | SPFA |
| All-pairs, dense | Floyd-Warshall |
| All-pairs, sparse | Johnson's |
| Known target | A* |
| Known both endpoints | Bidirectional |

---

## Распространённые ошибки

### 1. Dijkstra с negative weights

```kotlin
// ❌ НЕПРАВИЛЬНО: Dijkstra не работает с negative!
val adj = mapOf(
    0 to listOf(1 to 5, 2 to 2),
    2 to listOf(1 to -10)  // Negative edge
)
dijkstra(adj, 0)  // WRONG ANSWER!

// Путь 0→2→1 = 2 + (-10) = -8
// Dijkstra найдёт 0→1 = 5 (неправильно!)
```

### 2. Integer overflow в расстояниях

```kotlin
// ❌ НЕПРАВИЛЬНО: INF + weight может overflow
val INF = Int.MAX_VALUE
if (dist[u] + weight < dist[v])  // Overflow если dist[u] = INF!

// ✅ ПРАВИЛЬНО: используй INF/2 или проверяй
val INF = Int.MAX_VALUE / 2
// или
if (dist[u] < INF && dist[u] + weight < dist[v])
```

### 3. Забыть пометить visited в Dijkstra

```kotlin
// ❌ НЕПРАВИЛЬНО: обрабатываем вершину много раз
while (pq.isNotEmpty()) {
    val (d, u) = pq.poll()
    for ((v, w) in adj[u]) {
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w
            pq.add(dist[v] to v)
        }
    }
}

// ✅ ПРАВИЛЬНО: пропускаем устаревшие
while (pq.isNotEmpty()) {
    val (d, u) = pq.poll()
    // Эта запись устарела: мы уже нашли путь короче!
    // В очереди могут быть старые (d, u) — их нужно игнорировать
    if (d > dist[u]) continue
    // ...
}
```

### 4. Floyd-Warshall: неправильный порядок циклов

```kotlin
// ❌ НЕПРАВИЛЬНО: i-j-k
for (i in 0 until n)
    for (j in 0 until n)
        for (k in 0 until n)  // k должен быть ВНЕШНИМ!

// ✅ ПРАВИЛЬНО: k-i-j
for (k in 0 until n)
    for (i in 0 until n)
        for (j in 0 until n)
```

---

## Практика

### Концептуальные вопросы

1. **Почему Dijkstra не работает с negative weights?**

   Dijkstra полагается на инвариант: извлечённая вершина имеет финальное расстояние. Negative edge может улучшить путь к уже финализированной вершине.

2. **Когда SPFA лучше Bellman-Ford?**

   На sparse графах с random структурой. SPFA = O(E) average, но O(VE) worst case (специально сконструированные графы).

3. **Почему Floyd-Warshall O(V³) а не O(V²E)?**

   Мы итерируем по всем парам (i,j) для каждого k. Это V × V × V = V³ независимо от количества рёбер.

### LeetCode задачи

| # | Название | Сложность | Алгоритм |
|---|----------|-----------|----------|
| 743 | Network Delay Time | Medium | Dijkstra |
| 787 | Cheapest Flights Within K Stops | Medium | Bellman-Ford |
| 1334 | Find the City With the Smallest Number of Neighbors | Medium | Floyd-Warshall |
| 1514 | Path with Maximum Probability | Medium | Modified Dijkstra |
| 1631 | Path With Minimum Effort | Medium | Binary search + BFS / Dijkstra |
| 882 | Reachable Nodes In Subdivided Graph | Hard | Dijkstra |

---

## Связанные темы

### Prerequisites
- [Graphs](../data-structures/graphs.md)
- [BFS/DFS Patterns](../patterns/dfs-bfs-patterns.md)

### Unlocks
- [Graph Advanced](./graph-advanced.md) — A*, Bidirectional
- [Minimum Spanning Tree](./minimum-spanning-tree.md)
- Network Flow

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms: Dijkstra](https://cp-algorithms.com/graph/dijkstra.html) | Reference | Implementation |
| 2 | [CP-Algorithms: Bellman-Ford](https://cp-algorithms.com/graph/bellman_ford.html) | Reference | Negative cycles |
| 3 | [CP-Algorithms: Floyd-Warshall](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html) | Reference | All-pairs |
| 4 | [CP-Algorithms: 0-1 BFS](https://cp-algorithms.com/graph/01_bfs.html) | Reference | Special case |
| 5 | [CLRS] Introduction to Algorithms | Book | Theory |

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция Dijkstra/Bellman-Ford/Floyd-Warshall, 6 типичных ошибок, 5 ментальных моделей)*
