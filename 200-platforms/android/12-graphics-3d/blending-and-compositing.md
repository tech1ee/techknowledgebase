---
title: "Blending и compositing: alpha, premultiplied, Porter-Duff"
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
  - "[[rendering-pipeline-overview]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[overdraw-and-blending-cost]]"
  - "[[android-canvas-drawing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://dl.acm.org/doi/10.1145/800031.808606"
    title: "Porter, T. & Duff, T. (1984). Compositing Digital Images. SIGGRAPH"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#framebuffer-blending"
    title: "Vulkan 1.4: Blending spec"
    accessed: 2026-04-20
  - url: "https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl"
    title: "Android: AGSL and blending"
    accessed: 2026-04-20
  - url: "https://developer.nvidia.com/content/transparency-or-translucency-rendering"
    title: "NVIDIA: Order-Independent Transparency techniques"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/graphics/implement-hwc"
    title: "Android: Implement Hardware Composer HAL"
    accessed: 2026-04-20
reading_time: 26
difficulty: 4
---

# Blending и compositing

Когда в [[case-ikea-place-ar|IKEA Place]] виртуальный стеклянный стол накладывается на реальную комнату, GPU выполняет **alpha blending** — комбинирует цвет виртуального объекта с цветом фона по формуле из [Porter-Duff 1984](https://dl.acm.org/doi/10.1145/800031.808606). Когда Compose рендерит UI поверх 3D-сцены, SurfaceFlinger делает **compositing** — объединение layers с помощью того же математического аппарата. Все эти операции — в ROP (Render Output Unit) на GPU или в Hardware Composer. Знание теории blending открывает правильную работу с прозрачностью, antialiasing, particle effects, UI overlay, а также позволяет отладить 90% багов с «неправильным» внешним видом transparent objects.

---

## Зачем это знать

**Первое — premultiplied vs straight alpha.** Вечный источник багов. Текстура в одной конвенции, shader ожидает другую → цвета выглядят «грязно», мутно, с dark fringes на edges mipmap'ов. Этот баг появляется в 80% проектов, где team не договорилась о pipeline конвенции.

**Второе — transparent order.** Blending non-commutative: `(A over B) over C ≠ A over (B over C)` в общем случае. Нужен correct back-to-front sort. Неправильный sort = «сквозь стул виден задний стул вместо переднего».

**Третье — cost trade-offs.** Blending на IMR GPU — **дорого** (ROP read-modify-write в DRAM, bandwidth pressure). На TBR — **почти бесплатно** (tile memory R/W). Architect'у нужно понимать, для каких mobile платформ target'ит, чтобы choosing transparency strategy.

**Четвёртое — compositing layer.** SurfaceFlinger делает composition всех window layers (app UI, notification, status bar). Неправильно настроенный alpha — icons looks weird, UI appears washed out. Compose 1.6+ по умолчанию использует premultiplied; раньше была смешанная конвенция → баги.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[rendering-pipeline-overview]] | Blending — stage 16 в pipeline |
| [[tile-based-rendering-mobile]] | Почему blending дешёвый на mobile (tile memory) |
| [[gpu-architecture-fundamentals]] | ROP hardware, где blending выполняется |

---

## Терминология

| Термин | Что |
|---|---|
| Alpha | Компонента прозрачности (0 = прозрачный, 1 = непрозрачный) |
| Straight alpha | RGB и A хранятся независимо |
| Premultiplied alpha | RGB уже умножено на A; `(0.5, 0.5, 0.5, 0.5)` = полупрозрачный grey |
| Source (src) | Fragment, рассчитанный shader'ом |
| Destination (dst) | Уже в framebuffer |
| Blend factor | Коэффициент, на который умножается src или dst |
| Blend equation | Operation: ADD, SUBTRACT, REVERSE_SUBTRACT, MIN, MAX |
| Porter-Duff | Tom Porter + Tom Duff 1984 — формализация compositing operators |
| Over operator | `src + dst · (1-srcAlpha)` — стандартный alpha blend |
| Compositor | Separate stage/hardware that combines layers (SurfaceFlinger на Android) |
| OIT (Order-Independent Transparency) | Techniques для correct transparency без sorting |
| HWC (Hardware Composer) | Android display HAL — composition без GPU |
| Dual-source blending | Blending с двумя source values (расширенная функциональность) |
| ROP (Render Output Unit) | Hardware block, выполняющий blending |
| Color write mask | Per-channel enable/disable writes (RGBA mask) |

