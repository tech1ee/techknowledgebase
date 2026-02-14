---
title: "Фреймворк решения задач: UMPIRE и метод Полья"
created: 2025-12-29
modified: 2026-02-13
type: guide
status: published
confidence: high
tags:
  - topic/cs-fundamentals
  - type/guide
  - level/beginner
  - interview
related:
  - "[[big-o-complexity]]"
  - "[[coding-challenges]]"
  - "[[technical-interview]]"
reading_time: 32
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Problem-Solving Framework: как решать алгоритмические задачи

80% кандидатов проваливают coding интервью не из-за недостатка знаний, а из-за отсутствия структурированного подхода. Самая частая ошибка — начать писать код сразу после прочтения условия. UMPIRE framework решает эту проблему.

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **UMPIRE** | Understand-Match-Plan-Implement-Review-Evaluate — 6-шаговый фреймворк CodePath |
| **Polya's Method** | Классический 4-шаговый метод решения задач (1945) |
| **Pattern Matching** | Сопоставление задачи с известными паттернами решения |
| **Edge Case** | Граничные условия: пустой ввод, null, один элемент |
| **Brute Force** | Простейшее решение "в лоб", часто неоптимальное |
| **Pseudocode** | Псевдокод — описание алгоритма на естественном языке |
| **BTTC** | Best Theoretical Time Complexity — лучшая теоретическая сложность |
| **Upsolving** | Решение задач, которые не удалось решить на контесте |

---

## Зачем нужен фреймворк?

### Проблема без структуры

```
БЕЗ ФРЕЙМВОРКА:
┌─────────────────────────────────────────────────────┐
│ Прочитал задачу → Сразу код → Ошибки → Паника →    │
│ → Переписывание → Время вышло → FAIL               │
└─────────────────────────────────────────────────────┘

Типичный результат:
- Код не работает для edge cases
- Нет времени на оптимизацию
- Интервьюер не понял логику
- 45 минут потрачены впустую
```

### Решение с фреймворком

```
С UMPIRE:
┌─────────────────────────────────────────────────────┐
│ Understand → Match → Plan → Implement → Review →   │
│ → Evaluate → PASS                                   │
└─────────────────────────────────────────────────────┘

Результат:
- Правильное понимание задачи
- Оптимальный паттерн выбран
- Код работает с первого раза
- Complexity обсуждена
```

---

## UMPIRE Framework: 6 шагов к решению

### Визуальная схема

```
┌────────────────────────────────────────────────────────────────┐
│                        UMPIRE                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│   │    U     │───▶│    M     │───▶│    P     │                │
│   │Understand│    │  Match   │    │   Plan   │                │
│   │  5 min   │    │  3 min   │    │  5 min   │                │
│   └──────────┘    └──────────┘    └──────────┘                │
│        │                              │                        │
│        ▼                              ▼                        │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│   │    E     │◀───│    R     │◀───│    I     │                │
│   │ Evaluate │    │  Review  │    │Implement │                │
│   │  3 min   │    │  5 min   │    │ 20 min   │                │
│   └──────────┘    └──────────┘    └──────────┘                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### U — Understand (Понять задачу)

**Цель:** Полностью понять, что требуется решить.

**Действия:**
1. Прочитать условие **дважды**
2. Перефразировать задачу своими словами
3. Задать уточняющие вопросы
4. Написать 3-5 тест-кейсов

**Вопросы интервьюеру:**
- "Что вернуть, если массив пустой?"
- "Могут ли быть отрицательные числа?"
- "Нужно ли модифицировать input in-place?"
- "Какой диапазон значений?"
- "Строка только ASCII или Unicode?"

**Тест-кейсы:**

```
ПРИМЕР: Two Sum

Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]

