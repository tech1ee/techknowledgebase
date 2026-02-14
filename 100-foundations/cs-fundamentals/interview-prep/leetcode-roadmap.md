---
title: "LeetCode Roadmap: планы и стратегия подготовки"
created: 2026-02-09
modified: 2026-02-13
type: guide
status: published
tags:
  - topic/cs-fundamentals
  - type/guide
  - level/intermediate
  - interview
related:
  - "[[mock-interview-guide]]"
  - "[[common-mistakes]]"
  - "[[patterns-overview]]"
prerequisites:
  - "[[problem-solving-framework]]"
  - "[[big-o-complexity]]"
reading_time: 35
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# LeetCode Roadmap: Study Plans & Strategy

## TL;DR

Три главных списка: **Blind 75** (4-6 недель, essentials), **NeetCode 150** (8+ недель, comprehensive), **LeetCode Top 150** (official). Качество > количество: лучше глубоко понять 75 задач, чем поверхностно 300. Используй **UMPIRE метод** для каждой задачи. Spaced repetition для закрепления.

---

## Интуиция

### Аналогия 1: Паттерны как шахматные дебюты

```
ШАХМАТЫ = CODING INTERVIEW:

3000+ задач LeetCode    =    Бесконечные позиции
~20 основных паттернов  =    ~50 основных дебютов

Гроссмейстер не считает все ходы —
он узнаёт знакомые паттерны и применяет изученные идеи.

Two Sum → "Это HashMap паттерн"
Binary Search → "Это монотонная функция"
Subarray Sum → "Это Sliding Window"

Изучи паттерны, не зубри задачи.
```

### Аналогия 2: Blind 75 как MVP подготовки

```
STARTUP = ПОДГОТОВКА К ИНТЕРВЬЮ:

Не нужно:                   Нужно:
300 задач                   75 правильных задач
Все паттерны               Ключевые паттерны
12 месяцев                 4-6 недель

Blind 75 = MVP (Minimum Viable Preparation)
• Покрывает 80% интервью
• Минимум времени
• Максимум ROI

"Perfect is the enemy of good"
```

---

## Частые ошибки

### Ошибка 1: Решать задачи по порядку сложности

**СИМПТОМ:** Месяц на Easy, не дошёл до Medium

```
// НЕПРАВИЛЬНО:
Easy 1, Easy 2, Easy 3... Easy 100 → "Теперь Medium!"

// ПРАВИЛЬНО: По паттернам
Arrays: Easy → Medium → Hard
Trees: Easy → Medium → Hard
DP: Easy → Medium → Hard

Каждый паттерн от простого к сложному.
```

### Ошибка 2: Смотреть решение сразу после затруднения

**СИМПТОМ:** "Понял решение" ≠ "Могу решить сам"

```
// НЕПРАВИЛЬНО:
5 минут думал → не понял → смотрю решение → "Понятно!" → следующая

// ПРАВИЛЬНО (UMPIRE):
U - Understand: 10+ минут разбираться
M - Match: какой паттерн похож?
P - Plan: псевдокод без кода
I - Implement: только теперь код
R - Review: работает?
E - Evaluate: сложность?

Застрял? 30+ минут борьбы, ПОТОМ подсказка.
```

### Ошибка 3: Не повторять решённые задачи

**СИМПТОМ:** Решил месяц назад, забыл как

```
КРИВАЯ ЗАБЫВАНИЯ:
День 1: помню 100%
День 3: помню 70%
День 7: помню 40%
День 30: помню 10%

SPACED REPETITION:
День 1: решил задачу
День 3: повтори (5 минут)
День 7: повтори (3 минуты)
День 14: повтори (2 минуты)
```

---

## Ментальные модели

### Модель 1: "Паттерн → Распознавание → Применение"

