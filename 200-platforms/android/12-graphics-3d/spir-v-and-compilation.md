---
title: "SPIR-V и compilation pipeline для Android"
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
  - "[[shader-programming-fundamentals]]"
  - "[[glsl-language-deep]]"
  - "[[shader-compilation-jitter-mitigation]]"
  - "[[vulkan-pipeline-command-buffers]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[glsl-language-deep]]"
primary_sources:
  - url: "https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html"
    title: "Khronos: SPIR-V Specification"
    accessed: 2026-04-20
  - url: "https://developer.android.com/ndk/guides/graphics/shader-compilers"
    title: "Android NDK: Shader compilers"
    accessed: 2026-04-20
  - url: "https://github.com/google/shaderc"
    title: "Google shaderc library"
    accessed: 2026-04-20
reading_time: 14
difficulty: 4
---

# SPIR-V и compilation pipeline

SPIR-V (**Standard Portable Intermediate Representation - Vulkan**) — binary intermediate representation для GPU shader'ов. Стандарт Khronos с 2015 года. На Android 2026 — обязательный формат для Vulkan shaders; OpenGL ES может load GLSL напрямую или SPIR-V (через `VK_KHR_spirv_1_4`).

---

## Зачем SPIR-V

Before SPIR-V: GPU driver parsed GLSL text при каждом shader load. Slow, inconsistent parsing между vendors, exposed compiler bugs в runtime.

With SPIR-V: shader compiled offline (CI-time) в portable IR; driver загружает binary, compile в machine code в один прыжок.

**Benefits:**
- Faster shader load (no GLSL parsing на device).
- Offline validation (fewer runtime surprises).
- Multiple source languages (GLSL, HLSL, Slang, Rust GPU).
- Consistent spec across vendors.

---

## Pipeline

```
Shader Source (GLSL / HLSL / etc.)
        │
        │  Offline compile (CI):
        │  • glslc / shaderc (GLSL → SPIR-V)
        │  • DXC (HLSL → SPIR-V)
        │  • slangc (Slang → SPIR-V)
        ▼
SPIR-V binary (.spv file)
        │
        │  App bundles .spv in APK (assets/shaders/)
        ▼
App loads .spv at runtime
        │
        │  Vulkan driver compiles SPIR-V → GPU machine code
        │  (happens при vkCreateGraphicsPipelines)
        ▼
Executable GPU machine code
        │
        │  Cached в VkPipelineCache
        ▼
Runtime execution
```

---

## Tools

### shaderc / glslc

Google's shader compiler. Входит в Android NDK (`ndk/prebuilt/<host>/bin/glslc`):

```bash
glslc -fshader-stage=vertex my_shader.vert -o my_shader.vert.spv
glslc -fshader-stage=fragment my_shader.frag -o my_shader.frag.spv
```

Flags:
- `-O` — optimize.
- `-O0` — disable optimization (better debug).
- `--target-env=vulkan1.3` — target Vulkan version.
- `-Werror` — warnings as errors.

### Gradle integration

Android Studio 2024+ auto-compiles shaders из `app/src/main/shaders/` → `assets/shaders/*.spv` через built-in task.

### SPIRV-Tools

Khronos utilities:
- **`spirv-dis`** — disassemble .spv в text (читать что получилось).
- **`spirv-opt`** — optimize SPIR-V (often called by glslc с -O).
- **`spirv-val`** — validate.
- **`spirv-cross`** — reverse (SPIR-V → GLSL / HLSL / MSL).

### SPIRV-Reflect

Extract metadata from .spv (bindings, entry points, uniforms) для runtime. Automatically generate descriptor set layouts.

---

## Runtime compilation

```cpp
// Load .spv from assets
std::vector<uint8_t> code = readAsset("shaders/my_shader.vert.spv");

VkShaderModuleCreateInfo moduleInfo = {
    .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
    .codeSize = code.size(),
    .pCode = reinterpret_cast<const uint32_t*>(code.data()),
};
VkShaderModule shaderModule;
vkCreateShaderModule(device, &moduleInfo, nullptr, &shaderModule);
```

`VkPipelineShaderStageCreateInfo` references shader module. Actual compilation в machine code happens при `vkCreateGraphicsPipelines` или lazily в первом draw. Это source of **shader compilation jitter** — major production issue, см. [[shader-compilation-jitter-mitigation]].

---

## Pipeline cache

Critical для production. Save compiled pipelines (including translated machine code):

```cpp
// Создание pipeline cache с данными из previous session
VkPipelineCacheCreateInfo cacheInfo = {
    .pInitialData = savedData,
    .initialDataSize = savedSize,
};
vkCreatePipelineCache(device, &cacheInfo, nullptr, &pipelineCache);

// Используется при создании pipelines
vkCreateGraphicsPipelines(device, pipelineCache, ...);

// Сохранить после session
vkGetPipelineCacheData(device, pipelineCache, &size, data);
// Write data to disk в app data directory
```

Filament и каждый production engine сохраняет cache — instant startup на second launch.

---

## Shader permutations

Одна «PBR shader» часто имеет 2^N variants: with/without normal map, with/without shadow, with/without tessellation, etc. Каждая permutation — separate SPIR-V.

Strategies:
- **Static permutation:** compile все variants при build time. Много .spv files.
- **uber-shader:** один shader с uniform flags controlling behavior. Simpler, но warp divergence possible.
- **Specialization constants:** SPIR-V feature — compile-time constants injected при pipeline creation. Compromise.

---

## Связь

[[shader-programming-fundamentals]] — stages.
[[glsl-language-deep]] — source language.
[[vulkan-pipeline-command-buffers]] — VkPipelineCache.
[[shader-compilation-jitter-mitigation]] — production impact.

---

## Источники

- **Khronos SPIR-V Spec.** [registry.khronos.org/SPIR-V](https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html).
- **Android NDK: Shader compilers.** [developer.android.com/ndk/guides/graphics/shader-compilers](https://developer.android.com/ndk/guides/graphics/shader-compilers).
- **Google shaderc.** [github.com/google/shaderc](https://github.com/google/shaderc).

---

## Проверь себя

> [!question]- Почему SPIR-V, не GLSL прямо в Vulkan?
> Offline compilation — GLSL парsing не надо делать на device. Faster load. Consistent spec. Multiple source languages (HLSL, Slang) compile в same SPIR-V.

> [!question]- Что такое specialization constants?
> SPIR-V feature: pipeline creation injects compile-time constants в shader. Compiler specializes shader with those constants — better optimization чем uniforms. Used для feature flags, texture counts, etc.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Jitter | [[shader-compilation-jitter-mitigation]] |
| Pipeline cache | [[vulkan-pipeline-command-buffers]] |
| Examples | [[vertex-and-fragment-shaders-by-example]] |

---

*Deep-dive модуля M5.*
