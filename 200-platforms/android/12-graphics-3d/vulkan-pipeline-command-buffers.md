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
  - url: "https://github.com/KhronosGroup/Vulkan-Samples"
    title: "Khronos Vulkan Samples"
    accessed: 2026-04-20
reading_time: 30
difficulty: 7
---

# Vulkan Pipeline, Command Buffers, Descriptor Sets

Три фундаментальные абстракции Vulkan: **pipeline state object** (всё о том, как рисовать), **command buffer** (что делать), **descriptor set** (с чем работать). Понимание их взаимодействия — ключ к правильной архитектуре Vulkan-приложения. Каждая — радикальный отход от OpenGL ES модели, и каждая требует нового mental model. Этот deep-dive разбирает теорию, детали API, типичные паттерны, подводные камни, и как эти абстракции используются в real apps на Android (Filament, SceneView, custom engines уровня Planner 5D).

---

## Зачем это знать

**Первое — performance.** Правильное использование этих трёх абстракций даёт 20-40% более низкий CPU overhead vs OpenGL ES. Неправильное — всё равно slow или бажно.

**Второе — scalability.** Command buffers позволяют multi-threaded rendering — key для utilizing 8-core mobile CPUs. Без этого 3D apps bottleneck на main thread.

**Третье — architecture decisions.** Pipeline cache strategy, descriptor update patterns, command buffer reuse — всё влияет на ArchitecturalОБще app performance. Не случайные choices.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[vulkan-on-android-fundamentals]] | Core Vulkan concepts, VkInstance, VkDevice |
| [[rendering-pipeline-overview]] | Pipeline stages — что находится в VkPipeline |
| [[tile-based-rendering-mobile]] | Render pass design для TBR |

---

## Терминология

| Термин | Что |
|---|---|
| VkPipeline | Immutable state snapshot: shaders + fixed-function state + layout |
| Pipeline state object (PSO) | Vulkan term для VkPipeline |
| VkPipelineLayout | Declaration descriptor slots + push constants |
| VkPipelineCache | Opaque blob хранящий compiled shaders для reuse |
| VkCommandBuffer | Pre-recorded GPU command sequence |
| Primary command buffer | Submitable directly в queue |
| Secondary command buffer | Executed из primary, поддерживает parallel recording |
| VkCommandPool | Allocator для command buffers, один-на-thread |
| VkDescriptorSetLayout | Layout одного set: bindings types, shader stages visibility |
| VkDescriptorSet | Allocated set связывающий shader slots с actual resources |
| VkDescriptorPool | Allocator для descriptor sets |
| Push descriptors | Alternative: inline descriptor updates без persistent sets |
| Push constants | Small (128 bytes) data inlined directly в command buffer |
| Dynamic state | Subset pipeline state менящийся per-draw без pipeline recreation |
| Dynamic rendering | Vulkan 1.3+ feature: render pass inline без explicit VkRenderPass |

---

## Pipeline — anatomy

Pipeline encapsulates **всё** о том, как рисовать. В OpenGL ES эти параметры разбросаны по global state calls; в Vulkan — bundled в один immutable object.

### Graphics pipeline содержит

**Shader stages:**
- Vertex shader (mandatory).
- Fragment shader (optional — некоторые passes без, для depth-only).
- Tessellation control + evaluation (optional).
- Geometry shader (optional, deprecated на mobile).
- Mesh + task shader (extension, modern).

**Fixed-function state:**
- Vertex input: bindings (buffer slots) + attributes (layout).
- Input assembly: primitive topology (TRIANGLE_LIST, STRIP, FAN), primitive restart.
- Viewport + scissor.
- Rasterization: cull mode, front face, polygon mode, depth bias, line width.
- Multisampling: sample count, alpha-to-coverage, sample shading.
- Depth/stencil: test enable, compare op, write enable, stencil ops.
- Color blend: attachment-specific blend factors и equations.

**Dynamic state:** subset configurable per-draw без pipeline re-creation. Typical examples: viewport, scissor, line width, depth bias.

**Pipeline layout:**
- Descriptor set layouts (up to 32 sets typically).
- Push constant ranges.

**Render pass compatibility:** pipeline bound к specific render pass structure (attachments count/format/samples).

### Создание pipeline — пример

