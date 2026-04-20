---
title: "Z-буфер и depth testing: как GPU решает, какой пиксель ближе"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/deep-dive
  - level/intermediate
related:
  - "[[projections-perspective-orthographic]]"
  - "[[rendering-pipeline-overview]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[projections-perspective-orthographic]]"
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://www.reedbeta.com/blog/depth-precision-visualized/"
    title: "Nathan Reed: Depth Precision Visualized"
    accessed: 2026-04-20
  - url: "https://tomhultonharrop.com/posts/reverse-z/"
    title: "Tom Hulton-Harrop: Reverse Z (and why it's so awesome)"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#fragops-depth"
    title: "Vulkan 1.4: Depth Test spec"
    accessed: 2026-04-20
  - url: "https://developer.android.com/games/optimize/depth-buffer"
    title: "Android: Depth buffer formats"
    accessed: 2026-04-20
reading_time: 18
difficulty: 4
---

# Z-буфер и depth testing

Когда в сцене [[case-planner-5d|Planner 5D]] пользователь ставит стул за стол, пиксель на экране должен показать «стол, потому что стол ближе к камере». Это решение — работа **depth buffer** (z-buffer), фундаментального изобретения [Catmull 1974](https://link.springer.com/chapter/10.1007/978-1-4612-5094-1_7), который в PhD-диссертации в University of Utah описал: для каждого пикселя экрана хранить глубину ближайшего отрисованного фрагмента; при появлении нового — сравнивать с сохранённой глубиной.

Этот deep-dive покрывает: precision-проблему mobile float32 z-buffer, reverse-Z как production-стандарт, early-Z optimization, depth format selection (D16/D24/D32), z-fighting причины и mitigation. Файл — часть модуля M2 в [[android-graphics-3d-moc]].

---

## Зачем это знать

**Первое — z-fighting.** Две стены в Sweet Home 3D, касающиеся друг друга. На близком расстоянии всё ок, на дальнем — мерцающий узор. Причина — precision depth buffer на far plane. Исправление: reverse-Z или raising near plane.

**Второе — format choice.** D16 (16-bit float) экономит память, но z-fighting наступает почти сразу. D32_SFLOAT — максимум precision, но 2× memory. D24_UNORM_S8_UINT — стандарт compromise, включает stencil. Выбор формата влияет на framebuffer size.

**Третье — early-Z enablement.** Fragment shader с `discard` или `gl_FragDepth` отключает early-Z. Это может удваивать stunning cost на hot paths.

---

## Prerequisites

- [[projections-perspective-orthographic]] — perspective divide нелинейность
- [[rendering-pipeline-overview]] — где в pipeline depth test

---

## Терминология

| Термин | Определение |
|---|---|
| Z-buffer (depth buffer) | Буфер глубины размера viewport, хранит z ближайшего fragment на pixel |
| Depth test | Сравнение fragment z с хранящимся в z-buffer значением |
| Depth write | Запись fragment z в z-buffer после успешного test |
| Early-Z | Depth test **перед** fragment shader, возможен если shader не пишет FragDepth и не использует discard |
| Late-Z | Depth test после shader (когда early-Z невозможен) |
| Z-fighting | Артефакт мерцания, когда precision z-buffer недостаточно |
| Reverse-Z | Конвенция near → 1, far → 0 для лучшего использования float-precision |
| Depth bias | Смещение для сравнения (avoid z-fighting между touching surfaces) |
| Depth clamp | Отключение near/far clipping, depth clamped to [0,1] |

---

## Историческая справка

Z-buffer — одно из немногих изобретений в computer graphics, где можно назвать дату и автора. Вот полный контекст:

- **1974 — Ed Catmull.** Диссертация «A Subdivision Algorithm for Computer Display of Curved Surfaces» (University of Utah). Catmull описывает algorithmic problem: как отобразить 3D surface на 2D screen с правильным hidden surface removal. Ранее использовались painter's algorithm (отсортировать polygons по distance, рисовать back-to-front) или BSP trees. Обе плохо scalable. Catmull предлагает: для каждого pixel хранить depth. Линейный по memory, независим от сцены.
- **1975 — Tom Duff, Henry Fuchs.** Независимо предлагают похожие идеи в CGI/SIGGRAPH публикациях.
- **1978 — Fuchs et al. BSP trees** для hidden surface. BSP остался в architecture-heavy scenes (Quake 1996).
- **1983 — Silicon Graphics Iris 2000.** Первый commercial GPU с hardware z-buffer.
- **1996 — 3dfx Voodoo 1.** Consumer-grade Z-buffered rasterizer. Революция PC gaming.
- **1999 — Early-Z optimization появляется.** ATI Radeon и NVIDIA GeForce 3 имплементируют.
- **2003 — Hierarchical Z (Hi-Z).** Block-level summary буфер для быстрого tile rejection.
- **2009 — Reverse-Z описан.** [Matt Pettineo](https://therealmjp.github.io/posts/reversed-depth-buffer/), [Nathan Reed](https://www.reedbeta.com/blog/depth-precision-visualized/) и другие популяризируют.
- **2015 — Windows 10 DX12.** Microsoft рекомендует reverse-Z как «best practice» для новых игр.
- **2020+ — Filament, Unreal, Unity** все switch на reverse-Z default для новых проектов.
- **2024 — Variable rate depth.** Некоторые GPU могут делать depth test с разной resolution по regions экрана.

Интересный факт: Catmull — co-founder Pixar Animation Studios. Тот же человек, кто изобрёл z-buffer, основал студию, которая использовала его для Toy Story (1995).

---

## Теоретические основы

### Catmull 1974 — оригинальная идея

Для каждого пикселя экрана храним:
1. Текущий цвет пикселя (color buffer).
2. Текущую глубину ближайшего нарисованного фрагмента (z-buffer).

При рендере нового fragment:
1. Вычислить его z.
2. Сравнить с сохранённым в z-buffer по координатам (x, y).
3. Если ближе — записать новый color и новый z. Иначе — отбросить.

Elegant, parallel-friendly (no sorting of primitives). С 1980-х — стандарт всей аппаратной графики.

### Математика precision: откуда берётся нелинейность

Glubina в z-buffer хранится **после perspective divide**. Perspective projection matrix (стандартная):

```
P = | f/aspect  0                   0                     0                          |
    | 0         f                   0                     0                          |
    | 0         0       (near+far)/(near-far)   (2*near*far)/(near-far)              |
    | 0         0                  -1                     0                          |
```

где `f = 1/tan(fovY/2)`.

После умножения точки `(x, y, z_view, 1)`:
- `clip.z = (near+far)/(near-far) * z_view + (2*near*far)/(near-far)`
- `clip.w = -z_view`

После perspective divide:
```
z_ndc = clip.z / clip.w = -( (near+far) + 2*near*far / z_view ) / (near-far)
```

Это **гиперболическая функция** `z_view`. Для `near=0.1, far=1000`:
- `z_view = 0.1` → `z_ndc = 0.0`
- `z_view = 1.0` → `z_ndc = 0.9001`
- `z_view = 10.0` → `z_ndc = 0.99001`
- `z_view = 100.0` → `z_ndc = 0.99901`
- `z_view = 1000.0` → `z_ndc = 1.0`

Логарифмическое распределение. Precision `z_view` около far — практически нулевая.

### Float32 precision — второй шрам

Float32 хранит ~23 бита mantissa. Для значений около `1.0`:
- Precision = 2^(-23) ≈ 1.2 × 10⁻⁷.

Для значений около `0.0001`:
- Exponent снижается, effective precision shifts — ~1.0 × 10⁻¹¹ (много точнее).

Стандартный z-buffer концентрирует values около `1.0` для far — удваивает проблему.

### Reverse-Z математически

Reverse-Z inverts: `z_ndc_rev = 1 - z_ndc`.

```
z_view = 0.1   → z_ndc_rev = 1.0    (near)
z_view = 1.0   → z_ndc_rev = 0.0999
z_view = 10.0  → z_ndc_rev = 0.00999
z_view = 100.0 → z_ndc_rev = 0.00099
z_view = 1000.0→ z_ndc_rev = 0.0    (far)
```

Now near z_ndc values около 1.0 (low float precision) соответствуют near objects, где precision не критична (объекты близко). Far z_ndc values около 0.0 (high float precision) соответствуют far objects, где precision критична.

Выигрыш: ~20 бит effective precision вместо ~4.

### Nonlinear precision (legacy)

После perspective divide (см. [[homogeneous-coordinates-and-affine]]) z-ndc ∝ `1/z_view`. Большая часть precision концентрируется около near plane. Типичная картина:

| z_view (м) | z_ndc (стандарт 0→1) |
|---|---|
| 0.1 (near) | 0.000 |
| 1.0 | 0.900 |
| 10.0 | 0.990 |
| 100.0 | 0.999 |
| 1000.0 | 0.9999 |

Float32 имеет precision около 1.0 очень низкую — это и есть проблема z-fighting на far plane.

### Reverse-Z решение

Меняем convention: near → 1, far → 0. Теперь:

| z_view (м) | z_ndc_reverse |
|---|---|
| 0.1 | 1.000 |
| 1.0 | 0.100 |
| 10.0 | 0.010 |
| 100.0 | 0.001 |
| 1000.0 | 0.0001 |

Float32 имеет **больше precision около 0**, а значит precision распределена гораздо равномернее. Z-fighting resolved.

Implementation:
- Modified perspective matrix (см. [[projections-perspective-orthographic]]).
- `VkPipelineDepthStencilStateCreateInfo.depthCompareOp = VK_COMPARE_OP_GREATER_OR_EQUAL`.
- `vkCmdClearDepthStencilImage` depth = 0.0 (было 1.0).

### Format choice

| Format | Размер | Precision | Применение |
|---|---|---|---|
| D16_UNORM | 2 byte | 16-bit fixed | Экономия памяти, только простые сцены |
| D24_UNORM_S8_UINT | 4 byte (24+8) | 24-bit fixed + 8-bit stencil | Самый стандарт, good для shadow maps |
| D32_SFLOAT | 4 byte | 23-bit mantissa float | Best для reverse-Z, main depth buffer |
| D32_SFLOAT_S8_UINT | 5 byte (pad to 8) | 32-bit + stencil | Максимум, memory-heavy |

На TBR memoryless transient attachment (см. [[tile-based-rendering-mobile]]) — depth вообще не попадает в DRAM. Format выбирается свободно.

### Depth bias (polygon offset)

Для теней / decals — surfaces «прилипают» к основной геометрии. Depth bias смещает fragment z на известную величину чтобы избежать z-fighting:

```glsl
VkPipelineRasterizationStateCreateInfo rast = {
    .depthBiasEnable = VK_TRUE,
    .depthBiasConstantFactor = 0.001f,
    .depthBiasSlopeFactor = 0.05f,
    ...
};
```

Shadow mapping особенно требует bias для корректных теней.

### Early-Z requirements

Hardware может делать depth test **до** fragment shader если:
- Shader не пишет `gl_FragDepth`.
- Shader не использует `discard`.
- Нет side-effects (atomic writes, SSBO stores).

Все эти conditions программист контролирует. Filament avoids discard в favor of alpha-to-coverage или separate transparent pass.

### Depth pre-pass trick

Для complex shaders с expensive fragment cost: сначала render только depth (без fragment shader вообще — `VkPipeline` с fragment shader = NULL), получая full z-buffer. Потом главный pass с real shaders — early-Z скроет почти все occluded fragments.

Cost: 2 vertex passes вместо 1. Gain: ~30-50% снижение fragment shader executions в complex sцене.

---

## Уровень 1 — для начинающих

Представьте, что вы рисуете картину и хотите нарисовать забор перед домом. Чтобы забор закрывал часть дома, надо знать, что перед чем. Без знания вы случайно можете нарисовать дом поверх забора, и забор исчезнет.

Z-buffer — это таблица, где на каждый пиксель экрана записано «насколько далеко ближайший нарисованный объект». Когда новый объект хочет нарисоваться на том же пикселе, GPU сравнивает: ближе — рисует, дальше — отбрасывает.

В 2026 мобильные разработчики используют «reverse-Z» — трюк, который распределяет точность z-буфера равномернее для всех расстояний. Без него далёкие объекты мерцают.

---

## Уровень 2 — для студента

### Создание depth attachment в Vulkan

```cpp
VkImageCreateInfo depthImage = {
    .format = VK_FORMAT_D32_SFLOAT,
    .extent = { width, height, 1 },
    .usage = VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT |
             VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT,  // memoryless на TBR
    ...
};

VkAttachmentDescription depthAttachment = {
    .format = VK_FORMAT_D32_SFLOAT,
    .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
    .storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,  // не нужен после
    ...
};

VkClearValue depthClear = { .depthStencil = { .depth = 0.0f } };  // reverse-Z
```

### Depth test в pipeline

```cpp
VkPipelineDepthStencilStateCreateInfo depthStencil = {
    .depthTestEnable = VK_TRUE,
    .depthWriteEnable = VK_TRUE,
    .depthCompareOp = VK_COMPARE_OP_GREATER_OR_EQUAL,  // reverse-Z
    .depthBoundsTestEnable = VK_FALSE,
    .stencilTestEnable = VK_FALSE,
};
```

### Debug visualization

```glsl
// Fragment shader — визуализировать depth
out vec4 fragColor;

void main() {
    float depth = gl_FragCoord.z;  // already in NDC
    fragColor = vec4(vec3(depth), 1.0);
}
```

---

## Уровень 3 — для профессионала

### Infinite far reverse-Z

Объединяя [[projections-perspective-orthographic#Infinite far plane]] и reverse-Z:

```
| f/aspect  0  0   0     |
| 0         f  0   0     |
| 0         0  0   near  |
| 0         0 -1   0     |
```

Один параметр — near. Precision определяется только им. Outdoor сцены без artificial far cutoff.

### Hierarchical Z (Hi-Z)

Hardware maintains multi-level depth buffer — coarse (per tile) + fine (per pixel). Helps early-Z at tile granularity:
- Если self-shadow ray попадает в tile, где max depth < current, весь tile can be skipped.
- Adreno и Mali implement Hi-Z transparently.

Программист не контролирует напрямую, но может maximize utility через:
- Clearing depth в начале each frame (known max depth).
- Opaque front-to-back sorting (early-Z кладёт ближайшие первыми).

### Z-clip vs z-clamp

Vulkan `VK_EXT_depth_clip_enable`:
- `VK_TRUE` (default): fragments вне [0, 1] z-range clipped (отсечены).
- `VK_FALSE`: fragments outside clamped (заажаты до 0 или 1).

Depth clamp useful для skyboxes (draw на `z = far_plane`, no need to clip).

### Depth buffer на TBR/TBDR

Depth buffer на tile-based GPUs — особая история. Вместо хранения всего depth buffer в DRAM, хранится **только per-tile section** в on-chip SRAM. Это:
- Во-первых, экономит bandwidth (депт read/write не gehen to DRAM).
- Во-вторых, позволяет `VK_ATTACHMENT_STORE_OP_DONT_CARE` — depth dropped после tile render.
- В-третьих, комбинируя с `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` — attachment **никогда** не аллоцируется DRAM.

На Adreno 730: 1920×1080×4 depth buffer (8 MB) — memoryless attachment экономит именно 8 MB device memory. Per-frame — не DRAM writes, не DRAM reads.

Depth для shadow mapping — другая история. Shadow map **должен** быть сохранён в DRAM (используется в main pass как texture). Memoryless не применим.

### Depth prepass на mobile — когда оправдан

Depth pre-pass: render только depth (null fragment shader), потом main render pass с expensive shaders. Raison d'etre — early-Z culling main pass.

На IMR: typically помогает. Overhead vertex transform compensated by fragment savings.

На TBR (Mali, Adreno): **обычно contraindicated**. TBR binning уже делает per-tile primitive list; HSR (PowerVR) делает per-pixel occlusion free. Depth pre-pass добавляет второй vertex pass без существенного benefit.

Исключения для TBR:
- Fragment shader очень expensive (20+ texture samples).
- Много overdraw (5x+).
- Нет HSR (т.е. не PowerVR/Apple).

Filament по умолчанию отключает depth pre-pass на mobile. Unreal Mobile — тоже.

### Hardware depth compression

Все mobile GPUs применяют lossless depth compression — typically 4× для plane-ish regions (pixels с coherent depth). Транспарентно для программиста. Adreno — UBWC (Universal Bandwidth Compression), Mali — AFBC (через framebuffer, не pure depth).

Implications:
- Если scene имеет много sharp depth discontinuities (deep foliage), compression ratio падает до 1.5×.
- Bandwidth budget для depth не fixed — depends on content.

### Double-buffered depth / depth resolve

MSAA × depth — интересный case. Каждый subpixel имеет свой depth. В конце render pass для MSAA — **depth resolve**: avg или nearest sample выбирается как per-pixel depth.

На mobile TBR depth MSAA — практически бесплатно (все samples в tile memory). На IMR — 4× depth bandwidth.

### Shadow map depth issues

Shadow map — это просто depth buffer rendered from light. Precision requirements ещё выше (artifacts as shadow acne). Typical fixes:
- Bias (polygon offset) — 0.005–0.05 depending on scene scale.
- PCF (Percentage Closer Filtering) — blur shadow with multiple samples.
- Variance shadow maps — store depth² дополнительно для smooth.

---

## Реальные кейсы

### Кейс 1: Planner 5D — reverse-Z для interior scenes

Hallways в большом плане могут быть до 50 метров. Standard Z → z-fighting на дальних стенах. Reverse-Z + D32_SFLOAT → precision около 22 бита по всей сцене. No z-fighting, меньше tweaking needed per scene.

### Кейс 2: Sweet Home 3D — depth-pre-pass для complex scenes

Большая scene с furniture → overdraw 3-4x. Depth pre-pass + main pass даёт ~40% снижение fragment shader executions. Net saving ~25% frame time.

### Кейс 3: Filament — forward shading без discard

Filament fragment shaders avoid discard через использование alpha-to-coverage (MSAA) или separate transparent render queue. Early-Z всегда enabled для opaque passes.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Bigger depth buffer = better | Лучше reverse-Z с D32_SFLOAT чем plain D24. Precision distribution важнее bits |
| Z-buffer всегда нужен | Для pure 2D (UI) можно выключить; для 3D — ДА |
| `discard` — бесплатен | Убивает early-Z, удваивает shader cost на occluded pixels |
| Reverse-Z требует новое hardware | Работает на любом OpenGL ES 3.0+ и Vulkan GPU |

---

## Stencil buffer и его применения

Stencil — 8-bit буфер, обычно packed с depth. Configurable per-fragment operations:
- **Reference value** (to compare).
- **Compare mask** (bits to consider).
- **Write mask** (bits to write).
- **Fail action, depth fail action, pass action**: KEEP, ZERO, REPLACE, INCREMENT, DECREMENT, INVERT.

Классические use cases:

**UI masking:** Render UI только inside определённой region. First pass: render mask shape в stencil (INCREMENT). Second pass: main UI, stencil test = `STENCIL_FUNC_EQUAL` к mask value.

**Portal effects:** Сложный visual where через «портал» показывается другой мир. Stencil маркирует portal pixels, second render pass рисует мир через them.

**Shadow volumes (legacy):** Carmack's reverse technique. Pre-shader era, up to Doom 3 (2004). Сегодня заменены shadow maps.

**Deferred decals:** Project decals on geometry используя stencil для masking non-receiver surfaces.

На mobile stencil тест обычно free если depth attachment с stencil (D24S8, D32S8) — ROP processes both together. Пример pipeline config:

```cpp
VkStencilOpState stencilOp = {
    .failOp = VK_STENCIL_OP_KEEP,
    .passOp = VK_STENCIL_OP_REPLACE,
    .depthFailOp = VK_STENCIL_OP_KEEP,
    .compareOp = VK_COMPARE_OP_ALWAYS,
    .compareMask = 0xFF,
    .writeMask = 0xFF,
    .reference = 1,
};

VkPipelineDepthStencilStateCreateInfo ds = {
    .stencilTestEnable = VK_TRUE,
    .front = stencilOp,
    .back = stencilOp,
    ...
};
```

## Polygon offset — детально

Когда две surfaces copy depth (например, decal на wall), даже identical geometry может давать z-fighting из-за rasterization jitter. `VkPipelineRasterizationStateCreateInfo.depthBias*`:

```
effective_bias = depthBiasConstantFactor * depthFormatScale + 
                 depthBiasSlopeFactor * max(|dz/dx|, |dz/dy|)
```

- **depthFormatScale** — resolution depth format (D24: 2⁻²⁴, D32: min resolvable difference).
- **slopeFactor** — увеличивает bias для oblique surfaces (где depth changes быстро per pixel).

Типичные values для shadow map:
- `constantFactor = 0.005` (~5-10 depth units).
- `slopeFactor = 1.5` (adjust для oblique surfaces).

Слишком мало → shadow acne (self-shadowing artifacts). Слишком много → peter-panning (тени отделены от объекта).

## Depth-based effects

### Fog

Depth value используется для exponential или linear fog:
```glsl
float depth = gl_FragCoord.z;
float linearDepth = near / (far - depth * (far - near));
float fogFactor = exp(-fogDensity * linearDepth);
fragColor.rgb = mix(fogColor, fragColor.rgb, fogFactor);
```

### SSAO (Screen Space Ambient Occlusion)

Sample depth values in hemisphere around fragment, compare к current depth. Если neighbours closer — occluded. На mobile: expensive, часто simplified до 4-8 samples.

### Depth-based post-processing

Depth of field (bokeh blur) — depth determines blur radius. Motion blur — per-pixel velocity computed from depth + reprojection.

На mobile — frequently simplified или skipped. Battery budget не позволяет full screen-space effects.

## Подводные камни

### Ошибка 1: Legacy Z-buffer на mobile outdoor scenes

**Как избежать:** reverse-Z + D32_SFLOAT как default для любой production-graphics app.

### Ошибка 2: Shadow acne

**Как избежать:** depth bias = 0.005-0.05 для shadow passes, PCF for smoothing.

### Ошибка 3: Забытый depth clear

**Как избежать:** `VK_ATTACHMENT_LOAD_OP_CLEAR` + clear value 0.0 (reverse-Z) в render pass.

---

## Связь с другими темами

[[projections-perspective-orthographic]] — откуда берётся z_ndc.
[[rendering-pipeline-overview]] — где в pipeline depth test.
[[tile-based-rendering-mobile]] — memoryless depth attachment.
[[shadow-mapping-on-mobile]] — применение z-buffer для shadows.
[[overdraw-and-blending-cost]] — early-Z как способ снижения overdraw cost.

---

## Источники

- **Catmull, E. (1974). A Subdivision Algorithm for Computer Display of Curved Surfaces.** PhD thesis, Univ. of Utah. Изобретение z-buffer.
- **Akenine-Möller, T. et al. (2018). Real-Time Rendering, 4th ed.** Chapter 23 (Depth Precision).
- **Reed, N. Depth Precision Visualized.** [reedbeta.com](https://www.reedbeta.com/blog/depth-precision-visualized/).
- **Hulton-Harrop, T. Reverse Z.** [tomhultonharrop.com](https://tomhultonharrop.com/posts/reverse-z/).
- **Vulkan 1.4 Spec chapter 28.** [registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#fragops-depth).

---

## Проверь себя

> [!question]- Почему standard z-buffer страдает от z-fighting на far plane?
> Perspective divide делает z_ndc ∝ 1/z_view — нелинейно. Float32 precision также нелинейна (лучше около 0). Оба перекоса складываются неблагоприятно: precision концентрируется около near, у far — минимум. Два близких объекта на большой дистанции имеют почти одинаковые z_ndc, не различимые float-precision.

> [!question]- Как reverse-Z решает precision проблему?
> Инвертирует маппинг: near → 1, far → 0. Float precision хороша около 0. Сочетание с 1/z нелинейностью даёт почти равномерную precision по всей scene. Typical: standard gives ~4 bits at far, reverse-Z gives ~22 bits.

> [!question]- Что делает early-Z и что его отключает?
> Early-Z — depth test перед fragment shader, экономит shading cost для occluded pixels. Отключается если shader пишет gl_FragDepth, использует discard, или имеет side effects. Для production performance всегда структурируйте shaders чтобы early-Z работал.

---

## Ключевые карточки

Кто изобрёл z-buffer?
?
Ed Catmull в PhD-диссертации 1974 г. в University of Utah. Изобретение лежит в основе всей аппаратной 3D-графики.

---

Какой depth format используется в production mobile в 2026?
?
D32_SFLOAT для main depth attachment (23-bit mantissa float) + reverse-Z convention. D24_UNORM_S8_UINT когда нужен stencil.

---

Что такое depth bias и зачем нужен?
?
Смещение, applied to fragment z для avoiding z-fighting. Используется для shadow mapping, decals, coplanar geometry. Настраивается через VkPipelineRasterizationStateCreateInfo.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Проекции | [[projections-perspective-orthographic]] |
| Pipeline stages | [[rendering-pipeline-overview]] |
| Shadow mapping | [[shadow-mapping-on-mobile]] |
| Overdraw | [[overdraw-and-blending-cost]] |

---

*Deep-dive модуля M2.*
