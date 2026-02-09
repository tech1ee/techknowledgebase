---
title: "Строковые алгоритмы"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - interview
related:
  - "[[arrays-strings]]"
  - "[[string-algorithms-advanced]]"
  - "[[hash-tables]]"
---

# String Algorithms

## TL;DR

String matching: **KMP** — O(n+m) с prefix function, **Rabin-Karp** — O(n+m) average с rolling hash, **Z-function** — O(n) для всех вхождений. Выбор: KMP для single pattern, Rabin-Karp для multiple patterns, Z-function для анализа строк. Hashing = быстро, но collision риск. KMP/Z = точно, deterministic.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Поиск слова в книге

Представь, что ищешь слово "АЛГОРИТМ" в толстой книге.

**Наивный способ:**
```
Страница 1: Читаешь с первой буквы
  "АНАЛИЗ..." — нет, А есть, но дальше не то
  Сдвигаемся на 1 букву, пробуем снова
  И так для КАЖДОЙ позиции в книге
```

**Умный способ (KMP):**
```
Ищем "АЛГОРИТМ"

"АЛГОР..." — совпало 5 букв, потом несовпадение
Наивно: сдвигаемся на 1, начинаем заново

KMP: "Подожди! В слове 'АЛГОР' есть повторение 'АЛ'?
      Нет! Значит можно сдвинуться на 5 позиций!"

Экономим МНОГО сравнений!
```

---

### Аналогия 2: Prefix Function — "запасной парашют"

Представь, что строишь слово из букв, и каждый раз думаешь:

"Если следующая буква НЕ подойдёт, куда я могу вернуться, чтобы не начинать заново?"

```
Слово: "ABCABD"

Позиция 0: A      → π[0] = 0 (нет запасного)
Позиция 1: AB     → π[1] = 0 (нет повторов)
Позиция 2: ABC    → π[2] = 0 (нет повторов)
Позиция 3: ABCA   → π[3] = 1 ("A" в начале = "A" в конце)
Позиция 4: ABCAB  → π[4] = 2 ("AB" в начале = "AB" в конце)
Позиция 5: ABCABD → π[5] = 0 (нет совпадения)

π = [0, 0, 0, 1, 2, 0]
```

**Смысл:** Если на позиции 4 не совпало, можно "откатиться" на 2 символа и продолжить, а не начинать с нуля!

---

### Аналогия 3: Z-function — "насколько похоже на начало?"

Для каждой позиции отвечаем: "Насколько длинный префикс строки начинается здесь?"

```
Строка: "AABAAAB"

Позиция 0: -      (не считаем, это вся строка)
Позиция 1: "AB..." vs "AA..." → z[1] = 1 (только "A")
Позиция 2: "BAAAB" vs "AABAA" → z[2] = 0 (не совпадает)
Позиция 3: "AAAB" vs "AABA"   → z[3] = 2 (AA совпадает)
Позиция 4: "AAB" vs "AAB"     → z[4] = 3 (AAB совпадает!)
Позиция 5: "AB" vs "AA"       → z[5] = 1 (только A)
Позиция 6: "B" vs "A"         → z[6] = 0

z = [-, 1, 0, 2, 3, 1, 0]
```

**Применение для поиска:**
```
pattern + "$" + text = "ABA$AABABAABA"
Z-function найдёт все позиции, где z[i] = len(pattern) = 3
```

---

### Аналогия 4: Rabin-Karp — "отпечаток пальца"

Вместо сравнения символов сравниваем "отпечатки" (хеши).

```
Паттерн: "CAT" → hash("CAT") = 12345

Текст: "THE CAT SAT"

hash("THE") = 98765 ≠ 12345 → не совпадает
hash("HE ") = 54321 ≠ 12345 → не совпадает
hash("E C") = 11111 ≠ 12345 → не совпадает
hash(" CA") = 22222 ≠ 12345 → не совпадает
hash("CAT") = 12345 = 12345 → ВОЗМОЖНО совпадение!
  Проверяем посимвольно → ДА!
```

**Магия Rolling Hash:**
```
Не пересчитываем hash заново!

hash("CAT") → hash("ATS"):
  Убираем 'C', добавляем 'S'
  newHash = (oldHash - 'C' × base²) × base + 'S'

O(1) вместо O(m)!
```

---

### Числовой пример: Почему KMP быстрее

