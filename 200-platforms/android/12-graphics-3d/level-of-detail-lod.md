---
title: "Level of Detail (LOD): меньше полигонов далеко от камеры"
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
  - "[[mesh-compression-draco]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gltf-2-format-deep]]"
reading_time: 10
difficulty: 3
---

# Level of Detail (LOD)

Детализация модели дорога propor проnalно distance от камеры. Мебель на 20 метров занимает ~20 пикселей на экране — нет смысла render 10,000 polygons. **LOD** — множественные versions model с разным detail, runtime switch based on screen size/distance.

---

## Историческая справка

LOD эволюционировал от manual decimation к automatic continuous chains:

- **1976 — Clark.** "Hierarchical geometric models for visible surface algorithms" — first academic LOD.
- **1984 — DeHaemer, Zyda.** Practical LOD algorithms.
- **1992 — Hoppe** "Mesh optimization" — edge collapse-based simplification.
- **1996 — progressive meshes (Hoppe).** Continuous LOD via encoded edge operations.
- **1997-2000 — industry adoption.** Quake 3 Arena uses LOD for terrain.
- **2000s — commercial tools.** Simplygon (2006), InstantMesh.
- **2010 — Tessellation shaders** (OpenGL 4.0) — hardware tessellation for surface LOD.
- **2013 — Nvidia Meshes to Meshlets research.**
- **2020 — Mesh shaders (NVIDIA Turing).** Meshlet-based geometry pipeline.
- **2022 — Nanite (UE5).** Automatic continuous LOD through virtualized geometry. Revolutionary на desktop.
- **2024 — Meshlet LOD на mobile.** Adreno 730+, Mali G715+ with mesh shader support experimental.

2026 standard: glTF с MSFT_lod extension, автоматическая generation через meshoptimizer в asset pipeline.

## Основная идея

Classical LOD chain:
- **LOD 0** — high detail (~10k tri) for close-up (distance 0-3 m).
- **LOD 1** — medium (~3k tri) for medium range (3-10 m).
- **LOD 2** — low (~500 tri) for far (10-30 m).
- **LOD 3** — impostor (single billboard quad) for very far (> 30 m).

Selection based on screen-space size или distance от camera.

---

## Distance-based LOD

```kotlin
fun selectLOD(obj: Renderable, camera: Camera): Mesh {
    val distance = (obj.position - camera.position).length
    return when {
        distance < 5f -> obj.lod0
        distance < 15f -> obj.lod1
        distance < 30f -> obj.lod2
        else -> obj.lod3
    }
}
```

Simple, works для most cases.

---

## Screen-space LOD

Better approach: calculate projected size на screen, select based on pixel count.

```kotlin
fun projectedSize(obj: Renderable, camera: Camera, viewportHeight: Int): Float {
    val distance = (obj.position - camera.position).length
    val radius = obj.boundingSphere.radius
    val fov = camera.fovRadians
    // approximate projected radius
    return radius / (distance * tan(fov / 2)) * viewportHeight
}

fun selectLOD(obj: Renderable, camera: Camera, vh: Int): Mesh {
    val size = projectedSize(obj, camera, vh)
    return when {
        size > 100f -> obj.lod0
        size > 30f -> obj.lod1
        size > 10f -> obj.lod2
        else -> obj.lod3
    }
}
```

More accurate; work with widescreen aspects, different FOVs.

---

## LOD generation

### Artist-made

Artist модель creates each LOD manually in Blender/Maya. Best quality, most work.

### Auto-generation

Tools вроде **Simplygon**, **meshoptimizer**, **Meshlab** auto-simplify:

```bash
# Meshoptimizer
meshopt-simplify input.obj -ratio 0.5 -error 0.01 > output.obj
```

Output simplified mesh с ~50% polygons, preserving silhouette. Real-time LOD generation possible on load.

### glTF extensions

`MSFT_lod` extension в glTF stores multiple LODs в one file:

```json
{
    "extensions": {
        "MSFT_lod": {
            "ids": [1, 2, 3]  // references other nodes с lower LOD meshes
        }
    }
}
```

---

## LOD transitions

Popping (jarring transition between LODs) — visible artifact. Solutions:

### Dissolve transition

```glsl
// Fade between LODs over 0.5 m distance
float blend = smoothstep(edge - 0.25, edge + 0.25, distance);
// Render both LODs with mixed alpha
```

### Cross-dissolve

Render both LOD 1 и LOD 2 с complementary alpha. More expensive but smoother.

### Nanite-style (UE5)

Unreal 5 Nanite — automatic continuous LOD. Too expensive для mobile (compute shader-heavy, large memory). Future maybe.

---

## Impostors

Very far objects rendered как flat quad with pre-rendered texture:

```
// At LOD 3, заменяем full 3D model на billboard
val quad = BillboardQuad(position, facingCamera, impostorTexture)
drawBillboard(quad)
```

Zero vertex shader cost, simple fragment. Acceptable at large distance.

---

## Mobile specifics

На mobile LOD — **critical**. Budget:
- 60 FPS с 500k triangles scene — OK on flagship.
- 60 FPS с 2M triangles — requires LOD.

Scene layout typical для Planner 5D:
- 5-10 close furniture (LOD 0, ~50k tri total).
- 10-20 medium (LOD 1, ~50k tri).
- 30+ distant (LOD 2, ~20k tri).
- Wall textures для "infinite" rooms (impostors).

Total ~120k tri drawn vs 500k без LOD. 4× savings.

---

## Engines

- **Filament:** manual LOD (provide multiple glTF files, select at runtime).
- **SceneView:** manual.
- **Godot:** LOD supported, auto-selection based on screen size.
- **Unity:** LOD Group component, standard feature.
- **Unreal:** LOD chains + Nanite.

---

## Связь

[[frustum-culling]] — complementary: cull out-of-view, LOD simplifies in-view.
[[mesh-compression-draco]] — meshopt also генерирует LODs.
[[gpu-architecture-fundamentals]] — vertex cost matters.

---

## Источники

- **Akenine-Möller et al. (2018). RTRT 4, chapter 19.**
- **Meshoptimizer.** [github.com/zeux/meshoptimizer](https://github.com/zeux/meshoptimizer).

---

## Проверь себя

> [!question]- Почему screen-space LOD лучше distance-based?
> Distance-based не учитывает aspect ratio и FOV. Объект на 10 м при 90° FOV выглядит меньше чем при 30° FOV. Screen-space size — direct metric "насколько заметно".

---

*Deep-dive модуля M10.*
