# Topological Sort Pattern

---
title: "Topological Sort Pattern"
created: 2025-12-29
updated: 2026-01-06
type: deep-dive
status: complete
difficulty: intermediate
confidence: high
cs-foundations:
  - directed-acyclic-graph
  - topological-ordering
  - indegree-outdegree
  - dependency-resolution
  - cycle-detection
prerequisites:
  - "[[graphs]]"
  - "[[dfs-bfs-patterns]]"
  - "[[stacks-queues]]"
related:
  - "[[dfs-bfs-patterns]]"
  - "[[dp-patterns]]"
tags:
  - pattern
  - topological-sort
  - dag
  - dependency
  - interview
---

## TL;DR

Topological Sort упорядочивает вершины DAG так, что для каждого ребра u→v вершина u идёт перед v. **Два подхода: Kahn's (BFS + indegree) и DFS (reverse postorder)**. Определяет наличие циклов: если отсортировано меньше вершин, чем в графе — цикл есть. Оптимально для: зависимостей курсов, build систем, планировщиков задач.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Сборка мебели IKEA

Представь, что ты собираешь шкаф из IKEA. В инструкции 20 шагов, и некоторые из них зависят друг от друга:

```
Шаги сборки шкафа:
┌─────────────────────────────────────────────────────────────┐
│  [Ножки]──────┐                                             │
│               ▼                                             │
│  [Днище]────→[Соединить днище с ножками]                    │
│                          │                                  │
│  [Боковины]──────────────┼──→[Прикрепить боковины]          │
│                          │              │                   │
│  [Полки]─────────────────┼──────────────┼──→[Вставить полки]│
│                          │              │          │        │
│  [Задняя стенка]─────────┼──────────────┼──────────┼──→[Дверцы]
│                          │              │          │        │
│                          └──────────────┴──────────┴───→[ГОТОВО]
└─────────────────────────────────────────────────────────────┘
```

**Вопрос:** В каком порядке делать шаги, чтобы ничего не пришлось переделывать?

**Ответ:** Topological Sort! Он находит такой порядок, что каждый шаг выполняется только после всех его "предшественников".

**Ключевой инсайт:** Нельзя прикрепить полки, если боковины ещё не стоят. Нельзя установить дверцы, если корпус не собран.

---

### Аналогия 2: Университетские курсы

```
Программа обучения Computer Science:

Семестр 1:        Семестр 2:        Семестр 3:        Семестр 4:
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Матан   │──┬──→│ Линейная │──┬──→│   ML     │──┬──→│ Deep     │
│          │  │   │ алгебра  │  │   │          │  │   │ Learning │
└──────────┘  │   └──────────┘  │   └──────────┘  │   └──────────┘
              │                 │                 │
┌──────────┐  │   ┌──────────┐  │   ┌──────────┐  │
│  Python  │──┴──→│ Структуры│──┴──→│Алгоритмы │──┘
│          │      │ данных   │      │          │
└──────────┘      └──────────┘      └──────────┘

Зависимости (prerequisites):
- Линейная алгебра: требует Матан
- Структуры данных: требует Python
- ML: требует Линейная алгебра + Структуры данных
- Алгоритмы: требует Структуры данных
- Deep Learning: требует ML + Алгоритмы
```

**Вопрос:** В каком порядке проходить курсы?

Один правильный порядок: Матан → Python → Линейная → Структуры → ML → Алгоритмы → Deep Learning

Другой правильный порядок: Python → Матан → Структуры → Линейная → Алгоритмы → ML → Deep Learning

**Ключевой инсайт:** Может быть много правильных порядков! Toposort даёт любой из них.

---

### Аналогия 3: Рецепт борща

```
Приготовление борща — граф зависимостей:

[Почистить свёклу]──┐
                    ▼
[Нарезать свёклу]──→[Варить свёклу 40 мин]──┐
                                             │
[Почистить картошку]──┐                      │
                      ▼                      │
[Нарезать картошку]───┐                      │
                      │                      │
[Нарезать капусту]────┼──────────────────────┼──→[Собрать в кастрюле]
                      │                      │            │
[Пассировать лук]─────┤                      │            ▼
                      │                      │       [Варить 20 мин]
[Пассировать морковь]─┘                      │            │
                                             │            ▼
[Сварить бульон]─────────────────────────────┴──────→[ПОДАВАТЬ]
```

**Ключевой инсайт:**
- Нельзя нарезать свёклу, не почистив её
- Можно параллельно готовить бульон и овощи
- Финальная сборка зависит от всего

---

### Численный пример: Kahn's Algorithm пошагово