**Текст:** "AAAAAB"
**Паттерн:** "AAAB"

**Наивный подход:**
```
Позиция 0: AAAA vs AAAB → 3 совпадения, 4-е не совпало
Позиция 1: AAAA vs AAAB → 3 совпадения, 4-е не совпало
Позиция 2: AAAB vs AAAB → 4 совпадения → НАЙДЕНО!

Всего: 3 + 3 + 4 = 10 сравнений
```

**KMP с π = [0, 1, 2, 0]:**
```
Позиция 0: AAAA vs AAAB → 3 совпадения, 4-е не совпало
  π[3-1] = 2 → откатываемся на позицию 2 в паттерне

Продолжаем с позиции 1 в тексте, сравниваем с позиции 2 в паттерне:
  text[1..3] уже совпали! (мы знаем из π)
  text[3] = 'A' vs pattern[2] = 'A' → совпало
  text[4] = 'A' vs pattern[3] = 'B' → не совпало
  π[3-1] = 2 → откатываемся

Позиция 2: ...
  text[4] = 'A' vs pattern[2] = 'A' → совпало
  text[5] = 'B' vs pattern[3] = 'B' → совпало → НАЙДЕНО!

Всего: 3 + 1 + 1 + 1 + 1 = 7 сравнений (меньше!)
```

---

### Визуализация: Три алгоритма сравнения

```
Текст:    "A B C A B C A B D"
Паттерн:  "A B C A B D"

┌──────────────────────────────────────────────────────────┐
│ NAIVE: Сравниваем с каждой позиции заново               │
│                                                          │
│ A B C A B C A B D                                        │
│ A B C A B D       → 5 совпало, 6-е нет                  │
│   A B C A B D     → 0 совпало                           │
│     A B C A B D   → 0 совпало                           │
│       A B C A B D → ДА!                                  │
│                                                          │
│ Сравнений: 5 + 1 + 1 + 6 = 13                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ KMP: Используем prefix function                          │
│                                                          │
│ π("ABCABD") = [0, 0, 0, 1, 2, 0]                        │
│                                                          │
│ A B C A B C A B D                                        │
│ A B C A B D       → 5 совпало, π[4] = 2                 │
│       A B C A B D → Начинаем с позиции 2 в паттерне     │
│                   → Сразу совпало!                       │
│                                                          │
│ Сравнений: 5 + 1 + 4 = 10                               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ RABIN-KARP: Сравниваем хеши                              │
│                                                          │
│ hash("ABCABD") = 12345                                   │
│                                                          │
│ hash("ABCABC") = 12346 ≠ 12345 → пропускаем             │
│ hash("BCABCA") = 54321 ≠ 12345 → пропускаем             │
│ hash("CABCAB") = 11111 ≠ 12345 → пропускаем             │
│ hash("ABCABD") = 12345 = 12345 → проверяем!             │
│                                                          │
│ Сравнений хешей: 4, посимвольно: 6                       │
└──────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему String алгоритмы сложные

### Типичные ошибки студентов

#### Ошибка 1: Неправильное построение prefix function

**Симптом:** Бесконечный цикл или неправильные значения π

```
// ❌ ОШИБКА: j уменьшается неправильно
fun prefixFunction(s: String): IntArray {
    val pi = IntArray(s.length)
    for (i in 1 until s.length) {
        var j = pi[i - 1]
        while (j > 0 && s[i] != s[j]) {
            j--  // НЕПРАВИЛЬНО! Нужно j = pi[j-1]
        }
        if (s[i] == s[j]) j++
        pi[i] = j
    }
    return pi
}

// ✅ ПРАВИЛЬНО: используем prefix function для отката
fun prefixFunction(s: String): IntArray {
    val pi = IntArray(s.length)
    for (i in 1 until s.length) {
        var j = pi[i - 1]
        while (j > 0 && s[i] != s[j]) {
            j = pi[j - 1]  // ← Откат через prefix function!
        }
        if (s[i] == s[j]) j++
        pi[i] = j
    }
    return pi
}
```

---

#### Ошибка 2: Overflow в Rabin-Karp

**Симптом:** Неправильные хеши, false negatives

```
// ❌ ОШИБКА: умножение переполняется
val base = 26
var hash = 0L
for (c in s) {
    hash = hash * base + (c - 'a')  // Переполнение!
}

