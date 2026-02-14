---
title: "Советы по реализации для соревнований"
created: 2026-02-09
modified: 2026-02-13
type: guide
status: published
tags:
  - topic/cs-fundamentals
  - type/guide
  - level/intermediate
related:
  - "[[competitive-programming-overview]]"
  - "[[contest-strategy]]"
prerequisites:
  - "[[arrays-strings]]"
  - "[[big-o-complexity]]"
reading_time: 51
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Implementation Tips

## TL;DR

Быстрая реализация — 25% успеха в CP. Критичные навыки: **Fast I/O** (BufferedReader в 5x быстрее Scanner), **template** (готовый код экономит 5-10 мин), **debugging tricks** (print + binary search по коммитам). Код должен быть простым, не элегантным.

---

## Интуиция

### Аналогия 1: Template как инструменты хирурга

```
ХИРУРГ НЕ ИЩЕТ СКАЛЬПЕЛЬ ВО ВРЕМЯ ОПЕРАЦИИ:

Всё готово заранее:
• Инструменты стерилизованы
• Разложены в правильном порядке
• Ассистент знает что подавать

CP template = хирургический набор:
• Fast I/O готов
• DSU/SegTree под рукой
• Функции-хелперы написаны

Время контеста — на РЕШЕНИЕ, не на boilerplate.
```

### Аналогия 2: Простой код как IKEA инструкция

```
ХОРОШИЙ КОД НА КОНТЕСТЕ ≠ ХОРОШИЙ КОД НА РАБОТЕ:

На работе:              На контесте:
• Clean code            • Работающий код
• Читаемость            • Скорость написания
• Масштабируемость      • Правильность

CP код как инструкция IKEA:
• Простые шаги
• Минимум деталей
• Легко проверить

Элегантность — враг скорости.
```

---

## Частые ошибки

### Ошибка 1: Scanner вместо BufferedReader

**СИМПТОМ:** TLE на задачах с большим вводом (N > 10^5)

```kotlin
// МЕДЛЕННО: Scanner использует regex
val sc = Scanner(System.`in`)
val n = sc.nextInt()  // ~2.5 сек на 10^6 чисел

// БЫСТРО: BufferedReader читает блоками
val br = System.`in`.bufferedReader()
val n = br.readLine().toInt()  // ~0.5 сек (5x быстрее!)
```

**РЕШЕНИЕ:** Всегда BufferedReader для N > 10^4.

### Ошибка 2: Забыть flush() для PrintWriter

**СИМПТОМ:** Пустой вывод, WA при правильном решении

```kotlin
val bw = PrintWriter(System.out)
bw.println(answer)
// Программа завершилась, но данные в буфере!

// ОБЯЗАТЕЛЬНО в конце:
bw.flush()  // или bw.close()
```

**РЕШЕНИЕ:** flush() в конце main() — обязательно.

### Ошибка 3: Сложный код вместо простого

**СИМПТОМ:** Баги из-за умных оптимизаций, сложно дебажить

```kotlin
// ПЛОХО: Умно, но баг не найти
val result = arr.asSequence()
    .filter { it > 0 }
    .map { it * 2 }
    .fold(0L) { acc, x -> (acc + x) % MOD }

// ХОРОШО: Просто, легко дебажить
var result = 0L
for (x in arr) {
    if (x > 0) {
        result = (result + x * 2) % MOD
    }
}
```

**РЕШЕНИЕ:** KISS — Keep It Stupid Simple.

---

## Ментальные модели

### Модель 1: "Copy-paste > DRY"

```
НА РАБОТЕ: Don't Repeat Yourself
НА КОНТЕСТЕ: Copy-paste быстрее

Вместо:
fun helper(arr, transform) = arr.map(transform)

Просто:
// Для первого случая
for (x in arr1) result1 += x * 2
// Для второго случая
for (x in arr2) result2 += x + 1

Абстракции добавляют баги.
Дублирование — это ОК на контесте.
```

### Модель 2: "Debug через print"

```
СТРАТЕГИЯ ОТЛАДКИ:

1. Print входные данные (убедись что читаешь правильно)
2. Print промежуточные состояния
3. Binary search по коду:
   • Работает до строки X? → Да
   • Работает до строки Y? → Нет
   • Баг между X и Y!

Print debug > IDE debugger на контесте.
```

---

## 1. Fast I/O

### Почему это важно

В задачах с большим вводом (10^5 - 10^6 элементов) стандартный I/O может быть bottleneck. Разница между медленным и быстрым I/O — от TLE до AC.

### Kotlin Fast I/O

```kotlin
/**
 * БАЗОВЫЙ БЫСТРЫЙ ВВОД
 *
 * Почему BufferedReader, а не Scanner?
 * ────────────────────────────────────
 * Scanner:
 * - Парсит каждый токен регулярными выражениями
 * - Синхронизирован (thread-safe, но медленнее)
 * - ~2.5 секунд на 10^6 чисел
 *
 * BufferedReader:
 * - Читает большими блоками (буфер 8KB по умолчанию)
 * - Минимум системных вызовов
 * - ~0.5 секунд на 10^6 чисел (5x быстрее!)
 *
 * ВЫВОД: Для N > 10^4 всегда используй BufferedReader
 */

import java.io.BufferedReader
import java.io.PrintWriter

fun main() {
    val br = System.`in`.bufferedReader()
    val bw = PrintWriter(System.out)

    /**
     * StringTokenizer vs split(" ")
     * ─────────────────────────────
     * split(" "):
     * - Создает массив строк
     * - Использует регулярные выражения
     * - Выделяет много памяти
     *
     * StringTokenizer:
     * - Итератор (не создает массив сразу)
     * - Простое разделение по пробелам
     * - Быстрее на 30-50% для больших строк
     */
    val st = java.util.StringTokenizer(br.readLine())
    val n = st.nextToken().toInt()
    val arr = IntArray(n) { st.nextToken().toInt() }

    bw.println(arr.sum())

    /**
     * КРИТИЧНО: flush() в конце!
     * ─────────────────────────
     * PrintWriter буферизует вывод. Без flush():
     * - Данные остаются в буфере
     * - Программа завершается → данные теряются
     * - Judge получает пустой вывод → WA
     *
     * АЛЬТЕРНАТИВА: PrintWriter(System.out, true) — autoflush,
     * но это МЕДЛЕННЕЕ (flush после каждого println)
     */
    bw.flush()
}

// === Удобный template с функциями-хелперами ===

/**
 * @JvmField — зачем это нужно?
 * ────────────────────────────
 * В Kotlin top-level val компилируется в:
 * - private static field + public static getter
 *
 * Каждый вызов br.readLine() → getBr().readLine()
 * В горячих циклах это лишний overhead!
 *
 * @JvmField говорит компилятору:
 * - Сделать поле public static без getter
 * - Прямой доступ к полю, без вызова метода
 *
 * Экономия: ~5-10% на задачах с интенсивным I/O
 */
@JvmField val br = System.`in`.bufferedReader()
@JvmField val bw = java.io.PrintWriter(System.out)

fun readLine(): String = br.readLine()
fun readInt() = readLine().toInt()
fun readLong() = readLine().toLong()
fun readInts() = readLine().split(" ").map { it.toInt() }
fun readLongs() = readLine().split(" ").map { it.toLong() }

// Для очень большого ввода — StringTokenizer
fun readIntsFast(): IntArray {
    val st = java.util.StringTokenizer(readLine())
    return IntArray(st.countTokens()) { st.nextToken().toInt() }
}

fun main() {
    val n = readInt()
    val arr = readIntsFast()

    bw.println(arr.max())
    bw.flush()
}
```

