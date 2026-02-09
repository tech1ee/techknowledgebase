---
title: "Паттерн Meet in the Middle"
created: 2025-12-29
modified: 2026-01-06
type: deep-dive
status: published
difficulty: advanced
confidence: high
cs-foundations:
  - divide-and-conquer
  - exponential-to-sqrt-exponential
  - subset-enumeration
  - binary-search-combination
  - space-time-tradeoff
prerequisites:
  - "[[binary-search-pattern]]"
  - "[[bit-manipulation]]"
  - "[[hash-tables]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/advanced
  - pattern
  - interview
related:
  - "[[backtracking]]"
  - "[[dp-patterns]]"
---

# Meet in the Middle Pattern

## TL;DR

Meet in the Middle разбивает задачу на две половины, решает каждую отдельно, затем комбинирует результаты. **Снижает O(2^n) до O(2^(n/2) × n)**. Работает когда n ≤ 40 (слишком много для brute force, слишком мало для DP). Оптимально для: subset sum с большими значениями, 4SUM, bidirectional search.

---

## Часть 1: Интуиция без кода

### Аналогия 1: Поиск друга в толпе

Представь, что ты и друг потерялись на огромном фестивале с 1 миллионом людей.

```
Стратегия 1 — "Ты ищешь друга":
  Ты обходишь весь фестиваль, проверяя каждого из 1,000,000 людей
  Время: 1,000,000 шагов

Стратегия 2 — "Встречаемся посередине":
  Ты идёшь от входа и отмечаешь все точки, куда дошёл за полпути
  Друг идёт от выхода и отмечает свои точки
  Вы встречаетесь там, где ваши пути пересеклись!

  Каждый проходит √1,000,000 = 1,000 шагов
  Всего: 2,000 шагов вместо 1,000,000!

      ТЫ                      ДРУГ
   (от входа)              (от выхода)
       ↓                        ↓
  ┌─────────┐              ┌─────────┐
  │ 1000    │   ВСТРЕЧА!   │    1000 │
  │ точек   │───────X──────│    точек│
  └─────────┘              └─────────┘
```

**Ключевой инсайт:** Вместо поиска иголки в стоге сена — два человека ищут друг друга навстречу.

---

### Аналогия 2: Подбор кода к сейфу

```
Задача: Угадать 8-значный код (каждая цифра 0-9)

Brute Force — перебираем все коды:
  10^8 = 100,000,000 комбинаций
  При 1000 попыток в секунду = ~28 часов

Meet in the Middle — взламываем умнее:
  Шаг 1: Перебираем первые 4 цифры (10^4 = 10,000)
         Записываем "промежуточное состояние" сейфа после каждого

  Шаг 2: Перебираем последние 4 цифры (10^4 = 10,000)
         Смотрим, какое состояние приводит к открытию

  Шаг 3: Сопоставляем состояния
         Если состояние после первой половины = нужное для второй → код найден!

  Всего: 10,000 + 10,000 = 20,000 попыток
         При 1000 попыток в секунду = 20 секунд!

  Ускорение: 5000x быстрее!
```

**Это реальная криптографическая атака! MITM attack на блочные шифры.**

---

### Аналогия 3: Рюкзак альпиниста (Subset Sum)

```
Задача: У альпиниста 40 вещей разного веса.
        Рюкзак выдерживает 100 кг.
        Какой максимальный вес можно унести?

Brute Force — перебрать все комбинации:
  2^40 ≈ 1,000,000,000,000 вариантов
  Даже при 10^9 операций/сек = ~20 минут

Meet in the Middle:
  Шаг 1: Возьмём первые 20 вещей
         Переберём все 2^20 ≈ 1,000,000 комбинаций
         Запишем все возможные веса: 0кг, 2кг, 5кг, 7кг, ...

  Шаг 2: Возьмём оставшиеся 20 вещей
         Переберём их 2^20 комбинаций

  Шаг 3: Для каждого веса W из первой половины:
         Найдём максимальный вес V из второй, чтобы W + V ≤ 100
         Используем бинарный поиск!

  Всего: 2 × 1,000,000 + 1,000,000 × log(1,000,000) ≈ 22,000,000 операций
         При 10^9 операций/сек = 0.02 секунды!

  Ускорение: 60,000x быстрее!
```

---

### Численный пример: Closest Subset Sum

```
Массив: nums = [5, 8, 3, 1, 7, 2], target = 15
Найти: подмножество с суммой, ближайшей к 15

Шаг 1: Делим массив пополам
  left  = [5, 8, 3]
  right = [7, 2, 1]

Шаг 2: Генерируем все суммы для left (2³ = 8 комбинаций)
  {}     → 0
  {5}    → 5
  {8}    → 8
  {5,8}  → 13
  {3}    → 3
  {5,3}  → 8
  {8,3}  → 11
  {5,8,3}→ 16

  leftSums = [0, 3, 5, 8, 8, 11, 13, 16]
             (сортируем и убираем дубликаты)
           = [0, 3, 5, 8, 11, 13, 16]

Шаг 3: Генерируем все суммы для right
  rightSums = [0, 1, 2, 3, 7, 8, 9, 10]

Шаг 4: Сортируем rightSums для бинарного поиска
  rightSums = [0, 1, 2, 3, 7, 8, 9, 10]

Шаг 5: Для каждой leftSum ищем лучшую rightSum

  leftSum = 0:
    Ищем rightSum ≈ 15 - 0 = 15
    Ближайшее в rightSums: 10
    Сумма: 0 + 10 = 10, разница: |15 - 10| = 5

  leftSum = 5:
    Ищем rightSum ≈ 15 - 5 = 10
    Ближайшее: 10 ✓
    Сумма: 5 + 10 = 15, разница: 0 ✓ ИДЕАЛЬНО!

  Ответ: 15 (сумма подмножества {5} + {7, 2, 1} = {5, 7, 2, 1})
```

