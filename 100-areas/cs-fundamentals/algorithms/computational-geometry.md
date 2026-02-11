---
title: "Вычислительная геометрия"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/expert
related:
  - "[[divide-and-conquer]]"
  - "[[sorting-algorithms]]"
prerequisites:
  - "[[sorting-algorithms]]"
  - "[[divide-and-conquer]]"
  - "[[binary-search-pattern]]"
---

# Computational Geometry

## 1. Обзор и Мотивация

### Что такое вычислительная геометрия

Computational Geometry — раздел алгоритмов, работающих с геометрическими объектами: точками, отрезками, многоугольниками, кругами. В competitive programming геометрия считается одной из сложнейших тем из-за:
- Edge cases (коллинеарные точки, касания, degeneracy)
- Floating-point precision errors
- Большого количества формул для запоминания

### Почему это важно

```
ICPC World Finals: геометрия в каждом контесте
Codeforces: редко в Div.2, часто в Div.1
Google Code Jam: регулярные геометрические задачи

Критично понимать:
- Базовые операции (cross/dot product)
- Convex hull для многих оптимизационных задач
- Precision handling для избежания WA
```

### Реальные применения

| Область | Применение |
|---------|-----------|
| Computer Graphics | Рендеринг, clipping, collision detection |
| GIS | Карты, GPS, polygon operations |
| Robotics | Motion planning, obstacle avoidance |
| CAD | Дизайн, boolean operations |
| Game Development | Physics, hit detection |

---

## Часть 1: Интуиция без кода

### Аналогия 1: Cross Product как "правило правой руки"

Представьте, что вы стоите в точке A и смотрите на точку B. Приходит точка C — она слева от вас или справа?

```
Вы стоите в A, смотрите на B. Где C?

      C                           C
     ↗                             ↖
    /                               \
   A ──────► B                  A ──────► B

   C СЛЕВА от AB              C СПРАВА от AB
   cross > 0 (CCW)            cross < 0 (CW)
```

**Cross product = ваш "внутренний компас":**
- Положительный → точка слева (против часовой)
- Отрицательный → точка справа (по часовой)
- Ноль → точка прямо впереди или позади (на одной прямой)

**Правило правой руки в физике:**
Если пальцы правой руки загнуть от вектора A к вектору B, большой палец покажет направление A × B. В 2D это "вверх" (+) или "вниз" (-).

### Аналогия 2: Convex Hull как "резинка вокруг гвоздей"

Вбейте N гвоздей в доску случайным образом. Натяните резинку вокруг ВСЕХ гвоздей и отпустите.

```
До:                          После (резинка):
    •       •                    •───────•
       •                        / \       \
  •        •    →              •   •       •
      •  •                      \     \   /
    •                            •─────•─•

Все точки внутри           Резинка = Convex Hull
```

**Резинка:**
- Всегда образует ВЫПУКЛЫЙ многоугольник
- Проходит только через "крайние" точки
- Внутренние точки не влияют на форму

**Почему "выпуклый"?** Резинка не может "загнуться внутрь" — она стремится к минимальной длине, а кратчайший путь между двумя точками — прямая линия.

### Аналогия 3: Point in Polygon как "выход из лабиринта"

Вы в тёмной комнате и не знаете, внутри вы здания или снаружи. Идите прямо (стреляйте лучом) и считайте, сколько стен пересечёте.

```
Снаружи здания:              Внутри здания:
      ┌────┐                       ┌────┐
  P ──┼────┼──► (2 стены)          │  P─┼──► (1 стена)
      │    │                       │    │
      └────┘                       └────┘

   ЧЁТНОЕ = снаружи            НЕЧЁТНОЕ = внутри
```

**Теорема Жордана:** Любая замкнутая кривая делит плоскость на "внутри" и "снаружи". Каждое пересечение границы — переход между этими областями.

**Почему это работает:**
- Снаружи → внутрь → снаружи → внутрь → ...
- Начинаем снаружи (бесконечность)
- После нечётного числа переходов = внутри

### Аналогия 4: Rotating Calipers как "штангенциркуль"

Представьте огромный штангенциркуль, который измеряет расстояние между двумя параллельными губками.

```
    ═══════════════════  ← верхняя губка
         ●━━━━━━●
        ╱        ╲
       ●          ●  ← antipodal (противоположные) точки
        ╲        ╱
         ●━━━━━━●
    ═══════════════════  ← нижняя губка

    Вращаем штангенциркуль вокруг фигуры
```

**Как найти диаметр (максимальное расстояние):**
1. Приставьте губки к фигуре с двух сторон
2. Медленно вращайте штангенциркуль вокруг фигуры
3. Записывайте расстояние между губками
4. Максимум — это диаметр!

**Ключевой инсайт:** При вращении губки всегда касаются "antipodal" точек — пар вершин, между которыми проходят параллельные опорные прямые. Таких пар всего O(n), поэтому алгоритм линейный.

### Аналогия 5: Shoelace Formula как "площадь между графиком и осью"

Формула Shoelace ("шнуровка") вычисляет площадь как сумму трапеций между многоугольником и осью X.

```
Многоугольник:              Разбиение на трапеции:
    B                           B
   /\                          /|\
  /  \                        / | \
 /    \                      /  |  \
A──────C                    A──────C
                               │  │
                            ───┴──┴─── ось X

Трапеция под AB: + (идём вправо)
Трапеция под BC: + (идём вправо)
Трапеция под CA: - (идём влево!)

Сумма = площадь внутри (отрицательные части вычитаются)
```

**Почему "шнуровка"?** Формула перемножает координаты крест-накрест, как шнуровка ботинка:

```
x₁×y₂ - x₂×y₁
x₂×y₃ - x₃×y₂
x₃×y₁ - x₁×y₃
──────────────
    Σ / 2 = Площадь
```

---

## Часть 2: Почему это сложно

### Ошибка 1: Сравнение doubles через `==`

**СИМПТОМ:** Алгоритм работает на примерах из условия, но даёт WA на тестах. Точки, которые должны быть коллинеарны — не коллинеарны.

```kotlin
// ❌ НЕПРАВИЛЬНО — никогда не работает надёжно
if (cross(a, b, c) == 0.0) {
    // коллинеарны... или нет?
}

// Реальность:
val x = 0.1 + 0.2   // = 0.30000000000000004
x == 0.3            // FALSE!
```

**РЕШЕНИЕ:** Всегда используйте EPS для сравнения:

```kotlin
// ✅ ПРАВИЛЬНО
const val EPS = 1e-9

fun Double.eq(other: Double) = kotlin.math.abs(this - other) < EPS

if (cross(a, b, c).eq(0.0)) {
    // действительно коллинеарны
}
```

---

### Ошибка 2: Overflow в Cross Product

**СИМПТОМ:** Неверные знаки cross product, алгоритм "сходит с ума" на больших координатах.

```kotlin
// Координаты до 10^9 — кажется, помещается в Int...
val a = Point(1_000_000_000, 1_000_000_000)
val b = Point(0, 0)
val c = Point(1_000_000_000, 999_999_999)

// cross = 10^9 × 10^9 = 10^18 — OVERFLOW для Int!
// Int.MAX_VALUE ≈ 2 × 10^9
```

**РЕШЕНИЕ:** Используйте Long для целочисленных координат:

```kotlin
// ✅ ПРАВИЛЬНО
fun crossLong(o: LongPoint, a: LongPoint, b: LongPoint): Long {
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
}
// Long.MAX_VALUE ≈ 9 × 10^18 — помещается!
```

---

### Ошибка 3: Игнорирование Degenerate Cases

**СИМПТОМ:** Алгоритм падает или даёт WA на "особых" входах — коллинеарные точки, совпадающие точки, вырожденные многоугольники.

```kotlin
// ❌ НЕПРАВИЛЬНО — не обрабатывает коллинеарность
fun convexHull(points: List<Point>): List<Point> {
    // Что если ВСЕ точки на одной прямой?
    // Что если несколько точек совпадают?
    // ...
}
```

**Типичные degenerate cases:**
- Все точки коллинеарны (hull = отрезок или точка)
- Несколько точек совпадают
- Нулевая площадь многоугольника
- Параллельные отрезки при пересечении

**РЕШЕНИЕ:** Явно проверяйте и обрабатывайте:

```kotlin
// ✅ ПРАВИЛЬНО
fun convexHull(points: List<Point>): List<Point> {
    if (points.size < 3) return points  // degenerate
    // ... основной алгоритм ...
}
```

---

### Ошибка 4: Неправильный EPS для масштаба координат

**СИМПТОМ:** EPS 1e-9 не работает для больших координат (10^6 и выше).

```kotlin
// Координаты порядка 10^9
val a = 1_000_000_000.0
val b = 1_000_000_000.0 + 1e-7  // отличие в 7-м знаке

// С EPS = 1e-9:
(a - b).eq(0.0)  // FALSE! Но по смыслу они "равны"

// Проблема: 1e-9 слишком строгий для таких масштабов
// Относительная погрешность double ≈ 10^-15
// Для координат 10^9: абсолютная погрешность ≈ 10^-6
```

**РЕШЕНИЕ:** Выбирайте EPS в зависимости от масштаба:

```kotlin
// Правило большого пальца:
// EPS ≈ 10^(log₁₀(max_coord) - 15)

// Координаты до 10³: EPS = 1e-9 ✓
// Координаты до 10⁶: EPS = 1e-6
// Координаты до 10⁹: EPS = 1e-3 или переходите на Long
```

---

### Ошибка 5: Domain Error в acos/asin

