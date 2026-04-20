---
title: "Android GPU Inspector (AGI): главный инструмент профилирования"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/profiling
  - type/deep-dive
  - level/intermediate
related:
  - "[[perfetto-and-systrace-for-graphics]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[thermal-throttling-and-adpf]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gpu-architecture-fundamentals]]"
primary_sources:
  - url: "https://developer.android.com/agi"
    title: "Android GPU Inspector official"
    accessed: 2026-04-20
  - url: "https://developer.android.com/agi/start"
    title: "AGI Quickstart"
    accessed: 2026-04-20
  - url: "https://developer.android.com/agi/frame-trace/frame-profiler"
    title: "AGI Frame Profiler"
    accessed: 2026-04-20
reading_time: 12
difficulty: 4
---

# Android GPU Inspector (AGI)

## Историческая справка

GPU profiling инструменты эволюция:

- **Early 2010s — vendor-specific tools.** Adreno Profiler (Qualcomm), Mali Graphics Analyzer (ARM), PVRTune (Imagination). Каждый workable только для своего vendor.
- **2018 — Google announces Android GPU Inspector.** Cross-vendor, unified.
- **2020 — AGI 1.0 released.** Initially limited к Pixel phones.
- **2022 — AGI 2.0.** Support Adreno + Mali + PowerVR.
- **2023 — Vulkan support mature.**
- **2024 — AGI integration с Android Studio.**
- **2026 — current,** de-facto standard.

Before AGI, cross-vendor profiling требовал switching tools для different devices. AGI unified experience, accelerated Android graphics development.

Alternatives в 2026:
- **RenderDoc** — open source frame debugger. Weaker на Android, stronger на desktop.
- **NSight Mobile** — NVIDIA's mobile profiler (rarely applicable на Android).
- **Vendor-specific** — still exist, deeper native insights, но harder to use.



**AGI** — Google's primary GPU profiling tool на Android. Supports Adreno (Qualcomm), Mali (ARM), PowerVR (Imagination). Features: frame profile (per-draw call timing), system profile (CPU/GPU correlation), shader performance analysis.

Tool de-facto стандарт для Android graphics profiling в 2026.

---

## Установка