---

### Визуализация: Почему O(2^(n/2)) лучше O(2^n)

```
n = 40 элементов

Brute Force O(2^n):
  2^40 = 1,099,511,627,776 операций
                 ↓
          [очень много!]

Meet in the Middle O(2^(n/2) × n):
  2^20 × 40 = 1,048,576 × 40 = 41,943,040 операций
                        ↓
                   [терпимо]

Сравнение:
  2^40      = 1,099,511,627,776
  2^20 × 40 =        41,943,040
                          ↓
              Разница: 26,000x быстрее!

Почему так работает?
┌──────────────────────────────────────────────────────────┐
│  Вместо умножения:  2^20 × 2^20 = 2^40                   │
│  Делаем сложение:   2^20 + 2^20 + O(комбинирование)      │
│                                                          │
│  Аналогия: Площадь 1000×1000 = 1,000,000                 │
│            Периметр 2×(1000+1000) = 4,000                │
│            Мы "меряем периметр", а не "заполняем площадь"│
└──────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему это сложно

### Типичные ошибки студентов

#### Ошибка 1: Неравные половины

```kotlin
// ❌ НЕПРАВИЛЬНО — одна половина слишком большая
val left = nums.sliceArray(0 until 10)      // 2^10 = 1024
val right = nums.sliceArray(10 until 40)    // 2^30 ≈ 10^9 — слишком много!

// ✅ ПРАВИЛЬНО — делим РАВНО пополам
val left = nums.sliceArray(0 until n / 2)   // 2^20 = 10^6
val right = nums.sliceArray(n / 2 until n)  // 2^20 = 10^6

СИМПТОМ: Одна половина слишком медленная, общее время не улучшилось
РЕШЕНИЕ: Всегда дели n/2 и n/2 (или n/2 и n/2+1)
```

#### Ошибка 2: Забыли отсортировать для бинарного поиска

```kotlin
// ❌ НЕПРАВИЛЬНО
val rightSums = generateAllSums(right)
val idx = rightSums.binarySearch(target)  // НЕВЕРНЫЙ РЕЗУЛЬТАТ!

// Binary search ТРЕБУЕТ отсортированный массив!
// На неотсортированном — undefined behavior

// ✅ ПРАВИЛЬНО
val rightSums = generateAllSums(right).sorted()  // ← СОРТИРОВКА!
val idx = rightSums.binarySearch(target)

СИМПТОМ: Бинарный поиск возвращает неправильные индексы
РЕШЕНИЕ: ВСЕГДА сортируй массив перед binarySearch
```

#### Ошибка 3: Проверяем только точное совпадение

```kotlin
// ❌ НЕПРАВИЛЬНО — только точное совпадение
val idx = rightSums.binarySearch(needed)
if (idx >= 0) {  // Только если нашли ТОЧНО нужное
    answer = leftSum + rightSums[idx]
}

// Для задач "closest" или "≤ target" нужны СОСЕДИ!

// ✅ ПРАВИЛЬНО — проверяем оба соседних значения
val insertPoint = rightSums.binarySearch(needed).let {
    if (it >= 0) it else -(it + 1)
}

// Проверяем элемент НА позиции (если ≤ needed)
if (insertPoint < rightSums.size) {
    checkCandidate(rightSums[insertPoint])
}
// И элемент ДО позиции (последний ≤ needed)
if (insertPoint > 0) {
    checkCandidate(rightSums[insertPoint - 1])
}

СИМПТОМ: Не находим оптимальный ответ для "closest" задач
РЕШЕНИЕ: Проверяй insertPoint и insertPoint - 1
```

#### Ошибка 4: Переполнение при больших суммах

```kotlin
// ❌ НЕПРАВИЛЬНО — Int overflow
// nums[i] может быть до 10^9, сумма 40 элементов = 4×10^10 > Int.MAX_VALUE
var sum = 0  // Int, максимум 2×10^9
for (num in nums) sum += num  // OVERFLOW!

// ✅ ПРАВИЛЬНО — используем Long
var sum = 0L  // Long, максимум 9×10^18
for (num in nums) sum += num

СИМПТОМ: Неправильные суммы, отрицательные числа из ниоткуда
РЕШЕНИЕ: Для n ≤ 40 и nums[i] ≤ 10^9 ВСЕГДА используй Long
```

#### Ошибка 5: Пропускаем пустое подмножество

```kotlin
// ❌ НЕПРАВИЛЬНО — начинаем с mask = 1
for (mask in 1 until (1 shl n)) {  // Пропускаем mask = 0!
    // ...
}
// Пустое подмножество с суммой 0 — валидный вариант!

// ✅ ПРАВИЛЬНО — включаем mask = 0
for (mask in 0 until (1 shl n)) {
    // mask = 0 соответствует пустому подмножеству, сумма = 0
}