**СИМПТОМ:** NaN или RuntimeException при вычислении углов.

```kotlin
// ❌ НЕПРАВИЛЬНО
fun angle(a: Point, b: Point): Double {
    val cosAngle = dot(a, b) / (a.length() * b.length())
    return acos(cosAngle)  // CRASH если cosAngle = 1.00000001
}

// Из-за ошибок округления cosAngle может выйти за [-1, 1]:
// acos(1.0000001) = NaN
// acos(-1.0000001) = NaN
```

**РЕШЕНИЕ:** Ограничивайте аргумент:

```kotlin
// ✅ ПРАВИЛЬНО
fun angle(a: Point, b: Point): Double {
    val cosAngle = dot(a, b) / (a.length() * b.length())
    return acos(cosAngle.coerceIn(-1.0, 1.0))  // безопасно!
}
```

---

### Ошибка 6: Незамкнутый многоугольник в Shoelace

**СИМПТОМ:** Площадь многоугольника неверная, часто сильно меньше ожидаемой.

```kotlin
// ❌ НЕПРАВИЛЬНО — забыли последнее ребро
fun polygonArea(points: List<Point>): Double {
    var area = 0.0
    for (i in 0 until points.size - 1) {  // пропустили n-1 → 0!
        area += cross(points[i], points[i + 1])
    }
    return abs(area) / 2
}

// Не учтено ребро от последней точки к первой!
```

**РЕШЕНИЕ:** Используйте модульную арифметику для индексов:

```kotlin
// ✅ ПРАВИЛЬНО
fun polygonArea(points: List<Point>): Double {
    var area = 0.0
    val n = points.size
    for (i in 0 until n) {
        val j = (i + 1) % n  // замыкает: n-1 → 0
        area += cross(points[i], points[j])
    }
    return abs(area) / 2
}
```

---

## Часть 3: Ментальные модели

### Модель 1: Cross Product как детектор поворота

**Концепция:** Cross product отвечает на вопрос "в какую сторону поворачивать?"

```
Представьте, что вы ведёте машину по маршруту A → B → C:

       C                C
      ↗               ↖
     /                 \
    B                   B
   ↗                   ↗
  /                   /
 A                   A

cross(A,B,C) > 0     cross(A,B,C) < 0
Поворот НАЛЕВО      Поворот НАПРАВО
(против часовой)    (по часовой)
```

**Применения:**
- Convex hull: удаляем точки, где нужно повернуть "не туда"
- Orientation: CCW vs CW обход многоугольника
- Point in polygon: подсчёт пересечений через знаки

### Модель 2: Sweep Line как "машина времени"

**Концепция:** Вертикальная прямая движется слева направо, и события происходят в "моменты времени" = x-координаты.

```
Время →
t=0    t=1    t=2    t=3

│      │      │      │
│  ●   │  ●───┼──●   │
│ ╱╲   │     ╲│      │
│╱  ╲──┼──────┼──────│
│      │      │      │

События:
t=0: начало отрезка 1
t=1: начало отрезка 2, пересечение
t=2: конец отрезка 1
t=3: конец отрезка 2
```

**Что sweep line "видит":** В каждый момент времени — набор отрезков, пересекающих вертикаль. Поддерживаем этот набор в BST, отсортированном по y.

**Применения:**
- Пересечение N отрезков: O((n+k) log n) вместо O(n²)
- Closest pair: O(n log n)
- Union of rectangles: O(n log n)

### Модель 3: Convex Hull как "граница возможностей"

**Концепция:** Convex hull — это множество "экстремальных" точек в любом направлении.

```
Вопрос: какая точка максимальна в направлении d⃗?

    d⃗ →
                     ●  ← эта! (на hull)
         ●  ●       ╱
        ●    ●     ╱
       ●  ●●  ●   ╱
        ●    ●   ╱
         ●  ●   ╱

Ответ всегда на convex hull!
```

**Почему важно:** Многие оптимизационные задачи сводятся к поиску на convex hull:
- Максимальный скалярный продукт с вектором
- CHT (Convex Hull Trick) в DP
- Линейное программирование в 2D

### Модель 4: Precision как "размытие"

**Концепция:** Floating-point числа — не точки, а "облака" погрешности.

```
Математически:      В компьютере:
    ●                  ⚫
    |                 ╱│╲
    |                ╱ │ ╲
────┼────           ╱  │  ╲
    0            EPS зона неопределённости

"Точка" 0.0 на самом деле — интервал [-EPS, +EPS]
```

**Следствия:**
- `a == b` заменяем на `|a - b| < EPS`
- "На прямой" означает "достаточно близко к прямой"
- Порядок операций влияет на результат

**Правило:** Представляйте каждое число как интервал шириной 2×EPS. Если интервалы пересекаются — числа "равны".

### Модель 5: Дуальность точка-прямая

**Концепция:** Каждой точке (a, b) соответствует прямая y = ax + b, и наоборот.

```
Прямая y = ax + b    ←→    Точка (a, b) в двойственном пространстве

Три точки коллинеарны ←→ Три прямые пересекаются в одной точке
```

**Почему полезно:**
- Задача о прямых превращается в задачу о точках
- Half-plane intersection ←→ Convex hull в двойственном
- Линейное программирование: минимизация = поиск вершины

**Пример трансформации:**
```
Задача: найти прямую, проходящую через максимум точек
→ В двойственном: найти точку, через которую проходит максимум прямых
→ Это intersection всех прямых!
```

---

## 2. Базовые примитивы

### Point и Vector

```kotlin
/**
 * data class для автоматического equals(), hashCode(), copy()
 * Point используется и как точка, и как вектор
 */
data class Point(val x: Double, val y: Double) {
    /**
     * Операторы для векторной арифметики через operator overloading
     * Позволяет писать: val c = a + b вместо val c = Point(a.x + b.x, a.y + b.y)
     */
    operator fun plus(other: Point) = Point(x + other.x, y + other.y)
    operator fun minus(other: Point) = Point(x - other.x, y - other.y)
    operator fun times(scalar: Double) = Point(x * scalar, y * scalar)

    fun length() = sqrt(x * x + y * y)

    /**
     * Квадрат длины — избегаем sqrt когда возможно!
     * sqrt() дорогая операция. Для сравнения расстояний
     * достаточно сравнить квадраты: dist1² < dist2² ⟺ dist1 < dist2
     */
    fun lengthSquared() = x * x + y * y

    /**
     * Нормализация вектора (длина = 1)
     * Нужна для unit vectors (направлений)
     */
    fun normalize(): Point {
        val len = length()
        return if (len > EPS) Point(x / len, y / len) else Point(0.0, 0.0)
    }
}

/**
 * Epsilon для сравнения floating-point чисел
 * 10⁻⁹ подходит для большинства геометрических задач
 */
const val EPS = 1e-9

/**
 * Безопасное сравнение doubles с учётом погрешности
 * НИКОГДА не сравнивайте doubles через == напрямую!
 */
fun Double.eq(other: Double) = kotlin.math.abs(this - other) < EPS
fun Double.lt(other: Double) = this < other - EPS
fun Double.gt(other: Double) = this > other + EPS
```

### Cross Product (Векторное произведение 2D)

```kotlin
/**
 * Cross product в 2D возвращает скаляр (z-компонента 3D cross product)
 *
 * WHY: Фундаментальная операция для:
 * - Определения ориентации (по/против часовой)
 * - Площади треугольника/параллелограмма
 * - Проверки коллинеарности
 *
 * cross > 0: поворот против часовой (CCW)
 * cross < 0: поворот по часовой (CW)
 * cross = 0: коллинеарны
 */
fun cross(a: Point, b: Point): Double = a.x * b.y - a.y * b.x

// Cross product для трех точек: (b-a) × (c-a)
fun cross(a: Point, b: Point, c: Point): Double {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
}

/**
 * Знак cross product определяет ориентацию трёх точек:
 *
 * Визуализация для a → b → c:
 *
 *     c              c
 *    /              \
 *   b      vs        b
 *  /                  \
 * a                    a
 *
 * CCW (+1)           CW (-1)
 */
fun orientation(a: Point, b: Point, c: Point): Int {
    val cr = cross(a, b, c)
    return when {
        cr.gt(0.0) -> 1   // CCW (counter-clockwise, против часовой)
        cr.lt(0.0) -> -1  // CW (clockwise, по часовой)
        else -> 0          // Collinear (на одной прямой)
    }
}
```

### Dot Product (Скалярное произведение)

```kotlin
/**
 * Dot product: a · b = |a| × |b| × cos(θ)
 *
 * WHY: Используется для:
 * - Угла между векторами
 * - Проекции вектора
 * - Проверки перпендикулярности (dot = 0)
 */
fun dot(a: Point, b: Point): Double = a.x * b.x + a.y * b.y

// Угол между векторами (в радианах)
fun angle(a: Point, b: Point): Double {
    val cosAngle = dot(a, b) / (a.length() * b.length())
    /**
     * coerceIn(-1.0, 1.0) — защита от precision errors!
     *
     * Из-за погрешности cosAngle может быть 1.0000001 или -1.0000001
     * acos() для таких значений вернёт NaN!
     * Поэтому ограничиваем диапазон [-1, 1]
     */
    return kotlin.math.acos(cosAngle.coerceIn(-1.0, 1.0))
}

// Знаковый угол от a к b (с учетом направления)
fun signedAngle(a: Point, b: Point): Double {
    return kotlin.math.atan2(cross(a, b), dot(a, b))
}
```

### Визуализация Cross и Dot Product

