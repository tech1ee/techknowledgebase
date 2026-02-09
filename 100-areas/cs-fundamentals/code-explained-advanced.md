# Продвинутый код с объяснением каждой детали

Этот документ продолжает разбор с нуля, фокусируясь на продвинутых темах: строки, продвинутое DP, и оптимизации.

---

# ЧАСТЬ 1: СТРОКОВЫЕ АЛГОРИТМЫ

## 1.1 Хеширование строк (String Hashing)

```kotlin
/**
 * ХЕШИРОВАНИЕ СТРОК — преобразование строки в число для быстрого сравнения
 *
 * Идея: представляем строку как число в системе счисления BASE
 *       hash(s) = s[0] * BASE^(n-1) + s[1] * BASE^(n-2) + ... + s[n-1] * BASE^0
 *
 * Почему это полезно:
 * - Сравнение строк за O(1) вместо O(n)
 * - Поиск подстроки за O(n + m) вместо O(n * m)
 *
 * ВАЖНО: Хеши могут совпадать для разных строк (коллизии)!
 *        Используем большой MOD и проверяем при совпадении хешей.
 */

class StringHasher(private val s: String) {
    // Параметры хеширования
    // BASE — основание системы счисления (обычно простое число > размера алфавита)
    // MOD — большое простое число для избежания overflow
    private val BASE = 31L
    private val MOD = 1_000_000_007L

    private val n = s.length

    // prefixHash[i] = хеш подстроки s[0..i-1]
    private val prefixHash = LongArray(n + 1)

    // pow[i] = BASE^i mod MOD (предподсчитанные степени)
    private val pow = LongArray(n + 1)

    init {
        // Вычисляем степени BASE
        pow[0] = 1
        for (i in 1..n) {
            pow[i] = (pow[i - 1] * BASE) % MOD
        }

        // Вычисляем префиксные хеши
        // prefixHash[i] = hash(s[0..i-1])
        for (i in 0 until n) {
            // Каждый новый символ: умножаем предыдущий хеш на BASE и добавляем новый символ
            // s[i] - 'a' + 1: преобразуем букву в число (a=1, b=2, ...)
            // Используем +1, чтобы 'a' != 0 (иначе "a" и "aa" имели бы разные хеши)
            prefixHash[i + 1] = (prefixHash[i] * BASE + (s[i] - 'a' + 1)) % MOD
        }
    }

    /**
     * Получить хеш подстроки s[l..r] (включительно)
     *
     * Формула: hash(s[l..r]) = prefixHash[r+1] - prefixHash[l] * BASE^(r-l+1)
     *
     * Почему так работает:
     * prefixHash[r+1] = s[0]*B^r + s[1]*B^(r-1) + ... + s[r]*B^0
     * prefixHash[l]*B^(r-l+1) = s[0]*B^r + ... + s[l-1]*B^(r-l+1)
     * Разность = s[l]*B^(r-l) + s[l+1]*B^(r-l-1) + ... + s[r]*B^0
     * Это и есть хеш подстроки!
     */
    fun getHash(l: Int, r: Int): Long {
        val len = r - l + 1
        var hash = prefixHash[r + 1] - (prefixHash[l] * pow[len]) % MOD
        // Корректируем отрицательный результат
        hash = (hash % MOD + MOD) % MOD
        return hash
    }

    /**
     * Проверить, равны ли подстроки s[l1..r1] и s[l2..r2]
     */
    fun substringEquals(l1: Int, r1: Int, l2: Int, r2: Int): Boolean {
        // Проверяем длины
        if (r1 - l1 != r2 - l2) return false
        // Сравниваем хеши
        return getHash(l1, r1) == getHash(l2, r2)
    }
}

// ПРИМЕР:
// s = "abcabc"
//
// Хеш всей строки:
// hash("abcabc") = 1*31^5 + 2*31^4 + 3*31^3 + 1*31^2 + 2*31 + 3
//
// prefixHash:
// [0]: 0
// [1]: 1 (хеш "a")
// [2]: 1*31 + 2 = 33 (хеш "ab")
// [3]: 33*31 + 3 = 1026 (хеш "abc")
// [4]: 1026*31 + 1 = 31807 (хеш "abca")
// ...
//
// getHash(0, 2) = хеш "abc"
// getHash(3, 5) = хеш "abc"
// Они равны! → подстроки одинаковые


// Применение: поиск подстроки (алгоритм Рабина-Карпа)
fun rabinKarp(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val n = text.length
    val m = pattern.length

    if (m > n) return result

    val textHasher = StringHasher(text)

    // Вычисляем хеш паттерна
    var patternHash = 0L
    val BASE = 31L
    val MOD = 1_000_000_007L
    for (i in 0 until m) {
        patternHash = (patternHash * BASE + (pattern[i] - 'a' + 1)) % MOD
    }

    // Ищем совпадения
    for (i in 0..n - m) {
        if (textHasher.getHash(i, i + m - 1) == patternHash) {
            // Хеши совпали — проверяем строки (защита от коллизий)
            if (text.substring(i, i + m) == pattern) {
                result.add(i)
            }
        }
    }

    return result
}
```

---

## 1.2 Z-функция

```kotlin
/**
 * Z-ФУНКЦИЯ — для каждой позиции i находит длину наибольшего префикса строки,
 *             который совпадает с подстрокой, начинающейся в позиции i
 *
 * z[i] = длина наибольшей строки s[i..i+k], которая является префиксом s
 *
 * Пример: s = "aabxaa"
 * z[0] = 0 (по определению, не считаем)
 * z[1] = 1 ("a" является префиксом "aabxaa")
 * z[2] = 0 ("b..." не является префиксом)
 * z[3] = 0 ("x..." не является префиксом)
 * z[4] = 2 ("aa" является префиксом "aabxaa")
 * z[5] = 1 ("a" является префиксом)
 *
 * Временная сложность: O(n)
 */

fun zFunction(s: String): IntArray {
    val n = s.length
    val z = IntArray(n)
    // z[0] = 0 по определению

    // l и r — границы "z-блока" — самого правого совпадения
    // Это отрезок [l, r], где s[l..r] совпадает с s[0..r-l]
    var l = 0
    var r = 0

    for (i in 1 until n) {
        if (i < r) {
            // Случай 1: i находится внутри z-блока
            // Можем использовать уже вычисленное значение z[i - l]
            // Но не больше чем до правой границы блока
            z[i] = minOf(r - i, z[i - l])
        }

        // Пытаемся расширить z[i] наивным сравнением
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++
        }

        // Обновляем z-блок если текущий уходит правее
        if (i + z[i] > r) {
            l = i
            r = i + z[i]
        }
    }

    return z
}

// ПОШАГОВЫЙ ПРИМЕР:
// s = "aabxaab"
//      0123456
//
// i=1: s[1]='a', s[0]='a' → совпадает, z[1]=1
//      s[2]='b', s[1]='a' → не совпадает
//      z[1] = 1, обновляем [l,r] = [1, 2)
//
// i=2: i >= r, начинаем с z[2]=0
//      s[2]='b', s[0]='a' → не совпадает
//      z[2] = 0
//
// i=3: s[3]='x', s[0]='a' → не совпадает
//      z[3] = 0
//
// i=4: s[4]='a', s[0]='a' → совпадает, z[4]=1
//      s[5]='a', s[1]='a' → совпадает, z[4]=2
//      s[6]='b', s[2]='b' → совпадает, z[4]=3
//      конец строки
//      z[4] = 3, обновляем [l,r] = [4, 7)
//
// i=5: i < r (5 < 7), z[5] = min(7-5, z[5-4]) = min(2, z[1]) = min(2, 1) = 1
//      Пробуем расширить: s[5+1]='b', s[1]='a' → не совпадает
//      z[5] = 1
//
// i=6: i < r (6 < 7), z[6] = min(7-6, z[6-4]) = min(1, z[2]) = min(1, 0) = 0
//      Пробуем расширить: s[6]='b', s[0]='a' → не совпадает
//      z[6] = 0
//
// Результат: z = [0, 1, 0, 0, 3, 1, 0]


// Применение: поиск подстроки
fun findPatternWithZ(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val m = pattern.length

    // Создаём строку: pattern + '$' + text
    // '$' — разделитель, которого нет в тексте
    val combined = pattern + '$' + text
    val z = zFunction(combined)

    // Если z[i] == m, значит подстрока text начинающаяся в позиции i-m-1
    // совпадает с pattern
    for (i in m + 1 until combined.length) {
        if (z[i] == m) {
            result.add(i - m - 1)
        }
    }

    return result
}
```

---

## 1.3 KMP (Knuth-Morris-Pratt)

```kotlin
/**
 * KMP — алгоритм поиска подстроки за O(n + m)
 *
 * Ключевая идея: при несовпадении не начинаем сначала,
 *                а используем информацию о уже совпавших символах
 *
 * Prefix function (π-функция):
 * π[i] = длина наибольшего собственного префикса подстроки s[0..i],
 *        который также является суффиксом этой подстроки
 *
 * Пример: s = "abcabc"
 * π[0] = 0 (пустой префикс)
 * π[1] = 0 ("ab" — нет общего префикса-суффикса)
 * π[2] = 0 ("abc" — нет)
 * π[3] = 1 ("abca" — "a" является и префиксом и суффиксом)
 * π[4] = 2 ("abcab" — "ab")
 * π[5] = 3 ("abcabc" — "abc")
 */

fun prefixFunction(s: String): IntArray {
    val n = s.length
    val pi = IntArray(n)
    // pi[0] = 0 по определению

    for (i in 1 until n) {
        // j — текущая длина совпадающего префикса-суффикса
        var j = pi[i - 1]

        // Пока не нашли совпадение, откатываемся по pi
        while (j > 0 && s[i] != s[j]) {
            j = pi[j - 1]
        }

        // Если символы совпали, увеличиваем длину
        if (s[i] == s[j]) {
            j++
        }

        pi[i] = j
    }

    return pi
}

// ПОШАГОВЫЙ ПРИМЕР:
// s = "abcabc"
//
// i=0: pi[0] = 0
//
// i=1: j = pi[0] = 0
//      s[1]='b', s[0]='a' → не равны
//      pi[1] = 0
//
// i=2: j = pi[1] = 0
//      s[2]='c', s[0]='a' → не равны
//      pi[2] = 0
//
// i=3: j = pi[2] = 0
//      s[3]='a', s[0]='a' → равны! j++
//      pi[3] = 1
//
// i=4: j = pi[3] = 1
//      s[4]='b', s[1]='b' → равны! j++
//      pi[4] = 2
//
// i=5: j = pi[4] = 2
//      s[5]='c', s[2]='c' → равны! j++
//      pi[5] = 3
//
// Результат: pi = [0, 0, 0, 1, 2, 3]


/**
 * KMP поиск подстроки
 */
fun kmpSearch(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val m = pattern.length
    val n = text.length

    if (m == 0) return result
    if (m > n) return result

    // Вычисляем π-функцию для pattern
    val pi = prefixFunction(pattern)

    var j = 0  // Позиция в pattern

    for (i in 0 until n) {
        // Откатываемся, пока символы не совпадут
        while (j > 0 && text[i] != pattern[j]) {
            j = pi[j - 1]
        }

        // Если символы совпали
        if (text[i] == pattern[j]) {
            j++
        }

        // Если совпал весь pattern
        if (j == m) {
            result.add(i - m + 1)  // Начало вхождения
            j = pi[j - 1]  // Продолжаем поиск
        }
    }

    return result
}

// ПОШАГОВЫЙ ПРИМЕР:
// text = "abxabcabcaby", pattern = "abcaby"
// pi = [0, 0, 0, 1, 2, 0]
//
// i=0: text[0]='a', pattern[0]='a' → совпало, j=1
// i=1: text[1]='b', pattern[1]='b' → совпало, j=2
// i=2: text[2]='x', pattern[2]='c' → не совпало
//      j = pi[1] = 0
//      text[2]='x', pattern[0]='a' → не совпало
//      j = 0
// i=3: text[3]='a', pattern[0]='a' → совпало, j=1
// i=4: text[4]='b', pattern[1]='b' → совпало, j=2
// i=5: text[5]='c', pattern[2]='c' → совпало, j=3
// ...
// i=11: j=6 == m → нашли вхождение в позиции 6
```

