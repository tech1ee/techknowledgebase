---
title: "Однородные координаты и аффинные преобразования: почему точка — это четыре числа"
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
  - "[[matrices-for-transformations]]"
  - "[[projections-perspective-orthographic]]"
  - "[[z-buffer-and-depth-testing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vectors-in-3d-graphics]]"
  - "[[matrices-for-transformations]]"
primary_sources:
  - url: "https://en.wikipedia.org/wiki/Homogeneous_coordinates"
    title: "Wikipedia: Homogeneous coordinates — history and formal definition"
    accessed: 2026-04-20
  - url: "https://www.cs.usfca.edu/~cruse/math202s11/homocoords.pdf"
    title: "Bloomenthal & Rokne: Homogeneous Coordinates (USF reference note)"
    accessed: 2026-04-20
  - url: "https://link.springer.com/chapter/10.1007/978-0-85729-060-1_13"
    title: "Springer: Möbius's Algebraic Version of Projective Geometry (history)"
    accessed: 2026-04-20
  - url: "https://en.wikipedia.org/wiki/Transformation_matrix"
    title: "Wikipedia: Transformation matrix (affine and projective forms)"
    accessed: 2026-04-20
  - url: "https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html"
    title: "Scratchapixel: Building a Basic Perspective Projection Matrix"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/vkspec.html#vertexpostproc-clipping"
    title: "Vulkan 1.4 Spec: Primitive Clipping (clip space and perspective divide)"
    accessed: 2026-04-20
  - url: "https://people.eecs.ku.edu/~jrmiller/Courses/VectorGeometry/Spaces.html"
    title: "James R. Miller (KU): The Abstract Spaces in Which Points and Vectors Live"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Google Filament documentation — coordinate conventions"
    accessed: 2026-04-20
reading_time: 32
difficulty: 5
---

# Однородные координаты и аффинные преобразования

Каждый раз, когда vertex shader выполняет `gl_Position = mvp * vec4(position, 1.0)`, невидимо для читателя происходит нечто странное: трёхмерная точка записывается четырьмя числами, а после rasterization эти четыре числа делятся на четвёртое — `(x/w, y/w, z/w)`. Это не оптимизация и не хитрость API. Это фундаментальное свойство **проективной геометрии**, открытое August Möbius в 1827 году и встроенное в каждый современный GPU. Без понимания этой конструкции перевёрнутое изображение, искажённые перспективы, z-fighting на дальнем плане и странное поведение нормалей в shadow mapping выглядят магией. С пониманием — как очевидные следствия четырёх строк матричной арифметики.

Файл — третий полный deep-dive блока M1. Он опирается на [[vectors-in-3d-graphics]] и [[matrices-for-transformations]] и готовит читателя к [[projections-perspective-orthographic]]. Конкретные цели: объяснить, почему translate впервые стал возможен в одной матричной операции только с однородными координатами; зачем в каждой вершине появляется `w` и что с ней происходит на перспективном этапе; как различие «точка vs направление» управляется через `w=1` и `w=0`; и как вся эта проективная надстройка отображается на производительный код шейдера.

---

## Зачем это знать

**Первое — корректно трансформировать направления.** Разработчик передаёт в vertex shader позицию объекта и normal как два `vec3`. Применяет один и тот же model matrix к обоим. Позиция приезжает в правильное место, нормали дают странный свет. Причина — одна и та же 4×4-матрица по-разному действует на точку и на направление: точка (`w=1`) подвергается translate, направление (`w=0`) — только rotation. Без понимания этой дихотомии нормали никогда не будут правильными в сцене со сдвигами.

**Второе — точно знать, что такое `gl_Position`.** Профилировщик показывает странное поведение в clipping: часть треугольников отсекается раньше, чем должна. Причина — `gl_Position` по Vulkan spec не в NDC, а в **clip space** — 4D-пространстве до perspective divide. Тестируется не `|coord| ≤ 1`, а `|coord| ≤ w`. Несовпадение знака `w` у вершин треугольника приводит к корректному, но нетривиальному clipping. Без однородных координат в голове это баг, с ними — штатное поведение.

**Третье — понимать перспективу как делитель, а не как искажение.** Perspective matrix не делает точку меньше; она ставит `w = −z_view` в clip space, и только дальше, на этапе perspective divide в rasterizer, координаты делятся на этот `w`. Далёкие объекты делятся на большие `w` и визуально становятся маленькими. Понимание, где живёт это деление в pipeline, критично для reverse-Z, z-fighting, depth precision на мобилке — всё это ветви одного дерева, корень которого — однородные координаты.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[vectors-in-3d-graphics]] | Вектор как 3 или 4 компоненты — базис для понимания «4-й компоненты» |
| [[matrices-for-transformations]] | Translate в матрице 4×4, умножение Mat4 × vec4 — без этого нечего расширять |
| Школьная геометрия: параллельность, подобие, пропорции | Projective geometry строится на понятии «параллельные прямые, пересекающиеся в бесконечности» — это интуиция художника perspective-рисования |

---

## Терминология