Мои тест-кейсы:
1. [2, 7, 11, 15], target=9 → [0, 1]  // базовый
2. [3, 3], target=6 → [0, 1]          // дубликаты
3. [1], target=1 → []?                // один элемент
4. [], target=5 → []                  // пустой массив
5. [-1, -2, -3], target=-4 → [1, 2]   // отрицательные
```

**Красные флаги:**
- Начал кодить сразу после прочтения
- Не спросил ни одного вопроса
- Не придумал тест-кейсы

---

### M — Match (Сопоставить с паттерном)

**Цель:** Определить категорию задачи и применимые паттерны.

**Матрица паттернов:**

| Признак задачи | Вероятный паттерн | Пример |
|----------------|-------------------|--------|
| Sorted array, pairs | Two Pointers | Two Sum II |
| Subarray/substring с условием | Sliding Window | Max consecutive ones |
| Linked list, cycle | Fast & Slow Pointers | Linked List Cycle |
| Sorted + search | Binary Search | Search in Rotated Array |
| Tree traversal | DFS/BFS | Max Depth of Binary Tree |
| Counting ways, optimization | Dynamic Programming | Climbing Stairs |
| All combinations | Backtracking | Subsets, Permutations |
| Interval problems | Sort + Greedy | Merge Intervals |
| Graph connectivity | Union-Find | Number of Islands |
| Next greater element | Monotonic Stack | Daily Temperatures |

**Оценка применимости:**

```
ЗАДАЧА: Find the longest substring without repeating characters

ОЦЕНКА ПАТТЕРНОВ:
[✓] Sliding Window    — LIKELY (substring + условие)
[?] Two Pointers      — NEUTRAL (может помочь)
[✗] Binary Search     — UNLIKELY (нет sorted data)
[✗] DP                — UNLIKELY (не optimization)

ВЫВОД: Sliding Window с HashSet для tracking
```

**Время:** Не более 3-5 минут

---

### P — Plan (Спланировать решение)

**Цель:** Описать алгоритм до написания кода.

**Формат плана:**

```
ЗАДАЧА: Longest Substring Without Repeating Characters

ПЛАН:
1. Создать HashSet для tracking символов
2. Два указателя: left, right (sliding window)
3. Двигать right, добавляя в set
4. Если символ уже есть — двигать left, удаляя из set
5. Отслеживать max length = right - left + 1
6. Вернуть max length

EDGE CASES:
- Пустая строка → 0
- Все одинаковые "aaaa" → 1
- Все разные "abcd" → 4

COMPLEXITY (предварительно):
- Time: O(n) — каждый символ добавляем/удаляем max 1 раз
- Space: O(min(n, charset)) — HashSet
```

**Визуализация:**

```
"abcabcbb"

Шаг 1: [a]bcabcbb     set={a}     max=1
Шаг 2: [ab]cabcbb     set={a,b}   max=2
Шаг 3: [abc]abcbb     set={a,b,c} max=3
Шаг 4: a[bca]bcbb     set={b,c,a} max=3  (удалили первый 'a')
Шаг 5: ab[cab]cbb     set={c,a,b} max=3  (удалили первый 'b')
...
```

**Получить green light:**
> "Я планирую использовать sliding window с двумя указателями и HashSet. Можно начинать кодить?"

---

### I — Implement (Реализовать код)

**Цель:** Написать чистый, работающий код.

**Kotlin:**

```kotlin
fun lengthOfLongestSubstring(s: String): Int {
    val seen = mutableSetOf<Char>()
    var left = 0
    var maxLength = 0

    for (right in s.indices) {
        // Shrink window until no duplicates
        while (s[right] in seen) {
            seen.remove(s[left])
            left++
        }

        // Add current character
        seen.add(s[right])

        // Update max length
        maxLength = maxOf(maxLength, right - left + 1)
    }

    return maxLength
}
```

**Java:**

```java
public int lengthOfLongestSubstring(String s) {
    Set<Character> seen = new HashSet<>();
    int left = 0;
    int maxLength = 0;

    for (int right = 0; right < s.length(); right++) {
        // Shrink window until no duplicates
        while (seen.contains(s.charAt(right))) {
            seen.remove(s.charAt(left));
            left++;
        }

        // Add current character
        seen.add(s.charAt(right));

        // Update max length
        maxLength = Math.max(maxLength, right - left + 1);
    }

    return maxLength;
}
```

**Python:**

```python
def lengthOfLongestSubstring(s: str) -> int:
    seen = set()
    left = 0
    max_length = 0

    for right in range(len(s)):
        # Shrink window until no duplicates
        while s[right] in seen:
            seen.remove(s[left])
            left += 1

        # Add current character
        seen.add(s[right])

        # Update max length
        max_length = max(max_length, right - left + 1)

    return max_length
