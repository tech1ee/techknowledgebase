---
title: "Паттерн Union-Find (Disjoint Set Union)"
created: 2025-12-29
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - disjoint-set-data-structure
  - path-compression
  - union-by-rank
  - inverse-ackermann
  - connected-components
prerequisites:
  - "[[arrays-strings]]"
  - "[[recursion-fundamentals]]"
  - "[[graphs]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - pattern
  - interview
related:
  - "[[dfs-bfs-patterns]]"
  - "[[graphs]]"
reading_time: 47
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Union-Find Pattern (Disjoint Set Union)

## Теоретические основы

> **Система непересекающихся множеств (Disjoint Set Union, DSU)** — структура данных для хранения разбиения множества на непересекающиеся подмножества с поддержкой операций `Union` (объединение) и `Find` (определение множества элемента). Предложена Tarjan (1975).

### Две ключевые оптимизации

| Оптимизация | Суть | Эффект |
|-------------|------|--------|
| **Path Compression** | При `Find(x)` все узлы пути перенаправляются на корень: `parent[x] = Find(parent[x])` | Дерево становится почти плоским |
| **Union by Rank** | При `Union` корень меньшего дерева присоединяется к большему (по рангу/размеру) | Высота дерева ≤ `O(log n)` |

### Амортизированная сложность: α(n)

Совместное применение обеих оптимизаций даёт амортизированную сложность `O(α(n))` на операцию, где `α` — обратная функция Аккермана. Для всех практических значений `n < 10^80` выполняется `α(n) ≤ 4`, то есть фактически `O(1)`. Доказательство: Tarjan (1975), уточнение — Tarjan & van Leeuwen (1984).

### Применения

Union-Find оптимален для задач **динамической связности**: добавление рёбер с запросами «принадлежат ли вершины одной компоненте?». Классические применения: алгоритм Крускала (MST), обнаружение циклов в графе, кластеризация — см. [[graphs]], [[dfs-bfs-patterns]].

---

## TL;DR

Union-Find отслеживает связные компоненты с почти константным временем. **Две оптимизации: path compression (сжатие пути) и union by rank**. Сложность: O(α(n)) ≈ O(1) на операцию, где α — обратная функция Аккермана. Оптимально для: связности графов, кластеризации, Kruskal MST, детекции циклов.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Дружба в школе

Представь школу с 10 учениками. Каждый ученик сначала сам по себе — "одиночка".

```
Начало года (все отдельно):

  Петя   Маша   Коля   Аня   Дима   Вика   Саша   Лена   Миша   Юля
   [0]    [1]    [2]   [3]    [4]    [5]    [6]    [7]    [8]    [9]

Каждый — "капитан" своей группы (указывает на себя)
```

Постепенно формируются дружеские группы:

```
Событие 1: Петя и Маша подружились
  → Теперь они в одной группе, Петя — "капитан"

   Петя──────Маша
    ↑
  капитан

Событие 2: Коля и Аня подружились
  → Отдельная группа, Коля — "капитан"

Событие 3: Маша познакомила Аню с группой
  → union(Маша, Аня) → группы объединяются!

        Петя
       /    \
    Маша    Коля
              |
             Аня

Вопрос: Петя и Аня друзья?
→ find(Петя) = Петя
→ find(Аня) = Аня→Коля→Петя = Петя
→ Одинаковые корни = ДА, друзья!
```

**Ключевой инсайт:** Дружба транзитивна. Если A дружит с B, а B дружит с C, то A дружит с C.

---

### Аналогия 2: Острова и мосты

```
Начальное состояние — 6 отдельных островов:

    [A]        [B]        [C]

    [D]        [E]        [F]

Каждый остров — отдельная страна
Население каждого острова = 1
```

Строим мосты (Union операции):

```
Строим мост A-B:
    [A]═══════[B]        [C]
     └─────────┘
      1 страна

Строим мост D-E:
    [D]═══════[E]        [F]
     └─────────┘
      1 страна

Строим мост B-E (соединяем две страны!):
    [A]═══════[B]
         │
         ║  (мост)
         │
    [D]═══════[E]        [C]    [F]
    └──────────────────┘
         1 большая страна

Теперь: 3 страны (ABDE, C, F)

Вопрос: Можно ли доехать из A в E?
→ Да! A→B→E или A→B→... есть путь
→ find(A) = find(E) = общий "корень"
```

**Ключевой инсайт:** Union-Find отвечает "есть ли путь?", но не говорит какой именно путь.

---

### Аналогия 3: Электрическая сеть

```
Задача: Есть N домов. Провода соединяют некоторые дома.
Вопрос: Все ли дома имеют электричество от станции?

Электростанция в доме 0:

     [0]⚡─────[1]
      │        │
      │        │
     [2]      [3]─────[4]
                       │
                      [5]

Union операции (провода):
- union(0, 1)
- union(0, 2)
- union(1, 3)
- union(3, 4)
- union(4, 5)

Проверка: connected(0, 5)?
→ find(0) = 0 (станция)
→ find(5) = 5→4→3→1→0 = 0
→ Да! Дом 5 получает электричество ✓

Но с Path Compression после find(5):
     [0]⚡
    /|\ \ \
   1 2 3 4 5   ← Все напрямую к станции!
```

**Ключевой инсайт:** Path compression — как прокладывание "прямых линий" к корню.

---

### Численный пример: Пошаговый Union-Find

