---
title: "Продвинутые строковые алгоритмы"
created: 2026-02-08
modified: 2026-02-13
type: deep-dive
status: published
difficulty: advanced
confidence: high
cs-foundations:
  - pattern-matching
  - finite-automata
  - suffix-structures
  - hash-functions
  - amortized-analysis
prerequisites:
  - "[[arrays-strings]]"
  - "[[hash-tables]]"
  - "[[trees-binary]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/advanced
  - interview
related:
  - "[[two-pointers-pattern]]"
  - "[[sliding-window-pattern]]"
reading_time: 64
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# String Algorithms Advanced

## TL;DR

Продвинутые строковые алгоритмы решают задачи поиска подстрок и паттернов за линейное время. **KMP** и **Z-функция** — поиск одного паттерна за O(n+m). **Rabin-Karp** — rolling hash для множественного поиска. **Aho-Corasick** — поиск множества паттернов за O(n+m+z). **Suffix Array** — все подстроки за O(n log n) построение. **Manacher** — все палиндромы за O(n). Ключевая идея: **предобработка паттерна/текста** позволяет избежать повторных сравнений.

---

## Часть 1: Интуиция без кода

> **Цель:** понять ИДЕИ продвинутых строковых алгоритмов до любого кода.

### Почему наивный поиск неэффективен?

Представь, что ты ищешь слово "AAAB" в тексте "AAAAAAAAAB":

```
Наивный подход:
Текст:   A A A A A A A A A B
Паттерн: A A A B
         ✓ ✓ ✓ ✗ — не совпало, сдвигаем на 1

Текст:   A A A A A A A A A B
Паттерн:   A A A B
           ✓ ✓ ✓ ✗ — опять не совпало...

И так 7 раз подряд! Каждый раз сравниваем 4 символа.
Всего: 7 × 4 = 28 сравнений для текста длины 10.
В худшем случае: O(n × m) сравнений.
```

**Проблема:** мы "забываем" информацию, полученную при предыдущих сравнениях!

### Ключевой инсайт всех продвинутых алгоритмов

```
┌─────────────────────────────────────────────────────────────────┐
│              ГЛАВНАЯ ИДЕЯ: НЕ НАЧИНАЙ С НУЛЯ                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Наивный подход:                                                 │
│    При несовпадении → сдвинь на 1, начни сравнение заново       │
│    Забываем всё, что узнали → O(n×m)                            │
│                                                                  │
│  Умный подход:                                                   │
│    При несовпадении → используй СТРУКТУРУ паттерна              │
│    Знаем, что уже совпало → пропускаем повторные сравнения      │
│    → O(n+m)                                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Аналогия 1: Поиск по отпечатку пальца (Rabin-Karp)

Ты детектив, ищешь преступника по отпечатку пальца:

```
Глупый способ:
  Для каждого человека в базе:
    Сравни каждую линию отпечатка (долго!)

Умный способ (хеширование):
  Вычисли "хеш" отпечатка преступника (короткий код)
  Для каждого человека:
    Сравни хеши (быстро — одно число!)
    Если хеши совпали — проверь детально

Rolling hash — ещё умнее:
  При переходе к следующему человеку:
    Не вычисляй хеш заново
    Обнови хеш: убери старый палец, добавь новый
    → O(1) на каждого человека!
```

### Аналогия 2: Таблица переходов (KMP)

Представь, что ты учишь робота искать слово "ABCDABD":

```
Наивный робот:
  - Совпало "ABCDAB", но потом 'D' ≠ 'C'
  - Робот: "Эх, начну сначала с позиции 1..."

Умный робот (KMP):
  - Совпало "ABCDAB", но потом 'D' ≠ 'C'
  - Робот смотрит в таблицу подсказок:
    "Я уже знаю, что совпало 'ABCDAB'.
     Внутри есть 'AB' в начале И в конце!
     Значит, могу продолжить с позиции 2 ('AB'),
     не сравнивая эти буквы заново!"
```

**Таблица подсказок (prefix function)** — это предвычисленная информация о структуре паттерна.

### Аналогия 3: Z-функция как самоподобие

Z-функция для строки показывает, насколько каждая позиция "похожа на начало":

```
Строка: a a b a a b c
        ↑
        Начало

Z[0] = не определена (вся строка)
Z[1] = 1  (начинается с 'a', как и строка, но 'ab' ≠ 'aa')
Z[2] = 0  (начинается с 'b' ≠ 'a')
Z[3] = 4  (начинается с 'aaba', как и строка!)
Z[4] = 1  (начинается с 'a')
Z[5] = 0  (начинается с 'b')
Z[6] = 0  (начинается с 'c')

Визуализация совпадений с началом:
Позиция 3: a a b a a b c
                     ↓↓↓↓ совпадает с началом
           a a b a
```

### Аналогия 4: Aho-Corasick как GPS-навигатор

Представь, что ты ищешь несколько слов в тексте одновременно:

```
Слова для поиска: "he", "she", "his", "hers"
Текст: "ushers"

Наивный подход:
  Пройди текст 4 раза (для каждого слова)
  → O(n × k) где k — количество слов

Aho-Corasick (автомат):
  Построй "GPS-навигатор" из всех слов:

       root
      / | \
     h  s  ...
    /|   \
   e i    h
   |       \
   r        e
   |        |
   s        r

  "Failure links" — если заехал в тупик,
  куда перепрыгнуть, чтобы не начинать сначала.

  Проходим текст ОДИН раз, находим ВСЕ слова!
  → O(n + m + z) где z — число совпадений
```

### Аналогия 5: Suffix Array как словарь

Suffix Array — это "словарь" всех суффиксов строки:

```
Строка: "banana$"

Все суффиксы:         После сортировки:
0: banana$            6: $
1: anana$             5: a$
2: nana$              3: ana$
3: ana$               1: anana$
4: na$                0: banana$
5: a$                 4: na$
6: $                  2: nana$

Suffix Array: [6, 5, 3, 1, 0, 4, 2]

Теперь бинарный поиск по подстрокам работает за O(m log n)!
Ищем "ana": находим диапазон [2, 3] в sorted suffixes.
```

### Аналогия 6: Manacher как зеркало

Manacher использует свойство симметрии палиндромов:

```
Строка: a b a c a b a
              ↑
        Центр большого палиндрома (вся строка)

Если мы знаем, что "abacaba" — палиндром с центром в 'c':
- Левая часть = зеркальное отражение правой
- Палиндром с центром в 'a' (позиция 1) = палиндром с центром в 'a' (позиция 5)!

Не надо проверять заново — используем симметрию!
```

---

## Часть 2: Prefix Function (основа KMP)

### Что такое Prefix Function?

**Prefix Function π[i]** — длина наибольшего собственного префикса строки s[0..i], который также является суффиксом.

```
"Собственный" = не равен всей строке

s = "abcabc"

π[0] = 0  (для первого символа всегда 0)
π[1] = 0  "ab": нет общего prefix/suffix
π[2] = 0  "abc": нет общего prefix/suffix
π[3] = 1  "abca": "a" = prefix и suffix
π[4] = 2  "abcab": "ab" = prefix и suffix
π[5] = 3  "abcabc": "abc" = prefix и suffix

Результат: [0, 0, 0, 1, 2, 3]
```

### Визуализация

```
s = "aabaaab"

Позиция:  0 1 2 3 4 5 6
Строка:   a a b a a a b
π:        0 1 0 1 2 2 3

Объяснение π[5] = 2:
Подстрока: "aabaa|a"
                   ↑ позиция 5
