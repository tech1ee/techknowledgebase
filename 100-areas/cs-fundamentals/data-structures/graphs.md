---
title: "Графы (Graphs)"
created: 2025-12-29
modified: 2026-01-06
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - graph-representations
  - graph-traversal-dfs-bfs
  - shortest-path-algorithms
  - topological-ordering
  - connectivity-components
  - weighted-vs-unweighted
prerequisites:
  - "[[arrays-strings]]"
  - "[[hash-tables]]"
  - "[[stacks-queues]]"
  - "[[recursion-fundamentals]]"
teaches:
  - adjacency-list-matrix
  - bfs-shortest-path
  - dfs-cycle-detection
  - topological-sort
  - dijkstra-algorithm
unlocks:
  - "[[graph-algorithms]]"
  - "[[union-find-pattern]]"
  - "[[shortest-paths]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - interview
related:
  - "[[graph-algorithms]]"
  - "[[union-find-pattern]]"
  - "[[shortest-paths]]"
---

# Графы (Graphs)

---

## TL;DR

Граф — структура данных для представления связей между объектами. Состоит из вершин (nodes/vertices) и рёбер (edges). Используй **adjacency list** для большинства задач (O(V+E) память), **adjacency matrix** для плотных графов или быстрой проверки рёбер (O(1)). BFS находит кратчайший путь в невзвешенном графе, DFS — для поиска циклов и топологической сортировки. Сложность обходов: O(V+E).

---

## Часть 1: Интуиция без кода

### Аналогия 1: Карта метро

Представь схему метро в большом городе:

```
                    [Киевская]
                        │
     [Арбатская]───[Смоленская]───[Парк Культуры]
          │             │               │
     [Площадь      [Кропоткинская]  [Фрунзенская]
      Революции]        │
          │        [Октябрьская]
     [Китай-город]
```

**Станции = вершины (nodes).** Каждая станция — это точка на схеме.

**Переходы = рёбра (edges).** Линия между станциями — возможность перейти.

**Вопрос:** Как добраться от Арбатской до Фрунзенской?

**Ответ:** Арбатская → Смоленская → Парк Культуры → Фрунзенская (3 пересадки).

**Это и есть граф** — структура, которая хранит "что с чем связано".

### Аналогия 2: Социальная сеть

```
           Аня
          /   \
       Боря   Вика
        |       |
      Гриша───Даша───Женя
                      |
                    Захар
```

- **Люди = вершины**
- **Дружба = рёбра**
- Аня дружит с Борей и Викой
- Боря НЕ дружит с Викой напрямую (нет ребра)

**Типичные вопросы о графе-соцсети:**
- Сколько друзей у Даши? → 3 (Вика, Гриша, Женя)
- Как Аня может узнать Захара? → Через друзей друзей
- Есть ли "группа друзей" где все знают всех? → Гриша-Даша-Женя? Нет, Гриша и Женя не связаны.

### Аналогия 3: GPS-навигатор

```
          A ──5км── B ──3км── C
          │         │         │
         4км       2км       6км
          │         │         │
          D ──7км── E ──1км── F
```

Это **взвешенный граф** — рёбра имеют "стоимость" (расстояние).

**Вопрос:** Кратчайший путь от A до F?
- A → B → C → F = 5 + 3 + 6 = 14 км
- A → B → E → F = 5 + 2 + 1 = 8 км ← **Оптимально!**
- A → D → E → F = 4 + 7 + 1 = 12 км

**Именно так работает Google Maps** — ищет кратчайший путь по графу дорог.

### Почему граф — не просто "список связей"?

```
❌ НАИВНЫЙ ПОДХОД: Список пар
связи = [(A,B), (B,C), (A,D), (D,E), ...]

Проблема: чтобы найти всех соседей A,
нужно просмотреть ВСЕ пары — O(E)

✅ ГРАФ: Каждая вершина "знает" своих соседей
A → [B, D]
B → [A, C, E]
D → [A, E]

Соседи A? → Мгновенно: [B, D] — O(1)
```

### Граф vs Дерево

```
ДЕРЕВО:                         ГРАФ:
У каждого узла                 Связи могут быть
ОДИН родитель                  ЛЮБЫЕ

       A                          A───B
      / \                        / \ /
     B   C                      C───D───E
    / \                              \|/
   D   E                              F

- Нет циклов                   - Могут быть циклы
- Один путь между              - Много путей между
  любыми двумя узлами           двумя вершинами
- Иерархическая структура      - Сетевая структура
```

**Важно:** Дерево — это частный случай графа (связный граф без циклов).

---

## Часть 2: Почему графы сложные (типичные ошибки)

### Ошибка 1: Забыли отметить вершину как посещённую

