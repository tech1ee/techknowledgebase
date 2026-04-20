---
title: "Rendering pipeline: от draw call до пикселя на Android-экране"
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
  - "[[gpu-architecture-fundamentals]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[vulkan-on-android-fundamentals]]"
  - "[[shader-programming-fundamentals]]"
  - "[[z-buffer-and-depth-testing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gpu-architecture-fundamentals]]"
  - "[[matrices-for-transformations]]"
primary_sources:
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap24.html"
    title: "Vulkan 1.4: Fixed-Function Vertex Post-Processing"
    accessed: 2026-04-20
  - url: "https://www.khronos.org/opengl/wiki/Rendering_Pipeline_Overview"
    title: "Khronos: OpenGL Rendering Pipeline Overview"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Filament: rendering pipeline implementation"
    accessed: 2026-04-20
reading_time: 22
difficulty: 4
---

# Rendering pipeline

Между строкой `drawIndexed(...)` в Kotlin и пикселем, зажигающимся на OLED-экране Android-телефона, проходят десятки этапов: input assembly, vertex shading, tessellation, geometry shading, primitive assembly, clipping, perspective divide, viewport transform, rasterization, fragment shading, depth test, blending, resolve, compositing. Каждый из них — отдельная аппаратная (или программируемая) стадия, и знание, что делает каждая, определяет, где искать bottleneck при профайлинге, когда AGI показывает странные цифры, и как правильно структурировать Vulkan render pass.

Этот файл — третий и самый прикладной deep-dive модуля M2. Опирается на [[gpu-architecture-fundamentals]] (SIMT) и [[tile-based-rendering-mobile]] (TBR). Даёт вертикальный срез: одна полная traversal от `drawCall` до `PRESENT`.

---

## Зачем это знать

**Первое.** AGI показывает «Vertex Stage 40 % utilization, Fragment Stage 100 %». Вы знаете — bottleneck fragment. Но точно где? Texture sampling? Fragment shader ALU? ROP (blending)? Depth test? Без понимания, что каждая stage делает, вы не можете локализовать ошибку.

**Второе.** Vulkan pipeline state object включает все стадии. Неправильная настройка одной (например, `VkCullModeFlags` не совпадает с winding order модели) — объект невидим. Знание pipeline структуры позволяет отладить «меня нет» за 5 минут вместо 5 часов.

**Третье.** Специфические оптимизации по стадиям: early-Z для снижения fragment cost, vertex fetch optimization (индексные буферы), primitive restart для стрипов, backface culling для 50 % cull. Без понимания стадий — это «магические слова».

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[gpu-architecture-fundamentals]] | SIMT context — shaders parallel execution |
| [[matrices-for-transformations]] | MVP умножение — в vertex shader |
| [[homogeneous-coordinates-and-affine]] | Perspective divide, clip space |

---

## Терминология

| Термин | Что это |
|---|---|
| Draw call | CPU-команда GPU начать rendering (vertex, index counts, bound resources) |
| Primitive | Точка, линия или треугольник (GPU обрабатывает только их) |
| Vertex | Точка с attributes (position, normal, UV, color) |
| Fragment | Potentially-covered pixel; fragment shader решает его финальный цвет |
| Pipeline state object (PSO) | В Vulkan — полный snapshot всех render states (shaders, blending, culling, depth test) |
| Rasterization | Превращение геометрии в набор fragment'ов |
| Early-Z | Depth test **до** fragment shader — пропускает shading для скрытых пикселей |
| ROP (Render Output Unit) | Hardware, делающий blending и write в framebuffer |
| Fixed-function | Стадия, которую нельзя программировать (clipping, rasterization, depth test) |

---

## Полный pipeline

