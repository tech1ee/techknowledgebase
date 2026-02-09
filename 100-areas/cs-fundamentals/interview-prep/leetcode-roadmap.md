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

## Связанные темы

### Prerequisites
- Базовое знание Data Structures
- Понимание Big-O notation
- Один язык программирования

### Следующие шаги
- [Common Mistakes](./common-mistakes.md) — типичные ошибки
- [Mock Interview Guide](./mock-interview-guide.md) — практика
- System Design (для Senior+)

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [NeetCode](https://neetcode.io) | Platform | Study list |
| 2 | [Tech Interview Handbook](https://www.techinterviewhandbook.org/best-practice-questions/) | Guide | Blind 75 origin |
| 3 | [LeetCopilot](https://leetcopilot.dev/blog/neetcode-150-review-is-it-enough) | Blog | Study strategies |
| 4 | [CodePath](https://guides.codepath.com/compsci/UMPIRE-Interview-Strategy) | Guide | UMPIRE method |
| 5 | [Design Gurus](https://www.designgurus.io/blog/coding-interview-prep-roadmap-2025) | Blog | Timeline |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