---

## Историческая справка

- **1977 — Ed Catmull & Alvy Ray Smith (Xerox PARC).** Первое использование alpha channel в bitmap (в paint systems).
- **1981 — Bruce Wallace et al.** Hands-on implementation mattes (alpha compositing) для film work.
- **1984 — Tom Porter & Tom Duff.** «Compositing Digital Images» SIGGRAPH paper формализует 12 compositing operators (Over, In, Out, Atop, Xor, etc.). Основа всей современной CG композиции.
- **1985 — Alvy Ray Smith.** «Image compositing fundamentals» technical report — популяризирует premultiplied alpha как standard.
- **1995–2005 — fixed-function blending в OpenGL 1.x.** Ограниченный набор модов, программист выбирает из enum.
- **2006 — OpenGL 3.0, separate color/alpha blending.** Можно разные blend equations для colour и alpha channels.
- **2009 — Advanced Blend Modes.** `GL_KHR_blend_equation_advanced` — added Screen, Multiply, Overlay, как в Photoshop.
- **2011 — Dual source blending.** Two sources в blending (для advanced compositing).
- **2015 — Android API 21, Hardware Composer 2.0.** Hardware-accelerated composition на phone chips.
- **2019 — Weighted Blended OIT.** Morgan McGuire's paper — practical OIT для real-time.
- **2020+ — Ray traced transparency.** RT naturally handles order-independent transparency через secondary rays.
- **2023 — Compose 1.6 standardization.** Jetpack Compose fully commits к premultiplied alpha pipeline.

Интересный факт: Tom Porter и Tom Duff работали в Lucasfilm Computer Graphics Group (позже became Pixar). Paper написан в context film VFX, но стал foundational для **всей** computer graphics.

---

## Теоретические основы

### Blending equation

GPU-side формулы:

```
result.rgb = src.rgb · srcFactor + dst.rgb · dstFactor
result.a   = src.a · srcFactorA + dst.a · dstFactorA
```

`srcFactor`, `dstFactor` — configurable per pipeline. В Vulkan — `VkPipelineColorBlendAttachmentState`. Blend equation — configurable op: ADD (default), SUBTRACT, REVERSE_SUBTRACT, MIN, MAX.

### Full table blend factors (Vulkan)

| Factor | Formula | Use case |
|---|---|---|
| `ZERO` | 0 | Drop component |
| `ONE` | 1 | Pass through |
| `SRC_COLOR` | src.rgb | Multiplicative |
| `ONE_MINUS_SRC_COLOR` | 1 - src.rgb | Complementary |
| `DST_COLOR` | dst.rgb | Weighted by background |
| `ONE_MINUS_DST_COLOR` | 1 - dst.rgb | Darkening based on bg |
| `SRC_ALPHA` | src.a | Standard alpha blend |
| `ONE_MINUS_SRC_ALPHA` | 1 - src.a | Standard alpha blend complement |
| `DST_ALPHA` | dst.a | For double-buffer alpha effects |
| `ONE_MINUS_DST_ALPHA` | 1 - dst.a | Atop / In-out Porter-Duff |
| `CONSTANT_COLOR` | user-specified | Fade in/out effects |
| `CONSTANT_ALPHA` | user-specified | Fade transitions |
| `SRC_ALPHA_SATURATE` | min(src.a, 1-dst.a) | Legacy AA |
| `SRC1_COLOR` / `SRC1_ALPHA` | secondary shader output | Dual-source blending |

### Стандартные blending modes

**Opaque (no blend):** `(ONE, ZERO)` — просто write src, ignore dst. Для 3D меши. Can disable blending entirely (`blendEnable = VK_FALSE`) — driver может лучше optimizing.

**Straight alpha blend (over):** `(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)`. Классика. Работает с straight alpha textures.

```
result.rgb = src.rgb * src.a + dst.rgb * (1 - src.a)
result.a   = src.a + dst.a * (1 - src.a)
```

**Premultiplied alpha over:** `(ONE, ONE_MINUS_SRC_ALPHA)`. Src.rgb уже предварительно умножен на src.a, поэтому factor «ONE».