```
Граф курсов (5 курсов, 6 зависимостей):

    0 ────→ 2 ────→ 3
    │       ↑       ↑
    │       │       │
    └──→ 1 ─┴───────┘
         │
         └────→ 4

Рёбра: 0→1, 0→2, 1→2, 1→3, 1→4, 2→3

Шаг 1: Подсчитаем indegree (сколько стрелок ВХОДИТ в вершину)

  Вершина:   0   1   2   3   4
  indegree: [0] [1] [2] [2] [1]
            ↑
            Нет входящих!

Шаг 2: Кладём вершины с indegree=0 в очередь

  queue = [0]
  result = []

Шаг 3: Обрабатываем очередь

  Итерация 1:
    Извлекаем 0, result = [0]
    Соседи 0: вершины 1 и 2
    Уменьшаем их indegree: [0, 0, 1, 2, 1]
                               ↑
                               Стал 0!
    Добавляем 1 в очередь: queue = [1]

  Итерация 2:
    Извлекаем 1, result = [0, 1]
    Соседи 1: вершины 2, 3, 4
    Уменьшаем: [0, 0, 0, 1, 0]
                      ↑     ↑
                      Оба стали 0!
    queue = [2, 4]

  Итерация 3:
    Извлекаем 2, result = [0, 1, 2]
    Соседи 2: вершина 3
    Уменьшаем: [0, 0, 0, 0, 0]
    queue = [4, 3]

  Итерация 4:
    Извлекаем 4, result = [0, 1, 2, 4]
    Соседи 4: нет
    queue = [3]

  Итерация 5:
    Извлекаем 3, result = [0, 1, 2, 4, 3]
    queue = []

Шаг 4: Проверка

  result.size = 5 = количество вершин
  → Цикла нет, порядок найден!

  Финальный порядок: [0, 1, 2, 4, 3]

  Проверка: для каждого ребра u→v, u стоит перед v? ✓
    0→1: 0 перед 1 ✓
    0→2: 0 перед 2 ✓
    1→2: 1 перед 2 ✓
    1→3: 1 перед 3 ✓
    1→4: 1 перед 4 ✓
    2→3: 2 перед 3 ✓
```

---

### Что происходит при цикле?

```
Граф с циклом:

    0 ────→ 1
    ↑       │
    │       ▼
    └────── 2

Рёбра: 0→1, 1→2, 2→0 (ЦИКЛ!)

Подсчёт indegree:
  Вершина:   0   1   2
  indegree: [1] [1] [1]
            ↑   ↑   ↑
            Все > 0!

Начальная очередь: queue = [] (пустая!)

Никто не имеет indegree = 0
→ Нечего обрабатывать
→ result.size = 0 ≠ 3
→ ЦИКЛ ОБНАРУЖЕН!

Интуиция: Это как три курса, где:
- A требует B
- B требует C
- C требует A
→ Невозможно начать!
```

---

## Часть 2: Почему это сложно

### Типичные ошибки студентов

#### Ошибка 1: Перепутано направление рёбер

```
Задача: prerequisites = [[1,0], [2,1]]
Означает: чтобы взять курс 1, нужен курс 0
          чтобы взять курс 2, нужен курс 1

❌ НЕПРАВИЛЬНАЯ интерпретация:
   "1 → 0" и "2 → 1"
   Это даёт ОБРАТНЫЙ порядок!

✅ ПРАВИЛЬНАЯ интерпретация:
   [course, prereq] означает prereq → course
   "0 → 1" и "1 → 2"

Правильный порядок: 0, 1, 2

СИМПТОМ: Тесты падают, результат "в обратном порядке"
РЕШЕНИЕ: Всегда явно комментируй направление рёбер в коде
```

#### Ошибка 2: Забыли проверить на цикл

```kotlin
// ❌ НЕПРАВИЛЬНО
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    result.add(node)
    // ... обработка
}
return result.toIntArray()  // Может вернуть неполный результат!

// ✅ ПРАВИЛЬНО
while (queue.isNotEmpty()) { ... }
// ОБЯЗАТЕЛЬНО проверяем, все ли вершины обработаны
return if (result.size == numCourses) result.toIntArray() else intArrayOf()

СИМПТОМ: На тестах с циклами возвращается частичный результат
РЕШЕНИЕ: Всегда проверяй result.size == numVertices
```

#### Ошибка 3: Использование boolean visited вместо трёх состояний

```kotlin
// ❌ НЕПРАВИЛЬНО — не детектит циклы в DFS!
val visited = BooleanArray(n)
fun dfs(node: Int) {
    if (visited[node]) return  // Это не детектит back edge!
    visited[node] = true
    for (next in graph[node]) dfs(next)
    result.add(node)
}

// ✅ ПРАВИЛЬНО — три состояния
enum class State { WHITE, GRAY, BLACK }
val state = Array(n) { State.WHITE }
fun dfs(node: Int): Boolean {
    if (state[node] == GRAY) return false  // Back edge = цикл!
    if (state[node] == BLACK) return true
    state[node] = GRAY
    for (next in graph[node]) {
        if (!dfs(next)) return false
    }
    state[node] = BLACK
    result.add(node)
    return true
}

СИМПТОМ: DFS не находит циклы, возвращает неправильный порядок
РЕШЕНИЕ: Используй три состояния: WHITE (не посещён), GRAY (в текущем пути), BLACK (завершён)
```

#### Ошибка 4: Забыли развернуть результат DFS

