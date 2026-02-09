---
title: "Минимальное остовное дерево (MST)"
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
  - "[[union-find-pattern]]"
  - "[[greedy-algorithms]]"
---

# Minimum Spanning Tree (MST)

## TL;DR

MST — подграф, соединяющий все вершины с **минимальным суммарным весом** без циклов. **Kruskal** — сортировка рёбер + Union-Find за O(E log E), лучше для sparse. **Prim** — жадный рост от вершины за O(E log V), лучше для dense. **Boruvka** — параллелизуемый, O(E log V). Основа: Cut Property (min crossing edge in MST) и Cycle Property (max cycle edge not in MST).

---

## Часть 1: Интуиция без кода

### Аналогия 1: Прокладка электричества в деревне

```
Ты электрик. 6 домов нужно соединить проводами.
Провод стоит деньги — чем длиннее, тем дороже.
Каждый дом должен получить электричество.

Карта (числа = стоимость провода):

     A ────3──── B
    /│\         /│
   2 1 4       2 5
  /  │  \     /  │
 C───│───D───E───F
     3       1

Цель: соединить все дома МИНИМАЛЬНОЙ ценой

Плохой способ: соединить ВСЕХ со ВСЕМИ
  → Много лишних проводов, дорого!

Хороший способ (MST): ровно 5 проводов для 6 домов
  A─1─D, D─1─E, A─2─C, A─3─B, E─2─B → 9 единиц

  Получается "дерево" — нет лишних соединений!
```

**Ключевой инсайт:** Дерево из n вершин имеет ровно n-1 рёбер. Это минимум для связности и максимум без циклов.

---

### Аналогия 2: Жадный строитель (Kruskal)

```
Строитель сортирует все возможные дороги по цене
и строит их от дешёвой к дорогой:

Список дорог (отсортирован):
  1. A─D: 1 руб
  2. D─E: 1 руб
  3. A─C: 2 руб
  4. B─E: 2 руб
  5. A─B: 3 руб
  6. C─D: 3 руб
  7. A─E: 4 руб
  8. B─F: 5 руб

Процесс:
  Шаг 1: A─D за 1 руб → Строим! (A и D теперь связаны)
  Шаг 2: D─E за 1 руб → Строим! (теперь A-D-E связаны)
  Шаг 3: A─C за 2 руб → Строим! (C присоединился)
  Шаг 4: B─E за 2 руб → Строим! (B присоединился)
  Шаг 5: A─B за 3 руб → ПРОПУСКАЕМ! (A и B уже связаны через A-D-E-B)
  Шаг 6: C─D за 3 руб → ПРОПУСКАЕМ! (создаст цикл A-C-D-A)
  ...

  5 дорог построено → ВСЕ СВЯЗАНЫ → СТОП!
```

**Ключевой инсайт:** Берём дешёвое ребро, если оно НЕ создаёт цикл.

---

### Аналогия 3: Растущее дерево (Prim)

```
Садовник сажает дерево и растит его ветка за веткой:

Начинаем с семечки в точке A:
┌─────────────────────────────────┐
│  Итерация 1: Дерево = {A}       │
│  Варианты: A─B(3), A─C(2), A─D(1)│
│  Выбираем MIN: A─D(1)           │
│  Дерево = {A, D}                │
└─────────────────────────────────┘
      ↓
┌─────────────────────────────────┐
│  Итерация 2: Дерево = {A, D}    │
│  Варианты: A─B(3), A─C(2), D─E(1)│
│  Выбираем MIN: D─E(1)           │
│  Дерево = {A, D, E}             │
└─────────────────────────────────┘
      ↓
┌─────────────────────────────────┐
│  Итерация 3: Дерево = {A,D,E}   │
│  Варианты: A─B(3), A─C(2), E─B(2)│
│  Выбираем MIN: A─C(2) или E─B(2)│
│  Дерево = {A, D, E, C}          │
└─────────────────────────────────┘
      ...продолжаем пока все не в дереве
```

**Ключевой инсайт:** Растим дерево, каждый раз добавляя самое дешёвое ребро НАРУЖУ.

---

### Численный пример: Kruskal пошагово

```
Граф с 5 вершинами:

    0 ──4── 1
    │\      │\
    2  3    5  6
    │   \   │   \
    2 ──1── 3 ──2── 4

Рёбра: (вес, u, v)
  (1, 2, 3)
  (2, 0, 2)
  (2, 3, 4)
  (3, 0, 3)
  (4, 0, 1)
  (5, 1, 3)
  (6, 1, 4)

Сортируем по весу: (1,2,3), (2,0,2), (2,3,4), (3,0,3), (4,0,1), (5,1,3), (6,1,4)

Union-Find: parent = [0, 1, 2, 3, 4] (каждый сам себе)

Шаг 1: (1, 2, 3)
  find(2) = 2, find(3) = 3 → РАЗНЫЕ
  union(2, 3) → parent = [0, 1, 2, 2, 4]
  MST += 1

Шаг 2: (2, 0, 2)
  find(0) = 0, find(2) = 2 → РАЗНЫЕ
  union(0, 2) → parent = [0, 1, 0, 2, 4]
  MST += 2

Шаг 3: (2, 3, 4)
  find(3) = 2→0, find(4) = 4 → РАЗНЫЕ
  union(3, 4) → parent = [0, 1, 0, 2, 0]
  MST += 2

Шаг 4: (3, 0, 3)
  find(0) = 0, find(3) = 2→0 → ОДИНАКОВЫЕ!
  ПРОПУСКАЕМ (цикл!)

Шаг 5: (4, 0, 1)
  find(0) = 0, find(1) = 1 → РАЗНЫЕ
  union(0, 1) → parent = [0, 0, 0, 2, 0]
  MST += 4

4 ребра для 5 вершин → ГОТОВО!
MST вес = 1 + 2 + 2 + 4 = 9
```