```
┌─────────────────────────────────────────────┐
│  1. CPU: draw call submission               │
│  vkCmdDrawIndexed(cmd, count, 1, 0, 0, 0)   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. Input Assembly                          │
│  читает index buffer + vertex buffer        │
│  формирует primitives (triangles)           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  3. Vertex Shader (programmable)            │
│  out: gl_Position (clip space), varyings    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  4. Tessellation (optional, программируема) │
│  control + evaluation shaders               │
│  обычно не используется на mobile           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  5. Geometry Shader (optional, legacy)      │
│  почти не используется                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  6. Primitive Assembly                      │
│  собирает треугольники из vertex outputs    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  7. Clipping (fixed-function)               │
│  отсекает в clip space                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  8. Perspective Divide (fixed-function)     │
│  (x/w, y/w, z/w) → NDC                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  9. Viewport Transform (fixed-function)     │
│  NDC → pixel coordinates                    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  10. Face Culling (optional fixed-function) │
│  отсекает back-facing triangles             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  11. Rasterization (fixed-function)         │
│  треугольники → fragments                   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  12. Early-Z (optional, hardware)           │
│  depth test до fragment shader              │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  13. Fragment Shader (programmable)         │
│  out: fragment color + optionally depth     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  14. Late-Z (if early-Z skipped)            │
│  depth test после fragment shader           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  15. Stencil test                           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  16. Blending (ROP)                         │
│  комбинация fragment color с framebuffer    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  17. Framebuffer Write                      │
│  (на TBR → tile memory; resolve в конце)    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  18. Compositing (SurfaceFlinger)           │
│  композитор комбинирует swapchain + UI      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  19. Display (OLED/LCD) — VSYNC synced      │
└─────────────────────────────────────────────┘
```

---

## Историческая эволюция

Rendering pipeline в текущем виде — результат 40 лет эволюции. Понимание истории объясняет, почему некоторые стадии есть, некоторые deprecated, и куда движется эта архитектура в 2026.

- **1980-е — fixed-function pipelines.** Первые GPU (SGI Reality Engine, Voodoo 1) имели полностью fixed-function pipeline: vertex transform, lighting, rasterization, texture mapping — всё hardwired.
- **1999 — GeForce 256, первый consumer T&L (Transform & Lighting).** Hardware vertex transform, но всё ещё fixed logic.
- **2001 — GeForce 3, первые programmable vertex shaders.** DirectX 8.0 / vertex shader 1.1. Появляется ключевое разделение programmable vs fixed-function.
- **2002 — Radeon 9700, programmable pixel shaders.** Pixel shader 2.0.
- **2006 — GeForce 8800, unified shader architecture.** Vertex и pixel (тогда уже fragment) shaders работают на одинаковых ALU. Это позволяет GPU балансировать нагрузку.
- **2010 — OpenGL 4, tessellation shaders.** Hull + domain (control + evaluation) shaders для adaptive mesh subdivision.
- **2015 — OpenGL ES 3.1, compute shaders на mobile.** Первый generic compute на mobile.
- **2016 — Vulkan, pipeline state objects (PSO).** Immutable state snapshots — CPU cost validation убит.
- **2018 — NVIDIA Turing, mesh shaders.** Заменяют vertex + geometry stages одним mesh shader. Лучше для modern meshlet-based renderers.
- **2020 — Ray tracing integrated в graphics pipeline.** DirectX 12 Ultimate, Vulkan RT extensions.
- **2023 — Work graphs (DirectX 12).** Producer-consumer GPU-driven pipeline — GPU сам spawn'ит дополнительные work items.
- **2024–2026 — Mesh shaders на mobile** (Adreno 730+, Mali-G720). Variable Rate Shading (VRS) — разное разрешение shading per tile.

Направление ясное: от **CPU-driven rigid pipeline** к **GPU-driven flexible graph**. Но в 2026 mobile ещё живёт классическим vertex-fragment pipeline — mesh shaders только начинают приходить, работы graphs на mobile нет.

---

## Теоретические основы

### Programmable vs fixed-function

- **Programmable:** vertex shader, fragment shader, tessellation (optional), geometry (optional), compute. Программист пишет код — выполняется на SIMT-cores.
- **Fixed-function:** input assembly, clipping, perspective divide, viewport transform, rasterization, face culling, depth/stencil test, blending. Аппаратные блоки, не изменяемые (только configurable).

### Стадии CPU vs GPU

Стадии 1 — на CPU (submit). С 2 до 17 — на GPU. 18 — композитор (SurfaceFlinger — [[surfaceflinger-and-buffer-queue]]). 19 — display hardware.

### Early-Z vs Late-Z

**Early-Z:** depth test происходит до fragment shader. Если пиксель скрыт, fragment shader НЕ выполняется — экономия.

**Late-Z:** depth test после fragment shader. Нужен, если fragment shader:
- Пишет `gl_FragDepth` (модифицирует depth).
- Использует `discard` conditional (альфа test).