```
Cross Product (a × b):
       b
      /
     /  cross > 0 (CCW)
    /
   a────────→
    \
     \  cross < 0 (CW)
      \
       b

Dot Product (a · b):
   a · b > 0: острый угол (< 90°)
   a · b = 0: прямой угол (= 90°)
   a · b < 0: тупой угол (> 90°)
```

---

## 3. Площадь многоугольника (Shoelace Formula)

### Теория

Формула Shoelace (Гаусса) вычисляет **signed area** многоугольника по координатам вершин. Называется "шнуровкой" из-за перекрестного умножения координат.

```
        n-1
Area = ½ × |Σ (x_i × y_{i+1} - x_{i+1} × y_i)|
        i=0

Эквивалентно:
        n-1
Area = ½ × |Σ cross(p_i, p_{i+1})|
        i=0
```

### Почему это работает

Каждое ребро AB вносит signed area треугольника ABO (O = origin). При обходе многоугольника положительные и отрицательные area взаимно сокращаются, оставляя только площадь внутри.

```kotlin
/**
 * Shoelace formula для площади многоугольника
 *
 * Time: O(n)
 *
 * ВАЖНО: вершины должны быть упорядочены (CW или CCW)!
 * Возвращает unsigned area (модуль)
 *
 * ПОШАГОВЫЙ ПРИМЕР для квадрата [(0,0), (4,0), (4,3), (0,3)]:
 * cross((0,0), (4,0)) = 0*0 - 4*0 = 0
 * cross((4,0), (4,3)) = 4*3 - 4*0 = 12
 * cross((4,3), (0,3)) = 4*3 - 0*3 = 12
 * cross((0,3), (0,0)) = 0*0 - 0*3 = 0
 * signedArea = 0 + 12 + 12 + 0 = 24
 * Area = |24| / 2 = 12 ✓
 */
fun polygonArea(points: List<Point>): Double {
    val n = points.size
    if (n < 3) return 0.0

    var signedArea = 0.0
    for (i in 0 until n) {
        val j = (i + 1) % n
        // cross(p_i, p_{i+1}) = x_i * y_{i+1} - x_{i+1} * y_i
        signedArea += cross(points[i], points[j])
    }

    return kotlin.math.abs(signedArea) / 2.0
}

/**
 * Signed area — положительна для CCW, отрицательна для CW
 *
 * Полезно для определения ориентации многоугольника:
 * signedArea > 0 → вершины идут против часовой стрелки
 * signedArea < 0 → вершины идут по часовой стрелке
 */
fun signedPolygonArea(points: List<Point>): Double {
    val n = points.size
    if (n < 3) return 0.0

    var area = 0.0
    for (i in 0 until n) {
        val j = (i + 1) % n
        area += cross(points[i], points[j])
    }

    return area / 2.0
}

// Проверка ориентации многоугольника по знаку площади
fun isCounterClockwise(points: List<Point>): Boolean {
    return signedPolygonArea(points) > 0
}
```

### Площадь треугольника

```kotlin
/**
 * Площадь треугольника по трем вершинам
 *
 * Частный случай Shoelace formula, но эффективнее —
 * всего одно вычисление cross product
 *
 * Area = |cross(b-a, c-a)| / 2
 */
fun triangleArea(a: Point, b: Point, c: Point): Double {
    return kotlin.math.abs(cross(a, b, c)) / 2.0
}

/**
 * Signed area треугольника
 *
 * Положительна если a → b → c идут CCW (против часовой)
 * Отрицательна если a → b → c идут CW (по часовой)
 */
fun signedTriangleArea(a: Point, b: Point, c: Point): Double {
    return cross(a, b, c) / 2.0
}
```

---

## 4. Point in Polygon

### Два основных подхода

| Алгоритм | Сложность | Особенности |
|----------|----------|-------------|
| Ray Casting | O(n) | Простой, работает для simple polygons |
| Winding Number | O(n) | Корректен для self-intersecting polygons |

### Ray Casting Algorithm

Бросаем луч из точки вправо и считаем пересечения с границей:
- **Нечетное** число пересечений → точка внутри
- **Четное** число пересечений → точка снаружи

```kotlin
/**
 * Ray Casting / Crossing Number algorithm
 *
 * Time: O(n)
 *
 * ИДЕЯ АЛГОРИТМА:
 * Пускаем луч из точки вправо (в направлении +X) и считаем
 * сколько раз он пересекает границу многоугольника.
 *
 * Луч вправо — самый простой случай:
 * - Не нужно обрабатывать вертикальные рёбра (dx=0)
 * - Простая формула пересечения
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *        ┌────┐
 *   P ───┼────┼───> (луч вправо)
 *        │    │
 *   ─────┴────┘
 *        2 пересечения = СНАРУЖИ (чётное)
 *
 *        ┌────┐
 *        │ P ─┼───> (луч вправо)
 *        │    │
 *   ─────┴────┘
 *        1 пересечение = ВНУТРИ (нечётное)
 * ```
 *
 * @return true если точка строго внутри многоугольника
 */
fun pointInPolygon(point: Point, polygon: List<Point>): Boolean {
    val n = polygon.size
    if (n < 3) return false

    var crossings = 0

    for (i in 0 until n) {
        val a = polygon[i]
        val b = polygon[(i + 1) % n]

        /**
         * Проверяем только рёбра, пересекающие горизонталь через point.
         *
         * Условие (a.y <= point.y && b.y > point.y):
         *   - Ребро идёт ВВЕРХ (a ниже или на уровне, b выше)
         *   - "Upward crossing"
         *
         * Условие (a.y > point.y && b.y <= point.y):
         *   - Ребро идёт ВНИЗ (a выше, b ниже или на уровне)
         *   - "Downward crossing"
         *
         * Строгие/нестрогие неравенства подобраны так, чтобы
         * вершина считалась только один раз!
         */
        if ((a.y <= point.y && b.y > point.y) ||
            (a.y > point.y && b.y <= point.y)) {

            /**
             * Вычисляем X-координату пересечения луча с ребром.
             *
             * Луч: горизонтальная линия y = point.y
             * Ребро: линия от a до b
             *
             * Параметрическое уравнение ребра:
             *   x = a.x + t * (b.x - a.x)
             *   y = a.y + t * (b.y - a.y)
             *
             * При y = point.y:
             *   t = (point.y - a.y) / (b.y - a.y)
             *
             * Подставляем t:
             *   xIntersect = a.x + (point.y - a.y) * (b.x - a.x) / (b.y - a.y)
             */
            val slope = (b.x - a.x) / (b.y - a.y)
            val xIntersect = a.x + slope * (point.y - a.y)

            if (point.x < xIntersect) {
                crossings++
            }
        }
    }

    /**
     * Теорема Жордана:
     * - Нечётное число пересечений → точка ВНУТРИ
     * - Чётное число пересечений → точка СНАРУЖИ
     *
     * crossings % 2 == 1 проверяет нечётность
     */
    return crossings % 2 == 1
}

/**
 * Проверка: лежит ли точка на границе многоугольника
 */
fun pointOnPolygonBoundary(point: Point, polygon: List<Point>): Boolean {
    val n = polygon.size
    for (i in 0 until n) {
        val a = polygon[i]
        val b = polygon[(i + 1) % n]
        if (pointOnSegment(point, a, b)) return true
    }
    return false
}

/**
 * Проверка: лежит ли точка на отрезке AB
 *
 * ДВУХЭТАПНАЯ ПРОВЕРКА:
 * 1. Коллинеарность — точка на той же прямой, что и AB
 * 2. Bounding box — точка между A и B
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *   A ────────●──────── B     p на отрезке ✓
 *             p
 *
 *   A ──────────────── B   ●  p вне отрезка ✗
 *                          p  (коллинеарна, но за пределами)
 *
 *             ●  p            p вне отрезка ✗
 *   A ──────────────── B      (не коллинеарна)
 * ```
 */
fun pointOnSegment(p: Point, a: Point, b: Point): Boolean {
    /**
     * ШАГ 1: Проверяем коллинеарность (точки на одной прямой)
     *
     * cross(a, b, p) = 0 означает, что векторы AB и AP параллельны,
     * т.е. точка p лежит на прямой AB.
     *
     * Если cross ≠ 0, точка точно не на отрезке.
     */
    if (!cross(a, b, p).eq(0.0)) return false

    /**
     * ШАГ 2: Проверяем, что точка внутри bounding box отрезка AB
     *
     * Коллинеарность гарантирует, что p на прямой AB,
     * но нужно убедиться, что p между A и B, а не за ними.
     *
     * Проверяем: min(a.x, b.x) <= p.x <= max(a.x, b.x)
     *            min(a.y, b.y) <= p.y <= max(a.y, b.y)
     *
     * EPS добавляется для учёта погрешности вычислений.
     */
    return p.x >= minOf(a.x, b.x) - EPS &&
           p.x <= maxOf(a.x, b.x) + EPS &&
           p.y >= minOf(a.y, b.y) - EPS &&
           p.y <= maxOf(a.y, b.y) + EPS
}
```

### Winding Number Algorithm

```kotlin
/**
 * Winding Number algorithm
 *
 * Time: O(n)
 *
 * ПРЕИМУЩЕСТВО над Ray Casting:
 * Работает корректно для self-intersecting polygons!
 * Считает сколько раз многоугольник "обматывает" точку.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *      ┌───┐
 *      │ ┌─┼─┐       wn = 2 (обмотка дважды)
 *      │ │ P │ │
 *      │ └─┼─┘
 *      └───┘
 *
 *    ┌───────┐
 *    │       │        wn = 1 (обмотка один раз)
 *    │   P   │
 *    │       │
 *    └───────┘
 *
 *        P             wn = 0 (снаружи)
 *    ┌───────┐
 *    │       │
 *    └───────┘
 * ```
 *
 * АЛГОРИТМ:
 * - Обходим рёбра многоугольника
 * - Если ребро пересекает горизонталь ВВЕРХ и точка СЛЕВА → +1
 * - Если ребро пересекает горизонталь ВНИЗ и точка СПРАВА → -1
 *
 * @return winding number (0 = outside, non-zero = inside)
 */