// ✅ ПРАВИЛЬНО: модульная арифметика
val base = 26L
val mod = 1_000_000_007L
var hash = 0L
for (c in s) {
    hash = (hash * base % mod + (c - 'a')) % mod
}
```

---

#### Ошибка 3: Отрицательный хеш при вычитании

**Симптом:** Неправильные хеши для rolling hash

```
// ❌ ОШИБКА: вычитание может дать отрицательное
fun rollHash(oldHash: Long, oldChar: Char, newChar: Char): Long {
    return (oldHash - (oldChar - 'a') * basePow) % mod * base + (newChar - 'a')
}

// ✅ ПРАВИЛЬНО: добавляем mod перед взятием остатка
fun rollHash(oldHash: Long, oldChar: Char, newChar: Char): Long {
    val removed = (oldHash - (oldChar - 'a') * basePow % mod + mod) % mod
    return (removed * base + (newChar - 'a')) % mod
}
```

---

#### Ошибка 4: Забыть проверить после hash match

**Симптом:** False positives (ложные срабатывания)

```
// ❌ ОШИБКА: доверяем хешу безоговорочно
if (windowHash == patternHash) {
    result.add(i)  // Collision! Может быть ошибка!
}

// ✅ ПРАВИЛЬНО: всегда проверяем посимвольно
if (windowHash == patternHash) {
    if (text.substring(i, i + pattern.length) == pattern) {
        result.add(i)
    }
}
```

---

#### Ошибка 5: Z-function начинается с 0, не с 1

**Симптом:** Off-by-one ошибки

```
// ❌ ОШИБКА: пытаемся считать z[0]
fun zFunction(s: String): IntArray {
    val z = IntArray(s.length)
    for (i in 0 until s.length) {  // Начинаем с 0!
        // z[0] = вся строка, это не нужно
    }
}

// ✅ ПРАВИЛЬНО: z[0] не определён, начинаем с 1
fun zFunction(s: String): IntArray {
    val z = IntArray(s.length)
    var l = 0
    var r = 0
    for (i in 1 until s.length) {  // ← Начинаем с 1!
        // ...
    }
    return z
}
```

---

#### Ошибка 6: Неправильный разделитель для pattern + text

**Симптом:** Ложные совпадения

```
// ❌ ОШИБКА: разделитель может встретиться в строках
val combined = pattern + "a" + text  // 'a' может быть в text!
val z = zFunction(combined)

// ✅ ПРАВИЛЬНО: уникальный разделитель
val combined = pattern + "$" + text  // '$' не встречается
// Или
val combined = pattern + "\u0000" + text  // null character
```

---

## Часть 3: Ментальные модели

### Модель 1: Prefix Function — "fallback позиции"

```
Prefix function π[i] отвечает на вопрос:
"Если на позиции i не совпало, куда откатиться?"

Строка:  A B C A B D
Индекс:  0 1 2 3 4 5
π:       0 0 0 1 2 0

Читаем: "Если не совпало на позиции 4,
         можно откатиться на позицию 2,
         потому что 'AB' уже совпало!"

      A B C A B D
      ─────┬─────
            └── π[4] = 2 означает:
                pattern[0..1] = pattern[3..4] = "AB"
```

---

### Модель 2: Z-function — "длина совпадения с началом"

```
Z[i] = длина наибольшего общего префикса
       между s[0..] и s[i..]

Строка: A A B A A A B
z:      - 1 0 2 3 1 0

z[4] = 3 означает:
  s[0..2] = "AAB"
  s[4..6] = "AAB"
  Совпадают 3 символа!

Применение: ищем pattern в text
  combined = pattern + "$" + text
  z[i] = len(pattern) → найдено совпадение!
```

---

### Модель 3: Rolling Hash — "скользящее окно для чисел"

```
Строка как число в системе счисления base:
  "CAT" = 'C'×base² + 'A'×base¹ + 'T'×base⁰
        = 3×26² + 1×26¹ + 20×1
        = 2054

Rolling: "CAT" → "ATS"
  Убираем 'C' слева:  (2054 - 3×676) = 26
  Умножаем на base:   26 × 26 = 676
  Добавляем 'S':      676 + 19 = 695

  hash("ATS") = 695

