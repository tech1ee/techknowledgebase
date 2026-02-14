---
title: "Паттерны DFS и BFS"
created: 2025-12-29
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - graph-traversal
  - shortest-path-unweighted
  - cycle-detection
  - connected-components
  - topological-ordering
  - level-order-processing
prerequisites:
  - "[[graphs]]"
  - "[[trees-binary]]"
  - "[[stacks-queues]]"
  - "[[recursion-fundamentals]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - pattern
  - interview
related:
  - "[[topological-sort-pattern]]"
  - "[[union-find-pattern]]"
  - "[[backtracking]]"
reading_time: 75
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# DFS & BFS Patterns

## TL;DR

DFS и BFS — два фундаментальных обхода, покрывающих **~25% задач на интервью**. **BFS**: level-order, shortest path в невзвешенных графах (Queue). **DFS**: полный обход, cycle detection, path finding (Stack/Recursion). Шесть traversals деревьев: preorder, inorder, postorder (DFS) + level-order (BFS). Multi-source BFS для распространения.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Исследование лабиринта (DFS)

> "Imagine a maze with only one entrance and one exit. You are at the entrance and want to explore the maze to reach the exit. Obviously you cannot split yourself into more than one." — [CS 225 UIUC](https://courses.grainger.illinois.edu/cs225/sp2025/resources/bfs-dfs/)

```
DFS = исследователь лабиринта с ниткой

                    ВХОД
                      │
            ┌─────────┼─────────┐
            │         │         │
           [A]       [B]       [C]
            │         │
       ┌────┴────┐    │
      [D]       [E]  [F]
       │              │
      ТУПИК         ВЫХОД

Стратегия исследователя (DFS):
1. Иди по ОДНОМУ пути до конца (разматывай нитку)
2. Уткнулся в тупик? ВЕРНИСЬ (сматывай нитку)
3. Попробуй следующий путь

Маршрут: ВХОД → A → D → ТУПИК ↩ → E → ↩ A ↩ → B → F → ВЫХОД!

ВАЖНО: Нашёл выход, но это НЕ ОБЯЗАТЕЛЬНО кратчайший путь!
```

### Аналогия 2: Волна от камня в воде (BFS)

> "In the 'waterfront' analogy, imagine white nodes being dry areas, gray nodes being the waterfront, and black areas being completely submerged." — [OpenDSA](https://opendsa-server.cs.vt.edu/ODSA/Books/Everything/html/GraphTraversal.html)

```
BFS = волна от камня, брошенного в воду

Бросаем камень (старт):
                    ●
                   💧
Волна 0:          [S]        ← точка удара
                  / | \
Волна 1:        [A][B][C]    ← первый круг волны
                /     \
Волна 2:      [D]     [E]    ← второй круг волны
               |
Волна 3:      [F]            ← третий круг


Если E — это цель:
  Достигнута на Волне 2 = расстояние 2

КЛЮЧЕВОЕ СВОЙСТВО:
Волна не может "перепрыгнуть" — сначала ВСЕ на расстоянии 1,
потом ВСЕ на расстоянии 2, и т.д.

→ BFS ГАРАНТИРУЕТ кратчайший путь в невзвешенном графе!
```

### Аналогия 3: Социальная сеть (друзья друзей)

```
Задача: найти кратчайшую цепочку знакомств от Вас до Илона Маска

           ВЫ
          / | \
      Друг Друг Друг        ← 1 рукопожатие
       |     |     |
     Друзья друзей           ← 2 рукопожатия
           ...
     Илон Маск               ← N рукопожатий

DFS: Пойдёт вглубь одной цепочки друзей до конца
     Может найти путь через 100 человек, хотя есть путь через 5

BFS: Сначала проверит ВСЕХ ваших прямых друзей (уровень 1)
     Потом ВСЕХ друзей друзей (уровень 2)
     Первое найденное = МИНИМАЛЬНОЕ число рукопожатий

Это называется "Six Degrees of Separation" (6 рукопожатий)
```

### Визуальное сравнение: Как они "видят" граф

```
         1
        /|\
       2 3 4
      /|   |
     5 6   7

DFS "видит" как ДЕРЕВО ПУТЕЙ:
  1 → 2 → 5 (тупик, назад)
  1 → 2 → 6 (тупик, назад)
  1 → 3 (тупик, назад)
  1 → 4 → 7 (тупик, назад)

BFS "видит" как КРУГИ РАССТОЯНИЙ:
  Круг 0: {1}           ← расстояние 0
  Круг 1: {2, 3, 4}     ← расстояние 1
  Круг 2: {5, 6, 7}     ← расстояние 2
```

---

## Часть 2: Почему DFS/BFS сложные (типичные ошибки)

### Ошибка 1: Использовали DFS для кратчайшего пути

> "Using DFS when shortest path is needed will not work. Once we have found the target we are not sure if it is at the shortest distance." — [LeetCode Discuss](https://leetcode.com/discuss/study-guide/1072548/A-Beginners-guid-to-BFS-and-DFS/)

```
Граф:   A ───────────────── D
        │                   │
        B ─── C ─────────────

Кратчайший путь A → D?
Ответ: A → D (1 ребро)

❌ DFS может найти: A → B → C → D (3 ребра)
   Это ПЕРВЫЙ найденный путь, но не кратчайший!

✅ BFS найдёт: A → D (1 ребро) — ГАРАНТИРОВАННО
   Потому что проверит всех соседей A до перехода глубже
```

### Ошибка 2: Пометили visited ПОСЛЕ извлечения из очереди

```
❌ НЕПРАВИЛЬНО (дубликаты в очереди):

   A ─── B
   │     │
   C ─── D

   Очередь: [A]
   Извлекли A, добавили соседей: [B, C]
   Извлекли B, добавили D: [C, D]
   Извлекли C, D ещё не visited, добавили D: [D, D] ← D ДВАЖДЫ!

✅ ПРАВИЛЬНО (visited при добавлении):

   Добавили A, visited = {A}
   Извлекли A, добавили B,C, visited = {A,B,C}
   Извлекли B, D не в visited, добавили D, visited = {A,B,C,D}
   Извлекли C, D уже в visited → НЕ добавляем
   Очередь: [D] — только один раз!
```

### Ошибка 3: Не различают "visiting" и "visited" (cycle detection)

```
Граф зависимостей: A → B → C → A (цикл!)

❌ НЕПРАВИЛЬНО (только visited):
   visited = {}
   Проверяем A: добавили в visited
   Проверяем B: добавили в visited
   Проверяем C: добавили в visited
   C указывает на A, A в visited → "цикл?"

   НО ЭТО МОЖЕТ БЫТЬ ПРОСТО ПЕРЕСЕЧЕНИЕ ПУТЕЙ, не цикл!

✅ ПРАВИЛЬНО (три состояния):
   WHITE (0) = не посещён
   GRAY  (1) = в процессе (на текущем пути рекурсии)
   BLACK (2) = полностью обработан

   Visiting A (GRAY): A → B (GRAY) → C (GRAY) → A уже GRAY!
   GRAY → GRAY = back edge = ЦИКЛ!

   Если бы A был BLACK — это безопасно, просто пересечение
```

### Ошибка 4: Забыли backtrack в DFS (Word Search)

```
Задача: найти слово "CAT" в сетке

   C A T
   X Y Z

❌ НЕПРАВИЛЬНО (без backtrack):
   Ищем C (0,0) → нашли
   Пометили (0,0) как '#'
   Ищем A (0,1) → нашли
   Пометили (0,1) как '#'
   Ищем T (0,2) → нашли!

   Теперь ищем "CAR":
   Ищем C (0,0) → там '#', не нашли!
   Ошибка: сетка испорчена предыдущим поиском

✅ ПРАВИЛЬНО (с backtrack):
   temp = grid[r][c]
   grid[r][c] = '#'
   // ... поиск ...
   grid[r][c] = temp  // ВОССТАНОВИЛИ!
```

### Ошибка 5: StackOverflow при глубокой рекурсии

```
Длинная цепочка: 0 → 1 → 2 → ... → 50000

❌ Рекурсивный DFS:
   dfs(0) вызывает
     dfs(1) вызывает
       dfs(2) вызывает
         ... 50000 вложенных вызовов ...

   ⚠️ StackOverflowError!
   JVM stack ограничен (~10 MB)

✅ Итеративный DFS с явным стеком:
   Stack использует heap (гигабайты)
   Нет ограничения на глубину
```

### Ошибка 6: Не обработали несвязный граф

```
Несвязный граф (два "острова"):

   A ─ B         E ─ F
   │   │         │
   C ─ D         G

❌ НЕПРАВИЛЬНО:
   bfs(A) → посетит {A,B,C,D}
   E, F, G — НЕ ПОСЕЩЕНЫ!
   "Найдено 1 компонента" — НЕПРАВИЛЬНО

✅ ПРАВИЛЬНО:
   for vertex in all_vertices:
       if vertex not in visited:
           bfs(vertex)  // новая компонента!

   "Найдено 2 компоненты" — ПРАВИЛЬНО
```

---

## Часть 3: Ментальные модели

### Модель 1: Структура данных определяет поведение

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   DFS = Stack (LIFO)          BFS = Queue (FIFO)            │
│                                                             │
│   Последний вошёл →           Первый вошёл →                │
│   Первый вышел                Первый вышел                  │
│                                                             │
│   ┌───┐                       ┌───┬───┬───┬───┐             │
│   │ C │ ← top                 │ A │ B │ C │ D │             │
│   │ B │                       └───┴───┴───┴───┘             │
│   │ A │                       ↑               ↑             │
│   └───┘                      out             in             │
│                                                             │
│   Добавляем: A, B, C          Добавляем: A, B, C, D         │
│   Извлекаем: C, B, A          Извлекаем: A, B, C, D         │
│              (обратный!)                  (прямой!)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

ЗАПОМНИ: Одна строчка меняет алгоритм!
  stack.removeLast()  → DFS
  queue.removeFirst() → BFS
```

**Когда использовать:** При написании кода — выбор структуры данных автоматически определяет тип обхода.

### Модель 2: DFS — рекурсивное мышление

```
"Чтобы обработать эту вершину, мне нужно сначала
обработать все вершины в её поддереве"

        f(1)
        /|\
       / | \
   f(2) f(3) f(4)     f(1) вызывает f(2), f(3), f(4)
    |         |
   f(5)      f(6)     f(2) вызывает f(5)
                      f(4) вызывает f(6)

Call Stack во время выполнения:
[f(1)]                     → начали с 1
[f(1), f(2)]               → вошли в 2
[f(1), f(2), f(5)]         → вошли в 5
[f(1), f(2)]               → вернулись из 5
[f(1)]                     → вернулись из 2
[f(1), f(3)]               → вошли в 3
...

DFS = естественный порядок рекурсии!
```

**Когда использовать:** Для понимания, почему DFS и рекурсия связаны, и почему postorder = обработка после возврата из детей.

### Модель 3: BFS — уровни расстояния

```
"BFS организует граф по расстоянию от источника"

                    ИСТОЧНИК (расстояние 0)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   Расстояние 1    Расстояние 1    Расстояние 1
        │                │
   ┌────┴────┐      ┌────┴────┐
   │         │      │         │
Расст. 2  Расст. 2  Расст. 2  Расст. 2


BFS = одновременный обход всех вершин на расстоянии d,
      перед переходом к расстоянию d+1

Следствие: ПЕРВОЕ достижение вершины = МИНИМАЛЬНОЕ расстояние
```

**Когда использовать:** При решении задач на кратчайший путь или "минимальное количество шагов".

### Модель 4: Multi-source BFS — параллельные волны

```
Задача: от каждой точки найти расстояние до ближайшего источника

Источники: S1, S2

   S1 ─ A ─ B ─ C ─ D ─ S2

❌ Single-source BFS (от S1):
   Расстояние D до S1 = 4

❌ Single-source BFS (от S2):
   Расстояние D до S2 = 1

✅ Multi-source BFS (от S1 И S2 одновременно):

Время 0:  S1 ─ A ─ B ─ C ─ D ─ S2
          [0]               [0]     ← Обе волны стартуют

Время 1:  S1 ─ A ─ B ─ C ─ D ─ S2
          [0] [1]         [1] [0]   ← Волны расходятся

Время 2:  S1 ─ A ─ B ─ C ─ D ─ S2
          [0] [1] [2] [2] [1] [0]   ← Волны встретились!

Каждая клетка получает расстояние до БЛИЖАЙШЕГО источника!
```

**Когда использовать:** Rotting Oranges, Walls and Gates, 01-Matrix — все multi-source задачи.

### Модель 5: Выбор по типу задачи

```
┌────────────────────────────────────────────────────────────┐
│                    DECISION TREE                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   Задача на граф/дерево?                                   │
│          │                                                 │
│   ┌──────┴──────┐                                          │
│   │             │                                          │
│  "Кратчайший"  "Любой путь"                                │
│  "Минимум"     "Все пути"                                  │
│  "Ближайший"   "Существует ли"                             │
│   │             │                                          │
│   ↓             ↓                                          │
│  BFS           DFS                                         │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  КОНКРЕТНЫЕ ПАТТЕРНЫ:                                      │
│                                                            │
│  BFS:                      DFS:                            │
│  • Shortest path           • Path exists                   │
│  • Minimum steps           • All paths                     │
│  • Level-order             • Cycle detection               │
│  • Nearest X               • Topological sort              │
│  • Multi-source spread     • Backtracking                  │
│  • 0-1 BFS                 • Connected components          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Когда использовать:** При первом чтении задачи — ключевые слова подсказывают алгоритм.

---

## Зачем это нужно?

**Реальная проблема:**

Лабиринт 100×100. Нужно найти кратчайший путь от входа до выхода.

DFS может найти путь, но не гарантирует кратчайший — обойдёт весь лабиринт.
BFS найдёт кратчайший путь сразу — первый раз достигнув выхода.

**Где используется:**

| Область | DFS | BFS |
|---------|-----|-----|
| Соцсети | Все связи человека | Степени разделения (6 degrees) |
| Карты | Проверка достижимости | Кратчайший маршрут |
| Компиляторы | Dependency resolution | Parallel build order |
| AI/Games | Minimax, game tree | A* pathfinding основа |
| Веб | Crawler deep dive | Site map по уровням |
| Биоинформатика | Protein folding | Sequence alignment |

**Статистика:**
- ~25% задач LeetCode решаются через DFS/BFS
- Number of Islands (#200) — топ-3 по частоте на интервью
- BFS обязателен для shortest path в невзвешенных графах

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Графы** | DFS/BFS — алгоритмы обхода графов | [[graphs]] |
| **Деревья** | Tree traversals — частный случай DFS/BFS | [[trees]] |
| **Стек и очередь** | DFS = Stack, BFS = Queue | [[stacks-queues]] |
| **Рекурсия** | Рекурсивный DFS = implicit stack | [[recursion-fundamentals]] |
| **CS: Adjacency List/Matrix** | Способы представления графов | Теория графов |
| **CS: Visited Set** | Предотвращение бесконечных циклов | Обход структур данных |

---

## Что это такое?

### Объяснение для 5-летнего

**DFS (Depth-First Search)**: Представь, что ты в лабиринте. Ты идёшь по одному пути до тупика, потом возвращаешься и пробуешь другой путь.

```
Старт → 1 → 2 → ТУПИК
             ↩ возврат
        1 → 3 → 4 → ВЫХОД!
```

**BFS (Breadth-First Search)**: Представь, что ты бросил камень в воду. Волны расходятся кругами — сначала ближние, потом дальние.

```
        2
       ↗
Старт → 1 → 3    (уровень 1: все на расстоянии 1)
       ↘
        4
```

### Формальное определение

**DFS (Depth-First Search)** — алгоритм обхода, который исследует ветвь до максимальной глубины перед откатом и исследованием следующей ветви.

**BFS (Breadth-First Search)** — алгоритм обхода, который исследует все вершины на текущем уровне (расстоянии) перед переходом на следующий уровень.

**Ключевые различия:**

| Характеристика | DFS | BFS |
|---------------|-----|-----|
| Структура данных | Stack (или рекурсия) | Queue |
| Порядок обхода | Вглубь | По уровням |
| Память | O(h) высота | O(w) ширина уровня |
| Shortest path | Не гарантирует | Гарантирует (невзвешенный) |
| Полнота | Да (конечные графы) | Да |

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **Visited** | Множество посещённых вершин | `Set<Node>` |
| **Frontier** | Вершины для следующего посещения | Stack (DFS) / Queue (BFS) |
| **Level** | Расстояние от источника (BFS) | Level 0 = source |
| **Back Edge** | Ребро к предку (указывает на цикл) | В DFS traversal |
| **Tree Edge** | Ребро к новой вершине | Часть DFS-дерева |
| **Connected Component** | Максимальное связное подмножество | Острова в сетке |
| **Preorder** | Root → Left → Right | DFS traversal |
| **Inorder** | Left → Root → Right | BST sorted order |
| **Postorder** | Left → Right → Root | Delete tree |
| **Level-order** | Уровень за уровнем | BFS traversal |

---

## Как это работает?

### DFS на дереве (три варианта)

```
        1
       / \
      2   3
     / \   \
    4   5   6

PREORDER (Root, Left, Right): 1 → 2 → 4 → 5 → 3 → 6
- Обрабатываем узел ДО детей
- Используется: копирование дерева, сериализация

INORDER (Left, Root, Right): 4 → 2 → 5 → 1 → 3 → 6
- Обрабатываем узел МЕЖДУ детьми
- Используется: BST в отсортированном порядке

POSTORDER (Left, Right, Root): 4 → 5 → 2 → 6 → 3 → 1
- Обрабатываем узел ПОСЛЕ детей
- Используется: удаление дерева, вычисление высоты
```

### BFS на дереве (Level-order)

```
        1           Level 0
       / \
      2   3         Level 1
     / \   \
    4   5   6       Level 2

Level-order: [1] → [2, 3] → [4, 5, 6]

Queue эволюция:
  [1]           → обработали 1, добавили 2, 3
  [2, 3]        → обработали 2, добавили 4, 5
  [3, 4, 5]     → обработали 3, добавили 6
  [4, 5, 6]     → обработали 4, 5, 6
  []            → ГОТОВО!
```

### DFS на графе (с visited)

```
Graph:
    0 — 1
    |   |
    2 — 3

DFS от 0:
  Stack: [0], Visited: {}
  Pop 0, push neighbors → Stack: [1, 2], Visited: {0}
  Pop 2, push unvisited → Stack: [1, 3], Visited: {0, 2}
  Pop 3, push unvisited → Stack: [1], Visited: {0, 2, 3}
  Pop 1, already visited neighbors → Stack: [], Visited: {0, 2, 3, 1}

DFS Order: 0 → 2 → 3 → 1
```

### BFS для Shortest Path

```
Find shortest path from 0 to 5:

    0 — 1 — 4
    |   |
    2 — 3 — 5

BFS:
  Level 0: [0]
  Level 1: [1, 2]      (соседи 0)
  Level 2: [3, 4]      (соседи 1, 2 без посещённых)
  Level 3: [5]         (соседи 3 без посещённых) ← НАЙДЕНО!

Shortest path length = 3 (уровень где нашли)
Path: 0 → 2 → 3 → 5 или 0 → 1 → 3 → 5
```

### Multi-source BFS (Rotting Oranges)

```
Grid:
  [2, 1, 1]    2 = rotten, 1 = fresh, 0 = empty
  [1, 1, 0]
  [0, 1, 1]

Minute 0: Queue = [(0,0)]  — все изначально гнилые
Minute 1: (0,1), (1,0) гниют → Queue = [(0,1), (1,0)]
Minute 2: (0,2), (1,1) гниют → Queue = [(0,2), (1,1)]
Minute 3: (2,1) гниёт → Queue = [(2,1)]
Minute 4: (2,2) гниёт → Queue = [(2,2)]

Answer: 4 минуты
```

---

## Сложность операций

| Алгоритм | Время | Память | Комментарий |
|----------|-------|--------|-------------|
| DFS (дерево) | O(n) | O(h) | h = высота дерева |
| DFS (граф) | O(V + E) | O(V) | V вершин, E рёбер |
| BFS (дерево) | O(n) | O(w) | w = макс. ширина уровня |
| BFS (граф) | O(V + E) | O(V) | Для очереди + visited |
| BFS (сетка) | O(m × n) | O(m × n) | m строк, n столбцов |

**Почему O(V + E)?**

```
Каждая вершина посещается 1 раз: O(V)
Каждое ребро проверяется 1 раз: O(E)
Суммарно: O(V + E)

Для сетки m × n:
  V = m × n (клетки)
  E ≤ 4 × m × n (до 4 соседей у клетки)
  O(m × n)
```

---

## Реализация

### Kotlin

```kotlin
// ═══════════════════════════════════════════════════════════════════════════
// DFS: TREE TRAVERSALS
// ═══════════════════════════════════════════════════════════════════════════

class TreeNode(var `val`: Int) {
    var left: TreeNode? = null
    var right: TreeNode? = null
}

/**
 * PREORDER: Root → Left → Right
 *
 * Обрабатываем узел ДО детей
 *
 * ПРИМЕНЕНИЕ:
 * - Копирование дерева (сначала создаём узел, потом детей)
 * - Сериализация (JSON, XML)
 * - Prefix expression (польская нотация)
 *
 * ПРИМЕР:
 * ```
 *     1
 *    / \
 *   2   3    → Preorder: [1, 2, 4, 5, 3, 6]
 *  / \   \
 * 4   5   6
 * ```
 */
fun preorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun dfs(node: TreeNode?) {
        if (node == null) return
        result.add(node.`val`)  // Обрабатываем ДО рекурсивных вызовов
        dfs(node.left)          // Потом левое поддерево
        dfs(node.right)         // Потом правое поддерево
    }

    dfs(root)
    return result
}

/**
 * INORDER: Left → Root → Right
 *
 * Обрабатываем узел МЕЖДУ левым и правым поддеревом
 *
 * КЛЮЧЕВОЕ СВОЙСТВО:
 * Для BST возвращает элементы в ОТСОРТИРОВАННОМ порядке!
 *
 * ПРИМЕР:
 * ```
 *     4
 *    / \
 *   2   6    → Inorder: [1, 2, 3, 4, 5, 6] (sorted!)
 *  / \   \
 * 1   3   5
 * ```
 */
fun inorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun dfs(node: TreeNode?) {
        if (node == null) return
        dfs(node.left)          // Сначала всё левое поддерево
        result.add(node.`val`)  // Обрабатываем МЕЖДУ рекурсиями
        dfs(node.right)         // Потом правое поддерево
    }

    dfs(root)
    return result
}

/**
 * POSTORDER: Left → Right → Root
 *
 * Обрабатываем узел ПОСЛЕ всех детей
 *
 * ПРИМЕНЕНИЕ:
 * - Удаление дерева (сначала детей, потом родителя)
 * - Вычисление высоты/размера (нужны данные от детей)
 * - Postfix expression (обратная польская нотация)
 *
 * ПРИМЕР:
 * ```
 *     1
 *    / \
 *   2   3    → Postorder: [4, 5, 2, 6, 3, 1]
 *  / \   \
 * 4   5   6
 * ```
 */
fun postorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun dfs(node: TreeNode?) {
        if (node == null) return
        dfs(node.left)          // Сначала левое поддерево
        dfs(node.right)         // Потом правое поддерево
        result.add(node.`val`)  // Обрабатываем ПОСЛЕ рекурсий
    }

    dfs(root)
    return result
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: ITERATIVE (с использованием Stack)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Preorder обход ИТЕРАТИВНО (без рекурсии)
 *
 * Используем Stack вместо call stack
 * Stack — LIFO (Last In, First Out)
 */
fun preorderIterative(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()

    root?.let { stack.addLast(it) }

    while (stack.isNotEmpty()) {
        val node = stack.removeLast()
        result.add(node.`val`)

        /**
         * ПОРЯДОК ДОБАВЛЕНИЯ: сначала right, потом left
         *
         * Stack работает по LIFO: последний добавленный = первый извлечённый
         * Нам нужен порядок Left → Right, значит добавляем Right → Left
         *
         * Пример:
         *   Добавили: right, left
         *   Извлечём: left (первым!), right
         */
        node.right?.let { stack.addLast(it) }
        node.left?.let { stack.addLast(it) }
    }

    return result
}

// ═══════════════════════════════════════════════════════════════════════════
// BFS: LEVEL ORDER TRAVERSAL
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Level-order обход (BFS по дереву)
 *
 * Возвращает узлы сгруппированные по уровням
 *
 * КЛЮЧЕВОЙ ПРИЁМ: запомнить размер очереди ДО обработки
 */
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = ArrayDeque<TreeNode>()
    queue.addLast(root)

    while (queue.isNotEmpty()) {
        /**
         * ЗАПОМИНАЕМ размер текущего уровня
         *
         * Это критически важно! Queue растёт во время обработки
         * (добавляем детей), но нам нужно обработать ровно
         * levelSize элементов — все узлы текущего уровня
         *
         * Level 0: queue = [1]       → levelSize = 1
         * Level 1: queue = [2, 3]    → levelSize = 2
         * Level 2: queue = [4, 5, 6] → levelSize = 3
         */
        val levelSize = queue.size
        val level = mutableListOf<Int>()

        repeat(levelSize) {
            val node = queue.removeFirst()
            level.add(node.`val`)

            node.left?.let { queue.addLast(it) }
            node.right?.let { queue.addLast(it) }
        }

        result.add(level)
    }

    return result
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: NUMBER OF ISLANDS (Grid)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 200: Number of Islands
 *
 * ИДЕЯ: Каждый раз когда находим '1', это новый остров
 *       DFS "топит" весь остров (меняет '1' на '0')
 *
 * ПОШАГОВЫЙ ПРИМЕР:
 * ```
 * [1,1,0]     Найдена '1' в (0,0) → count=1
 * [1,0,0]     DFS топит весь остров:
 * [0,0,1]       (0,0)→'0', (0,1)→'0', (1,0)→'0'
 *
 * [0,0,0]     Продолжаем сканировать...
 * [0,0,0]     Найдена '1' в (2,2) → count=2
 * [0,0,1]     DFS топит: (2,2)→'0'
 *
 * Ответ: 2 острова
 * ```
 */
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val rows = grid.size
    val cols = grid[0].size
    var count = 0

    fun dfs(r: Int, c: Int) {
        // BASE CASE: выход за границы или вода/уже посещено
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] != '1') {
            return
        }

        // SINK THE ISLAND: меняем '1' на '0' как способ пометить посещённое
        // Это экономит память — не нужен отдельный visited массив!
        grid[r][c] = '0'

        // ОБХОД 4 НАПРАВЛЕНИЙ: вверх, вниз, влево, вправо
        dfs(r + 1, c)  // вниз
        dfs(r - 1, c)  // вверх
        dfs(r, c + 1)  // вправо
        dfs(r, c - 1)  // влево
    }

    for (r in 0 until rows) {
        for (c in 0 until cols) {
            if (grid[r][c] == '1') {
                count++    // Нашли новый остров!
                dfs(r, c)  // "Утопили" весь остров — больше его не найдём
            }
        }
    }

    return count
}

// ═══════════════════════════════════════════════════════════════════════════
// BFS: SHORTEST PATH IN BINARY MATRIX
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 1091: Shortest Path in Binary Matrix
 *
 * Найти кратчайший путь от (0,0) до (n-1,n-1)
 * 0 = проходимо, 1 = стена
 * Можно двигаться в 8 направлениях
 *
 * ПОЧЕМУ BFS:
 * В невзвешенном графе BFS всегда находит кратчайший путь!
 * Первое достижение цели = минимальное расстояние
 */
fun shortestPathBinaryMatrix(grid: Array<IntArray>): Int {
    val n = grid.size
    if (grid[0][0] == 1 || grid[n-1][n-1] == 1) return -1

    // 8 направлений: ↖↑↗←→↙↓↘
    val directions = arrayOf(
        intArrayOf(-1,-1), intArrayOf(-1,0), intArrayOf(-1,1),
        intArrayOf(0,-1),                    intArrayOf(0,1),
        intArrayOf(1,-1),  intArrayOf(1,0),  intArrayOf(1,1)
    )

    val queue = ArrayDeque<IntArray>()
    // Храним в очереди: [row, col, distance]
    queue.addLast(intArrayOf(0, 0, 1))
    grid[0][0] = 1  // Помечаем как посещённое (используем grid как visited)

    while (queue.isNotEmpty()) {
        val (row, col, dist) = queue.removeFirst()

        // ЦЕЛЬ ДОСТИГНУТА: BFS гарантирует кратчайший путь!
        if (row == n - 1 && col == n - 1) {
            return dist
        }

        for (dir in directions) {
            val newRow = row + dir[0]
            val newCol = col + dir[1]

            if (newRow in 0 until n && newCol in 0 until n && grid[newRow][newCol] == 0) {
                queue.addLast(intArrayOf(newRow, newCol, dist + 1))
                /**
                 * КРИТИЧНО: помечаем СРАЗУ при добавлении, НЕ при извлечении!
                 *
                 * Иначе одну клетку могут добавить несколько раз
                 * из разных соседей → дубликаты в очереди → TLE
                 */
                grid[newRow][newCol] = 1
            }
        }
    }

    return -1  // Путь не найден
}

// ═══════════════════════════════════════════════════════════════════════════
// BFS: ROTTING ORANGES (Multi-source BFS)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 994: Rotting Oranges
 *
 * Multi-source BFS: несколько стартовых точек одновременно
 *
 * ИДЕЯ: все гнилые апельсины стартуют BFS одновременно
 *       Волны "гнили" расходятся параллельно
 *       Считаем минуты = уровни BFS
 */
fun orangesRotting(grid: Array<IntArray>): Int {
    val rows = grid.size
    val cols = grid[0].size
    val queue = ArrayDeque<IntArray>()
    var freshCount = 0

    // ИНИЦИАЛИЗАЦИЯ: находим ВСЕ гнилые (стартовые точки) и считаем свежие
    for (r in 0 until rows) {
        for (c in 0 until cols) {
            when (grid[r][c]) {
                2 -> queue.addLast(intArrayOf(r, c))  // Гнилой → в очередь
                1 -> freshCount++                      // Считаем свежие
            }
        }
    }

    // EDGE CASE: нет свежих апельсинов — ничего гнить не нужно
    if (freshCount == 0) return 0

    val directions = arrayOf(intArrayOf(0,1), intArrayOf(0,-1), intArrayOf(1,0), intArrayOf(-1,0))
    var minutes = 0

    while (queue.isNotEmpty() && freshCount > 0) {
        val levelSize = queue.size
        minutes++

        repeat(levelSize) {
            val (r, c) = queue.removeFirst()

            for (dir in directions) {
                val nr = r + dir[0]
                val nc = c + dir[1]

                if (nr in 0 until rows && nc in 0 until cols && grid[nr][nc] == 1) {
                    // Апельсин становится гнилым (2) и добавляется в очередь
                    // для распространения гнили на следующей минуте
                    grid[nr][nc] = 2
                    freshCount--
                    queue.addLast(intArrayOf(nr, nc))
                }
            }
        }
    }

    return if (freshCount == 0) minutes else -1
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: CYCLE DETECTION (Directed Graph)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 207: Course Schedule
 *
 * Можно ли пройти все курсы? = Есть ли цикл в графе зависимостей?
 *
 * АЛГОРИТМ: Three-color marking (WHITE/GRAY/BLACK)
 *   0 = WHITE (не посещён)
 *   1 = GRAY (в процессе обработки — на текущем пути DFS)
 *   2 = BLACK (полностью обработан)
 *
 * ЦИКЛ ОБНАРУЖЕН когда натыкаемся на GRAY вершину
 * (back edge — ребро к предку на текущем пути)
 */
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val graph = Array(numCourses) { mutableListOf<Int>() }
    for ((course, prereq) in prerequisites) {
        graph[prereq].add(course)
    }

    val visited = IntArray(numCourses)  // 0 = unvisited, 1 = visiting, 2 = visited

    fun hasCycle(node: Int): Boolean {
        /**
         * GRAY (1): вершина на текущем пути DFS
         * Если мы снова дошли до неё — это back edge = ЦИКЛ!
         *
         * Визуально: A → B → C → A (вернулись к A, который ещё GRAY)
         */
        if (visited[node] == 1) return true

        // BLACK (2): уже полностью обработана в другом поддереве
        // Безопасно пропустить — циклов через неё нет
        if (visited[node] == 2) return false

        // Помечаем как GRAY: "мы сейчас обрабатываем эту вершину"
        visited[node] = 1

        for (neighbor in graph[node]) {
            if (hasCycle(neighbor)) return true
        }

        // Помечаем как BLACK: "закончили обработку, циклов нет"
        visited[node] = 2
        return false
    }

    for (course in 0 until numCourses) {
        if (hasCycle(course)) return false
    }

    return true
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: PATH SUM
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 112: Path Sum
 *
 * Есть ли путь от корня до листа с суммой = targetSum?
 *
 * ИДЕЯ: Вычитаем значение каждого узла из targetSum
 *       Когда дошли до листа — проверяем, равен ли остаток нулю
 */
fun hasPathSum(root: TreeNode?, targetSum: Int): Boolean {
    if (root == null) return false

    val newTarget = targetSum - root.`val`

    // ЛИСТ: нет детей, проверяем сумму
    // Если newTarget == 0, значит сумма пути = targetSum
    if (root.left == null && root.right == null) {
        return newTarget == 0
    }

    return hasPathSum(root.left, newTarget) || hasPathSum(root.right, newTarget)
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: WORD SEARCH
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 79: Word Search
 *
 * DFS + Backtracking: ищем слово в сетке букв
 *
 * КЛЮЧЕВОЙ ПРИЁМ: временная пометка '#' для избежания повторного
 *                 использования клетки + восстановление (backtrack)
 */
fun exist(board: Array<CharArray>, word: String): Boolean {
    val rows = board.size
    val cols = board[0].size

    fun dfs(r: Int, c: Int, index: Int): Boolean {
        // SUCCESS: нашли все символы слова
        if (index == word.length) return true

        // FAILURE: выход за границы или неправильный символ
        if (r < 0 || r >= rows || c < 0 || c >= cols ||
            board[r][c] != word[index]) {
            return false
        }

        // ВРЕМЕННО помечаем как посещённое
        // '#' — специальный символ, которого нет в слове
        val temp = board[r][c]
        board[r][c] = '#'

        val found = dfs(r + 1, c, index + 1) ||
                    dfs(r - 1, c, index + 1) ||
                    dfs(r, c + 1, index + 1) ||
                    dfs(r, c - 1, index + 1)

        // BACKTRACK: восстанавливаем символ для других путей
        board[r][c] = temp

        return found
    }

    for (r in 0 until rows) {
        for (c in 0 until cols) {
            if (dfs(r, c, 0)) return true
        }
    }

    return false
}

// ═══════════════════════════════════════════════════════════════════════════
// BFS: WORD LADDER (Shortest transformation)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 127: Word Ladder
 *
 * Найти кратчайшую цепочку трансформаций: hit → hot → dot → dog → cog
 *
 * ИДЕЯ: BFS по графу слов, где рёбра = слова отличаются на 1 букву
 *
 * ОПТИМИЗАЦИЯ: генерируем соседей на лету
 *              (менять каждую букву на a-z) вместо сравнения всех пар
 */
fun ladderLength(beginWord: String, endWord: String, wordList: List<String>): Int {
    val wordSet = wordList.toMutableSet()
    if (endWord !in wordSet) return 0

    val queue = ArrayDeque<Pair<String, Int>>()
    queue.addLast(beginWord to 1)

    while (queue.isNotEmpty()) {
        val (word, length) = queue.removeFirst()

        if (word == endWord) return length

        val chars = word.toCharArray()
        for (i in chars.indices) {
            val original = chars[i]
            for (c in 'a'..'z') {
                chars[i] = c
                val newWord = String(chars)

                if (newWord in wordSet) {
                    // УДАЛЯЕМ из множества = помечаем как посещённое
                    // Это экономит память по сравнению с отдельным visited set
                    wordSet.remove(newWord)
                    queue.addLast(newWord to length + 1)
                }
            }
            // Восстанавливаем символ для генерации следующих вариаций
            chars[i] = original
        }
    }

    return 0
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: CLONE GRAPH
// ═══════════════════════════════════════════════════════════════════════════

class Node(var `val`: Int) {
    var neighbors: ArrayList<Node?> = ArrayList()
}

/**
 * LeetCode 133: Clone Graph
 *
 * Глубокое копирование графа с возможными циклами
 *
 * КЛЮЧЕВОЙ ПРИЁМ: HashMap original → clone
 * Если уже клонировали узел — возвращаем клон (избегаем бесконечной рекурсии)
 */
fun cloneGraph(node: Node?): Node? {
    if (node == null) return null

    val cloned = mutableMapOf<Node, Node>()

    fun dfs(original: Node): Node {
        // Если уже клонировали этот узел — возвращаем готовый клон
        cloned[original]?.let { return it }

        val copy = Node(original.`val`)
        /**
         * КРИТИЧНО: добавляем в map ДО обхода соседей!
         *
         * Иначе при цикле A → B → A:
         * - Начали клонировать A
         * - Пошли к соседу B
         * - B хочет клонировать соседа A
         * - A ещё не в map → бесконечная рекурсия!
         */
        cloned[original] = copy

        for (neighbor in original.neighbors) {
            neighbor?.let { copy.neighbors.add(dfs(it)) }
        }

        return copy
    }

    return dfs(node)
}

// ═══════════════════════════════════════════════════════════════════════════
// BFS: WALLS AND GATES (Multi-source BFS)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * LeetCode 286: Walls and Gates
 *
 * Multi-source BFS от всех ворот одновременно
 * Заполняем расстояния до ближайших ворот
 */
fun wallsAndGates(rooms: Array<IntArray>) {
    if (rooms.isEmpty()) return

    val rows = rooms.size
    val cols = rooms[0].size
    val queue = ArrayDeque<IntArray>()

    // MULTI-SOURCE: добавляем ВСЕ ворота (0) в начальную очередь
    // BFS волны расходятся от всех ворот параллельно
    for (r in 0 until rows) {
        for (c in 0 until cols) {
            if (rooms[r][c] == 0) {
                queue.addLast(intArrayOf(r, c))
            }
        }
    }

    val directions = arrayOf(intArrayOf(0,1), intArrayOf(0,-1), intArrayOf(1,0), intArrayOf(-1,0))

    while (queue.isNotEmpty()) {
        val (r, c) = queue.removeFirst()

        for (dir in directions) {
            val nr = r + dir[0]
            val nc = c + dir[1]

            /**
             * Обновляем только ПУСТЫЕ комнаты (INF = 2147483647)
             *
             * Стены (-1) и уже посещённые комнаты пропускаем
             * Первое посещение = кратчайшее расстояние (BFS гарантирует)
             */
            if (nr in 0 until rows && nc in 0 until cols && rooms[nr][nc] == Int.MAX_VALUE) {
                rooms[nr][nc] = rooms[r][c] + 1
                queue.addLast(intArrayOf(nr, nc))
            }
        }
    }
}
```

### Java

```java
// ═══════════════════════════════════════════════════════════════════════════
// BFS: LEVEL ORDER TRAVERSAL
// ═══════════════════════════════════════════════════════════════════════════

public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> result = new ArrayList<>();
    if (root == null) return result;

    Queue<TreeNode> queue = new LinkedList<>();
    queue.offer(root);

    while (!queue.isEmpty()) {
        int levelSize = queue.size();  // Размер текущего уровня
        List<Integer> level = new ArrayList<>();

        for (int i = 0; i < levelSize; i++) {
            TreeNode node = queue.poll();
            level.add(node.val);

            if (node.left != null) queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }

        result.add(level);
    }

    return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// DFS: NUMBER OF ISLANDS
// ═══════════════════════════════════════════════════════════════════════════

public int numIslands(char[][] grid) {
    if (grid == null || grid.length == 0) return 0;

    int count = 0;
    for (int r = 0; r < grid.length; r++) {
        for (int c = 0; c < grid[0].length; c++) {
            if (grid[r][c] == '1') {
                count++;
                dfs(grid, r, c);
            }
        }
    }
    return count;
}

private void dfs(char[][] grid, int r, int c) {
    if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length ||
        grid[r][c] != '1') {
        return;
    }

    // Помечаем как посещённое, меняя '1' на '0' (sink the island)
    grid[r][c] = '0';

    dfs(grid, r + 1, c);
    dfs(grid, r - 1, c);
    dfs(grid, r, c + 1);
    dfs(grid, r, c - 1);
}
```

### Python

```python
from collections import deque
from typing import List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# BFS: LEVEL ORDER TRAVERSAL
# ═══════════════════════════════════════════════════════════════════════════

def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level)

    return result

# ═══════════════════════════════════════════════════════════════════════════
# DFS: NUMBER OF ISLANDS
# ═══════════════════════════════════════════════════════════════════════════

def num_islands(grid: List[List[str]]) -> int:
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r: int, c: int):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return

        grid[r][c] = '0'  # WHY: mark as visited

        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)

    return count

# ═══════════════════════════════════════════════════════════════════════════
# BFS: ROTTING ORANGES
# ═══════════════════════════════════════════════════════════════════════════

def oranges_rotting(grid: List[List[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh_count += 1

    if fresh_count == 0:
        return 0

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    minutes = 0

    while queue and fresh_count > 0:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()

            for dr, dc in directions:
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh_count -= 1
                    queue.append((nr, nc))

    return minutes if fresh_count == 0 else -1

# ═══════════════════════════════════════════════════════════════════════════
# DFS: COURSE SCHEDULE (Cycle Detection)
# ═══════════════════════════════════════════════════════════════════════════

def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    graph = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    # 0 = unvisited, 1 = visiting, 2 = visited
    state = [0] * num_courses

    def has_cycle(node: int) -> bool:
        if state[node] == 1:  # WHY: back edge
            return True
        if state[node] == 2:  # WHY: already processed
            return False

        state[node] = 1

        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True

        state[node] = 2
        return False

    for course in range(num_courses):
        if has_cycle(course):
            return False

    return True
```

---

## Распространённые ошибки

### 1. Забыли пометить как visited при добавлении в queue (BFS)

```kotlin
// ❌ НЕПРАВИЛЬНО: помечаем при извлечении
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    if (visited.contains(node)) continue  // Уже добавили в queue несколько раз!
    visited.add(node)
    // ...
}

// ✅ ПРАВИЛЬНО: помечаем при добавлении
if (!visited.contains(neighbor)) {
    // Помечаем СРАЗУ при добавлении, чтобы не добавить повторно
    visited.add(neighbor)
    queue.addLast(neighbor)
}
```

### 2. Не восстановили состояние в backtracking DFS

```kotlin
// ❌ НЕПРАВИЛЬНО: не восстановили ячейку (Word Search)
fun dfs(r: Int, c: Int, index: Int): Boolean {
    board[r][c] = '#'
    val found = dfs(r + 1, c, index + 1) || ...
    // Забыли восстановить!
    return found
}

// ✅ ПРАВИЛЬНО: восстанавливаем
fun dfs(r: Int, c: Int, index: Int): Boolean {
    val temp = board[r][c]
    board[r][c] = '#'
    val found = dfs(r + 1, c, index + 1) || ...
    board[r][c] = temp  // Backtrack: восстанавливаем для других путей
    return found
}
```

### 3. Неправильный base case в рекурсии

```kotlin
// ❌ НЕПРАВИЛЬНО: проверяем после обращения
fun dfs(node: TreeNode) {
    result.add(node.`val`)  // NullPointerException если node == null
    dfs(node.left)
    dfs(node.right)
}

// ✅ ПРАВИЛЬНО: проверяем в начале
fun dfs(node: TreeNode?) {
    if (node == null) return  // Base case ВСЕГДА первым делом!
    result.add(node.`val`)
    dfs(node.left)
    dfs(node.right)
}
```

### 4. Cycle Detection: не различаем "visiting" и "visited"

```kotlin
// ❌ НЕПРАВИЛЬНО: только visited
val visited = mutableSetOf<Int>()
fun hasCycle(node: Int): Boolean {
    if (visited.contains(node)) return true  // А это back edge или просто пересечение путей?
}

// ✅ ПРАВИЛЬНО: три состояния
val state = IntArray(n)  // 0 = unvisited, 1 = visiting, 2 = visited
fun hasCycle(node: Int): Boolean {
    // visiting (1) = на текущем пути → back edge → ЦИКЛ!
    if (state[node] == 1) return true
    // visited (2) = уже полностью обработан в другом поддереве → безопасно
    if (state[node] == 2) return false
}
```

### 5. Неправильные границы в grid

```kotlin
// ❌ НЕПРАВИЛЬНО: проверяем границы после обращения
fun dfs(r: Int, c: Int) {
    if (grid[r][c] != '1') return  // ArrayIndexOutOfBounds!
}

// ✅ ПРАВИЛЬНО: границы первым делом
fun dfs(r: Int, c: Int) {
    // Проверка границ ВСЕГДА первая — иначе ArrayIndexOutOfBounds!
    if (r < 0 || r >= rows || c < 0 || c >= cols) return
    if (grid[r][c] != '1') return
}
```

### 6. Stack overflow в глубокой рекурсии

```kotlin
// ❌ НЕПРАВИЛЬНО: рекурсия для очень большого графа
fun dfs(node: Int) {
    // 100000 вложенных вызовов → StackOverflowError
}

// ✅ ПРАВИЛЬНО: итеративный DFS со стеком
fun dfsIterative(start: Int) {
    val stack = ArrayDeque<Int>()
    stack.addLast(start)

    while (stack.isNotEmpty()) {
        val node = stack.removeLast()
        // ...
    }
}
```

---

## Когда использовать?

### Decision Tree

```
Задача на обход графа/дерева?
│
├─ Нужен КРАТЧАЙШИЙ ПУТЬ?
│   │
│   ├─ Невзвешенный граф? → BFS
│   │
│   └─ Взвешенный граф? → Dijkstra (не BFS/DFS)
│
├─ Нужно проверить ВСЕ пути / найти ЛЮБОЙ путь?
│   │
│   └─ Да → DFS
│
├─ LEVEL-ORDER обработка?
│   │
│   └─ Да → BFS
│
├─ Cycle detection в directed graph?
│   │
│   └─ Да → DFS с тремя состояниями
│
├─ Connected components?
│   │
│   └─ Да → DFS/BFS (любой) или Union-Find
│
└─ Распространение от НЕСКОЛЬКИХ источников?
    │
    └─ Да → Multi-source BFS
```

### Сравнение DFS vs BFS

| Критерий | DFS | BFS |
|----------|-----|-----|
| Shortest path (unweighted) | Нет | Да |
| Память (дерево) | O(h) высота | O(w) ширина |
| Полный обход | Да | Да |
| Реализация | Проще (рекурсия) | Queue |
| Cycle detection | Да (back edges) | Сложнее |
| Topological sort | Да | Да (Kahn's) |
| Level-by-level | Нет | Да |

### Признаки задачи

**DFS:**
- "Find any path", "check if exists"
- "All paths", "all combinations"
- "Detect cycle"
- "Connected components"
- "Backtracking" (subsets, permutations)

**BFS:**
- "Shortest path", "minimum steps"
- "Level order", "layer by layer"
- "Nearest", "closest"
- "Spread/propagate from multiple sources"

---

## Практика

### Концептуальные вопросы

1. **Почему BFS находит кратчайший путь в невзвешенном графе?**

   *Ответ:* BFS обходит вершины уровень за уровнем. Когда мы первый раз достигаем вершины, мы сделали минимальное количество шагов — BFS никогда не "прыгает" через уровни.

2. **Как отличить "visiting" от "visited" в cycle detection?**

   *Ответ:* "Visiting" = узел в текущем пути рекурсии. "Visited" = узел полностью обработан. Back edge идёт в "visiting" узел, создавая цикл.

3. **Когда использовать итеративный DFS вместо рекурсивного?**

   *Ответ:* Когда глубина может быть очень большой (> 1000-10000 вызовов) — чтобы избежать StackOverflowError. Также для определённых алгоритмов (Tarjan, Kosaraju).

4. **Как работает multi-source BFS?**

   *Ответ:* Начинаем со ВСЕХ источников в очереди одновременно. Они "распространяются" параллельно, и каждая ячейка получает расстояние до ближайшего источника.

### LeetCode задачи

#### DFS на деревьях

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 144 | Binary Tree Preorder | Easy | Базовый DFS |
| 94 | Binary Tree Inorder | Easy | BST → sorted |
| 104 | Maximum Depth | Easy | Высота дерева |
| 112 | Path Sum | Easy | Target в листе |
| 124 | Binary Tree Max Path Sum | Hard | Глобальный max |

#### BFS на деревьях

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 102 | Binary Tree Level Order | Medium | Базовый BFS |
| 103 | Zigzag Level Order | Medium | Reverse по уровням |
| 199 | Right Side View | Medium | Последний на уровне |
| 111 | Minimum Depth | Easy | Первый лист |

#### Grid Problems

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 200 | Number of Islands | Medium | DFS flood fill |
| 695 | Max Area of Island | Medium | DFS с подсчётом |
| 994 | Rotting Oranges | Medium | Multi-source BFS |
| 1091 | Shortest Path in Binary Matrix | Medium | BFS shortest |
| 79 | Word Search | Medium | DFS + backtrack |

#### Graph Problems

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 133 | Clone Graph | Medium | DFS + HashMap |
| 207 | Course Schedule | Medium | Cycle detection |
| 127 | Word Ladder | Hard | BFS на состояниях |
| 286 | Walls and Gates | Medium | Multi-source BFS |
| 417 | Pacific Atlantic | Medium | DFS от океанов |

---

## Связанные темы

### Prerequisites (нужно знать до)
- [Trees](../data-structures/trees-binary.md) — структура деревьев
- [Graphs](../data-structures/graphs.md) — представление графов
- [Recursion](../algorithms/backtracking.md) — для DFS

### Unlocks (открывает доступ к)
- [Topological Sort Pattern](./topological-sort-pattern.md) — на основе DFS
- [Union-Find Pattern](./union-find-pattern.md) — альтернатива для компонент
- [Shortest Path Algorithms](../algorithms/shortest-paths.md) — Dijkstra, Bellman-Ford

### Часто комбинируется с
- **Backtracking** — DFS + undo
- **Dynamic Programming** — memoization в DFS
- **Union-Find** — для connected components
- **Topological Sort** — DFS postorder

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "DFS и BFS взаимозаменяемы" | **Нет!** BFS даёт shortest path в невзвешенном графе, DFS — нет. Для maze shortest path — только BFS. Выбор критичен |
| "BFS всегда требует больше памяти" | **Зависит от структуры!** BFS хранит O(width), DFS — O(depth). Для wide shallow tree DFS лучше, для deep narrow — BFS |
| "Рекурсивный DFS = итеративный" | **Нет!** Рекурсивный DFS может stack overflow на глубоких графах. Для production нужен explicit stack |
| "Visited нужен всегда" | **Для деревьев не нужен!** Деревья не имеют циклов. Для графов — обязателен, иначе бесконечный цикл |
| "Multi-source BFS сложен" | **Простой шаблон!** Добавь все источники в queue ДО начала BFS. Остальной код идентичен single-source |
| "BFS не работает для weighted graphs" | **Работает, но не оптимально!** BFS даст путь, но не кратчайший по весу. Для weighted — Dijkstra или Bellman-Ford |
| "DFS обязательно рекурсивный" | **Нет!** Итеративный DFS со стеком — лучше для глубоких графов. Preorder легко, postorder сложнее |
| "Level-order traversal только для деревьев" | **Работает для любых графов!** BFS по уровням применим везде. Главное — visited set для предотвращения циклов |

---

## CS-фундамент

| CS-концепция | Применение в DFS/BFS |
|--------------|---------------------|
| **Graph Traversal** | Систематический обход всех достижимых вершин. DFS идёт вглубь (Stack), BFS — по уровням (Queue) |
| **Shortest Path (Unweighted)** | BFS гарантирует кратчайший путь в невзвешенном графе. Первое посещение = минимальное расстояние |
| **Cycle Detection** | DFS: back edge (возврат к ancestor в рекурсии). BFS: посещение уже visited с другим parent |
| **Connected Components** | DFS/BFS от каждой непосещённой вершины находит одну компоненту. Количество запусков = количество компонент |
| **Topological Sort** | DFS postorder в обратном порядке. Работает только для DAG (directed acyclic graph) |
| **Level-Order Processing** | BFS естественно обрабатывает граф по уровням. Нужен size = queue.size() в начале каждого уровня |
| **Tree Traversals** | DFS даёт preorder (node→left→right), inorder (left→node→right), postorder (left→right→node). BFS = level-order |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Labuladong BFS](https://labuladong.online/algo/en/essential-technique/bfs-framework/) | Туториал | BFS Template |
| 2 | [LeetCode Patterns](https://medium.com/leetcode-patterns/leetcode-pattern-1-bfs-dfs-25-of-the-problems-part-1-519450a84353) | Туториал | 25% coverage |
| 3 | [GeeksforGeeks](https://www.geeksforgeeks.org/detect-cycle-in-a-graph/) | Туториал | Cycle detection |
| 4 | [Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/graph/) | Гайд | Cheatsheet |
| 5 | [Interview Cake](https://www.interviewcake.com/concept/java/bfs) | Туториал | BFS shortest |

---

## Куда дальше

→ **Расширение:** [[topological-sort-pattern]] — DFS для dependency ordering
→ **Связанный паттерн:** [[union-find-pattern]] — альтернатива для connected components
→ **Комбинируется с:** [[backtracking]] — DFS с откатом для перебора
→ **Вернуться к:** [[patterns-overview|Обзор паттернов]]


---

## Проверь себя

> [!question]- Когда BFS гарантирует кратчайший путь, а когда нет?
> BFS гарантирует кратчайший путь только в невзвешенных графах (все рёбра вес 1). Каждый level = +1 к расстоянию. Для взвешенных графов нужен Dijkstra (неотрицательные веса) или Bellman-Ford (отрицательные). BFS в взвешенном графе может найти некратчайший путь.

> [!question]- Как DFS обнаруживает цикл в направленном графе и почему трёх цветов достаточно?
> Три состояния: WHITE (не посещён), GRAY (в текущем стеке DFS), BLACK (полностью обработан). Цикл найден когда DFS встречает GRAY вершину — это back edge к предку в текущем пути. Двух цветов недостаточно: visited-only не отличает cross edge от back edge в directed graph.

> [!question]- Задача: найти количество островов в 2D grid. Почему DFS и BFS дают одинаковый результат и какой эффективнее?
> Оба обхода находят все связные компоненты. Результат одинаков потому что нужен только факт связности, не кратчайший путь. DFS обычно проще в реализации (рекурсия). BFS безопаснее для больших компонент (нет stack overflow). Итеративный DFS со стеком = оптимальный выбор.

## Ключевые карточки

Чем DFS отличается от BFS?
?
DFS: стек/рекурсия, идёт вглубь, O(h) память для деревьев. BFS: очередь, идёт вширь, O(w) память. DFS: cycle detection, topological sort, path finding. BFS: shortest path (невзвешенный), level-order, multi-source propagation.

Что такое Multi-source BFS?
?
BFS с несколькими стартовыми точками одновременно. Все источники в очередь на старте, level 0. Каждый level = +1 расстояние от ближайшего источника. Пример: 01 Matrix (расстояние от каждой ячейки до ближайшего 0). O(V+E).

Какие 6 обходов деревьев существуют?
?
DFS: Preorder (root-left-right), Inorder (left-root-right), Postorder (left-right-root). BFS: Level-order (по уровням). Итеративные: Morris Traversal (O(1) память), Iterative с explicit stack. Inorder BST дает отсортированный порядок.

Когда использовать итеративный DFS вместо рекурсивного?
?
1) Глубокие графы/деревья (stack overflow). 2) Нужен контроль над стеком. 3) Нужно прервать обход досрочно. 4) Языки с лимитом рекурсии (Python ~1000). Итеративный DFS: explicit stack, push children in reverse order.

Как BFS решает задачу Shortest Path в невзвешенном графе?
?
Очередь хранит (node, distance). Каждый level = distance+1. Первое посещение вершины = кратчайший путь к ней. visited set предотвращает повторные посещения. O(V+E) время, O(V) память. Для восстановления пути: parent map.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[patterns/topological-sort-pattern]] | Топологическая сортировка на основе DFS/BFS |
| Углубиться | [[algorithms/graph-algorithms]] | Алгоритмы на графах подробно |
| Смежная тема | [[data-structures/graphs]] | Представление графов |
| Обзор | [[patterns/patterns-overview]] | Вернуться к карте паттернов |


---

*Обновлено: 2026-01-07 — добавлены педагогические секции (интуиция DFS/BFS, типичные ошибки, 5 ментальных моделей)*