fun windingNumber(point: Point, polygon: List<Point>): Int {
    val n = polygon.size
    var wn = 0  // winding number

    for (i in 0 until n) {
        val a = polygon[i]
        val b = polygon[(i + 1) % n]

        if (a.y <= point.y) {
            /**
             * Upward crossing: ребро идёт ВВЕРХ
             * (a на уровне или ниже point, b выше point)
             *
             *       b
             *      /
             *  ───P───  ← горизонталь через point
             *    /
             *   a
             */
            if (b.y > point.y) {
                /**
                 * cross(a, b, point) > 0 означает:
                 * point находится СЛЕВА от направленного ребра a→b
                 *
                 * Это значит луч ВПРАВО из point пересекает ребро,
                 * и обход против часовой → увеличиваем winding number
                 */
                if (cross(a, b, point) > 0) {
                    wn++
                }
            }
        } else {
            /**
             * Downward crossing: ребро идёт ВНИЗ
             * (a выше point, b на уровне или ниже)
             *
             *   a
             *    \
             *  ───P───  ← горизонталь через point
             *      \
             *       b
             */
            if (b.y <= point.y) {
                /**
                 * cross(a, b, point) < 0 означает:
                 * point находится СПРАВА от направленного ребра a→b
                 *
                 * Это значит луч ВПРАВО из point пересекает ребро,
                 * и обход по часовой → уменьшаем winding number
                 */
                if (cross(a, b, point) < 0) {
                    wn--
                }
            }
        }
    }

    return wn
}

fun isInsideWindingNumber(point: Point, polygon: List<Point>): Boolean {
    return windingNumber(point, polygon) != 0
}
```

---

## 5. Convex Hull

### Определение

**Convex Hull** (выпуклая оболочка) — минимальный выпуклый многоугольник, содержащий все точки множества. Аналогия: резинка, натянутая вокруг гвоздей.

### Алгоритмы

| Алгоритм | Время | Особенности |
|----------|-------|-------------|
| Gift Wrapping (Jarvis) | O(nh) | h = размер hull, плохо для больших h |
| Graham Scan | O(n log n) | Сортировка по полярному углу |
| Andrew's Monotone Chain | O(n log n) | Сортировка по x, более стабильный |
| Quickhull | O(n log n) avg | Divide & Conquer |

### Graham Scan

```kotlin
/**
 * Graham Scan Algorithm
 *
 * Time: O(n log n)
 * Space: O(n)
 *
 * ИДЕЯ АЛГОРИТМА:
 * 1. Находим "якорную" точку (самую нижнюю)
 * 2. Сортируем остальные точки по полярному углу относительно якоря
 * 3. Обходим точки по порядку, строя выпуклую оболочку через стек
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *        3
 *       /
 *      2       Сортировка по углу: start → 1 → 2 → 3 → 4
 *     /
 *   start ─── 1 ─── 4
 * ```
 *
 * При обходе удаляем точки, которые создают "вогнутость"
 * (правый поворот / clockwise).
 */
fun grahamScan(points: List<Point>): List<Point> {
    if (points.size < 3) return points.toList()

    /**
     * Находим самую НИЖНЮЮ точку (минимальный y).
     * При равенстве y — самую ЛЕВУЮ (минимальный x).
     *
     * Эта точка ГАРАНТИРОВАННО на convex hull!
     * Она станет началом (якорем) для сортировки.
     */
    val start = points.minWithOrNull(compareBy({ it.y }, { it.x }))!!

    /**
     * Сортируем по ПОЛЯРНОМУ УГЛУ относительно start.
     *
     * cross(start, a, b) > 0 → a левее b (меньший угол) → a первым
     * cross(start, a, b) < 0 → b левее a → b первым
     * cross(start, a, b) = 0 → коллинеарны
     *
     * Полярный угол = угол между вектором (start→точка) и осью X.
     */
    val sorted = points.filter { it != start }
        .sortedWith { a, b ->
            val cross = cross(start, a, b)
            when {
                cross.gt(0.0) -> -1  // a before b (CCW)
                cross.lt(0.0) -> 1   // b before a
                else -> {
                    /**
                     * Коллинеарные точки: на одном луче из start.
                     * Ставим БЛИЖНЮЮ первой — иначе можем "перепрыгнуть"
                     * точку на hull и потерять её.
                     */
                    val distA = (a - start).lengthSquared()
                    val distB = (b - start).lengthSquared()
                    distA.compareTo(distB)
                }
            }
        }

    /**
     * Стек для построения hull.
     *
     * Инвариант: точки в стеке образуют CCW-поворачивающую ломаную.
     */
    val hull = mutableListOf<Point>()
    hull.add(start)

    for (p in sorted) {
        /**
         * Удаляем точки с вершины стека, пока добавление p
         * создаёт ПРАВЫЙ поворот (CW) или коллинеарность.
         *
         * cross(second, top, p) <= 0 означает:
         * - < 0: правый поворот (CW) — top вне hull
         * - = 0: коллинеарны — top не нужна (не вершина hull)
         *
         * ВИЗУАЛИЗАЦИЯ:
         * ```
         *     p               p
         *    /               /
         *   top      →   second
         *  /
         * second          (top удалена!)
         * ```
         */
        while (hull.size >= 2) {
            val top = hull[hull.size - 1]
            val second = hull[hull.size - 2]
            if (cross(second, top, p) <= 0) {
                hull.removeLast()
            } else {
                break
            }
        }
        hull.add(p)
    }

    return hull
}
```

### Andrew's Monotone Chain (Recommended)

```kotlin
/**
 * Andrew's Monotone Chain Algorithm
 *
 * Time: O(n log n)
 * Space: O(n)
 *
 * ПРЕИМУЩЕСТВА над Graham Scan:
 * 1. Сортировка по (x, y) — простая и стабильная
 * 2. Строит lower и upper hull ОТДЕЛЬНО — легче отлаживать
 * 3. Меньше проблем с точностью (нет вычисления углов)
 *
 * ИДЕЯ АЛГОРИТМА:
 * ```
 *     upper hull
 *    ╱─────────╲
 *   ╱           ╲
 *  ●─────────────●   ← крайние точки (min x, max x)
 *   ╲           ╱
 *    ╲─────────╱
 *     lower hull
 * ```
 *
 * Строим две "цепочки":
 * - Lower hull: слева направо по отсортированным точкам
 * - Upper hull: справа налево (обратный обход)
 */
fun convexHull(points: List<Point>): List<Point> {
    val n = points.size
    if (n < 3) return points.toList()

    /**
     * Лексикографическая сортировка: сначала по x, затем по y.
     *
     * Результат: точки упорядочены "слева направо" (и снизу вверх при равных x).
     * Первая точка — левая нижняя, последняя — правая верхняя.
     */
    val sorted = points.sortedWith(compareBy({ it.x }, { it.y }))

    val hull = mutableListOf<Point>()

    /**
     * LOWER HULL: обходим слева направо.
     *
     * Для каждой точки: пока последние 2 точки в hull
     * создают правый поворот (CW) с текущей — удаляем последнюю.
     *
     * Результат: нижняя граница выпуклой оболочки.
     */
    for (p in sorted) {
        while (hull.size >= 2) {
            val top = hull[hull.size - 1]
            val second = hull[hull.size - 2]
            /**
             * cross <= 0 означает:
             * - < 0: правый поворот (CW) — вогнутость
             * - = 0: коллинеарны — средняя точка не нужна
             *
             * Удаляем top, потому что она "внутри" hull.
             */
            if (cross(second, top, p) <= 0) {
                hull.removeLast()
            } else {
                break
            }
        }
        hull.add(p)
    }

    /**
     * UPPER HULL: обходим справа налево (от n-2 до 0).
     *
     * Пропускаем последнюю точку (n-1), т.к. она уже в lower hull.
     * lowerSize запоминаем, чтобы не трогать lower hull при удалении.
     */
    val lowerSize = hull.size
    for (i in n - 2 downTo 0) {
        val p = sorted[i]
        while (hull.size > lowerSize) {
            val top = hull[hull.size - 1]
            val second = hull[hull.size - 2]
            if (cross(second, top, p) <= 0) {
                hull.removeLast()
            } else {
                break
            }
        }
        hull.add(p)
    }

    /**
     * Удаляем последнюю точку — это дубликат первой!
     *
     * Upper hull заканчивается в точке sorted[0],
     * которая уже есть в начале lower hull.
     */
    hull.removeLast()

    return hull
}

/**
 * Вариант с включением коллинеарных точек на hull
 *
 * КОГДА НУЖНО:
 * - Нужно знать ВСЕ точки на границе, не только вершины
 * - Задачи на подсчёт точек на границе многоугольника
 * - Формула Пика: A = i + b/2 - 1 (b = точки на границе)
 *
 * ОТЛИЧИЕ ОТ СТАНДАРТНОГО:
 * Используем строгое < вместо <=, чтобы НЕ удалять коллинеарные точки.
 */