```cpp
VkGraphicsPipelineCreateInfo pipelineInfo = {
    .sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
    .stageCount = 2,
    .pStages = shaderStages,  // vertex + fragment
    .pVertexInputState = &vertexInput,
    .pInputAssemblyState = &inputAssembly,
    .pViewportState = &viewportState,
    .pRasterizationState = &rasterizer,
    .pMultisampleState = &multisampling,
    .pDepthStencilState = &depthStencil,
    .pColorBlendState = &colorBlend,
    .pDynamicState = &dynamicState,
    .layout = pipelineLayout,
    .renderPass = renderPass,
    .subpass = 0,
};

VkPipeline pipeline;
vkCreateGraphicsPipelines(device, pipelineCache, 1, &pipelineInfo, nullptr, &pipeline);
```

**Создание дорого** — shader compilation (SPIR-V → GPU machine code) может занимать 50-500 ms per pipeline на Android. Множественные pipelines → заметные stalls.

### Pipeline cache

`VkPipelineCache` — opaque blob where driver хранит compiled shader binaries. Reuse across:
- Within session — multiple pipelines with shared shaders compiled once.
- Across sessions — save/load blob на disk.

```cpp
// Load cache from disk
std::vector<char> cacheData = loadFromDisk("pipeline_cache.bin");

VkPipelineCacheCreateInfo cacheInfo = {
    .pInitialData = cacheData.data(),
    .initialDataSize = cacheData.size(),
};
vkCreatePipelineCache(device, &cacheInfo, nullptr, &pipelineCache);

// Use при создании pipelines
vkCreateGraphicsPipelines(device, pipelineCache, 1, &info, nullptr, &pipeline);

// Save после session
size_t size = 0;
vkGetPipelineCacheData(device, pipelineCache, &size, nullptr);
std::vector<char> data(size);
vkGetPipelineCacheData(device, pipelineCache, &size, data.data());
saveToDisk("pipeline_cache.bin", data);
```

На subsequent launch cache loaded → pipelines create near-instantly (driver uses cached binaries).

### Dynamic rendering (Vulkan 1.3+)

VPA-16 требует `VK_KHR_dynamic_rendering`. Упрощает rendering без explicit `VkRenderPass` object:

```cpp
VkRenderingAttachmentInfo colorAttachment = {
    .imageView = swapchainImageView,
    .imageLayout = VK_IMAGE_LAYOUT_ATTACHMENT_OPTIMAL,
    .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
    .storeOp = VK_ATTACHMENT_STORE_OP_STORE,
    .clearValue = {.color = {0.1f, 0.1f, 0.1f, 1.0f}},
};

VkRenderingInfo renderingInfo = {
    .renderArea = {{0,0}, {width, height}},
    .layerCount = 1,
    .colorAttachmentCount = 1,
    .pColorAttachments = &colorAttachment,
    .pDepthAttachment = &depthAttachment,
};

vkCmdBeginRendering(cmd, &renderingInfo);
// draw calls
vkCmdEndRendering(cmd);
```

**Trade-off для mobile TBR:** классический `VkRenderPass` с explicit subpass dependencies даёт hardware лучшие hints для tile optimizations. Dynamic rendering проще но может быть менее optimal на некоторых drivers. Profile before switching.

### Pipeline derivatives (deprecated)

Старая идея: create pipeline inheriting от parent pipeline для faster creation. В practice — almost never faster on mobile, и drivers ignore. Use pipeline cache instead.

---

## Command Buffers — теория и практика

Command buffer — GPU command stream, pre-recorded CPU-side.

### Lifecycle

```
┌─────────────┐
│  Allocate   │  из VkCommandPool
└──────┬──────┘
       ▼
┌─────────────┐
│  Begin      │  vkBeginCommandBuffer
└──────┬──────┘
       ▼
┌─────────────┐
│  Record     │  vkCmd* functions
└──────┬──────┘
       ▼
┌─────────────┐
│  End        │  vkEndCommandBuffer
└──────┬──────┘
       ▼
┌─────────────┐
│  Submit     │  vkQueueSubmit (queue to GPU)
└──────┬──────┘
       ▼
┌─────────────┐
│  Wait       │  via fence (CPU waits для GPU complete)
└──────┬──────┘
       ▼
┌─────────────┐
│  Reset      │  reset for reuse, либо release
└─────────────┘
```

### Primary vs Secondary