```kotlin
// DFS добавляет вершины в POSTORDER — после обработки всех соседей
// Это даёт ОБРАТНЫЙ топологический порядок!

// ❌ НЕПРАВИЛЬНО
fun dfs(node: Int) {
    // ...
    result.add(node)  // Postorder
}
return result.toIntArray()  // Обратный порядок!

// ✅ ПРАВИЛЬНО
return result.reversed().toIntArray()  // Или result.asReversed()

СИМПТОМ: Зависимости идут в неправильном порядке
РЕШЕНИЕ: Всегда реверсируй результат DFS toposort
```

#### Ошибка 5: Граф не связный — не обработали все компоненты

```kotlin
// ❌ НЕПРАВИЛЬНО
dfs(0)  // Запустили только от вершины 0
return result.reversed().toIntArray()

// Но граф может быть несвязным!
// Пример: 0→1, 2→3 — две отдельные компоненты

// ✅ ПРАВИЛЬНО
for (i in 0 until numCourses) {
    if (state[i] == WHITE) {
        if (!dfs(i)) return intArrayOf()  // Цикл
    }
}
return result.reversed().toIntArray()

СИМПТОМ: Часть вершин пропущена
РЕШЕНИЕ: Запускай DFS от каждой непосещённой вершины
```

#### Ошибка 6: Путаница с терминами Source vs Sink

```
Source (источник): indegree = 0, нет входящих рёбер
Sink (сток): outdegree = 0, нет исходящих рёбер

В Kahn's algorithm мы начинаем с SOURCE (indegree = 0)
— это вершины БЕЗ зависимостей, которые можно делать первыми

❌ НЕПРАВИЛЬНО: начинать с вершин с outdegree = 0
✅ ПРАВИЛЬНО: начинать с вершин с indegree = 0

СИМПТОМ: Алгоритм "застревает" сразу или даёт обратный порядок
РЕШЕНИЕ: Запомни — SOURCE (indegree=0) = можно делать ПЕРВЫМ
```

---

## Часть 3: Ментальные модели

### Модель 1: "Снимаем слои луковицы" (Kahn's)

```
Представь граф как луковицу:

        ┌───────────────────┐
        │     ┌───────┐     │
        │     │ ┌───┐ │     │
        │     │ │ 4 │ │     │
        │     │ └───┘ │     │
        │  2  │   3   │  5  │
        │     └───────┘     │
        │         1         │
        └───────────────────┘

Внешний слой: вершины с indegree = 0 (нет зависимостей)
Снимаем слой → уменьшаем indegree соседей → открывается следующий слой

Порядок снятия слоёв = топологический порядок

Применение: Parallel Courses — минимум семестров = количество слоёв
```

### Модель 2: "Обратный порядок завершения" (DFS)

```
DFS как исследователь:

1. Входит в комнату (WHITE → GRAY)
2. Исследует все двери (соседи)
3. Возвращается и отмечает "done" (GRAY → BLACK)
4. Записывает комнату в дневник

Дневник записывается от конца к началу!
Те, кто зависит от других — записываются первыми (в конце дневника)
Те, от кого зависят — записываются последними (в начале дневника)

Поэтому нужен reverse — дневник "с конца"
```

### Модель 3: "Игра в падающие домино"

```
Topological order = порядок падения домино

  1     2     3     4     5
  ▼     ▼     ▼     ▼     ▼
┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
│   │→│   │→│   │→│   │→│   │
└───┘ └───┘ └───┘ └───┘ └───┘

Толкаем домино 1 → оно роняет 2 → роняет 3 → ...

Kahn's: находим домино, которое никто не толкает (indegree=0)
         → это первое в цепочке

DFS: записываем, когда домино упало (postorder)
     → последнее упавшее было толкнуто первым
     → reverse даёт порядок толкания
```

### Модель 4: "Зависимости как долги"

```
Каждое ребро u → v означает: "v должен u"
indegree[v] = сколько долгов у v

Kahn's algorithm:
1. Находим тех, кто никому не должен (indegree = 0) — они могут "уйти"
2. Когда кто-то уходит, долги ему прощаются (indegree соседей--)
3. Если появились новые люди без долгов — они тоже могут уйти

Цикл = круговой долг: A должен B, B должен C, C должен A
       → никто не может уйти первым!
```

### Модель 5: "Сборочный конвейер"

```
Автомобильный завод:

Станция 1: Шасси ────┐
                     ├──→ Станция 4: Сборка кузова ──┐
Станция 2: Рама  ────┘                               │
                                                     ├──→ Готово!
Станция 3: Двигатель ─────────────────────────────────┘

Правила:
- Станция 4 не может начать, пока Станции 1 и 2 не закончат
- Финальная сборка ждёт Станции 3 и 4

indegree = количество "входящих конвейеров"
Станция готова к работе, когда все входящие конвейеры доставили детали

Kahn's: обрабатываем станции, готовые к работе
        → уведомляем следующие станции
        → если они тоже готовы — обрабатываем их
```

---

## Зачем это нужно?

**Реальная проблема:**

