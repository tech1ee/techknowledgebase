# Divide and Conquer

## TL;DR

Divide and Conquer — парадигма: **разбить** задачу на подзадачи, **решить** рекурсивно, **объединить** результаты. Master Theorem: T(n) = aT(n/b) + f(n) определяет сложность. Примеры: Merge Sort O(n log n), Quick Sort O(n log n) avg, Binary Search O(log n), Karatsuba multiplication O(n^1.58). Ключ — уменьшение работы на каждом уровне.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Турнир на выбывание

Представь турнир по шахматам с 128 участниками. Нужно найти чемпиона.

**Наивный способ:** Каждый играет с каждым → 128 × 127 / 2 = 8128 партий.

**Турнирная система (Divide & Conquer):**

```
Раунд 1: 64 пары → 64 победителя
Раунд 2: 32 пары → 32 победителя
Раунд 3: 16 пар  → 16 победителей
Раунд 4: 8 пар   → 8 победителей
Раунд 5: 4 пары  → 4 победителя
Раунд 6: 2 пары  → 2 победителя
Раунд 7: 1 пара  → ЧЕМПИОН!

Всего: 64 + 32 + 16 + 8 + 4 + 2 + 1 = 127 партий
```

**Ускорение:** 8128 → 127 = **в 64 раза быстрее!**

---

### Аналогия 2: Телефонный справочник

Нужно найти "Петрова" в справочнике из 1000 страниц.

**Наивно:** Листать с первой страницы → до 1000 страниц.

**Divide & Conquer (Binary Search):**

```
Открываем середину (страница 500):
  - Там "Николаев" → Петров ПОСЛЕ → ищем в [501-1000]

Открываем страницу 750:
  - Там "Сидоров" → Петров ДО → ищем в [501-749]

Открываем страницу 625:
  - Там "Павлов" → Петров ПОСЛЕ → ищем в [626-749]

... и так далее

Максимум: log₂(1000) ≈ 10 страниц вместо 1000!
```

---

### Аналогия 3: Сортировка карточек

У тебя 100 карточек с числами. Как отсортировать?

**Merge Sort — стратегия "разделяй и властвуй":**

```
1. РАЗДЕЛИ стопку пополам (50 и 50)
2. ПОВТОРИ для каждой половины (рекурсия)
3. Когда остались стопки по 1 карточке — они "отсортированы"
4. СЛЕЙ две отсортированные стопки в одну:
   - Сравни верхние карточки обеих стопок
   - Меньшую положи в результат
   - Повторяй пока не закончатся обе стопки
```

**Визуализация:**

```
      [38, 27, 43, 3, 9, 82, 10]
              ↓ DIVIDE
    [38, 27, 43]      [3, 9, 82, 10]
       ↓                   ↓
  [38, 27] [43]     [3, 9] [82, 10]
     ↓       ↓         ↓       ↓
  [38][27] [43]     [3][9]  [82][10]
     ↓       ↓         ↓       ↓
   [27,38] [43]      [3,9]  [10,82]
       ↓                   ↓
    [27,38,43]        [3,9,10,82]
              ↓ COMBINE
      [3, 9, 10, 27, 38, 43, 82]
```

---

### Аналогия 4: Quick Sort — выбор лидера

Представь класс из 30 учеников. Нужно выстроить по росту.

**Quick Sort:**

```
1. Выбери одного ученика — "пивот" (например, Петя ростом 165 см)
2. Все ниже Пети → идут СЛЕВА
   Все выше Пети → идут СПРАВА
3. Петя теперь ТОЧНО на своём месте!
4. Повтори для левой и правой групп

Петя (165 см) — пивот:
  [Маша 150] [Вова 160] ← ПЕТЯ → [Саша 170] [Лена 175]

Петя уже отсортирован! Рекурсивно сортируем группы слева и справа.
```

**Отличие от Merge Sort:**

| | Merge Sort | Quick Sort |
|---|------------|------------|
| Работа | При COMBINE (слияние) | При DIVIDE (partition) |
| Баланс | Всегда ровно пополам | Зависит от пивота |
| Worst case | O(n log n) всегда | O(n²) при плохом пивоте |
| In-place | Нет (нужен доп. массив) | Да |

---

### Числовой пример: Master Theorem

**Задача:** Определить сложность T(n) = 2T(n/2) + n (Merge Sort).

```
T(n) = aT(n/b) + f(n)
       ↓    ↓     ↓
       a=2  b=2   f(n)=n

Критическая точка: n^(log_b(a)) = n^(log₂2) = n¹ = n

Сравниваем f(n) = n с n^(log_b(a)) = n:
  f(n) = Θ(n) = Θ(n^(log_b(a))) → Case 2!

Case 2: T(n) = Θ(n^(log_b(a)) × log n) = Θ(n log n)
```

**Визуально — дерево рекурсии:**

```
Level 0:        n                    работа: n
               / \
Level 1:     n/2  n/2                работа: n
             /\    /\
Level 2:  n/4 n/4 n/4 n/4            работа: n
          ...  ...  ...  ...
Level k:  1  1  1  ...  1  1         работа: n

Высота дерева: log n
Работа на уровне: n (всегда одинакова)
Итого: n × log n = O(n log n)
```

