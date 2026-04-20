---
title: "Occlusion culling: не рендерить то, что скрыто другими объектами"
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
  - "[[frustum-culling]]"
  - "[[z-buffer-and-depth-testing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[frustum-culling]]"
reading_time: 10
difficulty: 5
---

# Occlusion culling

**Occlusion culling** — skip rendering объектов, которые скрыты другими (ближе к камере) objects. Frustum culling убирает out-of-view; occlusion culling убирает in-view но occluded.

На mobile GPU — **не всегда win**. TBDR (PowerVR, Apple AGX) уже делает per-tile occlusion бесплатно. Mali/Adreno — могут benefit но overhead self-test sometimes превышает savings.

---

## Techniques

### 1. Hardware occlusion queries

OpenGL / Vulkan support. Render bounding box с disabled color write, check query result — passed samples > 0 = visible.

```cpp
// Issue query
vkCmdBeginQuery(cmd, queryPool, queryIndex, 0);
// draw bounding box
vkCmdEndQuery(cmd, queryPool, queryIndex);

// Later — check
vkGetQueryPoolResults(device, queryPool, queryIndex, 1, sizeof(uint64_t), &result, ...);
if (result > 0) {
    // visible
}
```

Problem: one-frame latency. Result available после render finished.

### 2. Hi-Z / coarse Z

Hardware maintains hierarchical depth buffer. Testing bounding box against max Z in tile — если all pixels behind → cull.

Adreno и Mali implement Hi-Z transparently. Programmer doesn't control directly, but:
- Draw front-to-back для maximize Hi-Z effectiveness.
- Use pre-Z pass (render depth only first).

### 3. Software occlusion culling

CPU-side rasterize simplified occluder meshes в coarse depth buffer, test other objects. Используется в Unreal Engine, some mobile engines.

Cost: CPU-bound, но может be fast enough. Win — zero GPU wait.

### 4. Portal culling

Scene divided в rooms connected через portals (doorways). Камера в room A → render A. Looking through portal to B → render B. Не-connected rooms never rendered.

Used в architectural visualizations, FPS games с separate rooms. Planner 5D-type apps могут benefit для multi-room floor plans.

---

## На mobile — когда оправдано

**Чистый TBR (Mali, Adreno):**
- Hardware Hi-Z уже снижает overdraw cost.
- Software occlusion culling на CPU добавляет overhead.
- Occlusion queries have frame latency.
- Обычно **не worth it** для most apps.

**Кейсы где стоит:**
- Scene с expensive shaders (PBR + shadows) — savings large.
- Long-running sessions где thermal matters.
- Scenes с clear occlusion structure (rooms with walls).

**TBDR (PowerVR, Apple AGX):**
- Hardware already делает perfect occlusion.
- Software culling — redundant.

---

## Pre-Z pass trick

Alternative — **pre-Z pass**:

1. **Pass 1:** render scene с depth только (no color, no complex shader). Fast.
2. **Pass 2:** render scene с full shaders. Early-Z автоматически rejects occluded fragments.

Cost: 2 vertex passes. Gain: ~30-50 % снижение fragment executions.

Worth if fragment shaders expensive.

---

## Реальное использование

**Filament:** не делает software occlusion. Relies on TBR hardware + pre-Z pass.

**Unity:** umbra-based occlusion (bake offline для static).

**Planner 5D-class:** фокус на frustum culling + LOD, не occlusion. Scenes обычно не have heavy occlusion.

---

## Связь

[[frustum-culling]] — prerequisite.
[[z-buffer-and-depth-testing]] — early-Z relationship.
[[tile-based-rendering-mobile]] — TBDR hardware occlusion.
[[level-of-detail-lod]] — complementary technique.

---

## Источники

- **Akenine-Möller et al. (2018). RTRT 4, chapter 19.**
- **GPU Gems 3, chapter 6 (Hardware Occlusion Queries Made Useful).**

---

## Проверь себя

> [!question]- Почему occlusion culling часто не нужен на mobile?
> TBR (Adreno, Mali) имеет Hi-Z hardware — tile-level depth rejection автоматический. TBDR (PowerVR, Apple AGX) вообще делает perfect occlusion. Software occlusion добавляет CPU overhead без значимого win для most apps.

---

*Deep-dive модуля M10.*