fun convexHullWithCollinear(points: List<Point>): List<Point> {
    val n = points.size
    if (n < 3) return points.toList()

    val sorted = points.sortedWith(compareBy({ it.x }, { it.y }))

    val hull = mutableListOf<Point>()

    // Lower hull (используем < вместо <=)
    for (p in sorted) {
        while (hull.size >= 2) {
            val top = hull[hull.size - 1]
            val second = hull[hull.size - 2]
            /**
             * Строго < (без =) для сохранения коллинеарных точек.
             *
             * cross = 0 означает: second, top, p на одной прямой.
             * При <= мы бы удалили top.
             * При < мы оставляем top — все точки на ребре сохраняются!
             */
            if (cross(second, top, p) < 0) {
                hull.removeLast()
            } else {
                break
            }
        }
        hull.add(p)
    }

    // Upper hull
    val lowerSize = hull.size
    for (i in n - 2 downTo 0) {
        val p = sorted[i]
        while (hull.size > lowerSize) {
            val top = hull[hull.size - 1]
            val second = hull[hull.size - 2]
            if (cross(second, top, p) < 0) {
                hull.removeLast()
            } else {
                break
            }
        }
        hull.add(p)
    }

    hull.removeLast()
    return hull
}
```

### Визуализация Convex Hull

```
    *           *
   / \         /|\
  /   \   →   / | \
 *     *     *  |  *
  \   /       \ | /
   \ /         \|/
    *           *

Points      Convex Hull
```

---

## 6. Closest Pair of Points

### Divide and Conquer подход

Наивный O(n²) можно улучшить до **O(n log n)** с помощью divide and conquer.

```
1. Сортируем точки по x
2. Делим на две половины
3. Рекурсивно находим min distance в каждой
4. Берем минимум d
5. Проверяем "strip" — точки в полосе ±d от линии раздела
6. В strip каждая точка сравнивается с максимум 7 соседями (доказано!)
```

```kotlin
/**
 * Closest Pair of Points — O(n log n)
 *
 * ИДЕЯ DIVIDE AND CONQUER:
 * 1. Делим точки вертикальной линией пополам
 * 2. Рекурсивно находим минимум в каждой половине
 * 3. Проверяем пары через границу в "полосе" (strip)
 *
 * КЛЮЧЕВОЙ ИНСАЙТ:
 * В полосе шириной 2d может быть максимум 8 точек в прямоугольнике d × 2d!
 * Доказательство: если бы было больше, расстояние между двумя из них было бы < d,
 * что противоречит определению d как минимума в половинах.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *    left  │ right
 *          │
 *     •    │  •     d = min в каждой половине
 *       •  │    •
 *     •    │•       ← эти точки в "strip" могут дать меньший d
 *          │
 *    ◄──d──┼──d──►  полоса шириной 2d
 * ```
 */
fun closestPair(points: List<Point>): Double {
    if (points.size < 2) return Double.MAX_VALUE

    /**
     * Предсортировка по X — для разделения на половины.
     * O(n log n) один раз, не в каждой рекурсии!
     */
    val sortedByX = points.sortedBy { it.x }

    /**
     * Предсортировка по Y — для быстрой фильтрации strip.
     * Сохраняем порядок при merge, избегая O(n log n) сортировки на каждом уровне.
     */
    val sortedByY = points.sortedBy { it.y }

    return closestPairRecursive(sortedByX, sortedByY)
}

private fun closestPairRecursive(
    byX: List<Point>,
    byY: List<Point>
): Double {
    val n = byX.size

    /**
     * Base case: для 2-3 точек используем brute force O(1).
     * Накладные расходы рекурсии не стоят того для малых n.
     */
    if (n <= 3) {
        return bruteForceClosest(byX)
    }

    val mid = n / 2
    val midPoint = byX[mid]

    /**
     * DIVIDE: разделяем точки по X-координате.
     * midPoint.x — вертикальная линия раздела.
     */
    val leftX = byX.subList(0, mid)
    val rightX = byX.subList(mid, n)

    /**
     * Фильтруем byY для каждой половины, СОХРАНЯЯ порядок по Y.
     * Это ключ к O(n log n): не пересортируем, а фильтруем за O(n).
     */
    val leftY = byY.filter { it.x <= midPoint.x }
    val rightY = byY.filter { it.x > midPoint.x }

    /**
     * CONQUER: рекурсивно находим минимум в каждой половине.
     */
    val dLeft = closestPairRecursive(leftX, leftY)
    val dRight = closestPairRecursive(rightX, rightY)
    var d = minOf(dLeft, dRight)

    /**
     * COMBINE: собираем "strip" — точки в пределах d от линии раздела.
     *
     * Только эти точки могут дать пару с расстоянием < d,
     * потому что точки дальше d от линии не могут быть ближе d
     * к точкам по другую сторону.
     */
    val strip = byY.filter {
        kotlin.math.abs(it.x - midPoint.x) < d
    }

    /**
     * Проверяем пары в strip.
     * Благодаря сортировке по Y, каждая точка сравнивается
     * максимум с 7 следующими (доказано геометрически).
     */
    d = stripClosest(strip, d)

    return d
}

private fun stripClosest(strip: List<Point>, d: Double): Double {
    var minD = d
    val n = strip.size

    for (i in 0 until n) {
        /**
         * Проверяем только следующие точки, пока разница по Y < d.
         *
         * ДОКАЗАТЕЛЬСТВО, что достаточно 7:
         * В прямоугольнике d × 2d (разделённом линией) может быть
         * максимум 8 точек (4 слева, 4 справа в сетке d/2 × d/2).
         * Одна из них — текущая, остаётся проверить 7.
         *
         * ```
         *   d
         * ┌─┬─┐
         * │•│•│  ← макс 4 точки слева
         * ├─┼─┤
         * │•│•│
         * ├─┼─┤  2d
         * │•│•│  ← макс 4 точки справа
         * ├─┼─┤
         * │•│•│
         * └─┴─┘
         * ```
         */
        var j = i + 1
        while (j < n && strip[j].y - strip[i].y < minD) {
            val dist = distance(strip[i], strip[j])
            if (dist < minD) {
                minD = dist
            }
            j++
        }
    }

    return minD
}

private fun bruteForceClosest(points: List<Point>): Double {
    var minDist = Double.MAX_VALUE
    for (i in points.indices) {
        for (j in i + 1 until points.size) {
            minDist = minOf(minDist, distance(points[i], points[j]))
        }
    }
    return minDist
}

private fun distance(a: Point, b: Point): Double {
    val dx = a.x - b.x
    val dy = a.y - b.y
    return kotlin.math.sqrt(dx * dx + dy * dy)
}
```

---

## 7. Rotating Calipers

### Концепция

**Rotating Calipers** — техника для нахождения оптимальных пар вершин выпуклого многоугольника за O(n). Представьте вращающийся штангенциркуль вокруг polygon.

### Antipodal Pairs

**Antipodal points** — пары вершин, через которые можно провести параллельные опорные прямые.

```
    ┌─────────┐
    │    *    │ ← parallel support lines
    │   / \   │
    │  /   \  │
    │ *     * │
    │  \   /  │
    │   \ /   │
    │    *    │
    └─────────┘
```

### Diameter (Максимальное расстояние)

```kotlin
/**
 * Диаметр выпуклого многоугольника (максимальное расстояние между вершинами)
 *
 * Time: O(n) — после построения convex hull
 *
 * ИДЕЯ ROTATING CALIPERS:
 * Представьте штангенциркуль, который вращается вокруг многоугольника.
 * Две параллельные "губки" всегда касаются двух antipodal точек.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *    ════════════════  ← одна "губка" (опорная прямая)
 *         ●━━━━●
 *        ╱      ╲
 *       ●        ●  ← antipodal пара (максимально удалены)
 *        ╲      ╱
 *         ●━━━━●
 *    ════════════════  ← другая "губка"
 * ```
 *
 * Все antipodal пары проверяются за O(n), потому что оба указателя
 * проходят по hull только один раз (амортизированно).
 */
fun convexPolygonDiameter(hull: List<Point>): Double {
    val n = hull.size
    if (n < 2) return 0.0
    if (n == 2) return distance(hull[0], hull[1])

    var maxDist = 0.0

    /**
     * Инициализация: находим точку, максимально удалённую от первого ребра.
     *
     * triangleArea(hull[0], hull[1], p) пропорциональна расстоянию от p
     * до прямой через hull[0] и hull[1].
     *
     * Продвигаем j, пока площадь увеличивается — ищем "вершину" параболы.
     */
    var j = 1
    while (triangleArea(hull[0], hull[1], hull[(j + 1) % n]) >
           triangleArea(hull[0], hull[1], hull[j])) {
        j = (j + 1) % n
    }

    /**
     * Основной цикл: "вращаем" calipers вокруг polygon.
     *
     * Для каждого ребра i→nextI находим antipodal точку j
     * и проверяем расстояние.
     */
    for (i in 0 until n) {
        // Проверяем расстояние от hull[i] до текущего antipodal
        maxDist = maxOf(maxDist, distance(hull[i], hull[j]))

        val nextI = (i + 1) % n

        /**
         * Продвигаем j, пока площадь треугольника (i, nextI, j) увеличивается.
         *
         * Это эквивалентно: пока j отдаляется от ребра i→nextI.
         * Когда площадь начнёт уменьшаться — нашли antipodal точку.
         */
        while (triangleArea(hull[i], hull[nextI], hull[(j + 1) % n]) >
               triangleArea(hull[i], hull[nextI], hull[j])) {
            j = (j + 1) % n
            maxDist = maxOf(maxDist, distance(hull[i], hull[j]))
        }

        /**
         * Особый случай: площади равны → две точки на одинаковом расстоянии.
         *
         * Ребро hull параллельно опорной прямой → нужно проверить обе точки!
         * Это "касание" calipers к ребру, а не к вершине.
         */
        if (triangleArea(hull[i], hull[nextI], hull[(j + 1) % n]).eq(
            triangleArea(hull[i], hull[nextI], hull[j]))) {
            maxDist = maxOf(maxDist, distance(hull[i], hull[(j + 1) % n]))
        }
    }

    return maxDist
}

