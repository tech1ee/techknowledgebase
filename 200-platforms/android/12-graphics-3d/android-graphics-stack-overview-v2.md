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
reading_time: 12
difficulty: 3
---

# Android Graphics Stack

Обновлённый overview полного graphics stack на Android 2026. Даёт вертикальный срез от App-layer Kotlin кода до пикселя на дисплее. Каждый layer — ссылки на deep-dive.

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

## Где найти detailed coverage

Этот overview — карта. Каждый layer разобран в отдельном deep-dive:

- GPU internals → [[gpu-architecture-fundamentals]], [[tile-based-rendering-mobile]]
- Rendering pipeline → [[rendering-pipeline-overview]]
- Low-level APIs → [[vulkan-on-android-fundamentals]], [[opengl-es-fundamentals-android]], [[angle-and-gl-compatibility]]
- System graphics → [[surfaceflinger-and-buffer-queue]], [[vsync-choreographer-deep]]
- HWUI/Skia → [[hwui-skia-hardware-rendering]] (pending)
- Engines → [[engine-comparison-matrix]], [[filament-architecture-deep]]
- Profiling → [[android-gpu-inspector-agi]]

---

## Связь с существующим

Этот файл обновляет [[android-graphics-apis]] (существующий 705-строчный deep-dive) с расширенным vertical view в контексте курса [[android-graphics-3d-moc]].

---

## Источники

- **AOSP Graphics documentation.** [source.android.com/docs/core/graphics](https://source.android.com/docs/core/graphics).
- **Google I/O 2024 — Graphics performance session.** [android-developers.googleblog.com](https://android-developers.googleblog.com/2025/03/building-excellent-games-with-better-graphics-and-performance.html).

---

*Overview модуля M3.*
