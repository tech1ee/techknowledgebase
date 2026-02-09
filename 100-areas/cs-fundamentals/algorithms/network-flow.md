---
title: "Сетевые потоки (Network Flow)"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/expert
related:
  - "[[graph-algorithms]]"
  - "[[graph-advanced]]"
  - "[[shortest-paths]]"
---

# Network Flow

## TL;DR

Network Flow — нахождение максимального потока из source в sink. **Ford-Fulkerson** — O(E × max_flow), **Edmonds-Karp** (BFS) — O(VE²), **Dinic** — O(V²E). Max-Flow = Min-Cut (теорема). Применения: bipartite matching, edge-disjoint paths, project selection.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Водопроводная система

Представьте городское водоснабжение:

```
            ┌─────────────────────────────────────────────────────┐
            │            ВОДОПРОВОДНАЯ СИСТЕМА ГОРОДА             │
            └─────────────────────────────────────────────────────┘

     ВОДОХРАНИЛИЩЕ (source)                          ГОРОД (sink)
           ▼                                              ▲
           ║                                              ║
           ║ труба 10 л/сек                              ║
           ╠════════════════╗                             ║
           ║                ║                             ║
           ║            НАСОСНАЯ А                        ║
           ║                ║                             ║
           ║                ╠═══════════════╗            ║
           ║                ║     5 л/сек   ║            ║
           ║                ║               ╠════════════╝
           ║            труба 8 л/сек       ║   7 л/сек
           ║                ║               ║
           ║                ╠═══════════════╣
           ║                    НАСОСНАЯ Б
           ║                         ║
           ╠═════════════════════════╝
                        6 л/сек
```

**Ключевые ограничения:**
- Каждая труба имеет **пропускную способность** (capacity) — максимум воды в секунду
- Вода не появляется и не исчезает в промежуточных точках (conservation)
- Мы хотим максимизировать поток воды в город

**Bottleneck (узкое место):** Если путь идёт через трубы 10→8→5, то максимум 5 л/сек — лимитирует самая узкая труба.

### Аналогия 2: Дорожное движение

```
                    ПРОБКА НА ВЪЕЗДЕ В ГОРОД

      Трасса             Развязка А          Центр города
     (source)    ════════════════════════>      (sink)
         │          3 полосы                      ▲
         │                                        │
         │                                        │
         └────────> Развязка Б ──────────────────┘
               2 полосы        2 полосы

    Пропускная способность:
    • Трасса → А: 3000 машин/час
    • А → Центр: 2000 машин/час    ← BOTTLENECK!
    • Трасса → Б: 2000 машин/час
    • Б → Центр: 2000 машин/час

    Max flow = 4000 машин/час (2000 через А + 2000 через Б)
    Узкое место НЕ на въезде, а на выезде из развязки А!
```

**Интуиция про Min-Cut:** Чтобы заблокировать весь трафик в город, нужно перекрыть минимум рёбер с суммарной пропускной способностью = max flow.

### Аналогия 3: Сеть курьеров (Bipartite Matching)

```
                    СЛУЖБА ДОСТАВКИ

    КУРЬЕРЫ              ЗАКАЗЫ           Вопрос: Сколько заказов
       │                   │              можно выполнить одновременно?
       ▼                   ▼

    Петя ─────────────> Заказ 1           Каждый курьер берёт 1 заказ
       │ ╲
       │  ╲
    Вася ───────────────> Заказ 2         Каждый заказ выполняет 1 курьер
       │   ╲
       │    ╲
    Маша ─────────────────> Заказ 3       Max matching = Max flow
                                          с capacity=1 везде
```

**Редукция к Flow:**
- Добавляем виртуальный **source** — начальник отдела
- Добавляем виртуальный **sink** — клиенты
- Все рёбра capacity = 1 (каждый работает один раз)

### Числовой пример: Ford-Fulkerson пошагово

```
    ИСХОДНАЯ СЕТЬ:

         s ──(10)──> A ──(5)──> t
         │          ▲ │         ▲
        (10)       (5)(2)      (10)
         │          │ ▼         │
         └───────> B ──(8)─────┘

    Числа в скобках = capacity
```