---

## Часть 2: Почему Divide & Conquer сложный

### Типичные ошибки студентов

#### Ошибка 1: Забыть base case

**Симптом:** StackOverflowError / бесконечная рекурсия

```
// ❌ ОШИБКА: нет base case
fun mergeSort(arr: IntArray, l: Int, r: Int) {
    val mid = (l + r) / 2
    mergeSort(arr, l, mid)      // Бесконечно делим!
    mergeSort(arr, mid + 1, r)
    merge(arr, l, mid, r)
}

// ✅ ПРАВИЛЬНО:
fun mergeSort(arr: IntArray, l: Int, r: Int) {
    if (l >= r) return  // ← BASE CASE: массив из 0-1 элементов
    val mid = (l + r) / 2
    mergeSort(arr, l, mid)
    mergeSort(arr, mid + 1, r)
    merge(arr, l, mid, r)
}
```

---

#### Ошибка 2: Неправильное вычисление mid

**Симптом:** ArrayIndexOutOfBoundsException или бесконечный цикл

```
// ❌ ОШИБКА: переполнение при больших индексах
val mid = (l + r) / 2  // l + r может переполниться!

// ✅ ПРАВИЛЬНО:
val mid = l + (r - l) / 2  // Безопасное вычисление
```

---

#### Ошибка 3: Забыть COMBINE шаг

**Симптом:** Алгоритм ничего не делает

```
// ❌ ОШИБКА: подзадачи решены, но не объединены
fun countInversions(arr: IntArray, l: Int, r: Int): Long {
    if (l >= r) return 0
    val mid = (l + r) / 2
    countInversions(arr, l, mid)      // Посчитали инверсии слева
    countInversions(arr, mid + 1, r)  // Посчитали инверсии справа
    // ← ГДЕ ПОДСЧЁТ ИНВЕРСИЙ МЕЖДУ ПОЛОВИНАМИ?!
    return 0  // Всегда 0!
}

// ✅ ПРАВИЛЬНО:
fun countInversions(arr: IntArray, l: Int, r: Int): Long {
    if (l >= r) return 0
    val mid = (l + r) / 2
    var count = countInversions(arr, l, mid)
    count += countInversions(arr, mid + 1, r)
    count += mergeAndCount(arr, l, mid, r)  // ← COMBINE!
    return count
}
```

---

#### Ошибка 4: Путаница с границами [l, mid] vs [mid+1, r]

**Симптом:** Пропущенные или дублированные элементы

```
// ❌ ОШИБКА: mid обрабатывается дважды
mergeSort(arr, l, mid)
mergeSort(arr, mid, r)  // mid включён в обе части!

// ✅ ПРАВИЛЬНО:
mergeSort(arr, l, mid)      // [l, mid]
mergeSort(arr, mid + 1, r)  // [mid+1, r]
```

---

#### Ошибка 5: Неправильный pivot в Quick Sort

**Симптом:** O(n²) на отсортированных массивах

```
// ❌ ОШИБКА: всегда берём первый элемент
val pivot = arr[l]
// На отсортированном массиве: pivot = min, всё справа
// Partition: 0 элементов слева, n-1 справа → O(n²)

// ✅ ПРАВИЛЬНО: случайный pivot
val randomIndex = l + Random().nextInt(r - l + 1)
swap(arr, randomIndex, r)  // Перемещаем в конец
val pivot = arr[r]
```

---

#### Ошибка 6: Мутация исходного массива при merge

**Симптом:** Данные перезаписываются до использования

```
// ❌ ОШИБКА: пишем в arr, пока читаем из arr
while (i <= mid && j <= r) {
    if (arr[i] <= arr[j]) arr[k++] = arr[i++]  // Перезатёрли!
    else arr[k++] = arr[j++]
}

// ✅ ПРАВИЛЬНО: копируем в временные массивы
val left = arr.sliceArray(l..mid)
val right = arr.sliceArray(mid + 1..r)
// Теперь безопасно читаем из left/right, пишем в arr
```

---

## Часть 3: Ментальные модели

### Модель 1: Три шага D&C

```
┌─────────────────────────────────────────────────────────┐
│                    DIVIDE & CONQUER                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. DIVIDE: Разбей на подзадачи                        │
│     - Binary Search: left/right half                    │
│     - Merge Sort: two halves                            │
│     - Quick Sort: partition around pivot                │
│                                                         │
│  2. CONQUER: Реши подзадачи рекурсивно                 │
│     - Base case: тривиальная подзадача                 │
│     - Recursive case: вызови себя                       │
│                                                         │
│  3. COMBINE: Объедини результаты                       │
│     - Binary Search: выбери нужную половину            │
│     - Merge Sort: merge отсортированных половин        │
│     - Quick Sort: ничего (partition уже сделал!)       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Модель 2: Merge Sort vs Quick Sort

```
MERGE SORT:                          QUICK SORT:

Лёгкий DIVIDE,                       Тяжёлый DIVIDE,
Тяжёлый COMBINE                      COMBINE не нужен

    [4,2,3,1]                           [4,2,3,1]
       ↓ split                             ↓ partition (pivot=2)
  [4,2] [3,1]                         [1] [2] [4,3]
     ↓                                      ↓
 ... рекурсия ...                     ... рекурсия ...
     ↓                                      ↓
  [2,4] [1,3]                         [1] [2] [3,4]
       ↓ MERGE (работа!)                   ↓ ничего!
    [1,2,3,4]                           [1,2,3,4]
```

**Мнемоника:**
- Merge Sort: "Сначала разбей, потом собери" (работа при combine)
- Quick Sort: "Сначала расставь, потом разбей" (работа при divide)

---

### Модель 3: Дерево рекурсии для анализа

**Для T(n) = aT(n/b) + f(n):**

```
                    f(n)                    Level 0: 1 × f(n)
           /    /    |    \    \
         f(n/b) ... a раз ... f(n/b)        Level 1: a × f(n/b)
         /   \               /   \
       ...   ...           ...   ...        Level 2: a² × f(n/b²)
       ...   ...           ...   ...

       O(1) O(1) O(1) ... O(1) O(1)         Level log_b(n): n^(log_b(a)) × O(1)
```

**Три случая:**
1. **Листья доминируют:** f(n) маленькая → T(n) = Θ(n^(log_b(a)))
2. **Все уровни равны:** f(n) = Θ(n^(log_b(a))) → T(n) = Θ(f(n) × log n)
3. **Корень доминирует:** f(n) большая → T(n) = Θ(f(n))

---

### Модель 4: Когда использовать D&C

```
Используй D&C, когда:

1. Задача РАЗБИВАЕТСЯ на похожие подзадачи
   ✓ Сортировка → сортировка половин
   ✓ Поиск максимума → максимум в половинах

2. Подзадачи НЕЗАВИСИМЫ
   ✓ Левая половина не зависит от правой
   ✗ Если подзадачи перекрываются → используй DP!

3. Решения КОМБИНИРУЮТСЯ эффективно
   ✓ Merge двух отсортированных массивов — O(n)
   ✗ Если combine стоит O(n²) — D&C не поможет

НЕ используй D&C, когда:
- Подзадачи перекрываются → Dynamic Programming
- Нет естественного разбиения
- Combine слишком дорогой
```

---

### Модель 5: Шаблон кода D&C

```
fun divideAndConquer(problem, params):
    // 1. BASE CASE
    if (problem достаточно мал):
        return тривиальное_решение

    // 2. DIVIDE
    subproblems = разбить(problem)

    // 3. CONQUER
    results = []
    for sub in subproblems:
        results.add(divideAndConquer(sub, params))

    // 4. COMBINE
    return объединить(results)
```

**Пример — Merge Sort:**

```kotlin
fun mergeSort(arr, l, r):
    // BASE CASE
    if (l >= r) return

    // DIVIDE
    mid = l + (r - l) / 2

    // CONQUER
    mergeSort(arr, l, mid)
    mergeSort(arr, mid + 1, r)

    // COMBINE
    merge(arr, l, mid, r)
```

---

## Зачем это нужно?

**Проблема:**

```
Сортировка массива из 10^6 элементов.

Наивно (Bubble Sort): O(n²) = 10^12 операций → 1000 секунд
D&C (Merge Sort): O(n log n) = 20 × 10^6 операций → 0.02 секунды

50,000x быстрее!
```

**Где используется:**

| Область | Алгоритм | Ускорение |
|---------|----------|-----------|
| Сортировка | Merge Sort, Quick Sort | O(n²) → O(n log n) |
| Поиск | Binary Search | O(n) → O(log n) |
| Умножение | Karatsuba, Strassen | O(n²) → O(n^1.58) |
| FFT | Cooley-Tukey | O(n²) → O(n log n) |
| Closest pair | 2D closest pair | O(n²) → O(n log n) |

---

## Что это такое?

### Для 5-летнего

```
Представь, что нужно найти самого высокого в очереди из 100 детей.

Наивно: сравнить всех со всеми — очень долго!

Divide and Conquer:
1. Раздели очередь пополам (50 и 50)
2. Найди самого высокого в каждой половине
3. Сравни двух победителей

Каждый раз работы ВДВОЕ меньше!
```

### Формально

**Divide and Conquer** — алгоритмическая парадигма:

1. **Divide**: Разбить задачу размера n на a подзадач размера n/b
2. **Conquer**: Решить подзадачи рекурсивно
3. **Combine**: Объединить решения подзадач

```
        Problem(n)
        /    |    \
       /     |     \
   P(n/b)  P(n/b)  P(n/b)    ← a подзадач
     |       |       |
   solve   solve   solve      ← рекурсия
     \       |      /
      \      |     /
       combine(...)           ← объединение
           |
        Solution