---

# ЧАСТЬ 2: ПРОДВИНУТОЕ DP

## 2.1 DP на подотрезках (Interval DP)

```kotlin
/**
 * INTERVAL DP — когда состояние это отрезок [l, r]
 *
 * Типичная задача: оптимальное разбиение/объединение отрезка
 *
 * Рекуррентное соотношение:
 * dp[l][r] = лучшее значение для отрезка [l, r]
 *          = min/max по всем k ∈ [l, r-1]:
 *            f(dp[l][k], dp[k+1][r])
 *
 * Порядок обхода: по возрастанию длины отрезка!
 */

// Задача: Matrix Chain Multiplication
// Даны размеры матриц: A1 (p0 × p1), A2 (p1 × p2), ..., An (p(n-1) × pn)
// Найти минимальное число скалярных умножений для их перемножения

fun matrixChainOrder(dimensions: IntArray): Int {
    val n = dimensions.size - 1  // Количество матриц
    // dp[i][j] = минимальная стоимость перемножения матриц с i по j
    val dp = Array(n) { IntArray(n) { 0 } }

    // Перебираем длину цепочки
    for (len in 2..n) {
        // Перебираем начало цепочки
        for (i in 0 until n - len + 1) {
            val j = i + len - 1  // Конец цепочки

            dp[i][j] = Int.MAX_VALUE

            // Пробуем все возможные разбиения
            for (k in i until j) {
                // Стоимость = левая часть + правая часть + объединение
                // Объединение матриц размеров (p[i] × p[k+1]) и (p[k+1] × p[j+1])
                // требует p[i] * p[k+1] * p[j+1] умножений
                val cost = dp[i][k] + dp[k + 1][j] +
                           dimensions[i] * dimensions[k + 1] * dimensions[j + 1]

                dp[i][j] = minOf(dp[i][j], cost)
            }
        }
    }

    return dp[0][n - 1]
}

// ПОШАГОВЫЙ ПРИМЕР:
// dimensions = [10, 20, 30, 40]
// Матрицы: A1 (10×20), A2 (20×30), A3 (30×40)
//
// Варианты:
// ((A1 × A2) × A3): (10×20×30) + (10×30×40) = 6000 + 12000 = 18000
// (A1 × (A2 × A3)): (20×30×40) + (10×20×40) = 24000 + 8000 = 32000
//
// Минимум: 18000


// Задача: Palindrome Partitioning
// Минимальное число разрезов, чтобы все части были палиндромами
fun minCut(s: String): Int {
    val n = s.length

    // isPalin[i][j] = true если s[i..j] палиндром
    val isPalin = Array(n) { BooleanArray(n) }

    // Все строки длины 1 — палиндромы
    for (i in 0 until n) isPalin[i][i] = true

    // Строки длины 2
    for (i in 0 until n - 1) {
        isPalin[i][i + 1] = (s[i] == s[i + 1])
    }

    // Строки длины 3 и более
    for (len in 3..n) {
        for (i in 0..n - len) {
            val j = i + len - 1
            isPalin[i][j] = (s[i] == s[j]) && isPalin[i + 1][j - 1]
        }
    }

    // dp[i] = минимум разрезов для s[0..i]
    val dp = IntArray(n) { it }  // Максимум i разрезов

    for (i in 0 until n) {
        if (isPalin[0][i]) {
            dp[i] = 0  // Вся подстрока — палиндром, разрезов не нужно
        } else {
            for (j in 0 until i) {
                if (isPalin[j + 1][i]) {
                    dp[i] = minOf(dp[i], dp[j] + 1)
                }
            }
        }
    }

    return dp[n - 1]
}
```

---

## 2.2 Bitmask DP

```kotlin
/**
 * BITMASK DP — когда состояние это подмножество элементов
 *
 * Ключевая идея: подмножество из n элементов можно закодировать
 *                целым числом от 0 до 2^n - 1
 *
 * Бит i установлен (равен 1) ↔ элемент i включён в подмножество
 *
 * Пример: n=4, mask=0b1011 (=11)
 * Бит 0 = 1 → элемент 0 включён
 * Бит 1 = 1 → элемент 1 включён
 * Бит 2 = 0 → элемент 2 НЕ включён
 * Бит 3 = 1 → элемент 3 включён
 * Подмножество: {0, 1, 3}
 */

// Задача: Traveling Salesman Problem (TSP)
// Найти кратчайший путь, посещающий все города ровно один раз

fun tsp(dist: Array<IntArray>): Int {
    val n = dist.size
    val INF = Int.MAX_VALUE / 2

    // dp[mask][i] = минимальная длина пути, который:
    // - начинается в городе 0
    // - посетил все города из mask
    // - заканчивается в городе i
    val dp = Array(1 shl n) { IntArray(n) { INF } }

    // Базовый случай: только город 0 посещён
    dp[1][0] = 0  // mask=1 = 0b0001 = только город 0

    // Перебираем все подмножества
    for (mask in 1 until (1 shl n)) {
        // Перебираем последний посещённый город
        for (last in 0 until n) {
            // Город last должен быть в mask
            if (mask and (1 shl last) == 0) continue
            // Если путь до (mask, last) не существует
            if (dp[mask][last] == INF) continue

            // Пробуем добавить новый город
            for (next in 0 until n) {
                // next не должен быть в mask
                if (mask and (1 shl next) != 0) continue

                val newMask = mask or (1 shl next)  // Добавляем next в маску
                val newDist = dp[mask][last] + dist[last][next]

                dp[newMask][next] = minOf(dp[newMask][next], newDist)
            }
        }
    }

    // Находим минимальный полный путь с возвратом в город 0
    val fullMask = (1 shl n) - 1  // Все города посещены
    var result = INF
    for (last in 0 until n) {
        result = minOf(result, dp[fullMask][last] + dist[last][0])
    }

    return result
}

// ПОШАГОВЫЙ ПРИМЕР:
// n = 3, города: 0, 1, 2
// dist = [[0, 10, 15],
//         [10, 0, 20],
//         [15, 20, 0]]
//
// Маски: 0b001=1, 0b010=2, 0b011=3, 0b100=4, 0b101=5, 0b110=6, 0b111=7
//
// dp[1][0] = 0 (старт в городе 0)
//
// mask=1 (только 0):
//   last=0: добавляем 1 → dp[3][1] = 0 + dist[0][1] = 10
//           добавляем 2 → dp[5][2] = 0 + dist[0][2] = 15
//
// mask=3 (0,1):
//   last=1: добавляем 2 → dp[7][2] = 10 + dist[1][2] = 30
//
// mask=5 (0,2):
//   last=2: добавляем 1 → dp[7][1] = 15 + dist[2][1] = 35
//
// mask=7 (все):
//   Возвращаемся в 0:
//   dp[7][1] + dist[1][0] = 35 + 10 = 45
//   dp[7][2] + dist[2][0] = 30 + 15 = 45
//
// Результат: 45 (путь 0→1→2→0 или 0→2→1→0)


// Полезные битовые операции для bitmask DP:

// Проверить, есть ли элемент i в множестве mask
fun hasElement(mask: Int, i: Int): Boolean = (mask and (1 shl i)) != 0

// Добавить элемент i в множество
fun addElement(mask: Int, i: Int): Int = mask or (1 shl i)

// Удалить элемент i из множества
fun removeElement(mask: Int, i: Int): Int = mask and (1 shl i).inv()

// Количество элементов в множестве
fun countElements(mask: Int): Int = Integer.bitCount(mask)

// Перебор всех подмножеств множества mask
fun iterateSubsets(mask: Int): Sequence<Int> = sequence {
    var subset = mask
    while (subset > 0) {
        yield(subset)
        subset = (subset - 1) and mask
    }
    yield(0)  // Пустое подмножество
}
```

---

## 2.3 DP на деревьях (Tree DP)