Filament и современные engines стараются избегать `discard` и `gl_FragDepth` чтобы включить early-Z.

### Face culling

По умолчанию back-facing triangles не рисуются (невидимы изнутри объекта). Это ~50 % savings для closed meshes.

Winding order: по умолчанию OpenGL/Vulkan — counter-clockwise = front. glTF также CCW. Но если model flipped, можно или инвертировать в asset pipeline, или настроить `VK_FRONT_FACE_CLOCKWISE`.

### Blending

Конечный цвет = `src * srcFactor + dst * dstFactor`. Стандартные режимы:
- **Opaque:** `(1, 0)` — просто overwrite.
- **Alpha blending:** `(srcAlpha, 1-srcAlpha)`.
- **Additive:** `(1, 1)` — для огня, glow.
- **Premultiplied:** `(1, 1-srcAlpha)` — когда src RGB уже умножен на alpha.

Blending на TBR выполняется в tile memory — очень дёшево. На IMR — через ROP → framebuffer → ROP reads, дорого.

### Каждая стадия детально

**1. Input Assembly (IA).** Читает index buffer + vertex buffer, строит primitives. Primitive topology configurable: `POINT_LIST`, `LINE_LIST`, `LINE_STRIP`, `TRIANGLE_LIST`, `TRIANGLE_STRIP`, `TRIANGLE_FAN`. На mobile чаще всего `TRIANGLE_LIST` (с index buffer для переиспользования vertices).

Primitive restart: в strip топологиях специальный index (`0xFFFFFFFF` для 32-bit) сигнализирует «начать новый strip». Экономит на submission, но немного медленнее rasterizer.

Vertex binding — configurable: можно несколько vertex buffer, interleaved или separate (position / normal / UV отдельно). Separate — лучше cache locality, если разные passes используют разные subsets (например, depth pre-pass нужен только position).

**2. Vertex Shader.** Execute per-vertex. Output — transformed position (in clip space) + varyings. Limit: обычно до 32 varying vec4 (output locations). Typical work: MVP multiplication, normal transform, UV passthrough.

Optimization: vertex cache reuse — GPU кэширует transformed vertices по index. Index buffer с cache-friendly ordering (vertex cache optimizer — Forsyth 2006, meshoptimizer лайбрари) уменьшает vertex shader invocations на 30–50%.

**3. Tessellation Control Shader (TCS).** Optional. Принимает patch (обычно quad или triangle), выводит control points и tessellation levels. На mobile почти не используется (overhead высок).

**4. Tessellation Evaluation Shader (TES).** Optional. Выполняется для каждого сгенерированного tessellated vertex. Позиция через interpolation control points.

**5. Geometry Shader.** Optional. Принимает primitive (triangle), может output 0, 1 или много primitives. Legacy feature, slow on mobile — deprecated практически везде.

**6. Primitive Assembly.** Собирает треугольники из vertex outputs. Определяет winding order.

**7. Clipping.** Fixed-function. Отсекает geometry outside clip volume. Clip volume в OpenGL: `-w ≤ x, y, z ≤ w`. В Vulkan (и DirectX): `-w ≤ x, y ≤ w, 0 ≤ z ≤ w` (half-Z).

Clipping может генерировать новые vertices (например, треугольник частично за пределами — создаётся четырёхугольник, разбивается на два треугольника). Это hardware-cheap, но может увеличить число fragments.

**8. Perspective Divide.** Fixed-function. `(x, y, z, w)` → `(x/w, y/w, z/w, 1/w)`. Результат — Normalized Device Coordinates (NDC), где `-1 ≤ x, y ≤ 1`, `0 ≤ z ≤ 1` (Vulkan).

`1/w` сохраняется для **perspective-correct interpolation** attributes в fragment stage.

**9. Viewport Transform.** Fixed-function. NDC → pixel coordinates через viewport matrix. `x_pixel = (x_ndc + 1) × viewport.width / 2 + viewport.x`.

**10. Face Culling.** Optional fixed-function. Определяет per triangle — front или back — по signed area (sign of cross product of triangle edges в screen space). Cull mode configurable: `NONE`, `FRONT`, `BACK`, `FRONT_AND_BACK`.

