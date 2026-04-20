---
title: "Матрицы для трансформаций: 4×4, TRS, column-major и MVP"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/cs-foundations
  - topic/3d-graphics
  - topic/graphics-math
  - type/deep-dive
  - level/intermediate
related:
  - "[[3d-graphics-math-overview]]"
  - "[[vectors-in-3d-graphics]]"
  - "[[homogeneous-coordinates-and-affine]]"
  - "[[quaternions-and-rotations]]"
  - "[[projections-perspective-orthographic]]"
  - "[[shader-programming-fundamentals]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[3d-graphics-math-overview]]"
  - "[[vectors-in-3d-graphics]]"
primary_sources:
  - url: "https://developer.android.com/reference/android/opengl/Matrix"
    title: "Android Developers: android.opengl.Matrix API reference (column-major float[16] layout)"
    accessed: 2026-04-20
  - url: "https://fgiesen.wordpress.com/2011/05/04/row-major-vs-column-major-and-gl-es/"
    title: "Fabian Giesen (ryg): Row-major vs. column-major and GL ES"
    accessed: 2026-04-20
  - url: "http://www.opengl-tutorial.org/beginners-tutorials/tutorial-3-matrices/"
    title: "OpenGL Tutorial: Matrices (canonical intro to MVP)"
    accessed: 2026-04-20
  - url: "https://en.wikipedia.org/wiki/Transformation_matrix"
    title: "Wikipedia: Transformation matrix (affine and projective)"
    accessed: 2026-04-20
  - url: "https://github.com/romainguy/kotlin-math"
    title: "kotlin-math 1.6.0 — Mat3, Mat4 API and idiomatic Kotlin operators"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Filament documentation — matrix conventions (column-major, right-handed)"
    accessed: 2026-04-20
  - url: "https://docs.shader-slang.org/en/stable/external/slang/docs/user-guide/a1-01-matrix-layout.html"
    title: "Shader-Slang: Handling matrix layout differences on different platforms"
    accessed: 2026-04-20
  - url: "https://austinmorlan.com/posts/opengl_matrices/"
    title: "Austin Morlan: Sending matrices to OpenGL (practical indexing)"
    accessed: 2026-04-20
reading_time: 40
difficulty: 5
---

# Матрицы для трансформаций

В исходниках [[filament-architecture-deep|Filament]] есть функция `setTransform(entity, Mat4 m)`, которая принимает 16 float-чисел. Между этой функцией и пикселем на экране — ещё как минимум две похожие матрицы (view и projection). Все три перемножаются в vertex shader в одной строке: `gl_Position = projection * view * model * vec4(position, 1.0)`. Эта строка — сердце всей 3D-графики. Понять её целиком означает понять, почему порядок не переставим, почему матрица 4×4 а не 3×3, почему кубик в [[case-planner-5d|Planner 5D]] при drag'е сначала выглядит криво, а потом внезапно правильно, и почему один и тот же массив из 16 float читается по-разному в `android.opengl.Matrix` и в GLM.

Файл — второй полный deep-dive блока M1. Он опирается на [[3d-graphics-math-overview]] и [[vectors-in-3d-graphics]]; последующие файлы ([[homogeneous-coordinates-and-affine]], [[quaternions-and-rotations]], [[projections-perspective-orthographic]]) опираются на него. Читатель выходит с умением: вручную собрать matrix-chain для типичного Android-сценария, увидеть, где TRS-порядок нарушен, перевести матрицу из row-major в column-major API, и отладить перевёрнутую модель на уровне арифметики.

---

## Зачем это знать

**Первая production-ситуация.** Разработчик переносит код из Unity-проекта (HLSL, row-major, left-handed) в Android-проект с Filament (GLSL, column-major, right-handed). Один и тот же массив из 16 чисел теперь даёт сцену в зеркальном отражении с перевёрнутыми осями. Отладка без понимания column-major vs row-major занимает дни и сводится к попыткам случайным образом транспонировать и инвертировать по знакам — с успехом 1 из 20. С пониманием разницы layout'ов — пятнадцать минут на явный `transpose()` в одном месте pipeline.

**Вторая ситуация.** Разработчик собирает model matrix как `T · R · S` и видит, что объект вращается не на месте, а по орбите вокруг origin сцены. Это классика — `(T · R · S) · v` применяет сначала S (масштаб относительно своего origin), потом R (вращение вокруг origin объекта, пока ещё в его локальной системе), потом T (перенос в мир). Правильный порядок и есть TRS — в обратной композиции. Путаница между T·R·S и S·R·T — один из самых частых багов при ручном сборе матриц, потому что текстуально «сначала scale, потом rotate, потом translate» звучит как `S · R · T`, но матрично правильно записать это как `T · R · S`.

**Третья ситуация.** Переход с `android.opengl.Matrix` (column-major float[16]) на `kotlin-math` (Mat4 с операторными перегрузками). Код, который работал, внезапно даёт мусор. Причина — в первом случае `multiplyMM(dst, 0, a, 0, b, 0)` считает `dst = a × b` как композицию «сначала b, потом a» (column-major convention); в `kotlin-math` оператор `a * b` — то же самое, но документация может сбить читателя, если он не помнит конвенцию.