```
WORKFLOW ДЛЯ КАЖДОЙ ЗАДАЧИ:

1. РАСПОЗНАЙ ПАТТЕРН:
   "Найти пару элементов" → HashMap / Two Pointers
   "Минимум/максимум на отрезке" → Sliding Window / Monotonic Stack
   "Оптимальный путь" → DP / BFS

2. ПРИМЕНИ ШАБЛОН:
   HashMap паттерн:
   for num in array:
       if target - num in seen:
           return [seen[target-num], i]
       seen[num] = i

3. АДАПТИРУЙ ПОД ЗАДАЧУ
```

### Модель 2: "Time Boxing для каждой задачи"

```
ТАЙМЕР НА КАЖДУЮ ЗАДАЧУ:

Easy:   20 минут (10 думать, 10 кодить)
Medium: 30 минут (15 думать, 15 кодить)
Hard:   45 минут (20 думать, 25 кодить)

НЕ УЛОЖИЛСЯ → Смотри подсказку/решение
             → Через 3 дня повтори БЕЗ решения

Цель: научиться решать за время интервью,
      а не за 2 часа дома.
```

---

## Зачем это нужно?

**Реальная проблема:**

LeetCode имеет 3000+ задач. Без структуры можно потратить месяцы и не подготовиться к интервью. Правильный roadmap экономит время и даёт системное покрытие всех паттернов.

**Статистика:**
- 87% задач на интервью построены на ~20 паттернах
- Blind 75 покрывает ~80% вопросов FAANG
- NeetCode 150 покрывает ~95% вопросов

---

## Выбор Study Plan

### Decision Tree

```
Сколько времени на подготовку?
│
├─ < 4 недель: Blind 75 (только Medium/Hard)
│
├─ 4-6 недель: Blind 75 полностью
│
├─ 8-12 недель: NeetCode 150
│
└─ > 12 недель: NeetCode 150 + LeetCode Premium company tags
```

### Сравнение списков

| Критерий | Blind 75 | NeetCode 150 | LC Top 150 |
|----------|----------|--------------|------------|
| Задач | 75 | 150 | 150 |
| Время | 4-6 нед | 8-12 нед | 8-12 нед |
| Уровень | Experienced | All levels | All levels |
| Видео | Частично | Все | Нет |
| Сложность | Medium-Hard | Easy-Hard | Easy-Hard |
| Coverage | Core patterns | Comprehensive | Official |

### Рекомендация

```
1. Новичок в алгоритмах:
   → NeetCode 150 (есть Easy задачи, видео объяснения)

2. Опытный, нужен refresh:
   → Blind 75 (быстро, только essentials)

3. Targeting FAANG:
   → NeetCode 150 → Company-specific на LC Premium

4. Мало времени:
   → Tech Interview Handbook "50 questions in 5 weeks"
```

---

## UMPIRE Method

Каждую задачу решай по этому framework:

### U — Understand (5-7 минут)

```
Вопросы для уточнения:
□ Какие constraints на input? (size, range, type)
□ Может ли быть пустой input?
□ Есть ли дубликаты?
□ Sorted или unsorted?
□ Что возвращать если нет решения?
□ Какой формат output?

Пример для Two Sum:
- "Может ли target быть отрицательным?"
- "Гарантирован ли ровно один ответ?"
- "Можно ли использовать один элемент дважды?"
```

### M — Match (2-3 минуты)

```
Определи паттерн:
□ Sorted array? → Binary Search / Two Pointers
□ Substring/Subarray? → Sliding Window
□ Tree/Graph traversal? → DFS/BFS
□ Find optimal? → DP / Greedy
□ Connected components? → Union-Find
□ Dependencies? → Topological Sort
□ Next greater? → Monotonic Stack
```

### P — Plan (3-5 минут)

```
1. Опиши brute force
2. Определи bottleneck
3. Оптимизируй
4. Напиши псевдокод

Пример:
"Brute force: O(n²) — проверить все пары.
Bottleneck: поиск complement за O(n).
Optimization: HashMap для O(1) lookup.
Итого: O(n) time, O(n) space."
```

### I — Implement (15-20 минут)