---

### Cut Property — почему жадность работает

```
"Cut" — это разрез графа на две части

            S                    V - S
       ┌─────────┐          ┌─────────┐
       │    A    │────5─────│    D    │
       │         │          │         │
       │    B    │════2═════│    E    │  ← минимальное
       │         │          │         │      crossing edge
       │    C    │────7─────│    F    │
       └─────────┘          └─────────┘

ТЕОРЕМА: Минимальное ребро, пересекающее любой cut,
         ОБЯЗАТЕЛЬНО входит в какой-то MST!

Доказательство (от противного):
  Допустим, min edge (B-E, вес 2) НЕ в MST T.
  Тогда в T есть другой путь B → ... → E.
  Этот путь пересекает cut → есть другое crossing edge e'.
  weight(e') > 2 (т.к. B-E минимальное)

  Заменим e' на B-E:
  Новое дерево T' легче T → противоречие!
  Значит, B-E должно быть в MST. ∎
```

---

## Часть 2: Почему это сложно

### Типичные ошибки студентов

#### Ошибка 1: Забыли про несвязный граф

```kotlin
// ❌ НЕПРАВИЛЬНО — не проверяем, что MST построен полностью
fun kruskal(n: Int, edges: List<Edge>): Long {
    var totalWeight = 0L
    var edgeCount = 0
    // ... добавляем рёбра ...
    return totalWeight  // Может вернуть частичный вес!
}

// ✅ ПРАВИЛЬНО — проверяем количество рёбер в MST
fun kruskal(n: Int, edges: List<Edge>): Long? {
    var totalWeight = 0L
    var edgeCount = 0
    // ... добавляем рёбра ...
    if (edgeCount != n - 1) return null  // Граф не связный!
    return totalWeight
}

СИМПТОМ: Получаем MST меньшего размера, чем ожидалось
РЕШЕНИЕ: MST из n вершин ДОЛЖЕН иметь n-1 рёбер
```

#### Ошибка 2: Union-Find без Path Compression

```kotlin
// ❌ НЕПРАВИЛЬНО — O(n) на операцию в худшем случае
fun find(x: Int): Int {
    if (parent[x] != x) return find(parent[x])
    return x
}

// Для цепочки 0→1→2→...→n-1:
// find(n-1) = n операций!

// ✅ ПРАВИЛЬНО — Path Compression, O(α(n)) ≈ O(1)
fun find(x: Int): Int {
    if (parent[x] != x) {
        parent[x] = find(parent[x])  // Сжимаем путь!
    }
    return parent[x]
}

СИМПТОМ: TLE на больших графах
РЕШЕНИЕ: ВСЕГДА используй Path Compression
```

#### Ошибка 3: Prim с изолированной начальной вершиной

```kotlin
// ❌ НЕПРАВИЛЬНО — начинаем с вершины 0, но она может быть изолированной
fun prim(): Long {
    val start = 0  // Что если adj[0] пуст?
    // ... pq.add(0L to start) ...
}

// Если вершина 0 не имеет соседей, алгоритм "зависнет"

// ✅ ПРАВИЛЬНО — выбираем вершину с хотя бы одним соседом
fun prim(): Long {
    val start = (0 until n).firstOrNull { adj[it].isNotEmpty() }
        ?: return 0L  // Граф пуст
    // ...
}

СИМПТОМ: Неполный MST или бесконечный цикл
РЕШЕНИЕ: Проверяй начальную вершину
```

#### Ошибка 4: Путаница между Kruskal и Prim

```kotlin
// ❌ НЕПРАВИЛЬНО — пытаемся применить логику Prim в Kruskal
fun kruskal(...) {
    val visited = BooleanArray(n)  // Не нужно в Kruskal!
    for (edge in sortedEdges) {
        if (!visited[edge.u] || !visited[edge.v]) {  // НЕПРАВИЛЬНО!
            // ...
        }
    }
}

// Kruskal проверяет КОМПОНЕНТЫ через Union-Find
// Prim проверяет ПОСЕЩЁННОСТЬ вершин

// ✅ ПРАВИЛЬНО — используй Union-Find для Kruskal
fun kruskal(...) {
    for (edge in sortedEdges) {
        if (uf.find(edge.u) != uf.find(edge.v)) {  // Разные компоненты?
            uf.union(edge.u, edge.v)
            // ...
        }
    }
}

СИМПТОМ: Добавляются лишние рёбра или пропускаются нужные
РЕШЕНИЕ: Kruskal = Union-Find, Prim = visited set
```

