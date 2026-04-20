---
title: "Vulkan Synchronization и Memory Management"
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
  - "[[vulkan-pipeline-command-buffers]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vulkan-pipeline-command-buffers]]"
primary_sources:
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap7.html#synchronization"
    title: "Vulkan 1.4: Synchronization"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap11.html#memory"
    title: "Vulkan 1.4: Memory Management"
    accessed: 2026-04-20
  - url: "https://gpuopen.com/learn/vulkan-barriers-explained/"
    title: "GPUOpen: Vulkan Barriers Explained"
    accessed: 2026-04-20
---

# Vulkan Synchronization и Memory

Vulkan — explicit API, значит программист отвечает за два сложных domain: **synchronization** (execution и memory dependencies между commands) и **memory management** (allocation, typing, binding). Неправильное использование — source most Vulkan bugs. Эти две темы — самое сложное в Vulkan, и понимание их — маркер продвинутого Vulkan developer'а.

---

## Зачем это знать

**Первое — correctness.** Без правильной synchronization — race conditions, visual corruption, crashes. Symptom может appear random на разных GPUs.

**Второе — performance.** Over-synchronization кастратирует parallelism. Under-synchronization = bugs. Finding sweet spot — skill.

**Третье — mobile specifics.** Memory types на mobile other than desktop (unified memory model, lazy allocation for TBR). Правильные choices значат разница между smooth 60 FPS и frame drops.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[vulkan-pipeline-command-buffers]] | CBs между которыми sync |
| [[vulkan-on-android-fundamentals]] | Core Vulkan concepts |
| [[tile-based-rendering-mobile]] | Memoryless attachments |

---

## Терминология

| Термин | Что |
|---|---|
| Execution dependency | Порядок между stages (A перед B) |
| Memory dependency | Visibility writes A для reads B |
| Semaphore | GPU-to-GPU sync между queue submissions |
| Fence | GPU-to-CPU sync (CPU ждёт GPU done) |
| Barrier | Synchronization within command buffer |
| Timeline semaphore | Semaphore с monotonically incrementing counter |
| Image layout | Internal GPU representation image (COLOR_ATTACHMENT_OPTIMAL, SHADER_READ_ONLY_OPTIMAL, etc.) |
| Pipeline stage | Конкретная stage rendering pipeline где synchronization applies |
| Access mask | What operation (read/write, specific type) synchronization covers |
| Memory type | Category of memory (DEVICE_LOCAL, HOST_VISIBLE, etc.) |
| Heap | Pool of memory (GPU heap, system heap) |
| VMA | Vulkan Memory Allocator, AMD's recommended allocator library |
| Lazy allocation | Memory backing allocated on-demand, used для transient resources |

---

## Историческая справка