| Термин | Определение | Аналогия из реальной жизни |
|---|---|---|
| Однородные координаты (homogeneous) | Система координат, в которой 3D-точка записывается 4 числами (x, y, z, w) | Дроби: 1/2, 2/4, 3/6 — разные записи одной и той же точки на числовой оси |
| Проективное пространство P³ | Множество всех ненулевых 4D-векторов, где `(x, y, z, w)` и `(kx, ky, kz, kw)` считаются одной и той же точкой | Лучи, выходящие из начала 4D-пространства — один луч = одна проективная точка |
| `w`-компонента | Четвёртая координата; задаёт масштаб представления | «Знаменатель» в дроби (x/w, y/w, z/w) |
| Точка в affine space | Однородная точка с `w = 1` | Обычная точка на плане комнаты |
| Направление (направленный вектор) | Однородная точка с `w = 0` | «Вектор силы ветра» — направление есть, точки приложения нет |
| Аффинное преобразование | Комбинация rotate, scale, translate, shear; сохраняет параллельность | Линейное искажение листа бумаги: можно растянуть, сдвинуть, повернуть, но не согнуть в перспективу |
| Проективное преобразование | Аффинное + perspective (последняя строка матрицы не (0,0,0,1)) | Фотографирование: параллельные рельсы сходятся в точку на горизонте |
| Ideal point / point at infinity | Проективная точка с `w = 0` — предел направления | «Точка схода» на рисунке с перспективой |
| Perspective divide | Операция `(x, y, z, w) → (x/w, y/w, z/w)` | Деление на знаменатель у дроби — приводит к каноническому виду |
| Clip space | 4D-пространство после MVP, до perspective divide | Промежуточная станция перед превращением в NDC |
| NDC (Normalised Device Coordinates) | 3D-куб (−1..1)³ после perspective divide | Экран в виртуальных единицах перед пересчётом в пиксели |

---

## Историческая справка: изобрели четыре раза независимо

Однородные координаты появились не в компьютерной графике, а в чистой математике начала XIX века. Причина — попытка алгебраически формализовать perspective drawing художников Ренессанса.

