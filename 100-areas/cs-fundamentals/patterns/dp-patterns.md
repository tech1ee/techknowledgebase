# Dynamic Programming Patterns

---
title: "Dynamic Programming Patterns"
created: 2025-12-29
updated: 2026-01-06
type: deep-dive
status: complete
difficulty: advanced
confidence: high
cs-foundations:
  - optimal-substructure
  - overlapping-subproblems
  - memoization-caching
  - tabulation-iteration
  - state-space-design
  - recurrence-relations
prerequisites:
  - "[[recursion-fundamentals]]"
  - "[[big-o-complexity]]"
  - "[[arrays-strings]]"
related:
  - "[[backtracking]]"
  - "[[greedy-algorithms]]"
tags:
  - pattern
  - dynamic-programming
  - memoization
  - tabulation
  - optimization
  - interview
---

## TL;DR

DP решает задачи с **overlapping subproblems** и **optimal substructure** через кэширование результатов. **Top-down** (рекурсия + memo) vs **Bottom-up** (итеративно). Пять основных паттернов: **Fibonacci** (зависимость от предыдущих), **0/1 Knapsack** (выбрать/не выбрать), **LCS** (две последовательности), **LIS** (возрастающая подпоследовательность), **Grid DP** (пути в матрице).

---

## Часть 1: Интуиция без кода

### Главная идея DP: Меняем время на память