```kotlin
// Важно комментировать ПОЧЕМУ вы делаете каждый шаг!
fun twoSum(nums: IntArray, target: Int): IntArray {
    // Используем HashMap: ключ = число, значение = его индекс
    // HashMap даёт O(1) поиск — вместо O(n) перебора второго числа
    val map = mutableMapOf<Int, Int>()

    for ((i, num) in nums.withIndex()) {
        val complement = target - num

        // ВАЖНО: сначала проверяем, потом добавляем текущее число!
        // Если добавить сначала, то num может найти сам себя как complement
        // Пример: [3, 3], target=6 → 3 не должен использоваться дважды
        map[complement]?.let { return intArrayOf(it, i) }

        map[num] = i
    }

    // По условию задачи решение ВСЕГДА существует
    // Этот код никогда не выполнится, но компилятору нужен return
    throw IllegalArgumentException("No solution")
}
```

### R — Review (3-5 минут)

```
Checklist:
□ Синтаксические ошибки?
□ Off-by-one errors?
□ Правильные границы циклов?
□ Все переменные инициализированы?
□ Return statement во всех ветках?
□ Edge cases:
  - Empty input
  - Single element
  - All same elements
  - Negative numbers
```

### E — Evaluate (2-3 минуты)

```
Time Complexity:
- Какие операции в цикле?
- Nested loops?
- Sorting? → O(n log n)
- Heap operations? → O(log n) each

Space Complexity:
- Дополнительные структуры?
- Рекурсия? → Stack space O(depth)

Trade-offs:
"Можно O(1) space с сортировкой, но тогда O(n log n) time"
```

---

## Три разбора задач: от Easy до Hard

Теория паттернов бесполезна без практики РАССУЖДЕНИЙ. Ниже -- три задачи разного уровня. Для каждой разбираем не код, а МЫШЛЕНИЕ: как подступиться, какие ловушки, почему именно этот паттерн.

---

### Разбор 1 (Easy): Valid Parentheses (LeetCode #20)

**Условие:** Дана строка из символов `()[]{}`. Определить, является ли она валидной (каждая открывающая скобка имеет соответствующую закрывающую, и порядок правильный).

**Шаг 1: Понять задачу глубже, чем кажется.**

На первый взгляд кажется, что нужно просто посчитать скобки. Строка `"()"` -- валидна, `")("` -- нет. Но простой подсчёт не работает: строка `"([)]"` имеет равное количество открывающих и закрывающих скобок каждого типа, но невалидна. Почему? Потому что скобки должны закрываться в правильном ПОРЯДКЕ: последняя открытая должна закрыться первой. Это принцип LIFO -- Last In, First Out.

**Шаг 2: Распознать паттерн.**

LIFO -- это стек. Каждый раз, когда мы видим открывающую скобку, мы "откладываем" её на стек (ожидаем соответствующую закрывающую). Когда видим закрывающую -- проверяем, совпадает ли она с верхушкой стека. Если нет -- невалидно. Если стек пуст, а закрывающая пришла -- невалидно. Если в конце стек не пуст -- остались незакрытые скобки, невалидно.

**Шаг 3: Ловушки.**

Ловушка 1: Пустая строка. Это валидный ввод? По условию LeetCode -- да, пустая строка считается валидной. Ловушка 2: Строка из одного символа -- всегда невалидна. Ловушка 3: Только открывающие скобки `"((("` -- стек не пуст в конце, невалидно. Ловушка 4: Закрывающая без пары `")(` -- стек пуст, когда приходит `")"`.

**Шаг 4: Сложность.**

O(n) по времени (один проход по строке), O(n) по памяти (стек в худшем случае хранит все символы). Можно ли лучше? Нет: мы должны посмотреть на каждый символ хотя бы раз.

> **Инсайт:** Stack -- не просто структура данных. Это способ мышления: "отложи текущую задачу и вернись к ней позже". Скобки, вызовы функций, undo-операции -- везде стек.

---

### Разбор 2 (Medium): 3Sum (LeetCode #15)

**Условие:** Дан массив целых чисел. Найти все уникальные тройки (a, b, c), такие что a + b + c = 0.

**Шаг 1: Начать с brute force.**

