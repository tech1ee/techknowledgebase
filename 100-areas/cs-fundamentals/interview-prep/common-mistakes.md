# Common Coding Interview Mistakes

## TL;DR

Топ-5 ошибок: 1) Прыгать в код без понимания задачи, 2) Игнорировать edge cases, 3) Не анализировать complexity, 4) Off-by-one errors, 5) Не тестировать решение. **25% отказов** из-за игнорирования сложности при рабочем коде. Используй UMPIRE и чеклисты.

---

## Интуиция

### Аналогия 1: Интервью как экзамен по вождению

```
ЭКЗАМЕН ПО ВОЖДЕНИЮ = CODING INTERVIEW:

"Я умею водить" ≠ "Я сдам экзамен"

Ошибки, которые заваливают:
• Не посмотрел в зеркало перед манёвром = не уточнил условия
• Пересёк сплошную = off-by-one error
• Не включил поворотник = не объяснил что делаешь
• Превысил скорость = O(n²) когда нужно O(n)

Экзаменатор оценивает ПРОЦЕСС, не только результат!
```

### Аналогия 2: Edge cases как краш-тесты

```
КРАШ-ТЕСТ АВТОМОБИЛЯ:

"Машина едет" — недостаточно.
Нужно проверить:
• Лобовое столкновение (пустой input)
• Боковой удар (один элемент)
• Переворот (отрицательные числа)
• Экстремальный холод (INT_MIN/MAX)

Автомобиль, не прошедший краш-тест = код без проверки edge cases.
```

---

## Частые ошибки

### Ошибка 1: Не уточнять constraints

**СИМПТОМ:** Написал O(n²), а нужно O(n)

```
ОБЯЗАТЕЛЬНО СПРОСИ:
• "Какой размер input?" (n ≤ 100 vs n ≤ 10^6)
• "Может ли быть пустой/null?"
• "Sorted или unsorted?"
• "Уникальные или дубликаты?"
• "Положительные или любые числа?"

n ≤ 100 → O(n²) = 10,000 операций (OK)
n ≤ 10^6 → O(n²) = 10^12 операций (TLE!)
```

### Ошибка 2: Off-by-one в циклах и индексах

**СИМПТОМ:** Wrong Answer на edge cases

```kotlin
// ТИПИЧНЫЕ OFF-BY-ONE:

// Длина vs последний индекс
for (i in 0..arr.size)      // НЕПРАВИЛЬНО: выход за границы
for (i in 0 until arr.size) // ПРАВИЛЬНО

// Включительные границы
arr.slice(0, mid)           // [0, mid) — mid не включён
arr.slice(0, mid + 1)       // [0, mid] — mid включён

// Binary search
while (left < right)        // Когда использовать?
while (left <= right)       // Зависит от того, что ищем!
```

### Ошибка 3: "Работает = готово" без complexity

**СИМПТОМ:** Код работает, но reject из-за TLE

```
INTERVIEWER: "What's the time complexity?"
CANDIDATE: "Uh... O(n)?"
INTERVIEWER: "Are you sure? There's a loop inside a loop."
CANDIDATE: "Oh... O(n²)?"
INTERVIEWER: "The input is 10^6. Will this work?"

ПРАВИЛО: ВСЕГДА анализируй сложность ПЕРЕД кодированием.
         Лучше 5 минут на анализ, чем 30 минут на неправильный код.
```

---

## Ментальные модели

### Модель 1: "Чеклист edge cases"

```
УНИВЕРСАЛЬНЫЙ ЧЕКЛИСТ:

□ Empty input: [], "", null
□ Single element: [1]
□ Two elements: [1, 2] (минимум для "пары")
□ Duplicates: [1, 1, 1]
□ Negative: [-5, -1, 0]
□ Boundaries: INT_MIN, INT_MAX, 0
□ Sorted/reverse sorted: [1,2,3], [3,2,1]
□ Already satisfied: answer = input

Проверяй ВСЛУХ перед написанием кода!
```

### Модель 2: "Сложность определяет подход"

```
CONSTRAINTS → АЛГОРИТМ:

n ≤ 10       → O(n!)      Brute force, backtracking
n ≤ 20       → O(2^n)     Bitmask DP
n ≤ 500      → O(n³)      Floyd-Warshall
n ≤ 5,000    → O(n²)      Simple DP, nested loops
n ≤ 10^6     → O(n log n) Sorting, binary search
n ≤ 10^8     → O(n)       Linear scan, two pointers
n > 10^8     → O(log n)   Binary search, math

Прочитай constraints ПЕРВЫМ делом!
```