**Итерация 1: Находим путь s → A → t**
```
    Путь: s → A → t
    Bottleneck: min(10, 5) = 5
    Пропускаем 5 единиц

    Residual graph после итерации 1:
         s ──(5)──> A ──(0)──> t
         │   (5)←  ▲ │   (5)←  ▲
        (10)      (5)(2)      (10)
         │         │ ▼         │
         └───────> B ──(8)─────┘

    Красным: обратные рёбра (можно "отменить" поток)
```

**Итерация 2: Находим путь s → B → t**
```
    Путь: s → B → t
    Bottleneck: min(10, 8) = 8
    Пропускаем 8 единиц

    Total flow = 5 + 8 = 13
```

**Итерация 3: Находим путь s → B → A → t**
```
    Остаточная сеть:
         s ──(5)──> A ──(0)──> t
         │   (5)←  ▲ │   (5)←  ▲
        (2)       (5)(2)      (10-8=2)
         │  (8)←   │ ▼         │
         └───────> B ──(0)─────┘

    Путь: s → B → A → t (через обратное B→A!)
    Но B→A capacity = 5, и s→B осталось 2
    Bottleneck: min(2, 5, 2) = 2

    Total flow = 13 + 2 = 15
```

**Итерация 4: Нет путей из s в t**
```
    Все пути заблокированы → MAX FLOW = 15
```

### Магия обратных рёбер

```
    ЗАЧЕМ НУЖНЫ ОБРАТНЫЕ РЁБРА?

    Представьте: вы начали не с лучшего пути.

    Шаг 1: s → A → B → t (плохой выбор!)
    ┌───────────────────────────────────┐
    │     s ───> A ───> B ───> t        │
    │         ↓     ↓                   │
    │     Заняли ребро A→B              │
    └───────────────────────────────────┘

    Шаг 2: Хотим s → B → t, но B занята!
    ┌───────────────────────────────────┐
    │     Обратное ребро B→A позволяет  │
    │     "переместить" поток:          │
    │                                   │
    │     s → B → A (отменяем A→B)      │
    │           ↓                       │
    │           t                       │
    └───────────────────────────────────┘

    По сути: "Ой, ошибся! Переделываю маршрут."
```

### Теорема Max-Flow = Min-Cut

```
    ИНТУИЦИЯ: Горлышко бутылки

    ═══════════════════════════════════════════════════

        SOURCE                               SINK
           │                                   │
           │      ┌─────────────────────┐      │
           ●══════│    УЗКОЕ МЕСТО      │══════●
                  │    (Min-Cut)        │
                  └─────────────────────┘

    ═══════════════════════════════════════════════════

    Сколько бы труб ни было на входе,
    если все они проходят через узкое место capacity = C,
    то max flow ≤ C.

    И наоборот: max flow достигает этого предела!
```

**Min-Cut — это ответ на вопрос:** "Какие трубы перерезать, чтобы полностью остановить поток, и при этом 'стоимость' резки минимальна?"

---

## Часть 2: Почему это сложно

### Типичные ошибки студентов

#### Ошибка 1: Забыли обратные рёбра

```kotlin
// ❌ НЕПРАВИЛЬНО: нет обратных рёбер
fun addEdge(from: Int, to: Int, cap: Int) {
    capacity[from][to] = cap
    adj[from].add(to)
    // Где обратное ребро?!
}

// ✅ ПРАВИЛЬНО: обязательно добавляем обратное
fun addEdge(from: Int, to: Int, cap: Int) {
    capacity[from][to] = cap
    adj[from].add(to)
    adj[to].add(from)  // Обратное ребро с capacity=0!
}
```

**СИМПТОМ:** Алгоритм находит неоптимальный поток, зависит от порядка поиска путей.

**РЕШЕНИЕ:** Обратные рёбра — это НЕ реальные трубы. Это механизм "отмены" неудачных решений. В начале их capacity = 0.

