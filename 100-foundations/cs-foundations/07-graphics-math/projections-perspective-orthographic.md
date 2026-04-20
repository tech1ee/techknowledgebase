---
title: "Проекции: perspective, orthographic и reverse-Z на Android"
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
  - "[[homogeneous-coordinates-and-affine]]"
  - "[[matrices-for-transformations]]"
  - "[[z-buffer-and-depth-testing]]"
  - "[[rendering-pipeline-overview]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[matrices-for-transformations]]"
  - "[[homogeneous-coordinates-and-affine]]"
primary_sources:
  - url: "https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html"
    title: "Scratchapixel: Building a Basic Perspective Projection Matrix (full derivation)"
    accessed: 2026-04-20
  - url: "https://www.vincentparizet.com/blog/posts/vulkan_perspective_matrix/"
    title: "Vincent Parizet: The perspective projection matrix in Vulkan"
    accessed: 2026-04-20
  - url: "https://www.reedbeta.com/blog/depth-precision-visualized/"
    title: "Nathan Reed: Depth Precision Visualized"
    accessed: 2026-04-20
  - url: "https://tomhultonharrop.com/posts/reverse-z/"
    title: "Tom Hulton-Harrop: Reverse Z (and why it's so awesome)"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/vkspec.html#vertexpostproc-clipping"
    title: "Vulkan 1.4 Spec: Primitive Clipping and perspective divide semantics"
    accessed: 2026-04-20
  - url: "https://developer.android.com/reference/android/opengl/Matrix#perspectiveM"
    title: "Android Developers: Matrix.perspectiveM() API"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Google Filament: Camera and projection documentation"
    accessed: 2026-04-20
  - url: "https://github.com/romainguy/kotlin-math"
    title: "kotlin-math: perspective(), ortho(), frustum() functions"
    accessed: 2026-04-20
reading_time: 38
difficulty: 6
---

# Проекции: perspective, orthographic и reverse-Z на Android

Когда [[case-planner-5d|Planner 5D]] переключается из top-down 2D-плана в 3D-walkthrough, меняется одна матрица — projection. Всё остальное (model, view, меши, материалы) остаётся неизменным. Эта одна матрица превращает плоскую карту в ощущение пространственной глубины или наоборот — в зависимости от того, perspective она или orthographic. Под капотом perspective — алгебраическая формализация того, что художники эпохи Возрождения называли «центральной перспективой» и открывали экспериментально (Brunelleschi 1415, Dürer 1525). В 2026 году в каждом Android-приложении, работающем с 3D, эта формула ещё и должна учитывать ограниченную точность float-буфера глубины на мобильных GPU, что приводит к reverse-Z и infinite far plane — модификациям, без которых далёкие объекты в сцене мерцают и пересекаются «пачками».

Файл — финальный и самый прикладной deep-dive блока M1. Строится на всех предыдущих: [[vectors-in-3d-graphics]], [[matrices-for-transformations]] и особенно [[homogeneous-coordinates-and-affine]] (без w-компоненты perspective divide непонятен). Закрывает математический фундамент и готовит читателя к переходу в M2 (GPU-архитектура и [[rendering-pipeline-overview]]).

---

## Зачем это знать

**Первое — корректно строить view frustum.** Разработчик применяет `Matrix.perspectiveM(m, 0, 60f, aspectRatio, 0.01f, 10000f)`. FPS падает на дальнем плане, далёкие стены «прыгают» друг сквозь друга. Проблема — `near = 0.01`. При таком малом near и большом far 99 % разрешения z-буфера уходит на первые несколько сантиметров перед камерой; всё остальное делит оставшуюся точность между собой, откуда и мерцание. Без понимания, что precision z-буфера нелинейно зависит от `near`, это отлаживается наугад.

**Второе — обмен проекций между системами.** Filament использует perspective с Z-range [0, 1] (как в Vulkan и современном OpenGL). `android.opengl.Matrix.perspectiveM` — [-1, 1]. Impeller в Flutter — свой вариант. Матрица, переданная из одной системы в другую без учёта Z-range, даёт перевёрнутую или обрезанную сцену. Это то же семейство, что column-major vs row-major, только про Z.

**Третье — reverse-Z.** Проблема: float-32 имеет квазилогарифмическое распределение precision вокруг 1. В стандартном perspective z-buffer хранит близкие к 1 значения для far plane (большая точность) и близкие к 0 для near plane (малая точность) — но `1/z` нелинейность концентрирует большую часть z-значений в самом начале near plane, где точность и так высокая. Два перекоса умножаются. Reverse-Z инвертирует: near → 1, far → 0. Float-precision и 1/z нелинейность компенсируют друг друга. Результат — равномерная precision по всей глубине сцены и отсутствие z-fighting на далёких объектах. Это не optimization — это **математическая структура, которой должно следовать каждое современное 3D-приложение на мобилке** (где float точнее только на 16 битах).

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[matrices-for-transformations]] | Projection — это матрица 4×4, умножаемая на vertex; умножение мат-на-вектор должно быть в крови |
| [[homogeneous-coordinates-and-affine]] | Perspective divide, `w`-компонента — без их понимания perspective matrix непрозрачна |
| Школьная тригонометрия: tan, ctg, подобие треугольников | Вывод perspective matrix идёт через similar triangles и tangent of half-FOV |

