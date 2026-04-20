---
title: "Vulkan Pipeline, Command Buffers и Descriptor Sets"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/vulkan
  - type/deep-dive
  - level/advanced
related:
  - "[[vulkan-on-android-fundamentals]]"
  - "[[rendering-pipeline-overview]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[vulkan-synchronization-memory]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vulkan-on-android-fundamentals]]"
primary_sources:
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap9.html#pipelines"
    title: "Vulkan 1.4: Pipelines"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap5.html#commandbuffers"
    title: "Vulkan 1.4: Command Buffers"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap14.html#descriptorsets"
    title: "Vulkan 1.4: Descriptor Sets"
    accessed: 2026-04-20
reading_time: 22
difficulty: 7
---

# Vulkan Pipeline, Command Buffers, Descriptor Sets

Три фундаментальные абстракции Vulkan: **pipeline state object** (всё о том, как рисовать), **command buffer** (что делать), **descriptor set** (с чем работать). Понимание их взаимодействия — ключ к правильной architecture Vulkan-приложения.

---

## Pipeline

Pipeline — immutable snapshot всего rendering state. В Vulkan ~~нет ~~ global state; всё живёт в pipeline.

### Graphics pipeline содержит

- Shader stages (vertex, fragment, опционально tessellation/geometry).
- Vertex input description (layout, bindings).
- Input assembly (primitive topology).
- Viewport, scissor.
- Rasterization state (culling, fill mode, depth bias).
- Multisampling.
- Depth/stencil state.
- Color blend state.
- Dynamic state (какие параметры меняются per-draw без pipeline recreation).
- Pipeline layout (descriptor set layouts + push constants).
- Render pass compatibility.

Создание дорого (особенно shader compilation). Cache через `VkPipelineCache`.

### Pipeline cache

```cpp
VkPipelineCacheCreateInfo cacheInfo = {
    .pInitialData = savedCacheData,  // from previous session
    .initialDataSize = size,
};
vkCreatePipelineCache(device, &cacheInfo, nullptr, &pipelineCache);

// При создании каждого pipeline:
vkCreateGraphicsPipelines(device, pipelineCache, 1, &info, nullptr, &pipeline);

// Сохранить после session:
vkGetPipelineCacheData(device, pipelineCache, &size, data);
// store data to disk
```

Filament и другие engines сохраняют cache на disk → мгновенная загрузка на следующие запуски.

### Dynamic rendering (Vulkan 1.3+)

VPA-16 требует `VK_KHR_dynamic_rendering`. Упрощает creation без explicit render pass:

```cpp
VkRenderingInfo renderingInfo = {
    .renderArea = { {0,0}, {width, height} },
    .layerCount = 1,
    .colorAttachmentCount = 1,
    .pColorAttachments = &colorAttachment,
    .pDepthAttachment = &depthAttachment,
};
vkCmdBeginRendering(cmd, &renderingInfo);
// draw
vkCmdEndRendering(cmd);
```

Но для mobile **классический `VkRenderPass` с subpass dependencies обычно лучше** — даёт hardware лучшие hints для TBR tile optimizations.

---

## Command Buffers

Command buffer — pre-recorded sequence of commands.

### Lifecycle

1. **Allocate** из pool.
2. **Begin recording** (`vkBeginCommandBuffer`).
3. **Record** commands (`vkCmdDraw`, `vkCmdCopyBuffer`, `vkCmdBindPipeline`, ...).
4. **End recording**.
5. **Submit** to queue (`vkQueueSubmit`).
6. **Wait** done via fence, либо **re-submit**.
7. **Reset** для reuse (или release).

### Primary vs Secondary

- **Primary** — directly submittable.
- **Secondary** — executable только из primary через `vkCmdExecuteCommands`. Полезны для multi-threaded recording.

### Pool management

CommandPool — allocator. One pool per thread (avoid sync overhead). Reset entire pool через `vkResetCommandPool` — дёшево.

Pattern: per-frame command pool, reset at beginning of frame, allocate fresh command buffers. Swapchain images обычно 2-3, поэтому нужно 2-3 pools.

### Recording в parallel

```cpp
// Thread 1 — records opaque geometry
VkCommandBuffer cmd1 = allocateCmd(threadPool1);
recordOpaqueDraws(cmd1, scene);

// Thread 2 — records transparent geometry
VkCommandBuffer cmd2 = allocateCmd(threadPool2);
recordTransparentDraws(cmd2, scene);

// Main thread — combines and submits
VkCommandBuffer cmds[] = { cmd1, cmd2 };
vkQueueSubmit(queue, 1, { .commandBufferCount = 2, .pCommandBuffers = cmds }, fence);
```