Университет с 10,000 курсов и prerequisites. Студенту нужно пройти все курсы в правильном порядке. Граф зависимостей может иметь циклы (ошибка в данных). Topological Sort: найти порядок за O(V+E) или обнаружить цикл.

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| Образование | Course scheduling | Coursera prerequisites |
| Build системы | Dependency resolution | Maven, Gradle, npm |
| Компиляторы | Instruction scheduling | Порядок операций |
| Базы данных | Query optimization | Порядок JOIN операций |
| CI/CD | Pipeline stages | Jenkins, GitHub Actions |
| Spreadsheets | Cell recalculation | Excel формулы |

**Статистика:**
- 10-15% задач на интервью связаны с графами
- Course Schedule — одна из top-20 задач LeetCode
- Критически важен для понимания DAG и зависимостей

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Графы** | Топологическая сортировка работает на DAG | [[graphs]] |
| **BFS** | Kahn's algorithm использует BFS | [[dfs-bfs-patterns]] |
| **DFS** | Альтернативный подход через postorder | [[dfs-bfs-patterns]] |
| **Queue** | Для Kahn's algorithm | [[stacks-queues]] |
| **CS: Directed Graph** | Рёбра имеют направление | Теория графов |
| **CS: Indegree/Outdegree** | Количество входящих/исходящих рёбер | Теория графов |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что ты одеваешься утром. Нельзя надеть ботинки до носков, и нельзя надеть куртку до футболки.

```
Правила:
- Носки → перед ботинками
- Футболка → перед курткой
- Штаны → перед ботинками

Один правильный порядок:
1. Носки
2. Штаны
3. Футболка
4. Ботинки
5. Куртка

Это topological sort!
```

### Формальное определение

**Topological Sort** — линейное упорядочивание вершин направленного ациклического графа (DAG), такое что для каждого ребра (u, v) вершина u появляется перед v в упорядочивании.

**Ключевые свойства:**
- Существует **только для DAG** (Directed Acyclic Graph)
- Если граф имеет цикл — topological sort невозможен
- Может быть **несколько валидных** упорядочиваний
- Время: O(V + E), где V — вершины, E — рёбра

**Два основных алгоритма:**

```
1. Kahn's Algorithm (BFS)
   - Подсчитать indegree каждой вершины
   - Добавить в очередь вершины с indegree = 0
   - Обрабатывать очередь, уменьшая indegree соседей

2. DFS-based (Tarjan's approach)
   - Выполнить DFS
   - Добавлять вершину в результат после обработки всех потомков
   - Перевернуть результат (reverse postorder)
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **DAG** | Directed Acyclic Graph | Граф без циклов |
| **Indegree** | Количество входящих рёбер | indegree(v) = 0 значит нет prerequisites |
| **Outdegree** | Количество исходящих рёбер | Сколько зависит от вершины |
| **Source** | Вершина с indegree = 0 | Начальная точка |
| **Sink** | Вершина с outdegree = 0 | Конечная точка |
| **Postorder** | Порядок после обработки потомков | DFS: сначала потомки, потом вершина |
| **Cycle** | Путь из вершины в себя | Делает toposort невозможным |

---

## Как это работает?

### Kahn's Algorithm (BFS)

```
Граф курсов:
  0 → 1
  0 → 2
  1 → 3
  2 → 3

Шаг 1: Подсчёт indegree
  indegree = [0, 1, 1, 2]
  (0 имеет 0 входящих, 3 имеет 2 входящих)

Шаг 2: Очередь с indegree = 0
  queue = [0]

Шаг 3: Обработка

  Извлекаем 0, result = [0]
  Уменьшаем indegree соседей: 1 и 2
  indegree = [0, 0, 0, 2]
  queue = [1, 2]

  Извлекаем 1, result = [0, 1]
  Уменьшаем indegree соседа 3
  indegree = [0, 0, 0, 1]
  queue = [2]

  Извлекаем 2, result = [0, 1, 2]
  Уменьшаем indegree соседа 3
  indegree = [0, 0, 0, 0]
  queue = [3]

  Извлекаем 3, result = [0, 1, 2, 3]
  queue = []

Результат: [0, 1, 2, 3]
Все вершины обработаны → нет цикла ✓
```

**Визуализация:**

```
Исходный граф:        Порядок обработки:
    0                     ①
   / \                   / \
  1   2      →          ②   ③
   \ /                   \ /
    3                     ④

Результат: [0, 1, 2, 3] или [0, 2, 1, 3]
```

### DFS-based Algorithm

```
Граф курсов:
  0 → 1
  0 → 2
  1 → 3
  2 → 3

DFS от каждой непосещённой вершины:

Состояния: WHITE (не посещена), GRAY (в обработке), BLACK (завершена)

DFS(0):
  0 → GRAY
  DFS(1):
    1 → GRAY
    DFS(3):
      3 → GRAY
      3 → BLACK, добавляем в stack: [3]
    1 → BLACK, добавляем в stack: [3, 1]
  DFS(2):
    2 → GRAY
    3 уже BLACK (пропускаем)
    2 → BLACK, добавляем в stack: [3, 1, 2]
  0 → BLACK, добавляем в stack: [3, 1, 2, 0]