```

**Правила реализации:**
1. Называть переменные понятно (`left`, `right`, NOT `i`, `j`)
2. Комментировать логические блоки
3. Говорить вслух, что пишешь
4. Не оптимизировать преждевременно

---

### R — Review (Проверить код)

**Цель:** Найти баги ДО того, как их найдёт интервьюер.

**НИКОГДА не пропускай этот шаг!**

**Метод проверки:**

```
WATCHLIST:
- left = ?
- right = ?
- seen = ?
- maxLength = ?

TRACE через "abcab":

right=0: s[0]='a'
  while 'a' in {} → false
  seen = {a}
  maxLength = max(0, 0-0+1) = 1

right=1: s[1]='b'
  while 'b' in {a} → false
  seen = {a, b}
  maxLength = max(1, 1-0+1) = 2

right=2: s[2]='c'
  while 'c' in {a,b} → false
  seen = {a, b, c}
  maxLength = max(2, 2-0+1) = 3

right=3: s[3]='a'
  while 'a' in {a,b,c} → TRUE!
    seen.remove(s[0]='a') → {b, c}
    left = 1
  while 'a' in {b,c} → false
  seen = {b, c, a}
  maxLength = max(3, 3-1+1) = 3

right=4: s[4]='b'
  while 'b' in {b,c,a} → TRUE!
    seen.remove(s[1]='b') → {c, a}
    left = 2
  while 'b' in {c,a} → false
  seen = {c, a, b}
  maxLength = max(3, 4-2+1) = 3

RESULT: 3 ✓
```

**Чеклист проверки:**
- [ ] Off-by-one ошибки (< vs <=)
- [ ] Пустой input
- [ ] Single element
- [ ] Null/None
- [ ] Negative numbers
- [ ] Integer overflow

---

### E — Evaluate (Оценить решение)

**Цель:** Обсудить сложность и улучшения.

**Шаблон ответа:**

```
TIME COMPLEXITY: O(n)
- Каждый символ добавляется в set max 1 раз
- Каждый символ удаляется из set max 1 раз
- Итого: 2n операций → O(n)

SPACE COMPLEXITY: O(min(n, m))
- n = длина строки
- m = размер алфавита (128 ASCII / 26 букв)
- HashSet хранит max m символов

TRADE-OFFS:
- Можно использовать HashMap<Char, Int> для index
- Позволит прыгать left сразу к нужной позиции
- Но код сложнее, а complexity та же

IMPROVEMENTS:
- Для фиксированного алфавита можно использовать array[128]
- Чуть быстрее на практике, но O(1) → O(1)
```

---

## Polya's Method: классика 1945 года

Джордж Полья — венгерский математик, написавший книгу "How to Solve It" в 1945. Его метод повлиял на UMPIRE и другие современные фреймворки.

```
POLYA'S 4 STEPS:
                        ┌─────────────────────┐
                        │   1. UNDERSTAND     │
                        │   What is unknown?  │
                        │   What is given?    │
                        │   What is the       │
                        │   condition?        │
                        └─────────┬───────────┘
                                  │
                        ┌─────────▼───────────┐
                        │   2. DEVISE A PLAN  │
                        │   Find connection   │
                        │   Similar problems? │
                        │   Auxiliary problem?│
                        └─────────┬───────────┘
                                  │
                        ┌─────────▼───────────┐
                        │  3. CARRY OUT PLAN  │
                        │   Check each step   │
                        │   Can you prove it? │
                        └─────────┬───────────┘
                                  │
                        ┌─────────▼───────────┐
                        │    4. LOOK BACK     │
                        │   Check result      │
                        │   Can you use it    │
                        │   for other probs?  │
                        └─────────────────────┘
```

**Ключевые вопросы Полья:**

| Шаг | Вопросы |
|-----|---------|
| Understand | Что неизвестно? Что дано? Каковы условия? |
| Plan | Есть ли похожая задача? Можно ли упростить? |
| Execute | Можешь ли доказать каждый шаг? |
| Look Back | Можно ли решить иначе? Применимо ли для других задач? |

---

## Time Management: 45 минут

```
РАСПРЕДЕЛЕНИЕ ВРЕМЕНИ:
┌────────────────────────────────────────────────────────┐
│ 0        5       10       20       35       45 min    │
│ │────────│────────│────────│────────│────────│        │
│ │  U+M   │   P    │      I        │   R+E   │        │
│ │Понять  │План    │  Реализация   │Проверка │        │
│ │5 min   │5 min   │   15-20 min   │10 min   │        │
└────────────────────────────────────────────────────────┘

