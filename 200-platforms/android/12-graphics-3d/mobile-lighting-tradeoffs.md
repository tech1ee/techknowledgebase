---
title: "Mobile lighting tradeoffs: что реально работает на Adreno/Mali в 2026"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/lighting
  - type/deep-dive
  - level/advanced
related:
  - "[[pbr-physically-based-rendering]]"
  - "[[lighting-models-lambert-phong-blinn]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[thermal-throttling-and-adpf]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[pbr-physically-based-rendering]]"
reading_time: 12
difficulty: 5
---

# Mobile lighting: реальность 2026

Теория PBR great, но на mobile — trade-offs. Этот файл — практический guide: какие lighting strategies работают на реальных phones в 2026.

---

## Budget за frame

Typical mobile budget (60 FPS):
- **Adreno 740** (flagship): ~2 TFLOPS, ~16 ms per frame.
- **Mali-G710** (mid-high): ~1.5 TFLOPS.
- **Adreno 650** (2020 flagship): ~1.2 TFLOPS.
- **Mali-G52** (mid-range): ~0.5 TFLOPS.

На 1080p × 60 FPS = 124 million pixels/sec. Для PBR fragment shader ~50 ALU per pixel = 6 GFLOPS. Flagship: 2/6 ≈ 30% budget на shading. Mid-range: рассчитано на edge.

---

## Tiers

### Tier 1: flagship (Adreno 740+, Mali-G710+)

Full PBR Disney:
- Metallic-roughness workflow.
- IBL with split-sum.
- Multiple point + directional lights.
- Shadow maps.
- Post-processing (bloom, tone mapping).

Expectation: 60 FPS, good battery.

### Tier 2: mid-range (Adreno 630, Mali-G57)

Simplified PBR:
- Disney BRDF.
- IBL only diffuse (no specular IBL).
- 1 directional + 2 point lights max.
- Baked shadow maps.
- Minimal post-processing.

### Tier 3: low-end (Adreno 500, Mali-G31)

Blinn-Phong:
- Albedo + specular parameter.
- 1 directional light.
- No shadows or pre-baked.
- No post-processing.

### Tier 4: very low (Adreno 300, Mali-400)

Lambert only:
- Vertex lighting вместо fragment (cheaper).
- Single light.
- Unlit sometimes acceptable.

---

## Device detection

```kotlin
fun selectLightingTier(): LightingTier {
    val gpuVendor = GLES30.glGetString(GLES30.GL_VENDOR)
    val gpuRenderer = GLES30.glGetString(GLES30.GL_RENDERER)
    
    return when {
        "Adreno 7" in gpuRenderer || "Mali-G7" in gpuRenderer -> TIER_1
        "Adreno 6" in gpuRenderer || "Mali-G5" in gpuRenderer -> TIER_2
        "Adreno 5" in gpuRenderer -> TIER_3
        else -> TIER_4
    }
}
```

Filament обычно определяет automatically. Для custom engine — device-based selection OR user setting.

---

## Baked vs dynamic

**Baked lighting** — lightmap texture precomputed offline (Blender, Unity, custom tool). Scene lighting «baked in», no runtime cost для static geometry.

Pros:
- Free at runtime.
- Beautiful global illumination.
- Simple setup.

Cons:
- Only static geometry (не moving objects).
- APK size (large lightmaps).
- Re-bake нужен при изменениях.

**Dynamic lighting** — calculated per frame.

Pros:
- Any moving light или object.
- No precomputation.

Cons:
- Runtime cost.
- Lesser quality than baked (обычно).

**Hybrid** — default для games. Static scene baked, moving objects (characters, furniture) dynamic.

---

## Light probes

For dynamic objects in baked scene: sample pre-computed probes at object position → approximation of baked ambient для dynamic object.

Light probes — spherical harmonic approximation environment radiance per sample location. Cheap to sample (9 coefficients вместо cubemap).

Unity, Unreal, Godot все support. Filament — через IBL probes.

---

## Shadow strategies

**Real-time shadow maps** (см. [[shadow-mapping-on-mobile]]):
- Expensive на mobile.
- Quality issues (acne, PCF).
- Use sparingly (1 shadow-casting light).

**Baked shadows:**
- Pre-computed.
- High quality.
- Only static.

**Contact shadows / SSAO:**
- Approximate local occlusion.
- Not real shadows but look plausible.

**Stylized shadows:**
- Hard shadows projected onto ground plane.
- Cheap.
- Works для certain aesthetics.

---

## Real-world numbers

### Planner 5D (Tier 1-2 depending)

