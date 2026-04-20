---
title: "Filament Materials: material language и PBR на практике"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/filament
  - type/deep-dive
  - level/advanced
related:
  - "[[filament-architecture-deep]]"
  - "[[pbr-physically-based-rendering]]"
  - "[[image-based-lighting-ibl]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[filament-architecture-deep]]"
primary_sources:
  - url: "https://google.github.io/filament/Materials.html"
    title: "Filament Materials documentation"
    accessed: 2026-04-20
reading_time: 12
difficulty: 5
---

# Filament Materials и PBR на практике

Детализация material system Filament — как описать material, compile, load, bind textures.

## Зачем отдельный material system

Встроенный в GLSL материал требует 500+ lines shader code. Реализация multiple materials становится copy-paste hell. Filament решает:

1. **Декларативный DSL** — material expressed в 20-50 lines vs 500+ raw GLSL.
2. **Compile-time оптимизация** — unused features stripped.
3. **Shader permutations** — automatic generation variants для lit/unlit, shadow/no-shadow, instancing/not, etc.
4. **Shader validation** — errors at compile time, не runtime.
5. **Cross-platform** — один .mat → compiles для GL / Vulkan / Metal.

### Shading models (full list)

- **lit** — default PBR (Disney BRDF).
- **unlit** — без lighting, pure albedo. Для UI / decals / foliage cards.
- **subsurface** — skin, wax. Simplified SSS approximation.
- **cloth** — specialized BRDF для fabrics (Ashikhmin / Charlie distribution).
- **specularGlossiness** — legacy workflow (до metallic-roughness standardization).

### Material parameters types

- `float, float2, float3, float4` — scalars / vectors.
- `float3x3, float4x4` — matrices.
- `sampler2d, sampler3d, samplerCube` — textures.
- `bool` — flags.

### Vertex attribute requirements

```
requires : [ uv0, uv1, color, tangents ]
```

Declares what vertex data material needs. Filament validates mesh provides these attributes.

### Compile-time features

```
material {
    variantFilter : [ skinning ],  // exclude skinning variant
    culling : back,                // back / front / none / frontAndBack
    depthWrite : true,
    depthCulling : true,
    doubleSided : false,
    ...
}
```

### Packing tricks

MetallicRoughness map хранит 3 grayscale values в RGB channels: R = occlusion, G = roughness, B = metallic. Одна texture вместо трёх. Saves memory и bandwidth.

---


---

## Material definition file

```glsl
material {
    name : "ProductMaterial",
    shadingModel : lit,   // lit (PBR), unlit, subsurface, cloth, specularGlossiness
    blending : opaque,     // opaque, transparent, masked, fade, multiply
    parameters : [
        { type : sampler2d, name : baseColorMap },
        { type : sampler2d, name : normalMap },
        { type : sampler2d, name : metallicRoughnessMap },
        { type : float, name : emissiveFactor },
        { type : float3, name : emissiveColor }
    ],
    requires : [ uv0, tangents ]  // vertex attributes
}

fragment {
    void material(inout MaterialInputs material) {
        prepareMaterial(material);
        
        material.baseColor = texture(materialParams_baseColorMap, getUV0());
        material.normal = texture(materialParams_normalMap, getUV0()).rgb * 2.0 - 1.0;
        
        vec3 mr = texture(materialParams_metallicRoughnessMap, getUV0()).rgb;
        material.roughness = mr.g;
        material.metallic = mr.b;
        
        material.emissive.rgb = materialParams.emissiveColor * materialParams.emissiveFactor;
    }
}
```

Compiled в `.filamat` через:
```bash
matc -p mobile -a vulkan -a opengl -o product.filamat product.mat
```

`-p mobile` — target mobile platforms. Produces optimized variants для Adreno/Mali/PowerVR.

---

## Loading и instantiation

```kotlin
// Load compiled material
val materialData = assets.open("product.filamat").readBytes()
val material = Material.Builder()
    .package(materialData, materialData.size)
    .build(engine)

// Create instance (multiple instances can share one material)
val instance = material.createInstance()

// Bind textures and parameters
instance.setParameter("baseColorMap", baseColorTexture, textureSampler)
instance.setParameter("normalMap", normalTexture, textureSampler)
instance.setParameter("metallicRoughnessMap", mrTexture, textureSampler)
instance.setParameter("emissiveFactor", 1.0f)
instance.setParameter("emissiveColor", 0f, 0f, 0f)

// Assign to renderable entity
RenderableManager.Builder(1)
    .material(0, instance)
    .build(engine, entity)
```

---

## Shading models

- **lit** — standard PBR (metallic-roughness).
- **unlit** — no lighting (UI, flat colors).
- **subsurface** — approximation subsurface scattering (skin, wax).
- **cloth** — special BRDF для cloth materials.
- **specularGlossiness** — legacy workflow (glTF 1.0 style).

---

## Blending modes

- **opaque** — no blending, depth write.
- **transparent** — standard alpha blending.
- **masked** — alpha test с threshold (cutout).
- **fade** — blend + depth write off.
- **multiply** — multiplicative (для decals, shadows).

---

## Variants

Material может иметь variants (conditional compilation):

```glsl
variants : [
    { shadow : true, normal_map : true },
    { shadow : true, normal_map : false },
    { shadow : false, normal_map : true }
]
```

Filament compiles separate shader для каждого variant. Runtime выбирает based on conditions.

Reduces warp divergence — каждый variant — specialized.

---

## Real-world example

glTF model loaded через `gltfio` extension — Filament auto-generates materials based on glTF metallic-roughness workflow. No need писать .mat files для standard case.

Custom materials: если нужны special effects (procedural, animation, custom lighting) — writing .mat makes sense.

---

## Связь

[[filament-architecture-deep]] — engine context.
[[pbr-physically-based-rendering]] — theory.
[[image-based-lighting-ibl]] — IBL для ambient.
[[shader-programming-fundamentals]] — shader-level understanding.

---

## Источники

- **Filament Materials documentation.** [google.github.io/filament/Materials.html](https://google.github.io/filament/Materials.html).

---

## Проверь себя

> [!question]- Чем отличается opaque от transparent blending?
> Opaque — no alpha blending, depth write on, participates in early-Z. Transparent — alpha blended, depth write off (всегда draws), sorted back-to-front. Performance impact — transparent меньше оптимизаций.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Engine detail | [[filament-architecture-deep]] |
| PBR theory | [[pbr-physically-based-rendering]] |
| IBL | [[image-based-lighting-ibl]] |

---

*Deep-dive модуля M8.*