#### Ошибка 5: Неправильная обработка "устаревших" рёбер в Prim

```kotlin
// ❌ НЕПРАВИЛЬНО — не проверяем, что вершина уже в MST
fun primLazy() {
    while (pq.isNotEmpty()) {
        val (weight, u, parent) = pq.poll()
        mstEdges.add(parent to u)  // Может добавить дубликат!
        totalWeight += weight
        // ...
    }
}

// В lazy Prim в куче могут быть несколько рёбер к одной вершине
// Нужно игнорировать все после первого

// ✅ ПРАВИЛЬНО — проверяем inMST
fun primLazy() {
    while (pq.isNotEmpty()) {
        val (weight, u, parent) = pq.poll()
        if (inMST[u]) continue  // Уже в MST — пропускаем!
        inMST[u] = true
        // ...
    }
}

СИМПТОМ: MST содержит циклы или лишние рёбра
РЕШЕНИЕ: В lazy Prim ВСЕГДА проверяй inMST перед добавлением
```

#### Ошибка 6: Kruskal vs Prim — неправильный выбор

```
Kruskal лучше когда:
- Граф SPARSE (мало рёбер): E ≈ V
- Рёбра уже даны списком
- Нужен список рёбер MST

Prim лучше когда:
- Граф DENSE (много рёбер): E ≈ V²
- Граф задан матрицей смежности
- Нужен только вес MST

❌ НЕПРАВИЛЬНО — Kruskal для полного графа
n = 1000, E = n(n-1)/2 ≈ 500,000
Сортировка: O(E log E) ≈ O(500,000 × 20) = 10^7

✅ ПРАВИЛЬНО — Prim для полного графа
Prim (eager): O(V²) = 10^6 — быстрее!
```

---

## Часть 3: Ментальные модели

### Модель 1: "Жадная сеть" (Kruskal)

```
Представь, что рёбра — это предложения от подрядчиков.
Каждый подрядчик предлагает построить одну дорогу.

Менеджер проекта:
1. Сортирует все предложения по цене
2. Принимает самое дешёвое, ЕСЛИ оно нужно
   (соединяет ещё не связанные районы)
3. Отклоняет, если дорога избыточна
   (районы уже связаны другими дорогами)

Union-Find = "карта районов"
- find(x) = какому району принадлежит город x?
- union(x, y) = районы x и y объединились
```

### Модель 2: "Растущий кристалл" (Prim)

```
MST как кристалл, который растёт из одной точки:

     ●  ← начальная "затравка"
    /|\
   ● ● ●  ← первый слой
  /|   |\
 ● ●   ● ●  ← второй слой
           ...

На каждом шаге:
- Смотрим на все рёбра от кристалла наружу
- Выбираем САМОЕ КОРОТКОЕ
- Присоединяем новый атом

PriorityQueue = "список кандидатов на присоединение"
inMST = "уже часть кристалла"
```

### Модель 3: "Cut Property как гарантия"

```
Почему жадность работает для MST?

Любой cut даёт ГАРАНТИЮ:
  "Минимальное crossing edge ОБЯЗАТЕЛЬНО в MST"

Kruskal использует это неявно:
  Когда берём min edge между двумя компонентами,
  это минимальное crossing edge для cut между ними!

Prim использует это явно:
  На каждом шаге есть cut: {MST} vs {остальные}
  Берём min crossing edge → гарантированно правильно!

Это как "сертификат качества" для каждого ребра
```

### Модель 4: "Spanning Tree = Skeleton"

```
Граф — это "тело" с множеством связей
MST — это "скелет", минимальная структура для целостности

     Полный граф:              MST (скелет):
        A                          A
       /|\\\                      /|
      B─C─D─E                    B C D E
       \|/|/                        \|/
        F─G                          F
                                      \
                                       G

Скелет сохраняет СВЯЗНОСТЬ, но убирает ИЗБЫТОЧНОСТЬ
n костей для n+1 сустава (n-1 рёбер для n вершин)
```

### Модель 5: "Greedy на уровне рёбер vs вершин"

```
Два способа думать о жадности:

KRUSKAL — жадность на уровне РЁБЕР:
  "Какое следующее ребро добавить?"
  Ответ: самое дешёвое из неиспользованных, не создающее цикл

PRIM — жадность на уровне ВЕРШИН:
  "Какую следующую вершину присоединить?"
  Ответ: ту, до которой самое дешёвое ребро из текущего дерева

Обе стратегии дают один и тот же (оптимальный) результат!
Это потому что обе опираются на Cut Property.
```

---

## Зачем это нужно?

**Проблема:**