```
5 элементов: 0, 1, 2, 3, 4

Инициализация:
  parent = [0, 1, 2, 3, 4]  ← каждый на себя
  rank   = [0, 0, 0, 0, 0]  ← все высоты = 0

Визуально:
  [0]   [1]   [2]   [3]   [4]   (5 отдельных деревьев)
```

**Операция 1: union(0, 1)**

```
  find(0) = 0
  find(1) = 1
  rank[0] == rank[1] == 0
  → parent[1] = 0, rank[0]++

  parent = [0, 0, 2, 3, 4]
  rank   = [1, 0, 0, 0, 0]

  Визуально:
    [0]       [2]   [3]   [4]
     |
    [1]
```

**Операция 2: union(2, 3)**

```
  find(2) = 2
  find(3) = 3
  rank[2] == rank[3] == 0
  → parent[3] = 2, rank[2]++

  parent = [0, 0, 2, 2, 4]
  rank   = [1, 0, 1, 0, 0]

  Визуально:
    [0]       [2]       [4]
     |         |
    [1]       [3]
```

**Операция 3: union(1, 3)** (объединяем две группы!)

```
  find(1) = 1→0 = 0
  find(3) = 3→2 = 2
  rank[0] == rank[2] == 1
  → parent[2] = 0, rank[0]++

  parent = [0, 0, 0, 2, 4]
  rank   = [2, 0, 1, 0, 0]

  Визуально:
        [0]              [4]
       /   \
     [1]   [2]
            |
           [3]
```

**Операция 4: find(3) с Path Compression**

```
  find(3):
    3 → parent[3] = 2
    2 → parent[2] = 0
    0 → parent[0] = 0 (корень!)

  При возврате: parent[3] = 0, parent[2] = 0

  parent = [0, 0, 0, 0, 4]

  Визуально (после сжатия):
        [0]         [4]
      / | \
    [1][2][3]   ← Все напрямую к 0!
```

---

### Что такое Path Compression визуально

```
ДО Path Compression:              ПОСЛЕ find(5):

        [0]                           [0]
         |                          / | \ \
        [1]                       [1][2][3][5]
         |                             |
        [2]                           [4]
         |
        [3]
         |
        [4]
         |
        [5]

find(5) проходит: 5→4→3→2→1→0
На обратном пути: parent[5]=0, parent[4]=0, parent[3]=0...

Результат: дерево "сплющивается"!
Следующий find(5): 5→0 (1 шаг вместо 5)
```

---

## Часть 2: Почему это сложно

### Типичные ошибки студентов

#### Ошибка 1: Забыли Path Compression

```kotlin
// ❌ НЕПРАВИЛЬНО — O(n) на каждый find в худшем случае
fun find(x: Int): Int {
    var curr = x
    while (parent[curr] != curr) {
        curr = parent[curr]
    }
    return curr
}

// ✅ ПРАВИЛЬНО — O(α(n)) ≈ O(1)
fun find(x: Int): Int {
    if (parent[x] != x) {
        parent[x] = find(parent[x])  // ← Path Compression!
    }
    return parent[x]
}

СИМПТОМ: TLE (Time Limit Exceeded) на больших тестах
РЕШЕНИЕ: Добавь одну строку: parent[x] = find(parent[x])
```

#### Ошибка 2: Union без проверки на одинаковый корень

```kotlin
// ❌ НЕПРАВИЛЬНО — count может стать отрицательным!
fun union(x: Int, y: Int) {
    parent[find(x)] = find(y)
    count--  // Уменьшаем даже если x и y уже связаны!
}

// Пример проблемы:
// union(0, 1) → count = 4
// union(0, 1) → count = 3  ← Ошибка! Ничего не изменилось!

// ✅ ПРАВИЛЬНО — проверяем, что корни разные
fun union(x: Int, y: Int): Boolean {
    val rootX = find(x)
    val rootY = find(y)
    if (rootX == rootY) return false  // Уже связаны!
    parent[rootX] = rootY
    count--
    return true
}

СИМПТОМ: Неправильное количество компонент
РЕШЕНИЕ: Всегда проверяй rootX != rootY перед union
```

#### Ошибка 3: Неправильная инициализация parent

```kotlin
// ❌ НЕПРАВИЛЬНО — все указывают на 0
val parent = IntArray(n)  // По умолчанию все = 0

// Проблема:
find(5) = 5→0 (думает что 5 уже в группе с 0!)

// ✅ ПРАВИЛЬНО — каждый указывает на себя
val parent = IntArray(n) { it }  // parent[i] = i

// Или:
val parent = IntArray(n)
for (i in 0 until n) parent[i] = i

СИМПТОМ: Все элементы "уже связаны" с самого начала
РЕШЕНИЕ: Инициализируй parent[i] = i
```

#### Ошибка 4: Путаница с индексацией 0-based vs 1-based

```kotlin
// Задача даёт вершины 1..n

// ❌ НЕПРАВИЛЬНО
val uf = UnionFind(n)
uf.union(1, 2)  // ArrayIndexOutOfBoundsException при n=2!

// ✅ ПРАВИЛЬНО — массив размера n+1
val uf = UnionFind(n + 1)  // Индексы 0..n, используем 1..n

СИМПТОМ: ArrayIndexOutOfBoundsException
РЕШЕНИЕ: Если вершины 1..n, создавай массив размера n+1
```

#### Ошибка 5: Сравнение parent вместо корней

