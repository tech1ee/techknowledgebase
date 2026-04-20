---
title: "glTF 2.0: де-факто стандарт 3D ассетов"
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
  - "[[texture-compression-ktx2-basis]]"
  - "[[mesh-compression-draco]]"
  - "[[filament-architecture-deep]]"
  - "[[pbr-physically-based-rendering]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[pbr-physically-based-rendering]]"
primary_sources:
  - url: "https://www.khronos.org/gltf/"
    title: "Khronos glTF specification"
    accessed: 2026-04-20
  - url: "https://github.com/KhronosGroup/glTF"
    title: "glTF 2.0 GitHub repo"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html"
    title: "glTF 2.0 Specification"
    accessed: 2026-04-20
reading_time: 15
difficulty: 3
---

# glTF 2.0: де-факто стандарт

## Историческая справка

Путь к glTF 2.0 и его adoption:

- **1970s-1980s — ранние форматы.** PLY, STL — академические, simple geometry.
- **1990s — OBJ (Wavefront Technologies).** Text-based, still used. Только geometry + basic materials.
- **1996 — COLLADA (Sony CE).** XML-based, comprehensive. But verbose и slow to parse.
- **2005 — FBX становится dominant.** Autodesk proprietary, industry-standard для authoring. Closed format, license fees.
- **2011 — Khronos начинает glTF working group.**
- **2015 — glTF 1.0 released.** Embedded shader code — проблематично для cross-platform.
- **2017 — glTF 2.0 released.** Removed shader code, added **PBR metallic-roughness** materials. Industry takes notice.
- **2018 — Google Filament adopts glTF 2.0.**
- **2019 — Facebook / Meta use glTF для VR assets.** Quest store.
- **2020 — Mozilla uses для WebXR.** Web standard for 3D.
- **2021 — Apple USDZ (Universal Scene Description zip).** Apple's alternative, но glTF remains web/Android default.
- **2023 — glTF 2.0 extensions stabilized.** KHR_mesh_compression (meshopt), KHR_texture_basisu, KHR_lights_punctual standardized.
- **2026 — Near-universal adoption.** Unity (via plugin), Unreal, Godot, Blender, Maya — all export/import glTF 2.0.

glTF success factors: open, royalty-free, PBR-focused, streaming-friendly, Khronos backing, good tooling (validator, viewer).

---


glTF (**GL Transmission Format**) — open-standard Khronos для 3D-ассетов, оптимизированный для transmission и rendering, не authoring. Version 2.0 released 2017, с тех пор became "JPEG для 3D": Android / iOS / web / Unreal / Unity / Godot / Filament — все support. Google Filament uses glTF as primary format.

---

## Зачем glTF

До glTF 2.0: many formats — FBX (Autodesk proprietary), OBJ (ancient), COLLADA (XML, slow), PLY, STL. All with quirks: different Y-up/Z-up, different handedness, some binary only, some text only, variety material models.

glTF унифицирует:
- **Right-handed, Y-up** (matches OpenGL / Vulkan standard).
- **PBR materials** (metallic-roughness workflow).
- **Compact binary** (GLB variant).
- **Streaming-friendly** (separate buffers).
- **JSON-described** (human-readable).
- **Extensions** для specific features (animations, morph targets, compressions).

---

## Структура

### Two formats

1. **`.gltf`** — JSON + separate binary buffers (`.bin`) + textures (`.jpg`/`.png`/`.ktx2`).
2. **`.glb`** — binary wrapper around всех частях (one file).

GLB для distribution, .gltf для editing.

### JSON schema

```json
{
    "asset": { "version": "2.0", "generator": "Blender 4.0" },
    "scenes": [{ "nodes": [0] }],
    "nodes": [
        {
            "name": "SofaRoot",
            "mesh": 0,
            "translation": [0, 0, 0],
            "rotation": [0, 0, 0, 1],  // quaternion [x,y,z,w]
            "scale": [1, 1, 1]
        }
    ],
    "meshes": [
        {
            "primitives": [{
                "attributes": {
                    "POSITION": 0,
                    "NORMAL": 1,
                    "TEXCOORD_0": 2
                },
                "indices": 3,
                "material": 0
            }]
        }
    ],
    "materials": [
        {
            "name": "LeatherMaterial",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.8, 0.3, 0.1, 1.0],
                "baseColorTexture": { "index": 0 },
                "metallicFactor": 0.0,
                "roughnessFactor": 0.8
            },
            "normalTexture": { "index": 1 }
        }
    ],
    "textures": [...],
    "images": [...],
    "accessors": [...],
    "bufferViews": [...],
    "buffers": [...]
}
```

---

## Key concepts

### Scene → Node → Mesh → Primitive

Hierarchical:
- **Scene** contains top-level nodes.
- **Node** has transform (translation + rotation quaternion + scale), optional mesh, children.
- **Mesh** contains **primitives** (rendering units).
- **Primitive** — one draw call: attributes (positions, normals, UVs, tangents), indices, material.

### Accessor / BufferView / Buffer

Layered data access:
- **Buffer** — raw bytes (file or URL или embedded base64).
- **BufferView** — window into buffer (offset + length).
- **Accessor** — typed view (count, component type, attribute type).