#### Ошибка 2: Путаница между capacity и flow

```
    ПУТАНИЦА:

    capacity[u][v] = ?

    Версия 1: Это ИЗНАЧАЛЬНАЯ пропускная способность
    Версия 2: Это ОСТАТОЧНАЯ пропускная способность

    В большинстве реализаций capacity[u][v] — это RESIDUAL,
    то есть "сколько ЕЩЁ можно пропустить".

    flow = original_capacity - current_capacity
```

**СИМПТОМ:** Неправильные обновления, поток превышает capacity.

**РЕШЕНИЕ:** Чётко определите, что хранит ваш массив capacity. Для простоты храните residual capacity.

#### Ошибка 3: Неправильное обновление residual graph

```kotlin
// ❌ НЕПРАВИЛЬНО: только уменьшаем прямое ребро
capacity[u][v] -= pathFlow

// ✅ ПРАВИЛЬНО: обновляем оба направления
capacity[u][v] -= pathFlow  // Прямое: уменьшаем
capacity[v][u] += pathFlow  // Обратное: увеличиваем

// ЛОГИКА:
// - Прямое ребро: "осталось меньше capacity"
// - Обратное ребро: "можем отменить этот поток"
```

**СИМПТОМ:** Алгоритм зацикливается или даёт неверный ответ.

#### Ошибка 4: Ford-Fulkerson с DFS на больших capacities

```
    ПРОБЛЕМА С DFS:

    Capacity рёбер: 1000000

    DFS может выбирать "плохие" пути:
    Итерация 1: поток +1
    Итерация 2: поток +1
    ...
    Итерация 1000000: поток +1

    Время: O(E × max_flow) = O(E × 10^6) — СЛИШКОМ ДОЛГО!

    РЕШЕНИЕ: Используйте BFS (Edmonds-Karp) или Dinic
```

**СИМПТОМ:** TLE на больших графах или больших capacities.

**РЕШЕНИЕ:** Никогда не используйте чистый Ford-Fulkerson с DFS в продакшене. Используйте Edmonds-Karp (BFS) или Dinic.

#### Ошибка 5: Неправильная редукция к потокам

```
    ЗАДАЧА: Максимальное паросочетание

    ❌ НЕПРАВИЛЬНО:
    - Просто соединили левые с правыми
    - Забыли source и sink
    - Поставили capacity > 1

    ✅ ПРАВИЛЬНО:

        SOURCE ──(1)──> Левые вершины
                            │
                           (1) для каждого ребра
                            │
                            ▼
                        Правые вершины ──(1)──> SINK

    Все capacity = 1, чтобы каждая вершина
    участвовала максимум в одном паросочетании!
```

**СИМПТОМ:** Результат не соответствует условию задачи.

**РЕШЕНИЕ:** Тщательно продумайте редукцию. Нарисуйте граф потока. Проверьте, что constraints исходной задачи отражены в capacities.

#### Ошибка 6: Min-Cut находят до вычисления Max-Flow

```kotlin
// ❌ НЕПРАВИЛЬНО: ищем min-cut в исходном графе
fun wrongMinCut() {
    // BFS в ИСХОДНОМ графе — бессмысленно!
    // Min-cut определяется ПОСЛЕ насыщения потоком
}

// ✅ ПРАВИЛЬНО: сначала max flow, потом min cut
fun correctMinCut() {
    maxFlow(source, sink)  // СНАЧАЛА насыщаем сеть

    // ТЕПЕРЬ BFS в RESIDUAL графе
    // Вершины, достижимые из source = одна сторона разреза
    // Недостижимые = другая сторона
    // Насыщенные рёбра между ними = min cut
}
```

**СИМПТОМ:** Получаете неправильный разрез или его вес ≠ max flow.

---

## Часть 3: Ментальные модели

### Модель 1: Жидкость в трубах