```kotlin
// ❌ НЕПРАВИЛЬНО — сравниваем непосредственных родителей
fun connected(x: Int, y: Int): Boolean {
    return parent[x] == parent[y]
}

// Проблема:
// Если 0→1, 1→2, 2→3 и 0→1, 1→3
// parent[0] = 1, parent[1] = 3
// connected(0, 1) вернёт false! (1 != 3)
// Но они в одной группе!

// ✅ ПРАВИЛЬНО — сравниваем КОРНИ
fun connected(x: Int, y: Int): Boolean {
    return find(x) == find(y)
}

СИМПТОМ: connected() возвращает false для связанных элементов
РЕШЕНИЕ: Всегда используй find() для получения корня
```

#### Ошибка 6: Забыли про 2D→1D преобразование в grid

```kotlin
// Grid m×n, нужен Union-Find

// ❌ НЕПРАВИЛЬНО — использование (row, col) напрямую
val uf = UnionFind(???)  // Какой размер? Как хранить пары?

// ✅ ПРАВИЛЬНО — преобразование в 1D индекс
val uf = UnionFind(m * n)
fun index(row: Int, col: Int) = row * n + col

// Клетка (2, 3) в сетке 4×5:
// index = 2 * 5 + 3 = 13

// Соседи клетки (i, j):
// Вверх:  (i-1, j) → (i-1) * n + j
// Вниз:   (i+1, j) → (i+1) * n + j
// Влево:  (i, j-1) → i * n + (j-1)
// Вправо: (i, j+1) → i * n + (j+1)

СИМПТОМ: Непонятно как хранить 2D координаты
РЕШЕНИЕ: index = row * cols + col
```

---

## Часть 3: Ментальные модели

### Модель 1: "Лес перевёрнутых деревьев"

```
Union-Find — это лес, где каждое дерево = одна компонента
Деревья "перевёрнуты": дети указывают на родителей

   Обычное дерево:        Union-Find дерево:
        A                       A
       / \                      ↑
      B   C                    / \
     /                        B   C
    D                         ↑
                              D

В обычном: родитель знает детей
В Union-Find: ребёнок знает родителя

Корень — это "представитель" всей компоненты
find(x) = подняться до корня
union(x, y) = соединить два корня
```

### Модель 2: "Генеалогическое древо"

```
Каждый элемент помнит своего "предка" (parent)

Семья Ивановых:         Семья Петровых:
    Иван                    Пётр
     ↑                       ↑
    Мария                   Анна
     ↑                       ↑
   Алексей                 Сергей

Вопрос: Алексей и Сергей родственники?
→ Предок(Алексей) = Иван
→ Предок(Сергей) = Пётр
→ Разные предки = разные семьи!

union(Мария, Анна) — брак!
→ Теперь все одна семья с общим "предком"
```

### Модель 3: "Цвета краски"

```
Каждая компонента — свой цвет
find(x) = какого цвета элемент x?
union(x, y) = смешать цвета (все становятся одного цвета)

Начало:       После union(0,1):    После union(2,3):
🔴 🔵 🟢 🟡      🔴 🔴 🟢 🟡          🔴 🔴 🟢 🟢
0  1  2  3      0  1  2  3          0  1  2  3

После union(1,3):
🔴 🔴 🔴 🔴   ← Все одного цвета!
0  1  2  3

Количество цветов = количество компонент
```

### Модель 4: "Представители на собрании"

```
В каждой группе есть представитель (корень)
Все решения принимаются представителем

Группа A: [Петя*, Маша, Коля]    (* = представитель)
Группа B: [Аня*, Дима]

Вопрос от Маши: "Мы с Димой в одной группе?"
→ Представитель Маши: Петя
→ Представитель Димы: Аня
→ Разные представители = разные группы!

union(Маша, Дима):
→ Группы объединяются
→ Нужен новый представитель
→ Выбираем того, чья группа больше (union by rank)
```

### Модель 5: "Интернет-провайдеры"

```
Каждый провайдер — корень своей сети
Компьютеры подключены через цепочку роутеров к провайдеру

ISP_A                    ISP_B
  |                        |
Router1                  Router3
  |                        |
Router2                  PC_4
  |
PC_1, PC_2, PC_3

find(PC_2) = PC_2 → Router2 → Router1 → ISP_A
→ "Кто твой провайдер?"

Path Compression = "прямой канал до провайдера"

После find(PC_2):
ISP_A ← PC_2  (напрямую!)

connected(PC_1, PC_4)?
→ ISP_A ≠ ISP_B
→ Нет связи между ними
```

---

## Зачем это нужно?

**Реальная проблема:**

Социальная сеть с 1 миллиардом пользователей. Нужно быстро отвечать: "Связаны ли пользователи A и B?" и объединять группы друзей. Наивный BFS/DFS: O(V+E) на каждый запрос. Union-Find: O(1) амортизированно.

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| Соцсети | Friend connections | Facebook friend graph |
| Сети | Network connectivity | Определение изоляции узлов |
| Кластеризация | Image segmentation | Region merging |
| Игры | Percolation | Достижимость в сетке |
| Графы | Minimum Spanning Tree | Kruskal's algorithm |
| Компиляторы | Type equivalence | Union types |

**Статистика:**
- 10-15% задач на графы используют Union-Find
- Kruskal MST — классический алгоритм с Union-Find
- Number of Islands, Accounts Merge — частые задачи на интервью

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Массивы** | parent[] и rank[] массивы | [[arrays-strings]] |
| **Рекурсия** | Для path compression (find) | [[recursion-fundamentals]] |
| **Графы** | Концепция связных компонент | [[graphs]] |
| **CS: Tree как структура** | Union-Find = лес деревьев | Структуры данных |
| **CS: Amortized Analysis** | O(α(n)) — почти O(1) amortized | Анализ алгоритмов |