Massive win для multi-core CPUs (mobile обычно 8 cores).

---

## Descriptor Sets

Descriptor — "binding" между shader slot и resource. Shader declares:

```glsl
layout(set = 0, binding = 0) uniform sampler2D u_texture;
layout(set = 0, binding = 1) uniform UBO { mat4 mvp; } ubo;
```

App provides descriptor set матching этот layout.

### Lifecycle

1. Create `VkDescriptorSetLayout` (struct layout).
2. Create `VkDescriptorPool`.
3. Allocate `VkDescriptorSet` из pool.
4. Update (`vkUpdateDescriptorSets`) — связать actual resources.
5. Bind в command buffer (`vkCmdBindDescriptorSets`).
6. Draw — shader читает через descriptors.

### Update strategies

**Static** (rarely updated): update once at startup. Used для scene constants.

**Per-frame** (changes every frame): allocate pool per frame, update at beginning, reset at end.

**Per-draw** (changes per object): **push descriptors** (`VK_KHR_push_descriptor`) или **dynamic offsets** (UBOs with base offset).

### Push descriptors (VPA-16)

```cpp
vkCmdPushDescriptorSetKHR(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, layout, 0,
                          1, &writeDescriptor);
```

Faster than traditional descriptor sets для per-draw updates. В VPA-16 Android 16 обязательно.

### Push constants

Тiny data (up to 128 bytes обычно) embedded directly в command buffer:

```cpp
vkCmdPushConstants(cmd, layout, VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(mat4), &mvp);
```

Доступны в shader:
```glsl
layout(push_constant) uniform Push {
    mat4 mvp;
} push;
```

Ideal для per-object constants (model matrix). Faster than UBO для small data.

---

## Совместная архитектура

Рекомендуемая структура Vulkan renderer:

```cpp
// Setup (once)
createSwapchain();
createRenderPass();
createPipelineLayout();  // descriptors + push constants
createPipelines();       // pipelines for each material/state combo
loadPipelineCache();

// Per-frame
acquireSwapchainImage();
beginCommandBuffer(cmd);
  cmdBeginRenderPass(cmd, renderPass);
    for each drawable (sorted by pipeline):
      if (pipeline changed): bindPipeline();
      if (descriptor changed): bindDescriptorSets();
      pushConstants(cmd, drawable.mvp);
      cmdDraw(cmd, drawable.vertexCount);
  cmdEndRenderPass(cmd);
endCommandBuffer(cmd);
submitCommandBuffer(cmd);
presentSwapchain();
```

Ключевой trick — **sort drawables by pipeline** чтобы минимизировать state changes.

---

## Подводные камни

### Pipeline explosion

Если создавать pipeline per-material-variant, легко получить 1000+ pipelines. Compile time добавится. Pipeline cache решает.

### Descriptor pool overflow

Not enough descriptors в pool → allocation fails. Plan ahead (count peak usage).

### Command buffer validation errors

Validation layers в debug build catch common mistakes (wrong state, unbound resources, etc.). Run with layers enabled.

---

## Связь

[[vulkan-on-android-fundamentals]] — context.
[[vulkan-synchronization-memory]] — sync between CBs.
[[tile-based-rendering-mobile]] — render pass design для TBR.
[[spir-v-and-compilation]] — shader compilation flow.

---

## Источники

- **Vulkan 1.4 Spec chapters 5, 9, 14.** Command buffers, pipelines, descriptor sets.
- **Vulkan Samples (Khronos/KhronosGroup).** [github.com/KhronosGroup/Vulkan-Samples](https://github.com/KhronosGroup/Vulkan-Samples).
- **Sellers, G. (2017). Vulkan Programming Guide.**

---

## Проверь себя

> [!question]- Зачем pipeline cache?
> Shader compilation (SPIR-V → GPU machine code) медленная (100-500 ms per pipeline). Cache сохраняет compiled binaries, reuses across sessions. Exp: Filament saves cache to disk → instant startup.

> [!question]- Чем push constants быстрее UBO?
> Embedded directly в command buffer, no separate memory. Limit 128 bytes. Ideal для per-draw data (model matrix, constant indices). UBO лучше для larger / shared data.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Sync | [[vulkan-synchronization-memory]] |
| Shaders compilation | [[spir-v-and-compilation]] |
| TBR design | [[tile-based-rendering-mobile]] |

---

*Deep-dive модуля M4.*
