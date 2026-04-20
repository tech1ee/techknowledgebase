---
title: "Case study: Planner 5D — архитектура и инженерия"
created: 2026-04-20
modified: 2026-04-20
type: case-study
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/case-study
  - type/case-study
  - level/intermediate
related:
  - "[[engine-comparison-matrix]]"
  - "[[case-ikea-place-ar]]"
  - "[[case-sweet-home-3d-android]]"
  - "[[build-3d-home-planner-from-scratch]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
primary_sources:
  - url: "https://planner5d.com/blog/planner-5d-redefining-home-management-through-immersive-design-tech"
    title: "Planner 5D blog — technical overview"
    accessed: 2026-04-20
  - url: "https://www.unite.ai/alexey-sheremetyev-founder-and-chief-product-officer-at-planner-5d-interview-series/"
    title: "Alexey Sheremetyev (CPO) interview"
    accessed: 2026-04-20
reading_time: 15
difficulty: 4
---

# Case study: Planner 5D

## Компания history

Planner 5D timeline:

- **2011 — founded** в Вильнюсе (Литва) Сергеем Норицыным и Алексеем Шеретьевым.
- **2012 — первая версия** app для iPad.
- **2014 — Android launch.** Cross-platform С++/NDK engine.
- **2015 — user base ~10M.**
- **2018 — web version** через Emscripten (C++ → WebAssembly).
- **2019 — AR mode** добавлен.
- **2021 — 4K cloud rendering** — AI-enhanced.
- **2023 — 74M users.** One of top interior design apps.
- **2024 — ML-powered furniture search.**
- **2026 — 74M+ users, 160M designs.** Continued growth.

Series funding: $22M+ over 10 years. Team ~150+ people, distributed.

Business model freemium:
- Free: limited catalog, 2D + 3D view, basic AR.
- Premium ($6.99/month): full catalog, 4K rendering credits, advanced AR features.
- Enterprise: licensed to real estate companies, interior design firms.



**Planner 5D** — flagship interior design app. 74 million users, 160 million designs. Founded 2011, Android and iOS + web. Flagship для класс home planner / interior design apps.

---

## Product

Core features:
- **2D floor plan editor.** Drag-and-drop walls, rooms, doors.
- **3D view.** Instant switch — same scene in 3D.
- **Extensive catalog.** 10,000+ furniture, materials, decorations.
- **Cloud sync.** Scenes accessible any device.
- **4K photorealistic rendering** — cloud-based (AI-powered).
- **AR mode** — place furniture в real room.
- **Freemium** — pro features paid.

---

## Technical stack (from interviews и inference)

### Android

- **Kotlin** primary.
- **Custom C++/NDK 3D engine** — not Unity/Unreal/Filament.
- **OpenGL ES 3.0** primary rendering (migrating Vulkan).
- **Room** для local cache of scene state.
- **Coroutines/Flow** для reactive updates.

### Cross-platform

Same C++ core used on iOS, Android, web (emscripten). Major engineering investment.

### Cloud infrastructure

- **4K rendering** runs on cloud GPUs (AWS / Google Cloud).
- Client sends scene, gets back rendered image.
- Avoids mobile GPU load для highest quality.

---

## Architectural decisions

### Custom engine choice

При 11 years и 74M users, custom engine оправдан:
- Full control over pipeline.
- Optimize для specific use case (interior design).
- Small binary size.
- No licensing.

Downside: thousands of hours development.

### 2D + 3D unified data model

Single scene representation (walls, rooms, objects in 3D world coords). 2D view — orthographic projection top-down. 3D view — perspective walking. **Both render same data**, just different projection matrix.

Architectural benefit: editing в 2D automatically reflects в 3D without sync code.

### Cloud rendering

For 4K photorealistic shots: dedicated cloud GPU farm. Mobile can't match quality in reasonable time.

User requests → scene upload → cloud GPU renders → image down to device. ~30 seconds per render (acceptable для "final shot").

Day-to-day 3D view — local rendering.

---

## Technical problems they solved

### Problem 1: 2D/3D state consistency

Edit wall в 2D should update 3D instantly. Both views share same mutable model.

Architecture:
- MVVM с single source of truth (SceneModel).
- StateFlow broadcasts changes.
- Both views observe, re-render.
- Delta updates (only changed parts).

### Problem 2: Large scenes performance

Design с 200+ objects needs smooth 60 FPS interaction.

Mitigations:
- **LOD:** simplify distant furniture.
- **Instancing:** identical chairs — one draw.
- **Frustum culling:** off-screen objects not drawn.
- **Texture atlases:** fewer GL state changes.

### Problem 3: Cloud sync

Large scene (100+ objects) ~5 MB JSON. Slow over 3G.

Solutions:
- Differential sync (only changes sent).
- Binary format (glTF/protobuf) — 2× smaller.
- Local cache (Room DB) для offline.

### Problem 4: AR mode

AR integration added 2018. ARCore + custom 3D engine via Vulkan bridge.

Complex: two different rendering systems unified.

---

## Performance metrics (inferred)

- **APK size:** ~45 MB (including catalog of most used models).
- **Cold start:** ~2-3 seconds.
- **Scene load time:** 1-2 seconds (local), ~5 sec (cloud fetch).
- **FPS on Snapdragon 7 Gen 1:** 55-60 FPS in 3D view.
- **Battery:** ~15-20% per hour intensive use.
- **4K cloud render:** 15-30 seconds per image.

---

## Lessons для learners

1. **Custom engine ≠ always better.** Works because Planner 5D scale + company investment. Most projects use Filament / SceneView / Godot.

2. **Unified data model** для multi-view — architectural gem. Don't duplicate scene data.

3. **Cloud rendering** для premium quality — sensible separation. Local interactive + cloud photorealistic.

4. **LOD + culling + instancing** — essential для large scenes even с custom engine.

5. **Long-term engineering investment** required. 11 years иterating.

---

## Technologies demonstrated

- Custom NDK rendering.
- 2D/3D unified view.
- Cloud sync architecture.
- ARCore integration (post-facto).
- Freemium cloud feature model.

---

## Adapting ideas для new app

Don't copy custom engine. Use:
- [[filament-architecture-deep]] — render engine.
- [[sceneview-arcore-composable-3d]] — AR simplification.
- **Same unified 2D/3D data model** principle.
- **Same cloud rendering** idea для "final shots".

Shortens timeline from 11 years to 1-2.

---

## Связь

[[engine-comparison-matrix]] — why custom engine chose.
[[case-ikea-place-ar]] — alternative architecture (AR-first).
[[case-sweet-home-3d-android]] — open-source alternative.
[[build-3d-home-planner-from-scratch]] — capstone inspired by this.
[[instancing-batching-draw-calls]] — used optimizations.

---

## Источники

- **Planner 5D blog.** [planner5d.com/blog](https://planner5d.com/blog/planner-5d-redefining-home-management-through-immersive-design-tech).
- **Alexey Sheremetyev interview (unite.ai).** [unite.ai](https://www.unite.ai/alexey-sheremetyev-founder-and-chief-product-officer-at-planner-5d-interview-series/).

---

*Case study модуля M15.*