Prefix "aa" = Suffix "aa" ✓
Длина = 2
```

### Ключевое свойство: π[i+1] ≤ π[i] + 1

```
Почему?

Если π[i] = k, то s[0..k-1] = s[i-k+1..i]

Для π[i+1]:
- Максимум можно "продлить" совпадение на 1 символ
- Если s[k] = s[i+1], то π[i+1] = k + 1
- Если s[k] ≠ s[i+1], надо искать более короткий prefix

Это даёт амортизированную сложность O(n)!
```

### Реализация Kotlin

```kotlin
/**
 * Prefix Function (failure function)
 * Time: O(n), Space: O(n)
 */
fun prefixFunction(s: String): IntArray {
    val n = s.length
    val pi = IntArray(n)

    for (i in 1 until n) {
        var j = pi[i - 1]

        // Ищем более короткий prefix, пока не найдём совпадение
        while (j > 0 && s[i] != s[j]) {
            j = pi[j - 1]
        }

        // Если символы совпали — увеличиваем длину
        if (s[i] == s[j]) {
            j++
        }

        pi[i] = j
    }

    return pi
}

// Пример
fun main() {
    val pi = prefixFunction("abcabc")
    println(pi.toList())  // [0, 0, 0, 1, 2, 3]
}
```

### Реализация Python

```python
def prefix_function(s: str) -> list[int]:
    """
    Prefix Function (failure function)
    Time: O(n), Space: O(n)
    """
    n = len(s)
    pi = [0] * n

    for i in range(1, n):
        j = pi[i - 1]

        # Find shorter prefix that matches suffix
        while j > 0 and s[i] != s[j]:
            j = pi[j - 1]

        # If characters match, extend the prefix
        if s[i] == s[j]:
            j += 1

        pi[i] = j

    return pi


# Example
if __name__ == "__main__":
    print(prefix_function("abcabc"))  # [0, 0, 0, 1, 2, 3]
```

---

## Часть 3: KMP Algorithm

### Идея алгоритма

KMP (Knuth-Morris-Pratt) использует prefix function для умного сдвига при несовпадении:

```
Текст:     a b a b c a b c a b a b a b d
Паттерн:   a b a b d
           ↑ ↑ ↑ ↑ ✗ (несовпадение на 'd' vs 'c')

Наивно: сдвинуть паттерн на 1 позицию вправо

KMP: π[3] = 2, значит "ab" в начале паттерна = "ab" в конце совпавшей части
     Можем сдвинуть паттерн так, чтобы этот "ab" совпал!

Текст:     a b a b c a b c a b a b a b d
Паттерн:       a b a b d
               ↑ ↑ (уже знаем, что совпадает!)
```

### Реализация через конкатенацию

Элегантный способ — объединить паттерн и текст через разделитель:

```
pattern = "aba"
text = "abacaba"
combined = "aba#abacaba"

Вычисляем prefix function для combined:
Позиция:  0 1 2 3 4 5 6 7 8 9 10
Строка:   a b a # a b a c a b a
π:        0 0 1 0 1 2 3 0 1 2 3
                      ↑     ↑
                  Совпадения (π = len(pattern))
```

### Реализация Kotlin

```kotlin
/**
 * KMP Pattern Matching
 * Time: O(n + m), Space: O(m)
 */
fun kmpSearch(text: String, pattern: String): List<Int> {
    if (pattern.isEmpty()) return emptyList()

    val combined = "$pattern#$text"
    val pi = prefixFunction(combined)
    val result = mutableListOf<Int>()
    val m = pattern.length

    for (i in (m + 1) until combined.length) {
        if (pi[i] == m) {
            // Найдено совпадение на позиции i - 2*m в исходном тексте
            result.add(i - 2 * m)
        }
    }

    return result
}

/**
 * KMP с явным автоматом (более эффективно по памяти)
 */
fun kmpSearchOptimized(text: String, pattern: String): List<Int> {
    if (pattern.isEmpty()) return emptyList()

    val pi = prefixFunction(pattern)
    val result = mutableListOf<Int>()
    var j = 0  // Текущая позиция в паттерне

    for (i in text.indices) {
        // Ищем подходящую позицию в паттерне
        while (j > 0 && text[i] != pattern[j]) {
            j = pi[j - 1]
        }

        if (text[i] == pattern[j]) {
            j++
        }

        if (j == pattern.length) {
            result.add(i - j + 1)
            j = pi[j - 1]  // Продолжаем поиск
        }
    }

    return result
}

// Пример
fun main() {
    val matches = kmpSearch("abacabacaba", "aba")
    println(matches)  // [0, 4, 8]
}
```

### Реализация Python

```python
def kmp_search(text: str, pattern: str) -> list[int]:
    """
    KMP Pattern Matching using concatenation
    Time: O(n + m), Space: O(n + m)
    """
    if not pattern:
        return []

    combined = pattern + "#" + text
    pi = prefix_function(combined)
    m = len(pattern)

    result = []
    for i in range(m + 1, len(combined)):
        if pi[i] == m:
            result.append(i - 2 * m)

    return result


def kmp_search_optimized(text: str, pattern: str) -> list[int]:
    """
    KMP with explicit automaton (memory efficient)
    Time: O(n + m), Space: O(m)
    """
    if not pattern:
        return []

    pi = prefix_function(pattern)
    result = []
    j = 0  # Current position in pattern

    for i in range(len(text)):
        # Find appropriate position in pattern
        while j > 0 and text[i] != pattern[j]:
            j = pi[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == len(pattern):
            result.append(i - j + 1)
            j = pi[j - 1]  # Continue searching

    return result


# Example
if __name__ == "__main__":
    print(kmp_search("abacabacaba", "aba"))  # [0, 4, 8]
```

---

## Часть 4: Z-Function

### Что такое Z-функция?

**Z[i]** — длина наибольшего общего префикса строки s и её суффикса, начинающегося с позиции i.

```
s = "aabxaab"

Z[0] = undefined (или 0, или len(s))
Z[1] = 1    "abxaab" имеет общий prefix "a" со строкой
Z[2] = 0    "bxaab" не начинается с 'a'
Z[3] = 0    "xaab" не начинается с 'a'
Z[4] = 3    "aab" = prefix "aab" ✓
Z[5] = 1    "ab" имеет общий prefix "a"
Z[6] = 0    "b" не начинается с 'a'

Результат: [-, 1, 0, 0, 3, 1, 0]
```

### Z-Box оптимизация

```
Ключевая идея: поддерживаем "Z-box" [l, r] —
самый правый отрезок, совпадающий с префиксом.

Если i находится внутри [l, r]:
- Мы знаем, что s[l..r] = s[0..r-l]
- Значит s[i..r] = s[i-l..r-l]
- Можем использовать уже вычисленное Z[i-l]!

     l         i         r
     ↓         ↓         ↓
s:   [=========|=========]
     ↑                   ↑
     Этот отрезок = начало строки

Если Z[i-l] < r - i + 1:
    Z[i] = Z[i-l]  (полностью помещается в box)
Иначе:
    Начинаем с r - i + 1 и расширяем
```

### Реализация Kotlin

```kotlin
/**
 * Z-Function
 * Time: O(n), Space: O(n)
 */
fun zFunction(s: String): IntArray {
    val n = s.length
    val z = IntArray(n)
    var l = 0
    var r = 0

    for (i in 1 until n) {
        if (i < r) {
            // Внутри Z-box: используем уже вычисленное значение
            z[i] = minOf(r - i, z[i - l])
        }

        // Расширяем Z[i] сравнением символов
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++
        }

        // Обновляем Z-box если вышли за границу
        if (i + z[i] > r) {
            l = i
            r = i + z[i]
        }
    }

    return z
}

