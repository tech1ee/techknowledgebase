---
title: "Продвинутые алгоритмы на графах"
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
  - "[[shortest-paths]]"
  - "[[graphs]]"
prerequisites:
  - "[[graphs]]"
  - "[[graph-algorithms]]"
  - "[[dfs-bfs-patterns]]"
---

# Advanced Graph Algorithms

## TL;DR

Продвинутые алгоритмы графов: **Floyd-Warshall** — все пары за O(V³), **Bellman-Ford** — negative weights за O(VE), **Johnson's** — sparse graphs с negative weights за O(V² log V + VE), **A*** — эвристический поиск с гарантией оптимальности. **Bidirectional Search** — сокращает поиск в 2^(d/2) раз. В 2024 году побит 40-летний "sorting barrier" в shortest path.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Floyd-Warshall — "телефонная книга дистанций"

Представь, что ты работаешь в авиакомпании и нужно знать стоимость перелёта между **любыми** двумя городами.

```
Проблема: У нас 100 городов и 500 прямых рейсов.
          Как узнать цену A → Z, если нет прямого рейса?

Наивно: Для каждой пары запустить Dijkstra → 100 × O(E log V) = много!

Floyd-Warshall: Строим "справочник" за один проход O(V³):

Идея: "Можно ли улететь дешевле через пересадку в городе K?"

     Москва ───500$─── Берлин
        │                 │
      300$               200$
        │                 │
     Дубай ──────────── Лондон

Без пересадок: Москва → Берлин = 500$
Через Дубай:   Москва → Дубай → Берлин = 300$ + ??? (нет рейса!)
Через Лондон:  Москва → Лондон → Берлин = ??? + 200$

Итерируем по ВСЕМ возможным пересадкам K = 1, 2, ..., V
и обновляем: dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

**Ключевой инсайт:** После проверки K промежуточных вершин, dist[i][j] содержит кратчайший путь, использующий ТОЛЬКО вершины {1..K}.

---

### Аналогия 2: Bellman-Ford — "распространение слухов"

Представь, что ты хочешь распространить новость по социальной сети.

```
День 0: Только ты знаешь новость (dist[тебя] = 0)
День 1: Твои друзья узнали (dist[друзей] = 1)
День 2: Друзья друзей узнали (dist = 2)
...
День V-1: ВСЕ, кто могут узнать, узнали

Bellman-Ford работает так же!

Итерация 1: Обновляем всех на расстоянии 1 ребра от старта
Итерация 2: Обновляем всех на расстоянии 2 рёбер
...
Итерация V-1: Все кратчайшие пути найдены!

Почему V-1 достаточно?
Кратчайший путь без циклов содержит максимум V-1 ребро.
(V вершин, между соседними V-1 переход)
```

**Про отрицательные циклы:**
```
Если на V-й день кто-то СНОВА обновил расстояние:
  → Есть "бесконечный слух" (отрицательный цикл)
  → Расстояние можно уменьшать бесконечно!
```

---

### Аналогия 3: Johnson's — "переводчик валют"

Представь, что у тебя есть курсы обмена валют, но некоторые невыгодные (отрицательная прибыль).

```
Проблема: Dijkstra не работает с отрицательными курсами!

Решение Johnson's: "Нормализация курсов"

1. Создаём фиктивную "мировую валюту" (вершина q)
   с курсом 0 ко всем валютам

2. Bellman-Ford от q → получаем "базовые курсы" h[v]

3. Перевзвешивание: новый курс = старый + h[from] - h[to]
   Гарантирует: все новые курсы ≥ 0!

4. Теперь можно V раз Dijkstra!

5. Корректируем обратно: реальный_курс = новый - h[from] + h[to]

Магия: Сумма по любому пути меняется на h[start] - h[end]
       Это КОНСТАНТА для пары (start, end)!
       → Кратчайший путь остаётся кратчайшим!
```

---

### Аналогия 4: A* — "умный GPS"

Представь два GPS-навигатора:

```
Навигатор 1 (Dijkstra):
  "Исследую ВСЕ дороги в радиусе,
   постепенно расширяя круг от старта"

  Круги расходятся во все стороны:
       • • • • •
      • • • • • •
     • • S • • • •   ← Старт в центре
      • • • • • •
       • • • • •

Навигатор 2 (A*):
  "Исследую в НАПРАВЛЕНИИ цели,
   учитывая расстояние до неё"

  Эллипс в сторону цели:
           • •
          • • •
     S • • • • G     ← Направленный поиск
          • • •
           • •

A* исследует МЕНЬШЕ узлов!
```

**Формула A*:**
```
f(n) = g(n) + h(n)

g(n) = реально потраченное время от старта до n
h(n) = ОЦЕНКА времени от n до цели (эвристика)

Выбираем вершину с минимальным f(n):
  - Учитываем и пройденное, и оставшееся
  - GPS "смотрит вперёд"!
```

---

### Аналогия 5: Bidirectional — "встреча посередине"

Представь, что нужно найти путь между Москвой и Сиднеем.

```
Обычный BFS:
  Москва → соседние города → их соседи → ... → Сидней
  Исследуем ВСЁ полушарие!

Bidirectional BFS:
  Поток 1: Москва → Европа → Ближний Восток → ...
  Поток 2: Сидней → Австралия → Азия → ...

  ВСТРЕЧА где-то в Азии!

Почему быстрее?
  BFS: Круг радиуса d → площадь π × d²
  Bidirectional: Два круга радиуса d/2 → 2 × π × (d/2)² = π × d²/2

  В 2 раза меньше площадь → в 2 раза меньше работы!
  (На практике выигрыш ещё больше из-за экспоненты)
```

---

### Числовой пример: Почему Dijkstra ломается на отрицательных весах

```
Граф:
    A ──(5)──→ B
    │          │
   (2)       (-4)
    ↓          ↓
    C ←───────

Dijkstra от A:
  Шаг 1: dist = [A:0, B:∞, C:∞]
  Шаг 2: Обрабатываем A → dist = [A:0, B:5, C:2]
  Шаг 3: Обрабатываем C (минимум!) → dist[C] = 2 ФИНАЛИЗИРОВАНО
  Шаг 4: Обрабатываем B →
         Можно ли улучшить C? B + (-4) = 5 - 4 = 1 < 2!
         НО C УЖЕ ФИНАЛИЗИРОВАНО!

Dijkstra: dist[C] = 2 ❌
Реально:  dist[C] = 1 ✓ (путь A → B → C = 5 - 4 = 1)

Проблема: Dijkstra предполагает, что вершина с минимальным dist
          уже оптимальна. Отрицательные рёбра нарушают это!
