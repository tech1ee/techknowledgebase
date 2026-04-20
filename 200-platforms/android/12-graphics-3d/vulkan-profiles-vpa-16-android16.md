---
title: "Vulkan Profile for Android 16 (VPA-16)"
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
  - "[[vulkan-synchronization-memory]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vulkan-on-android-fundamentals]]"
primary_sources:
  - url: "https://developer.android.com/ndk/guides/graphics/android-vulkan-profile"
    title: "Android Vulkan Profiles documentation"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/compatibility/16/android-16-cdd"
    title: "Android 16 Compatibility Definition"
    accessed: 2026-04-20
reading_time: 10
difficulty: 5
---

# Vulkan Profile for Android 16 (VPA-16)

Android 16 (April 2026) ввёл **VPA-16** — обязательный сертификационный Vulkan profile для new devices. Разработчик может рассчитывать на определённые Vulkan 1.3+ features без fallback кода, если `minSdk = Android 16`.

---

## Зачем

Проблема: Vulkan на Android фрагментирован. Разные GPUs support different extensions, features, limits. Разработчики либо пишут fallback for every case, либо target наименьшего общего знаменателя. Medium-quality experience.

VPA-16 устанавливает minimum bar: производители новых устройств должны сертифицировать support определённого feature set.

Developer benefit:
- Single code path с advanced features.
- Known hardware minimums.
- Faster development.

---

## Required features

- **Vulkan 1.3 baseline** (2022).
- **`VK_KHR_dynamic_rendering`** — simplified rendering без explicit VkRenderPass. Optional, но encourages простую architecture.
- **`VK_KHR_synchronization2`** — simpler barriers API (см. [[vulkan-synchronization-memory]]).
- **`VK_EXT_host_image_copy`** — CPU→VkImage без staging buffer. Сэкономит memory, упрощает texture upload.
- **`VK_KHR_push_descriptor`** — dynamic descriptors без descriptor sets.
- **`VK_EXT_extended_dynamic_state`** — more state mutable per-draw.
- **Advanced sampler features:** `samplerYcbcrConversion`, `borderColorSwizzle`.
- **Image/buffer limits:** 8K texture support (8192×8192), 4 GB buffer size.
- **Render output:** 4+ hardware overlay planes для HWC composition.
- **HDR composition support** через HWC.
- **120 Hz refresh** support.
- **Adaptive refresh rate** (VRR).

---

## Feature detection

Before VPA-16 (minSdk < 16):

```cpp
VkPhysicalDeviceFeatures2 features = {};
features.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2;

VkPhysicalDeviceSynchronization2Features sync2 = {};
sync2.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES;
features.pNext = &sync2;

vkGetPhysicalDeviceFeatures2(physicalDevice, &features);
if (sync2.synchronization2) {
    // Use synchronization2
} else {
    // Fallback
}
```

With VPA-16 (minSdk = 16): no need — feature guaranteed.

---

## Практическая польза

### Рендеринг

Dynamic rendering упрощает подход:
```cpp
VkRenderingInfo renderingInfo = { ... };
vkCmdBeginRendering(cmd, &renderingInfo);
// draw
vkCmdEndRendering(cmd);
```

Меньше boilerplate vs explicit VkRenderPass. Но на TBR — explicit RenderPass still recommended для tile optimization hints (обсуждается в [[tile-based-rendering-mobile]]).

### Synchronization2

```cpp
VkMemoryBarrier2 barrier = {
    .srcStageMask = VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
    .dstStageMask = VK_PIPELINE_STAGE_2_FRAGMENT_SHADER_BIT,
    ...
};
```

Single struct vs separate srcStageMask/dstStageMask/srcAccessMask/dstAccessMask. Clearer, less error-prone.

### Host image copy

```cpp
VkMemoryToImageCopy copy = { ... };
vkCopyMemoryToImageEXT(device, ...);
```

Direct CPU→VkImage. No staging buffer, no barrier sequences. Texture upload easier.

---

## Migration path

### Pre-VPA-16 code

```cpp
// Check feature, fallback if not supported
if (hasSynchronization2) {
    vkCmdPipelineBarrier2(cmd, ...);
} else {
    vkCmdPipelineBarrier(cmd, srcStage, dstStage, ...);
}
```

### VPA-16 era

```cpp
// Guaranteed — just use
vkCmdPipelineBarrier2(cmd, ...);
```

Simpler code, faster development.

---

## When to target

### minSdk Android 16

- **Brand new apps** — consider targeting Android 16+.
- Android 16 market share slowly growing через 2026-2027.
- Early adopter phones — Pixel, Samsung flagships.

### Lower minSdk

- **Mass-market apps** (broad install base).
- Keep feature-detection code.
- Upgrade gradually.

Filament, Unity, Unreal — все provide fallbacks.

---

## Android 17+ (speculation)

Google likely releases:
- VPA-17 с new baseline (Vulkan 1.4 всё на device?).
- Required ray tracing?
- Mesh shader support?
- VRS (Variable Rate Shading)?

Stay tuned via AOSP CDD.

---

## Связь

[[vulkan-on-android-fundamentals]] — Vulkan context.
[[vulkan-synchronization-memory]] — synchronization2 detail.
[[vulkan-pipeline-command-buffers]] — push descriptors.
[[tile-based-rendering-mobile]] — RenderPass still important.

---

## Источники

- **Android Vulkan Profiles.** [developer.android.com/ndk/guides/graphics/android-vulkan-profile](https://developer.android.com/ndk/guides/graphics/android-vulkan-profile).
- **Android 16 Compatibility Definition.** [source.android.com/docs/compatibility/16/android-16-cdd](https://source.android.com/docs/compatibility/16/android-16-cdd).

---

## Проверь себя

> [!question]- Что даёт VPA-16 разработчику?
> Guaranteed set of Vulkan 1.3+ features на любом новом Android 16 устройстве. Single code path (no feature detection / fallback) если minSdk = 16. Faster development, cleaner code.

---

*Deep-dive модуля M12.*