---

## Зачем это нужно?

**Реальность:**

Большинство кандидатов проваливаются не из-за незнания алгоритмов, а из-за preventable mistakes. Изучение типичных ошибок экономит время и повышает pass rate.

**Статистика:**
- 25% rejection'ов при рабочем коде — из-за плохой complexity
- 40% кандидатов не проверяют edge cases
- 30% молчат во время решения

---

## Категория 1: Problem Understanding

### Ошибка: Прыгать сразу в код

```
❌ НЕПРАВИЛЬНО:
Interviewer: "Find two numbers that sum to target"
Candidate: *сразу пишет код*

✅ ПРАВИЛЬНО:
Candidate: "Let me clarify a few things:
- Is the array sorted?
- Can I use the same element twice?
- Are there duplicates?
- What if there's no solution?
- What's the expected output format?"
```

### Ошибка: Неправильно понять задачу

```
Пример: "Return the kth largest element"

❌ Неправильное понимание:
   k=1 → вернуть самый маленький

✅ Правильное:
   k=1 → вернуть самый БОЛЬШОЙ
   k=n → вернуть самый маленький

СОВЕТ: Проверь понимание на примере!
"So for [3,1,4,1,5] with k=2, the answer would be 4, correct?"
```

### Чеклист: Before Coding

```
□ Повторил задачу своими словами
□ Уточнил input constraints
□ Спросил про edge cases
□ Проверил понимание на примере
□ Знаю формат output
```

---

## Категория 2: Edge Cases

### Ошибка: Игнорировать границы

```kotlin
// ❌ НЕПРАВИЛЬНО: не проверяет пустой массив
fun findMax(nums: IntArray): Int {
    var max = nums[0]  // Crash если nums пустой!
    for (num in nums) {
        max = maxOf(max, num)
    }
    return max
}

// ✅ ПРАВИЛЬНО:
fun findMax(nums: IntArray): Int {
    if (nums.isEmpty()) {
        throw IllegalArgumentException("Array is empty")
        // или return Int.MIN_VALUE в зависимости от требований
    }
    var max = nums[0]
    for (num in nums) {
        max = maxOf(max, num)
    }
    return max
}
```

### Common Edge Cases Checklist

| Тип данных | Edge Cases |
|------------|------------|
| Array/List | Empty, single element, all same, sorted, reverse sorted |
| String | Empty, single char, all same char, palindrome |
| Number | 0, 1, -1, MAX_VALUE, MIN_VALUE, negative |
| Tree | Null, single node, skewed, complete |
| Graph | Disconnected, single node, cycle, no edges |
| Linked List | Null, single node, cycle, two nodes |

### Ошибка: Off-by-One Errors

```kotlin
// ❌ НЕПРАВИЛЬНО: пропускает последний элемент
for (i in 0 until nums.size - 1) {  // 0..n-2, пропустили n-1!
    process(nums[i])
}

// ✅ ПРАВИЛЬНО:
for (i in 0 until nums.size) {  // 0..n-1
    process(nums[i])
}

// ❌ НЕПРАВИЛЬНО: binary search границы
while (lo < hi) {
    val mid = lo + (hi - lo) / 2
    if (check(mid)) {
        lo = mid      // Infinite loop когда lo = mid!
    } else {
        hi = mid - 1
    }
}

// ✅ ПРАВИЛЬНО:
while (lo < hi) {
    val mid = lo + (hi - lo) / 2
    if (check(mid)) {
        lo = mid + 1  // Избегаем застревания
    } else {
        hi = mid
    }
}
```

### Boundary Testing Template

```
Для каждой задачи проверь:
□ n = 0 (пустой)
□ n = 1 (один элемент)
□ n = 2 (два элемента)
□ n = большое число (overflow?)
□ Negative values
□ Duplicates
□ Already sorted / reverse sorted
```

---

## Категория 3: Complexity Analysis

### Ошибка: Игнорировать Big-O