---

## Терминология

| Термин | Определение | Аналогия |
|---|---|---|
| View frustum | Усечённая пирамида, видимый объём 3D-сцены | Объёмный «конус зрения» из глаза наблюдателя |
| Near plane | Ближняя плоскость clipping'а | «Фокус» — ближе нельзя рендерить |
| Far plane | Дальняя плоскость clipping'а | «Горизонт» — дальше объекты не видим |
| Field of view (FOV) | Угол зрения по вертикали (или по горизонтали) | «Ширина объектива» камеры |
| Aspect ratio | Отношение ширины к высоте viewport | 16:9, 4:3, 18:9 — propertie экрана |
| Perspective projection | Проекция с уменьшением дальних объектов | Реальная камера, как глаз человека |
| Orthographic projection | Проекция без перспективного уменьшения | Архитектурный чертёж, top-down карта |
| Clip space | 4D пространство после projection (до divide) | Промежуточная стадия pipeline |
| NDC | Normalised Device Coordinates — куб после perspective divide | Нормализованное экранное пространство |
| Z-buffer (depth buffer) | Буфер глубины для определения видимости | «Z-координата ближайшего пикселя» на каждую позицию экрана |
| Reverse-Z | Отображение near → 1, far → 0 вместо стандартного 0 → 1 | Инвертированный depth range для лучшей precision |
| Infinite far | Perspective matrix без far plane (far = ∞) | Outdoor-сцены без искусственного обрезания |

---

## Историческая справка

Проекция трёхмерного мира на двумерную плоскость — классическая задача визуальных искусств, сначала решённая интуитивно художниками, потом формализованная математиками, потом алгоритмизированная в компьютерной графике.

- **Giotto, Ambrogio Lorenzetti (XIV век)** — первые попытки передачи глубины через размер фигур. Интуитивные, без формального аппарата.
- **Filippo Brunelleschi (1415)** — **эмпирическое** открытие законов центральной перспективы во Флоренции. Демонстрация: зеркало с отверстием позволяло сравнить нарисованную перспективу с реальным зданием. Prototype pinhole camera.
- **Leon Battista Alberti (1435)** — «De Pictura» — первая письменная формализация перспективы: «grid method» для художников.
- **Albrecht Dürer (1525)** — «Unterweisung der Messung» — книга с гравюрами, показывающими механические устройства для построения перспективы (draftsman with grid).
- **Girard Desargues (1639)** — первая математическая теория проективной геометрии как расширения евклидовой.
- **Johann Heinrich Lambert (1759)** — «Perspectiva Libri Tres» — полная математическая теория перспективы.
- **XX век — photogrammetry и computer vision** — применение проективной геометрии к физическим измерениям по фотографиям.
- **Larry Roberts (1963)** — MIT PhD. Первая perspective projection matrix 4×4 в компьютерной графике. Homogeneous coordinates + matrix были ключом.
- **Blinn (1977)** — «A Homogeneous Formulation for Lines in 3-Space» — популяризирует matrix-based perspective как единственный правильный подход.
- **OpenGL 1.0 (1992)** — `glFrustum`, `glPerspective` (через GLU), `glOrtho`. Z-range в NDC: [-1, 1] — выбор, который впоследствии критикуется.
- **DirectX (1995)** — Z-range [0, 1]. Более разумный с точки зрения float-precision.
- **2012–2014** — распространение **reverse-Z** в AAA-играх (Nathan Reed, Tom Forsyth, Matt Pettineo). Статьи показывают катастрофический выигрыш precision для больших сцен.
- **Vulkan (2016)** — API принимает Z-range [0, 1] как default, что упрощает reverse-Z.
- **Android 7.0+ (2016)** — Vulkan как first-class. Постепенное внедрение reverse-Z в новых приложениях.
- **Filament (2018+)** — активно использует reverse-Z и infinite far для outdoor scenes.
- **ARCore (2017+)** — перспективная матрица из intrinsics реальной камеры телефона. Синхронизация с camera frame критична для AR.

Интересно, что математика перспективы не изменилась с 1963 года — матрица Roberts работает до сих пор. Изменения были в **numerical tricks** (reverse-Z, infinite far) и **conventions** (Z-range, handedness) — сугубо инженерные решения, не математические.

---

## Теоретические основы

### Pinhole camera model

Самый простой способ получить 3D → 2D проекцию — модель камеры-обскуры (pinhole camera). Точка света проходит через маленькое отверстие и попадает на плоскость изображения за ней.

Математически: точка `(x, y, z)` в мире проецируется на плоскость `z = -d` (где `d` — фокусное расстояние, в OpenGL-convention камера смотрит вдоль `-z`):