- **Primary** — directly submittable. Can begin/end render passes.
- **Secondary** — executed из primary через `vkCmdExecuteCommands`. Useful для multi-threaded recording.

Secondary command buffers **могут быть записаны concurrently** в разных threads, затем executed из main primary. Это — **основной способ** использовать multi-core CPU для rendering.

### Pool management

CommandPool — allocator для command buffers. Rules:
- **One pool per thread** (pools are не thread-safe).
- Reset entire pool через `vkResetCommandPool` — дёшево; resets all allocated buffers.
- Don't free individual command buffers unless необходимо.

**Pattern для mobile:**
- Per-frame command pool, reset at beginning of frame.
- Allocate fresh command buffers каждый frame (drawing commands).
- Swapchain typically 2-3 images → need 2-3 pools (for in-flight frames).

```cpp
struct Frame {
    VkCommandPool pool;
    VkCommandBuffer primaryCmd;
    VkFence inFlightFence;
    VkSemaphore imageAvailable;
    VkSemaphore renderFinished;
};

Frame frames[MAX_FRAMES_IN_FLIGHT];

// Per-frame
Frame& frame = frames[currentFrame];
vkWaitForFences(device, 1, &frame.inFlightFence, VK_TRUE, UINT64_MAX);
vkResetFences(device, 1, &frame.inFlightFence);
vkResetCommandPool(device, frame.pool, 0);
vkAllocateCommandBuffers(device, &allocInfo, &frame.primaryCmd);
// record
// submit
currentFrame = (currentFrame + 1) % MAX_FRAMES_IN_FLIGHT;
```

### Recording в parallel

Multi-threaded rendering пример:

```cpp
// Thread 1 — records opaque geometry
VkCommandBuffer cmd1 = allocateSecondaryFromPool(threadPool1);
recordOpaqueDraws(cmd1, scene.opaque);

// Thread 2 — records transparent geometry
VkCommandBuffer cmd2 = allocateSecondaryFromPool(threadPool2);
recordTransparentDraws(cmd2, scene.transparent);

// Thread 3 — records UI overlay
VkCommandBuffer cmd3 = allocateSecondaryFromPool(threadPool3);
recordUIDraws(cmd3, ui);

// Main thread — combines via primary
vkBeginCommandBuffer(primaryCmd, ...);
vkCmdBeginRenderPass(primaryCmd, ...);
VkCommandBuffer secondaries[] = {cmd1, cmd2, cmd3};
vkCmdExecuteCommands(primaryCmd, 3, secondaries);
vkCmdEndRenderPass(primaryCmd);
vkEndCommandBuffer(primaryCmd);

vkQueueSubmit(queue, 1, {.commandBufferCount = 1, .pCommandBuffers = &primaryCmd}, fence);
```

Massive win для multi-core CPU (mobile обычно 4-8 performance cores + 4 efficiency).

### Common commands

```cpp
// Render pass management
vkCmdBeginRenderPass / vkCmdEndRenderPass
vkCmdBeginRendering / vkCmdEndRendering  // Vulkan 1.3

// Binding
vkCmdBindPipeline
vkCmdBindDescriptorSets
vkCmdBindVertexBuffers
vkCmdBindIndexBuffer

// Drawing
vkCmdDraw(cmd, vertexCount, instanceCount, firstVertex, firstInstance)
vkCmdDrawIndexed(cmd, indexCount, instanceCount, firstIndex, vertexOffset, firstInstance)
vkCmdDrawIndirect / vkCmdDrawIndexedIndirect  // GPU-driven

// State dynamic
vkCmdSetViewport / vkCmdSetScissor
vkCmdPushConstants

// Resources
vkCmdCopyBuffer / vkCmdCopyImage / vkCmdBlitImage
vkCmdPipelineBarrier  // synchronization
```

---

## Descriptor Sets — binding model

Descriptor — "binding" между shader slot и resource. Shader declares:

```glsl
layout(set = 0, binding = 0) uniform sampler2D u_texture;
layout(set = 0, binding = 1) uniform UBO { mat4 mvp; } ubo;
layout(set = 1, binding = 0) buffer SSBO { float data[]; } ssbo;
```

App must provide descriptor set matching этот layout.

### Lifecycle