### Java Fast I/O

```java
/**
 * FastReader класс (РЕКОМЕНДУЕТСЯ)
 *
 * Зачем нужен свой класс вместо Scanner?
 * ──────────────────────────────────────
 * Scanner — удобный, но медленный:
 * - nextInt(), nextLong() парсят через regex
 * - Синхронизирован для thread-safety
 *
 * FastReader — лучшее из двух миров:
 * - BufferedReader для быстрого чтения
 * - StringTokenizer для разбора строки
 * - Удобный API: nextInt(), nextLong()
 *
 * ПРОИЗВОДИТЕЛЬНОСТЬ:
 * Scanner:    ~2.5 сек на 10^6 чисел
 * FastReader: ~0.5 сек на 10^6 чисел
 */

import java.io.*;
import java.util.*;

public class Main {
    static BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    static StringTokenizer st;

    static String next() throws IOException {
        while (st == null || !st.hasMoreTokens())
            st = new StringTokenizer(br.readLine());
        return st.nextToken();
    }

    static int nextInt() throws IOException { return Integer.parseInt(next()); }
    static long nextLong() throws IOException { return Long.parseLong(next()); }
    static double nextDouble() throws IOException { return Double.parseDouble(next()); }

    public static void main(String[] args) throws IOException {
        int n = nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = nextInt();

        out.println(Arrays.stream(arr).sum());

        // КРИТИЧНО! Без flush данные останутся в буфере и не выведутся
        out.flush();
    }
}
```

### C++ Fast I/O

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    /**
     * УСКОРЕНИЕ C++ I/O
     *
     * sync_with_stdio(false):
     * ───────────────────────
     * По умолчанию C++ streams синхронизированы с C stdio (printf/scanf).
     * Это позволяет смешивать cout и printf в одной программе,
     * но добавляет overhead на каждую операцию I/O.
     *
     * Отключение синхронизации:
     * - cin/cout работают независимо от stdin/stdout
     * - Ускорение в 3-4 раза!
     * - ВАЖНО: После этого нельзя использовать printf/scanf!
     */
    ios_base::sync_with_stdio(false);

    /**
     * cin.tie(nullptr):
     * ──────────────────
     * По умолчанию cin "привязан" к cout:
     * - Перед каждым cin автоматически вызывается cout.flush()
     * - Нужно для интерактивных программ (ввод после вывода)
     *
     * В соревновательном программировании:
     * - Обычно читаем всё, потом выводим всё
     * - Автоматический flush не нужен — это лишний overhead
     * - tie(nullptr) отключает эту связь
     */
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> arr(n);
    for (int& x : arr) cin >> x;

    cout << accumulate(arr.begin(), arr.end(), 0LL) << '\n';

    return 0;
}

// ВАЖНО: После sync_with_stdio(false) НЕ использовать printf/scanf!
```

### Сравнение скорости

| Метод | Время (10^6 integers) |
|-------|----------------------|
| Scanner (Java) | ~2.5 сек |
| BufferedReader + StringTokenizer | ~0.5 сек |
| DataInputStream (custom) | ~0.3 сек |
| cin без оптимизации | ~1.5 сек |
| cin с sync_with_stdio(false) | ~0.4 сек |

---

## 2. Code Template

### Kotlin Competitive Template

```kotlin
@file:Suppress("NOTHING_TO_INLINE")

import java.io.*
import java.util.*

// === I/O ===
@JvmField val INPUT = System.`in`
@JvmField val OUTPUT = System.out
@JvmField val br = INPUT.bufferedReader()
@JvmField val bw = PrintWriter(OUTPUT, false)

fun readLine(): String = br.readLine()
fun readInt() = readLine().toInt()
fun readLong() = readLine().toLong()
fun readInts() = readLine().split(" ").map { it.toInt() }
fun readLongs() = readLine().split(" ").map { it.toLong() }

inline fun readIntArray(n: Int) = IntArray(n) { readInt() }
inline fun readLongArray(n: Int) = LongArray(n) { readLong() }

fun readIntsFast(): IntArray {
    val st = StringTokenizer(readLine())
    return IntArray(st.countTokens()) { st.nextToken().toInt() }
}

// === Constants ===
const val MOD = 1_000_000_007L
const val INF = Int.MAX_VALUE / 2
const val LINF = Long.MAX_VALUE / 2

// === Utility ===
inline fun <T> Iterable<T>.sumByLong(selector: (T) -> Long): Long {
    var sum = 0L
    for (element in this) sum += selector(element)
    return sum
}

// === Main ===
fun solve() {
    val n = readInt()
    val arr = readIntsFast()

    // Solution here

    bw.println("answer")
}