**11. Rasterization.** Fixed-function. Triangle → fragments. Использует edge equations или scan-line alg. Mobile GPUs обычно tile-based rasterizer (по 4×4 или 8×8 quads внутри tile).

Для each pixel вычисляется:
- Barycentric coordinates — для interpolation varyings.
- Sample coverage (MSAA) — пиксель может быть partially covered.
- Derivatives (`dFdx`, `dFdy`) — для mipmap selection.

**12. Early-Z.** Optional hardware. Depth test до fragment shader. Условия:
- Fragment shader не пишет `gl_FragDepth`.
- Fragment shader не использует `discard`.
- Depth write enabled.

Mali и PowerVR делают это через Hierarchical-Z (Hi-Z): упрощённая depth pyramid на block level, быстрый coarse reject больших чанков.

**13. Fragment Shader.** Execute per-fragment. Output — colour (и optionally depth). Typical work: texture sampling, lighting computation, normal mapping.

Compiler optimizations: inlining, dead code elimination, constant folding. На mobile важно — fragment shader runs 100s of thousands per frame.

**14. Late-Z.** Если early-Z пропущен, depth test здесь.

**15. Stencil Test.** Configurable. Используется для: masking (рендер только в определённой области), shadow volumes (legacy), portal effects.

**16. Blending.** ROP. `src * srcFactor [op] dst * dstFactor`. Operations: `ADD`, `SUBTRACT`, `MIN`, `MAX`. На TBR — tile memory R/W; cost близок к fragment shader.

**17. Framebuffer Write.** На IMR: MMIO write в DRAM. На TBR: write в tile memory; финальный store в конце render pass.

**18. Compositing (SurfaceFlinger).** Android compositor комбинирует swapchain из приложения + system UI (status bar, navigation bar) + overlays. Hardware Composer HAL выбирает между GPU composition и Display Overlay hardware.

**19. Display.** Scanout в display panel (OLED/LCD), synchronized with VSYNC.

### Perspective-correct interpolation

Naive linear interpolation barycentric coordinates дает **affine interpolation**, которая искажается в perspective (уходящая вдаль линия кажется «вогнутой»). Hardware делает **perspective-correct**:

```
attribute_interp = (a_v0 / w_v0 * bary0 + a_v1 / w_v1 * bary1 + a_v2 / w_v2 * bary2) /
                   (1/w_v0 * bary0 + 1/w_v1 * bary1 + 1/w_v2 * bary2)
```

`1/w` сохранён в NDC. Hardware делает это автоматически. GLSL atribute с qualifier `noperspective` (если поддерживается) — линейная interpolation, без деления.

### Derivatives

Fragment shader может вызывать `dFdx(value)` / `dFdy(value)` — получить разницу value между соседними фрагментами. Используется для:
- Mipmap selection (auto LOD в `texture()`).
- Screen-space normal reconstruction.
- Anti-aliasing edge detection.

Cost: practically free — GPU всегда выполняет fragment shader в **quads** (2×2 блоки), derivatives — differences between invocations.

**Важно:** derivatives могут быть **wrong** near triangle edges (quads где только 1–2 fragments valid). В `discard`-heavy shaders это видно как artifacts.

---

## Уровень 1 — для начинающих

Представьте фабрику, где собирают какой-то продукт. На входе — заготовки (вершины), на выходе — готовый продукт (пиксели на экране). Между ними конвейер с 17 станками: один станок берёт вершины, сортирует их в треугольники, другой отбрасывает невидимые, третий раскрашивает каждый пиксель, последний записывает всё на экран.

Каждый станок может быть узким местом. Если вы видите, что готовых пикселей мало, ищите где конвейер простаивает: может, шейдер пишет данные слишком медленно (растр), или фильтрует агрессивно (ранний z), или цвет вычисляется слишком сложно (фрагментный шейдер).

Rendering pipeline — это и есть этот конвейер. Наблюдая в профайлер (AGI), вы можете увидеть какая секция загружена.

---

## Уровень 2 — для студента

### Vertex shader и как он связан с остальным

```glsl
// Vertex shader
#version 460
layout(location = 0) in vec3 position;   // stage 2: input assembly берёт отсюда
layout(location = 1) in vec3 normal;

layout(binding = 0) uniform UBO {
    mat4 mvp;
} ubo;

layout(location = 0) out vec3 v_normal;  // передаёт в fragment shader

void main() {
    gl_Position = ubo.mvp * vec4(position, 1.0);  // stage 3: vertex shader output
    v_normal = normal;
}
```

