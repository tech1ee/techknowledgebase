---
title: "ARCore Depth API: реальная глубина сцены"
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
  - level/intermediate
related:
  - "[[arcore-fundamentals]]"
  - "[[ar-occlusion-rendering]]"
  - "[[case-ikea-place-ar]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
primary_sources:
  - url: "https://developers.google.com/ar/develop/depth"
    title: "ARCore Depth API"
    accessed: 2026-04-20
  - url: "https://augmentedperception.github.io/depthlab/assets/Du_DepthLab-Real-Time3DInteractionWithDepthMapsForMobileAugmentedReality_UIST2020.pdf"
    title: "DepthLab (Du et al., UIST 2020)"
    accessed: 2026-04-20
reading_time: 12
difficulty: 4
---

# ARCore Depth API

**Depth API** — ARCore feature, даёт per-pixel depth estimation из one camera. Range 0.5–65 m, precision improves with phone movement. Makes **occlusion-aware AR** possible — virtual furniture correctly hidden за real objects.

Introduced 2019; hardware-accelerated на Pixel 4+ с ToF-sensor, software fallback для other devices (since UIST 2020 — Du et al. DepthLab algorithm).

---

## Зачем

Без depth: virtual chair "plavayет" at the floor level, но не знает что real human sits on the floor в front of it → virtual chair covers the real human visually. Not realistic.

С depth: ARCore knows distance to real-world объекты. Virtual chair correctly occluded за real human.

Houzz study: AR with occlusion → 11× higher conversion to purchase vs без occlusion.

---

## Enable depth

```kotlin
val config = Config(session).apply {
    depthMode = Config.DepthMode.AUTOMATIC  
    // AUTOMATIC — hardware if available, else software
    // RAW_DEPTH_ONLY — raw ToF (flagship only)
    // DISABLED
}
session.configure(config)

// Check support
if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
    // OK
}
```

---

## Depth data

Per frame:

```kotlin
try {
    val depthImage = frame.acquireDepthImage16Bits()
    // Use depth data
    depthImage.close()
} catch (e: NotYetAvailableException) {
    // Depth not ready этот frame
}
```

`depthImage` — bitmap с pixel values = distance в mm.

Format:
- **CPU depth image16Bits:** 16-bit integer, millimeters.
- **GPU depth texture:** attach как sampler2D в fragment shader для per-pixel occlusion.

---

## GPU occlusion shader

```glsl
// Fragment shader
uniform sampler2D u_depthTexture;
uniform vec2 u_depthTextureSize;

in vec2 v_cameraUV;       // camera-space UV
in float v_worldDepth;     // virtual object depth at this fragment

out vec4 fragColor;

void main() {
    // Sample real depth
    vec2 duv = v_cameraUV / u_depthTextureSize;
    float realDepth = texture(u_depthTexture, duv).r;  // in meters
    
    // Если real depth меньше virtual → real thing closer → discard virtual pixel
    if (realDepth < v_worldDepth - 0.01) {  // small bias
        discard;  // note: discard disables early-Z, accept the cost
    }
    
    // Draw virtual fragment
    fragColor = computeVirtualColor();
}
```

Real-time occlusion. Furniture hidden за real table, real human, real wall.

---

## Depth precision

- **Close (0.5-3 m):** ±1-2 cm typical.
- **Medium (3-10 m):** ±5-10 cm.
- **Far (10-65 m):** ±50 cm or more.

Accuracy depends on:
- Camera sensor quality.
- Scene lighting.
- ToF sensor (flagship) vs software estimation.
- Movement — more movement = better estimates.

---

## ToF hardware

Phones с **Time-of-Flight** sensor (Pixel 4/5/6 Pro, Samsung S20 Ultra+) — direct depth sensor. Very accurate.

Non-ToF phones (Pixel 4a, most mid-range) — software depth estimation via feature tracking + monocular depth ML model (since DepthLab 2020).

Check at runtime:
```kotlin
val raw = session.isDepthModeSupported(Config.DepthMode.RAW_DEPTH_ONLY)
// true = hardware ToF available
```

---

## Use cases

- **Occlusion rendering** (см. [[ar-occlusion-rendering]]).
- **Physics collision** — virtual ball bouncing off real ground.
- **Measurement** — distance between real points.
- **Environmental understanding** — map room geometry.
- **Passthrough effects** — blur background (depth-based portrait mode в AR).

---

## Performance

Depth generation:
- **ToF hardware:** negligible overhead.
- **Software:** ~5-10% CPU, ~5% GPU. Can be throttled down.

Vietnam Для AR apps — depth обычно justifies the cost через better visual quality.

---

## Real-world case: IKEA Place

IKEA Place uses depth для:
1. **Occlusion:** diван correctly hidden за real furniture.
2. **Lighting:** depth helps establish scene geometry.
3. **Measurement:** user can see exact size match.

Result — 11× purchase conversion vs pre-depth AR.

---

## Связь

[[arcore-fundamentals]] — context.
[[ar-occlusion-rendering]] — применение depth.
[[case-ikea-place-ar]] — real deployment.
[[arcore-plane-detection-deep]] — complementary.

---

## Источники

- **ARCore Depth API.** [developers.google.com/ar/develop/depth](https://developers.google.com/ar/develop/depth).
- **DepthLab paper (UIST 2020).** [augmentedperception.github.io/depthlab](https://augmentedperception.github.io/depthlab/assets/Du_DepthLab-Real-Time3DInteractionWithDepthMapsForMobileAugmentedReality_UIST2020.pdf).

---

## Проверь себя

> [!question]- Зачем Depth API если plane detection уже есть?
> Plane — geometric surfaces (floor, walls). Depth — **per-pixel distance**. Depth дает occlusion behind ANY real object (human, table, couch), не только planes. Complementary — использовать оба.

---

*Deep-dive модуля M13.*