```

---

## Master Theorem

### Формула

Для рекуррентности T(n) = aT(n/b) + f(n):

```
Сравниваем f(n) с n^(log_b(a)):

Case 1: f(n) = O(n^(log_b(a) - ε))    → T(n) = Θ(n^(log_b(a)))
        (рекурсия доминирует)

Case 2: f(n) = Θ(n^(log_b(a)) log^k n) → T(n) = Θ(n^(log_b(a)) log^(k+1) n)
        (одинаковая работа на каждом уровне)

Case 3: f(n) = Ω(n^(log_b(a) + ε))    → T(n) = Θ(f(n))
        (combine доминирует)
        + условие регулярности: af(n/b) ≤ cf(n) для c < 1
```

### Примеры

```
Binary Search: T(n) = T(n/2) + O(1)
a=1, b=2, f(n)=O(1), n^(log_2(1))=n^0=1
f(n) = Θ(1) = Θ(n^0) → Case 2, k=0
T(n) = Θ(log n) ✓

Merge Sort: T(n) = 2T(n/2) + O(n)
a=2, b=2, f(n)=O(n), n^(log_2(2))=n^1=n
f(n) = Θ(n) = Θ(n^1) → Case 2, k=0
T(n) = Θ(n log n) ✓

Karatsuba: T(n) = 3T(n/2) + O(n)
a=3, b=2, f(n)=O(n), n^(log_2(3))≈n^1.58
f(n) = O(n) = O(n^(1.58-0.58)) → Case 1
T(n) = Θ(n^1.58) ✓

Strassen: T(n) = 7T(n/2) + O(n²)
a=7, b=2, f(n)=O(n²), n^(log_2(7))≈n^2.81
f(n) = O(n²) = O(n^(2.81-0.81)) → Case 1
T(n) = Θ(n^2.81) ✓
```

### Визуализация дерева рекурсии

```
T(n) = 2T(n/2) + cn (Merge Sort)

Level 0:           cn                    → cn
                  /  \
Level 1:     cn/2    cn/2               → cn
             /  \    /  \
Level 2:  cn/4 cn/4 cn/4 cn/4           → cn
           ...  ...  ...  ...
Level k:  c  c  c  c  c  c  c  c  ...   → cn

Height = log n levels
Work per level = cn
Total = cn × log n = O(n log n)
```

---

## Классические алгоритмы

### 1. Merge Sort

```kotlin
/**
 * Сортировка слиянием — классический пример Divide & Conquer
 *
 * ТРИ ЭТАПА D&C:
 * 1. DIVIDE: Делим массив пополам (mid)
 * 2. CONQUER: Рекурсивно сортируем каждую половину
 * 3. COMBINE: Сливаем отсортированные половины в один массив
 *
 * ПОШАГОВЫЙ ПРИМЕР (arr = [38, 27, 43, 3]):
 *
 *                [38, 27, 43, 3]
 *                  /          \
 *            [38, 27]        [43, 3]
 *             /    \          /    \
 *          [38]   [27]     [43]   [3]     ← База
 *             \    /          \    /
 *            [27, 38]        [3, 43]      ← Merge
 *                  \          /
 *              [3, 27, 38, 43]            ← Финальный Merge
 *
 * СЛОЖНОСТЬ: T(n) = 2T(n/2) + O(n) = O(n log n)
 */
fun mergeSort(arr: IntArray, l: Int = 0, r: Int = arr.size - 1) {
    if (l >= r) return

    val mid = l + (r - l) / 2

    // DIVIDE: разбиваем массив на две половины
    // Левая часть: [l, mid], Правая часть: [mid+1, r]
    mergeSort(arr, l, mid)
    mergeSort(arr, mid + 1, r)

    // CONQUER + COMBINE: сливаем отсортированные половины
    // На этом этапе обе половины уже отсортированы рекурсией
    merge(arr, l, mid, r)
}

/**
 * Слияние двух отсортированных подмассивов
 *
 * МЕХАНИЗМ TWO-POINTER:
 * - i указывает на текущий элемент в left[]
 * - j указывает на текущий элемент в right[]
 * - На каждом шаге берём меньший элемент
 *
 * ПОШАГОВЫЙ ПРИМЕР (left = [27, 38], right = [3, 43]):
 *
 * Шаг 1: left[0]=27 vs right[0]=3 → берём 3, j++
 * Шаг 2: left[0]=27 vs right[1]=43 → берём 27, i++
 * Шаг 3: left[1]=38 vs right[1]=43 → берём 38, i++
 * Шаг 4: left закончился → берём остаток right: 43
 *
 * Результат: [3, 27, 38, 43]
 */