```

---

## Часть 2: Почему продвинутые графовые алгоритмы сложные

### Типичные ошибки студентов

#### Ошибка 1: Неправильный порядок циклов в Floyd-Warshall

**Симптом:** Неправильные расстояния

```
// ❌ ОШИБКА: k внутри — нарушает DP-инвариант
for (i in 0 until n) {
    for (j in 0 until n) {
        for (k in 0 until n) {  // K должен быть ВНЕШНИМ!
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        }
    }
}

// Проблема: Когда обрабатываем (i,j) с k=5,
//           dist[i][3] ещё НЕ учитывает путь через вершину 4!
//           Результат неполный.

// ✅ ПРАВИЛЬНО: k внешний
for (k in 0 until n) {  // ← ВНЕШНИЙ ЦИКЛ!
    for (i in 0 until n) {
        for (j in 0 until n) {
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        }
    }
}

// DP-смысл: на итерации k рассматриваем пути через {0,1,...,k}
```

---

#### Ошибка 2: Не проверяют отрицательный цикл в Bellman-Ford

**Симптом:** Бесконечный цикл или неправильные (очень маленькие) расстояния

```
// ❌ ОШИБКА: забыли V-ю итерацию
fun bellmanFord(source: Int): IntArray {
    repeat(n - 1) {
        for (e in edges) {
            if (dist[e.from] + e.weight < dist[e.to]) {
                dist[e.to] = dist[e.from] + e.weight
            }
        }
    }
    return dist  // Может содержать -∞ если есть негативный цикл!
}

// ✅ ПРАВИЛЬНО: проверяем V-ю итерацию
fun bellmanFord(source: Int): IntArray? {
    repeat(n - 1) { /* релаксация */ }

    // V-я итерация: если улучшилось — негативный цикл!
    for (e in edges) {
        if (dist[e.from] + e.weight < dist[e.to]) {
            return null  // Сигнал: бесконечно уменьшаемое расстояние
        }
    }
    return dist
}
```

---

#### Ошибка 3: Недопустимая эвристика в A*

**Симптом:** A* находит НЕ оптимальный путь

```
// ❌ ОШИБКА: эвристика ПЕРЕОЦЕНИВАЕТ расстояние
fun badHeuristic(x: Int, y: Int, goalX: Int, goalY: Int): Double {
    // Умножаем на 2 "для скорости"
    return 2.0 * sqrt((x - goalX)² + (y - goalY)²)
}

// Проблема: h(n) > реальное_расстояние
//           A* пропустит оптимальный путь!

// ✅ ПРАВИЛЬНО: эвристика НЕДООЦЕНИВАЕТ или точна
fun goodHeuristic(x: Int, y: Int, goalX: Int, goalY: Int): Double {
    return sqrt((x - goalX)² + (y - goalY)²)  // Евклидово (никогда не переоценивает)
}

// ПРАВИЛО: h(n) ≤ реальное_расстояние (admissible)
//          Тогда A* ГАРАНТИРУЕТ оптимальность!
```

---

#### Ошибка 4: Bidirectional без проверки пересечения

**Симптом:** Пропускаем встречу волн, ищем дольше нужного

```
// ❌ ОШИБКА: проверяем пересечение слишком поздно
while (forwardQueue.isNotEmpty() && backwardQueue.isNotEmpty()) {
    expandFrontier(forwardQueue, forwardVisited)
    expandFrontier(backwardQueue, backwardVisited)

    // Проверка ПОСЛЕ обоих expand — можем пропустить встречу!
    if (forwardVisited.keys.any { it in backwardVisited }) {
        // Нашли, но уже сделали лишнюю работу
    }
}

// ✅ ПРАВИЛЬНО: проверяем пересечение СРАЗУ при добавлении
fun expandFrontier(...): Int? {
    for (neighbor in adj[current]) {
        if (neighbor in visited) continue
        visited[neighbor] = current

        if (neighbor in otherVisited) {
            return neighbor  // СРАЗУ возвращаем точку встречи!
        }

        queue.add(neighbor)
    }
    return null
}
```

---

#### Ошибка 5: Переполнение в Floyd-Warshall

**Симптом:** Переполнение при сложении INF + вес

```
// ❌ ОШИБКА: INF + weight переполняется
val INF = Int.MAX_VALUE
// ...
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
// Если dist[i][k] = INF, то INF + dist[k][j] = отрицательное число!

// ✅ ПРАВИЛЬНО: проверяем на INF перед сложением
if (dist[i][k] < INF && dist[k][j] < INF) {
    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
}

// ИЛИ: используем INF = 1e9 (достаточно большое, но не переполняется)
val INF = 1_000_000_000L
```

---

#### Ошибка 6: Неправильное перевзвешивание в Johnson's

**Симптом:** Отрицательные веса после перевзвешивания

```
// ❌ ОШИБКА: забыли добавить фиктивную вершину q
val h = bellmanFord(0)  // Запускаем от существующей вершины

// Проблема: 0 может не достигать всех вершин!
// h[недостижимая] = INF → перевзвешивание сломано

// ✅ ПРАВИЛЬНО: добавляем фиктивную вершину q
// q соединена со ВСЕМИ вершинами рёбрами веса 0
for (v in 0 until n) {
    addEdge(n, v, 0)  // q = n, q → v с весом 0
}
val h = bellmanFord(n)  // Теперь все вершины достижимы из q!
```

---

## Часть 3: Ментальные модели

### Модель 1: Single-source vs All-pairs

```
┌────────────────────────────────────────────────────────────┐
│                  КРАТЧАЙШИЕ ПУТИ                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  SINGLE-SOURCE (от одной вершины):                        │
│    • Dijkstra — O(E log V), только положительные веса     │
│    • Bellman-Ford — O(VE), любые веса                     │
│    • 0-1 BFS — O(V+E), веса только 0 и 1                  │
│                                                            │
│  ALL-PAIRS (между всеми парами):                          │
│    • Floyd-Warshall — O(V³), любые веса, dense графы      │
│    • Johnson's — O(V²log V + VE), sparse графы            │
│    • V × Dijkstra — O(VE log V), только положительные     │
│                                                            │
│  SINGLE-PAIR (между двумя вершинами):                     │
│    • A* — O(E) лучший случай, с эвристикой                │
│    • Bidirectional — O(b^(d/2)), встреча посередине       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### Модель 2: Эвристики A* для разных задач