CHECKPOINTS:
10 min → Должен понимать задачу и иметь план
20 min → Должен иметь working brute force
35 min → Должен иметь optimized solution
45 min → Должен объяснить complexity
```

**Если застрял:**

1. Попробуй brute force
2. Реши упрощённую версию
3. Рисуй примеры
4. Попроси hint (это нормально!)

---

## Pattern Recognition: как определить тип задачи

### Decision Tree

```
НАЧАЛО АНАЛИЗА:
           │
           ▼
    ┌──────────────┐
    │ Sorted data? │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
┌─────────┐   ┌─────────────┐
│ Binary  │   │ Subarray/   │
│ Search  │   │ Substring?  │
└─────────┘   └──────┬──────┘
                     │
              ┌──────┴──────┐
              │ YES         │ NO
              ▼             ▼
         ┌─────────┐   ┌─────────────┐
         │ Sliding │   │ Tree/Graph? │
         │ Window  │   └──────┬──────┘
         └─────────┘          │
                        ┌─────┴─────┐
                        │ YES       │ NO
                        ▼           ▼
                   ┌─────────┐   ┌───────────┐
                   │ DFS/BFS │   │ Counting/ │
                   └─────────┘   │Optimization│
                                 └─────┬─────┘
                                       │ YES
                                       ▼
                                  ┌─────────┐
                                  │   DP    │
                                  └─────────┘
```

### Сигнатуры паттернов

| Ключевые слова в условии | Паттерн |
|--------------------------|---------|
| "find pair", "sorted array" | Two Pointers |
| "longest/shortest substring", "consecutive" | Sliding Window |
| "detect cycle", "find middle" | Fast & Slow Pointers |
| "find target", "rotated sorted" | Binary Search |
| "all paths", "connected components" | DFS |
| "shortest path", "level order" | BFS |
| "overlapping intervals", "scheduling" | Intervals + Sort |
| "minimum/maximum", "count ways" | Dynamic Programming |
| "all combinations", "generate all" | Backtracking |
| "next greater", "histogram" | Monotonic Stack |

---

## Data Structure Selection

### Когда что использовать

```
┌─────────────────────────────────────────────────────────────┐
│              DATA STRUCTURE SELECTION GUIDE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Нужен быстрый доступ по индексу?                         │
│   └── YES → ARRAY                                          │
│                                                             │
│   Частые вставки/удаления в середине?                      │
│   └── YES → LINKED LIST                                    │
│                                                             │
│   Быстрый поиск по ключу?                                  │
│   └── YES → HASH MAP / HASH SET                            │
│                                                             │
│   Нужен порядок элементов?                                 │
│   └── YES → TREE MAP / TREE SET (BST)                      │
│                                                             │
│   Операции с приоритетом (min/max)?                        │
│   └── YES → HEAP / PRIORITY QUEUE                          │
│                                                             │
│   LIFO операции (последний вошёл — первый вышел)?          │
│   └── YES → STACK                                          │
│                                                             │
│   FIFO операции (первый вошёл — первый вышел)?             │
│   └── YES → QUEUE                                          │
│                                                             │
│   Prefix matching / autocomplete?                          │
│   └── YES → TRIE                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Communication: как говорить на интервью

### Что говорить на каждом этапе

**U — Understand:**
> "Дайте убедиться, что я правильно понял. Нам нужно найти... Входные данные — это... Вернуть нужно..."

**M — Match:**
> "Это похоже на задачу типа [pattern]. Я видел похожие задачи, где использовался [approach]."

**P — Plan:**
> "Мой план такой: сначала..., затем..., в конце... Сложность будет примерно O(n). Можно начинать кодить?"

**I — Implement:**
> "Здесь я создаю HashSet для отслеживания... Теперь итерируюсь по массиву..."

**R — Review:**
> "Давайте пройдём по примеру. При i=0 переменная x равна... На i=1..."

**E — Evaluate:**
> "Временная сложность O(n), потому что... Пространственная O(k), где k — это..."

### Когда застрял

> "Хм, я пока не вижу оптимального решения. Давайте начну с brute force подхода, а потом попробую оптимизировать."

> "Можете дать подсказку, в правильном ли направлении я думаю?"

---

## Common Mistakes: 10 ошибок, которые стоят оффера

### 1. Сразу кодить

