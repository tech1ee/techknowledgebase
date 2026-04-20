---
title: "Vulkan на Android: основы, статус 2026 и VPA-16"
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
  - level/intermediate
related:
  - "[[rendering-pipeline-overview]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[vulkan-pipeline-command-buffers]]"
  - "[[opengl-vs-vulkan-decision]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://developer.android.com/games/develop/vulkan/overview"
    title: "Android Developers: Vulkan overview"
    accessed: 2026-04-20
  - url: "https://developer.android.com/ndk/guides/graphics/getting-started"
    title: "Android NDK: Vulkan getting started"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/"
    title: "Vulkan 1.4 Specification"
    accessed: 2026-04-20
  - url: "https://developer.android.com/ndk/guides/graphics/android-vulkan-profile"
    title: "Android Vulkan Profiles (VPA)"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/compatibility/16/android-16-cdd"
    title: "Android 16 Compatibility Definition (VPA-16 requirements)"
    accessed: 2026-04-20
reading_time: 25
difficulty: 6
---

# Vulkan на Android

Vulkan на Android в 2026 году — не экспериментальный API, а **default для новых проектов**. 85 % активных устройств поддерживают Vulkan 1.1+, flagship'ы имеют Vulkan 1.3/1.4. Android 16 (апрель 2026) обязывает производителей новых устройств сертифицироваться по **Vulkan Profile for Android 16 (VPA-16)**, включающему Host Image Copy, advanced synchronization, 4+ hardware overlay planes. Google's ANGLE постепенно становится GL driver по default, т. е. даже «OpenGL ES» приложения в 2026 исполняются на Vulkan layer underneath.

Этот файл разбирает: что такое Vulkan принципиально, зачем он нужен mobile GPU, и какая его структура на Android. Последующие файлы M4 углубляются в pipeline/command buffers ([[vulkan-pipeline-command-buffers]]), synchronization ([[vulkan-synchronization-memory]]), сравнение с OpenGL ES ([[opengl-vs-vulkan-decision]]).

---

## Зачем это знать

**Первое — правильный выбор API.** Новые проекты в 2026: Vulkan лучший выбор для 3D. OpenGL ES уместен только для very-legacy support или простых 2D с GL.

**Второе — правильное использование.** Vulkan — explicit API: программист сам управляет memory, synchronization, pipeline state. Неправильное использование даёт хуже performance, чем OpenGL ES. Правильное — 20-30 % CPU saving и better thermal behavior.

**Третье — будущее Android graphics.** VPA-16, ANGLE, Jetpack XR, HDR — всё строится вокруг Vulkan. Понимание основ необходимо для любой серьёзной работы с графикой на Android в 2026+.

---

## Prerequisites

- [[rendering-pipeline-overview]] — general pipeline structure.
- [[gpu-architecture-fundamentals]] — SIMT, warps.
- [[tile-based-rendering-mobile]] — почему render pass design critical.

---

## Терминология

| Термин | Что |
|---|---|
| Vulkan | Low-level cross-platform graphics and compute API от Khronos Group |
| VkInstance | Per-process Vulkan handle |
| VkPhysicalDevice | GPU hardware |
| VkDevice | Logical device handle (один на physical device в typical app) |
| Queue | Очередь командбуферов; supports graphics / compute / transfer / present |
| CommandBuffer | Pre-recorded sequence of GPU commands |
| Pipeline | Pre-compiled state (shaders + fixed functions) |
| Descriptor | Binding между shader и resource (buffer, image, sampler) |
| Synchronization primitives | Semaphore, fence, barrier, event |
| VPA-16 | Vulkan Profile for Android 16 — certification requirements |
| Host Image Copy | `VK_EXT_host_image_copy` — CPU → GPU image upload без staging buffer |

---

## Историческая справка