Три вложенных цикла: для каждой пары (i, j) ищем k такой, что nums[i] + nums[j] + nums[k] = 0. Сложность O(n^3). Для n = 3000 (типичный constraint) это 2.7 * 10^10 операций -- слишком медленно.

**Шаг 2: Сократить измерение задачи.**

Two Sum решается за O(n) с HashMap. 3Sum можно свести к Two Sum: фиксируем первый элемент a = nums[i], и ищем пару (b, c) такую что b + c = -a. Это превращает 3Sum в n вызовов Two Sum, т.е. O(n^2). Но Two Sum с HashMap возвращает индексы, а нам нужны уникальные значения -- возникает проблема дубликатов.

**Шаг 3: Почему Two Pointers лучше HashMap здесь.**

Если отсортировать массив (O(n log n), что не ухудшает общий O(n^2)), можно использовать Two Pointers вместо HashMap. Для каждого i фиксируем left = i + 1, right = n - 1. Если сумма меньше нуля -- двигаем left вправо (увеличиваем сумму). Если больше -- двигаем right влево (уменьшаем). Если равна нулю -- нашли тройку.

Преимущество сортировки: дубликаты стоят рядом. Чтобы избежать повторных троек, пропускаем одинаковые значения: если nums[i] == nums[i-1], пропускаем i. Аналогично для left и right после нахождения решения.

**Шаг 4: Ловушки.**

Ловушка 1: Не пропустить дубликаты. Массив [-1, -1, -1, 2] должен вернуть одну тройку [-1, -1, 2], не три. Ловушка 2: Отрицательные числа. Многие забывают, что все три элемента могут быть отрицательными (если target != 0 в обобщённой задаче). Ловушка 3: Overflow. Для больших значений сумма трёх int может выйти за пределы int. На LeetCode это обычно не проблема, но на интервью стоит спросить.

**Шаг 5: Сложность.**

O(n^2) по времени (сортировка + n * two-pointer проход), O(1) или O(n) по памяти (зависит от алгоритма сортировки). Для n = 3000 это 9 * 10^6 операций -- комфортно.

> **Инсайт:** Когда задача требует найти k элементов с определённым свойством, попробуйте свести kSum к (k-1)Sum. 3Sum → 2Sum, 4Sum → 3Sum → 2Sum. Сортировка -- ваш друг для устранения дубликатов.

---

### Разбор 3 (Hard): Trapping Rain Water (LeetCode #42)

**Условие:** Дан массив неотрицательных целых чисел, представляющих карту высот (ширина каждого столбца = 1). Вычислить, сколько воды может быть собрано после дождя.

**Шаг 1: Визуализировать.**

Это задача, где рисунок решает всё. Массив [0,1,0,2,1,0,1,3,2,1,2,1] выглядит как:

```
      #
  #   ## #
 ## ####_##
____________
 0102101 3212 1
```

Вода заполняет "ямы" между стенками. Сколько воды над каждым столбцом? Интуитивно: над столбцом i помещается столько воды, сколько позволяет НИЖНЯЯ из двух стен -- максимальная высота слева и максимальная высота справа. Вода "стекает" через более низкую стену.

**Шаг 2: Формализовать.**

Для каждого столбца i: `water[i] = min(max_left[i], max_right[i]) - height[i]`. Если результат отрицательный -- воды нет (столбец выше стен). max_left[i] = максимальная высота среди height[0..i]. max_right[i] = максимальная высота среди height[i..n-1].

**Шаг 3: Три подхода -- от O(n^2) к O(n).**

Подход 1 (Brute Force): Для каждого i вычисляем max_left и max_right двумя проходами. O(n) на столбец, O(n^2) всего. Работает, но медленно.

Подход 2 (Prefix/Suffix Arrays): Предвычисляем max_left[] одним проходом слева направо, max_right[] -- справа налево. Третий проход считает воду. O(n) по времени, O(n) по памяти.

Подход 3 (Two Pointers): Можно ли O(n) по времени и O(1) по памяти? Да! Ключевое наблюдение: если max_left[i] < max_right[i], вода определяется max_left[i] (более низкая стена). И наоборот. Мы не обязаны знать ТОЧНУЮ максимальную высоту с обеих сторон -- достаточно знать, какая сторона ниже.

