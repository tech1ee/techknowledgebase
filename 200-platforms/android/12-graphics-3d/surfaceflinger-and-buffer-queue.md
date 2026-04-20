---
title: "SurfaceFlinger и BufferQueue: как Android композитит окна"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/android-internals
  - type/deep-dive
  - level/advanced
related:
  - "[[android-window-system]]"
  - "[[vsync-choreographer-deep]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-window-system]]"
  - "[[android-view-rendering-pipeline]]"
primary_sources:
  - url: "https://source.android.com/docs/core/graphics"
    title: "AOSP: Graphics architecture overview"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/graphics/surfaceflinger-windowmanager"
    title: "AOSP: SurfaceFlinger and WindowManager"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/graphics/arch-bq-gralloc"
    title: "AOSP: BufferQueue and gralloc"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/graphics/implement-hwc"
    title: "AOSP: Hardware Composer HAL"
    accessed: 2026-04-20
reading_time: 22
difficulty: 6
---

# SurfaceFlinger и BufferQueue

Между `vkQueuePresentKHR` в Vulkan-приложении и пикселями, загорающимися на экране Android-телефона, стоит системный сервис **SurfaceFlinger** и механизм **BufferQueue**. Ни один кадр не попадает на дисплей минуя их. Понимание этой машинерии — предпосылка для грамотного использования VSYNC, frame pacing, и объяснения, почему одно и то же приложение работает различно в portrait/landscape, fullscreen/split-screen, foreground/background.

Этот deep-dive разбирает: archeology SurfaceFlinger (с 2008), роль BufferQueue producer/consumer, Gralloc, Hardware Composer (HWC), triple buffering, и interaction с [[tile-based-rendering-mobile|TBR]].

---

## Зачем это знать

**Первый production-сценарий.** Приложение рендерит в 120 FPS, но на дисплее видно 60. Проблема — refresh rate дисплея 60 Hz, SurfaceFlinger сбрасывает лишние frames. Fix — либо снизить internal rendering до matching framerate (экономия battery), либо правильно настроить Swappy (Android Frame Pacing Library).

**Второй.** Три последовательных frames показывают одну и ту же картинку, потом сразу две новые. Это **frame pacing jank** — VSYNC timing нарушен, SurfaceFlinger не получил свежий buffer вовремя.

**Третий.** В PiP режиме app видит странный resize every several frames — SurfaceFlinger меняет target surface geometry.

---

## Prerequisites

- [[android-window-system]] — Window, Surface, SurfaceView context.
- [[android-view-rendering-pipeline]] — что происходит с View.invalidate до отправки buffer в SurfaceFlinger.

---

## Терминология

| Термин | Что |
|---|---|
| SurfaceFlinger | System service (C++, system_server process), композитит все windows на экране |
| BufferQueue | IPC-based queue between "producer" (app) и "consumer" (SurfaceFlinger) |
| Producer | Приложение, которое рендерит в buffer |
| Consumer | SurfaceFlinger, забирающий buffer для композиции |
| Gralloc | Hardware abstraction для memory allocation buffer'ов |
| HAL (Hardware Abstraction Layer) | Vendor-specific driver |
| Hardware Composer (HWC) | Hardware block for compositing layers без GPU |
| Layer | Один surface для compositing (app window, status bar, navigation) |
| VSYNC | Vertical Synchronization signal от display, трриггер для нового frame |
| Triple buffering | 3 buffers в rotation: current display, next, app writing |
| FBO (Framebuffer Object) | GPU framebuffer, в который приложение рендерит |

---

## Историческая справка

- **2008 — Android 1.0.** Первый SurfaceFlinger, простой compositor.
- **2012 — Android 4.1 (Jelly Bean).** Project Butter — VSYNC syncronization, Choreographer, triple buffering. Массовое улучшение smoothness.
- **2015 — Android 6.0.** Hardware Composer HAL 2.0.
- **2019 — Android 10.** Display refresh rates up to 120 Hz.
- **2021 — Android 12.** Improved frame pacing, 120 Hz variable refresh rate support.
- **2024 — Android 15.** Adaptive refresh, Jelly Bean-quality тех времен становится default.
- **2026 — Android 16.** Full support for 144 Hz+ displays, VPA-16 Vulkan profile, improved multi-display.