```
┌────────────────────────────────────────────────────────────┐
│              ВЫБОР ЭВРИСТИКИ ДЛЯ A*                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ СЕТКА 4 направления (↑↓←→):                               │
│   h = |x1-x2| + |y1-y2| (Manhattan)                       │
│   Идеально подходит! Точно = минимум шагов без препятствий│
│                                                            │
│ СЕТКА 8 направлений (+ диагонали):                        │
│   h = max(|x1-x2|, |y1-y2|) (Chebyshev, если диагональ=1) │
│   h = √2 × min + |dx-dy| (Octile, если диагональ=√2)      │
│                                                            │
│ СВОБОДНОЕ движение (не по сетке):                         │
│   h = √((x1-x2)² + (y1-y2)²) (Euclidean)                  │
│   Кратчайшая прямая — всегда недооценивает                │
│                                                            │
│ ГРАФ БЕЗ КООРДИНАТ:                                       │
│   h = 0 (A* = Dijkstra)                                   │
│   Или предвычисленные landmarks                           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### Модель 3: Когда какой алгоритм

```
                  Нужен кратчайший путь?
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    От одной         Между всеми      Между двумя
    вершины            парами          вершинами
         │                │                │
    ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
    │         │      │         │      │         │
Negative?  Positive Dense?   Sparse  Есть      Нет
 weights?  weights?  │         │     эвристика эвристики
    │         │      │         │         │         │
    ↓         ↓      ↓         ↓         ↓         ↓
 Bellman  Dijkstra Floyd   Johnson's   A*    Bidirectional
  -Ford            Warshall           (с h)     BFS
```

---

### Модель 4: Relaxation — универсальная операция

```
ВСЕ алгоритмы кратчайших путей используют РЕЛАКСАЦИЮ:

if (dist[u] + weight(u,v) < dist[v]):
    dist[v] = dist[u] + weight(u,v)

"Нашли путь короче — обновляем!"

┌─────────────────┬──────────────────────────────────────┐
│ Алгоритм        │ Порядок релаксации                   │
├─────────────────┼──────────────────────────────────────┤
│ BFS             │ По уровням (очередь FIFO)            │
│ Dijkstra        │ По минимальному dist (приоритет)     │
│ Bellman-Ford    │ Все рёбра, V-1 раз                   │
│ Floyd-Warshall  │ Через все промежуточные k            │
│ 0-1 BFS         │ Deque: вес 0 → начало, вес 1 → конец │
│ A*              │ По минимальному f = g + h            │
└─────────────────┴──────────────────────────────────────┘
```

---

### Модель 5: Сложность алгоритмов — быстрая шпаргалка

```
┌────────────────────────────────────────────────────────────┐
│                  СЛОЖНОСТЬ АЛГОРИТМОВ                      │
├─────────────────┬──────────────┬───────────┬───────────────┤
│ Алгоритм        │ Время        │ Память    │ Neg weights?  │
├─────────────────┼──────────────┼───────────┼───────────────┤
│ BFS             │ O(V+E)       │ O(V)      │ Нет           │
│ Dijkstra        │ O(E log V)   │ O(V)      │ Нет           │
│ Bellman-Ford    │ O(VE)        │ O(V)      │ ДА            │
│ SPFA (avg)      │ O(E)         │ O(V)      │ ДА            │
│ Floyd-Warshall  │ O(V³)        │ O(V²)     │ ДА            │
│ Johnson's       │ O(V²log V+VE)│ O(V²)     │ ДА            │
│ A*              │ O(E)~O(b^d)  │ O(V)      │ Нет           │
│ Bidirectional   │ O(b^(d/2))   │ O(b^(d/2))│ Нет           │
└─────────────────┴──────────────┴───────────┴───────────────┘

Где:
  V = вершины, E = рёбра
  b = branching factor (среднее число соседей)
  d = глубина решения (длина пути)
```

---

## Зачем это нужно?

**Проблема:**

```
Dijkstra отлично работает, но:
1. Не работает с negative weights
2. Single-source → для all-pairs нужно V запусков
3. Не использует информацию о цели (слепой поиск)

Нужны специализированные алгоритмы!
```

**Когда какой алгоритм:**

| Задача | Алгоритм | Сложность |
|--------|----------|-----------|
| All-pairs, dense graph | Floyd-Warshall | O(V³) |
| All-pairs, sparse, neg weights | Johnson's | O(V² log V + VE) |
| Single-source, neg weights | Bellman-Ford | O(VE) |
| Single-pair, known goal | A* | O(E) best case |
| Single-pair, both endpoints known | Bidirectional | O(b^(d/2)) |

---

## Floyd-Warshall Algorithm

### Что это?

Алгоритм для поиска кратчайших путей между **всеми парами вершин**. Работает с negative weights (но не с negative cycles).

### Ключевая идея

```
Динамическое программирование:
dp[k][i][j] = кратчайший путь от i до j,
              используя только вершины {0, 1, ..., k} как промежуточные

Переход:
dp[k][i][j] = min(dp[k-1][i][j],           // не используем k
                  dp[k-1][i][k] + dp[k-1][k][j])  // используем k

Оптимизация: можно хранить только текущий слой dp[i][j]
```

### Визуализация

```
Граф:           Матрица смежности (INF = ∞):
    1
  ↙   ↘           0    1    2    3
 2  →  3        ┌────────────────────┐
  ↘   ↙       0 │  0    5    ∞    10 │
    4         1 │  ∞    0    3    ∞  │
              2 │  ∞    ∞    0    1  │
              3 │  ∞    ∞    ∞    0  │
                └────────────────────┘

После Floyd-Warshall:
                  0    1    2    3
                ┌────────────────────┐
              0 │  0    5    8    9  │
              1 │  ∞    0    3    4  │
              2 │  ∞    ∞    0    1  │
              3 │  ∞    ∞    ∞    0  │
                └────────────────────┘
```

### Реализация (Kotlin)

```kotlin
/**
 * Floyd-Warshall — кратчайшие пути между ВСЕМИ парами вершин
 *
 * ИДЕЯ: DP по промежуточным вершинам
 *       dist[i][j] через {0..k} = min(dist через {0..k-1}, dist[i][k] + dist[k][j])
 *
 * СЛОЖНОСТЬ: O(V³) время, O(V²) память
 */
class FloydWarshall(private val n: Int) {
    // INF: достаточно большой, но INF + INF не переполняет Long
    private val INF = 1e9.toLong()
    private val dist = Array(n) { LongArray(n) { INF } }
    // next[i][j] = следующая вершина на пути i → j (для восстановления пути)
    private val next = Array(n) { IntArray(n) { -1 } }

    init {
        for (i in 0 until n) {
            dist[i][i] = 0
            next[i][i] = i
        }
    }

    fun addEdge(from: Int, to: Int, weight: Long) {
        dist[from][to] = weight
        next[from][to] = to
    }

