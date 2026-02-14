---
title: "Обзор соревновательного программирования"
created: 2026-02-09
modified: 2026-02-13
type: overview
status: published
tags:
  - topic/cs-fundamentals
  - type/overview
  - level/intermediate
related:
  - "[[cs-fundamentals-overview]]"
  - "[[contest-strategy]]"
  - "[[implementation-tips]]"
  - "[[problem-classification]]"
reading_time: 16
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Competitive Programming Overview

## TL;DR

Competitive Programming — соревновательное решение алгоритмических задач на время. Платформы: **Codeforces**, **AtCoder**, **LeetCode**. Ключевые навыки: pattern recognition, fast implementation, debugging under pressure. Рейтинги: Codeforces (800-3500+), AtCoder (colors). Подготовка: 200+ задач для уверенного уровня.

---

## Интуиция

### Аналогия 1: CP как спортивные шахматы

```
ШАХМАТЫ С ЧАСАМИ = COMPETITIVE PROGRAMMING:

Обычные шахматы:           Блиц (3 мин на партию):
• Думай сколько хочешь     • Каждая секунда на счету
• Идеальный ход важнее     • Хороший ход СЕЙЧАС > идеальный ПОТОМ
• Нет давления             • Стресс, адреналин

CP = алгоритмы под давлением времени.
Знать алгоритм недостаточно — нужно применить его БЫСТРО.
```

### Аналогия 2: Рейтинг как ELO в шахматах

```
РЕЙТИНГОВАЯ СИСТЕМА:

Выигрываешь у сильного → много очков
Проигрываешь слабому → теряешь много

Codeforces рейтинг работает так же:
• Решил больше ожидаемого → рейтинг растёт
• Решил меньше → падает
• Стабильные результаты → медленный рост

Ключ: КОНСИСТЕНТНОСТЬ важнее случайных побед.
```

---

## Частые ошибки

### Ошибка 1: Решать слишком сложные задачи

**СИМПТОМ:** Час сидишь над D, когда не решены A и B

```
НЕПРАВИЛЬНО:
"Хочу вырасти → буду решать сложные задачи"
Результат: фрустрация, 0 прогресса

ПРАВИЛЬНО:
Решай задачи на своём уровне (+100-200 рейтинга)
• Рейтинг 1200 → задачи 1200-1400
• Понял 5 задач уровня → переходи выше
```

**РЕШЕНИЕ:** Правило 50/50 — 50% задач должны решаться за 30 мин.

### Ошибка 2: Не анализировать свои ошибки

**СИМПТОМ:** Повторяешь одни и те же баги contest за contest

```
НЕПРАВИЛЬНО: Решил/не решил → идём дальше
ПРАВИЛЬНО: После контеста — upsolving + разбор

Что анализировать:
□ Почему получил WA? (баг, edge case, неверный алгоритм?)
□ Почему не решил? (не знал алгоритм? не хватило времени?)
□ Как решили другие? (читай разборы!)
```

**РЕШЕНИЕ:** Веди лог ошибок. После 10 контестов увидишь паттерны.

### Ошибка 3: Игнорировать время на отладку

**СИМПТОМ:** TLE/WA в последние 5 минут, не успел исправить

```
ТАЙМИНГ КОНТЕСТА (2 часа, 5 задач):
• A: 5-10 мин
• B: 10-15 мин
• C: 20-30 мин
• D: 30-40 мин
• Буфер на отладку: 15-20 мин (!!)

Без буфера → один баг = провал контеста.
```

**РЕШЕНИЕ:** Всегда оставляй 15+ минут на исправления.

---

## Ментальные модели

### Модель 1: "Constraint → Algorithm"

```
Смотри на N в условии:

N ≤ 20     → Перебор (2^N), bitmask DP
N ≤ 1000   → O(N²) — простой DP, nested loops
N ≤ 10^5  → O(N log N) — сортировка, бинпоиск, segment tree
N ≤ 10^6  → O(N) — линейные алгоритмы
N ≤ 10^9  → O(log N) или O(1) — математика

Ограничения ПОДСКАЗЫВАЮТ алгоритм!
```

### Модель 2: "Сначала AC, потом оптимизация"