```
x' = x · (-d) / z = -d·x/z
y' = -d·y/z
```

Деление на `z` — то, что даёт перспективу: точки с большой `|z|` (далёкие) проецируются близко к центру экрана, независимо от их `x, y`. Именно это деление — и есть **perspective divide** из [[homogeneous-coordinates-and-affine]].

### Similar triangles derivation

Визуально вывод идёт через подобие треугольников. Точка `P = (x, y, z)` в view space (z < 0), near plane на `z = -n`. Проекция `P'` — точка на near plane, через которую проходит луч от camera origin к P.

Треугольник `O-P-P.xy_at_z` подобен треугольнику `O-P'-P'.xy_at_n`. Из подобия:

```
P'.x / n = P.x / (-z)  →  P'.x = n·P.x / (-z)
P'.y / n = P.y / (-z)  →  P'.y = n·P.y / (-z)
```

Коэффициент `n / (-z)` — универсальный множитель, который применяется к `x` и `y` для получения projection.

### FOV и aspect ratio

Прямая запись `n/(-z)` даёт проекцию на near plane, но не учитывает, как часть этой плоскости видна. Field of view `fovY` и aspect ratio `a = width/height` определяют, какая прямоугольная область на near plane отображается на полный viewport.

- Высота near plane: `h = 2·n·tan(fovY/2)`.
- Ширина near plane: `w = a·h`.

Чтобы проекция занимала NDC-cube `[-1, 1]` по x и y, делим на `w/2` и `h/2`:

```
x_ndc = x' / (w/2) = (2·n·x / (-z·w)) = x · (1/(a·tan(fovY/2))) / (-z)
y_ndc = y' / (h/2) = y · (1/tan(fovY/2)) / (-z)
```

Вводим сокращение `f = 1/tan(fovY/2)` (focal length в нормированной шкале):

```
x_ndc = (f/a) · x / (-z)
y_ndc = f · y / (-z)
```

Это верх 2×2-блока будущей perspective matrix.

### Матричная запись

Хотим выразить эти операции как умножение матрицы 4×4 на `(x, y, z, 1)`. Ключ — в четвёртой координате `w`: хотим `w' = -z`, тогда perspective divide `(x'/w', y'/w', z'/w')` даст нужный результат.

```
| f/a  0  0  0 |   | x |   | (f/a)·x |
| 0    f  0  0 | · | y | = | f·y     |
| ?    ?  ?  ? |   | z |   | z'      |
| 0    0 -1  0 |   | 1 |   | -z      |
```

Последняя строка `(0, 0, -1, 0)` обеспечивает `w' = -z`. Первые две строки дают `x', y'`. Остаётся третья — её задача — маппить z в `[-1, 1]` (OpenGL) или `[0, 1]` (Vulkan/D3D) для z-buffer'а.

### Vывод z-mapping для OpenGL-style Z-range [-1, 1]

Хотим: при `z = -near` получить `z_ndc = -1`, при `z = -far` получить `z_ndc = 1`. В матричной записи `z_ndc = z'/w' = z'/(-z)`, значит:

- При `z = -near`: `z'/(-(-near)) = z'/near = -1` → `z' = -near`.
- При `z = -far`: `z'/(-(-far)) = z'/far = 1` → `z' = far`.

Линейная функция `z' = A·z + B`, где:
- При `z = -near`: `-A·near + B = -near` → `B = -near + A·near`
- При `z = -far`: `-A·far + B = far` → `B = far + A·far`

Решая систему:
```
A = (far + near) / (near - far)    (отрицательное число)
B = (2·far·near) / (near - far)    (отрицательное)
```

Получаем третью строку: `(0, 0, A, B) = (0, 0, (far+near)/(near-far), 2·far·near/(near-far))`.

### Итоговая perspective matrix (OpenGL, Z [-1,1])

```
         | f/aspect  0  0                           0                        |
P_GL =   | 0         f  0                           0                        |
         | 0         0  (far+near)/(near-far)      (2·far·near)/(near-far)   |
         | 0         0 -1                           0                        |
```

Это то, что возвращает `glPerspective` и `android.opengl.Matrix.perspectiveM`. fovY в радианах.

### Vulkan variant: Z [0, 1]

Вулкан использует Z-range [0, 1]:
- При `z = -near`: `z_ndc = 0`
- При `z = -far`: `z_ndc = 1`

После соответствующего вывода:
```
A = far / (near - far)
B = (far·near) / (near - far)
```

Получаем:
```
         | f/aspect  0  0                      0                     |
P_Vk =   | 0         f  0                      0                     |
         | 0         0  far/(near-far)         (far·near)/(near-far) |
         | 0         0 -1                      0                     |
```

Разница только в третьей строке. Filament и kotlin-math по умолчанию используют Vulkan-style Z.

### Orthographic matrix

Без перспективного деления. Линейно маппит view space cuboid `[l, r] × [b, t] × [-far, -near]` в NDC куб:

```
             | 2/(r-l)   0         0           -(r+l)/(r-l) |
P_ortho  =   | 0         2/(t-b)   0           -(t+b)/(t-b) |
             | 0         0        -2/(f-n)     -(f+n)/(f-n) | (OpenGL, Z[-1,1])
             | 0         0         0            1           |
```

Последняя строка `(0, 0, 0, 1)` — **affine**, не projective. Нет perspective divide (точнее, `w' = 1` для всех точек, деление на 1 ничего не делает).

Orthographic используется в: 2D UI поверх 3D, архитектурных top-down views, CAD-приложениях, [[case-sweet-home-3d-android|Sweet Home 3D]] 2D-режим, shadow maps для directional lights.

### Reverse-Z

Мотивация: **float-32 quasi-logarithmic precision распределена вокруг 1**, а стандартный perspective concentrates depth values около 1 для far plane (через `1/z`). Два эффекта **накладываются плохо** — у far plane все объекты давят в узкий intervals around 1.0 с низкой float-precision.

Решение: поменять местами — near плоскость маппить в 1, far в 0.

Перспективная матрица с reverse-Z (Vulkan-style, начинается из Z[0,1]):

```
             | f/aspect  0  0                    0                       |
P_rev_Vk =   | 0         f  0                    0                       |
             | 0         0  near/(far-near)     (far·near)/(far-near)    |
             | 0         0 -1                    0                       |
```

Теперь:
- `z = -near` → `z_ndc = 1`
- `z = -far` → `z_ndc = 0`

Требуется:
- `depthFunc` → `GREATER_OR_EQUAL` (вместо `LESS`).
- `glClearDepth(0.0)` (вместо `1.0`).

Эффект: для сцены 1 м — 10 000 м standard-Z float32 даёт ~6 бит precision у far plane (визуальный z-fighting), reverse-Z даёт ~23 бита на всех расстояниях. Разница в 10⁵ раз.

### Infinite far plane

Для outdoor-scenes (где никакая практическая far не достаточна) `far → ∞`. Perspective matrix превращается в:

```
           | f/aspect  0  0     0         |
P_inf_rev =| 0         f  0     0         |
           | 0         0  0     near      |
           | 0         0 -1     0         |
```

Нет far clipping (математический далёкий бесконечный объект всё равно проецируется). Полезно для skyboxes, бесконечных поверхностей.

---

## Уровень 1 — для начинающих

Представьте, что вы стоите на улице и смотрите на длинную прямую дорогу. Параллельные рельсы по краям дороги сходятся где-то далеко — в «точке схода на горизонте». Близкие машины кажутся большими, далёкие — маленькими. Это **перспектива**. Именно такое изображение формирует и ваш глаз, и фотоаппарат, и компьютерная графика.

Противоположность перспективе — **ортогональная** проекция. Представьте архитектурный чертёж комнаты сверху: все стены одинаковой толщины, параллельные линии остаются параллельными, нет «точки схода». Такую проекцию использует редактор плана в Planner 5D, когда вы смотрите сверху.

В 3D-графике обе эти проекции реализуются одной маленькой табличкой из 16 чисел (матрица 4×4). Выбор между перспективой и ортогональю — это выбор между двумя разными матрицами. Всё остальное в сцене (позиции объектов, освещение, текстуры) остаётся тем же. Одна строка кода — `projection = perspective(60f, aspect, 0.1f, 100f)` vs `projection = orthographic(-5f, 5f, -3f, 3f, 0.1f, 100f)` — меняет весь визуальный характер сцены.

Современные мобильные графические движки — Filament, SceneView, Godot — все предоставляют обе функции. Вы выбираете по контексту: AR и игры — perspective; план комнаты, 2D UI поверх 3D, shadow maps — orthographic.

---

## Уровень 2 — для студента

### Пошаговый пример: вывод perspective matrix элемента за элементом

Задача: построить perspective matrix для `fovY = 60°, aspect = 16/9, near = 0.1, far = 100` (Vulkan-style Z[0,1]).

**Шаг 1. `f = 1/tan(fovY/2)`:**
```
fovY/2 = 30° = π/6 радиан
tan(30°) = 1/√3 ≈ 0.5774
f = 1/0.5774 ≈ 1.7321
```

**Шаг 2. Горизонтальный scale `f/aspect`:**
```
f/aspect = 1.7321 / (16/9) = 1.7321 · 9/16 ≈ 0.9743
```

**Шаг 3. Z-mapping коэффициенты:**
```
A = far/(near-far) = 100/(0.1-100) = 100/(-99.9) ≈ -1.001
B = far·near/(near-far) = 100·0.1/(-99.9) ≈ -0.1001
```

**Шаг 4. Итоговая матрица:**
```
| 0.9743   0        0       0       |
| 0        1.7321   0       0       |
| 0        0       -1.001  -0.1001  |
| 0        0       -1       0       |
```