fun main() {
    val t = 1  // readInt() for multiple test cases
    repeat(t) { solve() }
    bw.flush()
}
```

### C++ Competitive Template

```cpp
#include <bits/stdc++.h>
using namespace std;

// === Type aliases ===
using ll = long long;
using ull = unsigned long long;
using pii = pair<int, int>;
using pll = pair<ll, ll>;
using vi = vector<int>;
using vll = vector<ll>;
using vvi = vector<vi>;
using vpii = vector<pii>;

// === Macros ===
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define sz(x) (int)(x).size()
#define pb push_back
#define eb emplace_back
#define fi first
#define se second

// === Constants ===
const int MOD = 1e9 + 7;
const int INF = 1e9;
const ll LINF = 1e18;

// === Debug ===
#ifdef LOCAL
#define debug(x) cerr << #x << " = " << (x) << endl
#else
#define debug(x)
#endif

// === I/O ===
template<typename T>
void read(vector<T>& v) { for (auto& x : v) cin >> x; }

template<typename T>
void print(const vector<T>& v, string sep = " ") {
    for (int i = 0; i < sz(v); i++) cout << v[i] << (i < sz(v)-1 ? sep : "\n");
}

void solve() {
    int n;
    cin >> n;
    vi a(n);
    read(a);

    // Solution here

    cout << "answer\n";
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int t = 1;
    // cin >> t;
    while (t--) solve();

    return 0;
}
```

---

## 3. Modular Arithmetic

### Зачем MOD = 10^9 + 7?

```
1. Первое 10-значное простое число
2. Помещается в int (2^30 ≈ 10^9)
3. Два числа можно умножить без overflow в long long
4. Простое → существует модульный обратный
```

### Базовые операции

```kotlin
const val MOD = 1_000_000_007L

/**
 * БЕЗОПАСНЫЙ ОСТАТОК ПО МОДУЛЮ
 *
 * Проблема: В Kotlin/Java оператор % сохраняет знак делимого:
 * - (-5) % 3 = -2  (а не 1!)
 * - (-7) % 4 = -3  (а не 1!)
 *
 * Для модульной арифметики нужен ПОЛОЖИТЕЛЬНЫЙ остаток:
 * - (-5) mod 3 = 1
 * - (-7) mod 4 = 1
 *
 * Формула: ((a % MOD) + MOD) % MOD
 * ────────────────────────────────
 * Шаг 1: a % MOD → может быть отрицательным (от -MOD+1 до MOD-1)
 * Шаг 2: + MOD   → сдвигаем в положительную область (от 1 до 2*MOD-1)
 * Шаг 3: % MOD   → нормализуем (от 0 до MOD-1)
 *
 * ПРИМЕР: a = -5, MOD = 3
 * (-5) % 3 = -2
 * -2 + 3 = 1
 * 1 % 3 = 1 ✓
 */
fun Long.mod() = ((this % MOD) + MOD) % MOD
fun Int.mod() = this.toLong().mod()

// Сложение
fun addMod(a: Long, b: Long): Long = (a + b).mod()

// Вычитание
fun subMod(a: Long, b: Long): Long = (a - b).mod()

// Умножение
fun mulMod(a: Long, b: Long): Long = (a * b).mod()
```

### Binary Exponentiation

```kotlin
/**
 * Быстрое возведение в степень по модулю
 *
 * Time: O(log n)
 *
 * WHY: a^n mod m вычисляется за log(n) умножений
 * используя свойство: a^n = (a^(n/2))^2 для четных n
 */
fun powMod(base: Long, exp: Long, mod: Long = MOD): Long {
    var result = 1L
    var b = base % mod
    var e = exp

    /**
     * БИНАРНОЕ ВОЗВЕДЕНИЕ В СТЕПЕНЬ
     *
     * Идея: представить exp в двоичной системе и использовать свойства степеней
     *
     * ПРИМЕР: 3^13 (exp = 13 = 1101₂)
     * ─────────────────────────────────
     * 13 = 8 + 4 + 1 = 2³ + 2² + 2⁰
     * 3^13 = 3^8 × 3^4 × 3^1
     *
     * Итерация:   e(двоич)   бит=1?   result        base
     * ───────────────────────────────────────────────────
     * Старт:      1101       -        1             3
     * i=0:        1101       ДА       1×3=3         3²=9
     * i=1:        0110       НЕТ      3             9²=81
     * i=2:        0011       ДА       3×81=243      81²=6561
     * i=3:        0001       ДА       243×6561      (не нужен)
     *
     * ИТОГО: 4 умножения вместо 12!
     */
    while (e > 0) {
        // Если младший бит exp равен 1, добавляем текущую степень в результат
        if (e and 1L == 1L) {
            result = (result * b) % mod
        }
        // base → base² (следующая степень двойки)
        // e → e/2 (сдвигаем биты вправо)
        b = (b * b) % mod
        e = e shr 1
    }

    return result
}

// Пример: 2^10 mod (10^9+7)
val result = powMod(2, 10)  // = 1024
```

### Modular Inverse (Обратный элемент)

```kotlin
/**
 * Модульный обратный элемент через теорему Ферма
 *
 * WHY: a^(-1) ≡ a^(p-2) (mod p) для простого p
 *
 * Применяется когда нужно "делить" по модулю:
 * (a / b) mod p = (a * b^(-1)) mod p
 */
fun modInverse(a: Long, mod: Long = MOD): Long {
    return powMod(a, mod - 2, mod)
}

// Деление по модулю
fun divMod(a: Long, b: Long): Long {
    return mulMod(a, modInverse(b))
}

// Пример: (10 / 2) mod (10^9+7)
val result = divMod(10, 2)  // = 5
```

### Factorial и Binomial Coefficients

```kotlin
/**
 * Предподсчет факториалов и обратных факториалов
 *
 * WHY: позволяет вычислять C(n, k) за O(1) после предподсчета
 */
class Combinatorics(maxN: Int) {
    private val fact = LongArray(maxN + 1)
    private val invFact = LongArray(maxN + 1)

