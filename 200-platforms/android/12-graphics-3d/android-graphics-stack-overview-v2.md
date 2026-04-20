---
title: "Android Graphics Stack: вертикальный срез от App до пикселя"
created: 2026-04-20
modified: 2026-04-20
type: overview
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/overview
  - level/intermediate
related:
  - "[[android-graphics-apis]]"
  - "[[surfaceflinger-and-buffer-queue]]"
  - "[[vsync-choreographer-deep]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-graphics-apis]]"
primary_sources:
  - url: "https://source.android.com/docs/core/graphics"
    title: "AOSP Graphics documentation"
    accessed: 2026-04-20
  - url: "https://android-developers.googleblog.com/2025/03/building-excellent-games-with-better-graphics-and-performance.html"
    title: "Google I/O 2024: Graphics pipeline on Android"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/graphics/architecture"
    title: "AOSP: Graphics architecture deep"
    accessed: 2026-04-20
  - url: "https://developer.android.com/games/optimize/vulkan-prerotation"
    title: "Android: Vulkan pre-rotation"
    accessed: 2026-04-20
reading_time: 22
difficulty: 4
---

# Android Graphics Stack

Обновлённый overview полного graphics stack на Android 2026. Даёт вертикальный срез от App-layer Kotlin кода до пикселя на дисплее. Этот файл — дорожная карта: каждый layer получает краткий обзор ответственности, главные dependencies, и ссылку на соответствующий deep-dive.

Понимание этого stack критично для архитектурных решений: «а где болит?» при профайлинге, «кого винить?» при странном поведении, «что можно оптимизировать?» при bottleneck.

---

## Зачем это знать

**Первое — debugging.** Bug «иконка не рисуется» может быть в 8 разных местах: app rendering code, Compose recomposition, HWUI display list, Skia drawing, OpenGL/Vulkan submission, driver issue, GPU hardware bug, SurfaceFlinger miscomposition. Без vertical map — случайное angling.

**Второе — performance targeting.** Если profiler показывает "30 ms per frame", это может быть:
- 20 ms CPU (Compose / Business logic).
- 5 ms GPU render.
- 3 ms driver overhead.
- 2 ms composition.

Каждая цифра — разный layer для оптимизации. Stack awareness направляет effort.

**Третье — vendor-agnostic design.** Qualcomm, ARM, Samsung, Imagination — все имеют own driver implementations. Bugs vendor-specific. App должно работать на всех. Knowledge stack дает framework для writing portable code.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[android-graphics-apis]] | Существующий 705-line overview — база для этого обновления |
| [[gpu-architecture-fundamentals]] | SIMT, shader cores, warps — hardware layer |

---

## Терминология

| Термин | Что |
|---|---|
| App Layer | Application code (Kotlin, Java, C++, Unity, etc.) |
| Framework Layer | AOSP UI APIs — HWUI, Skia, View system, Compose |
| API Layer | OpenGL ES / Vulkan — standardized GPU APIs |
| Driver Layer | Vendor implementation of API — translates to hardware commands |
| GPU Hardware | Silicon chip (Adreno, Mali, PowerVR, Xclipse) |
| BufferQueue | Shared memory queue for GPU buffers between processes |
| Gralloc | HAL for allocating GPU-accessible memory |
| SurfaceFlinger | System compositor service (в system_server process) |
| HWC (Hardware Composer) | Hardware block для display composition без GPU |
| Display Panel | Physical OLED/LCD, receives final framebuffer |
| HAL (Hardware Abstraction Layer) | Vendor driver interface |

---

## Историческая справка

Стек эволюционировал с 2008 года через несколько major redesigns:

- **Android 1.0–3.0 (2008–2011) — software rendering.** View system рисовал в Java Canvas (CPU-based Skia). Heavy apps struggled at 30 FPS. Scrolling list → jank.
- **Android 3.0 (2011) — HWUI introduced.** Hardware-accelerated View rendering via OpenGL ES 2.0. Opt-in, many apps broke due to drawing assumptions.
- **Android 4.0 (2011) — HWUI by default.** Hardware acceleration default for View system.
- **Android 4.1 (2012) — Project Butter.** VSYNC synchronization, triple buffering, Choreographer. Mobile UX becomes smooth.
- **Android 5.0 (2014) — RenderThread.** Drawing offloaded from main thread to dedicated RenderThread. Smoother scrolling.
- **Android 7.0 (2016) — Vulkan 1.0.** New low-level API для games, demanding apps.
- **Android 9.0 (2018) — ANGLE experimental.** GL→Vulkan translation. Initially for games.
- **Android 10 (2019) — high refresh rate support.** 90 и 120 Hz displays. VSYNC updated.
- **Android 11 (2020) — Graphics HAL 3.0.** Modernized HAL interfaces.
- **Android 12 (2021) — Variable Refresh Rate (VRR).** Display может skip frames.
- **Android 13 (2022) — HDR composition.** HWC supports HDR10, HLG.
- **Android 14 (2023) — Shader cache improvements.** Faster first-launch.
- **Android 15 (2024) — ANGLE expanded.** ANGLE may be default GL driver on некоторых devices.
- **Android 16 (2026) — VPA-16 Vulkan profile.** Required для new devices. Host Image Copy, advanced HDR composition.

