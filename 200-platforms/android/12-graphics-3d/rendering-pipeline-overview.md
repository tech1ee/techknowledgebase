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

### Кейс 3: Filament — Forward+ pipeline

Forward+ использует:
- PSO 1: opaque objects (culling on, depth write on, blend off)
- PSO 2: transparent objects (culling on, depth write off, blend alpha)
- PSO 3: skybox (culling off, depth test always, depth write off)

3 PSO на scene — минимум state changes.

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