Позволяет one buffer shared across many primitives (efficient).

### PBR material

glTF uses **metallic-roughness workflow** (Disney-compatible):
- `baseColorFactor` + optional texture.
- `metallicFactor`, `roughnessFactor` (combined in metallicRoughnessTexture, green = roughness, blue = metallic).
- `normalTexture`.
- `occlusionTexture`.
- `emissiveFactor` + texture.

Alternative — specular-glossiness (via extension `KHR_materials_pbrSpecularGlossiness`). Less common nowadays.

---

## Extensions

Official Khronos extensions для advanced features:

- `KHR_materials_ior` — index of refraction (glass, water).
- `KHR_materials_transmission` — transparency with refraction.
- `KHR_materials_anisotropy` — anisotropic materials (hair, metallic brushed surfaces).
- `KHR_materials_sheen` — fabric.
- `KHR_materials_clearcoat` — car paint.
- `KHR_materials_emissive_strength` — HDR emissive.
- `KHR_texture_basisu` — Basis Universal compressed textures (см. [[texture-compression-ktx2-basis]]).
- `KHR_texture_transform` — UV matrix.
- `KHR_lights_punctual` — point/directional/spot lights.
- `KHR_draco_mesh_compression` — Draco geometry compression (см. [[mesh-compression-draco]]).
- `EXT_meshopt_compression` — alternative mesh compression.

Filament supports most важные. SceneView — similar.

---

## Animations

Embedded в glTF:

```json
{
    "animations": [{
        "channels": [{
            "sampler": 0,
            "target": { "node": 0, "path": "rotation" }
        }],
        "samplers": [{
            "input": 4,  // time accessor
            "output": 5,  // keyframe values accessor
            "interpolation": "LINEAR"
        }]
    }]
}
```

Paths: `translation`, `rotation`, `scale`, `weights` (morph targets). Interpolation: LINEAR, STEP, CUBICSPLINE.

---

## Skeletal animation

Via `skins`:

```json
{
    "skins": [{
        "joints": [1, 2, 3, 4],  // node indices
        "inverseBindMatrices": 6  // accessor
    }]
}
```

Each vertex has `JOINTS_0` (indices) + `WEIGHTS_0` (weights) attributes. Vertex shader blends:

```glsl
mat4 skinMatrix = 
    weights.x * jointMatrices[joints.x] +
    weights.y * jointMatrices[joints.y] +
    weights.z * jointMatrices[joints.z] +
    weights.w * jointMatrices[joints.w];
vec4 skinnedPosition = skinMatrix * vec4(position, 1.0);
```

---

## Loading in Android

### Filament

```kotlin
val gltfAssetLoader = AssetLoader(engine, UbershaderProvider(engine), entityManager)
val asset = gltfAssetLoader.createAsset(bufferByteBuffer)
ResourceLoader(engine).loadResources(asset)
scene.addEntities(asset.entities)
```

### SceneView

```kotlin
sceneView.apply {
    modelNode("my_model.glb")?.let { node ->
        addChild(node)
    }
}
```

---

## Tooling

- **Blender** — export .gltf/.glb native.
- **Maya / 3dsMax** — via plugin.
- **Khronos Tools** (cli) — convert, optimize, validate.
- **glTF Validator** — [github.com/KhronosGroup/glTF-Validator](https://github.com/KhronosGroup/glTF-Validator).
- **glTF-Viewer** — reference viewer для debugging.

---

## Real usage

- **Google samples** — all в glTF.
- **Filament** — native format.
- **SceneView** — loads glTF first-class.
- **Unity** — via UnityGLTF package (не primary но supported).
- **Unreal** — import glTF supported с 5.0.
- **Godot** — native (с 4.0).
- **Microsoft 3D Viewer на Windows** — glTF/GLB.
- **Adobe Creative Cloud** — substantial support.

---

## Связь

[[texture-compression-ktx2-basis]] — texture compression in glTF.
[[mesh-compression-draco]] — mesh compression.
[[pbr-physically-based-rendering]] — material model.
[[quaternions-and-rotations]] — rotation format.
[[filament-architecture-deep]] — glTF as primary format.

---

## Источники

- **Khronos glTF.** [khronos.org/gltf](https://www.khronos.org/gltf/).
- **glTF 2.0 Specification.** [registry.khronos.org/glTF](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).
- **glTF GitHub.** [github.com/KhronosGroup/glTF](https://github.com/KhronosGroup/glTF).

---

## Проверь себя

> [!question]- Что дает GLB вместо .gltf?
> Binary wrapper: всё в одном файле (JSON + buffers + textures embedded). Проще для distribution (один файл). .gltf для editing — separate files легче modify.

---

## Ключевые карточки

glTF — аналог JPEG/HTML для 3D?
?
Standardized Khronos format для 3D asset transmission. Supported всеми major engines, editors, viewers. PBR metallic-roughness material model. Y-up right-handed coordinate system.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Texture compression | [[texture-compression-ktx2-basis]] |
| Mesh compression | [[mesh-compression-draco]] |
| Filament integration | [[filament-architecture-deep]] |

---

*Deep-dive модуля M7.*