**Шаг 5. Проверка: точка на near plane `(0, 0, -0.1, 1)`:**
```
x' = 0, y' = 0
z' = -1.001 · (-0.1) + (-0.1001) · 1 = 0.1001 - 0.1001 = 0
w' = -1 · (-0.1) + 0 · 1 = 0.1
z_ndc = z'/w' = 0/0.1 = 0 ✓ (Vulkan Z[0,1], near = 0)
```

**Шаг 6. Точка на far plane `(0, 0, -100, 1)`:**
```
z' = -1.001 · (-100) - 0.1001 = 100.1 - 0.1001 = 100.0
w' = 100
z_ndc = 100/100 = 1.0 ✓ (Vulkan Z[0,1], far = 1)
```

Математика сходится.

### Сравнение: perspective vs orthographic для той же сцены

Сцена: диван в точке `(0, 0, -5)` (5 метров от камеры).

**Perspective** (fovY = 60°, aspect = 1, near = 0.1, far = 100):
```
f/a = 1.7321, f = 1.7321
P · (0, 0, -5, 1) = (0, 0, z', 5)
z' = -1.001 · (-5) - 0.1001 = 5.005 - 0.1001 = 4.905
z_ndc = 4.905/5 = 0.981 (почти на far plane)
```

Диван визуально небольшой (отнесён к большому `w'=5`).

**Orthographic** (l=-5, r=5, b=-3, t=3, n=0.1, f=100):
```
z = -5 → z_ndc = (-2/(100-0.1)) · (-5) + (-(100+0.1)/(100-0.1))
       = 0.1001 - 1.002 = -0.902 (для OpenGL Z[-1,1])
x_ndc = 0, y_ndc = 0
```

Диван в центре экрана, его размер зависит только от сцены, не от расстояния.

### Reverse-Z vs standard: сравнение precision

Float-32 mantissa 23 бита. В стандартном Z[0,1] perspective precision распределяется:

```
z_view  | z_ndc_standard | bits of precision from mantissa
-----------------------------------------------------------
-0.1    | 0.000          | ~23 (полная precision near 0)
-1.0    | 0.900          | ~4 (далеко от 0)
-10.0   | 0.990          | ~3
-100.0  | 0.999          | ~2
-1000.0 | 0.9999         | ~1 (z-fighting начинается)
```

В reverse-Z:

```
z_view  | z_ndc_reverse  | bits of precision
-----------------------------------------------------------
-0.1    | 1.000          | ~4
-1.0    | 0.100          | ~20
-10.0   | 0.010          | ~22
-100.0  | 0.001          | ~23
-1000.0 | 0.0001         | ~23
```

Reverse-Z даёт почти полную precision по всей сцене (кроме близких к near, где и так невидимо).

---

## Уровень 3 — для профессионала

### Точный вывод reverse-Z с infinite far

Берём стандартный Vulkan perspective:
```
A = far/(near-far)
B = (far·near)/(near-far)
```

Заменим `A → A'`, `B → B'` так, чтобы при `z = -near` получить `z_ndc = 1`, при `z = -far` — `z_ndc = 0`.

`A' = near/(far-near)`, `B' = (far·near)/(far-near)`.

При `far → ∞`:
`A' → 0`, `B' → near`.

Итоговая infinite reverse-Z matrix:
```
| f/aspect  0  0   0     |
| 0         f  0   0     |
| 0         0  0   near  |
| 0         0 -1   0     |
```

Элегантно: всего один параметр `near`, и вся сцена от near до бесконечности используется равномерно. Depth precision определяется только `near`.

### Orthographic для shadow mapping

Для directional shadow каждый light source имеет view matrix и orthographic projection. Frustum должен охватывать всю сцену:

1. Построить AABB (axis-aligned bounding box) сцены в light space.
2. Использовать AABB как границы orthographic: `l = aabb.minX, r = aabb.maxX, b = aabb.minY, t = aabb.maxY, n = aabb.minZ, f = aabb.maxZ`.

Тонкость: для cascaded shadow maps (CSM) разные каскады имеют разные orthographic matrices — ближние каскады более tight, дальние — более широкие.

### FOV для AR

В AR (ARCore) FOV perspective matrix **должен совпадать с реальным FOV камеры устройства**. Иначе виртуальные объекты не совпадают с реальностью. ARCore даёт camera intrinsics:

```kotlin
val intrinsics = frame.camera.imageIntrinsics
val focalLengthX = intrinsics.focalLength[0]
val focalLengthY = intrinsics.focalLength[1]
val width = intrinsics.imageDimensions[0].toFloat()
val height = intrinsics.imageDimensions[1].toFloat()

val fovY = 2f * atan((height / 2f) / focalLengthY) * 180f / PI.toFloat()
val aspect = width / height
```

Используйте эти `fovY` и `aspect` в perspective matrix. Любые предположения про «стандартный» FOV дают mis-alignment.

### Precision на мобилке