СИМПТОМ: Не находим ответ, когда нужно взять элементы только из одной половины
РЕШЕНИЕ: Начинай с mask = 0 (пустое подмножество)
```

#### Ошибка 6: Не понимаем, когда MITM применим

```kotlin
// ❌ НЕПРАВИЛЬНО — применяем MITM когда не нужно
// Задача: n = 100 элементов, каждый 0-1000
// MITM: O(2^50) — слишком медленно!
// Но DP: O(n × sum) = O(100 × 100000) = 10^7 — быстро!

// MITM применим когда:
// 1. n ≤ 40 (иначе 2^(n/2) всё ещё слишком много)
// 2. target слишком большой для DP (> 10^6)
// 3. Задача "делится на две независимые половины"

СИМПТОМ: MITM медленнее наивного решения
РЕШЕНИЕ: Проверь ограничения! MITM для 20 < n ≤ 40 и большого target
```

---

## Часть 3: Ментальные модели

### Модель 1: "Два фронта наступления"

```
Военная стратегия: атака с двух сторон одновременно

ВРАГ (все 2^n комбинаций)
         ▼
┌─────────────────────────────────────┐
│                                     │
│    ←←←← ЛЕВЫЙ        ПРАВЫЙ ←←←←    │
│         ФРОНТ         ФРОНТ         │
│         (2^(n/2))     (2^(n/2))     │
│                                     │
│              ОКРУЖЕНИЕ!             │
│                                     │
└─────────────────────────────────────┘

Каждый фронт продвигается на 2^(n/2) "позиций"
Когда фронты встречаются — задача решена

Время: 2^(n/2) + 2^(n/2) = 2 × 2^(n/2)
       вместо 2^n (один фронт до самого конца)
```

### Модель 2: "Телефонная книга с двух концов"

```
Задача: Найти пару чисел A + B = target

Обычный поиск:
  Для каждого A проверяем все B → O(n²)

MITM подход:
  1. Сортируем все B и записываем в "книгу"
  2. Для каждого A ищем target - A в "книге" за O(log n)

  Время: O(n log n) вместо O(n²)

Расширение для подмножеств:
  1. Все суммы левой половины → "левая книга"
  2. Все суммы правой половины → "правая книга" (отсортированная)
  3. Для каждой суммы из левой книги ищем complement в правой
```

### Модель 3: "Промежуточные состояния"

```
Криптографический MITM:

Шифрование E с ключом K:
  Plaintext → [E_K1] → Intermediate → [E_K2] → Ciphertext
              ╰──────────╯            ╰──────────╯
                Левая                   Правая
               половина                половина

Атака:
  1. Перебираем K1, вычисляем Intermediate от Plaintext
  2. Перебираем K2, вычисляем Intermediate от Ciphertext (обратно!)
  3. Если Intermediate совпадает — ключи найдены!

В subset sum:
  Plaintext = 0 (начальная сумма)
  Ciphertext = target (целевая сумма)
  Intermediate = leftSum = target - rightSum
```

### Модель 4: "Квадратный корень"

```
Главный математический инсайт:

  2^n = 2^(n/2) × 2^(n/2)   ← умножение (Brute Force)

  но

  2^n >> 2^(n/2) + 2^(n/2)  ← сложение (MITM)

Пример с n = 40:
  2^40 = 2^20 × 2^20 = 1,099,511,627,776
  2^20 + 2^20 = 2,097,152

MITM берёт "квадратный корень" от exponential:
  √(2^n) = 2^(n/2)

Это как площадь vs периметр:
  Площадь квадрата 1000×1000 = 1,000,000
  Периметр = 4000
  Но хватает проверить ПЕРИМЕТР, а не всю ПЛОЩАДЬ!
```

### Модель 5: "Два списка покупок"

```
Задача: Выбрать продукты на фиксированный бюджет (≈ subset sum)

40 продуктов, бюджет = 1000 рублей

Стратегия "перебрать всё":
  2^40 комбинаций — невозможно!

Стратегия MITM:
  Список 1: Первые 20 продуктов
            Выписываем все 2^20 возможных сумм чеков
            Сортируем по цене

  Список 2: Последние 20 продуктов
            Тоже 2^20 сумм

  Комбинирование:
            Для каждой суммы S1 из Списка 1
            Ищем в Списке 2 максимальную S2 такую, что S1 + S2 ≤ 1000
            Используем бинарный поиск!

  Результат: Набор продуктов с максимальной общей ценой ≤ бюджета
```

---

## Зачем это нужно?

**Реальная проблема:**

Массив из 40 чисел, каждое до 10^9. Найти максимальную сумму подмножества ≤ S (S до 10^18). Brute force: 2^40 ≈ 10^12 — слишком медленно. DP: требует O(S) памяти — невозможно. Meet in the Middle: 2^20 × 20 ≈ 2×10^7 — выполнимо!

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| Криптография | Brute force attacks | MITM attack on block ciphers |
| Соцсети | Friend of friend | 6 degrees of separation |
| Игры | Pathfinding | Bidirectional A* |
| Combinatorics | Subset problems | Closest subset sum |
| Competitive | Large N problems | N ≤ 40 constraint |

**Статистика:**
- Редкий паттерн, но критически важен для определённых задач
- Появляется в ~5% Hard задач LeetCode
- Сигнал для использования: n ≤ 40, exponential search space

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Binary Search** | Для комбинирования результатов двух половин | [[binary-search-pattern]] |
| **Bitmask Enumeration** | Для генерации всех подмножеств | [[bit-manipulation]] |
| **HashMap** | Альтернатива binary search для exact match | [[hash-tables]] |
| **Big O нотация** | Понимание O(2^n) vs O(2^(n/2)) | [[big-o-complexity]] |
| **CS: Subset Generation** | 2^n подмножеств через bitmask | Комбинаторика |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что тебе нужно найти путь из твоего дома в школу друга через огромный город. Вместо того чтобы искать весь путь из дома, можно:
1. Ты идёшь из дома и отмечаешь все места, куда можешь дойти за полпути
2. Друг идёт из школы и отмечает свои места
3. Если вы встретитесь на каком-то месте — путь найден!

```
        ┌──────────┐
  ДОМ ──┤ Встреча! ├── ШКОЛА
        └──────────┘
   →→→→→             ←←←←←
  Половина        Половина
   пути            пути