---

## Что это такое?

### Объяснение для 5-летнего

Представь детский сад, где дети держатся за руки. Каждая группа детей — это "команда". У каждой команды есть "капитан" (ребёнок, за которого держатся все остальные через цепочку рук).

```
Команда 1:     Команда 2:
  Петя           Маша
  ↑   ↑            ↑
Вова  Катя       Саша

Вопрос: Петя и Катя в одной команде?
→ Идём по цепочке: Катя → Петя, Петя → Петя. Да!

Вопрос: Петя и Маша в одной команде?
→ Петя → Петя, Маша → Маша. Разные капитаны — разные команды!

Объединяем команды: Петя становится "капитаном" Маши
       Петя
      ↑ ↑  ↑
  Вова Катя Маша
            ↑
          Саша
```

### Формальное определение

**Union-Find (Disjoint Set Union)** — структура данных для работы с непересекающимися множествами, поддерживающая операции:
- **makeSet(x)** — создать множество из одного элемента
- **find(x)** — найти представителя (корень) множества
- **union(x, y)** — объединить множества, содержащие x и y

**Ключевые свойства:**
- Каждое множество представлено деревом
- Корень дерева — представитель множества
- parent[x] указывает на родителя (или на себя для корня)

**Две критические оптимизации:**

```
1. Path Compression (сжатие пути)
   При find(x) прицепляем все узлы напрямую к корню
   Уменьшает высоту дерева

2. Union by Rank/Size
   Присоединяем меньшее дерево к большему
   Ограничивает высоту до O(log n)

Вместе: O(α(n)) ≈ O(1) на операцию
α(n) — обратная функция Аккермана, ≤ 4 для всех практических n
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **Representative (Root)** | Корень дерева множества | parent[root] == root |
| **Rank** | Верхняя граница высоты поддерева | Используется для union by rank |
| **Size** | Количество элементов в множестве | Альтернатива rank |
| **Path Compression** | Присоединение узлов к корню при find | parent[x] = find(parent[x]) |
| **Union by Rank** | Присоединение меньшего дерева к большему | if rank[x] < rank[y]: parent[x] = y |
| **α(n)** | Inverse Ackermann function | ≤ 4 для n < 10^600 |
| **Connected Components** | Количество уникальных корней | Количество множеств |

---

## Как это работает?

### Базовые операции

```
Инициализация: каждый элемент — свой собственный родитель
parent = [0, 1, 2, 3, 4]  # parent[i] = i
rank   = [0, 0, 0, 0, 0]  # все ранги = 0

Union(0, 1):
  root0 = find(0) = 0
  root1 = find(1) = 1
  rank[0] == rank[1] → parent[1] = 0, rank[0]++

  parent = [0, 0, 2, 3, 4]
  rank   = [1, 0, 0, 0, 0]

Union(2, 3):
  root2 = find(2) = 2
  root3 = find(3) = 3
  rank[2] == rank[3] → parent[3] = 2, rank[2]++

  parent = [0, 0, 2, 2, 4]
  rank   = [1, 0, 1, 0, 0]

Union(1, 3):
  root1 = find(1) = 0
  root3 = find(3) = 2
  rank[0] == rank[2] → parent[2] = 0, rank[0]++

  parent = [0, 0, 0, 2, 4]
  rank   = [2, 0, 1, 0, 0]
```

### Path Compression

```
Без path compression:
        0
       / \
      1   2
         / \
        3   4

find(3):
  3 → 2 → 0 (3 шага)

С path compression:
find(3):
  3 → 2 → 0 (3 шага)
  НО: parent[3] = 0, parent[2] = 0

        0
      / | \ \
     1  2  3  4

find(3) снова:
  3 → 0 (1 шаг!)
```

**Визуализация:**

```
До path compression:        После path compression:
      0                           0
     /|\                       /||\\\
    1 2 5                     1 2 3 4 5
     /|\
    3 4 6

find(6):                      find(6):
6→2→0 (2 шага)               6→0 (1 шаг)
+ сжатие: parent[6]=0
```

---

## Сложность операций

| Операция | Без оптимизаций | С оптимизациями | Примечание |
|----------|-----------------|-----------------|------------|
| makeSet | O(1) | O(1) | Инициализация |
| find | O(n) worst | O(α(n)) | α(n) ≤ 4 |
| union | O(n) worst | O(α(n)) | Включает find |
| connected | O(n) worst | O(α(n)) | find(x) == find(y) |
| count components | O(n) | O(n) | Пересчёт корней |

**Амортизированный анализ:**
- m операций на n элементах: O(m × α(n))
- Практически линейно!

---

## Реализация

### Union-Find Class (Kotlin)

```kotlin
/**
 * Структура данных Union-Find (Disjoint Set Union, DSU)
 *
 * ОПЕРАЦИИ:
 * - find(x): найти представителя (корень) множества для x
 * - union(x, y): объединить множества, содержащие x и y
 * - connected(x, y): проверить, в одном ли множестве x и y
 *
 * ДВЕ ОПТИМИЗАЦИИ:
 * 1. Path Compression (сжатие пути) — при find все узлы
 *    присоединяются напрямую к корню
 * 2. Union by Rank — меньшее дерево присоединяется к большему
 *
 * Вместе дают почти O(1) на операцию: O(α(n)) где α — обратная
 * функция Аккермана, растёт невероятно медленно (≤4 для всех
 * практических n ≤ 10^600)
 *
 * ВИЗУАЛИЗАЦИЯ PATH COMPRESSION:
 *
 * До find(4):          После find(4):
 *       1                    1
 *       |                  / | \
 *       2                 2  3  4
 *       |
 *       3
 *       |
 *       4
 */
