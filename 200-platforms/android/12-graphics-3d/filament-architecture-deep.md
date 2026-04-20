---
title: "Google Filament: архитектура PBR-движка на Android"
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
  - "[[engine-comparison-matrix]]"
  - "[[filament-materials-and-pbr]]"
  - "[[pbr-physically-based-rendering]]"
  - "[[gltf-2-format-deep]]"
  - "[[androidexternalsurface-vs-embedded]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vulkan-on-android-fundamentals]]"
  - "[[pbr-physically-based-rendering]]"
primary_sources:
  - url: "https://github.com/google/filament"
    title: "Google Filament GitHub"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Filament documentation"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Materials.html"
    title: "Filament Materials documentation"
    accessed: 2026-04-20
reading_time: 25
difficulty: 6
---

# Google Filament: архитектура PBR-движка

## Историческая справка

Filament timeline:
- **2014 — Romain Guy** (Android framework lead) начинает экспериментировать с PBR на mobile в свободное время.
- **2017 — проект announced** на Google I/O.
- **2018 — Filament 1.0 open-sourced.** Apache 2.0 license.
- **2019 — ARCore integration.** Sceneform uses Filament as backend.
- **2020 — Vulkan backend stable.**
- **2021 — Google deprecates Sceneform.** Community picks up → **SceneView** (built on Filament).
- **2022 — 1.20 стабильный, IBL improvements.**
- **2023 — Filament с AGSL integration.**
- **2024 — 1.50+, dynamic resolution, better mobile optimizations.**
- **2025 — 1.60, PBR Neutral tone mapping added.**
- **2026 — 1.71 (current), full VPA-16 support.**

В 2026 Filament — единственный mainstream mobile PBR engine с open-source и industry-grade quality. Alternative только Unity / Unreal (heavier).



**Filament** — Google's open-source PBR rendering engine, released 2018, автор Romain Guy (ex-Android framework team). Версия 1.71 (апрель 2026). Language: C++ с Java/Kotlin bindings. Platforms: Android, iOS, Linux, macOS, Windows, WebGL, Fuchsia.

Filament — **pure rendering engine**, не framework. Отсутствуют scene management, physics, animation (частично), input, UI. Это даёт flexibility (используйте с любой architecture) но требует подтянуть эти capabilities самостоятельно или через SceneView.

---

## Зачем Filament

До Filament: PBR на mobile означал либо Unity (тяжёлый), либо custom implementation (дорого). Google Filament заполнил gap — Google-quality PBR, open-source, lightweight (~7-12 MB AAR), maintainable.

В 2026 Filament — **де-facto стандарт для custom PBR на Android** в профессиональных apps: Google samples, IKEA Place (через SceneView), многие AR apps.

---

## Prerequisites

- [[vulkan-on-android-fundamentals]] — Filament использует Vulkan и GL ES.
- [[pbr-physically-based-rendering]] — understanding PBR принципов.

---

## Architecture

### Core objects

```cpp
Engine* engine = Engine::create();  // per-process singleton

SwapChain* swapChain = engine->createSwapChain(androidSurface);

Renderer* renderer = engine->createRenderer();  // issues render commands

Scene* scene = engine->createScene();  // holds entities
Camera* camera = engine->createCamera();
View* view = engine->createView();  // couples scene + camera + settings

// entities (ECS-style)
EntityManager& em = EntityManager::get();
Entity entity = em.create();

// Components on entities
TransformManager& tm = engine->getTransformManager();
tm.create(entity, parent, worldTransform);

RenderableManager& rm = engine->getRenderableManager();
RenderableManager::Builder(1)
    .boundingBox(...)
    .material(0, material->getDefaultInstance())
    .geometry(0, TRIANGLES, vertexBuffer, indexBuffer)
    .build(*engine, entity);
```

### Render loop

```cpp
void onFrame() {
    if (renderer->beginFrame(swapChain)) {
        renderer->render(view);
        renderer->endFrame();
    }
}
```

Simple. Renderer handles everything: culling, shadow maps, IBL, post-processing.

---

## Key features

### PBR material system

Filament uses **metallic-roughness workflow** (Disney-compatible). Material описывается в собственном **Filament Material Language** (`.mat` файлы):

```glsl
// Material definition
material {
    name : "Leather",
    shadingModel : lit,
    parameters : [
        { type : sampler2d, name : baseColor },
        { type : sampler2d, name : normal },
        { type : sampler2d, name : metallicRoughness }
    ],
    requires : [ uv0, tangents ]
}

fragment {
    void material(inout MaterialInputs material) {
        prepareMaterial(material);
        material.baseColor = texture(baseColor, getUV0());
        material.normal = texture(normal, getUV0()).rgb * 2.0 - 1.0;
        vec3 mr = texture(metallicRoughness, getUV0()).rgb;
        material.roughness = mr.g;
        material.metallic = mr.b;
    }
}
```

Compiled offline через `matc` → binary `.filamat`:

```bash
matc -p all -a all -o leather.filamat leather.mat
```

Loaded in app:
```cpp
Material* material = Material::Builder()
    .package(filamatData, filamatSize)
    .build(*engine);
```