Ставим left = 0, right = n - 1. Поддерживаем left_max и right_max. Если left_max < right_max, вода над left определяется left_max -- обрабатываем left и двигаем вправо. Иначе обрабатываем right и двигаем влево.

**Шаг 4: Почему Two Pointers работает.**

Это самая трудная часть для понимания. Когда left_max < right_max, мы ЗНАЕМ, что правая стена достаточно высокая, чтобы удержать воду высотой left_max. Неважно, что справа от right -- мы уже знаем, что right_max >= left_max. Вода определяется более НИЗКОЙ стеной, и она слева.

**Шаг 5: Ловушки.**

Ловушка 1: height[i] может быть 0 -- столбца нет, но вода всё равно может быть. Ловушка 2: Массив из 1-2 элементов -- воды быть не может (нужны минимум 3 элемента). Ловушка 3: Монотонно возрастающий/убывающий массив -- воды тоже нет. Ловушка 4: Все элементы одинаковые -- воды нет.

> **Инсайт:** Задачи с "ловушкой воды" учат важному приёму -- вычислять свойство каждого элемента через его КОНТЕКСТ (что слева и справа). Prefix/suffix arrays -- мощный паттерн для таких задач. Two Pointers -- элегантная оптимизация, когда нужна информация с обоих концов.

---

## Как распознать паттерн по условию задачи

Одна из главных трудностей на интервью -- понять КАКОЙ паттерн применить. Вот фреймворк принятия решений, основанный на ключевых сигналах в условии:

```
DECISION FRAMEWORK: Сигнал → Паттерн

"Найти пару/тройку с суммой X"
  → Sorted? → Two Pointers
  → Unsorted? → HashMap (complement lookup)

"Найти подстроку/подмассив с условием"
  → Фиксированный размер? → Sliding Window (fixed)
  → Переменный размер? → Sliding Window (variable)
  → Нужны все подстроки? → Возможно, DP

"Оптимальный путь / минимальная стоимость"
  → Дерево решений? → DFS/BFS
  → Подзадачи перекрываются? → DP
  → Жадный выбор оптимален? → Greedy

"K-й элемент / top K"
  → Несортированный массив? → Heap (PQ) или Quick Select
  → Stream данных? → Два Heap'а

"Все комбинации / перестановки"
  → Backtracking (DFS с откатом)

"Связные компоненты / циклы"
  → Union-Find или DFS

"Следующий больший / предыдущий меньший"
  → Monotonic Stack

"Зависимости / порядок выполнения"
  → Topological Sort (Kahn's BFS или DFS)

"Поиск в отсортированном"
  → Binary Search
  → "Отсортированное" может быть неявным:
    монотонная функция → Binary Search by answer

"Дерево: обход / свойство"
  → DFS (preorder/inorder/postorder)
  → Уровни? → BFS (level-order)
```

Этот фреймворк -- не волшебная палочка. Многие задачи комбинируют паттерны: Binary Search + Greedy, BFS + DP, Stack + Two Pointers. Но он даёт отправную точку для размышлений.

> **Практический совет:** После каждой решённой задачи запишите: "Какой сигнал в условии указывал на паттерн?" Через 50-100 задач распознавание станет автоматическим, как у шахматиста, который видит знакомую позицию.

---

## Распределение по паттернам

### NeetCode 150 Breakdown