/**
 * Minimum Width (минимальная ширина polygon)
 *
 * ЧТО ТАКОЕ ШИРИНА:
 * Минимальное расстояние между двумя параллельными опорными прямыми,
 * между которыми умещается весь многоугольник.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *    ═══════════════  ← опорная прямая (касается ребра)
 *         ●━━━━●
 *        ╱      ╲
 *   ←───●        ●  width = расстояние между прямыми
 *        ╲      ╱
 *         ●━━━━●   ← antipodal вершина
 *    ═══════════════
 * ```
 */
fun convexPolygonWidth(hull: List<Point>): Double {
    val n = hull.size
    if (n < 3) return 0.0

    var minWidth = Double.MAX_VALUE
    var j = 1

    for (i in 0 until n) {
        val nextI = (i + 1) % n

        /**
         * Для ребра i→nextI ищем вершину j, максимально удалённую от него.
         *
         * Продвигаем j, пока расстояние увеличивается.
         * Это и есть antipodal вершина для данного ребра.
         */
        while (pointToLineDistance(hull[j], hull[i], hull[nextI]) <
               pointToLineDistance(hull[(j + 1) % n], hull[i], hull[nextI])) {
            j = (j + 1) % n
        }

        val width = pointToLineDistance(hull[j], hull[i], hull[nextI])
        minWidth = minOf(minWidth, width)
    }

    return minWidth
}

// Расстояние от точки до прямой, проходящей через a и b
private fun pointToLineDistance(p: Point, a: Point, b: Point): Double {
    val area = kotlin.math.abs(cross(a, b, p))
    val base = distance(a, b)
    return if (base > EPS) area / base else 0.0
}
```

### Другие применения Rotating Calipers

| Задача | Сложность |
|--------|-----------|
| Minimum Bounding Rectangle | O(n) |
| Maximum distance between two polygons | O(n + m) |
| Минимальная enclosing strip | O(n) |
| Onion layers | O(n²) |

---

## 8. Line Segment Intersection

### Пересечение двух отрезков

```kotlin
/**
 * Проверка пересечения отрезков AB и CD
 *
 * МЕТОД: используем ориентации (orientations) для robust проверки.
 *
 * ИДЕЯ:
 * Отрезки пересекаются ⟺ концы каждого отрезка лежат по разные
 * стороны от прямой, содержащей другой отрезок.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *     A ───────── B
 *          ╳
 *     C ───────── D
 *
 *     d1 = orient(C,D,A) = +1 (A слева от CD)
 *     d2 = orient(C,D,B) = -1 (B справа от CD)
 *     d1 * d2 < 0 ✓
 *
 *     d3 = orient(A,B,C) = -1 (C справа от AB)
 *     d4 = orient(A,B,D) = +1 (D слева от AB)
 *     d3 * d4 < 0 ✓
 *
 *     → Пересекаются!
 * ```
 */
fun segmentsIntersect(a: Point, b: Point, c: Point, d: Point): Boolean {
    val d1 = orientation(c, d, a)
    val d2 = orientation(c, d, b)
    val d3 = orientation(a, b, c)
    val d4 = orientation(a, b, d)

    /**
     * ОБЩИЙ СЛУЧАЙ: концы AB по разные стороны от CD, И
     * концы CD по разные стороны от AB.
     *
     * d1 * d2 < 0 означает: d1 и d2 разных знаков (A и B по разные стороны от CD)
     * d3 * d4 < 0 означает: d3 и d4 разных знаков (C и D по разные стороны от AB)
     */
    if (d1 * d2 < 0 && d3 * d4 < 0) return true

    /**
     * ОСОБЫЕ СЛУЧАИ: одна из точек коллинеарна с другим отрезком.
     *
     * orientation = 0 означает коллинеарность.
     * Нужно дополнительно проверить, что точка лежит НА отрезке
     * (а не на продолжении прямой).
     *
     * ```
     *     A ────●──── B     (● = C или D на отрезке AB)
     *           C─────D
     * ```
     */
    if (d1 == 0 && onSegment(c, a, d)) return true
    if (d2 == 0 && onSegment(c, b, d)) return true
    if (d3 == 0 && onSegment(a, c, b)) return true
    if (d4 == 0 && onSegment(a, d, b)) return true

    return false
}

// Проверка: лежит ли q на отрезке pr (при условии коллинеарности)
private fun onSegment(p: Point, q: Point, r: Point): Boolean {
    return q.x <= maxOf(p.x, r.x) && q.x >= minOf(p.x, r.x) &&
           q.y <= maxOf(p.y, r.y) && q.y >= minOf(p.y, r.y)
}

/**
 * Точка пересечения двух отрезков (если существует)
 */
fun segmentIntersection(a: Point, b: Point, c: Point, d: Point): Point? {
    if (!segmentsIntersect(a, b, c, d)) return null

    val a1 = b.y - a.y
    val b1 = a.x - b.x
    val c1 = a1 * a.x + b1 * a.y

    val a2 = d.y - c.y
    val b2 = c.x - d.x
    val c2 = a2 * c.x + b2 * c.y

    val det = a1 * b2 - a2 * b1

    if (det.eq(0.0)) {
        /**
         * det = 0 означает: прямые ПАРАЛЛЕЛЬНЫ или СОВПАДАЮТ.
         *
         * Если отрезки пересекаются (мы уже проверили выше),
         * значит они коллинеарны и перекрываются.
         *
         * Возвращаем одну из точек, которая лежит на пересечении.
         */
        return if (pointOnSegment(a, c, d)) a
               else if (pointOnSegment(b, c, d)) b
               else if (pointOnSegment(c, a, b)) c
               else d
    }

    val x = (b2 * c1 - b1 * c2) / det
    val y = (a1 * c2 - a2 * c1) / det

    return Point(x, y)
}
```

### Bentley-Ottmann Algorithm (обзор)

Для нахождения **всех** пересечений среди N отрезков:

```
Наивный подход: O(n²) — проверяем все пары
Bentley-Ottmann: O((n + k) log n) где k = число пересечений

Идея: sweep line слева направо
- Event queue (priority queue по x)
- Status tree (BST отрезков по y на текущей линии)
- События: начало отрезка, конец отрезка, пересечение
```

---

## 9. Half-Plane Intersection

### Определение

**Half-plane** — полуплоскость, заданная прямой. Пересечение полуплоскостей образует выпуклую область (возможно пустую или unbounded).

### S&I Algorithm (Sort-and-Incremental)

```kotlin
/**
 * Half-plane (полуплоскость), заданная неравенством: ax + by + c ≤ 0
 *
 * Эквивалентно: все точки СЛЕВА от направленной прямой ax + by + c = 0.
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *     ax + by + c > 0
 *     (вне полуплоскости)
 *            │
 *            │  нормаль (a, b)
 *            │     ↓
 *   ─────────┼───────────→ направление (-b, a)
 *            │
 *     ax + by + c ≤ 0
 *     (ВНУТРИ полуплоскости)
 * ```
 */
data class HalfPlane(
    val a: Double, val b: Double, val c: Double
) {
    /**
     * Направляющий вектор прямой.
     *
     * Нормаль к прямой: (a, b) — показывает "наружу".
     * Направление: перпендикулярно нормали, поворот на 90° влево.
     * (-b, a) — поворот (a, b) на 90° CCW.
     */
    val direction: Point get() = Point(-b, a)

    /**
     * Угол направления для сортировки полуплоскостей.
     *
     * atan2 возвращает угол в радианах от -π до π.
     * Сортировка по углу позволяет обрабатывать полуплоскости
     * в порядке "вращения" по кругу.
     */
    val angle: Double get() = kotlin.math.atan2(a, -b)

    /**
     * Проверка: лежит ли точка в полуплоскости.
     *
     * ax + by + c ≤ 0 (с учётом погрешности EPS).
     */
    fun contains(p: Point): Boolean {
        return a * p.x + b * p.y + c <= EPS
    }
}

/**
 * Пересечение полуплоскостей — O(n log n)
 *
 * Возвращает вершины результирующего ВЫПУКЛОГО многоугольника,
 * или пустой список если пересечение пусто.
 *
 * ИДЕЯ АЛГОРИТМА (Sort and Incremental):
 * 1. Сортируем полуплоскости по углу направления
 * 2. Поддерживаем deque "активных" полуплоскостей
 * 3. При добавлении новой — удаляем те, что стали "лишними"
 *
 * ВИЗУАЛИЗАЦИЯ:
 * ```
 *      ╲     ╱
 *       ╲   ╱
 *        ╲ ╱  ← пересечение = выпуклый многоугольник
 *        ╱ ╲
 *       ╱   ╲
 * ```
 */