```

### Формальное определение

**Meet in the Middle** — алгоритмическая техника, которая:
1. Разбивает пространство поиска на две равные части
2. Генерирует все возможные решения для каждой части: O(2^(n/2))
3. Комбинирует частичные решения для получения полного

**Когда применим:**
- Exponential search space (2^n варианта)
- n в диапазоне 20-45 (brute force слишком медленный, но память для 2^(n/2) достаточна)
- Результаты двух половин можно эффективно скомбинировать (сортировка + бинарный поиск)

**Complexity improvement:**
```
Brute force:  O(2^n)
Meet in Middle: O(2^(n/2) × log(2^(n/2))) = O(2^(n/2) × n)

Для n = 40:
  Brute force: 2^40 ≈ 10^12 операций
  MITM:        2^20 × 40 ≈ 4 × 10^7 операций

  Ускорение: ~25,000x!
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **Left half** | Первая половина входных данных | nums[0..n/2) |
| **Right half** | Вторая половина входных данных | nums[n/2..n) |
| **Left sums** | Все возможные суммы подмножеств left | 2^(n/2) значений |
| **Right sums** | Все возможные суммы подмножеств right | 2^(n/2) значений |
| **Combine** | Этап объединения результатов | Binary search / Two pointers |
| **Target complement** | target - leftSum | Ищем в right sums |

---

## Как это работает?

### Subset Sum ≤ S

```
Задача: nums = [1, 3, 5, 7, 2, 4], S = 12
Найти максимальную сумму подмножества ≤ S

Шаг 1: Разделить на половины
  left = [1, 3, 5]
  right = [7, 2, 4]

Шаг 2: Генерируем все суммы подмножеств left
  {} → 0
  {1} → 1
  {3} → 3
  {1,3} → 4
  {5} → 5
  {1,5} → 6
  {3,5} → 8
  {1,3,5} → 9

  leftSums = [0, 1, 3, 4, 5, 6, 8, 9]

Шаг 3: Генерируем все суммы подмножеств right
  rightSums = [0, 2, 4, 6, 7, 9, 11, 13]

Шаг 4: Сортируем rightSums
  rightSums = [0, 2, 4, 6, 7, 9, 11, 13]

Шаг 5: Для каждой leftSum ищем лучшую rightSum
  Нужно: leftSum + rightSum ≤ 12
  Эквивалентно: rightSum ≤ 12 - leftSum

  leftSum=0: rightSum ≤ 12, max rightSum = 11 → total = 11
  leftSum=1: rightSum ≤ 11, max rightSum = 11 → total = 12 ✓
  leftSum=3: rightSum ≤ 9, max rightSum = 9 → total = 12 ✓
  leftSum=4: rightSum ≤ 8, max rightSum = 7 → total = 11
  leftSum=5: rightSum ≤ 7, max rightSum = 7 → total = 12 ✓
  leftSum=6: rightSum ≤ 6, max rightSum = 6 → total = 12 ✓
  leftSum=8: rightSum ≤ 4, max rightSum = 4 → total = 12 ✓
  leftSum=9: rightSum ≤ 3, max rightSum = 2 → total = 11

Ответ: 12
```

**Визуализация:**

```
        Left half                Right half
      {1, 3, 5}                 {7, 2, 4}
          │                         │
          ▼                         ▼
    ┌─────────────┐          ┌─────────────┐
    │ Generate    │          │ Generate    │
    │ 2³ = 8 sums │          │ 2³ = 8 sums │
    └─────────────┘          └─────────────┘
          │                         │
          └────────┬────────────────┘
                   │
                   ▼
           ┌─────────────┐
           │   Combine   │
           │ Binary Search│
           │ O(2³ × 3)   │
           └─────────────┘
                   │
                   ▼
              Answer: 12
```

### 4SUM via Meet in the Middle

```
Задача: Найти a + b + c + d = target

Стандартный подход: O(n³) с сортировкой + two pointers

Meet in the Middle подход: O(n²)
1. Генерируем все пары a+b → leftPairSums
2. Генерируем все пары c+d → rightPairSums
3. Для каждой leftSum ищем target - leftSum в rightSums

Пример: nums = [1, 2, 3, 4], target = 10

leftPairs:
  (1,2) → 3
  (1,3) → 4
  (1,4) → 5
  (2,3) → 5
  (2,4) → 6
  (3,4) → 7

rightPairs: (те же числа, но храним отдельно для поиска)

Ищем: leftSum + rightSum = 10
  3 + 7 = 10 ✓ → (1,2,3,4)
```