    /**
     * Порядок циклов КРИТИЧЕН: k (промежуточные вершины) ДОЛЖЕН быть внешним!
     *
     * ПОЧЕМУ: На итерации k мы разрешаем использовать вершины {0..k}.
     *         dist[i][j] обновляется через уже вычисленные dist[i][k] и dist[k][j].
     *         Если k внутри — нарушается DP-инвариант.
     */
    fun compute(): Boolean {
        for (k in 0 until n) {
            for (i in 0 until n) {
                for (j in 0 until n) {
                    // Проверяем на INF чтобы избежать overflow (INF + вес)
                    if (dist[i][k] < INF && dist[k][j] < INF) {
                        if (dist[i][k] + dist[k][j] < dist[i][j]) {
                            dist[i][j] = dist[i][k] + dist[k][j]
                            next[i][j] = next[i][k]
                        }
                    }
                }
            }
        }

        // Negative cycle detection: если dist[v][v] < 0, есть отрицательный цикл
        for (i in 0 until n) {
            if (dist[i][i] < 0) return false
        }
        return true
    }

    fun getDistance(from: Int, to: Int): Long = dist[from][to]

    /**
     * Восстановление пути через next[][]
     * next[i][j] хранит первую вершину после i на пути к j
     */
    fun getPath(from: Int, to: Int): List<Int>? {
        if (dist[from][to] >= INF) return null

        val path = mutableListOf(from)
        var current = from
        while (current != to) {
            current = next[current][to]
            if (current == -1) return null
            path.add(current)
        }
        return path
    }
}
```

### Использование

```kotlin
val fw = FloydWarshall(4)
fw.addEdge(0, 1, 5)
fw.addEdge(0, 3, 10)
fw.addEdge(1, 2, 3)
fw.addEdge(2, 3, 1)

if (fw.compute()) {
    println(fw.getDistance(0, 3))  // 9 (0→1→2→3)
    println(fw.getPath(0, 3))      // [0, 1, 2, 3]
} else {
    println("Negative cycle detected")
}
```

### Сложность

| Операция | Время | Память |
|----------|-------|--------|
| Compute | O(V³) | O(V²) |
| Get distance | O(1) | — |
| Get path | O(V) | — |

---

## Bellman-Ford Algorithm

### Что это?

Single-source shortest path с поддержкой **negative weights** и **детекцией negative cycles**.

### Ключевая идея

```
Релаксация рёбер V-1 раз:
- Кратчайший путь содержит максимум V-1 рёбер
- После V-1 итераций все кратчайшие пути найдены
- Если на V-й итерации что-то улучшилось → negative cycle!
```

### Визуализация работы

```
Граф с negative edge:
    A ──2──→ B
    │        │
    4       -3
    ↓        ↓
    C ←──1── D

Итерация 0: dist = [0, ∞, ∞, ∞]  (A=0)
Итерация 1: dist = [0, 2, 4, ∞]  (B через A, C через A)
Итерация 2: dist = [0, 2, 4, -1] (D через B: 2-3=-1)
Итерация 3: dist = [0, 2, 0, -1] (C через D: -1+1=0)

Финал: dist(A→C) = 0, а не 4! (путь A→B→D→C)
```

### Реализация (Kotlin)

```kotlin
/**
 * Bellman-Ford — кратчайшие пути с отрицательными весами
 *
 * ИДЕЯ: Релаксация всех рёбер V-1 раз
 *       Кратчайший путь без цикла содержит ≤ V-1 рёбер
 *
 * СЛОЖНОСТЬ: O(V × E)
 */
class BellmanFord(private val n: Int) {
    data class Edge(val from: Int, val to: Int, val weight: Long)

    private val INF = Long.MAX_VALUE / 2
    private val edges = mutableListOf<Edge>()
    private val dist = LongArray(n) { INF }
    private val parent = IntArray(n) { -1 }

    fun addEdge(from: Int, to: Int, weight: Long) {
        edges.add(Edge(from, to, weight))
    }

    /**
     * Вычисление кратчайших путей
     * @return true если нет отрицательного цикла
     */
    fun compute(source: Int): Boolean {
        dist[source] = 0

        // V-1 итераций: кратчайший путь без циклов имеет ≤ V-1 рёбер
        repeat(n - 1) {
            var relaxed = false
            for (e in edges) {
                if (dist[e.from] < INF && dist[e.from] + e.weight < dist[e.to]) {
                    dist[e.to] = dist[e.from] + e.weight
                    parent[e.to] = e.from
                    relaxed = true
                }
            }
            // Early termination: если ничего не изменилось, дальше не изменится
            if (!relaxed) return true
        }

        // V-я итерация: если что-то улучшилось → отрицательный цикл!
        // (можно бесконечно уменьшать путь, проходя по циклу)
        for (e in edges) {
            if (dist[e.from] < INF && dist[e.from] + e.weight < dist[e.to]) {
                return false
            }
        }

        return true
    }

    /**
     * Поиск и восстановление отрицательного цикла
     */
    fun findNegativeCycle(source: Int): List<Int>? {
        dist.fill(INF)
        dist[source] = 0

        var cycleVertex = -1

        repeat(n) { iteration ->
            cycleVertex = -1
            for (e in edges) {
                if (dist[e.from] < INF && dist[e.from] + e.weight < dist[e.to]) {
                    // Ограничиваем -INF чтобы избежать overflow при дальнейших сложениях
                    dist[e.to] = maxOf(-INF, dist[e.from] + e.weight)
                    parent[e.to] = e.from
                    cycleVertex = e.to
                }
            }
        }

        if (cycleVertex == -1) return null

        // Проходим n шагов по parent[], чтобы гарантированно попасть В цикл
        // (не на "хвост", ведущий к циклу)
        repeat(n) { cycleVertex = parent[cycleVertex] }

        // Собираем цикл, начиная с cycleVertex
        val cycle = mutableListOf<Int>()
        var v = cycleVertex
        do {
            cycle.add(v)
            v = parent[v]
        } while (v != cycleVertex)
        cycle.add(cycleVertex)

        return cycle.reversed()
    }

    fun getDistance(to: Int): Long = dist[to]

    fun getPath(to: Int): List<Int>? {
        if (dist[to] >= INF) return null
        val path = mutableListOf<Int>()
        var v = to
        while (v != -1) {
            path.add(v)
            v = parent[v]
        }
        return path.reversed()
    }
}
```

### SPFA (Shortest Path Faster Algorithm)

```kotlin
/**
 * SPFA — оптимизация Bellman-Ford с очередью
 *
 * ИДЕЯ: Релаксируем только те рёбра, откуда пришло улучшение.
 *       Храним вершины с обновлённым dist в очереди.
 *
 * СЛОЖНОСТЬ: O(E) в среднем, O(VE) в worst case
 * Worst case на специально подобранных графах (не рекомендуется для соревнований)
 */