---

## Архитектура

```
┌──────────────────────────────────────────────┐
│  Application Process                         │
│  ┌─────────────────────────────────────────┐ │
│  │ App UI + GPU Rendering                  │ │
│  │ (Compose / View / Vulkan / OpenGL ES)   │ │
│  └──────────┬──────────────────────────────┘ │
│             │ Writes to buffer                │
│             ▼                                 │
│  ┌─────────────────────────────────────────┐ │
│  │ BufferQueue (Producer side)             │ │
│  │  • Gralloc-allocated ION/DMABUF memory  │ │
│  │  • Dequeue → write → queue              │ │
│  └──────────┬──────────────────────────────┘ │
└─────────────┼────────────────────────────────┘
              │  Binder IPC
              ▼
┌──────────────────────────────────────────────┐
│  system_server process                       │
│  ┌─────────────────────────────────────────┐ │
│  │ SurfaceFlinger                          │ │
│  │  • N BufferQueues (one per Surface)     │ │
│  │  • Layers ordered by Z                  │ │
│  │  • VSYNC-driven scheduling              │ │
│  └──────────┬──────────────────────────────┘ │
│             │ Choose composition strategy    │
│             ▼                                 │
│  ┌─────────────────────────────────────────┐ │
│  │ Hardware Composer HAL                   │ │
│  │  • HWC delta layers HARDWARE            │ │
│  │  • Fallback: GPU composition            │ │
│  └──────────┬──────────────────────────────┘ │
└─────────────┼────────────────────────────────┘
              │
              ▼
       Display (OLED/LCD)
```

### BufferQueue producer-consumer

BufferQueue — Android-specific shared buffer protocol. Между app и SurfaceFlinger:

1. **Allocate.** Application запрашивает buffer из Gralloc (через BufferQueue, lazy).
2. **Dequeue.** Producer получает buffer slot. `IGraphicBufferProducer.dequeueBuffer()`.
3. **Fill.** App рендерит в buffer (GPU через EGL_IMAGE или Vulkan swapchain).
4. **Queue.** Producer отдаёт buffer consumer'у. `queueBuffer()` с timestamp и VSYNC requirement.
5. **Acquire.** SurfaceFlinger берёт buffer из очереди. `acquireBuffer()`.
6. **Compose + Display.** SurfaceFlinger композитит этот layer вместе с остальными.
7. **Release.** SurfaceFlinger отпускает buffer back в pool. `releaseBuffer()`.

Triple buffering: 3 buffers в ротации. Producer может работать на следующем кадре, пока consumer показывает текущий, а третий — в транзите.

### Gralloc

Abstraction over memory allocation. Каждый vendor implements Gralloc HAL. Allocates:
- **Shared memory** (ION, DMA-BUF on Android 10+).
- **Correct alignment** для GPU access.
- **Correct format** (RGBA8, RGB565, YUV для video, AFBC-compressed).

Gralloc descriptor хранит: width, height, format, usage flags. Passed через Binder IPC.

### Hardware Composer (HWC)

Специальное hardware на phone SoC для композиции layers без использования GPU. Input — N layers (app windows, system UI, wallpaper), output — single framebuffer for display.

**HWC advantages:**
- No GPU wake-up for simple composition (экономия battery).
- No extra framebuffer allocation (direct composition).
- Overlay planes support (video directly to display без CPU/GPU involvement).

**HWC limitations:**
- Limited to certain formats, blending modes.
- SurfaceFlinger falls back to GPU composition if HWC can't handle (unusual blending, rotation, complex transformations).

**VPA-16 in Android 16** requires all devices to support advanced HWC features (up to 4 hardware overlay planes, HDR, variable refresh rate).

### VSYNC