1. Download [developer.android.com/agi](https://developer.android.com/agi).
2. Available для Windows/macOS/Linux.
3. Also available in Android Studio Electric Eel+ как integration.

Device requirements:
- Developer options enabled.
- USB debugging on.
- GPU profiling on (in dev options).

---

## Три режима

### Frame Profiler

Per-draw call analysis. Shows:
- Draw time per call.
- Shader ALU utilization.
- Memory reads/writes.
- Tile memory usage (TBR).
- State changes.

Use case: find slow draws, optimize hot paths.

### System Profiler

CPU/GPU/memory/thermal timeline:
- App thread activity.
- Choreographer timing.
- VSYNC.
- Thermal throttling events.
- Memory usage.

Use case: find jank causes, synchronization issues, thermal problems.

### Shader Performance

Per-shader analysis:
- ALU count.
- Memory fetches.
- Branch divergence indicators.
- Register pressure.

Use case: optimize specific shaders after identifying bottleneck.

---

## Basic workflow

1. Launch AGI.
2. Connect device via USB.
3. Select app (must be debuggable).
4. Choose Frame Profile or System Profile.
5. Launch app, capture frame(s).
6. Analyze.

---

## Key metrics (frame profile)

### Per-draw

- **Time** — duration GPU executing (microseconds).
- **Vertices** — vertex count processed.
- **Fragments** — fragments generated.
- **Bandwidth read/write** — memory IO.
- **Shader invocations** — actual runs (may differ from theoretical).

Target: total frame GPU time < 16 ms (60 FPS). If exceeded, identify longest draws → optimize.

### Per-frame

- **Total GPU time** — main metric.
- **Vertex stage %** — should be low (< 25%) для most apps.
- **Fragment stage %** — often dominant.
- **Bandwidth** — DRAM reads/writes per frame.

---

## Warp occupancy

Shows actual SIMT utilization.

- **100%** — GPU fully utilized, all warps active.
- **50%** — half warps waiting (memory, register pressure).
- **25%** — heavy underutilization — investigate.

Low occupancy causes:
- Register pressure (shader uses too many registers).
- Memory stalls (bad access patterns).
- Wave divergence.

---

## Shader analysis

AGI opens shader в editor, shows:
- GLSL source (if available).
- Compiled SPIR-V.
- GPU machine code (native ISA).
- ALU count, memory ops per invocation.

Helpful для:
- Identifying long instructions.
- Finding redundant computations.
- Optimizing math.

---

## Common patterns

### High fragment time

Investigate:
- Overdraw (blur, particles).
- Expensive fragment shader (PBR с complex IBL).
- Many texture samples.

Mitigations: reduce overdraw ([[overdraw-and-blending-cost]]), simplify shader, mipmap carefully.

### High vertex time

Investigate:
- Too many vertices (no LOD).
- Complex vertex shader (skinning, tessellation).

Mitigations: LOD ([[level-of-detail-lod]]), simpler vertex math, GPU instancing.

### High bandwidth

Investigate:
- Non-TBR-friendly render pass design.
- Large textures uncompressed.
- Many swapchain images.

Mitigations: proper load/store ops ([[tile-based-rendering-mobile]]), KTX2 compression, fewer swapchain images.

### Warp divergence

Investigate в shader:
- `if-else` на hot paths.
- Varying data between pixels.

Mitigations: branchless code, specialization constants.

---

## Vendor counters

AGI exposes vendor-specific:
- **Adreno:** `Prefetch Tag Misses`, `Resolve Fetches`, `Depth Test Fails`.
- **Mali:** `AFBC Compression Ratio`, `Tile Fetches`, `Early Z Tests`.
- **PowerVR:** `Parameter Buffer Usage`, `HSR Rate`.

Use for deep vendor-specific debugging.

---

## Integration с Vulkan validation

AGI работает с validation layers. Enable в debug builds:

```cpp
std::vector<const char*> layers = {"VK_LAYER_KHRONOS_validation"};
```

Catches misuse (incorrect barriers, unbound descriptors, etc.) before it becomes performance issue.

---

## Real-world story

"Planner 5D FPS drop на Samsung Galaxy A55":
1. Run AGI.
2. Frame profile: fragment time 25 ms (over 16 budget).
3. Drill down: one draw takes 12 ms — sofa с complex PBR shader.
4. Shader analysis: 80 ALU, high register pressure.
5. Fix: simplify fragment shader, use mediump для normals, reduce texture samples.
6. Re-profile: 15 ms frame. FPS stable 60.

Standard diagnosis pattern.

---

## Связь

[[perfetto-and-systrace-for-graphics]] — alternative system-level profiling.
[[gpu-architecture-fundamentals]] — understanding warps/occupancy.
[[thermal-throttling-and-adpf]] — thermal info in AGI system profile.
[[shader-compilation-jitter-mitigation]] — jitter visible в AGI timeline.

---

## Источники

- **AGI official.** [developer.android.com/agi](https://developer.android.com/agi).
- **AGI Quickstart.** [developer.android.com/agi/start](https://developer.android.com/agi/start).
- **AGI Frame Profiler.** [developer.android.com/agi/frame-trace/frame-profiler](https://developer.android.com/agi/frame-trace/frame-profiler).

---

## Проверь себя

> [!question]- Когда использовать Frame Profile vs System Profile в AGI?
> Frame Profile — per-draw-call GPU analysis (find slow draws, optimize shaders). System Profile — CPU/GPU correlation over time (find jank, VSYNC issues, thermal). Обычно — System сначала to locate problem frames, затем Frame для drill-down.

---

*Deep-dive модуля M11.*