В OpenGL ES driver handled sync transparently — программист не думал. Но это stopping point performance:
- Driver needed to track dependencies conservatively.
- Over-synchronization common (driver can't know application intent).
- Multi-threaded rendering impossible без significant performance loss.

Vulkan philosophy: expose sync, let programmer decide.

Historical Vulkan sync API:
- **Vulkan 1.0 (2016):** VkPipelineBarrier, VkEvent, VkSemaphore, VkFence. Complex API с separate masks.
- **Vulkan 1.1 (2018):** Subgroup operations.
- **Vulkan 1.2 (2019):** Timeline semaphores — more flexible sync.
- **Vulkan 1.3 (2022):** `VK_KHR_synchronization2` — simplified API (unified `VkDependencyInfo`).
- **Vulkan 1.4 (2024):** Host image copy (no staging buffer).

VPA-16 (Android 16) requires synchronization2 — модернизация developer experience.

---

## Synchronization primitives

### Semaphore

GPU-to-GPU sync. Signal одной queue submission, wait в другой:

```cpp
vkQueueSubmit(queue, 1, {
    .waitSemaphoreCount = 1,
    .pWaitSemaphores = &imageAvailableSemaphore,
    .pWaitDstStageMask = &waitStage,
    .commandBufferCount = 1,
    .pCommandBuffers = &cmd,
    .signalSemaphoreCount = 1,
    .pSignalSemaphores = &renderFinishedSemaphore,
}, fence);

// Present waits renderFinished
vkQueuePresentKHR(queue, {
    .waitSemaphoreCount = 1,
    .pWaitSemaphores = &renderFinishedSemaphore,
    ...
});
```

### Fence

GPU-to-CPU sync. CPU ждёт done GPU work:

```cpp
vkWaitForFences(device, 1, &fence, VK_TRUE, UINT64_MAX);
vkResetFences(device, 1, &fence);
```

Используется для: reuse command buffer, safe recycle resources.

### Barrier

Синхронизация within command buffer. Самая важная primitive для правильного Vulkan.

```cpp
VkMemoryBarrier2 barrier = {
    .srcStageMask = VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
    .srcAccessMask = VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT,
    .dstStageMask = VK_PIPELINE_STAGE_2_FRAGMENT_SHADER_BIT,
    .dstAccessMask = VK_ACCESS_2_SHADER_READ_BIT,
};
VkDependencyInfo dep = { ..., .pMemoryBarriers = &barrier };
vkCmdPipelineBarrier2(cmd, &dep);
```

Барьер гарантирует: writes на stage A visible для reads на stage B.

### Image Layout transitions

VkImage существует в различных layouts: `UNDEFINED`, `COLOR_ATTACHMENT_OPTIMAL`, `SHADER_READ_ONLY_OPTIMAL`, `PRESENT_SRC_KHR`. Transitions через barrier:

```cpp
VkImageMemoryBarrier2 imgBarrier = {
    .oldLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
    .newLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
    .image = offscreenImage,
    .subresourceRange = { VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 },
    ...
};
```

Если layout не matches что shader ожидает — validation error, возможно crash.

### Synchronization2 (Vulkan 1.3+)

Упрощённый API через one-stop `VkMemoryBarrier2` вместо separate stage + access masks. VPA-16 требует.

### Timeline semaphores (Vulkan 1.2+)

Semaphore с incrementing counter. Лучше для complex CPU-GPU coordination:

```cpp
VkSemaphoreTypeCreateInfo typeInfo = {
    .semaphoreType = VK_SEMAPHORE_TYPE_TIMELINE,
    .initialValue = 0,
};
vkCreateSemaphore(device, {..., .pNext = &typeInfo}, nullptr, &timeline);

// Signal counter = 5
vkQueueSubmit(queue, ..., { .signalSemaphoreValue = 5 });

// Wait counter >= 5
vkWaitSemaphores(device, { .pSemaphores = &timeline, .pValues = &five }, UINT64_MAX);
```

---

## Memory Management

### Memory types

VkPhysicalDevice exposes multiple memory types с различными properties:
- **`DEVICE_LOCAL`** — fastest GPU access, not CPU-accessible. Stored в VRAM (on mobile — part of system RAM allocated для GPU).
- **`HOST_VISIBLE`** — CPU can map and write. Slower GPU access.
- **`HOST_COHERENT`** — CPU writes automatically visible в GPU (no flush needed).
- **`HOST_CACHED`** — CPU reads cached.
- **`LAZILY_ALLOCATED`** — memory backing tile memory, real allocation lazy. **Key для mobile TBR.**

### Typical allocations

```cpp
// Vertex buffer (static) — DEVICE_LOCAL, upload via staging
VkBuffer vertexBuffer;
VkDeviceMemory vertexMem;  // DEVICE_LOCAL

// Uniform buffer (per-frame updates) — HOST_VISIBLE | HOST_COHERENT
VkBuffer ubo;
VkDeviceMemory uboMem;  // HOST_VISIBLE + HOST_COHERENT

// Depth attachment (transient on TBR) — DEVICE_LOCAL + LAZILY_ALLOCATED
VkImage depthImage;
VkDeviceMemory depthMem;  // LAZY, memoryless
```

### Host Image Copy (VPA-16)

`VK_EXT_host_image_copy` (Vulkan 1.4, required by VPA-16) — CPU copy directly in VkImage без intermediate staging buffer. Экономит memory, упрощает texture upload.

```cpp
VkHostImageCopyFlags flags = 0;
VkMemoryToImageCopy copy = {
    .pHostPointer = texelData,
    .imageSubresource = { VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1 },
    .imageExtent = { width, height, 1 },
};
vkCopyMemoryToImageEXT(device, { ..., .regionCount = 1, .pRegions = &copy });
```

### Memory allocator library

Прямая Vulkan memory management verbose. Рекомендуется **[Vulkan Memory Allocator (VMA)](https://gpuopen.com/vulkan-memory-allocator/)** от AMD — open-source allocator поверх Vulkan API. Handles:
- Memory type selection.
- Allocation pooling.
- Defragmentation.
- Mapping/unmapping.

Production Vulkan apps обычно используют VMA.

---

## Staging buffer pattern

Для DEVICE_LOCAL memory (быстро для GPU) CPU не может write directly. Pattern:

1. Create staging buffer в HOST_VISIBLE memory.
2. CPU писет data в staging buffer.
3. Command buffer copies staging → DEVICE_LOCAL via `vkCmdCopyBuffer`.
4. Submit, wait completion.
5. Destroy staging buffer.

```cpp
// Create staging
VkBuffer stagingBuffer;
VkDeviceMemory stagingMem;
createBuffer(size, VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
             VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
             VK_MEMORY_PROPERTY_HOST_COHERENT_BIT,
             stagingBuffer, stagingMem);

// Map, write data
void* mapped;
vkMapMemory(device, stagingMem, 0, size, 0, &mapped);
memcpy(mapped, srcData, size);
vkUnmapMemory(device, stagingMem);

// Create destination
VkBuffer destBuffer;
createBuffer(size, VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
             VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT,
             destBuffer, destMem);

// Copy command
VkBufferCopy copyRegion = { 0, 0, size };
vkCmdCopyBuffer(cmd, stagingBuffer, destBuffer, 1, &copyRegion);

// Submit and wait
submitAndWait(cmd);

// Cleanup staging
vkDestroyBuffer(device, stagingBuffer, nullptr);
vkFreeMemory(device, stagingMem, nullptr);
```

Host image copy (VPA-16) bypasses staging buffer — can write directly в VkImage.

## Queue families

Vulkan GPUs expose multiple **queue families**:
- **Graphics** — vertex + fragment + compute.
- **Compute** — compute only.
- **Transfer** — memory copies only.
- **Sparse binding** — sparse resources.

Different queue families могут execute parallel. Async compute — doing compute work parallel с graphics. На mobile typically:
- 1 graphics queue (main rendering).
- 1 transfer queue (for async uploads) — available on most modern SoCs.
- 1 compute queue — shared или separate.

```cpp
uint32_t queueFamilyCount;
vkGetPhysicalDeviceQueueFamilyProperties(gpu, &queueFamilyCount, nullptr);
std::vector<VkQueueFamilyProperties> queueFamilies(queueFamilyCount);
vkGetPhysicalDeviceQueueFamilyProperties(gpu, &queueFamilyCount, queueFamilies.data());

// Find specific queue family
for (uint32_t i = 0; i < queueFamilyCount; i++) {
    if (queueFamilies[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) {
        graphicsQueueFamilyIndex = i;
    }
    if (queueFamilies[i].queueFlags == VK_QUEUE_TRANSFER_BIT) {
        transferQueueFamilyIndex = i;  // dedicated transfer queue
    }
}
```

## Queue ownership transfer

Resources accessed by multiple queue families требуют ownership transfer. Rare в простых apps, но important если используете async transfer queue:

```cpp
// Release from graphics queue
VkBufferMemoryBarrier2 release = {
    .srcQueueFamilyIndex = graphicsQueueFamilyIndex,
    .dstQueueFamilyIndex = transferQueueFamilyIndex,
    // ...
};

// Acquire in transfer queue (on submit там)
VkBufferMemoryBarrier2 acquire = {
    .srcQueueFamilyIndex = graphicsQueueFamilyIndex,
    .dstQueueFamilyIndex = transferQueueFamilyIndex,
    // ...
};
```

---

## Memoryless attachments

Ключевой mobile feature. Depth buffer, G-buffer, transient offscreen для TBR:

```cpp
VkImageCreateInfo depthImage = {
    .usage = VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT |
             VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT,  // transient
    ...
};
// Allocate from LAZILY_ALLOCATED memory type
```

Tile memory never flushed to DRAM. Zero bandwidth cost для depth.

---

## Реальные кейсы

### Filament memory strategy

Filament uses VMA (Vulkan Memory Allocator) под капотом:
- Static vertex/index buffers: DEVICE_LOCAL + staging upload.
- Per-frame UBOs: HOST_VISIBLE + HOST_COHERENT, ring buffer pattern.
- Textures: DEVICE_LOCAL с staging, или Host Image Copy где supported.
- Depth/G-buffer: LAZILY_ALLOCATED (memoryless).

Peak memory на Sponza scene: ~80 MB device local, 8 MB host visible для ring buffers.

### Planner 5D custom engine

Custom allocator (до VMA existed):
- Pool of DEVICE_LOCAL blocks (16 MB each).
- Linear sub-allocations within pool.
- Defragmentation periodically.
- Staging pool 32 MB reused для uploads.

Peak usage: ~60 MB для 50-object interior scene с PBR textures.

### Timeline semaphore use case

Synchronizing async compute с graphics:
```cpp
// Graphics queue signals timeline = N
vkQueueSubmit(graphicsQueue, ..., { .signalSemaphoreValue = N });

// Compute queue waits N, then performs post-processing
vkQueueSubmit(computeQueue, ..., {
    .waitSemaphoreValue = N,
    .signalSemaphoreValue = N+1,
});

// Main thread waits N+1 before present
vkWaitSemaphores(device, { .pSemaphores = &timeline, .pValues = &nplus1 });
```

Traditional binary semaphores не enough — timeline позволяет multi-step синхронизацию.

---

## Подводные камни

### Ошибка 1: Wrong barrier direction

`srcStageMask` — когда writes happen. `dstStageMask` — когда reads happen. Easy to confuse. Validation layers помогают.

### Ошибка 2: Missing barrier

Without barrier, memory writes не visible для subsequent reads. Symptom — corrupted images, wrong data. Very hard to debug.

### Ошибка 3: Too many barriers

Over-synchronization hurts performance. Use `VK_KHR_synchronization2` с precise stage masks, не `PIPELINE_STAGE_ALL_COMMANDS_BIT`.

### Ошибка 4: Memory leak в pool

VkDeviceMemory allocations limited (~4096 per process). Pool allocations через VMA.

---

## Связь

[[vulkan-on-android-fundamentals]] — context.
[[vulkan-pipeline-command-buffers]] — CBs между которыми sync.
[[gpu-memory-management-mobile]] — memory detail в контексте mobile.
[[tile-based-rendering-mobile]] — memoryless attachments.

---

## Источники

- **Vulkan 1.4 Spec chapters 7, 11.**
- **GPUOpen. Vulkan Barriers Explained.** [gpuopen.com/learn/vulkan-barriers-explained](https://gpuopen.com/learn/vulkan-barriers-explained/).
- **AMD Vulkan Memory Allocator.** [gpuopen.com/vulkan-memory-allocator](https://gpuopen.com/vulkan-memory-allocator/).

---

## Проверь себя

> [!question]- Зачем image layout transitions?
> GPU stores image в различных internal representations depending on use (color attachment, shader read, present). Explicit transitions через barriers сообщают driver — optimize layout для next use. Missing transition → wrong format used, corruption.

> [!question]- Что такое memoryless attachment?
> VkImage с `TRANSIENT_ATTACHMENT_BIT` + `LAZILY_ALLOCATED` memory. Backing memory никогда не allocated в DRAM — только tile memory (on-chip SRAM). Zero bandwidth cost. Ideal для depth и G-buffer на TBR.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Pipeline detail | [[vulkan-pipeline-command-buffers]] |
| Mobile memory | [[gpu-memory-management-mobile]] |
| TBR | [[tile-based-rendering-mobile]] |

---

*Deep-dive модуля M4.*