fun merge(arr: IntArray, l: Int, mid: Int, r: Int) {
    val left = arr.sliceArray(l..mid)
    val right = arr.sliceArray(mid + 1..r)

    var i = 0
    var j = 0
    var k = l

    // Two-pointer слияние: берём меньший из двух указателей
    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            arr[k++] = left[i++]
        } else {
            arr[k++] = right[j++]
        }
    }

    // Добавляем остатки (только один из циклов выполнится)
    while (i < left.size) arr[k++] = left[i++]
    while (j < right.size) arr[k++] = right[j++]
}
```

**Сложность**: T(n) = 2T(n/2) + O(n) = **O(n log n)**

### 2. Quick Sort

```kotlin
/**
 * Быстрая сортировка — D&C с partition вместо merge
 *
 * ОТЛИЧИЕ ОТ MERGE SORT:
 * - Merge Sort: лёгкий divide, тяжёлый combine
 * - Quick Sort: тяжёлый divide (partition), combine НЕ НУЖЕН!
 *
 * ТРИ ЭТАПА:
 * 1. DIVIDE: partition — все элементы < pivot слева, >= pivot справа
 * 2. CONQUER: рекурсивно сортируем левую и правую части
 * 3. COMBINE: не нужен! Partition уже расставил элементы in-place
 *
 * ПОШАГОВЫЙ ПРИМЕР (arr = [3, 6, 8, 10, 1, 2, 1], pivot = 1 в конце):
 *
 * После partition с pivot=1:
 * [1, 1, 3, 6, 8, 10, 2]  ← неправильно, pivot должен быть в позиции
 *       ^
 * Правильно: [элементы < pivot] [pivot] [элементы >= pivot]
 *
 * СЛОЖНОСТЬ:
 * - Average: O(n log n) — при хорошем pivot делим примерно пополам
 * - Worst: O(n²) — при плохом pivot (уже отсортированный массив)
 * - Random pivot защищает от worst case
 */
fun quickSort(arr: IntArray, l: Int = 0, r: Int = arr.size - 1) {
    if (l >= r) return

    // DIVIDE: partition разделяет массив вокруг pivot
    // После partition: arr[l..pivotIndex-1] < pivot <= arr[pivotIndex+1..r]
    val pivotIndex = partition(arr, l, r)

    // CONQUER: рекурсивно сортируем обе части
    quickSort(arr, l, pivotIndex - 1)
    quickSort(arr, pivotIndex + 1, r)
    // COMBINE: не нужен! Partition уже расставил элементы правильно
}

/**
 * Partition (схема Lomuto)
 *
 * ИДЕЯ:
 * - Выбираем pivot (случайный для защиты от worst case)
 * - Переставляем элементы: < pivot слева, >= pivot справа
 * - Pivot встаёт на своё финальное место
 *
 * МЕХАНИЗМ:
 * - i — граница между "меньшими" и "большими/равными"
 * - j — текущий элемент для проверки
 *
 * ПОШАГОВЫЙ ПРИМЕР (arr = [3, 6, 2, 8, 1], pivot = arr[4] = 1):
 * Swap pivot в конец: [3, 6, 2, 8, 1], pivot = 1
 *
 * j=0: arr[0]=3 >= 1, skip
 * j=1: arr[1]=6 >= 1, skip
 * j=2: arr[2]=2 >= 1, skip
 * j=3: arr[3]=8 >= 1, skip
 * Финал: swap arr[0] и arr[4]: [1, 6, 2, 8, 3]
 *
 * Результат: pivot=1 на позиции 0, все справа >= 1
 */
fun partition(arr: IntArray, l: Int, r: Int): Int {
    // Random pivot для O(n log n) average
    // Без рандома отсортированный массив даёт O(n²)
    val pivotIdx = (l..r).random()
    arr[pivotIdx] = arr[r].also { arr[r] = arr[pivotIdx] }

    val pivot = arr[r]
    var i = l  // Граница "меньших" элементов

    for (j in l until r) {
        if (arr[j] < pivot) {
            arr[i] = arr[j].also { arr[j] = arr[i] }
            i++
        }
    }

    // Ставим pivot на своё место
    arr[i] = arr[r].also { arr[r] = arr[i] }
    return i
}
```

**Сложность**:
- Average: O(n log n)
- Worst (bad pivot): O(n²)

### 3. Binary Search

```kotlin
/**
 * Бинарный поиск — D&C с ОДНОЙ подзадачей (Decrease & Conquer)
 *
 * ОТЛИЧИЕ ОТ КЛАССИЧЕСКОГО D&C:
 * - Классический D&C: решаем ОБЕ подзадачи (left и right)
 * - Decrease & Conquer: решаем ОДНУ подзадачу (left ИЛИ right)
 *
 * ИДЕЯ:
 * - Сравниваем target с серединой
 * - Если нашли — возвращаем
 * - Если target больше — ищем в правой половине
 * - Если target меньше — ищем в левой половине
 *
 * ПОШАГОВЫЙ ПРИМЕР (arr = [1, 3, 5, 7, 9], target = 7):
 *
 * Шаг 1: l=0, r=4, mid=2, arr[2]=5 < 7 → l=3
 * Шаг 2: l=3, r=4, mid=3, arr[3]=7 == 7 → return 3 ✓
 *
 * СЛОЖНОСТЬ: T(n) = T(n/2) + O(1) = O(log n)
 */
