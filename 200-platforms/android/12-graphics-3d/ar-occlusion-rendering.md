---
title: "AR occlusion rendering: как скрывать виртуальные объекты за реальными"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/ar
  - type/deep-dive
  - level/advanced
related:
  - "[[arcore-depth-api]]"
  - "[[arcore-plane-detection-deep]]"
  - "[[case-ikea-place-ar]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-depth-api]]"
reading_time: 10
difficulty: 5
---

# AR occlusion rendering

## Почему это game-changer

До ARCore Depth API (2019), AR objects floated "over" world. Users noticed fakeness immediately. Impact:
- IKEA Place **без** occlusion: 5.5× conversion vs 2D catalog.
- IKEA Place **с** occlusion: 11× conversion.
- **2× improvement от one feature.**

Occlusion — #1 feature separating "gimmick AR" от "convincing AR".

## Techniques evolution

- **2017-2019 — plane-based only.** ARCore имеет planes, render как depth-only. Works только для simple floor-level placement. Pokemon GO original — no occlusion.
- **2019 — ARCore Depth API.** Per-pixel depth from motion. Enables occlusion за any real object (humans, walls, furniture).
- **2020 — DepthLab UIST paper.** Academic foundation published.
- **2021 — IKEA Place production adoption.** 2× conversion improvement demonstrated.
- **2022 — Streetscape Geometry.** Outdoor scale occlusion через VPS.
- **2023 — ML-refined depth.** Better edge preservation.
- **2024 — Real-time semantic segmentation.** People, vehicles handled separately.
- **2026 — Near-perfect mobile AR occlusion** на flagship devices.



**Occlusion** — virtual objects correctly hidden за real-world objects. Без этого virtual содержимое "плavет" over реальностью — breaks immersion. IKEA Place study: 11× higher conversion с occlusion vs без.

Achievable via ARCore Depth API, plane-based occlusion, или Streetscape Geometry.

---

## Depth-based occlusion

Most advanced. Per-pixel comparison virtual vs real depth (см. [[arcore-depth-api]]).

Fragment shader:
```glsl
uniform sampler2D u_depthTexture;
uniform mat4 u_depthTransform;

in vec4 v_clipPos;
in vec2 v_cameraUV;

out vec4 fragColor;

void main() {
    // Get real depth at this pixel
    float realDepth = texture(u_depthTexture, v_cameraUV).r;  // in meters
    
    // Virtual fragment depth
    float virtualDepth = v_clipPos.z / v_clipPos.w;
    virtualDepth = virtualDepth * 0.5 + 0.5;  // NDC [0,1]
    // Convert к meters using near/far planes
    float virtualDepthMeters = linearizeDepth(virtualDepth, near, far);
    
    // Если real closer by > bias → real object occludes virtual
    if (realDepth < virtualDepthMeters - 0.01) {
        discard;  // real thing in front
    }
    
    // Draw virtual content
    fragColor = computeMaterialColor();
}
```

Note: `discard` disables early-Z, но acceptable cost для AR.

---

## Plane-based occlusion

Simpler. Real-world planes (floor, walls, tables) rendered как depth-only silhouettes. Virtual objects behind planes → occluded.

```glsl
// Pass 1: render plane silhouettes, depth only, no color write
for (plane in detectedPlanes) {
    drawPlaneSilhouette(plane)  // обычно invisible color, но writes depth
}

// Pass 2: virtual objects render normally, depth test rejects occluded
```

Works когда scene primarily planar (floor-level objects).

---

## Streetscape Geometry

В outdoor/city AR: VPS provides buildings mesh (см. [[arcore-geospatial-api-vps]]). Render as depth silhouettes — virtual content correctly hidden за buildings.

```kotlin
val geometries = session.getAllTrackables(StreetscapeGeometry::class.java)
for (geom in geometries) {
    val mesh = geom.mesh
    // Render mesh as depth-only
    renderDepthOnly(mesh, geom.centerPose)
}
```

Essential для outdoor AR (Pokemon GO, navigation).

---

## Trade-offs

### Depth API
- **Pro:** per-pixel accurate, handles any real object.
- **Con:** cost 5-10% CPU/GPU; may be noisy. ToF hardware helps.

### Plane-based
- **Pro:** cheap, easy.
- **Con:** doesn't handle complex geometry (human, random shapes).

### Streetscape Geometry
- **Pro:** indoor for outdoor scale scenes.
- **Con:** VPS coverage required; indoor useless.

---

## IKEA Place architecture

Hybrid:
1. **Plane detection** для initial placement.
2. **Depth API** для occlusion rendering.
3. **Lighting estimation** для realistic shading.
4. All combined в Filament pipeline.

Result: furniture that behaves как real, occludes correctly, shades under real light.

---

## Performance

Occlusion cost:
- **Depth sampling:** ~2-3 GPU cycles per fragment.
- **Branch / discard:** ~5-10 cycles.
- **Total:** maybe 5% frame time overhead.

Worth it для AR quality.

---

## Связь

[[arcore-depth-api]] — depth source.
[[arcore-plane-detection-deep]] — plane silhouettes.
[[arcore-geospatial-api-vps]] — Streetscape Geometry.
[[case-ikea-place-ar]] — production use.

---

## Источники

- **ARCore Depth API docs.** [developers.google.com/ar/develop/depth](https://developers.google.com/ar/develop/depth).
- **DepthLab UIST 2020.**

---

## Проверь себя

> [!question]- Зачем `discard` в depth-based occlusion?
> Virtual fragment has own depth. Compare с real depth: если real closer → drop virtual (`discard`). Early-Z deactivated когда shader uses discard, но эта cost оправдана для AR occlusion качества (11× conversion).

---

*Deep-dive модуля M13.*