```kotlin
/**
 * TREE DP — динамическое программирование на деревьях
 *
 * Обычно используем DFS для обхода дерева "снизу вверх":
 * сначала вычисляем DP для детей, потом для текущего узла
 */

// Задача: Максимальная независимая сумма вершин
// Выбрать вершины так, чтобы никакие две не соседствовали, и сумма максимальна

fun maxIndependentSetSum(
    adj: Array<MutableList<Int>>,
    weights: IntArray
): Long {
    val n = adj.size

    // dp[v][0] = максимальная сумма в поддереве v, если v НЕ выбрана
    // dp[v][1] = максимальная сумма в поддереве v, если v выбрана
    val dp = Array(n) { LongArray(2) }
    val visited = BooleanArray(n)

    fun dfs(v: Int, parent: Int) {
        visited[v] = true

        // Если выбрали v, добавляем её вес
        dp[v][1] = weights[v].toLong()

        for (u in adj[v]) {
            if (u == parent) continue
            if (visited[u]) continue

            dfs(u, v)

            // Если v НЕ выбрана, детей можно выбирать или нет
            dp[v][0] += maxOf(dp[u][0], dp[u][1])

            // Если v выбрана, детей выбирать нельзя
            dp[v][1] += dp[u][0]
        }
    }

    dfs(0, -1)  // Начинаем с корня (вершина 0)

    return maxOf(dp[0][0], dp[0][1])
}

// ПОШАГОВЫЙ ПРИМЕР:
// Дерево:      1(10)
//             / \
//           2(5) 3(6)
//           /
//         4(3)
//
// Веса: [10, 5, 6, 3] (индексация с 0, но для понятности использую с 1)
// Вершина 0 = 10, 1 = 5, 2 = 6, 3 = 3
//
// DFS порядок: 3→1→2→0 (от листьев к корню)
//
// Вершина 3 (лист): dp[3] = [0, 3]
// Вершина 2 (лист): dp[2] = [0, 6]
//
// Вершина 1:
//   dp[1][0] = max(dp[3][0], dp[3][1]) = max(0, 3) = 3
//   dp[1][1] = 5 + dp[3][0] = 5 + 0 = 5
//   dp[1] = [3, 5]
//
// Вершина 0 (корень):
//   dp[0][0] = max(dp[1][0], dp[1][1]) + max(dp[2][0], dp[2][1])
//            = max(3, 5) + max(0, 6) = 5 + 6 = 11
//   dp[0][1] = 10 + dp[1][0] + dp[2][0] = 10 + 3 + 0 = 13
//   dp[0] = [11, 13]
//
// Результат: max(11, 13) = 13
// Оптимальный выбор: вершины 0 и 3 (10 + 3 = 13)


// Задача: Диаметр дерева
fun treeDiameter(adj: Array<MutableList<Int>>): Int {
    val n = adj.size
    var diameter = 0

    // depth[v] = максимальная глубина поддерева с корнем v
    val depth = IntArray(n)

    fun dfs(v: Int, parent: Int): Int {
        var maxDepth = 0
        var secondMaxDepth = 0

        for (u in adj[v]) {
            if (u == parent) continue

            val childDepth = dfs(u, v) + 1

            if (childDepth > maxDepth) {
                secondMaxDepth = maxDepth
                maxDepth = childDepth
            } else if (childDepth > secondMaxDepth) {
                secondMaxDepth = childDepth
            }
        }

        // Путь через v = maxDepth + secondMaxDepth
        diameter = maxOf(diameter, maxDepth + secondMaxDepth)

        return maxDepth
    }

    dfs(0, -1)
    return diameter
}
```

---

# ЧАСТЬ 3: ОПТИМИЗАЦИИ DP

## 3.1 Convex Hull Trick (CHT)

```kotlin
/**
 * CONVEX HULL TRICK — оптимизация DP когда:
 *
 * dp[i] = min(dp[j] + cost(j, i)) для всех j < i
 *
 * И cost(j, i) = a[j] * b[i] + c[j]
 * (линейная функция от b[i] с коэффициентами, зависящими от j)
 *
 * Идея: храним набор прямых y = a[j]*x + c[j]
 *       и для каждого запроса находим минимум в точке x = b[i]
 *
 * Если a[j] убывает, можно использовать deque для O(1) на запрос
 */

class ConvexHullTrickMin {
    // Храним прямые в виде (slope, intercept) = (a, c)
    private val lines = ArrayDeque<Pair<Long, Long>>()

    // Проверяем, нужна ли средняя прямая
    // Если прямая m лежит "над" пересечением l и r для всех x, она не нужна
    private fun bad(
        l: Pair<Long, Long>,
        m: Pair<Long, Long>,
        r: Pair<Long, Long>
    ): Boolean {
        // Пересечение l и m: x = (m.c - l.c) / (l.a - m.a)
        // Пересечение m и r: x = (r.c - m.c) / (m.a - r.a)
        // m не нужна если первое >= второго
        // Используем умножение вместо деления для избежания дробей
        return (m.second - l.second) * (m.first - r.first) >=
               (r.second - m.second) * (l.first - m.first)
    }

    // Добавить прямую y = slope * x + intercept
    // ВАЖНО: slope должны добавляться в убывающем порядке!
    fun addLine(slope: Long, intercept: Long) {
        val newLine = Pair(slope, intercept)

        // Удаляем прямые, которые стали ненужными
        while (lines.size >= 2 && bad(lines[lines.size - 2], lines.last(), newLine)) {
            lines.removeLast()
        }

        lines.addLast(newLine)
    }

    // Найти минимум в точке x
    // ВАЖНО: x должны запрашиваться в возрастающем порядке!
    fun query(x: Long): Long {
        // Удаляем прямые, которые уже не оптимальны
        while (lines.size >= 2) {
            val first = lines.first()
            val second = lines[1]
            if (first.first * x + first.second > second.first * x + second.second) {
                lines.removeFirst()
            } else {
                break
            }
        }

        val best = lines.first()
        return best.first * x + best.second
    }
}

// Пример использования: задача о делении отрезка
// dp[i] = min(dp[j] + cost(j, i)) для j < i
// где cost(j, i) = a[j] * b[i] (произведение)

fun optimizedDP(a: LongArray, b: LongArray): LongArray {
    val n = a.size
    val dp = LongArray(n)
    val cht = ConvexHullTrickMin()

    dp[0] = 0
    cht.addLine(a[0], dp[0])

    for (i in 1 until n) {
        // Запрос: находим минимум a[j] * b[i] + dp[j] для всех j < i
        dp[i] = cht.query(b[i])

        // Добавляем новую прямую для текущего i
        cht.addLine(a[i], dp[i])
    }

    return dp
}
```

---

## 3.2 SOS DP (Sum over Subsets)

```kotlin
/**
 * SOS DP — вычисление суммы по всем подмножествам для каждой маски
 *
 * Задача: для каждой маски m вычислить
 *         f[m] = Σ a[s] для всех s ⊆ m (s — подмножество m)
 *
 * Наивно: O(3^n) — для каждой маски перебираем подмножества
 * SOS DP: O(n * 2^n)
 *
 * Идея: dp[mask][i] = сумма по всем подмножествам, которые
 *       отличаются от mask только в первых i битах
 */

fun sosDP(a: IntArray, n: Int): LongArray {
    val size = 1 shl n  // 2^n

    // Инициализируем dp значениями a
    val dp = LongArray(size) { a[it].toLong() }

    // Для каждого бита
    for (i in 0 until n) {
        // Для каждой маски
        for (mask in 0 until size) {
            // Если бит i установлен
            if ((mask and (1 shl i)) != 0) {
                // Добавляем значения из маски без этого бита
                dp[mask] += dp[mask xor (1 shl i)]
            }
        }
    }

    return dp
}

// ПОШАГОВЫЙ ПРИМЕР:
// n = 2, a = [1, 2, 3, 4]
// a[00] = 1, a[01] = 2, a[10] = 3, a[11] = 4
//
// Ожидаемый результат:
// f[00] = a[00] = 1
// f[01] = a[00] + a[01] = 1 + 2 = 3
// f[10] = a[00] + a[10] = 1 + 3 = 4
// f[11] = a[00] + a[01] + a[10] + a[11] = 1 + 2 + 3 + 4 = 10
//
// Начало: dp = [1, 2, 3, 4]
//
// i = 0 (бит 0):
//   mask=01: бит 0 установлен → dp[01] += dp[00] = 2 + 1 = 3
//   mask=11: бит 0 установлен → dp[11] += dp[10] = 4 + 3 = 7
//   dp = [1, 3, 3, 7]
//
// i = 1 (бит 1):
//   mask=10: бит 1 установлен → dp[10] += dp[00] = 3 + 1 = 4
//   mask=11: бит 1 установлен → dp[11] += dp[01] = 7 + 3 = 10
//   dp = [1, 3, 4, 10]
//
// Результат совпадает с ожидаемым!


// Обратное: для каждой маски найти сумму по всем НАДмножествам
fun reverseSosDP(a: IntArray, n: Int): LongArray {
    val size = 1 shl n
    val dp = LongArray(size) { a[it].toLong() }

    for (i in 0 until n) {
        for (mask in 0 until size) {
            // Если бит i НЕ установлен
            if ((mask and (1 shl i)) == 0) {
                dp[mask] += dp[mask or (1 shl i)]
            }
        }
    }

    return dp
}
```

---

# ЧАСТЬ 4: МОДУЛЬНАЯ АРИФМЕТИКА (детально)

## 4.1 Расширенный алгоритм Евклида

```kotlin
/**
 * РАСШИРЕННЫЙ АЛГОРИТМ ЕВКЛИДА
 *
 * Находит x, y такие что: ax + by = gcd(a, b)
 *
 * Применение:
 * - Модульный обратный элемент
 * - Решение диофантовых уравнений
 * - Китайская теорема об остатках
 */

// Возвращает Triple(gcd, x, y) такой что ax + by = gcd
fun extendedGcd(a: Long, b: Long): Triple<Long, Long, Long> {
    if (b == 0L) {
        // База: a * 1 + 0 * 0 = a = gcd(a, 0)
        return Triple(a, 1L, 0L)
    }

    // Рекурсивный вызов для (b, a mod b)
    val (g, x1, y1) = extendedGcd(b, a % b)

    // Пересчитываем x и y
    // Из: b * x1 + (a mod b) * y1 = g
    // a mod b = a - (a/b) * b
    // b * x1 + (a - (a/b) * b) * y1 = g
    // a * y1 + b * (x1 - (a/b) * y1) = g
    val x = y1
    val y = x1 - (a / b) * y1

    return Triple(g, x, y)
}

// ПРИМЕР:
// extendedGcd(35, 15)
//   extendedGcd(15, 5)
//     extendedGcd(5, 0) → (5, 1, 0)
//   ← (5, 0, 1 - 3*0) = (5, 0, 1)
//   Проверка: 15*0 + 5*1 = 5 ✓
// ← (5, 1, 0 - 2*1) = (5, 1, -2)
// Проверка: 35*1 + 15*(-2) = 35 - 30 = 5 ✓


// Модульный обратный через расширенный Евклид
// Работает для любого модуля (не обязательно простого)!
fun modInverseExtGcd(a: Long, mod: Long): Long? {
    val (g, x, _) = extendedGcd(a, mod)

    // Обратный существует только если gcd(a, mod) = 1
    if (g != 1L) return null

    // Приводим x к положительному остатку
    return ((x % mod) + mod) % mod
}
```

---

## 4.2 Китайская теорема об остатках (CRT)

