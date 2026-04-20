---
title: "Shader programming: фундаментальные концепции"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/shaders
  - type/deep-dive
  - level/intermediate
related:
  - "[[gpu-architecture-fundamentals]]"
  - "[[rendering-pipeline-overview]]"
  - "[[glsl-language-deep]]"
  - "[[spir-v-and-compilation]]"
  - "[[vertex-and-fragment-shaders-by-example]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gpu-architecture-fundamentals]]"
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html"
    title: "Khronos: GLSL 4.60 Specification"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html"
    title: "Khronos: SPIR-V Specification"
    accessed: 2026-04-20
reading_time: 18
difficulty: 4
---

# Shader programming: фундаментальные концепции

Shader — программа, выполняющаяся на GPU как часть rendering pipeline. Между моделью в `.gltf` и пикселями на экране — как минимум два shader'а: vertex (обрабатывает каждую вершину) и fragment (каждый пиксель). Компилируются через GLSL → SPIR-V → GPU machine code; выполняются на SIMT cores warp'ами.

---

## Зачем это знать

Shader — core того, что делает GPU. Все materials, lighting, post-processing — shaders. Без понимания, как они работают, невозможно: writing custom materials, optimizing performance, debugging visual bugs.

---

## Stages

| Stage | Purpose | Input | Output |
|---|---|---|---|
| **Vertex** | Transform vertices, compute per-vertex data | Vertex attributes (pos, normal, UV) | `gl_Position` + varyings |
| **Tessellation** (optional) | Subdivide primitives | Patches | Tessellated primitives |
| **Geometry** (optional, legacy) | Modify primitives | Primitives | Primitives |
| **Fragment** | Compute pixel colors | Varyings + texture sample | Fragment color + depth |
| **Compute** (standalone) | General-purpose GPU | Input buffers | Output buffers |

Самые используемые: vertex + fragment. Компьютер shader'ы — для не-render compute (particle simulation, image processing).

---

## Языки и компиляция

### GLSL (OpenGL Shading Language)

Default language всех OpenGL ES / Vulkan shader'ов.

```glsl
#version 460
layout(location = 0) in vec3 position;
layout(location = 0) out vec4 fragColor;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * vec4(position, 1.0);
}
```

### SPIR-V

Binary intermediate representation (IR). Vulkan shaders load как SPIR-V, не GLSL text.

Compilation: GLSL → `glslc` / `shaderc` → SPIR-V.

SPIR-V pros:
- Offline compilation (no runtime GLSL compile).
- Faster load.
- Multiple source languages (GLSL, HLSL, Slang).

### HLSL, MSL, Slang

Other shader languages:
- **HLSL** (DirectX) — originally Microsoft, cross-compile to SPIR-V via DXC.
- **MSL** (Metal Shading Language) — iOS / macOS.
- **Slang** (NVIDIA research, now cross-vendor) — modern alternative.

На Android 2026 primary: GLSL → SPIR-V для Vulkan, GLSL для GL ES.

---

## Shader execution model

Каждый shader invocation:
- **Vertex shader:** один раз per vertex. Input — vertex attributes, output — clip-space position + varyings.
- **Fragment shader:** один раз per fragment (rasterization output). Input — interpolated varyings, output — color.
- **Compute shader:** один раз per work item (configurable workgroup).

All invocations parallel на SIMT cores (warps/wavefronts). Divergent branches penalized (см. [[gpu-architecture-fundamentals]]).

---

## Data flow

```
CPU side:
├─ Vertex attributes → VkBuffer (vertex buffer)
├─ Uniform data → VkBuffer (UBO)
├─ Textures → VkImage
└─ Descriptor set bindings
        │
        ▼
    vkCmdDraw(...)
        │
        ▼
GPU side:
├─ Vertex shader reads vertex attributes
├─ Outputs gl_Position + varyings
├─ Rasterizer interpolates varyings
├─ Fragment shader reads varyings + samples textures
└─ Outputs fragColor
```

### Precision qualifiers

- **`highp`** — 32-bit float.
- **`mediump`** — 16-bit float (half).
- **`lowp`** — 10-bit fixed (deprecated, treated as mediump).

