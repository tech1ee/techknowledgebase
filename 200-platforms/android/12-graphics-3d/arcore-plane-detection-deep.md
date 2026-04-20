---
title: "ARCore plane detection: как ARCore находит поверхности"
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
  - "[[battery-drain-plane-detection]]"
  - "[[arcore-depth-api]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
primary_sources:
  - url: "https://developers.google.com/ar/develop/java/plane-detection"
    title: "ARCore Plane detection"
    accessed: 2026-04-20
reading_time: 10
difficulty: 3
---

# ARCore plane detection

Plane detection — нахождение горизонтальных и вертикальных поверхностей в scene. Foundation для placement объектов (furniture, decor, objects "на полу").

---

## Алгоритмы под капотом

ARCore plane detection — сложный ML + computer vision pipeline:

1. **Feature detection:** Shi-Tomasi corner detector или SIFT-like finds high-contrast points per frame.
2. **Feature matching:** descriptors (BRIEF, ORB) связывают points между frames.
3. **Visual-Inertial Odometry (VIO):** fuses camera + IMU data для accurate 3D position estimation каждого feature.
4. **RANSAC plane fitting:** cluster feature points, fit plane через random sampling, extract plane с largest inlier set.
5. **Temporal smoothing:** smooth plane updates over frames.

Limitations:
- **Featureless surfaces fail.** White walls, plain wooden floors — sometimes not detected.
- **Poor lighting.** Dim light reduces feature detection.
- **Reflective surfaces.** Mirrors, glossy tile — false features.
- **Moving surfaces.** Cars, animals — tracked as failed.

В 2022 Google added **Scene Semantics** (ML-based scene classification) — complement plane detection when features fail.

## Как работает

SLAM tracking identifies "feature points" — high-contrast visual features. Clusters of nearby feature points на similar plane → plane detection.

ARCore continuously grows planes as camera moves и more features detected.

---

## Configuration

```kotlin
val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    // Или: HORIZONTAL_ONLY, VERTICAL_ONLY, DISABLED
}
```

Most furniture/interior apps — HORIZONTAL only (floors, tables). AR-TV mount would use VERTICAL (walls).

---

## Plane types

```kotlin
enum class Plane.Type {
    HORIZONTAL_UPWARD_FACING,    // floor, tabletop
    HORIZONTAL_DOWNWARD_FACING,  // ceiling
    VERTICAL                     // walls
}
```

---

## Iterating planes

```kotlin
val planes = session.getAllTrackables(Plane::class.java)
for (plane in planes) {
    if (plane.trackingState != TrackingState.TRACKING) continue
    
    val centerPose = plane.centerPose
    val extentX = plane.extentX  // meters
    val extentZ = plane.extentZ
    val type = plane.type
    
    // Use для visualization or hit testing
}
```

---

## Hit testing

```kotlin
val hitResults = frame.hitTest(touchX, touchY)
for (hit in hitResults) {
    val trackable = hit.trackable
    if (trackable is Plane && trackable.isPoseInPolygon(hit.hitPose)) {
        // Tapped on the plane
        val anchor = hit.createAnchor()
        // place object
        break
    }
}
```

`isPoseInPolygon` важен — plane может быть bigger than visible extents.

---

## Problems

### White walls не detected

Plane detection nuждается в feature points (contrast). Blank white walls → no features → no plane.

Mitigation: instruct user osмотреть комнату, move camera around. Feature points накапливаются.

### Glossy surfaces

Reflective floors могут confuse tracking. Specific UI hints для users: "Move to matte surface".

### Low light

Dark rooms → less feature detection → slow / failed plane detection.

---

## Real-world numbers

IKEA Place benchmark:
- 30% users — plane detected в first 3 sec.
- 60% — within 10 sec.
- 90% — within 30 sec.
- 10% — never (glossy/dark/empty scene).

UX должен handle все cases.

---

## Battery impact

Plane detection — **continuous operation**. Battery drain ~10-15% per hour (см. [[battery-drain-plane-detection]]).

Mitigation: **disable after user placed object**. Plane no longer needed для further interaction:

```kotlin
// After anchor created
val config = session.config
config.planeFindingMode = Config.PlaneFindingMode.DISABLED
session.configure(config)
```

Battery saved ~10% per hour.

---

## Visualizing planes

For user feedback — render plane outlines:

```kotlin
for (plane in session.getAllTrackables(Plane::class.java)) {
    if (plane.trackingState != TrackingState.TRACKING) continue
    
    val polygon = plane.polygon  // FloatBuffer с vertices
    renderPlaneOutline(polygon, plane.centerPose)
}
```

Shows user where они могут place objects.

---

## Связь

[[arcore-fundamentals]] — ARCore context.
[[battery-drain-plane-detection]] — battery mitigation.
[[arcore-depth-api]] — alternative / complement.
[[ar-occlusion-rendering]] — using planes для occlusion.

---

## Источники

- **ARCore Plane detection.** [developers.google.com/ar/develop/java/plane-detection](https://developers.google.com/ar/develop/java/plane-detection).

---

## Проверь себя

> [!question]- Почему белые стены плохо детектируются?
> Plane detection uses visual feature points (corners, edges, contrast). Blank walls have no features → no plane. Mitigation: suggest user add environmental texture to tracking (move camera around for multiple viewpoints) или использовать depth API для geometric detection.

---

*Deep-dive модуля M13.*