```
ПРИОРИТЕТЫ НА КОНТЕСТЕ:

1. Working solution (даже неоптимальная)
2. Все тесты проходят
3. Оптимизация (если нужно)

Рабочий O(N²) лучше, чем незаконченный O(N log N).
Сначала РАБОТАЕТ, потом БЫСТРО.
```

---

## Зачем это нужно?

**Преимущества:**

| Аспект | Польза |
|--------|--------|
| Алгоритмы | Глубокое понимание DS и алгоритмов |
| Скорость | Быстрое написание correct кода |
| Debugging | Находить баги под давлением |
| Interview | Техническая подготовка |
| Problem solving | Системный подход к задачам |

---

## Платформы

### Codeforces

```
Тип: Регулярные contests (Div1, Div2, Div3, Div4)
Рейтинг: 800-3500+
Частота: 2-3 раза в неделю
Язык задач: Английский/Русский

Цвета рейтинга:
Gray      < 1200   Newbie
Green     1200-1399 Pupil
Cyan      1400-1599 Specialist
Blue      1600-1899 Expert
Violet    1900-2099 Candidate Master
Orange    2100-2399 Master
Red       2400+     Grandmaster/LGM
```

### AtCoder

```
Тип: ABC (Beginner), ARC (Regular), AGC (Grand)
Рейтинг: 0-4000+
Частота: 1-2 раза в неделю
Особенность: Очень качественные задачи

Цвета:
Gray      < 400
Brown     400-799
Green     800-1199
Cyan      1200-1599
Blue      1600-1999
Yellow    2000-2399
Orange    2400-2799
Red       2800+
```

### LeetCode

```
Тип: Weekly/Biweekly contests
Фокус: Interview preparation
Рейтинг: ~1500-3000+
Особенность: Похоже на реальные интервью
```

---

## Структура решения

### Template

```kotlin
import java.io.*
import java.util.*

fun main() {
    val br = BufferedReader(InputStreamReader(System.`in`))
    val bw = BufferedWriter(OutputStreamWriter(System.`out`))

    val t = br.readLine().toInt()
    repeat(t) {
        val (n, m) = br.readLine().split(" ").map { it.toInt() }
        // solve
        bw.write("$answer\n")
    }

    bw.flush()
}
```

### Fast I/O (критично для больших данных)

```kotlin
// BufferedReader в 10-100x быстрее Scanner!
// Scanner использует регулярные выражения — это медленно.
// BufferedReader просто читает текст построчно.
val br = BufferedReader(InputStreamReader(System.`in`))

// StringTokenizer разбивает строку на токены по пробелам
// Быстрее чем split(" ") — не создаёт массив строк
val st = StringTokenizer(br.readLine())
val n = st.nextToken().toInt()

// BufferedWriter накапливает вывод в буфере
// println() делает системный вызов на КАЖДУЮ строку — очень медленно!
// BufferedWriter делает один системный вызов при flush()
val bw = BufferedWriter(OutputStreamWriter(System.`out`))
bw.write("$result\n")
bw.flush()
```

---

## Типичные категории задач

### По сложности (Codeforces)

```
A (800-1000): Implementation, math basics
B (1000-1300): Simple algorithms, greedy
C (1300-1600): Standard algorithms, DP basics
D (1600-2000): Advanced DP, graphs, data structures
E (2000-2400): Complex combinations of techniques
F+ (2400+): Research-level problems
```

### По темам

| Тема | Частота | Примеры |
|------|---------|---------|
| Implementation | Очень высокая | Simulation, parsing |
| Math | Высокая | Number theory, combinatorics |
| Greedy | Высокая | Scheduling, intervals |
| DP | Высокая | Knapsack, LIS, tree DP |
| Graphs | Средняя | BFS, DFS, shortest paths |
| Data Structures | Средняя | Segment tree, DSU |
| Strings | Средняя | Hashing, KMP |
| Binary Search | Средняя | Search answer |
| Geometry | Низкая | Convex hull, intersections |

---

## Стратегия на контесте

### Распределение времени (2h contest, 6 problems)

```
0-5 min:   Читаем ВСЕ задачи быстро
5-20 min:  Решаем A
20-40 min: Решаем B
40-70 min: Решаем C
70-100 min: Решаем D (или E если D сложная)
100-120 min: Debug / попытки на оставшиеся
```

### Приоритеты

