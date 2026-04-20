---
title: "Mesh compression: Draco и Meshopt"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/assets
  - type/deep-dive
  - level/intermediate
related:
  - "[[gltf-2-format-deep]]"
  - "[[texture-compression-ktx2-basis]]"
  - "[[asset-loading-streaming]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gltf-2-format-deep]]"
primary_sources:
  - url: "https://github.com/google/draco"
    title: "Google Draco geometry compression"
    accessed: 2026-04-20
  - url: "https://github.com/zeux/meshoptimizer"
    title: "Meshoptimizer (EXT_meshopt_compression)"
    accessed: 2026-04-20
---

# Mesh compression

3D-модели содержат thousands vertices с positions, normals, UVs, tangents, indices. Uncompressed vertex данных scale easily в tens of MB per model. Mesh compression сжимает geometry 4-20× с minor runtime decode cost.

---

## Проблема

Typical sofa model:
- 10,000 vertices × 32 bytes per vertex (pos + normal + UV + tangent) = 320 KB.
- 30,000 indices × 4 bytes = 120 KB.
- Total: ~440 KB uncompressed.

Large AAA scene with 500 objects × 100 KB average = 50 MB geometry.

---

## Draco (Google)

Google [Draco](https://github.com/google/draco) — open-source library для compression 3D geometric data. Launched 2017.

**Technique:**
- **Quantization** — float positions → smaller integers (16-bit обычно).
- **Predictive coding** — compress differences между vertices.
- **Edgebreaker** (connectivity) — triangle topology ~1 bit per vertex.
- **Entropy coding** — arithmetic/huffman.

**Savings:** 5-10× for typical geometry.

**Costs:**
- Decode: ~10-50 ms per million vertices on mobile CPU.
- Compression offline (slow).

### glTF integration

Extension `KHR_draco_mesh_compression`:

```json
{
    "extensionsUsed": ["KHR_draco_mesh_compression"],
    "meshes": [{
        "primitives": [{
            "extensions": {
                "KHR_draco_mesh_compression": {
                    "bufferView": 0,
                    "attributes": { "POSITION": 0, "NORMAL": 1 }
                }
            }
        }]
    }]
}
```

Loader detects extension, calls Draco decoder.

### Android loader

Filament и SceneView include Draco decoder. Transparent.

Custom:
```cpp
draco::Decoder decoder;
auto mesh = decoder.DecodeMeshFromBuffer(&buffer);
// extract positions, normals, etc.
```

---

## Meshoptimizer (Arseny Kapoulkine)

[Meshoptimizer](https://github.com/zeux/meshoptimizer) — alternative / complement to Draco.

**Features:**
- Compression (EXT_meshopt_compression в glTF).
- Vertex cache optimization (reorder для GPU post-transform cache).
- Overdraw optimization.
- Simplification (LOD generation).
- Mesh merging.

**Compression:** similar ratio to Draco, sometimes лучше, **faster decode** (~2-5× быстрее).

### Why popular

Many engines switched to meshopt over Draco:
- Faster decode на runtime.
- Also provides LOD simplification (кastrу Draco не делает).
- One tool для multiple optimizations.

### Integration

Unity, Unreal, Godot, Filament, Three.js — все поддерживают `EXT_meshopt_compression`.

---

## Draco vs Meshopt

| Критерий | Draco | Meshopt |
|---|---|---|
| Compression ratio | 5-10× | 5-10× |
| Decode speed | 10-50 ms/M vertices | 5-15 ms/M vertices |
| Lossy | yes (quantization) | configurable |
| Offline LOD | no | yes |
| Complexity | complex | simpler |
| glTF support | `KHR_draco_mesh_compression` | `EXT_meshopt_compression` |
| Trend | declining | growing |

На 2026: **meshopt более популярный** в новых проектах.

---

## Detailed algorithms

### Edgebreaker (Draco connectivity compression)

Topology encoding идея: вместо хранения полного triangle list (3 indices × N triangles), encode **traversal of triangle mesh** через символы:

- C (continue): продолжить текущий fan.
- L (left): повернуть налево.
- R (right): повернуть направо.
- E (end): заканчать путь.
- S (split): ветвление.

Символы ~2.5 bits per triangle average. For 10k-triangle mesh: ~25k bits = 3 KB vs 120 KB uncompressed. **40× compression** только на connectivity.

### Parallelogram prediction

Для positions: predict next vertex based на previous triangle:

```
given triangle ABC, predict vertex D = A + C - B (parallelogram completion)
actual D может отличаться — store delta (usually small)
```

Delta small → fewer bits to encode. Works хорошо для smooth meshes, плохо для high-detail noisy geometry.

### Vertex cache optimization (meshopt)

Modern GPU имеет small vertex cache (~16-32 vertices). Если triangle references vertex уже в cache — reuse. If not — re-transform (costly).

Meshopt reorders index buffer to maximize cache hits. Algorithm: Tom Forsyth 2006.

Benefit: 20-50% reduction vertex shader invocations. **Не compression**, но related asset pipeline step.

### Overdraw optimization (meshopt)

Reorder triangles чтобы front-facing triangles rendered first → early-Z rejection более effective. Works for opaque geometry.

Combined с vertex cache optimization: `meshopt_optimizeVertexCache` → `meshopt_optimizeOverdraw` → `meshopt_optimizeVertexFetch`.

### Simplification (meshopt)

Edge collapse-based LOD generation:
1. Find edge с smallest **visual error** if collapsed.
2. Collapse edge, creating new vertex.
3. Repeat until target triangle count.

Output: multiple LOD levels от same source model. See [[level-of-detail-lod]].

## Quantization

Both techniques rely heavily на quantization:
- **Positions:** float32 → uint16 mapped на bounding box. Loss: ~0.001 of object size (visually imperceptible).
- **Normals:** float32[3] → octahedral encoded int16[2] (4 bytes → 4 bytes but no precision loss for unit vectors).
- **UVs:** float32 → uint16 (16-bit usually enough для 4K textures).

Sum: from 32 bytes per vertex to ~10 bytes. Further Huffman-like compression adds 2-3×.

---

## Cost analysis

For Planner 5D-sized scene (500 objects × 100 KB geometry):
- Uncompressed: 50 MB.
- Draco: 5-10 MB (80% saving).
- Meshopt: 5-10 MB + faster decode.
- Draco transcoding cost: ~500 ms for 500 models.
- Meshopt: ~150 ms.

Decode time amortized во время loading screen.

---

## GPU instancing alternative

Если scene имеет 1000 one tree model, не compress 1000 copies — use GPU instancing (one vertex buffer, 1000 instance matrices). Orthogonal to compression.

---

## Связь

[[gltf-2-format-deep]] — container format.
[[texture-compression-ktx2-basis]] — textures compression.
[[asset-loading-streaming]] — loading pipeline.
[[level-of-detail-lod]] — meshopt также делает LOD.
[[instancing-batching-draw-calls]] — alternative to compression.

---

## Источники

- **Google Draco.** [github.com/google/draco](https://github.com/google/draco).
- **Meshoptimizer.** [github.com/zeux/meshoptimizer](https://github.com/zeux/meshoptimizer).
- **glTF extensions for compression.** [github.com/KhronosGroup/glTF/tree/main/extensions](https://github.com/KhronosGroup/glTF/tree/main/extensions).

---

## Проверь себя

> [!question]- Draco или Meshopt?
> В 2026 — meshopt рекомендуется для новых проектов. Faster decode, additional features (LOD simplification, vertex cache optimization). Draco still supported широко но declining.

---

*Deep-dive модуля M7.*