```kotlin
/**
 * КИТАЙСКАЯ ТЕОРЕМА ОБ ОСТАТКАХ
 *
 * Система уравнений:
 * x ≡ a1 (mod m1)
 * x ≡ a2 (mod m2)
 * ...
 * x ≡ ak (mod mk)
 *
 * Имеет единственное решение по модулю M = m1 * m2 * ... * mk
 * если все mi попарно взаимно просты
 */

fun chineseRemainderTheorem(
    remainders: LongArray,  // a1, a2, ..., ak
    moduli: LongArray       // m1, m2, ..., mk
): Long {
    val k = remainders.size
    val M = moduli.reduce { acc, m -> acc * m }  // Произведение всех модулей

    var result = 0L

    for (i in 0 until k) {
        val mi = moduli[i]
        val ai = remainders[i]

        // Mi = M / mi
        val Mi = M / mi

        // Находим обратный к Mi по модулю mi
        val (_, yi, _) = extendedGcd(Mi, mi)

        // Добавляем вклад: ai * Mi * yi
        result += ai * Mi * ((yi % mi + mi) % mi)
        result %= M
    }

    return (result % M + M) % M
}

// ПРИМЕР:
// x ≡ 2 (mod 3)
// x ≡ 3 (mod 5)
// x ≡ 2 (mod 7)
//
// M = 3 * 5 * 7 = 105
//
// Для i=0: M0 = 35, 35^(-1) mod 3 = 2^(-1) mod 3 = 2
//          вклад = 2 * 35 * 2 = 140
//
// Для i=1: M1 = 21, 21^(-1) mod 5 = 1^(-1) mod 5 = 1
//          вклад = 3 * 21 * 1 = 63
//
// Для i=2: M2 = 15, 15^(-1) mod 7 = 1^(-1) mod 7 = 1
//          вклад = 2 * 15 * 1 = 30
//
// x = (140 + 63 + 30) mod 105 = 233 mod 105 = 23
//
// Проверка:
// 23 mod 3 = 2 ✓
// 23 mod 5 = 3 ✓
// 23 mod 7 = 2 ✓
```

---

# ЧАСТЬ 5: СУФФИКСНЫЕ СТРУКТУРЫ

## 5.1 Суффиксный массив (Suffix Array)

```kotlin
/**
 * СУФФИКСНЫЙ МАССИВ — отсортированный массив всех суффиксов строки
 *
 * Суффикс строки s начиная с позиции i — это s[i..n-1]
 *
 * Пример: s = "banana"
 * Суффиксы:
 *   0: "banana"
 *   1: "anana"
 *   2: "nana"
 *   3: "ana"
 *   4: "na"
 *   5: "a"
 *
 * После сортировки (лексикографически):
 *   5: "a"
 *   3: "ana"
 *   1: "anana"
 *   0: "banana"
 *   4: "na"
 *   2: "nana"
 *
 * Suffix Array = [5, 3, 1, 0, 4, 2]
 *
 * Применение:
 * - Поиск подстроки за O(m log n)
 * - LCP (Longest Common Prefix) — общие префиксы соседних суффиксов
 * - Количество различных подстрок
 */

// Наивное построение за O(n² log n) — для понимания
fun buildSuffixArrayNaive(s: String): IntArray {
    val n = s.length

    // Создаём пары (суффикс как строка, его начальный индекс)
    // Сортируем по суффиксу, возвращаем индексы
    return (0 until n)
        .sortedBy { s.substring(it) }  // Сортировка по суффиксам
        .toIntArray()
}

// ПОШАГОВЫЙ ПРИМЕР для s = "banana":
// Создаём пары:
//   (0, "banana"), (1, "anana"), (2, "nana"),
//   (3, "ana"), (4, "na"), (5, "a")
//
// Сортируем по второму элементу (суффиксу):
//   (5, "a"), (3, "ana"), (1, "anana"),
//   (0, "banana"), (4, "na"), (2, "nana")
//
// Берём первые элементы: [5, 3, 1, 0, 4, 2]


/**
 * Эффективное построение за O(n log n) — алгоритм с сортировкой по удвоению
 *
 * Идея:
 * 1. Сортируем суффиксы по первым 1, 2, 4, 8, ... символам
 * 2. На каждом шаге используем результат предыдущего шага
 * 3. log n шагов, каждый шаг O(n) с counting sort
 */
fun buildSuffixArray(s: String): IntArray {
    val n = s.length

    // suffixArray[i] = индекс i-го суффикса в отсортированном порядке
    var suffixArray = IntArray(n) { it }

    // rank[i] = ранг (позиция в сортировке) суффикса, начинающегося в i
    var rank = IntArray(n) { s[it].code }

    // Сортируем по первым k символам, k = 1, 2, 4, 8, ...
    var k = 1
    while (k < n) {
        // Сортируем по паре (rank[i], rank[i+k])
        // Если i+k >= n, то rank[i+k] = -1 (пустой суффикс идёт первым)

        // Компаратор для сортировки
        val comparator = Comparator<Int> { i, j ->
            if (rank[i] != rank[j]) {
                rank[i] - rank[j]
            } else {
                val ri = if (i + k < n) rank[i + k] else -1
                val rj = if (j + k < n) rank[j + k] else -1
                ri - rj
            }
        }

        suffixArray = suffixArray.sortedWith(comparator).toIntArray()

        // Обновляем ранги
        val newRank = IntArray(n)
        newRank[suffixArray[0]] = 0

        for (i in 1 until n) {
            val prev = suffixArray[i - 1]
            val curr = suffixArray[i]

            // Если пары разные — увеличиваем ранг
            val prevPair = Pair(rank[prev], if (prev + k < n) rank[prev + k] else -1)
            val currPair = Pair(rank[curr], if (curr + k < n) rank[curr + k] else -1)

            newRank[curr] = if (prevPair == currPair) {
                newRank[prev]
            } else {
                newRank[prev] + 1
            }
        }

        rank = newRank
        k *= 2
    }

    return suffixArray
}

// ПОШАГОВЫЙ ПРИМЕР для s = "abaab":
//
// Начало: rank по символам
// rank = [97, 98, 97, 97, 98]  (ASCII коды: a=97, b=98)
//
// k=1: сортируем по парам (rank[i], rank[i+1])
// Пары: (97,98), (98,97), (97,97), (97,98), (98,-)
// После сортировки: suffixArray = [2, 0, 3, 1, 4]
// Новые ранги: [1, 3, 0, 2, 4]
//
// k=2: сортируем по парам (rank[i], rank[i+2])
// После сортировки: suffixArray = [2, 3, 0, 4, 1]
// ...
//
// k=4: финальный результат


/**
 * LCP Array (Longest Common Prefix)
 *
 * lcp[i] = длина общего префикса суффиксов suffixArray[i] и suffixArray[i-1]
 *
 * Алгоритм Касаи — строит LCP за O(n)
 */
fun buildLCPArray(s: String, suffixArray: IntArray): IntArray {
    val n = s.length
    val lcp = IntArray(n)

    // rank[i] = позиция суффикса i в suffixArray
    val rank = IntArray(n)
    for (i in 0 until n) {
        rank[suffixArray[i]] = i
    }

    var k = 0  // Текущая длина LCP

    for (i in 0 until n) {
        if (rank[i] == 0) {
            k = 0
            continue
        }

        // Предыдущий суффикс в отсортированном порядке
        val j = suffixArray[rank[i] - 1]

        // Считаем общий префикс
        while (i + k < n && j + k < n && s[i + k] == s[j + k]) {
            k++
        }

        lcp[rank[i]] = k

        // Ключевое наблюдение: lcp для следующего суффикса не меньше k-1
        if (k > 0) k--
    }

    return lcp
}

// ПРИМЕНЕНИЕ: Количество различных подстрок
// Всего подстрок: n*(n+1)/2
// Дубликаты: сумма LCP
// Различных = n*(n+1)/2 - sum(lcp)

fun countDistinctSubstrings(s: String): Long {
    val n = s.length
    val sa = buildSuffixArray(s)
    val lcp = buildLCPArray(s, sa)

    val total = n.toLong() * (n + 1) / 2
    val duplicates = lcp.sumOf { it.toLong() }

    return total - duplicates
}
```

---

## 5.2 Применение суффиксного массива

```kotlin
/**
 * Поиск подстроки с помощью суффиксного массива
 *
 * Идея: бинарный поиск в отсортированном массиве суффиксов
 * Сложность: O(m log n) где m — длина паттерна
 */
fun searchPattern(text: String, pattern: String, suffixArray: IntArray): List<Int> {
    val n = text.length
    val m = pattern.length
    val result = mutableListOf<Int>()

    // Бинарный поиск: находим первый суффикс >= pattern
    var left = 0
    var right = n

    while (left < right) {
        val mid = (left + right) / 2
        val suffix = text.substring(suffixArray[mid])

        if (suffix < pattern) {
            left = mid + 1
        } else {
            right = mid
        }
    }

    val start = left

    // Находим последний суффикс, начинающийся с pattern
    right = n
    while (left < right) {
        val mid = (left + right) / 2
        val suffix = text.substring(suffixArray[mid])

        if (suffix.startsWith(pattern)) {
            left = mid + 1
        } else {
            right = mid
        }
    }

    // Все суффиксы в диапазоне [start, left) содержат pattern
    for (i in start until left) {
        result.add(suffixArray[i])
    }

    return result.sorted()
}

// ПРИМЕР:
// text = "banana", pattern = "ana"
// suffixArray = [5, 3, 1, 0, 4, 2]
// Суффиксы: ["a", "ana", "anana", "banana", "na", "nana"]
//
// Поиск "ana":
// - Бинарный поиск находит позиции 1 и 2 (суффиксы "ana" и "anana")
// - Результат: позиции 3 и 1 в исходной строке


/**
 * Longest Repeated Substring (Самая длинная повторяющаяся подстрока)
 *
 * Это максимальное значение в LCP массиве!
 */
fun longestRepeatedSubstring(s: String): String {
    if (s.length <= 1) return ""

    val sa = buildSuffixArray(s)
    val lcp = buildLCPArray(s, sa)

    // Находим максимальный LCP
    var maxLcp = 0
    var pos = 0

    for (i in 1 until s.length) {
        if (lcp[i] > maxLcp) {
            maxLcp = lcp[i]
            pos = sa[i]
        }
    }

    return if (maxLcp > 0) s.substring(pos, pos + maxLcp) else ""
}

// ПРИМЕР:
// s = "banana"
// LCP = [0, 1, 3, 0, 0, 2]
// Максимум 3 на позиции 2 → suffixArray[2] = 1
// Подстрока s[1..3] = "ana"
```

---

# ЧАСТЬ 6: ПОТОКИ В ГРАФАХ

## 6.1 Максимальный поток (Алгоритм Эдмондса-Карпа)