O(1) переход вместо O(m) пересчёта!
```

---

### Модель 4: Выбор алгоритма

```
┌────────────────────────────────────────────────────────────┐
│                  ВЫБОР STRING АЛГОРИТМА                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 1. ОДИН паттерн, нужна 100% точность?                     │
│    → KMP O(n+m) — детерминированный                       │
│                                                            │
│ 2. МНОГО паттернов одинаковой длины?                      │
│    → Rabin-Karp — один проход для всех                    │
│                                                            │
│ 3. Нужно найти ВСЕ вхождения + анализ строки?             │
│    → Z-function — универсальный инструмент                │
│                                                            │
│ 4. МНОГО паттернов РАЗНОЙ длины?                          │
│    → Aho-Corasick — автомат для всех паттернов            │
│                                                            │
│ 5. Строки ОЧЕНЬ короткие (< 100 символов)?                │
│    → Naive O(nm) — проще и достаточно быстро              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### Модель 5: Шаблоны кода

**KMP шаблон:**
```kotlin
// 1. Строим prefix function
val pi = prefixFunction(pattern)

// 2. Ищем
var j = 0
for (i in text.indices) {
    while (j > 0 && text[i] != pattern[j]) {
        j = pi[j - 1]  // Откат
    }
    if (text[i] == pattern[j]) j++
    if (j == pattern.length) {
        // Найдено на позиции i - j + 1
        j = pi[j - 1]  // Продолжаем поиск
    }
}
```

**Z-function шаблон:**
```kotlin
// Поиск pattern в text
val combined = pattern + "$" + text
val z = zFunction(combined)

for (i in pattern.length + 1 until combined.length) {
    if (z[i] == pattern.length) {
        // Найдено на позиции i - pattern.length - 1 в text
    }
}
```

---

## Зачем это нужно?

**Проблема:**

```
Поиск подстроки "needle" в тексте из 10^6 символов.

Наивно: O(n × m) = 10^6 × 6 = 6 × 10^6 сравнений
С KMP: O(n + m) = 10^6 + 6 ≈ 10^6 сравнений

В 6 раз быстрее! Для длинных паттернов разница ещё больше.
```

**Применения:**

| Задача | Алгоритм |
|--------|----------|
| Поиск подстроки | KMP, Rabin-Karp |
| Поиск всех вхождений | KMP, Z-function |
| Multiple patterns | Rabin-Karp, Aho-Corasick |
| Longest palindrome | Manacher |
| Suffix operations | Suffix Array, Z-function |

---

## Naive String Matching

### Как работает

```kotlin
/**
 * Наивный поиск подстроки
 *
 * ИДЕЯ: Проверяем каждую позицию text как возможное начало pattern
 * СЛОЖНОСТЬ: O(n × m) — worst case при pattern типа "AAAAB" в тексте "AAAA...A"
 */
fun naiveSearch(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val n = text.length
    val m = pattern.length

    // Проверяем каждую возможную начальную позицию
    for (i in 0..n - m) {
        var match = true
        for (j in 0 until m) {
            if (text[i + j] != pattern[j]) {
                match = false
                break
            }
        }
        if (match) result.add(i)
    }

    return result
}
```

**Сложность**: O(n × m) — неэффективно для длинных паттернов

### Проблема наивного подхода

```
Text:    "AAAAAAAAAB"
Pattern: "AAAAB"

Position 0: AAAAA vs AAAAB — 4 совпадения, потом несовпадение
Position 1: AAAAA vs AAAAB — опять 4 совпадения!

Повторяем одну и ту же работу много раз!
```

---

## KMP (Knuth-Morris-Pratt)

### Ключевая идея

```
Используем информацию о уже совпавших символах,
чтобы не начинать сравнение заново.

Prefix Function π[i] = длина наибольшего собственного
префикса строки s[0..i], который также является суффиксом.

"ABCABD"
π = [0, 0, 0, 1, 2, 0]

"AAAA"
π = [0, 1, 2, 3]
```

### Визуализация Prefix Function