| Категория | Задач | Приоритет | Ключевые проблемы |
|-----------|-------|-----------|-------------------|
| Arrays & Hashing | 9 | P0 | Two Sum, Top K Frequent |
| Two Pointers | 5 | P0 | 3Sum, Container With Water |
| Sliding Window | 6 | P0 | Longest Substring, Min Window |
| Stack | 7 | P0 | Valid Parentheses, Daily Temps |
| Binary Search | 7 | P0 | Search Rotated, Koko Bananas |
| Linked List | 11 | P1 | Reverse, Merge K Lists |
| Trees | 15 | P0 | Invert, Max Depth, LCA |
| Tries | 3 | P2 | Implement Trie, Word Search II |
| Heap/PQ | 7 | P1 | Find Median, Task Scheduler |
| Backtracking | 9 | P1 | Subsets, Permutations, N-Queens |
| Graphs | 13 | P1 | Clone Graph, Course Schedule |
| Advanced Graphs | 6 | P2 | Dijkstra, MST |
| 1D DP | 12 | P0 | Climbing Stairs, House Robber |
| 2D DP | 11 | P1 | Unique Paths, LCS |
| Greedy | 8 | P1 | Jump Game, Gas Station |
| Intervals | 6 | P1 | Merge Intervals, Meeting Rooms |
| Math & Geometry | 8 | P2 | Rotate Image, Spiral Matrix |
| Bit Manipulation | 7 | P2 | Single Number, Counting Bits |

### Weekly Study Plan (8 weeks)

```
Week 1: Arrays & Hashing + Two Pointers
  - 14 problems
  - Focus: HashMap, sorting, pointer techniques

Week 2: Sliding Window + Stack
  - 13 problems
  - Focus: Window expansion/contraction, monotonic stack

Week 3: Binary Search + Linked List
  - 18 problems
  - Focus: Search space, list manipulation

Week 4: Trees (Part 1)
  - 8 problems
  - Focus: Traversals, recursion patterns

Week 5: Trees (Part 2) + Tries
  - 10 problems
  - Focus: BST operations, prefix trees

Week 6: Heap + Backtracking
  - 16 problems
  - Focus: Priority queue, exhaustive search

Week 7: Graphs + DP (Part 1)
  - 19 problems
  - Focus: DFS/BFS, basic DP

Week 8: DP (Part 2) + Greedy + Review
  - 17 problems + weak areas
  - Focus: 2D DP, greedy proofs

Week 9+: Mock interviews + Company-specific
```

---

## Spaced Repetition System

### Leitner System для LeetCode

```
Box 1: Новые задачи → Review каждый день
Box 2: Решил 1 раз → Review через 3 дня
Box 3: Решил 2 раза → Review через 1 неделю
Box 4: Решил 3 раза → Review через 2 недели
Box 5: Mastered → Review через месяц

Если не решил без подсказок → вернуть в Box 1
```

### Tracking Template

```markdown
| Problem | Pattern | Box | Last Review | Next Review |
|---------|---------|-----|-------------|-------------|
| Two Sum | HashMap | 4 | 2025-12-20 | 2025-01-03 |
| 3Sum | Two Ptr | 2 | 2025-12-28 | 2025-12-31 |
| ...     | ...     | ... | ...         | ...         |
```

---

## Время на одну задачу

### По сложности

| Difficulty | Target Time | Reality Check |
|------------|-------------|---------------|
| Easy | 15-20 min | Если > 30 min → изучи паттерн |
| Medium | 25-35 min | Если > 45 min → допустима подсказка |
| Hard | 40-60 min | Если > 60 min → смотри решение |

### Правило 20 минут

```
Застрял > 20 минут без прогресса?
│
├─ Не понимаю задачу → Перечитай, нарисуй пример
│
├─ Не вижу подход → Посмотри hint / подумай о паттерне
│
└─ Знаю подход, не могу реализовать → Посмотри решение

ВАЖНО: После подсказки — реши заново через 3 дня
```

---

## Распространённые ловушки

### 1. Random grinding

```
❌ НЕПРАВИЛЬНО: Решать задачи случайно

✅ ПРАВИЛЬНО: Группировать по паттернам
   Week 1: Все Two Pointers задачи
   Week 2: Все Sliding Window задачи
   → Паттерн закрепляется
```

### 2. Смотреть решение слишком быстро

```
❌ НЕПРАВИЛЬНО: Застрял 5 минут → смотрю решение

✅ ПРАВИЛЬНО:
   1. Подумай 20+ минут
   2. Попробуй brute force
   3. Посмотри hint (не решение)
   4. Если всё ещё нет → решение
   5. Закрой и реши сам
   6. Вернись через 3 дня
```