```
result.rgb = src.rgb + dst.rgb * (1 - src.a)   // src.rgb already * src.a
result.a   = src.a + dst.a * (1 - src.a)
```

**Additive:** `(ONE, ONE)`. Для огня, glow, particles, lightshafts. Делает светлее, clamped to 1.0 по default (framebuffer precision может дать HDR).

```
result.rgb = src.rgb + dst.rgb
```

Не physically correct для light (energy conservation violated), но practically pleasant для emissive effects.

**Multiplicative:** `(ZERO, SRC_COLOR)` или `(DST_COLOR, ZERO)`. Darkens — для shadow overlays, tinting.

**Screen:** `(ONE_MINUS_DST_COLOR, ONE)` — Photoshop's Screen mode. Lightens без overflow в sames как additive.

**Multiply+Screen в advanced blend:** `GL_KHR_blend_equation_advanced` — Overlay, SoftLight, HardLight, ColorDodge, ColorBurn. Photoshop layer modes в hardware. Mobile support variable.

### Straight vs premultiplied (детально)

**Straight alpha:** texture stores `(R, G, B, A)` independently.
```
Raw texel: (1.0, 0.5, 0.0, 0.5)  // orange, 50% alpha
```

Blending с straight alpha shader output:
```glsl
vec4 color = texture(tex, uv);  // straight
fragColor = color;

// Pipeline: (SRC_ALPHA, ONE_MINUS_SRC_ALPHA)
// result = (1.0, 0.5, 0.0) * 0.5 + dst.rgb * 0.5
//        = (0.5, 0.25, 0.0) + dst * 0.5
```

**Premultiplied:** texture stores RGB already multiplied by A.
```
Raw texel: (0.5, 0.25, 0.0, 0.5)  // orange RGB * 0.5 alpha
```

Shader output same. Blending:
```glsl
vec4 color = texture(tex, uv);  // premultiplied
fragColor = color;

// Pipeline: (ONE, ONE_MINUS_SRC_ALPHA)
// result = (0.5, 0.25, 0.0) + dst.rgb * 0.5
//        = (0.5, 0.25, 0.0) + dst * 0.5  (same!)
```

Результаты математически identical, но:

**Premultiplied преимущества:**

1. **Filtering correctness.** Mipmap downsampling со straight alpha даёт «dark fringes» — edges blurred to transparent, cause colour-alpha mismatch:

```
Straight: two adjacent texels (1.0, 0.0, 0.0, 1.0) и (0.0, 0.0, 0.0, 0.0)
Average: ((1.0 + 0.0)/2, (0.0 + 0.0)/2, (0.0 + 0.0)/2, (1.0 + 0.0)/2) = (0.5, 0.0, 0.0, 0.5)
После blending с alpha 0.5: result.rgb = 0.25 * 1.0 = 0.25 red — wrong!
```

```
Premultiplied: (1.0, 0.0, 0.0, 1.0) и (0.0, 0.0, 0.0, 0.0)
Average: (0.5, 0.0, 0.0, 0.5)
После blending (ONE, ONE_MINUS_SRC_ALPHA): result.rgb = 0.5 + dst * 0.5 — correct!
```

2. **Blending math simpler.** Один multiplication removed from hot path.

3. **Hardware filtering correct.** GPU filter units работают per-channel; premultiplied даёт correct results automatically.

4. **Ordered compositing asociative для premultiplied.** `A over (B over C) == (A over B) over C` в premultiplied (not true for straight).

**Straight преимущества (редкие):**

- Alpha-masking artistic control (edit alpha независимо от RGB).
- Legacy asset compatibility.
- Некоторые filtering scenarios.

**Современная практика:** premultiplied default. Filament, Jetpack Compose, Unity URP 2020+, Unreal 4.27+ — all premultiplied.

### Porter-Duff (1984) — 12 операторов

Для двух слоёв A (src) и B (dst), все возможные визуальные комбинации:

| Operator | Formula (result = αA·A + αB·B) | αA factor | αB factor | Описание |
|---|---|---|---|---|
| **Clear** | 0 | 0 | 0 | Result empty |
| **Source (A)** | A | 1 | 0 | Только A |
| **Destination (B)** | B | 0 | 1 | Только B |
| **Over (A over B)** | A + B(1-αA) | 1 | 1-αA | Стандартный alpha blend |
| **In (A in B)** | A·αB | αB | 0 | A показан только где B непрозрачен |
| **Out (A out B)** | A(1-αB) | 1-αB | 0 | A показан только где B прозрачен |
| **Atop (A atop B)** | A·αB + B(1-αA) | αB | 1-αA | A поверх B но ограничен B |
| **Xor** | A(1-αB) + B(1-αA) | 1-αB | 1-αA | A + B минус intersection |
| **Plus (additive)** | A + B | 1 | 1 | Additive blend |
| **Multiply** | A·B | B | 0 | Photoshop multiply |
| **Screen** | A + B - A·B | 1 | 1-A | Inverse multiply |
| **Dest over** | B + A(1-αB) | 1-αB | 1 | B над A |

На Android Canvas API — `PorterDuff.Mode.{SRC_OVER, SRC_IN, ... }`. На GPU (Vulkan) через blend factors. 12 Porter-Duff operators — именно комбинации configurable 8 factors.

### Расширенные blend modes

OpenGL/Vulkan extension `KHR_blend_equation_advanced` вводит non-linear Photoshop-like modes:

- **Multiply, Screen, Overlay** (combined multiply+screen based on darker/lighter).
- **Darken, Lighten** (min/max per channel).
- **Color Dodge, Color Burn** (tonal adjustments).
- **Hard Light, Soft Light** (overlay variants).
- **Difference, Exclusion** (subtractive effects).
- **Hue, Saturation, Color, Luminosity** (HSL-based blends).

Все требуют **barrier между overlapping fragments** (т.к. non-commutative — нужен определённый order). Это expensive на mobile — GPU сериализует fragments. Избегать в hot paths.

### Compositing on Android

**Three layers of compositing:**

1. **GPU blending (ROP):** внутри одного render pass/framebuffer. Fragment shader output + blending stage → write to tile memory или framebuffer.

2. **Hardware Composer (HWC):** compositing separate swapchain layers на display. Примеры: 3D scene surface + UI surface + system UI overlay + notification = 4 layers. HWC combines them directly в display pipeline, without going through GPU.

3. **SurfaceFlinger:** orchestrates HWC. Decides какие layers идут в HWC, какие в GPU fallback. При Galaxy S24 typical scenario: ~3-4 layers в HWC, 0 в GPU fallback — **most efficient path**.

### Hardware Composer detail

HWC operates on layers описанные как:

```
Layer {
    Surface (source buffer — swapchain image)
    Source crop (rectangle в source)
    Display frame (rectangle на display)
    Transform (rotation, flip)
    Blending type (opaque, coverage, pre-multiplied)
    Alpha (float global alpha)
    Z order
}
```

Mobile SoCs have hardware overlay planes (2-8 typical). Each plane может scale, rotate, blend independently. HWC tries to assign each Surface в hardware plane.

Fallback: if too many layers или unsupported transforms, SurfaceFlinger делает **GPU composition** — renders всё в single surface используя OpenGL. Это дороже (battery) но всегда работает.

Power savings от HWC vs GPU composition: ~100-200 mW. Over 24 hours display-on time — значительная экономия.

### Dual-source blending

`SRC1_COLOR`, `SRC1_ALPHA` — second shader output для blending. Используется для:

- **Glass with tint.** `src` = base, `src1` = tint factor.
- **Subpixel AA (ClearType-like).** Per-channel alpha for RGB subpixels.
- **Advanced mixing.** Two-tap blending в one pass.

GLSL:
```glsl
layout(location = 0, index = 0) out vec4 outColor;
layout(location = 0, index = 1) out vec4 outColor1;

void main() {
    outColor = baseColor;
    outColor1 = blendFactor;
}
```

Pipeline:
```cpp
VkPipelineColorBlendAttachmentState blend = {
    .srcColorBlendFactor = VK_BLEND_FACTOR_SRC1_COLOR,
    .dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC1_COLOR,
    ...
};
```

Mobile support: available on Vulkan 1.0+ с feature `dualSrcBlend`. Большинство modern mobile GPU support.

---

## Уровень 1 — для начинающих

Представьте, что у вас есть несколько рисунков на прозрачных плёнках (как раньше использовали в школе). Вы накладываете их друг на друга — через верхний плёнка виден нижний, если верхняя полупрозрачна. Если верхняя полностью прозрачна, виден только нижний. Если верхняя полностью непрозрачна, нижний не виден.