### Bidirectional BFS (6 Degrees of Separation)

```
Задача: Найти кратчайший путь между двумя узлами в графе

Стандартный BFS: O(b^d), где b = branching factor, d = depth

Bidirectional BFS: O(b^(d/2))

     Start                          End
       │                             │
       ▼                             ▼
   Level 1 ←───────────────────→ Level 1
       │                             │
       ▼                             ▼
   Level 2 ←───────────────────→ Level 2
       │                             │
       └──────────┬──────────────────┘
                  │
            Meeting point!

Если d = 6 и b = 100:
  BFS: 100^6 = 10^12
  Bidirectional: 2 × 100^3 = 2 × 10^6

Ускорение: ~500,000x!
```

---

## Сложность операций

| Подход | Time | Space | Применимость |
|--------|------|-------|--------------|
| Brute Force | O(2^n) | O(n) | n ≤ 20 |
| Meet in Middle | O(2^(n/2) × n) | O(2^(n/2)) | 20 < n ≤ 40 |
| DP | O(n × target) | O(target) | target маленький |
| Bidirectional BFS | O(b^(d/2)) | O(b^(d/2)) | Графы с высоким branching |

**Когда MITM лучше:**
- n > 20 (brute force слишком медленный)
- target слишком большой для DP (> 10^6)
- Можно эффективно скомбинировать половины

---

## Реализация

### Closest Subsequence Sum (Kotlin)

```kotlin
/**
 * CLOSEST SUBSEQUENCE SUM — найти подмножество с суммой, ближайшей к goal
 *
 * Идея Meet in the Middle:
 * 1. Делим массив пополам: left и right
 * 2. Генерируем все 2^(n/2) сумм для каждой половины
 * 3. Для каждой суммы из left ищем лучшую пару в right через binary search
 *
 * Сложность: O(2^(n/2) × n) вместо O(2^n)
 * Для n=40: 2^20 × 40 ≈ 4×10^7 вместо 2^40 ≈ 10^12
 */
fun minAbsDifference(nums: IntArray, goal: Int): Int {
    val n = nums.size

    // MITM: разделяем массив на две РАВНЫЕ половины
    // Равные — для минимизации max(2^(n/2)), т.к. 2^20 + 2^20 < 2^19 + 2^21
    val left = nums.sliceArray(0 until n / 2)
    val right = nums.sliceArray(n / 2 until n)

    // Генерируем ВСЕ возможные суммы подмножеств каждой половины
    // Для массива из k элементов — 2^k сумм (включая пустое подмножество)
    val leftSums = generateAllSums(left).sorted()
    val rightSums = generateAllSums(right).sorted()

    var minDiff = Long.MAX_VALUE

    // Для каждой суммы из левой половины ищем оптимальную пару в правой
    for (ls in leftSums) {
        val target = goal - ls  // Нужно найти rightSum ≈ target

        // Binary search: находим позицию, где rightSum ≈ target
        // binarySearch возвращает: положительный индекс если найдено,
        // иначе -(insertion_point + 1)
        val idx = rightSums.binarySearch(target).let {
            if (it >= 0) it else -(it + 1)
        }

        // Проверяем ОБА соседних элемента: idx и idx-1
        // Один из них даст минимальную разницу с target
        if (idx < rightSums.size) {
            minDiff = minOf(minDiff, kotlin.math.abs(goal - (ls + rightSums[idx])))
        }
        if (idx > 0) {
            minDiff = minOf(minDiff, kotlin.math.abs(goal - (ls + rightSums[idx - 1])))
        }
    }

    return minDiff.toInt()
}

/**
 * Генерирует все 2^n сумм подмножеств массива
 *
 * Использует bitmask enumeration:
 * - mask от 0 до 2^n - 1
 * - Бит i в mask = 1 означает "включить arr[i] в подмножество"
 *
 * Пример: arr = [1, 3, 5]
 * mask=0 (000): {} → 0
 * mask=1 (001): {1} → 1
 * mask=2 (010): {3} → 3
 * mask=3 (011): {1,3} → 4
 * mask=4 (100): {5} → 5
 * ...
 */
private fun generateAllSums(arr: IntArray): List<Long> {
    val sums = mutableListOf<Long>()
    val n = arr.size

    // Bitmask enumeration: перебираем все 2^n комбинаций
    for (mask in 0 until (1 shl n)) {
        var sum = 0L
        for (i in 0 until n) {
            // Проверяем, установлен ли бит i в маске
            if ((mask shr i) and 1 == 1) {
                sum += arr[i]
            }
        }
        sums.add(sum)
    }

    return sums
}
```

### Subset Sum ≤ Target (Maximum) (Kotlin)