Reverse stack: [0, 2, 1, 3]

Результат: [0, 2, 1, 3]
```

**Обнаружение цикла в DFS:**

```
Если встречаем GRAY вершину при DFS → цикл найден!

Пример с циклом: 0 → 1 → 2 → 0

DFS(0):
  0 → GRAY
  DFS(1):
    1 → GRAY
    DFS(2):
      2 → GRAY
      DFS(0):
        0 is GRAY → ЦИКЛ НАЙДЕН!
```

---

## Сложность операций

| Алгоритм | Time | Space | Примечание |
|----------|------|-------|------------|
| Kahn's (BFS) | O(V + E) | O(V + E) | Очередь + граф |
| DFS-based | O(V + E) | O(V + E) | Стек + граф |
| Cycle Detection | O(V + E) | O(V) | Встроено в оба |

**Почему O(V + E)?**
- Каждая вершина посещается ровно 1 раз: O(V)
- Каждое ребро обрабатывается ровно 1 раз: O(E)

---

## Реализация

### Kahn's Algorithm (Kotlin)

```kotlin
/**
 * Course Schedule I — проверка возможности пройти все курсы (Kahn's Algorithm)
 *
 * ИДЕЯ: Если граф зависимостей содержит цикл, пройти все курсы невозможно.
 *       Kahn's algorithm либо обрабатывает все вершины (нет цикла),
 *       либо "застревает" (есть цикл — все оставшиеся вершины имеют indegree > 0).
 *
 * ПОШАГОВЫЙ ПРИМЕР: numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]
 *   Граф: 0→1, 0→2, 1→3, 2→3
 *   indegree: [0,1,1,2]
 *
 *   queue=[0] → обработали 0 → indegree=[0,0,0,2] → queue=[1,2]
 *   queue=[1,2] → обработали 1 → indegree=[0,0,0,1] → queue=[2]
 *   queue=[2] → обработали 2 → indegree=[0,0,0,0] → queue=[3]
 *   queue=[3] → обработали 3 → processed=4 = numCourses ✓
 */
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    // Adjacency list: graph[u] = список вершин, в которые ведут рёбра из u
    // Эффективнее матрицы смежности: O(V+E) памяти вместо O(V²)
    val graph = Array(numCourses) { mutableListOf<Int>() }
    val indegree = IntArray(numCourses)

    // Один проход: строим граф + считаем indegree
    for ((course, prereq) in prerequisites) {
        // Ребро ОТ prereq К course: prereq должен быть пройден первым
        graph[prereq].add(course)
        indegree[course]++
    }

    // Стартуем с "источников" — курсов без prerequisites
    // У них indegree = 0, значит можно начать сразу
    val queue = ArrayDeque<Int>()
    for (i in 0 until numCourses) {
        if (indegree[i] == 0) {
            queue.add(i)
        }
    }

    var processed = 0

    while (queue.isNotEmpty()) {
        val course = queue.removeFirst()
        processed++

        // "Прошли" курс → уменьшаем indegree всех зависимых
        for (next in graph[course]) {
            indegree[next]--
            // Все prerequisites выполнены → курс готов к прохождению
            if (indegree[next] == 0) {
                queue.add(next)
            }
        }
    }

    // Если обработали все курсы — цикла нет, можно пройти всё
    // Иначе остались курсы с indegree > 0 — они в цикле
    return processed == numCourses
}
```

### Course Schedule II — вернуть порядок (Kotlin)

```kotlin
/**
 * Возвращаем порядок прохождения курсов
 *
 * Отличие от Course Schedule I: собираем результат вместо счётчика
 */
fun findOrder(numCourses: Int, prerequisites: Array<IntArray>): IntArray {
    val graph = Array(numCourses) { mutableListOf<Int>() }
    val indegree = IntArray(numCourses)

    for ((course, prereq) in prerequisites) {
        graph[prereq].add(course)
        indegree[course]++
    }

    val queue = ArrayDeque<Int>()
    for (i in 0 until numCourses) {
        if (indegree[i] == 0) {
            queue.add(i)
        }
    }

    val result = mutableListOf<Int>()

    while (queue.isNotEmpty()) {
        val course = queue.removeFirst()
        // Kahn's: курс добавляется когда все его prerequisites обработаны
        result.add(course)

        for (next in graph[course]) {
            indegree[next]--
            if (indegree[next] == 0) {
                queue.add(next)
            }
        }
    }

    // Не все курсы обработаны → есть цикл → валидного порядка нет
    return if (result.size == numCourses) result.toIntArray() else intArrayOf()
}
```

### DFS-based Topological Sort (Kotlin)

```kotlin
/**
 * Topological Sort через DFS (Tarjan's approach)
 *
 * ИДЕЯ: DFS postorder даёт ОБРАТНЫЙ топологический порядок
 *       Добавляем вершину в результат ПОСЛЕ обработки всех потомков
 *       Затем разворачиваем результат
 *
 * ОБНАРУЖЕНИЕ ЦИКЛА: Три цвета (WHITE/GRAY/BLACK)
 *   - Если при DFS встречаем GRAY (в текущем пути) → цикл!
 *
 * ВИЗУАЛИЗАЦИЯ (цвета):
 *   0 → 1 → 3
 *   ↓
 *   2
 *
 *   DFS от 0: 0→GRAY, dfs(1), 1→GRAY, dfs(3), 3→GRAY
 *             3 завершён→BLACK, result=[3]
 *             1 завершён→BLACK, result=[3,1]
 *             dfs(2), 2→GRAY, 2 завершён→BLACK, result=[3,1,2]
 *             0 завершён→BLACK, result=[3,1,2,0]
 *   Reverse: [0,2,1,3] — топологический порядок
 */