```
    ФИЗИЧЕСКАЯ МОДЕЛЬ

    ●═══════════════●═══════════════●
    SOURCE          junction         SINK

    Законы:
    1. Жидкость не сжимается (conservation)
    2. Труба не пропускает больше своей ширины (capacity)
    3. Жидкость течёт от высокого давления к низкому (source→sink)

    Max flow = Сколько воды дойдёт до sink, если открыть кран на максимум
```

**Когда использовать:** Для понимания базовой концепции. Жидкость — интуитивно понятная аналогия.

### Модель 2: Игра "Толкай поток"

```
    ПОШАГОВАЯ ИГРА

    Правила:
    1. Стоишь в SOURCE с бесконечным запасом "монет"
    2. Каждый ход: выбираешь путь до SINK
    3. Толкаешь по нему min(capacities) монет
    4. Уменьшаешь capacity на пути
    5. Повторяешь, пока есть пути

    Хитрость: Обратные рёбра позволяют "забрать" монеты обратно
    и направить по другому пути.

    Победа: Собрать максимум монет в SINK
```

**Когда использовать:** Для понимания алгоритма Ford-Fulkerson. Каждая итерация — один ход.

### Модель 3: Бухгалтерия потоков

```
    БАЛАНС В КАЖДОЙ ВЕРШИНЕ

    ┌─────────────────────────────────────────────────┐
    │  Для каждой вершины v ≠ source, sink:          │
    │                                                 │
    │       Σ (входящий поток) = Σ (исходящий поток) │
    │                                                 │
    │  "Что пришло — то и ушло"                       │
    │  "Деньги не появляются из воздуха"              │
    └─────────────────────────────────────────────────┘

    SOURCE: только исходящий поток (производитель)
    SINK: только входящий поток (потребитель)

    Max Flow = Σ исходящего из SOURCE = Σ входящего в SINK
```

**Когда использовать:** Для проверки корректности. Если баланс не сходится — ошибка.

### Модель 4: Дуальность Max-Flow / Min-Cut

```
    ДВЕ СТОРОНЫ ОДНОЙ МЕДАЛИ

    ┌──────────────────────┐    ┌──────────────────────┐
    │      MAX FLOW        │ =  │       MIN CUT        │
    │                      │    │                      │
    │ "Максимум, что можно │    │ "Минимум, что нужно  │
    │  пропустить"         │    │  перерезать, чтобы   │
    │                      │    │  остановить поток"   │
    └──────────────────────┘    └──────────────────────┘

         ПРЯМАЯ ЗАДАЧА              ДВОЙСТВЕННАЯ

    Пример:
    Max flow = 15 единиц
    Значит, чтобы полностью заблокировать,
    нужно перерезать рёбра с суммой capacity = 15
```

**Когда использовать:** Для задач типа "минимальная стоимость разделения", "критические рёбра". Min-Cut часто имеет практический смысл.

### Модель 5: Слоёный торт Dinic

```
    LEVEL GRAPH = СЛОИ ТОРТА

    Уровень 0:    [SOURCE]
                     │
                     ▼
    Уровень 1:    [A] [B] [C]
                     │ ╲ │ / │
                     ▼  ╲▼/  ▼
    Уровень 2:    [D]  [E]  [F]
                      ╲  │  /
                       ╲ │ /
                        ▼▼▼
    Уровень 3:        [SINK]

    BLOCKING FLOW: Насыщаем ВСЕ пути в торте до дна!

    После каждой итерации:
    - Расстояние от SOURCE до SINK увеличивается
    - "Слоёв" становится больше
    - Но максимум V-1 итераций → O(V²E)
```

**Когда использовать:** Для понимания, почему Dinic быстрее. Каждая итерация делает "срез" торта толще.

### Сравнение ментальных моделей

| Модель | Лучше всего для | Ограничения |
|--------|-----------------|-------------|
| Жидкость | Интуиция, объяснения | Не объясняет обратные рёбра |
| Игра "толкай" | Понимание алгоритма | Может быть медленной (DFS) |
| Бухгалтерия | Проверка корректности | Абстрактна |
| Дуальность | Задачи min-cut, оптимизация | Требует доказательства |
| Слоёный торт | Dinic, оптимизация | Только для Dinic |