fun spfa(source: Int): Boolean {
    dist.fill(INF)
    dist[source] = 0

    val inQueue = BooleanArray(n)
    // Счётчик: сколько раз вершина попадала в очередь
    // Если > n → отрицательный цикл (бесконечное улучшение)
    val count = IntArray(n)

    val queue = ArrayDeque<Int>()
    queue.add(source)
    inQueue[source] = true

    while (queue.isNotEmpty()) {
        val u = queue.removeFirst()
        inQueue[u] = false

        for (e in adj[u]) {
            if (dist[u] + e.weight < dist[e.to]) {
                dist[e.to] = dist[u] + e.weight
                parent[e.to] = u

                if (!inQueue[e.to]) {
                    queue.add(e.to)
                    inQueue[e.to] = true
                    count[e.to]++

                    // Вершина в очереди > n раз → она на отрицательном цикле
                    if (count[e.to] > n) return false
                }
            }
        }
    }
    return true
}
```

### Сложность

| Операция | Время | Память |
|----------|-------|--------|
| Standard | O(VE) | O(V + E) |
| SPFA average | O(E) | O(V + E) |
| SPFA worst | O(VE) | O(V + E) |

---

## Johnson's Algorithm

### Что это?

All-pairs shortest path для **sparse графов** с negative weights. Комбинирует Bellman-Ford и Dijkstra.

### Ключевая идея

```
Проблема: Dijkstra не работает с negative weights
Решение: "Перевзвесить" рёбра чтобы все стали ≥ 0

1. Добавить фиктивную вершину q со связями к всем (вес 0)
2. Bellman-Ford от q → получаем h[v] для всех v
3. Новый вес: w'(u,v) = w(u,v) + h[u] - h[v] ≥ 0
4. V раз Dijkstra на новом графе
5. Корректируем расстояния: d(u,v) = d'(u,v) - h[u] + h[v]
```

### Почему перевзвешивание работает?

```
Для любого пути P от u до v:
w'(P) = w(P) + h[u] - h[v]

h[u] и h[v] — константы для пары (u, v)
→ Если P был кратчайшим в исходном графе,
  он останется кратчайшим в перевзвешенном

Треугольное неравенство гарантирует w' ≥ 0:
h[v] ≤ h[u] + w(u,v)  (по определению кратчайшего пути)
→ w(u,v) + h[u] - h[v] ≥ 0
```

### Визуализация

```
Исходный граф:          После reweighting:
    A ──3──→ B              A ──4──→ B
    │        │              │        │
   -2        1              0        2
    ↓        ↓              ↓        ↓
    C ←──2── D              C ←──2── D

h = [0, -1, -2, 0] (от Bellman-Ford)

w'(A,B) = 3 + h[A] - h[B] = 3 + 0 - (-1) = 4
w'(A,C) = -2 + h[A] - h[C] = -2 + 0 - (-2) = 0
...

Все веса неотрицательные → можно Dijkstra!
```

### Реализация (Kotlin)

```kotlin
/**
 * Johnson's Algorithm — all-pairs shortest path для sparse графов
 *
 * ИДЕЯ: Перевзвесить рёбра так, чтобы убрать отрицательные веса,
 *       затем V раз запустить Dijkstra
 *
 * СЛОЖНОСТЬ: O(V²log V + VE) vs O(V³) у Floyd-Warshall
 *            Лучше для sparse графов (E << V²)
 */
class JohnsonAlgorithm(private val n: Int) {
    data class Edge(val to: Int, val weight: Long)

    private val adj = Array(n) { mutableListOf<Edge>() }
    private val INF = Long.MAX_VALUE / 2

    fun addEdge(from: Int, to: Int, weight: Long) {
        adj[from].add(Edge(to, weight))
    }

    fun compute(): Array<LongArray>? {
        // Шаг 1: Добавляем фиктивную вершину q, соединённую со всеми
        val extendedAdj = Array(n + 1) { mutableListOf<Edge>() }
        for (u in 0 until n) {
            extendedAdj[u].addAll(adj[u])
            // q → u с весом 0 (чтобы достичь всех вершин)
            extendedAdj[n].add(Edge(u, 0))
        }

        // Шаг 2: Bellman-Ford от q → получаем потенциалы h[v]
        val h = bellmanFord(extendedAdj, n, n + 1) ?: return null

        // Шаг 3: Перевзвешивание — w'(u,v) = w(u,v) + h[u] - h[v] ≥ 0
        val reweighted = Array(n) { mutableListOf<Edge>() }
        for (u in 0 until n) {
            for (e in adj[u]) {
                val newWeight = e.weight + h[u] - h[e.to]
                reweighted[u].add(Edge(e.to, newWeight))
            }
        }

        // Шаг 4: V раз Dijkstra на перевзвешенном графе
        val result = Array(n) { LongArray(n) { INF } }
        for (source in 0 until n) {
            val dist = dijkstra(reweighted, source, n)
            for (target in 0 until n) {
                if (dist[target] < INF) {
                    // Шаг 5: Корректируем обратно — d(u,v) = d'(u,v) - h[u] + h[v]
                    result[source][target] = dist[target] - h[source] + h[target]
                }
            }
        }

        return result
    }

    private fun bellmanFord(
        adj: Array<MutableList<Edge>>,
        source: Int,
        totalNodes: Int
    ): LongArray? {
        val dist = LongArray(totalNodes) { INF }
        dist[source] = 0

        repeat(totalNodes - 1) {
            for (u in 0 until totalNodes) {
                if (dist[u] < INF) {
                    for (e in adj[u]) {
                        if (dist[u] + e.weight < dist[e.to]) {
                            dist[e.to] = dist[u] + e.weight
                        }
                    }
                }
            }
        }

        // Проверка на отрицательный цикл (V-я итерация Bellman-Ford)
        for (u in 0 until totalNodes) {
            if (dist[u] < INF) {
                for (e in adj[u]) {
                    if (dist[u] + e.weight < dist[e.to]) {
                        return null
                    }
                }
            }
        }

        return dist
    }

    private fun dijkstra(
        adj: Array<MutableList<Edge>>,
        source: Int,
        n: Int
    ): LongArray {
        val dist = LongArray(n) { INF }
        dist[source] = 0

        // Min-heap: извлекаем вершину с минимальным расстоянием
        val pq = PriorityQueue<Pair<Long, Int>>(compareBy { it.first })
        pq.add(0L to source)

        while (pq.isNotEmpty()) {
            val (d, u) = pq.poll()
            if (d > dist[u]) continue

            for (e in adj[u]) {
                if (dist[u] + e.weight < dist[e.to]) {
                    dist[e.to] = dist[u] + e.weight
                    pq.add(dist[e.to] to e.to)
                }
            }
        }

        return dist
    }
}
```

### Когда использовать

| Граф | Johnson's | Floyd-Warshall |
|------|-----------|----------------|
| Sparse (E << V²) | ✓ Быстрее | Медленнее |
| Dense (E ≈ V²) | Одинаково | ✓ Проще |
| Negative weights | ✓ | ✓ |

### Сложность

| Операция | Время | Память |
|----------|-------|--------|
| Bellman-Ford | O(VE) | O(V) |
| V × Dijkstra | O(V² log V + VE) | O(V + E) |
| **Total** | **O(V² log V + VE)** | **O(V²)** |

---

## A* Algorithm

### Что это?

Эвристический поиск кратчайшего пути с **гарантией оптимальности** при правильной эвристике.

### Ключевая идея

```
f(n) = g(n) + h(n)