fun findOrderDFS(numCourses: Int, prerequisites: Array<IntArray>): IntArray {
    val graph = Array(numCourses) { mutableListOf<Int>() }

    for ((course, prereq) in prerequisites) {
        graph[prereq].add(course)
    }

    // Три цвета для обнаружения циклов:
    // 0 = WHITE (не посещена)
    // 1 = GRAY (в процессе — в текущем DFS пути)
    // 2 = BLACK (полностью обработана)
    val state = IntArray(numCourses)
    val result = mutableListOf<Int>()

    fun dfs(node: Int): Boolean {
        if (state[node] == 1) return false  // GRAY в текущем пути = цикл!
        if (state[node] == 2) return true   // BLACK = уже обработана, пропускаем

        state[node] = 1  // Входим в вершину → GRAY

        for (next in graph[node]) {
            if (!dfs(next)) return false  // Цикл найден в потомке
        }

        state[node] = 2  // Выходим из вершины → BLACK
        // Postorder: добавляем ПОСЛЕ всех потомков
        result.add(node)
        return true
    }

    // Граф может быть несвязным — запускаем DFS от каждой непосещённой
    for (i in 0 until numCourses) {
        if (state[i] == 0 && !dfs(i)) {
            return intArrayOf()  // Цикл → невозможно
        }
    }

    // Postorder даёт обратный порядок → разворачиваем
    return result.reversed().toIntArray()
}
```

### Alien Dictionary (Java)

```java
/**
 * Alien Dictionary — восстановление алфавита инопланетян
 *
 * ЗАДАЧА: Дан отсортированный словарь инопланетного языка.
 *         Восстановить порядок букв в алфавите.
 *
 * ИДЕЯ: Сравниваем соседние слова, находим первую различающуюся букву.
 *       Это даёт нам ребро в графе: буква1 → буква2.
 *       Затем применяем topological sort.
 *
 * ПРИМЕР: words = ["wrt", "wrf", "er", "ett", "rftt"]
 *   "wrt" vs "wrf": t → f
 *   "wrf" vs "er":  w → e
 *   "er" vs "ett":  r → t
 *   "ett" vs "rftt": e → r
 *
 *   Граф: t→f, w→e, r→t, e→r
 *   Toposort: w → e → r → t → f
 *   Ответ: "wertf"
 */
public String alienOrder(String[] words) {
    // Граф зависимостей между буквами
    Map<Character, Set<Character>> graph = new HashMap<>();
    Map<Character, Integer> indegree = new HashMap<>();

    // Сначала регистрируем все буквы (могут быть изолированные)
    for (String word : words) {
        for (char c : word.toCharArray()) {
            graph.putIfAbsent(c, new HashSet<>());
            indegree.putIfAbsent(c, 0);
        }
    }

    // Сравниваем соседние слова — они отсортированы!
    for (int i = 0; i < words.length - 1; i++) {
        String w1 = words[i];
        String w2 = words[i + 1];

        // Невалидный случай: "abc" перед "ab" невозможен
        // (длинное слово не может идти перед своим префиксом)
        if (w1.length() > w2.length() && w1.startsWith(w2)) {
            return "";
        }

        // Находим ПЕРВУЮ различающуюся букву
        for (int j = 0; j < Math.min(w1.length(), w2.length()); j++) {
            char c1 = w1.charAt(j);
            char c2 = w2.charAt(j);

            if (c1 != c2) {
                // c1 идёт ПЕРЕД c2 в алфавите → ребро c1→c2
                if (!graph.get(c1).contains(c2)) {
                    graph.get(c1).add(c2);
                    indegree.merge(c2, 1, Integer::sum);
                }
                // Только первое различие важно!
                // "wrt" vs "wrf": сравнение w==w, r==r, t!=f → t→f
                break;
            }
        }
    }

    // Kahn's algorithm для toposort
    Queue<Character> queue = new LinkedList<>();
    for (char c : indegree.keySet()) {
        if (indegree.get(c) == 0) {
            queue.offer(c);
        }
    }

    StringBuilder result = new StringBuilder();
    while (!queue.isEmpty()) {
        char c = queue.poll();
        result.append(c);

        for (char next : graph.get(c)) {
            indegree.merge(next, -1, Integer::sum);
            if (indegree.get(next) == 0) {
                queue.offer(next);
            }
        }
    }

    // Не все буквы обработаны → цикл → невозможный словарь
    return result.length() == indegree.size() ? result.toString() : "";
}
```

### Build Order (Python)

```python
def find_build_order(projects: list, dependencies: list) -> list:
    """
    projects: ['a', 'b', 'c', 'd', 'e', 'f']
    dependencies: [('a', 'd'), ('f', 'b'), ...]  # (first, second) = first before second
    """
    from collections import defaultdict, deque

    graph = defaultdict(list)
    indegree = {p: 0 for p in projects}

    # WHY: строим граф зависимостей
    for first, second in dependencies:
        graph[first].append(second)
        indegree[second] += 1

    # WHY: начинаем с проектов без зависимостей
    queue = deque([p for p in projects if indegree[p] == 0])
    result = []

    while queue:
        project = queue.popleft()
        result.append(project)

        for dependent in graph[project]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    # WHY: если не все проекты в результате — циклическая зависимость
    if len(result) != len(projects):
        raise ValueError("Circular dependency detected")

    return result