---

## Зачем это нужно?

**Проблема:**

```
Сеть труб от источника к стоку.
Каждая труба имеет пропускную способность.
Какой максимальный объём можно перекачать?
```

**Применения:**

| Задача | Редукция к flow |
|--------|-----------------|
| Bipartite matching | Max flow = max matching |
| Edge-disjoint paths | Capacity = 1 |
| Min vertex cover | Min cut |
| Project selection | Source/sink модель |

---

## Основные понятия

### Flow Network

```
G = (V, E) — ориентированный граф
s — source (исток)
t — sink (сток)
c(u,v) — capacity ребра (u,v)
f(u,v) — поток по ребру

Ограничения:
1. Capacity: 0 ≤ f(u,v) ≤ c(u,v)
2. Conservation: Σf(v,u) = Σf(u,w) для всех v ≠ s,t
   (что входит = что выходит)
```

### Residual Graph

```
Остаточная сеть Gf показывает "что ещё можно пустить":

Для ребра (u,v) с capacity c и flow f:
- cf(u,v) = c(u,v) - f(u,v)  (можем добавить)
- cf(v,u) = f(u,v)            (можем отменить)
```

### Augmenting Path

```
Путь от s к t в residual graph.
Если существует — поток не максимален!
```

---

## Ford-Fulkerson

### Идея

```
1. Пока существует augmenting path P в Gf:
   a. Найти bottleneck = min capacity на P
   b. Увеличить flow по P на bottleneck
   c. Обновить residual graph
2. Вернуть total flow
```

### Реализация (Kotlin)

```kotlin
/**
 * FORD-FULKERSON / EDMONDS-KARP — алгоритм максимального потока
 *
 * Идея: находим путь из source в sink, пропускаем поток,
 * повторяем пока есть пути.
 *
 * BFS вместо DFS (Edmonds-Karp) гарантирует O(VE²)
 */
class FordFulkerson(private val n: Int) {
    // capacity[u][v] = сколько ещё можно пропустить из u в v
    // Изначально = пропускная способность ребра
    // После пропуска потока — уменьшается
    private val capacity = Array(n) { IntArray(n) }
    private val adj = Array(n) { mutableListOf<Int>() }

    fun addEdge(from: Int, to: Int, cap: Int) {
        capacity[from][to] = cap
        adj[from].add(to)
        // ВАЖНО: добавляем ОБРАТНОЕ ребро!
        // Это нужно для residual graph — возможности "отменить" поток
        adj[to].add(from)
    }

    /**
     * BFS находит augmenting path (дополняющий путь)
     * Использование BFS вместо DFS = алгоритм Edmonds-Karp
     */
    private fun bfs(source: Int, sink: Int, parent: IntArray): Boolean {
        val visited = BooleanArray(n)
        val queue = ArrayDeque<Int>()

        queue.add(source)
        visited[source] = true

        while (queue.isNotEmpty()) {
            val u = queue.removeFirst()

            for (v in adj[u]) {
                // Ребро существует в residual graph если capacity > 0
                // capacity = 0 означает: пропускная способность исчерпана
                if (!visited[v] && capacity[u][v] > 0) {
                    visited[v] = true
                    parent[v] = u
                    if (v == sink) return true
                    queue.add(v)
                }
            }
        }

        return false
    }

    fun maxFlow(source: Int, sink: Int): Int {
        val parent = IntArray(n)
        var maxFlow = 0

        // Пока существует путь из source в sink
        while (bfs(source, sink, parent)) {
            // Находим BOTTLENECK — минимальную пропускную способность на пути
            var pathFlow = Int.MAX_VALUE
            var s = sink
            while (s != source) {
                pathFlow = minOf(pathFlow, capacity[parent[s]][s])
                s = parent[s]
            }

            // Обновляем RESIDUAL GRAPH:
            var v = sink
            while (v != source) {
                val u = parent[v]
                capacity[u][v] -= pathFlow  // Прямое ребро: уменьшаем capacity
                capacity[v][u] += pathFlow  // Обратное: увеличиваем (возможность отмены)
                v = parent[v]
            }

            maxFlow += pathFlow
        }

        return maxFlow
    }
}
```

