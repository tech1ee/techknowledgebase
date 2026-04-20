---
title: "GPU memory management на mobile: VRAM, tile memory, transient attachments"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/optimization
  - type/deep-dive
  - level/advanced
related:
  - "[[vulkan-synchronization-memory]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[asset-loading-streaming]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vulkan-synchronization-memory]]"
reading_time: 12
difficulty: 5
---

# GPU memory на mobile

На mobile devices нет физически отдельной VRAM — CPU и GPU share **unified memory** (system RAM). Это и плюс (zero-copy возможен), и минус (bandwidth contention, memory pressure). Правильное memory management — критическая часть performance.

---

## Уникальность mobile memory

Unlike desktop GPUs с dedicated VRAM (separate 8-24 GB), mobile GPUs share system RAM with CPU:
- **Unified Memory Architecture (UMA).** Physical same pool.
- **Bandwidth shared.** 51-68 GB/s LPDDR5X, divided between CPU (30-40%), GPU (40-60%), display (10-20%).
- **No PCIe overhead** — same physical memory, no transfer latency.
- **Но cache coherence — tricky.** CPU writes needed flush для GPU visibility.

Consequences:
- **Memory "pressure" shared.** App using too much RAM affects both CPU и GPU.
- **Transfer "free"** (nominally) — no PCIe, но cache flushes still have cost.
- **Bandwidth is king.** More budget goes к reducing memory reads/writes чем к allocations themselves.

Historical evolution:
- **2010 — early mobile.** Very limited memory (512 MB total RAM). Textures had to be compressed aggressively.
- **2015 — 4 GB becomes norm.**
- **2020 — flagship 12 GB+.**
- **2024 — 16 GB flagship.** Enables desktop-class games.
- **2026 — 24 GB coming в ultra-flagship.** AI workloads drive increased memory.

## Memory hierarchy на mobile

```
Registers (per shader thread, few KB total)
    ↓
Tile Memory (on-chip SRAM, ~128-512 KB) — TBR critical resource
    ↓
L1 Cache (per SM, ~32 KB)
    ↓
L2 Cache (system-wide, ~2-8 MB)
    ↓
System RAM (shared CPU/GPU, 4-16 GB)
```

Each level — ~10× slower than previous. Keep data в fastest level as much as possible.

---

## Memory types Vulkan

See [[vulkan-synchronization-memory#Memory types]] для detail. Summary:

- **DEVICE_LOCAL** — allocated в system RAM для GPU access. Fast GPU read/write. Not CPU-accessible.
- **HOST_VISIBLE** — CPU can map и write. Slower GPU access.
- **HOST_COHERENT** — auto-visible to GPU.
- **LAZILY_ALLOCATED** — for transient attachments, backing memory lazy (may never allocate).

---

## Transient attachments (critical)

Depth/stencil buffer и intermediate framebuffer attachments:

```cpp
VkImageCreateInfo transient = {
    .usage = VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT |
             VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT,
    ...
};

// Allocate from LAZILY_ALLOCATED memory type
// Never flushes to DRAM on TBR GPUs
```

**Saving:** depth buffer для 1080p = ~8 MB. Transient → 0 MB в DRAM.

---

## AFBC (ARM Frame Buffer Compression)

Mali GPUs auto-compress framebuffer attachments в tile memory. Lossless ~2× compression. Transparent — enable via format/usage flags.

---

## Memory budget

Typical Android:
- **Total RAM:** 4-16 GB.
- **Process limit:** 512 MB (low) to 4+ GB (flagship).
- **Graphics budget:** ~50-200 MB typical для 3D app.

Breakdown for 200 MB:
- Vertex buffers: 30 MB.
- Index buffers: 10 MB.
- Textures: 100 MB.
- Uniforms / constants: 10 MB.
- Swapchain images (3× triple buffering): 20 MB.
- Overhead: 30 MB.

---

## Vulkan Memory Allocator (VMA)

Production-grade allocator от AMD. Handles:
- Memory type selection.
- Sub-allocation pools.
- Defragmentation.
- Mapping.

```cpp
VmaAllocatorCreateInfo vmaInfo = {
    .physicalDevice = physicalDevice,
    .device = device,
    .instance = instance,
};
VmaAllocator allocator;
vmaCreateAllocator(&vmaInfo, &allocator);

VkBufferCreateInfo bufferInfo = { ... };
VmaAllocationCreateInfo allocInfo = {
    .usage = VMA_MEMORY_USAGE_AUTO,
};
VkBuffer buffer;
VmaAllocation allocation;
vmaCreateBuffer(allocator, &bufferInfo, &allocInfo, &buffer, &allocation, nullptr);
```

---

## Staging buffers

Upload CPU data to DEVICE_LOCAL via staging:

1. Allocate HOST_VISIBLE staging buffer.
2. `memcpy` data в staging.
3. `vkCmdCopyBuffer` staging → DEVICE_LOCAL GPU buffer.
4. Submit, wait fence.
5. Free staging.

For textures: `vkCmdCopyBufferToImage`.

Alternative (VPA-16, Vulkan 1.4): **Host Image Copy** — direct CPU → VkImage без staging. Ускоряет loading, saves memory.

---

## Texture memory strategies

### Mipmaps

Automatic power-of-2 reductions. GPU selects appropriate mip based on distance. Standard approach. Texture memory = 4/3 × base (all mips combined).

### Texture atlases

Combine small textures в одну большую. Reduces binding changes и descriptor count. Common для UI textures.

### Texture streaming

Load low mips first, high mips on demand based on visible size. Virtual texturing — advanced; few mobile engines имеют.

### Compressed formats

ASTC / ETC2 / BCn уменьшают memory 4-10×. KTX2 + Basis Universal для universal delivery (см. [[texture-compression-ktx2-basis]]).

---

## Memory pressure

Android signals low memory via `ComponentCallbacks2.onTrimMemory`. Levels:

- `TRIM_MEMORY_RUNNING_LOW` — app usable, OS under pressure.
- `TRIM_MEMORY_BACKGROUND` — app backgrounded, can reduce.
- `TRIM_MEMORY_UI_HIDDEN` — UI hidden, can free UI caches.
- `TRIM_MEMORY_CRITICAL` — urgent.

Response:
```kotlin
override fun onTrimMemory(level: Int) {
    when (level) {
        TRIM_MEMORY_UI_HIDDEN -> clearUITextureCache()
        TRIM_MEMORY_BACKGROUND -> reduceAssetDetail()
        TRIM_MEMORY_CRITICAL -> freeAllNonEssential()
    }
}
```

---

## Profile

AGI shows memory allocations и usage. Key metrics:
- **Allocation count** — too many = overhead.
- **Total GPU memory** — stay within budget.
- **Swapchain acquire time** — high = back-pressure from SurfaceFlinger.

---

## Связь

[[vulkan-synchronization-memory]] — memory types.
[[tile-based-rendering-mobile]] — transient attachments.
[[asset-loading-streaming]] — streaming strategies.
[[texture-compression-ktx2-basis]] — texture memory reduction.

---

## Источники

- **Vulkan Memory Allocator.** [gpuopen.com/vulkan-memory-allocator](https://gpuopen.com/vulkan-memory-allocator/).
- **ARM Mali Memory Best Practices.**
- **Khronos Vulkan memory types.**

---

## Проверь себя

> [!question]- Почему transient attachments важны на mobile?
> Они backed by LAZILY_ALLOCATED memory — backing не allocated в DRAM если GPU не flush tile memory. Depth buffer 8 MB → 0 MB в RAM. Significant win для multi-pass rendering.

---

*Deep-dive модуля M10.*