```
s = "AABAAAB"

i=0: "A"       → π[0] = 0 (по определению)
i=1: "AA"      → "A" = "A" → π[1] = 1
i=2: "AAB"     → нет совпадений → π[2] = 0
i=3: "AABA"    → "A" = "A" → π[3] = 1
i=4: "AABAA"   → "AA" = "AA" → π[4] = 2
i=5: "AABAAA"  → "A" = "A" (не "AAA") → π[5] = 2? Нет!
                 Проверяем: "AAA" ≠ "AAB", "AA" ≠ "BA", "A" = "A"
                 π[5] = 1... Но "AAA"? Нет, проверяем иначе.

Правильно для i=5:
s[0..5] = "AABAA" + "A" = "AABAAA"
Суффикс "A"? Да, есть "A" в начале.
"AA"? Есть "AA" в начале.
"AAA"? Нет "AAA" в начале (есть "AAB").
π[5] = 2
```

### Реализация Prefix Function

```kotlin
/**
 * Prefix Function (π-функция) для KMP
 *
 * π[i] = длина наибольшего собственного prefix-suffix для s[0..i]
 *
 * ПОШАГОВЫЙ ПРИМЕР для s = "ABCABD":
 *   i=0: "A"      → π[0] = 0 (по определению, нет собственного префикса)
 *   i=1: "AB"     → "A" ≠ "B" → π[1] = 0
 *   i=2: "ABC"    → нет совпадений → π[2] = 0
 *   i=3: "ABCA"   → "A" = "A" → π[3] = 1
 *   i=4: "ABCAB"  → "AB" = "AB" → π[4] = 2
 *   i=5: "ABCABD" → s[5]='D' ≠ s[2]='C' → откат → π[5] = 0
 *
 *   Результат: [0, 0, 0, 1, 2, 0]
 *
 * СЛОЖНОСТЬ O(n): Amortized анализ — j увеличивается ≤ n раз,
 *                  значит уменьшается тоже ≤ n раз суммарно
 */
fun prefixFunction(s: String): IntArray {
    val n = s.length
    val pi = IntArray(n)
    // π[0] = 0: пустой/односимвольный prefix не считается "собственным"

    for (i in 1 until n) {
        // j = длина текущего кандидата на prefix-suffix
        // Начинаем с π[i-1] — лучшего результата для предыдущей позиции
        var j = pi[i - 1]

        // Откатываемся по цепочке π, пока не найдём совпадение
        // или j станет 0 (нет подходящего prefix-suffix)
        while (j > 0 && s[i] != s[j]) {
            // Следующий кандидат = π[j-1]
            // Это наибольший prefix-suffix для s[0..j-1]
            j = pi[j - 1]
        }

        // Если текущий символ совпал с s[j], расширяем prefix-suffix
        if (s[i] == s[j]) {
            j++
        }

        pi[i] = j
    }

    return pi
}
```

### KMP Поиск

```kotlin
/**
 * KMP Search — поиск через конкатенацию
 *
 * ИДЕЯ: Создаём строку "pattern#text" и вычисляем π-функцию.
 *       Если π[i] = m, значит prefix длины m совпал с суффиксом,
 *       т.е. pattern нашёлся в text!
 *
 * ПРИМЕР: pattern="AB", text="CABAB"
 *   combined = "AB#CABAB"
 *   π =        [0,0,0,0,1,2,1,2]
 *                         ↑   ↑ — π[i]=2=m → вхождения
 *   Позиция в text: i - 2*m = 5 - 4 = 1, и 7 - 4 = 3
 */
fun kmpSearch(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()

    // Конкатенация: pattern + разделитель + text
    // Разделитель '#' гарантирует π[i] ≤ m (не пересечёт границу)
    val combined = "$pattern#$text"
    val pi = prefixFunction(combined)
    val m = pattern.length

    // π[i] = m означает полное совпадение паттерна
    for (i in m + 1 until combined.length) {
        if (pi[i] == m) {
            // Позиция в text: i - m (длина pattern) - 1 (разделитель) - (m-1)
            // = i - 2*m
            result.add(i - 2 * m)
        }
    }

    return result
}

/**
 * KMP Search — оптимизированная версия без конкатенации
 *
 * ПРЕИМУЩЕСТВО: O(m) памяти вместо O(n+m)
 *               Работает с потоковыми данными
 */
fun kmpSearchOptimized(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val n = text.length
    val m = pattern.length
    val pi = prefixFunction(pattern)

    // j = количество уже совпавших символов паттерна
    var j = 0

    for (i in 0 until n) {
        // При несовпадении откатываемся по π-функции
        // Используем уже вычисленную информацию о prefix-suffix
        while (j > 0 && text[i] != pattern[j]) {
            j = pi[j - 1]
        }

        if (text[i] == pattern[j]) {
            j++
        }

        // j = m → все символы паттерна совпали!
        if (j == m) {
            result.add(i - m + 1)
            // Продолжаем искать следующие вхождения
            // (паттерны могут пересекаться: "AA" в "AAA" → [0, 1])
            j = pi[j - 1]
        }
    }

    return result
}
```