    init {
        /**
         * ШАГ 1: Предподсчет факториалов
         * ──────────────────────────────
         * fact[i] = i! mod MOD
         *
         * Строим итеративно:
         * fact[0] = 1
         * fact[1] = 1 × 1 = 1
         * fact[2] = 1 × 2 = 2
         * fact[3] = 2 × 3 = 6
         * ...
         *
         * Сложность: O(n)
         */
        fact[0] = 1
        for (i in 1..maxN) {
            fact[i] = (fact[i - 1] * i) % MOD
        }

        /**
         * ШАГ 2: Обратный факториал через теорему Ферма
         * ──────────────────────────────────────────────
         * invFact[i] = (i!)^(-1) mod MOD
         *
         * Теорема Ферма: a^(-1) ≡ a^(p-2) mod p (для простого p)
         *
         * Оптимизация: вычисляем только invFact[maxN],
         * остальные получаем из рекуррентного соотношения
         */
        invFact[maxN] = modInverse(fact[maxN])

        /**
         * ШАГ 3: Заполнение обратных факториалов снизу вверх
         * ────────────────────────────────────────────────────
         * Используем соотношение:
         * (n-1)! = n! / n
         *
         * Для обратных:
         * ((n-1)!)^(-1) = (n!)^(-1) × n
         *
         * ПРИМЕР: n = 5
         * invFact[5] = (5!)^(-1)  (вычислили через Ферма)
         * invFact[4] = invFact[5] × 5 = (5!)^(-1) × 5 = (4!)^(-1)
         * invFact[3] = invFact[4] × 4 = (4!)^(-1) × 4 = (3!)^(-1)
         * ...
         *
         * Это O(n) вместо O(n × log p) если считать каждый через Ферма!
         */
        for (i in maxN - 1 downTo 0) {
            invFact[i] = (invFact[i + 1] * (i + 1)) % MOD
        }
    }

    /**
     * C(n, k) = n! / (k! * (n-k)!)
     */
    fun nCr(n: Int, k: Int): Long {
        if (k < 0 || k > n) return 0L
        return (fact[n] * invFact[k] % MOD) * invFact[n - k] % MOD
    }

    /**
     * P(n, k) = n! / (n-k)!
     */
    fun nPr(n: Int, k: Int): Long {
        if (k < 0 || k > n) return 0L
        return fact[n] * invFact[n - k] % MOD
    }

    fun factorial(n: Int) = fact[n]
}

// Использование:
val comb = Combinatorics(200_000)
println(comb.nCr(10, 3))  // = 120
```

---

## 4. Bit Manipulation

### Основные операции

```kotlin
// === Базовые битовые операции ===

// Проверить i-й бит
fun getBit(n: Int, i: Int): Boolean = (n shr i) and 1 == 1

// Установить i-й бит в 1
fun setBit(n: Int, i: Int): Int = n or (1 shl i)

// Сбросить i-й бит в 0
fun clearBit(n: Int, i: Int): Int = n and (1 shl i).inv()

// Переключить i-й бит
fun toggleBit(n: Int, i: Int): Int = n xor (1 shl i)

// Количество единичных битов
fun popcount(n: Int): Int = Integer.bitCount(n)

// Количество ведущих нулей
fun leadingZeros(n: Int): Int = Integer.numberOfLeadingZeros(n)

// Количество trailing нулей (позиция младшего бита)
fun trailingZeros(n: Int): Int = Integer.numberOfTrailingZeros(n)

// Позиция старшего бита (0-indexed, -1 если n=0)
fun highestBit(n: Int): Int = if (n == 0) -1 else 31 - Integer.numberOfLeadingZeros(n)
```

### Полезные трюки

```kotlin
// === Часто используемые bit tricks ===

// 1. Проверка на степень двойки
fun isPowerOfTwo(n: Int): Boolean = n > 0 && (n and (n - 1)) == 0

// 2. Округление до следующей степени двойки
fun nextPowerOfTwo(n: Int): Int {
    if (n <= 0) return 1
    var x = n - 1
    x = x or (x shr 1)
    x = x or (x shr 2)
    x = x or (x shr 4)
    x = x or (x shr 8)
    x = x or (x shr 16)
    return x + 1
}

// 3. Выделение младшего установленного бита
fun lowestSetBit(n: Int): Int = n and (-n)

// 4. Сброс младшего установленного бита
fun clearLowestSetBit(n: Int): Int = n and (n - 1)

// 5. Все биты справа от младшего установленного бита
fun rightPropagateLowest(n: Int): Int = n or (n - 1)

// 6. Swap без временной переменной
fun swap(a: Int, b: Int): Pair<Int, Int> {
    var x = a xor b
    val y = x xor b  // y = a
    x = x xor y      // x = b
    return Pair(x, y)
}

// 7. Абсолютное значение без ветвлений
fun absNoBranch(n: Int): Int {
    val mask = n shr 31
    return (n xor mask) - mask
}

// 8. Максимум без ветвлений
fun maxNoBranch(a: Int, b: Int): Int {
    return a - ((a - b) and ((a - b) shr 31))
}
```

### Перебор подмножеств

```kotlin
// === Итерация по подмножествам ===

/**
 * Перебор всех непустых подмножеств множества mask
 *
 * WHY: Важный паттерн для bitmask DP
 * Сложность: O(2^popcount(mask))
 */
fun iterateSubsets(mask: Int, action: (Int) -> Unit) {
    var subset = mask
    while (subset > 0) {
        action(subset)
        subset = (subset - 1) and mask
    }
}

// Пример: подмножества mask = 0b1011 = 11
// Выведет: 11, 10, 9, 8, 3, 2, 1
iterateSubsets(11) { println(it) }

/**
 * Перебор всех масок размера k из n битов
 */
