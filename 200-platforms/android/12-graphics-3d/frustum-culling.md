---
title: "Frustum culling: не рендерить то, что вне камеры"
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
  - "[[occlusion-culling]]"
  - "[[projections-perspective-orthographic]]"
  - "[[rendering-pipeline-overview]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[projections-perspective-orthographic]]"
reading_time: 10
difficulty: 4
---

# Frustum culling

**Frustum** — виртуальный «видеоконус» камеры, определяемый 6 плоскостями: left, right, top, bottom, near, far. Объекты вне frustum невидимы — **не нужно их rendering'овать**. Frustum culling — тест bounding volume каждого object против этих 6 planes на CPU перед отправкой в GPU draw.

---

## Историческая справка

Frustum culling — одна из древнейших optimization techniques в real-time 3D:

- **1969 — Sutherland-Hodgman polygon clipping.** Algorithm for clipping polygon vs plane. Basis of modern clipping.
- **1980s — scanline rendering.** Early games implemented basic bounding sphere vs frustum.
- **1996 — Quake (id Software).** BSP tree + PVS (Potentially Visible Set) for levels. Advanced culling for maze-like environments.
- **2001 — Gribb & Hartmann paper.** "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix" — now-classical technique used everywhere.
- **2005+ — modern engines.** Hierarchical bounding volumes (BVH), spatial hashing.
- **2015+ — GPU-driven culling.** Compute shaders perform culling на GPU, feeding multi-draw-indirect.
- **2020+ — occlusion culling alongside frustum.** Hierarchical Z (Hi-Z) buffer generated первым frame, used во втором.
- **2023+ — meshlet culling (UE5 Nanite).** Per-meshlet frustum + backface + cluster culling.

Frustum culling remains fundamental — даже с advanced techniques, первая stage остаётся простая AABB-vs-frustum test.

---

## Зачем

Без culling — каждый object рисуется, даже невидимый. GPU выполняет vertex shaders для всех вершин, clip-ит на стадии clipping (см. [[rendering-pipeline-overview]]). CPU overhead на draw calls также растёт.

С culling — только visible objects отправляются на GPU. Обычная scene имеет 10-50 % visible objects в camera view в каждый момент — massive savings.

---

## Извлечение frustum planes из MVP

Известный result (Gribb & Hartmann, 2001):

```
// MVP matrix → 6 plane equations
plane_left   = row3 + row0
plane_right  = row3 - row0
plane_bottom = row3 + row1
plane_top    = row3 - row1
plane_near   = row3 + row2  // в OpenGL Z[-1,1]
plane_far    = row3 - row2
```

Normalize каждую plane (divide xyz by length of xyz part).

```kotlin
fun extractFrustumPlanes(mvp: Mat4): Array<Vec4> {
    val planes = Array(6) { Vec4.zero }
    val m = mvp.toFloatArray()
    
    // Left
    planes[0] = Vec4(m[3]+m[0], m[7]+m[4], m[11]+m[8], m[15]+m[12])
    // Right
    planes[1] = Vec4(m[3]-m[0], m[7]-m[4], m[11]-m[8], m[15]-m[12])
    // Bottom
    planes[2] = Vec4(m[3]+m[1], m[7]+m[5], m[11]+m[9], m[15]+m[13])
    // Top
    planes[3] = Vec4(m[3]-m[1], m[7]-m[5], m[11]-m[9], m[15]-m[13])
    // Near
    planes[4] = Vec4(m[3]+m[2], m[7]+m[6], m[11]+m[10], m[15]+m[14])
    // Far
    planes[5] = Vec4(m[3]-m[2], m[7]-m[6], m[11]-m[10], m[15]-m[14])
    
    return planes.map { normalize(it) }.toTypedArray()
}
```

---

## Bounding volumes

Для каждого object храним bounding volume (conservative shape):

### AABB (axis-aligned bounding box)

Fastest test. Min/max corners:
```kotlin
class AABB(val min: Vec3, val max: Vec3)
```

Test against plane:
```kotlin
fun isInsidePlane(aabb: AABB, plane: Vec4): Boolean {
    val pVertex = Vec3(
        if (plane.x > 0) aabb.max.x else aabb.min.x,
        if (plane.y > 0) aabb.max.y else aabb.min.y,
        if (plane.z > 0) aabb.max.z else aabb.min.z
    )
    return dot(plane.xyz, pVertex) + plane.w >= 0
}
```

### Bounding sphere

Simpler. Center + radius:
```kotlin
class Sphere(val center: Vec3, val radius: Float)

fun isInsidePlane(s: Sphere, p: Vec4): Boolean {
    return dot(p.xyz, s.center) + p.w >= -s.radius
}
```

Use AABB для tight bounds, sphere для fast tests на many simple objects.

---

## Polish pass

```kotlin
fun cullObjects(objects: List<Renderable>, mvp: Mat4): List<Renderable> {
    val planes = extractFrustumPlanes(mvp)
    return objects.filter { obj ->
        planes.all { plane -> isInsidePlane(obj.aabb, plane) }
    }
}
```

Только objects внутри всех 6 planes — visible.

---

## Hierarchical culling

Для scenes с тысячами objects — hierarchical структура (BVH, octree). Test parent bounding first, если выкрут → cull все children без individual tests.

```
Scene BVH:
 root bounding box
 ├── section 1 (half scene) — reject → skip 500 objects
 └── section 2 (other half) — test → recurse
     ├── sub-section A — accept → test children
     │   ├── object 1 — visible
     │   └── object 2 — reject
     └── sub-section B — reject
```

Godot, Filament, Unity — все используют BVH internally. Custom renderer нужно implement самостоятельно.

---

## Real-world numbers

Scene с 10,000 objects:
- Without culling: 10,000 draw calls, 50 ms CPU.
- With frustum culling: ~500-2000 draw calls (depending on camera), 5-10 ms CPU.

Бо lshoy win.

---

## Edge cases

- **Very close объекты (near plane clip):** standard test works.
- **Очень большие objects (stretching across frustum):** всё ещё within frustum (tested with AABB).
- **Skybox:** всегда visible — не testable normally. Специальный flag.

---

## Связь

[[occlusion-culling]] — next level culling (hidden by geometry).
[[projections-perspective-orthographic]] — frustum определяется perspective matrix.
[[rendering-pipeline-overview]] — где это в pipeline (pre-draw).
[[level-of-detail-lod]] — LOD selection также based on distance (related).

---

## Источники

- **Gribb, G. & Hartmann, K. (2001). Fast Extraction of Viewing Frustum Planes.** Classic paper.
- **Akenine-Möller et al. (2018). RTRT 4.** Chapter 19 (Acceleration Algorithms).

---

## Проверь себя

> [!question]- Как получить frustum planes из MVP matrix?
> Gribb & Hartmann 2001 method: каждая plane = row3 ± row0/1/2 of MVP matrix. 6 planes. Normalize xyz part.

---

*Deep-dive модуля M10.*