class UnionFind(n: Int) {
    // parent[i] = i означает, что i — корень своего множества
    // Изначально каждый элемент — сам себе корень
    private val parent = IntArray(n) { it }

    // rank — верхняя граница высоты поддерева
    // Используется для union by rank: меньшее к большему
    private val rank = IntArray(n)

    // count — количество связных компонент
    // Уменьшается при каждом успешном union
    var count = n
        private set

    /**
     * Найти корень множества с path compression
     *
     * Path compression: при каждом find все узлы на пути
     * присоединяются напрямую к корню
     *
     * ПРИМЕР: find(4) в цепочке 1→2→3→4
     * Рекурсивно: find(4)→find(3)→find(2)→find(1)=1
     * На обратном ходе: parent[2]=1, parent[3]=1, parent[4]=1
     */
    fun find(x: Int): Int {
        if (parent[x] != x) {
            // Path compression: присоединяем напрямую к корню
            parent[x] = find(parent[x])
        }
        return parent[x]
    }

    /**
     * Объединить два множества с union by rank
     *
     * Union by rank: присоединяем дерево с меньшим rank к большему
     * Это сохраняет деревья сбалансированными
     *
     * @return true если множества были разными и объединены
     *         false если x и y уже в одном множестве
     */
    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)

        // Если уже в одном множестве — объединять нечего
        if (rootX == rootY) return false

        // Присоединяем дерево с меньшим rank к большему
        when {
            rank[rootX] < rank[rootY] -> parent[rootX] = rootY
            rank[rootX] > rank[rootY] -> parent[rootY] = rootX
            else -> {
                // При равных ranks выбираем любое, увеличиваем rank
                parent[rootY] = rootX
                rank[rootX]++
            }
        }

        count--  // Два множества стали одним → на одну компоненту меньше
        return true
    }

    /**
     * Проверить, связаны ли x и y (в одном множестве)
     */
    fun connected(x: Int, y: Int): Boolean = find(x) == find(y)
}
```

### Number of Islands (Kotlin)

```kotlin
/**
 * Подсчёт островов через Union-Find
 *
 * ИДЕЯ:
 * 1. Преобразуем 2D сетку в 1D массив: (i, j) → i * n + j
 * 2. Для каждой клетки земли объединяем её с соседями (вправо, вниз)
 * 3. Количество островов = компоненты связности среди земли
 *
 * ПОЧЕМУ ТОЛЬКО ВПРАВО И ВНИЗ:
 * При проходе слева направо, сверху вниз:
 * - Соседи слева и сверху уже обработаны (мы их уже union'или)
 * - Проверяем только вправо и вниз, чтобы избежать дублирования
 *
 * ПРИМЕР:
 * grid = [['1','1','0'],
 *         ['0','1','0'],
 *         ['0','0','1']]
 *
 * Индексы:  0  1  2
 *           3  4  5
 *           6  7  8
 *
 * union(0,1), union(1,4) → компонента {0,1,4}
 * 8 остаётся отдельно → компонента {8}
 * Острова: 2
 */
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val m = grid.size
    val n = grid[0].size
    val uf = UnionFind(m * n)

    // Преобразование 2D координат в 1D индекс
    fun index(i: Int, j: Int) = i * n + j

    var waterCount = 0

    for (i in 0 until m) {
        for (j in 0 until n) {
            if (grid[i][j] == '0') {
                waterCount++  // Вода — отдельно, не участвует в union
                continue
            }

            // Объединяем с соседями справа и снизу (если там земля)
            if (i + 1 < m && grid[i + 1][j] == '1') {
                uf.union(index(i, j), index(i + 1, j))
            }
            if (j + 1 < n && grid[i][j + 1] == '1') {
                uf.union(index(i, j), index(i, j + 1))
            }
        }
    }

    // Острова = все компоненты минус "пустые" компоненты воды
    return uf.count - waterCount
}
```

### Redundant Connection (Kotlin)

```kotlin
/**
 * Найти лишнее ребро, образующее цикл
 *
 * ИДЕЯ:
 * - Дерево с n вершинами имеет n-1 рёбер
 * - Если дано n рёбер, одно из них — лишнее (создаёт цикл)
 * - Добавляем рёбра по порядку; когда union возвращает false,
 *   это значит вершины уже связаны → ребро создаёт цикл
 *
 * ПОШАГОВЫЙ ПРИМЕР (edges = [[1,2], [1,3], [2,3]]):
 * union(1,2): uf = {1,2}, {3} → true
 * union(1,3): uf = {1,2,3} → true
 * union(2,3): 2 и 3 уже в одном множестве → false!
 *             Ребро [2,3] создаёт цикл → возвращаем его
 */