```kotlin
/**
 * МАКСИМАЛЬНЫЙ ПОТОК — найти максимальное количество "жидкости",
 *                      которое можно передать от источника к стоку
 *
 * Граф: рёбра имеют пропускную способность (capacity)
 * Поток: сколько "жидкости" течёт по каждому ребру
 *
 * Ограничения:
 * 1. Поток ≤ пропускной способности
 * 2. Сохранение потока: входящий = исходящий (кроме source и sink)
 *
 * Алгоритм Эдмондса-Карпа = Ford-Fulkerson с BFS для поиска пути
 * Сложность: O(V * E²)
 */

class MaxFlow(private val n: Int) {
    // capacity[u][v] = пропускная способность ребра u→v
    private val capacity = Array(n) { IntArray(n) }

    // adj[u] = список соседей вершины u (включая обратные рёбра)
    private val adj = Array(n) { mutableListOf<Int>() }

    /**
     * Добавить ребро u→v с пропускной способностью cap
     */
    fun addEdge(u: Int, v: Int, cap: Int) {
        capacity[u][v] += cap
        adj[u].add(v)
        adj[v].add(u)  // Обратное ребро для алгоритма
    }

    /**
     * Найти максимальный поток от source к sink
     */
    fun maxFlow(source: Int, sink: Int): Int {
        var totalFlow = 0

        // Пока существует увеличивающий путь
        while (true) {
            // BFS для поиска кратчайшего пути от source к sink
            val parent = IntArray(n) { -1 }
            val visited = BooleanArray(n)
            val queue = ArrayDeque<Int>()

            queue.addLast(source)
            visited[source] = true

            while (queue.isNotEmpty() && !visited[sink]) {
                val u = queue.removeFirst()

                for (v in adj[u]) {
                    // Можем идти по ребру u→v если:
                    // 1. v не посещена
                    // 2. Есть остаточная пропускная способность
                    if (!visited[v] && capacity[u][v] > 0) {
                        visited[v] = true
                        parent[v] = u
                        queue.addLast(v)
                    }
                }
            }

            // Если не дошли до sink — путей больше нет
            if (!visited[sink]) break

            // Находим минимальную пропускную способность на пути
            var pathFlow = Int.MAX_VALUE
            var v = sink
            while (v != source) {
                val u = parent[v]
                pathFlow = minOf(pathFlow, capacity[u][v])
                v = u
            }

            // Обновляем остаточные пропускные способности
            v = sink
            while (v != source) {
                val u = parent[v]
                capacity[u][v] -= pathFlow  // Уменьшаем прямое ребро
                capacity[v][u] += pathFlow  // Увеличиваем обратное ребро
                v = u
            }

            totalFlow += pathFlow
        }

        return totalFlow
    }
}

// ПОШАГОВЫЙ ПРИМЕР:
// Граф:
//        10         10
//   0 --------→ 1 --------→ 3
//   |           ↑           ↑
//   |5          |5          |10
//   ↓           |           |
//   2 --------→ 4 --------→-+
//        10         5
//
// source=0, sink=3
//
// Итерация 1:
//   BFS находит путь: 0 → 1 → 3
//   Минимальная пропускная способность: min(10, 10) = 10
//   Обновляем: capacity[0][1]=0, capacity[1][3]=0
//   totalFlow = 10
//
// Итерация 2:
//   BFS находит путь: 0 → 2 → 4 → 3
//   Минимальная пропускная способность: min(5, 10, 10) = 5
//   totalFlow = 15
//
// Итерация 3:
//   Нет пути от 0 к 3 с положительной пропускной способностью
//   Ответ: 15


// Использование:
fun maxFlowExample() {
    val mf = MaxFlow(4)
    mf.addEdge(0, 1, 10)
    mf.addEdge(0, 2, 5)
    mf.addEdge(1, 3, 10)
    mf.addEdge(2, 3, 10)
    mf.addEdge(2, 1, 5)

    println(mf.maxFlow(0, 3))  // 15
}
```

---

## 6.2 Алгоритм Диница (более эффективный)

```kotlin
/**
 * Алгоритм ДИНИЦА — улучшенный алгоритм максимального потока
 *
 * Отличия от Эдмондса-Карпа:
 * 1. Строим "уровневый граф" с помощью BFS
 * 2. Ищем все блокирующие потоки с помощью DFS
 *
 * Сложность: O(V² * E)
 * Для unit capacity графов: O(E * √V)
 */

class Dinic(private val n: Int) {
    private data class Edge(val to: Int, var cap: Int, val rev: Int)

    private val graph = Array(n) { mutableListOf<Edge>() }
    private val level = IntArray(n)
    private val iter = IntArray(n)

    /**
     * Добавить ребро u→v с пропускной способностью cap
     */
    fun addEdge(from: Int, to: Int, cap: Int) {
        // Прямое ребро
        graph[from].add(Edge(to, cap, graph[to].size))
        // Обратное ребро (нулевая пропускная способность)
        graph[to].add(Edge(from, 0, graph[from].size - 1))
    }

    /**
     * BFS для построения уровневого графа
     *
     * level[v] = кратчайшее расстояние от source до v
     * Возвращает true если sink достижим
     */
    private fun bfs(source: Int, sink: Int): Boolean {
        level.fill(-1)
        level[source] = 0
        val queue = ArrayDeque<Int>()
        queue.addLast(source)

        while (queue.isNotEmpty()) {
            val v = queue.removeFirst()
            for (edge in graph[v]) {
                // Идём по ребру если есть пропускная способность
                // и вершина ещё не посещена
                if (edge.cap > 0 && level[edge.to] < 0) {
                    level[edge.to] = level[v] + 1
                    queue.addLast(edge.to)
                }
            }
        }

        return level[sink] >= 0
    }

    /**
     * DFS для поиска блокирующего потока
     *
     * @param v текущая вершина
     * @param sink конечная вершина
     * @param f текущий поток (минимум на пути)
     * @return размер найденного потока
     */
    private fun dfs(v: Int, sink: Int, f: Int): Int {
        if (v == sink) return f

        // iter[v] — с какого ребра продолжать поиск
        // (оптимизация: не проверяем уже использованные рёбра)
        while (iter[v] < graph[v].size) {
            val edge = graph[v][iter[v]]

            // Идём только "вниз" по уровням и по рёбрам с пропускной способностью
            if (edge.cap > 0 && level[v] < level[edge.to]) {
                val d = dfs(edge.to, sink, minOf(f, edge.cap))

                if (d > 0) {
                    // Нашли поток — обновляем рёбра
                    edge.cap -= d
                    graph[edge.to][edge.rev].cap += d
                    return d
                }
            }
            iter[v]++
        }

        return 0
    }

    /**
     * Найти максимальный поток
     */
    fun maxFlow(source: Int, sink: Int): Long {
        var flow = 0L

        // Пока sink достижим из source
        while (bfs(source, sink)) {
            iter.fill(0)  // Сбрасываем итераторы

            // Ищем все блокирующие потоки
            var f: Int
            while (true) {
                f = dfs(source, sink, Int.MAX_VALUE)
                if (f == 0) break
                flow += f
            }
        }

        return flow
    }
}

// ПОЧЕМУ ДИНИЦА БЫСТРЕЕ:
// 1. BFS строит уровни — идём только "вперёд" к sink
// 2. После нахождения блокирующего потока, расстояние до sink увеличивается
// 3. Максимум V фаз (BFS), в каждой фазе O(V*E) для блокирующего потока
// 4. Итого: O(V² * E)
```

---

# ЧАСТЬ 7: FFT И NTT

## 7.1 Быстрое преобразование Фурье (FFT)

```kotlin
import kotlin.math.*

/**
 * FFT (Fast Fourier Transform) — быстрое умножение многочленов
 *
 * Задача: даны два многочлена степени n-1, найти их произведение
 *
 * Наивное умножение: O(n²)
 * FFT: O(n log n)
 *
 * Идея:
 * 1. Многочлен можно представить коэффициентами ИЛИ значениями в точках
 * 2. Умножение значений в точках: O(n)
 * 3. FFT переводит коэффициенты → значения за O(n log n)
 * 4. IFFT переводит значения → коэффициенты за O(n log n)
 *
 * Алгоритм:
 * 1. FFT(A), FFT(B) — переводим в значения
 * 2. C[i] = A[i] * B[i] — поточечное умножение
 * 3. IFFT(C) — переводим обратно в коэффициенты
 */

// Комплексное число
data class Complex(val re: Double, val im: Double) {
    operator fun plus(other: Complex) = Complex(re + other.re, im + other.im)
    operator fun minus(other: Complex) = Complex(re - other.re, im - other.im)
    operator fun times(other: Complex) = Complex(
        re * other.re - im * other.im,
        re * other.im + im * other.re
    )
    operator fun div(scalar: Double) = Complex(re / scalar, im / scalar)
}

/**
 * FFT/IFFT рекурсивная реализация
 *
 * @param a массив коэффициентов/значений
 * @param invert true для обратного преобразования
 */
fun fft(a: Array<Complex>, invert: Boolean = false) {
    val n = a.size
    if (n == 1) return

    // Разделяем на чётные и нечётные индексы
    val a0 = Array(n / 2) { a[it * 2] }      // Чётные: a[0], a[2], a[4], ...
    val a1 = Array(n / 2) { a[it * 2 + 1] }  // Нечётные: a[1], a[3], a[5], ...

    // Рекурсивно применяем FFT
    fft(a0, invert)
    fft(a1, invert)

    // Вычисляем угол для корня из единицы
    val angle = 2 * PI / n * (if (invert) -1 else 1)
    var w = Complex(1.0, 0.0)  // Текущий корень
    val wn = Complex(cos(angle), sin(angle))  // Примитивный корень

    for (i in 0 until n / 2) {
        // Формула "бабочки":
        // a[i] = a0[i] + w * a1[i]
        // a[i + n/2] = a0[i] - w * a1[i]
        val t = w * a1[i]
        a[i] = a0[i] + t
        a[i + n / 2] = a0[i] - t

        w = w * wn  // Следующий корень
    }

    // Для обратного преобразования делим на n
    if (invert) {
        for (i in 0 until n) {
            a[i] = a[i] / n.toDouble()
        }
    }
}

/**
 * Умножение многочленов через FFT
 *
 * @param a коэффициенты первого многочлена
 * @param b коэффициенты второго многочлена
 * @return коэффициенты произведения
 */
fun multiplyPolynomials(a: IntArray, b: IntArray): IntArray {
    // Находим размер, кратный степени двойки
    val resultSize = a.size + b.size - 1
    var n = 1
    while (n < resultSize) n *= 2

    // Преобразуем в комплексные числа с дополнением нулями
    val fa = Array(n) { if (it < a.size) Complex(a[it].toDouble(), 0.0) else Complex(0.0, 0.0) }
    val fb = Array(n) { if (it < b.size) Complex(b[it].toDouble(), 0.0) else Complex(0.0, 0.0) }

    // Прямое FFT
    fft(fa)
    fft(fb)

    // Поточечное умножение
    for (i in 0 until n) {
        fa[i] = fa[i] * fb[i]
    }

    // Обратное FFT
    fft(fa, invert = true)

    // Преобразуем обратно в целые числа
    return IntArray(resultSize) { (fa[it].re + 0.5).toInt() }
}

// ПРИМЕР:
// a = [1, 2, 3] → многочлен 1 + 2x + 3x²
// b = [4, 5]    → многочлен 4 + 5x
//
// Произведение: (1 + 2x + 3x²)(4 + 5x)
// = 4 + 5x + 8x + 10x² + 12x² + 15x³
// = 4 + 13x + 22x² + 15x³
//
// Результат: [4, 13, 22, 15]

fun fftExample() {
    val a = intArrayOf(1, 2, 3)
    val b = intArrayOf(4, 5)
    val result = multiplyPolynomials(a, b)
    println(result.toList())  // [4, 13, 22, 15]
}


// ОБЪЯСНЕНИЕ FFT (упрощённо):
//
// 1. КОРНИ ИЗ ЕДИНИЦЫ
//    wₙ = e^(2πi/n) — комплексное число такое что wₙⁿ = 1
//    w₄ = i (мнимая единица), т.к. i⁴ = 1
//
// 2. ИДЕЯ DIVIDE & CONQUER
//    P(x) = P₀(x²) + x * P₁(x²)
//    где P₀ = чётные коэффициенты, P₁ = нечётные
//
// 3. ФОРМУЛА БАБОЧКИ
//    P(wₙᵏ) = P₀(wₙ²ᵏ) + wₙᵏ * P₁(wₙ²ᵏ)
//    P(wₙᵏ⁺ⁿ/²) = P₀(wₙ²ᵏ) - wₙᵏ * P₁(wₙ²ᵏ)
//
// 4. РЕКУРСИЯ
//    T(n) = 2T(n/2) + O(n) → O(n log n)
```