```
1. Читай внимательно (многие WA из-за непонимания)
2. Начни с примеров (проверь понимание)
3. Думай о edge cases ДО кодирования
4. Не застревай (15 min на задачу max, потом switch)
5. Проверяй код перед submit
```

---

## Типичные ошибки

### Runtime Error

```kotlin
// ❌ Array index out of bounds
arr[n]  // когда arr.size = n

// ❌ Division by zero
val x = a / b  // когда b = 0

// ❌ Stack overflow
fun f(n: Int): Int = if (n == 0) 1 else f(n-1)  // n > 10^5
```

### Wrong Answer

```kotlin
// ❌ Integer overflow
val sum = a * b  // Int overflow если a, b большие

// ❌ Off-by-one
for (i in 0 until n-1)  // пропустили последний элемент

// ❌ Неправильный формат вывода
print(answer)  // Нужен println или \n
```

### Time Limit Exceeded

```kotlin
// ❌ Неэффективный алгоритм
for (i in 0 until n)
    for (j in 0 until n)
        // O(n²) когда n = 10^5

// ❌ Медленный I/O
println(x)  // Используй BufferedWriter
```

---

## Путь развития

### Beginner (0-3 месяца)

```
Цель: Рейтинг 1200+ (Codeforces Pupil)

Фокус:
- Базовые структуры данных (array, set, map)
- Базовые алгоритмы (sorting, binary search)
- Простые реализации
- 50+ задач уровня A-B

Ресурсы:
- USACO Guide (Bronze)
- Codeforces Div3/Div4
```

### Intermediate (3-12 месяцев)

```
Цель: Рейтинг 1600+ (Codeforces Expert)

Фокус:
- DP (классические паттерны)
- Графы (BFS, DFS, shortest paths)
- Продвинутые DS (segment tree, DSU)
- Greedy с доказательствами
- 200+ задач уровня B-D

Ресурсы:
- CSES Problem Set
- AtCoder ABC
- CP-Algorithms
```

### Advanced (1-2 года)

```
Цель: Рейтинг 2000+ (Candidate Master)

Фокус:
- Сложный DP (bitmask, digit, tree)
- Flows, matching
- String algorithms
- Math (number theory, combinatorics)
- 500+ задач

Ресурсы:
- Codeforces Div1
- AtCoder ARC/AGC
- Competitive Programming 3/4
```

---

## Полезные техники

### Binary Search on Answer

```kotlin
/**
 * Binary Search on Answer — когда ответ монотонный
 *
 * Идея: если ответ X возможен, то все ответы > X тоже возможны
 * (или наоборот: если X возможен, то все < X тоже)
 *
 * Примеры:
 * - "Минимальная максимальная нагрузка" — если можем с X, можем с X+1
 * - "Максимальный минимальный gap" — если можем с X, можем с X-1
 */
fun solve(arr: IntArray, target: Int): Int {
    var lo = 0
    var hi = 1_000_000_000

    while (lo < hi) {
        val mid = lo + (hi - lo) / 2
        if (check(arr, mid, target)) {
            hi = mid
        } else {
            lo = mid + 1
        }
    }

    return lo
}
```

### Coordinate Compression

```kotlin
/**
 * Сжатие координат — когда значения большие, но их МАЛО
 *
 * Пример: массив [1000000000, 1, 500000000]
 * После сжатия: [2, 0, 1] (индексы в отсортированном порядке)
 *
 * Зачем? Теперь можно использовать значения как индексы массива!
 * Это открывает возможность использовать Segment Tree, BIT и т.д.
 */
fun compress(arr: IntArray): IntArray {
    val sorted = arr.toSortedSet().toList()
    val map = sorted.withIndex().associate { it.value to it.index }
    return arr.map { map[it]!! }.toIntArray()
}
```

### Prefix Sum / Difference Array

```kotlin
/**
 * Prefix Sum — сумма на отрезке за O(1)
 *
 * prefix[i] = сумма arr[0..i-1]
 * sum(l, r) = prefix[r+1] - prefix[l]
 *
 * Построение: O(n), запрос: O(1)
 */
val prefix = IntArray(n + 1)
for (i in 0 until n) prefix[i + 1] = prefix[i] + arr[i]

// Sum [l, r] = prefix[r+1] - prefix[l]
```

---

## Практика

### Рекомендуемый план