fun iterateMasksOfSizeK(n: Int, k: Int, action: (Int) -> Unit) {
    if (k == 0) {
        action(0)
        return
    }

    var mask = (1 shl k) - 1  // Начинаем с k младших битов
    val maxMask = 1 shl n

    while (mask < maxMask) {
        action(mask)

        /**
         * GOSPER'S HACK — получение следующей комбинации с тем же числом битов
         *
         * ПРИМЕР: mask = 0b0110 (выбраны биты 1 и 2)
         * Хотим: следующая маска с 2 битами → 0b1001, 0b1010, 0b1100
         *
         * КАК ЭТО РАБОТАЕТ:
         * ─────────────────
         * 1. lowest = mask & (-mask)
         *    Выделяем младший установленный бит
         *    0b0110 & 0b1010 = 0b0010
         *
         * 2. ripple = mask + lowest
         *    Добавляем 1 к младшему биту — это "перенос"
         *    0b0110 + 0b0010 = 0b1000
         *
         * 3. ones = ((mask ^ ripple) >> 2) / lowest
         *    Вычисляем сколько единиц нужно вернуть в младшие биты
         *    mask ^ ripple = 0b1110 (изменённые биты)
         *    >> 2 / lowest — нормализация
         *
         * 4. mask = ripple | ones
         *    Объединяем: старший бит переноса + младшие единицы
         *
         * ПОСЛЕДОВАТЕЛЬНОСТЬ для n=4, k=2:
         * 0011 → 0101 → 0110 → 1001 → 1010 → 1100 → конец
         */
        val lowest = mask and (-mask)
        val ripple = mask + lowest
        val ones = ((mask xor ripple) shr 2) / lowest
        mask = ripple or ones
    }
}

// Пример: все маски размера 2 из 4 битов
// Выведет: 3, 5, 6, 9, 10, 12
iterateMasksOfSizeK(4, 2) { println(it) }
```

---

## 5. Debugging Techniques

### Debug Print Макросы

```kotlin
/**
 * DEBUG РЕЖИМ
 *
 * КРИТИЧНО: Выключить перед submit!
 * ─────────────────────────────────
 * DEBUG = true → вывод в System.err
 * DEBUG = false → код полностью удаляется компилятором (inline!)
 *
 * Почему System.err, а не System.out?
 * - System.out идёт в judge → может испортить ответ
 * - System.err не проверяется judge'ом
 * - На локальной машине оба видны в консоли
 *
 * ВАЖНО: На некоторых судьях вывод в stderr замедляет программу!
 * Поэтому DEBUG = false перед отправкой ОБЯЗАТЕЛЬНО
 */
const val DEBUG = true  // ← ВЫКЛЮЧИТЬ ПЕРЕД SUBMIT!

inline fun debug(vararg args: Any?) {
    if (DEBUG) {
        System.err.println(args.joinToString(" "))
    }
}

inline fun <T> T.dbg(): T {
    if (DEBUG) System.err.println("DBG: $this")
    return this
}

// Использование:
val result = someFunction(arr).dbg()  // Выведет результат
debug("n =", n, "arr =", arr.toList())
```

```cpp
// C++ debug macros
#ifdef LOCAL
#define debug(x) cerr << #x << " = " << (x) << endl
#define debugv(v) { cerr << #v << ": "; for(auto& x : v) cerr << x << " "; cerr << endl; }
#define debugm(m) { cerr << #m << ":\n"; for(auto& row : m) { for(auto& x : row) cerr << x << " "; cerr << endl; } }
#else
#define debug(x)
#define debugv(v)
#define debugm(m)
#endif
```

### Stress Testing

```kotlin
/**
 * Stress test framework
 *
 * WHY: находит минимальный тест, на котором решение даёт неправильный ответ
 */
object StressTest {
    private val random = java.util.Random()

    // Генерация случайного числа в диапазоне [l, r]
    fun randInt(l: Int, r: Int): Int = l + random.nextInt(r - l + 1)

    // Генерация случайного массива
    fun randArray(n: Int, l: Int, r: Int): IntArray {
        return IntArray(n) { randInt(l, r) }
    }

    // Генерация случайной перестановки
    fun randPermutation(n: Int): IntArray {
        val arr = IntArray(n) { it + 1 }
        for (i in n - 1 downTo 1) {
            val j = random.nextInt(i + 1)
            val tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp
        }
        return arr
    }

    // Генерация случайного дерева
    fun randTree(n: Int): List<Pair<Int, Int>> {
        val edges = mutableListOf<Pair<Int, Int>>()
        for (i in 2..n) {
            val parent = randInt(1, i - 1)
            edges.add(Pair(parent, i))
        }
        return edges
    }

    /**
     * Основная функция stress test
     */
    fun run(
        iterations: Int = 1000,
        generator: () -> Any,           // Генерирует входные данные
        bruteForce: (Any) -> Any,       // Медленное, но правильное решение
        optimized: (Any) -> Any         // Быстрое решение для тестирования
    ) {
        repeat(iterations) { i ->
            val input = generator()
            val expected = bruteForce(input)
            val actual = optimized(input)

            if (expected != actual) {
                System.err.println("FAILED on iteration $i!")
                System.err.println("Input: $input")
                System.err.println("Expected: $expected")
                System.err.println("Actual: $actual")
                return
            }

            if (i % 100 == 0) {
                System.err.println("Passed $i iterations...")
            }
        }
        System.err.println("All $iterations tests passed!")
    }
}

// Пример использования:
fun main() {
    StressTest.run(
        iterations = 10000,
        generator = {
            val n = StressTest.randInt(1, 100)
            StressTest.randArray(n, -100, 100)
        },
        bruteForce = { input ->
            val arr = input as IntArray
            arr.maxOrNull()  // O(n)
        },
        optimized = { input ->
            val arr = input as IntArray
            // Ваше оптимизированное решение
            arr.maxOrNull()
        }
    )
}
```

### Bash Stress Test Script

```bash
#!/bin/bash
# stress_test.sh

# WHY: автоматизированный stress test
# Компилируем все решения
g++ -O2 -o solution solution.cpp
g++ -O2 -o brute brute.cpp
g++ -O2 -o gen gen.cpp

for ((i = 1; ; i++)); do
    # Генерируем тест
    ./gen $i > test_input.txt

    # Запускаем оба решения
    ./solution < test_input.txt > solution_output.txt
    ./brute < test_input.txt > brute_output.txt

    # Сравниваем
    if ! diff -q solution_output.txt brute_output.txt > /dev/null; then
        echo "FAILED on test $i"
        echo "Input:"
        cat test_input.txt
        echo "Expected:"
        cat brute_output.txt
        echo "Actual:"
        cat solution_output.txt
        break
    fi

    if ((i % 100 == 0)); then
        echo "Passed $i tests..."
    fi