fun binarySearch(arr: IntArray, target: Int): Int {
    var l = 0
    var r = arr.size - 1

    while (l <= r) {
        // Безопасный mid: l + (r - l) / 2 вместо (l + r) / 2
        // (l + r) может overflow при больших l и r
        val mid = l + (r - l) / 2

        when {
            arr[mid] == target -> return mid
            // target больше mid → искомое в правой половине
            // Отбрасываем [l, mid], ищем в [mid+1, r]
            arr[mid] < target -> l = mid + 1
            // target меньше mid → искомое в левой половине
            // Отбрасываем [mid, r], ищем в [l, mid-1]
            else -> r = mid - 1
        }
    }

    return -1  // Не найдено
}
```

**Сложность**: T(n) = T(n/2) + O(1) = **O(log n)**

### 4. Karatsuba Multiplication

```kotlin
/**
 * Умножение Карацубы — умножение больших чисел за O(n^1.58) вместо O(n²)
 *
 * КЛАССИЧЕСКОЕ УМНОЖЕНИЕ:
 * x × y требует 4 умножения: ac, ad, bc, bd → T(n) = 4T(n/2) + O(n) = O(n²)
 *
 * ТРЮК КАРАЦУБЫ:
 * Вместо 4 умножений делаем 3, используя алгебру:
 *
 * МАТЕМАТИКА:
 * Пусть x = a × 10^(n/2) + b, y = c × 10^(n/2) + d
 *
 * Тогда: x × y = ac × 10^n + (ad + bc) × 10^(n/2) + bd
 *
 * Как найти (ad + bc) без вычисления ad и bc отдельно?
 * (a + b)(c + d) = ac + ad + bc + bd
 * → ad + bc = (a + b)(c + d) - ac - bd
 *
 * Итого 3 умножения: ac, bd, (a+b)(c+d)
 *
 * ПОШАГОВЫЙ ПРИМЕР (x = 1234, y = 5678):
 *
 * n = 4, half = 2, power = 100
 * x = 12 × 100 + 34 → a=12, b=34
 * y = 56 × 100 + 78 → c=56, d=78
 *
 * 1. ac = karatsuba(12, 56) = 672
 * 2. bd = karatsuba(34, 78) = 2652
 * 3. (a+b)(c+d) = karatsuba(46, 134) = 6164
 *
 * ad + bc = 6164 - 672 - 2652 = 2840
 *
 * x × y = 672 × 10000 + 2840 × 100 + 2652
 *       = 6720000 + 284000 + 2652
 *       = 7006652 ✓
 *
 * СЛОЖНОСТЬ: T(n) = 3T(n/2) + O(n) = O(n^log₂3) ≈ O(n^1.58)
 */
fun karatsuba(x: Long, y: Long): Long {
    if (x < 10 || y < 10) return x * y

    val n = maxOf(x.toString().length, y.toString().length)
    val half = n / 2
    val power = 10L.pow(half)

    // Разбиваем: x = a × 10^(n/2) + b, y = c × 10^(n/2) + d
    val a = x / power  // Старшие цифры x
    val b = x % power  // Младшие цифры x
    val c = y / power  // Старшие цифры y
    val d = y % power  // Младшие цифры y

    // 3 рекурсивных умножения вместо 4 — в этом весь трюк!
    val ac = karatsuba(a, c)
    val bd = karatsuba(b, d)
    val abcd = karatsuba(a + b, c + d)

    // Алгебраический трюк: (a+b)(c+d) - ac - bd = ad + bc
    val adPlusBc = abcd - ac - bd

    // Собираем результат: x×y = ac × 10^n + (ad+bc) × 10^(n/2) + bd
    return ac * 10L.pow(2 * half) + adPlusBc * power + bd
}

fun Long.pow(n: Int): Long {
    var result = 1L
    repeat(n) { result *= 10 }
    return result
}
```

**Сложность**: T(n) = 3T(n/2) + O(n) = **O(n^log₂3) ≈ O(n^1.58)**

### 5. Closest Pair of Points

```kotlin
/**
 * Ближайшая пара точек — классическая задача D&C на плоскости
 *
 * НАИВНЫЙ ПОДХОД: O(n²) — проверить все пары
 *
 * D&C ПОДХОД: O(n log n)
 * 1. DIVIDE: делим точки вертикальной линией пополам
 * 2. CONQUER: рекурсивно находим min расстояние в каждой половине
 * 3. COMBINE: проверяем пары, где одна точка слева, другая справа
 *
 * КЛЮЧЕВАЯ ОПТИМИЗАЦИЯ COMBINE:
 * - Не нужно проверять ВСЕ пары через границу!
 * - Если минимум в половинах = d, то проверяем только точки
 *   в "полосе" шириной 2d вокруг разделительной линии
 * - Для каждой точки в полосе проверяем максимум 7 соседей
 *   (доказано геометрически — в прямоугольник d×2d
 *   помещается не более 8 точек с попарным расстоянием ≥ d)
 *
 * ВИЗУАЛИЗАЦИЯ:
 *
 *     LEFT  |  RIGHT
 *           |
 *      •    |    •
 *        •  |  •
 *      •    |      •
 *           |
 *     ←  d  →←  d  →
 *       strip (2d)
 *
 * СЛОЖНОСТЬ: T(n) = 2T(n/2) + O(n) = O(n log n)
 */