> "The intuition behind dynamic programming is that we trade space for time—instead of calculating all the states taking a lot of time but no space, we take up space to store the results of all the sub-problems to save time later." — [HackerEarth](https://www.hackerearth.com/practice/algorithms/dynamic-programming/introduction-to-dynamic-programming-1/tutorial/)

```
Аналогия: ЭКЗАМЕН С ШПАРГАЛКОЙ

Без DP (наивная рекурсия):
┌─────────────────────────────────────────────────────┐
│ Преподаватель: "Чему равно fib(5)?"                 │
│                                                     │
│ Студент: Думает... fib(5) = fib(4) + fib(3)         │
│          fib(4) = fib(3) + fib(2)   ← вычисляет     │
│          fib(3) = fib(2) + fib(1)   ← вычисляет     │
│          fib(3) = fib(2) + fib(1)   ← СНОВА!        │
│          fib(2) = fib(1) + fib(0)   ← и это снова   │
│          ...                                        │
│ Время: 2^n операций — ОЧЕНЬ ДОЛГО                   │
└─────────────────────────────────────────────────────┘

С DP (мемоизация):
┌─────────────────────────────────────────────────────┐
│ Преподаватель: "Чему равно fib(5)?"                 │
│                                                     │
│ Студент со ШПАРГАЛКОЙ:                              │
│   📝 fib(0) = 0 ✓                                   │
│   📝 fib(1) = 1 ✓                                   │
│   📝 fib(2) = 1 ✓ (записал)                         │
│   📝 fib(3) = 2 ✓ (записал, fib(2) уже есть!)       │
│   📝 fib(4) = 3 ✓ (записал, fib(3) уже есть!)       │
│   📝 fib(5) = 5 ✓ (fib(4) и fib(3) уже есть!)       │
│                                                     │
│ Время: n операций — МГНОВЕННО                       │
└─────────────────────────────────────────────────────┘
```

### Аналогия 1: Рецепт с полуфабрикатами

```
Задача: Приготовить сложное блюдо (Торт Наполеон)

❌ БЕЗ DP (каждый раз с нуля):
   Гость 1 просит торт → делаешь тесто, крем, выпекаешь, собираешь
   Гость 2 просит торт → СНОВА делаешь тесто, крем, выпекаешь...
   Гость 3 просит торт → СНОВА делаешь тесто, крем...

   Время: 3 часа × 3 = 9 часов

✅ С DP (полуфабрикаты):
   Утром: сделал 10 порций теста 📝
          сделал 10 порций крема 📝
          выпек 10 коржей 📝

   Гость 1 → собираешь из готового (5 минут)
   Гость 2 → собираешь из готового (5 минут)
   Гость 3 → собираешь из готового (5 минут)

   Время: 3 часа подготовки + 15 минут = 3.25 часа

СУТЬ DP: Заранее вычисли и сохрани то, что будет
         использоваться многократно!
```

### Аналогия 2: Задача про лестницу (визуально)

```
Задача: Сколько способов подняться на 5-ю ступеньку?
        (за раз можно подняться на 1 или 2 ступеньки)

              ┌───┐
           5  │   │  ← СЮДА нужно попасть
              ├───┤
           4  │ 5 │  ← 5 способов дойти до 4-й
              ├───┤
           3  │ 3 │  ← 3 способа дойти до 3-й
              ├───┤
           2  │ 2 │  ← 2 способа дойти до 2-й
              ├───┤
           1  │ 1 │  ← 1 способ дойти до 1-й
              ├───┤
         СТАРТ│   │
              └───┘

КЛЮЧЕВОЕ НАБЛЮДЕНИЕ:
На 5-ю ступеньку можно попасть ТОЛЬКО двумя путями:
  1. С 4-й ступеньки (шаг 1)
  2. С 3-й ступеньки (шаг 2)

Значит: способов(5) = способов(4) + способов(3)
                     = 5 + 3 = 8

Это и есть РЕКУРРЕНТНОЕ СООТНОШЕНИЕ — сердце DP!
```

### Аналогия 3: Рюкзак туриста (0/1 Knapsack)

```
Ты идёшь в поход. Рюкзак выдержит только 10 кг.
Какие вещи взять, чтобы получить максимум пользы?

┌──────────────┬────────┬───────────┐
│ Предмет      │ Вес    │ Польза    │
├──────────────┼────────┼───────────┤
│ Палатка      │ 6 кг   │ ⭐⭐⭐⭐⭐ 50 │
│ Спальник     │ 3 кг   │ ⭐⭐⭐ 30   │
│ Еда на 3 дня │ 4 кг   │ ⭐⭐⭐⭐ 40  │
│ Кружка       │ 1 кг   │ ⭐ 10      │
└──────────────┴────────┴───────────┘

❌ Наивный перебор: 2^4 = 16 комбинаций проверить

✅ DP-подход: Для каждого предмета решаем:
   "Если у меня осталось X кг, брать этот предмет или нет?"

   И ЗАПИСЫВАЕМ ответы в таблицу!

   Оптимальный набор: Спальник (3 кг) + Еда (4 кг) + Кружка (1 кг)
   Итого: 8 кг, польза = 30 + 40 + 10 = 80

   (Палатка не влезла бы с едой: 6 + 4 > 10)
```

### Визуализация: Top-Down vs Bottom-Up

```
                    fib(5)
                   /      \
              fib(4)      fib(3)
             /     \      /    \
        fib(3)  fib(2) fib(2) fib(1)
        /    \
    fib(2) fib(1)

TOP-DOWN (Мемоизация):
┌────────────────────────────────────────────────────────┐
│ Начинаем СВЕРХУ с fib(5)                               │
│ "Мне нужен fib(4)... а для него fib(3)... и т.д."      │
│                                                        │
│ Идём ВНИЗ, записывая по пути:                          │
│   memo = {}                                            │
│   fib(5) → нужен fib(4), fib(3)                        │
│   fib(4) → нужен fib(3), fib(2) → вычислили, записали  │
│   fib(3) → УЖЕ В MEMO! Возвращаем                      │
│                                                        │
│ 💡 "Ленивое" вычисление — только то, что нужно         │
└────────────────────────────────────────────────────────┘

BOTTOM-UP (Табуляция):
┌────────────────────────────────────────────────────────┐
│ Начинаем СНИЗУ с известных значений                    │
│                                                        │
│   dp[0] = 0  ← базовый случай                          │
│   dp[1] = 1  ← базовый случай                          │
│   dp[2] = dp[0] + dp[1] = 1                            │
│   dp[3] = dp[1] + dp[2] = 2                            │
│   dp[4] = dp[2] + dp[3] = 3                            │
│   dp[5] = dp[3] + dp[4] = 5  ← ОТВЕТ                   │
│                                                        │
│ 💡 Заполняем таблицу от базы до ответа                 │
└────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему DP сложный (типичные ошибки)

> "Common pitfalls: Skipping the recursive brute-force step; not writing down the state clearly before coding; trying to memorize solutions without internalizing the problem structure." — [LeetCode Discussion](https://leetcode.com/discuss/post/5583619/Learning-the-Art-of-Intuition-for-Solving-Dynamic-Programming-Problems/)

### Ошибка 1: Прыгнули сразу к DP, минуя рекурсию

```
❌ НЕПРАВИЛЬНО (сразу пишем DP):
   "Так, dp[i] = ... эммм... что-то там..."
   Результат: запутался, ошибки, не работает

✅ ПРАВИЛЬНО (пошаговый подход):

   ШАГ 1: Наивная рекурсия (brute force)
   fun fib(n: Int): Int {
       if (n <= 1) return n
       return fib(n-1) + fib(n-2)  // Работает, но медленно!
   }

   ШАГ 2: Добавляем мемоизацию
   val memo = mutableMapOf<Int, Int>()
   fun fib(n: Int): Int {
       if (n <= 1) return n
       return memo.getOrPut(n) { fib(n-1) + fib(n-2) }
   }

   ШАГ 3: (Опционально) Переписываем bottom-up
   fun fib(n: Int): Int {
       val dp = IntArray(n + 1)
       dp[0] = 0; dp[1] = 1
       for (i in 2..n) dp[i] = dp[i-1] + dp[i-2]
       return dp[n]
   }

ПРАВИЛО: Brute Force → Memoization → Tabulation
```

### Ошибка 2: Не определили STATE чётко

```
❌ НЕПРАВИЛЬНО:
   "dp[i][j] = ... что-то связанное с i и j..."

   Что такое i? Что такое j? Что хранит dp[i][j]?
   Непонятно → ошибки в transition

✅ ПРАВИЛЬНО (явное определение):

   ЗАДАЧА: Longest Common Subsequence для s1 и s2

   STATE: dp[i][j] = длина LCS для s1[0..i-1] и s2[0..j-1]
                     │              │              │
                     ЧТО хранит     КАКАЯ часть    КАКАЯ часть
                                    первой строки  второй строки

   Теперь transition очевиден:
   если s1[i-1] == s2[j-1]:
       dp[i][j] = dp[i-1][j-1] + 1  // Добавляем совпавший символ
   иначе:
       dp[i][j] = max(dp[i-1][j], dp[i][j-1])  // Пропускаем один из символов
```

### Ошибка 3: Забыли базовые случаи

```
❌ НЕПРАВИЛЬНО:
   for (i in 1..n) {
       dp[i] = dp[i-1] + dp[i-2]  // dp[0] и dp[1] не определены!
   }

   Результат: dp[2] = undefined + undefined = NaN или 0

✅ ПРАВИЛЬНО:
   dp[0] = 0  // ← БАЗОВЫЙ СЛУЧАЙ
   dp[1] = 1  // ← БАЗОВЫЙ СЛУЧАЙ

   for (i in 2..n) {
       dp[i] = dp[i-1] + dp[i-2]  // Теперь всё определено!
   }

ПРАВИЛО: Всегда начинай с вопроса:
         "Что я знаю ТОЧНО без вычислений?"
```

### Ошибка 4: Неправильный порядок циклов в Knapsack

```
Задача: 0/1 Knapsack (каждый предмет можно взять ОДИН раз)

❌ НЕПРАВИЛЬНО (слева направо):
   for (num in nums) {
       for (j in num..target) {  // СЛЕВА НАПРАВО
           dp[j] = dp[j] || dp[j - num]
       }
   }

   Пример: nums = [3], target = 6
   Начало: dp = [T, F, F, F, F, F, F]
   j=3: dp[3] = dp[3] || dp[0] = T  → dp = [T,F,F,T,F,F,F]
   j=6: dp[6] = dp[6] || dp[3] = T  → dp = [T,F,F,T,F,F,T]

   ОШИБКА! dp[6] = true означает "можно набрать 6 из [3]"
   Но 3 использовали ДВАЖДЫ (3+3=6)!

✅ ПРАВИЛЬНО (справа налево):
   for (num in nums) {
       for (j in target downTo num) {  // СПРАВА НАЛЕВО
           dp[j] = dp[j] || dp[j - num]
       }
   }

   j=6: dp[6] = dp[6] || dp[3] = F || F = F  (dp[3] ещё старый!)
   j=3: dp[3] = dp[3] || dp[0] = F || T = T

   Результат: dp[6] = false — ПРАВИЛЬНО!
```

### Ошибка 5: Off-by-one в индексах

```
Задача: LCS для "abc" и "ac"

❌ НЕПРАВИЛЬНО:
   for (i in 0 until m) {
       for (j in 0 until n) {
           if (s1[i] == s2[j]) {
               dp[i][j] = dp[i-1][j-1] + 1  // i=0 → dp[-1][...]!
           }
       }
   }

   ArrayIndexOutOfBoundsException!

✅ ПРАВИЛЬНО (индексы со сдвигом +1):
   // dp[i][j] соответствует s1[0..i-1] и s2[0..j-1]
   // dp[0][...] и dp[...][0] — пустые строки (базовый случай = 0)

   for (i in 1..m) {
       for (j in 1..n) {
           if (s1[i-1] == s2[j-1]) {  // i-1 и j-1!
               dp[i][j] = dp[i-1][j-1] + 1
           }
       }
   }
```

---

## Часть 3: Ментальные модели

### Модель 1: DP = Рекурсия + Кэш

> "Top-Down: Start solving the problem by breaking it down. If you see that the problem has been solved already, return the saved answer. If not, solve it and save." — [Stack Overflow Blog](https://stackoverflow.blog/2022/01/31/the-complete-beginners-guide-to-dynamic-programming/)

```
ЛЮБУЮ DP-задачу можно решить так:

1. Напиши рекурсию (brute force)
2. Добавь HashMap для кэша
3. Готово!

┌─────────────────────────────────────────────────────────┐
│                                                         │
│   fun solve(state): Result {                            │
│       // 1. Базовый случай                              │
│       if (state is base) return baseAnswer              │
│                                                         │
│       // 2. Проверка кэша                               │
│       if (state in cache) return cache[state]           │
│                                                         │
│       // 3. Рекурсивное вычисление                      │
│       result = combine(solve(substate1),                │
│                        solve(substate2), ...)           │
│                                                         │
│       // 4. Сохранение в кэш                            │
│       cache[state] = result                             │
│       return result                                     │
│   }                                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

Это УНИВЕРСАЛЬНЫЙ шаблон для 90% DP задач!
```

**Когда использовать:** Когда начинаешь решать любую DP задачу — начни с этого шаблона.

### Модель 2: Определи STATE и TRANSITION

```
DP = STATE + TRANSITION + BASE CASES

┌────────────────────────────────────────────────────────┐
│ STATE (Состояние)                                      │
│   "Какая минимальная информация нужна для ответа?"     │
│                                                        │
│   Примеры:                                             │
│   • dp[i] — ответ для первых i элементов               │
│   • dp[i][j] — ответ для подзадачи с параметрами i, j  │
│   • dp[mask] — ответ для подмножества (bitmask)        │
├────────────────────────────────────────────────────────┤
│ TRANSITION (Переход)                                   │
│   "Как связаны большие состояния с меньшими?"          │
│                                                        │
│   Примеры:                                             │
│   • dp[i] = dp[i-1] + dp[i-2]         (Fibonacci)      │
│   • dp[i] = max(dp[i-1], dp[i-2]+a[i]) (House Robber)  │
│   • dp[i][j] = dp[i-1][j-1] + 1        (LCS match)     │
├────────────────────────────────────────────────────────┤
│ BASE CASES (Базовые случаи)                            │
│   "Что я знаю точно без вычислений?"                   │
│                                                        │
│   Примеры:                                             │
│   • dp[0] = 0, dp[1] = 1              (Fibonacci)      │
│   • dp[0] = 1                         (Coin Change II) │
│   • dp[i][0] = 0, dp[0][j] = 0        (LCS)            │
└────────────────────────────────────────────────────────┘
```

**Когда использовать:** При проектировании решения — начни с определения этих трёх компонентов.

### Модель 3: Распознавание паттерна по ключевым словам

> "One way to realize whether DP is applicable: if the problem asks for minimum/maximum cost or count number of ways." — [Educative](https://www.educative.io/blog/leetcode-dynamic-programming)

```
┌────────────────────────────────────────────────────────┐
│                  KEYWORD → PATTERN                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  "minimum steps/cost"         → DP (минимизация)       │
│  "maximum profit/value"       → DP (максимизация)      │
│  "count ways/combinations"    → DP (подсчёт)           │
│  "is it possible?"            → DP (булева таблица)    │
│  "longest/shortest sequence"  → LIS/LCS паттерн        │
│                                                        │
│  "take or leave each item"    → 0/1 Knapsack           │
│  "unlimited usage"            → Unbounded Knapsack     │
│  "two strings compare"        → LCS / Edit Distance    │
│  "path in grid"               → Grid DP                │
│  "depends on previous"        → Fibonacci pattern      │
│                                                        │
└────────────────────────────────────────────────────────┘

Примеры:
• "Minimum coins to make amount" → Unbounded Knapsack
• "Number of ways to climb stairs" → Fibonacci
• "Longest common subsequence" → LCS
• "Maximum path sum in grid" → Grid DP
```

**Когда использовать:** При первом чтении условия задачи.

### Модель 4: Оптимизация памяти — Rolling Array

```
НАБЛЮДЕНИЕ: Часто dp[i] зависит только от dp[i-1] (и dp[i-2])

Fibonacci:
┌──────────────────────────────────────────────────────┐
│ БЫЛО: dp = [0, 1, 1, 2, 3, 5, 8, ...]                │
│       Память: O(n)                                   │
│                                                      │
│ СТАЛО:                                               │
│       prev1 = 0                                      │
│       prev2 = 1                                      │
│       for i in 2..n:                                 │
│           curr = prev1 + prev2                       │
│           prev1 = prev2                              │
│           prev2 = curr                               │
│       Память: O(1)                                   │
└──────────────────────────────────────────────────────┘

2D Grid DP:
┌──────────────────────────────────────────────────────┐
│ БЫЛО: dp[m][n] — полная таблица                      │
│       Память: O(m×n)                                 │
│                                                      │
│ НАБЛЮДЕНИЕ: dp[i][j] зависит только от              │
│             dp[i-1][j] и dp[i][j-1]                  │
│                                                      │
│ СТАЛО: Храним только текущую и предыдущую строку    │
│       prev = [...], curr = [...]                    │
│       Память: O(n)                                   │
│                                                      │
│ ИЛИ ДАЖЕ: Только одну строку!                       │
│       dp[j] += dp[j-1]  (старый dp[j] = "сверху")   │
│       Память: O(n)                                   │
└──────────────────────────────────────────────────────┘
```

**Когда использовать:** После того как решение работает — для оптимизации памяти.

### Модель 5: 5 основных паттернов покрывают 80% задач

```
┌─────────────────────────────────────────────────────────┐
│          80% DP ЗАДАЧ = 5 ПАТТЕРНОВ                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. FIBONACCI PATTERN                                   │
│     dp[i] = f(dp[i-1], dp[i-2], ...)                    │
│     Примеры: Climbing Stairs, House Robber              │
│                                                         │
│  2. 0/1 KNAPSACK                                        │
│     "Взять или не взять?" для каждого элемента          │
│     Примеры: Partition Equal Subset, Target Sum         │
│                                                         │
│  3. UNBOUNDED KNAPSACK                                  │
│     Элементы можно брать неограниченно                  │
│     Примеры: Coin Change, Rod Cutting                   │
│                                                         │
│  4. LCS (Longest Common Subsequence)                    │
│     Две последовательности → общая часть                │
│     Примеры: LCS, Edit Distance, Shortest Common Super  │
│                                                         │
│  5. GRID DP                                             │
│     Пути в матрице                                      │
│     Примеры: Unique Paths, Min Path Sum, Maximal Square │
│                                                         │
└─────────────────────────────────────────────────────────┘

БОНУС-ПАТТЕРНЫ:
• LIS (Longest Increasing Subsequence)
• Kadane's Algorithm (Maximum Subarray)
• Interval DP (Matrix Chain Multiplication)
• Bitmask DP (Travelling Salesman)
```

**Когда использовать:** Определи паттерн → примени соответствующий шаблон.

---

## Зачем это нужно?

**Реальная проблема:**

Fibonacci наивной рекурсией: fib(50) требует ~2^50 = 10^15 вызовов.
С DP (мемоизация): fib(50) требует 50 вызовов.

Разница: от "вселенная умрёт раньше" до "мгновенно".

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| Финансы | Portfolio optimization | Knapsack вариации |
| Биоинформатика | Sequence alignment | Edit Distance, LCS |
| Маршрутизация | Shortest paths | Bellman-Ford, Floyd |
| Компиляторы | Code optimization | Register allocation |
| NLP | Speech recognition | Viterbi algorithm |
| Игры | AI decision making | Game theory DP |

**Статистика:**
- ~20% задач LeetCode требуют DP
- Top-5 самых частых тем на FAANG интервью
- Coin Change, House Robber, LCS — топ-10 по частоте

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Рекурсия** | DP строится на рекурсивном мышлении | [[recursion-fundamentals]] |
| **Big O нотация** | Понимание оптимизации O(2^n) → O(n) | [[big-o-complexity]] |
| **Массивы** | 1D/2D DP таблицы | [[arrays-strings]] |
| **Hash Tables** | Для мемоизации (top-down) | [[hash-tables]] |
| **CS: Рекуррентные соотношения** | dp[i] = f(dp[i-1], dp[i-2], ...) | Дискретная математика |
| **CS: Mathematical Induction** | Доказательство корректности DP | Математические основы |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что ты поднимаешься по лестнице. За раз можешь подняться на 1 или 2 ступеньки.

```
Лестница из 4 ступенек:
  ___
 |   |4
 |___|
 |   |3
 |___|
 |   |2
 |___|
 |   |1
 |___|
```

Сколько способов подняться? Вместо того чтобы перебирать ВСЕ варианты, заметим:
- Чтобы попасть на ступеньку 4, нужно прийти с 3 (шаг 1) ИЛИ с 2 (шаг 2)
- Способов на 4 = способов на 3 + способов на 2!

Это и есть DP — используем уже вычисленные ответы для новых!

### Формальное определение

**Dynamic Programming** — метод оптимизации, который решает сложные задачи, разбивая их на перекрывающиеся подзадачи, решая каждую подзадачу один раз и сохраняя результат.

**Два ключевых свойства:**

1. **Optimal Substructure** — оптимальное решение задачи содержит оптимальные решения подзадач

2. **Overlapping Subproblems** — одни и те же подзадачи решаются многократно

**Два подхода:**

```
TOP-DOWN (Memoization)
├── Рекурсия сверху вниз
├── Кэширование при первом вычислении
└── "Ленивое" вычисление — только нужные подзадачи

BOTTOM-UP (Tabulation)
├── Итерация снизу вверх
├── Заполнение таблицы в порядке зависимостей
└── "Жадное" вычисление — все подзадачи
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **State** | Минимальная информация для ответа | `dp[i]` = способов до i |
| **Transition** | Связь между состояниями | `dp[i] = dp[i-1] + dp[i-2]` |
| **Base Case** | Начальные известные значения | `dp[0] = 1, dp[1] = 1` |
| **Memoization** | Кэш для рекурсии | `Map<State, Result>` |
| **Tabulation** | Таблица для итерации | `Array<Result>` |
| **Dimension** | Количество параметров состояния | 1D, 2D, 3D... |
| **Space Optimization** | Уменьшение памяти | Хранить только последние состояния |

---

## Основные паттерны

### 1. Fibonacci Pattern (Linear DP)

```
Когда использовать:
- dp[i] зависит от dp[i-1], dp[i-2], ...
- Ответ — один параметр (индекс)

Примеры:
- Climbing Stairs: dp[i] = dp[i-1] + dp[i-2]
- House Robber: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
- Decode Ways: dp[i] = dp[i-1] + dp[i-2] (если валидно)

Оптимизация памяти: O(n) → O(1) — храним только 2 последних значения
```

### 2. 0/1 Knapsack Pattern

```
Когда использовать:
- Есть набор элементов
- Для каждого: взять или не взять (0 или 1)
- Ограничение (вес, сумма, количество)
- Цель: максимизировать/минимизировать

State: dp[i][w] = макс. ценность с первыми i предметами и ёмкостью w

Transition: dp[i][w] = max(
    dp[i-1][w],           // не берём предмет i
    dp[i-1][w-weight[i]] + value[i]  // берём предмет i
)

Примеры:
- Partition Equal Subset Sum
- Target Sum
- Last Stone Weight II
```

### 3. Unbounded Knapsack Pattern

```
Когда использовать:
- То же что 0/1, но можно брать неограниченно

Transition: dp[i][w] = max(
    dp[i-1][w],           // не берём предмет i
    dp[i][w-weight[i]] + value[i]  // берём предмет i (i, не i-1!)
)

Примеры:
- Coin Change (минимум монет)
- Coin Change II (количество способов)
- Rod Cutting
```

### 4. LCS Pattern (Longest Common Subsequence)

```
Когда использовать:
- Две последовательности
- Найти общую подпоследовательность
- Минимальные изменения (edit distance)

State: dp[i][j] = LCS для s1[0..i-1] и s2[0..j-1]

Transition:
  if s1[i-1] == s2[j-1]:
      dp[i][j] = dp[i-1][j-1] + 1
  else:
      dp[i][j] = max(dp[i-1][j], dp[i][j-1])

Примеры:
- Longest Common Subsequence
- Edit Distance
- Shortest Common Supersequence
```

### 5. LIS Pattern (Longest Increasing Subsequence)

```
Когда использовать:
- Одна последовательность
- Найти подпоследовательность с условием (возрастающая, битоническая)

State (O(n²)): dp[i] = длина LIS заканчивающейся на i

Transition: dp[i] = max(dp[j] + 1) для всех j < i где nums[j] < nums[i]

Оптимизация (O(n log n)): Binary Search + patience sort

Примеры:
- Longest Increasing Subsequence
- Russian Doll Envelopes
- Number of Longest Increasing Subsequence
```

### 6. Grid DP Pattern

```
Когда использовать:
- Матрица/сетка
- Пути из угла в угол
- Движение: вправо, вниз (или другие направления)

State: dp[i][j] = ответ для позиции (i,j)

Transition: dp[i][j] = f(dp[i-1][j], dp[i][j-1], ...)

Примеры:
- Unique Paths
- Minimum Path Sum
- Dungeon Game
- Maximal Square
```

---

## Как это работает?

### Climbing Stairs (Fibonacci Pattern)

```
n = 5 ступенек

Top-Down:
  climb(5) → нужны climb(4), climb(3)
  climb(4) → нужны climb(3), climb(2)  ← climb(3) уже в кэше!
  climb(3) → нужны climb(2), climb(1)
  ...

Bottom-Up:
  dp[1] = 1
  dp[2] = 2
  dp[3] = dp[1] + dp[2] = 3
  dp[4] = dp[2] + dp[3] = 5
  dp[5] = dp[3] + dp[4] = 8  ← ответ

Space Optimized:
  prev1 = 1, prev2 = 2
  for i in 3..5:
      curr = prev1 + prev2
      prev1 = prev2
      prev2 = curr
  return prev2 = 8
```

### 0/1 Knapsack

```
items = [(weight=1, value=1), (w=2, v=6), (w=3, v=10)]
capacity = 5

Таблица dp[i][w]:

     w: 0  1  2  3  4  5
  i=0:  0  0  0  0  0  0   (нет предметов)
  i=1:  0  1  1  1  1  1   (+предмет 1: w=1, v=1)
  i=2:  0  1  6  7  7  7   (+предмет 2: w=2, v=6)
  i=3:  0  1  6 10 11 16   (+предмет 3: w=3, v=10)
                        ↑
                      ответ = 16

Backtrack: dp[3][5]=16 включает предмет 3 (w=3, v=10)
           dp[2][2]=6 включает предмет 2 (w=2, v=6)
           Итого: предметы 2 и 3, value = 16
```

### LCS (Longest Common Subsequence)

```
s1 = "ABCDE", s2 = "ACE"

Таблица dp[i][j]:

      ""  A  C  E
  "":  0  0  0  0
  A:   0  1  1  1   (A совпало)
  B:   0  1  1  1
  C:   0  1  2  2   (C совпало)
  D:   0  1  2  2
  E:   0  1  2  3   (E совпало)
              ↑
           ответ = 3, LCS = "ACE"
```

---

## Сложность операций

| Паттерн | Время | Память | С оптимизацией |
|---------|-------|--------|----------------|
| Fibonacci | O(n) | O(n) | O(1) |
| 0/1 Knapsack | O(n×W) | O(n×W) | O(W) |
| Unbounded Knapsack | O(n×W) | O(n×W) | O(W) |
| LCS | O(n×m) | O(n×m) | O(min(n,m)) |
| LIS (naive) | O(n²) | O(n) | — |
| LIS (optimized) | O(n log n) | O(n) | — |
| Grid DP | O(n×m) | O(n×m) | O(m) |

---

## Реализация

### Kotlin

```kotlin
// ═══════════════════════════════════════════════════════════════════════════
// FIBONACCI PATTERN: CLIMBING STAIRS
// ═══════════════════════════════════════════════════════════════════════════

// Top-Down (Memoization)
fun climbStairsTopDown(n: Int): Int {
    val memo = mutableMapOf<Int, Int>()

    fun dp(i: Int): Int {
        /**
         * Базовые случаи:
         * i=1 → 1 способ (один шаг)
         * i=2 → 2 способа (1+1 или 2)
         */
        if (i <= 2) return i
        return memo.getOrPut(i) { dp(i - 1) + dp(i - 2) }
    }

    return dp(n)
}

// Bottom-Up (Tabulation)
fun climbStairsBottomUp(n: Int): Int {
    if (n <= 2) return n

    val dp = IntArray(n + 1)
    dp[1] = 1
    dp[2] = 2

    for (i in 3..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }

    return dp[n]
}

// Space Optimized O(1)
fun climbStairs(n: Int): Int {
    if (n <= 2) return n

    /**
     * Оптимизация памяти: храним только 2 последних значения
     *
     * prev1 = dp[i-2] (на 2 ступени назад)
     * prev2 = dp[i-1] (на 1 ступень назад)
     *
     * Пример: n=5
     * Начало: prev1=1 (dp[1]), prev2=2 (dp[2])
     * i=3: curr=1+2=3, prev1=2, prev2=3
     * i=4: curr=2+3=5, prev1=3, prev2=5
     * i=5: curr=3+5=8, prev1=5, prev2=8
     * Ответ: 8
     */
    var prev1 = 1
    var prev2 = 2

    for (i in 3..n) {
        val curr = prev1 + prev2
        prev1 = prev2
        prev2 = curr
    }

    return prev2
}

// ═══════════════════════════════════════════════════════════════════════════
// FIBONACCI PATTERN: HOUSE ROBBER
// ═══════════════════════════════════════════════════════════════════════════

fun rob(nums: IntArray): Int {
    if (nums.isEmpty()) return 0
    if (nums.size == 1) return nums[0]

    /**
     * prev1 = максимальная добыча БЕЗ предыдущего дома
     * prev2 = максимальная добыча ВКЛЮЧАЯ предыдущий дом
     *
     * Для каждого дома с деньгами num выбираем:
     * 1. Не грабим текущий → берём prev2
     * 2. Грабим текущий → берём prev1 + num (пропустили предыдущий)
     *
     * ПОШАГОВЫЙ ПРИМЕР: [2, 7, 9, 3, 1]
     * Начало: prev1=0, prev2=0
     * num=2: curr=max(0, 0+2)=2, prev1=0, prev2=2
     * num=7: curr=max(2, 0+7)=7, prev1=2, prev2=7
     * num=9: curr=max(7, 2+9)=11, prev1=7, prev2=11
     * num=3: curr=max(11, 7+3)=11, prev1=11, prev2=11
     * num=1: curr=max(11, 11+1)=12, prev1=11, prev2=12
     * Ответ: 12 (грабим дома 1,3,5: 2+9+1=12)
     */
    var prev1 = 0
    var prev2 = 0

    for (num in nums) {
        // Выбор: взять текущий (prev1 + num) или пропустить (prev2)
        val curr = maxOf(prev2, prev1 + num)
        prev1 = prev2
        prev2 = curr
    }

    return prev2
}

// ═══════════════════════════════════════════════════════════════════════════
// 0/1 KNAPSACK PATTERN: PARTITION EQUAL SUBSET SUM
// ═══════════════════════════════════════════════════════════════════════════

fun canPartition(nums: IntArray): Boolean {
    val sum = nums.sum()
    // Нечётную сумму невозможно разделить на 2 равные части
    // Пример: sum=11 → 11/2 = 5.5, не целое число
    if (sum % 2 != 0) return false

    val target = sum / 2

    /**
     * dp[j] = можно ли набрать сумму j из элементов массива
     *
     * ПОШАГОВЫЙ ПРИМЕР: nums = [1, 5, 11, 5], sum = 22, target = 11
     *
     * Начало: dp = [T, F, F, F, F, F, F, F, F, F, F, F]
     *                0  1  2  3  4  5  6  7  8  9 10 11
     *
     * num=1:  dp = [T, T, F, F, F, F, F, F, F, F, F, F]
     * num=5:  dp = [T, T, F, F, F, T, T, F, F, F, F, F]
     * num=11: dp = [T, T, F, F, F, T, T, F, F, F, F, T] ← dp[11]=true!
     *
     * Ответ: true (подмножество {11} или {1,5,5} даёт 11)
     */
    val dp = BooleanArray(target + 1)
    // Базовый случай: сумму 0 ВСЕГДА можно набрать (пустое подмножество)
    dp[0] = true

    for (num in nums) {
        /**
         * Идём СПРАВА НАЛЕВО (от target до num)
         *
         * Почему? Если идти слева направо, мы можем использовать
         * один и тот же элемент несколько раз (это не 0/1 knapsack!)
         *
         * Справа налево: когда обновляем dp[j], dp[j-num] ещё "старое"
         */
        for (j in target downTo num) {
            dp[j] = dp[j] || dp[j - num]
        }
    }

    return dp[target]
}

// ═══════════════════════════════════════════════════════════════════════════
// 0/1 KNAPSACK PATTERN: TARGET SUM
// ═══════════════════════════════════════════════════════════════════════════

fun findTargetSumWays(nums: IntArray, target: Int): Int {
    val sum = nums.sum()

    /**
     * МАТЕМАТИЧЕСКОЕ ПРЕОБРАЗОВАНИЕ:
     *
     * Пусть P = сумма чисел со знаком +
     * Пусть N = сумма чисел со знаком -
     *
     * P - N = target  (по условию)
     * P + N = sum     (сумма всех чисел)
     *
     * Складываем: 2P = target + sum
     * Значит: P = (target + sum) / 2
     *
     * Задача свелась к: "сколько подмножеств с суммой P?"
     *
     * Пример: nums=[1,1,1,1,1], target=3
     * sum=5, P=(3+5)/2=4
     * Ищем подмножества с суммой 4: {1,1,1,1} (4 способа выбрать 4 из 5 единиц)
     */
    if ((target + sum) % 2 != 0 || target + sum < 0) return 0

    val subsetSum = (target + sum) / 2

    val dp = IntArray(subsetSum + 1)
    // Один способ набрать сумму 0 — не брать ничего
    dp[0] = 1

    for (num in nums) {
        for (j in subsetSum downTo num) {
            dp[j] += dp[j - num]
        }
    }

    return dp[subsetSum]
}

// ═══════════════════════════════════════════════════════════════════════════
// UNBOUNDED KNAPSACK: COIN CHANGE (Minimum coins)
// ═══════════════════════════════════════════════════════════════════════════

fun coinChange(coins: IntArray, amount: Int): Int {
    /**
     * dp[i] = минимальное количество монет для суммы i
     *
     * Инициализация: amount + 1 — это "бесконечность"
     * Почему amount + 1? Максимум нужно amount монет (все по 1)
     * Если после вычислений dp[amount] > amount, значит невозможно
     *
     * ПОШАГОВЫЙ ПРИМЕР: coins=[1,2,5], amount=11
     *
     * dp = [0, ∞, ∞, ∞, ∞, ∞, ∞, ∞, ∞, ∞, ∞, ∞]
     *       0  1  2  3  4  5  6  7  8  9  10 11
     *
     * i=1: dp[1] = min(∞, dp[0]+1) = 1
     * i=2: dp[2] = min(∞, dp[1]+1, dp[0]+1) = 1
     * i=5: dp[5] = min(∞, dp[4]+1, dp[3]+1, dp[0]+1) = 1
     * ...
     * i=11: dp[11] = 3 (монеты: 5+5+1)
     */
    val dp = IntArray(amount + 1) { amount + 1 }
    dp[0] = 0  // Для суммы 0 нужно 0 монет

    for (i in 1..amount) {
        for (coin in coins) {
            if (coin <= i) {
                dp[i] = minOf(dp[i], dp[i - coin] + 1)
            }
        }
    }

    return if (dp[amount] > amount) -1 else dp[amount]
}

// ═══════════════════════════════════════════════════════════════════════════
// UNBOUNDED KNAPSACK: COIN CHANGE II (Number of ways)
// ═══════════════════════════════════════════════════════════════════════════

fun change(amount: Int, coins: IntArray): Int {
    // dp[i] = количество способов набрать сумму i
    val dp = IntArray(amount + 1)
    dp[0] = 1

    /**
     * ВАЖНО: порядок циклов определяет комбинации vs перестановки!
     *
     * Внешний по монетам, внутренний по суммам → КОМБИНАЦИИ
     * (1+2 и 2+1 считаются как ОДИН способ)
     *
     * Внешний по суммам, внутренний по монетам → ПЕРЕСТАНОВКИ
     * (1+2 и 2+1 считаются как ДВА способа)
     *
     * ПОШАГОВЫЙ ПРИМЕР: coins=[1,2,5], amount=5
     *
     * После coin=1: dp = [1,1,1,1,1,1] (только единицами)
     * После coin=2: dp = [1,1,2,2,3,3] (добавили двойки)
     * После coin=5: dp = [1,1,2,2,3,4] (добавили пятёрку)
     *
     * 4 способа: {5}, {2+2+1}, {2+1+1+1}, {1+1+1+1+1}
     */
    for (coin in coins) {
        for (i in coin..amount) {
            dp[i] += dp[i - coin]
        }
    }

    return dp[amount]
}

// ═══════════════════════════════════════════════════════════════════════════
// LCS PATTERN: LONGEST COMMON SUBSEQUENCE
// ═══════════════════════════════════════════════════════════════════════════

fun longestCommonSubsequence(text1: String, text2: String): Int {
    val m = text1.length
    val n = text2.length

    /**
     * dp[i][j] = длина LCS для text1[0..i-1] и text2[0..j-1]
     *
     * ПОШАГОВЫЙ ПРИМЕР: text1="abcde", text2="ace"
     *
     *     ""  a  c  e
     * ""   0  0  0  0
     * a    0  1  1  1
     * b    0  1  1  1
     * c    0  1  2  2
     * d    0  1  2  2
     * e    0  1  2  3  ← ответ: 3 ("ace")
     *
     * Если символы равны: берём диагональ + 1
     * Если разные: max(сверху, слева)
     */
    val dp = Array(m + 1) { IntArray(n + 1) }

    for (i in 1..m) {
        for (j in 1..n) {
            if (text1[i - 1] == text2[j - 1]) {
                // Символы совпали → добавляем к LCS и берём диагональ
                dp[i][j] = dp[i - 1][j - 1] + 1
            } else {
                // Символы разные → берём максимум из "без последнего из text1" или "без последнего из text2"
                dp[i][j] = maxOf(dp[i - 1][j], dp[i][j - 1])
            }
        }
    }

    return dp[m][n]
}

// Space Optimized O(min(m,n))
fun longestCommonSubsequenceOptimized(text1: String, text2: String): Int {
    val (short, long) = if (text1.length < text2.length) text1 to text2 else text2 to text1
    val m = short.length
    val n = long.length

    var prev = IntArray(m + 1)
    var curr = IntArray(m + 1)

    for (i in 1..n) {
        for (j in 1..m) {
            if (long[i - 1] == short[j - 1]) {
                curr[j] = prev[j - 1] + 1
            } else {
                curr[j] = maxOf(prev[j], curr[j - 1])
            }
        }
        // Swap: prev становится curr, curr становится prev
        // Используем also для атомарного обмена в одну строку
        prev = curr.also { curr = prev }
    }

    return prev[m]
}

// ═══════════════════════════════════════════════════════════════════════════
// LCS PATTERN: EDIT DISTANCE
// ═══════════════════════════════════════════════════════════════════════════

fun minDistance(word1: String, word2: String): Int {
    val m = word1.length
    val n = word2.length

    /**
     * dp[i][j] = минимум операций для преобразования
     * word1[0..i-1] → word2[0..j-1]
     *
     * ПОШАГОВЫЙ ПРИМЕР: "horse" → "ros"
     *
     *     ""  r  o  s
     * ""   0  1  2  3
     * h    1  1  2  3
     * o    2  2  1  2
     * r    3  2  2  2
     * s    4  3  3  2
     * e    5  4  4  3  ← ответ: 3 операции
     *
     * Операции: horse → rorse (replace h→r) → rose (delete r) → ros (delete e)
     */
    val dp = Array(m + 1) { IntArray(n + 1) }

    /**
     * Базовые случаи:
     * dp[i][0] = i операций (удалить все i символов)
     * dp[0][j] = j операций (вставить все j символов)
     */
    for (i in 0..m) dp[i][0] = i
    for (j in 0..n) dp[0][j] = j

    for (i in 1..m) {
        for (j in 1..n) {
            if (word1[i - 1] == word2[j - 1]) {
                // Символы равны — бесплатно, берём диагональ
                dp[i][j] = dp[i - 1][j - 1]
            } else {
                /**
                 * Три варианта (выбираем минимум + 1 операция):
                 * - dp[i-1][j]: удалить символ из word1
                 * - dp[i][j-1]: вставить символ в word1
                 * - dp[i-1][j-1]: заменить символ
                 */
                dp[i][j] = 1 + minOf(
                    dp[i - 1][j],     // delete
                    dp[i][j - 1],     // insert
                    dp[i - 1][j - 1]  // replace
                )
            }
        }
    }

    return dp[m][n]
}

// ═══════════════════════════════════════════════════════════════════════════
// LIS PATTERN: LONGEST INCREASING SUBSEQUENCE
// ═══════════════════════════════════════════════════════════════════════════

// O(n²) solution
fun lengthOfLIS(nums: IntArray): Int {
    val n = nums.size
    /**
     * dp[i] = длина наибольшей возрастающей подпоследовательности,
     * ЗАКАНЧИВАЮЩЕЙСЯ на элементе nums[i]
     *
     * Инициализация: 1, потому что сам элемент — LIS длины 1
     *
     * ПОШАГОВЫЙ ПРИМЕР: nums = [10, 9, 2, 5, 3, 7, 101, 18]
     *
     * dp = [1, 1, 1, 1, 1, 1, 1, 1] — начальное
     * i=3 (num=5): 2 < 5 → dp[3] = max(1, dp[2]+1) = 2
     * i=4 (num=3): 2 < 3 → dp[4] = max(1, dp[2]+1) = 2
     * i=5 (num=7): 2,5,3 < 7 → dp[5] = max(dp[2],dp[3],dp[4])+1 = 3
     * ...
     * Ответ: max(dp) = 4 (подпоследовательность [2,3,7,101] или [2,5,7,101])
     */
    val dp = IntArray(n) { 1 }

    for (i in 1 until n) {
        for (j in 0 until i) {
            if (nums[j] < nums[i]) {
                dp[i] = maxOf(dp[i], dp[j] + 1)
            }
        }
    }

    return dp.max()
}

// O(n log n) solution with Binary Search
fun lengthOfLISOptimized(nums: IntArray): Int {
    /**
     * tails[i] = минимальный последний элемент LIS длины (i+1)
     *
     * КЛЮЧЕВАЯ ИДЕЯ:
     * - Если num > все элементы в tails → расширяем LIS
     * - Иначе → заменяем первый элемент >= num
     *
     * Замена НЕ ломает LIS! Мы просто запоминаем,
     * что есть "лучший" (меньший) конец для той же длины
     *
     * ПОШАГОВЫЙ ПРИМЕР: nums = [10, 9, 2, 5, 3, 7, 101]
     *
     * num=10: tails = [10]
     * num=9:  tails = [9]      ← заменили 10 на 9 (меньший конец для длины 1)
     * num=2:  tails = [2]      ← заменили 9 на 2
     * num=5:  tails = [2, 5]   ← 5 > 2, расширили
     * num=3:  tails = [2, 3]   ← заменили 5 на 3 (меньший конец для длины 2)
     * num=7:  tails = [2, 3, 7]   ← 7 > 3, расширили
     * num=101: tails = [2, 3, 7, 101] ← расширили
     *
     * Ответ: tails.size = 4
     */
    val tails = mutableListOf<Int>()

    for (num in nums) {
        val pos = tails.binarySearch(num).let { if (it < 0) -it - 1 else it }
        if (pos == tails.size) {
            // Новый максимум — увеличиваем длину LIS
            tails.add(num)
        } else {
            // Нашли меньший конец для LIS той же длины
            tails[pos] = num
        }
    }

    return tails.size
}

// ═══════════════════════════════════════════════════════════════════════════
// GRID DP: UNIQUE PATHS
// ═══════════════════════════════════════════════════════════════════════════

fun uniquePaths(m: Int, n: Int): Int {
    /**
     * dp[i][j] = количество уникальных путей до клетки (i, j)
     *
     * Инициализация: все 1, потому что первая строка и столбец
     * имеют только один путь (вправо или вниз)
     *
     * ПОШАГОВЫЙ ПРИМЕР: m=3, n=3
     *
     * 1  1  1
     * 1  2  3
     * 1  3  6  ← ответ: 6 путей
     *
     * Формула: dp[i][j] = dp[i-1][j] + dp[i][j-1]
     * (сверху + слева, т.к. можно прийти только оттуда)
     */
    val dp = Array(m) { IntArray(n) { 1 } }

    for (i in 1 until m) {
        for (j in 1 until n) {
            // Пути сверху + пути слева
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
        }
    }

    return dp[m - 1][n - 1]
}

// Space Optimized O(n)
fun uniquePathsOptimized(m: Int, n: Int): Int {
    /**
     * Оптимизация памяти: храним только одну строку
     *
     * dp[j] — "сверху" (старое значение из предыдущей строки)
     * dp[j-1] — "слева" (новое значение из текущей строки)
     *
     * dp[j] += dp[j-1] эквивалентно dp[j] = dp[j] + dp[j-1]
     */
    val dp = IntArray(n) { 1 }

    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[j] += dp[j - 1]
        }
    }

    return dp[n - 1]
}

// ═══════════════════════════════════════════════════════════════════════════
// GRID DP: MINIMUM PATH SUM
// ═══════════════════════════════════════════════════════════════════════════

fun minPathSum(grid: Array<IntArray>): Int {
    val m = grid.size
    val n = grid[0].size

    /**
     * In-place модификация: grid[i][j] становится минимальной суммой пути до (i,j)
     *
     * ПОШАГОВЫЙ ПРИМЕР:
     * Исходная сетка:     После обработки:
     * 1  3  1             1  4  5
     * 1  5  1      →      2  7  6
     * 4  2  1             6  8  7  ← ответ: 7
     *
     * Путь: 1→3→1→1→1 = 7
     */
    for (i in 0 until m) {
        for (j in 0 until n) {
            when {
                // Начальная точка — не меняем
                i == 0 && j == 0 -> { }
                // Первая строка — можно прийти только слева
                i == 0 -> grid[i][j] += grid[i][j - 1]
                // Первый столбец — можно прийти только сверху
                j == 0 -> grid[i][j] += grid[i - 1][j]
                // Остальные — минимум из сверху и слева
                else -> grid[i][j] += minOf(grid[i - 1][j], grid[i][j - 1])
            }
        }
    }

    return grid[m - 1][n - 1]
}

// ═══════════════════════════════════════════════════════════════════════════
// KADANE'S ALGORITHM: MAXIMUM SUBARRAY
// ═══════════════════════════════════════════════════════════════════════════

fun maxSubArray(nums: IntArray): Int {
    /**
     * Алгоритм Кадане (Kadane's Algorithm)
     *
     * maxEndingHere = максимальная сумма подмассива, ЗАКАНЧИВАЮЩЕГОСЯ здесь
     * maxSoFar = глобальный максимум
     *
     * ПОШАГОВЫЙ ПРИМЕР: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
     *
     * i=0: maxEndingHere = -2, maxSoFar = -2
     * i=1: maxEndingHere = max(1, -2+1) = 1, maxSoFar = 1
     * i=2: maxEndingHere = max(-3, 1-3) = -2, maxSoFar = 1
     * i=3: maxEndingHere = max(4, -2+4) = 4, maxSoFar = 4
     * i=4: maxEndingHere = max(-1, 4-1) = 3, maxSoFar = 4
     * i=5: maxEndingHere = max(2, 3+2) = 5, maxSoFar = 5
     * i=6: maxEndingHere = max(1, 5+1) = 6, maxSoFar = 6 ✓
     *
     * Ответ: 6 (подмассив [4, -1, 2, 1])
     */
    var maxSoFar = nums[0]
    var maxEndingHere = nums[0]

    for (i in 1 until nums.size) {
        /**
         * Ключевое решение на каждом шаге:
         * 1. Начать новый подмассив с nums[i]
         * 2. Продолжить текущий: maxEndingHere + nums[i]
         *
         * Выбираем максимум из двух вариантов
         */
        maxEndingHere = maxOf(nums[i], maxEndingHere + nums[i])
        maxSoFar = maxOf(maxSoFar, maxEndingHere)
    }

    return maxSoFar
}

// ═══════════════════════════════════════════════════════════════════════════
// PALINDROME DP: LONGEST PALINDROMIC SUBSTRING
// ═══════════════════════════════════════════════════════════════════════════

fun longestPalindrome(s: String): String {
    val n = s.length
    if (n < 2) return s

    /**
     * dp[i][j] = true, если подстрока s[i..j] является палиндромом
     *
     * Рекуррентное соотношение:
     * dp[i][j] = (s[i] == s[j]) && dp[i+1][j-1]
     *
     * То есть: крайние символы равны И внутренняя часть — палиндром
     *
     * ПОШАГОВЫЙ ПРИМЕР: s = "babad"
     *
     * Длина 1: все true (a, b, a, b, a, d — все палиндромы)
     * Длина 2: "ba"=false, "ab"=false, "ba"=false, "ad"=false
     * Длина 3: "bab"=true (b==b, "a"=true), "aba"=true
     * Длина 4: "baba"=false (b==a? нет)
     * Длина 5: "babad"=false
     *
     * Ответ: "bab" или "aba" (длина 3)
     */
    val dp = Array(n) { BooleanArray(n) }
    var start = 0
    var maxLen = 1

    // Базовый случай: все подстроки длины 1 — палиндромы
    for (i in 0 until n) dp[i][i] = true

    // Подстроки длины 2: палиндром только если оба символа равны
    for (i in 0 until n - 1) {
        if (s[i] == s[i + 1]) {
            dp[i][i + 1] = true
            start = i
            maxLen = 2
        }
    }

    // Подстроки длины 3+: используем рекуррентное соотношение
    for (len in 3..n) {
        for (i in 0..n - len) {
            val j = i + len - 1
            // Крайние равны И внутренняя часть — палиндром
            if (s[i] == s[j] && dp[i + 1][j - 1]) {
                dp[i][j] = true
                start = i
                maxLen = len
            }
        }
    }

    return s.substring(start, start + maxLen)
}

// ═══════════════════════════════════════════════════════════════════════════
// WORD BREAK
// ═══════════════════════════════════════════════════════════════════════════

fun wordBreak(s: String, wordDict: List<String>): Boolean {
    val wordSet = wordDict.toSet()
    val n = s.length

    /**
     * dp[i] = true, если строку s[0..i-1] можно разбить на слова из словаря
     *
     * Рекуррентное соотношение:
     * dp[i] = true, если существует j < i такой, что:
     *   1. dp[j] = true (s[0..j-1] можно разбить)
     *   2. s[j..i-1] есть в словаре
     *
     * ПОШАГОВЫЙ ПРИМЕР: s = "leetcode", dict = ["leet", "code"]
     *
     * dp[0] = true (пустая строка)
     * dp[4] = dp[0] && "leet" in dict = true ✓
     * dp[8] = dp[4] && "code" in dict = true ✓
     *
     * Ответ: true
     */
    val dp = BooleanArray(n + 1)
    // Базовый случай: пустую строку всегда можно "разбить"
    dp[0] = true

    for (i in 1..n) {
        for (j in 0 until i) {
            // Если s[0..j-1] разбивается И s[j..i-1] есть в словаре
            if (dp[j] && s.substring(j, i) in wordSet) {
                dp[i] = true
                break  // Нашли способ — дальше искать не нужно
            }
        }
    }

    return dp[n]
}
```

### Python

```python
from typing import List
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════════════════
# FIBONACCI PATTERN: CLIMBING STAIRS
# ═══════════════════════════════════════════════════════════════════════════

def climb_stairs_memo(n: int) -> int:
    @lru_cache(maxsize=None)  # WHY: автоматическая мемоизация
    def dp(i: int) -> int:
        if i <= 2:
            return i
        return dp(i - 1) + dp(i - 2)

    return dp(n)

def climb_stairs(n: int) -> int:
    if n <= 2:
        return n

    prev1, prev2 = 1, 2

    for _ in range(3, n + 1):
        prev1, prev2 = prev2, prev1 + prev2

    return prev2

# ═══════════════════════════════════════════════════════════════════════════
# COIN CHANGE
# ═══════════════════════════════════════════════════════════════════════════

def coin_change(coins: List[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1

# ═══════════════════════════════════════════════════════════════════════════
# LCS
# ═══════════════════════════════════════════════════════════════════════════

def longest_common_subsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]

# ═══════════════════════════════════════════════════════════════════════════
# LIS (O(n log n))
# ═══════════════════════════════════════════════════════════════════════════

import bisect

def length_of_lis(nums: List[int]) -> int:
    tails = []

    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num

    return len(tails)
```

---

## Распространённые ошибки

### 1. Неправильный порядок циклов в 0/1 Knapsack

```kotlin
// ❌ НЕПРАВИЛЬНО: идём слева направо — используем элемент дважды!
for (num in nums) {
    for (j in num..target) {  // WRONG!
        dp[j] = dp[j] || dp[j - num]
    }
}

// ✅ ПРАВИЛЬНО: справа налево для 0/1 Knapsack
for (num in nums) {
    // Идём справа налево, чтобы dp[j-num] было "старым" значением
    // Если идти слева направо, dp[j-num] уже обновлён → используем num дважды!
    for (j in target downTo num) {
        dp[j] = dp[j] || dp[j - num]
    }
}
```

### 2. Забыли base cases

```kotlin
// ❌ НЕПРАВИЛЬНО: не инициализировали dp[0]
val dp = IntArray(n + 1)
for (i in 1..n) {
    dp[i] = dp[i - 1] + dp[i - 2]  // dp[0] = 0 по умолчанию — НЕПРАВИЛЬНО!
}

// ✅ ПРАВИЛЬНО: явные base cases
dp[0] = 1  // или 0, зависит от задачи
dp[1] = 1
```

### 3. Off-by-one в индексах LCS

```kotlin
// ❌ НЕПРАВИЛЬНО: сравниваем text1[i] с text2[j]
if (text1[i] == text2[j]) {  // IndexOutOfBounds при i=m или j=n!
    dp[i][j] = dp[i-1][j-1] + 1
}

// ✅ ПРАВИЛЬНО: индексы смещены на 1
// dp[i][j] соответствует text1[0..i-1] и text2[0..j-1]
// Поэтому сравниваем text1[i-1] и text2[j-1]
if (text1[i - 1] == text2[j - 1]) {
    dp[i][j] = dp[i - 1][j - 1] + 1
}
```

### 4. Integer overflow в больших DP

```kotlin
// ❌ НЕПРАВИЛЬНО: dp может overflow
val dp = IntArray(n + 1)
dp[i] = dp[i - 1] + dp[i - 2]  // Может быть > Int.MAX_VALUE!

// ✅ ПРАВИЛЬНО: используем Long или модуль
val dp = LongArray(n + 1)
// или
dp[i] = (dp[i - 1] + dp[i - 2]) % MOD
```

### 5. Неправильный transition в Edit Distance

```kotlin
// ❌ НЕПРАВИЛЬНО: забыли +1 для replace
dp[i][j] = minOf(
    dp[i - 1][j],     // delete
    dp[i][j - 1],     // insert
    dp[i - 1][j - 1]  // replace БЕЗ +1!
)

// ✅ ПРАВИЛЬНО: +1 для каждой операции
dp[i][j] = 1 + minOf(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
```

---

## Когда использовать?

### Decision Tree

```
Задача имеет optimal substructure + overlapping subproblems?
│
├─ Нет → Не DP (возможно Greedy или другой подход)
│
└─ Да → Определи тип:
        │
        ├─ Один параметр, зависимость от предыдущих?
        │   └─ FIBONACCI PATTERN
        │
        ├─ Набор элементов, взять/не взять, ограничение?
        │   ├─ Каждый элемент 1 раз? → 0/1 KNAPSACK
        │   └─ Неограниченно? → UNBOUNDED KNAPSACK
        │
        ├─ Две последовательности, общие элементы?
        │   └─ LCS PATTERN
        │
        ├─ Одна последовательность, подпоследовательность с условием?
        │   └─ LIS PATTERN
        │
        └─ Матрица/сетка, пути?
            └─ GRID DP
```

### Признаки DP задачи

1. **"Maximum/Minimum"** — оптимизация
2. **"Count ways"** — подсчёт вариантов
3. **"Is it possible"** — существование решения
4. **"Longest/Shortest"** — экстремальная подструктура
5. **Ограничения**: n ≤ 1000 (O(n²)), n ≤ 10000 (O(n log n))

---

## Практика

### Концептуальные вопросы

1. **Когда использовать Top-Down vs Bottom-Up?**

   *Ответ:* Top-Down проще для реализации (просто добавить мемоизацию к рекурсии). Bottom-Up быстрее (нет overhead рекурсии) и позволяет легче оптимизировать память.

2. **Как оптимизировать память в 2D DP?**

   *Ответ:* Если dp[i] зависит только от dp[i-1], достаточно хранить две строки. Если только от предыдущих элементов той же строки — достаточно одной.

3. **Почему порядок циклов важен в Knapsack?**

   *Ответ:* В 0/1 Knapsack идём справа налево чтобы не использовать обновлённые значения (элемент берётся 1 раз). В Unbounded — слева направо (можно брать многократно).

### LeetCode задачи

#### Fibonacci Pattern

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 70 | Climbing Stairs | Easy | Базовый Fibonacci |
| 198 | House Robber | Medium | Max(skip, take) |
| 213 | House Robber II | Medium | Circular array |
| 509 | Fibonacci Number | Easy | Classic |

#### 0/1 Knapsack

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 416 | Partition Equal Subset Sum | Medium | Target = sum/2 |
| 494 | Target Sum | Medium | Transform to subset sum |
| 1049 | Last Stone Weight II | Medium | Min difference |

#### Unbounded Knapsack

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 322 | Coin Change | Medium | Minimum coins |
| 518 | Coin Change II | Medium | Count ways |
| 279 | Perfect Squares | Medium | Min squares |

#### LCS Pattern

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 1143 | Longest Common Subsequence | Medium | Classic LCS |
| 72 | Edit Distance | Medium | Insert/Delete/Replace |
| 583 | Delete Operation for Two Strings | Medium | LCS based |

#### LIS Pattern

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 300 | Longest Increasing Subsequence | Medium | O(n²) or O(n log n) |
| 354 | Russian Doll Envelopes | Hard | 2D LIS |
| 673 | Number of LIS | Medium | Count LIS |

#### Grid DP

| # | Название | Сложность | Ключевой момент |
|---|----------|-----------|-----------------|
| 62 | Unique Paths | Medium | Classic grid |
| 64 | Minimum Path Sum | Medium | Min path |
| 221 | Maximal Square | Medium | Min of 3 neighbors |

---

## Связанные темы

### Prerequisites
- [Recursion & Backtracking](./backtracking.md) — основа для Top-Down
- [Arrays](../data-structures/arrays-strings.md) — работа с индексами

### Unlocks
- [Graph Algorithms](../algorithms/shortest-paths.md) — DP в графах
- [String Algorithms](../algorithms/string-algorithms.md) — KMP, Z-function

### Часто комбинируется с
- **Binary Search** — LIS за O(n log n)
- **Greedy** — когда optimal substructure + greedy choice
- **BFS/DFS** — memoization в графах

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "DP = сложно и требует гениальности" | **Нет!** DP — это рекурсия + memoization. Начни с brute force рекурсии, добавь кэш. Систематический подход, не магия |
| "Нужно сразу думать о таблице" | **Top-down проще!** Начинай с рекурсии + memo, это естественнее. Bottom-up (табуляция) — оптимизация для production |
| "Каждая DP задача уникальна" | **80% задач = комбинация 5 паттернов:** Fibonacci, Knapsack, LCS, LIS, Grid. Узнай паттерн — решишь задачу |
| "Space optimization не важна" | **Критично!** O(n²) память может вызвать MLE. Rolling array снижает до O(n), иногда до O(1). На интервью спросят |
| "DP всегда оптимальнее brute force" | **Только при overlapping subproblems!** Если подзадачи не пересекаются, brute force = DP по сложности |
| "Top-down всегда медленнее bottom-up" | **Не всегда!** Top-down вычисляет только нужные состояния (lazy). Bottom-up может вычислять лишнее. Зависит от задачи |
| "Bitmask DP слишком сложный" | **Шаблон простой!** Состояние = integer как bitmask. Переход: проверка/установка битов. 2^n состояний для n элементов |
| "Нужно запоминать все DP таблицы" | **Нет!** Запомни 5 паттернов и общий подход: 1) Define state 2) Find recurrence 3) Base cases 4) Order of computation |