```kotlin
/**
 * MAX SUBSET SUM ≤ TARGET — найти максимальную сумму подмножества, не превышающую target
 *
 * Отличие от Closest Sum: здесь нужен МАКСИМУМ ≤ target, а не ближайший
 * Используем upperBound вместо обычного binarySearch
 */
fun maxSubsetSum(nums: IntArray, target: Long): Long {
    val n = nums.size
    val mid = n / 2

    // Списки для хранения всех сумм подмножеств каждой половины
    val leftSums = mutableListOf<Long>()
    val rightSums = mutableListOf<Long>()

    /**
     * Рекурсивная генерация всех сумм подмножеств
     *
     * Для каждого элемента есть 2 выбора: включить или не включить
     * Это даёт 2^n вариантов — все подмножества
     */
    fun generate(idx: Int, end: Int, sum: Long, sums: MutableList<Long>) {
        if (idx == end) {
            sums.add(sum)
            return
        }
        // Ветка 1: НЕ включаем nums[idx]
        generate(idx + 1, end, sum, sums)
        // Ветка 2: включаем nums[idx]
        generate(idx + 1, end, sum + nums[idx], sums)
    }

    generate(0, mid, 0L, leftSums)
    generate(mid, n, 0L, rightSums)

    // Сортируем правую половину для бинарного поиска
    rightSums.sort()

    var maxSum = 0L

    for (ls in leftSums) {
        if (ls > target) continue  // Сама левая сумма уже превышает target

        val remaining = target - ls  // Сколько ещё можем добавить

        // Ищем МАКСИМАЛЬНЫЙ rightSum ≤ remaining
        // upperBound даёт первый индекс, где значение > remaining
        // Значит, idx - 1 — это максимальное значение ≤ remaining
        val idx = upperBound(rightSums, remaining) - 1

        if (idx >= 0) {
            maxSum = maxOf(maxSum, ls + rightSums[idx])
        }
    }

    return maxSum
}

/**
 * UPPER BOUND — первый индекс, где arr[idx] > value
 *
 * Эквивалент std::upper_bound в C++
 * Возвращает позицию ПОСЛЕ последнего элемента ≤ value
 *
 * Пример: arr = [1, 3, 5, 7], value = 5
 * upperBound = 3 (первый индекс где arr > 5, т.е. позиция 7)
 * upperBound - 1 = 2 (максимальный элемент ≤ 5, т.е. сама 5)
 */
private fun upperBound(arr: List<Long>, value: Long): Int {
    var lo = 0
    var hi = arr.size
    while (lo < hi) {
        val mid = (lo + hi) / 2
        if (arr[mid] <= value) lo = mid + 1  // Ищем СТРОГО больше
        else hi = mid
    }
    return lo
}
```

### 4Sum II (Java)

```java
/**
 * 4SUM II — сколько четвёрок (i, j, k, l) дают A[i]+B[j]+C[k]+D[l] = 0?
 *
 * Meet in the Middle подход:
 * 1. "Левая половина": все суммы A[i] + B[j] → HashMap с частотами
 * 2. "Правая половина": для каждой суммы C[k] + D[l] ищем complement
 *
 * Сложность: O(n²) вместо O(n⁴) brute force
 *
 * Пример: A=[1,2], B=[-2,-1], C=[-1,2], D=[0,2]
 * leftSums: {-1: 2, 0: 1, 1: 1}  (1-2=-1, 2-2=0, 1-1=0, 2-1=1)
 * Ищем: -(C[k]+D[l]) в leftSums
 */
public int fourSumCount(int[] A, int[] B, int[] C, int[] D) {
    // Храним все суммы A[i] + B[j] с их ЧАСТОТОЙ
    // Частота важна: может быть несколько пар с одинаковой суммой
    Map<Integer, Integer> leftSums = new HashMap<>();

    for (int a : A) {
        for (int b : B) {
            int sum = a + b;
            leftSums.merge(sum, 1, Integer::sum);  // +1 к счётчику
        }
    }

    int count = 0;

    // Для каждой пары из правой половины ищем complement в левой
    for (int c : C) {
        for (int d : D) {
            // Нужно: A[i] + B[j] + C[k] + D[l] = 0
            // Значит: A[i] + B[j] = -(C[k] + D[l])
            int target = -(c + d);
            count += leftSums.getOrDefault(target, 0);
        }
    }

    return count;
}
```

### Bidirectional BFS (Python)

```python
"""
BIDIRECTIONAL BFS — поиск кратчайшего пути с двух сторон

Идея: вместо одного BFS от start к end, запускаем два BFS:
- Один от start вглубь
- Другой от end вглубь
Когда frontiers встречаются — путь найден!

Почему быстрее?
- Обычный BFS: O(b^d), где b = branching factor, d = глубина
- Bidirectional: O(2 × b^(d/2)) = O(b^(d/2))

Пример: граф социальной сети, b = 100 друзей, d = 6
- BFS: 100^6 = 10^12 узлов
- Bidirectional: 2 × 100^3 = 2 × 10^6 узлов

Ускорение: ~500,000x!
"""
from collections import deque

def bidirectional_bfs(graph: dict, start: int, end: int) -> int:
    """Returns shortest path length, or -1 if no path."""
    if start == end:
        return 0

    # Два "фронта" поиска — множества узлов на текущем уровне
    front_start = {start}  # Фронт от начальной точки
    front_end = {end}      # Фронт от конечной точки

    # Отдельные множества посещённых для каждого направления
    # Нужны раздельные, чтобы определить момент встречи
    visited_start = {start}
    visited_end = {end}

    distance = 0

    while front_start and front_end:
        distance += 1

        # ОПТИМИЗАЦИЯ: всегда расширяем МЕНЬШИЙ фронт
        # Это балансирует работу и минимизирует общее число узлов
        if len(front_start) > len(front_end):
            front_start, front_end = front_end, front_start
            visited_start, visited_end = visited_end, visited_start

        # Расширяем текущий фронт на один уровень
        new_front = set()
        for node in front_start:
            for neighbor in graph.get(node, []):
                # КЛЮЧЕВОЙ МОМЕНТ: если сосед уже в другом фронте —
                # фронты встретились! Путь найден!
                if neighbor in visited_end:
                    return distance

                if neighbor not in visited_start:
                    visited_start.add(neighbor)
                    new_front.add(neighbor)

        front_start = new_front

    return -1  # Фронты не встретились — пути нет
```