data class Point(val x: Double, val y: Double)

fun closestPair(points: List<Point>): Double {
    val sortedByX = points.sortedBy { it.x }
    return closestPairRec(sortedByX)
}

fun closestPairRec(points: List<Point>): Double {
    // База: для ≤3 точек используем brute force
    if (points.size <= 3) {
        return bruteForce(points)
    }

    val mid = points.size / 2
    val midPoint = points[mid]

    // DIVIDE: разбиваем точки на левую и правую половины
    val left = points.subList(0, mid)
    val right = points.subList(mid, points.size)

    // CONQUER: рекурсивно находим минимум в каждой половине
    val dLeft = closestPairRec(left)
    val dRight = closestPairRec(right)
    var d = minOf(dLeft, dRight)

    // COMBINE: проверяем точки в полосе шириной 2d
    // Только точки с |x - midX| < d могут образовать более близкую пару
    val strip = points.filter { abs(it.x - midPoint.x) < d }
        .sortedBy { it.y }

    // Для каждой точки проверяем только 7 следующих по Y
    // Доказано: в прямоугольнике d×2d максимум 8 точек с расстоянием ≥ d
    for (i in strip.indices) {
        var j = i + 1
        while (j < strip.size && (strip[j].y - strip[i].y) < d) {
            d = minOf(d, distance(strip[i], strip[j]))
            j++
        }
    }

    return d
}
```

**Сложность**: T(n) = 2T(n/2) + O(n) = **O(n log n)**

---

## Паттерны применения

### 1. Decrease and Conquer (одна подзадача)

```
Binary Search, Ternary Search, Exponentiation

T(n) = T(n/2) + O(1) = O(log n)
```

### 2. Classic D&C (две+ подзадачи)

```
Merge Sort, Quick Sort, Closest Pair

T(n) = 2T(n/2) + O(n) = O(n log n)
```

### 3. Reduce Constants (оптимизация)

```
Karatsuba: 4 умножения → 3 умножения
Strassen: 8 умножений → 7 умножений

Уменьшение a в T(n) = aT(n/b) + f(n) критично!
```

### 4. D&C на структурах данных

```
Segment Tree: query/update = O(log n)
Merge Sort Tree: range queries with D&C merge
```

---

## Merge Sort Tree (продвинутый пример)

```kotlin
/**
 * Merge Sort Tree — дерево отрезков + merge sort
 *
 * ЗАДАЧА:
 * Отвечать на запросы "сколько элементов < x на отрезке [l, r]"
 *
 * ИДЕЯ:
 * - Каждый узел дерева хранит отсортированный список элементов своего отрезка
 * - При build сливаем списки детей (как в merge sort)
 * - При query используем binary search в нужных узлах
 *
 * СТРУКТУРА ДЕРЕВА (arr = [3, 1, 4, 1, 5, 9]):
 *
 *              [1,1,3,4,5,9]        ← корень: весь массив отсортирован
 *             /             \
 *       [1,3,4]            [1,5,9]
 *       /     \            /     \
 *    [1,3]   [4]       [1,5]    [9]
 *    /   \             /   \
 *  [3]  [1]          [1]  [5]
 *
 * ЗАПРОС countLess(0, 5, 4):
 * "Сколько элементов < 4 в arr[0..5]?"
 *
 * В корне [1,1,3,4,5,9]: binary_search(4) = 3 → 3 элемента < 4
 *
 * СЛОЖНОСТЬ:
 * - Build: O(n log n)
 * - Query: O(log² n) — log n узлов × binary search O(log n)
 * - Память: O(n log n)
 */
class MergeSortTree(private val arr: IntArray) {
    private val n = arr.size
    private val tree = Array<MutableList<Int>>(4 * n) { mutableListOf() }

    init {
        build(1, 0, n - 1)
    }

    private fun build(v: Int, tl: Int, tr: Int) {
        if (tl == tr) {
            tree[v].add(arr[tl])
        } else {
            val mid = (tl + tr) / 2
            build(2 * v, tl, mid)
            build(2 * v + 1, mid + 1, tr)

            // Merge отсортированных списков детей — как в merge sort
            // Результат: tree[v] содержит все элементы [tl, tr] отсортированными
            tree[v] = merge(tree[2 * v], tree[2 * v + 1])
        }
    }

    private fun merge(a: List<Int>, b: List<Int>): MutableList<Int> {
        val result = mutableListOf<Int>()
        var i = 0
        var j = 0
        while (i < a.size && j < b.size) {
            if (a[i] <= b[j]) result.add(a[i++])
            else result.add(b[j++])
        }
        while (i < a.size) result.add(a[i++])
        while (j < b.size) result.add(b[j++])
        return result
    }

    /**
     * Количество элементов < x на отрезке [l, r]
     */
    fun countLess(l: Int, r: Int, x: Int): Int {
        return query(1, 0, n - 1, l, r, x)
    }

