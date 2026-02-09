# Research Report: Dynamic Programming — Teaching Approach

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep (педагогический фокус)

## Executive Summary

Dynamic Programming — техника оптимизации через сохранение результатов подзадач. Лучшие аналогии: пазл (решённые части не переделываем), лестница (поднимаемся по ступенькам), рецепт (ингредиенты готовим один раз). Ключевые концепции: overlapping subproblems (одинаковые подзадачи решаются многократно) и optimal substructure (оптимальное решение состоит из оптимальных подрешений). Memoization = top-down (рекурсия + кэш), Tabulation = bottom-up (итеративно заполняем таблицу).

---

## Key Findings for Teaching

### 1. Best Analogies for Beginners

| Concept | Analogy | Why It Works |
|---------|---------|--------------|
| **DP itself** | Пазл: решённые части не переделываем | Визуально понятно, что храним результат |
| **Memoization** | Записная книжка: записал — не забудешь | Кэширование интуитивно понятно |
| **Overlapping Subproblems** | Fibonacci: F(3) нужен и для F(4), и для F(5) | Классический пример повторения |
| **Optimal Substructure** | Кратчайший путь: Seattle→LA через Portland, значит Portland→LA тоже кратчайший | Реальный жизненный пример |
| **Tabulation** | Строить дом с фундамента, а не с крыши | Снизу-вверх понятно |
| **State** | GPS-координаты: где мы сейчас находимся | Состояние = позиция в задаче |

### 2. Why DP Is Hard for Beginners

**Главные проблемы (из исследований):**

1. **"DP — это алгоритм"** — нет, это способ мышления
2. **"Все DP-задачи похожи"** — нет, они выглядят совершенно по-разному
3. **"Нужно сразу писать оптимальное решение"** — нет, сначала brute force
4. **"Если рекурсия, значит DP"** — нет, нужны overlapping subproblems

**Цитата из ACM исследования:**
> "Students struggle defining the notion of a subproblem and identifying particular subproblems."

### 3. Step-by-Step Framework for Beginners

**FAST Method (Simple Programmer):**

```
F — Find first solution (brute force recursive)
A — Analyze solution (identify repeated work)
S — Subproblems (cache them — memoization)
T — Turn around (convert to bottom-up if needed)
```

**Детальный алгоритм:**

1. **Можно ли разбить на подзадачи?**
   - Если да → кандидат для DP
   - Если нет → другой подход

2. **Есть ли повторяющиеся подзадачи?**
   - Нарисуй дерево рекурсии
   - Видишь одинаковые узлы? → DP поможет

3. **Определи состояние**
   - Какие параметры меняются?
   - dp[i] или dp[i][j] — что хранится?

4. **Найди переход (transition)**
   - Как связаны состояния?
   - dp[i] = f(dp[i-1], dp[i-2], ...)

5. **База (base case)**
   - Когда i=0 или i=1 — что известно?

6. **Реализуй**
   - Сначала memoization (проще думать)
   - Потом tabulation (если нужна оптимизация)

### 4. Memoization vs Tabulation — When to Use

| Критерий | Memoization | Tabulation |
|----------|-------------|------------|
| **Направление** | Сверху-вниз (от большого к малому) | Снизу-вверх (от малого к большому) |
| **Реализация** | Рекурсия + HashMap/Array | Цикл for + массив |
| **Когда нужны не все подзадачи** | Лучше (ленивые вычисления) | Хуже (вычисляет всё) |
| **Когда нужны все подзадачи** | Хуже (overhead рекурсии) | Лучше (быстрее) |
| **Stack Overflow риск** | Да (глубокая рекурсия) | Нет |
| **Space optimization** | Сложно | Легко (rolling array) |
| **Для новичков** | Легче понять (думай рекурсивно) | Сложнее (нужен порядок заполнения) |

### 5. Common Mistakes to Teach Against

| Ошибка | Почему происходит | Как избежать |
|--------|-------------------|--------------|
| **Неправильное состояние** | Не все параметры учтены | Спроси: "Что однозначно определяет подзадачу?" |
| **Неправильный переход** | Логическая ошибка | Проверь на маленьких примерах вручную |
| **Забыл base case** | Сразу думает о transition | Всегда начинай с "Что известно при i=0?" |
| **Off-by-one** | Путаница 0-based/1-based | Нарисуй таблицу, проверь индексы |
| **Сразу оптимизирует** | Хочет rolling array сразу | Сначала полная таблица, потом оптимизируй |
| **Не видит DP** | Не распознаёт паттерн | Практика: 50+ задач по категориям |