### Сложность

- Prefix function: **O(m)**
- Search: **O(n)**
- **Total: O(n + m)**

---

## Z-Function

### Ключевая идея

```
z[i] = длина наибольшего общего префикса
       строки s и её суффикса, начинающегося с позиции i.

s = "AABXAAB"
z = [-, 1, 0, 0, 3, 1, 0]

z[0] не определён (или = n по соглашению)
z[1]: "ABXAAB" vs "AABXAAB" → "A" общий → z[1] = 1
z[4]: "AAB" vs "AABXAAB" → "AAB" общий → z[4] = 3
```

### Визуализация

```
s = "AAAAA"

i=1: s[1..] = "AAAA", s = "AAAAA" → z[1] = 4
i=2: s[2..] = "AAA",  s = "AAAAA" → z[2] = 3
i=3: s[3..] = "AA",   s = "AAAAA" → z[3] = 2
i=4: s[4..] = "A",    s = "AAAAA" → z[4] = 1

z = [5, 4, 3, 2, 1]
```

### Реализация

```kotlin
/**
 * Z-функция за O(n)
 *
 * КЛЮЧЕВАЯ ИДЕЯ: Поддерживаем [l, r] — "z-box", самый правый отрезок,
 *                где s[l..r] = s[0..r-l] (совпадает с префиксом)
 *
 * Если i < r, то s[i] уже внутри z-box, и мы можем использовать
 * ранее вычисленное z[i-l] как начальное значение z[i].
 *
 * ВИЗУАЛИЗАЦИЯ:
 *   s = "AABXAAB"
 *       [l----r]    z-box: s[4..6] = "AAB" = s[0..2]
 *
 *   Для i=5: i-l=1, z[1]=1
 *            z[5] ≥ min(r-i, z[1]) = min(1, 1) = 1
 */
fun zFunction(s: String): IntArray {
    val n = s.length
    val z = IntArray(n)
    z[0] = n  // По соглашению: вся строка совпадает сама с собой

    // [l, r) — границы самого правого z-box
    var l = 0
    var r = 0

    for (i in 1 until n) {
        if (i < r) {
            // Мы внутри z-box! Используем симметрию:
            // z[i] ≥ min(r-i, z[i-l])
            z[i] = minOf(r - i, z[i - l])
        }

        // Наивное расширение: проверяем символы дальше z[i]
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++
        }

        // Обновляем z-box, если нашли более правый
        if (i + z[i] > r) {
            l = i
            r = i + z[i]
        }
    }

    return z
}
```

### Z-Function для поиска

```kotlin
/**
 * Поиск паттерна через Z-функцию
 *
 * ИДЕЯ: В строке "pattern#text" значение z[i] = m означает,
 *       что суффикс с позиции i совпадает с паттерном целиком
 */
fun zSearch(text: String, pattern: String): List<Int> {
    val combined = "$pattern#$text"
    val z = zFunction(combined)
    val m = pattern.length
    val result = mutableListOf<Int>()

    for (i in m + 1 until combined.length) {
        // z[i] = m → полное совпадение с паттерном
        if (z[i] == m) {
            result.add(i - m - 1)  // Позиция в text
        }
    }

    return result
}
```

### Сложность

**O(n)** — каждый символ обрабатывается константное число раз

---

## Rabin-Karp (Rolling Hash)

### Ключевая идея

```
Вместо посимвольного сравнения сравниваем HASH строк.

Hash("ABC") = 'A'×p² + 'B'×p + 'C' (по модулю)

Rolling hash позволяет вычислить hash(s[i+1..j+1])
из hash(s[i..j]) за O(1).
```

### Визуализация Rolling Hash

```
s = "ABCDE", window = 3, p = 31, mod = 10^9+7

hash("ABC") = A×31² + B×31 + C = 65×961 + 66×31 + 67 = 64573

Shift right: "BCD"
hash("BCD") = (hash("ABC") - A×31²) × 31 + D
            = (64573 - 65×961) × 31 + 68
            = 2528 × 31 + 68
            = 78436

WHY O(1)? Вычитаем старый символ, умножаем, добавляем новый.
```