    private fun query(v: Int, tl: Int, tr: Int, l: Int, r: Int, x: Int): Int {
        if (l > tr || r < tl) return 0
        if (l <= tl && tr <= r) {
            // Binary search в отсортированном списке tree[v]
            // binarySearch возвращает позицию или -(insertionPoint + 1)
            // Нам нужна позиция первого элемента >= x
            return tree[v].binarySearch(x).let { if (it < 0) -(it + 1) else it }
        }
        val mid = (tl + tr) / 2
        return query(2 * v, tl, mid, l, r, x) +
               query(2 * v + 1, mid + 1, tr, l, r, x)
    }
}
```

---

## Распространённые ошибки

### 1. Неправильный base case

```kotlin
// ❌ НЕПРАВИЛЬНО: бесконечная рекурсия
fun mergeSort(arr: IntArray, l: Int, r: Int) {
    val mid = (l + r) / 2
    mergeSort(arr, l, mid)  // Когда l == r, mid == l → бесконечный цикл!
    mergeSort(arr, mid + 1, r)
    merge(arr, l, mid, r)
}

// ✅ ПРАВИЛЬНО: base case
fun mergeSort(arr: IntArray, l: Int, r: Int) {
    if (l >= r) return  // База: отрезок из ≤1 элемента уже отсортирован
    val mid = (l + r) / 2
    mergeSort(arr, l, mid)
    mergeSort(arr, mid + 1, r)
    merge(arr, l, mid, r)
}
```

### 2. Overflow при вычислении mid

```kotlin
// ❌ НЕПРАВИЛЬНО: (l + r) может overflow
val mid = (l + r) / 2

// ✅ ПРАВИЛЬНО: безопасный mid
val mid = l + (r - l) / 2
```

### 3. Неправильные границы при разбиении

```kotlin
// ❌ НЕПРАВИЛЬНО: пропускаем элемент
mergeSort(arr, l, mid - 1)  // Если mid = l, то l-1 < l!
mergeSort(arr, mid, r)

// ✅ ПРАВИЛЬНО:
mergeSort(arr, l, mid)
mergeSort(arr, mid + 1, r)
```

### 4. Забыть про combine

```kotlin
// ❌ НЕПРАВИЛЬНО: результаты подзадач не объединены
fun countInversions(arr: IntArray, l: Int, r: Int): Long {
    if (l >= r) return 0
    val mid = (l + r) / 2
    countInversions(arr, l, mid)
    countInversions(arr, mid + 1, r)
    // Забыли посчитать инверсии между половинами!
}

// ✅ ПРАВИЛЬНО:
fun countInversions(arr: IntArray, l: Int, r: Int): Long {
    if (l >= r) return 0
    val mid = (l + r) / 2
    var count = countInversions(arr, l, mid)
    count += countInversions(arr, mid + 1, r)
    // COMBINE: считаем инверсии между половинами при merge
    count += mergeAndCount(arr, l, mid, r)
    return count
}
```

---

## Практика

### Концептуальные вопросы

1. **Когда D&C лучше DP?**

   D&C когда подзадачи независимы и не перекрываются. DP когда есть overlapping subproblems и можно кэшировать.

2. **Почему Karatsuba быстрее?**

   Обычное умножение: 4 подзадачи (ac, ad, bc, bd). Karatsuba: 3 подзадачи ((a+b)(c+d), ac, bd). Меньше a в Master Theorem → лучшая асимптотика.

3. **Что если подзадачи разного размера?**

   Master Theorem не применим напрямую. Используй Akra-Bazzi theorem или метод подстановки.

### LeetCode задачи

| # | Название | Сложность | Паттерн |
|---|----------|-----------|---------|
| 912 | Sort an Array | Medium | Merge/Quick Sort |
| 23 | Merge k Sorted Lists | Hard | D&C merge |
| 315 | Count of Smaller Numbers After Self | Hard | Merge Sort + count |
| 493 | Reverse Pairs | Hard | Merge Sort variant |
| 4 | Median of Two Sorted Arrays | Hard | Binary Search D&C |
| 973 | K Closest Points to Origin | Medium | Quick Select |

---

## Связанные темы

### Prerequisites
- Recursion basics
- Complexity analysis

### Unlocks
- [Sorting Algorithms](./sorting-algorithms.md)
- [Binary Search Pattern](../patterns/binary-search-pattern.md)
- FFT (Fast Fourier Transform)
- Segment Tree

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CLRS] Introduction to Algorithms | Book | Theory |
| 2 | [CP-Algorithms: D&C](https://cp-algorithms.com/dynamic_programming/divide-and-conquer-dp.html) | Reference | D&C DP |
| 3 | [MIT OCW 6.006](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/) | Course | Master Theorem |
| 4 | [Karatsuba Algorithm](https://en.wikipedia.org/wiki/Karatsuba_algorithm) | Wiki | Multiplication |

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция D&C, 6 типичных ошибок, 5 ментальных моделей)*