/**
 * Pattern matching using Z-function
 */
fun zSearch(text: String, pattern: String): List<Int> {
    val combined = "$pattern#$text"
    val z = zFunction(combined)
    val m = pattern.length

    return z.indices
        .filter { i -> i > m && z[i] == m }
        .map { i -> i - m - 1 }
}

// Пример
fun main() {
    println(zFunction("aabxaab").toList())  // [0, 1, 0, 0, 3, 1, 0]
    println(zSearch("abacabacaba", "aba"))  // [0, 4, 8]
}
```

### Реализация Python

```python
def z_function(s: str) -> list[int]:
    """
    Z-Function
    Time: O(n), Space: O(n)
    """
    n = len(s)
    z = [0] * n
    l, r = 0, 0

    for i in range(1, n):
        if i < r:
            # Inside Z-box: use already computed value
            z[i] = min(r - i, z[i - l])

        # Extend Z[i] by comparing characters
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1

        # Update Z-box if extended beyond
        if i + z[i] > r:
            l = i
            r = i + z[i]

    return z


def z_search(text: str, pattern: str) -> list[int]:
    """Pattern matching using Z-function"""
    combined = pattern + "#" + text
    z = z_function(combined)
    m = len(pattern)

    return [i - m - 1 for i in range(m + 1, len(z)) if z[i] == m]


# Example
if __name__ == "__main__":
    print(z_function("aabxaab"))  # [0, 1, 0, 0, 3, 1, 0]
    print(z_search("abacabacaba", "aba"))  # [0, 4, 8]
```

### KMP vs Z-function

| Аспект | KMP (Prefix Function) | Z-Function |
|--------|----------------------|------------|
| Определение | Длина prefix = suffix | Длина совпадения с началом |
| Направление | "Смотрит назад" | "Смотрит вперёд" |
| Применение | Pattern matching, автоматы | Pattern matching, сжатие строк |
| Код | Немного сложнее | Проще для понимания |
| Связь | π можно получить из Z и наоборот | |

---

## Часть 5: Rabin-Karp (Rolling Hash)

### Идея алгоритма

Вместо посимвольного сравнения используем **хеш-функцию**:

```
Паттерн: "abc"  → hash("abc") = 12345
Текст:   "xabcd"

Скользящее окно:
  "xab" → hash = 98765 ≠ 12345 (пропускаем)
  "abc" → hash = 12345 = 12345 (проверяем детально!)
  "bcd" → hash = 54321 ≠ 12345 (пропускаем)
```

### Polynomial Hash

```
hash(s) = s[0] * p^(n-1) + s[1] * p^(n-2) + ... + s[n-1] * p^0  (mod M)

где p — простое число (обычно 31 или 37)
    M — большое простое число (обычно 10^9 + 7)

Пример: s = "abc", p = 31, M = 10^9 + 7
hash = 'a' * 31^2 + 'b' * 31^1 + 'c' * 31^0
     = 97 * 961 + 98 * 31 + 99 * 1
     = 93217 + 3038 + 99
     = 96354
```

### Rolling Hash: O(1) обновление

```
Окно сдвигается вправо:
  Убираем первый символ, добавляем новый

hash("abc") → hash("bcd")

Старый: 'a'*p^2 + 'b'*p + 'c'
Новый:  'b'*p^2 + 'c'*p + 'd'

Формула обновления:
new_hash = (old_hash - old_char * p^(m-1)) * p + new_char

Одна операция вместо m!
```

### Проблема коллизий (Birthday Paradox)

```
Вероятность коллизии (два разных текста с одинаковым хешем):

Для M = 10^9 и n = 10^5 строк:
P(collision) ≈ n^2 / (2 * M) ≈ 0.5%

Решения:
1. Двойное хеширование (два разных p и M)
2. При совпадении хеша — проверка посимвольно
3. Рандомизация p в runtime
```

### Реализация Kotlin

```kotlin
/**
 * Rabin-Karp Pattern Matching with Rolling Hash
 * Time: O(n + m) average, O(nm) worst case
 * Space: O(1)
 */
class RabinKarp(
    private val base: Long = 31L,
    private val mod: Long = 1_000_000_007L
) {

    fun search(text: String, pattern: String): List<Int> {
        if (pattern.isEmpty() || pattern.length > text.length) {
            return emptyList()
        }

        val m = pattern.length
        val result = mutableListOf<Int>()

        // Вычисляем p^(m-1) для удаления первого символа
        var pPow = 1L
        repeat(m - 1) { pPow = pPow * base % mod }

        // Хеш паттерна
        var patternHash = 0L
        for (c in pattern) {
            patternHash = (patternHash * base + (c - 'a' + 1)) % mod
        }

        // Хеш первого окна
        var windowHash = 0L
        for (i in 0 until m) {
            windowHash = (windowHash * base + (text[i] - 'a' + 1)) % mod
        }

        // Проверяем первое окно
        if (windowHash == patternHash && text.substring(0, m) == pattern) {
            result.add(0)
        }

        // Скользящее окно
        for (i in m until text.length) {
            // Удаляем первый символ окна
            val oldChar = text[i - m] - 'a' + 1
            windowHash = (windowHash - oldChar * pPow % mod + mod) % mod

            // Сдвигаем и добавляем новый символ
            val newChar = text[i] - 'a' + 1
            windowHash = (windowHash * base + newChar) % mod

            // Проверяем совпадение
            if (windowHash == patternHash) {
                val start = i - m + 1
                if (text.substring(start, start + m) == pattern) {
                    result.add(start)
                }
            }
        }

        return result
    }

    /**
     * Множественный поиск с предвычислением prefix хешей
     */
    fun prefixHashes(s: String): Pair<LongArray, LongArray> {
        val n = s.length
        val h = LongArray(n + 1)    // prefix hashes
        val p = LongArray(n + 1)     // powers of base

        p[0] = 1
        for (i in 0 until n) {
            h[i + 1] = (h[i] * base + (s[i] - 'a' + 1)) % mod
            p[i + 1] = p[i] * base % mod
        }

        return h to p
    }

    /**
     * Хеш подстроки s[l..r] за O(1)
     */
    fun substringHash(
        prefixHash: LongArray,
        powers: LongArray,
        l: Int,
        r: Int
    ): Long {
        val hash = (prefixHash[r + 1] - prefixHash[l] * powers[r - l + 1] % mod + mod) % mod
        return hash
    }
}