fun findRedundantConnection(edges: Array<IntArray>): IntArray {
    val n = edges.size
    val uf = UnionFind(n + 1)  // Вершины нумеруются с 1, поэтому n+1

    for (edge in edges) {
        val (u, v) = edge

        // Если union вернул false, вершины уже связаны
        // Добавление этого ребра создаст цикл
        if (!uf.union(u, v)) {
            return edge  // Это избыточное ребро
        }
    }

    return intArrayOf()  // Не должно произойти по условию задачи
}
```

### Accounts Merge (Java)

```java
/**
 * Слияние аккаунтов через Union-Find
 *
 * ЗАДАЧА:
 * Аккаунты = [имя, email1, email2, ...]
 * Два аккаунта принадлежат одному человеку, если у них общий email.
 * Объединить все аккаунты одного человека.
 *
 * ИДЕЯ:
 * 1. Присваиваем каждому уникальному email индекс
 * 2. Объединяем все email'ы одного аккаунта (они принадлежат одному человеку)
 * 3. Группируем email'ы по корню (все email'ы с одним корнём = один человек)
 *
 * ПРИМЕР:
 * accounts = [["John", "j1@mail", "j2@mail"],
 *             ["John", "j3@mail"],
 *             ["John", "j2@mail", "j4@mail"]]
 *
 * Шаг 1: emailToIndex = {j1:0, j2:1, j3:2, j4:3}
 * Шаг 2: union(0,1) для 1-го аккаунта
 *        union(1,3) для 3-го аккаунта (j2 и j4)
 *        → {j1, j2, j4} в одном множестве
 * Шаг 3: Группировка → John: [j1, j2, j4], John: [j3]
 */
public List<List<String>> accountsMerge(List<List<String>> accounts) {
    // email → числовой индекс для Union-Find
    Map<String, Integer> emailToIndex = new HashMap<>();
    // email → имя владельца (для восстановления в результате)
    Map<String, String> emailToName = new HashMap<>();

    int index = 0;
    for (List<String> account : accounts) {
        String name = account.get(0);
        for (int i = 1; i < account.size(); i++) {
            String email = account.get(i);
            if (!emailToIndex.containsKey(email)) {
                emailToIndex.put(email, index++);
            }
            emailToName.put(email, name);
        }
    }

    UnionFind uf = new UnionFind(index);

    // Объединяем все email'ы каждого аккаунта
    // (все email'ы в одном аккаунте принадлежат одному человеку)
    for (List<String> account : accounts) {
        String firstEmail = account.get(1);
        int firstIndex = emailToIndex.get(firstEmail);

        for (int i = 2; i < account.size(); i++) {
            String email = account.get(i);
            uf.union(firstIndex, emailToIndex.get(email));
        }
    }

    // Группируем email'ы по корню (одинаковый корень = один человек)
    Map<Integer, List<String>> rootToEmails = new HashMap<>();
    for (String email : emailToIndex.keySet()) {
        int root = uf.find(emailToIndex.get(email));
        rootToEmails.computeIfAbsent(root, k -> new ArrayList<>()).add(email);
    }

    // Формируем результат: [имя, email1, email2, ...] для каждого человека
    List<List<String>> result = new ArrayList<>();
    for (List<String> emails : rootToEmails.values()) {
        Collections.sort(emails);  // Сортировка по условию задачи
        String name = emailToName.get(emails.get(0));
        emails.add(0, name);  // Имя в начало списка
        result.add(emails);
    }

    return result;
}
```

### Kruskal MST (Python)

```python
def kruskal_mst(n: int, edges: list) -> tuple:
    """
    Алгоритм Краскала для построения MST через Union-Find

    ИДЕЯ (жадный алгоритм):
    1. Сортируем рёбра по весу (от меньшего к большему)
    2. Перебираем рёбра в порядке возрастания веса
    3. Добавляем ребро в MST, если оно не создаёт цикл
    4. Останавливаемся, когда добавили n-1 рёбер

    Цикл определяем через Union-Find:
    - Если вершины уже в одном множестве → ребро создаст цикл
    - Если в разных → можно добавить, объединяем множества

    n: количество вершин
    edges: [(weight, u, v), ...]
    Returns: (mst_weight, mst_edges)
    """
    # Сортируем рёбра по весу — жадно берём самые лёгкие
    edges.sort()

    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]

    def union(x: int, y: int) -> bool:
        root_x, root_y = find(x), find(y)
        if root_x == root_y:
            return False  # Уже в одном множестве = добавление создаст цикл

        # Union by rank
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
        return True

    mst_weight = 0
    mst_edges = []

    for weight, u, v in edges:
        # Добавляем ребро только если оно не создаёт цикл
        if union(u, v):
            mst_weight += weight
            mst_edges.append((u, v, weight))

            # MST для n вершин имеет ровно n-1 рёбер
            if len(mst_edges) == n - 1:
                break

    return mst_weight, mst_edges
```

---

## Распространённые ошибки

### 1. Забыть path compression

```kotlin
// ❌ НЕПРАВИЛЬНО: O(n) на каждый find
fun find(x: Int): Int {
    var curr = x
    while (parent[curr] != curr) {
        curr = parent[curr]
    }
    return curr
}

// ✅ ПРАВИЛЬНО: O(α(n)) с path compression
fun find(x: Int): Int {
    if (parent[x] != x) {
        parent[x] = find(parent[x])  // Сжимаем путь: все узлы → напрямую к корню
    }
    return parent[x]
}
```

### 2. Union без проверки на одинаковый корень

```kotlin
// ❌ НЕПРАВИЛЬНО: count уменьшается даже когда элементы уже связаны
fun union(x: Int, y: Int) {
    parent[find(x)] = find(y)
    count--  // Неправильно! Может уменьшить count лишний раз
}