g(n) = реальная стоимость от старта до n
h(n) = эвристическая оценка от n до цели

A* выбирает вершину с минимальным f(n)
```

### Admissible Heuristic

```
Эвристика h(n) называется ДОПУСТИМОЙ если:
h(n) ≤ h*(n) для всех n

где h*(n) — реальная стоимость до цели

Допустимая эвристика ГАРАНТИРУЕТ оптимальное решение!
```

### Популярные эвристики для сетки

```kotlin
/**
 * Manhattan Distance — эвристика для 4-направленного движения
 *
 * ПРИМЕНЕНИЕ: Сетка где можно двигаться только ↑↓←→
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 * S . . . .     Расстояние от S(0,0) до G(2,3):
 * . . . . .     dx = |0-2| = 2
 * . . . G .     dy = |0-3| = 3
 *               Manhattan = 2 + 3 = 5 шагов
 * ```
 *
 * ПОЧЕМУ ДОПУСТИМАЯ (admissible):
 * - Без диагоналей нельзя дойти быстрее чем dx + dy шагов
 * - Эвристика точно равна оптимальному пути без препятствий
 * - С препятствиями реальный путь ≥ Manhattan → гарантирует оптимум
 */
fun manhattanDistance(x1: Int, y1: Int, x2: Int, y2: Int): Int {
    return abs(x1 - x2) + abs(y1 - y2)
}

/**
 * Diagonal Distance — эвристика для 8-направленного движения
 *
 * ПРИМЕНЕНИЕ: Сетка где можно двигаться в 8 направлениях (включая диагонали)
 *
 * ПАРАМЕТРЫ:
 * - D = стоимость горизонтального/вертикального шага (обычно 1)
 * - D2 = стоимость диагонального шага (обычно √2 ≈ 1.414 или 1)
 *
 * ФОРМУЛА: D * (dx + dy) + (D2 - 2*D) * min(dx, dy)
 *
 * ИНТУИЦИЯ:
 * ```
 * Если D=1, D2=1 (диагональ = 1):
 *   Chebyshev distance = max(dx, dy)
 *
 * Если D=1, D2=√2 (реалистичная диагональ):
 *   Октильное расстояние = min(dx,dy)*√2 + |dx-dy|*1
 *
 * S . . . .     dx = 2, dy = 3, min = 2
 * . \ . . .     Идём 2 шага по диагонали → (2,2)
 * . . \ G .     Потом 1 шаг вниз → (2,3) = G
 *               = 2 * √2 + 1 * 1 ≈ 3.83
 * ```
 */
fun diagonalDistance(x1: Int, y1: Int, x2: Int, y2: Int, D: Int, D2: Int): Int {
    val dx = abs(x1 - x2)
    val dy = abs(y1 - y2)
    return D * (dx + dy) + (D2 - 2 * D) * minOf(dx, dy)
}

/**
 * Euclidean Distance — эвристика для свободного движения
 *
 * ПРИМЕНЕНИЕ: Движение в любом направлении (не по сетке)
 *
 * ФОРМУЛА: √((x1-x2)² + (y1-y2)²)
 *
 * ОСОБЕННОСТИ:
 * - Самая "оптимистичная" эвристика (кратчайшая прямая)
 * - Всегда допустимая (admissible)
 * - Менее информативная чем Manhattan для сеток → больше узлов исследуется
 *
 * КОГДА ИСПОЛЬЗОВАТЬ:
 * - Роботы с омни-колёсами (движение в любом направлении)
 * - Дроны, квадрокоптеры
 * - Персонажи в играх с плавным движением
 *
 * НЕ ИСПОЛЬЗОВАТЬ:
 * - Для сеток с 4/8 направлениями — слишком оптимистична
 */
fun euclideanDistance(x1: Int, y1: Int, x2: Int, y2: Int): Double {
    val dx = x1 - x2
    val dy = y1 - y2
    return sqrt((dx * dx + dy * dy).toDouble())
}
```

### Реализация (Kotlin)

```kotlin
/**
 * A* (A-Star) — алгоритм поиска кратчайшего пути с эвристикой
 *
 * ИДЕЯ: Комбинация Dijkstra + эвристика направляет поиск к цели
 *       f(n) = g(n) + h(n), где:
 *       - g(n) = реальная стоимость от старта до n
 *       - h(n) = оценка стоимости от n до цели
 *
 * ПОШАГОВЫЙ ПРИМЕР:
 * ```
 * Сетка 3x3, старт S(0,0), цель G(2,2), # = препятствие:
 *
 * S . .     Шаг 1: openSet = {S(f=4)}  (h = Manhattan = 4)
 * . # .
 * . . G
 *
 * Шаг 2: Извлекаем S, добавляем соседей (1,0) и (0,1)
 *        openSet = {(1,0 f=4), (0,1 f=4)}
 *
 * Шаг 3: Извлекаем (1,0), сосед (2,0)
 *        openSet = {(0,1 f=4), (2,0 f=4)}
 *
 * ... продолжаем пока не достигнем G
 *
 * Путь: S → (1,0) → (2,0) → (2,1) → G
 * ```
 *
 * СЛОЖНОСТЬ: O(E log V) в худшем случае, но на практике
 *            намного быстрее благодаря эвристике
 */