// Пример
fun main() {
    val rk = RabinKarp()
    println(rk.search("abacabacaba", "aba"))  // [0, 4, 8]
}
```

### Реализация Python

```python
class RabinKarp:
    """
    Rabin-Karp Pattern Matching with Rolling Hash
    Time: O(n + m) average, O(nm) worst case
    Space: O(1)
    """

    def __init__(self, base: int = 31, mod: int = 10**9 + 7):
        self.base = base
        self.mod = mod

    def search(self, text: str, pattern: str) -> list[int]:
        if not pattern or len(pattern) > len(text):
            return []

        m = len(pattern)
        result = []

        # Compute p^(m-1) for removing first character
        p_pow = pow(self.base, m - 1, self.mod)

        # Pattern hash
        pattern_hash = 0
        for c in pattern:
            pattern_hash = (pattern_hash * self.base + ord(c) - ord('a') + 1) % self.mod

        # First window hash
        window_hash = 0
        for i in range(m):
            window_hash = (window_hash * self.base + ord(text[i]) - ord('a') + 1) % self.mod

        # Check first window
        if window_hash == pattern_hash and text[:m] == pattern:
            result.append(0)

        # Sliding window
        for i in range(m, len(text)):
            # Remove first character of window
            old_char = ord(text[i - m]) - ord('a') + 1
            window_hash = (window_hash - old_char * p_pow) % self.mod

            # Shift and add new character
            new_char = ord(text[i]) - ord('a') + 1
            window_hash = (window_hash * self.base + new_char) % self.mod

            # Check match
            if window_hash == pattern_hash:
                start = i - m + 1
                if text[start:start + m] == pattern:
                    result.append(start)

        return result

    def prefix_hashes(self, s: str) -> tuple[list[int], list[int]]:
        """Precompute prefix hashes for O(1) substring hash queries"""
        n = len(s)
        h = [0] * (n + 1)  # prefix hashes
        p = [1] * (n + 1)  # powers of base

        for i in range(n):
            h[i + 1] = (h[i] * self.base + ord(s[i]) - ord('a') + 1) % self.mod
            p[i + 1] = p[i] * self.base % self.mod

        return h, p

    def substring_hash(
        self,
        prefix_hash: list[int],
        powers: list[int],
        l: int,
        r: int
    ) -> int:
        """Hash of substring s[l..r] in O(1)"""
        return (prefix_hash[r + 1] - prefix_hash[l] * powers[r - l + 1]) % self.mod


# Example
if __name__ == "__main__":
    rk = RabinKarp()
    print(rk.search("abacabacaba", "aba"))  # [0, 4, 8]
```

---

## Часть 6: Aho-Corasick Algorithm

### Проблема

Найти все вхождения множества паттернов {p1, p2, ..., pk} в тексте T.

```
Паттерны: ["he", "she", "his", "hers"]
Текст: "ushers"

Ответ:
  - "she" на позиции 1
  - "he" на позиции 2
  - "hers" на позиции 2
```

### Идея алгоритма

1. **Построить Trie** из всех паттернов
2. **Добавить Failure Links** (suffix links) — как в KMP, но для дерева
3. **Пройти текст один раз**, переходя по автомату

```
Trie для ["he", "she", "his", "hers"]:

         root
        / | \
       h  s  ...
      /|   \
     e i    h
     |       \
     r        e
     |
     s

Failure links (показаны ---→):

         root ←─────────┐
        / | \           │
       h  s  ...        │
      /|   \            │
     e i    h ─────→ h  │
     ↓       \      ↓   │
     r        e ──→ e   │
     ↓                  │
     s ────────────────→┘
```

### Реализация Kotlin

```kotlin
/**
 * Aho-Corasick Algorithm
 * Time: O(n + m + z) where z is number of matches
 * Space: O(m * alphabet_size)
 */
class AhoCorasick {
    private data class Node(
        val children: MutableMap<Char, Int> = mutableMapOf(),
        var fail: Int = 0,
        var output: MutableList<Int> = mutableListOf()  // Индексы паттернов
    )

    private val nodes = mutableListOf(Node())
    private val patterns = mutableListOf<String>()

    /**
     * Добавить паттерн в Trie
     */
    fun addPattern(pattern: String) {
        var curr = 0
        for (c in pattern) {
            if (c !in nodes[curr].children) {
                nodes[curr].children[c] = nodes.size
                nodes.add(Node())
            }
            curr = nodes[curr].children[c]!!
        }
        nodes[curr].output.add(patterns.size)
        patterns.add(pattern)
    }

    /**
     * Построить failure links (BFS)
     */
    fun build() {
        val queue = ArrayDeque<Int>()

        // Первый уровень: все дети root имеют fail = 0
        for ((_, child) in nodes[0].children) {
            queue.add(child)
        }

        while (queue.isNotEmpty()) {
            val curr = queue.removeFirst()

            for ((c, child) in nodes[curr].children) {
                queue.add(child)

                // Ищем failure link
                var fail = nodes[curr].fail
                while (fail != 0 && c !in nodes[fail].children) {
                    fail = nodes[fail].fail
                }

                nodes[child].fail = nodes[fail].children[c] ?: 0

                // Копируем output из failure link (suffix matches)
                nodes[child].output.addAll(nodes[nodes[child].fail].output)
            }
        }
    }

    /**
     * Поиск всех паттернов в тексте
     * Returns: List of (position, pattern_index)
     */
    fun search(text: String): List<Pair<Int, String>> {
        val result = mutableListOf<Pair<Int, String>>()
        var curr = 0

        for (i in text.indices) {
            val c = text[i]

            // Переходим по failure links пока не найдём переход
            while (curr != 0 && c !in nodes[curr].children) {
                curr = nodes[curr].fail
            }

            curr = nodes[curr].children[c] ?: 0

            // Собираем все совпадения
            for (patternIdx in nodes[curr].output) {
                val pattern = patterns[patternIdx]
                result.add(i - pattern.length + 1 to pattern)
            }
        }

        return result
    }
}

// Пример
fun main() {
    val ac = AhoCorasick()
    ac.addPattern("he")
    ac.addPattern("she")
    ac.addPattern("his")
    ac.addPattern("hers")
    ac.build()

    val matches = ac.search("ushers")
    for ((pos, pattern) in matches) {
        println("'$pattern' at position $pos")
    }
    // 'she' at position 1
    // 'he' at position 2
    // 'hers' at position 2
}
```

### Реализация Python

```python
from collections import deque
from typing import List, Tuple


class AhoCorasick:
    """
    Aho-Corasick Algorithm
    Time: O(n + m + z) where z is number of matches
    Space: O(m * alphabet_size)
    """

    def __init__(self):
        self.nodes = [{"children": {}, "fail": 0, "output": []}]
        self.patterns = []

    def add_pattern(self, pattern: str) -> None:
        """Add pattern to Trie"""
        curr = 0
        for c in pattern:
            if c not in self.nodes[curr]["children"]:
                self.nodes[curr]["children"][c] = len(self.nodes)
                self.nodes.append({"children": {}, "fail": 0, "output": []})
            curr = self.nodes[curr]["children"][c]

        self.nodes[curr]["output"].append(len(self.patterns))
        self.patterns.append(pattern)

    def build(self) -> None:
        """Build failure links using BFS"""
        queue = deque()

        # First level: all children of root have fail = 0
        for child in self.nodes[0]["children"].values():
            queue.append(child)

        while queue:
            curr = queue.popleft()

            for c, child in self.nodes[curr]["children"].items():
                queue.append(child)

                # Find failure link
                fail = self.nodes[curr]["fail"]
                while fail != 0 and c not in self.nodes[fail]["children"]:
                    fail = self.nodes[fail]["fail"]

                self.nodes[child]["fail"] = self.nodes[fail]["children"].get(c, 0)

                # Copy output from failure link (suffix matches)
                self.nodes[child]["output"].extend(
                    self.nodes[self.nodes[child]["fail"]]["output"]
                )

    def search(self, text: str) -> List[Tuple[int, str]]:
        """
        Search for all patterns in text
        Returns: List of (position, pattern)
        """
        result = []
        curr = 0

        for i, c in enumerate(text):
            # Follow failure links until we find a transition
            while curr != 0 and c not in self.nodes[curr]["children"]:
                curr = self.nodes[curr]["fail"]

            curr = self.nodes[curr]["children"].get(c, 0)

            # Collect all matches
            for pattern_idx in self.nodes[curr]["output"]:
                pattern = self.patterns[pattern_idx]
                result.append((i - len(pattern) + 1, pattern))

        return result