Сегодняшний stack — гибрид от original 2008 идей (View + Canvas) к modern low-level (Vulkan + Compose + ANGLE).

---

## Вертикальный срез

```
┌─────────────────────────────────────────────┐
│  APP LAYER                                  │
│  • Jetpack Compose / View System / Canvas   │
│  • 3D engines: Filament / SceneView /       │
│    Godot / Unity / Unreal / NDK C++         │
│  → см. [[engine-comparison-matrix]]         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  FRAMEWORK LAYER                            │
│  • HWUI (Hardware Accelerated UI)           │
│  • Skia (2D graphics engine)                │
│  • OpenGL ES wrapper / Vulkan thin shim     │
│  → см. [[hwui-skia-hardware-rendering]]     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  API LAYER                                  │
│  • OpenGL ES 2.0 / 3.0 / 3.1 / 3.2          │
│  • Vulkan 1.0–1.4 (API 24+, most on 1.3+)   │
│  • ANGLE translation layer (GL→Vulkan)      │
│  → см. [[vulkan-on-android-fundamentals]]   │
│  → см. [[angle-and-gl-compatibility]]        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  GPU DRIVER (vendor-specific)               │
│  • Qualcomm Adreno driver                    │
│  • ARM Mali driver (Valhall, Bifrost)        │
│  • Imagination PowerVR driver                │
│  • Samsung Xclipse (RDNA-based) driver       │
│  • Implements Khronos spec, tailored to HW  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  GPU HARDWARE                                │
│  • SIMT cores (warps 16-64)                  │
│  • TBR/TBDR architecture                     │
│  • On-chip SRAM tile memory                  │
│  • RT cores (flagship)                       │
│  → см. [[gpu-architecture-fundamentals]]    │
│  → см. [[tile-based-rendering-mobile]]       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  BUFFER QUEUE / GRALLOC                      │
│  • Shared memory (ION/DMABUF)                │
│  • Producer-consumer between app & SF        │
│  → см. [[surfaceflinger-and-buffer-queue]]   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  SURFACEFLINGER                              │
│  • System compositor                         │
│  • Layer management                          │
│  • VSYNC coordination                        │
│  → см. [[vsync-choreographer-deep]]          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  HARDWARE COMPOSER (HWC)                     │
│  • Layer composition без GPU                 │
│  • Overlay planes                            │
│  • Fallback на GPU composition если нужно   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  DISPLAY HARDWARE                            │
│  • 60/90/120/144 Hz                          │
│  • VSYNC signal                              │
│  • HDR, wide color gamut (P3/BT.2020)        │
└─────────────────────────────────────────────┘
```

---

## Каждый слой — одна задача

| Layer | Responsibility | Owned by |
|---|---|---|
| App | Business logic + rendering commands | Application |
| Framework | High-level UI APIs | AOSP framework |
| API | GPU command submission | Khronos specs |
| Driver | Translates to hardware | Vendor |
| GPU | Executes | Hardware |
| BufferQueue | Memory handoff | AOSP |
| SurfaceFlinger | Composition | AOSP (system_server) |
| HWC | Hardware-accelerated composition | Vendor HAL |
| Display | Shows pixels | Hardware |

---

## Каждый слой детально

### 1. App Layer

Где начинается всё. Application code может быть:

- **Jetpack Compose (Kotlin):** declarative UI. Generates commands через HWUI + Skia.
- **View System (legacy Kotlin/Java):** imperative UI. Также via HWUI + Skia.
- **Android Canvas API:** 2D drawing. Directly via Skia.
- **3D engines:**
  - **Filament** (Google C++) — первый-class для mobile, Compose-integrable.
  - **SceneView** (Kotlin) — wrapper для AR.
  - **Godot 4 Mobile** — polymerase game engine, GDScript или C++.
  - **Unity/Unreal** — cross-platform commercial engines.
  - **NDK C++ custom** — уровень Planner 5D, полный контроль.