class AStar(
    private val n: Int,
    private val m: Int,
    private val grid: Array<BooleanArray>,  // true = проходимая клетка
    private val heuristic: (Int, Int, Int, Int) -> Double
) {
    data class Node(
        val x: Int,
        val y: Int,
        val g: Double,  // реальная стоимость от старта
        val f: Double   // g + h (полная оценка)
    )

    // Смещения для 4 направлений: вверх, вниз, влево, вправо
    private val dx = intArrayOf(-1, 1, 0, 0)
    private val dy = intArrayOf(0, 0, -1, 1)

    fun findPath(
        startX: Int, startY: Int,
        goalX: Int, goalY: Int
    ): List<Pair<Int, Int>>? {
        /**
         * Priority Queue упорядочена по f-score (g + h)
         *
         * ПОЧЕМУ ПО f, а не по g (как в Dijkstra):
         * - g учитывает только пройденный путь
         * - f = g + h учитывает и оставшееся расстояние до цели
         * - Это направляет поиск к цели, а не во все стороны
         *
         * Визуально:
         *   Dijkstra: ищет кругами от старта ○
         *   A*: ищет эллипсом в сторону цели ⟶ ◎
         */
        val openSet = PriorityQueue<Node>(compareBy { it.f })
        val gScore = Array(n) { DoubleArray(m) { Double.MAX_VALUE } }
        val parent = Array(n) { arrayOfNulls<Pair<Int, Int>>(m) }
        val closed = Array(n) { BooleanArray(m) }

        val startH = heuristic(startX, startY, goalX, goalY)
        openSet.add(Node(startX, startY, 0.0, startH))
        gScore[startX][startY] = 0.0

        while (openSet.isNotEmpty()) {
            val current = openSet.poll()

            // ЦЕЛЬ ДОСТИГНУТА — восстанавливаем путь
            // A* гарантирует оптимальность при допустимой эвристике,
            // поэтому первое достижение цели = кратчайший путь
            if (current.x == goalX && current.y == goalY) {
                return reconstructPath(parent, goalX, goalY)
            }

            if (closed[current.x][current.y]) continue
            closed[current.x][current.y] = true

            /**
             * ИССЛЕДОВАНИЕ СОСЕДЕЙ (relaxation)
             *
             * Для каждого соседа проверяем:
             * 1. Находится ли в границах сетки
             * 2. Проходим ли (не стена)
             * 3. Не обработан ли уже (closed)
             * 4. Нашли ли более короткий путь через current
             *
             * Если нашли лучший путь — обновляем gScore и добавляем в очередь
             */
            for (i in 0 until 4) {
                val nx = current.x + dx[i]
                val ny = current.y + dy[i]

                if (nx !in 0 until n || ny !in 0 until m) continue
                if (!grid[nx][ny] || closed[nx][ny]) continue

                val tentativeG = gScore[current.x][current.y] + 1.0

                if (tentativeG < gScore[nx][ny]) {
                    parent[nx][ny] = current.x to current.y
                    gScore[nx][ny] = tentativeG

                    val h = heuristic(nx, ny, goalX, goalY)
                    val f = tentativeG + h

                    openSet.add(Node(nx, ny, tentativeG, f))
                }
            }
        }

        return null  // Путь не найден (цель недостижима)
    }

    private fun reconstructPath(
        parent: Array<Array<Pair<Int, Int>?>>,
        goalX: Int, goalY: Int
    ): List<Pair<Int, Int>> {
        val path = mutableListOf<Pair<Int, Int>>()
        var current: Pair<Int, Int>? = goalX to goalY

        while (current != null) {
            path.add(current)
            current = parent[current.first][current.second]
        }

        return path.reversed()
    }
}
```

### A* vs Dijkstra

```
            Dijkstra                    A*
         ┌─────────────┐          ┌─────────────┐
         │  • • • • •  │          │      •      │
         │ • • • • • • │          │     • •     │
         │• • S • • • •│          │    • S •    │
         │ • • • • • • │          │     • • •   │
         │  • • • • • •│          │      • • G  │
         │   • • • G   │          │             │
         └─────────────┘          └─────────────┘
         Исследует всё             Направлен к цели

A* с хорошей эвристикой исследует значительно меньше вершин
```

### Сложность

| Случай | Время | Память |
|--------|-------|--------|
| Best | O(d) | O(d) |
| Worst | O(b^d) | O(b^d) |
| With good heuristic | O(b^(d/2)) | O(b^(d/2)) |

Где d — глубина решения, b — branching factor.

---

## Bidirectional Search

### Что это?

Поиск одновременно от старта и от цели, встреча посередине.

### Ключевая идея

```
Обычный BFS: исследует O(b^d) вершин

Bidirectional:
- От старта: O(b^(d/2))
- От цели: O(b^(d/2))
- Итого: 2 × O(b^(d/2)) << O(b^d)

Пример: b=10, d=6
- BFS: 10^6 = 1,000,000
- Bidirectional: 2 × 10^3 = 2,000
```

### Визуализация

```
         Обычный BFS              Bidirectional

    S • • • • • • • G         S • • • • • • • G
    │ • • • • • • • │         │ • ←───┬───→ • │
    │ • • • • • • • │         │   • • │ • •   │
    │ • • • • • • • │         │     • │ •     │
    │ • • • • • • • │         │       │       │
    └───────────────┘         └───────┴───────┘
      Исследует всё             Встреча в середине
```

### Реализация (Kotlin)

```kotlin
/**
 * Bidirectional BFS — поиск кратчайшего пути с двух сторон
 *
 * ИДЕЯ: Запускаем BFS одновременно от старта и от цели
 *       Когда волны встречаются — нашли путь
 *
 * ПОШАГОВЫЙ ПРИМЕР:
 * ```
 * Граф: 0 — 1 — 2 — 3 — 4 — 5
 *       Старт = 0, Цель = 5
 *
 * Шаг 1: forward = {0}, backward = {5}
 * Шаг 2: forward = {1}, backward = {4}
 * Шаг 3: forward = {2}, backward = {3}
 * Шаг 4: forward = {3} — ВСТРЕЧА! 3 уже в backward
 *
 * Путь: 0 → 1 → 2 → 3 → 4 → 5
 *
 * Обычный BFS: 6 вершин
 * Bidirectional: 4 шага (быстрее!)
 * ```
 *
 * СЛОЖНОСТЬ: O(b^(d/2)) вместо O(b^d)
 *            При b=10, d=6: 2×10³ вместо 10⁶
 */
class BidirectionalBFS(private val n: Int) {
    private val adj = Array(n) { mutableListOf<Int>() }

    /**
     * Добавляем ребро в обе стороны
     *
     * ПОЧЕМУ В ОБЕ СТОРОНЫ:
     * - Backward поиск идёт от цели к старту
     * - Ему нужны обратные рёбра для движения "назад"
     * - Для неориентированного графа: adj[to].add(from) уже есть
     * - Для ориентированного: нужно хранить отдельный обратный граф
     */
    fun addEdge(from: Int, to: Int) {
        adj[from].add(to)
        adj[to].add(from)
    }

