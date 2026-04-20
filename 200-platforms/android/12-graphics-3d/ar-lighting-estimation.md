---
title: "AR Lighting Estimation: виртуальные объекты под реальным светом"
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
  - "[[pbr-physically-based-rendering]]"
  - "[[image-based-lighting-ibl]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
  - "[[pbr-physically-based-rendering]]"
primary_sources:
  - url: "https://developers.google.com/ar/develop/lighting-estimation"
    title: "ARCore Lighting Estimation"
    accessed: 2026-04-20
reading_time: 8
difficulty: 4
---

# AR Lighting Estimation

Virtual object должен **выглядеть принадлежащим** реальной сцене. Diван в тёмной комнате — dim; in bright sunlit room — bright. Shadow direction — matches real light. Metallic object reflects real environment.

**ARCore Lighting Estimation** — API для этого. Three modes: ambient intensity, environmental HDR, main directional light.

---

## Modes

```kotlin
val config = Config(session).apply {
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    // OR: AMBIENT_INTENSITY (simpler), DISABLED
}
```

### AMBIENT_INTENSITY

Simple. Single RGB ambient color + intensity scalar. Ancient API.

```kotlin
val lightEstimate = frame.lightEstimate
val color = lightEstimate.colorCorrection  // RGBA
val intensity = lightEstimate.pixelIntensity  // 0.0-1.0
```

Use:
```glsl
fragColor.rgb *= color.rgb * intensity;
```

Good enough для simple apps.

### ENVIRONMENTAL_HDR

Advanced. Provides:
- **Main directional light** (sun simulation) — direction + color + intensity.
- **Ambient spherical harmonics** — 9 coefficients describing ambient from все directions.
- **HDR cubemap** — для IBL reflections on metallic/glossy surfaces.

Физически корректная approximation.

```kotlin
val light = frame.lightEstimate

// Directional
val direction = light.environmentalHdrMainLightDirection  // Float[3]
val intensity = light.environmentalHdrMainLightIntensity  // Float[3] RGB
val shadow = direction  // used для shadow mapping

// Ambient SH (9 coefficients × RGB = 27 floats)
val sh = light.environmentalHdrAmbientSphericalHarmonics

// HDR cubemap
val cubemap = light.acquireEnvironmentalHdrCubeMap()
// Upload cubemap как texture, use для IBL reflections
```

---

## Integration с Filament

Filament supports environmental HDR natively:

```kotlin
val ibl = IndirectLight.Builder()
    .reflections(cubemap)
    .irradiance(3, sh)  // 3rd-order SH
    .intensity(intensity.average())
    .build(engine)

scene.setIndirectLight(ibl)
```

Virtual objects автоматически match scene lighting.

---

## Shadows

Main directional light direction used for shadow mapping:

```kotlin
// Construct light view
val lightView = lookAt(eye = center - direction * 10f, target = center, up = up)
// Render shadow map from light's POV
```

Shadow направление matches real sun/light angle. Virtual object casts shadow corresponding к real one.

---

## Real-world impact

IKEA Place data:
- Without lighting estimation: 50% users felt virtual sofa "не looked real".
- With ENVIRONMENTAL_HDR: 85% felt realistic.

Conversion → purchase boost.

---

## Performance

ARCore generates lighting ~once per frame (30-60 Hz). Cheap.

HDR cubemap update может быть lower rate (5-10 Hz). Scene lighting usually slow-changing. Save some cost.

---

## Cases когда disable

- **Indoor controlled lighting** — known studio, pre-computed IBL лучше.
- **Stylized app** — unrealistic lighting (painterly shader). Estimation irrelevant.
- **Performance-критичные** — shave battery.

---

## Связь

[[arcore-fundamentals]] — ARCore context.
[[pbr-physically-based-rendering]] — PBR uses these inputs.
[[image-based-lighting-ibl]] — IBL через cubemap.
[[ar-occlusion-rendering]] — complement.

---

## Источники

- **ARCore Lighting Estimation.** [developers.google.com/ar/develop/lighting-estimation](https://developers.google.com/ar/develop/lighting-estimation).

---

## Проверь себя

> [!question]- Зачем spherical harmonics для ambient?
> SH — compact representation of environmental light от all directions (9 float-triplets vs full cubemap). Fast evaluation в shader: dot product with normal gives indirect light approximation. Фундамент modern IBL.

---

*Deep-dive модуля M13.*