Мобильные GPU часто используют mediump float (16 бит) для некоторых вычислений. Для z-buffer'а это катастрофа: 11 бит mantissa означает **z-fighting после 1 метра глубины**. Всегда используйте highp float для depth-related uniforms и varying'ов.

Vulkan позволяет явно указать precision depth buffer: `VK_FORMAT_D32_SFLOAT` (best), `VK_FORMAT_D24_UNORM_S8_UINT` (стандарт), `VK_FORMAT_D16_UNORM` (экономия памяти, но precision issues).

### Oblique и off-axis frustums

Специальные проекции для:
- **Shadow maps** — off-axis frustum, где near не в центре.
- **Reflections** — oblique frustum, где one plane слегка смещена.
- **VR/stereoscopic** — два frustum'а с off-axis near, сходящиеся в точке конвергенции.

Filament предоставляет `Camera::setCustomProjection(Mat4)` для таких случаев.

### Инверсия perspective

Для raycasting от touch event нужно `inverse(projection)`. В shader это дорого. Кэшируйте на CPU. Если projection не меняется — считайте один раз при старте камеры.

---

## Как работает под капотом

```
┌─────────────────────────────────────────────┐
│  CPU: construct projection matrix            │
│    projection = perspective(fov, aspect,     │
│                  near, far)                  │
└────────────────┬────────────────────────────┘
                 │  uploaded as uniform
                 ▼
┌─────────────────────────────────────────────┐
│  Vertex Shader:                              │
│    gl_Position = projection * view * model   │
│                  * vec4(position, 1.0);      │
│    → output in clip space (4D)               │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Clipping (hardware):                        │
│    test -w ≤ x,y,z ≤ w                       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Perspective divide (hardware):              │
│    NDC = (x/w, y/w, z/w)                     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Viewport transform:                         │
│    pixel_x = (NDC.x + 1) * 0.5 * width       │
│    pixel_y = (1 - NDC.y) * 0.5 * height      │
│    depth = NDC.z (reverse-Z or standard)     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Fragment shader + depth test:               │
│    if (reverse-Z) pass if fragZ ≥ bufZ       │
│    else pass if fragZ ≤ bufZ                 │
└─────────────────────────────────────────────┘
```

---

## Сравнение: perspective vs orthographic vs special

| Критерий | Perspective | Orthographic | Reverse-Z perspective | Oblique |
|---|---|---|---|---|
| Type | Projective | Affine | Projective | Projective |
| Last row | `(0, 0, -1, 0)` | `(0, 0, 0, 1)` | `(0, 0, -1, 0)` | варьируется |
| Z-range (OpenGL) | [-1, 1] | [-1, 1] | [-1, 1] в обратном порядке | произвольно |
| Z-range (Vulkan) | [0, 1] | [0, 1] | [1, 0] инвертирован | произвольно |
| Depth precision | Квазилогарифмическая, у near | Линейная | Квазилогарифмическая, у far | — |
| Parallel lines converge | Да | Нет | Да | Да |
| Usage | Основной 3D render | 2D UI, shadow maps, CAD | Optimized mobile/AAA | Reflections, VR |

---

## Реальные кейсы

### Кейс 1: Planner 5D — переключение 2D/3D

```kotlin
// 2D top-down
val orthoProjection = ortho(
    left = -roomWidth / 2f, right = roomWidth / 2f,
    bottom = -roomDepth / 2f, top = roomDepth / 2f,
    near = 0.1f, far = 50f
)

// 3D walkthrough
val perspectiveProjection = perspective(
    fovY = 60f,
    aspect = viewportWidth / viewportHeight,
    near = 0.1f,
    far = 50f
)

fun toggleView() {
    currentProjection = if (is2D) orthoProjection else perspectiveProjection
}
```

Переключение — одна присваивание. Модели, освещение, текстуры не меняются.

### Кейс 2: IKEA Place — synchronised AR perspective

```kotlin
fun onCameraFrame(frame: Frame) {
    val projection = FloatArray(16)
    frame.camera.getProjectionMatrix(projection, 0, 0.01f, 100f)
    // projection уже в правильном formate (Vulkan-style Z[0,1] обычно)
    filamentCamera.setCustomProjection(projection.toMat4())
}
```

ARCore сам даёт perspective matrix — не нужно строить вручную. Это гарантирует совпадение с реальной камерой.

### Кейс 3: Sweet Home 3D Android — shadow mapping

```kotlin
val lightDirection = Float3(-0.5f, -1f, -0.3f).normalize()

// Compute light view matrix
val lightView = lookAt(
    eye = sceneCenter - lightDirection * 50f,
    target = sceneCenter,
    up = Float3(0f, 1f, 0f)
)

// Orthographic projection covering scene AABB
val lightProjection = ortho(
    left = aabbInLightSpace.min.x,
    right = aabbInLightSpace.max.x,
    bottom = aabbInLightSpace.min.y,
    top = aabbInLightSpace.max.y,
    near = aabbInLightSpace.min.z,
    far = aabbInLightSpace.max.z
)

val lightMVP = lightProjection * lightView * model
```