1. Create `VkDescriptorSetLayout` (layout description — bindings count, types, shader stages visibility).
2. Create `VkDescriptorPool` (allocator).
3. Allocate `VkDescriptorSet` из pool.
4. Update (`vkUpdateDescriptorSets`) — связать actual resources (buffers, images, samplers).
5. Bind в command buffer (`vkCmdBindDescriptorSets`).
6. Draw — shader читает через descriptors.

### Create layout

```cpp
VkDescriptorSetLayoutBinding bindings[] = {
    {
        .binding = 0,
        .descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,
        .descriptorCount = 1,
        .stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT,
    },
    {
        .binding = 1,
        .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
        .descriptorCount = 1,
        .stageFlags = VK_SHADER_STAGE_VERTEX_BIT,
    },
};

VkDescriptorSetLayoutCreateInfo layoutInfo = {
    .bindingCount = 2,
    .pBindings = bindings,
};
vkCreateDescriptorSetLayout(device, &layoutInfo, nullptr, &setLayout);
```

### Update strategies

**Static** (rarely updated): update once at startup. Used для scene-level constants, environment maps, shadow maps.

**Per-frame** (changes every frame): allocate pool per frame, update at beginning, reset at end.

**Per-draw** (changes per object): **push descriptors** (`VK_KHR_push_descriptor`) или **dynamic offsets** (shared UBO with different offsets per draw).

### Push descriptors (VPA-16)

```cpp
VkWriteDescriptorSet write = {
    .dstBinding = 0,
    .descriptorCount = 1,
    .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
    .pBufferInfo = &bufferInfo,
};

vkCmdPushDescriptorSetKHR(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, layout, 0,
                          1, &write);
```

Faster than traditional descriptor sets для per-draw updates. В VPA-16 Android 16 обязательно.

### Push constants

Tiny data (up to 128 bytes обычно) embedded directly в command buffer:

```cpp
struct PushData {
    mat4 modelMatrix;
    vec4 tint;
};
vkCmdPushConstants(cmd, layout, VK_SHADER_STAGE_VERTEX_BIT,
                   0, sizeof(PushData), &data);
```

Available в shader:
```glsl
layout(push_constant) uniform Push {
    mat4 modelMatrix;
    vec4 tint;
} push;
```

Ideal для per-object constants (model matrix, colors). Faster than UBO для small data.

### Dynamic offsets

Альтернатива для per-draw data — один UBO с multiple offset'ами:

```cpp
// Single UBO хранит data для N objects
struct PerObjectData { mat4 mvp; /* etc */ };
PerObjectData data[N];
// Upload to UBO

// Per draw:
uint32_t offset = i * sizeof(PerObjectData);  // aligned properly
vkCmdBindDescriptorSets(cmd, ..., 1, &descriptorSet, 1, &offset);
vkCmdDraw(cmd, ...);
```

Descriptor set layout declares binding as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC`. Offset plugged in при bind.

---

## Типичная архитектура renderer

```cpp
// Setup (once при startup)
createInstance();
createSurface();
createDevice();
createSwapchain();
createRenderPass();  // или dynamic rendering
createPipelineLayout();  // descriptors + push constants
loadPipelineCache();
createPipelines();  // pipelines для each material/state combo
createCommandPools();
createSyncPrimitives();

// Per-frame
Frame& frame = getFrame(currentFrame);
vkWaitForFences(device, 1, &frame.inFlightFence, VK_TRUE, UINT64_MAX);

uint32_t imageIndex;
vkAcquireNextImageKHR(device, swapchain, UINT64_MAX, frame.imageAvailable,
                      VK_NULL_HANDLE, &imageIndex);

vkResetCommandPool(device, frame.pool, 0);
vkBeginCommandBuffer(frame.cmd, &beginInfo);
vkCmdBeginRenderPass(frame.cmd, &renderPassInfo, VK_SUBPASS_CONTENTS_INLINE);

// Sort drawables by pipeline чтобы минимизировать state changes
auto drawables = sortByPipeline(scene.drawables);