---

## 7.2 NTT (Number Theoretic Transform)

```kotlin
/**
 * NTT — FFT для целых чисел по модулю
 *
 * Преимущества:
 * - Нет ошибок округления (в отличие от FFT с комплексными числами)
 * - Результат точный
 *
 * Требования к модулю:
 * - MOD = c * 2^k + 1 (простое число)
 * - Популярные модули: 998244353, 1004535809, 985661441
 * - 998244353 = 119 * 2^23 + 1, примитивный корень = 3
 */

const val NTT_MOD = 998244353L
const val NTT_ROOT = 3L  // Примитивный корень по модулю NTT_MOD

// Быстрое возведение в степень по модулю
fun powMod(base: Long, exp: Long, mod: Long): Long {
    var result = 1L
    var b = base % mod
    var e = exp

    while (e > 0) {
        if (e and 1L == 1L) {
            result = result * b % mod
        }
        b = b * b % mod
        e = e shr 1
    }

    return result
}

/**
 * NTT — преобразование в поле по модулю
 */
fun ntt(a: LongArray, invert: Boolean = false) {
    val n = a.size

    // Bit-reversal перестановка
    var j = 0
    for (i in 1 until n) {
        var bit = n shr 1
        while (j and bit != 0) {
            j = j xor bit
            bit = bit shr 1
        }
        j = j xor bit

        if (i < j) {
            val temp = a[i]
            a[i] = a[j]
            a[j] = temp
        }
    }

    // Итеративная бабочка
    var len = 2
    while (len <= n) {
        val w = if (invert) {
            powMod(NTT_ROOT, NTT_MOD - 1 - (NTT_MOD - 1) / len, NTT_MOD)
        } else {
            powMod(NTT_ROOT, (NTT_MOD - 1) / len, NTT_MOD)
        }

        var i = 0
        while (i < n) {
            var wj = 1L
            for (jj in 0 until len / 2) {
                val u = a[i + jj]
                val v = a[i + jj + len / 2] * wj % NTT_MOD

                a[i + jj] = (u + v) % NTT_MOD
                a[i + jj + len / 2] = (u - v + NTT_MOD) % NTT_MOD

                wj = wj * w % NTT_MOD
            }
            i += len
        }

        len *= 2
    }

    if (invert) {
        val nInv = powMod(n.toLong(), NTT_MOD - 2, NTT_MOD)
        for (i in 0 until n) {
            a[i] = a[i] * nInv % NTT_MOD
        }
    }
}

/**
 * Умножение многочленов через NTT (без ошибок округления!)
 */
fun multiplyPolynomialsNTT(a: LongArray, b: LongArray): LongArray {
    val resultSize = a.size + b.size - 1
    var n = 1
    while (n < resultSize) n *= 2

    val fa = LongArray(n)
    val fb = LongArray(n)
    for (i in a.indices) fa[i] = a[i]
    for (i in b.indices) fb[i] = b[i]

    ntt(fa)
    ntt(fb)

    for (i in 0 until n) {
        fa[i] = fa[i] * fb[i] % NTT_MOD
    }

    ntt(fa, invert = true)

    return fa.copyOf(resultSize)
}

// КОГДА ИСПОЛЬЗОВАТЬ NTT вместо FFT:
// 1. Результат нужен по модулю (особенно 998244353)
// 2. Нужна точность (FFT может дать ошибки для больших коэффициентов)
// 3. Competitive programming (обычно модуль = 998244353)
```

---

# ЧАСТЬ 8: ДОПОЛНИТЕЛЬНЫЕ ТЕХНИКИ

## 8.1 Heavy-Light Decomposition (HLD)

```kotlin
/**
 * HEAVY-LIGHT DECOMPOSITION — разбиение дерева на "тяжёлые" и "лёгкие" пути
 *
 * Позволяет отвечать на запросы на пути в дереве за O(log² n)
 *
 * Идея:
 * 1. Для каждой вершины определяем "тяжёлого" ребёнка (с наибольшим поддеревом)
 * 2. Тяжёлые рёбра образуют цепи
 * 3. Любой путь пересекает O(log n) цепей
 * 4. На каждой цепи используем дерево отрезков
 */

class HLD(private val n: Int) {
    private val adj = Array(n) { mutableListOf<Int>() }

    // Результаты HLD
    private val parent = IntArray(n) { -1 }
    private val depth = IntArray(n)
    private val heavy = IntArray(n) { -1 }  // Тяжёлый ребёнок
    private val head = IntArray(n)          // Голова цепи
    private val pos = IntArray(n)           // Позиция в дереве отрезков

    private var currentPos = 0

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)
    }

    /**
     * DFS 1: вычисляем размеры поддеревьев и находим тяжёлые рёбра
     */
    private fun dfs(v: Int): Int {
        var size = 1
        var maxChildSize = 0

        for (u in adj[v]) {
            if (u == parent[v]) continue

            parent[u] = v
            depth[u] = depth[v] + 1

            val childSize = dfs(u)
            size += childSize

            // Обновляем тяжёлого ребёнка
            if (childSize > maxChildSize) {
                maxChildSize = childSize
                heavy[v] = u
            }
        }

        return size
    }

    /**
     * DFS 2: строим цепи и назначаем позиции
     */
    private fun decompose(v: Int, h: Int) {
        head[v] = h
        pos[v] = currentPos++

        // Сначала идём по тяжёлому ребру (чтобы цепь была непрерывной)
        if (heavy[v] != -1) {
            decompose(heavy[v], h)
        }

        // Потом по лёгким рёбрам (начинаем новые цепи)
        for (u in adj[v]) {
            if (u != parent[v] && u != heavy[v]) {
                decompose(u, u)  // u — новая голова цепи
            }
        }
    }

    fun build(root: Int = 0) {
        dfs(root)
        decompose(root, root)
    }

    /**
     * Запрос на пути от u до v
     * (здесь: сумма значений на пути)
     */
    fun queryPath(u: Int, v: Int, segmentTree: SegmentTree): Long {
        var a = u
        var b = v
        var result = 0L

        while (head[a] != head[b]) {
            // Поднимаем вершину с большей глубиной головы
            if (depth[head[a]] < depth[head[b]]) {
                val temp = a; a = b; b = temp
            }

            // Запрос на текущей цепи: от head[a] до a
            result += segmentTree.query(pos[head[a]], pos[a])

            // Переходим к родителю головы цепи
            a = parent[head[a]]
        }

        // a и b в одной цепи
        if (depth[a] > depth[b]) {
            val temp = a; a = b; b = temp
        }
        result += segmentTree.query(pos[a], pos[b])

        return result
    }
}

// ВИЗУАЛИЗАЦИЯ HLD:
//
// Дерево:           После HLD:
//       1                 1 (цепь 1)
//      /|\                |
//     2 3 4              2 (цепь 1)
//    /|   |              |
//   5 6   7             5 (цепь 1)
//   |
//   8                   3,4,6,7,8 — отдельные лёгкие вершины
//
// Тяжёлые рёбра: 1→2, 2→5
// Цепь 1: [1, 2, 5] (нумерация в дереве отрезков: 0, 1, 2)
//
// Любой путь пересекает O(log n) цепей!
```

---

## 8.2 Centroid Decomposition