### Реализация

```kotlin
/**
 * Rabin-Karp алгоритм поиска подстроки
 *
 * ИДЕЯ: Polynomial Rolling Hash
 *   hash(s) = s[0]×p^(n-1) + s[1]×p^(n-2) + ... + s[n-1]×p^0 (mod M)
 *
 * ПРЕИМУЩЕСТВО: Можно пересчитать hash за O(1) при сдвиге окна
 */
class RabinKarp(private val base: Long = 31, private val mod: Long = 1_000_000_007) {

    /**
     * Поиск одного паттерна
     *
     * ПОШАГОВЫЙ ПРИМЕР: text="ABCAB", pattern="CAB"
     *   patternHash = hash("CAB")
     *   windowHash[0] = hash("ABC")
     *   windowHash[1] = hash("BCA") — rolling update
     *   windowHash[2] = hash("CAB") = patternHash → проверяем → match!
     */
    fun search(text: String, pattern: String): List<Int> {
        val n = text.length
        val m = pattern.length
        if (m > n) return emptyList()

        val result = mutableListOf<Int>()

        // Предвычисляем base^(m-1) для удаления старшего разряда
        var basePow = 1L
        repeat(m - 1) { basePow = (basePow * base) % mod }

        // Hash паттерна — вычисляем один раз
        var patternHash = 0L
        for (c in pattern) {
            patternHash = (patternHash * base + (c - 'a' + 1)) % mod
        }

        // Hash первого окна text[0..m-1]
        var windowHash = 0L
        for (i in 0 until m) {
            windowHash = (windowHash * base + (text[i] - 'a' + 1)) % mod
        }

        // Sliding window: сдвигаем окно по тексту
        for (i in 0..n - m) {
            if (i > 0) {
                // Rolling hash за O(1):
                // 1. Убираем старший разряд (левый символ)
                // 2. Умножаем на base (сдвигаем разряды)
                // 3. Добавляем новый символ
                windowHash = (windowHash - (text[i - 1] - 'a' + 1) * basePow % mod + mod) % mod
                windowHash = (windowHash * base + (text[i + m - 1] - 'a' + 1)) % mod
            }

            // Hash совпал — возможно collision!
            if (windowHash == patternHash) {
                // Посимвольная проверка для исключения false positive
                if (text.substring(i, i + m) == pattern) {
                    result.add(i)
                }
            }
        }

        return result
    }

    /**
     * Поиск нескольких паттернов одновременно
     *
     * ПРЕИМУЩЕСТВО перед KMP: один проход по тексту для всех паттернов
     *                         одинаковой длины
     */
    fun searchMultiple(text: String, patterns: List<String>): Map<String, List<Int>> {
        val result = mutableMapOf<String, MutableList<Int>>()
        val patternHashes = mutableMapOf<Long, MutableList<String>>()

        // Группируем паттерны по hash (возможны коллизии!)
        for (pattern in patterns) {
            result[pattern] = mutableListOf()
            var hash = 0L
            for (c in pattern) {
                hash = (hash * base + (c - 'a' + 1)) % mod
            }
            patternHashes.getOrPut(hash) { mutableListOf() }.add(pattern)
        }

        // Обрабатываем каждую уникальную длину отдельно
        val lengths = patterns.map { it.length }.toSet()
        for (len in lengths) {
            if (len > text.length) continue

            var basePow = 1L
            repeat(len - 1) { basePow = (basePow * base) % mod }

            var windowHash = 0L
            for (i in 0 until len) {
                windowHash = (windowHash * base + (text[i] - 'a' + 1)) % mod
            }

            for (i in 0..text.length - len) {
                if (i > 0) {
                    windowHash = (windowHash - (text[i - 1] - 'a' + 1) * basePow % mod + mod) % mod
                    windowHash = (windowHash * base + (text[i + len - 1] - 'a' + 1)) % mod
                }

                patternHashes[windowHash]?.forEach { pattern ->
                    if (pattern.length == len && text.substring(i, i + len) == pattern) {
                        result[pattern]!!.add(i)
                    }
                }
            }
        }

        return result
    }
}
```

### Сложность

- Average: **O(n + m)**
- Worst (many collisions): O(n × m)

