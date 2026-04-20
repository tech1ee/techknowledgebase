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

Vulkan — explicit API, значит программист отвечает за два сложных domain: **synchronization** (execution и memory dependencies между commands) и **memory management** (allocation, typing, binding). Неправильное использование — source most Vulkan bugs.

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
