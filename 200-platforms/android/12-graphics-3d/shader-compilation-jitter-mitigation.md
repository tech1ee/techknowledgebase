---
title: "Shader compilation jitter: как победить подтормаживания при первом запуске"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/shaders
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[spir-v-and-compilation]]"
  - "[[vulkan-pipeline-command-buffers]]"
  - "[[frame-pacing-swappy-library]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[spir-v-and-compilation]]"
primary_sources:
  - url: "https://developer.android.com/ndk/guides/graphics/shader-compilers"
    title: "Android NDK: Shader compilers"
    accessed: 2026-04-20
  - url: "https://developer.android.com/games/develop/vulkan/pre-compiled"
    title: "Android: Pre-compile Vulkan shaders"
    accessed: 2026-04-20
---

# Shader compilation jitter

Symptom: приложение при первом запуске или при переходе в новую сцену на 200-500 ms зависает. Frame times 60 ms → 400 ms → 60 ms. Cause — **shader compilation jitter**: GPU driver translates SPIR-V в machine code при первом usage; это CPU-intensive operation.

## Почему это production-critical

Shader compilation jitter — one из topmost production issues на mobile Vulkan/GL:
- **User impact:** visible pauses / hitches во время gameplay, animation, transitions.
- **Review impact:** reviewers (Google Play, App Store) detect FPS drops, may flag.
- **Perception:** 200 ms freeze при navigation subjective feels like crash.

Google I/O 2024 presentation explicitly called it out: "shader compilation hitches are the #1 cause of janky first-run experience." Every major engine (Unity, Unreal, Filament, Godot) имеет dedicated mitigation strategies.

## Историческая справка

- **2010s — OpenGL ES era.** Shader compile happens на `glLinkProgram`. Less visible (fewer shaders typically), but same issue.
- **2016 — Vulkan ships.** Explicit SPIR-V loading exposes compile timing.
- **2018 — Pipeline cache standardized.** `VkPipelineCache` provides shared compile cache.
- **2020 — "Shader jitter" publicly recognized.** Epic Games presentation on Unreal mobile ports.
- **2021 — Google Play Games Services.** Pre-delivery shader compilation via Play Store.
- **2023 — VK_EXT_pipeline_library.** Incremental pipeline creation, easier caching.
- **2024 — Android Performance Tuner.** Integrates shader cache analytics.
- **2026 — VPA-16 requires fast pipeline creation** through explicit features.

## Measurement

AGI (Android GPU Inspector) shows pipeline creation time:
- "GPU Events" track with pipeline create events.
- Frame times spike на events.
- Vulkan validation warnings if creation synchronous.

Target: <10 ms per pipeline creation. If >50 ms — mitigation needed.

---

## Проблема

Vulkan pipeline cache works так:
1. `vkCreateGraphicsPipelines()` — create pipeline.
2. If machine code не в cache, driver compiles SPIR-V → HW code. **Blocks thread** до завершения.
3. Compilation time: 50-500 ms per pipeline depending on complexity и device.

Для complex apps с 50+ pipelines первый запуск = несколько секунд freeze.

---

## Mitigations

### 1. Pipeline cache

Основной fix. Save compiled cache на disk, load на following launches:

```cpp
// Load cache on startup
std::vector<uint8_t> savedData = loadFromDisk("pipeline_cache.bin");

VkPipelineCacheCreateInfo cacheInfo = {
    .pInitialData = savedData.data(),
    .initialDataSize = savedData.size(),
};
VkPipelineCache cache;
vkCreatePipelineCache(device, &cacheInfo, nullptr, &cache);

// Use cache при создании pipelines
vkCreateGraphicsPipelines(device, cache, ...);

// Save cache на shutdown
size_t size;
vkGetPipelineCacheData(device, cache, &size, nullptr);
std::vector<uint8_t> data(size);
vkGetPipelineCacheData(device, cache, &size, data.data());
saveToDisk("pipeline_cache.bin", data);
```

Эффект: первый запуск медленный (compilation happens), subsequent — instant.

### 2. Pre-warm at startup

Compile all pipelines синхронно при startup (loading screen), before any rendering:

```kotlin
class Renderer {
    fun initialize() {
        showLoadingScreen()
        
        // Force compile all pipelines
        for (material in allMaterials) {
            createPipelineForMaterial(material)
        }
        
        hideLoadingScreen()
        startRendering()
    }
}
```

Users accept loading screen. Not acceptable is mid-game stutters.