Alpha blending — то же самое, только на компьютере. Каждый пиксель имеет «прозрачность» (alpha). При рисовании нового пикселя поверх старого, компьютер смешивает цвета согласно alpha.

Есть две convention как хранить alpha + цвет:
- **Straight:** цвет и alpha хранятся независимо. Это как плёнка с нарисованным предметом и отдельной маской.
- **Premultiplied:** цвет уже «затемнён» соответственно alpha. Как плёнка сразу полу-затемнённой краской.

В современной mobile графике используется premultiplied — проще математика, правильнее filter.

---

## Уровень 2 — практика

### Transparent sorting

Transparent objects must быть рендереный **back-to-front** для correct blending. Opaque — front-to-back для early-Z (см. [[z-buffer-and-depth-testing]]).

Filament workflow:
1. Opaque render pass (all opaque objects, depth write on).
2. Transparent render pass (sorted back-to-front based on centroid distance, depth read-only).

```kotlin
val opaqueObjects = allObjects.filter { !it.hasTransparency }
val transparentObjects = allObjects.filter { it.hasTransparency }
    .sortedByDescending { it.distanceToCamera }

renderPass.begin()
opaqueObjects.forEach { it.render(opaquePipeline) }
transparentObjects.forEach { it.render(transparentPipeline) }
renderPass.end()
```

### Glass table в IKEA Place

```cpp
VkPipelineColorBlendAttachmentState glassBlend = {
    .blendEnable = VK_TRUE,
    .srcColorBlendFactor = VK_BLEND_FACTOR_ONE,             // premultiplied
    .dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA,
    .colorBlendOp = VK_BLEND_OP_ADD,
    .srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE,
    .dstAlphaBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA,
    .alphaBlendOp = VK_BLEND_OP_ADD,
    .colorWriteMask = VK_COLOR_COMPONENT_R_BIT |
                      VK_COLOR_COMPONENT_G_BIT |
                      VK_COLOR_COMPONENT_B_BIT |
                      VK_COLOR_COMPONENT_A_BIT,
};

VkPipelineDepthStencilStateCreateInfo glassDepth = {
    .depthTestEnable = VK_TRUE,   // проверять — за чем?
    .depthWriteEnable = VK_FALSE, // не писать — transparent objects
    ...
};
```

### Particle system с additive blending

```cpp
// Fire particles
VkPipelineColorBlendAttachmentState additiveBlend = {
    .blendEnable = VK_TRUE,
    .srcColorBlendFactor = VK_BLEND_FACTOR_ONE,
    .dstColorBlendFactor = VK_BLEND_FACTOR_ONE,
    .colorBlendOp = VK_BLEND_OP_ADD,
    // alpha ignored for pure additive
    ...
};
```

Overlapping particles accumulate brightness — fire глобально brighter в center.

### Debug alpha на screenshot

```glsl
// Fragment shader для debug visualization
void main() {
    vec4 albedo = texture(tex, uv);
    
    // Show alpha as separate channel
    if (debugMode == DEBUG_ALPHA) {
        fragColor = vec4(vec3(albedo.a), 1.0);
    } else {
        fragColor = albedo;
    }
}
```

Позволяет проверить, что alpha correctly encoded в source texture.

---

## Уровень 3 — для профессионала

### Order-Independent Transparency (OIT)

Correct transparency требует back-to-front sort. Для dynamic scenes (trees/foliage moving) cost заметен. OIT techniques avoid sorting:

**Weighted Blended OIT (McGuire 2013):** каждый transparent fragment пишется в два буфера:
- Accumulation: `result += premult * weight(alpha, z)`
- Revealage: `result *= (1 - alpha)`

В finalize pass combines: `result = accumulation / revealage`.

Approximation — не 100% correct, но close enough for most scenes. Free sort cost.

**Depth Peeling (Everitt 2001):** multiple render passes, each capturing next-closer layer. Expensive — N passes for N layers.

**Per-Pixel Linked Lists (Gruen/Thibieroz 2011):** store list of fragments per pixel в atomic counter + buffer. Sort per-pixel в composite pass. Correct but memory-heavy.

**Mobile practice:** weighted blended OIT — реалистичный choice. Full per-pixel lists — только для high-end desktop.

