---
title: "Draw calls, batching, instancing: снижение CPU overhead"
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
  - "[[vulkan-pipeline-command-buffers]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[rendering-pipeline-overview]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
reading_time: 10
difficulty: 4
---

# Draw calls, batching, instancing

Каждый draw call имеет CPU overhead — validating state, submitting command to GPU. Много draw calls → CPU-bound. Techniques для reducing draw count: **batching** (merge objects) и **instancing** (one draw for many copies).

---

## Cost of a draw call

На OpenGL ES: ~20-50 μs per draw call (driver validation). На Vulkan: ~5-15 μs. Flagship mobile CPU обрабатывает ~20,000-50,000 draw calls/second.

Для 60 FPS budget — ~333-833 draw calls per frame. Large scene с 5000 objects — уже over budget.

---

## Batching

Combine multiple objects в один vertex buffer + one draw call:

### Static batching

Pre-combine vertices offline. Single VBO, single draw.

Pros: max performance.
Cons: shared material (те objects должны have identical materials), shared transform (все фиксированы relative each other).

Use case: static scene geometry (wall tiles, floor pattern).

### Dynamic batching

Combine каждый frame для small objects (≤50 vertices each):
- CPU copies transformed vertices в shared VBO.
- One draw of combined VBO.

Cons: CPU cost per frame.
Pros: works с moving objects.

Unity использует dynamic batching для small objects по-dfault.

---

## Instancing

Альтернатива — **hardware instancing**. One mesh, N instances с per-instance data (matrix, color, etc.):

```cpp
// Vertex shader
layout(location = 0) in vec3 position;
layout(location = 4) in mat4 instanceMatrix;  // per-instance data
uniform mat4 vp;

void main() {
    gl_Position = vp * instanceMatrix * vec4(position, 1.0);
}

// Draw call
glDrawElementsInstanced(GL_TRIANGLES, indexCount, GL_UNSIGNED_INT, 0, numInstances);
```

Или Vulkan:
```cpp
vkCmdDrawIndexed(cmd, indexCount, instanceCount, 0, 0, 0);
```

**Huge win:** 1000 instances × 1 draw call vs 1000 draw calls. CPU cost — 1000x меньше.

### Instance attributes

Per-instance data либо:
- **Instance buffer** (vertex buffer с `VK_VERTEX_INPUT_RATE_INSTANCE`).
- **SSBO / UBO** indexed by `gl_InstanceID`.

Typical per-instance:
- Model matrix (64 bytes).
- Color tint (16 bytes).
- LOD factor (4 bytes).

---

## When to use

**Instancing** — best для:
- Many copies same mesh (grass, stones, crowd).
- Particle systems.
- Furniture arrays (chairs в restaurant).

**Static batching** — best для:
- Immovable environment (walls, floor).
- Known fixed scene layout.

**Dynamic batching** — limited on mobile, often not worth it. Filament avoids.

---

## Multi-draw indirect (VK 1.2+)

Evolution: **`vkCmdDrawIndirect`** — GPU reads draw parameters из buffer. Combined с GPU-driven culling — full GPU-side rendering pipeline, no CPU overhead per object.

```cpp
// Draw parameters precomputed в buffer (по объекту)
vkCmdDrawIndexedIndirect(cmd, drawParamsBuffer, 0, drawCount, sizeof(DrawParams));
```

Future direction, gaining traction на mobile в 2026.

---

## Real-world scenes

### Planner 5D

Room с 50 pieces мебели → 50 draw calls (если no batching). С instancing (identical chairs) → 10 уникальных draw + instanced для chairs. Save ~40 draws.

### Open-world game

10,000 trees + 1,000 rocks + 500 buildings = 11,500 objects. Без оптимизации — impossible на mobile. С instancing trees + static batching environment — few hundred draws, playable.

### AR furniture app

5 placed virtual objects → 5 draws. Trivial, не need batching. But AR scene с 100 small decals → instancing.

---

## Profiling

AGI / Perfetto показывает draw calls per frame. Red flag — > 500 на mobile. Investigate, use batching/instancing.

---

## Связь

[[vulkan-pipeline-command-buffers]] — batched commands в CB.
[[gpu-architecture-fundamentals]] — CPU overhead implications.
[[rendering-pipeline-overview]] — draw call через pipeline.
[[gpu-memory-management-mobile]] — shared vertex buffers.

---

## Источники

- **Akenine-Möller et al. (2018). RTRT 4, chapter 19.**
- **OpenGL / Vulkan instancing specs.**

---

## Проверь себя

> [!question]- Когда использовать instancing вместо batching?
> Instancing — когда objects — identical copies same mesh с разным transform/color (1000 trees). Batching — когда objects разные, но shared material и не moving (walls). Instancing более efficient для many copies; batching — для mixed static scene.

---

*Deep-dive модуля M10.*