```kotlin
/**
 * CENTROID DECOMPOSITION — divide & conquer на деревьях
 *
 * Центроид — вершина, при удалении которой все поддеревья имеют ≤ n/2 вершин
 *
 * Идея:
 * 1. Находим центроид
 * 2. Решаем задачу для путей через центроид
 * 3. Удаляем центроид и рекурсивно обрабатываем поддеревья
 *
 * Глубина рекурсии: O(log n)
 * Каждая вершина обрабатывается O(log n) раз
 */

class CentroidDecomposition(private val n: Int) {
    private val adj = Array(n) { mutableListOf<Int>() }
    private val subtreeSize = IntArray(n)
    private val removed = BooleanArray(n)  // Удалённые центроиды

    // Результат: дерево центроидов
    private val centroidParent = IntArray(n) { -1 }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)
    }

    /**
     * Вычисляем размеры поддеревьев
     */
    private fun calcSize(v: Int, parent: Int): Int {
        subtreeSize[v] = 1
        for (u in adj[v]) {
            if (u != parent && !removed[u]) {
                subtreeSize[v] += calcSize(u, v)
            }
        }
        return subtreeSize[v]
    }

    /**
     * Находим центроид поддерева
     */
    private fun findCentroid(v: Int, parent: Int, treeSize: Int): Int {
        for (u in adj[v]) {
            if (u != parent && !removed[u] && subtreeSize[u] > treeSize / 2) {
                return findCentroid(u, v, treeSize)
            }
        }
        return v
    }

    /**
     * Строим дерево центроидов
     */
    fun build(v: Int = 0, parent: Int = -1): Int {
        // Вычисляем размеры
        val treeSize = calcSize(v, -1)

        // Находим центроид
        val centroid = findCentroid(v, -1, treeSize)

        // Устанавливаем родителя в дереве центроидов
        centroidParent[centroid] = parent

        // Помечаем центроид как удалённый
        removed[centroid] = true

        // Рекурсивно обрабатываем поддеревья
        for (u in adj[centroid]) {
            if (!removed[u]) {
                build(u, centroid)
            }
        }

        return centroid
    }

    /**
     * Пример задачи: найти количество путей длины k
     * (здесь упрощённая версия — подсчёт расстояний от центроида)
     */
    fun solve(root: Int) {
        build(root)

        // Для каждого запроса:
        // 1. Поднимаемся по дереву центроидов от v
        // 2. На каждом уровне запрашиваем информацию
        // Всего O(log n) уровней!
    }
}

// ПРИМЕР использования:
//
// Задача: для каждой пары вершин (u, v) найти расстояние
//
// Наивно: O(n²)
// С Centroid Decomposition: O(n log n)
//
// Для каждого центроида:
// 1. BFS/DFS от центроида, считаем расстояния до всех вершин поддерева
// 2. Пути через центроид = dist[u] + dist[v]
// 3. Обрабатываем все такие пары
// 4. Удаляем центроид и рекурсивно обрабатываем поддеревья
```

---

# ЗАКЛЮЧЕНИЕ

## Что изучать дальше?

1. **Более сложные строковые алгоритмы** — Suffix Automaton, Aho-Corasick
2. **Min-Cost Max-Flow** — потоки минимальной стоимости
3. **Матричное возведение в степень** — линейные рекуррентности
4. **Persistent Data Structures** — версионные структуры данных
5. **Link-Cut Trees** — динамическая связность в деревьях
6. **Randomized Algorithms** — Treap, Skip List

---

# ЧАСТЬ 9: ВЫЧИСЛИТЕЛЬНАЯ ГЕОМЕТРИЯ

## 9.1 Базовые операции с векторами

```kotlin
import kotlin.math.*

/**
 * ВЕКТОР В 2D — основа вычислительной геометрии
 *
 * Точка (x, y) и вектор (x, y) — математически одно и то же,
 * но интерпретация разная:
 * - Точка: позиция в пространстве
 * - Вектор: направление и длина
 */

data class Point(val x: Double, val y: Double) {
    // Сложение векторов: (a.x + b.x, a.y + b.y)
    operator fun plus(other: Point) = Point(x + other.x, y + other.y)

    // Вычитание: создаёт вектор от other к this
    operator fun minus(other: Point) = Point(x - other.x, y - other.y)

    // Умножение на скаляр
    operator fun times(k: Double) = Point(x * k, y * k)

    // Длина вектора: √(x² + y²)
    fun length() = sqrt(x * x + y * y)

    // Расстояние до другой точки
    fun distTo(other: Point) = (this - other).length()
}

/**
 * СКАЛЯРНОЕ ПРОИЗВЕДЕНИЕ (Dot Product)
 *
 * a · b = |a| * |b| * cos(θ)
 *       = a.x * b.x + a.y * b.y
 *
 * Применение:
 * - Угол между векторами: cos(θ) = (a · b) / (|a| * |b|)
 * - Проекция вектора на другой
 * - Проверка перпендикулярности: a · b = 0
 */
fun dot(a: Point, b: Point): Double {
    return a.x * b.x + a.y * b.y
}

// ПРИМЕР:
// a = (3, 0), b = (0, 4)
// dot(a, b) = 3*0 + 0*4 = 0 → векторы перпендикулярны!
//
// a = (1, 0), b = (1, 1)
// dot(a, b) = 1*1 + 0*1 = 1
// cos(θ) = 1 / (1 * √2) = 1/√2 → θ = 45°


/**
 * ВЕКТОРНОЕ ПРОИЗВЕДЕНИЕ (Cross Product)
 *
 * a × b = |a| * |b| * sin(θ)
 *       = a.x * b.y - a.y * b.x
 *
 * Геометрический смысл: площадь параллелограмма × знак
 *
 * Знак показывает ориентацию:
 * - > 0: b слева от a (против часовой стрелки)
 * - < 0: b справа от a (по часовой стрелке)
 * - = 0: a и b коллинеарны (на одной прямой)
 */
fun cross(a: Point, b: Point): Double {
    return a.x * b.y - a.y * b.x
}

// ПРИМЕР:
// a = (1, 0), b = (0, 1)
// cross(a, b) = 1*1 - 0*0 = 1 > 0 → b слева от a
//
// a = (1, 0), b = (0, -1)
// cross(a, b) = 1*(-1) - 0*0 = -1 < 0 → b справа от a


/**
 * ОРИЕНТАЦИЯ ТРОЙКИ ТОЧЕК
 *
 * Определяет, как расположены три точки относительно друг друга:
 * - По часовой стрелке (CW)
 * - Против часовой (CCW)
 * - На одной линии (коллинеарны)
 */
enum class Orientation { CCW, CW, COLLINEAR }

fun orientation(a: Point, b: Point, c: Point): Orientation {
    // Вектор AB
    val ab = b - a
    // Вектор AC
    val ac = c - a

    // Знак векторного произведения определяет ориентацию
    val crossProduct = cross(ab, ac)

    return when {
        crossProduct > 1e-9 -> Orientation.CCW  // Против часовой
        crossProduct < -1e-9 -> Orientation.CW   // По часовой
        else -> Orientation.COLLINEAR            // На одной линии
    }
}

// ВИЗУАЛИЗАЦИЯ:
//
// CCW (против часовой):    CW (по часовой):      COLLINEAR:
//       C                       B                  A---B---C
//      /                       /
//     /                       /
//    A----B                  A----C
```

---

## 9.2 Выпуклая оболочка (Convex Hull)

```kotlin
/**
 * ВЫПУКЛАЯ ОБОЛОЧКА — минимальный выпуклый многоугольник,
 *                     содержащий все точки
 *
 * Представьте резинку, натянутую вокруг гвоздей —
 * это и есть выпуклая оболочка!
 *
 * Алгоритм Эндрю (Monotone Chain):
 * 1. Сортируем точки по x (при равенстве по y)
 * 2. Строим нижнюю оболочку слева направо
 * 3. Строим верхнюю оболочку справа налево
 * 4. Объединяем
 *
 * Сложность: O(n log n) из-за сортировки
 */
fun convexHull(points: List<Point>): List<Point> {
    val n = points.size
    if (n < 3) return points

    // Шаг 1: Сортируем по x, при равенстве по y
    val sorted = points.sortedWith(compareBy({ it.x }, { it.y }))

    // Функция для построения половины оболочки
    // direction: true = нижняя (по часовой), false = верхняя (против часовой)
    fun buildHalf(pts: List<Point>): MutableList<Point> {
        val hull = mutableListOf<Point>()

        for (p in pts) {
            // Пока последние две точки и новая образуют "неправильный" поворот
            // (для нижней — не по часовой, для верхней — по часовой)
            while (hull.size >= 2 &&
                   orientation(hull[hull.size - 2], hull[hull.size - 1], p) != Orientation.CW) {
                hull.removeAt(hull.size - 1)  // Удаляем среднюю точку
            }
            hull.add(p)
        }

        return hull
    }

    // Шаг 2: Строим нижнюю оболочку (слева направо)
    val lower = buildHalf(sorted)

    // Шаг 3: Строим верхнюю оболочку (справа налево)
    // Меняем условие: CCW вместо CW
    val upper = mutableListOf<Point>()
    for (p in sorted.reversed()) {
        while (upper.size >= 2 &&
               orientation(upper[upper.size - 2], upper[upper.size - 1], p) != Orientation.CW) {
            upper.removeAt(upper.size - 1)
        }
        upper.add(p)
    }

    // Шаг 4: Объединяем (убираем дублирующиеся концевые точки)
    lower.removeAt(lower.size - 1)
    upper.removeAt(upper.size - 1)

    return lower + upper
}

// ПОШАГОВЫЙ ПРИМЕР:
// Точки: A(0,0), B(2,2), C(4,0), D(2,1), E(1,1)
//
// После сортировки: A(0,0), E(1,1), D(2,1), B(2,2), C(4,0)
//
// Нижняя оболочка (CW повороты):
// 1. Добавляем A: [A]
// 2. Добавляем E: [A, E] — поворот ещё не определён
// 3. Добавляем D: [A, E, D]
//    Проверяем AED: CCW → удаляем E
//    [A, D]
// 4. Добавляем B: [A, D, B]
//    Проверяем ADB: CCW → удаляем D
//    [A, B]
// 5. Добавляем C: [A, B, C]
//    Проверяем ABC: CW → оставляем
//
// Нижняя: [A, B, C]
//
// Верхняя оболочка (справа налево):
// Аналогично получаем [C, A]
//
// Результат: [A, B, C, A] → убираем дубли → [A, B, C]
// Это треугольник!
```

---

## 9.3 Точка внутри многоугольника