- **2013 — AMD Mantle.** Proprietary low-level API для AMD GPUs, foundation for Vulkan.
- **2014 — Khronos announces "glNext".**
- **2016 — Vulkan 1.0 release.**
- **2016 — Android 7.0 Nougat.** Vulkan support added to Android NDK.
- **2017 — Vulkan 1.1.** Subgroup operations, 16-bit storage.
- **2019 — Vulkan 1.2.** Timeline semaphores, buffer device address.
- **2022 — Vulkan 1.3.** Dynamic rendering, synchronization2 (simpler API), extended dynamic state.
- **2024 — Vulkan 1.4.** Host image copy, push descriptors standard, new clipping/depth features.
- **2025 — VPA-16 draft.** Required capabilities для Android 16 certification.
- **2026 — Android 16 release.** VPA-16 mandatory для new phones.

Vulkan became first-class on Android — Google invested heavily in drivers, tools (AGI), libraries (Swappy, validation layers).

---

## Философия Vulkan — что делает его особенным

Vulkan spec (Khronos 2016) был спроектирован с тремя core principles:

### 1. Explicit over implicit

**OpenGL ES философия:** driver «знает лучше». Hide complexity, allow simple patterns. Example: `glBufferData(target, size, data)` — driver decides where memory lives, when to copy, lifetime, etc.

**Vulkan философия:** программист «знает лучше». Expose every decision. Example: для того же effect в Vulkan — создаём VkBuffer с usage flags, запрашиваем memory requirements, allocate VkDeviceMemory из explicit memory type (DEVICE_LOCAL, HOST_VISIBLE, etc.), bind. 4 calls вместо одного.

Cost: более сложный API, более длинный initialization. Benefit: no hidden driver overhead, predictable performance.

### 2. Pre-validate, pre-compile

OpenGL ES валидирует **каждый draw call** (shader binding, state consistency, etc.) — expensive overhead каждый раз.

Vulkan валидирует **pipeline creation once**. Compile все shaders, validate all state → opaque VkPipeline. Every draw then just binds pipeline и issues command — zero validation cost.

Impact: app с 1000 draws/frame может save 10-20 ms CPU per frame on OpenGL ES → ~30-60 FPS pure from API overhead reduction.

### 3. Multi-threaded by design

OpenGL ES имеет **single GL context** per thread. Switching contexts = expensive. Thus rendering happens on one thread.

Vulkan: command buffers могут записываться **параллельно** в разных threads. Finally submitted to queue from one thread. Games с complex scenes могут использовать 4-8 threads для parallel command recording.

Example: Planner 5D scene recording:
- Thread 1: shadow map command buffer.
- Thread 2: opaque scene command buffer.
- Thread 3: transparent objects command buffer.
- Thread 4: UI overlay command buffer.
- Main thread: submit all 4 to queue sequentially.

4× faster CPU-side commanding vs serial OpenGL ES.

---

## Архитектура Vulkan на Android

```
┌─────────────────────────────────────────────┐
│  App (Kotlin / C++ via NDK)                 │
│  Vulkan API calls (vkCreateInstance, etc.)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Vulkan Loader (part of Android)            │
│  • libvulkan.so                              │
│  • Entry-point dispatch                      │
│  • Validation layers (debug only)            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Vendor Vulkan Driver                        │
│  • Qualcomm (Adreno)                         │
│  • ARM (Mali Vulkan driver)                  │
│  • Imagination (PowerVR)                     │
│  • Samsung (Xclipse RDNA driver)             │
│  Translates Vulkan commands → HW commands    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  GPU Hardware                                │
└─────────────────────────────────────────────┘
```

Vulkan Loader — tiny abstraction over vendor driver. Validation layers — injectable для debug builds (huge help for catching bugs).

### Core objects

- **`VkInstance`** — per-process. Созд создаётся первым.
- **`VkPhysicalDevice`** — GPU hardware enumeration.
- **`VkDevice`** — logical interface to one physical device.
- **`VkQueue`** — очереди для submitting commands. Обычно одна graphics queue + опциональная async compute, transfer.
- **`VkCommandPool`** + **`VkCommandBuffer`** — recording commands.
- **`VkSwapchain`** — swapchain для presenting to surface.

### Пример minimal init (Kotlin + NDK)