# Example
if __name__ == "__main__":
    ac = AhoCorasick()
    ac.add_pattern("he")
    ac.add_pattern("she")
    ac.add_pattern("his")
    ac.add_pattern("hers")
    ac.build()

    matches = ac.search("ushers")
    for pos, pattern in matches:
        print(f"'{pattern}' at position {pos}")
    # 'she' at position 1
    # 'he' at position 2
    # 'hers' at position 2
```

---

## Часть 7: Suffix Array

### Что такое Suffix Array?

**Suffix Array** — отсортированный массив всех суффиксов строки, представленный их начальными индексами.

```
s = "banana$"  ($ — sentinel, меньше всех букв)

Суффиксы:
0: banana$
1: anana$
2: nana$
3: ana$
4: na$
5: a$
6: $

Отсортированные:
6: $         (позиция 0 в sorted)
5: a$        (позиция 1)
3: ana$      (позиция 2)
1: anana$    (позиция 3)
0: banana$   (позиция 4)
4: na$       (позиция 5)
2: nana$     (позиция 6)

Suffix Array: SA = [6, 5, 3, 1, 0, 4, 2]
```

### Алгоритмы построения

| Алгоритм | Сложность | Описание |
|----------|-----------|----------|
| Наивная сортировка | O(n² log n) | Сортируем суффиксы напрямую |
| Prefix Doubling | O(n log² n) | Manber-Myers, doubling |
| DC3 / Skew | O(n) | Kärkkäinen-Sanders |
| SA-IS | O(n) | Induced Sorting |

### Prefix Doubling (O(n log² n))

```
Идея: сортируем суффиксы по первым 2^k символам на каждой итерации.

Шаг k=0: сортируем по первому символу
Шаг k=1: сортируем по первым 2 символам
Шаг k=2: сортируем по первым 4 символам
...
До k = ⌈log₂ n⌉

На каждом шаге используем результат предыдущего:
  Ключ сортировки для суффикса i = (rank[i], rank[i + 2^(k-1)])
  → две "половинки" уже отсортированы!
```

### Реализация Kotlin

```kotlin
/**
 * Suffix Array Construction (Prefix Doubling)
 * Time: O(n log² n) with simple sort, O(n log n) with radix sort
 * Space: O(n)
 */
fun buildSuffixArray(s: String): IntArray {
    val n = s.length
    val sa = IntArray(n) { it }
    var rank = IntArray(n) { s[it].code }
    var tmp = IntArray(n)

    var k = 1
    while (k < n) {
        // Сравнение суффиксов по паре (rank[i], rank[i + k])
        val comparator = Comparator<Int> { i, j ->
            if (rank[i] != rank[j]) {
                rank[i] - rank[j]
            } else {
                val ri = if (i + k < n) rank[i + k] else -1
                val rj = if (j + k < n) rank[j + k] else -1
                ri - rj
            }
        }

        // Сортируем суффиксы
        val sortedSa = sa.sortedWith(comparator)
        for (i in 0 until n) sa[i] = sortedSa[i]

        // Обновляем ранги
        tmp[sa[0]] = 0
        for (i in 1 until n) {
            tmp[sa[i]] = tmp[sa[i - 1]]
            if (comparator.compare(sa[i - 1], sa[i]) < 0) {
                tmp[sa[i]]++
            }
        }
        rank = tmp.also { tmp = rank }

        // Ранняя остановка если все ранги уникальны
        if (rank[sa[n - 1]] == n - 1) break

        k *= 2
    }

    return sa
}

/**
 * Бинарный поиск паттерна в тексте через Suffix Array
 * Time: O(m log n) where m is pattern length
 */
fun searchWithSuffixArray(text: String, sa: IntArray, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    var lo = 0
    var hi = n - 1

    while (lo <= hi) {
        val mid = (lo + hi) / 2
        val suffix = text.substring(sa[mid], minOf(sa[mid] + m, n))

        when {
            suffix < pattern -> lo = mid + 1
            suffix > pattern -> hi = mid - 1
            else -> return sa[mid]  // Найдено
        }
    }

    return -1  // Не найдено
}

// Пример
fun main() {
    val text = "banana"
    val sa = buildSuffixArray(text)
    println("SA: ${sa.toList()}")  // [5, 3, 1, 0, 4, 2]

    println(searchWithSuffixArray(text, sa, "ana"))  // 1 или 3
    println(searchWithSuffixArray(text, sa, "nan"))  // 2
}
```

### Реализация Python

```python
def build_suffix_array(s: str) -> list[int]:
    """
    Suffix Array Construction (Prefix Doubling)
    Time: O(n log² n), Space: O(n)
    """
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]

    k = 1
    while k < n:
        # Compare suffixes by pair (rank[i], rank[i + k])
        def compare_key(i: int) -> tuple[int, int]:
            return (rank[i], rank[i + k] if i + k < n else -1)

        sa.sort(key=compare_key)

        # Update ranks
        tmp = [0] * n
        for i in range(1, n):
            tmp[sa[i]] = tmp[sa[i - 1]]
            if compare_key(sa[i - 1]) < compare_key(sa[i]):
                tmp[sa[i]] += 1
        rank = tmp

        # Early termination if all ranks are unique
        if rank[sa[n - 1]] == n - 1:
            break

        k *= 2

    return sa


def search_with_suffix_array(text: str, sa: list[int], pattern: str) -> int:
    """
    Binary search for pattern using Suffix Array
    Time: O(m log n)
    """
    n = len(text)
    m = len(pattern)

    lo, hi = 0, n - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        suffix = text[sa[mid]:sa[mid] + m]

        if suffix < pattern:
            lo = mid + 1
        elif suffix > pattern:
            hi = mid - 1
        else:
            return sa[mid]  # Found

    return -1  # Not found


# Example
if __name__ == "__main__":
    text = "banana"
    sa = build_suffix_array(text)
    print(f"SA: {sa}")  # [5, 3, 1, 0, 4, 2]

    print(search_with_suffix_array(text, sa, "ana"))  # 1 or 3
    print(search_with_suffix_array(text, sa, "nan"))  # 2
```

---

## Часть 8: LCP Array (Kasai's Algorithm)

### Что такое LCP Array?

**LCP Array** — массив длин наибольших общих префиксов между соседними суффиксами в отсортированном порядке (Suffix Array).

```
s = "banana"
SA = [5, 3, 1, 0, 4, 2]

Отсортированные суффиксы:
SA[0] = 5: a
SA[1] = 3: ana
SA[2] = 1: anana
SA[3] = 0: banana
SA[4] = 4: na
SA[5] = 2: nana

LCP[i] = LCP(SA[i-1], SA[i]):
LCP[0] = undefined (или 0)
LCP[1] = LCP("a", "ana") = 1
LCP[2] = LCP("ana", "anana") = 3
LCP[3] = LCP("anana", "banana") = 0
LCP[4] = LCP("banana", "na") = 0
LCP[5] = LCP("na", "nana") = 2

LCP Array: [-, 1, 3, 0, 0, 2]
```

### Kasai's Algorithm (O(n))

```
Ключевое наблюдение:
Если LCP(SA[rank[i]-1], SA[rank[i]]) = h,
то LCP(SA[rank[i+1]-1], SA[rank[i+1]]) ≥ h - 1

Почему?
- Убираем первый символ от обоих суффиксов
- Относительный порядок сохраняется (почти)
- Общий префикс уменьшается максимум на 1

Итого: h может уменьшиться n раз и увеличиться n раз
→ O(n) амортизированно
```

### Реализация Kotlin

```kotlin
/**
 * Kasai's Algorithm for LCP Array
 * Time: O(n), Space: O(n)
 */