Для mobile — использовать `mediump` где можно, уменьшает register pressure (см. [[gpu-architecture-fundamentals#Register pressure]]). `highp` для positions, normals в world space.

---

## Историческая справка

Shader programming прошёл через несколько revolutions с 1980-х:

- **1984 — Shade Trees (Cook).** Первая концепция shader как programmable function. Теоретическая, не real-time.
- **1989 — RenderMan Shading Language (RSL).** Pixar's shader language для offline rendering. Используется в Toy Story (1995), WALL-E (2008).
- **2001 — NVIDIA GeForce 3, programmable vertex shaders.** DirectX 8.0 Vertex Shader 1.0.
- **2002 — Pixel shaders (fragment).** Pixel Shader 1.0/2.0.
- **2004 — GLSL (OpenGL Shading Language) 1.10.** Khronos standard, C-like syntax.
- **2006 — Unified shader architecture (GeForce 8800, Radeon HD 2000).** Same hardware для vertex/pixel/geometry.
- **2007 — Geometry shaders.** OpenGL 3.2, DirectX 10.
- **2010 — Tessellation shaders.** OpenGL 4.0, DirectX 11.
- **2012 — Compute shaders в OpenGL 4.3.** GPU для general-purpose parallel compute.
- **2015 — SPIR-V announced.** Khronos intermediate representation.
- **2016 — Vulkan, SPIR-V mandatory.** Binary IR standard.
- **2018 — Mesh shaders (NVIDIA Turing).** Alternative geometry pipeline.
- **2020 — Ray tracing shaders (KHR_ray_tracing_pipeline).** 5 new shader types.
- **2023 — Work graphs (DirectX 12).** GPU-driven shader dispatch.
- **2025 — Slang language adoption.** Modern shader language, cross-API.

Shader complexity grew: 1985 Cook's paper showed ~10-line shade tree; modern AAA material can have 10,000+ lines GLSL.

---

## Уровень 1 — для начинающих

Представьте, что вы дизайнер, заказывающий 1000 одинаковых вывесок. Вместо того, чтобы рисовать каждую индивидуально, вы пишете инструкцию: «возьми шаблон, примени цвет A, добавь текст B, сохрани в location C». Типография (фабрика) выполняет эту инструкцию 1000 раз параллельно.

Shader — такая инструкция для GPU. Vertex shader — инструкция «преобразовать точку модели в экранные координаты». Fragment shader — «вычислить цвет пикселя». GPU выполняет эти инструкции тысячи-миллионы раз параллельно, на каждой вершине или пикселе.

Shaders пишутся на специальном языке (GLSL) — он проще чем обычное programming language, потому что задача узкая: математика над vectors и матрицами.

---

## Уровень 2 — для студента

Shader — просто C-подобный код с несколькими особенностями:
- Built-in types: `float`, `vec2`, `vec3`, `vec4`, `mat3`, `mat4`.
- Operations: element-wise (`+`, `-`, `*`, `/`), dot product, cross product, transforms.
- Built-in functions: `normalize`, `sin`, `cos`, `mix`, `clamp`, `smoothstep`, `texture`.
- Inputs (uniforms, attributes) и outputs.

**Vertex shader** пример:
```glsl
#version 460
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

layout(binding = 0) uniform UBO {
    mat4 model, view, projection;
} ubo;

layout(location = 0) out vec3 v_normal;
layout(location = 1) out vec3 v_worldPos;

void main() {
    vec4 worldPos = ubo.model * vec4(position, 1.0);
    gl_Position = ubo.projection * ubo.view * worldPos;
    v_normal = mat3(ubo.model) * normal;
    v_worldPos = worldPos.xyz;
}
```

**Fragment shader** пример:
```glsl
#version 460
layout(location = 0) in vec3 v_normal;
layout(location = 1) in vec3 v_worldPos;
layout(location = 0) out vec4 fragColor;

layout(binding = 1) uniform sampler2D u_albedo;
layout(binding = 2) uniform Light { vec3 dir; vec3 color; } light;

void main() {
    vec3 N = normalize(v_normal);
    vec3 L = normalize(-light.dir);
    float NdotL = max(dot(N, L), 0.0);
    vec3 albedo = texture(u_albedo, gl_FragCoord.xy / 1024.0).rgb;
    vec3 diffuse = albedo * light.color * NdotL;
    fragColor = vec4(diffuse, 1.0);
}
```

Simple diffuse lighting. Extended further → PBR (см. [[pbr-physically-based-rendering]]).

---

## Уровень 3 — для профессионала

### Shader optimization principles

1. **Reduce ALU ops.** Каждая multiply, add, exp — cycle. Simplify math где possible.
2. **Reduce texture samples.** Texture reads expensive (latency 100-400 cycles). Cache-friendly patterns (spatial locality).
3. **Avoid divergence.** `if (varying_condition) {...}` → warp divergence.
4. **Use precision qualifiers.** `mediump` halves register use.
5. **Separate color/depth writes.** Multiple render targets require bandwidth.
6. **Precompute constants.** Anything not per-vertex/per-fragment — compute CPU-side, send as uniform.

### Register pressure

Каждый shader invocation uses GPU registers. Too many registers per invocation → fewer warps in flight → lower occupancy → worse latency hiding.

На Mali-G710: 32 registers × 16-wide warp = budget. Shader с 64 register usage = only 1 warp per shader core = no latency hiding.

Profile через AGI "Occupancy" counter. Target ≥ 50%.

### Uniform buffer vs push constants vs separate uniforms

- **Uniform buffer (UBO):** GPU memory, large (up to 64KB), cache-friendly. Best для shared-between-draws data.
- **Push constants:** tiny (128 bytes), inline в command buffer, fastest. Best per-draw data.
- **Separate uniforms (GL ES legacy):** set via glUniform*. Driver manages internally. Medium performance.

### Dynamic branching

```glsl
// Bad — divergent branching
if (material.isTransparent) {
    // complex code
} else {
    // different complex code
}

// Good — mask result
result = mix(opaqueResult, transparentResult, step(0.5, material.isTransparent));
```

Branch prediction на GPU limited. Mask-based often faster than explicit branch, especially для small bodies.

### Loop unrolling

```glsl
// Loop
for (int i = 0; i < 4; i++) {
    color += samples[i];
}

// Unrolled — compiler may do auto, может не
color += samples[0] + samples[1] + samples[2] + samples[3];
```

Modern GLSL compilers usually unroll fixed-count loops. Variable loops (dependent на uniform) — не unroll, keep logic.

### Shader compilation pipeline

```
GLSL source
    │
    │ glslangValidator / glslc
    ▼
SPIR-V binary
    │
    │ (Vulkan)
    │ runtime driver compile
    ▼
GPU machine code (vendor-specific)
    │
    │ linked в VkPipeline
    ▼
Executable
```

SPIR-V — platform-independent. Runtime driver translates к vendor-specific instructions. Cache в VkPipelineCache для fast subsequent builds.

---

## Реальные кейсы

### Filament material system

Filament использует custom material language, compiles к GLSL → SPIR-V. Material specs в simple DSL:

```
material {
    parameters : [
        { type : sampler2d, name : albedo },
        { type : float3, name : baseColor },
    ],
    requires : [ uv0 ]
}
fragment {
    void material(inout MaterialInputs material) {
        prepareMaterial(material);
        material.baseColor.rgb = texture(materialParams_albedo, getUV0()).rgb * 
                                 materialParams.baseColor;
    }
}
```

Compiler generates full PBR fragment shader from material spec. Shader reuse — critical для Filament performance.

### Planner 5D custom shaders

Planner 5D uses GLSL ES 3.0 fragment shaders:
- Diffuse + specular (Blinn-Phong).
- Normal mapping.
- Shadow mapping с PCF.
- Alpha test для foliage/plants.

~50 unique shaders total, каждый ~100-300 lines. SPIR-V cached после compilation.

### AGSL inside Compose

AGSL — Android Graphics Shading Language (API 33+). Subset of GLSL, runs in Compose:

```kotlin
val shader = RuntimeShader("""
    uniform float2 iResolution;
    uniform float iTime;
    half4 main(float2 fragCoord) {
        float2 uv = fragCoord / iResolution;
        return half4(uv.x, uv.y, sin(iTime) * 0.5 + 0.5, 1.0);
    }
""")

Box(Modifier.graphicsLayer {
    renderEffect = RenderEffect.createRuntimeShaderEffect(shader, "")
        .asComposeRenderEffect()
})
```

Allows custom visual effects в Compose UI without full Vulkan pipeline.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Shader — это функция, выполняющаяся sequentially | Parallel invocations на warps, SIMT execution |
| Больше shader detail = лучше | Дороже. Mobile: balance quality и cost |
| Vertex shader дешёвый | Не всегда — complex vertex shaders bottleneck когда много vertices |
| `if` безвреден | Может вызвать warp divergence |
| Floats и ints одинаковы cost | Ints иногда slower на некоторых GPUs |

---

## Shader types в deep detail (будущие файлы)

- [[glsl-language-deep]] — syntax, types, operators.
- [[spir-v-and-compilation]] — compilation pipeline.
- [[vertex-and-fragment-shaders-by-example]] — practical examples.
- [[compute-shaders-on-mobile]] — compute для mobile.
- [[agsl-runtime-shader-compose]] — AGSL с Compose.
- [[shader-compilation-jitter-mitigation]] — production-critical issue.

---

## Связь

[[rendering-pipeline-overview]] — где shader'ы живут в pipeline.
[[gpu-architecture-fundamentals]] — как shader'ы исполняются на SIMT.
[[vulkan-pipeline-command-buffers]] — как они связаны с pipeline objects.

---

## Источники

- **Khronos GLSL 4.60 Specification.**
- **Khronos SPIR-V Specification.**
- **Rost, R. (2009). OpenGL Shading Language, 3rd ed.** Канонический учебник.

---

## Проверь себя

> [!question]- Чем vertex shader отличается от fragment shader по execution?
> Vertex — один invocation per vertex, outputs clip-space position + varyings. Fragment — один per fragment (rasterized pixel), reads interpolated varyings, outputs color. Vertex shader обычно cheaper (меньше invocations).

---

## Куда дальше

| Направление | Куда |
|---|---|
| Syntax | [[glsl-language-deep]] |
| Compilation | [[spir-v-and-compilation]] |
| Примеры | [[vertex-and-fragment-shaders-by-example]] |

---

*Deep-dive модуля M5.*