```

---

## Распространённые ошибки

### 1. Неправильное направление рёбер

```kotlin
// ❌ НЕПРАВИЛЬНО: [course, prereq] означает prereq → course
for ((prereq, course) in prerequisites) {  // перепутали!
    graph[prereq].add(course)
}

// ✅ ПРАВИЛЬНО: prereq должен быть выполнен перед course
for ((course, prereq) in prerequisites) {
    graph[prereq].add(course)  // Ребро: prereq → course (prereq первый)
    indegree[course]++         // course получает входящее ребро
}
```

### 2. Не проверяют цикл

```kotlin
// ❌ НЕПРАВИЛЬНО: не проверяют, все ли вершины обработаны
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    result.add(node)
    // ...
}
return result.toIntArray()  // может вернуть неполный результат!

// ✅ ПРАВИЛЬНО: проверяем на цикл
return if (result.size == numCourses) result.toIntArray() else intArrayOf()
```

### 3. Неправильное обнаружение цикла в DFS

```kotlin
// ❌ НЕПРАВИЛЬНО: использование boolean visited
val visited = BooleanArray(n)
fun dfs(node: Int) {
    if (visited[node]) return  // это не детектит цикл правильно!
    visited[node] = true
    // ...
}

// ✅ ПРАВИЛЬНО: три состояния (WHITE, GRAY, BLACK)
val state = IntArray(n)  // 0=WHITE, 1=GRAY, 2=BLACK
fun dfs(node: Int): Boolean {
    if (state[node] == 1) return false  // GRAY = в текущем DFS пути = цикл!
    if (state[node] == 2) return true   // BLACK = полностью обработана, пропускаем
    state[node] = 1
    // ...
    state[node] = 2
    return true
}
```

### 4. Забыть развернуть результат DFS

```kotlin
// ❌ НЕПРАВИЛЬНО: postorder без reverse
result.add(node)  // добавляем после обработки потомков
return result.toIntArray()  // неправильный порядок!

// ✅ ПРАВИЛЬНО: reverse для получения topological order
return result.reversed().toIntArray()
```

### 5. Не обрабатывают отдельные компоненты

```kotlin
// ❌ НЕПРАВИЛЬНО: DFS только от одной вершины
dfs(0)  // если граф не связный, пропустим вершины

// ✅ ПРАВИЛЬНО: DFS от каждой непосещённой вершины
for (i in 0 until n) {
    if (state[i] == 0) {
        if (!dfs(i)) return intArrayOf()
    }
}
```

---

## Когда использовать

### Decision Tree

```
Задача про зависимости/порядок?
│
├─ YES: Topological Sort
│   │
│   ├─ Только проверка возможности?
│   │   └─ Kahn's + проверка size
│   │
│   ├─ Нужен конкретный порядок?
│   │   └─ Kahn's или DFS + reverse
│   │
│   ├─ Лексикографически минимальный порядок?
│   │   └─ Kahn's с PriorityQueue вместо Queue
│   │
│   ├─ Все возможные порядки?
│   │   └─ Backtracking с toposort
│   │
│   └─ Определить порядок из примеров?
│       └─ Alien Dictionary: построить граф + toposort
│
└─ NO: Другой паттерн
    │
    ├─ Кратчайший путь? → BFS/Dijkstra
    ├─ Связные компоненты? → Union-Find/DFS
    └─ Цикл в undirected? → Union-Find