App typically имеет один **Surface** (окно), в которое рендерит. Games могут иметь 1 Surface (игровой), UI часто имеет 2 (3D + overlay UI).

См. [[engine-comparison-matrix]] для детального сравнения.

### 2. Framework Layer — HWUI

**HWUI (Hardware-Accelerated UI)** — Android internal library, ответственная за преобразование View hierarchy в GPU commands. Architecture:

1. **Display List:** при View.draw(), HWUI collects draw operations (draw rect, draw text, etc.) в DisplayList object.
2. **Render Thread:** separate thread, который reads display lists и submits к OpenGL/Vulkan.
3. **Skia integration:** underlying 2D engine. Skia handles text rendering, path rendering, anti-aliasing.

HWUI оптимизации:
- **RenderNode caching:** unchanged subtrees не redrawn.
- **Transform flattening:** repeated transforms combined.
- **Display list reuse:** static content не regenerates.

Compose internally использует HWUI для final commands через `CanvasImpl` (Compose Canvas → Skia).

### 3. Framework Layer — Skia

**Skia** — Google's 2D graphics engine. Used by Chrome, Android, Flutter. Written в C++.

Handles:
- Shape rendering (rect, path, bezier, text).
- Anti-aliasing (coverage-based).
- Gradient, shader, color management.
- Text layout и rendering (shaping, hinting, subpixel positioning).

Backends:
- **CPU (legacy):** Skia on CPU. Still used для некоторых paths.
- **OpenGL ES:** Skia generates GL commands.
- **Vulkan (Android 9+):** Skia может target Vulkan directly.

Skia Shader Language (**SkSL**) — own shader DSL. Transpiled к GLSL или SPIR-V.

### 4. API Layer

**OpenGL ES:** versions 2.0, 3.0, 3.1, 3.2. Stateful API (глобальное state изменяется glUniform, glBindTexture calls).

**Vulkan:** 1.0–1.4 (most devices на 1.3+). Stateless, explicit. Pipeline State Objects encapsulate all state.

**ANGLE:** Google's library translating GL ES к Vulkan (or DX). Available as optional GL driver on Android 10+. Default on некоторых Android 15+ phones (Pixel, например).

См. [[vulkan-on-android-fundamentals]], [[opengl-es-fundamentals-android]], [[angle-and-gl-compatibility]].

### 5. Driver Layer

Vendor drivers implement Khronos specs, tailored для own hardware. Major vendors:

- **Qualcomm Adreno.** Closed-source (proprietary). Strong performance, ubiquitous.
- **ARM Mali.** Reference implementation широко используется. Several architectures: Utgard (Mali-200/400), Midgard, Bifrost, Valhall. Valhall — newest (since 2019).
- **Imagination PowerVR.** Minor share сегодня, но returning с B-series (Photon).
- **Samsung Xclipse.** Basedна AMD RDNA (2022+). Hybrid IMR/tiling.
- **Intel (rare).** Некоторые Android devices используют Intel GPU.

Драйверы имеют **bugs**. Production app может encounter vendor-specific issues. Workarounds:
- Conditional feature use (checkа extensions).
- Driver version checks.
- Fallback code paths.

### 6. GPU Hardware

Физический GPU chip. Key components:

- **Shader cores (SIMT):** execute vertex, fragment, compute shaders. 16–64 wide warps.
- **Rasterizer:** converts triangles в fragments.
- **Texture units:** sample textures (filtering, LOD selection).
- **ROP (Render Output Unit):** blending, depth/stencil.
- **Tile memory:** on-chip SRAM (для TBR/TBDR).
- **L1/L2 caches:** texture, vertex, general data.
- **RT cores (flagship 2023+):** BVH traversal, ray-triangle intersection.

См. [[gpu-architecture-fundamentals]] для details.

### 7. BufferQueue / Gralloc

Between GPU output и display — buffer handoff mechanism:

- **Gralloc:** allocates GPU-accessible memory (ION/DMABUF).
- **BufferQueue:** producer-consumer queue protecting buffers.
- Triple buffering: 3 buffers rotating.

См. [[surfaceflinger-and-buffer-queue]].

### 8. SurfaceFlinger

System service compositing all windows:
- Collects Surfaces from apps.
- Composes с system UI (status bar, navigation bar, notifications).
- Delivers to HWC или GPU composition.

Scheduled by VSYNC. Offset'ы auto-tuned.

См. [[vsync-choreographer-deep]].