### Alpha-to-coverage (alternative to alpha blending)

MSAA primitive: alpha value → percentage of coverage samples. Alpha 0.5 → 50% samples coverage.

```cpp
VkPipelineMultisampleStateCreateInfo msaa = {
    .rasterizationSamples = VK_SAMPLE_COUNT_4_BIT,
    .alphaToCoverageEnable = VK_TRUE,
    ...
};
```

**Преимущества:**
- Order-independent (не нужен back-to-front sort).
- Depth buffer correct (depth write enabled — coverage → some samples pass).
- Sharp edges (для foliage, hair) — looks better than straight alpha.

**Недостатки:**
- Requires MSAA (budget увеличен).
- Steppy transparency (discrete levels — 0, 0.25, 0.5, 0.75, 1.0 для 4× MSAA).
- Может быть unsuitable для smooth gradients.

Filament использует alpha-to-coverage для foliage, trees. For glass/water — regular alpha blending.

### Tile-based blending на TBR

На TBR (Mali, Adreno) blending happens in **tile memory**:

1. Fragment shader produces `src` color.
2. Blending unit reads current tile pixel color (`dst`).
3. Computes blended result.
4. Writes back to tile memory.

All in SRAM, tile-local, ~1 clock cycle.

На IMR (desktop) blending requires ROP read-modify-write через L2 cache или framebuffer — тысячи раз медленнее per pixel.

**Implication:** Mobile apps can afford много transparency без bandwidth pressure. Desktop apps с heavy transparency — bandwidth-bound.

### Programmable blending (experimental)

Vulkan extension `VK_EXT_blend_operation_advanced` или custom approach через `VK_EXT_shader_framebuffer_fetch` (позволяет fragment shader читать current framebuffer value).

```glsl
#extension GL_EXT_shader_framebuffer_fetch : require
layout(inout, location = 0) vec4 fragColor;  // read existing

void main() {
    vec4 dst = fragColor;
    vec4 src = computeSrc();
    fragColor = customBlend(src, dst);  // any formula
}
```

На mobile (Mali, PowerVR) это — **zero cost** (tile memory is accessible anyway). На IMR — слishком expensive для production.

Useful для: advanced effects, custom blend modes, tone mapping per-fragment, decals.

### Overdraw impact

Blending = overdraw. Каждый transparent fragment adds cost:
- Fragment shader invocation.
- Blending op (ROP или tile).
- Potential texture samples.

Cost грубо: `N_transparent_layers × N_transparent_pixels × cost_per_fragment`.

В производственной AR scene (IKEA Place) с 5 glass-like objects partially overlapping — ~30% screen area has 2-3x transparent overdraw. Budget allocated accordingly.

### Hardware Composer limits

HWC на mobile имеет **fixed number of hardware planes** (typical 4-8). Если приложение создаёт больше layers — fallback на GPU composition.

Typical breakdown:
- Plane 1: app primary surface (3D content).
- Plane 2: Compose UI overlay.
- Plane 3: system status bar.
- Plane 4: system navigation bar.
- Plane 5: notifications shade.
- Plane 6: cursor (input method).

Modern phones (Galaxy S24) have 6-8 planes. Older — 4. Apps с custom layer stacks могут exhaust их.

Monitoring: `adb shell dumpsys SurfaceFlinger` показывает composition strategy (HWC vs GPU) for each frame.

### Dual-source blending для ClearType / subpixel AA

Text rendering с subpixel alpha (different alpha per R, G, B subpixel):

```glsl
// Fragment shader
vec3 alphaRGB = computePerSubpixelAlpha(uv);
outColor = vec4(textColor, 1.0);
outColor1 = vec4(alphaRGB, 1.0);  // per-channel blend factor
```

Pipeline:
```cpp
srcColorBlendFactor = VK_BLEND_FACTOR_SRC1_COLOR,
dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC1_COLOR,
```

Result: per-R/G/B alpha masking — sharper text. Legacy LCD display trick.

Modern OLED displays и mobile: subpixel AA не используется (OLED subpixels не aligned в RGB stripe pattern). Но technique remains для specific ports.

---

## Реальные кейсы

### Planner 5D — glass и textile rendering

Planner 5D scene может иметь glass surfaces (transparent), textile (partially transparent meshes у fabric edges), mirrors (separate handling).