```kotlin
/**
 * ТОЧКА ВНУТРИ МНОГОУГОЛЬНИКА — проверка принадлежности
 *
 * Алгоритм Ray Casting:
 * 1. Выпускаем луч из точки вправо (до бесконечности)
 * 2. Считаем пересечения с рёбрами многоугольника
 * 3. Нечётное число пересечений → внутри, чётное → снаружи
 *
 * Почему работает: каждый раз когда луч входит/выходит из многоугольника,
 * он пересекает ровно одно ребро
 */
fun isInsidePolygon(point: Point, polygon: List<Point>): Boolean {
    val n = polygon.size
    var crossings = 0

    for (i in 0 until n) {
        val a = polygon[i]
        val b = polygon[(i + 1) % n]

        // Проверяем, пересекает ли горизонтальный луч вправо от point ребро a-b

        // Условия пересечения:
        // 1. Ребро должно пересекать горизонталь y = point.y
        // 2. Точка пересечения должна быть справа от point

        // Проверка 1: ребро пересекает горизонталь
        if ((a.y <= point.y && b.y > point.y) ||  // ребро идёт вверх
            (b.y <= point.y && a.y > point.y)) {  // ребро идёт вниз

            // Вычисляем x-координату пересечения
            // Параметрическое уравнение: x = a.x + t * (b.x - a.x)
            // где t = (point.y - a.y) / (b.y - a.y)
            val t = (point.y - a.y) / (b.y - a.y)
            val xIntersect = a.x + t * (b.x - a.x)

            // Проверка 2: пересечение справа от точки
            if (point.x < xIntersect) {
                crossings++
            }
        }
    }

    return crossings % 2 == 1  // Нечётное = внутри
}

// ВИЗУАЛИЗАЦИЯ:
//
// Многоугольник:       Луч из P:
//    ┌───┐               ┌───┐
//    │   │           P ──│───│──→
//    │   │               │   │
//    └───┘               └───┘
//
// Луч пересекает 2 ребра → чётное → снаружи
//
//    ┌───┐               ┌───┐
//    │ P │           ────│─P─│──→
//    │   │               │   │
//    └───┘               └───┘
//
// Луч пересекает 1 ребро → нечётное → внутри


/**
 * Для выпуклого многоугольника можно проверить быстрее:
 * Точка внутри ⟺ она "слева" от всех рёбер (при обходе против часовой)
 */
fun isInsideConvex(point: Point, convexPolygon: List<Point>): Boolean {
    val n = convexPolygon.size

    for (i in 0 until n) {
        val a = convexPolygon[i]
        val b = convexPolygon[(i + 1) % n]

        // Если точка справа от какого-либо ребра — она снаружи
        if (orientation(a, b, point) == Orientation.CW) {
            return false
        }
    }

    return true
}
```

---

## 9.4 Площадь многоугольника (формула шнурков)

```kotlin
/**
 * ФОРМУЛА ШНУРКОВ (Shoelace Formula)
 *
 * Площадь многоугольника = (1/2) * |Σ(x[i] * y[i+1] - x[i+1] * y[i])|
 *
 * Почему "шнурков"? Вычисления похожи на перекрещивание шнурков:
 *
 *   x₀  y₀
 *    ╲╱
 *   x₁  y₁
 *    ╲╱
 *   x₂  y₂
 *    ...
 *
 * Это сумма векторных произведений соседних точек
 */
fun polygonArea(polygon: List<Point>): Double {
    val n = polygon.size
    var area = 0.0

    for (i in 0 until n) {
        val current = polygon[i]
        val next = polygon[(i + 1) % n]

        // Добавляем "перекрёстное" произведение
        area += current.x * next.y
        area -= next.x * current.y
    }

    // Берём модуль и делим на 2
    return abs(area) / 2.0
}

// ПОШАГОВЫЙ ПРИМЕР:
// Треугольник: (0,0), (4,0), (2,3)
//
// i=0: (0,0) → (4,0): area += 0*0 - 4*0 = 0
// i=1: (4,0) → (2,3): area += 4*3 - 2*0 = 12
// i=2: (2,3) → (0,0): area += 2*0 - 0*3 = 0
//
// area = 12, |area|/2 = 6
//
// Проверка: основание = 4, высота = 3
// Площадь = 4*3/2 = 6 ✓


/**
 * ЗНАКОВАЯ ПЛОЩАДЬ — определяет ориентацию многоугольника
 *
 * > 0: вершины против часовой стрелки (CCW)
 * < 0: вершины по часовой стрелке (CW)
 */
fun signedPolygonArea(polygon: List<Point>): Double {
    val n = polygon.size
    var area = 0.0

    for (i in 0 until n) {
        val current = polygon[i]
        val next = polygon[(i + 1) % n]
        area += cross(current, next)
    }

    return area / 2.0
}

// Если signedArea > 0 → CCW, < 0 → CW
// Это полезно для определения ориентации многоугольника
```

---

## 9.5 Пересечение отрезков

```kotlin
/**
 * ПЕРЕСЕЧЕНИЕ ОТРЕЗКОВ — проверка и нахождение точки пересечения
 *
 * Два отрезка AB и CD пересекаются если:
 * 1. Ориентации (A,B,C) и (A,B,D) разные (C и D по разные стороны от AB)
 * 2. Ориентации (C,D,A) и (C,D,B) разные (A и B по разные стороны от CD)
 *
 * Особый случай: коллинеарные отрезки (на одной прямой)
 */
fun segmentsIntersect(a: Point, b: Point, c: Point, d: Point): Boolean {
    val o1 = orientation(a, b, c)
    val o2 = orientation(a, b, d)
    val o3 = orientation(c, d, a)
    val o4 = orientation(c, d, b)

    // Общий случай: разные ориентации
    if (o1 != o2 && o3 != o4) {
        return true
    }

    // Особые случаи: коллинеарные точки
    // Проверяем, лежит ли точка на отрезке

    fun onSegment(p: Point, q: Point, r: Point): Boolean {
        return q.x <= maxOf(p.x, r.x) && q.x >= minOf(p.x, r.x) &&
               q.y <= maxOf(p.y, r.y) && q.y >= minOf(p.y, r.y)
    }

    if (o1 == Orientation.COLLINEAR && onSegment(a, c, b)) return true
    if (o2 == Orientation.COLLINEAR && onSegment(a, d, b)) return true
    if (o3 == Orientation.COLLINEAR && onSegment(c, a, d)) return true
    if (o4 == Orientation.COLLINEAR && onSegment(c, b, d)) return true

    return false
}


/**
 * ТОЧКА ПЕРЕСЕЧЕНИЯ — вычисление координат
 *
 * Параметрическое представление прямых:
 * P = A + t * (B - A)
 * P = C + u * (D - C)
 *
 * Решаем систему для t и u
 */
fun lineIntersection(a: Point, b: Point, c: Point, d: Point): Point? {
    val ab = b - a
    val cd = d - c
    val ac = c - a

    val denom = cross(ab, cd)

    // Параллельные прямые
    if (abs(denom) < 1e-9) return null

    val t = cross(ac, cd) / denom

    // Точка пересечения
    return a + ab * t
}

// ПРИМЕР:
// Отрезок 1: (0,0) → (2,2)
// Отрезок 2: (0,2) → (2,0)
//
// ab = (2,2), cd = (2,-2), ac = (0,2)
// denom = cross((2,2), (2,-2)) = 2*(-2) - 2*2 = -8
// t = cross((0,2), (2,-2)) / (-8) = (0*(-2) - 2*2) / (-8) = 4/8 = 0.5
//
// Точка: (0,0) + 0.5 * (2,2) = (1, 1)
```

---

## Главные идеи

| Техника | Когда применять | Сложность |
|---------|-----------------|-----------|
| Хеширование строк | Сравнение подстрок за O(1) | O(n) build, O(1) query |
| Z-функция / KMP | Поиск паттерна, периодичность | O(n + m) |
| Suffix Array | Поиск подстроки, LCP | O(n log n) build |
| Interval DP | Оптимальное разбиение отрезка | O(n³) обычно |
| Bitmask DP | Подмножества, n ≤ 20 | O(2ⁿ × n) |
| Tree DP | DP на структуре дерева | O(n) |
| CHT | Минимум линейных функций | O(n) или O(log n) |
| SOS DP | Сумма по подмножествам | O(n × 2ⁿ) |
| Max Flow | Потоки в сетях | O(V² × E) Dinic |
| FFT/NTT | Умножение многочленов | O(n log n) |
| HLD | Запросы на путях | O(log² n) query |
| Centroid | Divide & conquer на деревьях | O(n log n) |
| Convex Hull | Выпуклая оболочка | O(n log n) |
| Cross Product | Ориентация, площади | O(1) |

## Финальные советы

1. **Понимай, не заучивай** — понимание алгоритма важнее заучивания кода
2. **Трассируй вручную** — прежде чем кодить, пройди алгоритм на бумаге
3. **Тестируй на малых примерах** — отладка на n=3 проще чем на n=10⁵
4. **Читай editorials** — после контеста всегда разбирай решения
5. **Веди заметки** — записывай новые техники и типичные ошибки
6. **Практикуйся регулярно** — даже 30 минут в день дадут результат

## Путь обучения

```
Начинающий (0-800):
├── Базовый синтаксис
├── Простые циклы и условия
├── Работа с массивами
└── Сортировка и поиск

Новичок (800-1200):
├── STL/стандартная библиотека
├── Бинарный поиск
├── Two pointers
├── Простое DP
└── BFS/DFS

Ученик (1200-1400):
├── Продвинутое DP
├── Графы (Dijkstra, DSU)
├── Segment Tree
├── Divide & Conquer
└── Математика (mod, gcd)

Специалист (1400-1600):
├── Строковые алгоритмы
├── Продвинутые DS (Fenwick, Sparse Table)
├── Bitmask DP
├── Геометрия основы
└── Number Theory

Эксперт (1600-1900):
├── FFT/NTT
├── Max Flow
├── HLD, Centroid
├── Advanced Geometry
└── Suffix structures

Мастер (1900+):
├── Persistent DS
├── Link-Cut Trees
├── Advanced Flow
├── Combinatorics
└── Game Theory
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужно заучить все алгоритмы" | Важно **понимать паттерны**, а не зубрить код. Понимание позволяет адаптировать под задачу |
| "Competitive programming = интервью" | CP алгоритмы часто **сложнее** интервью. Фокус на скорости кодирования и edge cases |
| "Сложный алгоритм = лучшее решение" | Часто **простое решение** эффективнее. Добавляй сложность только когда нужно |
| "Оптимальное время = правильный ответ" | TLE/WA часто из-за **константного фактора** или corner cases, не complexity |
| "Хороший рейтинг = хороший программист" | CP — узкий навык. Production код требует **другие навыки** (testing, maintainability) |

---

## CS-фундамент

| CS-концепция | Применение в Competitive Programming |
|--------------|-------------------------------------|
| **Time Complexity Analysis** | Выбор алгоритма под ограничения: n≤10³ → O(n²), n≤10⁵ → O(n log n), n≤10⁶ → O(n) |
| **Amortized Analysis** | DSU с path compression: отдельные операции O(n), но M операций O(M·α(n)) |
| **Divide and Conquer** | Merge Sort, Binary Search, Segment Tree. Разбиение задачи на подзадачи |
| **Dynamic Programming** | Оптимальная подструктура + overlapping subproblems. Memoization vs tabulation |
| **Graph Theory** | BFS/DFS, shortest paths, spanning trees, topological sort. Моделирование задач графами |

---

*Этот документ охватывает все основные алгоритмы competitive programming с детальными объяснениями каждой строки кода. Используй его как справочник при изучении и практике.*

---

*Последнее обновление: 2026-01-09 — Проверено, соответствует педагогическому стандарту*