done
```

---

## 6. Common Idioms

### Частые паттерны

```kotlin
// === Array и коллекции ===

// Создание 2D массива
val grid = Array(n) { IntArray(m) }
val dp = Array(n) { LongArray(m) { -1L } }

// Подсчет элементов
val count = arr.groupingBy { it }.eachCount()

// Prefix sum
val prefix = LongArray(n + 1)
for (i in arr.indices) prefix[i + 1] = prefix[i] + arr[i]
// Сумма [l, r) = prefix[r] - prefix[l]

// Suffix sum
val suffix = LongArray(n + 1)
for (i in arr.indices.reversed()) suffix[i] = suffix[i + 1] + arr[i]

// Координатное сжатие
fun compress(arr: IntArray): Map<Int, Int> {
    return arr.toSortedSet().withIndex().associate { it.value to it.index }
}

// === Математика ===

// Безопасное деление с округлением вверх
fun ceilDiv(a: Long, b: Long): Long = (a + b - 1) / b

// GCD (встроенный)
fun gcd(a: Long, b: Long): Long = if (b == 0L) a else gcd(b, a % b)

/**
 * LCM — наименьшее общее кратное
 *
 * Формула: lcm(a, b) = a × b / gcd(a, b)
 *
 * ВАЖНО: порядок операций!
 * ────────────────────────
 * НЕПРАВИЛЬНО: a * b / gcd(a, b)
 *   - a * b может переполниться!
 *   - Пример: a = 10^9, b = 10^9 → a * b = 10^18 (overflow для Int!)
 *
 * ПРАВИЛЬНО: a / gcd(a, b) * b
 *   - Сначала делим — результат точный (gcd делит a нацело)
 *   - Потом умножаем — меньше шансов overflow
 *   - a / gcd ≤ a, поэтому (a / gcd) * b ≤ a * b
 */
fun lcm(a: Long, b: Long): Long = a / gcd(a, b) * b

// === Графы ===

/**
 * Список смежности — стандартное представление графа
 *
 * Почему 0-indexed?
 * ────────────────
 * Во входных данных вершины часто 1-indexed: "1 2 3 ... n"
 * В массивах индексы 0-indexed: arr[0], arr[1], ...
 *
 * Если не конвертировать:
 * - adj[0] будет пустым (вершины 1..n)
 * - adj[n] выйдет за границы (ArrayIndexOutOfBounds)
 *
 * Конвертация: читаем u, делаем u - 1
 * Теперь вершины 0..n-1 соответствуют arr[0..n-1]
 */
val adj = Array(n) { mutableListOf<Int>() }
repeat(m) {
    val (u, v) = readInts().map { it - 1 }  // 1-indexed → 0-indexed
    adj[u].add(v)
    adj[v].add(u)  // для неориентированного графа
}

// Взвешенный граф
data class Edge(val to: Int, val weight: Long)
val graph = Array(n) { mutableListOf<Edge>() }

// === Сортировка ===

// По нескольким ключам
data class Item(val a: Int, val b: Int)
val items = listOf(Item(1, 2), Item(2, 1))
items.sortedWith(compareBy({ it.a }, { -it.b }))

// Custom comparator
arr.sortedWith { x, y -> x.length - y.length }
```

### Частые ошибки и их решения

```kotlin
// === Integer Overflow ===
// BAD:
val sum = arr.sum()  // Возвращает Int!

// GOOD:
val sum = arr.sumOf { it.toLong() }

// === Off-by-one ===
// BAD:
for (i in 1..n) { ... }  // включает n

// GOOD (если нужны индексы 0..n-1):
for (i in 0 until n) { ... }
for (i in arr.indices) { ... }

// === Mutable collections ===
// BAD (copy reference):
val copy = list

// GOOD:
val copy = list.toMutableList()

// === String concatenation в цикле ===
// BAD:
var s = ""
repeat(n) { s += "x" }

// GOOD:
val sb = StringBuilder()
repeat(n) { sb.append("x") }
val s = sb.toString()

// или
val s = buildString { repeat(n) { append("x") } }
```

---

## 7. Data Structure Templates

### Disjoint Set Union (DSU)

```kotlin
/**
 * Union-Find / Disjoint Set Union
 *
 * Time: O(α(n)) ≈ O(1) amortized per operation
 */
class DSU(n: Int) {
    private val parent = IntArray(n) { it }
    private val rank = IntArray(n) { 0 }

    /**
     * FIND с PATH COMPRESSION (сжатие пути)
     *
     * Без сжатия пути:
     * ─────────────────
     * find(5): 5 → 4 → 3 → 2 → 1 → 0  (O(n) в худшем случае)
     *
     * Дерево:
     *     0
     *     ↑
     *     1
     *     ↑
     *     2
     *     ↑
     *     3
     *     ↑
     *     4
     *     ↑
     *     5
     *
     * С PATH COMPRESSION:
     * ─────────────────────
     * После find(5) все элементы на пути указывают прямо на корень:
     *
     *        0
     *   ↑  ↑  ↑  ↑  ↑
     *   1  2  3  4  5
     *
     * Теперь find(5) = O(1)!
     * Амортизированная сложность: O(α(n)) ≈ O(1)
     */
    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Рекурсивно сжимаем путь
        }
        return parent[x]
    }

    /**
     * UNION BY RANK (объединение по рангу)
     *
     * Проблема без ранга:
     * ───────────────────
     * Если всегда присоединять A к B:
     * union(0,1): 1 ← 0
     * union(1,2): 2 ← 1 ← 0
     * union(2,3): 3 ← 2 ← 1 ← 0
     * → Линейная цепочка, find = O(n)
     *
     * UNION BY RANK:
     * ──────────────
     * Присоединяем МЕНЬШЕЕ дерево к БОЛЬШЕМУ
     * rank[x] ≈ log(размер поддерева x)
     *
     * После n операций union:
     * - Высота дерева ≤ log(n)
     * - find = O(log n) даже без path compression
     * - С path compression: O(α(n)) ≈ O(1)
     */
    fun union(x: Int, y: Int): Boolean {
        val px = find(x)
        val py = find(y)
        if (px == py) return false

        when {
            rank[px] < rank[py] -> parent[px] = py
            rank[px] > rank[py] -> parent[py] = px
            else -> {
                parent[py] = px
                rank[px]++
            }
        }
        return true
    }

    fun connected(x: Int, y: Int) = find(x) == find(y)
}
```

### Binary Indexed Tree (Fenwick Tree)

```kotlin
/**
 * Fenwick Tree / Binary Indexed Tree
 *
 * Time: O(log n) per operation
 * Supports: point update, prefix sum query
 */