### 3. Не анализировать ошибки

```
❌ НЕПРАВИЛЬНО: Решил → забыл

✅ ПРАВИЛЬНО: После каждой задачи записать:
   - Какой паттерн?
   - Где застрял?
   - Какой insight помог?
   - Что сделал бы по-другому?
```

### 4. Игнорировать Easy задачи

```
❌ НЕПРАВИЛЬНО: Easy слишком простые, пропускаю

✅ ПРАВИЛЬНО: Easy задачи учат:
   - Базовые паттерны
   - Edge cases handling
   - Clean code practices
   - Скорость реализации
```

---

## Company-Specific Preparation

### FAANG Focus Areas

| Company | Focus | Top Problems |
|---------|-------|--------------|
| Google | Graphs, DP, Strings | LRU Cache, Word Ladder, Merge K Lists |
| Meta | Arrays, Trees, Design | Add Two Numbers, Merge Intervals, LCA |
| Amazon | Arrays, Design, Greedy | Two Sum, LRU Cache, Merge Intervals |
| Apple | Strings, Arrays, Trees | Valid Palindrome, Binary Tree Level Order |
| Microsoft | Arrays, Trees, DP | Two Sum, LCA, Maximum Subarray |

### LeetCode Premium Value

```
Worth it if:
+ Targeting specific company
+ 8+ weeks to prepare
+ Need company-specific questions
+ Want frequency data

Not worth if:
- General preparation
- < 4 weeks time
- Already know patterns well
```

---

## Progress Tracking

### Weekly Metrics

```
Track each week:
□ Problems solved: ___ / target
□ New patterns learned: ___
□ Problems reviewed (spaced rep): ___
□ Mock interviews done: ___
□ Weak areas identified: ___
```

### Readiness Checklist

```
Ready for interviews when:
□ Can solve Medium in < 30 min consistently
□ Recognize patterns in < 3 min
□ Know time/space complexity without thinking
□ Can explain approach clearly
□ Handle edge cases automatically
□ Done 3+ mock interviews
□ Completed target list (75/150)
```

---

## Ресурсы

### Обязательные