- **Glass:** premultiplied alpha blend, depth write off, back-to-front sorted.
- **Textile:** alpha-to-coverage для fabric weave (smooth edges).
- **Mirrors:** separate render pass с flipped camera (reflection pass), composited on top с blend.

Result: visually convincing interior scene с moderate performance cost (~10% frame time for blending stages).

### IKEA Place — AR transparency

Virtual furniture placed in real room. Если furniture transparent (glass table), needs occlusion-aware blending:
- Depth from ARCore Depth API (см. [[arcore-depth-api]]).
- Custom blend: `if (virtual_depth < real_depth) { blend normally } else { skip }`.

Implementation через programmable blending (shader_framebuffer_fetch) или discard + alpha blend.

### Compose UI на top 3D

Compose renders UI surface separate from 3D. SurfaceFlinger composes:
- Layer 1: 3D surface (app content).
- Layer 2: Compose UI surface (premultiplied).
- HWC blends: UI `over` 3D.

Compose 1.6+ все assets premultiplied. Earlier versions had inconsistency — status bar icons sometimes looked wrong cause of mixed conventions.

### Sweet Home 3D — водяные эффекты

Water surface implemented as transparent plane + normal map distortion. Double-sided (visible from below).

Blending: premultiplied alpha over, depth test yes, write no.

Performance: на Snapdragon 7 Gen 1 — 55 FPS с водой, 60 без. ~10% cost.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Straight alpha «правильнее» premultiplied | Premultiplied mathematically superior для filtering/blending. Большинство modern engines используют it |
| Blending expensive на mobile | На TBR — почти бесплатно (tile memory). На IMR — да, expensive |
| Porter-Duff = 12 отдельных алгоритмов | Все 12 — разные комбинации одних blend factors. Hardware configurable |
| Order independence невозможна без sort | OIT techniques (weighted blended, depth peeling) дают approximate order-independence без sort |
| Alpha-to-coverage — просто alternative | Не свободен: нужен MSAA budget, discrete alpha levels |
| HWC всегда используется для compositing | Только если layers fit hardware planes. Иначе fallback на GPU composition (более expensive) |

---

## Подводные камни

### Ошибка 1: mixing straight and premultiplied в pipeline

**Как избежать:** установить один convention для всего pipeline. Document в asset standards. Premultiplied рекомендуется для new projects. Convert legacy assets with tooling (ImageMagick, premultiply script).

### Ошибка 2: depth write на transparent

**Как избежать:** для transparent — depth test yes, depth write no. Otherwise — транспарентные объекты маскируют за собой другие transparent и opaque objects incorrectly.

### Ошибка 3: Incorrect transparent sort

**Как избежать:** sort back-to-front по centroid distance каждый frame. Или использовать OIT (weighted blended) для approximate but fast correctness.

### Ошибка 4: Using `SRC_ALPHA, ONE_MINUS_SRC_ALPHA` с premultiplied texture

**Как избежать:** для premultiplied — `(ONE, ONE_MINUS_SRC_ALPHA)`. Иначе double-multiplied alpha → too dark.

### Ошибка 5: Heavy advanced blend modes on hot path

**Как избежать:** `GL_KHR_blend_equation_advanced` ops serialize fragments. Use sparingly. Classic blending в hot paths, advanced only for specific layers.

### Ошибка 6: Не учитывать HWC plane limit

**Как избежать:** ограничить количество overlays. Профилировать `dumpsys SurfaceFlinger` на target device.

---

## Связь с другими темами

[[rendering-pipeline-overview]] — blending как stage 16 (после fragment shader, depth/stencil test).
[[tile-based-rendering-mobile]] — blending cost на TBR (tile memory cheap, vs IMR DRAM expensive).
[[overdraw-and-blending-cost]] — detailed cost analysis, how transparent overdraw impacts mobile performance.
[[android-canvas-drawing]] — PorterDuff.Mode в 2D Canvas API; same math, different API.
[[z-buffer-and-depth-testing]] — depth write off for transparent objects.
[[surfaceflinger-and-buffer-queue]] — compositor layer management.
[[gpu-architecture-fundamentals]] — ROP hardware где blending выполняется.
[[shader-programming-fundamentals]] — fragment shader output связь с blending pipeline.

---

## Источники