```
WRONG:
"Two Sum? Легко!"
*начинает писать код*

RIGHT:
"Two Sum. Давайте уточню: массив может содержать
дубликаты? Отрицательные числа? Всегда есть решение?"
```

### 2. Молчать при кодировании

```
WRONG:
*30 минут тишины*
"Готово!"

RIGHT:
"Сейчас я создаю HashMap для хранения индексов...
Здесь проверяю, есть ли complement в map..."
```

### 3. Игнорировать edge cases

```
WRONG:
// Works for [2, 7, 11, 15]
// Fails for [], [1], null

RIGHT:
if (nums == null || nums.length < 2) {
    return new int[]{};
}
```

### 4. Не тестировать код

```
WRONG:
"Выглядит правильно, отправляю."

RIGHT:
"Давайте проверим на примере [2, 7, 11, 15], target=9.
При i=0, nums[0]=2, complement=7..."
```

### 5. Не обсуждать complexity

```
WRONG:
"Работает, всё."

RIGHT:
"Временная сложность O(n) — один проход по массиву.
Пространственная O(n) в worst case — HashMap."
```

---

## Debugging Strategies

### Rubber Duck Debugging

```
МЕТОД:
Объясняй код строка за строкой, как будто
объясняешь резиновой уточке.

ПОЧЕМУ РАБОТАЕТ:
Когда объясняешь — находишь логические ошибки,
которые не замечал при чтении.
```

### Divide and Conquer

```
МЕТОД:
1. Определи, работает ли первая половина кода
2. Определи, работает ли вторая половина
3. Сузь поиск бага

ПРИМЕР:
// До этой строки всё работает?
System.out.println("Checkpoint 1: " + variable);
```

### Типичные баги

| Баг | Как найти |
|-----|-----------|
| Off-by-one | Проверь `<` vs `<=`, границы массива |
| Null pointer | Добавь null checks в начало |
| Integer overflow | Проверь умножение больших чисел |
| Infinite loop | Проверь условие выхода и изменение переменных |
| Wrong return | Trace вручную, проверь return statements |

---

## Competitive Programming Strategy

### Effective Practice

```
ПРАВИЛО 30-40%:
Решай задачи, где можешь решить ~30-40% самостоятельно.
Это "зона роста" — не слишком легко, не слишком сложно.

UPSOLVING:
После контеста ОБЯЗАТЕЛЬНО разбери задачи,
которые не решил. Это главный источник роста.

ВРЕМЯ:
На 4 часа решения — 1 час изучения теории.
```

### Contest Strategy

```
ПРИОРИТЕТЫ:
1. Прочитай ВСЕ задачи (5 минут)
2. Начни с самой лёгкой
3. Не застревай — переходи к следующей
4. Возвращайся к сложным в конце

TIMING:
- Easy: 10-15 минут
- Medium: 20-30 минут
- Hard: 40-60 минут
```

---

## Практика

### Задачи для тренировки UMPIRE

| # | Задача | Паттерн | Сложность |
|---|--------|---------|-----------|
| 1 | Two Sum | Hash Map | Easy |
| 2 | Valid Palindrome | Two Pointers | Easy |
| 3 | Longest Substring Without Repeating | Sliding Window | Medium |
| 4 | Binary Search | Binary Search | Easy |
| 5 | Maximum Subarray | DP (Kadane) | Medium |
| 6 | Merge Intervals | Intervals | Medium |
| 7 | Number of Islands | DFS/BFS | Medium |
| 8 | Coin Change | DP | Medium |
| 9 | Word Search | Backtracking | Medium |
| 10 | Daily Temperatures | Monotonic Stack | Medium |

### Чеклист для каждой задачи

```
□ Прочитал условие дважды
□ Задал 3+ уточняющих вопроса
□ Написал 3+ тест-кейса
□ Определил паттерн
□ Написал план/псевдокод
□ Получил green light
□ Написал код с комментариями
□ Прошёл код вручную с примером
□ Проверил edge cases
□ Обсудил time/space complexity
```

---

## Мифы и заблуждения

**Миф:** "Нужно решить 1000 задач на LeetCode"

**Реальность:** 150-200 задач с глубоким пониманием паттернов эффективнее 1000 задач без понимания.

---

**Миф:** "Интервьюеру нужен только правильный код"

**Реальность:** 4 критерия оценки: communication, problem solving, technical competency, testing. Код — только часть.

---

**Миф:** "Просить подсказку — плохо"