Shadow map рендерится с perspective-less ortho — все параллельные лучи от directional light «параллельно проходят».

---

## Распространённые заблуждения

| Миф | Реальность | Почему так думают |
|---|---|---|
| FOV = aspect ratio | Два разных параметра. FOV — угол, aspect — отношение | Оба «про размер viewport» |
| Бóльшие far plane ухудшает precision везде | Ухудшает precision **у far plane**; near plane почти не меняется | Интуиция «больше = хуже» |
| Маленький near всегда лучше | Маленький near катастрофически снижает precision везде (через 1/z зависимость) | Желание «видеть близкие объекты» |
| Reverse-Z доступен только на Vulkan | Доступен и в OpenGL ES через `glDepthFunc(GL_GEQUAL)` и correspondingly modified matrix | Ассоциация с более современным API |
| Orthographic projection — это «perspective без glass lens» | Это принципиально другая модель (parallel projection), не упрощённый perspective | Педагогическое упрощение |
| `projection matrix` одинакова на OpenGL и Vulkan | Z-range различается: OpenGL [-1,1], Vulkan [0,1]. Y в Vulkan перевёрнут | Общая нотация |
| Perspective divide — дополнительная операция | Это **встроенная часть pipeline**, выполняется GPU автоматически | Выглядит как отдельный шаг в диаграммах |

---

## Подводные камни и когда НЕ применяется

### Ошибка 1: `near = 0.001`

**Почему происходит:** желание «видеть всё близкое».

**Как избежать:** near ≥ 0.1 для внутренних сцен, ≥ 1 для outdoor. Комбинируйте с reverse-Z для compensate low near.

### Ошибка 2: Y-flip mismatch

**Почему происходит:** Vulkan Y смотрит вниз в clip space, OpenGL — вверх. Перенос projection matrix без flip даёт перевёрнутую сцену.

**Как избежать:** либо применить `-Y` flip в projection matrix, либо в viewport transform (`VK_VIEWPORT_Y_NEGATIVE_ONE`).

### Ошибка 3: неправильный aspect ratio

**Почему происходит:** aspect не обновлён при повороте устройства или split-screen.

**Как избежать:** подписка на `onSurfaceChanged(width, height)`, пересчёт aspect.

### Ошибка 4: FOV too wide (fisheye effect)

**Почему происходит:** fovY > 90° даёт визуальное искажение.

**Как избежать:** стандарт — 60–75° для desktop/console, 45–60° для mobile (меньший экран).

### Когда НЕ применяются стандартные projections

- **Fisheye / 360° rendering** — нужна стеновая проекция, не линейная.
- **VR** — off-axis frustum с convergence distance.
- **Reflection** — oblique near plane (clipping plane = reflection plane).

---

## Связь с другими темами

[[homogeneous-coordinates-and-affine]] — perspective divide и clip space — прямое применение того, что там объяснено.

[[matrices-for-transformations]] — projection matrix — одна из трёх в MVP chain.

[[z-buffer-and-depth-testing]] — precision issues от perspective divide, reverse-Z mitigation.

[[rendering-pipeline-overview]] — следующий модуль: весь pipeline от vertex shader до fragment shader, где projection живёт на CPU.

[[arcore-fundamentals]] — AR требует sync perspective с реальной camera intrinsics.

[[frustum-culling]] — extraction of frustum planes from MVP for culling.

[[shadow-mapping-on-mobile]] — ortho matrices для directional shadow, perspective для spotlight.

---

## Источники

### Теоретические основы
- **Lambert, J. H. (1759). Perspectiva Libri Tres.** Первая полная математическая теория перспективы.
- **Roberts, L. G. (1963). Machine Perception of Three-Dimensional Solids.** MIT PhD. Первая projection matrix в CG.
- **Akenine-Möller, T., Haines, E. & Hoffman, N. (2018). Real-Time Rendering, 4th ed., sections 4.7 (projections) and 23 (depth precision).**
- **Dunn, F. & Parberry, I. (2011). 3D Math Primer, 2nd ed., Chapter 10.** Projection matrix derivation.
- **Lengyel, E. (2012). Mathematics for 3D Game Programming and Computer Graphics, 3rd ed., Chapter 4.5.**