// ✅ ПРАВИЛЬНО: проверяем, что корни разные
fun union(x: Int, y: Int): Boolean {
    val rootX = find(x)
    val rootY = find(y)
    if (rootX == rootY) return false  // Уже связаны — объединять нечего
    parent[rootX] = rootY
    count--
    return true
}
```

### 3. Неправильная инициализация

```kotlin
// ❌ НЕПРАВИЛЬНО: все parent = 0
val parent = IntArray(n)  // всё заполнено нулями!

// ✅ ПРАВИЛЬНО: parent[i] = i (каждый сам себе корень)
val parent = IntArray(n) { it }
```

### 4. Забыть про 0-based vs 1-based индексацию

```kotlin
// ❌ НЕПРАВИЛЬНО: вершины нумеруются с 1, но массив с 0
val uf = UnionFind(n)
uf.union(1, 2)  // IndexOutOfBounds!

// ✅ ПРАВИЛЬНО: учитываем нумерацию
val uf = UnionFind(n + 1)  // Для вершин 1..n нужен массив размера n+1
```

### 5. Сравнение элементов вместо корней

```kotlin
// ❌ НЕПРАВИЛЬНО: сравниваем сами элементы
fun connected(x: Int, y: Int) = parent[x] == parent[y]  // Неверно!

// ✅ ПРАВИЛЬНО: сравниваем корни
fun connected(x: Int, y: Int) = find(x) == find(y)
```

---

## Когда использовать

### Decision Tree

```
Задача про связность/группировку?
│
├─ YES: Union-Find
│   │
│   ├─ Количество связных компонент?
│   │   └─ Union-Find + count
│   │
│   ├─ Проверка связности двух элементов?
│   │   └─ find(x) == find(y)
│   │
│   ├─ Детекция цикла в undirected графе?
│   │   └─ union возвращает false = цикл
│   │
│   ├─ Minimum Spanning Tree?
│   │   └─ Kruskal's с Union-Find
│   │
│   └─ Группировка по эквивалентности?
│       └─ Union-Find + group by root
│
└─ NO: Другой паттерн
    │
    ├─ Порядок зависимостей? → Topological Sort
    ├─ Кратчайший путь? → BFS/Dijkstra
    └─ SCC? → Tarjan's/Kosaraju's
