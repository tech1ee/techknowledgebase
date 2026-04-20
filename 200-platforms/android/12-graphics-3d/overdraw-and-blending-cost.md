---
title: "Overdraw и blending cost на TBR mobile GPU"
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
  - level/intermediate
related:
  - "[[tile-based-rendering-mobile]]"
  - "[[blending-and-compositing]]"
  - "[[z-buffer-and-depth-testing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[tile-based-rendering-mobile]]"
reading_time: 10
difficulty: 4
---

# Overdraw и blending cost

**Overdraw** — ситуация, когда один pixel рисуется несколько раз за frame (потому что разные объекты overlap). На mobile GPU каждое написание pixel — значимый cost. Высокий overdraw = низкий FPS + high battery drain.

---

## Что считается

Overdraw factor = total fragments shaded / screen resolution pixels.

- **1× overdraw:** каждый pixel written once. Ideal.
- **2×:** average pixel written twice.
- **3-4×:** common для mobile scenes.
- **>5×:** problem — redesign needed.

---

## Источники

1. **Transparent objects** — не write depth, rendered on top of everything. Window с UI overlay + dialog + transparent animation — 4× overdraw easily.

2. **Particle systems** — тысячи overlapping billboards.

3. **Back-to-front transparent sort mandatory** — каждый transparent layer adds overdraw.

4. **Post-processing** — bloom, DOF, motion blur — каждый effect passes add overdraw.

5. **UI poor layering** — nested semi-transparent backgrounds.

---

## Detection

### Android GPU Inspector (AGI)

AGI → Frame Profiler → overdraw visualization. Color-coded: blue = 1×, green = 2×, red = 3×+.

### Debug GPU overdraw

Android dev options → "Debug GPU overdraw" (system-wide):
- Blue = 1×.
- Light blue/green = 2×.
- Yellow/red = 4×+.

Quick visual check.

---

## Mitigation

### 1. Draw opaque front-to-back

Front-to-back ordering → early-Z (см. [[z-buffer-and-depth-testing]]) rejects occluded fragments без shader run. Major savings.

### 2. Sort transparents back-to-front

Necessary для correct blending. Can't reorder.

### 3. Reduce transparent objects

Each transparent — cost. Questions:
- Can dialog use opaque background?
- Does animation really need 100 particles, or 20 enough?

### 4. Pre-multiply alpha

Сам blending cost slightly cheaper (см. [[blending-and-compositing]]).

### 5. Alpha-to-coverage для masked transparency

Вместо alpha blending для cutout (e.g. leaves), use alpha test + MSAA. Preserves early-Z.

### 6. Single-pass blending

Combine several transparent layers в один shader pass. One fragment execution instead of N.

### 7. Reduce post-processing

Each post-pass = full screen overdraw. Skip unnecessary effects (bloom только для hero moments, etc.).

---

## TBR advantage

На TBR (Mali, Adreno) — blending читает/writes in tile memory, cost mainly fragment shader executions. На IMR (desktop NVIDIA) — ROP reads/writes в DRAM, much more expensive.

TBDR (PowerVR, Apple AGX) — hidden surface removal **before** fragment shader. Zero overdraw для opaque. Massive advantage.

---

## Budget guidelines

Typical frame budget 16 ms (60 FPS). Fragment shader ALU budget:
- Adreno 740: ~30 GFLOPS available.
- Fragment shader 50 ALU × 2M pixels × 3× overdraw = 300 MFLOPS. OK.
- 50 ALU × 2M × 6× overdraw = 600 MFLOPS. Tight.

Goal: keep overdraw ≤ 3× для steady 60 FPS на mid-range.

---

## Real examples

### Planner 5D room render

- Floor: 1× (opaque, back).
- Walls: 1× each side (opaque, sorted).
- Furniture: 1× (opaque, instanced).
- Glass stuff (tables): transparent, 1× extra.
- Shadows: pre-multiplied, 1× extra в некоторых регионах.

Total: 2-3× в среднем. Acceptable.

### Fire particle effect

100 particles × overlapping → 20-50× в core of fire. Mitigation — smaller particles, fewer counts.

---

## Связь

[[tile-based-rendering-mobile]] — TBR blending cost.
[[blending-and-compositing]] — blending theory.
[[z-buffer-and-depth-testing]] — early-Z for overdraw reduction.
[[frustum-culling]] — cull out-of-view первый.

---

## Источники

- **ARM: Optimizing Mobile Graphics.** Best practices.
- **Akenine-Möller et al. (2018). RTRT 4.**

---

## Проверь себя

> [!question]- Почему sort opaque front-to-back, а transparent back-to-front?
> Opaque front-to-back: early-Z skips occluded fragments → savings. Transparent back-to-front: correct blending — each layer sees all behind. Opposite orderings для opposite reasons.

---

*Deep-dive модуля M10.*