```

### Kahn vs DFS

| Критерий | Kahn's (BFS) | DFS |
|----------|--------------|-----|
| Интуитивность | Высокая | Средняя |
| Обнаружение цикла | size check | три состояния |
| Лексикографический | PriorityQueue | Сложнее |
| Память | O(V) для queue | O(V) для стека вызовов |
| Параллелизация | Легко (по уровням) | Сложнее |

---

## Практика

### Концептуальные вопросы

1. **Может ли быть несколько topological orderings?**
   - Да, если есть вершины с одинаковым "уровнем" (indegree = 0 одновременно)
   - Пример: A→C, B→C имеет orderings [A,B,C] и [B,A,C]

2. **Как получить лексикографически минимальный порядок?**
   - Использовать PriorityQueue вместо Queue в Kahn's
   - Всегда выбирать наименьшую вершину из доступных

3. **Можно ли применить toposort к undirected графу?**
   - Нет, toposort определён только для directed графов
   - Undirected ребро создаёт "цикл" (A→B и B→A)

### LeetCode задачи

| # | Название | Сложность | Паттерн | Ключевая идея |
|---|----------|-----------|---------|---------------|
| 207 | Course Schedule | Medium | Kahn's | Проверка наличия цикла |
| 210 | Course Schedule II | Medium | Kahn's/DFS | Вернуть порядок |
| 269 | Alien Dictionary | Hard | Build graph + Toposort | Граф из словаря |
| 310 | Minimum Height Trees | Medium | Leaf removal (reverse Kahn's) | Центроиды графа |
| 802 | Find Eventual Safe States | Medium | Reverse toposort | Безопасные вершины |
| 1136 | Parallel Courses | Medium | Kahn's по уровням | Минимум семестров |
| 2115 | Find All Possible Recipes | Medium | Toposort | Зависимости рецептов |

### Порядок изучения

```
1. 207. Course Schedule (Medium) — базовый Kahn's
2. 210. Course Schedule II (Medium) — возврат порядка
3. 269. Alien Dictionary (Hard) — построение графа
4. 310. Minimum Height Trees (Medium) — reverse approach
5. 802. Find Eventual Safe States (Medium) — reverse toposort
```

---

## Связанные темы

### Prerequisites (изучить до)
- **Graph Basics** — представление графов (adjacency list/matrix)
- **BFS** — для Kahn's algorithm
- **DFS** — для DFS-based toposort
- **Queue/Stack** — базовые структуры

### Unlocks (откроет путь к)
- **Strongly Connected Components** — Tarjan's, Kosaraju's
- **Critical Path Method** — планирование проектов
- **DAG DP** — динамическое программирование на DAG
- **Longest Path in DAG** — O(V+E) вместо NP-hard

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Topological sort работает на любом графе" | **Только на DAG!** Directed Acyclic Graph. Если есть цикл — топологический порядок невозможен |
| "Kahn's и DFS дают одинаковый результат" | **Результаты могут отличаться!** Оба корректны, но порядок может быть разным. Топологический порядок не уникален |
| "Cycle detection — отдельный алгоритм" | **Встроено!** Kahn's: если обработано < V вершин → цикл. DFS: back edge → цикл |
| "DFS approach сложнее" | **Проще концептуально!** Просто DFS + добавление в result после обработки всех соседей (postorder) |
| "Нужен отдельный граф для зависимостей" | **Зависит от направления!** a→b означает "a должен быть перед b" ИЛИ "a зависит от b". Выбери и следуй |
| "O(V+E) — медленно" | **Оптимально!** Нужно посетить каждую вершину и ребро минимум раз. Это lower bound |
| "Топологическая сортировка только для задач" | **Реальные применения!** Build systems (Make, Gradle), package managers (npm), CI/CD pipelines |
| "Нельзя определить все порядки" | **Можно!** Но их экспоненциально много. На практике достаточно одного валидного порядка |

---

## CS-фундамент

| CS-концепция | Применение в Topological Sort |
|--------------|-------------------------------|
| **DAG (Directed Acyclic Graph)** | Обязательное условие. Направленный граф без циклов. Топологический порядок существует ⟺ граф DAG |
| **Indegree** | Количество входящих рёбер. Вершины с indegree=0 могут быть первыми. Kahn's начинает с них |
| **Postorder DFS** | Добавляем вершину в result ПОСЛЕ обработки всех соседей. Reverse postorder = топологический порядок |
| **Dependency Graph** | Граф зависимостей. Ребро a→b = "a зависит от b" или "a должен быть перед b" (зависит от интерпретации) |
| **Cycle Detection** | Kahn's: processed < V. DFS: visiting → visited (back edge). Цикл = невозможность топологического порядка |
| **Partial Order** | Топологический порядок — линеаризация частичного порядка. Множество допустимых порядков может быть большим |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/topological-sorting-indegree-based-solution/) | Tutorial | Kahn's algorithm |
| 2 | [LeetCode Guide](https://leetcode.com/discuss/post/6136469/Guide-How-to-identify-and-solve-topological-sort-questions/) | Guide | Cycle detection |
| 3 | [CP-Algorithms](https://cp-algorithms.com/graph/topological-sort.html) | Reference | Формальное описание |
| 4 | [NeetCode](https://neetcode.io/roadmap) | Roadmap | Порядок задач |

---

## Куда дальше

→ **Расширение:** Strongly Connected Components (Tarjan's, Kosaraju's)
→ **Применение:** [[dp-patterns]] — DP на DAG
→ **Вернуться к:** [[patterns-overview|Обзор паттернов]]

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция toposort: IKEA/курсы/борщ, 6 типичных ошибок, 5 ментальных моделей)*
