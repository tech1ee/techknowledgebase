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