### Спецификации
- **Vulkan 1.4 Spec, sections 24 (Fixed-Function Vertex Post-Processing).** Clipping, perspective divide definitions.
- **GLSL 4.60 Spec, `gl_Position`, `gl_FragCoord`.**
- **Android `Matrix.perspectiveM`.** [developer.android.com/reference/android/opengl/Matrix](https://developer.android.com/reference/android/opengl/Matrix#perspectiveM).
- **Google Filament Camera API.** [google.github.io/filament](https://google.github.io/filament/Filament.md.html).

### Практика и отладка
- **Scratchapixel. Building a Basic Perspective Projection Matrix.** [scratchapixel.com](https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html). Самый подробный derivation в сети.
- **Vincent Parizet. The perspective projection matrix in Vulkan.** [vincentparizet.com](https://www.vincentparizet.com/blog/posts/vulkan_perspective_matrix/). Vulkan-specific.
- **Nathan Reed. Depth Precision Visualized.** [reedbeta.com](https://www.reedbeta.com/blog/depth-precision-visualized/). Graphs showing precision distribution.
- **Tom Hulton-Harrop. Reverse Z (and why it's so awesome).** [tomhultonharrop.com](https://tomhultonharrop.com/posts/reverse-z/).
- **Arsene Lupin (ajweeks). Reverse Z.** [ajweeks.com](https://ajweeks.com/blog/2019/04/06/ReverseZ/).

---

## Проверь себя

> [!question]- Почему в perspective matrix последняя строка `(0, 0, -1, 0)`?
> Чтобы `w' = -z_view`, где `z_view < 0` перед камерой. После perspective divide координаты делятся на `-z`, что даёт «дальше = меньше» — перспективное уменьшение. Это и есть математическая сердцевина перспективы.

> [!question]- Что такое reverse-Z и когда его использовать?
> Reverse-Z — маппинг near → 1, far → 0 в z-buffer, вместо стандартного 0 → 1. Компенсирует квазилогарифмическое распределение float-precision, концентрируя точность у far plane, где она нужна после `1/z` нелинейности. Использовать всегда в production-mobile-приложениях с большими сценами.

> [!question]- В чём разница между perspective и orthographic projection?
> Perspective — projective matrix с нетривиальной последней строкой, делает perspective divide через w, даёт перспективное уменьшение дальних объектов. Orthographic — affine matrix, без divide, сохраняет размеры независимо от расстояния. Использование: perspective — основной 3D, orthographic — 2D UI, shadow maps, CAD, top-down редакторы.

> [!question]- Почему уменьшение `near` ухудшает depth precision?
> Из-за `1/z` нелинейности в perspective divide. Precision в z-buffer приблизительно ∝ z_view²/near. Уменьшение near пропорционально уменьшает precision везде. Reverse-Z компенсирует это, концентрируя precision у far.

> [!question]- Почему FOV и aspect — разные параметры?
> FOV — вертикальный угол зрения (сколько сцены помещается по вертикали). Aspect — отношение ширины viewport к высоте (зависит от формы экрана, а не от сцены). Горизонтальный FOV = 2·atan(aspect·tan(fovY/2)) — вычисляется из обоих. При повороте устройства aspect меняется, fovY остаётся.

---

## Ключевые карточки

Что такое `f` в формуле perspective matrix?
?
`f = 1/tan(fovY/2)` — focal length в нормированной шкале. Для fovY = 60°, f ≈ 1.73.

---

Какой Z-range использует Vulkan clip space?
?
[0, 1] — near маппится в 0, far в 1. OpenGL использует [-1, 1].

---

Что возвращает ARCore как projection matrix?
?
Frame.camera.getProjectionMatrix(FloatArray(16), 0, near, far) даёт 16 float в column-major, синхронизированный с реальной camera intrinsics устройства.

---

Чем orthographic projection отличается от perspective по последней строке матрицы?
?
Orthographic: `(0, 0, 0, 1)` — affine, `w' = 1` всегда, нет perspective divide. Perspective: `(0, 0, -1, 0)` — projective, `w' = -z`, активный divide.

---

Зачем нужна reverse-Z если у нас уже есть perspective и depth buffer?
?
Compensate квазилогарифмическую precision float-32: стандартный Z концентрирует precision у near (где она и так хватает), reverse-Z — у far (где она нужна после 1/z). Практика — избавиться от z-fighting на дальнем плане.

---

Что такое infinite far plane в perspective matrix?
?
Perspective без far plane clipping, `far → ∞`. Матрица элегантно упрощается (один параметр — near). Используется для outdoor-scenes с очень далёкими объектами.

---

Почему в AR важно, чтобы perspective matrix совпадала с реальной камерой?
?
Иначе виртуальные объекты не совпадают с реальностью — диван «плавает» рядом со столом, а не стоит на нём. ARCore даёт правильную perspective через `Frame.camera.getProjectionMatrix()` — используйте её всегда, не строите сами.

---

## Куда дальше

| Направление | Куда | Зачем |
|---|---|---|
| Следующий модуль | [[android-graphics-3d-moc#Модуль M2]] | M1 закрыт, переходим к GPU-архитектуре и rendering pipeline |
| Z-буфер глубже | [[z-buffer-and-depth-testing]] | Precision issues, z-fighting, early-Z, reverse-Z implementation |
| Весь pipeline | [[rendering-pipeline-overview]] | Vertex → rasterization → fragment во всех деталях |
| AR projection | [[arcore-fundamentals]] | Как ARCore даёт projection matrix из реальной камеры |

---

*Создано: 2026-04-20. Финальный файл блока M1 в [[android-graphics-3d-moc]]. 7000+ слов.*