**Реальность:** Умение работать с подсказками и строить на них решение — положительный сигнал.

---

## Связи

- [[big-o-complexity]] — анализ сложности для шага Evaluate
- [[coding-challenges]] — паттерны для шага Match
- [[data-structures/arrays-strings]] — выбор структуры данных
- [[algorithms/recursion-fundamentals]] — для рекурсивных решений

---

## Источники

- [CodePath UMPIRE Guide](https://guides.codepath.com/compsci/UMPIRE-Interview-Strategy) — официальный источник UMPIRE
- [Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/) — техники решения
- [How to Solve It (Wikipedia)](https://en.wikipedia.org/wiki/How_to_Solve_It) — метод Полья
- [Polya's Problem Solving Techniques](https://sass.queensu.ca/sites/sasswww/files/uploaded_files/Resource%20PDFs/polya.pdf) — оригинальный PDF
- [Interview Cake Tips](https://www.interviewcake.com/coding-interview-tips) — практические советы
- [Codeforces Practice Guide](https://codeforces.com/blog/entry/116371) — стратегия для competitive
- [Research: Problem-Solving Framework](../docs/research/2025-12-29-problem-solving-framework.md) — полное исследование

---

---

## Проверь себя

> [!question]- Почему шаг Understand (U) считается самым важным в UMPIRE, хотя на него отводится всего 5 минут?
> Неправильное понимание задачи делает бесполезными все последующие шаги. 80% провалов связаны с тем, что кандидат решал не ту задачу. 5 минут на уточняющие вопросы и тест-кейсы предотвращают 45 минут потерянного времени.

> [!question]- Тебе дали задачу "найти самую длинную подстроку с не более чем k различными символами". Какой паттерн ты выберешь и почему?
> Sliding Window, потому что задача содержит ключевые сигнатуры: "подстрока" (непрерывный участок) + условие (не более k символов). Два указателя определяют границы окна, HashMap отслеживает количество символов.

> [!question]- В чём опасность пропуска шага Review (R) при решении задачи на интервью?
> Без ручной трассировки кода остаются незамеченными off-by-one ошибки, неправильная обработка edge cases и логические ошибки. Интервьюер оценивает не только код, но и способность находить баги самостоятельно.

> [!question]- Почему brute force решение не является плохим подходом?
> Brute force даёт гарантированно правильный ответ для проверки оптимизированного решения. На интервью лучше начать с рабочего O(n^2) и оптимизировать, чем застрять на поиске идеального решения и не написать ничего.

---

## Ключевые карточки

Что такое UMPIRE?
?
Understand-Match-Plan-Implement-Review-Evaluate — 6-шаговый фреймворк решения алгоритмических задач от CodePath. Даёт структуру вместо хаотичного подхода.

Как распределить 45 минут на интервью по UMPIRE?
?
U+M: 5 мин, P: 5 мин, I: 15-20 мин, R+E: 10 мин. К 10-й минуте должен быть план, к 20-й — brute force, к 35-й — оптимизированное решение.

Что такое BTTC?
?
Best Theoretical Time Complexity — лучшая теоретическая сложность задачи. Например, для поиска в неотсортированных данных BTTC = O(n), потому что нужно проверить каждый элемент.

Какие ключевые слова указывают на паттерн Sliding Window?
?
"longest/shortest substring", "consecutive", "subarray с условием". Если задача требует найти оптимальный непрерывный подмассив или подстроку — это Sliding Window.

Что говорить интервьюеру, если застрял?
?
"Давайте начну с brute force подхода, а потом оптимизирую" или "Можете дать подсказку, в правильном ли направлении я думаю?" Умение работать с подсказками — положительный сигнал.

Какие 4 критерия оценивают интервьюеры?
?
Communication (общение), problem solving (подход к решению), technical competency (технические навыки), testing (проверка решения). Код — только часть оценки.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[algorithms/recursion-fundamentals]] | Освоить рекурсию для решения задач |
| Углубиться | [[patterns/patterns-overview]] | Изучить все паттерны для шага Match |
| Смежная тема | [[interview-prep/mock-interview-guide]] | Практика UMPIRE на mock-интервью |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |

*Последнее обновление: 2026-02-13 — Проверено, соответствует педагогическому стандарту*

---

[[big-o-complexity|← Big O Complexity]] | [[algorithms/recursion-fundamentals|Recursion Fundamentals →]]