- **Porter, T. & Duff, T. (1984). Compositing Digital Images.** SIGGRAPH. [ACM DOI](https://dl.acm.org/doi/10.1145/800031.808606). Классика — 12 compositing operators.
- **Smith, A.R. (1995). Image Compositing Fundamentals.** Microsoft Research TR. Популяризация premultiplied.
- **Vulkan 1.4 Spec, chapter 28.** [registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#framebuffer-blending).
- **Akenine-Möller et al. (2018). Real-Time Rendering, 4th ed.** Chapter 5 (Shading Basics), Chapter 20 (Transparency).
- **McGuire, M. & Bavoil, L. (2013). Weighted Blended Order-Independent Transparency.** JCGT. Key OIT paper.
- **Everitt, C. (2001). Interactive Order-Independent Transparency.** NVIDIA whitepaper. Depth peeling.
- **Android SurfaceFlinger docs.** [source.android.com/docs/core/graphics](https://source.android.com/docs/core/graphics/implement-hwc).
- **Compose Graphics Pipeline documentation.** [developer.android.com/develop/ui/compose/graphics](https://developer.android.com/develop/ui/compose/graphics/draw/modifiers).

---

## Проверь себя

> [!question]- Premultiplied или straight alpha для mobile textures?
> Premultiplied в современной практике. Filtering корректен (no dark fringes), blending проще (one multiplication меньше в hot path), associative compositing, совместимо с hardware filtering units. Compose, Filament, Unity URP, Unreal — все premultiplied. Установите single convention для всего pipeline.

> [!question]- Почему opaque рендерится front-to-back, transparent — back-to-front?
> Opaque front-to-back enables early-Z (depth test rejects hidden fragments before fragment shader). Transparent back-to-front даёт correct blending — каждый слой correctly accumulates над уже отрендеренными behind.

> [!question]- Что такое OIT и когда оправдан?
> Order-Independent Transparency — techniques (weighted blended, depth peeling, per-pixel linked lists) для correct transparency без back-to-front sort. Оправдан когда sort cost significant (dynamic scenes, many transparent objects). Weighted blended — наиболее practical на mobile, approximate но fast.

> [!question]- Почему blending дешевле на TBR чем на IMR?
> На TBR blending происходит в tile memory (on-chip SRAM). На IMR — ROP читает и пишет framebuffer (DRAM). Разница в bandwidth и energy ~100×. Mobile apps могут afford больше transparency без bandwidth pressure.

> [!question]- Что такое Hardware Composer и какие limits?
> HWC — display HAL на Android для compositing layers без GPU. Имеет fixed number hardware planes (4-8 типично). Если layers fit — efficient, no GPU composition. Если exceed — SurfaceFlinger fallback на GPU compose (more expensive, ~100-200 mW additional).

---

## Ключевые карточки

Какой Porter-Duff operator — самый используемый?
?
Over (A over B): `A + B·(1-αA)`. Стандартный alpha blend для transparent объектов поверх непрозрачных. 90%+ всех compositing scenarios.

---

Что такое premultiplied alpha?
?
Convention где RGB в текстуре уже умножен на A. Mathematical advantages: correct filtering, simpler blending math, associative compositing. Filament, Compose, modern engines all use it.

---

Какой blend factor использовать с premultiplied texture?
?
`(VK_BLEND_FACTOR_ONE, VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA)`. Для straight alpha было бы `(VK_BLEND_FACTOR_SRC_ALPHA, ...)`. Использование wrong factor даёт double-multiplied → too dark.

---

Что такое Weighted Blended OIT?
?
Morgan McGuire 2013 — approximate OIT без sort. Два буфера: accumulation и revealage. Finalize pass combines. Approximate но practical для real-time.

---

Что делает alpha-to-coverage?
?
Использует MSAA coverage для simulating transparency. Alpha 0.5 → 50% samples covered. Order-independent, depth-write compatible. Discrete steps (4× MSAA → 5 levels). Хорош для foliage, hair edges.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Overdraw cost | [[overdraw-and-blending-cost]] |
| 2D на Android | [[android-canvas-drawing]] |
| Pipeline stages | [[rendering-pipeline-overview]] |
| SurfaceFlinger | [[surfaceflinger-and-buffer-queue]] |
| Depth handling | [[z-buffer-and-depth-testing]] |

---

*Deep-dive модуля M2. Расширенный 2026-04-20.*