class BIT(private val n: Int) {
    private val tree = LongArray(n + 1)

    /**
     * POINT UPDATE: добавить delta к элементу i
     *
     * Ключевая операция: i & (-i) — МЛАДШИЙ УСТАНОВЛЕННЫЙ БИТ (LSB)
     * ────────────────────────────────────────────────────────────
     *
     * Как работает i & (-i)?
     * -i в дополнительном коде = инверсия всех битов + 1
     *
     * ПРИМЕР: i = 6 = 0110₂
     * -i = 1001 + 1 = 1010₂
     * i & (-i) = 0110 & 1010 = 0010₂ = 2
     *
     * LSB показывает "ответственность" ячейки:
     * tree[6] отвечает за 2 элемента (индексы 5-6)
     *
     * ОБХОД ПРИ UPDATE (i = 3):
     * ─────────────────────────
     * idx = 3 = 011₂, LSB = 1 → обновляем tree[3]
     * idx = 4 = 100₂, LSB = 4 → обновляем tree[4]
     * idx = 8 = 1000₂         → обновляем tree[8]
     * ...
     *
     * Каждая ячейка tree[idx] накапливает изменения
     * от элементов в своём "диапазоне ответственности"
     */
    fun update(i: Int, delta: Long) {
        // Внутри BIT индексы 1-based (tree[1..n])
        // Снаружи 0-based (arr[0..n-1])
        // Поэтому: idx = i + 1
        var idx = i + 1
        while (idx <= n) {
            tree[idx] += delta
            idx += idx and (-idx)  // Переход к следующей ответственной ячейке
        }
    }

    // Сумма [0, i]
    fun query(i: Int): Long {
        var sum = 0L
        var idx = i + 1
        while (idx > 0) {
            sum += tree[idx]
            idx -= idx and (-idx)
        }
        return sum
    }

    // Сумма [l, r]
    fun rangeQuery(l: Int, r: Int): Long {
        return query(r) - if (l > 0) query(l - 1) else 0L
    }
}
```

### Segment Tree

```kotlin
/**
 * Segment Tree для range sum queries и point updates
 *
 * Time: O(log n) per operation
 */
class SegmentTree(private val arr: LongArray) {
    private val n = arr.size
    private val tree = LongArray(4 * n)

    init { build(0, 0, n - 1) }

    private fun build(v: Int, tl: Int, tr: Int) {
        if (tl == tr) {
            tree[v] = arr[tl]
        } else {
            val tm = (tl + tr) / 2
            build(2 * v + 1, tl, tm)
            build(2 * v + 2, tm + 1, tr)
            tree[v] = tree[2 * v + 1] + tree[2 * v + 2]
        }
    }

    // Point update: arr[pos] = value
    fun update(pos: Int, value: Long) {
        update(0, 0, n - 1, pos, value)
    }

    private fun update(v: Int, tl: Int, tr: Int, pos: Int, value: Long) {
        if (tl == tr) {
            tree[v] = value
        } else {
            val tm = (tl + tr) / 2
            if (pos <= tm) {
                update(2 * v + 1, tl, tm, pos, value)
            } else {
                update(2 * v + 2, tm + 1, tr, pos, value)
            }
            tree[v] = tree[2 * v + 1] + tree[2 * v + 2]
        }
    }

    // Range query: sum [l, r]
    fun query(l: Int, r: Int): Long {
        return query(0, 0, n - 1, l, r)
    }

    private fun query(v: Int, tl: Int, tr: Int, l: Int, r: Int): Long {
        if (l > tr || r < tl) return 0L
        if (l <= tl && tr <= r) return tree[v]

        val tm = (tl + tr) / 2
        return query(2 * v + 1, tl, tm, l, r) +
               query(2 * v + 2, tm + 1, tr, l, r)
    }
}
```

---

## 8. Чеклист перед Submit

```
□ Правильный тип данных (Int vs Long)
□ Array bounds проверены
□ Деление на 0 невозможно
□ Overflow учтен (сумма, произведение)
□ Edge cases:
  □ n = 0, n = 1
  □ Пустой ввод
  □ Все элементы одинаковые
  □ Отсортированный / обратно отсортированный