### 9. Hardware Composer (HWC)

Specialized display hardware для composition без GPU. Saves battery. Supports:
- Alpha blending.
- Rotation (0/90/180/270).
- Overlay planes (video, camera preview).

Limited plane count (typically 4-8). Overflow falls back to GPU composition.

### 10. Display

Физический OLED или LCD panel. Key parameters:
- **Refresh rate:** 60/90/120/144 Hz (sometimes 165 Hz premium).
- **Resolution:** 1080p/1440p/4K.
- **Color gamut:** sRGB (standard), DCI-P3 (wide), BT.2020 (ultra wide).
- **HDR support:** peak brightness, HDR10/HLG/Dolby Vision capability.

Receives final framebuffer через MIPI DSI (standard phone interface). VSYNC signal сигнализирует completion каждого refresh cycle.

---

## Where bottlenecks live

Разные performance issues — разные layers:

| Symptom | Likely Layer | Tool to diagnose |
|---|---|---|
| Slow recomposition | App / Framework (Compose) | Compose Compiler logs, Layout Inspector |
| Main thread ANR | App | CPU Profiler |
| GPU underutilized while CPU high | API / Driver overhead | AGI frame profile |
| Low FPS, GPU saturated | GPU Hardware | AGI GPU counters |
| Jank / missed VSYNC | VSYNC / SF / HWC | Perfetto, dumpsys SurfaceFlinger |
| Battery drain without high CPU | Composition / HWC fallback | dumpsys SurfaceFlinger |
| Shader stuttering | Driver shader cache | Vulkan pipeline cache stats |
| OOM on large scenes | Driver / Gralloc | Memory Profiler |

---

## Эволюция

- **Android 1.0–4.0** — Software rendering, без GPU acceleration в UI.
- **Android 4.1 (2012)** — Project Butter, HWUI, triple buffering.
- **Android 7.0 (2016)** — Vulkan 1.0 support.
- **Android 10 (2019)** — high-refresh support.
- **Android 12 (2021)** — VRR, GameMode.
- **Android 14 (2023)** — Shader cache improvements.
- **Android 15 (2024)** — ANGLE as optional GL driver.
- **Android 16 (2026)** — VPA-16 Vulkan profile обязателен для new devices, ANGLE default GL driver на some devices, Host Image Copy стандартен.

---

## Reality checks для разработчиков

### Не пишите assuming latest Android only

Device base на Android:
- API 24+ (Android 7, Vulkan 1.0+): 99% devices.
- API 26+ (Android 8): 97%.
- API 30+ (Android 11): 85%.
- API 33+ (Android 13): 60%.
- API 34+ (Android 14): 40%.
- API 36+ (Android 16): <5% (new devices only).

Target min SDK carefully. Vulkan доступен с 24, но quality driver varies — test on real devices.

### Vendor variations

Same код работает по-разному:
- **Adreno:** strict spec compliance, fewest bugs. Best Vulkan support.
- **Mali:** reference но slower updates. Some extensions lag.
- **PowerVR:** limited market share means less testing. Most bugs.
- **Xclipse:** newer, occasional RDNA-specific quirks.

Test matrix должен include хотя бы Adreno + Mali flagships + mid-range.

### Driver version matters

Driver updates deliver fixes и performance improvements. Updatable GPU drivers (Samsung, Google Pixel) получают patches separately from OS. Older phones stuck с original drivers.

App может check `VkPhysicalDeviceDriverProperties.driverVersion`. Some apps refuse run на known buggy drivers.

---

## Где найти detailed coverage

Этот overview — карта. Каждый layer разобран в отдельном deep-dive:

- GPU internals → [[gpu-architecture-fundamentals]], [[tile-based-rendering-mobile]]
- Rendering pipeline → [[rendering-pipeline-overview]]
- Low-level APIs → [[vulkan-on-android-fundamentals]], [[opengl-es-fundamentals-android]], [[angle-and-gl-compatibility]]
- System graphics → [[surfaceflinger-and-buffer-queue]], [[vsync-choreographer-deep]]
- HWUI/Skia → [[hwui-skia-hardware-rendering]] (pending)
- Engines → [[engine-comparison-matrix]], [[filament-architecture-deep]]
- Profiling → [[android-gpu-inspector-agi]], [[perfetto-and-systrace-for-graphics]]

---

## Реальные кейсы

### Planner 5D stack usage