fun buildLcpArray(s: String, sa: IntArray): IntArray {
    val n = s.length
    val rank = IntArray(n)
    val lcp = IntArray(n)

    // Обратный массив: rank[i] = позиция суффикса i в SA
    for (i in 0 until n) {
        rank[sa[i]] = i
    }

    var h = 0
    for (i in 0 until n) {
        if (rank[i] > 0) {
            val j = sa[rank[i] - 1]  // Предыдущий суффикс в SA

            // Расширяем LCP
            while (i + h < n && j + h < n && s[i + h] == s[j + h]) {
                h++
            }

            lcp[rank[i]] = h

            // h может уменьшиться максимум на 1
            if (h > 0) h--
        }
    }

    return lcp
}

/**
 * Поиск самой длинной повторяющейся подстроки
 */
fun longestRepeatedSubstring(s: String): String {
    val sa = buildSuffixArray(s)
    val lcp = buildLcpArray(s, sa)

    val maxLcpIdx = lcp.indices.maxByOrNull { lcp[it] } ?: return ""
    val maxLcp = lcp[maxLcpIdx]

    return if (maxLcp > 0) {
        s.substring(sa[maxLcpIdx], sa[maxLcpIdx] + maxLcp)
    } else ""
}

// Пример
fun main() {
    val s = "banana"
    val sa = buildSuffixArray(s)
    val lcp = buildLcpArray(s, sa)

    println("SA:  ${sa.toList()}")   // [5, 3, 1, 0, 4, 2]
    println("LCP: ${lcp.toList()}")  // [0, 1, 3, 0, 0, 2]
    println("Longest repeated: ${longestRepeatedSubstring(s)}")  // "ana"
}
```

### Реализация Python

```python
def build_lcp_array(s: str, sa: list[int]) -> list[int]:
    """
    Kasai's Algorithm for LCP Array
    Time: O(n), Space: O(n)
    """
    n = len(s)
    rank = [0] * n
    lcp = [0] * n

    # Inverse array: rank[i] = position of suffix i in SA
    for i in range(n):
        rank[sa[i]] = i

    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]  # Previous suffix in SA

            # Extend LCP
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1

            lcp[rank[i]] = h

            # h can decrease by at most 1
            if h > 0:
                h -= 1

    return lcp


def longest_repeated_substring(s: str) -> str:
    """Find the longest repeated substring"""
    sa = build_suffix_array(s)
    lcp = build_lcp_array(s, sa)

    max_lcp_idx = max(range(len(lcp)), key=lambda i: lcp[i])
    max_lcp = lcp[max_lcp_idx]

    return s[sa[max_lcp_idx]:sa[max_lcp_idx] + max_lcp] if max_lcp > 0 else ""


# Example
if __name__ == "__main__":
    s = "banana"
    sa = build_suffix_array(s)
    lcp = build_lcp_array(s, sa)

    print(f"SA:  {sa}")   # [5, 3, 1, 0, 4, 2]
    print(f"LCP: {lcp}")  # [0, 1, 3, 0, 0, 2]
    print(f"Longest repeated: {longest_repeated_substring(s)}")  # "ana"
```

---

## Часть 9: Manacher's Algorithm

### Проблема

Найти все палиндромные подстроки или самый длинный палиндром за O(n).

### Идея алгоритма

```
1. Преобразуем строку, вставляя разделители:
   "abba" → "#a#b#b#a#"

   Теперь все палиндромы имеют нечётную длину!

2. Вычисляем d[i] — радиус палиндрома с центром в i.

3. Используем симметрию:
   Если мы внутри уже найденного палиндрома,
   используем зеркальное значение!

     l     mirror    c     i       r
     |       |       |     |       |
     [=======|=======|=====|=======]
             ↑       ↑     ↑
     d[mirror] уже известно!
     d[i] ≥ min(d[mirror], r - i)
```

### Реализация Kotlin

```kotlin
/**
 * Manacher's Algorithm
 * Time: O(n), Space: O(n)
 * Returns: array of palindrome radii for transformed string
 */
fun manacher(s: String): IntArray {
    // Преобразуем: "abc" → "#a#b#c#"
    val t = StringBuilder("#")
    for (c in s) {
        t.append(c).append('#')
    }
    val transformed = t.toString()
    val n = transformed.length

    val d = IntArray(n)  // d[i] = радиус палиндрома
    var c = 0  // Центр текущего "самого правого" палиндрома
    var r = 0  // Правая граница

    for (i in 0 until n) {
        if (i < r) {
            // Используем симметрию
            val mirror = 2 * c - i
            d[i] = minOf(r - i, d[mirror])
        }

        // Пробуем расширить
        while (i - d[i] - 1 >= 0 &&
               i + d[i] + 1 < n &&
               transformed[i - d[i] - 1] == transformed[i + d[i] + 1]) {
            d[i]++
        }

        // Обновляем границы если вышли за r
        if (i + d[i] > r) {
            c = i
            r = i + d[i]
        }
    }

    return d
}

/**
 * Найти самый длинный палиндром
 */
fun longestPalindrome(s: String): String {
    if (s.isEmpty()) return ""

    val d = manacher(s)
    var maxRadius = 0
    var centerIdx = 0

    for (i in d.indices) {
        if (d[i] > maxRadius) {
            maxRadius = d[i]
            centerIdx = i
        }
    }

    // Преобразуем обратно в индексы исходной строки
    val start = (centerIdx - maxRadius) / 2
    val end = start + maxRadius

    return s.substring(start, end)
}

/**
 * Подсчитать все палиндромные подстроки
 */
fun countPalindromes(s: String): Long {
    val d = manacher(s)
    var count = 0L

    for (i in d.indices) {
        // Каждый радиус d[i] соответствует (d[i] + 1) / 2 палиндромам
        // (делим на 2 из-за вставленных #)
        count += (d[i] + 1) / 2
    }

    return count
}

// Пример
fun main() {
    println(longestPalindrome("babad"))  // "bab" или "aba"
    println(longestPalindrome("cbbd"))   // "bb"
    println(countPalindromes("aaa"))     // 6: "a"(3), "aa"(2), "aaa"(1)
}
```

### Реализация Python

```python
def manacher(s: str) -> list[int]:
    """
    Manacher's Algorithm
    Time: O(n), Space: O(n)
    Returns: array of palindrome radii for transformed string
    """
    # Transform: "abc" → "#a#b#c#"
    t = "#" + "#".join(s) + "#"
    n = len(t)

    d = [0] * n  # d[i] = palindrome radius
    c = 0  # Center of current "rightmost" palindrome
    r = 0  # Right boundary

    for i in range(n):
        if i < r:
            # Use symmetry
            mirror = 2 * c - i
            d[i] = min(r - i, d[mirror])

        # Try to expand
        while (i - d[i] - 1 >= 0 and
               i + d[i] + 1 < n and
               t[i - d[i] - 1] == t[i + d[i] + 1]):
            d[i] += 1

        # Update boundaries if extended beyond r
        if i + d[i] > r:
            c = i
            r = i + d[i]

    return d


def longest_palindrome(s: str) -> str:
    """Find the longest palindromic substring"""
    if not s:
        return ""

    d = manacher(s)
    max_radius = max(d)
    center_idx = d.index(max_radius)

    # Convert back to original string indices
    start = (center_idx - max_radius) // 2
    end = start + max_radius

    return s[start:end]