    fun findPath(start: Int, goal: Int): List<Int>? {
        if (start == goal) return listOf(start)

        /**
         * ДВЕ ОЧЕРЕДИ — сердце Bidirectional поиска
         *
         * forwardQueue: волна от старта → к цели
         * backwardQueue: волна от цели → к старту
         *
         * visited хранят parent для восстановления пути:
         * - forwardVisited[node] = откуда пришли со стороны старта
         * - backwardVisited[node] = откуда пришли со стороны цели
         */
        val forwardQueue = ArrayDeque<Int>()
        val backwardQueue = ArrayDeque<Int>()

        val forwardVisited = mutableMapOf<Int, Int>()  // node → parent
        val backwardVisited = mutableMapOf<Int, Int>() // node → parent

        forwardQueue.add(start)
        backwardQueue.add(goal)
        forwardVisited[start] = -1   // -1 означает "нет родителя"
        backwardVisited[goal] = -1

        while (forwardQueue.isNotEmpty() && backwardQueue.isNotEmpty()) {
            /**
             * ОПТИМИЗАЦИЯ: расширяем МЕНЬШИЙ фронтир
             *
             * ПОЧЕМУ ЭТО ВАЖНО:
             * ```
             * Без оптимизации: всегда сначала forward, потом backward
             *   forward: 1 → 10 → 100 → 1000 вершин
             *   backward: 1 → 10 → 100 вершин
             *
             * С оптимизацией: всегда расширяем меньшую волну
             *   Волны растут равномерно → встреча раньше
             *   Меньше вершин исследуется в сумме
             * ```
             */
            val meetingNode = if (forwardQueue.size <= backwardQueue.size) {
                expandFrontier(forwardQueue, forwardVisited, backwardVisited)
            } else {
                expandFrontier(backwardQueue, backwardVisited, forwardVisited)
            }

            if (meetingNode != null) {
                return reconstructPath(meetingNode, forwardVisited, backwardVisited)
            }
        }

        return null
    }

    /**
     * Расширение одного фронтира на один уровень BFS
     *
     * @return вершина пересечения если волны встретились, иначе null
     */
    private fun expandFrontier(
        queue: ArrayDeque<Int>,
        visited: MutableMap<Int, Int>,
        otherVisited: Map<Int, Int>
    ): Int? {
        if (queue.isEmpty()) return null

        val current = queue.removeFirst()

        for (neighbor in adj[current]) {
            if (neighbor in visited) continue

            visited[neighbor] = current

            /**
             * ПРОВЕРКА ПЕРЕСЕЧЕНИЯ ВОЛН
             *
             * Если сосед уже посещён ДРУГИМ направлением:
             * - Волны встретились!
             * - neighbor — точка встречи
             *
             * Визуально:
             * ```
             * forward:  S → a → b → [neighbor]
             * backward: G → x → y → [neighbor]
             *                        ↑
             *                   Точка встречи!
             * ```
             */
            if (neighbor in otherVisited) {
                return neighbor
            }

            queue.add(neighbor)
        }

        return null
    }

    /**
     * Восстановление полного пути из точки встречи
     */
    private fun reconstructPath(
        meeting: Int,
        forwardVisited: Map<Int, Int>,
        backwardVisited: Map<Int, Int>
    ): List<Int> {
        /**
         * ЧАСТЬ 1: путь от старта до meeting
         *
         * Идём по цепочке родителей в forwardVisited:
         * meeting ← ... ← a ← start
         * Затем разворачиваем: start → a → ... → meeting
         */
        val forwardPath = mutableListOf<Int>()
        var node: Int? = meeting
        while (node != null && node != -1) {
            forwardPath.add(node)
            node = forwardVisited[node]
        }
        forwardPath.reverse()

        /**
         * ЧАСТЬ 2: путь от meeting до цели (БЕЗ meeting!)
         *
         * meeting уже включён в forwardPath, поэтому
         * начинаем с backwardVisited[meeting] (следующий после meeting)
         *
         * backwardVisited хранит путь: goal ← ... ← meeting
         * Читаем как есть (уже в правильном порядке)
         */
        val backwardPath = mutableListOf<Int>()
        node = backwardVisited[meeting]
        while (node != null && node != -1) {
            backwardPath.add(node)
            node = backwardVisited[node]
        }

        return forwardPath + backwardPath
    }
}
```

### Когда использовать

| Условие | Подходит |
|---------|----------|
| Известны start и goal | ✓ |
| Одинаковый branching factor | ✓ |
| Можно идти в обе стороны | ✓ |
| Только start известен | ✗ Используй BFS/DFS |

---

## Сравнение алгоритмов

| Алгоритм | Задача | Negative | Time | Space |
|----------|--------|----------|------|-------|
| Floyd-Warshall | All-pairs | ✓ | O(V³) | O(V²) |
| Johnson's | All-pairs (sparse) | ✓ | O(V² log V + VE) | O(V²) |
| Bellman-Ford | Single-source | ✓ | O(VE) | O(V) |
| Dijkstra | Single-source | ✗ | O(E log V) | O(V) |
| A* | Single-pair | ✗ | O(E) ~ O(b^d) | O(V) |
| Bidirectional | Single-pair | ✗ | O(b^(d/2)) | O(b^(d/2)) |

---

## Практика

### Концептуальные вопросы

1. **Почему порядок циклов в Floyd-Warshall важен?**

   K должен быть внешним, потому что мы строим DP по промежуточным вершинам: сначала пути через вершину 0, потом через 0 и 1, и т.д.

2. **Когда A* становится Dijkstra?**

   Когда h(n) = 0 для всех n. Эвристика не даёт направления, поиск становится "слепым".

3. **Почему Bidirectional эффективнее?**

   Площадь двух кругов радиуса d/2 меньше одного круга радиуса d: 2πr² < π(2r)² = 4πr².

### LeetCode задачи

| # | Название | Сложность | Алгоритм |
|---|----------|-----------|----------|
| 787 | Cheapest Flights K Stops | Medium | Bellman-Ford |
| 743 | Network Delay Time | Medium | Dijkstra/Bellman-Ford |
| 1334 | Find City with Smallest Neighbors | Medium | Floyd-Warshall |
| 127 | Word Ladder | Hard | Bidirectional BFS |
| 752 | Open the Lock | Medium | BFS / Bidirectional |

---

## Связанные темы

### Prerequisites
- [Graphs](../data-structures/graphs.md)
- [BFS/DFS Patterns](../patterns/dfs-bfs-patterns.md)
- Dynamic Programming basics

### Unlocks
- [Minimum Spanning Tree](./minimum-spanning-tree.md)
- [Shortest Paths](./shortest-paths.md)
- [Network Flow](./network-flow.md)

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms: Floyd-Warshall](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html) | Reference | Implementation |
| 2 | [CP-Algorithms: Bellman-Ford](https://cp-algorithms.com/graph/bellman_ford.html) | Reference | Negative cycles |
| 3 | [Stanford: A* Heuristics](http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html) | Tutorial | Heuristic design |
| 4 | [Brilliant: Johnson's Algorithm](https://brilliant.org/wiki/johnsons-algorithm/) | Wiki | Reweighting |
| 5 | [Wikipedia: Bidirectional Search](https://en.wikipedia.org/wiki/Bidirectional_search) | Reference | Theory |
| 6 | [Quanta Magazine 2024](https://www.quantamagazine.org/) | News | Sorting barrier breakthrough |

---

*Обновлено: 2026-01-09 — добавлены педагогические секции (интуиция Floyd-Warshall/Bellman-Ford/Johnson's/A*/Bidirectional, 6 типичных ошибок, 5 ментальных моделей)*