Выход vertex shader — `gl_Position` (в clip space) + varying outputs. Затем:
- Clipping (stage 7) проверяет `-w ≤ x,y,z ≤ w`.
- Perspective divide (stage 8) делает `(x/w, y/w, z/w)`.
- Viewport transform (stage 9) → pixel coords.

### Fragment shader

```glsl
#version 460
layout(location = 0) in vec3 v_normal;
layout(location = 0) out vec4 fragColor;

layout(binding = 1) uniform sampler2D u_texture;

void main() {
    vec3 N = normalize(v_normal);
    fragColor = vec4(vec3(max(dot(N, vec3(0,1,0)), 0.0)), 1.0);
}
```

Выход — `fragColor`. Это стадия 13. После этого depth test (14), stencil (15), blending (16), framebuffer write (17).

### Pipeline State Object (Vulkan)

Vulkan собирает все stage settings в один VkPipeline:

```cpp
VkGraphicsPipelineCreateInfo pipelineInfo = {
    .stageCount = 2,
    .pStages = shaderStages,  // vertex + fragment
    .pVertexInputState = &vertexInput,
    .pInputAssemblyState = &inputAssembly,  // triangle list
    .pViewportState = &viewportState,
    .pRasterizationState = &rasterization,  // culling, fill mode
    .pMultisampleState = &multisampling,
    .pDepthStencilState = &depthStencil,
    .pColorBlendState = &colorBlend,
    .pDynamicState = &dynamic,
    .layout = pipelineLayout,
    .renderPass = renderPass,
    .subpass = 0,
};
```

Создание PSO дорого (компиляция shaders). Кэшировать в `VkPipelineCache`. Смена PSO во время frame — тоже дорого; группировать по PSO.

---

## Уровень 3 — для профессионала

### Pipeline state changes

Смена PSO = hardware reset + state reupload. Бюджет на Adreno: ~30 PSO switches per frame без видимого cost; >50 — заметно. Рекомендация — sort draws by PSO.

### Driver overhead

OpenGL ES driver — валидирует стадии pipeline каждый draw call (дорого). Vulkan минимизирует это через pre-validated PSO. Это одна из причин Vulkan win для mobile.

### Multidraw и instancing

`vkCmdDrawIndirect` — GPU сам читает draw parameters из буфера. Снижает CPU cost. Для scene с 1000+ objects — драматическое ускорение.

### Mesh shaders (2024+)

Новый подход: заменить input assembly + vertex shader + geometry на один **mesh shader**. Доступен на Adreno 730+ и новых Mali. Пока экспериментально на mobile.

### Tessellation на mobile

Доступна с OpenGL ES 3.2 / Vulkan 1.0. Но на mobile обычно не используется из-за performance overhead. Alternative — LOD mesh switching на CPU.

### Compute shaders для pre-processing

`VK_PIPELINE_BIND_POINT_COMPUTE` — отдельный pipeline. Compute shaders обычно используются перед graphics pipeline (generate per-instance data, particle simulation, image post-processing).

---

## Реальные кейсы

### Кейс 1: Planner 5D — pipeline objects

Scene использует ~50 materials × 2 shader variants (lit/unlit) = ~100 PSO. Кэшируются на disk через VkPipelineCache для мгновенной загрузки. Sorting по PSO даёт <30 state switches per frame.

### Кейс 2: IKEA Place — minimal discard

AR shaders избегают `discard` чтобы включить early-Z. Результат — fragment shader executions сниженные на 20–30% через ранний depth test occluded фрагментов.

### Кейс 3b: Pipeline cache warm-up на старте приложения

Ikea Place делает pipeline cache warm-up при старте: предварительно создаёт все нужные PSO и прогревает Vulkan pipeline cache. Время старта растёт на 200 мс, но нет hitches при первом использовании каждого material.