| Ресурс | Тип | Описание |
|--------|-----|----------|
| [NeetCode.io](https://neetcode.io) | Platform | 150 задач с видео |
| [Blind 75](https://neetcode.io/practice/practice/blind75) | List | Original Blind 75 |
| [Tech Interview Handbook](https://www.techinterviewhandbook.org) | Guide | Best practices |
| [LeetCode Patterns](https://seanprashad.com/leetcode-patterns/) | Reference | Grouped by pattern |

### Дополнительные

| Ресурс | Тип | Когда |
|--------|-----|-------|
| LeetCode Premium | Platform | Company-specific prep |
| AlgoExpert | Course | Prefer video learning |
| Grokking Coding Interview | Course | Pattern-first approach |
| LeetCode Discuss | Forum | Alternative solutions |

---

## Связь с другими темами

**[[common-mistakes]]** -- типичные ошибки на интервью. После изучения roadmap'а и паттернов, перед mock-интервью обязательно разберите самые частые причины провалов. Многие кандидаты знают паттерны, но теряются из-за плохой коммуникации или игнорирования edge cases.

**[[mock-interview-guide]]** -- практика с обратной связью. Решение задач в одиночку -- это только половина подготовки. Mock-интервью тренируют навыки, которые невозможно развить одному: объяснение хода мысли, работа под давлением, реакция на подсказки.

**[[problem-solving-framework]]** -- общая методология решения задач. UMPIRE -- это специализация этого фреймворка для coding-интервью. Понимание общих принципов problem solving помогает в незнакомых ситуациях, когда ни один паттерн не подходит напрямую.

---

## Источники и дальнейшее чтение

- **Halim, S. (2013). Competitive Programming 3.** -- Наиболее полная классификация задач по паттернам. Главы 3-4 покрывают все основные алгоритмические техники с сотнями задач. Незаменимо для систематической подготовки.

- **Skiena, S. (2020). The Algorithm Design Manual, 3rd Ed.** -- Отличный "мост" между теоретическими алгоритмами и практическим решением задач. "War Stories" в каждой главе показывают, как паттерны применяются в реальных проектах.

- **NeetCode (neetcode.io)** -- Видео-разборы 150 задач с объяснением рассуждений. Лучший ресурс для тех, кто учится распознавать паттерны.

- **Tech Interview Handbook (techinterviewhandbook.org)** -- Создатели Blind 75. Практические советы по тайм-менеджменту, коммуникации и выбору задач для подготовки.


---

## Проверь себя

> [!question]- Почему Blind 75 считается минимально достаточным набором и чем он лучше случайных 75 задач?
> Blind 75 покрывает все основные паттерны (Two Pointers, Binary Search, DP, Trees, Graphs, etc.) с минимальным пересечением. Каждая задача — представитель класса. Случайные 75 могут пропустить целый паттерн или дать 10 задач одного типа. Blind 75 = минимальный покрывающий набор для интервью.

> [!question]- Как спaced repetition помогает в подготовке к LeetCode и какой оптимальный интервал?
> Кривая забывания: без повторения решение забывается за 3-7 дней. SR: повтор через 1, 3, 7, 14, 30 дней. Не перерешивать, а пересмотреть подход и ключевую идею. Для каждой задачи: записать паттерн + trick + edge cases. Ревизия 10 задач за 15 мин (только подход, не код).

> [!question]- Задача решена, но за 45 минут вместо 20. Стоит ли идти дальше или практиковать скорость?
> Скорость критична: на интервью 20-25 мин на задачу. Повторять задачи для скорости: re-solve через 3 дня, цель < 15 мин. Скорость приходит от understanding, не от memorization. Если 45 мин из-за debugging — практикуй чистый код. Если из-за approach — углуби понимание паттерна.

## Ключевые карточки

Что такое Blind 75?
?
75 задач LeetCode, покрывающих все основные паттерны. Создан разработчиком из Meta. Категории: Array, Binary, DP, Graph, Interval, Linked List, Matrix, String, Tree, Heap. 4-6 недель интенсивной подготовки. Достаточно для большинства FAANG интервью.

Чем NeetCode 150 отличается от Blind 75?
?
NeetCode 150 = расширенный Blind 75: больше задач на каждый паттерн, добавлены категории (Backtracking, Tries, Math). Видео-объяснения для каждой задачи. 8+ недель подготовки. Лучше для глубокого понимания. Порядок: Blind 75 сначала, потом NeetCode 150.

Что такое UMPIRE метод?
?
U: Understand (уточнить условия). M: Match (определить паттерн). P: Plan (описать алгоритм). I: Implement (написать код). R: Review (проверить). E: Evaluate (сложность). Используй для каждой задачи на интервью. Предотвращает 'jump to code' ошибку.

Как организовать подготовку по неделям?
?
Неделя 1-2: Array, String, Two Pointers, Sliding Window. Неделя 3-4: Stack, Binary Search, Linked List. Неделя 5-6: Trees, Graphs, BFS/DFS. Неделя 7-8: DP, Backtracking, Heap. Ежедневно: 2-3 задачи + review предыдущих. Mock interview раз в неделю.

Когда переходить от Easy к Medium?
?
Easy < 15 мин стабильно -> переходи к Medium. Medium покрывает 70% интервью. Easy для фундамента, Medium для подготовки, Hard для продвинутых позиций. Соотношение: 30% Easy, 50% Medium, 20% Hard. На интервью: обычно 1 Medium или Easy+Medium.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[interview-prep/mock-interview-guide]] | Mock интервью для практики |
| Углубиться | [[interview-prep/common-mistakes]] | Типичные ошибки на интервью |
| Смежная тема | [[patterns/patterns-overview]] | Паттерны для решения задач |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |


---

*Последнее обновление: 2026-02-10 -- Добавлены 3 полных разбора задач (Easy: Valid Parentheses, Medium: 3Sum, Hard: Trapping Rain Water) с рассуждениями и ловушками, Decision Framework для распознавания паттернов по условию задачи*