```kotlin
// ❌ НЕПРАВИЛЬНО: O(n²) когда можно O(n)
fun hasDuplicate(nums: IntArray): Boolean {
    for (i in nums.indices) {
        for (j in i + 1 until nums.size) {
            if (nums[i] == nums[j]) return true
        }
    }
    return false
}

// ✅ ПРАВИЛЬНО: O(n) с HashSet
fun hasDuplicate(nums: IntArray): Boolean {
    val seen = HashSet<Int>()
    for (num in nums) {
        if (!seen.add(num)) return true
    }
    return false
}
```

### Ошибка: Неправильный анализ

```
❌ НЕПРАВИЛЬНО:
"Тут один цикл, значит O(n)"
// Но внутри цикла есть list.contains() который O(n)!
// Итого: O(n²)

✅ ПРАВИЛЬНО:
"Цикл O(n), внутри HashSet.contains() O(1), итого O(n)"
```

### Quick Complexity Reference

| Операция | Time |
|----------|------|
| Array access | O(1) |
| HashMap get/put | O(1) average |
| TreeMap get/put | O(log n) |
| List.contains() | O(n) |
| List.add(0, x) | O(n) |
| Sorting | O(n log n) |
| BFS/DFS | O(V + E) |

### Trade-off Communication

```
ПРАВИЛЬНЫЙ формат:
"I can solve this in O(n²) time O(1) space using two loops.
But if we use a HashMap, we can improve to O(n) time O(n) space.
Given the constraints (n ≤ 10⁵), O(n²) might TLE,
so I recommend the HashMap approach.
Should I proceed with that?"
```

---

## Категория 4: Communication

### Ошибка: Молчаливое кодирование

```
❌ НЕПРАВИЛЬНО:
*5 минут молчания*
*пишет код*
*ещё 5 минут молчания*
"Done."

✅ ПРАВИЛЬНО:
"I'm going to iterate through the array...
Using a HashMap to store values we've seen...
For each element, I check if complement exists...
Let me write this out..."
```

### Ошибка: Оборонительная позиция

```
❌ НЕПРАВИЛЬНО:
Interviewer: "What if the array is empty?"
Candidate: "That won't happen" / "The problem says it's non-empty"

✅ ПРАВИЛЬНО:
Candidate: "Good point. Let me add a check for that.
If empty, I'll return -1 / throw exception / return empty.
What behavior would you prefer?"
```

### Think Aloud Template

```
При решении проговаривай:
1. "I'm thinking about using [pattern] because..."
2. "Let me consider the edge cases..."
3. "I notice this is similar to [known problem]..."
4. "The bottleneck here is [operation], so I'll optimize by..."
5. "I'm going to write a helper function for..."
```

---

## Категория 5: Code Quality

### Ошибка: Нечитаемый код

```kotlin
// ❌ НЕПРАВИЛЬНО:
fun f(a: IntArray): Int {
    var r = 0
    var i = 0
    var j = a.size - 1
    while (i < j) {
        r = maxOf(r, minOf(a[i], a[j]) * (j - i))
        if (a[i] < a[j]) i++ else j--
    }
    return r
}

// ✅ ПРАВИЛЬНО:
fun maxArea(heights: IntArray): Int {
    var maxWater = 0
    var left = 0
    var right = heights.size - 1

    while (left < right) {
        val width = right - left
        val height = minOf(heights[left], heights[right])
        val water = width * height
        maxWater = maxOf(maxWater, water)

        // Move pointer with smaller height
        if (heights[left] < heights[right]) {
            left++
        } else {
            right--
        }
    }

    return maxWater
}
```

### Ошибка: Copy-paste ошибки

```kotlin
// ❌ НЕПРАВИЛЬНО: copy-paste без изменения
if (node.left != null) {
    queue.add(node.left)
}
if (node.left != null) {  // Должно быть node.right!
    queue.add(node.left)  // Должно быть node.right!
}

// СОВЕТ: После copy-paste сразу проверь все переменные
```

### Code Style Checklist

```
□ Meaningful variable names
□ Consistent indentation
□ No magic numbers (use constants)
□ Short functions (< 20 lines ideal)
□ Early returns for edge cases
□ Comments for non-obvious logic
```

---

## Категория 6: Testing

### Ошибка: Не тестировать

```
❌ НЕПРАВИЛЬНО:
"Готово!"
*не проверяет*

✅ ПРАВИЛЬНО:
"Let me trace through with the given example:
Input: [1, 2, 3], target = 4
- i=0: num=1, complement=3, not in map, add 1→0
- i=1: num=2, complement=2, not in map, add 2→1
- i=2: num=3, complement=1, found! return [0, 2]
Output: [0, 2] ✓

Let me check edge cases:
- Empty array: returns early ✓
- No solution: correctly returns error ✓"
```