Display sends VSYNC signal каждые refresh interval (60 Hz → 16.67 ms). SurfaceFlinger wakes up at VSYNC, composes, presents. App Choreographer also receives VSYNC — starts new frame processing.

Three timings:
- **Display VSYNC** (refresh signal).
- **SF VSYNC** (offset, when SurfaceFlinger wakes).
- **App VSYNC** (offset, when app wakes).

Proper offsets give app time to render before SF time. Android auto-tunes offsets based on hardware.

---

## Уровень 1 — начинающим

Представьте почту: ваше приложение — отправитель, экран телефона — получатель. Между ними курьерская служба (SurfaceFlinger). Вы складываете готовый конверт (нарисованный frame) в ящик (BufferQueue), курьер каждые 16 миллисекунд забирает всё из ящиков разных отправителей (ваш app + UI + статус бар), собирает в одну посылку и доставляет на экран.

Если вы рисуете слишком медленно, курьер приходит и ящик пустой — экран показывает старую картинку (frame drop). Если рисуете слишком быстро, ящик переполняется — курьер выбрасывает старое. Synchronization этого процесса и есть задача VSYNC + Choreographer + BufferQueue.

SurfaceFlinger ещё и умеет экономить батарею: когда layers простые (статичный UI + немного графики), он использует hardware compositor (HWC) без задействования GPU. Это major reason why идол-экран телефона разряжается медленнее чем игровой.

---

## Уровень 2 — для студента

### BufferQueue через Vulkan swapchain

```cpp
VkSwapchainCreateInfoKHR swapchainInfo = {
    .surface = surface,
    .minImageCount = 3,  // triple buffering
    .imageFormat = VK_FORMAT_R8G8B8A8_UNORM,
    .imageExtent = { width, height },
    .presentMode = VK_PRESENT_MODE_FIFO_KHR,  // VSYNC-locked
    ...
};
vkCreateSwapchainKHR(device, &swapchainInfo, nullptr, &swapchain);
```

`VK_PRESENT_MODE_FIFO_KHR` == queue behind VSYNC (буферизация). `MAILBOX_KHR` = newest frame always displayed (tears through old). `IMMEDIATE_KHR` = tearing possible.

For standard apps — FIFO. For high-FPS games — MAILBOX.

### Frame pacing with Swappy

```cpp
SwappyGL_init(env, activity);
// в render loop:
SwappyGL_swap(display, surface);  // замена eglSwapBuffers
```

Swappy Library мониторит VSYNC timing и автоматически throttle, если app render faster than display.

---

## Уровень 3 — для профессионала

### HWC fallback triggers

SurfaceFlinger падает на GPU composition если layer:
- Has unusual blending (custom shader).
- Requires rotation не в 0/90/180/270.
- Format not supported by HWC (некоторые YUV variants).
- More layers than HWC planes (обычно 4).

Watch AGI trace: если GPU utilization высокая при простой scene, возможно fallback. Reduce layer count, use standard rotations.

### Variable Refresh Rate (VRR)

Android 12+ supports VRR. Display may skip refresh cycles если no new frame. Battery-saving для mostly-static UI.

App должно correctly set `SurfaceControl.setFrameRate()` или Vulkan `VK_KHR_display_native_hdr` → display drives at requested rate.

### VPA-16 на Android 16

Обязательные features для new devices:
- 4 hardware overlay planes.
- HDR composition via HWC.
- 120 Hz+ refresh support.
- Adaptive refresh rate.
- Host Image Copy для ускорения swapchain acquire.

---

## Реальные кейсы

### Planner 5D — правильный swapchain setup

`VK_PRESENT_MODE_FIFO_KHR`, 3 swapchain images, pre-rotation — стандартный setup. Battery-friendly.

### IKEA Place — AR session с camera

ARCore camera preview идёт через отдельный surface. SurfaceFlinger композит 2 layers: camera + virtual content. HWC может справиться, экономя GPU cycles.

### Games с 120 FPS