### Equal Partition Check (Kotlin)

```kotlin
/**
 * CAN PARTITION — можно ли разделить массив на два с равной суммой?
 *
 * Эквивалентно: существует ли подмножество с суммой = total / 2?
 *
 * MITM подход: генерируем суммы для обеих половин,
 * ищем пару leftSum + rightSum = target в HashSet за O(1)
 *
 * Пример: nums = [1, 5, 11, 5], total = 22, target = 11
 * leftSums (из [1,5]): {0, 1, 5, 6}
 * rightSums (из [11,5]): {0, 5, 11, 16}
 * Ищем: leftSum + rightSum = 11
 * Находим: 0 + 11 = 11 ✓ или 6 + 5 = 11 ✓
 */
fun canPartition(nums: IntArray): Boolean {
    val total = nums.sum()

    // Если общая сумма НЕЧЁТНАЯ — разделить поровну невозможно математически
    if (total % 2 != 0) return false

    val target = total / 2
    val n = nums.size
    val mid = n / 2

    // HashSet для O(1) проверки наличия нужной суммы
    val leftSums = hashSetOf<Int>()
    val rightSums = hashSetOf<Int>()

    fun generate(idx: Int, end: Int, sum: Int, sums: HashSet<Int>) {
        if (idx == end) {
            sums.add(sum)
            return
        }
        generate(idx + 1, end, sum, sums)
        generate(idx + 1, end, sum + nums[idx], sums)
    }

    generate(0, mid, 0, leftSums)
    generate(mid, n, 0, rightSums)

    // Для каждой leftSum проверяем, есть ли нужный complement в rightSums
    // leftSum + rightSum = target → rightSum = target - leftSum
    for (ls in leftSums) {
        if (rightSums.contains(target - ls)) {
            return true
        }
    }

    return false
}
```

---

## Распространённые ошибки

### 1. Неправильное разделение на половины

```kotlin
// ❌ НЕПРАВИЛЬНО: неравные половины могут быть неоптимальны
val left = nums.sliceArray(0 until n / 3)
val right = nums.sliceArray(n / 3 until n)

// ✅ ПРАВИЛЬНО: делим пополам
val left = nums.sliceArray(0 until n / 2)
val right = nums.sliceArray(n / 2 until n)
```

### 2. Забыть отсортировать для binary search

```kotlin
// ❌ НЕПРАВИЛЬНО: binary search на неотсортированном массиве
val rightSums = generateAllSums(right)
rightSums.binarySearch(target)  // Неверный результат!

// ✅ ПРАВИЛЬНО: сортируем перед binary search
val rightSums = generateAllSums(right).sorted()
rightSums.binarySearch(target)
```

### 3. Overflow при больших суммах

```kotlin
// ❌ НЕПРАВИЛЬНО: Int overflow при суммах > 2^31
var sum = 0  // Int
for (num in nums) sum += num

// ✅ ПРАВИЛЬНО: используем Long
var sum = 0L
for (num in nums) sum += num
```

### 4. Не проверять оба соседа в binary search

```kotlin
// ❌ НЕПРАВИЛЬНО: проверяем только точное совпадение
val idx = rightSums.binarySearch(target)
if (idx >= 0) result = rightSums[idx]

// ✅ ПРАВИЛЬНО: проверяем ближайших соседей
val idx = rightSums.binarySearch(target).let { if (it >= 0) it else -(it + 1) }
if (idx < rightSums.size) checkCandidate(rightSums[idx])
if (idx > 0) checkCandidate(rightSums[idx - 1])
```

### 5. Не учитывать пустое подмножество

```kotlin
// ❌ НЕПРАВИЛЬНО: начинаем с mask = 1
for (mask in 1 until (1 shl n)) { ... }  // пропускаем пустое подмножество!

// ✅ ПРАВИЛЬНО: включаем пустое подмножество (mask = 0)
for (mask in 0 until (1 shl n)) { ... }
```

---

## Когда использовать

### Decision Tree

```
Задача с exponential search space (2^n)?
│
├─ n ≤ 20?
│   └─ Brute force / Backtracking O(2^n)
│
├─ 20 < n ≤ 40?
│   │
│   ├─ Можно разделить на две независимые части?
│   │   │
│   │   ├─ Результаты комбинируются суммой/разностью?
│   │   │   └─ Meet in the Middle + Binary Search
│   │   │
│   │   └─ Нужен точный match?
│   │       └─ Meet in the Middle + HashSet
│   │
│   └─ Нельзя разделить?
│       └─ Другие оптимизации (pruning, DP если target маленький)
│
└─ n > 40?
    └─ Скорее всего, есть polynomial решение или NP-hard
```

### MITM vs Alternatives

| Задача | MITM | Alternative | Когда лучше |
|--------|------|-------------|-------------|
| Subset Sum | O(2^(n/2) × n) | DP O(n × target) | MITM: большой target |
| 4Sum | O(n²) | Sort + 2ptr O(n³) | MITM: всегда лучше |
| Shortest Path | O(b^(d/2)) | BFS O(b^d) | MITM: high branching |
| Partition | O(2^(n/2)) | DP O(n × sum/2) | Depends on sum |