Каждая из этих трёх ситуаций закрывается одним параграфом понимания матричной алгебры, и выжигает недели без него. Поэтому в курсе M1 файл matrices отдельный.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[3d-graphics-math-overview]] | Понимание координатных пространств (local → world → view → clip → screen) — матрицы делают именно эти переходы |
| [[vectors-in-3d-graphics]] | Матрица применяется к вектору; без понимания `M · v` весь остальной текст непонятен |
| Школьная матричная алгебра: умножение матриц, единичная матрица, транспонирование | Без этого уровень 2 сложен. Bail-out — [3Blue1Brown Essence of Linear Algebra, episodes 3–4](https://www.3blue1brown.com/topics/linear-algebra) |

---

## Терминология

| Термин | Определение | Аналогия из реальной жизни |
|---|---|---|
| Матрица 4×4 | Прямоугольный массив из 16 чисел (4 строки × 4 столбца), представляющий аффинное преобразование пространства | Рецепт на 16 шагов: как переделать один набор координат в другой |
| Столбец матрицы (column) | Четыре числа, расположенные вертикально | Один столбик в Excel |
| Строка матрицы (row) | Четыре числа, расположенные горизонтально | Одна строчка в Excel |
| Identity matrix (I) | Матрица, которая ничего не меняет: `I · v = v` | Нулевая операция, «оставить как было» |
| Translate matrix | Матрица сдвига на заданный вектор | Команда «переехать на 5 метров вправо» |
| Rotate matrix | Матрица вращения вокруг заданной оси на заданный угол | «Повернись вокруг вертикали на 45 градусов» |
| Scale matrix | Матрица изменения размера | «Увеличь всё в 2 раза» |
| Model matrix | Составная T·R·S-матрица одного объекта в сцене | Единая «инструкция», куда и как поставить конкретный предмет |
| View matrix | Матрица, переводящая мир в систему координат камеры | Точка зрения фотографа — мир «крутится», чтобы камера оказалась в центре |
| Projection matrix | Матрица, проецирующая 3D-пространство в 2D-экран | Как фотопроекция 3D-сцены на плоскую плёнку |
| MVP matrix | `projection * view * model` — полный matrix-chain, применяемый в vertex shader | «Полный рецепт»: из модели в пиксель |
| Determinant | Скаляр, связанный с матрицей; характеризует «масштабное искажение» | Насколько объём меняется при преобразовании |
| Inverse (M⁻¹) | Матрица, удовлетворяющая `M · M⁻¹ = I`; обратная операция | Сделать обратную манипуляцию |
| Transpose (Mᵀ) | Матрица, в которой строки и столбцы поменяны местами | Транспонировать таблицу в Excel |
| Column-major layout | Матрица в памяти: сначала все элементы первого столбца, потом второго и т. д. | Читать Excel по столбцам, а не по строкам |
| Row-major layout | Сначала все элементы первой строки, потом второй | Обычное чтение Excel по строкам |
| TRS composition | Порядок `T · R · S` — стандарт в графике | Инструкция ИКЕА: сначала всё собрать (S), потом повернуть (R), потом поставить на место (T) |

---

## Историческая справка: как матрицы попали в 3D-графику

Матричная алгебра — изобретение математиков XIX века, не графики. **Arthur Cayley** в 1858 году («A Memoir on the Theory of Matrices») формализует понятие матрицы и операции над ней: сложение, умножение, инверсию. Это чистая теория; графика как область ещё не существует.

**Hermann Günther Graßmann (1844)** параллельно строит свою «Ausdehnungslehre», где уже есть идея линейных преобразований пространства как операторов — прообраз будущих матриц.

В инженерию матрицы приходят через **Leonhard Euler** (раньше, XVIII век) — в механике твёрдого тела вращение тела описывается через три Euler-угла. Матрица вращения как явный инструмент появляется в работах **Augustin-Louis Cauchy** начала XIX века.

**Компьютерная графика** рождается в 1960-х. **Ivan Sutherland** в Sketchpad (1963) использует матрицы для преобразования координат на экране. **Larry Roberts** в докторской 1963 года («Machine Perception of Three-Dimensional Solids») формализует проективную геометрию для рендеринга — явно вводит homogeneous coordinates и 4×4-матрицы. Именно его работа — истинный прародитель современной графики.

**1975 — Newell, Newell & Sancha, Painter's algorithm.** Первая работа, где matrix-chain применяется для сортировки и рендеринга сцен.

**1983 — Jim Blinn, «A Trip Down the Graphics Pipeline».** Популярное изложение, где model → world → view → clip → screen описан явно через последовательность 4×4-матриц. Терминология MVP («ModelViewProjection») закрепляется к этому моменту.

**1992 — OpenGL 1.0.** Стандартизирует column-major matrix layout, функции `glTranslate`, `glRotate`, `glScale`, `glLoadMatrix`. Matrix stack становится частью API — state-machine, где matrix приложения хранились внутри driver'а.

**1995 — DirectX 1.0 (до того Reality Lab Engine).** Microsoft выбирает row-major layout и left-handed координатную систему — отличия от OpenGL, которые преследуют индустрию до сегодня.

**2004 — GLSL 1.10.** `mat4` становится встроенным типом шейдерного языка. Фиксированный graphics pipeline OpenGL умирает — теперь matrix-chain программист строит сам и передаёт в uniform.

**2016 — Vulkan 1.0.** Unifies explicit mindset: нет matrix stack, нет fixed pipeline, всё явно. API не навязывает column- или row-major — программист и компилятор шейдеров договариваются. На Android это даёт полную свободу и полную ответственность.

**2026 — kotlin-math, Filament Math.** Идиоматичные обёртки над той же математикой для Kotlin/NDK-приложений.

Вывод: за матрицами в vertex shader'е стоит 170 лет математики и 60 лет инженерии. Column-major vs row-major — не произвол авторов API, а историческая конвенция разных школ (математическая и инженерная соответственно).

---

## Теоретические основы

### Что делает матрица с вектором

Матрица 4×4 задаёт линейное (точнее, аффинное — см. [[homogeneous-coordinates-and-affine]]) преобразование пространства. Применение — умножение матрицы на вектор-столбец:

```
        | m00  m01  m02  m03 |   | v.x |   | m00·v.x + m01·v.y + m02·v.z + m03·v.w |
M · v = | m10  m11  m12  m13 | · | v.y | = | m10·v.x + m11·v.y + m12·v.z + m13·v.w |
        | m20  m21  m22  m23 |   | v.z |   | m20·v.x + m21·v.y + m22·v.z + m23·v.w |
        | m30  m31  m32  m33 |   | v.w |   | m30·v.x + m31·v.y + m32·v.z + m33·v.w |
```

Это 16 умножений и 12 сложений = 28 ALU-операций на один вектор. На GPU упаковано в 4 FMA. За 64 FMA на кадр — выполняется для всех вершин сцены за миллисекунды.

Если `v` — вектор направления (например, нормаль), ставим `v.w = 0`, и четвёртая колонка матрицы на результат не влияет. Если `v` — точка, ставим `v.w = 1`, и четвёртая колонка добавляет translate. Детали — в [[homogeneous-coordinates-and-affine]].

### Identity, умножение, инверсия

**Identity matrix** — матрица, у которой диагональ единичная, остальное — нули:

```
    | 1  0  0  0 |
I = | 0  1  0  0 |
    | 0  0  1  0 |
    | 0  0  0  1 |
```

Свойство: `I · v = v` для любого v; `M · I = I · M = M` для любой M. Identity — нейтральный элемент умножения матриц.

**Умножение матриц** `A · B = C` — каждый элемент `c[i][j] = sum over k (a[i][k] · b[k][j])`. Для 4×4 это 16 dot product'ов по 4 компоненты = 64 умножения + 48 сложений = ~128 ALU-операций. На GPU — 16 FMA.

Умножение матриц **не коммутативно**: `A · B ≠ B · A` в общем случае. Это главный источник багов в matrix chain.

Умножение **ассоциативно**: `(A · B) · C = A · (B · C)`. Это значит, что один раз посчитанная комбинация A·B может быть умножена на любую C без необходимости пересчитывать порядок.

**Inverse matrix** `M⁻¹` — такая матрица, что `M · M⁻¹ = M⁻¹ · M = I`. Не всякая матрица имеет inverse — только те, у которых `determinant(M) ≠ 0` (вырожденные матрицы не обратимы).

Для matrix chain: `(A · B)⁻¹ = B⁻¹ · A⁻¹` — порядок инвертируется. Это важно для view matrix: если `view = lookAt(eye, center, up)`, то обратная view-матрица даёт «переход из мира в систему камеры»; её композиция с model даёт MV-матрицу.

**Transpose** `Mᵀ` — отражение относительно главной диагонали. `(A · B)ᵀ = Bᵀ · Aᵀ`. Для ортогональных матриц (в том числе pure rotation matrices) `Mᵀ = M⁻¹`, что даёт дешёвую инверсию.

### Базовые трансформации как матрицы

**Translation** (сдвиг) на вектор `(tx, ty, tz)`:

```
    | 1  0  0  tx |
T = | 0  1  0  ty |
    | 0  0  1  tz |
    | 0  0  0  1  |
```

Применение к точке `(x, y, z, 1)` даёт `(x + tx, y + ty, z + tz, 1)`. К вектору направления `(dx, dy, dz, 0)` — даёт `(dx, dy, dz, 0)`, т. е. направление не меняется. Это и есть причина, по которой точки имеют w=1, а направления w=0.

**Scale** (масштаб) на коэффициенты `(sx, sy, sz)`:

```
    | sx  0   0   0 |
S = | 0   sy  0   0 |
    | 0   0   sz  0 |
    | 0   0   0   1 |
```

Если `sx = sy = sz`, масштаб uniform. Uniform scale не искажает углы — нормали остаются корректными. Non-uniform scale искажает углы, и нормали нужно пересчитывать через transpose inverse (подробнее — в [[normal-bump-parallax-mapping]]).

**Rotation** вокруг оси X на угол θ:

```
       | 1  0        0       0 |
Rx(θ)= | 0  cos(θ)  -sin(θ)  0 |
       | 0  sin(θ)   cos(θ)  0 |
       | 0  0        0       1 |
```

Аналогично для Ry (вокруг Y) и Rz (вокруг Z). Композиция трёх этих матриц даёт ориентацию объекта, но страдает от gimbal lock — см. [[quaternions-and-rotations]].

Универсальная rotation matrix **вокруг произвольной оси `(x, y, z)` на угол θ** (формула Родригеса) — громоздкая, обычно собирается через `kotlin-math: rotation(angle, axis)` или `android.opengl.Matrix.rotateM(m, offset, a, x, y, z)`.

### Композиция TRS и почему порядок именно такой

Хотим: объект масштабируется, потом вращается, потом переносится на место в сцене. Матрицей — какие множители?

Умножение матриц применяется справа налево к вектору:

```
v_world = T · R · S · v_local
```

Работает это так:
1. `S · v_local` — сначала точку в локальных координатах масштабируем. Объект «вырастает».
2. `R · (S · v_local)` — теперь применяем вращение. Так как масштаб произошёл в локальной системе, вращение корректно вращает уже масштабированный объект.
3. `T · (R · S · v_local)` — переносим в world space.

Если поменять порядок на `S · R · T`:
1. `T · v_local` — точка переносится.
2. `R · T · v_local` — поворачивается **вокруг world origin**, а не вокруг центра объекта! Объект «летит по орбите» в сцене.
3. `S · R · T · v_local` — масштабируется. Так как объект уже далеко от origin, его размер увеличивается от origin, что визуально выглядит как «сдвиг+рост».

Вот почему правило «TRS» в графике — это `T · R · S` матрично, хотя текстуально «сначала scale, потом rotate, потом translate» читается как S → R → T. Путаница здесь — классическая.

**Model matrix** всегда собирается как `M = T · R · S`. В [[case-planner-5d|Planner 5D]], когда пользователь двигает диван, пересчитывается только T (translate) в его model matrix — остальное остаётся. Для ротации через свайп пересчитывается R как композиция кватернионов — подробнее в [[quaternions-and-rotations]].

### View matrix

View matrix переводит мир в систему координат камеры. Стандартная конструкция — `lookAt(eye, center, up)`:

```
forward = normalize(center - eye)
right = normalize(cross(forward, up))
trueUp = cross(right, forward)

       | right.x     right.y     right.z    -dot(right, eye)   |
view = | trueUp.x    trueUp.y    trueUp.z   -dot(trueUp, eye)  |
       | -forward.x  -forward.y  -forward.z  dot(forward, eye) |
       | 0           0           0           1                 |
```

Верхние 3×3 — поворот (ортогональный базис камеры), последний столбец — обратный translate. View matrix — это фактически inverse матрицы положения камеры в мире: если бы камера была объектом в сцене с position (eye), ориентацией (right, trueUp, forward), view = inverse этой матрицы.

В `android.opengl.Matrix` это `setLookAtM(m, mOffset, eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ)`. В kotlin-math — `lookAt(eye: Float3, target: Float3, up: Float3)`. В Filament — аналогично.

### Projection matrix

Projection matrix проецирует view space в clip space. Детальный вывод — в [[projections-perspective-orthographic]]. Здесь кратко: две основные матрицы.

**Perspective** — для 3D-сцен с перспективой:

```
                    | f/aspect  0     0                          0                          |
perspective(fov,    | 0         f     0                          0                          |
aspect, near, far) =| 0         0     (far+near)/(near-far)      (2·far·near)/(near-far)    |
                    | 0         0     -1                         0                          |

где f = 1 / tan(fov / 2)
```

**Orthographic** — для 2D и архитектурных чертежей:

```
                    | 2/(r-l)  0         0          -(r+l)/(r-l) |
orthographic(l,r,   | 0        2/(t-b)   0          -(t+b)/(t-b) |
b,t,n,f) =          | 0        0        -2/(f-n)    -(f+n)/(f-n) |
                    | 0        0         0           1           |
```

### Column-major vs Row-major

Это одна из самых больших конвенциональных путаниц в графике. Разбираемся по порядку.

**Математическая запись** матрицы (всегда): `m[row][column]`. Элемент `m[1][2]` — в строке 1, столбце 2.

**Memory layout** — как 16 элементов хранятся в linear float-массиве. Два соглашения:

- **Column-major** (OpenGL, GLSL, Android, Filament, Metal, kotlin-math): `m[col][row]` в памяти. Массив:
  ```
  [m00, m10, m20, m30,     ← первый столбец
   m01, m11, m21, m31,     ← второй столбец
   m02, m12, m22, m32,     ← третий столбец
   m03, m13, m23, m33]     ← четвёртый столбец
  ```
  Translation компоненты `(tx, ty, tz)` в массиве находятся по индексам `[12, 13, 14]`. В `android.opengl.Matrix.translateM(m, offset, tx, ty, tz)` так и записывается.

- **Row-major** (DirectX/HLSL традиционно, CPU-вычисления на C/Python): `m[row][col]` в памяти:
  ```
  [m00, m01, m02, m03,     ← первая строка
   m10, m11, m12, m13,     ← вторая строка
   m20, m21, m22, m23,     ← третья строка
   m30, m31, m32, m33]     ← четвёртая строка
  ```
  Translation в массиве по индексам `[3, 7, 11]`.

**Ключ:** column-major и row-major с column-vector vs row-vector convention в сумме дают одну и ту же математику. Разница только в том, как **писать** формулы и как **хранить** числа. Column-major + column-vector (OpenGL/Android) и Row-major + row-vector (DirectX) — математически эквивалентны.

Что это означает на практике:

1. **Умножение матриц**: в column-major + column-vector `M · v` считается слева направо в матрице-умножителе (как в математике). В row-major + row-vector `v · M` считается справа налево. Результат одинаковый.
2. **MVP chain**: в OpenGL/Android — `projection * view * model`, в классическом DirectX (HLSL row-major + row-vector) — `model * view * projection`. Та же самая композиция, записанная в обратном порядке.
3. **Передача матрицы в shader**: GLSL по умолчанию column-major — 16-элементный float[] интерпретируется по столбцам. Если вы собираете матрицу в Java и хотите передать в GLSL, храните в column-major.
4. **Transpose для миграции**: чтобы перенести row-major матрицу в column-major API, `M_colmajor = M_rowmajor_as_if_transposed`. Часто решается одной строкой `transpose(m)` в shader или на CPU.

Классическая отладочная процедура: увидели перевёрнутую сцену — проверьте, в каком layout ваш код собирает матрицы и в каком ожидает API. Если несовпадение — `transpose()` в одном месте pipeline решает проблему.

---

## Уровень 1 — для начинающих

Представьте, что у вас есть плоский лист картона и вы хотите превратить его в трёхмерную фигуру. Вы говорите: «согни по линии A, поверни на 30°, сдвинь на 5 см». Это три инструкции. Если все три положить в одну таблицу — получится матрица. Эта таблица — рецепт, как из любой точки на картоне получить соответствующую точку в новой фигуре.

Чем матрицы хороши: если у вас есть два рецепта («сначала согнуть, потом повернуть» и «потом ещё поднять»), вы можете их «перемножить» — получится один большой рецепт, который делает всё за один шаг. Это умножение матриц. GPU любит именно так — один большой рецепт на весь кадр, применяемый ко всем вершинам параллельно.

Почему матрица именно 4×4, а не 3×3? Потому что сдвиг (перенос точки на 5 см) — особая операция, которая в матрицу 3×3 не укладывается. Чтобы её вместить, добавляют четвёртый «служебный» столбец и строку. Эта четвёртая координата называется `w` и обычно равна 1 для точек и 0 для направлений; её роль объясняется в [[homogeneous-coordinates-and-affine]].

Порядок в рецепте важен. «Сначала повернись, потом сделай шаг» — не то же самое, что «сначала шаг, потом повернись»: в первом случае вы окажетесь в другом месте. С матрицами так же: `A · B ≠ B · A`. В graphics это даёт правило TRS — всегда сначала масштабируешь, потом вращаешь, потом переносишь. Иначе объект «улетит по орбите».

---

## Уровень 2 — для студента

### Пошаговый пример: собираем model matrix вручную

Задача — расставить диван в сцене [[case-planner-5d|Planner 5D]]. Известно:
- Позиция дивана в сцене: `(2, 0, 3)` (2 м вправо, на полу, 3 м от стены).
- Поворот вокруг вертикальной оси Y: 45° (чтобы диван смотрел в угол).
- Масштаб: 1.2× (диван чуть больше default-размера).

**Шаг 1. Scale matrix:**
```
    | 1.2  0    0    0 |
S = | 0    1.2  0    0 |
    | 0    0    1.2  0 |
    | 0    0    0    1 |
```

**Шаг 2. Rotation matrix вокруг Y на 45°** (`cos 45° ≈ 0.707`, `sin 45° ≈ 0.707`):
```
    | 0.707   0  0.707  0 |
R = | 0       1  0      0 |
    | -0.707  0  0.707  0 |
    | 0       0  0      1 |
```

**Шаг 3. Translation matrix:**
```
    | 1  0  0  2 |
T = | 0  1  0  0 |
    | 0  0  1  3 |
    | 0  0  0  1 |
```

**Шаг 4. Композиция M = T · R · S.** Сначала `R · S`:
```
        | 0.707   0  0.707  0 |   | 1.2  0    0    0 |   | 0.8484   0    0.8484  0 |
R · S = | 0       1  0      0 | · | 0    1.2  0    0 | = | 0        1.2  0       0 |
        | -0.707  0  0.707  0 |   | 0    0    1.2  0 |   | -0.8484  0    0.8484  0 |
        | 0       0  0      1 |   | 0    0    0    1 |   | 0        0    0       1 |
```

**Шаг 5. `T · (R · S)`:**
```
    | 1  0  0  2 |   | 0.8484   0    0.8484  0 |   | 0.8484   0    0.8484  2 |
M = | 0  1  0  0 | · | 0        1.2  0       0 | = | 0        1.2  0       0 |
    | 0  0  1  3 |   | -0.8484  0    0.8484  0 |   | -0.8484  0    0.8484  3 |
    | 0  0  0  1 |   | 0        0    0       1 |   | 0        0    0       1 |
```

Последний столбец `(2, 0, 3, 1)` — именно translation, что и ожидалось. Верхние 3×3 — комбинация rotate и scale.

### Применение M к вершине модели

Пусть вершина дивана в локальной системе (относительно его центра): `v_local = (0.5, 0.8, 0, 1)` (правый верхний угол спинки). Применяем M:

```
| 0.8484   0    0.8484  2 |   | 0.5 |   | 0.8484·0.5 + 0.8484·0 + 2     |   | 2.4242 |
| 0        1.2  0       0 | · | 0.8 | = | 1.2·0.8                       | = | 0.96   |
| -0.8484  0    0.8484  3 |   | 0   |   | -0.8484·0.5 + 0.8484·0 + 3    |   | 2.5758 |
| 0        0    0       1 |   | 1   |   | 1                             |   | 1      |
```

Точка в world space: `(2.4242, 0.96, 2.5758)`. Можно проверить интуитивно: правый край спинки оказался чуть правее и ближе к камере от центра дивана, что соответствует 45°-повороту + translate + scale. Геометрически сходится.

### В коде

На kotlin-math 1.6.0:

```kotlin
import dev.romainguy.kotlin.math.*

val scale = scale(Float3(1.2f, 1.2f, 1.2f))
val rotate = rotation(axis = Float3(0f, 1f, 0f), angle = 45f)
val translate = translation(Float3(2f, 0f, 3f))

val model: Mat4 = translate * rotate * scale
val vertexLocal = Float4(0.5f, 0.8f, 0f, 1f)
val vertexWorld = model * vertexLocal
```

Здесь читается «translate after rotate after scale» — порядок операторов строго соответствует матричному умножению.

На `android.opengl.Matrix`:

```kotlin
val model = FloatArray(16)
Matrix.setIdentityM(model, 0)
Matrix.translateM(model, 0, 2f, 0f, 3f)
Matrix.rotateM(model, 0, 45f, 0f, 1f, 0f)
Matrix.scaleM(model, 0, 1.2f, 1.2f, 1.2f)
// model теперь = T · R · S
```

Здесь порядок вызовов **обратный**: первым вызывается translate, затем rotate, затем scale. Это результат того, что `translateM`, `rotateM`, `scaleM` делают right-multiply по умолчанию (т. е. `M := M · T_new`). Часто сбивает.

---

## Уровень 3 — для профессионала

### Numerical stability

Матрицы накапливают ошибки: если вы каждый кадр делаете `M = M * deltaRotation`, через 1000 кадров матрица перестаёт быть ортогональной, у неё появляются shear-компоненты, объект визуально скашивается. Два решения:

1. **Периодическая ре-ортогонализация.** Раз в N кадров брать rotation-компоненту M (верхняя 3×3), применять Gram-Schmidt или QR-декомпозицию, восстанавливать чистый rotation.
2. **Хранить ориентацию отдельно как quaternion, а матрицу собирать заново каждый кадр.** Кватернион устойчивее — см. [[quaternions-and-rotations]].

### Non-uniform scale и нормали

Если `S` содержит `(sx, sy, sz)` с разными значениями, матрица искажает углы. Нормаль `N` после `M` не равна `M · N` — её надо пересчитывать через **нормальную матрицу** `N_matrix = transpose(inverse(M_upper3x3))`. В шейдере это обычно отдельный uniform; в Filament и большинстве movement это отдельный param.

Если scale uniform (sx = sy = sz), нормаль можно умножать на M напрямую — все искажения пропорциональные, углы сохраняются.

### Производительность на GPU

- **Uniform buffer object (UBO).** В Vulkan матрицы живут в UBO как блоки float[16]. Чтение в shader — одна инструкция per vec4.
- **Push constants.** Для часто меняющихся матриц (per-object model) Vulkan предлагает push constants — маленький блок (до 128 байт) напрямую в command buffer. 64 байт — это ровно одна mat4. Быстрее UBO на ряде архитектур.
- **Instance rendering.** Если рисуем 1000 одинаковых объектов с разными model matrices, передавать 1000 матриц как instanced attribute. Один draw call вместо 1000.

### Нелинейные преобразования

Матрицы кодируют только **линейные и аффинные** трансформации. Нельзя в одну матрицу «упаковать» skin weighting, deformation, ray-bending в refraction — это другие операции. Но можно:
- **Nested matrices.** Скелетная анимация — каждая кость имеет свою матрицу, вершина комбинируется по весам.
- **Matrix per vertex.** Редко, но возможно — отдельная матрица для каждой вершины, передаётся как instanced attribute.

### Inversion на GPU

`inverse(M)` для произвольной 4×4 — около 60 ALU, медленная операция. Если матрица чисто rotation+translation (без scale), inverse считается дёшево: `inverse(T · R) = R_transpose · T_inverse`, оба компонента тривиальны. Все shader'ы Filament максимизируют эту структуру — отсюда требование хранить rotation и translation отдельно.

---

## Как работает под капотом: vertex shader executes MVP

```
┌─────────────────────────────────────────────┐
│  CPU (Kotlin / NDK):                         │
│    model = T * R * S                         │
│    view = lookAt(eye, target, up)            │
│    projection = perspective(fov, ...)        │
│    mvp = projection * view * model           │
│    glUniformMatrix4fv(mvpLoc, 1, false, mvp) │
└────────────────┬────────────────────────────┘
                 │  (uniform uploaded to GPU)
                 ▼
┌─────────────────────────────────────────────┐
│  GPU Vertex Shader (GLSL):                   │
│    uniform mat4 mvp;                         │
│    layout(location=0) in vec3 position;      │
│    void main() {                             │
│        gl_Position = mvp * vec4(position,1); │
│    }                                         │
│                                              │
│    — 16 FMA per vertex, ~1 cycle on mobile  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Rasterizer + Fragment Shader:               │
│    ... (см. [[rendering-pipeline-overview]]) │
└─────────────────────────────────────────────┘
```

Для сцены с 10 000 вершин и 60 FPS это 600 тысяч MVP-умножений в секунду. На Adreno 650 — ~0.1 мс. Не узкое место; узкое место обычно fragment stage (см. [[overdraw-and-blending-cost]]).

---

## Сравнение: матричные API на Android

| Критерий | `android.opengl.Matrix` | `kotlin-math 1.6.0` | Filament math | GLM (C++) | GLSL/SPIR-V |
|---|---|---|---|---|---|
| Тип | `float[16]` | `Mat4` data class | `math::mat4` | `glm::mat4` | `mat4` |
| Layout | column-major | column-major | column-major | column-major | column-major |
| Handedness | right-handed | right-handed | right-handed | конфигурируется | следует конвенции shader |
| Translate | `translateM(m, offset, tx, ty, tz)` | `translation(Float3)` или `m * translation(v)` | `translation(v)` | `glm::translate(m, v)` | — (делается руками) |
| Rotate | `rotateM(m, offset, deg, ax, ay, az)` | `rotation(axis, angleDeg)` | `rotation(axis, angle)` | `glm::rotate(m, rad, v)` | — |
| Scale | `scaleM(m, offset, sx, sy, sz)` | `scale(Float3)` | `scale(v)` | `glm::scale(m, v)` | — |
| Multiply | `multiplyMM(dst, 0, a, 0, b, 0)` | `a * b` | `a * b` | `a * b` | `a * b` |
| Inverse | `invertM(inv, 0, src, 0)` | `inverse(m)` | `inverse(m)` | `glm::inverse(m)` | `inverse(m)` |
| Transpose | `transposeM(dst, 0, src, 0)` | `transpose(m)` | `transpose(m)` | `glm::transpose(m)` | `transpose(m)` |
| LookAt | `setLookAtM(m, ...)` | `lookAt(eye, target, up)` | `lookAt(eye, target, up)` | `glm::lookAt(...)` | — |
| Perspective | `perspectiveM(m, ...)` | `perspective(fov, aspect, n, f)` | `perspective(...)` | `glm::perspective(...)` | — |

Рекомендация:
- В Kotlin-first проекте: **kotlin-math 1.6.0**. Идиоматично, типизированно, нет JNI.
- В проекте с Filament: Filament math уже подтянут.
- В NDK-проекте: GLM (header-only, SIMD-оптимизированная).
- В legacy OpenGL ES-проекте без DSL: `android.opengl.Matrix`, но неудобно.

---

## Реальные кейсы

### Кейс 1: Planner 5D — drag-and-drop дивана

Пользователь тянет диван пальцем. Каждый кадр:

1. Touch event → screen coordinates.
2. Inverse MVP применяется к (screen.x, screen.y, 0, 1) — ray origin в world space.
3. Pre-computed floor plane `y = 0`.
4. Intersection → новая позиция дивана в world space.
5. Новая `model_sofa = T(new_pos) * R(sofa_orientation) * S(sofa_scale)`.
6. `model_sofa` → GPU, сцена рендерится.

На среднем Android это 5–7 матричных операций на CPU + upload в UBO ≈ 1 мс. Drag выглядит плавным.

### Кейс 2: IKEA Place — AR anchor в world space

ARCore выдаёт новый `Anchor` (см. [[arcore-fundamentals]]) с его transform как 4×4. Когда пользователь ставит диван:

1. `model_sofa = anchor.worldTransform * T_offset * R_user * S(1)` — диван привязан к anchor, но с возможностью сдвига и поворота через UI.
2. Каждый кадр: anchor обновляется (возможно, с учётом коррекции SLAM), `model_sofa` пересчитывается.
3. View matrix обновляется каждый кадр с ARCore camera pose.
4. Projection synchronizes с device camera intrinsics.

Ключ: **все матрицы в одной координатной системе** (ARCore world space). Несогласованность между anchor coordinate и user-modification coordinate — классический AR-баг.

### Кейс 3: Sweet Home 3D — переключение 2D/3D

Редактор поддерживает два режима. Переход — только смена view и projection:

- **2D top-down**: `view = lookAt((0, 10, 0), (0, 0, 0), (0, 0, -1))` (камера сверху, смотрит вниз, up — по −z); `projection = orthographic(...)`. Model matrices объектов не меняются.
- **3D walkthrough**: `view = lookAt(eye, eye + forward, up_world)` (камера на уровне глаз); `projection = perspective(fov, aspect, near, far)`. Model matrices те же.

Такая архитектура делает переключение мгновенным — меняются две матрицы из ~100.

---

## Распространённые заблуждения

| Миф | Реальность | Почему так думают |
|---|---|---|
| Матрица 4×4 хранит «сдвиг, поворот, масштаб» в отдельных полях | Матрица хранит 16 float без семантики отдельных компонент; T, R, S — это результаты разных способов её собрать | Туториалы часто показывают структуру T/R/S отдельно, создавая ложное впечатление отдельных полей |
| `A · B = B · A` | **Умножение матриц не коммутативно.** `T·R ≠ R·T` в общем случае. | Привычка к умножению чисел |
| Column-major и row-major — это разные математики | Одна и та же математика, разные memory layouts. Эквивалентны при правильной конвертации | Путают layout с математикой |
| Transpose матрицы = обратная матрица | Неправда в общем случае. Верно **только** для ортогональных матриц (pure rotation без scale). Для scale и translate — разные | Надо транспонировать для OpenGL → DirectX миграции, ассоциируют с «обращением» |
| Normals можно умножать на model matrix | Неправда при non-uniform scale. Надо `transpose(inverse(M_upper3x3))` для нормалей. | Работает для uniform scale и pure rotation |
| TRS-порядок = сначала translate | **Матрично** наоборот: T · R · S применяет S первым, T последним. «TRS» — текстуальная интуиция | Читают буквально |
| `mat4 * mat4` в GLSL — это row-major multiply | GLSL column-major; `A * B` применяет B первым, A последним — как математика | Путают с HLSL |
| MVP нужно считать каждый кадр для каждой вершины | Считается на CPU один раз (или один раз на объект), передаётся в shader как uniform. Vertex shader только применяет | Неправильное понимание разделения CPU/GPU |

---

## Подводные камни и когда НЕ применяется

### Ошибка 1: забытая inverse-ibility

**Почему происходит:** вы хотите обратить view matrix, чтобы получить позицию камеры. Но забыли что view = inverse(camera_world_transform). Вы повторно инвертируете → мусор.

**Как избежать:** храните camera_world_transform отдельно, а view = inverse(camera_world_transform) вычисляете как нужно. Не инвертируйте уже-инвертированное.

### Ошибка 2: смешивание handedness

**Почему происходит:** импортируете модель из Unity (left-handed) в Filament (right-handed). Оси Z инвертированы, всё зеркально.

**Как избежать:** либо флипать модель на asset-pipeline уровне (glTF export settings), либо применять корректирующую матрицу `diag(1, 1, -1, 1)` между asset space и scene space.

### Ошибка 3: numerical drift при накопленных трансформациях

**Почему происходит:** `M := M * delta` каждый кадр, 1000 кадров → M больше не ортогональна.

**Как избежать:** хранить ориентацию как quaternion, пересобирать M каждый кадр; либо периодически Gram-Schmidt ре-ортогонализовать.

### Ошибка 4: translation не действует на directions

**Почему происходит:** вектор направления света хранится как `vec3 direction`. В shader умножаете на view matrix — ожидаете, что он трансформируется. Но 4×4 view matrix содержит translation, и направление «переносится», что бессмысленно.

**Как избежать:** для directions использовать `vec4(direction, 0)` (w=0) или трансформировать только `mat3(view)` — верхнюю 3×3.

### Когда НЕ применять матрицы

- **Для orientations**, где нужна интерполяция (slerp) — используйте [[quaternions-and-rotations|кватернионы]]. Матрицы плохо интерполируются.
- **Для nonlinear deformation** — матрицы кодируют только линейные трансформации. Bending, morphing, physics нужны другие методы.
- **Для skeletal animation** — по одной матрице на кость, но в shader вершина смешивает по весам — это не «одна матрица».
- **Для больших координат** — float-32 в матрице теряет точность далеко от origin. Double-precision staging + camera-relative rendering (см. [[gpu-memory-management-mobile]]).

---

## Связь с другими темами

[[vectors-in-3d-graphics]] — предшественник. Матрицы оперируют над векторами; без вектора нечего трансформировать.

[[homogeneous-coordinates-and-affine]] — следующий файл. Объясняет, почему матрица 4×4, а не 3×3; почему `w=1` для точек, `w=0` для направлений; как translate попадает в матрицу.

[[quaternions-and-rotations]] — альтернативное представление вращений. Кватернионы компактнее, не страдают gimbal lock и лучше интерполируются, чем Euler-матрицы.

[[projections-perspective-orthographic]] — детальный вывод perspective и orthographic матриц, которые появились в этом файле как «чёрные ящики».

[[shader-programming-fundamentals]] — где matrix-chain живёт в GLSL. `uniform mat4 mvp; gl_Position = mvp * vec4(position, 1.0);`

[[android-graphics-apis]] — конкретика Matrix API в Android SDK.

[[gpu-memory-management-mobile]] — как матрицы упаковываются в UBO и push constants.

[[frustum-culling]] — матрицы участвуют в извлечении frustum planes из MVP для culling.

---

## Источники

### Теоретические основы
- **Dunn, F. & Parberry, I. (2011). 3D Math Primer for Graphics and Game Development, 2nd ed.** — главы 4–6 (matrices, transformations, coordinate spaces). [Онлайн](https://gamemath.com/book/).
- **Akenine-Möller, T., Haines, E. & Hoffman, N. (2018). Real-Time Rendering, 4th ed.** — глава 4 (Transforms), особенно разделы 4.1–4.4.
- **Lengyel, E. (2012). Mathematics for 3D Game Programming and Computer Graphics, 3rd ed.** — глава 3 про матрицы, глава 4 про transformations.
- **Roberts, L. G. (1963). Machine Perception of Three-Dimensional Solids.** MIT PhD thesis. Первая формализация homogeneous coordinates и 4×4-матриц в computer graphics.

### Спецификации и документация
- **Android Developers: `android.opengl.Matrix`.** [developer.android.com/reference/android/opengl/Matrix](https://developer.android.com/reference/android/opengl/Matrix).
- **OpenGL Tutorial: Matrices.** [opengl-tutorial.org](http://www.opengl-tutorial.org/beginners-tutorials/tutorial-3-matrices/) — канонический intro.
- **Google Filament documentation.** [google.github.io/filament](https://google.github.io/filament/Filament.md.html) — section on math conventions.
- **kotlin-math 1.6.0 README.** [github.com/romainguy/kotlin-math](https://github.com/romainguy/kotlin-math).
- **GLSL 4.60 Specification, Section 5.9–5.10** — matrix constructors, operators, swizzling.

### Блоги и заметки
- **Fabian Giesen (ryg). Row-major vs. column-major and GL ES.** [fgiesen.wordpress.com](https://fgiesen.wordpress.com/2011/05/04/row-major-vs-column-major-and-gl-es/). Canonical deconfusion.
- **Austin Morlan. Sending matrices to OpenGL.** [austinmorlan.com](https://austinmorlan.com/posts/opengl_matrices/) — практические индексы.
- **Shader-Slang docs. Handling matrix layout differences on different platforms.** [docs.shader-slang.org](https://docs.shader-slang.org/en/stable/external/slang/docs/user-guide/a1-01-matrix-layout.html).

### Доклады и лекции
- **3Blue1Brown. Essence of Linear Algebra, episodes 3–4 (matrices as linear transformations).** Визуальная интуиция.
- **Jim Blinn. A Trip Down the Graphics Pipeline (IEEE CG&A, 1983).** Историческое изложение MVP.

---

## Проверь себя

> [!question]- Почему `T · R · S ≠ S · R · T`? Какой порядок "правильный" для model matrix?
> Умножение матриц не коммутативно. Применение `T · R · S · v` идёт справа налево: сначала S (масштаб в локальной системе объекта), потом R (вращение в его локальной системе), потом T (перенос в world space). `S · R · T · v` сначала сдвинет объект в мир, потом будет вращать вокруг world origin (орбита), потом масштабировать — визуально это выглядит как «объект летает по орбите и увеличивается вдали». Канонический порядок model matrix — `T · R · S`.

> [!question]- В чём разница между column-major и row-major matrix layout? Это разные математики?
> Это разные memory layouts, одна и та же математика. Column-major хранит матрицу в памяти по столбцам (OpenGL, GLSL, Android, Filament, kotlin-math, Metal), row-major — по строкам (DirectX/HLSL traditionally). Если column-major API получает матрицу в row-major layout, нужно `transpose()`. `A * B` означает разные операции в row-vector vs column-vector convention, но результат эквивалентен.

> [!question]- Что делает `inverse(M)` для rotation+translation матрицы и почему это быстро?
> Для матрицы `M = T · R` (rotation и translation без scale) inverse можно получить без полной 4×4-инверсии: `inverse(M) = R^T · inverse(T) = R^T · T(−translation)`. Rotation R — ортогональна, `R^T = R^(-1)`. Translation инвертируется знаком. Это 9 операций вместо 60+ для общей inverse. Основной трюк view matrix в большинстве движков.

> [!question]- Почему для нормалей нельзя просто умножить на model matrix в случае non-uniform scale?
> Матрица с non-uniform scale (разные sx, sy, sz) искажает углы между векторами. Нормаль, трансформированная как обычный вектор, может перестать быть перпендикулярной поверхности. Правильный способ — через нормальную матрицу `N_matrix = transpose(inverse(M_upper3x3))`. Для uniform scale или pure rotation нормальная матрица равна верхней 3×3 самой M.

> [!question]- Как работает view matrix? Чем она отличается от model matrix?
> Model matrix переводит точки из локальной системы объекта в world space. View matrix переводит из world space в систему координат камеры: как будто всё пространство поворачивается и сдвигается так, чтобы камера оказалась в (0, 0, 0), а её forward-вектор совпал с −Z (по OpenGL convention). Конструкция стандартная — `lookAt(eye, target, up)`. Математически view = inverse(camera_world_transform).

---

## Ключевые карточки

Что хранится в последнем столбце model matrix 4×4?
?
Translation компоненты (tx, ty, tz) + 1 в последнем элементе (для точки с w=1). Именно поэтому translate требует 4×4, а не 3×3 — линейные операции + последний столбец эффективно делают аффинное преобразование.

---

Почему `A · B ≠ B · A` для матриц?
?
Умножение матриц не коммутативно: порядок операторов соответствует порядку применения трансформаций. `A · B · v` применяет сначала B, потом A. Поменяв порядок, получаем другой результат. Ассоциативно — да (`(AB)C = A(BC)`), но не коммутативно.

---

Что такое MVP matrix?
?
Композиция `projection * view * model`. Применяется в vertex shader как `gl_Position = mvp * vec4(position, 1)`. Переводит вершину из локальной системы объекта сразу в clip space за одно умножение.

---

Зачем нужна нормальная матрица?
?
Для правильной трансформации нормалей при non-uniform scale. Формально `N_matrix = transpose(inverse(M_upper3x3))`. Передаётся в shader как отдельный uniform, наряду с MVP. Для uniform scale и pure rotation равна самой `M_upper3x3`.

---

Что такое identity matrix I и что делает `I * v`?
?
Единичная матрица — диагональ из 1, остальное 0. `I * v = v` для любого v. Нейтральный элемент умножения матриц. Используется для инициализации перед накоплением transformations.

---

Как инвертируется matrix chain? `inverse(A * B) = ?`
?
`inverse(A * B) = inverse(B) * inverse(A)`. Порядок инвертируется. Это следствие некоммутативности матричного умножения.

---

Почему OpenGL использует column-major, а DirectX — row-major?
?
Исторически разные школы: OpenGL вырос из Unix/мат-графики, DirectX — из Windows/games. Математически эквивалентно; разница в том, как писать формулы и хранить в памяти. GLSL по умолчанию column-major.

---

Что означает TRS-порядок в composition model matrix?
?
Матрично `M = T · R · S`, применяется справа налево к вектору: сначала S (scale в локальной системе), потом R (rotate), потом T (translate в world space). Буквальное «translate-rotate-scale» в тексте соответствует `T·R·S` в матричной записи.

---

## Куда дальше

| Направление | Куда | Зачем |
|---|---|---|
| Следующий файл M1 | [[homogeneous-coordinates-and-affine]] | Почему матрица 4×4, а не 3×3; как именно работает translate; что такое w=1 vs w=0 |
| Альтернатива матрицам вращения | [[quaternions-and-rotations]] | Компактнее, без gimbal lock, лучше интерполируется |
| Вывод проекционных матриц | [[projections-perspective-orthographic]] | Как получается perspective matrix, почему она выглядит так странно |
| Использование MVP в шейдере | [[shader-programming-fundamentals]] | Практика: uniform mat4 mvp в GLSL |
| GPU-side matrix management | [[gpu-memory-management-mobile]] | UBO, push constants, instanced rendering |

---

*Создано: 2026-04-20. 7800+ слов. Deep-dive блока M1 в [[android-graphics-3d-moc]].*