### Testing Strategy

```
1. Trace через given example
2. Проверь edge cases:
   - Empty/null
   - Single element
   - All same elements
3. Проверь boundary:
   - First/last elements
   - Min/max values
4. Проверь negative cases:
   - No solution exists
```

---

## Категория 7: Time Management

### Распределение времени (45 min interview)

```
┌────────────────────────────────────────────────┐
│ 0-7 min: Understand & Clarify                  │
├────────────────────────────────────────────────┤
│ 7-12 min: Plan & Discuss Approach              │
├────────────────────────────────────────────────┤
│ 12-35 min: Implement                           │
├────────────────────────────────────────────────┤
│ 35-42 min: Test & Debug                        │
├────────────────────────────────────────────────┤
│ 42-45 min: Optimize & Questions                │
└────────────────────────────────────────────────┘
```

### Ошибка: Застрять на одном подходе

```
❌ НЕПРАВИЛЬНО:
*20 минут пытается один подход*
*не работает*
*паника*

✅ ПРАВИЛЬНО:
"I've been trying recursive approach for 5 minutes
but it's getting complex. Let me step back and
consider an iterative solution with a stack instead."
```

### Recovery Strategies

```
Застрял? Попробуй:
1. Brute force — работает ли хотя бы?
2. Другая структура данных
3. Reverse thinking (от конца к началу)
4. Меньший пример
5. Попроси hint (это нормально!)
```

---

## Anti-Patterns Summary

| Anti-Pattern | Симптом | Решение |
|--------------|---------|---------|
| Code First | Сразу пишет код | UMPIRE method |
| Silent Coder | Молчит 5+ минут | Think aloud |
| Perfectionist | Переписывает чистый код | Move on when works |
| Defender | Спорит с feedback | Accept and adapt |
| Overconfident | Не тестирует | Always trace through |
| Panicker | Паникует при stuck | Дыши, попроси hint |
| Memorizer | Помнит решения, не понимает | Focus on patterns |

---

## Recovery Playbook

### Когда застрял

```
1. Дыши (2-3 глубоких вдоха)
2. Проговори что знаешь:
   "Input is..., output should be..., I've tried..."
3. Попроси hint:
   "I'm stuck on [specific part]. Could you give me a hint?"
4. Упрости задачу:
   "Let me solve a simpler version first"
```

### Когда нашёл баг

```
1. Не паникуй — это нормально
2. Проговори:
   "I see the issue. On line X, I should..."
3. Исправь
4. Объясни:
   "The bug was [description]. Now it's fixed because..."
```

### Когда не успеваешь

```
1. Сообщи:
   "I might not finish the full solution"
2. Приоритезируй:
   "Let me focus on the core logic and handle
   edge cases if time permits"
3. Покажи понимание:
   "Given more time, I would add [optimizations]"
```

---

## Practice Checklist

Перед каждой практикой:

```
□ Установил таймер
□ Без IDE подсказок
□ Объясняю вслух (даже один)
□ Пишу на доске/бумаге периодически
□ Анализирую ошибки после
```

После каждой задачи:

```
□ Что пошло хорошо?
□ Где застрял?
□ Какие edge cases пропустил?
□ Правильно ли оценил complexity?
□ Что сделаю по-другому?
```

---

## Связанные темы

### Prerequisites
- [LeetCode Roadmap](./leetcode-roadmap.md) — что практиковать
- Pattern knowledge — как решать

### Next Steps
- [Mock Interview Guide](./mock-interview-guide.md) — практика с фидбеком
- Behavioral interviews — STAR method

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [AlgoCademy](https://algocademy.com/blog/coding-interview-mistakes-that-cost-you-the-job/) | Blog | Mistake statistics |
| 2 | [Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/) | Guide | Best practices |
| 3 | [Design Gurus](https://www.designgurus.io/blog/how-to-avoid-coding-mistakes-during-interviews) | Blog | Prevention tips |
| 4 | [Educative](https://www.educative.io/blog/coding-interviews-mistakes) | Blog | Common patterns |
| 5 | [Dan Dreams of Coding](https://dandreamsofcoding.com/2012/11/17/screwing-up-the-technical-interview-common-mistakes/) | Blog | Edge cases |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