```

### Union-Find vs BFS/DFS

| Критерий | Union-Find | BFS/DFS |
|----------|------------|---------|
| Множество запросов | O(α(n)) каждый | O(V+E) каждый |
| Динамические рёбра | Отлично (только добавление) | Пересчёт |
| Удаление рёбер | Плохо (нужен rollback) | OK |
| Память | O(n) | O(V+E) |
| Кратчайший путь | Нет | BFS |
| MST | Kruskal's | Prim's |

---

## Практика

### Концептуальные вопросы

1. **Почему α(n) практически константа?**
   - α(n) — обратная функция Аккермана
   - α(10^80) ≈ 4 (атомов во Вселенной < 10^80)
   - Для любого практического n, α(n) ≤ 4

2. **Можно ли удалять рёбра из Union-Find?**
   - Стандартный UF не поддерживает удаление
   - Для offline задач: обработка в обратном порядке
   - Для online: Link-Cut Trees (сложнее)

3. **Union by Size vs Union by Rank?**
   - Size: точное количество элементов
   - Rank: верхняя граница высоты
   - Оба дают O(α(n)), rank чуть проще

### LeetCode задачи

| # | Название | Сложность | Паттерн | Ключевая идея |
|---|----------|-----------|---------|---------------|
| 200 | Number of Islands | Medium | Grid UF | 2D → 1D индексация |
| 547 | Number of Provinces | Medium | Basic UF | Матрица смежности |
| 684 | Redundant Connection | Medium | Cycle detection | union returns false |
| 721 | Accounts Merge | Medium | String UF | email → index |
| 990 | Satisfiability of Equality | Medium | Variable UF | a==b → union |
| 1319 | Number of Operations | Medium | Count components | n - uf.count |
| 128 | Longest Consecutive | Medium | Alternative | Также можно HashSet |

### Порядок изучения

```
1. 547. Number of Provinces (Medium) — базовый UF
2. 200. Number of Islands (Medium) — 2D grid
3. 684. Redundant Connection (Medium) — cycle detection
4. 990. Satisfiability of Equality (Medium) — string mapping
5. 721. Accounts Merge (Medium) — complex grouping
6. 1319. Number of Operations (Medium) — component counting
```

---

## Связанные темы

### Prerequisites (изучить до)
- **Arrays** — parent/rank массивы
- **Recursion** — для path compression
- **Graph Basics** — концепция связности

### Unlocks (откроет путь к)
- **Kruskal's MST** — использует Union-Find
- **Dynamic Connectivity** — Online/Offline задачи
- **Percolation** — классическое применение

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Union-Find сложный" | **Простая структура!** Два массива (parent, rank), две операции (find, union). 15 строк кода |
| "DFS/BFS всегда лучше" | **Union-Find быстрее для динамической связности!** Добавление рёбер + проверка связности = O(α(n)) |
| "Path compression обязательна" | **Желательна!** Без неё O(log n), с ней O(α(n)). На практике разница небольшая для маленьких n |
| "Union by rank обязателен" | **Можно без него!** Но худший случай O(n) без rank. С rank — гарантия O(log n) даже без path compression |
| "α(n) — это O(log n)" | **α(n) < 5 для любого реального n!** Обратная функция Аккермана растёт невероятно медленно. Практически O(1) |
| "Union-Find только для графов" | **Шире!** String grouping (Accounts Merge), equality equations, image segmentation. Везде где есть "группировка" |
| "Нужно отдельно хранить компоненты" | **Нет!** Count уменьшаем при каждом успешном union. components = n - successful_unions |
| "2D grid нельзя в Union-Find" | **Можно!** 2D → 1D: index = row * cols + col. Соседи: (r±1, c), (r, c±1) |

---

## CS-фундамент

| CS-концепция | Применение в Union-Find |
|--------------|-------------------------|
| **Disjoint Set** | Множества без пересечений. Элемент принадлежит ровно одному множеству. Эффективный merge и query |
| **Path Compression** | При find(x) все узлы на пути указывают напрямую на root. Уплощает дерево, ускоряет будущие find |
| **Union by Rank** | Меньшее дерево присоединяется к большему. rank = верхняя граница высоты. Предотвращает длинные цепочки |
| **Inverse Ackermann α(n)** | α(n) < 5 для n < 10^80. Практически константа. Результат комбинации path compression + union by rank |
| **Forest Representation** | Union-Find = лес деревьев. Каждое дерево = одна компонента. Root = representative элемент |
| **Cycle Detection** | Если find(u) == find(v) ДО union → добавление ребра создаёт цикл. Основа Kruskal MST |

---

## Источники

### Теоретические основы

| # | Источник | Вклад |
|---|----------|-------|
| 1 | Tarjan (1975). *Efficiency of a good but not linear set union algorithm* | Оригинальная статья: доказательство O(α(n)) амортизированной сложности |
| 2 | Cormen et al. (2009). *CLRS* — глава 21 (Data Structures for Disjoint Sets) | Формальный анализ path compression и union by rank |

### Практические руководства

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/union-by-rank-and-path-compression-in-union-find-algorithm/) | Tutorial | Оптимизации |
| 2 | [CP-Algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html) | Reference | Формальный анализ |
| 3 | [Princeton Algorithms](https://algs4.cs.princeton.edu/15uf/) | Course | Теория и практика |
| 4 | [TakeUForward](https://takeuforward.org/data-structure/disjoint-set-union-by-rank-union-by-size-path-compression-g-46) | Tutorial | Видео объяснение |

---

## Куда дальше

→ **Применение:** Kruskal's MST Algorithm
→ **Альтернатива:** [[dfs-bfs-patterns]] — для статической связности
→ **Вернуться к:** [[patterns-overview|Обзор паттернов]]


---

## Проверь себя

> [!question]- Почему Union-Find с path compression и union by rank даёт amortized O(alpha(n)) на операцию?
> Path compression: при Find все узлы пути указывают напрямую на корень — следующий Find для этих узлов = O(1). Union by rank: дерево остаётся плоским (высота <= log n). Вместе: amortized O(alpha(n)), где alpha — обратная функция Аккермана, практически <= 4 для всех реальных n.

> [!question]- Задача: Number of Islands с Union-Find. Почему DFS проще, но Union-Find масштабируемее?
> DFS: простая рекурсия, O(m*n). Union-Find: каждая клетка = node, union соседних land-клеток. Сложнее в реализации. Но Union-Find лучше для: dynamic connectivity (острова добавляются/удаляются), параллельной обработки (union thread-safe), streaming данных.

> [!question]- Когда Union-Find лучше BFS/DFS для задач связности?
> Union-Find лучше: 1) Online queries (рёбра добавляются по одному). 2) Dynamic connectivity. 3) Kruskal MST (проверка цикла). 4) Redundant Connection (найти лишнее ребро). BFS/DFS лучше: shortest path, полный обход, задачи на расстояние, задачи на уровни.

## Ключевые карточки

Какие две оптимизации Union-Find?
?
1) Path Compression: при Find(x) все узлы пути перенаправляются на корень. Реализация: parent[x] = Find(parent[x]) рекурсивно. 2) Union by Rank: при Union меньшее дерево присоединяется к большему. Rank = верхняя граница высоты. Вместе: amortized O(alpha(n)).

Как Union-Find обнаруживает цикл в графе?
?
Для каждого ребра (u,v): если Find(u) == Find(v) — они уже в одной компоненте, добавление ребра создаёт цикл. Иначе — Union(u,v). Применение: Kruskal MST (добавляем ребро если не создаёт цикл), Redundant Connection.

Что такое Weighted Union-Find?
?
Расширение: каждое ребро имеет вес/соотношение. Пример: a/b = 2, b/c = 3, тогда a/c = 6. При Union сохраняем weight ratio. При Find обновляем weight по пути. Задача: Evaluate Division (399).

Как Union-Find используется в Kruskal MST?
?
1) Сортировка рёбер по весу. 2) Для каждого ребра (u,v,w): если Find(u) != Find(v) — добавляем в MST, Union(u,v). Иначе — пропускаем (создаёт цикл). 3) Повторяем пока V-1 рёбер. O(E log E + E * alpha(V)).

Сколько памяти нужно Union-Find?
?
O(n): массив parent[n] + массив rank[n] (или size[n]). Никаких дополнительных структур. Очень компактно по сравнению с adjacency list для того же графа. Инициализация: parent[i] = i, rank[i] = 0 для всех.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[patterns/bit-manipulation]] | Битовые манипуляции |
| Углубиться | [[algorithms/minimum-spanning-tree]] | MST с Kruskal + Union-Find |
| Смежная тема | [[patterns/dfs-bfs-patterns]] | DFS/BFS для связности |
| Обзор | [[patterns/patterns-overview]] | Вернуться к карте паттернов |


---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция Union-Find: дружба/острова/электросеть, 6 типичных ошибок, 5 ментальных моделей)*