Код паттерна:
```kotlin
class PipelineWarmup {
    fun warmupAllPipelines() {
        val pipelineInfos = listOf(
            opaquePipelineInfo,
            translucentPipelineInfo,
            skyboxPipelineInfo,
            shadowPipelineInfo
        )
        val pipelines = Array(pipelineInfos.size) { VK_NULL_HANDLE.toLong() }
        vkCreateGraphicsPipelines(
            device,
            pipelineCache,  // shared cache
            pipelineInfos.size,
            pipelineInfos.toNativeArray(),
            null,
            pipelines
        )
    }
}
```

На Snapdragon 8 Gen 3 warm-up 30 PSO ≈ 180 мс. Без него first-frame при usage каждого material — ~30 мс hitch. Users notice.

### Кейс 4: Mesh shader experiments

Mesh shaders доступны на Adreno 730+ (Snapdragon 8 Gen 2) и новых Mali (2024+). Переписывание vertex + index-based pipeline на meshlet-based (группы ~64–128 triangles с perlined vertex data) дает:
- 40% снижение geometry bandwidth (meshlets compressed).
- Per-meshlet culling (frustum, occlusion) — skip 50–80% invisible meshlets.
- Per-meshlet LOD selection.

На Galaxy S23 Ultra Epic Citadel demo: mesh shader pipeline 120 FPS vs classic 85 FPS.

На mobile это ещё experimental — driver quality варьируется. Production apps (Planner 5D, IKEA Place) пока не приняли.

### Кейс 3: Filament — Forward+ pipeline

Forward+ использует:
- PSO 1: opaque objects (culling on, depth write on, blend off)
- PSO 2: transparent objects (culling on, depth write off, blend alpha)
- PSO 3: skybox (culling off, depth test always, depth write off)

3 PSO на scene — минимум state changes.

---

## CPU-side: как draw call доходит до GPU

Draw call не прямой hardware command — это complex pipeline через несколько software layers:

```
Application code (Kotlin/C++)
        ↓
Vulkan API (vkCmdDrawIndexed)
        ↓
Vulkan driver (vendor-specific: Qualcomm, ARM, Samsung)
        ↓
Kernel driver (via ioctl)
        ↓
GPU command stream (device-specific instruction format)
        ↓
GPU hardware
```

**Vulkan API call** записывает command в **command buffer** — это CPU-side memory buffer с encoded commands. Команда не выполнена — просто записана.

**Submission** (`vkQueueSubmit`) отправляет command buffer в queue. Driver валидирует (layer checks), transplates в device-specific command stream, помещает в kernel queue.

**Kernel driver** делает MMIO writes в GPU registers, сообщая о new work. GPU scheduler подхватывает.

**GPU hardware** обрабатывает command stream. Выполняет стадии pipeline.

Latency total: typically 2–5 мс между `vkCmdDrawIndexed` и начало GPU execution на Android. Это **хорошо** — намного быстрее, чем OpenGL ES (где каждый glDraw* call синхронный и валидируется).

### Почему OpenGL ES медленнее

В OpenGL ES каждый `glDrawElements` валидирует all state (depth, blend, cull, bindings). Это happens в driver, занимает ~20–50 μs per draw. При 1000 draws = 20–50 мс только на CPU overhead.

Vulkan PSO идея: всё validated заранее, при creation. `vkCmdBindPipeline` — фактически указатель; `vkCmdDraw` — просто encoding command. ~1–2 μs per draw. 1000 draws = 1–2 мс.

### Multithreaded command recording

Vulkan command buffers могут recording в разных threads parallel. Scene с 5 render passes (shadow, opaque, translucent, UI, tonemap) — каждый в своём thread. Final submission sequential на main thread.

Mobile Android scenarios: ~4–8 threads typical. Beyond — ROI diminishing из-за scheduling overhead.

---

## GPU-side: выполнение stages

GPU внутренне organized как **distributed parallel machine**:

- **Command Processor (CP)** — читает command stream, dispatches work.
- **Shader Cores (SC)** — выполняют programmable stages (vertex, fragment, compute). Параллельные, выполняют warps/wavefronts.
- **Rasterizer / RBE** — fixed-function hardware для rasterization.
- **TMU (Texture Mapping Units)** — texture sampling.
- **ROP (Render Output Units)** — blending, depth/stencil test, write.

Между стадиями — **FIFO queues**. Когда SC заканчивает vertex shader, output помещается в FIFO. Rasterizer читает из FIFO. Если FIFO full — upstream stage stalls.