### Сложность

- Ford-Fulkerson (DFS): O(E × max_flow) — может быть медленным
- **Edmonds-Karp (BFS): O(V × E²)**

---

## Dinic's Algorithm

### Идея

```
Улучшение: используем level graph + blocking flow

1. Построить level graph (BFS от s)
2. Найти blocking flow (DFS, saturating edges)
3. Повторять пока есть путь s→t

WHY быстрее?
Каждая итерация увеличивает distance s→t минимум на 1.
Максимум V-1 итераций.
```

### Реализация

```kotlin
/**
 * DINIC — быстрый алгоритм максимального потока O(V²E)
 *
 * Улучшение над Ford-Fulkerson:
 * 1. Строим LEVEL GRAPH (BFS) — каждая вершина имеет "уровень" от source
 * 2. Ищем BLOCKING FLOW (DFS) — насыщаем все пути в level graph
 * 3. Повторяем пока sink достижим
 *
 * Почему быстрее? Каждая итерация увеличивает расстояние s→t минимум на 1.
 */
class Dinic(private val n: Int) {
    data class Edge(val to: Int, var cap: Int, val rev: Int)

    private val graph = Array(n) { mutableListOf<Edge>() }
    private val level = IntArray(n)  // Уровень вершины от source
    private val iter = IntArray(n)   // Итератор для DFS (оптимизация)

    fun addEdge(from: Int, to: Int, cap: Int) {
        graph[from].add(Edge(to, cap, graph[to].size))
        // Обратное ребро с capacity=0 (для residual graph)
        // rev указывает на индекс прямого ребра в списке to
        graph[to].add(Edge(from, 0, graph[from].size - 1))
    }

    /**
     * BFS строит LEVEL GRAPH
     * level[v] = расстояние от source до v
     * Возвращает true если sink достижим
     */
    private fun bfs(s: Int, t: Int): Boolean {
        level.fill(-1)
        val queue = ArrayDeque<Int>()
        level[s] = 0
        queue.add(s)

        while (queue.isNotEmpty()) {
            val v = queue.removeFirst()
            for (e in graph[v]) {
                if (e.cap > 0 && level[e.to] < 0) {
                    level[e.to] = level[v] + 1
                    queue.add(e.to)
                }
            }
        }

        return level[t] >= 0
    }

    /**
     * DFS находит BLOCKING FLOW в level graph
     *
     * Blocking flow = поток, после которого нет пути s→t в level graph
     * (все пути "заблокированы" насыщенными рёбрами)
     */
    private fun dfs(v: Int, t: Int, f: Int): Int {
        if (v == t) return f

        while (iter[v] < graph[v].size) {
            val e = graph[v][iter[v]]
            // Идём ТОЛЬКО по level graph:
            // level[v] < level[e.to] гарантирует движение "вперёд"
            if (e.cap > 0 && level[v] < level[e.to]) {
                val d = dfs(e.to, t, minOf(f, e.cap))
                if (d > 0) {
                    e.cap -= d
                    graph[e.to][e.rev].cap += d
                    return d
                }
            }
            iter[v]++
        }

        return 0
    }

    fun maxFlow(s: Int, t: Int): Long {
        var flow = 0L

        while (bfs(s, t)) {
            iter.fill(0)
            var f: Int
            while (true) {
                f = dfs(s, t, Int.MAX_VALUE)
                if (f == 0) break
                flow += f
            }
        }

        return flow
    }
}
```

### Сложность

- General: **O(V² × E)**
- Unit capacity: O(E × √V)
- Bipartite matching: O(E × √V)

---

## Max-Flow Min-Cut Theorem

```
Максимальный поток = Минимальный разрез

Min-cut: минимальная сумма capacities рёбер,
         удаление которых отсоединяет s от t.

WHY равны?
- Flow ≤ Cut для любого cut (flow ограничен capacity)
- При max flow существует saturating cut
```