fun halfPlaneIntersection(planes: List<HalfPlane>): List<Point> {
    if (planes.isEmpty()) return emptyList()

    /**
     * Сортируем по углу направления.
     *
     * Это обеспечивает "круговой" обход полуплоскостей,
     * что критично для корректной работы deque.
     */
    val sorted = planes.sortedBy { it.angle }

    /**
     * Deque для инкрементального построения пересечения.
     *
     * deque хранит "активные" полуплоскости.
     * points хранит точки пересечения соседних полуплоскостей в deque.
     */
    val deque = ArrayDeque<HalfPlane>()
    val points = ArrayDeque<Point>()

    for (plane in sorted) {
        /**
         * Удаляем с КОНЦА deque полуплоскости, ставшие лишними.
         *
         * Если новая полуплоскость НЕ содержит последнюю точку пересечения,
         * значит последняя полуплоскость в deque "отсечена" новой.
         *
         * ```
         *   old   ╲
         *         ╳──── new "отрезает" old
         *         ╱
         * ```
         */
        while (points.isNotEmpty() && !plane.contains(points.last())) {
            deque.removeLast()
            points.removeLast()
        }

        /**
         * Аналогично удаляем с НАЧАЛА deque.
         *
         * Deque — циклический, поэтому нужно проверять оба конца.
         */
        while (points.isNotEmpty() && !plane.contains(points.first())) {
            deque.removeFirst()
            points.removeFirst()
        }

        /**
         * Обработка ПАРАЛЛЕЛЬНЫХ полуплоскостей.
         *
         * cross ≈ 0 означает параллельность.
         */
        if (deque.isNotEmpty()) {
            val last = deque.last()
            if (kotlin.math.abs(cross(plane.direction, last.direction)).lt(EPS)) {
                if (dot(plane.direction, last.direction) > 0) {
                    /**
                     * Однонаправленные параллельные полуплоскости.
                     *
                     * Оставляем более "строгую" (ближе к пересечению).
                     * ```
                     *   ═══════  plane1 (шире)
                     *   ───────  plane2 (строже) ← оставляем эту
                     * ```
                     */
                    if (!plane.contains(Point(-last.a * last.c, -last.b * last.c))) {
                        deque.removeLast()
                        if (points.isNotEmpty()) points.removeLast()
                    } else {
                        continue
                    }
                } else {
                    /**
                     * Противоположно направленные параллельные полуплоскости.
                     *
                     * Пересечение ПУСТО (одна говорит "слева", другая "справа").
                     * ```
                     *   ←───────  plane1
                     *   ───────→  plane2
                     *   Пересечение = ∅
                     * ```
                     */
                    return emptyList()
                }
            }
        }

        /**
         * Добавляем новую полуплоскость в deque.
         *
         * Также вычисляем точку пересечения с предыдущей полуплоскостью.
         */
        if (deque.isNotEmpty()) {
            val intersection = lineIntersection(deque.last(), plane)
            if (intersection != null) {
                points.addLast(intersection)
            }
        }
        deque.addLast(plane)
    }

    /**
     * Финальная очистка: "замыкаем" deque.
     *
     * После обработки всех полуплоскостей нужно проверить,
     * что первая и последняя полуплоскости согласованы.
     */
    while (points.size >= 2 && !deque.first().contains(points.last())) {
        deque.removeLast()
        points.removeLast()
    }
    while (points.size >= 2 && !deque.last().contains(points.first())) {
        deque.removeFirst()
        points.removeFirst()
    }

    if (deque.size < 3) return emptyList()

    /**
     * Добавляем точку пересечения ПЕРВОЙ и ПОСЛЕДНЕЙ полуплоскостей.
     *
     * Это "замыкает" многоугольник.
     */
    val closing = lineIntersection(deque.first(), deque.last())
    if (closing != null) {
        points.addLast(closing)
    }

    return points.toList()
}

private fun lineIntersection(h1: HalfPlane, h2: HalfPlane): Point? {
    val det = h1.a * h2.b - h2.a * h1.b
    if (det.eq(0.0)) return null

    val x = (h1.b * h2.c - h2.b * h1.c) / det
    val y = (h2.a * h1.c - h1.a * h2.c) / det
    return Point(x, y)
}
```

---

## 10. Precision и Edge Cases

### Главные проблемы

| Проблема | Симптом | Решение |
|----------|---------|---------|
| Floating-point comparison | a == b fails | Используйте EPS |
| Overflow в cross product | Неверный знак | long long или BigInteger |
| acos/asin domain error | NaN/Runtime error | Clamp в [-1, 1] |
| Degeneracy | Коллинеарные точки | Отдельная обработка |

### Best Practices

```kotlin
/**
 * ГЛОБАЛЬНЫЕ КОНСТАНТЫ для precision.
 *
 * EPS = 1e-9 — типичный выбор для floating-point сравнений.
 * - Слишком маленький (1e-12): может не уловить ошибки округления
 * - Слишком большой (1e-6): может давать false positives
 *
 * INF = 1e18 — "бесконечность" для Double (не переполняется при сложении)
 */
const val EPS = 1e-9
const val INF = 1e18

/**
 * БЕЗОПАСНОЕ СРАВНЕНИЕ Double с учётом погрешности.
 *
 * НИКОГДА не используйте == для Double!
 * 0.1 + 0.2 == 0.3 вернёт FALSE из-за floating-point представления.
 *
 * eq: "равны" (|a - b| < EPS)
 * lt: "строго меньше" (a < b - EPS)
 * le: "меньше или равно" (a < b + EPS)
 */
infix fun Double.eq(other: Double) = kotlin.math.abs(this - other) < EPS
infix fun Double.lt(other: Double) = this < other - EPS
infix fun Double.le(other: Double) = this < other + EPS

/**
 * БЕЗОПАСНЫЙ acos для избежания domain error.
 *
 * ПРОБЛЕМА: acos определён только на [-1, 1].
 * Из-за ошибок округления можно получить значение типа 1.0000000001,
 * что вызовет NaN или RuntimeException.
 *
 * РЕШЕНИЕ: coerceIn ограничивает значение допустимым диапазоном.
 */
fun safeAcos(x: Double): Double {
    return kotlin.math.acos(x.coerceIn(-1.0, 1.0))
}

/**
 * Квадрат расстояния — ИЗБЕГАЕМ sqrt когда возможно.
 *
 * ПРЕИМУЩЕСТВА:
 * 1. sqrt — относительно дорогая операция
 * 2. Для СРАВНЕНИЯ расстояний sqrt не нужен:
 *    dist(a,b) < dist(c,d)  ⟺  dist²(a,b) < dist²(c,d)
 * 3. Меньше ошибок округления (нет иррациональных чисел)
 */
fun distanceSquared(a: Point, b: Point): Double {
    val dx = a.x - b.x
    val dy = a.y - b.y
    return dx * dx + dy * dy
}

/**
 * Сравнение расстояний через КВАДРАТЫ (без sqrt).
 *
 * Проверяем: dist(a,b) < dist(c,d)?
 * Эквивалентно: dist²(a,b) < dist²(c,d)
 *
 * Работает корректно, потому что оба расстояния неотрицательны,
 * а функция x² монотонна на [0, +∞).
 */
fun isCloser(a: Point, b: Point, c: Point, d: Point): Boolean {
    return distanceSquared(a, b) < distanceSquared(c, d)
}
```

### Использование Long для точности

```kotlin
/**
 * Integer-based cross product для избежания floating-point errors.
 *
 * КОГДА ИСПОЛЬЗОВАТЬ:
 * Если координаты в задаче ЦЕЛЫЕ — используйте Long вместо Double!
 *
 * ПРЕИМУЩЕСТВА:
 * 1. Нет ошибок округления — сравнения точные
 * 2. cross = 0 означает ТОЧНО коллинеарны
 * 3. Не нужен EPS
 *
 * ОГРАНИЧЕНИЕ:
 * Координаты до 10^9: произведение двух координат до 10^18 ✓
 * Координаты до 10^18: ПЕРЕПОЛНЕНИЕ! Нужен BigInteger.
 */
data class LongPoint(val x: Long, val y: Long)

fun crossLong(o: LongPoint, a: LongPoint, b: LongPoint): Long {
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
}

/**
 * Orientation через Long — ТОЧНЫЙ знак без overflow.
 *
 * Для координат до 10^9:
 * - Разность: до 2 * 10^9 (помещается в Long)
 * - Произведение: до 4 * 10^18 (помещается в Long)
 *
 * Если координаты больше — используйте BigInteger или Int128.
 */
fun orientationLong(a: LongPoint, b: LongPoint, c: LongPoint): Int {
    val cr = crossLong(a, b, c)
    return when {
        cr > 0 -> 1
        cr < 0 -> -1
        else -> 0
    }
}
```

---

## 11. Практические задачи

### Задача 1: Convex Hull Area

```kotlin
/**
 * Найти площадь convex hull для заданных точек
 */
fun convexHullArea(points: List<Point>): Double {
    val hull = convexHull(points)
    return polygonArea(hull)
}
```

### Задача 2: Проверка выпуклости

```kotlin
/**
 * Проверить, является ли многоугольник выпуклым
 */
fun isConvex(polygon: List<Point>): Boolean {
    val n = polygon.size
    if (n < 3) return false

    var sign = 0
    for (i in 0 until n) {
        val o = orientation(
            polygon[i],
            polygon[(i + 1) % n],
            polygon[(i + 2) % n]
        )

        if (o != 0) {
            if (sign == 0) {
                sign = o
            } else if (sign != o) {
                /**
                 * Разные направления поворота = НЕвыпуклый!
                 *
                 * В выпуклом многоугольнике все повороты должны быть
                 * в одном направлении (все CCW или все CW).
                 *
                 * Если встретили поворот в другую сторону — есть "вогнутость".
                 */
                return false
            }
        }
    }

    return true
}
```

### Задача 3: Minimum Enclosing Circle

```kotlin
/**
 * Минимальный охватывающий круг (Welzl's algorithm)
 *
 * Time: O(n) expected
 */