### Multi-platform Vulkan + GL ES

Filament abstracts GPU backend. Runtime select based на device capability:
- **Vulkan** на Android 10+ flagship с working Vulkan drivers.
- **OpenGL ES 3.1+** fallback.
- **Metal** on iOS.
- **WebGL 2** on browsers.

One codebase, all platforms.

### IBL (Image-Based Lighting)

Filament включает **advanced IBL** с split-sum approximation (Karis 2013, см. [[pbr-physically-based-rendering]]):

```cpp
IndirectLight* ibl = IndirectLight::Builder()
    .reflections(cubemap)
    .irradiance(sphericalHarmonics9)
    .intensity(30000.0f)
    .build(*engine);

scene->setIndirectLight(ibl);
```

Pre-computed environment maps или runtime generated.

### Optimizations

Built-in:
- **Frustum culling.**
- **Hardware instancing** где applicable.
- **Shadow map rendering.**
- **Bloom, tone mapping, FXAA.**
- **Per-material optimization variants** (lit/unlit, with/without normal map, etc.).

---

## Compose integration

См. [[androidexternalsurface-vs-embedded]] и [[filament-inside-compose]]. Basic pattern:

```kotlin
@Composable
fun FilamentViewer(modelPath: String) {
    val context = LocalContext.current
    val engine = remember { Engine.create() }
    val renderer = remember { engine.createRenderer() }
    
    AndroidExternalSurface(
        modifier = Modifier.fillMaxSize()
    ) {
        onSurface { surface, _, _ ->
            val swapChain = engine.createSwapChain(surface)
            // ... setup scene, camera, model ...
            
            while (true) {
                if (renderer.beginFrame(swapChain, System.nanoTime())) {
                    renderer.render(view)
                    renderer.endFrame()
                }
                awaitFrame()
            }
        }
    }
}
```

---

## Performance

Typical metrics:
- **APK size:** +7-12 MB (base Filament).
- **RAM:** +20-40 MB overhead.
- **First model load (50k triangles):** ~50 ms.
- **Frame time (60 FPS target):** 16 ms.
- **Shader compilation** (first use): 100-500 ms — mitigate через VkPipelineCache.

Excellent для flagship mobile. On low-end (Adreno 500) — simplified material variants still give 60 FPS for simple scenes.

---

## Comparison с SceneView

Filament — чистый rendering engine. SceneView добавляет:
- Scene graph (node hierarchy).
- glTF loader auto.
- ARCore integration (ArSceneView).
- Gesture handling.
- Kotlin-first API.

Разница:
- Direct Filament: больше boilerplate, full control.
- SceneView: меньше кода, готовые conventions.

Для простого viewer — SceneView. Для complex custom pipeline — Filament direct.

---

## Real usage

- **Google samples** (github.com/google/filament/tree/main/android/samples).
- **IKEA Place** (через SceneView + Filament).
- **SceneView community** apps.
- **Google Search 3D preview** (через Model Viewer поверх Filament).

---

## Связь

[[engine-comparison-matrix]] — позиция среди других движков.
[[filament-materials-and-pbr]] — detail на material system.
[[pbr-physically-based-rendering]] — PBR теоретика.
[[gltf-2-format-deep]] — primary asset format.
[[androidexternalsurface-vs-embedded]] — Compose integration.
[[filament-inside-compose]] — practical example.
[[sceneview-arcore-composable-3d]] — wrapper.

---

## Источники

- **Filament GitHub.** [github.com/google/filament](https://github.com/google/filament).
- **Filament documentation.** [google.github.io/filament](https://google.github.io/filament/Filament.md.html).
- **Filament Materials.** [google.github.io/filament/Materials.html](https://google.github.io/filament/Materials.html).
- **Romain Guy blog.** [romainguy.curious-creature.org](https://romainguy.curious-creature.org/).

---

## Проверь себя

> [!question]- Когда использовать Filament direct vs SceneView?
> Direct Filament — когда нужен полный control (custom pipeline, advanced materials, precise performance tuning). SceneView — когда нужны scene graph / ARCore / Kotlin idioms готовые. Overhead SceneView minimal.

> [!question]- Какой shading model используется в Filament PBR?
> Metallic-roughness (Disney-compatible). GGX NDF, Smith geometry, Schlick Fresnel. Split-sum IBL approximation (Karis 2013). Industry standard.

---

## Ключевые карточки

Что такое Filament Material Language?
?
Proprietary shader-like language для define material. Compiled через `matc` в binary `.filamat` — loaded runtime. Gives artist-friendly abstraction над underlying GLSL/SPIR-V.

---

Какие platforms Filament supports?
?
Android, iOS, macOS, Linux, Windows, WebGL, Fuchsia. C++ core с Java/Kotlin bindings для Android. Metal для Apple, Vulkan/GL ES для остальных.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Material system | [[filament-materials-and-pbr]] |
| Compose integration | [[filament-inside-compose]] |
| SceneView wrapper | [[sceneview-arcore-composable-3d]] |
| glTF | [[gltf-2-format-deep]] |

---

*Deep-dive модуля M8.*