VkPipeline currentPipeline = VK_NULL_HANDLE;
VkDescriptorSet currentSet = VK_NULL_HANDLE;
for (const Drawable& d : drawables) {
    if (d.pipeline != currentPipeline) {
        vkCmdBindPipeline(frame.cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, d.pipeline);
        currentPipeline = d.pipeline;
    }
    if (d.descriptorSet != currentSet) {
        vkCmdBindDescriptorSets(frame.cmd, ..., 0, 1, &d.descriptorSet, 0, nullptr);
        currentSet = d.descriptorSet;
    }
    vkCmdPushConstants(frame.cmd, layout, VK_SHADER_STAGE_VERTEX_BIT,
                       0, sizeof(mat4), &d.modelMatrix);
    vkCmdBindVertexBuffers(frame.cmd, 0, 1, &d.vertexBuffer, &offset);
    vkCmdBindIndexBuffer(frame.cmd, d.indexBuffer, 0, VK_INDEX_TYPE_UINT32);
    vkCmdDrawIndexed(frame.cmd, d.indexCount, 1, 0, 0, 0);
}

vkCmdEndRenderPass(frame.cmd);
vkEndCommandBuffer(frame.cmd);

// Submit
VkSubmitInfo submit = {
    .waitSemaphoreCount = 1,
    .pWaitSemaphores = &frame.imageAvailable,
    .pWaitDstStageMask = &waitStage,
    .commandBufferCount = 1,
    .pCommandBuffers = &frame.cmd,
    .signalSemaphoreCount = 1,
    .pSignalSemaphores = &frame.renderFinished,
};
vkQueueSubmit(queue, 1, &submit, frame.inFlightFence);

// Present
VkPresentInfoKHR presentInfo = {
    .waitSemaphoreCount = 1,
    .pWaitSemaphores = &frame.renderFinished,
    .swapchainCount = 1,
    .pSwapchains = &swapchain,
    .pImageIndices = &imageIndex,
};
vkQueuePresentKHR(queue, &presentInfo);