Opaque PBR + IBL + 1 directional light + ambient occlusion. ~40 ALU per pixel. На Adreno 740 — 60 FPS, battery drain moderate.

### IKEA Place (AR, Tier 1)

PBR + ARCore lighting estimation (SH) + depth occlusion. Additional cost от camera feed rendering. ~60 ALU per pixel. 60 FPS on flagship, 30-45 on mid-range.

### Sweet Home 3D (Tier 2-3)

Simplified Blinn-Phong + vertex lighting на low-end. 30 FPS acceptable для editor.

---

## Детальный budget analysis

### ALU budget на Snapdragon 8 Gen 3 (Adreno 830)

Рассмотрим concretely что позволяет budget flagship mobile GPU:

- **Теоретический peak:** 4 TFLOPS (FP32).
- **Realized в real workloads:** ~40-60% от peak из-за memory stalls, divergence.
- **Effective:** ~1.8 TFLOPS.
- **Per frame @ 60 FPS:** 30 GFLOPS.
- **1080p × 4× overdraw:** 8 million fragments × 4 = 32M.
- **ALU per fragment:** 30 GFLOPS / 32M = ~940 ops.

Typical shader complexity:
- Lambert only: 20-30 ops.
- Blinn-Phong: 40-50 ops.
- Simplified PBR (no IBL): 80-120 ops.
- Full PBR (Cook-Torrance + IBL + shadows): 200-400 ops.

На flagship budget easily accommodates full PBR с overhead для effects.

### Bandwidth budget

More constraining чем ALU на mobile:
- LPDDR5X bandwidth: ~68 GB/s shared с CPU.
- Available для GPU: ~30-40 GB/s.
- Per frame: 600 MB @ 60 FPS.
- 1080p framebuffer (RGBA8): 8.3 MB × 2 writes (color + depth) = 16.6 MB.
- Textures × N samples per fragment: depends.

Easy to bandwidth-bound. Tile-based rendering (TBR) crucial.

### Memory budget

- Total device RAM: 8-16 GB typical.
- App allocation limit: ~2-4 GB.
- Scene data + textures typically: 200-500 MB.

Budget для textures: ~300 MB. С KTX2 compression это ≈ 1.5 GB uncompressed equivalent.

---

## Performance traps

### Trap 1: Per-fragment light loops

```glsl
// Bad — divergent loop
for (int i = 0; i < numLights; i++) {
    if (lightInRange[i]) {
        color += computeLight(i);
    }
}
```

Warp divergence if `numLights` varies. Better: clustered forward with per-cluster light lists.

### Trap 2: Heavy shader compilation

Complex shaders с 500+ lines могут compile 200+ ms. Первый draw hitch. Solution: pipeline cache (см. [[shader-compilation-jitter-mitigation]]).

### Trap 3: Forgetting Fresnel

Без Fresnel term surfaces look "flat" at grazing angles. Huge quality degradation vs small cost (5-10 ops).

### Trap 4: Wrong precision

All-highp doubles register pressure vs mediump + strategic highp. Occupancy halved.

### Trap 5: Deferred shading on TBR

Deferred requires multiple render targets (G-buffer 3-4 attachments). На TBR это reduces tile size, hurts efficiency. Forward+ usually wins на mobile.

---

## Optimization techniques

1. **Light culling.** Don't compute lights out of range.
2. **Clustered forward.** Light list per screen cluster.
3. **Mediump precision** для lighting math.
4. **Separate passes** для opaque + transparent.
5. **Simpler BRDF** for distant objects (LOD).

---

## Связь

[[pbr-physically-based-rendering]] — full PBR theory.
[[lighting-models-lambert-phong-blinn]] — simpler alternatives.
[[gpu-architecture-fundamentals]] — register pressure, occupancy.
[[thermal-throttling-and-adpf]] — thermal implications.
[[image-based-lighting-ibl]] — IBL detail.

---

## Источники

- **Google Filament documentation.** PBR on mobile section.
- **Unity URP performance guidelines.**
- **Arm Mali best practices guide.**

---

## Проверь себя

> [!question]- Когда использовать baked vs dynamic lighting на mobile?
> Baked для static geometry (room, environment) — free at runtime, highest quality. Dynamic для moving objects (characters, furniture in Planner 5D). Hybrid — standard approach.

---

## Куда дальше

| Направление | Куда |
|---|---|
| PBR theory | [[pbr-physically-based-rendering]] |
| IBL | [[image-based-lighting-ibl]] |
| Shadows | [[shadow-mapping-on-mobile]] |

---

*Deep-dive модуля M6.*