```cpp
VkInstanceCreateInfo instanceInfo = {
    .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
    .pApplicationInfo = &appInfo,
    // extensions: VK_KHR_surface, VK_KHR_android_surface, validation
};
VkInstance instance;
vkCreateInstance(&instanceInfo, nullptr, &instance);

// Enumerate physical devices
uint32_t count;
vkEnumeratePhysicalDevices(instance, &count, nullptr);
std::vector<VkPhysicalDevice> gpus(count);
vkEnumeratePhysicalDevices(instance, &count, gpus.data());

// Choose GPU (обычно first suitable)
VkPhysicalDevice gpu = gpus[0];

// Create device
VkDeviceQueueCreateInfo queueInfo = {
    .queueFamilyIndex = 0,  // graphics queue family
    .queueCount = 1,
    .pQueuePriorities = &priority,
};
VkDeviceCreateInfo deviceInfo = {
    .queueCreateInfoCount = 1,
    .pQueueCreateInfos = &queueInfo,
    // features, extensions
};
VkDevice device;
vkCreateDevice(gpu, &deviceInfo, nullptr, &device);
```

### Frame loop

```cpp
while (running) {
    uint32_t imageIndex;
    vkAcquireNextImageKHR(device, swapchain, UINT64_MAX, imageAvailableSem, VK_NULL_HANDLE, &imageIndex);
    
    // Record commands
    vkBeginCommandBuffer(cmd, &beginInfo);
    vkCmdBeginRenderPass(cmd, &renderPassInfo, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline);
    vkCmdDraw(cmd, 3, 1, 0, 0);
    vkCmdEndRenderPass(cmd);
    vkEndCommandBuffer(cmd);
    
    // Submit
    vkQueueSubmit(queue, 1, &submitInfo, renderFence);
    
    // Present
    vkQueuePresentKHR(queue, &presentInfo);
}
```

---

## VPA-16 (Android 16, 2026)