### 3. Async compilation

Compile pipelines на background thread, use placeholder до готовности:

```cpp
// Background thread
auto future = std::async(std::launch::async, [&]() {
    return createPipelineForMaterial(material);
});

// Main thread — use простой placeholder pipeline, retry later
if (future.ready()) {
    pipeline = future.get();
}
```

Complex, но даёт smooth frame times.

### 4. Specialization constants

Reduce pipeline count via specialization constants вместо многих permutations. Меньше pipelines = меньше compile time.

### 5. Google Play Asset Delivery

Vulkan pipelines могут быть pre-compiled на build server и shipped в APK expansion files. Требует специфичный tooling. Rare в practice.

### 6. `VK_EXT_pipeline_creation_feedback`

Extension позволяет query compile time:

```cpp
VkPipelineCreationFeedback feedback;
VkPipelineCreationFeedbackCreateInfo feedbackInfo = {
    .pPipelineCreationFeedback = &feedback,
};
// ...vkCreateGraphicsPipelines чтото...
// feedback.duration = compile time ns
```

Helps identify slow pipelines для further optimization.

---

## OpenGL ES equivalent

GL ES имеет `glProgramBinary` — similar concept. Save program binary на disk, reuse. Since 2016 widely supported.

```kotlin
val program = GLES30.glCreateProgram()
// compile shaders, link
val binaryLength = IntArray(1)
GLES30.glGetProgramiv(program, GLES30.GL_PROGRAM_BINARY_LENGTH, binaryLength, 0)
val binary = ByteBuffer.allocateDirect(binaryLength[0])
val format = IntArray(1)
GLES30.glGetProgramBinary(program, binaryLength[0], null, 0, format, 0, binary)
// save binary + format[0] to disk

// Load next session
GLES30.glProgramBinary(program, savedFormat, savedBinary, savedLength)
```

---

## Thermal interaction

Shader compilation на weak phones вызывает CPU spike → thermal throttling → GPU throttled → FPS drop even после compilation complete. Mitigation — spread compilation across time.

---

## Real numbers

From Google I/O 2024 data:
- Simple vertex shader: ~10 ms compile.
- Standard fragment shader: ~50 ms.
- PBR fragment shader: ~150 ms.
- Complex uber-shader: 300-500 ms.

50 pipelines × 100 ms average = 5 seconds initial compile. Unacceptable в-game.

---

## Production pattern

```cpp
// Engine initialization
class Engine {
    void init() {
        // 1. Load pipeline cache from disk
        loadCache();
        
        // 2. Show loading screen
        showLoading();
        
        // 3. Create all pipelines (uses cache if present)
        createAllPipelines();
        
        // 4. Hide loading, start rendering
        hideLoading();
    }
    
    void shutdown() {
        // 5. Save updated cache back to disk
        saveCache();
    }
}
```

Filament does exactly this. First-launch — 3 secondов loading. Subsequent — instant.

---

## Связь

[[spir-v-and-compilation]] — compilation pipeline.
[[vulkan-pipeline-command-buffers]] — VkPipelineCache API.
[[thermal-throttling-and-adpf]] — thermal implications.
[[frame-pacing-swappy-library]] — steady frame times.

---

## Источники

- **Android NDK: Shader compilers.** [developer.android.com/ndk/guides/graphics/shader-compilers](https://developer.android.com/ndk/guides/graphics/shader-compilers).
- **Android: Pre-compile Vulkan shaders.** [developer.android.com/games/develop/vulkan/pre-compiled](https://developer.android.com/games/develop/vulkan/pre-compiled).
- **Google I/O 2024: Graphics performance.** [android-developers.googleblog.com](https://android-developers.googleblog.com/2025/03/building-excellent-games-with-better-graphics-and-performance.html).

---

## Проверь себя

> [!question]- Зачем pipeline cache на disk?
> First-launch compile может 3-5 seconds. Subsequent launches instant если cache valid. Standard production pattern для all Vulkan engines (Filament, Unity, Unreal, Godot).

> [!question]- Когда VkPipelineCache invalidated?
> GPU driver update (different vendor code). OS update. Device change. Detect через hash stored alongside data, recompile on mismatch.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Compilation flow | [[spir-v-and-compilation]] |
| VkPipelineCache API | [[vulkan-pipeline-command-buffers]] |
| Frame stability | [[frame-pacing-swappy-library]] |
| Thermal | [[thermal-throttling-and-adpf]] |

---

*Deep-dive модуля M5.*