### 6. Two Key Properties Explained Simply

**Optimal Substructure:**
```
Кратчайший путь Seattle → Los Angeles проходит через Portland.

Вопрос: Какой кратчайший путь Portland → Los Angeles?

Ответ: ТОТ ЖЕ, что был частью Seattle → LA!

Если бы был короче — мы бы использовали его для Seattle→LA,
и Seattle→LA стал бы ещё короче. Противоречие!

Значит: оптимальное решение состоит из оптимальных подрешений.
```

**Overlapping Subproblems:**
```
Fibonacci: F(5) = F(4) + F(3)
                   ↓       ↓
           F(4) = F(3) + F(2)
                   ↑
           F(3) вычисляется ДВА раза!

Дерево вызовов:
           F(5)
          /    \
       F(4)    F(3)    ← F(3) уже здесь
       /  \
    F(3)  F(2)         ← и ещё раз здесь!

Без кэша: O(2^n) вызовов
С кэшем: O(n) вызовов

В МИЛЛИОН раз быстрее для n=30!
```

### 7. Visual Learning Resources

**Interactive:**
- [VisuAlgo DP](https://visualgo.net/en/recursion) — визуализация рекурсии и мемоизации
- [CS Academy DP](https://csacademy.com/lesson/introduction_to_dynamic_programming/) — интерактивные примеры

**Diagrams to Draw:**
1. **Recursion Tree** — показывает overlapping subproblems
2. **DP Table** — показывает заполнение снизу-вверх
3. **DAG (Directed Acyclic Graph)** — показывает зависимости

### 8. Teaching Progression

**Порядок изучения задач:**

```
УРОВЕНЬ 1: Понять идею (1D DP)
├── Fibonacci (классика)
├── Climbing Stairs (вариация Fibonacci)
└── House Robber (первый "настоящий" DP)

УРОВЕНЬ 2: 1D DP задачи
├── Maximum Subarray (Kadane)
├── Coin Change (unbounded knapsack)
└── Longest Increasing Subsequence

УРОВЕНЬ 3: 2D DP задачи
├── Unique Paths (grid DP)
├── 0/1 Knapsack
└── Longest Common Subsequence

УРОВЕНЬ 4: Комплексные паттерны
├── Edit Distance
├── Burst Balloons (interval DP)
└── Word Break (string partition)
```

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Stack Overflow - Complete Beginners Guide](https://stackoverflow.blog/2022/01/31/the-complete-beginners-guide-to-dynamic-programming/) | Tutorial | 0.90 | Analogies, step-by-step |
| 2 | [GeeksforGeeks - Steps to Solve DP](https://www.geeksforgeeks.org/dsa/solve-dynamic-programming-problem/) | Guide | 0.90 | Framework |
| 3 | [freeCodeCamp - Follow These Steps](https://www.freecodecamp.org/news/follow-these-steps-to-solve-any-dynamic-programming-interview-problem-cc98e508cd0e/) | Tutorial | 0.90 | FAST method |
| 4 | [Medium - DP 101 Intuition](https://zephiroth.medium.com/dynamic-programming-101-intuition-and-how-to-solving-problems-b97b90fc9b96) | Tutorial | 0.85 | Intuition building |
| 5 | [Baeldung - Tabulation vs Memoization](https://www.baeldung.com/cs/tabulation-vs-memoization) | Comparison | 0.90 | Visual differences |
| 6 | [ACM - Student Misconceptions](https://dl.acm.org/doi/abs/10.1145/3159450.3159528) | Academic | 0.95 | Why students struggle |
| 7 | [interviewing.io - DP Interview Questions](https://interviewing.io/dynamic-programming-interview-questions) | Guide | 0.90 | Common mistakes |
| 8 | [Wikipedia - Optimal Substructure](https://en.wikipedia.org/wiki/Optimal_substructure) | Reference | 0.95 | Formal definitions |
| 9 | [AfterAcademy - Optimal Substructure](https://afteracademy.com/blog/optimal-substructure-and-overlapping-subproblems/) | Tutorial | 0.85 | Simple explanations |

---

*Generated: 2025-12-29*
*Purpose: Teaching-focused research for dynamic-programming.md rewrite*