[Vulkan Profile for Android 16](https://developer.android.com/ndk/guides/graphics/android-vulkan-profile) — certification:

**Required features:**
- Vulkan 1.3 baseline.
- `VK_KHR_dynamic_rendering` — упрощённый rendering без explicit render pass.
- `VK_KHR_synchronization2` — simpler barriers API.
- `VK_EXT_host_image_copy` — CPU → GPU image upload без staging.
- `VK_KHR_push_descriptor` — dynamic descriptors без descriptor sets.
- 4+ hardware overlay planes для HWC.
- 8K texture support.

**Benefits:**
- Consistent developer experience across all Android 16 devices.
- Advanced features gated behind device class.
- Better optimized drivers with standard feature set.

### Что это значит для разработчика

Если target `minSdk = Android 16`, можно рассчитывать на VPA-16 features без fallback кода. Для `minSdk < Android 16`, требуется feature detection + fallback.

---

## Swapchain на Android — детально

Swapchain — мост между Vulkan rendering и Android display/compositor. Создаётся over platform-specific surface.

```cpp
// Android-specific surface creation
VkAndroidSurfaceCreateInfoKHR surfaceInfo = {
    .sType = VK_STRUCTURE_TYPE_ANDROID_SURFACE_CREATE_INFO_KHR,
    .window = androidNativeWindow,  // from AAssetManager или ANativeWindow
};
VkSurfaceKHR surface;
vkCreateAndroidSurfaceKHR(instance, &surfaceInfo, nullptr, &surface);

// Query surface capabilities
VkSurfaceCapabilitiesKHR caps;
vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physicalDevice, surface, &caps);

// Создание swapchain
VkSwapchainCreateInfoKHR swapchainInfo = {
    .surface = surface,
    .minImageCount = 3,  // triple buffering typical
    .imageFormat = VK_FORMAT_R8G8B8A8_UNORM,
    .imageExtent = caps.currentExtent,
    .presentMode = VK_PRESENT_MODE_FIFO_KHR,
    .preTransform = caps.currentTransform,  // для pre-rotation!
    ...
};
```

### Pre-rotation на Android

Ключевая особенность: phone может быть в portrait или landscape. Если `currentTransform == VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR` — display expects rotated output.

**Wrong approach:** render in identity orientation, compositor handles rotation → extra pass, 10-15% overhead.

**Right approach:** render in physical orientation. Apply rotation matrix in vertex shader:

```glsl
// Vertex shader
layout(push_constant) uniform PrerotateConstants {
    mat4 prerotateMatrix;
} prerotate;

void main() {
    gl_Position = prerotate.prerotateMatrix * mvpMatrix * position;
}
```

CPU-side matrix computed once per orientation change:
```cpp
mat4 prerotate = mat4(1.0f);
switch (surfaceCaps.currentTransform) {
    case VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR:
        prerotate = rotate(prerotate, 90.0f, vec3(0, 0, 1));
        break;
    case VK_SURFACE_TRANSFORM_ROTATE_180_BIT_KHR:
        prerotate = rotate(prerotate, 180.0f, vec3(0, 0, 1));
        break;
    // ...
}
```

### Swapchain image acquisition

```cpp
uint32_t imageIndex;
VkResult result = vkAcquireNextImageKHR(
    device, swapchain, UINT64_MAX,
    imageAvailableSemaphore,  // signals когда image ready
    VK_NULL_HANDLE,
    &imageIndex
);

if (result == VK_ERROR_OUT_OF_DATE_KHR) {
    // Window resized или orientation changed — recreate swapchain
    recreateSwapchain();
    return;
}
```

### Present mode nuances

- **FIFO:** guaranteed VSYNC-lock. Safe battery-efficient choice.
- **FIFO_RELAXED:** VSYNC unless late — then immediate. Reduces stuttering на slow frames.
- **MAILBOX:** latest frame always shown. No tearing. High battery use.
- **IMMEDIATE:** no sync. Tearing possible. Rarely used.

На Android VRR (variable refresh rate) — FIFO_RELAXED часто best choice. `Surface.setFrameRate()` hint для adaptive VSYNC.

---

## Validation layers — must for development

Vulkan не прощает mistakes. Spec violation = undefined behavior (crash, corruption, silent incorrect rendering).

**Validation layers** — injectable CPU layer that intercepts API calls и checks spec compliance. Catches 90% of bugs.

```cpp
const char* validationLayers[] = {
    "VK_LAYER_KHRONOS_validation",  // Khronos-provided
};

VkInstanceCreateInfo instanceInfo = {
    .enabledLayerCount = 1,
    .ppEnabledLayerNames = validationLayers,
    // ...
};
```

Messages printed через debug callback:
```cpp
VkDebugUtilsMessengerCreateInfoEXT debugInfo = {
    .messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                       VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
    .messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                   VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                   VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
    .pfnUserCallback = debugCallback,
};
```

**Production builds:** disable validation layers — 10-30% CPU overhead.

---

## Extensions важные для Android

Vulkan базовая spec — minimal. Extensions добавляют platform features.

### Required для Android

- `VK_KHR_surface` — generic surface.
- `VK_KHR_android_surface` — Android ANativeWindow integration.
- `VK_KHR_swapchain` — swapchain support.

### Highly recommended

- `VK_KHR_maintenance1/2/3/4` — minor spec fixes, always enable.
- `VK_KHR_external_memory/semaphore/fence` — sharing resources between processes (e.g., camera feed).
- `VK_KHR_shader_float16_int8` — smaller data types для compute.
- `VK_EXT_debug_utils` — debug labels, naming resources.

### VPA-16 mandatory

- `VK_KHR_dynamic_rendering`
- `VK_KHR_synchronization2`
- `VK_EXT_host_image_copy`
- `VK_KHR_push_descriptor`
- `VK_EXT_extended_dynamic_state3`
- `VK_EXT_image_compression_control`

### Flagship / specialized

- `VK_KHR_ray_tracing_pipeline` — full ray tracing.
- `VK_KHR_ray_query` — inline ray queries в regular shaders.
- `VK_EXT_mesh_shader` — modern geometry pipeline.
- `VK_EXT_fragment_shader_interlock` — ordered fragment shader execution.

---

## Ключевые особенности Vulkan vs OpenGL ES

### Explicit synchronization

В OpenGL ES driver automatically sync between commands. Vulkan — программист must explicitly synchronize через:
- **Semaphores** — GPU-to-GPU sync within frame.
- **Fences** — GPU-to-CPU sync (CPU waits for GPU done).
- **Barriers** — sync внутри command buffer (memory / execution).
- **Events** — fine-grained.

Cost: разработчик должен думать. Benefit: hardware не угадывает — точно знает dependencies.

### Explicit memory management

OpenGL ES — driver allocates memory. Vulkan — программист:
1. Create `VkBuffer` / `VkImage`.
2. Query memory requirements.
3. Allocate `VkDeviceMemory` из подходящего memory type.
4. Bind memory to resource.

Для mobile — **memoryless attachments** (transient, never leaves tile memory) это power feature недоступная в GL.

### Pre-validated state

OpenGL ES driver validates state каждый draw call (slow). Vulkan validates once при создании pipeline, multiple draws share compiled state.

Для CPU-bound apps с thousands of draw calls — Vulkan саved 10-20 % CPU.

### Multi-threading

OpenGL ES — GL context per thread, switching expensive. Vulkan — command buffers can be recorded on multiple threads parallel, then submitted from one.

Games с multi-threaded rendering — significant win.

---

## Типичные ошибки Android-developers при переходе на Vulkan

### Ошибка: missing pre-rotation

OpenGL ES driver автоматически делает rotation для orientation. Vulkan — нет. Забытое pre-rotation в Vulkan приводит:
- 10-15% performance drop (лишний compositor pass).
- Battery drain увеличен.
- На older phones — visible tearing или artifacts.

### Ошибка: тяжёлая synchronization

Vulkan allows fine-grained synchronization. Novice programmers часто over-synchronize (too many fences, barriers), что убивает parallelism. Best practice: start с minimal sync (one fence per frame), add только когда validation layers flag issues.

### Ошибка: создание pipeline в hot path

VkPipeline creation — expensive (shader compilation). Если app создаёт pipelines in rendering loop (при смене state), получает hitches.

**Solution:** предсоздать все нужные pipelines at startup, cache via VkPipelineCache. См. [[shader-compilation-jitter-mitigation]].

### Ошибка: неправильный memory type

Vulkan имеет много memory types:
- `DEVICE_LOCAL_BIT`: быстрая GPU memory. Default choice.
- `HOST_VISIBLE_BIT`: CPU может читать/писать. Медленнее для GPU.
- `DEVICE_LOCAL | HOST_VISIBLE`: best of both (unified memory на mobile!). Available на most Android.
- `LAZILY_ALLOCATED_BIT`: memoryless attachments, transient.

Mobile GPUs имеют unified memory — no dedicated VRAM. Properties different от desktop. Использовать `LAZILY_ALLOCATED` для depth/stencil = major bandwidth saving.

### Ошибка: ignoring device limits

`VkPhysicalDeviceLimits` содержит tons of constraints: max texture size, max uniform buffer size, max bound descriptors, etc. Разные devices — разные limits. Mobile обычно ниже desktop.

Example: `maxImageDimension2D` на flagship = 16384, на budget = 4096. Если app предполагает 8K texture, на budget device fails.

**Solution:** always query limits, scale assets / quality tiers accordingly.

---

## Performance budget на Android mobile

Typical target 60 FPS = 16.67 ms/frame. Breakdown:

| Stage | Budget | Notes |
|---|---|---|
| CPU app logic | ~3-5 ms | Main thread, Compose, physics |
| CPU command recording | ~1-2 ms | Vulkan command buffers |
| CPU → GPU submission | ~0.5 ms | Vulkan driver |
| GPU execution | ~8-10 ms | Actual rendering |
| Composition (SF) | ~1-2 ms | SurfaceFlinger |
| HWC | ~0.5 ms | Hardware composition |
| Total | ~15 ms | Буфер 1-2 ms для variance |

При 120 FPS — half of this. At 30 FPS — double.

Thermal throttling на sustained load: CPU/GPU downclock → budget becomes tighter. Game mode / ADPF helps maintain budget (см. [[thermal-throttling-and-adpf]]).

---

## Когда использовать Vulkan на Android 2026

✅ **Brand new 3D apps** — default choice.
✅ **Performance-critical** — games, AR, professional 3D.
✅ **Complex pipelines** — deferred rendering, compute integration.
✅ **Cross-platform** — Vulkan runs на Windows, Linux, Android (not iOS без MoltenVK).

❌ **Simple 2D Canvas** — use Compose/View directly.
❌ **Legacy code with GL** — migration cost не оправдана для small projects.
❌ **Team без graphics experience** — Vulkan steep learning curve.

---

## Подводные камни

### Ошибка 1: Missing synchronization

**Симптом:** crashes, corrupted images, tearing.
**Как избежать:** validation layers в debug build. Use `VK_KHR_synchronization2` (simpler API).

### Ошибка 2: Overly complex first project

**Как избежать:** начать с established framework (Filament, SceneView, LunarG SDK samples). Vulkan не для "write my first renderer" projects.

### Ошибка 3: Ignoring Android-specific optimizations

**Как избежать:** pre-rotation, tile memory usage, VPA-16 features. AGI profiling.

---

## Связь с другими темами

[[vulkan-pipeline-command-buffers]] — detail on pipeline / CB.
[[vulkan-synchronization-memory]] — sync primitives и memory management.
[[angle-and-gl-compatibility]] — ANGLE как GL → Vulkan слой.
[[opengl-vs-vulkan-decision]] — when to choose какой.
[[shader-compilation-jitter-mitigation]] — SPIR-V pipeline cache.
[[tile-based-rendering-mobile]] — render pass design для TBR.
[[surfaceflinger-and-buffer-queue]] — VkSwapchain backing.

---

## Источники

- **Vulkan 1.4 Specification.** [registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/).
- **Android Developers: Vulkan overview.** [developer.android.com/games/develop/vulkan](https://developer.android.com/games/develop/vulkan/overview).
- **Android NDK: Vulkan getting started.** [developer.android.com/ndk/guides/graphics/getting-started](https://developer.android.com/ndk/guides/graphics/getting-started).
- **Android 16 CDD.** [source.android.com/docs/compatibility/16](https://source.android.com/docs/compatibility/16/android-16-cdd).
- **Sellers, G., Kessenich, J. (2017). Vulkan Programming Guide.** Канонический учебник.
- **LunarG SDK tutorials.** [vulkan.lunarg.com](https://vulkan.lunarg.com/).

---

## Проверь себя

> [!question]- Зачем VPA-16 на Android 16?
> Сертификационный стандарт, требующий новые устройства поддерживать определённый набор Vulkan features. Разработчик может рассчитывать на эти features без fallback. Standardize experience across Android 16+ devices.

> [!question]- В чём главное преимущество Vulkan над OpenGL ES на mobile?
> Explicit control (synchronization, memory, pipeline state) → меньше driver overhead → 20-30% CPU savings → better thermal/battery behavior. Также multi-threaded command recording.

---

## Ключевые карточки

Какая версия Vulkan требуется VPA-16?
?
Vulkan 1.3 baseline + specific extensions (dynamic rendering, synchronization2, host image copy, push descriptors).

---

Зачем Vulkan Loader на Android?
?
Tiny abstraction over vendor driver. Enables validation layers (debug), entry-point dispatch. Sits between app и actual driver (Adreno/Mali/PowerVR/Xclipse).

---

Что такое Host Image Copy?
?
`VK_EXT_host_image_copy` — CPU может напрямую copy data в VkImage без staging buffer. Экономит memory, упрощает texture upload. Обязательно в VPA-16.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Pipeline detail | [[vulkan-pipeline-command-buffers]] |
| Sync detail | [[vulkan-synchronization-memory]] |
| GL vs Vulkan | [[opengl-vs-vulkan-decision]] |
| Shader compilation | [[spir-v-and-compilation]] |

---

*Deep-dive модуля M4.*