□ Debug print выключен
□ Правильный формат вывода
□ flush() / endl для output
□ MOD применен где нужно
□ 0-indexed vs 1-indexed согласованы
```

---

## 9. Резюме

### Приоритет оптимизаций

| Приоритет | Что | Когда |
|-----------|-----|-------|
| 1 | Правильный алгоритм | Всегда |
| 2 | Правильный тип данных | При больших числах |
| 3 | Fast I/O | При N > 10^5 |
| 4 | Константные оптимизации | При TLE на границе |

### Ресурсы

- [CP-Algorithms](https://cp-algorithms.com) — алгоритмы и структуры
- [Codeforces EDU](https://codeforces.com/edu/courses) — курсы
- [USACO Guide](https://usaco.guide) — структурированное обучение
- [AtCoder Library](https://github.com/atcoder/ac-library) — reference implementation

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Оптимизация важнее алгоритма" | **Правильный алгоритм** важнее micro-optimizations. O(n log n) всегда лучше O(n²) |
| "Fast I/O нужен всегда" | Fast I/O помогает при n > 10⁵. Для **маленького ввода** обычный I/O достаточен |
| "Templates = читерство" | Templates — **стандартная практика**. Экономят время на contest. Но нужно понимать код |
| "Debug output безвреден" | Debug print может вызвать **TLE** на больших данных. Всегда удаляй перед submit |
| "Один WA = неправильный алгоритм" | Часто проблема в **edge cases**, overflow, 0/1-indexing. Проверь corner cases |

---

## CS-фундамент

| CS-концепция | Применение в Implementation |
|--------------|-----------------------------|
| **Integer Overflow** | Int: ~2×10⁹, Long: ~9×10¹⁸. Сумма n×10⁹ чисел требует Long |
| **I/O Buffering** | BufferedReader быстрее Scanner. Flush после output критичен для interactive |
| **Modular Arithmetic** | (a + b) mod m = ((a mod m) + (b mod m)) mod m. Применяй MOD часто |
| **0-indexed vs 1-indexed** | Массивы 0-indexed, но задачи часто 1-indexed. Консистентность критична |
| **Precision** | Double: ~15 значащих цифр. EPS comparison для floating point |

---

## Связь с другими темами

**[[competitive-programming-overview]]** — Implementation tips — это практическая «боевая» часть соревновательного программирования, описанного в overview. Если overview даёт общую карту мира CP (платформы, рейтинги, форматы контестов), то данный файл вооружает конкретными инструментами: шаблонами, Fast I/O, приёмами модульной арифметики. Без этих навыков даже правильный алгоритм может получить TLE или WA из-за технических ошибок реализации. Overview объясняет «зачем», implementation tips — «как именно».

**[[contest-strategy]]** — Стратегия контеста и реализация неразрывно связаны. Стратегия определяет, сколько времени выделить на задачу, а скорость реализации определяет, укладываешься ли ты в это время. Готовый template экономит 5-10 минут — это разница между «решил C» и «не успел C». Правило «A+B за 15 минут» из стратегии выполнимо только при отлаженном Fast I/O и привычке к KISS-коду. Debugging под давлением, описанный в стратегии, напрямую использует приёмы debug print и stress testing из этого файла.

---

## Источники и дальнейшее чтение

### Книги

- **Halim, Halim (2013). "Competitive Programming 3."** — Содержит обширную коллекцию шаблонов кода, приёмов Fast I/O и реализаций стандартных структур данных (DSU, Segment Tree, BIT), которые составляют основу любого competitive template. Практические советы по реализации проверены на тысячах контестов.
- **Skiena (2008). "The Algorithm Design Manual."** — Помимо теории алгоритмов, книга уделяет внимание практическим аспектам реализации: как избежать типичных ошибок, как тестировать решения, как выбирать структуры данных для конкретных задач. War Stories показывают реальные ловушки реализации.
- **Sedgewick, Wayne (2011). "Algorithms."** — Образцовые реализации всех основных алгоритмов и структур данных на Java. Код из этой книги можно адаптировать как competitive template. Особенно полезны реализации priority queue, union-find и сортировок с подробным анализом производительности.


---

## Проверь себя

> [!question]- Почему BufferedReader в Java в 5-10x быстрее Scanner и когда это критично?
> Scanner парсит regex для каждого token (обёрнут в Pattern). BufferedReader читает блоками, split/parseInt вручную. Для N=10^6 чисел: Scanner ~2-3 секунды, BufferedReader ~0.3 секунды. Критично когда TL=1-2 секунды и большой input. В Python: sys.stdin.readline() вместо input().

> [!question]- Какие элементы должен содержать competitive template и почему он экономит время?
> Template: Fast I/O, typedefs (long long, pair), DSU/SegTree, GCD/power(mod), сортировка, debug macro. Экономит 5-10 мин setup на каждом contest. Код уже протестирован — меньше багов в boilerplate. У топ-участников template 200-500 строк. Ключ: template который ты понимаешь наизусть.

> [!question]- Почему простой код лучше элегантного на контесте?
> 1) Меньше багов: простой код легче дебажить. 2) Быстрее писать: меньше thinking overhead. 3) Легче модифицировать: при WA проще найти ошибку. 4) Меньше edge cases: сложный код больше ломается. Правило: 'stupid code that works > clever code that might work'. Элегантность — для production, не для CP.

## Ключевые карточки

Как организовать Fast I/O в разных языках?
?
C++: ios_base::sync_with_stdio(false); cin.tie(NULL). Java: BufferedReader + StringTokenizer. Python: sys.stdin.readline, sys.stdout.write. Kotlin: BufferedReader(System.`in`.reader()). Разница: 5-10x для больших inputs.

Какие debug-техники самые эффективные на контесте?
?
1) cerr << для промежуточных значений. 2) Маленькие ручные тесты (n=3-5). 3) Stress test: brute force + random generator + compare. 4) Assert для инвариантов. 5) '#ifdef LOCAL' для debug-only кода.

Какие типичные баги на контесте?
?
1) Integer overflow (используй long long). 2) Off-by-one (0-indexed vs 1-indexed). 3) Array bounds. 4) Не инициализировал переменные. 5) Сортировка: wrong comparator. 6) Забыл clear global data между тестами. 7) Modular arithmetic: (a-b)%MOD может быть отрицательным.

Как обрабатывать модулярную арифметику?
?
MOD = 1e9+7. Сложение: (a+b)%MOD. Вычитание: ((a-b)%MOD + MOD)%MOD. Умножение: (1LL*a*b)%MOD. Деление: a * power(b, MOD-2, MOD) % MOD (Fermat). Всегда берём mod после каждой операции.

Что такое stress testing?
?
Автоматическая проверка решения: 1) Brute force (O(n^2), гарантированно правильный). 2) Random test generator. 3) Цикл: генерируем тест, запускаем оба, сравниваем. При расхождении — нашли баг + тест. Скрипт 10-20 строк, экономит часы дебага.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[competitive/problem-classification]] | Классификация задач |
| Углубиться | [[competitive/contest-strategy]] | Стратегия на контесте |
| Смежная тема | [[interview-prep/common-mistakes]] | Типичные ошибки — пересечение с CP |
| Обзор | [[competitive/competitive-programming-overview]] | Вернуться к обзору CP |


---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