> **Факт:** Это самая частая ошибка при работе с графами (источник: [YouCademy](https://youcademy.org/common-mistakes-in-graph-dfs/)).

```
ПРОБЛЕМА: Бесконечный цикл

Граф:  A ─── B
       │     │
       C ─── D

Обход без visited:
A → B → D → C → A → B → D → C → A → ...
(бесконечно!)

Почему? Граф содержит цикл A-B-D-C-A.
Без отслеживания посещённых вершин мы ходим по кругу.
```

**Правило:** Всегда отмечай вершину как посещённую СРАЗУ при добавлении в очередь/стек.

### Ошибка 2: Отметили visited ПОСЛЕ извлечения из очереди

```
┌──────────────────────────────────────────────────────────────────┐
│ ❌ НЕПРАВИЛЬНО: visited после извлечения                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Граф: A → B                                                    │
│         ↓   ↓                                                    │
│         C → D                                                    │
│                                                                  │
│   Шаг 1: очередь = [A], visited = {}                             │
│   Шаг 2: извлекли A, visited = {A}, добавили B и C               │
│          очередь = [B, C]                                        │
│   Шаг 3: извлекли B, visited = {A,B}, добавили D                 │
│          очередь = [C, D]                                        │
│   Шаг 4: извлекли C, visited = {A,B,C}, добавили D               │
│          очередь = [D, D]  ← D ДОБАВЛЕН ДВАЖДЫ!                  │
│                                                                  │
│   РЕЗУЛЬТАТ: D обработается 2 раза = неэффективно или ошибка    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ✅ ПРАВИЛЬНО: visited ПРИ добавлении в очередь                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Шаг 1: очередь = [A], visited = {A}  ← сразу!                  │
│   Шаг 2: извлекли A, добавили B и C, visited = {A,B,C}           │
│          очередь = [B, C]                                        │
│   Шаг 3: извлекли B, D не в visited, добавили D                  │
│          очередь = [C, D], visited = {A,B,C,D}                   │
│   Шаг 4: извлекли C, D уже в visited → пропускаем                │
│          очередь = [D]                                           │
│   Шаг 5: извлекли D                                              │
│                                                                  │
│   РЕЗУЛЬТАТ: D обработан ровно 1 раз ✓                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Ошибка 3: Перепутали BFS и DFS для кратчайшего пути

> **Факт:** "Using DFS when shortest path is needed will not work. If we use DFS then we will travel down a path till we don't find the target. But once we have found it we are not sure if it is at the shortest distance." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/when-to-use-dfs-or-bfs-to-solve-a-graph-problem/)

```
Граф:   A ─── B ─── C ─── D
        │                 │
        └─────────────────┘

Кратчайший путь A → D?
Ответ: A → D (1 ребро)

DFS может найти: A → B → C → D (3 ребра) — первый найденный путь!
BFS найдёт:      A → D (1 ребро) — гарантированно кратчайший!

ПОЧЕМУ?
BFS обходит "волнами" по уровням:
  Уровень 0: A
  Уровень 1: B, D  ← D найден на уровне 1!

DFS идёт "вглубь" по первому попавшемуся пути:
  A → B → C → D  ← нашёл, но длинный путь
```

### Ошибка 4: Не обработали несвязный граф

```
┌──────────────────────────────────────────────────────────────────┐
│ НЕСВЯЗНЫЙ ГРАФ: два "острова"                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│      A ─── B         E ─── F                                     │
│      │     │         │                                           │
│      C ─── D         G                                           │
│                                                                  │
│   Компонента 1        Компонента 2                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

❌ ОШИБКА: bfs(start=A) → посетит только {A,B,C,D}
           E, F, G — НЕ ПОСЕЩЕНЫ!

✅ РЕШЕНИЕ: запустить обход от КАЖДОЙ непосещённой вершины:

for (vertex in all_vertices):
    if (vertex not in visited):
        bfs(vertex)  // новая компонента!
```

### Ошибка 5: Неправильное направление рёбер

```
ОРИЕНТИРОВАННЫЙ vs НЕОРИЕНТИРОВАННЫЙ

Задача: "Курс A требует прохождения курса B"
        A зависит от B

❌ НЕПРАВИЛЬНО: A → B  (A указывает на B)
   Это значит: "от A можно перейти к B"
   Но по смыслу: "B должен быть ДО A"!

✅ ПРАВИЛЬНО: B → A  (B указывает на A)
   Это значит: "B ведёт к A" = "сначала B, потом A"

Топологическая сортировка даст: B, A (правильный порядок)
```

### Ошибка 6: StackOverflow при рекурсивном DFS

```
Глубокий граф: 0 → 1 → 2 → ... → 50000

Рекурсивный DFS:
dfs(0) вызывает
  dfs(1) вызывает
    dfs(2) вызывает
      ...
        dfs(50000)

⚠️ РЕЗУЛЬТАТ: StackOverflowError!
   Системный стек вызовов ограничен (~1-10 MB)

✅ РЕШЕНИЕ: Итеративный DFS с явным стеком
   Явный стек использует heap, который гораздо больше
```

### Ошибка 7: Adjacency List vs Matrix — неправильный выбор

| Граф | Неправильный выбор | Правильный выбор |
|------|-------------------|------------------|
| Соцсеть: 1M пользователей, ~500 друзей каждый | Matrix: 10^12 ячеек = 1 TB памяти! | List: ~500M связей = умеренно |
| Полный граф 100 вершин (все связаны со всеми) | List: много дублирования | Matrix: 10K ячеек, быстрая проверка |

**Правило:**
- **E << V²** (разреженный) → Adjacency List
- **E ≈ V²** (плотный) → Adjacency Matrix

---

## Часть 3: Ментальные модели

### Модель 1: Волна (для BFS)

> "Breadth‑First Search spreads through the graph like waves, reaching nearby nodes first, then expanding outwards — layer by layer." — [Jake Tae](https://jaketae.github.io/study/bfs-dfs/)

```
Брось камень в воду — волны расходятся кругами:

                    Уровень 0 (старт)
                          │
          ┌───────────────┼───────────────┐
          │               │               │
        Уровень 1       Уровень 1       Уровень 1
          │               │               │
     ┌────┴────┐     ┌────┴────┐         ...
  Уровень 2  Уровень 2  ...


Пример: поиск кратчайшего пути от A до E

        A ─── B ─── C
        │     │
        D ─── E

Волна 0: [A]           ← камень упал
Волна 1: [B, D]        ← первый круг волны
Волна 2: [C, E]        ← второй круг, E найден!

Кратчайший путь до E = 2 ребра (нашли на волне 2)
```

**Когда использовать "волну":**
- Кратчайший путь в невзвешенном графе
- Обход по уровням (например, друзья друзей)
- Поиск ближайшего объекта

### Модель 2: Исследователь лабиринта (для DFS)

> "You pick a path and follow it until you hit a dead end, then you backtrack and try another route. This natural, intuitive approach is the essence of Depth-First Search." — [Medium](https://medium.com/swlh/solving-mazes-with-depth-first-search-e315771317ae)

```
Представь: ты в лабиринте с фонариком

        START
          │
    ┌─────┼─────┐
    │     │     │
    ▼     ▼     ▼
   [A]   [B]   [C]
    │     │
    ▼     ▼
   ТУПИК [D]───[E]
              │
              ▼
            ВЫХОД

Стратегия DFS:
1. Иди ВГЛУБЬ по первому пути → A → тупик
2. ВЕРНИСЬ (backtrack) → попробуй B → D → E → Выход!

DFS не гарантирует кратчайший путь,
но ТОЧНО найдёт выход (если он есть).
```

**Когда использовать "исследователя":**
- Поиск ЛЮБОГО пути (не обязательно кратчайшего)
- Обнаружение циклов
- Backtracking-задачи (судоку, N-queens)
- Топологическая сортировка

### Модель 3: Очередь в банке (для понимания BFS)

```
BFS = строгая очередь: кто первый пришёл, первым обслужили

Очередь клиентов:     [A] → [B] → [C] → ...

1. Вызываем A (первого в очереди)
2. A приводит друзей (соседей): D, E
3. D и E встают В КОНЕЦ очереди
4. Вызываем B (следующего в очереди)
5. ...

Порядок обслуживания: A, B, C, D, E, ...

Это гарантирует: сначала все "близкие" (уровень 1),
потом "далёкие" (уровень 2), и т.д.
```

### Модель 4: Стопка тарелок (для понимания DFS)

```
DFS = стопка тарелок: последняя положенная — первая взятая

Стопка:      [E]  ← верх (последний добавленный)
             [D]
             [C]
             [B]
             [A]  ← низ (первый добавленный)

1. Берём E (верхнюю тарелку)
2. E добавляет соседей F, G на верх стопки
3. Берём G (новую верхнюю)
4. ...

Это приводит к "глубокому" исследованию:
A → B → C → D → E → G → ... → backtrack → F → ...
```

### Модель 5: Карта и маркер (для построения графа)

```
Строим граф зависимостей курсов:

Курсы: Алгебра, Матанализ, Физика, Программирование
Зависимости:
  - Матанализ требует Алгебру
  - Физика требует Матанализ
  - Программирование требует Алгебру

Как нарисовать граф?
1. Напиши каждый курс как точку (вершину)
2. Проведи стрелку от prerequisite к курсу

        [Алгебра]
           │ \
           ▼  \
     [Матанализ] ▼
           │   [Программирование]
           ▼
       [Физика]

Топологическая сортировка:
Алгебра → Матанализ → Физика → Программирование
                    ↘ Программирование

(можно начать Программирование после Алгебры,
не дожидаясь Матанализа и Физики)
```

### Сравнение BFS и DFS

```
┌─────────────────────────────────────────────────────────────────┐
│                    BFS vs DFS: ВЫБОР                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ИСПОЛЬЗУЙ BFS КОГДА:               ИСПОЛЬЗУЙ DFS КОГДА:       │
│   ─────────────────────              ─────────────────────      │
│   • Нужен КРАТЧАЙШИЙ путь            • Нужен ЛЮБОЙ путь         │
│   • Обход по уровням                 • Поиск циклов             │
│   • Ближайший объект                 • Топологическая сорт.     │
│   • Граф широкий и неглубокий        • Граф глубокий            │
│                                                                 │
│   СТРУКТУРА ДАННЫХ:                  СТРУКТУРА ДАННЫХ:          │
│   Очередь (Queue, FIFO)              Стек (Stack, LIFO)         │
│                                      или рекурсия               │
│                                                                 │
│   АНАЛОГИЯ:                          АНАЛОГИЯ:                  │
│   Волна от камня в воде              Исследователь лабиринта    │
│   Очередь в банке                    Стопка тарелок             │
│                                                                 │
│   ПАМЯТЬ:                            ПАМЯТЬ:                    │
│   O(ширина графа)                    O(глубина графа)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно?

### Мотивирующая проблема

**Задача: Карта метро**

Представь, что ты разрабатываешь приложение навигации по метро. У тебя есть:
- 200 станций
- 300 переходов между станциями
- Пользователь хочет найти кратчайший путь от станции A до станции B

**Как хранить эту информацию?**

```
Вариант 1: Список переходов
[(Пушкинская, Тверская), (Тверская, Чеховская), ...]
→ Проблема: чтобы найти все соседние станции, нужно просмотреть весь список

Вариант 2: Матрица 200×200
matrix[i][j] = 1 если есть переход
→ Проблема: 40,000 ячеек, но только 300 реальных переходов (99.25% пустых)

Вариант 3: Граф — список соседей для каждой станции
Пушкинская → [Тверская, Чеховская]
Тверская → [Пушкинская, Маяковская]
→ Эффективно: храним только реальные связи
```

### Где используются графы?

| Область | Вершины | Рёбра | Пример |
|---------|---------|-------|--------|
| Соцсети | Пользователи | Дружба/подписки | Facebook, Instagram |
| Карты | Локации | Дороги | Google Maps, Яндекс.Карты |
| Интернет | Страницы | Ссылки | PageRank Google |
| Зависимости | Модули/задачи | Требования | npm, gradle, make |
| Биология | Белки | Взаимодействия | Исследования генома |
| Электросети | Узлы | Провода | Энергосистемы |

**Факт:** Google использовал алгоритм PageRank (основанный на графах) для ранжирования страниц. Это сделало их поиск революционно лучше конкурентов в 1998 году.

---

## Что это такое?

### Объяснение для 5-летнего

Представь карту города LEGO:
- **Домики** — это вершины (каждый домик имеет номер)
- **Дорожки** между домиками — это рёбра
- Некоторые дорожки — **односторонние** (можно ехать только в одну сторону)
- Некоторые дорожки **длиннее** других (это веса)

```
    [1]----[2]
     |    / |
     |   /  |
     |  /   |
    [3]----[4]

Домики 1,2,3,4 соединены дорожками.
Из домика 1 можно дойти до любого другого.
```

### Формальное определение

**Граф G = (V, E)** — это:
- **V** (Vertices) — конечное множество вершин
- **E** (Edges) — множество рёбер, где каждое ребро e ∈ E соединяет две вершины

**Типы графов:**

```
НЕОРИЕНТИРОВАННЫЙ              ОРИЕНТИРОВАННЫЙ (Directed)
    1 ─── 2                        1 ──→ 2
    │     │                        ↑     │
    │     │                        │     ↓
    3 ─── 4                        3 ←── 4

Ребро (1,2) = ребро (2,1)      Ребро (1,2) ≠ ребро (2,1)


ВЗВЕШЕННЫЙ                      НЕВЗВЕШЕННЫЙ
    1 ──5── 2                      1 ─── 2
    │       │                      │     │
    3       7                      │     │
    │       │                      │     │
    3 ──2── 4                      3 ─── 4

Рёбра имеют вес (стоимость)    Все рёбра равнозначны
```

**Свойства графа:**

| Свойство | Описание |
|----------|----------|
| Связный (Connected) | Есть путь между любыми двумя вершинами |
| Ациклический (Acyclic) | Нет циклов |
| DAG | Directed Acyclic Graph — ориентированный ациклический граф |
| Степень вершины (Degree) | Количество рёбер, инцидентных вершине |
| Плотный (Dense) | E ≈ V² — много рёбер |
| Разреженный (Sparse) | E << V² — мало рёбер |

---

## Терминология

| Термин | Английский | Определение | Пример |
|--------|------------|-------------|--------|
| Вершина | Vertex/Node | Узел графа | Станция метро |
| Ребро | Edge | Связь между вершинами | Переход между станциями |
| Смежные | Adjacent | Вершины, соединённые ребром | Соседние станции |
| Инцидентные | Incident | Ребро и его концевые вершины | Переход и его станции |
| Степень | Degree | Количество рёбер вершины | Сколько пересадок |
| Путь | Path | Последовательность вершин через рёбра | Маршрут от A до B |
| Цикл | Cycle | Путь, начинающийся и заканчивающийся в одной вершине | Кольцевая линия |
| Компонента связности | Connected Component | Максимальный связный подграф | Отдельная ветка метро |
| DAG | DAG | Directed Acyclic Graph | Граф зависимостей |
| Взвешенный граф | Weighted Graph | Граф с весами на рёбрах | Карта с расстояниями |
| Петля | Self-loop | Ребро из вершины в себя | Ссылка страницы на себя |

---

## Как это работает?

### Представление 1: Adjacency List (Список смежности)

Каждая вершина хранит список своих соседей.

```
Граф:
    0 ─── 1
    │   / │
    │  /  │
    │ /   │
    2 ─── 3

Adjacency List:
┌───────┬──────────────┐
│ Вершина │ Соседи      │
├───────┼──────────────┤
│   0   │ [1, 2]       │
│   1   │ [0, 2, 3]    │
│   2   │ [0, 1, 3]    │
│   3   │ [1, 2]       │
└───────┴──────────────┘

В памяти (HashMap/Array):
graph[0] → LinkedList [1, 2]
graph[1] → LinkedList [0, 2, 3]
graph[2] → LinkedList [0, 1, 3]
graph[3] → LinkedList [1, 2]
```

**Для взвешенного графа:**
```
graph[0] → [(1, 5), (2, 3)]  // (сосед, вес)
graph[1] → [(0, 5), (2, 2), (3, 7)]
```

### Представление 2: Adjacency Matrix (Матрица смежности)

2D массив где `matrix[i][j] = 1` означает наличие ребра.

```
Тот же граф:
    0 ─── 1
    │   / │
    │  /  │
    │ /   │
    2 ─── 3

Adjacency Matrix:
        0   1   2   3
      ┌───┬───┬───┬───┐
    0 │ 0 │ 1 │ 1 │ 0 │
      ├───┼───┼───┼───┤
    1 │ 1 │ 0 │ 1 │ 1 │
      ├───┼───┼───┼───┤
    2 │ 1 │ 1 │ 0 │ 1 │
      ├───┼───┼───┼───┤
    3 │ 0 │ 1 │ 1 │ 0 │
      └───┴───┴───┴───┘

matrix[i][j] = 1 ⟺ есть ребро (i, j)
Для неориентированного графа: matrix симметрична
```

**Для взвешенного графа:**
```
        0   1   2   3
      ┌───┬───┬───┬───┐
    0 │ 0 │ 5 │ 3 │ ∞ │
      ├───┼───┼───┼───┤
    1 │ 5 │ 0 │ 2 │ 7 │
      ...

matrix[i][j] = вес ребра (или ∞ если нет ребра)
```

### Когда что использовать?

```
                     ВЫБОР ПРЕДСТАВЛЕНИЯ
                            │
              ┌─────────────┴─────────────┐
              │                           │
        E близко к V²?              E << V²?
        (Плотный граф)           (Разреженный)
              │                           │
              ▼                           ▼
      ADJACENCY MATRIX              ADJACENCY LIST

      ✓ O(1) проверка ребра         ✓ O(V+E) память
      ✓ Простая реализация          ✓ Быстрый обход соседей
      ✗ O(V²) память                ✗ O(degree) проверка ребра

      Floyd-Warshall                 BFS/DFS
      Мелкие графы                   Социальные сети
      Dense networks                 Web crawling
```

---

## BFS (Breadth-First Search) — Поиск в ширину

### Визуализация

```
Начинаем с вершины 0, ищем все достижимые вершины:

      0 ─── 1 ─── 4
      │     │
      2 ─── 3 ─── 5

Уровень 0: [0]          ← Стартовая вершина
Уровень 1: [1, 2]       ← Соседи 0
Уровень 2: [3, 4]       ← Соседи 1 и 2 (не посещённые)
Уровень 3: [5]          ← Соседи 3 (не посещённые)

BFS исследует граф "волнами" — сначала все на расстоянии 1,
потом все на расстоянии 2, и т.д.
```

### Алгоритм

```
BFS(start):
    1. Создать очередь, добавить start
    2. Пометить start как посещённый
    3. Пока очередь не пуста:
        a. Извлечь вершину v из очереди
        b. Для каждого соседа u вершины v:
           - Если u не посещён:
             * Пометить u как посещённый
             * Добавить u в очередь
```

### Свойства BFS

- **Находит кратчайший путь** в невзвешенном графе
- **Использует очередь (Queue)** — FIFO
- **Время:** O(V + E)
- **Память:** O(V) для visited + O(V) для очереди

---

## DFS (Depth-First Search) — Поиск в глубину

### Визуализация

```
Начинаем с вершины 0:

      0 ─── 1 ─── 4
      │     │
      2 ─── 3 ─── 5

DFS идёт "вглубь" до тупика, затем возвращается:

Шаг 1: 0 → 1 → 3 → 2 (тупик, 0 уже посещён)
Шаг 2: Возврат к 3 → 5 (тупик)
Шаг 3: Возврат к 1 → 4 (тупик)
Шаг 4: Возврат к 0 (все посещены)

Порядок посещения: 0, 1, 3, 2, 5, 4
```

### Алгоритм (рекурсивный)

```
DFS(v, visited):
    1. Пометить v как посещённый
    2. Обработать v
    3. Для каждого соседа u вершины v:
       - Если u не посещён:
         * DFS(u, visited)
```

### Свойства DFS

- **Не гарантирует кратчайший путь**
- **Использует стек** (явный или рекурсия)
- **Время:** O(V + E)
- **Память:** O(V) для visited + O(V) для стека

### BFS vs DFS

| Аспект | BFS | DFS |
|--------|-----|-----|
| Структура данных | Очередь (Queue) | Стек (Stack/рекурсия) |
| Порядок обхода | По уровням | Вглубь |
| Кратчайший путь | Да (невзвешенный) | Нет |
| Память | O(ширина) | O(глубина) |
| Применение | Кратчайший путь, уровни | Циклы, топ. сортировка |

---

## Сложность операций

### Adjacency List vs Matrix

| Операция | Adjacency List | Adjacency Matrix |
|----------|---------------|------------------|
| Память | O(V + E) | O(V²) |
| Добавить ребро | O(1) | O(1) |
| Удалить ребро | O(degree) | O(1) |
| Проверить ребро | O(degree) | O(1) |
| Найти всех соседей | O(degree) | O(V) |
| Обход всего графа | O(V + E) | O(V²) |

### Алгоритмы

| Алгоритм | Время | Память | Применение |
|----------|-------|--------|------------|
| BFS | O(V + E) | O(V) | Кратчайший путь (невзвешенный) |
| DFS | O(V + E) | O(V) | Циклы, связность, топ. сортировка |
| Топологическая сортировка | O(V + E) | O(V) | Зависимости, планирование |
| Dijkstra | O(E log V) | O(V) | Кратчайший путь (положительные веса) |
| Bellman-Ford | O(V × E) | O(V) | Кратчайший путь (любые веса) |
| Floyd-Warshall | O(V³) | O(V²) | Все пары кратчайших путей |
| Union-Find | ≈ O(1) | O(V) | Связность, циклы |
| Kruskal (MST) | O(E log E) | O(V) | Минимальное остовное дерево |
| Prim (MST) | O(E log V) | O(V) | Минимальное остовное дерево |

---

## Реализация

### Kotlin — Adjacency List

```kotlin
/**
 * Граф на основе списка смежности
 *
 * WHY adjacency list: Большинство реальных графов разреженные.
 * Социальная сеть с 1M пользователей: матрица = 10^12 ячеек,
 * но реальных связей ~1000 на пользователя = 10^9.
 */
class Graph(private val n: Int) {
    // WHY MutableList: динамическое добавление соседей
    private val adj: Array<MutableList<Int>> = Array(n) { mutableListOf() }

    /**
     * Добавляет ребро в неориентированный граф
     * WHY обе стороны: u-v означает и v-u
     */
    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)
    }

    /**
     * Добавляет ребро в ориентированный граф
     * WHY только одна сторона: направление имеет значение
     */
    fun addDirectedEdge(from: Int, to: Int) {
        adj[from].add(to)
    }

    /**
     * BFS — поиск в ширину
     *
     * WHY очередь: FIFO гарантирует обход по уровням
     * WHY visited сразу при добавлении в очередь:
     *     избегаем дублирования в очереди
     */
    fun bfs(start: Int): List<Int> {
        val result = mutableListOf<Int>()
        val visited = BooleanArray(n)
        val queue: Queue<Int> = LinkedList()

        queue.offer(start)
        visited[start] = true  // WHY здесь: предотвращает повторное добавление

        while (queue.isNotEmpty()) {
            val node = queue.poll()
            result.add(node)

            for (neighbor in adj[node]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true  // WHY до добавления: критично!
                    queue.offer(neighbor)
                }
            }
        }
        return result
    }

    /**
     * DFS — рекурсивный поиск в глубину
     *
     * WHY рекурсия: естественно выражает "иди вглубь, потом вернись"
     * RISK: StackOverflow на глубоких графах (>10000 уровней)
     */
    fun dfsRecursive(start: Int): List<Int> {
        val result = mutableListOf<Int>()
        val visited = BooleanArray(n)

        fun dfs(node: Int) {
            visited[node] = true
            result.add(node)

            for (neighbor in adj[node]) {
                if (!visited[neighbor]) {
                    dfs(neighbor)
                }
            }
        }

        dfs(start)
        return result
    }

    /**
     * DFS — итеративный (безопасный для больших графов)
     *
     * WHY явный стек: избегаем stack overflow
     * WHY проверка visited после pop: вершина могла быть добавлена несколько раз
     */
    fun dfsIterative(start: Int): List<Int> {
        val result = mutableListOf<Int>()
        val visited = BooleanArray(n)
        val stack = ArrayDeque<Int>()

        stack.push(start)

        while (stack.isNotEmpty()) {
            val node = stack.pop()

            // WHY проверка здесь: вершина могла быть добавлена несколько раз
            if (visited[node]) continue

            visited[node] = true
            result.add(node)

            // WHY reverse: чтобы порядок совпадал с рекурсивным DFS
            for (neighbor in adj[node].reversed()) {
                if (!visited[neighbor]) {
                    stack.push(neighbor)
                }
            }
        }
        return result
    }

    /**
     * BFS для поиска кратчайшего пути
     *
     * WHY BFS а не DFS: BFS гарантирует минимальное количество рёбер
     * WHY parent map: восстановление пути от end к start
     */
    fun shortestPath(start: Int, end: Int): List<Int>? {
        if (start == end) return listOf(start)

        val visited = BooleanArray(n)
        val parent = IntArray(n) { -1 }
        val queue: Queue<Int> = LinkedList()

        queue.offer(start)
        visited[start] = true

        while (queue.isNotEmpty()) {
            val node = queue.poll()

            for (neighbor in adj[node]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true
                    parent[neighbor] = node

                    // WHY раннее завершение: нашли цель
                    if (neighbor == end) {
                        return reconstructPath(parent, start, end)
                    }

                    queue.offer(neighbor)
                }
            }
        }

        return null  // Путь не найден
    }

    private fun reconstructPath(parent: IntArray, start: Int, end: Int): List<Int> {
        val path = mutableListOf<Int>()
        var current = end

        while (current != -1) {
            path.add(current)
            current = parent[current]
        }

        return path.reversed()  // WHY reverse: строили от end к start
    }

    /**
     * Проверка на наличие цикла в неориентированном графе
     *
     * WHY parent tracking: ребро к родителю не считается циклом
     */
    fun hasCycleUndirected(): Boolean {
        val visited = BooleanArray(n)

        // WHY цикл по всем вершинам: граф может быть несвязным
        for (i in 0 until n) {
            if (!visited[i]) {
                if (dfsCycleUndirected(i, -1, visited)) {
                    return true
                }
            }
        }
        return false
    }

    private fun dfsCycleUndirected(node: Int, parent: Int, visited: BooleanArray): Boolean {
        visited[node] = true

        for (neighbor in adj[node]) {
            if (!visited[neighbor]) {
                if (dfsCycleUndirected(neighbor, node, visited)) {
                    return true
                }
            } else if (neighbor != parent) {
                // WHY neighbor != parent: нашли посещённую вершину, которая не родитель = цикл
                return true
            }
        }
        return false
    }

    /**
     * Количество компонент связности
     *
     * WHY: определяет сколько "островов" в графе
     */
    fun countConnectedComponents(): Int {
        val visited = BooleanArray(n)
        var count = 0

        for (i in 0 until n) {
            if (!visited[i]) {
                dfsMarkComponent(i, visited)
                count++
            }
        }
        return count
    }

    private fun dfsMarkComponent(node: Int, visited: BooleanArray) {
        visited[node] = true
        for (neighbor in adj[node]) {
            if (!visited[neighbor]) {
                dfsMarkComponent(neighbor, visited)
            }
        }
    }
}
```

### Kotlin — Взвешенный граф

```kotlin
/**
 * Взвешенный граф для алгоритмов кратчайшего пути
 */
class WeightedGraph(private val n: Int) {
    // WHY Pair: храним (сосед, вес) вместо просто соседа
    private val adj: Array<MutableList<Pair<Int, Int>>> = Array(n) { mutableListOf() }

    fun addEdge(u: Int, v: Int, weight: Int) {
        adj[u].add(v to weight)
        adj[v].add(u to weight)
    }

    fun addDirectedEdge(from: Int, to: Int, weight: Int) {
        adj[from].add(to to weight)
    }

    /**
     * Алгоритм Дейкстры — кратчайший путь от одной вершины
     *
     * WHY PriorityQueue: всегда берём вершину с минимальным расстоянием
     * WHY только положительные веса: отрицательные ломают жадный подход
     *
     * Time: O(E log V) с PriorityQueue
     */
    fun dijkstra(start: Int): IntArray {
        val dist = IntArray(n) { Int.MAX_VALUE }
        dist[start] = 0

        // WHY PriorityQueue по расстоянию: жадно берём ближайшую вершину
        val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.second })
        pq.offer(start to 0)

        while (pq.isNotEmpty()) {
            val (node, d) = pq.poll()

            // WHY эта проверка: вершина могла быть обновлена после добавления в очередь
            if (d > dist[node]) continue

            for ((neighbor, weight) in adj[node]) {
                val newDist = dist[node] + weight

                if (newDist < dist[neighbor]) {
                    dist[neighbor] = newDist
                    pq.offer(neighbor to newDist)
                }
            }
        }

        return dist
    }
}
```

### Kotlin — Топологическая сортировка

```kotlin
/**
 * Топологическая сортировка для DAG (Directed Acyclic Graph)
 *
 * WHY: упорядочивает вершины так, что все зависимости идут перед зависимыми
 * Пример: порядок компиляции модулей, расписание курсов
 */
class TopologicalSort(private val n: Int) {
    private val adj: Array<MutableList<Int>> = Array(n) { mutableListOf() }

    fun addEdge(from: Int, to: Int) {
        adj[from].add(to)
    }

    /**
     * Топологическая сортировка через DFS
     *
     * WHY post-order + reverse: вершина добавляется после всех её зависимостей
     * Возвращает null если есть цикл
     */
    fun topologicalSort(): List<Int>? {
        val visited = BooleanArray(n)
        // onStack отслеживает вершины в ТЕКУЩЕМ пути DFS
        // Это нужно для обнаружения циклов!
        // visited = "вершина когда-либо посещалась"
        // onStack = "вершина в текущей цепочке рекурсии"
        val onStack = BooleanArray(n)
        val result = ArrayDeque<Int>()

        fun dfs(node: Int): Boolean {
            visited[node] = true
            // Помечаем: вершина сейчас в текущем пути DFS
            onStack[node] = true

            for (neighbor in adj[node]) {
                if (onStack[neighbor]) {
                    // Если сосед уже в текущем пути — это back edge!
                    // Back edge означает цикл в графе.
                    // В DAG (directed acyclic graph) не должно быть back edges.
                    return false
                }
                if (!visited[neighbor]) {
                    if (!dfs(neighbor)) return false
                }
            }

            onStack[node] = false
            // addFirst: добавляем в НАЧАЛО результата
            // Топ-сорт строится "с конца" — сначала добавляются
            // вершины без исходящих рёбер (листья)
            result.addFirst(node)
            return true
        }

        for (i in 0 until n) {
            if (!visited[i]) {
                if (!dfs(i)) return null  // Цикл обнаружен
            }
        }

        return result.toList()
    }

    /**
     * Алгоритм Кана — топологическая сортировка через BFS
     *
     * WHY in-degree: вершина без входящих рёбер может быть обработана первой
     * WHY BFS: обрабатываем "готовые" вершины по мере появления
     */
    fun kahnTopologicalSort(): List<Int>? {
        val inDegree = IntArray(n)

        // Считаем входящие степени
        for (u in 0 until n) {
            for (v in adj[u]) {
                inDegree[v]++
            }
        }

        // WHY очередь: все вершины с inDegree=0 можно обработать в любом порядке
        val queue: Queue<Int> = LinkedList()
        for (i in 0 until n) {
            if (inDegree[i] == 0) {
                queue.offer(i)
            }
        }

        val result = mutableListOf<Int>()

        while (queue.isNotEmpty()) {
            val node = queue.poll()
            result.add(node)

            for (neighbor in adj[node]) {
                inDegree[neighbor]--
                if (inDegree[neighbor] == 0) {
                    // Все "зависимости" этой вершины обработаны!
                    // inDegree == 0 означает: все входящие рёбра "удалены"
                    // Теперь вершину можно добавить в результат
                    queue.offer(neighbor)
                }
            }
        }

        // Проверка на цикл: если обработали не все вершины — есть цикл
        // При наличии цикла inDegree никогда не станет 0 для вершин в цикле
        return if (result.size == n) result else null
    }
}
```

### Java — Adjacency List

```java
/**
 * Граф на основе списка смежности (Java версия)
 */
public class Graph {
    private final int n;
    private final List<List<Integer>> adj;

    public Graph(int n) {
        this.n = n;
        this.adj = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
        }
    }

    public void addEdge(int u, int v) {
        adj.get(u).add(v);
        adj.get(v).add(u);
    }

    /**
     * BFS с поиском кратчайшего пути
     */
    public List<Integer> bfs(int start) {
        List<Integer> result = new ArrayList<>();
        boolean[] visited = new boolean[n];
        Queue<Integer> queue = new LinkedList<>();

        queue.offer(start);
        visited[start] = true;

        while (!queue.isEmpty()) {
            int node = queue.poll();
            result.add(node);

            for (int neighbor : adj.get(node)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.offer(neighbor);
                }
            }
        }

        return result;
    }

    /**
     * DFS рекурсивный
     */
    public List<Integer> dfs(int start) {
        List<Integer> result = new ArrayList<>();
        boolean[] visited = new boolean[n];
        dfsHelper(start, visited, result);
        return result;
    }

    private void dfsHelper(int node, boolean[] visited, List<Integer> result) {
        visited[node] = true;
        result.add(node);

        for (int neighbor : adj.get(node)) {
            if (!visited[neighbor]) {
                dfsHelper(neighbor, visited, result);
            }
        }
    }
}
```

### Python — Компактная реализация

```python
from collections import deque, defaultdict
from typing import List, Optional, Set

class Graph:
    """
    Граф на основе списка смежности (Python версия)
    WHY defaultdict: автоматически создаёт пустой список для новой вершины
    """
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u: int, v: int) -> None:
        self.adj[u].append(v)
        self.adj[v].append(u)

    def add_directed_edge(self, from_node: int, to_node: int) -> None:
        self.adj[from_node].append(to_node)

    def bfs(self, start: int) -> List[int]:
        """BFS — поиск в ширину"""
        result = []
        visited = {start}
        queue = deque([start])

        while queue:
            node = queue.popleft()
            result.append(node)

            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return result

    def dfs(self, start: int) -> List[int]:
        """DFS — рекурсивный поиск в глубину"""
        result = []
        visited = set()

        def dfs_helper(node: int) -> None:
            visited.add(node)
            result.append(node)

            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    dfs_helper(neighbor)

        dfs_helper(start)
        return result

    def shortest_path(self, start: int, end: int) -> Optional[List[int]]:
        """Кратчайший путь через BFS"""
        if start == end:
            return [start]

        visited = {start}
        parent = {start: None}
        queue = deque([start])

        while queue:
            node = queue.popleft()

            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = node

                    if neighbor == end:
                        # Восстанавливаем путь
                        path = []
                        current = end
                        while current is not None:
                            path.append(current)
                            current = parent[current]
                        return path[::-1]

                    queue.append(neighbor)

        return None  # Путь не найден
```

---

## Распространённые ошибки

### 1. Забыли отметить вершину как посещённую

```kotlin
// НЕПРАВИЛЬНО: бесконечный цикл в графе с циклами
fun bfsBroken(start: Int) {
    val queue: Queue<Int> = LinkedList()
    queue.offer(start)

    while (queue.isNotEmpty()) {
        val node = queue.poll()
        println(node)

        for (neighbor in adj[node]) {
            queue.offer(neighbor)  // BUG: добавляем одни и те же вершины
        }
    }
}

// ПРАВИЛЬНО: отмечаем ДО добавления в очередь
fun bfsCorrect(start: Int) {
    val visited = mutableSetOf<Int>()
    val queue: Queue<Int> = LinkedList()

    queue.offer(start)
    visited.add(start)  // ВАЖНО: сразу отмечаем

    while (queue.isNotEmpty()) {
        val node = queue.poll()
        println(node)

        for (neighbor in adj[node]) {
            if (neighbor !in visited) {
                visited.add(neighbor)  // ВАЖНО: до добавления в очередь
                queue.offer(neighbor)
            }
        }
    }
}
```

### 2. Не обработали несвязный граф

```kotlin
// НЕПРАВИЛЬНО: обходим только одну компоненту
fun traverseBroken(graph: List<List<Int>>) {
    val visited = BooleanArray(graph.size)
    dfs(0, visited, graph)  // Начинаем только с 0
}

// ПРАВИЛЬНО: запускаем DFS от каждой непосещённой вершины
fun traverseCorrect(graph: List<List<Int>>) {
    val visited = BooleanArray(graph.size)

    for (i in graph.indices) {
        if (!visited[i]) {
            dfs(i, visited, graph)  // Новая компонента
        }
    }
}
```

### 3. Перепутали направление рёбер

```kotlin
// НЕПРАВИЛЬНО: для ориентированного графа добавили обратное ребро
fun buildGraphBroken(edges: List<Pair<Int, Int>>): List<MutableList<Int>> {
    val graph = List(n) { mutableListOf<Int>() }

    for ((u, v) in edges) {
        graph[u].add(v)
        graph[v].add(u)  // BUG: это для неориентированного графа!
    }

    return graph
}

// ПРАВИЛЬНО: уважаем направление
fun buildDirectedGraph(edges: List<Pair<Int, Int>>): List<MutableList<Int>> {
    val graph = List(n) { mutableListOf<Int>() }

    for ((u, v) in edges) {
        graph[u].add(v)  // Только в одну сторону
    }

    return graph
}
```

### 4. BFS: отметили visited после извлечения из очереди

```kotlin
// НЕПРАВИЛЬНО: вершина может быть добавлена несколько раз
fun bfsBroken(start: Int) {
    val visited = mutableSetOf<Int>()
    val queue: Queue<Int> = LinkedList()
    queue.offer(start)

    while (queue.isNotEmpty()) {
        val node = queue.poll()
        if (node in visited) continue  // Поздно проверять!
        visited.add(node)  // BUG: слишком поздно

        for (neighbor in adj[node]) {
            if (neighbor !in visited) {
                queue.offer(neighbor)  // Может добавиться несколько раз
            }
        }
    }
}

// ПРАВИЛЬНО: отмечаем при добавлении в очередь
fun bfsCorrect(start: Int) {
    val visited = mutableSetOf(start)  // Сразу отмечаем start
    val queue: Queue<Int> = LinkedList()
    queue.offer(start)

    while (queue.isNotEmpty()) {
        val node = queue.poll()

        for (neighbor in adj[node]) {
            if (neighbor !in visited) {
                visited.add(neighbor)  // ДО добавления в очередь
                queue.offer(neighbor)
            }
        }
    }
}
```

### 5. Использовали рекурсивный DFS на большом графе

```kotlin
// ОПАСНО: может вызвать StackOverflowError
fun dfsBroken(node: Int, visited: MutableSet<Int>) {
    visited.add(node)
    for (neighbor in adj[node]) {
        if (neighbor !in visited) {
            dfsBroken(neighbor, visited)  // Глубокая рекурсия!
        }
    }
}

// БЕЗОПАСНО: итеративный DFS с явным стеком
fun dfsIterative(start: Int): Set<Int> {
    val visited = mutableSetOf<Int>()
    val stack = ArrayDeque<Int>()
    stack.push(start)

    while (stack.isNotEmpty()) {
        val node = stack.pop()
        if (node in visited) continue
        visited.add(node)

        for (neighbor in adj[node]) {
            if (neighbor !in visited) {
                stack.push(neighbor)
            }
        }
    }

    return visited
}
```

---

## Когда использовать?

### Выбор представления графа

```
                    ТВОЙ ГРАФ
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   E близко к V²?   E << V²?      Часто проверяешь
   (> V²/2 рёбер)  (мало рёбер)   наличие ребра?
        │               │               │
        ▼               ▼               ▼
  ADJACENCY MATRIX  ADJACENCY LIST  ADJACENCY MATRIX
                                   (или HashSet в list)
```

### Выбор алгоритма обхода

| Задача | Алгоритм | Почему |
|--------|----------|--------|
| Кратчайший путь (невзвешенный) | BFS | Обходит по уровням |
| Кратчайший путь (взвешенный, ≥0) | Dijkstra | Жадно берёт минимум |
| Кратчайший путь (отриц. веса) | Bellman-Ford | Обрабатывает отрицательные |
| Все пары кратчайших путей | Floyd-Warshall | Оптимально для плотных |
| Обнаружение цикла | DFS | Отслеживает back edges |
| Топологическая сортировка | DFS или Kahn | Зависимости |
| Связность | DFS/BFS/Union-Find | Любой подходит |
| Компоненты связности | DFS | Простая реализация |
| Минимальное остовное дерево | Kruskal/Prim | Kruskal для разреженных |

### Сравнение с другими структурами

| Структура | Преимущества | Недостатки | Когда использовать |
|-----------|-------------|------------|-------------------|
| Граф | Произвольные связи | Сложнее деревьев | Сети, зависимости |
| Дерево | Иерархия, нет циклов | Только один путь | Файловая система, DOM |
| Список | Линейный доступ | Нет связей между элементами | Последовательности |
| Hash Map | O(1) lookup | Нет связей | Ключ-значение |

---

## Практика

### Концептуальные вопросы

1. **Q:** Почему BFS гарантирует кратчайший путь в невзвешенном графе, а DFS — нет?

   **A:** BFS обходит граф "волнами" — сначала все вершины на расстоянии 1, потом на расстоянии 2, и т.д. Когда BFS достигает вершины, это происходит по кратчайшему пути. DFS идёт вглубь и может найти длинный путь первым.

2. **Q:** Когда использовать итеративный DFS вместо рекурсивного?

   **A:** Когда граф может быть очень глубоким (>10000 вершин в цепочке). Рекурсия использует системный стек, который ограничен (~1-10 MB). Явный стек использует heap, который значительно больше.

3. **Q:** Как определить, является ли граф деревом?

   **A:** Граф с V вершинами — дерево тогда и только тогда, когда:
   - Он связен (одна компонента связности)
   - Имеет ровно V-1 рёбер
   - Не содержит циклов (любые 2 условия из 3 достаточны)

4. **Q:** Почему для Dijkstra нельзя использовать отрицательные веса?

   **A:** Dijkstra — жадный алгоритм. Он помечает вершину как "обработанную" после нахождения минимального пути к ней. С отрицательными весами может оказаться, что есть более короткий путь через уже обработанную вершину.

5. **Q:** В чём разница между связным и сильно связным графом?

   **A:** Связный — для неориентированных графов (есть путь между любыми вершинами). Сильно связный — для ориентированных (есть путь в обе стороны между любыми вершинами).

### LeetCode задачи

#### Easy

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 733 | [Flood Fill](https://leetcode.com/problems/flood-fill/) | BFS/DFS от стартовой точки |
| 997 | [Find the Town Judge](https://leetcode.com/problems/find-the-town-judge/) | In-degree = N-1, Out-degree = 0 |
| 1971 | [Find if Path Exists](https://leetcode.com/problems/find-if-path-exists-in-graph/) | BFS/DFS или Union-Find |

#### Medium

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 200 | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | Подсчёт компонент через DFS/BFS |
| 207 | [Course Schedule](https://leetcode.com/problems/course-schedule/) | Cycle detection в directed graph |
| 210 | [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) | Топологическая сортировка |
| 133 | [Clone Graph](https://leetcode.com/problems/clone-graph/) | BFS/DFS + HashMap для копий |
| 547 | [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | Connected components |
| 785 | [Is Graph Bipartite?](https://leetcode.com/problems/is-graph-bipartite/) | BFS с 2-раскраской |
| 743 | [Network Delay Time](https://leetcode.com/problems/network-delay-time/) | Dijkstra |
| 994 | [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Multi-source BFS |
| 841 | [Keys and Rooms](https://leetcode.com/problems/keys-and-rooms/) | DFS reachability |
| 1091 | [Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | BFS с 8 направлениями |

#### Hard

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 127 | [Word Ladder](https://leetcode.com/problems/word-ladder/) | BFS на implicit graph |
| 269 | [Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) | Topological sort |
| 332 | [Reconstruct Itinerary](https://leetcode.com/problems/reconstruct-itinerary/) | Hierholzer (Eulerian path) |
| 1192 | [Critical Connections](https://leetcode.com/problems/critical-connections-in-a-network/) | Tarjan (bridges) |

---

## Связанные темы

### Prerequisites (нужно знать перед графами)

- [[arrays]] — основа для представления графа
- [[hash-tables]] — HashMap для adjacency list
- [[queues]] — для BFS
- [[stacks]] — для итеративного DFS
- [[recursion]] — для рекурсивного DFS

### Что изучать после графов

- [[trees-binary]] — частный случай графа (связный ациклический)
- [[union-find-pattern]] — эффективная проверка связности
- [[dfs-bfs-patterns]] — паттерны решения задач
- [[topological-sort-pattern]] — упорядочивание зависимостей
- [[shortest-paths]] — Dijkstra, Bellman-Ford подробно
- [[minimum-spanning-tree]] — Kruskal, Prim
- [[graph-advanced]] — SCCs, bridges, articulation points

### Алгоритмы, основанные на графах

- Shortest path: Dijkstra, Bellman-Ford, Floyd-Warshall
- MST: Kruskal, Prim
- Connectivity: Union-Find, Tarjan (SCCs)
- Flow: Ford-Fulkerson, Edmonds-Karp

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Adjacency matrix лучше" | Matrix O(V²) память. **Adjacency list** O(V+E) — лучше для sparse графов |
| "DFS и BFS дают одинаковый результат" | DFS не даёт **shortest path**. BFS гарантирует shortest в unweighted |
| "Directed и undirected — почти одинаково" | **Разная семантика**: cycle detection, SCCs только для directed. Edge добавляется дважды для undirected |
| "Union-Find = DFS для компонент" | Union-Find **амортизированно O(α(n)) ≈ O(1)**. DFS — O(V+E) каждый запрос |
| "Dijkstra работает с отрицательными весами" | **Нет!** Для отрицательных весов нужен Bellman-Ford. Dijkstra может дать неправильный ответ |

---

## CS-фундамент

| CS-концепция | Применение в Graphs |
|--------------|---------------------|
| **Graph Representation** | Adjacency List O(V+E), Adjacency Matrix O(V²), Edge List O(E) |
| **Graph Traversal** | DFS (глубина), BFS (ширина). Основа всех graph алгоритмов |
| **Connectivity** | Union-Find для dynamic connectivity. DFS/BFS для static |
| **Shortest Path** | BFS (unweighted), Dijkstra (non-negative), Bellman-Ford (any weights) |
| **Topological Sort** | DFS postorder reverse. Только для DAG. Dependency resolution |

---

## Источники

1. [GeeksforGeeks — Graph Representations](https://www.geeksforgeeks.org/dsa/graph-and-its-representations/)
2. [Tech Interview Handbook — Graph](https://www.techinterviewhandbook.org/algorithms/graph/)
3. [LeetCode Graph Study Guide](https://leetcode.com/discuss/study-guide/1326900/graph-algorithms-problems-to-practice)
4. [Baeldung — Dijkstra vs Bellman-Ford](https://www.baeldung.com/cs/dijkstra-vs-bellman-ford)
5. [CP-Algorithms — Disjoint Set Union](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
6. [USACO Guide — Graph Traversal](https://usaco.guide/silver/graph-traversal)
7. [Kodeco — Graphs in Kotlin](https://www.kodeco.com/books/data-structures-algorithms-in-kotlin/v1.0/chapters/19-graphs)
8. Research: [2025-12-29-graphs-data-structure.md](../../docs/research/2025-12-29-graphs-data-structure.md)

---

*Обновлено: 2026-01-06 — добавлены педагогические секции (интуиция графов, типичные ошибки BFS/DFS, 5 ментальных моделей)*

---

[[trees-binary|← Binary Trees]] | [[cs-fundamentals-overview|CS Fundamentals MOC]] | [[heaps-priority-queues|Heaps →]]