```
Неделя 1-4: 5 задач/день уровня A-B
Неделя 5-8: 3-4 задачи/день уровня B-C
Неделя 9-12: 2-3 задачи/день уровня C-D
+ Участие в 1-2 contests в неделю
```

### Разбор после контеста

```
1. Дорешай все задачи которые не успел
2. Прочитай editorial
3. Посмотри решения топ участников
4. Запиши новые техники
```

---

## Связанные темы

### Prerequisites
- [LeetCode Roadmap](../interview-prep/leetcode-roadmap.md)
- Basic algorithms and data structures

### Unlocks
- [Contest Strategy](./contest-strategy.md)
- [Implementation Tips](./implementation-tips.md)
- ICPC/IOI preparation

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Codeforces](https://codeforces.com) | Platform | Contests |
| 2 | [USACO Guide](https://usaco.guide) | Course | Structured learning |
| 3 | [CP-Algorithms](https://cp-algorithms.com) | Reference | Algorithms |
| 4 | [CSES Problem Set](https://cses.fi/problemset/) | Practice | 300 classic problems |


---

## Проверь себя

> [!question]- Почему соревновательное программирование развивает навыки, полезные на coding-интервью?
> CP тренирует: 1) Pattern recognition — быстрое распознавание типа задачи. 2) Fast implementation — чистый код под давлением. 3) Edge case мышление — тесты заставляют думать о граничных случаях. 4) Complexity analysis — constraints определяют алгоритм. 5) Debugging under pressure. Эти навыки напрямую переносятся на интервью.

> [!question]- Как выбрать платформу для начала: Codeforces, AtCoder или LeetCode?
> LeetCode: для подготовки к интервью (задачи в формате FAANG). Codeforces: для роста в CP (регулярные contests, рейтинг, editorial). AtCoder: чистые задачи, хорошие beginner contests (ABC). Начало: LeetCode Easy -> Codeforces Div.2 A-B -> развитие дальше. Каждая платформа имеет свою нишу.

> [!question]- Сколько задач нужно решить для уверенного уровня и почему качество важнее количества?
> 200+ задач для уверенного intermediate. Но решить 200 с разбором и пониманием лучше, чем 500 с подглядыванием. Ключ: после решения — читать editorial, изучать alternative approaches, upsolving (дорешивание нерешённых). Deliberate practice: решать на границе своего уровня.

## Ключевые карточки

Какие три главные CP платформы?
?
1) Codeforces: крупнейшая, регулярные contests, рейтинг 800-3500+, Div.1-4. 2) AtCoder: японская, чистые задачи, ABC/ARC/AGC, рейтинг с цветами. 3) LeetCode: фокус на интервью, Weekly/Biweekly contests, без строгого рейтинга.

Что такое рейтинговая система Codeforces?
?
ELO-подобная: 800 (Newbie) -> 1200 (Pupil) -> 1400 (Specialist) -> 1600 (Expert) -> 1900 (Candidate Master) -> 2100 (Master) -> 2400+ (Grandmaster). Рейтинг меняется после каждого contest в зависимости от места и рейтинга соперников.

Что такое upsolving и почему это ключевой навык?
?
Upsolving: решение задач после конца contest, которые не успел решить. Читаешь editorial, разбираешь подход, реализуешь сам. Самый эффективный способ обучения в CP: задача на границе твоего уровня + разбор = максимальный рост.

Какие типы contests на Codeforces?
?
Div.1: для рейтинга 1900+, 5-6 задач, сложные. Div.2: для рейтинга < 1900, 5-6 задач A(easy) до F(hard). Div.3: для < 1600, 6-7 задач, проще. Div.4: для < 1400, самые простые. Educational: обучающие, нет рейтинга для Div.1.

Как подсчитать сколько операций допускает time limit?
?
~10^8 операций в секунду для C++, ~10^7 для Python. Если N = 10^5 и TL = 2s: O(N^2) = 10^10 — TLE. O(N log N) = 10^5 * 17 ~ 2*10^6 — OK. Constraints подсказывают нужную сложность.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[competitive/contest-strategy]] | Стратегия на контесте |
| Углубиться | [[competitive/problem-classification]] | Классификация задач |
| Смежная тема | [[patterns/patterns-overview]] | Паттерны для решения задач |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |


---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