---

## CS-фундамент

| CS-концепция | Применение в Dynamic Programming |
|--------------|----------------------------------|
| **Optimal Substructure** | Оптимальное решение содержит оптимальные решения подзадач. Пример: кратчайший путь A→C через B = кратчайший A→B + кратчайший B→C |
| **Overlapping Subproblems** | Одни подзадачи вычисляются многократно. fib(5) = fib(4) + fib(3), fib(4) = fib(3) + fib(2) — fib(3) дважды! Кэшируем |
| **Memoization (Top-Down)** | Рекурсия + HashMap/Array. Вычисляем "сверху вниз", кэшируя результаты. Естественный способ думать о задаче |
| **Tabulation (Bottom-Up)** | Итеративно заполняем таблицу от базовых случаев к ответу. Нет накладных расходов рекурсии, легче оптимизировать память |
| **State Space Design** | Определение состояния — главное в DP. dp[i][j] = что означает? От выбора состояния зависит сложность и корректность |
| **Recurrence Relation** | dp[i] = f(dp[i-1], dp[i-2], ...). Математическое выражение связи состояний. Основа для доказательства корректности |
| **Space Optimization / Rolling Array** | Если dp[i] зависит только от dp[i-1], храним только 2 значения вместо n. O(n) → O(1) память |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [AlgoMaster DP Patterns](https://blog.algomaster.io/p/20-patterns-to-master-dynamic-programming) | Туториал | 20 patterns |
| 2 | [GeeksforGeeks](https://www.geeksforgeeks.org/tabulation-vs-memoization/) | Туториал | Top-down vs Bottom-up |
| 3 | [AlgoMap](https://algomap.io/lessons/dynamic-programming) | Туториал | Templates |
| 4 | [LeetCode DP Tag](https://leetcode.com/tag/dynamic-programming/) | Практика | Problems |
| 5 | [Design Gurus](https://www.designgurus.io/answers/detail/what-are-common-dynamic-programming-questions-in-tech-interviews) | Гайд | Interview tips |

---

## Куда дальше

→ **Базовый алгоритм:** [[dynamic-programming]] — теория DP подробно
→ **Связанный паттерн:** [[backtracking]] — когда DP не работает
→ **Комбинируется с:** [[binary-search-pattern]] — Binary Search on Answer + DP
→ **Вернуться к:** [[patterns-overview|Обзор паттернов]]

---

*Обновлено: 2026-01-07 — добавлены педагогические секции (интуиция DP, типичные ошибки, 5 ментальных моделей)*