### Нахождение Min-Cut

```kotlin
/**
 * Нахождение MIN CUT после вычисления max flow
 *
 * Алгоритм:
 * 1. После max flow делаем BFS из source по рёбрам с capacity > 0
 * 2. visited вершины = S-сторона разреза
 * 3. Рёбра из visited в unvisited = минимальный разрез
 */
fun minCut(source: Int): List<Pair<Int, Int>> {
    // BFS находит все вершины, достижимые из source в residual graph
    val visited = BooleanArray(n)
    val queue = ArrayDeque<Int>()
    queue.add(source)
    visited[source] = true

    while (queue.isNotEmpty()) {
        val u = queue.removeFirst()
        for (e in graph[u]) {
            if (e.cap > 0 && !visited[e.to]) {
                visited[e.to] = true
                queue.add(e.to)
            }
        }
    }

    // Рёбра, пересекающие границу visited → unvisited
    // Это и есть минимальный разрез!
    // e.cap == 0 означает: ребро насыщено (весь поток через него)
    val cutEdges = mutableListOf<Pair<Int, Int>>()
    for (u in 0 until n) {
        if (visited[u]) {
            for (e in graph[u]) {
                if (!visited[e.to] && e.cap == 0) {
                    cutEdges.add(u to e.to)
                }
            }
        }
    }

    return cutEdges
}
```

---

## Bipartite Matching

```
Задача: Максимальное паросочетание в двудольном графе.

Редукция к max flow:
1. Добавить source s, соединить со всеми левыми вершинами (cap=1)
2. Добавить sink t, соединить все правые вершины с ним (cap=1)
3. Все рёбра графа имеют cap=1
4. Max flow = max matching
```

```kotlin
/**
 * МАКСИМАЛЬНОЕ ПАРОСОЧЕТАНИЕ через max flow
 *
 * Редукция: двудольный граф → flow network
 * - Source соединяется со всеми ЛЕВЫМИ вершинами (cap=1)
 * - Все ПРАВЫЕ вершины соединяются с sink (cap=1)
 * - Рёбра графа имеют cap=1
 *
 * Max flow = количество рёбер в максимальном паросочетании
 */
fun maxBipartiteMatching(left: Int, right: Int, edges: List<Pair<Int, Int>>): Int {
    val n = left + right + 2
    val source = 0
    val sink = n - 1

    val dinic = Dinic(n)

    // Source → все левые вершины (cap=1)
    // Каждая левая вершина может быть выбрана только один раз
    for (i in 1..left) {
        dinic.addEdge(source, i, 1)
    }

    // Все правые вершины → sink (cap=1)
    // Каждая правая вершина может быть выбрана только один раз
    for (i in left + 1 until sink) {
        dinic.addEdge(i, sink, 1)
    }

    // Рёбра двудольного графа (cap=1)
    for ((l, r) in edges) {
        dinic.addEdge(l, left + r, 1)
    }

    return dinic.maxFlow(source, sink).toInt()
}
```

---

## Практика

### LeetCode задачи

| # | Название | Сложность | Тема |
|---|----------|-----------|------|
| 785 | Is Graph Bipartite | Medium | Prereq |
| — | Maximum Bipartite Matching | — | Classic |
| — | Min Cut | — | Max-flow min-cut |

---

## Связанные темы

### Prerequisites
- [Graphs](../data-structures/graphs.md)
- BFS/DFS

### Unlocks
- Min-cost max-flow
- Matching algorithms
- Linear programming duality

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms: Max Flow](https://cp-algorithms.com/graph/edmonds_karp.html) | Reference | Edmonds-Karp |
| 2 | [CP-Algorithms: Dinic](https://cp-algorithms.com/graph/dinic.html) | Reference | Dinic |
| 3 | [CLRS] Introduction to Algorithms | Book | Theory |

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция Flow: водопровод/пробки/курьеры, 6 типичных ошибок включая обратные рёбра, 5 ментальных моделей включая дуальность Max-Flow/Min-Cut)*