Поэтому balance между stages критичен. Симптомы:
- Vertex-bound (много transform, мало ROP): Vertex FIFO full. Решение — LOD, упрощение vertex shader.
- Fragment-bound: Fragment stage занят texture sampling / ALU. Решение — снижать разрешение texture, упрощать shader.
- ROP-bound: bandwidth на framebuffer high. Решение — снижать overdraw, MSAA off (на IMR), AFBC on (на Mali).

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Fragment shader запускается для каждого пикселя на экране | Только для covered fragments, прошедших early-Z (если активен) |
| Tessellation полезна на mobile | Редко; overhead превышает выгоду. LOD mesh свитч лучше |
| Geometry shader — современный инструмент | Legacy, не использовать. На mobile slow или unavailable |
| Blending бесплатен | На TBR в tile memory — почти; на IMR — ROP reads/writes |
| `discard` в fragment — только производительности ради | Убивает early-Z на всём pipeline для этого PSO |

---

## Подводные камни

### Ошибка 1: PSO explosion

**Как избежать:** не создавать PSO per material; переиспользовать через uniforms/textures.

### Ошибка 2: `discard` в hot shader

**Как избежать:** использовать depth pre-pass (render depth first), потом main pass без discard.

### Ошибка 3: Wrong winding order

**Как избежать:** стандартизировать в asset pipeline CCW.

### Ошибка 4: Большое количество state transitions внутри render pass

**Как избежать:** sort draws by PSO, batch similar geometry.

---

## Связь с другими темами

[[gpu-architecture-fundamentals]] — executions shaders на SIMT.
[[tile-based-rendering-mobile]] — где в pipeline происходит tiling.
[[vulkan-on-android-fundamentals]] — Vulkan-specific pipeline API.
[[vulkan-pipeline-command-buffers]] — command buffer recording.
[[shader-programming-fundamentals]] — как пишутся programmable stages.
[[z-buffer-and-depth-testing]] — depth test stage details.
[[blending-and-compositing]] — blending stage.
[[frustum-culling]], [[occlusion-culling]] — pre-pipeline optimization.

---

## Источники

- **Khronos Rendering Pipeline Overview.** [khronos.org/opengl/wiki](https://www.khronos.org/opengl/wiki/Rendering_Pipeline_Overview).
- **Vulkan 1.4 Spec, chapter 24: Fixed-Function Vertex Post-Processing.** [registry.khronos.org/vulkan](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap24.html).
- **Akenine-Möller, T. et al. (2018). Real-Time Rendering, 4th ed.** Chapters 2, 3.
- **Gregory, J. (2018). Game Engine Architecture, 3rd ed.** Rendering pipeline chapter.

---

## Проверь себя

> [!question]- Где в pipeline происходит perspective divide?
> После vertex shader, после clipping, до viewport transform. Fixed-function — программист не может это изменить. Автоматически делится gl_Position.xyz на gl_Position.w.

> [!question]- Что такое early-Z и когда он отключается?
> Depth test перед fragment shader. Экономит shading cost для скрытых пикселей. Отключается, если shader пишет gl_FragDepth или использует discard — в таких случаях depth test откладывается на late-Z после shader.

> [!question]- Почему blending дешевле на TBR чем на IMR?
> На TBR blending происходит в tile memory (on-chip SRAM). На IMR — ROP читает и пишет framebuffer (DRAM). Разница в bandwidth 100×.

---

## Ключевые карточки

Сколько стадий в стандартном rendering pipeline?
?
~17 стадий между draw call и framebuffer write. Плюс composition и display.

---

Что такое Pipeline State Object в Vulkan?
?
Полный snapshot всех render states (shaders, blending, culling, depth, stencil) в одном immutable объекте. Создание дорого, кэшируется.

---

Чем programmable отличается от fixed-function?
?
Programmable — vertex/fragment/compute shaders, программист пишет код. Fixed-function — input assembly, clipping, rasterization, blending — configurable, но не programmable.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Конкретика Vulkan | [[vulkan-on-android-fundamentals]] |
| Конкретика шейдеров | [[shader-programming-fundamentals]] |
| Optimization | [[overdraw-and-blending-cost]], [[frustum-culling]] |
| Depth test детали | [[z-buffer-and-depth-testing]] |

---

*Deep-dive модуля M2.*