App layer: Kotlin + собственный C++ 3D engine. Framework layer: minimal (только для UI). API: Vulkan 1.1. Driver: любой (compatibility tested). GPU: любой Android. BufferQueue: 3 buffers. SF: normal composition. HWC: 2 planes (3D + UI). Display: full range 60-120 Hz.

### IKEA Place AR stack

App: Kotlin + ARCore + custom Filament-like renderer. Framework: Compose minimal. API: Vulkan with pre-rotation. Driver: checks for ARCore support. GPU: requires ARCore-compatible. BufferQueue: camera feed via separate surface. SF: composes camera + virtual content. HWC: camera overlay + app surface. Display: active AR session.

### Compose-heavy productivity app

App: Compose only. Framework: HWUI + Skia extensively. API: Vulkan through Skia backend. Driver: mainstream. GPU: moderate. BufferQueue: single surface. SF: simple composition. HWC: 3-4 planes (app, status bar, nav bar, keyboard). Display: adaptive refresh rate.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| Compose рисует напрямую на GPU | Compose → Skia → OpenGL/Vulkan → GPU |
| Vulkan доступен на всех Android | С API 24+, но driver quality varies |
| HWC делает composition всегда | Fallback на GPU если layers exceed planes или features |
| Driver — transparent | Driver bugs — major source production issues |
| ANGLE — experimental | Default GL driver на Android 15+ на некоторых devices |

---

## Связь с существующим

Этот файл обновляет [[android-graphics-apis]] (существующий 705-строчный deep-dive) с расширенным vertical view в контексте курса [[android-graphics-3d-moc]].

Другие existing files обновлены cross-linked:
- [[android-view-rendering-pipeline]] — now links to HWUI detail.
- [[android-canvas-drawing]] — links к Skia.
- [[android-compose-internals]] — links к Compose → HWUI chain.

---

## Источники

- **AOSP Graphics documentation.** [source.android.com/docs/core/graphics](https://source.android.com/docs/core/graphics).
- **Google I/O 2024 — Graphics performance session.** [android-developers.googleblog.com](https://android-developers.googleblog.com/2025/03/building-excellent-games-with-better-graphics-and-performance.html).
- **AOSP Graphics architecture.** [source.android.com/docs/core/graphics/architecture](https://source.android.com/docs/core/graphics/architecture).
- **Vulkan on Android docs.** [developer.android.com/ndk/guides/graphics](https://developer.android.com/ndk/guides/graphics/getting-started).
- **Android Code Search.** [cs.android.com/android/platform/superproject/main/+/main:frameworks/base/libs/hwui/](https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/libs/hwui/).

---

## Проверь себя

> [!question]- Сколько layers в Android graphics stack от app code до pixel?
> 10: App, Framework (HWUI/Skia), API (GL/Vulkan), Driver, GPU Hardware, BufferQueue, SurfaceFlinger, HWC, Display Panel. Каждый может быть bottleneck.

> [!question]- Что такое HWUI и в чём роль?
> HWUI = Hardware-Accelerated UI. AOSP internal library конвертирующая View hierarchy в GPU commands через display lists. Используется в View system, Canvas API, Compose (через Skia).

> [!question]- Почему bugs бывают vendor-specific?
> Каждый vendor пишет own driver, own implementation Khronos spec. Driver code может содержать bugs специфичные для architecture. Production apps должны test на Adreno + Mali + PowerVR + Xclipse чтобы catch all.

---

## Ключевые карточки

Кто выполняет composition на Android?
?
SurfaceFlinger (system service) orchestrates, Hardware Composer (HWC) делает physical composition. Fallback — GPU composition через OpenGL ES, более battery-intensive.

---

Что такое ANGLE на Android?
?
Google's GL→Vulkan translation layer. Optional GL driver с Android 10+. Default на Pixel и некоторых phones с Android 15+. Позволяет deprecate per-vendor GL drivers, unified через Vulkan.

---

Какие 4 major vendor GPU families на Android в 2026?
?
Qualcomm Adreno, ARM Mali (Valhall, Immortalis), Imagination PowerVR (Photon B-series), Samsung Xclipse (RDNA-based). Plus Intel rare cases.

---

## Куда дальше

| Направление | Куда |
|---|---|
| GPU internals | [[gpu-architecture-fundamentals]] |
| Rendering pipeline | [[rendering-pipeline-overview]] |
| Composition | [[surfaceflinger-and-buffer-queue]] |
| VSYNC | [[vsync-choreographer-deep]] |
| Engines | [[engine-comparison-matrix]] |
| Profiling | [[android-gpu-inspector-agi]] |

---

*Overview модуля M3. Расширенный 2026-04-20.*