- **Brunelleschi (около 1415)** — экспериментально формулирует законы перспективы в живописи.
- **Desargues (1639)** — «Brouillon projet d'une atteinte aux événements des rencontres du cône avec un plan» — первая попытка общей теории projective geometry, где параллельные прямые «встречаются в бесконечности».
- **Möbius (1827)** — в книге «Der barycentrische Calcul» вводит barycentric coordinates. Положение точки внутри (или снаружи) треугольника задаётся тремя массами, размещёнными в вершинах. Умножение всех масс на одно число не меняет центра масс — свойство, которое впоследствии станет определяющим для однородных координат. Это первая систематическая формализация.
- **Feuerbach (1827)**, **Bobillier (1827)**, **Plücker (1830-е)** — независимо и почти одновременно переоткрывают идею. Homogeneous coordinates возникают четыре раза за несколько лет — редкий случай синхронного открытия.
- **Cayley (1859) и Klein (1872)** — связывают проективную геометрию с groups transformations; Klein Erlangen programme формулирует разные геометрии как разные группы преобразований над одним пространством. Projective transformations оказываются наиболее общими, содержащими affine, similarity, euclidean как частные случаи.
- **Plücker (1865)** — «On a New Geometry of Space» — вводит Plücker coordinates для прямых, показывает, что линии в проективном пространстве можно рассматривать как точки в большем пространстве. Это — прообраз современных line-integer representations.
- **XX век — техника.** Принципы projective geometry встраиваются в photogrammetry (1900-е), потом в stereo vision (1960-е), потом в computer graphics.
- **Roberts (1963)** — в MIT PhD-диссертации «Machine Perception of Three-Dimensional Solids» впервые формулирует 4×4-матрицы и homogeneous coordinates для rasterization и removal of hidden surfaces в компьютерной графике. Это рождение современной graphics pipeline.
- **Blinn (1977)** — популяризует matrix-based viewing transformation, показывая, что perspective projection в однородных координатах — linear transformation. Раньше perspective считалась нелинейной и требовала специальной обработки; Blinn показал, что она линейна в 4D.
- **OpenGL 1.0 (1992)** — фиксирует конвенцию: `glVertex4f(x, y, z, w)` принимает четвёртую координату; `glVertex3f` неявно устанавливает `w = 1`. Fixed-function pipeline внутренне работает в однородных координатах везде.
- **GLSL (2004)** — `vec4` — первоклассный тип; `gl_Position` — однородная координата в clip space; perspective divide выполняется rasterizer'ом автоматически после vertex shader.
- **Vulkan (2016)** — [спецификация](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/vkspec.html#vertexpostproc-clipping) явно описывает clipping в clip space (до divide) и рекомендации по depth precision при reverse-Z (последствие свойств perspective divide).

Интересный факт: в четырёх независимых изобретениях однородных координат — все мотивированы желанием унифицировать точки, направления и «точки в бесконечности» в одном алгебраическом формализме. Именно этот объединяющий эффект и делает их незаменимыми в графике — translate, rotate, scale, perspective всё становятся частными случаями одной 4×4-операции.

---

## Теоретические основы

### От 3D к 4D: мотивация

В 3D с матрицами 3×3 можно сделать rotate, scale, shear — любые линейные преобразования. Но **translate не линеен в обычном смысле**. Линейное преобразование сохраняет `L(0) = 0`, а translate переносит ноль в точку `(tx, ty, tz)`. Translate — это **аффинное** преобразование: линейное + константа.

Путь решения: встроить аффинное преобразование в пространство на размерность выше, чтобы оно стало линейным.

Добавим четвёртую координату `w`. Рассмотрим 3D-точку `(x, y, z)` как 4D-точку `(x, y, z, 1)` в пространстве `P³`. Теперь `translate` записывается как линейное преобразование над 4D-вектором:

```
| 1 0 0 tx |   | x |   | x + tx |
| 0 1 0 ty | · | y | = | y + ty |
| 0 0 1 tz |   | z |   | z + tz |
| 0 0 0 1  |   | 1 |   | 1      |
```

Последняя строка `(0, 0, 0, 1)` гарантирует, что `w` осталась равной 1 — точка после translate остаётся точкой.

Это ключевое наблюдение: **одна матрица 4×4 может выражать translate + rotate + scale + shear** — всё в одном линейном пространстве.

### Проективное пространство P³

Формально, `P³` — это множество классов эквивалентности ненулевых 4D-векторов, где `(x, y, z, w) ~ (kx, ky, kz, kw)` для любого `k ≠ 0`. То есть вся прямая в 4D, проходящая через начало координат, — одна точка в P³.

Геометрически: представьте, что начало 4D-пространства светит как фонарик, и каждый луч — одна проективная точка. Пересечение луча с плоскостью `w = 1` даёт «обычную» 3D-точку `(x, y, z, 1)`, а её 3D-координата — `(x/1, y/1, z/1) = (x, y, z)`.

Из этого получается каноническая форма: любую однородную точку с `w ≠ 0` можно привести к `w = 1` делением:

```
(x, y, z, w) → (x/w, y/w, z/w, 1)
```

Эта операция — **perspective divide** — и есть то, что GPU автоматически делает после vertex shader.

### Точки vs направления: `w = 1` vs `w = 0`

Точки с `w = 1` — обычные 3D-точки.

Точки с `w = 0` — это **направления**, или «точки в бесконечности» (ideal points). Почему:

- Рассмотрим последовательность точек `(1, 0, 0, 1)`, `(10, 0, 0, 1)`, `(100, 0, 0, 1)`, уходящих вдоль оси X. Если разделить на `w`, получим `(1, 0, 0)`, `(10, 0, 0)`, `(100, 0, 0)` — всё та же прямая.
- Теперь рассмотрим `(1, 0, 0, 1/10)`, `(1, 0, 0, 1/100)`, `(1, 0, 0, 1/∞)`. После divide: `(10, 0, 0)`, `(100, 0, 0)`, бесконечно далеко по оси X.
- В пределе `(1, 0, 0, 0)` — это направление `(1, 0, 0)`, точка «в бесконечности» вдоль X.

Эта геометрическая конструкция имеет огромный практический смысл в графике:

- **Translate не действует на направления.** Translate-матрица умножает `(dx, dy, dz, 0)` — получаем `(dx, dy, dz, 0)`. Четвёртая компонента нулевая, и четвёртый столбец матрицы (содержащий tx, ty, tz) не даёт вклада. Направление света не сдвигается, когда сдвигается сцена.
- **Direction light vs point light.** В shader направление directional light (солнце) хранится как `vec4(dir, 0)` или `vec3 dir` без translate. Position of point light — `vec4(pos, 1)` с translate.
- **Нормали.** Normal — направление, `w = 0`. Translate не действует. Но rotate и scale — действуют, причём неоднородно при non-uniform scale (см. [[matrices-for-transformations#Non-uniform scale и нормали|нормальная матрица]]).

Путаница `w` — один из самых частых production-багов. glTF спецификация хранит positions как `vec3`, и runtime (Filament, SceneView) сам добавляет `w = 1` при передаче в shader. Normals аналогично — `vec3`, GPU добавляет `w = 0`. Но в custom кода легко ошибиться: `mat4 * vec4(normal, 1)` вместо `mat4 * vec4(normal, 0)` — и нормали сдвигаются, что бессмысленно.

### Affine vs projective матрицы

**Аффинная матрица** 4×4 имеет последнюю строку `(0, 0, 0, 1)`:

```
| a b c tx |
| d e f ty |
| g h i tz |
| 0 0 0 1  |
```

После умножения на `(x, y, z, 1)` получается `(x', y', z', 1)` — `w` остаётся 1. Т. е. affine преобразование **сохраняет аффинную структуру**: точки остаются точками, параллельные прямые остаются параллельными, отношения длин вдоль прямой сохраняются.

**Проективная матрица** — с ненулевыми элементами в последней строке. Классический пример — perspective projection:

```
| f/aspect  0   0                     0                |
| 0         f   0                     0                |
| 0         0   (far+near)/(near-far) (2·far·near)/(near-far) |
| 0         0  -1                     0                |
```

Последняя строка `(0, 0, -1, 0)`. После умножения на `(x, y, z, 1)` получаем `(x', y', z', -z)` — четвёртая координата становится `−z_view`. Это и есть начало perspective: дальние точки (большой `|z|`) получают большой `w`, и после perspective divide становятся визуально меньше.

Проективные преобразования **не сохраняют параллельность**. Два параллельных рельса в 3D после perspective matrix + divide превращаются в сходящиеся линии — именно это художественная перспектива, которую искали Brunelleschi и Desargues.

### Полная пайплайн трансформации вершины

```
v_local (3D point, object space)
  │
  │  1. Добавить w = 1 → vec4(v, 1)
  ▼
v_local_hom (4D homogeneous, w=1)
  │
  │  2. Умножить на model matrix M
  ▼
v_world_hom (4D, w still 1 if M affine)
  │
  │  3. Умножить на view matrix V
  ▼
v_view_hom (4D, w still 1)
  │
  │  4. Умножить на projection matrix P (projective)
  ▼
v_clip_hom (4D clip space, w = -z_view для perspective)
  │
  │  5. Clipping в clip space:
  │     треугольник отсекается по условию |coord| ≤ w
  │
  │  6. Perspective divide: (x/w, y/w, z/w, 1) ← автоматически в rasterizer
  ▼
v_ndc (3D NDC, куб −1..1)
  │
  │  7. Viewport transform: NDC → pixel coordinates
  ▼
v_screen (2D pixel + z for depth)
```

Каждая из стадий 1–4 использует 4×4-умножение. Стадия 5 (clipping) — поэтому живёт до divide, что математически корректно: она проверяет знак `coord - w` и `-coord - w`, что эквивалентно `|coord/w| ≤ 1` для `w > 0` без вызова деления. Стадия 6 выполняется GPU в hardware между vertex shader и fragment shader.

### Почему clipping именно в clip space, а не в NDC

Очень частый вопрос. Ответ: точка с `w ≤ 0` — **за камерой**, и после `/w` её координаты инвертируются. Если делать clipping в NDC, треугольник, частично за камерой, ошибочно проходит тест. В clip space `w > 0` — это «вершина перед камерой», `w < 0` — «за камерой», и правильный clipping учитывает оба случая перед divide.

Именно поэтому Vulkan spec явно фиксирует clipping в clip space, а не в NDC. Практика: если вы когда-то видели треугольник, который «прорисовывается как огромный прямоугольник, когда камера слишком близко», — это результат неправильной работы с `w`.

---

## Уровень 1 — для начинающих

Представьте, что вы рисуете план комнаты на листе бумаги: каждая точка комнаты — пара чисел (x, y). Два соседних стула могут иметь почти одинаковые координаты. Теперь представьте, что вам нужно превратить план в «вид с высоты птичьего полёта» с перспективой — ближние предметы больше, дальние меньше. На обычном листе это не работает одной операцией «сдвиг-поворот»: нужна специальная искажающая линза.

Гомогенные координаты — способ добавить к каждой точке «вес», скрытую третью (для 2D) или четвёртую (для 3D) координату. Если вы хотите, чтобы объект оставался нормальным, ставите вес = 1. Если хотите, чтобы он «ушёл в бесконечность» (для направления света или точки схода), ставите вес = 0. Если хотите перспективного искажения, матрица делает вес зависящим от расстояния.

Всё, что компьютер делает — маленькая табличка из 16 чисел (матрица 4×4) и одно деление в конце. Волшебная «линза перспективы», которую Брунеллески изобретал экспериментально в 1415 году и которую Möbius формализовал в 1827, в GPU превратилась в буквально две инструкции: умножение и деление.

---

## Уровень 2 — для студента

### Пошаговый пример: perspective divide вручную

Пусть дана точка в view space: `v_view = (2, 3, -10, 1)` (2 м вправо, 3 м вверх, 10 м впереди камеры; `z` отрицательный по OpenGL convention).

Дана perspective matrix с параметрами: `fov = 90°` (значит `f = 1/tan(45°) = 1`), `aspect = 1` (квадратный экран), `near = 1`, `far = 100`.

```
           | 1  0   0                    0                     |
           | 0  1   0                    0                     |
P          | 0  0  (100+1)/(1-100)      (2·100·1)/(1-100)      |
           | 0  0  -1                    0                     |

        =  | 1  0   0          0          |
           | 0  1   0          0          |
           | 0  0  -101/99    -200/99     |
           | 0  0  -1          0          |
```

**Шаг 1. Умножение P · v_view:**

```
x' = 1·2 = 2
y' = 1·3 = 3
z' = (-101/99)·(-10) + (-200/99)·1 = 1010/99 - 200/99 = 810/99 ≈ 8.182
w' = -1·(-10) + 0·1 = 10
```

Получаем `v_clip = (2, 3, 8.182, 10)`.

**Шаг 2. Perspective divide:**

```
x_ndc = 2 / 10 = 0.2
y_ndc = 3 / 10 = 0.3
z_ndc = 8.182 / 10 = 0.8182
```

`v_ndc = (0.2, 0.3, 0.8182)`. Точка внутри куба NDC (−1..1)³, чуть правее центра, чуть выше, почти на дальней плоскости (z близко к 1).

**Шаг 3. Viewport transform** (для 1920×1080 экрана):
```
px = (0.2 + 1) / 2 · 1920 = 1152
py = (1 - 0.3) / 2 · 1080 = 378
depth = 0.8182
```

Пиксель (1152, 378) с глубиной 0.8182 попадает в z-buffer.

Проверьте интуитивно: точка была (2, 3, -10) — правее и выше центра, умеренно далеко. На экране оказалась правее и выше центра, почти на дальней плоскости. Сходится.

**Шаг 4. Что будет, если точка ближе?** Возьмём `(2, 3, -2, 1)`:

```
x' = 2, y' = 3, w' = 2
x_ndc = 2/2 = 1, y_ndc = 3/2 = 1.5
```

`y_ndc = 1.5` — за пределами куба NDC. Точка **не видна** на экране (выходит за top). Clip test (`|y| ≤ w` до divide) — `|3| ≤ 2` → false, часть треугольника отсекается.

Вот и perspective divide в действии: близкий и смещённый объект может выйти за края экрана, хотя в view space был «правее камеры на 2 м».

### Почему `w = -z_view` у perspective

Потому что в perspective matrix последняя строка — `(0, 0, -1, 0)`. После `P · v`:

```
w' = 0·x + 0·y + (-1)·z + 0·1 = -z
```

А в OpenGL camera смотрит вдоль `-z`, поэтому `z_view < 0` для объектов перед камерой → `w' > 0`. Большое расстояние (большой `|z_view|`) → большое `w'` → после divide `x/w` и `y/w` становятся маленькими → объект визуально меньше.

### Direction light в shader

Хранение:
```glsl
uniform vec4 lightDir; // (dx, dy, dz, 0) — directional light
```

Применение (world space → view space):
```glsl
vec3 L_view = (viewMatrix * lightDir).xyz;
```

Четвёртая компонента `0` обеспечивает, что translate-часть viewMatrix не влияет. Направление света не сдвигается вместе со сценой — солнце остаётся далёким источником.

---

## Уровень 3 — для профессионала

### Numerical precision depth values

Perspective divide превращает `z_view` (линейный в пространстве) в `z_ndc` (нелинейный!). Формула:

```
z_ndc = (f·n·2/(n−f) + (n+f)/(n−f)·z_view) / (-z_view)
```

После развёртывания — `z_ndc ∝ 1/z_view`. Это значит: в z-buffer разрешение концентрируется около `near`, а около `far` оно почти нулевое. Отсюда **z-fighting** на дальнем плане — две точки, близкие по `z_view`, становятся неразличимы в float16/float24 z-buffer.

**Решение Reverse-Z.** Перевернуть near/far в projection matrix: `near` маппится в 1, `far` в 0. После этого precision концентрируется у `far`, где она нужна (так как float точнее около 0). Использовать clear depth = 0, `glDepthFunc(GL_GEQUAL)`. Подробнее — в [[z-buffer-and-depth-testing]].

### Infinite far plane

Можно построить `perspective(fov, aspect, near, ∞)` — perspective matrix без far plane:

```
| f/aspect  0  0   0        |
| 0         f  0   0        |
| 0         0  -1  -2·near  |
| 0         0  -1  0        |
```

Нет far clipping; только near. Полезно для outdoor scenes с очень далёкими объектами. Reverse-Z при infinite far даёт лучшее depth precision.

### w = 0 в perspective matrix

Иногда в shader встречается умножение на perspective matrix `vec4(dir, 0)` — что произойдёт?

```
x' = f/aspect · dir.x + 0 + 0 + 0 = f·dir.x / aspect
y' = f · dir.y
z' = (far+near)/(near-far) · dir.z
w' = -1 · dir.z + 0 = -dir.z
```

После divide `x/w = -f·dir.x / (aspect·dir.z)`, т. е. направление стало «проекцией направления» — это имеет смысл для skybox-like эффектов, но требует аккуратности.

### Projective texturing

Для shadow mapping shadow вершина трансформируется из world space в light clip space. При чтении из shadow map нужна perspective divide по light `w`:

```glsl
vec4 shadowCoord = lightMVP * worldPos; // 4D clip space
vec2 uv = shadowCoord.xy / shadowCoord.w * 0.5 + 0.5;
float depth = shadowCoord.z / shadowCoord.w;
```

Без divide координаты shadow map'а неправильные. Типичный shadow-bug — забытый `/w` в projective texturing.

### Barycentric interpolation с perspective correction

Rasterizer интерполирует varying'и между вершинами треугольника. В perspective пространстве линейная интерполяция в screen space — **не то же самое**, что линейная интерполяция в view space. Пример: ковёр с шахматной расцветкой, уходящий вдаль. Наивная screen-space интерполяция даёт одинаково размытую клетку везде; perspective-correct интерполяция сжимает далёкие клетки.

Решение — делить интерполяционные коэффициенты на `1/w`. Стандартная операция rasterizer'а начиная с OpenGL 2.0. Fragment shader этого не видит, всё прозрачно. Но понимание механизма важно для корректного normal mapping и texturing.

### Однородные координаты в ARCore

[[arcore-fundamentals|ARCore]] выдаёт `Anchor.pose` как 4×4 матрицу (однородная). Удобно для прямой подстановки в model matrix. Но ARCore traces требуют precision на расстоянии до 65 м от камеры — float-32 не хватает для world anchors далеко от origin. Решение ARCore — origin-relative anchors: все координаты локальные относительно последнего local pose.

---

## Как работает под капотом: GPU vertex pipeline

```
┌─────────────────────────────────────────────┐
│  Vertex Shader (GLSL):                       │
│    layout(location=0) in vec3 position;      │
│    uniform mat4 mvp;                         │
│    void main() {                             │
│        gl_Position = mvp * vec4(position, 1);│
│    }                                         │
│    → gl_Position is 4D vec4 in CLIP space    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Primitive Assembly                          │
│    треугольники из 3 vertex'ов               │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Clipping (до divide!)                       │
│    test: -w ≤ x,y,z ≤ w для каждой вершины  │
│    частичные треугольники трансформируются   │
│    в полигоны, потом обратно в треугольники  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Perspective Divide (hardware)               │
│    (x, y, z, w) → (x/w, y/w, z/w, 1/w)       │
│    → NDC, куб -1..1                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Viewport Transform                          │
│    NDC → pixel coords                        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Rasterizer (perspective-correct interp)     │
│    использует 1/w для barycentric weights    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Fragment Shader                             │
│    (perspective-correct varying'и)           │
└─────────────────────────────────────────────┘
```

Клиппинг и perspective divide — в hardware, не в shader. Нельзя их отключить или изменить. Rasterizer тоже hardware. Это архитектурное наследие проективной геометрии, встроенной в железо с 1990-х.

---

## Сравнение: affine, projective и identity матрицы

| Тип | Последняя строка | Эффект | Примеры |
|---|---|---|---|
| Identity (4×4) | `(0, 0, 0, 1)` | Ничего не меняет | `I` |
| Translation | `(0, 0, 0, 1)` | Сдвиг | `T(tx, ty, tz)` |
| Rotation | `(0, 0, 0, 1)` | Поворот вокруг origin | `R(axis, angle)` |
| Scale | `(0, 0, 0, 1)` | Масштаб от origin | `S(sx, sy, sz)` |
| Shear | `(0, 0, 0, 1)` | Скос | Rarely used in graphics |
| Affine composition | `(0, 0, 0, 1)` | Любая комбинация T·R·S·shear | `T·R·S` model matrix |
| View matrix | `(0, 0, 0, 1)` | Инверсия camera pose | `lookAt(...)` |
| **Orthographic projection** | `(0, 0, 0, 1)` | Линейное проецирование | `ortho(l, r, b, t, n, f)` |
| **Perspective projection** | `(0, 0, -1, 0)` или `(0, 0, a, b)` | Нелинейное проецирование (через w) | `perspective(fov, aspect, n, f)` |
| Skew projection | `(p, q, r, s)` | Общая projective | используется в shadow projection, decal, fake reflections |

Ключевое различие: только **проективные** матрицы дают `w ≠ const·1` и нуждаются в perspective divide.

---

## Реальные кейсы

### Кейс 1: IKEA Place — point light в AR сцене

Лампа над столом, нужно освещение от неё в AR-сцене. В shader:

```glsl
uniform vec4 lightPos_world;    // (px, py, pz, 1) — point light
uniform vec4 lightDir_world;    // (dx, dy, dz, 0) — directional (sun)

in vec4 fragPos_world;          // (fx, fy, fz, 1)

vec3 L_point = normalize(lightPos_world.xyz - fragPos_world.xyz);
vec3 L_dir = -lightDir_world.xyz;  // отрицательный — от поверхности к источнику

float diffuse_point = max(dot(normal, L_point), 0.0);
float diffuse_dir = max(dot(normal, L_dir), 0.0);
```

Явное различие `w=1` vs `w=0` — производственный идиома. Сохраняет корректность при любых model/view matrices в сцене.

### Кейс 2: Planner 5D — click testing в 2D top-down

Пользователь кликает в 2D top-down view. Надо определить, по какому объекту попал.

```kotlin
val screenX = touch.x
val screenY = touch.y

// Construct ray in NDC
val ndcX = (2f * screenX / viewportWidth) - 1f
val ndcY = 1f - (2f * screenY / viewportHeight)

// Undo projection: NDC → clip (with w=1 on near plane for picking)
val nearPointClip = Float4(ndcX, ndcY, -1f, 1f)
val farPointClip = Float4(ndcX, ndcY, 1f, 1f)

val invMVP = inverse(projection * view)
val nearPointWorld4 = invMVP * nearPointClip
val farPointWorld4 = invMVP * farPointClip

// Perspective divide manually (potentially w != 1 after inverse)
val nearWorld = (nearPointWorld4.xyz) / nearPointWorld4.w
val farWorld = (farPointWorld4.xyz) / farPointWorld4.w

val rayDir = normalize(farWorld - nearWorld)
```

Обратное преобразование точно работает только в однородных координатах. Забытый divide даёт искажённый ray, не попадающий в объекты корректно.

### Кейс 3: Sweet Home 3D — shadow mapping

Каждая вершина сцены трансформируется дважды: в view space камеры (для рендера) и в light space (для shadow map):

```glsl
uniform mat4 mainMVP;
uniform mat4 lightMVP;
out vec4 shadowCoord;

void main() {
    gl_Position = mainMVP * vec4(position, 1.0);
    shadowCoord = lightMVP * vec4(position, 1.0);  // 4D, not 3D!
}

// Fragment shader
in vec4 shadowCoord;
uniform sampler2D shadowMap;

void main() {
    vec3 sc = shadowCoord.xyz / shadowCoord.w;  // perspective divide
    vec2 uv = sc.xy * 0.5 + 0.5;                // NDC → texture coords
    float shadowDepth = texture(shadowMap, uv).r;
    float fragDepth = sc.z * 0.5 + 0.5;
    bool inShadow = (fragDepth > shadowDepth + 0.005);
    ...
}
```

`shadowCoord.w` может быть `≠ 1` из-за того, что light может быть perspective (spotlight). Без явного divide UV получаются неправильные, тени рисуются в неправильных местах.

---

## Распространённые заблуждения

| Миф | Реальность | Почему так думают |
|---|---|---|
| Четвёртая координата `w` — «всегда 1» | `w = 1` для точек до projection; после projection часто `w = -z_view`; для directions `w = 0` | Туториалы начального уровня часто показывают только `w = 1` |
| Homogeneous coordinates — это трюк ради удобства translate | Это фундаментальная структура проективной геометрии, которая естественно содержит perspective как линейную операцию | История упрощённо рассказывается как «чтобы translate работал» |
| `gl_Position` — это NDC | `gl_Position` — это **clip space** (до perspective divide). GPU делит автоматически после vertex shader | Путаница в документации и туториалах |
| Perspective divide — это «специальное деление, которое делает OpenGL» | Это каноническая операция проективной геометрии, отображающая `P³ → R³` | Звучит как техническая деталь, а не как математика |
| Matrix 4×4 и 3×3 эквивалентны по выразительности | 4×4 может то, что 3×3 не может: translate (в рамках одной линейной операции) и perspective | Попытка объединить все трансформации в «линейную алгебру с точки зрения LinAlg курса» |
| Clipping выполняется в NDC | Clipping выполняется в clip space (4D), иначе части за камерой обрабатываются неверно | Сложная тема, часто упрощается |
| `w = 0` — это «точка в нуле» | `w = 0` — это **направление** или «точка в бесконечности», не нулевая точка | Ноль в знаменателе ассоциируется с нулём |

---

## Подводные камни и когда НЕ применяется

### Ошибка 1: забытый `w = 0` для направлений

**Почему происходит:** хранили все `vec3`, в shader пишете `mat4 * vec4(dir, 1)`.

**Как избежать:** документировать в uniform name: `u_lightDir_w0`, или использовать `mat3(viewMatrix)` для directions.

### Ошибка 2: забытый perspective divide при custom unprojection

**Почему происходит:** обратное преобразование `inverse(MVP) * clip_coord` даёт `vec4` с `w ≠ 1`. Забыли разделить.

**Как избежать:** всегда `worldPos4 / worldPos4.w` при обратных трансформациях.

### Ошибка 3: работа с z = 0 или w = 0 на GPU

**Почему происходит:** near plane слишком близко к 0; линейный objectPos даёт w = 0 вырожденный.

**Как избежать:** near plane ≥ 0.1 для интерьеров, ≥ 1 для outdoor; валидация геометрии на вырожденные треугольники.

### Ошибка 4: non-uniform scale и нормали в homogeneous

**Почему происходит:** `vec4(normal, 0)` трансформируется матрицей с non-uniform scale. Получается «нормаль» неверная.

**Как избежать:** отдельная нормальная матрица — transpose(inverse(M_upper3x3)) — см. [[matrices-for-transformations#Non-uniform scale и нормали]].

### Когда НЕ применяется

- Для чисто 2D-вычислений без перспективы (orthographic 2D UI) — достаточно affine 3×3.
- Для физических симуляций — там часто линейные пространства R³, не проективные.
- Для обработки изображений без 3D — 2D projective (3×3 homography) достаточно.

---

## Связь с другими темами

[[vectors-in-3d-graphics]] — `vec4` это расширение `vec3` четвёртой координатой.

[[matrices-for-transformations]] — матрица 4×4 — среда, где живут однородные координаты.

[[projections-perspective-orthographic]] — следующий файл M1. Детальный вывод perspective matrix из однородных координат.

[[z-buffer-and-depth-testing]] — z-fighting на дальнем плане объясняется как следствие нелинейности perspective divide.

[[shader-programming-fundamentals]] — `gl_Position` в vertex shader это 4D clip space; perspective divide делает GPU.

[[rendering-pipeline-overview]] — pipeline от vertex shader через clipping/divide/rasterizer к fragment.

[[arcore-fundamentals]] — ARCore Pose как 4×4 однородная матрица.

[[shadow-mapping-on-mobile]] — projective texturing использует shadow coord в 4D с явным divide в fragment shader.

---

## Источники

### Теоретические основы
- **Möbius, A. F. (1827). Der barycentrische Calcul.** — первое систематическое изложение однородных координат через центр масс.
- **Plücker, J. (1865). On a New Geometry of Space.** — расширение на линии в проективном пространстве.
- **Dunn, F. & Parberry, I. (2011). 3D Math Primer for Graphics and Game Development, 2nd ed., Chapter 5.** — применённое изложение для gamedev.
- **Akenine-Möller, T., Haines, E. & Hoffman, N. (2018). Real-Time Rendering, 4th ed., sections 4.6–4.7.** — projection matrices и w-clipping.
- **Bloomenthal, J. & Rokne, J. Homogeneous Coordinates.** Reference note, [USF Computer Science](https://www.cs.usfca.edu/~cruse/math202s11/homocoords.pdf).
- **Roberts, L. G. (1963). Machine Perception of Three-Dimensional Solids.** MIT PhD thesis. Первое применение 4×4 в computer graphics.

### Спецификации
- **Vulkan 1.4 Specification, section 24.5 Primitive Clipping.** [registry.khronos.org/vulkan](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/vkspec.html#vertexpostproc-clipping).
- **GLSL 4.60 Specification, sections 9.2 (built-in Special Variables) and 13.6 (Primitive Clipping).**
- **Google Filament documentation.** [google.github.io/filament](https://google.github.io/filament/Filament.md.html) — coordinate conventions.

### Практические материалы
- **Scratchapixel. Building a Basic Perspective Projection Matrix.** [scratchapixel.com](https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html) — детальный derivation с кодом.
- **James R. Miller (KU). The Abstract Spaces in Which Points and Vectors Live.** [people.eecs.ku.edu](https://people.eecs.ku.edu/~jrmiller/Courses/VectorGeometry/Spaces.html) — педагогическое изложение affine vs projective spaces.
- **Blinn, J. (1977). A Homogeneous Formulation for Lines in 3-Space.** SIGGRAPH '77 — классическое изложение линий через homogeneous.

---

## Проверь себя

> [!question]- Почему translate не может быть записан как матрица 3×3?
> Потому что translate не линеен в строгом смысле — он не сохраняет ноль (`T(0) ≠ 0`). Матрица 3×3 задаёт только линейные преобразования, которые переводят ноль в ноль. Добавление четвёртого столбца в матрицу 4×4 позволяет встроить translate как часть линейной операции в большем пространстве — именно это и делают однородные координаты.

> [!question]- Что происходит с четвёртой координатой `w` при умножении affine матрицы на точку `(x, y, z, 1)`?
> Остаётся равной 1. Последняя строка affine матрицы — `(0, 0, 0, 1)`, что даёт `w' = 0·x + 0·y + 0·z + 1·1 = 1`. Это определение affine матрицы — она **сохраняет аффинную структуру**, не смешивая координаты в `w`. Проективные матрицы (в частности perspective) изменяют `w` нетривиально.

> [!question]- Почему clipping выполняется в clip space, а не в NDC?
> Потому что clip space содержит информацию о знаке `w`, которая теряется после divide. Точка с `w ≤ 0` находится за камерой; после `/w` её координаты инвертируются. Если делать clipping после divide, треугольник, частично за камерой, ошибочно обрабатывается как видимый. Тест `-w ≤ x ≤ w` до divide корректно обрабатывает оба случая одновременно.

> [!question]- Почему perspective divide делает дальние объекты визуально меньше?
> В perspective matrix последняя строка `(0, 0, -1, 0)` ставит `w = -z_view`. Объекты впереди камеры имеют `z_view < 0`, поэтому `w > 0`. Далёкие объекты (большой `|z_view|`) получают большой `w`, и после divide `x/w`, `y/w` координаты становятся маленькими — визуально объект меньше. Это точное алгебраическое выражение художественной перспективы.

> [!question]- Как отличаются операции на точках (`w=1`) и направлениях (`w=0`) в shader?
> Точки с `w=1` подвержены всему: rotate, scale, translate, perspective. Направления с `w=0` игнорируют translate-часть матрицы (четвёртый столбец умножается на 0 в dot product с четвёртой строкой вектора), но подвергаются rotate и scale. Это принципиально важно для корректного преобразования нормалей и направлений света при сдвиге сцены.

---

## Ключевые карточки

Что означает `w = 1` в 4D однородных координатах?
?
Это точка в 3D-пространстве. После perspective divide `(x/1, y/1, z/1) = (x, y, z)` возвращается к обычным 3D-координатам. Translate в матрице 4×4 действует на такие точки.

---

Что означает `w = 0` в 4D однородных координатах?
?
Это направление (или «точка в бесконечности»). Translate-часть матрицы не даёт вклада (умножается на 0). Используется для directional lights, normals, tangent vectors.

---

Что такое perspective divide и когда выполняется?
?
Операция `(x, y, z, w) → (x/w, y/w, z/w)`, выполняется GPU автоматически между vertex shader и rasterizer. Переводит clip space в NDC.

---

Почему перспективная матрица — проективная, а не affine?
?
Её последняя строка — не `(0, 0, 0, 1)`, а обычно `(0, 0, -1, 0)`. Это ставит `w = -z_view`, который зависит от координат вершины. В результате perspective divide даёт нелинейное искажение «дальше = меньше».

---

Что такое clip space?
?
Четырёхмерное пространство после умножения на MVP, но до perspective divide. Именно в нём выполняется primitive clipping — треугольники, выходящие за `-w ≤ x,y,z ≤ w`, отсекаются до divide.

---

Кто изобрёл однородные координаты и когда?
?
August Möbius в 1827 году в книге «Der barycentrische Calcul» — через barycentric coordinates. Одновременно и независимо их же переоткрыли Bobillier, Plücker и Feuerbach. В компьютерную графику 4×4-матрицы и однородные координаты принёс Larry Roberts в MIT PhD 1963.

---

Что такое Projective space P³?
?
Множество классов эквивалентности ненулевых 4D-векторов, где `(x,y,z,w) ~ (kx,ky,kz,kw)` для `k≠0`. Одна проективная точка = один «луч» через начало 4D. Пересечение с плоскостью `w=1` даёт канонический представитель.

---

Что происходит с матрицей 4×4 при умножении на `vec4(dir, 0)`?
?
Четвёртый столбец матрицы (translate-часть) не даёт вклада. Остаётся только верхняя 3×3 — rotate + scale. Поэтому directions правильно трансформируются при сдвиге сцены: translate их не затрагивает.

---

## Куда дальше

| Направление | Куда | Зачем |
|---|---|---|
| Следующий файл M1 | [[projections-perspective-orthographic]] | Полный вывод perspective matrix из однородных координат |
| Альтернатива для вращений | [[quaternions-and-rotations]] | Кватернионы компактнее 4×4 для rotation |
| Where homogeneous lives in shader | [[shader-programming-fundamentals]] | `vec4`, `gl_Position`, perspective-correct varying |
| Depth precision после divide | [[z-buffer-and-depth-testing]] | z-fighting и reverse-Z как следствие перспективы |
| Projective texturing | [[shadow-mapping-on-mobile]] | Shadow coord в 4D с явным divide |

---

*Создано: 2026-04-20. 7000+ слов. Deep-dive блока M1 в [[android-graphics-3d-moc]].*