currentFrame = (currentFrame + 1) % MAX_FRAMES_IN_FLIGHT;
```

Ключевые tricks:
- **Sort drawables by pipeline** чтобы минимизировать state changes.
- **Push constants для per-draw** data.
- **In-flight frames** (2-3) чтобы GPU и CPU pipeline overlap.

---

## Подводные камни

### Pipeline explosion

Если создавать pipeline per-material-variant, легко получить 1000+ pipelines. Compile time добавится. Pipeline cache решает для subsequent launches, но first launch всё равно медленный.

**Solution:** ограничить material variants, use shader permutations вместо separate pipelines.

### Descriptor pool overflow

Not enough descriptors в pool → allocation fails. Plan ahead (count peak usage).

```cpp
VkDescriptorPoolSize poolSizes[] = {
    { VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1000 },
    { VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 500 },
    // ...
};
```

Overestimate slightly, pool size is cheap.

### Command buffer lifetime violations

Submitting a command buffer that's currently executing on GPU = undefined behavior. Always use fences / semaphores.

**Validation layers** catch this.

### Wrong pipeline-render pass compatibility

Pipeline must be compatible с render pass. Incompatible = hard-to-debug crashes. Compatible означает same attachments structure (counts, formats, sample counts) — не same instance.

### Forgetting to end render pass

Every `vkCmdBeginRenderPass` must be paired с `vkCmdEndRenderPass`. Otherwise validation error.

### Thread-unsafe pool access

VkCommandPool не thread-safe. Multiple threads accessing same pool = race condition.

**Solution:** per-thread pools. Или external synchronization (not recommended).

---

## Оптимизационные паттерны

### Pipeline bucketing

Sort drawables by (renderPass, pipeline, descriptorSet, pushConstants). Minimize state transitions.

### Indirect drawing

`vkCmdDrawIndirect` — GPU reads draw parameters из buffer. Enables GPU-driven culling без CPU roundtrip.

```cpp
// Compute shader writes indirect draw commands
// Graphics submitshifts from same buffer
vkCmdDrawIndirect(cmd, indirectBuffer, 0, drawCount, stride);
```

### Pipeline creation asynchronously

Don't block main thread creating pipelines. Spawn worker thread, build pipelines в background.

```cpp
std::thread([this]() {
    createAllPipelines();  // takes seconds
    pipelinesReady = true;
}).detach();
```

First-frame uses fallback (simple shader), subsequent use full pipelines.

### Command buffer pooling

Instead of allocating fresh buffers каждый frame — pool их. Reset instead of free.

---

## Реальные кейсы

### Filament command structure

Filament (Google) использует:
- Pipeline cache loaded at startup, saved on shutdown.
- Descriptor pool с big capacity.
- Primary command buffer per frame.
- Secondary command buffers for multi-threaded scene recording.
- Push constants для per-object transforms.

Result: 2-3 ms CPU submission time для complex scene (1000+ objects).

### Planner 5D custom renderer

Planner 5D's C++ engine:
- Один pipeline per material × 2 variants (lit/unlit) = ~100 pipelines.
- Saved pipeline cache → second launch practically instant.
- Sort drawables сложным 3-level sort (pipeline → descriptor set → depth).
- Per-draw push constants для model matrix.

Metrics: 55-60 FPS на Snapdragon 7 Gen 1 с 200+ objects.

### IKEA Place frame loop

AR specific pattern:
- ARCore камера updates в отдельный surface.
- AR frame → acquire camera texture + depth.
- Compute shader для depth-based occlusion mask.
- Graphics pipeline для virtual furniture с blending.
- Submit once per ARCore update (30 FPS target).

Использование secondary command buffers для parallel recording: camera processing + virtual rendering в parallel threads.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Pipeline создание быстрое если есть cache | Cache помогает только для compiled binaries; validation и setup всё равно medium cost |
| Descriptor sets всегда persistent | Push descriptors dynamic, dynamic offsets tổhrough shared UBO |
| Primary CB можно recording в multiple threads | НЕТ — primary один, secondary для parallel |
| Dynamic rendering лучше render pass | Render pass с explicit subpass dependencies — лучше для TBR optimization |
| Push constants = UBO | Push constants inline в command buffer, limit 128 bytes, faster для tiny data |

---

## Связь

[[vulkan-on-android-fundamentals]] — context.
[[vulkan-synchronization-memory]] — sync between CBs.
[[tile-based-rendering-mobile]] — render pass design для TBR.
[[spir-v-and-compilation]] — shader compilation flow.
[[shader-compilation-jitter-mitigation]] — pipeline cache strategies.
[[gpu-memory-management-mobile]] — descriptor pool memory.

---

## Источники

- **Vulkan 1.4 Spec chapters 5, 9, 14.** Command buffers, pipelines, descriptor sets.
- **Vulkan Samples (Khronos).** [github.com/KhronosGroup/Vulkan-Samples](https://github.com/KhronosGroup/Vulkan-Samples).
- **Sellers, G. (2017). Vulkan Programming Guide.** Canonical textbook.
- **Filament source.** [github.com/google/filament](https://github.com/google/filament). Real-world Vulkan использование.
- **Khronos: Efficient Use of Vulkan.** [github.com/KhronosGroup/Vulkan-Guide](https://github.com/KhronosGroup/Vulkan-Guide).

---

## Проверь себя

> [!question]- Зачем pipeline cache?
> Shader compilation (SPIR-V → GPU machine code) медленная (50-500 ms per pipeline). Cache сохраняет compiled binaries, reuses across sessions. Exp: Filament saves cache to disk → instant startup.

> [!question]- Чем push constants быстрее UBO?
> Embedded directly в command buffer, no separate memory allocation, no descriptor update. Limit 128 bytes. Ideal для per-draw data (model matrix, constant indices). UBO лучше для larger / shared data.

> [!question]- Primary vs Secondary command buffers — когда какой?
> Primary — directly submittable, can manage render pass. Secondary — для parallel recording в threads, executed from primary via vkCmdExecuteCommands. Multi-threaded rendering требует secondary.

> [!question]- Почему pool-per-thread?
> VkCommandPool не thread-safe. Multiple threads modifying one pool = race conditions. Per-thread pool solves.

---

## Ключевые карточки

Что такое Pipeline State Object?
?
Immutable snapshot всех render states (shaders + fixed function). В Vulkan replaces global state model OpenGL ES. Create once, bind много раз.

---

Какой максимальный размер push constants?
?
Guaranteed 128 bytes per Vulkan spec. Некоторые GPUs support больше, но rely на 128 для portability.

---

Зачем dynamic offsets?
?
Позволяют использовать один descriptor set с multiple UBO offsets для per-draw data. Альтернатива per-draw descriptor updates.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Sync | [[vulkan-synchronization-memory]] |
| Shaders compilation | [[spir-v-and-compilation]] |
| TBR design | [[tile-based-rendering-mobile]] |
| Shader jitter mitigation | [[shader-compilation-jitter-mitigation]] |

---

*Deep-dive модуля M4. Расширенный 2026-04-20.*