```
Есть N городов, нужно соединить их дорогами.
Стоимость дороги между городами i и j = cost[i][j].
Найти минимальную стоимость, чтобы все города были связаны.

Полный граф: N(N-1)/2 рёбер
N = 1000 → ~500,000 рёбер

Перебор всех spanning trees? Их n^(n-2) (Cayley formula)
n = 10 → 100,000,000 деревьев

Нужен эффективный алгоритм!
```

**Реальные применения:**

| Область | Использование |
|---------|---------------|
| Телекоммуникации | Минимизация длины кабеля |
| Электросети | Оптимальная прокладка линий |
| Кластеризация | Single-linkage hierarchical clustering |
| TSP | Lower bound для решения |
| Network design | Избежание redundant connections |

---

## Что это такое?

### Для 5-летнего

```
Представь, что у тебя много домиков, которые нужно
соединить дорожками. Между любыми двумя домиками
можно построить дорожку, но каждая стоит по-разному.

Минимальное остовное дерево — это способ соединить
ВСЕ домики, потратив МЕНЬШЕ ВСЕГО денег на дорожки,
и при этом от любого домика можно дойти до любого!

Хитрость: никаких "лишних" дорожек — ровно столько,
сколько нужно, чтобы все были связаны.
```

### Формально

**Spanning Tree** графа G = (V, E):
- Подграф T = (V, E'), где E' ⊆ E
- T — дерево (связный, без циклов)
- T содержит все вершины V
- |E'| = |V| - 1

**Minimum Spanning Tree**:
- Spanning tree с минимальной суммой весов рёбер
- Может быть несколько MST с одинаковым весом

```
Граф:                     MST:
    1                       1
   /|\                     / \
  3 2 4                   3   2
 /  |  \                 /     \
4───5───6               4       5
  2   1                       1
                              |
                              6

Weight = 3+2+2+1+1 = 9 (минимум)
```

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Spanning Tree** | Дерево, покрывающее все вершины графа |
| **Cut** | Разбиение вершин на два множества S и V-S |
| **Crossing Edge** | Ребро с концами в разных частях cut |
| **Safe Edge** | Ребро, добавление которого не нарушает MST свойство |
| **Light Edge** | Минимальное ребро пересекающее cut |

---

## Как это работает?

### Cut Property (Blue Rule)

```
Для любого cut в графе:
Минимальное crossing edge ОБЯЗАТЕЛЬНО входит в какой-то MST.

Визуализация:
    S              V-S
┌───────┐      ┌───────┐
│ A ● ● │──5───│ ● D   │
│   ●   │══2═══│   ●   │  ← min edge (weight 2)
│ B     │──7───│     E │
└───────┘      └───────┘

Ребро с весом 2 ГАРАНТИРОВАННО в MST!
```

### Cycle Property (Red Rule)

```
Для любого цикла в графе:
Максимальное ребро цикла НЕ входит ни в какой MST.

Цикл: A─3─B─5─C─4─A
            ↑
         max = 5

Ребро B─C с весом 5 НЕ в MST!
```

### Почему это работает?

```
Cut Property доказательство (proof by contradiction):

Допустим, min crossing edge e = (u, v) НЕ в MST T.
T — spanning tree → есть путь u → v в T.
Путь пересекает cut → есть другое crossing edge e'.

T + e создаёт цикл.
Удаляем e' из цикла → новое spanning tree T'.
weight(e) < weight(e') → weight(T') < weight(T).
Противоречие: T был MST!

Следовательно, e должно быть в MST.
```

---

## Kruskal's Algorithm

### Идея

```
1. Сортируем все рёбра по весу
2. Берём рёбра по одному (от min к max)
3. Если ребро не создаёт цикл → добавляем в MST
4. Останавливаемся когда V-1 рёбер

WHY Union-Find?
Проверка цикла = "в одной ли компоненте u и v?"
Union-Find отвечает за O(α(n)) ≈ O(1)
```

### Визуализация

```
Рёбра отсортированы: (A,B,1), (B,C,2), (A,C,3), (C,D,4), (B,D,5)

Step 1: (A,B,1) — A и B в разных компонентах → ADD
        MST: A─B

Step 2: (B,C,2) — B и C в разных компонентах → ADD
        MST: A─B─C

Step 3: (A,C,3) — A и C В ОДНОЙ компоненте → SKIP (цикл!)

Step 4: (C,D,4) — C и D в разных компонентах → ADD
        MST: A─B─C─D

V-1 = 3 рёбер → DONE!
Total weight = 1+2+4 = 7
```

### Реализация (Kotlin)

```kotlin
class KruskalMST {
    data class Edge(val u: Int, val v: Int, val weight: Long): Comparable<Edge> {
        override fun compareTo(other: Edge) = weight.compareTo(other.weight)
    }

    /**
     * UNION-FIND (Disjoint Set Union)
     *
     * Две оптимизации делают операции почти O(1):
     * 1. Path Compression — при find сжимаем путь к корню
     * 2. Union by Rank — меньшее дерево подвешиваем под большее
     *
     * Амортизированная сложность: O(α(n)) ≈ O(1)
     * где α — обратная функция Аккермана (растёт ОЧЕНЬ медленно)
     */
    class UnionFind(private val n: Int) {
        private val parent = IntArray(n) { it }
        private val rank = IntArray(n) { 0 }

        /**
         * FIND с PATH COMPRESSION
         *
         * Без сжатия:           С сжатием:
         *       0                    0
         *       ↑               ↑  ↑  ↑  ↑
         *       1               1  2  3  4
         *       ↑
         *       2
         *       ↑
         *       3
         *       ↑
         *       4
         *
         * После find(4) все элементы указывают прямо на корень
         */
        fun find(x: Int): Int {
            if (parent[x] != x) {
                parent[x] = find(parent[x])  // Рекурсивное сжатие пути
            }
            return parent[x]
        }

        /**
         * UNION BY RANK
         *
         * Всегда подвешиваем меньшее дерево под большее
         * rank[x] ≈ log(размер поддерева x)
         *
         * Гарантирует: высота дерева ≤ log(n)
         */
        fun union(x: Int, y: Int): Boolean {
            val px = find(x)
            val py = find(y)

            // Уже в одной компоненте — цикл образуется!
            if (px == py) return false

            if (rank[px] < rank[py]) {
                parent[px] = py
            } else if (rank[px] > rank[py]) {
                parent[py] = px
            } else {
                parent[py] = px
                rank[px]++
            }
            return true
        }
    }

    /**
     * АЛГОРИТМ КРАСКАЛА
     *
     * Жадно добавляем рёбра от минимального к максимальному,
     * пропуская те, которые создают цикл
     */
    fun kruskal(n: Int, edges: List<Edge>): Pair<Long, List<Edge>> {
        // Сортировка рёбер — основной bottleneck: O(E log E)
        val sortedEdges = edges.sorted()
        val uf = UnionFind(n)
        val mstEdges = mutableListOf<Edge>()
        var totalWeight = 0L

        for (edge in sortedEdges) {
            /**
             * ПРОВЕРКА ЦИКЛА через Union-Find
             *
             * Если u и v в одной компоненте (find(u) == find(v)),
             * то добавление ребра (u,v) создаст цикл
             *
             * union() возвращает false, если уже в одной компоненте
             */
            if (uf.union(edge.u, edge.v)) {
                mstEdges.add(edge)
                totalWeight += edge.weight

                /**
                 * ОСТАНОВКА: MST имеет ровно V-1 рёбер
                 *
                 * Дерево с V вершинами всегда имеет V-1 рёбер
                 * Как только набрали V-1, MST построен
                 */
                if (mstEdges.size == n - 1) break
            }
        }

        return totalWeight to mstEdges
    }
}
```

### Сложность

| Операция | Время |
|----------|-------|
| Сортировка | O(E log E) |
| E операций Union-Find | O(E · α(V)) |
| **Итого** | **O(E log E)** ≈ **O(E log V)** |

---

## Prim's Algorithm

### Идея

```
1. Начинаем с любой вершины
2. Добавляем минимальное ребро, ведущее в новую вершину
3. Повторяем пока не покроем все вершины

WHY Priority Queue?
Нужно быстро находить минимальное ребро из текущего дерева.
Min-heap даёт O(log V) extract-min.
```

### Визуализация

```
Граф:
    A
   /|\
  2 1 4
 /  |  \
B───C───D
  3   5

Start from A:

Step 1: Выбираем min из {(A,B,2), (A,C,1), (A,D,4)}
        → (A,C,1)
        MST: A─C

Step 2: Выбираем min из {(A,B,2), (A,D,4), (C,B,3), (C,D,5)}
        → (A,B,2)
        MST: A─C, A─B

Step 3: Выбираем min из {(A,D,4), (C,D,5)}
        (C,B,3 не рассматриваем — B уже в MST)
        → (A,D,4)
        MST: A─C, A─B, A─D

All vertices covered → DONE!
Total weight = 1+2+4 = 7
```

### Реализация (Kotlin)

```kotlin
class PrimMST(private val n: Int) {
    data class Edge(val to: Int, val weight: Long)

    private val adj = Array(n) { mutableListOf<Edge>() }

    fun addEdge(u: Int, v: Int, weight: Long) {
        adj[u].add(Edge(v, weight))
        adj[v].add(Edge(u, weight))
    }

    /**
     * АЛГОРИТМ ПРИМА (Lazy версия)
     *
     * Растим дерево от начальной вершины, добавляя минимальное ребро,
     * ведущее к ещё не посещённой вершине
     */
    fun prim(start: Int = 0): Pair<Long, List<Pair<Int, Int>>> {
        /**
         * MIN-HEAP по весу ребра
         *
         * Храним (вес, вершина, родитель)
         * На каждом шаге извлекаем ребро с минимальным весом
         */
        val pq = PriorityQueue<Triple<Long, Int, Int>>(compareBy { it.first })
        val inMST = BooleanArray(n)
        val mstEdges = mutableListOf<Pair<Int, Int>>()
        var totalWeight = 0L

        // Начинаем с любой вершины (граф связный → результат один)
        pq.add(Triple(0L, start, -1))  // (weight, vertex, parent)

        while (pq.isNotEmpty() && mstEdges.size < n) {
            val (weight, u, parent) = pq.poll()

            /**
             * LAZY: в куче могут быть устаревшие рёбра
             *
             * Если вершина u уже в MST, это ребро неактуально
             * (было добавлено раньше, но другое ребро к u победило)
             */
            if (inMST[u]) continue

            inMST[u] = true
            totalWeight += weight
            if (parent != -1) {
                mstEdges.add(parent to u)
            }

            /**
             * РАСШИРЯЕМ ФРОНТИР
             *
             * Добавляем все рёбра от u к ещё не посещённым соседям
             * Heap выберет минимальное среди всех кандидатов
             */
            for ((v, w) in adj[u]) {
                if (!inMST[v]) {
                    pq.add(Triple(w, v, u))
                }
            }
        }

        return totalWeight to mstEdges
    }

    /**
     * АЛГОРИТМ ПРИМА (Eager версия)
     *
     * Отличие от Lazy: храним только ОДНО лучшее ребро к каждой вершине
     *
     * Преимущества:
     * - Меньше элементов в куче: O(V) вместо O(E)
     * - Меньше памяти
     * - Быстрее на dense графах
     */
    fun primEager(start: Int = 0): Long {
        val dist = LongArray(n) { Long.MAX_VALUE }
        val inMST = BooleanArray(n)
        var totalWeight = 0L

        /**
         * INDEXED PRIORITY QUEUE (упрощённая версия)
         *
         * Идеально: PQ с decrease-key за O(log n)
         * Здесь: просто добавляем новые записи, игнорируя устаревшие
         *
         * Для полной эффективности нужен IndexedMinPQ (Fibonacci heap → O(1) decrease-key)
         */
        val pq = PriorityQueue<Pair<Long, Int>>(compareBy { it.first })

        dist[start] = 0
        pq.add(0L to start)

        while (pq.isNotEmpty()) {
            val (d, u) = pq.poll()

            if (inMST[u]) continue
            inMST[u] = true
            totalWeight += d

            for ((v, w) in adj[u]) {
                /**
                 * RELAXATION: обновляем если нашли лучшее ребро
                 *
                 * dist[v] — вес минимального ребра из MST в v
                 * Если текущее ребро (u,v) легче → обновляем
                 *
                 * Аналогия с Dijkstra, но вместо расстояния от старта
                 * храним минимальный вес ребра к вершине
                 */
                if (!inMST[v] && w < dist[v]) {
                    dist[v] = w
                    pq.add(w to v)
                }
            }
        }

        return totalWeight
    }
}
```

### Сложность

| Версия | Время | Память |
|--------|-------|--------|
| Lazy (binary heap) | O(E log E) | O(E) |
| Eager (binary heap) | O(E log V) | O(V) |
| Fibonacci heap | O(E + V log V) | O(V) |

---

## Boruvka's Algorithm

### Идея

```
1. Каждая вершина — отдельная компонента
2. Для каждой компоненты находим min исходящее ребро
3. Добавляем все найденные рёбра
4. Компоненты сливаются
5. Повторяем пока не останется одна компонента

WHY параллелизуемый?
Шаг 2 можно выполнять параллельно для всех компонент!
```

### Визуализация

```
Round 1:
Компоненты: {A}, {B}, {C}, {D}

A: min edge = (A,B,1)
B: min edge = (A,B,1)
C: min edge = (C,B,2)
D: min edge = (D,C,3)

Добавляем: (A,B,1), (C,B,2), (D,C,3)
Компоненты: {A,B,C,D}

DONE! (одна компонента)
```

### Реализация (Kotlin)

```kotlin
class BoruvkaMST(private val n: Int) {
    data class Edge(val u: Int, val v: Int, val weight: Long)

    private val edges = mutableListOf<Edge>()

    fun addEdge(u: Int, v: Int, weight: Long) {
        edges.add(Edge(u, v, weight))
    }

    fun boruvka(): Long {
        val parent = IntArray(n) { it }
        val rank = IntArray(n) { 0 }

        fun find(x: Int): Int {
            if (parent[x] != x) parent[x] = find(parent[x])
            return parent[x]
        }

        fun union(x: Int, y: Int) {
            val px = find(x)
            val py = find(y)
            if (rank[px] < rank[py]) parent[px] = py
            else if (rank[px] > rank[py]) parent[py] = px
            else { parent[py] = px; rank[px]++ }
        }

        var totalWeight = 0L
        var numComponents = n

        /**
         * ГЛАВНЫЙ ЦИКЛ: O(log V) раундов
         *
         * Почему log V?
         * В каждом раунде каждая компонента сливается хотя бы с одной другой
         * → количество компонент уменьшается как минимум вдвое
         * → максимум log₂(V) раундов
         */
        while (numComponents > 1) {
            /**
             * cheapest[i] = индекс минимального ребра,
             *               выходящего из компоненты i
             *
             * -1 означает: пока не нашли ребра наружу
             */
            val cheapest = IntArray(n) { -1 }

            /**
             * ПАРАЛЛЕЛИЗУЕМЫЙ ШАГ!
             *
             * Для каждого ребра проверяем:
             * - Соединяет ли оно разные компоненты?
             * - Является ли оно минимальным для этих компонент?
             *
             * Каждое ребро можно обрабатывать независимо
             * → идеально для MapReduce / GPU
             */
            for ((idx, edge) in edges.withIndex()) {
                val compU = find(edge.u)
                val compV = find(edge.v)

                if (compU == compV) continue  // Внутри одной компоненты

                // Обновляем минимальное ребро для обеих компонент
                if (cheapest[compU] == -1 || edges[cheapest[compU]].weight > edge.weight) {
                    cheapest[compU] = idx
                }
                if (cheapest[compV] == -1 || edges[cheapest[compV]].weight > edge.weight) {
                    cheapest[compV] = idx
                }
            }

            // Добавляем все выбранные рёбра и сливаем компоненты
            for (i in 0 until n) {
                if (cheapest[i] != -1) {
                    val edge = edges[cheapest[i]]
                    val compU = find(edge.u)
                    val compV = find(edge.v)

                    if (compU != compV) {
                        union(compU, compV)
                        totalWeight += edge.weight
                        numComponents--
                    }
                }
            }
        }

        return totalWeight
    }
}
```

### Сложность

| Операция | Время |
|----------|-------|
| Раундов | O(log V) |
| На раунд | O(E) |
| **Итого** | **O(E log V)** |

---

## Second Best MST

### Идея

```
Second Best MST отличается от MST ровно на ОДНО ребро.

Алгоритм:
1. Строим MST
2. Для каждого НЕ-MST ребра (u,v):
   - Добавление создаёт цикл
   - Находим max ребро на пути u→v в MST
   - Разница = weight(u,v) - weight(max_on_path)
3. Выбираем замену с минимальной разницей
```

### Реализация с LCA (Kotlin)

```kotlin
class SecondBestMST(private val n: Int) {
    // ... Kruskal для построения MST ...

    /**
     * BINARY LIFTING для LCA и max edge на пути
     *
     * Ключевая идея: предвычисляем для каждой вершины:
     * - up[v][k] = 2^k-й предок v
     * - maxEdge[v][k] = максимальное ребро на пути к 2^k-му предку
     *
     * Это позволяет:
     * - Найти LCA за O(log n)
     * - Найти max edge на любом пути за O(log n)
     */
    private lateinit var up: Array<IntArray>
    private lateinit var maxEdge: Array<LongArray>
    private val LOG = 20

    fun preprocess(mstAdj: Array<MutableList<Pair<Int, Long>>>) {
        up = Array(n) { IntArray(LOG) { -1 } }
        maxEdge = Array(n) { LongArray(LOG) { 0 } }
        val depth = IntArray(n)

        /**
         * DFS для заполнения базы (k=0):
         * - up[v][0] = непосредственный родитель v
         * - maxEdge[v][0] = вес ребра к родителю
         */
        fun dfs(v: Int, p: Int, d: Int, edgeWeight: Long) {
            depth[v] = d
            up[v][0] = p
            maxEdge[v][0] = edgeWeight

            for ((u, w) in mstAdj[v]) {
                if (u != p) {
                    dfs(u, v, d + 1, w)
                }
            }
        }

        dfs(0, -1, 0, 0)

        /**
         * BINARY LIFTING — заполняем up[v][k] и maxEdge[v][k]
         *
         * Рекуррентное соотношение:
         * up[v][k] = up[up[v][k-1]][k-1]
         *          = 2^(k-1) + 2^(k-1) = 2^k шагов вверх
         *
         * maxEdge[v][k] = max(maxEdge[v][k-1], maxEdge[up[v][k-1]][k-1])
         *               = max на первой половине пути ∪ max на второй половине
         */
        for (k in 1 until LOG) {
            for (v in 0 until n) {
                if (up[v][k - 1] != -1) {
                    up[v][k] = up[up[v][k - 1]][k - 1]
                    maxEdge[v][k] = maxOf(
                        maxEdge[v][k - 1],
                        maxEdge[up[v][k - 1]][k - 1]
                    )
                }
            }
        }
    }

    /**
     * MAX EDGE НА ПУТИ u → v за O(log n)
     *
     * Алгоритм:
     * 1. Поднимаем u и v до одного уровня, собирая max
     * 2. Поднимаем обоих до LCA, собирая max
     * 3. Возвращаем общий max
     */
    fun maxOnPath(u: Int, v: Int): Long {
        // ... LCA + max edge calculation ...
        var a = u
        var b = v
        var maxE = 0L

        // Поднимаем до одной глубины, собирая max
        // Затем поднимаем обоих до LCA

        return maxE
    }

    fun findSecondBestMST(edges: List<Edge>, mstWeight: Long): Long {
        var minIncrease = Long.MAX_VALUE

        for (edge in edges) {
            if (!edge.inMST) {
                val maxInPath = maxOnPath(edge.u, edge.v)
                val increase = edge.weight - maxInPath
                minIncrease = minOf(minIncrease, increase)
            }
        }

        return mstWeight + minIncrease
    }
}
```

### Сложность

| Операция | Время |
|----------|-------|
| Построение MST | O(E log E) |
| Preprocessing LCA | O(V log V) |
| Проверка non-MST edges | O(E log V) |
| **Итого** | **O(E log V)** |

---

## Сравнение алгоритмов

| Критерий | Kruskal | Prim | Boruvka |
|----------|---------|------|---------|
| **Лучше для** | Sparse | Dense | Parallel |
| **Время** | O(E log E) | O(E log V) | O(E log V) |
| **Структура** | Union-Find | PQ | Union-Find |
| **Disconnected** | ✓ (forest) | ✗ | ✗ |
| **Параллелизм** | Сложно | Средне | Отлично |

### Когда какой использовать?

```
E < V log V (sparse)     → Kruskal
E ≈ V² (dense)           → Prim
Multi-core / distributed → Boruvka
Need MST edges           → Kruskal (естественно даёт список)
Only need weight         → Prim eager
```

---

## Распространённые ошибки

### 1. Забыть про несвязный граф

```kotlin
// ❌ НЕПРАВИЛЬНО: не проверяем связность
fun kruskal(...): Long {
    // ... добавляем рёбра ...
    return totalWeight  // Может быть MST forest, не tree!
}

// ✅ ПРАВИЛЬНО: проверяем количество рёбер
fun kruskal(...): Long? {
    // ... добавляем рёбра ...
    if (mstEdges.size != n - 1) return null  // Не связный!
    return totalWeight
}
```

### 2. Неправильный Union-Find

```kotlin
// ❌ НЕПРАВИЛЬНО: без path compression
fun find(x: Int): Int {
    if (parent[x] != x) return find(parent[x])  // O(n) worst case!
    return x
}

// ✅ ПРАВИЛЬНО: с path compression
fun find(x: Int): Int {
    if (parent[x] != x) parent[x] = find(parent[x])  // O(α(n))
    return parent[x]
}
```

### 3. Prim с неправильной начальной вершиной

```kotlin
// ❌ НЕПРАВИЛЬНО: hardcoded vertex 0
fun prim() = primFrom(0)  // Что если 0 изолирована?

// ✅ ПРАВИЛЬНО: проверка или выбор неизолированной
fun prim(): Long {
    val start = (0 until n).firstOrNull { adj[it].isNotEmpty() } ?: return 0
    return primFrom(start)
}
```

---

## Практика

### Концептуальные вопросы

1. **Может ли быть несколько MST?**

   Да, если есть рёбра с одинаковым весом. Все MST имеют одинаковый total weight.

2. **Почему Kruskal лучше для sparse графов?**

   Сортировка O(E log E) дешевле когда E мало. Prim всегда делает V extract-min операций.

3. **Как найти MST с ограничением на degree?**

   NP-hard в общем случае. Для degree ≤ 2: это задача о кратчайшем гамильтоновом пути.

### LeetCode задачи

| # | Название | Сложность | Паттерн |
|---|----------|-----------|---------|
| 1135 | Connecting Cities With Minimum Cost | Medium | Kruskal/Prim |
| 1584 | Min Cost to Connect All Points | Medium | Prim (dense) |
| 1168 | Optimize Water Distribution | Hard | Virtual node + MST |
| 1489 | Find Critical and Pseudo-Critical Edges | Hard | MST properties |
| 1697 | Checking Existence of Edge Length Limited Paths | Hard | Offline + MST |

---

## Связанные темы

### Prerequisites
- [Graphs](../data-structures/graphs.md)
- [Union-Find Pattern](../patterns/union-find-pattern.md)
- Greedy algorithms

### Unlocks
- [Graph Advanced](./graph-advanced.md)
- Network Flow (cuts and flows duality)
- Approximation algorithms (TSP)

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms: Kruskal](https://cp-algorithms.com/graph/mst_kruskal_with_dsu.html) | Reference | Implementation |
| 2 | [CP-Algorithms: Prim](https://cp-algorithms.com/graph/mst_prim.html) | Reference | Implementation |
| 3 | [Princeton: MST](https://algs4.cs.princeton.edu/43mst/) | Course | Theory |
| 4 | [CP-Algorithms: Second Best MST](https://cp-algorithms.com/graph/second_best_mst.html) | Reference | Advanced |
| 5 | [Baeldung: Boruvka](https://www.baeldung.com/java-boruvka-algorithm) | Tutorial | Parallel MST |

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция MST: электрика деревни/жадный строитель Kruskal/растущее дерево Prim, 6 типичных ошибок, 5 ментальных моделей)*