---

## Практика

### Концептуальные вопросы

1. **Почему MITM даёт O(2^(n/2)) вместо O(2^n)?**
   - Вместо 2^n комбинаций генерируем 2×2^(n/2)
   - Комбинирование через сортировку + binary search: O(2^(n/2) × n)
   - 2^(n/2) × n << 2^n для n > 20

2. **Можно ли разделить на более чем 2 части?**
   - Теоретически да, но редко выгодно
   - 3 части: O(3 × 2^(n/3)) + комбинирование
   - Комбинирование становится сложнее

3. **Когда bidirectional BFS лучше обычного BFS?**
   - Когда branching factor высокий (много соседей)
   - Когда начальная и конечная точки известны
   - Не работает: shortest path ко всем вершинам

### LeetCode задачи

| # | Название | Сложность | Паттерн | Ключевая идея |
|---|----------|-----------|---------|---------------|
| 1755 | Closest Subsequence Sum | Hard | MITM + BS | n ≤ 40, goal ≤ 10^9 |
| 805 | Split Array Same Average | Hard | MITM | Equal average check |
| 454 | 4Sum II | Medium | MITM pairs | HashMap O(n²) |
| 2035 | Partition Array Min Diff | Hard | MITM + BS | Two halves sum |
| 18 | 4Sum | Medium | Sort + 2ptr | But MITM possible |

### Порядок изучения

```
1. 454. 4Sum II (Medium) — базовый MITM с HashMap
2. 1755. Closest Subsequence Sum (Hard) — классический MITM
3. 2035. Partition Array Min Diff (Hard) — продвинутый MITM
4. 805. Split Array Same Average (Hard) — MITM с дробями
```

---

## Связанные темы

### Prerequisites (изучить до)
- **Binary Search** — для комбинирования результатов
- **Bitmask enumeration** — для генерации подмножеств
- **HashMap** — альтернатива binary search для точного match

### Unlocks (откроет путь к)
- **Cryptographic attacks** — MITM attack on ciphers
- **Advanced pathfinding** — A* с bidirectional search
- **Competitive programming** — задачи с ограничением n ≤ 40

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "MITM подходит для любого n" | **Нет!** Работает для n ≤ 40. Для n > 40 даже O(2^(n/2)) слишком медленно. Для n ≤ 20 проще brute force |
| "Всегда делим ровно пополам" | **Обычно да, но не обязательно!** Для несбалансированных задач можно делить по-другому, но n/2 обычно оптимально |
| "MITM = Divide and Conquer" | **Похоже, но не то же!** D&C рекурсивно делит, MITM делит один раз и комбинирует. MITM — для exponential search space |
| "Только для subset sum" | **Шире!** 4Sum, bidirectional BFS, closest pair of sums, многие NP-hard задачи с малым n |
| "Binary Search обязателен" | **HashMap тоже работает!** Для exact match HashMap проще. BS нужен для closest/lower bound |
| "Memory не проблема" | **Может быть!** O(2^(n/2)) элементов = миллионы для n=40. Нужно учитывать memory limit |
| "MITM — редкий паттерн" | **Да, но узнаваемый!** n ≤ 40 + exponential = сигнал. В competitive programming частый |
| "Сложно реализовать" | **Шаблон простой!** Generate half1, sort, for each in half2: binary search complement. ~20 строк кода |

---

## CS-фундамент

| CS-концепция | Применение в Meet in the Middle |
|--------------|--------------------------------|
| **Exponential to Sqrt-Exponential** | O(2^n) → O(2^(n/2) × log(2^(n/2))) = O(2^(n/2) × n). Квадратный корень от exponential |
| **Subset Enumeration** | Bitmask от 0 до 2^(n/2)-1. Каждый бит = включён/исключён элемент. Генерация всех подмножеств |
| **Binary Search Combination** | Sort one half, for each sum in other half: binary search for complement (target - sum) |
| **Space-Time Tradeoff** | Храним O(2^(n/2)) сумм первой половины. Trade memory for time. Классический tradeoff |
| **Bidirectional Search** | В графах: BFS от start и от end. Встреча в середине = path found. O(b^(d/2)) вместо O(b^d) |
| **Hash-Based Alternative** | Вместо sort + binary search: HashMap для O(1) lookup. Проще, но не для closest match |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/meet-in-the-middle/) | Tutorial | Базовый алгоритм |
| 2 | [USACO Guide](https://usaco.guide/gold/meet-in-the-middle) | Guide | Competitive programming |
| 3 | [LeetCode Discuss](https://leetcode.com/discuss/interview-question/2077168/meet-in-the-middle-algorithm-subset-bitmask/) | Discussion | Interview problems |
| 4 | [Codeforces](https://codeforces.com/blog/entry/95571) | Blog | Advanced applications |

---

## Куда дальше

→ **Связанный паттерн:** [[binary-search-pattern]] — для комбинирования результатов
→ **Альтернатива:** [[dp-patterns]] — для больших n с overlapping subproblems
→ **Вернуться к:** [[patterns-overview|Обзор паттернов]]

---

*Обновлено: 2026-01-08 — добавлены педагогические секции (интуиция MITM: толпа/сейф/рюкзак, 6 типичных ошибок, 5 ментальных моделей)*