Games запрашивают `VK_PRESENT_MODE_MAILBOX_KHR` + `setFrameRate(120.0f)`. SurfaceFlinger VSYNC-lock на 120 Hz display.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Все frames от app попадают на display | Frame drops — нормально при slow rendering или VSYNC miss |
| GPU всегда делает composition | HWC handles большинство case бесплатно |
| MAILBOX present mode лучше FIFO | MAILBOX tears latest frame; battery-heavy. FIFO для normal apps |
| SurfaceFlinger только композитит | Также делает scheduling, VSYNC distribution, HWC coordination |

---

## Подводные камни

### Ошибка 1: Неправильный present mode

**Как избежать:** FIFO для большинства apps. MAILBOX — только для 120+ FPS games. IMMEDIATE — tests only.

### Ошибка 2: Too many layers

**Как избежать:** ограничить количество Surfaces. HWC обычно handles 4; больше — GPU fallback.

### Ошибка 3: Ignoring pre-rotation

**Как избежать:** apply pre-rotation в Vulkan vertex shader, избежать дополнительной composition work.

---

## Связь с другими темами

[[android-window-system]] — Surface as producer endpoint.
[[vsync-choreographer-deep]] — VSYNC distribution в app.
[[android-view-rendering-pipeline]] — как View.invalidate превращается в buffer queued.
[[tile-based-rendering-mobile]] — TBR generates swapchain buffer.
[[vulkan-on-android-fundamentals]] — Vulkan swapchain API.
[[frame-pacing-swappy-library]] — Swappy для frame pacing.

---

## Источники

- **AOSP Graphics architecture.** [source.android.com/docs/core/graphics](https://source.android.com/docs/core/graphics).
- **AOSP SurfaceFlinger and WindowManager.** [source.android.com/docs/core/graphics/surfaceflinger-windowmanager](https://source.android.com/docs/core/graphics/surfaceflinger-windowmanager).
- **AOSP BufferQueue and gralloc.** [source.android.com/docs/core/graphics/arch-bq-gralloc](https://source.android.com/docs/core/graphics/arch-bq-gralloc).
- **AOSP HWC HAL.** [source.android.com/docs/core/graphics/implement-hwc](https://source.android.com/docs/core/graphics/implement-hwc).
- **Android Project Butter (2012) talk.** Google I/O 2012, introduction of VSYNC synchronization.

---

## Проверь себя

> [!question]- Что такое BufferQueue?
> IPC-based queue между producer (app) и consumer (SurfaceFlinger). Обычно 2-3 buffers rotation (triple buffering). App dequeue → write → queue; SF acquire → compose → release.

> [!question]- Что делает Hardware Composer?
> Specialized hardware block для compositing layers без использования GPU. Экономит battery. Supports overlay planes (video, UI). Fallback на GPU composition если features don't match.

> [!question]- Когда используется FIFO vs MAILBOX present mode?
> FIFO — стандарт, VSYNC-synchronized, battery-friendly. MAILBOX — для high-FPS games где latest frame должен display независимо от VSYNC tearing.

---

## Ключевые карточки

Сколько buffers в стандартном triple buffering?
?
3: current display, next queued, app writing. Rotation синхронизирована с VSYNC.

---

Что такое Gralloc?
?
Hardware abstraction для buffer memory allocation. Vendor-specific HAL (Qualcomm, ARM, etc.). Allocates ION/DMABUF с правильным alignment для GPU.

---

Зачем SurfaceFlinger отдельный процесс?
?
Security и stability. App crash не влияет на composition. SurfaceFlinger ownership каждого buffer — через Binder IPC. Также унифицированный scheduling для всех apps.

---

## Куда дальше

| Направление | Куда |
|---|---|
| VSYNC mechanism | [[vsync-choreographer-deep]] |
| Window system | [[android-window-system]] |
| Frame pacing | [[frame-pacing-swappy-library]] |
| Vulkan swapchain | [[vulkan-on-android-fundamentals]] |

---

*Deep-dive модуля M3.*
