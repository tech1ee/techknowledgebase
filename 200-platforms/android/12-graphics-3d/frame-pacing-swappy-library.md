---
title: "Android Frame Pacing Library (Swappy)"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[vsync-choreographer-deep]]"
  - "[[surfaceflinger-and-buffer-queue]]"
  - "[[thermal-throttling-and-adpf]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vsync-choreographer-deep]]"
primary_sources:
  - url: "https://developer.android.com/games/sdk/frame-pacing"
    title: "Android Frame Pacing (Swappy)"
    accessed: 2026-04-20
  - url: "https://github.com/android/games-samples/tree/main/agdk/frame_pacing"
    title: "Swappy sample code"
    accessed: 2026-04-20
reading_time: 10
difficulty: 5
---

# Android Frame Pacing Library

**Swappy** — Google's library для stable frame pacing. Wraps OpenGL `eglSwapBuffers` / Vulkan `vkQueuePresent`. Automatically handles VSYNC timing, adaptive refresh rate, thermal throttling, wait/presentation mode selection.

Result: consistent inter-frame intervals (jank reduction), даже когда app renders faster than display.

---

## Зачем

Problem: app renders 70-120 FPS, но display только 60 Hz. Без framerate throttling:
- Tearing (fragments multiple frames shown).
- Inconsistent frame intervals (16 ms, 16 ms, 8 ms, 24 ms...).
- Battery drain от unnecessary rendering.

Solution: sync presentation to VSYNC with correct timing.

Vulkan has `VK_PRESENT_MODE_FIFO_KHR` (VSYNC-locked). But doesn't handle:
- Variable refresh rate devices (60/90/120 Hz adaptive).
- Thermal throttling → downgrade to 30 FPS smoothly.
- Detect слow frames and adjust automatically.

Swappy handles all that.

---

## Integration

### OpenGL ES

```cpp
#include <swappy/swappyGL.h>

// One-time init
SwappyGL_init(env, activity);

// Set target refresh rate (optional)
SwappyGL_setSwapIntervalNS(16_666_666);  // 60 Hz

// Instead of eglSwapBuffers
while (running) {
    renderFrame();
    SwappyGL_swap(display, surface);  // replaces eglSwapBuffers
}
```

### Vulkan

```cpp
#include <swappy/swappyVk.h>

SwappyVk_init(env, activity);

// Create swapchain normally via vkCreateSwapchainKHR

SwappyVk_setWindow(device, swapchain, nativeWindow);
SwappyVk_setSwapIntervalNS(swapchain, 16_666_666);

// Instead of vkQueuePresentKHR
while (running) {
    recordCommands();
    vkQueueSubmit(queue, &submit, fence);
    SwappyVk_queuePresent(queue, &presentInfo);
}
```

---

## Features

### Auto refresh rate

Device имеет 60 Hz и 120 Hz modes. Swappy chooses optimal based on app render time:
- Render < 8.3 ms → 120 Hz.
- Render 8.3–16.6 ms → 60 Hz.
- Render > 16.6 ms → 30 Hz.

User gets smooth frame pacing even without target-tuning.

### Thermal-aware

Detects thermal state через `PowerManager.THERMAL_STATUS_*`. Proactively reduces target refresh rate when throttling imminent (см. [[thermal-throttling-and-adpf]]).

### Automatic frame timing

Measures actual render time per frame, adjusts expected VSYNC offset. Compensates для varying render times.

### Fallback

Gracefully handles edge cases: device rotation mid-frame, composition fallback, surface recreation.

---

## Metrics

Perfetto traces show Swappy timing:
- `swap_interval_ns` — target interval.
- `actual_swap_time` — measured.
- `vsync_offset` — latency to VSYNC.

Analyze если frame drops — look for `actual > target`.

---

## Когда использовать

✅ **Games** — critical.
✅ **Video playback** — smooth playback.
✅ **Any 60+ FPS custom rendering** — recommended.
✅ **High-end AR apps** — reduced jank.

❌ **Simple 2D UI** (Compose/View) — system handles through Choreographer. Swappy adds overhead. Not needed.

---

## Интеграция с engines

- **Unity:** Unity Adaptive Performance package uses Swappy underneath.
- **Unreal:** Unreal 5 Mobile includes Swappy.
- **Godot:** manual integration (few lines).
- **Filament:** optional; community integrations available.

---

## Real numbers

Before Swappy:
- Frame intervals: mean 16.7 ms, stddev 4 ms.
- Jank events per minute: 8-12.

After Swappy:
- Mean 16.7 ms, stddev 1 ms.
- Jank events: 0-1.

Meaningful improvement.

---

## Связь

[[vsync-choreographer-deep]] — Swappy builds on top of Choreographer.
[[surfaceflinger-and-buffer-queue]] — SwapChain interaction.
[[thermal-throttling-and-adpf]] — cooperative.
[[vulkan-on-android-fundamentals]] — Vulkan-specific Swappy.

---

## Источники

- **Android Frame Pacing.** [developer.android.com/games/sdk/frame-pacing](https://developer.android.com/games/sdk/frame-pacing).
- **Sample code.** [github.com/android/games-samples](https://github.com/android/games-samples/tree/main/agdk/frame_pacing).

---

## Проверь себя

> [!question]- Swappy vs просто `VK_PRESENT_MODE_FIFO_KHR`?
> FIFO — plain VSYNC-lock. Swappy adds: adaptive refresh rate selection, thermal awareness, auto-tuning VSYNC offset, frame time monitoring. Strongly recommended для games / heavy 3D apps.

---

*Deep-dive модуля M12.*