data class Circle(val center: Point, val radius: Double) {
    fun contains(p: Point): Boolean {
        return distance(center, p) <= radius + EPS
    }
}

fun minEnclosingCircle(points: List<Point>): Circle {
    /**
     * Случайное перемешивание — КРИТИЧНО для O(n)!
     *
     * Без рандомизации: worst case O(n²) (например, точки по кругу).
     * С рандомизацией: expected O(n) — почти всегда линейное время.
     *
     * Доказательство: вероятность "неудачного" случая экспоненциально мала.
     */
    val shuffled = points.shuffled()
    return welzl(shuffled, mutableListOf(), shuffled.size)
}

private fun welzl(
    points: List<Point>,
    boundary: MutableList<Point>,
    n: Int
): Circle {
    /**
     * BASE CASES:
     * - n = 0: все точки обработаны → строим круг по boundary
     * - boundary.size = 3: три точки на границе определяют круг однозначно
     *
     * Круг определяется максимум 3 точками на границе (описанная окружность треугольника).
     */
    if (n == 0 || boundary.size == 3) {
        return makeCircle(boundary)
    }

    val p = points[n - 1]
    val circle = welzl(points, boundary, n - 1)

    /**
     * Если точка p ВНУТРИ текущего круга — круг не меняется.
     *
     * Это "удачный" случай, который происходит часто благодаря рандомизации.
     */
    if (circle.contains(p)) {
        return circle
    }

    /**
     * Если точка p ВНЕ текущего круга — она должна быть на ГРАНИЦЕ
     * минимального охватывающего круга!
     *
     * ДОКАЗАТЕЛЬСТВО:
     * Если p вне круга, то любой меньший круг, содержащий все точки,
     * должен проходить через p (иначе p не накроется).
     *
     * Добавляем p в boundary и рекурсивно строим круг.
     */
    boundary.add(p)
    val result = welzl(points, boundary, n - 1)
    boundary.removeLast()

    return result
}

private fun makeCircle(boundary: List<Point>): Circle {
    return when (boundary.size) {
        0 -> Circle(Point(0.0, 0.0), 0.0)
        1 -> Circle(boundary[0], 0.0)
        2 -> {
            val center = Point(
                (boundary[0].x + boundary[1].x) / 2,
                (boundary[0].y + boundary[1].y) / 2
            )
            Circle(center, distance(center, boundary[0]))
        }
        3 -> circumcircle(boundary[0], boundary[1], boundary[2])
        else -> throw IllegalStateException()
    }
}

private fun circumcircle(a: Point, b: Point, c: Point): Circle {
    val d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
    if (d.eq(0.0)) {
        /**
         * d ≈ 0 означает: точки КОЛЛИНЕАРНЫ (на одной прямой).
         *
         * В этом случае описанная окружность не существует
         * (бесконечный радиус).
         *
         * РЕШЕНИЕ: минимальный круг = диаметр между двумя крайними точками.
         * Находим пару с максимальным расстоянием и строим круг по ней.
         */
        val maxDist = maxOf(distance(a, b), distance(b, c), distance(a, c))
        return when {
            distance(a, b).eq(maxDist) -> makeCircle(listOf(a, b))
            distance(b, c).eq(maxDist) -> makeCircle(listOf(b, c))
            else -> makeCircle(listOf(a, c))
        }
    }

    val ux = ((a.x * a.x + a.y * a.y) * (b.y - c.y) +
              (b.x * b.x + b.y * b.y) * (c.y - a.y) +
              (c.x * c.x + c.y * c.y) * (a.y - b.y)) / d
    val uy = ((a.x * a.x + a.y * a.y) * (c.x - b.x) +
              (b.x * b.x + b.y * b.y) * (a.x - c.x) +
              (c.x * c.x + c.y * c.y) * (b.x - a.x)) / d

    val center = Point(ux, uy)
    return Circle(center, distance(center, a))
}
```

---

## 12. Резюме и чеклист

### Complexity Summary

| Алгоритм | Время | Пространство |
|----------|-------|--------------|
| Polygon Area (Shoelace) | O(n) | O(1) |
| Point in Polygon | O(n) | O(1) |
| Convex Hull | O(n log n) | O(n) |
| Closest Pair | O(n log n) | O(n) |
| Rotating Calipers | O(n) | O(1) |
| Segment Intersection | O(1) | O(1) |
| Half-Plane Intersection | O(n log n) | O(n) |
| Min Enclosing Circle | O(n) exp | O(n) |

### Чеклист для геометрических задач

```
□ Определить тип координат (int или double)
□ Выбрать EPS (обычно 1e-9 для double)
□ Проверить overflow в cross product
□ Обработать degenerate cases (коллинеарность, совпадение)
□ Проверить edge cases:
  - Пустой ввод
  - 1-2 точки
  - Все точки коллинеарны
  - Все точки совпадают
□ Для double: использовать EPS в сравнениях
□ Избегать sqrt когда возможно (сравнивать квадраты)
□ Clamp аргументы acos/asin в [-1, 1]
```

### Рекомендуемые ресурсы

1. **Victor Lecomte's Handbook** — лучший гайд по геометрии для CP
2. **CP-Algorithms** — качественные реализации
3. **USACO Guide** — примеры задач с объяснениями
4. **Codeforces Geometry Blog** — обсуждения edge cases

### Типичные паттерны задач

| Паттерн | Признаки | Алгоритм |
|---------|----------|----------|
| Оптимизация на hull | "Максимальная/минимальная величина" | Convex Hull + DP/Поиск |
| Видимость | "Что видно из точки" | Half-plane intersection |
| Покрытие | "Минимальный круг/прямоугольник" | Rotating Calipers / Welzl |
| Пересечения | "Сколько пар пересекаются" | Sweep Line |
| Геолокация | "Ближайшая точка" | Closest Pair / Voronoi |

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Геометрия = просто формулы" | Геометрия — **самая error-prone** область CP. Floating point precision, degenerate cases, edge cases |
| "EPS = 1e-9 всегда работает" | EPS зависит от **порядка величин**. Для координат 10⁹ нужен EPS 10⁻⁶, не 10⁻⁹ |
| "Integer координаты = нет проблем" | Cross product может **overflow**. 10⁹ × 10⁹ = 10¹⁸, нужен long long |
| "sqrt() безопасен" | Избегай sqrt где возможно — **сравнивай квадраты** расстояний. Точнее и быстрее |
| "Convex hull решает все" | Convex hull — начало. Часто нужен **rotating calipers**, half-plane intersection или Voronoi |

---

## CS-фундамент

| CS-концепция | Применение в Computational Geometry |
|--------------|-------------------------------------|
| **Cross Product** | Основа всего: направление поворота, площадь, положение точки относительно прямой |
| **Sweep Line** | Эффективный обход слева направо: пересечения отрезков, closest pair, area union |
| **Convex Hull** | Graham scan, Andrew's algorithm. Основа для оптимизационных задач |
| **Divide and Conquer** | Closest pair O(n log n), merge convex hulls, Voronoi diagram |
| **Floating Point Arithmetic** | EPS comparison, накопление ошибок, catastrophic cancellation. Критично для корректности |

---

## Связь с другими темами

**[[divide-and-conquer]]** --- многие ключевые геометрические алгоритмы основаны на стратегии «разделяй и властвуй». Closest pair за O(n log n) делит точки вертикальной линией, рекурсивно решает подзадачи и объединяет через strip шириной 2d. Merge-подход используется для построения convex hull (алгоритм Preparata--Hong), а также для построения диаграммы Вороного за O(n log n). Понимание D&C --- необходимая база для эффективных геометрических алгоритмов.

**[[sorting-algorithms]]** --- sweep line алгоритмы требуют предварительной сортировки событий по одной из координат, что определяет нижнюю границу O(n log n) для многих геометрических задач. Graham scan сортирует точки по полярному углу, Andrew's algorithm --- по координатам, closest pair --- по X-координате. Bentley-Ottmann для пересечения отрезков сортирует events. Сортировка по углу (atan2) --- специфический геометрический приём, который не встречается в других областях алгоритмов.

---

## Источники и дальнейшее чтение

### Книги

- **de Berg, Cheong, van Kreveld & Overmars (2008). "Computational Geometry: Algorithms and Applications."** --- каноническая книга по вычислительной геометрии: convex hull, line segment intersection, polygon triangulation, Voronoi diagrams с доказательствами и анализом
- **O'Rourke (1998). "Computational Geometry in C."** --- практическая реализация геометрических алгоритмов на C с детальным разбором edge cases и numerical precision
- **Preparata & Shamos (1985). "Computational Geometry: An Introduction."** --- классическое введение в область, охватывающее divide-and-conquer подходы, lower bounds и теоретические основы

### Онлайн-ресурсы

- [CP-Algorithms: Geometry](https://cp-algorithms.com/) --- реализации с объяснениями на C++ для соревновательного программирования
- **Halim (2013). "Competitive Programming 3."** --- глава по геометрии для соревнований: типичные задачи, подводные камни precision, шаблонный код

---

*Обновлено: 2026-01-09 --- добавлены педагогические секции (интуиция cross product/convex hull/point-in-polygon/rotating calipers/shoelace, 6 типичных ошибок floating-point/overflow/degenerate cases, 5 ментальных моделей)*