### Double Hashing (избегаем collisions)

```kotlin
/**
 * Двойное хеширование для снижения вероятности коллизий
 *
 * С одним hash вероятность коллизии ≈ 1/mod ≈ 10^-9
 * С двумя независимыми hash: ≈ 1/mod² ≈ 10^-18
 *
 * Практически исключает false positives
 */
class DoubleHash {
    private val base1 = 31L
    private val base2 = 37L
    private val mod1 = 1_000_000_007L
    private val mod2 = 1_000_000_009L

    fun hash(s: String): Pair<Long, Long> {
        var h1 = 0L
        var h2 = 0L
        for (c in s) {
            h1 = (h1 * base1 + (c - 'a' + 1)) % mod1
            h2 = (h2 * base2 + (c - 'a' + 1)) % mod2
        }
        return h1 to h2
    }
}
```

---

## Сравнение алгоритмов

| Алгоритм | Время | Память | Deterministic | Best For |
|----------|-------|--------|---------------|----------|
| Naive | O(nm) | O(1) | ✓ | Короткие строки |
| KMP | O(n+m) | O(m) | ✓ | Single pattern |
| Z-function | O(n+m) | O(n+m) | ✓ | String analysis |
| Rabin-Karp | O(n+m) avg | O(1) | ✗ | Multiple patterns |

---

## Распространённые ошибки

### 1. Overflow в Rabin-Karp

```kotlin
// ❌ НЕПРАВИЛЬНО: overflow при умножении
hash = hash * base + char  // Long overflow!

// ✅ ПРАВИЛЬНО: модульная арифметика
hash = (hash * base % mod + char) % mod
```

### 2. Negative hash

```kotlin
// ❌ НЕПРАВИЛЬНО: вычитание может дать отрицательное
hash = (hash - oldChar * basePow) % mod  // Может быть < 0!

// ✅ ПРАВИЛЬНО: добавляем mod
hash = (hash - oldChar * basePow % mod + mod) % mod
```

### 3. Забыть проверку после hash match

```kotlin
// ❌ НЕПРАВИЛЬНО: collision может дать false positive
if (windowHash == patternHash) {
    result.add(i)  // Может быть неправильно!
}

// ✅ ПРАВИЛЬНО: посимвольная проверка
if (windowHash == patternHash && text.substring(i, i+m) == pattern) {
    result.add(i)
}
```

---

## Практика

### Концептуальные вопросы

1. **Когда KMP лучше Rabin-Karp?**

   KMP гарантирует O(n+m) всегда. Rabin-Karp может деградировать при collisions. Для single deterministic search — KMP.

2. **Зачем нужен разделитель в KMP/Z-function?**

   Без разделителя паттерн может "продолжиться" в текст, давая ложное совпадение π[i] > m.

3. **Как выбрать base и mod для hashing?**

   base > размер алфавита, желательно простое. mod — большое простое число. Для надёжности — double hashing.

### LeetCode задачи

| # | Название | Сложность | Алгоритм |
|---|----------|-----------|----------|
| 28 | Find the Index of the First Occurrence | Easy | KMP/Rabin-Karp |
| 459 | Repeated Substring Pattern | Easy | KMP/Z-function |
| 214 | Shortest Palindrome | Hard | KMP |
| 1392 | Longest Happy Prefix | Hard | KMP/Z-function |
| 686 | Repeated String Match | Medium | Rabin-Karp |
| 187 | Repeated DNA Sequences | Medium | Rolling Hash |

---

## Связанные темы

### Prerequisites
- Arrays and strings basics
- Modular arithmetic

### Unlocks
- [String Advanced](./string-advanced.md) — Suffix Array, Aho-Corasick
- Pattern matching problems
- Bioinformatics algorithms

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms: Prefix Function](https://cp-algorithms.com/string/prefix-function.html) | Reference | KMP |
| 2 | [CP-Algorithms: Z-Function](https://cp-algorithms.com/string/z-function.html) | Reference | Z-function |
| 3 | [CP-Algorithms: Rabin-Karp](https://cp-algorithms.com/string/rabin-karp.html) | Reference | Hashing |
| 4 | [CLRS] Introduction to Algorithms | Book | Theory |

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция KMP/Z-function/Rabin-Karp, 6 типичных ошибок, 5 ментальных моделей)*