def count_palindromes(s: str) -> int:
    """Count all palindromic substrings"""
    d = manacher(s)
    # Each radius d[i] corresponds to (d[i] + 1) // 2 palindromes
    return sum((r + 1) // 2 for r in d)


# Example
if __name__ == "__main__":
    print(longest_palindrome("babad"))  # "bab" or "aba"
    print(longest_palindrome("cbbd"))   # "bb"
    print(count_palindromes("aaa"))     # 6: "a"(3), "aa"(2), "aaa"(1)
```

---

## Часть 10: Сравнение алгоритмов

### Таблица сложностей

| Алгоритм | Время построения | Время запроса | Память | Применение |
|----------|-----------------|---------------|--------|------------|
| **Naive** | - | O(nm) | O(1) | Простые случаи |
| **KMP** | O(m) | O(n) | O(m) | Один паттерн |
| **Z-function** | O(n+m) | O(n+m) | O(n+m) | Один паттерн |
| **Rabin-Karp** | O(m) | O(n) avg | O(1) | Множественный поиск |
| **Aho-Corasick** | O(Σm) | O(n + z) | O(Σm·|Σ|) | Много паттернов |
| **Suffix Array** | O(n log n) | O(m log n) | O(n) | Все подстроки |
| **Suffix Array + LCP** | O(n log n) | O(m + log n) | O(n) | Подстроки + LCP |
| **Manacher** | O(n) | - | O(n) | Палиндромы |

### Какой алгоритм выбрать?

```
┌─────────────────────────────────────────────────────────────────┐
│                    ДЕРЕВО РЕШЕНИЙ                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Сколько паттернов ищем?                                        │
│  ├─ Один паттерн                                                │
│  │  ├─ Простой случай, короткий текст → Naive                  │
│  │  ├─ Нужна гарантия O(n+m) → KMP или Z-function              │
│  │  └─ Множество поисков в одном тексте → Suffix Array         │
│  │                                                              │
│  ├─ Несколько паттернов (2-10)                                  │
│  │  ├─ Хотим простоту → Rabin-Karp                              │
│  │  └─ Хотим скорость → Aho-Corasick                           │
│  │                                                              │
│  └─ Много паттернов (>10)                                       │
│     └─ Обязательно Aho-Corasick                                │
│                                                                 │
│  Ищем палиндромы?                                               │
│  └─ Manacher (единственный O(n) алгоритм)                      │
│                                                                 │
│  Ищем все вхождения всех подстрок?                             │
│  └─ Suffix Array + LCP                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Часть 11: Типичные задачи

### Задача 1: Pattern Matching (LeetCode 28)

**Условие:** Найти первое вхождение needle в haystack.

```kotlin
// KMP решение
fun strStr(haystack: String, needle: String): Int {
    if (needle.isEmpty()) return 0

    val pi = prefixFunction(needle)
    var j = 0

    for (i in haystack.indices) {
        while (j > 0 && haystack[i] != needle[j]) {
            j = pi[j - 1]
        }
        if (haystack[i] == needle[j]) j++
        if (j == needle.length) return i - j + 1
    }

    return -1
}
```

### Задача 2: Longest Palindromic Substring (LeetCode 5)

**Условие:** Найти самую длинную палиндромную подстроку.

```kotlin
// Manacher решение — O(n)
fun longestPalindromeSubstring(s: String): String {
    return longestPalindrome(s)  // Используем Manacher
}
```

### Задача 3: Repeated Substring Pattern (LeetCode 459)

**Условие:** Проверить, можно ли составить строку из повторений подстроки.

```kotlin
// Z-function решение
fun repeatedSubstringPattern(s: String): Boolean {
    val n = s.length
    val z = zFunction(s)

    for (i in 1 until n) {
        // Если s можно разбить на (n/i) копий подстроки длины i
        if (n % i == 0 && i + z[i] == n) {
            return true
        }
    }

    return false
}
```

### Задача 4: Word Search II (LeetCode 212)

**Условие:** Найти все слова из словаря в сетке букв (Boggle).

```kotlin
// Aho-Corasick + DFS (или Trie + DFS для сетки)
// Aho-Corasick полезен когда ищем в длинном тексте
```

### Задача 5: Longest Duplicate Substring (LeetCode 1044)

**Условие:** Найти самую длинную повторяющуюся подстроку.

```kotlin
// Suffix Array + LCP решение — O(n log n)
fun longestDupSubstring(s: String): String {
    return longestRepeatedSubstring(s)
}

// Альтернатива: Binary Search + Rabin-Karp — O(n log n)
```

### Задача 6: Distinct Substrings (SPOJ DISUBSTR)

**Условие:** Подсчитать количество различных подстрок.

```kotlin
fun countDistinctSubstrings(s: String): Long {
    val n = s.length
    val sa = buildSuffixArray(s)
    val lcp = buildLcpArray(s, sa)

    // Всего подстрок: n*(n+1)/2
    // Вычитаем дубликаты (суммы LCP)
    val total = n.toLong() * (n + 1) / 2
    val duplicates = lcp.sum().toLong()

    return total - duplicates
}
```

---

## Часть 12: Мифы и заблуждения

### Миф 1: "KMP всегда лучше наивного поиска"

**Реальность:** Для коротких паттернов (<10 символов) и случайных текстов наивный поиск часто быстрее из-за:
- Cache locality
- Отсутствия overhead на построение prefix function
- Expected O(n) для случайных данных

### Миф 2: "Rabin-Karp ненадёжен из-за коллизий"

**Реальность:**
- С двойным хешированием вероятность ложного срабатывания: ~10^-18
- Всегда проверяем совпадение посимвольно при равных хешах
- Monte Carlo версия (без проверки) опасна, Las Vegas — безопасна

### Миф 3: "Suffix Array сложнее Suffix Tree"

**Реальность:**
- Suffix Array проще в реализации
- Занимает меньше памяти (4n vs 20n+ байт)
- С LCP array решает те же задачи
- Suffix Tree нужен только для специфических задач (Ukkonen online)

### Миф 4: "Z-function и KMP — это одно и то же"

**Реальность:**
- Концептуально разные: Z смотрит "вперёд", π смотрит "назад"
- Z-function проще для понимания
- KMP проще конвертировать в конечный автомат
- Можно преобразовать друг в друга, но это не тривиально

### Миф 5: "Aho-Corasick нужен только для антивирусов"

**Реальность:** Применения:
- Поисковые системы (подсветка ключевых слов)
- Фильтрация контента
- Биоинформатика (поиск мотивов ДНК)
- Лексический анализ в компиляторах

---

## Часть 13: Interview Tips

### Распознавание паттерна

| Ключевые слова в условии | Алгоритм |
|--------------------------|----------|
| "Find pattern in text" | KMP, Z-function |
| "All occurrences" | KMP, Rabin-Karp |
| "Multiple patterns" | Aho-Corasick |
| "Longest palindrome" | Manacher |
| "Repeated substring" | Suffix Array, Z-function |
| "All distinct substrings" | Suffix Array + LCP |
| "Pattern matching with wildcards" | Rabin-Karp модификация |

### Оптимизации для интервью

1. **Начинай с наивного решения** — O(nm), объясни почему неэффективно
2. **Объясни идею** — "используем структуру паттерна"
3. **Если забыл детали KMP** — используй Z-function (проще)
4. **Rolling hash** — полезен для многих вариаций задач

### Частые ошибки

1. **Off-by-one в Z-function:** i начинается с 1, не с 0
2. **Модульная арифметика в Rabin-Karp:** не забывай +mod перед %
3. **Sentinel в Suffix Array:** добавляй $ или используй comparator
4. **Manacher:** возврат к исходным индексам (делить на 2)

---

## Практические задачи (LeetCode)

| Задача | Алгоритм | Сложность |
|--------|----------|-----------|
| [28. Find the Index of the First Occurrence](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | KMP, Z-function | Easy |
| [5. Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) | Manacher, DP | Medium |
| [459. Repeated Substring Pattern](https://leetcode.com/problems/repeated-substring-pattern/) | KMP, Z-function | Easy |
| [214. Shortest Palindrome](https://leetcode.com/problems/shortest-palindrome/) | KMP, Z-function | Hard |
| [686. Repeated String Match](https://leetcode.com/problems/repeated-string-match/) | Rabin-Karp | Medium |
| [1044. Longest Duplicate Substring](https://leetcode.com/problems/longest-duplicate-substring/) | Suffix Array, Binary Search + Hash | Hard |
| [1316. Distinct Echo Substrings](https://leetcode.com/problems/distinct-echo-substrings/) | Rolling Hash | Hard |
| [212. Word Search II](https://leetcode.com/problems/word-search-ii/) | Trie, Aho-Corasick idea | Hard |
| [647. Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) | Manacher | Medium |
| [1392. Longest Happy Prefix](https://leetcode.com/problems/longest-happy-prefix/) | KMP prefix function | Hard |

---

## Ссылки и источники

- [CP-Algorithms: String Processing](https://cp-algorithms.com/string/)
- [cp-algorithms: Prefix Function (KMP)](https://cp-algorithms.com/string/prefix-function.html)
- [cp-algorithms: Z-Function](https://cp-algorithms.com/string/z-function.html)
- [cp-algorithms: Aho-Corasick](https://cp-algorithms.com/string/aho_corasick.html)
- [cp-algorithms: Suffix Array](https://cp-algorithms.com/string/suffix-array.html)
- [cp-algorithms: Manacher's Algorithm](https://cp-algorithms.com/string/manacher.html)
- [USACO Guide: String Searching](https://usaco.guide/adv/string-search)
- [Codeforces: Polynomial Hashing Analysis](https://codeforces.com/blog/entry/100027)
- [Brilliant: KMP Algorithm](https://brilliant.org/wiki/knuth-morris-pratt-algorithm/)
- [Wikipedia: Suffix Array](https://en.wikipedia.org/wiki/Suffix_array)
- [GeeksforGeeks: Manacher's Algorithm](https://www.geeksforgeeks.org/manachers-algorithm-linear-time-longest-palindromic-substring-part-1/)

---

## Связь с другими темами

### [[two-pointers-pattern]]
Two Pointers используется в базовых строковых задачах (проверка палиндрома, reverse string), а продвинутые строковые алгоритмы решают те же классы задач, но для более сложных случаев. Например, Manacher's algorithm находит все палиндромные подстроки за O(n), тогда как наивный two-pointer подход требует O(n^2). Понимание two-pointer подхода формирует интуицию для перехода к продвинутым методам: если two pointers недостаточно быстры, значит нужна предобработка (prefix function, Z-function, hashing).

### [[sliding-window-pattern]]
Sliding Window и строковые алгоритмы тесно связаны через концепцию «окна» по тексту. Rabin-Karp использует rolling hash — по сути скользящее окно фиксированного размера, где хеш пересчитывается за O(1) при сдвиге. Многие задачи на строки (longest substring without repeating characters, minimum window substring) решаются именно sliding window. Продвинутые алгоритмы вроде KMP и Aho-Corasick можно рассматривать как «умное скользящее окно», которое не возвращается назад при несовпадении.

---


---

## Проверь себя

> [!question]- Почему KMP предобрабатывает паттерн в failure function, а не текст?
> Паттерн обычно короче текста. Failure function (prefix function) pi[i] = длина наибольшего собственного префикса-суффикса pattern[0..i]. При несовпадении на позиции j: сдвигаем паттерн на j-pi[j-1] позиций, не возвращаемся в тексте. Текст проходится за один проход O(n), предобработка паттерна O(m). Итого O(n+m).

> [!question]- Как Rabin-Karp использует rolling hash и почему возможны ложные срабатывания?
> Rolling hash: hash(s[i+1..i+m]) вычисляется из hash(s[i..i+m-1]) за O(1) (вычитаем первый символ, умножаем на base, добавляем новый). Hash collision: разные строки могут дать одинаковый hash. Решение: при совпадении hash — проверяем посимвольно. Вероятность collision: 1/MOD. Два hash-а снижают до 1/MOD^2.

> [!question]- Задача: найти все вхождения набора из K паттернов в тексте. Почему Aho-Corasick лучше K отдельных KMP?
> K отдельных KMP: O(n*K + sum(m_i)). Aho-Corasick: O(n + sum(m_i) + z), где z = число вхождений. Строим trie из всех паттернов + suffix links (аналог failure function). Один проход по тексту находит все вхождения всех паттернов. Применение: множественный поиск, фильтрация, антивирусы.

## Ключевые карточки

Что такое KMP алгоритм?
?
Knuth-Morris-Pratt: поиск подстроки за O(n+m). Предобработка: prefix function pi[i] = длина наибольшего собственного prefix==suffix для pattern[0..i]. Поиск: при несовпадении сдвигаем на основе pi, не возвращаемся в тексте. Один проход по тексту.

Что такое Z-функция?
?
Z[i] = длина наибольшей подстроки начиная с i, совпадающей с префиксом строки. Z-функция для 'P$T' (P=pattern, T=text): позиции где Z[i] == len(P) = вхождения P в T. O(n+m). Альтернатива KMP, проще в реализации.

Как работает Rabin-Karp?
?
Rolling hash: hash окна длины m. Сдвиг: O(1) для нового hash. Совпадение hash -> проверка строк. Средний O(n+m), worst O(nm). Преимущество: легко расширить на множественный поиск (несколько паттернов одной длины).

Что такое Suffix Array?
?
Отсортированный массив всех суффиксов строки (по индексам). Построение: O(n log n) или O(n). Бинарный поиск подстроки: O(m log n). LCP Array (Longest Common Prefix): находит повторяющиеся подстроки. Компактнее Suffix Tree.

Что такое Manacher's Algorithm?
?
Нахождение всех палиндромов за O(n). Идея: используем уже найденные палиндромы для ускорения. Для каждой позиции i вычисляем радиус наибольшего палиндрома с центром в i. Трюк: обрабатываем чётные и нечётные длины единообразно (вставка спецсимволов).

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[competitive/competitive-programming-overview]] | Применение в соревнованиях |
| Углубиться | [[algorithms/string-advanced]] | String algorithms — теория |
| Смежная тема | [[data-structures/tries]] | Trie — основа Aho-Corasick |
| Обзор | [[patterns/patterns-overview]] | Вернуться к карте паттернов |


## Источники и дальнейшее чтение

- Cormen, Leiserson, Rivest & Stein (2009). *Introduction to Algorithms (CLRS).* — глава 32 (String Matching): формальное изложение Rabin-Karp, KMP и автоматного подхода; доказательства корректности и анализ сложности каждого алгоритма
- Gusfield (1997). *Algorithms on Strings, Trees, and Sequences.* — наиболее полное академическое изложение строковых алгоритмов: suffix trees, suffix arrays, Aho-Corasick; стандартный учебник для углублённого изучения
- Crochemore & Rytter (2003). *Jewels of Stringology.* — элегантные строковые алгоритмы с математическими доказательствами; глубокий разбор Z-function, prefix function и их связи; для продвинутого уровня
